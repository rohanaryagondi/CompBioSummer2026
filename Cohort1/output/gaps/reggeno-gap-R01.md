---
agent: reggeno
round: 1
date: 2026-04-14
type: gap-report
---

# Regulatory Genomics & Epigenomics -- Round 1 Gap Reports

**Agent:** Dr. Regulatory Genomics & Epigenomics Expert (reggeno)
**Round:** 1
**Date:** 2026-04-14

---

## Executive Summary

After extensive literature review of >80 recent papers, preprints, and benchmarks (2024--2026), I identify four significant gaps in regulatory genomics and epigenomics that are computationally tractable, benefit from large-scale compute, and are suitable for ambitious research targeting Nature Computational Science. The non-coding genome remains biology's largest unsolved data interpretation problem: 90%+ of GWAS variants fall in non-coding regions, yet computational methods for predicting complex trait variant effects perform at near-random levels (AUROC 0.48--0.52). Genomic foundation models have exploded in number but suffer from critical failures in cell-type-specific prediction, cross-cell-type generalization, and multi-modal integration. These gaps represent genuine opportunities for transformative computational contributions.

---
---

# Gap 1: Cell-Type-Specific Regulatory Prediction Collapse in Genomic Deep Learning Models

## gap_id: celltype-reg-collapse

## Reporting Agent
Dr. Regulatory Genomics & Epigenomics Expert (reggeno), Cohort1 Gap Scouts

## Gap Description

### What Is Missing

Current state-of-the-art genomic deep learning models -- including Enformer (Avsec et al., 2021), Borzoi (Linder et al., 2024), Sei (Chen et al., 2022), and even the recently released AlphaGenome (DeepMind, 2025) -- exhibit a systematic and quantifiable failure: their prediction accuracy drops substantially in genomic regions with cell-type-specific chromatin accessibility compared to ubiquitously accessible regions. This means the models perform worst precisely where they matter most -- in the regulatory elements that distinguish one cell type from another and that harbor the majority of disease-relevant variation.

What is missing is a genomic sequence model that maintains high prediction accuracy specifically in cell-type-specific regulatory regions across hundreds of cell types, including rare and underrepresented cell types. No current model achieves this.

### Current State of the Art

**Enformer** (Avsec et al., 2021, Nature Methods): Processes 196,608 bp of DNA sequence and predicts 5,313 genomic tracks (gene expression, histone marks, chromatin accessibility) at 128 bp resolution. Achieves a Pearson correlation of ~0.85 for gene expression prediction genome-wide, but this performance is driven by ubiquitous regulatory elements.

**Borzoi** (Linder et al., 2024, Nature Genetics): Extends Enformer with a U-net architecture for 32 bp resolution (vs 128 bp) and expanded sequence context. Predicts RNA-seq coverage directly. Competitive with or outperforms Enformer on eQTL prediction (AUROC ~0.77 for eQTLs). Flashzoi (Hähnel et al., 2025) provides a 3x faster variant using rotary positional encodings and FlashAttention-2.

**AlphaGenome** (DeepMind, 2025, Nature): Processes 1 Mb of DNA sequence at single-base-pair resolution. Predicts thousands of functional genomic tracks. Matches or exceeds the strongest external models in 25 of 26 variant effect prediction evaluations. Improved tissue-weighted mean Spearman rho from 0.39 (Borzoi) to 0.49 and mean sign AUROC from 0.75 to 0.80 for eQTL prediction. However, AlphaGenome itself acknowledges that predictions for underrepresented tissues or rare cell types remain limited, and it was primarily trained on bulk tissue functional genomics datasets.

**Sei** (Chen et al., 2022): Predicts histone marks, TF binding, and chromatin accessibility across 2,372 profiles in >1,300 cell lines and tissues.

**Critical finding (Yengo et al., 2024, Genome Biology):** A systematic evaluation demonstrated that both Enformer and Sei show decreased performance in cell-type-specific accessible regions compared to ubiquitously accessible regions. The performance drop is not marginal -- models that achieve strong genome-wide metrics exhibit substantially compromised accuracy in regions with high cell-type specificity. This is particularly concerning because these cell-type-specific regions harbor significant disease heritability. Increasing model capacity for cell-type-specific regulatory syntax through single-task learning or high-capacity multi-task models can improve performance, but the gap persists.

**EpiAgent** (Chen et al., 2025, Nature Methods): A foundation model for scATAC-seq pretrained on ~5 million cells and 35 billion tokens from the Human-scATAC-Corpus (5,407,621 cells from 35 datasets across 37 tissues). Excels at unsupervised feature extraction, cell type annotation, and data imputation. However, EpiAgent operates at the cell-level representation scale, not at the sequence-to-function prediction level needed for variant effect prediction.

### Evidence the Gap Exists

1. **Systematic performance drop in cell-type-specific regions:** Yengo et al. (2024, Genome Biology) showed that Enformer and Sei accuracy varies across the genome and is reduced in cell-type-specific accessible regions. This was validated across multiple cell types and evaluation metrics.

2. **AlphaGenome's own stated limitations:** DeepMind acknowledges that AlphaGenome is "primarily trained on large bulk-tissue functional genomics datasets, so predictions for under-represented tissues or rare cell types remain limited and would require model retraining" (DeepMind blog, 2025).

3. **Training data bias:** Models are trained predominantly on ENCODE and Roadmap Epigenomics data, which covers ~127 reference epigenomes (Roadmap Epigenomics Consortium, 2015, Nature) and a few hundred cell lines. The Human-scATAC-Corpus covers only 37 tissues/cell lines. There are an estimated >400 distinct cell types in the human body, with many rare cell types having minimal or no functional genomics data.

