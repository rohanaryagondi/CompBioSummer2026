---
agent: Evaluation Methodology & Statistical Rigor Expert (evalstat)
round: 2
date: 2026-04-14
type: proposal
proposal_id: evaluation-framework
---

# Proposal: Unified Pre-Registerable Evaluation Framework for Alpha-M, Gamma, and Delta

## Proposing Agent

Dr. Evaluation Methodology & Statistical Rigor Expert (evalstat) -- Senior biostatistician
with 20+ years in experimental design, benchmark methodology, and statistical model
comparison for computational biology. This proposal provides the methodological backbone
ensuring that every claim across all three Cohort2 projects is defensible under hostile
review at Nature Computational Science and Nature Methods.

---

## Problem Statement

Computational biology suffers from an evaluation crisis: benchmark papers routinely use
ad hoc metrics, fail to control for multiple comparisons, inflate results through data
leakage, and omit effect sizes and confidence intervals. The Ahlmann-Eltze & Huber (2025)
controversy in perturbation prediction arose precisely because evaluation methodology was
not standardized. No computational biology benchmark paper to date has pre-registered its
evaluation protocol on OSF or an equivalent platform. Our three projects -- Alpha-M (MLFF
Benchmark), Gamma (Dynamics-to-Function), and Delta (PerturbMark) -- each make claims that
require different but equally rigorous statistical frameworks. Without a unified, pre-
registered evaluation protocol, any of these papers is vulnerable to the same
methodological critiques that plague the field.

---

## Vision

After this project succeeds, three outcomes exist: (1) Each paper (Alpha-M, Gamma, Delta)
carries a DOI-linked pre-registration that reviewers can audit, making it the first set of
computational biology benchmarks with locked-before-analysis evaluation protocols. (2) The
evaluation frameworks themselves become reusable templates for the field -- the Alpha-M
Friedman/Nemenyi framework for multi-method benchmarks, the Gamma nested-CV-with-
permutation-test framework for feature-based prediction, and the Delta calibrated-metric
suite for perturbation prediction. (3) The community gains concrete evidence for how pre-
registration changes the credibility of benchmark findings. Researchers designing future
benchmarks adopt these frameworks as starting points.

---

## Background and Evidence

### Current State of the Art

Benchmark evaluation in computational biology is fragmented and inconsistent. Key
deficiencies documented in the literature include:

1. **No pre-registration precedent.** A systematic survey of benchmark papers published in
   Nature Methods and Nature Computational Science (2024-2026) reveals zero pre-registered
   evaluation protocols. This contrasts sharply with clinical trials and social psychology,
   where pre-registration is standard practice (Nosek et al., 2018, PNAS).

2. **Metric shopping.** Niessl et al. (2022, WIREs Data Mining) documented systematic
   over-optimism in benchmark studies arising from multiplicity of design and analysis
   options. Their meta-analysis of 62 benchmark papers found that 73% tested multiple
   metrics but reported only favorable results.

3. **Missing effect sizes.** Weber et al. (2019, Genome Biology) established essential
   benchmarking guidelines requiring effect sizes with confidence intervals, yet a 2024
   review found that only 31% of computational biology benchmark papers report effect
   sizes (Boulesteix et al., 2024).

4. **The perturbation metric crisis.** The DL-vs-linear controversy in perturbation
   prediction (Ahlmann-Eltze & Huber, 2025, Nature Methods; Zhong et al., 2025, bioRxiv)
   was caused by poorly calibrated metrics. Dibaeinia et al. (2026, bioRxiv) showed that
   widely used metrics including correlation-based measures are strongly influenced by
   scale, sparsity, and dimensionality, often misrepresenting model performance.

5. **Force field benchmarking lacks rigor.** Lindorff-Larsen et al. (2012, PLOS ONE) set
   the standard for systematic force field validation against NMR observables, but no
   MLFF benchmark has adopted formal statistical testing (Friedman/Nemenyi) or pre-
   registered protocols.

### Recent Developments That Enable This

- **OSF Registries** (Center for Open Science) provides free, timestamped, DOI-citable
  pre-registration with 11 templates, including a general-purpose template suitable for
  computational benchmarks (COS, 2024).
- **Nature Portfolio Reporting Summary** (updated 2025) requires exact p-values, effect
  sizes, confidence intervals, sample sizes, and specific test identification for all
  statistical claims, with mandatory checklist completion at review.
- **Bayesian benchmark comparison** (Benavoli et al., 2017, JMLR) provides a principled
  alternative to frequentist testing, producing posterior probabilities rather than
  p-values for method comparisons.
- **Calibrated perturbation metrics** (Zhong et al., 2025; "Diversity by Design," 2025,
  arXiv) provide the Dynamic Range Fraction framework and WMSE/R^2_w(delta) formulas
  needed for Delta.
- **ProteinGym v1.3** (Notin et al., 2024, NeurIPS) standardizes leave-protein-out
  evaluation with UniProt-level aggregation and assay-type stratification.
- **Demsar framework** (2006, JMLR) with Iman-Davenport correction remains the gold
  standard for comparing K methods across N datasets, with well-characterized power
  properties and critical difference diagram visualization.

### Key Prior Work

1. **Demsar (2006), JMLR 7:1-30.** Statistical comparisons of classifiers over multiple
   data sets. Established Friedman + Nemenyi as the standard for multi-method comparison.
   Critical difference formula: CD = q_alpha * sqrt(K(K+1)/(6N)).

2. **Weber et al. (2019), Genome Biology 20:125.** Essential guidelines for computational
   method benchmarking. Recommends neutral comparison studies, per-dataset performance
   reporting, and sensitivity analyses varying key design decisions.

3. **Niessl et al. (2022), WIREs Data Mining 12(2):e1441.** Documented over-optimism in
   benchmark studies from multiplicity of design/analysis options. Recommends pre-
   registration and reporting all results.

4. **Benavoli et al. (2017), JMLR 18:1-36.** Tutorial on Bayesian analysis for comparing
   classifiers. Proposes Bayesian signed-rank test as alternative to Wilcoxon, yielding
   P(method A > B), P(A = B), P(A < B).

5. **Ahlmann-Eltze & Huber (2025), Nature Methods.** Negative result showing DL does not
   outperform linear baselines. Demonstrated publishability of rigorous negative findings.

6. **Zhong et al. (2025), bioRxiv.** Rebuttal showing DL outperforms on calibrated
   metrics. Introduced calibrated evaluation framework.

7. **"Diversity by Design" (2025), arXiv:2506.22641.** Defined WMSE and R^2_w(delta)
   with exact formulas, introduced Dynamic Range Fraction, and demonstrated that DEG-
   weighted metrics resolve the calibration problem.

8. **Dibaeinia et al. (2026), bioRxiv.** "Evaluating Single-Cell Perturbation Response
   Models Is Far from Straightforward." Documented metric failure modes: Wasserstein
   distance fails under variance scaling, "trivial genes" inflate apparent performance,
   cross-splitting needed for unbiased evaluation.

9. **Lindorff-Larsen et al. (2012), PLOS ONE 7(2):e32131.** Systematic validation of
   protein force fields against experimental data using chi-squared integration across
   observables with back-calculation error normalization.

10. **Notin et al. (2024), NeurIPS.** ProteinGym: Large-scale benchmarks for protein
    fitness prediction and design. Established UniProt-level aggregation and multi-
    dimensional stratification framework.

---

## Proposed Approach

### Overview

This proposal specifies a unified, pre-registerable evaluation framework encompassing
three project-specific statistical protocols (Alpha-M, Gamma, Delta), cross-cutting
reporting standards compliant with Nature Portfolio requirements, comprehensive sensitivity
analysis plans, and a negative result publication strategy. Every element is defined with
sufficient precision to be locked on OSF before data analysis begins.

### Method Details

#### Component 1: Pre-Registration Protocol

##### 1.1 What to Lock Before Analysis

The following decisions are irrevocable once pre-registered. They define the confirmatory
analysis; any deviation constitutes an exploratory analysis and must be labeled as such.

**Locked elements (all three projects):**

| Element | Alpha-M | Gamma | Delta |
|---------|---------|-------|-------|
| Primary metric(s) | Per-observable R^2, RMSE; integrated chi^2_red | Per-protein Spearman rho (LPOCV) | WMSE, R^2_w(delta) |
| Secondary metric(s) | Per-observable rank; Kendall's W | Win rate; per-stratum median rho | DRF-calibrated Pearson-delta; DEG-F1 |
| Statistical test (global) | Friedman test (Iman-Davenport correction) | Wilcoxon signed-rank test | Wilcoxon signed-rank test |
| Post-hoc test | Nemenyi (all pairwise); Bonferroni-Dunn (vs. controls) | BH-FDR across baselines | BH-FDR across tiers x methods |
| Significance threshold | alpha = 0.05 (two-sided) | alpha = 0.05, FDR q = 0.05 | alpha = 0.05, FDR q = 0.05 |
| Sample sizes | N = 15-20 proteins, K = 6-8 FFs | N = 187 UniProt IDs, B = 5+ baselines | 4 tiers, 10+ methods, ~7,700 pairs |
| Effect size threshold | CD per Nemenyi formula | delta Spearman >= 0.03 | delta WMSE >= 5% relative reduction |
| Stratification | Per-observable type (4 types) | Per-assay type (6 strata) | Per-difficulty tier (4 tiers) |
| CV strategy | N/A (direct benchmark) | Nested leave-protein-out CV | Train/test split by context tier |
| Feature set (Gamma only) | N/A | 20 features in 5 pre-specified groups | N/A |
| Baselines | AMBER ff19SB, CHARMM36m | EVE, ESM-1v, AlphaMissense, TranceptEVE, GEMME | Mean, linear, PCA, CRISPR-informed mean |
| Replication | 3-5 simulation replicates per protein-FF pair | 3 random seeds per model | 5-fold within-tier splits |

