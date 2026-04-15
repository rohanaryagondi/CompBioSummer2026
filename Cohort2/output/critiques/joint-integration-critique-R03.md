---
agent: mlffeng + bioval + ensfunc (joint)
round: 3
date: 2026-04-14
type: critique
proposal_reviewed: combined-gamma-alpha-m
---

# Joint Integration Critique: From Accurate Ensembles to Biological Function

## Reviewing Panel

This critique represents the joint assessment of three specialist agents, each
contributing a distinct and critical perspective on the proposed combined paper:

1. **mlffeng (ML Force Field & Simulation Engineering Expert):** 15+ years
   molecular dynamics simulation, 5+ years ML force fields. Evaluates whether
   the MLFF simulations produce trajectories that are physically meaningful
   enough to serve as the validation anchor for the combined narrative.
   Practitioner-first perspective: the simulation protocol, convergence, and
   cross-engine fairness must be bulletproof for the combined paper to stand.

2. **bioval (Biophysical Validation & Experimental Data Expert):** 20+ years in
   NMR spectroscopy, SAXS, and computational biophysics. Evaluates whether the
   experimental reference data are adequate, properly curated, and correctly
   back-calculated. The bridge between "simulated observable" and "measured
   observable" -- the quality of this bridge determines whether the Alpha-M
   validation is credible, and therefore whether the combined paper's
   integration claim is defensible.

3. **ensfunc (Ensemble-to-Function Prediction Expert):** 10 years across
   structural bioinformatics, protein engineering, and ML for biology. Evaluates
   whether the Gamma component's ensemble-to-function pipeline is robust, whether
   the wildtype ensemble hypothesis is appropriately tested, and whether the
   8-protein integration with Alpha-M creates genuine scientific insight rather
   than a forced narrative.

**Why a joint review matters:** The combined paper's central claim -- that
physically accurate ensembles produce better functional predictions -- sits at
the intersection of all three domains. No single reviewer can assess the full
chain: MLFF simulation quality (mlffeng) --> experimental validation (bioval)
--> ensemble features (ensfunc) --> functional prediction (ensfunc). This
joint review traces the entire chain and identifies where it is strongest,
where it is weakest, and where it might break.

---

## Combined Narrative Summary

The proposed paper, titled "From Accurate Ensembles to Biological Function:
Validating and Applying ML Protein Dynamics," makes a two-part claim unified
by a bridge analysis. Part I (Alpha-M) benchmarks 3 ML force fields and 2
classical baselines against experimental NMR/SAXS observables across 7 proteins,
establishing which ensemble generators produce physically realistic dynamics.
Part II (Gamma) demonstrates that conformational ensemble features derived from
BioEmu predict mutation fitness effects across ~200 ProteinGym proteins, with
the strongest signal for binding and catalysis assays. Part III (Integration)
connects the two by showing, across 8 proteins with both NMR data and DMS
assays, that ensemble generators with better experimental agreement also produce
better functional predictions.

---

## Overall Assessment

**Verdict:** Support with Modifications

**One-line take:** The combined narrative is scientifically ambitious, editorially
compelling, and fills a genuine gap -- but the integration claim rests on a
statistically fragile 8-protein correlation, the timeline alignment is precarious,
and the force field bias chain creates a circularity that must be explicitly
controlled for the paper to withstand Nature Computational Science review.

---

## Integration Analysis

### 1. Scientific Soundness of the Integration Claim

The central integration claim is: "More physically accurate ensemble generators
produce better functional predictions." Testing this requires correlating Alpha-M
validation quality (e.g., S2 R^2 against NMR experiment) with Gamma prediction
quality (Spearman rho on DMS fitness) across the 8 overlap proteins, for each
ensemble generator (BioEmu, MACE-OFF24, SO3LR, AI2BMD, AMBER ff19SB, CHARMM36m).

**Is this scientifically sound?** In principle, yes. The logic is clean: if
ensemble physical accuracy matters for function, then methods that produce more
experimentally accurate ensembles should also produce more functionally predictive
features. This is analogous to the established finding in materials science that
MLFFs with better phonon spectra produce better thermal conductivity predictions
(Mannan et al., arXiv 2508.05762, UniFFBench). In protein science, no such
connection has been made. This would be genuinely novel.

**However, the statistical design has critical limitations:**

**(a) N=8 proteins is marginally sufficient.** For a Spearman rank correlation
between S2 agreement rank and fitness prediction rank across 6 generators, each
protein provides one paired data point per generator. With 8 proteins and 6
generators, the correlation can be computed at the generator level (averaging
across proteins, N=6 generators) or at the protein-generator level (N=48 data
points, but with non-independence within proteins and within generators).

At N=6 generators (aggregated across proteins): Spearman correlation can detect
only very large effects. The critical value for Spearman rho at alpha=0.05
(two-tailed) with N=6 is |rho| >= 0.886. This means only a near-perfect
monotonic relationship would reach significance. Power analysis (using the
approximation from Bonett & Wright, 2000, Psychometrika) indicates that to
detect rho=0.8 with 80% power, N=7 data points are needed; to detect rho=0.6,
N=14 are needed. At N=6, the test has approximately 50% power for rho=0.8 and
less than 25% for rho=0.6. This is uncomfortably low.

At the protein-generator level (N=48, treating each protein-generator pair as a
data point): Multilevel modeling (HLM or mixed-effects correlation) would
provide more power, but the independence assumption is violated -- observations
within the same protein are correlated (some proteins are inherently easier for
all methods) and observations from the same generator are correlated (some
generators are uniformly better or worse). A permutation test stratified by
protein would be more appropriate than naive Spearman.

**(b) The correlation structure is complex.** The integration involves:
- 6 generators ranked on validation quality (per-protein S2 R^2)
- The same 6 generators ranked on functional prediction quality (per-protein
  Spearman rho on DMS)
- 8 proteins providing paired rankings

The natural analysis is a within-protein rank correlation: for each protein,
rank the 6 generators by S2 R^2 and by fitness Spearman, then compute the
per-protein rank correlation. Average these across proteins (Fisher-z
transformed) and test whether the mean is positive. This is essentially a
meta-analytic approach.

**Recommended statistical test:** Per-protein Spearman correlation between
validation quality and prediction quality (yielding 8 correlation values), then
one-sample Wilcoxon signed-rank test on the 8 correlations against zero. This
is more powerful than a single aggregate correlation and naturally handles
protein-level variation. However, 8 observations still limit power to detect
moderate effects.

