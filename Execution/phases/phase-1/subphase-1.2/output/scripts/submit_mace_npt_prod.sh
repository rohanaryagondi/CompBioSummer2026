#!/bin/bash
# =============================================================================
# submit_mace_npt_prod.sh -- SLURM wrapper for MACE-OFF24 hybrid NPT production
# (Sub 1.2 task-001, Round 3 recipe = sentinel-bond + HBonds + dt=1 fs + MCB freq=25).
#
# Usage:
#   ./submit_mace_npt_prod.sh <protein> <cryptic_tag> [partition] [target_ns] [walltime]
#
# Arguments:
#   protein       ww | gb3 | ubq | ntl9
#   cryptic_tag   8-char alphanumeric
#   partition     gpu_h200 (production, default) | priority_gpu (probe) | scavenge_gpu (free-tier probe/prod)
#   target_ns     5.0 (default for prod) | 0.05 (probe)
#   walltime      23:59:00 (default for prod) | 1:30:00 / 2:00:00 / 5:55:00 (probe)
#
# Examples:
#   # Probes (priority queue, RTX 5000 Ada):
#   ./submit_mace_npt_prod.sh gb3 b8r3kt5x priority_gpu 0.05 1:30:00
#   ./submit_mace_npt_prod.sh ubq c4n7vp2j priority_gpu 0.05 2:00:00
#   # Probes (scavenge_gpu, free, h200):
#   ./submit_mace_npt_prod.sh ntl9 q6n9tlpb scavenge_gpu 0.05 5:55:00   # 2026-05-03 UBQ substitute
#   # Production (gpu_h200, OpenCL hybrid):
#   ./submit_mace_npt_prod.sh ww  d6h2qx9m gpu_h200 5.0 23:59:00
#   ./submit_mace_npt_prod.sh gb3 e7w3jr4n gpu_h200 5.0 23:59:00
#   ./submit_mace_npt_prod.sh ubq f9p8mc6k gpu_h200 5.0 23:59:00
#
# Resubmission: submit again with the SAME cryptic tag. The Python script
# detects the existing checkpoint at
#   /nfs/roberts/scratch/pi_mg269/rag88/alpha-m/mace-npt-prod/<tag>/checkpoint_latest.chk
# and resumes production from it. Inner-loop exit codes:
#   0 -- target reached
#   2 -- walltime guard fired (resubmit SLURM job to continue)
#   1 -- fatal error
#
# Inner loop also auto-restarts the Python process up to MAX_RESTARTS=20 if
# it dies (hang watchdog or transient failure) -- script reports the FINAL
# exit code from sbatch.
# =============================================================================

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <ww|gb3|ubq|ubq_alt|ntl9> <cryptic-8char-tag> [partition] [target_ns] [walltime]" >&2
    exit 2
fi

PROTEIN=$1
TAG=$2
PARTITION=${3:-gpu_h200}
TARGET_NS=${4:-5.0}
WALLTIME=${5:-23:59:00}

case "$PROTEIN" in
    ww)      RESRANGE=6-39 ;;
    gb3)     RESRANGE="" ;;
    ubq)     RESRANGE="" ;;
    ubq_alt) RESRANGE="" ;;  # 2026-05-03 option-(d) UBQ alt start (1XQQ NMR model 1, NaN-asymptote test)
    ntl9)    RESRANGE="" ;;  # 2026-05-03 option-(c) UBQ substitute (Tier B, 51 aa, 390 protein atoms)
    *)
        echo "Unknown protein: $PROTEIN (expected ww|gb3|ubq|ubq_alt|ntl9)" >&2
        exit 2
        ;;
esac

# Map partition to SLURM account / qos / gres
case "$PARTITION" in
    gpu_h200)
        ACCOUNT=pi_mg269
        QOS=normal
        GRES=gpu:h200:1
        ;;
    priority_gpu)
        ACCOUNT=prio_mg269
        QOS=prio_mg269
        GRES=gpu:rtx_5000_ada:1
        ;;
    gpu)
        ACCOUNT=pi_mg269
        QOS=normal
        GRES=gpu:rtx_5000_ada:1
        ;;
    gpu_devel)
        ACCOUNT=pi_mg269
        QOS=normal
        GRES=gpu:rtx_5000_ada:1
        ;;
    scavenge_gpu)
        ACCOUNT=pi_mg269
        QOS=normal
        GRES=gpu:h200:1
        ;;
    *)
        echo "Unknown partition: $PARTITION" >&2
        exit 2
        ;;
