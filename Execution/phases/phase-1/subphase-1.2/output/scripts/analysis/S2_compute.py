#!/usr/bin/env python
"""S2_compute.py -- Lipari-Szabo S2 backbone N-H order parameters from MD trajectory.

Computes per-residue S2 from the autocorrelation of backbone N-H bond vectors.
Uses block-split (default 4 x 1.25 ns blocks for a 5 ns trajectory) to estimate
confidence intervals by bootstrapping over blocks.

Theory (Lipari & Szabo, JACS 1982; Smith / Lai & Brooks, JPCB 2024):
    S^2 = lim_{tau -> infty} <P2(mu(0).mu(tau))>
where P2(x) = (3x^2 - 1)/2 is the second-order Legendre polynomial, mu(t) is
the unit N-H bond vector at time t, and the angle brackets denote a time
average over a sufficiently long lag tau (typical ~1 ns plateau for folded
proteins). Assumes isotropic tumbling has been removed (we operate on
aligned trajectories so global rotation is suppressed; this is documented
as a caveat below).

I/O contract
    Inputs:
        traj_path : str | Path -- DCD/XTC/HDF5 trajectory of the production segment
        top_path  : str | Path -- topology with backbone atoms (PDB or PRMTOP)
        block_ns  : float      -- size of each block in ns (default 1.25)
        tau_ns    : float      -- correlation lag at which to read S2 (default 1.0)

    Outputs:
        dict with keys:
            'resid'         : (N_res,) int residue numbers (1-based)
            'resname'       : (N_res,) str three-letter residue names
            'S2_mean'       : (N_res,) float S2 per residue (block-mean)
            'S2_low'        : (N_res,) float lower 95% CI (block-bootstrap)
            'S2_high'       : (N_res,) float upper 95% CI
            'n_blocks'      : int number of blocks used
            'tau_ns'        : float plateau time used
            'block_ns'      : float block size

Caveats (Sub 1.4 SubAgent must surface in figures/text):
    * Isotropic tumbling assumption is approximate -- aligned trajectory
      kills global rotation; rotational diffusion contribution to NMR
      relaxation is NOT modelled here. Add iRED for rigorous comparison
      to BMRB, or use isotropic-tumbling correction during back-calculation.
    * 5 ns is short for true plateau convergence on slow side chains;
      Lipari-Szabo S2 from short trajectories can be biased high by
      under-sampling. Block-bootstrap CIs help quantify this.
    * Proline residues lack backbone N-H -- skip and emit NaN with a flag.

Sub 1.4 SubAgent: implement the body using mdtraj.compute_NH_order_parameters
or MDAnalysis.analysis.encore plus a manual P2 autocorrelation. See
references in `README.md`.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np


# Default parameters (override per-protein if needed)
DEFAULT_BLOCK_NS = 1.25
DEFAULT_TAU_NS = 1.0
DEFAULT_BOOTSTRAP_RESAMPLES = 1000
DEFAULT_CI_PERCENTILES = (2.5, 97.5)


@dataclass
class S2Result:
    """Container for per-residue S2 + uncertainties."""
    resid: np.ndarray         # (N_res,) int
    resname: np.ndarray       # (N_res,) <U3
    s2_mean: np.ndarray       # (N_res,) float
    s2_low: np.ndarray        # (N_res,) float (lower CI)
    s2_high: np.ndarray       # (N_res,) float (upper CI)
    n_blocks: int
    tau_ns: float
    block_ns: float
    skipped_resid: list       # residues without N-H (e.g., PRO, N-terminal)


def _load_nh_vectors(traj_path: Path, top_path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Load N-H bond unit vectors and per-residue metadata.

    Returns
        nh_vectors : (n_frames, n_residues, 3) float64 unit vectors
        resids     : (n_residues,) int residue numbers
        resnames   : (n_residues,) <U3 residue names
        dt_ps      : float time step between frames in ps

    Sub 1.4: implement with mdtraj or MDAnalysis. PRO residues should be
    excluded here; record their resids in the caller.
    """
    raise NotImplementedError(
        "Sub 1.4 SubAgent: load trajectory with mdtraj.load(traj_path, top=top_path); "
        "select backbone N + H atoms (skip PRO); return unit vectors per frame per residue."
    )


def _autocorrelation_s2(nh_vectors: np.ndarray, dt_ps: float, tau_ns: float) -> np.ndarray:
    """Compute per-residue S2 from N-H bond vector autocorrelation.

    Implements C(tau) = <P2(mu(0).mu(tau))> averaged over time origins,
    then reads S2 = C(tau_plateau).

    Inputs:
        nh_vectors : (n_frames, n_residues, 3) unit vectors
        dt_ps      : time step in ps
        tau_ns     : plateau correlation time in ns

    Returns:
        s2 : (n_residues,) float
    """
    raise NotImplementedError(
        "Sub 1.4 SubAgent: for each residue compute P2(mu(0).mu(t)) averaged "
        "over time origins; locate plateau at tau_ns; return S2 per residue."
    )


