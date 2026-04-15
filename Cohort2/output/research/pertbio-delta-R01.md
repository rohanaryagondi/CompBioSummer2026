---
agent: Perturbation Biology & Single-Cell Benchmarking Expert (pertbio)
round: 1
date: 2026-04-14
type: research-note
topic: Delta -- PerturbMark design, Tahoe-100M analysis, method catalog
---

# Research Note: PerturbMark -- A Cross-Context Perturbation Prediction Benchmark Built on Tahoe-100M

## Agent

Dr. Perturbation Biology & Single-Cell Benchmarking Expert (pertbio), Cohort 2 Deep Divers. 15+ years in computational genomics, single-cell biology, and benchmark design. Specialization in evaluation frameworks that reveal truth rather than confirm expectations.

## Summary

This research note provides the deep technical foundation for Project Delta (PerturbMark), the highest-scored gap from Cohort 1 (consensus 8.64). The perturbation prediction field is experiencing a genuine methodological crisis: between March 2025 and April 2026, an unprecedented cascade of contradictory evidence has left the field unable to answer a basic question -- do deep learning methods actually outperform simple linear baselines for predicting cellular responses to perturbations?

Through extensive internet research conducted on April 14, 2026, I have audited the Tahoe-100M dataset in technical detail, cataloged 18+ perturbation prediction methods with their April 2026 status, dissected the metric controversy with specific failure mode characterizations, and designed a four-tier cross-context benchmark framework that differentiates PerturbMark from the existing scPerturBench (Nature Methods 2026).

**Key conclusion:** PerturbMark remains strongly differentiated from scPerturBench and all existing benchmarks. The combination of (a) Tahoe-100M's 50-cell-line chemical perturbation data for Tier 3 cross-context evaluation, (b) a calibrated metric suite addressing the known failure modes of MSE, Pearson-delta, Wasserstein, and Energy distance, (c) mandatory inclusion of all major linear baselines (mean, additive, CRISPR-informed mean, matrix factorization), and (d) systematic inclusion of 2026 models (X-Cell, AlphaCell, AetherCell, SCALE, Scouter, Stack, pertTF) is unprecedented. This benchmark can be executed in 1,000--2,000 GPU-hours and would constitute a definitive contribution to the most active methodological controversy in computational biology.

---

## Research Questions

1. What is the exact technical specification of Tahoe-100M, and how should cross-context splits be constructed from its 50 cell lines and 379 compounds?
2. What is the complete catalog of perturbation prediction methods as of April 2026, including their architectures, availability, and claimed performance?
3. Which evaluation metrics have known failure modes, and what constitutes a minimal well-calibrated metric suite?
4. How should a Tier 0--3 difficulty hierarchy be precisely defined and operationalized?
5. What specific gaps does PerturbMark fill that scPerturBench (Nature Methods 2026) does not?

---

## Methods and Sources

Research conducted via systematic web search and document retrieval on April 14, 2026. Sources include:

- HuggingFace dataset documentation for Tahoe-100M (tahoebio/Tahoe-100M)
- bioRxiv preprints: Tahoe-100M (Zhang et al., Feb 2025), AlphaCell (March 2026), AetherCell (March 2026), X-Cell (March 2026), pertTF (March 2026), SCALE (March 2026), Stack (Jan 2026), Cole et al. (Feb 2026), Dibaeinia et al. (Feb 2026), Well-Calibrated Metrics (Miller et al., Oct 2025), Diversity by Design (Camillo et al., Jun 2025), Tahoe-x1 (Oct 2025), rBio (Aug 2025), State (Jun 2025)
- Published papers: scPerturBench (Wei et al., Nature Methods 2026), Ahlmann-Eltze et al. (Nature Methods 2025), Systema/Vinas Torne et al. (Nature Biotechnology 2025), Wong et al. (Bioinformatics 2025), Scouter (Zhu & Li, Nature Computational Science 2026), GEARS (Roohani et al., Nature Biotechnology 2023), CPA (Lotfollahi et al., Molecular Systems Biology 2023), PerturbNet (Molecular Systems Biology 2025)
- Arc Institute Virtual Cell Challenge 2025 wrap-up report
- scPerturb resource (Peidli et al., Nature Methods 2024)
- OP3 benchmark (NeurIPS 2024 Datasets and Benchmarks Track)
- GitHub repositories: snap-stanford/GEARS, theislab/cpa, bm2-lab/scPerturBench, Xaira-Therapeutics/X-Cell, czi-ai/rbio, tahoebio/tahoe-x1

---

## Findings

### Finding 1: Tahoe-100M Deep Technical Audit

#### 1.1 Dataset Specifications

Tahoe-100M is the largest publicly available single-cell perturbation dataset, released February 25, 2025 under a CC0-1.0 license (Zhang et al., bioRxiv 2025).

| Attribute | Value |
|-----------|-------|
| Total cells | 100.6 million transcriptomic profiles |
| Total rows (all tables) | 4,286,159,337 |
| Expression data rows | 95.6 million |
| File size | 429 GB (Parquet format on HuggingFace) |
| Cell lines | 50 cancer cell lines (47 with sufficient representation) |
| Compounds | 379 distinct drugs (1,100 drug-dose combinations originally reported) |
| Unique drug-cell line conditions | 17,813 |
| License | CC0-1.0 (Public Domain) |
| Platform | Mosaic high-throughput (Vevo Therapeutics) + Parse Bioscience GigaLab |
| Genome build | Ensembl release 109, GRCh38 |
| Gene metadata | 62,700 entries |

#### 1.2 Data Schema

The expression data table uses a sparse tokenized format:

| Field | Type | Description |
|-------|------|-------------|
| `genes` | `sequence<int64>` | Gene token IDs (non-zero expression only); first entry is CLS marker token (ignore) |
| `expressions` | `sequence<float32>` | Raw count values; first entry is CLS token (ignore) |
| `drug` | `string` | Treatment name; `DMSO_TF` for vehicle controls |
| `sample` | `string` | Unique sample identifier |
| `BARCODE_SUB_LIB_ID` | `string` | Unique cell identifier (19 characters) |
| `cell_line_id` | `stringclasses(50)` | Cellosaurus ID |
| `moa-fine` | `stringclasses(15)` | Fine-grained mechanism of action |
| `canonical_smiles` | `string` | SMILES molecular structure |
| `pubchem_cid` | `string` | PubChem Compound ID |
| `plate` | `string` | 96-well plate identifier (1-14) |