esac

# === Priority SU budget pre-check (head-1.2 closure infrastructure) ====
# Only enforces for priority_gpu submissions (account=prio_mg269). Standard
# Tier (gpu, gpu_h200, gpu_devel on pi_mg269) is free and not gated.
SUBMIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$PARTITION" == "priority_gpu" ]]; then
    TRACKER="${SUBMIT_DIR}/prio_su_tracker.sh"
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

# Paths -------------------------------------------------------------------
SUBPHASE_DIR=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2
SCRIPT_PY=${SUBPHASE_DIR}/output/scripts/mace_hybrid_npt_prod.py
OUTPUT_DIR=${SUBPHASE_DIR}/output/trajectories/mace_npt_prod
SCRATCH_DIR=/nfs/roberts/scratch/pi_mg269/rag88/alpha-m/mace-npt-prod
SLURM_LOG_DIR=${SUBPHASE_DIR}/output/slurm_logs

mkdir -p "$OUTPUT_DIR" "$SCRATCH_DIR/$TAG" "$SLURM_LOG_DIR"

PDB_PATH=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/${PROTEIN}.pdb

# Walltime guard: 90% of SLURM walltime in seconds (saves checkpoint cleanly)
WT_HOURS=$(echo "$WALLTIME" | cut -d: -f1)
WT_MINS=$(echo "$WALLTIME" | cut -d: -f2)
WT_SECS=$(echo "$WALLTIME" | cut -d: -f3)
WT_TOTAL_SEC=$(( WT_HOURS * 3600 + WT_MINS * 60 + WT_SECS ))
GUARD_SEC=$(( WT_TOTAL_SEC * 90 / 100 ))

echo "Submitting MACE NPT prod: protein=$PROTEIN tag=$TAG partition=$PARTITION account=$ACCOUNT"
echo "  walltime=$WALLTIME (${WT_TOTAL_SEC}s); guard=${GUARD_SEC}s; target_ns=$TARGET_NS"

SBATCH_OUTPUT_FILE=$(mktemp)
trap 'rm -f "$SBATCH_OUTPUT_FILE"' EXIT

sbatch \
    --job-name="${TAG}" \
    --partition="${PARTITION}" \
    --account="${ACCOUNT}" \
    --qos="${QOS}" \
    --gres="${GRES}" \
    --time="${WALLTIME}" \
    --requeue \
    --cpus-per-task=4 \
    --mem=32G \
    --output="${SLURM_LOG_DIR}/mace_npt_prod_${PROTEIN}_${TAG}_%j.out" \
    --error="${SLURM_LOG_DIR}/mace_npt_prod_${PROTEIN}_${TAG}_%j.err" \
    --export=ALL,MACE_HYBRID_PROTEIN="$PROTEIN",MACE_HYBRID_PDB="$PDB_PATH",MACE_HYBRID_RESRANGE="$RESRANGE",MACE_HYBRID_TARGET_NS="$TARGET_NS",MACE_HYBRID_TAG="$TAG",MACE_OUTPUT_DIR="$OUTPUT_DIR",MACE_SCRATCH_DIR="$SCRATCH_DIR",MACE_HYBRID_WALLTIME_GUARD_SEC="$GUARD_SEC",MACE_HYBRID_DT_FS="${MACE_HYBRID_DT_FS:-1.0}" \
    --wrap="\
set -uo pipefail
echo '=========================================='
echo \"MACE hybrid NPT PROD  |  SLURM \$SLURM_JOB_ID  |  recipe=Round3\"
echo \"Node: \$(hostname)\"
echo \"GPU: \$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo unknown)\"
echo \"Date: \$(date -u '+%Y-%m-%dT%H:%M:%SZ')\"
echo \"Protein: $PROTEIN  Tag: $TAG  Partition: $PARTITION  Target: ${TARGET_NS} ns  Walltime: $WALLTIME  Guard: ${GUARD_SEC}s\"
echo '=========================================='
source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-mace
export PYTHONNOUSERSITE=1
export LD_LIBRARY_PATH=\"\${CONDA_PREFIX}/lib:\${LD_LIBRARY_PATH:-}\"

# Thread limits matched to --cpus-per-task=4: prevents OpenMM/MACE from
# over-subscribing host threads (default unbounded BLAS may contend with
# vesin/MACE neighbor list). Per optimization-hunter C5.
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=4

