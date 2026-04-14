---
agent: sysnet
round: 2
date: 2026-04-14
type: deep-dive
---

# Deep Dive: Perturbation Prediction Crisis and Cross-Context Benchmark

## Executive Summary

The perturbation prediction field is in genuine crisis. Between March 2025 and April 2026, an extraordinary cascade of papers has systematically dismantled the claimed successes of deep learning for predicting cellular responses to genetic and chemical perturbations. The core finding: **no deep learning method has convincingly beaten simple linear baselines under properly calibrated evaluation**. Simultaneously, the field is witnessing an explosion of new models (X-Cell, AlphaCell, AetherCell, pertTF, Stack, State, rBio) and massive new datasets (X-Atlas/Pisces at 25.6M cells, Tahoe-100M at 100M cells), yet the fundamental benchmarking question remains unresolved. This creates a rare and extraordinary opportunity: a rigorous, independent, cross-context perturbation benchmark that definitively answers "what actually works" would be instantly high-impact.

---

## 1. Gap Verification

### 1.1 Is the Gap Still Open?

**Yes, emphatically.** The gap has not been resolved -- it has deepened and become more contentious as of early 2026. The field is now split into opposing camps:

**Camp 1: "DL Does Not Work"**
- Ahlmann-Eltze, Huber & Anders (Nature Methods 2025): 7 models (scGPT, scFoundation, GEARS, CPA, Geneformer, scBERT, UCE) all failed to outperform linear baselines on Norman, Adamson, and Replogle datasets.
- Wong, Hill & Moccia (Bioinformatics 2025): CRISPR-informed mean baseline surpassed all DL models by 4.7x to 213.9x over GEARS and 3.9x to 155.4x over scGPT depending on dataset.
- Vinas Torne et al. (Nature Biotechnology 2025, Systema): Performance on 10 datasets across 3 technologies and 5 cell lines correlated with systematic variation (r=0.91 for scGPT; r=0.95 for GEARS), meaning models learn confounders, not perturbation biology.
- Virtual Cell Challenge 2025 (Arc Institute): 5,000+ registrants, 300+ final submissions. Key finding: "perturbation prediction models are not yet consistently outperforming naive baselines across all metrics." Almost all models performed worse than baseline on MAE.
- Dibaeinia et al. (bioRxiv 2026, "Virtual Cells Need Context, Not Just Scale"): On a 22M-cell CD4+ T cell dataset, DEG recall was only ~9% despite favorable aggregate metrics. DEG-F1 correlated weakly with aggregate metrics (r=0.26 with Correlation-delta; r=-0.05 with L2-delta).

**Camp 2: "DL Works If You Measure Right"**
- bioRxiv 2025 ("Deep Learning-Based Genetic Perturbation Models Do Outperform Uninformative Baselines on Well-Calibrated Metrics"): Introduced dynamic range fraction and interpolated duplicate positive controls. Under weighted and rank-based metrics, DL models outperformed mean, control, and linear baselines.
- "Diversity by Design" (arXiv 2025): Showed control-referenced deltas and unweighted metrics reward mode collapse. Introduced weighted MSE (WMSE) and weighted delta R-squared that correctly penalize mean prediction.
- X-Cell (Xaira, March 2026): Claims 5x higher Pearson delta than next-best method on held-out iPSC perturbations, with zero-shot T-cell generalization.
- AetherCell (bioRxiv, March 2026): Median DEG PCC of 0.82-0.83 on unseen cells and compounds.
- Scouter (Nature Computational Science 2026): Claims to reduce errors from state-of-the-art by half or more.

**The verdict: The gap is not just open -- it is THE central methodological controversy in computational biology right now.** No consensus exists on (a) what metrics to use, (b) what baselines to require, (c) how to define cross-context generalization tasks, or (d) whether DL actually adds value over linear methods.

### 1.2 Recent Papers Attempting Resolution

| Paper | Venue | Date | Claim |
|-------|-------|------|-------|
| Ahlmann-Eltze et al. | Nature Methods | 2025 | DL fails vs. linear baselines |
| Systema (Vinas Torne et al.) | Nature Biotechnology | Aug 2025 | Methods learn systematic variation, not biology |
| Wong et al. | Bioinformatics | Jun 2025 | CRISPR-informed mean beats all DL by 4-214x |
| scPerturBench | Nature Methods | 2025 | 27 methods, 29 datasets: poor generalization |
| Well-Calibrated Metrics | bioRxiv | Oct 2025 | DL wins under proper metrics |
| Diversity by Design | arXiv | Jun 2025 | Mode collapse explains baseline dominance |
| Virtual Cell Challenge | Arc Institute | Dec 2025 | No model dominates all metrics |
| Virtual Cells Need Context | bioRxiv | Feb 2026 | Context diversity > scale |
| X-Cell | bioRxiv | Mar 2026 | 5x Pearson delta improvement |
| AlphaCell | bioRxiv | Mar 2026 | Zero-shot context generalization |
| AetherCell | bioRxiv | Mar 2026 | DEG PCC 0.82-0.83 |
| pertTF | bioRxiv | Mar 2026 | Cross-system perturbation prediction |
| Stack | bioRxiv | Jan 2026 | In-context learning for perturbation |
| State | bioRxiv | Jun 2025 | 30%+ discrimination improvement |
| rBio (CZI) | bioRxiv | Aug 2025 | Reasoning model beats SUMMER |

