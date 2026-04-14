---
agent: orch
round: 1
date: 2026-04-14
type: roundtable-synthesis
---

# Round 1 Synthesis: Broad Gap Scanning Results

## Overview

Seven domain specialists completed Round 1 broad gap scanning, producing **33 total gaps**
across protein dynamics, generative chemistry, multi-scale simulation, regulatory genomics,
systems biology, AI/ML methods, and translational medicine. Each specialist performed
extensive internet research and produced gap reports with citations, feasibility assessments,
and impact scores.

---

## Master Gap Catalog (Ranked by Overall Score)

### Tier 1: Highest-Impact Gaps (Score >= 8.0)

| Rank | Agent | Gap ID | Title | Overall |
|------|-------|--------|-------|---------|
| 1 | reggeno | complex-trait-vep | Near-Random Prediction of Complex Trait Non-Coding Variant Effects | 8.4 |
| 2 | aiml | perturbation-prediction-crisis | Deep Learning Fails to Beat Linear Baselines for Perturbation Prediction | 8.4 |
| 3 | transmed | context-vus | Context-Dependent Variant Pathogenicity for Clinical VUS Resolution | 8.4 |
| 4 | genchem | evaluation-crisis | No End-to-End Benchmark for Molecular Design to Drug Discovery | 8.2 |
| 5 | aiml | fm-evaluation-crisis | Foundation Model Benchmarks Suffer from Contamination and Gaming | 8.2 |
| 6 | protdyn | dynamics-to-function | No Framework Maps Conformational Ensembles to Biological Function | 8.0 |
| 7 | protdyn | ensemble-mutation-effects | Mutation Effect Predictors Ignore Conformational Dynamics | 8.0 |
| 8 | multisim | mlff-experimental-validation | ML Force Fields Validated on Energy/Force, Not Experimental Observables | 8.0 |
| 9 | sysnet | context-perturb-transfer | No Rigorous Cross-Context Perturbation Generalization Benchmark | 8.0 |
| 10 | aiml | uncertainty-aware-bio-fm | Foundation Models Lack Calibrated Uncertainty Estimates | 8.0 |

### Tier 2: Strong Gaps (Score 7.2-7.8)

| Rank | Agent | Gap ID | Title | Overall |
|------|-------|--------|-------|---------|
| 11 | protdyn | allostery-from-sequence | No Sequence-Only Allosteric Communication Predictor | 7.8 |
| 12 | genchem | scoring-generalization | ML Scoring Functions Collapse on Novel Targets (40% Drop) | 7.8 |
| 13 | protdyn | ensemble-evaluation-framework | No Standardized Ensemble Evaluation with Functional Tier | 7.6 |
| 14 | multisim | proteome-dynamics-mutations | >65% Human Proteome Lacks Dynamics Characterization | 7.6 |
| 15 | aiml | cross-scale-fm-integration | No Framework Bridges FM Predictions Across Biological Scales | 7.6 |
| 16 | sysnet | causal-grn-scale | Genome-Scale Causal GRN That Improves Prediction Unsolved | 7.6 |
| 17 | reggeno | celltype-reg-collapse | Cell-Type-Specific Regulatory Prediction Systematically Fails | 7.4 |
| 18 | transmed | combo-efficacy | Drug Combination Efficacy Prediction Beyond Synergy Scores | 7.4 |
| 19 | transmed | pharmacogenomics-substrate | Substrate-Aware Pharmacogenomic Variant Effect Prediction | 7.4 |
| 20 | genchem | selectivity-design | No Proteome-Wide Selectivity in Molecular Design | 7.2 |
| 21 | multisim | high-throughput-fep | FEP Limited to ~30-100 Compounds Per Target | 7.2 |
| 22 | reggeno | multimodal-reg-genome | No Unified Multi-Modal Regulatory Genome Model | 7.2 |
| 23 | sysnet | temporal-perturb-dynamics | Perturbation Methods Predict Static Endpoints Only | 7.2 |
| 24 | sysnet | spatial-perturb-tissue | Spatially-Resolved Perturbation Prediction | 7.2 |
| 25 | sysnet | multimodal-perturb-predict | Multi-Modal Perturbation Prediction | 7.2 |
| 26 | transmed | penetrance-modifier | Computational Penetrance Prediction with Genetic Modifiers | 7.2 |

### Tier 3: Lower Priority (Score <= 7.0)

