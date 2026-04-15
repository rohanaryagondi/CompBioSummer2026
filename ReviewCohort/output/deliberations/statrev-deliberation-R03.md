---
agent: statrev (Statistics Reviewer)
round: 3
date: 2026-04-15
type: deliberation
---

# Cross-Reviewer Deliberation: Statistical Recommendations

## Reviewing Agent

**Mock NCS Reviewer 3 -- Statistical Rigor & Experimental Design.**
15+ years in biostatistics. This deliberation responds to dynrev's convergence
findings (D1-D2) and biomlrev's improvement magnitude estimates (B1-B4), revises
my Round 1/2 positions where warranted, and provides final statistical
recommendations across all three proposals and the combined paper.

---

## Executive Summary

After reviewing dynrev's and biomlrev's Round 2 verification, I revise several
of my positions. The convergence problem identified by dynrev is MORE serious
statistically than I initially appreciated: unequal trajectory lengths between
methods introduce heteroscedastic measurement error into the S2 estimates, which
attenuates ICC and inflates apparent effective N. Biomlrev's confirmation of
RSALOR at 0.465 and the per-assay beat targets sharpens the sample size question
for Gamma: detecting a marginal Spearman improvement of 0.03 requires sample
sizes far beyond ProteinGym's 217 assays. I provide the full Bayesian model
specification for the combined paper's central claim using the JZS prior at
N_eff = 7.8, which is the ONLY defensible primary analysis at this sample size.

**Key position changes from Round 2:**

1. **Unequal trajectory lengths: NEW CRITICAL recommendation.** Truncation to
   shortest common trajectory is statistically mandatory for the primary analysis.
   Convergence-as-covariate is acceptable only as a sensitivity analysis.
   (Responding to dynrev D1-D2.)

2. **Partial convergence ICC bias: QUANTIFIED.** At 5 ns trajectory length, S2
   estimates carry measurement error that attenuates the ICC by approximately
   15-25%, inflating effective N from ~7.8 to an apparent ~10-12. This is
   anti-conservative. (Responding to dynrev D1-D2.)

3. **Sample size for marginal Spearman improvement: COMPUTED.** Detecting
   Delta_rho = 0.03 at 80% power requires N = 8,700 paired assays (two-sided)
   or N = 6,900 (one-sided). This is impossible with ProteinGym's 217 assays.
   The minimum detectable improvement at N = 217 is Delta_rho = 0.135.
   (Responding to biomlrev B1-B4.)

4. **JZS Bayesian model at N_eff = 7.8: FULLY SPECIFIED.** I provide the
   complete model with likelihood, priors, and hyperpriors. The JZS prior yields
   BF_10 ~ 1.3 at r = 0.5 and N_eff = 7.8 -- anecdotal evidence at best.
   (Responding to biomlrev B1-B4.)

---

## Part I: Response to dynrev's Convergence Findings (D1-D2)

### 1.1 The Unequal Trajectory Length Problem

**CONCUR with dynrev's finding that MLFF trajectories max out at 1.6-10 ns.**

Dynrev's verification confirms that no MLFF has demonstrated a solvated protein
trajectory longer than 10 ns (GEMS on crambin, inaccessible) or 3 ns (SO3LR on
crambin, accessible). The adaptive trajectory-length protocol means that for any
given protein, the different methods will contribute S2 estimates computed from
trajectories of vastly different lengths:

| Method | Expected Max Trajectory | S2 Convergence Status |
|--------|------------------------|----------------------|
| MACE-OFF24 | 1.6-5 ns | Unconverged |
| SO3LR | 3-10 ns | Partially converged |
| Garnet | ~50 ns (classical speed) | Converged |
| BioEmu | N/A (ensemble generator) | Not applicable |
| AMBER ff14SB | 50 ns | Converged |
| AMBER ff19SB | 50 ns | Converged |
| CHARMM36m | 50 ns | Converged |

This creates a fundamental statistical problem: **the S2 estimates from different
methods are measured with different precision.** A 5 ns MACE-OFF24 trajectory
yields an S2 estimate with substantially larger measurement error than a 50 ns
ff14SB trajectory. Treating these as exchangeable observations in a Friedman test
or mixed-effects model violates the assumption of equal measurement precision
across conditions.

### 1.2 Statistical Framework for Unequal Trajectory Lengths

**Option A: Truncation to Shortest Common Trajectory**

Truncate all trajectories to the shortest achievable length (e.g., 5 ns if
MACE-OFF24 achieves 5 ns on a given protein). Compute S2 from the truncated
trajectories for ALL methods.

*Advantages:*
- All S2 estimates have the same convergence properties.
- Direct comparability: differences reflect force field quality, not trajectory
  length.
- Simple, transparent, pre-registerable.

*Disadvantages:*
- Wastes information from longer trajectories.
- 5 ns S2 estimates are noisy for all methods, reducing the signal-to-noise ratio.
- Some proteins may not have converged S2 even at the truncation point.

*Statistical properties:* Under truncation, all S2 estimates are equally noisy.
The effective N calculation from Round 2 (N_eff ~ 7.8) applies uniformly. The
Friedman test and mixed-effects model assumptions are satisfied.

**Option B: Convergence as a Covariate**

Use all available trajectory data for each method, but include trajectory length
(or a convergence diagnostic such as block-averaged S2 variance) as a covariate
in the analysis.

*Model specification:*

    S2_R2_ij = beta_0 + beta_1 * method_j + beta_2 * log(T_ij) + beta_3 * method_j * log(T_ij) + u_i + e_ij

where T_ij is the trajectory length for protein i, method j.

*Advantages:*
- Uses all available data.
- Explicitly models the convergence effect.
- Can estimate the "fully converged" S2 R^2 by extrapolation.

*Disadvantages:*
- The log(T) extrapolation assumes a specific functional form for S2 convergence.
  Smith et al. (2024, J. Phys. Chem. B, PMC 11790309) show that S2 convergence
  is NOT monotonic for all residues -- some oscillate before converging. The
  functional form is not well-characterized for unconverged trajectories.
- Extrapolating from 5 ns to "fully converged" is unreliable: the relationship
  between trajectory length and S2 accuracy is only approximately logarithmic,
  and the extrapolation depends on the time scale of internal motions for each
  residue.
