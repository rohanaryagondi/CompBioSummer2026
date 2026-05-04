#!/bin/bash
# =============================================================================
# prio_su_enforce.sh -- PROJECTED priority SU budget enforcement.
#
# Computes projected SU consumption (current used + remaining-walltime × billing
# for RUNNING/PENDING Sub 1.2 priority jobs). If projected > budget, cancels
# the largest-projected jobs until projected <= budget. Writes a help-needed
# notification so head-1.2 sees the action on next check-in.
#
# Differs from prio_su_tracker.sh: tracker measures CURRENT consumption
# (elapsed × billing); this script projects FUTURE consumption from walltime.
# A job within current budget can still be auto-cancelled if its remaining
# walltime would push the total over the cap.
#
# Usage:
#   ./prio_su_enforce.sh             # enforce; cancel offenders; write notification
#   ./prio_su_enforce.sh --dry-run   # report what would be cancelled
#
# Exit codes:
#   0  WITHIN_BUDGET (projected) -- no action
#   1  cancellations made -- check shared/help-needed/head-1.2-su-budget-auto-cancel-*
#   2  still over budget after cancellations OR error
#
# Identification scheme (same as tracker): jobs with q6* name OR job_id in
# prio_su_registry.json. Other-project jobs are invisible.
# =============================================================================
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUDGET_FILE="${SCRIPT_DIR}/prio_su_budget.json"
REGISTRY_FILE="${SCRIPT_DIR}/prio_su_registry.json"
HELP_NEEDED_DIR="${SCRIPT_DIR}/../../../../shared/help-needed"

DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

[[ ! -f "$BUDGET_FILE" ]] && { echo "ERROR: $BUDGET_FILE not found" >&2; exit 2; }
BUDGET_SU=$(jq -r '.budget_su' "$BUDGET_FILE")

# Get currently-used SU from tracker
USED_SU=$(bash "${SCRIPT_DIR}/prio_su_tracker.sh" 2>/dev/null | grep "^Used:" | awk '{print $2}')
[[ -z "$USED_SU" ]] && USED_SU=0

# Build registry job ID set
declare -A REGISTRY_JOBS=()
if [[ -f "$REGISTRY_FILE" ]]; then
    while IFS= read -r jid; do
        [[ -n "$jid" ]] && REGISTRY_JOBS["$jid"]=1
    done < <(jq -r '.jobs[].job_id' "$REGISTRY_FILE" 2>/dev/null)
fi

# Helper: parse SLURM time (HH:MM:SS, D-HH:MM:SS, MM:SS) to seconds
parse_time() {
    local t="$1"
    if [[ "$t" =~ ^([0-9]+)-([0-9]+):([0-9]+):([0-9]+)$ ]]; then
        echo $(( BASH_REMATCH[1]*86400 + BASH_REMATCH[2]*3600 + BASH_REMATCH[3]*60 + BASH_REMATCH[4] ))
    elif [[ "$t" =~ ^([0-9]+):([0-9]+):([0-9]+)$ ]]; then
        echo $(( BASH_REMATCH[1]*3600 + BASH_REMATCH[2]*60 + BASH_REMATCH[3] ))
    elif [[ "$t" =~ ^([0-9]+):([0-9]+)$ ]]; then
        echo $(( BASH_REMATCH[1]*60 + BASH_REMATCH[2] ))
    else
        echo 0
    fi
}

# Compute projected SU per in-flight Sub 1.2 priority job
INFLIGHT_PROJECTED=0
declare -A INFLIGHT_DETAILS=()
declare -a SORTED_BY_PROJ=()

while IFS='|' read -r jobid jobname partition state elapsed timelimit; do
    [[ -z "$jobid" ]] && continue
    [[ "$state" != "RUNNING" && "$state" != "PENDING" ]] && continue
    [[ "$partition" != "priority_gpu" && "$partition" != "priority" ]] && continue

    # Sub 1.2 project filter: q6* name OR registry job_id
    is_project=0
    if [[ "$jobname" == q6* ]]; then is_project=1
    elif [[ -n "${REGISTRY_JOBS[$jobid]+x}" ]]; then is_project=1; fi
    [[ "$is_project" -eq 0 ]] && continue

    wt_sec=$(parse_time "$timelimit")
    el_sec=$(parse_time "$elapsed")
    rem_sec=$((wt_sec - el_sec))
    [[ $rem_sec -lt 0 ]] && rem_sec=0

    # Billing rate: assume RTX 5000 Ada (priority_gpu default for our jobs)
    BILLING_RATE=15
    proj_su=$(echo "scale=2; $BILLING_RATE * $rem_sec / 3600" | bc)

    INFLIGHT_DETAILS["$jobid"]="${jobname}|${state}|${proj_su}|${timelimit}|${elapsed}"
    SORTED_BY_PROJ+=("${proj_su}:${jobid}")
    INFLIGHT_PROJECTED=$(echo "scale=2; $INFLIGHT_PROJECTED + $proj_su" | bc)
done < <(squeue -u rag88 -o "%i|%j|%P|%T|%M|%l" -h)

PROJECTED_TOTAL=$(echo "scale=2; $USED_SU + $INFLIGHT_PROJECTED" | bc)
EXCESS=$(echo "scale=2; $PROJECTED_TOTAL - $BUDGET_SU" | bc)

