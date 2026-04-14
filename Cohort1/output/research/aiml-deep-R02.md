---
agent: aiml
round: 2
date: 2026-04-14
type: deep-dive
---

# Deep Dive: Foundation Model Evaluation Crisis and Uncertainty Quantification

## Executive Summary

This deep-dive investigates two tightly coupled gaps in computational biology: (1) the
absence of a cross-modal, continuously updated ("live") benchmark for biological
foundation models that prevents data contamination, and (2) the lack of calibrated
uncertainty quantification (UQ) in biological FMs. Both gaps remain confirmed as of
April 2026. LiveProteinBench (December 2025) demonstrates the viability of temporal
gating for proteins, but no equivalent exists for DNA, molecules, or single-cell data.
Meanwhile, extensive contamination evidence across all modalities, combined with the
demonstrated failure of UQ to consistently improve downstream tasks, creates a
compelling opportunity for a unified "LiveBioBench" that addresses evaluation integrity
AND uncertainty calibration simultaneously.

---

## 1. Gap Verification

### 1.1 Cross-Modal Live Benchmarks: Gap Confirmed

As of April 2026, **no cross-modal live benchmark exists** that applies temporal gating
across proteins, DNA/RNA, molecules, and single-cell data simultaneously. The landscape
of relevant benchmarks is fragmented:

**Protein-only live benchmarks:**
- **LiveProteinBench** (Rongdingyi et al., December 2025, arXiv:2512.22257) -- the
  closest precedent. Uses proteins validated after January 1, 2025. Covers 12 tasks
  from UniProt. Continuously updated via automated pipeline. However, it is
  protein-only and focuses on LLM evaluation (not specialist biological FMs).
- **PFMBench** (June 2025, arXiv:2506.14796) -- 38 tasks across 17 protein foundation
  models. Comprehensive but uses static data splits (30% sequence similarity cutoff),
  not temporal gating. No contamination prevention mechanism.
- **ProteinBench** (Shen, Xue et al., September 2024, arXiv:2409.06744) -- holistic
  evaluation across structure prediction, design, and dynamics. Static benchmark, no
  temporal gating.

**DNA/Genomics benchmarks:**
- **GUE (Genome Understanding Evaluation)** from DNABERT-2 (Zhou & Ji, ICLR 2024) --
  36 datasets, 9 tasks. Static; no contamination prevention.
- **Benchmarking DNA foundation models** (Nature Communications, 2025) -- evaluated
  DNABERT-2, Nucleotide Transformer V2, HyenaDNA, Caduceus-Ph, GROVER across
  diverse genomic tasks. Static benchmark.

**Single-cell benchmarks:**
- **BioLLM** (BGI Research, Patterns, July 2025) -- standardized framework integrating
  scGPT, Geneformer, scBERT, scFoundation. Static.
- **CZI Virtual Cells benchmarking suite** (2025) -- six standardized tasks. Community-
  informed but static.

**Cross-modal/multi-scale benchmarks:**
- **BioMol-LLM-Bench** (April 2026, arXiv:2604.03361) -- 26 tasks, 4 difficulty levels,
  13 models. Closest to cross-modal, but static and focused on LLM text understanding
  of biomolecules, not specialist biological FMs. No temporal gating.
- **BixBench** (March 2025, arXiv:2503.00096) -- LLM-based agents in computational
  biology. Agent-focused, not FM evaluation.

**Critical gap confirmed:** No benchmark combines (a) temporal gating, (b) multiple
biological modalities, (c) continuous updates, and (d) evaluation of specialist
biological FMs (not just general LLMs).

### 1.2 FM Uncertainty Quantification: Gap Confirmed

**No major biological FM benchmark includes calibration metrics as standard.**

Recent developments show growing awareness but no comprehensive solution:

- **ImmUQBench** (NeurIPS 2025, Oxford Open Immunology) -- first dedicated UQ benchmark
  for protein immunogenicity. Compares Deep Ensemble, MC Dropout, SWAG, Laplace
  Approximation. Narrow scope (immunogenicity only).
- **Greenman, Amini & Yang** (PLOS Computational Biology, January 2025) -- benchmarked
  7 UQ methods on FLIP protein engineering tasks. Found "no single best UQ method"
  and uncertainty-based Bayesian optimization "never outperforms greedy sampling."
- **Benchmarking Probabilistic Modeling Methods** (Preprints.org, April 2025) --
  compared GP, BBP, Deep Ensemble, MVE, MC Dropout, SWAG across 11 protein fitness
  datasets. GP superior for prediction; ensembles best OOD.

**Key finding:** While individual UQ studies exist for specific protein tasks, there is
no unified benchmark that evaluates calibration across modalities (proteins, DNA,
molecules, single-cell) or across different FM architectures.

---

## 2. LiveProteinBench Methodology

### 2.1 Temporal Cutoff Mechanism

LiveProteinBench establishes a strict temporal boundary:

- **Cutoff date:** January 1, 2025
- **Data source:** UniProt database (experimentally validated annotations only)
- **Mechanism:** All evaluation proteins were first publicly released after the cutoff
  date. Creation dates are cross-validated with publication dates.
