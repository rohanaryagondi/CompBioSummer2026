#!/bin/bash
###############################################################################
# SO3LR rescue DIAGNOSTIC — 5 ps validation run for GB3 neutral XYZ.
#
# Per the diagnostic-first rule (operational-practices.md):
# Before committing 19 priority SU on the 3 rescue gates, validate that the
# rescue_runner + neutral-prep XYZ + sbatch infrastructure works end-to-end
# on a small target. 5 ps target = 10 cycles = ~30 sec wall time.
#
# Submitted to standard `gpu` partition with cryptic name. Costs <1 SU.
###############################################################################
#SBATCH --job-name=d3n7q4xm
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --account=pi_mg269

REPO_ROOT="/home/rag88/projects/CompBioSummer2026"
SUBPHASE_ROOT="${REPO_ROOT}/Execution/phases/phase-1/subphase-1.2"
NEUTRAL_DIR="${SUBPHASE_ROOT}/output/trajectories/so3lr_vacuum_neutral"
DIAG_DIR="${SUBPHASE_ROOT}/output/trajectories/so3lr_vacuum_rescue_diag"
RUNNER="${SUBPHASE_ROOT}/output/scripts/so3lr_rescue_runner.py"

mkdir -p "${DIAG_DIR}/gb3"
exec > "${DIAG_DIR}/gb3/slurm-${SLURM_JOB_ID}.out" 2> "${DIAG_DIR}/gb3/slurm-${SLURM_JOB_ID}.err"

echo "==== DIAGNOSTIC: SO3LR rescue runner, GB3 neutral, 5 ps ===="
echo "Job ${SLURM_JOB_ID}, node $(hostname), $(date -u +%Y-%m-%dT%H:%M:%SZ)"
nvidia-smi --query-gpu=name,memory.free --format=csv,noheader

module purge
module load miniconda
conda activate env-so3lr
export PYTHONNOUSERSITE=0
export PYTHONPATH="${CONDA_PREFIX}/lib/python3.12/site-packages:/home/rag88/.local/lib/python3.12/site-packages:${PYTHONPATH:-}"

python -c "import so3lr; import jax; print('SO3LR', so3lr.__version__, 'JAX', jax.__version__, 'backend', jax.default_backend(), jax.devices())"

# Tiny target: 5 ps = 10 cycles × 1000 steps × 0.5 fs.
python "${RUNNER}" \
    --protein gb3 \
    --mode run \
    --target-ns 0.005 \
    --dt-fs 0.5 \
    --precision float32 \
    --nhc-chain 3 \
    --nhc-thermo 100.0 \
    --input-xyz "${NEUTRAL_DIR}/gb3/input_neutral.xyz" \
    --output-dir "${DIAG_DIR}"

EXIT_CODE=$?

echo ""
echo "==== DIAGNOSTIC EXIT ${EXIT_CODE} ===="
ls -lh "${DIAG_DIR}/gb3/"
exit ${EXIT_CODE}