# NUMA-aware GPU/CPU binding (deeper-opt-hunter A2): avoids cross-socket
# latency for vesin neighbor list ↔ GPU PCIe transfers. SLURM honors this
# per-allocation when set; falls through silently if not.
export OMP_PROC_BIND=close
export OMP_PLACES=cores

# External-process GPU keepalive (2026-04-20 patch): MACE force callbacks can
# hold GIL during long calls, so the in-Python keepalive thread cannot run.
# Spawn separate process so keepalive survives GIL-blocked periods.
KEEPALIVE_SCRIPT='/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/gpu_keepalive.py'
python \"\${KEEPALIVE_SCRIPT}\" > \"${SLURM_LOG_DIR}/keepalive-mace-prod-\${SLURM_JOB_ID}.log\" 2>&1 &
KEEPALIVE_PID=\$!
echo \"GPU keepalive (external process) spawned PID \${KEEPALIVE_PID}\"

# Kill helpers on exit
trap 'kill \${KEEPALIVE_PID} 2>/dev/null || true' EXIT

# Auto-restart loop with hang watchdog
MAX_RESTARTS=20
RESTART_COUNT=0
HANG_TIMEOUT=1200  # 20 min

while [ \$RESTART_COUNT -lt \$MAX_RESTARTS ]; do
    echo \"--- Run \$((RESTART_COUNT+1)) of \$MAX_RESTARTS (\$(date -u '+%H:%M:%SZ')) ---\"

    /home/rag88/.conda/envs/env-mace/bin/python $SCRIPT_PY &
    PY_PID=\$!

    OUT_LOG=\"${SLURM_LOG_DIR}/mace_npt_prod_${PROTEIN}_${TAG}_\${SLURM_JOB_ID}.out\"
    stall_sec=0
    last_mtime=0
    HUNG=0
    while kill -0 \$PY_PID 2>/dev/null; do
        sleep 60
        if [ -f \"\${OUT_LOG}\" ]; then
            current_mtime=\$(stat -c %Y \"\${OUT_LOG}\" 2>/dev/null || echo 0)
            if [ \"\${current_mtime}\" = \"\${last_mtime}\" ]; then
                stall_sec=\$((stall_sec + 60))
            else
                stall_sec=0
                last_mtime=\${current_mtime}
            fi
            if [ \"\${stall_sec}\" -ge \${HANG_TIMEOUT} ]; then
                echo \"[watchdog \$(date -u '+%H:%M:%SZ')] HANG: no writes for \${stall_sec}s. Killing Python PID \${PY_PID}.\"
                kill \${PY_PID} 2>/dev/null || true
                sleep 2
                kill -9 \${PY_PID} 2>/dev/null || true
                HUNG=1
                break
            fi
        fi
    done

    wait \${PY_PID} 2>/dev/null
    EXIT_CODE=\$?

    if [ \$EXIT_CODE -eq 0 ]; then
        echo \"TARGET REACHED — done\"
        break
    elif [ \$EXIT_CODE -eq 1 ] && [ \$HUNG -eq 0 ]; then
        echo \"FATAL ERROR — check logs\"
        break
    elif [ \$EXIT_CODE -eq 2 ]; then
        echo \"WALLTIME GUARD — resubmit SLURM job to continue\"
        break
    else
        RESTART_COUNT=\$((RESTART_COUNT+1))
        echo \"Restart \$RESTART_COUNT/\$MAX_RESTARTS (hung=\$HUNG exit=\$EXIT_CODE). Resuming from checkpoint in 5s...\"
        stall_sec=0
        last_mtime=0
        HUNG=0
        sleep 5
    fi
done

kill \${KEEPALIVE_PID} 2>/dev/null || true
echo \"Final exit: \$EXIT_CODE after \$RESTART_COUNT restarts\"
exit \$EXIT_CODE
" | tee "$SBATCH_OUTPUT_FILE"

# === Auto-register priority submissions in tracker registry ===
if [[ "$PARTITION" == "priority_gpu" ]]; then
    JID=$(awk '/Submitted batch job/{print $4; exit}' "$SBATCH_OUTPUT_FILE")
    if [[ -n "$JID" ]] && [[ -x "${SUBMIT_DIR}/prio_register_job.sh" ]]; then
        BILL_RATE=15  # RTX 5000 Ada on priority_gpu
        bash "${SUBMIT_DIR}/prio_register_job.sh" \
            "$JID" "$TAG" "$WT_TOTAL_SEC" \
            "MACE NPT prod ${PROTEIN} target=${TARGET_NS}ns" "$BILL_RATE" || true
    fi
fi
