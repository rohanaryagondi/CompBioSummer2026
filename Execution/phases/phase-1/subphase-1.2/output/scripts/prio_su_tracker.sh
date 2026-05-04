#!/bin/bash
set -euo pipefail

# === Priority SU Tracker ===
# Tracks SU consumption on prio_mg269 for CompBioSummer2026 project jobs.
# Identifies project jobs via: (1) q6* job names in sacct, (2) job IDs in registry.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUDGET_FILE="${SCRIPT_DIR}/prio_su_budget.json"
REGISTRY_FILE="${SCRIPT_DIR}/prio_su_registry.json"
STATUS_FILE="${SCRIPT_DIR}/prio_su_status.json"

USER="rag88"
ACCOUNT="prio_mg269"

# ---- Load budget config ----
if [[ ! -f "$BUDGET_FILE" ]]; then
    echo "ERROR: Budget file not found: $BUDGET_FILE" >&2
    exit 3
fi
BUDGET_SU=$(jq -r '.budget_su' "$BUDGET_FILE")
WARNING_THRESHOLD=$(jq -r '.warning_threshold' "$BUDGET_FILE")

# ---- Collect job IDs from registry (belt) ----
declare -A REGISTRY_JOBS=()
if [[ -f "$REGISTRY_FILE" ]]; then
    while IFS= read -r jid; do
        if [[ -n "$jid" ]]; then
            REGISTRY_JOBS["$jid"]=1
        fi
    done < <(jq -r '.jobs[].job_id' "$REGISTRY_FILE" 2>/dev/null)
fi

# ---- Query sacct for q6* jobs on prio_mg269 (suspenders) ----
# Use a broad start time to catch all project history.
# We query all prio_mg269 jobs and filter by name prefix q6 + registry IDs.
SACCT_OUTPUT=$(sacct -u "$USER" -A "$ACCOUNT" \
    --format="JobID,JobName,State,Elapsed,AllocTRES%80" \
    --parsable2 --noheader --starttime=2026-01-01 2>/dev/null || true)

# ---- Parse and accumulate SU ----
TOTAL_SU=0
JOB_COUNT=0
COMPLETED_COUNT=0
FAILED_COUNT=0
RUNNING_COUNT=0
PENDING_COUNT=0
CANCELLED_COUNT=0
OTHER_COUNT=0

# We only want parent job rows (no .batch, .extern substeps).
# A parent row has a purely numeric JobID (no dot).
declare -A SEEN_JOBS=()
JOB_DETAILS=""

