"""Test float32 MACE with surgical fixes for .double() and requires_grad."""
import os, sys, time, numpy as np, tempfile
os.environ['PYTHONNOUSERSITE'] = '1'
import torch

def log(msg):
    from datetime import datetime, timezone
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%SZ')}] {msg}", flush=True)

log(f"torch {torch.__version__} | GPU: {torch.cuda.get_device_name(0)}")

# Set default dtype FIRST
torch.set_default_dtype(torch.float32)

# Patch vesin
import numpy as _np
from vesin import NeighborList as _VesinNL
import mace.data.neighborhood as _mace_nh
_vc = _VesinNL(cutoff=1.0, full_list=True)
def _vnl(quantities, atoms=None, cutoff=None, positions=None, cell=None, pbc=None, **kw):
    positions = _np.asarray(positions, dtype=_np.float64)
    cell = _np.asarray(cell, dtype=_np.float64)
    periodic = bool(pbc is not None and any(pbc))
    _vc.cutoff = cutoff
    return _vc.compute(points=positions, box=cell, periodic=periodic, quantities=quantities, copy=True)
_mace_nh.neighbour_list = _vnl

# Patch the .double() call in MACE forward method
import mace.modules.models as _mm
_orig_forward = _mm.MACE.forward

def _patched_forward(self, data, training=False, compute_force=True, **kwargs):
    # Ensure positions have requires_grad
    if not torch.compiler.is_compiling():
        data["positions"].requires_grad_(True)
    return _orig_forward(self, data, training=training, compute_force=compute_force, **kwargs)

# Don't patch forward yet — first test: does the .double() line matter?

# Load model as float32
from mace.calculators.foundations_models import mace_off
model = mace_off(model='https://github.com/ACEsuit/mace-off/blob/main/mace_off24/MACE-OFF24_medium.model?raw=true',
                 device='cuda', return_raw_model=True).to('cuda').float()
for p in model.parameters():
    p.requires_grad = False
log(f"Model loaded, dtype={next(model.parameters()).dtype}")

# Build WW-like input
from mace.tools import utils, to_one_hot, atomic_numbers_to_indices
from mace.data.neighborhood import get_neighborhood
from openmm.app import PDBFile, Modeller, ForceField
from openmm import unit
from pdbfixer import PDBFixer

pdb = PDBFile("/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ww.pdb")
m = Modeller(pdb.topology, pdb.positions)
std = {'ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE','LEU','LYS','MET','PHE','PRO','SER','THR','TRP','TYR','VAL','HID','HIE','HIP','CYX','CYM','ASH','GLH','LYN'}
m.delete([r for r in m.topology.residues() if r.name not in std])
ch0 = list(m.topology.chains())[0].id
oth = []
for c in m.topology.chains():
    if c.id != ch0: oth.extend(c.residues())
if oth: m.delete(oth)
m.delete([r for r in m.topology.residues() if int(r.id)<6 or int(r.id)>39])
with tempfile.NamedTemporaryFile(suffix='.pdb', mode='w', delete=False) as f:
    PDBFile.writeFile(m.topology, m.positions, f); tmp=f.name
fx = PDBFixer(filename=tmp); fx.findMissingResidues(); fx.missingResidues={}
fx.findNonstandardResidues(); fx.replaceNonstandardResidues()
fx.findMissingAtoms(); fx.addMissingAtoms(); fx.addMissingHydrogens(pH=7.0)
m = Modeller(fx.topology, fx.positions); os.unlink(tmp)
ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
m.addSolvent(ff, padding=1.0*unit.nanometer, ionicStrength=0.15*unit.molar, model='tip3p')

pa = list(range(534))  # protein atoms
all_pos = np.array([[p.x, p.y, p.z] for p in m.positions]) * 10.0  # nm->A
prot_pos = all_pos[pa]
cell_v = m.topology.getPeriodicBoxVectors()
cell = np.array([[v.x, v.y, v.z] for v in cell_v]) * 10.0
cutoff = float(model.r_max.detach())

