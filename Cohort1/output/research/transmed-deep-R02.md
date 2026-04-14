---
agent: transmed
round: 2
date: 2026-04-14
type: deep-dive
---

# Deep Dive: Context-Dependent VUS Resolution

## Executive Summary

This deep dive investigates the gap in context-dependent variant effect prediction (VEP) for resolving Variants of Uncertain Significance (VUS). The gap remains substantial but the competitive landscape has shifted significantly since Round 1. Several new tools (DYNA, DIVA, IMPPROVE, popEVE, AlphaGenome, ML-Penetrance) address fragments of the problem, but **no single tool integrates tissue-specific expression, disease context, mechanism-of-action (GOF/LOF), and penetrance into a unified framework for coding VUS resolution**. The gap is narrower than initially assessed but still genuinely open, with a clear path to a high-impact publication.

---

## 1. Gap Verification

### 1.1 Has the Gap Been Filled?

**Short answer: No, but it has been partially addressed from multiple angles.**

Since our Round 1 assessment, several new methods have emerged that chip away at the context-dependence problem from different directions:

**DYNA (Disease-Specific Language Model, Nature Machine Intelligence, 2025)**
- Developed by Zhang Lab (Columbia/Mount Sinai)
- A disease-specific language model for variant pathogenicity in cardiac and regulatory genomics
- Integrates disease context through fine-tuning on disease-specific variant sets
- Limited to cardiac and regulatory genomics domains; not proteome-wide
- Does not explicitly model tissue-specific expression or penetrance

**DIVA (Disease-Specific Variant Pathogenicity, bioRxiv September 2025)**
- Integrates ESM protein language model + PubMedBERT for disease text
- Contrastive learning aligns variants with disease annotations
- Predicts specific disease types alongside deleteriousness
- Does NOT incorporate tissue-specific expression, penetrance, or mechanism-of-action
- Represents a step toward disease-context integration but remains limited

**IMPPROVE (Phenotype-Specific Models, Nature Communications 2025)**
- Constructs 1,866 Random Forest models for individual HPO (Human Phenotype Ontology) terms
- Integrates CADD scores with GTEx bulk and Tabula Sapiens single-cell expression data
- Key result: 90% of phenotypes have pathogenic variants better predicted by single-cell tissue models than CADD alone
- Limitation: Uses Random Forest (not deep learning), limited to HPO phenotype conditioning, does not model GOF/LOF or penetrance

**popEVE (Nature Genetics, December 2025)**
- Deep generative model combining evolutionary and population data
- Places variants on a continuous severity spectrum
- Does NOT incorporate tissue context, disease context, or mechanism-of-action
- Represents improved population-level scoring, not context-dependent prediction

**AlphaGenome (Nature, January 2026)**
- DeepMind's unified DNA sequence model for non-coding regulatory variants
- Predicts thousands of functional genomic tracks at single-base resolution
- Handles regulatory/non-coding variants with tissue-specific predictions
- Does NOT handle coding missense variants (complementary to AlphaMissense, not a replacement)
- Relevant for the Combined Project Beta (non-coding gap) but not directly for coding VUS

**ML-Penetrance (Science, August 2025)**
- Mount Sinai group; ML-based penetrance prediction using EHR data
- Models 10 autosomal dominant diseases across 1.35M participants
- Incorporates clinical phenotype data into penetrance estimation
- Addresses the penetrance dimension but not variant pathogenicity per se
- Uses EHR data that is not publicly available in raw form (but method is generalizable)

**V2P (Multi-Task Variant-to-Phenotype, 2025)**
- Multi-task, multi-output ML model predicting variant pathogenicity conditioned on 23 top-level HPO disease phenotypes
- Covers SNVs and indels genome-wide
- Steps toward phenotype-conditioning but coarse (23 phenotype categories)

### 1.2 What Remains Open

The critical gap is that **no existing tool jointly models all four context dimensions**:

| Context Dimension | AlphaMissense | DYNA | DIVA | IMPPROVE | popEVE | ML-Penetrance | V2P |
|---|---|---|---|---|---|---|---|
| Tissue-specific expression | No | No | No | Yes (GTEx) | No | No | No |
| Disease context | No | Partial (cardiac) | Yes (text) | Yes (HPO) | No | Yes (10 diseases) | Yes (23 HPO) |
| Mechanism (GOF/LOF) | No | No | No | No | No | No | No |
| Penetrance estimation | No | No | No | No | No | Yes | No |
| Proteome-wide scale | Yes | No | Yes | Yes | Yes | No (10 diseases) | Yes |

**The gap for a unified, proteome-wide, context-dependent VEP that integrates all four dimensions remains open.** This is the target.

### 1.3 Gap Confidence Assessment

- **Round 1 gap score**: 8.4/10
- **Revised gap score**: 7.8/10 (reduced slightly due to partial addressing by DYNA/DIVA/IMPPROVE)
- **Rationale for remaining high**: The partial solutions demonstrate both demand and feasibility, but none achieve the integrated architecture needed. The existence of multiple partial solutions actually strengthens the case that this is a recognized unmet need.

