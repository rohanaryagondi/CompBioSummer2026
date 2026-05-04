#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=40G
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --output=/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/logs/bioemu-%A_%a.log
#SBATCH --error=/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/logs/bioemu-%A_%a.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=amita4171@gmail.com

###############################################################################
# BioEmu Batch 2 Ensemble Generation (Sub 1.2 task-004)
#
# SLURM array job: each task generates N conformations for one protein.
# Per-protein num_samples is read from batch2_manifest.csv (column 9).
#
# Requirements (per task-004 spec + user memory):
#  - RTX 5000 Ada partition `gpu` ONLY (NEVER gpu_h200 or gpu_b200)
#  - 2 CPUs, 40G RAM per Sub 1.1 SPG1 lesson
#  - Protobuf fix for tensorflow-cpu/jax conflict
#  - MSA cache reused from batch1 (same seq -> same cache)
#
# Usage (via submit_bioemu_batch2.sh):
#   sbatch --array=0-9 bioemu_batch2.sbatch
#   sbatch --array=10-19 bioemu_batch2.sbatch
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

# Output directory per protein (use UniProt_ID as directory name for
# consistency with batch 1 layout)
OUTPUT_DIR="${OUTPUT_BASE}/${UNIPROT_ID}"
mkdir -p "${OUTPUT_DIR}" "${OUTPUT_BASE}/logs"

echo "============================================================"
echo "BioEmu Batch 2 Generation (Sub 1.2 task-004)"
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

# Safety check: verify we are on RTX 5000 Ada (per SU policy)
if ! nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | grep -qi "5000 Ada"; then
    echo "WARNING: Not on RTX 5000 Ada! GPU type check failed."
    echo "This violates the Sub 1.2 task-004 SU policy. Aborting."
    exit 99
fi

# Show GPU info
nvidia-smi
echo ""

# Load conda and activate environment
module purge
module load miniconda/24.11.3
source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-bioemu

# Verify environment
echo "Environment check:"
python --version
python -c "import bioemu; print(f'  bioemu: {bioemu.__version__}')"
python -c "import torch; print(f'  torch: {torch.__version__}'); print(f'  CUDA available: {torch.cuda.is_available()}'); print(f'  GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"none\"}')"
echo ""

# Set caches to scratch (shared with batch 1)
export HF_HOME="${SCRATCH}/.hf_cache"
export BIOEMU_EMBEDS_CACHE="${CACHE_DIR}"
mkdir -p "${HF_HOME}" "${CACHE_DIR}"

# Fix protobuf conflict between tensorflow-cpu and jax/xla (per Sub 1.1 line 66)
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Set MPLBACKEND to avoid display issues
export MPLBACKEND=Agg

# Check if already completed
if [ -f "${OUTPUT_DIR}/generation_status.json" ]; then
    STATUS=$(python3 -c "import json; d=json.load(open('${OUTPUT_DIR}/generation_status.json')); print(d.get('status','unknown'))")
    if [ "$STATUS" = "success" ]; then
        echo "SKIPPING: ${UNIPROT_ID} already completed successfully."
        echo "  Remove ${OUTPUT_DIR}/generation_status.json to re-run."
        exit 0
    else
        echo "Previous run status: ${STATUS}. Re-running..."
        rm -f "${OUTPUT_DIR}/generation_status.json"
    fi
fi

