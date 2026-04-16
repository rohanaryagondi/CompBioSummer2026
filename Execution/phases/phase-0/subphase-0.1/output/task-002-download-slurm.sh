#!/bin/bash
#SBATCH --job-name=tahoe-download
#SBATCH --partition=week
#SBATCH --time=5-00:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/output/tahoe-download-%j.log
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/output/tahoe-download-%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=amita4171@gmail.com

###############################################################################
# Tahoe-100M Download SLURM Job
#
# Downloads the full tahoebio/Tahoe-100M dataset from Hugging Face to
# HPC scratch storage. Expected runtime: 1-5 days depending on bandwidth.
#
# Monitor: squeue -j $SLURM_JOB_ID
# Logs:    output/tahoe-download-<jobid>.log
# Cancel:  scancel $SLURM_JOB_ID
#
# Resume: The download script supports resume. If the job is interrupted
# (timeout, network error, etc.), simply resubmit this script. Previously
# downloaded files will be skipped.
###############################################################################

set -euo pipefail

echo "============================================================"
echo "Tahoe-100M Download Job"
echo "  Job ID:    ${SLURM_JOB_ID}"
echo "  Node:      $(hostname)"
echo "  Start:     $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "  Partition:  ${SLURM_JOB_PARTITION}"
echo "  CPUs:       ${SLURM_CPUS_PER_TASK}"
echo "  Memory:     ${SLURM_MEM_PER_NODE}MB"
echo "============================================================"

# Load conda and activate download environment
module purge
module load miniconda/24.11.3
source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-tahoe-download

# Verify environment
echo ""
echo "Environment check:"
python --version
python -c "import huggingface_hub; print(f'  huggingface_hub: {huggingface_hub.__version__}')"
python -c "import datasets; print(f'  datasets: {datasets.__version__}')"
python -c "import pyarrow; print(f'  pyarrow: {pyarrow.__version__}')"
echo ""

# Check scratch space before starting
echo "Scratch space:"
df -h /nfs/roberts/scratch/pi_mg269/rag88/
echo ""

# Set HF cache to scratch to avoid filling home directory
export HF_HOME=/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/.hf_cache
export HF_HUB_ENABLE_HF_TRANSFER=1
mkdir -p "${HF_HOME}"

# Run the download script
SCRIPT_DIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/output"
python "${SCRIPT_DIR}/task-002-download-script.py"

EXIT_CODE=$?

echo ""
echo "============================================================"
echo "Download finished"
echo "  Exit code: ${EXIT_CODE}"
echo "  End time:  $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo ""
echo "Scratch space after download:"
df -h /nfs/roberts/scratch/pi_mg269/rag88/
echo ""
echo "Data directory size:"
du -sh /nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/ 2>/dev/null || echo "  (not found)"
echo "============================================================"

exit ${EXIT_CODE}
