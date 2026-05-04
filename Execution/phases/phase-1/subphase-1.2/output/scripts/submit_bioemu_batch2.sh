#!/bin/bash
###############################################################################
# BioEmu Batch 2 Submission Controller (Sub 1.2 task-004)
#
# Forked from
# phases/phase-1/subphase-1.1/output/scripts/submit_bioemu_batches.sh
#
# Changes from batch 1:
#   - Reads batch2_manifest.csv and batch2_manifest.fasta instead of the
#     batch 1 sequences FASTA (per-protein num_samples + class metadata)
#   - RTX 5000 Ada partition forced (never gpu_h200, gpu_b200)
#   - Up to ~10 batches of 10 proteins each (manifest has 93 proteins)
#   - Cryptic 8-char alphanumeric SLURM job name auto-generated per submit
#   - --cache-first runs one protein on login node to prime MSA cache
#     (batch 2 FASTA has mostly-new sequences, so MSA cache needs warming)
#
# Usage:
#   # Phase 1: Cache MSA embeddings for first protein (login node)
#   bash submit_bioemu_batch2.sh --cache-first
#
#   # Phase 2: Submit batches incrementally (respects QOS 2-pending limit)
#   bash submit_bioemu_batch2.sh --batch 1   # proteins 0-9
#   bash submit_bioemu_batch2.sh --batch 2   # proteins 10-19
#   ...
#   bash submit_bioemu_batch2.sh --batch 10  # proteins 90-92
#
#   # Check status across all proteins
#   bash submit_bioemu_batch2.sh --status
#
#   # Resubmit failed/partial proteins
#   bash submit_bioemu_batch2.sh --retry-failed
###############################################################################

set -euo pipefail

SCRIPTS_DIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts"
SRC_DIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts"
MANIFEST_CSV="${SCRIPTS_DIR}/batch2_manifest.csv"
MANIFEST_FASTA="${SCRIPTS_DIR}/batch2_manifest.fasta"
SCRATCH="/nfs/roberts/scratch/pi_mg269/rag88"
OUTPUT_BASE="${SCRATCH}/gamma/bioemu-ensembles/batch2"
CACHE_DIR="${SCRATCH}/.bioemu_embeds_cache"
SBATCH_SCRIPT="${SCRIPTS_DIR}/bioemu_batch2.sbatch"

# Create log directory and base output
mkdir -p "${OUTPUT_BASE}/logs"

# Sanity checks on manifest
if [ ! -f "${MANIFEST_CSV}" ]; then
    echo "ERROR: Manifest CSV not found at ${MANIFEST_CSV}"
    echo "  Run: python3 ${SCRIPTS_DIR}/batch2_manifest_builder.py"
    exit 1
fi
if [ ! -f "${MANIFEST_FASTA}" ]; then
    echo "ERROR: Manifest FASTA not found at ${MANIFEST_FASTA}"
    echo "  Run: python3 ${SCRIPTS_DIR}/batch2_manifest_builder.py"
    exit 1
fi

# Total proteins in manifest
TOTAL_PROTEINS=$(python3 -c "
import csv
with open('${MANIFEST_CSV}') as f:
    reader = csv.DictReader(f)
    print(sum(1 for _ in reader))
")
echo "Total proteins in batch2_manifest.csv: ${TOTAL_PROTEINS}"

# Helper: generate cryptic 8-char job name
cryptic_jobname() {
    python3 -c "
import random, string
random.seed()
alphabet = string.ascii_lowercase + string.digits
print(''.join(random.choices(alphabet, k=8)))
"
}

case "${1:-}" in
    --cache-first)
        echo ""
        echo "=== PHASE 1: Cache embeddings for first protein (login node) ==="
        echo "This must run on a node with internet access (login node)."
        echo "It will cache MSA embeddings for the first protein in the manifest,"
        echo "priming the MSA cache for subsequent SLURM jobs."
        echo ""

        # Load conda
        module purge
        module load miniconda/24.11.3
        source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
        conda activate env-bioemu

        # Fix protobuf
        export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
        export HF_HOME="${SCRATCH}/.hf_cache"
        export MPLBACKEND=Agg
        mkdir -p "${HF_HOME}" "${CACHE_DIR}"

        # Get the first protein UniProt ID
        FIRST_UID=$(python3 -c "
import csv
with open('${MANIFEST_CSV}') as f:
    reader = csv.DictReader(f)
    first = next(reader)
print(first['uniprot_id'])
")
        echo "First-protein UniProt_ID: ${FIRST_UID}"
        echo ""

        # Generate with just 10 samples to cache embeddings, then delete
        # the small run so the full submission can produce a clean ensemble.
        TMP_OUT="${OUTPUT_BASE}/_cache_priming"
        mkdir -p "${TMP_OUT}"

        python "${SRC_DIR}/bioemu_generate_single.py" \
            --fasta "${MANIFEST_FASTA}" \
            --protein-index 0 \
            --output-dir "${TMP_OUT}/${FIRST_UID}" \
            --cache-dir "${CACHE_DIR}" \
            --num-samples 10 \
            --seed 42 || {
                echo ""
                echo "WARNING: Cache-priming run failed. Possible causes:"
                echo "  - Login node has no GPU (try interactive devel session)"
                echo "  - Protobuf/HF version drift in env-bioemu"
                echo "  - MSA server unreachable (check MSA_SERVER env var if required)"
                echo ""
                echo "If the cache was at least partially populated, SLURM jobs"
                echo "may still succeed (they fall back to recomputing MSA on GPU)."
                echo "Proceed with --batch 1 anyway and monitor first batch."
            }

        # Cleanup partial run; MSA cache is external, not in TMP_OUT
        rm -rf "${TMP_OUT}"

        echo ""
        echo "MSA cache priming complete. Now submit batches via:"
        echo "  bash submit_bioemu_batch2.sh --batch 1"
        ;;

    --batch)
        BATCH_NUM="${2:-}"
        if [ -z "${BATCH_NUM}" ]; then
            echo "Usage: $0 --batch <N>   (N = 1..ceil(total/10))"
            exit 1
        fi

        # Compute array range: batch N covers proteins [(N-1)*10 .. N*10-1]
        # capped at TOTAL_PROTEINS-1
        LO=$(( (BATCH_NUM - 1) * 10 ))
        HI=$(( BATCH_NUM * 10 - 1 ))
        if [ "${HI}" -ge "${TOTAL_PROTEINS}" ]; then
            HI=$(( TOTAL_PROTEINS - 1 ))
        fi
        if [ "${LO}" -ge "${TOTAL_PROTEINS}" ]; then
            echo "ERROR: batch ${BATCH_NUM} would start beyond total (${TOTAL_PROTEINS})."
            exit 1
        fi
        ARRAY="${LO}-${HI}"

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

        JOBNAME=$(cryptic_jobname)
        echo "Cryptic job name: ${JOBNAME}"

        JOB_ID=$(sbatch --job-name="${JOBNAME}" --array="${ARRAY}" "${SBATCH_SCRIPT}" | awk '{print $4}')
        echo "Submitted job ${JOB_ID} with name=${JOBNAME} array=${ARRAY}"
        echo "Monitor with: squeue -u ${USER}"
        echo "Check logs in: ${OUTPUT_BASE}/logs/"
        ;;

    --status)
        echo ""
        echo "=== BioEmu Batch 2 Generation Status ==="
        echo ""
        python3 -c "
