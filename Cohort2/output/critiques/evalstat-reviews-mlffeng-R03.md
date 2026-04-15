---
agent: evalstat
round: 3
date: 2026-04-14
type: critique
proposal_reviewed: alpha-m-simulation
---

# Critique: Alpha-M -- Statistical and Methodological Adequacy of the MLFF Benchmark Design

## Reviewing Agent

**Dr. Evaluation Methodology & Statistical Rigor Expert (evalstat)** -- Senior
biostatistician with 20+ years in experimental design, benchmark methodology, and
statistical model comparison for computational biology. I review this proposal as
Reviewer 2 at Nature Computational Science: the hostile but constructive reviewer
who reads every methods section looking for the statistical flaw that could invalidate
the main claim. My focus areas are: statistical power with the proposed sample size,
multi-observable ranking integration, effect size quantification, pre-registration
design, ablation sufficiency, convergence verification, and the negative result
strategy. I explicitly complement bioval's Wave 1 critique, which covered data
quality issues (temperature, pH, S2 convergence, iRED, NVT/NPT). I do not repeat
those findings here.

## Proposal Summary

mlffeng proposes a systematic benchmark comparing 3 MLFFs (MACE-OFF24(M), SO3LR,
AI2BMD), 2 classical baselines (AMBER ff19SB, CHARMM36m), and BioEmu against
experimental NMR/SAXS observables across 7 proteins (MVP), using Friedman/Nemenyi
ranking as the statistical framework. The compute budget is ~88,400 GPU-hrs over
12-14 weeks, targeting Nature Computational Science.

---

## Overall Assessment

**Verdict:** Support with Modifications

**One-line take:** The proposal is scientifically well-motivated and the simulation
engineering is strong, but the statistical framework is critically underpowered at
N=7 proteins, lacks a principled multi-observable integration strategy, does not
specify effect size thresholds, omits pre-registration of key analytical decisions,
and has no formal strategy for the most likely outcome -- that MLFF and classical
FF performance differences are small and difficult to distinguish statistically.

---

## Strengths

1. **Correct identification of the Friedman/Nemenyi framework:** The proposal correctly
   references the Demsar (2006, JMLR) framework for comparing K methods across N datasets.
   This is the gold standard for multi-method benchmark comparison and is the right
   starting point. The Iman-Davenport correction to the Friedman chi-squared statistic
   (replacing the conservative chi-squared approximation with an F-distribution
   approximation) is methodologically correct and improves power slightly (Iman &
   Davenport, 1980, Technometrics). The plan to use both Nemenyi (all pairwise) and
   Bonferroni-Dunn (vs. control) post-hoc tests is sound, as these answer different
   research questions.

2. **Convergence ablation design is well-conceived:** The trajectory-length convergence
   analysis (10, 20, 30, 40, 50 ns checkpoints) and replica-count dependence (N = 3, 5,
   7, 10) are excellent ablation studies. These directly address the question "do
   conclusions depend on protocol choices?" and will be among the first things a
   reviewer checks. The fact that these ablations are built into the core design rather
   than treated as afterthoughts reflects good experimental design instincts.

3. **Multiple back-calculation tools as sensitivity analysis:** Running both SPARTA+
   and ShiftX2 for chemical shifts, and both Pepsi-SAXS and CRYSOL for SAXS, provides
   a built-in robustness check against back-calculation method dependence. If the
   ranking of force fields changes depending on the back-calculation tool, this reveals
   that the back-calculation noise is dominating the signal -- an important negative
   finding.

4. **BioEmu as a non-MD comparator is strategically brilliant:** Including a method
   from a fundamentally different paradigm (generative model vs. physics-based
   simulation) provides a built-in "surprise" finding regardless of outcome. From a
   statistical standpoint, BioEmu serves as an external anchor: if BioEmu outperforms
   MLFFs on NMR observables, the entire ranking shifts in a way that changes the story.
   Its trivial compute cost (~200 GPU-hrs) makes the risk-reward ratio highly favorable.

5. **Kill criteria and stability monitoring are appropriate:** The layered stability
   checks prevent wasted compute on failed simulations. From a statistical perspective,
   the survival landscape (which MLFF-protein combinations survive 50 ns) is itself a
   valuable binary outcome that can be reported as a contingency table with Fisher's
   exact test.

6. **Clear baseline identification:** Including two classical baselines (AMBER ff19SB,
   CHARMM36m) spanning the known performance range (S2 R2 = 0.62 vs. 0.51; Smith et al.,
   2024) establishes interpretable upper and lower bounds. Adding the crystal structure
   as a lower-bound baseline and published literature values as external validation is
   methodologically appropriate.

---

## Weaknesses

### 1. **Critical: Friedman/Nemenyi Test with N=7 Proteins Has Insufficient Power for Pairwise Discrimination**

The proposal plans to rank K = 6 methods (3 MLFFs + 2 classical + BioEmu) across
N = 7 proteins. The Nemenyi critical difference formula is:

```
CD_Nemenyi = q_{alpha,K} * sqrt(K(K+1) / (6N))
```

At alpha = 0.05 with K = 6: q_{0.05,6} = 2.850 (from Studentized range / sqrt(2);
Demsar, 2006, Table 5 interpolation).

```
CD_Nemenyi(N=7) = 2.850 * sqrt(6 * 7 / (6 * 7)) = 2.850 * sqrt(1.0) = 2.850
```

This means that to detect a significant pairwise difference between two methods at
N = 7, their average ranks must differ by at least 2.85 out of a possible range of
1 to 6. In practical terms, this can only distinguish the best method (average rank
~1-2) from the worst method (average rank ~5-6). It cannot distinguish between any
pair of methods in the middle of the ranking. Even the Bonferroni-Dunn test (more
powerful for control-vs-others comparison) yields:

```
CD_BD(N=7) = z_{0.05/(K-1)} * sqrt(K(K+1) / (6N))
             = z_{0.01} * sqrt(42/42)
             = 2.326 * 1.0
             = 2.326
```

This is slightly better but still cannot distinguish methods with average rank
differences below 2.3 -- meaning it can only separate the top from the bottom third
of the ranking.

