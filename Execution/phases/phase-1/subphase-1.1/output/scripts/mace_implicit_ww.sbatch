#!/bin/bash
#SBATCH --job-name=x2n7fp5k
#SBATCH --partition=gpu_devel
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --time=04:00:00
#SBATCH --mem=24G
#SBATCH --cpus-per-task=4
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/mace_implicit_ww_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/mace_implicit_ww_%j.err

# =============================================================================
# Option 4 pilot: MACE-OFF24 + GBn2 implicit solvent NVT on Pin1 WW (34 aa).
# Tests whether replacing ~7K explicit TIP3P-FB water atoms with a continuum
# dielectric restores Phase 2 MACE throughput on OpenCL RTX 5000 Ada.
#
# Compare against explicit-hybrid WW: 0.184 ns/day (job 8736919).
# Target: >1 ns/day (implicit) -> Phase 2 IP scope becomes feasible.
#
# Cryptic job name (YCRC feedback_cryptic_job_names policy).
# =============================================================================

echo "=========================================="
echo "MACE implicit WW  |  SLURM $SLURM_JOB_ID"
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

# -- Env verification --------------------------------------------------------
echo ""
echo "=== Env verification ==="
${ENV_PYTHON} -c "
import openmm, torch
print('torch:', torch.__version__, '| cuda_avail:', torch.cuda.is_available())
print('openmm:', openmm.__version__, '| PythonForce:', hasattr(openmm, 'PythonForce'))
for i in range(openmm.Platform.getNumPlatforms()):
    p = openmm.Platform.getPlatform(i)
    print(f'  Platform {i}: {p.getName()} (speed {p.getSpeed()})')
from openmm.app import ForceField
ff = ForceField('amber14-all.xml', 'implicit/gbn2.xml')
print('ForceField amber14-all + implicit/gbn2.xml: OK')
" || echo "WARNING: env verification issues, continuing anyway..."

# -- Run --------------------------------------------------------------------
echo ""
echo "=== Running MACE + GBn2 implicit on WW domain (residues 6-39 of 2F21) ==="
export MACE_IMPL_PROTEIN=ww
export MACE_IMPL_PDB=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ww.pdb
export MACE_IMPL_RESRANGE=6-39
export MACE_IMPL_MODEL=gbn2
export MACE_IMPL_EQUIL_PS=30
export MACE_IMPL_PROD_PS=60
export MACE_IMPL_TAG=ww
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
