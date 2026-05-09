#!/bin/bash
#SBATCH --partition=scavenge_gpu
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=40G
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --output=/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/logs/bioemu-%A_%a.log
#SBATCH --error=/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/logs/bioemu-%A_%a.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=amita4171@gmail.com
#SBATCH --requeue

###############################################################################
# BioEmu Batch 2 Ensemble Generation — 12h MEDIUM variant for L=200-499 proteins
#
# Forked from bioemu_batch2_24h.sbatch on 2026-05-05 per Round-4 BioEmu reorg
# (recommendations #1, #6).
# Differences from bioemu_batch2_24h.sbatch:
#   - --time=12:00:00 (was 23:59:00) — medium proteins finish well under 12h
#     per runtime model in round-4 study §1; 12h ceiling improves backfill.
#   - --cpus-per-task=4 (was 2) — recommendation #6.
#   - --mem=40G (kept) — required for L=200-499 proteins.
#   - --partition=scavenge_gpu (kept) — Standard SU rate already 1.5/hr on
#     RTX 5000 Ada via scavenge_gpu (10× lower than other Standard partitions).
#
# All other settings (env, GPU keepalive, disorder pre-screen, oversampling
# formula, batch_size_100 formula, NPZ cleanup) preserved verbatim from the
# 24h variant — LOCKED per Sub 1.2 success criteria + OSF v3 §7.
#
# Cohort: 18 PENDING proteins (idx 11, 18-19, 24-38) with L=200-499 aa.
###############################################################################

set -euo pipefail

# Paths
SCRIPTS_DIR_SRC="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts"
SCRIPTS_DIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts"
MANIFEST_CSV="${SCRIPTS_DIR}/batch2_manifest.csv"
MANIFEST_FASTA="${SCRIPTS_DIR}/batch2_manifest.fasta"
SCRATCH="/nfs/roberts/scratch/pi_mg269/rag88"
OUTPUT_BASE="${SCRATCH}/gamma/bioemu-ensembles/batch2"
CACHE_DIR="${SCRATCH}/.bioemu_embeds_cache"  # share with batch 1 (seq-keyed hash)

# Protein index from array task ID
PROTEIN_IDX=${SLURM_ARRAY_TASK_ID}

