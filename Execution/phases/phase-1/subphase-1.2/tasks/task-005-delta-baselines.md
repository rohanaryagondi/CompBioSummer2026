---
task_id: "task-005"
title: "Delta 5 baselines + WMSE evaluation harness"
subphase: "1.2"
track: delta
wave: 2
agent: "delta-baselines"
effort: "7-10 days, ~30 GPU-hrs RTX 5000 Ada"
status: planned
created: 2026-04-18
---

# Task 005: Delta 5 Baselines + WMSE Evaluation Harness

## Objective

Implement the 5 mandatory Delta baselines (linear regression, mean expression,
PCA-based, random, persistence) per IP §5.3 + §12.4, plus the WMSE → Spearman-top-k-DEG
hierarchical evaluation harness (IP §12.4 primary metric), FDR (BH primary, BY
sensitivity), calibration metrics (reliability diagram, ECE, vs random
metric-gaming test), and stratified evaluation (per cell type, perturbation type,
expression level). Validate on a 1M-cell Tahoe-100M subsample. Completing this
task **fully retires the D3 gate** (the only outstanding D3 criterion was
"Baseline implementations complete"; D3 was upgraded CONDITIONAL → GO on
2026-04-17 contingent on this).

---

## Context

**Why baselines now (not Sub 1.3):** D3 gate (June 6) requires baselines complete.
Sub 1.1 closed with 5/5 Tier 1 methods installed but baselines still owed. Sub 1.2
must close that gap to fully retire D3. Without baselines, D3 remains CONDITIONAL.

**What "5 baselines" means:** Per IP §5.3:
1. **Linear regression** — sklearn LinearRegression on flattened gene expression × perturbation features
2. **Mean expression** — predict perturbation-conditional mean expression per gene (no signal beyond mean)
3. **PCA-based** — project to top-K principal components and reconstruct (control for explained variance)
4. **Random** — permuted prediction (calibration-test baseline; WMSE > random = passes metric-gaming)
5. **Persistence** — predict same perturbation effect from a different cell type (transfer baseline)

**What "WMSE harness" means:** Per IP §12.4, WMSE is the primary metric and gates
Spearman on top-k DEGs hierarchically (Spearman only reported if WMSE significantly
better than random). The harness implements this gating.

**Why 1M-cell Tahoe subsample (not full 100M):** Sub 1.1 documented Tahoe-100M
loader bottleneck. 1M cells is sufficient for baseline validation and method
comparison; full evaluation is Phase 2 scope. If 1M is too slow, fall back to
100K (per Sub 1.1 fallback).

**Env mapping:** GEARS, scGPT, scFoundation use env-delta-v2. Tahoe-x1 uses env-tahoex1.
CPA uses env-cpa (yml ready, build on demand). For baselines themselves, use
env-delta-v2 (sklearn + numpy + scipy already present).

---

## Detailed Instructions

### Step 1: Implement 5 baselines (Day 1-3)

Build files at `phases/phase-1/subphase-1.2/output/scripts/delta/baselines/`:

#### `linear.py`
```python
from sklearn.linear_model import Ridge
import numpy as np

def fit_predict(X_train, Y_train, X_test):
    """X is perturbation features (one-hot or embedding), Y is gene expression."""
    model = Ridge(alpha=1.0)
    model.fit(X_train, Y_train)
    return model.predict(X_test)
```

#### `mean.py`
```python
import numpy as np

def fit_predict(X_train, Y_train, X_test, perturbation_ids_train, perturbation_ids_test):
    """Predict the per-perturbation mean expression."""
    pert_means = {}
    for pid in np.unique(perturbation_ids_train):
        mask = perturbation_ids_train == pid
        pert_means[pid] = Y_train[mask].mean(axis=0)
    return np.stack([pert_means.get(pid, Y_train.mean(axis=0)) for pid in perturbation_ids_test])
```

#### `pca.py`
```python
from sklearn.decomposition import PCA
import numpy as np

def fit_predict(X_train, Y_train, X_test, n_components=50):
    """Project Y_train to PCA basis, predict X_test as reconstruction."""
    pca = PCA(n_components=n_components)
    Y_train_proj = pca.fit_transform(Y_train)
    # ... linear map from X to PCA space, then inverse transform
    # Implementation per IP §12.4 detail
```

#### `random.py`
```python
import numpy as np

def fit_predict(X_train, Y_train, X_test, seed=42):
    """Calibration-test baseline: predict random samples from Y_train distribution."""
    rng = np.random.default_rng(seed)
    return rng.permutation(Y_train)[:len(X_test)]  # simplest: shuffle Y_train
```

#### `persistence.py`
```python
import numpy as np

def fit_predict(perturbation_ids_train, Y_train, cell_type_train, perturbation_ids_test, cell_type_test):
    """Predict same perturbation in different cell type (transfer baseline)."""
    # For each test (pert, cell_type), find a train sample with same pert but different cell_type
    # Return that sample's Y as prediction
```