- **Automated pipeline:** Continuously scans UniProt for new entries meeting strict
  criteria, ensuring the benchmark "stays ahead of the training data cut-offs of
  future LLMs."

### 2.2 Task Structure (12 Tasks)

| Category | Task | Abbrev. | N samples |
|----------|------|---------|-----------|
| Functional Annotation | Catalytic Activity | CA | 200 |
| Functional Annotation | EC Number | EC | 200 |
| Functional Annotation | Molecular Function | MF | 195 |
| Functional Annotation | Biological Process | BP | 193 |
| Functional Annotation | Pathway | PW | 200 |
| Structure & Location | Active Site | AS | 146 |
| Structure & Location | Cofactor | CF | 186 |
| Structure & Location | Motif Position | MP | 52 |
| Structure & Location | Transmembrane | TM | 134 |
| Structure & Location | Cellular Component | CC | 196 |
| Physicochemical | Optimal pH | PH | 54 |
| Physicochemical | Thermal Adaptation | TA | 41 |

**Total:** ~1,797 test instances (plus 195 supplementary CPI).

### 2.3 Evaluation Format

- Multiple-choice questions with single correct answers
- Primary metric: Accuracy
- Secondary metric: Pass Rate (format compliance)
- No calibration or uncertainty metrics included

### 2.4 Contamination Validation

Models showed significantly higher accuracy on 2020-era data vs. 2025 data. For
example, GPT-5 achieved 66.76% on 2020 data vs. 38.47% on 2025 data across 5 tasks --
a **28.3 percentage point drop**, directly quantifying the contamination effect.

### 2.5 Key Results

| Model | Avg. Accuracy | Type |
|-------|---------------|------|
| GPT-5 | 60.65% | Closed-source |
| GPT-o3 | 56.48% | Closed-source |
| Gemini-2.5-Pro | 47.97% | Closed-source |
| Claude-3.7-Sonnet | 47.58% | Closed-source |
| Deepseek-V3 | 38.95% | Open-source |
| BioMedGPT-R1 | <32% | Domain-specific |

**Critical observations:**
- General LLMs outperform domain-specific biological models by >20%
- Multimodal structural input (3D projections) often degrades performance
- Performance correlates with inference compute cost, not parameter count

### 2.6 Limitations Acknowledged by Authors

- Focuses on single protein properties only
- Does not cover protein-protein interactions, docking, or mutation effects
- No extension to DNA, RNA, molecules, or cellular data discussed
- Does not evaluate specialist biological FMs (ESM, ProtTrans, etc.)

### 2.7 Extensibility Assessment

**Can LiveProteinBench's approach extend to other modalities?**

| Modality | Temporal Data Source | Feasibility | Challenge |
|----------|---------------------|-------------|-----------|
| Proteins | UniProt (new entries weekly) | HIGH | Already demonstrated |
| Small molecules | ChEMBL (annual releases, timestamped documents since v34) | HIGH | Requires bioactivity data temporal extraction |
| DNA/Genomics | GEO, ENCODE (continuous) | MEDIUM | Regulatory annotations slower to validate |
| Protein structures | PDB (>20,000 depositions in 2025) | HIGH | Rich structural data pipeline |
| Single-cell | CELLxGENE Census (weekly additions) | MEDIUM | Cell type annotations lag behind data |

---

## 3. Contamination Evidence Across Modalities

### 3.1 Protein Language Models

**Hermann, Fiedler et al. (2024)** -- "Beware of Data Leakage from Protein LLM
Pretraining" (MLCB, ICLR 2024 workshop):
- Studied ESM2-family models, ESM-1b, ESMFold, ProtTrans
- Task: Protein thermostability (melting point) prediction
- **Quantitative result:** Pretraining data leakage inflates performance by an
  average of **11.1%** compared to pretraining-aware splits
- The naive split (clustering without considering pretraining data) consistently
  overestimates generalization

**Rethinking Text-based Protein Understanding** (arXiv:2505.20354, 2025):
- Label leakage rates exceed **50%** for most protein understanding tasks
- Surpass **95%** in some extreme cases

**Flaw in PLMs for PPI inference** (Nature Machine Intelligence, 2025):
- Pretrained protein language models are a source of data leakage in protein-
  protein interaction inference tasks, producing inflated performance scores

### 3.2 Protein Interaction Benchmarks

**Revealing data leakage in protein interaction benchmarks** (ICLR 2024 GEM Workshop,
arXiv:2404.10457):
- Commonly used splitting strategies introduce "major data leakage"
- **Up to 65% data leakage** measured in standard protein interaction benchmarks
- Refinement considering deposition time reduces to 61% -- still catastrophic
- Proposed solution: Split based on 3D structural similarity of protein-protein
  interfaces

### 3.3 AlphaFold Benchmarks

**"Importance of updated benchmark sets for statistically correct AlphaFold
applications"** (bioRxiv, August 2024):
- Data leakage is a "serious issue" for ML methods built on AlphaFold2/3
- Rigorous, temporally updated benchmark sets are needed