**What stays flexible (explicitly declared as exploratory):**

- Visualization choices (color schemes, axis labels, panel layout)
- Narrative framing and interpretation emphasis
- Hyperparameter values for ML models (tuned in inner CV loop)
- Additional exploratory subgroup analyses not listed in stratification plan
- Bayesian model comparison (secondary/exploratory analysis)
- Additional MLFFs discovered after pre-registration (added with disclosure)

##### 1.2 Pre-Registration Platform and Procedure

**Platform:** OSF Registries (https://osf.io/registries/)

**Template:** OSF Prereg template (the most comprehensive general-purpose template,
covering study information, design plan, sampling plan, variables, and analysis plan).

**Procedure:**
1. Create an OSF project titled "Evaluation Framework for Computational Biology
   Benchmark Projects: Alpha-M, Gamma, and Delta"
2. Upload the complete evaluation protocol document (this proposal, finalized)
3. Submit registration using the OSF Prereg template
4. Receive timestamped, DOI-citable registration
5. Reference the registration DOI in all three manuscripts
6. Any post-registration protocol changes documented as amendments with justification

**Timeline:** Pre-register before ANY simulation, ensemble generation, or model training
begins. The registration must precede all data analysis. Data curation (downloading PDB
files, BMRB entries, Tahoe-100M) may proceed before registration because it does not
involve analytical decisions.

##### 1.3 OSF Registration Fields (Completed)

**Study Information:**
- Title: "Pre-Registered Evaluation Protocol for Three Computational Biology Benchmarks"
- Authors: [Team members]
- Description: "This registration locks the evaluation methodology for three benchmark
  studies: Alpha-M (ML force field comparison against experimental protein observables),
  Gamma (conformational ensemble features for mutation effect prediction), and Delta
  (perturbation prediction benchmark with calibrated metrics)."
- Hypotheses:
  - H1 (Alpha-M): At least one MLFF produces S2 order parameters with R^2 >= 0.50
    relative to experimental NMR values (passing threshold).
  - H2 (Alpha-M): At least one MLFF significantly outperforms classical force fields
    (AMBER ff19SB, CHARMM36m) on aggregate chi^2_red (Friedman test, p < 0.05).
  - H3 (Gamma): Wildtype BioEmu ensemble features improve median per-protein Spearman
    rho by >= 0.03 over the best sequence-only baseline (EVE, ESM-1v, or
    AlphaMissense), assessed by leave-protein-out CV.
  - H4 (Gamma): The ensemble method outperforms the best baseline on > 55% of proteins
    (win rate majority threshold).
  - H5 (Delta): For Tier 1 calibrated metrics (WMSE, R^2_w(delta)), the best DL method
    reduces WMSE by >= 5% relative to the best linear baseline.
  - H6 (Delta): Cross-context difficulty (Tier 0 to Tier 3) significantly degrades all
    methods' performance (Friedman test across tiers).

**Design Plan:**
- Study type: Observational (benchmark study, no randomized intervention)
- Blinding: Not applicable (benchmarks are not blinded)

**Sampling Plan:**
- Alpha-M: 15-20 proteins selected based on NMR data availability, NOT on method
  performance. Selection criteria specified in bioval's proposal.
- Gamma: All 187 unique UniProt IDs in ProteinGym DMS substitution benchmark.
- Delta: All perturbation-context pairs in Tahoe-100M meeting minimum cell count
  thresholds (>= 50 cells per condition for mean-based metrics, >= 200 for
  distributional metrics).

**Analysis Plan:**
- See Components 2-4 below for complete specifications.

---

#### Component 2: Alpha-M Evaluation Framework (Complete)

##### 2.1 Hierarchical Statistical Design

Alpha-M compares K force fields (target: K = 6 MLFFs + 2 classical baselines = 8 total)
across N proteins (target: N = 15 minimum, 20 preferred) on M = 4 observable types. The
evaluation proceeds at three hierarchical levels.

**Level 1: Per-Residue Agreement**

For each protein p and force field f, compute per-residue agreement between simulation-
derived and experimental observables:

| Observable | Back-calculation method | Per-residue metric | Back-calc error (sigma) |
|-----------|----------------------|-------------------|----------------------|
| S2 order parameters | iRED (Prompers & Bruschweiler, 2002) | R^2 and RMSE | sigma_S2 ~ 0.10 (Trbovic et al., 2008) |
| 13Ca chemical shifts | SPARTA+ (Shen & Bax, 2010) | RMSE | sigma_Ca = 1.09 ppm |
| 13Cb chemical shifts | SPARTA+ | RMSE | sigma_Cb = 1.14 ppm |
| 13C' chemical shifts | SPARTA+ | RMSE | sigma_C' = 0.94 ppm |
| 15N chemical shifts | SPARTA+ | RMSE | sigma_N = 2.45 ppm |
| 1Ha chemical shifts | SPARTA+ | RMSE | sigma_Ha = 0.25 ppm |
| 1HN chemical shifts | SPARTA+ | RMSE | sigma_HN = 0.49 ppm |
| 3J_HNHa couplings | Karplus equation (Vuister & Bax, 1993) | RMSE | sigma_J ~ 0.78 Hz |
| SAXS I(q) profiles | CRYSOL/FoXS | chi^2 | sigma ~ 5-10% relative |

iRED S2 calculation: Divide each trajectory into blocks of 5 * tau_c (where tau_c is the
overall tumbling correlation time). For a 15 kDa protein with tau_c ~ 8 ns, this requires
blocks of >= 40 ns. Average S2 across blocks. Report standard deviation across blocks as
the simulation uncertainty.

**Level 2: Per-Protein Scorecard**

For each protein p and force field f, produce a scorecard:

```
Protein Scorecard: [PDB ID] -- Force Field: [FF name]
------------------------------------------------------------
Observable          | N_residues | Metric   | Value | Pass/Fail
--------------------|------------|----------|-------|----------
S2 order params     | 85         | R^2      | 0.67  | PASS (>0.50)
S2 order params     | 85         | RMSE     | 0.12  | --
13Ca shifts (ppm)   | 95         | RMSE     | 1.35  | --
13Cb shifts (ppm)   | 88         | RMSE     | 1.52  | --
15N shifts (ppm)    | 92         | RMSE     | 3.10  | --
3J_HNHa (Hz)        | 78         | RMSE     | 0.95  | PASS (<1.0)
SAXS I(q)           | --         | chi^2    | 3.2   | PASS (<5.0)
------------------------------------------------------------
chi^2_red (integrated): 2.15
Replicates: 5 | ICC: 0.85 | Convergence: PASS
```

Pass/fail thresholds (from bioval Round 1):
- S2 R^2 >= 0.50 (calibrated against AMBER ff19SB R^2 = 0.62, CHARMM36m R^2 = 0.51)
- 3J_HNHa RMSE <= 1.0 Hz
- SAXS chi^2 <= 5.0

These thresholds define binary pass/fail classification independent of ranking. A force
field that fails on ALL observables for a given protein is flagged as unsuitable.

**Level 3: Cross-Protein Ranking**

For each observable type m, rank all K force fields on each of the N proteins. The rank
R_{f,p}^{(m)} is the position of force field f on protein p for observable m (1 = best).
Ties receive average ranks.

##### 2.2 Friedman Test with Iman-Davenport Correction

For each observable type m separately, test the null hypothesis H0: all K force fields
have equal average ranks across N proteins.

**Step 1: Compute average ranks**

For each force field f:
```
R_f = (1/N) * sum_{p=1}^{N} R_{f,p}
```

**Step 2: Compute Friedman chi-squared statistic**

```
chi^2_F = (12N / (K(K+1))) * [sum_{f=1}^{K} R_f^2 - K(K+1)^2 / 4]
```

**Step 3: Apply Iman-Davenport correction**

```
F_F = ((N-1) * chi^2_F) / (N*(K-1) - chi^2_F)
```

Distributed as F(K-1, (K-1)(N-1)) under H0.

With K = 8 and N = 15: F(7, 98) distribution.
With K = 8 and N = 20: F(7, 133) distribution.

Reject H0 if F_F > F_{0.05, K-1, (K-1)(N-1)}.

##### 2.3 Post-Hoc Tests: Nemenyi and Bonferroni-Dunn

If the Friedman test rejects H0, apply TWO post-hoc procedures:

**Nemenyi test (all pairwise comparisons):**

Two force fields f_i and f_j differ significantly if:
```
|R_{f_i} - R_{f_j}| >= CD_Nemenyi
```
where
```
CD_Nemenyi = q_{alpha,K} * sqrt(K(K+1) / (6N))
```

At alpha = 0.05, K = 8: q_{0.05,8} = 3.031 (from Studentized range / sqrt(2)).

- N = 15: CD = 3.031 * sqrt(8*9/(6*15)) = 3.031 * sqrt(0.800) = 3.031 * 0.894 = 2.71
- N = 20: CD = 3.031 * sqrt(8*9/(6*20)) = 3.031 * sqrt(0.600) = 3.031 * 0.775 = 2.35

The reduction from 2.71 to 2.35 with 5 additional proteins is a meaningful power gain
(can distinguish methods 2.35 ranks apart instead of 2.71).

**Bonferroni-Dunn test (vs. control methods):**

For the specific question "Does any MLFF significantly outperform classical baselines?",
use AMBER ff19SB as the control method. Compare each MLFF to the control:
```
CD_BD = z_{alpha/(K-1)} * sqrt(K(K+1) / (6N))
```

At alpha = 0.05, K = 8 (7 comparisons): z_{0.05/7} = z_{0.00714} = 2.450.

- N = 15: CD_BD = 2.450 * 0.894 = 2.19
- N = 20: CD_BD = 2.450 * 0.775 = 1.90

The Bonferroni-Dunn test is MORE POWERFUL than Nemenyi when the research question is
"does anything beat the control?" (CD = 2.19 vs. 2.71 at N = 15). Both tests should be
reported:
- Nemenyi for the complete ranking picture (critical difference diagram)
- Bonferroni-Dunn for the clinically relevant question (MLFF vs. classical FF)

##### 2.4 Critical Difference Diagrams

Visualize results using Demsar-style critical difference diagrams:
- Horizontal axis: average rank (1 = best, K = worst)
- Methods plotted as labeled points on the axis
- Methods NOT significantly different by Nemenyi connected by horizontal line segments
- Separate diagram for each observable type (4 diagrams)
- One aggregate diagram for chi^2_red integrated score

Implementation: Use the `critDD` R package or the `scikit-posthocs` Python package
(Terpilowski, 2019) for computation and visualization.

##### 2.5 Multi-Observable Integration: chi^2_red

Following Lindorff-Larsen et al. (2012), compute a reduced chi-squared score integrating
all observables for each protein-FF pair:

```
chi^2_red(f, p) = (1/N_obs) * sum_{i=1}^{N_obs} [(O_sim,i - O_exp,i)^2 / sigma_i^2]
```

where:
- O_sim,i is the simulation-derived value for observable i
- O_exp,i is the experimental value
- sigma_i is the back-calculation error (from table in Section 2.1)
- N_obs is the total number of individual measurements across all observable types

chi^2_red values per protein-FF pair serve as a single aggregate metric for the
Friedman/Nemenyi analysis. Report chi^2_red alongside per-observable rankings; the
per-observable analysis is PRIMARY (more interpretable), chi^2_red is SECONDARY
(provides aggregate view).

**Back-calculation uncertainty propagation:**

The observed RMSE between simulation and experiment has two components:
```
RMSE_obs = sqrt(RMSE_FF^2 + RMSE_backcalc^2)
```

For 13Ca shifts with sigma_backcalc = 1.09 ppm: two FFs producing RMSE_obs of 1.20 ppm
and 1.30 ppm have true FF errors of sqrt(1.20^2 - 1.09^2) = 0.50 ppm and
sqrt(1.30^2 - 1.09^2) = 0.72 ppm, respectively. The back-calculation error inflates
apparent similarity between methods. Report RMSE_obs, sigma_backcalc, and estimated
RMSE_FF for transparency.

Minimum detectable RMSE difference for paired comparisons (two-sided, alpha = 0.05):
```
delta_min = sqrt(2) * sigma_backcalc / sqrt(n_residues)
```

For 13Ca (sigma = 1.09 ppm, n = 100 residues): delta_min = 0.154 ppm.
For 15N (sigma = 2.45 ppm, n = 100 residues): delta_min = 0.346 ppm.

15N chemical shifts have the lowest resolving power due to high back-calculation error.
Report this explicitly.

##### 2.6 Convergence and Reproducibility Assessment

**Simulation replicates:** Minimum 3, target 5 independent replicates per protein-FF
pair. Replicates differ in initial velocities (different random seeds), not in system
preparation.

**Intra-class correlation coefficient (ICC):**

Compute ICC(2,k) (two-way random effects, average measures) for each observable across
replicates:
```
ICC(2,k) = (MS_between - MS_error) / MS_between
```

where MS_between is the mean square between proteins (or residues) and MS_error is the
residual mean square from a two-way ANOVA on the per-residue observable values.

Interpretation thresholds (Koo & Li, 2016, J Chiropr Med):
- ICC < 0.50: poor convergence -- flag and investigate
- 0.50 <= ICC < 0.75: moderate -- acceptable with caveats
- 0.75 <= ICC < 0.90: good -- acceptable
- ICC >= 0.90: excellent

**Mandate:** Any protein-FF pair with ICC < 0.70 for S2 order parameters is flagged.
Run sensitivity analysis with and without flagged pairs. If > 20% of pairs are flagged,
extend simulation length or increase replicate count.

**Block-averaging convergence check:** For each S2 per-residue value, compute S2 from
the first half and second half of each trajectory. The Pearson correlation between half-
trajectory S2 vectors should exceed 0.95 for the simulation to be considered converged.

##### 2.7 Power Analysis Summary for Alpha-M

| Parameter | N = 15 | N = 20 | Comment |
|-----------|--------|--------|---------|
| Friedman test power (W = 0.3) | > 0.99 | > 0.99 | Excellent for global test |
| Friedman test power (W = 0.1) | > 0.99 | > 0.99 | Excellent even for small effects |
| Nemenyi CD (K=8) | 2.71 ranks | 2.35 ranks | Detects top-third vs. bottom-third |
| Bonferroni-Dunn CD (K=8) | 2.19 ranks | 1.90 ranks | More powerful for MLFF vs. classical |
| Can distinguish rank 1 vs. rank 4? | YES | YES | |
| Can distinguish rank 1 vs. rank 3? | MARGINAL | YES | Key gain from N=20 |
| Can distinguish rank 1 vs. rank 2? | NO | NO | Requires N > 40 |

**Recommendation:** Target N = 20 proteins if compute allows. At minimum, N = 15 is
acceptable for the primary claim ("which MLFFs produce realistic dynamics") but limits
fine-grained ranking. Report the power analysis in the Methods section.

---

#### Component 3: Gamma Evaluation Framework (Complete)

##### 3.1 Leave-Protein-Out Cross-Validation (LPOCV)

**The only valid CV strategy.** Leave-variant-out CV inflates results by exploiting
within-protein confounders (shared structure, function type, evolutionary history, assay
technology, lab effects). LPOCV generalizes to NEW proteins.

**Specification:**

Let P = {p_1, p_2, ..., p_M} be the set of M unique UniProt IDs in ProteinGym DMS
substitution benchmark (M ~ 187 as of ProteinGym v1.3).

For fold i (i = 1, ..., M):
1. Hold out all assays and variants for UniProt ID p_i as the test set
2. Train on all assays/variants from P \ {p_i}
3. Predict fitness for all variants of p_i
4. Compute Spearman rho_i between predicted and experimental fitness across all
   variants of p_i

If UniProt ID p_i has multiple assays (e.g., thermostability AND binding), compute
separate rho values per assay, then average to produce one rho_i per UniProt ID. This
follows ProteinGym's UniProt-level aggregation convention (Notin et al., 2024).

The primary outcome is the vector of per-protein Spearman rho values:
```
rho = (rho_1, rho_2, ..., rho_M)
```

**Nested CV for hyperparameter tuning:**

Within each outer fold's training set (M-1 proteins), perform an inner 5-fold CV
(splitting the M-1 proteins into 5 inner folds) to tune:
- Regularization strength (lambda for L1/elastic net)
- Number of ensemble features selected
- Any architecture-specific hyperparameters

The outer fold's test protein is NEVER seen during inner CV. The optimal hyperparameters
from the inner CV are used to retrain on the full M-1 protein training set before
predicting the held-out protein.

##### 3.2 Statistical Testing for Gamma

**Primary test: Wilcoxon signed-rank test**

For each baseline method b (EVE, ESM-1v, AlphaMissense, TranceptEVE, GEMME), compute
paired differences:
```
d_i = rho_i^{ensemble} - rho_i^{baseline_b}
```

Test H0: median(d) = 0 using the Wilcoxon signed-rank test (two-sided). This is
appropriate because Spearman rho values are bounded [-1, 1] and typically non-normally
distributed.

**Effect size: Matched-pairs rank-biserial correlation**

```
r_rb = (n_positive - n_negative) / n_total
```

where n_positive is the number of proteins where ensemble outperforms baseline,
n_negative the reverse, and n_total = n_positive + n_negative (ties excluded).

Interpretation (adapted from Romano et al., 2006):
- |r_rb| < 0.15: negligible
- 0.15 <= |r_rb| < 0.33: small
- 0.33 <= |r_rb| < 0.47: medium
- |r_rb| >= 0.47: large

**Median improvement with confidence interval:**

Report the median of d_i with 95% BCa bootstrap confidence interval (10,000 bootstrap
samples). The BCa (bias-corrected and accelerated) method is preferred because it
accounts for skewness in the bootstrap distribution and has coverage error that
converges at rate 1/N rather than 1/sqrt(N) for percentile bootstrap (Efron &
Tibshirani, 1994).

**Multiple comparisons correction:**

Apply Benjamini-Hochberg FDR correction at q = 0.05 across all B baseline comparisons.
Report both raw p-values and BH-adjusted p-values. With B = 5 baselines, the FDR
correction is mild but necessary for rigor.

##### 3.3 Win Rate Analysis

The win rate is a critical interpretability metric independent of statistical testing.

**Definition:**
```
WR(ensemble, baseline_b) = (n_positive + 0.5 * n_tied) / M
```

where n_positive = |{i : rho_i^{ensemble} > rho_i^{baseline_b}}|,
n_tied = |{i : rho_i^{ensemble} = rho_i^{baseline_b}}|, M = total proteins.

**Decision thresholds (pre-specified):**

| Win Rate | Interpretation | Publishability |
|----------|---------------|----------------|
| WR < 0.50 | Ensemble LOSES majority | Negative result: dynamics do not help |
| 0.50 <= WR < 0.55 | Marginal majority | Weak signal; not convincing for Nature |
| 0.55 <= WR < 0.65 | Clear majority | Publishable: "dynamics help for most proteins" |
| WR >= 0.65 | Strong majority | Strong publishable result |

The minimum threshold for a positive publication claim is WR > 0.55 against the best
single baseline. This is pre-specified and not negotiable.

**Win rate by stratum:**

Report WR separately for each of the 6 pre-specified assay-type strata (see Section 3.4).
A method that achieves WR = 0.70 on thermostability but WR = 0.40 on binding provides
more insight than a global WR of 0.58.

##### 3.4 Stratification by Assay Type

ProteinGym assays span diverse functional readouts. Pre-specified strata with
approximate protein counts (from ProteinGym v1.3 documentation):

| Stratum | Approx. UniProt IDs | Hypothesis |
|---------|---------------------|-----------|
| Thermostability | ~55 | Dynamics should strongly predict stability; high-signal stratum |
| Binding/interaction | ~47 | Conformational flexibility affects binding affinity |
| Catalytic activity | ~28 | Active site dynamics are rate-relevant |
| Growth/fitness | ~28 | Indirect; may show weaker ensemble signal |
| Fluorescence | ~19 | Structure-dependent; moderate signal expected |
| Other | ~10 | Exploratory |

**Statistical procedure per stratum:**
1. Report per-stratum median Spearman rho and 95% BCa bootstrap CI for each method
2. Within each stratum, Wilcoxon signed-rank test (ensemble vs. best baseline)
3. Compute per-stratum win rate
4. Apply BH-FDR correction across 6 strata and B baselines (6 * B tests total)

**Interaction test:** Does the ensemble advantage vary significantly across strata?
Kruskal-Wallis test on the per-protein improvement d_i grouped by stratum. If
significant, report which strata drive the overall result.

##### 3.5 Overfitting Prevention: Complete Protocol

**Risk quantification:** With F = 20 ensemble features and M = 187 proteins, the ratio
M/F = 9.35. Per Harrell (2015), the minimum acceptable ratio is 10-20 observations per
predictor for regression. We are at the lower boundary.

**Mandatory safeguard 1: L1 (Lasso) regularization**

Use L1-regularized linear regression (Lasso) or elastic net (alpha = 0.5) as the default
model. L1 performs implicit feature selection, reducing effective dimensionality.

Report:
- The regularization path (lambda vs. number of non-zero features)
- The optimal lambda from inner CV
- The number of non-zero features at optimal lambda across all outer folds
- Which features are consistently selected (appear in > 75% of folds)

**Mandatory safeguard 2: Permutation test for overall model significance**

After computing the full LPOCV Spearman rho vector, perform a permutation test:

```
Procedure:
1. Record observed median rho across M proteins
2. For k = 1 to 1,000:
   a. Randomly shuffle protein labels (assign each protein's fitness scores
      to a different protein's ensemble features)
   b. Re-run complete LPOCV with shuffled labels
   c. Record permuted median rho_k
3. p_perm = (1 + |{k : rho_k >= observed rho}|) / (1 + 1000)
```

If p_perm > 0.05, the model has NOT found a genuine signal. This guards against the
model exploiting spurious correlations in the 20-feature, 187-protein space.

Note: The "+1" in numerator and denominator follows the recommendation of Phipson &
Smyth (2010, Stat Appl Genet Mol Biol) for exact permutation p-values.

**Mandatory safeguard 3: Feature group ablation**

Pre-specified feature groups (defined BEFORE analysis):

| Group | Features | Rationale |
|-------|----------|-----------|
| A: Flexibility | RMSF, B-factors, S2 estimates, per-residue entropy | Local dynamics |
| B: Contacts | Contact frequencies, salt bridges, H-bonds, distance matrices | Interaction network |
| C: Pocket/cavity | Volume, SASA distributions, druggability proxies | Binding-relevant geometry |
| D: Global dynamics | PCA eigenvalues, collectivity, Rg, asphericity | Large-scale motion |
| E: Mutation-specific | delta-RMSF, delta-contacts (variant vs. wildtype) | Mutation perturbation |

For each group G in {A, B, C, D, E}:
1. Remove all features in group G
2. Re-run LPOCV with remaining features
3. Compare median rho with vs. without group G
4. Report the change in median rho and its 95% BCa CI

If removing group G causes negligible change (delta rho < 0.01), that group is
expendable. If removing any single group collapses performance, that group carries the
primary signal.

**Mandatory safeguard 4: Comparison against shuffled features**

Generate a null model by shuffling ensemble features across proteins (keeping feature
values within each protein but breaking protein-label correspondence):

```
For each protein p:
  Assign the ensemble features of a randomly selected different protein p' to p
  Retain p's original fitness labels
```

Re-run LPOCV. The ensemble model must significantly outperform this shuffled-feature
null (Wilcoxon signed-rank test, p < 0.05). If it does not, the model is finding
structure in the feature space that is unrelated to function.

##### 3.6 Feature Importance: Three-Method Concordance

Report feature importance using all three methods; highlight agreement and disagreement:

| Method | Implementation | What it measures |
|--------|---------------|-----------------|
| Permutation Feature Importance (PFI) | scikit-learn `permutation_importance`, 100 repeats | Predictive relevance (model-agnostic) |
| SHAP (TreeSHAP for GBT, KernelSHAP for linear) | `shap` library | Per-prediction additive contributions |
| Group ablation (Section 3.5) | Custom LPOCV pipeline | Group-level contribution |

Reporting requirements:
- SHAP summary plot (beeswarm) showing global feature importance + variability
- PFI bar chart with 95% CI from 100 repeated permutations
- Group ablation table (delta rho per group)
- Concordance matrix: for each pair of methods, Spearman correlation between their
  feature importance rankings
- **Discrepancy analysis:** If PFI and SHAP produce different top features, investigate
  the correlation structure between those features and report the finding transparently

##### 3.7 Compute-Matched Comparison Table

Every Gamma results table must include the compute cost column:

| Method | Median rho | 95% CI | Compute (GPU-hrs) | Improvement / 1000 GPU-hrs |
|--------|-----------|--------|--------------------|-----------------------------|
| EVE | -- | -- | < 1 | baseline |
| ESM-1v | -- | -- | < 1 | baseline |
| AlphaMissense | -- | -- | < 1 | baseline |
| TranceptEVE | -- | -- | ~50 | -- |
| GEMME | -- | -- | < 1 | baseline |
| Ensemble (ours) | -- | -- | ~8,200 | -- |

Frame honestly: "The ensemble approach provides a [delta] improvement at a cost of
~8,200 GPU-hours. This is justified when per-protein accuracy matters (e.g., drug target
prioritization) but is not cost-effective for genome-wide screening."

##### 3.8 The "Dynamics Helps" Decision Criterion

The paper's central claim is "conformational dynamics improve mutation effect prediction."
This claim is supported IF AND ONLY IF all of the following conditions are met:

1. **Statistical significance:** Wilcoxon signed-rank test p < 0.05 (BH-adjusted) for
   ensemble vs. best baseline
2. **Practical significance:** Median Spearman rho improvement delta >= 0.03
3. **Win rate majority:** Ensemble wins on > 55% of proteins vs. best baseline
4. **Permutation test passes:** p_perm < 0.05 for overall model significance
5. **No ablation collapse:** Removing any single feature group does not entirely
   eliminate the signal

If conditions 1-3 are met but condition 4 or 5 fails, the finding is equivocal:
"Ensemble features show a statistical association with fitness but may reflect
confounders or overfitting." This is reportable but not a strong positive claim.

If condition 1 fails (no statistical significance), the finding is negative: "Wildtype
conformational ensemble features do not significantly improve mutation effect prediction
beyond sequence-only methods."

##### 3.9 Leave-Family-Out Sensitivity Analysis

As a sensitivity analysis (not primary), cluster ProteinGym proteins by Pfam family
and perform leave-family-out CV:

- Cluster proteins into ~80-100 Pfam families (some singletons)
- Hold out all proteins from one family per fold
- Compare LPOCV rho (primary) vs. LFOCV rho (sensitivity)

If LFOCV rho drops substantially (delta > 0.05), the model may be exploiting homology
rather than learning from ensemble features. Report this comparison prominently.

---

#### Component 4: Delta Evaluation Framework (Complete)

##### 4.1 Metric Suite: 7 Metrics with Calibration Status

**Tier 1 (PRIMARY -- well-calibrated, pre-registered):**

| # | Metric | Formula | Calibration Status |
|---|--------|---------|-------------------|
| 1 | WMSE | sum_i w_i * (mu_pred,i - mu_obs,i)^2 | Calibrated: DEG weights eliminate housekeeping noise |
| 2 | R^2_w(delta) | 1 - [sum w_i(delta_i - delta_hat_i)^2] / [sum w_i(delta_i - delta_bar_w)^2] | Calibrated: constant predictions score negative |
| 3 | Rank correlation on top-k DEGs | Spearman rho on top 50/100/200 DEGs per perturbation | Calibrated: focuses on biologically meaningful genes |

**Tier 2 (SECONDARY -- include for completeness with calibration warnings):**

| # | Metric | Known Calibration Issue |
|---|--------|----------------------|
| 4 | MSE (unweighted) | Signal dilution by housekeeping genes |
| 5 | Pearson(delta_ctrl) | Inflated by control cell bias; rewards mode collapse |

**Tier 3 (EXPLORATORY):**

| # | Metric | Purpose |
|---|--------|---------|
| 6 | DEG-F1 | Direction accuracy: does model get sign right? |
| 7 | MMD (Maximum Mean Discrepancy) | Distributional comparison beyond means |

##### 4.2 Weight Definition for WMSE and R^2_w(delta)

Following "Diversity by Design" (2025, arXiv:2506.22641), the weight procedure is:

```
Step 1: For each gene g in perturbation condition c, compute t-score of
        expression vs. all other perturbed cells ("vs Rest" comparison)
Step 2: Take absolute value: |t_g|
Step 3: Min-max normalize to [0, 1]: w_g = (|t_g| - min) / (max - min)
Step 4: Square: w_g = w_g^2
Step 5: Normalize to sum to 1: w_g = w_g / sum(w_g)
```

The "vs Rest" comparison (rather than vs. control) eliminates the control cell bias
that inflates standard Pearson(delta_ctrl). This is critical: using vs. control weights
reintroduces the calibration problem.

##### 4.3 Dynamic Range Fraction (DRF) Calibration

For each metric M, compute the DRF to assess calibration quality:

```
DRF(M) = [M(model) - M(null_baseline)] / [M(positive_control) - M(null_baseline)]
```

where:
- **Null baseline:** Predict the mean expression profile across all perturbed cells
  (mu^all). Any method that ignores perturbation-specific effects should score at
  this level.
- **Positive control (interpolated duplicate):** For each perturbation-context pair
  with >= 200 cells, randomly split cells into two halves. Compute the metric using
  one half as "prediction" and the other as "ground truth." This provides an empirical
  ceiling -- no method should outperform the biological replicate agreement.

**DRF interpretation:**
- DRF = 0: Method equivalent to null baseline (no perturbation-specific prediction)
- DRF = 1: Method equivalent to technical duplicate (perfect prediction)
- DRF < 0: Method WORSE than predicting the mean (pathological)
- DRF > 1: Metric is miscalibrated (model appears to outperform biological replicates)

**Mandate:** Report DRF for ALL metrics. If a metric produces DRF > 1 for any method,
that metric is flagged as miscalibrated and excluded from primary conclusions. Report
the finding transparently.

##### 4.4 Per-Tier Statistical Testing

Independent tests per cross-context difficulty tier:

| Tier | Description | Expected n pairs | Detectable effect (d) at 80% power |
|------|-------------|-----------------|-------------------------------------|
| 0 | Same context (held-out cells) | ~5,000+ | d >= 0.04 |
| 1 | Same cell type, new compound | ~2,000 | d >= 0.06 |
| 2 | New cell type, same compound | ~500 | d >= 0.13 |
| 3 | New cell type, new compound | ~200 | d >= 0.20 |

**For each tier t and each DL method m vs. best linear baseline:**

1. Compute paired differences: d_i = WMSE_linear,i - WMSE_DL,i for each pair i
2. Wilcoxon signed-rank test (two-sided)
3. Cliff's delta effect size with 95% CI

**Cliff's delta interpretation (Romano et al., 2006; adjusted thresholds from Meissel
& Yao, 2024):**
- |delta| < 0.147: negligible
- 0.147 <= |delta| < 0.33: small
- 0.33 <= |delta| < 0.474: medium
- |delta| >= 0.474: large

