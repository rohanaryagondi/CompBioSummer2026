#!/bin/bash
# All-in-one: upgrade torch 2.10 + install oeq + OpenMM CUDA 12 + benchmark
# Runs on compute node (needs GPU + memory + nvcc)
# Reverts torch if anything breaks
set -euo pipefail

echo "=== UPGRADE + BENCHMARK $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
echo "Node: $(hostname) | GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader)"

source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-mace
export PYTHONNOUSERSITE=1

# Load CUDA toolkit for oeq build
module load CUDA/12.8.0 2>/dev/null || true

# Record current state for revert
echo "--- Current state ---"
python -c "import torch; print(f'torch: {torch.__version__}')"
python -c "import openmm; print(f'openmm: {openmm.__version__}')"
python -c "import mace; print(f'mace: ok')"
python -c "import e3nn; print(f'e3nn: ok')"

# Step 1: Upgrade torch to 2.10
echo ""
echo "--- Step 1: Upgrade torch to 2.10.0 ---"
pip install 'torch==2.10.0' 2>&1 | tail -5
python -c "import torch; print(f'torch now: {torch.__version__}')"

# Verify MACE + e3nn still import
echo "--- Verify imports ---"
python -c "
import torch; print(f'torch {torch.__version__}')
import e3nn; print('e3nn: OK')
from mace.calculators.foundations_models import mace_off; print('mace: OK')
import openmm; print(f'openmm {openmm.__version__}')
from openmmml import MLPotential; print('openmmml: OK')
print('ALL IMPORTS OK')
" 2>&1 || { echo "IMPORT FAILED — reverting torch"; pip install 'torch==2.5.1+cu121' -f https://download.pytorch.org/whl/cu121; exit 1; }

# Step 2: Install openequivariance (builds CUDA kernels)
echo ""
echo "--- Step 2: Install openequivariance ---"
pip install openequivariance==0.6.6 2>&1 | tail -5
python -c "import openequivariance as oeq; print(f'oeq: {oeq.__version__}')" 2>&1 || echo "oeq import failed (non-fatal)"

# Step 3: Install cuequivariance-ops (now unblocked with cublas 12.8)
echo ""
echo "--- Step 3: Install cuequivariance-ops ---"
pip install cuequivariance-ops-torch-cu12 2>&1 | tail -5
python -c "import cuequivariance_ops_torch; print('cueq-ops: OK')" 2>&1 || echo "cueq-ops import failed (non-fatal)"

# Step 4: Try OpenMM CUDA 12 build
echo ""
echo "--- Step 4: OpenMM CUDA platform check ---"
python -c "
import openmm
try:
    p = openmm.Platform.getPlatformByName('CUDA')
    print(f'CUDA platform: OK (speed={p.getSpeed()})')
except Exception as e:
    print(f'CUDA platform: FAIL ({e})')
    print('Attempting OpenMM CUDA 12 swap via conda...')
" 2>&1

# Try conda install if CUDA failed (may OOM but worth trying with 32G)
python -c "import openmm; openmm.Platform.getPlatformByName('CUDA')" 2>/dev/null || {
    echo "Trying conda swap..."
    conda install -c conda-forge -y 'openmm=8.5.1=py310hc82e367_0' 2>&1 | tail -10 || echo "conda swap failed (non-fatal)"
}

# Step 5: Benchmark
echo ""
echo "--- Step 5: Benchmark ---"
/home/rag88/.conda/envs/env-mace/bin/python -c "
import os, sys, time, numpy as np, tempfile
os.environ['PYTHONNOUSERSITE'] = '1'
import torch

def log(msg):
    from datetime import datetime, timezone
    print(f'[{datetime.now(timezone.utc).isoformat()[:19]}Z] {msg}', flush=True)

log(f'torch {torch.__version__} | GPU: {torch.cuda.get_device_name(0)}')

# Check what accelerators are available
oeq_ok = False
try:
    import openequivariance; oeq_ok = True; log('openequivariance: available')
except: log('openequivariance: NOT available')

cueq_ops_ok = False
try:
    import cuequivariance_ops_torch; cueq_ops_ok = True; log('cuequivariance-ops: available')
except: log('cuequivariance-ops: NOT available')

import openmm
cuda_ok = False
try:
    openmm.Platform.getPlatformByName('CUDA'); cuda_ok = True; log('OpenMM CUDA: available')
except: log('OpenMM CUDA: NOT available')

# Build WW system
from openmm import unit, MonteCarloBarostat
from openmm.app import PDBFile, Modeller, Simulation, ForceField, PME
from openmmml import MLPotential
from pdbfixer import PDBFixer

pdb = PDBFile('/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ww.pdb')
m = Modeller(pdb.topology, pdb.positions)
std = {'ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE','LEU','LYS','MET','PHE','PRO','SER','THR','TRP','TYR','VAL','HID','HIE','HIP','CYX','CYM','ASH','GLH','LYN'}
m.delete([r for r in m.topology.residues() if r.name not in std])
ch0 = list(m.topology.chains())[0].id
oth = []
for c in m.topology.chains():
    if c.id != ch0: oth.extend(c.residues())
