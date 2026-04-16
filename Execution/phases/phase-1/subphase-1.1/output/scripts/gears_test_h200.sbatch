#!/bin/bash
#SBATCH --job-name=gears_h200
#SBATCH --partition=gpu_devel
#SBATCH --gres=gpu:h200:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=96G
#SBATCH --time=00:30:00
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/gears_test_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/gears_test_%j.err

# GEARS Test on H200 GPU
export PYTHONNOUSERSITE=1

PYTHON=/home/rag88/.conda/envs/env-delta/bin/python

echo "=== Environment ==="
$PYTHON -c "import torch; print('torch:', torch.__version__, 'CUDA:', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')" 2>&1
$PYTHON -c "import gears; print('GEARS: OK')" 2>&1
echo "==================="

cd /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts
$PYTHON gears_test.py

echo ""
echo "=== Job completed ==="
echo "Exit code: $?"
