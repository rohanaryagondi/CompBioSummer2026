#!/usr/bin/env python
"""density_T_P.py -- NPT-specific quality control from OpenMM StateDataReporter logs.

Reads a CSV log produced by openmm.app.StateDataReporter (the StateDataReporter
output used by `mace_hybrid_npt_prod.py`) and computes summary statistics +
linear-drift detection for density, temperature, and pressure.

I/O contract
    Inputs:
        log_path  : str | Path -- StateDataReporter CSV (header in first line)
        target_T  : float      -- target temperature in K (default 300)
        target_P  : float      -- target pressure in atm (default 1.0)
        target_density_g_cc : float | None -- target water-protein density in g/cm^3
            (typical ~1.00 for solvated protein at 300 K, 1 atm; default None = auto)
        drift_threshold : float    -- |slope| * duration_ns; flag if exceeded
            (default 0.05 g/cm^3 over the full window for density;
             5 K for temperature; 50 atm for pressure)

    Outputs (JSON, returned and optionally written):
        {
            "duration_ns": ...,
            "n_frames": ...,
            "density": {"mean": ..., "std": ..., "slope_per_ns": ..., "drift": ...,
                        "drift_flag": bool},
            "temperature": {...},
            "pressure": {...},
            "verdict": "PASS" | "FAIL"
        }

Reference: Sub 1.1 `mace_analyze.py` parse_log() + thresholds carried forward
from `1.2-mace-npt-fixed.md` (T = 300 +/- 15 K; P approx 1 atm; density physical).
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import numpy as np


# Sub 1.4 production-acceptance thresholds (from 1.2-mace-npt-fixed.md)
DEFAULT_TARGET_T = 300.0
DEFAULT_TARGET_P = 1.0
DEFAULT_T_TOL = 15.0     # K (|mean - target| <= 15 K)
DEFAULT_P_TOL = 200.0    # atm (1-frame P fluctuates +/-100s atm; mean tighter)
DEFAULT_DENSITY_RANGE = (0.85, 1.10)   # g/cm^3, accept band

# Drift flags: if |slope_per_ns| * duration_ns > threshold, flag drift
DEFAULT_DENSITY_DRIFT_THR = 0.05    # g/cm^3 over the run
DEFAULT_T_DRIFT_THR = 5.0           # K over the run
DEFAULT_P_DRIFT_THR = 100.0         # atm over the run


@dataclass
class TimeSeriesStats:
    mean: float
    std: float
    min: float
    max: float
    slope_per_ns: float
    drift_total: float            # slope * duration_ns
    drift_flag: bool


def parse_state_log(log_path: Path) -> dict:
    """Parse OpenMM StateDataReporter CSV into named numpy arrays.

    Header (with quotes) typically includes:
        '#"Step"', '"Time (ps)"', '"Potential Energy (kJ/mole)"',
        '"Kinetic Energy (kJ/mole)"', '"Total Energy (kJ/mole)"',
        '"Temperature (K)"', '"Box Volume (nm^3)"', '"Density (g/mL)"', ...

    Returns dict with available columns mapped to:
        step, time_ps, pe, ke, total_e, temp, volume_nm3, density_g_cc,
        pressure_atm, speed_ns_per_day
    """
    data: dict[str, list] = {
        "step": [], "time_ps": [], "pe": [], "ke": [], "total_e": [],
        "temp": [], "volume_nm3": [], "density_g_cc": [],
        "pressure_atm": [], "speed_ns_per_day": [],
    }

    with open(log_path) as f:
        reader = csv.reader(f)
        header = next(reader)
        col_map: dict[str, int] = {}
        for i, h in enumerate(header):
            h_clean = h.strip().lstrip("#").strip().strip('"').lower()
            if h_clean.startswith("step"):
                col_map["step"] = i
            elif "time" in h_clean and "step" not in h_clean:
                col_map["time_ps"] = i
            elif "potential energy" in h_clean:
                col_map["pe"] = i
            elif "kinetic energy" in h_clean:
                col_map["ke"] = i
            elif "total energy" in h_clean:
                col_map["total_e"] = i
            elif "temperature" in h_clean:
                col_map["temp"] = i
            elif "box volume" in h_clean or "volume" in h_clean:
                col_map["volume_nm3"] = i
            elif "density" in h_clean:
                col_map["density_g_cc"] = i
            elif "pressure" in h_clean:
                col_map["pressure_atm"] = i
            elif "speed" in h_clean:
                col_map["speed_ns_per_day"] = i

        for row in reader:
            if not row or (row[0].strip().startswith("#")):
                continue
            try:
                for key, idx in col_map.items():
                    data[key].append(float(row[idx]))
            except (ValueError, IndexError):
                continue

    return {k: np.asarray(v, dtype=np.float64) for k, v in data.items()}


def compute_drift(time_ps: np.ndarray, values: np.ndarray) -> tuple[float, float]:
    """Linear regression slope (per ns) and total drift over the window.

    Returns (slope_per_ns, total_drift_over_window).
    """
    if values.size < 2:
        return 0.0, 0.0
    time_ns = time_ps / 1000.0
    slope, intercept = np.polyfit(time_ns, values, 1)
    duration_ns = float(time_ns[-1] - time_ns[0])
    return float(slope), float(slope * duration_ns)


def stats_from_series(time_ps: np.ndarray, values: np.ndarray, drift_thr: float) -> TimeSeriesStats:
    if values.size == 0:
        return TimeSeriesStats(
            mean=float("nan"), std=float("nan"),
            min=float("nan"), max=float("nan"),
            slope_per_ns=float("nan"), drift_total=float("nan"),
            drift_flag=False,
        )
    slope, total = compute_drift(time_ps, values)
    return TimeSeriesStats(
        mean=float(values.mean()),
        std=float(values.std()),
        min=float(values.min()),
        max=float(values.max()),
        slope_per_ns=slope,
        drift_total=total,
        drift_flag=abs(total) > drift_thr,
    )


def evaluate_log(
    log_path: str | Path,
    target_T: float = DEFAULT_TARGET_T,
    target_P: float = DEFAULT_TARGET_P,
    density_range: tuple[float, float] = DEFAULT_DENSITY_RANGE,
    T_tol: float = DEFAULT_T_TOL,
    P_tol: float = DEFAULT_P_TOL,
    density_drift_thr: float = DEFAULT_DENSITY_DRIFT_THR,
    T_drift_thr: float = DEFAULT_T_DRIFT_THR,
    P_drift_thr: float = DEFAULT_P_DRIFT_THR,
) -> dict:
    """Top-level NPT QC. Returns a JSON-serializable dict."""
    log_path = Path(log_path)
    data = parse_state_log(log_path)
    time_ps = data.get("time_ps", np.array([]))
    duration_ns = float((time_ps[-1] - time_ps[0]) / 1000.0) if time_ps.size > 0 else 0.0

    density_stats = stats_from_series(time_ps, data.get("density_g_cc", np.array([])), density_drift_thr)
    temp_stats = stats_from_series(time_ps, data.get("temp", np.array([])), T_drift_thr)
    pressure_stats = stats_from_series(time_ps, data.get("pressure_atm", np.array([])), P_drift_thr)

    # Verdict: T within tol, density within band, no drift flagged.
    # Pressure mean is informational only (large fluctuations expected).
    t_pass = (not np.isnan(temp_stats.mean)) and abs(temp_stats.mean - target_T) <= T_tol
    d_pass = (not np.isnan(density_stats.mean)) and (
        density_range[0] <= density_stats.mean <= density_range[1]
    )
    no_drift = not (density_stats.drift_flag or temp_stats.drift_flag)

    verdict = "PASS" if (t_pass and d_pass and no_drift) else "FAIL"

    return {
        "log_path": str(log_path),
        "duration_ns": duration_ns,
        "n_frames": int(time_ps.size),
        "target_T_K": target_T,
        "target_P_atm": target_P,
        "density": asdict(density_stats),
        "temperature": asdict(temp_stats),
        "pressure": asdict(pressure_stats),
        "checks": {
            "temperature_within_tol": bool(t_pass),
            "density_within_band": bool(d_pass),
            "no_drift_flag": bool(no_drift),
        },
        "verdict": verdict,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--log", required=True, help="StateDataReporter CSV log")
    p.add_argument("--output", required=True, help="Output JSON path")
    p.add_argument("--target-T", type=float, default=DEFAULT_TARGET_T)
    p.add_argument("--target-P", type=float, default=DEFAULT_TARGET_P)
    args = p.parse_args()

    result = evaluate_log(args.log, target_T=args.target_T, target_P=args.target_P)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)
    print(f"[npt_qc] verdict={result['verdict']} duration={result['duration_ns']:.2f} ns "
          f"T={result['temperature']['mean']:.1f}+/-{result['temperature']['std']:.1f} K "
          f"density={result['density']['mean']:.3f}+/-{result['density']['std']:.3f} g/cc "
          f"P={result['pressure']['mean']:.0f}+/-{result['pressure']['std']:.0f} atm")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
