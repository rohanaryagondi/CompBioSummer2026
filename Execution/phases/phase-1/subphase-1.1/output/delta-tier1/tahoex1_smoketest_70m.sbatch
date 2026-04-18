#!/bin/bash
#SBATCH --job-name=z2qtx170
#SBATCH --partition=gpu_devel
#SBATCH --gpus=rtx_5000_ada:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=00:45:00
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err

set -euo pipefail

module purge
module load miniconda/24.11.3
source activate env-tahoex1
export PYTHONNOUSERSITE=1
export HF_HOME=/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/.hf_cache

cd /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/delta-tier1

python -u tahoex1_smoketest.py --model-size 70m --n-cells 100
