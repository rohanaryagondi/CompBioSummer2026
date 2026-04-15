---
agent: Evaluation Methodology & Statistical Rigor Expert (evalstat)
round: 1
date: 2026-04-14
type: research-note
topic: Cross-project evaluation frameworks for Alpha-M, Gamma, and Delta
---

# Research Note: Cross-Project Evaluation Frameworks for Alpha-M, Gamma, and Delta

## Agent
Dr. Evaluation Methodology & Statistical Rigor Expert (evalstat) -- Senior biostatistician
specializing in experimental design, benchmark methodology, and statistical model comparison.
20+ years in evaluation frameworks for computational biology.

---

## Summary

This research note defines pre-registerable evaluation frameworks for all three Cohort2
projects: Alpha-M (MLFF Benchmark), Gamma (Dynamics-to-Function), and Delta (PerturbMark).
Each framework specifies the exact statistical tests, aggregation strategies, power
requirements, multiple-testing corrections, and reporting standards needed to produce
claims defensible at Nature Computational Science or Nature Methods. Key findings include:
(1) Alpha-M requires a multi-level Friedman/Nemenyi framework with chi-squared integration
across observables, with 15 proteins providing ~80% power only for large effects;
(2) Gamma faces severe overfitting risk with 20 features on 217 assays and must use
nested leave-protein-out CV with strict regularization; (3) Delta's metric controversy
is resolvable through Dynamic Range Fraction calibration, requiring separate per-tier
significance testing with Benjamini-Hochberg correction; (4) all three projects should
pre-register their evaluation protocols on OSF or a comparable platform before analysis begins.

---

## Research Questions

1. What is the correct statistical framework for comparing N MLFFs across M experimental
   observables and P proteins, and is 15 proteins sufficient for statistical power?
2. How should the Gamma project handle leave-protein-out CV with 217 assays and prevent
   overfitting when extracting ensemble features?
3. How should the Delta project resolve the DL-vs-linear controversy given that
   conventional metrics (MSE, Pearson-delta) are poorly calibrated?
4. What cross-cutting best practices ensure all three projects meet Nature-level
   statistical reporting standards?

---

## Methods and Sources

### Databases Searched
- PubMed, Google Scholar, arXiv, bioRxiv, Semantic Scholar
- Nature Methods and Nature Computational Science article archives (2024-2026)
- ProteinGym documentation and GitHub repository
- BMRB (Biological Magnetic Resonance Bank)
- scPerturBench documentation and GitHub repository

### Key Journals / Preprint Servers
- Nature Methods (2024-2026): benchmark methodology, perturbation prediction controversy
- Nature Computational Science (2024-2026): benchmark paper statistical practices
- Journal of Machine Learning Research: Demsar (2006) on classifier comparison
- Genome Biology: Weber et al. (2019) benchmarking guidelines
- WIREs Data Mining: Niessl et al. (2022) over-optimism in benchmarks
- Journal of Biomolecular NMR: SPARTA+ validation, S2 order parameter methodology

### Search Queries
- "benchmark design computational biology statistical methodology 2024 2025 2026"
- "Demsar 2006 critical difference diagrams comparing multiple classifiers"
- "power analysis leave-one-out cross-validation sample size protein benchmark"
- "metric calibration perturbation prediction well-calibrated metrics"
- "statistical comparison force fields molecular dynamics NMR SAXS observables"
- "ProteinGym evaluation methodology leave-protein-out cross-validation"
- "Bayesian model comparison benchmark studies computational biology"
- "pre-registration evaluation protocol computational biology benchmark"
- "batch effect correction single cell perturbation prediction confounding"
- "SHAP permutation importance feature importance comparison reliability"

---

## Findings

### Finding 1: Alpha-M Evaluation Framework -- Multi-Level MLFF Comparison

#### 1.1 The Statistical Design Problem

Alpha-M compares K = 6 MLFFs (MACE-OFF23, SO3LR, AI2BMD, ANI-2x, LiTEN-FF, plus
2 classical baselines: AMBER ff19SB, CHARMM36m) across P = 15 proteins on M = 4
observable types (S2 order parameters, chemical shifts, J-couplings, SAXS profiles).
This is a multi-factor, multi-level comparison problem that requires careful statistical
design at three hierarchical levels.

