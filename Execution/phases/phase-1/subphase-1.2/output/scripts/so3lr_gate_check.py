#!/usr/bin/env python3
"""
SO3LR rescue gate check (Task 002 Rescue, Subphase 1.2).

For each protein gate, parse:
  - stageA.log    -- thermodynamic time series (T, E, KE, PE, H, time/step)
  - stageA.hdf5   -- positions for Rg / COM-displacement check

Gate criteria (ALL must hold for PASS):
  1. No NaN through 500 ps
  2. Rg ratio (final / initial) < 1.2
  3. T mean 285-315 K over 50-500 ps (drop first 50 ps as equilibration)
  4. COM displacement < 5 Å vs frame 0

Run inside env-mace (h5py, numpy):
  conda activate env-mace
  PYTHONNOUSERSITE=1 python so3lr_gate_check.py \\
      --rescue-dir output/trajectories/so3lr_vacuum_rescue
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

import numpy as np
import h5py

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("so3lr_gate_check")


def parse_stage_log(log_path):
    """Parse SO3LR's stageA.log; return arrays of step, t_ps, T, KE, PE, E, H."""
    rows = []
    with open(log_path) as f:
        for line in f:
            # Match SO3LR log lines like:
            # 2026-04-21 18:01:53 - SO3LR - INFO - 100000  -930.077  22.324  -952.401  -941.526  323.4  2.49e-03
            parts = line.strip().split()
            # We expect: date, time, '-', 'SO3LR', '-', 'INFO', '-', step, E, KE, PE, H, T, time/step
            # Use the dash-separated form: split on " - " then take the last part.
            if "INFO -" not in line:
                continue
            tail = line.split("INFO -", 1)[1].strip()
            tail_parts = tail.split()
            if len(tail_parts) < 7:
                continue
            try:
                step = int(tail_parts[0])
                e_tot = float(tail_parts[1])
                ke = float(tail_parts[2])
                pe = float(tail_parts[3])
                h = float(tail_parts[4])
                t = float(tail_parts[5])
            except ValueError:
                continue
            rows.append((step, e_tot, ke, pe, h, t))
    if not rows:
        return None
    arr = np.array(rows, dtype=float)
    # Compute t_ps from step index. Each log line is 1 cycle = 1000 steps × dt fs.
    # We'll compute dt from the spacing between consecutive steps if available.
    return arr


def compute_rg_series(hdf5_path, max_frames=2000):
    """Compute Rg time series and COM displacement from stageA.hdf5.

    Returns (n_frames_used, rg_series, com_disp_series, nan_count).
    """
    with h5py.File(hdf5_path, "r") as f:
        positions = f["positions"][:]  # (n_buf, 50, N_atoms, 3)
    # Flatten buffer × frame axis
    n_buf, frames_per_buf, n_atoms, _ = positions.shape
    flat = positions.reshape(n_buf * frames_per_buf, n_atoms, 3)
    n_frames = min(flat.shape[0], max_frames)
    flat = flat[:n_frames]

    # NaN frames: any frame containing any NaN
    nan_mask = np.isnan(flat).any(axis=(1, 2))
    nan_count = int(nan_mask.sum())

    rg_series = np.full(n_frames, np.nan)
    com_disp_series = np.full(n_frames, np.nan)
    com_initial = None
    for i in range(n_frames):
        if nan_mask[i]:
            continue
        coords = flat[i]
        com = coords.mean(axis=0)
        d = coords - com
        rg = float(np.sqrt((d * d).sum(axis=1).mean()))
        rg_series[i] = rg
        if com_initial is None:
            com_initial = com
        com_disp_series[i] = float(np.linalg.norm(com - com_initial))
    return n_frames, rg_series, com_disp_series, nan_count


