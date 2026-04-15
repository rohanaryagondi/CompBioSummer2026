---
agent: scopeadv
round: 3
date: 2026-04-14
type: critique
proposal_reviewed: gamma-dynamics-function
---

# Critique: Conformational Ensembles Predict Protein Function Beyond Sequence -- Strategic Review

## Reviewing Agent

Dr. Strategic Scope & Competition Analyst (scopeadv). Former academic researcher,
scientific program director, and journal editor. Reviewing the Gamma proposal from
the **publication strategy perspective**: competitive positioning, narrative
strength, scope calibration, timeline risk, scooping scenarios, editorial
psychology, and whether this paper changes how the field thinks or merely adds a
data point. mlffeng has covered the technical ensemble-quality issues. I cover
everything else an editor and a strategic program director would scrutinize.

## Proposal Summary

ensfunc proposes the first systematic framework connecting BioEmu-generated
conformational ensembles to ProteinGym DMS fitness prediction across ~200 proteins,
using 15 ensemble features and a 4-stage ML pipeline, with a wildtype ensemble
hypothesis as the central claim and Alpha-M integration on 8 proteins as the
combined-paper linchpin. Compute budget: ~3,037 GPU-hrs. Timeline: 11 weeks.
Success threshold: >55% win rate against ESMDance on binding/catalysis assays.

---

## Overall Assessment

**Verdict:** Support with Modifications

**One-line take:** The gap is real, the timing is right, and the wildtype
ensemble hypothesis is the correct editorial framing -- but the proposal is
dangerously over-scoped for an 11-week window, the standalone narrative is weaker
than it needs to be for Nature Computational Science, and the competitive moat
is thinner than the team believes.

---

## Strengths

1. **The gap remains genuinely open (confirmed April 14, 2026).** I conducted a
   fresh competitive scan across bioRxiv, arXiv, PubMed, Microsoft Research
   publications, Marks Lab / OATML outputs, and ICML/NeurIPS 2026 workshop
   submissions. No published or preprinted work connects explicit BioEmu-generated
   conformational ensembles to systematic ProteinGym DMS fitness prediction at
   scale. The ProteinGym leaderboard (90+ methods as of April 2026) contains zero
   methods incorporating explicit conformational ensemble features. Microsoft's
   February 2025 blog post "Exploring the structural changes driving protein
   function with BioEmu-1" focuses on drug discovery, cryptic pockets, and protein
   stability -- with no mention of ProteinGym, DMS fitness prediction, or
   systematic ensemble-to-function mapping. The gap is real.

2. **The wildtype ensemble hypothesis is the right editorial anchor.** From an
   editor's perspective, "wildtype dynamics predict mutation effects without
   simulating mutants" is a clean, surprising, testable claim. It is
   counterintuitive (you might expect you need to simulate each mutant), which
   makes it editorially interesting. It also has the virtue of being falsifiable
   with pre-registered kill criteria. This is the single strongest strategic
   element of the proposal. Nature Computational Science editors value papers
   where the main claim can be stated in one sentence and understood by a
   non-specialist.

3. **The assay-type stratification creates a publishable finding regardless of
   overall effect size.** Even if the overall Spearman improvement is modest
   (~0.02-0.03), showing that dynamics features disproportionately improve
   binding and catalysis predictions while adding nothing to stability or
   expression predictions would be a genuinely novel mechanistic finding. This
   stratification converts a potentially underwhelming overall result into a
   scientifically interesting differential finding. An editor would send this
   to review.

4. **Compute budget is realistic and disciplined.** The refined 3,037 GPU-hr
   estimate (down from Cohort 1's 8,200 estimate) reflects honest accounting.
   Tier 1 ensemble generation at 143 GPU-hrs is small enough that the entire
   hypothesis can be tested for less GPU time than a single day of H200
   utilization. This is a significant strength: the cost-benefit ratio is
   excellent for the potential upside.

5. **Kill criteria are genuinely pre-registered, not retroactive.** The June 30
   RMSF rho < 0.1 criterion and the July 31 win rate < 45% criterion are specific,
   dated, and actionable. In my experience as an editor and program director,
   fewer than 20% of computational biology proposals include kill criteria this
   concrete. Reviewers will notice and appreciate this.

6. **Negative result has a clear publication path.** The proposal explicitly plans
   for a negative outcome ("Why conformational ensembles fail to predict mutation
   effects") targeting Bioinformatics or PLOS Computational Biology. This is
   strategically sound: the team's time is not wasted regardless of outcome.

---

## Weaknesses

### 1. The Competition Window Is Narrower Than Assessed -- The Distogram Threat

**Severity:** Major

The proposal cites a 6-12 month competition window with 15-25% scoop probability.
My fresh scan reveals this is optimistic. Two developments shift the threat
landscape:

**(a) "Learning Dynamic Protein Representations at Scale with Distograms"
(bioRxiv January 29, 2026, doi:10.64898/2026.01.29.702509).** This preprint uses
residue-residue distance probability distributions (distograms) from AlphaFold2
as edge features in graph neural networks, explicitly framing this as a way to
encode "dynamic structural information" without explicit conformational sampling.
It reports improvements including a 4 Spearman-point improvement on affinity
prediction tasks. While this paper does not use BioEmu and does not benchmark
on ProteinGym DMS fitness per se, it occupies adjacent conceptual territory:
encoding conformational variability as features for protein function prediction.
If this group extends their distogram approach to ProteinGym -- which is a natural
next step and requires no new data -- they would partially scoop the Gamma
narrative. The key differentiator would be that Gamma uses *explicit* ensemble
features from *physical* sampling (BioEmu), while distograms use *implicit*
variability from *predicted* distance distributions. This distinction is real
but subtle. An editor who has already reviewed a distogram-to-fitness paper
may perceive Gamma as incremental.

**(b) "Mutation-induced reshaping of protein conformational dynamics revealed by
a coarse-grained modeling framework" (bioRxiv March 29, 2026,
doi:10.64898/2026.03.29.715126).** This preprint introduces ICed-ENM, a
coarse-grained framework that captures mutation-induced conformational
landscape changes. While methodologically different from Gamma, it occupies the
same intellectual space: connecting conformational dynamics to mutation effects.
If this group demonstrates predictive power on DMS data, it narrows the
novelty claim.

**(c) The Marks Lab / OATML ProteinGym maintainers are best positioned to do
this.** The ProteinGym team (Notin, Marks) has the data, the infrastructure, and
the community relationships to add a BioEmu-based method to the leaderboard.
They have not done so yet -- but they are the most dangerous potential
competitors because they could execute the core analysis (BioEmu ensembles on
ProteinGym proteins) with minimal setup time. I found no evidence they are
pursuing this, but the absence of evidence is not evidence of absence.

**(d) PEGASUS (JACS/JCIM 2026) predicts RMSF from sequence alone.** A
sequence-based flexibility predictor achieves Spearman improvements of 19-24%
over PredyFlexy on MD-derived RMSF prediction. If PEGASUS-predicted RMSF
correlates with DMS fitness as well as BioEmu-derived RMSF, it would undermine
the computational cost argument for explicit ensemble generation.

**Revised assessment:** Competition window is 4-8 months (not 6-12). Scoop
probability is 25-35% within 6 months (not 15-25%).

**Addressable?** Partially. Speed is the primary mitigation:
1. Post a preprint by September 2026, not October. This means the 11-week
   timeline must be compressed, not extended.
2. Frame the paper's novelty around *explicit physical ensembles* (not just
   "dynamics features"), which distograms and PEGASUS cannot provide.
