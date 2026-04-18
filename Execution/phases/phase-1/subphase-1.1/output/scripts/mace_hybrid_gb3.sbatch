#!/bin/bash
#SBATCH --job-name=m4h9fr6v
#SBATCH --partition=gpu_devel
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --time=04:00:00
#SBATCH --mem=24G
#SBATCH --cpus-per-task=4
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/mace_hybrid_gb3_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/mace_hybrid_gb3_%j.err

# =============================================================================
# MACE hybrid NVT on GB3 (56 aa, BMRB 5839 S2-bearing protein, 0 SS bonds).
# Per Subagent G recommendation: NVT hybrid stability test on an S2-bearing
# protein to cover the Phase 2 use case (WW/ubiquitin don't have the same
# S2 role). Uses tuned minimization (maxIterations=200).
# Policy: RTX 5000 Ada, OpenCL backend, gpu_devel partition (stable priority).
# =============================================================================

echo "=========================================="
echo "MACE hybrid GB3  |  SLURM $SLURM_JOB_ID"
echo "Node: $(hostname)"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo 'unknown')"
echo "Date: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "=========================================="

ENV_DIR=/home/rag88/.conda/envs/env-mace
ENV_PYTHON=${ENV_DIR}/bin/python

SCRIPT_DIR=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts
OUTPUT_DIR=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output
SCRATCH_DIR=/nfs/roberts/scratch/pi_mg269/rag88/mace-hybrid

export PYTHONNOUSERSITE=1

echo ""
echo "=== Running MACE hybrid NVT on GB3 (PDB 1P7E, 56 aa) ==="
export MACE_HYBRID_PROTEIN=gb3
export MACE_HYBRID_PDB=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/gb3.pdb
export MACE_HYBRID_RESRANGE=
export MACE_HYBRID_EQUIL_PS=30
export MACE_HYBRID_PROD_PS=60
export MACE_HYBRID_TAG=gb3
export MACE_OUTPUT_DIR=${OUTPUT_DIR}
export MACE_SCRATCH_DIR=${SCRATCH_DIR}

set -uo pipefail
${ENV_PYTHON} ${SCRIPT_DIR}/mace_hybrid_nvt.py
EXIT_CODE=$?

echo ""
echo "=========================================="
echo "Exit: $EXIT_CODE"
echo "Verdict: $([ $EXIT_CODE -eq 0 ] && echo 'PASS' || echo 'FAIL')"
echo "Completed: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "=========================================="

exit $EXIT_CODE
