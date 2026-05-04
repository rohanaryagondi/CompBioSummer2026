"""
Power simulation for the Combined-paper pre-registration (OSF Appendix B).

Design: 14 S2-counted proteins x 10 generators (crossed)
        9 MLFF-feasible x 10 generators (sub-benchmark)
ICC convergence attenuation: primary = 0.20; sensitivity = 0.15, 0.25.
Prior: JZS (rho+1)/2 ~ Beta(sqrt(2), sqrt(2)) [matches R BayesFactor default].
Decision rule: BF_10 > 3 under JZS.
n_sim per (rho, att) cell: 10,000 draws.
Random seed: 20260515 (locked to OSF deposit target date).

Uses the validated _bf10_exact() from jzs_bf.py (Fisher 1915 exact closed form,
matching R BayesFactor::correlationBF to <0.01% relative error). This replaces
the PyMC bridge-sampling approach in the v1 Appendix B code, which would have
taken ~12-18 hours per cell. The exact closed form runs in milliseconds per BF.

Usage:
    conda activate env-stats
    cd /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/stats
    python power_simulation.py

Output: prints the 3x3 power table + the 9-protein MLFF sub-benchmark table.
"""

import sys
import os
import time

import numpy as np

# Add the stats package to path so we can import jzs_bf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jzs_bf import _bf10_exact

RNG_SEED = 20260515
N_SIM = 10_000

# Design parameters from IP and pre-reg
N_PROTEINS_S2 = 14       # S2-counted proteins
N_GENERATORS = 10
N_PROTEINS_MLFF = 9      # MLFF-feasible AND S2-counted subset (10 minus HPr excluded)

# Variance components from Phase 0 pilot calibration (IP §1 / pre-reg §10)
ICC_RAW = 0.7
SIGMA_PROTEIN = 0.08
SIGMA_GENERATOR = 0.10
SIGMA_NOISE = 0.12

RHO_GRID = [0.3, 0.5, 0.7]
ATT_GRID = [0.15, 0.20, 0.25]


def effective_n(n_proteins, n_generators, icc_corrected):
    """Effective sample size for crossed random effects using Kish's formula.

    For a crossed (1|protein) + (1|generator) design, the effective n accounts
    for the inflation due to non-independence within protein and generator
    clusters. Per IP §10.3 and Kish (1965):

        n_eff = n_total / (1 + (k_avg - 1) * ICC_corrected)

    where k_avg is the average cluster size and n_total = n_proteins * n_generators.
    For a fully crossed design, k_avg = max(n_proteins, n_generators).
    """
    n_total = n_proteins * n_generators
    k_avg = max(n_proteins, n_generators)
    deff = 1.0 + (k_avg - 1) * icc_corrected
    return max(n_total / deff, 5)  # floor at 5 for BF computation


def simulate_one(rho, att, n_proteins, n_generators, rng):
    """Simulate one dataset, compute sample r, return BF_10 > 3."""
    icc_eff = ICC_RAW * (1 - att)

    # Generate random effects
    u = rng.normal(0, SIGMA_PROTEIN, n_proteins)
    v = rng.normal(0, SIGMA_GENERATOR, n_generators)

    # Generate x (Gamma Spearman proxy) and y (S2 R^2 proxy)
    x = rng.standard_normal((n_proteins, n_generators))
    beta1 = rho  # standardized slope
    y = (beta1 * x
         + u[:, None]
         + v[None, :]
         + rng.normal(0, SIGMA_NOISE, (n_proteins, n_generators)))

    # Flatten and compute sample Pearson r
    x_flat = x.flatten()
    y_flat = y.flatten()
    r = float(np.corrcoef(x_flat, y_flat)[0, 1])

    # Compute effective n accounting for ICC attenuation
    n_eff = effective_n(n_proteins, n_generators, icc_eff)
    n_eff_int = max(int(round(n_eff)), 5)

    # BF via exact Fisher closed form (validated to match R BayesFactor to <0.01%)
    bf10 = _bf10_exact(r, n_eff_int, "jzs")
    return bf10 > 3


def power_cell(rho, att, n_proteins, n_generators, n_sim=N_SIM, seed=RNG_SEED):
    """Fraction of simulated datasets yielding BF_10 > 3 under JZS."""
    rng = np.random.default_rng(seed + int(rho * 1000) + int(att * 100))
    wins = sum(
        simulate_one(rho, att, n_proteins, n_generators, rng)
        for _ in range(n_sim)
    )
    return wins / n_sim


def main():
    print("=" * 72)
    print("OSF Pre-Registration Power Analysis (Combined Paper)")
    print("Fisher exact BF_10 via jzs_bf._bf10_exact (validated vs R)")
    print(f"n_sim = {N_SIM} per cell, seed = {RNG_SEED}")
    print("=" * 72)

    # Table 1: 14 S2-counted proteins x 10 generators
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

    # Table 2: 9 MLFF-feasible proteins x 10 generators
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

    # Also print effective n for reference
    print("\n--- Effective sample sizes ---")
    for att in ATT_GRID:
        icc_eff = ICC_RAW * (1 - att)
        n_eff_14 = effective_n(N_PROTEINS_S2, N_GENERATORS, icc_eff)
        n_eff_9 = effective_n(N_PROTEINS_MLFF, N_GENERATORS, icc_eff)
        print(f"att={att:.2f}: ICC_eff={icc_eff:.3f}, n_eff(14x10)={n_eff_14:.1f}, n_eff(9x10)={n_eff_9:.1f}")

    # Print raw numeric table for copy-paste
    print("\n--- Raw numeric table (for OSF copy-paste) ---")
    print("Table 1 (14 S2-counted x 10 generators):")
    for rho in RHO_GRID:
        vals = [f"{table1[(rho, att)]:.3f}" for att in ATT_GRID]
        print(f"  rho={rho}: att=0.15={vals[0]}, att=0.20={vals[1]}, att=0.25={vals[2]}")

    print("Table 2 (9 MLFF-feasible x 10 generators):")
    for rho in RHO_GRID:
        vals = [f"{table2[(rho, att)]:.3f}" for att in ATT_GRID]
        print(f"  rho={rho}: att=0.15={vals[0]}, att=0.20={vals[1]}, att=0.25={vals[2]}")


if __name__ == "__main__":
    main()