**(c) Effect size expectations.** The expected effect is that better S2 agreement
translates to better RMSF features, which translates to better fitness prediction.
But the chain is long: S2 measures ps-ns backbone dynamics; RMSF integrates
fluctuations across the entire BioEmu ensemble; fitness prediction depends on
15 features, not just RMSF. The correlation between S2 quality and fitness
prediction quality will be attenuated by each step in the chain. We estimate the
realistic effect size as rho = 0.4-0.6, which is detectable at N=48 (protein-
generator level) but not at N=6 (generator level) or N=8 (per-protein average).

**Bottom line (joint view):** The integration is scientifically sound in concept
but statistically fragile. The paper should present the 8-protein integration
as suggestive evidence, not as a definitive proof. The primary Alpha-M and Gamma
results must each stand on their own. The integration should be framed as "the
first evidence that validation quality correlates with application quality" with
appropriate caveats about sample size. Expanding to 10-12 overlap proteins (by
adding SNase, HIV protease, alpha-synuclein, p53 from bioval's stretch set) would
substantially strengthen the statistical case.

---

### 2. Timeline Alignment

**Alpha-M timeline (mlffeng proposal):**
- Phase 1 (setup + stability): Weeks 1-2
- Phase 2 (production 50 ns): Weeks 3-8
- Phase 3 (S2 replicas): Weeks 5-10
- Phase 4 (BioEmu ensembles): Weeks 5-6
- Phase 5 (back-calculation): Weeks 9-12
- Phase 6 (writing): Weeks 11-14
- **Total: 12-14 weeks**

**Gamma timeline (ensfunc proposal):**
- Phase 1 (ensemble generation): Weeks 1-3
- Phase 2 (feature extraction): Weeks 2-4
- Phase 3 (ML training): Weeks 4-6
- Phase 4 (ablation + integration): Weeks 6-8
- Phase 5 (figures): Weeks 8-9
- Phase 6 (writing): Weeks 9-11
- **Total: ~11 weeks**

**Integration requires both to deliver:**
- Alpha-M Phase 5 (back-calculation results) is needed for integration
- Gamma Phase 4 (integration analysis) cannot start without Alpha-M S2 results
  for all 6 generators on the 8 overlap proteins
- Alpha-M back-calculation finishes at Week 12; Gamma integration analysis is
  planned for Weeks 6-8

**Critical path problem:** Gamma's integration analysis (Weeks 6-8) needs
Alpha-M data that will not be available until Week 12. This 4-6 week gap means
either:

(a) **Gamma integration waits until Alpha-M Week 12.** This pushes Gamma
    completion from Week 11 to Week 15-16. Combined paper completion would be
    Week 16-18 (approximately September-October 2026 if starting in May). This
    is within the competition window but tight.

(b) **Gamma uses partial Alpha-M data.** If Alpha-M Phase 2 production runs
    complete by Week 8, preliminary S2 and chemical shift calculations from the
    50 ns trajectories (not the S2 replica campaign) could provide initial
    integration data by Week 10. This allows Gamma to begin integration analysis
    at Week 10 instead of Week 12, saving 2 weeks.

(c) **Gamma generates AMBER ff19SB ensembles independently.** ensfunc's Open
    Question 6 suggests running short (10-50 ns) AMBER ff19SB MD simulations for
    the 8 overlap proteins and comparing BioEmu RMSF vs. AMBER RMSF as fitness
    predictors. This can proceed without Alpha-M data and provides a "bridge
    analysis" early in the Gamma timeline. Alpha-M data then enriches this
    analysis when available.

**Joint recommendation:** Adopt option (c) as the baseline plan: Gamma runs
AMBER ff19SB comparisons on the 8 overlap proteins independently (Weeks 3-5,
~50 GPU-hrs), producing a "BioEmu vs. classical MD" fitness prediction
comparison. When Alpha-M data arrives (Week 10-12), the full 6-generator
integration analysis replaces the 2-generator preliminary analysis. This
decouples the critical paths and makes each project independently publishable
on schedule.

**Can Part III start before both are done?** Yes, but only the 2-generator
preliminary version (BioEmu vs. AMBER). The full 6-generator analysis requires
Alpha-M completion.

---

### 3. The 8-Protein Overlap: Sufficiency and Representativeness

The 8 overlap proteins are:

| Protein | Size | Fold | NMR Data Richness | DMS Assay Type | Integration Concern |
|---------|------|------|-------------------|----------------|---------------------|
| Ubiquitin (76 res) | Small | alpha/beta | Excellent (S2, shifts, J, RDCs) | Stability | Gold standard; may not generalize |
| GB1/GB3 (56 res) | Small | beta | Excellent (36 RDC sets) | Stability | Excellent NMR, stability-only DMS |
| T4 Lysozyme (164 res) | Medium | alpha | Good (S2, shifts) | Activity | Enzyme; best for dynamics-catalysis |
| Barnase (110 res) | Medium | alpha/beta | Good (S2, methyl S2) | Activity | Enzyme catalysis |
| HIV Protease (99x2 res) | Medium (dimer) | alpha/beta | Moderate (S2, flap dynamics) | Activity | Drug resistance; dimer complexity |
| Alpha-synuclein (140 res) | Medium (IDP) | Disordered | Good (shifts, PRE, SAXS) | Aggregation | IDP -- fundamentally different |
| p53 (195 res) | Large | alpha/beta | Limited (shifts) | Binding | Cancer; limited NMR; Zn binding |
| SNase (149 res) | Medium | alpha/beta | Good (S2, shifts, J) | Stability | Classic folding model |

**Strengths of this set:**
- Spans 3 DMS assay types (stability, activity, aggregation, binding)
- Includes both small (56-76 res) and medium (110-195 res) proteins
- Covers alpha, beta, mixed, and disordered folds
- Includes enzymes (barnase, T4 lysozyme, HIV protease) where dynamics-function
  relationships are well-characterized
- 3/8 (ubiquitin, GB3, SNase) have excellent multi-observable NMR data

**Weaknesses (mlffeng + bioval perspective):**
- **Size bias:** All proteins are <200 residues. No large protein (>300 res)
  is represented. DMS datasets for larger proteins exist in ProteinGym (e.g.,
  influenza HA ~330 res, TEM-1 beta-lactamase 286 res) but none has NMR
  dynamics data suitable for Alpha-M.
- **Over-representation of stability assays:** 3/8 proteins (ubiquitin, GB3,
  SNase) measure stability. The integration claim is strongest for activity
  assays but only 3/8 proteins test this.
- **NMR data quality varies dramatically:** Ubiquitin and GB3 have thousands
  of NMR data points. p53 has only chemical shifts. Alpha-synuclein requires
  IDP-specific analysis (Rg, PRE, not S2). The S2-to-fitness correlation can
  only be computed for proteins with S2 data, reducing the effective N to 5-6.
- **HIV Protease is a dimer.** MLFF simulation of a homodimer doubles system
  size and introduces interchain contact sampling challenges. Alpha-M may not
  be able to produce a fair comparison for this protein, reducing effective N
  to 7.
- **Alpha-synuclein is an IDP.** BioEmu was not extensively validated on IDPs.
  MLFF IDP simulations require much longer timescales (microseconds) than
  folded proteins. S2 order parameters are less informative for IDPs (most
  are near zero). The IDP integration point is conceptually different from the
  folded protein integration.

**Recommendation:** The 8-protein overlap is adequate for a first study but
should be acknowledged as exploratory. Consider removing alpha-synuclein and
HIV protease from the primary integration analysis (flagging them as stretch
targets) and focusing the core integration on the 6 well-characterized folded
proteins (ubiquitin, GB3, T4 lysozyme, barnase, p53, SNase) where the S2
validation-to-fitness pipeline is most comparable. Report the IDP and dimer
results separately with appropriate caveats.

Adding RNase H and Cyclophilin A from bioval's stretch set (both have excellent
NMR data but lack ProteinGym DMS assays) would not help the integration since
they lack DMS data. The only path to expanding the overlap set is to identify
additional proteins with BOTH rich NMR data AND ProteinGym DMS assays. From our
review of the data: SH3 domain (Fyn), chignolin, and Protein L are candidates
with published NMR dynamics data but would need to be confirmed against the
ProteinGym assay list.

