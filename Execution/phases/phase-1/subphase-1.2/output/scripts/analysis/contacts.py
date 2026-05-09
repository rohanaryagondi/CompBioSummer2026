#!/usr/bin/env python
"""contacts.py -- Cα-Cα residue-residue contact analysis for MD trajectories.

Used to track structural integrity over an MD trajectory by comparing the
contact map at each frame to the contact map of the starting / reference
structure. Detects loss of native contacts and formation of novel contacts,
which are downstream signals for unfolding, partial misfolding, or
PME-pressure-driven artefacts in MLFF NPT runs.

I/O contract
    Inputs:
        traj_path : str | Path -- DCD/XTC/HDF5 trajectory
        top_path  : str | Path -- topology with at least Cα atoms
        ref_path  : str | Path | None -- reference structure (PDB) for
            'native' contact reference. If None, frame 0 is used.
        cutoff_A  : float      -- Cα-Cα distance threshold in Angstroms (default 7.0)
        seq_separation : int   -- minimum |i-j| residue separation for a "contact"
            to filter out backbone-adjacent pairs (default 4; matches typical
            Q-score conventions)

    Outputs (returned dict + optional NPZ + summary JSON):
        contact_evolution : (n_frames, n_residue_pairs) bool -- frame-by-frame
            contact matrix (sparse-friendly)
        native_contacts   : (n_residue_pairs,) bool -- reference contact map
        fraction_native   : (n_frames,) float -- Q-score per frame
        novel_contacts_per_frame : (n_frames,) int -- contacts present that are
            not in the native map
        summary statistics (mean Q, min Q, novel-contact fraction at end, etc.)

Sub 1.4 SubAgent: implement using mdtraj.compute_contacts(scheme='ca') or
MDAnalysis distance_array on Cα selection. Q-score formulation follows
Best, Hummer, Eaton (PNAS 2013): Q = mean over native pairs of theta(d - d_ref).
For simplicity here we use a hard cutoff (theta = step function); soft Q-score
with sigmoid is documented as a future extension.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np


DEFAULT_CUTOFF_A = 7.0
DEFAULT_SEQ_SEPARATION = 4


@dataclass
class ContactResult:
    """Container for contact-map analysis."""
    n_frames: int
    n_residues: int
    n_pairs: int
    cutoff_A: float
    seq_separation: int
    pair_indices: np.ndarray          # (n_pairs, 2) int residue indices
    native_contacts: np.ndarray       # (n_pairs,) bool
    fraction_native: np.ndarray       # (n_frames,) float, Q-score in [0,1]
    novel_contacts_per_frame: np.ndarray  # (n_frames,) int
    contact_evolution: np.ndarray     # (n_frames, n_pairs) bool (optional, large)


def _load_ca_positions(traj_path: Path, top_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Load Cα positions for all frames.

    Returns
        ca_xyz : (n_frames, n_residues, 3) float64 in Angstroms
        resids : (n_residues,) int
    """
    raise NotImplementedError(
        "Sub 1.4 SubAgent: implement with mdtraj.load(traj, top=top).atom_slice("
        "topology.select('name CA')) or MDAnalysis equivalent. Convert nm->A "
        "if mdtraj is used."
    )


def _load_reference_ca(ref_path: Path) -> np.ndarray:
    """Load Cα positions from a reference PDB. Returns (n_residues, 3) in A."""
    raise NotImplementedError(
        "Sub 1.4 SubAgent: parse reference PDB; return Cα positions in Angstroms."
    )


def _pairs_above_separation(n_res: int, sep: int) -> np.ndarray:
    """Generate residue index pairs (i, j) with j - i >= sep.

    Returns (n_pairs, 2) int array.
    """
    pairs = []
    for i in range(n_res):
        for j in range(i + sep, n_res):
            pairs.append((i, j))
    return np.asarray(pairs, dtype=np.int64)


def _contact_matrix(positions: np.ndarray, pairs: np.ndarray, cutoff_A: float) -> np.ndarray:
    """Compute boolean contact vector for given pairs.

    positions : (n_residues, 3)
    pairs     : (n_pairs, 2)
    Returns   : (n_pairs,) bool
    """
    diff = positions[pairs[:, 0]] - positions[pairs[:, 1]]
    d = np.linalg.norm(diff, axis=1)
    return d < cutoff_A


