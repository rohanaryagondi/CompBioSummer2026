---
agent: Computational Biology & ML Reviewer (biomlrev)
round: 1
date: 2026-04-15
type: review-assessment
scope: cross-cohort
---

# Mock NCS Reviewer 2: Gamma, Combined Narrative, and Delta Assessment

## Reviewing Agent

I am Mock NCS Reviewer 2, assigned when a paper claims ML predicts biological function
from structural or dynamic features. I have 12+ years at the intersection of ML and
structural/evolutionary biology. I contributed to ProteinGym benchmarking, built fitness
prediction models, and reviewed dozens of papers that claimed dynamics adds value beyond
sequence. My role is hostile but fair: I will find what the proposers missed, quantify
what they hand-waved, and determine whether the claimed novelty survives contact with
the current literature.

## Executive Summary

The combined Gamma+Alpha-M proposal attempts to connect force field validation quality
to downstream fitness prediction -- a conceptually appealing idea. However, the Gamma
component faces a fundamental challenge that Cohort 2 underestimates: the "dynamics
adds value beyond sequence" hypothesis is weaker than assumed, given that (a) a
parameter-free baseline (RSALOR: conservation + solvent accessibility) already achieves
Spearman 0.473 on ProteinGym, within striking distance of top methods at ~0.50, (b)
Boltz-2 (June 2025) now matches or exceeds BioEmu on RMSF prediction, undermining
BioEmu's privileged position, (c) the Ozkan et al. (PNAS 2025) dynamics-based GNN and
the Burgin (JCIM 2025) QDPR paper already occupy the "dynamics-to-fitness" niche on
ProteinGym proteins, and (d) a March 2026 bioRxiv preprint directly correlates
mutational robustness with protein dynamics (rho ~0.6) across 2,000 proteins, partially
scooping Gamma's core hypothesis. The combined paper's integration rests on N=6-8
proteins, which is statistically fragile. Delta (PerturbMark) is the strongest proposal
in the portfolio but faces a rapidly evolving competitive landscape (Systema in Nature
Biotechnology, Ahlmann-Eltze et al. in Nature Methods, Tahoe-x1 3B-parameter model).

**Overall: Gamma+Alpha-M Combined requires major revision before it could survive NCS
review. Delta requires minor revision and is publishable at Nature Methods.**

---

## Part I: Gamma Assessment

### Critical Issues

**C1. The "null dynamics" baseline is missing the most important comparison: RSALOR.**

Tsishyn et al. (Bioinformatics, June 2025) demonstrated that a parameter-free model
using only residue conservation (log-odds ratio from MSA) scaled by relative solvent
accessibility achieves Spearman 0.473 across 217 ProteinGym assays. This matches or
exceeds GEMME (0.447), TranceptEVE (0.450), and ESM2-650M (0.428). The proposal
compares Gamma against ESM2-650M and the "top-5 ProteinGym baselines" but never
mentions RSALOR or its implication: that two simple features (conservation + RSA)
already capture most of the fitness signal.

Why this is critical: If Gamma's dynamics features (RMSF, contacts, S2) are correlated
with conservation and solvent accessibility -- and they are, since flexible residues
tend to be surface-exposed and less conserved -- then Gamma may simply be recovering
the RSALOR signal through a more expensive route (2,000 BioEmu conformations per
protein vs. a single MSA query). The proposal must include RSALOR as a mandatory
baseline and demonstrate that dynamics features add value AFTER controlling for
conservation and RSA.

**Specific numbers the proposal should have cited:**
- RSALOR Spearman by assay type: Stability 0.551, Binding 0.455, Activity 0.472,
  Expression 0.428, Fitness 0.419
- ProSST-2048 (structure + PLM): 0.522
- ESM2-650M: 0.428
- GEMME: 0.447
- TranceptEVE (L): 0.450

The success threshold of "win rate >55% against top-5 on binding/catalysis" becomes
meaningless if the top-5 now includes methods at Spearman ~0.50. Gamma would need to
demonstrate Spearman improvement of >0.03 over RSALOR specifically on binding/catalysis
to claim dynamics adds value. At 150 proteins, the standard error on mean Spearman is
approximately 0.01-0.02, so a 0.03 improvement may not reach significance.

**C2. The dynamics-to-fitness niche is no longer empty.**

Cohort 2 repeatedly claims "no paper has connected ensemble dynamics to ProteinGym
fitness prediction." This is no longer true as of early 2026:

1. **Ozkan et al. (PNAS 2025):** A dynamics-based GNN using the Asymmetric Dynamic
   Coupling Index (DCIasym) from elastic network models. Tested on 4 proteins from
   ProteinGym DMS datasets. Outperforms existing approaches on epistasis prediction.
   This is exactly the "dynamics features + GNN + ProteinGym" combination that Gamma
   proposes, albeit at smaller scale.