---

## 2. VUS Landscape Quantification

### 2.1 ClinVar Scale

As of early 2026, ClinVar contains **>3 million submitted variant interpretations** from >2,800 organizations worldwide (ClinVar NAR update, January 2025). Key statistics:

- **Total unique variants**: ~2.5M+ unique variants across all classification categories
- **VUS proportion**: Of ~330,000 missense variants from clinical testing, approximately **70% are VUS** (Findlay et al., 2021; ClinVar statistics)
- **Growth rate**: ClinVar passed 1 million variants in 2021; it has tripled in under 5 years
- **VUS growth outpacing reclassification**: The rate of new VUS submissions far exceeds reclassification capacity

### 2.2 VUS by Gene Class and Disease Area

**Hereditary Cancer Genes (highest clinical urgency)**:
- BRCA1: 80% of missense variants are VUS (n=2,395 VUS as of recent counts)
- BRCA2: 85% of missense variants are VUS (5,534 VUS out of 6,506 missense; ClinVar 2022)
- TP53: 64% of missense variants are VUS (n=589)
- Recent BRCA2 saturation study reclassified ~5,500 VUS to benign/likely benign and 785 to pathogenic, leaving only 608 VUS -- but this required massive experimental effort (Nature 2024)

**Cardiac Arrhythmia Genes (critical for clinical decision-making)**:
- KCNH2 (hERG, long QT syndrome): High VUS burden; functional assays combined with MAVE data enable reclassification (Circulation 2025)
- SCN5A (Brugada/long QT): VUS reclassification ongoing with functional studies
- RYR2 (catecholaminergic polymorphic VT): Extremely large protein (4,967 aa), dense VUS accumulation

**Cardiomyopathy Genes**:
- MYH7, MYBPC3, TNNT2: Significant VUS burden in sarcomeric genes
- AlphaMissense performance for sarcomeric genes shows gene-specific variability (Circulation: Genomic and Precision Medicine, 2024)

**Hereditary Disease Panels**:
- In multigene panel testing of 1,689,845 individuals, **41% had at least one VUS** (JAMA 2023)
- VUS rates highest in non-European populations due to underrepresentation in reference databases

### 2.3 Clinical Impact of Unresolved VUS

- Patients with VUS experience "diagnostic odyssey" -- prolonged uncertainty
- Clinicians cannot act on VUS: no risk management, no cascade testing
- Mean time to VUS reclassification: **30.7 months** to benign/likely benign, **22.4 months** to pathogenic/likely pathogenic
- Of reclassified VUS, **80.2%** are ultimately benign/likely benign -- suggesting massive over-reporting of uncertain variants
- Variant classification inequity: VUS rates significantly higher in non-European ancestry populations

### 2.4 Scale of the Computational Challenge

- **~231,000 missense VUS** in ClinVar (70% of 330K clinical missense variants)
- **~4 million possible human missense variants** (AlphaMissense proteome-wide predictions)
- Of these, AlphaMissense classifies 89% as likely benign or likely pathogenic, leaving **~440,000 ambiguous** variants
- The intersection of clinical VUS and computationally ambiguous variants represents the hardest cases

---

## 3. Context Data Availability

### 3.1 GTEx (Genotype-Tissue Expression Project)

**Current status: GTEx v8 (final release)**
- **54 tissue types** (including 11 brain regions and 2 cell lines)
- **838 donors**, **17,382 RNA-seq samples**
- **49 tissues** with at least 70 individuals having both RNA-seq and WGS
- Median gene expression per tissue: publicly downloadable
- eQTL data: tissue-specific eQTLs for all 49 tissues
- sQTL data: splicing quantitative trait loci across tissues

**Data usability for context-dependent VEP**:
- Gene expression vectors across 54 tissues can serve as tissue embeddings
- Tissue-specific eQTLs provide ground truth for tissue-dependent variant effects
- Limitation: bulk tissue data, not single-cell resolution
- Limitation: Only 838 donors, limited population diversity

### 3.2 Human Protein Atlas (HPA)

**Current status: HPA v25 (November 2025)**
- **27,883 antibodies** targeting **17,407 unique proteins**
- **>10 million manually annotated bio-images**
- **>6 billion assay measurements** from 300,000 biological samples
- **34 tissue types** with single-cell ATAC-seq data
- **154 cell types** represented
- Blood Atlas: 32 disease cohorts, 71 diseases
- Protein interaction networks for >15,000 proteins with 23,000 AlphaFold3-predicted PPI structures

**Data usability**: Protein-level tissue-specific expression; complementary to GTEx (RNA-level). The disease cohort data in Blood Atlas v25 is directly relevant to disease-context conditioning.

### 3.3 Single-Cell Expression Atlases

- **Tabula Sapiens**: Human cell atlas with single-cell RNA-seq across 24 organs, 483 cell types
- **Human Cell Atlas**: Growing atlas with multi-omics across hundreds of cell types
- **CellxGene (Chan Zuckerberg)**: 50M+ cells across 400+ datasets; standardized cell type annotations
- These provide cell-type-level resolution beyond bulk tissue, critical for precision in variant interpretation

