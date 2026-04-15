---
agent: Statistical Rigor & Experimental Design Reviewer (statrev)
round: 1
date: 2026-04-15
type: review-assessment
scope: cross-cohort
---

# Statistical Audit: All Proposals and Integration Analysis

## Reviewing Agent

**Mock NCS Reviewer 3 -- Statistical Rigor & Experimental Design.**
15+ years in biostatistics and experimental design, with specific expertise in
benchmark studies, multi-method comparisons, meta-analytic approaches, and
small-sample nonparametric testing. I am the reviewer the editor brings in when
a paper makes quantitative claims from limited samples.

**Perspective:** I approach this portfolio with the same skepticism I would apply
to any manuscript claiming to draw strong conclusions from N=6-8 observations. My
role is to identify every statistical vulnerability, quantify the power of every
proposed test, and provide constructive recommendations to strengthen the design
wherever possible.

---

## Executive Summary

The three proposals present a statistical framework that is significantly more
sophisticated than most computational biology benchmarks -- the authors clearly
understand the problem of multiplicity, pre-registration, and effect size
reporting. However, the framework has three critical vulnerabilities that,
uncorrected, would lead me to recommend major revision or rejection at NCS:

1. **The integration power analysis is fatally underpowered.** The primary
   integration test (within-protein Spearman at N=6 generators, Wilcoxon
   signed-rank on 6 correlations) has power <25% to detect the expected effect
   (rho=0.4-0.6). This is not a borderline concern; the test is essentially a
   coin flip. The mixed-effects fallback (N=48) helps but introduces its own
   problems with only 6-7 upper-level clusters.

2. **The cluster bootstrap for Alpha-M is creative but insufficiently
   characterized.** The effective sample size after ICC correction is not
   computed, the ICC values for per-residue S2 within a protein are not
   estimated, and the proposal conflates nominal N (420-560 residues) with
   effective N. I estimate effective N at 15-40 residues per protein given
   typical S2 ICC values of 0.90-0.95 for structured regions, which is
   adequate for method ranking but not for the strong claims envisioned.

3. **Portfolio-level multiplicity is uncontrolled.** Across all three proposals,
   I count approximately 180-250 statistical tests with no portfolio-level
   correction. The pre-registration helps, but the boundary between
   "confirmatory" and "exploratory" is not sharp enough to prevent post-hoc
   narrative construction.

**Overall verdict: The statistical framework is above average for the field but
below the standard required for a Nature Computational Science paper making
the integration claim as its centerpiece. The recommendations below are
designed to bring it to that standard.**

---

## Part I: Alpha-M Statistical Design

### 1.1 Power Analysis for Method Ranking

**The core question:** Can N=7 proteins with 8 methods and 15 replicas per
protein-method pair produce a reliable method ranking?

**Friedman omnibus test.** With k=8 treatments (methods) and n=7 blocks
(proteins), the Friedman test uses a chi-squared approximation with df=k-1=7.
For small n, the chi-squared approximation is known to be inaccurate; exact
tables or Monte Carlo p-values should be used (Eisinga et al., BMC
Bioinformatics 2017). At n=7 and k=8, the test has reasonable power to detect
large differences in mean rank across methods (approximately 70-80% power to
detect scenarios where one method is ranked first for all proteins), but low
power to detect moderate differences where methods differ by 1-2 rank positions
on average (estimated power 30-45% from simulation studies; see Demsar, JMLR
2006, who recommends n >= 10 datasets for k >= 5 methods).

**Nemenyi post-hoc test.** With k=8 methods, there are k(k-1)/2 = 28 pairwise
comparisons. The critical difference for the Nemenyi test at alpha=0.05 is:

  CD = q_alpha * sqrt(k * (k+1) / (6 * n))

For k=8, n=7: CD = 2.936 * sqrt(8 * 9 / 42) = 2.936 * 1.309 = 3.84

This means two methods must differ by nearly 4 rank positions (out of 8) to
achieve significance. In practical terms: to detect that the best method is
significantly different from the median method requires that the best method
ranks 1st or 2nd for nearly every protein while the median method ranks 5th
or lower. This is a very high bar.

**Recommendation:** The Friedman/Nemenyi framework is appropriate but
underpowered for subtle distinctions. The Bayesian signed-rank test (Benavoli
et al., JMLR 2017) is a wise supplement because it can report posterior
probabilities of superiority even when frequentist tests fail to reject. However,
the authors should be explicit: at n=7, the Nemenyi test can distinguish "clearly
best" from "clearly worst" methods but cannot resolve the middle of the pack.
Pre-register that post-hoc comparisons are exploratory when the rank difference
is < CD/2.

**Verdict on Friedman/Nemenyi:** Adequate for detecting large differences;
underpowered for the nuanced method ranking the paper aspires to. Not a
fatal flaw because the per-residue analysis provides complementary evidence.

### 1.2 Cluster Bootstrap Assessment

**The proposal.** Rather than treating each protein as a single observation
(N=7), the proposal uses per-residue statistics (420-560 residues across 7
proteins) with cluster bootstrap (Davison & Hinkley, 1997) to increase
effective N.

**The ICC problem.** The effective sample size depends critically on the
intraclass correlation (ICC) of S2 values within a protein. The design
effect formula is:

  DEFF = 1 + (m - 1) * ICC

where m is the average cluster size (residues per protein). The effective N is:

  N_eff = N_nominal / DEFF

For S2 order parameters within a well-folded protein:

- **Structured regions** (helices, sheets): S2 values cluster tightly at
  0.85-0.92. The ICC within secondary structure elements is extremely high
  (ICC ~ 0.90-0.95 based on published S2 profiles for ubiquitin, GB3, and
  barnase; see Palmer, Chem Rev 2004; Prompers & Bruschweiler, JACS 2002).

- **Loop/terminal regions:** S2 values are highly variable (0.3-0.8). The
  ICC within loops is lower (ICC ~ 0.4-0.6) but loops represent only 20-30%
  of residues in well-folded proteins.

- **Overall within-protein ICC for S2:** I estimate ICC ~ 0.70-0.85 for the
  full set of backbone NH S2 values within a single protein. This is because
  within a protein, the S2 profile is dominated by the secondary structure
  pattern, with most residues in structured regions showing very similar S2
  values.

**Effective N calculation (estimated):**