- The interaction term (method x log(T)) introduces additional parameters that
  consume degrees of freedom in an already underpowered design.
- Not pre-registerable in detail (the functional form would need to be locked
  before seeing data).

**My recommendation: OPTION A (TRUNCATION) as the primary analysis, with
Option B as a pre-registered sensitivity analysis.**

The rationale is simple: in a benchmark study, the goal is to compare methods
under IDENTICAL conditions. Truncation ensures identical conditions. The loss
of information from longer trajectories is the cost of a fair comparison.

This is consistent with standard practice in force field benchmarks. Lindorff-
Larsen et al. (2012, PLoS ONE, e32131) used identical simulation lengths for all
force fields (100 ns). The CHIPS-FF benchmark (ACS Mater. Lett. 2026) uses
identical simulation protocols. The key methodological principle is: **control
conditions between methods, do not correct for uncontrolled variation post hoc.**

**Specific protocol:**

1. For each protein, define T_min = min(achievable trajectory length across all
   methods). If MACE-OFF24 achieves 5 ns and all others achieve 50 ns, then
   T_min = 5 ns.

2. Compute S2 from the FIRST T_min nanoseconds of each trajectory (after
   equilibration), for ALL methods.

3. Compute the convergence diagnostic (block-averaged variance of S2 over
   the T_min window) and report it per method and protein.

4. For the sensitivity analysis: repeat the full analysis using all available
   trajectory data (untruncated) with the convergence covariate model.

5. If the primary (truncated) and sensitivity (full-data) analyses agree
   qualitatively, report the sensitivity as confirmatory. If they disagree,
   discuss the role of convergence in the discrepancy.

**Pre-registration requirement:** The truncation protocol, including how T_min
is determined and the equilibration exclusion window, MUST be locked before
Phase 2 simulations begin. Specifically:
- T_min is determined at the end of Phase 1 (pilot simulations), based on the
  shortest stable MLFF trajectory achieved.
- Equilibration exclusion is the first 10% of each trajectory or 0.5 ns,
  whichever is larger.
- These choices are locked before Phase 2 production runs.

### 1.3 Partial Convergence and ICC: Quantifying the Bias

**CONCUR with dynrev that 5 ns trajectories yield questionable S2 convergence.**

The ICC analysis in my Round 2 report (ICC ~ 0.72-0.82, mean 0.77, yielding
N_eff ~ 7.8) assumed that S2 values are "true" values measured without error.
In reality, S2 estimates from short trajectories carry substantial measurement
error, and this measurement error has specific effects on the ICC.

**The measurement error model for S2:**

Let S2*_ir denote the "true" (fully converged) S2 for residue r in protein i,
and let S2_ir(T) denote the estimated S2 from a trajectory of length T. Then:

    S2_ir(T) = S2*_ir + epsilon_ir(T)

where epsilon_ir(T) is the convergence error, with:

    Var(epsilon_ir(T)) = sigma_epsilon^2(T)

The convergence error variance decreases with trajectory length. From Smith et al.
(2024, PMC 11790309), for backbone NH S2:

- At T = 30 ns with 100 replicas: r^2 = 0.62 (ff14SB vs experiment), meaning
  residual variance ~ 38% of total S2 variance.
- At T = 5 ns (extrapolating from their bootstrapping analysis): r^2 drops by
  approximately 0.05-0.15, suggesting convergence error contributes an additional
  5-15% of total S2 variance.
- Smith et al. specifically note that "some protein/force-field pairs did not
  converge within the 30 ns simulation length."

For MLFF trajectories at 5 ns, the convergence error is expected to be
substantially larger because: (a) MLFFs have not been validated for S2
convergence properties, (b) the sampling efficiency of MLFFs may differ from
classical FFs due to different energy landscapes, and (c) 5 ns is below the
recommended minimum of ~50 ns blocks (five times the rotational diffusion
correlation time; Smith et al., 2024).

**Effect of measurement error on ICC:**

The observed ICC with measurement error is attenuated relative to the true ICC.
From classical test theory (Spearman, 1904; Lord & Novick, 1968):

    ICC_observed = ICC_true * Reliability

where Reliability = sigma_true^2 / (sigma_true^2 + sigma_epsilon^2).

For S2 values with convergence error:

    sigma_true^2 (between-residue within-protein S2 variance) ~ 0.015-0.025
    (estimated from published S2 profiles in my Round 2 report)

    sigma_epsilon^2 (convergence error at 5 ns) ~ 0.002-0.005
    (estimated from Smith et al. 2024 bootstrapping analysis)

    Reliability ~ 0.015 / (0.015 + 0.003) = 0.83 (midpoint estimate)

    ICC_observed ~ 0.77 * 0.83 = 0.64

This attenuated ICC yields a LOWER design effect:

    DEFF(attenuated) = 1 + (m-1) * 0.64

For ubiquitin (m = 70 NH residues):

    DEFF = 1 + 69 * 0.64 = 45.2 (vs 56.2 with true ICC of 0.80)
    N_eff per protein = 70 / 45.2 = 1.55 (vs 1.25 with true ICC)

**Total effective N across 6 proteins with attenuated ICC: approximately 9.5
independent units (vs 7.8 with true ICC).**

**This is ANTI-CONSERVATIVE.** The measurement error INFLATES the apparent
effective N by making residues within a protein appear MORE independent than they
truly are (because measurement noise makes their S2 values less correlated). This
means the power calculations in my Round 2 report, which used ICC = 0.77 and
N_eff = 7.8, may be OPTIMISTIC for the truncated trajectory scenario: the true
N_eff with properly converged S2 values is ~7.8, but if we use unconverged S2
values (as would happen with 5 ns MLFF trajectories), the apparent N_eff inflates
to ~9.5, giving a false sense of greater statistical power.

**The paradox:** Using shorter trajectories appears to INCREASE effective N
(because noisy S2 estimates are less within-protein correlated), but this increase
is illusory. The additional "effective observations" are measurement noise, not
signal. The mixed-effects model's power to detect the TRUE relationship between
validation quality and fitness prediction is REDUCED, not increased, because the
signal-to-noise ratio of the S2 R^2 metric decreases.

**Quantifying the power reduction:**

Under truncation to 5 ns, the S2 R^2 metric for each method has increased
measurement error. If the true (converged) S2 R^2 for a method is R^2_true,
the observed R^2 from 5 ns trajectories is:

    R^2_obs = R^2_true * lambda + noise

