---
agent: reggeno
round: 2
date: 2026-04-14
type: deep-dive
---

# Deep Dive: Non-Coding Variant Effect Prediction

## Executive Summary

This deep dive investigates the gap in computational prediction of non-coding variant effects, originally scored 8.4 in Round 1. The central finding is nuanced: **the gap has partially narrowed since Round 1 assessment but remains critically open in specific dimensions**. AlphaGenome (Nature, January 2026) and the Sniff/Borzoi-informed fine-mapping framework (bioRxiv, July 2025) represent significant advances, but neither solves the core problem: integrating deep variant effect prediction with statistical fine-mapping, tissue-specific epigenomics, and clinical context in a unified framework. The near-random performance for common GWAS variants (AUROC 0.48-0.52) reported in earlier benchmarks has been improved by newer models for certain evaluation protocols, but the fundamental challenge of distinguishing causal from non-causal variants in LD blocks persists. A reframed project focusing on **context-aware integrative variant effect prediction** -- combining the strengths of AlphaGenome/Borzoi with fine-mapping posteriors, single-cell epigenomics, and disease context -- remains highly publishable and fills a genuine gap.

---

## 1. Gap Verification

### 1.1 Major Developments Since Round 1

The landscape of non-coding variant effect prediction has evolved substantially in 2025-2026, with three landmark developments:

**AlphaGenome (DeepMind, Nature, January 2026)**
AlphaGenome represents the most significant advance in genomic sequence modeling since Enformer. Key capabilities:
- Takes 1 Mb DNA sequence input, predicts 5,930 human tracks across 11 modalities at up to single-base-pair resolution
- U-Net-inspired backbone with transformer blocks at 128-bp resolution
- Matched or exceeded external models in 25/26 variant effect prediction evaluations
- eQTL sign prediction: AUROC 0.80 vs Borzoi's 0.75
- eQTL coefficient prediction: Spearman rho 0.49 vs Borzoi's 0.39
- eQTL recovery at 90% accuracy: 41% vs Borzoi's 19%
- Inference <1 second on NVIDIA H100 GPU using distilled student model
- Source code and weights released for non-commercial use (January 2026) via Hugging Face and Kaggle
(Marin et al., Nature, 2026; Nature Structural & Molecular Biology perspective, 2026)

**Borzoi-Informed Fine-Mapping / Sniff (bioRxiv, July 2025)**
The first direct integration of a deep sequence model (Borzoi) with statistical fine-mapping (SuSiE via PolyFun):
- Combined Borzoi variant effect predictions with 187 baseline-LF annotations as priors for SuSiE
- Applied to 15 UK Biobank traits
- Identified 9.45% more fine-mapped variants at PIP >0.8 compared to PolyFun-Baseline
- 255 additional likely causal variants across tested traits
- Prioritized variants showed allele-specific activity in reporter assays and tissue-specific activity in trait-relevant tissues
(bioRxiv 2025.07.09.663936)

**EMO -- Epigenomic Multi-modal Organizer (Nature Computational Science, October 2025)**
A transformer-based model integrating DNA sequence with chromatin accessibility:
- Predicts regulatory impact of non-coding SNPs on gene expression across tissues and single-cell landscapes
- Incorporates personalized functional genomic profiles for individual-level predictions
- Identifies cell-type-specific regulatory patterns in single-cell contexts
(Nature Computational Science, 2025)

### 1.2 What the Gap Still Looks Like

Despite these advances, critical gaps persist:

1. **No unified framework exists** that combines deep VEP (AlphaGenome/Borzoi) with fine-mapping posteriors AND tissue-specific epigenomics AND clinical variant context in a single coherent system. Sniff integrates Borzoi with SuSiE but uses annotations as priors, not as a deeply integrated architecture. EMO integrates epigenomics but does not incorporate fine-mapping posteriors.

2. **Common GWAS variant prediction remains weak.** The 2022 benchmark by Li et al. showing AUROC 0.48-0.52 for GWAS variants was conducted with older methods. However, the TraitGym benchmark (February 2025) confirms that even modern models show "much lower" performance on complex traits than Mendelian traits, and that different model families excel at different variant types -- no single model dominates.

3. **Cell-type specificity is inadequate.** AlphaGenome predicts across many tracks but does not natively condition on cell state. The Virtual Cells perspective paper (bioRxiv 2026) explicitly argues that "cellular response is context-dependent -- the same genetic perturbation produces different transcriptional outcomes depending on the cell's activation state, microenvironment, and epigenetic history."

4. **The variant-to-gene-to-mechanism pipeline is fragmented.** Moving from "this variant affects this track" to "this variant causes this disease through this gene in this tissue" requires integration across multiple tools and data types that currently do not communicate.

### 1.3 Gap Status Assessment

**Original gap (near-random GWAS variant prediction):** PARTIALLY CLOSED by AlphaGenome and Borzoi for eQTL-overlapping variants, but STILL OPEN for the broader set of GWAS common variants in LD blocks.

**Reframed gap (context-aware integrative variant effect prediction):** FULLY OPEN and more precisely defined by recent work showing the limitations of single-modality approaches.

---

## 2. Near-Random Performance Evidence

### 2.1 The Landmark Li et al. (2022) Benchmark

The most cited evidence for near-random GWAS variant prediction comes from Li et al. (Genomics, Proteomics & Bioinformatics, 2022), who systematically evaluated 24 computational methods across four benchmark datasets:

**Benchmark datasets:**
- Rare germline variants (ClinVar): 515 positive, 1,850 negative
- Rare somatic variants (COSMIC): 1,966 positive, 597,221 negative
- Common regulatory variants (eQTL): 13,274 positive, 13,274 negative
- Disease-associated common variants (GWAS): 73,693 positive, 76,214 negative

**AUROC ranges by variant type:**
| Variant Type | AUROC Range | Median AUROC |
|---|---|---|
| Rare germline (ClinVar) | 0.4481-0.8033 | 0.6988 |
| Rare somatic (COSMIC) | 0.4984-0.7131 | 0.6295 |
| Common regulatory (eQTL) | 0.4837-0.6472 | 0.5619 |
| Common GWAS | **0.4766-0.5188** | **0.5041** |