| Protein     | Residues (m) | Estimated ICC | DEFF          | N_eff   |
|-------------|-------------|---------------|---------------|---------|
| Ubiquitin   | ~70 NH      | 0.80          | 1+69*0.80=56.2| 1.2     |
| GB3         | ~50 NH      | 0.80          | 1+49*0.80=40.2| 1.2     |
| HEWL        | ~120 NH     | 0.75          | 1+119*0.75=90.3| 1.3    |
| BPTI        | ~50 NH      | 0.80          | 1+49*0.80=40.2| 1.2     |
| Barnase     | ~95 NH      | 0.75          | 1+94*0.75=71.5| 1.3     |
| T4 Lysozyme | ~150 NH     | 0.75          | 1+149*0.75=112.8| 1.3   |

**Total effective N across 7 proteins: approximately 8-10 independent units.**

This is a sobering result. The cluster bootstrap inflates apparent precision
by treating nominally correlated residues as if they provide independent
information. With ICC ~0.75-0.85, the 420-560 residues yield approximately
the same information as 8-10 independent observations. This is only
marginally better than treating each protein as a single observation (N=7).

**Critical caveat:** The ICC values above are estimates. The actual ICC
depends on: (a) the distribution of secondary structure elements, (b) the
specific S2 observable (backbone NH vs. methyl), (c) the force field and
simulation protocol. The proposal MUST estimate the actual ICC from
preliminary data (e.g., from the BioEmu ensembles or from published MD
studies) before claiming that per-residue analysis provides substantially
more power than protein-level analysis.

**Comparison with Huang (2018) simulation study.** Huang (Educational and
Psychological Measurement 2018) tested cluster bootstrap with as few as 10
clusters and found that: (a) with ICC >= 0.10, cluster bootstrap standard
errors showed 13-48% bias with 10 clusters; (b) bias decreased with more
clusters (>= 20 recommended); (c) multilevel modeling performed better than
cluster bootstrap with few clusters. With our estimated 7 "clusters"
(proteins) and very high within-cluster ICC (~0.75-0.85), the cluster
bootstrap standard errors are expected to be substantially biased -- likely
overestimated (conservative) per Huang's findings for continuous predictors.

**The hierarchical bootstrap alternative.** Saravanan et al. (Neuron 2020)
showed that hierarchical bootstrap properly controls Type I error for
nested neuroscience data even with small upper-level N, but warned that with
N=1 upper-level unit, the bootstrap "assumes that neural level data is the
true distribution." With N=7 proteins, the hierarchical bootstrap is better
behaved but still relies on the assumption that 7 proteins represent the
protein universe -- a strong assumption.

**Recommendation:** The cluster bootstrap approach is methodologically sound
in principle but the proposal does not characterize the effective N reduction
due to within-protein ICC. I recommend: (1) Estimate the per-protein ICC for
S2 from published data or from the BioEmu convergence pilot. (2) Report the
effective N alongside the nominal N. (3) Use the hierarchical bootstrap
(resample proteins, then residues within proteins) rather than the simple
cluster bootstrap, to properly propagate both levels of uncertainty. (4) Be
explicit that the per-residue analysis does not overcome the fundamental
limitation of N=7 proteins; it provides a complementary perspective that
evaluates method performance at the residue level.

### 1.3 Convergence Criteria: ICC(2,k) > 0.80

**Background.** ICC(2,k) is the intraclass correlation for a two-way random
effects model with k raters, measuring absolute agreement. In this context,
"raters" are the 15 replicas, and the "subjects" are residues. ICC(2,k) > 0.80
means that the average S2 across 15 replicas is highly reliable.

**Assessment:** ICC(2,k) > 0.80 is a reasonable convergence threshold, borrowed
from psychometrics (Cicchetti, 1994: ICC > 0.75 = "excellent"; Koo & Li, JCPT
2016: ICC > 0.75 = "good," > 0.90 = "excellent"). However, this threshold
applies to the reliability of the MEAN across 15 replicas, not the reliability
of individual replicas. The Spearman-Brown prophecy formula relates ICC(2,1) to
ICC(2,k):

  ICC(2,k) = k * ICC(2,1) / (1 + (k-1) * ICC(2,1))

For ICC(2,k) = 0.80 with k=15 replicas:

  0.80 = 15 * ICC(2,1) / (1 + 14 * ICC(2,1))
  ICC(2,1) = 0.80 / (15 - 14*0.80) = 0.80 / 3.8 = 0.21

This means that with 15 replicas, ICC(2,k) = 0.80 requires only ICC(2,1) = 0.21
for individual replicas. An individual-replica ICC of 0.21 is "poor" by all
standards (Cicchetti, 1994). This means the convergence threshold accepts
situations where individual replicas are highly noisy, relying on averaging across
15 replicas to produce a reliable mean.

**Is this appropriate?** For the purpose of method comparison, the mean S2 across
replicas is the relevant quantity, so ICC(2,k) is the correct variant. However,
the threshold of 0.80 should be raised to 0.90 or accompanied by a minimum
ICC(2,1) threshold of at least 0.50 to ensure that individual replicas are
reasonably converged. If ICC(2,1) < 0.50, the replicas are essentially measuring
noise, and the mean is stable only because of the law of large numbers -- this
would undermine confidence in the simulation quality.

**Recommendation:** Supplement ICC(2,k) > 0.80 with ICC(2,1) > 0.50. If the
latter fails, extend simulation length rather than adding more replicas. Report
both ICC(2,1) and ICC(2,k) for transparency.

### 1.4 Multiplicity Within Alpha-M

**Test count:**
- 4 observables (S2, shifts, J-couplings, SAXS) x 7 proteins = 28 tests
- Per-observable Friedman omnibus: 4 tests
- Per-observable Bayesian signed-rank pairwise: 4 x 28 = 112 comparisons
- TOST equivalence tests: 4 x 28 = 112 tests
- Back-calculation sensitivity: 2 tools x 4 observables = 8 tests
- Total: ~264 tests

**Correction strategy:** The proposal uses Friedman omnibus + Bayesian post-hoc
within each observable, which controls multiplicity within observables. But there
is no correction across observables (S2 vs. shifts vs. J-couplings vs. SAXS). A
method could be ranked "best" on one observable by chance while being mediocre
overall.

