#!/bin/bash
#SBATCH --job-name=bioemu-ss-test
#SBATCH --partition=gpu_devel
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/output/task-004-bioemu-%j.log
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/output/task-004-bioemu-%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=amita4171@gmail.com

###############################################################################
# BioEmu Disulfide Bond Test (Task 004)
#
# Generates 100 BioEmu conformations each for BPTI and HEWL, measures SS
# distances, computes integrity metrics, and writes the T3/AK3 assessment.
#
# Expected runtime: 30-120 minutes depending on GPU and MSA computation.
###############################################################################

set -euo pipefail

echo "============================================================"
echo "BioEmu Disulfide Bond Test (Task 004)"
echo "  Job ID:    ${SLURM_JOB_ID}"
echo "  Node:      $(hostname)"
echo "  Start:     $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "  Partition:  ${SLURM_JOB_PARTITION}"
echo "  GPUs:       ${SLURM_GPUS_ON_NODE:-1}"
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
python -c "import torch; print(f'  torch: {torch.__version__}'); print(f'  CUDA available: {torch.cuda.is_available()}')"
python -c "import mdtraj; print(f'  mdtraj: {mdtraj.__version__}')"
echo ""

# Set caches to scratch to avoid filling home directory
export HF_HOME=/nfs/roberts/scratch/pi_mg269/rag88/.hf_cache
export BIOEMU_EMBEDS_CACHE=/nfs/roberts/scratch/pi_mg269/rag88/.bioemu_embeds_cache
mkdir -p "${HF_HOME}" "${BIOEMU_EMBEDS_CACHE}"

# Fix protobuf conflict between tensorflow-cpu and jax/xla
# Both register xla/xla_data.proto; pure-Python impl avoids the C++ crash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Set MPLBACKEND to avoid display issues
export MPLBACKEND=Agg

# Run the analysis script
SCRIPT_DIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/output"
python "${SCRIPT_DIR}/task-004-bioemu-analysis.py"

EXIT_CODE=$?

echo ""
echo "============================================================"
echo "BioEmu test finished"
echo "  Exit code: ${EXIT_CODE}"
echo "  End time:  $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "============================================================"

exit ${EXIT_CODE}