The GWAS results (median AUROC 0.5041, essentially coin-flip) are robust across all 24 methods tested. FATHMM-XF was the best performer for rare variants (0.8033) but dropped precipitously for common variants.

### 2.2 Why Performance Is Near-Random for GWAS Variants

Several explanations emerge from the literature:

1. **LD block problem:** GWAS variants and their controls are often in the same LD block. Methods that distinguish functional from non-functional regions perform well in relaxed evaluations but fail when negatives are drawn from the same regulatory landscape as positives.

2. **Small effect sizes:** Common GWAS variants typically have very small effect sizes (OR 1.05-1.20), making their functional signatures subtle and hard to distinguish computationally.

3. **Evaluation artifact vs. real limitation:** As noted in the comprehensive review by Huang et al. (arXiv:2411.11158, 2024), "Different choices of negative set can yield vastly different results." However, this cuts both ways -- the near-random performance under stringent evaluation is arguably the most meaningful test.

4. **Polygenicity:** For complex traits, the signal is distributed across hundreds to thousands of variants, each contributing marginally.

### 2.3 Updated Performance with Modern Models (2025-2026)

The TraitGym benchmark (February 2025) provides the most up-to-date comparison:

**Models benchmarked:** Enformer (246M params), Sei (890M params), Borzoi (186M params), GPN-MSA (86M), Nucleotide Transformer (2.5B), HyenaDNA (14M), Caduceus (8M), AIDO.DNA (7B), Evo2 (40B), CADD, phastCons, phyloP

**Key findings:**
- For Mendelian traits: GPN-MSA achieves substantial margin over other models
- For complex non-disease traits: Enformer and Borzoi excel with linear probing
- For complex disease traits: Alignment-based models (CADD, GPN-MSA) compare favorably
- Ensemble of Borzoi + GPN-MSA + CADD achieves best combined performance
- eQTL-overlapping variants are "much easier to predict" than non-eQTL variants
- Overall complex trait scores remain "much lower than in Mendelian traits"

**AlphaGenome (January 2026):**
- eQTL sign AUROC: 0.80 (vs Borzoi 0.75, Enformer ~0.72)
- eQTL coefficient Spearman rho: 0.49 (vs Borzoi 0.39)
- MPRA prediction (CAGI5): Pearson r = 0.57-0.65 depending on aggregation
- ClinVar pathogenic (deep intronic/synonymous): auPRC 0.66

**Critical assessment:** The near-random performance for *general GWAS common variant classification* has NOT been solved. AlphaGenome improves substantially on eQTL-associated variants and specific functional assay predictions, but the core challenge of distinguishing causal from non-causal common variants in LD blocks remains.

### 2.4 Comparative Analysis of Deep Learning Models (2025)

A separate benchmark by Kaltsas et al. (Genes, 2025) focused on predicting causative regulatory variants in enhancers using experimentally validated MPRA data:
- CNN-based models (TREDNet, SEI) achieved best alignment with experimental variant effects: Pearson r = 0.297 and 0.276, respectively
- The best transformer-based model (Nucleotide Transformer v2) achieved only r = 0.105
- This highlights that larger models do not automatically yield better variant effect predictions

---

## 3. Data Availability Audit

### 3.1 GWAS Data Scale

**GWAS Catalog (as of 2025):**
- >7,400 curated publications
- >1,040,000 reported SNP-trait associations
- ~625,000 lead associations
- 85,000 full genome-wide summary statistics datasets
- >15,000 traits represented

**UK Biobank GWAS:**
- Summary statistics available for hundreds of traits
- Sample sizes typically 300,000-500,000 individuals
- Fine-mapping conducted via multiple methods (SuSiE, FINEMAP, SUSIE-inf)

### 3.2 Fine-Mapping Data (SuSiE Credible Sets)

**Open Targets Genetics (2025):**
- 133,441 loci with fine-mapping credible sets
- 2.37 million human candidate cis-regulatory elements (cCREs) in ENCODE SCREEN
- Locus-to-Gene (L2G) machine-learning algorithm ranks causal genes at each credible set
- 6.5 million rare and common variants with functional context
- Binary and quantitative traits from GWAS Catalog and FinnGen (R12)
- SuSiE-inf applied with pan-UKBB LD matrices

**CAUSALdb2 (2025):**
- 15,057 GWAS summary statistics across 10,839 unique traits
- Both LD-based and LD-free fine-mapping approaches
- Integration of TOPMED and UK Biobank LD panels
- Functional annotations via PolyFun integrated

**FinnGen:**
- R12 release with fine-mapping for Finnish population
- SuSiE credible sets available for download

### 3.3 Experimental Validation Data

**MPRA datasets:**
- Melanoma: 1,992 variants tested, 285 showing significant allelic activity across 42 loci (Choi et al., AJHG, 2022)
- Psychiatric disorders: >20,000 variants tested in human neural progenitors, including 177 psychiatric GWAS variants (Cell, 2024)
- Autoimmune: >18,000 variants tested in primary human CD4+ T cells, 545 with allele-specific effects (emVars) (Nature Genetics, 2025)
- Schizophrenia: 5,173 fine-mapped variants in neural progenitors, 439 with allelic regulatory effects (Lett et al.)
- Neuronal enhancers: >50,000 sequences in induced human neurons (Nature Communications, 2025)
- CAD: >25,000 variants in vascular smooth muscle cells (Nature Cardiovascular Research, 2025)

**CRISPRi/CRISPR validation:**
- CRAFTseq multi-omic single-cell approach for variant effect testing (Nature, 2025)
- Single-cell CRISPR screens in primary T cells mapping non-coding regulatory elements (Genome Biology, 2024)

**MaveDB (2024 update):**
- >7 million variant effect measurements
- 1,884 datasets
- Supports non-coding targets with nucleotide-level heatmaps
- Includes MPRA and saturation genome editing data