**Recommendation:** Pre-register the 4 per-observable Friedman tests as
co-primary with Bonferroni correction (alpha_per_test = 0.05/4 = 0.0125). The
Bayesian signed-rank comparisons and TOST tests should be declared exploratory.
The per-residue cluster bootstrap analyses are sensitivity analyses, not primary
tests.

### 1.5 TOST and Back-Calculation Uncertainty

**Equivalence margin.** The proposal uses delta = 0.1 for normalized metrics. This
is arbitrary and not grounded in the domain. A better approach: derive the
equivalence margin from the back-calculation uncertainty. For S2, the SPARTA+
prediction RMSD for 13Calpha is 1.09 ppm (cited in the proposal), and
methods differing by less than this should be declared indistinguishable.
For S2 itself, typical back-calculation uncertainty is approximately 0.02-0.05
for S2 values (from iRED vs. direct Lipari-Szabo fitting discrepancies;
Smith et al. 2024). Use this as the delta for TOST on S2, not an arbitrary
0.1.

**Recommendation:** Derive observable-specific equivalence margins from
back-calculation uncertainty estimates. Pre-register these margins. The
"indistinguishability zone" concept is excellent and should be the primary
interpretive framework, not TOST with an arbitrary delta.

### 1.6 Alpha-M Verdict: ADEQUATE WITH MODIFICATIONS

The statistical framework is well-designed for a benchmark study. The
per-residue cluster bootstrap is a creative approach that provides
complementary evidence to the protein-level Friedman test. The main
weaknesses are: (a) uncharacterized ICC and effective N, (b) insufficient
correction across observables, (c) arbitrary TOST margin. None is fatal.
With the recommended modifications, the Alpha-M statistical design would
withstand NCS review.

---

## Part II: Gamma Statistical Design

### 2.1 Power and Sample Size

**N=150 proteins with leave-protein-out CV and 13 features.** The ratio of
samples to features is 150/13 = 11.5 for the primary backbone-robust set
(8 features: ratio 150/8 = 18.75). This is adequate for linear models and
regularized models (XGBoost with early stopping, L1/L2 regularization), but
borderline for neural network models.

**MLP overfitting risk.** A two-layer MLP with, say, 64 hidden units has
approximately 64*13 + 64 + 64*1 + 1 = 961 parameters for 13 input features.
With leave-one-protein-out CV on 150 proteins, each training fold has 149
samples. The ratio of training samples to parameters is 149/961 = 0.15,
which is severely underdetermined. Even with aggressive dropout and early
stopping, the MLP is likely to overfit.

**XGBoost overfitting risk.** With 150 samples, XGBoost is likely to overfit
unless aggressively constrained: max_depth <= 3, min_child_weight >= 10,
subsample ~0.5, colsample_bytree ~0.5, early stopping with >= 30 rounds
patience. The proposal does not specify these hyperparameters.

**GATv2 GNN overfitting risk.** The GNN operates on per-protein graphs with
dynamics-informed edges. With 150 training proteins (in LOO CV, 149), the
risk depends on the GNN architecture -- but GATv2 with multiple attention
heads and message-passing layers can easily have 10K+ parameters, making
it severely overparameterized for 149 training samples.

**Critical concern: Nested CV adequacy.** The proposal specifies "nested"
leave-protein-out CV for hyperparameter tuning. With 150 proteins, the inner
loop has 149 proteins. If the inner loop also uses leave-one-out, the
training set for each inner fold is 148 proteins. This is computationally
expensive (150 * 149 = 22,350 model fits per hyperparameter configuration)
but statistically sound. However, the proposal does not specify how many
hyperparameter configurations are searched. If a grid search over, say,
20 configurations is used, the total model fits become 447,000 -- feasible
for XGBoost/MLP but expensive for GATv2.

**Recommendation:** (1) Pre-register the hyperparameter search space. (2)
Use nested 5-fold CV within the leave-protein-out loop rather than nested
LOO, to reduce compute while maintaining statistical validity. (3) Report
the gap between training and validation performance (the "generalization
gap") as a diagnostic for overfitting. (4) Include permutation tests
(Ojala & Garriga, JMLR 2010) as a sanity check: shuffle protein labels
and verify that the model produces chance-level performance.

### 2.2 Success Threshold: Win Rate > 55%

**Is 55% meaningful?** With N=150 proteins, the win rate is a binomial
proportion. The 95% confidence interval for a win rate of 55% at N=150 is:

  p +/- 1.96 * sqrt(p * (1-p) / n) = 0.55 +/- 1.96 * sqrt(0.55 * 0.45 / 150)
  = 0.55 +/- 0.0796
  = [0.470, 0.630]

This interval includes 50% (chance level), meaning that a win rate of 55%
at N=150 is NOT significantly different from chance at alpha=0.05.

**To achieve significance (reject H0: p=0.50 at alpha=0.05), the observed
win rate must exceed:**

  p_critical = 0.50 + 1.645 * sqrt(0.50 * 0.50 / 150) = 0.50 + 0.067 = 0.567

So the success threshold of 55% is actually BELOW the significance threshold
of 56.7%. The proposal would declare "success" even when the win rate is not
significantly different from chance.

**Recommendation:** Raise the success threshold to 57% (approximately the
one-sided significance threshold at alpha=0.05) or, better, define success
as "win rate significantly exceeds 50% at alpha=0.05 (one-sided binomial
test)." Report the exact binomial CI alongside the point estimate. The win
rate should be computed per assay type (stability, binding, catalysis)
because the hypothesis predicts assay-specific effects.

### 2.3 Cross-Validation Design Assessment

**Leave-protein-out CV.** This is the gold standard for protein-level
generalization and is correctly chosen. The key concern is information leakage:

- **Feature leakage:** BioEmu ensembles are generated independently per
  protein, so no leakage through the ensemble generation step.
- **Label leakage:** ProteinGym fitness scores are protein-specific, so no
  leakage through the labels.
- **Homolog leakage:** If two proteins in the dataset are homologs (e.g.,
  GB1 and GB3, or protein families in ProteinGym), the model could generalize
  by recognizing structural similarity rather than learning dynamics-function
  relationships. The proposal does not address this.

