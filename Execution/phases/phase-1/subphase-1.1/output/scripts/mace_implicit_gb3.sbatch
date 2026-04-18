#!/bin/bash
#SBATCH --job-name=q8w4vh3t
#SBATCH --partition=gpu
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --time=04:00:00
#SBATCH --mem=24G
#SBATCH --cpus-per-task=4
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/mace_implicit_gb3_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/mace_implicit_gb3_%j.err

# =============================================================================
# Option 4 pilot: MACE-OFF24 + GBn2 implicit solvent NVT on GB3 (56 aa).
# BMRB 5839 S2-bearing protein — complements WW pilot by testing a moderately
# larger protein (GB3 is the S2 reference in Hall & Fushman 2003). Compare
# against explicit-hybrid GB3: 0.111 ns/day (job 8736921).
#
# Cryptic job name (YCRC feedback_cryptic_job_names policy).
# =============================================================================

echo "=========================================="
echo "MACE implicit GB3  |  SLURM $SLURM_JOB_ID"
echo "Node: $(hostname)"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo 'unknown')"
echo "Date: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "=========================================="

ENV_DIR=/home/rag88/.conda/envs/env-mace
ENV_PYTHON=${ENV_DIR}/bin/python

SCRIPT_DIR=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts
OUTPUT_DIR=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output
SCRATCH_DIR=/nfs/roberts/scratch/pi_mg269/rag88/mace-implicit

export PYTHONNOUSERSITE=1

echo ""
echo "=== Running MACE + GBn2 implicit on GB3 (PDB 1P7E, 56 aa) ==="
export MACE_IMPL_PROTEIN=gb3
export MACE_IMPL_PDB=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/gb3.pdb
export MACE_IMPL_RESRANGE=
export MACE_IMPL_MODEL=gbn2
export MACE_IMPL_EQUIL_PS=30
export MACE_IMPL_PROD_PS=60
export MACE_IMPL_TAG=gb3
export MACE_OUTPUT_DIR=${OUTPUT_DIR}
export MACE_SCRATCH_DIR=${SCRATCH_DIR}

set -uo pipefail
${ENV_PYTHON} ${SCRIPT_DIR}/mace_implicit_nvt.py
EXIT_CODE=$?

echo ""
echo "=========================================="
echo "Exit: $EXIT_CODE"
echo "Verdict: $([ $EXIT_CODE -eq 0 ] && echo 'PASS' || echo 'FAIL')"
echo "Completed: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "=========================================="

exit $EXIT_CODE
