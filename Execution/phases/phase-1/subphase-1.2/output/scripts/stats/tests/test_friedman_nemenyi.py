"""
test_friedman_nemenyi -- synthetic-data unit test for friedman_nemenyi.

Design
------
Generate a (14 proteins x 10 generators) table of "S2 R^2" where generator 0
is systematically better than the other 9 by a fixed effect Delta = 0.20 on
R^2 scale (with protein-level random noise).

Ground truth
------------
1. Friedman omnibus p < 0.05 (easily; 14 proteins with consistent superiority
   gives power ~ 1.0 at alpha=0.05).
2. Nemenyi pairwise: at least 8 of the 9 pairs (g0, g_j) for j=1..9 must be
   flagged significant (at k=10 conditions Nemenyi is conservative; one
   noise-favourable draw can leave a single pair just above alpha even when
   the omnibus is extremely small -- acceptance threshold documented).
3. Pairs among (i, j) for i,j >= 1 should mostly be NON-significant
   (by construction the noise generators are exchangeable). We require
   <= 5 of the 36 off-diagonal non-(0,*) pairs to be flagged.
4. g0 must have the largest mean rank (direction check).

Expected behaviour documented per task-006 success criterion 1.
"""
from __future__ import annotations

import sys

from _util import _ensure_parent_on_path  # noqa: F401

import numpy as np

from friedman_nemenyi import friedman_nemenyi


def _generate_data(seed: int = 42):
    rng = np.random.default_rng(seed)
    n_proteins, n_generators = 14, 10
    # protein-level offset (shared across all generators for that protein)
    protein_offset = rng.normal(loc=0.7, scale=0.05, size=n_proteins)
    # per-(protein, generator) noise
    noise = rng.normal(loc=0.0, scale=0.03, size=(n_proteins, n_generators))
    data = protein_offset[:, None] + noise
    # inject systematic advantage for generator 0
    data[:, 0] += 0.20
    return data


def main() -> int:
    data = _generate_data()
    out = friedman_nemenyi(data, alpha=0.05, generator_names=[f"g{i}" for i in range(10)])
    ok = True

    # 1. Omnibus significant
    omnibus_ok = out["p_value"] < 0.05
    print(
        f"[friedman_nemenyi] omnibus: chi2={out['chi2']:.3f}, "
        f"p={out['p_value']:.3e}, df={out['df']}, "
        f"pass={'YES' if omnibus_ok else 'NO'}"
    )
    ok &= omnibus_ok

    # 2. At least 8 of the 9 (g0, g_j) pairs significant.
    # Nemenyi at k=10 is conservative; for 14 proteins one draw can leave a
    # single pair just above alpha even when the omnibus is extremely small.
    # Documented acceptance bound -- protects against legit regression while
    # tolerating sampling noise.
    sig_set = {(a, b) for a, b, _ in out["significant_pairs"]}
    g0_hits = sum(
        (("g0", f"g{j}") in sig_set or (f"g{j}", "g0") in sig_set)
        for j in range(1, 10)
    )
    g0_pairs_ok = g0_hits >= 8
    print(
        f"[friedman_nemenyi] g0 vs others significant count: "
        f"{g0_hits}/9 (required >=8); pass={'YES' if g0_pairs_ok else 'NO'}. "
        f"Total sig pairs: {len(out['significant_pairs'])}/45"
    )
    ok &= g0_pairs_ok

    # 3. Among (i, j) for i, j >= 1: at most 5 should be flagged (noise).
    noise_sig = [
        (a, b) for a, b, _ in out["significant_pairs"]
        if a != "g0" and b != "g0"
    ]
    noise_ok = len(noise_sig) <= 5
    print(
        f"[friedman_nemenyi] noise-pair false positives: "
        f"{len(noise_sig)}/36 (allowed <=5); "
        f"pass={'YES' if noise_ok else 'NO'}"
    )
    ok &= noise_ok

    # 4. g0 should have the highest mean rank
    mr = out["mean_ranks"]
    top_is_g0 = mr.idxmax() == "g0"
    print(
        f"[friedman_nemenyi] top-ranked generator: {mr.idxmax()} "
        f"(mean rank {mr.max():.2f}); pass={'YES' if top_is_g0 else 'NO'}"
    )
    ok &= top_is_g0

    if ok:
        print("[friedman_nemenyi] OVERALL: PASS")
        return 0
    else:
        print("[friedman_nemenyi] OVERALL: FAIL")
        return 1


if __name__ == "__main__":
    sys.exit(main())