# Length-aware batch_size_100 (2026-04-19 patch):
# bioemu.sample.py:239 computes `batch_size = int(batch_size_100 * (100/L)^2)`.
# Default batch_size_100=10 yields batch_size=0 for L > ~316 aa (bioemu:
# range(0, N, 0) → ValueError). Fix: scale batch_size_100 with (L/100)^2 so
# the resulting batch_size is always >=3. Floor at 10 (bioemu default) for
# short sequences. This ensures consistent batch size across all protein
# lengths (batch_size ~= 3 regardless of L). Verified: fixes FAILED cases
# at L=354 (_7), 361 (_8), 364 (_9), 556 (_1) from batch 1 of 2026-04-19.
BATCH_SIZE_100=$(python3 -c "
import math
L = ${SEQ_LEN}
target_bs = 3
bs100 = math.ceil(target_bs * (L/100)**2)
print(max(10, bs100))
")
echo "Computed batch_size_100 = ${BATCH_SIZE_100} for L=${SEQ_LEN} (target batch_size>=3)"

# ===========================================================================
# GPU keepalive (2026-04-20 patch per user directive): bioemu's MSA-build and
# model-load startup is CPU-heavy (tens of minutes for uncached proteins).
# YCRC auto-cancels GPU jobs with <10% util for >1 hr. Spawn gpu_keepalive.py
# as a BACKGROUND process BEFORE main bioemu invocation; it performs a tiny
# 64x64 matmul every 300 s against the same GPU, keeping util >0%. Kill on
# exit. Precedent: Sub 1.2 BioEmu precache 8887441 was YCRC-cancelled at 1.2h
# despite srun --overlap rescue (too late). Pre-startup keepalive avoids that.
# ===========================================================================
KEEPALIVE_SCRIPT="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/gpu_keepalive.py"
python "${KEEPALIVE_SCRIPT}" > "${OUTPUT_BASE}/logs/keepalive-${SLURM_JOB_ID}.log" 2>&1 &
KEEPALIVE_PID=$!
echo "GPU keepalive spawned (PID ${KEEPALIVE_PID}) — log: keepalive-${SLURM_JOB_ID}.log"
# Ensure keepalive dies when sbatch exits (safety; SLURM kills children anyway)
trap 'kill ${KEEPALIVE_PID} 2>/dev/null || true' EXIT

# Run generation (reuse Sub 1.1 bioemu_generate_single.py; batch 2 FASTA)
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
# Stop keepalive (trap will also fire on any earlier exit)
kill ${KEEPALIVE_PID} 2>/dev/null || true

# ===========================================================================
# Post-success NPZ cleanup (2026-05-03 patch — head-1.2 Item A storage saver):
# bioemu writes intermediate `batch_*.npz` files during sampling, then
# concatenates them into `samples.xtc` as the FINAL step (bioemu/sample.py:275).
# Once samples.xtc exists and is non-empty, the NPZs are redundant: ~73% of
# bytes per protein dir are intermediate NPZs that are never read again
# (validated: batch1 47 protein dirs have 2.18 GB NPZ vs 0.46 GB XTC).
#
# Failure path: keep NPZs intact. bioemu's resume uses
# `count_samples_in_output_dir` (sample.py:244) which counts batch_*.npz
# files. Deleting NPZs after a partial-success run would force regeneration
# from sample 0 on the next sbatch resubmission.
#
# Gate conditions (ALL must be true to delete NPZs):
#   1. EXIT_CODE == 0 (bioemu wrapper succeeded; status=success not partial)
#   2. samples.xtc exists at OUTPUT_DIR
#   3. samples.xtc has size > 0 bytes
#   4. At least one batch_*.npz exists (otherwise nothing to delete)
# ===========================================================================
NPZ_CLEANUP_BYTES=0
NPZ_CLEANUP_COUNT=0
if [ ${EXIT_CODE} -eq 0 ] \
   && [ -f "${OUTPUT_DIR}/samples.xtc" ] \
   && [ -s "${OUTPUT_DIR}/samples.xtc" ]; then
    # Count + sum NPZ bytes before deleting
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
echo "BioEmu batch 2 generation finished"
echo "  Protein:    ${UNIPROT_ID}"
echo "  Exit code:  ${EXIT_CODE}"
echo "  NPZ freed:  ${NPZ_CLEANUP_BYTES} bytes (${NPZ_CLEANUP_COUNT} files)"
echo "  End time:   $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "============================================================"

exit ${EXIT_CODE}
