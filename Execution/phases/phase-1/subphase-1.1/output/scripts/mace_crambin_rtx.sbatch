#!/bin/bash
#SBATCH --job-name=mace-crambin-nvt
#SBATCH --partition=gpu
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --time=04:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/mace_crambin_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/mace_crambin_%j.err

# ============================================================================
# MACE-OFF24 Crambin NVT Simulation -- D1 Gate Validation
# Task 001, Subphase 1.1
# Uses gpu_h200 partition (H200, 80 GB VRAM, sm_90 compatible with cu121)
# ============================================================================

echo "=========================================="
echo "MACE-OFF24 Crambin NVT -- SLURM Job $SLURM_JOB_ID"
echo "Node: $(hostname)"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo 'unknown')"
echo "Date: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "=========================================="

# -- Paths -------------------------------------------------------------------
ENV_DIR=/home/rag88/.conda/envs/env-mace
ENV_PYTHON=${ENV_DIR}/bin/python

SCRIPT_DIR=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts
OUTPUT_DIR=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output
SCRATCH_DIR=/nfs/roberts/scratch/pi_mg269/rag88/mace-crambin

# Avoid user site-packages contamination
export PYTHONNOUSERSITE=1

# -- Step 1: Environment Verification (non-fatal) ----------------------------
echo ""
echo "=== Step 1: Environment Verification ==="
${ENV_PYTHON} -c "
import torch
print('torch:', torch.__version__, '| CUDA:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('  GPU:', torch.cuda.get_device_name(0))
    print('  VRAM:', torch.cuda.get_device_properties(0).total_memory / 1e9, 'GB')

import openmm
print('openmm:', openmm.__version__)
for i in range(openmm.Platform.getNumPlatforms()):
    p = openmm.Platform.getPlatform(i)
    print(f'  Platform {i}: {p.getName()} (speed: {p.getSpeed()})')

from openmmml import MLPotential
print('openmmml: OK')

import mace
print('mace:', mace.__version__)
" || echo "WARNING: Environment verification had issues, continuing anyway..."

# -- Step 2: Run Simulation --------------------------------------------------
echo ""
echo "=== Step 2: Running MACE-OFF24 Crambin NVT ==="
export MACE_OUTPUT_DIR=${OUTPUT_DIR}
export MACE_SCRATCH_DIR=${SCRATCH_DIR}

set -uo pipefail
${ENV_PYTHON} ${SCRIPT_DIR}/mace_crambin_nvt.py
EXIT_CODE=$?

echo ""
echo "=========================================="
echo "Simulation exit code: $EXIT_CODE"
echo "D1 verdict: $([ $EXIT_CODE -eq 0 ] && echo 'PASS' || echo 'FAIL')"
echo "Completed: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "=========================================="

exit $EXIT_CODE
