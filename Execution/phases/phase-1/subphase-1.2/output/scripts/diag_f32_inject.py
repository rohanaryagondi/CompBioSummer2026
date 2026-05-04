"""Fix f32 by injecting a correctly-loaded model into OpenMM's PythonForce."""
import os, sys, time, numpy as np
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

import openmm, tempfile
from openmm import unit, MonteCarloBarostat
from openmm.app import PDBFile, Modeller, Simulation, ForceField, PME
from openmmml import MLPotential
from pdbfixer import PDBFixer
from mace.calculators.foundations_models import mace_off

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
pa = list(range(m.topology.getNumAtoms()))
ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
m.addSolvent(ff, padding=1.0*unit.nanometer, ionicStrength=0.15*unit.molar, model='tip3p')
log(f"System: {m.topology.getNumAtoms()} atoms")

# Create hybrid system with precision='single'
mm_sys = ff.createSystem(m.topology, nonbondedMethod=PME, nonbondedCutoff=1.0*unit.nanometer,
                         constraints=None, rigidWater=True)
pot = MLPotential('mace-off24-medium')
hy = pot.createMixedSystem(m.topology, mm_sys, pa, interpolate=False, precision='single')

# NOW: load a FRESH model the way that works (Test 1 approach)
log("Loading fresh f32 model (the working way)...")
good_model = mace_off(model='https://github.com/ACEsuit/mace-off/blob/main/mace_off24/MACE-OFF24_medium.model?raw=true',
                      device='cuda', return_raw_model=True).to('cuda').float()
for p in good_model.parameters():
    p.requires_grad = False
log(f"Good model dtype: {next(good_model.parameters()).dtype}")

# Inject into the PythonForce callback
replaced = False
for i in range(hy.getNumForces()):
    force = hy.getForce(i)
    if isinstance(force, openmm.PythonForce):
        cb = force.getComputeFunction()
        if hasattr(cb, 'keywords') and 'model' in cb.keywords:
            old_dtype = next(cb.keywords['model'].parameters()).dtype
            cb.keywords['model'] = good_model
            replaced = True
            log(f"Replaced model in PythonForce (was {old_dtype}, now float32)")
        break

if not replaced:
    log("WARNING: Could not find PythonForce model to replace")

hy.addForce(MonteCarloBarostat(1.0*unit.atmosphere, 300.0*unit.kelvin, 25))
plat = openmm.Platform.getPlatformByName('OpenCL')
integ = openmm.LangevinMiddleIntegrator(300*unit.kelvin, 1.0/unit.picosecond, 1.0*unit.femtosecond)
sim = Simulation(m.topology, hy, integ, plat, {})
sim.context.setPositions(m.positions)

log("Minimizing...")
try:
    sim.minimizeEnergy(maxIterations=100)
    st = sim.context.getState(getForces=True)
    mf = float(np.max(np.abs(st.getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer))))
    log(f"Post-min max force: {mf:.2e}")

    sim.context.setVelocitiesToTemperature(300*unit.kelvin)
    sim.step(20)  # warmup
    t0 = time.time(); sim.step(100); el = time.time() - t0
    nsd = 100*1e-6/el*86400
    log(f"F32 BENCHMARK: {nsd:.2f} ns/day | {el/100*1000:.1f} ms/step")

    # Compare: also run f64 baseline
    torch.set_default_dtype(torch.float64)
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
    log(f"F64 BASELINE: {nsd2:.2f} ns/day | {el/100*1000:.1f} ms/step")
    log(f"SPEEDUP: {nsd/nsd2:.2f}x")
except Exception as e:
    log(f"FAIL: {e}")
    import traceback; traceback.print_exc()

torch.set_default_dtype(torch.float64)
log("=== DONE ===")
