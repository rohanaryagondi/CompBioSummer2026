"""Stratified evaluation for Delta (IP §12.4).

Runs `hierarchical_wmse_spearman` per stratum defined by:
  * cell_type
  * perturbation_type
  * expression_level (per-cell mean expression, bucketed into tertiles by default)

Returns a nested dict:
    {
      "cell_type":       {ct1: wmse_dict, ct2: wmse_dict, ...},
      "perturbation_type": {pt1: wmse_dict, ...},
      "expression_level":  {"low": wmse_dict, "mid": wmse_dict, "high": wmse_dict},
    }

A stratum is skipped (and recorded with `status="skipped-small"`) if it has
fewer than `min_rows` rows (default 20). This prevents nonsensical WMSE
estimates on tiny partitions.
"""
from __future__ import annotations

from typing import Dict
import numpy as np

from .wmse import hierarchical_wmse_spearman


def _bucket_expression(Y, n_buckets: int = 3):
    """Tertile bucket labels based on per-row mean expression."""
    means = np.asarray(Y).mean(axis=1)
    quantiles = np.quantile(means, np.linspace(0, 1, n_buckets + 1)[1:-1])
    labels = np.digitize(means, quantiles)  # 0..n_buckets-1
    names = ["low", "mid", "high"] if n_buckets == 3 else [f"q{i}" for i in range(n_buckets)]
    return np.array([names[i] for i in labels])


def stratified_evaluation(
    pred, true,
    cell_type=None, perturbation_type=None, expression_level=None,
    min_rows: int = 20, top_k: int = 20, alpha: float = 0.05,
    n_perm: int = 100, seed: int = 0,
) -> Dict:
    """Compute per-stratum hierarchical WMSE/Spearman.

    `expression_level` can be an array of labels OR None (will be computed
    from `true` as tertiles of per-row mean expression).
    """
    pred = np.asarray(pred)
    true = np.asarray(true)
    n = true.shape[0]

    strata = {}
    if cell_type is not None:
        strata["cell_type"] = np.asarray(cell_type)
    if perturbation_type is not None:
        strata["perturbation_type"] = np.asarray(perturbation_type)
    if expression_level is None:
        strata["expression_level"] = _bucket_expression(true, n_buckets=3)
    else:
        strata["expression_level"] = np.asarray(expression_level)

    out = {}
    for stratum_name, labels in strata.items():
        assert len(labels) == n, f"label length {len(labels)} != n_rows {n}"
        per_label = {}
        for label in np.unique(labels):
            mask = labels == label
            c = int(mask.sum())
            if c < min_rows:
                per_label[str(label)] = {"status": "skipped-small", "n": c}
                continue
            r = hierarchical_wmse_spearman(
                pred[mask], true[mask],
                top_k=top_k, alpha=alpha, n_perm=n_perm, seed=seed,
            )
            r["n"] = c
            per_label[str(label)] = r
        out[stratum_name] = per_label
    return out
