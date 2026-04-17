#!/bin/bash
#SBATCH --job-name=so3lr_qt
#SBATCH --partition=gpu_devel
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/so3lr_quicktest_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/so3lr_quicktest_%j.err

###############################################################################
# SO3LR Quick Test: 10 ps NVT on crambin via CLI
# Purpose: Validate the CLI works before the full production run
###############################################################################

echo "=============================="
echo "SO3LR Quick Test - Job $SLURM_JOB_ID"
echo "Node: $(hostname)"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=============================="

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

BASEDIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output"
SCRATCH="/nfs/roberts/scratch/pi_mg269/rag88/alpha-m/so3lr-crambin"
INPUT="${BASEDIR}/crambin_h_vacuum.xyz"

cd "${SCRATCH}"

echo ""
echo "Input: ${INPUT}"
python -c "from ase.io import read; a=read('${INPUT}'); print(f'{len(a)} atoms, formula={a.get_chemical_formula()}')"

# ---- Test 1: 10 ps with geometry relaxation ----
echo ""
echo "=== Test 1: 10 ps NVT with --relax ==="
echo "Start: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

so3lr nvt \
    --input "${INPUT}" \
    --output "${SCRATCH}/quicktest_relax.hdf5" \
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
    --log-file "${SCRATCH}/quicktest_relax.log"

T1_EXIT=$?
echo "Test 1 exit: ${T1_EXIT}"
echo "End: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [ ${T1_EXIT} -ne 0 ]; then
    echo ">>> Test 1 FAILED. Trying without --relax..."

    # ---- Test 2: 10 ps without relaxation ----
    echo ""
    echo "=== Test 2: 10 ps NVT with --no-relax ==="
    so3lr nvt \
        --input "${INPUT}" \
        --output "${SCRATCH}/quicktest_norelax.hdf5" \
        --dt 0.5 \
        --temperature 300 \
        --md-cycles 20 \
        --md-steps 1000 \
        --no-relax \
        --seed 42 \
        --precision float32 \
        --lr-cutoff 12.0 \
        --save-buffer 10 \
        --log-file "${SCRATCH}/quicktest_norelax.log"

    T2_EXIT=$?
    echo "Test 2 exit: ${T2_EXIT}"

    if [ ${T2_EXIT} -ne 0 ]; then
        echo ">>> Test 2 also FAILED. Trying float64 + smaller dt..."

        # ---- Test 3: float64, dt=0.25 ----
        echo ""
        echo "=== Test 3: 10 ps NVT float64 dt=0.25 ==="
        so3lr nvt \
            --input "${INPUT}" \
            --output "${SCRATCH}/quicktest_f64.hdf5" \
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
            --log-file "${SCRATCH}/quicktest_f64.log"

        T3_EXIT=$?
        echo "Test 3 exit: ${T3_EXIT}"

        if [ ${T3_EXIT} -ne 0 ]; then
            echo ">>> ALL TESTS FAILED."
        fi
    fi
fi

echo ""
echo "=== Scratch contents ==="
ls -lh "${SCRATCH}/"

echo ""
echo "Job completed: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
