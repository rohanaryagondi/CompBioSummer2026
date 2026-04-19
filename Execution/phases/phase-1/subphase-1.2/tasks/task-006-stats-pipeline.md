---
task_id: "task-006"
title: "Statistical pipeline core (Friedman/Nemenyi, ICC, hierarchical bootstrap, JZS BF, T_min truncation)"
subphase: "1.2"
track: cross-cutting
wave: 2
agent: "stats-pipeline"
effort: "7-10 days, CPU only"
status: planned
created: 2026-04-18
---

# Task 006: Statistical Pipeline Core

## Objective

Implement the 5 critical statistical components specified in IP §12 + Appendix A
that Phase 2 production analysis depends on: (1) Friedman test + Nemenyi post-hoc
for Alpha-M generator comparison, (2) ICC(2,k) and ICC(2,1) with documented
convergence-correction factor for Alpha-M S2 reproducibility, (3) hierarchical
bootstrap (resample proteins → residues) with ≥10K iterations, (4) JZS Bayesian
correlation pipeline with 4-prior sensitivity for the combined paper integration
analysis, and (5) trajectory truncation protocol (T_min per protein) for fair
generator comparison. Each component is validated on synthetic data with known
ground truth so Sub 1.4 can invoke them on real pilot data with confidence.

---

## Context

**Why now (not Sub 1.4):** Sub 1.4 needs to invoke these on real pilot data to
score D2 G2/G3/G6. Sub 1.4 is too late to also implement them. Sub 1.2 is the
last opportunity to build the pipeline before Phase 2 production starts July 1.

**Why CPU only:** All 5 components are CPU-bound (statistical computations on
small-to-medium tables). No GPU needed. Standard Tier per user decision.

**Why synthetic data validation:** Each component must be validated against a
known answer. For example, JZS BF on data with known correlation ρ=0.5 should
return BF ≈ a known value (cross-checked against R `BayesFactor::correlationBF`).
This validates the implementation BEFORE trusting it on real pilot data.

**Why 5 components (and not, say, the full IP §12 spec):** These 5 are the load-bearing
ones for D2/D6 evidence. Other items (e.g., FDR, calibration) are in task-005's scope.

---

## Detailed Instructions

### Step 1: Friedman + Nemenyi (Day 1)

Build `phases/phase-1/subphase-1.2/output/scripts/stats/friedman_nemenyi.py`:

```python
"""
Per IP §12.1: Primary test for Alpha-M is Friedman test with Nemenyi post-hoc
across generators. Each row = a protein; each column = a generator's S2 R² to NMR.
"""
import numpy as np
from scipy.stats import friedmanchisquare
import scikit_posthocs as sp

def friedman_nemenyi(data: np.ndarray, alpha: float = 0.05):
    """
    data: 2D array, shape (n_proteins, n_generators). Values are ranks or scores.
    Returns: dict with 'chi2', 'p_value', 'pairwise_p_matrix', 'significant_pairs'.
    """
    chi2, p = friedmanchisquare(*data.T)
    pairwise = sp.posthoc_nemenyi_friedman(data)
    sig = (pairwise < alpha) & (np.eye(pairwise.shape[0]) == 0)
    return {"chi2": chi2, "p_value": p, "pairwise_p": pairwise.values, "significant_pairs": sig}
```

Synthetic test (`tests/test_friedman_nemenyi.py`):
- Generate fake S2 data: 14 proteins × 10 generators, with generator 0 systematically
  better by Δ=0.2 in R²
- Expected: Friedman p < 0.05; Nemenyi shows generator 0 vs others as significant

### Step 2: ICC(2,k) + ICC(2,1) with convergence correction (Day 2-3)

Build `phases/phase-1/subphase-1.2/output/scripts/stats/icc.py`:

