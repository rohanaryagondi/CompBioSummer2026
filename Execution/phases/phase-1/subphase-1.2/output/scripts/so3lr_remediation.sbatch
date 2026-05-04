#!/bin/bash
###############################################################################
# SO3LR Remediation: dt=0.25 fs re-runs for 3 failed proteins (WW, GB3, NTL9)
#
# Original dt=0.5 fs runs failed:
#   WW:   NaN at 0.7 ns
#   GB3:  Silent structural explosion (Rg 10.6 -> 986 A, energy normal)
#   NTL9: Structural explosion then NaN at 4.4 ns
#
# Remediation: halve timestep to dt=0.25 fs, keeping 5 ns target.
#   md-cycles=20000, md-steps=1000, dt=0.25 -> 5 ns total
#   Output goes to so3lr_vacuum_dt025/<protein>/ (fresh tree, parallel to original)
#
# Usage:
#   sbatch --job-name=<cryptic-8char> \
#          --export=PROTEIN=<ww|gb3|ntl9> \
#          output/scripts/so3lr_remediation.sbatch
###############################################################################
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=2-00:00:00
#SBATCH --account=pi_mg269

PROTEIN="${PROTEIN:-ww}"

REPO_ROOT="/home/rag88/projects/CompBioSummer2026"
SUBPHASE_ROOT="${REPO_ROOT}/Execution/phases/phase-1/subphase-1.2"
ORIG_TRAJ="${SUBPHASE_ROOT}/output/trajectories/so3lr_vacuum"
REMED_ROOT="${SUBPHASE_ROOT}/output/trajectories/so3lr_vacuum_dt025"
PROTEIN_DIR="${REMED_ROOT}/${PROTEIN}"
RUNNER="${SUBPHASE_ROOT}/output/scripts/so3lr_pilot_runner.py"
mkdir -p "${PROTEIN_DIR}"

# Copy input.xyz from original run into the remediation protein dir so the
# runner finds it and skips PDB->XYZ conversion
ORIG_XYZ="${ORIG_TRAJ}/${PROTEIN}/input.xyz"
REMED_XYZ="${PROTEIN_DIR}/input.xyz"
if [ ! -f "${REMED_XYZ}" ] && [ -f "${ORIG_XYZ}" ]; then
    cp "${ORIG_XYZ}" "${REMED_XYZ}"
fi

# Redirect SLURM output into the protein dir
exec > "${PROTEIN_DIR}/slurm-${SLURM_JOB_ID}.out" 2> "${PROTEIN_DIR}/slurm-${SLURM_JOB_ID}.err"

echo "=============================="
echo "SO3LR Remediation - Job ${SLURM_JOB_ID}"
echo "Protein: ${PROTEIN}"
echo "dt: 0.25 fs (halved from 0.5 fs)"
echo "Target: 5 ns (20000 cycles x 1000 steps x 0.25 fs)"
echo "Node: $(hostname)"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Partition: ${SLURM_JOB_PARTITION}"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'unknown')"
echo "=============================="

# --- Environment setup (identical to working so3lr_pilot.sbatch) ---
module purge
module load miniconda
conda activate env-so3lr

export PYTHONNOUSERSITE=0
export PYTHONPATH="${CONDA_PREFIX}/lib/python3.12/site-packages:/home/rag88/.local/lib/python3.12/site-packages:${PYTHONPATH:-}"

echo "Python: $(which python)"
echo "Python version: $(python --version 2>&1)"
python -c "import numpy; print('numpy:', numpy.__version__, numpy.__file__)"
python -c "import so3lr; print('SO3LR:', so3lr.__version__)"
python -c "import jax; print('JAX:', jax.__version__); print('JAX backend:', jax.default_backend()); print('JAX devices:', jax.devices())"

nvidia-smi

# --- Verify input exists ---
if [ ! -f "${REMED_XYZ}" ]; then
    echo "FATAL: Input XYZ not found: ${REMED_XYZ}"
    exit 99
fi
echo "Input XYZ: ${REMED_XYZ} ($(wc -l < "${REMED_XYZ}") lines)"

# --- Run SO3LR with dt=0.25 fs ---
echo ""
echo "============================================"
echo "STEP: SO3LR NVT remediation @ dt=0.25 fs, 5 ns for ${PROTEIN}"
echo "Start: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"

# The runner takes --output-dir and creates <output-dir>/<protein>/ internally.
# We pass REMED_ROOT so the runner creates REMED_ROOT/<protein>/stageA.hdf5,
# which is exactly PROTEIN_DIR.
python "${RUNNER}" \
    --protein "${PROTEIN}" \
    --mode run \
    --target-ns 5.0 \
    --dt-fs 0.25 \
    --output-dir "${REMED_ROOT}"

EXIT_CODE=$?

echo ""
echo "============================================"
echo "SO3LR CLI EXIT: ${EXIT_CODE}"
echo "End: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"

# --- Post-run Rg check (catches silent structural explosions like GB3) ---
echo ""
echo "============================================"
echo "STEP: Post-run Rg structural integrity check"
echo "============================================"

python << 'PYEOF'
import sys, os, json, glob
import numpy as np