**Level 1: Per-residue comparison.** For each protein-MLFF pair, compute a per-residue
agreement metric between simulated and experimental observables. For S2 order parameters,
this yields one R^2 and one RMSE value per protein-MLFF pair. For chemical shifts, this
yields nucleus-specific RMSE values (13Ca, 13Cb, 13C', 15N, 1Ha, 1HN).

**Level 2: Per-protein comparison.** Aggregate per-residue metrics into a single score
per protein-MLFF pair. This is the unit of analysis for statistical testing.

**Level 3: Global comparison.** Compare MLFFs across all proteins using rank-based
non-parametric tests.

#### 1.2 The Demsar Framework for MLFF Ranking

The gold standard for comparing K algorithms across N datasets is the Demsar (2006)
framework, which proceeds as follows:

**Step 1: Friedman test.** Test the null hypothesis that all K methods have equal
average ranks across N datasets (proteins). The Friedman statistic is:

    chi^2_F = (12N / (K(K+1))) * [sum_j(R_j^2) - K(K+1)^2 / 4]

where R_j is the average rank of method j across all N datasets. The Friedman test
is a non-parametric analog of repeated-measures ANOVA, appropriate when the normality
assumption is questionable (as it typically is with benchmark scores).

Demsar (2006) recommends the Iman-Davenport correction, which adjusts the Friedman
statistic to an F-distribution:

    F_F = ((N-1) * chi^2_F) / (N*(K-1) - chi^2_F)

distributed as F(K-1, (K-1)(N-1)) under the null (Demsar, 2006, JMLR 7:1-30).

**Step 2: Post-hoc Nemenyi test.** If the Friedman test rejects the null, apply the
Nemenyi test to identify which pairs of methods differ significantly. Two methods differ
significantly if their average ranks differ by at least the critical difference:

    CD = q_alpha * sqrt(K(K+1) / (6N))

where q_alpha is the critical value from the Studentized range distribution divided
by sqrt(2). At alpha = 0.05 with K = 8 methods, q_0.05 = 3.031.

**Step 3: Critical difference diagram.** Visualize results as a critical difference
diagram with methods plotted on a horizontal axis by average rank, and connected by
a thick line if they are NOT significantly different by the Nemenyi test.

**Application to Alpha-M:** With K = 8 (6 MLFFs + 2 classical FFs) and N = 15 proteins:

    CD = 3.031 * sqrt(8 * 9 / (6 * 15)) = 3.031 * sqrt(0.80) = 3.031 * 2.83 = 2.71

This means two methods must differ by at least 2.71 average rank positions (out of 8)
to be significantly different. This is a large critical difference, indicating that 15
proteins may provide limited resolving power for closely-ranked methods.

#### 1.3 Power Analysis: Is 15 Proteins Enough?

The power of the Friedman test depends on: (a) the number of methods K, (b) the number
of datasets N, (c) the effect size (how different the methods actually are in rank), and
(d) the significance level alpha.

**Effect size metric:** Kendall's W (coefficient of concordance) measures the degree of
agreement in rankings across datasets:

    W = chi^2_F / (N * (K - 1))

W ranges from 0 (no agreement) to 1 (perfect agreement). In benchmark studies, W values
of 0.3-0.5 are common (moderate effect), and W > 0.7 indicates strong method differentiation.

**Power estimation for N = 15, K = 8:**

Using the approximation that the Friedman test power is:

    Power approx Pr(chi^2(K-1, lambda) > chi^2_{alpha,K-1})

where lambda = N * K * (K-1) * W is the non-centrality parameter:

- For W = 0.3 (moderate effect): lambda = 15 * 8 * 7 * 0.3 = 252, power > 0.99
- For W = 0.1 (small effect): lambda = 15 * 8 * 7 * 0.1 = 84, power > 0.99

The Friedman test itself has excellent power with 15 proteins. The bottleneck is the
Nemenyi post-hoc test, which requires larger rank differences to declare significance.

**Post-hoc power analysis:** With CD = 2.71 out of 8 ranks, we can detect:
- Methods ranked 1st vs. 4th or worse: YES (rank difference >= 3)
- Methods ranked 1st vs. 3rd: MARGINAL (rank difference of 2 < 2.71)
- Methods ranked 1st vs. 2nd: NO

**Recommendation:** 15 proteins provide sufficient power to identify clearly superior
or inferior methods, but NOT to distinguish closely-ranked methods. This is acceptable
for the Alpha-M paper's primary claim ("Which MLFFs produce realistic dynamics?") but
limits fine-grained ranking. Increasing to 20 proteins would reduce CD to 2.35, a
meaningful improvement. The mlffeng and bioval agents should attempt to identify 20
suitable proteins if feasible.

**Sensitivity analysis mandate:** Report power analysis in the paper's Methods section.
State explicitly: "With N = 15 proteins and K = 8 force fields, the Nemenyi post-hoc
test at alpha = 0.05 has a critical difference of CD = 2.71 average ranks. This design
is powered to detect large differences (methods ranked in the top vs. bottom third) but
not to resolve adjacent rankings."

#### 1.4 Multi-Observable Integration

Alpha-M compares MLFFs on four observable types: S2 order parameters, chemical shifts
(6 nucleus types), J-couplings, and SAXS profiles. The question is whether to produce
separate rankings per observable or an integrated ranking.

**Option A: Separate rankings per observable (RECOMMENDED AS PRIMARY).**
Run independent Friedman/Nemenyi analyses for each observable type. This is the most
transparent approach and avoids the problem of choosing relative weights across observables.
It directly answers: "Which MLFF best reproduces S2 values? Which best reproduces
chemical shifts?" etc.

**Option B: Integrated chi-squared score (RECOMMENDED AS SECONDARY).**
Following Lindorff-Larsen et al. (2012, PLOS ONE 7:e32131) and the methodology
described in Nerenberg & Head-Gordon (2018, Curr. Opin. Struct. Biol. 49:129-138), compute
a reduced chi-squared statistic integrating all observables:

    chi^2_red = (1/N_obs) * sum_i [ (O_sim,i - O_exp,i)^2 / sigma_i^2 ]

where sigma_i is the back-calculation error for observable type i. Known error values:

| Observable | Back-calculation tool | sigma (error) | Source |
|-----------|---------------------|---------------|--------|
| 13Ca shift | SPARTA+ | 1.09 ppm | Shen & Bax, 2010, J Biomol NMR |
| 13Cb shift | SPARTA+ | 1.14 ppm | Shen & Bax, 2010 |
| 13C' shift | SPARTA+ | 1.09 ppm | Shen & Bax, 2010 |
| 15N shift | SPARTA+ | 2.45 ppm | Shen & Bax, 2010 |
| 1Ha shift | SPARTA+ | 0.25 ppm | Shen & Bax, 2010 |
| 1HN shift | SPARTA+ | 0.49 ppm | Shen & Bax, 2010 |
| S2 order param | iRED/Direct | ~0.10 | Trbovic et al., 2008, Proteins |
| 3J-HNHa | Karplus eq. | ~0.78 Hz | Vuister & Bax, 1993 |
| SAXS I(q) | CRYSOL/FoXS | ~5-10% | Svergun et al., 1995 |

The chi-squared integration normalizes different observable types to a common scale
using their known prediction uncertainties. This yields a single aggregate score per
protein-MLFF pair that can then be subjected to the Friedman/Nemenyi analysis.

**Critical consideration: back-calculation uncertainty propagation.** SPARTA+ chemical
shift predictions have intrinsic errors of 1.09-2.45 ppm. Any MLFF whose shift
prediction error is within this range cannot be statistically distinguished from a
perfect simulation -- the back-calculation noise dominates. This means:

- RMSE(sim vs. exp) = sqrt(RMSE(FF)^2 + RMSE(backcalc)^2) approximately
- Two MLFFs can only be distinguished if their RMSE difference exceeds
  sqrt(2) * sigma_backcalc / sqrt(n_residues) for paired comparisons

For 13Ca shifts with sigma = 1.09 ppm and n = 100 residues: the minimum detectable
RMSE difference is approximately 1.09 * sqrt(2) / sqrt(100) = 0.154 ppm. This is
achievable for the best vs. worst force fields (AMBER ff19SB 13Ca RMSE ~1.0 ppm vs.
poor MLFFs at ~2+ ppm) but challenging for closely performing methods.

**Recommendation:** Present both separate-observable and integrated analyses. Use
separate-observable rankings as the primary result (more interpretable, avoids weighting
arbitrariness) and chi-squared-integrated ranking as a secondary, aggregate summary.
Report back-calculation errors prominently and use them in significance testing.

#### 1.5 Classical FF Baselines

**Minimum baselines (mandatory):**
- AMBER ff19SB (most widely used; S2 R^2 = 0.62 as reported in Cohort 1)
- CHARMM36m (strong competitor; S2 R^2 = 0.51)

**Recommended additional baselines:**
- OPLS-AA/M (alternative paradigm, popular in drug discovery)
- ff14SB (older AMBER version, to show historical progress)

Including 2-4 classical FFs is critical: if ALL MLFFs fail to beat classical baselines,
that IS the paper's main finding (analogous to the Ahlmann-Eltze result for perturbation
prediction). At minimum, 2 classical FFs must be included. These serve as the "linear
baseline" equivalent for this domain.