### 3.4 Disease-Specific Expression Databases

- **TCGA**: 33 cancer types, ~11,000 tumors with multi-omics (RNA-seq, WES, methylation)
- **TARGET**: Pediatric cancer expression data
- **GEO/ArrayExpress**: Thousands of disease-specific expression datasets
- **Open Targets**: Disease-gene associations with tissue expression evidence
- **OMIM**: Mendelian disease gene annotations with phenotype descriptions

### 3.5 ClinVar Reclassification Data (Training Labels)

**Critical for supervised training:**
- **37,699 unique VUS reclassified** over time (as of recent analysis)
- 80.2% reclassified to benign/likely benign
- 19.8% reclassified to pathogenic/likely pathogenic
- These temporal reclassifications can serve as a **natural test set**: predict current VUS classifications, validate against future reclassifications
- ClinVar star system provides confidence levels: 0-4 stars per assertion

### 3.6 Population Biobank Data

- **UK Biobank**: 490,640 participants with WGS + rich phenotype data
- **All of Us**: ~250,000+ with exome/genome + EHR data
- **gnomAD v4.0**: 730,947 exomes for constraint metrics (LOEUF < 0.6 for LoF-intolerant genes)
- **BioBank Japan, FinnGen, Estonian Biobank**: Additional population data
- Biobank phenotype-genotype associations provide computational validation data for variant effects

### 3.7 MAVE/Functional Data

- **MaveDB**: >7 million variant effects from multiplexed functional assays
- **MaveMD**: 74 curated MAVE datasets, 438,318 variant effect measurements across 32 clinically relevant genes
- MAVE data enables reclassification of ~55% of VUS in well-studied genes
- Can serve as training data for gene-specific functional impact models

---

## 4. AlphaMissense Limitation Analysis

### 4.1 Systematic Failure Modes

**Context-free prediction**: AlphaMissense generates a single pathogenicity score per variant, regardless of tissue, disease, or clinical context. This is fundamentally limiting because:

1. **The same variant can be pathogenic in one tissue and benign in another** (e.g., a variant in a gene expressed only in cardiac tissue is irrelevant in liver disease)
2. **The same variant can cause different diseases** depending on mechanism (GOF vs LOF)
3. **Pathogenicity depends on penetrance**, which is not a sequence-level property

### 4.2 Gene-Specific Performance Variability

AlphaMissense shows dramatic performance differences across genes:

- **IRF6**: 83.3% false positive rate (15 of 18 benign variants misclassified as pathogenic) (Frontiers in Genetics, 2024)
- **CFTR**: High false positive rate despite good sensitivity for severe CF variants (Benchmarking AlphaMissense, PMC, 2023)
- **Sarcomeric genes (MYH7, MYBPC3)**: Variable performance, gene-dependent (Circulation: Genomic PM, 2024)
- **DDR genes in cancer**: Accuracy is gene-dependent (PMC, 2025)

The recommended threshold of 0.56 was calibrated on bulk ClinVar data, providing "no guarantee that it will work equally well across different genes and domains" (Frontiers in Genetics, 2024).

### 4.3 Gain-of-Function Blind Spot

Most VEPs including AlphaMissense are trained primarily on loss-of-function signals:

- **GOF mutations are underrepresented** in training data (conservation-based signals favor LOF detection)
- **PreMode** (Nature Communications, 2025) addresses this with SE(3)-equivariant graph neural networks for gene-specific GOF/LOF prediction, but is not integrated with pathogenicity scoring
- **LoGoFunc** predicts pathogenic GOF vs LOF vs neutral, outperforming pathogenicity-only tools for GOF identification
- GOF mutations are clinically critical: oncogene activation (RAS, BRAF, EGFR), channel disorders (SCN5A GOF = Brugada/long QT), receptor hyperactivation

### 4.4 Where VEPs Disagree with Functional Data

Analysis of MAVE data from 37 proteins vs 5 VEPs reveals systematic biases (bioRxiv, 2025):

- **VEPs overestimate pathogenicity at buried, hydrophobic residues** (structural conservation bias)
- **VEPs underestimate impact in disordered regions** (lack of structural context for IDPs)
- **VEPs underestimate impact on charged surface residues** (interaction interfaces, allosteric sites)
- **MAVEs capture context-specific mechanisms more accurately** than sequence-based VEPs

### 4.5 Quantitative Performance Benchmarks

On ProteinGym (2.7M missense variants, 217 DMS assays, 2,525 clinical proteins):
- AlphaMissense: Strong overall but gene-heterogeneous
- popEVE: Comparable proteome-wide performance with better calibration against population data
- VARITY_R: Top-performing clinical-trained predictor
- ESM1b: Strong zero-shot performance from protein language models
- **No single predictor dominates across all gene classes** -- this heterogeneity is the core problem

---

## 5. Architecture Design

### 5.1 Proposed Architecture: ContextVEP

A multi-modal transformer architecture that predicts variant pathogenicity conditioned on tissue, disease, mechanism, and clinical context.