4. **Entropy analysis of genomic foundation models:** An information-theoretic analysis (2025, arXiv:2604.04287) showed that DNA foundation models assign near-uniform probability distributions across tokens (KL divergence of <1 bit for k-mer tokenizers vs >10 bits for text models), indicating they struggle to learn confident, interpretable distributions. Fisher information concentrates in embedding layers rather than transformer layers, suggesting models ignore the attention mechanism designed to capture token dependencies.

5. **CREATE method** (Nature Communications, 2025): A multimodal framework for cell-type-specific CRE identification found that data imbalance for silencers and underrepresented cell types impairs CRE identification performance.

## Why This Gap Matters

### Scientific Importance

Cell-type-specific gene regulation is fundamental to development, homeostasis, and disease. The regulatory elements that distinguish one cell type from another are where disease variants exert their effects. If models cannot accurately predict regulatory function in specific cell types, they cannot fulfill their promise for understanding gene regulation or interpreting disease variation. This is not a minor calibration issue -- it is a fundamental limitation that undermines the utility of the entire class of genomic deep learning models.

### Practical Impact

- **Variant interpretation:** >90% of GWAS variants are non-coding, and their effects are cell-type-specific. Models that fail in cell-type-specific regions cannot reliably prioritize causal variants.
- **Drug target discovery:** Identifying which cell type a disease variant acts through is critical for therapeutic targeting. Current models are worst at this task.
- **Rare disease:** Many rare diseases affect specific cell types. Models trained on common cell lines miss the relevant regulatory logic.

### Publication Potential

A model that demonstrably maintains high accuracy in cell-type-specific regulatory regions across hundreds of cell types would be a major advance. This directly addresses the primary criticism of current models and has clear benchmarking against Enformer, Borzoi, and AlphaGenome. **Target:** Nature Computational Science or Nature Methods. **Main claim:** "A multi-modal regulatory model that eliminates the cell-type-specificity performance gap in genomic prediction."

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

Develop a model that integrates DNA sequence with cell-type-specific epigenomic signals (scATAC-seq, histone modifications) and 3D chromatin organization to predict regulatory activity at cell-type resolution. The key innovation would be an architecture that conditions sequence-based predictions on a learned cell-type embedding derived from accessible chromatin profiles, enabling the model to generalize to cell types not seen during training.

### Required Data

- **ENCODE Phase 4 and Roadmap Epigenomics:** ~127 reference epigenomes with histone marks, DNase-seq, RNA-seq
- **Human-scATAC-Corpus:** 5,407,621 cells across 37 tissues (Chen et al., 2025)
- **GTEx v8:** 15,253 RNA-seq samples from 838 individuals across 54 tissues; 4,278,636 cis-eVariants
- **gnomAD non-coding constraint scores:** 1,665,599 exclusively non-coding 1kb windows with Gnocchi scores
- **Hi-C and Micro-C data:** From 4D Nucleome Project and ENCODE
- All publicly available; no restricted data needed.

### Required Compute

- Training sequence-to-function models at 1 Mb context with single-base resolution requires substantial GPU memory and throughput
- Estimated: 32-64 H200 GPUs for 2-4 weeks for model training
- Inference on millions of variants across hundreds of cell types: 8-16 GPUs for 1-2 weeks
- Well within HPC cluster capabilities

### Required Methods

- Transformer-based sequence encoder (building on Enformer/Borzoi architecture)
- Cell-type conditioning module using scATAC-seq embeddings
- Multi-task learning across cell types with loss reweighting for rare cell types
- Evaluation framework specifically targeting cell-type-specific regions

## Feasibility Assessment

### Technical Feasibility (Rating: Medium-High)
The individual components (sequence models, scATAC-seq embeddings, multi-task learning) all exist. The challenge is integrating them effectively and training at scale. EpiBERT (2025) and CREsted (2026, Nature Methods) demonstrate that combining sequence and epigenomic data is technically feasible.

### Timeline Feasibility (Rating: Medium)
Building and training a model of this complexity is ambitious for a summer timeline. A focused approach targeting a specific architectural innovation (e.g., the cell-type conditioning module) with existing pre-trained backbones could be achievable.

### Wet Lab Independence (Rating: High)
Entirely computational. All training and evaluation data are publicly available. Validation uses held-out cell types from existing datasets.

## Competitive Landscape

### Who Else Might Fill This Gap
- **DeepMind/Google:** AlphaGenome is the closest competitor, but they acknowledge the rare cell type limitation. A follow-up addressing this is likely.
- **Arc Institute (Evo team):** Focused on generative models rather than cell-type-specific prediction.
- **Calico (Borzoi team):** May extend Borzoi/Flashzoi with cell-type conditioning.
- **Broad Institute (Engreitz lab):** Working on enhancer-gene prediction but focused on the ABC model framework.

### Risk of Being Scooped
**Medium-High.** AlphaGenome's release signals intense competition. However, the specific gap of cell-type-specific performance has not been directly addressed by any major group's published roadmap. The window is 6-12 months.

### Differentiation
The key differentiator would be demonstrating performance maintenance in rare cell types through a principled conditioning mechanism, rather than simply training on more data. This is a methodological contribution, not just a scaling exercise.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 7 | The problem is documented but no solution exists; the specific approach of cell-type conditioning for sequence models is novel |
| Scientific impact | 9 | Cell-type-specific regulation is central to biology and medicine; solving this unlocks variant interpretation |
| Feasibility (computational only) | 7 | Components exist but integration is non-trivial; large-scale training required |
| Timeline (summer 2026) | 6 | Ambitious but possible with focused scope; risk of timeline overrun |
| Publication potential (Nat Comp Sci) | 8 | Directly addresses the #1 criticism of current models; clear benchmarking story |
| **Overall** | **7.4** | High-impact gap with good but challenging feasibility |

