#!/bin/bash
#SBATCH --job-name=m6q4p8xn
#SBATCH --partition=gpu_devel
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --time=00:30:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=2
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/optl/%x_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/optl/%x_%j.err

echo "=========================================="
echo "MACE CUDA bench hybrid (BLOCKING)  |  SLURM ${SLURM_JOB_ID}"
echo "Node: $(hostname)"
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

# Force CUDA operations to run synchronously for diagnostic purposes
export CUDA_LAUNCH_BLOCKING=1

export BENCH_MODE=hybrid
export BENCH_TAG=hybrid_rtx5000_blocking
export BENCH_HYBRID_EQUIL_PS=1
export BENCH_HYBRID_PROD_PS=2

set -uo pipefail
${ENV_PYTHON} ${SCRIPT_DIR}/mace_cuda_bench.py
EXIT_CODE=$?

echo ""
echo "Exit: $EXIT_CODE"
exit $EXIT_CODE
