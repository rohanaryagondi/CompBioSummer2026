#!/bin/bash
#SBATCH --job-name=f4p2w9ns
#SBATCH --partition=gpu_devel
#SBATCH --gres=gpu:h200:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/env-audit/cuda_compare_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/env-audit/cuda_compare_%j.err

echo "=== original env-delta torch CUDA ==="
source /etc/profile.d/modules.sh
module --force purge
module load miniconda/24.11.3
eval "$(conda shell.bash hook 2>/dev/null)"
conda activate env-delta
export PYTHONNOUSERSITE=1
python -c "
import torch
print('torch:', torch.__version__)
print('cuda available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('device name:', torch.cuda.get_device_name(0))
    x = torch.randn(8, 8, device='cuda')
    print('GPU matmul shape:', tuple((x @ x.t()).shape))
"
echo ""
echo "=== env-delta-v2 torch CUDA ==="
conda deactivate
conda activate env-delta-v2
export PYTHONNOUSERSITE=1
python -c "
import torch
print('torch:', torch.__version__)
print('cuda available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('device name:', torch.cuda.get_device_name(0))
    x = torch.randn(8, 8, device='cuda')
    print('GPU matmul shape:', tuple((x @ x.t()).shape))
"
