---
agent: Multi-Scale Simulation Expert (multisim)
round: 3
date: 2026-04-14
type: research-note
topic: Cross-specialist ranking of 6 candidate projects for final gap selection
---

# Round 3 Ranking: Multi-Scale Simulation Expert Assessment of All 6 Projects

## Agent

Multi-Scale Simulation Expert (multisim) -- specializing in molecular dynamics, ML force
fields, free energy calculations, and multi-scale simulation methodology. Brings a
physics-first perspective to evaluate computational rigor, data quality, and the
likelihood that any given project will produce robust, reproducible science.

---

## Summary

This document ranks all six candidate projects from the combined Round 1/Round 2
analysis: Gamma (Dynamics-to-Function), Delta (PerturbMark), Alpha-M (MLFF Biomolecular
Crash Test), Alpha-L (LiveBioBench), Alpha-G (Molecular Design Benchmark), and Beta
(ContextVEP). Rankings are based on five criteria: Novelty, Scientific Impact,
Computational Feasibility, Timeline Feasibility, and Publication Potential (1-10 each).

From a multi-scale simulation standpoint, the central question is: which project makes
the most durable scientific contribution by being grounded in rigorous computational
methodology, has the clearest path through summer 2026, and would withstand the scrutiny
of reviewers at Nature Computational Science or Nature Methods? My top recommendation
is **Alpha-M (MLFF Biomolecular Crash Test)** as the highest-novelty, highest-community-
impact contribution with a genuinely empty competitive space. My best combination
recommendation is **Alpha-M + Gamma** as a unified "ensemble quality + function" axis.

---

## Research Questions Guiding This Round

1. Has the competitive landscape for any project shifted materially between Round 2
   (April 2026) and the present, based on new preprints or papers?
2. For benchmark/evaluation projects (Delta, Alpha-M, Alpha-L, Alpha-G), has anyone
   published the benchmark in the intervening period?
3. For the physics-intensive project (Alpha-M), are the compute estimates still valid
   and is the toolchain still complete?
4. Which project would an expert reviewer at Nature Computational Science be most
   excited about -- and most skeptical of?
5. Which projects could be combined without losing coherence?

---

## Methods and Sources

### Web Searches Conducted (April 2026)

- "MLFF machine learning force field benchmark NMR SAXS experimental validation
  protein 2025 2026" -- confirmed no systematic MLFF-vs-experimental-observables
  benchmark exists as of April 2026
- "MACE-OFF23 SO3LR AI2BMD protein simulation benchmark experimental observables 2025
  2026" -- confirmed tools all remain open-source and protein-ready
- "biomolecular crash test OR MLFF protein benchmark experimental NMR order parameters
  SAXS 2026 preprint" -- nearest match was a May 2025 preprint using MLFF
  embeddings to predict NMR chemical shifts (not a simulation-vs-experiment benchmark)
- "BioEmu conformational ensemble DMS fitness prediction ProteinGym dynamics function
  2026 preprint" -- confirmed no paper has combined BioEmu ensembles with ProteinGym
  DMS prediction as of April 2026
- "perturbation prediction benchmark single cell Tahoe-100M cross-context 2026" --
  confirmed Tahoe-100M is public (CC0), and a new 3B parameter Tahoe-x1 model appeared
  October 2025, but no cross-context benchmark resolving the DL-vs-linear debate exists
- "AlphaCell bioRxiv March 2026 perturbation prediction zero-shot cellular context
  world model" -- AlphaCell (March 5, 2026 preprint) is a significant new entrant in
  the Delta space; important for competition assessment
- "PerturbMark scPerturBench definitive cross-context perturbation prediction benchmark
  2026" -- scPerturBench published in Nature Methods (February 2026), but covers 27
  methods x 29 datasets without the Tahoe-100M data and without resolving the
  DL-vs-linear metric controversy
- "LiveBioBench biological foundation model benchmark temporal contamination UQ 2026"
  -- LiveProteinBench confirmed as protein-only with no cross-modal equivalent
- "end-to-end drug design evaluation benchmark pipeline ADMET synthesizability
  retrospective validation 2025 2026" -- confirmed gap still open; MolGenBench
  (November 2025) is the closest attempt but still misses ADMET/synthesizability/
  retrospective components
- "ContextVEP context-dependent variant effect prediction VUS tissue GOF LOF 2026"
  -- confirmed no unified context-aware VEP tool exists; AlphaMissense remains the
  state of the art for coding VUS
- "Nature Computational Science benchmark paper 2025 evaluation methodology machine
  learning biology" -- confirmed benchmark papers do land in NatCompSci (Scouter 2026,
  EMO 2025) but Nature Methods is a stronger primary target for benchmark papers

### Key Literature Consulted

- Round 2 deep-dive reports: multisim, protdyn, sysnet, aiml, genchem, reggeno, transmed
- Round 2 synthesis (orch)
- Ahlmann-Eltze et al., Nature Methods 2025 (perturbation DL-vs-linear)
- Wei et al., Nature Methods 2026 (scPerturBench: 27 methods, 29 datasets)
- AlphaCell preprint, bioRxiv March 5, 2026
- Tahoe-x1 preprint, bioRxiv October 23, 2025
- MACE-OFF23, JACS 2025; SO3LR, JACS 2026; AI2BMD, Nature 2024
- Structure-Based Experimental Datasets review (PMC12823150, 2025)
- LiveProteinBench (arXiv 2512.22257, December 2025)
- MolGenBench preprint, bioRxiv November 2025
- popEVE, Nature Genetics December 2025
- AlphaGenome, Nature January 2026
- BioEmu assessment papers (Aryal et al., IJMS 2025; BioEmu augmented MD, January 2026)

---

## Findings: Current State of Each Project (Pre-Ranking Update)

### Alpha-M (MLFF Biomolecular Crash Test)

