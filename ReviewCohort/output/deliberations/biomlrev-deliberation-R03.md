---
agent: biomlrev (ML/Biology Reviewer)
round: 3
date: 2026-04-15
type: deliberation
---

# Cross-Reviewer Deliberation: ML/Biology Assessment of Gamma, Combined Paper, and Integration Viability

## Reviewing Agent

Computational Biology & ML Reviewer (biomlrev), Mock NCS Reviewer 2. This
deliberation responds to dynrev's dynamics findings (D3-D4) and statrev's
statistical concerns (S1, S3), revises my positions where warranted, and
provides an updated verdict on the combined Gamma+Alpha-M paper and the
separation question.

---

## Executive Summary

After reviewing dynrev's Round 2 verification of the BioEmu ff14SB ceiling,
Boltz-2 RMSF metrics, and the BioEmu augmented MD preprint, and after
reviewing statrev's revised power analysis (42% power at rho=0.5 for 6x8,
~80% for 14x10) and Bayesian prior critique, I revise my assessment as
follows:

1. **PARTIALLY CONCUR with dynrev** on the BioEmu ff14SB ceiling. The
   ceiling is real (R^2=0.62 vs experiment) but its impact on Gamma depends
   on whether the FITNESS-relevant dynamics signal is captured by the first
   0.62 of variance or resides in the remaining 0.38. I argue the former is
   more likely for binding/catalysis, making the ceiling less fatal than it
   appears for dynamics metrics but still a serious constraint.

2. **CONCUR with statrev** on the inadequacy of the N(0.5, 0.15^2) prior
   and the need for JZS as the primary Bayesian test. The 4:1 prior-to-data
   ratio is indefensible for a first-of-kind study.

3. **PARTIALLY CONCUR with statrev** on effect size. The smallest
   biologically meaningful improvement over RSALOR is delta-rho >= 0.04 on
   binding/activity assays (from 0.416/0.479 to ~0.46/0.52). This is
   detectable with the 14x10 design under Bayesian analysis but not with
   the 6x8 frequentist approach. The rho=0.5 target for the integration
   correlation is optimistic but not unreasonable given MutRobustness
   priors.

4. **DISAGREE with the Round 2 synthesis framing** that the combined paper
   is at "40% viable." I revise this to 30-35% for the combined paper at
   NCS, with a clear fallback path (separate Alpha-M at NatMeth + Gamma at
   PLOS Computational Biology or Bioinformatics). The separation question
   should be resolved by August 31 based on pilot data.

5. **Recommend conditional separation** as the default strategy, with the
   combined paper as an upside scenario that requires specific quantitative
   thresholds to proceed.

---

## Section 1: Response to dynrev's Dynamics Findings (D3-D4)

### 1.1 BioEmu ff14SB Ceiling and Gamma's Improvement Ceiling

**dynrev finding:** BioEmu faithfully reproduces ff14SB equilibrium
distributions. BioEmu S2 accuracy is bounded by ff14SB R^2=0.62 vs
experiment. Aryal et al. (IJMS 2026) confirmed BioEmu "effectively
reproduces fundamental properties" when compared to MD -- meaning BioEmu
emulates ff14SB, not experiment.

**PARTIALLY CONCUR.** The ceiling is real and quantified. But I want to
sharpen what this means for Gamma specifically.

**The critical question is not "how accurate is BioEmu dynamics?" but "do
BioEmu dynamics features predict fitness better than no dynamics features?"**

These are different questions. Consider the analogy: AlphaFold2 predicted
structures have systematic errors (especially in loop regions, with GDT-TS
~0.90 on average), yet AlphaFold2 structures are ENORMOUSLY useful for
fitness prediction (AlphaMissense, ESM-IF1, ProSST). The errors are not in
the fitness-relevant information. Similarly, BioEmu's ff14SB ceiling means
its dynamics are imperfect, but the imperfections may not reside in the
fitness-relevant features.

**Quantitative argument for why the ceiling matters less than it appears:**

1. **RMSF is a rank-order feature for Gamma.** Gamma uses RMSF to identify
   which residues are flexible vs rigid, not to predict exact RMSF values.
   BioEmu RMSF correlation with ff14SB MD is Pearson 0.71-0.80 on mdCATH/
   ATLAS (Boltz-2 paper benchmarks). The rank ordering of flexible vs rigid
   residues is substantially preserved even at R^2=0.62 for S2. If residue
   A has S2=0.85 (rigid) and residue B has S2=0.55 (flexible) in experiment,
   ff14SB typically preserves this ordering even if the absolute values
   differ.

2. **The fitness signal depends on the CORRECT side of the conservation-
   dynamics correlation.** RSALOR captures conservation + RSA. Dynamics
   features could add value if they identify residues where flexibility is
   DECOUPLED from conservation -- i.e., conserved residues that are
   unexpectedly flexible (catalytic loops, hinge regions) or variable
   residues that are unexpectedly rigid (structural scaffolding). This
   signal does not require perfect dynamics accuracy; it requires correct
   identification of unusual residues. BioEmu at ff14SB accuracy is
   sufficient for this.

3. **The bias chain attenuates but does not eliminate the signal.** The
   chain is: Experiment -> ff14SB (R^2=0.62) -> BioEmu (R^2~0.8 vs ff14SB
   on RMSF) -> Feature extraction -> ML model -> Fitness prediction. Each
   link attenuates. End-to-end, the dynamics signal reaching the fitness
   predictor is approximately:
   - sqrt(0.62) * sqrt(0.80) * feature_extraction_efficiency ~ 0.79 * 0.89 * 0.7
   - ~ 0.49 of the original experimental dynamics information.

   This means about half the true dynamics-fitness signal is preserved. If
   the true dynamics-fitness correlation is rho=0.6 (MutRobustness level),
   the observable correlation through BioEmu would be rho ~ 0.6 * 0.49 =
   0.29. This is detectable but small. If the true correlation is rho=0.3
   (pessimistic), the observable signal would be rho ~ 0.15, which is at
   the noise floor.

