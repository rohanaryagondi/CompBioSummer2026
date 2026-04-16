#!/bin/bash
###############################################################################
# BioEmu Batch Submission Controller (Task 003)
#
# Submits SLURM array jobs in phases to respect QOS limit (max 2 pending).
# Each phase submits one array job covering a range of protein indices.
#
# Usage:
#   # Phase 1: First protein on login node (needs internet for MSA server)
#   bash submit_bioemu_batches.sh --cache-first
#
#   # Phase 2: Submit first batch (proteins 0-9)
#   bash submit_bioemu_batches.sh --batch 1
#
#   # Phase 3: Submit second batch (proteins 10-19)
#   bash submit_bioemu_batches.sh --batch 2
#
#   # Phase 4: Submit third batch (proteins 20-29)
#   bash submit_bioemu_batches.sh --batch 3
#
#   # Phase 5: Submit fourth batch (proteins 30-39)
#   bash submit_bioemu_batches.sh --batch 4
#
#   # Phase 6: Submit fifth batch (proteins 40-46)
#   bash submit_bioemu_batches.sh --batch 5
#
#   # Check status of all proteins
#   bash submit_bioemu_batches.sh --status
#
#   # Resubmit failed proteins
#   bash submit_bioemu_batches.sh --retry-failed
###############################################################################

set -euo pipefail

SCRIPTS_DIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts"
FASTA="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/task-003-sequences.fasta"
SCRATCH="/nfs/roberts/scratch/pi_mg269/rag88"
OUTPUT_BASE="${SCRATCH}/gamma/bioemu-ensembles/batch1"
CACHE_DIR="${SCRATCH}/.bioemu_embeds_cache"
SBATCH_SCRIPT="${SCRIPTS_DIR}/bioemu_batch.sbatch"

# Create log directory
mkdir -p "${OUTPUT_BASE}/logs"

# Total proteins in FASTA
TOTAL_PROTEINS=$(grep -c '^>' "${FASTA}")
echo "Total proteins in FASTA: ${TOTAL_PROTEINS}"

case "${1:-}" in
    --cache-first)
        echo ""
        echo "=== PHASE 1: Cache embeddings for first protein (login node) ==="
        echo "This must run on a node with internet access (login node)."
        echo "It will cache MSA embeddings for the first protein."
        echo ""

        # Load conda
        source /apps/custom/lmod/lmod/init/profile
        module purge
        module load miniconda/24.11.3
        source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
        conda activate env-bioemu

        # Fix protobuf
        export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
        export HF_HOME="${SCRATCH}/.hf_cache"
        export MPLBACKEND=Agg
        mkdir -p "${HF_HOME}" "${CACHE_DIR}"

        echo "WARNING: This will use GPU on the login node (if available)."
        echo "For a CPU-only login node, this will fail. Use an interactive session instead:"
        echo "  srun --partition=gpu_devel --gres=gpu:1 --mem=40G --cpus-per-task=4 --time=01:00:00 --pty bash"
        echo ""
        echo "Starting embedding cache for protein index 0..."

        # Get the first protein name
        FIRST_PROTEIN=$(python3 -c "
with open('${FASTA}') as f:
    for line in f:
        if line.startswith('>'):
            print(line.strip()[1:].split('|')[0])
            break
")
        echo "First protein: ${FIRST_PROTEIN}"

        # Generate with just 10 samples to cache embeddings
        python "${SCRIPTS_DIR}/bioemu_generate_single.py" \
            --fasta "${FASTA}" \
            --protein-index 0 \
            --output-dir "${OUTPUT_BASE}/${FIRST_PROTEIN}" \
            --cache-dir "${CACHE_DIR}" \
            --num-samples 10 \
            --seed 42

        echo ""
        echo "Embedding cache populated. Now submit batch jobs."
        echo "NOTE: Re-run protein 0 with full 2000 samples via batch submission."
        # Clean up the 10-sample test
        rm -rf "${OUTPUT_BASE}/${FIRST_PROTEIN}"
        ;;

    --batch)
        BATCH_NUM="${2:-}"
        if [ -z "${BATCH_NUM}" ]; then
            echo "Usage: $0 --batch <1-5>"
            exit 1
        fi

        case "${BATCH_NUM}" in
            1) ARRAY="0-9" ;;
            2) ARRAY="10-19" ;;
            3) ARRAY="20-29" ;;
            4) ARRAY="30-39" ;;
            5) ARRAY="40-$((TOTAL_PROTEINS - 1))" ;;
            *)
                echo "Invalid batch number. Use 1-5."
                exit 1
                ;;
        esac

        echo ""
        echo "=== Submitting batch ${BATCH_NUM}: array=${ARRAY} ==="

        # Check current pending/running jobs
        PENDING=$(squeue -u "${USER}" -t PENDING -h 2>/dev/null | wc -l)
        RUNNING=$(squeue -u "${USER}" -t RUNNING -h 2>/dev/null | wc -l)
        echo "Current jobs: ${RUNNING} running, ${PENDING} pending"

        if [ "${PENDING}" -ge 2 ]; then
            echo "WARNING: Already have ${PENDING} pending jobs. QOS limit is 2."
            echo "Wait for some jobs to start before submitting more."
            exit 1
        fi

        JOB_ID=$(sbatch --array="${ARRAY}" "${SBATCH_SCRIPT}" | awk '{print $4}')
        echo "Submitted job ${JOB_ID} with array=${ARRAY}"
        echo "Monitor with: squeue -u ${USER}"
        echo "Check logs in: ${OUTPUT_BASE}/logs/"
        ;;

    --status)
        echo ""
        echo "=== BioEmu Generation Status ==="
        echo ""

        SUCCESS=0
        FAILED=0
        PARTIAL=0
        MISSING=0
        TOTAL=0

        # Parse FASTA to get protein names
        python3 -c "