#### 1.6 Simulation Convergence and Reproducibility

**Statistical requirement:** Each MLFF-protein simulation must include multiple independent
replicates (minimum 3, ideally 5) to assess convergence and reproducibility. Report:
- Per-replica variance in each observable
- Inter-replica agreement (intra-class correlation coefficient, ICC)
- Block-averaging analysis to demonstrate convergence of S2 parameters

Per Trbovic et al. (2008, Proteins 71:684-694), S2 order parameters require simulation
lengths of at least 5x the overall tumbling correlation time. For a 15 kDa protein with
tau_c ~ 8 ns, this means at least 40 ns of production simulation. The planned 50 ns
should be sufficient but marginal for larger proteins.

**Reporting requirement:** Include ICC values in supplementary tables. Any protein-MLFF
pair with ICC < 0.7 for S2 should be flagged and possibly excluded from ranking analysis
(with sensitivity analysis showing results with and without exclusion).

---

### Finding 2: Gamma Evaluation Framework -- Ensemble-to-Function Prediction

#### 2.1 Cross-Validation Strategy

The Gamma project trains ML models to predict ProteinGym DMS fitness scores from BioEmu
ensemble features. The cross-validation strategy is the single most important design
decision for credibility.

**MANDATORY: Leave-protein-out cross-validation (LPOCV).**

In LPOCV, all variants of a given protein are held out as the test set, and the model
is trained on variants from all other proteins. This is the only valid strategy because:

1. Within-protein variants share massive confounders (protein structure, function type,
   evolutionary history, assay technology, lab effects)
2. Leave-variant-out CV within a protein would dramatically overestimate generalization
   by exploiting these shared confounders
3. The claim "ensemble features predict function" must generalize to NEW proteins, not
   just unseen variants of training proteins

ProteinGym already aggregates results by UniProt ID to avoid biasing toward proteins
with multiple assays (Notin et al., 2024, NeurIPS). Our LPOCV must respect this:
aggregate at the UniProt level, not the assay level.

**Implementation:** With ~217 assays across ~187 unique UniProt IDs (some proteins have
multiple assays), LPOCV produces 187 folds. For each fold:
1. Hold out all assays for one UniProt ID
2. Train on all assays from the remaining 186 UniProt IDs
3. Predict fitness for all variants of the held-out protein
4. Compute per-protein Spearman correlation between predicted and experimental fitness

The per-protein Spearman rho values are the primary unit of analysis.

#### 2.2 Statistical Significance Testing

**Primary test:** Wilcoxon signed-rank test comparing per-protein Spearman rho values
between the ensemble-based method and each baseline. This is a paired test: for each
protein, both the ensemble method and the baseline produce a Spearman rho, yielding
paired observations across 187 proteins.

**Why Wilcoxon, not paired t-test:** Spearman rho values are bounded [-1, 1] and
typically non-normally distributed (often left-skewed with many high values). The
Wilcoxon signed-rank test makes no distributional assumptions.

**Effect size:** Report the matched-pairs rank-biserial correlation (r_rb) as the
effect size for the Wilcoxon test:

    r_rb = (n_positive - n_negative) / n_total

where n_positive is the number of proteins where the ensemble method outperforms the
baseline, and n_negative is the reverse. Also report the median improvement in Spearman
rho and its 95% bootstrap confidence interval (BCa method, 10,000 bootstrap samples).

**Multiple comparisons:** If comparing against B baselines (EVE, ESM-1v, AlphaMissense,
etc.), apply Benjamini-Hochberg FDR correction at q = 0.05 across all B comparisons.
Report both uncorrected and FDR-corrected p-values.

#### 2.3 Power Analysis for LPOCV with 187 Proteins

**Question:** Is 187 proteins sufficient to detect a meaningful improvement over baselines?

**Scenario:** Current SOTA Spearman rho on ProteinGym is approximately 0.47-0.52 across
all proteins. Suppose the ensemble method achieves a median Spearman rho of 0.55 (an
improvement of delta = 0.05). Under what conditions is this detectable?

**Wilcoxon signed-rank test power analysis:**

Using the asymptotic efficiency of the Wilcoxon test relative to the t-test (ARE = 3/pi
= 0.955 for normal distributions, higher for heavy-tailed distributions):

For a paired design with N = 187 proteins, standardized effect size d = delta / sigma_diff:
- If sigma_diff (SD of per-protein rho differences) = 0.15 (conservative), then d = 0.05/0.15 = 0.33
- Power for N = 187, d = 0.33, alpha = 0.05: > 0.95 (well-powered)
- If sigma_diff = 0.25 (very conservative), then d = 0.05/0.25 = 0.20
- Power for N = 187, d = 0.20, alpha = 0.05: approximately 0.70-0.75

**Conclusion:** 187 proteins provide good power (>80%) to detect improvements of delta >= 0.05
in median Spearman rho, assuming sigma_diff <= 0.20. If the true effect is smaller
(delta = 0.02-0.03), power drops below 50%. This means: if ensemble features add only
a marginal signal, we may not detect it. This is fine -- marginal signals are not worth
publishing at Nature Comp Sci anyway.

**Minimum clinically significant effect:** Define a priori that an improvement of
delta >= 0.03 in median Spearman rho across proteins is the minimum effect worth reporting.
Below this threshold, the ensemble approach does not meaningfully advance the field,
regardless of statistical significance.

#### 2.4 Stratification by Assay Type

ProteinGym assays span diverse functional readouts: thermostability (30%), binding (25%),
catalytic activity (15%), growth/fitness (15%), fluorescence (10%), other (5%). The
ensemble-based method may help more for some assay types than others.

**Pre-specified stratification (MANDATORY):**