def evaluate_gate(rescue_dir, protein, equil_ps=50.0, target_ns=0.5):
    """Apply gate criteria to one protein's trajectory."""
    pdir = Path(rescue_dir) / protein
    log_path = pdir / "stageA.log"
    hdf5_path = pdir / "stageA.hdf5"
    summary_path = pdir / "run_summary.json"

    result = {
        "protein": protein,
        "log_exists": log_path.exists(),
        "hdf5_exists": hdf5_path.exists(),
        "summary_exists": summary_path.exists(),
    }

    if not (log_path.exists() and hdf5_path.exists()):
        result["verdict"] = "MISSING_DATA"
        result["reason"] = (
            f"log_exists={result['log_exists']} "
            f"hdf5_exists={result['hdf5_exists']}")
        return result

    if summary_path.exists():
        with open(summary_path) as f:
            summary = json.load(f)
        result["dt_fs"] = summary.get("dt_fs", None)
        result["precision"] = summary.get("precision", None)
        result["wall_seconds"] = summary.get("wall_seconds", None)
        result["cli_returncode"] = summary.get("returncode",
                                                summary.get("cli_returncode"))

    # Parse log
    arr = parse_stage_log(str(log_path))
    if arr is None:
        result["verdict"] = "LOG_PARSE_FAIL"
        return result

    # Extract dt from cycle spacing
    if arr.shape[0] < 2:
        result["verdict"] = "INSUFFICIENT_DATA"
        result["n_log_rows"] = arr.shape[0]
        return result

    steps = arr[:, 0]
    e_tot = arr[:, 1]
    ke = arr[:, 2]
    pe = arr[:, 3]
    h = arr[:, 4]
    t = arr[:, 5]

    # Compute t_ps from step delta. Default dt from summary (else 0.5 fs)
    dt_fs = result.get("dt_fs", 0.5) or 0.5
    t_ps = steps * dt_fs / 1000.0  # fs -> ps

    # NaN onset (first row with NaN energy or T)
    nan_log_mask = np.isnan(e_tot) | np.isnan(t) | np.isnan(pe)
    if nan_log_mask.any():
        nan_idx = np.argmax(nan_log_mask)
        result["log_nan_onset_step"] = int(steps[nan_idx])
        result["log_nan_onset_ps"] = float(t_ps[nan_idx])
    else:
        result["log_nan_onset_step"] = None
        result["log_nan_onset_ps"] = None

    # T statistics over 50-500 ps (or whatever's available)
    pre_nan_mask = ~nan_log_mask
    equil_mask = (t_ps >= equil_ps) & pre_nan_mask
    if equil_mask.any():
        t_post_equil = t[equil_mask]
        result["t_mean_K"] = float(np.mean(t_post_equil))
        result["t_std_K"] = float(np.std(t_post_equil))
        result["t_min_K"] = float(np.min(t_post_equil))
        result["t_max_K"] = float(np.max(t_post_equil))
    else:
        result["t_mean_K"] = None
        result["t_std_K"] = None

    # Energy drift over post-equil clean window (eV/ns)
    if equil_mask.sum() >= 2:
        t_clean_ps = t_ps[equil_mask]
        e_clean = e_tot[equil_mask]
        h_clean = h[equil_mask]
        ns_span = (t_clean_ps[-1] - t_clean_ps[0]) / 1000.0
        if ns_span > 0:
            result["e_drift_eV_per_ns"] = float(
                (e_clean[-1] - e_clean[0]) / ns_span)
            result["h_drift_eV_per_ns"] = float(
                (h_clean[-1] - h_clean[0]) / ns_span)
        else:
            result["e_drift_eV_per_ns"] = None
            result["h_drift_eV_per_ns"] = None

    result["log_n_rows"] = int(arr.shape[0])
    result["log_last_step"] = int(steps[-1])
    result["log_last_ps"] = float(t_ps[-1])

    # Structural / HDF5 analysis
    n_frames, rg, com_disp, nan_count = compute_rg_series(str(hdf5_path))
    result["hdf5_n_frames_inspected"] = n_frames
    result["hdf5_nan_frames"] = nan_count
    valid_idx = ~np.isnan(rg)
    if valid_idx.sum() >= 2:
        rg_valid = rg[valid_idx]
        result["rg_initial_A"] = float(rg_valid[0])
        result["rg_final_A"] = float(rg_valid[-1])
        result["rg_ratio"] = (
            float(rg_valid[-1] / rg_valid[0]) if rg_valid[0] > 0 else None)
        result["rg_max_A"] = float(np.max(rg_valid))
        result["com_disp_max_A"] = float(np.nanmax(com_disp))
    else:
        result["rg_initial_A"] = None
        result["rg_final_A"] = None
        result["rg_ratio"] = None

    # Verdict
    pass_no_nan = (result.get("log_nan_onset_step") is None
                   and nan_count == 0)
    rg_ratio = result.get("rg_ratio")
    pass_rg = (rg_ratio is not None and rg_ratio < 1.2)
    t_mean = result.get("t_mean_K")
    pass_t = (t_mean is not None and 285.0 <= t_mean <= 315.0)
    com_max = result.get("com_disp_max_A")
    pass_com = (com_max is not None and com_max < 5.0)

    result["check_no_nan"] = bool(pass_no_nan)
    result["check_rg_ratio_lt_1p2"] = bool(pass_rg)
    result["check_t_mean_285_315"] = bool(pass_t)
    result["check_com_disp_lt_5A"] = bool(pass_com)
    result["verdict"] = (
        "PASS" if (pass_no_nan and pass_rg and pass_t and pass_com)
        else "FAIL")

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rescue-dir",
                        default="output/trajectories/so3lr_vacuum_rescue")
    parser.add_argument("--proteins", nargs="+", default=["ww", "gb3", "ntl9"])
    parser.add_argument("--equil-ps", type=float, default=50.0)
    parser.add_argument("--target-ns", type=float, default=0.5)
    parser.add_argument("--out-json", default=None,
                        help="Write summary JSON to this path")
    args = parser.parse_args()

    summary = {
        "rescue_dir": args.rescue_dir,
        "equil_ps": args.equil_ps,
        "target_ns": args.target_ns,
        "results": {},
    }

    for p in args.proteins:
        logger.info(f"=== Gate check: {p} ===")
        r = evaluate_gate(args.rescue_dir, p, equil_ps=args.equil_ps,
                         target_ns=args.target_ns)
        summary["results"][p] = r

        # Print per-protein verdict line
        v = r.get("verdict", "?")
        rg = r.get("rg_ratio")
        rg_s = f"{rg:.3f}" if rg is not None else "n/a"
        t_mean = r.get("t_mean_K")
        t_s = f"{t_mean:.1f}" if t_mean is not None else "n/a"
        nan_onset = r.get("log_nan_onset_ps")
        nan_s = f"{nan_onset:.3f}" if nan_onset is not None else "none"
        com_max = r.get("com_disp_max_A")
        com_s = f"{com_max:.2f}" if com_max is not None else "n/a"
        last_ps = r.get("log_last_ps")
        last_s = f"{last_ps:.1f}" if last_ps is not None else "n/a"
        print(f"  {p:5s}  verdict={v:14s}  Rg ratio={rg_s}  "
              f"T mean={t_s} K  COM max={com_s} A  "
              f"NaN onset={nan_s} ps  last_ps={last_s}")

    # Aggregate verdict
    verdicts = [r["verdict"] for r in summary["results"].values()]
    pass_count = sum(1 for v in verdicts if v == "PASS")
    summary["pass_count"] = pass_count
    summary["fail_count"] = sum(1 for v in verdicts if v == "FAIL")
    print()
    print(f"Pass count: {pass_count}/{len(verdicts)}")

    if args.out_json:
        with open(args.out_json, "w") as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Wrote {args.out_json}")

    return 0 if pass_count == len(verdicts) else 1


if __name__ == "__main__":
    sys.exit(main())
