"""
test_hierarchical_bootstrap -- synthetic-data unit test for hierarchical_bootstrap.

Design
------
Simulate 14 proteins x 50 residues per protein; true per-residue mean S2 R^2 =
0.75 with per-protein offsets (sd 0.04) and per-residue noise (sd 0.10). The
grand mean is 0.75.

Ground truth
------------
1. The bootstrap distribution mean should equal the sample grand mean to
   within Monte Carlo error (< 0.005 absolute).
2. The 95% percentile CI (alpha=0.05) from the hierarchical bootstrap should
   bracket the SAMPLE grand mean (empirical truth for this draw).
3. The CI WIDTH for the hierarchical bootstrap should be LARGER than the CI
   from a naive (level-2-only) bootstrap. The naive bootstrap under-estimates
   sampling variance because it ignores between-protein correlation; the
   hierarchical version is the correction. IP §12.1 + §14.1.
4. Coverage sweep: over 20 independent seeds, the hierarchical bootstrap
   95% CI should cover the population truth (0.75) in >= 17/20 runs
   (coverage >= 85%, conservative relative to nominal 95% because we use
   2K iterations and n_proteins=14).

Note: the test uses 2,000 iterations per run to stay tractable on a login
node (Standard Tier). At 2K iterations the CI is sufficiently accurate; the
production default is 10,000 (see ``--iterations`` CLI flag).
"""
from __future__ import annotations

import argparse
import sys

from _util import _ensure_parent_on_path  # noqa: F401

import numpy as np

from hierarchical_bootstrap import bootstrap_ci, hierarchical_bootstrap


def _simulate(seed: int = 42, n_proteins: int = 14, residues_per_protein: int = 50):
    rng = np.random.default_rng(seed)
    data = []
    level1 = []
    for p in range(n_proteins):
        offset = rng.normal(0.0, 0.04)
        residues = 0.75 + offset + rng.normal(0.0, 0.10, size=residues_per_protein)
        data.extend(residues.tolist())
        level1.extend([p] * residues_per_protein)
    return np.array(data), np.array(level1)


def _naive_bootstrap(
    data: np.ndarray, n_iterations: int = 2000, seed: int = 42
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out = np.empty(n_iterations)
    n = len(data)
    for i in range(n_iterations):
        idx = rng.integers(0, n, size=n)
        out[i] = float(np.mean(data[idx]))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--coverage-seeds", type=int, default=20)
    args = parser.parse_args()

    data, level1 = _simulate(args.seed)
    truth = 0.75
    sample_mean = float(data.mean())

    boot = hierarchical_bootstrap(
        data, level1, statistic=np.mean, n_iterations=args.iterations, seed=args.seed
    )
    ci = bootstrap_ci(boot)
    # 1. Bootstrap mean should equal the sample mean to within MC error.
    mean_matches_sample = abs(ci["mean"] - sample_mean) < 0.005
    # 2. Bootstrap CI covers the sample mean (self-consistency check).
    covers_sample = ci["ci_lo"] <= sample_mean <= ci["ci_hi"]

    # Compare to naive 1-level bootstrap
    naive = _naive_bootstrap(data, args.iterations, args.seed)
    naive_ci = bootstrap_ci(naive)
    hier_width = ci["ci_hi"] - ci["ci_lo"]
    naive_width = naive_ci["ci_hi"] - naive_ci["ci_lo"]
    # 3. Hierarchical CI should be STRICTLY wider than naive (1-level) CI;
    # tolerance: hier_width >= 1.3 * naive_width (hierarchical accounts for
    # between-protein variance that naive ignores).
    width_strict_ok = hier_width >= 1.3 * naive_width

    print(
        f"[hier_bootstrap] n_iter={args.iterations}, sample_mean={sample_mean:.4f}"
    )
    print(
        f"[hier_bootstrap] hier   mean={ci['mean']:.4f}, "
        f"CI=({ci['ci_lo']:.4f}, {ci['ci_hi']:.4f}), width={hier_width:.4f}"
    )
    print(
        f"[hier_bootstrap] naive  mean={naive_ci['mean']:.4f}, "
        f"CI=({naive_ci['ci_lo']:.4f}, {naive_ci['ci_hi']:.4f}), "
        f"width={naive_width:.4f}"
    )
    print(
        f"[hier_bootstrap] mean_matches_sample={mean_matches_sample}, "
        f"covers_sample={covers_sample}, width_strict_ok={width_strict_ok} "
        f"(hier/naive ratio={hier_width/naive_width:.2f})"
    )

    # 4. Coverage sweep over 20 independent data simulations.
    # Under nominal 95% CI, expected coverage ~0.95; we require >= 17/20
    # (conservative: sampling noise at k=2000 iterations and n=14 proteins).
    coverage_hits = 0
    coverage_n = args.coverage_seeds
    for s in range(coverage_n):
        d2, l2 = _simulate(seed=100 + s)
        b2 = hierarchical_bootstrap(
            d2, l2, statistic=np.mean, n_iterations=args.iterations, seed=100 + s
        )
        c2 = bootstrap_ci(b2)
        if c2["ci_lo"] <= truth <= c2["ci_hi"]:
            coverage_hits += 1
    coverage_ok = coverage_hits >= 17
    print(
        f"[hier_bootstrap] coverage sweep: {coverage_hits}/{coverage_n} "
        f"runs had CI covering truth={truth} (required >=17/{coverage_n}); "
        f"pass={coverage_ok}"
    )

    shape_ok = boot.shape == (args.iterations,)
    ok = bool(
        mean_matches_sample
        and covers_sample
        and width_strict_ok
        and coverage_ok
        and shape_ok
    )
    print(f"[hier_bootstrap] OVERALL: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