3. Include a direct comparison: BioEmu RMSF vs. PEGASUS-predicted RMSF vs.
   distogram-derived variance as predictors of DMS fitness. This head-to-head
   comparison would strengthen novelty regardless of which approach wins.

---

### 2. The Standalone Gamma Narrative Is Weaker Than Nature Computational Science Requires

**Severity:** Major

Nature Computational Science has an explicit editorial criterion: papers should
represent "an advance in understanding likely to influence thinking in the field"
and should include "methodological development," not just "straightforward usage
of machine learning algorithms." Let me assess Gamma against these criteria.

**The editorial framing problem:** As a standalone paper, Gamma's central claim
is: "BioEmu ensemble features improve DMS fitness prediction, especially for
binding and catalysis assays." An editor scanning this would ask three questions:

(a) **Is this methodological development or application?** The ML architectures
are standard (MLP, XGBoost, GATv2). The features are standard biophysics
descriptors (RMSF, contacts, MI). The evaluation framework is standard
(leave-protein-out CV on ProteinGym). The only genuinely novel element is
connecting BioEmu to ProteinGym -- which is a data integration exercise, not
a methodological contribution. NCS editors are explicit that "straightforward
usage of machine learning algorithms is usually outside the journal's scope."
The GATv2 GNN with dynamics-informed edges is not novel enough to qualify as
methodological development in its own right.

(b) **Does this change how the field thinks?** If the result is positive
(dynamics help by ~0.03 Spearman), the field learns that dynamics features
provide marginal improvement on top of evolutionary and structural features.
This is interesting but not paradigm-shifting. If the result is negative (dynamics
do not help), the field learns a useful null result. Neither outcome changes
how researchers think about the problem at a fundamental level.

(c) **What is the paper's contribution beyond the data?** The strongest version
of this paper is not "dynamics features improve predictions" but rather "we
identify which physical mechanisms of protein dynamics are informative for which
types of biological function." The assay-type stratification gets at this, but
the proposal frames it as a secondary finding rather than the primary claim. An
editor would be more interested in "binding fitness depends on conformational
selection dynamics while catalytic fitness depends on active-site flexibility"
than in "our GNN beats ESMDance by 0.03 Spearman."

**What changes this calculus: the Alpha-M integration.** The combined
Gamma+Alpha-M paper has a fundamentally different editorial pitch: "Physically
validated ensembles predict function better than unvalidated ones." This IS a
paradigm claim. It connects ensemble quality (a physics question) to functional
prediction (a biology question) through experimental validation (an empirical
question). An NCS editor would send this to review. The standalone Gamma paper
is marginal for NCS; the combined paper is solidly within scope.

**Addressable?** Yes, through reframing and integration:
1. **Elevate the mechanistic stratification to the primary claim.** The paper's
   title should not be "Ensembles Predict Function" (a performance claim) but
   rather something like "Conformational Dynamics Encode Distinct Functional
   Information Across Protein Activities" (a mechanistic claim). This reframing
   makes the assay-type differential finding the lead result, not the overall
   Spearman improvement.
2. **Make the Alpha-M integration non-optional.** The standalone paper is NCS-
   marginal. The combined paper is NCS-strong. This means the project plan
   must prioritize the 8-protein integration data, not treat it as supplementary.
   If Alpha-M data is delayed, generate AMBER ff19SB ensembles (as Open Question 6
   suggests) and compare BioEmu vs. AMBER RMSF as predictors -- this still tests
   the ensemble quality hypothesis without waiting for MLFF data.