protein = os.environ.get("PROTEIN", "unknown")
remed_root = os.environ.get("REMED_ROOT", ".")
protein_dir = os.path.join(remed_root, protein)

def compute_rg(positions):
    """Compute radius of gyration from Nx3 array of positions."""
    com = positions.mean(axis=0)
    diff = positions - com
    return np.sqrt(np.mean(np.sum(diff**2, axis=1)))

# Find the output HDF5 (stageA.hdf5 or stageB.hdf5)
hdf5_files = sorted(glob.glob(os.path.join(protein_dir, "stage*.hdf5")))
if not hdf5_files:
    print(f"WARNING: No HDF5 trajectory found in {protein_dir}")
    result = {
        "protein": protein,
        "dt_fs": 0.25,
        "rg_check": "NO_TRAJECTORY",
        "status": "UNKNOWN"
    }
    with open(os.path.join(protein_dir, "rg_check.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

hdf5_path = hdf5_files[-1]  # latest stage
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
            # Try to find any 3D or 4D dataset
            for k in keys:
                if isinstance(h5[k], h5py.Dataset) and len(h5[k].shape) >= 3:
                    pos_key = k
                    break

        if pos_key is None:
            print(f"  WARNING: Could not find positions dataset. Keys: {keys}")
            result = {
                "protein": protein,
                "dt_fs": 0.25,
                "rg_check": "NO_POSITIONS_KEY",
                "hdf5_keys": keys,
                "status": "UNKNOWN"
            }
        else:
            positions = h5[pos_key]
            print(f"  Dataset '{pos_key}': shape={positions.shape}")

            # SO3LR HDF5 stores positions as 4D: (n_buffers, buffer_size, n_atoms, 3)
            # Reshape to (n_frames, n_atoms, 3) for Rg computation
            if len(positions.shape) == 4:
                n_buffers, buf_size, n_atoms_dim, xyz_dim = positions.shape
                n_frames = n_buffers * buf_size
                first_frame = positions[0, 0]           # first buffer, first step
                last_frame = positions[-1, -1]           # last buffer, last step
                mid_buf = n_buffers // 2
                mid_step = buf_size // 2
                mid_frame = positions[mid_buf, mid_step]
            elif len(positions.shape) == 3:
                n_frames = positions.shape[0]
                first_frame = positions[0]
                last_frame = positions[-1]
                mid_frame = positions[n_frames // 2]
            else:
                print(f"  Unexpected positions shape: {positions.shape}")
                result = {"protein": protein, "dt_fs": 0.25, "status": "UNKNOWN",
                          "error": f"positions shape {positions.shape}"}
                rg_json = os.path.join(protein_dir, "rg_check.json")
                with open(rg_json, "w") as f:
                    json.dump(result, f, indent=2)
                sys.exit(0)

            rg_first = compute_rg(first_frame)
            rg_last = compute_rg(last_frame)
            rg_ratio = rg_last / rg_first if rg_first > 0 else float('inf')

            rg_mid = compute_rg(mid_frame)

            print(f"  n_frames (total): {n_frames}")
            print(f"  Rg(first frame): {rg_first:.2f} A")
            print(f"  Rg(mid frame):   {rg_mid:.2f} A")
            print(f"  Rg(last frame):  {rg_last:.2f} A")
            print(f"  Rg ratio (last/first): {rg_ratio:.3f}")

            if rg_ratio > 2.0:
                status = "STRUCTURAL_FAIL"
                print(f"  STATUS: STRUCTURAL_FAIL (Rg ratio {rg_ratio:.3f} > 2.0)")
            elif np.any(np.isnan(last_frame)):
                status = "NAN_FAIL"
                print(f"  STATUS: NAN_FAIL (NaN in last frame positions)")
            else:
                status = "PASS"
                print(f"  STATUS: PASS")

            result = {
                "protein": protein,
                "dt_fs": 0.25,
                "n_frames": int(n_frames),
                "rg_first_A": round(float(rg_first), 3),
                "rg_mid_A": round(float(rg_mid), 3),
                "rg_last_A": round(float(rg_last), 3),
                "rg_ratio": round(float(rg_ratio), 4),
                "status": status,
                "hdf5_path": hdf5_path,
            }

except Exception as e:
    print(f"  ERROR during Rg check: {e}")
    result = {
        "protein": protein,
        "dt_fs": 0.25,
        "rg_check": "ERROR",
        "error": str(e),
        "status": "UNKNOWN"
    }

# Write result JSON
rg_json = os.path.join(protein_dir, "rg_check.json")
with open(rg_json, "w") as f:
    json.dump(result, f, indent=2)
print(f"  Wrote: {rg_json}")
PYEOF

RG_EXIT=$?
echo "Rg check exit code: ${RG_EXIT}"

# --- Final summary ---
echo ""
echo "============================================"
echo "FINAL SUMMARY"
echo "============================================"
echo "SO3LR exit code: ${EXIT_CODE}"
echo "Rg check exit code: ${RG_EXIT}"
echo ""
echo "Output files in ${PROTEIN_DIR}:"
ls -lh "${PROTEIN_DIR}/" 2>/dev/null

# Exit with the SO3LR exit code (Rg check is informational)
exit ${EXIT_CODE}