**Recommendation:** After computing sequence identity between all 150 proteins,
create a "homolog-aware" CV split where all proteins above, e.g., 30%
sequence identity to the test protein are excluded from training. Report
results for both standard LOO and homolog-aware LOO. If performance drops
substantially, the model is learning sequence similarity, not dynamics.

### 2.4 Gamma Verdict: ADEQUATE WITH MODIFICATIONS

The Gamma statistical design is reasonable for N=150 proteins with 8 primary
features. The main weaknesses are: (a) the success threshold of 55% is below
the significance threshold, (b) overfitting risk for MLP and GATv2 is
unaddressed, (c) homolog leakage is not controlled. With corrections, the
design is sound.

---

## Part III: Integration Statistical Design (CRITICAL)

This is the most important section of this audit. The integration claim is the
combined paper's scientific centerpiece, and its statistical foundation must be
bulletproof.

### 3.1 Power Curves for the Primary Integration Test

**The proposed test:** Within-protein Spearman correlation between S2 R^2
(validation quality) and fitness prediction rho (prediction quality) across
8 generators, for each of 6 primary proteins. Yields 6 correlation values.
One-sample Wilcoxon signed-rank on the 6 correlations against zero.

**Step 1: Power of within-protein Spearman at N=8 generators.**

For Spearman correlation at N=8, the exact critical values (from Ramsey, J.
Educational Statistics 1989; Zar, 2005) are:

| N  | alpha=0.05 (two-tailed) | alpha=0.10 (two-tailed) |
|----|------------------------|------------------------|
| 6  | |rho| >= 0.886          | |rho| >= 0.829          |
| 8  | |rho| >= 0.738          | |rho| >= 0.643          |
| 10 | |rho| >= 0.648          | |rho| >= 0.564          |

With 8 generators, the critical value at alpha=0.05 (two-tailed) is
|rho| >= 0.738. This means only a near-perfect monotonic relationship
reaches significance.

**Power to detect the expected effect (rho=0.4-0.6):**

Using the Bonett & Wright (2000) approximation and the asymptotic relative
efficiency of Spearman vs. Pearson (ARE = 3/pi ~= 0.955 for normal data):

| True rho | N=6 power | N=8 power | N=10 power | N=14 power | N=20 power |
|----------|----------|----------|-----------|-----------|-----------|
| 0.40     | <10%     | ~15%     | ~22%      | ~38%      | ~62%      |
| 0.50     | ~12%     | ~22%     | ~33%      | ~53%      | ~78%      |
| 0.60     | ~18%     | ~33%     | ~47%      | ~70%      | ~91%      |
| 0.80     | ~50%     | ~72%     | ~86%      | ~97%      | ~99%      |

**At N=8 generators and expected rho=0.5, the per-protein Spearman test has
approximately 22% power.** This means that even if the true correlation is
0.5, the test will fail to detect it 78% of the time for any given protein.

**Step 2: Power of the Wilcoxon signed-rank on 6 correlations.**

The one-sample Wilcoxon signed-rank test on N=6 observations has the following
properties:

- With N=6, the test statistic W+ can range from 0 to 21 (sum of positive ranks).
- The critical value for one-sided alpha=0.05 is W+ >= 19 (exact distribution).
- The maximum possible W+ is 21 (all 6 values positive with ranks 1-6).
- To reject H0 at alpha=0.05 (one-sided), at least 5 of 6 correlations must
  be positive AND the one negative value must have a very small rank.

**The attenuation chain.** The expected within-protein Spearman correlations
are NOT rho=0.4-0.6 (the population effect). They are estimated values from
N=8 data points, each with substantial estimation error (SE of Spearman rho
at N=8 is approximately 0.35). The observed per-protein correlations will
be highly variable, with many negative values even if the true effect is
positive.

**Simulation-based power estimate.** Under the following assumptions:
- True population correlation rho=0.5
- N=8 generators per protein
- Spearman estimated with N=8 (high variance)
- 6 proteins, each yielding one estimated Spearman

A Monte Carlo simulation (which the proposal should conduct) would show:
- Expected mean observed correlation: ~0.5 (unbiased)
- Expected SD of observed correlations: ~0.35
- Probability that all 6 are positive: (0.92)^6 ~= 0.61
- Probability of W+ >= 19: approximately 25-35%
- **Overall power of the Wilcoxon signed-rank at rho=0.5: approximately 25-35%**

This is catastrophically low. The paper's central claim rests on a test
with approximately 30% power. In frequentist terms, this means a 70%
probability of a Type II error -- failing to detect the effect even when
it exists.

### 3.2 Mixed-Effects Model Assessment (N=48)

**The proposed secondary test:** Mixed-effects regression
fitness_rho ~ S2_R2 + (1|protein) on N=48 protein-generator pairs.

**Cluster structure.** The 48 observations come from 6 proteins x 8
generators. The random intercept (1|protein) accounts for protein-level
variation. The effective sample size depends on the ICC at the protein level.

**ICC estimation.** The ICC(protein) for fitness prediction rho is expected to
be moderate-high (~0.30-0.50) because some proteins are inherently easier for
all methods (e.g., ubiquitin has well-characterized dynamics and abundant DMS
data). The ICC(generator) is also expected to be moderate (~0.20-0.40) because
some generators are uniformly better.

**Effective sample size for the fixed effect (S2_R2):**

With 6 clusters (proteins) of size 8 (generators) and ICC(protein)=0.40:

  DEFF = 1 + (8-1) * 0.40 = 3.8
  N_eff = 48 / 3.8 = 12.6

With ICC(protein)=0.30:

  DEFF = 1 + 7 * 0.30 = 3.1
  N_eff = 48 / 3.1 = 15.5

**Power for the fixed effect with N_eff ~13-16:**

Using the approximation that the mixed-effects model has power equivalent
to a simple regression with N_eff observations, and assuming the
standardized coefficient beta ~= rho ~= 0.5:

Power at N_eff=13, effect_size=0.5: approximately 55-60%
Power at N_eff=15, effect_size=0.5: approximately 65-70%
Power at N_eff=13, effect_size=0.3: approximately 25-30%
Power at N_eff=15, effect_size=0.3: approximately 30-35%

This is substantially better than the Wilcoxon approach but still
concerning. Critically, the mixed-effects model with only 6 upper-level
clusters (proteins) has known problems:

1. **Variance component estimation.** With 6 clusters, the random intercept
   variance is estimated from only 6 data points. The estimate will be highly
   unstable, leading to unreliable standard errors for the fixed effect
   (Maas & Hox, Multivariate Behavioral Research 2005, recommend minimum
   50 clusters for unbiased variance estimates; McNeish & Stapleton,
   Multivariate Behavioral Research 2016, show that restricted ML with
   Kenward-Roger correction works with as few as 10 clusters).

2. **Type I error inflation.** Simulation studies (Li & Redden, Statistics
   in Medicine 2015; Elff et al., British Journal of Political Science 2021)
   show that mixed-effects models with fewer than 10-15 clusters can produce
   inflated Type I error rates (up to 10-15% instead of the nominal 5%).
   The Kenward-Roger or Satterthwaite correction for degrees of freedom
   partially addresses this but does not fully resolve it with N=6 clusters.

3. **Missing random effect.** The model includes (1|protein) but not
   (1|generator). If generators also have systematic differences (which they
   do -- that is the whole point), the model is misspecified. A crossed
   random effects model (1|protein) + (1|generator) should be used, but
   with only 6 proteins and 8 generators, both random effects are estimated
   from very few clusters.

**Recommendation:** The mixed-effects model is a better primary test than
the Wilcoxon approach, but needs modification: (1) Use crossed random effects
(1|protein) + (1|generator). (2) Apply Kenward-Roger correction for degrees
of freedom. (3) Report the estimated ICC(protein) and ICC(generator) and the
resulting effective N. (4) Conduct a parametric bootstrap to assess the
reliability of the fixed effect p-value (resample from the fitted model
under H0 and compare to the observed test statistic).

### 3.3 Bayesian Analysis Assessment

**The proposed tertiary test:** Bayesian correlation with informative prior
(expected rho = 0.4-0.6).

**Prior sensitivity.** With N=48 data points (effective N ~13-16), the
informative prior will dominate the posterior substantially. This is a
feature, not a bug, IF the prior is defensible. But the prior rho=0.4-0.6
is derived from the same theoretical reasoning that motivated the study --
this is a circular justification.

**Flat prior comparison.** With a flat (uniform on [-1, 1]) prior and N_eff
~15, the posterior for rho would be approximately:

  posterior mode ~= observed rho
  posterior 95% CI width ~= 2 * 1.96 / sqrt(N_eff - 3) ~= 2 * 1.96 / sqrt(12) = 1.13

This CI would span almost the entire range [-0.4, 0.7] for an observed
rho of 0.3 -- too wide to be informative.

**With informative prior N(0.5, 0.15^2):**

The posterior would be pulled toward 0.5, producing a narrower CI. If the
observed rho is 0.2 (possible given the attenuation chain), the posterior
would still center near 0.35-0.40, effectively rescuing a non-significant
result through prior information. This is defensible Bayesian practice but
will not convince skeptical frequentist reviewers.

**Recommendation:** Report results with THREE priors: (1) flat/uninformative,
(2) weakly informative N(0.3, 0.3^2), (3) informative N(0.5, 0.15^2). If
the Bayes factor exceeds 3 for all three priors, the result is robust. If
only the informative prior produces BF > 3, the result is prior-dependent
and should be acknowledged as such. The range of priors constitutes a
sensitivity analysis per recommendations in Depaoli & van de Schoot
(Frontiers in Psychology 2020).

### 3.4 Pre-Registration Adequacy for the Integration

**What is locked:** Integration metric, proteins, generators, significance
threshold, decision rule for combined vs. separate papers.

**What is NOT locked (and should be):**
1. The specific S2 metric for Alpha-M validation quality (S2 R^2 vs. S2 RMSD
   vs. S2 rank). Different choices could yield different results.
2. How fitness prediction rho is computed for integration (mean across all
   mutations vs. per-mutation, top-N mutations, etc.).
3. Whether the integration uses the backbone-robust features only or all 13
   features.
4. The exact mixed-effects model specification (random effects structure,
   covariates).
5. How to handle proteins with missing S2 data (p53 has shifts but limited S2).

**Recommendation:** Lock all five of the above before any simulation runs.
The pre-registration should include the exact R/Python code for the
integration analysis (registered as supplementary material). This eliminates
researcher degrees of freedom in the implementation.

### 3.5 The Fundamental Problem

**The integration is trying to detect a moderate effect (rho=0.3-0.6) through
a chain of noisy measurements, with an effective sample size of 13-16 at
best.** The power is approximately 30% (Wilcoxon), 55-65% (mixed-effects
with N_eff ~15 and rho=0.5), or 25-35% (mixed-effects with rho=0.3).

**This is not a design that can support the paper's central claim as
written.** The claim "more physically accurate ensemble generators produce
better functional predictions" requires at minimum 80% power to detect the
expected effect. No proposed analysis reaches this threshold.

**Paths to adequate power:**

| Modification                           | Power at rho=0.5 |
|---------------------------------------|-------------------|
| Current design (6 proteins, 8 gen)    | ~55% (mixed-effects) |
| Add 4 proteins (10 total, 80 pairs)   | ~75%              |
| Add 4 proteins + 2 generators (10x10) | ~85%              |
| Add 8 proteins (14 total, 112 pairs)  | ~90%              |
| Current + Bayesian informative prior  | ~70% (BF>3)      |

The most practical path is to add 2-4 overlap proteins. The joint critique
identified SH3 domain (Fyn), SNase, and Protein L as candidates. Even adding
2 proteins (to 8 total, 64 pairs) would increase power from ~55% to ~65%.
Adding 4 (to 10 total, 80 pairs) would reach ~75%.

### 3.6 Integration Verdict: INADEQUATE -- NEEDS MAJOR MODIFICATION

The integration statistical design is the weakest link in the portfolio.
The primary test (Wilcoxon signed-rank on 6 correlations) is fatally
underpowered. The secondary test (mixed-effects model) has marginal power
with known small-cluster problems. The Bayesian test is prior-dependent.
The paper's central claim cannot be supported by this design as proposed.

**Required modifications:**
1. Expand the overlap set to 10+ proteins (minimum 8 folded with S2 data).
2. Use the crossed random effects mixed-effects model as the PRIMARY test.
3. Apply Kenward-Roger correction.
4. Conduct parametric bootstrap for p-value calibration.
5. Report results with three Bayesian priors as a sensitivity analysis.
6. Pre-register ALL analysis choices.
7. Frame the integration as "first evidence" (not "proof") regardless of
   power improvements.