**No single paper resolves the crisis.** Each adds evidence but uses different metrics, datasets, and evaluation protocols, making direct comparison impossible.

---

## 2. Linear Baseline Evidence

### 2.1 The Ahlmann-Eltze et al. Nature Methods 2025 Paper

**Full citation:** Ahlmann-Eltze C, Huber W, Anders S. "Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines." Nature Methods (2025).

**What they tested:**
- 5 foundation models: scGPT, scFoundation, Geneformer, scBERT, UCE
- 2 task-specific DL models: GEARS, CPA
- Total: 7 deep learning approaches

**Baselines:**
1. **No-change model**: Predicts control expression for all perturbations (i.e., "nothing happens")
2. **Additive model**: For double perturbations, sums individual log fold changes
3. **Mean baseline**: Predicts average expression from training set
4. **Linear model**: Learned gene and perturbation embeddings with matrix factorization

**Datasets:**
- Norman et al. (K562): 100 single + 124 double CRISPRa perturbations; 19,264 genes
- Adamson et al. (K562): CRISPRi
- Replogle et al. (K562 and RPE1): Genome-scale Perturb-seq

**Key quantitative results:**
- **Double perturbations**: All 7 DL models had prediction error substantially higher than the additive baseline across 62 held-out doubles (L2 distance on 1,000 most-expressed genes)
- **Genetic interactions**: None of the models was better than the "no change" baseline for detecting epistatic interactions deviating from additivity
- **Single perturbations**: None of the DL models consistently outperformed mean prediction or the linear model across 134-210 unseen perturbations
- Models showed reduced prediction variation compared to ground truth and frequently predicted near-zero changes (mode collapse)
- DL models required orders of magnitude more compute than the linear baseline for equivalent or worse performance

### 2.2 The Wong et al. Bioinformatics 2025 Paper

**Full citation:** Wong DR, Hill AS, Moccia R. "Simple controls exceed best deep learning algorithms and reveal foundation model effectiveness for predicting genetic perturbations." Bioinformatics 41(6), btaf317 (2025).

**Key finding:** A CRISPR-informed mean baseline surpassed all DL models, with rank improvement ranging from **4.7x to 213.9x better than GEARS** and **3.9x to 155.4x better than scGPT** depending on dataset.

### 2.3 The Systema Framework (Nature Biotechnology 2025)

**Full citation:** Vinas Torne R, Wiatrak M, Piran Z, Fan S, Jiang L, Teichmann SA, Nitzan M, Brbic M. "Systema: a framework for evaluating genetic perturbation response prediction beyond systematic variation." Nature Biotechnology (2025).

**What is systematic variation:** Consistent transcriptional differences between perturbed and control cells arising from selection biases or confounders (e.g., growth rate differences, technical artifacts) rather than true perturbation-specific effects.

**Key findings:**
- Performance correlates with systematic variation: r=0.91 for scGPT, r=0.95 for GEARS
- Standard metrics overestimate performance by conflating systematic artifacts with genuine prediction
- Predicting responses to unseen perturbations is "substantially harder than standard metrics suggest"
- Proposed new metrics: Pearson correlation on delta profiles using centroid of perturbed cells; centroid accuracy (whether predicted profiles are closer to correct ground-truth centroid)

### 2.4 The Counter-Argument: Well-Calibrated Metrics

A bioRxiv preprint (October 2025) argues that the linear baseline dominance is partly a measurement artifact:
- Conventional metrics (MSE, control-referenced Pearson delta) are "poorly calibrated"
- They introduced the **dynamic range fraction** and **interpolated duplicate** positive control
- Under weighted and rank-based alternatives (WMSE, weighted R-squared), DL models DO outperform baselines
- This is supported by the "Diversity by Design" paper showing that mode collapse is rewarded by standard metrics

**Critical assessment:** This counter-argument has merit but remains unresolved. The field lacks consensus on which metrics are correct. This is itself a major gap.

---

## 3. Dataset Accessibility Audit

### 3.1 Available Perturbation Datasets

| Dataset | Cells | Perturbation Type | Cell Types | Public | Format | Source |
|---------|-------|--------------------|------------|--------|--------|--------|
| **Tahoe-100M** | 100.6M | 1,100 small molecules | 50 cancer cell lines | Yes (CC0) | Parquet, 429 GB | HuggingFace |
| **X-Atlas/Pisces** | 25.6M | CRISPRi genome-wide | 16 contexts (HCT116, HEK293T, HepG2, iPSC, Jurkat) | Partial (subset on HF) | h5ad | HuggingFace |
| **Replogle et al.** | ~2.5M | CRISPRi genome-wide | K562, RPE1 | Yes | h5ad, AnnData | Figshare, gwps.wi.mit.edu |
| **Norman et al.** | 81K | CRISPRa (100 single + 131 double) | K562 | Yes | h5ad | Figshare, Google Drive |
| **scPerturb** | ~millions | 44 datasets (CRISPR + drugs) | Multiple | Yes | h5ad | scperturb.org, Zenodo |
| **Virtual Cell Challenge** | ~300K | CRISPRi (300 perturbations) | H1 hESCs | Yes | Unknown | Arc Institute |
| **Perturb-Sapiens** | Generated | 201 perturbations | 40 cell classes, 28 tissues | Yes | Unknown | HuggingFace (Arc) |
| **Adamson et al.** | ~50K | CRISPRi | K562 | Yes | h5ad | scPerturb |

