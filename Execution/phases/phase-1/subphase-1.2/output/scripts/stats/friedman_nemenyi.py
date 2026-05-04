"""
friedman_nemenyi -- Friedman test + Nemenyi post-hoc (Alpha-M primary test).

Per IP §12.1: the primary Alpha-M test is a Friedman test (non-parametric repeated
measures across k conditions) with Nemenyi post-hoc for pairwise generator
comparisons. Each row is a protein; each column is one generator's S2 R^2 to
experimental NMR.

The Friedman test ranks generators within each protein, then tests whether the
mean rank differs across generators. Nemenyi is the standard post-hoc for the
Friedman test and uses the studentized range distribution to control family-wise
error across all pairs.

Dependencies: scipy (>=1.10), scikit-posthocs (>=0.7).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import scikit_posthocs as sp
from scipy.stats import friedmanchisquare


def friedman_nemenyi(
    data: np.ndarray | pd.DataFrame,
    alpha: float = 0.05,
    generator_names: Optional[Sequence[str]] = None,
) -> Dict:
    """Run Friedman omnibus + Nemenyi post-hoc on a (proteins x generators) table.

    Parameters
    ----------
    data
        2-D array-like, shape ``(n_proteins, n_generators)``. Each row is a
        protein; each column is one generator's score (e.g., S2 R^2 to NMR).
        Higher is better. No missing values allowed (drop incomplete rows before
        calling). ``n_generators >= 3`` is required by the Friedman test.
    alpha
        Family-wise error rate used to flag significant pairwise Nemenyi
        comparisons. Default ``0.05``.
    generator_names
        Optional labels for the columns. If ``None``, integer indices are used
        in the returned ``pairwise_p`` DataFrame.

    Returns
    -------
    dict with keys
        ``chi2`` : float -- Friedman chi-square statistic
        ``p_value`` : float -- Friedman omnibus p-value
        ``df`` : int -- degrees of freedom = n_generators - 1
        ``n_proteins`` : int
        ``n_generators`` : int
        ``pairwise_p`` : pd.DataFrame -- symmetric matrix of Nemenyi p-values
        ``significant_pairs`` : List[Tuple[str, str, float]] -- (a, b, p) tuples
            with ``p < alpha``, ``a != b``, de-duplicated (a < b by index).
        ``mean_ranks`` : pd.Series -- Friedman mean rank per generator; lower =
            better when scores are "higher-is-better" (scipy ranks ties by mean).

    Notes
    -----
    * Assumes ``data`` scores are "higher = better" (the Alpha-M convention for
      S2 R^2). Mean-rank inversion is handled here so that the generator with
      the highest mean rank is the "best" in the returned Series.
    * Nemenyi uses the studentized-range approximation; for small k it is
      slightly conservative vs asymptotic chi-square. Acceptable for Alpha-M
      where we want conservative family-wise error control.
    """
    # Coerce to ndarray + DataFrame pair
    if isinstance(data, pd.DataFrame):
        df = data.copy()
        arr = df.to_numpy(dtype=float)
        if generator_names is None:
            generator_names = list(df.columns)
    else:
        arr = np.asarray(data, dtype=float)
        if arr.ndim != 2:
            raise ValueError(f"data must be 2-D; got shape {arr.shape}")
        df = pd.DataFrame(
            arr,
            columns=(
                list(generator_names)
                if generator_names is not None
                else list(range(arr.shape[1]))
            ),
        )

    n_proteins, n_generators = arr.shape
    if n_generators < 3:
        raise ValueError(
            f"Friedman test requires >=3 generators; got {n_generators}"
        )
    if n_proteins < 2:
        raise ValueError(
            f"Friedman test requires >=2 proteins; got {n_proteins}"
        )
    if np.isnan(arr).any():
        raise ValueError(
            "NaN found in data; drop incomplete proteins before calling."
        )

    # Friedman omnibus
    chi2, p = friedmanchisquare(*arr.T)
    df_friedman = n_generators - 1

    # Nemenyi post-hoc: scikit-posthocs expects shape (n_blocks, n_conditions)
    # i.e., rows = proteins (blocks), columns = generators (treatments).
    pairwise = sp.posthoc_nemenyi_friedman(arr)
    pairwise.index = list(df.columns)
    pairwise.columns = list(df.columns)

    # Significant pairs (de-duplicated, i < j by column-name order)
    cols = list(df.columns)
    sig_pairs: List[Tuple[object, object, float]] = []
    for i, a in enumerate(cols):
        for j, b in enumerate(cols):
            if j <= i:
                continue
            pv = float(pairwise.iloc[i, j])
            if pv < alpha:
                sig_pairs.append((a, b, pv))
    sig_pairs.sort(key=lambda t: t[2])  # by p-value ascending

    # Mean ranks per generator. scipy.stats ranks ties by mean; we want
    # "best = highest rank" for higher-is-better metrics. So rank by
    # -score across each row (smaller rank = better). Then invert.
    ranks_per_protein = np.apply_along_axis(_rankdata_higher_better, 1, arr)
    mean_ranks = pd.Series(
        ranks_per_protein.mean(axis=0),
        index=df.columns,
        name="mean_rank_higher_better",
    )

    return {
        "chi2": float(chi2),
        "p_value": float(p),
        "df": int(df_friedman),
        "n_proteins": int(n_proteins),
        "n_generators": int(n_generators),
        "pairwise_p": pairwise,
        "significant_pairs": sig_pairs,
        "mean_ranks": mean_ranks,
    }


def _rankdata_higher_better(row: np.ndarray) -> np.ndarray:
    """Rank a row so that the largest value has rank n_generators.

    Ties get average ranks (scipy 'average' method).
    """
    from scipy.stats import rankdata

    return rankdata(row, method="average")


__all__ = ["friedman_nemenyi"]