---

### 4. BioEmu as the Bridge

BioEmu occupies a unique dual role in the combined paper:
- In Alpha-M: BioEmu is a non-MD comparator, benchmarked against NMR
  observables alongside MLFFs and classical baselines
- In Gamma: BioEmu is the primary ensemble generator, producing the ensembles
  from which fitness-predictive features are extracted

This is elegant in design but creates a high-stakes dependency.

**Scenario analysis:**

**(a) BioEmu performs well in Alpha-M (S2 R^2 >= 0.50, comparable to classical
FFs):** This is the best-case scenario. The combined paper's narrative is:
"BioEmu produces physically realistic ensembles (validated by Alpha-M), and
these ensembles predict function (demonstrated by Gamma)." The integration
claim is strengthened because the ensemble generator used for Gamma has been
independently validated.

**(b) BioEmu performs poorly in Alpha-M (S2 R^2 < 0.40, worse than classical
FFs):** This is not a failure -- it is actually THE key finding of the combined
paper. The narrative becomes: "Despite producing ensembles with lower physical
accuracy than classical FFs, BioEmu ensembles still predict function. This
suggests that functional prediction depends on ensemble topology (which
conformational states are sampled) rather than ensemble accuracy (how precisely
each state is sampled)." This is a scientifically richer and more nuanced
finding than the success case.

Furthermore, if Alpha-M identifies that one MLFF (say MACE-OFF24) produces
better S2 than BioEmu, the combined paper can then show: "MACE-OFF24 ensembles
predict function even better than BioEmu ensembles on the 8 overlap proteins."
This would be a spectacular result -- demonstrating that investing in physically
accurate simulations pays off in functional prediction.

**(c) BioEmu performs inconsistently in Alpha-M (good S2 for some proteins, poor
for others):** This creates a protein-level correlation opportunity. The
integration analysis becomes: "For proteins where BioEmu S2 agreement is high,
BioEmu fitness prediction is also better" -- a within-generator, across-protein
correlation. This is statistically more tractable than the full 6-generator
correlation.

**Joint assessment:** The BioEmu dual role is a strength, not a weakness, for
the combined paper. All three scenarios produce publishable findings. The key
is to frame the integration analysis as hypothesis-generating rather than
hypothesis-confirming. The narrative should present the three possible outcomes
in the Introduction and let the data decide. This is the kind of
"hypothesis-agnostic" framing that Nature Computational Science editors value
(see Nature Computational Science editorial criteria: "an advance in
understanding likely to influence thinking in the field").

**Risk to Gamma standalone:** If BioEmu validation is poor (scenario b), Gamma
must defend its use of BioEmu ensembles for fitness prediction. The defense is
the wildtype ensemble hypothesis: even imperfect ensembles capture the topology
of conformational space (which positions are flexible, which are rigid) well
enough for fitness prediction, even if the precise dynamics are biased. The
March 2026 bioRxiv preprint (rho ~0.6 between RMSF and mutational sensitivity)
supports this: the signal is in the spatial pattern of flexibility, not in the
absolute magnitude of fluctuations.

---

### 5. Feature Consistency Between Alpha-M and Gamma

Alpha-M validates dynamics through:
- S2 order parameters (ps-ns backbone NH dynamics)
- 3J-couplings (backbone phi angle distributions)
- Chemical shifts (local electronic environment, sensitive to structure)
- SAXS profiles (global shape and compactness)

Gamma uses dynamics features including:
- RMSF (global positional fluctuations)
- Contact frequency (pairwise proximity across ensemble)
- Mutual information (correlated motions)
- SASA distribution (solvent exposure)
- S2 (predicted from ensemble)

**Are these measuring the same thing?**

Partially, but not completely. The connection between S2 and RMSF is well-
established: both measure backbone fluctuations, and they are formally related.
S2 is the plateau of the autocorrelation function of the NH bond vector, while
RMSF is the root-mean-square fluctuation of atomic positions. For a rigid
residue, S2 is high (~0.85-0.90) and RMSF is low (<0.5 A). For a flexible
residue, S2 is low (<0.6) and RMSF is high (>1.5 A). The correlation between
S2 and 1/RMSF is typically r > 0.7 for well-folded proteins (Prompers &
Bruschweiler, JACS 2002; Palmer, Chem Rev 2004).

**However, the relationship is not perfect:**

**(a) Timescale mismatch.** Experimental S2 reports on ps-ns dynamics (the
timescale accessible to 15N NMR relaxation). RMSF from a BioEmu ensemble
integrates fluctuations across all sampled conformational states, which may
include slow motions (us-ms or longer) that S2 does not capture. An MLFF could
produce accurate S2 (correct ps-ns dynamics) but inaccurate RMSF (wrong sampling
of slow conformational transitions). For the integration claim, this means an
MLFF with good S2 might not produce RMSF features that predict function better
than one with poor S2, if the functionally relevant dynamics are on timescales
beyond what S2 measures.

**(b) S2 is backbone-only; several Gamma features need side chains.** As
mlffeng's critique identified, BioEmu generates backbone-only coordinates.
Alpha-M validates backbone dynamics (S2, J-couplings, backbone chemical shifts).
But several of Gamma's most promising features (SASA, H-bond persistence,
contact frequency) are degraded by the backbone-only limitation. The integration
analysis should focus on backbone-robust features (RMSF, B-factor variance, S2,
PCA amplitudes) to maintain consistency with Alpha-M's validation scope.