### 3.2 Dataset Characteristics Summary

**Genetic perturbation data (CRISPRi/CRISPRa):**
- Replogle K562 genome-wide: ~9,000 genes targeted, ~2.5M cells
- Replogle K562 essential: 2,012 gene sets
- Replogle RPE1 essential: 2,094 gene sets
- Norman: 287 perturbation conditions (100 single + 131 double combinations from 112 genes)
- X-Atlas/Pisces: 25.6M cells across 16 contexts, genome-wide CRISPRi

**Chemical perturbation data:**
- Tahoe-100M: 100M cells, 1,100 compounds, 50 cancer cell lines, CC0 license, 429 GB on HuggingFace
- scPerturb includes 9 drug-perturbation datasets

**Critical observation:** The field has a massive imbalance. Tahoe-100M provides enormous chemical perturbation data but is cancer-cell-line-centric. X-Atlas/Pisces is the largest genetic perturbation resource but only a subset is publicly released. Most benchmarks still rely on Norman (81K cells, K562 only) and Replogle, which are tiny compared to what is now available.

### 3.3 Format Interoperability

All major datasets use **AnnData/h5ad** format (Python scanpy ecosystem) or **Parquet** (Tahoe-100M). The scPerturb project has harmonized 44 datasets with uniform QC and feature annotations. However, cross-dataset integration (e.g., combining Tahoe chemical data with X-Atlas genetic data) has not been systematically attempted and would require substantial preprocessing.

---

## 4. Method Landscape

### 4.1 Complete Method Catalog

| Method | Year | Architecture | Claimed Performance | Evaluation Methodology | Status |
|--------|------|-------------|---------------------|----------------------|--------|
| **CPA** | 2023 | Compositional perturbation autoencoder (VAE) | Compositional generalization | In-distribution splits | Published, Nature Methods |
| **GEARS** | 2023 | GNN + gene embeddings on Gene Ontology | Novel multigene prediction | Norman dataset, held-out doubles | Published, Nature Biotech |
| **scGPT** | 2024 | Transformer foundation model, 33M cells pretrained | General single-cell tasks | Fine-tuned on Norman | Published, Nature Methods |
| **scFoundation** | 2024 | Large foundation model, 50M cells | Broad transfer learning | Multiple downstream tasks | Published |
| **Geneformer** | 2023 | Transformer, 30M cells | Gene network prediction | Transfer learning | Published, Nature |
| **scBERT** | 2022 | BERT-style transformer | Cell type annotation + perturbation | Norman dataset | Published |
| **UCE** | 2024 | Universal cell embedding | Broad cell representation | Cross-dataset transfer | Published |
| **X-Cell** | Mar 2026 | Diffusion language model, 4.9B params | 5x Pearson delta over next-best | X-Atlas/Pisces, held-out iPSC | Preprint, proprietary data |
| **AlphaCell** | Mar 2026 | OT conditional flow matching, latent manifold rectification | Zero-shot cross-context | Compositional generalization | Preprint |
| **AetherCell** | Mar 2026 | Generative foundation model | DEG PCC 0.82-0.83 unseen compounds | Unseen cell and compound scenarios | Preprint |
| **pertTF** | Mar 2026 | Transformer + GNN (GEARS-derived gene embeddings) | Cross-system perturbation | Pancreatic development contexts | Preprint |
| **Stack** | Jan 2026 | Tabular attention, 149M cells pretrained | In-context learning for perturbation | Zero-shot Perturb-Sapiens | Preprint |
| **State** | Jun 2025 | Dual-module transformer (ST + SE) | 30%+ discrimination improvement | 100M+ perturbed + 167M unperturbed cells | Preprint (Arc) |
| **rBio** | Aug 2025 | Qwen-based reasoning model with RL | Beats SUMMER on PerturbQA | Virtual cell simulation rewards | Preprint (CZI) |
| **Scouter** | 2026 | LLM embeddings for perturbation | 50%+ error reduction vs SOTA | Nature Comp Sci paper | Published |
| **PerturbNet** | 2025 | Deep generative (VAE + normalizing flow) | Chemical + genetic in one model | Unseen genes and compounds | Published, Nature Comp Biology |
| **BioMap (BM_xTVC)** | Dec 2025 | Hybrid DL + classical statistics | Won Virtual Cell Challenge | scFoundation + protein embeddings | Competition winner |
| **Altos Labs** | Dec 2025 | Flow matching generative model, U-Net | Won Generalist Prize | 7M cells pretrained | Competition winner |

### 4.2 Key Observations

1. **Model proliferation without resolution**: At least 18 distinct methods have been proposed, yet no head-to-head comparison uses identical datasets, splits, and metrics.

2. **Private data advantage**: X-Cell (Xaira, $1B+ funded) trained on 25.6M proprietary cells before partial release. AetherCell uses undisclosed clinical data. Fair comparison is impossible when training data differs.

