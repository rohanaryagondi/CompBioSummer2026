---
agent: aiml
round: 3
date: 2026-04-14
type: ranking
---

# Round 3 Ranking: AI/ML Methods Expert Assessment of All 6 Combined Projects

## Preamble

This ranking integrates my domain expertise in AI/ML evaluation methodology, foundation
model benchmarking, and uncertainty quantification with the cross-domain evidence
accumulated across Rounds 1 and 2. As the AI/ML Methods Expert, I evaluate each project
not just on scientific merit but specifically on: (a) whether the evaluation methodology
is sound, (b) whether the approach advances the state of the art in ways the ML community
cares about, (c) whether the gap is real and unoccupied, and (d) whether the resulting
artifact -- benchmark, model, or framework -- would durably reshape how the field
operates.

I also bring a deliberate skepticism toward projects that benchmark without innovating
(a real risk in this cohort) and a preference for projects that close feedback loops
between evaluation quality and scientific discovery.

Projects ranked: Gamma, Delta, Alpha-M, Alpha-L, Alpha-G, Beta.
R2 aggregate scores: Alpha-M 8.7, Delta 8.6, Gamma 8.5, Alpha-L 8.2, Alpha-G 8.2, Beta 8.2.

---

## Part 1: Individual Project Scorecards

### Project Gamma: Dynamics-to-Function (R2 = 8.5)

**Claim:** First systematic framework connecting BioEmu conformational ensembles to
biological function measured by deep mutational scanning (DMS). Uses ProteinGym 2.7M
variants across 217 assays as ground truth.

**AI/ML Methods Expert Assessment:**

The core scientific bet is that conformational ensemble features -- not just
static structure -- are predictive of variant functional effects. This is a
testable, falsifiable ML hypothesis. BioEmu (Jing et al., 2024; Microsoft Research)
is MIT-licensed, pip-installable, and explicitly designed to generate statistically
valid Boltzmann ensembles at H200-feasible compute cost. ProteinGym v1.3 provides
one of the cleanest held-out evaluation frameworks in all of computational biology --
217 assays with defined experimental protocols and quantitative fitness measurements.

From an ML methodology perspective, the project has several strong properties:
- The input feature space (ensemble-derived collective variables, contact frequency
  matrices, RMSF profiles, pairwise distance distributions) is genuinely novel relative
  to existing variant effect predictors (AlphaMissense, ESM-1v, EVE, GEMME) which all
  use static representations
- The evaluation framework is pre-existing and independent (ProteinGym), which
  eliminates the most common benchmark-gaming failure mode
- The null hypothesis (static structure is sufficient; dynamics adds nothing) is
  precisely defined and would itself be a publishable finding if confirmed
- The computational pipeline is end-to-end differentiable, opening the door to
  learning which ensemble features matter via gradient-based attribution

**Key risk from AI/ML perspective:** The feature engineering from raw trajectory to
functional predictor is the hard step. Naive descriptors (average RMSF, average RMSD)
are unlikely to outperform static methods. The project needs ensemble fingerprinting
methods that capture relevant conformational heterogeneity -- this is a non-trivial
ML design challenge that could consume significant iteration time.

**Competition window assessment:** BioEmu + ProteinGym combination has not been
published as of April 2026. The Microsoft BioEmu team and the Marks Lab (ProteinGym)
are the two most likely groups to attempt this combination, but neither has announced
it. The 6-18 month window estimate from Round 2 is reasonable but should be treated
as 6-9 months given the obvious nature of the combination to insiders.

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | 9 | Dynamics-informed variant effect prediction is a genuine first. The specific BioEmu+ProteinGym combination is unoccupied. |
| Scientific impact | 9 | Resolves central post-AlphaFold question: does dynamics matter for function? Affects entire field of variant effect prediction, enzyme engineering, and disease variant interpretation. |
| Computational feasibility | 8 | BioEmu is confirmed ready; 8,200 GPU-hrs is modest by HPC standards. Risk is iteration time for ensemble feature design, not raw compute. |
| Timeline feasibility | 7 | 6-9 month competition window is tight. Feature engineering and ML training cycles could push timeline past safe window. Feasible in summer 2026 if started immediately. |
| Publication potential | 9 | Clean fit for Nature Computational Science: novel framework, testable hypothesis, existing benchmark, quantitative result. Strong precedent from Notin et al. (2022) in Nature Methods. |

**Weighted Score: 8.4**

**Target venue:** Nature Computational Science (primary), Nature Methods (backup)

---

### Project Delta: PerturbMark -- Resolving the Perturbation Prediction Crisis (R2 = 8.6)

**Claim:** Definitive cross-context benchmark resolving whether deep learning models
outperform linear baselines for gene perturbation prediction, using Tahoe-100M
(429GB, CC0 license, 100M+ cells), cross-dataset generalization as primary metric,
and proper evaluation controls for the Ahlmann-Eltze vs. Lotfollahi controversy.

**AI/ML Methods Expert Assessment:**

This project sits squarely in my domain: it is fundamentally an ML evaluation
methodology paper. The controversy is real and consequential. Ahlmann-Eltze, Huber
& Anders (Nature Methods, 2025) demonstrated that "deep-learning-based gene
perturbation effect prediction does not yet outperform simple linear baselines" across
five foundation models and two deep learning models. The scPerturb and CZI responses
argue this is a metric artifact (gene-level aggregation obscures cell-level improvements)
and a data artifact (Replogle screens are poorly suited to generalization).