**Realistic improvement ceiling over RSALOR:**

Given the above, I estimate:

| Scenario | True dynamics-fitness rho | BioEmu-attenuated rho | Delta over RSALOR (Spearman) |
|----------|--------------------------|----------------------|------------------------------|
| Optimistic | 0.6 (MutRobustness) | 0.29 | +0.04-0.06 on binding/activity |
| Moderate | 0.4 | 0.20 | +0.02-0.03 on binding/activity |
| Pessimistic | 0.2 | 0.10 | +0.00-0.01 (undetectable) |

The optimistic scenario gives a detectable improvement (delta-Spearman ~0.04-
0.06 over RSALOR on binding/activity). The moderate scenario is marginal. The
pessimistic scenario means dynamics adds nothing beyond RSALOR. The proposal
needs to demonstrate the optimistic or moderate scenario to have a publishable
finding.

**Key implication:** The ceiling is not fatal to Gamma if the study is
designed to detect delta-Spearman >= 0.04 on binding/activity assays. But
it means the combined paper's integration claim ("better physics leads to
better predictions") will be attenuated. The S2 R^2 --> fitness Spearman
correlation across generators will be weak (rho ~0.3-0.5 rather than the
0.6-0.8 one might naively expect), requiring the 14x10 design to detect.

**Verdict on ceiling: PARTIALLY CONCUR with dynrev.** The ff14SB ceiling
is real and constrains the integration claim. But it does not kill Gamma
as a standalone fitness prediction study, provided the study targets
binding/activity assays where the dynamics signal is expected to be
strongest and where RSALOR is weakest (Spearman 0.416 on binding, 0.479
on activity).

---

### 1.2 Boltz-2 Inclusion in the Combined Paper

**dynrev finding:** Boltz-2 RMSF Spearman 0.76-0.84 vs BioEmu 0.69-0.75
on mdCATH/ATLAS. Boltz-2 outperforms on per-residue fluctuations. But
BioEmu produces better ensemble diversity.

**My Round 2 revision:** I revised "Boltz-2 RMSF superiority" downward.
Boltz-2 and BioEmu are comparable on RMSF, with marginal Boltz-2 advantage
(0.01-0.09 depending on benchmark and metric). Not a dramatic gap.

**CONCUR that Boltz-2 should be included, but for a different reason than
dynrev suggests.**

The strategic argument for including Boltz-2 is not that it is better than
BioEmu (it may or may not be for fitness-relevant features), but that it
adds a critical data point to the integration scatter plot. The current
scatter plot has:

- 3 classical FFs (ff14SB, ff19SB, CHARMM36m): expected to cluster in
  "moderate S2 accuracy, moderate fitness prediction" region
- 1 NMR-aware ML FF (Garnet): contaminated, expected near classical FFs
- 2 MLFFs (MACE-OFF24, SO3LR): unknown, the exciting unknowns
- 1 generative model (BioEmu): expected in "high S2 accuracy" region

Adding Boltz-2 provides:
- 1 additional generative model, creating a "BioEmu vs Boltz-2" within-
  category comparison that tests whether ensemble diversity (BioEmu's
  advantage) or per-residue accuracy (Boltz-2's advantage) matters more
  for fitness prediction
- This is a GENUINELY INTERESTING FINDING regardless of the result

If BioEmu-derived features predict fitness EQUALLY WELL as Boltz-2-derived
features despite Boltz-2's RMSF advantage, this suggests that ensemble
diversity (BioEmu) matters more than per-residue accuracy for function
prediction. This is a publishable insight.

If Boltz-2-derived features predict fitness BETTER than BioEmu-derived
features, this strengthens the "accuracy matters" narrative and supports the
combined paper's thesis.

Either outcome enriches the paper. Therefore:

**Recommendation: INCLUDE Boltz-2 as a mandatory ensemble generator for the
8 overlap proteins.** Boltz-2 ensembles are trivial to generate (seconds per
protein, open-source, MIT license). The compute cost is negligible compared
to MD simulations. This is a free additional data point that strengthens the
paper under either outcome.

Furthermore, Boltz-sample (Rosenstein et al., bioRxiv January 2026) provides
a tunable diversity parameter (beta scaling of the pair representation). This
means the combined paper could include MULTIPLE Boltz-2 conditions (e.g.,
beta=0.5, beta=1.0, beta=2.0), creating a within-generator diversity
gradient. This is arguably more informative than the between-generator
comparison because it isolates the diversity variable.

**Verdict: CONCUR with dynrev on inclusion.** Boltz-2 is a mandatory
addition. Include standard Boltz-2 (X-ray conditioning) and Boltz-2 (MD
conditioning) at minimum. Consider Boltz-sample with 2-3 beta values as
bonus data points for the integration plot.

---

### 1.3 BioEmu Augmented MD Preprint Implications

**dynrev finding:** BioEmu augmented MD (bioRxiv v2, February 2026)
demonstrates that raw BioEmu + MD + MSMs capture kinetics on CDK2 and BRAF.
Failure on GlyT1 and plasmepsin-II. Gamma uses raw BioEmu for feature
extraction.

**CONCUR that this is a concern, but it is manageable.**

The augmented MD preprint targets KINETIC information (transition rates,
metastable state populations). Gamma targets EQUILIBRIUM-AVERAGED features
(RMSF, S2, contact frequency). These are different physical quantities:

- Kinetics require correct barrier heights and transition path sampling
- Equilibrium features require correct free energy landscape shape but
  NOT correct barrier heights

BioEmu's documented strength is equilibrium distribution sampling (it was
trained on equilibrium ensembles from ff14SB MD). The augmented MD paper
shows BioEmu needs MD refinement for KINETICS, not for equilibrium
averages. For Gamma's features (RMSF, contact frequency, S2), raw BioEmu
is expected to be adequate.

