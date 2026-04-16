#!/bin/bash
#SBATCH --job-name=so3lr_cli
#SBATCH --partition=gpu_devel
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/so3lr_cli_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/so3lr_cli_%j.err

###############################################################################
# SO3LR Crambin NVT -- CLI-based approach (D1 gate evidence)
#
# Strategy:
#   1. Quick sanity test: 10 ps NVT with --relax (20 cycles x 1000 steps x 0.5 fs)
#   2. Stage A: 100 ps NVT (200 cycles x 1000 steps x 0.5 fs) -- D1 minimum
#   3. Stage B: 1 ns NVT (2000 cycles x 1000 steps x 0.5 fs) -- D1 target
#
# Uses the so3lr CLI which handles neighbor lists, thermostat, JIT, checkpoints.
###############################################################################

echo "=============================="
echo "SO3LR Crambin NVT (CLI) - Job $SLURM_JOB_ID"
echo "Node: $(hostname)"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Partition: $SLURM_JOB_PARTITION"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'unknown')"
echo "=============================="

# --- Environment setup ---
module purge
module load miniconda
conda activate env-so3lr

# Ensure user site-packages are on the path (numpy, etc. may be installed there)
export PYTHONPATH="/home/rag88/.local/lib/python3.12/site-packages:${PYTHONPATH}"
export PYTHONNOUSERSITE=0

echo "Python: $(which python)"
echo "Python version: $(python --version 2>&1)"
python -c "import numpy; print('numpy:', numpy.__version__, numpy.__file__)"
python -c "import so3lr; print('SO3LR:', so3lr.__version__)"
python -c "import jax; print('JAX:', jax.__version__); print('JAX devices:', jax.devices()); print('Backend:', jax.default_backend())"

nvidia-smi

# --- Paths ---
BASEDIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output"
SCRATCH="/nfs/roberts/scratch/pi_mg269/rag88/alpha-m/so3lr-crambin"
INPUT="${BASEDIR}/crambin_h_vacuum.xyz"

cd "${SCRATCH}"

echo ""
echo "Input file: ${INPUT}"
python -c "from ase.io import read; a=read('${INPUT}'); print(f'{len(a)} atoms, formula={a.get_chemical_formula()}')"

if [ $? -ne 0 ]; then
    echo "ERROR: Cannot read input file"
    exit 1
fi

# =========================================================================
# Step 1: Quick sanity test (10 ps with geometry relaxation)
# 20 cycles x 1000 steps x 0.5 fs = 10 ps
# =========================================================================
echo ""
echo "============================================"
echo "STEP 1: Quick 10 ps NVT test (with --relax)"
echo "Start: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"

so3lr nvt \
    --input "${INPUT}" \
    --output "${SCRATCH}/test_10ps.hdf5" \
    --dt 0.5 \
    --temperature 300 \
    --md-cycles 20 \
    --md-steps 1000 \
    --relax \
    --force-conv 0.05 \
    --seed 42 \
    --precision float32 \
    --lr-cutoff 12.0 \
    --save-buffer 10 \
    --log-file "${SCRATCH}/test_10ps.log" \
    --restart-save "${SCRATCH}/test_10ps_checkpoint.npz"

TEST_EXIT=$?
echo "10 ps test exit code: ${TEST_EXIT}"
echo "End: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [ ${TEST_EXIT} -ne 0 ]; then
    echo ">>> 10 ps test FAILED. Trying without --relax..."

    so3lr nvt \
        --input "${INPUT}" \
        --output "${SCRATCH}/test_10ps_norelax.hdf5" \
        --dt 0.5 \
        --temperature 300 \
        --md-cycles 20 \
        --md-steps 1000 \
        --no-relax \
        --seed 42 \
        --precision float32 \
        --lr-cutoff 12.0 \
        --save-buffer 10 \
        --log-file "${SCRATCH}/test_10ps_norelax.log" \
        --restart-save "${SCRATCH}/test_10ps_norelax_checkpoint.npz"

    TEST_EXIT=$?
    echo "10 ps test (no relax) exit code: ${TEST_EXIT}"

    if [ ${TEST_EXIT} -ne 0 ]; then
        echo ">>> 10 ps test FAILED both with and without relax."
        echo ">>> Trying with float64 precision and smaller timestep..."

        so3lr nvt \
            --input "${INPUT}" \
            --output "${SCRATCH}/test_10ps_f64.hdf5" \
            --dt 0.25 \
            --temperature 300 \
            --md-cycles 40 \
            --md-steps 1000 \
            --relax \
            --force-conv 0.01 \
            --seed 42 \
            --precision float64 \
            --lr-cutoff 12.0 \
            --save-buffer 10 \
            --log-file "${SCRATCH}/test_10ps_f64.log" \
            --restart-save "${SCRATCH}/test_10ps_f64_checkpoint.npz"

        TEST_EXIT=$?
        echo "10 ps test (float64, dt=0.25) exit code: ${TEST_EXIT}"

        if [ ${TEST_EXIT} -ne 0 ]; then
            echo ">>> ALL 10 ps tests FAILED. D1 = FAIL for SO3LR."
            echo "FINAL_STATUS=FAIL" > "${SCRATCH}/run_status.txt"
            exit 0
        fi
    fi