3. **Add a "mechanism" figure.** Visualize, for 3-4 exemplar proteins, how the
   dynamics features that drive fitness prediction map onto known functional
   sites. Show that the GNN attention weights concentrate on active sites for
   catalysis assays and binding interfaces for binding assays. This converts
   the paper from a benchmark study into a mechanistic discovery.

---

### 3. The Scope Is Too Broad for 11 Weeks

**Severity:** Major

Let me trace the critical path through the 11-week timeline with realistic
assumptions:

**Week 1-3: Ensemble Generation**
- ColabFold MSA retrieval for 200 proteins: realistic at ~4 hours on 16 CPU cores
- BioEmu Tier 1 sampling (200 proteins): 143 GPU-hrs. On 4 H200 GPUs, this is
  ~36 hours wall time. Achievable.
- BioEmu Tier 2 sampling (50 proteins x 20 variants): 1,700 GPU-hrs. On 8 H200
  GPUs, this is ~212 hours = ~9 days. This overlaps with Tier 1 and pushes into
  Week 4.
- **Risk: Tier 2 variant sampling is 12x the compute of Tier 1 and provides
  data for a secondary analysis.** The wildtype hypothesis is the primary claim.
  Variant sampling is a confirmatory analysis whose expected result (null, per
  Aryal) strengthens the wildtype narrative. Spending 56% of compute budget on
  a confirmatory analysis is strategically questionable.

**Week 2-4: Feature Extraction**
- 88 GPU-hrs for feature extraction. Achievable.
- But: if mlffeng's convergence concerns are valid and 5,000-10,000 samples are
  needed for MI and kurtosis features, this triples the ensemble generation cost
  and delays feature extraction by 2+ weeks.

**Week 4-6: ML Training**
- Nested leave-protein-out CV with 200 folds x 5 inner folds = 1,000 model
  trainings. For GNN at 15 min each, this is 250 GPU-hrs over ~5 days on 2 GPUs.
  Achievable but requires no debugging.

**Week 6-8: Ablation + Integration**
- This is where the timeline breaks. Feature importance (SHAP) requires
  1,000 permutation trainings (83 CPU-hrs for MLP). Group ablation (15 individual
  feature ablations x 200 folds) is an additional 3,000 model trainings.
  Ensemble-augmented baselines (3 methods x 200 folds) add 600 trainings.
  Alpha-M integration adds 200 GPU-hrs.
- **Total Week 6-8 compute: ~550 GPU-hrs + ~400 CPU-hrs**. Achievable
  computationally, but the *analysis* time is the bottleneck. Running 15 ablation
  experiments, interpreting results, generating figures, and identifying the
  narrative takes human time that is not accounted for.

**Week 8-11: Figures + Writing**
- 3 weeks for manuscript preparation is tight for a Nature Computational Science
  submission, which typically requires 6-8 main figures, 10-20 supplementary
  figures, and extended methods. First drafts of NCS papers typically take 4-6
  weeks from a team of 2-3 people writing in parallel.

**Net assessment:** The 11-week timeline works only if (a) variant sampling is
deferred, (b) no convergence issues arise with features, (c) Alpha-M data
arrives on schedule, and (d) writing begins in parallel with Week 6-8 analysis.
The probability of all four conditions holding is low (<30%).

**Addressable?** Yes, through scope reduction:
1. **Defer Tier 2 variant sampling to a later phase.** The wildtype hypothesis
   is the primary claim. Spend the 1,700 GPU-hrs on additional wildtype
   replicates (for convergence) or on AMBER/Boltz-2 comparison ensembles
   instead.
2. **Target a 14-week timeline.** Add 1 week for debugging/contingency and
   2 weeks for writing. This shifts the preprint target from mid-September
   to early October -- still within the competition window.
3. **Reduce from 200 to 150 proteins.** The 50 Tier 3 "no-ensemble" proteins
   are a nice-to-have control but not essential. The 50 Tier 1 + 100 Tier 2
   (wildtype only) = 150 proteins is sufficient for all primary claims and
   saves ~25% of ensemble generation time.

---

### 4. The Success Threshold Is Miscalibrated

**Severity:** Moderate

The proposal sets two success thresholds:
- (a) Higher average Spearman than ESMDance (~0.46) across all proteins
- (b) Win rate >55% against ESMDance in per-protein comparison
- (c) Significant improvement on binding + catalysis subsets

**Problem 1: ESMDance is the wrong benchmark.** ESMDance reports Spearman ~0.46
on ProteinGym, which is below ESM-1v (~0.43 originally but updated scores may
differ), TranceptEVE (~0.49), and GEMME (~0.48). Beating ESMDance is beating the
weakest dynamics-adjacent method, not beating the field. A reviewer will ask:
"You beat ESMDance, but do you beat TranceptEVE?" If the answer is no, the
paper's impact is diminished. The success threshold should be against the
field's top methods, not against the weakest dynamics baseline.

**Problem 2: Win rate >55% is barely above chance.** In a 200-protein comparison,
a 55% win rate means winning on 110 proteins and losing on 90. With sampling
noise in the leave-protein-out CV, a 55% win rate may not be statistically
significant (depends on the effect size distribution). The evaluation should
report the Wilcoxon signed-rank p-value for the win rate, not just the
percentage.

**Problem 3: The real success threshold is "does dynamics add value beyond
existing modalities?"** The most compelling result is not "our GNN beats
ESMDance" but "ESM2 + ensemble features > ESM2 alone" (Stage 4 ensemble-
augmented baselines). This directly answers the question: does dynamics provide
additive information beyond what PLMs already capture? The proposal includes
this analysis but buries it in Stage 4 rather than making it the primary
success criterion.

