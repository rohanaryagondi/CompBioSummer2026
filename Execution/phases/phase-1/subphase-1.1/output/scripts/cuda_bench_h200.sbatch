#!/bin/bash
#SBATCH --job-name=x3f9w5kb
#SBATCH --partition=gpu_devel
#SBATCH --gres=gpu:h200:1
#SBATCH --time=00:45:00
#SBATCH --mem=24G
#SBATCH --cpus-per-task=2
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/optl/%x_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/optl/%x_%j.err

echo "=========================================="
echo "MACE CUDA bench H200  |  MODE=${BENCH_MODE:-hybrid}  |  SLURM ${SLURM_JOB_ID}"
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

export BENCH_MODE=${BENCH_MODE:-hybrid}
export BENCH_TAG=${BENCH_TAG:-${BENCH_MODE}_h200}

set -uo pipefail
${ENV_PYTHON} ${SCRIPT_DIR}/mace_cuda_bench.py
EXIT_CODE=$?

echo ""
echo "=========================================="
echo "Exit: $EXIT_CODE"
echo "Completed: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "=========================================="
exit $EXIT_CODE
