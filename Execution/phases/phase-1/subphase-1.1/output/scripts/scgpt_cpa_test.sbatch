#!/bin/bash
#SBATCH --job-name=scgpt_cpa
#SBATCH --partition=gpu_devel
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts/scgpt_cpa_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts/scgpt_cpa_%j.err

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

cd /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts

echo "=========================================="
echo "     PART 1: scGPT Test"
echo "=========================================="
python scgpt_test.py
SCGPT_EXIT=$?
echo ""
echo "scGPT exit code: $SCGPT_EXIT"
echo ""

echo "=========================================="
echo "     PART 2: CPA Test"
echo "=========================================="
python cpa_test.py
CPA_EXIT=$?
echo ""
echo "CPA exit code: $CPA_EXIT"
echo ""

echo "=== Job Complete ==="
echo "scGPT: $SCGPT_EXIT"
echo "CPA: $CPA_EXIT"
echo "Date: $(date -u)"