### 5.2 Input Modalities

**Modality 1: Variant Representation (Protein-Level)**
- Amino acid sequence context (local window around variant)
- ESM-2 embeddings (pre-computed, 650M or 3B parameter model)
- AlphaFold2 structural features (pLDDT, contact map, secondary structure)
- Conservation features (MSA-derived, from AlphaMissense pipeline)
- Position-specific: surface accessibility, disorder probability, domain annotations

**Modality 2: Tissue Context**
- GTEx expression vector (54 tissues x gene expression level)
- Single-cell resolution: Tabula Sapiens cell-type expression profiles
- Tissue embedding: learned embedding from tissue expression patterns
- Isoform-specific expression: which isoform is dominant in the target tissue

**Modality 3: Disease Context**
- Disease text embedding (PubMedBERT or BioGPT encoding of disease description)
- HPO term hierarchy encoding (graph neural network over HPO DAG)
- Disease-gene association strength (Open Targets, OMIM)
- Known mechanism-of-action for the gene in the disease context

**Modality 4: Mechanism-of-Action**
- Gene constraint metrics (gnomAD v4 LOEUF, missense constraint)
- Known GOF/LOF classification for the gene (ClinGen gene-disease validity)
- Protein functional domain context (Pfam, InterPro annotations)
- PreMode-derived GOF/LOF probability

**Modality 5: Population and Clinical Context**
- gnomAD allele frequency (overall and per-population)
- UK Biobank/All of Us phenotype associations (if available)
- ClinVar submission history and star rating
- Family segregation evidence (if encoded in ClinVar submissions)

### 5.3 Architecture Design

```
Input: (variant, tissue, disease, mechanism_context)
    |
    v
[ESM-2 Encoder] --> variant_embedding (1280-dim)
[Structural Encoder] --> structure_embedding (256-dim)
[Tissue Encoder] --> tissue_embedding (128-dim)  
[Disease Encoder] --> disease_embedding (256-dim)
[Mechanism Encoder] --> mechanism_embedding (64-dim)
    |
    v
[Cross-Attention Fusion Module]
    - Variant attends to tissue context
    - Variant attends to disease context  
    - Disease attends to tissue (which tissues relevant for this disease?)
    - Mechanism modulates pathogenicity interpretation
    |
    v
[Multi-Task Prediction Heads]
    |-- Pathogenicity score (continuous, 0-1, ACMG-calibrated)
    |-- GOF/LOF/Neutral classification
    |-- Disease-specific pathogenicity (per-disease score)
    |-- Tissue-specific impact score (per-tissue vector)
    |-- Penetrance estimate (continuous, 0-1)
    |-- ACMG evidence strength (PP3 supporting/moderate/strong)
```

### 5.4 Training Strategy

**Phase 1: Pre-training on large-scale variant data**
- Train on ClinVar pathogenic/benign variants (conservative labels only, per RENOVO approach)
- Pre-train tissue encoder on GTEx expression prediction task
- Pre-train disease encoder on disease-gene association prediction

**Phase 2: Multi-task fine-tuning**
- Joint training on pathogenicity + GOF/LOF + disease-specific + tissue-specific tasks
- Use MAVE data (MaveDB 7M+ measurements) for functional impact supervision
- Use ClinVar reclassification data as temporal validation

**Phase 3: Calibration**
- Per-gene calibration using ACMG-validated variants from ClinGen Expert Panels
- Threshold optimization per disease area
- Calibrate ACMG evidence strength categories (PP3 supporting/moderate/strong/very strong)

### 5.5 Compute Requirements

- **ESM-2 3B inference**: ~30 GPU-hours for all human proteins on H200
- **Training the fusion model**: Estimated 200-500 GPU-hours on H200 (comparable to DIVA/DYNA training)
- **Hyperparameter search**: 100-200 GPU-hours
- **Full pipeline**: ~500-1000 GPU-hours total
- **Well within HPC budget** with H200 and B200 nodes available

---

## 6. Computational Validation Strategy

### 6.1 Primary Validation: ClinVar Temporal Holdout

**Design**: Use historical ClinVar snapshots to create a natural prospective test:
- Training set: All pathogenic/benign variants classified before a cutoff date (e.g., January 2024)
- Test set: VUS that were **reclassified after the cutoff** (37,699 reclassified VUS available)
- This mimics real-world deployment: predict today's VUS, validate against tomorrow's reclassifications

**Metric**: AUC-ROC, precision-recall, and calibration for reclassified variants
**Advantage**: No wet lab required; uses the natural reclassification process as ground truth

### 6.2 Secondary Validation: Biobank Phenotype Association

**Design**: For variants predicted as pathogenic in specific tissues/diseases:
- Check if carriers in UK Biobank (490,640 WGS) or All of Us show elevated disease risk
- Use the framework from Bhat et al. (AJHG, 2025): extract pathogenicity evidence from population biobank data
- Test whether context-dependent predictions better explain phenotype associations than context-free predictions

**Key metric**: Does adding tissue/disease context improve variant-phenotype association strength?

### 6.3 Tertiary Validation: MAVE Concordance