edges, shifts, _, _ = get_neighborhood(prot_pos, cutoff, [True,True,True], cell)
atomicNumbers = [a.element.atomic_number for a in list(m.topology.atoms())[:534]]
zTable = utils.AtomicNumberTable([int(z) for z in model.atomic_numbers])
na = to_one_hot(torch.tensor(atomic_numbers_to_indices(atomicNumbers, z_table=zTable),
                dtype=torch.long, device='cuda').unsqueeze(-1),
                num_classes=len(zTable)).to(torch.float32)

pos_t = torch.tensor(prot_pos, dtype=torch.float32, device='cuda', requires_grad=True)
log(f"Input: {pos_t.shape[0]} atoms, {edges.shape[1]} edges, requires_grad={pos_t.requires_grad}")

inp = {
    "ptr": torch.tensor([0, 534], dtype=torch.long, device='cuda'),
    "node_attrs": na, "batch": torch.zeros(534, dtype=torch.long, device='cuda'),
    "pbc": torch.tensor([True,True,True], dtype=torch.bool, device='cuda'),
    "positions": pos_t,
    "edge_index": torch.tensor(edges, dtype=torch.int64, device='cuda'),
    "shifts": torch.tensor(shifts, dtype=torch.float32, device='cuda'),
    "cell": torch.tensor(cell, dtype=torch.float32, device='cuda'),
    "total_charge": torch.tensor([0.0], dtype=torch.float32, device='cuda'),
    "total_spin": torch.tensor([1.0], dtype=torch.float32, device='cuda'),
}

# Test 1: Direct call with requires_grad=True
log("Test 1: Direct f32 call, 534 atoms, requires_grad=True")
try:
    res = model(inp, compute_force=True)
    e = float(res["interaction_energy"].detach())
    f = res["forces"].detach()
    log(f"  PASS: E={e:.4f} eV, max|F|={f.abs().max():.4f} eV/A")
except Exception as ex:
    log(f"  FAIL: {ex}")
    import traceback; traceback.print_exc()

# Test 2: Through OpenMM PythonForce
log("Test 2: Through OpenMM createMixedSystem with precision='single'")
try:
    import openmm
    from openmm import MonteCarloBarostat
    from openmm.app import Simulation, PME
    from openmmml import MLPotential

    mm_sys = ff.createSystem(m.topology, nonbondedMethod=PME,
                             nonbondedCutoff=1.0*unit.nanometer,
                             constraints=None, rigidWater=True)
    pot = MLPotential('mace-off24-medium')
    hy = pot.createMixedSystem(m.topology, mm_sys, pa, interpolate=False, precision='single')
    hy.addForce(MonteCarloBarostat(1.0*unit.atmosphere, 300.0*unit.kelvin, 25))
    plat = openmm.Platform.getPlatformByName('OpenCL')
    integ = openmm.LangevinMiddleIntegrator(300*unit.kelvin, 1.0/unit.picosecond, 1.0*unit.femtosecond)
    sim = Simulation(m.topology, hy, integ, plat, {})
    sim.context.setPositions(m.positions)
    sim.minimizeEnergy(maxIterations=50)
    st = sim.context.getState(getForces=True)
    mf = float(np.max(np.abs(st.getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer))))
    log(f"  Post-min max force: {mf:.2e}")
    sim.context.setVelocitiesToTemperature(300*unit.kelvin)
    t0 = time.time(); sim.step(50); el = time.time() - t0
    nsd = 50*1e-6/el*86400
    log(f"  PASS: {nsd:.2f} ns/day | {el/50*1000:.1f} ms/step")
except Exception as ex:
    log(f"  FAIL: {ex}")
    import traceback; traceback.print_exc()

torch.set_default_dtype(torch.float64)
log("=== DONE ===")
