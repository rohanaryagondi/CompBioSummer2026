"""Fix f32: monkey-patch _computeMACE to explicitly handle float32."""
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

# Monkey-patch: replace _computeMACE with a f32-safe version
import openmmml.models.macepotential as _mp
from openmm import unit as _unit

_orig_computeMACE = _mp._computeMACE

def _f32_computeMACE(state, model, ptr, node_attrs, batch, pbc, returnEnergyType, charge, multiplicity, indices, periodic):
    """Float32-safe version: forces default dtype to match model during each call."""
    model_dtype = next(model.parameters()).dtype
    old_default = torch.get_default_dtype()
    torch.set_default_dtype(model_dtype)
    try:
        result = _orig_computeMACE(state, model, ptr, node_attrs, batch, pbc, returnEnergyType, charge, multiplicity, indices, periodic)
    finally:
        torch.set_default_dtype(old_default)
    return result

_mp._computeMACE = _f32_computeMACE
log("Patched _computeMACE for f32 safety")

# Build + benchmark
import openmm
from openmm import unit, MonteCarloBarostat
from openmm.app import PDBFile, Modeller, Simulation, ForceField, PME
from openmmml import MLPotential
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
pa = list(range(m.topology.getNumAtoms()))
ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
m.addSolvent(ff, padding=1.0*unit.nanometer, ionicStrength=0.15*unit.molar, model='tip3p')
log(f"System: {m.topology.getNumAtoms()} atoms")

# F32 benchmark
log("--- F32 with monkey-patched _computeMACE ---")
try:
    mm_sys = ff.createSystem(m.topology, nonbondedMethod=PME, nonbondedCutoff=1.0*unit.nanometer,
                             constraints=None, rigidWater=True)
    pot = MLPotential('mace-off24-medium')
    hy = pot.createMixedSystem(m.topology, mm_sys, pa, interpolate=False, precision='single')
    hy.addForce(MonteCarloBarostat(1.0*unit.atmosphere, 300.0*unit.kelvin, 25))
    plat = openmm.Platform.getPlatformByName('OpenCL')
    integ = openmm.LangevinMiddleIntegrator(300*unit.kelvin, 1.0/unit.picosecond, 1.0*unit.femtosecond)
    sim = Simulation(m.topology, hy, integ, plat, {})
    sim.context.setPositions(m.positions)
    sim.minimizeEnergy(maxIterations=100)
    st = sim.context.getState(getForces=True)
    mf = float(np.max(np.abs(st.getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer))))
    log(f"  Post-min max force: {mf:.2e}")
    sim.context.setVelocitiesToTemperature(300*unit.kelvin)
    sim.step(20)
    t0 = time.time(); sim.step(100); el = time.time() - t0
    nsd = 100*1e-6/el*86400
    log(f"  F32: {nsd:.2f} ns/day | {el/100*1000:.1f} ms/step")
except Exception as e:
    log(f"  F32 FAIL: {e}")
    import traceback; traceback.print_exc()

# F64 baseline
log("--- F64 baseline ---")
torch.set_default_dtype(torch.float64)
try:
    mm_sys2 = ff.createSystem(m.topology, nonbondedMethod=PME, nonbondedCutoff=1.0*unit.nanometer,
                              constraints=None, rigidWater=True)
    pot2 = MLPotential('mace-off24-medium')
    hy2 = pot2.createMixedSystem(m.topology, mm_sys2, pa, interpolate=False)
    hy2.addForce(MonteCarloBarostat(1.0*unit.atmosphere, 300.0*unit.kelvin, 25))
    integ2 = openmm.LangevinMiddleIntegrator(300*unit.kelvin, 1.0/unit.picosecond, 1.0*unit.femtosecond)
    sim2 = Simulation(m.topology, hy2, integ2, plat, {})
    sim2.context.setPositions(m.positions)
    sim2.minimizeEnergy(maxIterations=100)
    sim2.context.setVelocitiesToTemperature(300*unit.kelvin)
    sim2.step(20)
    t0 = time.time(); sim2.step(100); el = time.time() - t0
    nsd2 = 100*1e-6/el*86400
    log(f"  F64: {nsd2:.2f} ns/day | {el/100*1000:.1f} ms/step")
    if 'nsd' in dir():
        log(f"  SPEEDUP: {nsd/nsd2:.2f}x")
except Exception as e:
    log(f"  F64 FAIL: {e}")

log("=== DONE ===")
