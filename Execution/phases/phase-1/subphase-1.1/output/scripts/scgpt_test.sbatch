#!/bin/bash
#SBATCH --job-name=scgpt_test
#SBATCH --partition=gpu_devel
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts/scgpt_test_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts/scgpt_test_%j.err

echo "=== SLURM Job Info ==="
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'unknown')"
echo "Date: $(date -u)"
echo ""

# Load conda
source /etc/profile.d/modules.sh
module --force purge
module load miniconda/24.11.3
eval "$(conda shell.bash hook 2>/dev/null)"
conda activate env-delta

# Fix library path for conda-forge ICU
export LD_LIBRARY_PATH=/home/rag88/.conda/envs/env-delta/lib:$LD_LIBRARY_PATH

# Run test
cd /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts
python scgpt_test.py

echo ""
echo "=== Job Complete ==="
echo "Exit code: $?"
echo "Date: $(date -u)"
