---
agent: aiml
round: 1
date: 2026-04-14
type: gap-report
---

# AI/ML Methods for Biology -- Round 1 Gap Reports

**Reporting Agent:** Dr. AI/ML Methods for Biology Expert (aiml)
**Perspective:** Maverick AI/ML Expert -- Methods-first thinker grounded in biology

This document contains 4 gap reports covering methodological and evaluation gaps at the intersection of machine learning and computational biology. Each gap was identified through extensive literature review of 2024--2026 publications, benchmark analyses, and community discussions from NeurIPS, ICML, and ICLR proceedings.

---

# Gap 1: The Cross-Scale Foundation Model Integration Problem -- No Unified Framework Bridges Molecular, Cellular, and Tissue-Level Biological Predictions

---
gap_id: cross-scale-fm-integration
---

## Reporting Agent
Dr. AI/ML Methods for Biology Expert (aiml) -- Maverick Track

## Gap Description

### What Is Missing

There is no foundation model or principled framework that coherently bridges predictions across biological scales -- from molecules (proteins, small molecules, DNA sequences) through cells (transcriptomes, epigenomes) to tissues and organisms. The field has produced strong scale-specific foundation models: ESM-2/ESM3 for proteins (Lin et al., 2023; Hayes et al., 2025), Evo/Evo-2 for DNA (Nguyen et al., 2024; Arc Institute, 2025), scGPT/Geneformer for single cells (Cui et al., 2024; Theodoris et al., 2023), and Nicheformer for spatial transcriptomics (Schaar et al., 2025). But these models exist as isolated silos. A mutation in a protein sequence has downstream consequences for cellular phenotype and tissue function, yet no model can trace this causal chain computationally.

The fundamental challenge is that biological information flows across scales through complex, non-linear interactions: a single nucleotide variant alters protein structure, which changes binding affinity, which rewires a signaling network, which shifts cellular state, which manifests as a tissue-level phenotype. Current models capture at most one or two links in this chain.

### Current State of the Art

The state of the art for cross-scale integration is nascent and fragmented:

- **Xpressor** (Sapoval et al., 2025, bioRxiv) represents the first explicit attempt at cross-scale biological foundation modeling. It uses a cross-attention mechanism to compress gene-level protein representations into cell-state vectors, achieving +12% improvement in cell-type prediction and +8% in embedding quality when bridging protein-to-cell scales. However, it only connects two scales (protein to cell) and has been validated on limited tasks.

- **PULSAR** (Liang et al., 2025, bioRxiv) is a multi-scale, multi-cellular foundation model that attempts to integrate molecular and cellular information, but primarily operates at the cell-to-tissue interface rather than the molecule-to-organism continuum.

- **AIDO** (Carnegie Mellon, 2025) proposes a "digital organism" system of multi-scale foundation models but remains a conceptual framework without unified training or benchmarking.

- **Compositional Foundation Models (CFMs)** have been proposed as an architectural paradigm (Cell Systems, 2026) that fuses frozen unimodal experts via learned interfaces. The Synergistic Information Score (SIS) has been introduced to quantify cross-modal information gain, but the approach has not been demonstrated across more than two modalities.

- **Multimodal approaches in Nature** (Bunne et al., 2025) envision models pretrained on genomics, transcriptomics, epigenomics, proteomics, metabolomics, and spatial profiling, but acknowledge that the lack of large-scale paired data across modalities prohibits joint training.

### Evidence the Gap Exists

1. **Siloed model development:** A comprehensive review in National Science Review (Gao et al., 2025) cataloged foundation models across 4 biological scales (molecule, chain, cell, tissue) and explicitly noted that "these models do not yet bridge these scales."

2. **The paired data bottleneck:** Unimodal datasets are abundant (e.g., 104 million single-cell transcriptomes for Geneformer; 9 trillion DNA bases for Evo-2), but high-quality measurements spanning multiple scales on the same biological samples are scarce (Bunne et al., Nature 2025).

3. **Compositional model limitations:** Research by the CZ Biohub (bioRxiv, 2026) showed that simple alignment of modality-specific models propagates redundant structure while suppressing modality-specific signal. Their SIS metric revealed that many "multimodal" approaches fail to achieve synergistic information gain beyond what each modality provides independently.

4. **Benchmarking absence:** PFMBench (Gong et al., 2025, AAAI) spans 38 tasks across 8 categories for protein foundation models but does not include any cross-scale tasks. No benchmark evaluates whether a model's understanding of protein structure improves its predictions at the cellular or tissue level.

5. **Scaling laws are scale-specific:** While scaling laws have been demonstrated for single-cell models (up to 27B parameters, bioRxiv 2025) and protein models (ESM2 series up to 15B), no one has studied whether scale-specific scaling laws compose when models are integrated.

## Why This Gap Matters

### Scientific Importance

Biology operates across scales. Understanding how molecular events propagate to cellular and organismal phenotypes is arguably the central question of modern biology. Without cross-scale computational models, we cannot:
- Predict how a drug binding a protein target will alter cellular networks
- Understand how genetic variants in regulatory elements affect tissue-level phenotypes
- Model disease mechanisms that span molecular dysfunction to clinical presentation

### Practical Impact

Drug discovery loses billions annually because molecular-level binding predictions fail to translate to cellular efficacy. Precision medicine requires connecting patient genotypes (DNA scale) to molecular mechanisms (protein scale) to treatment response (cellular/tissue scale). A cross-scale framework would enable end-to-end in silico modeling from variant to phenotype.

### Publication Potential

This directly targets Nature Computational Science or Nature Methods. The 2025 Nature perspective "Towards multimodal foundation models in molecular cell biology" (Bunne et al.) explicitly calls for this type of work. A systematic study establishing (a) when cross-scale integration helps, (b) what architectures enable it, and (c) a benchmark for evaluating it would be a landmark contribution.

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

A two-part contribution:

1. **Cross-Scale Biological Benchmark (CrossBioBench):** A benchmark suite that evaluates models on tasks requiring information flow across scales. Example tasks: predicting cellular phenotype changes from protein mutations; predicting tissue-level gene expression changes from regulatory variant effects; predicting drug response from molecular binding + cellular network context. This would require curating datasets where the same perturbation is measured at multiple biological scales.

2. **Cross-Scale Integration Architecture Study:** Systematically compare approaches for bridging scale-specific foundation models: (a) feature concatenation, (b) cross-attention adapters (Xpressor-style), (c) compositional FMs with frozen experts, (d) end-to-end multi-scale pretraining, (e) retrieval-augmented cross-scale prediction. Evaluate on CrossBioBench.

### Required Data

- Protein mutation effects measured at both molecular (binding, stability) and cellular (fitness, expression) levels -- available from ProteinGym + matched DMS datasets
- Genetic variant effects measured at DNA, RNA expression, and phenotype levels -- available from ENCODE, GTEx, ClinVar
- Drug perturbation data with molecular target information + cellular transcriptomic response -- available from LINCS L1000, scPerturb
- Spatial transcriptomics datasets with matched single-cell and bulk data -- available from HuBMAP, Nicheformer corpus

### Required Compute

- Fine-tuning and adapter training for multiple large foundation models (ESM-2 650M, Evo-2 7B/40B, scGPT, Geneformer): H200 GPUs, estimated 2,000--4,000 GPU-hours total
- Benchmark evaluation across hundreds of cross-scale task configurations: 500--1,000 GPU-hours
- Feasible on HPC cluster with H200/B200 GPUs

### Required Methods

- Cross-attention adapter architectures
- Contrastive learning for cross-scale alignment
- Scaling law analysis methodology
- Benchmark design principles (contamination-free evaluation, proper data splitting)

## Feasibility Assessment

### Technical Feasibility (Rating: Medium)
Cross-scale integration is architecturally straightforward (cross-attention, adapter layers) but curating meaningful cross-scale evaluation tasks with proper ground truth is challenging. The existence of Xpressor and PULSAR as proof-of-concepts supports feasibility.

### Timeline Feasibility (Rating: Medium)
Benchmark curation: 2--3 months. Architecture comparison study: 2--3 months. Total: 4--6 months is tight but feasible if the benchmark scope is focused on 2--3 scale bridges rather than all possible combinations.

### Wet Lab Independence (Rating: High)
All proposed data sources are publicly available. No wet-lab validation needed -- the benchmark evaluates computational predictions against existing multi-scale measurements.

## Competitive Landscape

### Who Else Might Fill This Gap
- **Arc Institute / Evo team:** Have the models (Evo-2) and could extend to cross-scale, but their focus is on DNA-centric generation
- **Chan Zuckerberg Initiative / Biohub:** Actively pursuing virtual cell models but focused more on infrastructure than systematic benchmarking
- **Meta AI (FAIR):** ESM team could extend protein models upward, but have shown no interest in cross-scale work
- **Helmholtz Munich (Fabian Theis lab):** Leaders in single-cell FMs but primarily within-scale

### Risk of Being Scooped
Medium. The community is aware of this gap (multiple perspective papers call for it), but no one has produced a rigorous benchmark or systematic comparison. The benchmark contribution is defensible because it requires deep curation expertise.

### Differentiation
A benchmark-first approach (rather than model-first) is the key differentiator. The field has too many models and too few evaluations. A CrossBioBench that becomes the standard evaluation suite would have outsized impact.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 8 | Xpressor is the only prior work; systematic benchmarking is entirely new |
| Scientific impact | 9 | Addresses a fundamental question about biological information flow |
| Feasibility (computational only) | 6 | Data curation across scales is challenging; compute is feasible |
| Timeline (summer 2026) | 6 | Tight but achievable with focused scope |
| Publication potential (Nat Comp Sci) | 9 | Multiple Nature papers have called for exactly this work |
| **Overall** | **7.6** | High impact, medium feasibility -- the benchmark alone would be a major contribution |

## References

1. Lin, Z. et al. (2023). Evolutionary-scale prediction of atomic-level protein structure with a language model. Science, 379(6637), 1123-1130.
2. Hayes, T. et al. (2025). Simulating 500 million years of evolution with a language model. Science, 387(6741).
3. Nguyen, E. et al. (2024). Sequence modeling and design from molecular to genome scale with Evo. Science, 386(6723).
4. Arc Institute. (2025/2026). Genome modelling and design across all domains of life with Evo 2. Nature.
5. Cui, H. et al. (2024). scGPT: toward building a foundation model for single-cell multi-omics using generative AI. Nature Methods, 21, 1470-1480.
6. Theodoris, C.V. et al. (2023). Transfer learning enables predictions in network biology. Nature, 618, 616-624.
7. Schaar, A.C. et al. (2025). Nicheformer: a foundation model for single-cell and spatial omics. Nature Methods.
8. Sapoval, N. et al. (2025). Towards foundation models that learn across biological scales. bioRxiv.
9. Liang, Y. et al. (2025). PULSAR: a Foundation Model for Multi-scale and Multicellular Biology. bioRxiv.
10. Gao, Z. et al. (2025). Foundation models in bioinformatics. National Science Review, 12(4).
11. Bunne, C. et al. (2025). Towards multimodal foundation models in molecular cell biology. Nature.
12. Gong, X. et al. (2025). PFMBench: Protein Foundation Model Benchmark. AAAI.
13. CZ Biohub. (2026). Beyond alignment: synergistic integration is required for multimodal cell foundation models. bioRxiv.
14. Cell Systems Editorial. (2026). From modality-specific to compositional foundation models for cell biology. Cell Systems.
15. Xing, E.P. et al. (2025). Toward AI-Driven Digital Organism: A System of Multiscale Foundation Models. CMU Technical Report.

---

# Gap 2: The Perturbation Prediction Crisis -- Deep Learning Fails to Beat Linear Baselines, Exposing a Fundamental Evaluation and Modeling Gap

---
gap_id: perturbation-prediction-crisis
---