2. **Burgin (JCIM, October 2025):** "Quantified Dynamics-Property Relationships"
   (QDPR). Uses MD-derived features (RMSF, hydrogen bonding energies, SASA, PCA
   projections) plus CNNs for fitness prediction on GB1 and AvGFP from ProteinGym.
   This is the closest prior art to Gamma: MD features mapped to DMS fitness via ML.
   The proposal does not cite this paper.

3. **"Mutational Robustness Predicts Protein Dynamics" (bioRxiv, March 2026):**
   Demonstrates that per-residue mutational robustness (from ThermoMPNN) correlates
   with MD RMSF, B-factors, and NMR S2 across ~2,000 proteins at median rho ~0.6.
   This directly establishes the dynamics-fitness connection Gamma seeks to prove,
   but from the opposite direction (fitness predicts dynamics, not dynamics predicts
   fitness).

4. **Hou et al. (PNAS 2026), ESMDance/SeqDance:** PLMs trained on dynamic properties
   from MD/NMA of 65,100 proteins. ESMDance achieves median Spearman 0.46 on
   ProteinGym (412 proteins), matching ESM2-650M. This demonstrates that dynamics
   information CAN be encoded into sequence models, but the improvement over pure
   sequence models is marginal.

**The implication:** Gamma's claim to novelty must be sharpened. "First to connect
BioEmu ensembles to ProteinGym" is factually defensible but scientifically weak if
Ozkan (2025) already showed dynamics-GNN predicts fitness, Burgin (2025) already
showed MD-features predict fitness on ProteinGym proteins, and ESMDance (2026) already
showed dynamics-aware PLMs match sequence-only PLMs on ProteinGym. Gamma's
differentiation must be the SCALE (150 proteins vs. Ozkan's 4, Burgin's 2) and the
INTEGRATION with Alpha-M -- not the concept itself.

**C3. BioEmu is no longer the only scalable ensemble generator.**

Boltz-2 (Wohlwend et al., bioRxiv June 2025) generates protein ensembles conditioned
on MD and achieves RMSF correlations with ground-truth MD that are "generally stronger"
than BioEmu and AlphaFlow on the mdCATH and ATLAS benchmarks. Boltz-2 is open-source,
runs on a single GPU, and produces ensembles in seconds.

This undermines Gamma's dependence on BioEmu in two ways:
1. A reviewer will ask: "Why BioEmu and not Boltz-2? If Boltz-2 produces better RMSF,
   why not use it?" The proposal mentions AlphaFlow and Boltz-2 as alternative
   generators in the kill criteria but never explains why BioEmu is preferred.
2. The combined paper's narrative ("BioEmu validated by Alpha-M, then used for Gamma")
   becomes less compelling if Boltz-2 is a superior ensemble generator that was not
   tested.

**Recommendation:** Add Boltz-2 as a mandatory ensemble generator for the 8 overlap
proteins. This strengthens the integration analysis (8 generators instead of 6-8)
and addresses the "why BioEmu?" objection. If Boltz-2 produces better RMSF AND better
fitness predictions, the combined paper's story is actually stronger: "Better ensembles
predict better function, regardless of the generator."

### Major Issues

**M1. The feature set is standard and the ML pipeline is off-the-shelf.**

The 13 primary features (RMSF, B-factor variance, SS propensity, S2, Rg, asphericity,
PCA amplitudes, inter-domain distance, SASA, contact frequency, MI, bimodality
coefficient, cryptic pocket occupancy) are all standard biophysical descriptors
computed with standard tools (MDAnalysis, CPPTRAJ, PocketMiner). The ML pipeline
(MLP, XGBoost, GATv2) uses standard architectures.

NCS editorial criteria explicitly state: "straightforward usage of machine learning
algorithms is usually outside the journal's scope" (NCS editorial, 2021). The proposal
tries to deflect this by arguing the novelty is in the "integration" -- but the
integration is connecting two datasets (BioEmu ensembles, ProteinGym fitness), not
developing a new method.

The comparison to AlphaFold2 (Attack Vector 4 pre-emption) is misleading. AlphaFold2
introduced novel architecture (Evoformer, invariant point attention, recycling) and a
new training paradigm. Gamma introduces no new architecture, no new training paradigm,
and no new features. The dynamics-informed GATv2 edges are the closest thing to
methodological novelty, but GATv2 with contact-based edges is established (Ozkan et
al. 2025 used a similar approach).

**M2. Win rate >55% is an extraordinarily low bar for NCS.**

The success threshold is "win rate >55% against top-5 ProteinGym baselines on
binding/catalysis." The current top-5 baselines achieve Spearman ~0.45-0.52. A 55%
win rate means Gamma beats them on slightly more than half of the assays, which could
easily be within noise.