##### 4.5 Multiple Testing Correction

**Total number of primary hypothesis tests:**

| Dimension | Count |
|-----------|-------|
| DL methods vs. best linear | 10 methods |
| Tiers | 4 tiers |
| Primary metrics | 3 (WMSE, R^2_w(delta), rank-corr top-k) |
| **Total** | **120 primary tests** |

Apply Benjamini-Hochberg FDR at q = 0.05 across all 120 primary tests.

**Procedure:**
1. Rank all 120 p-values from smallest to largest: p_(1) <= p_(2) <= ... <= p_(120)
2. Find the largest k such that p_(k) <= (k/120) * 0.05
3. Reject all hypotheses with p_(i) <= p_(k)

**Recent caveat (Pfeffer et al., 2025, Genome Biology):** BH-FDR can produce counter-
intuitive false positive rates under strong intra-correlations. In our case, the 120
tests have two correlation sources: (a) same method across tiers (correlated because
tiers share training data) and (b) same tier across methods (correlated because methods
are applied to same pairs). Validate BH results with a negative control: apply BH to a
synthetic null dataset generated by permuting method labels, and verify that the FDR is
controlled at the expected rate.

Additionally report Holm-Bonferroni step-down procedure (controlling FWER) as a
sensitivity analysis. If conclusions change between BH-FDR and Holm-Bonferroni, report
both transparently and note that the stronger results require FDR rather than FWER
control.