**Critical preprocessing notes:**
- Raw counts are provided (no log-transformation or normalization applied)
- Sparse representation: only non-zero expression values included
- DMSO controls are plate-matched: use `DMSO_TF` + `plate` for proper control matching
- Gene mapping requires the `gene_metadata` table to convert token_ids to symbols/Ensembl IDs

#### 1.3 Metadata Architecture

Four metadata tables support the expression data:

1. **Gene Metadata** (62,700 rows): gene_symbol (HGNC), ensembl_id, token_id
2. **Sample Metadata** (1,340 rows): mean_gene_count, mean_tscp_count, mean_mread_count, mean_pcnt_mito, drugname_drugconc (dose information)
3. **Drug Metadata** (379 rows): targets (gene symbols), moa-broad ("inhibitor/antagonist", "activator/agonist", "unclear"), moa-fine (25 curated MOA categories), human-approved status, clinical-trials status
4. **Cell Line Metadata** (50 rows): cell_name, DepMap ID, Cellosaurus ID, Organ (13 distinct organs), Driver mutation fields with zygosity, type, and functional mechanism
5. **Obs Metadata** (101M rows): detailed cell-level metadata indexed by BARCODE_SUB_LIB_ID

#### 1.4 Cell Line Composition

The 50 cell lines span 13 organ types, with majority representation from lung, bowel, pancreas, and skin. Cell line identifiers use Cellosaurus format (e.g., CVCL_0480, CVCL_0546). Key characteristics:

- 47 of 50 cell lines had sufficient representation across conditions for analysis
- TP53, KRAS, and CDKN2A are altered in approximately half of the cell lines
- Driver mutations are annotated with zygosity, type, and functional mechanism
- DepMap IDs enable cross-referencing with CRISPR essentiality data

#### 1.5 Drug and Dose Information

- 379 distinct compounds with annotated targets and mechanisms of action
- 180 compounds classified into 25 MOA categories
- Median 5 unique drugs per MOA (range: 3--27)
- 69% of compounds are approved agents
- 325 target genes, with 120 targeted by more than one drug
- Dose information encoded in sample_metadata as `drugname_drugconc` (e.g., "8-Hydroxyquinoline" at 0.05 micromolar)
- 17,813 unique cell-line-drug conditions (31-fold increase over prior benchmarks)

#### 1.6 Quality Control and Batch Effects

- The Mosaic platform uses a **cell village approach** where all 50 cell lines are co-cultured in each pool, theoretically eliminating cell-line-level batch effects within a plate
- QC metrics available per sample: mean gene count, mean UMI transcript count, mean read count, mean mitochondrial percentage
- **No ambient RNA correction** is applied in the released data; users must apply their own
- **No normalization** is applied; raw counts are provided
- The Theislab/Vevo analysis pipeline (theislab/vevo_Tahoe_100m_analysis) uses RAPIDS-accelerated scanpy for GPU/CPU PCA and UMAP at this scale

#### 1.7 What Has Tahoe-100M Been Used For?

As of April 2026, documented uses include:

1. **Tahoe-x1** (Gandhi et al., bioRxiv Oct 2025): 3B-parameter foundation model pretrained on Tahoe-100M, achieving SOTA on gene essentiality, cancer hallmarks, cell-type classification, and perturbation response prediction
2. **SCALE** (bioRxiv March 2026): BioNeMo-based foundation model achieving 12.02% improvement in PDCorr and 10.66% in DE Overlap over State on Tahoe-100M benchmark
3. **Cole et al.** (bioRxiv Feb 2026): Used Tahoe-100M as one of the evaluation datasets for foundation model perturbation prediction
4. **AetherCell** (bioRxiv March 2026): Trained on multiple datasets including Tahoe-100M for chemical perturbation prediction
5. **A knowledge-driven framework** (bioRxiv Feb 2026): Reported 13.3% improvement in top-50 DE Pearson delta correlation on Tahoe-100M

**Critical observation:** Despite being the largest chemical perturbation dataset by 50x, Tahoe-100M has NOT been used for a systematic cross-context benchmark comparing DL vs linear baselines. All existing uses are model-centric (training and evaluating specific models) rather than benchmark-centric (systematic comparison of all major methods under standardized conditions). This is the core opportunity for PerturbMark.

#### 1.8 Compute Requirements for Loading and Preprocessing

- Full download: 429 GB
- Streaming mode supported via HuggingFace datasets library (avoids full download)
- Conversion to AnnData (h5ad) format available via Arc Institute alternative hosting
- GPU-accelerated preprocessing via RAPIDS/scanpy recommended for PCA/UMAP at this scale
- Estimated preprocessing compute: 50--100 CPU-hours for full QC + normalization pipeline
- Pseudobulk aggregation table (4.09B rows) available pre-computed

---

### Finding 2: Complete Method Catalog (April 2026 State)

#### 2.1 Deep Learning Methods -- Task-Specific

| Method | Architecture | Training Data | Code Available | Key Claim | Known Limitation |
|--------|-------------|---------------|----------------|-----------|-----------------|
| **GEARS** | Graph-enhanced gene activation/repression simulator; GNN on gene-gene knowledge graph | Norman, Replogle | Yes (GitHub: snap-stanford/GEARS) | Predicts single + double perturbation outcomes | Cannot predict for genes not in knowledge graph; requires combinatorial training data for combo predictions; surpassed by CRISPR-informed mean by 4.7--213.9x (Wong et al., 2025) |
| **CPA** | Compositional perturbation autoencoder; disentangled VAE with perturbation/dose/covariate embeddings | Multiple (modular) | Yes (GitHub: theislab/cpa) | OOD drug combination prediction, dose-response curves | Performance degrades on unseen cell types; limited cross-context generalization |
| **Scouter** | LLM embeddings + lightweight compressor-generator neural network | Norman, Replogle | Yes (Python package) | Reduces errors from GEARS/biolord by half or more | Published NatCompSci 2026; uses LLM text embeddings for gene representations; genetic perturbations only |
| **PerturbNet** | VAE (ZINB likelihood) + conditional invertible neural network (normalizing flow) | Multiple | Yes (GitHub) | Distributional predictions; handles chemical + genetic; attributes to molecular features | Published MolSysBio 2025; less tested at scale |
| **AttentionPert** | Multi-scale attention for multiplexed perturbations | Norman | Yes (GitHub) | Better handling of multi-gene perturbations | Limited to genetic perturbations |

