#!/bin/bash
###############################################################################
# SO3LR Pilot SLURM Template (Task 002, Subphase 1.2)
#
# Runs 5 ns vacuum NVT on one Tier A/B protein via the `so3lr nvt` CLI.
# One job per protein. Target partition: `gpu` (RTX 5000 Ada, 15 SU/hr).
#
# Usage:
#   sbatch --job-name=<cryptic-8char> \
#          --export=PROTEIN=<ww|gb3|gb1|ntl9|ubq>,MODE=<run|restart>,TARGET_NS=<float> \
#          output/scripts/so3lr_pilot.sbatch
#
# The submit_so3lr_pilot.sh wrapper sets all of these automatically.
#
# Per shared/notes/operational-practices.md:
#   - Cryptic 8-char alphanumeric job name (never descriptive)
#   - RTX 5000 Ada default for SO3LR (vacuum, tiny VRAM)
#   - For env-so3lr: DO NOT set PYTHONNOUSERSITE=1. The env relies on user-site
#     site-packages for several transitive deps (typing_extensions, pandas,
#     rich, pyyaml, dateutil, etc.). This matches the Sub 1.1 working pattern
#     (so3lr_crambin_v5.sbatch / so3lr_crambin_cli.sbatch). The MACE env has
#     the opposite contract (numpy must be from conda, user-site must be off).
###############################################################################
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=1-00:00:00
#SBATCH --account=pi_mg269

# Defaults (can be overridden via --export)
PROTEIN="${PROTEIN:-ww}"
MODE="${MODE:-run}"
TARGET_NS="${TARGET_NS:-5.0}"

REPO_ROOT="/home/rag88/projects/CompBioSummer2026"
SUBPHASE_ROOT="${REPO_ROOT}/Execution/phases/phase-1/subphase-1.2"
OUTPUT_DIR="${SUBPHASE_ROOT}/output/trajectories/so3lr_vacuum"
RUNNER="${SUBPHASE_ROOT}/output/scripts/so3lr_pilot_runner.py"
LOG_DIR="${OUTPUT_DIR}/${PROTEIN}"
mkdir -p "${LOG_DIR}"

# SLURM output paths (redirect because we override partition default)
exec > "${LOG_DIR}/slurm-${SLURM_JOB_ID}.out" 2> "${LOG_DIR}/slurm-${SLURM_JOB_ID}.err"

echo "=============================="
echo "SO3LR Pilot - Job ${SLURM_JOB_ID}"
echo "Protein: ${PROTEIN}"
echo "Mode: ${MODE}"
echo "Target ns: ${TARGET_NS}"
echo "Node: $(hostname)"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Partition: ${SLURM_JOB_PARTITION}"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'unknown')"
echo "=============================="

# --- Environment setup ---
module purge
module load miniconda
conda activate env-so3lr

# CRITICAL for env-so3lr (per Sub 1.1 so3lr_crambin_v5.sbatch working pattern):
# ALLOW user-site packages — env-so3lr's transitive deps (typing_extensions,
# pandas, rich, pyyaml, dateutil, ...) live in the user site. Setting
# PYTHONNOUSERSITE=1 here causes ModuleNotFoundError at `import flax.linen`.
# The env's own site-packages (numpy etc) still takes precedence because it is
# prepended first via CONDA_PREFIX on PYTHONPATH.
export PYTHONNOUSERSITE=0
export PYTHONPATH="${CONDA_PREFIX}/lib/python3.12/site-packages:/home/rag88/.local/lib/python3.12/site-packages:${PYTHONPATH:-}"

echo "Python: $(which python)"
echo "Python version: $(python --version 2>&1)"
python -c "import numpy; print('numpy:', numpy.__version__, numpy.__file__)"
python -c "import so3lr; print('SO3LR:', so3lr.__version__)"
python -c "import jax; print('JAX:', jax.__version__); print('JAX backend:', jax.default_backend()); print('JAX devices:', jax.devices())"

nvidia-smi

# --- Run ---
echo ""
echo "============================================"
echo "STEP: SO3LR ${MODE} @ ${TARGET_NS} ns for ${PROTEIN}"
echo "Start: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"

python "${RUNNER}" \
    --protein "${PROTEIN}" \
    --mode "${MODE}" \
    --target-ns "${TARGET_NS}" \
    --output-dir "${OUTPUT_DIR}"

EXIT_CODE=$?

echo ""
echo "============================================"
echo "EXIT ${EXIT_CODE}"
echo "End: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"
echo ""
echo "Output files in ${LOG_DIR}:"
ls -lh "${LOG_DIR}/"

exit ${EXIT_CODE}