**AlphaFold pLDDT Calibration Failures:**
- pLDDT values show no correlation with B-factors (Oliveira et al., 2023)
- 30-40% of amino acids fall in low-confidence pLDDT range for model organisms
- **33.6% FalseVerify rate** for fold-switching proteins -- AF2 is simultaneously
  confident and wrong (bioRxiv:2026.02.19.706878)
- Membrane protein pLDDT scores can be very high for non-physiological conformations
- EQAFold and AFDB were "overconfident in a low accuracy region"

### 3.4 Single-Cell Foundation Models

**Zero-shot evaluation reveals limitations** (Genome Biology, 2025, from Microsoft
Research):
- Geneformer and scGPT perform **worse than selecting highly variable genes (HVG)**
  with standard methods (Harmony, scVI) for cell type clustering
- **Data contamination documented:** Pancreas dataset partially overlaps Geneformer
  pretraining; Tabula Sapiens and Immune datasets were in scGPT pretraining data
- Models "do not consistently outperform baselines on datasets already seen during
  pretraining"
- Advocates for "community-maintained evaluation datasets excluded from all future
  pretraining"

**Gene perturbation prediction** (Ahlmann-Eltze, Huber & Anders, Nature Methods, 2025):
- "Deep-learning-based gene perturbation effect prediction does not yet outperform
  simple linear baselines"
- **None** of 5 foundation models + 2 deep learning models outperformed deliberately
  simple baselines for transcriptome change prediction
- Foundation models' "goal of providing a generalizable representation of cellular
  states... is still elusive"

### 3.5 DNA Foundation Models

**DNABERT-2** (Zhou & Ji, ICLR 2024):
- Identified k-mer tokenization causing "information leakage and overall poor
  computational efficiency" -- motivated switch to BPE
- GUE benchmark (36 datasets) does not account for pretraining overlap

**Nucleotide Transformer** (Nature Methods, 2024):
- Evaluation on reference genome tasks without systematic pretraining-awareness

### 3.6 Molecular/Drug Discovery Models

**Therapeutics Data Commons (TDC)** (Zitnik Lab, Harvard):
- Implements temporal splits as one of 5 split strategies
- DTI-DG benchmark with patent temporal split shows **Pearson's correlation drops
  from ~0.70 (in-distribution) to 0.42-0.43** with domain generalization methods
- However, temporal splits are optional, not enforced across all TDC tasks

**MOSES and GuacaMol** (established molecular generation benchmarks):
- No temporal gating mechanism
- MolScore (2024) re-implements both but does not add temporal splits
- Analysis shows many top-scoring GuacaMol proposals "do not pass experimental priors"

---

## 4. UQ Methods for Biological FMs

### 4.1 Method Taxonomy and Performance

Based on Greenman et al. (2025), ImmUQBench (2025), and additional sources:

| Method | Cost (relative) | Calibration | Scalability | Bio-FM Applicability |
|--------|-----------------|-------------|-------------|---------------------|
| **Deep Ensemble** | 5x training + inference | Often poor despite high accuracy | Linear cost scaling | Prohibitive for large FMs (ESM3 98B) |
| **MC Dropout** | 10-50x inference | Moderate | Manageable | Feasible with adapter layers |
| **Evidential DL** | 1x training, 1x inference | Variable | Excellent | Promising for regression tasks |
| **SWAG** | ~2x training | Best on immunogenicity | Good | Needs weight trajectory storage |
| **Laplace Approx.** | Post-hoc, minimal extra | Good for ECE | Good | Last-layer applicable to any FM |
| **SNGP** | ~1x (single network) | Strong, distance-aware | Excellent | Demonstrated for PPI (TUnA) |
| **Conformal Prediction** | Post-hoc calibration set | Guaranteed coverage | Excellent | Growing adoption (protein search, enzyme annotation) |
| **GP (exact)** | Cubic in N | Often best | Poor for large datasets | Infeasible for large protein datasets |

### 4.2 Key Quantitative Findings

**From Greenman et al. (2025) on FLIP benchmark:**
- 7 UQ methods on 3 protein landscapes (GB1, AAV, Meltome), 8 tasks
- "No single method that performs consistently well across all metrics"
- Ensemble: highest accuracy but "one of the most poorly calibrated"
- ESM embeddings outperformed one-hot in 21/51 cases for prediction, 29/51 for uncertainty
- **Critical for active learning:** "Uncertainty-based methods almost always perform
  better than random baseline but never outperform greedily sampling the sequences
  with the highest predicted values" in Bayesian optimization
- This means current UQ does NOT enable the promised "smart" experimental design

**From ImmUQBench (NeurIPS 2025):**
- Tasks: Immuno-Virus, Immuno-Bacteria, Immuno-Tumor
- SWAG consistently dominated UQ metrics for bacteria and tumor datasets
- Ensemble best for virus dataset (except ECE, where Laplace won)
- "Almost all UQ methods outperformed their deterministic alternative" -- UQ adds value
  even if no single method dominates