#### 2.2 Deep Learning Methods -- Foundation Models

| Method | Architecture | Parameters | Training Data | Code/Weights | Key Claim | Limitation |
|--------|-------------|-----------|---------------|-------------|-----------|------------|
| **scGPT** | Generative pre-trained transformer for single-cell | ~86M | 33M cells | Yes (GitHub, readthedocs) | Multi-task single-cell FM; fine-tunable for perturbation | Failed vs linear baselines in Ahlmann-Eltze et al. (2025); learns systematic variation r=0.91 (Systema, 2025) |
| **Tahoe-x1** | Masked-expression generative objective with drug token | 3B | Tahoe-100M + others | Yes (HuggingFace: tahoebio/Tahoe-x1; GitHub) | 3--30x compute efficiency; SOTA on 4 cancer-relevant benchmarks | Trained on Tahoe-100M itself -- circular evaluation risk if benchmarking on Tahoe-100M |
| **X-Cell** | Diffusion language model; cross-attention to multi-modal priors (NLP, protein LM, interaction networks, morphology) | Up to 4.9B (X-Cell-Ultra) | X-Atlas/Pisces (25.6M cells, 16 contexts CRISPRi) | Partial (GitHub: Xaira-Therapeutics/X-Cell; X-Atlas subset on HF) | 5x higher Pearson delta than next-best; zero-shot T-cell generalization; power-law scaling | Genetic perturbations only (CRISPRi); X-Atlas not fully public; relies on Xaira proprietary data |
| **AlphaCell** | Latent Manifold Rectification + Biological Reality Reconstruction + Universal State Transition (Optimal Transport CFM) | Not disclosed | Multiple datasets | Preprint only (bioRxiv March 2026) | Zero-shot cross-context prediction; compositional generalization | Preprint; code availability unclear; may use proprietary data |
| **AetherCell** | Generative engine; VAE-based | Not disclosed | Multiple including Tahoe-100M | Preprint only (bioRxiv March 2026) | DEG PCC 0.82--0.83 on unseen cells/compounds; organoid translation | Preprint; drug discovery-focused (teriflunomide, dabigatran validation); code unclear |
| **Stack** | Tabular attention; in-context learning from unlabeled cells | Not disclosed | 149M human cells | Preprint (bioRxiv Jan 2026) | Zero-shot in-context learning; Perturb-Sapiens atlas (28 tissues, 40 cell classes, 201 perturbations) | Arc Institute; availability unclear for external benchmarking |
| **State** | State transition model + cell embedding model | Not disclosed | 100M+ perturbed cells (70 contexts) + 167M observational cells | Yes (GitHub: ArcInstitute/state) | 50%+ discrimination improvement; zero-shot cross-context identification | Arc Institute; evaluation on their own data; not independently validated |
| **SCALE** | Set-aware flow architecture; LLaMA-based cellular encoding + endpoint OT supervision; BioNeMo framework | Not disclosed | Tahoe-100M | Preprint (bioRxiv March 2026) | 12.02% PDCorr improvement, 10.66% DE Overlap over State; 12.51x training speedup | NVIDIA-affiliated; Tahoe-100M-specific evaluation |
| **pertTF** | Transformer; trained on pancreatic development knockouts | Not disclosed | 30 gene KOs x 14 cell types (pancreas) | Preprint (bioRxiv March 2026) | Cross-system transfer learning; captures cell identity shifts | Narrow training domain (pancreatic beta-cell differentiation); genetic only |
| **rBio** | Reasoning LLM post-trained with RL; uses TranscriptFormer as soft verifier | Not disclosed | LLM + virtual cell simulations | Yes (GitHub: czi-ai/rbio; HuggingFace) | Outperforms SUMMER on PerturbQA benchmark | CZI; reasoning model, not direct expression prediction; PerturbQA is text-based |

#### 2.3 Linear and Simple Baselines

| Baseline | Specification | Reference |
|----------|--------------|-----------|
| **No-change model** | Predicts control expression y_ctrl for all perturbations (i.e., "nothing happens") | Ahlmann-Eltze et al. (NatMeth 2025) |
| **Mean baseline** | Predicts mean of expression values in the training data across all perturbations | Ahlmann-Eltze et al. (NatMeth 2025) |
| **Additive model** | For double perturbation of genes A and B: y_pred = y_A + y_B - y_ctrl, where y_A, y_B are mean observed expression for single perturbations | Ahlmann-Eltze et al. (NatMeth 2025) |
| **Linear model (matrix factorization)** | argmin_W ||Y_train - (GWP^T + b)||^2, where G = gene embeddings (K-dim), P = perturbation embeddings (L-dim), W = K x L matrix, b = row means; solved via ridge regression (lambda=0.1) | Ahlmann-Eltze et al. (NatMeth 2025) |
| **CRISPR-informed mean** | Mean expression of cells with CRISPR perturbation of the target gene's pathway members; incorporates biological prior knowledge | Wong et al. (Bioinformatics 2025): surpasses GEARS by 4.7--213.9x, scGPT by 3.9--155.4x |
| **TransPert** | Statistical framework: gene-level perturbation summaries from reference cell lines + similarity-aware aggregation + global linear scaling | Virtual Cell Challenge 2025 3rd place (Team Outlier) |

**Critical observation for PerturbMark:** Every benchmark MUST include at minimum: no-change, mean, additive (for combinations), linear matrix factorization, and CRISPR-informed mean. Any DL method that cannot beat all five should not be claimed as "state of the art."

#### 2.4 Method Availability Assessment for PerturbMark

| Category | Methods Available for Benchmarking | Methods Potentially Unavailable |
|----------|------------------------------------|--------------------------------|
| **Immediately runnable** | GEARS, CPA, scGPT, Scouter, PerturbNet, all linear baselines, State | -- |
| **Code available, weights may need retraining** | Tahoe-x1, rBio | -- |
| **Partial availability** | X-Cell (code on GitHub, X-Atlas subset on HF), SCALE (preprint) | Full X-Atlas/Pisces data, X-Cell-Ultra weights |
| **Likely unavailable** | -- | AlphaCell, AetherCell, Stack (code/weights not confirmed public) |

