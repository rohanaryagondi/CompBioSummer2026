# Delta (PerturbMark): Calibrated Perturbation Benchmarking on Tahoe-100M

## Target Venue: Nature Methods

## One-Sentence Pitch

The first independent, neutral benchmark of perturbation prediction methods on Tahoe-100M with calibrated metrics and difficulty stratification, answering "when does deep learning actually help?"

---

## Problem

The perturbation prediction field cannot answer its most basic question: do deep learning methods outperform simple linear baselines for predicting cellular responses to perturbations? The evidence is contradictory:

- **Ahlmann-Eltze et al. (NatMeth 2025):** 7 DL models fail against linear baselines.
- **Miller et al. (bioRxiv 2025):** Under calibrated metrics, DL wins.
- **scPerturBench (NatMeth 2026):** 27 methods, 29 datasets, but uses uncalibrated metrics, omits Tahoe-100M, and doesn't test cross-context generalization.
- **VCC 2025:** Random data with proper transformations outperformed legitimate models on MAE -- exposing metric gaming.

The controversy is partly a **measurement artifact**: under uncalibrated metrics (MSE, Pearson-delta), DL fails; under calibrated metrics (WMSE, rank-based), DL succeeds. Nobody has resolved this on the world's largest perturbation dataset (Tahoe-100M: 100M cells, 50 cell lines, 379 compounds).

---

## What We Do

Run the definitive neutral benchmark on Tahoe-100M with calibrated evaluation.

### Dataset: Tahoe-100M

- 100.6M cells, 50 cancer cell lines, 379 compounds, 17,813 conditions
- CC0 license, publicly available via CZ CELLxGENE Discover
- Cell village design eliminates cell-line-level batch effects
- 429 GB total

### Methods Evaluated

**Tier 1 (mandatory, 5 DL + 5 baselines):**

| # | Method | Type | Notes |
|---|--------|------|-------|
| 1 | GEARS | GNN | Needs memory optimization for 100M cells |
| 2 | scGPT | Transformer | Available |
| 3 | CPA | VAE | Last release 2023 |
| 4 | scFoundation | Large foundation model | Available |
| 5 | Tahoe-x1 | Foundation model (3B params) | Native Tahoe-100M streaming; Apache 2.0 |
| 6 | Linear regression | Baseline | |
| 7 | Mean expression | Baseline | |
| 8 | PCA-based | Baseline | |
| 9 | Random | Calibration control | |
| 10 | Persistence | Baseline | Same cell type, different perturbation |

**Tier 2 (if feasible):**
- AetherCell (sole viable candidate; 15 GitHub stars, code available)

**Dropped (no code/weights):** scPPDM, AlphaCell, X-Cell, pertTF

### Evaluation Framework

**7 Calibrated Metrics:**

| Metric | Type | Calibration Status |
|--------|------|-------------------|
| WMSE | Weighted MSE (DEG-aware) | Calibrated (Miller et al.) |
| Spearman on top-k DEGs | Rank correlation | Calibrated |
| DEG-F1 | Classification | Calibrated |
| Pearson-delta (centroid-ref) | Corrected correlation | Calibrated (Systema) |
| Energy distance | Distributional | Partially calibrated |
| Reliability diagram / ECE | Calibration metric | Novel for this field |
| Dynamic range fraction | Meta-metric | Validates other metrics |