| Stratum | Expected proteins | Hypothesis |
|---------|-------------------|-----------|
| Thermostability | ~55 | Dynamics should strongly predict stability |
| Binding/interaction | ~47 | Conformational flexibility affects binding affinity |
| Catalytic activity | ~28 | Active site dynamics are rate-relevant |
| Growth/fitness | ~28 | Indirect; may show weaker ensemble signal |
| Fluorescence | ~19 | Structure-dependent; moderate signal expected |
| Other | ~10 | Exploratory |

**Statistical approach per stratum:**
- Report per-stratum median Spearman rho and 95% bootstrap CI for each method
- Within each stratum, perform Wilcoxon signed-rank test (ensemble vs. best baseline)
- Apply Benjamini-Hochberg correction across strata (6 tests) and across baselines
- Report the fraction of proteins in each stratum where ensemble method wins (> 50%
  is the minimum for a credible claim)

**What fraction of proteins must improve?** At minimum, the ensemble method must
outperform the best baseline on >55% of proteins (majority rule). Ideally, >65%. If
the ensemble method wins on only 52% of proteins, even with a significant Wilcoxon test,
the practical value is questionable. Report the exact win/draw/loss counts per stratum.

#### 2.5 Overfitting Prevention with 20 Features on 217 Assays

**The core risk:** If the Gamma project extracts F = 20 ensemble features per protein
(RMSF profile statistics, contact map metrics, pocket volumes, hinge motion amplitudes,
principal component variances, etc.) and trains an ML model on N = 187 unique proteins,
the ratio N/F = 187/20 = 9.35. This is dangerously low for non-regularized models.

**Rule of thumb (Harrell, 2015):** For regression problems, the number of effective
observations should be at least 10-20 per predictor. With 187 proteins and 20 features,
we are at the lower boundary.

**Mandatory safeguards:**

1. **Nested cross-validation.** The LPOCV described above is the outer loop. Any
   hyperparameter tuning (regularization strength, feature selection) MUST use an inner
   CV loop within the training set. Never tune on outer-fold test performance.

2. **Strong regularization.** Use L1 (Lasso) or elastic net regularization as the
   default. L1 will perform implicit feature selection, reducing effective dimensionality.
   Report the regularization path and the number of non-zero features at the optimal lambda.

3. **Permutation test for overall model significance.** After computing LPOCV Spearman
   rho, perform a permutation test (n = 1,000 permutations) where protein fitness labels
   are shuffled across proteins. The p-value is the fraction of permutations yielding
   Spearman rho >= observed. This guards against the model finding spurious structure.

4. **Pre-specified feature groups for ablation.** Define feature groups BEFORE analysis:
   - Group A: Flexibility features (RMSF, B-factors, S2)
   - Group B: Contact/interaction features (contact maps, salt bridges, H-bonds)
   - Group C: Pocket/cavity features (volume, druggability scores)
   - Group D: Global dynamics features (PCA eigenvalues, collectivity indices)
   - Group E: Mutation-specific features (delta-RMSF, delta-contacts for variant vs. WT)
   
   Perform ablation by removing one group at a time. This is more informative than
   individual feature importance and less susceptible to multicollinearity artifacts.

5. **Comparison against shuffled features.** Generate a null model by shuffling ensemble
   features across proteins (keeping feature values but breaking the protein-label
   correspondence). The ensemble model must significantly outperform this null.

#### 2.6 Compute-Matched Comparison

**The fairness problem:** BioEmu ensemble generation requires ~8,200 GPU-hours for all
proteins. Sequence-only baselines (EVE, ESM-1v, AlphaMissense) require minutes.
How to report this comparison fairly?

**Recommendation:** Include a "compute budget" column in all comparison tables:

| Method | Median Spearman rho | Compute (GPU-hrs) | Improvement per 1000 GPU-hrs |
|--------|--------------------|--------------------|------------------------------|
| EVE | 0.47 | <1 | baseline |
| ESM-1v | 0.49 | <1 | baseline |
| AlphaMissense | 0.52 | <1 | baseline |
| Ensemble (ours) | 0.57* | 8,200 | +0.006 |

*hypothetical

Frame the compute cost honestly: "The ensemble approach provides a delta = +0.05
improvement in median Spearman rho at a cost of 8,200 GPU-hours. This is justified when
per-protein accuracy matters (e.g., drug target prioritization) but may not be
cost-effective for genome-wide screening."

#### 2.7 Feature Importance: Which Method?

**Recommendation: Use all three, report agreement and disagreement.**

| Method | What it measures | Strengths | Weaknesses |
|--------|-----------------|-----------|-----------|
| Permutation importance | Model-agnostic; measures predictive relevance | Robust, interpretable | Biased by correlated features |
| SHAP (TreeSHAP for GBT) | Per-prediction feature contributions | Local + global; theoretically grounded | Computationally expensive; diverges from PFI |
| Group ablation | Contribution of feature groups | Handles multicollinearity | Coarse-grained |

Recent literature (2024-2025) shows that PFI and SHAP can produce dramatically different
feature rankings, especially with correlated features (as ensemble features likely are).
The safest approach:

1. Report SHAP summary plots (global feature importance + per-protein variability)
2. Report PFI with 95% CI from repeated permutations
3. Report group ablation results
4. **Highlight any discrepancies** between methods and discuss why they arise

If SHAP says "RMSF is most important" but PFI says "pocket volume is most important,"
this is an important finding, not a failure. Report it transparently and investigate
the correlation structure.

---

### Finding 3: Delta Evaluation Framework -- Resolving the Perturbation Prediction Crisis

#### 3.1 The Metric Controversy: Diagnosis and Resolution

The DL-vs-linear controversy in perturbation prediction is fundamentally a metric
calibration problem. The key papers are:

- **Ahlmann-Eltze & Huber (2025, Nature Methods):** "Deep-learning-based gene
  perturbation effect prediction does not yet outperform simple linear baselines."
  Conclusion: DL fails. Metrics used: MSE, Pearson correlation on delta from control.

- **Rebuttal (2025, bioRxiv):** "Deep Learning-Based Genetic Perturbation Models
  Do Outperform Uninformative Baselines on Well-Calibrated Metrics." Conclusion: DL
  wins when metrics are calibrated. Key insight: conventional MSE and Pearson(delta_ctrl)
  are poorly calibrated and reward mode collapse.

- **"Diversity by Design" (2025, arXiv):** Introduces Dynamic Range Fraction (DRF)
  as a calibration measure, plus DEG-score-weighted metrics. Shows mode collapse is
  the real failure mode, not DL architecture.