### 3.4 Epigenomic and Expression Data

**GTEx v8:**
- 53 tissue sites, ~1,000 individuals
- 449 donors, 44 tissues
- 18,262 protein-coding genes with cis-eQTLs
- 4,278,636 variants significant in at least 1 tissue (43% of all variants with MAF >= 0.01)
- Fine-mapping via CaVEMaN, CAVIAR, and dap-g

**ENCODE (Phase 4):**
- 2,348,854 human cCREs (GRCh38) -- expanded from 0.9M in previous release
- >90% of cCREs profiled by functional characterization (STARR-seq, MPRA, CRISPR, transgenic mouse)
- Hundreds of unique cell and tissue types

**EpiMap:**
- 10,000 epigenomic maps across 800 samples
- Chromatin states, high-resolution enhancers, enhancer modules
- 20,000 GWAS loci annotated across 232 traits

**Single-cell eQTL atlases:**
- OneK1K: 1.27 million PBMCs from 982 donors, 14 immune cell types, 26,597 cis-eQTLs
- JOBS method (2025): 586% more eQTLs; 29.9-32.2% more GWAS colocalizations vs single-modality eQTL

### 3.5 ClinVar Non-Coding Variant Data

**ClinVar (June 2025):**
- 5,432,546 submissions on 3,591,080 variants total
- Only ~0.34% of high-confidence pathogenic variants are in UTRs/upstream regions
- Non-coding regulatory variants significantly underrepresented
- This represents both a limitation (sparse training data for regulatory variants) and an opportunity (enormous unresolved VUS burden)

**Data availability verdict:** Abundant data exists across all required modalities. The bottleneck is not data availability but integration -- no existing pipeline unifies deep VEP scores, fine-mapping posteriors, tissue-specific epigenomics, and experimental validation in a coherent framework.

---

## 4. Model Availability and Requirements

### 4.1 AlphaGenome

| Attribute | Detail |
|---|---|
| **Availability** | Open-sourced January 2026 (non-commercial) |
| **Weights** | Hugging Face (google/alphagenome-all-folds), Kaggle |
| **Code** | GitHub: google-deepmind/alphagenome (JAX implementation) |
| **Research code** | GitHub: google-deepmind/alphagenome_research |
| **API** | Free for non-commercial use; suitable for <1M predictions |
| **GPU requirement** | Minimum 1x NVIDIA H100 for inference |
| **Inference speed** | <1 second per variant on H100 (distilled model) |
| **Training** | 8x TPU v3 with sequence parallelism (1 Mb split into 131 kb chunks) |
| **Input** | 1 Mb DNA sequence |
| **Output** | 5,930 human / 1,128 mouse tracks across 11 modalities |
| **Resolution** | 1-bp (RNA-seq, ATAC, DNase, splice) to 2,048-bp (contact maps) |
| **Framework** | JAX |
| **Community port** | PyTorch port available (gtca/alphagenome_pytorch on HF) |

**H200 compatibility:** The H200 has more HBM3e memory than H100 (141 GB vs 80 GB). Since AlphaGenome runs on a single H100, it will run comfortably on H200. Batch processing of millions of variants is feasible.

### 4.2 Borzoi / Flashzoi

| Attribute | Detail |
|---|---|
| **Availability** | Open-source (Calico, Apache 2.0) |
| **Weights** | HuggingFace (johahi/borzoi-replicate-0), .h5 files |
| **Code** | GitHub: calico/borzoi (TensorFlow), johahi/borzoi-pytorch (PyTorch) |
| **Parameters** | 186M |
| **Input** | ~524 kb DNA sequence |
| **Output** | >10,000 genomic assay tracks at 32-bp resolution |
| **GPU requirement** | Standard GPU sufficient; specific VRAM not published |
| **Flashzoi variant** | 3x faster training/inference, 2.4x reduced memory (FlashAttention-2 + rotary embeddings) |
| **Published** | Nature Genetics (2024); Flashzoi in Bioinformatics (2025) |

### 4.3 Enformer

| Attribute | Detail |
|---|---|
| **Availability** | Open-source (Google DeepMind) |
| **Parameters** | 246M |
| **Input** | ~200 kb DNA sequence |
| **Output** | 5,313 tracks at 128-bp resolution |
| **Kipoi** | Available in Kipoi model repository |
| **Note** | Superseded by AlphaGenome for most tasks |

### 4.4 Sei

| Attribute | Detail |
|---|---|
| **Availability** | Open-source (Troyanskaya lab, Princeton) |
| **Parameters** | 890M |
| **Output** | 21,907 chromatin profiles, 40 sequence classes |
| **Framework** | PyTorch |
| **Note** | Strong on enhancer variant effects (Pearson r 0.276 vs experimental) |

### 4.5 Evo2

| Attribute | Detail |
|---|---|
| **Availability** | Open-source (Arc Institute) |
| **Parameters** | 7B and 40B versions |
| **Context** | 1M tokens with single-nucleotide resolution |
| **Published** | Nature (2026) |
| **Note** | Outperforms on non-coding non-SNV variants; 40B suffers accuracy issues on non-FP8 hardware |

### 4.6 Additional Relevant Models

- **ChromBPNet:** Base-pair resolution chromatin accessibility prediction (open-source)
- **EpiGePT:** Transformer for context-specific epigenomics (2024)
- **EpiBERT:** Multi-modal transformer for cell type-agnostic regulatory predictions (Cell Genomics, 2025)
- **OmniReg-GPT:** 270M parameter hybrid-attention model for regulatory element prediction (Nature Communications, 2025)
- **EPInformer:** Lightweight (0.4M params) enhancer-promoter interaction model (Nature Communications, 2026)

**Compute feasibility verdict:** All major models are available open-source with weights. H200 GPUs provide more than sufficient memory and compute for inference. Training custom integration layers is feasible. The API limit for AlphaGenome (~1M predictions) may require local deployment for genome-wide scoring, which is achievable on H200.

