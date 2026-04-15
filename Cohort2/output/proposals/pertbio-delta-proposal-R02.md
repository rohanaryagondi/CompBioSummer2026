---
agent: Perturbation Biology & Single-Cell Benchmarking Expert (pertbio)
round: 2
date: 2026-04-14
type: proposal
proposal_id: delta-perturbmark
---

# Proposal: PerturbMark -- A Cross-Context Benchmark Resolving the Perturbation Prediction Controversy

## Proposing Agent

Dr. Perturbation Biology & Single-Cell Benchmarking Expert (pertbio), Cohort 2 Deep
Divers. 15+ years in computational genomics, single-cell biology, and evaluation
framework design. Brings deep expertise in benchmark architecture, metric calibration,
information leakage prevention, and the sociology of benchmark adoption. This proposal
is grounded in a 572-line Round 1 research note with 28 citations, the April 2026
landscape audit of 18+ perturbation prediction methods, and the full metric controversy
analysis spanning Ahlmann-Eltze et al. (NatMeth 2025), Miller et al. (bioRxiv Oct 2025),
Camillo et al. (arXiv Jun 2025), and Dibaeinia et al. (bioRxiv Feb 2026).

---

## Problem Statement

The perturbation prediction field cannot answer its most basic question: do deep
learning methods actually outperform simple linear baselines for predicting cellular
responses to perturbations? Between March 2025 and April 2026, the field has produced
contradictory evidence at an unprecedented rate. Ahlmann-Eltze et al. (NatMeth 2025)
showed 7 DL models failing against linear baselines. Miller et al. (bioRxiv 2025)
showed DL winning under calibrated metrics. scPerturBench (NatMeth 2026) benchmarked
27 methods across 29 datasets but used 4 of 6 metrics with known failure modes and did
not include Tahoe-100M, the world's largest chemical perturbation dataset. Meanwhile,
an explosion of 8+ new foundation models in January--March 2026 (AlphaCell, X-Cell,
AetherCell, SCALE, pertTF, Stack, State, LPM) has outpaced the evaluation infrastructure.
The field is drowning in claims and starving for evidence. PerturbMark provides the
definitive, neutral, calibrated evaluation that resolves this crisis.

---

## Vision

After PerturbMark, the field has a definitive answer to the DL-vs-linear controversy,
stratified by difficulty tier (Tier 0--3), perturbation type, mechanism of action, and
cellular context. Researchers know which method to use for which prediction task.
Benchmark developers adopt the calibrated 7-metric suite and Tier 0--3 framework as
the standard for evaluating future models. Nature Methods publishes PerturbMark as the
reference benchmark for chemical perturbation prediction, analogous to what ImageNet
was for computer vision. The DL-vs-linear debate moves from "does it work?" to "under
what conditions does it work, and by how much?"

---

## Background and Evidence

### Current State of the Art

The perturbation prediction field is fractured along four axes:

**Axis 1: Metrics.** Papers use at least 13 different metrics. MSE and control-referenced
Pearson-delta are "poorly calibrated" (dynamic range fraction near zero; Miller et al.,
2025). WMSE and rank-based alternatives are "well-calibrated" (Miller et al., 2025). Under
uncalibrated metrics, DL fails; under calibrated metrics, DL succeeds. This means the
DL-vs-linear debate is partly a measurement artifact.

**Axis 2: Datasets.** scPerturBench uses 29 datasets from the scPerturb harmonized
collection (Peidli et al., NatMeth 2024), dominated by small-scale genetic perturbation
screens. Tahoe-100M (Zhang et al., bioRxiv 2025) -- 100.6M cells, 50 cell lines, 379
compounds, CC0 -- has not been used for systematic benchmarking. The OP3 benchmark
(NeurIPS 2024) covers only 146 compounds in PBMCs.

**Axis 3: Difficulty.** Most evaluations test only Tier 0 (in-distribution) or Tier 1
(unseen perturbation, same context). Cross-context generalization (Tier 2--3) is the
real-world challenge but is rarely tested systematically. "Virtual Cells Need Context,
Not Just Scale" (bioRxiv Feb 2026) demonstrates that context diversity, not cell count,
drives cross-context generalization.

**Axis 4: Methods.** The March 2026 model explosion (X-Cell, AlphaCell, AetherCell,
SCALE, pertTF) has produced multiple claims of "state-of-the-art" performance, but none
has been independently evaluated against all others under standardized conditions.

### Recent Developments That Enable This

1. **Tahoe-100M release** (Feb 2025): CC0-licensed, 100M cells, 50 cell lines, 379
   compounds, plate-matched DMSO controls. The first dataset with sufficient scale and
   diversity for Tier 3 cross-context evaluation of chemical perturbations.

2. **Metric calibration framework** (Miller et al., Oct 2025): Introduced interpolated
   duplicate positive controls and dynamic range fraction, enabling systematic identification
   of well-calibrated vs poorly-calibrated metrics.

3. **DEG-aware weighting** (Camillo et al., Jun 2025): WMSE weights by perturbation-specific
   differential expression signal, eliminating mode collapse rewards.

4. **scPerturBench publication** (Wei et al., NatMeth Feb 2026): Established the
   benchmark-paper precedent at Nature Methods, proving editorial appetite for this format.

5. **March 2026 model explosion:** AlphaCell (bioRxiv Mar 2026), X-Cell (Xaira,
   bioRxiv Mar 2026), AetherCell (bioRxiv Mar 2026), SCALE (NVIDIA, bioRxiv Mar 2026),
   pertTF (bioRxiv Mar 2026). All claim cross-context generalization but none has been
   independently benchmarked.

6. **DataSAIL** (Hummer et al., NatComm Apr 2025): Leakage-reduced splitting framework
   applicable to biological benchmark construction.

### Key Prior Work

1. **Ahlmann-Eltze, Huber & Anders (NatMeth 2025):** Benchmarked scGPT, scFoundation,
   GEARS against linear baselines on Norman/Adamson/Replogle. None outperformed. Used
   top-1000 expressed genes for evaluation. Established the controversy.

2. **Wei et al. / scPerturBench (NatMeth 2026, vol. 23, pp. 451--464):** 27 methods,
   29 datasets, 6 metrics (MSE, PCC-delta, E-distance, Wasserstein, KL-divergence,
   Common-DEGs). Found no single method dominates; proposed bioLord-emCell for context
   generalization. Does NOT include Tahoe-100M, calibrated metrics, or Tier 3 evaluation.

3. **Miller et al. (bioRxiv Oct 2025):** "Well-Calibrated Metrics." 14 datasets, 13
   metrics. Showed MSE and Pearson(delta-ctrl) have dynamic range fraction near zero.
   Under WMSE and rank-based metrics, DL outperforms baselines. Introduced interpolated
   duplicate and dynamic range fraction.

4. **Camillo et al. (arXiv Jun 2025):** "Diversity by Design." Showed control-referenced
   deltas reward mode collapse. Introduced WMSE as loss function, which reduces mode
   collapse and reveals genuine DL advantages.

5. **Dibaeinia et al. (bioRxiv Feb 2026):** Showed Wasserstein distance fails under
   variance scaling, Energy distance overlooks gene-gene interaction disruptions, DEG
   recall is ~9% despite favorable aggregate metrics. Correlation between DEG-F1 and
   aggregate metrics is weak (r = 0.26 with Corr-delta; r = -0.05 with L2-delta).

6. **Wong et al. (Bioinformatics 2025):** CRISPR-informed mean surpasses GEARS by
   4.7--213.9x and scGPT by 3.9--155.4x. Demonstrates that knowledge-informed simple
   baselines are powerful.

