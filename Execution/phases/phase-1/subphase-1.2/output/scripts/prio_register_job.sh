#!/bin/bash
# === Register a priority-tier SLURM job in prio_su_registry.json ===
# Used by production submitters (submit_mace_npt_prod.sh,
# submit_so3lr_rescue_production.sh) to make the tracker visible to jobs
# that don't follow the q6XXXXXX naming scheme.
#
# Usage: prio_register_job.sh <job_id> <job_name> <walltime_sec> <purpose> [billing_rate]
#
# billing_rate defaults to 15 (RTX 5000 Ada). H200 = 300, B200 = 370.
# Max SU estimate = billing_rate * walltime_sec / 3600.

set -euo pipefail

if [[ $# -lt 4 ]]; then
    echo "Usage: $0 <job_id> <job_name> <walltime_sec> <purpose> [billing_rate=15]" >&2
    exit 2
fi

JOB_ID="$1"
JOB_NAME="$2"
WALLTIME_SEC="$3"
PURPOSE="$4"
BILLING_RATE="${5:-15}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY_FILE="${SCRIPT_DIR}/prio_su_registry.json"

if [[ ! -f "$REGISTRY_FILE" ]]; then
    echo '{"jobs": []}' > "$REGISTRY_FILE"
fi

NOW_UTC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
MAX_SU=$(echo "scale=2; ${BILLING_RATE} * ${WALLTIME_SEC} / 3600" | bc)

TMPFILE=$(mktemp)
jq --arg jid "$JOB_ID" \
   --arg jname "$JOB_NAME" \
   --arg ts "$NOW_UTC" \
   --arg purpose "$PURPOSE" \
   --arg max_su "$MAX_SU" \
   --arg bill "$BILLING_RATE" \
   '.jobs += [{
     "job_id": $jid,
     "job_name": $jname,
     "submit_time": $ts,
     "purpose": $purpose,
     "status": "SUBMITTED",
     "actual_su": 0,
     "notes": ("Max SU at billing=" + $bill + ": " + $max_su)
   }]' "$REGISTRY_FILE" > "$TMPFILE" && mv "$TMPFILE" "$REGISTRY_FILE"

echo "Registered job ${JOB_ID} (${JOB_NAME}) max SU=${MAX_SU} in prio_su_registry.json"