**Recommendation:** PerturbMark should benchmark all immediately runnable methods plus Tahoe-x1 and any March 2026 models that release code before benchmark execution. Methods without public code should be noted as absent with explicit reason.

---

### Finding 3: The Metric Controversy -- Diagnosis and Resolution

#### 3.1 The Crisis in Numbers

As of April 2026, perturbation prediction papers use at least 13 different evaluation metrics, and different metrics give opposite conclusions about the same models:

| Metric | Used By | Known Failure Modes |
|--------|---------|-------------------|
| **MSE (Mean Squared Error)** | Ahlmann-Eltze et al. | Poorly calibrated (Miller et al., 2025); dominated by housekeeping genes; rewards mode collapse |
| **Pearson (delta, ctrl-referenced)** | Many papers | Poorly calibrated (Miller et al., 2025); inflated by systematic variation r=0.91--0.95 (Systema, 2025) |
| **Pearson (delta, perturbation-referenced)** | Systema | Better calibrated but sensitive to scaling |
| **MAE (Mean Absolute Error)** | Virtual Cell Challenge | Almost all VCC models performed WORSE than baseline on MAE |
| **WMSE (Weighted MSE)** | Diversity by Design (Camillo et al., 2025) | Correctly penalizes mean prediction; requires DEG-aware weighting |
| **Weighted R-squared (R^2_w delta)** | Diversity by Design | Correctly rewards diversity; sensitive to weight specification |
| **Dynamic Range Fraction** | Well-Calibrated Metrics (Miller et al., 2025) | New calibration measure; not yet widely adopted |
| **PDS (Perturbation Discrimination Score)** | Virtual Cell Challenge | Scale-sensitive; rewards correct expression patterns over exact magnitude |
| **DES (Differential Expression Score)** | Virtual Cell Challenge | Evaluates correct identification of up/down-regulated genes |
| **E-distance (Energy distance)** | scPerturBench | Can overlook disruptions in gene-gene interactions (Dibaeinia et al., 2026) |
| **Wasserstein distance** | scPerturBench | Fails in high-dimensional gene expression spaces under variance scaling (Dibaeinia et al., 2026); incompatible formulations across papers (1D per-gene vs multivariate vs LP) |
| **KL-divergence** | scPerturBench | Sensitive to support mismatch; requires density estimation |
| **Common-DEGs (DEG overlap)** | scPerturBench, SCALE | Discrete; threshold-dependent; does not capture magnitude |
| **DEG recall / DEG-F1** | Dibaeinia et al. (2026) | Only ~9% recall despite favorable aggregate metrics; weakly correlated with aggregate metrics (r=0.26 with Corr-delta; r=-0.05 with L2-delta) |
| **Centroid accuracy** | Systema (NatBiotech 2025) | Whether predicted profile is closer to correct vs incorrect ground-truth centroid |

#### 3.2 Specific Failure Mode Evidence

**Dibaeinia et al. (bioRxiv Feb 2026) -- "Evaluating Single-Cell Perturbation Response Models Is Far from Straightforward":**
- Used cross-splitting, controlled noise experiments, and synthetic data
- Wasserstein distance fails under variance scaling in high-dimensional gene expression spaces
- Energy distance can overlook disruptions in gene-gene interactions
- Correlation-based metrics are strongly influenced by scale, sparsity, and dimensionality
- DEG recall was only approximately 9% despite favorable aggregate metrics
- DEG-F1 correlated weakly with aggregate metrics (r=0.26 with Correlation-delta; r=-0.05 with L2-delta)
- Conclusion: "expectations for accurate and generalizable prediction are overly optimistic, largely due to the failure modes of existing evaluation metrics"

**Miller et al. (bioRxiv Oct 2025) -- "Well-Calibrated Metrics":**
- Tested 14 perturbation datasets x 13 evaluation metrics
- Introduced interpolated duplicate positive control: synthetic "good prediction" from replicate data
- Introduced dynamic range fraction: proportion of metric range between negative control (random prediction) and positive control (perfect prediction)
- MSE and control-referenced Pearson delta are "poorly calibrated" -- dynamic range fraction near zero
- Weighted and rank-based alternatives (WMSE, weighted R-squared) exhibit consistent calibration
- Under well-calibrated metrics, DL models DO outperform baselines

**Camillo et al. (arXiv Jun 2025) -- "Diversity by Design":**
- Control-referenced deltas and unweighted metrics reward mode collapse
- WMSE weights error by perturbation-specific DEG signal, allowing gene signal prioritization
- With WMSE as loss function, mode collapse reduces and model performance improves
- Under WMSE, mean baseline correctly sinks to null performance

#### 3.3 Proposed Minimal Metric Suite for PerturbMark

Based on the failure mode analysis, I propose a **7-metric core suite** that covers all known dimensions:

| Metric | Purpose | Calibration Status | Source |
|--------|---------|-------------------|--------|
| **WMSE (weighted MSE)** | Gene-level prediction accuracy, DEG-weighted | Well-calibrated (Miller et al.) | Diversity by Design |
| **Pearson-delta (centroid-referenced)** | Systematic variation correction | Better than ctrl-referenced | Systema (NatBiotech 2025) |
| **PDS (Perturbation Discrimination Score)** | Can model distinguish perturbations from each other? | Scale-sensitive but informative | Virtual Cell Challenge |
| **DES (Differential Expression Score)** | Correct identification of up/down-regulated genes | Biologically grounded | Virtual Cell Challenge |
| **DEG-F1** | Precision and recall of differentially expressed genes | Captures biological signal | Dibaeinia et al. (2026) |
| **Dynamic Range Fraction** | Metric calibration control (meta-metric) | Calibration measure | Miller et al. (2025) |
| **MMD (Maximum Mean Discrepancy)** | Distributional distance; robust in high dimensions | Sample-based, kernel-based | Alternative to Wasserstein/Energy |