Consider: if there are ~30-40 binding/catalysis assays in ProteinGym, a 55% win rate
means winning on 17-22 assays. Under the null hypothesis of equal performance, the
expected win rate is 50%, and the standard deviation of the win rate with N=35 assays
is sqrt(0.25/35) = 0.085 = 8.5%. So 55% is less than one standard deviation above
chance. This would not survive a binomial test at alpha = 0.05 (which requires ~60%
win rate at N=35).

**Recommendation:** Raise the success threshold to win rate >60% on binding/catalysis,
or switch to a paired Wilcoxon signed-rank test on per-assay Spearman differences
with a pre-specified effect size (e.g., median Spearman improvement > 0.02).

**M3. Overfitting risk with 13 features and 150 proteins.**

The proposal trains ML models (MLP, XGBoost, GATv2) on 13 features across 150
proteins using leave-protein-out CV. With 13 features and 150 training examples (at
the protein level), the feature-to-sample ratio is ~1:11. For XGBoost with
hyperparameter tuning, this is in the overfitting danger zone.

The proposal mentions "nested leave-protein-out CV, L1, permutation tests" as
mitigations. These are necessary but may be insufficient. The more fundamental
concern is that with 13 correlated biophysical features (RMSF correlates with S2 at
r ~0.7, with SASA at r ~0.4, with B-factor variance at r ~0.9), effective
dimensionality may be 4-5, making the feature-to-sample ratio more reasonable but
raising the question: why use 13 features when 4-5 capture the same information?

**Recommendation:** Add a principal component analysis of the 13 features across
150 proteins. If 3-4 PCs explain >90% of variance, the paper should use PCs as
features (or at least report PC-based results alongside raw features).

**M4. The SHAP + permutation importance design is necessary but not sufficient.**

SHAP values from tree-based models (XGBoost) and permutation importance are standard
interpretability tools. They answer "which features are important for the trained
model" but not "which features carry genuinely new information beyond what sequence
provides." The critical question is not "is RMSF important in our model?" (it almost
certainly will be) but "does RMSF add predictive power beyond ESM2 embeddings + RSA?"

The proposal's Stage 4 (ensemble-augmented baselines: ESM2 + RMSF, AlphaMissense +
RMSF) is the right experiment. But the proposal does not specify the statistical test
for whether the augmentation is significant. A paired test (e.g., DeLong test for
AUC, or paired Wilcoxon for Spearman) across assays is needed, with correction for
multiple comparisons.

**M5. Assay-type stratification is the real result, but the proposal underemphasizes it.**

The most interesting scientific question is: "For which types of protein function does
dynamics add value?" The proposal mentions that binding and catalysis are expected to
benefit most, but this is presented as a success criterion rather than as the primary
finding. The paper should be structured around this question, not around the overall
win rate.

ESMDance (Hou et al., PNAS 2026) showed dynamics-trained PLMs particularly benefit
viral proteins and designed proteins but not standard eukaryotic proteins. This
assay-type stratification is the publishable finding, not the overall average.
Gamma should structure its analysis similarly.

### Minor Issues

**m1.** The proposal cites "Ozkan et al. (PNAS 2025) from 4 proteins to 200" but
this is Gamma's own plan, not a cited result. The actual Ozkan paper tested 4 proteins.
Gamma's scale-up to 150 proteins is a contribution, but the framing suggests an
existing result.

**m2.** The convergence pilot (5 proteins, 500-10,000 BioEmu samples) is a good
control. However, the proposal does not specify what happens if convergence requires
>2,000 samples for some proteins. The compute budget assumes 2,000 conformations per
protein. If convergence analysis reveals that 5,000-10,000 samples are needed for
large proteins, the 215 GPU-hr budget is insufficient.

**m3.** PocketMiner for cryptic pocket occupancy is an interesting feature but has not
been validated as a fitness predictor. The feature may add noise rather than signal.
Consider making it exploratory rather than primary.

**m4.** The kill criterion "RMSF rho < 0.1 across >50% of Tier 1 proteins" at June 30
is too permissive. Raw RMSF-fitness correlation across ALL assay types should be ~0.2
(since RMSF correlates with conservation at r ~0.5-0.6, and conservation predicts
fitness at rho ~0.47). A kill criterion of rho < 0.1 would only trigger if the
BioEmu ensembles are fundamentally broken. Consider rho < 0.15 as a more informative
threshold.

---

## Part II: Combined Paper Narrative Assessment

### Novelty Analysis

The combined paper claims: "More physically accurate ensembles produce better
functional predictions." I assess this claim along three dimensions.

**1. Is this claim novel?**

Partially. No published paper has correlated force field validation quality (NMR S2
agreement) with downstream fitness prediction quality across multiple generators. In
this narrow sense, the claim is novel.

However, the claim is scientifically intuitive to the point of being unsurprising.
"Better physics gives better predictions" is the implicit assumption of every force
field development effort. The materials science analogy (UniFFBench: MLFFs with better
phonon spectra give better thermal conductivity) is apt but also illustrates the
concern: nobody would be surprised by this result. The question is whether proving it
for protein dynamics is sufficiently interesting.

