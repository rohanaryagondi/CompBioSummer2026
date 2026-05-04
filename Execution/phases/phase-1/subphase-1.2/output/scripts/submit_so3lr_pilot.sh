#!/bin/bash
# Submit SO3LR pilot runs for all 5 Tier A/B proteins (or a subset).
#
# Usage:
#   ./submit_so3lr_pilot.sh               # submit all 5 (ww, gb3, gb1, ntl9, ubq)
#   ./submit_so3lr_pilot.sh ww gb3        # submit only the named proteins
#   ./submit_so3lr_pilot.sh --mode restart ww   # restart protein
#
# Per shared/notes/operational-practices.md:
#   - Each submission gets an opaque 8-char alphanumeric job name.

set -euo pipefail

REPO_ROOT="/home/rag88/projects/CompBioSummer2026"
SUBPHASE_ROOT="${REPO_ROOT}/Execution/phases/phase-1/subphase-1.2"
SBATCH="${SUBPHASE_ROOT}/output/scripts/so3lr_pilot.sbatch"
JOB_LOG="${SUBPHASE_ROOT}/output/trajectories/so3lr_vacuum/submitted_jobs.tsv"

# Default arguments
MODE="run"
TARGET_NS="5.0"
declare -a PROTEINS=()

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="$2"; shift 2 ;;
    --target-ns) TARGET_NS="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 [--mode run|restart] [--target-ns 5.0] [ww gb3 gb1 ntl9 ubq]"
      exit 0 ;;
    *)
      PROTEINS+=("$1"); shift ;;
  esac
done

if [[ ${#PROTEINS[@]} -eq 0 ]]; then
  PROTEINS=(ww gb3 gb1 ntl9 ubq)
fi

# Pre-determined cryptic 8-char alphanumeric job names (one per protein).
# Generated 2026-04-19 with: tr -dc 'a-z0-9' </dev/urandom | head -c 8
# Resubmission 2026-04-19 (typing_extensions env regression fix, v2 names):
declare -A CRYPTIC_NAMES=(
  [ww]="h6k3vr9m"
  [gb3]="pr32hg7t"
  [gb1]="ixgkbzna"
  [ntl9]="ubi1w71f"
  [ubq]="g6m5vkof"
)
# ww tag history:
#   h6k3vr9m — v3 fresh 2026-04-19T16:06Z after v2 NODE_FAIL + 5.5h hang at step 498K (0.25 ns)
#   932e3sz8 — v2 NODE_FAIL at 07:59:35Z (artifacts archived as *.hang); also cancelled reuse attempt 8903309
#   p3v8xt7r — v1 FAILED typing_extensions env-var bug
# Previous (FAILED, env-so3lr missing typing_extensions under PYTHONNOUSERSITE=1):
#   ww=p3v8xt7r(8886091) gb3=k9m2qw5n(8886092) gb1=j7r4nb6x(8886093)
#   ntl9=z5k8fp2q(8886094) ubq=h4w9rn3m(8886095)

mkdir -p "$(dirname "${JOB_LOG}")"
# Header once
if [[ ! -f "${JOB_LOG}" ]]; then
  echo -e "timestamp\tprotein\tjob_id\tjob_name\tmode\ttarget_ns" > "${JOB_LOG}"
fi

for p in "${PROTEINS[@]}"; do
  name="${CRYPTIC_NAMES[$p]:-}"
  if [[ -z "$name" ]]; then
    echo "ERROR: no cryptic name for protein '$p'. Update CRYPTIC_NAMES map." >&2
    exit 2
  fi

  echo "Submitting SO3LR ${MODE} for ${p} (target ${TARGET_NS} ns, job-name ${name})"
  job_id=$(
    sbatch \
      --parsable \
      --job-name="${name}" \
      --export="PROTEIN=${p},MODE=${MODE},TARGET_NS=${TARGET_NS}" \
      "${SBATCH}"
  )
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo -e "${ts}\t${p}\t${job_id}\t${name}\t${MODE}\t${TARGET_NS}" >> "${JOB_LOG}"
  echo "  → job ${job_id} (${name}) submitted"
done

echo ""
echo "All submissions recorded to: ${JOB_LOG}"
tail -n +1 "${JOB_LOG}"
