#!/bin/bash
#SBATCH --job-name=x7k9m2q4
#SBATCH --partition=gpu_devel
#SBATCH --gres=gpu:h200:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=00:15:00
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/env-audit/smoke_h200_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/env-audit/smoke_h200_%j.err

echo "=== SLURM Job Info ==="
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Partition: $SLURM_JOB_PARTITION"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo unknown)"
echo "Driver: $(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null || echo unknown)"
echo "Date: $(date -u)"
echo ""

source /etc/profile.d/modules.sh
module --force purge
module load miniconda/24.11.3
eval "$(conda shell.bash hook 2>/dev/null)"
conda activate env-delta-v2

export PYTHONNOUSERSITE=1
export LD_LIBRARY_PATH=/home/rag88/.conda/envs/env-delta-v2/lib:$LD_LIBRARY_PATH

cd /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/env-audit
python smoke_test.py
echo "=== Job Complete ==="