**What "calibration" means for a metric:**

A metric M is well-calibrated if:
1. M(perfect_prediction) >> M(mean_baseline) -- it can distinguish real predictions from trivial ones
2. M improves monotonically with better predictions along a controlled interpolation
3. M assigns the worst score to predictions that ignore perturbation-specific effects

The Dynamic Range Fraction (DRF) quantifies calibration:

    DRF = [M(model) - M(null_baseline)] / [M(positive_control) - M(null_baseline)]

where the null baseline is "predict the mean of all perturbations" and the positive
control is "predict using a technical replicate" (interpolated duplicate).

#### 3.2 Recommended Metric Suite

Based on the calibration analysis, I recommend the following metric suite for Delta:

**Tier 1 metrics (PRIMARY -- well-calibrated):**

| Metric | Formula | Why it's calibrated |
|--------|---------|-------------------|
| WMSE (weighted MSE) | sum_i w_i * (mu_pred,i - mu_obs,i)^2 | Weights by DEG score; ignores housekeeping gene noise |
| R^2_w(delta) | 1 - [sum w_i(delta_i - delta_hat_i)^2] / [sum w_i(delta_i - delta_bar_w)^2] | Reference is global mean, not control; constant predictions score negative |
| Rank correlation on top-k DEGs | Spearman rho on top 50/100/200 DEGs per perturbation | Focuses on biologically meaningful genes |

**Tier 2 metrics (SECONDARY -- include for completeness, note calibration issues):**

| Metric | Known issue |
|--------|-------------|
| MSE (unweighted) | Signal dilution; dominated by housekeeping genes |
| Pearson(delta_ctrl) | Inflated by control cell bias; rewards mode collapse |
| Pearson(raw) | Dominated by baseline expression; nearly all methods score >0.95 |

**Tier 3 metrics (EXPLORATORY):**

| Metric | Purpose |
|--------|---------|
| Direction accuracy (DEG sign) | Binary: does the model get the direction right? |
| Gene set enrichment overlap | Pathway-level prediction accuracy |
| Distribution divergence (Wasserstein) | Full distributional comparison, not just means |

**Critical design element: the interpolated duplicate baseline.** For each perturbation-
context pair with sufficient cells, randomly split cells into two halves. Use one half
as the "prediction" and compare to the other half as "ground truth." This provides an
empirical ceiling for each metric -- no method can outperform the biological replicate
agreement. Report all metric values as a fraction of this ceiling.

#### 3.3 Statistical Testing: DL vs. Linear

**Question:** Does DL significantly outperform linear baselines?

**Design:** This is a paired comparison across perturbation-context pairs. For each
pair, both the DL method and the linear baseline produce a metric score (e.g., WMSE).
The pair (DL_score_i, linear_score_i) is the unit of analysis.

**Test:** Wilcoxon signed-rank test for each metric, comparing DL vs. linear baseline
per perturbation-context pair.

**Effect size:** Report Cohen's d (or its non-parametric equivalent, Cliff's delta) and
the median improvement with 95% bootstrap BCa confidence interval.

**Clinically meaningful effect size:** Define a priori: DL is considered "better" if
it reduces WMSE by >= 5% relative to the linear baseline. Below this threshold, the
added model complexity is not justified.

**What if the conclusion depends on the metric?** This is the EXPECTED scenario based
on prior literature. The paper should:
1. Report results for all metrics (Tier 1, 2, 3)
2. Highlight where conclusions change across metrics
3. Use DRF calibration analysis to argue which metrics are trustworthy
4. Make the primary conclusion based on Tier 1 (calibrated) metrics only

If DL wins on Tier 1 metrics but loses on Tier 2, the conclusion is: "DL genuinely
outperforms linear baselines when evaluated with calibrated metrics. Previous negative
findings were artifacts of uncalibrated evaluation."

If DL loses on ALL metrics including Tier 1, the conclusion is: "DL does not yet
outperform linear baselines for perturbation prediction, even under favorable
evaluation. The linear baseline is surprisingly strong."

Both conclusions are publishable. The key is that the evaluation framework is defensible
regardless of the outcome.

#### 3.4 Per-Tier Analysis: Cross-Context Difficulty

The Delta project defines four cross-context difficulty tiers:

| Tier | Description | Example | Expected n pairs |
|------|-------------|---------|-----------------|
| 0 | Same cell type, same compound | Held-out cells from same condition | ~5,000+ |
| 1 | Same cell type, new compound | Train on compound A, predict compound B in same cells | ~2,000 |
| 2 | New cell type, same compound | Train in HeLa, predict in MCF7 for same compound | ~500 |
| 3 | New cell type, new compound | Full cross-context: unseen compound in unseen cells | ~200 |

**Independent significance testing per tier:** Run separate Wilcoxon tests per tier.
The biological question is different at each tier -- Tier 0 is interpolation, Tier 3
is extrapolation. A method may excel at Tier 0 but fail at Tier 3.

**Power analysis per tier:**

For the Wilcoxon signed-rank test at alpha = 0.05 (two-sided), effect size d:
- Tier 0 (n = 5,000): detects d >= 0.04 at 80% power
- Tier 1 (n = 2,000): detects d >= 0.06 at 80% power
- Tier 2 (n = 500): detects d >= 0.13 at 80% power
- Tier 3 (n = 200): detects d >= 0.20 at 80% power

Tier 3 has limited power and will only detect large effects. This is acceptable: if DL
only marginally outperforms linear baselines in the most challenging tier, that is not
a compelling case for DL.

**Multiple testing correction:** Apply Benjamini-Hochberg FDR correction across all
tier x method x metric combinations. With 4 tiers x 10 methods x 6 metrics = 240 tests,
uncorrected p-values will produce many false positives. BH-FDR at q = 0.05 is appropriate.

Total number of hypothesis tests:
- 10 methods vs. linear baseline
- 4 tiers
- 3 primary metrics (Tier 1)
- = 120 primary tests
- BH correction at q = 0.05

#### 3.5 Batch Effect Controls

Tahoe-100M uses a "cell village" design where multiple cell lines are profiled
simultaneously, which reduces batch effects relative to traditional plate-based designs
(Tahoe-100M preprint, bioRxiv 2025). However, residual batch effects may still confound
cross-context predictions.

**Mandatory batch effect controls:**

