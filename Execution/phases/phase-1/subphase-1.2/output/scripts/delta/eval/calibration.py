"""Calibration metrics for Delta (IP §12.4).

Regression calibration for perturbation-response prediction:
    * reliability_diagram: bin predicted values, compute empirical mean of
      true values in each bin. A perfectly calibrated regressor traces y=x.
    * ece: expected calibration error = frequency-weighted |bin_pred_mean -
      bin_true_mean| over the reliability diagram.

All metrics are computed on flattened (cell, gene) pairs by default.
"""
from __future__ import annotations

import numpy as np


def reliability_diagram(pred, true, n_bins: int = 10, bin_strategy: str = "quantile"):
    """Return (bin_pred_means, bin_true_means, bin_counts).

    Args:
        pred, true   : arrays flattened to 1-D or (n_rows, n_genes); flattened internally.
        n_bins       : number of bins.
        bin_strategy : "quantile" (equal-mass) or "uniform" (equal-width over pred range).
    """
    p = np.asarray(pred, dtype=np.float64).ravel()
    t = np.asarray(true, dtype=np.float64).ravel()
    assert p.shape == t.shape, f"pred/true shape mismatch: {p.shape} vs {t.shape}"

    if bin_strategy == "quantile":
        # Equal-mass bins on pred.
        edges = np.quantile(p, np.linspace(0, 1, n_bins + 1))
        edges = np.unique(edges)  # collapse duplicate quantile edges for flat preds
    elif bin_strategy == "uniform":
        lo, hi = float(p.min()), float(p.max())
        if hi <= lo:
            hi = lo + 1e-6
        edges = np.linspace(lo, hi, n_bins + 1)
    else:
        raise ValueError(bin_strategy)

    # np.digitize: edges[i-1] <= x < edges[i] -> bin i (1..len(edges)-1)
    bin_idx = np.digitize(p, edges[1:-1], right=False)  # -> 0..n_bins-1

    bin_pred_means = np.full(len(edges) - 1, np.nan, dtype=np.float64)
    bin_true_means = np.full(len(edges) - 1, np.nan, dtype=np.float64)
    bin_counts = np.zeros(len(edges) - 1, dtype=np.int64)
    for b in range(len(edges) - 1):
        mask = bin_idx == b
        c = int(mask.sum())
        bin_counts[b] = c
        if c > 0:
            bin_pred_means[b] = p[mask].mean()
            bin_true_means[b] = t[mask].mean()

    return bin_pred_means, bin_true_means, bin_counts


def ece(pred, true, n_bins: int = 10, bin_strategy: str = "quantile") -> float:
    """Expected Calibration Error (weighted by bin count)."""
    bp, bt, bc = reliability_diagram(pred, true, n_bins=n_bins, bin_strategy=bin_strategy)
    mask = ~np.isnan(bp) & ~np.isnan(bt) & (bc > 0)
    if not mask.any():
        return float("nan")
    diff = np.abs(bp[mask] - bt[mask])
    weights = bc[mask].astype(np.float64)
    return float(np.average(diff, weights=weights))


def save_reliability_plot(pred, true, out_path: str,
                          n_bins: int = 10, title: str = "",
                          bin_strategy: str = "quantile"):
    """Save a PNG reliability plot. Requires matplotlib."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    bp, bt, bc = reliability_diagram(pred, true, n_bins=n_bins, bin_strategy=bin_strategy)
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    lo = float(min(np.nanmin(bp), np.nanmin(bt)))
    hi = float(max(np.nanmax(bp), np.nanmax(bt)))
    ax.plot([lo, hi], [lo, hi], "k--", lw=0.8, label="perfect calibration")
    mask = ~np.isnan(bp) & ~np.isnan(bt)
    sizes = (bc[mask] / (bc[mask].max() + 1e-9)) * 80 + 8
    ax.scatter(bp[mask], bt[mask], s=sizes, alpha=0.8, label="bin means")
    ax.set_xlabel("predicted expression (bin mean)")
    ax.set_ylabel("true expression (bin mean)")
    ece_val = ece(pred, true, n_bins=n_bins, bin_strategy=bin_strategy)
    ax.set_title(f"{title}\nECE = {ece_val:.4f}")
    ax.legend(loc="best", frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return ece_val