---
---

# Gap 2: Near-Random Prediction of Complex Trait Non-Coding Variant Effects

## gap_id: complex-trait-vep

## Reporting Agent
Dr. Regulatory Genomics & Epigenomics Expert (reggeno), Cohort1 Gap Scouts

## Gap Description

### What Is Missing

The computational biology community has no method that can reliably predict the functional effects of common non-coding variants associated with complex traits (type 2 diabetes, cardiovascular disease, schizophrenia, etc.) identified through GWAS. Current methods achieve AUROC scores of 0.48--0.52 on disease-associated common variants from curated GWAS -- essentially random performance. This is in stark contrast to their performance on rare Mendelian variants (AUROC 0.69--0.80), creating a critical gap in translating GWAS discoveries to biological mechanism.

### Current State of the Art

**Scale of the problem:** The GWAS Catalog (2025) contains >7,400 publications, >1,040,000 reported SNP-trait associations across >15,000 traits. Over 90% of these variants are non-coding. Only 309 non-coding GWAS variants have been experimentally validated across 130 human disease traits (Alsheikh et al., 2022, BMC Medical Genomics).

**ClinVar non-coding coverage:** Only 0.34% (1 in 294) of high-confidence pathogenic variants in ClinVar are in UTRs or immediately upstream regions. Among UTR variants, 63.4% are classified as variants of uncertain significance (VUS) vs 44.2% for coding variants.

**Performance on complex trait variants:** A systematic benchmark (2022, Computational and Structural Biotechnology Journal) found that performance of existing methods was acceptable for rare germline variants from ClinVar (AUROC 0.45--0.80) but poor for disease-associated common variants from curated GWAS (AUROC 0.48--0.52).

**TraitGym benchmark (Brandes et al., 2025):** This comprehensive benchmark evaluated multiple model classes on causal regulatory variant prediction:
- For **Mendelian traits:** Alignment-based models (CADD, GPN-MSA, phyloP) dominated. GPN-MSA achieved substantial margins over other models.
- For **complex traits:** Functional-genomics-supervised models (Enformer, Borzoi) performed best with linear probing, but "overall scores are much lower than in Mendelian traits." The authors note variants influencing complex traits "are expected to have relatively small effect sizes."
- Evo2 (40 billion parameters) showed "substantial performance gains with scale" but still underperformed alignment-based methods, particularly struggling with enhancer variants.
- The key conclusion: "The classification of variants is substantially harder for complex traits."

**AlphaGenome (DeepMind, 2025):** Improved eQTL prediction from Spearman rho 0.39 to 0.49 and sign AUROC from 0.75 to 0.80 compared to Borzoi. But these are eQTL-level evaluations, not the harder task of predicting which GWAS variants are truly causal and through what mechanism.

**Comparative deep learning analysis (2025, Genes):** CNN architectures (TREDNet, SEI) perform best for predicting regulatory impact of SNPs in enhancers. Hybrid CNN-Transformer models (Borzoi) perform best for causal variant prioritization within LD blocks. But Borzoi achieves AUROC of only 0.672 for detecting enhancer regions.

### Evidence the Gap Exists

1. **Near-random AUROC for GWAS variants:** AUROC 0.48--0.52 on curated GWAS common variants is essentially coin-flip performance (Fang & Wei, 2022).

2. **Only 309 experimentally validated non-coding GWAS variants** across 130 diseases (Alsheikh et al., 2022), out of >1,000,000 reported associations. The validation rate is <0.03%.

3. **Small effect sizes:** Complex trait variants typically have odds ratios of 1.05--1.2, producing subtle regulatory changes that are below the detection threshold of current models.

4. **Missing tissue/cell-type context:** Most GWAS variants act in specific cell types and conditions. Models trained on average-across-tissues data miss the signal.

5. **LD confounding:** GWAS identifies haplotype blocks, not individual causal variants. Current models evaluate individual variants in isolation, ignoring the statistical fine-mapping context.

6. **No model integrates fine-mapping posteriors:** Statistical fine-mapping methods (SuSiE, FINEMAP) produce posterior probabilities of causality, but these are not integrated with sequence-based functional predictions in a unified framework.

## Why This Gap Matters

### Scientific Importance

GWAS has been the single most productive approach for identifying genetic contributions to common diseases over the past two decades. The inability to computationally predict which of the >1,000,000 reported associations involve truly causal variants, and through what regulatory mechanism they act, represents the single largest bottleneck in human genetics. This gap directly prevents the translation of genetic discoveries into biological understanding.

### Practical Impact

- **Drug target identification:** GWAS-based target identification is a major pharmaceutical strategy, but requires knowing the causal variant, target gene, and relevant cell type -- none of which current methods can reliably predict for complex traits.
- **Polygenic risk scores:** Improving causal variant identification would improve PRS accuracy and transferability across ancestries.
- **Precision medicine:** Predicting which regulatory variants contribute to individual disease risk requires models that work for small-effect common variants.

### Publication Potential

A method that substantially improves complex trait variant effect prediction (e.g., from AUROC ~0.5 to >0.7) would be a landmark paper. The benchmarking infrastructure exists (TraitGym, ClinVar). **Target:** Nature Genetics or Nature Computational Science. **Main claim:** "A unified framework for causal regulatory variant prediction that integrates sequence-based functional predictions with statistical fine-mapping to break the complex trait prediction barrier."

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

Develop a framework that combines:
1. Sequence-based variant effect prediction from models like Borzoi/AlphaGenome (providing functional impact scores)
2. Statistical fine-mapping posteriors from SuSiE/FINEMAP (providing causal probability estimates)
3. Cell-type-specific regulatory annotations (providing tissue context)
4. An integrative model that learns to combine these signals to predict causal mechanisms for complex trait variants