**From protein-ligand binding (Scientific Reports, 2025):**
- 5 methods compared: Deep Ensemble, MC Dropout, Laplace, Bayes by Backprop, Evidential
- Bayes by Backprop "first time applied" to this domain
- No universal winner; method choice depends on distribution shift magnitude

### 4.3 Compute Cost Analysis

- **Deep Ensemble of 5 ESM2-650M models:** ~3.25B parameters total, ~5x inference time.
  For ESM3-98B, an ensemble of 5 would require ~490B parameters -- **infeasible** on
  any current cluster.
- **MC Dropout (10 passes) on ESM2-650M:** ~10x inference time but only 1x memory for
  model weights. Feasible but slow for large-scale evaluation.
- **SNGP (single forward pass):** ~1x inference cost. Spectral normalization adds
  negligible overhead. Most practical for large FMs.
- **Conformal Prediction:** Post-hoc. Requires a calibration set (~1000 samples) but
  zero additional inference cost per prediction beyond the base model. Best for
  deployment scenarios.
- **MC-CP (Monte Carlo Conformal Prediction):** Adaptive early stopping reduces MC
  dropout passes by 50-80% while maintaining conformal guarantees.

### 4.4 The Calibration Gap in Current Benchmarks

**No major biological FM benchmark currently reports:**
- Expected Calibration Error (ECE)
- Maximum Calibration Error (MCE)
- Brier Score decomposition (reliability + resolution + uncertainty)
- Prediction interval coverage probability (PICP)
- Mean prediction interval width (MPIW)

PFMBench (38 tasks, 17 models) -- no calibration metrics.
LiveProteinBench (12 tasks) -- no calibration metrics.
ProteinBench -- no calibration metrics.
BioLLM -- no calibration metrics.
GUE -- no calibration metrics.

This is a systematic blind spot across the entire biological FM evaluation landscape.

---

## 5. LiveBioBench Cross-Modal Design

### 5.1 Architecture Overview

A proposed **LiveBioBench** would combine temporal gating across four biological
modalities with mandatory uncertainty/calibration evaluation:

```
LiveBioBench
|
+-- Protein Module
|   +-- Source: UniProt (reviewed/Swiss-Prot), PDB
|   +-- Temporal gate: Entry creation date > cutoff
|   +-- Tasks: Function prediction, fitness, structure quality
|   +-- Update: Monthly (UniProt release cycle)
|
+-- DNA/RNA Module
|   +-- Source: ENCODE, GEO, ClinVar, gnomAD
|   +-- Temporal gate: Submission/release date > cutoff
|   +-- Tasks: Variant effect, expression, regulatory element
|   +-- Update: Quarterly (regulatory annotation lag)
|
+-- Molecule Module
|   +-- Source: ChEMBL, PubChem BioAssay
|   +-- Temporal gate: Document creation date (ChEMBL v34+)
|   +-- Tasks: Bioactivity, ADMET, binding affinity
|   +-- Update: Biannually (ChEMBL release cycle)
|
+-- Single-Cell Module
|   +-- Source: CELLxGENE Census, GEO
|   +-- Temporal gate: Dataset deposition date > cutoff
|   +-- Tasks: Cell type, perturbation response, gene program
|   +-- Update: Monthly (CELLxGENE weekly ingestion)
|
+-- Cross-Modal Tasks (NOVEL)
|   +-- Variant-to-protein-function (DNA -> Protein)
|   +-- Drug-target interaction (Molecule -> Protein)
|   +-- Perturbation-to-expression (Single-cell -> DNA)
|   +-- Structure-activity relationship (Protein -> Molecule)
|
+-- UQ Evaluation Layer (ALL modules)
    +-- ECE, MCE, Brier Score
    +-- PICP and MPIW for regression tasks
    +-- Conformal prediction coverage at 90%, 95%
    +-- Selective prediction (accuracy vs. abstention curve)
    +-- OOD detection AUROC
```

### 5.2 Data Source Feasibility and Rates

| Source | New entries/year | Temporal metadata | API access | Feasibility |
|--------|-----------------|-------------------|------------|-------------|
| UniProt/Swiss-Prot | ~4,000 reviewed/year | Creation date | REST API | Proven by LiveProteinBench |
| PDB | >20,000 in 2025 | Deposition + release date | REST API | High |
| ChEMBL | ~2M bioactivities/release | Document CREATION_DATE (v34+) | REST API | High |
| ClinVar | ~80K submissions/year | Submission date | FTP/API | High |
| gnomAD | Major releases every 1-2 years | Release version | API | Medium |
| ENCODE | Continuous | Release date metadata | REST API | Medium |
| CELLxGENE | Weekly additions | Dataset deposition date | Python API | High |
| GEO | ~5,000 datasets/month | Submission date | FTP/API | High |

### 5.3 Proposed Task Set (40 Tasks)

