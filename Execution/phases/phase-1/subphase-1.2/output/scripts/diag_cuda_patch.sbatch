#!/bin/bash
#SBATCH --job-name=k9v2m7fx
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --time=00:10:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --account=pi_mg269
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/slurm_logs/diag_cuda_patch_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/slurm_logs/diag_cuda_patch_%j.err

# Diagnostic: verify MACE CUDA patch (GPU NL + cuequivariance) before production.
# Per diagnostic-first rule: gpu partition, 10 min walltime, smallest plausible target.

set -euo pipefail
echo "SLURM Job ID: ${SLURM_JOB_ID}"
echo "Node: $(hostname)"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo unknown)"
echo "Date: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"

source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-mace
export PYTHONNOUSERSITE=1

/home/rag88/.conda/envs/env-mace/bin/python \
    /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/diag_cuda_patch.py

EXIT_CODE=$?
echo "Diagnostic exit: ${EXIT_CODE} (0=PASS, 1=FAIL)"
exit $EXIT_CODE