1. **Negative control:** Include a "predict from batch label only" baseline. If a model's
   cross-context predictions are explained entirely by batch identity, it is memorizing
   batch effects, not learning biology. Train a simple model (logistic regression) to
   predict perturbation response from batch indicators alone. This sets a floor.

2. **Batch-shuffled null model:** For each cross-context prediction, shuffle batch labels
   and re-predict. If performance does not degrade, the model is not relying on batch
   structure.

3. **Within-batch vs. across-batch performance:** Report method performance separately
   for test pairs from the same batch vs. different batches. If performance drops sharply
   across batches, this indicates batch confounding.

4. **Principal component analysis on residuals:** After prediction, examine PCs of
   residual errors. If residual PCs correlate with batch identity, the model has not
   fully captured the biological signal and is partially confounded.

---

### Finding 4: Cross-Cutting Best Practices

#### 4.1 Pre-Registration Protocol

All three projects should pre-register their evaluation protocols before beginning
analysis. Pre-registration locks the following decisions:

**What to pre-register:**

| Decision | Alpha-M | Gamma | Delta |
|----------|---------|-------|-------|
| Primary metric(s) | S2 R^2, chi-squared | Spearman rho (LPOCV) | WMSE, R^2_w(delta) |
| Statistical test | Friedman + Nemenyi | Wilcoxon signed-rank | Wilcoxon signed-rank |
| Significance threshold | alpha = 0.05 | alpha = 0.05, FDR q = 0.05 | alpha = 0.05, FDR q = 0.05 |
| Sample sizes | 15 proteins, 8 FFs | 187 proteins, B baselines | 4 tiers, ~7,700 pairs |
| Effect size threshold | CD = 2.71 ranks | delta Spearman >= 0.03 | delta WMSE >= 5% |
| Multiple testing | Nemenyi (built-in) | BH-FDR across baselines | BH-FDR across tiers/methods |
| Stratification | Per-observable type | Per-assay type | Per-tier |
| CV strategy | N/A (benchmark) | LPOCV | Train/test by context tier |
| Feature set | N/A | 20 features, 5 groups | N/A |
| Baselines | AMBER ff19SB, CHARMM36m | EVE, ESM-1v, AlphaMissense | Mean, linear, PCA baselines |

