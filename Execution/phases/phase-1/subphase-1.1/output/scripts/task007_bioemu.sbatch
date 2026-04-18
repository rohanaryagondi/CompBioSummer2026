#!/bin/bash
#SBATCH --partition=gpu_devel
#SBATCH --time=00:45:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=amita4171@gmail.com

###############################################################################
# BioEmu sanity check: single-protein, 100 conformations on RTX 5000 Ada.
# Args passed via exported env vars (see task007_submit.sh):
#   SHORT_NAME    - ntl9 | acbp | fkbp12 | enhd | crambin
#   SEQUENCE      - amino acid sequence (one-letter)
#   OUTPUT_DIR    - absolute path to protein output dir
###############################################################################

set -euo pipefail

SCRIPTS_DIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts"
SCRATCH="/nfs/roberts/scratch/pi_mg269/rag88"
CACHE_DIR="${SCRATCH}/.bioemu_embeds_cache"

echo "============================================================"
echo "BioEmu Sanity (Task 007)"
echo "  Job ID:       ${SLURM_JOB_ID}"
echo "  Node:         $(hostname)"
echo "  Start:        $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "  Partition:    ${SLURM_JOB_PARTITION}"
echo "  GPU:          $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo unknown)"
echo "  Short name:   ${SHORT_NAME}"
echo "  Output dir:   ${OUTPUT_DIR}"
echo "============================================================"

nvidia-smi
echo ""

module purge
module load miniconda/24.11.3
source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-bioemu

python --version
python -c "import bioemu; print(f'  bioemu: {bioemu.__version__}')"
python -c "import torch; print(f'  torch: {torch.__version__}, cuda: {torch.cuda.is_available()}')"

export HF_HOME="${SCRATCH}/.hf_cache"
export BIOEMU_EMBEDS_CACHE="${CACHE_DIR}"
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
export MPLBACKEND=Agg
mkdir -p "${HF_HOME}" "${CACHE_DIR}"

# Skip if already done successfully
if [ -f "${OUTPUT_DIR}/generation_status.json" ]; then
    STATUS=$(python3 -c "import json; d=json.load(open('${OUTPUT_DIR}/generation_status.json')); print(d.get('status','unknown'))" 2>/dev/null || echo unknown)
    if [ "$STATUS" = "success" ]; then
        echo "SKIPPING: ${SHORT_NAME} already completed."
        exit 0
    fi
    rm -f "${OUTPUT_DIR}/generation_status.json"
fi

python "${SCRIPTS_DIR}/task007_bioemu_sanity.py" \
    --short-name "${SHORT_NAME}" \
    --sequence "${SEQUENCE}" \
    --output-dir "${OUTPUT_DIR}" \
    --cache-dir "${CACHE_DIR}" \
    --num-samples 100 \
    --batch-size-100 10 \
    --model-name "bioemu-v1.1" \
    --seed 42

EXIT_CODE=$?
echo ""
echo "============================================================"
echo "BioEmu sanity finished: ${SHORT_NAME}, exit=${EXIT_CODE}, $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "============================================================"
exit ${EXIT_CODE}