**Contrast with my R02 evaluation proposal recommendations:** In my own evaluation
framework (evalstat-evaluation-proposal-R02.md, Section 2.7), I computed power
analysis for N = 15 and N = 20 proteins with K = 8 methods. The critical differences
were:

| N | CD_Nemenyi (K=8) | CD_BD (K=8) | Can distinguish rank 1 vs 3? |
|---|-----------------|-------------|------------------------------|
| 7 | 3.54 | 2.72 | NO |
| 15 | 2.71 | 2.19 | MARGINAL |
| 20 | 2.35 | 1.90 | YES |

The proposal's N = 7 makes the Friedman/Nemenyi framework essentially uninformative
for the central question: "Which MLFF is best?" At N = 7, you can only answer the
question: "Is there ANY significant difference among methods?" (the global Friedman
test), which has reasonable power even at small N because Kendall's W (the Friedman
test effect size) is sensitive to global disagreement. But the post-hoc tests -- the
ones that actually tell you WHICH methods differ -- will almost certainly fail to
find significant pairwise differences.

**The Friedman test's relationship to Kendall's W:** The Friedman chi-squared
statistic is directly related to Kendall's coefficient of concordance W:

```
W = chi^2_F / (N * (K - 1))
```

where W ranges from 0 (no agreement among protein-level rankings) to 1 (complete
agreement). For N = 7 and K = 6, the Friedman test rejects H0 at alpha = 0.05 when
W >= approximately 0.33 (moderate effect per Cohen's interpretation: 0.1 = small,
0.3 = moderate, 0.5 = large; Kendall, 1948). This means the global test has adequate
power to detect moderate-to-large ranking effects -- but the Nemenyi post-hoc cannot
decompose this into specific pairwise differences.

**The consequence for the paper's main claim:** The paper's central claim is "We
reveal a biomolecular reality gap..." If the Friedman test rejects H0 but Nemenyi
finds no significant pairwise differences, the paper can only say "methods differ
overall" without specifying which ones. This is publishable but substantially weaker
than "MACE-OFF24 significantly outperforms CHARMM36m on S2 order parameters."

- **Severity:** Critical
- **Addressable?** Partially. Three complementary strategies:

  **(a) Expand to N >= 15 proteins.** My R02 proposal identified 15-20 proteins with
  adequate NMR data. bioval's R01 research note classified proteins into Tier A (8
  proteins, excellent data), Tier B (6 proteins, good data), and Tier C (6 proteins,
  partial data). Adding 8 proteins from bioval's Tier A/B sets brings N to 15,
  reducing CD_Nemenyi from 2.85 to 2.71 (modest gain) and CD_BD from 2.33 to 2.19
  (meaningful gain). The additional compute for 8 more proteins is approximately
  40,000-50,000 GPU-hrs -- a significant increase. If compute is truly constrained
  to the MVP of ~88K GPU-hrs, then:

  **(b) Supplement Friedman/Nemenyi with Bayesian model comparison.** The Bayesian
  signed-rank test (Benavoli et al., 2017, JMLR) produces posterior probabilities
  P(method A > method B), P(A = B), and P(A < B), which are interpretable even at
  small N. The test uses a Dirichlet Process prior and a Region of Practical
  Equivalence (ROPE) parameter to distinguish "practically equivalent" from
  "meaningfully different." At N = 7, Bayesian posteriors provide more nuanced
  information than "significant / not significant." I recommend running the Bayesian
  signed-rank test for every pairwise comparison and reporting the full posterior
  simplex alongside the Friedman/Nemenyi results. The `baycomp` Python library
  (Bayesian Comparison of Machine Learning Algorithms) provides a reference
  implementation.

  **(c) Use per-residue-level bootstrap for pairwise comparisons.** Instead of
  treating each protein as one data point (N = 7), compute per-residue agreement
  for each force field and use paired bootstrap confidence intervals on the per-
  residue RMSE differences. For S2 with ~300-500 residues across 7 proteins, this
  gives N_eff in the hundreds. The bootstrap approach (10,000 resamples, BCa
  confidence intervals; Efron & Tibshirani, 1994) does not assume normality and
  naturally handles heterogeneous variance across proteins and residue types. Report
  bootstrap 95% CI for the pairwise RMSE difference between each method pair. If
  the CI excludes zero, the difference is significant at the residue level. However,
  note that this treats residues as independent, which they are not -- residues
  within the same protein share correlated errors. Use cluster bootstrap (resampling
  at the protein level) to account for this.

### 2. **Critical: No Principled Multi-Observable Integration Strategy**

The proposal evaluates 4 observable types (S2, chemical shifts, J-couplings, SAXS)
but provides no formal method for combining results across observables into a single
ranking or conclusion. The closest it comes is a "comparison heatmap" in the paper
structure section. This is a critical gap because:

(a) A method might rank 1st on S2 but 4th on chemical shifts. What is the overall
    conclusion?
(b) The 4 observables have fundamentally different error structures: S2 is bounded
    [0, 1], chemical shifts are in ppm with atom-type-dependent scales, J-couplings
    are in Hz, SAXS is chi^2. They cannot be directly compared.
(c) Without a pre-specified integration rule, the authors are free to cherry-pick
    the observable that supports their preferred narrative -- the exact metric
    shopping that Niessl et al. (2022, WIREs Data Mining) documented in 73% of
    benchmark papers.

**My R02 proposal addressed this explicitly** with the chi^2_red integration
metric following Lindorff-Larsen et al. (2012):

```
chi^2_red(f, p) = (1/N_obs) * sum_{i=1}^{N_obs} [(O_sim,i - O_exp,i)^2 / sigma_i^2]
```

where sigma_i is the back-calculation error for observable i (e.g., 1.09 ppm for
13Ca via SPARTA+, 0.78 Hz for 3J_HNHa). This normalizes each observable by its
inherent prediction uncertainty, making cross-observable comparison meaningful.