The key insight is that no single model captures all the information needed -- the solution requires principled integration of statistical genetics with deep learning predictions.

### Required Data

- **TraitGym benchmark** (Brandes et al., 2025): Curated causal/candidate variants across 113 Mendelian and 83 complex traits
- **GTEx v8 eQTL data:** 4,278,636 cis-eVariants across 54 tissues with fine-mapping results
- **UK Biobank GWAS summary statistics:** Publicly available for ~7,000 phenotypes
- **ENCODE/Roadmap functional annotations:** Chromatin state maps across 127 epigenomes
- **gnomAD v4:** Population allele frequencies and non-coding constraint scores (Gnocchi)
- All publicly available.

### Required Compute

- Pre-computed variant effect predictions from existing models (AlphaGenome API, Borzoi) for millions of variants: moderate compute
- Training the integrative model: 8-16 GPUs for 1-2 weeks
- Running statistical fine-mapping across thousands of GWAS loci: CPU-intensive, ~1000 CPU-hours

### Required Methods

- Transfer learning from pre-trained sequence models (AlphaGenome/Borzoi)
- Bayesian fine-mapping (SuSiE framework)
- Multi-task learning across trait categories
- Calibrated probability estimation (not just ranking)

## Feasibility Assessment

### Technical Feasibility (Rating: High)
All components exist individually. The innovation is the integration framework. The main technical challenge is obtaining variant effect predictions at scale from existing models (AlphaGenome API limits, Borzoi inference cost).

### Timeline Feasibility (Rating: High)
This is a well-scoped project that leverages existing models and datasets. The integrative framework can be developed in 2-3 months, with 1-2 months for benchmarking.

### Wet Lab Independence (Rating: High)
Entirely computational. Validated against existing experimental benchmarks (TraitGym, eQTL fine-mapping).

## Competitive Landscape

### Who Else Might Fill This Gap
- **Broad Institute (Finucane/Price labs):** Leading statistical genetics groups that work on fine-mapping and functional enrichment, but primarily use traditional statistical methods rather than deep learning.
- **DeepMind:** Could extend AlphaGenome toward this, but their focus is on the base model rather than downstream integration.
- **Brandes et al. (TraitGym authors):** Have the benchmark but not the integrative solution.

### Risk of Being Scooped
**Medium.** The problem is well-known but the specific approach of integrating deep learning VEP with fine-mapping in a unified model has not been published. Multiple groups are working on individual components.

### Differentiation
The differentiation is in the principled statistical integration of heterogeneous prediction signals -- not just another VEP model, but a meta-framework that combines the best of statistical genetics and deep learning.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 7 | Integration framework is novel; individual components exist |
| Scientific impact | 10 | Addresses the single largest bottleneck in human genetics |
| Feasibility (computational only) | 8 | Leverages existing models and data; well-scoped |
| Timeline (summer 2026) | 8 | Achievable in 3-4 months with existing infrastructure |
| Publication potential (Nat Comp Sci) | 9 | Massive unmet need with clear benchmarking |
| **Overall** | **8.4** | Highest-impact gap with strong feasibility |

---
---

# Gap 3: Absence of a Unified Multi-Modal Regulatory Genome Model (Sequence + Epigenome + 3D Structure)

## gap_id: multimodal-reg-genome

## Reporting Agent
Dr. Regulatory Genomics & Epigenomics Expert (reggeno), Cohort1 Gap Scouts

## Gap Description

### What Is Missing

Despite the explosion of genomic foundation models, no existing model jointly integrates DNA sequence, cell-type-specific epigenomic data (histone modifications, chromatin accessibility), and 3D genome organization (chromatin contacts, TADs, loops) into a single unified framework for regulatory prediction. Current models operate in silos: sequence models (Enformer, AlphaGenome) predict from DNA alone; epigenome models (EpiAgent, ChromHMM) analyze chromatin data without sequence context; 3D genome models (Hi-Compass, FLAMINGO) predict chromatin conformation but do not link it to gene expression. The field lacks a model that captures the full regulatory code by modeling how sequence encodes regulatory elements, how epigenomic modifications activate or silence them in specific cell types, and how 3D genome organization brings distal elements into contact with their target genes.

### Current State of the Art

**Sequence-only models:**
- AlphaGenome (2025, Nature): Predicts chromatin contact maps alongside other modalities but from sequence alone, without conditioning on observed epigenomic state. Mean sign AUROC of 0.80 for eQTL effect direction.
- Enformer/Borzoi: Predict functional genomics tracks from sequence. Do not incorporate observed epigenomic data as input.
- Evo2 (Arc Institute, 2025-2026, Nature): 7B--40B parameter generative model trained on 9 trillion nucleotides, but focused on generation rather than regulatory prediction and does not incorporate epigenomic data.

**Epigenome-focused models:**
- EpiAgent (2025, Nature Methods): Foundation model for scATAC-seq, pretrained on 5M cells. Excels at cell type annotation and imputation. Does not integrate DNA sequence or 3D genome.
- ChromHMM/Segway: Segment the genome into chromatin states based on histone marks. No sequence input, no 3D genome.
- EpiBERT (2025): Multi-modal transformer for sequence + chromatin accessibility. A step toward integration but limited in scope (no 3D genome, no histone modifications beyond accessibility).

**3D genome models:**
- Hi-Compass (2025, bioRxiv): Predicts cell-type-specific chromatin organization from scATAC-seq data across diverse biological contexts. However, it does not integrate with gene expression prediction or variant effect prediction.
- FLAMINGO (2022, Nature Communications): Reconstructs high-resolution 3D structures. Does not link structure to function.
- C.Origami (2023, Nature Biotechnology): Predicts cell-type-specific 3D chromatin organization from sequence and CTCF/ATAC data. A notable step toward multi-modal integration, but does not predict gene expression or variant effects downstream.