---

## 5. Integration Framework Design

### 5.1 Architecture Overview: Context-Aware Variant Effect Integration (CAVE)

The proposed framework integrates four signal types at the variant level:

```
Layer 1: Deep Sequence Models
    AlphaGenome (1 Mb context, 5,930 tracks, 1-bp resolution)
    + Borzoi/Flashzoi (524 kb context, RNA-seq specialization)
    + Evo2 (1M token context, evolutionary conservation signal)
    --> Variant-level multi-model feature vectors

Layer 2: Statistical Fine-Mapping Integration
    SuSiE posterior inclusion probabilities (PIPs)
    + PolyFun functional priors
    + Multi-ancestry fine-mapping (SuSiEx)
    --> Bayesian causal probability estimates

Layer 3: Context-Specific Epigenomics
    Cell-type/tissue-specific chromatin accessibility (ENCODE cCREs)
    + Single-cell eQTL maps (OneK1K, GTEx)
    + Disease-relevant epigenomic profiles
    --> Context-dependent functional activity scores

Layer 4: Integration and Prediction
    Gradient-boosted ensemble OR transformer-based cross-attention
    --> Unified variant effect scores with:
        - Causal probability
        - Effect direction and magnitude
        - Tissue/cell-type specificity
        - Confidence calibration
```

### 5.2 Key Design Decisions

**Why not just use AlphaGenome?**
AlphaGenome excels at predicting molecular effects from sequence alone but:
- Does not incorporate population-level association data (GWAS, fine-mapping)
- Does not natively condition on cell state or disease context
- Cannot distinguish causal from correlated variants in LD
- Multimodal random forest on AlphaGenome features improved eQTL causality from AUROC 0.68 to 0.75 -- good but still 25% of causal variants missed

**Why combine with fine-mapping?**
Fine-mapping provides the crucial statistical signal that discriminates causal from LD-correlated variants. The Sniff framework demonstrated that Borzoi + SuSiE integration yields 9.45% more causal variants. AlphaGenome features should amplify this further.

**Why add epigenomic context?**
The same variant can be functional in one cell type and neutral in another. The OneK1K single-cell eQTL atlas showed 29-32% more GWAS colocalizations by incorporating cell-type specificity. Disease context (e.g., activated vs resting immune cells for autoimmune disease) matters enormously.

### 5.3 Technical Implementation Path

**Phase 1 (Months 1-2): Feature extraction**
- Score all GWAS variants (1M+) through AlphaGenome (local deployment on H200, <1 second per variant)
- Score through Borzoi/Flashzoi (open-source, GPU-accelerated)
- Extract Evo2 conservation-like scores for each variant
- Aggregate SuSiE PIPs from Open Targets, CAUSALdb2, and FinnGen

**Phase 2 (Months 2-3): Context integration**
- Map variants to tissue/cell-type-specific cCREs (2.37M ENCODE cCREs)
- Overlay with GTEx tissue-specific eQTL effects (53 tissues)
- Integrate OneK1K single-cell eQTL data for immune-relevant traits
- Create variant x tissue x model feature tensors

**Phase 3 (Months 3-4): Model training and evaluation**
- Train integration model on experimentally validated variants (MPRA, CRISPRi)
- Evaluate on held-out traits using TraitGym benchmark
- Calibrate confidence scores using Bayesian framework
- Compare against individual models and Sniff/PolyFun baseline

**Phase 4 (Month 5): Application and publication**
- Apply to disease-specific proof-of-concept systems
- Generate mechanistic hypotheses for top-ranked novel causal variants
- Benchmark against AlphaGenome alone, Borzoi alone, and Sniff

### 5.4 What Makes This Different From Sniff?

Sniff (Borzoi + PolyFun/SuSiE) is the closest existing work. Our framework differs in:

1. **Multi-model ensemble:** AlphaGenome + Borzoi + Evo2 vs Borzoi alone (complementary signal types)
2. **Explicit cell-type conditioning:** Single-cell eQTL and context-specific epigenomics as input features vs using annotations only as fine-mapping priors
3. **Disease-specific contextualization:** Disease-relevant cell states and tissues as conditioning variables
4. **Deeper integration:** Cross-attention or graph neural network integrating all layers vs linear combination of priors
5. **Broader validation:** Training on combined MPRA + CRISPRi data across diseases vs evaluation on reporter assays only

---

## 6. Proof-of-Concept Disease Systems

### 6.1 Tier 1: Autoimmune Diseases (Recommended Primary System)

**Rationale:** Best combination of GWAS scale, fine-mapping resolution, functional validation data, and cell-type-specific resources.

**Available data:**
- >300 loci for rheumatoid arthritis, lupus, type 1 diabetes, inflammatory bowel disease, multiple sclerosis
- OneK1K single-cell eQTL atlas: 14 immune cell types, 26,597 cis-eQTLs, 982 donors
- 18,000+ autoimmune variants tested by MPRA in CD4+ T cells with 545 emVars identified
- CRISPRi screens in primary T cells linking variant CREs to target genes
- Over 330 SLE loci, 76-81% in enhancers/TF-binding elements
- Single-cell CRISPR screens (CRAFTseq) providing ground truth

**Specific advantages:**
- Immune cell types well-characterized epigenomically (ENCODE, Roadmap, BLUEPRINT)
- Cell-type specificity is crucial (different variants active in CD4+ T cells vs B cells vs monocytes)
- Transition from resting to activated states creates natural context-dependence test
- Direct connection to transmed's VUS gap: autoimmune VUS in non-coding regions

### 6.2 Tier 2: Type 2 Diabetes

**Rationale:** Most extensively fine-mapped complex trait with rich tissue-specific data.

**Available data:**
- 243 loci, 403 distinct association signals (latest GWAS)
- Fine-mapped credible sets including 42 associations with <5 variants in 95% credible set
- MTNR1B locus as gold-standard functional validation example
- Pancreatic islet epigenomics deeply characterized
- 95% of variants in non-coding regions
- Bridging the variant-to-function gap review (Diabetologia, 2025) provides comprehensive framework

