---
agent: ensfunc
round: 3
date: 2026-04-14
type: critique
proposal_reviewed: delta-perturbmark
---

# Critique: PerturbMark -- Cross-Domain Lessons from Protein Dynamics Benchmarking

## Reviewing Agent

Dr. Maverick Ensemble-to-Function Expert (ensfunc). 10 years across structural
bioinformatics, protein engineering, and ML for biology. This review examines
PerturbMark from a **cross-domain perspective**: I bring benchmark design lessons
from ProteinGym (217 DMS assays, 90+ models), CASP (30 years of blind assessment),
and MoleculeNet (600K compounds), as well as conceptual analogies between
conformational ensembles and biological replicates, and between the "does dynamics
add value beyond sequence?" question (Gamma) and the "does DL add value beyond
linear?" question (Delta). My value is in seeing structural parallels that the
perturbation biology specialists miss, and in identifying benchmark design pitfalls
that have been learned the hard way in adjacent fields.

## Proposal Summary

PerturbMark proposes a cross-context benchmark on Tahoe-100M (100M cells, 50 cell
lines, 379 compounds, CC0) evaluating 10+ perturbation prediction methods across 4
difficulty tiers (Tier 0-3) using a calibrated 7-metric suite, 5 mandatory linear
baselines, batch effect controls, and leakage prevention protocols. Target: Nature
Methods preprint by August 15, 2026 (revised from July 15 per scopeadv recommendation).

---

## Overall Assessment

**Verdict:** Support with Modifications

**One-line take:** PerturbMark is the strongest perturbation benchmark proposal I
have seen, and the Tier 0-3 difficulty stratification is genuinely innovative, but
the proposal underexploits its richest asset -- the heterogeneity within Tahoe-100M
conditions -- and misses several benchmark design lessons that have been painfully
learned in the protein fitness prediction and molecular property prediction fields.

---

## Strengths

1. **Tier 0-3 difficulty stratification is a genuine contribution to benchmark
   methodology.** No existing biological benchmark I know of defines difficulty tiers
   with the precision PerturbMark proposes. CASP distinguishes TBM-Easy, TBM-Hard,
   FM/TBM, and FM categories based on template availability (Kryshtafovych et al.,
   Proteins 2014, 2019, 2021), but these are post-hoc classifications assigned by
   assessors, not pre-specified split designs. ProteinGym does not define explicit
   difficulty tiers at all -- it stratifies by assay type (stability, binding,
   activity, organismal fitness, expression) but not by prediction difficulty within
   each type (Notin et al., NeurIPS 2023). PerturbMark's pre-specified Tier 0-3,
   defined by the intersection of perturbation generalization and context
   generalization, is structurally cleaner and more principled than either. This alone
   justifies a benchmark paper. If PerturbMark contributes nothing else beyond the
   Tier system and calibrated metrics, it has advanced benchmark methodology.

2. **Calibrated metric primacy addresses a real failure mode that ProteinGym also
   struggles with.** In ProteinGym, the primary metric is Spearman rho, which is
   robust to monotone transformations but insensitive to the magnitude of fitness
   effects. A model that correctly orders benign vs. pathogenic variants but assigns
   meaningless absolute scores gets the same Spearman rho as one that calibrates
   perfectly. ProteinGym v1.3 partially addresses this by stratifying by assay type
   (structure-aware models excel on stability but not activity -- Notin et al., 2023),
   but the core metric remains rank-based. PerturbMark's WMSE is an error-magnitude
   metric that penalizes mode collapse by weighting DEGs. The combination of WMSE
   (error magnitude on biologically relevant genes) and a rank-based metric (per
   evalstat's recommendation of Spearman on top-k DEGs) provides non-redundant
   information that ProteinGym's single-metric approach misses. This is a design
   advance that ProteinGym should learn from.

3. **The mandatory 5-baseline requirement is the correct default posture.** In
   ProteinGym, the zero-shot prediction leaderboard includes both unsupervised
   (EVE, DeepSequence) and supervised methods, but the "baseline" is poorly defined
   -- there is no equivalent of PerturbMark's "you must beat all 5 linear baselines
   before claiming DL superiority." The CRISPR-informed mean (Wong et al.,
   Bioinformatics 2025) is the perturbation prediction analog of the "wild-type
   frequency" baseline in variant effect prediction. Its inclusion as mandatory is
   non-negotiable, and the proposal correctly identifies this.

4. **The DRF meta-metric is a self-diagnosing mechanism that other benchmarks lack.**
   Neither ProteinGym, CASP, nor MoleculeNet has a built-in mechanism for detecting
   when its own metrics are unreliable on a given dataset. DRF detects this by
   comparing model performance to interpolated duplicate positive controls and
   random-permutation negative controls. This is analogous to what CASP does manually
   (assessors visually inspect FM models because GDT-TS fails on loose resemblances),
   but automated and pre-specified. This should be adopted by future benchmarks
   in adjacent fields.