3. **Metric disagreement**: Papers claiming DL wins use WMSE, weighted R-squared, or perturbation discrimination scores. Papers claiming DL fails use MSE, Pearson delta, or DEG overlap. The choice of metric determines the conclusion.

4. **Evaluation protocol fragmentation**: Each paper defines its own train/test splits, gene subsets, and "unseen" criteria. No standard exists for "cross-context" generalization.

5. **Compute asymmetry**: X-Cell at 4.9B parameters likely requires hundreds of GPU-hours; the linear baseline runs in seconds on a laptop. If performance differences are marginal, the practical utility argument collapses.

---

## 5. Benchmark Design

### 5.1 What Would a Definitive Cross-Context Perturbation Benchmark Look Like?

Drawing on Ahlmann-Eltze, Systema, scPerturBench, the Virtual Cell Challenge, and "Virtual Cells Need Context," the following benchmark design would be genuinely definitive.

### 5.2 Benchmark Difficulty Tiers (from Dibaeinia et al.)

| Tier | Description | What It Tests |
|------|-------------|---------------|
| **Tier 0** | In-distribution: same cell type, seen perturbation | Interpolation / memorization |
| **Tier 1** | New perturbation, same context | Perturbation generalization |
| **Tier 2** | Same perturbation, new context | Context generalization |
| **Tier 3** | New perturbation, new context | True cross-context transport |

Most existing benchmarks only test Tier 0-1. Tier 3 is what matters for real-world applications and where all methods currently fail.

### 5.3 Required Datasets

A definitive benchmark must span:
- **Multiple perturbation modalities**: CRISPRi (loss-of-function), CRISPRa (gain-of-function), small molecules
- **Multiple cell types**: At least 5-10 diverse cell types with shared perturbations
- **Shared perturbation overlaps**: Same genes/compounds tested across contexts to enable Tier 2-3 evaluation

**Recommended dataset stack:**
1. **Replogle et al.** (K562 + RPE1 genome-wide CRISPRi) -- mature, well-characterized, shared gene overlaps
2. **X-Atlas/Pisces subset** (HCT116, HEK293T, HepG2, iPSC, Jurkat CRISPRi) -- 16 contexts with genome-wide coverage
3. **Tahoe-100M** (50 cancer lines, 1,100 compounds) -- chemical perturbation cross-context
4. **Norman et al.** (K562 CRISPRa combinatorial) -- double perturbation benchmark
5. **scPerturb harmonized collection** -- additional diversity

### 5.4 Train/Test Split Protocol

**Critical requirement: Strict information leakage prevention.**

1. **Perturbation-level hold-out**: Entire perturbation identities held out (not random cell-level splits)
2. **Context-level hold-out**: Entire cell types/conditions held out for Tier 2-3
3. **Temporal hold-out**: If data spans timepoints, later timepoints as test
4. **No overlapping perturbation-context pairs between train and test** for Tier 3

**Split ratios per tier:**
- Tier 1: 70/15/15 perturbation split within each context
- Tier 2: Leave-one-context-out (train on N-1 contexts, test on held-out context)
- Tier 3: Leave-one-context-out AND hold out subset of perturbations not seen in training contexts

### 5.5 Required Metrics (Resolving the Metric War)

Based on the metric calibration literature, the benchmark must report ALL of the following:

**Aggregate accuracy:**
- MSE (standard, despite flaws, for comparability)
- Weighted MSE (WMSE, from "Diversity by Design") -- upweights DEGs
- Pearson correlation on raw expression
- Pearson correlation on delta profiles (Pearson-delta)
- Weighted delta R-squared (R-squared_w, from "Diversity by Design")

**Biological recovery:**
- DEG precision, recall, F1 (top-N and threshold-based)
- Overlap of direction of change (up vs. down)
- Gene set enrichment preservation (GO term overlap between predicted and true DEGs)

**Distributional fidelity:**
- E-distance (from scPerturb)
- Wasserstein distance
- Perturbation discrimination score (PDS, from Virtual Cell Challenge)

**Calibration controls (from "Well-Calibrated Metrics" paper):**
- Dynamic range fraction for each metric
- Interpolated duplicate positive control
- Mean-prediction negative control
- No-change negative control

### 5.6 Required Baselines

Every method must be compared against:
1. **No-change model**: Predict control expression
2. **Mean model**: Predict mean of training perturbation expressions
3. **CRISPR-informed mean** (from Wong et al.): Predict mean informed by CRISPR status
4. **Additive model**: Sum individual LFCs for combinations
5. **Linear model with perturbation embeddings** (from Ahlmann-Eltze): Matrix factorization approach
6. **k-NN in perturbation space**: Use gene/compound similarity to retrieve nearest training perturbation

---

## 6. Compute Requirements

### 6.1 Model Training Costs (Estimated)

