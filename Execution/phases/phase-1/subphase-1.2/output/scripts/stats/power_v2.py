"""
Corrected power analysis for OSF pre-registration v2 (Combined paper).

The v1 Appendix B code had a simulation flaw: it generated observations on the
full N_proteins x N_generators grid (e.g. 140 points), computed sample r from
all 140 points (inflating r due to high nominal n), then evaluated BF at the
Kish-adjusted n_eff ~ 17. This produced 100% power at all (rho, att) cells
because r ~ 0.83 even when rho_true = 0.3.

CORRECTED APPROACH: draw sample r directly from Fisher's sampling distribution
with parameters (rho_true, n_eff), then evaluate BF_10(r, n_eff) via Fisher's
exact closed form. This is equivalent to observing n_eff independent bivariate
normal pairs with true correlation rho -- the ICC attenuation is accounted for
by reducing n to n_eff via Kish's design-effect formula.

Design:
  - 14 S2-counted proteins x 10 generators (Table 1)
  - 9 MLFF-feasible x 10 generators (Table 2)
  - ICC_raw = 0.70 (IP §1 conservative estimate)
  - Attenuation grid: 0.15, 0.20, 0.25 (IP §10.3)
  - rho grid: 0.3, 0.5, 0.7
  - Prior: JZS (rho+1)/2 ~ Beta(sqrt(2), sqrt(2)) [matches R BayesFactor]
  - Decision rule: BF_10 > 3
  - n_sim = 10,000 per cell
  - Seed: 20260515 (locked to OSF deposit target date)

Uses the validated _bf10_exact() from jzs_bf.py (Fisher 1915 exact closed form,
matching R BayesFactor::correlationBF to <0.01% relative error).

Usage:
    conda activate env-stats
    python power_v2.py
"""

import sys
import os
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jzs_bf import _bf10_exact

RNG_SEED = 20260515
N_SIM = 10_000

N_PROTEINS_S2 = 14
N_GENERATORS = 10
N_PROTEINS_MLFF = 9
ICC_RAW = 0.70

RHO_GRID = [0.3, 0.5, 0.7]
ATT_GRID = [0.15, 0.20, 0.25]


def effective_n(n_proteins, n_generators, icc_corrected):
    """Effective sample size for crossed random effects using Kish's formula.

    deff = 1 + (k_avg - 1) * ICC_corrected
    n_eff = n_total / deff
    Floor at 5 (minimum for BF computation).
    """
    n_total = n_proteins * n_generators
    k_avg = max(n_proteins, n_generators)
    deff = 1.0 + (k_avg - 1) * icc_corrected
    return max(n_total / deff, 5)


def draw_sample_r(rho, n, rng):
    """Draw sample r from Fisher's asymptotic sampling distribution.

    z = atanh(r) ~ N(atanh(rho), 1 / sqrt(n - 3)).
    Returns r = tanh(z).
    """
    z_true = np.arctanh(min(rho, 0.999))
    se = 1.0 / np.sqrt(max(n - 3, 1))
    z_sample = rng.normal(z_true, se)
    return float(np.tanh(z_sample))


def power_cell(rho, att, n_proteins, n_generators, n_sim=N_SIM, seed=RNG_SEED):
    """Fraction of simulated datasets yielding BF_10 > 3 under JZS."""
    # Deterministic seed per cell for reproducibility
    rng = np.random.default_rng(seed + int(rho * 1000) + int(att * 100))
    icc_eff = ICC_RAW * (1 - att)
    n_eff = effective_n(n_proteins, n_generators, icc_eff)
    n_eff_int = max(int(round(n_eff)), 5)
    wins = 0
    for _ in range(n_sim):
        r = draw_sample_r(rho, n_eff_int, rng)
        r = float(np.clip(r, -0.9999, 0.9999))
        bf10 = _bf10_exact(r, n_eff_int, "jzs")
        if bf10 > 3:
            wins += 1
    return wins / n_sim


def main():
    print("=" * 72)
    print("OSF Pre-Registration v2 Power Analysis (Combined Paper)")
    print("Corrected: Fisher-z sampling distribution at n_eff + exact BF")
    print(f"n_sim = {N_SIM} per cell, seed = {RNG_SEED}")
    print("=" * 72)

    # Table 1: 14 S2-counted x 10 generators
    print("\n--- Table 1: 14 S2-counted proteins x 10 generators ---")
    print(f"{'rho':>6}  {'att=0.15':>10}  {'att=0.20':>12}  {'att=0.25':>10}")
    table1 = {}
    t0 = time.time()
    for rho in RHO_GRID:
        row = []
        for att in ATT_GRID:
            p = power_cell(rho, att, N_PROTEINS_S2, N_GENERATORS)
            table1[(rho, att)] = p
            row.append(p)
        print(f"{rho:>6.1f}  {row[0]:>10.1%}  {row[1]:>12.1%}  {row[2]:>10.1%}")
    elapsed1 = time.time() - t0
    print(f"(elapsed: {elapsed1:.1f} s)")

    # Table 2: 9 MLFF-feasible x 10 generators
    print("\n--- Table 2: 9 MLFF-feasible x 10 generators ---")
    print(f"{'rho':>6}  {'att=0.15':>10}  {'att=0.20':>12}  {'att=0.25':>10}")
    table2 = {}
    t0 = time.time()
    for rho in RHO_GRID:
        row = []
        for att in ATT_GRID:
            p = power_cell(rho, att, N_PROTEINS_MLFF, N_GENERATORS)
            table2[(rho, att)] = p
            row.append(p)
        print(f"{rho:>6.1f}  {row[0]:>10.1%}  {row[1]:>12.1%}  {row[2]:>10.1%}")
    elapsed2 = time.time() - t0
    print(f"(elapsed: {elapsed2:.1f} s)")

    # Effective sample sizes
    print("\n--- Effective sample sizes ---")
    for att in ATT_GRID:
        icc_eff = ICC_RAW * (1 - att)
        n_eff_14 = effective_n(N_PROTEINS_S2, N_GENERATORS, icc_eff)
        n_eff_9 = effective_n(N_PROTEINS_MLFF, N_GENERATORS, icc_eff)
        print(
            f"att={att:.2f}: ICC_eff={icc_eff:.3f}, "
            f"n_eff(14x10)={n_eff_14:.1f}, n_eff(9x10)={n_eff_9:.1f}"
        )

    # Raw numeric for copy-paste
    print("\n--- Raw numeric (for OSF copy-paste) ---")
    print("Table 1 (14 S2-counted x 10 generators):")
    for rho in RHO_GRID:
        vals = [f"{table1[(rho, att)]:.4f}" for att in ATT_GRID]
        print(f"  rho={rho}: att=0.15={vals[0]}, att=0.20={vals[1]}, att=0.25={vals[2]}")
    print("Table 2 (9 MLFF-feasible x 10 generators):")
    for rho in RHO_GRID:
        vals = [f"{table2[(rho, att)]:.4f}" for att in ATT_GRID]
        print(f"  rho={rho}: att=0.15={vals[0]}, att=0.20={vals[1]}, att=0.25={vals[2]}")


if __name__ == "__main__":
    main()