**Competition status: STILL CLEAR.** The May 2025 preprint "Representing local protein
environments with machine learning force fields" (arXiv 2505.23354) uses MLFF embeddings
as input features to a chemical shift predictor -- this is categorically different from
running actual MLFF-based MD simulations and comparing the resulting trajectories to
experimental NMR S2 order parameters, SAXS profiles, and HDX-MS protection factors.
The TEA Challenge 2023 (published Chemical Science, 2025) benchmarked MLFFs on peptide
systems using DFT reference, not experimental observables, and on materials/surfaces.
The Structure-Based Experimental Datasets review (PMC12823150, 2025) explicitly states
these datasets "could be used to benchmark the increasing number of machine learning
models" but acknowledges this has not been done.

**Verdict:** As of April 2026, no group has run systematic MD with multiple open-source
MLFFs and compared resulting trajectories to the full suite of experimental biophysical
observables. The gap is intact and the competitive moat is deep.

**Toolchain update:** MACE-OFF23 (JACS 2025), SO3LR (JACS 2026, 2.6 ns/day at 10K
atoms on H100), AI2BMD (Nature 2024) all confirmed open-source and protein-ready.
OpenMM-ML plugin supports MACE-OFF23 and ANI-2x for standardized MD runs. No new
entrant has closed any part of the MLFF-vs-NMR/SAXS gap.

### Gamma (Dynamics-to-Function)

**Competition status: WINDOW NARROWING BUT STILL OPEN.** The January 2026 BioEmu
augmented MD preprint (bioRxiv 2026.01.07.698041) demonstrates combining BioEmu
ensembles with Markov State Models for kinase conformational dynamics and mutation-
induced population shifts -- the closest work yet -- but critically, it does not connect
BioEmu ensemble features to ProteinGym DMS fitness scores. The Aryal et al. (IJMS 2025)
assessment found BioEmu "fails to predict mutation-induced shifts in conformational
distribution" and "cannot differentiate driver from passenger mutations" -- highlighting
the precise gap Gamma would fill (the ensemble-to-function mapping layer). No paper
has connected BioEmu to DMS fitness prediction on ProteinGym.

**Verdict:** Window is 6-12 months. The BioEmu+MSM preprint makes the combination more
visible to competitors, but the specific DMS fitness angle remains unclaimed.

### Delta (PerturbMark)

**Competition status: SIGNIFICANTLY MORE CROWDED.** This is the most important update
since Round 2. Three critical new developments:

1. **scPerturBench** (Wei et al., Nature Methods, February 2026, vol. 23, pp. 451-464):
   27 methods, 29 datasets, 6 metrics. This is a major benchmark paper published in
   the exact target venue. However, it does NOT use Tahoe-100M, does NOT resolve the
   DL-vs-linear metric controversy (it uses static metrics without the weighted/ranked
   variants proposed by the "Diversity by Design" paper), and does NOT include cross-
   context (zero-shot cell line) evaluation at the scale Tahoe-100M enables.

2. **AlphaCell** (bioRxiv March 5, 2026): A fully generative "Virtual Cell World Model"
   achieving zero-shot prediction of cellular dynamics in unseen contexts. Trained on
   220M single cells (including Tahoe-100M). Makes strong claims about cross-context
   generalization. If AlphaCell's claims hold up, they partially answer the question
   PerturbMark would address.

3. **Tahoe-x1** (bioRxiv October 2025): 3B parameter perturbation-trained model with
   state-of-the-art on four disease-relevant benchmarks, trained on Tahoe-100M.

**Verdict:** The Delta competitive space has shifted materially. A benchmark paper
entering this space now faces: (a) scPerturBench already published in Nature Methods,
(b) AlphaCell claiming to solve cross-context prediction, (c) Tahoe-x1 claiming SOTA.
Delta still has value -- none of these papers use standardized metrics to settle the
DL-vs-linear debate with proper controls -- but the competitive moat has eroded since R2.

### Alpha-L (LiveBioBench)

**Competition status: STILL OPEN FOR CROSS-MODAL.** LiveProteinBench (arXiv December
2025) established temporal gating for proteins only. It covers 12 tasks, uses proteins
validated after January 2025, and addresses LLM evaluation -- but is protein-only and
does not include DNA, molecules, or single-cell foundation models. BioMol-LLM-Bench
(April 2026) is the closest cross-modal benchmark but is static (no temporal gating)
and focuses on general LLMs, not specialist biological FMs. No cross-modal, temporally-
gated, UQ-aware benchmark for specialist biological FMs exists.

**Verdict:** Gap confirmed open for the cross-modal + temporal + UQ intersection.
The primary precedent (LiveProteinBench) proves the approach is publishable.

### Alpha-G (Molecular Design Benchmark)

**Competition status: STILL OPEN BUT CURATION BURDEN IS THE BOTTLENECK.** MolGenBench
(November 2025) is the closest attempt with 120 protein targets and 220K actives, but
it still lacks ADMET, synthesizability, and retrospective outcome validation -- the
three components that would make it a true end-to-end pipeline benchmark. Polaris Hub
is ADMET-focused but not generation-focused. The "affinity-validity trade-off" paper
(January 2026) adds evidence of the gap but doesn't close it. The fundamental challenge
Alpha-G faces is the massive manual curation effort required to build a retrospective
drug progression dataset across 30-50 targets, which is a data-acquisition bottleneck,
not a computational bottleneck.

**Verdict:** Gap still open. The curation challenge is real and time-consuming.

### Beta (ContextVEP)