| Model | Parameters | Estimated Training | GPU Type | Time Estimate |
|-------|-----------|-------------------|----------|---------------|
| **Linear baseline** | ~10K | CPU only | None | Minutes |
| **GEARS** | ~1M | Single GPU | H100 | Hours (single dataset) |
| **CPA** | ~5M | Single GPU | H100 | Hours |
| **scGPT fine-tune** | ~51M | Single GPU | H100 | 1-4 hours (fine-tuning) |
| **scGPT pretrain** | ~51M | Multi-GPU | A100/H100 cluster | Days (33M cells, 6 epochs) |
| **scFoundation** | ~100M | Multi-GPU | A100 cluster | Days-weeks |
| **X-Cell Mini** | 55M | Unknown | Unknown | Unknown |
| **X-Cell Ultra** | 4.9B | Large GPU cluster | Likely H100/A100 cluster | Weeks-months (estimated) |
| **State (Arc)** | Unknown | Multi-GPU | Unknown | Days (100M+ cells) |
| **Stack** | Unknown | Multi-GPU | Unknown | Days (149M cells pretrained) |

### 6.2 Benchmark Execution Costs

For a definitive benchmark evaluating ~15 methods across ~5 dataset configurations with ~4 difficulty tiers:

- **Data processing**: Loading and preprocessing Tahoe-100M (429 GB) + X-Atlas/Pisces (~100+ GB) + Replogle (~50 GB) requires substantial RAM (256+ GB) and storage (1+ TB)
- **Baseline computation**: Hours on CPU cluster
- **DL method training**: ~10-50 GPU-hours per method per dataset on H200/A100
- **Full benchmark**: ~500-2,000 GPU-hours total (manageable on described HPC cluster with H200, RTX 5000 Ada, B200)
- **Metric computation**: Hours on CPU (E-distance, Wasserstein expensive for large datasets)

### 6.3 Feasibility on Available HPC

The described compute environment (H200, RTX 5000 Ada, B200 GPUs, hundreds of CPU nodes) is **more than sufficient** for this benchmark project:
- Training even the largest reproducible models (scGPT, State) requires at most a few H200 GPUs for days
- The massive datasets (Tahoe-100M, X-Atlas) can be processed in streaming mode
- The benchmark is embarrassingly parallel across methods and datasets
- No need to pretrain foundation models from scratch -- use released checkpoints
- Total compute: 1,000-2,000 GPU-hours is well within summer 2026 budget

---

## 7. Competition Assessment

### 7.1 Who Is Building Perturbation Benchmarks?

| Group | Effort | Status | Limitations |
|-------|--------|--------|-------------|
| **Ahlmann-Eltze lab (EMBL)** | Linear baseline comparison | Published (Nat Methods 2025) | Only 3 datasets, only 2 baselines, no cross-context |
| **Brbic lab (EPFL) -- Systema** | Systematic variation evaluation | Published (Nat Biotech 2025) | 10 datasets but single-context focus, no standard splits |
| **bm2-lab -- scPerturBench** | 27 methods, 29 datasets | Published (Nat Methods 2025) | Broadest but lacks metric calibration, limited cross-context |
| **Arc Institute -- Virtual Cell Challenge** | Public competition | Completed (Dec 2025) | Single cell type (H1 hESCs), limited generalization testing |
| **Arc Institute -- State** | State model + benchmark | Preprint (Jun 2025) | Proprietary model, not a neutral benchmark |
| **CZI -- Virtual Cells Platform** | cz-benchmarks package | Active (2025-2026) | Platform-centric, 6 tasks but embedded in CZI ecosystem |
| **Xaira -- X-Cell** | X-Atlas/Pisces + X-Cell | Preprint (Mar 2026) | Proprietary data, company-authored benchmark |
| **Dibaeinia et al. (Chicago/Biohub)** | "Context Not Scale" analysis | Preprint (Feb 2026) | Position paper, not executable benchmark |
| **Wong et al. (industry)** | CRISPR-informed mean | Published (Bioinformatics 2025) | Narrow scope, no cross-context |
| **"Well-Calibrated Metrics" authors** | Metric calibration framework | Preprint (Oct 2025) | Metrics only, no new benchmark protocol |

### 7.2 What Is Missing

**No existing effort combines ALL of the following:**
1. Multiple datasets spanning genetic AND chemical perturbations
2. Standardized difficulty tiers (Tier 0-3 cross-context)
3. Both "old" metrics (MSE, Pearson) and "new" calibrated metrics (WMSE, weighted R-squared, dynamic range fraction)
4. Comprehensive baselines (no-change, mean, CRISPR-informed mean, additive, linear, k-NN)
5. All major methods from both industry (X-Cell, AetherCell) and academia (GEARS, CPA, scGPT, State, Stack)
6. Reproducible code and data infrastructure
7. Neutral academic authorship (not affiliated with any competing method)

**This is the gap.** Everyone has built partial benchmarks that support their own method or critique. No one has built the definitive, comprehensive, neutral benchmark.

### 7.3 Timing Assessment

The window is optimal:
- Tahoe-100M released February 2025 (CC0 license)
- X-Atlas/Pisces subset released March 2026
- scPerturBench published 2025, Systema published 2025 -- the field is primed for synthesis
- The "metric war" papers (2025) have identified the problem but not solved it
- 15+ methods now exist to benchmark
- Virtual Cell Challenge demonstrated massive community interest (5,000+ registrants)
- Nature Methods and Nature Biotechnology have published benchmarking papers in this space -- the venue is receptive

**Risk**: The scPerturBench team or CZI could preempt with a more comprehensive v2. However, their current efforts lack the cross-context focus and metric calibration integration that would make a benchmark definitive.