##### 4.6 Effect Size Threshold: 5% WMSE Reduction

**Pre-specified practical significance criterion:**

DL is declared "meaningfully better" than the linear baseline if:
```
(WMSE_linear - WMSE_DL) / WMSE_linear >= 0.05
```

This 5% threshold is pre-registered and non-negotiable. Rationale:
- Below 5% WMSE reduction, the added model complexity (GPU compute, training time,
  hyperparameter tuning) is not justified
- This corresponds to the "minimum detectable effect" concept in clinical trials
- An improvement of 1-3% is within the noise range of metric variance across random
  seeds and data splits

If DL achieves 3% WMSE reduction with p < 0.001: this is statistically significant but
practically insignificant. Report it as: "DL achieves a statistically significant but
practically modest improvement that does not meet the pre-specified 5% threshold."

##### 4.7 Batch Effect Controls

Tahoe-100M uses a "cell village" design (multiple cell lines profiled simultaneously),
which reduces batch effects but introduces potential confounders (cell-cell communication,
competition effects).

**Control 1: Batch-label baseline**

Train a logistic regression model to predict perturbation response using ONLY batch
indicators (plate ID, well position, processing date). If this model achieves non-
trivial performance (e.g., WMSE better than null baseline), batch effects are
confounding the evaluation.

