"""
hierarchical_bootstrap -- 2-level bootstrap (proteins, then residues).

Per IP §12.1 + §14.1 reviewer-attack pre-emption ("Per-residue analysis inflates
N"): a standard 1-level bootstrap over per-residue observations
underestimates sampling variance because residues within a protein are not
independent. The fix is a 2-level hierarchical bootstrap:
    Level 1: resample proteins WITH replacement (n_proteins bootstrap proteins)
    Level 2: for each resampled protein, resample its residues WITH replacement

The resampled aggregate is then passed to the statistic of interest. The
procedure is repeated ``n_iterations`` times; default 10,000 (IP §12.1 spec).

Implementation is pure NumPy -- no GPU, no heavy deps. Runtime scales as
O(n_iterations * n_total_residues) for simple statistics like the mean.
"""

from __future__ import annotations

from typing import Callable, Dict, Optional, Sequence

import numpy as np


def hierarchical_bootstrap(
    data: np.ndarray,
    level1_idx: np.ndarray,
    statistic: Callable[[np.ndarray], float] = np.mean,
    n_iterations: int = 10_000,
    seed: Optional[int] = 42,
) -> np.ndarray:
    """Run a 2-level hierarchical bootstrap.

    Level 1: resample proteins with replacement.
    Level 2: within each resampled protein, resample residues with replacement.

    Parameters
    ----------
    data
        1-D array of per-residue values (e.g., S2 R^2 per residue across all
        proteins). Length ``N_total_residues``.
    level1_idx
        Same length as ``data``. Integer (or string) protein ID per residue.
        Protein membership must be consistent across ``data``.
    statistic
        Callable that takes a 1-D array and returns a scalar (the bootstrap
        statistic). Default ``np.mean``.
    n_iterations
        Number of bootstrap iterations. Default 10,000.
    seed
        Seed for ``numpy.random.default_rng``. Set to ``None`` for unseeded.

    Returns
    -------
    np.ndarray, shape (n_iterations,)
        The bootstrap distribution of ``statistic``.

    Notes
    -----
    * We cache the per-protein index lists ONCE before the loop to avoid a
      per-iteration O(N) mask scan (critical for 10K iterations).
    * We resample residues with replacement WITHIN each resampled protein with
      the same number of residues as that protein contains. This is the
      "pairs-bootstrap" form of the 2-level design used in IP §12.1.
    * For k bootstrap iterations of N residues total, the memory cost is
      ``8 * k`` bytes for the result + temporary buffers; safe to scale to
      10K+ iterations on commodity CPU.
    """
    data = np.asarray(data)
    level1_idx = np.asarray(level1_idx)
    if data.shape != level1_idx.shape:
        raise ValueError(
            f"data and level1_idx must have same shape; got "
            f"{data.shape} vs {level1_idx.shape}"
        )
    if data.ndim != 1:
        raise ValueError(f"data must be 1-D; got ndim={data.ndim}")
    if n_iterations < 1:
        raise ValueError(f"n_iterations must be >=1; got {n_iterations}")

    rng = np.random.default_rng(seed)

    # Cache per-protein residue-row indices (NOT residue counts -- we need the
    # actual positions for level-2 resampling).
    unique_proteins, inverse = np.unique(level1_idx, return_inverse=True)
    n_proteins = len(unique_proteins)
    # protein_rows[p] = ndarray of integer rows in `data` that belong to protein p
    protein_rows = [np.where(inverse == p)[0] for p in range(n_proteins)]
    protein_sizes = np.array([len(r) for r in protein_rows])

    out = np.empty(n_iterations, dtype=float)

    for it in range(n_iterations):
        # Level 1: sample proteins WITH replacement (n_proteins of them).
        sampled_p = rng.integers(0, n_proteins, size=n_proteins)
        # Level 2: for each sampled protein, resample its residues WITH replacement.
        # We accumulate row-indices into `data`, then index once at the end for speed.
        total_rows = int(protein_sizes[sampled_p].sum())
        row_buf = np.empty(total_rows, dtype=np.int64)
        pos = 0
        for p in sampled_p:
            n_r = protein_sizes[p]
            # sample n_r residues with replacement from this protein's rows
            sampled_rows = rng.choice(protein_rows[p], size=n_r, replace=True)
            row_buf[pos : pos + n_r] = sampled_rows
            pos += n_r
        resampled = data[row_buf]
        out[it] = float(statistic(resampled))

    return out


def bootstrap_ci(
    bootstrap_dist: np.ndarray, alpha: float = 0.05
) -> Dict[str, float]:
    """Percentile CI from a bootstrap distribution.

    Parameters
    ----------
    bootstrap_dist
        1-D array, output of :func:`hierarchical_bootstrap`.
    alpha
        Two-sided alpha; default 0.05 -> 95% CI.

    Returns
    -------
    dict
        ``mean``, ``median``, ``ci_lo``, ``ci_hi``, ``se`` (std of the
        bootstrap distribution).
    """
    lo = float(np.quantile(bootstrap_dist, alpha / 2))
    hi = float(np.quantile(bootstrap_dist, 1 - alpha / 2))
    return {
        "mean": float(bootstrap_dist.mean()),
        "median": float(np.median(bootstrap_dist)),
        "ci_lo": lo,
        "ci_hi": hi,
        "se": float(bootstrap_dist.std(ddof=1)),
    }


__all__ = ["hierarchical_bootstrap", "bootstrap_ci"]
