#!/bin/bash
set -euo pipefail

# === Priority Queue Safe Submission Wrapper ===
# Wraps sbatch to enforce SU budget, q6 naming, and registry tracking.
#
# Usage: ./prio_submit.sh [sbatch args...] script.sbatch

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRACKER="${SCRIPT_DIR}/prio_su_tracker.sh"
REGISTRY_FILE="${SCRIPT_DIR}/prio_su_registry.json"
BUDGET_FILE="${SCRIPT_DIR}/prio_su_budget.json"

# ---- Validate dependencies ----
if [[ ! -f "$TRACKER" ]]; then
    echo "ERROR: Tracker script not found: $TRACKER" >&2
    exit 3
fi

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 [sbatch args...] script.sbatch" >&2
    echo "" >&2
    echo "Wraps sbatch for priority queue (prio_mg269) with:" >&2
    echo "  - SU budget enforcement" >&2
    echo "  - Automatic q6XXXXXX job naming" >&2
    echo "  - Job registry tracking" >&2
    exit 1
fi

# ---- Step 1: Check budget ----
echo "Checking priority SU budget..."
echo ""

TRACKER_EXIT=0
bash "$TRACKER" || TRACKER_EXIT=$?

if [[ $TRACKER_EXIT -eq 2 ]]; then
    echo "" >&2
    echo "BLOCKED: Priority SU budget is exhausted. Cannot submit." >&2
    echo "Run ./prio_su_tracker.sh for details." >&2
    exit 2
fi

if [[ $TRACKER_EXIT -eq 1 ]]; then
    echo ""
    echo "WARNING: Priority SU budget is above 80%. Proceeding with submission."
    echo "Press Ctrl-C within 5 seconds to abort..."
    sleep 5
fi

# ---- Step 2: Process arguments, inject q6 name and prio account ----
SBATCH_ARGS=()
HAS_Q6_NAME=0
USER_JOBNAME=""
SBATCH_SCRIPT=""
PURPOSE=""

# Parse arguments to find --job-name and the script
ARGS=("$@")
i=0
while [[ $i -lt ${#ARGS[@]} ]]; do
    arg="${ARGS[$i]}"
    case "$arg" in
        --job-name=q6*)
            HAS_Q6_NAME=1
            USER_JOBNAME="${arg#--job-name=}"
            SBATCH_ARGS+=("$arg")
            ;;
        --job-name=*)
            # User provided a non-q6 name; we will override
            USER_JOBNAME="${arg#--job-name=}"
            # Do NOT add to SBATCH_ARGS; we will inject our own
            ;;
        -J)
            i=$((i + 1))
            if [[ $i -lt ${#ARGS[@]} ]]; then
                USER_JOBNAME="${ARGS[$i]}"
                if [[ "$USER_JOBNAME" == q6* ]]; then
                    HAS_Q6_NAME=1
                    SBATCH_ARGS+=("-J" "$USER_JOBNAME")
                fi
                # else: skip, we will inject our own
            fi
            ;;
        --account=*|--qos=*)
            # Strip user-provided account/qos; we force prio_mg269
            ;;
        -A)
            # Skip -A and its value
            i=$((i + 1))
            ;;
        --purpose=*)
            PURPOSE="${arg#--purpose=}"
            ;;
        *)
            SBATCH_ARGS+=("$arg")
            ;;
    esac
    i=$((i + 1))
done

# Generate q6 name if user did not provide one
if [[ $HAS_Q6_NAME -eq 0 ]]; then
    Q6_NAME="q6$(python3 -c "import random,string; print(''.join(random.choices(string.ascii_lowercase+string.digits,k=6)),end='')")"
    SBATCH_ARGS=("--job-name=${Q6_NAME}" "${SBATCH_ARGS[@]}")
else
    Q6_NAME="$USER_JOBNAME"
fi

# Force prio_mg269 account/qos and priority_gpu partition
SBATCH_ARGS=("--account=prio_mg269" "--qos=prio_mg269" "--partition=priority_gpu" "${SBATCH_ARGS[@]}")

echo ""
echo "Submitting to priority queue with:"
echo "  Job name:  ${Q6_NAME}"
echo "  Account:   prio_mg269"
echo "  Partition:  priority_gpu"
echo "  Arguments: ${SBATCH_ARGS[*]}"
echo ""

# ---- Step 3: Submit via sbatch ----
SBATCH_OUTPUT=$(sbatch "${SBATCH_ARGS[@]}" 2>&1)
SBATCH_EXIT=$?

