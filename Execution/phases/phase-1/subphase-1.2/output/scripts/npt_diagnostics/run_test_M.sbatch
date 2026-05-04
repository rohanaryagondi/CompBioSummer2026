#!/bin/bash
#SBATCH --job-name=m5q4r2bx
#SBATCH --partition=gpu_devel
#SBATCH --account=pi_mg269
#SBATCH --qos=normal
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/npt_diagnostics/logs/m5q4r2bx_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/npt_diagnostics/logs/m5q4r2bx_%j.err

set -euo pipefail

SCRIPT_DIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/npt_diagnostics"

echo "============================================"
echo "NPT Diagnostic: test_M (Round 3C: sentinel + HBonds + dt=0.5 fs)"
echo "SLURM Job ID:   ${SLURM_JOB_ID}"
echo "Node:           ${SLURMD_NODENAME}"
echo "Start time:     $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"

source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-mace
export PYTHONNOUSERSITE=1
export LD_LIBRARY_PATH="${CONDA_PREFIX}/lib:${LD_LIBRARY_PATH:-}"

cd "${SCRIPT_DIR}"
python test_M_combined.py
EXIT_CODE=$?

echo ""
echo "============================================"
[ $EXIT_CODE -eq 0 ] && echo "RESULT: PASS" || echo "RESULT: FAIL (exit code ${EXIT_CODE})"
echo "End time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"
exit $EXIT_CODE