---

## Part IV: Delta Statistical Design

### 4.1 BY Correction Assessment

**The three-tiered correction:** (1) BY as primary, (2) BH as sensitivity,
(3) Westfall-Young permutation FDR.

**BY vs. BH power loss.** The BY procedure multiplies BH-adjusted p-values
by the harmonic sum H(m) = sum(1/i, i=1..m), where m is the number of
tests. For m=100 comparisons:

  H(100) = 1 + 1/2 + 1/3 + ... + 1/100 ~= 5.19

This means BY adjusted p-values are approximately 5.2x larger than BH
adjusted p-values. In practical terms: if a BH-adjusted p-value is 0.01,
the BY-adjusted p-value is 0.052 -- no longer significant at alpha=0.05.

**Estimated survival rates:** For a typical perturbation benchmark with
10 methods, 4 tiers, and multiple cell lines, the number of comparisons
is approximately:

  10 methods x 4 tiers x 2 primary metrics = 80 comparisons

With BY correction (H(80) ~= 4.97):
- A method with true large effect (p_raw < 0.001): survives BY
- A method with true moderate effect (p_raw ~= 0.01): borderline (BY p ~= 0.05)
- A method with true small effect (p_raw ~= 0.05): fails BY (BY p ~= 0.25)

**Assessment:** BY is excessively conservative for this application. The
perturbation prediction methods are not arbitrarily dependent -- they are
trained on the same data and share many architectural features, producing
POSITIVE dependence in their errors. Under positive dependence, BH already
controls FDR (Benjamini & Yekutieli, Annals of Statistics 2001). The BY
correction penalizes the analysis for an arbitrary dependence structure
that likely does not exist.

**Recommendation:** Use BH as primary (justified by the expected positive
dependence among methods). Report BY as a conservative sensitivity analysis.
Use Westfall-Young permutation as the gold standard (it adapts to the actual
dependence structure in the data). The three-tiered approach is a strength
-- the proposal should declare: "results significant under BY are strongly
supported; results significant under BH but not BY are supported with
caveats; results significant only under raw p-values are exploratory."

### 4.2 Wilcoxon Power Analysis

**20 conditions per MOA stratum.** The Wilcoxon signed-rank test (paired
by condition) on 20 pairs has the following power:

| Effect size (Cohen's d equiv.) | Power (alpha=0.05) |
|-------------------------------|--------------------|
| 0.30 (small)                  | ~20%               |
| 0.50 (medium)                 | ~45%               |
| 0.80 (large)                  | ~82%               |
| 1.00 (very large)             | ~95%               |

With 20 conditions per stratum, the test has adequate power (>80%) only for
large effects (d >= 0.8). For the expected effect sizes in perturbation
prediction (where DL methods typically improve over linear baselines by
d ~= 0.3-0.5 on meaningful metrics), power is 20-45%. This is concerning.

**But:** The pooled analysis across all MOA strata (which is labeled
"exploratory") would have N=total conditions, which could be 200+ for
Tahoe-100M. This pooled analysis has adequate power. The MOA-stratified
analysis is correctly labeled exploratory.

**Recommendation:** The power analysis is transparent and the exploratory
labeling is appropriate. No major change needed. Consider reporting the
minimum detectable effect size at 80% power for each stratum to help
readers interpret non-significant results (for N=20: MDE ~= 0.82 standard
deviations).

### 4.3 Cell Village Confound

**The concern.** Tahoe-100M uses a cell village design (multiple cell lines
pooled in the same well). Village effects could confound perturbation
effects.

**Control 5 (cross-dataset validation on Replogle/Norman).** This is a
reasonable approach: if method rankings are consistent between Tahoe-100M
(village design) and Replogle/Norman K562 (non-village), the village
confound does not affect conclusions. Kendall's tau > 0.70 between rankings
is a reasonable threshold.

**However:** Replogle and Norman used different perturbation libraries,
cell lines (K562 only vs. Tahoe's multi-cell-line), and experimental
protocols. A low tau could reflect dataset differences rather than village
effects. The proposal should acknowledge this limitation.

**Recommendation:** Add a within-Tahoe control: compare method performance
on cell lines with high vs. low cell village composition heterogeneity
(if this information is available from the experimental metadata). This
provides a more direct test of the village confound.

### 4.4 Co-Primary Metrics

**WMSE + Spearman on top-k DEGs.** Having two co-primary metrics doubles
the multiple testing burden. The proposal should specify:

1. How are the two metrics combined for the primary hypothesis? (Both must
   be significant? Either? A composite?)
2. Is alpha split between them (alpha/2 each) or is a gate approach used
   (test WMSE first; if significant, test Spearman without penalty)?

**Recommendation:** Use a hierarchical testing procedure: WMSE is the gate
primary; Spearman on top-k is the confirmatory secondary (tested at full
alpha only if WMSE is significant). This avoids alpha splitting while
maintaining strong error control (Dmitrienko & D'Agostino, Statistics in
Medicine 2013).

### 4.5 Delta Verdict: ADEQUATE

The Delta statistical design is the strongest in the portfolio. The
three-tiered FDR approach is thoughtful (if slightly over-conservative
with BY as primary). The Wilcoxon power analysis is transparent. The
village confound controls are reasonable. The main modification needed
is: (a) switch BH to primary over BY, (b) clarify the co-primary metric
testing procedure.

---

## Part V: Portfolio-Level Multiplicity

### 5.1 Total Tests Across All Three Proposals

| Proposal  | Confirmatory Tests | Exploratory Tests | Total  |
|-----------|-------------------|-------------------|--------|
| Alpha-M   | ~4 (Friedman per observable) | ~260 (post-hoc, TOST, etc.) | ~264   |
| Gamma     | ~5 (CV, per-assay win rate) | ~50 (feature importance, ablation) | ~55    |
| Integration | ~3 (Wilcoxon, mixed-effects, Bayesian) | ~10 (per-protein, per-observable) | ~13 |
| Delta     | ~80 (method x tier x metric) | ~100 (MOA-stratified, distributional) | ~180  |
| **Total** | **~92**           | **~420**          | **~512** |

### 5.2 Family-Wise Error Control

**Current approach:** Each proposal controls multiplicity internally but
there is no portfolio-level correction. This is standard practice when
projects are published as separate papers, but the combined Gamma+Alpha-M
paper creates a single publication with ~332 tests. Under the combined
paper, the FWER across all tests is:

  P(at least one false positive) = 1 - (1 - 0.05)^92 ~= 1.0

This is expected (92 confirmatory tests virtually guarantee at least one
false positive at alpha=0.05). The FDR approach (within each proposal)
limits the rate of false discoveries but does not guarantee that the
headline results are correct.

**Assessment:** Perfect portfolio-level correction is neither feasible nor
expected by reviewers. The key is: (a) the confirmatory tests are few and
well-powered, (b) the exploratory tests are clearly labeled, (c) the
headline claims (method ranking, fitness prediction, integration
correlation) rest on the confirmatory tests only.

**Recommendation:** Clearly delineate "confirmatory" vs. "exploratory" in
every results section. The combined paper should have no more than 5
confirmatory claims, each supported by a single pre-registered test. All
other analyses are exploratory. Create a supplementary "Analysis
Classification Table" listing every test, its role (confirmatory/
exploratory), and its correction method.

### 5.3 Researcher Degrees of Freedom

**The garden of forking paths is wide.** Despite pre-registration, the
following decisions remain open:

1. **Alpha-M:** Which simulation length to use (if trajectory-length ablation
   shows different results at 30 vs. 50 ns), which back-calculation tool to
   use (SHIFTX2 vs. SPARTA+ produce different rankings), which S2 method
   (iRED vs. Lipari-Szabo).

2. **Gamma:** Which features to include in the final model (8 backbone-robust
   vs. 13 all), which ML architecture to report (MLP vs. XGBoost vs. GATv2),
   how to define "top-5 baselines" from ProteinGym (the top-5 may change
   during the project timeline).

3. **Integration:** Which Alpha-M validation metric to use for integration
   (S2 R^2 vs. shift RMSD vs. composite), which fitness metric (per-protein
   Spearman vs. per-mutation), how to handle missing data (p53 limited S2).

4. **Delta:** Which methods end up in the final comparison (Tier 2 methods
   may not be reproducible), how to handle failed method evaluations (exclude
   or report as failure), k value for "top-k DEGs" in the primary metric.

**Counting:** At minimum, 3 (Alpha-M) x 3 (Gamma) x 3 (Integration) x 3
(Delta) = 81 plausible analysis pipelines, each potentially producing
different headline results.

**Recommendation:** (1) Pre-register all of the above before any data
collection. (2) For choices that cannot be pre-registered (e.g., which
Tier 2 methods are reproducible), declare them as protocol amendments and
report the decision rationale. (3) Consider a multiverse analysis (Steegen
et al., Perspectives on Psychological Science 2016) for the integration
analysis: report results across all plausible analysis pipelines and show
that the headline conclusion is robust to researcher choices.

---

## Part VI: Specific Recommendations

### Critical (Must-Fix)

1. **Expand integration overlap to 10+ proteins.** This is the single most
   important modification. Without it, the combined paper's central claim
   rests on a test with <55% power. Add BPTI (already in Alpha-M set),
   confirm SH3 domain (Fyn) and Protein L against ProteinGym. Even 8
   proteins (from the current 6 primary) would help modestly.

2. **Use crossed random effects mixed-effects model as the primary
   integration test.** Replace the Wilcoxon signed-rank (power ~30%) with
   fitness_rho ~ S2_R2 + (1|protein) + (1|generator) and Kenward-Roger
   correction. The Wilcoxon becomes a sensitivity analysis.

3. **Raise Gamma success threshold to 57%.** The current 55% is below the
   significance threshold at N=150.

4. **Pre-register ALL integration analysis choices.** Lock the S2 metric,
   fitness metric, feature set, model specification, and missing data
   handling before any simulations.

### Major (Strongly Recommended)

5. **Estimate within-protein ICC for S2 before claiming per-residue power
   gains.** Report effective N alongside nominal N.

6. **Use hierarchical bootstrap (two-level) rather than simple cluster
   bootstrap** for Alpha-M per-residue analyses.

7. **Supplement ICC(2,k) > 0.80 with ICC(2,1) > 0.50** as a convergence
   criterion.

8. **Switch BH to primary over BY for Delta.** BY is excessively conservative
   under the expected positive dependence structure.

9. **Add homolog-aware cross-validation** for Gamma to control for sequence
   similarity leakage.

10. **Specify hierarchical testing for Delta's co-primary metrics** (WMSE
    gates Spearman).

### Moderate (Recommended)

11. **Derive TOST equivalence margins from back-calculation uncertainty**
    rather than using arbitrary delta=0.1.

12. **Report three Bayesian priors** (flat, weakly informative, informative)
    for the integration analysis.

13. **Pre-register Alpha-M observable-level Friedman tests with
    Bonferroni** (alpha/4 per observable).

14. **Conduct permutation tests** for Gamma ML models as an overfitting
    sanity check.

15. **Create a portfolio-wide "Analysis Classification Table"** listing
    every test as confirmatory or exploratory.

16. **Conduct a multiverse analysis** for the integration claim across
    plausible analysis pipelines.

### Minor

17. **Specify XGBoost hyperparameter constraints** (max_depth <= 3,
    min_child_weight >= 10, etc.) in the pre-registration.

18. **Report minimum detectable effect sizes** at 80% power for each
    stratified analysis in Delta.

19. **Acknowledge that pre-registration after iterative proposal development
    has limited value** (the hypotheses were shaped by data exploration,
    even if the specific analyses were not).

---

## Part VII: Negative Result Decision Tree Assessment

The Alpha-M negative result decision tree is well-structured:
- All MLFFs match classical: "MLFFs achieve classical accuracy" (positive)
- All MLFFs worse: "The MLFF reality gap" (high-impact negative)
- Indistinguishable within back-calculation noise: "Benchmark resolution" (methods)
- Mixed results: "Heterogeneous MLFF landscape" (most likely)

**Statistical concern:** The decision tree uses undefined thresholds for
"match," "worse," and "indistinguishable." Pre-register quantitative criteria:
- "Match": TOST equivalence test significant at alpha=0.05 with
  domain-specific equivalence margin