**Design**: Compare model predictions against MAVE functional data:
- MaveMD contains 438,318 variant effect measurements across 32 genes
- Test whether context-dependent predictions better match tissue-relevant functional assays
- Use gene-specific functional data as independent ground truth

### 6.4 GOF/LOF Validation

**Design**: Validate mechanism-of-action predictions against:
- Known GOF/LOF classifications from ClinGen gene-disease validity
- LoGoFunc benchmark set of GOF/LOF/neutral variants
- PreMode predictions as additional comparison
- Oncogene vs tumor suppressor classification from COSMIC

### 6.5 Cross-Population Validation

**Design**: Test whether context-dependent predictions reduce VUS disparity across populations:
- Compare VUS resolution rates in European vs non-European ancestry populations
- MAVE data has shown potential to reduce classification inequity (Genome Medicine, 2024)
- Test whether adding tissue/disease context preferentially helps underrepresented populations

### 6.6 Comparison Baselines

All validations compare against:
1. AlphaMissense (context-free, current SOTA for missense)
2. REVEL (ensemble, widely used clinically)
3. popEVE (population-informed)
4. DYNA (disease-specific, cardiac)
5. DIVA (disease-context via text)
6. IMPPROVE (phenotype-specific, GTEx-based)
7. CADD (aggregate annotation)
8. ClinPred (clinical-trained)

---

## 7. Competition Assessment

### 7.1 Google DeepMind

**AlphaMissense**: Published Science 2023. No evidence of AlphaMissense 2.0 or context-dependent extension as of April 2026. DeepMind appears to have pivoted to **AlphaGenome** for regulatory/non-coding variants rather than extending AlphaMissense for context-dependent coding variants.

**AlphaGenome**: Published Nature January 2026. Covers non-coding regulatory variants with tissue-level predictions. Does NOT address coding missense VUS. Available as API, not open-source model weights. Relevant for Combined Project Beta but not a direct competitor for coding VUS.

**Assessment**: DeepMind is **not pursuing context-dependent coding VUS resolution** based on public evidence. Their trajectory (AlphaFold -> AlphaMissense -> AlphaGenome) suggests moving toward regulatory genomics, leaving the context-dependent coding VUS space open.

### 7.2 Illumina

**PrimateAI-3D**: Published 2023, trained on 233 primate species. Primate-informed but not context-dependent.

**PromoterAI**: Published May 2025 in Science. Addresses non-coding regulatory (promoter) variants. Combined with PrimateAI-3D + SpliceAI, doubles diagnostic yield vs protein-truncating variants alone.

**Connected Multiomics Platform**: January 2026 launch. Cloud-based integration but uses existing PrimateAI/PromoterAI scores -- no new context-dependent coding VEP.

**Assessment**: Illumina's commercial strategy integrates existing tools rather than developing new context-dependent VEPs. They are a potential user/licensee of a context-dependent tool, not a competitor building one.

### 7.3 Broad Institute / ClinGen

**Variant-to-Function (V2F) initiative**: Symposium September 2025. Focused on MAVE data integration and ACMG criteria calibration.

**ClinGen Expert Panels**: Gene-by-gene curation approach (inherently slow, not scalable).

**New PP3/BP4 calibrations**: 2025 publication expanding ClinGen recommendations for computational evidence. Calibrated 3 new predictors alongside 4 existing ones. But these are calibrations of existing tools, not new context-dependent architectures.

**Assessment**: Broad/ClinGen focuses on curation infrastructure and calibration. They would be **adopters and validators** of a context-dependent VEP, not competitors building one.

### 7.4 Academic Groups

**Zhang Lab (DYNA)**: Published Nature Machine Intelligence 2025. Disease-specific for cardiac. May extend to other diseases, but currently narrow scope.

**DIVA group**: bioRxiv September 2025. Disease text integration via contrastive learning. Closer to our vision but missing tissue, mechanism, and penetrance dimensions.

**Mount Sinai (ML-Penetrance)**: Published Science August 2025. Penetrance focus with EHR data. Complementary to our approach, not competing directly.

**IMPPROVE group**: Nature Communications 2025. Phenotype-specific with GTEx data. Uses Random Forest, not deep learning. Could be extended but fundamentally simpler architecture.

**Marks Lab (popEVE, EVE)**: Strong evolutionary models but explicitly population-focused, not context-dependent.

### 7.5 Competitive Window Assessment

**Window of opportunity: 12-18 months** before convergence. Multiple groups are addressing individual context dimensions. The risk is that someone publishes a unified framework before us. However:

- No preprint or announced project combining all four dimensions exists as of April 2026
- The data integration challenge is substantial (not just a model architecture problem)
- The clinical validation framework we propose is novel
- First-mover advantage is significant in this space (cf. AlphaMissense defining the field)

---

## 8. Feasibility Reassessment

### 8.1 Data Feasibility: HIGH