fi

echo ">>> 10 ps test PASSED."

# =========================================================================
# Step 2: Stage A -- 100 ps NVT (D1 minimum acceptable)
# 200 cycles x 1000 steps x 0.5 fs = 100 ps
# =========================================================================
echo ""
echo "============================================"
echo "STEP 2: Stage A -- 100 ps NVT"
echo "Start: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"

so3lr nvt \
    --input "${INPUT}" \
    --output "${SCRATCH}/stageA.hdf5" \
    --dt 0.5 \
    --temperature 300 \
    --md-cycles 200 \
    --md-steps 1000 \
    --relax \
    --force-conv 0.05 \
    --seed 42 \
    --precision float32 \
    --lr-cutoff 12.0 \
    --save-buffer 50 \
    --log-file "${SCRATCH}/stageA.log" \
    --restart-save "${SCRATCH}/stageA_checkpoint.npz"

STAGEA_EXIT=$?
echo "Stage A exit code: ${STAGEA_EXIT}"
echo "End: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [ ${STAGEA_EXIT} -ne 0 ]; then
    echo ">>> Stage A FAILED. D1 minimum not met."
    echo "FINAL_STATUS=STAGE_A_FAIL" > "${SCRATCH}/run_status.txt"
    # Still continue to record partial data
    exit 0
fi

echo ">>> Stage A (100 ps) PASSED. Proceeding to Stage B."

# =========================================================================
# Step 3: Stage B -- 1 ns NVT (D1 target)
# 2000 cycles x 1000 steps x 0.5 fs = 1 ns
# Uses restart from Stage A checkpoint
# =========================================================================
echo ""
echo "============================================"
echo "STEP 3: Stage B -- 1 ns NVT (restart from Stage A)"
echo "Start: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"

so3lr nvt \
    --input "${INPUT}" \
    --output "${SCRATCH}/stageB.hdf5" \
    --dt 0.5 \
    --temperature 300 \
    --md-cycles 1800 \
    --md-steps 1000 \
    --no-relax \
    --seed 42 \
    --precision float32 \
    --lr-cutoff 12.0 \
    --save-buffer 50 \
    --log-file "${SCRATCH}/stageB.log" \
    --restart-load "${SCRATCH}/stageA_checkpoint.npz" \
    --restart-save "${SCRATCH}/stageB_checkpoint.npz"

STAGEB_EXIT=$?
echo "Stage B exit code: ${STAGEB_EXIT}"
echo "End: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [ ${STAGEB_EXIT} -ne 0 ]; then
    echo ">>> Stage B FAILED. But Stage A passed, so D1 minimum met."
    echo "FINAL_STATUS=STAGE_A_PASS_STAGE_B_FAIL" > "${SCRATCH}/run_status.txt"
else
    echo ">>> Stage B (1 ns) PASSED. Full D1 target met."
    echo "FINAL_STATUS=FULL_PASS" > "${SCRATCH}/run_status.txt"
fi

# =========================================================================
# Final summary
# =========================================================================
echo ""
echo "=============================="
echo "FINAL SUMMARY"
echo "10ps test:  exit=${TEST_EXIT}"
echo "Stage A:    exit=${STAGEA_EXIT}"
echo "Stage B:    exit=${STAGEB_EXIT}"
echo ""
echo "Files in scratch:"
ls -lh "${SCRATCH}/"
echo ""
echo "Job completed at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=============================="