**Competition status: STILL OPEN BUT NARROWER.** AlphaGenome (Nature, January 2026)
improved non-coding eQTL prediction substantially (AUROC 0.80 vs Borzoi's 0.75). popEVE
(Nature Genetics, December 2025) improved evolutionary scoring for rare variants but
without tissue or disease context. IMPPROVE (Nature Communications, 2025) uses GTEx
single-cell data for tissue conditioning but is Random Forest-based and limited to HPO
phenotypes. The full integration (tissue expression + disease context + GOF/LOF
mechanism + penetrance + proteome-wide scale) remains unclaimed. The compute burden
is very low (500-1000 GPU-hrs), making this highly feasible from a resource perspective.

**Verdict:** Gap persists in the integration dimension. The narrowing since Round 1
(AlphaMissense for coding, AlphaGenome for non-coding) means ContextVEP must be very
clearly differentiated from these tools to make a compelling Nature Comp Sci case.

---

## Detailed Rankings

### Project 1: Alpha-M -- MLFF Biomolecular Crash Test

**R2 Score: 8.7 | Compute: 180K-270K GPU-hrs | Target Venue: Nature Computational Science**

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | **9** | No systematic benchmark of multiple MLFFs against experimental protein observables exists as of April 2026. The analogous UniFFBench for materials science (finding a "reality gap" between computational and experimental benchmarks) demonstrates the precedent and the expected impact. The MLFF community benchmarks exclusively against DFT-computed references. Moving to NMR S2 order parameters, 3J-couplings, SAXS I(q) profiles, and HDX-MS protection factors is a categorical novelty. |
| Scientific Impact | **9** | Directly answers the question that every experimental biophysicist asks when confronted with an MLFF paper: "Should I trust this for my protein?" The classical FF community spent 30+ years building this validation infrastructure. If MLFFs fail (e.g., wrong S2 order parameters, bad J-couplings), the field must course-correct. If they pass, it unlocks a wave of biophysical simulation studies. Either result is high-impact. The result is immediately actionable by the ~10 major MLFF groups and by all experimental groups choosing between AMBER, CHARMM, and new MLFFs. |
| Computational Feasibility | **7** | Requires 180K-270K GPU-hrs total: 15 proteins x 6 MLFFs x 50ns each = 4,500 production runs at ~40 GPU-hrs each. This is within the HPC budget (H200s, B200s) but requires careful scheduling. The main technical risk is stability: some MLFFs (SO3LR, LiTEN-FF) have been validated on crambin but not on more challenging targets (IDPs, membrane proteins). NMR back-calculation (SPARTA+, SHIFTS, SPyCi-PDB) is well-established. SAXS back-calculation (FOXS, Pepsi-SAXS) is routine. The main unknown is whether all 6 MLFFs will run stably for 50ns on all 15 proteins without trajectory divergence. |
| Timeline Feasibility | **7** | The 2-3 month execution window is tight but achievable given sufficient parallelism. The critical path is: (1) protein selection and system prep (2 weeks), (2) equilibration and production MD for all MLFF/protein pairs (6-8 weeks at scale on HPC), (3) back-calculation of observables and analysis (2 weeks), (4) writing (3 weeks). Total: ~14 weeks from start, fitting a summer 2026 timeline if started immediately. The risk is debugging: if one MLFF is unstable on several proteins, that adds debugging time. |
| Publication Potential | **9** | Nature Computational Science is the ideal venue. The paper makes a clear, falsifiable claim ("MLFF X performs Y relative to classical FF Z on experimental observables at proteins A-O"), presents resource-intensive but well-controlled experiments, fills a gap explicitly acknowledged in the literature (PMC12823150, 2025), and guides an entire community. Comparable precedent: Lindorff-Larsen et al. (Science, 2011) on FF comparison against NMR data had enormous and lasting impact. Reviewers will likely demand (a) more proteins, (b) more observables, or (c) statistical treatment of uncertainty -- all manageable. |

**Alpha-M Total: 41/50 (Weighted Mean: 8.2)**

Note: The R2 score of 8.7 reflected cross-cohort weighting. The per-criterion mean of
8.2 reflects my honest assessment that the timeline and compute feasibility (both scored
7) are genuine constraints that must be acknowledged. This is still the top-ranked
project overall once uncertainty is factored in, because the novelty and impact scores
of 9 are the highest of any project.

---

### Project 2: Gamma -- Dynamics-to-Function

**R2 Score: 8.5 | Compute: ~8,200 GPU-hrs | Target Venue: Nature Computational Science**

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | **8** | BioEmu (Science, 2025) is now 9+ months old and well-known. No paper yet uses BioEmu ensembles as features for DMS fitness prediction, which is the core novel claim. Related work (ESMDance/SeqDance, Ozkan DCIasym GNN, QDPR) uses implicit or computed dynamics features rather than explicit ensembles from generative models. However, the novelty is a "method combination" -- a genuinely novel framework, but not a fundamentally new concept (dynamics matters for function is established; the step is the explicit BioEmu → fitness mapping). Score capped at 8 because the conceptual connection between dynamics and function is well-recognized; the execution step is novel, not the hypothesis. |
| Scientific Impact | **8** | Addresses the central post-AlphaFold question: what does conformational heterogeneity tell us about biological function? If successful, Gamma reframes mutation effect prediction from sequence-centric (PLMs) to ensemble-centric (BioEmu + DMS). ProteinGym's 2.7M variants across 217 assays provide the broadest possible functional ground truth. The result would directly influence how the field uses AI-generated ensembles and could shift practice in protein engineering and drug design. The impact is slightly lower than Alpha-M because the causal chain (ensemble → function) is harder to interpret and requires the BioEmu ensemble quality to be trustworthy -- which Aryal et al. (2025) showed has limitations for mutation-induced conformational shifts. |
| Computational Feasibility | **9** | BioEmu is MIT-licensed, pip-installable, and H200-compatible. ProteinGym is publicly available (MIT license). The compute estimate (~8,200 GPU-hrs) is modest: 50 proteins x ~164 GPU-hrs each for BioEmu ensemble generation (1000 conformations per protein) + feature extraction and regression. No special hardware requirements beyond standard CUDA. OpenMM/GROMACS for any validation MD. Back-calculation of ensemble features (RMSF, cryptic pocket occupancy, contact frequency matrices) is straightforward. This is among the most computationally accessible of the six projects. |
| Timeline Feasibility | **9** | 8,200 GPU-hrs maps to ~6 weeks on 8 H200s. With parallelism, ensemble generation for all 217 ProteinGym proteins could complete in 3-4 weeks. Feature extraction, regression, and analysis could proceed in parallel. Total realistic timeline: 10-12 weeks from start to draft, easily fitting summer 2026. The main bottleneck is iteration on the mapping architecture (choosing between simple regression, attention-based pooling, or graph neural network aggregation of ensemble features), which requires 2-3 weeks of model development. |
| Publication Potential | **8** | Nature Computational Science is the target and the fit is strong: the paper addresses the central question of post-AF structural biology, uses newly available tools (BioEmu, BioEmu v1.2), and provides a quantitative benchmark against the largest DMS dataset in existence. The risk is reviewer skepticism about BioEmu ensemble quality -- particularly given the Aryal et al. finding. This can be addressed by framing the paper as "what can current ensemble generators do" (with honest BioEmu limitations acknowledged) and showing that even imperfect ensembles carry functional information. Competing approaches (PLMs, ESM2, EVE) must be strong baselines. |

**Gamma Total: 42/50 (Weighted Mean: 8.4)**

Note: Gamma actually scores higher than Alpha-M by raw mean (8.4 vs 8.2) because its
feasibility scores are much better. The overall R2 score of 8.5 for Gamma vs 8.7 for
Alpha-M reflects the community's view that Alpha-M has higher novelty ceiling.
From a pure summer-2026 executability standpoint, Gamma is the safer choice.

---

### Project 3: Delta -- PerturbMark

**R2 Score: 8.6 | Compute: 1,000-2,000 GPU-hrs | Target Venue: Nature Methods**

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | **6** | This score has dropped from Round 2 due to three developments: scPerturBench (Nature Methods, February 2026) published a 27-method x 29-dataset benchmark; AlphaCell (bioRxiv March 2026) claims zero-shot cross-context generalization; and Tahoe-x1 (bioRxiv October 2025) is a 3B-parameter model trained on Tahoe-100M claiming SOTA across contexts. The core novelty of PerturbMark -- "a cross-context benchmark using Tahoe-100M with standardized metrics" -- is now contested terrain. What remains novel is the specific combination: (a) Tahoe-100M as test data (scPerturBench doesn't use it), (b) the weighted/ranked metrics proposed by the "Diversity by Design" paper (no existing benchmark adopts them), and (c) the cross-dataset/cross-cell-line generalization evaluation. But claiming novelty requires clearly carving out what scPerturBench did not do. |
| Scientific Impact | **8** | The field is in genuine methodological crisis. Nature Methods published scPerturBench (February 2026) and Ahlmann-Eltze et al. (2025) within months of each other, with contradictory conclusions. A definitive cross-context benchmark using Tahoe-100M -- the largest perturbation dataset ever -- with standardized metric choices could settle this. The scientific stakes are high: if DL truly doesn't outperform linear baselines even with massive data, this has profound implications for the virtual cell vision. High impact, but requires clearly differentiating from scPerturBench. |
| Computational Feasibility | **10** | The lowest compute requirement of any project (1,000-2,000 GPU-hrs). All methods (GEARS, CPA, scGPT, X-Cell, SCALE, AlphaCell) are open-source. Tahoe-100M is CC0-licensed on Hugging Face (429 GB). X-Atlas (25.6M cells) is publicly available. Evaluation can be done on a subset of the data for fast iteration. This is a strength: the project is not gated on compute, only on careful experimental design and analysis time. |
| Timeline Feasibility | **9** | The low compute requirement means fast iteration. The primary time investment is experimental design (defining cross-context splits, selecting baselines, choosing metrics) and analysis. Realistically: 2-3 weeks for dataset preparation + 2-3 weeks for model training and evaluation + 3-4 weeks for analysis and writing = 7-10 weeks total. Fits summer 2026 easily. |
| Publication Potential | **7** | Nature Methods is the natural venue (benchmark/evaluation methodology). scPerturBench was just published there (February 2026), which cuts both ways: it proves Nature Methods accepts perturbation benchmarks at this scale, but it also means the Delta paper must clearly differentiate from scPerturBench in the introduction and establish that scPerturBench left specific questions unanswered (Tahoe-100M scale, metric controversy, cross-context splits). Reviewers will ask: "How is this different from scPerturBench?" This is answerable but requires careful framing. Nature Comp Sci is a stretch -- benchmark papers with no new computational methods typically land in Nature Methods or similar. |

**Delta Total: 40/50 (Weighted Mean: 8.0)**

Downgraded from R2 = 8.6 to 8.0 due to the significant increase in competition from
scPerturBench (Nature Methods, February 2026) and AlphaCell (March 2026). The competitive
moat has eroded. The project remains feasible and impactful, but now requires a clearer
differentiation narrative.

---

### Project 4: Alpha-L -- LiveBioBench

**R2 Score: 8.2 | Compute: 1,500-16,000 GPU-hrs/yr | Target Venue: Nature Methods / NeurIPS**

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | **8** | No cross-modal, temporally-gated, UQ-aware benchmark exists for specialist biological foundation models (distinct from general LLMs). LiveProteinBench (December 2025) establishes temporal gating for proteins, and the 28.3 percentage-point drop in model performance on uncontaminated data is a striking finding. BioMol-LLM-Bench (April 2026) is cross-modal but static and LLM-focused. The genuine novelty is the intersection of all four properties: specialist FMs + temporal gating + cross-modal + UQ calibration. However, the novelty of each individual component is moderate -- temporal gating is borrowed from LiveProteinBench, cross-modal benchmarks exist (just not temporally gated), and UQ benchmarks exist (ImmUQBench, UNIQUE). The novelty is in the combination and in the cross-modal scope. |
| Scientific Impact | **8** | Demonstrating that FM performance degrades 28% on uncontaminated data across modalities would force the community to adopt stricter evaluation practices. The annual renewal mechanism gives the benchmark long-term value (a living resource, not a one-time paper). UQ-aware evaluation would be the first to require calibration alongside accuracy for biological FMs. Medium-term impact: shapes how the next generation of FMs are evaluated. Long-term impact: potentially as influential as ImageNet for vision was to that field. However, the impact depends on community adoption, which is not guaranteed. |
| Computational Feasibility | **8** | Compute is modest to moderate (1,500-16,000 GPU-hrs per annual cycle depending on scope). All data sources support temporal metadata: UniProt, PDB, ChEMBL, ClinVar, CELLxGENE all have creation/release dates. The main technical challenge is building the infrastructure for automated temporal filtering, multi-modal evaluation pipelines, and calibration metric computation -- this is engineering, not novel computation. The UQ component requires running FMs multiple times (dropout, ensembles) which adds cost but is manageable. |
| Timeline Feasibility | **7** | The initial benchmark release is achievable in summer 2026 (data curation + evaluation infrastructure + initial model evaluation). However, "living benchmark" infrastructure requires ongoing maintenance post-publication, which is a commitment beyond a single summer. The first publication can be a snapshot ("as of June 2026"), with the annual renewal framed as a future benefit. The main risk is scope creep: trying to cover all four modalities deeply in one summer may require prioritizing (e.g., proteins + DNA in v1.0, molecules + single-cell in v2.0). |
| Publication Potential | **7** | NeurIPS Datasets and Benchmarks or Nature Methods are the appropriate venues. The paper would be accepted readily at NeurIPS if the cross-modal scope is delivered. Nature Methods is possible but more likely to require a strong showing of impact (e.g., demonstrating that model rankings change dramatically on uncontaminated data). Nature Computational Science is a reach for a benchmark paper without a novel algorithm, though the contamination-finding framing ("models are 28% less accurate than reported") could make it attractive to NatCompSci as a "perspective with evaluation" type article. |

**Alpha-L Total: 38/50 (Weighted Mean: 7.6)**

From a multisim perspective, this is a strong project scientifically but slightly lower
priority than Alpha-M and Gamma because (a) it is most distant from simulation methodology
(purely benchmark/evaluation), (b) the timeline feasibility for the full cross-modal
scope is tighter than it appears, and (c) it requires infrastructure engineering that
is labor-intensive and may distract from the core science. Excellent project, but not
the top choice from a physics-grounded simulation viewpoint.

---

### Project 5: Alpha-G -- Molecular Design Benchmark

**R2 Score: 8.2 | Compute: 20,000-85,000 GPU-hrs | Target Venue: Nature Computational Science / Nature Chemistry**

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | **7** | The gap is acknowledged by the community (three independent efforts -- MolGenBench, Beyond Affinity, MolScore -- each identified it from different angles). MolGenBench (November 2025) is the closest published attempt: 120 targets, 220K actives, real-world scenarios. However, MolGenBench still lacks ADMET, synthesizability, and retrospective outcome validation. The genuine novelty of Alpha-G is closing all four remaining gaps simultaneously (ADMET + synthesizability + retrospective outcomes + cross-paradigm fairness). But with MolGenBench already existing, the differentiation must be sharp and the value-add clearly quantified. |
| Scientific Impact | **8** | The field genuinely lacks a benchmark that mimics real drug discovery decision-making. Pipeline attrition rates differ 10-100x across methods (genchem deep-dive), meaning methods that look equivalent by current metrics could have dramatically different real-world utility. If Alpha-G demonstrates this, it reshapes how generative molecular design is evaluated. Pharmaceutical industry relevance is high (practical industry consortium, Polaris, etc.). However, the risk is that "another benchmark" is perceived as incremental given MolGenBench (November 2025). |
| Computational Feasibility | **6** | The compute estimate (20K-85K GPU-hrs) is feasible on the HPC, but the bottleneck is NOT compute -- it is the massive manual curation effort. Building a retrospective dataset connecting 30-50 drug targets to actual drug progression data (hit → lead → preclinical → clinical) requires licensing agreements, data extraction from literature, and expert annotation. This is a human-hours bottleneck, not a GPU-hours bottleneck. The public datasets that exist (ChEMBL 36, BindingDB) provide bioactivity data but not the progression narrative. The curation risk is high and may not complete within a summer 2026 timeframe. |
| Timeline Feasibility | **5** | The data curation bottleneck makes timeline feasibility the weakest of all six projects. A comprehensive alpha-G paper requires: (a) target selection and literature-based progression data curation (3-5 weeks, partially manual), (b) docking calculations (1-2 weeks with parallelism), (c) ADMET predictions via open tools (1 week), (d) synthesizability scoring via ASKCOS or RxnFP (1 week), (e) running 5-10 generative models on each target (2-3 weeks), (f) analysis and comparison to known actives (2-3 weeks), (g) writing (3 weeks). Total: 13-19 weeks, pushing the edge of summer 2026 even with a motivated team. |
| Publication Potential | **7** | Nature Computational Science or Nature Chemistry are the natural venues. The paper's central claim -- "existing benchmarks fail to predict drug discovery pipeline success" -- is compelling and backed by the industry data on attrition. Reviewers will ask: why these 30-50 targets and not others? How do you handle proprietary data in retrospective validation? These are answerable but require careful framing. The publication potential is solid but execution risk is high. |

**Alpha-G Total: 33/50 (Weighted Mean: 6.6)**

Alpha-G is a strong scientific concept but the curation burden and timeline risk are
genuine concerns that the multi-scale simulation perspective amplifies. Projects that
depend primarily on human-hours for data curation rather than computational resources
are harder to de-risk within a fixed summer timeline than those that are GPU-bound.

---

### Project 6: Beta -- ContextVEP

**R2 Score: 8.2 | Compute: 500-1,000 GPU-hrs | Target Venue: Nature Genetics / Genome Research**

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | **6** | The gap has been partially filled from multiple directions since Round 1: AlphaMissense (Science, 2023) for coding VUS, AlphaGenome (Nature, January 2026) for non-coding regulatory variants, popEVE (Nature Genetics, December 2025) for population-calibrated evolutionary scoring, IMPPROVE (Nature Communications, 2025) for tissue conditioning via GTEx, DYNA (Nature Machine Intelligence, 2025) for disease-specific coding variants, ML-Penetrance (Science, August 2025) for penetrance estimation. The integration of all four context dimensions (tissue expression + disease context + GOF/LOF + penetrance) remains unclaimed. But the novelty claim is "integration of existing tools" rather than "new computational method," which limits the novelty ceiling. |
| Scientific Impact | **8** | 1M+ VUS in ClinVar represent a genuine clinical need. If ContextVEP correctly reclassifies even 5% of uncertain variants to "likely pathogenic/benign," it directly impacts patient care. The clinical impact makes this appealing to high-impact venues. However, without wet-lab validation (which is excluded), the clinical utility claim requires careful framing as "computational prioritization" rather than "clinical reclassification." The lack of experimental validation is a serious limitation for a clinical variant paper in Nature Genetics. |
| Computational Feasibility | **9** | 500-1,000 GPU-hrs is the lowest compute requirement of any project. All data sources are public: GTEx v8, HPA v25, ClinVar 3M+ variants, gnomAD v4 730K exomes. The technical work involves feature engineering (combining AlphaMissense scores, AlphaGenome regulatory tracks, GTEx expression, gnomAD allele frequencies) followed by ensemble or deep learning integration. No new MLFF training or long MD simulations required. From a resource perspective, this is the most accessible project. |
| Timeline Feasibility | **9** | The low compute requirement and well-defined data sources make this highly feasible within summer 2026. Estimated timeline: 2-3 weeks for data integration and feature engineering, 2-3 weeks for model training and evaluation, 2 weeks for analysis, 3 weeks for writing = 9-11 weeks. Highly manageable. |
| Publication Potential | **6** | Nature Genetics or Genome Research are the natural venues. Nature Genetics has published AlphaMissense and would be receptive to a successor. However, the "integration of existing tools" framing is harder to defend at Nature Genetics than a novel method. Reviewers will ask: what does ContextVEP predict that AlphaMissense + AlphaGenome + popEVE cannot predict individually? Demonstrating that the integrated model outperforms each component significantly, especially for the high-difficulty VUS cases, is achievable but requires careful benchmark design. Nature Computational Science is unlikely to accept a variant predictor paper without novel methodology or a surprise finding. |

**Beta Total: 38/50 (Weighted Mean: 7.6)**

Beta is the most computationally accessible project and the most clinical in scope. From
a multi-scale simulation perspective, it sits slightly outside the core expertise domain
(no simulation methodology involved) and the novelty and publication potential scores
(both 6) reflect the genuinely crowded competitive landscape since Round 1.

---

## Summary Ranking Table

| Rank | Project | Novelty | Impact | Comp. Feasibility | Timeline | Pub. Potential | Total | Mean | R2 Score | Venue Target |
|------|---------|---------|--------|-------------------|----------|---------------|-------|------|----------|--------------|
| 1 | **Alpha-M** (MLFF Crash Test) | 9 | 9 | 7 | 7 | 9 | 41 | 8.2 | 8.7 | Nat Comp Sci |
| 2 | **Gamma** (Dynamics-to-Function) | 8 | 8 | 9 | 9 | 8 | 42 | 8.4 | 8.5 | Nat Comp Sci |
| 3 | **Delta** (PerturbMark) | 6 | 8 | 10 | 9 | 7 | 40 | 8.0 | 8.6 | Nat Methods |
| 4 | **Alpha-L** (LiveBioBench) | 8 | 8 | 8 | 7 | 7 | 38 | 7.6 | 8.2 | Nat Methods / NeurIPS |
| 5 | **Beta** (ContextVEP) | 6 | 8 | 9 | 9 | 6 | 38 | 7.6 | 8.2 | Nat Genetics |
| 6 | **Alpha-G** (Molecular Design) | 7 | 8 | 6 | 5 | 7 | 33 | 6.6 | 8.2 | Nat Comp Sci |

Notes on rank ordering:
- **Alpha-M and Gamma are very close** and could be swapped depending on risk tolerance.
  Alpha-M has the higher novelty/impact ceiling; Gamma has the better feasibility scores.
  I rank Alpha-M #1 because novelty and scientific impact matter most for Nature Comp Sci.
- **Delta drops from R2 rank 2 to rank 3** primarily due to the AlphaCell and scPerturBench
  competition intensification. Still strong, but the competitive moat has eroded materially.
- **Alpha-L and Beta tie** at 38/50 but with different profiles: Alpha-L is higher novelty
  but harder to scope; Beta is lower novelty but more feasible. The tie is appropriate.
- **Alpha-G ranks last** not because the idea is bad but because the data curation bottleneck
  is the real constraint, and it is harder to resolve with compute than with human time.

---

## Top Pick

**Recommendation: Alpha-M (MLFF Biomolecular Crash Test)**

From the multi-scale simulation expert perspective, Alpha-M is the top pick for the
following reasons:

1. **The gap is real and verified.** No paper has systematically compared multiple
   MLFFs against experimental protein biophysical observables (NMR order parameters,
   3J-couplings, SAXS profiles, HDX-MS protection factors). The Structure-Based
   Experimental Datasets review (PMC12823150, 2025) makes this explicit. The materials
   science analog (UniFFBench) demonstrated that "models achieving impressive
   computational benchmark performance often fail when confronted with experimental
   complexity" -- the biomolecular analog of this finding has not been made.

2. **The competitive space is empty.** As of April 2026, no group has announced this
   project. The nearest competitor (arXiv 2505.23354) uses MLFF embeddings to predict
   NMR chemical shifts without running MLFF-based MD simulations at all. This is
   categorically different from the benchmark Alpha-M would build.

3. **The community need is acute.** Every group publishing a new MLFF (at least 8
   groups in 2024-2026) claims near-quantum-mechanical accuracy for proteins. Every
   experimental biophysicist reading these papers has the same question: "What happens
   to NMR observables?" Alpha-M answers this definitively for the first time.

4. **The result is high-impact regardless of direction.** If MLFFs pass the experimental
   benchmark, the MLFF field receives a major validation. If they fail, the field gets
   a critical course-correction. Either outcome is publishable in Nature Computational
   Science with immediate citation impact.

5. **The toolchain is complete.** MACE-OFF23, SO3LR, AI2BMD, LiTEN-FF, ANI-2x, Allegro
   are all open-source and protein-tested. BMRB has 21,820 NMR entries. SASBDB has
   5,272 SAXS datasets. OpenMM-ML provides a unified simulation interface. SPARTA+,
   SHIFTS, and SPyCi-PDB back-calculate NMR observables from MD trajectories.
   FOXS and Pepsi-SAXS back-calculate SAXS profiles. The pipeline is completely
   defined with no missing links.

**Acknowledged weaknesses of Alpha-M:**
- High compute (180K-270K GPU-hrs) requires careful resource allocation
- Timeline is tight: 14 weeks if starting now
- Some MLFFs may be unstable on challenging proteins (IDPs, large complexes)
- If results show all MLFFs fail similarly, differentiation among them is limited

These weaknesses are manageable: the compute is within the HPC budget, the instability
risk can be mitigated by protein selection (starting with well-folded globular proteins),
and the instability finding itself is scientifically interesting.

---

## Best Combination

**Recommended Combination: Alpha-M + Gamma (MLFF Quality Underpins Ensemble Function)**

These two projects form a coherent scientific axis:

**Alpha-M** establishes: which MLFFs accurately reproduce experimental protein dynamics
(NMR, SAXS, HDX-MS). It answers: "Can we trust AI-generated ensembles?"

**Gamma** establishes: do accurate conformational ensembles predict biological function
(DMS fitness)? It answers: "What does ensemble quality buy us?"

Together, they tell a complete story:
1. Alpha-M identifies which ensemble generators (classical FF, MLFF, BioEmu) best
   reproduce experimental observables.
2. Gamma shows that better ensemble quality → better DMS fitness prediction.
3. The combined result is: "MLFF X produces biophysically accurate ensembles (Alpha-M),
   and those ensembles predict mutation effects better than existing PLM-only approaches
   (Gamma)."

This combination could be published as a single Nature Computational Science paper or
as two back-to-back papers in the same issue. The combined story -- "from accurate
dynamics to function prediction" -- is more compelling than either piece alone and
would be instantly recognized as a landmark post-AlphaFold contribution.

**Practical consideration:** Alpha-M requires ~180K GPU-hrs; Gamma requires ~8,200 GPU-hrs.
The total (~188K GPU-hrs) is within budget. The Alpha-M simulation data could directly
inform which trajectories to use as input for Gamma's ensemble-to-function mapping.
The projects could be executed sequentially (Alpha-M first to identify best-performing
MLFF; Gamma second using that MLFF's ensembles plus BioEmu) or in parallel on different
HPC partitions.

**Alternative combination to consider:** Gamma + Beta. Gamma predicts functional effects
of mutations from conformational ensembles; Beta predicts pathogenicity of VUS variants
from context. Both are about "function prediction beyond sequence." This pairing is
less computationally demanding (total ~9,000-10,000 GPU-hrs) and more feasible for
a team with limited HPC allocation, though less scientifically coherent from a
multi-scale simulation standpoint.

---

## Reasoning: Objective Criteria Applied

### Why Alpha-M Over Gamma as Top Pick

Both projects score very close (Alpha-M 41, Gamma 42 by raw total). I assign Alpha-M
the top rank despite the lower raw total because:

1. **Novelty ceiling:** Alpha-M's novelty (9) is one point higher than Gamma's (8).
   For a Nature Computational Science paper, novelty is the most important criterion.
   "First benchmark of MLFFs against experimental biophysical observables" is a stronger
   novelty claim than "first framework connecting BioEmu ensembles to ProteinGym fitness."

2. **Dual-outcome impact:** If Alpha-M shows MLFFs fail, the impact is equally large
   as if they pass. Gamma's impact depends on finding that BioEmu ensembles are
   sufficiently informative -- which the Aryal et al. (2025) assessment suggests may
   require careful protein selection.

3. **Competitive moat:** Alpha-M has an essentially empty competitive space. Gamma
   has a 6-12 month window before the BioEmu + DMS connection becomes obvious to other
   groups (e.g., the BioEmu team at Microsoft, the Marks Lab at ProteinGym).

4. **Feasibility of Gamma depends on Alpha-M type work:** The best ensemble generator
   for Gamma should ideally be validated against experiments first. Alpha-M provides
   this validation infrastructure.

### Why Delta Dropped

The emergence of scPerturBench (Nature Methods, February 2026) and AlphaCell
(bioRxiv, March 2026) between Round 2 and Round 3 is the key competitive update.
scPerturBench publishes 27 methods x 29 datasets in the exact target venue. While
it does not use Tahoe-100M and does not resolve the metric controversy, its existence
means Delta cannot be the "first comprehensive perturbation benchmark" -- it must be
the "second but definitively better" benchmark. This is achievable but requires sharper
framing and narrows the novelty from 8 to 6.

### Why Alpha-G Ranks Last

The decisive factor is the curation bottleneck. Alpha-G requires constructing a
retrospective drug progression dataset linking molecule generation to actual hit→lead→
preclinical outcomes across 30-50 targets. This is largely a human-hours problem
(literature mining, expert annotation, licensing) rather than a compute problem. For
a project constrained to a summer 2026 timeline with a small computational team and
no wet-lab or pharma collaborators assumed, this bottleneck is the highest risk of
any project. MolGenBench (November 2025) took what appears to be a substantial team
effort to assemble its 120-target, 220K-active dataset -- and it still doesn't include
the retrospective progression data that would make Alpha-G genuinely novel.

### Venue Clarification

- **Alpha-M, Gamma:** Nature Computational Science (novel framework, resource-intensive,
  community-shaping result)
- **Delta:** Nature Methods (benchmark/evaluation methodology, precedent from scPerturBench
  and Ahlmann-Eltze et al.)
- **Alpha-L:** Nature Methods or NeurIPS Datasets & Benchmarks (benchmark infrastructure
  paper)
- **Beta:** Nature Genetics (variant effect prediction, clinical focus)
- **Alpha-G:** Nature Computational Science or Nature Chemistry (if fully executed),
  but more realistically Journal of Chemical Information and Modeling or Nature Methods
  given timeline risks

---

## References

1. Mannan et al. (2025) "UniFFBench: Benchmarking Universal Force Fields Against
   Experimental Crystal Structures." arXiv 2508.05762. [Materials science analog
   demonstrating "reality gap" between computational and experimental benchmarks]

2. Kovacs et al. (2025) "MACE-OFF: Short-Range Transferable Machine Learning Force
   Fields for Organic Molecules." Journal of the American Chemical Society.
   https://pubs.acs.org/doi/10.1021/jacs.4c07099

3. Frank et al. (2026) "SO3LR: Molecular Simulations with a Pretrained Neural Network
   and Universal Pairwise Force Fields." Journal of the American Chemical Society.
   https://pubs.acs.org/doi/10.1021/jacs.5c09558

4. Li et al. (2024) "AI2BMD: Ab initio characterization of protein molecular dynamics
   with AI2BMD." Nature. https://www.nature.com/articles/s41586-024-08127-z

5. PMC12823150 (2025) "Structure-Based Experimental Datasets for Benchmarking Protein
   Simulation Force Fields." Living Journal of Computational Molecular Science.
   https://pmc.ncbi.nlm.nih.gov/articles/PMC12823150/ [Explicitly acknowledges MLFF
   benchmarking gap]

6. TEA Challenge 2023 (2025) "Crash testing machine learning force fields for molecules,
   materials, and interfaces." Chemical Science.
   https://pubs.rsc.org/en/content/articlehtml/2025/sc/d4sc06530a

7. Bojan et al. (2025/2026) "Representing local protein environments with machine
   learning force fields." arXiv 2505.23354. [Uses MLFF embeddings, not MLFF
   simulation vs. experimental observables -- confirmed as distinct from Alpha-M]

