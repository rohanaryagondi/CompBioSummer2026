#!/bin/bash
###############################################################################
# Submit 3 SO3LR rescue gate jobs (500 ps each) on priority_gpu / RTX 5000 Ada.
#
# Per the rescue plan (output/so3lr_rescue_plan.md):
#   WW   gate: float64, dt=0.25 fs, NHC chain=5, target 0.5 ns
#   GB3  gate: neutral XYZ, float32, dt=0.5 fs (default), target 0.5 ns
#   NTL9 gate: neutral XYZ, float32, dt=0.5 fs (default), target 0.5 ns
#
# Estimated cost: ~9 + 5 + 5 = ~19 priority SU. Well under 25 SU envelope.
###############################################################################

set -euo pipefail

REPO_ROOT="/home/rag88/projects/CompBioSummer2026"
SUBPHASE_ROOT="${REPO_ROOT}/Execution/phases/phase-1/subphase-1.2"
SBATCH="${SUBPHASE_ROOT}/output/scripts/so3lr_rescue.sbatch"
NEUTRAL_DIR="${SUBPHASE_ROOT}/output/trajectories/so3lr_vacuum_neutral"
RESCUE_DIR="${SUBPHASE_ROOT}/output/trajectories/so3lr_vacuum_rescue"
SUBMIT_LOG="${RESCUE_DIR}/submitted_gates.tsv"

mkdir -p "${RESCUE_DIR}/ww" "${RESCUE_DIR}/gb3" "${RESCUE_DIR}/ntl9"

# Cryptic 8-char alphanumeric job names per operational-practices.md.
# Different from any prior task-002 names (audit-trail integrity).
declare -A CRYPTIC=( \
    [ww]="r4w7q8nx" \
    [gb3]="g3b6kt2p" \
    [ntl9]="n9t4mv5h" \
)

# For GB3 / NTL9, use the neutral-protonation XYZ produced by
# so3lr_prep_proteins_neutral.py. For WW, use the v1 XYZ (chemistry already
# fine; only numerical fix needed).
WW_INPUT_XYZ=""   # default → v1 pilot input.xyz
GB3_INPUT_XYZ="${NEUTRAL_DIR}/gb3/input_neutral.xyz"
NTL9_INPUT_XYZ="${NEUTRAL_DIR}/ntl9/input_neutral.xyz"

if [ ! -f "${GB3_INPUT_XYZ}" ]; then
    echo "ERROR: GB3 neutral XYZ not found: ${GB3_INPUT_XYZ}"
    echo "  Run: python ${SUBPHASE_ROOT}/output/scripts/so3lr_prep_proteins_neutral.py \\"
    echo "         --proteins gb3 ntl9 --output-dir ${NEUTRAL_DIR}"
    exit 1
fi

if [ ! -f "${NTL9_INPUT_XYZ}" ]; then
    echo "ERROR: NTL9 neutral XYZ not found: ${NTL9_INPUT_XYZ}"
    exit 1
fi

# WW v1 input.xyz must already exist from task-002 v1
WW_V1_XYZ="${SUBPHASE_ROOT}/output/trajectories/so3lr_vacuum/ww/input.xyz"
if [ ! -f "${WW_V1_XYZ}" ]; then
    echo "ERROR: WW v1 input.xyz not found: ${WW_V1_XYZ}"
    exit 1
fi
# Stage it into the rescue dir so the runner can find it via default path
cp -n "${WW_V1_XYZ}" "${RESCUE_DIR}/ww/input.xyz" 2>/dev/null || true

# Header for submission log
{
    echo -e "timestamp\tprotein\tjob_id\tjob_name\tprecision\tdt_fs\tnhc_chain\tnhc_thermo\ttarget_ns\tinput_xyz"
} > "${SUBMIT_LOG}"

# priority_gpu requires --gpus= specification per node type; rtx_5000_ada is
# the SO3LR-target tier (15-equivalent SU; vacuum NVT fits in 32 GB).
GPU_FLAG="--gpus=rtx_5000_ada:1"

# Submit WW gate (float64, dt=0.25 fs, NHC chain=5, NHC thermo=200)
echo "Submitting WW gate (float64 + dt=0.25 fs + NHC chain=5)..."
JID_WW=$(sbatch \
    --partition=priority_gpu \
    --account=prio_mg269 \
    ${GPU_FLAG} \
    --time=03:00:00 \
    --job-name="${CRYPTIC[ww]}" \
    --export=PROTEIN=ww,MODE=run,TARGET_NS=0.5,DT_FS=0.25,PRECISION=float64,NHC_CHAIN=5,NHC_THERMO=200.0,INPUT_XYZ="${WW_V1_XYZ}",OUTPUT_SUBDIR=so3lr_vacuum_rescue \
    "${SBATCH}" | awk '{print $4}')
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo -e "${TS}\tww\t${JID_WW}\t${CRYPTIC[ww]}\tfloat64\t0.25\t5\t200.0\t0.5\t${WW_V1_XYZ}" >> "${SUBMIT_LOG}"
echo "  job ${JID_WW}, name ${CRYPTIC[ww]}, partition priority_gpu, time 03:00:00"

# Submit GB3 gate (neutral XYZ, float32, dt=0.5 fs default)
echo "Submitting GB3 gate (neutral protonation, float32 default)..."
JID_GB3=$(sbatch \
    --partition=priority_gpu \
    --account=prio_mg269 \
    ${GPU_FLAG} \
    --time=02:00:00 \
    --job-name="${CRYPTIC[gb3]}" \
    --export=PROTEIN=gb3,MODE=run,TARGET_NS=0.5,DT_FS=0.5,PRECISION=float32,NHC_CHAIN=3,NHC_THERMO=100.0,INPUT_XYZ="${GB3_INPUT_XYZ}",OUTPUT_SUBDIR=so3lr_vacuum_rescue \
    "${SBATCH}" | awk '{print $4}')
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo -e "${TS}\tgb3\t${JID_GB3}\t${CRYPTIC[gb3]}\tfloat32\t0.5\t3\t100.0\t0.5\t${GB3_INPUT_XYZ}" >> "${SUBMIT_LOG}"
echo "  job ${JID_GB3}, name ${CRYPTIC[gb3]}, partition priority_gpu, time 02:00:00"

# Submit NTL9 gate
echo "Submitting NTL9 gate (neutral protonation, float32 default)..."
JID_NTL9=$(sbatch \
    --partition=priority_gpu \
    --account=prio_mg269 \
    ${GPU_FLAG} \
    --time=02:00:00 \
    --job-name="${CRYPTIC[ntl9]}" \
    --export=PROTEIN=ntl9,MODE=run,TARGET_NS=0.5,DT_FS=0.5,PRECISION=float32,NHC_CHAIN=3,NHC_THERMO=100.0,INPUT_XYZ="${NTL9_INPUT_XYZ}",OUTPUT_SUBDIR=so3lr_vacuum_rescue \
    "${SBATCH}" | awk '{print $4}')
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo -e "${TS}\tntl9\t${JID_NTL9}\t${CRYPTIC[ntl9]}\tfloat32\t0.5\t3\t100.0\t0.5\t${NTL9_INPUT_XYZ}" >> "${SUBMIT_LOG}"
echo "  job ${JID_NTL9}, name ${CRYPTIC[ntl9]}, partition priority_gpu, time 02:00:00"

echo ""
echo "All 3 gate jobs submitted. Submission log: ${SUBMIT_LOG}"
echo ""
sacct -j "${JID_WW},${JID_GB3},${JID_NTL9}" --format=JobID,JobName,Partition,State,Submit,Start
