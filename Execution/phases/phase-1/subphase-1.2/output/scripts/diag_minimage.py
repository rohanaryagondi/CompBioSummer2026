"""
Minimal diagnostic: verify minimum-image GPU NL produces correct forces
on real WW system, then benchmark 50 steps for throughput.
Tests both OpenCL and CUDA platforms (if available after OpenMM upgrade).
"""
import os, sys, time, numpy as np, tempfile
os.environ['PYTHONNOUSERSITE'] = '1'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import torch

def log(msg):
    from datetime import datetime, timezone
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%SZ')}] {msg}", flush=True)

log(f"GPU: {torch.cuda.get_device_name(0)}")

# Step 1: Force comparison (GPU NL vs matscipy on same positions)
log("--- Step 1: Force comparison ---")
from mace.calculators.foundations_models import mace_off
from mace.data.neighborhood import get_neighborhood
from mace.tools import utils, to_one_hot, atomic_numbers_to_indices
from openmm.app import PDBFile, Modeller, ForceField
from openmm import unit
from pdbfixer import PDBFixer

device = torch.device('cuda:0')
model = mace_off(model='https://github.com/ACEsuit/mace-off/blob/main/mace_off24/MACE-OFF24_medium.model?raw=true',
                 device=str(device), return_raw_model=True).to(device)
for p in model.parameters():
    p.requires_grad = False
cutoff = float(model.r_max.detach())

# Build WW system
pdb = PDBFile("/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ww.pdb")
m = Modeller(pdb.topology, pdb.positions)
std = {'ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE','LEU','LYS',
       'MET','PHE','PRO','SER','THR','TRP','TYR','VAL','HID','HIE','HIP','CYX',
       'CYM','ASH','GLH','LYN'}
m.delete([r for r in m.topology.residues() if r.name not in std])
ch0 = list(m.topology.chains())[0].id
oth = []
for c in m.topology.chains():
    if c.id != ch0:
        oth.extend(c.residues())
if oth:
    m.delete(oth)
m.delete([r for r in m.topology.residues() if int(r.id) < 6 or int(r.id) > 39])
with tempfile.NamedTemporaryFile(suffix='.pdb', mode='w', delete=False) as f:
    PDBFile.writeFile(m.topology, m.positions, f)
    tmp = f.name
fx = PDBFixer(filename=tmp)
fx.findMissingResidues(); fx.missingResidues = {}
fx.findNonstandardResidues(); fx.replaceNonstandardResidues()
fx.findMissingAtoms(); fx.addMissingAtoms(); fx.addMissingHydrogens(pH=7.0)
m = Modeller(fx.topology, fx.positions)
os.unlink(tmp)
pa = list(range(m.topology.getNumAtoms()))
n_prot = len(pa)
ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
m.addSolvent(ff, padding=1.0*unit.nanometer, ionicStrength=0.15*unit.molar, model='tip3p')
total = m.topology.getNumAtoms()
log(f"System: {total} atoms (protein={n_prot})")

# Get positions
all_pos = np.array([[p.x, p.y, p.z] for p in m.positions]) * 10.0
prot_pos = all_pos[pa]
cell_v = m.topology.getPeriodicBoxVectors()
cell = np.array([[v.x, v.y, v.z] for v in cell_v]) * 10.0
box_L = np.diag(cell)
dtype = torch.float64

log(f"Protein x=[{prot_pos[:,0].min():.1f},{prot_pos[:,0].max():.1f}] box={box_L[0]:.1f}")

# Matscipy reference
ref_edges, ref_shifts, _, _ = get_neighborhood(prot_pos, cutoff, [True,True,True], cell)
atomicNumbers = [a.element.atomic_number for a in list(m.topology.atoms())[:n_prot]]
zTable = utils.AtomicNumberTable([int(z) for z in model.atomic_numbers])
nodeAttrs = to_one_hot(
    torch.tensor(atomic_numbers_to_indices(atomicNumbers, z_table=zTable),
                 dtype=torch.long, device=device).unsqueeze(-1),
    num_classes=len(zTable)).to(dtype)

pos_t = torch.tensor(prot_pos, dtype=dtype, device=device)
inp_ref = {
    "ptr": torch.tensor([0, n_prot], dtype=torch.long, device=device),
    "node_attrs": nodeAttrs,
    "batch": torch.zeros(n_prot, dtype=torch.long, device=device),
    "pbc": torch.tensor([True,True,True], dtype=torch.bool, device=device),
    "positions": pos_t.clone(),
    "edge_index": torch.tensor(ref_edges, dtype=torch.int64, device=device),
    "shifts": torch.tensor(ref_shifts, dtype=dtype, device=device),
    "cell": torch.tensor(cell, dtype=dtype, device=device),
    "total_charge": torch.tensor([0.0], dtype=dtype, device=device),
    "total_spin": torch.tensor([1.0], dtype=dtype, device=device),
}
r_ref = model(inp_ref, compute_force=True)
e_ref = float(r_ref["interaction_energy"].detach())
f_ref = r_ref["forces"].detach().cpu().numpy()