**2. Does it meet the NCS bar?**

Uncertain. NCS has published benchmark papers (e.g., ProteinGym itself, Notin et al.
NeurIPS 2023, which was Datasets track, not a journal). The closest NCS precedent I
can identify is the Scouter paper (2025/2026) predicting transcriptional responses to
perturbations, which introduced a novel architecture. NCS has also published papers
on single-cell analysis (Annotatability, 2025) and protein engineering (PIC, 2025).

The pattern I see in recent NCS publications is: new method + biological insight.
The combined paper offers biological insight (dynamics-function connection) but no
new method. This is the fundamental editorial vulnerability.

**Precedent analysis:** I searched for NCS papers that combine force field benchmarking
with biological prediction. I found none. The closest analogs are:
- MOFSimBench (npj Comput. Mat., 2026): MLFF benchmark for metal-organic frameworks
- CHIPS-FF (ACS Mater. Lett., 2026): MLFF benchmark for materials properties
- Garnet (arXiv, March 2026): GNN-parameterized force field trained on NMR data

None of these appeared in NCS. Force field benchmarks have historically appeared in
JCTC, JACS, and Nature Methods, not NCS. The combined paper would be a first-of-kind
for NCS, which is either an opportunity or a red flag.

**3. Is "better physics leads to better predictions" surprising?**

Only if the result is negative or nuanced. Scenarios:
- If the correlation is strong (rho > 0.7): unsurprising, expected.
- If the correlation is weak or absent: surprising, more publishable. "Ensemble
  accuracy is orthogonal to functional prediction" would be a stronger NCS paper.
- If the correlation is assay-type-dependent: most interesting. "Accuracy matters
  for catalysis but not for stability" would be a genuine finding.

The proposal acknowledges all three outcomes (Section on BioEmu scenarios). This is
good scientific design. But the framing assumes the positive result is the publishable
one, when in fact the negative or nuanced result is more interesting and more
publishable at NCS.

### Integration Claim Assessment

**I1. N=6 primary proteins for integration is dangerously low.**

The revised plan uses 6 primary folded proteins + 2 exploratory (HIV protease, alpha-
synuclein). The within-protein Spearman correlation between S2 R2 and fitness Spearman
across 8 generators yields 6 correlation values. A one-sample Wilcoxon signed-rank
test on 6 values has very limited power.

For the Wilcoxon signed-rank test with N=6 and alpha=0.05 (one-tailed), the critical
region requires all 6 correlations to be positive (p = 2^-6 = 0.016) or at most 1
negative (p = 7/64 = 0.109). So significance requires either unanimous positive
correlations (stringent) or is unattainable with even 2 negative values. This is a
coin-flip experimental design: it works if the effect is large and consistent, but
has no power to detect moderate or variable effects.

The multilevel model (protein-generator pairs, N=48) is better powered but introduces
model assumptions (normality, linearity) that may not hold for rank correlations.

**I2. The S2-to-RMSF-to-fitness chain has multiple attenuation points.**

The integration logic is: S2 R2 (Alpha-M) -> RMSF quality -> fitness prediction
quality. But:
- S2 measures ps-ns backbone dynamics; RMSF from BioEmu integrates all sampled
  timescales
- S2 R2 depends on back-calculation (SHIFTX2/SPARTA+ add noise)
- RMSF is one of 13 features; the other 12 may dominate
- Fitness prediction quality depends on the ML model, the CV strategy, and the assay

Each link attenuates the correlation. The expected end-to-end correlation (S2 R2 vs.
fitness Spearman) may be rho ~0.3-0.4 (the joint critique estimates 0.4-0.6, which I
consider optimistic). At this effect size, N=6 proteins cannot detect it reliably.

**I3. The "Dynamics Quality-Function Plane" figure may have too few points to be
convincing.**

The proposed scatter plot (Panel A) has 8 points (generators). With error bars,
bootstrap CIs, and potential outliers, this figure may look like a cloud rather than
a trend. The proposal does not discuss what happens if the figure is unconvincing --
e.g., if 2-3 generators cluster together (classical FFs with similar S2 R2 and similar
fitness Spearman), reducing the effective range.

**Recommendation:** Power the figure with more generators. Boltz-2 should be added.
Consider also adding: AlphaFlow (if ensembles are available for the overlap proteins),
PEGASUS distograms as a "zero-MD" comparator, and normal mode analysis (ANM/GNM) as
a cheap dynamics proxy. This would increase the scatter plot to 10-12 points and
dramatically improve visual and statistical power.

---

## Part III: Delta (PerturbMark) Assessment

### Strengths

**S1. Timely and well-differentiated.**