if [[ $SBATCH_EXIT -ne 0 ]]; then
    echo "ERROR: sbatch failed (exit $SBATCH_EXIT):" >&2
    echo "$SBATCH_OUTPUT" >&2
    exit $SBATCH_EXIT
fi

echo "$SBATCH_OUTPUT"

# Parse job ID from "Submitted batch job 12345678"
JOB_ID=""
if [[ "$SBATCH_OUTPUT" =~ Submitted\ batch\ job\ ([0-9]+) ]]; then
    JOB_ID="${BASH_REMATCH[1]}"
fi

if [[ -z "$JOB_ID" ]]; then
    echo "WARNING: Could not parse job ID from sbatch output. Manual registry update needed." >&2
    exit 0
fi

# ---- Step 4: Estimate max SU from time limit ----
# Try to extract time limit from the sbatch script or args
MAX_SU_EST="unknown"
# Check for --time in our args
for arg in "${SBATCH_ARGS[@]}"; do
    if [[ "$arg" =~ ^--time=(.+)$ ]]; then
        TIME_LIMIT="${BASH_REMATCH[1]}"
        # Parse time limit to hours (supports HH:MM:SS, D-HH:MM:SS, MM, MM:SS)
        LIMIT_HOURS=0
        if [[ "$TIME_LIMIT" =~ ^([0-9]+)-([0-9]+):([0-9]+):([0-9]+)$ ]]; then
            LIMIT_HOURS=$(echo "scale=2; ${BASH_REMATCH[1]} * 24 + ${BASH_REMATCH[2]} + ${BASH_REMATCH[3]} / 60.0 + ${BASH_REMATCH[4]} / 3600.0" | bc)
        elif [[ "$TIME_LIMIT" =~ ^([0-9]+):([0-9]+):([0-9]+)$ ]]; then
            LIMIT_HOURS=$(echo "scale=2; ${BASH_REMATCH[1]} + ${BASH_REMATCH[2]} / 60.0 + ${BASH_REMATCH[3]} / 3600.0" | bc)
        elif [[ "$TIME_LIMIT" =~ ^([0-9]+):([0-9]+)$ ]]; then
            LIMIT_HOURS=$(echo "scale=2; ${BASH_REMATCH[1]} / 60.0 + ${BASH_REMATCH[2]} / 3600.0" | bc)
        elif [[ "$TIME_LIMIT" =~ ^([0-9]+)$ ]]; then
            LIMIT_HOURS=$(echo "scale=2; ${BASH_REMATCH[1]} / 60.0" | bc)
        fi
        # Estimate: assume RTX 5000 Ada (billing=15) as conservative default
        # H200 jobs would be billing=300 but we cannot know GPU type from args alone
        MAX_SU_EST=$(echo "scale=1; 15 * $LIMIT_HOURS" | bc)
        break
    fi
done

# ---- Step 5: Register in registry ----
if [[ -z "$PURPOSE" ]]; then
    PURPOSE="Submitted via prio_submit.sh"
fi

NOW_UTC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Initialize registry if it does not exist
if [[ ! -f "$REGISTRY_FILE" ]]; then
    echo '{"jobs": []}' > "$REGISTRY_FILE"
fi

# Append to registry using jq
TMPFILE=$(mktemp)
jq --arg jid "$JOB_ID" \
   --arg jname "$Q6_NAME" \
   --arg ts "$NOW_UTC" \
   --arg purpose "$PURPOSE" \
   --arg max_su "$MAX_SU_EST" \
   '.jobs += [{
     "job_id": $jid,
     "job_name": $jname,
     "submit_time": $ts,
     "purpose": $purpose,
     "status": "SUBMITTED",
     "actual_su": 0,
     "notes": ("Max SU estimate (RTX 5000 Ada rate): " + $max_su)
   }]' "$REGISTRY_FILE" > "$TMPFILE" && mv "$TMPFILE" "$REGISTRY_FILE"

echo ""
echo "Registered job ${JOB_ID} (${Q6_NAME}) in prio_su_registry.json"
if [[ "$MAX_SU_EST" != "unknown" ]]; then
    echo "Max SU estimate (at RTX 5000 Ada rate): ${MAX_SU_EST} SU"
fi

# ---- Step 6: Show updated budget ----
echo ""
echo "--- Updated Budget ---"
bash "$TRACKER" || true