8. Lewis et al. (2025) "Scalable emulation of protein equilibrium ensembles with
   generative deep learning (BioEmu)." Science.
   https://www.biorxiv.org/content/10.1101/2024.12.05.626885v1.full [MIT license,
   H200-compatible]

9. Aryal et al. (2025) "Assessing the Performance of BioEmu in Understanding Protein
   Dynamics." International Journal of Molecular Sciences 27, 2896.
   https://www.mdpi.com/1422-0067/27/6/2896 [BioEmu limitations for mutation-induced
   conformational shifts]

10. BioEmu Augmented Molecular Simulation (2026). bioRxiv 2026.01.07.698041.
    https://www.biorxiv.org/content/10.64898/2026.01.07.698041v1 [January 2026 preprint
    combining BioEmu with MD and MSM -- closest work to Gamma, but no DMS connection]

11. Ahlmann-Eltze C, Huber W, Anders S (2025) "Deep-learning-based gene perturbation
    effect prediction does not yet outperform simple linear baselines." Nature Methods.
    https://www.nature.com/articles/s41592-025-02772-6

12. Wei Z et al. (2026) "Benchmarking algorithms for generalizable single-cell
    perturbation response prediction (scPerturBench)." Nature Methods 23, 451-464.
    https://www.nature.com/articles/s41592-025-02980-0 [KEY: Published February 2026,
    major competitive development for Delta]