The perturbation prediction field is in a state of crisis. Two 2025 papers have
established that current methods may not work:
- Ahlmann-Eltze et al. (Nature Methods 2025): "Deep-learning-based gene perturbation
  effect prediction does not yet outperform simple linear baselines." Compared 5
  foundation models and 2 DL models against simple baselines; none outperformed.
- Systema (Brbic et al., Nature Biotechnology 2025): Current evaluation metrics
  overestimate performance due to systematic variation. Proposed new evaluation
  framework emphasizing perturbation-specific effects.

PerturbMark occupies an important niche between these: it uses a different dataset
(Tahoe-100M chemical perturbations vs. genetic perturbations in the above), includes
cross-context generalization (organ-based holdout), and evaluates both gene-level and
distributional metrics. The Tahoe-100M dataset (100M cells, 429 compounds, 50 cancer
cell lines, CC0 license) is the ideal testbed.

**S2. The mandatory baselines are appropriate.**

Five mandatory baselines including mean expression, additive perturbation effect,
CRISPR-informed mean, per-gene linear model, and per-gene ridge regression. Given
Ahlmann-Eltze et al.'s finding that linear baselines beat DL, these baselines are
essential. The proposal correctly positions PerturbMark as asking "when does deep
learning help?" rather than assuming it does.

**S3. The difficulty tier system is well-designed.**

Tier 0 (interpolation within cell line) through Tier 3 (cross-organ, unseen compound)
creates a graduated evaluation. This allows the paper to make nuanced claims: "DL
helps at Tier 0-1 but not at Tier 2-3" would be a publishable finding with practical
implications.

**S4. Co-primary metrics (WMSE + Spearman on top-k DEGs) are non-redundant and
well-chosen.**

WMSE measures absolute error magnitude weighted by differential expression; Spearman
on top-k DEGs measures rank fidelity of the most biologically relevant genes. These
capture different failure modes and resist gaming.

### Weaknesses

**W1. The competitive landscape is moving faster than the proposal accounts for.**

Since the Cohort 2 proposal was finalized (April 14, 2026):
- **Tahoe-x1** (bioRxiv, October 2025): A 3B-parameter perturbation-trained single-
  cell foundation model trained on Tahoe-100M. Claims SOTA on perturbation response
  prediction. If Tahoe-x1 is not included in PerturbMark, the benchmark is already
  incomplete on publication day.
- **Tahoe partnership announcement (January 2026):** Tahoe Therapeutics, Arc Institute,
  and Biohub announced a new dataset 4x more perturbation-rich than Tahoe-100M
  (>120M cells, 225,000 drug-patient interactions). PerturbMark may be benchmarking
  on yesterday's data.
- **Systema (Nature Biotechnology, 2025):** The evaluation framework directly competes
  with PerturbMark's metric design. PerturbMark must differentiate on chemical
  perturbations (Systema focuses on genetic perturbations) and on the Tahoe-100M
  dataset.

**Recommendation:** Add Tahoe-x1 to the Tier 1 method catalog (it is pretrained on
the benchmark data, creating an interesting inclusion/exclusion decision). Address
the Tahoe partnership in the discussion: acknowledge that larger datasets are coming
and position PerturbMark as the evaluation framework for the current generation.

**W2. The anti-gaming measures are incomplete.**

The proposal lists: time-stamped submissions, code + environment requirement, hidden
holdout tier, data hash verification. These are standard for ML benchmarks. Missing:
- **Holdout contamination:** If methods are pretrained on Tahoe-100M (like Tahoe-x1),
  the test set may be in the pretraining data. PerturbMark needs a protocol for
  pretrained-on-benchmark methods.
- **Metric gaming via threshold selection:** WMSE requires a DEG threshold. Methods
  can optimize this threshold on the test set. The proposal should fix the DEG
  threshold in the pre-registration.
- **Adaptive overfitting:** Methods submitted after seeing the leaderboard can
  overfit to the hidden holdout. Consider a one-shot evaluation track alongside the
  iterative leaderboard.

**W3. Distributional evaluation at cell level is computationally expensive and may
not be practical for all methods.**

The proposal elevates cell-level distributional metrics to co-primary for Tiers 0-1.
Many perturbation prediction methods output pseudobulk predictions (mean gene
expression per condition), not single-cell distributions. Requiring distributional
metrics may exclude methods that only produce pseudobulk predictions, biasing the
benchmark against an entire class of approaches.

**Recommendation:** Keep distributional metrics but as a secondary track. Methods
that produce single-cell predictions get evaluated on both pseudobulk and
distributional metrics. Methods that only produce pseudobulk get evaluated on
pseudobulk only. Report both tracks transparently.

**W4. The 12-week timeline is tight for evaluating 10+ methods.**