**Addressable?** Yes:
1. Redefine success threshold as: "ESM2-650M + ensemble features achieves
   statistically significant improvement (Wilcoxon p < 0.05) over ESM2-650M
   alone, stratified by assay type." This is the cleanest, most reviewer-proof
   success criterion.
2. Keep the ESMDance comparison as a secondary benchmark (dynamics-specific),
   but add GEMME and TranceptEVE as explicit baselines to beat for overall
   claims.
3. Report the Bayes factor or posterior probability of improvement, not just
   frequentist p-values. Bayesian analysis is increasingly expected in NCS.

---

### 5. Microsoft Scooping Scenario Is Under-Analyzed

**Severity:** Moderate

The proposal assesses Microsoft Research (BioEmu developers) as "not currently
pursuing this direction" based on the absence of evidence from their blog and
publications. This is correct as of April 14, 2026, but the analysis
underestimates the speed at which Microsoft could execute:

**(a) Microsoft has every advantage.** They built BioEmu. They have the model
weights, the training data, the team expertise, and the compute. They have
published BioEmu's ddG predictions, cryptic pocket detection, and domain
motion analysis. Connecting BioEmu to ProteinGym is a natural next step that
their team could execute in weeks, not months. If a Microsoft researcher reads
the Gamma preprint and decides to scoop or extend it, they could have a
submission within 2-3 months.

**(b) The blog post provides incomplete intelligence.** Corporate blog posts
are marketing documents, not research plans. Microsoft Research's actual
project pipeline is not publicly visible. The BioEmu GitHub repository
(github.com/microsoft/bioemu) shows activity but does not reveal internal
research directions. The blog post dates from February 2025, 14 months ago.

**(c) The mitigation strategy (scale and rigor) is weaker than assumed.**
The proposal states: "Submit preprint by October 2026; our scale (200 proteins)
and integration (Alpha-M) are hard to replicate quickly." But Microsoft has
more compute, a larger team, and deeper BioEmu expertise. If they chose to
replicate, they could match 200 proteins in weeks. The Alpha-M integration
is the only element Microsoft cannot easily replicate, because it requires
independent MLFF simulation data.

**Revised scooping probability from Microsoft: 10-20% within 6 months.** This
is higher than the proposal's implicit estimate but still manageable.

**Addressable?** Yes:
1. **Speed is the only real mitigation.** Post the preprint as early as possible.
   Every week saved on the timeline is a week of additional competitive moat.
2. **Alpha-M integration is the defensive moat.** Microsoft can replicate the
   standalone Gamma analysis but cannot replicate the combined Alpha-M+Gamma
   integration. This is another argument for making the integration non-optional.
3. **Consider reaching out to Microsoft.** If the team has any connection to
   the BioEmu developers, a brief communication asking "are you working on
   BioEmu + DMS fitness prediction?" would resolve the intelligence gap. This
   is standard practice in competitive scientific fields.

---

### 6. The "Worst Case Still Publishes" Claim Needs Testing

**Severity:** Minor

The proposal claims that a negative result ("dynamics don't help") is publishable
in Bioinformatics or PLOS Computational Biology. This is probably true, but the
claim requires nuance:

**(a) A fully negative result across all 200 proteins and all assay types is
unlikely.** Given the March 2026 preprint showing per-protein rho ~0.6 between
RMSF and mutational sensitivity, it is almost certain that RMSF correlates with
fitness *within* individual proteins. The interesting question is whether this
within-protein signal generalizes *across* proteins in leave-protein-out CV.
A "negative" result likely means "dynamics help within-protein but don't
generalize cross-protein," which is a publishable finding.

**(b) A negative result paper still requires the same amount of experimental
work.** The team cannot save time by discovering a negative result early. All
200 proteins must be analyzed, all features extracted, all ablations run. The
only savings is in the writing framing.

**(c) The venue floor matters.** "Why conformational ensembles fail to predict
mutation effects" would be publishable in Bioinformatics (IF ~5.8) or PLOS
Computational Biology (IF ~4.3), but these are not Nature Computational Science
(IF ~14). If the team invests 11 weeks and 3,037 GPU-hrs for a Bioinformatics
paper, the return on investment is low relative to spending the same resources
on Alpha-M or Delta.

**Addressable?** Yes:
1. The kill criteria (June 30, July 31) are correctly calibrated to detect
   the negative scenario early, before most compute is spent. This is the right
   approach.
2. If Kill Criterion 1 fires (RMSF rho < 0.1 for >50% of proteins), the
   pivot should be to Alpha-M or Delta, not to writing a negative result paper.
   The negative result paper can be written later, using the Tier 1 data already
   generated, without consuming additional compute.

---

### 7. The Title Options Are Weak

**Severity:** Minor

The proposal lists three title options:
1. "Conformational Ensembles Predict Protein Function Beyond Sequence"
2. "Dynamics-Informed Mutation Effect Prediction Across 200 Proteins"
3. "Wildtype Conformational Dynamics Predict Mutational Tolerance at Genome Scale"

**Editorial critique:**
- Title 1 is vague. "Beyond sequence" does not tell the reader *what* the
  ensembles add. It also overclaims -- the paper does not predict "function"
  writ large; it predicts DMS fitness scores, which are a proxy for function.
- Title 2 is descriptive but uninspired. "200 proteins" sounds like a methods
  paper, not a discovery paper. NCS editors want discovery framing.