**However, the reviewer objection is predictable.** A reviewer WILL cite
the augmented MD paper and ask: "Why not use augmented BioEmu?" The pre-
emption should be:

1. Gamma extracts equilibrium features (RMSF, contacts), not kinetic
   features (transition rates). Raw BioEmu is sufficient for equilibrium
   averages (Aryal et al., IJMS 2026).
2. Augmented BioEmu+MD would add significant compute cost (~10-100x per
   protein) and defeat the purpose of BioEmu as a FAST alternative to MD.
3. As a sensitivity analysis, include augmented BioEmu for 2-3 pilot
   proteins and compare feature values to raw BioEmu. If features are
   similar, raw BioEmu is validated. If different, report both.

**Verdict: CONCUR with dynrev that this requires pre-emption.** Include a
2-3 protein sensitivity analysis comparing raw vs augmented BioEmu features.
Cost: ~50-100 additional GPU-hours. This is cheap insurance against a
predictable reviewer objection.

---

## Section 2: Response to statrev's Effect Size Concerns (S1, S3)

### 2.1 Smallest Biologically Meaningful Improvement Over RSALOR

**statrev finding:** At rho=0.5, even the 14x10 design has only ~80% power.
JZS prior recommended as primary Bayesian test. The question: what is the
smallest improvement that justifies "dynamics adds value"?

**CONCUR with statrev's statistical analysis. My biological answer:**

The smallest biologically meaningful improvement in Spearman correlation over
RSALOR is **delta-rho >= 0.04 on binding assays and delta-rho >= 0.03 on
activity assays.** Here is my reasoning:

**Argument from practical significance:**

A protein engineer deciding whether to generate BioEmu ensembles (cost:
~2,000 conformations in minutes, negligible compute) vs running RSALOR
(cost: seconds, pip install) would switch workflows only if the dynamics-
augmented method consistently ranks the top mutations better. The relevant
metric is not average Spearman across all variants, but rank fidelity in
the TOP-K mutations (the ones the engineer would actually test).

For a typical DMS assay with ~2,000 variants, improving Spearman from 0.416
to 0.456 (delta = 0.04) on binding assays translates to approximately:
- 3-5 additional correctly ranked top-20 mutations (out of 20)
- 1-2 additional truly beneficial mutations in the top-10 selection

This is practically meaningful for a protein engineer who screens 10-20
variants per round. Below delta=0.03, the improvement in top-K ranking is
within the noise of the experimental assay itself.

**Argument from statistical detectability:**

ProteinGym has 14 binding assays and 43 activity assays. Using a paired
Wilcoxon signed-rank test on per-assay Spearman differences:

| Assay Type | N assays | delta-rho | SE of mean Spearman | Power (paired Wilcoxon) |
|------------|----------|-----------|--------------------|-----------------------|
| Binding | 14 | 0.04 | ~0.03 | ~65% |
| Binding | 14 | 0.06 | ~0.03 | ~85% |
| Activity | 43 | 0.03 | ~0.02 | ~70% |
| Activity | 43 | 0.05 | ~0.02 | ~90% |

The SE estimates assume per-assay Spearman SD of ~0.12 (typical for
ProteinGym methods across assays within a category). At N=14 binding assays
and delta=0.04, power is ~65% -- marginal but detectable. At N=43 activity
assays and delta=0.03, power is ~70% -- better.

**Combining binding + activity (N=57 assays):** At delta=0.03, power
reaches ~80%. This is the minimal threshold for a publishable finding:
dynamics features improve binding+activity prediction by Spearman 0.03,
detected across 57 ProteinGym assays with 80% power.

**Is rho=0.5 realistic for the integration?**

The prior evidence:

| Study | Proteins | rho (dynamics-fitness) | Nature of correlation |
|-------|----------|----------------------|----------------------|
| Ozkan et al. 2025 | 4 | ~0.6 (epistasis) | ENM dynamics -> GNN -> DMS fitness |
| Burgin QDPR 2025 | 2 (GB1, AvGFP) | Not reported as rho | MD features -> CNN -> fitness |
| MutRobustness 2026 | 2,000+ natural | median ~0.6 | Predicted ddG robustness -> RMSF |
| MutRobustness 2026 | 759 NMR | median ~0.6 | Predicted ddG robustness -> S2 |
| ESMDance 2026 | 412 | 0.46 median Spearman | Dynamics-trained PLM -> DMS fitness |

The MutRobustness rho=0.6 is the strongest prior, but it measures the
REVERSE direction (fitness -> dynamics) and uses PREDICTED ddG, not
experimental DMS fitness. The Ozkan rho~0.6 is on 4 proteins only --
unstable. ESMDance 0.46 is on a non-standard ProteinGym subset.

**My estimate for the integration (S2 accuracy vs fitness prediction
across generators):** rho=0.4-0.6 is plausible if the relationship
exists, with the lower end more likely because of the BioEmu ff14SB
attenuation. At rho=0.4, the 14x10 design has ~55-60% frequentist power
and ~70% with Bayesian JZS. At rho=0.5, ~80% frequentist power with
14x10.

**Verdict: rho=0.5 is optimistic but not unreasonable.** The minimum
viable target should be rho=0.4, which requires the 14x10 design with
Bayesian supplementation. At rho=0.3, the integration is undetectable
regardless of design.

---

### 2.2 MutRobustness Differentiation via Experimental DMS Data

**statrev question:** Given MutRobustness (2,000+ proteins, |rho|~0.6),
can Gamma differentiate by using EXPERIMENTAL DMS data? How many ProteinGym
assays have both experimental fitness data AND sufficient protein dynamics
information?

