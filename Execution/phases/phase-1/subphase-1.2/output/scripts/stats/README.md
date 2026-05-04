# Statistical Pipeline Core (Sub 1.2 task-006)

Load-bearing statistical components for the CompBioSummer2026 execution
pipeline, per `ImplementationPlan.md §12` and `Appendix A`.

- **Location:** `phases/phase-1/subphase-1.2/output/scripts/stats/`
- **Subphase:** 1.2
- **Track:** cross-cutting (Alpha-M + Gamma + Delta + Combined)
- **Tier:** Standard (CPU-only)
- **Env:** `env-stats` (see "Environment" below)

## Components

| Module | Implements | IP reference |
|--------|------------|--------------|
| `friedman_nemenyi.py` | Friedman omnibus + Nemenyi post-hoc, mean-rank table | §12.1 Alpha-M primary test |
| `icc.py` | ICC(2,1) + ICC(2,k) absolute-agreement via `pingouin`; convergence-correction factor from block-split R^2; IP §10.3 attenuation documented | §12.1 convergence criterion; §10.3 statistical-risk mitigation |
| `hierarchical_bootstrap.py` | 2-level resample (proteins, then residues); CI helper; default 10,000 iterations | §12.1 clustering; §14.1 reviewer-attack pre-emption |
| `jzs_bf.py` | Bayesian correlation BF via Fisher's exact sampling distribution (agrees with `R::BayesFactor::correlationBF` to <0.01% on same data); 4-prior sensitivity (JZS, Skeptical, Informative, Flat); PyMC posterior summaries; R subprocess fallback | §12.3 combined-paper primary test; Appendix A Bayesian model |
| `truncation.py` | `compute_t_min`, `log_truncation_events`, `truncate_trajectories` (mdtraj); JSON audit log | §12.1 truncation; §15.3 data integrity |

## Environment

All components run under the `env-stats` conda environment (created in Sub 1.2):

```
env-stats   # /home/rag88/.conda/envs/env-stats/
  python=3.11
  numpy, scipy, pandas
  pingouin>=0.6     # ICC
  scikit-posthocs>=0.12  # Nemenyi
  statsmodels
  pymc>=5, arviz    # JZS BF posterior
  mdtraj            # truncation file IO
  r-base, r-bayesfactor, r-jsonlite   # R validation + production path
```

Activate:
```bash
module purge
module load miniconda/24.11.3
conda activate env-stats
```

> **Do NOT modify `env-stats` in place.** Per `shared/notes/operational-practices.md`:
> clone to `env-stats-v2` first, test, document.

## Running the test suite

```bash
cd /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/stats
python tests/test_all.py   # exit 0 iff all pass
```

The runner executes each synthetic-data unit test as a subprocess. Typical
wall time on a login node: ~30 s (the JZS test dominates; it samples PyMC
for 4 priors and validates against R).

Skip the slow PyMC test with `SKIP_JZS_TEST=1`. Do not do this in production.

Per-component test:
```
python tests/test_friedman_nemenyi.py
python tests/test_icc.py
python tests/test_hierarchical_bootstrap.py --coverage-seeds 20 --iterations 2000
python tests/test_jzs_bf.py
python tests/test_truncation.py
```

### Unit-test expectations (what each test asserts)

| Test | Synthetic setup | Asserts |
|------|-----------------|---------|
| `test_friedman_nemenyi` | 14 proteins x 10 generators; g0 better by Delta=0.20 | Omnibus p < 0.05; at least 8 of 9 (g0, g_j) Nemenyi pairs sig; <=5 of 36 noise pairs flagged; g0 top-ranked |
| `test_icc` | Variance-components simulation (sub-A) + analytical correction (sub-B) | ICC(2,1) in (0.60, 0.99); ICC(2,k) >= ICC(2,1); convergence-correction recovers ICC=0.85 from measured 0.68; cap at 1.0 |
| `test_hierarchical_bootstrap` | 14 proteins x 50 residues, grand mean 0.75 | Mean matches sample mean; CI covers sample mean; hier CI width >= 1.3 x naive CI width; coverage sweep: >=17/20 runs cover truth=0.75 |
| `test_jzs_bf` | n=20, rho=0.6; n=20, rho=0.0; 4-prior sweep | Strong-signal: BF_10 >= 3, rho_hat close to truth, R cross-check within 20%; null: BF_10 <= 1.5, CI includes 0; sensitivity: all priors give correct direction, IP §12.3 decision rule satisfied |
| `test_truncation` | Mock trajectory-length dict | compute_t_min correct; log_truncation_events writes valid JSON with all fields; empty-dict edge cases handled |