### Step 2: Implement WMSE harness (Day 3-4)

Build `phases/phase-1/subphase-1.2/output/scripts/delta/eval/wmse.py`:

```python
import numpy as np
from scipy.stats import spearmanr, kstest

def wmse(pred, true, weights=None):
    """Weighted MSE per IP §12.4. Default weight = 1/var(gene) for gene-wise weighting."""
    if weights is None:
        weights = 1.0 / (true.var(axis=0) + 1e-6)
    return np.average(np.mean((pred - true) ** 2, axis=0), weights=weights)

def hierarchical_wmse_spearman(pred, true, top_k=20, alpha=0.05):
    """
    IP §12.4 hierarchical testing:
      1. Compute WMSE.
      2. If WMSE significantly better than random (KS test), proceed.
      3. Then compute Spearman on top-k DEGs.
    """
    wmse_val = wmse(pred, true)
    # Compare to random baseline (need 100 random shuffles)
    random_wmse = [wmse(np.random.permutation(pred), true) for _ in range(100)]
    p_value = (np.array(random_wmse) <= wmse_val).mean()
    if p_value > alpha:
        return {"wmse": wmse_val, "wmse_p": p_value, "spearman_topk": None, "gate": "FAIL"}
    # Top-k DEGs by absolute fold change
    fold = np.abs(true - true.mean(axis=0)).max(axis=0)
    top_genes = np.argsort(fold)[-top_k:]
    spearman_per_pert = [spearmanr(pred[i, top_genes], true[i, top_genes]).correlation for i in range(len(pred))]
    return {"wmse": wmse_val, "wmse_p": p_value, "spearman_topk": np.nanmean(spearman_per_pert), "gate": "PASS"}
```

### Step 3: Implement FDR + calibration + stratified (Day 4-6)

#### `delta/eval/fdr.py`
```python
from statsmodels.stats.multitest import multipletests

def fdr_bh(p_values, alpha=0.05):
    return multipletests(p_values, alpha=alpha, method='fdr_bh')

def fdr_by(p_values, alpha=0.05):
    return multipletests(p_values, alpha=alpha, method='fdr_by')
```

#### `delta/eval/calibration.py`
```python
import numpy as np

def reliability_diagram(pred, true, n_bins=10):
    """Returns (bin_means, bin_pred_means, bin_true_means) for plotting."""
    # Implementation per scikit-learn calibration_curve

def ece(pred, true, n_bins=10):
    """Expected Calibration Error."""
    bin_means, bin_pred, bin_true = reliability_diagram(pred, true, n_bins)
    return np.average(np.abs(bin_pred - bin_true), weights=bin_means)
```

#### `delta/eval/stratified.py`
```python
def stratified_evaluation(pred, true, strata):
    """
    strata: dict with keys 'cell_type', 'perturbation_type', 'expression_level' → array of labels
    Returns: dict of per-stratum WMSE/Spearman.
    """
    results = {}
    for stratum_name, stratum_labels in strata.items():
        per_label = {}
        for label in np.unique(stratum_labels):
            mask = stratum_labels == label
            per_label[label] = hierarchical_wmse_spearman(pred[mask], true[mask])
        results[stratum_name] = per_label
    return results
```

### Step 4: End-to-end smoke test on Tahoe-100M subsample (Day 7-8)

```python
# Load 1M-cell Tahoe subsample (or 100K fallback)
# For baseline_name in ['linear', 'mean', 'pca', 'random', 'persistence']:
#   pred = baselines[baseline_name].fit_predict(X_train, Y_train, X_test)
#   metrics = hierarchical_wmse_spearman(pred, Y_test)
#   strat = stratified_evaluation(pred, Y_test, {'cell_type': ..., 'perturbation_type': ..., 'expression_level': ...})
#   calibration = {'ece': ece(pred, Y_test), 'reliability_data': reliability_diagram(pred, Y_test)}
#   ... write to results table

# Also test ONE method (e.g., GEARS) for cross-validation:
#   from gears_adapter import predict
#   pred_gears = predict(...)
#   metrics_gears = hierarchical_wmse_spearman(pred_gears, Y_test)
```

Aggregate into `phases/phase-1/subphase-1.2/output/delta_baselines_results.md`:

| Baseline / Method | WMSE | WMSE p | Spearman top-k | Gate | ECE | Cell-type strat | Pert-type strat |
|-------------------|-----:|-------:|---------------:|------|----:|----------------|-----------------|
| linear | ... | ... | ... | PASS/FAIL | ... | ... | ... |
| mean | ... | ... | ... | ... | ... | ... | ... |
| pca | ... | ... | ... | ... | ... | ... | ... |
| random | ... | ... | ... | should FAIL gate (calibration test) | ... | ... | ... |
| persistence | ... | ... | ... | ... | ... | ... | ... |
| GEARS (smoke test) | ... | ... | ... | ... | ... | ... | ... |