---

## 8. Feasibility Reassessment

### 8.1 Strengths

- **All key datasets are publicly available**: Tahoe-100M (CC0), Replogle (public), Norman (public), scPerturb (public), X-Atlas/Pisces (partial public release), Virtual Cell Challenge data (public)
- **All key methods are open-source**: GEARS (GitHub), CPA (GitHub), scGPT (GitHub), scFoundation (GitHub), State (GitHub), Stack (GitHub), X-Cell Mini (GitHub/HuggingFace), Systema (GitHub)
- **Compute is sufficient**: 1,000-2,000 GPU-hours on available HPC
- **No wet lab required**: Entirely computational
- **Strong publication precedent**: scPerturBench (Nat Methods), Systema (Nat Biotech), Ahlmann-Eltze (Nat Methods) -- all benchmark papers in top venues

### 8.2 Weaknesses and Risks

- **Reproducibility burden**: Running 15+ methods across 5+ datasets requires substantial engineering. Some methods have undocumented dependencies or broken codebases.
- **X-Cell full model not public**: X-Cell Ultra (4.9B) weights may never be released. X-Cell Mini (55M) is available. This limits comparison with the most hyped method.
- **AetherCell code availability**: Unknown if reproducible.
- **Data scale**: Processing Tahoe-100M (429 GB, 100M cells) and X-Atlas/Pisces (25.6M cells) requires significant data engineering.
- **Metric calibration**: Implementing the dynamic range fraction and interpolated duplicate requires careful statistical work.
- **Scope creep**: The temptation to include every method and dataset could make the project unwieldy.

### 8.3 Mitigation Strategy

- **Prioritize reproducible methods**: Only benchmark methods with working public code. Document any method that cannot be reproduced.
- **Use scPerturBench codebase**: The bm2-lab has 27 methods already implemented. Extend rather than rebuild.
- **Start with Replogle + X-Atlas subset**: These are manageable-scale datasets with cross-context overlaps. Add Tahoe-100M for chemical perturbation validation.
- **Implement metric suite early**: Build the multi-metric evaluation framework first, then add methods incrementally.
- **Timeline**: 2-3 months data engineering + evaluation framework, 1-2 months running all methods, 1 month analysis and writing.

### 8.4 Feasibility Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Data availability | 9 | Nearly all data public; only X-Cell Ultra and AetherCell training data restricted |
| Method reproducibility | 7 | Most methods open-source but integration work needed |
| Compute feasibility | 9 | Well within HPC budget |
| Timeline (summer 2026) | 7 | Aggressive but achievable with focused scope |
| No wet lab required | 10 | Entirely computational |
| Novel contribution | 9 | No existing benchmark combines all elements |
| Publication potential | 9 | Nature Methods / Nature Biotechnology receptive to benchmarks |

**Overall feasibility: 8.6/10**

---

## 9. Publication Framing

### 9.1 Proposed Title

**"What Actually Works in Perturbation Prediction: A Cross-Context Benchmark with Calibrated Metrics and Standardized Baselines"**

Alternative: "Perturbation Prediction at the Crossroads: A Definitive Benchmark Resolving the Linear-vs-Deep-Learning Debate"

### 9.2 Target Venue

**Primary**: Nature Methods (has published Ahlmann-Eltze, scPerturBench, scPerturb -- the natural home)
**Secondary**: Nature Biotechnology (published Systema, GEARS -- receptive to perturbation prediction work)
**Reach**: Nature Computational Science (published Scouter, PerturbNet -- growing interest)

### 9.3 Main Claim

Under a unified evaluation framework with calibrated metrics, standardized difficulty tiers, and comprehensive baselines, we resolve the perturbation prediction debate and identify the specific conditions under which deep learning adds genuine value over linear methods -- and where it does not.

### 9.4 Key Figures

1. **Figure 1**: Benchmark design schematic showing difficulty tiers (Tier 0-3), datasets, methods, and metric categories
2. **Figure 2**: Heatmap of method performance across datasets and tiers, highlighting where DL wins/loses vs. baselines
3. **Figure 3**: Metric calibration analysis showing dynamic range fractions for all metrics, demonstrating which are well-calibrated
4. **Figure 4**: "The Context Gap" -- performance degradation from Tier 1 to Tier 3 across methods
5. **Figure 5**: DEG recovery vs. aggregate metrics scatter plot showing dissociation (extending Dibaeinia et al.)
6. **Figure 6**: Scaling analysis -- compute cost vs. marginal performance gain for each method
7. **Supplementary**: Full results for all methods x datasets x tiers x metrics (~50 supplementary figures)

### 9.5 What Reviewers Will Attack

1. **"You did not include [Method X]"**: Preempt by documenting every method attempted, including those that could not be reproduced.
2. **"Your splits are not fair to DL methods"**: Use multiple split strategies and report all. Include both random and structured splits.
3. **"Your datasets are too small/old"**: Include Tahoe-100M and X-Atlas to represent state-of-the-art data scale.
4. **"You are biased toward baselines"**: Include the "well-calibrated metrics" framework that favors DL, alongside traditional metrics. Let readers see both.
5. **"The field is moving too fast -- this will be outdated"**: Position as a benchmark FRAMEWORK (code + data + metrics) that others can extend, not just a snapshot.

