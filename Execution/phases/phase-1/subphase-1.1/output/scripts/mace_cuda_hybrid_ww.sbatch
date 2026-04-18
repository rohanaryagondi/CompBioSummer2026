#!/bin/bash
#SBATCH --job-name=w3f8a6qn
#SBATCH --partition=scavenge_gpu
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --time=01:30:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=2
#SBATCH --requeue
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/optj/%x_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/optj/%x_%j.err

echo "=========================================="
echo "MACE hybrid CUDA WW  |  SLURM ${SLURM_JOB_ID}"
echo "Node: $(hostname)"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo unknown)"
echo "Date: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "=========================================="

ENV_DIR=/home/rag88/.conda/envs/env-mace-cuda
OPENMM_DIR=/home/rag88/opt/openmm-cuda128
ENV_PYTHON=${ENV_DIR}/bin/python
SCRIPT_DIR=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts

unset LD_LIBRARY_PATH LIBRARY_PATH CPATH 2>/dev/null || true
export LD_LIBRARY_PATH=${ENV_DIR}/lib:${OPENMM_DIR}/lib
export OPENMM_LIB_PATH=${OPENMM_DIR}/lib
export OPENMM_PLUGIN_DIR=${OPENMM_DIR}/lib/plugins
export PYTHONNOUSERSITE=1
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export MACE_EQUIL_PS=2
export MACE_PROD_PS=3
export MACE_TAG="cuda_hybrid_ww"

echo ""
echo "=== Env verification ==="
${ENV_PYTHON} -c "
import openmm, torch
print('torch:', torch.__version__, '| cuda_avail:', torch.cuda.is_available())
print('openmm:', openmm.__version__, 'at', openmm.__file__)
for i in range(openmm.Platform.getNumPlatforms()):
    p = openmm.Platform.getPlatform(i)
    print(f'  Platform {i}: {p.getName()} (speed {p.getSpeed()})')
" || echo "WARNING: env verification issues, continuing anyway..."

echo ""
echo "=== Running MACE CUDA hybrid on WW domain ==="
set -uo pipefail
${ENV_PYTHON} ${SCRIPT_DIR}/mace_cuda_hybrid_ww.py
EXIT_CODE=$?

echo ""
echo "=========================================="
echo "Exit: $EXIT_CODE"
echo "Completed: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "=========================================="
exit $EXIT_CODE
