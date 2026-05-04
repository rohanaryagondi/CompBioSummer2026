#!/bin/bash
# Upgrade torch 2.5.1 → 2.10.0, install openequivariance, benchmark
# torch.load patches already applied on login node
# If anything fails: backups at *.orig files
set -euo pipefail

echo "=== TORCH 2.10 UPGRADE + OEQ $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
echo "Node: $(hostname) | GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo none)"

source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-mace
export PYTHONNOUSERSITE=1

echo "--- Pre-upgrade state ---"
python -c "import torch; print(f'torch: {torch.__version__}')"
python -c "import e3nn; print('e3nn: OK')"
python -c "from mace.calculators.foundations_models import mace_off; print('mace: OK')"

echo ""
echo "--- Step 1: Upgrade torch to 2.10.0 ---"
pip install 'torch==2.10.0' 2>&1 | tail -5
python -c "import torch; print(f'torch: {torch.__version__}')"

echo ""
echo "--- Step 2: Verify imports ---"
python -c "
import torch; print(f'torch {torch.__version__}')
import e3nn; print('e3nn: OK')
from mace.calculators.foundations_models import mace_off; print('mace: OK')
from openmmml import MLPotential; print('openmmml: OK')
import openmm; print(f'openmm {openmm.__version__}')
print('ALL IMPORTS OK')
" 2>&1 || { echo "IMPORTS FAILED — reverting torch"; pip install 'torch==2.5.1+cu121' -f https://download.pytorch.org/whl/cu121 2>&1 | tail -3; exit 1; }

echo ""
echo "--- Step 3: Install openequivariance ---"
module load CUDA/12.8.0 2>/dev/null || true
pip install openequivariance==0.6.6 2>&1 | tail -5
python -c "import openequivariance as oeq; print(f'oeq {oeq.__version__}: OK')" 2>&1 || echo "oeq import failed (non-fatal)"

echo ""
echo "--- Step 4: Check CUDA platform ---"
python -c "
import openmm
try:
    p = openmm.Platform.getPlatformByName('CUDA')
    print(f'CUDA platform: OK (speed={p.getSpeed()})')
except Exception as e:
    print(f'CUDA platform: {e}')
"

echo ""
echo "--- Step 5: Quick benchmark (if GPU available) ---"
python -c "
import torch
if not torch.cuda.is_available():
    print('No GPU — skipping benchmark')
    exit(0)

import os, sys, time, numpy as np, tempfile
os.environ['PYTHONNOUSERSITE'] = '1'

# Check available accelerators
oeq_ok = False
try:
    import openequivariance; oeq_ok = True; print(f'oeq: available ({openequivariance.__version__})')
except: print('oeq: NOT available')

# Build WW system + benchmark
import openmm
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
print(f'System: {m.topology.getNumAtoms()} atoms')

configs = [('f64/OpenCL', {}, 'OpenCL', {})]

# Float32
torch.set_default_dtype(torch.float32)
configs.append(('f32/OpenCL', {'precision':'single'}, 'OpenCL', {}))

# CUDA if available
try:
    openmm.Platform.getPlatformByName('CUDA')
    configs.append(('f64/CUDA', {}, 'CUDA', {}))
    configs.append(('f32/CUDA', {'precision':'single'}, 'CUDA', {}))
except: pass

torch.set_default_dtype(torch.float64)  # reset for f64 tests

for label, prec_kw, pname, pprops in configs:
    try:
        if 'f32' in label:
            torch.set_default_dtype(torch.float32)
        else:
            torch.set_default_dtype(torch.float64)
        mm_sys = ff.createSystem(m.topology,nonbondedMethod=PME,nonbondedCutoff=1.0*unit.nanometer,constraints=None,rigidWater=True)
        pot = MLPotential('mace-off24-medium')
        hy = pot.createMixedSystem(m.topology,mm_sys,pa,interpolate=False,**prec_kw)
        hy.addForce(MonteCarloBarostat(1.0*unit.atmosphere,300.0*unit.kelvin,25))
        plat = openmm.Platform.getPlatformByName(pname)
        integ = openmm.LangevinMiddleIntegrator(300*unit.kelvin,1.0/unit.picosecond,1.0*unit.femtosecond)
        sim = Simulation(m.topology,hy,integ,plat,pprops)
        sim.context.setPositions(m.positions)
        sim.minimizeEnergy(maxIterations=100)
        state = sim.context.getState(getForces=True)
        max_f = float(np.max(np.abs(state.getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer))))
        if max_f > 1e5:
            print(f'  {label}: FAIL force {max_f:.0e}'); continue
        sim.context.setVelocitiesToTemperature(300*unit.kelvin)
        sim.step(20)
        t0=time.time(); sim.step(50); el=time.time()-t0
        nsd=50*1e-6/el*86400
        print(f'  {label}: {nsd:.2f} ns/day | {el/50*1000:.1f} ms/step')
    except Exception as e:
        print(f'  {label}: ERROR — {e}')

torch.set_default_dtype(torch.float64)  # restore
print('BENCHMARK DONE')
"

echo "=== ALL DONE ==="
