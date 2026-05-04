"""Bypass openmmml entirely for f32: load model ourselves, create PythonForce manually."""
import os, sys, time, numpy as np, tempfile
os.environ['PYTHONNOUSERSITE'] = '1'
import torch
torch.set_default_dtype(torch.float32)

def log(msg):
    from datetime import datetime, timezone
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%SZ')}] {msg}", flush=True)

log(f"torch {torch.__version__} | GPU: {torch.cuda.get_device_name(0)}")

# Vesin patch
import numpy as _np
from vesin import NeighborList as _VesinNL
import mace.data.neighborhood as _mace_nh
_vc = _VesinNL(cutoff=1.0, full_list=True)
def _vnl(quantities, atoms=None, cutoff=None, positions=None, cell=None, pbc=None, **kw):
    positions = _np.asarray(positions, dtype=_np.float64)
    cell = _np.asarray(cell, dtype=_np.float64)
    _vc.cutoff = cutoff
    return _vc.compute(points=positions, box=cell, periodic=bool(pbc is not None and any(pbc)), quantities=quantities, copy=True)
_mace_nh.neighbour_list = _vnl

import openmm
from openmm import unit, MonteCarloBarostat
from openmm.app import PDBFile, Modeller, Simulation, ForceField, PME
from openmmml import MLPotential
from pdbfixer import PDBFixer
from mace.calculators.foundations_models import mace_off
from mace.tools import utils, to_one_hot, atomic_numbers_to_indices
from mace.data.neighborhood import get_neighborhood
from functools import partial

# Build system
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

protein_atoms = list(range(m.topology.getNumAtoms()))
n_prot = len(protein_atoms)
ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
m.addSolvent(ff, padding=1.0*unit.nanometer, ionicStrength=0.15*unit.molar, model='tip3p')
log(f"System: {m.topology.getNumAtoms()} atoms, protein={n_prot}")

# Load model OUR WAY (the way that works in direct calls)
log("Loading f32 model...")
model = mace_off(model='https://github.com/ACEsuit/mace-off/blob/main/mace_off24/MACE-OFF24_medium.model?raw=true',
                 device='cuda', return_raw_model=True).to('cuda').float()
for p in model.parameters():
    p.requires_grad = False
dtype = torch.float32
device = torch.device('cuda')
cutoff = float(model.r_max.detach())

# Setup atom encoding
includedAtoms = [list(m.topology.atoms())[i] for i in protein_atoms]
atomicNumbers = [atom.element.atomic_number for atom in includedAtoms]
zTable = utils.AtomicNumberTable([int(z) for z in model.atomic_numbers])
nodeAttrs = to_one_hot(
    torch.tensor(atomic_numbers_to_indices(atomicNumbers, z_table=zTable),
                 dtype=torch.long, device=device).unsqueeze(-1),
    num_classes=len(zTable)).to(dtype)
indices = np.array(protein_atoms)
periodic = True

# Our f32 PythonForce callback
def compute_f32(state, model, ptr, node_attrs, batch, pbc, indices, periodic):
    torch.set_default_dtype(torch.float32)
    energyScale = 96.4853
    lengthScale = 10.0
    positions = state.getPositions(asNumpy=True).value_in_unit(unit.angstrom)
    numAtoms = positions.shape[0]
    positions = positions[indices]
    if periodic:
        cell = state.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.angstrom)
    else:
        cell = np.identity(3, dtype=np.float64)
    edgeIndex, shifts, _, _ = get_neighborhood(positions, cutoff, [periodic]*3, cell)
    inputDict = {
        "ptr": ptr,
        "node_attrs": node_attrs,
        "batch": batch,
        "pbc": pbc,
        "positions": torch.tensor(positions, dtype=dtype, device=device),
        "edge_index": torch.tensor(edgeIndex, dtype=torch.int64, device=device),
        "shifts": torch.tensor(shifts, dtype=dtype, device=device),
        "cell": torch.tensor(cell, dtype=dtype, device=device),
        "total_charge": torch.tensor([0.0], dtype=dtype, device=device),
        "total_spin": torch.tensor([1.0], dtype=dtype, device=device),
    }
    results = model(inputDict, compute_force=True)
    energy = float(results["interaction_energy"].detach()) * energyScale
    forces = (results["forces"] * energyScale * lengthScale).detach().cpu().numpy()
    f = np.zeros((numAtoms, 3), dtype=np.float32)
    f[indices] = forces
    return energy, f