def compute_s2(
    traj_path: str | Path,
    top_path: str | Path,
    block_ns: float = DEFAULT_BLOCK_NS,
    tau_ns: float = DEFAULT_TAU_NS,
    bootstrap_resamples: int = DEFAULT_BOOTSTRAP_RESAMPLES,
    ci_percentiles: tuple[float, float] = DEFAULT_CI_PERCENTILES,
) -> S2Result:
    """Compute Lipari-Szabo S2 with block-split bootstrap CIs.

    Procedure
        1. Load N-H bond vectors per frame per residue.
        2. Split trajectory into n_blocks = floor(traj_ns / block_ns) blocks.
        3. Compute per-residue S2 within each block.
        4. Bootstrap over blocks (resample with replacement) to get CIs.
        5. Return mean across blocks + 2.5/97.5 percentiles of bootstrap distribution.
    """
    nh, resids, resnames, dt_ps = _load_nh_vectors(Path(traj_path), Path(top_path))
    n_frames = nh.shape[0]
    traj_ns = n_frames * dt_ps / 1000.0
    frames_per_block = int(round(block_ns * 1000.0 / dt_ps))
    n_blocks = max(1, n_frames // frames_per_block)

    block_s2 = np.zeros((n_blocks, nh.shape[1]), dtype=np.float64)
    for b in range(n_blocks):
        start = b * frames_per_block
        end = start + frames_per_block
        block_s2[b] = _autocorrelation_s2(nh[start:end], dt_ps, tau_ns)

    # Block-bootstrap
    rng = np.random.default_rng(seed=42)
    bs_means = np.zeros((bootstrap_resamples, nh.shape[1]), dtype=np.float64)
    for r in range(bootstrap_resamples):
        idx = rng.integers(0, n_blocks, size=n_blocks)
        bs_means[r] = block_s2[idx].mean(axis=0)

    s2_mean = block_s2.mean(axis=0)
    s2_low = np.percentile(bs_means, ci_percentiles[0], axis=0)
    s2_high = np.percentile(bs_means, ci_percentiles[1], axis=0)

    return S2Result(
        resid=resids,
        resname=resnames,
        s2_mean=s2_mean,
        s2_low=s2_low,
        s2_high=s2_high,
        n_blocks=int(n_blocks),
        tau_ns=float(tau_ns),
        block_ns=float(block_ns),
        skipped_resid=[],
    )


def save_s2_npz(result: S2Result, out_path: str | Path) -> None:
    """Save S2 result to NPZ. Convention matches compute_rmsf_batch1.py."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        out,
        resid=result.resid,
        resname=result.resname,
        S2_mean=result.s2_mean,
        S2_low=result.s2_low,
        S2_high=result.s2_high,
        n_blocks=result.n_blocks,
        tau_ns=result.tau_ns,
        block_ns=result.block_ns,
    )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--input-traj", required=True, help="DCD/XTC/HDF5 trajectory")
    p.add_argument("--input-top", required=True, help="Topology PDB/PRMTOP")
    p.add_argument("--output-dir", required=True, help="Output directory")
    p.add_argument("--protein-id", required=True, help="Protein identifier (e.g., WW, GB3)")
    p.add_argument("--block-ns", type=float, default=DEFAULT_BLOCK_NS)
    p.add_argument("--tau-ns", type=float, default=DEFAULT_TAU_NS)
    args = p.parse_args()

    result = compute_s2(
        args.input_traj, args.input_top,
        block_ns=args.block_ns, tau_ns=args.tau_ns,
    )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    npz_path = out_dir / f"{args.protein_id}_S2.npz"
    save_s2_npz(result, npz_path)

    summary = {
        "protein_id": args.protein_id,
        "n_residues": int(result.resid.size),
        "n_blocks": result.n_blocks,
        "tau_ns": result.tau_ns,
        "block_ns": result.block_ns,
        "S2_mean_global": float(np.nanmean(result.s2_mean)),
        "S2_min": float(np.nanmin(result.s2_mean)),
        "S2_max": float(np.nanmax(result.s2_mean)),
        "skipped_resid": result.skipped_resid,
    }
    with (out_dir / f"{args.protein_id}_S2_summary.json").open("w") as f:
        json.dump(summary, f, indent=2)
    print(f"[S2] {args.protein_id}: {summary['n_residues']} residues, "
          f"S2_mean={summary['S2_mean_global']:.3f}, n_blocks={result.n_blocks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
