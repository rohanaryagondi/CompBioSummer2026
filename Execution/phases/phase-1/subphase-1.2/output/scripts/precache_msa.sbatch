#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --output=/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/logs/precache-%j.log
#SBATCH --error=/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/logs/precache-%j.err

###############################################################################
# MSA Pre-cache SLURM job for BioEmu Batch 2 (Sub 1.2 task-004)
#
# Runs precache_msa.py on a compute node with internet access (compute nodes
# at YCRC have outbound internet for HTTPS). Primes the MSA cache for a
# range of batch 2 proteins in one pass. Each protein takes ~1-3 min.
#
# Usage:
#   sbatch --export=INDICES=0,1,2 --job-name=<cryptic> precache_msa.sbatch
#   sbatch --export=INDICES=all --time=04:00:00 --job-name=<cryptic> precache_msa.sbatch
#
# Environment variables:
#   INDICES - comma-separated or "all". Defaults to "0" if unset.
###############################################################################

set -euo pipefail

INDICES="${INDICES:-0}"
SCRIPTS_DIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts"
SCRATCH="/nfs/roberts/scratch/pi_mg269/rag88"
CACHE_DIR="${SCRATCH}/.bioemu_embeds_cache"
MANIFEST_FASTA="${SCRIPTS_DIR}/batch2_manifest.fasta"
mkdir -p "${CACHE_DIR}"

echo "============================================================"
echo "BioEmu MSA Pre-cache (Sub 1.2 task-004)"
echo "  Job ID:    ${SLURM_JOB_ID}"
echo "  Node:      $(hostname)"
echo "  Start:     $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "  Partition: ${SLURM_JOB_PARTITION}"
echo "  INDICES:   ${INDICES}"
echo "  Cache dir: ${CACHE_DIR}"
echo "============================================================"

# Load conda
module purge
module load miniconda/24.11.3
source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-bioemu

# Env hygiene (matches Sub 1.1 submit script)
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
export HF_HOME="${SCRATCH}/.hf_cache"
export MPLBACKEND=Agg
mkdir -p "${HF_HOME}"

python "${SCRIPTS_DIR}/precache_msa.py" \
    --manifest-fasta "${MANIFEST_FASTA}" \
    --cache-dir "${CACHE_DIR}" \
    --indices "${INDICES}"

echo "Pre-cache finished at $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