# Create hybrid system using openmmml for classical forces (f64 is fine for classical)
torch.set_default_dtype(torch.float64)  # reset for openmmml system creation
mm_system = ff.createSystem(m.topology, nonbondedMethod=PME,
                            nonbondedCutoff=1.0*unit.nanometer,
                            constraints=None, rigidWater=True)
pot = MLPotential('mace-off24-medium')
hybrid_system = pot.createMixedSystem(m.topology, mm_system, protein_atoms, interpolate=False)

# Find and REPLACE the MACE PythonForce with our f32 version
for i in range(hybrid_system.getNumForces()):
    force = hybrid_system.getForce(i)
    if isinstance(force, openmm.PythonForce):
        fg = force.getForceGroup()
        pbc_flag = force.usesPeriodicBoundaryConditions()
        hybrid_system.removeForce(i)
        log(f"Removed openmmml PythonForce (group={fg})")
        break

# Add our f32 PythonForce
compute = partial(compute_f32,
                  model=model,
                  ptr=torch.tensor([0, n_prot], dtype=torch.long, device=device),
                  node_attrs=nodeAttrs,
                  batch=torch.zeros(n_prot, dtype=torch.long, device=device),
                  pbc=torch.tensor([periodic]*3, dtype=torch.bool, device=device),
                  indices=indices,
                  periodic=periodic)
new_force = openmm.PythonForce(compute)
new_force.setForceGroup(fg)
new_force.setUsesPeriodicBoundaryConditions(pbc_flag)
hybrid_system.addForce(new_force)
log("Added f32 PythonForce with our model")

hybrid_system.addForce(MonteCarloBarostat(1.0*unit.atmosphere, 300.0*unit.kelvin, 25))
plat = openmm.Platform.getPlatformByName('OpenCL')
integ = openmm.LangevinMiddleIntegrator(300*unit.kelvin, 1.0/unit.picosecond, 1.0*unit.femtosecond)
sim = Simulation(m.topology, hybrid_system, integ, plat, {})
sim.context.setPositions(m.positions)

log("Minimizing (f32)...")
try:
    sim.minimizeEnergy(maxIterations=100)
    st = sim.context.getState(getForces=True)
    mf = float(np.max(np.abs(st.getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer))))
    log(f"Post-min force: {mf:.2e}")
    sim.context.setVelocitiesToTemperature(300*unit.kelvin)
    sim.step(20)
    t0 = time.time(); sim.step(100); el = time.time() - t0
    nsd = 100*1e-6/el*86400
    log(f"F32 BYPASS: {nsd:.2f} ns/day | {el/100*1000:.1f} ms/step")
except Exception as e:
    log(f"F32 BYPASS FAIL: {e}")
    import traceback; traceback.print_exc()

# F64 baseline for comparison
log("F64 baseline...")
torch.set_default_dtype(torch.float64)
mm_sys2 = ff.createSystem(m.topology, nonbondedMethod=PME, nonbondedCutoff=1.0*unit.nanometer,
                          constraints=None, rigidWater=True)
hy2 = pot.createMixedSystem(m.topology, mm_sys2, protein_atoms, interpolate=False)
hy2.addForce(MonteCarloBarostat(1.0*unit.atmosphere, 300.0*unit.kelvin, 25))
integ2 = openmm.LangevinMiddleIntegrator(300*unit.kelvin, 1.0/unit.picosecond, 1.0*unit.femtosecond)
sim2 = Simulation(m.topology, hy2, integ2, plat, {})
sim2.context.setPositions(m.positions)
sim2.minimizeEnergy(maxIterations=100)
sim2.context.setVelocitiesToTemperature(300*unit.kelvin)
sim2.step(20)
t0 = time.time(); sim2.step(100); el = time.time() - t0
nsd2 = 100*1e-6/el*86400
log(f"F64: {nsd2:.2f} ns/day | {el/100*1000:.1f} ms/step")
if 'nsd' in dir():
    log(f"SPEEDUP: {nsd/nsd2:.2f}x")

log("=== DONE ===")