**Protein Tasks (12, extending LiveProteinBench):**
1. Function prediction (GO terms: MF, BP, CC) -- 3 tasks
2. Enzyme classification (EC number)
3. Active site identification
4. Cofactor prediction
5. Subcellular localization
6. Thermostability prediction
7. Fitness effect of mutations (from new DMS data)
8. Structure quality assessment (new PDB vs. AlphaFold)
9. Protein-protein interaction prediction (new PDB complexes)
10. Disorder prediction (new IDP annotations)

**DNA/RNA Tasks (10):**
11. Variant effect prediction (new ClinVar pathogenic/benign)
12. Splice site prediction (new transcripts)
13. Promoter activity (new ENCODE CAGE data)
14. Enhancer-gene linking (new Hi-C/ATAC data)
15. Gene expression prediction (new GTEx tissues)
16. Transcription factor binding (new ChIP-seq)
17. Chromatin accessibility (new ATAC-seq)
18. RNA secondary structure (new Rfam families)
19. Non-coding RNA function (new annotations)
20. Epigenetic mark prediction (new bisulfite-seq)

**Molecule Tasks (8):**
21. Bioactivity prediction (new ChEMBL assays)
22. ADMET property prediction (new clinical data)
23. Binding affinity (new co-crystal structures from PDB)
24. Drug-likeness assessment (new approved drugs)
25. Selectivity prediction (new selectivity panels)
26. Molecular similarity search (new scaffolds)
27. Reaction prediction (new enzymatic reactions)
28. Synthesizability scoring (new synthetic routes)

**Single-Cell Tasks (6):**
29. Cell type annotation (new CELLxGENE datasets)
30. Gene program identification (new perturbation screens)
31. Batch effect detection (multi-site replication studies)
32. Trajectory inference (new time-course studies)
33. Cell-cell communication (new ligand-receptor data)
34. Perturbation response (new CRISPR screen results)

**Cross-Modal Tasks (4):**
35. Variant-to-protein-function (ClinVar -> UniProt)
36. Drug-target binding (ChEMBL -> PDB)
37. Perturbation-to-expression (CRISPR -> scRNA-seq)
38. Genotype-to-phenotype (gnomAD -> clinical)
39. Structure-activity (PDB -> ChEMBL)
40. Expression QTL prediction (GTEx -> regulatory)

### 5.4 Contamination Prevention Protocol

For each modality, the temporal gating protocol:

1. **Establish global cutoff date T** (e.g., January 1, 2026)
2. **Collect all data entries with creation/deposition date > T**
3. **Cross-validate dates:** Verify that no entry existed in any form before T
   (check preprints, supplementary data, conference submissions)
4. **Sequence similarity filter:** Remove any test entry with >30% sequence identity
   (proteins) or >80% nucleotide identity (DNA) to any entry before T
5. **Pretraining awareness:** For each FM evaluated, check if its training data
   could have included entries before T (using model release dates)
6. **Rolling update:** Advance cutoff date by 3 months every quarter

### 5.5 UQ Evaluation Protocol

For every task and every model, LiveBioBench would require:

**Classification tasks:**
- Standard: Accuracy, F1, AUROC
- Calibration: ECE (15 bins), MCE, Brier Score
- Selective prediction: Accuracy@90% coverage, AUROC for rejection
- Conformal: Coverage at alpha=0.05 and 0.10, average set size

**Regression tasks:**
- Standard: RMSE, MAE, Spearman rho
- Calibration: Miscalibration Area (AUCE), interval calibration plot
- Coverage: PICP at 90% and 95% nominal levels
- Sharpness: MPIW (mean prediction interval width)
- Selective prediction: RMSE@90% coverage

**OOD Detection:**
- AUROC for detecting temporally shifted data vs. pre-cutoff data
- FPR@95% TPR for OOD detection

---

## 6. Compute Requirements

### 6.1 Benchmark Infrastructure

**Data pipeline (continuous):**
- Automated scrapers for UniProt, PDB, ChEMBL, ClinVar, CELLxGENE, GEO
- Temporal filtering and deduplication
- Sequence similarity filtering (MMseqs2 for proteins, minimap2 for DNA)
- Estimated: 4-8 CPU cores continuously, ~100 GB storage growing ~50 GB/quarter

**Evaluation runs (per model):**
- 40 tasks, average ~500 test instances each = ~20,000 evaluations
- Per protein FM inference: ~0.1-1.0 GPU-seconds per sample on H200
- Per model total: ~2,000-20,000 GPU-seconds = 0.5-5.5 GPU-hours
- For 20 models: 10-110 GPU-hours per benchmark round
- **With UQ (5-member ensemble or 10 MC passes):** 50-550 GPU-hours per round
- **With conformal calibration:** Additional ~5% overhead (calibration set processing)

**Quarterly update cycle:**
- New test set curation: ~40 CPU-hours (automated pipeline)
- Full benchmark re-run: 50-550 GPU-hours (depends on model count)
- Analysis and leaderboard update: ~8 CPU-hours

### 6.2 Total Annual Compute Budget