Additionally, I recommend a **Robust Rank Aggregation (RRA)** approach (Kolde et
al., 2012, Bioinformatics) as a complementary method. RRA tests whether methods
are ranked consistently better than expected under a null hypothesis of uncorrelated
rankings across observables. For each force field, compute its rank on each
observable type for each protein, then aggregate using the RRA beta-min p-value.
Methods with consistently good ranks across observables receive low RRA p-values.
This approach:
- Handles heterogeneous metrics naturally (works on ranks, not raw values)
- Does not require weighting decisions across observable types
- Produces a p-value for each method's overall ranking consistency
- Has been validated in bioinformatics meta-analysis settings

A third option is the **Plackett-Luce model** (Maystre & Grossglauser, 2015, NeurIPS;
Turner et al., 2020, Computational Statistics), which estimates latent quality scores
from observed rankings across multiple criteria. The PlackettLuce R package provides
an implementation with mixture extensions for handling heterogeneous agreement
patterns across observable types.

- **Severity:** Critical
- **Addressable?** Yes. Pre-specify the integration strategy:
  (1) Per-observable Friedman/Nemenyi as PRIMARY analysis (4 separate tests)
  (2) chi^2_red integration as SECONDARY single-number summary
  (3) RRA or Plackett-Luce as EXPLORATORY aggregate ranking
  Lock the choice of (1) and (2) in pre-registration. Report (3) as sensitivity
  analysis.

### 3. **Major: No Effect Size Quantification or Practical Significance Thresholds**

The proposal uses R2, RMSE, Pearson correlation, and chi^2 as metrics, but never
specifies what magnitude of difference between methods constitutes a practically
meaningful result. This is a pervasive problem in computational biology benchmarks
(Weber et al., 2019, Genome Biology; Boulesteix et al., 2024).

**The issue concretely:** Suppose MACE-OFF24 achieves S2 R2 = 0.58 and AMBER ff19SB
achieves R2 = 0.62. Is this difference meaningful? The proposal's statistical
framework (Friedman/Nemenyi) asks only whether the rank difference is statistically
significant, not whether it is practically important. At N = 7, the rank test will
almost certainly say "not significant." But even at N = 20, a statistically
significant rank difference of, say, 0.04 in R2 might or might not matter for
downstream applications.

**What to specify (and pre-register):**

(a) **Minimum meaningful difference (MMD) for each observable:**

| Observable | Metric | Proposed MMD | Rationale |
|-----------|--------|-------------|-----------|
| S2 | R2 | 0.05 | ~half the known gap between AMBER (0.62) and CHARMM (0.51) |
| S2 | RMSE | 0.02 | ~2x the back-calculation uncertainty (sigma_S2 ~ 0.10, so the minimum detectable RMSE difference at N=85 residues is sqrt(2)*0.10/sqrt(85) = 0.015) |
| 3J_HNHa | RMSE (Hz) | 0.15 Hz | ~1/3 of the range across classical FFs (0.35-0.97 Hz; Robertson et al., 2015) |
| 13Ca shifts | RMSE (ppm) | 0.20 ppm | ~2x the minimum detectable difference (delta_min = sqrt(2)*1.09/sqrt(100) = 0.154 ppm, from my R02 Section 2.5) |
| SAXS | chi^2 | 1.0 | One chi^2 unit is conventional threshold for "good fit" vs. "acceptable fit" |

(b) **Equivalence testing for the null result scenario.** If MLFF and classical FF
performance are similar, the appropriate test is NOT failure to reject the Friedman
null. Instead, use the Two One-Sided Tests (TOST) equivalence testing procedure
(Lakens, 2017, Psychol. Sci.; Schuirmann, 1987) with the MMD as the equivalence
bound. TOST provides positive evidence that "methods are practically equivalent,"
which is a much stronger claim than "we failed to find a difference." The TOSTER
R package or scipy.stats.equivalence in Python provide implementations.

(c) **Cohen's d or Cliff's delta for pairwise comparisons.** For each pair of
methods, compute a standardized effect size on the per-protein performance metric
difference. Cliff's delta (nonparametric) is preferable to Cohen's d here because
the metrics are not normally distributed:

```
Cliff's delta = (n_concordant - n_discordant) / (n_pairs)
```

where n_concordant is the number of protein-observable pairs where method A
outperforms method B, and n_discordant is the reverse. Report Cliff's delta with
BCa bootstrap 95% CI (10,000 resamples) for every pairwise comparison. Interpret
using the Vargha-Delaney scale: |delta| < 0.147 negligible, < 0.33 small, < 0.474
medium, >= 0.474 large (Vargha & Delaney, 2000, JEBS).

- **Severity:** Major
- **Addressable?** Yes. Add effect size computation and MMD thresholds to the
  analysis plan. Pre-register the MMD values. Compute Cliff's delta with CI for
  all pairwise comparisons. Add TOST equivalence testing for the null result scenario.

### 4. **Major: Pre-Registration Protocol Is Absent**

The proposal does not mention pre-registration. This is a significant omission for
a benchmark study targeting Nature Computational Science, which requires exact
p-values, effect sizes, confidence intervals, sample sizes, and specific test
identification in its Reporting Summary (Nature Portfolio, updated 2025). My R02
evaluation proposal (Section 1) specified a complete OSF pre-registration protocol
with locked elements, flexible elements, and explicit hypotheses.

**What must be locked before any simulations run:**

| Element | Specification |
|---------|--------------|
| Primary metrics | Per-observable R2, RMSE; integrated chi^2_red |
| Secondary metrics | Per-observable rank; Kendall's W |
| Statistical test (global) | Friedman (Iman-Davenport) |
| Post-hoc test | Nemenyi + Bonferroni-Dunn (both) |
| Significance threshold | alpha = 0.05 (two-sided) |
| Sample size | N = [locked number] proteins, K = 6 methods |
| Effect size measure | Cliff's delta with BCa 95% CI |
| MMD thresholds | Per-observable table (locked values) |
| Equivalence bounds | TOST bounds = MMD values |
| Stratification | Per-observable type (4 types) |
| Integration method | chi^2_red formula with locked sigma_i |
| Pass/fail criteria | S2 R2 >= 0.50, 3J RMSE <= 1.0 Hz, SAXS chi^2 <= 5.0 |
| Convergence criterion | ICC >= 0.70 for S2 |
| Ablation protocol | Trajectory length: 10/20/30/40/50 ns; replicas: 3/5/7/10 |

