#!/bin/bash
###############################################################################
# Submit 5 ns SO3LR full-rescue jobs to Standard Tier (preferred) for
# proteins that PASSED their 500 ps gate.
#
# Per the rescue plan:
#   - Standard Tier (`gpu` partition, account=pi_mg269) is free but fair-share
#     is 0.0146 (deeply depleted) — long queue wait possible.
#   - If a 5 ns rescue is critical and Standard blocks past 2026-05-08,
#     escalate to head-1.2 for priority Tier authorization.
#
# Usage:
#   ./submit_so3lr_rescue_production.sh ww gb3 ntl9       # all 3 (only those that PASSED gates)
#   ./submit_so3lr_rescue_production.sh --priority gb3    # use priority_gpu for gb3
#
# Reuses the gate-tested parameter sets (per-protein) from the rescue plan:
#   WW:   float64, dt=0.25 fs, NHC chain=5, NHC thermo=200
#   GB3:  neutral XYZ, float32, dt=0.5 fs, NHC chain=3, NHC thermo=100 (default)
#   NTL9: neutral XYZ, float32, dt=0.5 fs, NHC chain=3, NHC thermo=100 (default)
###############################################################################

set -euo pipefail

USE_PRIORITY=0
USE_SCAVENGE=0
if [ "${1:-}" = "--priority" ]; then
    USE_PRIORITY=1
    shift
elif [ "${1:-}" = "--scavenge" ]; then
    USE_SCAVENGE=1
    shift
fi

REPO_ROOT="/home/rag88/projects/CompBioSummer2026"
SUBPHASE_ROOT="${REPO_ROOT}/Execution/phases/phase-1/subphase-1.2"
SBATCH="${SUBPHASE_ROOT}/output/scripts/so3lr_rescue.sbatch"
NEUTRAL_DIR="${SUBPHASE_ROOT}/output/trajectories/so3lr_vacuum_neutral"
PROD_DIR="${SUBPHASE_ROOT}/output/trajectories/so3lr_vacuum_rescue_prod"
SUBMIT_LOG="${PROD_DIR}/submitted_production.tsv"

mkdir -p "${PROD_DIR}/ww" "${PROD_DIR}/gb3" "${PROD_DIR}/ntl9"

declare -A CRYPTIC_PROD=( \
    [ww]="w8q4r3xz" \
    [gb3]="g7p4tv8m" \
    [ntl9]="n5h6kx9q" \
)

if [ ! -f "${SUBMIT_LOG}" ]; then
    echo -e "timestamp\tprotein\tjob_id\tjob_name\tprecision\tdt_fs\tnhc_chain\tnhc_thermo\ttarget_ns\tinput_xyz\tpartition\taccount" > "${SUBMIT_LOG}"
fi

if [ ${USE_PRIORITY} -eq 1 ]; then
    PARTITION="priority_gpu"
    ACCOUNT="prio_mg269"
    GPU_FLAG="--gpus=rtx_5000_ada:1"
    TIME_LIMIT="1-00:00:00"   # priority cap is typically 1d
elif [ ${USE_SCAVENGE} -eq 1 ]; then
    PARTITION="scavenge_gpu"
    ACCOUNT="pi_mg269"
    GPU_FLAG="--gres=gpu:1"   # any GPU; SO3LR is small VRAM
    TIME_LIMIT="1-00:00:00"   # scavenge MaxWall cap; preemptible (REQUEUE)
else
    PARTITION="gpu"
    ACCOUNT="pi_mg269"
    GPU_FLAG="--gres=gpu:1"
    TIME_LIMIT="1-00:00:00"
fi

echo "Production submission settings: partition=${PARTITION}, account=${ACCOUNT}, time=${TIME_LIMIT}"

# === Priority SU budget pre-check (head-1.2 closure infrastructure) ====
# Only enforces for priority_gpu submissions (account=prio_mg269). Standard
# Tier (gpu on pi_mg269) is free and not gated.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$PARTITION" == "priority_gpu" ]]; then
    TRACKER="${SCRIPT_DIR}/prio_su_tracker.sh"
    if [[ -x "$TRACKER" ]]; then
        echo ""
        echo "=== Priority SU budget pre-check ==="
        TRACKER_EXIT=0
        bash "$TRACKER" || TRACKER_EXIT=$?
        if [[ $TRACKER_EXIT -eq 2 ]]; then
            echo "" >&2
            echo "BLOCKED: priority SU budget exhausted. NOT submitting." >&2
            echo "Either raise budget_su in prio_su_budget.json or wait for jobs to terminate." >&2
            exit 2
        elif [[ $TRACKER_EXIT -eq 1 ]]; then
            echo ""
            echo "WARNING: priority SU >80% of budget. Press Ctrl-C within 5s to abort..."
            sleep 5
        fi
        echo "Budget OK — proceeding with submission."
        echo ""
    else
        echo "WARNING: prio_su_tracker.sh not found at $TRACKER; skipping budget check." >&2
    fi
