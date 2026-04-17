#!/bin/bash
#SBATCH --job-name=so3lr_cram
#SBATCH --partition=gpu_b200
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

# Environment setup
module purge
module load miniconda
conda activate env-so3lr
export PYTHONPATH="/home/rag88/.local/lib/python3.12/site-packages:${PYTHONPATH}"

echo "Python: $(which python)"
echo "Python version: $(python --version)"
python -c "import numpy; print('numpy:', numpy.__version__)"
python -c "import so3lr; print('SO3LR:', so3lr.__version__)"
python -c "import jax; print('JAX:', jax.__version__)"

nvidia-smi
python -c "import jax; print('JAX devices:', jax.devices()); print('Backend:', jax.default_backend())"

WORKDIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output"
SCRIPTS="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts"

cd "$WORKDIR"

# Input file already prepared on login node
echo "Input file: crambin_h_vacuum.xyz"
python -c "from ase.io import read; a=read('${WORKDIR}/crambin_h_vacuum.xyz'); print(f'{len(a)} atoms, {a.get_chemical_formula()}')"

if [ $? -ne 0 ]; then
    echo "ERROR: Cannot read input file"
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