**This is the most important strategic question for Gamma's novelty claim.**

**MutRobustness uses predicted ddG (ThermoMPNN), not experimental DMS
fitness.** This is a critical distinction:

1. ThermoMPNN predicts ddG from structure, trained on ProTherm and
   Megascale datasets. The "robustness" metric is the SD of predicted ddG
   across 19 substitutions per position -- a COMPUTED quantity.

2. Experimental DMS fitness measures the ACTUAL functional effect of
   mutations in a biological assay. DMS fitness includes effects on folding
   stability, binding, catalysis, expression, and cellular fitness -- many
   of which are NOT captured by ddG alone.

3. The correlation between predicted ddG (ThermoMPNN) and experimental DMS
   fitness is itself imperfect. From ProteinGym data, ddG-based predictors
   (FoldX, Rosetta, ThermoMPNN) achieve Spearman ~0.35-0.45 on stability
   assays and ~0.20-0.30 on binding/activity assays. This means
   MutRobustness's rho=0.6 between predicted ddG robustness and dynamics
   is partially circular: ThermoMPNN is structure-aware, and structure
   correlates with dynamics.

4. **Gamma's use of experimental DMS fitness is genuinely novel.** The
   question "do dynamics features predict EXPERIMENTAL DMS fitness better
   than sequence alone?" has NOT been answered at scale. MutRobustness
   answers a different question: "does predicted thermodynamic robustness
   correlate with dynamics?"

**How many ProteinGym assays have both experimental fitness AND dynamics
information?**

I define "sufficient dynamics information" as having either:
(a) Published NMR S2 order parameters, or
(b) PDB structure suitable for BioEmu ensemble generation (single-chain,
    folded, <500 residues)

For criterion (b), essentially ALL 217 ProteinGym assays qualify, because
BioEmu can generate ensembles for any protein with a PDB structure. This
is the power of using BioEmu: dynamics information is computed, not
measured, so the coverage is universal.

For criterion (a), the overlap is small. From the BMRB, approximately 119
proteins have published S2 order parameters (ChemRxiv 2023 estimate). The
overlap with ProteinGym's 217 assays (covering ~200 distinct proteins) is
estimated at ~10-20 proteins. The Alpha-M benchmark set (ubiquitin, GB3,
BPTI, barnase, HEWL, T4 lysozyme, crambin) includes proteins with NMR S2
data, but not all are in ProteinGym:

| Protein | In ProteinGym? | NMR S2? | Assay Type |
|---------|---------------|---------|-----------|
| Ubiquitin | Yes (UBE4B, UBI4) | Yes | Activity |
| GB3 | No | Yes | N/A |
| BPTI | No | Yes | N/A |
| Barnase | Yes (RNAS1_BACAM) | Yes | Activity, Binding |
| HEWL | No direct DMS | Yes | N/A |
| T4 Lysozyme | Yes (LYS_BPT4) | Yes | Activity, Stability |
| Crambin | No DMS | No NMR S2 | N/A |

The overlap is thin: ubiquitin, barnase, and T4 lysozyme are in BOTH
ProteinGym AND have NMR S2 data. This is N=3 for the "full validation"
where experimental dynamics AND experimental fitness are both available.

**However, Gamma does not need NMR S2 for its fitness prediction task.**
Gamma uses BioEmu-COMPUTED dynamics features (RMSF, contacts, etc.) to
predict experimental DMS fitness. The NMR S2 data is needed only for the
Alpha-M integration (validating force field accuracy). For the Gamma
standalone study, all 217 ProteinGym assays are usable.

**The differentiation from MutRobustness is therefore:**

| Feature | MutRobustness | Gamma |
|---------|--------------|-------|
| Fitness measure | Predicted ddG (ThermoMPNN) | Experimental DMS fitness |
| Dynamics measure | MD RMSF, B-factors, S2 | BioEmu RMSF, contacts, S2 (computed) |
| Scale | 2,000+ proteins | 150+ ProteinGym proteins |
| Direction | Fitness -> Dynamics | Dynamics -> Fitness |
| Assay types | N/A (single ddG metric) | Binding, Activity, Stability, etc. |
| Stratification | By protein family | By assay type |
| Novelty of fitness | LOW (predicted) | HIGH (experimental) |

**This differentiation is STRONG.** Gamma uses experimental DMS fitness,
stratifies by assay type, and tests the predictive direction (dynamics ->
fitness). MutRobustness uses predicted ddG and tests the reverse direction.
These are complementary, not competing.

**Verdict: CONCUR with statrev that the differentiation question is
critical.** The answer is: Gamma CAN differentiate by using experimental
DMS fitness across all 5 ProteinGym assay types, not just the single ddG
metric that MutRobustness uses. This should be the lead differentiator in
the paper's introduction. The paper should explicitly state: "Unlike
MutRobustness (Zuk, 2026), which correlates predicted ddG robustness with
dynamics, we test whether dynamics features predict EXPERIMENTAL fitness
across 150+ deep mutational scanning assays spanning binding, activity,
expression, stability, and organismal fitness."

---

### 2.3 Revised Power Assessment for the Integration

Combining dynrev's ceiling analysis and statrev's power calculations, I
provide my revised assessment of the integration's viability.

**The integration correlation we are trying to detect:**

- X-axis: S2 R^2 (or RMSF Pearson) for each generator on each protein
- Y-axis: Delta-Spearman over RSALOR for each generator on each protein
- Each point: one (protein, generator) pair
- Claim: positive correlation (better S2 -> better fitness prediction)

**Expected effect size (my revised estimate):**

The signal chain from S2 accuracy to fitness prediction improvement is:

1. S2 accuracy varies across generators. Expected range: R^2 = 0.30
   (poor MLFF) to 0.62 (BioEmu/ff14SB). This gives a spread of ~0.32
   in S2 R^2.

