#!/bin/bash
###############################################################################
# SO3LR Rescue SLURM Template (Task 002 Rescue, Subphase 1.2)
#
# Fork of so3lr_pilot.sbatch with rescue-specific knobs piped through to the
# runner. Used for both 500 ps gates (priority queue) and 5 ns full rescues
# (Standard Tier preferred). Per-protein parameters are set via --export.
#
# Inputs (all via --export, with defaults):
#   PROTEIN       — ww | gb3 | ntl9 (any of {ww, gb3, gb1, ntl9, ubq})
#   MODE          — run | restart                                    (run)
#   TARGET_NS     — float                                            (0.5)
#   DT_FS         — float                                            (0.5)
#   PRECISION     — float32 | float64                                (float32)
#   NHC_CHAIN     — int                                              (3)
#   NHC_THERMO    — float (Tdamp in dt units)                        (100.0)
#   INPUT_XYZ     — absolute path to alt XYZ (e.g., neutral)         ("")
#   OUTPUT_SUBDIR — relative subdir under output/trajectories/       ("so3lr_vacuum_rescue")
#   ACCOUNT       — SLURM account                                    (pi_mg269)
#   PARTITION     — SLURM partition                                  (gpu)
#
# Per shared/notes/operational-practices.md:
#   - Cryptic 8-char alphanumeric job name (set via sbatch --job-name)
#   - RTX 5000 Ada (gpu / priority_gpu) for SO3LR (vacuum, tiny VRAM)
#   - env-so3lr contract: PYTHONNOUSERSITE=0 + user-site appended to PYTHONPATH
###############################################################################
# Note: --gpus= and --time are set by the submitter via sbatch CLI flags so
# they can be overridden per-partition (priority_gpu requires --gpus=
# specification per node-type, while standard `gpu` accepts --gres=gpu:1).
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G

# Defaults (can be overridden via --export)
PROTEIN="${PROTEIN:-ww}"
MODE="${MODE:-run}"
TARGET_NS="${TARGET_NS:-0.5}"
DT_FS="${DT_FS:-0.5}"
PRECISION="${PRECISION:-float32}"
NHC_CHAIN="${NHC_CHAIN:-3}"
NHC_THERMO="${NHC_THERMO:-100.0}"
INPUT_XYZ="${INPUT_XYZ:-}"
OUTPUT_SUBDIR="${OUTPUT_SUBDIR:-so3lr_vacuum_rescue}"

REPO_ROOT="/home/rag88/projects/CompBioSummer2026"
SUBPHASE_ROOT="${REPO_ROOT}/Execution/phases/phase-1/subphase-1.2"
OUTPUT_DIR="${SUBPHASE_ROOT}/output/trajectories/${OUTPUT_SUBDIR}"
RUNNER="${SUBPHASE_ROOT}/output/scripts/so3lr_rescue_runner.py"
LOG_DIR="${OUTPUT_DIR}/${PROTEIN}"
mkdir -p "${LOG_DIR}"

# SLURM output paths
exec > "${LOG_DIR}/slurm-${SLURM_JOB_ID}.out" 2> "${LOG_DIR}/slurm-${SLURM_JOB_ID}.err"

echo "=============================="
echo "SO3LR Rescue - Job ${SLURM_JOB_ID}"
echo "Protein:    ${PROTEIN}"
echo "Mode:       ${MODE}"
echo "Target ns:  ${TARGET_NS}"
echo "dt (fs):    ${DT_FS}"
echo "Precision:  ${PRECISION}"
echo "NHC chain:  ${NHC_CHAIN}"
echo "NHC thermo: ${NHC_THERMO}"
echo "Input XYZ:  ${INPUT_XYZ:-<default-pilot-input>}"
echo "Output:     ${LOG_DIR}"
echo "Account:    ${SLURM_JOB_ACCOUNT:-?}"
echo "Partition:  ${SLURM_JOB_PARTITION:-?}"
echo "Node:       $(hostname)"
echo "Date:       $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "GPU:        $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'unknown')"
echo "=============================="

# --- Environment setup ---
module purge
module load miniconda
conda activate env-so3lr

# env-so3lr contract: do NOT set PYTHONNOUSERSITE=1. The env relies on
# user-site for typing_extensions, rich, pandas, pyyaml, dateutil. See
# shared/notes/1.2-env-so3lr-typing-extensions-fix.md.
export PYTHONNOUSERSITE=0
export PYTHONPATH="${CONDA_PREFIX}/lib/python3.12/site-packages:/home/rag88/.local/lib/python3.12/site-packages:${PYTHONPATH:-}"

# JAX_ENABLE_X64 is set by the runner when --precision=float64. We leave it
# unset here to avoid float64 leaking into float32 jobs.

# JAX persistent compilation cache — cuts JIT compile from 30-60 s to 1-2 s on
# subsequent runs. Lossless, shared across all SO3LR launches. Per subagent B.
export JAX_COMPILATION_CACHE_DIR="/home/rag88/.cache/jax_compilation"
export JAX_PERSISTENT_CACHE_MIN_ENTRY_SIZE_BYTES=0
mkdir -p "${JAX_COMPILATION_CACHE_DIR}"

# XLA optimizations: Triton GEMM emitter for irregular-shape matmul (SO3LR
# tensor products) + latency-hiding scheduler. Lossless. Per deeper-opt-hunter A1.
export XLA_FLAGS="--xla_gpu_triton_gemm_any=true --xla_gpu_enable_latency_hiding_scheduler=true"

echo "Python:     $(which python)"
echo "Python ver: $(python --version 2>&1)"
python -c "import numpy; print('numpy:', numpy.__version__, '@', numpy.__file__)"
python -c "import so3lr; print('SO3LR:', so3lr.__version__)"
python -c "import jax; print('JAX:', jax.__version__, 'backend:', jax.default_backend(), 'devices:', jax.devices())"

nvidia-smi

# --- Run ---
echo ""
echo "============================================"
echo "STEP: SO3LR ${MODE} @ ${TARGET_NS} ns for ${PROTEIN}"
echo "  (dt=${DT_FS} fs, precision=${PRECISION}, nhc=${NHC_CHAIN}/${NHC_THERMO})"
echo "Start: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"

INPUT_XYZ_ARG=""
if [ -n "${INPUT_XYZ}" ]; then
    INPUT_XYZ_ARG="--input-xyz ${INPUT_XYZ}"
fi

python "${RUNNER}" \
    --protein "${PROTEIN}" \
    --mode "${MODE}" \
    --target-ns "${TARGET_NS}" \
    --dt-fs "${DT_FS}" \
    --precision "${PRECISION}" \
    --nhc-chain "${NHC_CHAIN}" \
    --nhc-thermo "${NHC_THERMO}" \
    ${INPUT_XYZ_ARG} \
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
