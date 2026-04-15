---
agent: mlffeng
round: 3
date: 2026-04-14
type: critique
proposal_reviewed: gamma-dynamics-function
---

# Critique: Conformational Ensembles Predict Protein Function Beyond Sequence

## Reviewing Agent

Dr. ML Force Field & Simulation Engineering Expert (mlffeng). 15+ years molecular
dynamics simulation, 5+ years ML force fields. Reviewing the Gamma proposal from the
**ensemble quality perspective**: whether BioEmu ensembles are physically realistic
enough to support the proposed dynamics-to-function mapping, whether the ensemble
features are well-chosen given the backbone-only limitation, whether convergence
requirements are met, and whether the Alpha-M integration is scientifically sound.

## Proposal Summary

ensfunc proposes the first systematic framework connecting BioEmu-generated
conformational ensembles to ProteinGym DMS fitness prediction across ~200 proteins,
using 15 ensemble features and a 4-stage ML pipeline (statistical baseline, MLP,
GATv2 GNN, ensemble-augmented baselines), with 8-protein integration with Alpha-M
to test whether physically validated ensembles produce better functional predictions.

---

## Overall Assessment

**Verdict:** Support with Modifications

**One-line take:** A scientifically compelling and well-structured proposal with a
genuine gap to fill, but it underestimates three simulation-grounded risks --
force field bias inherited from BioEmu training data, insufficient convergence of
pairwise/higher-order features at 2,000 samples, and the backbone-only limitation
that silently undermines at least 5 of 15 proposed features -- each of which is
addressable with the modifications recommended below.

---

## Strengths

1. **The wildtype ensemble hypothesis is the right framing.** Given Aryal et al.
   (IJMS 2026) demonstrating that BioEmu "fails to predict mutation-induced shifts
   in conformational distribution" and "cannot differentiate driver from passenger
   mutations," anchoring on wildtype ensemble properties rather than variant-specific
   sampling is both scientifically honest and practically necessary. This turns a
   known limitation into a testable hypothesis. The proposal correctly frames a
   negative variant-specific result as strengthening the wildtype narrative rather
   than as failure.

2. **Tiered protein selection is well-designed.** The 50/100/50 tier structure
   (full analysis / wildtype-only / sequence-comparison) with explicit selection
   criteria scored on 5 dimensions is methodologically rigorous. The inclusion of
   a Tier 3 "no-ensemble" comparison set prevents the fallacy of only testing
   proteins where dynamics might help. The 8-protein Alpha-M overlap set is
   strategically chosen with rich NMR data and ProteinGym coverage.

3. **4-stage ML pipeline provides essential interpretability.** Starting with raw
   RMSF-fitness correlation (Stage 1) before any ML ensures the base signal is
   established independently. If Stage 1 shows rho < 0.1 for most proteins, the
   project has a kill switch before significant compute is spent on GNN training.
   The XGBoost variant for SHAP analysis is a practical choice for mechanistic
   interpretation that reviewers will value.

4. **Kill criteria are well-specified and appropriately conservative.** The June 30
   kill criterion (RMSF rho < 0.1 across >50% of Tier 1 proteins) and the July 31
   win rate criterion (>45% against any top-5 baseline) are concrete, pre-registered,
   and tied to go/no-go decisions. This is exactly the kind of rigor Nature
   Computational Science reviewers expect.