7. **Vinas Torne et al. / Systema (NatBiotech 2025):** Performance of DL models
   correlates with systematic variation (r = 0.91 for scGPT, r = 0.95 for GEARS).
   Introduced centroid-referenced Pearson-delta as a corrected metric.

8. **Zhang et al. / Tahoe-100M (bioRxiv Feb 2025):** 100.6M cells, 50 cancer cell
   lines, 379 compounds, 17,813 unique conditions. Cell village approach eliminates
   cell-line-level batch effects within plates. CC0 license.

9. **Miladinovic et al. / LPM (NatCompSci Nov 2025):** First model integrating genetic
   and chemical perturbations in shared latent space. Demonstrates scaling behavior:
   accuracy improves with more perturbation types and contexts.

10. **Xaira / X-Cell (bioRxiv Mar 2026):** 4.9B-parameter diffusion language model.
    Claims 5x Pearson-delta improvement. Zero-shot T-cell generalization. Power-law
    scaling. Trained on X-Atlas/Pisces (25.6M cells, 16 CRISPRi contexts). Genetic
    perturbations only.

---

## Proposed Approach

### Overview

PerturbMark is a cross-context benchmark for chemical perturbation prediction built
on Tahoe-100M (100.6M cells, 50 cell lines, 379 compounds, CC0). It evaluates 10+
methods (8+ DL, 5 mandatory linear baselines) across 4 difficulty tiers (Tier 0:
in-distribution through Tier 3: unseen perturbation in unseen cell line) using a
calibrated 7-metric suite that avoids all documented failure modes. The benchmark
resolves the DL-vs-linear controversy by showing results under both calibrated and
uncalibrated metrics, stratified by difficulty, mechanism of action, and cellular
context. It is supplemented by batch-effect controls (negative control, batch-shuffled
null, within-vs-across-plate analysis) and information leakage prevention protocols.

### Method Details

#### Component 1: Dataset Stack and Preprocessing

**Primary dataset: Tahoe-100M (chemical perturbation)**

| Attribute | Value |
|-----------|-------|
| Total cells | 100.6 million |
| Expression data rows | 95.6 million |
| File size | 429 GB (Parquet, HuggingFace) |
| Cell lines | 50 cancer cell lines (47 usable with sufficient representation) |
| Compounds | 379 distinct drugs |
| Unique conditions | 17,813 (cell line x drug) |
| Organ types | 13 distinct |
| MOA categories | 25 fine-grained, 3 broad (inhibitor/antagonist, activator/agonist, unclear) |
| License | CC0-1.0 |
| Data format | Sparse tokenized (only non-zero genes stored) |
| Expression type | Raw counts (no normalization applied) |
| Controls | Plate-matched DMSO_TF |
| Gene annotations | 62,700 genes, Ensembl release 109, GRCh38 |

**Supplementary datasets (for genetic perturbation validation):**

| Dataset | Perturbation Type | Cells | Cell Lines | Genes | Access |
|---------|------------------|-------|------------|-------|--------|
| Replogle K562 (Cell 2022) | CRISPRi | ~2.5M | K562 | genome-wide | Figshare/pertpy |
| Replogle RPE1 (Cell 2022) | CRISPRi | ~1M | RPE1 | genome-wide | Figshare/pertpy |
| Norman (Science 2019) | CRISPRa | ~90K | K562 | 287 perturbations (100 single + 131 double) | Figshare/pertpy |

**Preprocessing protocol:**

The preprocessing pipeline uses scanpy (scverse ecosystem) with GPU acceleration via
RAPIDS where required by Tahoe-100M's scale.

**Step 1: Quality Control Filtering**
- Minimum genes per cell: 200 (sc.pp.filter_cells, min_genes=200)
- Minimum cells per gene: 50 (sc.pp.filter_genes, min_cells=50)
- Mitochondrial percentage threshold: < 20% (derived from mean_pcnt_mito in sample_metadata)
- Remove cells with > 10,000 genes (potential doublets)
- Remove cells with < 500 UMIs (potential empty droplets)
- Ambient RNA: not corrected in Tahoe-100M release; assess contribution via
  SoupX/DecontX on 3 representative cell lines, report as supplementary analysis.
  If ambient RNA fraction > 10%, apply SoupX correction.

**Step 2: Normalization**

Two normalization strategies tested in parallel (normalization sensitivity analysis):

*Strategy A: Library-size normalization + log1p (standard)*
```
sc.pp.normalize_total(adata, target_sum=10000)
sc.pp.log1p(adata)
```

*Strategy B: Analytic Pearson residuals (modern, recommended by Lause et al. 2021)*
```
sc.experimental.pp.normalize_pearson_residuals(adata)
```

If results substantively differ between Strategy A and B (>5% change in method rankings
under WMSE), this is itself a finding about normalization sensitivity and is reported
as a main-text result. Otherwise, Strategy A is used as default for backward
compatibility.

**Step 3: Gene Selection**

Gene selection is a critical confound. Different gene sets give different conclusions
(Ahlmann-Eltze used top-1000 expressed; scPerturBench used DEGs; Virtual Cell Challenge
used transcriptome-wide). PerturbMark reports on all four:

| Gene Set | Definition | Expected Size | Primary/Secondary |
|----------|-----------|---------------|-------------------|
| **DEGs per condition** | Wilcoxon rank-sum test, BH-adjusted p < 0.05, |log2FC| > 0.5, vs plate-matched DMSO | 50--500 per condition | **Primary** (most biologically relevant) |
| **Union DEGs** | Union of all per-condition DEGs across all conditions in training set | 2,000--5,000 | Secondary |
| **HVGs** | sc.pp.highly_variable_genes, flavor='seurat_v3', n_top_genes=2000 | 2,000 | Secondary |
| **All expressed genes** | All genes passing QC filters | 15,000--20,000 | Secondary (completeness check) |

**Rationale for DEGs-per-condition as primary:** This is the biologically meaningful
gene set. A method that accurately predicts expression of housekeeping genes but misses
differentially expressed genes has not learned perturbation biology. This choice is
directly supported by Dibaeinia et al. (2026), who showed DEG recall was only ~9%
despite favorable aggregate metrics on unconstrained gene sets.

**Step 4: Pseudobulk Aggregation**

For computational tractability and to match the evaluation paradigm of most perturbation
prediction methods:
- Aggregate to pseudobulk: mean expression per (cell_line, drug, plate) group
- Minimum 30 cells per pseudobulk sample (filter groups below threshold)
- Single-cell evaluation reported as supplementary (MMD metric only, which requires
  distributional comparison)

**Step 5: Batch Correction Assessment**

Tahoe-100M uses a cell village design (all 50 cell lines co-cultured per plate), which
theoretically eliminates cell-line-level batch effects within plates. We verify this:
- Compute plate-to-plate variation for DMSO controls within same cell line
- If plate effect explains > 10% of variance (by ANOVA on PC1--5), apply ComBat or
  Harmony correction and report both corrected and uncorrected results
- Assess whether plate-matched DMSO normalization (subtract plate-specific DMSO mean
  from treated cells) suffices to remove residual plate effects

#### Component 2: Cross-Context Difficulty Tiers (Tier 0--3)

**Tier 0: In-Distribution (Interpolation Test)**

| Attribute | Specification |
|-----------|--------------|
| Definition | Predict expression for held-out cells under SEEN perturbation in SEEN cell line |
| Split type | Random 80/10/10 cell-level split within each (cell_line, drug) group |
| Purpose | Sanity check; confirms methods learn from training data |
| Expected outcome | All methods should perform well; DL should match or exceed baselines |
| Sample size | All 17,813 conditions contribute; minimum 30 cells per condition |
| Replication | 5 random seeds for cell-level split |