**(c) Chemical shifts and J-couplings do not directly map to Gamma features.**
Alpha-M validates chemical shifts and J-couplings, but Gamma does not use these
as features. This means that improvements in chemical shift accuracy (from a
better MLFF) may not translate into improvements in fitness prediction. The
integration claim is strongest when focused on S2 (which maps directly to
RMSF/S2 in Gamma) and weakest when considering chemical shifts.

**Recommendation:** For the integration analysis, use S2 R^2 as the primary
Alpha-M validation metric (not chemical shifts or J-couplings), because S2 maps
most directly to the RMSF features used in Gamma. Report chemical shift and
J-coupling integration results separately as sensitivity analyses. This focuses
the integration claim on the strongest link in the feature chain.

---

### 6. Force Field Bias Chain

The bias chain is:

```
AMBER ff14SB (training data for BioEmu)
    |
    v
BioEmu ensembles (learned approximation of ff14SB equilibrium)
    |
    v
Gamma features (RMSF, contacts, etc. from BioEmu)
    |
    v
Fitness prediction (trained on ProteinGym DMS scores)
```

Meanwhile, Alpha-M benchmarks against experiment using AMBER ff19SB (not ff14SB)
as the classical baseline. The chain raises three concerns:

**(a) Circularity in stability prediction.** BioEmu v1.2 was fine-tuned with
PPFT on ~776,000 ddG/DeltaG measurements from MEGAscale. ProteinGym stability
assays measure the same quantity (ddG). If BioEmu ensembles predict stability
fitness well because BioEmu was trained on stability data, the dynamics signal
is confounded with the stability signal. This circularity does not affect
binding or catalysis assays, which makes the assay-type stratification
essential. But if the paper's headline result is "dynamics predict stability
fitness," reviewers will immediately identify this confound.

**(b) AMBER ff14SB vs. ff19SB.** Alpha-M uses ff19SB as the classical baseline;
BioEmu was trained on ff14SB. These force fields differ in their torsional
parameters (ff19SB has improved backbone phi/psi potentials; Tian et al., JCTC
2020). If BioEmu inherits ff14SB biases (e.g., alpha-helix over-stabilization),
these biases may make BioEmu ensembles *different* from the ff19SB baseline in
systematic ways that are unrelated to BioEmu's generative model quality. The
Alpha-M comparison of BioEmu vs. ff19SB then conflates "BioEmu model error"
with "ff14SB-vs-ff19SB force field error."

**(c) The bias chain affects the integration claim asymmetrically.** For the
integration analysis, we correlate S2 agreement with fitness prediction quality
across generators. BioEmu's S2 agreement includes both its generative model
quality and its inherited ff14SB bias. If ff14SB S2 values are systematically
lower than experiment (as Smith et al. 2024 showed: R^2 = 0.62), and BioEmu
faithfully reproduces ff14SB dynamics, then BioEmu S2 will also be lower than
experiment -- but this is not a failure of BioEmu's generative approach, it is
an inherited limitation. The integration analysis should distinguish "BioEmu-
specific errors" from "inherited classical FF errors."

**Mitigation strategy (joint recommendation):**

1. **Add a stability circularity control** (mlffeng suggestion, endorsed by all
   three reviewers): For stability assays, regress out BioEmu's direct ddG
   predictions (which it was trained to produce) before evaluating RMSF-fitness
   correlation. If RMSF predicts fitness even after controlling for BioEmu ddG,
   the dynamics signal is genuine.

2. **Include AMBER ff14SB as a baseline** in addition to ff19SB. This
   disentangles "BioEmu-specific error" from "ff14SB bias." If BioEmu S2 ~=
   ff14SB S2 < ff19SB S2 < experiment, then BioEmu's dynamics are faithful to
   its training data (not a BioEmu failure, but a data limitation). If BioEmu
   S2 < ff14SB S2, then BioEmu introduces additional errors beyond its training
   data.

3. **Frame the bias chain explicitly in the paper.** Present the chain as a
   known limitation and let the integration data speak. If biased ensembles
   still predict function, the finding is: "Even biased dynamics carry
   functional information." If accurate ensembles predict better, the finding
   is: "Ensemble accuracy matters." Both are publishable.

---

### 7. Separability Analysis

The combined paper's resilience depends on how each component performs
independently.

**Scenario A: Alpha-M works, Gamma shows no signal**
- Alpha-M stands alone as "The MLFF Biomolecular Crash Test" -- a benchmark
  paper targeting Nature Computational Science or Nature Methods
- The benchmark paper is strong regardless of Gamma (UniFFBench precedent:
  benchmark papers are independently valuable)
- Publication strategy: Alpha-M as standalone Nature Methods benchmark paper
- Risk: moderate. Alpha-M compute investment (~88K GPU-hrs) is justified by
  the benchmark alone.