def analyze_contacts(
    traj_path: str | Path,
    top_path: str | Path,
    ref_path: str | Path | None = None,
    cutoff_A: float = DEFAULT_CUTOFF_A,
    seq_separation: int = DEFAULT_SEQ_SEPARATION,
    store_full_evolution: bool = False,
) -> ContactResult:
    """Compute contact map evolution + Q-score per frame.

    If `store_full_evolution=False`, the full (n_frames, n_pairs) bool matrix
    is replaced with an empty array to save memory; only summary statistics
    and per-frame Q + novel counts are stored. Default is False.
    """
    ca, resids = _load_ca_positions(Path(traj_path), Path(top_path))
    n_frames, n_res, _ = ca.shape

    pairs = _pairs_above_separation(n_res, seq_separation)

    # Reference contacts: from ref_path (if given) or frame 0
    if ref_path is not None:
        ref_ca = _load_reference_ca(Path(ref_path))
    else:
        ref_ca = ca[0]
    native = _contact_matrix(ref_ca, pairs, cutoff_A)
    n_native = int(native.sum())

    fraction_native = np.zeros(n_frames, dtype=np.float64)
    novel = np.zeros(n_frames, dtype=np.int64)
    evol = np.zeros((n_frames, pairs.shape[0]), dtype=bool) if store_full_evolution else np.empty(0, dtype=bool)

    for k in range(n_frames):
        c = _contact_matrix(ca[k], pairs, cutoff_A)
        fraction_native[k] = float((c & native).sum()) / max(1, n_native)
        novel[k] = int((c & ~native).sum())
        if store_full_evolution:
            evol[k] = c

    return ContactResult(
        n_frames=int(n_frames),
        n_residues=int(n_res),
        n_pairs=int(pairs.shape[0]),
        cutoff_A=float(cutoff_A),
        seq_separation=int(seq_separation),
        pair_indices=pairs,
        native_contacts=native,
        fraction_native=fraction_native,
        novel_contacts_per_frame=novel,
        contact_evolution=evol,
    )


def save_contact_result(result: ContactResult, out_path: str | Path) -> None:
    """Save contact result NPZ + summary JSON."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        out,
        pair_indices=result.pair_indices,
        native_contacts=result.native_contacts,
        fraction_native=result.fraction_native,
        novel_contacts_per_frame=result.novel_contacts_per_frame,
        n_residues=result.n_residues,
        cutoff_A=result.cutoff_A,
    )


def summarize(result: ContactResult) -> dict:
    return {
        "n_frames": result.n_frames,
        "n_residues": result.n_residues,
        "n_native_pairs": int(result.native_contacts.sum()),
        "Q_mean": float(result.fraction_native.mean()),
        "Q_min": float(result.fraction_native.min()),
        "Q_final": float(result.fraction_native[-1]),
        "novel_contacts_mean": float(result.novel_contacts_per_frame.mean()),
        "novel_contacts_final": int(result.novel_contacts_per_frame[-1]),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--input-traj", required=True)
    p.add_argument("--input-top", required=True)
    p.add_argument("--reference", default=None, help="Optional reference PDB")
    p.add_argument("--output-dir", required=True)
    p.add_argument("--protein-id", required=True)
    p.add_argument("--cutoff-A", type=float, default=DEFAULT_CUTOFF_A)
    p.add_argument("--seq-separation", type=int, default=DEFAULT_SEQ_SEPARATION)
    p.add_argument("--store-full-evolution", action="store_true",
                   help="Store the per-frame contact matrix (large; off by default).")
    args = p.parse_args()

    result = analyze_contacts(
        args.input_traj, args.input_top, ref_path=args.reference,
        cutoff_A=args.cutoff_A, seq_separation=args.seq_separation,
        store_full_evolution=args.store_full_evolution,
    )
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    save_contact_result(result, out / f"{args.protein_id}_contacts.npz")
    summary = summarize(result)
    summary["protein_id"] = args.protein_id
    with (out / f"{args.protein_id}_contacts_summary.json").open("w") as f:
        json.dump(summary, f, indent=2)
    print(f"[contacts] {args.protein_id}: Q_mean={summary['Q_mean']:.3f} "
          f"Q_min={summary['Q_min']:.3f} novel_final={summary['novel_contacts_final']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