All required data is publicly available:
- ClinVar: Public, updated monthly, API access
- GTEx v8: Public, downloadable bulk data
- HPA v25: Public, API access
- gnomAD v4: Public, downloadable
- MaveDB/MaveMD: Public, standardized formats
- UK Biobank: Requires application (~3 month approval) but 490K WGS available
- ProteinGym: Public benchmark suite
- ESM-2 embeddings: Pre-computable from open-source model
- AlphaFold structures: Public database

### 8.2 Compute Feasibility: HIGH

- Total estimated compute: 500-1000 GPU-hours on H200
- Available: H200 (8 GPUs/node, 80GB each), B200, RTX 5000 Ada
- ESM-2 inference: Well-documented, PyTorch-native
- Training: Standard transformer training, well within single-node multi-GPU capacity
- Hyperparameter search: Embarrassingly parallel across GPU nodes

### 8.3 Timeline Feasibility: MODERATE-HIGH

| Phase | Duration | Description |
|---|---|---|
| Data preparation | 3-4 weeks | Download, preprocess ClinVar/GTEx/gnomAD/MAVE data |
| Feature engineering | 2-3 weeks | Compute ESM-2 embeddings, structural features, tissue vectors |
| Model development | 4-6 weeks | Architecture implementation, training, ablation studies |
| Validation | 3-4 weeks | Temporal holdout, biobank, MAVE concordance, cross-population |
| Analysis & writing | 3-4 weeks | Figures, comparisons, manuscript preparation |
| **Total** | **15-21 weeks** | **Feasible within summer 2026** |

### 8.4 Risk Assessment

| Risk | Probability | Mitigation |
|---|---|---|
| Context data doesn't help beyond AlphaMissense | Low (IMPPROVE shows 90% improvement) | Ablation study design already planned |
| Competitor publishes unified framework | Medium | Move fast; our validation framework is unique |
| UK Biobank access delayed | Medium | Can validate with gnomAD + ClinVar without UK Biobank initially |
| GOF/LOF prediction is too noisy | Medium | Can release without GOF/LOF head as v1, add in v2 |
| Model doesn't calibrate well for ACMG evidence | Low | ClinGen calibration methodology is well-established |

---

## 9. Publication Framing

### 9.1 Target Venue

**Primary**: Nature Computational Science
**Secondary**: Nature Methods, Nature Genetics
**Tertiary**: Genome Research, American Journal of Human Genetics

### 9.2 Proposed Title

"Context-dependent variant effect prediction resolves variants of uncertain significance across tissues and diseases"

Alternative: "ContextVEP: integrating tissue, disease, and mechanism context for clinical variant interpretation"

### 9.3 Central Claim

Current variant effect predictors assign a single pathogenicity score per variant, ignoring the biological reality that variant effects depend on tissue, disease, mechanism, and clinical context. We present ContextVEP, a multi-modal framework that conditions variant pathogenicity prediction on tissue-specific expression, disease context, mechanism-of-action, and penetrance. ContextVEP reclassifies [X%] of ClinVar VUS with [Y] precision, significantly outperforming context-free predictors, and reduces VUS classification disparity across ancestral populations.

### 9.4 Key Figures (Planned)

**Figure 1**: The VUS problem -- ClinVar growth, VUS proportion, tissue/disease dependence examples

**Figure 2**: ContextVEP architecture -- multi-modal inputs, cross-attention fusion, multi-task outputs

**Figure 3**: Temporal validation -- performance on ClinVar reclassified VUS vs AlphaMissense, REVEL, popEVE, DIVA

**Figure 4**: Context matters -- case studies where tissue/disease context changes prediction (cardiac vs oncology vs neurological variants in the same gene)

**Figure 5**: Mechanism-of-action -- GOF vs LOF prediction accuracy, examples of GOF mutations in oncogenes vs LOF in tumor suppressors

**Figure 6**: Clinical impact -- ACMG evidence calibration, VUS resolution rates by gene class, cross-population equity analysis

**Extended Data**: Ablation studies (which context dimensions help most), per-gene performance, biobank phenotype validation, comparison to all baselines

### 9.5 What Reviewers Will Attack

1. **"Tissue expression is a noisy proxy for tissue-specific pathogenicity"**
   - Mitigation: Show ablation with single-cell (Tabula Sapiens) vs bulk (GTEx) data
   - IMPPROVE already demonstrates this works (Nature Communications 2025)

2. **"Disease context encoding is subjective"**
   - Mitigation: Use standardized HPO ontology + PubMedBERT encoding
   - Compare multiple disease encoding strategies

3. **"How does this change clinical practice?"**
   - Mitigation: Frame in ACMG evidence categories; show calibrated PP3 evidence strength
   - Demonstrate VUS resolution rates comparable to MAVE-based reclassification

4. **"Validation without wet lab is insufficient"**
   - Mitigation: Three independent validation strategies (temporal holdout, biobank phenotype, MAVE concordance)
   - Cross-population validation addresses equity dimension

5. **"AlphaMissense is already good enough"**
   - Mitigation: Quantify gene classes where AlphaMissense fails (IRF6 83% FPR)
   - Show that context-dependent predictions rescue these failure cases

### 9.6 Why Nature Computational Science

