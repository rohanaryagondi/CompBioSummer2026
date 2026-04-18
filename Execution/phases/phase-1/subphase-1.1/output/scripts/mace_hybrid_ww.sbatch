#!/bin/bash
#SBATCH --job-name=a7k3xq9p
#SBATCH --partition=scavenge_gpu
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --time=04:00:00
#SBATCH --mem=24G
#SBATCH --cpus-per-task=4
#SBATCH --requeue
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/mace_hybrid_ww_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/mace_hybrid_ww_%j.err

# =============================================================================
# Deliverable 1: MACE hybrid-mode validation on Pin1 WW domain (34 aa).
# Exercises openmmml.MLPotential.createMixedSystem with MACE on protein atoms
# + TIP3P-FB classical water. Policy: RTX 5000 Ada (15 SU/hr vs H200 300 SU/hr),
# OpenCL backend (CUDA verified broken across H200/B200/RTX 5000 Ada).
# =============================================================================

echo "=========================================="
echo "MACE hybrid WW  |  SLURM $SLURM_JOB_ID"
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
from openmmml import MLPotential
p = MLPotential('mace-off24-medium')
print('createMixedSystem attr present:', hasattr(p, 'createMixedSystem'))
try:
    import pdbfixer
    print('pdbfixer: OK')
except ImportError:
    print('pdbfixer: MISSING (fallback to Modeller.addHydrogens)')
" || echo "WARNING: env verification issues, continuing anyway..."

# -- Run --------------------------------------------------------------------
echo ""
echo "=== Running MACE hybrid NVT on WW domain (residues 6-39 of 2F21) ==="
export MACE_HYBRID_PROTEIN=ww
export MACE_HYBRID_PDB=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ww.pdb
export MACE_HYBRID_RESRANGE=6-39
export MACE_HYBRID_EQUIL_PS=50
export MACE_HYBRID_PROD_PS=100
export MACE_HYBRID_TAG=ww
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