**Tier 1: Unseen Perturbation (Perturbation Generalization)**

| Attribute | Specification |
|-----------|--------------|
| Definition | Predict expression under UNSEEN perturbation in SEEN cell line |
| Split type | Perturbation-level split: 80% compounds train, 10% validation, 10% test |
| Split constraint | Split by compound identity (all doses of a compound in same split) |
| Leakage prevention | Compounds sharing >80% structural similarity (Tanimoto on Morgan fingerprints, radius=2) must be in same split. Compounds sharing the same molecular target (from drug_metadata targets field) must be in same split. |
| Sample size per fold | ~38 held-out compounds x 47 cell lines = ~1,786 test conditions |
| Replication | 5-fold CV at compound level |

**Cell line hold-out selection for Tier 2--3:**

We hold out cell lines by organ type to maximize biological novelty. Based on the
Tahoe-100M cell line composition (50 lines across 13 organs), the hold-out strategy is:

| Fold | Held-Out Organs | Approximate Lines Held Out | Justification |
|------|----------------|---------------------------|---------------|
| 1 | Pancreas | 5--6 lines | KRAS-driven cancers, distinct from training |
| 2 | Skin | 4--5 lines | Melanoma biology, distinct drug sensitivity profile |
| 3 | Haematopoietic/Lymphoid | 4--5 lines | Suspension culture, different gene programs |
| 4 | Breast + Ovary | 5--6 lines | Hormone-responsive cancers |
| 5 | Central Nervous System | 3--4 lines | Brain-specific expression programs |

Rationale: Organ-based hold-out ensures held-out cell lines are biologically distinct
from training lines, not just label-held-out. This is a harder, more realistic test
than random cell line hold-out and directly addresses the critique of "Virtual Cells
Need Context, Not Just Scale" (bioRxiv Feb 2026).

**Tier 2: Unseen Context, Known Perturbation (Context Generalization)**

| Attribute | Specification |
|-----------|--------------|
| Definition | Predict expression for KNOWN perturbation in UNSEEN cell line |
| Split type | Cell-line-level split: held-out lines excluded from all training |
| Perturbation requirement | Test compounds must appear in training with other cell lines |
| Coverage constraint | Each held-out cell line must have >= 100 tested compounds that also appear in training |
| Sample size per fold | ~5 held-out cell lines x ~300 overlapping compounds = ~1,500 test conditions |
| Replication | 5-fold CV at cell-line level (organ-based folds above) |

**Tier 3: Full Cross-Context (True Transport)**

| Attribute | Specification |
|-----------|--------------|
| Definition | Predict expression for UNSEEN perturbation in UNSEEN cell line |
| Split type | Both cell line AND perturbation held out jointly |
| Construction | Intersection of Tier 1 held-out perturbations and Tier 2 held-out cell lines |
| Matrix completion constraint | Held-out compound P must appear in training with non-held-out cell lines; held-out cell line C must appear in training with non-held-out compounds |
| Sample size per fold | ~5 held-out lines x ~38 held-out compounds = ~190 test conditions per fold (sufficient for 80% power at alpha=0.05 for detecting 0.05 Pearson-delta improvement given ~400 total across 5 folds) |
| MOA stratification | Report Tier 3 results stratified by held-out compound MOA category |
| Replication | Same 5-fold structure as Tier 2; perturbation split nested within |

**Statistical power analysis:**

Detecting a 0.05 improvement in Pearson-delta with 80% power at alpha = 0.05 requires
approximately 400 test instances per comparison (paired t-test on per-condition metric
values). Per tier:

| Tier | Test conditions per fold | Total across 5 folds | Adequate power? |
|------|--------------------------|----------------------|-----------------|
| 0 | ~17,813 | ~17,813 | Yes (abundant) |
| 1 | ~1,786 | ~8,930 | Yes |
| 2 | ~1,500 | ~7,500 | Yes |
| 3 | ~190 | ~950 | Yes (borderline; sufficient for primary comparison, limited for subgroup analysis) |

For Tier 3 MOA-stratified analysis, some MOA categories may have insufficient power.
Report confidence intervals and note underpowered comparisons explicitly.

#### Component 3: Method Evaluation Protocol

**Priority 1 -- Immediately runnable (include in benchmark regardless):**

| Method | Architecture | Chemical Perturbation Support | Run Mode | Est. GPU-hrs |
|--------|-------------|------------------------------|----------|-------------|
| **CPA** | Disentangled VAE | Native (designed for chemical) | Retrain per fold | 100 |
| **PerturbNet** | VAE + normalizing flow (ZINB) | Native (ChemicalVAE encoder) | Retrain per fold | 100 |
| **scGPT** | Transformer FM | Fine-tune with compound tokens | Fine-tune per fold | 200 |
| **Scouter** | LLM embeddings + compressor-generator | Adaptable (LLM gene embeddings) | Retrain per fold | 50 |
| **State** | State transition + cell embedding | Yes (perturbation-agnostic architecture) | Fine-tune/evaluate | 100 |

**Priority 2 -- Code available, retraining may be needed:**

| Method | Architecture | Chemical Perturbation Support | Run Mode | Est. GPU-hrs |
|--------|-------------|------------------------------|----------|-------------|
| **Tahoe-x1** | Masked-expression FM (3B params) | Native (trained on Tahoe-100M) | Inference only; flag pre-training contamination | 100 |
| **X-Cell** | Diffusion language model | Genetic only (CRISPRi); exclude from chemical benchmark, include in Replogle supplementary | Inference with public weights if available | 50 (supplementary only) |
| **LPM** | Integrated chemical + genetic FM | Native (cross-perturbation) | Evaluate if weights public | 100 |

**Priority 3 -- Include if code/weights become public before execution:**

| Method | Status as of April 2026 | Action |
|--------|------------------------|--------|
| AlphaCell | Preprint only (bioRxiv Mar 2026) | Monitor GitHub; include if released by May 15, 2026 |
| AetherCell | Preprint only (bioRxiv Mar 2026) | Monitor; include if released by May 15, 2026 |
| SCALE | Preprint (NVIDIA, bioRxiv Mar 2026) | Monitor; flag Tahoe-100M pre-training contamination |
| Stack | Preprint (Arc Institute, bioRxiv Jan 2026) | Monitor; include if released |
| pertTF | Preprint (bioRxiv Mar 2026) | Genetic only; Replogle supplementary if released |

**Fairness protocol:**

To ensure fair comparison across methods of vastly different scale:

1. **Training data:** All methods trained on same Tahoe-100M splits (train/val/test).
   No external perturbation data allowed during training for the primary benchmark.
2. **Compute budget:** Report wall-clock time and GPU-hours per method. Include a
   "compute-adjusted" analysis: performance normalized by GPU-hours.
3. **Hyperparameter budget:** Each method gets a maximum of 50 hyperparameter
   configurations (random search on validation set). Report best validation performance
   configuration.
4. **Pre-training contamination flag:** Methods pre-trained on Tahoe-100M (Tahoe-x1,
   SCALE) are marked with an asterisk (*) in all results tables. Their results are
   reported in a separate sub-panel. A strict hold-out of entire cell lines and
   compounds ensures zero overlap between pre-training splits used by these models
   and our test set -- but perfect decontamination cannot be guaranteed for pre-trained
   models. This limitation is stated explicitly.
5. **Model size reporting:** Report parameter count for all methods alongside performance.

**Handling methods that cannot run on chemical perturbations:**

