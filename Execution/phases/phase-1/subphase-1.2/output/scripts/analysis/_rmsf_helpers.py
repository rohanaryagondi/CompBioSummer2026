"""_rmsf_helpers.py -- shared per-residue Cα RMSF helpers for analyze_mace_npt
and analyze_so3lr_vacuum.

Two entry points:
    * `kabsch_aligned_ca_rmsf(positions, ca_indices)` -- pure-numpy core: Kabsch
      align all frames to frame 0 using ca_indices, compute per-Cα RMSF in
      Angstrom. Used by both MACE (MDAnalysis-loaded path) and SO3LR
      (HDF5-array-loaded path).
    * `mace_compute_rmsf(traj_path, top_path)` -- MDAnalysis wrapper that mirrors
      `output/scripts/features/compute_rmsf_batch1.py:compute_rmsf` lines 99-138
      so MACE NPT analysis joins cleanly with batch1 BioEmu RMSF features.

NOTE: positions everywhere are in Angstroms. mdtraj uses nm internally, so any
caller that loads with mdtraj must convert before passing positions to the core
helper (multiply xyz by 10).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np


def _kabsch_rotation(P: np.ndarray, Q: np.ndarray) -> np.ndarray:
    """Compute the optimal 3x3 rotation matrix R such that R @ P^T best aligns
    to Q^T (least squares), where P, Q are (N, 3) arrays already centered at
    the origin. Standard Kabsch (Acta Cryst A 32, 922 (1976)).
    """
    H = P.T @ Q
    U, _, Vt = np.linalg.svd(H)
    # Reflection correction
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    D = np.diag([1.0, 1.0, d])
    return Vt.T @ D @ U.T


def kabsch_aligned_ca_rmsf(positions: np.ndarray, ca_indices: np.ndarray) -> np.ndarray:
    """Per-residue Cα RMSF in the same units as `positions` (intended Angstroms).

    Parameters
    ----------
    positions : (n_frames, n_atoms, 3) float
        Trajectory positions. Caller is responsible for unit conversion.
    ca_indices : (n_residues,) int
        Atom indices selecting Cα atoms.

    Returns
    -------
    rmsf : (n_residues,) float64
        Square root of the time-mean squared deviation of each Cα from its
        time-mean position, after Kabsch alignment to frame 0 on Cα.

    Edge cases:
        * n_frames < 2 returns zeros (RMSF undefined).
        * n_residues < 2 returns zeros (cannot align a single point).
        * NaN positions raise ValueError (callers should detect+truncate first).
    """
    P = np.asarray(positions, dtype=np.float64)
    if P.ndim != 3 or P.shape[2] != 3:
        raise ValueError(f"positions must be (n_frames, n_atoms, 3); got {P.shape}")
    if np.isnan(P).any():
        raise ValueError("positions contains NaN; truncate before RMSF")

    ca_idx = np.asarray(ca_indices, dtype=np.int64)
    n_frames = P.shape[0]
    n_res = ca_idx.size

    if n_frames < 2 or n_res < 2:
        return np.zeros(n_res, dtype=np.float64)

    ca = P[:, ca_idx, :]  # (n_frames, n_res, 3)
    # Reference frame: frame 0
    ref = ca[0]
    ref_centroid = ref.mean(axis=0)
    ref_centered = ref - ref_centroid

    aligned = np.empty_like(ca)
    aligned[0] = ref_centered

    for k in range(1, n_frames):
        frame = ca[k]
        centroid = frame.mean(axis=0)
        frame_centered = frame - centroid
        R = _kabsch_rotation(frame_centered, ref_centered)
        aligned[k] = frame_centered @ R.T

    mean_pos = aligned.mean(axis=0)
    diff = aligned - mean_pos
    msd = (diff ** 2).sum(axis=2).mean(axis=0)
    return np.sqrt(msd)


def mace_compute_rmsf(
    traj_path: Path,
    top_path: Path,
    discard_first_ps: float = 100.0,
) -> dict:
    """MACE NPT compute_rmsf body. Mirrors compute_rmsf_batch1.py:99-138.

    Returns dict with keys:
        ok, n_frames, n_residues, resid, resname, rmsf_A,
        rmsf_mean, rmsf_median, rmsf_max, rmsf_min, skip_reason.

    Discards the first `discard_first_ps` ps (default 100) as MACE NPT
    equilibration per OSF v3 §8.
    """
    status = {
        "ok": False,
        "n_frames": None,
        "n_residues": None,
        "resid": None,
        "resname": None,
        "rmsf_A": None,
        "rmsf_mean": None,
        "rmsf_median": None,
        "rmsf_max": None,
        "rmsf_min": None,
        "skip_reason": None,
    }

    try:
        import MDAnalysis as mda
        from MDAnalysis.analysis import align, rms
    except ImportError as exc:
        status["skip_reason"] = f"mdanalysis_unavailable:{exc}"
        return status

    try:
        u = mda.Universe(str(top_path), str(traj_path), in_memory=True)
    except Exception as exc:
        status["skip_reason"] = f"load_failed:{exc}"
        return status

    # Discard MACE NPT equilibration window (default 100 ps) before RMSF.
    # MDAnalysis time units default to ps; in_memory keeps frame metadata.
    if discard_first_ps > 0 and u.trajectory.n_frames > 1:
        try:
            dt_ps = float(u.trajectory.dt)  # ps per frame
        except Exception:
            dt_ps = 0.0
        if dt_ps > 0:
            n_skip = int(np.floor(discard_first_ps / dt_ps))
            if 0 < n_skip < u.trajectory.n_frames - 1:
                # Re-load in_memory but trim to frames [n_skip:]; MDAnalysis
                # in_memory traj allows slicing via transfer_to_memory(start=)
                u.transfer_to_memory(start=n_skip)

    n_frames = u.trajectory.n_frames
    # Restrict to chain A (default) — first chain segment if available.
    # Mirrors compute_rmsf_batch1.py which does not segment but trajectories
    # there are single-chain. For multi-chain MACE NPT, scope to first segid.
    ca = u.select_atoms("name CA")
    if len(ca) > 0 and len({s.segid for s in ca.segments}) > 1:
        first_seg = sorted({s.segid for s in ca.segments})[0]
        ca = u.select_atoms(f"name CA and segid {first_seg}")

    n_res = ca.residues.n_residues
    status["n_frames"] = int(n_frames)
    status["n_residues"] = int(n_res)

    if n_frames < 2:
        status["skip_reason"] = f"too_few_frames:{n_frames}"
        return status
    if n_res < 2:
        status["skip_reason"] = f"too_few_residues:{n_res}"
        return status

    try:
        # Align all frames to frame 0 on CA (in-place since in_memory=True)
        align.AlignTraj(u, u, select="name CA", in_memory=True, ref_frame=0).run()
        R = rms.RMSF(ca).run()
        rmsf = np.asarray(R.results.rmsf, dtype=np.float64)
    except Exception as exc:
        status["skip_reason"] = f"rmsf_failed:{exc}"
        return status

    resids = np.asarray(ca.residues.resids, dtype=np.int64)
    resnames = np.asarray(ca.residues.resnames, dtype="<U3")

    status["ok"] = True
    status["resid"] = resids
    status["resname"] = resnames
    status["rmsf_A"] = rmsf
    status["rmsf_mean"] = float(rmsf.mean())
    status["rmsf_median"] = float(np.median(rmsf))
    status["rmsf_max"] = float(rmsf.max())
    status["rmsf_min"] = float(rmsf.min())
    return status


def so3lr_compute_ca_rmsf(
    positions: np.ndarray,
    ca_mask: np.ndarray,
    resids: np.ndarray,
    resnames: np.ndarray,
) -> dict:
    """SO3LR vacuum NVT compute_ca_rmsf body. Returns dict matching MACE.

    `positions` is (n_frames, n_atoms, 3) in Angstroms (vacuum: all atoms are
    protein).  `ca_mask` is a boolean (n_atoms,) selector for Cα atoms.
    """
    status = {
        "ok": False,
        "n_frames": int(positions.shape[0]) if positions.ndim == 3 else None,
        "n_residues": None,
        "resid": None,
        "resname": None,
        "rmsf_A": None,
        "rmsf_mean": None,
        "rmsf_median": None,
        "rmsf_max": None,
        "rmsf_min": None,
        "skip_reason": None,
    }
    if positions.ndim != 3 or positions.shape[2] != 3:
        status["skip_reason"] = f"bad_positions_shape:{positions.shape}"
        return status

    ca_mask_arr = np.asarray(ca_mask, dtype=bool)
    if ca_mask_arr.shape[0] != positions.shape[1]:
        status["skip_reason"] = (
            f"ca_mask_size_mismatch:{ca_mask_arr.shape[0]} vs {positions.shape[1]}"
        )
        return status

    ca_indices = np.flatnonzero(ca_mask_arr)
    n_res = ca_indices.size
    status["n_residues"] = int(n_res)

    if positions.shape[0] < 2 or n_res < 2:
        status["skip_reason"] = (
            f"insufficient:n_frames={positions.shape[0]},n_residues={n_res}"
        )
        return status

    try:
        rmsf = kabsch_aligned_ca_rmsf(positions, ca_indices)
    except Exception as exc:
        status["skip_reason"] = f"rmsf_failed:{exc}"
        return status

    resids_arr = np.asarray(resids, dtype=np.int64)
    resnames_arr = np.asarray(resnames, dtype="<U3")
    if resids_arr.size != n_res:
        # If resids was given over all atoms, subset to ca_indices
        if resids_arr.size == positions.shape[1]:
            resids_arr = resids_arr[ca_indices]
        else:
            resids_arr = np.arange(1, n_res + 1, dtype=np.int64)
    if resnames_arr.size != n_res:
        if resnames_arr.size == positions.shape[1]:
            resnames_arr = resnames_arr[ca_indices]
        else:
            resnames_arr = np.array(["UNK"] * n_res, dtype="<U3")

    status["ok"] = True
    status["resid"] = resids_arr
    status["resname"] = resnames_arr
    status["rmsf_A"] = rmsf
    status["rmsf_mean"] = float(rmsf.mean())
    status["rmsf_median"] = float(np.median(rmsf))
    status["rmsf_max"] = float(rmsf.max())
    status["rmsf_min"] = float(rmsf.min())
    return status