echo "=== Projected SU enforcement ==="
echo "Budget cap:          $BUDGET_SU SU"
echo "Used (terminated):   $USED_SU SU"
echo "In-flight projected: $INFLIGHT_PROJECTED SU"
echo "Projected total:     $PROJECTED_TOTAL SU"
echo "Excess:              $EXCESS SU"

if (( $(echo "$EXCESS <= 0" | bc -l) )); then
    echo "Status:              WITHIN_BUDGET (projected). No action."
    exit 0
fi

# Sort jobs by projected_su descending; cancel until excess <= 0
IFS=$'\n' SORTED=($(printf "%s\n" "${SORTED_BY_PROJ[@]}" | sort -t: -k1,1 -nr))
unset IFS

declare -a CANCEL_LIST=()
running_excess=$EXCESS
for entry in "${SORTED[@]}"; do
    proj_su="${entry%%:*}"
    jobid="${entry##*:}"
    if (( $(echo "$running_excess <= 0" | bc -l) )); then break; fi
    CANCEL_LIST+=("${jobid}:${proj_su}")
    running_excess=$(echo "scale=2; $running_excess - $proj_su" | bc)
done

echo ""
echo "Cancellation plan: ${#CANCEL_LIST[@]} job(s)"
for entry in "${CANCEL_LIST[@]}"; do
    jobid="${entry%%:*}"
    proj_su="${entry##*:}"
    detail="${INFLIGHT_DETAILS[$jobid]}"
    name=$(echo "$detail" | cut -d'|' -f1)
    state=$(echo "$detail" | cut -d'|' -f2)
    timelimit=$(echo "$detail" | cut -d'|' -f4)
    elapsed=$(echo "$detail" | cut -d'|' -f5)
    echo "  $jobid ($name, $state, walltime=${timelimit}, elapsed=${elapsed}) — saves $proj_su SU"
done

if [[ $DRY_RUN -eq 1 ]]; then
    echo ""
    echo "DRY-RUN: not cancelling. Re-run without --dry-run to apply."
    exit 0
fi

# Apply cancellations and write help-needed notification
NOW_UTC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
NOTE_FILE="${HELP_NEEDED_DIR}/head-1.2-su-budget-auto-cancel-${NOW_UTC//:/-}.md"
mkdir -p "$HELP_NEEDED_DIR"

{
    echo "---"
    echo "author: prio_su_enforce.sh (auto-generated)"
    echo "date: ${NOW_UTC}"
    echo "urgency: critical"
    echo "affected_tracks: [alpha-m, infrastructure]"
    echo "---"
    echo ""
    echo "# Auto-cancellation: priority SU projected over budget"
    echo ""
    echo "The prio_su_enforce.sh script cancelled the following job(s) because their"
    echo "remaining walltime would push priority SU consumption past the cap."
    echo ""
    echo "## Budget state at cancellation"
    echo ""
    echo "| Field | Value |"
    echo "|-------|-------|"
    echo "| Budget cap | ${BUDGET_SU} SU |"
    echo "| Used (terminated) | ${USED_SU} SU |"
    echo "| In-flight projected (pre-cancel) | ${INFLIGHT_PROJECTED} SU |"
    echo "| Projected total (pre-cancel) | ${PROJECTED_TOTAL} SU |"
    echo "| Excess to remove | ${EXCESS} SU |"
    echo ""
    echo "## Cancelled jobs"
    echo ""
    echo "| JobID | Name | State | Walltime | Elapsed | Projected SU saved |"
    echo "|-------|------|-------|----------|---------|---------------------|"
} > "$NOTE_FILE"

CANCEL_RC=0
for entry in "${CANCEL_LIST[@]}"; do
    jobid="${entry%%:*}"
    proj_su="${entry##*:}"
    detail="${INFLIGHT_DETAILS[$jobid]}"
    name=$(echo "$detail" | cut -d'|' -f1)
    state=$(echo "$detail" | cut -d'|' -f2)
    timelimit=$(echo "$detail" | cut -d'|' -f4)
    elapsed=$(echo "$detail" | cut -d'|' -f5)
    if scancel "$jobid" 2>/dev/null; then
        echo "  scancel $jobid OK"
        echo "| $jobid | $name | $state | $timelimit | $elapsed | $proj_su |" >> "$NOTE_FILE"
    else
        echo "  scancel $jobid FAILED"
        echo "| $jobid | $name | $state | $timelimit | $elapsed | $proj_su (CANCEL FAILED) |" >> "$NOTE_FILE"
        CANCEL_RC=2
    fi
done

cat >> "$NOTE_FILE" <<'EOF'

## Recommended head-1.2 action

These job(s) were cancelled to honor the priority SU budget cap. To preserve
the scientific work without compromise, **resubmit them on Standard Tier**
(`gpu` partition, account=`pi_mg269`). Standard Tier is free but fair-share-gated
(currently ~0.0146 — slow dispatch). Acceptable per Sub 1.2 closure window.

Other options (require explicit user authorization):
1. Raise the priority budget cap in `prio_su_budget.json:budget_su`.
2. Reduce the SLURM walltime so projected fits within budget (still on priority).
3. Defer the work to Sub 1.3.

This note was auto-generated. head-1.2 should triage at next check-in and
resubmit cancelled work on Standard Tier per the no-compromise directive.
EOF

echo ""
echo "Wrote help-needed notification: $NOTE_FILE"
echo "Cancelled ${#CANCEL_LIST[@]} job(s). Exit code 1."
exit ${CANCEL_RC:-1}
