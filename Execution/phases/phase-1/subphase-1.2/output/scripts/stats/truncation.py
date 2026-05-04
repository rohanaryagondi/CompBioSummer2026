"""
truncation -- T_min trajectory truncation protocol (IP §12.1).

Per IP §12.1: all trajectories for a given protein are truncated to
``T_min(protein) = min over generators of trajectory_length_ns``. This ensures
that Alpha-M per-protein comparisons across generators are made on equal
trajectory length, pre-empting reviewer attack "The MLFF trajectories are too
short" (IP §14.1) by making it a design choice rather than a confound.

Every truncation event is logged to a JSON file for reproducibility (per IP
§15.3 data-integrity requirement). The log records:
- timestamp (UTC ISO)
- per-protein T_min (ns)
- per-trajectory source path, timestep, frames_original, frames_kept
- stats-pipeline version

The actual frame-truncation operation uses mdtraj if available; for pure
numeric tests we expose a lightweight ``compute_t_min`` that does not require
mdtraj.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any, Dict, Mapping, Optional


def compute_t_min(
    trajectories: Mapping[str, Mapping[str, float]],
) -> Dict[str, float]:
    """Compute T_min per protein from a trajectory-length dict.

    Parameters
    ----------
    trajectories
        ``{protein_id: {generator_id: trajectory_length_ns}}``.
        Values are trajectory lengths in ns (or any consistent unit).

    Returns
    -------
    dict
        ``{protein_id: t_min}`` — the minimum trajectory length across all
        generators for each protein.

    Notes
    -----
    Proteins with an empty inner dict are skipped (no T_min definable).
    """
    out: Dict[str, float] = {}
    for protein, gens in trajectories.items():
        if not gens:
            continue
        out[protein] = float(min(gens.values()))
    return out


def log_truncation_events(
    t_min: Mapping[str, float],
    per_trajectory_info: Mapping[str, Mapping[str, Dict[str, Any]]],
    log_path: str,
    pipeline_version: str = "0.1.0",
) -> str:
    """Write a JSON log of the truncation plan.

    Parameters
    ----------
    t_min
        ``{protein_id: t_min_ns}``.
    per_trajectory_info
        ``{protein_id: {generator_id: {'source_path': str, 'timestep_ps': float,
        'frames_original': int, 'frames_kept': int}}}``.
    log_path
        Destination JSON file. Parent dirs are created automatically.
    pipeline_version
        Pinned version of the stats pipeline (for reproducibility).

    Returns
    -------
    str
        The absolute path of the written log.
    """
    log_dir = Path(log_path).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    log = {
        "timestamp_utc": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "pipeline_version": pipeline_version,
        "t_min_per_protein_ns": {k: float(v) for k, v in t_min.items()},
        "per_trajectory": {
            p: {g: dict(info) for g, info in gens.items()}
            for p, gens in per_trajectory_info.items()
        },
    }
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2, sort_keys=True)
    return os.path.abspath(log_path)


def truncate_trajectories(
    trajectories: Mapping[str, Mapping[str, str]],
    t_min: Mapping[str, float],
    timestep_ps: Mapping[str, Mapping[str, float]],
    output_dir: str,
    log_path: Optional[str] = None,
    pipeline_version: str = "0.1.0",
) -> Dict:
    """Truncate each trajectory to T_min for its protein; write to output_dir.

    Parameters
    ----------
    trajectories
        ``{protein_id: {generator_id: source_path_to_trajectory}}``.
    t_min
        ``{protein_id: t_min_ns}``.
    timestep_ps
        ``{protein_id: {generator_id: timestep_ps}}`` -- time between frames
        (picoseconds) for each trajectory. Needed to convert ns -> frames.
    output_dir
        Root dir to write truncated trajectories. Layout:
        ``<output_dir>/<protein_id>/<generator_id>_truncated.dcd``.
    log_path
        Optional JSON log path; defaults to ``<output_dir>/t_min_log.json``.
    pipeline_version
        Stats-pipeline version for the log.

    Returns
    -------
    dict
        ``{'truncation_log_path': str, 'per_trajectory': {...}}``.
        ``per_trajectory`` has the same structure passed to
        ``log_truncation_events``.

    Notes
    -----
    Requires ``mdtraj`` for the actual file I/O. If mdtraj is not importable
    (e.g., running the synthetic unit test in a stripped-down env), the
    function raises ``RuntimeError`` with a clear hint. The synthetic unit
    test covers ``compute_t_min`` and ``log_truncation_events`` directly.
    """
    try:
        import mdtraj as md
    except ImportError as e:  # pragma: no cover -- exercised only on real trajs
        raise RuntimeError(
            "mdtraj is required to truncate trajectory files. Install into "
            "env-stats (conda install -c conda-forge mdtraj) or use "
            "compute_t_min + log_truncation_events on pre-extracted frame "
            "counts instead."
        ) from e

    os.makedirs(output_dir, exist_ok=True)
    per_traj: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for protein, gens in trajectories.items():
        if protein not in t_min:
            continue
        t = float(t_min[protein])
        prot_out = Path(output_dir) / str(protein)
        prot_out.mkdir(parents=True, exist_ok=True)
        per_traj[protein] = {}
        for gen, src in gens.items():
            dt_ps = float(timestep_ps[protein][gen])
            traj = md.load(src)
            frames_original = traj.n_frames
            n_keep = int(round(t * 1000.0 / dt_ps))  # ns -> ps -> frames
            n_keep = min(n_keep, frames_original)
            truncated = traj[:n_keep]
            dest = prot_out / f"{gen}_truncated.dcd"
            truncated.save_dcd(str(dest))
            per_traj[protein][gen] = {
                "source_path": str(src),
                "dest_path": str(dest),
                "timestep_ps": dt_ps,
                "frames_original": int(frames_original),
                "frames_kept": int(n_keep),
                "length_kept_ns": float(n_keep * dt_ps / 1000.0),
            }

    if log_path is None:
        log_path = str(Path(output_dir) / "t_min_log.json")
    written = log_truncation_events(t_min, per_traj, log_path, pipeline_version)
    return {"truncation_log_path": written, "per_trajectory": per_traj}


__all__ = [
    "compute_t_min",
    "log_truncation_events",
    "truncate_trajectories",
]