- **Paradigm shift**: From "one score per variant" to "context-dependent interpretation"
- **Broad impact**: Millions of VUS affect clinical decision-making worldwide
- **Multi-modal innovation**: Novel cross-attention fusion of protein, tissue, disease, mechanism data
- **Clinical relevance**: Directly addresses precision medicine needs
- **Equity dimension**: Reduces VUS disparity across populations
- **Computational rigor**: Multiple independent validation strategies

---

## 10. Combined Project Beta Design

### 10.1 Motivation for Combining with Non-Coding Variant Gap

The reggeno agent identified a parallel gap in non-coding variant effect prediction:
- GWAS loci are >90% non-coding
- Current tools (Enformer, Sei, AlphaGenome) predict regulatory effects but not clinical pathogenicity
- Tissue-specific regulatory effects are the fundamental challenge

**The shared challenge**: Both coding VUS and non-coding GWAS variants require tissue-specific, disease-aware interpretation. The data sources (GTEx, HPA, biobank phenotypes) and the conceptual framework (context-dependent prediction) are identical.

### 10.2 Unified Framework: ContextVEP-Unified

**Architecture for combined coding + non-coding prediction:**

```
[Coding Variant Input]                [Non-Coding Variant Input]
   |                                       |
[ESM-2 Protein Encoder]          [AlphaGenome/Enformer DNA Encoder]
   |                                       |
   v                                       v
variant_embedding (protein)      variant_embedding (regulatory)
   \                                      /
    \                                    /
     [Shared Context Module]
     |  Tissue Encoder (GTEx/HPA/scRNA)
     |  Disease Encoder (HPO/PubMedBERT)
     |  Gene-Regulatory Link (eQTL/enhancer-gene maps)
     |
     v
     [Cross-Attention Fusion]
     |
     [Task-Specific Heads]
     |-- Coding pathogenicity
     |-- Non-coding regulatory impact
     |-- Tissue-specific effect scores
     |-- Disease-specific pathogenicity
     |-- Gene expression change prediction
     |-- Penetrance estimation
```

### 10.3 Key Innovation of Unified Approach

**The gene as the integration point**: Both coding and non-coding variants affect gene function. Coding variants alter protein sequence; non-coding variants alter gene regulation. By linking through the gene:

1. Non-coding variant in an enhancer of BRCA1 -> predicted to reduce expression in breast tissue -> predicted pathogenic for breast cancer
2. Coding missense in BRCA1 -> predicted to disrupt DNA repair function -> predicted pathogenic for breast cancer
3. **Both share tissue-disease context** and can be jointly evaluated

This is what Volaria (bioRxiv, January 2026) begins to address with "gene-centered representations of coding and regulatory genetic variation," but Volaria focuses on disease outcome prediction rather than variant interpretation per se.

### 10.4 Training Data for Unified Framework

**Coding arm**: ClinVar pathogenic/benign + MAVE data + gnomAD constraint
**Non-coding arm**: GWAS fine-mapped variants + eQTL + regulatory annotations (ENCODE)
**Shared**: GTEx expression, disease phenotypes, biobank phenotype associations
**Bridge data**: eQTL that connect non-coding variants to gene expression to protein function

### 10.5 Advantages of the Combined Approach

1. **Shared tissue/disease encoders** -- more training data, better representations
2. **Transfer learning** -- tissue-specific patterns learned from non-coding data help coding predictions
3. **Clinical utility** -- clinicians need to interpret both coding and non-coding variants in a single patient
4. **Whole-genome variant interpretation** -- steps toward comprehensive genome interpretation
5. **Publication scope** -- significantly broader impact and novelty than either gap alone

### 10.6 Risks of the Combined Approach

1. **Scope creep** -- combining two projects may be too ambitious for summer 2026
2. **Architectural complexity** -- the unified model is harder to train and debug
3. **Evaluation complexity** -- need separate benchmarks for coding and non-coding

### 10.7 Recommended Strategy

**Option A (Conservative)**: Build ContextVEP for coding VUS only. This is a complete, publishable project on its own. Leave the unified framework as "future work" in the paper.

**Option B (Ambitious)**: Build ContextVEP-Unified with both coding and non-coding arms. Higher risk, higher reward. Requires tight coordination with reggeno agent's expertise.

**Recommendation**: Start with **Option A** (coding VUS), design the architecture to be extensible to non-coding variants, and add the non-coding arm if timeline permits. The coding VUS problem alone is sufficient for a Nature Computational Science paper. The unified framework elevates it to a potential Nature main journal paper.

### 10.8 Combined Project Feasibility

| Component | Timeline | Compute |
|---|---|---|
| Coding VEP (core) | 15-21 weeks | 500-1000 GPU-hours |
| Non-coding arm addition | +4-6 weeks | +300-500 GPU-hours |
| Unified validation | +2-3 weeks | +100-200 GPU-hours |
| **Total combined** | **21-30 weeks** | **900-1700 GPU-hours** |

The combined project pushes against but does not exceed the summer 2026 timeline, assuming prompt project start and efficient execution.

---

## References