5. **Compute budget is realistic and well-scoped.** The refined 3,037 GPU-hr estimate
   (down from Cohort 1's 8,200 estimate) is achievable and reflects careful accounting.
   Tier 1 ensemble generation at 143 GPU-hrs is small enough to start immediately
   and test the hypothesis cheaply before committing to Tier 2 variant sampling at
   1,700 GPU-hrs.

6. **Assay-type stratification addresses the right question.** The pre-specified
   hypothesis that binding and catalysis assays benefit most from dynamics features
   is physically well-motivated. Conformational selection and induced fit are
   well-established mechanisms in enzyme catalysis and molecular recognition
   (Csermely et al., Trends Biochem Sci, 2010; Boehr et al., Nat Chem Biol, 2009).
   Showing differential dynamics utility across assay types would be a genuinely
   novel finding.

---

## Weaknesses

### 1. BioEmu Ensembles Inherit Force Field Biases from Training Data

**Severity:** Major

BioEmu was trained on >200 ms of all-atom MD simulations using AMBER force fields
(primarily ff14SB with TIP3P water), supplemented with 750,000+ experimental ddG
measurements from the MEGAscale dataset (Lewis et al., Science 2025; bioRxiv
2024.12.05.626885). The proposal treats BioEmu ensembles as if they are "ground truth"
equilibrium distributions, but they are in fact learned approximations of AMBER ff14SB
equilibrium distributions, reweighted by experimental stability data.

This has concrete implications:

**(a) Known AMBER ff14SB biases propagate into BioEmu ensembles.** AMBER ff14SB is
known to over-stabilize alpha-helical structure (Best et al., JCTC 2014; Piana et
al., JPCB 2015) and underestimate the population of left-handed polyproline II (PPII)
conformations. Smith et al. (JPCB 2024) showed ff14SB achieves S2 R2 = 0.62 against
NMR experiment -- substantially better than CHARMM36m (R2 = 0.51) but still leaving
38% of variance unexplained. If BioEmu faithfully learned the ff14SB distribution,
its ensembles carry the same biases. For proteins where these biases affect the
mutation-sensitive regions (e.g., helix-loop boundaries, proline-rich regions, IDPs),
the RMSF and contact features will be systematically distorted.

**(b) MEGAscale ddG reweighting introduces a stability bias.** BioEmu v1.2 was
fine-tuned with property prediction fine-tuning (PPFT) on ~776,000 ddG/DeltaG
measurements. This explicitly biases the ensemble generator toward stability-relevant
conformational features. Since ProteinGym stability assays measure the same quantity
(ddG), there is a circularity risk: BioEmu ensembles may predict stability fitness
well because BioEmu was trained on stability data, not because the ensembles are
physically realistic. This confound is absent for binding and catalysis assays,
which makes the assay-type stratification even more critical -- but the proposal
does not identify or control for this circularity.

**(c) The proposal does not distinguish "BioEmu dynamics" from "AMBER dynamics."**
When the paper claims "conformational dynamics predict function," a reviewer will
ask: "Are these real dynamics or AMBER dynamics?" Without Alpha-M data showing
how BioEmu RMSF compares to RMSF from MACE-OFF24(M), SO3LR, and CHARMM36m on
the same proteins, this question is unanswerable. The 8-protein integration is
designed to address this, but the proposal treats it as supplementary rather than
as the critical validation it is.

**Addressable?** Yes, with three additions:
1. Explicitly state in the paper that BioEmu ensembles approximate AMBER ff14SB
   equilibrium distributions, not "true" equilibrium distributions.
2. Add a "stability circularity control": for stability assays, test whether
   BioEmu's ddG predictions alone (which it was trained to produce) explain
   away the RMSF-fitness correlation. If RMSF predicts fitness even after
   regressing out BioEmu ddG, the signal is genuine.
3. Elevate the Alpha-M integration from supplementary analysis to co-primary
   analysis. The question "do MLFFs with better experimental agreement produce
   ensembles that better predict function?" is the linchpin of the combined
   paper's narrative.

---

### 2. Convergence of Pairwise and Higher-Order Features at 2,000 Samples

**Severity:** Major

The proposal specifies 2,000 BioEmu conformations per protein (wildtype) with a
convergence check based on RMSF: "Require per-residue RMSF Pearson r > 0.95 between
halves." This is appropriate for RMSF, which converges relatively quickly because
it depends only on the variance of a single coordinate vector. However, 5 of the
15 proposed features are pairwise or higher-order statistics that converge far more
slowly:

**(a) Mutual information (Feature 8) requires the most samples.** MI between
displacement vectors involves estimating a joint probability distribution in
high-dimensional space. Lange and Grubmuller (Proteins 2006) established that
generalized correlation (related to MI) requires microseconds of continuous
trajectory to converge for small proteins (e.g., ~5 microseconds for ubiquitin).
Hacisuleyman and Erman (Bioinformatics 2024) showed that "trajectory lengths of
approximately 5 microseconds for ubiquitin and 1 microsecond for PLpro mark the
onset of convergence" for MI profiles. BioEmu generates 2,000 independent snapshots,
which is fundamentally different from a continuous trajectory. While independent
samples are more statistically efficient than correlated MD frames, 2,000 samples
may still be insufficient to estimate MI for pairs of residues with low
correlation (the interesting regime for allosteric detection). The proposal does
not provide any convergence analysis for MI.

**(b) Contact frequency (Feature 6) is more robust but size-dependent.** For a
protein with N residues, the contact frequency matrix has O(N^2) entries. Each
entry is a binomial proportion (fraction of frames with Cb-Cb < 8 A). For a
contact with true frequency 0.05 (transient, potentially functional), 2,000
samples give a 95% confidence interval of approximately 0.05 +/- 0.01 (binomial
SE = sqrt(p*(1-p)/n) = 0.005). This seems adequate. However, for the rarest
contacts -- those involved in cryptic pocket formation or allosteric pathways,
where true frequency may be 0.001-0.01 -- 2,000 samples give only 2-20 expected
observations, far too few for stable estimation.

**(c) Distance distribution kurtosis (Feature 7) requires many samples for the
fourth moment.** Kurtosis estimation is notoriously sensitive to sample size; DeCarlo
(Psychol Methods 1997) showed that n > 1,000 is needed for reliable kurtosis
estimation even for univariate distributions, and higher for heavy-tailed
distributions typical of flexible protein regions. For rigid positions, kurtosis
will be near-zero regardless of sample size (Gaussian-like). For flexible
positions -- the ones where dynamics features should carry the most functional
information -- the distribution is likely multi-modal, requiring even more samples.

**(d) PCA amplitude ratios (Feature 13) should converge adequately.** PCA on 2,000
aligned Ca coordinates (dimensions: 2000 x 3N) is well-conditioned for N < ~600
residues (within the proposal's scope). The first 3 PCs should stabilize with
1,000-2,000 samples based on standard random matrix theory. This feature is
acceptably specified.

**(e) Cryptic pocket occupancy (Feature 14) uses only 20 conformations.** The
proposal specifies PocketMiner applied to "20 representative conformations." This
dramatically under-samples the ensemble. If a cryptic pocket opens in 5% of frames,
20 samples give only 1 expected detection -- rendering the occupancy estimate
essentially binary noise. PocketMiner inference is GPU-accelerated and fast;
applying it to all 2,000 conformations rather than 20 would add negligible compute.

**Addressable?** Yes:
1. Run a convergence pilot on 5 proteins (as the proposal's own Open Question 1
   suggests) using 500, 1,000, 2,000, 5,000, and 10,000 samples. Compute the
   coefficient of variation (CV) for each feature across bootstrap resamples at
   each sample size. Publish the convergence profiles in the supplementary.
2. For MI specifically: use the multivariate Gaussian approximation of
   Hacisuleyman and Erman (Bioinformatics 2024), which converges with much shorter
   trajectories (~5 ns for ubiquitin). This could work well with 2,000 independent
   BioEmu snapshots since the Gaussian assumption is more tenable for equilibrium
   samples than for correlated MD frames.
3. Increase cryptic pocket evaluation from 20 to 2,000 conformations. The
   computational cost is trivial relative to ensemble generation.
4. Consider replacing kurtosis with a more robust statistic (e.g., interquartile
   range or the bimodality coefficient) that is less sensitive to sample size.

---

### 3. The Backbone-Only Limitation Is More Severe Than Acknowledged

**Severity:** Major

BioEmu generates backbone coordinates only (N, Ca, C, O atoms per residue). The
proposal acknowledges this in Open Question 2 ("Should we use backbone-only contacts
throughout, or invest in side-chain reconstruction for a subset?") but does not
quantify how this limitation affects specific features. From a dynamics simulation
perspective, this is a critical gap:

**(a) At least 5 of 15 features are significantly degraded by backbone-only
representation.**

| Feature | Impact of backbone-only | Severity |
|---------|------------------------|----------|
| SASA (Feature 3) | Backbone SASA is ~30-40% of total SASA. Side chains dominate burial, especially hydrophobic packing. Backbone-only SASA misses the dominant contributor to binding interfaces and active sites. | High |
| H-bond persistence (Feature 10) | Backbone H-bonds (N-H...O=C) capture secondary structure stability but miss the majority of functionally relevant H-bonds: side-chain H-bonds at active sites, substrate contacts, and allosteric network connections. Serine/threonine/histidine/aspartate side-chain H-bonds are invisible. | High |
| Contact frequency (Feature 6) | Ca-Ca contacts at 8 A are a crude proxy for true atomic contacts. Aromatic stacking (Phe, Trp, Tyr), salt bridges (Lys-Asp, Arg-Glu), and hydrophobic packing (Ile, Leu, Val) -- all functionally critical -- require side-chain atoms. Ca-Ca contact maps miss contacts where side chains are long (Arg, Lys: ~7 A from Ca to terminal atom) and detect false contacts between residues whose Ca atoms are close but whose side chains point away from each other. | Medium-High |
| Cryptic pocket occupancy (Feature 14) | Cryptic pocket opening is often driven by side-chain rearrangement (rotamer switching of gatekeeper residues). PocketMiner was trained on all-atom structures. Applying it to backbone-only structures may produce unreliable scores. | High |
| Surface flexibility index (Feature 15) | Composite of SASA and RMSF; inherits SASA's backbone-only degradation. | Medium |

**(b) Features that are robust to backbone-only representation:**

| Feature | Robustness | Reason |
|---------|-----------|--------|
| RMSF (Feature 1) | High | Ca RMSF is the standard metric; backbone and all-atom RMSF are highly correlated |
| B-factor variance (Feature 2) | High | Same reasoning as RMSF |
| SS propensity (Feature 4) | High | DSSP operates on backbone atoms (H-bond geometry defined by N, C, O) |
| S2 order parameter (Feature 5) | High | Backbone N-H bond vector; Ca-C approximation is standard |
| Rg (Feature 11) | High | Ca-based Rg is the standard; correlates well with all-atom Rg |
| Asphericity (Feature 12) | High | Ca-based gyration tensor is standard |
| PC amplitudes (Feature 13) | High | Ca PCA is the standard in essential dynamics |
| MI (Feature 8) | Medium | Ca displacement MI captures backbone correlated motions, but misses side-chain-mediated allostery |
| Distance moments (Feature 7) | Medium | Ca distances are a reasonable proxy for backbone distance fluctuations |
| Inter-domain distance (Feature 9) | High | Center-of-mass-based; robust to atom selection |

**(c) Side-chain reconstruction introduces its own errors.** HPacker (Visani et al.,
2024) achieves chi1 accuracy of ~75-80% for buried residues but lower for surface
residues. Reconstructed side chains are placed in the context of a single backbone
frame without energy minimization across the ensemble, so they do not reflect true
side-chain dynamics -- they reflect the most likely rotamer given a static backbone
pose. Using HPacker-reconstructed side chains for SASA or H-bond calculation would
add a second layer of model noise (BioEmu backbone noise + HPacker rotamer noise)
on top of the signal.

**Addressable?** Yes, with honest scoping:
1. Separate the 15 features into "backbone-robust" (8 features) and "side-chain-
   dependent" (5 features) and run the full ML pipeline on each set independently.
   If backbone-robust features alone carry the functional signal, the paper is
   stronger because it avoids the side-chain reconstruction confound entirely.
2. For SASA specifically: report both Ca-SASA (backbone proxy) and HPacker-
   reconstructed SASA, and show the correlation between the two. If Ca-SASA
   already captures most of the variance, the backbone-only limitation is moot
   for this feature.
3. For cryptic pocket occupancy: explicitly test PocketMiner on backbone-only vs.
   all-atom structures from the PDB for the 8 overlap proteins. If backbone-only
   PocketMiner scores correlate well (r > 0.8) with all-atom scores, the feature
   is usable.
4. For H-bond persistence: restrict to backbone H-bonds and rename the feature
   "secondary structure hydrogen bond persistence" to avoid overclaiming.
5. Acknowledge in the paper that side-chain-mediated features are a known limitation
   and direction for future work with all-atom ensemble generators (Boltz-2, MD).

---

### 4. The Wildtype Ensemble Hypothesis Has Known Failure Modes for Allosteric Mutations

**Severity:** Moderate

The wildtype ensemble hypothesis states that the dynamics properties of the wildtype
protein predict mutation tolerance at each position without variant-specific sampling.
This is physically plausible for mutations that disrupt local packing or stability
(most mutations in a DMS experiment), because rigid positions tend to be mutation-
intolerant and flexible positions tend to be mutation-tolerant -- as demonstrated by
the March 2026 bioRxiv preprint showing median per-protein rho ~0.6 between RMSF
and mutational sensitivity.

However, the hypothesis has known failure modes:

**(a) Allosteric mutations far from the active site.** Lisanza et al. (Science 2025)
demonstrated that single point mutations can "dramatically alter conformational
equilibria with large functional consequences," and that "many predicted mutations
are far from regions undergoing the largest conformational changes." For such
mutations, the wildtype RMSF at the mutation position may be low (rigid, packed
position) yet the mutation's effect on function is large because it alters the
global energy landscape. The wildtype ensemble features at the mutation site
carry no information about the downstream conformational redistribution.

**(b) Gain-of-function mutations in kinases and receptors.** Oncogenic mutations
(e.g., BRAF V600E, EGFR L858R) often increase activity by shifting the
conformational equilibrium from inactive to active states. The wildtype ensemble
occupancy of the active conformation is low, and the mutation stabilizes it.
Wildtype RMSF at V600 in BRAF is not particularly unusual, yet the mutation has
dramatic functional consequences. Rana et al. (bioRxiv 2026) showed that BioEmu
augmented with MD can capture BRAF V600E effects, but only through variant-specific
ensemble generation -- precisely what the proposal de-emphasizes.

**(c) Mutations at allosteric network hubs.** Proteins like PDZ domains, GPCRs, and
allosteric enzymes have conserved allosteric networks where mutations at hub
positions propagate conformational changes over long distances (Lockless and Ranganathan,
Science 1999; Reynolds et al., Cell 2011). The wildtype MI feature (Feature 8)
would capture the hub connectivity, but the proposal's MI computation may not
converge at 2,000 samples (see Weakness 2), and the MLP encoding of MI (10-dimensional
local neighborhood profile) may not capture long-range allosteric propagation.

**(d) The per-protein rho ~0.6 leaves 64% of variance unexplained.** The March 2026
bioRxiv paper showing rho ~0.6 is encouraging, but rho = 0.6 means R^2 = 0.36 --
only 36% of variance in mutational sensitivity is explained by RMSF. The remaining
64% includes allosteric effects, specific side-chain interactions, and sequence
context that wildtype backbone dynamics cannot capture.

**Addressable?** Partially:
1. Include an explicit "allosteric protein" subset analysis for proteins with known
   allosteric mechanisms in the Tier 1 set (e.g., HIV protease, p53, kinases).
   Test whether wildtype ensemble features perform worse on these proteins
   than on non-allosteric proteins. This is a publishable sub-analysis regardless
   of direction.
2. For the 50 proteins with variant-specific ensembles (Tier 2 sampling), explicitly
   test whether variant-specific ensemble features improve predictions for allosteric
   proteins more than for non-allosteric proteins. This directly tests the hypothesis's
   failure mode.
3. Consider adding the Asymmetric Dynamic Coupling Index (DCIasym) from Ozkan et al.
   (PNAS 2025) as a 16th feature, which captures directional allosteric coupling
   and could partially address failure mode (a). However, DCIasym requires
   perturbation-response analysis, which is more computationally intensive than
   simple covariance analysis.

---

### 5. Alpha-M Integration Is Sound in Principle but Has Statistical Power Concerns

**Severity:** Moderate

The integration design is scientifically elegant: rank ensemble generators (BioEmu,
MACE-OFF24(M), SO3LR, AI2BMD, AMBER ff19SB, CHARMM36m) by S2 agreement with NMR
data, then correlate S2 agreement rank with fitness prediction quality rank. This
directly tests the combined paper's central thesis.

However:

**(a) 8 proteins x 6 generators = 48 data points is underpowered.** The proposal
correctly notes this is "sufficient for detecting strong effects (rho > 0.5) but
not subtle ones." For a Spearman rank correlation test with n = 48, the minimum
detectable effect (at alpha = 0.05, power = 0.80) is approximately rho = 0.40
(Zar, Biostatistical Analysis, 2010). But this assumes all 48 observations are
independent -- they are not, because 6 observations from the same protein are
correlated (same fitness labels, same DMS assay noise). The effective sample size
is closer to 8 proteins with 6 repeated measures per protein, which drastically
reduces power. A mixed-effects model would be more appropriate than a simple
rank correlation.

**(b) S2 agreement and fitness prediction quality may confound through protein
identity.** Some proteins are easier for both S2 prediction and fitness prediction
(e.g., ubiquitin: small, well-folded, extensively studied). If the correlation
between S2 agreement and fitness prediction is driven by protein identity rather
than by ensemble quality differences among generators, the integration claim is
weakened. The proposal should include a "protein-stratified" analysis where the
within-protein correlation across generators is the primary statistic, not the
pooled cross-protein correlation.

**(c) BioEmu ensembles and MD trajectories produce fundamentally different types
of conformational samples.** BioEmu generates independent equilibrium snapshots;
MD produces correlated frames from a continuous trajectory. S2 order parameters
are defined through time autocorrelation functions of bond vectors -- they are
intrinsically time-dependent quantities. Computing "S2" from BioEmu's independent
snapshots requires an alternative estimator (e.g., the bond vector variance
approach of Bremi and Ernst, 1997, as the proposal specifies), but this estimator
converges to the same value as the time-correlation S2 only under the assumption
of ergodic sampling of the equilibrium distribution. If BioEmu under-samples
rare conformations, the static S2 estimator may systematically overestimate
rigidity (because rare, large-amplitude motions are under-represented). This means
BioEmu S2 values should be compared against MD-derived S2 values from the same
estimator (bond vector variance from independent frames), not from time
autocorrelation, to ensure a fair comparison.

**Addressable?** Yes:
1. Use a mixed-effects model (protein as random effect, generator as fixed effect)
   rather than a simple rank correlation. This properly accounts for the repeated-
   measures structure.
2. Report both the pooled correlation and the within-protein correlation (mean
   rank correlation across generators within each protein).
3. Apply the same S2 estimator to both BioEmu samples and MD trajectory subsamples
   (e.g., 2,000 evenly-spaced frames from the MD trajectory) to ensure
   methodological comparability. Do not compare BioEmu bond-vector-variance S2
   against MD time-autocorrelation S2.
4. If Alpha-M delivers 15 proteins instead of 7 for the MVP (the stretch goal),
   the power increases to ~90 effective data points (15 proteins x 6 generators),
   which substantially improves detection. Coordinate with mlffeng on timeline
   to maximize overlap.

---

### 6. Two Missing Features Would Substantially Strengthen the Proposal

**Severity:** Minor

**(a) Normal mode analysis (NMA) features from the mean BioEmu structure.** The mean
structure of the BioEmu ensemble can be analyzed with elastic network models (ENMs)
such as the Anisotropic Network Model (ANM; Atilgan et al., Biophys J, 2001) to
extract low-frequency vibrational modes. ANM B-factors correlate with experimental
B-factors at r ~0.6-0.8 and capture collective motions that are mechanistically
linked to function (hinge motions, shear motions). Comparing BioEmu PCA modes
(Feature 13) with ANM modes would test whether BioEmu captures physically meaningful
collective motions or random fluctuations. If BioEmu PCA mode 1 aligns with ANM
mode 1 (overlap > 0.7), the ensemble captures the functionally relevant motion;
if not, the ensemble dynamics may be noise. NMA is computationally trivial (seconds
per protein on CPU with ProDy; Bakan et al., Bioinformatics, 2011).

**(b) Local packing density.** The number of Ca atoms within 10 A of each residue
(local packing density) is a simple, backbone-robust feature that captures the
structural environment of each position. It is complementary to RMSF (which
measures fluctuation) and SASA (which measures surface exposure). Tightly packed
core residues have high packing density and low RMSF; mutations at these positions
are typically destabilizing. Loosely packed surface residues have low packing
density and high RMSF; mutations are typically tolerated. Including packing density
would test whether the RMSF-fitness correlation is partially confounded by packing
effects (since RMSF and packing density are inversely correlated).

**Addressable?** Yes, trivially. Both features require seconds of CPU time per
protein. Add as Features 16 and 17 in the ablation study.

---

## Feasibility Assessment

### Technical Feasibility

**Strong.** BioEmu is pip-installable, MIT-licensed, and well-documented. ProteinGym
provides precomputed baseline scores for all 90+ methods. MDAnalysis, eRMSF, and
PocketMiner are mature, open-source tools. The GATv2 architecture is well-
established. SLURM scheduling for batch GPU jobs is standard HPC practice. The
major technical risk is BioEmu stability for longer proteins (>450 residues), which
the proposal addresses by excluding proteins >600 residues and flagging 450-600
residue proteins for additional quality control.

### Scientific Feasibility

**Moderate to Strong.** The base signal (RMSF-fitness rho ~0.6 per protein, from
the March 2026 preprint) is real and well-documented. The question is whether
this per-protein signal survives leave-protein-out cross-validation to become a
generalizable cross-protein signal. The per-protein stratified Spearman analysis
is the appropriate fallback if cross-protein generalization fails. The circularity
concern (BioEmu trained on stability data, tested on stability assays) is the
largest scientific risk and must be controlled explicitly.

The physically plausible expectation is that the Gamma proposal will show
statistically significant improvements on binding and catalysis assays (where
dynamics matter mechanistically) with modest or no improvement on stability
assays (where BioEmu circularity confounds the result) and no improvement on
expression assays (where dynamics are less relevant). This outcome is publishable
in Nature Computational Science if the effect sizes are convincing and the
statistical framework is rigorous.

### Timeline Feasibility

**Tight but achievable.** The 11-week timeline assumes no delays in BioEmu
installation, SLURM job scheduling, or ProteinGym data processing. Phase 1
(ensemble generation) is the critical path, but at 143 GPU-hrs for Tier 1, it can
complete on 4 H200 GPUs in approximately 36 hours of wall time. The real bottleneck
is Phase 2 (feature extraction at 88 GPU-hrs) and Phase 4 (Alpha-M integration at
200 GPU-hrs), which depend on Alpha-M delivering data. If Alpha-M is delayed beyond
Week 6, the integration analysis compresses into the writing phase, which is risky.

The proposal wisely includes the suggestion (Open Question 6) of pre-generating
AMBER ff19SB ensembles for the 8 overlap proteins as backup. I strongly endorse
this: 8 proteins x 50 ns x AMBER ff19SB is approximately 40 CPU-hours on OpenMM
(trivial), and these ensembles provide a non-ML baseline for the integration test
even without full Alpha-M data.

---

## Suggested Modifications

1. **Add a stability circularity control.** For stability-type DMS assays, compute
   BioEmu's own ddG prediction (which it was explicitly trained to produce) as a
   covariate. Test whether RMSF predicts fitness *after* regressing out BioEmu ddG.
   If yes, the dynamics signal is independent of the stability training signal. If
   no, the RMSF-fitness correlation for stability assays may be a training artifact.
   Report this analysis prominently. This is the single most important modification
   to preempt a devastating reviewer critique.

2. **Run the convergence pilot.** The proposal's Open Question 1 already identifies
   this need. Make it mandatory, not optional. Generate 10,000 samples for 5
   representative proteins (1 small, 1 medium, 1 large, 1 multidomain, 1 IDP).
   Compute all 15 features at sample sizes [500, 1000, 2000, 5000, 10000]. Report
   the coefficient of variation for each feature at each sample size. If MI and
   cryptic pocket features do not converge at 2,000 samples, either increase the
   sample count or drop these features from the primary analysis.

3. **Split features into backbone-robust and side-chain-dependent sets.** Run the
   full ablation pipeline on {Features 1, 2, 4, 5, 7, 8, 11, 12, 13} (backbone-
   robust) separately from {Features 3, 6, 10, 14, 15} (side-chain-dependent).
   If backbone-robust features carry the signal, the paper is cleaner and avoids
   the HPacker reconstruction confound entirely. If side-chain-dependent features
   add signal, include a HPacker sensitivity analysis in supplementary.

4. **Increase PocketMiner evaluation from 20 to 2,000 conformations.** The cost is
   negligible; the improvement in pocket occupancy estimation is substantial.
   PocketMiner inference on a single structure takes ~0.1 seconds on GPU. For 200
   proteins x 2,000 conformations = 400,000 evaluations, this is approximately
   11 GPU-hours -- well within the compute budget.

5. **Replace kurtosis with a robust bimodality metric.** Use Hartigan's Dip Test
   statistic or Ashman's D (separation between modes in a Gaussian mixture) instead
   of kurtosis for characterizing distance distribution shape. These are more
   interpretable, less sample-size-sensitive, and directly test the biologically
   interesting hypothesis (bimodal = two conformational states).

6. **Add NMA mode overlap as a quality control metric.** For each BioEmu ensemble,
   compute the overlap between PCA mode 1 and ANM mode 1 from the mean structure.
   Report this as a quality metric: high overlap indicates that BioEmu captures
   the expected functional motion, low overlap flags proteins where BioEmu ensemble
   dynamics may not be physically meaningful.

7. **Use a mixed-effects model for Alpha-M integration.** Replace the rank
   correlation test (Section 6.2) with a linear mixed-effects model: fitness
   prediction quality ~ S2 agreement + (1|protein). This properly accounts for
   the repeated-measures structure (6 generators x 8 proteins) and provides
   parameter estimates for the effect of ensemble accuracy on functional
   prediction quality.

8. **Ensure matched S2 estimation across generators.** Apply the same bond-vector-
   variance estimator to BioEmu snapshots, MD trajectory subsamples, and MLFF
   trajectory subsamples. Do not compare S2 values computed by different methods
   (time autocorrelation vs. static variance).

---

## Alternative Approaches

**Consider using Boltz-2 as a secondary ensemble generator.** Boltz-2 (Wohlwend et
al., 2025-2026) produces MD-conditioned ensembles with all-atom output, supports
multi-chain complexes, and can handle ligand-bound states. For the ~30 binding-type
ProteinGym assays where side-chain contacts at the binding interface are critical,
Boltz-2 ensembles could provide the all-atom features that BioEmu cannot. The
proposal mentions Boltz-2 in the ablation study ("BioEmu ensemble vs. AlphaFlow
vs. Boltz-2") but only as a generator comparison, not as a complementary all-atom
source for side-chain-dependent features. Generating Boltz-2 ensembles for 30
binding-assay proteins and extracting all-atom SASA, H-bond, and contact features
would directly test whether side-chain information adds signal. Compute cost would
be modest (Boltz-2 is comparable to BioEmu in speed for backbone generation but
adds side-chain prediction).

**Consider AlphaFlow (Jing et al., ICML 2024) as a faster alternative for the
convergence pilot.** AlphaFlow generates all-atom ensembles from AlphaFold2 weights,
including side chains. It is faster than BioEmu for short proteins. For the
convergence pilot (5 proteins, 10,000 samples), running both BioEmu and AlphaFlow
would test generator dependence of features at minimal additional cost.

---

## Impact on Publication Narrative

The Gamma proposal is the heart of the combined Gamma+Alpha-M paper. Its success
or failure determines whether the paper is "accurate ensembles predict function"
(positive, Nature Comp Sci) or "the dynamics prediction paradox: when do ensembles
help?" (mixed, still publishable but lower impact).

From the ensemble quality perspective, the proposal's strength is that the wildtype
ensemble hypothesis is falsifiable, pre-registered with kill criteria, and
independent of variant-specific BioEmu quality (which is known to be poor). Its
weakness is the unacknowledged stability circularity and the backbone-only limitation
that affects several features.

The modifications I recommend -- stability circularity control, backbone/side-chain
feature split, convergence pilot, and mixed-effects integration analysis --
collectively transform the paper from "we tried dynamics features and they helped
a bit" into "we systematically dissected when and why dynamics features help,
controlled for training-data circularity, validated ensemble quality against
experiment, and identified the physical mechanisms underlying dynamics-function
relationships." The second version is Nature Computational Science material; the
first is PLOS Computational Biology material.

The Alpha-M integration is not optional for the combined paper narrative. If
Alpha-M shows that MACE-OFF24(M) S2 values are closer to NMR experiment than
BioEmu S2 values (plausible, given that BioEmu was trained on AMBER dynamics,
not NMR data), and if MACE-OFF24(M) RMSF also better predicts fitness for the
8 overlap proteins, the combined paper has a uniquely compelling claim: "physically
accurate ensemble generators produce better functional predictions." This cannot
be achieved by either project alone. The proposal should explicitly plan for
this possibility and have the analysis pipeline ready for Day 1 of Alpha-M data
delivery.

---

## References

1. Lewis, S. et al. (2025). Scalable emulation of protein equilibrium ensembles
   with generative deep learning. *Science*, 369, 270-278.

2. Aryal, R. et al. (2026). Assessing the Performance of BioEmu in Understanding
   Protein Dynamics. *Int. J. Mol. Sci.*, 27(6), 2896.

3. Smith, D.G.A. et al. (2024). The Accuracy and Reproducibility of Lipari-Szabo
   Order Parameters From Molecular Dynamics. *J. Phys. Chem. B*, 128, 10419-10432.

4. Hacisuleyman, A. and Erman, B. (2024). Dynamic correlations: exact and
   approximate methods for mutual information. *Bioinformatics*, 40(2), btae076.

5. Lange, O.F. and Grubmuller, H. (2006). Generalized Correlation for
   Biomolecular Dynamics. *Proteins*, 62(4), 1053-1061.

6. Best, R.B. et al. (2014). Optimization of the additive CHARMM all-atom protein
   force field targeting improved sampling of the backbone phi, psi and side-chain
   chi(1) and chi(2) dihedral angles. *J. Chem. Theory Comput.*, 10, 3257-3273.

7. Piana, S. et al. (2015). How robust are protein folding simulations with
   respect to force field parameterization? *Biophys. J.*, 100(9), L47-L49.

8. Kovacs, D. et al. (2025). MACE-OFF24(M): Scalable machine learning force field
   for organic molecules. *JACS*, 147, 6810-6823.

9. Ozkan, S. et al. (2025). A protein dynamics-based deep learning model enhances
   predictions of fitness and epistasis. *PNAS*, 122, e2502444122.

10. Lisanza, S. et al. (2025). Computational design of conformation-biasing
    mutations to alter protein functions. *Science*.

11. Rana, M. et al. (2026). Accelerated sampling of protein dynamics using BioEmu
    augmented molecular simulation. *bioRxiv*, doi:10.64898/2026.01.07.698041v2.

12. Visani, G.M. et al. (2024). H-Packer: Holographic Rotationally Equivariant
    Convolutional Neural Network for Protein Side-Chain Packing. *J. Chem. Inf.
    Model.*, 64(5), 1710-1727.

13. Bremi, T. and Ernst, R.R. (1997). A protocol for the interpretation of
    side-chain dynamics based on NMR relaxation: application to phenylalanines
    in antamanide. *J. Am. Chem. Soc.*, 119(18), 4272-4284.

14. Atilgan, A.R. et al. (2001). Anisotropy of Fluctuation Dynamics of Proteins
    with an Elastic Network Model. *Biophys. J.*, 80(1), 505-515.

15. Bakan, A. et al. (2011). ProDy: Protein Dynamics Inferred from Theory and
    Experiments. *Bioinformatics*, 27(11), 1575-1577.

16. DeCarlo, L.T. (1997). On the meaning and use of kurtosis. *Psychol. Methods*,
    2(3), 292-307.

17. Csermely, P. et al. (2010). Structure and dynamics of molecular networks.
    *Trends Biochem. Sci.*, 35(10), 539-546.

18. Boehr, D.D. et al. (2009). The role of dynamic conformational ensembles in
    biomolecular recognition. *Nat. Chem. Biol.*, 5(11), 789-796.

19. Lockless, S.W. and Ranganathan, R. (1999). Evolutionarily conserved pathways
    of energetic connectivity in protein families. *Science*, 286(5438), 295-299.

20. Reynolds, K.A. et al. (2011). Hot spots for allosteric regulation on protein
    surfaces. *Cell*, 147(7), 1564-1575.

21. Wohlwend, J. et al. (2025-2026). Boltz-2: Towards Accurate and Efficient
    Binding Affinity Prediction. *bioRxiv*.

22. Jing, B. et al. (2024). AlphaFold Meets Flow Matching for Generating Protein
    Ensembles. *ICML 2024*.

23. Robustelli, P. et al. (2018). Developing a molecular dynamics force field for
    both folded and disordered protein states. *PNAS*, 115(21), E4758-E4766.

24. Han, Y. et al. (2025). BioEmu: AI-Powered Revolution in Scalable Protein
    Dynamics Simulation. *J. Cell. Mol. Med.*, 29, e70960.

25. Meller, A. et al. (2023). Predicting locations of cryptic pockets from single
    protein structures using the PocketMiner graph neural network. *Nat. Comms*,
    14, 1177.