while IFS='|' read -r jobid jobname state elapsed alloctres; do
    # Skip empty lines
    [[ -z "$jobid" ]] && continue

    # Skip substep rows (contain a dot: 12345.batch, 12345.extern)
    [[ "$jobid" == *.* ]] && continue

    # Check if this job belongs to our project:
    #   (a) job name starts with q6, OR
    #   (b) job ID is in the registry
    is_project=0
    if [[ "$jobname" == q6* ]]; then
        is_project=1
    elif [[ -n "${REGISTRY_JOBS[$jobid]+x}" ]]; then
        is_project=1
    fi

    [[ "$is_project" -eq 0 ]] && continue

    # Skip if we already processed this job ID (dedup)
    [[ -n "${SEEN_JOBS[$jobid]+x}" ]] && continue
    SEEN_JOBS["$jobid"]=1

    # Extract billing weight from AllocTRES (e.g., "billing=15,cpu=2,...")
    billing=0
    if [[ "$alloctres" =~ billing=([0-9]+) ]]; then
        billing="${BASH_REMATCH[1]}"
    fi

    # Parse elapsed time (HH:MM:SS or D-HH:MM:SS) to fractional hours
    elapsed_hours=0
    if [[ "$elapsed" =~ ^([0-9]+)-([0-9]+):([0-9]+):([0-9]+)$ ]]; then
        days="${BASH_REMATCH[1]}"
        hours="${BASH_REMATCH[2]}"
        mins="${BASH_REMATCH[3]}"
        secs="${BASH_REMATCH[4]}"
        elapsed_hours=$(echo "scale=6; $days * 24 + $hours + $mins / 60.0 + $secs / 3600.0" | bc)
    elif [[ "$elapsed" =~ ^([0-9]+):([0-9]+):([0-9]+)$ ]]; then
        hours="${BASH_REMATCH[1]}"
        mins="${BASH_REMATCH[2]}"
        secs="${BASH_REMATCH[3]}"
        elapsed_hours=$(echo "scale=6; $hours + $mins / 60.0 + $secs / 3600.0" | bc)
    fi

    # SU = billing * elapsed_hours
    su_used=$(echo "scale=2; $billing * $elapsed_hours" | bc)

    TOTAL_SU=$(echo "scale=2; $TOTAL_SU + $su_used" | bc)
    JOB_COUNT=$((JOB_COUNT + 1))

    # Classify state
    case "$state" in
        COMPLETED)     COMPLETED_COUNT=$((COMPLETED_COUNT + 1)) ;;
        FAILED)        FAILED_COUNT=$((FAILED_COUNT + 1)) ;;
        RUNNING)       RUNNING_COUNT=$((RUNNING_COUNT + 1)) ;;
        PENDING)       PENDING_COUNT=$((PENDING_COUNT + 1)) ;;
        CANCELLED*)    CANCELLED_COUNT=$((CANCELLED_COUNT + 1)) ;;
        *)             OTHER_COUNT=$((OTHER_COUNT + 1)) ;;
    esac

    JOB_DETAILS="${JOB_DETAILS}  ${jobid}  ${jobname}  ${state}  ${elapsed}  billing=${billing}  SU=${su_used}\n"

done <<< "$SACCT_OUTPUT"

# ---- If sacct returned nothing for a registry job, use registry's actual_su ----
for reg_id in "${!REGISTRY_JOBS[@]}"; do
    if [[ -z "${SEEN_JOBS[$reg_id]+x}" ]]; then
        # This registry job was not found in sacct; use the recorded actual_su
        reg_su=$(jq -r --arg jid "$reg_id" '.jobs[] | select(.job_id == $jid) | .actual_su // 0' "$REGISTRY_FILE" 2>/dev/null)
        reg_name=$(jq -r --arg jid "$reg_id" '.jobs[] | select(.job_id == $jid) | .job_name // "unknown"' "$REGISTRY_FILE" 2>/dev/null)
        reg_status=$(jq -r --arg jid "$reg_id" '.jobs[] | select(.job_id == $jid) | .status // "UNKNOWN"' "$REGISTRY_FILE" 2>/dev/null)

        if [[ -n "$reg_su" && "$reg_su" != "0" && "$reg_su" != "null" ]]; then
            TOTAL_SU=$(echo "scale=2; $TOTAL_SU + $reg_su" | bc)
            JOB_COUNT=$((JOB_COUNT + 1))
            case "$reg_status" in
                COMPLETED)     COMPLETED_COUNT=$((COMPLETED_COUNT + 1)) ;;
                FAILED)        FAILED_COUNT=$((FAILED_COUNT + 1)) ;;
                RUNNING)       RUNNING_COUNT=$((RUNNING_COUNT + 1)) ;;
                *)             OTHER_COUNT=$((OTHER_COUNT + 1)) ;;
            esac
            JOB_DETAILS="${JOB_DETAILS}  ${reg_id}  ${reg_name}  ${reg_status}  (registry)  SU=${reg_su}\n"
            SEEN_JOBS["$reg_id"]=1
        fi
    fi
done

# ---- Calculate remaining and status ----
REMAINING_SU=$(echo "scale=2; $BUDGET_SU - $TOTAL_SU" | bc)
USAGE_FRACTION=$(echo "scale=4; $TOTAL_SU / $BUDGET_SU" | bc)

if (( $(echo "$TOTAL_SU >= $BUDGET_SU" | bc -l) )); then
    STATUS="OVER_BUDGET"
    EXIT_CODE=2