| Rank | Agent | Gap ID | Title | Overall |
|------|-------|--------|-------|---------|
| 27 | reggeno | grn-generalization | Cross-Cell-Type GRN Inference Generalization Failure | 6.8 |
| 28 | multisim | automated-multi-resolution | Automated Multi-Resolution Simulation Framework | 6.8 |
| 29 | genchem | conformational-ensemble | Ensemble-Conditioned Molecular Generation | 6.8 |
| 30 | genchem | synthesis-reality | Reaction Feasibility Problem in Synthesis-Aware Generation | 6.6 |
| 31 | protdyn | condensate-multiscale | Condensate Multiscale Ensemble Simulation | 6.6 |
| 32 | multisim | foundation-reactive-mlff | Foundation Reactive ML Force Field for Biomolecules | 6.6 |

---

## Cross-Domain Convergence Analysis

### Theme A: The Evaluation and Benchmarking Crisis (6 gaps, 3 agents)

**Convergent gaps:** aiml perturbation-prediction-crisis (8.4), genchem evaluation-crisis (8.2),
aiml fm-evaluation-crisis (8.2), multisim mlff-experimental-validation (8.0),
sysnet context-perturb-transfer (8.0), protdyn ensemble-evaluation-framework (7.6)

**Key insight:** Three independent specialists (aiml, genchem, multisim) converged on the same
meta-problem: **the field is evaluating computational methods against the wrong metrics.**
- ML scoring functions achieve R=0.81 on benchmarks but R=0.42 on novel targets
- Deep learning perturbation models fail to beat linear baselines
- ML force fields are validated on energy/force errors, not experimental observables
- Foundation model benchmarks have contamination and metric gaming

**Combined project potential:** A cross-domain "Evaluation Crisis in Computational Biology"
paper that systematically exposes evaluation failures across molecular design, perturbation
biology, dynamics prediction, and foundation models -- then proposes principled evaluation
frameworks. This would be a paradigm-shifting contribution.

**Nature Comp Sci fit:** Extremely high. Evaluation/benchmark papers are among the most
cited in the field (MoleculeNet, ProteinGym, scIB).

### Theme B: Context-Aware Variant Effect Prediction (4 gaps, 2 agents)

**Convergent gaps:** reggeno complex-trait-vep (8.4), transmed context-vus (8.4),
transmed pharmacogenomics-substrate (7.4), transmed penetrance-modifier (7.2)

**Key insight:** Two independent specialists arrived at the same core problem: **current
variant effect predictors are context-free, but biology is context-dependent.** AlphaMissense
gives one score per variant, but pathogenicity depends on tissue, disease, genetic background,
and substrate. The numbers are stark:
- AUROC 0.48-0.52 (near random) for GWAS non-coding variant effects
- 83.3% false positive rate for AlphaMissense in some gene classes
- >1M VUS in ClinVar with no resolution path
- Only 309 of >1M GWAS associations experimentally validated

**Combined project potential:** A unified context-dependent variant effect prediction
framework that integrates tissue-specific expression, disease context, 3D structure,
and genetic background. Could target both coding VUS (transmed) and non-coding GWAS
variants (reggeno).

**Nature Comp Sci fit:** Very high. AlphaMissense (Nature 2023) and Enformer (Nature Methods
2021) set the stage; a context-aware successor would be the natural next step.

### Theme C: Dynamics-to-Function Bridge (4 gaps, 2 agents)

**Convergent gaps:** protdyn dynamics-to-function (8.0), protdyn ensemble-mutation-effects (8.0),
multisim proteome-dynamics-mutations (7.6), protdyn allostery-from-sequence (7.8)

**Key insight:** BioEmu and AlphaFlow now generate conformational ensembles, but **no
method connects ensemble properties to biological function.** This is the central
unanswered question of post-AlphaFold structural biology. The pieces are newly available:
- BioEmu generates microsecond-scale ensembles in minutes
- DMS data (ProteinGym) provides functional readouts for thousands of mutations
- ATLAS/mdCATH provide dynamics benchmarks for thousands of proteins

**Combined project potential:** "Dynamics-to-Function" -- predicting how mutations reshape
conformational ensembles and how those reshaped ensembles alter function. Uses BioEmu for
ensemble generation, DMS/ProteinGym for functional labels, and develops the first
ensemble-to-function predictive framework.

**Nature Comp Sci fit:** Very high. Fills the most-discussed gap in post-AlphaFold biology.

### Theme D: Perturbation Biology at Scale (5 gaps, 2 agents)

**Convergent gaps:** aiml perturbation-prediction-crisis (8.4),
sysnet context-perturb-transfer (8.0), sysnet causal-grn-scale (7.6),
sysnet temporal-perturb-dynamics (7.2), sysnet multimodal-perturb-predict (7.2)

**Key insight:** The perturbation prediction field is in crisis: models proliferate (X-Cell,
SCALE, AlphaCell, GEARS) but none demonstrate rigorous cross-context generalization, and
recent work shows linear baselines match deep learning. Meanwhile, massive new datasets
(X-Atlas 25.6M cells, Tahoe-100M) are available but unevaluated.