### Step 5: SLURM submission

Single SLURM job for the smoke test (other implementation work is interactive):

```bash
#!/bin/bash
#SBATCH --job-name=<8-char-cryptic>
#SBATCH --partition=gpu        # RTX 5000 Ada
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G              # Tahoe loader needs CPU RAM
#SBATCH --time=12:00:00
#SBATCH --account=pi_mg269

set -euo pipefail
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env-delta-v2
export PYTHONNOUSERSITE=1
export HF_HOME=/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/.hf_cache

python phases/phase-1/subphase-1.2/output/scripts/delta/eval/run_smoketest.py \
    --subsample 1000000 \
    --baselines linear,mean,pca,random,persistence \
    --methods gears
```

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| `../../tasks/task-005-delta-baselines.md` | This task spec |
| `../../../../../shared/notes/1.1-delta-methods-install.md` | Env paths, adapter locations, smoke test patterns |
| `../../../../../shared/notes/1.1-env-split.md` | env-delta-v2 vs env-cpa vs env-tahoex1 mapping |
| `../../../../../shared/notes/operational-practices.md` | RTX 5000 Ada policy, env hygiene |
| `../../../subphase-1.1/output/delta-tier1/gears_adapter.py` (and others) | Reusable adapters for Tahoe-100M |
| `../../../../../../Proposal/Delta.md` (§3, §4, §12) | Tahoe-100M format, method roster, stats framework |
| `../../../../../../Proposal/ImplementationPlan.md` (§5.3, §12.4) | Baselines spec + WMSE harness spec |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../shared/notes/1.2-scope-recommendations.md` | Items 14-17, 24 are explicit scope for this task |
| `../../../subphase-1.1/output/delta-tier1/scfoundation_smoketest.py` | Pattern for HuggingFace model loading |

### DO NOT READ

- Other SubAgents' task specs
- `../../../../../../Proposal/HumanOnlyProposal.md`
- Future subphase plans

---

## Output Artifacts

### Code and data artifacts

| Artifact | Path | Format |
|----------|------|--------|
| Baselines | `../../output/scripts/delta/baselines/{linear,mean,pca,random,persistence}.py` | Python |
| Evaluation harness | `../../output/scripts/delta/eval/{wmse,fdr,calibration,stratified}.py` | Python |
| Smoke test runner | `../../output/scripts/delta/eval/run_smoketest.py` | Python |
| Results table | `../../output/delta_baselines_results.md` | Markdown |
| Reliability diagrams (PNG) | `../../output/figures/reliability_*.png` | PNG |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-005-status.md` | `templates/status-report.md` |
| Cross-agent note | `../../../../../shared/notes/1.2-delta-baselines-results.md` | `templates/cross-agent-note.md` |

---

## Success Criteria (Zero Compromise)

1. [ ] All 5 baseline scripts exist at `../../output/scripts/delta/baselines/` and produce predictions on test split
2. [ ] WMSE harness (`wmse.py`) exists with `hierarchical_wmse_spearman` function
3. [ ] FDR (`fdr.py`) implements BH primary + BY sensitivity
4. [ ] Calibration (`calibration.py`) implements reliability diagram + ECE
5. [ ] Stratified eval (`stratified.py`) implements cell type × perturbation type × expression level
6. [ ] End-to-end smoke test ran on ≥1M-cell Tahoe-100M subsample (or 100K fallback if 1M too slow)
7. [ ] Results table at `../../output/delta_baselines_results.md` populated for all 5 baselines + ≥1 method (GEARS)
8. [ ] Random baseline FAILS the WMSE gate (validates the metric-gaming check)
9. [ ] Cross-agent note `1.2-delta-baselines-results.md` written
10. [ ] Status report written to `../../status/task-005-status.md`

---

## Verification

1. `ls ../../output/scripts/delta/baselines/` shows 5 .py files
2. `ls ../../output/scripts/delta/eval/` shows 5 .py files (wmse, fdr, calibration, stratified, run_smoketest)
3. `python -c "from delta.baselines import linear, mean, pca, random, persistence; print('all import OK')"` succeeds
4. Results table has ≥6 rows (5 baselines + ≥1 method) populated
5. The "random" row shows WMSE gate = FAIL (validates calibration check)
6. Status report exists with status `complete`

---

## Failure Protocol

1. **Tahoe-100M loader OOMs at 1M cells:** Reduce to 100K cells. Document in cross-agent note. Status: `complete` (the harness is what matters, not the subsample size).
2. **GEARS smoke test fails (env-delta-v2 broken):** Use scGPT or scFoundation as alternative method. Both also in env-delta-v2.
3. **Persistence baseline can't find matching cell-type pairs in subsample:** Use cell-type clustering as proxy; document the approximation.
4. **All baselines produce identical (nonsensical) output:** env or data loader bug. Status: `failed`. Help-needed.

Document everything in status report.