# Parse manifest row: protein_id, uniprot_id, sequence, length, ..., num_samples
PARSED=$(python3 -c "
import csv
with open('${MANIFEST_CSV}') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
r = rows[${PROTEIN_IDX}]
print('{}|{}|{}|{}|{}|{}'.format(
    r['protein_id'], r['uniprot_id'], r['length'],
    r['expected_class'], r['num_samples'], r['memory_gb']))
")

PROTEIN_ID=$(echo "${PARSED}" | cut -d'|' -f1)
UNIPROT_ID=$(echo "${PARSED}" | cut -d'|' -f2)
SEQ_LEN=$(echo "${PARSED}" | cut -d'|' -f3)
CLS=$(echo "${PARSED}" | cut -d'|' -f4)
NUM_SAMPLES=$(echo "${PARSED}" | cut -d'|' -f5)

OUTPUT_DIR="${OUTPUT_BASE}/${UNIPROT_ID}"
mkdir -p "${OUTPUT_DIR}" "${OUTPUT_BASE}/logs"

echo "============================================================"
echo "BioEmu Batch 2 Generation (Sub 1.2 task-004) [12h MEDIUM variant]"
echo "  Job ID:       ${SLURM_JOB_ID}"
echo "  Array Task:   ${SLURM_ARRAY_TASK_ID}"
echo "  Node:         $(hostname)"
echo "  Start:        $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "  Partition:    ${SLURM_JOB_PARTITION}"
echo "  GPU:          $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'unknown')"
echo "  Protein idx:  ${PROTEIN_IDX}"
echo "  Protein id:   ${PROTEIN_ID}"
echo "  UniProt:      ${UNIPROT_ID}"
echo "  Length:       ${SEQ_LEN}"
echo "  Class:        ${CLS}"
echo "  Num samples:  ${NUM_SAMPLES}"
echo "  Output dir:   ${OUTPUT_DIR}"
echo "============================================================"

if ! nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | grep -qi "5000 Ada"; then
    echo "WARNING: Not on RTX 5000 Ada! GPU type check failed."
    echo "This violates the Sub 1.2 task-004 SU policy. Aborting."
    exit 99
fi

nvidia-smi
echo ""

module purge
module load miniconda/24.11.3
source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-bioemu

echo "Environment check:"
python --version
python -c "import bioemu; print(f'  bioemu: {bioemu.__version__}')"
python -c "import torch; print(f'  torch: {torch.__version__}'); print(f'  CUDA available: {torch.cuda.is_available()}'); print(f'  GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"none\"}')"
echo ""

export HF_HOME="${SCRATCH}/.hf_cache"
export BIOEMU_EMBEDS_CACHE="${CACHE_DIR}"
mkdir -p "${HF_HOME}" "${CACHE_DIR}"
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
export MPLBACKEND=Agg

if [ -f "${OUTPUT_DIR}/generation_status.json" ]; then
    STATUS=$(python3 -c "import json; d=json.load(open('${OUTPUT_DIR}/generation_status.json')); print(d.get('status','unknown'))")
    if [ "$STATUS" = "success" ]; then
        echo "SKIPPING: ${UNIPROT_ID} already completed successfully."
        exit 0
    else
        echo "Previous run status: ${STATUS}. Re-running..."
        rm -f "${OUTPUT_DIR}/generation_status.json"
    fi
fi

# Length-aware batch_size_100 (LOCKED per OSF v3 §7).
BATCH_SIZE_100=$(python3 -c "
import math
L = ${SEQ_LEN}
target_bs = 3
bs100 = math.ceil(target_bs * (L/100)**2)
print(max(10, bs100))
")
echo "Computed batch_size_100 = ${BATCH_SIZE_100} for L=${SEQ_LEN} (target batch_size>=3)"

KEEPALIVE_SCRIPT="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/gpu_keepalive.py"
python "${KEEPALIVE_SCRIPT}" > "${OUTPUT_BASE}/logs/keepalive-${SLURM_JOB_ID}.log" 2>&1 &
KEEPALIVE_PID=$!
echo "GPU keepalive spawned (PID ${KEEPALIVE_PID}) — log: keepalive-${SLURM_JOB_ID}.log"
trap 'kill ${KEEPALIVE_PID} 2>/dev/null || true' EXIT

python "${SCRIPTS_DIR_SRC}/bioemu_generate_single.py" \
    --fasta "${MANIFEST_FASTA}" \
    --protein-index "${PROTEIN_IDX}" \
    --output-dir "${OUTPUT_DIR}" \
    --cache-dir "${CACHE_DIR}" \
    --num-samples "${NUM_SAMPLES}" \
    --batch-size-100 "${BATCH_SIZE_100}" \
    --model-name "bioemu-v1.1" \
    --seed 42

EXIT_CODE=$?
kill ${KEEPALIVE_PID} 2>/dev/null || true

NPZ_CLEANUP_BYTES=0
NPZ_CLEANUP_COUNT=0
if [ ${EXIT_CODE} -eq 0 ] \
   && [ -f "${OUTPUT_DIR}/samples.xtc" ] \
   && [ -s "${OUTPUT_DIR}/samples.xtc" ]; then
    NPZ_FILES=( "${OUTPUT_DIR}"/batch_*.npz )
    if [ -e "${NPZ_FILES[0]}" ]; then
        NPZ_CLEANUP_COUNT=${#NPZ_FILES[@]}
        NPZ_CLEANUP_BYTES=$(du -bc "${OUTPUT_DIR}"/batch_*.npz 2>/dev/null | tail -n1 | awk '{print $1}')
        rm -f "${OUTPUT_DIR}"/batch_*.npz
        echo "NPZ cleanup: deleted ${NPZ_CLEANUP_COUNT} batch_*.npz files (${NPZ_CLEANUP_BYTES} bytes freed) — samples.xtc preserved"
    else
        echo "NPZ cleanup: no batch_*.npz files present — nothing to delete"
    fi
else
    echo "NPZ cleanup: skipped (exit=${EXIT_CODE}, samples.xtc may be missing/empty) — keeping NPZs for resume"
fi

echo ""
echo "============================================================"
echo "BioEmu batch 2 generation finished [12h MEDIUM variant]"
echo "  Protein:    ${UNIPROT_ID}"
echo "  Exit code:  ${EXIT_CODE}"
echo "  NPZ freed:  ${NPZ_CLEANUP_BYTES} bytes (${NPZ_CLEANUP_COUNT} files)"
echo "  End time:   $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "============================================================"

exit ${EXIT_CODE}
