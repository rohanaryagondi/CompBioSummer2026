#!/bin/bash
#SBATCH --job-name=q7k-r5
#SBATCH --partition=gpu,gpu_rtx6000
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=10G
#SBATCH --gres=gpu:1
#SBATCH --output=/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch1/logs/q7k-r5-%A_%a.log
#SBATCH --error=/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch1/logs/q7k-r5-%A_%a.err

set -euo pipefail

SCRIPTS_DIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts"
FASTA="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/task-003-sequences.fasta"
SCRATCH="/nfs/roberts/scratch/pi_mg269/rag88"
OUTPUT_BASE="${SCRATCH}/gamma/bioemu-ensembles/batch1"
CACHE_DIR="${SCRATCH}/.bioemu_embeds_cache"

PROTEIN_IDX=${SLURM_ARRAY_TASK_ID}

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
print(parts[0])
")

OUTPUT_DIR="${OUTPUT_BASE}/${PROTEIN_NAME}"

echo "============================================================"
echo "  Job ID:       ${SLURM_JOB_ID}"
echo "  Array Task:   ${SLURM_ARRAY_TASK_ID}"
echo "  Node:         $(hostname)"
echo "  Start:        $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "  Partition:    ${SLURM_JOB_PARTITION}"
echo "  GPU:          $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'unknown')"
echo "  Protein idx:  ${PROTEIN_IDX}"
echo "  Protein:      ${PROTEIN_NAME}"
echo "  Output dir:   ${OUTPUT_DIR}"
echo "  Mode:         TOP-UP (oversample to 2000 physical)"
echo "============================================================"

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

# Skip if already at target
if [ -f "${OUTPUT_DIR}/generation_status.json" ]; then
    PHYS=$(python3 -c "import json; d=json.load(open('${OUTPUT_DIR}/generation_status.json')); print(d.get('validation',{}).get('conformation_count',0))")
    if [ "${PHYS}" -ge 2000 ]; then
        echo "SKIPPING: ${PROTEIN_NAME} already has ${PHYS} physical conformations."
        exit 0
    fi
fi

python "${SCRIPTS_DIR}/bioemu_topup_single.py" \
    --output-dir "${OUTPUT_DIR}" \
    --cache-dir "${CACHE_DIR}" \
    --target-physical 2000 \
    --safety-margin 1.20 \
    --batch-size-100 30 \
    --model-name "bioemu-v1.1" \
    --seed 42

EXIT_CODE=$?

echo ""
echo "============================================================"
echo "  Protein:   ${PROTEIN_NAME}"
echo "  Exit code: ${EXIT_CODE}"
echo "  End time:  $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "============================================================"

exit ${EXIT_CODE}
