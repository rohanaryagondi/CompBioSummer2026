#!/bin/bash
#SBATCH --job-name=bioemu-batch1
#SBATCH --partition=gpu
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=40G
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --output=/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch1/logs/bioemu-%A_%a.log
#SBATCH --error=/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch1/logs/bioemu-%A_%a.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=amita4171@gmail.com

###############################################################################
# BioEmu Batch Ensemble Generation (Task 003)
#
# SLURM array job: each task generates 2000 conformations for one protein.
# The array index maps to the protein index in the FASTA file.
#
# Usage:
#   # Submit proteins 0-9 (first 10):
#   sbatch --array=0-9 bioemu_batch.sbatch
#
#   # Submit proteins 10-19 (next 10):
#   sbatch --array=10-19 bioemu_batch.sbatch
#
#   # Submit specific proteins:
#   sbatch --array=0,5,10,15,20 bioemu_batch.sbatch
#
# IMPORTANT: Due to QOS limit of 2 pending jobs per user, submit in small
# batches (10 proteins per submission). The array tasks within one submission
# count as one job for QOS purposes.
###############################################################################

set -euo pipefail

# Paths
SCRIPTS_DIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts"
FASTA="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/task-003-sequences.fasta"
SCRATCH="/nfs/roberts/scratch/pi_mg269/rag88"
OUTPUT_BASE="${SCRATCH}/gamma/bioemu-ensembles/batch1"
CACHE_DIR="${SCRATCH}/.bioemu_embeds_cache"

# Protein index from array task ID
PROTEIN_IDX=${SLURM_ARRAY_TASK_ID}

# Parse protein name from FASTA for directory naming
PROTEIN_NAME=$(python3 -c "
entries = []
header = None
with open('${FASTA}') as f:
    for line in f:
        line = line.strip()
        if line.startswith('>'):
            if header is not None:
                entries.append(header)
            header = line[1:]
    if header:
        entries.append(header)
parts = entries[${PROTEIN_IDX}].split('|')
# Use UniProt_ID as directory name
print(parts[0])
")

OUTPUT_DIR="${OUTPUT_BASE}/${PROTEIN_NAME}"

echo "============================================================"
echo "BioEmu Batch Generation (Task 003)"
echo "  Job ID:       ${SLURM_JOB_ID}"
echo "  Array Task:   ${SLURM_ARRAY_TASK_ID}"
echo "  Node:         $(hostname)"
echo "  Start:        $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "  Partition:    ${SLURM_JOB_PARTITION}"
echo "  GPU:          $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'unknown')"
echo "  Protein idx:  ${PROTEIN_IDX}"
echo "  Protein:      ${PROTEIN_NAME}"
echo "  Output dir:   ${OUTPUT_DIR}"
echo "============================================================"

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

# Set caches to scratch
export HF_HOME="${SCRATCH}/.hf_cache"
export BIOEMU_EMBEDS_CACHE="${CACHE_DIR}"
mkdir -p "${HF_HOME}" "${CACHE_DIR}"

# Fix protobuf conflict between tensorflow-cpu and jax/xla
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Set MPLBACKEND to avoid display issues
export MPLBACKEND=Agg

# Check if already completed
if [ -f "${OUTPUT_DIR}/generation_status.json" ]; then
    STATUS=$(python3 -c "import json; d=json.load(open('${OUTPUT_DIR}/generation_status.json')); print(d.get('status','unknown'))")
    if [ "$STATUS" = "success" ]; then
        echo "SKIPPING: ${PROTEIN_NAME} already completed successfully."
        echo "  Remove ${OUTPUT_DIR}/generation_status.json to re-run."
        exit 0
    else
        echo "Previous run status: ${STATUS}. Re-running..."
        rm -f "${OUTPUT_DIR}/generation_status.json"
    fi
fi

# Run generation
python "${SCRIPTS_DIR}/bioemu_generate_single.py" \
    --fasta "${FASTA}" \
    --protein-index "${PROTEIN_IDX}" \
    --output-dir "${OUTPUT_DIR}" \
    --cache-dir "${CACHE_DIR}" \
    --num-samples 2000 \
    --batch-size-100 10 \
    --model-name "bioemu-v1.1" \
    --seed 42

EXIT_CODE=$?

echo ""
echo "============================================================"
echo "BioEmu generation finished"
echo "  Protein:   ${PROTEIN_NAME}"
echo "  Exit code: ${EXIT_CODE}"
echo "  End time:  $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "============================================================"

exit ${EXIT_CODE}
