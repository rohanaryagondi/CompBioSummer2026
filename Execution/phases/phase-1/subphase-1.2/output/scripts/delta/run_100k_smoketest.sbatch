#!/bin/bash
#SBATCH --job-name=dx7k9pq2
#SBATCH --partition=gpu
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:30:00
#SBATCH --account=pi_mg269
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/slurm_logs/dx7k9pq2_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/slurm_logs/dx7k9pq2_%j.err
# Delta baselines 100K-cell Tahoe-100M smoke test (Sub 1.2 task-005).
# RTX 5000 Ada @ 15 SU/hr, 2.5 h walltime cap => ~38 SU worst case.

set -euo pipefail

export PYTHONNOUSERSITE=1
export HF_HOME=/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/.hf_cache
PYBIN=/home/rag88/.conda/envs/env-delta-v2/bin/python
SCRIPTS=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts
OUT=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output

cd "$SCRIPTS"
$PYBIN -c "import numpy, sklearn, scipy, pandas, statsmodels; print('env ok')"

$PYBIN -m delta.eval.run_smoketest \
    --subsample 100000 \
    --n-top-genes 2000 \
    --top-k-perts 25 \
    --baselines linear,mean,pca,random,persistence \
    --methods none \
    --max-parquets 80 \
    --n-perm 100 \
    --out-dir "$OUT"