5. **Pre-specified effect size threshold addresses Goodhart's Law.** When benchmarks
   become targets, they cease to be good measures (Goodhart, 1975; Strathern, 1997).
   The LLM benchmark gaming phenomenon -- where selective model submissions inflated
   Arena scores by up to 100 points through cherry-picking (Chatbot Arena analysis,
   2025) -- demonstrates this vividly. PerturbMark's pre-specified 5% WMSE threshold
   reduces gaming by defining what counts as meaningful before results are seen. This
   is structurally similar to pre-registration in clinical trials. The threshold needs
   empirical calibration (as evalstat noted), but the principle is sound and rare
   in computational biology benchmarks.

6. **The "both outcomes are publishable" design is strategically mature.** In Gamma
   (my domain), the analogous question is "does dynamics add value beyond sequence
   for function prediction?" If the answer is no, that is itself a publishable
   finding -- and the paper design must accommodate this. PerturbMark correctly
   designs around both positive and negative outcomes at each tier. This is a lesson
   from CASP, where the most impactful rounds were those that revealed unexpected
   failures (e.g., CASP14 revealing that AlphaFold2 solved template-free modeling
   while most methods stagnated -- Jumper et al., Nature 2021). The benchmark's
   value comes from the answer, not from the answer being positive.

---

## Weaknesses

### 1. The Feature-vs-Model Blind Spot: PerturbMark Tests Models but Not Representations

In Gamma, the central question is not just "does BioEmu outperform AlphaFold2 for
function prediction?" but "what FEATURES of conformational ensembles predict
function?" -- RMSF, S2 order parameters, contact frequency changes, pocket volumes,
inter-residue distance distributions. The distinction matters because if we discover
that a simple feature (e.g., RMSF at the active site) predicts function as well as
an end-to-end model, this tells us something fundamental about the biology. The
feature IS the insight.

PerturbMark does not test this. It evaluates whole models (CPA, scGPT, PerturbNet,
etc.) against whole baselines, but does not decompose what features drive predictions.
This is a missed opportunity with structural parallels across computational biology.

**Evidence from adjacent fields:**
- In MoleculeNet (Wu et al., Chem Sci 2018), one of the most impactful findings was
  that physics-aware featurizations (Coulomb matrices, grid featurizations) were more
  important than choice of learning algorithm for quantum mechanical property
  prediction. The feature mattered more than the model.
- In ProteinGym, Notin et al. (NeurIPS 2023) showed that multimodal models combining
  MSA and structure outperform sequence-only or structure-only models, revealing that
  the information source (evolutionary vs. structural) matters as much as the model
  architecture.
- In perturbation prediction, D-SPIN (Yao et al., Nat Biotechnol 2024) identifies
  gene programs through unsupervised NMF and constructs regulatory networks,
  demonstrating that program-level features can capture perturbation biology that
  gene-level features miss.

**Specific recommendation:** Add a "Feature Importance" module to PerturbMark that
decomposes predictions into feature contributions. Specifically:

(a) **Gene program features vs. raw gene expression.** For each method, project
predictions into gene program space (using Hallmarks, KEGG, Reactome gene sets)
and evaluate at the pathway level. Some recent work suggests pathway-level evaluation
may reveal DL advantages invisible at the gene level (D-SPIN; also Dibaeinia et al.,
2026, showed DEG recall is only ~9%, implying gene-level evaluation may miss
program-level accuracy). Report WMSE at both gene level and program level.

(b) **Feature ablation for linear baselines.** Baseline 5 (per-gene ridge) uses
Morgan fingerprints + MOA + cell line features. Which features drive performance?
Ablate each feature group and measure WMSE change. If MOA one-hot alone explains
80% of the baseline's performance, this tells the field that mechanism knowledge,
not raw chemistry, is what matters -- a finding with major implications for method
design.

(c) **Representation similarity analysis.** For DL methods that produce internal
representations (CPA embeddings, scGPT hidden states), compute Centered Kernel
Alignment (CKA) between these learned representations and curated biological
features (pathway scores, drug target embeddings, cell line transcriptomic
signatures). This reveals whether DL methods rediscover known biology or learn
genuinely novel representations.

- **Severity:** Major
- **Addressable?** Yes. The gene program evaluation adds ~50 lines of code
  (project predictions into pathway space using gsva or decoupler). The feature
  ablation adds ~5 GPU-hrs (retrain Baseline 5 with ablated features). The CKA
  analysis adds ~2 GPU-hrs. Total additional compute: <10 GPU-hrs, well within
  budget. This module transforms PerturbMark from "which model wins?" to "what
  information predicts perturbation response?" -- a fundamentally more valuable
  question for the field.

### 2. Biological Replicates Are Underexploited: The Ensemble Analogy

In protein dynamics, a conformational ensemble is a collection of structures
sampled from the Boltzmann distribution. The ensemble captures the inherent
variability of the system, and the VARIANCE of the ensemble is as informative as
its mean. In Gamma, I proposed extracting not just mean RMSF but the full
distribution of RMSF across an ensemble -- the shape of the distribution, not just
its center, predicts function.

Tahoe-100M has an analogous structure: multiple cells per condition constitute a
biological ensemble. The proposal correctly aggregates to pseudobulk (mean
expression per condition) for tractability, but then evaluates predictions
ONLY at the pseudobulk level. The single-cell distributional metric (MMD, Metric 7)
is relegated to supplementary. This discards the single richest information source
in the dataset.