**Explicitly excluded from the core suite (with justification):**
- Standard MSE: poorly calibrated, rewards mode collapse
- Standard Pearson-delta (ctrl-referenced): inflated by systematic variation
- Wasserstein distance: fails in high-dimensional spaces, incompatible implementations across papers
- Energy distance: overlooks gene-gene interaction disruptions
- KL-divergence: requires density estimation, sensitive to support mismatch

**Reporting requirement:** PerturbMark should report all 7 core metrics plus the dynamic range fraction for each metric, enabling calibration assessment. For backward compatibility, report MSE and Pearson-delta (ctrl-referenced) in supplementary tables with explicit warnings about their limitations.

---

### Finding 4: Cross-Context Benchmark Design -- The Tier 0--3 Framework

#### 4.1 Precise Tier Definitions

| Tier | Name | Definition | Data Requirement | Difficulty |
|------|------|-----------|-----------------|------------|
| **Tier 0** | In-distribution | Predict expression for held-out cells under SEEN perturbation in SEEN cell line. Random cell-level split within (perturbation, cell_line) groups. | Any dataset | Trivial (baseline benchmark) |
| **Tier 1** | Unseen perturbation | Predict expression under UNSEEN perturbation in SEEN cell line. Perturbation-level split: some compounds held out entirely from training within each cell line. | Sufficient perturbation diversity | Moderate |
| **Tier 2** | Unseen context (known perturbation) | Predict expression for KNOWN perturbation in UNSEEN cell line. Cell-line-level split: some cell lines held out from training entirely, but their perturbations appear in training on other lines. | Multi-context dataset with overlapping perturbations | Hard |
| **Tier 3** | Full cross-context | Predict expression for UNSEEN perturbation in UNSEEN cell line. Both cell line AND perturbation are held out. Neither appears together in training; the perturbation appears in other cell lines and the cell line appears with other perturbations. | Large multi-context dataset with rich overlap | Very hard (the true test) |

#### 4.2 Constructing Tier 3 Splits from Tahoe-100M

Tahoe-100M's 17,813 unique cell-line-drug conditions across 47 usable cell lines and 379 drugs enable the richest Tier 3 splits ever constructed for chemical perturbation prediction. The split construction protocol:

**Step 1: Cell line grouping by organ type**
- 13 organ types available; hold out cell lines by organ to maximize biological novelty
- Example split: Train on 40 cell lines from 11 organs, hold out all cell lines from 2 organs (e.g., all pancreas + all skin lines)
- This ensures the held-out cell lines are biologically distinct, not just label-held-out

**Step 2: Perturbation grouping by MOA**
- 25 curated MOA categories; hold out perturbations by MOA to test mechanistic generalization
- Example: Hold out all "kinase inhibitors" (up to 27 compounds); test whether models predict kinase inhibitor effects on unseen cell lines from compound structure alone
- This prevents trivial generalization from seeing similar-mechanism compounds in training

**Step 3: Ensuring training set coverage**
- For Tier 3: held-out perturbation P must appear in training with other cell lines; held-out cell line C must appear in training with other perturbations
- This is a matrix completion problem: the (C, P) test entries are missing, but C and P each appear in other rows/columns of the training matrix
- Tahoe-100M's 17,813 conditions provide sufficient density for this

**Step 4: Replication and statistical power**
- Minimum 20 held-out (cell_line, perturbation) pairs per tier for statistical power
- 5-fold cross-validation at the cell-line level: 5 different hold-out groups
- Report mean +/- standard error across folds

#### 4.3 Information Leakage Prevention

Known leakage risks in perturbation prediction benchmarks:

1. **Stereoisomer leakage:** Stereoisomers in training and test sets may have similar effects, inflating performance. PerturbMark must deduplicate by canonical SMILES before splitting. Tahoe-100M provides `canonical_smiles` per compound.

2. **Target overlap leakage:** Compounds with the same molecular target in train and test sets enable trivial generalization. PerturbMark must split by target gene, not just compound identity. Drug_metadata provides `targets` field.

3. **Plate batch effects:** Within Tahoe-100M, plate-matched DMSO controls must be used (not pooled DMSO). Cross-plate evaluation must be validated.

4. **Cell line family leakage:** Cell lines from the same tissue/donor may share transcriptional programs. DataSAIL (Nature Communications 2025) provides a leakage-reduced splitting tool applicable to biological data.

5. **Pre-training contamination:** Models pre-trained on Tahoe-100M (e.g., Tahoe-x1, SCALE) cannot be "fairly" evaluated on Tahoe-100M hold-outs. PerturbMark must track pre-training data and flag potential contamination.

#### 4.4 Statistical Power Requirements

Per tier, PerturbMark requires:
- **Tier 0:** Minimum 50 perturbation conditions evaluated (trivial to achieve)
- **Tier 1:** Minimum 30 held-out perturbations per cell line (achievable: 379 compounds, hold out 10%)
- **Tier 2:** Minimum 5 held-out cell lines per fold (achievable: 47 lines, 5-fold CV)
- **Tier 3:** Minimum 20 (cell_line, perturbation) test pairs per fold, with both axis held out (achievable given 17,813 conditions)

For effect size estimation: detecting a 0.05 improvement in Pearson-delta (the typical margin claimed by new models) with 80% power at alpha=0.05 requires approximately 400 test instances per tier. Tahoe-100M provides this comfortably for Tiers 0--2; Tier 3 depends on overlap density.

---

### Finding 5: Differentiation from scPerturBench

#### 5.1 What scPerturBench Covers

scPerturBench (Wei et al., Nature Methods 2026, vol. 23, pp. 451--464) is the most comprehensive existing perturbation prediction benchmark:

- **Methods:** 27 methods including biolord, CellOT, inVAE, scDisInFact, scGen, scPRAM, scPreGAN, SCREEN, scVIDR, trVAE, AttentionPert, CPA, GEARS, GenePert, linearModel, scGPT, scFoundation, chemCPA, Scouter, scELMo, GeneCompass, cycleCDR, PRnet, and 4 baselines
- **Datasets:** 29 datasets (primarily from scPerturb harmonized collection and custom datasets)
- **Metrics:** 6 metrics (MSE, PCC-delta, E-distance, Wasserstein distance, KL-divergence, Common-DEGs)
- **Evaluation tasks:** (a) Cellular context generalization (i.i.d. and o.o.d.), (b) Perturbation generalization (genetic and chemical)
- **Solution proposed:** bioLord-emCell (cellular context embedding + disentanglement)