2. The fitness prediction improvement correlates with RMSF accuracy, not
   directly with S2 R^2. RMSF is more relevant for fitness prediction
   (per-residue flexibility). RMSF correlation with S2 is r~0.7-0.8.
   So the effective range in fitness-relevant accuracy is ~0.22-0.26.

3. The fitness prediction improvement over RSALOR is bounded by delta ~0.04-
   0.06 (optimistic) on binding/activity. This improvement varies across
   generators proportionally to their dynamics accuracy.

4. The correlation between (3) and (1) across generators and proteins is
   the target. Given the attenuation, I estimate rho = 0.35-0.55.

**Design requirements:**

| Target rho | Design | Frequentist Power | Bayesian (JZS) Power | Verdict |
|-----------|--------|-------------------|---------------------|---------|
| 0.55 | 14 x 10 | ~85% | ~90% | Adequate |
| 0.45 | 14 x 10 | ~70% | ~80% | Marginal |
| 0.35 | 14 x 10 | ~50% | ~65% | Inadequate |
| 0.55 | 10 x 10 | ~72% | ~82% | Marginal |
| 0.45 | 10 x 10 | ~55% | ~70% | Inadequate |

**The 14x10 design is necessary for the integration.** Below this,
the power is insufficient for all but the most optimistic effect sizes.
Even at 14x10, the integration should be framed as "first evidence"
with Bayesian support, not as definitive proof.

**Verdict: CONCUR with statrev that 14x10 is the minimum viable design.**
The 6x8 design is DEAD for the integration claim. If 14 proteins with
NMR S2 data are not feasible (dynrev must assess this), the integration
claim should be abandoned and the papers separated.

---

## Section 3: Revised Gamma and Combined Paper Assessment

### 3.1 Should the Combined Paper Proceed or Be Separated?

**My recommendation: DEFAULT TO SEPARATION, with the combined paper as a
conditional upside.**

The rationale:

**Arguments for separation (STRONG):**

1. **Statistical power.** The 6x8 integration design has ~42% power at
   rho=0.5. Even expanding to 14x10 gives only ~80% at rho=0.5. If the
   true effect is rho=0.4, power drops to ~70% with Bayesian analysis.
   The integration claim is fragile.

2. **NCS editorial risk.** NCS has published zero force field benchmark
   papers, zero dynamics-to-fitness papers, and zero papers combining
   the two. The combined paper would be first-of-kind, which means
   either a trailblazing opportunity or an editorial dead end. I estimate
   50-50 on whether the NCS editor even sends it for review. The
   "straightforward ML" editorial bar is high, and the Gamma component
   uses standard ML (MLP, XGBoost, GATv2).

3. **Timeline risk.** The combined paper requires BOTH Alpha-M AND Gamma
   to succeed. If either component fails, the combined paper is dead but
   the successful component could still be published separately. Starting
   with separation reduces the blast radius of individual failures.

