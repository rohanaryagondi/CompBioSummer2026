#!/bin/bash
#SBATCH --partition=priority_gpu
#SBATCH --account=prio_mg269
#SBATCH --qos=prio_mg269
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=01:30:00
# NOTE: --output and --error are set by submit_all_diags.sh on the command line
# to use absolute paths. If running manually, add:
#   --output=/path/to/npt_diagnostics/logs/%x_%j.out
#   --error=/path/to/npt_diagnostics/logs/%x_%j.err

# run_npt_diag.sbatch -- SLURM wrapper for NPT barostat diagnostic tests.
#
# Usage:
#   sbatch --export=ALL,NPT_DIAG_TEST=test_A_classical_npt run_npt_diag.sbatch
#
# The NPT_DIAG_TEST variable specifies which test script to run (without .py).
# Job name should be set externally via --job-name (submit_all_diags.sh handles this).
#
# Project: CompBioSummer2026 Sub 1.2 task-001 NPT diagnostics.

set -euo pipefail

# Validate test name
if [ -z "${NPT_DIAG_TEST:-}" ]; then
    echo "ERROR: NPT_DIAG_TEST not set. Usage: sbatch --export=ALL,NPT_DIAG_TEST=test_A_classical_npt run_npt_diag.sbatch"
    exit 1
fi

SCRIPT_DIR="${NPT_DIAG_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
TEST_SCRIPT="${SCRIPT_DIR}/${NPT_DIAG_TEST}.py"

if [ ! -f "$TEST_SCRIPT" ]; then
    echo "ERROR: Test script not found: $TEST_SCRIPT"
    exit 1
fi

# Create logs directory if needed
mkdir -p "${SCRIPT_DIR}/logs"

echo "============================================"
echo "NPT Diagnostic: ${NPT_DIAG_TEST}"
echo "SLURM Job ID:   ${SLURM_JOB_ID}"
echo "Node:           ${SLURMD_NODENAME}"
echo "GPU:            ${CUDA_VISIBLE_DEVICES:-not set}"
echo "Start time:     $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Script:         ${TEST_SCRIPT}"
echo "============================================"

# Activate conda env-mace
source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-mace

# Set required environment variables
export PYTHONNOUSERSITE=1
export LD_LIBRARY_PATH="${CONDA_PREFIX}/lib:${LD_LIBRARY_PATH:-}"

echo "Python: $(which python)"
echo "Conda env: ${CONDA_PREFIX}"
echo ""

# Run the test
cd "${SCRIPT_DIR}"
python "${TEST_SCRIPT}"
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