13. AlphaCell (2026) "Towards building a World Model to simulate perturbation-induced
    cellular dynamics by AlphaCell." bioRxiv, March 5, 2026.
    https://www.biorxiv.org/content/10.64898/2026.03.02.709176v1 [KEY: Zero-shot
    cross-context perturbation prediction, trained on Tahoe-100M]

14. Gandhi et al. (2025) "Tahoe-x1: Scaling Perturbation-Trained Single-Cell Foundation
    Models to 3 Billion Parameters." bioRxiv, October 23, 2025.
    https://www.biorxiv.org/content/10.1101/2025.10.23.683759v1 [3B parameter model
    trained on Tahoe-100M, SOTA on four disease benchmarks]

15. Tahoe-100M (2025) "Tahoe-100M: A Giga-Scale Single-Cell Perturbation Atlas."
    bioRxiv February 2025. CC0 license. Hugging Face: tahoebio/Tahoe-100M.
    https://www.biorxiv.org/content/10.1101/2025.02.20.639398v1

16. Rongdingyi et al. (2025) "LiveProteinBench: A Contamination-Free Benchmark for
    Assessing Models' Specialized Capabilities in Protein Science." arXiv 2512.22257.
    https://arxiv.org/html/2512.22257v1 [Protein-only temporal-gated benchmark;
    no cross-modal equivalent exists as of April 2026]

