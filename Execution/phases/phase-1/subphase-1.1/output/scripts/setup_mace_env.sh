#!/bin/bash
# setup_mace_env.sh — Install OpenMM+CUDA, openmm-ml, and CUDA PyTorch into env-mace
# Run this ONCE before submitting the simulation job.
# Can run on login node (no GPU required for install).

set -euo pipefail

CONDA=/apps/software/system/software/miniconda/24.11.3/bin/conda
ENV_NAME=env-mace
ENV_PYTHON=/nfs/roberts/project/pi_mg269/rag88/ycrc_conda/envs/${ENV_NAME}/bin/python
ENV_PIP=/nfs/roberts/project/pi_mg269/rag88/ycrc_conda/envs/${ENV_NAME}/bin/pip

echo "=== Step 1: Install OpenMM 8.5.1 + CUDA via conda-forge ==="
$CONDA install -n $ENV_NAME -c conda-forge openmm=8.5.1 openmm-ml=1.6 cudatoolkit -y 2>&1

echo ""
echo "=== Step 2: Install CUDA-enabled PyTorch ==="
# Remove CPU-only torch if it's in the env's site-packages
$ENV_PIP uninstall torch -y 2>/dev/null || true
# Install PyTorch with CUDA 12.1 support (compatible with cluster driver)
$ENV_PIP install torch --index-url https://download.pytorch.org/whl/cu121 2>&1

echo ""
echo "=== Step 3: Re-install mace-torch to ensure compatibility ==="
$ENV_PIP install mace-torch==0.3.15 --no-deps 2>&1

echo ""
echo "=== Step 4: Verification ==="
# Use PYTHONNOUSERSITE=1 to avoid user site-packages contamination
PYTHONNOUSERSITE=1 $ENV_PYTHON -c "
import torch
print('torch version:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
print('CUDA build version:', torch.version.cuda)
print()

import openmm
print('openmm version:', openmm.__version__)
for i in range(openmm.Platform.getNumPlatforms()):
    p = openmm.Platform.getPlatform(i)
    print(f'  Platform {i}: {p.getName()} (speed: {p.getSpeed()})')
print()

from openmmml import MLPotential
print('openmmml imported OK')
print('Registered potentials:', MLPotential.getRegisteredPotentials())
print()

import mace
print('mace version:', mace.__version__)
print()
print('=== ALL CHECKS PASSED ===')
"

echo ""
echo "Setup complete. Submit mace_crambin.sbatch next."
