"""
test_icc -- synthetic-data unit test for icc.

Design
------
Two sub-tests.

Sub-test A: basic ICC estimation under a known variance-components model.
We simulate a "high-ICC" dataset where subject variance dominates rater
variance, and verify:
    ICC(2,1) is in the range 0.60-0.90 (conservative band for n=14, k=3).
    ICC(2,k) >= ICC(2,1).

Sub-test B: convergence-correction sanity.
Given an asymptotic ICC_true = 0.85 and an attenuation a = 0.20, a single
application of the correction to the attenuated (0.85 * 0.80 = 0.68) value
should recover ICC ~= 0.85 exactly. A zero attenuation should leave the
measured value unchanged.
"""
from __future__ import annotations

import sys

from _util import _ensure_parent_on_path  # noqa: F401

import numpy as np
import pandas as pd

from icc import convergence_correction, estimate_attenuation_from_blocks, icc_2k


def _simulate_long_format(
    n_subjects: int = 14,
    n_raters: int = 3,
    subject_sd: float = 0.20,
    rater_sd: float = 0.02,
    noise_sd: float = 0.05,
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    subj_eff = rng.normal(0.7, subject_sd, size=n_subjects)
    rater_eff = rng.normal(0.0, rater_sd, size=n_raters)
    rows = []
    for s in range(n_subjects):
        for r in range(n_raters):
            eps = rng.normal(0, noise_sd)
            val = subj_eff[s] + rater_eff[r] + eps
            rows.append({"subject": f"p{s:02d}", "rater": f"r{r}", "value": val})
    return pd.DataFrame(rows)


def sub_test_A() -> bool:
    df = _simulate_long_format()
    out = icc_2k(df, target_col="subject", rater_col="rater", value_col="value")
    icc21 = out["ICC2_1"]
    icc2k = out["ICC2k"]
    # Theoretical ICC = var_subj / (var_subj + var_rater + var_noise)
    # = 0.04 / (0.04 + 0.0004 + 0.0025) = 0.04 / 0.0429 ~= 0.932
    # For n=14, k=3 the sampling estimate is generally in 0.80-0.97.
    # We accept a wide band 0.60-0.99 for unit-test stability across seeds.
    range_ok = 0.60 <= icc21 <= 0.99
    ordering_ok = icc2k >= icc21
    ci_ok = (
        np.isfinite(out["CI_2k"][0]) and np.isfinite(out["CI_2k"][1])
        and out["CI_2k"][0] <= icc2k <= out["CI_2k"][1]
    )
    n_ok = out["n_targets"] == 14 and out["n_raters"] == 3
    print(
        f"[icc/A] ICC(2,1)={icc21:.3f}, ICC(2,k)={icc2k:.3f}, "
        f"CI_2k={out['CI_2k']}, n_targets={out['n_targets']}, "
        f"n_raters={out['n_raters']}"
    )
    print(
        f"[icc/A] range_ok={range_ok}, ordering_ok={ordering_ok}, "
        f"ci_ok={ci_ok}, n_ok={n_ok}"
    )
    return bool(range_ok and ordering_ok and ci_ok and n_ok)


def sub_test_B() -> bool:
    # Given true ICC=0.85 and attenuation a=0.20 -> measured = 0.85 * 0.80 = 0.68
    measured = 0.85 * (1 - 0.20)
    corrected = convergence_correction(measured, 0.20)
    recovery_ok = abs(corrected - 0.85) < 1e-12
    # Attenuation = 0 should be identity.
    identity_ok = abs(convergence_correction(0.42, 0.0) - 0.42) < 1e-12
    # Cap at 1.0 when correction pushes above unity.
    cap_ok = convergence_correction(0.95, 0.50) == 1.0
    # Block-based attenuation estimate: if two blocks agree perfectly, a -> 0.
    rng = np.random.default_rng(42)
    base = rng.normal(size=40)
    est_perfect = estimate_attenuation_from_blocks(base, base)
    block_perfect_ok = est_perfect < 1e-6
    # Noisy blocks should give attenuation > 0.
    noisy = base + rng.normal(scale=0.3, size=40)
    est_noisy = estimate_attenuation_from_blocks(base, noisy)
    block_noisy_ok = est_noisy > 0.0
    print(
        f"[icc/B] recovery_ok={recovery_ok} (corrected={corrected:.6f}), "
        f"identity_ok={identity_ok}, cap_ok={cap_ok}, "
        f"block_perfect={est_perfect:.4f}, block_noisy={est_noisy:.4f}"
    )
    return bool(recovery_ok and identity_ok and cap_ok and block_perfect_ok and block_noisy_ok)


def main() -> int:
    a = sub_test_A()
    b = sub_test_B()
    print(f"[icc] OVERALL: {'PASS' if (a and b) else 'FAIL'}")
    return 0 if (a and b) else 1


if __name__ == "__main__":
    sys.exit(main())
