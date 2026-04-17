#!/bin/bash
#SBATCH --job-name=so3lr_cram
#SBATCH --partition=gpu_devel
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=so3lr_crambin_devel_%j.out
#SBATCH --error=so3lr_crambin_devel_%j.err

# ---- SO3LR Crambin NVT Simulation (gpu_devel) ----
# Task 002 - D1 Gate Evidence

echo "=============================="
echo "SO3LR Crambin NVT - Job $SLURM_JOB_ID"
echo "Node: $(hostname)"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Partition: $SLURM_JOB_PARTITION"
echo "=============================="

# Environment setup
eval "$(conda shell.bash hook 2>/dev/null)"
conda activate env-so3lr

echo "Python: $(python --version)"
echo "JAX version: $(python -c 'import jax; print(jax.__version__)')"
echo "SO3LR version: $(python -c 'import so3lr; print(so3lr.__version__)')"

# CUDA/GPU info
nvidia-smi
echo ""
python -c "import jax; print('JAX devices:', jax.devices()); print('JAX backend:', jax.default_backend())"

# Working directory
WORKDIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output"
SCRIPTS="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts"
INPUT_PDB="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/crambin.pdb"

cd "$WORKDIR"

# Step 1: Prepare input (add hydrogens, convert to XYZ)
echo ""
echo "=== Preparing input structure ==="
python -c "
from ase.io import read, write
import subprocess
subprocess.run(['/home/rag88/.local/bin/obabel', '${INPUT_PDB}', '-O', '${WORKDIR}/crambin_h.pdb', '-h'], check=True)
atoms = read('${WORKDIR}/crambin_h.pdb')
atoms.set_cell([0,0,0])
atoms.set_pbc(False)
atoms.center()
write('${WORKDIR}/crambin_h_vacuum.xyz', atoms)
print(f'Prepared: {len(atoms)} atoms, formula: {atoms.get_chemical_formula()}')
"

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to prepare input structure"
    exit 1
fi

# Step 2: Run Stage A (100 ps test)
echo ""
echo "=== Stage A: 100 ps NVT test ==="
python "${SCRIPTS}/so3lr_crambin_nvt.py" \
    --stage A \
    --output-dir "$WORKDIR"

STAGE_A_EXIT=$?
echo "Stage A exit code: $STAGE_A_EXIT"

if [ $STAGE_A_EXIT -ne 0 ]; then
    echo "Stage A FAILED. Skipping Stage B."
    exit 0
fi

# Check Stage A results
STAGE_A_STATUS=$(python -c "import json; d=json.load(open('${WORKDIR}/so3lr_results_stageA.json')); print(d['status'])")
echo "Stage A status: $STAGE_A_STATUS"

if [ "$STAGE_A_STATUS" != "COMPLETED" ]; then
    echo "Stage A did not complete successfully. Skipping Stage B."
    exit 0
fi

# Step 3: Run Stage B (1 ns production)
echo ""
echo "=== Stage B: 1 ns NVT production ==="
python "${SCRIPTS}/so3lr_crambin_nvt.py" \
    --stage B \
    --output-dir "$WORKDIR"

echo ""
echo "=============================="
echo "Job completed at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Results in: $WORKDIR"
echo "=============================="
