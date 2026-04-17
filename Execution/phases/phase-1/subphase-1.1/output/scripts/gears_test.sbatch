#!/bin/bash
#SBATCH --job-name=gears_test
#SBATCH --partition=gpu
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/gears_test_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/gears_test_%j.err

# GEARS Test on Tahoe-100M
# Tests GEARS installation, data loading, forward pass, and memory scaling

# Avoid user site-packages conflicts (critical for torch version)
export PYTHONNOUSERSITE=1

# Activate environment
source $(conda info --base 2>/dev/null || echo "/home/rag88/.conda")/etc/profile.d/conda.sh 2>/dev/null
eval "$(conda shell.bash hook 2>/dev/null)" 2>/dev/null

# Try direct Python path if conda activation fails
PYTHON=/home/rag88/.conda/envs/env-delta/bin/python
if ! command -v conda &>/dev/null; then
    echo "Using direct Python path: $PYTHON"
else
    conda activate env-delta
    PYTHON=python
fi

echo "=== Environment ==="
echo "Python: $($PYTHON --version)"
echo "torch: $($PYTHON -c 'import torch; print(torch.__version__)')"
echo "CUDA: $($PYTHON -c 'import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A")')"
echo "GEARS: $($PYTHON -c 'import gears; print("OK")')"
echo "==================="

# Run test
cd /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts
$PYTHON gears_test.py

echo ""
echo "=== Job completed ==="
echo "Exit code: $?"