| Component | GPU-hours/year | CPU-hours/year |
|-----------|---------------|----------------|
| Data pipeline | 0 | ~2,000 |
| Protein FM evaluation (20 models x 4 quarters) | 200-2,200 | 160 |
| DNA FM evaluation (10 models x 4 quarters) | 100-1,100 | 80 |
| Molecule FM evaluation (10 models x 4 quarters) | 50-500 | 80 |
| Single-cell FM evaluation (10 models x 4 quarters) | 200-2,200 | 80 |
| UQ overhead (5-10x for ensemble/MC methods) | 1,000-10,000 | 400 |
| **Total** | **~1,550-16,000** | **~2,800** |

**This is feasible on the available HPC cluster** with H200, RTX 5000 Ada, and B200
GPUs. The compute requirement is modest -- the main effort is in the engineering of the
data pipeline and standardized evaluation framework.

### 6.3 Development Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Data pipeline engineering | 6 weeks | Automated scrapers for all 8+ data sources |
| Task definition and curation | 4 weeks | 40 task specifications with initial test sets |
| UQ evaluation framework | 4 weeks | Calibration metric suite, conformal prediction |
| Initial benchmark run | 4 weeks | 10-20 models across all modalities |
| Paper writing | 4 weeks | Methods + initial results |
| **Total** | **~5 months** | Full benchmark + manuscript |

---

## 7. Competition Assessment

### 7.1 Direct Competitors

**LiveProteinBench** (Rongdingyi et al., 2025):
- Closest competitor for the protein modality
- Limitation: Protein-only, LLM-focused (not specialist bio-FMs), no UQ metrics
- Our differentiation: Cross-modal, includes specialist FMs, mandatory UQ evaluation

**PFMBench** (2025):
- 38 tasks, 17 models -- impressive breadth for proteins
- Limitation: Static benchmark, no temporal gating, no UQ metrics
- Our differentiation: Temporal gating, continuously updated, UQ layer

**CZI Virtual Cells Benchmarking Suite** (2025):
- Strong community backing (42 institutions)
- Limitation: Single-cell only, six tasks, no temporal gating
- Our differentiation: Cross-modal, temporal gating, UQ evaluation
- **Potential synergy:** Could integrate CZI tasks into single-cell module

**TDC (Therapeutics Data Commons):**
- Already supports temporal splits for drug-target tasks
- Limitation: Molecule-focused, no FM evaluation framework, UQ not required
- Our differentiation: FM-specific evaluation, mandatory UQ, cross-modal

### 7.2 Groups Working on Related Problems

**Meta FAIR / EvolutionaryScale:**
- ESM3 (98B parameters) trained with 1 trillion TFLOPs
- Focus: Model development, not benchmark creation
- Released open-source ESM Cambrian embeddings
- No indication of live benchmark development

**DeepMind / Google:**
- AlphaFold3 development, pLDDT confidence scores
- No public live benchmark project
- Could be developing internal evaluation infrastructure

**Chan Zuckerberg Initiative:**
- Active in single-cell benchmarking through Virtual Cells initiative
- Workshop in 2025 identified benchmarking as key need
- Focused on single-cell, not cross-modal

**Microsoft Research:**
- Published zero-shot evaluation of scFMs (Genome Biology, 2025)
- Identified contamination issues
- Not building a continuous benchmark platform

**BioGeometry (GeoFlow V2, 2025):**
- Protein-focused, structure prediction and design
- No cross-modal benchmark efforts

### 7.3 Gap in the Competition Landscape

No group is currently building a **cross-modal, continuously updated, uncertainty-aware**
benchmark for biological foundation models. The closest efforts are:

1. LiveProteinBench: Temporal + protein-only + no UQ
2. CZI: Community + single-cell-only + no temporal gating
3. PFMBench: Comprehensive protein + static + no UQ
4. TDC: Temporal splits + molecule-focused + no FM evaluation

The intersection of ALL four requirements (cross-modal + temporal + continuous +
UQ-aware) is entirely unoccupied.

---

## 8. Feasibility Reassessment

### 8.1 Technical Feasibility: HIGH

**Proven components:**
- Temporal gating: Demonstrated by LiveProteinBench (protein), LiveBench (NLP),
  LiveCodeBench (code). The mechanism is well-understood.
- UQ evaluation: Established metrics (ECE, Brier, conformal coverage). ImmUQBench
  and Greenman et al. provide implementation templates.
- Cross-modal data sources: All proposed sources (UniProt, PDB, ChEMBL, ClinVar,
  CELLxGENE, GEO) have programmatic APIs with temporal metadata.
- FM evaluation: PFMBench, BioLLM, GUE provide task-specific evaluation code.

**Engineering challenges (solvable):**
- Automated pipeline reliability across 8+ data sources
- Handling different update frequencies (weekly to annual)
- Standardizing evaluation across heterogeneous FM architectures
- Managing ~50 GB/quarter of new benchmark data

### 8.2 Scientific Novelty: HIGH

**What has NOT been done:**
1. Cross-modal temporal gating (only protein-only exists)
2. Mandatory UQ evaluation in biological FM benchmarks
3. Cross-modal contamination analysis (each modality studied in isolation)
4. Conformal prediction coverage guarantees for biological FMs
5. Systematic comparison of UQ methods across modalities