Reproducing 10+ DL methods (GEARS, scGPT, scFoundation, CPA, scPPDM, scDFM,
AlphaCell, X-Cell, AetherCell, pertTF) on a new dataset with standardized evaluation
is a major engineering effort. The 4-week buffer for reproducibility failures is
realistic but assumes only 1-2 methods will be problematic. In practice, more than
half may require debugging, hyperparameter adaptation, or author correspondence.

---

## Assessment of Attack Vector Pre-emptions

### Attack Vector 4: "Standard features/ML, no novelty" (Probability: 70%)

**Pre-emption quality: INSUFFICIENT.**

The proposal's pre-emption relies on four arguments:
1. Novelty is in the integration, not the methods.
2. Dynamics-informed GATv2 edges are novel.
3. Frame as paradigm, not algorithm.
4. Assay-type stratification is a novel finding.

**My assessment of each:**

1. "Integration novelty" is weak for NCS. Connecting two datasets is data analysis,
   not methodological development. The NCS editorial explicitly warns against this.

2. Dynamics-informed GATv2 edges are modestly novel but incremental. Ozkan et al.
   (PNAS 2025) already used dynamics-informed GNN edges (DCIasym-weighted). The
   PEGASUS paper (Portal et al., bioRxiv 2026) uses distogram-derived edges.
   Gamma's contribution is using BioEmu contact frequency as edge weights, which is
   a minor variation.

3. The "paradigm" framing is defensible ONLY if the combined paper delivers a
   surprising finding. "Better physics gives better predictions" is not a paradigm
   shift -- it is the default expectation. A paradigm shift would be: "For catalysis,
   ps-ns dynamics predict function; for binding, us-ms dynamics predict function; for
   stability, dynamics add nothing beyond conservation." This level of stratified
   insight would be paradigm-level.

4. Assay-type stratification IS the strongest argument for novelty. But it must be
   positioned as the paper's primary contribution, not a secondary analysis. The
   current proposal buries it in the ablation phase.

**What would fix this:** Restructure the paper so the primary question is: "For which
types of protein function do conformational dynamics predict fitness beyond sequence?"
The answer (stratified by assay type) becomes the finding. The overall win rate becomes
secondary. The integration with Alpha-M becomes the validation that the dynamics signal
is physical, not artifactual.

### Attack Vector 5: "Marginal improvement does not justify compute" (Probability: 60%)

**Pre-emption quality: PARTIALLY ADEQUATE.**

The proposal's compute-matched comparison is good: Alpha-M costs ~107K GPU-hrs but
produces a community resource; Gamma adds only ~2.1K GPU-hrs. The argument that
Gamma's marginal compute is comparable to ESM2 training is fair.

However, the deeper issue is not compute cost but practical utility. If dynamics
features improve Spearman by 0.02-0.03 on average, a protein engineer would never
bother generating BioEmu ensembles when ESM2 inference takes seconds. The proposal
needs to identify a USE CASE where the dynamics improvement is practically significant:
e.g., a specific protein family where dynamics features flip the ranking of the most
beneficial mutations.

The ESM-IF1 analogy (attack pre-emption 5c) is apt: ESM-IF1 showed modest improvement
over sequence-only but opened a new modality (structure). If Gamma convincingly opens
the dynamics modality, the modest overall improvement is acceptable. But this framing
requires the paper to explicitly identify WHERE dynamics helps and WHERE it does not.

---

## Additional Issues Not Identified by Cohort 2

**A1. The "Mutational Robustness Predicts Dynamics" preprint (bioRxiv March 2026)
partially scoops Gamma's hypothesis.**

This preprint (posted March 23, 2026 -- 22 days before this review) shows that
per-residue mutational robustness (from ThermoMPNN) correlates with RMSF, B-factors,
and NMR S2 at median rho ~0.6 across ~2,000 proteins. This establishes the
dynamics-fitness link from the FITNESS side (fitness predicts dynamics) rather than
the DYNAMICS side (dynamics predicts fitness). The correlation is bidirectional:
if fitness predicts dynamics, dynamics predicts fitness.

**Impact on Gamma:** Gamma cannot claim "first evidence that dynamics correlates with
fitness" because this preprint already shows it (from the reverse direction). Gamma
CAN still claim "first systematic evaluation of dynamics as a PREDICTOR of fitness on
ProteinGym" and "first to quantify the ADDITIVE value of dynamics over sequence."

**A2. Boltz-2 RMSF superiority over BioEmu invalidates the BioEmu monopoly assumption.**

The proposal assumes BioEmu is the best available ensemble generator for fitness
prediction. Boltz-2 (June 2025) produces ensembles with stronger RMSF correlations
to ground-truth MD than BioEmu. If Gamma uses BioEmu but not Boltz-2, a reviewer will
immediately ask: "Did you try the better ensemble generator?" This is especially
damaging for the combined paper, whose integration claim depends on correlating
ensemble quality with fitness prediction quality.

**A3. The QDPR paper (Burgin, JCIM 2025) is direct prior art that was not cited.**