### 9.6 Comparison Baselines Needed

The minimal viable paper requires:
- 6 baselines (no-change, mean, CRISPR-informed mean, additive, linear, k-NN)
- 8-10 DL methods (GEARS, CPA, scGPT, scFoundation, State, Stack, X-Cell Mini, Scouter, PerturbNet, plus 1-2 others)
- 3-4 datasets with cross-context structure
- 4 difficulty tiers
- 10+ metrics spanning aggregate, biological, distributional, and calibration categories

### 9.7 Minimal Viable Experiment

**Phase 1 (Month 1-2)**: Build evaluation framework
- Implement all metrics with calibration controls
- Process Replogle (K562 + RPE1) and X-Atlas/Pisces subset
- Define Tier 0-3 splits
- Run all baselines

**Phase 2 (Month 2-3)**: Run methods
- GEARS, CPA, scGPT (established methods with working code)
- State, Stack, X-Cell Mini (recent methods with available code)
- Scouter, PerturbNet (published with code)

**Phase 3 (Month 3-4)**: Chemical perturbation extension
- Add Tahoe-100M for drug perturbation benchmark
- Run CPA, chemCPA, PerturbNet, AetherCell (if code available)

**Phase 4 (Month 4-5)**: Analysis and writing
- Cross-method, cross-dataset, cross-tier analysis
- Compute cost vs. performance analysis
- Context diversity analysis (extending Dibaeinia et al.)
- Write manuscript

---

## 10. Combined Project Delta Design

### 10.1 Project Title

**"PerturbMark: A Unified Cross-Context Benchmark for Cellular Perturbation Prediction with Calibrated Metrics"**

### 10.2 Project Scope

PerturbMark unifies the two related gaps (perturbation prediction crisis + cross-context generalization) into a single coherent project that:

1. **Resolves the metric war**: Implements both traditional and calibrated metrics with positive/negative controls, enabling the field to see results under both frameworks simultaneously.

2. **Establishes difficulty tiers**: Formalizes Tier 0-3 cross-context generalization as the standard evaluation protocol, making it impossible for future papers to only report easy evaluations.

3. **Provides comprehensive baselines**: Sets the bar with 6 carefully implemented baselines, including the CRISPR-informed mean and linear embedding model that have embarrassed DL methods.

4. **Benchmarks 10+ methods head-to-head**: First time all major methods are evaluated on identical data, splits, and metrics.

5. **Tests context vs. scale hypothesis**: Uses Tahoe-100M and X-Atlas/Pisces to directly test whether context diversity or data scale drives generalization, extending the Dibaeinia et al. analysis.

6. **Releases a living benchmark**: Code, processed datasets, splits, and evaluation infrastructure as a community resource. Future methods can be immediately evaluated against the benchmark.

### 10.3 Deliverables

1. **Benchmark framework** (Python package): Standardized data loading, split generation, metric computation, result visualization
2. **Processed datasets**: Pre-split versions of Replogle, X-Atlas/Pisces, Tahoe-100M, Norman in uniform format
3. **Baseline implementations**: 6 baselines, rigorously tested
4. **Method evaluation results**: All methods across all tiers and metrics
5. **Nature Methods manuscript**: The definitive benchmarking paper
6. **Web dashboard**: Interactive exploration of results (like scPerturBench-reproducibility)

### 10.4 Why This Is Nature Methods Material

1. **Timeliness**: The field is in active crisis. Five contradictory papers in 2025 alone. The community needs resolution.
2. **Comprehensiveness**: No existing benchmark covers all methods, datasets, tiers, and metrics.
3. **Community impact**: 5,000+ people registered for the Virtual Cell Challenge. The audience is massive and hungry for guidance.
4. **Precedent**: scPerturBench and Ahlmann-Eltze were both published in Nature Methods. This would be the definitive follow-up.
5. **Neutrality**: Academic benchmark from a group not affiliated with any competing method.
6. **Lasting value**: The framework enables ongoing evaluation as new methods appear.

### 10.5 Novelty Assessment

| Component | Novel? | Explanation |
|-----------|--------|-------------|
| Cross-context difficulty tiers | Partially | Dibaeinia proposed conceptually; not implemented as executable benchmark |
| Calibrated metric suite | Novel combination | Individual metrics exist; unified suite with calibration controls is new |
| Comprehensive baseline set | Novel combination | Individual baselines published; systematic comparison across tiers is new |
| Multi-modality (genetic + chemical) | Novel | No benchmark spans CRISPRi + CRISPRa + small molecules |
| Context vs. scale analysis | Extension | Extends Dibaeinia's analysis with more methods and datasets |
| Living benchmark infrastructure | Novel for this field | scPerturBench web interface exists but lacks calibrated metrics and tiers |

### 10.6 Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Method code breaks | High | Medium | Document failures; use scPerturBench implementations where possible |
| X-Cell Ultra never released | Medium | Low | Benchmark X-Cell Mini; document gap |
| Someone publishes similar benchmark | Medium | High | Move fast; our calibrated-metrics + tiers angle is unique |
| Tahoe-100M too large to process | Low | Medium | Use streaming mode; subsample if needed |
| Metric calibration framework is wrong | Low | High | Include both calibrated and uncalibrated metrics; let readers decide |
| Summer 2026 timeline insufficient | Medium | Medium | Scope to MVP first (Replogle + 3 methods + all metrics), then expand |

