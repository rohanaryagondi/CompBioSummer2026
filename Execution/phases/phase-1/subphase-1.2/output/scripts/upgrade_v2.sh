#!/bin/bash
set -euo pipefail
echo "=== TORCH 2.10 UPGRADE v2 $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
echo "Node: $(hostname) | GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo none)"

source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-mace
export PYTHONNOUSERSITE=1

# KEY FIX: ensure conda's libstdc++ (has CXXABI_1.3.15) is found before system's
export LD_LIBRARY_PATH="${CONDA_PREFIX}/lib:${LD_LIBRARY_PATH:-}"

echo "--- Step 1: Upgrade torch ---"
pip install 'torch==2.10.0' 2>&1 | tail -3
python -c "import torch; print(f'torch {torch.__version__}')"

echo "--- Step 2: Verify ALL imports ---"
python -c "
import torch; print(f'torch {torch.__version__}')
import e3nn; print('e3nn: OK')
from mace.calculators.foundations_models import mace_off; print('mace: OK')
from openmmml import MLPotential; print('openmmml: OK')
import openmm; print(f'openmm {openmm.__version__}: OK')
" || { echo "FAILED — reverting"; pip install 'torch==2.5.1' --index-url https://download.pytorch.org/whl/cu121 2>&1 | tail -3; exit 1; }

echo "--- Step 3: Install openequivariance ---"
module load CUDA/12.8.0 2>/dev/null || true
pip install openequivariance==0.6.6 2>&1 | tail -3
python -c "import openequivariance as oeq; print(f'oeq {oeq.__version__}: OK')" || echo "oeq: FAIL (non-fatal)"

echo "--- Step 4: Check platforms ---"
python -c "
import openmm
for pn in ['OpenCL','CUDA']:
    try:
        p = openmm.Platform.getPlatformByName(pn)
        print(f'{pn}: OK (speed={p.getSpeed()})')
    except Exception as e:
        print(f'{pn}: {e}')
"

echo "--- Step 5: Benchmark ---"
python -c "
import os,sys,time,numpy as np,tempfile,torch
os.environ['PYTHONNOUSERSITE']='1'
print(f'GPU: {torch.cuda.get_device_name(0)}')

# Check accelerators
oeq_ok=False
try:
    import openequivariance; oeq_ok=True; print(f'oeq: {openequivariance.__version__}')
except: print('oeq: unavailable')

import openmm
from openmm import unit,MonteCarloBarostat
from openmm.app import PDBFile,Modeller,Simulation,ForceField,PME
from openmmml import MLPotential
from pdbfixer import PDBFixer

pdb=PDBFile('/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ww.pdb')
m=Modeller(pdb.topology,pdb.positions)
std={'ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE','LEU','LYS','MET','PHE','PRO','SER','THR','TRP','TYR','VAL','HID','HIE','HIP','CYX','CYM','ASH','GLH','LYN'}
m.delete([r for r in m.topology.residues() if r.name not in std])
ch0=list(m.topology.chains())[0].id
oth=[]
for c in m.topology.chains():
    if c.id!=ch0: oth.extend(c.residues())
if oth: m.delete(oth)
m.delete([r for r in m.topology.residues() if int(r.id)<6 or int(r.id)>39])
with tempfile.NamedTemporaryFile(suffix='.pdb',mode='w',delete=False) as f:
    PDBFile.writeFile(m.topology,m.positions,f);tmp=f.name
fx=PDBFixer(filename=tmp);fx.findMissingResidues();fx.missingResidues={}
fx.findNonstandardResidues();fx.replaceNonstandardResidues()
fx.findMissingAtoms();fx.addMissingAtoms();fx.addMissingHydrogens(pH=7.0)
m=Modeller(fx.topology,fx.positions);os.unlink(tmp)
pa=list(range(m.topology.getNumAtoms()))
ff=ForceField('amber14-all.xml','amber14/tip3pfb.xml')
m.addSolvent(ff,padding=1.0*unit.nanometer,ionicStrength=0.15*unit.molar,model='tip3p')
print(f'System: {m.topology.getNumAtoms()} atoms')

configs=[('A:f64/OpenCL',{},'OpenCL',{})]

# f32
torch.set_default_dtype(torch.float32)
configs.append(('B:f32/OpenCL',{'precision':'single'},'OpenCL',{}))

# CUDA
try:
    openmm.Platform.getPlatformByName('CUDA')
    configs.append(('C:f64/CUDA',{},'CUDA',{}))
    configs.append(('D:f32/CUDA',{'precision':'single'},'CUDA',{}))
    configs.append(('E:f32/CUDA/mixed',{'precision':'single'},'CUDA',{'Precision':'mixed'}))
except: pass

# OEQ: replace model in PythonForce after system creation
if oeq_ok:
    configs.append(('F:f64/OpenCL/oeq',{'_oeq':True},'OpenCL',{}))

torch.set_default_dtype(torch.float64)

for label,pkw,pname,pprops in configs:
    try:
        use_oeq=pkw.pop('_oeq',False)
        if 'f32' in label: torch.set_default_dtype(torch.float32)
        else: torch.set_default_dtype(torch.float64)
        mm_sys=ff.createSystem(m.topology,nonbondedMethod=PME,nonbondedCutoff=1.0*unit.nanometer,constraints=None,rigidWater=True)
        pot=MLPotential('mace-off24-medium')
        prec_kw={k:v for k,v in pkw.items()}
        hy=pot.createMixedSystem(m.topology,mm_sys,pa,interpolate=False,**prec_kw)
        if use_oeq:
            from mace.calculators.foundations_models import mace_off
            from mace.cli.convert_e3nn_oeq import run as run_e3nn_to_oeq
            raw=mace_off(model='https://github.com/ACEsuit/mace-off/blob/main/mace_off24/MACE-OFF24_medium.model?raw=true',device='cuda',return_raw_model=True).to('cuda')
            oeq_m=run_e3nn_to_oeq(raw,device='cuda').to('cuda')
            for p in oeq_m.parameters(): p.requires_grad=False
            for i in range(hy.getNumForces()):
                f=hy.getForce(i)
                if isinstance(f,openmm.PythonForce):
                    cb=f.getComputeFunction()
                    if hasattr(cb,'keywords') and 'model' in cb.keywords:
                        cb.keywords['model']=oeq_m; break
        hy.addForce(MonteCarloBarostat(1.0*unit.atmosphere,300.0*unit.kelvin,25))
        plat=openmm.Platform.getPlatformByName(pname)
        integ=openmm.LangevinMiddleIntegrator(300*unit.kelvin,1.0/unit.picosecond,1.0*unit.femtosecond)
        sim=Simulation(m.topology,hy,integ,plat,pprops)
        sim.context.setPositions(m.positions)
        sim.minimizeEnergy(maxIterations=100)
        st=sim.context.getState(getForces=True)
        mf=float(np.max(np.abs(st.getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer))))
        if mf>1e5: print(f'  {label}: FAIL force {mf:.0e}');continue
        sim.context.setVelocitiesToTemperature(300*unit.kelvin)
        sim.step(20)
        t0=time.time();sim.step(50);el=time.time()-t0
        nsd=50*1e-6/el*86400
        print(f'  {label}: {nsd:.2f} ns/day | {el/50*1000:.1f} ms/step')
    except Exception as e:
        print(f'  {label}: ERROR — {e}')
torch.set_default_dtype(torch.float64)
print('DONE')
"
echo "=== ALL DONE ==="