- **Gamma's "no signal" result**: publishable as a negative finding ("Why
  conformational ensembles fail to predict mutation effects") in Bioinformatics
  or PLOS Computational Biology (ensfunc's pre-planned negative result path)

**Scenario B: Gamma works, Alpha-M cannot complete in time**
- Gamma stands alone as "Conformational Ensembles Predict Function Beyond
  Sequence"
- As scopeadv's critique identified, standalone Gamma is editorially marginal
  for NCS without Alpha-M integration
- **Mitigation:** Gamma can generate AMBER ff19SB ensembles independently for
  the 8 overlap proteins (~50 GPU-hrs) and compare BioEmu vs. classical MD as
  fitness predictors. This provides a "BioEmu validation" without Alpha-M
  MLFF data.
- Publication strategy: Gamma standalone targets NCS with the AMBER comparison
  as partial validation, or targets Genome Research / Bioinformatics if the
  NCS framing is too weak.
- Risk: moderate-high. Without Alpha-M, Gamma is a good paper but not a great
  one.

**Scenario C: Both work, but 8-protein integration shows no correlation**
- This is actually the most interesting scientific outcome.
- The narrative becomes: "Ensemble physical accuracy (validated by NMR) is
  orthogonal to functional prediction quality. Functional prediction depends
  on ensemble topology, not accuracy."
- Two separate papers:
  - Paper 1: Alpha-M benchmark (standalone, NCS/Nature Methods)
  - Paper 2: Gamma dynamics-to-function (standalone, NCS/Genome Research)
  - Both papers reference each other but do not share a combined narrative
- Risk: low. Both components produce independent contributions. The null
  integration result is itself publishable as a finding.

**Joint assessment of separability:** The project is well-designed for
separability. Each component (Alpha-M, Gamma) produces a standalone publication
regardless of the other. The combined paper is the high-ceiling option. The
null integration result is the most intellectually interesting outcome and
should not be treated as failure. We recommend:

- Treat the combined paper as aspirational (probability: ~40-50%)
- Design each component for standalone publication as the baseline expectation
- Frame the integration analysis as "if the data support it" rather than
  "the paper's central claim"
- Use scopeadv's 4-checkpoint decision system (June 30, Aug 15, Sep 30, Oct 15)
  to decide combined vs. separate at the appropriate milestone

---

### 8. The Killer Figure

**Concept: "The Dynamics Quality-Function Plane"**

A two-panel figure that is the visual centerpiece of the combined paper:

**Panel A: The Dynamics Quality Landscape**
- X-axis: Ensemble physical accuracy (mean S2 R^2 across 8 overlap proteins)
- Y-axis: Functional prediction quality (mean Spearman rho on DMS fitness
  across 8 overlap proteins)
- Points: 6 generators (BioEmu, MACE-OFF24, SO3LR, AI2BMD, AMBER ff19SB,
  CHARMM36m), each labeled and color-coded
- Error bars: 95% CI from bootstrap across proteins
- Trend line: Linear regression with R^2 and p-value
- Background quadrants:
  - Top-right: "Accurate AND predictive" (goal)
  - Top-left: "Predictive but inaccurate" (surprising -- topology matters
    more than accuracy)
  - Bottom-right: "Accurate but not predictive" (validation alone is
    insufficient)
  - Bottom-left: "Neither" (method fails)
- Annotations: Classical FFs provide the baseline; MLFFs should land in the
  top-right; BioEmu's position reveals whether generative models can
  shortcut physics

**Panel B: The Per-Protein Waterfall**
- X-axis: 8 proteins (ordered by integration effect size)
- Y-axis: Delta Spearman (fitness prediction improvement when switching from
  least accurate to most accurate ensemble generator for that protein)
- Bars: Colored by assay type (stability=blue, activity=red, binding=green,
  aggregation=purple)
- Overlaid diamonds: S2 R^2 improvement (scaled to same axis)
- Narrative: "For proteins where ensemble accuracy matters most (high delta
  S2 R^2), functional prediction also improves most"

**Why this figure would work for a cover:**
- The quadrant plot (Panel A) is visually striking -- 6 clearly differentiated
  points with a trend line tell the story at a glance
- The color coding connects physical accuracy to biological function in a
  single visual
- The question it answers ("does accuracy predict utility?") is universally
  interesting beyond the MLFF community
- Nature Computational Science covers favor clean, conceptual figures over
  dense data plots
- The figure encapsulates the combined paper's entire contribution in one image

**Fallback figure (if integration correlation is weak):**
A radar/spider plot showing each generator's performance across both validation
metrics (S2, shifts, J-couplings, SAXS) and functional metrics (stability rho,
activity rho, binding rho). This visualizes the multi-dimensional comparison
even without a single correlation, and would still be visually compelling.

---

### 9. Top 5 Reviewer Attack Vectors

**Attack 1: "N=8 proteins is too few for the integration claim."**

- **Probability:** 95% (essentially guaranteed from any statistical reviewer)
- **The concern:** 8 proteins cannot establish a robust correlation between
  validation quality and prediction quality. The Spearman test at N=6
  (generators) requires |rho| >= 0.886 for significance.
- **Pre-emption:** (a) Present the integration as "first evidence" not
  "definitive proof." (b) Use the per-protein within-generator analysis
  (N=48 data points with multilevel modeling) as the primary test, not the
  across-generator aggregate (N=6). (c) Report exact p-values and Bayes factors;
  even non-significant trends with BF > 3 are interpretable. (d) Emphasize that
  both Alpha-M and Gamma stand independently -- the integration is additive,
  not essential.
- **Precedent:** Lindorff-Larsen et al. (2012) drew force field conclusions
  from 4 proteins. Robustelli et al. (2018) used 21 but for classical FFs
  only. Our 8 proteins with 6 generators exceeds the Lindorff-Larsen standard
  for a multi-method benchmark. The Brini/Cavender et al. (Living J. Comp.
  Mol. Sci. 2025) review catalogs the standard protein benchmark sets and
  endorses sets of 4-15 proteins as adequate for force field comparison.

**Attack 2: "BioEmu inherits AMBER ff14SB biases -- the dynamics signal is a
force field artifact."**

- **Probability:** 80% (from structural biology or MD expert reviewers)
- **The concern:** BioEmu's ensemble features may predict stability fitness
  because BioEmu was trained on stability data (MEGAscale ddG), not because
  it captures real dynamics. The circularity confounds the integration claim.
- **Pre-emption:** (a) The stability circularity control (regress out BioEmu
  ddG predictions before evaluating RMSF-fitness correlation). (b) Report
  results separately for stability vs. non-stability assays; if dynamics
  features predict binding/catalysis (where BioEmu was NOT trained on fitness
  data), the signal is genuine. (c) Include ff14SB as an additional Alpha-M
  baseline to disentangle BioEmu model error from inherited FF error. (d) If
  MACE-OFF24 or SO3LR ensembles (which do NOT inherit ff14SB biases) also
  predict function on the 8 overlap proteins, the bias chain objection is
  fully addressed.

**Attack 3: "50 ns MLFF trajectories are too short to produce converged
dynamics for comparison with BioEmu's equilibrium ensembles."**

- **Probability:** 75% (from MD simulation experts)
- **The concern:** BioEmu samples equilibrium distributions (by construction),
  while 50 ns MLFF trajectories may not have converged, especially for slow
  motions. Comparing unconverged MLFF dynamics to converged BioEmu dynamics
  conflates ensemble quality with sampling adequacy.
- **Pre-emption:** (a) The S2 multi-replica protocol (10 replicas x 10 ns)
  specifically addresses convergence for ps-ns dynamics. (b) The trajectory-
  length ablation (10/20/30/40/50 ns checkpoints) directly tests whether
  conclusions depend on simulation length. (c) Chemical shifts and J-couplings
  converge in 10-20 ns (Lindorff-Larsen 2012). (d) For the integration
  analysis, use S2 (which converges with the replica protocol) rather than
  RMSF (which depends on total sampling time). (e) Acknowledge that slow
  conformational dynamics (us-ms) are beyond the scope of both MLFFs (at
  50 ns) and the comparison; this is a known limitation shared by all methods
  except long-timescale classical MD.

