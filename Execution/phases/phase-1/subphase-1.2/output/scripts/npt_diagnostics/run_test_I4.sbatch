#!/bin/bash
#SBATCH --partition=gpu_devel
#SBATCH --account=pi_mg269
#SBATCH --qos=normal
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --job-name=t4btx5wp

set -euo pipefail

SCRIPT_DIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/npt_diagnostics"

echo "============================================"
echo "NPT Diagnostic: test_I4_both (Step 2, enforce_pbc + molecular)"
echo "SLURM Job ID:   ${SLURM_JOB_ID}"
echo "Start time:     $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"

source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-mace

export PYTHONNOUSERSITE=1
export LD_LIBRARY_PATH="${CONDA_PREFIX}/lib:${LD_LIBRARY_PATH:-}"

cd "${SCRIPT_DIR}"
python test_I4_both.py
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "RESULT: PASS"
else
    echo "RESULT: FAIL (exit ${EXIT_CODE})"
fi
echo "End: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit $EXIT_CODE
