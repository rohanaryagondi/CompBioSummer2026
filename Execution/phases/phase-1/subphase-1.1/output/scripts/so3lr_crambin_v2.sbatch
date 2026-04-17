#!/bin/bash
#SBATCH --job-name=so3lr_cram
#SBATCH --partition=gpu_devel
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=so3lr_crambin_%j.out
#SBATCH --error=so3lr_crambin_%j.err

echo "=============================="
echo "SO3LR Crambin NVT - Job $SLURM_JOB_ID"
echo "Node: $(hostname)"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Partition: $SLURM_JOB_PARTITION"
echo "=============================="

# ---- CRITICAL: Load conda via module system ----
module load miniconda
conda activate env-so3lr

echo "Python: $(which python)"
echo "Python version: $(python --version)"
echo "SO3LR: $(python -c 'import so3lr; print(so3lr.__version__)')"
echo "JAX: $(python -c 'import jax; print(jax.__version__)')"

# GPU info
nvidia-smi
python -c "import jax; print('JAX devices:', jax.devices()); print('Backend:', jax.default_backend())"

WORKDIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output"
SCRIPTS="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts"
INPUT_PDB="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/crambin.pdb"

cd "$WORKDIR"

# Prepare input: add hydrogens, strip cell for vacuum simulation
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

# Stage A: 100 ps NVT test
echo ""
echo "=== Stage A: 100 ps NVT ==="
python "${SCRIPTS}/so3lr_crambin_nvt.py" --stage A --output-dir "$WORKDIR"
STAGE_A_EXIT=$?
echo "Stage A exit code: $STAGE_A_EXIT"

if [ $STAGE_A_EXIT -ne 0 ]; then
    echo "Stage A FAILED (exit=$STAGE_A_EXIT)"
    exit 0
fi

STAGE_A_STATUS=$(python -c "import json; d=json.load(open('${WORKDIR}/so3lr_results_stageA.json')); print(d['status'])")
echo "Stage A status: $STAGE_A_STATUS"

if [ "$STAGE_A_STATUS" != "COMPLETED" ]; then
    echo "Stage A incomplete: $STAGE_A_STATUS"
    exit 0
fi

# Stage B: 1 ns NVT production
echo ""
echo "=== Stage B: 1 ns NVT ==="
python "${SCRIPTS}/so3lr_crambin_nvt.py" --stage B --output-dir "$WORKDIR"

echo ""
echo "=============================="
echo "Job completed at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=============================="