## Reporting Agent
Dr. AI/ML Methods for Biology Expert (aiml) -- Maverick Track

## Gap Description

### What Is Missing

The field of single-cell perturbation response prediction is in methodological crisis. Despite years of increasingly sophisticated deep learning approaches -- including graph neural networks (GEARS), variational autoencoders (CPA, SAMS-VAE), and foundation model adaptations (scGPT, scFoundation) -- a landmark Nature Methods paper in 2025 demonstrated that none of these methods outperform deliberately simple linear baselines for predicting transcriptomic changes after gene perturbations (Ahlmann-Eltze, Huber & Anders, 2025).

What is missing is threefold:

1. **A rigorous, non-gameable evaluation framework** that measures biologically meaningful prediction accuracy rather than metrics that can be inflated by predicting the average response
2. **Models that capture the heterogeneous, non-linear aspects of perturbation responses** that linear models provably cannot
3. **An understanding of when and why complexity helps** -- the conditions under which deep learning provides genuine value over simple baselines for biological perturbation prediction

### Current State of the Art

The perturbation prediction landscape is crowded but underperforming:

- **GEARS** (Roohani et al., 2023): Graph-based approach using gene interaction networks. Initially showed promise for combinatorial perturbation prediction but has been shown to fail at generalization.

- **CPA** (Lotfollahi et al., 2023): Compositional Perturbation Autoencoder. Designed for combinatorial chemical + genetic perturbations but performance degrades significantly on out-of-distribution conditions.

- **scGPT and scFoundation** adaptations: Fine-tuned foundation models for perturbation tasks. Despite massive pretraining, they do not outperform linear baselines on standard benchmarks (Ahlmann-Eltze et al., 2025).

- **PerturBench** (NeurIPS 2024): Benchmarked multiple ML models for cellular perturbation analysis across tasks including perturbation response prediction, combinatorial perturbation response prediction, and drug-dose response prediction.

- **scPerturBench** (Nature Methods, 2025): Comprehensive benchmark of 27 methods across 29 datasets with 6 metrics. Found that recommendations depend heavily on evaluation setup.

- **PerturbNet** (2025): Claims to predict single-cell responses to unseen chemical and genetic perturbations but has been contested.

- **Linear baselines:** The 2025 Nature Methods paper showed that a simple linear model (predicting perturbation effects as a linear combination of known single-gene effects) matches or exceeds all tested deep learning approaches.

### Evidence the Gap Exists

1. **The linear baseline paper (Ahlmann-Eltze et al., Nature Methods, 2025):** Compared 5 foundation models and 2 deep learning models against simple baselines. "None of the deep learning models outperformed the baselines." This is the most damning evidence: years of model development have produced no meaningful advance over the simplest possible approach.

2. **Benchmark sensitivity:** scPerturBench (Nature Methods, 2025) showed that the "best" method depends entirely on the evaluation setup, dataset, and metrics chosen. This means the field cannot even reliably rank methods.

3. **Metric gaming:** Many perturbation prediction papers report high correlation with ground truth, but this can be achieved by predicting the mean unperturbed expression and letting the natural variance in perturbation effects generate apparent correlation. The mean-prediction baseline achieves surprisingly high scores on standard metrics.

4. **Combinatorial prediction failure:** For combinatorial perturbations (pairs of gene knockouts), all methods perform dramatically worse. The number of possible pairs grows quadratically while training data covers only a tiny fraction of the combinatorial space.

5. **Counter-evidence debate:** A 2025 bioRxiv preprint "Deep Learning-Based Genetic Perturbation Models Do Outperform Uninformative Baselines on Well-Calibrated Metrics" argues the opposite conclusion, claiming the issue is metric calibration rather than model failure. This active disagreement itself is evidence of a gap -- the field cannot agree on how to measure progress.

## Why This Gap Matters

### Scientific Importance

Perturbation prediction is a gateway technology for computational biology. If we cannot predict how cells respond to genetic or chemical perturbations in silico, we cannot:
- Design CRISPR experiments computationally
- Screen drug candidates without wet-lab experiments
- Build virtual cells (a major community goal, with the 2025 Virtual Cell Challenge focused on this)
- Infer causal gene regulatory networks from observational data

The fact that linear models suffice suggests either: (a) current evaluation methods miss the non-linear signal, or (b) current models do not learn biologically meaningful non-linear relationships. Understanding which is the case is a fundamental question.

### Practical Impact

Drug discovery companies and academic labs are building pipelines around perturbation prediction models. If these models are no better than linear interpolation, billions of dollars of infrastructure investment may be misdirected. A clear, rigorous evaluation framework would redirect effort toward genuinely valuable methods.

### Publication Potential

This is a direct Nature Methods or Nature Computational Science paper. The 2025 linear baseline paper was published in Nature Methods and generated enormous discussion. A definitive follow-up that either (a) designs evaluation metrics that reveal genuine non-linear prediction value or (b) designs models that definitively beat linear baselines on biologically validated tasks would be a landmark contribution.

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

A three-component study:

1. **Evaluation Framework Overhaul:** Design new metrics that specifically measure biologically meaningful non-linear prediction accuracy. This means: (a) subtracting the linear-predictable component of perturbation effects and measuring residual prediction accuracy, (b) evaluating on tasks where linear models provably fail (non-additive combinatorial effects, context-dependent responses), (c) biological validation metrics (do predicted differentially expressed genes match known pathway biology?).

2. **Model Architecture Investigation:** Systematically test whether specific architectural choices (graph structure priors, attention over gene interactions, causal mechanisms, equivariant layers) capture non-linear biology that linear models miss. Use ablation studies to isolate which model components contribute genuine non-linear signal vs. noise fitting.

3. **Data Regime Analysis:** Identify the data characteristics (perturbation types, cell types, sequencing depth, number of perturbations) under which non-linear models begin to outperform linear ones. This may reveal that current benchmarks simply do not contain enough combinatorial perturbation data to test non-linear models fairly.

### Required Data