The AI/ML community has seen this exact dynamic before: the ImageNet/CIFAR era of
leaderboard racing where careful evaluation design mattered enormously. LiveProteinBench
(2025) showed that evaluation integrity issues can cause 28 percentage point inflation
in performance scores. The perturbation prediction field is at risk of the same pattern.

**What makes PerturbMark scientifically compelling from an ML perspective:**

1. The evaluation design must itself be a contribution. Simply running existing methods
   on Tahoe-100M without resolving the methodological dispute would not reach Nature
   Methods. The benchmark must operationalize the controversy -- define what "outperform
   linear baselines" means rigorously, control for gene essentiality, use held-out cell
   lines, held-out perturbagens, and ideally held-out experimental contexts.

2. The cross-context generalization failure is the key metric. If GEARS and scGPT are
   trained on one cell line (K562) and evaluated on another (RPE1), do they generalize?
   If trained on small molecule perturbations and evaluated on CRISPR, do representations
   transfer? These are genuine ML generalization questions with no current answers.

3. Tahoe-100M's CC0 license and scale (100M cells vs. 2.5M in Replogle) makes this
   the first dataset where saturation of single-perturbation space might be achievable,
   enabling systematic combinatorial prediction benchmarks.

**Key AI/ML concern:** Benchmark-only papers without a new method are increasingly
difficult to place at Nature Computational Science (which prefers methods + evaluation)
but fit well at Nature Methods (which has published CASP-style benchmarks). The Round 2
synthesis correctly identifies this venue tension. A strong publication strategy would
include: (a) the benchmark framework, (b) a finding that resolves the controversy
definitively, and (c) an "improved baseline" that incorporates evaluation insights --
showing what works once you measure correctly. This triad would support Nature Comp Sci.

**Compute advantage:** 1,000-2,000 GPU-hrs is extremely modest, enabling rapid
iteration on evaluation design and the ability to run the full benchmark suite
multiple times as methods improve. This is a major practical advantage for summer 2026.

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | 8 | Cross-context evaluation design is novel; the methodological controversy is real; but benchmark-only papers are less novel than new methods. |
| Scientific impact | 9 | Resolves an active field-level controversy with implications for all perturbation biology, drug discovery, and cellular reprogramming. Tahoe-100M is a paradigm-shifting dataset. |
| Computational feasibility | 10 | 1-2K GPU-hrs is trivially available. Data is CC0. Methods are all open-source. This is the most computationally feasible project in the cohort. |
| Timeline feasibility | 9 | Low compute + clear evaluation design + available data = fastest path to completion. Main risk is the time to curate cross-context splits properly (weeks not months). |
| Publication potential | 8 | Strong Nature Methods paper; reachable Nature Comp Sci if new method insight or framework component added. High community impact. Active controversy guarantees editor attention. |

**Weighted Score: 8.8**

**Target venue:** Nature Methods (primary), Nature Computational Science (if method component added)

---

### Project Alpha-M: MLFF Biomolecular Crash Test (R2 = 8.7)

**Claim:** First systematic benchmark of machine-learned force fields (MACE-OFF23,
SO3LR, AI2BMD, LiTEN-FF, ANI-2x) against experimental protein observables:
NMR order parameters (S2), SAXS radius of gyration (Rg), HDX-MS exchange rates,
and hydrogen bond populations. ~15 proteins x 3 MLFFs x 50ns trajectories.

**AI/ML Methods Expert Assessment:**

From an ML perspective, Alpha-M is not primarily an ML methods paper -- it is a
physics validation paper. The evaluation framework draws on physical observables
(NMR relaxation, SAXS curves, HDX exchange) rather than ML benchmarks or
downstream task performance. This distinction matters for venue and for how I score it.

**Strengths from ML perspective:**

1. The MLFF field is undergoing rapid development with no established ground truth
   against experimental observables. Classical benchmarks like MD17/MD22, QM9, and
   SPICE exist for small molecules and quantum chemistry, but biomolecular dynamics
   benchmarks equivalent to CASP for structure prediction are entirely absent. This
   is a genuine and important gap.

2. The benchmark design -- using NMR S2 order parameters (classical baseline:
   AMBER ff19SB achieves R2=0.62, CHARMM36m R2=0.51 from the literature) as
   a primary metric -- is rigorous because S2 values are directly calculated from
   MD trajectories via the Lipari-Szabo model-free approach and compared to
   experimentally measured backbone relaxation data from BMRB (~21,820 entries).

3. No group has published this benchmark. The compute requirement (180K-270K
   GPU-hrs) is actually a moat: few groups have both the HPC resources and the
   motivation to run extensive MD trajectories AND process them against experimental
   observables. This HPC cluster is ideal.

4. The outcome -- which MLFFs are reliable for biomolecular simulation? -- has
   immediate practical consequences for the entire MLFF user community. A benchmark
   paper that shows MACE-OFF23 underperforms on intrinsically disordered regions
   while SO3LR excels on compact globular proteins would reshape how users choose
   force fields.

**Key concerns from ML perspective:**

