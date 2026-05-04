"""Weighted MSE + hierarchical WMSE->Spearman gate (IP §12.4).

IP §12.4 specifies:
    1. WMSE is the primary metric.
    2. Spearman on top-k DEGs is REPORTED ONLY IF WMSE is significantly better
       than random (hierarchical testing closes the top-k metric-gaming door).

Weighting choice (w_g = 1 / (var_g + eps)) is gene-wise inverse variance so
that low-variance housekeeping genes (which all methods predict trivially
well) don't dominate MSE. This is the Ahlmann-Eltze / scPerturBench default.

`hierarchical_wmse_spearman` returns:
    {
      "wmse"         : float       — primary metric
      "wmse_p"       : float       — permutation p under H0 of random prediction
      "wmse_baseline_mean" : float — mean WMSE of n_perm random permutations
      "wmse_z"       : float       — (wmse_baseline - wmse) / sigma(wmse_baseline)
      "spearman_topk": float|None  — None iff gate fails
      "n_pass_topk"  : int         — per-row correlations with |rho| >= 0 non-NaN
      "top_k"        : int
      "gate"         : "PASS" | "FAIL"
    }

Gate semantics: PASS iff WMSE is significantly better (smaller) than random
permutations at level alpha. FAIL is the expected outcome for the random
baseline (that is the metric-gaming calibration check).
"""
from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr


def wmse(pred, true, weights=None, eps: float = 1e-6) -> float:
    """Weighted mean squared error per gene.

    Default weight is 1 / (gene-wise variance of `true` + eps). Pass
    `weights=np.ones(n_genes)` for unweighted MSE.
    """
    pred = np.asarray(pred, dtype=np.float64)
    true = np.asarray(true, dtype=np.float64)
    assert pred.shape == true.shape, f"shape mismatch: {pred.shape} vs {true.shape}"
    per_gene_mse = np.mean((pred - true) ** 2, axis=0)  # (n_genes,)
    if weights is None:
        weights = 1.0 / (true.var(axis=0) + eps)
    weights = np.asarray(weights, dtype=np.float64)
    assert weights.shape == per_gene_mse.shape
    return float(np.average(per_gene_mse, weights=weights))


def _random_permutation_wmses(true, weights, n_perm=100, seed=0):
    """Null distribution of WMSE under random prediction (permute true rows).

    We permute `true` rather than `pred` so the *null* corresponds to "your
    prediction explains nothing." A smaller wmse than the null means the
    prediction is informative. This matches the IP §12.4 metric-gaming check.
    """
    rng = np.random.default_rng(seed)
    nulls = np.empty(n_perm, dtype=np.float64)
    for i in range(n_perm):
        perm = rng.permutation(true.shape[0])
        nulls[i] = wmse(true[perm], true, weights=weights)
    return nulls


def _top_k_deg_indices(true, top_k=20):
    """Pick genes with the largest absolute deviation from the global mean.

    Matches IP §12.4 "top-k DEGs" — differentially expressed genes selected by
    absolute fold-change in `true`. With log1p counts this is |log1p| not raw
    fold-change, but the ranking is what the harness needs.
    """
    if true.shape[1] <= top_k:
        return np.arange(true.shape[1])
    fold = np.abs(true - true.mean(axis=0, keepdims=True)).max(axis=0)
    return np.argsort(fold)[-top_k:]


def hierarchical_wmse_spearman(pred, true, top_k: int = 20, alpha: float = 0.05,
                               n_perm: int = 100, seed: int = 0, weights=None):
    """WMSE gate then Spearman-top-k (IP §12.4).

    Returns a dict; see module docstring.
    """
    pred = np.asarray(pred, dtype=np.float64)
    true = np.asarray(true, dtype=np.float64)
    if pred.shape != true.shape:
        raise ValueError(f"shape mismatch: {pred.shape} vs {true.shape}")

    # Weights fixed from true so every method is evaluated on the same axis-weighting.
    if weights is None:
        weights = 1.0 / (true.var(axis=0) + 1e-6)

    wmse_val = wmse(pred, true, weights=weights)

    # Null distribution of WMSE under random prediction (row-shuffling true).
    null = _random_permutation_wmses(true, weights, n_perm=n_perm, seed=seed)
    # One-sided p: fraction of nulls with wmse <= observed (i.e., observed is NOT
    # significantly smaller than null).
    p = float((null <= wmse_val).mean())
    null_mean = float(null.mean())
    null_std = float(null.std(ddof=1) + 1e-12)
    z = (null_mean - wmse_val) / null_std  # positive = observed beats null

    if p > alpha:
        return {
            "wmse": wmse_val,
            "wmse_p": p,
            "wmse_baseline_mean": null_mean,
            "wmse_z": z,
            "spearman_topk": None,
            "n_pass_topk": 0,
            "top_k": int(top_k),
            "gate": "FAIL",
        }

    # Gate passed — compute Spearman on top-k DEGs per row, vectorised.
    top_idx = _top_k_deg_indices(true, top_k=top_k)
    a = pred[:, top_idx]
    b = true[:, top_idx]
    # rank-transform along axis=1; spearman == pearson on ranks.
    def _rankdata_axis1(arr):
        # scipy.stats.rankdata axis= is supported but slow on very wide arrays;
        # numpy argsort twice (double argsort trick) is the fastest pure-numpy
        # rank transform and works fine for ties with average method when
        # deduplicated via a small stabilisation. For the top-k DEG use case
        # (k=20), the fraction of ties is negligible so a plain double-argsort
        # is sufficient and O(n*k*log(k)).
        order = np.argsort(arr, axis=1, kind="mergesort")
        ranks = np.empty_like(order)
        idx_col = np.arange(arr.shape[1])
        ranks[np.arange(arr.shape[0])[:, None], order] = idx_col[None, :]
        return ranks.astype(np.float64)

    a_r = _rankdata_axis1(a)
    b_r = _rankdata_axis1(b)
    a_mean = a_r.mean(axis=1, keepdims=True)
    b_mean = b_r.mean(axis=1, keepdims=True)
    a_c = a_r - a_mean
    b_c = b_r - b_mean
    num = (a_c * b_c).sum(axis=1)
    denom = np.sqrt((a_c ** 2).sum(axis=1) * (b_c ** 2).sum(axis=1))
    rhos = np.where(denom > 0, num / denom, np.nan)
    rhos_finite = rhos[np.isfinite(rhos)]
    spearman_mean = float(rhos_finite.mean()) if rhos_finite.size else float("nan")
    n_valid = int(rhos_finite.size)

    return {
        "wmse": wmse_val,
        "wmse_p": p,
        "wmse_baseline_mean": null_mean,
        "wmse_z": z,
        "spearman_topk": spearman_mean,
        "n_pass_topk": n_valid,
        "top_k": int(top_k),
        "gate": "PASS",
    }