- Title 3 is the best of the three but "genome scale" is a stretch for 200
  proteins (the human genome encodes ~20,000 proteins). Also, "mutational
  tolerance" is narrower than "mutation effects."

**Better alternatives:**
- "Wildtype protein dynamics predict the functional impact of mutations across
  diverse biological activities"
  (Emphasizes the surprise: wildtype-only, no mutant simulation needed)
- "Conformational flexibility encodes functional constraint: dynamics features
  reveal why mutations damage binding more than stability"
  (Leads with the mechanistic finding, which is the most novel element)
- "How protein motion shapes mutational outcomes: ensemble dynamics predict
  fitness effects where sequence models cannot"
  (Narrative hook + competitive framing)

**The best title will depend on results.** If the assay-type stratification
shows a dramatic differential (dynamics help binding/catalysis but not
stability), the title should lead with that finding. If the overall improvement
is modest, the title should lead with the wildtype hypothesis.

---

## Feasibility Assessment

### Technical Feasibility

**Strong.** BioEmu is pip-installable (confirmed: `pip install bioemu`, MIT
license). ProteinGym v1.3 provides precomputed baseline scores for all 90+
methods (CC-BY 4.0, direct download from proteingym.org). MDAnalysis v2.x,
eRMSF (JCIM 2026), PocketMiner, and GATv2 (PyG) are all mature, well-documented,
open-source tools. SLURM batch scheduling for ensemble generation is standard HPC
practice. The technical stack is production-ready. I assessed zero technical
feasibility risk on the infrastructure side. The only technical risk is BioEmu
quality for larger proteins (>450 residues), which the proposal correctly
addresses by excluding proteins >600 residues.

### Scientific Feasibility

**Moderate-Strong.** The base signal is real. The March 2026 bioRxiv preprint
(doi:10.64898/2026.03.19.713008) demonstrates median within-protein Spearman
rho ~0.6 between per-residue mutational sensitivity (ThermoMPNN-predicted ddG
std) and RMSF across ~2,000 proteins, including de novo designs lacking
evolutionary history. This is strong prior evidence that the wildtype ensemble
hypothesis holds. The eRMSF package (JCIM 2026, doi:10.1021/acs.jcim.5c02413)
was explicitly designed for BioEmu ensemble analysis, confirming that the tooling
ecosystem supports this project.

The key scientific uncertainty is whether the within-protein RMSF-fitness
correlation survives leave-protein-out cross-validation. The March 2026 paper
reports *within-protein* correlations, which are analytically different from
*cross-protein* generalization. The per-protein Spearman analysis (win rate
statistics) is the appropriate fallback if cross-protein generalization fails.

mlffeng's circularity concern (BioEmu trained on stability data, tested on
stability assays) is the most serious scientific risk and must be controlled.
The stability circularity control (regressing out BioEmu ddG before testing
RMSF-fitness correlation) is essential.

### Timeline Feasibility

**Tight.** As analyzed in Weakness 3, the 11-week timeline works only under
optimistic assumptions. Realistic estimate: 13-15 weeks for a submission-ready
NCS manuscript. The Tier 2 variant sampling (1,700 GPU-hrs) should be deferred
to protect the critical path. The preprint target should be adjusted from
mid-September to late September / early October.

**Critical path analysis:**
- Weeks 1-3: Ensemble generation (Tier 1 only) + MSA retrieval
- Weeks 2-4: Feature extraction (pipeline development + execution)
- Weeks 3-4: Statistical baseline (Stage 1: RMSF-fitness correlations)
  -- THIS IS THE GO/NO-GO CHECKPOINT
- Weeks 4-6: ML training (Stages 2-3: MLP, XGBoost, GNN)
- Weeks 6-8: Ablation + ensemble-augmented baselines (Stage 4)
- Weeks 7-9: Alpha-M integration (if data available) or AMBER comparison
- Weeks 8-11: Figure generation + supplementary analysis
- Weeks 10-14: Writing + revision + internal review
- Week 14: Preprint posted on bioRxiv (early October 2026)

The parallel writing strategy (begin methods section in Week 4, introduction
in Week 6, results sections as each analysis completes) can compress the
writing phase but requires discipline.

---

## Suggested Modifications

### Strategic Modifications (Priority Order)

1. **Scope down to 150 proteins, defer Tier 2 variant sampling.** The wildtype
   hypothesis is the primary claim. Tier 2 variant sampling (50 proteins x 20
   variants, 1,700 GPU-hrs) tests a *secondary* hypothesis whose expected result
   (null, per Aryal et al.) merely confirms the primary narrative. Redirect
   those GPU-hrs to: (a) convergence pilot on 5 proteins at 5,000-10,000 samples
   (as mlffeng recommends), (b) AMBER ff19SB ensembles for 8 integration
   proteins, and (c) PEGASUS-predicted RMSF comparison. This reduces the
   timeline by ~1 week and eliminates a major compute bottleneck.

2. **Reframe the primary claim from performance to mechanism.** Instead of
   "ensembles improve fitness prediction," lead with "conformational dynamics
   encode distinct functional constraints across protein activities." The
   performance improvement is evidence for the mechanistic claim, not the
   claim itself. This shifts the paper from a leaderboard study to a discovery
   study. Nature Computational Science editors will respond to the latter.

3. **Make Alpha-M integration non-optional.** The standalone Gamma paper is
   NCS-marginal; the combined paper is NCS-strong. If Alpha-M MLFF data is
   delayed, use AMBER ff19SB ensembles for the 8 overlap proteins as a fallback
   comparison. The question "do ensembles from different generators produce
   different functional predictions?" is answerable with BioEmu vs. AMBER alone,
   without waiting for MACE/SO3LR data. Pre-generate AMBER ensembles in Week 1
   (40 CPU-hrs for 8 proteins x 50 ns, trivial).