**Partial integrations:**
- EPInformer: Integrates promoter-enhancer sequences with multimodal epigenomic data for gene expression prediction. A promising direction but limited in scope and not at foundation model scale.
- VariantFormer (2025, bioRxiv): 1.2B-parameter model that predicts tissue-specific gene expression from personalized diploid genomes. Uses genotype data but not epigenomic or 3D genome data as input.
- A data-driven chromatin model (PNAS, 2025): Uses FI-Chrom (Full-Inversion Chromatin) to infer effective interactions from Hi-C data, but this is a physics model, not a deep learning model that integrates sequence.

### Evidence the Gap Exists

1. **No single model in the literature combines all three modalities.** I conducted extensive searches of bioRxiv, PubMed, and arXiv (2024-2026) and found no published model that takes DNA sequence + histone modifications + chromatin contacts as joint input to predict gene expression and variant effects.

2. **Multi-modal integration review (Nature, 2025):** A review "Towards multimodal foundation models in molecular cell biology" (Nature, 2025) calls for multimodal foundation models but acknowledges that "a unified model integrating sequence, epigenomic, and 3D genome data" does not yet exist.

3. **3D genome prediction remains decoupled from gene expression:** Hi-Compass and C.Origami predict chromatin conformation but do not close the loop to gene expression. The ABC model (Fulco/Engreitz) combines activity and contact but uses simple linear assumptions and has documented limitations in quantitative prediction (eLife, 2025).

4. **Known regulatory biology requires integration:** Enhancer-promoter regulation involves: (a) DNA sequence encoding TF binding motifs, (b) chromatin accessibility/histone marks determining which motifs are active in a cell type, and (c) 3D chromatin proximity determining which enhancer-promoter pairs can interact. Modeling any one without the others is incomplete.

5. **Recent mathematical analysis of ABC model (eLife, 2025):** Showed that the ABC model's mathematical foundations are informal, and its quantitative predictions of enhancer effects are limited. The field needs a more principled approach to combining activity and contact information.

## Why This Gap Matters

### Scientific Importance

Gene regulation is inherently multi-modal: sequence determines the grammar, epigenomics determines the state, and 3D structure determines the connectivity. A model that captures all three would represent a qualitative advance in our ability to decode the regulatory genome. This is analogous to how protein structure prediction required integrating sequence with evolutionary and structural information -- the regulatory genome prediction problem demands a similar multi-modal solution.

### Practical Impact

- **Variant interpretation:** Many disease variants disrupt enhancer-promoter interactions, requiring 3D genome context for interpretation.
- **Cell state transitions:** During development and disease, epigenomic states change, rewiring regulatory circuits. A multi-modal model could predict these transitions.
- **Therapeutic target identification:** Understanding which enhancers regulate which genes in which cell types requires all three modalities.

### Publication Potential

A unified multi-modal regulatory genome model would be a major contribution. **Target:** Nature Computational Science. **Main claim:** "A unified foundation model for the regulatory genome that jointly models DNA sequence, epigenomic state, and 3D chromatin organization."

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

Build a multi-modal transformer architecture with three input streams:
1. **Sequence encoder:** Process DNA sequence with a pre-trained backbone (e.g., Enformer/Borzoi weights)
2. **Epigenome encoder:** Process cell-type-specific chromatin accessibility and histone mark profiles (using scATAC-seq and ChIP-seq data)
3. **3D structure encoder:** Process Hi-C/Micro-C contact maps to capture chromatin topology

These streams would be fused through cross-attention layers that allow each modality to inform the others. The model would be trained to predict cell-type-specific gene expression, variant effects, and enhancer-promoter interactions.

### Required Data

- **ENCODE Phase 4:** Histone marks, ATAC-seq, RNA-seq across hundreds of biosamples
- **4D Nucleome Project:** Hi-C and Micro-C contact maps at multiple resolutions
- **Human-scATAC-Corpus:** 5.4M cells, 37 tissues
- **GTEx v8:** Gene expression across 54 tissues
- **CRISPR validation datasets:** CRISPRi/CRISPRa perturbation data for enhancer-gene links (Gasperini et al., 2019; Fulco et al., 2019)
- All publicly available.

### Required Compute

- Substantial: Training a multi-modal model with 1 Mb DNA context, thousands of epigenomic tracks, and Hi-C contact maps
- Estimated: 64-128 H200 GPUs for 3-6 weeks
- Inference: 16-32 GPUs for large-scale variant scoring
- Feasible on the HPC cluster described

### Required Methods

- Multi-modal transformer architecture with cross-attention
- Pre-training on individual modalities followed by joint fine-tuning
- Contrastive learning to align modality representations
- Multi-task training: gene expression prediction + variant effect prediction + enhancer-promoter interaction prediction

## Feasibility Assessment

### Technical Feasibility (Rating: Medium)
Multi-modal transformers are well-established in NLP and computer vision. The challenge is handling the scale of genomic data (1 Mb sequences, genome-wide Hi-C maps, thousands of epigenomic tracks) and the heterogeneity of data types. Pre-training individual encoders and fine-tuning jointly is a proven strategy that mitigates this.

### Timeline Feasibility (Rating: Low-Medium)
This is the most ambitious of the four gaps. Building and training a full multi-modal model from scratch in one summer is extremely challenging. A focused version -- e.g., combining a pre-trained sequence encoder with an epigenome conditioning module -- is more realistic. The full three-modality model might require a phased approach.

### Wet Lab Independence (Rating: High)
Entirely computational. All data are public. Validation against CRISPR-based enhancer perturbation data (published datasets).