1. The ML novelty is limited. This is infrastructure for the physics community, not
   a new ML algorithm or framework. The ML community's contribution is building the
   benchmark; the scientific discovery is whether MLFFs are ready for biology. This
   profile fits Nature Methods better than Nature Computational Science.

2. The compute is high (180K-270K GPU-hrs), representing 2-3 months of intensive HPC
   usage. Technical failures (MLFF instabilities, trajectory crashes, incorrect
   SAXS calculation) could consume significant time. The multisim specialist's
   comfort with MD protocols is critical.

3. The MLFF field moves fast. MACE-OFF23 (2024) may be superseded by MACE-OFF25 or
   equivalent during the summer 2026 timeline, requiring re-evaluation. This is a
   real risk for benchmark papers in rapidly evolving ML fields.

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | 9 | No systematic biomolecular MLFF benchmark against experimental observables exists. This fills a structural gap that the entire field knows is missing. |
| Scientific impact | 9 | Guides the MLFF community on biomolecular applicability. Sets the evaluation standard for future MLFF papers. Critical infrastructure for the next decade of ML-enhanced simulation. |
| Computational feasibility | 6 | 180K-270K GPU-hrs is 30-50x larger than most other projects in this cohort. Technically feasible on the available HPC but requires sustained execution without major technical failures. |
| Timeline feasibility | 6 | 2-3 months of continuous HPC simulation, plus analysis, plus writing = tight for summer 2026. Any MD instability or force field crash adds weeks. |
| Publication potential | 8 | Strong Nature Methods or Nature Computational Science paper. CASP-analogous benchmarks have high impact and longevity. Risk: might need 30+ proteins to be definitive, not just 15. |

**Weighted Score: 7.6**

**Target venue:** Nature Methods (primary), Nature Computational Science (if landmark scope achieved with 30+ proteins)

---

### Project Alpha-L: LiveBioBench (R2 = 8.2)

**Claim:** First cross-modal, temporally-gated, uncertainty-quantification-aware
benchmark for biological foundation models spanning proteins, DNA/RNA, small
molecules, and single-cell data. Annually renewable. Addresses both contamination
and calibration gaps simultaneously.

**AI/ML Methods Expert Assessment:**

This is my home project and I evaluate it with both the deepest understanding and
the most rigorous skepticism. The Round 2 deep dive established:

- GPT-5 drops 28.3 percentage points on uncontaminated data vs. 2020-era proteins
  (LiveProteinBench, Rongdingyi et al., December 2025)
- Label leakage rates exceed 50% for most protein understanding tasks and 95% in
  extreme cases (arXiv:2505.20354, 2025)
- Up to 65% data leakage in standard protein interaction benchmarks (ICLR 2024
  GEM Workshop, arXiv:2404.10457)
- Zero major biological FM benchmark currently reports calibration metrics (ECE,
  MCE, Brier Score, PICP) -- a systematic blind spot across PFMBench, ProteinBench,
  LiveProteinBench, BioLLM, GUE

The scientific case is strong. The question is whether a cross-modal extension of
LiveProteinBench is sufficient for Nature Computational Science or whether it is
an engineering contribution (valuable but lower-impact).

**What elevates Alpha-L from engineering to science:**

1. The cross-modal contamination measurement itself is a scientific result. When
   GPT-5 drops 28 pp on proteins, does it also drop similarly on molecules? On
   DNA? On single-cell data? These gaps have never been measured. The answer would
   characterize how biological FMs learn differently from domain-general LLMs.

2. The UQ integration is scientifically novel. No benchmark shows whether biological
   FMs that report uncertainty estimates are actually calibrated. This is directly
   analogous to the weather forecasting calibration literature (Gneiting & Raftery,
   2007) applied to biology -- a well-framed problem with clear metrics (ECE, Brier).

3. The annually-renewable infrastructure is a durable contribution. Unlike one-shot
   benchmarks, LiveBioBench creates a community resource that compounds in value
   as new models are released. This is the Nature Methods "resource" paper model.

4. The cross-modal tasks are genuinely novel evaluation targets. Drug-target
   interaction benchmarks with temporal gating (ChEMBL document creation dates as
   temporal metadata) have never been done; variant-to-function benchmarks with
   both DNA and protein modalities evaluated together have never been done.

**Key concerns:**

1. The project is broad. Proteins + DNA + molecules + single-cell across all tasks
   is a large curation effort. The Round 2 deep dive estimated 1,550-16,000
   GPU-hrs/year depending on scope -- the range is too wide, suggesting the
   evaluation design needs tightening. A focused initial submission (proteins
   + molecules, 6 tasks per modality, annual release) is more achievable than
   the full architecture described in the deep dive.

2. Competition exists at the margins. BioMol-LLM-Bench (April 2026, arXiv:2604.03361)
   covers 26 tasks across 4 difficulty levels but is static. LiveProteinBench (December
   2025) covers proteins only. If either group extends their benchmark before submission,
   the novelty window closes. The cross-modal + temporal + UQ combination remains
   genuinely empty as of April 2026, but this could change within months.

