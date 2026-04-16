#!/usr/bin/env python3
"""
SO3LR Crambin NVT Analysis Script
==================================
Reads SO3LR CLI output (HDF5 trajectory + log files) and produces:
  - RMSD vs starting structure
  - Potential energy trace
  - Temperature trace
  - Summary statistics as JSON
  - Plots saved as PNG

Usage:
    python so3lr_analyze.py --scratch /path/to/scratch --output /path/to/output
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

# Try to import optional analysis packages
try:
    import h5py
    HAS_H5PY = True
except ImportError:
    HAS_H5PY = False

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

try:
    from ase.io import read as ase_read
    HAS_ASE = True
except ImportError:
    HAS_ASE = False


def parse_log_file(log_path):
    """Parse SO3LR CLI log file for energy/temperature data.

    The SO3LR CLI log format typically has lines like:
        cycle  step  time[fs]  Epot[eV]  Ekin[eV]  Etot[eV]  T[K]
    """
    data = {
        "cycle": [], "step": [], "time_fs": [],
        "Epot_eV": [], "Ekin_eV": [], "Etot_eV": [], "T_K": []
    }

    if not os.path.exists(log_path):
        print(f"WARNING: Log file not found: {log_path}")
        return data

    with open(log_path, "r") as f:
        lines = f.readlines()

    # Try to detect the format by looking for numeric lines
    header_found = False
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Look for header line
        if "cycle" in line.lower() or "step" in line.lower() or "time" in line.lower():
            header_found = True
            continue

        # Try parsing as numeric data
        parts = line.split()
        if len(parts) >= 4:
            try:
                vals = [float(x) for x in parts[:7] if x.replace(".", "").replace("-", "").replace("+", "").replace("e", "").replace("E", "").isdigit() or "." in x]
                if len(vals) >= 4:
                    # Assume format: cycle step time Epot [Ekin] [Etot] [T]
                    data["cycle"].append(int(vals[0]) if len(vals) > 0 else 0)
                    data["step"].append(int(vals[1]) if len(vals) > 1 else 0)
                    data["time_fs"].append(vals[2] if len(vals) > 2 else 0.0)
                    data["Epot_eV"].append(vals[3] if len(vals) > 3 else 0.0)
                    if len(vals) > 4:
                        data["Ekin_eV"].append(vals[4])
                    if len(vals) > 5:
                        data["Etot_eV"].append(vals[5])
                    if len(vals) > 6:
                        data["T_K"].append(vals[6])
            except (ValueError, IndexError):
                continue

    return data


def read_hdf5_trajectory(hdf5_path):
    """Read SO3LR HDF5 trajectory file."""
    if not HAS_H5PY:
        print("WARNING: h5py not available, cannot read HDF5 trajectory")
        return None

    if not os.path.exists(hdf5_path):
        print(f"WARNING: Trajectory file not found: {hdf5_path}")
        return None

    traj_data = {}
    with h5py.File(hdf5_path, "r") as f:
        print(f"  HDF5 keys: {list(f.keys())}")
        for key in f.keys():
            if isinstance(f[key], h5py.Dataset):
                traj_data[key] = np.array(f[key])
                print(f"  {key}: shape={f[key].shape}, dtype={f[key].dtype}")
            elif isinstance(f[key], h5py.Group):
                print(f"  Group '{key}': {list(f[key].keys())}")
                for subkey in f[key].keys():
                    full_key = f"{key}/{subkey}"
                    if isinstance(f[key][subkey], h5py.Dataset):
                        traj_data[full_key] = np.array(f[key][subkey])
                        print(f"    {subkey}: shape={f[key][subkey].shape}, dtype={f[key][subkey].dtype}")

    return traj_data


def compute_rmsd(positions, reference):
    """Compute RMSD between each frame and a reference structure.

    positions: (n_frames, n_atoms, 3) or (n_atoms, 3)
    reference: (n_atoms, 3)
    """
    if positions.ndim == 2:
        positions = positions[np.newaxis, :, :]

    n_frames = positions.shape[0]
    rmsd = np.zeros(n_frames)

    for i in range(n_frames):
        # Center both structures
        pos = positions[i] - positions[i].mean(axis=0)
        ref = reference - reference.mean(axis=0)

        # Simple RMSD without alignment (Kabsch not needed for quick check)
        diff = pos - ref
        rmsd[i] = np.sqrt(np.mean(np.sum(diff**2, axis=1)))

    return rmsd


def read_reference_structure(xyz_path):
    """Read reference structure from XYZ file."""
    if HAS_ASE:
        atoms = ase_read(xyz_path)
        return atoms.get_positions()

    # Fallback: parse XYZ manually
    with open(xyz_path, "r") as f:
        lines = f.readlines()

    n_atoms = int(lines[0].strip())
    positions = []
    for i in range(2, 2 + n_atoms):
        parts = lines[i].strip().split()
        positions.append([float(parts[1]), float(parts[2]), float(parts[3])])

    return np.array(positions)


def analyze_stage(stage_name, scratch_dir, output_dir, ref_positions):
    """Analyze a single stage (test, stageA, or stageB)."""
    print(f"\n--- Analyzing {stage_name} ---")

    results = {
        "stage": stage_name,
        "status": "not_found",
        "trajectory_frames": 0,
        "simulation_time_ps": 0.0,
    }

    # Check for HDF5 trajectory
    hdf5_path = os.path.join(scratch_dir, f"{stage_name}.hdf5")
    log_path = os.path.join(scratch_dir, f"{stage_name}.log")

    # Also check test variants
    if stage_name == "test":
        for variant in ["test_10ps", "test_10ps_norelax", "test_10ps_f64"]:
            hdf5_variant = os.path.join(scratch_dir, f"{variant}.hdf5")
            log_variant = os.path.join(scratch_dir, f"{variant}.log")
            if os.path.exists(hdf5_variant):
                hdf5_path = hdf5_variant
                log_path = log_variant
                stage_name = variant
                break

    # Read trajectory
    traj_data = None
    if os.path.exists(hdf5_path):
        print(f"  Reading trajectory: {hdf5_path}")
        traj_data = read_hdf5_trajectory(hdf5_path)
        results["status"] = "trajectory_found"
        results["hdf5_path"] = hdf5_path
        results["hdf5_size_mb"] = os.path.getsize(hdf5_path) / (1024 * 1024)
    else:
        print(f"  No trajectory found at {hdf5_path}")

    # Read log
    log_data = parse_log_file(log_path)
    if log_data["Epot_eV"]:
        results["status"] = "data_available"
        results["log_entries"] = len(log_data["Epot_eV"])
        results["Epot_mean_eV"] = float(np.mean(log_data["Epot_eV"]))
        results["Epot_std_eV"] = float(np.std(log_data["Epot_eV"]))
        if log_data["T_K"]:
            results["T_mean_K"] = float(np.mean(log_data["T_K"]))
            results["T_std_K"] = float(np.std(log_data["T_K"]))
        if log_data["Etot_eV"]:
            results["Etot_mean_eV"] = float(np.mean(log_data["Etot_eV"]))
            results["Etot_std_eV"] = float(np.std(log_data["Etot_eV"]))
            # Energy drift
            etot = np.array(log_data["Etot_eV"])
            if len(etot) > 1:
                drift = (etot[-1] - etot[0]) / len(etot)
                results["Etot_drift_eV_per_cycle"] = float(drift)
        if log_data["time_fs"]:
            results["simulation_time_ps"] = float(max(log_data["time_fs"])) / 1000.0

    # Compute RMSD from trajectory positions
    if traj_data is not None and ref_positions is not None:
        # Look for position data in common HDF5 key patterns
        pos_key = None
        for candidate in ["positions", "R", "coords", "trajectory/positions",
                          "trajectory/R", "atoms/positions"]:
            if candidate in traj_data:
                pos_key = candidate
                break

        if pos_key is not None:
            positions = traj_data[pos_key]
            print(f"  Positions key: {pos_key}, shape: {positions.shape}")

            if positions.ndim == 3:
                results["trajectory_frames"] = positions.shape[0]
                rmsd = compute_rmsd(positions, ref_positions)
                results["rmsd_mean_A"] = float(np.mean(rmsd))
                results["rmsd_max_A"] = float(np.max(rmsd))
                results["rmsd_final_A"] = float(rmsd[-1])

                # Check for NaN
                nan_mask = np.isnan(positions).any(axis=(1, 2))
                results["nan_frames"] = int(nan_mask.sum())
                results["has_nan"] = bool(nan_mask.any())
        else:
            print(f"  No position data found in HDF5. Available keys: {list(traj_data.keys())}")

    # Generate plots
    if HAS_MPL and (log_data["Epot_eV"] or (traj_data is not None)):
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f"SO3LR Crambin NVT - {stage_name}", fontsize=14)

        # Energy plot
        ax = axes[0, 0]
        if log_data["Epot_eV"]:
            time_ps = np.array(log_data["time_fs"]) / 1000.0 if log_data["time_fs"] else np.arange(len(log_data["Epot_eV"]))
            ax.plot(time_ps, log_data["Epot_eV"], "b-", alpha=0.7, label="Epot")
            if log_data["Etot_eV"]:
                ax.plot(time_ps[:len(log_data["Etot_eV"])], log_data["Etot_eV"], "k-", alpha=0.7, label="Etot")
            ax.set_xlabel("Time (ps)")
            ax.set_ylabel("Energy (eV)")
            ax.set_title("Potential & Total Energy")
            ax.legend()

        # Temperature plot
        ax = axes[0, 1]
        if log_data["T_K"]:
            time_ps = np.array(log_data["time_fs"]) / 1000.0 if log_data["time_fs"] else np.arange(len(log_data["T_K"]))
            ax.plot(time_ps[:len(log_data["T_K"])], log_data["T_K"], "r-", alpha=0.7)
            ax.axhline(300.0, color="k", linestyle="--", alpha=0.5, label="Target 300 K")
            ax.set_xlabel("Time (ps)")
            ax.set_ylabel("Temperature (K)")
            ax.set_title("Temperature")
            ax.legend()

        # RMSD plot
        ax = axes[1, 0]
        if "rmsd_mean_A" in results:
            rmsd = compute_rmsd(traj_data[pos_key], ref_positions)
            time_ps = np.linspace(0, results["simulation_time_ps"], len(rmsd))
            ax.plot(time_ps, rmsd, "g-", alpha=0.7)
            ax.set_xlabel("Time (ps)")
            ax.set_ylabel("RMSD (A)")
            ax.set_title("RMSD vs Starting Structure")
        else:
            ax.text(0.5, 0.5, "No position data", transform=ax.transAxes,
                    ha="center", va="center")

        # Kinetic energy plot
        ax = axes[1, 1]
        if log_data["Ekin_eV"]:
            time_ps = np.array(log_data["time_fs"]) / 1000.0 if log_data["time_fs"] else np.arange(len(log_data["Ekin_eV"]))
            ax.plot(time_ps[:len(log_data["Ekin_eV"])], log_data["Ekin_eV"], "m-", alpha=0.7)
            ax.set_xlabel("Time (ps)")
            ax.set_ylabel("Kinetic Energy (eV)")
            ax.set_title("Kinetic Energy")
        else:
            ax.text(0.5, 0.5, "No Ekin data", transform=ax.transAxes,
                    ha="center", va="center")

        plt.tight_layout()
        plot_path = os.path.join(output_dir, f"task-002-{stage_name}.png")
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"  Plot saved: {plot_path}")
        results["plot_path"] = plot_path

    return results


def main():
    parser = argparse.ArgumentParser(description="Analyze SO3LR crambin NVT results")
    parser.add_argument("--scratch", default="/nfs/roberts/scratch/pi_mg269/rag88/alpha-m/so3lr-crambin",
                        help="Path to scratch directory with SO3LR output")
    parser.add_argument("--output", default="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output",
                        help="Path to output directory for plots and reports")
    parser.add_argument("--input-xyz", default=None,
                        help="Path to reference XYZ file (crambin_h_vacuum.xyz)")
    args = parser.parse_args()

    scratch_dir = args.scratch
    output_dir = args.output

    # Default input path
    if args.input_xyz is None:
        args.input_xyz = os.path.join(output_dir, "crambin_h_vacuum.xyz")

    print("=" * 60)
    print("SO3LR Crambin NVT Analysis")
    print("=" * 60)
    print(f"Scratch dir: {scratch_dir}")
    print(f"Output dir:  {output_dir}")
    print(f"Reference:   {args.input_xyz}")

    # List scratch contents
    if os.path.exists(scratch_dir):
        print(f"\nScratch directory contents:")
        for f in sorted(os.listdir(scratch_dir)):
            fpath = os.path.join(scratch_dir, f)
            size = os.path.getsize(fpath) if os.path.isfile(fpath) else 0
            print(f"  {f} ({size / 1024:.1f} KB)")
    else:
        print(f"\nWARNING: Scratch directory does not exist: {scratch_dir}")
        sys.exit(1)

    # Read reference structure
    ref_positions = None
    if os.path.exists(args.input_xyz):
        ref_positions = read_reference_structure(args.input_xyz)
        print(f"\nReference structure: {ref_positions.shape[0]} atoms")
    else:
        print(f"\nWARNING: Reference file not found: {args.input_xyz}")

    # Check run status
    status_file = os.path.join(scratch_dir, "run_status.txt")
    if os.path.exists(status_file):
        with open(status_file) as f:
            print(f"\nRun status: {f.read().strip()}")

    # Analyze each stage
    all_results = {}
    for stage in ["test", "stageA", "stageB"]:
        results = analyze_stage(stage, scratch_dir, output_dir, ref_positions)
        all_results[stage] = results

    # Save combined results as JSON
    results_path = os.path.join(output_dir, "task-002-analysis-results.json")
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved: {results_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    max_stable_ps = 0.0
    d1_pass = False

    for stage_name, res in all_results.items():
        status = res.get("status", "not_found")
        sim_time = res.get("simulation_time_ps", 0.0)
        has_nan = res.get("has_nan", False)

        print(f"  {stage_name}: status={status}, time={sim_time:.1f} ps, NaN={has_nan}")

        if status in ["data_available", "trajectory_found"] and not has_nan:
            if sim_time > max_stable_ps:
                max_stable_ps = sim_time

        if "T_mean_K" in res:
            print(f"    T = {res['T_mean_K']:.1f} +/- {res['T_std_K']:.1f} K")
        if "rmsd_mean_A" in res:
            print(f"    RMSD = {res['rmsd_mean_A']:.2f} A (max: {res['rmsd_max_A']:.2f} A)")
        if "Epot_mean_eV" in res:
            print(f"    Epot = {res['Epot_mean_eV']:.2f} +/- {res['Epot_std_eV']:.2f} eV")

    print(f"\n  Maximum stable simulation time: {max_stable_ps:.1f} ps")

    if max_stable_ps >= 100.0:
        d1_pass = True
        print("  D1 verdict: PASS (>= 100 ps stable)")
    else:
        print("  D1 verdict: FAIL (< 100 ps stable)")

    print(f"\n  D1 minimum met: {d1_pass}")
    if max_stable_ps >= 1000.0:
        print("  D1 target met: YES (>= 1 ns)")
    elif d1_pass:
        print(f"  D1 target (1 ns): NOT YET (achieved {max_stable_ps:.1f} ps)")

    return all_results


if __name__ == "__main__":
    main()