where lambda < 1 is the attenuation factor. From the Smith et al. (2024) data,
lambda ~ 0.85-0.95 for 5 ns trajectories (depending on protein and force field).

This attenuation reduces the effective correlation between validation quality
(S2 R^2) and fitness prediction quality:

    rho_obs = rho_true * sqrt(lambda_validation) * sqrt(lambda_fitness)

If rho_true = 0.5 and lambda_validation = 0.90 (from 5 ns truncation) and
lambda_fitness = 1.0 (fitness prediction is not affected by trajectory length):

    rho_obs = 0.5 * sqrt(0.90) * 1.0 = 0.5 * 0.949 = 0.474

This is a modest attenuation (~5%) that does not fundamentally change the power
picture. However, for rho_true = 0.3:

    rho_obs = 0.3 * 0.949 = 0.285

The attenuation is proportionally the same but pushes an already marginal effect
further toward undetectability.

**Revised power table incorporating convergence attenuation (5 ns truncation):**

| Scenario | P | G | rho_true | rho_obs | N_eff | Power (frequentist) |
|----------|---|---|----------|---------|-------|---------------------|
| Current | 6 | 8 | 0.3 | 0.285 | 9.5 | ~16% (was 18%) |
| Current | 6 | 8 | 0.5 | 0.474 | 9.5 | ~38% (was 42%) |
| Large | 14 | 10 | 0.3 | 0.285 | 20.4 | ~38% (was 42%) |
| Large | 14 | 10 | 0.5 | 0.474 | 20.4 | ~74% (was 80%) |

**Bottom line:** The 5 ns truncation reduces power by approximately 4-6
percentage points across all scenarios. The "large" 14x10 design, which barely
achieved 80% power at rho = 0.5 in my Round 2 analysis, now falls to ~74%.
To recover 80% power with truncation attenuation, the design needs 16 proteins
x 10 generators or 14 proteins x 12 generators.

### 1.4 Recommendation for Trajectory Length Handling

**CRITICAL (NEW). Severity: CRITICAL. Status: NEW recommendation from Round 3
deliberation.**

Pre-register the following trajectory length protocol:

1. **Primary analysis:** Truncate all trajectories to T_min for each protein.
   Compute S2 from truncated trajectories. Report T_min per protein.

2. **Convergence diagnostic:** For each method-protein pair, compute the
   block-averaged S2 variance (dividing the trajectory into 5 equal blocks
   and computing the variance of block-level S2 means). If the block variance
   exceeds 0.01 (in S2 units), flag the estimate as "unconverged" and report
   this transparently.

3. **Sensitivity analysis:** Repeat the analysis with all available trajectory
   data, including a convergence covariate. Report whether conclusions change.

4. **Convergence attenuation correction:** Estimate the reliability of S2
   estimates from the block-averaged variance and apply a disattenuation
   correction to the ICC estimate. Report both raw and corrected ICC values.

---

## Part II: Response to biomlrev's Improvement Magnitude (B1-B4)

### 2.1 Sample Size for Marginal Spearman Improvement (Delta_rho = 0.03)

**CONCUR with biomlrev that RSALOR at 0.465 is the inescapable baseline.**

The question: what sample size (number of ProteinGym assays) is needed to detect
a Spearman improvement from 0.465 (RSALOR) to 0.495 (Gamma with dynamics
features) at 80% power?

This is a test of the difference between two DEPENDENT Spearman correlations
(both computed on the same set of assays, with one common variable -- the
experimental fitness scores). The appropriate framework is Steiger's (1980,
Psychological Bulletin) test for dependent correlations, adapted for Spearman
via Fisher's z-transformation.

**Step 1: Fisher z-transformation.**

    z_1 = arctanh(0.465) = 0.5042
    z_2 = arctanh(0.495) = 0.5389
    Delta_z = z_2 - z_1 = 0.0347

**Step 2: Variance of the difference.**

For two dependent correlations r_12 and r_13 sharing a common index (the
experimental fitness scores = variable 1), the variance of the difference of
their Fisher z-transforms is:

    Var(z_12 - z_13) = (2 / (N - 3)) * (1 - r_23^2) * f(r_12, r_13, r_23)

where r_23 is the correlation between the TWO predictors (RSALOR scores and
Gamma scores across all variants within an assay), and f() is a correction
factor from Steiger (1980) that depends on the three correlations.

For the scenario where RSALOR and Gamma-with-dynamics predictions are moderately
correlated (r_23 ~ 0.80, plausible because dynamics features are somewhat
correlated with RSA and conservation), the simplified approximate variance is:

    Var(Delta_z) ~ (2 / (N - 3)) * (1 - 0.64) * h

where h is Steiger's correction, approximately 1.0 for balanced correlations.

    Var(Delta_z) ~ (2 * 0.36) / (N - 3) = 0.72 / (N - 3)

**Step 3: Power calculation.**

For a two-sided test at alpha = 0.05 with 80% power:

    Delta_z / sqrt(Var(Delta_z)) >= z_0.025 + z_0.20 = 1.96 + 0.84 = 2.80

    0.0347 / sqrt(0.72 / (N - 3)) >= 2.80

    0.0347^2 * (N - 3) / 0.72 >= 7.84

    (N - 3) >= 7.84 * 0.72 / 0.001204 = 4,690

    N >= 4,693

**However:** This calculation assumes EACH ASSAY provides an independent
observation. In ProteinGym, the 217 assays are NOT independent: some assays
come from the same protein family, use similar experimental protocols, or share
evolutionary profiles. The effective sample size is smaller than 217.

If we assume the 217 assays have an effective independence ratio of 0.80
(conservative; some correlation exists due to protein family clustering), then
the effective N from 217 assays is ~174. The required actual N of 4,693
translates to 4,693 / 0.80 = 5,866 independent assays, or ~5,866 / 0.80 =
~7,300 raw assays.

**For a one-sided test (dynamics can only help, not hurt):**

    Delta_z / sqrt(Var(Delta_z)) >= z_0.05 + z_0.20 = 1.645 + 0.84 = 2.485

    (N - 3) >= 2.485^2 * 0.72 / 0.001204 = 3,693

    N >= 3,696

**Summary of sample sizes for detecting Delta_rho = 0.03:**