3. Infrastructure maintenance is a hidden cost not fully accounted for in compute
   estimates. Running automated pipelines that query UniProt, ChEMBL, ClinVar, and
   CELLxGENE monthly requires DevOps-level attention. For a summer 2026 academic
   team, this is a real risk.

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | 9 | Cross-modal temporal gating is genuinely empty. UQ integration in bio FM evaluation is a first. The combination is highly novel. |
| Scientific impact | 8 | Exposes systematic overestimation across all biological FMs. Establishes calibration as a required evaluation criterion. High long-term infrastructure value. |
| Computational feasibility | 9 | 1,550-16,000 GPU-hrs (wide range but upper end feasible on HPC; lower end sufficient for initial submission). Data sources all have public APIs. |
| Timeline feasibility | 8 | Data curation and pipeline automation is time-consuming but not compute-limited. Scoped version (2 modalities, 12 tasks) achievable in 3-4 months. |
| Publication potential | 8 | Strong Nature Methods or Nature Computational Science fit. "Resource" paper model with high citation longevity. Annual updates guarantee multi-paper impact. |

**Weighted Score: 8.4**

**Target venue:** Nature Methods (primary for resource framing), Nature Computational Science (if cross-modal findings are striking enough)

---

### Project Alpha-G: End-to-End Molecular Design Benchmark (R2 = 8.2)

**Claim:** First benchmark testing the full drug design pipeline end-to-end:
target identification → hit generation → bioactivity prediction → ADMET estimation
→ synthesizability → retrospective validation against clinical outcomes. Pipeline
attrition (fraction of molecules surviving each filter) as primary metric.

**AI/ML Methods Expert Assessment:**

Alpha-G is the most ambitious benchmark in scope but also faces the most significant
ML methodology challenges. The core insight -- that current benchmarks evaluate each
pipeline stage independently, missing the compounding failures across stages -- is
correct and important. Pipeline attrition rates differing 10-100x across methods
(from the genchem Round 2 deep dive) is a striking quantitative finding that would
form a compelling opening claim.

**What is genuinely novel from ML perspective:**

1. End-to-end evaluation with stage-specific dropout metrics is analogous to the
   production ML concept of "pipeline recall" -- how many molecules that enter the
   hit generation stage still survive at the clinical candidate stage? This is a
   novel operationalization of drug discovery success that has not been applied
   systematically.

2. Retrospective validation against approved drugs and clinical failures (using
   ChEMBL, DailyMed, ClinicalTrials.gov, DrugBank) provides a ground truth that
   is independent of any model-specific evaluation, unlike self-referential
   benchmarks that evaluate against their own training objectives.

3. The "30-50 well-characterized targets" selection methodology matters enormously.
   If targets are chosen to favor specific methods, the benchmark loses credibility.
   An explicit target selection protocol (balanced across protein families, diverse
   clinical outcomes, diverse compound classes) is itself a contribution.

**Key concerns from ML perspective:**

1. Curation burden is extremely high. 30-50 targets x multi-stage evaluation x
   retrospective validation against clinical data is a multi-person-year curation
   effort. Summer 2026 is insufficient for a comprehensive version. A focused version
   (10-15 carefully curated targets) might be publishable but would face reviewer
   concerns about generalizability.

2. The "retrospective validation" claim requires data that is genuinely prospective
   relative to method training. If ChEMBL 36 is in the training data of most
   molecular generation models (which it is), then retrospective clinical validation
   is contaminated. Only approved drugs from 2024-2026 that post-date the training
   cutoffs would be truly uncontaminated -- a much smaller set.

3. The scoop risk is non-trivial. TDC (Therapeutics Data Commons) from Zitnik Lab
   already implements multi-stage drug discovery evaluation with temporal splits.
   MolScore (2024) re-implements MOSES and GuacaMol. A differentiated Alpha-G must
   explicitly show what TDC does NOT cover (end-to-end pipeline, attrition metrics,
   clinical retrospective validation). The differentiation argument needs tightening.

4. Compute range (20K-85K GPU-hrs) is wide, suggesting the scope is not yet fully
   defined. This uncertainty itself is a timeline risk.

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | 7 | End-to-end pipeline evaluation is underexplored, but TDC and MolScore partially cover this space. Pipeline attrition as a metric is the novel contribution. |
| Scientific impact | 8 | If successful, would reframe how molecular design methods are evaluated -- high impact for drug discovery AI. |
| Computational feasibility | 7 | 20K-85K GPU-hrs is feasible but the curation effort (selecting 30-50 targets with full clinical data) is the real bottleneck. |
| Timeline feasibility | 6 | Comprehensive version is infeasible in summer 2026. Scoped version (10-15 targets) is achievable but may not reach Nature Comp Sci bar. |
| Publication potential | 7 | Strong Journal of Chemical Information and Modeling or Journal of Medicinal Chemistry paper. Nature Methods possible if retrospective clinical validation is compelling. |

**Weighted Score: 7.0**

**Target venue:** Journal of Chemical Information and Modeling (primary), Nature Methods (if clinical validation is comprehensive)

---

### Project Beta: ContextVEP -- Context-Dependent Variant Effect Prediction (R2 = 8.2)

**Claim:** First framework integrating tissue-specific expression (GTEx v8), disease
context (ClinVar 3M+), variant mechanism (loss-of-function, gain-of-function,
dominant negative), and population genetic background (gnomAD v4 730K exomes) into
a unified variant effect predictor applicable to 1M+ VUS in ClinVar.