## Usage examples

### Friedman + Nemenyi (Alpha-M)

```python
from stats.friedman_nemenyi import friedman_nemenyi

# s2_table shape (n_proteins, n_generators); higher S2 R^2 = better generator
out = friedman_nemenyi(s2_table, alpha=0.05, generator_names=["mace", "so3lr", "ff14sb", ...])
print(out["chi2"], out["p_value"])
print(out["pairwise_p"])           # symmetric p-matrix
print(out["significant_pairs"])    # [(a, b, p), ...] at p < alpha
print(out["mean_ranks"])           # higher rank = better
```

### ICC(2,k) + convergence correction (Alpha-M)

```python
import pandas as pd
from stats.icc import icc_2k, convergence_correction, estimate_attenuation_from_blocks

df = pd.DataFrame({
    "protein":  ["p01"]*3 + ["p02"]*3 + ...,
    "replicate": ["r1","r2","r3"]*N,
    "s2_r2":    [...],
})
out = icc_2k(df, target_col="protein", rater_col="replicate", value_col="s2_r2")
print(out["ICC2k"], out["ICC2_1"], out["CI_2k"])

# For production Sub 1.4, estimate attenuation empirically from block-split R^2:
a_hat = estimate_attenuation_from_blocks(s2_block_a, s2_block_b)
corrected = convergence_correction(out["ICC2k"], a_hat)
```

### Hierarchical bootstrap (all tracks)

```python
import numpy as np
from stats.hierarchical_bootstrap import hierarchical_bootstrap, bootstrap_ci

# `s2_by_residue` is 1-D; `protein_id` labels each residue's protein
boot = hierarchical_bootstrap(s2_by_residue, protein_id, statistic=np.mean,
                              n_iterations=10_000, seed=42)
ci = bootstrap_ci(boot, alpha=0.05)
print(ci["mean"], ci["ci_lo"], ci["ci_hi"])
```

### JZS Bayes factor (combined paper)

```python
from stats.jzs_bf import jzs_correlation_bf, four_prior_sensitivity, jzs_correlation_bf_r

# Primary (IP §12.3)
out = jzs_correlation_bf(s2_r2_per_protein, gamma_spearman_per_protein, prior="jzs")
print(out["BF_10"], out["rho_hat_posterior_mean"], out["CI95"])

# 4-prior sensitivity (IP Appendix A)
all4 = four_prior_sensitivity(x, y)
for prior_name, r in all4.items():
    print(prior_name, r["BF_10"], r["rho_hat_posterior_mean"])

# R cross-check (recommended for paper-grade BF)
r_out = jzs_correlation_bf_r(x, y)
print(r_out["BF_10"])
```

### Trajectory truncation (Alpha-M)

```python
from stats.truncation import compute_t_min, log_truncation_events, truncate_trajectories

lengths = {
    "ww":  {"mace": 10.0, "so3lr": 8.0, "amber": 25.0},
    "gb3": {"mace": 5.0,  "so3lr": 7.0, "amber": 30.0},
}
t_min = compute_t_min(lengths)   # {"ww": 8.0, "gb3": 5.0}

# With actual DCD files and timestep info:
result = truncate_trajectories(traj_paths, t_min, timestep_ps, output_dir="truncated/")
print(result["truncation_log_path"])  # JSON audit log
```

## The PyMC vs R choice (JZS BF)

We investigated three BF computation paths during Sub 1.2:

1. **Savage-Dickey via KDE on PyMC posterior samples.**  *Rejected.* KDE
   density estimation at rho=0 is unstable when the posterior concentrates
   away from zero (strong-signal case), producing BFs that diverge from R
   by orders of magnitude.

2. **Fisher-z asymptotic approximation.**  *Rejected.* Normal approximation
   to z_hat | z ~ Normal(z, 1/sqrt(n-3)) introduces 2-5x bias at n < 20.

3. **Fisher's exact sampling distribution** (Fisher 1915; Jeffreys 1961 §5.5;
   Ly, Verhagen & Wagenmakers 2016 eq. 12).  **SHIPPED.**
   The closed-form
   ```
   p(r | rho, n) ~ (1 - rho^2)^((n-1)/2) * (1 - rho*r)^(-(2n-3)/2)
                 * 2F1(1/2, 1/2, (2n-1)/2, (1 + rho*r)/2),
   ```
   integrated numerically against the prior on rho, matches R's
   `BayesFactor::correlationBF` to <0.01% relative error on synthetic data
   (see `tests/test_jzs_bf.py::sub_test_A`: Python BF_10 = 288.2478, R BF_10
   = 288.2478 at n=20, r=0.7605).

