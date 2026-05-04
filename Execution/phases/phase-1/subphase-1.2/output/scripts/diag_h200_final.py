"""Final H200 verification: float32 + vesin + CUDA platform. Minimal steps."""
import os, sys, time, numpy as np, tempfile
os.environ['PYTHONNOUSERSITE'] = '1'

import torch

def log(msg):
    from datetime import datetime, timezone
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%SZ')}] {msg}", flush=True)

log(f"torch {torch.__version__} | GPU: {torch.cuda.get_device_name(0)} | sm_{torch.cuda.get_device_capability()[0]}{torch.cuda.get_device_capability()[1]}")

# Vesin patch
import numpy as _np
from vesin import NeighborList as _VesinNL
import mace.data.neighborhood as _mace_nh
_vesin_calc = _VesinNL(cutoff=1.0, full_list=True)
def _vesin_nl(quantities, atoms=None, cutoff=None, positions=None, cell=None, pbc=None, **kw):
    positions = _np.asarray(positions, dtype=_np.float64)
    cell = _np.asarray(cell, dtype=_np.float64)
    periodic = bool(pbc is not None and any(pbc))
    _vesin_calc.cutoff = cutoff
    return _vesin_calc.compute(points=positions, box=cell, periodic=periodic, quantities=quantities, copy=True)
_mace_nh.neighbour_list = _vesin_nl
log("vesin NL: patched")

# CUDA platform check
import openmm
from openmm import unit, MonteCarloBarostat
from openmm.app import PDBFile, Modeller, Simulation, ForceField, PME
from openmmml import MLPotential
from pdbfixer import PDBFixer

cuda_ok = False
try:
    sys_t = openmm.System(); sys_t.addParticle(1.0)
    ctx = openmm.Context(sys_t, openmm.VerletIntegrator(0.001), openmm.Platform.getPlatformByName('CUDA'))
    cuda_ok = True; del ctx
    log("CUDA platform: OK")
except Exception as e:
    log(f"CUDA platform: {e}")

# Build WW
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

# Benchmark configs
configs = []

# A: f64/OpenCL (baseline with vesin)
configs.append(('A:f64/OpenCL/vesin', {}, 'OpenCL', {}))

# B: f32/OpenCL (the key test)
configs.append(('B:f32/OpenCL/vesin', {'precision': 'single'}, 'OpenCL', {}))

# C: CUDA if available
if cuda_ok:
    configs.append(('C:f64/CUDA/vesin', {}, 'CUDA', {}))
    configs.append(('D:f32/CUDA/vesin', {'precision': 'single'}, 'CUDA', {}))

for label, prec_kw, pname, pprops in configs:
    try:
        if prec_kw.get('precision') == 'single':
            torch.set_default_dtype(torch.float32)
        else:
            torch.set_default_dtype(torch.float64)
        mm_sys = ff.createSystem(m.topology, nonbondedMethod=PME,
                                 nonbondedCutoff=1.0*unit.nanometer,
                                 constraints=None, rigidWater=True)
        pot = MLPotential('mace-off24-medium')
        hy = pot.createMixedSystem(m.topology, mm_sys, pa, interpolate=False, **prec_kw)
        hy.addForce(MonteCarloBarostat(1.0*unit.atmosphere, 300.0*unit.kelvin, 25))
        plat = openmm.Platform.getPlatformByName(pname)
        integ = openmm.LangevinMiddleIntegrator(300*unit.kelvin, 1.0/unit.picosecond, 1.0*unit.femtosecond)
        sim = Simulation(m.topology, hy, integ, plat, pprops)
        sim.context.setPositions(m.positions)
        sim.minimizeEnergy(maxIterations=100)
        st = sim.context.getState(getForces=True)
        mf = float(np.max(np.abs(st.getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer))))
        if mf > 1e5:
            log(f"  {label}: FAIL force {mf:.0e}"); continue
        sim.context.setVelocitiesToTemperature(300*unit.kelvin)
        sim.step(20)
        t0 = time.time(); sim.step(100); el = time.time() - t0
        nsd = 100*1e-6/el*86400
        log(f"  {label}: {nsd:.2f} ns/day | {el/100*1000:.1f} ms/step")
    except Exception as e:
        log(f"  {label}: ERROR — {e}")

torch.set_default_dtype(torch.float64)
log("=== DONE ===")