**AI/ML Methods Expert Assessment:**

Beta is the most clinically motivated project in the cohort and the one where
the AI/ML contribution is primarily integration rather than invention. AlphaMissense
(Cheng et al., Science, 2023) set the baseline for proteome-scale variant effect
prediction. AlphaGenome (Nature, January 2026) improves eQTL AUROC to 0.80 and handles
non-coding variants. DYNA and DIVA handle specific mechanism components. The gap is
the lack of unified integration.

**What is genuinely novel from ML perspective:**

1. Context conditioning in variant effect prediction is underdeveloped. Most predictors
   output a single pathogenicity score per variant regardless of tissue or disease
   context. A model that outputs different scores for the same missense variant in
   hepatocytes vs. neurons vs. cardiomyocytes would be a qualitative advance.

2. Mechanism classification (LoF vs. GoF vs. dominant negative vs. dominant positive)
   combined with population frequency (gnomAD allele frequencies) could enable the
   first principled framework for VUS reclassification in different clinical contexts
   -- directly actionable for clinical genetics.

3. The 1M+ VUS problem is quantifiable and growing. ClinVar currently contains
   approximately 3M variant entries, with a large fraction classified as VUS. A
   context-aware predictor that reclassifies a meaningful fraction would have
   immediate clinical impact.

**Key concerns from ML perspective:**

1. AlphaGenome (January 2026) substantially narrows the gap. Its eQTL AUROC of 0.80
   already incorporates some tissue context information. The differentiation from
   AlphaGenome needs to be explicit: what does ContextVEP do that AlphaGenome does
   not? If the answer is "mechanism classification + population context," that is a
   narrower contribution than the full ContextVEP vision implies.

2. Ground truth for context-dependent VEP is sparse. GTEx provides tissue-specific
   eQTL data, but for most VUS in ClinVar there is no experimental ground truth for
   context-specific effects. The evaluation framework must rely on (a) known pathogenic
   variants with well-characterized tissue specificity and (b) DMS data for specific
   proteins -- both of which are limited in scope.

3. The 500-1,000 GPU-hrs estimate is very low, which raises questions about the
   ambition of the model architecture. A simple integration framework (logistic
   regression on concatenated features from AlphaMissense + GTEx eQTL scores + gnomAD
   frequencies) could be built in days. But a genuinely novel context-aware model
   (transformer with tissue/disease conditioning, multi-task training, etc.) would
   require substantially more compute and development time.

4. The combined reggeno + transmed framing is correct but requires cross-domain
   coordination that adds execution risk. A clean separation of responsibilities
   (reggeno handles non-coding variants + regulatory context; transmed handles coding
   variants + clinical integration) would reduce collision risk.

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | 7 | Context-dependent VEP is genuinely open, but AlphaGenome (Jan 2026) and AlphaMissense partly occupy the space. Integration novelty is meaningful but not groundbreaking. |
| Scientific impact | 8 | 1M+ VUS is a real clinical problem. Context-aware reclassification would have immediate utility in clinical genetics. High translational impact even if basic science novelty is moderate. |
| Computational feasibility | 10 | 500-1,000 GPU-hrs is trivially feasible. All data sources are public (GTEx, ClinVar, gnomAD). No technical barriers. |
| Timeline feasibility | 9 | Low compute + available data + clear evaluation targets (ClinVar VUS, known tissue-specific phenotypes) = fast execution. |
| Publication potential | 7 | Strong Nature Genetics or American Journal of Human Genetics paper. Nature Computational Science requires stronger methodological novelty beyond integration. |

**Weighted Score: 8.2**

**Target venue:** Nature Genetics (primary), Nature Computational Science (if context-conditioning architecture is genuinely novel)

---

## Part 2: Summary Comparison Table

| Project | Short Name | Novelty | Impact | Comp. Feasibility | Timeline | Pub. Potential | **Weighted Avg** |
|---------|-----------|---------|--------|-------------------|----------|----------------|------------------|
| Delta | PerturbMark | 8 | 9 | 10 | 9 | 8 | **8.8** |
| Gamma | Dynamics-to-Function | 9 | 9 | 8 | 7 | 9 | **8.4** |
| Alpha-L | LiveBioBench | 9 | 8 | 9 | 8 | 8 | **8.4** |
| Beta | ContextVEP | 7 | 8 | 10 | 9 | 7 | **8.2** |
| Alpha-M | MLFF Crash Test | 9 | 9 | 6 | 6 | 8 | **7.6** |
| Alpha-G | Mol Design Bench | 7 | 8 | 7 | 6 | 7 | **7.0** |

*Weights: Novelty x 0.25, Impact x 0.25, Comp. Feasibility x 0.20, Timeline x 0.15, Pub. Potential x 0.15*

Note: My weights are chosen to reflect the specific constraints of this system:
Summer 2026 timeline requires feasibility weighting; Novelty and Impact define the
Nature Comp Sci bar; Timeline feasibility is a hard constraint given the deadline.

---

## Part 3: Final Rankings with Justification

### Rank 1: Project Delta (PerturbMark) -- Score 8.8

**Why Delta wins in my assessment:**