# GPU minimum-image NL
box_t = torch.tensor(box_L, dtype=dtype, device=device)
pos_wrapped = pos_t - torch.floor(pos_t / box_t) * box_t
diff = pos_wrapped.unsqueeze(0) - pos_wrapped.unsqueeze(1)
diff = diff - torch.round(diff / box_t) * box_t
dists = torch.linalg.norm(diff, dim=-1)
mask = (dists < cutoff) & (dists > 1e-8)
s, r = torch.where(mask)
raw_diff = pos_wrapped[r] - pos_wrapped[s]
shifts_gpu = diff[s, r] - raw_diff

inp_gpu = {
    "ptr": torch.tensor([0, n_prot], dtype=torch.long, device=device),
    "node_attrs": nodeAttrs,
    "batch": torch.zeros(n_prot, dtype=torch.long, device=device),
    "pbc": torch.tensor([True,True,True], dtype=torch.bool, device=device),
    "positions": pos_wrapped.clone(),
    "edge_index": torch.stack([s, r]),
    "shifts": shifts_gpu,
    "cell": torch.tensor(cell, dtype=dtype, device=device),
    "total_charge": torch.tensor([0.0], dtype=dtype, device=device),
    "total_spin": torch.tensor([1.0], dtype=dtype, device=device),
}
r_gpu = model(inp_gpu, compute_force=True)
e_gpu = float(r_gpu["interaction_energy"].detach())
f_gpu = r_gpu["forces"].detach().cpu().numpy()

e_diff = abs(e_gpu - e_ref)
f_diff = np.max(np.abs(f_gpu - f_ref))
log(f"Energy: ref={e_ref:.6f} gpu={e_gpu:.6f} diff={e_diff:.2e} eV")
log(f"Force max diff: {f_diff:.2e} eV/A")
log(f"Edges: ref={ref_edges.shape[1]} gpu={s.shape[0]}")

if np.isnan(e_gpu) or np.isnan(f_diff):
    log("FAIL: NaN in GPU NL forces")
    sys.exit(1)
if f_diff > 0.01:
    log(f"FAIL: Force diff {f_diff:.2e} exceeds 0.01 tolerance")
    sys.exit(1)
log("PASS: GPU minimum-image NL forces match matscipy")

# Step 2: Full hybrid benchmark (50 steps)
log("--- Step 2: Throughput benchmark ---")
import openmm
from openmm import MonteCarloBarostat
from openmm.app import Simulation, PME
from openmmml import MLPotential

import mace_cuda_patch
mace_cuda_patch.apply()

mm_sys = ff.createSystem(m.topology, nonbondedMethod=PME,
                         nonbondedCutoff=1.0*unit.nanometer,
                         constraints=None, rigidWater=True)
pot = MLPotential('mace-off24-medium')
hy = pot.createMixedSystem(m.topology, mm_sys, pa, interpolate=False)
hy.addForce(MonteCarloBarostat(1.0*unit.atmosphere, 300.0*unit.kelvin, 25))

# Test available platforms
for pname in ['CUDA', 'OpenCL']:
    try:
        plat = openmm.Platform.getPlatformByName(pname)
        props = {'Precision': 'mixed'} if pname == 'CUDA' else {}
        integ = openmm.LangevinMiddleIntegrator(300*unit.kelvin, 1.0/unit.picosecond,
                                                 1.0*unit.femtosecond)
        sim = Simulation(m.topology, hy, integ, plat, props)
        sim.context.setPositions(m.positions)
        sim.minimizeEnergy(maxIterations=100)
        state = sim.context.getState(getForces=True)
        max_f = float(np.max(np.abs(
            state.getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer))))
        if max_f > 1e5:
            log(f"  {pname}: FAIL post-min force {max_f:.2e}")
            continue
        sim.context.setVelocitiesToTemperature(300*unit.kelvin)
        sim.step(20)  # warmup
        t0 = time.time()
        sim.step(50)
        el = time.time() - t0
        nsd = 50*1e-6/el*86400
        log(f"  {pname}: {nsd:.2f} ns/day | {el/50*1000:.1f} ms/step | post-min F={max_f:.0e}")
    except Exception as e:
        log(f"  {pname}: ERROR — {e}")

log("=== DONE ===")