**The cross-domain insight:** Just as conformational ensemble variance predicts
protein function (Nussinov et al., Curr Opin Struct Biol 2024: "the propensities of
the conformations can be predictors of cell function"), response heterogeneity
across cells within a condition may predict perturbation efficacy. A perturbation
that produces a tightly clustered response (low variance) may act differently from
one that produces a bimodal response (high variance), even if their mean responses
are identical. Pseudobulk evaluation erases this distinction.

**Recent evidence:**
- Mixscale (Burkhardt et al., Nat Cell Biol 2025) demonstrated that modeling
  individual cellular variation in perturbation response reveals information invisible
  to population-level metrics. Their perturbation-response score captures per-cell
  variation that pseudobulk analysis misses entirely.
- Weinberger et al. (Nat Genet 2025) showed that modeling heterogeneity in
  single-cell perturbation states enhanced detection of response eQTLs by 36.9%
  compared to discrete (pseudobulk) models. The cell-level heterogeneity is not
  noise -- it is signal.
- MrVI (Boyeau et al., Nat Methods 2025) integrates biological replicates into a
  shared embedding while preserving sample-level heterogeneity, demonstrating that
  deep generative models can leverage replicate structure for improved perturbation
  effect estimation.

**Specific recommendation:** Elevate single-cell distributional evaluation from
supplementary to a Tier 0 and Tier 1 co-primary analysis (Tier 2-3 may have
insufficient cells per condition for distributional tests). Specifically:

(a) Add a **response heterogeneity metric**: for each condition, compute the
variance (or entropy) of per-cell perturbation responses. Report whether methods
that capture this heterogeneity (distributional models like PerturbNet, scDFM)
outperform point-prediction models (CPA, scGPT) on conditions with high
heterogeneity.

(b) Stratify results by **response modality**: bimodal conditions (where a drug
affects only a subpopulation) vs. unimodal conditions. Test whether DL methods
show differential advantage on bimodal vs. unimodal conditions. This is the
perturbation analog of testing whether dynamics features predict function better
for proteins with multiple conformational states (e.g., allosteric proteins)
vs. single-state proteins.

(c) Report a **replicate concordance** metric: for conditions measured on multiple
plates, compute the agreement between plate-specific pseudobulk profiles. This is
analogous to computing the convergence of a conformational ensemble simulation --
if replicates disagree, the "ground truth" pseudobulk is unreliable, and any
metric computed on it is questionable.

- **Severity:** Major
- **Addressable?** Yes, for Tier 0-1. Distributional evaluation at Tier 2-3 may
  require subsampling to equalize cell counts, which adds complexity. Recommend
  implementing for Tier 0-1 as primary, Tier 2-3 as exploratory. Additional
  compute: ~20 GPU-hrs for MMD computation at single-cell level across Tier 0-1.

### 3. ProteinGym's Assay Heterogeneity Lesson: MOA Is Not Enough

ProteinGym stratifies its 217 assays into 5 functional categories: stability,
binding, activity, organismal fitness, and expression. This stratification revealed
that model performance varies dramatically by function type: structure-aware models
(ESM-IF1) excel on stability (Spearman rho = 0.624) but lag on activity and
organismal fitness, while MSA-based models show the opposite pattern (Notin et al.,
NeurIPS 2023, v1.3 update). This finding -- that no single method dominates across
all function types -- is one of ProteinGym's most important contributions.

PerturbMark plans MOA-stratified analysis (25 categories), which is the correct
analog. But ProteinGym's experience suggests two additional stratifications that
PerturbMark should adopt:

**(a) Perturbation effect magnitude stratification.** In ProteinGym, methods
perform very differently on assays with large dynamic range (many strongly
deleterious variants) vs. narrow dynamic range (most variants near wild-type).
Analogously, PerturbMark should stratify by perturbation effect size: strong
perturbations (many DEGs, large fold changes) vs. weak perturbations (few DEGs,
small effects). The DL-vs-linear comparison may differ dramatically between
strong and weak perturbations. If DL wins only on strong perturbations (where
the signal is clear) but not on weak ones (where signal-to-noise is low), this
tells the field something important about the signal regime where DL helps.

**(b) Cell line transcriptomic diversity stratification.** ProteinGym showed
that prediction difficulty correlates with MSA depth (proteins with shallow
MSAs are harder to predict). The PerturbMark analog is cell line transcriptomic
distinctiveness. Cell lines with unique transcriptomic profiles (far from the
training set centroid) should be harder to predict than those with common
profiles. Report prediction error as a function of cell line distance from the
training set centroid (measured by Pearson correlation on DMSO expression
profiles). This connects to evalstat's concern about the organ-based holdout
confound: if transcriptomic distance, not organ identity, drives Tier 2-3
difficulty, then random holdout should produce similar results to organ-based
holdout (testing evalstat's sensitivity analysis recommendation).

- **Severity:** Minor
- **Addressable?** Yes. Both stratifications require only post-hoc analysis of
  existing results. Zero additional compute. Add as planned analyses in the
  analysis phase (Week 5 of the sprint).

### 4. The Difficulty Tier Validation Gap: Is Tier 3 Actually Harder Than Tier 2?

PerturbMark assumes a monotonic difficulty gradient: Tier 0 > Tier 1 > Tier 2 >
Tier 3 performance. This is a reasonable prior, but it is an assumption, not a
guaranteed property. CASP's experience is instructive: the difficulty ranking of
TBM-Easy > TBM-Hard > FM/TBM > FM generally holds, but specific targets violate
monotonicity. Some "easy" template-based targets are harder than some "free
modeling" targets because the available template is misleading (incorrect
oligomeric state, missing ligand-induced conformational change). The difficulty
category describes the information available to the predictor, not the intrinsic
difficulty of the prediction.

For PerturbMark, Tier 3 is defined as the intersection of Tier 1 (unseen
perturbation) and Tier 2 (unseen context). But this does not guarantee that Tier 3
is harder than either Tier 1 or Tier 2 individually. Consider: a method might
perform poorly at Tier 2 because it cannot predict baseline expression in an unseen
cell line, but perform better at Tier 3 because the perturbation effect (delta) is
conserved across cell lines even when baseline expression differs. In other words,
if the drug effect is cell-line-invariant for the held-out compounds, Tier 3 may
not be harder than Tier 2.

**Specific recommendation:** The monotonic difficulty gradient should be tested,
not assumed. If the gradient is violated (Tier 3 performance > Tier 2 performance
for some methods), this is itself a finding -- it reveals that the barriers to
cross-context prediction are not additive. Report the pairwise Tier performance
differences with confidence intervals. If any method violates monotonicity at
p < 0.05, flag this as a key finding and discuss what it reveals about the
structure of cross-context generalization.

Furthermore, decompose Tier 3 difficulty into its two components:
- **Tier 3 performance = f(Tier 1 difficulty, Tier 2 difficulty, interaction)**
- Fit a simple model: Tier3_error ~ Tier1_error + Tier2_error + Tier1*Tier2
- If the interaction term is significant, the two difficulty axes are non-additive,
  which has implications for how methods should handle cross-context prediction
  (e.g., whether a method should separately model perturbation generalization and
  context generalization, or jointly).

- **Severity:** Minor
- **Addressable?** Yes. This is a post-hoc analysis requiring zero additional
  computation. Add to the analysis plan.

### 5. Leaderboard Design: ProteinGym's Cautionary Tale

ProteinGym launched with a public leaderboard (proteingym.org/benchmarks) that
ranks models by average Spearman rho across all 217 DMS assays. This leaderboard
has driven adoption and visibility but has also created perverse incentives.

**ProteinGym leaderboard problems that PerturbMark should learn from:**

**(a) Aggregate ranking obscures heterogeneity.** The top model on ProteinGym's
aggregate leaderboard may be mediocre on stability but excellent on binding,
or vice versa. Users who want a stability prediction model should look at the
stability-specific ranking, not the aggregate. But the aggregate is what gets
cited in papers ("ranked #1 on ProteinGym"). PerturbMark's Tier 0-3 structure
provides a natural multi-ranking system, but the proposal does not specify how
rankings will be presented. Will there be an aggregate ranking? Per-tier
rankings? Per-MOA rankings?

**Recommendation:** Do NOT provide an aggregate ranking across tiers. Provide
per-tier rankings only. An aggregate ranking would allow methods that excel at
Tier 0 (the easiest task, where everyone performs well) to be ranked highly
even if they fail at Tier 2-3 (the most important task). The per-tier ranking
forces users to choose the ranking relevant to their use case. If an aggregate
must be provided (for simplicity), weight it inversely by tier difficulty (Tier 3
weighted highest), so that the ranking rewards methods that solve the hardest
problems.

**(b) Leaderboard gaming through test set memorization.** In the LLM benchmark
world, selective model submissions inflated Arena scores by up to 100 points
(Chatbot Arena analysis, 2025). In MoleculeNet, scaffold splits were shown to
overestimate virtual screening performance because molecules with different
scaffolds can still be structurally similar (Gorantla et al., arXiv 2024). In
ProteinGym, the risk is that models are optimized specifically for the 217
benchmark DMS assays.

For PerturbMark, the pre-training contamination risk is real: Tahoe-x1 and
SCALE are trained on Tahoe-100M itself. The proposal flags these with an
asterisk (*), which is necessary but may not be sufficient. Consider adding a
**held-out validation set** that is never released publicly. This is the CASP
model: targets are blind until after predictions are submitted. PerturbMark
could hold back one organ fold (e.g., CNS lines) as a fully blind test set,
publishing results on the other 4 folds in the main paper and reserving the
5th fold for evaluating future submissions to the leaderboard. This prevents
gaming because the test data is unknown.

**(c) Leaderboard staleness.** ProteinGym's leaderboard is a snapshot of model
performance on a fixed dataset. As new DMS assays become available, the benchmark
becomes stale. PerturbMark should plan for benchmark versioning from the start
(PerturbMark v1.0 on Tahoe-100M, v2.0 on the Tahoe/Arc/Biohub next-generation
dataset). The benchmark code should be dataset-agnostic, as scopeadv recommended.

- **Severity:** Minor
- **Addressable?** Yes. The per-tier ranking is a presentation decision, not a
  methodological one. The blind fold approach requires holding back one fold from
  publication, which is feasible but reduces the primary paper's statistical power
  by 20%. Consider this trade-off carefully. If adopted, the blind fold should be
  the fold with the most distinctive biology (e.g., haematopoietic, which uses
  suspension culture and is most biologically distinct from the other folds).

### 6. Negative Results Framing Needs Explicit Pre-Registration

In Gamma, I have planned for the possibility that conformational ensemble features
do NOT add value beyond sequence features for fitness prediction. If this happens,
the finding is publishable (and arguably more important than a positive result),
but the paper's narrative must be designed in advance to handle it.

PerturbMark faces the same structural risk: if DL does not beat linear baselines
even under calibrated metrics, the paper's title ("Resolving the Perturbation
Prediction Controversy") becomes awkward. scopeadv correctly recommended a
question-driven title ("When Does Deep Learning Help?"), which handles both
outcomes gracefully.

But beyond the title, the proposal needs explicit pre-registration of what
constitutes a negative result at each tier. Specifically:

(a) **Tier-specific null hypotheses.** Pre-register: "We test the null hypothesis
that the best DL method does not reduce WMSE by >= [threshold] relative to the
best linear baseline at each tier." This gives 4 independent tests, one per tier.
If the null is rejected at Tier 0-1 but not Tier 2-3, the result is:
"DL helps for interpolation and perturbation generalization but not for context
generalization." This is the most interesting and publishable outcome.

(b) **Pre-registered interpretation guide.** For each combination of tier-level
outcomes (DL wins at all tiers, DL wins at Tier 0-1 only, DL wins at Tier 2-3
only, DL wins nowhere), pre-register the interpretation. This prevents post-hoc
narrative construction. The interpretation guide should be filed at OSF or
Zenodo before results are computed, as the proposal already plans for pre-registration.

(c) **Analogy to Gamma:** In my project, the analogous pre-registration is: "We
test whether ensemble-derived features (RMSF, S2, contact frequency) predict DMS
fitness beyond what ESM2 embeddings predict." If no, the finding is: "Sequence
information already captures the functionally relevant conformational information."
For PerturbMark, the analogous finding would be: "Linear embeddings of drug
structure and cell identity already capture the perturbation-relevant information."
Both negative results are important because they reveal that the bottleneck is not
model complexity but data representation.

- **Severity:** Minor
- **Addressable?** Yes. Add a "Pre-Registered Interpretations" section to the
  pre-registration document. This takes 1-2 hours of writing.

### 7. The Cross-Project Synergy Blind Spot: Drug Targets Are Proteins with Dynamics

The proposal treats Delta (PerturbMark) as fully independent of Gamma+Alpha-M.
Operationally, this is correct -- the projects can execute in parallel on different
compute allocations. But scientifically, there is an unexploited connection:

**Drug perturbation responses are mediated by protein conformational changes.** When
a drug binds its target protein, it shifts the conformational ensemble of that
protein. This shift propagates through signaling pathways to produce the transcriptomic
response measured in Tahoe-100M. The conformational dynamics of the target protein
(the subject of Gamma) are therefore a causal determinant of the perturbation
response (the subject of Delta).

Evidence for this connection:
- Nussinov & Tsai (Curr Opin Struct Biol 2024) argued that "the propensities of
  the conformations can be predictors of cell function," explicitly connecting
  protein-level ensemble dynamics to cell-level phenotypes.
- Allosteric drugs work by shifting conformational ensemble distributions rather
  than blocking binding sites (Nussinov et al., JACS 2014). The cellular response
  to an allosteric vs. orthosteric drug targeting the same protein may differ
  because the induced conformational changes differ.

**Practical implication for PerturbMark:** For the 379 compounds in Tahoe-100M,
each has annotated molecular targets (from drug_metadata). For a subset of these
targets, BioEmu could generate conformational ensembles (as planned in Gamma).
A future PerturbMark extension could test whether drug-induced conformational
ensemble features (predicted by BioEmu or MLFF simulations) improve perturbation
response prediction beyond what drug structure features (Morgan fingerprints)
provide.

This is not a modification for the current PerturbMark proposal -- it is a
**future direction** that should be mentioned in the Discussion section of the
paper. It connects the two projects scientifically and signals to reviewers that
the team is thinking about the bigger picture.

**Specific recommendation:** Add a 2-paragraph "Cross-Scale Integration" subsection
to the Discussion/Future Directions section. This does not change the current
proposal's scope or timeline but creates a published connection point for Gamma
and enriches the paper's intellectual contribution.

- **Severity:** Minor
- **Addressable?** Yes. Two paragraphs in the Discussion. Zero additional
  experiments.

### 8. The "Null Benchmark" Control Is Missing

In every good experiment, there is a null control. In Gamma, my null is: "Do
random conformational features (shuffled RMSF values) predict function as well as
real features?" If so, the prediction is not using dynamics information but
exploiting spurious correlations.

PerturbMark has batch effect controls (DMSO-only, batch-shuffled null, etc.) that
serve as negative controls for data quality. But it lacks a **benchmark-level null
control**: a test of whether the benchmark itself can distinguish good methods from
bad methods.

**Specific concern:** If all 10+ methods produce nearly identical WMSE values
across all tiers (i.e., the benchmark has no resolution power), the paper reports
a null result that is uninterpretable -- was there truly no difference between
methods, or was the benchmark unable to detect one?

**Recommendation:** Before running any DL methods, compute the **benchmark
resolution power** from baselines alone. The 5 linear baselines span a range of
sophistication (no-change is the simplest; per-gene ridge with cell line features
is the most complex). If WMSE(no-change) >> WMSE(additive) >> WMSE(ridge), the
benchmark has resolution power -- it can distinguish methods of different quality.
If all 5 baselines produce similar WMSE, the benchmark may lack the dynamic range
to distinguish DL from linear, regardless of whether DL is truly better.

This is a Week 2 computation (already planned) that should be explicitly reported
as a "benchmark resolution" metric. If baseline WMSE range is less than 2x the
within-method variance (across folds and seeds), the benchmark's ability to detect
DL advantages is limited, and this should be acknowledged before interpreting DL
results.

- **Severity:** Minor
- **Addressable?** Yes. This is a reframing of existing planned computations, not
  an additional experiment. Report the baseline WMSE spread as a benchmark quality
  metric in the results.

---

## Feasibility Assessment

### Technical Feasibility

**High.** The proposed modifications add <30 GPU-hrs total (feature importance
module: ~10 GPU-hrs; elevated single-cell distributional analysis for Tier 0-1:
~20 GPU-hrs; all other modifications: post-hoc analysis only). The total compute
with modifications remains well within the 1,000-2,000 GPU-hr budget. The data
sources (Tahoe-100M, Replogle, Norman) are all CC0 or public. The methods (scanpy,
pertpy, decoupler for pathway analysis) are all open-source.

### Scientific Feasibility

**High with the feature importance caveat.** The feature importance module
(Weakness 1) is the most scientifically ambitious modification. It requires
projection of predictions into gene program space, which depends on the quality
of gene set annotations (Hallmarks, KEGG, Reactome). For MOA categories with
well-annotated target pathways (e.g., kinase inhibitors), pathway-level evaluation
will be informative. For MOA categories with poorly understood mechanisms (e.g.,
"unclear" -- 199 of 379 compounds), pathway-level evaluation may add noise.
Recommend restricting pathway-level evaluation to the ~180 compounds with
annotated MOAs in the drug_metadata.

### Timeline Feasibility

**Moderate at 10-12 weeks.** The modifications I propose add approximately 1 week
of analysis time (feature importance computation, single-cell distributional
analysis for Tier 0-1, additional stratification analyses). Integrated with
evalstat's extended timeline recommendation (10-12 weeks), this fits within the
analysis phase (Weeks 9-10). The August 15 preprint target remains feasible.

---

## Suggested Modifications

### Priority 1 (Must-Have for Publication Impact)

1. **Add a Feature Importance module** (Weakness 1). Decompose predictions into
   feature contributions at the gene program level. Test whether drug structure
   features (Morgan fingerprints), MOA features, or cell line identity features
   drive linear baseline performance. Report pathway-level WMSE alongside gene-level
   WMSE. This transforms the paper from "which model wins?" to "what information
   predicts perturbation response?"

2. **Elevate single-cell distributional evaluation** (Weakness 2) from supplementary
   to co-primary for Tier 0-1. Stratify by response modality (unimodal vs. bimodal
   conditions). Report replicate concordance as a ground-truth quality metric. This
   leverages Tahoe-100M's scale advantage over every prior dataset and tests whether
   distributional models (PerturbNet, scDFM) show differential advantage on
   heterogeneous conditions.

### Priority 2 (Recommended for Benchmark Rigor)

3. **Add perturbation effect magnitude stratification** (Weakness 3a). Stratify
   results by number of DEGs per condition and by mean absolute log2FC. This is
   zero-cost post-hoc analysis that may reveal that DL advantage is
   signal-regime-dependent.

4. **Add cell line transcriptomic distance stratification** (Weakness 3b). Report
   Tier 2-3 error as a function of distance from training set centroid. This
   disentangles the organ-based confound that evalstat identified.

5. **Test the monotonic difficulty gradient** (Weakness 4). Report pairwise Tier
   performance differences with CIs. Decompose Tier 3 difficulty into Tier 1 and
   Tier 2 components with interaction test.

6. **Implement per-tier rankings, not aggregate** (Weakness 5a). If an aggregate
   ranking must be provided, weight inversely by tier difficulty.

7. **Consider a blind fold for future leaderboard submissions** (Weakness 5b).
   Hold back one organ fold from publication and use it for blind evaluation of
   future method submissions.

### Priority 3 (Nice-to-Have for Intellectual Contribution)

8. **Pre-register tier-specific interpretations** (Weakness 6). File at OSF/Zenodo
   before results are computed.

9. **Add a Cross-Scale Integration discussion section** (Weakness 7). Connect drug
   target protein dynamics (Gamma) to perturbation response prediction (Delta).

10. **Report benchmark resolution power** (Weakness 8). Compute and report baseline
    WMSE spread as a benchmark self-diagnostic metric.

---

## Alternative Approaches

### Alternative 1: Representation-Centric Benchmark

Instead of (or alongside) the model-centric benchmark, evaluate whether specific
**data representations** predict perturbation response:
- Gene-level raw expression vs. gene program scores (NMF, PCA, or pathway-based)
- Drug representations: Morgan fingerprints vs. learned drug embeddings (ChemBERTa)
  vs. target-based representations (one-hot target genes)
- Cell line representations: transcriptomic profile vs. DepMap essentiality vs.
  mutation-based

Fix the model (e.g., ridge regression) and vary the representation. Then fix the
representation and vary the model. This 2x2 design (representation x model)
directly answers whether the bottleneck in perturbation prediction is the
representation or the model. This is the structural analog of the question in
Gamma: "Is the bottleneck the ensemble generator or the feature extractor?"

### Alternative 2: Cross-Scale Transfer Learning Test

For the subset of Tahoe-100M compounds with known protein targets that have
experimental structures in the PDB, test whether adding target protein structural
features (from PDB structures or BioEmu ensembles) to the input representation
improves perturbation response prediction. This directly connects the molecular
scale (protein dynamics) to the cellular scale (transcriptomic response) and would
be the first benchmark to test cross-scale feature integration for perturbation
prediction.

This is a future direction, not a modification to the current proposal, but it
should be mentioned in the Discussion as a connection point to Gamma.

---

## Impact on Publication Narrative

PerturbMark's current narrative is: "We resolve the DL-vs-linear controversy using
calibrated metrics and cross-context tiers on 100M cells." This is strong but
one-dimensional. The modifications I propose enrich the narrative along three axes:

1. **What information matters?** (Feature importance module) -- The paper answers
   not just "which model wins?" but "what features drive predictions?" This is the
   difference between a benchmark paper and a scientific insight paper. Nature
   Methods publishes both, but the insight paper gets more citations.

2. **Does heterogeneity contain information?** (Single-cell distributional elevation)
   -- Testing whether distributional models outperform point-prediction models on
   heterogeneous conditions connects to the broader theme of "when does cell-level
   resolution matter?" This is relevant beyond perturbation prediction -- it speaks
   to the fundamental question of when single-cell data is worth its cost.

3. **Are the barriers to prediction additive?** (Tier difficulty decomposition) --
   If Tier 3 difficulty is not the sum of Tier 1 and Tier 2 difficulties, this
   reveals non-trivial structure in cross-context generalization. This is a
   computational science insight, strengthening the case for Nature Computational
   Science as an alternative venue (per scopeadv's recommendation to prepare for
   both venues).

The enriched narrative positions PerturbMark as more than a benchmark -- it is a
systematic investigation of the information landscape of perturbation prediction.
This distinction matters for editorial impact: benchmark papers are useful, but
insight papers are celebrated.

---

## Cross-Reviewer Synthesis

Having read evalstat's and scopeadv's critiques, I note convergence on several
points and offer my perspective on the remaining disagreements:

**Convergence:**
- All three reviewers agree the 6-week timeline is unrealistic. I support the
  10-12 week timeline with August 15 target.
- All three reviewers agree WMSE/R^2_w(delta) redundancy should be resolved.
  evalstat's recommendation (WMSE + Spearman on top-k DEGs) is sound.
- All three reviewers agree the narrative should be question-driven, not
  resolution-claiming. scopeadv's title option 2 ("When Does Deep Learning
  Help?") is the best framing.

**My additional perspective:**
- evalstat's organ-based holdout confound concern (Weakness 3) is important, but
  my cell line transcriptomic distance stratification (Weakness 3b above) provides
  a more direct test: if error correlates with transcriptomic distance regardless
  of organ, then organ identity is a proxy for transcriptomic novelty, not a
  separate confound.
- scopeadv's concern about missing March 2026 models (AlphaCell, AetherCell, SCALE)
  is valid, but my feature importance module partially addresses this: even without
  the newest models, understanding what features drive prediction is arguably more
  valuable than evaluating one more model.
- evalstat's BY-FDR recommendation is statistically correct but may be overly
  conservative. My recommendation: proceed with evalstat's three-tiered correction
  (BY primary, BH sensitivity, permutation-based FDR). Report all three.

---

## References

1. Notin P, Kollasch AW, Ritter D, et al. "ProteinGym: Large-Scale Benchmarks
   for Protein Fitness Prediction and Design." NeurIPS Datasets and Benchmarks
   Track (2023). doi:10.48550/arXiv.2312.07570

2. Kryshtafovych A, Schwede T, Topf M, et al. "Critical assessment of methods
   of protein structure prediction (CASP) -- Round XIV." Proteins 89(12):
   1607--1617 (2021). doi:10.1002/prot.26237

3. Kryshtafovych A, Schwede T, Topf M, et al. "Critical assessment of methods
   of protein structure prediction (CASP) -- Round XIII." Proteins 87(12):
   1011--1020 (2019). doi:10.1002/prot.25823

4. Wu Z, Ramsundar B, Feinberg EN, et al. "MoleculeNet: a benchmark for
   molecular machine learning." Chemical Science 9: 513--530 (2018).
   doi:10.1039/C7SC02664A

5. Nussinov R, Tsai CJ. "Cell phenotypes can be predicted from propensities of
   protein conformations." Current Opinion in Structural Biology 83: 102722
   (2024). doi:10.1016/j.sbi.2023.102722

6. Nussinov R, Tsai CJ, Csermely P. "Principles of allosteric interactions in
   cell signaling." Journal of the American Chemical Society 136(51):
   17692--17701 (2014). doi:10.1021/ja510028c

7. Miller HE, Mejia GM, Leblanc FJA, et al. "Deep Learning-Based Genetic
   Perturbation Models Do Outperform Uninformative Baselines on Well-Calibrated
   Metrics." bioRxiv (2025). doi:10.1101/2025.10.20.683304

8. Ahlmann-Eltze C, Huber W, Anders S. "Deep-learning-based gene perturbation
   effect prediction does not yet outperform simple linear baselines." Nature
   Methods (2025). doi:10.1038/s41592-025-02772-6

9. Wong DR, Hill AS, Moccia R. "Simple controls exceed best deep learning
   algorithms and reveal foundation model effectiveness for predicting genetic
   perturbations." Bioinformatics 41(6): btaf317 (2025).
   doi:10.1093/bioinformatics/btaf317

10. Camillo LP, et al. "Diversity by Design: Addressing Mode Collapse Improves
    scRNA-seq Perturbation Modeling on Well-Calibrated Metrics." arXiv:2506.22641
    (2025).

11. Dibaeinia P, et al. "Evaluating Single-Cell Perturbation Response Models Is
    Far from Straightforward." bioRxiv (2026). doi:10.64898/2026.02.14.705879

12. Wei Z, Wang Y, Gao Y, et al. "Benchmarking algorithms for generalizable
    single-cell perturbation response prediction." Nature Methods 23: 451--464
    (2026). doi:10.1038/s41592-025-02980-0

13. Burkhardt DB, et al. "Decoding heterogeneous single-cell perturbation
    responses." Nature Cell Biology (2025). doi:10.1038/s41556-025-01626-9

14. Weinberger E, et al. "Modeling heterogeneity in single-cell perturbation
    states enhances detection of response eQTLs." Nature Genetics (2025).
    doi:10.1038/s41588-025-02344-6

15. Boyeau P, et al. "Deep generative modeling of sample-level heterogeneity in
    single-cell genomics." Nature Methods (2025).
    doi:10.1038/s41592-025-02808-x

16. Gorantla R, et al. "Scaffold Splits Overestimate Virtual Screening
    Performance." arXiv:2406.00873 (2024).

17. Goodhart CAE. "Problems of Monetary Management: The U.K. Experience."
    Monetary Theory and Practice. Macmillan (1984).

18. Jumper J, Evans R, Pritzel A, et al. "Highly accurate protein structure
    prediction with AlphaFold." Nature 596: 583--589 (2021).
    doi:10.1038/s41586-021-03819-2

19. Hummer AM, Blumenthal DB, Kalinina OV. "Data splitting to avoid information
    leakage with DataSAIL." Nature Communications 16: 3337 (2025).
    doi:10.1038/s41467-025-58606-8

20. Zhang S, Gandhi S, et al. "Tahoe-100M: A Giga-Scale Single-Cell
    Perturbation Atlas for Context-Dependent Gene Function and Cellular Modeling."
    bioRxiv (2025). doi:10.1101/2025.02.20.639398

21. Vinas Torne R, Wiatrak M, Piran Z, et al. "Systema: a framework for
    evaluating genetic perturbation response prediction beyond systematic
    variation." Nature Biotechnology (2025).
    doi:10.1038/s41587-025-02777-8

22. Yao J, et al. "Scalable genetic screening for regulatory circuits using
    compressed Perturb-seq." Nature Biotechnology (2024).
    doi:10.1038/s41587-023-01964-9

23. Chen H, et al. "A systematic study of key elements underlying molecular
    property prediction." Nature Communications 14: 6395 (2023).
    doi:10.1038/s41467-023-41948-6

24. Notin P. "Have We Hit the Scaling Wall for Protein Language Models?"
    Substack (2025). https://pascalnotin.substack.com/p/have-we-hit-the-scaling-wall-for

25. Weber LM, Saelens W, Cannoodt R, et al. "Essential guidelines for
    computational method benchmarking." Genome Biology 20: 125 (2019).
    doi:10.1186/s13059-019-1738-8

26. Mangul S, et al. "Systematic benchmarking of omics computational tools."
    Nature Communications 10: 1393 (2019). doi:10.1038/s41467-019-09406-4

27. Sadiq SK, et al. "Integrating Protein Dynamics into Structure-Based Drug
    Design via Full-Atom Stochastic Flows." arXiv:2503.03989 (2025).

28. Miladinovic D, Hoppe P, et al. "In silico biological discovery with large
    perturbation models." Nature Computational Science 5: 1029--1040 (2025).
    doi:10.1038/s43588-025-00870-1