17. Marin et al. (2026) "Advancing regulatory variant effect prediction with AlphaGenome."
    Nature. https://www.nature.com/articles/s41586-025-10014-0 [AlphaGenome: eQTL
    AUROC 0.80, non-commercial license, January 2026]

18. popEVE (2025) "Proteome-wide model for human disease genetics." Nature Genetics.
    https://www.nature.com/articles/s41588-025-02400-1 [December 2025, population-
    calibrated evolutionary scoring without tissue/disease context]

19. MolGenBench (2025) "Benchmarking Real-World Applicability of Molecular Generative
    Models from De novo Design to Lead Optimization." bioRxiv November 2025.
    https://www.biorxiv.org/content/10.1101/2025.11.03.686215v1 [120 targets, 220K
    actives, no ADMET/synthesizability/retrospective outcomes -- confirms Alpha-G gap]

20. Dibaeinia et al. (2026) "Virtual Cells Need Context, Not Just Scale." bioRxiv
    February 2026.
    https://www.biorxiv.org/content/10.64898/2026.02.04.703804v1 [DEG recall ~9%
    despite favorable aggregate metrics; context diversity > scale]

21. Lindorff-Larsen K et al. (2012) "Systematic validation of protein force fields
    against experimental data." PLoS ONE 7, e32131. [Historical precedent for the
    type of comparison Alpha-M would conduct for MLFFs]