**Specific advantages:**
- Tissue specificity well-defined (islets, liver, adipose, muscle)
- FOXA2 ChIP-seq provides TF binding validation
- Strong existing fine-mapping from multi-ancestry studies

### 6.3 Tier 3: Coronary Artery Disease

**Available data:**
- 393 loci, ~18,500 variants in LD with proxies
- 95% in non-coding regions
- MPRA on >25,000 variants in vascular smooth muscle cells (2025)
- 60% of variants overlap with cis-regulatory elements
- 42 associations with <5 variants in 95% credible set via functionally informed fine-mapping

### 6.4 Tier 3: Schizophrenia/Psychiatric Disorders

**Available data:**
- 287+ significant loci
- MPRA of 5,173 fine-mapped variants in neural progenitors (439 with allelic effects)
- 249 functional variants affecting TF binding across 99 loci
- Brain-specific eQTLs and splicing QTLs
- Cross-disorder MPRA in neural progenitors testing >20,000 variants

### 6.5 Recommended Strategy

**Primary proof-of-concept:** Autoimmune diseases (best data density, clearest cell-type specificity story, direct clinical relevance for VUS interpretation)

**Secondary validation:** Type 2 diabetes (independent disease, different tissue biology, demonstrates generalizability)

**Extended application:** Show framework transfers across all four disease categories with consistent improvement over single-model baselines.

---

## 7. Competition Assessment

### 7.1 Direct Competitors

**Google DeepMind (AlphaGenome team)**
- Published AlphaGenome (Nature, January 2026)
- Multimodal random forest on AlphaGenome features for eQTL causality (AUROC 0.68 to 0.75)
- NOT pursuing deep integration with fine-mapping or clinical context
- Their focus appears to be on improving the base model, not the integration pipeline
- Risk: They could build exactly what we propose, but their publication trajectory suggests continued model development rather than integrative pipelines

**Kellis Lab (MIT/Broad) -- Sniff**
- Borzoi-informed fine-mapping (bioRxiv, July 2025)
- 15 UK Biobank traits, 9.45% improvement in causal variant identification
- Uses Borzoi only (not AlphaGenome or multi-model ensemble)
- Does not incorporate cell-type-specific epigenomics or disease context
- Risk: Could extend to AlphaGenome; close to our proposed approach but narrower in scope

**Troyanskaya Lab (Princeton) -- Sei, FUN-LDA**
- Developed Sei (sequence class framework, 890M params)
- Focus on regulatory vocabulary rather than variant-level integration
- Active in functional annotation space but not in fine-mapping integration

**Kundaje Lab (Stanford) -- ChromBPNet**
- Base-pair resolution accessibility models
- Contributed to AlphaGenome benchmarks
- Not pursuing integrative variant-to-disease pipelines directly

**Lappalainen Lab (NYU/New York Genome Center)**
- Leading work on variant effect prediction evaluation and benchmarking
- Co-authored comprehensive review (arXiv:2411.11158)
- Focus on evaluation methodology rather than new integrative frameworks

**Finucane Lab (Broad) -- PolyFun**
- Developed PolyFun for functionally informed fine-mapping
- Collaborative with Sniff team
- May extend PolyFun to incorporate newer models

**Arc Institute -- Evo2**
- 40B parameter genome model
- Strong on non-SNV variants and non-coding regions
- Focus on generative modeling, not clinical variant interpretation

### 7.2 Competition Risk Assessment

| Risk Factor | Level | Mitigation |
|---|---|---|
| DeepMind builds integrative pipeline | Medium | Our focus on clinical context and disease specificity differentiates |
| Sniff extends to AlphaGenome | Medium-High | We include multi-model ensemble + cell-type conditioning, which is architecturally different |
| New benchmark paper makes gap seem closed | Low | TraitGym already shows complex trait variants remain hard |
| Someone else publishes similar framework | Medium | Speed of execution matters; 5-month timeline is aggressive |

### 7.3 Differentiating Factors

Our approach is unique in combining ALL of:
1. Multi-model deep VEP ensemble (AlphaGenome + Borzoi + Evo2)
2. Bayesian fine-mapping integration (SuSiE/PolyFun posteriors as features, not just priors)
3. Context-specific conditioning (cell-type, tissue, disease state)
4. Clinical VUS framework (connecting to translational medicine)
5. Comprehensive validation across 4+ disease systems

No published or preprinted work combines all five. The closest (Sniff) covers only items 1 (partially, Borzoi only) and 2.

---

## 8. Feasibility Reassessment

### 8.1 Compute Requirements

| Task | Compute | Time Estimate |
|---|---|---|
| AlphaGenome scoring of 1M variants | 1x H200, <1 sec/variant | ~12 days (with batching: 2-3 days) |
| Borzoi/Flashzoi scoring of 1M variants | 1x GPU, 3x faster with Flashzoi | ~1-2 days |
| Evo2 (7B) scoring | 1x H200 | ~3-5 days |
| Feature extraction + tensor construction | CPU cluster | ~1 day |
| Integration model training | 1-4x GPU | ~1-2 weeks (multiple experiments) |
| End-to-end pipeline | H200 cluster | ~3-4 weeks total compute |

**Available resources:** HPC cluster with H200, RTX 5000 Ada, B200 GPUs; SLURM scheduler. This is more than sufficient. AlphaGenome requires minimum H100; H200 exceeds this. Borzoi/Flashzoi run on any modern GPU.

### 8.2 Data Accessibility