## Competitive Landscape

### Who Else Might Fill This Gap
- **DeepMind:** AlphaGenome already predicts Hi-C-like contact maps from sequence; extending to condition on observed epigenomic data is a natural next step.
- **Broad Institute:** Multiple labs working on enhancer-gene prediction and 3D genome modeling.
- **NVIDIA BioNeMo team:** Building genomic foundation models with large compute budgets.
- **InstaDeep (NTv3 team):** Developing multi-species, multi-task genomic models.

### Risk of Being Scooped
**High.** Multiple well-funded groups are converging on multi-modal genomic models. The window for a pioneering contribution is narrow (6-12 months).

### Differentiation
The key differentiator would be demonstrating that the multi-modal model outperforms any single-modality model on cell-type-specific tasks where single-modality models fail (linking to Gap 1). The value proposition is not just the architecture but the empirical demonstration that integration is necessary.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 9 | No existing model truly integrates all three modalities |
| Scientific impact | 9 | Would represent a qualitative advance in decoding the regulatory genome |
| Feasibility (computational only) | 5 | Technically challenging; multi-modal architectures at genomic scale are hard |
| Timeline (summer 2026) | 4 | Full model very ambitious for summer; focused version more realistic |
| Publication potential (Nat Comp Sci) | 9 | Extremely high if successful; clear advance over all existing models |
| **Overall** | **7.2** | Highest novelty and impact but significant feasibility risk |

---
---

# Gap 4: Cross-Cell-Type Generalization Failure in Gene Regulatory Network Inference

## gap_id: grn-generalization

## Reporting Agent
Dr. Regulatory Genomics & Epigenomics Expert (reggeno), Cohort1 Gap Scouts

## Gap Description

### What Is Missing

Computational methods for inferring gene regulatory networks (GRNs) from single-cell data fail to generalize across cell types, conditions, and biological contexts. Despite extensive method development, a comprehensive 2025 benchmarking study (geneRNIB) found that simple correlation-based methods often outperform complex deep learning and prior-knowledge-based approaches, and performance on real data remains "unreliable, limited by technical and biological noise." The field lacks a GRN inference method that can learn transferable regulatory logic from one cell type and apply it to predict regulation in another -- a capability that would transform our understanding of how regulatory networks are rewired during development, disease, and evolution.

### Current State of the Art

**Benchmarking landscape (2025):**
- **geneRNIB** (2025, bioRxiv): A comprehensive GRN benchmarking framework that assessed 10 inference methods across 5 diverse datasets with thousands of perturbation scenarios. Key finding: "simple models with fewer assumptions often outperformed more complex pipelines, and notably gene expression-based correlation algorithms yielded better results than more advanced approaches incorporating prior datasets or pre-trained on large datasets."
- **CausalBench** (2025, Communications Biology): Large-scale benchmark using real-world single-cell perturbation data. Found that on real data, "performance remains unreliable, limited by technical and biological noise, as well as algorithmic scalability."
- **Comparison of causal structure learning** (2025, bioRxiv): Found that accurate GRN recovery is achieved under favorable conditions with strong interventions, large sample sizes, and low noise, but real-data performance is poor.

**Current methods:**
- **DAZZLE** (2025): Ensemble version (DAZZLE-10x) has the best performance in over half the benchmark cases, ranking 2nd or 3rd in all others within 6% of the top score.
- **HyperG-VAE** (2025, Cell Reports Methods): Bayesian deep generative model using hypergraph representation. Shows improvement on benchmarks but limited to single-dataset evaluations.
- **GRaNIE/GRaNPA** (2024, Nature Biotechnology): Infers GRNs from single-cell multiome data using atlas-scale external data. Represents a step toward leveraging large-scale data but does not explicitly address cross-cell-type transfer.
- **Dictys** and **SCENIC+**: Integrate scRNA-seq with scATAC-seq for TF-gene regulatory inference. Cell-type-specific but do not transfer learned logic across cell types.

**Cross-cell-type prediction:**
- Current 3D genome models show that "the most desirable application [is] the use of a model trained in a cell line to make predictions for another cell line; current methods, however, perform undesirably across cell lines" (2025 review).
- This same generalization failure applies to GRN inference: networks inferred in one cell type do not transfer to another.

### Evidence the Gap Exists

1. **geneRNIB benchmark (2025):** Directly demonstrates that complex methods do not outperform simple correlations, indicating that no method has learned transferable regulatory logic.

2. **CausalBench (2025):** Shows that on real perturbation data, GRN inference is unreliable -- the gap between synthetic data performance and real data performance is large.

3. **Cross-cell-type 3D genome prediction (2025):** Hi-Compass and similar models acknowledge that cross-cell-type prediction remains a major limitation.

4. **Population-specific regulation gap:** Most eQTL studies use European-ancestry individuals. The MAGE dataset (2024, Nature) -- 731 individuals across 26 populations -- revealed population-specific regulatory variants. GRN models do not account for genetic background.

5. **GTEx tissue limitation:** GTEx covers 54 tissues from bulk RNA-seq but does not resolve individual cell types within tissues. Cell-type-deconvolution approaches exist but add noise.

6. **Dropout and sparsity in scRNA-seq:** Due to picogram-level DNA amounts, single-cell data is inherently sparse. Current GRN methods do not adequately handle this sparsity when transferring across contexts.

## Why This Gap Matters

### Scientific Importance

GRNs are the operating system of cells. Understanding how they are rewired during differentiation, disease, and perturbation is a central question in biology. The inability to transfer regulatory logic across cell types means we cannot predict how a cell will respond to perturbation without directly measuring it -- eliminating the predictive power that computational biology should provide.