- Perturb-seq datasets from scPerturb (44 datasets, 32 CRISPR, 9 drug, avg 160K cells per dataset)
- CausalBench data (200,000+ interventional datapoints)
- Combinatorial perturbation datasets (Norman et al., 2019; Replogle et al., 2022)
- All publicly available and already curated

### Required Compute

- Training and evaluating multiple model architectures across dozens of datasets: 1,000--2,000 GPU-hours
- Metric computation and statistical analysis: minimal compute
- Feasible on HPC cluster

### Required Methods

- Linear and non-linear statistical baselines
- Partial information decomposition for separating linear vs. non-linear signal
- Causal inference methods for evaluating prediction quality
- Comprehensive statistical testing framework (multiple seeds, confidence intervals, Bonferroni correction)

## Feasibility Assessment

### Technical Feasibility (Rating: High)
All data, methods, and models are publicly available. The main challenge is designing metrics that are truly informative, which is a conceptual challenge rather than a technical one.

### Timeline Feasibility (Rating: High)
Metric design: 1--2 months. Systematic evaluation: 2--3 months. Analysis and writing: 1--2 months. Total: 4--6 months.

### Wet Lab Independence (Rating: High)
Entirely computational. Uses existing publicly available perturbation datasets. Biological validation uses known pathway annotations and gene function databases.

## Competitive Landscape

### Who Else Might Fill This Gap
- **Ahlmann-Eltze, Huber, Anders:** They published the linear baseline paper and could follow up, but their work was a critique, not a constructive framework
- **scPerturBench team (Tongji Univ.):** Have the benchmark infrastructure but focused on ranking existing methods, not redesigning evaluation
- **Theis Lab (Helmholtz Munich):** CPA/scGen developers but invested in model development, not critical evaluation
- **GEARS team (Stanford):** Could defend their approach but likely focused on next-gen models

### Risk of Being Scooped
Medium-high. The linear baseline paper has created intense community discussion. Multiple groups are likely working on responses. Speed matters.