**Attack 4: "The ensemble features are standard biophysics descriptors
computed with standard tools -- where is the methodological novelty?"**

- **Probability:** 70% (from NCS editors who require methodological development)
- **The concern:** NCS editorial criteria state that "straightforward usage of
  machine learning algorithms is usually outside the journal's scope." The
  MLP, XGBoost, and GATv2 are standard. The features (RMSF, contacts, MI) are
  standard. The evaluation (leave-protein-out CV) is standard. The only
  novelty is connecting BioEmu to ProteinGym -- which is data integration,
  not method development.
- **Pre-emption:** (a) The combined paper's novelty is in the INTEGRATION,
  not the individual methods. No paper has ever connected force field
  validation quality to downstream functional prediction quality. This is a
  new conceptual framework. (b) The dynamics-informed graph edges for GATv2
  (using BioEmu contact frequency instead of static distance cutoffs) are
  novel for this application, extending Ozkan et al. (PNAS 2025) from 4
  proteins to 200. (c) Frame the paper as establishing a new paradigm
  ("from validated ensembles to function") rather than introducing new
  algorithms. Precedent: the AlphaFold2 paper (Nature 2021) used standard
  attention mechanisms and equivariant networks but introduced a new approach
  to protein structure prediction. (d) The assay-type stratification, showing
  which dynamics modalities matter for which biological functions, is a novel
  finding, not a standard analysis.

**Attack 5: "The improvement over existing ProteinGym methods is marginal
(~0.02-0.03 Spearman) and does not justify the compute cost."**

- **Probability:** 60% (from practical/applied reviewers)
- **The concern:** Even if dynamics features improve predictions, a ~0.02-0.03
  Spearman improvement at the cost of ~91K GPU-hrs (Alpha-M + Gamma combined)
  is not practical for real-world protein engineering.
- **Pre-emption:** (a) The compute-matched comparison table (ensfunc
  proposal): report improvement per GPU-hr and note that AlphaMissense
  required millions of GPU-hrs for training, ESM2 required >10K GPU-hrs,
  while Gamma ensemble generation costs only 143 GPU-hrs for the primary
  analysis. (b) The overall Spearman improvement may be modest, but the
  improvement on binding and catalysis assays may be substantial (0.05-0.10).
  The stratified result is the publishable finding, not the overall average.
  (c) The paper establishes a new modality (dynamics), not a final method.
  The first paper adding structure to sequence predictions (ESM-IF1) also
  showed modest improvements over sequence-only methods but was highly
  impactful because it opened a new direction. (d) The Alpha-M benchmark
  component justifies its compute independently (community resource), so
  the marginal compute cost of the Gamma integration is only ~3K GPU-hrs.

---

### 10. Combined vs. Separate Recommendation

**Option A: ONE combined paper (higher ceiling, higher risk)**
- **Pros:**
  - The integration claim ("validated ensembles predict function better") is
    the strongest possible contribution and cannot be made by either paper alone
  - NCS editors strongly prefer papers with both methodological and biological
    contributions; the combined paper provides both
  - scopeadv's assessment that standalone Gamma is NCS-marginal means the
    combined paper is the only route to a top-tier venue for Gamma
  - The "killer figure" (Question 8) only exists in the combined paper
  - Higher citation impact: one high-profile paper vs. two medium-profile papers
- **Cons:**
  - Timeline dependency: Gamma waits for Alpha-M, pushing completion to
    Week 16-18
  - Statistical fragility of the 8-protein integration
  - Longer paper (estimated 12-15 main figures, 30+ supplementary): NCS has
    a 50,000-character limit for Articles; this may require a Resource format
  - If either component underperforms, the combined paper is weaker than two
    separate papers would have been
  - Reviewer burden: finding 3-4 reviewers who can evaluate MLFF benchmarking
    AND ML fitness prediction AND experimental NMR data is extremely difficult

**Option B: TWO separate papers (lower ceiling, lower risk, faster to publish)**
- **Pros:**
  - Each paper has a focused narrative and reviewer set
  - Alpha-M can publish first (Nature Methods benchmark, no Gamma dependency)
  - Gamma can use AMBER ff19SB comparisons for partial validation (no MLFF
    dependency)
  - Timeline is shorter for each paper (12-14 weeks Alpha-M, 11-14 weeks Gamma)
  - If one fails, the other is unaffected
- **Cons:**
  - The integration claim is lost or reduced to a "companion paper" reference
  - Gamma standalone is NCS-marginal (scopeadv assessment)
  - Two medium-impact papers may have lower total impact than one high-impact
    paper

**Option C: TWO papers with shared data/methods section (compromise)**
- **Pros:**
  - Each paper has a focused narrative
  - A shared "companion" section (or companion Resource paper) establishes the
    integration data
  - Nature Computational Science and Nature Methods accept companion papers
  - The integration finding appears in both papers with appropriate cross-
    referencing
- **Cons:**
  - Requires coordination with editors at two journals
  - The integration finding is diluted across two papers
  - Logistically complex (simultaneous submission)

**Our recommendation: Option A (combined paper) as the primary target, with
Option B as the pre-planned fallback.**

**Reasoning:**

1. **The integration claim is the paper's scientific moat.** Neither a standalone
   MLFF benchmark (Alpha-M) nor a standalone dynamics-to-function study (Gamma)
   is unique enough for NCS by itself. Alpha-M is a very strong benchmark paper
   (UniFFBench precedent), but benchmark papers face headwinds at NCS without
   biological application. Gamma fills a genuine gap but uses standard ML on
   standard features. The COMBINATION -- showing that validation quality predicts
   application quality -- is genuinely novel and paradigm-establishing.

2. **The risk is manageable.** The timeline risk is addressed by decoupling the
   critical paths (Gamma runs AMBER comparisons independently; Alpha-M proceeds
   to full MLFF analysis independently). The statistical risk is addressed by
   framing the integration as "first evidence" rather than "definitive proof."
   The separability analysis (Question 7) shows that both components produce
   standalone papers if the combined paper falls through.

3. **The decision can be deferred.** scopeadv's 4-checkpoint system provides
   natural decision points. At June 30, assess whether BioEmu Tier 1 generation
   and Alpha-M stability tests are on track. At August 15, assess whether
   Alpha-M production simulations are complete and Gamma has preliminary results.
   At September 30, assess whether the 8-protein integration data supports a
   combined paper. The combined vs. separate decision should be made at September
   30, not today.

4. **The fallback costs nothing.** If at September 30 the integration data does
   not support a combined paper, both components can be submitted as separate
   papers within 2-4 weeks (the individual narratives are already developed).
   The combined paper attempt costs only the ~50 GPU-hrs for Gamma's preliminary
   AMBER comparison and the time spent on the integration analysis (~2 weeks).