Models designed exclusively for genetic perturbations (GEARS, X-Cell, pertTF) cannot
be directly applied to chemical perturbation prediction on Tahoe-100M. These methods
are:
- Excluded from the primary Tahoe-100M benchmark
- Evaluated on the supplementary Replogle/Norman genetic perturbation benchmark
- Their absence from the chemical benchmark is documented with explicit technical
  justification

#### Component 4: Mandatory Linear Baselines

Every DL method is compared against all 5 linear baselines. A DL method that cannot
beat all 5 on calibrated metrics cannot claim superiority.

**Baseline 1: No-Change Model (Mean Control)**

| Attribute | Specification |
|-----------|--------------|
| Prediction | y_pred = mean(DMSO_ctrl_cells) for the plate-matched control group |
| Interpretation | "The perturbation does nothing" |
| Compute | ~0 GPU-hrs (CPU matrix operations) |
| Reference | Ahlmann-Eltze et al. (NatMeth 2025) |

For each test condition (cell_line c, drug d, plate p):
y_pred(c, d) = (1/|S|) * sum_{i in S} y_i, where S = {cells in (c, DMSO_TF, p)}

**Baseline 2: Additive Shift Model**

| Attribute | Specification |
|-----------|--------------|
| Prediction | y_pred = mean(ctrl_c) + [mean(treated_d_train) - mean(ctrl_train)] |
| Interpretation | "Apply the average perturbation effect observed in training" |
| Construction | For test condition (cell_line c, drug d): compute mean perturbation effect delta_d from training cell lines; add delta_d to test cell line control mean |
| Compute | ~0 GPU-hrs |
| Reference | Ahlmann-Eltze et al. (NatMeth 2025) |