### When to call Python vs R

- **Python** (`jzs_correlation_bf`, `four_prior_sensitivity`): fast (~5 s per
  prior with PyMC posterior summaries), deterministic (seeded), vectorised-
  friendly for sensitivity sweeps. Use for rapid 4-prior BF tables across
  many protein-generator pairs.
- **R** (`jzs_correlation_bf_r`): independent reference implementation. Call
  once per paper-grade BF value so reviewers can point at the BayesFactor
  package directly (Ly et al. 2016 is the canonical citation).

Both produce identical BFs (same prior, same likelihood kernel). The task
spec tolerance was 20%; our actual agreement is 0.0001%.

## Bayesian mixed-effects model (IP Appendix A)

`jzs_bf.py` implements the marginal BF for the **correlation** (beta_1 in the
Appendix A model). The full random-effects model
```
S2_R2_ij ~ Normal(beta_0 + beta_1 * Fitness_ij + u_i + v_j, sigma^2)
```
with beta_1 ~ Cauchy(0, 1) (JZS), Half-Cauchy priors on sigma_protein and
sigma_generator, and parametric-bootstrap p-values (IP §12.3) will be fit in
Sub 1.4 and Phase 2 using this pipeline as the primary-test reference. The
full mixed model requires a dedicated PyMC specification that is scaffolded
via the prior specifications here; Sub 1.4 will add the protein / generator
random-effect layers on top of the marginal correlation BF.

## IP §10.3 convergence correction

Per Implementation Plan §10.3 statistical-risk mitigation:

> Convergence attenuation reduces power below 70% - Probability 30%.
> Mitigation: Report corrected ICC; add proteins if available.

The correction factor is **not a fixed constant**. Sub 1.4 will estimate
it empirically per-protein from block-split R^2 on real pilot trajectories
(function `icc.estimate_attenuation_from_blocks`). The midpoint default
(a = 0.20) is shipped so the pipeline is callable end-to-end before Sub 1.4
data lands. Every ICC value in a Phase 2 manuscript MUST be reported as
both raw and corrected, with the estimated attenuation factor cited.

## Troubleshooting

- **PyMC import slow.** First-time import of `pymc` pulls in PyTensor which
  compiles a C backend. This is a one-time cost per Python process.
- **`pingouin` ICC type strings.** pingouin >=0.6 uses `ICC(A,k)` rather
  than the pingouin-0.4 `ICC2k`. Our code supports both naming schemes; if
  you see `RuntimeError: pingouin did not return ICC2/ICC2k rows`, check
  `pingouin.__version__` and file a bug referencing `icc.py` L80.
- **R BayesFactor unavailable.** Ensure `r-bayesfactor` and `r-jsonlite`
  are in `env-stats`. `conda install -n env-stats -c conda-forge r-bayesfactor r-jsonlite`.
- **`test_jzs_bf.py` takes >30 s.** Expected. Sub-test C runs 4 PyMC sampler
  invocations. Ctrl-C-safe.

## Files and layout

```
stats/
  __init__.py                 # re-exports 5 modules
  README.md                   # this file
  friedman_nemenyi.py
  icc.py
  hierarchical_bootstrap.py
  jzs_bf.py
  truncation.py
  tests/
    __init__.py
    _util.py                  # path-bootstrap helper
    test_friedman_nemenyi.py
    test_icc.py
    test_hierarchical_bootstrap.py
    test_jzs_bf.py
    test_truncation.py
    test_all.py               # runner; exit 0 iff all pass
```

## References

- Fisher, R.A. (1915). Frequency distribution of the values of the correlation
  coefficient in samples from an indefinitely large population. *Biometrika*,
  10(4), 507-521.
- Friedman, M. (1937). The use of ranks to avoid the assumption of normality
  implicit in the analysis of variance. *JASA*, 32(200), 675-701.
- Gronau, Q.F. et al. (2017). A tutorial on bridge sampling. *Journal of
  Mathematical Psychology*, 81, 80-97.
- Jeffreys, H. (1961). *Theory of Probability*, 3rd ed. Oxford UP. §5.5.
- Ly, A., Verhagen, J. & Wagenmakers, E.-J. (2016). Harold Jeffreys's default
  Bayes factor hypothesis tests. *Journal of Mathematical Psychology*, 72, 19-32.
- Nemenyi, P. (1963). *Distribution-free multiple comparisons*. Doctoral
  dissertation, Princeton University.
- Shrout, P.E. & Fleiss, J.L. (1979). Intraclass correlations: uses in
  assessing rater reliability. *Psychological Bulletin*, 86(2), 420-428.
