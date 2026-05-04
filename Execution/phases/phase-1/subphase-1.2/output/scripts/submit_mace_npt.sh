#!/bin/bash
# =============================================================================
# submit_mace_npt.sh -- SLURM wrapper for MACE-OFF24 hybrid NPT production
# (Sub 1.2 task-001, Option 5: H200 OpenCL path)
#
# Usage:
#   ./submit_mace_npt.sh <protein> <cryptic_tag>
#
# Examples:
#   ./submit_mace_npt.sh ww m4k2pz9q
#   ./submit_mace_npt.sh gb3 n7r9tx4w
#   ./submit_mace_npt.sh ubq q3j8vb6p
#
# Resubmission: submit again with the SAME cryptic tag. The Python script
# detects the existing checkpoint at
#   /nfs/roberts/scratch/pi_mg269/rag88/alpha-m/mace-npt/<tag>/checkpoint_latest.chk
# and resumes production from it. Exit codes:
#   0 -- trajectory reached target 5 ns
#   2 -- walltime guard fired, resubmit to continue
#   1 -- fatal error (NaN, OOM, hang escalated to exception)
# =============================================================================

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <ww|gb3|ubq> <cryptic-8char-tag>" >&2
    exit 2
fi

PROTEIN=$1
TAG=$2

case "$PROTEIN" in
    ww)  RESRANGE=6-39 ;;
    gb3) RESRANGE="" ;;
    ubq) RESRANGE="" ;;
    *)
        echo "Unknown protein: $PROTEIN (expected ww|gb3|ubq)" >&2
        exit 2
        ;;
esac

# Paths -------------------------------------------------------------------
SUBPHASE_DIR=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2
SCRIPT_PY=${SUBPHASE_DIR}/output/scripts/mace_hybrid_npt.py
OUTPUT_DIR=${SUBPHASE_DIR}/output/trajectories/mace_npt
SCRATCH_DIR=/nfs/roberts/scratch/pi_mg269/rag88/alpha-m/mace-npt
SLURM_LOG_DIR=${SUBPHASE_DIR}/output/slurm_logs

mkdir -p "$OUTPUT_DIR" "$SCRATCH_DIR/$TAG" "$SLURM_LOG_DIR"

PDB_PATH=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/${PROTEIN}.pdb

# Submit ------------------------------------------------------------------
# H200 OpenCL is the Phase 2 MACE primary path per
#   shared/help-needed/sub-1.2-phase2-mlff-scope.md (Option 5).
# Partition gpu_h200, 300 SU/hr; 23:59:00 walltime (max for this partition).
# Python walltime guard fires at 22.5 hr (81000 s) to save checkpoint cleanly.

sbatch \
    --job-name="${TAG}" \
    --partition=gpu_h200 \
    --gres=gpu:h200:1 \
    --time=23:59:00 \
    --cpus-per-task=4 \
    --mem=32G \
    --account=pi_mg269 \
    --output="${SLURM_LOG_DIR}/mace_npt_${PROTEIN}_${TAG}_%j.out" \
    --error="${SLURM_LOG_DIR}/mace_npt_${PROTEIN}_${TAG}_%j.err" \
    --export=ALL,MACE_HYBRID_PROTEIN="$PROTEIN",MACE_HYBRID_PDB="$PDB_PATH",MACE_HYBRID_RESRANGE="$RESRANGE",MACE_HYBRID_TARGET_NS=5.0,MACE_HYBRID_BAROSTAT=npt,MACE_HYBRID_TAG="$TAG",MACE_OUTPUT_DIR="$OUTPUT_DIR",MACE_SCRATCH_DIR="$SCRATCH_DIR",MACE_HYBRID_WALLTIME_GUARD_SEC=81000 \
    --wrap="\
set -uo pipefail
echo '=========================================='
echo \"MACE hybrid NPT  |  SLURM \$SLURM_JOB_ID\"
echo \"Node: \$(hostname)\"
echo \"GPU: \$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo unknown)\"
echo \"Date: \$(date -u '+%Y-%m-%dT%H:%M:%SZ')\"
echo \"Protein: $PROTEIN  Tag: $TAG\"
echo '=========================================='
source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-mace
export PYTHONNOUSERSITE=1
# Ensure conda's libstdc++ (has CXXABI_1.3.15) loads before system's GCC 12.2
export LD_LIBRARY_PATH=\"\${CONDA_PREFIX}/lib:\${LD_LIBRARY_PATH:-}\"

# External-process GPU keepalive (2026-04-20 patch per user directive): MACE's
# matscipy.neighbour_list holds Python GIL during long calls, so the in-Python
# keepalive thread cannot run → YCRC auto-cancels at 2h 0% GPU. Spawn separate
# process so keepalive survives GIL-blocked periods. Precedent: 8939395 (WW v9)
# + 8939396 (GB3 v9) + 8939397 (UBQ v9) were all cancelled by YCRC despite
# in-Python keepalive. External-process fix tested in bioemu_batch2.sbatch.
KEEPALIVE_SCRIPT='/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/gpu_keepalive.py'
python \"\${KEEPALIVE_SCRIPT}\" > \"${SLURM_LOG_DIR}/keepalive-mace-\${SLURM_JOB_ID}.log\" 2>&1 &
KEEPALIVE_PID=\$!
echo \"GPU keepalive (external process) spawned PID \${KEEPALIVE_PID}\"

# Kill helpers on exit
trap 'kill \${KEEPALIVE_PID} 2>/dev/null || true' EXIT

# Auto-restart loop with integrated hang watchdog.
# matscipy hangs sporadically (~15-30K steps). Instead of scancel (kills whole
# job), the watchdog kills just the Python process; the loop restarts it from
# the last checkpoint. Runs until target (exit 0), fatal (exit 1), or walltime (exit 2).
MAX_RESTARTS=200
RESTART_COUNT=0
HANG_TIMEOUT=1200  # 20 min

while [ \$RESTART_COUNT -lt \$MAX_RESTARTS ]; do
    echo \"--- Run \$((RESTART_COUNT+1)) of \$MAX_RESTARTS (\$(date -u '+%H:%M:%SZ')) ---\"

    # Launch Python in background so we can monitor + kill it
    /home/rag88/.conda/envs/env-mace/bin/python $SCRIPT_PY &
    PY_PID=\$!

    # Inline watchdog: monitor stdout mtime, kill PY_PID on stall
    OUT_LOG=\"${SLURM_LOG_DIR}/mace_npt_${PROTEIN}_${TAG}_\${SLURM_JOB_ID}.out\"
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
"