**Trigger for switching to Option B:**
- If Alpha-M stability tests fail for >=2 of 3 MLFFs (end of Week 2)
- If Gamma Stage 1 RMSF-fitness correlation is rho < 0.1 for >50% of proteins
  (June 30 kill criterion)
- If at September 30 the 8-protein integration Spearman is rho < 0.3 with
  p > 0.2

---

## Strengths of the Combined Narrative

1. **Fills a genuine gap at the intersection of two active fields.** No paper
   has ever connected MLFF/ensemble validation quality to downstream functional
   prediction quality. This is the paper's unique contribution. The gap is
   confirmed open as of April 14, 2026 (scopeadv verification).

2. **Each component is independently strong.** Alpha-M is the first systematic
   MLFF benchmark against experimental protein observables (UniFFBench parallel
   for biomolecules). Gamma is the first systematic connection of BioEmu
   ensembles to ProteinGym fitness prediction. Neither has been done.

3. **The integration narrative is editorially compelling.** "From accurate
   ensembles to biological function" is a clean, memorable framing. The
   quadrant figure (Question 8) tells the story visually. NCS editors look for
   papers that change how researchers think about a problem; this paper argues
   that ensemble quality matters for function -- a new way of thinking about
   both force field validation and fitness prediction.

4. **All outcomes are publishable.** Positive integration (accuracy predicts
   function), negative integration (accuracy is orthogonal to function), and
   partial integration (accuracy matters for some assay types but not others)
   are all scientifically interesting and publishable. This is a hallmark of
   well-designed research.

5. **The BioEmu dual role creates narrative coherence.** BioEmu as both
   validation target (Alpha-M) and prediction tool (Gamma) unifies the paper
   around a single technology. Any finding about BioEmu's validation performance
   directly informs the interpretation of its functional predictions.

6. **Compute allocation is well-balanced.** Alpha-M (~88K GPU-hrs) is the
   heavy lift but produces a benchmark resource. Gamma (~3K GPU-hrs) is
   inexpensive relative to impact. The combined paper's total (~91K GPU-hrs)
   is within the project's HPC allocation.

---

## Weaknesses of the Combined Narrative

1. **Statistical fragility of the 8-protein integration.** As analyzed in
   Question 1, the correlation test has limited power at N=6 generators and
   N=8 proteins. The integration claim may be "suggestive" rather than
   "definitive."
   - **Severity:** Major
   - **Addressable?** Partially. Use multilevel modeling and within-protein
     correlations to increase effective N. Expand overlap to 10-12 proteins
     if feasible. Frame as "first evidence."

2. **Timeline dependency.** Alpha-M (12-14 weeks) and Gamma (11 weeks) have
   overlapping timelines, but the integration analysis requires Alpha-M
   completion before Gamma can finalize Part III. Total combined timeline:
   16-18 weeks.
   - **Severity:** Major
   - **Addressable?** Yes. Decouple critical paths with preliminary AMBER
     comparisons (Gamma Weeks 3-5). Full integration analysis at Week 12-14.

3. **Force field bias chain.** BioEmu inherits AMBER ff14SB biases. Stability
   assay circularity. The integration claim must survive bias-aware analysis.
   - **Severity:** Major
   - **Addressable?** Yes. Add circularity control, ff14SB baseline, and
     assay-type stratification.

4. **Feature inconsistency between Alpha-M and Gamma.** S2 maps to RMSF, but
   chemical shifts and J-couplings do not map to Gamma features. The
   integration claim is weaker for non-S2 observables.
   - **Severity:** Moderate
   - **Addressable?** Yes. Focus integration on S2 as primary metric.

5. **Reviewer expertise mismatch.** Finding reviewers who span MD simulation,
   NMR spectroscopy, and ML fitness prediction is extremely difficult. A
   combined paper risks receiving reviews that are expert on one component but
   superficial on others.
   - **Severity:** Moderate
   - **Addressable?** Partially. Suggest reviewers to the editor. Write each
     section to be understandable by non-specialists.

6. **Paper length.** The combined paper requires extensive methods and results
   for two independent studies plus the integration. NCS Articles have a
   50,000-character limit. The paper may need a Resource format or companion
   Supplementary Note.
   - **Severity:** Minor
   - **Addressable?** Yes. Move detailed protocols to Supplementary Methods.
     NCS Resource papers have no strict length limit.

---

## Suggested Modifications

1. **Expand the integration overlap set to 10-12 proteins.** Add BPTI and
   barnase S2 analysis to Alpha-M (bioval's critique confirms adequate data
   exists). Confirm whether SH3 domain, chignolin, or Protein L have ProteinGym
   DMS assays that could enter the overlap set.

2. **Decouple Gamma and Alpha-M critical paths.** Gamma generates AMBER ff19SB
   ensembles for the 8 overlap proteins independently (Weeks 3-5, ~50 GPU-hrs).
   This produces a "BioEmu vs. classical MD" fitness comparison before Alpha-M
   delivers MLFF data.

3. **Add AMBER ff14SB as an Alpha-M baseline.** This disentangles BioEmu-
   specific errors from inherited force field biases and directly addresses the
   bias chain concern.

4. **Implement the stability circularity control.** For stability assays,
   regress out BioEmu's direct ddG predictions before evaluating RMSF-fitness
   correlation.

5. **Focus integration analysis on S2 as the primary Alpha-M metric.** S2
   maps directly to RMSF/S2 in Gamma. Chemical shifts and J-couplings are
   secondary integration metrics.

6. **Use multilevel modeling for the integration analysis.** Treat protein-
   generator pairs as nested data (generators nested within proteins). This
   increases effective N from 6 to 48 while properly accounting for non-
   independence.

7. **Adopt bioval's critical modifications for Alpha-M.** Temperature matching
   (308 K for HEWL, BPTI; 310 K for T4 lysozyme), pH-appropriate protonation
   (PropKa/H++ at experimental pH), iRED for S2, increased S2 replicas to N=15.

8. **Reduce Gamma scope per scopeadv's recommendation.** Defer Tier 2 variant
   sampling. Target 150 proteins (Tier 1 + Tier 2 only). Extend timeline to
   14 weeks. Prioritize the integration analysis and mechanistic stratification
   over exhaustive permutation tests.

9. **Pre-register the integration analysis.** Before any simulations run, lock
   the following on OSF: integration metric (within-protein Spearman between
   S2 R^2 and fitness prediction rho), proteins included, generators compared,
   significance threshold, and decision rule for combined vs. separate papers.