**What this enables that is impossible today:**
- Fair comparison of FMs across modalities on truly unseen data
- Identification of which modalities are most contaminated
- Assessment of whether FM confidence is calibrated per modality
- Discovery of cross-modal UQ failure modes (e.g., does a protein FM's confidence
  transfer when applied to molecular tasks?)

### 8.3 Computational Feasibility: HIGH

- Total compute: ~1,550-16,000 GPU-hours/year (H200 equivalent)
- This is ~5-50 GPU-days -- trivial on the described HPC cluster
- Main bottleneck: Engineering, not compute
- Data storage: ~200 GB/year -- negligible

### 8.4 Timeline Feasibility: HIGH

- 5 months for complete system + initial paper
- Can start producing results within 3 months (protein module first)
- Quarterly updates sustainable with <1 person-week/quarter once pipeline is built

### 8.5 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Data source API changes | Medium | High | Redundant scrapers, fallback mechanisms |
| Insufficient post-cutoff data for some tasks | Low | Medium | Adjust task granularity, extend cutoff window |
| Some FMs not publicly available | Medium | Low | Focus on open-source FMs |
| Competing benchmark launches | Low | High | Speed to publication, broader scope |
| UQ metrics not discriminative | Medium | Medium | Include diverse metrics, ablation studies |

---

## 9. Publication Framing

### 9.1 Target Venue

**Primary:** Nature Computational Science

**Secondary:** Nature Methods, Nature Biotechnology

**Rationale:** Nature Computational Science published benchmarking work (AUTOENCODIX,
2025) and methodology papers. A cross-modal evaluation framework addressing
contamination + UQ fits their scope of "computational approaches that transform
scientific inquiry."

### 9.2 Proposed Title

**"LiveBioBench: A Continuously Updated, Uncertainty-Aware Benchmark for Biological
Foundation Models Across Molecular Scales"**

### 9.3 Main Claim

"We present LiveBioBench, the first cross-modal benchmark for biological foundation
models that combines temporal gating to prevent data contamination with mandatory
uncertainty calibration evaluation across proteins, DNA/RNA, small molecules, and
single-cell transcriptomics. Across 40 tasks and N models, we reveal that (1)
contamination inflates reported performance by 15-30% across all modalities, (2) no
current biological FM produces well-calibrated uncertainty estimates, and (3)
cross-modal tasks expose dramatic failure modes invisible to single-modality
benchmarks."

### 9.4 Key Figures

1. **The Contamination Heatmap:** Performance inflation (post-cutoff vs. pre-cutoff) for
   each model x modality combination. Dramatic visual showing contamination is pervasive.

2. **The Calibration Wall:** Reliability diagrams for top 10 FMs across 4 modalities.
   Expected to show systematic overconfidence.

3. **The Cross-Modal Failure Matrix:** Which models fail catastrophically on cross-modal
   tasks despite strong single-modal performance.

4. **UQ Method Comparison Radar:** Spider plots comparing 5+ UQ methods across accuracy,
   calibration, coverage, compute cost, per modality.

5. **Temporal Drift Curves:** How model performance degrades as test data gets further
   from training cutoff, per modality.

6. **Architecture diagram** of the LiveBioBench pipeline and update mechanism.

### 9.5 Anticipated Reviewer Concerns

| Concern | Response |
|---------|----------|
| "Is this just engineering, not science?" | Novel contamination and calibration analysis produces scientific insights about FM generalization. Cross-modal analysis reveals new failure modes. |
| "Sample sizes are small for some tasks" | Temporal gating inherently limits test set size. We show statistical power is sufficient and grows each quarter. |
| "Why not evaluate more models?" | Open-source focus ensures reproducibility. Commercial API models included where accessible. |
| "UQ overhead makes this impractical" | Conformal prediction is post-hoc with negligible cost. We provide compute budgets for all methods. |
| "LiveProteinBench already exists" | We extend beyond proteins to 4 modalities, add specialist FM evaluation, and add mandatory UQ -- fundamentally different scope. |

### 9.6 Comparison Baselines

- LiveProteinBench (temporal protein-only, no UQ)
- PFMBench (static protein-only, no UQ)
- TDC (temporal molecule-only, no UQ)
- FLIP (static protein engineering, limited UQ)
- GUE (static genomics, no UQ)
- BioLLM (static single-cell, no UQ)

---

## References

1. Rongdingyi et al. (2025). "LiveProteinBench: A Contamination-Free Benchmark for
   Assessing Models' Specialized Capabilities in Protein Science." arXiv:2512.22257.

2. Hermann, Fiedler et al. (2024). "Beware of Data Leakage from Protein LLM
   Pretraining." Proceedings of Machine Learning Research, 261.

3. Greenman KP, Amini AP, Yang KK (2025). "Benchmarking uncertainty quantification
   for protein engineering." PLOS Computational Biology 21(1): e1012639.

