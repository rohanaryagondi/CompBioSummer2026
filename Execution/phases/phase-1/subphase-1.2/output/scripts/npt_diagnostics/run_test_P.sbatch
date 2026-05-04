#!/bin/bash
#SBATCH --job-name=p3w7m9kc
#SBATCH --partition=priority_gpu
#SBATCH --account=prio_mg269
#SBATCH --qos=prio_mg269
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=03:30:00
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/npt_diagnostics/logs/p3w7m9kc_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/npt_diagnostics/logs/p3w7m9kc_%j.err

set -euo pipefail

SCRIPT_DIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/npt_diagnostics"

echo "============================================"
echo "NPT Production Confirmation: test_P_extended"
echo "Config: sentinel-bond + HBonds + dt=1 fs (Round 3B winner)"
echo "Target: 1 ps NVT + 100 ps NPT"
echo "Partition: priority_gpu / prio_mg269 (~10 SU budget)"
echo "SLURM Job ID:   ${SLURM_JOB_ID}"
echo "Node:           ${SLURMD_NODENAME}"
echo "GPU:            ${CUDA_VISIBLE_DEVICES:-not set}"
echo "Start time:     $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"

source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-mace
export PYTHONNOUSERSITE=1
export LD_LIBRARY_PATH="${CONDA_PREFIX}/lib:${LD_LIBRARY_PATH:-}"

cd "${SCRIPT_DIR}"
python test_P_extended.py
EXIT_CODE=$?

echo ""
echo "============================================"
[ $EXIT_CODE -eq 0 ] && echo "RESULT: PASS" || echo "RESULT: FAIL (exit code ${EXIT_CODE})"
echo "End time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"
exit $EXIT_CODE