4. **Add a PEGASUS/distogram comparison.** Include PEGASUS-predicted RMSF and
   AlphaFold2-derived distogram variance as alternative dynamics proxies. If
   BioEmu RMSF outperforms PEGASUS and distogram predictors, the explicit
   ensemble generation is justified. If PEGASUS performs equally well, the
   paper pivots to "you don't need expensive ensembles -- predicted flexibility
   suffices," which is also publishable (but in a different venue). This
   comparison pre-empts the distogram preprint threat and strengthens the
   paper's competitive positioning.

5. **Compress the timeline to post a preprint by September 30.** Every week
   of delay increases scooping risk. Target September 30 for bioRxiv submission,
   not mid-October. This requires: (a) beginning writing in Week 4, (b)
   deferring variant sampling, (c) using pre-generated AMBER ensembles for
   integration instead of waiting for MLFF data.

6. **Redefine success threshold around additive value.** Replace "beat ESMDance"
   with "ESM2-650M + ensemble features significantly outperforms ESM2-650M
   alone, stratified by assay type." This is the reviewer-proof success
   criterion. Add GEMME and TranceptEVE as explicit baselines for overall
   performance claims.

7. **Add a scooping response protocol with dated triggers.** Expand Pivot
   Criterion (July 15) to a monthly competitive scan:
   - May 15: Check bioRxiv/arXiv for BioEmu+fitness preprints. If found, assess
     differentiation immediately.
   - June 15: Repeat scan. If a comprehensive competitor appears, accelerate
     preprint posting of the statistical baseline results (Stage 1) as a
     standalone short paper or letter.
   - July 15: Repeat scan. If scooped on the core claim, pivot to the
     Alpha-M integration angle exclusively.
   - Monthly scans continue until preprint is posted.

### Technical Modifications (Supporting)

8. **Adopt mlffeng's stability circularity control.** For stability-type DMS
   assays, regress out BioEmu's own ddG prediction before testing RMSF-fitness
   correlation. This is the single most important technical addition for
   surviving peer review.

9. **Run the convergence pilot as mandatory, not optional.** 5 proteins at
   500/1,000/2,000/5,000/10,000 samples. Report convergence profiles for all
   15 features. Drop MI and kurtosis from the primary analysis if they do not
   converge at 2,000 samples. This costs ~50 GPU-hrs and saves the team from
   a devastating reviewer critique about unconverged features.

10. **Increase PocketMiner from 20 to 2,000 conformations.** As mlffeng notes,
    this costs ~11 GPU-hrs and eliminates a clear methodological weakness.

---

## Alternative Approaches

### Alternative 1: The "MVP Preprint + Full Paper" Strategy

Instead of one comprehensive 11-week effort, split the work into two phases:

**Phase 1 (6 weeks): MVP Preprint**
- 50 Tier 1 proteins only
- RMSF + 4 backbone-robust features only (no MI, kurtosis, cryptic pockets)
- MLP + XGBoost only (no GNN)
- Statistical baseline + feature-based models
- Assay-type stratification
- Post on bioRxiv by July 15

**Phase 2 (8 weeks): Full Paper**
- Expand to 150 proteins
- Add pairwise and global features
- GNN architecture
- Alpha-M integration
- Ensemble-augmented baselines
- Submit to NCS by November 1

**Advantages:** Phase 1 establishes priority and tests the hypothesis cheaply.
If Phase 1 shows no signal, Phase 2 is cancelled. If Phase 1 shows signal,
Phase 2 builds on a known-good foundation with reduced scooping risk.

**Disadvantages:** The MVP preprint may be perceived as preliminary. NCS does
not typically accept papers that have been extensively preprinted in earlier
versions. However, the MVP preprint could target a different venue (e.g., a
letter in Bioinformatics or a short paper at ICML Computational Biology
Workshop) while the full paper targets NCS.

This is my recommended approach if the team assesses the scooping risk as
>25% within 6 months.

### Alternative 2: Reframe Around the Assay-Type Question

Instead of "do dynamics predict fitness?", reframe the entire paper around:
"For which types of biological function does conformational dynamics provide
predictive information?" This changes the paper from a performance benchmark
to a systematic scientific investigation. It makes negative results for
stability assays (expected due to circularity) a *feature* rather than a
*limitation*. It makes the assay-type differential finding the headline
result, not a secondary analysis. This framing is more aligned with NCS's
interest in "advances in understanding."

---

## Impact on Publication Narrative

### For the Combined Gamma+Alpha-M Paper

The Gamma proposal is the heart of the combined paper's narrative. If Gamma
shows that dynamics features predict function, the combined paper asks: "but
are all dynamics equal?" Alpha-M answers: "no -- physically accurate dynamics
produce better functional predictions." This two-act structure is editorially
compelling and unique.

**Critically, the combined paper's strength depends on the Gamma signal being
real.** If dynamics features do not improve fitness prediction at all, the
Alpha-M contribution (MLFF benchmark against NMR) stands alone as a Nature
Methods paper, but the combined narrative collapses. The kill criteria are
correctly designed to detect this scenario early.

### For the Standalone Gamma Paper

If forced to publish standalone, the paper must be reframed around the
mechanistic question (assay-type stratification) rather than the performance
question (beating baselines). The standalone paper should target the subtitle:
"Dynamics features reveal differential functional constraints across protein
activities." This framing positions the paper as a discovery, not a benchmark,
and makes it more defensible for NCS review.

