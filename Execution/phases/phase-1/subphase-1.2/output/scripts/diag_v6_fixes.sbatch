#!/bin/bash
#SBATCH --job-name=d6v6fxwq
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --account=pi_mg269
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/slurm_logs/diag_v6_fixes_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/slurm_logs/diag_v6_fixes_%j.err

source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-mace
export PYTHONNOUSERSITE=1
export LD_LIBRARY_PATH="${CONDA_PREFIX}/lib:${LD_LIBRARY_PATH:-}"

# Test WW with cleaned state (fresh start) + short target to verify equil works
export MACE_HYBRID_PROTEIN=ww
export MACE_HYBRID_TAG=d6v6fxwq
export MACE_HYBRID_TARGET_NS=0.001
export MACE_HYBRID_WALLTIME_GUARD_SEC=600

echo "=== Diagnostic: v6 fixes (equil 50ps, _dof fix, checkpoint mismatch handling) ==="
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo unknown)"
echo "Date: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"

python /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/mace_hybrid_npt.py
EXIT=$?
echo "Exit code: $EXIT"

# Clean up diagnostic scratch
rm -rf /nfs/roberts/scratch/pi_mg269/rag88/alpha-m/mace-npt/d6v6fxwq

exit $EXIT