#### 5.2 What scPerturBench Does NOT Cover (PerturbMark's Differentiation)

| Gap in scPerturBench | PerturbMark's Coverage |
|----------------------|----------------------|
| **No Tahoe-100M evaluation** | First systematic benchmark on the world's largest chemical perturbation dataset (100M cells, 50 cell lines, 379 drugs) |
| **No Tier 3 cross-context** | Full Tier 0--3 difficulty hierarchy with organ-based cell line hold-out AND MOA-based compound hold-out |
| **Uses 4 of 6 metrics that have known failure modes** | Calibrated 7-metric suite avoiding MSE, Wasserstein, Energy distance failure modes; includes WMSE, PDS, DES, DEG-F1 |
| **No metric calibration controls** | Dynamic range fraction + interpolated duplicate positive controls for every metric |
| **Missing March 2026 models** | Includes X-Cell, AlphaCell, AetherCell, SCALE, Stack, pertTF, Scouter, rBio |
| **No CRISPR-informed mean baseline** | All 5 mandatory linear baselines included |
| **Limited chemical perturbation coverage** | PerturbMark centers chemical perturbation as the primary evaluation modality |
| **No information leakage analysis** | Explicit stereoisomer, target-overlap, plate, cell-family, and pre-training contamination controls |
| **No systematic MOA-stratified analysis** | Performance stratified by 25 MOA categories reveals mechanism-specific model strengths/weaknesses |
| **Published before the metric crisis papers** | Integrates findings from Dibaeinia et al. (Feb 2026), Cole et al. (Feb 2026), and the Well-Calibrated Metrics framework |

#### 5.3 Framing: Complementary, Not Redundant

PerturbMark and scPerturBench are **complementary:**