### For the Overall Publication Portfolio

The Gamma timeline is the critical dependency for the combined paper. If
Gamma is delayed past October 2026, the combined paper cannot be submitted
before January 2027, which increases scooping risk for both projects.
Conversely, if Gamma posts a preprint by September 30, it establishes
priority regardless of Alpha-M's timeline, and the combined paper can be
assembled from the preprint + Alpha-M data when available.

**Recommendation:** Design Gamma for separability. Every analysis step must
produce a standalone result interpretable without Alpha-M. The combined
paper is assembled from two modular halves, not written as a monolith.
This principle is already stated in my Round 2 strategy proposal, and the
Gamma proposal follows it -- but the integration analysis (Component 6)
creates a dependency on Alpha-M data that should have a guaranteed fallback
(AMBER ff19SB ensembles).

---

## Kill Criteria Evaluation

### Kill Criterion 1 (June 30): RMSF rho < 0.1 across >50% of Tier 1 proteins

**Calibration:** The March 2026 bioRxiv preprint shows median within-protein
rho ~0.6 between mutational sensitivity (ThermoMPNN ddG std) and MD RMSF.
However, the Gamma proposal measures a different correlation: per-residue RMSF
vs. DMS fitness score at the mutation position. These are different quantities.
ThermoMPNN ddG std is a *predicted* mutation sensitivity metric derived from a
neural network; DMS fitness is a *measured* experimental quantity with assay-
specific noise. The DMS-derived correlation will be noisier and lower than the
ThermoMPNN-derived one. A more realistic expectation for RMSF vs. DMS fitness
is rho ~0.2-0.4 (not 0.6), depending on assay quality and protein type.

With this calibration, the kill criterion (rho < 0.1 for >50% of proteins) is
appropriately conservative. It would fire only if the signal is essentially
absent, which the March 2026 evidence suggests is unlikely. This is the right
threshold: tight enough to detect genuine failure, loose enough not to kill a
project with modest but real signal.

**Verdict: Correctly calibrated.**

### Kill Criterion 2 (July 31): Win rate < 45% against any top-5 baseline

**Calibration:** 45% win rate means losing on >55% of proteins. This is a
very low bar -- it fires only if the method is systematically worse than the
best existing methods. For a method providing truly additive information, 45%
win rate is essentially guaranteed even with modest improvement. This criterion
is appropriately lenient for the go/no-go purpose.

**Concern:** The criterion says "any single baseline in the top-5." This means
the method must achieve >45% win rate against at least one top-5 method. But
all top-5 methods are highly correlated (they all use evolutionary information).
The method might achieve 48% against all top-5 methods, which passes the
criterion but is not publishable.

**Suggested revision:** Change to "win rate >50% against ESM2-650M + ensemble
features vs. ESM2-650M alone" -- the additive value test. This directly tests
whether dynamics adds information beyond PLM features, which is the core
scientific question.

### Pivot Criterion (July 15): Scooping response

**Calibration:** This criterion triggers when a competitor preprint appears.
The response is sensible (assess differentiation, proceed if scale/rigor
differentiate). However, it should be expanded to include a *monthly* scan,
not a one-time assessment, as recommended in Suggested Modification 7.

**Overall kill criteria verdict: Good but need minor recalibration.**

---

## Worst Case Analysis

### Scenario 1: Dynamics features provide zero improvement across all assay types

**Probability: 10-15%.** Given the March 2026 within-protein rho ~0.6
evidence, a complete null is unlikely but possible if: (a) BioEmu's
AMBER ff14SB biases distort the RMSF sufficiently that it does not
correlate with real DMS data, or (b) the within-protein signal does not
survive leave-protein-out cross-validation because the dynamics-function
relationship is too protein-specific.

**Publication path:** "Why conformational ensembles fail to predict mutation
effects" in Bioinformatics or PLOS Comp Biol. Estimated impact: moderate.
Key contribution: systematic null result that saves the field from
pursuing this direction.

### Scenario 2: Dynamics features help only for binding/catalysis, not overall

**Probability: 40-50%.** This is the most likely outcome. Overall Spearman
improvement is ~0.01-0.02 (not SOTA), but binding/catalysis assays show
statistically significant improvement while stability/expression do not.

**Publication path:** Nature Computational Science if framed as a mechanistic
discovery. Nature Methods if framed as a methodological contribution.
Estimated impact: high, especially if the assay-type differential is
dramatic (e.g., binding improvement rho = +0.05 while stability = +0.00).

### Scenario 3: Dynamics features provide strong overall improvement

**Probability: 10-20%.** Overall Spearman improvement of +0.03-0.05, with
consistent improvement across most assay types and win rate >60% against
ESMDance.

**Publication path:** Nature Computational Science as a clear-cut
contribution. Estimated impact: very high. This would establish dynamics
as a new modality for variant effect prediction.

### Scenario 4: Scooped before preprint

**Probability: 15-25% within 6 months.** A competitor (Microsoft, Marks Lab,
distogram group, or an independent team) publishes BioEmu+DMS fitness
prediction before our preprint.

**Response:** Assess differentiation. If their analysis covers <50 proteins,
proceed with scale as differentiator. If comprehensive, pivot to Alpha-M
integration angle exclusively.

### Scenario 5: BioEmu quality is insufficient for most proteins

**Probability: 10-15%.** BioEmu fails convergence or quality checks for
>40% of the 200 target proteins (e.g., due to length, multidomain
architecture, or IDP behavior).