**Where to pre-register:** OSF Registries (https://osf.io/registries/) or aspredicted.org.
Both are free, timestamped, and DOI-citable.

**What NOT to pre-register:** Exploratory analyses, visualization choices, narrative
framing. These are legitimately flexible and should not be locked.

#### 4.2 Reporting Standards: What Every Figure and Table Must Include

Following Weber et al. (2019, Genome Biology), Nature Methods guidelines, and the
Niessl et al. (2022, WIREs) recommendations on over-optimism prevention:

**Every performance comparison figure must show:**

1. **Individual data points, not just summaries.** Do not show only bar charts with
   error bars. Show per-protein/per-pair scatter plots, violin plots, or beeswarm plots.
   The distribution matters as much as the mean.

2. **Confidence intervals.** 95% bootstrap BCa CIs on all summary statistics (means,
   medians, rank correlations). CI width is as informative as the point estimate.

3. **Effect sizes with CIs.** Not just p-values. Report Cohen's d or Cliff's delta with
   95% CIs. A p-value of 0.001 with Cohen's d = 0.05 is statistically significant but
   practically meaningless.

4. **Sample sizes.** Every panel must indicate n (number of proteins, perturbation pairs,
   residues, etc.). This includes subgroup analyses.

5. **Baseline performance.** Every figure showing method performance must include baseline
   performance on the same axes. Never show a method in isolation.

**Every comparison table must include:**

| Column | Required |
|--------|----------|
| Method name | Yes |
| Primary metric (mean or median) | Yes |
| 95% CI on metric | Yes |
| Sample size (n) | Yes |
| Compute cost | Yes (at least order of magnitude) |
| p-value vs. best baseline | Yes (FDR-corrected) |
| Effect size vs. best baseline | Yes (with CI) |
| Win/draw/loss count | Yes (number of datasets where method beats baseline) |

**Supplementary requirements:**
- Full per-protein/per-pair results (not just aggregates) in supplementary tables
- Raw data for all evaluations deposited in a public repository
- Code for all evaluation computations in a public repository with a frozen version tag

#### 4.3 Common Statistical Mistakes in Recent Benchmark Papers (2024-2026)

Based on systematic review of recent computational biology benchmark papers, the following
mistakes are most frequent and most damaging:

**Mistake 1: Data leakage through homology.**
Problem: Train and test proteins share high sequence similarity, inflating performance.
How it manifests in our projects: In Gamma, two ProteinGym proteins from the same family
(e.g., two kinases) may share structural and functional properties. If one is in training
and one in testing, the model may generalize via homology rather than ensemble features.
Fix: Report sequence identity between train/test splits. Consider leave-family-out CV
as a sensitivity analysis (more stringent than leave-protein-out).

**Mistake 2: Metric shopping.**
Problem: Testing many metrics and reporting only the one that shows significance.
How it manifests: Delta could test 10 metrics, find significance on 2, and report only
those. This is p-hacking.
Fix: Pre-register the primary metric. Report ALL metrics. Apply multiple testing correction.
Highlight any discrepancies between metrics as scientific findings, not as problems to hide.

**Mistake 3: Inadequate baselines.**
Problem: Comparing against weak or outdated baselines to inflate apparent performance.
How it manifests: In Gamma, comparing against a random forest on raw sequence features
rather than against state-of-the-art methods (AlphaMissense, ESM-1v, EVE).
Fix: Include ALL relevant published methods. Include trivial baselines (mean prediction,
majority class) AND state-of-the-art baselines. The claim must beat BOTH.

**Mistake 4: Ignoring variance across datasets.**
Problem: Reporting aggregate performance without per-dataset breakdowns. A method may
excel on 3 proteins and fail on 12, yet show a positive aggregate.
Fix: Always show per-protein/per-pair distributions. Report the fraction of datasets
where the method improves over baseline (win rate).

**Mistake 5: Confusing statistical significance with practical significance.**
Problem: Large sample sizes (e.g., 5,000 perturbation pairs in Delta Tier 0) guarantee
small p-values for even trivial effects.
Fix: Define minimum effect size thresholds a priori (see Section 3.3). Report effect
sizes and their CIs. A statistically significant improvement of 0.1% WMSE reduction
is not a publishable finding.

**Mistake 6: Selective reporting of subgroup analyses.**
Problem: Testing many subgroups (by protein family, by assay type, by cell line) and
reporting only positive results.
Fix: Pre-register subgroup analyses. Report ALL subgroups. Apply FDR correction across
subgroups.

**Mistake 7: Cherry-picked examples.**
Problem: Showing 3-4 proteins/perturbations where the method works well, without
systematic sampling.
Fix: Select examples using a pre-specified rule: "best case, worst case, median case"
for the method. Include at least one failure case.

#### 4.4 Handling Negative Results

All three projects face the possibility that the primary hypothesis fails:
- Alpha-M: All MLFFs are worse than classical FFs
- Gamma: Ensemble features do not improve over sequence-only methods
- Delta: DL genuinely does not beat linear baselines under any metric

**Negative results ARE publishable at top venues if:**

1. The evaluation is rigorous and comprehensive (this is what our framework ensures)
2. The negative finding is surprising and changes how the field thinks
3. The paper provides actionable guidance (what SHOULD researchers do instead?)
4. The failure analysis reveals WHY the method fails

Ahlmann-Eltze & Huber (2025) published a negative result ("DL doesn't beat linear
baselines") in Nature Methods. This succeeded because:
- The evaluation was comprehensive (5 foundation models, 2 DL methods, multiple baselines)
- The finding was surprising and field-changing
- The paper was framed as a call to action, not just a critique

**Our framing for negative results:**

| Project | Negative finding | Publication framing |
|---------|-----------------|-------------------|
| Alpha-M | MLFFs all fail | "The MLFF reality gap: ML force fields trained on QM data do not yet reproduce experimental protein observables" |
| Gamma | Ensembles don't help | "Conformational dynamics are necessary but not sufficient for mutation effect prediction: why sequence-only methods remain competitive" |
| Delta | DL truly fails | "The perturbation prediction ceiling: fundamental limits of transcriptomic response prediction from single-cell data" |

In each case, the negative result paper must include a diagnostic analysis: WHICH
aspects fail, HOW they fail, and WHAT would need to change for the approach to succeed.

#### 4.5 Bayesian Model Comparison (Optional Enhancement)

For projects comparing many methods (Alpha-M: 8 FFs; Delta: 10+ methods), Bayesian model
comparison can complement frequentist testing:

**Bayes factors for method comparison:**

Instead of "reject / fail to reject" at alpha = 0.05, compute Bayes factors:
- BF_10 > 10: strong evidence for model 1 over model 0
- BF_10 = 3-10: moderate evidence
- BF_10 = 1/3-3: inconclusive
- BF_10 < 1/3: evidence for model 0

This is particularly useful when the Nemenyi test is inconclusive (adjacent methods not
distinguished). A Bayes factor analysis can provide additional evidence for or against
a difference.

**Implementation:** Use the Bayesian signed-rank test (Benavoli et al., 2017, JMLR) as
an alternative to the Wilcoxon test. This produces a posterior probability that method A
is better than method B, which is more interpretable than a p-value.

Recent work (Systematic Biology, 2026) has shown that LOO-CV-based model comparison
outperforms Bayes factors in some settings. For benchmark studies, I recommend:
- Primary: frequentist (Friedman/Nemenyi for Alpha-M, Wilcoxon for Gamma/Delta)
- Secondary: Bayesian signed-rank test for ambiguous pairwise comparisons
- Report both where they disagree

#### 4.6 Nature-Level Reporting Checklist

Based on review of benchmark papers published in Nature Methods and Nature Computational
Science (2024-2026), the following elements appear in ALL successful benchmark papers:

**Main text requirements:**
- [ ] Study design figure showing data flow, methods, and evaluation protocol
- [ ] Critical difference diagram or equivalent multi-method comparison visualization
- [ ] At least one figure showing per-dataset (not just aggregate) performance
- [ ] Effect sizes with confidence intervals for all primary claims
- [ ] Explicit discussion of limitations and failure cases
- [ ] Compute cost comparison across methods
- [ ] Code and data availability statement with DOIs

**Supplementary requirements:**
- [ ] Full per-dataset results tables
- [ ] Sensitivity analysis varying key design decisions
- [ ] Convergence/stability analysis for simulation-based methods
- [ ] Runtime benchmarks on standardized hardware
- [ ] Detailed hyperparameter settings for all methods

**Statistical reporting requirements (from Nature Portfolio guidelines):**
- [ ] All statistical tests named explicitly
- [ ] All p-values reported to 3 significant figures (not "p < 0.05")
- [ ] Confidence intervals at 95% level
- [ ] Multiple testing correction method and adjusted p-values
- [ ] Sample sizes for every analysis
- [ ] Effect sizes for every statistical test
- [ ] Software versions for all statistical analyses

---

## Implications for the Project

### Opportunities

1. **Pre-registration differentiates us.** No computational biology benchmark paper I
   have found (2024-2026) pre-registered its evaluation protocol. Doing so would be a
   novel methodological contribution and would strengthen reviewer confidence. This is a
   low-cost, high-value addition.

2. **The metric calibration framework for Delta is a standalone contribution.** The DRF
   analysis, interpolated duplicate baseline, and systematic comparison of calibrated vs.
   uncalibrated metrics could constitute a Methods section that elevates the paper from
   "yet another benchmark" to "methodological advance in benchmark design."

3. **Multi-level analysis for Alpha-M is novel.** No MLFF benchmark has applied the full
   Demsar framework with chi-squared integration across observables and critical difference
   diagrams. This statistical rigor distinguishes our benchmark from ad hoc comparisons.

4. **Group ablation for Gamma provides mechanistic insight.** Rather than just showing
   "ensembles help," we can show WHICH ensemble properties contribute (dynamics vs.
   contacts vs. pocket geometry). This transforms the paper from a prediction paper into
   a biological insight paper.

### Risks

1. **15 proteins may be underpowered for Alpha-M post-hoc tests.** The Nemenyi critical
   difference of 2.71 ranks (out of 8) means we can only distinguish clearly superior
   from clearly inferior methods. Adjacent methods will be statistically indistinguishable.
   Mitigation: increase to 20 proteins; or use Bonferroni-Dunn test (control method vs.
   all others) instead of Nemenyi (all pairwise), which has a smaller critical difference.

2. **Overfitting in Gamma is a severe risk.** With 20 features on 187 proteins, the
   model WILL find spurious patterns unless rigorously controlled. Nested CV, strong
   regularization, and permutation tests are not optional -- they are mandatory.

3. **The Delta metric controversy may not be fully resolved.** If WMSE and R^2_w(delta)
   give different conclusions from each other, we face a meta-controversy about which
   calibrated metric to trust. Mitigation: the DRF analysis provides an objective
   calibration assessment.

4. **Multiple testing burden in Delta is severe.** With 4 tiers x 10 methods x 6 metrics
   = 240 tests, many individually significant results will not survive FDR correction.
   This is correct and expected -- it means the true signals must be strong.

### Open Questions

1. Should Alpha-M use the Bonferroni-Dunn test (compare all methods to a control, e.g.,
   AMBER ff19SB) instead of Nemenyi (all pairwise)? The Bonferroni-Dunn test has more
   power when the research question is "does any MLFF beat classical FFs?" rather than
   "which MLFF is best?"

2. For Gamma, should leave-family-out CV be the primary analysis (more conservative) or
   a sensitivity analysis? Leave-family-out dramatically reduces sample size per fold
   but guards against homology leakage.

3. For Delta, how should Tahoe-100M's "cell village" design be accounted for in the
   batch effect analysis? The simultaneous profiling of multiple cell lines reduces
   batch effects but introduces new confounders (cell-cell communication, competition).

4. Should we include a Bayesian model comparison layer across all three projects, or
   is it unnecessary complexity for the primary submission?

5. For Alpha-M, how should the back-calculation uncertainty of SPARTA+ (1.09 ppm for
   13Ca) be propagated through the chi-squared scoring? Should we use a parametric model
   of back-calculation error or a bootstrap approach?

---

## References

1. Demsar, J. (2006). Statistical comparisons of classifiers over multiple data sets.
   Journal of Machine Learning Research, 7, 1-30.

2. Weber, L. M., Saelens, W., Cannoodt, R., Soneson, C., Hapfelmeier, A., Gardner, P. P.,
   Boulesteix, A. L., Saeys, Y., & Robinson, M. D. (2019). Essential guidelines for
   computational method benchmarking. Genome Biology, 20, 125.

3. Niessl, C., Klau, S., Boulesteix, A. L. (2022). Over-optimism in benchmark studies
   and the multiplicity of design and analysis options when interpreting their results.
   WIREs Data Mining and Knowledge Discovery, 12(2), e1441.

4. Boulesteix, A. L., Wilson, R., & Hapfelmeier, A. (2017). Towards evidence-based
   computational statistics: Lessons from clinical research on the role and design of
   real-data benchmark studies. BMC Medical Research Methodology, 17, 138.

5. Shen, Y., & Bax, A. (2010). SPARTA+: A modest improvement in empirical NMR chemical
   shift prediction by means of an artificial neural network. Journal of Biomolecular
   NMR, 48(1), 13-22.

6. Ahlmann-Eltze, C., & Huber, W. (2025). Deep-learning-based gene perturbation effect
   prediction does not yet outperform simple linear baselines. Nature Methods.

7. Notin, P., Kollasch, A. W., Ritter, D., van Niekerk, L., Paul, S., Spinner, H., ...
   & Marks, D. S. (2024). ProteinGym: Large-scale benchmarks for protein fitness
   prediction and design. Advances in Neural Information Processing Systems (NeurIPS 2023), 36.

8. Nerenberg, P. S., & Head-Gordon, T. (2018). New developments in force fields for
   biomolecular simulations. Current Opinion in Structural Biology, 49, 129-138.

9. Lindorff-Larsen, K., Maragakis, P., Piana, S., Eastwood, M. P., Dror, R. O., &
   Shaw, D. E. (2012). Systematic validation of protein force fields against experimental
   data. PLOS ONE, 7(2), e32131.

10. Trbovic, N., Kim, B., Friesner, R. A., & Palmer, A. G. (2008). Structural analysis
    of protein dynamics by MD simulations and NMR spin-relaxation. Proteins, 71(2), 684-694.

11. Harrell, F. E. (2015). Regression modeling strategies. Springer. (Rule of thumb for
    predictors per observation.)

12. Benavoli, A., Corani, G., Demsar, J., & Zaffalon, M. (2017). Time for a change: A
    tutorial for comparing multiple classifiers through Bayesian analysis. Journal of
    Machine Learning Research, 18, 1-36.

13. Tahoe-100M Consortium. (2025). Tahoe-100M: A giga-scale single-cell perturbation
    atlas for context-dependent gene function and cellular modeling. bioRxiv.

14. scPerturBench (2025). Benchmarking algorithms for generalizable single-cell
    perturbation response prediction. Nature Methods.

15. Aryal, R. P. et al. (2025). Assessing the performance of BioEmu in understanding
    protein dynamics. International Journal of Molecular Sciences, 27(6), 2896.

16. Zhong, B. et al. (2025). Deep learning-based genetic perturbation models do
    outperform uninformative baselines on well-calibrated metrics. bioRxiv.

17. "Diversity by Design" (2025). Addressing mode collapse improves scRNA-seq perturbation
    modeling on well-calibrated metrics. arXiv:2506.22641.

18. Kovacs, D. P. et al. (2024). MACE-OFF: Short-range transferable machine learning
    force fields for organic molecules. Journal of the American Chemical Society.

19. UniFFBench (2025). Evaluating universal machine learning force fields against
    experimental measurements. arXiv:2508.05762.

20. AlphaCell (2026). Towards building a world model to simulate perturbation-induced
    cellular dynamics. bioRxiv.

21. Vuister, G. W., & Bax, A. (1993). Quantitative J correlation: A new approach for
    measuring homonuclear three-bond J(HNHa) coupling constants in 15N-enriched proteins.
    Journal of the American Chemical Society, 115(17), 7772-7777.

22. Boulesteix, A. L. (2015). Ten simple rules for reducing overoptimistic reporting in
    methodological computational research. PLOS Computational Biology, 11(4), e1004191.

23. Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A
    practical and powerful approach to multiple testing. Journal of the Royal Statistical
    Society B, 57(1), 289-300.

24. Efron, B., & Tibshirani, R. J. (1994). An introduction to the bootstrap. Chapman &
    Hall/CRC. (BCa confidence intervals methodology.)

25. Identifying the best approximating model in Bayesian phylogenetics: Bayes factors,
    cross-validation or wAIC? Systematic Biology, 72(3), 616-632 (2023). (LOO-CV vs.
    Bayes factors for model comparison.)