QDPR uses MD-derived features (RMSF, H-bond energies, SASA, PCA) plus CNNs for
fitness prediction on GB1 and AvGFP from ProteinGym. These are exactly Gamma's
features (minus S2 and cryptic pocket occupancy, plus H-bond energies). The QDPR
paper demonstrates the concept works on 2 proteins. Gamma scales to 150. This is a
legitimate contribution, but the paper MUST cite QDPR and position Gamma as the
large-scale evaluation that QDPR's pilot study called for.

**A4. The "sequence is enough" hypothesis is stronger than the proposal acknowledges.**

RSALOR (Spearman 0.473) using only conservation + RSA. VespaG (Spearman 0.48) using
PLM embeddings. ProSST-2048 (Spearman 0.522) using structure + PLM. The top of the
ProteinGym leaderboard (VenusREM, S3F-MSA) achieves ~0.50-0.58 using structure + MSA.

The gap between "sequence + static structure" and "sequence + static structure +
dynamics" must be > 0.03 Spearman to be convincing. ESMDance (PNAS 2026) trained
explicitly on dynamics data achieved median Spearman 0.46, which is BELOW RSALOR
(0.473). This is a sobering result: training a PLM on dynamics data does not
outperform a parameter-free conservation + RSA baseline.

Gamma proposes to use 13 dynamics features from BioEmu ensembles. If ESMDance's
dynamics-trained PLM cannot beat RSALOR, why would 13 hand-crafted features do
better? The proposal must address this directly.

**A5. The proposal does not adequately discuss the correlation between RMSF and
conservation/RSA.**

This is the elephant in the room. Flexible residues (high RMSF) tend to be:
- Surface-exposed (high RSA) -- correlation r ~0.4-0.6
- Less conserved -- correlation r ~0.3-0.5
- Less functionally constrained

Conservation and RSA are the two features in RSALOR (Spearman 0.473). RMSF is
correlated with both. The question is: does RMSF predict fitness BEYOND what
conservation + RSA already predict? If not, Gamma's entire 2,130 GPU-hr ensemble
generation is wasted.

The critical ablation is:
1. Baseline: ESM2-650M + RSA (no dynamics)
2. Test: ESM2-650M + RSA + RMSF
3. If improvement < 0.02 Spearman: dynamics adds nothing beyond RSA

This ablation is implicit in Stage 4 but not explicitly designed as the central
hypothesis test.

---

## Verdicts

### Gamma+Alpha-M Combined: MAJOR REVISION

**Rationale:** The combined paper has a defensible conceptual core (connecting force
field validation to functional prediction), but the Gamma component faces fundamental
challenges:

1. The "dynamics adds value beyond sequence" hypothesis is weaker than assumed, given
   RSALOR, ESMDance, and recent dynamics-fitness correlation papers.
2. The ML pipeline is standard (MLP/XGBoost/GATv2 on standard features), falling
   below NCS methodological novelty expectations.
3. The integration rests on N=6 proteins, which is statistically fragile.
4. BioEmu is no longer the unique best ensemble generator (Boltz-2).
5. Direct prior art (Ozkan 2025, Burgin 2025, mutational robustness 2026) was not
   cited and partially scoops the concept.

**Requirements for acceptance:**

- RSALOR as mandatory baseline with explicit ablation: dynamics features vs.
  conservation + RSA
- Add Boltz-2 as ensemble generator for overlap proteins
- Cite and position against Ozkan (2025), Burgin (2025), mutational robustness (2026)
- Restructure around assay-type stratification as primary finding
- Raise success threshold to >60% win rate or use formal statistical tests
- Increase integration overlap to >8 generators (add Boltz-2, AlphaFlow)
- Add a "null dynamics" baseline: ESM2 + RSA + static structure features (AlphaFold2
  pLDDT, B-factor prediction) to isolate the dynamics contribution

**If all requirements are met:** The paper could target NCS as a Resource (with the
Alpha-M benchmark data as the resource component) or as an Article if the assay-type
stratification reveals a genuinely surprising finding.

### Delta (PerturbMark): MINOR REVISION

**Rationale:** PerturbMark is well-designed, well-differentiated, and addresses a
genuine crisis in the perturbation prediction field. The competitive landscape has
evolved since the proposal was written (Tahoe-x1, Systema), but PerturbMark's focus
on chemical perturbations, cross-context generalization, and the Tahoe-100M dataset
provides sufficient differentiation.

**Requirements for acceptance:**

- Add Tahoe-x1 to method catalog (with clear protocol for pretrained-on-benchmark
  methods)
- Differentiate explicitly against Systema (genetic vs. chemical perturbations,
  different metrics)
- Address holdout contamination for pretrained models
- Keep distributional metrics as secondary track, not co-primary
- Fix DEG threshold in pre-registration to prevent metric gaming