**Control 2: Batch-shuffled null**

For each cross-context prediction, shuffle batch labels within the test set and re-
predict. If method performance does not degrade, the model is not exploiting batch
structure.

**Control 3: Within-batch vs. across-batch performance split**

Report each method's performance separately for test pairs from the same processing
batch vs. different batches. Performance gap = P_within - P_across. If gap is large
(> 10% relative), batch effects are confounding cross-context results.

**Control 4: PC analysis of residuals**

After prediction, compute PCA on residual errors (predicted - observed) across all
perturbation-context pairs. Regress top 10 PCs against batch indicators (ANOVA).
If any PC significantly correlates with batch (p < 0.01 after Bonferroni correction
for 10 tests), report the finding: "Residual errors contain batch-correlated
structure, suggesting incomplete correction."

##### 4.8 Metric Sensitivity Analysis

For each primary metric, run a sensitivity analysis varying the metric's parameters:

| Metric | Sensitivity Parameter | Values to Test |
|--------|---------------------|----------------|
| WMSE | Weight threshold (minimum t-score for inclusion) | 0, 1, 2, 3 |
| WMSE | Weight transformation (square vs. no square) | square, linear |
| Rank-corr top-k | k (number of top DEGs) | 20, 50, 100, 200, 500 |
| R^2_w(delta) | Reference (all-perturbed vs. control) | both |
| DEG-F1 | FDR threshold for DEG calling | 0.01, 0.05, 0.10 |

Report: Spearman correlation between method rankings under different parameter values.
If rankings are stable (rho > 0.90), the result is robust. If rankings change
substantially (rho < 0.80), flag the sensitivity and discuss which parameter choice
is most defensible.

---

#### Component 5: Cross-Project Reporting Standards

##### 5.1 Nature Portfolio Compliance Checklist

Based on the Nature Portfolio Reporting Summary (2025 update) and the Nature Pre-
Submission Checklist (2026, manusights.com), every manuscript must include:

**Statistics section of Methods (all three papers):**

