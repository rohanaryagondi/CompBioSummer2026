#!/bin/bash
###############################################################################
# SO3LR Remediation DIAGNOSTIC: dt=0.25 fs, ~50 ps (100 cycles) for WW
#
# Diagnostic-first rule: run a quick test before committing to 2-day production.
# 100 cycles x 1000 steps x 0.25 fs = 25 ps -- enough to verify:
#   1. env-so3lr activates correctly
#   2. so3lr CLI starts and runs with dt=0.25
#   3. No immediate NaN or crash
#   4. Rg check runs on the output HDF5
###############################################################################
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=0-00:15:00
#SBATCH --account=pi_mg269

PROTEIN="${PROTEIN:-ww}"

REPO_ROOT="/home/rag88/projects/CompBioSummer2026"
SUBPHASE_ROOT="${REPO_ROOT}/Execution/phases/phase-1/subphase-1.2"
ORIG_TRAJ="${SUBPHASE_ROOT}/output/trajectories/so3lr_vacuum"
DIAG_ROOT="${SUBPHASE_ROOT}/output/trajectories/so3lr_vacuum_dt025_diag"
PROTEIN_DIR="${DIAG_ROOT}/${PROTEIN}"
RUNNER="${SUBPHASE_ROOT}/output/scripts/so3lr_pilot_runner.py"
mkdir -p "${PROTEIN_DIR}"

# Copy input.xyz from original run
ORIG_XYZ="${ORIG_TRAJ}/${PROTEIN}/input.xyz"
DIAG_XYZ="${PROTEIN_DIR}/input.xyz"
if [ ! -f "${DIAG_XYZ}" ] && [ -f "${ORIG_XYZ}" ]; then
    cp "${ORIG_XYZ}" "${DIAG_XYZ}"
fi

exec > "${PROTEIN_DIR}/slurm-${SLURM_JOB_ID}.out" 2> "${PROTEIN_DIR}/slurm-${SLURM_JOB_ID}.err"

echo "=============================="
echo "SO3LR Remediation DIAG - Job ${SLURM_JOB_ID}"
echo "Protein: ${PROTEIN}"
echo "dt: 0.25 fs, target: 0.025 ns (100 cycles diagnostic)"
echo "Node: $(hostname)"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'unknown')"
echo "=============================="

module purge
module load miniconda
conda activate env-so3lr

export PYTHONNOUSERSITE=0
export PYTHONPATH="${CONDA_PREFIX}/lib/python3.12/site-packages:/home/rag88/.local/lib/python3.12/site-packages:${PYTHONPATH:-}"

echo "Python: $(which python)"
python -c "import numpy; print('numpy:', numpy.__version__, numpy.__file__)"
python -c "import so3lr; print('SO3LR:', so3lr.__version__)"
python -c "import jax; print('JAX:', jax.__version__); print('JAX backend:', jax.default_backend()); print('JAX devices:', jax.devices())"

nvidia-smi

if [ ! -f "${DIAG_XYZ}" ]; then
    echo "FATAL: Input XYZ not found: ${DIAG_XYZ}"
    exit 99
fi

echo ""
echo "STEP: Diagnostic SO3LR NVT @ dt=0.25 fs, 0.025 ns for ${PROTEIN}"
echo "Start: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# 100 cycles x 1000 steps x 0.25 fs = 25 ps = 0.025 ns
python "${RUNNER}" \
    --protein "${PROTEIN}" \
    --mode run \
    --target-ns 0.025 \
    --dt-fs 0.25 \
    --output-dir "${DIAG_ROOT}"

EXIT_CODE=$?

echo ""
echo "SO3LR CLI EXIT: ${EXIT_CODE}"
echo "End: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Quick Rg check
python << 'PYEOF'
import sys, os, json, glob
import numpy as np

protein = os.environ.get("PROTEIN", "unknown")
diag_root = os.environ.get("DIAG_ROOT", ".")
protein_dir = os.path.join(diag_root, protein)

def compute_rg(positions):
    com = positions.mean(axis=0)
    diff = positions - com
    return np.sqrt(np.mean(np.sum(diff**2, axis=1)))

hdf5_files = sorted(glob.glob(os.path.join(protein_dir, "stage*.hdf5")))
if not hdf5_files:
    print(f"WARNING: No HDF5 found in {protein_dir}")
    json.dump({"protein": protein, "status": "NO_TRAJECTORY"},
              open(os.path.join(protein_dir, "rg_check.json"), "w"), indent=2)
    sys.exit(0)

hdf5_path = hdf5_files[-1]
print(f"Checking Rg in: {hdf5_path}")

try:
    import h5py
    with h5py.File(hdf5_path, "r") as h5:
        keys = list(h5.keys())
        print(f"  HDF5 keys: {keys}")
        pos_key = None
        for k in ["positions", "pos", "R", "trajectory"]:
            if k in h5:
                pos_key = k
                break
        if pos_key is None:
            for k in keys:
                if isinstance(h5[k], h5py.Dataset) and len(h5[k].shape) >= 3:
                    pos_key = k
                    break
        if pos_key is None:
            print("  No positions key found")
            result = {"protein": protein, "status": "UNKNOWN", "hdf5_keys": keys}
        else:
            positions = h5[pos_key]
            print(f"  Dataset '{pos_key}': shape={positions.shape}")
            # SO3LR HDF5 is 4D: (n_buffers, buffer_size, n_atoms, 3)
            if len(positions.shape) == 4:
                n_frames = positions.shape[0] * positions.shape[1]
                first_frame = positions[0, 0]
                last_frame = positions[-1, -1]
            elif len(positions.shape) == 3:
                n_frames = positions.shape[0]
                first_frame = positions[0]
                last_frame = positions[-1]
            else:
                print(f"  Unexpected shape: {positions.shape}")
                result = {"protein": protein, "status": "UNKNOWN"}
                json.dump(result, open(os.path.join(protein_dir, "rg_check.json"), "w"), indent=2)
                sys.exit(0)
            rg_first = compute_rg(first_frame)
            rg_last = compute_rg(last_frame)
            rg_ratio = rg_last / rg_first if rg_first > 0 else float('inf')
            status = "STRUCTURAL_FAIL" if rg_ratio > 2.0 else ("NAN_FAIL" if np.any(np.isnan(last_frame)) else "PASS")
            print(f"  n_frames={n_frames}, Rg_first={rg_first:.2f}, Rg_last={rg_last:.2f}, ratio={rg_ratio:.3f}, status={status}")
            result = {"protein": protein, "dt_fs": 0.25, "n_frames": int(n_frames),
                      "rg_first_A": round(float(rg_first), 3), "rg_last_A": round(float(rg_last), 3),
                      "rg_ratio": round(float(rg_ratio), 4), "status": status}
except Exception as e:
    print(f"  ERROR: {e}")
    result = {"protein": protein, "status": "ERROR", "error": str(e)}

json.dump(result, open(os.path.join(protein_dir, "rg_check.json"), "w"), indent=2)
print(f"  Wrote rg_check.json")
PYEOF

echo ""
echo "Output files:"
ls -lh "${PROTEIN_DIR}/"
echo ""
echo "DIAGNOSTIC COMPLETE. Exit code: ${EXIT_CODE}"
exit ${EXIT_CODE}