import json
import os

fasta_path = '${FASTA}'
output_base = '${OUTPUT_BASE}'

entries = []
header = None
with open(fasta_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith('>'):
            if header is not None:
                entries.append(header)
            header = line[1:]
    if header:
        entries.append(header)

success = 0
failed = 0
partial = 0
missing = 0

for i, header in enumerate(entries):
    uid = header.split('|')[0]
    protein_name = header.split('|')[1] if '|' in header else uid
    status_file = os.path.join(output_base, uid, 'generation_status.json')

    if os.path.exists(status_file):
        with open(status_file) as sf:
            status = json.load(sf)
        s = status.get('status', 'unknown')
        elapsed = status.get('elapsed_minutes', '?')
        n_conf = status.get('validation', {}).get('conformation_count', '?')

        if s == 'success':
            icon = 'OK'
            success += 1
        elif s == 'partial':
            icon = 'PARTIAL'
            partial += 1
        else:
            icon = 'FAIL'
            failed += 1

        print(f'  [{icon:7s}] {i:2d}. {uid:30s} {protein_name:30s} {elapsed:>6s} min  conf={n_conf}')
    else:
        icon = 'PENDING'
        missing += 1
        print(f'  [{icon:7s}] {i:2d}. {uid:30s} {protein_name:30s}')

total = len(entries)
print()
print(f'Summary: {success} success, {partial} partial, {failed} failed, {missing} pending')
print(f'Total: {success + partial}/{total} generated ({success}/{total} fully validated)')
"
        ;;

    --retry-failed)
        echo ""
        echo "=== Finding failed proteins for retry ==="

        FAILED_INDICES=$(python3 -c "
import json
import os

fasta_path = '${FASTA}'
output_base = '${OUTPUT_BASE}'

entries = []
header = None
with open(fasta_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith('>'):
            if header is not None:
                entries.append(header)
            header = line[1:]
    if header:
        entries.append(header)

failed = []
for i, header in enumerate(entries):
    uid = header.split('|')[0]
    status_file = os.path.join(output_base, uid, 'generation_status.json')

    if os.path.exists(status_file):
        with open(status_file) as sf:
            status = json.load(sf)
        if status.get('status') in ('failed', 'partial'):
            failed.append(str(i))
            # Remove status file so the job will re-run
            os.remove(status_file)
    else:
        # Never ran
        pass

if failed:
    print(','.join(failed))
else:
    print('NONE')
")

        if [ "${FAILED_INDICES}" = "NONE" ]; then
            echo "No failed proteins found."
        else
            echo "Failed protein indices: ${FAILED_INDICES}"
            echo "Submitting retry..."
            JOB_ID=$(sbatch --array="${FAILED_INDICES}" "${SBATCH_SCRIPT}" | awk '{print $4}')
            echo "Submitted retry job ${JOB_ID}"
        fi
        ;;

    *)
        echo "Usage: $0 <--cache-first|--batch N|--status|--retry-failed>"
        echo ""
        echo "  --cache-first    Run first protein to cache MSA embeddings (login node)"
        echo "  --batch N        Submit batch N (1-5, each ~10 proteins)"
        echo "  --status         Show generation status for all proteins"
        echo "  --retry-failed   Resubmit failed/partial proteins"
        exit 1
        ;;
esac