import json, os, csv
manifest_csv = '${MANIFEST_CSV}'
output_base = '${OUTPUT_BASE}'

with open(manifest_csv) as f:
    rows = list(csv.DictReader(f))

success = partial = failed = missing = 0
for i, r in enumerate(rows):
    uid = r['uniprot_id']
    status_file = os.path.join(output_base, uid, 'generation_status.json')
    if os.path.exists(status_file):
        try:
            with open(status_file) as sf:
                d = json.load(sf)
            s = d.get('status', 'unknown')
            elapsed = d.get('elapsed_minutes', '?')
            n_conf = d.get('validation', {}).get('conformation_count', '?')
        except Exception:
            s = 'parse-error'; elapsed = '?'; n_conf = '?'
        if s == 'success': icon = 'OK'; success += 1
        elif s == 'partial': icon = 'PARTIAL'; partial += 1
        else: icon = 'FAIL'; failed += 1
        print(f'  [{icon:7s}] {i:3d}. {uid:25s} len={r[\"length\"]:>4s} cls={r[\"expected_class\"]:22s} n={r[\"num_samples\"]:>5s} conf={n_conf} time={elapsed}')
    else:
        icon = 'PENDING'; missing += 1
        print(f'  [{icon:7s}] {i:3d}. {uid:25s} len={r[\"length\"]:>4s} cls={r[\"expected_class\"]:22s} n={r[\"num_samples\"]:>5s}')

total = len(rows)
print()
print(f'Summary: {success} success, {partial} partial, {failed} failed, {missing} pending / total {total}')
# >=2000 conformations count
over_2k = 0
for r in rows:
    sf = os.path.join(output_base, r['uniprot_id'], 'generation_status.json')
    if os.path.exists(sf):
        try:
            d = json.load(open(sf))
            c = d.get('validation', {}).get('conformation_count') or 0
            if c and c >= 2000: over_2k += 1
        except Exception: pass
print(f'Reached >=2,000 conformations: {over_2k}/{total}')
"
        ;;

    --retry-failed)
        echo ""
        echo "=== Finding failed/partial proteins for retry ==="

        FAILED_INDICES=$(python3 -c "
import json, os, csv
manifest_csv = '${MANIFEST_CSV}'
output_base = '${OUTPUT_BASE}'

with open(manifest_csv) as f:
    rows = list(csv.DictReader(f))

failed = []
for i, r in enumerate(rows):
    uid = r['uniprot_id']
    status_file = os.path.join(output_base, uid, 'generation_status.json')
    if os.path.exists(status_file):
        try:
            with open(status_file) as sf:
                d = json.load(sf)
            if d.get('status') in ('failed', 'partial'):
                failed.append(str(i))
                os.remove(status_file)
        except Exception:
            failed.append(str(i))
print(','.join(failed) if failed else 'NONE')
")

        if [ "${FAILED_INDICES}" = "NONE" ]; then
            echo "No failed/partial proteins found."
        else
            echo "Failed protein indices: ${FAILED_INDICES}"
            JOBNAME=$(cryptic_jobname)
            echo "Cryptic retry job name: ${JOBNAME}"
            JOB_ID=$(sbatch --job-name="${JOBNAME}" --array="${FAILED_INDICES}" "${SBATCH_SCRIPT}" | awk '{print $4}')
            echo "Submitted retry job ${JOB_ID}"
        fi
        ;;

    *)
        echo "Usage: $0 <--cache-first|--batch N|--status|--retry-failed>"
        echo ""
        echo "  --cache-first    Run first protein to cache MSA embeddings (login node)"
        echo "  --batch N        Submit batch N (proteins (N-1)*10 through N*10-1)"
        echo "  --status         Show generation status for all proteins"
        echo "  --retry-failed   Resubmit failed/partial proteins"
        echo ""
        echo "Total proteins in manifest: ${TOTAL_PROTEINS}"
        echo "Maximum batch number: $(( (TOTAL_PROTEINS + 9) / 10 ))"
        exit 1
        ;;
esac