elif (( $(echo "$USAGE_FRACTION >= $WARNING_THRESHOLD" | bc -l) )); then
    STATUS="WARNING"
    EXIT_CODE=1
else
    STATUS="WITHIN_BUDGET"
    EXIT_CODE=0
fi

# ---- Build state summary string ----
STATE_PARTS=()
[[ $COMPLETED_COUNT -gt 0 ]] && STATE_PARTS+=("${COMPLETED_COUNT} COMPLETED")
[[ $FAILED_COUNT -gt 0 ]] && STATE_PARTS+=("${FAILED_COUNT} FAILED")
[[ $RUNNING_COUNT -gt 0 ]] && STATE_PARTS+=("${RUNNING_COUNT} RUNNING")
[[ $PENDING_COUNT -gt 0 ]] && STATE_PARTS+=("${PENDING_COUNT} PENDING")
[[ $CANCELLED_COUNT -gt 0 ]] && STATE_PARTS+=("${CANCELLED_COUNT} CANCELLED")
[[ $OTHER_COUNT -gt 0 ]] && STATE_PARTS+=("${OTHER_COUNT} OTHER")

STATE_SUMMARY=""
if [[ ${#STATE_PARTS[@]} -gt 0 ]]; then
    STATE_SUMMARY=$(IFS=', '; echo "${STATE_PARTS[*]}")
fi

# ---- Print summary ----
echo ""
echo "=== Priority SU Tracker ==="
printf "Budget:    %.1f SU\n" "$BUDGET_SU"
if [[ $JOB_COUNT -gt 0 ]]; then
    printf "Used:      %.1f SU (%d jobs: %s)\n" "$TOTAL_SU" "$JOB_COUNT" "$STATE_SUMMARY"
else
    printf "Used:      %.1f SU (no project jobs found)\n" "$TOTAL_SU"
fi
printf "Remaining: %.1f SU\n" "$REMAINING_SU"
echo "Status:    ${STATUS}"

# Print job details if any
if [[ -n "$JOB_DETAILS" ]]; then
    echo ""
    echo "--- Job Details ---"
    echo -e "$JOB_DETAILS"
fi

# ---- Write status JSON ----
NOW_UTC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
cat > "$STATUS_FILE" << ENDJSON
{
  "timestamp": "${NOW_UTC}",
  "budget_su": ${BUDGET_SU},
  "used_su": ${TOTAL_SU},
  "remaining_su": ${REMAINING_SU},
  "status": "${STATUS}",
  "job_count": ${JOB_COUNT},
  "jobs_completed": ${COMPLETED_COUNT},
  "jobs_failed": ${FAILED_COUNT},
  "jobs_running": ${RUNNING_COUNT},
  "jobs_pending": ${PENDING_COUNT},
  "jobs_cancelled": ${CANCELLED_COUNT}
}
ENDJSON

# ---- Optional: enforce budget by cancelling running prio jobs ----
if [[ "${1:-}" == "--enforce" && "$STATUS" == "OVER_BUDGET" && $RUNNING_COUNT -gt 0 ]]; then
    echo ""
    echo "!!! ENFORCEMENT: Budget exceeded with ${RUNNING_COUNT} running job(s). Cancelling..."
    while IFS='|' read -r jobid jobname state elapsed alloctres; do
        [[ -z "$jobid" || "$jobid" == *.* ]] && continue
        is_project=0
        if [[ "$jobname" == q6* ]]; then is_project=1
        elif [[ -n "${REGISTRY_JOBS[$jobid]+x}" ]]; then is_project=1; fi
        [[ "$is_project" -eq 0 ]] && continue
        if [[ "$state" == "RUNNING" ]]; then
            echo "  scancel ${jobid} (${jobname})"
            scancel "$jobid" 2>/dev/null || true
        fi
    done <<< "$SACCT_OUTPUT"
    echo "Enforcement complete."
fi

exit $EXIT_CODE
