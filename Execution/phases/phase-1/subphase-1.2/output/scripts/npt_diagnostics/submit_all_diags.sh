#!/bin/bash
# submit_all_diags.sh -- Sequential submission helper for NPT diagnostics.
#
# Submits tests one at a time (NOT all at once -- SU budget is limited).
# Each test gets a unique q6* job name per the priority-queue convention.
#
# Usage:
#   ./submit_all_diags.sh                           # Submit all 7 tests sequentially
#   ./submit_all_diags.sh --test test_A_classical_npt  # Submit just one test
#   ./submit_all_diags.sh --dry-run                 # Show what would be submitted
#
# Project: CompBioSummer2026 Sub 1.2 task-001 NPT diagnostics.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SBATCH_SCRIPT="${SCRIPT_DIR}/run_npt_diag.sbatch"
REGISTRY="${SCRIPT_DIR}/job_registry.json"
LOG_DIR="${SCRIPT_DIR}/logs"

# All tests in recommended order (cheapest/fastest first)
ALL_TESTS=(
    test_A_classical_npt
    test_B_barostat_freq100
    test_C_barostat_freq500
    test_D_half_fs
    test_E_aniso_barostat
    test_F_f64_mace
    test_G_combo_best
)

# Estimated SU costs (RTX 5000 Ada = 15 SU/hr)
# Tests A-C,E,F: 30ps at ~2 ns/day => ~22 min wall + 50ps equil ~35 min => ~57 min => ~14 SU
# Test D: 30ps at ~1 ns/day (0.5fs) => ~43 min wall + 50ps equil ~70 min => ~113 min => ~28 SU
# Test G: 30ps at ~0.9 ns/day (0.5fs+f64) => ~48 min + 50ps equil ~80 min => ~128 min => ~32 SU
# But equil also takes time. Being conservative with padding for system build overhead.
declare -A SU_ESTIMATES
SU_ESTIMATES[test_A_classical_npt]=3          # classical is 100x faster, trivial
SU_ESTIMATES[test_B_barostat_freq100]=5
SU_ESTIMATES[test_C_barostat_freq500]=5
SU_ESTIMATES[test_D_half_fs]=8
SU_ESTIMATES[test_E_aniso_barostat]=5
SU_ESTIMATES[test_F_f64_mace]=6
SU_ESTIMATES[test_G_combo_best]=10

# Parse arguments
SINGLE_TEST=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --test)
            SINGLE_TEST="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--test TEST_NAME] [--dry-run]"
            echo ""
            echo "Tests available:"
            for t in "${ALL_TESTS[@]}"; do
                echo "  ${t}  (~${SU_ESTIMATES[$t]} SU)"
            done
            echo ""
            echo "Total estimated: ~42 SU"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Determine which tests to submit
if [ -n "$SINGLE_TEST" ]; then
    # Validate test name
    FOUND=false
    for t in "${ALL_TESTS[@]}"; do
        if [ "$t" = "$SINGLE_TEST" ]; then
            FOUND=true
            break
        fi
    done
    if [ "$FOUND" = false ]; then
        echo "ERROR: Unknown test '$SINGLE_TEST'. Valid tests:"
        for t in "${ALL_TESTS[@]}"; do
            echo "  $t"
        done
        exit 1
    fi
    TESTS_TO_RUN=("$SINGLE_TEST")
else
    TESTS_TO_RUN=("${ALL_TESTS[@]}")
fi

# Create logs directory
mkdir -p "$LOG_DIR"

# Initialize job registry if it doesn't exist
if [ ! -f "$REGISTRY" ]; then
    echo '{"jobs": []}' > "$REGISTRY"
fi

# Generate a q6-prefixed random job name (q6 + 6 alphanumeric chars)
generate_job_name() {
    echo "q6$(head -c 32 /dev/urandom | tr -dc 'a-z0-9' | head -c 6)"
}

echo "============================================"
echo "NPT Diagnostic Submission"
echo "Tests to submit: ${#TESTS_TO_RUN[@]}"
echo "SU budget (est): $(
    total=0
    for t in "${TESTS_TO_RUN[@]}"; do
        total=$((total + ${SU_ESTIMATES[$t]}))
    done
    echo "$total SU"
)"
echo "============================================"
echo ""

TOTAL_SU=0
for test_name in "${TESTS_TO_RUN[@]}"; do
    job_name=$(generate_job_name)
    su_est=${SU_ESTIMATES[$test_name]}
    TOTAL_SU=$((TOTAL_SU + su_est))

    echo "--- ${test_name} ---"
    echo "  Job name: ${job_name}"
    echo "  Est. SU:  ${su_est}"

    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY RUN] Would submit: sbatch --job-name=${job_name} --output=${LOG_DIR}/%x_%j.out --error=${LOG_DIR}/%x_%j.err --export=ALL,NPT_DIAG_TEST=${test_name} ${SBATCH_SCRIPT}"
        echo ""
        continue
    fi

    # Submit (pass absolute output/error paths so SLURM logs land in the right place)
    SUBMIT_OUTPUT=$(sbatch \
        --job-name="${job_name}" \
        --output="${LOG_DIR}/%x_%j.out" \
        --error="${LOG_DIR}/%x_%j.err" \
        --export=ALL,NPT_DIAG_TEST="${test_name}" \
        "${SBATCH_SCRIPT}" 2>&1)

    # Extract job ID
    JOB_ID=$(echo "$SUBMIT_OUTPUT" | grep -oP '\d+' | tail -1)

    if [ -z "$JOB_ID" ]; then
        echo "  ERROR: Failed to submit. Output: ${SUBMIT_OUTPUT}"
        echo ""
        continue
    fi

    echo "  Job ID:   ${JOB_ID}"
    echo "  Log:      ${LOG_DIR}/${job_name}_${JOB_ID}.out"
    echo ""

    # Record in registry (append to JSON array using python for correctness)
    python3 -c "
import json, sys
from datetime import datetime, timezone
reg_path = '${REGISTRY}'
with open(reg_path) as f:
    reg = json.load(f)
reg['jobs'].append({
    'test': '${test_name}',
    'job_name': '${job_name}',
    'job_id': '${JOB_ID}',
    'su_estimate': ${su_est},
    'submitted': datetime.now(timezone.utc).isoformat(),
    'status': 'submitted',
})
with open(reg_path, 'w') as f:
    json.dump(reg, f, indent=2)
"
done

echo "============================================"
echo "Total estimated SU: ${TOTAL_SU}"
if [ "$DRY_RUN" = true ]; then
    echo "[DRY RUN] No jobs submitted."
else
    echo "Job registry: ${REGISTRY}"
fi
echo "============================================"
