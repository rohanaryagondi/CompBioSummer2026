#!/usr/bin/env python
"""analyze_so3lr_vacuum.py -- Top-level analyzer for SO3LR vacuum NVT 5 ns runs.

Inputs (CLI):
    --input-traj   : SO3LR HDF5 trajectory (position key auto-detected)
    --input-log    : SO3LR CLI log file (cycle/step/time_fs/Epot/T)
    --topology     : PDB topology (residue + atom names)
    --reference    : reference XYZ from so3lr_prep_proteins[_neutral].py
    --output-dir   : output directory
    --protein-id   : short id, e.g. WW, GB3, NTL9, GB1, ubq
    --gate-ps      : runaway gate window in ps (default 500; per
                     1.2-so3lr-rescue-results.md)
    --rg-runaway-thr-A : flag charge-runaway if Rg grows by > thr (default 5.0 A)

Outputs in --output-dir:
    <id>_so3lr_qc.json   combined QC verdict
    <id>_rg.npz          Rg time series + runaway flag
    <id>_rmsf.npz / .csv per-residue Cα RMSF (matches compute_rmsf_batch1.py)
    <id>_com.npz         COM trajectory + max-drift
    <id>_nan_onset.json  NaN onset frame + first-NaN time

Verdict rules (from 1.2-so3lr-rescue-results.md):
    PASS      : >= 5 ns, no NaN, no Rg runaway
    GATE_PASS : >= gate_ps, no NaN, no Rg runaway (interim only)
    FAIL      : NaN before gate_ps, Rg runaway, or duration < gate_ps

References: Sub 1.1 so3lr_analyze.py (parse_log_file, read_hdf5_trajectory,
compute_rmsd) reused as patterns.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import numpy as np

from . import _rmsf_helpers


# Gate / runaway parameters (defaults from 1.2-so3lr-rescue-results.md)
DEFAULT_GATE_PS = 500.0
DEFAULT_RG_RUNAWAY_THR_A = 5.0   # Angstroms above starting Rg
DEFAULT_FULL_RUN_NS = 5.0


@dataclass
class So3lrQCResult:
    protein_id: str
    duration_ps: float
    n_frames: int
    nan_onset_frame: Optional[int]
    has_nan: bool
    rg_start_A: float
    rg_max_A: float
    rg_final_A: float
    rg_runaway_flag: bool
    com_drift_A: float
    rmsf_mean_A: float
    rmsf_max_A: float
    verdict: str


def load_so3lr_hdf5(traj_path: Path) -> tuple[np.ndarray, dict]:
    """Load positions (n_frames, n_atoms, 3) in A + metadata.

    Sub 1.4: reuse so3lr_analyze.read_hdf5_trajectory; auto-detect key from
    ['positions', 'R', 'coords', 'trajectory/positions', 'trajectory/R',
    'atoms/positions']; convert nm->A if needed.
    """
    raise NotImplementedError("Sub 1.4: see docstring")


def parse_so3lr_log(log_path: Path) -> dict:
    """Parse SO3LR CLI log. Returns dict with cycle/step/time_fs/Epot_eV/
    Ekin_eV/Etot_eV/T_K arrays. Sub 1.4: copy so3lr_analyze.parse_log_file body."""
    raise NotImplementedError("Sub 1.4: see docstring")


def compute_rg(positions: np.ndarray, masses: Optional[np.ndarray] = None) -> np.ndarray:
    """Radius of gyration per frame; positions (n_frames, n_atoms, 3) in A."""
    if masses is None:
        com = positions.mean(axis=1, keepdims=True)
        diff = positions - com
        return np.sqrt((diff ** 2).sum(axis=2).mean(axis=1))
    m = masses[None, :, None]
    total = masses.sum()
    com = (positions * m).sum(axis=1, keepdims=True) / total
    diff = positions - com
    return np.sqrt(((diff ** 2).sum(axis=2) * masses[None, :]).sum(axis=1) / total)


def compute_com_trajectory(positions: np.ndarray) -> np.ndarray:
    """COM per frame (unweighted)."""
    return positions.mean(axis=1)


def detect_nan_onset(positions: np.ndarray) -> Optional[int]:
    """First frame index with any NaN; None if clean."""
    if not np.isnan(positions).any():
        return None
    return int(np.argmax(np.isnan(positions).any(axis=(1, 2))))


def compute_ca_rmsf(positions, ca_mask, resids, resnames) -> dict:
    """Per-residue Cα RMSF after Kabsch alignment of Cα to frame 0.

    Inputs:
        positions : (n_frames, n_atoms, 3) float, Angstroms (vacuum: all
            atoms are protein, no solvent to filter).
        ca_mask   : (n_atoms,) bool selector for Cα atoms.
        resids    : per-residue resid array (or per-atom; will subset to Cα).
        resnames  : per-residue resname array (or per-atom; will subset).

    Returns dict with keys ok, n_frames, n_residues, resid, resname, rmsf_A,
    rmsf_mean, rmsf_median, rmsf_max, rmsf_min, skip_reason. Same shape as
    `analyze_mace_npt.compute_rmsf` so downstream aggregation is uniform.

    Implementation in `_rmsf_helpers.kabsch_aligned_ca_rmsf` (pure-numpy
    Kabsch; no mdtraj/MDAnalysis dependency, since SO3LR HDF5 may not have a
    native PDB topology at hand).
    """
    return _rmsf_helpers.so3lr_compute_ca_rmsf(positions, ca_mask, resids, resnames)


def load_topology_metadata(topology_path: Path) -> dict:
    """Returns {ca_mask, resids, resnames, masses}.
    Sub 1.4: parse PDB or use mdtraj.load(topology_path).topology.
    """
    raise NotImplementedError("Sub 1.4: parse topology PDB")


def run(
    traj_path: str | Path,
    log_path: str | Path,
    topology_path: str | Path,
    reference_xyz: str | Path,
    output_dir: str | Path,
    protein_id: str,
    gate_ps: float = DEFAULT_GATE_PS,
    rg_runaway_thr_A: float = DEFAULT_RG_RUNAWAY_THR_A,
    full_run_ns: float = DEFAULT_FULL_RUN_NS,
) -> So3lrQCResult:
    """Top-level pipeline. Returns combined QC result + writes artifacts."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    positions, traj_meta = load_so3lr_hdf5(Path(traj_path))
    log = parse_so3lr_log(Path(log_path))
    topo = load_topology_metadata(Path(topology_path))

    n_frames = positions.shape[0]
    duration_ps = float(max(log.get("time_fs", [0.0])) / 1000.0) if log.get("time_fs") else 0.0

    # NaN detection
    nan_onset = detect_nan_onset(positions)
    has_nan = nan_onset is not None
    if has_nan:
        # truncate analysis to frames before NaN
        positions = positions[:nan_onset]
        n_frames = positions.shape[0]

    # Rg time series + runaway detection
    rg = compute_rg(positions, masses=topo.get("masses"))
    rg_start = float(rg[0]) if rg.size > 0 else float("nan")
    rg_max = float(rg.max()) if rg.size > 0 else float("nan")
    rg_final = float(rg[-1]) if rg.size > 0 else float("nan")
    rg_runaway = (rg_max - rg_start) > rg_runaway_thr_A

    np.savez(
        out / f"{protein_id}_rg.npz",
        rg_A=rg, rg_start_A=rg_start, rg_max_A=rg_max,
        rg_runaway_flag=bool(rg_runaway),
        threshold_A=rg_runaway_thr_A,
    )

    # COM trajectory + drift (max-displacement of COM relative to frame 0)
    com = compute_com_trajectory(positions)
    com_drift = float(np.linalg.norm(com - com[0], axis=1).max()) if com.size > 0 else 0.0
    np.savez(out / f"{protein_id}_com.npz", com_xyz_A=com, com_drift_A=com_drift)

    # Per-residue Cα RMSF
    rmsf = compute_ca_rmsf(positions, topo["ca_mask"], topo["resids"], topo["resnames"])

    # NaN onset
    with (out / f"{protein_id}_nan_onset.json").open("w") as f:
        json.dump({
            "protein_id": protein_id,
            "has_nan": has_nan,
            "nan_onset_frame": nan_onset,
            "first_nan_time_ps": float(log["time_fs"][nan_onset] / 1000.0)
                if (has_nan and "time_fs" in log and nan_onset < len(log["time_fs"])) else None,
        }, f, indent=2)

    # Verdict
    if duration_ps >= full_run_ns * 1000.0 and not has_nan and not rg_runaway:
        verdict = "PASS"
    elif duration_ps >= gate_ps and not has_nan and not rg_runaway:
        verdict = "GATE_PASS"
    else:
        verdict = "FAIL"

    result = So3lrQCResult(
        protein_id=protein_id,
        duration_ps=duration_ps,
        n_frames=int(n_frames),
        nan_onset_frame=nan_onset,
        has_nan=has_nan,
        rg_start_A=rg_start,
        rg_max_A=rg_max,
        rg_final_A=rg_final,
        rg_runaway_flag=bool(rg_runaway),
        com_drift_A=com_drift,
        rmsf_mean_A=rmsf.get("rmsf_mean", float("nan")),
        rmsf_max_A=rmsf.get("rmsf_max", float("nan")),
        verdict=verdict,
    )
    with (out / f"{protein_id}_so3lr_qc.json").open("w") as f:
        json.dump(asdict(result), f, indent=2)
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--input-traj", required=True, help="SO3LR HDF5 trajectory")
    p.add_argument("--input-log", required=True)
    p.add_argument("--topology", required=True)
    p.add_argument("--reference", required=True, help="Reference XYZ from prep")
    p.add_argument("--output-dir", required=True)
    p.add_argument("--protein-id", required=True)
    p.add_argument("--gate-ps", type=float, default=DEFAULT_GATE_PS)
    p.add_argument("--rg-runaway-thr-A", type=float, default=DEFAULT_RG_RUNAWAY_THR_A)
    p.add_argument("--full-run-ns", type=float, default=DEFAULT_FULL_RUN_NS)
    args = p.parse_args()

    result = run(
        args.input_traj, args.input_log, args.topology, args.reference,
        args.output_dir, args.protein_id,
        gate_ps=args.gate_ps, rg_runaway_thr_A=args.rg_runaway_thr_A,
        full_run_ns=args.full_run_ns,
    )
    print(f"[so3lr] {args.protein_id} verdict={result.verdict} "
          f"duration={result.duration_ps:.1f} ps "
          f"Rg={result.rg_start_A:.2f}->{result.rg_final_A:.2f} A "
          f"runaway={result.rg_runaway_flag} NaN={result.has_nan}")
    return 0 if result.verdict in ("PASS", "GATE_PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