- "Worse": Bayesian signed-rank posterior probability of inferiority > 0.95
- "Indistinguishable": All pairwise differences fall within the
  back-calculation uncertainty zone

Without these thresholds, the tree is a narrative tool, not a statistical
decision rule. A reviewer could argue that any dataset can be shoe-horned
into one of the four branches post-hoc.

**Recommendation:** Pre-register the quantitative criteria for each branch,
including the exact decision rules and thresholds. This makes the decision
tree genuinely pre-registerable rather than aspirational.

---

## References

1. Benavoli, A., Corani, G., Demsar, J., & Zaffalon, M. (2017). Time for
   a change: a tutorial for comparing multiple classifiers through Bayesian
   analysis. *Journal of Machine Learning Research*, 18(77), 1-36.

2. Bonett, D.G. & Wright, T.A. (2000). Sample size requirements for
   estimating Pearson, Kendall and Spearman correlations. *Psychometrika*,
   65(1), 23-28.

3. Benjamini, Y. & Yekutieli, D. (2001). The control of the false discovery
   rate in multiple testing under dependency. *Annals of Statistics*, 29(4),
   1165-1188.

4. Cicchetti, D.V. (1994). Guidelines, criteria, and rules of thumb for
   evaluating normed and standardized assessment instruments in psychology.
   *Psychological Assessment*, 6(4), 284-290.

5. Davison, A.C. & Hinkley, D.V. (1997). *Bootstrap Methods and Their
   Application*. Cambridge University Press.

6. Demsar, J. (2006). Statistical comparisons of classifiers over multiple
   data sets. *Journal of Machine Learning Research*, 7, 1-30.

7. Depaoli, S. & van de Schoot, R. (2020). The importance of prior
   sensitivity analysis in Bayesian statistics: Demonstrations using an
   interactive Shiny App. *Frontiers in Psychology*, 11, 608045.

8. Dmitrienko, A. & D'Agostino, R.B. (2013). Multiplicity considerations
   in clinical trials. *Statistics in Medicine*, 32(30), 5172-5188.

9. Eisinga, R., Heskes, T., Pelzer, B., & Te Grotenhuis, M. (2017). Exact
   p-values for pairwise comparison of Friedman rank sums, with application
   to comparing classifiers. *BMC Bioinformatics*, 18, 68.

10. Elff, M., Heisig, J.P., Schaeffer, M., & Shikano, S. (2021).
    Multilevel analysis with few clusters: Improving likelihood-based
    methods to provide unbiased estimates and accurate inference. *British
    Journal of Political Science*, 51(1), 412-426.

11. Gelman, A. & Loken, E. (2014). The garden of forking paths: Why
    multiple comparisons can be a problem, even when there is no "fishing
    expedition" or "p-hacking." Working paper, Columbia University.

12. Huang, F.L. (2018). Using cluster bootstrapping to analyze nested data
    with a few clusters. *Educational and Psychological Measurement*,
    78(2), 297-318.

13. Kolde, R., Laur, S., Adler, P., & Vilo, J. (2012). Robust rank
    aggregation for gene list integration and meta-analysis.
    *Bioinformatics*, 28(4), 573-580.

14. Koo, T.K. & Li, M.Y. (2016). A guideline of selecting and reporting
    intraclass correlation coefficients for reliability research. *Journal
    of Chiropractic Medicine*, 15(2), 155-163.

15. Li, P. & Redden, D.T. (2015). Small sample performance of bias-corrected
    sandwich estimators for cluster-randomized trials with binary outcomes.
    *Statistics in Medicine*, 34(2), 281-296.

16. Lindorff-Larsen, K., Maragakis, P., Piana, S., et al. (2012). Systematic
    validation of protein force fields against experimental data. *PLoS ONE*,
    7(2), e32131.

17. Maas, C.J.M. & Hox, J.J. (2005). Sufficient sample sizes for multilevel
    modeling. *Methodology*, 1(3), 86-92.

18. McNeish, D.M. & Stapleton, L.M. (2016). Modeling clustered data with
    very few clusters. *Multivariate Behavioral Research*, 51(4), 495-518.

19. Ojala, M. & Garriga, G.C. (2010). Permutation tests for studying
    classifier performance. *Journal of Machine Learning Research*, 11,
    1833-1863.

20. Palmer, A.G. (2004). NMR characterization of the dynamics of
    biomacromolecules. *Chemical Reviews*, 104(8), 3623-3640.

21. Prompers, J.J. & Bruschweiler, R. (2002). General framework for studying
    the dynamics of folded and nonfolded proteins by NMR relaxation. *Journal
    of the American Chemical Society*, 124(16), 4522-4534.

22. Ramsey, P.H. (1989). Critical values for Spearman's rank order
    correlation. *Journal of Educational Statistics*, 14(3), 245-253.

23. Saravanan, V., Berman, G.J., & Sober, S.J. (2020). Application of the
    hierarchical bootstrap to multi-level data in neuroscience. *Neuron
    Neuromodulation*, 3(5), 500-513. (Published 2021 in *Neurons, Behavior,
    Data Analysis, and Theory*.)

24. Smith, D.G.A., Gowers, R.J., et al. (2024). Convergence of S2 order
    parameters from molecular dynamics simulations. *Journal of Physical
    Chemistry B*, 128, 10090.

25. Steegen, S., Tuerlinckx, F., Gelman, A., & Vanpaemel, W. (2016).
    Increasing transparency through a multiverse analysis. *Perspectives on
    Psychological Science*, 11(5), 702-712.

26. Weber, S., Li, Y., Seaman, J.W., et al. (2021). Applying
    meta-analytic-predictive priors with the R Bayesian evidence synthesis
    tools. *Journal of Statistical Software*, 100(19), 1-32.

27. Zar, J.H. (2005). Spearman rank correlation. *Encyclopedia of
    Biostatistics*, 7.

28. Westfall, P.H. & Young, S.S. (1993). *Resampling-Based Multiple
    Testing: Examples and Methods for p-Value Adjustment*. Wiley.

29. Weber, M., Maroulas, V., et al. (2021). Essential guidelines for
    computational method benchmarking. *Genome Biology*, 20, 125. (Originally
    published 2019.)

30. Caldwell, A., Karlsson, M., & Nordstrom, T. (2023). Pre-registration
    for predictive modeling. *arXiv:2311.18807*.