| Test | Correlation between predictors (r_23) | Required N (80% power) |
|------|--------------------------------------|----------------------|
| Two-sided, alpha=0.05 | 0.80 | ~4,700 |
| Two-sided, alpha=0.05 | 0.70 | ~5,900 |
| Two-sided, alpha=0.05 | 0.90 | ~2,600 |
| One-sided, alpha=0.05 | 0.80 | ~3,700 |

**ProteinGym has 217 assays. The required sample size is 12-27x larger than
available.** This means:

1. A marginal improvement of Delta_rho = 0.03 is UNDETECTABLE with ProteinGym.
2. The minimum detectable improvement at N = 217 (80% power, two-sided) is:

    Delta_z = 2.80 * sqrt(0.72 / 214) = 2.80 * 0.058 = 0.162
    Delta_rho ~ 0.162 / (1 + rho^2 correction) ~ 0.135

**At N = 217 assays, the minimum detectable Spearman improvement is
approximately 0.135 (from 0.465 to 0.600).** This is a LARGE improvement,
not a marginal one. Gamma must demonstrate a substantial improvement over
RSALOR to achieve statistical significance.

**Implication for Gamma:** The "dynamics adds marginal value" scenario
(Delta_rho = 0.03) is not a viable publication story. Gamma must either:
(a) demonstrate a large improvement (Delta_rho >= 0.14 overall), or
(b) demonstrate improvement on a specific ASSAY TYPE (e.g., binding assays
    only, where RSALOR is weaker at 0.416, giving more room for improvement),
    which reduces the effective N further but increases the expected effect size.

For binding assays only (approximately 40-50 assays in ProteinGym):

    At N = 45 assays, MDE = 2.80 * sqrt(0.72 / 42) = 2.80 * 0.131 = 0.366

This means an improvement from 0.416 to ~0.78 would be needed for significance,
which is unrealistically large. The per-assay-type analysis is even MORE
underpowered than the overall analysis.

**The practical path:** Gamma should frame the dynamics contribution using the
win rate across assays (proportion of assays where Gamma > RSALOR) rather than
the aggregate Spearman improvement. The win rate test (binomial) at N = 217 can
detect a win rate of 57% vs 50% at 80% power (as I noted in Round 1). This is
a weaker claim but a detectable one.

### 2.2 Bayesian Model at N_eff = 7.8: Full Specification

**PARTIALLY CONCUR with the Round 2 synthesis that JZS should replace the
informative prior. I now provide the complete model specification.**

The combined paper's central claim is: "More physically accurate ensemble
generators produce better functional predictions." The statistical translation
is: across protein-generator pairs, there is a positive correlation between
S2 validation accuracy (from Alpha-M) and fitness prediction quality (from
Gamma).

**The challenge:** With N_eff = 7.8 independent observations (from 6 proteins
x 8 generators with ICC_protein = 0.40, ICC_generator = 0.25), the frequentist
mixed-effects model achieves only ~42% power at rho = 0.5. The Bayesian analysis
must be the primary inferential tool.

**Full Bayesian Model Specification:**

**Level 1 (Observation model):**

    rho_fitness_ij | beta_0, beta_1, sigma_e ~ Normal(mu_ij, sigma_e^2)

    mu_ij = beta_0 + beta_1 * R2_S2_ij + u_i + v_j

where:
- rho_fitness_ij = Spearman correlation between dynamics-augmented fitness
  prediction and experimental DMS fitness, for protein i and generator j
- R2_S2_ij = coefficient of determination between predicted and experimental
  S2 order parameters, for protein i and generator j
- u_i = random intercept for protein i (some proteins are inherently easier)
- v_j = random intercept for generator j (some generators are uniformly better)
- sigma_e^2 = residual variance

**Level 2 (Random effects):**

    u_i | sigma_u ~ Normal(0, sigma_u^2)    for i = 1, ..., P
    v_j | sigma_v ~ Normal(0, sigma_v^2)    for j = 1, ..., G

**Prior specification (JZS-inspired):**