if oth: m.delete(oth)
m.delete([r for r in m.topology.residues() if int(r.id)<6 or int(r.id)>39])
with tempfile.NamedTemporaryFile(suffix='.pdb',mode='w',delete=False) as f:
    PDBFile.writeFile(m.topology,m.positions,f); tmp=f.name
fx = PDBFixer(filename=tmp); fx.findMissingResidues(); fx.missingResidues={}
fx.findNonstandardResidues(); fx.replaceNonstandardResidues()
fx.findMissingAtoms(); fx.addMissingAtoms(); fx.addMissingHydrogens(pH=7.0)
m = Modeller(fx.topology,fx.positions); os.unlink(tmp)
pa = list(range(m.topology.getNumAtoms()))
ff = ForceField('amber14-all.xml','amber14/tip3pfb.xml')
m.addSolvent(ff,padding=1.0*unit.nanometer,ionicStrength=0.15*unit.molar,model='tip3p')
log(f'System: {m.topology.getNumAtoms()} atoms')

configs = [('A: f64/OpenCL (baseline)', {}, 'OpenCL', {})]

# Float32 with e3nn patch
import e3nn.o3._wigner as _w
_w._Jd = [j.to(torch.float32) for j in _w._Jd]
_w._W3j_flat = _w._W3j_flat.to(torch.float32)
configs.append(('B: f32/OpenCL (e3nn patched)', {'precision':'single'}, 'OpenCL', {}))

if cuda_ok:
    configs.append(('C: f64/CUDA', {}, 'CUDA', {}))
    configs.append(('D: f32/CUDA', {'precision':'single'}, 'CUDA', {}))
    configs.append(('E: f32/CUDA/mixed', {'precision':'single'}, 'CUDA', {'Precision':'mixed'}))

# OEQ variants
if oeq_ok:
    configs.append(('F: f64/OpenCL/oeq', {'enable_oeq': True}, 'OpenCL', {}))

for label, prec_kw, plat_name, plat_props in configs:
    try:
        mm_sys = ff.createSystem(m.topology,nonbondedMethod=PME,nonbondedCutoff=1.0*unit.nanometer,constraints=None,rigidWater=True)
        pot = MLPotential('mace-off24-medium')

        # Handle oeq: need to load model separately and convert
        extra_kw = {k:v for k,v in prec_kw.items() if k != 'enable_oeq'}
        hy = pot.createMixedSystem(m.topology,mm_sys,pa,interpolate=False,**extra_kw)

        if prec_kw.get('enable_oeq') and oeq_ok:
            from mace.calculators.foundations_models import mace_off
            from mace.cli.convert_e3nn_oeq import run as run_e3nn_to_oeq
            raw = mace_off(model='https://github.com/ACEsuit/mace-off/blob/main/mace_off24/MACE-OFF24_medium.model?raw=true',device='cuda',return_raw_model=True).to('cuda')
            oeq_m = run_e3nn_to_oeq(raw, device='cuda').to('cuda')
            for p in oeq_m.parameters(): p.requires_grad = False
            for i in range(hy.getNumForces()):
                force = hy.getForce(i)
                if isinstance(force, openmm.PythonForce):
                    cb = force.getComputeFunction()
                    if hasattr(cb,'keywords') and 'model' in cb.keywords:
                        cb.keywords['model'] = oeq_m
                    break

        hy.addForce(MonteCarloBarostat(1.0*unit.atmosphere,300.0*unit.kelvin,25))
        plat = openmm.Platform.getPlatformByName(plat_name)
        integ = openmm.LangevinMiddleIntegrator(300*unit.kelvin,1.0/unit.picosecond,1.0*unit.femtosecond)
        sim = Simulation(m.topology,hy,integ,plat,plat_props)
        sim.context.setPositions(m.positions)
        sim.minimizeEnergy(maxIterations=200)
        state = sim.context.getState(getForces=True)
        max_f = float(np.max(np.abs(state.getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer))))
        if max_f > 1e5:
            log(f'  {label}: FAIL post-min force {max_f:.2e}'); continue
        sim.context.setVelocitiesToTemperature(300*unit.kelvin)
        sim.step(20)
        t0=time.time(); sim.step(50); el=time.time()-t0
        st=sim.context.getState(getPositions=True,getEnergy=True)
        pe=st.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
        pos=st.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        ok=not(np.any(np.isnan(pos)) or np.isnan(pe))
        nsd=50*1e-6/el*86400
        log(f'  {label}: {nsd:.2f} ns/day | {el/50*1000:.1f} ms/step | stable={ok}')
    except Exception as e:
        log(f'  {label}: ERROR — {e}')

log('=== BENCHMARK DONE ===')
"

echo "=== ALL DONE ==="
