#!/bin/bash
#SBATCH --job-name=h8xscfn1
#SBATCH --partition=gpu_devel
#SBATCH --gpus=rtx_5000_ada:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=00:30:00
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err

set -euo pipefail

module purge
module load miniconda/24.11.3
source activate env-delta-v2
export PYTHONNOUSERSITE=1

cd /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/delta-tier1

python -u scfoundation_smoketest.py