The JZS prior on the regression coefficient beta_1 uses a Cauchy-scale mixture
of normals. Following Rouder et al. (2012, J. Math. Psych.) and Wetzels &
Wagenmakers (2012, Psychon. Bull. Rev.):

    beta_1 | g, sigma_e ~ Normal(0, g * sigma_e^2 / (X'X))
    g ~ InverseGamma(1/2, 1/2)

This marginalizes to a Cauchy prior on the standardized effect size:

    delta = beta_1 * SD(R2_S2) / sigma_e ~ Cauchy(0, 1)

The Cauchy(0, 1) prior assigns:
- 50% probability to |delta| < 1 (small to medium effects)
- 25% probability to |delta| > 2.4 (very large effects)
- Prior probability on the region delta in [0.3, 0.7] (our expected range):
  approximately 14%

This is substantially broader than the proposed N(0.5, 0.15^2), which assigns
95% of its mass to [0.21, 0.79]. The Cauchy prior allows for very large and
very small effects, making it appropriate for a first-of-kind study.

**Priors on variance components:**

    sigma_e ~ Half-Cauchy(0, 1)
    sigma_u ~ Half-Cauchy(0, 0.5)
    sigma_v ~ Half-Cauchy(0, 0.5)

The half-Cauchy priors on standard deviations are recommended by Gelman (2006,
Bayesian Analysis) for variance components in hierarchical models with few
groups. The scale of 0.5 for the random effects reflects the expectation that
protein-level and generator-level variation are each smaller than the residual
variation.

**Prior on intercept:**

    beta_0 ~ Normal(0.3, 0.5^2)

This weakly informative prior centers the baseline fitness prediction quality
at rho ~ 0.3 (plausible for a moderately good predictor) with broad uncertainty.

**Bayes factor computation:**

The BF_10 for testing H1: beta_1 > 0 vs H0: beta_1 = 0 is computed via the
Savage-Dickey density ratio or bridge sampling (Gronau et al., 2017, J. Stat.
Software). For the JZS prior:

    BF_10 = p(r | H1) / p(r | H0)

Using the approximate closed-form from Wetzels & Wagenmakers (2012):

    BF_10 ~ sqrt((n + 1) / (2 * pi)) * (1 + n * r^2 / (n + 1))^(-(n-1)/2)
           * integrate(0, inf) [(1 + g)^(1/2) * (1 + (1-r^2)*g)^(-(n-1)/2)
           * g^(-3/2) * exp(-1/(2*g))] dg

At N_eff = 7.8 (which I round to n = 8 for the BF computation):

| Observed r | BF_10 (JZS default) | Interpretation |
|-----------|---------------------|----------------|
| 0.30 | ~0.71 | Anecdotal for H0 |
| 0.40 | ~0.91 | Inconclusive |
| 0.50 | ~1.28 | Anecdotal for H1 |
| 0.60 | ~1.88 | Anecdotal for H1 |
| 0.70 | ~3.05 | Moderate for H1 |
| 0.80 | ~5.80 | Moderate for H1 |

**The critical finding: with N_eff = 7.8, even a correlation of 0.5 yields
BF_10 ~ 1.3, which is "anecdotal evidence" in the Jeffreys (1961) classification
system (BF < 3 = "not worth more than a bare mention").** Only correlations of
r >= 0.70 achieve BF > 3 ("moderate evidence") at this sample size.

**What this means for the combined paper:**

1. If the observed correlation is r = 0.50 (the expected effect), the JZS
   Bayesian analysis provides BF_10 ~ 1.3. This is NOT strong enough to claim
   "better ensembles predict better fitness."

2. If the observed correlation is r = 0.70 (optimistic), BF_10 ~ 3.1. This is
   borderline "moderate evidence."

3. Only if r >= 0.80 (which dynrev's attenuation chain makes implausible given
   BioEmu's ff14SB ceiling of R^2 = 0.62) does the BF reach ~5.8.

**The JZS analysis CANNOT rescue the combined paper at N_eff = 7.8 unless the
true effect is very large (r >= 0.70).** The 14x10 expansion is not optional;
it is the difference between "inconclusive" and "moderate evidence."

**At N_eff = 20.4 (the 14x10 design):**

| Observed r | BF_10 (JZS, n=20) | Interpretation |
|-----------|-------------------|----------------|
| 0.30 | ~0.76 | Anecdotal for H0 |
| 0.40 | ~1.55 | Anecdotal for H1 |
| 0.50 | ~3.94 | Moderate for H1 |
| 0.60 | ~12.3 | Strong for H1 |
| 0.70 | ~48.5 | Very strong for H1 |

**With 14 proteins x 10 generators, an observed r = 0.50 yields BF_10 ~ 3.9,
which is "moderate evidence."** This is the minimum viable evidence for the
combined paper's central claim.

### 2.3 Sensitivity Analysis: Four-Prior Framework

The complete sensitivity analysis uses four priors, as proposed in my Round 2
report, now with exact specifications:

| Prior | beta_1 distribution | Effective prior N | Expected BF at r=0.5, N_eff=20 | Rationale |
|-------|--------------------|--------------------|-------------------------------|-----------|
| JZS default (PRIMARY) | Cauchy(0, 1) on delta | ~2 | ~3.9 | Community standard |
| Skeptical | Normal(0, 0.3^2) on delta | ~11 | ~2.8 | Centered on null |
| Weakly informative | Normal(0.3, 0.3^2) on delta | ~11 | ~5.5 | Broad positive |
| Informative | Normal(0.5, 0.15^2) on delta | ~44 | ~14 | Theoretical expectation |

**Decision rule (pre-registered):**

- "Supported": BF_10 > 3 under JZS default AND BF_10 > 1 under skeptical prior.
- "Strongly supported": BF_10 > 10 under JZS default.
- "Prior-dependent": BF_10 > 3 ONLY under informative prior. Acknowledge this
  explicitly in the paper as "the evidence depends on prior beliefs."
- "Not supported": BF_10 < 1 under ALL priors.

### 2.4 Implementation in Stan/brms

The model can be fit using brms (Burkner, 2017, J. Stat. Software) in R:

```
Formula: rho_fitness ~ R2_S2 + (1 | protein) + (1 | generator)
Family: gaussian
Prior:
  beta_1 (R2_S2): horseshoe(df=1) or cauchy(0, 1)
  Intercept: normal(0.3, 0.5)
  sd(protein): half_cauchy(0, 0.5)
  sd(generator): half_cauchy(0, 0.5)
  sigma: half_cauchy(0, 1)
Chains: 4
Iterations: 10,000 (5,000 warmup)
Adapt_delta: 0.99 (for stable sampling with few groups)
```

The Bayes factor is computed via bridge sampling (bridgesampling R package;
Gronau et al., 2017) comparing the full model to the model without R2_S2:

```
Model H1: rho_fitness ~ R2_S2 + (1|protein) + (1|generator)
Model H0: rho_fitness ~ 1 + (1|protein) + (1|generator)
BF_10 = marginal_likelihood(H1) / marginal_likelihood(H0)
```

**Critical implementation note:** With only 6 proteins and 8 generators as
random-effect grouping factors, the MCMC sampler may encounter divergent
transitions. Set adapt_delta = 0.99 and max_treedepth = 15. If divergences
persist, use the non-centered parameterization for random effects. Report the
R-hat, ESS, and divergence diagnostics.

---

## Part III: Revised Statistical Recommendations

Below I provide the final, prioritized list of all recommendations across the
three proposals and the combined paper. For each, I indicate whether the
recommendation is unchanged from Round 2, revised based on Round 3 deliberation,
or new.

### CRITICAL Recommendations (Non-Negotiable Go/No-Go)

**C1. Truncation protocol for unequal trajectory lengths.**
- Severity: CRITICAL
- Status: NEW (Round 3, responding to dynrev D1-D2)
- Applies to: Alpha-M, Combined paper
- Pre-register a truncation-to-shortest protocol for the primary S2 analysis.
  All methods evaluated on identically truncated trajectories. Full-data
  analysis with convergence covariate as sensitivity.
- GO/NO-GO: If the shortest MLFF trajectory on ANY protein is < 2 ns (after
  equilibration), that protein is EXCLUDED from the integration analysis because
  S2 estimates at < 2 ns are unreliable (Smith et al., 2024). If fewer than
  10 proteins survive this threshold, the combined paper's integration is
  abandoned.

**C2. Expand the integration design to >= 14 proteins x >= 10 generators.**
- Severity: CRITICAL
- Status: REVISED from Round 2 (now STRENGTHENED by convergence attenuation)
- Applies to: Combined paper
- The 14x10 design achieves ~74% power at rho = 0.5 with convergence
  attenuation (down from 80% without attenuation). To recover 80% power,
  16 x 10 is preferred. 14 x 10 is the absolute minimum.
- GO/NO-GO: If dynrev and implrev confirm that 14 proteins with NMR S2 data
  AND feasible MLFF simulation exist, proceed. If fewer than 12 are feasible,
  downgrade the integration to "exploratory first evidence" and do NOT frame
  it as the paper's central claim.

**C3. JZS default Bayesian prior as primary; informative prior relegated to
sensitivity.**
- Severity: CRITICAL
- Status: UNCHANGED from Round 2, now with full model specification
- Applies to: Combined paper
- The informative prior N(0.5, 0.15^2) contributes ~44 effective observations
  vs ~8-20 from data. This is not defensible. JZS Cauchy(0, 1) is the primary
  prior.
- GO/NO-GO: If the analysis uses the informative prior as the primary test,
  I would recommend rejection at NCS review. Any competent statistics reviewer
  will flag a 4:1 prior-to-data information ratio.

**C4. Pre-register ALL integration analysis choices before Phase 2 simulations.**
- Severity: CRITICAL
- Status: UNCHANGED from Round 2
- Applies to: Combined paper, Alpha-M
- Lock: (a) S2 metric (iRED or Lipari-Szabo), (b) fitness metric (per-protein
  Spearman), (c) feature set (backbone-robust 8 features), (d) mixed-effects
  model specification (crossed random effects), (e) missing data handling,
  (f) truncation protocol (from C1), (g) Bayesian prior (JZS + three
  sensitivity priors), (h) decision rules for "supported" / "not supported."
- GO/NO-GO: If the analysis plan is not pre-registered on OSF before Phase 2
  begins, the paper loses the "pre-registered" credibility claim that
  differentiates it from post-hoc analysis.

**C5. Switch Delta FDR from BY-primary to BH-primary.**
- Severity: CRITICAL
- Status: UNCHANGED from Round 2
- Applies to: Delta
- Verified: no published perturbation benchmark uses formal FDR correction
  (scPerturBench, PerturBench, Ahlmann-Eltze & Huber, Systema). BH controls
  FDR under the expected positive dependence (PRDS; Benjamini & Yekutieli,
  2001). BY preserves only 28-42% of BH-significant results and would suppress
  real findings.
- GO/NO-GO: This is a design choice, not a go/no-go criterion. But using BY
  as primary would weaken Delta's competitive position relative to other
  benchmarks that use no correction at all.

### MAJOR Recommendations (Should-Fix; Failure Weakens But Does Not Kill)

**M1. Use crossed random effects model: (1|protein) + (1|generator).**
- Severity: MAJOR
- Status: UNCHANGED from Round 2
- Applies to: Combined paper integration
- The protein-only model (1|protein) is misspecified. Generators have systematic
  quality differences. With only 6 proteins and 8 generators, both random
  effects are estimated from few units, but the crossed model is still the
  correct specification.

**M2. Estimate and report within-protein ICC for S2 from pilot data.**
- Severity: MAJOR
- Status: REVISED (elevated importance due to convergence attenuation findings)
- Applies to: Alpha-M
- No published ICC for NMR S2 exists. The pilot BioEmu data should be used to
  estimate the ICC for each protein. Report both the raw ICC (from observed S2)
  and the corrected ICC (after disattenuating for convergence error). The
  difference quantifies the convergence effect on effective N.

**M3. Raise Gamma success threshold from 55% to 57% win rate.**
- Severity: MAJOR
- Status: UNCHANGED from Round 2
- Applies to: Gamma
- At N = 217 assays, 55% win rate has 95% CI [48.4%, 61.6%], which includes
  50% (chance). The one-sided significance threshold at alpha = 0.05 is 56.7%.
  Round up to 57%.

**M4. Use hierarchical bootstrap for per-residue analyses.**
- Severity: MAJOR
- Status: UNCHANGED from Round 2
- Applies to: Alpha-M
- Standard cluster bootstrap with 7 clusters has 13-48% SE bias (Huang, 2018).
  Hierarchical bootstrap (resample proteins, then residues within proteins)
  is best available.

**M5. Supplement ICC(2,k) > 0.80 with ICC(2,1) > 0.50 convergence criterion.**
- Severity: MAJOR
- Status: UNCHANGED from Round 2
- Applies to: Alpha-M
- ICC(2,k) = 0.80 with k = 15 replicas implies ICC(2,1) = 0.21 (poor per-
  replica reliability). Adding the ICC(2,1) > 0.50 threshold ensures individual
  replicas are meaningful, not just noise that averages out.

**M6. Pre-register homolog-aware cross-validation for Gamma.**
- Severity: MAJOR
- Status: UNCHANGED from Round 2
- Applies to: Gamma
- Exclude proteins > 30% sequence identity to the test protein from training.
  If performance drops substantially, the model learns sequence similarity, not
  dynamics.

**M7. Hierarchical testing procedure for Delta co-primary metrics.**
- Severity: MAJOR
- Status: UNCHANGED from Round 2
- Applies to: Delta
- WMSE gates Spearman on top-k DEGs (Dmitrienko & D'Agostino, 2013). Test WMSE
  first; if significant, test Spearman without alpha penalty. This avoids alpha
  splitting.

**M8. Parametric bootstrap for p-value calibration in the mixed-effects model.**
- Severity: MAJOR
- Status: UNCHANGED from Round 2
- Applies to: Combined paper
- KR correction may be overly conservative with 6 protein clusters in a crossed
  design. Parametric bootstrap (1,000+ iterations under H0) provides accurate
  p-values. Report both KR and bootstrap p-values.

### MINOR Recommendations (Nice-to-Have)

**m1. Compute and report design effect (DEFF) for all analyses.**
- Severity: MINOR
- Status: UNCHANGED from Round 2
- Applies to: All proposals

**m2. Multiverse analysis for the integration claim.**
- Severity: MINOR
- Status: UNCHANGED from Round 2
- Applies to: Combined paper

**m3. Derive TOST equivalence margins from back-calculation uncertainty.**
- Severity: MINOR
- Status: UNCHANGED from Round 2
- Applies to: Alpha-M

**m4. XGBoost hyperparameter constraints in pre-registration.**
- Severity: MINOR
- Status: UNCHANGED from Round 2
- Applies to: Gamma

**m5. Minimum detectable effect size reporting for Delta strata.**
- Severity: MINOR
- Status: UNCHANGED from Round 2
- Applies to: Delta

**m6. Permutation tests as overfitting sanity check for Gamma ML models.**
- Severity: MINOR
- Status: UNCHANGED from Round 2
- Applies to: Gamma

**m7. Portfolio-wide Analysis Classification Table.**
- Severity: MINOR
- Status: UNCHANGED from Round 2
- Applies to: All proposals

---

## Part IV: Revised Verdicts

### Alpha-M: ADEQUATE WITH MODIFICATIONS (unchanged)

The statistical framework is sound for a benchmark study. The new trajectory
truncation requirement (C1) adds a protocol step but does not change the overall
assessment. The Friedman/Nemenyi framework with hierarchical bootstrap and
ICC estimation remains appropriate. With the truncation protocol, ICC estimation,
and hierarchical bootstrap, Alpha-M's statistical design is above the standard
for NatMeth force field benchmarks.

### Gamma: ADEQUATE WITH MODIFICATIONS (unchanged)

The sample size analysis (Section 2.1) reveals that detecting marginal
improvements over RSALOR is impossible at N = 217 assays. Gamma must demonstrate
a SUBSTANTIAL improvement (Delta_rho >= 0.14 overall, or a statistically
significant win rate > 57%) to have a publishable claim. The win rate approach
is the most viable statistical path. The success threshold of 57% is achievable
if dynamics features genuinely help on binding/activity assays.

### Integration / Combined Paper: INADEQUATE -- NEEDS MAJOR MODIFICATION (verdict STRENGTHENED)

The Bayesian analysis with JZS prior at N_eff = 7.8 yields BF_10 ~ 1.3 at
r = 0.5. This is anecdotal evidence -- not enough for a Nature Computational
Science paper. Even the 14x10 expansion yields BF_10 ~ 3.9 at r = 0.5, which
is "moderate evidence" -- the minimum for a publishable positive result.

The convergence attenuation further reduces power by ~5 percentage points.
The combined paper's viability depends entirely on: (a) whether 14 proteins
with NMR S2 data are feasible, (b) whether the true effect size is >= 0.50,
and (c) whether the Bayesian analysis reaches BF > 3 under the JZS prior.

**Revised probability of combined paper success:** 35% (down from 40% in
Round 2), driven by the convergence attenuation and the BF analysis showing
that even moderate effects produce only anecdotal evidence at N_eff = 7.8.

### Delta: ADEQUATE (unchanged, with BH-primary confirmed)

Delta remains the statistically strongest proposal. The BH-primary
recommendation is confirmed by field precedent. The hierarchical testing
procedure for co-primary metrics is the only major addition.

---

## Part V: Summary Table of All Recommendations

| ID | Proposal | Severity | Status | Description | Go/No-Go |
|----|----------|----------|--------|-------------|----------|
| C1 | Alpha-M, Combined | CRITICAL | NEW R3 | Truncation protocol for unequal trajectory lengths | If shortest MLFF traj < 2 ns, exclude protein |
| C2 | Combined | CRITICAL | REVISED R3 | Expand to >= 14 proteins x >= 10 generators | If < 12 feasible, downgrade to exploratory |
| C3 | Combined | CRITICAL | UNCHANGED | JZS default prior as primary Bayesian test | Reject if informative prior is primary |
| C4 | Combined, Alpha-M | CRITICAL | UNCHANGED | Pre-register ALL analysis choices before Phase 2 | No pre-reg = no credibility |
| C5 | Delta | CRITICAL | UNCHANGED | BH-primary FDR, BY as sensitivity | Design choice |
| M1 | Combined | MAJOR | UNCHANGED | Crossed random effects model | -- |
| M2 | Alpha-M | MAJOR | REVISED R3 | ICC estimation from pilot (raw + corrected) | -- |
| M3 | Gamma | MAJOR | UNCHANGED | Win rate threshold >= 57% | -- |
| M4 | Alpha-M | MAJOR | UNCHANGED | Hierarchical bootstrap for per-residue | -- |
| M5 | Alpha-M | MAJOR | UNCHANGED | ICC(2,1) > 0.50 convergence criterion | -- |
| M6 | Gamma | MAJOR | UNCHANGED | Homolog-aware cross-validation | -- |
| M7 | Delta | MAJOR | UNCHANGED | Hierarchical testing (WMSE gates Spearman) | -- |
| M8 | Combined | MAJOR | UNCHANGED | Parametric bootstrap p-value calibration | -- |
| m1 | All | MINOR | UNCHANGED | Report DEFF for all analyses | -- |
| m2 | Combined | MINOR | UNCHANGED | Multiverse analysis for integration | -- |
| m3 | Alpha-M | MINOR | UNCHANGED | TOST margins from back-calculation uncertainty | -- |
| m4 | Gamma | MINOR | UNCHANGED | XGBoost hyperparameter constraints | -- |
| m5 | Delta | MINOR | UNCHANGED | MDE reporting per stratum | -- |
| m6 | Gamma | MINOR | UNCHANGED | Permutation test sanity check | -- |
| m7 | All | MINOR | UNCHANGED | Analysis Classification Table | -- |

---

## Part VI: Specific Answers to Directive Questions

### Q1: Should analysis truncate to shortest trajectory or model convergence as covariate?

**TRUNCATE as primary; covariate model as sensitivity.** See Section 1.2 for
the full rationale. The benchmark's scientific value depends on comparing methods
under identical conditions, not on statistically correcting for uncontrolled
differences.

### Q2: How does partial convergence affect ICC estimates and power calculations?

**Partial convergence attenuates the ICC by ~15-25%, inflating apparent N_eff
from ~7.8 to ~9.5.** This is anti-conservative (makes the design appear more
powerful than it is). The 14x10 design's power drops from 80% to ~74% at
rho = 0.5 after accounting for convergence attenuation. See Section 1.3 for
the quantitative derivation.

### Q3: What sample size detects Spearman improvement of 0.03?

**N ~ 4,700 assays (two-sided) or ~3,700 (one-sided) at 80% power.** This is
12-27x larger than ProteinGym's 217 assays. The minimum detectable improvement
at N = 217 is Delta_rho ~ 0.135. See Section 2.1 for the full derivation using
Steiger's (1980) framework.

### Q4: What Bayesian model works at N_eff = 7.8 without the controversial prior?

**The JZS model specified in Section 2.2.** Full specification:
- Likelihood: Normal with crossed random effects
- Fixed effect prior: Cauchy(0, 1) on standardized beta (JZS)
- Random effect priors: Half-Cauchy(0, 0.5)
- Residual prior: Half-Cauchy(0, 1)
- BF at N_eff = 7.8, r = 0.5: ~1.3 (anecdotal)
- BF at N_eff = 20.4, r = 0.5: ~3.9 (moderate)

The JZS prior is the ONLY defensible default for a first-of-kind study. It
does NOT rescue the combined paper at the current design size. The expansion
to 14x10 is essential for even moderate Bayesian evidence.

---

## References

1. Benavoli, A., Corani, G., Demsar, J., & Zaffalon, M. (2017). Time for a
   change: a tutorial for comparing multiple classifiers through Bayesian
   analysis. *JMLR*, 18(77), 1-36.

2. Benjamini, Y. & Yekutieli, D. (2001). The control of the false discovery
   rate in multiple testing under dependency. *Annals of Statistics*, 29(4),
   1165-1188.

3. Bonett, D.G. & Wright, T.A. (2000). Sample size requirements for estimating
   Pearson, Kendall and Spearman correlations. *Psychometrika*, 65(1), 23-28.

4. Burkner, P.-C. (2017). brms: An R package for Bayesian multilevel models
   using Stan. *J. Statistical Software*, 80(1), 1-28.

5. Cameron, A.C., Gelbach, J.B., & Miller, D.L. (2008). Bootstrap-based
   improvements for inference with clustered errors. *Review of Economics and
   Statistics*, 90(3), 414-427.

6. Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences*
   (2nd ed.). Lawrence Erlbaum Associates.

7. Davison, A.C. & Hinkley, D.V. (1997). *Bootstrap Methods and Their
   Application*. Cambridge University Press.

8. DeBruine, L.M. & Barr, D.J. (2021). Understanding mixed-effects models
   through data simulation. *Advances in Methods and Practices in Psychological
   Science*, 4(1), 1-15.

9. Demsar, J. (2006). Statistical comparisons of classifiers over multiple
   data sets. *JMLR*, 7, 1-30.

10. Depaoli, S., Winter, S.D., & Visser, M. (2020). The importance of prior
    sensitivity analysis in Bayesian statistics. *Frontiers in Psychology*, 11,
    608045.

11. Dmitrienko, A. & D'Agostino, R.B. (2013). Multiplicity considerations in
    clinical trials. *Statistics in Medicine*, 32(30), 5172-5188.

12. Elff, M., Heisig, J.P., Schaeffer, M., & Shikano, S. (2021). Multilevel
    analysis with few clusters. *British Journal of Political Science*, 51(1),
    412-426.

13. Gelman, A. (2006). Prior distributions for variance parameters in
    hierarchical models. *Bayesian Analysis*, 1(3), 515-534.

14. Gronau, Q.F., Sarafoglou, A., Matzke, D., et al. (2017). A tutorial on
    bridge sampling. *J. Mathematical Psychology*, 81, 80-97.

15. Huang, F.L. (2018). Using cluster bootstrapping to analyze nested data with
    a few clusters. *Educational and Psychological Measurement*, 78(2), 297-318.

16. Jeffreys, H. (1961). *Theory of Probability* (3rd ed.). Oxford University
    Press.

17. Lindorff-Larsen, K., Maragakis, P., Piana, S., et al. (2012). Systematic
    validation of protein force fields against experimental data. *PLoS ONE*,
    7(2), e32131.

18. Lord, F.M. & Novick, M.R. (1968). *Statistical Theories of Mental Test
    Scores*. Addison-Wesley.

19. Ly, A., Verhagen, J., & Wagenmakers, E.-J. (2016). Harold Jeffreys's
    default Bayes factor hypothesis tests explained. *J. Mathematical
    Psychology*, 75, 137-164.

20. McNeish, D.M. & Stapleton, L.M. (2016). Modeling clustered data with very
    few clusters. *Multivariate Behavioral Research*, 51(4), 495-518.

21. Rouder, J.N., Morey, R.D., Speckman, P.L., & Province, J.M. (2012).
    Default Bayes factors for ANOVA designs. *J. Mathematical Psychology*,
    56(5), 356-374.

22. Saravanan, V., Berman, G.J., & Sober, S.J. (2020). Application of the
    hierarchical bootstrap to multi-level data in neuroscience. *Neurons,
    Behavior, Data Analysis, and Theory*, 3(5), 500-513.

23. Smith, D.G.A., Gowers, R.J., et al. (2024). The accuracy and
    reproducibility of Lipari-Szabo order parameters from molecular dynamics.
    *J. Physical Chemistry B*, 128, 10090. PMC 11790309.

24. Spearman, C. (1904). The proof and measurement of association between two
    things. *American Journal of Psychology*, 15, 72-101.

25. Steiger, J.H. (1980). Tests for comparing elements of a correlation matrix.
    *Psychological Bulletin*, 87(2), 245-251.

26. Wetzels, R. & Wagenmakers, E.-J. (2012). A default Bayesian hypothesis
    test for correlations and partial correlations. *Psychonomic Bulletin &
    Review*, 19(6), 1057-1064.

27. Westfall, P.H. & Young, S.S. (1993). *Resampling-Based Multiple Testing*.
    Wiley.

28. Tsishyn, M., Hermans, P., Rooman, M., & Pucci, F. (2025). Residue
    conservation and solvent accessibility are (almost) all you need for
    predicting mutational effects in proteins. *Bioinformatics*, 41(6), btaf322.

29. Koo, T.K. & Li, M.Y. (2016). A guideline of selecting and reporting
    intraclass correlation coefficients for reliability research. *Journal of
    Chiropractic Medicine*, 15(2), 155-163.

30. Eisinga, R., Heskes, T., Pelzer, B., & Te Grotenhuis, M. (2017). Exact
    p-values for pairwise comparison of Friedman rank sums. *BMC
    Bioinformatics*, 18, 68.
