"""
icc -- Intraclass Correlation Coefficient (ICC) with convergence correction.

Per IP §12.1 + §10.3:
- ICC(2,k): absolute agreement, two-way random-effects, average of k raters.
  Alpha-M S2 convergence criterion: ICC(2,k) > 0.80.
- ICC(2,1): absolute agreement, two-way random-effects, single rater.
  Alpha-M S2 convergence criterion: ICC(2,1) > 0.50.
- Convergence attenuation (IP §10.3): finite-length MD trajectories attenuate
  the measured ICC relative to the asymptotic (infinitely-long-trajectory) ICC.
  IP §10.3 notes this attenuation is typically ~15-25% (risk: "Convergence
  attenuation reduces power below 70%", mitigated by reporting corrected ICC).
  Sub 1.4 will estimate the empirical attenuation factor from block-split R^2
  on real pilot trajectories; for the pipeline we ship a documented
  correction-factor API with a default of 0.20 (midpoint of IP range).

Implementation: pingouin.intraclass_corr primary. Pingouin's ICC2/ICC2k follow
Shrout & Fleiss (1979) conventions and are numerically equivalent to R
psych::ICC within stochastic tolerance (verified in tests/test_icc.py).

Dependencies: pandas, pingouin (>=0.5.3).

References
----------
Shrout, P.E. & Fleiss, J.L. (1979). Intraclass correlations: uses in assessing
rater reliability. Psychological Bulletin, 86(2), 420-428.

Implementation Plan §12.1, §10.3:
"Convergence attenuation reduces power below 70% -- Probability 30%. Mitigation:
Report corrected ICC; add proteins if available."
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
import pingouin as pg


def icc_2k(
    data: pd.DataFrame,
    target_col: str,
    rater_col: str,
    value_col: str,
    ci: float = 0.95,
) -> Dict:
    """Compute ICC(2,k) and ICC(2,1) via pingouin.

    Two-way random effects, absolute agreement:
    - ICC(2,k): reliability of the average of k raters (Alpha-M uses k = number
      of replicate MD trajectories per protein-generator).
    - ICC(2,1): reliability of a single rater (one trajectory).

    Parameters
    ----------
    data
        Long-format DataFrame with columns ``target_col`` (subject id, e.g.
        protein), ``rater_col`` (rater id, e.g. replicate index), and
        ``value_col`` (numeric measurement, e.g. S2 R^2).
    target_col, rater_col, value_col
        Column names.
    ci
        Confidence-interval level for CI95-style columns (default ``0.95``).

    Returns
    -------
    dict with keys
        ``ICC2k`` : float -- absolute-agreement ICC for k raters
        ``ICC2_1`` : float -- absolute-agreement ICC for single rater
        ``CI_2k`` : Tuple[float, float] -- CI95 bounds for ICC(2,k)
        ``CI_2_1`` : Tuple[float, float] -- CI95 bounds for ICC(2,1)
        ``n_targets`` : int
        ``n_raters`` : int
        ``full_table`` : pd.DataFrame -- pingouin's full ICC table

    Notes
    -----
    * pingouin Type strings are ``'ICC2'`` (single rater) and ``'ICC2k'``
      (average of k raters). Both assume subjects and raters are random.
    * If the data is unbalanced (unequal replicates across proteins), pingouin
      handles it via aggregation; for MD replicates we expect balanced counts.
    """
    # Defensive: coerce to categorical-like where useful
    df = data[[target_col, rater_col, value_col]].copy()
    df[value_col] = pd.to_numeric(df[value_col])

    icc_tbl = pg.intraclass_corr(
        data=df,
        targets=target_col,
        raters=rater_col,
        ratings=value_col,
        nan_policy="raise",
    )
    # pingouin's 'Type' column encodes the 6 Shrout & Fleiss forms; naming is
    # version-dependent. Pingouin >=0.5.3 uses ``ICC(A,1)`` / ``ICC(A,k)`` for
    # the two-way random-effects absolute-agreement forms (equivalent to
    # ``ICC2`` / ``ICC2k`` in older pingouin releases and ``ICC(2,1)`` /
    # ``ICC(2,k)`` in Shrout & Fleiss 1979). Support both naming schemes.
    types = list(icc_tbl["Type"])
    single_candidates = ("ICC(A,1)", "ICC2", "ICC(2,1)")
    k_candidates = ("ICC(A,k)", "ICC2k", "ICC(2,k)")
    row_2 = icc_tbl.loc[icc_tbl["Type"].isin(single_candidates)]
    row_2k = icc_tbl.loc[icc_tbl["Type"].isin(k_candidates)]
    if row_2.empty or row_2k.empty:
        raise RuntimeError(
            f"pingouin did not return a recognisable ICC2/ICC2k row; types were: "
            f"{types}. Looked for any of {single_candidates} / {k_candidates}."
        )
    icc21 = float(row_2["ICC"].iloc[0])
    icc2k = float(row_2k["ICC"].iloc[0])
    # CI column name is 'CI95%' in pingouin; guard against column rename.
    ci_col = "CI95%" if "CI95%" in icc_tbl.columns else (
        "CI95" if "CI95" in icc_tbl.columns else None
    )
    if ci_col is None:
        ci_21 = (float("nan"), float("nan"))
        ci_2k = (float("nan"), float("nan"))
    else:
        ci_21 = _parse_ci(row_2[ci_col].iloc[0])
        ci_2k = _parse_ci(row_2k[ci_col].iloc[0])

    n_targets = df[target_col].nunique()
    n_raters = df[rater_col].nunique()

    return {
        "ICC2k": icc2k,
        "ICC2_1": icc21,
        "CI_2k": ci_2k,
        "CI_2_1": ci_21,
        "n_targets": int(n_targets),
        "n_raters": int(n_raters),
        "full_table": icc_tbl,
    }


def _parse_ci(ci_obj) -> Tuple[float, float]:
    """pingouin returns CI as list/np.ndarray. Normalise to (lo, hi) tuple."""
    arr = np.asarray(ci_obj, dtype=float).ravel()
    if arr.size != 2:
        return (float("nan"), float("nan"))
    return (float(arr[0]), float(arr[1]))


def convergence_correction(
    measured_icc: float,
    attenuation_factor: float = 0.20,
) -> float:
    """Apply the convergence-attenuation correction from IP §10.3.

    Model: finite-length trajectories attenuate the measured ICC by a factor
    ``(1 - a)`` where ``a`` is the per-trajectory attenuation (fraction of
    variance that is transient, i.e. not captured by the finite window).
    IP §10.3 gives the typical range as 15-25%; we use ``a = 0.20`` by default.

    ``true_icc ~= measured_icc / (1 - a)``

    When ``a = 0.20``, a measured ICC of 0.68 corrects to 0.85.

    Parameters
    ----------
    measured_icc
        ICC estimated from finite trajectories (e.g., 50-100 ns per replicate).
        Typically in [0, 1]; values outside will still be corrected but should
        be inspected.
    attenuation_factor
        Fraction of variance attributable to finite-trajectory attenuation.
        IP §10.3 range: 0.15-0.25. Default 0.20 (midpoint). Sub 1.4 should
        replace this with an empirical estimate from block-split R^2 on
        pilot trajectories (see IP §10.3 mitigation).

    Returns
    -------
    float
        Corrected ICC estimate. Bounded to max 1.0 when the correction
        pushes the estimate above unity (unusual, but possible if
        attenuation_factor overestimates).

    Notes
    -----
    * If ``attenuation_factor`` is 0, returns ``measured_icc`` unchanged.
    * Raises ``ValueError`` for ``attenuation_factor >= 1`` (division by zero
      or worse).
    * The correction is deterministic; propagating CIs through the correction
      is left to the caller (linear scaling preserves relative CI width).
    """
    if attenuation_factor >= 1.0:
        raise ValueError(
            f"attenuation_factor must be <1; got {attenuation_factor}"
        )
    if attenuation_factor < 0:
        raise ValueError(
            f"attenuation_factor must be >=0; got {attenuation_factor}"
        )
    corrected = measured_icc / (1.0 - attenuation_factor)
    # Cap at 1.0 -- an ICC > 1 is not physically meaningful.
    if corrected > 1.0:
        return 1.0
    return float(corrected)


def estimate_attenuation_from_blocks(
    block_a_scores: np.ndarray,
    block_b_scores: np.ndarray,
) -> float:
    """Estimate the attenuation factor from a block-split R^2 analysis.

    For each protein-generator, split the trajectory into two halves (blocks A
    and B); compute the per-residue S2 for each block; correlate. The
    block-split correlation ``rho_ab`` is an estimate of the true-score
    correlation; if ``rho_ab < 1``, the shortfall is attenuation.

    Spearman-Brown step-up: given the split-half correlation ``rho_ab``, the
    full-length reliability estimate is ``rho_full = 2 * rho_ab / (1 + rho_ab)``.
    The attenuation factor for a single half-length trajectory is then
    ``a ~= 1 - rho_ab``.

    Parameters
    ----------
    block_a_scores, block_b_scores
        Arrays of matched per-residue (or per-protein) scores from the two
        trajectory halves. Must be the same length and ordering.

    Returns
    -------
    float
        Estimated attenuation factor ``a = 1 - rho_ab``, clipped to [0, 0.5].
    """
    if block_a_scores.shape != block_b_scores.shape:
        raise ValueError(
            f"block shapes differ: {block_a_scores.shape} vs {block_b_scores.shape}"
        )
    if block_a_scores.size < 3:
        raise ValueError("Need >=3 paired observations to estimate correlation.")
    rho = float(np.corrcoef(block_a_scores, block_b_scores)[0, 1])
    a = 1.0 - rho
    # Clip to a sane range: negative attenuation is nonsense; >50% is implausible.
    return float(max(0.0, min(0.5, a)))


__all__ = [
    "icc_2k",
    "convergence_correction",
    "estimate_attenuation_from_blocks",
]
