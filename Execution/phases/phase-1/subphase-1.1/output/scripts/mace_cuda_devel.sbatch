#!/bin/bash
#SBATCH --job-name=d9j6t2xn
#SBATCH --partition=gpu_devel
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --time=00:45:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=2
#SBATCH --requeue
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/optj/%x_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/optj/%x_%j.err

echo "=========================================="
echo "MACE CUDA test RTX  |  SLURM ${SLURM_JOB_ID}"
echo "Node: $(hostname)"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo unknown)"
echo "Date: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "=========================================="

ENV_DIR=/home/rag88/.conda/envs/env-mace-cuda
ENV_PYTHON=${ENV_DIR}/bin/python
SCRIPT_DIR=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts

export PYTHONNOUSERSITE=1
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export MACE_DURATION_PS=10
export MACE_TAG="rtx5000_cuda"

echo ""
echo "=== Env verification ==="
${ENV_PYTHON} -c "
import openmm, torch
print('torch:', torch.__version__, '| cuda_avail:', torch.cuda.is_available())
print('openmm:', openmm.__version__)
for i in range(openmm.Platform.getNumPlatforms()):
    p = openmm.Platform.getPlatform(i)
    print(f'  Platform {i}: {p.getName()} (speed {p.getSpeed()})')
" || echo "WARNING: env verification issues, continuing anyway..."

echo ""
echo "=== Running MACE CUDA test on crambin vacuum ==="
set -uo pipefail
${ENV_PYTHON} ${SCRIPT_DIR}/mace_cuda_crambin.py
EXIT_CODE=$?

echo ""
echo "=========================================="
echo "Exit: $EXIT_CODE"
echo "Completed: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "=========================================="
exit $EXIT_CODE