**Confidence:** High. PerturbMark fills a genuine gap and the Tahoe-100M dataset
provides an unmatched evaluation platform. With the above modifications, this is a
strong Nature Methods paper.

---

## References

1. Tsishyn, M., Hermans, P., Rooman, M., and Pucci, F. (2025). Residue conservation
   and solvent accessibility are (almost) all you need for predicting mutational
   effects in proteins. Bioinformatics 41(6): btaf322.

2. Notin, P., Kollasch, A.W., Ritter, D., et al. (2023). ProteinGym: Large-Scale
   Benchmarks for Protein Fitness Prediction and Design. NeurIPS Datasets Track.

3. Ozkan, S., et al. (2025). A protein dynamics-based deep learning model enhances
   predictions of fitness and epistasis. PNAS 122(42): e2502444122.

4. Burgin, T.E. (2025). Quantified Dynamics-Property Relationships: Data-Efficient
   Protein Engineering with Machine Learning of Protein Dynamics. J. Chem. Inf.
   Model. 65(21): 11979-11987.

5. Hou, L., Zhao, Q., and Shen, Y. (2026). Protein Language Models Trained on
   Biophysical Dynamics Inform Mutation Effects. PNAS 123: e2530466123.

6. Wohlwend, J., et al. (2025). Boltz-2: Towards Accurate and Efficient Binding
   Affinity Prediction. bioRxiv 2025.06.14.659707.

7. Portal, N., Karroucha, W., Mallet, V., and Bonomi, M. (2026). Learning Dynamic
   Protein Representations at Scale with Distograms. bioRxiv 2026.01.29.702509.

8. Lewis, J., Jing, B., et al. (2025). Scalable Emulation of Protein Equilibrium
   Ensembles with Generative Deep Learning. Science 369: 270-278.

9. Ahlmann-Eltze, C., Huber, W., and Anders, S. (2025). Deep-learning-based gene
   perturbation effect prediction does not yet outperform simple linear baselines.
   Nature Methods 22: 1657-1661.

10. Brbic, M., et al. (2025). Systema: A framework for evaluating genetic
    perturbation response prediction beyond systematic variation. Nature
    Biotechnology.

11. Gandhi, S., Javadi, A., et al. (2025). Tahoe-x1: Scaling Perturbation-Trained
    Single-Cell Foundation Models to 3 Billion Parameters. bioRxiv
    2025.10.23.683759.

12. "Mutational Robustness Predicts Protein Dynamics Across Natural and Designed
    Proteins." (2026). bioRxiv 2026.03.19.713008.

13. Nature Computational Science editorial (2021). To review or not to review.
    Nature Computational Science 1: 226.

14. Zha, J., Li, Z., Li, X., Liu, J., Zhu, Y., Feng, L., Lu, M., and Zhang, Z.
    (2026). Assessing the Performance of BioEmu in Understanding Protein Dynamics.
    Int. J. Mol. Sci. 27(6): 2896.

15. Lindorff-Larsen, K., et al. (2012). Systematic Validation of Protein Force
    Fields against Experimental Data. PLoS ONE 7(2): e32131.

16. Robustelli, P., Piana, S., and Shaw, D.E. (2018). Developing a molecular
    dynamics force field for both folded and disordered protein states. PNAS 115(21):
    E4758-E4766.

17. Prompers, J.J. and Bruschweiler, R. (2002). General Framework for Studying the
    Dynamics of Folded and Nonfolded Proteins by NMR Relaxation. JACS 124:
    4522-4534.

18. Garnet: Training a force field for proteins and small molecules from scratch.
    (2026). arXiv 2603.16770.

19. "Mutation-induced reshaping of protein conformational dynamics revealed by a
    coarse-grained modeling framework." (2026). bioRxiv 2026.03.29.715126.

20. PEGASUS: Prediction of MD-derived protein flexibility from sequence. (2026).
    bioRxiv/PMC12267886.

21. VespaG: Expert-guided protein Language Models enable accurate and blazingly fast
    fitness prediction. (2024). Bioinformatics 40(11): btae621.

22. Tahoe-100M: A Giga-Scale Single-Cell Perturbation Atlas for Context-Dependent
    Gene Function and Cellular Modeling. (2025). bioRxiv 2025.02.20.639398.

23. scPerturBench: Benchmarking algorithms for generalizable single-cell perturbation
    response prediction. (2025). Nature Methods.

24. Palmer, A.G. (2004). NMR Characterization of the Dynamics of Biomacromolecules.
    Chem. Rev. 104: 3623-3640.

25. Kovacs, D.P., et al. (2025). MACE-OFF24: Short-Range Transferable Machine
    Learning Force Fields for Organic Molecules. JACS 147: 2977.

26. Notin, P. (2025). Have We Hit the Scaling Wall for Protein Language Models?
    Substack analysis of ProteinGym v1.3 leaderboard.