| Data Source | Access | Format | Size Estimate |
|---|---|---|---|
| AlphaGenome weights | HuggingFace/Kaggle (non-commercial) | JAX/PyTorch | ~GBs |
| Borzoi weights | HuggingFace | PyTorch/TF | ~GBs |
| Evo2 weights | GitHub (Arc Institute) | PyTorch | 7B: ~14 GB; 40B: ~80 GB |
| GWAS Catalog summary stats | EBI download | TSV | ~TBs total |
| Open Targets fine-mapping | API + download | Parquet | ~GBs |
| CAUSALdb2 | Public database | Various | ~GBs |
| GTEx v8 eQTLs | dbGaP (controlled) or summary stats | TSV | ~GBs |
| OneK1K sc-eQTL | onek1k.org | Various | ~GBs |
| ENCODE cCREs | SCREEN download | BED | ~MBs |
| MPRA data | GEO/supplementary | Various | ~MBs per study |
| MaveDB | API/download | CSV/JSON | Varies |

**Data access concerns:**
- GTEx individual-level data requires dbGaP access (controlled), but summary statistics are public
- AlphaGenome is non-commercial use only -- this is fine for academic publication
- All other resources are fully public

### 8.3 Timeline Assessment

| Month | Activity |
|---|---|
| Month 1 | Data acquisition, pipeline setup, model deployment |
| Month 2 | Feature extraction across all models and data sources |
| Month 3 | Integration model development and training |
| Month 4 | Validation on held-out diseases, benchmarking |
| Month 5 | Publication preparation, visualization, ablation studies |

**Risk factors:**
- AlphaGenome local deployment may require debugging JAX setup on HPC (mitigated by PyTorch port availability)
- Large-scale variant scoring is embarrassingly parallel, so scales well
- Integration model architecture requires careful design to avoid overfitting on small validation sets

### 8.4 Feasibility Verdict

**HIGHLY FEASIBLE.** All models are open-source with weights. All data is publicly available. H200 GPUs exceed minimum requirements. The 5-month timeline is tight but achievable given that no new model training from scratch is needed -- only feature extraction and integration layer training.

---

## 9. Publication Framing

### 9.1 Target Venue

**Primary:** Nature Computational Science
**Secondary:** Nature Methods or Nature Genetics

**Rationale for Nature Computational Science:**
- EMO (epigenomic integration for variant prediction) was published there in October 2025
- The journal prioritizes computational frameworks that enable new biological insights
- Our approach is methodological with immediate biological applications
- The multi-model integration paradigm is novel computational methodology

### 9.2 Proposed Title Options

1. "Context-Aware Variant Effect Integration (CAVE): Unifying Deep Genomic Models with Fine-Mapping and Epigenomics for Non-Coding Variant Interpretation"
2. "Beyond Sequence: Integrating Deep Variant Effect Prediction with Statistical Fine-Mapping and Disease Context for Non-Coding Variant Prioritization"
3. "Bridging the Variant-to-Function Gap through Multi-Modal Integration of Sequence Models, Fine-Mapping, and Cell-Type-Specific Epigenomics"

### 9.3 Main Claim

"We present CAVE, a framework that integrates variant effect predictions from multiple deep genomic models (AlphaGenome, Borzoi, Evo2) with Bayesian fine-mapping posteriors and cell-type-specific epigenomic context to achieve state-of-the-art performance in prioritizing causal non-coding variants for complex diseases, substantially outperforming any individual model or existing integration approach."

### 9.4 Key Figures

**Figure 1:** Framework overview showing four integration layers and data flow
**Figure 2:** Benchmarking on TraitGym comparing CAVE vs individual models, Sniff, and CADD across Mendelian and complex trait categories
**Figure 3:** Autoimmune disease case study showing cell-type-specific variant prioritization with experimental validation rates
**Figure 4:** Type 2 diabetes application demonstrating tissue-specific variant-to-gene-to-mechanism paths
**Figure 5:** Ablation studies showing contribution of each integration layer
**Figure 6:** Clinical VUS reclassification potential -- how many non-coding VUS could be reclassified using CAVE scores

### 9.5 Anticipated Reviewer Concerns

| Concern | Response |
|---|---|
| "This is just feature engineering on top of existing models" | The integration architecture with cross-attention and context-conditioning is non-trivial; ensemble approaches consistently outperform individual models (TraitGym) but nobody has done it systematically with the newest models |
| "AlphaGenome already solves this" | AlphaGenome improves variant-level prediction but does not incorporate fine-mapping posteriors or disease context; show specific examples where CAVE identifies causal variants that AlphaGenome alone misses |
| "Evaluation is cherry-picked" | Use standardized TraitGym benchmark + multiple disease systems + multiple validation datasets (MPRA, CRISPRi) |
| "Validation is purely computational" | MPRA and CRISPRi ground truth IS experimental validation, just not performed by us. Also generate testable predictions for follow-up |
| "Not novel enough" | The combination of ALL five components (multi-model, fine-mapping, context, clinical VUS, multi-disease) has not been published |

### 9.6 Comparison Baselines Required

1. AlphaGenome alone (feature-level and multimodal RF)
2. Borzoi alone
3. Evo2 alone
4. CADD
5. Sniff (Borzoi + PolyFun/SuSiE)
6. PolyFun baseline (SuSiE without deep VEP)
7. EMO (if code available)
8. Ensemble of 1-3 without fine-mapping
9. CAVE without context conditioning (ablation)
10. CAVE full model

---

## 10. Combined Project Beta Design

### 10.1 Convergence with Transmed's Context-Dependent VUS Gap

The transmed specialist identified a parallel gap: context-dependent interpretation of Variants of Uncertain Significance (VUS), particularly for non-coding variants where tissue/cell-type context determines pathogenicity. These gaps converge naturally:

**Reggeno gap:** Deep VEP models achieve near-random GWAS variant prediction; need integration with fine-mapping and context
**Transmed gap:** VUS reclassification requires tissue-specific and disease-context-aware computational prediction

**Combined insight:** The fundamental problem is the same -- predicting whether a non-coding variant is functionally meaningful requires integrating sequence-level predictions with population genetics (fine-mapping) and biological context (cell type, disease state, patient genotype).

### 10.2 Unified Project: Context-Aware Variant Effect Integration (CAVE)