**Response:** Reduce to the proteins where BioEmu works well. A study
covering 100-120 proteins is still sufficient for all primary claims.
Add Boltz-2 or AlphaFlow as alternative generators for failed proteins.

### Expected outcome: Scenario 2 is most likely, with a 40-50% probability.

This is a good outcome strategically: it produces a publishable paper with
a novel mechanistic finding, supports the combined Gamma+Alpha-M narrative,
and positions the team as pioneers in the dynamics-to-function space.

---

## References

1. Lewis, M. et al. (2025). Scalable emulation of protein equilibrium ensembles
   with generative deep learning. *Science*, 369, 270-278.

2. Notin, P. et al. (2023). ProteinGym: Large-Scale Benchmarks for Protein
   Fitness Prediction and Design. *Advances in NeurIPS*.

3. Hou, C., Zhao, H., and Shen, Y. (2026). Protein language models trained on
   biophysical dynamics inform mutation effects. *PNAS*, 123(4), e2530466123.

4. [Mutational robustness paper] (2026). Mutational Robustness Predicts Protein
   Dynamics Across Natural and Designed Proteins. *bioRxiv*,
   doi:10.64898/2026.03.19.713008.

5. Ozkan, S. et al. (2025). A protein dynamics-based deep learning model enhances
   predictions of fitness and epistasis. *PNAS*, 122, e2502444122.

6. Aryal, R. et al. (2026). Assessing the Performance of BioEmu in Understanding
   Protein Dynamics. *Int. J. Mol. Sci.*, 27(6), 2896.

7. Microsoft Research (2025). Exploring the structural changes driving protein
   function with BioEmu-1. Blog post, February 20, 2025.
   URL: https://www.microsoft.com/en-us/research/blog/exploring-the-structural-changes-driving-protein-function-with-bioemu-1/

8. [Learning Dynamic Protein Representations] (2026). Learning Dynamic Protein
   Representations at Scale with Distograms. *bioRxiv*,
   doi:10.64898/2026.01.29.702509.

9. [ICed-ENM] (2026). Mutation-induced reshaping of protein conformational
   dynamics revealed by a coarse-grained modeling framework. *bioRxiv*,
   doi:10.64898/2026.03.29.715126.

10. [eRMSF] (2026). eRMSF: A Python Package for Ensemble-Based RMSF Analysis
    of Biomolecular Systems. *JCIM*, doi:10.1021/acs.jcim.5c02413.

11. Schneider, M. et al. (2025). EnsembleFlex: Protein Structure Ensemble Analysis
    Made Easy. *Structure*.

12. [Portal et al.] (2026). Conformational ensembles improve protein fitness
    prediction via distogram features. *bioRxiv*.

13. Burgin, D. et al. (2025). Quantified Dynamics-Property Relationships:
    Data-Efficient Protein Engineering with Machine Learning of Protein Dynamics.
    *JCIM*.

14. Meller, A. et al. (2023). Predicting locations of cryptic pockets from single
    protein structures using the PocketMiner graph neural network. *Nature Comms*,
    14, 1177.

15. Rana, M. et al. (2026). Accelerated sampling of protein dynamics using BioEmu
    augmented molecular simulation. *bioRxiv*, doi:10.64898/2026.01.07.698041v2.

16. Lisanza, S. et al. (2025). Computational design of conformation-biasing
    mutations to alter protein functions. *Science*.

17. Wohlwend, J. et al. (2025-2026). Boltz-2: Towards Accurate and Efficient
    Binding Affinity Prediction. *bioRxiv*.

18. Jing, B. et al. (2024). AlphaFold Meets Flow Matching for Generating Protein
    Ensembles. *ICML 2024*.

19. [PEGASUS] (2026). PEGASUS: Prediction of MD-derived protein flexibility from
    sequence. *PMC/JCIM*.

20. Notin, P. (2026). Have We Hit the Scaling Wall for Protein Language Models?
    Blog post, Pascal Notin.

21. Nature Computational Science Editorial (2021). To review or not to review.
    *Nature Computational Science*, 1, 223.

22. [FLIP2] (2026). FLIP2: Expanding Protein Fitness Landscape Benchmarks for
    Real-World Machine Learning Applications. *bioRxiv*,
    doi:10.64898/2026.02.23.707496.

23. Cheng, J. et al. (2023). Accurate proteome-wide missense variant effect
    prediction with AlphaMissense. *Science*, 381, 1303-1308.

24. Frazer, J. et al. (2021). Disease variant prediction with deep generative
    models of evolutionary data. *Nature*, 599, 91-95.

25. He, K. et al. (2025). AIDO Protein-RAG: Retrieval-Augmented Generation for
    Protein Fitness Prediction.

26. [BioEmu-CV] (2026). Learning Collective Variables from BioEmu with Time-Lagged
    Generation. *arXiv*, 2507.07390.

27. [Boltz-sample] (2026). Steering Conformational Sampling in Boltz-2 via Pair
    Representation Scaling. *bioRxiv*, doi:10.64898/2026.01.23.701250.

28. Brody, S. et al. (2022). How Attentive are Graph Attention Networks?
    *ICLR 2022*.

29. Laine, E., Karami, Y., and Bhatt, T. (2019). GEMME: A Simple and Fast Global
    Epistatic Model Predicting Mutational Effects. *Mol. Biol. Evol.*, 36(11),
    2604-2619.

30. Meier, J. et al. (2021). Language models enable zero-shot prediction of the
    effects of mutations on protein function. *Advances in NeurIPS*.