Formally: delta_d = (1/|T|) * sum_{c' in T} [mean(y_{c',d}) - mean(y_{c',DMSO})],
where T = training cell lines that received drug d.
y_pred(c, d) = mean(y_{c,DMSO}) + delta_d

**Baseline 3: CRISPR-Informed Mean**

| Attribute | Specification |
|-----------|--------------|
| Construction for chemical perturbations | Use drug_metadata targets field to identify target genes for drug d. Identify all drugs in training set that target the same gene(s). Average their perturbation effects as the prediction for drug d. |
| Fallback | If no target-sharing drugs in training, fall back to Baseline 2 (additive shift) |
| Compute | ~0 GPU-hrs |
| Reference | Wong et al. (Bioinformatics 2025) |

Formally: For drug d with targets G_d, define the set of training drugs sharing at
least one target: D_shared = {d' in train : G_{d'} intersect G_d != empty}.
y_pred(c, d) = mean(y_{c, DMSO}) + (1/|D_shared|) * sum_{d' in D_shared} delta_{d'}

**Baseline 4: Matrix Factorization (Linear Embedding Model)**

| Attribute | Specification |
|-----------|--------------|
| Model | Y = G * W * P^T + b, where G = gene embeddings (K-dim), P = perturbation embeddings (L-dim), W = K x L interaction matrix, b = row means |
| Fitting | Ridge regression with lambda = 0.1 (Ahlmann-Eltze specification) |
| Rank | K = L = 50 (test K in {10, 25, 50, 100} on validation set) |
| Gene features | One-hot gene identity |
| Perturbation features | Morgan fingerprint (radius=2, 2048 bits) concatenated with target gene one-hot |
| Compute | ~10 GPU-hrs (matrix operations on full Tahoe-100M) |
| Reference | Ahlmann-Eltze et al. (NatMeth 2025), adapted for chemical perturbations |

**Baseline 5: Linear Regression (Per-Gene Ridge)**

| Attribute | Specification |
|-----------|--------------|
| Model | For each gene g: y_g = beta_0 + beta_drug * X_drug + beta_cell * X_cell + epsilon |
| Features | X_drug: Morgan fingerprint (radius=2, 2048 bits) + MOA one-hot (25 categories) + target gene indicators. X_cell: cell line identity one-hot + DepMap gene essentiality scores (binary) + driver mutation indicators |
| Regularization | Ridge (alpha chosen by 5-fold CV on training set from {0.01, 0.1, 1, 10, 100}) |
| Compute | ~10 GPU-hrs (parallelized across genes) |
| Advantage over Baseline 4 | Uses cell-line features, enabling Tier 2--3 prediction via feature generalization |

#### Component 5: Calibrated 7-Metric Suite

**Primary Metrics (Calibrated -- Used for Method Ranking)**

**Metric 1: WMSE (Weighted Mean Squared Error)**

Formula: WMSE = (1/G) * sum_{g=1}^{G} w_g * (y_g - y_hat_g)^2

where w_g = |delta_g| / sum_g |delta_g|, and delta_g = mean(y_g_treated) - mean(y_g_ctrl)
for gene g in the ground-truth data.

What it measures: Prediction accuracy weighted by the magnitude of the true perturbation
effect. Genes with large perturbation effects contribute more to the error.

Why included: Well-calibrated (Miller et al., 2025). Correctly penalizes mean prediction
(mode collapse) because w_g upweights genes that change, which the mean baseline misses.

Known limitation: Requires ground-truth perturbation effect to compute weights. In
practice, weights are computed from the ground-truth test data, which is available for
benchmark evaluation but not for deployment. Sensitivity to weight estimation noise
should be reported.

**Metric 2: R^2_w(delta) -- Weighted Coefficient of Determination on Perturbation Effects**

Formula: R^2_w(delta) = 1 - [sum_g w_g * (delta_g - delta_hat_g)^2] / [sum_g w_g * (delta_g - mean(delta))^2]

where delta_g = y_g_treated - y_g_ctrl (ground truth), delta_hat_g = y_hat_g - y_g_ctrl
(predicted effect), and weights w_g are the same DEG-aware weights as WMSE.

What it measures: Variance explained in the perturbation effect (not raw expression).
Corrects for the high baseline correlation between treated and control expression.

Why included: Directly addresses the systematic variation confound (Systema, NatBiotech
2025). Under this metric, a model must capture perturbation-specific signal beyond
the systematic cell-line expression pattern.

**Metric 3: DRF (Dynamic Range Fraction) -- Meta-Metric for Calibration**

Formula: DRF = (metric(model) - metric(negative_ctrl)) / (metric(positive_ctrl) - metric(negative_ctrl))

where negative_ctrl = random permutation of predictions across conditions (destroys
perturbation signal), and positive_ctrl = interpolated duplicate (Miller et al., 2025):
predictions drawn from held-out replicates of the same condition.

What it measures: The fraction of the metric's dynamic range that the model occupies.
DRF near 0 means the metric cannot distinguish model from noise. DRF near 1 means
the metric can distinguish model from perfect prediction.

Why included: Meta-metric that validates whether other metrics are working properly.
Report DRF for every metric. If DRF < 0.1 for a metric, that metric is flagged as
unreliable for the dataset.

**Secondary Metrics (Standard -- Reported for Backward Compatibility)**

**Metric 4: Pearson-delta (centroid-referenced)**

Formula: Pearson(delta_pred, delta_truth), where delta = y_treated - y_centroid,
y_centroid = mean across all perturbation conditions for that cell line.

What it measures: Correlation of perturbation effects relative to the cell-line centroid,
not the control. Reduces inflation from systematic variation.

Reference: Systema (Vinas Torne et al., NatBiotech 2025).

Why preferred over ctrl-referenced: Ctrl-referenced Pearson-delta is inflated by
systematic variation r = 0.91--0.95 (Systema, 2025). Centroid referencing removes
shared cell-line expression patterns.

**Metric 5: MSE (Mean Squared Error -- with calibration warning)**

Formula: MSE = (1/G) * sum_g (y_g - y_hat_g)^2

Why included: Standard metric for backward compatibility and comparison with prior
benchmarks. ALWAYS reported with DRF. If DRF(MSE) < 0.1, results table includes a
footnote: "MSE is poorly calibrated for this dataset (DRF < 0.1); WMSE is the
recommended primary metric."

**Biological Metrics (Signal-Focused)**

**Metric 6: DEG-F1**

Formula: F1 = 2 * (precision * recall) / (precision + recall)

where DEGs are identified by Wilcoxon rank-sum test (BH-adjusted p < 0.05, |log2FC| > 0.5)
on both ground-truth and predicted expression profiles, independently.

What it measures: Whether the model correctly identifies which genes are differentially
expressed (up or down) under perturbation.

Why included: Dibaeinia et al. (2026) showed DEG recall is ~9% for most models despite
favorable aggregate metrics. DEG-F1 directly assesses biological signal recovery.

**Metric 7: MMD (Maximum Mean Discrepancy) -- Single-Cell Distributional Metric**

Formula: MMD^2(P, Q) = E[k(x, x')] + E[k(y, y')] - 2*E[k(x, y)]

where k is an RBF kernel (bandwidth = median pairwise distance), x ~ P (predicted),
y ~ Q (ground truth), both at single-cell level.

What it measures: Distance between predicted and ground-truth cell-state distributions
in kernel feature space.

Why included: The only distributional metric in the suite. Required for evaluating
whether models capture population heterogeneity, not just mean effects. Applied to
single-cell predictions only (not pseudobulk). Computationally efficient and robust
under support mismatch, unlike Wasserstein distance (Dibaeinia et al., 2026).

**Metric Disagreement Protocol:**

When metrics disagree on method rankings (which they will):
1. Report all 7 metrics in a single results table
2. Compute rank correlation (Kendall's tau) between all metric pairs
3. Cluster metrics by agreement (hierarchical clustering on rank correlation matrix)
4. Report DRF for each metric; if any primary metric has DRF < 0.1, flag it
5. Present the primary conclusion from calibrated metrics (WMSE, R^2_w(delta))
   with explicit note of what uncalibrated metrics would conclude

#### Component 6: Batch Effect Control Protocol

**Control 1: Negative Control Analysis (DMSO-only Prediction)**

For each method, predict the expression profile of DMSO-treated cells (no perturbation).
The true perturbation effect is zero. Any method that shows non-zero predictions for
DMSO conditions is learning batch effects or systematic bias. Report the DMSO WMSE
for each method. Methods with DMSE WMSE > mean(DMSO WMSE across all methods) + 2*SD
are flagged.

**Control 2: Batch-Shuffled Null**

Randomly permute perturbation labels within batches (plates). Re-run all methods on
shuffled data. If a method achieves comparable performance on shuffled vs real data,
it is learning plate-level rather than perturbation-level signal. Report performance
on shuffled data alongside real data for all methods.

**Control 3: Within-vs-Across-Plate Analysis**

For conditions measured on multiple plates (if applicable), compare prediction error
for same-plate vs cross-plate test instances. If cross-plate error is substantially
higher, plate effects contaminate predictions. Report the ratio: MSE(across-plate) /
MSE(within-plate) for each method.

**Control 4: Cell Line Identity Test**

Provide methods with cell line identity information only (no perturbation information).
Measure how much of the predicted expression is explained by cell line identity alone.
This quantifies the "systematic variation" confound identified by Systema (NatBiotech
2025). Report R^2 of cell-line-only predictions vs actual expression.

#### Component 7: Information Leakage Prevention

Five leakage risks identified, with mitigations:

| Risk | Detection | Mitigation |
|------|-----------|------------|
| **Stereoisomer leakage** | Compute Tanimoto similarity on canonical SMILES (Morgan fingerprints, radius=2, 2048 bits) for all compound pairs | Compounds with Tanimoto > 0.80 assigned to same split partition |
| **Target overlap leakage** | Cross-reference drug_metadata targets field | Compounds sharing >= 1 molecular target assigned to same split partition |
| **Plate batch effects** | ANOVA on DMSO PC1-5 across plates within cell line | Use plate-matched DMSO for delta computation; report plate effect magnitude |
| **Cell line family leakage** | Cluster cell lines by transcriptomic similarity (Pearson on DMSO mean expression) | Organ-based hold-out (Component 2) prevents family leakage. Additionally verify that no held-out cell line has Pearson r > 0.95 with any training cell line on DMSO expression |
| **Pre-training contamination** | Document pre-training data for all methods | Flag contaminated methods (*); report separately; note that decontamination is imperfect |

Implementation: Use DataSAIL (Hummer et al., NatComm 2025) for leakage-reduced splitting
where applicable. DataSAIL's combinatorial optimization formulation handles multi-axis
constraints (compound similarity + target overlap + MOA grouping simultaneously).

### Data Requirements

| Data Source | Size | Format | Access | License |
|------------|------|--------|--------|---------|
| Tahoe-100M | 429 GB | Parquet (HuggingFace streaming) | huggingface.co/datasets/tahoebio/Tahoe-100M | CC0-1.0 |
| Replogle K562 | ~5 GB | AnnData (h5ad) | Figshare (doi:10.6084/m9.figshare.20029387) | Public |
| Replogle RPE1 | ~2 GB | AnnData (h5ad) | Figshare | Public |
| Norman 2019 | ~500 MB | AnnData (h5ad) | Figshare (doi:10.6084/m9.figshare.24688110) | Public |
| Drug metadata | ~1 MB | Part of Tahoe-100M | HuggingFace | CC0-1.0 |
| DepMap CRISPR essentiality | ~200 MB | CSV | depmap.org | CC-BY-4.0 |

Total storage requirement: ~450 GB raw + ~200 GB processed = ~650 GB.

### Compute Requirements

| Component | GPU-Hours | CPU-Hours | GPU Type | Notes |
|-----------|----------|----------|----------|-------|
| Data preprocessing + QC | 0 | 100 | -- | RAPIDS for scale; pre-computed pseudobulk available |
| Split construction + validation | 0 | 50 | -- | DataSAIL optimization |
| Linear baselines (5 x 4 tiers x 5 folds) | 10 | 200 | Any | Parallelizable |
| CPA (retrain per fold) | 100 | 50 | H200/A100 | 5 folds x ~20 GPU-hrs |
| PerturbNet (retrain per fold) | 100 | 50 | H200/A100 | 5 folds x ~20 GPU-hrs |
| scGPT (fine-tune per fold) | 200 | 50 | H200 | 5 folds x ~40 GPU-hrs |
| Scouter (retrain per fold) | 50 | 50 | Any GPU | Lightweight architecture |
| State (fine-tune + evaluate) | 100 | 20 | H200 | Arc Institute model |
| Tahoe-x1 (inference only) | 100 | 20 | H200 | 3B params; inference only |
| LPM (if weights available) | 100 | 20 | H200 | NatCompSci 2025 model |
| Additional 2026 models (as available) | 200 | 50 | H200 | Budget reserve |
| Analysis, metrics, figures | 10 | 100 | Any | Post-hoc computation |
| **Total** | **~1,070** | **~810** | -- | Within 1,000-2,000 GPU-hr budget |

Peak GPU utilization: ~8 H200 GPUs for 1 week (during DL method training in parallel).
Storage: ~650 GB local + ~200 GB for method checkpoints.

### Implementation Timeline (6-Week Sprint)

| Phase | Duration | Deliverable | Dependencies |
|-------|----------|-------------|--------------|
| **Week 1** | Days 1--7 | Data infrastructure: download Tahoe-100M (streaming or full), preprocessing pipeline, QC report, split construction, DMSO control analysis | None |
| **Week 2** | Days 8--14 | All 5 linear baselines implemented and evaluated across all 4 tiers and 5 folds. Metric computation pipeline validated. Baseline result tables. | Week 1 |
| **Week 3** | Days 15--21 | DL methods Wave 1: CPA, PerturbNet, Scouter (parallelized across GPUs). Train, validate, evaluate on all tiers. | Week 1-2 |
| **Week 4** | Days 22--28 | DL methods Wave 2: scGPT, State, Tahoe-x1, LPM (as available). Train/fine-tune, evaluate. Batch effect control experiments. | Week 1-2 |
| **Week 5** | Days 29--35 | Analysis: all metrics computed, DRF calibration, MOA-stratified analysis, metric agreement analysis, normalization sensitivity, gene set sensitivity. Figures and tables. | Weeks 2-4 |
| **Week 6** | Days 36--42 | Writing: main text, methods, supplementary. Internal review. Preprint preparation and posting to bioRxiv. | Week 5 |

**Critical path:** Data preprocessing (Week 1) must complete before any evaluation.
Linear baselines (Week 2) provide calibration anchors for interpreting DL results.
DL methods (Weeks 3--4) are the longest phase but fully parallelizable.

**Buffer:** 1--2 additional weeks for debugging, code release preparation, and
responding to internal review. Target bioRxiv posting: July 15, 2026.

---

## Impact Assessment

### Publication Strategy

**Target venue:** Nature Methods (primary)

**Justification:** scPerturBench was published in Nature Methods (Feb 2026, vol. 23,
pp. 451--464). PerturbMark addresses the specific gaps in scPerturBench (Tahoe-100M,
calibrated metrics, Tier 3, 2026 models) while providing the definitive resolution
to the DL-vs-linear controversy that Nature Methods itself published (Ahlmann-Eltze
et al., 2025). The journal has clear editorial interest in this topic.

**Alternative venue:** Nature Computational Science (if the findings reveal a
surprising computational principle -- e.g., "chemical perturbation prediction follows
power-law scaling with data diversity" or "context embeddings are necessary and
sufficient for cross-context generalization").

**Main claim:** "On the world's largest chemical perturbation dataset (100M cells,
50 cell lines, 379 compounds), using calibrated metrics that avoid documented failure
modes, we provide the definitive resolution of the DL-vs-linear perturbation prediction
controversy: [finding, stratified by difficulty tier]."

**Title options:**
1. "PerturbMark: A Cross-Context Benchmark Resolving the Perturbation Prediction
   Controversy" (primary)
2. "The Answer Depends on the Question: How Difficulty Tier and Metric Calibration
   Resolve the Deep Learning vs. Linear Baseline Debate in Perturbation Prediction"
3. "Beyond scPerturBench: Cross-Context Evaluation of Chemical Perturbation Prediction
   on 100 Million Cells"

**Expected reviewer concerns:**

| Concern | Pre-emptive Response |
|---------|---------------------|
| "How is this different from scPerturBench?" | Table 1 in main text: feature-by-feature comparison showing 10 specific differences (Tahoe-100M, Tier 3, calibrated metrics, 2026 models, CRISPR-informed mean, MOA stratification, leakage controls, batch controls, normalization sensitivity, DRF calibration) |
| "You didn't include AlphaCell / X-Cell / [newest model]" | Methods section explicitly lists which models were available vs unavailable, with dates. Code release monitoring documented. Benchmark designed for extensibility -- new methods can be added via standardized API. |
| "The metric suite is ad hoc" | Each metric justified with specific failure mode evidence from published papers. DRF calibration controls validate metric quality empirically. Both calibrated and uncalibrated metrics reported for transparency. |
| "Tahoe-100M has batch effects you haven't controlled for" | 4 batch effect controls (DMSO prediction, batch-shuffled null, within-vs-across plate, cell line identity test) with pre-registered thresholds. Cell village design provides theoretical protection. |
| "Pre-trained models have an unfair advantage or disadvantage" | Results reported separately for models trained on vs. off Tahoe-100M. Explicit contamination analysis with strict cell-line + compound hold-out. |
| "Gene set choice affects conclusions" | 4 gene sets evaluated (DEGs per condition, union DEGs, HVGs, all genes). Primary metric uses per-condition DEGs; sensitivity analysis across all 4. |

**Comparison baselines for the paper (not the benchmark):**

The paper itself is compared against:
- scPerturBench (NatMeth 2026): Our immediate predecessor; we must clearly surpass it
- Ahlmann-Eltze et al. (NatMeth 2025): The paper that started the controversy
- OP3 (NeurIPS 2024): Smaller-scale chemical perturbation benchmark
- Virtual Cell Challenge (Cell 2025): Competition format, not peer-reviewed benchmark

### Novelty Assessment

**Genuinely novel:**
1. First systematic benchmark on Tahoe-100M (100M cells, 50 cell lines, 379 compounds)
2. First Tier 3 cross-context evaluation for chemical perturbation prediction
3. First application of calibrated metric suite (WMSE, R^2_w(delta), DRF) to a
   large-scale perturbation benchmark
4. First independent evaluation of March 2026 foundation models under standardized
   conditions
5. First MOA-stratified difficulty analysis revealing mechanism-specific model
   strengths/weaknesses
6. First systematic information leakage prevention protocol for perturbation benchmarks

**Engineering of existing methods (not novel, but necessary):**
1. Adaptation of DataSAIL for perturbation benchmark splitting
2. Re-implementation of linear baselines from Ahlmann-Eltze et al.
3. Metric computation from Miller et al. and Camillo et al.

### Broader Impact

PerturbMark establishes the evaluation standard for a rapidly growing field. Its
contributions beyond the specific results:
1. **Calibrated metrics become standard:** Future papers adopt WMSE and R^2_w(delta)
   instead of raw MSE and Pearson-delta
2. **Tier system becomes standard:** Cross-context evaluation becomes expected, not
   optional
3. **Reproducibility resource:** All splits, metrics, and evaluation code released
   publicly, enabling any future method to benchmark against the same standard
4. **Benchmark extensibility:** New methods and datasets can be added without
   re-running the full benchmark, via the standardized evaluation API

---

## Evaluation Plan

### Primary Metrics

The benchmark's own success is evaluated on:
1. **Resolution power:** Do calibrated metrics produce consistent method rankings
   across folds (Kendall's tau > 0.7 between fold-specific rankings)?
2. **Differentiation:** Does Tier 3 produce meaningfully different rankings than
   Tier 0 (Kendall's tau < 0.5 between Tier 0 and Tier 3 rankings)?
3. **Metric calibration:** Do all primary metrics have DRF > 0.1 on Tahoe-100M?
4. **Controversy resolution:** Under calibrated metrics, is there a statistically
   significant winner (WMSE improvement >= 5%, BH-adjusted p < 0.05) at each tier?

### Baselines

The benchmark itself is "baselined" against prior benchmarks:
- scPerturBench: 27 methods, 29 datasets, 6 metrics
- Ahlmann-Eltze et al.: 7 DL methods, 3 datasets, top-1000 genes
- OP3: 146 compounds, PBMCs, NeurIPS track

### Ablation Studies

1. **Normalization ablation:** Library-size + log1p vs Pearson residuals vs raw counts
2. **Gene set ablation:** DEGs per condition vs union DEGs vs HVGs vs all genes
3. **Split method ablation:** Random split vs DataSAIL leakage-reduced split
4. **Tier construction ablation:** Organ-based cell line hold-out vs random cell line hold-out
5. **Metric ablation:** Rankings under calibrated (WMSE, R^2_w(delta)) vs uncalibrated (MSE, Pearson-delta-ctrl)

Each ablation quantifies the impact of a design choice on method rankings. If an
ablation changes the top-ranked method, this is reported as a main finding.

### Validation Strategy

No wet-lab validation required. Computational validation:
1. **Internal consistency:** Same method rankings across 5 folds (ICC > 0.7)
2. **Cross-dataset consistency:** Primary findings replicated on Replogle/Norman supplementary datasets
3. **Metric self-consistency:** DRF > 0.1 for all primary metrics
4. **Known-answer tests:** Verify that Tier 0 performance > Tier 3 performance for all methods
   (monotonic difficulty gradient)
5. **Null model tests:** Batch-shuffled null produces near-zero performance on calibrated
   metrics

---

## Differentiation from scPerturBench (Explicit)

| Feature | scPerturBench (NatMeth 2026) | PerturbMark (This Proposal) |
|---------|---------------------------|---------------------------|
| Primary dataset | 29 datasets from scPerturb (small-scale) | Tahoe-100M (100M cells, 50 cell lines, 379 compounds) |
| Tahoe-100M evaluation | No | Yes (first systematic) |
| Cell lines evaluated | Varies (1--3 per dataset) | 47 usable (from 50 in dataset) |
| Cross-context tiers | 2 scenarios (i.i.d. + o.o.d.) | 4 tiers (Tier 0: interpolation through Tier 3: full transport) |
| Tier 3 (unseen perturbation + unseen context) | No | Yes |
| Methods benchmarked | 27 (through ~late 2025) | 10+ (including March 2026 models: AlphaCell, X-Cell, AetherCell, SCALE, State) |
| Metrics used | 6 (MSE, PCC-delta, E-distance, Wasserstein, KL-div, Common-DEGs) | 7 calibrated (WMSE, R^2_w(delta), DRF, Pearson-delta-centroid, MSE, DEG-F1, MMD) |
| Metrics with known failure modes | 4 of 6 (MSE, E-distance, Wasserstein, KL-div) | 1 of 7 (MSE retained for backward compatibility, reported with DRF warning) |
| Metric calibration controls | No | Yes (DRF + interpolated duplicate for every metric) |
| CRISPR-informed mean baseline | No | Yes (mandatory) |
| Information leakage analysis | No | Yes (5 leakage types with mitigations) |
| Batch effect controls | No | Yes (4 control experiments) |
| MOA-stratified analysis | No | Yes (25 MOA categories) |
| Gene set sensitivity | Not reported | 4 gene sets compared |
| Normalization sensitivity | Not reported | 2 strategies compared |
| Chemical perturbation focus | Mixed (genetic + chemical) | Chemical primary (genetic supplementary) |
| Pre-training contamination tracking | No | Yes (flagged with *) |

**Framing: complementary, not redundant.** scPerturBench provides breadth (27 methods,
29 datasets, genetic + chemical). PerturbMark provides depth (Tahoe-100M's unprecedented
scale + calibrated metrics + Tier 3 cross-context + 2026 models). Together they
comprehensively evaluate the field. The editorial pitch: "scPerturBench showed that
methods struggle with generalization. PerturbMark reveals why, and provides the
calibrated framework to move forward."

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **scPerturBench Tahoe-100M follow-up published before our preprint** | Medium | High | Monitor scPerturBench GitHub and bm2-lab for Tahoe-100M activity weekly. Kill criterion: if Tahoe-100M + Tier 3 paper appears before July 15, 2026, reassess differentiation. Our calibrated metrics + 2026 models + batch controls remain differentiating. |
| **Tahoe-x1/SCALE/AlphaCell teams publish their own benchmark** | Medium | Medium | These are model developers, not neutral benchmarkers. PerturbMark's value is independence and neutrality. Frame as "the independent verification the field needs." |
| **Key DL methods (AlphaCell, AetherCell) don't release code by execution date** | High | Low | Proceed with available methods. Absent methods documented explicitly. Benchmark designed for extensibility -- methods can be added post-publication. |
| **Tahoe-100M preprocessing is more complex than expected** | Medium | Medium | Use pre-computed pseudobulk table (4.09B rows available on HuggingFace). Fall back to RAPIDS-accelerated pipeline (theislab/vevo_Tahoe_100m_analysis). Budget 50% more CPU-hours. |
| **Normalization choice changes conclusions** | Medium | High | This IS a finding. Report both normalization strategies in main text. If method rankings change under different normalizations, this is an important community service finding. |
| **Tier 3 has insufficient statistical power for subgroup analysis** | Medium | Low | Pre-compute power for each MOA category. Report only MOA categories with >= 20 test instances. Aggregate underpowered categories into "other." Main Tier 3 analysis (pooled across MOAs) has adequate power (~950 test instances across 5 folds). |
| **"No surprising finding" -- DL wins under calibrated metrics as expected** | Medium | Medium | Tier 3 cross-context and MOA-stratified results will likely contain surprises. If not, the value is confirmation with unprecedented rigor. Frame as: "We confirm with 100M cells what was suggested by smaller studies, and provide the first quantification of when and by how much." |
| **Compute budget exceeded** | Low | Medium | Core benchmark (5 baselines + 5 DL methods) fits in ~670 GPU-hrs. Additional models are stretch goals. Priority order defined. |
| **Reviewer requests additional methods not available** | High | Low | Pre-emptive: "Code for X was not publicly available as of [date]. PerturbMark is designed for community extension -- any method can be added using our standardized evaluation API." |
| **Data download issues (429 GB)** | Low | Low | Use HuggingFace streaming mode. Alternative: DNAnexus hosted mirror. Arc Virtual Cell Atlas provides AnnData-format alternative. |

---

## Kill Criteria (Pre-Registered)

PerturbMark should be abandoned if ANY of the following conditions are met:

1. **Scoop:** A paper combining Tahoe-100M + Tier 3 cross-context + calibrated metrics
   (WMSE or equivalent) is posted on bioRxiv before our preprint (check weekly,
   kill by July 15, 2026).

2. **Data quality failure:** Tahoe-100M QC reveals >30% of cell-line-drug conditions
   have fewer than 30 cells after filtering, making pseudobulk aggregation unreliable
   for >50% of conditions.

3. **Metric failure:** DRF < 0.05 for WMSE AND R^2_w(delta) on Tahoe-100M, indicating
   these "calibrated" metrics are also unreliable on this specific dataset.

4. **No differentiation from scPerturBench reviewers:** If pre-submission feedback
   from 3 independent computational biologists concludes PerturbMark does not
   sufficiently differentiate from scPerturBench, reassess scope.

---

## Open Questions

1. **Should the benchmark include dose-response evaluation?** Tahoe-100M includes
   dose information. Dose-response prediction is a distinct task from expression
   prediction. Including it adds complexity and a separate set of metrics (IC50
   correlation, dose-response curve fitting). Recommendation: exclude from v1.0;
   reserve for PerturbMark v2.0 or a separate dose-response benchmark.

2. **Should combinatorial perturbation prediction be tested?** Tahoe-100M contains
   single-compound perturbations only. The Norman dataset has combinatorial CRISPRa.
   Including combinatorial prediction would require a separate Tier hierarchy.
   Recommendation: single-compound is the primary focus. Norman combinatorial is
   supplementary.

3. **How to handle the trade-off between comprehensiveness and timeliness?** Adding
   more methods and analyses increases completeness but delays preprint posting. The
   3--6 month competitive window argues for speed. Recommendation: launch with core
   benchmark (5 baselines + 5 DL methods), post preprint, then extend with additional
   methods in v1.1 before journal submission.

4. **What constitutes a "meaningful" DL advantage?** evalstat recommends WMSE reduction
   >= 5%. This threshold is somewhat arbitrary. Recommendation: report effect sizes
   with confidence intervals; pre-register the 5% threshold but also report 1% and 10%
   thresholds for transparency.

5. **Should the benchmark include protein/pathway-level evaluation?** Some perturbation
   effects may be better captured at the pathway level (GSEA enrichment) than the gene
   level. Recommendation: reserve for extension. Gene-level evaluation is standard and
   sufficient for the primary contribution.

---

## Deliverables Summary

| Deliverable | Format | Audience |
|-------------|--------|----------|
| PerturbMark preprint | bioRxiv PDF + LaTeX source | Community |
| Benchmark results tables | CSV + interactive web dashboard | Researchers |
| Tahoe-100M splits (Tier 0--3, 5 folds) | JSON/CSV | Benchmark users |
| Evaluation code | Python package (pip-installable) | Method developers |
| Metric computation library | Python functions with unit tests | Community standard |
| Supplementary benchmark (Replogle/Norman) | Same format as primary | Cross-perturbation-type validation |
| Pre-registration document | OSF or Zenodo | Transparency |

---

## References

1. Zhang S, Gandhi S, et al. "Tahoe-100M: A Giga-Scale Single-Cell Perturbation Atlas
   for Context-Dependent Gene Function and Cellular Modeling." bioRxiv (2025).
   doi:10.1101/2025.02.20.639398

2. Wei Z, Wang Y, Gao Y, et al. "Benchmarking algorithms for generalizable single-cell
   perturbation response prediction." Nature Methods 23: 451--464 (2026).
   doi:10.1038/s41592-025-02980-0

3. Ahlmann-Eltze C, Huber W, Anders S. "Deep-learning-based gene perturbation effect
   prediction does not yet outperform simple linear baselines." Nature Methods (2025).
   doi:10.1038/s41592-025-02772-6

4. Miller HE, Mejia GM, Leblanc FJA, et al. "Deep Learning-Based Genetic Perturbation
   Models Do Outperform Uninformative Baselines on Well-Calibrated Metrics." bioRxiv
   (2025). doi:10.1101/2025.10.20.683304

5. Camillo LP, et al. "Diversity by Design: Addressing Mode Collapse Improves scRNA-seq
   Perturbation Modeling on Well-Calibrated Metrics." arXiv:2506.22641 (2025).

6. Dibaeinia P, et al. "Evaluating Single-Cell Perturbation Response Models Is Far from
   Straightforward." bioRxiv (2026). doi:10.64898/2026.02.14.705879

7. Wong DR, Hill AS, Moccia R. "Simple controls exceed best deep learning algorithms and
   reveal foundation model effectiveness for predicting genetic perturbations."
   Bioinformatics 41(6): btaf317 (2025). doi:10.1093/bioinformatics/btaf317

8. Vinas Torne R, Wiatrak M, Piran Z, et al. "Systema: a framework for evaluating
   genetic perturbation response prediction beyond systematic variation." Nature
   Biotechnology (2025).

9. Miladinovic D, Hoppe P, et al. "In silico biological discovery with large perturbation
   models." Nature Computational Science 5: 1029--1040 (2025).
   doi:10.1038/s43588-025-00870-1

10. AlphaCell Team. "Towards building a World Model to simulate perturbation-induced
    cellular dynamics by AlphaCell." bioRxiv (2026). doi:10.64898/2026.03.02.709176

11. Xaira Therapeutics. "X-Cell: Scaling Causal Perturbation Prediction Across Diverse
    Cellular Contexts via Diffusion Language Models." bioRxiv (2026).
    doi:10.64898/2026.03.18.712807

12. AetherCell Team. "AetherCell: A generative engine for virtual cell perturbation and
    in vivo drug discovery." bioRxiv (2026). doi:10.64898/2026.03.13.710968

13. SCALE Team. "SCALE: Scalable Conditional Atlas-Level Endpoint transport for virtual
    cell perturbation prediction." bioRxiv (2026). doi:10.64898/2026.03.17.712536

14. pertTF Team. "pertTF: context-aware AI modeling for genome-scale and cross-system
    perturbation prediction." bioRxiv (2026). doi:10.64898/2026.03.12.711379

15. Gandhi S, et al. "Tahoe-x1: Scaling Perturbation-Trained Single-Cell Foundation
    Models to 3 Billion Parameters." bioRxiv (2025). doi:10.1101/2025.10.23.683759

16. Arc Institute. "State: Predicting cellular responses to perturbation across diverse
    contexts." bioRxiv (2025). doi:10.1101/2025.06.26.661135

17. Roohani Y, Huang K, Leskovec J. "Predicting transcriptional outcomes of novel
    multigene perturbations with GEARS." Nature Biotechnology 41: 1600--1609 (2023).
    doi:10.1038/s41587-023-01905-6

18. Lotfollahi M, et al. "Predicting cellular responses to complex perturbations in
    high-throughput screens." Molecular Systems Biology 19: e11517 (2023).
    doi:10.15252/msb.202211517

19. PerturbNet Team. "PerturbNet predicts single-cell responses to unseen chemical and
    genetic perturbations." Molecular Systems Biology (2025).
    doi:10.1038/s44320-025-00131-3

20. Zhu Q, Li M. "Scouter predicts transcriptional responses to genetic perturbations
    with large language model embeddings." Nature Computational Science 6: 21--28 (2026).
    doi:10.1038/s43588-025-00912-8

21. Peidli S, et al. "scPerturb: harmonized single-cell perturbation data." Nature
    Methods (2024). doi:10.1038/s41592-023-02144-y

22. Hummer AM, Blumenthal DB, Kalinina OV. "Data splitting to avoid information leakage
    with DataSAIL." Nature Communications 16: 3337 (2025).
    doi:10.1038/s41467-025-58606-8

23. Cole E, Huizing GJ, Addagudi S, et al. "Foundation Models Improve Perturbation
    Response Prediction." bioRxiv (2026). doi:10.64898/2026.02.18.706454

24. Stack Team. "Stack: In-Context Learning of Single-Cell Biology." bioRxiv (2026).
    doi:10.64898/2026.01.09.698608

25. "Virtual Cells Need Context, Not Just Scale." bioRxiv (2026).
    doi:10.64898/2026.02.04.703804

26. Norman TM, Horlbeck MA, Replogle JM, et al. "Exploring genetic interaction manifolds
    constructed from rich single-cell phenotypes." Science 365: 786--793 (2019).
    doi:10.1126/science.aax4438

27. Replogle JM, Saunders RA, Pogson AN, et al. "Mapping information-rich
    genotype-phenotype landscapes with genome-scale Perturb-seq." Cell 185(14):
    2559--2575.e28 (2022). doi:10.1016/j.cell.2022.05.013

28. Virtual Cell Challenge Consortium. "Virtual Cell Challenge: Toward a Turing test for
    the virtual cell." Cell (2025). doi:10.1016/j.cell.2025.06.675

29. Lause J, Berens P, Kobak D. "Analytic Pearson residuals for normalization of
    single-cell RNA-seq UMI data." Genome Biology 22: 258 (2021).
    doi:10.1186/s13059-021-02451-7

30. Open Problems in Single-Cell Analysis. "OP3: A benchmark for prediction of
    transcriptomic responses to chemical perturbations across cell types." NeurIPS 2024
    Datasets and Benchmarks Track.

31. XPert Team. "Modelling drug-induced cellular perturbation responses with a
    biologically informed dual-branch transformer." Nature Machine Intelligence (2026).
    doi:10.1038/s42256-025-01165-w

32. CZI. "rBio1: training scientific reasoning LLMs with biological world models as
    soft verifiers." bioRxiv (2025). doi:10.1101/2025.08.18.670981