**Mission:** Build an integrative computational framework that unifies deep genomic sequence models, statistical fine-mapping, and cell-type-specific epigenomics to (a) prioritize causal non-coding variants at GWAS loci and (b) reclassify non-coding VUS in clinical genomics.

**Two complementary outputs from one framework:**
1. **Research output (reggeno focus):** Systematic identification of causal non-coding variants across 4+ disease systems, improving upon AlphaGenome and Sniff
2. **Clinical output (transmed focus):** VUS reclassification scores for non-coding variants with tissue-specific pathogenicity estimates

### 10.3 Combined Architecture

```
                     CAVE Framework
    ================================================
    |                                              |
    |  Sequence Layer:                             |
    |    AlphaGenome + Borzoi + Evo2               |
    |         |                                    |
    |  Fine-Mapping Layer:                         |
    |    SuSiE PIPs + PolyFun priors               |
    |         |                                    |
    |  Context Layer:                              |
    |    Cell-type epigenomics + sc-eQTL           |
    |    Disease state + patient genotype           |
    |         |                                    |
    |  Integration:                                |
    |    Cross-attention + calibrated ensemble      |
    |         |                                    |
    |    +-----------+    +-----------+            |
    |    | Research  |    | Clinical  |            |
    |    | Variant   |    | VUS       |            |
    |    | Causal    |    | Reclassi- |            |
    |    | Ranking   |    | fication  |            |
    |    +-----------+    +-----------+            |
    ================================================
```

### 10.4 Division of Labor

**Reggeno contributions:**
- Regulatory genomics expertise for feature engineering
- GWAS/fine-mapping data curation and processing
- Epigenomic context integration design
- Evaluation on complex trait GWAS benchmarks
- Enhancer and regulatory element analysis

**Transmed contributions:**
- Clinical VUS interpretation framework
- Disease-specific validation cohorts
- Translational framing and clinical impact assessment
- Patient-level genotype integration
- Drug target and therapeutic implication analysis

### 10.5 Publication Strategy for Combined Project

**Option A (Single high-impact paper):**
- "Context-Aware Variant Effect Integration: Unifying Sequence Models, Fine-Mapping, and Disease Context for Non-Coding Variant Interpretation and VUS Reclassification"
- Target: Nature Computational Science or Nature Methods
- Advantage: Maximum impact; demonstrates both research and clinical utility
- Risk: Paper becomes unwieldy; reviewers may find scope too broad

**Option B (Two complementary papers):**
- Paper 1 (reggeno lead): "CAVE: Multi-Modal Integration of Deep Genomic Models for Non-Coding Causal Variant Prioritization" -- Nature Computational Science
- Paper 2 (transmed lead): "Context-Aware VUS Reclassification for Non-Coding Regulatory Variants Using Integrated Sequence and Epigenomic Models" -- Nature Medicine or American Journal of Human Genetics
- Advantage: Focused narratives; broader impact across venues
- Risk: Need to be published in close succession; shared framework needs clear attribution

**Recommendation:** Option A for maximum impact, with extensive supplementary methods allowing the clinical application to stand alone if reviewers request splitting.

### 10.6 What Makes Combined Project Beta Stronger Than Separate Projects

1. **Shared infrastructure:** Same feature extraction pipeline serves both research and clinical outputs
2. **Cross-validation:** GWAS causal variant identification validates VUS predictions and vice versa
3. **Broader impact narrative:** From basic research (what variants cause disease) to clinical application (which patient variants matter)
4. **Larger validation surface:** MPRA/CRISPRi data validates research claims; ClinVar data validates clinical claims
5. **Publication competitiveness:** Dual research+clinical angle differentiates from pure-methods papers

---

## References

1. Marin, S. et al. Advancing regulatory variant effect prediction with AlphaGenome. *Nature* (2026). doi:10.1038/s41586-025-10014-0

2. Linder, J. et al. Predicting RNA-seq coverage from DNA sequence as a unifying model of gene regulation. *Nature Genetics* 57, 340-350 (2024). doi:10.1038/s41588-024-02053-6

3. Hahne, J. et al. Flashzoi: an enhanced Borzoi for accelerated genomic analysis. *Bioinformatics* 41(9), btaf467 (2025).

4. Li, S. et al. Performance Comparison of Computational Methods for the Prediction of the Function and Pathogenicity of Non-coding Variants. *Genomics, Proteomics & Bioinformatics* 20(5), 951-963 (2022). doi:10.1016/j.gpb.2022.02.002

5. Borzoi-informed fine mapping improves causal variant prioritization in complex trait GWAS. *bioRxiv* (2025). doi:10.1101/2025.07.09.663936

6. Huang, Y.-F. et al. Leveraging genomic deep learning models for the prediction of non-coding variant effects. *arXiv* 2411.11158v2 (2024).

7. TraitGym: Benchmarking DNA Sequence Models for Causal Regulatory Variant Prediction in Human Genetics. *bioRxiv* (2025). doi:10.1101/2025.02.11.637758

8. Weissbrod, O. et al. Functionally informed fine-mapping and polygenic localization of complex trait heritability. *Nature Genetics* 52, 1355-1363 (2020). doi:10.1038/s41588-020-00735-5

9. Nguyen, E. et al. Genome modeling and design across all domains of life with Evo 2. *Nature* (2026). doi:10.1038/s41586-026-10176-5

10. Chen, K. M. et al. A sequence-based global map of regulatory activity for deciphering human genetics. *Nature Genetics* 54, 1130-1140 (2022). doi:10.1038/s41588-022-01102-2

11. EMO: Predicting the regulatory impacts of noncoding variants on gene expression through epigenomic integration across tissues and single-cell landscapes. *Nature Computational Science* (2025). doi:10.1038/s43588-025-00878-7

12. Yazar, S. et al. Single-cell eQTL mapping identifies cell type-specific genetic control of autoimmune disease. *Science* 376, eabf3041 (2022).

13. An atlas of single-cell eQTLs dissects autoimmune disease genes and identifies novel drug classes for treatment. *Cell Genomics* (2025). doi:10.1016/j.xgen.2025.100076

