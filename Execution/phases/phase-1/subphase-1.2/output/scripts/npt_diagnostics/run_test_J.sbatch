#!/bin/bash
#SBATCH --job-name=j7s8b3rp
#SBATCH --partition=gpu_devel
#SBATCH --account=pi_mg269
#SBATCH --qos=normal
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/npt_diagnostics/logs/j7s8b3rp_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/npt_diagnostics/logs/j7s8b3rp_%j.err

set -euo pipefail

SCRIPT_DIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/npt_diagnostics"

echo "============================================"
echo "NPT Diagnostic: test_J_sentinel (Round 2 sentinel-bond fix)"
echo "SLURM Job ID:   ${SLURM_JOB_ID}"
echo "Node:           ${SLURMD_NODENAME}"
echo "GPU:            ${CUDA_VISIBLE_DEVICES:-not set}"
echo "Start time:     $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"

source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-mace

export PYTHONNOUSERSITE=1
export LD_LIBRARY_PATH="${CONDA_PREFIX}/lib:${LD_LIBRARY_PATH:-}"

echo "Python: $(which python)"
echo "Conda env: ${CONDA_PREFIX}"
echo ""

cd "${SCRIPT_DIR}"
python test_J_sentinel.py
EXIT_CODE=$?

echo ""
echo "============================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "RESULT: PASS"
else
    echo "RESULT: FAIL (exit code ${EXIT_CODE})"
fi
echo "End time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"

exit $EXIT_CODE