### Practical Impact

- **Virtual cell modeling:** Projects like the CZ Virtual Cell require GRNs that generalize across cell types. Without transferable GRN inference, virtual cell models cannot predict cell state transitions.
- **Drug response prediction:** Predicting how a drug perturbation will affect a cell type requires knowing the GRN of that cell type. If GRNs don't transfer, predictions require direct experimental data for each cell type.
- **Developmental biology:** Understanding cell fate decisions requires comparing GRNs across developmental stages and lineages.

### Publication Potential

A GRN inference method that demonstrably generalizes across cell types and outperforms simple correlations on real perturbation data would be a major advance. The benchmarking infrastructure exists (geneRNIB, CausalBench). **Target:** Nature Methods or Nature Computational Science. **Main claim:** "A transferable gene regulatory network model that learns cell-type-invariant regulatory logic from single-cell multi-omics data."

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

Develop a GRN inference framework based on:
1. A foundation model pre-trained on large-scale single-cell multi-omics data (scRNA-seq + scATAC-seq)
2. Learning cell-type-invariant TF-target relationships (the "regulatory grammar") shared across cell types
3. Cell-type-specific parameters that modulate the shared grammar based on chromatin state
4. Transfer learning: train on well-characterized cell types, predict GRNs in unseen cell types

The key innovation is decomposing GRNs into shared regulatory logic (which TFs can regulate which targets, based on motif grammar) and cell-type-specific activation (which regulatory connections are active, based on chromatin state).

### Required Data

- **CellxGene Census:** Millions of single-cell RNA-seq profiles across hundreds of cell types
- **Human-scATAC-Corpus:** 5.4M cells with chromatin accessibility
- **Perturb-seq datasets:** CRISPR perturbation screens in multiple cell types (Replogle et al., 2022; Dixit et al., 2016)
- **CZ CELLxGENE Discover:** Curated single-cell datasets with standardized cell type annotations
- All publicly available.

### Required Compute

- Pre-training on millions of cells: 16-32 GPUs for 1-2 weeks
- Fine-tuning and evaluation: 4-8 GPUs for 1-2 weeks
- Perturbation prediction inference: moderate compute

### Required Methods

- Graph neural networks for modeling TF-gene interactions
- Variational inference for handling sparsity and uncertainty
- Meta-learning framework for cross-cell-type transfer
- Causal inference components to distinguish correlation from regulation

## Feasibility Assessment

### Technical Feasibility (Rating: Medium)
GRN inference is fundamentally difficult because gene expression data is noisy and high-dimensional. The meta-learning/transfer approach is novel but adds complexity. The key risk is that regulatory logic may be less transferable than assumed.

### Timeline Feasibility (Rating: Medium)
A focused version (e.g., transfer learning for GRN inference between related cell types in hematopoiesis) is achievable in summer 2026. A general-purpose cross-cell-type GRN model is more ambitious.

### Wet Lab Independence (Rating: High)
Entirely computational. Validation against Perturb-seq data (publicly available CRISPR perturbation screens).

## Competitive Landscape

### Who Else Might Fill This Gap
- **CZ Biohub/CZI:** Building the Virtual Cell initiative, which requires transferable GRN models. Well-funded and actively working on this.
- **Microsoft Research (scGPT team):** Single-cell foundation models that could be extended to GRN inference.
- **Helmholtz Munich (Theis lab):** Leading single-cell computational biology group; developing perturbation prediction methods.

### Risk of Being Scooped
**Medium-High.** The CZ Virtual Cell initiative and foundation model teams are actively working on GRN inference. However, the specific decomposition of GRNs into transferable grammar and cell-type-specific activation is not clearly articulated in any group's published work.

### Differentiation
The focus on explicit decomposition of transferable vs. cell-type-specific regulatory logic, evaluated against rigorous perturbation benchmarks (geneRNIB, CausalBench), distinguishes this from both simple foundation model approaches and traditional GRN methods.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 7 | Transfer learning for GRN inference is underexplored; decomposition approach is novel |
| Scientific impact | 8 | GRN generalization is a fundamental problem in computational biology |
| Feasibility (computational only) | 6 | GRN inference is inherently difficult; real-data performance is the main risk |
| Timeline (summer 2026) | 6 | Focused scope (e.g., hematopoietic system) is achievable; general solution less so |
| Publication potential (Nat Comp Sci) | 7 | Strong if demonstrated on real perturbation data; benchmarks exist |
| **Overall** | **6.8** | Important gap with moderate-high feasibility risk |

---
---

# Cross-Gap Analysis and Synergies

## Connections Between Gaps

These four gaps are deeply interconnected:

1. **Gap 1 (cell-type-specific prediction collapse) feeds Gap 2 (complex trait VEP):** The inability to predict cell-type-specific regulation is a root cause of poor complex trait variant prediction. GWAS variants act in specific cell types; if models fail in cell-type-specific regions, they cannot identify the relevant cell type for a GWAS variant.

2. **Gap 3 (multi-modal integration) could address Gap 1:** A multi-modal model that conditions sequence predictions on observed epigenomic state would naturally improve cell-type-specific prediction, because the epigenome IS the cell-type-specific information.

3. **Gap 4 (GRN generalization) depends on Gap 1:** Inferring GRNs requires knowing which regulatory elements are active in each cell type. If the underlying regulatory predictions are poor in cell-type-specific regions, GRN inference inherits those errors.

4. **Gap 2 + Gap 3 combined:** Integrating fine-mapping with a multi-modal regulatory model would provide both the statistical context (which variants are likely causal) and the functional context (what regulatory effect the variant has in the relevant cell type) needed to break the complex trait prediction barrier.

## Recommended Priority Order