**Primary analysis:** WMSE gates Spearman on top-k DEGs via hierarchical testing (Dmitrienko & D'Agostino, 2013). Test WMSE first; if significant, test Spearman without alpha penalty.

**FDR:** BH primary (field standard is NO correction; BH already exceeds it). BY as sensitivity analysis.

### Difficulty Stratification (4 Tiers)

| Tier | Description | Challenge |
|------|------------|-----------|
| 0 | In-distribution | Seen perturbation, seen context |
| 1 | Unseen perturbation, same context | Standard holdout |
| 2 | Seen perturbation, new context | Cross-context transfer |
| 3 | Unseen perturbation, new context | True zero-shot |

Tahoe-100M's 50 cell lines and 379 compounds provide the first dataset with sufficient diversity for systematic Tier 2-3 evaluation.

---

## Differentiation from Existing Benchmarks

| Feature | scPerturBench | SCALE | PerturbMark (ours) |
|---------|--------------|-------|-------------------|
| Dataset | 29 small datasets | Tahoe-100M (self-eval) | Tahoe-100M (independent) |
| Metrics | 4/6 uncalibrated | Self-reported | 7 calibrated metrics |
| Difficulty tiers | Tier 0-1 | Not stratified | Tier 0-3 |
| Neutrality | Academic benchmark | Developer benchmark | Independent, neutral |
| Tahoe-x1 included | No | No (self-eval) | Yes |
| Calibration analysis | No | No | Yes (reliability diagrams) |
| Anti-gaming | No | No | Yes (random baseline, DRF) |

---

## Timeline

| Phase | Dates | Activities |
|-------|-------|-----------|
| Pre-project | Apr 15-30 | Tahoe-100M download + data pipeline (scDataset) |
| Weeks 1-5 | May 1 - Jun 6 | Method setup: GEARS, scGPT, CPA, scFoundation, Tahoe-x1, baselines |
| Weeks 6-9 | Jun 7 - Jul 4 | Full evaluation runs on Tahoe-100M |
| Weeks 10-13 | Jul 5 - Aug 1 | Cross-context evaluation, difficulty stratification, calibration |
| Weeks 14-15 | Aug 1 - Aug 15 | Figures, manuscript, **preprint** |
| Week 16 | Sep 1 | NatMeth submission |

**Preprint by August 15 is non-negotiable.** Scoop risk is 55-65% for differentiation erosion. Speed is the primary competitive advantage.

**Compute:** ~15,000-20,000 GPU-hours. Most DL methods train on 8-16 GB GPU memory (RTX 5000 Ada sufficient). Only scFoundation and Tahoe-x1 may need H200 for fine-tuning.

---

## Risks and Mitigations

| Risk | Probability | Mitigation |
|------|------------|-----------|
| Delta differentiation erosion (SCALE, VCC) | 55-65% | Frame as "neutral, calibrated" -- none of the competitors are independent |
| Ahlmann-Eltze challenge (DL doesn't beat linear) | 30% | "When does DL help?" framing works regardless of outcome |
| Tahoe-100M memory issues | 30% | scDataset streaming (48x speedup over AnnLoader) |
| <3 Tier 1 methods running | 15% | Drop failed methods; proceed with remainder |
| Independent Tahoe-100M benchmark published first | 15% | Reframe as replication + extension |

---

## Kill Criteria

| ID | Criterion | Threshold | Date |
|----|-----------|-----------|------|
| DK1 | Data pipeline fails | Can't load Tahoe-100M by May 31 | May 31 |
| DK2 | <3 methods running | Methods fail to reproduce | June 6 |
| DK3 | Independent benchmark published first | Competitor preprint | Ongoing |
| DK4 | All DL matches linear | No DL beats linear on any metric | Aug 1 |
| DK5 | Tahoe-x1 unavailable | Weights retracted | May 15 |

**DK4 is NOT a kill** -- it's still publishable. "Deep learning still does not outperform linear baselines, even at 100M-cell scale" is a significant finding that extends Ahlmann-Eltze.

---

## What Makes This Novel

1. **First independent Tahoe-100M benchmark.** Only self-evaluations exist (Tahoe-x1, SCALE).
2. **Calibrated metrics resolve the DL-vs-linear controversy.** The field's leading benchmarks use uncalibrated metrics.
3. **Tier 0-3 difficulty stratification.** First systematic test of when DL helps vs when it doesn't.
4. **Anti-gaming measures.** Random baseline, reliability diagrams, DRF -- learned from VCC 2025.
5. **Neutrality.** Not a method paper. Not developer self-evaluation. Independent and open.

---

## References

Key papers: Ahlmann-Eltze et al. (NatMeth 2025); Wei et al./scPerturBench (NatMeth 2026); Miller et al. (bioRxiv 2025) calibrated metrics; Camillo et al. (arXiv 2025) WMSE; Zhang et al. (bioRxiv 2025) Tahoe-100M; Gandhi et al. (bioRxiv 2025) Tahoe-x1; Vinas Torne et al./Systema (NatBiotech 2025); VCC 2025; SCALE (NVIDIA, bioRxiv 2026).