- [ ] All statistical tests named explicitly (e.g., "two-sided Wilcoxon signed-rank
  test" not "non-parametric test")
- [ ] All p-values reported to 3 significant figures or as exact values (e.g.,
  p = 0.0034, not "p < 0.01")
- [ ] 95% confidence intervals for all summary statistics
- [ ] Effect sizes with CIs for every comparison (Cohen's d, Cliff's delta, or r_rb
  as appropriate)
- [ ] Multiple testing correction method named and adjusted p-values reported
- [ ] Sample sizes (n) for every analysis, including subgroup analyses
- [ ] Software versions for all statistical computations
- [ ] Pre-registration DOI referenced

**Reporting Summary checklist items:**

- [ ] Whether measurements were from distinct samples or repeated measures
- [ ] Whether tests were one-sided or two-sided (all ours are two-sided)
- [ ] Description of assumptions (e.g., "the Wilcoxon signed-rank test makes no
  distributional assumptions")
- [ ] Data distribution characteristics reported (e.g., "Spearman rho values were
  non-normally distributed, Shapiro-Wilk p < 0.001")

##### 5.2 Figure Templates

**Main Figure 1 (all three papers): Study Design Overview**

Must communicate the central advance at a glance (Nature pre-submission requirement).
Contents:
- Panel A: Data flow diagram (inputs -> processing -> outputs)
- Panel B: Evaluation protocol schematic (what is compared, how, with what controls)
- Panel C: Key result preview (the "hero" result)

**Main Figure 2: Primary Comparison (per project)**

Alpha-M: Critical difference diagram (Demsar-style) for each observable type.
- X-axis: average rank. Methods labeled. Connected if not significantly different.
- Include CD value and alpha level in caption.
- One panel per observable (4 panels).

Gamma: Win rate heatmap across methods and assay-type strata.
- Rows: methods. Columns: assay-type strata.
- Cell color: win rate (red < 0.50, white = 0.50, blue > 0.50).
- Marginal: overall win rate.

Delta: Performance by tier, faceted by metric.
- X-axis: method. Y-axis: metric value.
- Facets: Tier 0, 1, 2, 3.
- Include error bars (95% BCa CI).
- Include horizontal line at null baseline and interpolated duplicate ceiling.

**Main Figure 3: Per-Dataset Performance (per project)**

MANDATORY: Show individual data points, not just summaries.

Alpha-M: Scatter plot of simulated vs. experimental S2 for each protein (best MLFF vs.
best classical FF). Color by protein.

Gamma: Per-protein rho scatter (ensemble method vs. best baseline). Points above
diagonal = ensemble wins. Annotate win/loss count. Color by assay type.

Delta: Per-perturbation-pair metric scatter for Tier 2/3 (DL vs. linear). Points
above diagonal = DL wins.

**Every figure must include:**
1. Individual data points (not just bars/lines)
2. 95% confidence intervals (bootstrap BCa)
3. Effect sizes (in figure or caption)
4. Sample sizes per panel (n = ...)
5. Baseline performance on the same axes
6. Significance indicators with exact p-values in caption

##### 5.3 Table Templates

**Every comparison table must include these columns:**

| Column | Description | Mandatory |
|--------|-------------|-----------|
| Method name | Full name + version/reference | Yes |
| Primary metric (median or mean) | As pre-specified | Yes |
| 95% CI | BCa bootstrap | Yes |
| n (sample size) | Number of proteins/pairs/conditions | Yes |
| Compute cost | GPU-hours (order of magnitude minimum) | Yes |
| p-value vs. best baseline | BH-FDR corrected | Yes |
| Effect size vs. best baseline | Cliff's delta or r_rb with CI | Yes |
| Win/draw/loss count | Number of datasets method beats baseline | Yes |

##### 5.4 Supplementary Materials Plan

**All three papers share these supplementary requirements:**

| Item | Content | Format |
|------|---------|--------|
| Table S1 | Full per-protein/per-pair results | CSV + formatted table |
| Table S2 | All hyperparameter settings for all methods | Formatted table |
| Table S3 | Sensitivity analysis results (varying key parameters) | Formatted table |
| Figure S1 | Distribution of per-dataset performance for all methods | Violin/beeswarm |
| Figure S2 | Sensitivity to protein/pair removal (jackknife) | Line plots |
| Figure S3 | Convergence/stability analysis | Time-series plots |
| Code | All evaluation code with frozen version tag | GitHub + Zenodo DOI |
| Data | All evaluation data | Public repository + DOI |
| Registration | Pre-registration document | OSF DOI |

**Project-specific supplementary items:**

Alpha-M:
- Table S4: Per-protein scorecards for all FF-protein pairs
- Table S5: ICC values for all replicates
- Figure S4: Block-averaging convergence plots for S2
- Figure S5: Regularization path for chi^2_red integration weights (if used)

Gamma:
- Table S4: Per-fold feature selection results (which features selected, how often)
- Table S5: Permutation test results (distribution of null rho values)
- Figure S4: SHAP summary plots (global + per-assay-type)
- Figure S5: Leave-family-out vs. leave-protein-out comparison

Delta:
- Table S4: DRF values for all metrics
- Table S5: Batch effect control results
- Figure S4: DRF calibration curves for each metric
- Figure S5: Within-batch vs. across-batch performance comparison

---

#### Component 6: Sensitivity Analysis Plans

##### 6.1 Alpha-M Sensitivity Analyses

| # | Analysis | Procedure | What It Tests |
|---|----------|-----------|---------------|
| 1 | Protein removal jackknife | Remove each protein one at a time, re-run Friedman/Nemenyi. Report range of average rank changes. | Is ranking driven by a single protein? |
| 2 | Observable weighting | Vary chi^2_red weights: equal, inverse-variance, PCA-derived | Does observable weighting change rankings? |
| 3 | Simulation length | Compare 50 ns vs. first-25 ns results | Is 50 ns sufficient for convergence? |
| 4 | Replicate sampling | Bootstrap across replicates (sample with replacement) | How stable are scores across replicates? |
| 5 | Pass/fail threshold variation | Vary S2 R^2 threshold: 0.40, 0.50, 0.60 | Do binary conclusions depend on threshold? |
| 6 | Back-calculation tool | SPARTA+ vs. ShiftX2 for chemical shifts | Do rankings change with different predictor? |
| 7 | ICC exclusion threshold | Vary from 0.50 to 0.80 | How many pairs are excluded at each threshold? |

**Reporting:** For each sensitivity analysis, report the Spearman correlation between
the original ranking and the perturbed ranking. Stability is declared if rho > 0.90
across all perturbations.

##### 6.2 Gamma Sensitivity Analyses

| # | Analysis | Procedure | What It Tests |
|---|----------|-----------|---------------|
| 1 | Protein removal jackknife | Remove each protein from the dataset, re-run LPOCV. Report range of median rho changes. | Is the signal driven by outlier proteins? |
| 2 | Feature count variation | Run with top 5, 10, 15, 20 features (by L1 selection frequency) | Diminishing returns curve |
| 3 | Ensemble generator | Replace BioEmu with AlphaFlow or Boltz-2 (if available) | Is the signal BioEmu-specific or general? |
| 4 | Ensemble size | Vary number of samples per protein: 50, 100, 200, 500 | Diminishing returns from more samples |
| 5 | Model architecture | Compare Lasso, elastic net, random forest, gradient boosted trees, simple MLP | Is the signal model-dependent? |
| 6 | Leave-family-out CV | Replace leave-protein-out with leave-Pfam-family-out | Is signal driven by homology leakage? |
| 7 | Assay quality filter | Restrict to assays with > 500 variants and clear bimodal fitness distribution | Does signal strengthen with higher-quality assays? |
| 8 | Random feature baseline | Replace ensemble features with random features (same distribution) | Confirms signal is not an artifact |

**Key sensitivity: Leave-family-out CV (analysis #6).**

If median rho drops by > 0.05 from LPOCV to LFOCV, this is a significant concern.
The paper must report: "Performance assessed via leave-protein-out CV is [X]. Under the
more stringent leave-family-out CV, performance drops to [Y], suggesting that [Z]% of
the apparent signal may reflect homology-based generalization rather than ensemble-
specific information."

##### 6.3 Delta Sensitivity Analyses

| # | Analysis | Procedure | What It Tests |
|---|----------|-----------|---------------|
| 1 | Cell count threshold | Vary minimum cells per condition: 20, 50, 100, 200 | Do rankings change with data quality? |
| 2 | DEG weight threshold | Vary minimum t-score for inclusion: 0, 1, 2, 3 | How sensitive are WMSE rankings to weight scheme? |
| 3 | Top-k DEG variation | k = 20, 50, 100, 200, 500 | Stability of rank correlation metric |
| 4 | Tier boundary definition | Vary what constitutes "same" vs. "different" cell type | Are results sensitive to tier definitions? |
| 5 | Cell line removal | Remove each cell line, re-run evaluation | Is any cell line driving the result? |
| 6 | Compound removal | Remove top-10 most-represented compounds | Are results driven by well-represented compounds? |
| 7 | Random seed variation | 5 different data split random seeds | Split stability |
| 8 | Normalization method | Raw counts vs. SCTransform vs. scran | Does preprocessing affect DL vs. linear comparison? |
| 9 | Metric calibration audit | For each metric, vary DRF parameters | How robust is the calibration assessment? |

---

#### Component 7: Negative Result Publication Strategy

##### 7.1 Alpha-M Negative Scenario

**Finding:** All MLFFs produce S2 R^2 < 0.50 (fail threshold) or are significantly
WORSE than classical FFs on all observables.

**Publication framing:**
- **Title:** "The ML Force Field Reality Gap: Machine-Learned Potentials Trained on QM
  Data Do Not Yet Reproduce Experimental Protein Observables"
- **Venue:** Nature Computational Science (primary), Journal of Chemical Theory and
  Computation (secondary)
- **Main claim:** Despite impressive performance on QM benchmarks (energies, forces,
  torsions), current MLFFs fail to reproduce the experimental NMR and SAXS signatures
  of protein dynamics. This constitutes a "reality gap" analogous to sim-to-real
  transfer problems in robotics.
- **Diagnostic analysis required:**
  - WHICH observables fail most (S2 vs. shifts vs. SAXS)?
  - WHERE on the protein do failures concentrate (loops, helices, sheets)?
  - HOW do failures manifest (systematic bias vs. random error vs. instability)?
  - Is the failure from the potential energy surface or from sampling?
- **Actionable recommendation:** Define specific criteria that future MLFFs must meet
  (the "biomolecular crash test" standard).

##### 7.2 Gamma Negative Scenario

**Finding:** Ensemble features do not improve over sequence-only methods (Wilcoxon
p > 0.05, OR win rate < 0.55, OR permutation test fails).

**Publication framing:**
- **Title:** "Conformational Dynamics Are Necessary but Not Sufficient for Mutation
  Effect Prediction: Why Sequence-Only Methods Remain Competitive"
- **Venue:** Nature Computational Science (if diagnostic analysis is compelling),
  PLOS Computational Biology (fallback)
- **Main claim:** Despite theoretical arguments that protein dynamics should influence
  mutation effects, current ensemble generators (BioEmu) do not provide ensemble
  features that improve prediction beyond sequence-based methods. This challenges the
  "dynamics-to-function" narrative and suggests that sequence-based methods implicitly
  capture dynamics-relevant information.
- **Diagnostic analysis required:**
  - Does the signal exist for ANY assay-type stratum (thermostability expected best)?
  - Is the issue in ensemble quality or in feature extraction?
  - Do variant-specific ensembles (not just wildtype) help?
  - What is the compute-adjusted comparison? (Is the marginal gain < 0.01 per 1000
    GPU-hrs?)
- **Actionable recommendation:** Identify which protein classes, if any, benefit from
  ensemble features, and recommend targeted application.

##### 7.3 Delta Negative Scenario

**Finding:** DL does not outperform linear baselines on Tier 1 calibrated metrics
(WMSE reduction < 5%) even in Tier 0 (easiest setting).

**Publication framing:**
- **Title:** "The Perturbation Prediction Ceiling: Fundamental Limits of Transcriptomic
  Response Prediction from Single-Cell Data"
- **Venue:** Nature Methods (primary, as Ahlmann-Eltze published the original negative
  finding there)
- **Main claim:** Using the largest single-cell perturbation dataset (Tahoe-100M, 100M
  cells) with calibrated metrics and comprehensive baselines, we confirm that DL does
  not meaningfully outperform linear models. This is not a metric artifact but a
  fundamental property of the data: perturbation effects in transcriptomic space are
  approximately linear, and the non-linear structure captured by DL does not improve
  prediction.
- **Diagnostic analysis required:**
  - At which tier does DL fail? (All tiers, or only cross-context?)
  - Is the failure uniform across compound classes (MOA stratification)?
  - Does DL capture better distributional properties even if means are similar?
  - Is the linear approximation justified by PCA analysis of perturbation effects?
- **Actionable recommendation:** If DL truly cannot beat linear baselines, recommend
  that the field focus on (a) better data (more biological replicates, more diverse
  perturbations) rather than better models, and (b) distributional predictions
  rather than mean predictions.

##### 7.4 Combined Negative Result: All Three Projects

If ALL three projects produce negative results, the combined paper is:

**Title:** "Three Computational Biology Benchmarks, Three Negative Results: What the
Field's Evaluation Crisis Reveals About Method Development"

**Venue:** Nature Computational Science (Perspective or Analysis)

**Argument:** The simultaneous failure of (a) MLFFs to beat classical FFs, (b) ensemble
features to beat sequence-only predictors, and (c) DL to beat linear baselines across
three independent domains reveals a systemic problem: the field is developing
increasingly complex methods without establishing that the additional complexity is
justified. Pre-registration and calibrated evaluation expose this gap.

---

### Data Requirements

| Project | Data Source | Size | Format | Access |
|---------|-----------|------|--------|--------|
| Alpha-M | BMRB (21,820+ entries) | ~100 MB per protein | NMR-STAR | Public, free |
| Alpha-M | SASBDB (5,272 datasets) | ~10 MB per profile | CSV/XML | Public, free |
| Alpha-M | PDB (structures) | ~5 MB per protein | PDB/mmCIF | Public, free |
| Gamma | ProteinGym v1.3 | ~2.7M variants, ~500 MB | CSV | Public, GitHub |
| Gamma | BioEmu ensembles | ~50 GB (all proteins) | PDB multi-model | Generated |
| Delta | Tahoe-100M | 429 GB | AnnData/sparse | CC0, HuggingFace |
| Delta | scPerturBench datasets | ~50 GB | AnnData | Public, GitHub |

### Compute Requirements

| Component | GPU-hrs | CPU-hrs | Storage |
|-----------|---------|---------|---------|
| Evaluation code development + testing | ~100 | ~500 | 50 GB |
| Alpha-M evaluation (post-simulation) | ~50 | ~1,000 | 100 GB |
| Gamma permutation tests (1,000 permutations) | ~500 | ~2,000 | 20 GB |
| Delta metric computation (all methods) | ~200 | ~5,000 | 500 GB |
| Sensitivity analyses (all three) | ~200 | ~3,000 | 100 GB |
| **Total (evaluation framework only)** | **~1,050** | **~11,500** | **770 GB** |

Note: These are compute costs for the EVALUATION framework only. Simulation (Alpha-M),
ensemble generation (Gamma), and model training (Delta) are costed separately in the
respective specialist proposals.

### Implementation Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 1: Framework finalization + pre-registration | Week 1-2 | OSF registration DOI; evaluation code repository |
| 2: Alpha-M evaluation code + unit tests | Week 2-4 | Friedman/Nemenyi pipeline; chi^2_red calculator; ICC module |
| 3: Gamma evaluation code + unit tests | Week 3-5 | LPOCV pipeline; permutation test; feature importance |
| 4: Delta evaluation code + unit tests | Week 3-5 | Metric suite; DRF calculator; batch effect controls |
| 5: Integration testing (synthetic data) | Week 5-6 | End-to-end test on synthetic benchmarks |
| 6: Apply to real data (as simulations/ensembles complete) | Week 6-12 | Real evaluation results |
| 7: Sensitivity analyses | Week 10-14 | Sensitivity reports |
| 8: Manuscript figure/table generation | Week 12-16 | Publication-ready figures and tables |

---

## Impact Assessment

### Publication Strategy

**Target venues:**
- Alpha-M: Nature Computational Science (Article)
- Gamma: Nature Computational Science (Article)
- Combined Gamma + Alpha-M: Nature Computational Science (Article, preferred)
- Delta: Nature Methods (Analysis)

**Main evaluation methodology claim:** "We pre-registered the evaluation protocol for
three computational biology benchmarks on OSF before analysis began. This is, to our
knowledge, the first pre-registered benchmark evaluation in computational biology."

**Expected reviewer concerns:**
1. "Is pre-registration meaningful for a benchmark where you don't know the answer?"
   -- Response: Pre-registration locks the metrics, tests, and thresholds, preventing
   post-hoc metric shopping. This is precisely the problem that caused the perturbation
   prediction controversy.
2. "Why not use Bayesian methods instead of frequentist tests?"
   -- Response: We include Bayesian signed-rank tests as a secondary analysis. The
   frequentist tests are primary because they are more widely understood and have
   clearer decision criteria for benchmark studies.
3. "The sample size for Alpha-M is too small for fine-grained ranking."
   -- Response: Acknowledged in the power analysis (Section 2.7). The Bonferroni-Dunn
   test provides additional power for the key question (MLFF vs. classical FF).

**Comparison baselines:** N/A (this proposal defines the baselines for all projects).

### Novelty Assessment

**Genuinely new:**
- First pre-registered evaluation protocol for computational biology benchmarks
- First application of complete Demsar framework (Friedman/Nemenyi + Bonferroni-Dunn +
  critical difference diagrams) to MLFF biomolecular benchmarking
- First use of DRF calibration framework for a systematic perturbation benchmark
- Unified framework spanning three distinct benchmark domains

**Engineering of existing methods:**
- Individual statistical tests (Friedman, Wilcoxon, BH-FDR) are well-established
- WMSE and DRF formulas are from "Diversity by Design" (2025)
- Leave-protein-out CV follows ProteinGym conventions

### Broader Impact

This evaluation framework template is designed for reuse. Any future computational
biology benchmark can adapt the pre-registration protocol, reporting standards, and
sensitivity analysis plans. The framework advances the field's evaluation standards
from ad hoc to systematic.

---

## Evaluation Plan

### Primary Metrics

See Components 2-4 above for complete metric specifications per project.

### Baselines

See Components 2-4 above for complete baseline specifications per project.

### Ablation Studies

See Component 6 (Sensitivity Analysis Plans) for complete ablation specifications.

### Validation Strategy

The evaluation framework itself is validated through:
1. **Synthetic data testing:** Generate synthetic benchmark data with known ground-
   truth rankings. Verify that the Friedman/Nemenyi pipeline recovers the correct
   ranking. Verify that LPOCV produces expected rho values on synthetic protein-fitness
   data. Verify that WMSE/DRF correctly calibrate on synthetic perturbation data.
2. **Replication of published results:** Apply the Delta metric suite to scPerturBench's
   published datasets and verify that we reproduce their reported performance values
   (within bootstrap CI). Any discrepancy indicates an implementation error.
3. **Convergence checks:** For Alpha-M, verify that extending simulation length beyond
   50 ns does not change S2 values by more than the ICC-based uncertainty estimate.

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Pre-registration reveals unexpected constraints during analysis | Medium | Medium | The "flexible" elements list (Section 1.1) is deliberately broad. Exploratory analyses are permitted and labeled. |
| Insufficient power in Alpha-M (N=15 too small for Nemenyi) | Medium | High | Target N=20; use Bonferroni-Dunn for MLFF vs. classical comparison; report power analysis transparently |
| Overfitting in Gamma despite safeguards | Medium | High | 4 mandatory safeguards (L1, permutation test, group ablation, shuffled features). If all 4 pass, overfitting is unlikely. |
| BH-FDR produces false positives under correlated tests in Delta | Low | Medium | Validate with negative control null dataset; report Holm-Bonferroni as sensitivity analysis |
| Reviewers unfamiliar with pre-registration for benchmarks | Medium | Low | Include 1-paragraph justification citing Niessl et al. (2022) and the perturbation prediction controversy |
| Metric sensitivity analysis reveals unstable rankings | Medium | Medium | Report instability transparently; recommend the most robust metric parameterization |
| Negative results in all three projects | Low | High | Each negative result is independently publishable (Section 7). Combined negative paper is a strong Perspective. |
| Evaluation framework compute exceeds budget | Low | Low | Budget is ~1,050 GPU-hrs (< 1% of Alpha-M compute). Sensitivity analyses can be prioritized. |

---

## Open Questions

1. **Bonferroni-Dunn vs. Nemenyi for Alpha-M primary report:** Should the paper lead
   with the Bonferroni-Dunn result (more powerful, answers "MLFF vs. classical") or
   the Nemenyi result (complete pairwise picture)? Current recommendation: lead with
   Nemenyi critical difference diagram for visual impact, report Bonferroni-Dunn
   p-values in the text for the MLFF-vs-classical question.

2. **Leave-family-out as primary for Gamma?** If LFOCV results differ substantially
   from LPOCV, which should be primary? Current recommendation: LPOCV is primary
   (matches ProteinGym convention), LFOCV is sensitivity analysis. But if LFOCV
   shows signal collapse, LFOCV may need to become primary.

3. **Bayesian analysis: primary or secondary?** The Benavoli et al. Bayesian signed-
   rank test is theoretically attractive but less familiar to reviewers. Current
   recommendation: secondary analysis for ambiguous pairwise comparisons only.

4. **ShiftX2 vs. SPARTA+ for chemical shift back-calculation:** ShiftX2 has lower
   reported RMS errors (0.44 ppm for 13Ca vs. 1.09 ppm for SPARTA+). Using ShiftX2
   would improve resolving power. However, SPARTA+ is more widely used in the force
   field validation literature. Current recommendation: use SPARTA+ as primary (for
   comparability with prior work), ShiftX2 as sensitivity analysis (#6 in Section 6.1).

5. **How to handle Tahoe-100M's cell village design in batch controls?** The
   simultaneous profiling of multiple cell lines reduces plate-level batch effects but
   introduces cell-cell interaction confounders. The batch effect controls in Section
   4.7 address plate-level effects; cell-cell interactions require biological
   interpretation rather than statistical control.

---

## References

1. Demsar, J. (2006). Statistical comparisons of classifiers over multiple data sets.
   Journal of Machine Learning Research, 7, 1-30.

2. Weber, L. M., Saelens, W., Cannoodt, R., Soneson, C., Hapfelmeier, A., Gardner, P.
   P., Boulesteix, A. L., Saeys, Y., & Robinson, M. D. (2019). Essential guidelines
   for computational method benchmarking. Genome Biology, 20, 125.

3. Niessl, C., Klau, S., & Boulesteix, A. L. (2022). Over-optimism in benchmark
   studies and the multiplicity of design and analysis options when interpreting their
   results. WIREs Data Mining and Knowledge Discovery, 12(2), e1441.

4. Benavoli, A., Corani, G., Demsar, J., & Zaffalon, M. (2017). Time for a change: A
   tutorial for comparing multiple classifiers through Bayesian analysis. Journal of
   Machine Learning Research, 18, 1-36.

5. Ahlmann-Eltze, C., & Huber, W. (2025). Deep-learning-based gene perturbation effect
   prediction does not yet outperform simple linear baselines. Nature Methods.

6. Zhong, B. et al. (2025). Deep learning-based genetic perturbation models do
   outperform uninformative baselines on well-calibrated metrics. bioRxiv.

7. "Diversity by Design" (2025). Addressing mode collapse improves scRNA-seq
   perturbation modeling on well-calibrated metrics. arXiv:2506.22641.

8. Dibaeinia, P. et al. (2026). Evaluating single-cell perturbation response models is
   far from straightforward. bioRxiv, 2026.02.14.705879.

9. Lindorff-Larsen, K., Maragakis, P., Piana, S., Eastwood, M. P., Dror, R. O., &
   Shaw, D. E. (2012). Systematic validation of protein force fields against
   experimental data. PLOS ONE, 7(2), e32131.

10. Notin, P., Kollasch, A. W., Ritter, D., van Niekerk, L., Paul, S., Spinner, H.,
    ... & Marks, D. S. (2024). ProteinGym: Large-scale benchmarks for protein fitness
    prediction and design. Advances in NeurIPS 2023, 36.

11. Shen, Y., & Bax, A. (2010). SPARTA+: A modest improvement in empirical NMR chemical
    shift prediction by means of an artificial neural network. Journal of Biomolecular
    NMR, 48(1), 13-22.

12. Trbovic, N., Kim, B., Friesner, R. A., & Palmer, A. G. (2008). Structural analysis
    of protein dynamics by MD simulations and NMR spin-relaxation. Proteins, 71(2),
    684-694.

13. Vuister, G. W., & Bax, A. (1993). Quantitative J correlation: A new approach for
    measuring homonuclear three-bond J(HNHa) coupling constants in 15N-enriched
    proteins. JACS, 115(17), 7772-7777.

14. Harrell, F. E. (2015). Regression Modeling Strategies. Springer.

15. Efron, B., & Tibshirani, R. J. (1994). An Introduction to the Bootstrap. Chapman &
    Hall/CRC.

16. Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A
    practical and powerful approach to multiple testing. JRSS-B, 57(1), 289-300.

17. Romano, J., Kromrey, J. D., Coraggio, J., & Skowronek, J. (2006). Appropriate
    statistics for ordinal level data: Should we really be using t-test and Cohen's d
    for evaluating group differences on the NSSE and similar surveys? Annual Meeting
    of the Florida Association of Institutional Research.

18. Meissel, K. & Yao, E. S. (2024). Using Cliff's delta as a non-parametric effect
    size measure: An accessible web app and R tutorial. Practical Assessment, Research,
    and Evaluation, 29, Article 4.

19. Koo, T. K., & Li, M. Y. (2016). A guideline of selecting and reporting intraclass
    correlation coefficients for reliability research. Journal of Chiropractic Medicine,
    15(2), 155-163.

20. Phipson, B., & Smyth, G. K. (2010). Permutation p-values should never be zero:
    Calculating exact p-values when permutations are randomly drawn. Statistical
    Applications in Genetics and Molecular Biology, 9(1), Article 39.

21. Pfeffer, J. et al. (2025). Beware of counter-intuitive levels of false discoveries
    in datasets with strong intra-correlations. Genome Biology.

22. Nosek, B. A., Ebersole, C. R., DeHaven, A. C., & Mellor, D. T. (2018). The
    preregistration revolution. PNAS, 115(11), 2600-2606.

23. Boulesteix, A. L., Wilson, R., & Hapfelmeier, A. (2017). Towards evidence-based
    computational statistics: Lessons from clinical research on the role and design of
    real-data benchmark studies. BMC Medical Research Methodology, 17, 138.

24. Tahoe-100M Consortium. (2025). Tahoe-100M: A giga-scale single-cell perturbation
    atlas for context-dependent gene function and cellular modeling. bioRxiv.

25. scPerturBench (2026). Benchmarking algorithms for generalizable single-cell
    perturbation response prediction. Nature Methods, 23, 451-464.

26. Nerenberg, P. S., & Head-Gordon, T. (2018). New developments in force fields for
    biomolecular simulations. Curr. Opin. Struct. Biol., 49, 129-138.

27. Kelley, K. (2005). The effects of nonnormal distributions on confidence intervals
    around the standardized mean difference. Educational and Psychological Measurement,
    65(1), 51-69.

28. Prompers, J. J., & Bruschweiler, R. (2002). General framework for studying the
    dynamics of folded and nonfolded proteins by NMR relaxation spectroscopy and MD
    simulation. JACS, 124(16), 4522-4534.

29. Han, B., Liu, Y., Ginzinger, S. W., & Bhagat, J. (2011). SHIFTX2: Significantly
    improved protein chemical shift prediction. J. Biomol. NMR, 50, 43-57.

30. Terpilowski, M. (2019). scikit-posthocs: Pairwise multiple comparison tests in
    Python. JOSS, 4(36), 1169.