**Combined project potential:** A definitive benchmarking study of perturbation prediction
methods, testing cross-context transfer on new large-scale datasets, with causal GRN
analysis to determine when and why deep learning helps.

### Theme E: Scoring and Binding Prediction (3 gaps, 2 agents)

**Convergent gaps:** genchem scoring-generalization (7.8), genchem selectivity-design (7.2),
multisim high-throughput-fep (7.2)

**Key insight:** The scoring function is the bottleneck for all of computational drug design.
ML scores collapse on novel targets. FEP is accurate but limited to ~30-100 compounds.
No method addresses selectivity.

### Theme F: Foundation Model Reliability (3 gaps, 1 agent)

**Convergent gaps:** aiml fm-evaluation-crisis (8.2), aiml uncertainty-aware-bio-fm (8.0),
aiml cross-scale-fm-integration (7.6)

**Key insight:** Foundation models are the dominant paradigm but lack reliable evaluation,
uncertainty quantification, and cross-scale integration. The field is building on
uncertain foundations.

---

## Top 10 Gaps Selected for Round 2 Deep Dives

Based on score, cross-domain convergence, feasibility, and Nature Comp Sci potential,
the following 10 gaps advance to deep-dive research:

| # | Gap ID | Agent | Score | Theme | Deep-Dive Focus |
|---|--------|-------|-------|-------|-----------------|
| 1 | complex-trait-vep | reggeno | 8.4 | B | Verify gap; assess data availability; scope integration framework |
| 2 | perturbation-prediction-crisis | aiml | 8.4 | A/D | Verify linear baseline results; scope definitive benchmark |
| 3 | context-vus | transmed | 8.4 | B | Assess ClinVar data; scope context-dependent VEP |
| 4 | evaluation-crisis | genchem | 8.2 | A | Scope end-to-end drug design benchmark |
| 5 | fm-evaluation-crisis | aiml | 8.2 | A/F | Scope LiveBioBench cross-modal benchmark |
| 6 | dynamics-to-function | protdyn | 8.0 | C | Assess BioEmu accessibility; scope ensemble-function pipeline |
| 7 | ensemble-mutation-effects | protdyn | 8.0 | C | Verify DMS data coverage; scope variant-ensemble study |
| 8 | mlff-experimental-validation | multisim | 8.0 | A | Scope ML force field biomolecular benchmark |
| 9 | context-perturb-transfer | sysnet | 8.0 | D | Assess X-Atlas/Tahoe data; scope cross-context benchmark |
| 10 | uncertainty-aware-bio-fm | aiml | 8.0 | F | Scope UQ framework across modalities |

---

## Potential Combined Projects (for Cohort 2 to develop)

### Combined Project Alpha: "The Evaluation Crisis in Computational Biology"
- Merges: Gaps 2, 4, 5, 8 (Theme A)
- Claim: Systematic evaluation failures across comp bio domains; principled frameworks
- Risk: Very broad scope; may need to focus on 2-3 domains
- Potential: Extremely high-impact benchmark paper

### Combined Project Beta: "Context-Aware Variant Effect Prediction"
- Merges: Gaps 1, 3 (Theme B)
- Claim: First variant effect predictor that accounts for biological context
- Risk: Complex integration; large training data needed
- Potential: Direct successor to AlphaMissense

### Combined Project Gamma: "Dynamics-to-Function Mapping"
- Merges: Gaps 6, 7 (Theme C)
- Claim: First framework connecting conformational ensembles to biological function
- Risk: BioEmu accessibility; ensemble quality for non-globular proteins
- Potential: Central post-AlphaFold contribution

### Combined Project Delta: "Perturbation Prediction: What Actually Works?"
- Merges: Gaps 2, 9 (Theme D)
- Claim: Definitive benchmark resolving the perturbation prediction crisis
- Risk: Competitive space; need differentiation from existing critiques
- Potential: Resolves active Nature Methods controversy

---

## Recommendations for Round 2

1. **Deep-dive assignments should test feasibility rigorously.** Several top gaps have
   high impact but unverified feasibility. Round 2 must confirm: (a) data is actually
   accessible, (b) compute requirements are realistic, (c) the gap hasn't been filled
   by a 2026 preprint.

2. **Cross-domain pairs should be explored.** Assign specialists to gaps outside their
   domain where themes converge (e.g., aiml on perturbation + sysnet context-transfer).

3. **Combined project framing matters.** The strongest Nature Comp Sci submission will
   likely combine 2-3 related gaps into a single coherent story, not address one gap
   in isolation.

4. **The evaluation/benchmarking theme is the strongest cross-cutting opportunity.**
   Six independent gaps from three agents converge on "we're measuring the wrong things."
   This is both the most novel and the most achievable theme.