---

## References

1. Ahlmann-Eltze C, Huber W, Anders S. "Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines." Nature Methods (2025). DOI: 10.1038/s41592-025-02772-6

2. Wong DR, Hill AS, Moccia R. "Simple controls exceed best deep learning algorithms and reveal foundation model effectiveness for predicting genetic perturbations." Bioinformatics 41(6), btaf317 (2025). DOI: 10.1093/bioinformatics/btaf317

3. Vinas Torne R, Wiatrak M, Piran Z, Fan S, Jiang L, Teichmann SA, Nitzan M, Brbic M. "Systema: a framework for evaluating genetic perturbation response prediction beyond systematic variation." Nature Biotechnology (2025). DOI: 10.1038/s41587-025-02777-8

4. Dibaeinia P, Babu S, Knudson M, ElSheikh A, Wen Y, Liu H, Perera J, Khan AA. "Virtual Cells Need Context, Not Just Scale." bioRxiv (2026). DOI: 10.64898/2026.02.04.703804

5. Xaira Therapeutics. "X-Cell: Scaling Causal Perturbation Prediction Across Diverse Cellular Contexts via Diffusion Language Models." bioRxiv (2026). DOI: 10.64898/2026.03.18.712807

6. "Towards building a World Model to simulate perturbation-induced cellular dynamics by AlphaCell." bioRxiv (2026). DOI: 10.64898/2026.03.02.709176

7. "AetherCell: A generative engine for virtual cell perturbation and in vivo drug discovery." bioRxiv (2026). DOI: 10.64898/2026.03.13.710968

8. "pertTF: context-aware AI modeling for genome-scale and cross-system perturbation prediction." bioRxiv (2026). DOI: 10.64898/2026.03.12.711379

9. "Stack: In-Context Learning of Single-Cell Biology." bioRxiv (2026). DOI: 10.64898/2026.01.09.698608

10. "Predicting cellular responses to perturbation across diverse contexts with State." bioRxiv (2025). DOI: 10.1101/2025.06.26.661135

11. "rbio1 - training scientific reasoning LLMs with biological world models as soft verifiers." bioRxiv (2025). DOI: 10.1101/2025.08.18.670981

12. "Deep Learning-Based Genetic Perturbation Models Do Outperform Uninformative Baselines on Well-Calibrated Metrics." bioRxiv (2025). DOI: 10.1101/2025.10.20.683304

13. "Diversity by Design: Addressing Mode Collapse Improves scRNA-seq Perturbation Modeling on Well-Calibrated Metrics." arXiv (2025). 2506.22641

14. Benchmarking algorithms for generalizable single-cell perturbation response prediction (scPerturBench). Nature Methods (2025). DOI: 10.1038/s41592-025-02980-0

15. Peidli S et al. "scPerturb: harmonized single-cell perturbation data." Nature Methods 21, 531-540 (2024). DOI: 10.1038/s41592-023-02144-y

16. Replogle JM et al. "Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq." Cell 185, 2559-2575 (2022). DOI: 10.1016/j.cell.2022.05.013

17. Norman TM et al. "Exploring genetic interaction manifolds constructed from rich single-cell phenotypes." Science 365, 786-793 (2019). DOI: 10.1126/science.aax4438

18. Roohani Y, Huang K, Leskovec J. "Predicting transcriptional outcomes of novel multigene perturbations with GEARS." Nature Biotechnology 42, 927-935 (2023). DOI: 10.1038/s41587-023-01905-6

19. Lotfollahi M, Wolf FA, Theis FJ. "CPA: Compositional perturbation autoencoder." Nature Methods (2023).

20. Cui H et al. "scGPT: toward building a foundation model for single-cell multi-omics using generative AI." Nature Methods (2024). DOI: 10.1038/s41592-024-02201-0

21. Tahoe-100M: A Giga-Scale Single-Cell Perturbation Atlas for Context-Dependent Gene Function and Cellular Modeling. bioRxiv (2025). DOI: 10.1101/2025.02.20.639398

22. Virtual Cell Challenge 2025 Wrap-Up: Winners and Reflections. Arc Institute (2025). https://arcinstitute.org/news/virtual-cell-challenge-2025-wrap-up

23. "Scouter predicts transcriptional responses to genetic perturbations with large language model embeddings." Nature Computational Science (2026). DOI: 10.1038/s43588-025-00912-8

24. "PerturbNet predicts single-cell responses to unseen chemical and genetic perturbations." Nature Computational Biology (2025). PMC: 12322087

25. CZI. "Accelerating AI in Biology With Community-Driven Benchmarks." https://chanzuckerberg.com/blog/ai-biology-community-benchmarks/

26. PerturBench: Benchmarking Machine Learning Models for Cellular Perturbation Analysis. arXiv (2024). 2408.10609

27. "The decomposition of perturbation modeling." Nature Computational Science (2024). DOI: 10.1038/s43588-024-00706-4

28. "Interpolating perturbations across contexts." Nature Computational Science (2025). DOI: 10.1038/s43588-025-00830-9