4. Alifbinabdulqayyum et al. (2025). "ImmUQBench: A Benchmark on Uncertainty
   Quantification of Protein Immunogenicity Prediction." Oxford Open Immunology;
   NeurIPS 2025.

5. Ahlmann-Eltze C, Huber W, Anders S (2025). "Deep-learning-based gene perturbation
   effect prediction does not yet outperform simple linear baselines." Nature Methods
   22: 1657-1661.

6. Kedzierska K, Crawford L et al. (2025). "Zero-shot evaluation reveals limitations
   of single-cell foundation models." Genome Biology 26: 99.

7. BioMol-LLM-Bench (2026). "The limits of bio-molecular modeling with large language
   models: a cross-scale evaluation." arXiv:2604.03361.

8. Zhou Z, Ji Y (2024). "DNABERT-2: Efficient Foundation Model and Benchmark For
   Multi-Species Genomes." ICLR 2024.

9. Dalla-Torre H et al. (2024). "Nucleotide Transformer: building and evaluating
   robust foundation models for human genomics." Nature Methods 21: 2448-2456.

10. Nature Communications (2025). "Benchmarking DNA foundation models for genomic and
    genetic tasks."

11. Liu et al. (2025). "BioLLM: A standardized framework for integrating and
    benchmarking single-cell foundation models." Patterns.

12. CZI Virtual Cells Workshop (2025). "Benchmarking and Evaluation of AI Models in
    Biology: Outcomes and Recommendations." arXiv:2507.10502.

13. PFMBench (2025). "PFMBench: Protein Foundation Model Benchmark." arXiv:2506.14796.

14. Shen, Xue et al. (2024). "ProteinBench: A Holistic Evaluation of Protein
    Foundation Models." arXiv:2409.06744.

15. White et al. (2024). "LiveBench: A Challenging, Contamination-Free LLM Benchmark."
    ICLR 2025 Spotlight. arXiv:2406.19314.

16. Jain N et al. (2024). "LiveCodeBench: Holistic and Contamination Free Evaluation
    of Large Language Models for Code." arXiv:2403.07974.

17. Revealing data leakage in protein interaction benchmarks (2024). ICLR 2024 GEM
    Workshop. arXiv:2404.10457.

18. "Confidence Without Verification: Screening pLDDT Unreliability in AlphaFold2
    Fold-Switching Predictions." bioRxiv:2026.02.19.706878.

19. "Flexibility or uncertainty? A critical assessment of AlphaFold 2 pLDDT."
    Structure (2025).

20. TDC: Therapeutics Data Commons (Zitnik Lab, Harvard). tdcommons.ai.

21. Soleimany et al. (2022). "Evidential Deep Learning for Guided Molecular Property
    Prediction and Discovery." ACS Central Science 7(8): 1356-1367.

22. EviDTI (2025). "Evidential deep learning-based drug-target interaction prediction."
    Nature Communications.

23. UQ for protein-ligand binding (2025). "Uncertainty quantification enables reliable
    deep learning for protein-ligand binding affinity prediction." Scientific Reports.

24. Liu J, Duvenaud D, Paisley J (2020). "Simple and Principled Uncertainty Estimation
    with Deterministic Deep Learning via Distance Awareness." arXiv:2006.10108.
    (SNGP method.)

25. TUnA (2024). "TUnA: an uncertainty-aware transformer model for sequence-based
    protein-protein interaction prediction." Briefings in Bioinformatics.

26. Watson et al. (2025). "Functional protein mining with conformal guarantees."
    Nature Communications.

27. Fink et al. (2024). "Leveraging conformal prediction to annotate enzyme function
    space with limited false positives." PLOS Computational Biology.

28. Luo et al. (2024). "Conformal Prediction Under Feedback Covariate Shift for
    Biomolecular Design." PNAS.

29. LucaOne (2025). "Generalized biological foundation model with unified nucleic
    acid and protein language." Nature Machine Intelligence.

30. Rethinking Text-based Protein Understanding (2025). arXiv:2505.20354.

31. BixBench (2025). "BixBench: a Comprehensive Benchmark for LLM-based Agents in
    Computational Biology." arXiv:2503.00096.

32. Milestone: >20,000 Structures Deposited to the PDB in 2025. RCSB PDB News.

33. UniProt Consortium (2025). "UniProt: the Universal Protein Knowledgebase in 2025."
    Nucleic Acids Research 53(D1): D609.

34. ChEMBL Database (2023). "ChEMBL Database in 2023: a drug discovery platform
    spanning multiple bioactivity data types and time periods." Nucleic Acids Research
    52(D1): D1180.

35. "Importance of updated benchmark sets for statistically correct AlphaFold
    applications." bioRxiv (2024).

36. "A flaw in using pretrained protein language models in protein-protein interaction
    inference models." Nature Machine Intelligence (2025).

37. Conformal prediction for uncertainty quantification in dynamic biological systems
    (2025). PLOS Computational Biology.

38. "Reliable machine learning models in genomic medicine using conformal prediction."
    Frontiers in Bioinformatics (2025).