### Differentiation
The key insight is that this is an evaluation methodology problem, not just a model development problem. A paper that provides definitive evidence about when and why non-linear models help (or don't) would be more impactful than yet another model.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 7 | Builds on recent critique but takes it to definitive resolution |
| Scientific impact | 9 | Resolves a fundamental question about perturbation modeling |
| Feasibility (computational only) | 9 | All data and methods exist; primarily conceptual/analytical work |
| Timeline (summer 2026) | 9 | Highly achievable with focused effort |
| Publication potential (Nat Comp Sci) | 8 | Direct follow-up to a Nature Methods paper; resolves an active controversy |
| **Overall** | **8.4** | High impact and high feasibility -- the best risk/reward ratio |

## References

1. Ahlmann-Eltze, C., Huber, W. & Anders, S. (2025). Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines. Nature Methods.
2. Roohani, Y., Huang, K. & Leskovec, J. (2023). Predicting transcriptional outcomes of novel multigene perturbations with GEARS. Nature Biotechnology, 42, 927-935.
3. Lotfollahi, M. et al. (2023). Predicting cellular responses to complex perturbations in high-throughput screens. Molecular Systems Biology.
4. Cui, H. et al. (2024). scGPT: toward building a foundation model for single-cell multi-omics using generative AI. Nature Methods.
5. Chevalley, M. et al. (2025). CausalBench: A Large-scale Benchmark for Network Inference from Single-cell Perturbation Data. Communications Biology.
6. Liu, Y. et al. (2025). scPerturBench: Benchmarking algorithms for generalizable single-cell perturbation response prediction. Nature Methods.
7. Norman, T.M. et al. (2019). Exploring genetic interaction manifolds constructed from rich single-cell phenotypes. Science, 365(6455), 786-793.
8. Replogle, J.M. et al. (2022). Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq. Cell, 185(14), 2559-2575.
9. Ji, Y. et al. (2024). PerturBench: Benchmarking Machine Learning Models for Cellular Perturbation Analysis. NeurIPS Datasets and Benchmarks.
10. Bereket, M. & Karaletsos, T. (2025). Deep Learning-Based Genetic Perturbation Models Do Outperform Uninformative Baselines on Well-Calibrated Metrics. bioRxiv.

---

# Gap 3: The Biological Foundation Model Evaluation Crisis -- Contamination, Metric Gaming, and the Absence of Temporally-Controlled Live Benchmarks

---
gap_id: fm-evaluation-crisis
---

## Reporting Agent
Dr. AI/ML Methods for Biology Expert (aiml) -- Maverick Track

## Gap Description

### What Is Missing

The field of biological foundation models lacks a principled, contamination-free, continuously-updated evaluation ecosystem. Current benchmarks suffer from three interconnected problems:

1. **Data contamination:** Foundation models are trained on massive biological databases (UniProt, PDB, GenBank) that overlap extensively with test sets of existing benchmarks. LiveProteinBench (2025) demonstrated that pre-2025 protein benchmarks are contaminated for any model trained on UniProt data released before January 2025.

2. **Metric gaming and saturation:** Standard benchmarks like MoleculeNet, TDC subsets, and MMLU biology sections are approaching saturation, with top models separated by fractions of a percentage point that fall within measurement noise (RAND Corporation, 2025; benchmark saturation study, 2026). LAB-Bench, designed as a challenging biology benchmark, already shows near-saturation on several subcategories.

3. **Missing modality coverage:** PFMBench (2025) showed that multimodal protein foundation models are "understudied in existing benchmarks, despite the field's rapid shift toward models that integrate sequence, structure, and functional data." Similarly, no benchmark evaluates DNA foundation models on their ability to predict functional consequences of variants across regulatory, coding, and non-coding regions in a unified manner.

What is fundamentally missing is a **live, continuously-updated, contamination-controlled benchmark ecosystem** for biological foundation models that (a) uses temporally gated data, (b) evaluates across biological modalities and scales, (c) measures biologically meaningful capabilities rather than pattern matching, and (d) evolves as models improve.

### Current State of the Art

**Protein benchmarks:**
- **ProteinGym** (Notin et al., 2023): 217 DMS assays for variant effect prediction. Widely used but training data contamination is a growing concern, especially for models pretrained on UniProt.
- **PFMBench** (Gong et al., 2025): 38 tasks, 17 models, 8 categories. Most comprehensive protein FM benchmark but static -- data can leak into future model training.
- **LiveProteinBench** (2025): First contamination-free protein benchmark using post-January 2025 UniProt releases. Found that general-purpose LLMs outperform domain-specific protein models by >20% accuracy in zero-shot settings, contradicting the narrative that domain pretraining always helps.

**Genomic benchmarks:**
- **Genomic benchmarks for DNA FMs** (Nature Communications, 2025): Evaluated DNABERT-2, NT-v2, HyenaDNA, Caduceus, GROVER across classification, expression, and variant tasks. DNABERT-2 outperformed others by 3.6--5.9% AUC on human tasks, but general-purpose DNA FMs were less effective than specialized models for expression prediction and QTL identification.
- **No live genomic benchmark exists.**

**Single-cell benchmarks:**
- **Zero-shot evaluation** (Genome Biology, 2025, Kedzierska et al.): scGPT and Geneformer perform worse than selecting HVGs + Harmony/scVI for cell type clustering in zero-shot settings.
- **BioLLM** (2025): Standardized framework for benchmarking single-cell FMs, but static.

**Molecular benchmarks:**
- **MoleculeNet** (Wu et al., 2018): Widely used but aging; known data leakage issues.
- **TDC** (Huang et al., 2022): 66 datasets, 22 tasks, 29 leaderboards. More comprehensive but still static.
- **NovoExpert-2** (2025): Achieves SOTA on 5 TDC ADMET endpoints using gradient-boosted trees + GIN embeddings -- notably, not a foundation model approach.

### Evidence the Gap Exists

1. **LiveProteinBench's existence is evidence:** The fact that a contamination-free benchmark needed to be created in late 2025 confirms that prior benchmarks are contaminated. LiveProteinBench found that "current benchmarks suffer from critical deficiencies, such as data contamination due to outdated test sets."

2. **Benchmark saturation is documented:** A 2026 systematic study found that "many publicly available biology and chemistry benchmarks are at or approaching saturation." LAB-Bench already shows near-saturation on several subcategories (LABBench2, 2026).

3. **Metric-benchmark mismatch:** The DNA foundation model benchmark (Nature Communications, 2025) found that model rankings depend heavily on task type. DNABERT-2 wins on human classification tasks; NT-v2 wins on epigenetic tasks; HyenaDNA wins on long-sequence tasks. No single evaluation captures overall capability.

4. **Reproducibility crisis in biological ML:** A comprehensive survey found that "for 16 identical training runs for a popular deep learning network, accuracy ranged from 8.6% to 99.0% -- a difference of 90.4% across runs" (AI Magazine, 2025). This variance dwarfs reported improvements between methods.

5. **Foundation model transparency gaps:** The 2025 Foundation Model Transparency Index revealed significant gaps in model documentation, data provenance, and evaluation methodology across biological foundation models.

6. **The protein scaling wall:** Analysis by Notin (2025) showed that "scaling protein language models does not seem to help beyond 1-4B parameters" for mutation effect prediction. If benchmarks cannot detect genuine capability differences as models scale, the field cannot make progress.

## Why This Gap Matters

### Scientific Importance

Without reliable evaluation, the field cannot distinguish genuine progress from noise. The current situation is analogous to drug development without clinical trials -- we are building increasingly expensive models without knowing if they work. The reproducibility crisis (90.4% accuracy variance across identical runs) makes published comparisons unreliable.

### Practical Impact

Benchmark-driven development is the engine of ML progress. When benchmarks are flawed, development effort is misdirected. The NovoExpert-2 result -- where gradient-boosted trees beat foundation models on TDC ADMET benchmarks -- suggests that enormous pretraining compute may be wasted on tasks where simpler methods suffice. A reliable evaluation ecosystem would redirect compute investment to genuinely valuable tasks.

### Publication Potential

Benchmark and evaluation papers have enormous impact in computational biology. ProteinGym (Notin et al., 2023) has 500+ citations. TDC (Huang et al., 2022) has 800+ citations. scPerturb has shaped the perturbation prediction field. A live, contamination-free, cross-modal benchmark ecosystem for biological foundation models would be highly cited and influential. Nature Methods or Nature Computational Science are appropriate venues.

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

**LiveBioBench:** A continuously-updated, contamination-controlled benchmark ecosystem for biological foundation models.

Core design principles:
1. **Temporal gating:** All test data comes from entries added to public databases after a fixed cutoff date (e.g., January 2026). Test sets are refreshed quarterly with newly deposited data.
2. **Cross-modal evaluation:** Tasks span DNA sequences, protein structures, single-cell transcriptomes, and molecular properties -- evaluating whether pretraining on one modality helps another.
3. **Biologically grounded metrics:** Beyond standard ML metrics (AUROC, Spearman rho), include biological validation metrics: pathway enrichment consistency, gene ontology agreement, known mechanism recovery.
4. **Anti-gaming measures:** (a) Hidden held-out test sets submitted to an evaluation server, (b) multiple random splits with reported variance, (c) mandatory reporting of computational cost per prediction, (d) comparison against deliberately simple baselines.
5. **Scaling analysis:** For each task, report performance as a function of model size, pretraining data size, and fine-tuning data size -- enabling community-wide scaling law analysis.

### Required Data

- Newly deposited UniProt/PDB entries (post-January 2026) for protein tasks
- New ENCODE/Roadmap Epigenomics releases for genomic tasks
- New scRNA-seq datasets deposited to GEO/CELLxGENE for single-cell tasks
- New compound assay data from ChEMBL releases for molecular tasks
- All publicly available by design

### Required Compute

- Benchmark construction and curation: minimal compute
- Running all baseline models for initial leaderboard: 2,000--5,000 GPU-hours
- Infrastructure for evaluation server: standard cloud compute
- Feasible on HPC cluster

### Required Methods

- Temporal data splitting methodology
- Contamination detection algorithms
- Cross-modal task design
- Statistical evaluation framework with proper multiple comparison correction
- Online leaderboard infrastructure

## Feasibility Assessment

### Technical Feasibility (Rating: High)
LiveProteinBench has proven the temporal gating approach is feasible for proteins. Extending to other modalities requires curation effort but no novel technical challenges.

### Timeline Feasibility (Rating: Medium)
Initial version with 2--3 modalities and 15--20 tasks: 3--4 months. Full ecosystem with evaluation server: 5--6 months. An MVP focusing on protein + genomics could be done in 3 months.

### Wet Lab Independence (Rating: High)
Entirely computational. Uses publicly deposited experimental data. The benchmark measures computational prediction accuracy, not experimental outcomes.

## Competitive Landscape

### Who Else Might Fill This Gap
- **LiveProteinBench team:** Could extend to other modalities but their current scope is protein-only
- **TDC team (Harvard/Zitnik Lab):** Could evolve TDC into a live benchmark but have shown no movement in this direction
- **ProteinGym maintainers:** Could add temporal gating but focused on variant effect prediction only
- **NeurIPS D&B Track community:** Individual benchmark papers appear each year but lack the unified, live ecosystem

### Risk of Being Scooped
Medium. LiveProteinBench shows the concept is emerging but no group has proposed a cross-modal live benchmark. The scope advantage (spanning protein, DNA, single-cell, molecules) provides defensibility.

### Differentiation
The key differentiator is unification: a single benchmark ecosystem that enables cross-modal evaluation and temporal contamination control across biological domains. Existing benchmarks are siloed by modality.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 8 | LiveProteinBench covers proteins only; cross-modal live benchmarking is new |
| Scientific impact | 9 | Reliable evaluation is a prerequisite for scientific progress |
| Feasibility (computational only) | 8 | Proven feasible for proteins; extension requires curation not invention |
| Timeline (summer 2026) | 7 | MVP feasible; full ecosystem needs longer |
| Publication potential (Nat Comp Sci) | 9 | Benchmark papers in this space are among the most cited |
| **Overall** | **8.2** | High impact across all dimensions; the community desperately needs this |

## References

1. LiveProteinBench. (2025). A Contamination-Free Benchmark for Assessing Models' Specialized Capabilities in Protein Science. arXiv:2512.22257.
2. Notin, P. et al. (2023). ProteinGym: Large-Scale Benchmarks for Protein Fitness Prediction and Design. NeurIPS.
3. Gong, X. et al. (2025). PFMBench: Protein Foundation Model Benchmark. AAAI.
4. Wu, Z. et al. (2018). MoleculeNet: a benchmark for molecular machine learning. Chemical Science.
5. Huang, K. et al. (2022). Therapeutics Data Commons: Machine Learning Datasets and Tasks for Drug Discovery and Development. NeurIPS D&B.
6. Kedzierska, K. et al. (2025). Zero-shot evaluation reveals limitations of single-cell foundation models. Genome Biology.
7. Nature Communications. (2025). Benchmarking DNA foundation models for genomic and genetic tasks.
8. Notin, P. (2025). Have We Hit the Scaling Wall for Protein Language Models? Substack analysis.
9. Semmelrock, E. et al. (2025). Reproducibility in machine-learning-based research: Overview, barriers, and drivers. AI Magazine.
10. RAND Corporation. (2025). Toward Comprehensive Benchmarking of the Biological Knowledge of Frontier Large Language Models.
11. Foundation Model Transparency Index. (2025). arXiv:2512.10169.
12. LABBench2. (2026). An Improved Benchmark for AI Systems Performing Biology Research. arXiv.
13. ChemRxiv. (2025). NovoExpert-2: State-of-the-Art ADMET Prediction via Gradient-Boosted Trees.
14. CZI Blog. (2025). Accelerating AI in Biology With Community-Driven Benchmarks.

---

# Gap 4: Uncertainty-Aware Biological Foundation Models -- The Missing Layer Between Prediction and Decision

---
gap_id: uncertainty-aware-bio-fm
---

## Reporting Agent
Dr. AI/ML Methods for Biology Expert (aiml) -- Maverick Track

## Gap Description

### What Is Missing

Biological foundation models produce point predictions without calibrated uncertainty estimates, yet nearly every downstream use case -- from drug prioritization to variant pathogenicity classification to clinical decision support -- requires knowing how much to trust a prediction. The field has developed impressive prediction machinery but has almost entirely neglected the question of prediction reliability.

What is specifically missing:

1. **Calibrated uncertainty for foundation model outputs:** ESM-2 predicts mutation effects with Spearman correlations of 0.4--0.5 on ProteinGym, but provides no indication of which predictions are reliable and which are noise. Drug designers cannot distinguish a confidently-predicted deleterious mutation from a low-confidence guess.

2. **Uncertainty-aware benchmarking:** Existing benchmarks (ProteinGym, TDC, scPerturb) evaluate only prediction accuracy, not prediction reliability. A model that is 80% accurate with calibrated confidence intervals is far more useful than a model that is 82% accurate but overconfident.

3. **Decision-theoretic framework:** Even where uncertainty methods exist, there is no framework for translating biological prediction uncertainty into actionable decisions (e.g., "this drug candidate is worth testing because the model is confident" vs. "this candidate needs additional computational validation because uncertainty is high").

### Current State of the Art

**Protein UQ benchmarking:**
- A comprehensive 2025 study (PLOS Computational Biology) benchmarked UQ methods on protein engineering tasks from FLIP. Key finding: "there is no single best UQ method across all datasets, splits, and metrics, and uncertainty-based sampling is often unable to outperform greedy sampling in Bayesian optimization." This means current UQ methods do not improve experimental design.

- For protein-ligand binding affinity, a 2025 Scientific Reports study compared 5 UQ methods (Deep Ensemble, MC Dropout, Laplace, Bayes by Backprop, Evidential Neural Networks). Bayes by Backprop was applied for the first time in this domain, suggesting the space is underexplored.

- ImmUQBench (2025) benchmarked UQ for protein immunogenicity prediction, finding that "protein language models and deep learning models often exhibit overconfident predictions and are prone to generating hallucinated outputs."

**Single-cell and genomics UQ:**
- Virtually absent. scGPT and Geneformer provide no built-in uncertainty estimates. No benchmark evaluates single-cell foundation model calibration.

**Molecular property prediction UQ:**
- Conformal prediction has been applied to drug discovery for QSAR-style predictions (Frontiers in Bioinformatics, 2025), providing distribution-free coverage guarantees.
- Conformal prediction under feedback covariate shift has been studied for biomolecular design (PNAS), addressing the setting where model predictions guide future experimental data collection.

**General biological ML:**
- A 2025 Genome Biology review noted that zero-shot performance of biological FMs is unreliable, but did not study whether uncertainty estimates could identify when zero-shot predictions will fail vs. succeed.

### Evidence the Gap Exists

1. **Overconfidence in biological FMs:** ImmUQBench (2025) showed that "protein language models often exhibit overconfident predictions." This is not unique to immunogenicity -- overconfidence is a documented property of large neural networks in general, but the biological FM community has largely ignored it.

2. **UQ doesn't improve protein engineering:** The FLIP benchmark study (2025) found that "uncertainty-based sampling is often unable to outperform greedy sampling in Bayesian optimization" for protein fitness landscapes. This means existing UQ methods are not informative enough to guide experimental decisions, which is their primary use case.

3. **No UQ in major benchmarks:** ProteinGym (217 DMS assays, 2.7M variant measurements), PFMBench (38 tasks), TDC (66 datasets), and scPerturBench (27 methods, 29 datasets) -- none of these major benchmarks include calibration or uncertainty metrics. The field literally does not measure prediction reliability.

4. **The scaling wall connects to uncertainty:** Notin (2025) showed that protein language models hit a scaling wall beyond 1--4B parameters for mutation effect prediction. This may be partly because larger models are more overconfident -- they memorize more of the training data while becoming less aware of what they don't know. No study has examined whether scaling affects calibration.

5. **Clinical deployment requires UQ:** For any biological FM to be used in clinical or experimental decision-making, regulatory frameworks (FDA draft guidance, 2025) increasingly require uncertainty estimates. Without calibrated uncertainty, biological FMs cannot be deployed responsibly.

6. **Distribution shift is ubiquitous in biology:** Biological prediction tasks inherently involve distribution shift -- predicting properties of novel proteins not in the training set, predicting effects in new cell types, predicting activity of novel chemical scaffolds. UQ is most critical precisely where models encounter OOD data. A 2025 Briefings in Bioinformatics review found that "traditional ML models often fail when facing out-of-distribution samples."

## Why This Gap Matters

### Scientific Importance

Uncertainty quantification is the bridge between prediction and understanding. A model that says "this variant is deleterious with 95% confidence based on evolutionary conservation patterns" is scientifically informative. A model that says "this variant is deleterious (p=0.51)" is scientifically useless even if it's technically correct. Understanding when and why biological FMs are uncertain reveals what biological features are captured vs. missed by representations.

### Practical Impact

Every active learning loop in biology (protein engineering, drug optimization, CRISPR experiment design) depends on uncertainty estimates to select informative experiments. The FLIP benchmark result -- that UQ doesn't help -- means that the entire model-guided experimental design paradigm in biology is built on unreliable foundations. Fixing this would unlock genuine AI-guided experimental design.

### Publication Potential

Strong fit for Nature Methods or Nature Computational Science. The topic combines methodological rigor (uncertainty quantification is technically sophisticated) with high practical relevance (experimental decision-making). A systematic study showing how to make biological FM uncertainty reliable and useful would be highly impactful.

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

**BioUQ-Bench:** A comprehensive uncertainty quantification benchmark and method development framework for biological foundation models.

Components:

1. **Uncertainty Evaluation Protocol:** Extend major biological benchmarks (ProteinGym, TDC, DNA FM tasks) with calibration metrics: Expected Calibration Error (ECE), Brier scores, prediction interval coverage, and a novel "decision utility" metric that measures whether uncertainty estimates improve downstream experimental selection.

2. **Method Comparison:** Systematically evaluate UQ approaches adapted to biological FMs:
   - Ensemble methods (deep ensembles, MC dropout, snapshot ensembles)
   - Post-hoc calibration (temperature scaling, Platt scaling, isotonic regression)
   - Conformal prediction (distribution-free coverage guarantees)
   - Evidential deep learning
   - Bayesian approaches (Laplace approximation, variational inference)
   
   Evaluate on both in-distribution and OOD settings, measuring whether UQ correctly flags OOD predictions as uncertain.

3. **Scaling and Calibration Analysis:** Study how model scale (from 8M to 15B parameters for ESM2; from 300M to 40B for Evo-2) affects calibration. Test whether larger models are more or less calibrated.

4. **Decision-Theoretic Validation:** Simulate active learning loops for protein engineering, drug optimization, and variant interpretation. Measure whether improved UQ translates to better experimental selection (fewer experiments to reach a fitness threshold).

### Required Data

- ProteinGym (217 assays) for protein variant UQ
- FLIP benchmark for protein engineering UQ
- TDC ADMET datasets for molecular property UQ
- DNA variant effect datasets (ClinVar, gnomAD) for genomic UQ
- scPerturb datasets for single-cell UQ
- All publicly available

### Required Compute

- Training ensembles and UQ variants for multiple foundation models: 3,000--5,000 GPU-hours
- Calibration analysis across scales: 1,000--2,000 GPU-hours
- Active learning simulations: 500--1,000 GPU-hours
- Total: ~5,000--8,000 GPU-hours, feasible on HPC cluster with H200/B200 GPUs

### Required Methods

- Calibration metrics (ECE, Brier, coverage)
- Conformal prediction
- Deep ensemble training
- MC dropout inference
- Temperature scaling and post-hoc calibration
- Active learning simulation framework
- Statistical comparison framework

## Feasibility Assessment

### Technical Feasibility (Rating: High)
UQ methods are well-developed in the general ML literature. The novelty is in systematic application to biological FMs and in developing biologically relevant evaluation metrics. All methods are implementable in PyTorch.

### Timeline Feasibility (Rating: High)
Calibration analysis of existing models: 1--2 months. UQ method comparison: 2--3 months. Active learning simulations: 1--2 months. Total: 4--6 months.

### Wet Lab Independence (Rating: High)
Entirely computational. Uses existing benchmark datasets. Active learning is simulated using existing experimental data, not real experiments.

## Competitive Landscape

### Who Else Might Fill This Gap
- **FLIP/ProteinGym teams:** Could add UQ metrics but seem focused on expanding task coverage, not UQ
- **TDC team:** Could add calibration metrics to TDC but have not moved in this direction
- **Conformal prediction groups (Stanford):** Have applied conformal prediction to biomolecular design but focused on narrow CP methodology, not comprehensive UQ for biological FMs
- **ImmUQBench team:** Focused specifically on immunogenicity, not general biological FMs

### Risk of Being Scooped
Low-medium. The UQ-for-biology space is surprisingly empty given the importance of the problem. Individual UQ benchmarks exist (FLIP, ImmUQBench) but no comprehensive cross-domain study.

### Differentiation
Comprehensive scope (protein, DNA, single-cell, molecular) combined with decision-theoretic validation (does better UQ lead to better experimental decisions?) is the key differentiator. No existing work combines both.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 8 | Individual UQ studies exist, but comprehensive biological FM UQ benchmarking is new |
| Scientific impact | 8 | Addresses reliability of predictions across all of computational biology |
| Feasibility (computational only) | 8 | UQ methods are well-established; adaptation is straightforward |
| Timeline (summer 2026) | 8 | Achievable with focused scope on 2--3 modalities |
| Publication potential (Nat Comp Sci) | 8 | Practical importance + methodological rigor = strong paper |
| **Overall** | **8.0** | High on all dimensions; underexplored despite clear importance |

## References

1. PLOS Computational Biology. (2025). Benchmarking uncertainty quantification for protein engineering.
2. ImmUQBench. (2025). A benchmark on uncertainty quantification of protein immunogenicity prediction. Oxford Open Immunology.
3. Scientific Reports. (2025). Uncertainty quantification enables reliable deep learning for protein-ligand binding affinity prediction.
4. JCIM. (2025). Uncertainty Quantification and Temperature Scaling Calibration for Protein-RNA Binding Site Prediction.
5. Frontiers in Bioinformatics. (2025). Reliable machine learning models in genomic medicine using conformal prediction.
6. Angelopoulos, A. & Bates, S. (2023). Conformal prediction: A gentle introduction. Foundations and Trends in Machine Learning.
7. Fannjiang, C. & Listgarten, J. (2022). Conformal prediction under feedback covariate shift for biomolecular design. PNAS.
8. Kedzierska, K. et al. (2025). Zero-shot evaluation reveals limitations of single-cell foundation models. Genome Biology.
9. Notin, P. (2025). Have We Hit the Scaling Wall for Protein Language Models?
10. Briefings in Bioinformatics. (2025). Out of distribution learning in bioinformatics: advancements and challenges.
11. Nature Computational Science. (2026). Scaling and quantization of large-scale foundation model enables resource-efficient predictions in network biology.
12. Nature Machine Intelligence. (2025). Training data composition determines machine learning generalization and biological rule discovery.
13. FDA. (2025). Draft guidance: Considerations for the Use of Artificial Intelligence to Support Regulatory Decision-Making for Drugs and Biologics.

---

# Summary and Cross-Gap Connections

## Gap Priority Ranking

| Rank | Gap | Overall Score | Key Strength |
|------|-----|-------------|-------------|
| 1 | Perturbation Prediction Crisis | 8.4 | Highest feasibility, resolves active controversy |
| 2 | FM Evaluation Crisis | 8.2 | Highest community need, benchmark impact |
| 3 | Uncertainty-Aware Bio FMs | 8.0 | Underexplored yet critical for decision-making |
| 4 | Cross-Scale FM Integration | 7.6 | Highest scientific ambition, medium feasibility |

## Cross-Gap Connections

These four gaps are deeply interconnected:

1. **Evaluation crisis enables perturbation crisis:** The perturbation prediction debate (Gap 2) exists partly because evaluation methodology (Gap 3) is broken. Better benchmarks with contamination control and biologically grounded metrics would clarify whether deep learning genuinely helps for perturbation prediction.

2. **Uncertainty connects evaluation to decision-making:** Gap 4 (uncertainty) bridges Gap 3 (evaluation) and practical deployment. A model that is well-calibrated can self-report when its predictions are unreliable, which is a form of evaluation embedded in the model itself.

3. **Cross-scale requires reliable within-scale models:** Gap 1 (cross-scale integration) depends on the within-scale models being reliable (Gap 3) and well-calibrated (Gap 4). Building cross-scale models on unreliable foundations would amplify errors across scales.

4. **A unified project opportunity:** A single ambitious project could address all four gaps simultaneously by building a **live, uncertainty-aware, cross-modal benchmark ecosystem** that evaluates biological foundation models on their ability to make calibrated predictions across biological scales. This would be a Nature Computational Science-level contribution that provides lasting infrastructure for the field.

## Strongest Single Project Candidate

If forced to choose one gap for a single summer 2026 project, **Gap 2 (Perturbation Prediction Crisis)** offers the best risk/reward trade-off: highest feasibility, an active controversy to resolve, clear data and methods, and direct relevance to the virtual cell agenda that the entire computational biology community is pursuing.

However, the highest-impact contribution would combine **Gap 2 + Gap 3** into a single study: a contamination-free, rigorously-evaluated comparison of perturbation prediction methods that definitively answers when and why non-linear models help, using temporally-gated data and biologically grounded metrics.