Delta is the project where evaluation methodology is itself the contribution, where
the computational constraints are trivially met, and where the field most urgently
needs a definitive answer. The Ahlmann-Eltze vs. Lotfollahi controversy in Nature
Methods is unresolved as of April 2026. Tahoe-100M (100M cells, CC0, released 2025)
is a dataset of unprecedented scale that has not been used to resolve this debate.
The cross-context evaluation design -- training on one cell line or perturbation type,
evaluating on held-out contexts -- is a methodology innovation that directly answers
the question the field is asking.

From my AI/ML perspective, the most impactful papers in computational biology are
often the ones that show the field has been measuring itself wrong and provide the
right measurement. Ahlmann-Eltze et al. (2025) showed DL doesn't outperform linear
baselines -- but this result is contested on methodological grounds. A PerturbMark
paper that definitively resolves this with proper controls, larger data, and
cross-context generalization would be immediately cited by everyone in the field.

The practical arguments are also overwhelming: fastest to execute, lowest compute
risk, clearest publication target (Nature Methods), highest probability of completion
in summer 2026.

**The only concern:** Delta may be "merely" a benchmark paper. To reach Nature
Computational Science instead of Nature Methods, the evaluation framework must yield
a genuinely new scientific insight -- not just "method X beats method Y" but "here
is why linear baselines are hard to beat, and here is the architectural principle
that would help." If the benchmark produces this insight, Nature Comp Sci is reachable.

---

### Rank 2 (tie): Projects Gamma and Alpha-L -- Score 8.4

**Why Gamma ties for second:**

Gamma has the highest individual scores for novelty and publication potential, and
addresses the single most important post-AlphaFold question: does conformational
dynamics matter for biological function? The tools are genuinely ready (BioEmu
released 2024, MIT license). The evaluation framework is pre-existing (ProteinGym v1.3).
The hypothesis is clear, falsifiable, and interesting regardless of outcome.

Gamma scores below Delta primarily due to timeline risk: the 6-9 month competition
window (shortened from the original 6-18 month estimate given the obvious nature of
the combination) means this project has the highest probability of being scooped before
submission. If Microsoft's BioEmu team or the Marks Lab simultaneously publish the same
combination, the project's value collapses. This is the key risk that pushes Gamma
below Delta in my final ranking.

**Why Alpha-L ties for second:**

Alpha-L is the most durable contribution in the cohort: an annually renewable
infrastructure asset that compounds in value as biological foundation models proliferate.
The cross-modal + temporal + UQ combination is genuinely empty as of April 2026. The
28.3 percentage point contamination finding from LiveProteinBench (Rongdingyi et al.,
December 2025) is a specific, quantified result that motivates the project.

Alpha-L scores below Delta primarily because the breadth makes scoping difficult.
A focused 2-modality version (proteins + molecules, 12 tasks, annual updates) would
be feasible in summer 2026 and highly publishable. The full 4-modality vision with UQ
integration is a 2-year project. The summer 2026 team should commit to the scoped version
and be explicit about future expansion.

Alpha-L also has the clearest AI/ML methodology contribution: the combination of temporal
gating + calibration metrics is a methodological innovation that would redefine how
biological FMs are evaluated. This is closer to my core domain than the other projects.

---

### Rank 4: Project Beta (ContextVEP) -- Score 8.2

**Why Beta is fourth:**

Beta has the highest feasibility scores (compute and timeline) of any project in the
cohort and addresses a real clinical need. But from an AI/ML perspective, the
contribution is integration rather than invention. AlphaGenome (January 2026) already
provides tissue-context-aware non-coding variant effects with AUROC 0.80. The remaining
gap -- combining coding + non-coding context with mechanism and population background --
is real but narrower than it appeared in Round 1.

Beta belongs in the cohort because it is the most translatable project: a context-aware
VUS reclassification framework would be immediately adopted by clinical genetics labs.
The clinical impact is higher than any other project here. But clinical impact alone does
not reach Nature Computational Science; the AI/ML novelty needs strengthening. The
context-conditioning architecture (how do you train a model to output different scores
for the same variant in different tissue/disease contexts?) is the key question, and the
answer is not yet specified in the project description.

---

### Rank 5: Project Alpha-M (MLFF Crash Test) -- Score 7.6

**Why Alpha-M is fifth despite highest R2 score:**

This is my most significant departure from the Round 2 consensus, where Alpha-M ranked
first at 8.7. My re-ranking reflects the AI/ML methodology perspective:

Alpha-M is primarily a physics validation paper. The ML contribution is: build a
benchmark, run simulations, measure against experimental observables. This is important
and unoccupied, but the ML novelty is limited to benchmark design, not algorithmic
innovation. The timeline feasibility (6) and computational feasibility (6) scores
reflect a genuine constraint: 180K-270K GPU-hrs, 2-3 months of continuous simulation,
and significant risk of technical failures (MLFF instabilities, trajectory crashes,
incorrect SAXS processing) make this the hardest project to execute in summer 2026.

I would raise Alpha-M's ranking if the project included an ML novelty component: for
example, using the experimental validation discrepancies to train a correction model
for MLFF observables, or developing an active learning framework that identifies which
proteins are most informative for MLFF calibration. As a pure benchmark project,
Alpha-M's compute requirements make it a higher-risk investment relative to Delta,
Gamma, or Alpha-L.

---