10. **Design the paper structure for separability.** Write Alpha-M and Gamma
    sections as self-contained modules that can be published independently.
    The integration section should be a clearly delineated Part III that can
    be added or removed without restructuring the other sections.

---

## Impact on Publication Strategy

**If combined paper proceeds (our recommendation):**
- Target: Nature Computational Science (Article or Resource)
- Timeline: Submission November 2026 (18 weeks from May start)
- Preprint: bioRxiv October 2026
- The combined paper is the strongest possible contribution this project can make

**If combined paper is abandoned (September 30 decision):**
- Paper 1: Alpha-M benchmark --> Nature Methods (Resource) or NCS (Article)
  - Submission: October 2026
  - Strongest as a community resource with benchmark data package
- Paper 2: Gamma dynamics-to-function --> NCS (if AMBER comparison included)
  or Genome Research
  - Submission: November 2026
  - Must include BioEmu vs. AMBER comparison for the 8 overlap proteins

**Delta remains independent** on its own timeline (preprint July 15, NatMeth
submission August 1). No dependency on Gamma+Alpha-M.

**The portfolio.** If the combined paper succeeds: 2 papers (combined + Delta).
If separate: 3 papers (Alpha-M + Gamma + Delta). In all scenarios, the project
produces multiple publications at high-quality venues.

---

## References

1. Lindorff-Larsen, K., Maragakis, P., Piana, S., Eastwood, M.P., Dror, R.O.,
   and Shaw, D.E. (2012). Systematic Validation of Protein Force Fields against
   Experimental Data. PLoS ONE 7(2): e32131.

2. Robustelli, P., Piana, S., and Shaw, D.E. (2018). Developing a molecular
   dynamics force field for both folded and disordered protein states. PNAS
   115(21): E4758-E4766.

3. Smith, D.G.A., Gowers, R.J., et al. (2024). Convergence of S2 Order
   Parameters from Molecular Dynamics Simulations. J. Phys. Chem. B 128: 10090.

4. Kovacs, D.P., et al. (2025). MACE-OFF24: Short-Range Transferable Machine
   Learning Force Fields for Organic Molecules. JACS 147: 2977.

5. Frank, M., et al. (2026). SO3LR: Molecular Simulations with a Pretrained
   Neural Network and Universal Pairwise Force Fields. JACS.

6. Li, J., et al. (2024). AI2BMD: Accurate Biomolecular Dynamics. Nature 636:
   1012.

7. Lewis, J., Jing, B., et al. (2025). Scalable Emulation of Protein
   Equilibrium Ensembles with Generative Deep Learning. Science 369: 270-278.

8. Notin, P., et al. (2023). ProteinGym: Large-Scale Benchmarks for Protein
   Fitness Prediction and Design. NeurIPS Datasets Track.

9. Aryal, R., et al. (2026). Assessment of BioEmu for Mutational Analysis.
   Int. J. Mol. Sci. 27: 2896.

10. Mannan, T., et al. (2025). UniFFBench: Benchmarking Universal Force Fields
    against Experiment. arXiv 2508.05762.

11. Hou, L., Zhao, Q., and Shen, Y. (2026). SeqDance/ESMDance: Pre-trained
    Protein Language Models on Dynamic Properties. PNAS 123: e2530466123.

12. Ozkan, S., et al. (2025). Dynamics-Based GNN for Allosteric Mutations.
    PNAS 122: e2502444122.

13. Prompers, J.J. and Bruschweiler, R. (2002). General Framework for Studying
    the Dynamics of Folded and Nonfolded Proteins by NMR Relaxation. JACS 124:
    4522-4534.

14. Palmer, A.G. (2004). NMR Characterization of the Dynamics of
    Biomacromolecules. Chem. Rev. 104: 3623-3640.

15. Shen, Y. and Bax, A. (2010). SPARTA+: A Modest Improvement in Empirical
    NMR Chemical Shift Prediction. J. Biomol. NMR 48: 13-22.

16. Han, B., et al. (2011). SHIFTX2: Significantly Improved Protein Chemical
    Shift Prediction. J. Biomol. NMR 50: 43-57.

17. Grudinin, S., et al. (2017). Pepsi-SAXS: An Adaptive Method for Rapid and
    Accurate Computation of SAXS Profiles. Acta Cryst. D73: 449-464.

18. Brini, E., Cavender, C.E., Case, D.A., et al. (2025). Structure-Based
    Experimental Datasets for Benchmarking Protein Simulation Force Fields.
    Living J. Comp. Mol. Sci. 6(1): 3871.

19. Bonett, D.G. and Wright, T.A. (2000). Sample Size Requirements for
    Estimating Pearson, Kendall and Spearman Correlations. Psychometrika 65(1):
    23-28.

20. Demsar, J. (2006). Statistical Comparisons of Classifiers over Multiple
    Data Sets. JMLR 7: 1-30.

21. Benavoli, A., Corani, G., Demsar, J., and Zaffalon, M. (2017). Time for
    a Change: A Tutorial for Comparing Multiple Classifiers Through Bayesian
    Analysis. JMLR 18: 1-36.

22. Tian, C., Kasavajhala, K., et al. (2020). ff19SB: Amino-Acid-Specific
    Protein Backbone Parameters Trained against Quantum Mechanics Energy
    Surfaces in Solution. JCTC 16(1): 528-552.

23. Waibl, F., et al. (2025). ANI-2x Produces Amorphous Solid Water. JCIM.

24. Garnet Force Field (2026). Training a Force Field for Proteins and Small
    Molecules from Scratch. arXiv 2603.16770.

25. Portal, L., et al. (2026). Learning Dynamic Protein Representations at
    Scale with Distograms. bioRxiv 2026.01.29.702509.

26. Lisanza, S., et al. (2025). Conformational Biasing with ProteinMPNN.
    Science.

27. Nature Computational Science (2026). Submission Guidelines: Editorial
    Process & Peer Review. https://www.nature.com/natcomputsci/submission-guidelines

28. Kolde, R., et al. (2012). Robust Rank Aggregation for Gene List
    Integration and Meta-Analysis. Bioinformatics 28(4): 573-580.

29. Hacisuleyman, A. and Erman, B. (2024). Convergence of Mutual Information
    from Molecular Dynamics Trajectories. Bioinformatics.

30. Raddi, R., et al. (2025). BICePs Bayesian Scoring of Force Fields on
    Chignolin CLN025. J. Chem. Theory Comput.

31. Rana, M.S., et al. (2026). BioEmu-Augmented MD for BRAF V600E Kinase
    Dynamics. bioRxiv 2026.01.07.698041v2.

32. Burgin, E., et al. (2025). Quantified Dynamics-Property Relationships
    for Protein Engineering. JCIM.