14. The ENCODE Project Consortium. An expanded registry of candidate cis-regulatory elements. *Nature* (2025). doi:10.1038/s41586-025-09909-9

15. The GTEx Consortium atlas of genetic regulatory effects across human tissues. *Science* 369, 1318-1330 (2020).

16. MaveDB 2024: a curated community database with over seven million variant effects from multiplexed functional assays. *Genome Biology* 26, 19 (2025).

17. Li, Y. et al. Funmap: integrating high-dimensional functional annotations to improve fine-mapping. *Bioinformatics* 41(1), btaf017 (2025).

18. The landscape of GWAS validation; systematic review identifying 309 validated non-coding variants across 130 human diseases. *BMC Medical Genomics* 15, 74 (2022).

19. CAUSALdb2: an updated database for causal variants of complex traits. *Nucleic Acids Research* 53(D1), D1295-D1302 (2025).

20. Kaltsas, A. et al. Comparative Analysis of Deep Learning Models for Predicting Causative Regulatory Variants. *Genes* 16(10), 1223 (2025).

21. Genetic and epigenetic screens in primary human T cells link candidate causal autoimmune variants to T cell networks. *Nature Genetics* (2025). doi:10.1038/s41588-025-02301-3

22. Precisely defining disease variant effects in CRISPR-edited single cells. *Nature* (2025). doi:10.1038/s41586-025-09313-3

23. Mapping causal non-coding variants in coronary artery disease. *Nature Cardiovascular Research* (2025). doi:10.1038/s44161-025-00715-0

24. Bridging the variant-to-function gap in type 2 diabetes: advances and challenges. *Diabetologia* (2025). doi:10.1007/s00125-025-06600-6

25. Choi, J. et al. Massively parallel reporter assays and variant scoring identified functional variants and target genes for melanoma loci. *American Journal of Human Genetics* 110(1), 141-152 (2023).

26. A review of post-GWAS studies in schizophrenia. *Translational Psychiatry* (2025). doi:10.1038/s41398-025-03656-1

27. OmniReg-GPT: a high-efficiency foundation model for comprehensive genomic sequence understanding. *Nature Communications* (2025). doi:10.1038/s41467-025-65066-7

28. EPInformer: scalable and integrative prediction of gene expression from promoter-enhancer sequences with multimodal epigenomic profiles. *Nature Communications* (2026). doi:10.1038/s41467-026-70535-8

29. Deep learning approaches for non-coding genetic variant effect prediction: current progress and future prospects. *Briefings in Bioinformatics* 25(5), bbae446 (2024).

30. Massively parallel reporter assay investigates shared genetic variants of eight psychiatric disorders. *Cell* (2024). doi:10.1016/j.cell.2024.12.001

31. Fine-mapping across diverse ancestries drives the discovery of putative causal variants underlying human complex traits and diseases. *medRxiv* (2023). doi:10.1101/2023.01.07.23284293

32. The NHGRI-EBI GWAS Catalog: standards for reusability, sustainability and diversity. *Nucleic Acids Research* (2025). doi:10.1093/nar/gkae1024

33. Benchmarking DNA foundation models for genomic and genetic tasks. *Nature Communications* (2025). doi:10.1038/s41467-025-65823-8

34. A Benchmark of Evo2 Genomic AI Models for Efficient and Practical Deployment. *bioRxiv* (2025). doi:10.1101/2025.09.10.675279

---

## Appendix A: Revised Gap Score

### Original Score: 8.4/10

### Revised Score: 7.8/10

**Rationale for adjustment:**

| Dimension | Round 1 | Round 2 | Change Reason |
|---|---|---|---|
| Novelty | 9 | 7 | AlphaGenome and Sniff partially address the gap |
| Impact | 9 | 9 | Unchanged -- the problem remains critically important |
| Computational Feasibility | 8 | 9 | All models now open-source with weights; compute verified sufficient |
| Timeline Feasibility | 8 | 8 | 5 months tight but achievable |
| Publication Potential | 8 | 7 | Competition from AlphaGenome and Sniff raises the bar |

**Net assessment:** The gap has narrowed but remains open in a well-defined, highly publishable form. The key insight is that **integration is the remaining challenge, not individual model performance**. AlphaGenome pushed the frontier of sequence-based prediction; SuSiE/PolyFun pushed fine-mapping; EMO pushed epigenomic context. Nobody has unified all three with multi-model ensembles and disease-specific conditioning. This integrated approach is differentiated from existing work and achievable with available resources.

### Combined Project Beta Score: 8.2/10

The combined project with transmed's VUS gap is stronger than either gap alone because:
1. Shared infrastructure reduces total work
2. Dual research + clinical narrative strengthens publication
3. Cross-validation between GWAS and clinical variant data
4. Broader scope justified by unified framework
5. Clinical relevance elevates impact argument

---

## Appendix B: Key Data Resources Summary

| Resource | URL/Access | Size | Key Content |
|---|---|---|---|
| AlphaGenome | huggingface.co/google/alphagenome-all-folds | ~GB | 5,930 track predictions per variant |
| Borzoi | github.com/calico/borzoi | ~GB | RNA-seq coverage predictions |
| Evo2 | github.com/ArcInstitute/evo2 | 14-80 GB | Conservation-like scores |
| GWAS Catalog | ebi.ac.uk/gwas | ~TB | 1M+ associations |
| Open Targets | platform.opentargets.org | ~GB | 133K fine-mapped loci |
| CAUSALdb2 | mulinlab.org/causaldb | ~GB | 15K GWAS fine-mapped |
| GTEx v8 | gtexportal.org | ~GB | 53 tissue eQTLs |
| OneK1K | onek1k.org | ~GB | 14 immune cell sc-eQTLs |
| ENCODE SCREEN | screen.encodeproject.org | ~MB | 2.35M human cCREs |
| MaveDB | mavedb.org | ~GB | 7M+ variant effects |
| TraitGym | HuggingFace | ~MB | Variant benchmark |