1. **Gap 2 (complex-trait-vep):** Highest overall score (8.4). Most feasible, clearest benchmarking, largest unmet need. Could be completed in summer 2026.
2. **Gap 1 (celltype-reg-collapse):** Second highest score (7.4). Addresses a well-documented problem with clear evaluation metrics. Achievable with focused scope.
3. **Gap 3 (multimodal-reg-genome):** Highest novelty (9) but significant feasibility risk. A focused version (sequence + epigenome, without 3D genome) is more realistic for summer 2026.
4. **Gap 4 (grn-generalization):** Important but most uncertain feasibility. GRN inference is inherently difficult and may require longer timeline.

## Combined Project Possibility

The strongest possible project would combine elements of Gaps 1, 2, and 3: build a multi-modal regulatory model that conditions on cell-type-specific epigenomic data (Gap 1 + 3) and integrate it with statistical fine-mapping to predict complex trait variant mechanisms (Gap 2). This combined project would address the field's most pressing need while being technically novel and computationally demanding enough for the available HPC resources.

---

## References

1. Avsec, Z. et al. (2021). Effective gene expression prediction from sequence by integrating long-range interactions. *Nature Methods*, 18, 1196-1203.
2. Linder, J. et al. (2024). Predicting RNA-seq coverage from DNA sequence as a unifying model of gene regulation. *Nature Genetics*, 56, 1-11.
3. Chen, K.M. et al. (2022). A sequence-based global map of regulatory activity for deciphering human genetics. *Nature Genetics*, 54, 940-949.
4. DeepMind (2025). Advancing regulatory variant effect prediction with AlphaGenome. *Nature*.
5. Hähnel, J. et al. (2025). Flashzoi: an enhanced Borzoi for accelerated genomic analysis. *Bioinformatics*, 41(9).
6. Yengo, L. et al. (2024). Current genomic deep learning models display decreased performance in cell type specific accessible regions. *Genome Biology*, 25, 202.
7. Chen, X. et al. (2025). EpiAgent: foundation model for single-cell epigenomics. *Nature Methods*.
8. Brandes, N. et al. (2025). Benchmarking DNA Sequence Models for Causal Regulatory Variant Prediction in Human Genetics. *bioRxiv/PMC*.
9. Fang, Z. & Wei, Z. (2022). Performance Comparison of Computational Methods for the Prediction of the Function and Pathogenicity of Non-coding Variants. *Computational and Structural Biotechnology Journal*.
10. Alsheikh, A.J. et al. (2022). The landscape of GWAS validation; systematic review identifying 309 validated non-coding variants across 130 human diseases. *BMC Medical Genomics*, 15, 225.
11. GWAS Catalog (2025). NHGRI-EBI GWAS Catalog: standards for reusability, sustainability and diversity. *Nucleic Acids Research*, 53(D1), D998.
12. Roadmap Epigenomics Consortium (2015). Integrative analysis of 111 reference human epigenomes. *Nature*, 518, 317-330.
13. GTEx Consortium (2020). The GTEx Consortium atlas of genetic regulatory effects across human tissues. *Science*, 369, eaaz1776.
14. Chen, L. et al. (2023). A genomic mutational constraint map using variation in 76,156 human genomes. *Nature*, 625, 92-100.
15. Arc Institute (2025-2026). Genome modelling and design across all domains of life with Evo 2. *Nature*.
16. Dalla-Torre, H. et al. (2024). Nucleotide Transformer: building and evaluating robust foundation models for human genomics. *Nature Methods*.
17. geneRNIB (2025). geneRNIB: a living benchmark for gene regulatory network inference. *bioRxiv*.
18. CausalBench (2025). A large-scale benchmark for network inference from single-cell perturbation data. *Communications Biology*.
19. Xu, Z. et al. (2025). CREATE: cell-type-specific cis-regulatory element identification via discrete embedding. *Nature Communications*.
20. MAGE Consortium (2024). Sources of gene expression variation in a globally diverse human cohort. *Nature*.
21. Fulco, C.P. et al. (2019). Activity-by-Contact model of enhancer-promoter regulation from thousands of CRISPR perturbations. *Nature Genetics*, 51, 1664-1669.
22. Gasperini, M. et al. (2019). A genome-wide framework for mapping gene regulation via cellular genetic screens. *Cell*, 176, 377-390.
23. GRaNIE/GRaNPA (2024). Inferring gene regulatory networks from single-cell multiome data using atlas-scale external data. *Nature Biotechnology*.
24. Entropy & Disagreement in Genomic FMs (2025). Entropy, Disagreement, and the Limits of Foundation Models in Genomics. *arXiv:2604.04287*.
25. Comparative deep learning VEP analysis (2025). Comparative Analysis of Deep Learning Models for Predicting Causative Regulatory Variants. *Genes*, 16(10), 1223.
26. OmniReg-GPT (2025). Omnireg-gpt: a high-efficiency foundation model for comprehensive genomic sequence understanding. *Nature Communications*.
27. Gene42 (2025). Gene42: Long-Range Genomic Foundation Model With Dense Attention. *arXiv:2503.16565*.
28. EpiBERT (2025). A multi-modal transformer for cell type-agnostic regulatory predictions. *PMC*.
29. Hi-Compass (2025). Hi-Compass resolves cell-type chromatin interactions by single-cell and spatial ATAC-seq data. *bioRxiv*.
30. FI-Chrom (2025). A data-driven chromatin model reveals spatial and dynamic features of genome organization. *PNAS*.
31. VariantFormer (2025). VariantFormer: A hierarchical transformer integrating DNA sequences with genetic variations. *bioRxiv*.
32. CREsted (2026). CREsted: modeling genomic and synthetic cell-type-specific enhancers across tissues and species. *Nature Methods*.