- scPerturBench provides breadth (27 methods, 29 datasets, genetic + chemical)
- PerturbMark provides depth (Tahoe-100M's unprecedented scale + calibrated metrics + Tier 3 cross-context + 2026 methods)

The Nature Methods editorial pitch: "scPerturBench showed that methods struggle with cross-context generalization. PerturbMark reveals WHY: on the largest chemical perturbation dataset ever created, with calibrated metrics that avoid the failure modes documented in 2025--2026, we show that [finding]. This resolves the DL-vs-linear debate that has consumed the field since Ahlmann-Eltze et al. (2025)."

#### 5.4 What Would Make a Nature Methods Editor Send PerturbMark to Review?

1. **Resolution of the DL-vs-linear debate:** A definitive answer, on a dataset 50x larger than prior benchmarks, using calibrated metrics, would be the central contribution
2. **Tahoe-100M as the evaluation standard:** Establishing Tahoe-100M as the standard evaluation resource for chemical perturbation prediction (analogous to ImageNet for computer vision)
3. **The metric calibration story:** Demonstrating that different metrics give opposite conclusions on the same data, and providing the community with a calibrated metric suite
4. **March 2026 model evaluation:** First independent evaluation of X-Cell, AlphaCell, AetherCell, SCALE under standardized conditions
5. **Actionable guidelines:** Which method to use for which task, backed by evidence from 4 difficulty tiers

---

### Finding 6: Competition and Timeline Analysis

#### 6.1 Active Competition (April 2026)

| Competitor | Threat Level | Differentiation |
|-----------|-------------|-----------------|
| **scPerturBench** (NatMeth 2026) | High (published) | Different dataset, different metrics, different models; PerturbMark is complementary |
| **Cole et al.** (bioRxiv Feb 2026) | Medium | 600+ model variants but not a systematic benchmark; no Tier 3; GenBio AI affiliation (commercial) |
| **Dibaeinia et al.** (bioRxiv Feb 2026) | Medium | Metric critique paper, not a benchmark; identifies problems but does not provide the full benchmark solution |
| **OP3 benchmark** (NeurIPS 2024) | Low-Medium | 146 compounds, blood cells only; much smaller scale; PBMCs not cancer lines |
| **PerturBench** (Altos Labs, arXiv 2024) | Low-Medium | Overlapping scope but different focus areas |
| **Virtual Cell Challenge** (Arc Institute 2025) | Low | Challenge competition, not a peer-reviewed benchmark paper; 300K cells, 300 perturbations (H1 hESCs only) |

#### 6.2 Timeline Assessment

**Critical window:** The metric crisis papers (Dibaeinia, Cole, Well-Calibrated) have all appeared in October 2025--February 2026. The March 2026 model explosion (X-Cell, AlphaCell, AetherCell, SCALE, pertTF) has created a moment where the field desperately needs standardized evaluation. If PerturbMark is submitted by August 2026, it will be the first benchmark to:
- Use Tahoe-100M for systematic evaluation
- Include all March 2026 models
- Apply calibrated metrics informed by the 2025--2026 metric crisis
- Provide Tier 3 cross-context evaluation

**Risk of being scooped:** Medium. The most likely competitor would come from the Tahoe Bio team themselves (they have the data and compute), the Arc Institute (State + Virtual Cell Challenge infrastructure), or Xaira (X-Atlas/Pisces + X-Cell). However, these are model developers with commercial interests -- they are less likely to produce an independent, neutral benchmark than an academic team.

#### 6.3 Estimated Compute Budget

| Component | GPU-Hours | CPU-Hours |
|-----------|----------|----------|
| Data preprocessing (Tahoe-100M QC, normalization, pseudobulk) | 0 (pre-computed available) | 100 |
| Split construction and validation | 0 | 50 |
| Linear baselines (5 models x 4 tiers x 5 folds) | 10 | 200 |
| GEARS (re-train + evaluate) | 100 | 50 |
| CPA (re-train + evaluate) | 100 | 50 |
| scGPT (fine-tune + evaluate) | 200 | 50 |
| Scouter (re-train + evaluate) | 50 | 50 |
| PerturbNet (re-train + evaluate) | 100 | 50 |
| Tahoe-x1 (inference only, pre-trained) | 100 | 20 |
| State (inference + fine-tune) | 100 | 20 |
| X-Cell (if weights available) | 100 | 20 |
| Additional 2026 models (as available) | 200 | 50 |
| Analysis, visualization, metric computation | 10 | 100 |
| **Total** | **~1,070** | **~810** |

This falls well within the 1,000--2,000 GPU-hour budget estimated by Cohort 1, with headroom for iteration.

---

### Finding 7: The DL-vs-Linear Controversy -- Current State of Evidence

#### 7.1 Evidence Summary (April 2026)

The field is genuinely split. This is not a settled debate:

**DL fails (strong evidence):**
- Ahlmann-Eltze et al. (NatMeth 2025): 7 DL models all failed vs linear baselines on Norman/Adamson/Replogle. Evaluation on top-1000 genes by expression.
- Wong et al. (Bioinformatics 2025): CRISPR-informed mean surpasses GEARS by 4.7--213.9x, scGPT by 3.9--155.4x
- Systema (NatBiotech 2025): Performance correlates with systematic variation (r=0.91 for scGPT, r=0.95 for GEARS)
- Virtual Cell Challenge 2025: Almost all models worse than baseline on MAE; hybrid statistical models won

**DL works (strong evidence):**
- Well-Calibrated Metrics (Miller et al., bioRxiv 2025): Under WMSE and rank-based metrics, DL outperforms baselines across 14 datasets, 13 metrics
- Cole et al. (bioRxiv Feb 2026): 600+ model variants; some foundation models significantly improve predictions for both genetic and chemical perturbations
- X-Cell (bioRxiv March 2026): 5x Pearson delta improvement; zero-shot T-cell generalization
- AetherCell (bioRxiv March 2026): DEG PCC 0.82--0.83 on unseen cells/compounds
- Scouter (NatCompSci 2026): Reduces errors from GEARS/biolord by half or more

**The metric is the resolution key:**
- Dibaeinia et al. (bioRxiv Feb 2026): Widely used metrics have failure modes that misrepresent performance
- The debate is partly a measurement artifact: different camps use different metrics
- Under "poorly calibrated" metrics (MSE, ctrl-referenced Pearson), DL fails
- Under "well-calibrated" metrics (WMSE, weighted R-squared), DL succeeds
- **PerturbMark's central contribution is to run ALL methods under ALL metrics and reveal whether the DL advantage is real or artifactual**

#### 7.2 Prediction for PerturbMark Findings

Based on the evidence, I predict PerturbMark will find:

1. **Tier 0--1:** DL methods modestly outperform linear baselines under calibrated metrics, but the margin is smaller than claimed by individual papers
2. **Tier 2:** Performance degrades substantially for all methods; the gap between DL and linear narrows
3. **Tier 3:** This is the true test. The most likely outcome is that foundation models trained on diverse contexts (Tahoe-x1, State, X-Cell) show some advantage, but task-specific models (GEARS, CPA) do not generalize. Linear baselines may remain competitive even at Tier 3 if the biological signal in cell-line responses to compounds is dominated by shared transcriptional programs rather than context-specific responses.
4. **MOA-stratified analysis:** Some MOA categories (e.g., kinase inhibitors, DNA damage) will show stronger DL advantage than others (e.g., metabolic modulators), because the former have more consistent transcriptional signatures

---

## Implications for the Project

### Opportunities

1. **Perfect timing.** The March 2026 model explosion creates an unprecedented need for standardized evaluation. No existing benchmark covers all these models.

2. **Tahoe-100M is the ideal dataset.** 50 cell lines x 379 compounds x 17,813 conditions provides the richest cross-context evaluation ever possible for chemical perturbation. CC0 license removes all access barriers.

3. **The metric crisis IS the story.** PerturbMark's central innovation is not just "another benchmark" but "the benchmark that resolves a methodological controversy by demonstrating that different metrics give different answers, and providing the calibrated metrics that give the RIGHT answer."

4. **Low compute cost.** 1,000--2,000 GPU-hours is trivially achievable on the available HPC. This project can be completed in 6--8 weeks.

5. **Clear publication strategy.** Nature Methods has precedent for benchmark papers (scPerturBench itself was published there). The DL-vs-linear controversy is the hottest topic in computational biology. A definitive resolution would be immediately impactful.

### Risks

1. **scPerturBench overlap perception.** Reviewers may ask "how is this different from scPerturBench?" The differentiation must be made crystal clear in the introduction: different dataset (Tahoe-100M), different metrics (calibrated), different difficulty (Tier 3), different models (2026 generation).

2. **Model availability.** AlphaCell, AetherCell, and Stack may not release code/weights before PerturbMark execution. Mitigation: proceed with available methods; note absent methods explicitly.

3. **Pre-training contamination.** Tahoe-x1 and SCALE were trained on Tahoe-100M. Their evaluation on Tahoe-100M hold-outs may be contaminated. Mitigation: report results separately for models trained on Tahoe-100M vs models not trained on it; use strict hold-out ensuring zero overlap between pre-training and test partitions.

4. **No "surprising" finding.** If PerturbMark confirms what everyone already suspects (DL is better under calibrated metrics, worse under uncalibrated ones), the paper may be seen as confirmatory rather than surprising. Mitigation: the Tier 3 cross-context results will likely be novel, and the MOA-stratified analysis may reveal unexpected patterns.

5. **Data preprocessing choices.** Different normalization/QC pipelines could affect results. Mitigation: test sensitivity to preprocessing choices as a supplementary analysis; use at least two normalization schemes (raw counts + log1p-normalized + scVI latent space).

### Open Questions

1. **Which normalization to use?** Tahoe-100M provides raw counts. Standard scRNA-seq pipelines use library-size normalization + log1p. But some methods (e.g., PerturbNet with ZINB VAE) work on raw counts. Should PerturbMark standardize normalization or test multiple?
   - **Recommendation:** Test both (a) log1p-normalized and (b) scVI latent representations. Report both; if results differ, this is itself a finding.

2. **Gene subset for evaluation?** Ahlmann-Eltze used top-1000 most expressed genes. scPerturBench used DEGs. Virtual Cell Challenge used transcriptome-wide. Different subsets give different conclusions.
   - **Recommendation:** Report on (a) all genes, (b) top-2000 variable genes, (c) DEGs per condition, (d) DEGs union. Always report on DEGs per condition as the primary metric.

3. **How to handle multi-dose data?** Tahoe-100M includes dose information. Should each dose be treated as a separate perturbation condition?
   - **Recommendation:** Yes, for Tiers 0--2. For Tier 3, hold out by compound identity (all doses), which is the harder test.

4. **Should genetic perturbation data be included?** PerturbMark focuses on chemical perturbation (Tahoe-100M), but scPerturBench showed genetic and chemical perturbations behave differently.
   - **Recommendation:** Primary benchmark on Tahoe-100M (chemical). Supplementary validation on Replogle K562 (genetic) to demonstrate cross-perturbation-type generality of the metric suite.

5. **How to evaluate models that cannot run on Tahoe-100M?** Some task-specific models (GEARS, designed for genetic perturbations) may not directly apply to chemical perturbation prediction.
   - **Recommendation:** Adapt models to chemical perturbation where possible (CPA and PerturbNet natively support chemical perturbations). For genetic-only models, evaluate on the Replogle supplementary benchmark only.

---

## References

1. Zhang S, Gandhi S, et al. "Tahoe-100M: A Giga-Scale Single-Cell Perturbation Atlas for Context-Dependent Gene Function and Cellular Modeling." bioRxiv (2025). doi:10.1101/2025.02.20.639398

2. Wei Z, Wang Y, Gao Y, et al. "Benchmarking algorithms for generalizable single-cell perturbation response prediction." Nature Methods 23: 451--464 (2026). doi:10.1038/s41592-025-02980-0

3. Ahlmann-Eltze C, Huber W, Anders S. "Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines." Nature Methods (2025). doi:10.1038/s41592-025-02772-6

4. Wong DR, Hill AS, Moccia R. "Simple controls exceed best deep learning algorithms and reveal foundation model effectiveness for predicting genetic perturbations." Bioinformatics 41(6): btaf317 (2025). doi:10.1093/bioinformatics/btaf317

5. Vinas Torne R, Wiatrak M, Piran Z, et al. "Systema: a framework for evaluating genetic perturbation response prediction beyond systematic variation." Nature Biotechnology (2025).

6. Miller HE, Mejia GM, Leblanc FJA, et al. "Deep Learning-Based Genetic Perturbation Models Do Outperform Uninformative Baselines on Well-Calibrated Metrics." bioRxiv (2025). doi:10.1101/2025.10.20.683304

7. Camillo LP, et al. "Diversity by Design: Addressing Mode Collapse Improves scRNA-seq Perturbation Modeling on Well-Calibrated Metrics." arXiv:2506.22641 (2025).

8. Dibaeinia P, et al. "Evaluating Single-Cell Perturbation Response Models Is Far from Straightforward." bioRxiv (2026). doi:10.64898/2026.02.14.705879

9. Cole E, Huizing GJ, Addagudi S, et al. "Foundation Models Improve Perturbation Response Prediction." bioRxiv (2026). doi:10.64898/2026.02.18.706454

10. AlphaCell Team. "Towards building a World Model to simulate perturbation-induced cellular dynamics by AlphaCell." bioRxiv (2026). doi:10.64898/2026.03.02.709176

11. AetherCell Team. "AetherCell: A generative engine for virtual cell perturbation and in vivo drug discovery." bioRxiv (2026). doi:10.64898/2026.03.13.710968

12. Xaira Therapeutics. "X-Cell: Scaling Causal Perturbation Prediction Across Diverse Cellular Contexts via Diffusion Language Models." bioRxiv (2026). doi:10.64898/2026.03.18.712807

13. pertTF Team. "pertTF: context-aware AI modeling for genome-scale and cross-system perturbation prediction." bioRxiv (2026). doi:10.64898/2026.03.12.711379

14. SCALE Team. "SCALE: Scalable Conditional Atlas-Level Endpoint transport for virtual cell perturbation prediction." bioRxiv (2026). doi:10.64898/2026.03.17.712536

15. Stack Team. "Stack: In-Context Learning of Single-Cell Biology." bioRxiv (2026). doi:10.64898/2026.01.09.698608

16. Arc Institute. "State: Predicting cellular responses to perturbation across diverse contexts." bioRxiv (2025). doi:10.1101/2025.06.26.661135

17. Gandhi S, et al. "Tahoe-x1: Scaling Perturbation-Trained Single-Cell Foundation Models to 3 Billion Parameters." bioRxiv (2025). doi:10.1101/2025.10.23.683759

18. CZI. "rBio1: training scientific reasoning LLMs with biological world models as soft verifiers." bioRxiv (2025). doi:10.1101/2025.08.18.670981

19. Zhu Q, Li M. "Scouter predicts transcriptional responses to genetic perturbations with large language model embeddings." Nature Computational Science (2026). doi:10.1038/s43588-025-00912-8

20. Roohani Y, Huang K, Leskovec J. "Predicting transcriptional outcomes of novel multigene perturbations with GEARS." Nature Biotechnology 41: 1600--1609 (2023). doi:10.1038/s41587-023-01905-6

21. Lotfollahi M, et al. "Predicting cellular responses to complex perturbations in high-throughput screens." Molecular Systems Biology 19: e11517 (2023). doi:10.15252/msb.202211517

22. PerturbNet Team. "PerturbNet predicts single-cell responses to unseen chemical and genetic perturbations." Molecular Systems Biology (2025). doi:10.1038/s44320-025-00131-3

23. Peidli S, et al. "scPerturb: harmonized single-cell perturbation data." Nature Methods (2024). doi:10.1038/s41592-023-02144-y

24. Arc Institute. "Virtual Cell Challenge 2025 Wrap-Up: Winners and Reflections." (2025). https://arcinstitute.org/news/virtual-cell-challenge-2025-wrap-up

25. Open Problems in Single-Cell Analysis. "OP3: A benchmark for prediction of transcriptomic responses to chemical perturbations across cell types." NeurIPS 2024 Datasets and Benchmarks Track.

26. Hummer AM, et al. "DataSAIL: Data Splitting Against Information Leakage." Nature Communications (2025). doi:10.1038/s41467-025-58606-8

27. Virtual Cell Challenge Consortium. "Virtual Cell Challenge: Toward a Turing test for the virtual cell." Cell (2025). doi:10.1016/j.cell.2025.06.675

28. XPert Team. "Modelling drug-induced cellular perturbation responses with a biologically informed dual-branch transformer." Nature Machine Intelligence (2026). doi:10.1038/s42256-025-01165-w
