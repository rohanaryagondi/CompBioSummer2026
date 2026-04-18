#!/bin/bash
#SBATCH --job-name=b2m5tn8w
#SBATCH --partition=scavenge_gpu
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --time=04:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --requeue
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/mace_hybrid_ubq_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/mace_hybrid_ubq_%j.err

# =============================================================================
# Deliverable 2: OpenCL throughput benchmark on ubiquitin (Tier B, 76 aa,
# ~1,200 MACE atoms, ~8,500 total atoms). Validates Subagent A's projected
# 0.60 ns/day for ubiquitin hybrid mode. 20 ps equilibration + 50 ps production
# is sufficient to extrapolate ns/day. 4 hr wall time cap.
# =============================================================================

echo "=========================================="
echo "MACE hybrid UBQ  |  SLURM $SLURM_JOB_ID"
echo "Node: $(hostname)"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo 'unknown')"
echo "Date: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "=========================================="

# -- Paths -------------------------------------------------------------------
ENV_DIR=/home/rag88/.conda/envs/env-mace
ENV_PYTHON=${ENV_DIR}/bin/python

SCRIPT_DIR=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts
OUTPUT_DIR=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output
SCRATCH_DIR=/nfs/roberts/scratch/pi_mg269/rag88/mace-hybrid

export PYTHONNOUSERSITE=1

# -- Env verification (non-fatal) -------------------------------------------
echo ""
echo "=== Env verification ==="
${ENV_PYTHON} -c "
import openmm, torch
print('torch:', torch.__version__, '| cuda_avail:', torch.cuda.is_available())
print('openmm:', openmm.__version__)
for i in range(openmm.Platform.getNumPlatforms()):
    p = openmm.Platform.getPlatform(i)
    print(f'  Platform {i}: {p.getName()} (speed {p.getSpeed()})')
" || echo "WARNING: env verification issues, continuing anyway..."

# -- Run --------------------------------------------------------------------
echo ""
echo "=== Running MACE hybrid NVT on ubiquitin (1UBQ, 76 aa) ==="
export MACE_HYBRID_PROTEIN=ubq
export MACE_HYBRID_PDB=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ubq.pdb
export MACE_HYBRID_RESRANGE=""
export MACE_HYBRID_EQUIL_PS=20
export MACE_HYBRID_PROD_PS=50
export MACE_HYBRID_TAG=ubq
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