### Rank 6: Project Alpha-G (Molecular Design Benchmark) -- Score 7.0

**Why Alpha-G is last:**

Alpha-G has the right vision -- end-to-end pipeline evaluation is genuinely needed in
drug discovery -- but faces the most significant practical challenges of any project:

1. Curation burden: 30-50 targets with full clinical histories, ChEMBL activity data,
   ADMET measurements, synthesis feasibility assessments, and retrospective clinical
   outcomes is a 12-18 month curation effort, not 3-4 months.

2. Contamination problem: Most molecular generation models trained on ChEMBL 36 means
   retrospective validation against pre-2024 clinical data is contaminated. The
   genuinely prospective evaluation set (drugs approved 2024-2026) is too small for
   statistical power.

3. TDC differentiation: Therapeutics Data Commons already provides multi-stage drug
   discovery evaluation. The differentiation argument needs to be sharper, and current
   project description does not fully make it.

4. Venue fit: The natural venue (JCIM, J. Med. Chem.) has lower impact than the Nature
   family journals targeted by other projects. Reaching Nature Methods requires clinical
   retrospective validation that is technically difficult to achieve in summer 2026.

Alpha-G should remain as a future cohort project with more time and team resources.
It is not infeasible -- it is infeasible in the summer 2026 timeline with a small team.

---

## Part 4: Combination Strategies

### Best Combination: Delta + Alpha-L (PerturbMark + LiveBioBench)

**Rationale:** Both projects are fundamentally about rigorous evaluation methodology.
Both expose systematic failures in how biological AI systems are currently assessed.
Delta exposes the failure to properly evaluate perturbation prediction models across
contexts. Alpha-L exposes the contamination and calibration failures across all
biological foundation models. Together, they form a coherent "evaluation integrity
manifesto" for computational biology AI.

**Combined paper structure:**
- **Unifying claim:** Biological foundation models are systematically overestimated
  due to (a) contaminated evaluation data (Alpha-L contamination findings), (b) metric
  artifacts that favor DL methods (Delta controversy), and (c) complete absence of
  calibration measurement (Alpha-L UQ findings).
- **Empirical contributions:** (1) LiveBioBench infrastructure demonstrating cross-modal
  contamination at scale; (2) PerturbMark framework resolving the DL vs. linear baseline
  controversy with proper cross-context controls; (3) first cross-domain calibration
  metrics showing which biological FMs are well-calibrated and which are not.
- **Unified finding:** The field's FM performance estimates are inflated by 15-30%
  across all modalities, and no FM currently provides calibrated uncertainty estimates
  that would enable reliable downstream use.