4. **The integration claim may be unsurprising.** "Better physics leads
   to better predictions" is the default expectation. A positive result
   is expected and therefore less interesting. A null result ("dynamics
   accuracy is orthogonal to fitness prediction quality") would be more
   surprising and more publishable, but this requires framing the paper
   differently.

**Arguments for combination (MODERATE):**

1. **The claim is completely unoccupied.** No published paper has
   correlated force field validation quality with downstream functional
   prediction quality. This is confirmed by both my Round 2 research and
   the Round 2 synthesis. The claim is genuinely novel.

2. **If the effect is strong (rho > 0.5), the combined paper is a
   conceptual advance.** Establishing the principle that "physical
   accuracy predicts functional utility" for the first time would be a
   real contribution to the field.

3. **The combined paper has a higher impact ceiling.** NCS combined >
   NatMeth Alpha-M standalone + Bioinformatics Gamma standalone. If it
   works, the payoff is larger.

4. **BioEmu ensembles are evaluated by both halves.** Alpha-M evaluates
   BioEmu's dynamics accuracy; Gamma evaluates BioEmu's fitness
   prediction utility. The same data serves both purposes, creating a
   natural connection.

**My assessment of the balance:**

The arguments for separation are stronger because the statistical
constraints (power, effective N, noise floor) are HARD constraints that
cannot be wished away. The arguments for combination are strategic
(higher impact ceiling) but depend on a large, consistent effect that
may not exist.

**Recommendation: Proceed with BOTH Alpha-M and Gamma as independent
work streams from May 1 to August 31. Design the experiments so that
the integration analysis is POSSIBLE but not REQUIRED.** At August 31,
evaluate the pilot data and decide:

### 3.2 August 31 Decision Criteria

**COMBINE if ALL of the following hold:**

1. **Alpha-M pilot success:** At least 4 of 7 benchmark proteins have
   MLFF trajectories >= 10 ns without structural collapse. S2 R^2 values
   span a range of >= 0.20 across generators (i.e., there is meaningful
   variation in dynamics accuracy to correlate with).

2. **Gamma pilot success:** On the first 30-50 ProteinGym proteins
   processed, dynamics-augmented Spearman exceeds RSALOR by >= 0.03 on
   binding+activity assays (one-sided p < 0.10 by paired Wilcoxon).

3. **Integration pilot:** For the 3-4 proteins with both Alpha-M S2 data
   and Gamma fitness predictions, the correlation between S2 accuracy and
   fitness improvement is positive (rho > 0.2, even if not significant
   at this small N).

4. **Feasibility of 14x10 design:** dynrev and implrev confirm that 14
   proteins with NMR S2 data are simulatable, and 10 ensemble generators
   are available and distinct.

**SEPARATE if ANY of the following hold:**

1. **Gamma fails:** Dynamics-augmented Spearman does NOT exceed RSALOR by
   >= 0.03 on binding+activity in the pilot (30-50 proteins).

2. **Integration negative:** The correlation between S2 accuracy and
   fitness improvement is negative or zero across the pilot proteins.

3. **Alpha-M trajectory failure:** Fewer than 3 MLFFs produce trajectories
   >= 10 ns on >= 3 proteins.

4. **14x10 infeasible:** Fewer than 14 proteins with NMR S2 data are
   available or simulatable.

**Separation fallback venues:**

| Component | Primary Venue | Fallback Venue |
|-----------|--------------|---------------|
| Alpha-M standalone | NatMeth | JCTC |
| Gamma standalone (positive result) | Bioinformatics | PLOS Comp Bio |
| Gamma standalone (stratified result) | Genome Research | PLOS Comp Bio |
| Delta standalone | NatMeth | Genome Biology |

### 3.3 Updated Verdict with CONCUR/PARTIALLY CONCUR/DISAGREE Markers

**V1. dynrev's BioEmu ff14SB ceiling constrains but does not kill Gamma.**

**PARTIALLY CONCUR.** The ceiling is real (R^2=0.62) and attenuates the
dynamics signal by ~50%. But the remaining signal (~0.04-0.06 delta-
Spearman on binding/activity in the optimistic scenario) is detectable
with proper design. The ceiling is more damaging to the INTEGRATION claim
than to the STANDALONE fitness prediction claim, because the integration
requires detecting a correlation across generators at attenuated effect
sizes.

**V2. statrev's power analysis makes the 6x8 integration design unviable.**

**CONCUR.** The 6x8 design with ~42% power at rho=0.5 is insufficient.
The 14x10 design is the minimum. If 14x10 is infeasible, the integration
should be abandoned. The Bayesian JZS prior should be primary, as statrev
recommends.

**V3. The N(0.5, 0.15^2) Bayesian prior is indefensible.**

**CONCUR.** The 4:1 prior-to-data ratio is unacceptable for a first-of-
kind study. JZS default as primary, with four-prior sensitivity analysis
(JZS, weakly informative, informative, skeptical). The decision rule:
claim supported if BF_10 > 3 under JZS AND BF_10 > 1 under skeptical
prior.

**V4. Boltz-2 should be included as a mandatory ensemble generator.**

**CONCUR with dynrev's recommendation, EXTENDED.** Include Boltz-2
(X-ray conditioning) and Boltz-2 (MD conditioning) at minimum. The
BioEmu vs Boltz-2 comparison on fitness prediction is a publishable
sub-finding regardless of outcome.

**V5. The combined paper should proceed ONLY as a conditional upside.**

**DISAGREE with the Round 2 synthesis framing of 40% viability.** I
revise downward to 30-35%. The statistical power constraints are harder
than the synthesis acknowledges. The default strategy should be
separation with conditional combination if August 31 thresholds are met.

**V6. RSALOR remains the most critical baseline.**

**CONCUR with my own Round 1/2 assessment, STRENGTHENED.** RSALOR at
0.465 (leaderboard) / 0.473 (paper) is the inescapable baseline. On
binding assays specifically, RSALOR is 0.416. ProSST-2048 is 0.445.
Gamma must beat BOTH on binding to claim dynamics adds value beyond
static structure. On activity assays, RSALOR is 0.479 -- already
competitive with top methods. The bar is high.

**V7. Gamma's differentiation from MutRobustness is via experimental
DMS fitness and assay-type stratification.**

**NEW POSITION.** MutRobustness establishes the dynamics-fitness link
at scale but uses predicted ddG, not experimental DMS. Gamma's novelty
is: (a) experimental DMS fitness, (b) assay-type stratification, (c)
integration with force field quality. The paper must lead with this
differentiation.

**V8. Assay-type stratification remains the paper's best finding.**

**CONCUR with my Round 1 position, STRENGTHENED.** The question "for
which types of protein function do dynamics add predictive value beyond
sequence?" is more interesting, more publishable, and more robust than
the overall win rate. The paper should be structured around this
question. Expected answer: dynamics helps for binding and catalysis
(where conformational selection is biophysically relevant) but not for
stability (where thermodynamic models dominate).

---

## Section 4: Specific Quantitative Requirements for Each Scenario

### 4.1 Combined Paper (NCS Target): Requirements

If the August 31 decision favors combination, the NCS submission requires:

1. **14 proteins x 10 generators** for the integration analysis.
   Proteins must have NMR S2 data (for Alpha-M) AND be in ProteinGym
   (for Gamma). The overlap set is small (~10-20 proteins) and must be
   carefully selected.

2. **Integration correlation rho > 0.4** with BF_10 > 3 under JZS prior.
   This is the central claim. If rho < 0.3, the claim is unsupported.

3. **Delta-Spearman > 0.04** over RSALOR on binding+activity (combined
   N=57 assays, paired Wilcoxon p < 0.05). This is the Gamma component's
   contribution.

4. **Assay-type stratification** showing dynamics features improve
   binding (delta > 0.04) and activity (delta > 0.03) but NOT stability
   (delta ~ 0.00). The null result on stability is as important as the
   positive result on binding/activity.

5. **Full ablation:** ESM2+RSA vs ESM2+RSA+RMSF vs ESM2+RSA+all dynamics
   features. If RMSF alone explains > 80% of the dynamics improvement,
   report this transparently.

6. **RSALOR + ProSST + S3F-MSA** as mandatory baselines per assay type.

7. **Boltz-2 as ensemble generator** alongside BioEmu, classical FFs,
   and MLFFs.

8. **Citations and positioning** against Ozkan (PNAS 2025), Burgin QDPR
   (JCIM 2025), MutRobustness (bioRxiv 2026), ESMDance (PNAS 2026).

### 4.2 Separated Alpha-M (NatMeth Target): Requirements

1. **7 proteins x 8+ generators** (no expansion needed beyond the
   current design).
2. **Pre-registered protocol** with adaptive trajectory lengths.
3. **Garnet contamination** handled by reporting contaminated vs clean
   results separately.
4. **BioEmu disulfide check** for BPTI and HEWL before committing.
5. **S2, J-coupling, and RMSF** as dynamics observables.
6. **Open-source benchmark framework** (software deliverable for NatMeth).

### 4.3 Separated Gamma (Bioinformatics/PLOS Comp Bio Target): Requirements

1. **150+ ProteinGym proteins** with BioEmu ensembles.
2. **RSALOR as mandatory baseline** with per-assay-type comparison.
3. **Assay-type stratification** as primary finding.
4. **Ablation:** ESM2+RSA vs ESM2+RSA+RMSF vs full dynamics features.
5. **Win rate > 57%** on binding+activity (raised from 55%, per statrev's
   power analysis). At N=57 binding+activity assays, 57% win rate is 32-33
   wins, which gives p~0.10 by one-sided binomial -- marginal. Prefer
   paired Wilcoxon on per-assay Spearman differences.
6. **Boltz-2 as comparison generator** (BioEmu vs Boltz-2 features).
7. **Compute-normalized comparison:** improvement per GPU-hour.

---

## Section 5: Remaining Concerns Not Addressed by Other Reviewers

### 5.1 The RMSF-Conservation-RSA Collinearity Problem

Neither dynrev nor statrev has addressed the elephant in the room: RMSF
is correlated with conservation (r ~0.3-0.5) and RSA (r ~0.4-0.6). These
are exactly the two features in RSALOR. If Gamma's dynamics features
improve over ESM2 but not over RSALOR, it would suggest dynamics is a
PROXY for conservation+RSA, not an independent information source.

The critical experiment is:

```
Model 1: ESM2-650M + RSA                    (no dynamics)
Model 2: ESM2-650M + RSA + RMSF             (add dynamics)
Model 3: ESM2-650M + RSA + RMSF + S2 + ...  (all dynamics)
Model 4: RSALOR                             (conservation + RSA)
Model 5: RSALOR + RMSF                      (conservation + RSA + dynamics)
```

If Model 2 > Model 1 but Model 5 ~ Model 4, then RMSF adds to ESM2 but
is redundant with conservation. The dynamics signal is merely re-encoding
evolutionary information through a physics-based proxy.

If Model 5 > Model 4, then dynamics provides genuinely new information
beyond conservation. This is the publishable finding.

**This ablation must be the CENTRAL hypothesis test, not a secondary
analysis.** I have stated this in Rounds 1 and 2. It remains my primary
requirement for any publication of Gamma results.

### 5.2 The ProteinGym Binding Assay Limitation

ProteinGym has only 14 binding assays (vs 43 activity, 66 stability, 77
organismal fitness, 17 expression). Binding is the category where dynamics
features are MOST expected to help (conformational selection for binding
requires sampling multiple states). But N=14 gives low power.

The proposal should consider supplementing ProteinGym binding assays with
additional DMS datasets not in the standard ProteinGym benchmark:
- ACE2-RBD binding DMS (multiple datasets from COVID-19 studies)
- Antibody-antigen DMS datasets (many available)
- PPI interface DMS datasets

Adding 5-10 binding DMS datasets from the literature would increase N to
19-24, substantially improving power for the binding-specific claim. This
is a modest effort (downloading published data, computing BioEmu
ensembles, running the prediction pipeline) that dramatically strengthens
the most important finding.

### 5.3 The "Compute-Normalized" Comparison Is Missing

For a practical audience, the relevant question is not "does dynamics help?"
but "does dynamics help per GPU-hour?" BioEmu generates 2,000 conformations
in ~10-30 minutes on a single GPU. ESM2 inference takes seconds. RSALOR
takes seconds with zero GPU.

If dynamics features improve Spearman by 0.04 at a cost of 30 GPU-minutes
per protein, while ESM2+RSA achieves a baseline of 0.465 at ~0 GPU cost,
the improvement efficiency is:

- Delta-Spearman per GPU-hour: 0.04 / 0.5 = 0.08 per GPU-hour

This is reasonable. But if the improvement is only 0.02, the efficiency
drops to 0.04 per GPU-hour, and a protein engineer would reasonably choose
RSALOR (free, instant, nearly as good).

The paper should include a "compute-normalized leaderboard" showing
improvement per GPU-hour for dynamics-augmented vs sequence-only methods.
This is a practical contribution that benchmarking papers often omit.

---

## Section 6: Final Verdict Summary

### Combined Gamma+Alpha-M (NCS Target)

**Verdict: MAJOR REVISION. Viability: 30-35%.**

The combined paper has a conceptually appealing and completely unoccupied
claim. But the statistical power constraints (requires 14x10 design for
~80% power at rho=0.5), the BioEmu ff14SB ceiling (attenuates the
dynamics-to-fitness signal by ~50%), and the NCS editorial risk (zero
precedent for FF benchmarks + fitness prediction papers) make success
contingent on multiple things going right simultaneously. Default to
separation.

### Alpha-M Standalone (NatMeth Target)

**Verdict: MINOR-TO-MAJOR REVISION. Viability: 65-70%.**

I defer to dynrev on MLFF feasibility and implrev on compute. From an
ML/biology perspective, Alpha-M as a standalone benchmark is a solid
NatMeth paper that does not require Gamma to succeed. The benchmark
framework, open-source tools, and novel dynamics observables (not just
RMSD) are sufficient contributions. Main risks: MLFF trajectory failures,
Garnet contamination.

### Gamma Standalone (Bioinformatics / PLOS Comp Bio Target)

**Verdict: MAJOR REVISION. Viability: 45-50%.**

Gamma can stand alone as a large-scale evaluation of dynamics features
for fitness prediction, provided it beats RSALOR on binding+activity
by >= 0.03 Spearman, includes the full ablation (ESM2+RSA vs
ESM2+RSA+dynamics), and frames assay-type stratification as the primary
finding. The venue target drops to Bioinformatics or PLOS Computational
Biology without the Alpha-M integration. With a surprising stratification
result, Genome Research is possible.

### Delta Standalone (NatMeth Target)

**Verdict: MINOR REVISION. Viability: 75-80%.**

No change from my Round 1/2 assessment. Delta is the strongest proposal.
My recommendations on distributional metrics (secondary track, not co-
primary), FDR correction (BH primary per statrev), and Tahoe-x1 inclusion
remain.

---

## References

1. Tsishyn, M., Hermans, P., Rooman, M., and Pucci, F. (2025). Residue
   conservation and solvent accessibility are (almost) all you need for
   predicting mutational effects in proteins. Bioinformatics 41(6): btaf322.

2. Notin, P., Kollasch, A.W., Ritter, D., et al. (2023). ProteinGym:
   Large-Scale Benchmarks for Protein Fitness Prediction and Design. NeurIPS
   Datasets Track.

3. ProteinGym v1.3 Substitution Benchmark CSV. GitHub: OATML-Markslab/
   ProteinGym. Accessed April 15, 2026.

4. Ozkan, S.B. et al. (2025). A protein dynamics-based deep learning model
   enhances predictions of fitness and epistasis. PNAS 122(42): e2502444122.

5. Burgin, T.E. (2025). Quantified Dynamics-Property Relationships:
   Data-Efficient Protein Engineering with Machine Learning of Protein
   Dynamics. J. Chem. Inf. Model. 65(21): 11979-11987.

6. Zuk, O. (2026). Mutational Robustness Predicts Protein Dynamics Across
   Natural and Designed Proteins. bioRxiv 2026.03.19.713008v1.

7. Hou, L., Zhao, Q., and Shen, Y. (2026). Protein Language Models Trained
   on Biophysical Dynamics Inform Mutation Effects. PNAS 123: e2530466123.

8. Lewis, S., Hempel, T., Jimenez-Luna, J., et al. (2025). Scalable
   emulation of protein equilibrium ensembles with generative deep learning.
   Science 369: 270-278.

9. Wohlwend, J., Passaro, S., Corso, G., et al. (2025). Boltz-2: Towards
   Accurate and Efficient Binding Affinity Prediction. bioRxiv
   2025.06.14.659707.

10. Rosenstein, B., et al. (2026). Steering Conformational Sampling in
    Boltz-2 via Pair Representation Scaling. bioRxiv 2026.01.23.701250.

11. Zha, J., Li, N., Li, M., et al. (2026). Assessing the Performance of
    BioEmu in Understanding Protein Dynamics. Int. J. Mol. Sci. 27(6): 2896.

12. BioEmu augmented MD preprint (2026). Accelerated sampling of protein
    dynamics using BioEmu augmented molecular simulation. bioRxiv
    2026.01.07.698041v2.

13. Wetzels, R. and Wagenmakers, E.J. (2012). A default Bayesian hypothesis
    test for correlations and partial correlations. Psychonomic Bulletin &
    Review 19: 1057-1064.

14. Smith, L.J., et al. (2024). The Accuracy and Reproducibility of
    Lipari-Szabo Order Parameters From Molecular Dynamics. J. Phys. Chem.
    B 128: 10813-10822.

15. Nature Computational Science editorial (2021). To review or not to
    review. Nat. Comput. Sci. 1: 226.

16. Notin, P. (2025). Have We Hit the Scaling Wall for Protein Language
    Models? Substack analysis.

17. Ahlmann-Eltze, C., Huber, W., and Anders, S. (2025). Deep-learning-
    based gene perturbation effect prediction does not yet outperform
    simple linear baselines. Nature Methods 22: 1657-1661.

18. Portal, N., Karroucha, W., Mallet, V., and Bonomi, M. (2026). Learning
    Dynamic Protein Representations at Scale with Distograms. bioRxiv
    2026.01.29.702509.

19. Garnet: Training a force field for proteins and small molecules from
    scratch. (2026). arXiv 2603.16770.

20. Kovacs, D.P., et al. (2025). MACE-OFF24: Short-Range Transferable
    Machine Learning Force Fields for Organic Molecules. JACS 147: 2977.

21. Kabylda, A., et al. (2026). Molecular Simulations with a Pretrained
    Neural Network and Universal Pairwise Force Fields. JACS. doi:
    10.1021/jacs.5c09558.

22. Benavoli, A., Corani, G., Demsar, J., and Zaffalon, M. (2017). Time
    for a Change: a Tutorial for Comparing Multiple Classifiers Through
    Bayesian Analysis. JMLR 18: 1-36.

23. Ly, A., Verhagen, J., and Wagenmakers, E.J. (2016). Harold Jeffreys's
    default Bayes factor hypothesis tests explained. J. Mathematical
    Psychology 75: 137-164.

24. Brbic, M., et al. (2025). Systema: A framework for evaluating genetic
    perturbation response prediction beyond systematic variation. Nature
    Biotechnology.

25. Gandhi, S., Javadi, A., et al. (2025). Tahoe-x1: Scaling
    Perturbation-Trained Single-Cell Foundation Models to 3 Billion
    Parameters. bioRxiv 2025.10.23.683759.

26. Prediction of Order Parameters based on Protein NMR Structure Ensemble
    and Machine Learning (2023). ChemRxiv 2023-ds62s-v2. Reports ~119
    protein S2 datasets in BMRB.

27. Depaoli, S., Winter, S.D., and Visser, M. (2020). The Impact of Prior
    Information on Bayesian Inference and Its Implications for Psychological
    Science. Frontiers in Psychology 11: 1032.