**What stays flexible (explicitly declared as exploratory):**
- Visualization choices (color, layout, axis scales)
- Additional MLFFs discovered after pre-registration (added with disclosure)
- Narrative framing and interpretation emphasis
- Bayesian model comparison (secondary/exploratory)
- RRA or Plackett-Luce aggregate ranking (exploratory)

**Platform:** OSF Registries (https://osf.io/registries/), using the OSF Prereg
template. The registration must be timestamped and DOI-citable BEFORE any production
simulations begin (Phase 1 stability testing may precede registration because it
does not involve analytical decisions).

No computational biology benchmark paper to date has pre-registered its evaluation
protocol on OSF. Being the first provides a methodological novelty claim that
strengthens the paper independently of the simulation results. Nosek et al. (2018,
PNAS) documented that pre-registration substantially increases the credibility of
empirical findings by eliminating post-hoc analytical flexibility.

- **Severity:** Major
- **Addressable?** Yes. Draft and file the pre-registration before Phase 2 production
  runs begin. The analytical decisions are already implicit in the proposal; they
  just need to be formalized and locked.

### 5. **Major: Back-Calculation Uncertainty Not Propagated Through Comparisons**

The proposal acknowledges SPARTA+ accuracy (CA RMSE 1.09 ppm, N RMSE 2.45 ppm) and
Karplus parameter uncertainty (~0.3-0.5 Hz), but does not propagate these uncertainties
through the comparison. This creates a critical interpretability problem:

**The problem concretely:** The observed RMSE between simulation and experiment has
two components:

```
RMSE_obs^2 = RMSE_FF^2 + RMSE_backcalc^2
```

For 13Ca shifts (RMSE_backcalc = 1.09 ppm):
- If FF_A produces RMSE_obs = 1.20 ppm, then RMSE_FF = sqrt(1.20^2 - 1.09^2) = 0.50 ppm
- If FF_B produces RMSE_obs = 1.30 ppm, then RMSE_FF = sqrt(1.30^2 - 1.09^2) = 0.72 ppm

The apparent difference (1.30 - 1.20 = 0.10 ppm) understates the true FF quality
difference (0.72 - 0.50 = 0.22 ppm). Conversely, for 15N shifts (RMSE_backcalc =
2.45 ppm):
- If FF_A produces RMSE_obs = 2.55 ppm, then RMSE_FF = sqrt(2.55^2 - 2.45^2) = 0.71 ppm
- If FF_B produces RMSE_obs = 2.65 ppm, then RMSE_FF = sqrt(2.65^2 - 2.45^2) = 1.02 ppm

Here the back-calculation error dominates so severely that 15N shifts provide
almost no discriminatory power between force fields. The minimum detectable RMSE
difference for 15N at N = 100 residues is:

```
delta_min = sqrt(2) * sigma_backcalc / sqrt(n_residues)
          = sqrt(2) * 2.45 / sqrt(100)
          = 0.346 ppm
```

This means 15N shifts can only detect force field differences that produce RMSE
differences larger than 0.35 ppm -- which may be larger than the actual differences
between methods.

**Required actions:**
(a) Report RMSE_obs, RMSE_backcalc (sigma), and estimated RMSE_FF for each
    observable and method.
(b) For the Friedman ranking, rank methods on estimated RMSE_FF (after subtracting
    back-calculation variance), not RMSE_obs. This prevents observables with high
    back-calculation error from dominating or washing out the ranking.
(c) Compute and report the minimum detectable RMSE difference (delta_min) for each
    observable type, making explicit which observables have adequate resolving power.
(d) If delta_min > expected FF differences for any observable, flag that observable
    as "low discriminatory power" and weight it lower (or exclude from) the
    integrated chi^2_red.

- **Severity:** Major
- **Addressable?** Yes. The deconvolution formula is straightforward. The back-
  calculation errors (sigma_i) are published. Implementation requires adding ~20
  lines to the analysis pipeline per observable type.

### 6. **Major: ICC > 0.70 Convergence Threshold Is Insufficiently Justified**

The proposal mentions "block-averaged errors computed identically for all methods"
as a convergence check, but does not specify the ICC threshold or the ICC model type.
My R02 proposal specified ICC(2,k) >= 0.70 for S2 order parameters, which I now
critically re-examine.

**The problem with 0.70:** According to Koo & Li (2016, J. Chiropr. Med.) -- the
definitive guideline on ICC reporting -- ICC values between 0.50 and 0.75 indicate
only "moderate" reliability. For a benchmark study claiming to establish which force
fields produce "physically realistic dynamics," moderate reliability is insufficient.
The guideline's threshold for "good" reliability is ICC >= 0.75, and "excellent" is
ICC >= 0.90.

Moreover, the ICC threshold must be calibrated to the expected effect size. If the
difference in S2 R2 between force fields is ~0.10 (the gap between AMBER at 0.62
and CHARMM at 0.51), then intra-method variance (measured by ICC) must be
substantially smaller than this inter-method difference. Specifically:

```
ICC >= 1 - (sigma_within^2 / sigma_total^2)
```

For the ranking to be stable, we need sigma_within (within-method, across-replica
variance) << sigma_between (between-method variance). If ICC = 0.70, then
sigma_within accounts for 30% of total variance, which could easily swamp a 0.10
difference in R2.

**My revised recommendation:**
- ICC >= 0.80 for S2 order parameters (the primary discriminatory observable)
- ICC >= 0.70 for chemical shifts and J-couplings (which converge faster)
- Report both ICC(2,1) (single-replica) and ICC(2,k) (averaged across k replicas)
- Use the Koo & Li (2016) ICC(2,k) model for test-retest reliability (two-way
  random effects, average measures)
- If ICC < 0.80 for any protein-FF pair on S2, investigate: is this a convergence
  failure (extend simulations) or genuine high variance (interesting finding)?
- Sample size for reliable ICC estimation: Koo & Li recommend at least 30
  heterogeneous samples. With 70-150 backbone NH residues per protein, this
  criterion is satisfied for individual proteins. But the 10 replicas (or 15 per
  bioval's recommendation) should provide adequate "raters" for the ICC computation.

- **Severity:** Major
- **Addressable?** Yes. Raise the S2 ICC threshold to 0.80. Specify the ICC model
  type as ICC(2,k). Add protocol for handling sub-threshold ICC cases.

### 7. **Major: Ablation Studies Are Necessary but Insufficient**

The proposal includes two ablation studies:
(a) Trajectory length: 10, 20, 30, 40, 50 ns checkpoints
(b) Replica count: N = 3, 5, 7, 10 replicas for S2

These are good but miss critical ablations that a reviewer will demand:

**(c) Back-calculation tool sensitivity:** The proposal mentions running both SPARTA+
and ShiftX2, but does not formalize this as an ablation. Pre-specify: "If the ranking
of force fields for chemical shifts differs between SPARTA+ and ShiftX2 (Kendall's
tau < 0.90 between the two rankings), flag back-calculation tool as a confound and
report both rankings equally." This is critical because UCBShift 2.0 (Li et al.,
JCTC 2024) claims improved accuracy over both SPARTA+ and ShiftX2 -- if two
established tools disagree, which do you trust? The answer must be pre-specified.

**(d) Water model sensitivity (for MACE-OFF24(M)):** The proposal correctly identifies
that MLFFs use "ML water" while classical baselines use TIP3P. But the ablation should
formalize the comparison: run MACE-OFF24(M) in both full-ML mode and ML/MM mode
(createMixedSystem() with TIP3P water) for at least 2 proteins (ubiquitin and HEWL).
Compare NMR observables between the two modes. If ML water quality substantially
affects protein observables, this is a critical finding. If not, it simplifies
interpretation. This ablation is mentioned as a "fallback" but should be elevated
to a pre-specified sensitivity analysis.

**(e) Karplus parameter sensitivity:** bioval identified the Vuister & Bax (1993) vs.
Bax (2015) parameter discrepancy. Formalize this as an ablation: compute J-couplings
with both parameter sets and report whether the force field ranking changes. If it
does, the Karplus parametrization is a confound; if not, the result is robust. This
costs zero additional compute.

**(f) Frame sampling density:** The proposal samples chemical shifts from every 100th
frame (500 frames per 50 ns). Add a pre-specified check: compute shifts at 10 ps
intervals (5,000 frames) for at least one protein-FF pair and compare to the 100 ps
result. If the ranking changes with denser sampling, the sparse sampling is a
confound.

- **Severity:** Major
- **Addressable?** Yes. Add ablations (c)-(f). They require zero or negligible
  additional simulation compute; only post-processing analysis time.

### 8. **Minor: No Formal Negative Result Strategy**

The proposal mentions that "Classical FFs dominate all observables" is a medium-high
likelihood outcome (Risk #3), and frames it as "identifying the reality gap." This
is correct in spirit but lacks methodological rigor. The negative result strategy
should be formalized with specific decision criteria:

**Decision tree for negative result scenarios:**

Scenario A: **MLFFs crash (>=2/3 fail stability test on >50% of proteins)**
- Publication angle: "Production readiness assessment of biomolecular MLFFs"
- Statistical framework: contingency table (stability/failure x MLFF x protein),
  Fisher's exact test
- Minimum viable paper: survival landscape + diagnostic analysis of failure modes
- Venue: JCTC (lower bar than Nature Comp Sci)

Scenario B: **MLFFs are stable but worse than classical FFs on all observables**
- Publication angle: "The biomolecular reality gap" (UniFFBench analogue)
- Statistical framework: Friedman test confirms significant ranking difference;
  critical difference diagram shows classical FFs in the top group, MLFFs in the
  bottom group
- Key question: Is the gap uniform across observables, or are there "islands of
  MLFF excellence" on specific observables/proteins?
- Equivalence test: Run TOST to determine whether MLFFs are within the MMD of
  classical FFs for any observable. If TOST rejects equivalence, the gap is real
  and meaningful.

Scenario C: **All methods perform similarly (no significant Friedman result)**
- This is the most statistically challenging outcome. The appropriate analysis is
  NOT "we found no difference" but rather:
  (1) TOST equivalence testing with pre-registered bounds: can we positively
      conclude that methods are equivalent?
  (2) Bayesian model comparison: what is P(all methods equivalent)? Use Benavoli
      et al. (2017) with ROPE = MMD values.
  (3) Power analysis disclosure: given our N and effect size, what differences
      could we have detected? If the power to detect the observed effect size is
      < 0.80, state explicitly that the study was underpowered for this scenario.
  (4) Publication angle: "Biomolecular MLFFs have reached accuracy parity with
      classical force fields for NMR observables" -- still publishable if supported
      by equivalence testing, not just failure to reject.

Scenario D: **Mixed results (MLFF ranks vary across observables)**
- This is actually the most likely outcome and the most interesting.
- Statistical framework: Report per-observable critical difference diagrams.
  Test for interaction between method and observable type using Scheirer-Ray-Hare
  test (nonparametric two-way ANOVA analogue) or permutation-based interaction test.
- Publication angle: "Observable-dependent accuracy of MLFFs reveals which physical
  properties are well-captured by DFT-trained potentials"

- **Severity:** Minor (the correct instincts are present; they just need formalization)
- **Addressable?** Yes. Add the decision tree to the pre-registration document.

### 9. **Minor: Residue-Level Outlier Analysis Is Missing**

The proposal computes per-residue agreement but does not specify how outlier residues
will be handled. This matters because:

(a) A few badly predicted residues (e.g., highly flexible loops, residues near
    protonation-sensitive sites) can dominate RMSE and distort the ranking.
(b) Outlier patterns may differ between force fields in informative ways (e.g., one
    MLFF consistently mispredicts proline residues while another fails at glycines).

**Required additions:**
- Report Cook's distance or DFFITS for per-residue S2 predictions to identify
  influential residues that disproportionately affect R2.
- Run the ranking analysis with and without the top 5% outlier residues per protein.
  If rankings change, the result is driven by a few residues, not systematic accuracy.
- Categorize residues by secondary structure type (helix, sheet, loop/coil) and
  report per-category performance. This is trivially computed from DSSP and provides
  mechanistic insight into where MLFFs succeed or fail.
- For J-couplings, residues adjacent to prolines should be flagged separately because
  the Karplus relationship has known limitations for pre-proline residues (Pardi et
  al., 1984; Schmidt et al., 2012).

- **Severity:** Minor
- **Addressable?** Yes. Requires only post-processing analysis additions.

### 10. **Minor: Classical Baseline Timestep Introduces an Unnecessary Confound**

The proposal runs classical baselines at 1 fs without SHAKE to match the MLFF
integrator, while also planning 2 fs + SHAKE results in the Supplementary. This is
scientifically motivated but creates a reviewer concern: 1 fs classical MD is
NOT how these force fields were validated. AMBER ff19SB was validated at 2 fs with
SHAKE (Tian et al., 2020, JCTC). CHARMM36m likewise (Huang et al., 2017, Nat.
Methods). Running them at 1 fs changes the ensemble sampling slightly (more frequent
integration steps, different energy conservation properties) and may produce subtly
different observables.

**My recommendation:** Run the classical baselines at BOTH timesteps as co-primary
results, not primary/supplementary. Frame the 2 fs + SHAKE results as "standard
protocol" and the 1 fs no-SHAKE results as "controlled comparison protocol."
Report both in the main text or at minimum in Extended Data. If the two protocols
produce different classical rankings (unlikely but possible), this itself is a
finding about timestep sensitivity. The additional compute cost for the 2 fs runs
is negligible (~60 GPU-hours total for 7 proteins x 2 FFs x 100 ns).

- **Severity:** Minor
- **Addressable?** Yes. Elevate 2 fs + SHAKE from Supplementary to Extended Data
  or dual reporting in the main text.

---

## Feasibility Assessment

### Technical Feasibility

The statistical analyses I recommend (Friedman/Nemenyi, Bayesian signed-rank,
bootstrap CI, TOST equivalence testing, Cliff's delta, ICC, RRA, chi^2_red
integration) are all implemented in mature, well-tested software:

| Analysis | Software | Package |
|----------|----------|---------|
| Friedman + Nemenyi | Python | `scikit-posthocs` (Terpilowski, 2019) |
| Bayesian signed-rank | Python | `baycomp` |
| Bootstrap BCa CI | Python | `scipy.stats.bootstrap` (scipy 1.9+) |
| TOST equivalence | Python/R | `TOSTER` (R), `scipy.stats` |
| Cliff's delta | Python/R | `cliffs_delta` in `scipy.stats` |
| ICC | R/Python | `pingouin.intraclass_corr` (Python), `irr` (R) |
| RRA | R | `RobustRankAggreg` (Kolde et al., 2012) |
| Critical difference diagrams | Python | `autorank` (Herbold, 2020) |
| Plackett-Luce | R | `PlackettLuce` (Turner et al., 2020) |

All require negligible compute time (minutes on a single CPU). The bottleneck is
simulation, not analysis. These statistical additions do not extend the timeline.

### Scientific Feasibility

Even with N = 7 proteins, the study produces valuable results IF the statistical
framework is properly calibrated to what N = 7 can and cannot answer. The study
CAN definitively answer:
- Are there significant global differences among methods? (Friedman test: YES,
  adequate power for moderate effects)
- Which methods crash? (Binary survival: no statistical issue)
- What are the per-observable performance profiles? (Descriptive, no N-dependence)
- Are methods practically equivalent? (TOST: requires N >= 5 for reasonable power)

The study CANNOT definitively answer with N = 7:
- Which specific MLFF is best? (Nemenyi: underpowered for fine-grained ranking)
- Is the difference between rank 2 and rank 3 significant? (Requires N >> 20)

This distinction must be stated transparently in the paper.

### Timeline Feasibility

The statistical framework additions I recommend add approximately 1-2 weeks of
analysis time (primarily for pre-registration drafting and Bayesian analysis
implementation). This fits within the 11-14 week timeline by overlapping with the
Phase 5 analysis period. The pre-registration itself should be completed during
Phase 1 (Weeks 1-2), before production simulations begin.

---

## Suggested Modifications

### Priority 1 (Critical -- Must Address Before Proceeding)

1. **Expand protein set to N >= 12, ideally 15.** If compute constraints prevent
   expanding to 15, at minimum expand to 12 by adding 5 proteins from bioval's
   Tier A/B classification. This reduces CD_Nemenyi(K=6) from 2.85 to approximately
   2.17, enabling discrimination of methods separated by approximately 2.2 average
   ranks (top third vs. bottom third). Every additional protein beyond 7 provides
   diminishing but valuable returns.

2. **Add Bayesian signed-rank test as secondary analysis.** For every pairwise method
   comparison, report P(A > B), P(A = B), P(A < B) using the Benavoli et al. (2017)
   framework with ROPE = MMD. This provides interpretable results even at small N.

3. **Pre-specify the multi-observable integration method.** Lock chi^2_red (Lindorff-
   Larsen, 2012) as the secondary integration metric. Lock the back-calculation error
   values (sigma_i) used in the denominator. Add RRA as an exploratory robustness check.

4. **Pre-register the evaluation protocol on OSF.** Before production simulations
   begin, file a complete pre-registration locking all analytical decisions listed
   in Weakness #4. This is the single highest-value addition to the proposal's
   credibility.

### Priority 2 (Major -- Strongly Recommended)

5. **Add effect size reporting for all pairwise comparisons.** Cliff's delta with
   BCa 95% CI. Pre-register MMD thresholds per observable.

6. **Propagate back-calculation uncertainty through comparisons.** Report RMSE_FF
   (deconvolved from back-calculation error) alongside RMSE_obs. Flag observables
   where delta_min exceeds expected inter-method differences.

7. **Raise the S2 ICC convergence threshold to 0.80.** Specify ICC(2,k) model type.
   Add protocol for sub-threshold cases.

8. **Add TOST equivalence testing for the null/equivalence scenario.** Pre-register
   equivalence bounds equal to the MMD thresholds. This provides positive evidence
   for equivalence rather than mere failure to reject difference.

9. **Formalize the back-calculation tool ablation.** Pre-specify Kendall's tau >= 0.90
   as the threshold for ranking agreement between SPARTA+ and ShiftX2.

### Priority 3 (Minor -- Address If Time Permits)

10. **Add residue-level outlier analysis.** Cook's distance, per-secondary-structure
    performance breakdown, pre-proline residue flagging.

11. **Elevate 2 fs + SHAKE classical results to co-primary status.**

12. **Formalize the negative result decision tree.** Include in the pre-registration
    document with specific analysis pathways for Scenarios A-D.

13. **Add per-residue cluster bootstrap** as supplementary evidence for pairwise
    method differences. Resample at the protein level to account for within-protein
    correlation.

---

## Alternative Approaches

### Bayesian Hierarchical Model as a Unified Framework

Instead of the Friedman/Nemenyi frequentist framework, consider a Bayesian
hierarchical model (Corani et al., 2017, Machine Learning) that jointly models all
observables, proteins, and methods:

```
Y_{obs,protein,method} ~ Normal(mu_{method,obs}, sigma_{protein,obs}^2 + sigma_{backcalc,obs}^2)
mu_{method,obs} ~ Normal(mu_{method}, tau_{obs}^2)
mu_{method} ~ Normal(mu_grand, tau_{method}^2)
```

This model:
- Pools information across proteins (partial pooling mitigates the small-N problem)
- Explicitly models back-calculation uncertainty as a separate variance component
- Produces posterior distributions for method rankings that naturally account for
  uncertainty
- Handles missing data (not all proteins have all observable types) gracefully
- Generates shrinkage estimates that are more reliable at small N than raw averages

The downside is complexity: the model requires careful prior specification and
convergence diagnostics (Rhat, effective sample size). Implementation in PyMC or
Stan requires approximately 100-200 lines of model specification. But the inferential
gains at N = 7 are substantial compared to the rank-based Friedman approach.

I present this as an alternative, not a replacement. The Friedman/Nemenyi framework
should remain the primary analysis (it is established, interpretable, and expected
by reviewers). The Bayesian hierarchical model should be positioned as a sensitivity
analysis that provides richer inference.

### Profile Likelihood for Multi-Observable Ranking

An alternative to chi^2_red integration is the profile likelihood approach used in
clinical diagnostics. For each force field, compute the likelihood of the observed
data given the force field's performance parameters across all observables. Rank
force fields by their profile log-likelihood. This naturally handles heterogeneous
error structures and provides a principled weighting of observables based on their
information content (high-precision observables automatically receive more weight).

This approach requires specifying a per-residue likelihood function for each
observable type (e.g., Normal for shifts, von Mises for dihedral-dependent
J-couplings, chi-squared for SAXS). The total log-likelihood across all observables
and residues for a given protein-FF pair is:

```
LL(FF, protein) = sum_{obs} sum_{residue} log P(data_{obs,residue} | FF, sigma_backcalc)
```

This is computationally trivial but provides a more principled aggregate than
chi^2_red because it accounts for the distributional properties of each observable.

---

## Impact on Publication Narrative

### For Nature Computational Science

The statistical framework is a crucial part of the publication narrative. With the
modifications I recommend, the paper can claim two layers of novelty:

1. **Scientific novelty:** First systematic MLFF benchmark against experimental
   protein observables.
2. **Methodological novelty:** First computational biology benchmark with
   pre-registered evaluation protocol, formal multi-observable integration, and
   equivalence testing for the null result.

The second claim is independently valuable. Reviewers at Nature Computational Science
will note that the evaluation methodology exceeds the standard for force field
benchmarks (which typically report ad hoc metrics without formal statistical testing).
This positions the paper as a methodological standard-setter, not just a result paper.

### For the Combined Gamma + Alpha-M Narrative

The statistical framework for Alpha-M directly feeds Gamma. If Alpha-M determines
that "MLFF X produces the most physically realistic ensembles" (based on the
Friedman ranking), then Gamma can test whether "ensembles from MLFF X also predict
function better." The strength of this connection depends entirely on the statistical
credibility of the Alpha-M ranking. With N = 7 and no pre-registration, a reviewer
can dismiss the ranking as "underpowered and potentially cherry-picked." With N >= 12,
pre-registration, and equivalence testing, the ranking is defensible and the
Gamma integration is credible.

### Risk of Underpowered Statistics

If the study proceeds with N = 7 and the Nemenyi test finds no significant pairwise
differences (the most likely outcome), the paper is reduced to descriptive statistics:
"Here are the per-observable performance profiles for each method." This is still
publishable (analogous to UniFFBench, which relied primarily on descriptive comparisons)
but forfeits the statistical rigor claim. A reviewer might write: "The authors propose
the Friedman/Nemenyi framework but with N = 7 proteins, this framework has no power
to detect the differences they claim to find. The analysis is essentially descriptive
dressed up in statistical language." This is the single most damaging reviewer comment
the paper could receive, and it is entirely preventable by expanding N or
supplementing with Bayesian methods.

---

## References

1. Demsar, J. (2006). Statistical Comparisons of Classifiers over Multiple Data Sets.
   *Journal of Machine Learning Research*, 7, 1-30.

2. Iman, R.L., & Davenport, J.M. (1980). Approximations of the critical region of the
   Friedman statistic. *Communications in Statistics - Theory and Methods*, 9(6), 571-595.

3. Benavoli, A., Corani, G., Demsar, J., & Zaffalon, M. (2017). Time for a Change: a
   Tutorial for Comparing Multiple Classifiers Through Bayesian Analysis. *Journal of
   Machine Learning Research*, 18, 1-36.

4. Kolde, R., Laur, S., Adler, P., & Vilo, J. (2012). Robust rank aggregation for gene
   list integration and meta-analysis. *Bioinformatics*, 28(4), 573-580. DOI:
   10.1093/bioinformatics/btr709

5. Weber, L.M., et al. (2019). Essential guidelines for computational method
   benchmarking. *Genome Biology*, 20, 125. DOI: 10.1186/s13059-019-1738-8

6. Niessl, C., Herrmann, M., Guenther, C., & Boulesteix, A.L. (2022). Over-optimism
   in benchmark studies and the multiplicity of design and analysis options when
   interpreting their results. *WIREs Data Mining and Knowledge Discovery*, 12(2),
   e1441.

7. Nosek, B.A., et al. (2018). The preregistration revolution. *Proceedings of the
   National Academy of Sciences*, 115(11), 2600-2606. DOI: 10.1073/pnas.1708274114

8. Koo, T.K., & Li, M.Y. (2016). A Guideline of Selecting and Reporting Intraclass
   Correlation Coefficients for Reliability Research. *Journal of Chiropractic
   Medicine*, 15(2), 155-163. DOI: 10.1016/j.jcm.2016.02.012

9. Lindorff-Larsen, K., et al. (2012). Systematic Validation of Protein Force Fields
   against Experimental Data. *PLoS ONE*, 7(2), e32131. DOI:
   10.1371/journal.pone.0032131

10. Efron, B., & Tibshirani, R.J. (1994). *An Introduction to the Bootstrap.* Chapman
    & Hall/CRC.

11. Lakens, D. (2017). Equivalence Tests: A Practical Primer for t Tests, Correlations,
    and Meta-Analyses. *Social Psychological and Personality Science*, 8(4), 355-362.
    DOI: 10.1177/1948550617697177

12. Vargha, A., & Delaney, H.D. (2000). A Critique and Improvement of the CL Common
    Language Effect Size Statistics of McGraw and Wong. *Journal of Educational and
    Behavioral Statistics*, 25(2), 101-132.

13. Corani, G., Benavoli, A., Demsar, J., Mangili, F., & Zaffalon, M. (2017).
    Statistical comparison of classifiers through Bayesian hierarchical modelling.
    *Machine Learning*, 106(11), 1817-1837. DOI: 10.1007/s10994-017-5641-9

14. Smith, L.J., et al. (2024). The Accuracy and Reproducibility of Lipari-Szabo Order
    Parameters From Molecular Dynamics. *Journal of Physical Chemistry B*, 128(44),
    10813-10822.

15. Terpilowski, M.A. (2019). scikit-posthocs: Pairwise multiple comparison tests in
    Python. *Journal of Open Source Software*, 4(36), 1169. DOI: 10.21105/joss.01169

16. Turner, H.L., van Etten, J., Firth, D., & Kosmidis, I. (2020). Modelling rankings
    in R: the PlackettLuce package. *Computational Statistics*, 35, 1027-1057. DOI:
    10.1007/s00180-020-00959-3

17. Maystre, L., & Grossglauser, M. (2015). Fast and Accurate Inference of Plackett-Luce
    Models. *Advances in Neural Information Processing Systems*, 28.

18. Herbold, S. (2020). autorank: A Python package for automated ranking of classifiers.
    *Journal of Open Source Software*, 5(48), 2173. DOI: 10.21105/joss.02173

19. Cavender, C.E., Case, D.A., et al. (2025). Structure-Based Experimental Datasets for
    Benchmarking Protein Simulation Force Fields. *Living Journal of Computational
    Molecular Science*, 6(1), e3871. DOI: 10.33011/livecoms.6.1.3871

20. Kendall, M.G. (1948). *Rank Correlation Methods.* Charles Griffin & Co.

21. Trbovic, N., Kim, B., Friesner, R.A., & Palmer, A.G. (2008). Structural analysis
    of protein dynamics by MD simulations and NMR spin-relaxation. *Proteins*, 71(2),
    684-694.

22. Nature Portfolio. (2025). Reporting Summary and Statistics Checklist. *Nature
    Computational Science* author guidelines.

23. Boulesteix, A.L., et al. (2024). A plea for taking all available clinical
    information into account when assessing the predictive value of omics data.
    *BMC Medical Research Methodology* (updated review of benchmark reporting practices).

24. Robertson, J.C., Hurley, M.G., & Spring-Robinson, C. (2015). Assessing the Current
    State of Amber Force Field Modifications for DNA. *Journal of Chemical Theory and
    Computation*, 11(3), 951-960.

25. Schuirmann, D.J. (1987). A comparison of the Two One-Sided Tests Procedure and the
    Power Approach for assessing the equivalence of average bioavailability. *Journal
    of Pharmacokinetics and Biopharmaceutics*, 15(6), 657-680.

26. Brini, E., et al. (2023). An Imbalance in the Force: The Need for Standardized
    Benchmarks for Molecular Simulation. *Journal of Chemical Theory and Computation*,
    19(5), 1325-1335. DOI: 10.1021/acs.jctc.2c00982

27. Phipson, B., & Smyth, G.K. (2010). Permutation P-values Should Never Be Zero:
    Calculating Exact P-values When Permutations Are Randomly Drawn. *Statistical
    Applications in Genetics and Molecular Biology*, 9(1), Article 39.

28. Shen, Y., & Bax, A. (2010). SPARTA+: a modest improvement in empirical NMR chemical
    shift prediction. *Journal of Biomolecular NMR*, 48(1), 13-22.

29. Mannan, S., et al. (2025). UniFFBench: Evaluating Universal Machine Learning Force
    Fields Against Experimental Measurements. *arXiv*, 2508.05762.

30. Kovacs, D.P., et al. (2025). MACE-OFF: Short-Range Transferable Machine Learning
    Force Fields for Organic Molecules. *JACS*, 147(21).

31. Tian, C., et al. (2020). ff19SB: Amino-Acid-Specific Protein Backbone Parameters.
    *Journal of Chemical Theory and Computation*, 16(1), 528-552.

32. Huang, J., et al. (2017). CHARMM36m: an improved force field for folded and
    intrinsically disordered proteins. *Nature Methods*, 14(1), 71-73.
