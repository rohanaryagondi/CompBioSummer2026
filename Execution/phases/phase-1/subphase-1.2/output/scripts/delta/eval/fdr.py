"""Multiple-testing correction for Delta (IP §12.4).

Provides:
  * fdr_bh — Benjamini-Hochberg, PRIMARY FDR method.
  * fdr_by — Benjamini-Yekutieli, SENSITIVITY analysis (dependence-robust).

Both return a dict:
  { "reject": bool[], "qvalues": float[], "alpha": float, "method": str }
"""
from __future__ import annotations

import numpy as np
from statsmodels.stats.multitest import multipletests


def _mt(p_values, alpha: float, method: str, label: str):
    p = np.asarray(p_values, dtype=np.float64)
    if p.ndim != 1:
        raise ValueError("p_values must be 1-D")
    reject, qvals, _, _ = multipletests(p, alpha=alpha, method=method)
    return {
        "reject": reject.astype(bool),
        "qvalues": qvals.astype(np.float64),
        "alpha": float(alpha),
        "method": label,
    }


def fdr_bh(p_values, alpha: float = 0.05):
    """Benjamini-Hochberg (primary)."""
    return _mt(p_values, alpha, "fdr_bh", "BH")


def fdr_by(p_values, alpha: float = 0.05):
    """Benjamini-Yekutieli (dependence-robust sensitivity)."""
    return _mt(p_values, alpha, "fdr_by", "BY")


def compare_bh_by(p_values, alpha: float = 0.05):
    """Run both corrections and summarise discrepancy."""
    bh = fdr_bh(p_values, alpha=alpha)
    by = fdr_by(p_values, alpha=alpha)
    n_bh = int(bh["reject"].sum())
    n_by = int(by["reject"].sum())
    overlap = int((bh["reject"] & by["reject"]).sum())
    return {
        "bh": bh,
        "by": by,
        "n_rejected_bh": n_bh,
        "n_rejected_by": n_by,
        "overlap": overlap,
        "bh_minus_by": n_bh - n_by,  # positive = BH finds more (expected)
    }