fi

submit_one() {
    local PROTEIN="$1"
    local DT_FS="$2"
    local PRECISION="$3"
    local NHC_CHAIN="$4"
    local NHC_THERMO="$5"
    local INPUT_XYZ="$6"

    if [ ! -f "${INPUT_XYZ}" ]; then
        echo "ERROR: input XYZ not found for ${PROTEIN}: ${INPUT_XYZ}"
        return 1
    fi

    JID=$(sbatch \
        --partition="${PARTITION}" \
        --account="${ACCOUNT}" \
        ${GPU_FLAG} \
        --time="${TIME_LIMIT}" \
        --job-name="${CRYPTIC_PROD[$PROTEIN]}" \
        --export=PROTEIN=${PROTEIN},MODE=run,TARGET_NS=5.0,DT_FS=${DT_FS},PRECISION=${PRECISION},NHC_CHAIN=${NHC_CHAIN},NHC_THERMO=${NHC_THERMO},INPUT_XYZ="${INPUT_XYZ}",OUTPUT_SUBDIR=so3lr_vacuum_rescue_prod \
        "${SBATCH}" | awk '{print $4}')
    TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    echo -e "${TS}\t${PROTEIN}\t${JID}\t${CRYPTIC_PROD[$PROTEIN]}\t${PRECISION}\t${DT_FS}\t${NHC_CHAIN}\t${NHC_THERMO}\t5.0\t${INPUT_XYZ}\t${PARTITION}\t${ACCOUNT}" >> "${SUBMIT_LOG}"
    echo "  ${PROTEIN} → job ${JID} (${CRYPTIC_PROD[$PROTEIN]})  partition=${PARTITION}"

    # Auto-register priority-tier submissions in the SU tracker registry.
    if [[ "${PARTITION}" == "priority_gpu" ]] && [[ -n "${JID}" ]] \
       && [[ -x "${SCRIPT_DIR}/prio_register_job.sh" ]]; then
        # Convert TIME_LIMIT (D-HH:MM:SS or HH:MM:SS) → seconds
        if [[ "${TIME_LIMIT}" =~ ^([0-9]+)-([0-9]+):([0-9]+):([0-9]+)$ ]]; then
            WT_SEC=$(( BASH_REMATCH[1]*86400 + BASH_REMATCH[2]*3600 + BASH_REMATCH[3]*60 + BASH_REMATCH[4] ))
        elif [[ "${TIME_LIMIT}" =~ ^([0-9]+):([0-9]+):([0-9]+)$ ]]; then
            WT_SEC=$(( BASH_REMATCH[1]*3600 + BASH_REMATCH[2]*60 + BASH_REMATCH[3] ))
        else
            WT_SEC=86400  # fallback 24h
        fi
        bash "${SCRIPT_DIR}/prio_register_job.sh" \
            "${JID}" "${CRYPTIC_PROD[$PROTEIN]}" "${WT_SEC}" \
            "SO3LR rescue prod ${PROTEIN} 5ns prec=${PRECISION} dt=${DT_FS}fs chain=${NHC_CHAIN}" \
            "15" || true
    fi
}

for PROTEIN in "$@"; do
    case "${PROTEIN}" in
        ww)
            WW_V1_XYZ="${SUBPHASE_ROOT}/output/trajectories/so3lr_vacuum/ww/input.xyz"
            submit_one ww 0.25 float64 5 200.0 "${WW_V1_XYZ}"
            ;;
        gb3)
            submit_one gb3 0.5 float32 3 100.0 "${NEUTRAL_DIR}/gb3/input_neutral.xyz"
            ;;
        ntl9)
            submit_one ntl9 0.5 float32 3 100.0 "${NEUTRAL_DIR}/ntl9/input_neutral.xyz"
            ;;
        *)
            echo "Unknown protein: ${PROTEIN} (must be ww, gb3, or ntl9)"
            exit 1
            ;;
    esac
done

echo ""
echo "Submission log: ${SUBMIT_LOG}"