1. Cheng, J., et al. (2023). Accurate proteome-wide missense variant effect prediction with AlphaMissense. *Science*, 381(6664), eadg7492.

2. Gao, H., et al. (2025). Proteome-wide model for human disease genetics (popEVE). *Nature Genetics*.

3. Frazer, J., et al. (2021). Disease variant prediction with deep generative models of evolutionary data (EVE). *Nature*, 599, 91-95.

4. Brandes, N., et al. (2023). Genome-wide prediction of disease variant effects with a deep protein language model (ESM1b). *Nature Genetics*, 55, 1512-1522.

5. AlphaGenome Consortium / Google DeepMind (2026). Advancing regulatory variant effect prediction with AlphaGenome. *Nature*.

6. Guo, M.H., et al. (2025). A disease-specific language model for variant pathogenicity in cardiac and regulatory genomics (DYNA). *Nature Machine Intelligence*.

7. Disease-specific variant pathogenicity prediction using multimodal biomedical language models (DIVA). *bioRxiv*, September 2025.

8. IMPPROVE: Expanding the utility of variant effect predictions with phenotype-specific models. *Nature Communications*, 2025.

9. Bhat, P., Yu, H., Brown, A., Pejaver, V., Lebo, M., Harrison, S., & Cassa, C. (2025). Extracting and calibrating evidence of variant pathogenicity from population biobank data. *American Journal of Human Genetics*.

10. Machine learning-based penetrance of genetic variants. *Science*, August 2025. DOI: 10.1126/science.adm7066.

11. Findlay, G.M., et al. (2021). Closing the gap: Systematic integration of multiplexed functional data resolves variants of uncertain significance in BRCA1, TP53, and PTEN. *AJHG*.

12. Functional evaluation and clinical classification of BRCA2 variants. *Nature*, 2024.

13. GTEx Consortium (2020). The GTEx Consortium atlas of genetic regulatory effects across human tissues. *Science*, 369(6509), 1318-1330.

14. Human Protein Atlas v25 (2025). Release notes, November 2025. https://www.proteinatlas.org

15. PreMode predicts mode-of-action of missense variants by deep graph representation learning. *Nature Communications*, 2025.

16. Genome-wide prediction of pathogenic gain- and loss-of-function variants (LoGoFunc). *Genome Medicine*, 2023.

17. ProteinGym: Large-Scale Benchmarks for Protein Design and Fitness Prediction. *NeurIPS*, 2023.

18. Calibration of additional computational tools expands ClinGen recommendation options for variant classification with PP3/BP4 criteria. *AJHG*, 2025.

19. ClinVar: updates to support classifications of both germline and somatic variants. *Nucleic Acids Research*, 53(D1), D1313, 2025.

20. gnomAD v4.0 Gene Constraint. Broad Institute, March 2024.

21. Multiplexed assays of variant effect for clinical variant interpretation. *Nature Reviews Genetics*, 2025.

22. MaveMD: A functional data resource for genomic medicine. *medRxiv*, November 2025.

23. Using multiplexed functional data to reduce variant classification inequities in underrepresented populations. *Genome Medicine*, 2024.

24. Rates and Classification of Variants of Uncertain Significance in Hereditary Disease Genetic Testing. *JAMA*, 2023.

25. Single-cell data combined with phenotypes improves variant interpretation (IMPPROVE details). *BMC Genomics*, May 2025.

26. Variant effect predictor correlation with functional assays is reflective of clinical classification performance. *Genome Biology*, 2025.

27. Exploring penetrance of clinically relevant variants in over 800,000 humans from gnomAD. *Nature Communications*, 2025.

28. Volaria: Gene-centered representation of coding and regulatory variation enables outcome prediction. *bioRxiv*, January 2026.

29. Illumina PromoterAI (2025). Illumina press release, May 2025.

30. V2P: Multi-task, multi-output variant-to-phenotype prediction. (2025).

31. Why variant effect predictors and multiplexed assays agree and disagree. *bioRxiv*, 2025.

32. A scalable approach to resolving variants of uncertain significance. *bioRxiv*, February 2026.

33. Comprehensive evaluation of AlphaMissense predictions by evidence quantification for variants of uncertain significance. *Frontiers in Genetics*, 2024.

34. Understanding the heterogeneous performance of variant effect predictors across human protein-coding genes. *Scientific Reports*, 2024.

35. Mapping the regulatory effects of common and rare non-coding variants across cellular and developmental contexts in the brain and heart. *bioRxiv*, February 2025.

36. From Uncertain to Actionable: Significant Reduction in Variants of Uncertain Significance via Multi-Institutional Real-World Evidence. *medRxiv*, August 2025.

37. Combining MAVEs and computational predictors improves variant classification. *medRxiv*, December 2025.

38. Disease-Specific Prediction of Missense Variant Pathogenicity with DNA Language Models and Graph Neural Networks. *Bioengineering*, 2025.

39. Language models reveal evidence gaps in variants of uncertain significance. *medRxiv*, February 2026.

40. Whole-genome sequencing of 490,640 UK Biobank participants. *Nature*, 2025.