- **Target venue:** Nature Computational Science ("The Evaluation Crisis in Biological
  Foundation Models"). Strong precedent from Ahlmann-Eltze et al. (2025) showing that
  evaluation methodology papers can reach Nature Methods with high impact.

**Practical synergy:** Delta (1-2K GPU-hrs) and scoped Alpha-L (1.5-5K GPU-hrs) together
require only ~6,500 GPU-hrs maximum -- the lowest compute footprint of any combined
project, enabling rapid iteration and early submission in summer 2026.

**Team division:** Delta (perturbation context generalization analysis) can be driven by
sysnet with aiml support on evaluation design. Alpha-L (cross-modal infrastructure and
UQ evaluation) is primarily aiml. The projects have natural division of labor.

### Alternative Combination: Gamma + Alpha-L (Dynamics-to-Function + LiveBioBench)

**Rationale:** Both projects involve sophisticated evaluation of biological foundation
models (BioEmu for Gamma, all biological FMs for Alpha-L). Alpha-L's UQ framework
could be applied to BioEmu ensemble outputs -- are BioEmu confidence scores calibrated?
Does BioEmu's self-assessed ensemble quality correlate with DMS functional accuracy?
These questions would extend Gamma's evaluation to include calibration as a primary
metric.

**Combined paper structure:**
- **Unifying claim:** Evaluation of protein dynamics models requires both functional
  accuracy (Gamma's DMS approach) and calibration (Alpha-L's UQ framework).
- **Practical advantage:** Alpha-L provides the calibration methodology; Gamma provides
  the functional validation. The combination is tighter than Delta + Alpha-L.
- **Risk:** Both projects already have strong standalone stories. Combining them may
  dilute each narrative rather than strengthen them. I recommend evaluating this
  combination only if the teams for both projects are co-located and can work in parallel.

### Projects Best Left Standalone:

- **Alpha-M:** The physics validation narrative is self-contained and should not be
  diluted by combining with ML-focused projects. Best as a standalone Nature Methods paper.
- **Beta:** The clinical genetics framing is distinct from the ML methodology narrative
  of other projects. Should be submitted to Nature Genetics or similar clinical venue
  as a standalone contribution.

---

## Part 5: Venue Targeting Summary

| Project | Recommended Venue | Backup Venue | Key Condition |
|---------|------------------|--------------|---------------|
| Delta | Nature Methods | Nature Comp Sci | Add method insight beyond benchmark |
| Gamma | Nature Comp Sci | Nature Methods | Publish before BioEmu/Marks Lab |
| Alpha-L | Nature Methods | Nature Comp Sci | Cross-modal UQ findings must be striking |
| Beta | Nature Genetics | Nature Comp Sci | Context-conditioning architecture must be novel |
| Alpha-M | Nature Methods | Nature Comp Sci | Need 30+ proteins for definitive scope |
| Alpha-G | J. Chem. Inf. Model. | Nature Methods | Requires 18+ months, not 3 |
| Delta + Alpha-L | Nature Comp Sci | Nature Methods | Combined evaluation crisis narrative |

---

## Part 6: AI/ML Expert Summary Recommendation

**Top Pick: Project Delta (PerturbMark)**

On pure execution risk vs. impact, Delta is the project this cohort should prioritize
if forced to choose one. The computation is trivially feasible (1-2K GPU-hrs), the
controversy is real and ongoing, the data (Tahoe-100M) is unprecedented in scale, and
the community impact of resolving the DL vs. linear baseline debate would be immediate
and cited extensively. The venue (Nature Methods) is well-matched to a benchmark paper,
and the evaluation framework extends naturally to future work.

**Best Investment for Long-Term Impact: Alpha-L (LiveBioBench)**

If the team can sustain the infrastructure commitment, Alpha-L is the project with the
highest long-term citation trajectory. An annually renewable benchmark for biological
foundation models would be cited every time a new FM is introduced, evaluated, or
deployed. The contamination finding (28 pp drop) is a compelling finding that will
generate sustained community attention.

**Highest Scientific Ambition: Gamma (Dynamics-to-Function)**

If the competition window can be monitored and the team can move quickly, Gamma is the
project most likely to produce a paper that the broader biology community (not just
the ML community) cares about. The question "does protein dynamics matter for function?"
is one that experimental biologists, structural biologists, and computational chemists
all have a stake in. A clear answer -- either direction -- would be widely cited.

**Best Strategic Combination: Delta + Alpha-L**

The lowest-compute, highest-feasibility combination that addresses a coherent scientific
theme (evaluation integrity) with a clear Nature Computational Science narrative ("The
Evaluation Crisis in Biological Foundation Models"). Recommended as the primary
submission strategy if the cohort architect builds Cohort 2 around evaluation methodology.

---

## References

1. Rongdingyi et al. (2025). "LiveProteinBench: A Dynamic Benchmark for Protein-Related
   LLMs Using Continuously Evolving Data." arXiv:2512.22257.
2. Ahlmann-Eltze C, Huber W, Anders S. (2025). "Deep-learning-based gene perturbation
   effect prediction does not yet outperform simple linear baselines." Nature Methods.
3. Hermann E, Fiedler W, et al. (2024). "Beware of Data Leakage from Protein LLM
   Pretraining." ICLR 2024 MLCB Workshop.
4. Jing B, Berber E, et al. (2024). "BioEmu: Biomolecular Emulation at Scale." Microsoft
   Research / MIT. arXiv.
5. Notin P, Dias M, et al. (2022). "Tranception: Protein Fitness Prediction with
   Autoregressive Transformers." Nature Methods.
6. Cheng J, Novati G, et al. (2023). "Accurate proteome-wide missense variant effect
   prediction with AlphaMissense." Science, 381(6664).
7. Greenman RL, Amini AP, Yang KK. (2025). "Benchmarking uncertainty quantification for
   protein engineering." PLOS Computational Biology, January 2025.
8. "ImmUQBench: A Unified Uncertainty Quantification Benchmark for Protein Immunogenicity
   Prediction." Oxford Open Immunology, NeurIPS 2025.
9. "Revealing data leakage in protein interaction benchmarks." ICLR 2024 GEM Workshop.
   arXiv:2404.10457.
10. AlphaGenome (Google DeepMind). (2026). "Accurate prediction of regulatory effects of
    genetic variants at base-pair resolution." Nature, January 2026.
11. "PFMBench: A Comprehensive Benchmark for Protein Foundation Models." arXiv:2506.14796.
    June 2025.
12. "BioMol-LLM-Bench: Cross-Modal Evaluation of LLMs for Biomolecular Tasks."
    arXiv:2604.03361. April 2026.
13. "Rethinking Text-based Protein Understanding." arXiv:2505.20354. 2025.
14. "Flaw in protein language models for protein-protein interaction inference."
    Nature Machine Intelligence, 2025.
15. Gneiting T, Raftery AE. (2007). "Strictly proper scoring rules, prediction, and
    estimation." Journal of the American Statistical Association, 102(477), 359-378.
16. Zitnik M, et al. (2021). "Therapeutics Data Commons: Machine Learning Datasets and
    Tasks for Drug Discovery and Development." NeurIPS 2021 Datasets and Benchmarks Track.
17. Tahoe-100M dataset. (2025). Tahoe Genomics. CC0 license. 100M+ single-cell
    transcriptome profiles.
18. "Zero-shot evaluation of single-cell foundation models reveals limitations."
    Genome Biology, 2025. Microsoft Research.
19. MACE-OFF23 force field. Kovacs DP, et al. (2023). "MACE-OFF23: Transferable Machine
    Learning Force Fields for Organic Molecules." arXiv:2312.15211.
20. ProteinGym v1.3. Notin P, et al. (2023). "ProteinGym: Large-Scale Benchmarks for
    Protein Fitness Prediction and Design." NeurIPS 2023 Datasets and Benchmarks Track.