```python
"""
Per IP §1 + §10.3: ICC(2,k) for absolute agreement among k raters (replicates),
two-way random effects. ICC(2,1) for single rater.

Convergence correction: trajectories of finite length attenuate measured ICC.
IP notes ~15-25% attenuation. We document the correction factor explicitly.
"""
import numpy as np
import pandas as pd
import pingouin as pg

def icc_2k(data: pd.DataFrame, target_col: str, rater_col: str, value_col: str):
    """
    Two-way random effects, absolute agreement, average of k raters (ICC(2,k))
    or single rater (ICC(2,1)).
    Returns: dict with 'ICC2k', 'ICC2_1', 'CI95_2k', 'CI95_2_1'.
    """
    icc = pg.intraclass_corr(data=data, targets=target_col, raters=rater_col, ratings=value_col)
    icc_2k_val = icc.loc[icc['Type'] == 'ICC2k', 'ICC'].values[0]
    icc_21_val = icc.loc[icc['Type'] == 'ICC2', 'ICC'].values[0]
    ci_2k = icc.loc[icc['Type'] == 'ICC2k', 'CI95%'].values[0]
    ci_21 = icc.loc[icc['Type'] == 'ICC2', 'CI95%'].values[0]
    return {"ICC2k": icc_2k_val, "ICC2_1": icc_21_val, "CI95_2k": ci_2k, "CI95_2_1": ci_21}

def convergence_correction(measured_icc: float, attenuation_factor: float = 0.20):
    """
    Apply the convergence-attenuation correction. For 20% attenuation:
      true_icc ≈ measured_icc / (1 - 0.20) = measured_icc / 0.80
    This is a documented IP §10.3 correction. The Sub 1.4 task will compute
    `attenuation_factor` empirically from block-split R².
    """
    return measured_icc / (1.0 - attenuation_factor)
```

Synthetic test:
- Generate fake replicate data with known ICC=0.85 and 20% attenuation
- Expected: measured ICC ≈ 0.68; corrected ICC ≈ 0.85

### Step 3: Hierarchical bootstrap (Day 3-4)

Build `phases/phase-1/subphase-1.2/output/scripts/stats/hierarchical_bootstrap.py`:

```python
"""
Per IP §12.1: Hierarchical bootstrap = resample proteins (level 1), then resample
residues within each resampled protein (level 2). 10,000 iterations.
"""
import numpy as np

def hierarchical_bootstrap(data, level1_idx, level2_idx, statistic, n_iterations=10000, seed=42):
    """
    data: per-residue values (e.g., S2 R² per residue)
    level1_idx: protein ID per residue
    level2_idx: residue ID per residue
    statistic: callable that takes resampled data and returns a scalar
    Returns: bootstrap distribution (1D array of length n_iterations)
    """
    rng = np.random.default_rng(seed)
    bootstrap_dist = np.empty(n_iterations)
    unique_proteins = np.unique(level1_idx)
    for it in range(n_iterations):
        # Level 1: resample proteins WITH replacement
        sampled_proteins = rng.choice(unique_proteins, size=len(unique_proteins), replace=True)
        # Level 2: for each resampled protein, resample residues WITH replacement
        sampled_data = []
        for p in sampled_proteins:
            mask = level1_idx == p
            n_residues = mask.sum()
            sampled_residues = rng.choice(np.where(mask)[0], size=n_residues, replace=True)
            sampled_data.append(data[sampled_residues])
        bootstrap_dist[it] = statistic(np.concatenate(sampled_data))
    return bootstrap_dist
```

Synthetic test:
- Generate 14 proteins × 50 residues with known mean S2 R² = 0.75
- Bootstrap CI on the mean should bracket 0.75 with ≥95% coverage at α=0.05

### Step 4: JZS Bayesian correlation with 4-prior sensitivity (Day 4-7)

Build `phases/phase-1/subphase-1.2/output/scripts/stats/jzs_bf.py`:

```python
"""
Per IP §12.3 + Appendix A: JZS Bayesian correlation with bridge sampling for BF
computation (Gronau et al. 2017). 4-prior sensitivity analysis.

Implementation: PyMC with bridgesampling. If PyMC fails validation, ship R wrapper
to BayesFactor::correlationBF.
"""
import numpy as np
import pymc as pm
import bridge_sampler  # or implement bridge sampling manually

def jzs_correlation_bf(x, y, prior='jzs'):
    """
    x, y: 1D arrays of paired observations
    prior: 'jzs' (Cauchy(0,1)), 'skeptical' (N(0,0.5²)), 'informative' (N(0.5,0.15²)), 'flat' (U(-1,1))
    Returns: dict with 'rho_posterior_mean', 'BF_10', 'BF_01', 'CI95'.
    """
    n = len(x)
    x_std = (x - x.mean()) / x.std()
    y_std = (y - y.mean()) / y.std()
    with pm.Model() as model:
        if prior == 'jzs':
            rho = pm.Cauchy('rho', alpha=0, beta=1)
        elif prior == 'skeptical':
            rho = pm.Normal('rho', mu=0, sigma=0.5)
        elif prior == 'informative':
            rho = pm.Normal('rho', mu=0.5, sigma=0.15)
        elif prior == 'flat':
            rho = pm.Uniform('rho', lower=-1, upper=1)
        else:
            raise ValueError(f"Unknown prior: {prior}")
        sigma_x = pm.HalfNormal('sigma_x', sigma=1)
        sigma_y = pm.HalfNormal('sigma_y', sigma=1)
        cov = pm.math.stack([[sigma_x**2, rho*sigma_x*sigma_y],
                             [rho*sigma_x*sigma_y, sigma_y**2]])
        obs = pm.MvNormal('obs', mu=[0,0], cov=cov, observed=np.column_stack([x_std, y_std]))
        idata = pm.sample(2000, return_inferencedata=True)
    # Bridge sampling for marginal likelihood; H0 model has rho=0 as point mass
    # ... (bridge sampling implementation)
    return {"rho_posterior_mean": ..., "BF_10": ..., "BF_01": ..., "CI95": ...}

def four_prior_sensitivity(x, y):
    """Run all 4 priors per IP App. A; return table for the methods section."""
    return {p: jzs_correlation_bf(x, y, prior=p) for p in ['jzs', 'skeptical', 'informative', 'flat']}
```

Synthetic test:
- Generate paired data with known ρ=0.5, n=14 (matches IP design)
- Cross-check JZS BF against R: install R + BayesFactor, run `correlationBF(y ~ x, data=df)`, compare BF values
- Tolerance: ≤20% relative difference (Bayesian estimates are stochastic)

**If PyMC validation fails:** Ship a thin R wrapper:
```python
def jzs_correlation_bf_r(x, y):
    import subprocess
    # write x, y to temp CSV
    # call Rscript with BayesFactor::correlationBF
    # parse stdout
    return {...}
```
Document the choice (PyMC vs R) in the stats pipeline README.

### Step 5: T_min trajectory truncation (Day 7-8)

Build `phases/phase-1/subphase-1.2/output/scripts/stats/truncation.py`:

```python
"""
Per IP §12.1: All trajectories per protein are truncated to T_min(protein) =
the shortest trajectory length that all generators achieved for that protein.
This ensures fair comparison.
"""
import json
import os
import mdtraj as md

def compute_t_min(trajectories: dict) -> dict:
    """
    trajectories: {protein_id: {generator_id: trajectory_length_ns}}
    Returns: {protein_id: t_min_ns}
    """
    return {p: min(g_lengths.values()) for p, g_lengths in trajectories.items()}

def truncate_trajectories(trajectories: dict, t_min: dict, output_dir: str):
    """
    For each (protein, generator) trajectory, truncate to t_min[protein] and write
    to output_dir/<protein>/<generator>_truncated.dcd.
    """
    for protein, generators in trajectories.items():
        t = t_min[protein]
        for generator, traj_path in generators.items():
            traj = md.load(traj_path)
            n_frames_to_keep = int(t / traj.timestep * 1000)  # assuming traj.timestep is ps
            truncated = traj[:n_frames_to_keep]
            out = os.path.join(output_dir, protein, f"{generator}_truncated.dcd")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            truncated.save_dcd(out)
            # Log the truncation to a JSON file for reproducibility
    log_path = os.path.join(output_dir, 't_min_log.json')
    with open(log_path, 'w') as f:
        json.dump({'t_min_per_protein': t_min, 'timestamp': '...'}, f, indent=2)
```

Synthetic test:
- Mock trajectory dict: {'ww': {'mace': 10, 'so3lr': 8, 'amber': 25}, 'gb3': {'mace': 5, 'so3lr': 7, 'amber': 30}}
- Expected T_min: {'ww': 8, 'gb3': 5}
- Verify truncation produces correctly sized output

### Step 6: Synthetic-data unit test runner (Day 8-9)

Build `phases/phase-1/subphase-1.2/output/scripts/stats/tests/test_all.py`:

```python
"""Run all synthetic-data unit tests; exit 0 iff all pass."""
import subprocess
import sys

tests = [
    'test_friedman_nemenyi.py',
    'test_icc.py',
    'test_hierarchical_bootstrap.py',
    'test_jzs_bf.py',
    'test_truncation.py',
]
results = {}
for t in tests:
    result = subprocess.run(['python', t], capture_output=True)
    results[t] = result.returncode
for t, code in results.items():
    print(f"{t}: {'PASS' if code == 0 else 'FAIL'}")
sys.exit(0 if all(c == 0 for c in results.values()) else 1)
```

### Step 7: README + cross-agent note (Day 9-10)

Write `phases/phase-1/subphase-1.2/output/scripts/stats/README.md` documenting:
- Which component implements which IP §12 spec
- How to invoke each on real Sub 1.4 data
- The PyMC vs R choice (and why)
- Per-component validation results

Write cross-agent note `shared/notes/1.2-stats-pipeline-validation.md`.

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| `../../tasks/task-006-stats-pipeline.md` | This task spec |
| `../../../../../../Proposal/ImplementationPlan.md` | §12 (full statistical framework), Appendix A (Bayesian model) |
| `../../../../../shared/notes/operational-practices.md` | Standard Tier policy |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../shared/notes/1.2-scope-recommendations.md` | Items 3-7, 11-13 are the explicit scope |
| `../../../../../shared/notes/1.1-protein-count-canonical.md` | Effective sample sizes for power simulations |

### DO NOT READ

- Other SubAgents' task specs
- `../../../../../../Proposal/HumanOnlyProposal.md`
- Future subphase plans

---

## Output Artifacts

### Code and data artifacts

| Artifact | Path | Format |
|----------|------|--------|
| Friedman+Nemenyi | `../../output/scripts/stats/friedman_nemenyi.py` | Python |
| ICC | `../../output/scripts/stats/icc.py` | Python |
| Hierarchical bootstrap | `../../output/scripts/stats/hierarchical_bootstrap.py` | Python |
| JZS BF | `../../output/scripts/stats/jzs_bf.py` | Python |
| Truncation | `../../output/scripts/stats/truncation.py` | Python |
| Unit tests | `../../output/scripts/stats/tests/test_*.py` | Python |
| Test runner | `../../output/scripts/stats/tests/test_all.py` | Python |
| README | `../../output/scripts/stats/README.md` | Markdown |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-006-status.md` | `templates/status-report.md` |
| Cross-agent note | `../../../../../shared/notes/1.2-stats-pipeline-validation.md` | `templates/cross-agent-note.md` |

---

## Success Criteria (Zero Compromise)

1. [ ] All 5 component scripts exist and are importable from `../../output/scripts/stats/`
2. [ ] All 5 unit tests in `tests/` pass against known synthetic data ground truth
3. [ ] `python tests/test_all.py` returns exit 0
4. [ ] JZS BF validated against R `BayesFactor::correlationBF` (within 20% relative tolerance) OR R wrapper shipped if PyMC fails
5. [ ] ICC convergence-correction documented in `icc.py` docstring with citation to IP §10.3
6. [ ] Hierarchical bootstrap implements correct 2-level resampling (proteins, then residues)
7. [ ] T_min truncation produces correct output on synthetic trajectory dict
8. [ ] README documents all 5 components with usage examples
9. [ ] Cross-agent note `1.2-stats-pipeline-validation.md` written
10. [ ] Status report written to `../../status/task-006-status.md`

---

## Verification

1. `cd ../../output/scripts/stats && python tests/test_all.py` returns exit 0
2. `python -c "from stats import friedman_nemenyi, icc, hierarchical_bootstrap, jzs_bf, truncation; print('all import OK')"` succeeds
3. README.md exists with sections for each component
4. JZS BF validation script in `tests/test_jzs_bf.py` shows comparison to R BayesFactor (or documents the R-wrapper choice)
5. Status report exists with status `complete`

---

## Failure Protocol

1. **PyMC JZS BF validation fails (>20% disagreement with R):** Ship R wrapper instead. Document in README. Status: `complete` with note.
2. **`pingouin` ICC implementation differs from R `psych::ICC`:** Cross-check; use R wrapper if needed. Document.
3. **Hierarchical bootstrap memory issue at 10K iterations × large data:** Reduce to 5K iterations; document in README; flag for Sub 1.4.
4. **Synthetic test fails for a component:** Debug; do NOT ship a broken component. If unable to fix, status: `partial`; flag in help-needed.

Document everything in status report.
