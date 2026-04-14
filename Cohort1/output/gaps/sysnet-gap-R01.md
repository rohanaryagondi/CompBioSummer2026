---
agent: sysnet
round: 1
date: 2026-04-14
type: gap-report
---

# Systems & Network Biology Expert -- Round 1 Gap Reports

## Reporting Agent

Dr. Systems & Network Biology Expert (sysnet), Maverick Track (7 years post-PhD).
Focus: biological networks, perturbation biology, multi-scale integration, virtual
cell models, GRN inference, cell-cell communication, and spatial systems biology.

---

# Gap 1: Context-Aware Cross-Cellular-State Perturbation Response Prediction

---
gap_id: context-perturb-transfer
---

## Gap Description

### What Is Missing

Current perturbation prediction models fail to generalize perturbation effects across
different cellular contexts (cell types, activation states, tissue microenvironments,
donor backgrounds). The field can predict what happens when you knock out gene X in
K562 cells given training data from K562 cells, but cannot reliably predict what happens
when you knock out gene X in a T cell, hepatocyte, or neuron if no perturbation data
exists for that context. This is the single largest failure mode standing between current
models and a true "virtual cell."

### Current State of the Art

The field of perturbation prediction has undergone a sobering reassessment followed by
a dramatic scaling race in 2025-2026. The story unfolds in three phases:

**Phase 1: The Benchmark Reckoning (2025)**

A landmark Nature Methods paper by Kernfeld et al. (2025) demonstrated that **none of
the deep learning models tested -- including GEARS, CPA, scGPT, scFoundation, scBERT,
Geneformer, and UCE -- consistently outperformed simple linear baselines** (mean predictor
or linear model with PCA embeddings) on the Replogle et al. and Norman et al. datasets.
Specifically:

- GenePert achieved an average PCC of 0.775, outperforming GEARS (0.692) and
  scGPT (0.661) -- but GenePert is itself a linear model (Kernfeld et al., Nature
  Methods, 2025).
- On the Norman et al. double-perturbation dataset (225 conditions, 19,264 genes),
  all deep learning approaches showed "substantially higher" error than the simple
  additive baseline for combinatorial perturbations.
- scGPT, UCE, and scBERT predictions "did not vary across perturbations," while GEARS
  and scFoundation "varied considerably less than the ground truth."

The Systema framework (Nature Biotechnology, 2025) further showed that current methods
struggle to generalize beyond systematic variation, with biases leading to overestimated
performance across 10 datasets spanning 3 technologies and 5 cell lines.

The scPerturBench evaluation (Nature Methods, 2025) of 27 methods across 29 datasets
using 6 metrics confirmed that **no single method reliably generalizes across cellular
contexts**. Their proposed solution -- cellular context embedding -- improved
generalizability but did not solve the fundamental problem.

**Phase 2: The Scaling Race (Late 2025 - Early 2026)**

Multiple groups responded with massive-scale models:

- **STATE** (Arc Institute, 2025): Trained on >100 million perturbed cells across 70
  cell contexts plus 167 million observational cells. STATE improved discrimination of
  perturbation effects by over 50% and identified true differentially expressed genes
  with 2x accuracy compared to existing models. However, STATE's gains were
  context-dependent.
- **PULSAR** (Stanford, bioRxiv, November 2025): Multi-scale foundation model trained
  on 36.2 million cells from 6,807 donors, explicitly hierarchical (molecular ->
  cellular -> multicellular).
- **SCALE** (NVIDIA/CZI, bioRxiv, March 2026): Scalable Conditional Atlas-Level Endpoint
  transport model using a LLaMA-style DeepSets encoder with conditional flow-matching.
  On Tahoe-100M, SCALE improved PDCorr by 12.02% and DE Overlap by 10.66% over STATE.
  Achieved 12.51x speedup on pretrain over the prior SOTA pipeline.

**Phase 3: The Context Awakening (Early 2026)**

A critical position paper, "Virtual Cells Need Context, Not Just Scale" (bioRxiv,
February 2026), argued that **scaling alone is insufficient** because:

1. The transcriptome is a lossy projection of cell state
2. The inference problem is confounded by unobserved biological context
3. Current models demonstrably collapse to context-averaged predictions

A 22-million-cell T cell dataset empirically showed that **context diversity, not cell
count, drives cross-context generalization**.

This catalyzed context-aware models:

- **X-Cell** (Xaira Therapeutics, bioRxiv, March 2026): A diffusion language model
  trained on X-Atlas/Pisces (25.6 million perturbed cells across 16 diverse contexts).
  X-Cell outperforms existing SOTA by up to five-fold on Pearson Delta. Scaled to 4.9
  billion parameters (X-Cell-Ultra), the largest causal perturbation model to date.
  Claims zero-shot generalization to unseen iPSC-derived melanocyte progenitors and
  primary human CD4+ T cells. **Perturbation prediction follows power-law scaling with
  an exponent matching LLMs.**
- **AlphaCell** (bioRxiv, March 2026): A "World Model" using optimal transport
  conditional flow matching, trained on 90 million perturbed profiles (80M from
  Tahoe-100M, ~10M from pharmacological screens). Claims zero-shot prediction in
  unseen cellular contexts.
- **TRAILBLAZER** (bioRxiv, March 2026): Models tissues as coordinated multicellular
  systems with near-linear scaling. Claims zero-shot multicellular prediction.
- **pertTF** (bioRxiv, March 2026): Context-aware transformer trained on 30 gene
  knockouts across 14 cell types during pancreatic development. Outperforms prior methods
  on cross-context prediction and infers perturbation-induced shifts in cell identity
  and population composition. Demonstrates transfer learning to primary human islets.
- **AetherCell** (bioRxiv, March 2026): Generative engine achieving translational
  prediction from cell lines to 3D organoids and patient-derived systems.

**Despite this progress, the fundamental gap persists**: No method has demonstrated
robust, rigorous cross-context generalization on a held-out benchmark with truly unseen
cell types, unseen perturbation targets, AND unseen biological conditions simultaneously.
X-Cell's zero-shot claims are promising but untested by independent evaluation. The
field still lacks:

1. A standardized cross-context benchmark (existing benchmarks allow data leakage
   between contexts)
2. Rigorous separation of interpolation vs. extrapolation performance
3. Understanding of when and why context transfer fails
4. Principled methods for identifying which contexts are "close enough" for transfer

### Evidence the Gap Exists

1. **Kernfeld et al., 2025 (Nature Methods)**: Deep learning models do not outperform
   linear baselines, suggesting fundamental representation failures.
2. **"Virtual Cells Need Context, Not Just Scale" (bioRxiv, 2026)**: Argues that
   implicit context inference from transcriptomes is fundamentally flawed.
3. **scPerturBench (Nature Methods, 2025)**: 27 methods, 29 datasets, no consistent
   winner for cross-context prediction.
4. **PerturBench (NeurIPS 2024)**: Evaluation across 5 datasets revealed mode collapse
   in published models.
5. **Tahoe-100M (bioRxiv, 2025)**: 100M cells across 50 cell lines demonstrates the
   data exists, but no model has solved the generalization problem.
6. **X-Cell (March 2026)**: Claims 5x improvement but no independent evaluation yet;
   benchmark design still allows systematic biases per Systema.

## Why This Gap Matters

### Scientific Importance

Understanding how the same genetic perturbation produces different effects in different
cellular contexts is fundamental to understanding gene function. If we cannot predict
that knocking out TP53 has different consequences in a stem cell versus a terminally
differentiated neuron, we do not truly understand TP53. This gap strikes at the heart
of the genotype-to-phenotype problem.

### Practical Impact

Drug target validation depends on predicting perturbation effects across tissues. A
drug that inhibits target X in hepatocytes may have dramatically different effects in
cardiomyocytes. Without cross-context prediction, computational drug safety assessment
is unreliable. AetherCell's demonstration of cell-line-to-organoid transfer for drug
repurposing (teriflunomide for dry eye disease) hints at the practical potential.

### Publication Potential

A method that demonstrably outperforms baselines on rigorous cross-context benchmarks --
or, critically, a comprehensive benchmark framework that exposes the limitations of
current approaches including X-Cell and SCALE -- would be immediately publishable in
Nature Computational Science. The bar has been clearly set by Kernfeld et al. -- beat
the linear baseline on truly held-out contexts, with rigorous Systema-style evaluation.

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

Two complementary paths:

**Path A: Rigorous Cross-Context Benchmark.** Build the definitive evaluation framework
that (a) systematically varies the degree of context novelty (seen cell type/unseen
perturbation, unseen cell type/seen perturbation, both unseen), (b) accounts for
systematic variation per Systema, (c) includes difficulty stratification, and (d)
provides community-accessible leaderboards. This alone would be a landmark contribution.

**Path B: Explicit Causal Context Conditioning.** Develop a framework that explicitly
conditions on observed biological context (cell type identity, chromatin accessibility
state, signaling environment from Multiome data) rather than relying on models to infer
context from expression alone. Key innovations:

- Conditioning perturbation prediction on cell-type-specific chromatin accessibility
  (from Multiome Perturb-seq data)
- Using in-context learning where sets of cells serve as prompts defining biological
  context at inference time (inspired by Stack, bioRxiv 2026)
- Causal representation learning to separate context-invariant gene function from
  context-dependent regulatory wiring
- Principled quantification of "context distance" -- predicting WHEN transfer will fail

### Required Data

- **X-Atlas/Pisces** (Xaira, 2026): 25.6 million perturbed cells across 16 diverse
  contexts. Largest genome-wide CRISPRi compendium.
- **Tahoe-100M** (Arc Institute, 2025): 100M cells, 1,100 small molecules, 50
  cancer cell lines.
- **Replogle et al. (Cell, 2022)**: Genome-scale Perturb-seq in K562 (~2.5M cells,
  9,866 genes) and RPE1 cells.
- **VIPerturb-seq data** (bioRxiv, 2026): Genome-wide Perturb-seq with 50-fold
  throughput improvement and 65% more detected genes per cell.
- **scPerturb** (Nature Methods, 2024): 44 harmonized datasets from 25 publications.
- **Multiome Perturb-seq** (Cell Systems, 2025): Joint RNA + ATAC perturbation data.

### Required Compute

- Benchmark construction and evaluation of existing models: ~200 H200 GPU-hours.
- Training context-conditioned models on 25M+ cells: 500-1,500 H200 GPU-hours.
- Hyperparameter search and ablation studies: 200-500 GPU-hours.
- Total estimated: 900-2,200 H200 GPU-hours (2-4 weeks on 10-GPU allocation).

### Required Methods

- Transformer-based perturbation models (building on X-Cell, STATE architectures)
- Causal representation learning (disentanglement of context from perturbation effect)
- Conditional flow matching / optimal transport for distribution alignment
- Rigorous evaluation framework following scPerturBench + Systema protocols
- Context distance metrics for transfer feasibility prediction

## Feasibility Assessment

### Technical Feasibility: High
All data is publicly available. The computational methods are well-established.
The key innovation is either benchmark design (Path A) or architectural (explicit
context conditioning, Path B), not requiring novel algorithms.

### Timeline Feasibility: High
With existing data and frameworks (scPerturBench, Systema), a focused team could
develop, evaluate, and publish within 3-4 months.

### Wet Lab Independence: High
Entirely computational. All validation uses existing published data.

## Competitive Landscape

### Who Else Might Fill This Gap
- **Xaira Therapeutics**: X-Cell developers with 4.9B parameter model and X-Atlas data.
  Best-resourced competitor.
- **Arc Institute** (Hie Lab): STATE developers + Tahoe-100M data.
- **NVIDIA/CZI**: SCALE developers with BioNeMo infrastructure.
- **AetherCell team**: Already demonstrating translational prediction.
- **Theis Lab (Helmholtz)**: Systema framework developers, positioned for rigorous
  benchmarking.

### Risk of Being Scooped
**HIGH**. This is the hottest area in computational biology in 2026. Multiple well-funded
groups are racing. However, the specific gap -- rigorous demonstration of cross-context
generalization with proper controls for systematic bias -- has NOT been filled by any of
these papers. Most show results on cherry-picked contexts, not systematic evaluation.

### Differentiation
Two differentiation strategies: (1) **Be the benchmark** -- the group that defines
rigorous cross-context evaluation will be cited by everyone. Systema set the precedent
at the single-context level; extending to cross-context would be analogous. (2) **Focus
on context representations** -- not scaling, but understanding what makes contexts
transferable. The "Virtual Cells Need Context" paper provides theoretical grounding.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 6 | Very active area, but rigorous cross-context benchmarking is novel |
| Scientific impact | 9 | Fundamental to virtual cell vision and gene function understanding |
| Feasibility (computational only) | 9 | All data public, established frameworks available |
| Timeline (summer 2026) | 8 | Benchmark-focused approach very achievable |
| Publication potential (Nat Comp Sci) | 8 | Directly addresses Nature Methods critique papers |
| **Overall** | **8.0** | High-impact gap with excellent feasibility; competition is fierce |

## References

1. Kernfeld, E.M. et al. (2025). Deep-learning-based gene perturbation effect
   prediction does not yet outperform simple linear baselines. *Nature Methods*.
   https://www.nature.com/articles/s41592-025-02772-6
2. Ji, Y. et al. (2025). Systema: a framework for evaluating genetic perturbation
   response prediction beyond systematic variation. *Nature Biotechnology*.
   https://www.nature.com/articles/s41587-025-02777-8
3. Wang, B. et al. (2026). Virtual Cells Need Context, Not Just Scale. *bioRxiv*
   10.64898/2026.02.04.703804.
4. Hie, B. et al. (2025). Predicting cellular responses to perturbation across
   diverse contexts with State. *bioRxiv* 10.1101/2025.06.26.661135.
5. X-Cell Team (2026). X-Cell: Scaling Causal Perturbation Prediction Across Diverse
   Cellular Contexts via Diffusion Language Models. *bioRxiv*
   10.64898/2026.03.18.712807.
6. AlphaCell Team (2026). Towards building a World Model to simulate
   perturbation-induced cellular dynamics by AlphaCell. *bioRxiv*
   10.64898/2026.03.02.709176.
7. TRAILBLAZER Team (2026). TRAILBLAZER: generative multicellular perturbation model
   of biology. *bioRxiv* 10.64898/2026.03.14.711710.
8. pertTF Team (2026). pertTF: context-aware AI modeling for genome-scale and
   cross-system perturbation prediction. *bioRxiv* 10.64898/2026.03.12.711379.
9. SCALE Team (2026). SCALE: Scalable Conditional Atlas-Level Endpoint transport for
   virtual cell perturbation prediction. *bioRxiv* 10.64898/2026.03.17.712536.
10. Pang, K. et al. (2025). PULSAR: a Foundation Model for Multi-scale and
    Multicellular Biology. *bioRxiv* 10.1101/2025.11.24.685470.
11. Replogle, J. et al. (2022). Mapping information-rich genotype-phenotype landscapes
    with genome-scale Perturb-seq. *Cell* 185(16):2559-2575.
12. Tahoe-100M (2025). A Giga-Scale Single-Cell Perturbation Atlas for
    Context-Dependent Gene Function and Cellular Modeling. *bioRxiv*
    10.1101/2025.02.20.639398.
13. X-Atlas/Pisces Team (2026). X-Atlas/Pisces: 25.6 Million Perturbed Cells Across
    16 Diverse Contexts. Xaira Therapeutics.
14. VIPerturb-seq Team (2026). Genome-wide single-cell perturbation screens with
    VIPerturb-seq. *bioRxiv* 10.64898/2026.02.12.705613.
15. AetherCell Team (2026). AetherCell: A generative engine for virtual cell
    perturbation and in vivo drug discovery. *bioRxiv* 10.64898/2026.03.13.710968.
16. Zhang, Y. et al. (2025). Benchmarking algorithms for generalizable single-cell
    perturbation response prediction. *Nature Methods*.
    https://www.nature.com/articles/s41592-025-02980-0
17. Hetzel, L. et al. (2024). PerturBench: Benchmarking Machine Learning Models for
    Cellular Perturbation Analysis. *NeurIPS 2024*.
18. Peidli, S. et al. (2024). scPerturb: harmonized single-cell perturbation data.
    *Nature Methods* 21:531-540.
19. Rood, J.E., Hupalowska, A., & Regev, A. (2024). Toward a foundation model of
    causal cell and tissue biology with a Perturbation Cell and Tissue Atlas. *Cell*
    187:4520-4545.

---

# Gap 2: Scalable Causal Gene Regulatory Network Inference from Perturbation Data

---
gap_id: causal-grn-scale
---

## Gap Description

### What Is Missing

Despite the availability of genome-scale perturbation data (Replogle et al., 2022:
~10,000 gene knockdowns; X-Atlas/Pisces: 25.6M cells across 16 contexts; Tahoe-100M:
100M cells across 50 cell lines), the field **cannot reliably infer genome-scale causal
gene regulatory networks**. Current GRN inference methods either: (a) scale to only
hundreds of genes with causal guarantees, (b) scale to thousands of genes but produce
correlation-based networks without causal interpretation, or (c) produce networks whose
predictive accuracy degrades severely on held-out perturbation data. There is no method
that combines genome-scale causal inference with perturbation-validated predictive
accuracy.

### Current State of the Art

**Correlation-based GRN inference** methods (GENIE3, SCENIC, SCENIC+) can scale to
genome-wide gene sets but produce undirected or weakly directed networks that conflate
correlation with causation. The BEELINE benchmark (Pratapa et al., Nature Methods, 2020)
evaluated 12 GRN inference algorithms and found that no method consistently outperformed
others across datasets, with GENIE3 and PIDC among the top performers.

The **geneRNIB** living benchmark (bioRxiv, 2025) systematically assessed 10 GRN
inference methods across 5 diverse datasets and found that **simple models with fewer
assumptions often outperformed more complex pipelines**, and gene expression-based
correlation algorithms yielded better results than approaches incorporating prior
datasets or pre-trained on large datasets. This mirrors the perturbation prediction
paradox (Kernfeld et al.) -- complexity does not reliably beat simplicity.

**Causal GRN inference** methods are beginning to leverage perturbation data:
- **inspre** (Fromer et al., Nature Communications, 2025): Applied inverse sparse
  regression to 788 genes from genome-wide Perturb-seq, discovering a network with
  small-world and scale-free properties. But 788 genes is far from genome-scale
  (~20,000 protein-coding genes).
- **ADAPRE** (bioRxiv, February 2026): Treats CRISPR interventions as instrumental
  variables within a Poisson-lognormal model. Adaptively accounts for variable
  perturbation strength, recovers potentially cyclic structures, and outperforms
  existing methods. Applied to genome-wide K562 Perturb-seq data and reconstructed
  networks enriched for known biological interactions and leukemia-associated
  subnetworks. Key advance: handles cyclic networks (unlike DAG-constrained methods)
  and variable knockdown efficiency. But causal guarantees depend on strong assumptions
  about perturbation specificity.
- **CausalGRN** (bioRxiv, December 2025): A scalable framework for causal GRN inference
  from single-cell CRISPR screens. Not yet validated at true genome scale on held-out
  data.

**GNN/Transformer approaches** show promise on benchmark datasets:
- **GRNFormer** (bioRxiv, 2025): Graph transformer achieving 0.90-0.98 AUROC on
  benchmark datasets. However, these benchmarks use curated ground-truth networks of
  modest size, not genome-scale perturbation validation.
- **scGREAT** (2024): Transformer-based model with 91.30% AUROC across 7 benchmarks.

**Dynamic GRN inference** is a newer frontier:
- **TRIGON** (bioRxiv, 2025): Transformer-based temporal causality model that improved
  accuracy by 204% over previous methods on developmental datasets.
- **GRIT** (Bioinformatics, 2025): Differential equation model with optimal transport
  for causal network inference from time-series single-cell data.

**CausalBench** (Communications Biology, 2025): The largest benchmark for network
inference from single-cell perturbation data. Uses interventional data from perturbational
scRNA-seq experiments (200,000+ interventional datapoints) to assess predicted edges.
Critical finding: **even simple methods (Mean Difference) outperform sophisticated GRN
inference algorithms on biological evaluation metrics**, indicating that existing methods
do not effectively leverage interventional data.

A separate comparison of interventional causal structure learning algorithms (bioRxiv,
December 2025) confirmed that newer methods show improved utilization of interventional
information compared to older approaches, but the gap between theoretical identifiability
results and practical performance remains large.

The fundamental problem is the **evaluation gap**: AUROC on curated benchmark networks
does not validate that inferred networks can predict responses to novel perturbations.
No published GRN inference method has demonstrated that the inferred network can be used
to predict the transcriptomic response to a held-out knockdown better than a direct
regression model. This means GRN inference has not proven its value as an intermediate
representation.

### Evidence the Gap Exists

1. **geneRNIB (bioRxiv, 2025)**: Simple methods outperform complex GRN inference
   pipelines, even with perturbation data available.
2. **CausalBench (Communications Biology, 2025)**: Mean Difference outperforms
   sophisticated GRN methods on biological evaluation metrics despite having 200K+
   interventional observations available.
3. **BEELINE (Nature Methods, 2020)**: No consistent winner among 12 methods.
4. **inspre (Nat Comm, 2025)**: Causal inference limited to 788 genes, not genome-scale.
5. **ADAPRE (bioRxiv, 2026)**: Genome-scale but relies on strong assumptions; validation
   is enrichment-based, not predictive.
6. **Kernfeld et al. (Nature Methods, 2025)**: GRN-based perturbation prediction does
   not outperform linear baselines -- implying current GRNs add no predictive value.
7. **Nature Reviews Genetics (2026)**: "Gene regulatory networks: from correlative
   models to causal explanations" -- title itself acknowledges the gap.
8. **Comparison of Interventional Causal Structure Learning (bioRxiv, 2025)**:
   Theoretical identifiability far exceeds practical performance.

## Why This Gap Matters

### Scientific Importance

Understanding the causal wiring diagram of gene regulation is arguably the most
fundamental question in molecular biology. If we know the causal network, we can
predict the effect of any single or combinatorial perturbation. The availability of
genome-scale perturbation data (Replogle, X-Atlas/Pisces, Tahoe-100M) creates an
unprecedented opportunity to infer causal networks at scale -- but no method capitalizes
on this.

The Nature paper by Gazal et al. (2025), "Causal modelling of gene effects from
regulators to programs to traits," demonstrates the biological importance of causal
gene regulatory architecture by integrating genetic associations with Perturb-seq data
to trace effects from regulators through transcriptional programs to complex traits.
This shows the downstream applications are ready -- the bottleneck is the GRN inference
itself.

### Practical Impact

Causal GRNs are essential for: (1) identifying therapeutic targets (which genes
causally drive disease phenotypes), (2) predicting drug combinations (which pathway
interactions produce synergy), (3) understanding drug resistance (which regulatory
rewiring enables escape), (4) cell engineering (which transcription factors to
manipulate for reprogramming). PDGrapher (Nature Biomedical Engineering, 2025) showed
that causally-inspired networks can predict combinatorial therapeutic perturbations 25x
faster than scGen and 100x faster than CellOT, but requires the causal network as input.

### Publication Potential

A method that infers genome-scale causal GRNs validated by held-out perturbation
prediction would be a landmark contribution. The availability of Perturb-seq data
for both training and validation creates a natural experimental design. Target venue:
Nature Computational Science or Nature Methods.

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

Develop a scalable causal discovery algorithm that:
1. Uses genome-scale Perturb-seq data as interventional observations (Replogle K562:
   9,866 knockdowns; X-Atlas/Pisces: genome-wide across 16 contexts)
2. Combines structural causal model theory with modern deep learning scalability
3. Validates inferred networks by predicting held-out perturbation responses (not just
   enrichment for known pathways)
4. Handles cyclic networks (following ADAPRE's approach of relaxing DAG constraints)
5. Produces confidence-calibrated edges (not just binary presence/absence)
6. Compares inferred-GRN-based prediction against direct perturbation prediction methods
   to demonstrate the added value of the intermediate GRN representation

Key innovation: Use the perturbation data itself as the ground truth -- the inferred
network should predict the transcriptomic response to a held-out knockdown. If a GRN
cannot be used for better perturbation prediction than direct models, it has not proven
its value as a scientific representation.

### Required Data

- **Replogle et al. (Cell, 2022)**: K562 genome-wide Perturb-seq (9,866 gene
  knockdowns, ~2.5M cells). Split into training (80%) and held-out validation (20%).
- **X-Atlas/Pisces** (Xaira, 2026): 25.6M cells across 16 contexts for cross-context
  GRN validation.
- **Tahoe-100M** (2025): 100M cells across 50 cell lines for multi-context analysis.
- **scPerturb** (Nature Methods, 2024): 44 harmonized datasets for external validation.
- **Known pathway databases**: KEGG, Reactome, STRING for enrichment analysis.
- **CausalBench** (2025): Existing benchmark for comparison.

### Required Compute

- Causal discovery on 10,000+ node networks with millions of interventional
  observations: highly compute-intensive.
- GPU-accelerated structure learning: ~500-2,000 H200 GPU-hours.
- Perturbation prediction from inferred networks: ~100 GPU-hours.
- Cross-context GRN comparison: ~200 GPU-hours.
- Total estimated: 800-2,500 H200 GPU-hours (2-5 weeks on 10 GPUs).

### Required Methods

- Structural causal models with interventional data (building on ADAPRE's instrumental
  variable approach)
- GPU-accelerated continuous optimization for structure learning (allowing cycles)
- GNN/transformer for parameterizing conditional distributions
- Perturbation prediction as the primary validation metric (not AUROC on curated networks)
- Comparison with inspre, ADAPRE, CausalGRN, and direct prediction baselines (GEARS,
  X-Cell, STATE)

## Feasibility Assessment

### Technical Feasibility: Medium
Causal discovery at genome scale is computationally demanding and theoretically
challenging. The cyclic nature of real GRNs complicates DAG-based methods. However,
ADAPRE has shown that instrumental variable approaches can handle genome scale, and the
availability of rich interventional data fundamentally changes identifiability.

### Timeline Feasibility: Medium
A focused contribution on a specific aspect (e.g., validating GRN inference methods by
their perturbation prediction performance, or scaling ADAPRE to multi-context data) is
feasible. A complete genome-scale causal GRN with full validation may require longer.

### Wet Lab Independence: High
Entirely computational. All validation uses published Perturb-seq data.

## Competitive Landscape

### Who Else Might Fill This Gap
- **Fromer & Regev (Broad/CZI)**: inspre developers, working on scaling causal
  inference.
- **Uhler Lab (MIT)**: Leading causal discovery methods for biology.
- **ADAPRE team**: Already achieving genome-scale with instrumental variables.
- **Leskovec Lab (Stanford)**: CausalBench developers + PULSAR + GNN expertise.
- **CausalGRN team**: Actively developing scalable causal GRN tools.
- **Gazal et al. (Nature, 2025)**: Demonstrated regulator-to-program-to-trait causal
  modeling.

### Risk of Being Scooped
**MEDIUM-HIGH**. The theoretical foundations exist, the data exists, but no one has
demonstrated that inferred GRNs improve perturbation prediction over direct methods.
ADAPRE is closest but validated by enrichment, not prediction. The "does GRN inference
add value?" question is the key open question.

### Differentiation
Focus on **perturbation prediction as the validation metric** for GRN inference. The
question "does knowing the causal network help predict perturbation responses better than
not knowing it?" has not been rigorously tested. This reframes GRN inference from a
descriptive exercise to a predictive one.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 8 | Genome-scale causal GRN validated by prediction is unsolved |
| Scientific impact | 9 | Fundamental to understanding gene regulation |
| Feasibility (computational only) | 6 | Computationally challenging, requires algorithmic innovation |
| Timeline (summer 2026) | 6 | Focused contribution feasible, complete solution harder |
| Publication potential (Nat Comp Sci) | 9 | Would be a landmark if achieved |
| **Overall** | **7.6** | Very high impact, moderate-high feasibility challenge |

## References

1. Pratapa, A. et al. (2020). Benchmarking algorithms for gene regulatory network
   inference from single-cell transcriptomic data. *Nature Methods* 17:147-154.
2. Fromer, M. et al. (2025). Large-scale causal discovery using interventional data
   sheds light on gene network structure in K562 cells. *Nature Communications*.
3. ADAPRE Team (2026). Causal gene regulatory network inference from Perturb-seq via
   adaptive instrumental variable modeling. *bioRxiv* 10.64898/2026.02.18.706642.
4. CausalGRN Team (2025). CausalGRN: deciphering causal gene regulatory networks from
   single-cell CRISPR screens. *bioRxiv* 10.64898/2025.12.30.692369.
5. geneRNIB Team (2025). geneRNIB: a living benchmark for gene regulatory network
   inference. *bioRxiv* 10.1101/2025.02.25.640181.
6. Hegde, A. & Cheng, J. (2025). GRNFormer: Accurate Gene Regulatory Network
   Inference Using Graph Transformer. *bioRxiv* 10.1101/2025.01.26.634966.
7. TRIGON Team (2025). Dissecting dynamic gene regulatory network using
   transformer-based temporal causality analysis. *bioRxiv*
   10.1101/2025.02.05.636766.
8. GRIT Team (2025). Dynamic gene regulatory network inference from single-cell data
   using optimal transport. *Bioinformatics* 41(8).
9. Nature Reviews Genetics (2026). Gene regulatory networks: from correlative models
   to causal explanations.
10. Kernfeld, E.M. et al. (2025). Deep-learning-based gene perturbation effect
    prediction does not yet outperform simple linear baselines. *Nature Methods*.
11. CausalBench (2025). A large-scale benchmark for network inference from single-cell
    perturbation data. *Communications Biology*.
    https://www.nature.com/articles/s42003-025-07764-y
12. Replogle, J. et al. (2022). Mapping information-rich genotype-phenotype landscapes
    with genome-scale Perturb-seq. *Cell* 185(16):2559-2575.
13. Gazal, S. et al. (2025). Causal modelling of gene effects from regulators to
    programs to traits. *Nature*. https://www.nature.com/articles/s41586-025-09866-3
14. PDGrapher Team (2025). Combinatorial prediction of therapeutic perturbations using
    causally inspired neural networks. *Nature Biomedical Engineering*.
    https://www.nature.com/articles/s41551-025-01481-x
15. Comparison of Interventional Causal Structure Learning Algorithms (2025). *bioRxiv*
    10.64898/2025.12.05.692565.
16. X-Atlas/Pisces Team (2026). X-Cell: Scaling Causal Perturbation Prediction.
    *bioRxiv* 10.64898/2026.03.18.712807.

---

# Gap 3: Temporal Dynamics of Perturbation Responses -- Beyond Static Snapshots

---
gap_id: temporal-perturb-dynamics
---

## Gap Description

### What Is Missing

Almost all perturbation prediction methods treat cellular responses as **static
endpoints** -- predicting the transcriptomic state at a single post-perturbation
timepoint. In reality, perturbation responses are **dynamic processes** that unfold
over hours to days, involving cascades of immediate early genes, secondary response
genes, adaptive rewiring, and potentially cell fate transitions or cell death. The
field cannot predict the temporal trajectory of a perturbation response -- the order
and timing of transcriptomic changes, transient states, and ultimate steady-state
outcomes.

### Current State of the Art

**Static perturbation prediction** methods (GEARS, CPA, scGPT, STATE, X-Cell, SCALE,
AlphaCell) predict a single post-perturbation expression profile, typically measured
at a fixed timepoint (e.g., 7 days post-CRISPRi in Replogle et al.). These methods
entirely ignore temporal dynamics.

**Trajectory-aware methods** are just emerging:
- **PerturbGen** (bioRxiv, March 2026): A generative foundation model trained on
  >100 million single-cell transcriptomes that predicts perturbation responses along
  cellular trajectories. It addresses how genetic perturbation at a source state shapes
  downstream states across time. This is the first model explicitly designed for
  trajectory-level perturbation prediction, but it infers pseudo-temporal trajectories
  from cross-sectional data rather than using true time-series measurements.
- **AlphaCell** (bioRxiv, March 2026): Uses optimal transport conditional flow matching
  to model perturbations as continuous deterministic vector fields, which implicitly
  captures dynamics. However, it was not explicitly validated on true temporal data.
- **DynPerturb** (bioRxiv, September 2025): Explicitly models dynamic perturbation
  for spatiotemporal single-cell systems. One of the first methods to jointly address
  temporal and spatial perturbation dynamics, though limited by available validation data.

**Time-series approaches for unperturbed dynamics**:
- **RNA velocity** (scVelo, La Manno et al.): Infers instantaneous rate of change
  from unspliced/spliced ratios. Not designed for perturbation responses.
- **Waddington-OT** (Schiebinger et al., Cell, 2019): Uses optimal transport to
  connect time-resolved single-cell snapshots. Not designed for perturbation prediction.
- **sc4D** (bioRxiv, November 2025): Spatio-temporal single-cell transcriptomics
  analysis for 4D modeling.
- **CellDrift** (2023): Explores temporal cell group profiles shaped by longitudinal
  perturbations using GLMs with functional data analysis.
- **MEFISTO** (2022): Time-aware multi-view decomposition.

**Dynamic GRN methods** capture some temporal information:
- **TRIGON** (bioRxiv, 2025): Infers dynamic GRNs at varying time resolutions,
  improving accuracy by 204% over previous methods on developmental datasets.
- **GRIT** (Bioinformatics, 2025): Fits differential equation models for network
  inference using optimal transport, inherently modeling dynamics.

**Drug-response temporal modeling** is a related area:
- **PertDiT** (Quantitative Biology, 2026): Multi-condition diffusion transformer
  for predicting drug-perturbed transcriptional responses, but focuses on endpoint
  prediction conditioned on drug information, not temporal trajectories.
- **XPert** (Nature Machine Intelligence, 2025): Biologically informed dual-branch
  transformer for drug-induced perturbation responses. Again endpoint, not temporal.

**The critical data gap**: Most large-scale perturbation datasets (Replogle, Tahoe-100M,
X-Atlas/Pisces) measure responses at **a single timepoint**. True time-series
perturbation data at single-cell resolution is extremely limited. The Adamson et al.
dataset includes early timepoints, and some CROP-seq experiments include multiple
timepoints, but there is no genome-scale time-resolved perturbation atlas.

**Emerging data opportunities**:
- X-Atlas/Orion (bioRxiv, 2025): Dose-dependent genome-wide Perturb-seq data. Dose
  can serve as a surrogate for temporal progression.
- Perturb-seq of pluripotency regulators (bioRxiv, August 2025): Reveals dose-dependent
  responses controlling self-renewal and differentiation -- dose as temporal proxy.
- Experimentally calibrated multiscale models (npj Systems Biology, 2026): Schedule-
  dependent drug combination predictions suggest temporal modeling adds value.

### Evidence the Gap Exists

1. **PerturbGen (bioRxiv, 2026)**: Authors explicitly state "recent computational
   approaches can predict single-cell perturbation responses in silico, but cannot
   predict responses across dynamic cell trajectories."
2. **Replogle et al. (Cell, 2022)**: Genome-scale Perturb-seq measured at day 6-8 only.
   No temporal resolution.
3. **Tahoe-100M (2025)**: 100M cells but at fixed timepoints per condition.
4. **X-Atlas/Pisces (2026)**: 25.6M cells, genome-wide, but single timepoints.
5. **Mini-review on perturbation modelling (Computational and Structural Biotechnology
   Journal, 2024)**: Identifies "trajectory-aware models needed for perturbation
   kinetics" as a major gap.
6. **No NeurIPS/ICML/Nature competition** has yet benchmarked temporal perturbation
   prediction.
7. **DynPerturb (bioRxiv, 2025)**: Existence of a new method for this confirms the
   gap; the method is early-stage and limited in validation.

## Why This Gap Matters

### Scientific Importance

The temporal dynamics of perturbation responses encode critical biological information:
- **Immediate vs. adaptive responses**: Are genes directly regulated by the knocked-out
  TF (fast response) or indirectly affected through network cascades (slow response)?
  This directly reveals GRN hierarchy.
- **Transient states**: Some perturbations induce transient stress responses that
  resolve to a new steady state. These transient states may reveal therapeutic
  vulnerabilities (e.g., a transient apoptotic window).
- **Cell fate decisions**: Perturbations that push cells toward different fates
  (differentiation, death, quiescence) do so through temporal cascading of regulatory
  events.
- **Mechanism of action**: The temporal signature of a perturbation response is
  informative about the mechanism (direct target inhibition vs. signaling cascade
  disruption vs. metabolic rewiring).

### Practical Impact

Drug response is inherently temporal. Understanding the kinetics of cellular response
to a compound (rapid transcriptomic change followed by adaptation) is critical for
dosing schedules, combination timing, and resistance prediction. Schedule-dependent drug
combination effects (npj Systems Biology, 2026) demonstrate that timing matters.

### Publication Potential

A computational framework that predicts temporal perturbation dynamics -- validated
on the limited time-resolved data available and using dose-response as temporal
surrogate -- would open a new subfield. High publication potential in Nature
Computational Science.

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

Develop a neural ODE/SDE framework that models perturbation responses as continuous
dynamical systems in gene expression space. Key components:

1. **Learn a base dynamical system** from unperturbed time-series data (RNA velocity,
   developmental trajectories)
2. **Learn perturbation-specific modifications** to the dynamics (how knockdown of
   gene X alters the vector field)
3. **Use dose-response data as temporal proxy**: X-Atlas/Orion provides dose-dependent
   perturbation responses; dose titration reveals the trajectory of increasing
   perturbation effect
4. **Predict the full temporal trajectory** of perturbation response, not just the
   endpoint
5. **Validate on available time-resolved data** (Adamson, CROP-seq time courses) and
   dose-response data
6. **Connect to GRN inference**: The temporal order of gene response reveals causal
   hierarchy in the GRN

### Required Data

- **Replogle et al. (Cell, 2022)**: Endpoint perturbation data for K562 and RPE1.
- **X-Atlas/Orion (bioRxiv, 2025)**: Dose-dependent genome-wide Perturb-seq data.
  Dose titration as temporal surrogate.
- **Adamson et al. (Cell, 2016)**: Time-resolved CRISPRi Perturb-seq in K562 cells.
- **CROP-seq time courses**: Multiple studies with 2-4 timepoints post-perturbation.
- **RNA velocity data**: Infer instantaneous dynamics from single timepoint data.
- **Perturb-seq pluripotency data (bioRxiv, 2025)**: Dose-dependent perturbation.

### Required Compute

- Neural ODE/SDE training on large single-cell datasets: 200-800 H200 GPU-hours.
- Inference on trajectory prediction: ~50 GPU-hours.
- Evaluation and comparison: ~50 GPU-hours.
- Total estimated: 300-900 H200 GPU-hours.

### Required Methods

- Neural ODEs/SDEs (Chen et al., 2018; latent SDEs)
- Optimal transport for matching distributions across timepoints
- RNA velocity integration for instantaneous dynamics
- Dose-response modeling as temporal proxy
- Transfer learning from static perturbation models (warm-start from STATE/X-Cell)
- Comparison with PerturbGen and DynPerturb baselines

## Feasibility Assessment

### Technical Feasibility: Medium
The main challenge is the scarcity of true time-resolved perturbation data. The creative
use of dose-response data as temporal surrogate (from X-Atlas/Orion) is a novel approach
that partially mitigates this. DynPerturb's existence shows the approach is technically
viable.

### Timeline Feasibility: Medium
A proof-of-concept on available time-resolved data with dose-as-time-proxy is feasible
in summer 2026. A comprehensive framework validated on true temporal data may require
additional data generation.

### Wet Lab Independence: High
Uses only published data. No wet lab needed.

## Competitive Landscape

### Who Else Might Fill This Gap
- **PerturbGen team**: Already tackling trajectory prediction but from cross-sectional
  data only.
- **AlphaCell team**: Vector field approach is inherently temporal.
- **DynPerturb team**: Explicitly addressing spatiotemporal perturbation.
- **Schiebinger Lab**: Waddington-OT expertise could extend to perturbation dynamics.
- **Chen Lab (neural ODE developers)**: Natural extension of methodology.

### Risk of Being Scooped
**MEDIUM**. PerturbGen and AlphaCell are moving in this direction, but neither has
validated on true temporal data. DynPerturb addresses this but is early-stage. The
gap between "pseudo-temporal trajectory inference" and "true temporal prediction" remains
open. The dose-as-time-proxy idea is largely unexplored.

### Differentiation
Focus on: (1) **validation with true time-resolved data** (not pseudo-time), (2)
**dose-response as temporal proxy** (novel contribution), and (3) **explicit temporal
predictions** (what genes change at 2h, 6h, 24h, 72h) rather than embedding in a
continuous latent trajectory.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 8 | True temporal perturbation prediction with dose-proxy is novel |
| Scientific impact | 8 | Opens new understanding of perturbation dynamics and GRN hierarchy |
| Feasibility (computational only) | 6 | Limited by available time-resolved data; dose-proxy helps |
| Timeline (summer 2026) | 6 | Proof-of-concept feasible, comprehensive framework harder |
| Publication potential (Nat Comp Sci) | 8 | New subfield with clear gap |
| **Overall** | **7.2** | High novelty and impact, moderate feasibility |

## References

1. PerturbGen Team (2026). Predicting how perturbations reshape cellular trajectories
   with PerturbGen. *bioRxiv* 10.64898/2026.03.04.709254.
2. AlphaCell Team (2026). Towards building a World Model to simulate
   perturbation-induced cellular dynamics by AlphaCell. *bioRxiv*
   10.64898/2026.03.02.709176.
3. DynPerturb Team (2025). DynPerturb: Dynamic Perturbation Modeling for
   Spatiotemporal Single-Cell Systems. *bioRxiv* 10.1101/2025.09.15.676236.
4. TRIGON Team (2025). Dissecting dynamic gene regulatory network using
   transformer-based temporal causality analysis. *bioRxiv*
   10.1101/2025.02.05.636766.
5. GRIT Team (2025). Dynamic gene regulatory network inference from single-cell data
   using optimal transport. *Bioinformatics* 41(8).
6. La Manno, G. et al. (2018). RNA velocity of single cells. *Nature* 560:494-498.
7. Schiebinger, G. et al. (2019). Optimal-transport analysis of single-cell gene
   expression identifies developmental trajectories in reprogramming. *Cell*
   176(4):928-943.
8. Chen, R.T.Q. et al. (2018). Neural ordinary differential equations. *NeurIPS*.
9. Replogle, J. et al. (2022). Mapping information-rich genotype-phenotype landscapes
   with genome-scale Perturb-seq. *Cell* 185(16):2559-2575.
10. Adamson, B. et al. (2016). A multiplexed single-cell CRISPR screening platform
    enables systematic dissection of the unfolded protein response. *Cell*
    167(7):1867-1882.
11. X-Atlas/Orion Team (2025). X-Atlas/Orion: Genome-wide Perturb-seq Datasets via a
    Scalable Fix-Cryopreserve Platform. *bioRxiv* 10.1101/2025.06.11.659105.
12. PertDiT Team (2026). Predicting drug-perturbed transcriptional responses using
    multi-conditional diffusion transformer. *Quantitative Biology*.
13. XPert Team (2025). Modelling drug-induced cellular perturbation responses with a
    biologically informed dual-branch transformer. *Nature Machine Intelligence*.
14. Experimentally calibrated multiscale model (2026). Predicts schedule dependent drug
    combination effects. *npj Systems Biology and Applications*.
15. Mini-review on perturbation modelling (2024). *Computational and Structural
    Biotechnology Journal*.

---

# Gap 4: Spatially-Resolved Perturbation Prediction -- Connecting Perturbation Models to Tissue Architecture

---
gap_id: spatial-perturb-tissue
---

## Gap Description

### What Is Missing

Current perturbation prediction models operate on **dissociated single cells in
isolation**, completely ignoring the spatial context in which cells exist within
tissues. A hepatocyte at the portal vein responds differently to the same perturbation
than a hepatocyte at the central vein, due to differences in oxygen, nutrient, and
signaling gradients. The field has no mature computational framework to predict how
genetic or chemical perturbations affect cells **in their native tissue
microenvironment**, accounting for cell-cell communication, spatial niches, and tissue
architecture -- or how perturbation effects propagate through tissues via cell-cell
interactions.

### Current State of the Art

**Spatial transcriptomics** has exploded in scale and resolution:
- **Nicheformer** (Nature Methods, 2025): Transformer-based foundation model trained on
  SpatialCorpus-110M (57 million dissociated + 53 million spatially resolved cells
  across 73 tissues). Key finding: models trained only on dissociated data "fail to
  recover the complexity of spatial microenvironments." This proves spatial context
  fundamentally changes cell state representations.
- **NicheCompass** (Nature Genetics, 2025): Graph deep learning for modeling cellular
  communication to learn interpretable cell embeddings encoding signaling events.
- **NicheFlow** (2025): Models microenvironment trajectories on spatial transcriptomics.
- **scNiche** (Nature Communications, 2025): Identifies and characterizes cell niches
  from spatial omics data at single-cell resolution.

**Cell-cell communication inference** has grown to >140 tools by 2025, but with
critical limitations:
- A comprehensive review (Briefings in Bioinformatics, 2025) documents >140 CCC tools
  and emphasizes: (a) high false-positive rates, (b) most tools operate at population
  resolution missing rare events, (c) no "gold standard" dataset exists for
  benchmarking, (d) limited ligand-receptor pairs measured.
- **SCILD** (Communications Biology, 2025): Models ligand diffusion and competitive
  binding for spatial CCC inference.
- **GITIII** (Nature Machine Intelligence, 2025): Self-supervised graph transformer
  for inferring CCI by examining cell state and niche correlations.
- A Nature Reviews Genetics review (2025) emphasizes "inferring the spatiotemporal
  dynamics of cell state transitions governed by cell-cell communication remains a
  challenge."

**Spatially-resolved perturbation** technologies have recently emerged:
- **Spatial Perturb-Seq** (Nature Communications, 2026; originally bioRxiv December
  2024): In vivo CRISPR technology that interrogates multiple genes within single cells
  of intact tissues. Applied to neurodegenerative disease risk genes in mouse brain,
  uncovering both cell-autonomous and cell-cell microenvironmental effects. First
  technology enabling perturbation screens in spatially intact tissue.
- **PERTURB-CAST/CHOCOLAT-G2P** (Nature Biomedical Engineering, 2025): Combines
  perturbation mapping with 10x Visium spatial transcriptomics and studies higher-order
  combinatorial perturbations that mimic tumor heterogeneity.
- **Perturb-Multimodal** (Cell, 2025): Paired imaging and sequencing for genotype-
  phenotype maps in tissues with pooled genetic perturbations.
- **SpaGraphCCI** (IET Systems Biology, 2025): GAT-based spatial CCC inference with
  co-convolution feature integration.

**Computational spatial perturbation prediction** is truly nascent:
- **SpatialProp** (bioRxiv, November 2025): The most directly relevant method. Uses
  graph neural networks to predict the effect of multi-gene, multi-cell-type
  perturbations on cells in whole tissue sections. Proposes CausalInteractionBench, a
  bidirectional benchmarking approach using curated cell-cell interactions to assess
  causal utility. This is the first computational framework explicitly designed for
  tissue-level perturbation prediction.
- **TRAILBLAZER** (bioRxiv, March 2026): Models tissues as coordinated multicellular
  systems with latent tokens, but without explicit spatial coordinates.
- **PULSAR** (bioRxiv, November 2025): Models donor-level multicellular systems but
  without spatial resolution.

**The gap**: Despite the recent emergence of SpatialProp, the field still lacks:
1. **Validated tissue-level perturbation prediction** -- SpatialProp is a proof-of-
   concept that has not been validated against actual spatial perturbation data (Spatial
   Perturb-Seq or PERTURB-CAST).
2. **Integration of perturbation data with spatial data** -- No method has been trained
   on actual matched spatial + perturbation experimental data.
3. **Prediction of perturbation propagation** -- How perturbation effects in one cell
   type alter neighboring cells through disrupted cell-cell communication.
4. **Scalable tissue-level perturbation simulation** -- Current methods cannot scale to
   whole-tissue simulations with millions of cells.

### Evidence the Gap Exists

1. **Nicheformer (Nature Methods, 2025)**: Demonstrates that spatial context changes
   cell representations fundamentally. Models trained on dissociated data fail.
2. **Spatial Perturb-Seq (Nature Communications, 2026)**: New experimental technology
   creates data that no prediction model can yet fully exploit.
3. **PERTURB-CAST (Nature Biomedical Engineering, 2025)**: Spatial perturbation data
   exists but no prediction framework matches it.
4. **SpatialProp (bioRxiv, 2025)**: First prediction method, but not validated on
   actual spatial perturbation data -- highlighting the gap between data and methods.
5. **Briefings in Bioinformatics review (2025)**: >140 CCC tools but most lack
   perturbation context and have high false-positive rates.
6. **"Virtual Cells Need Context" (2026)**: Spatial microenvironment is a key component
   of the missing "context" in perturbation prediction.

## Why This Gap Matters

### Scientific Importance

Tissues are not bags of independent cells. Cell-cell communication shapes cell state,
and perturbation responses propagate through tissues via signaling cascades. The Spatial
Perturb-Seq paper (Nature Communications, 2026) directly demonstrated that gene
perturbations in neurons produce both cell-autonomous effects AND microenvironmental
effects on neighboring cells -- effects invisible to dissociated-cell approaches.

This is particularly critical for:
- **Tumor microenvironment**: How does oncogene knockdown in tumor cells affect
  immune cell infiltration and activation?
- **Liver zonation**: How do drug metabolism genes respond differently in periportal
  vs. pericentral hepatocytes?
- **Brain circuits**: How does neuronal gene knockdown affect glial responses?

### Practical Impact

Drug effects are tissue-level phenomena. A drug targeting tumor cells will also alter
the tumor microenvironment through changed cell-cell communication. PERTURB-CAST's
study of combinatorial perturbations mimicking tumor heterogeneity demonstrates the
importance of tissue-level understanding for cancer therapy.

### Publication Potential

The intersection of spatial biology and perturbation prediction is nascent and high-
profile. A computational framework that integrates actual spatial perturbation data
(from Spatial Perturb-Seq or PERTURB-CAST) with tissue-level prediction would be
publishable in Nature Computational Science. The timing is ideal -- experimental data
is just becoming available.

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

Build a graph neural network framework that:
1. Represents tissue as a spatial graph (cells as nodes, spatial proximity + CCC as
   edges), building on SpatialProp's architecture
2. Trains on actual matched spatial + perturbation data from Spatial Perturb-Seq and
   PERTURB-CAST experiments
3. Propagates perturbation effects through the tissue graph via learned message-passing
   that respects ligand-receptor signaling
4. Predicts both cell-autonomous and non-cell-autonomous perturbation effects
5. Validates against held-out perturbations in actual spatial experiments
6. Uses CausalInteractionBench (SpatialProp) for principled evaluation

Key innovation: **Bridging experimental spatial perturbation data (which is new) with
computational tissue-level prediction (which is nascent)**. The experimental technology
now exists to validate spatial perturbation predictions -- the computational methods
must catch up.

### Required Data

- **Spatial Perturb-Seq data** (Nature Communications, 2026): Mouse brain spatial
  perturbation screens for neurodegenerative disease genes.
- **PERTURB-CAST data** (Nature Biomedical Engineering, 2025): Perturbation +
  Visium spatial transcriptomics in liver tumors.
- **Perturb-Multimodal data** (Cell, 2025): Paired imaging and sequencing perturbation
  data in tissue.
- **Nicheformer SpatialCorpus-110M**: 53 million spatially resolved cells for
  pre-training spatial representations.
- **Spatial transcriptomics atlases**: 10x Visium, MERFISH, Slide-seq datasets.
- **CCC databases**: CellChat, CellPhoneDB, NicheNet for ligand-receptor priors.

### Required Compute

- GNN training on spatial graphs with millions of nodes: 200-500 H200 GPU-hours.
- Integration with perturbation models: ~100 GPU-hours.
- Transfer learning from Nicheformer: ~100 GPU-hours.
- Evaluation and ablation: ~100 GPU-hours.
- Total estimated: 500-800 H200 GPU-hours.

### Required Methods

- Graph neural networks for spatial data (building on SpatialProp)
- Message passing for cell-cell communication propagation
- Transfer learning from Nicheformer spatial embeddings
- Integration with perturbation prediction (from STATE/X-Cell representations)
- Ligand-receptor signaling models (CellChat, NicheNet)
- CausalInteractionBench for evaluation

## Feasibility Assessment

### Technical Feasibility: Medium
The main advance since the initial assessment is the availability of actual spatial
perturbation data (Spatial Perturb-Seq, PERTURB-CAST, Perturb-Multimodal). SpatialProp
provides an initial architecture. The challenge is scale -- whole-tissue graphs are large
-- and the limited number of spatial perturbation experiments.

### Timeline Feasibility: Medium
A framework integrating SpatialProp with actual spatial perturbation data is feasible
in summer 2026. The key question is whether sufficient matched data is publicly
available for meaningful training and validation.

### Wet Lab Independence: High
Uses published spatial transcriptomics and spatial perturbation data. No wet lab required.

## Competitive Landscape

### Who Else Might Fill This Gap
- **SpatialProp team**: Already have the computational framework; natural extension
  to actual spatial perturbation data.
- **Regev Lab / CZI**: PERTURB-CAST developers with access to data.
- **Theis Lab (Helmholtz Munich)**: Nicheformer developers with spatial expertise.
- **TRAILBLAZER team**: Multicellular perturbation model could add spatial coordinates.
- **Spatial Perturb-Seq team**: Have the experimental data, may develop computational
  prediction tools.

### Risk of Being Scooped
**MEDIUM**. The intersection is nascent. SpatialProp exists but has not been validated
on actual spatial perturbation data. The computational-experimental integration is the
key open opportunity.

### Differentiation
Focus on **validated prediction using actual spatial perturbation data** rather than
simulated or inferred spatial effects. The availability of Spatial Perturb-Seq and
PERTURB-CAST data provides the first opportunity to rigorously validate tissue-level
perturbation predictions.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 8 | SpatialProp exists but validated integration is novel |
| Scientific impact | 8 | Connects perturbation biology with tissue architecture |
| Feasibility (computational only) | 6 | Now feasible with spatial perturbation data, but limited scale |
| Timeline (summer 2026) | 6 | Framework feasible; scale depends on data availability |
| Publication potential (Nat Comp Sci) | 8 | Novel intersection, high-profile experimental data now available |
| **Overall** | **7.2** | Novel and impactful; feasibility improved by new data |

## References

1. Schaar, A.C. et al. (2025). Nicheformer: a foundation model for single-cell and
   spatial omics. *Nature Methods*.
   https://www.nature.com/articles/s41592-025-02814-z
2. Spatial Perturb-Seq Team (2026). Spatial perturb-seq: single-cell functional
   genomics within intact tissue architecture. *Nature Communications*.
   https://www.nature.com/articles/s41467-026-69677-6
3. PERTURB-CAST Team (2025). Integrated in vivo combinatorial functional genomics and
   spatial transcriptomics of tumours. *Nature Biomedical Engineering*.
   https://www.nature.com/articles/s41551-025-01437-1
4. Perturb-Multimodal Team (2025). Simultaneous CRISPR screening and spatial
   transcriptomics reveal intracellular, intercellular, and functional transcriptional
   circuits. *Cell*.
5. SpatialProp Team (2025). SpatialProp: tissue perturbation modeling with spatially
   resolved single-cell transcriptomics. *bioRxiv* 10.64898/2025.11.30.691355.
6. TRAILBLAZER Team (2026). TRAILBLAZER: generative multicellular perturbation model
   of biology. *bioRxiv* 10.64898/2026.03.14.711710.
7. PULSAR Team (2025). PULSAR: a Foundation Model for Multi-scale and Multicellular
   Biology. *bioRxiv* 10.1101/2025.11.24.685470.
8. Advances and challenges in cell-cell communication inference (2025). *Briefings in
   Bioinformatics* 26(3):bbaf280.
   https://academic.oup.com/bib/article/26/3/bbaf280/8169297
9. SCILD Team (2025). Advancing spatial cellular communication inference with ligand
   diffusion and transport model. *Communications Biology*.
   https://www.nature.com/articles/s42003-025-09413-w
10. GITIII Team (2025). Inferring spatial single-cell-level interactions through
    interpreting cell state and niche correlations. *Nature Machine Intelligence*.
    https://www.nature.com/articles/s42256-025-01161-0
11. NicheCompass (2025). Quantitative characterization of cell niches in spatially
    resolved omics data. *Nature Genetics*.
12. DynPerturb Team (2025). DynPerturb: Dynamic Perturbation Modeling for
    Spatiotemporal Single-Cell Systems. *bioRxiv* 10.1101/2025.09.15.676236.
13. Wang, B. et al. (2026). Virtual Cells Need Context, Not Just Scale. *bioRxiv*
    10.64898/2026.02.04.703804.
14. Rood, J.E., Hupalowska, A., & Regev, A. (2024). Toward a foundation model of
    causal cell and tissue biology with a Perturbation Cell and Tissue Atlas. *Cell*
    187:4520-4545.

---

# Gap 5: Multi-Modal Perturbation Prediction -- Beyond the Transcriptome

---
gap_id: multimodal-perturb-predict
---

## Gap Description

### What Is Missing

Virtually all perturbation prediction methods operate exclusively on **transcriptomic
readouts** -- predicting gene expression changes after perturbation. However, cellular
state is defined by multiple molecular layers: chromatin accessibility (epigenome),
protein abundance (proteome), metabolites (metabolome), and cell morphology (phenome).
A perturbation may have dramatic effects on chromatin state or protein levels while
producing minimal transcriptomic changes, or vice versa. The field lacks mature methods
that predict perturbation effects across multiple molecular modalities simultaneously
and model the regulatory flow between them.

### Current State of the Art

**Multi-modal perturbation data** is now available:
- **Multiome Perturb-seq** (Cell Systems, January 2025): Simultaneously measures
  scRNA-seq and scATAC-seq (chromatin accessibility) after CRISPR perturbation. Applied
  CRISPRi screen of 13 chromatin remodelers in RPE-1 cells. Critical finding:
  **perturbation effects are modality-specific** -- ARID1A and SMARCC2 knockdowns
  primarily affected chromatin, DMAP1 and EP400 mostly modified gene expression, and
  SMARCE1 and YY1 altered both equally. This demonstrates that transcriptome-only
  prediction systematically misses important effects.
- **CAT-ATAC** (Cell Reports Methods, 2025): Simultaneous single-cell CRISPR, RNA,
  and ATAC-seq, enabling multiomic CRISPR screens.
- **Perturb-CITE-seq** (Frangieh et al., Nature Genetics, 2021): CRISPRi combined
  with protein surface marker measurement.
- **Cell Painting + L1000**: Image-based phenotyping combined with gene expression
  readouts. JUMP-CP consortium: 75 million cells treated with hundreds of chemical
  and genetic perturbations (Nature Methods, 2024).

**Multi-modal prediction models are emerging**:
- **MultiPert** (PLOS Computational Biology, March 2026): Adversarial alignment and
  dual attention framework for single-cell multi-omics perturbation prediction. Predicts
  both perturbed gene expression AND protein abundance profiles on THP-1 and kidney
  datasets. Achieves superior accuracy over GEARS and CPA. First published method for
  multi-omics perturbation prediction.
- **Prophet** (bioRxiv, 2025): Transformer pretrained on 4.7 million experiments that
  predicts outcomes across gene expression, viability, AND morphology. Can reduce
  viability screening experiments by 60x. Broadest multi-phenotype perturbation model.
- **MorphDiff** (Nature Communications, 2025): Transcriptome-guided latent diffusion
  model that simulates cell morphological responses to perturbations. Enhances MOA
  retrieval by 16.9% over baseline methods. First cross-modal prediction (expression ->
  morphology).
- **IMPA** (Nature Communications, 2024): Generative style-transfer model predicting
  morphological changes across genetic and chemical interventions.

**Multi-modal integration frameworks** (without perturbation):
- **MultiVI** (Nature Methods, 2023): Deep generative integration of multi-modal data.
- **MOFA+** (Genome Biology, 2020): Statistical multi-modal factor analysis.
- **SIMO** (Nature Communications, 2025): Spatial Integration of Multi-Omics through
  probabilistic alignment.
- **DBiTplus** (Nature Methods, 2025): Integrates sequencing-based spatial
  transcriptomics and multiplexed protein imaging on same tissue section.

**The gap has narrowed but not closed**:
1. MultiPert predicts RNA + protein but not chromatin/morphology.
2. MorphDiff predicts morphology from expression but not the reverse or joint prediction.
3. Prophet is broad but shallow -- predicts scalar phenotypes (viability), not full
   distributional shifts across modalities.
4. No method jointly predicts perturbation effects across transcriptome + epigenome
   (chromatin accessibility) using the Multiome Perturb-seq data, despite the data
   demonstrating modality-specific effects.
5. No method models the **regulatory flow** between modalities (chromatin -> RNA ->
   protein -> morphology) as a dynamic system.

### Evidence the Gap Exists

1. **Multiome Perturb-seq (Cell Systems, 2025)**: Chromatin and transcription changes
   are not redundant -- some perturbations primarily affect chromatin (ARID1A, SMARCC2),
   others primarily expression (DMAP1, EP400). Transcriptome-only models miss half
   the picture.
2. **CAT-ATAC (Cell Reports Methods, 2025)**: Further multi-modal perturbation data
   confirming modality-specific effects.
3. **mRNA-Protein Coordination paper (bioRxiv, 2025)**: mRNA-protein coordination is
   "contextualized by metastatic biological phenotypes" -- protein abundance does not
   always follow mRNA levels.
4. **scPerturBench (Nature Methods, 2025)**: 27 methods evaluated -- all on
   transcriptomic readouts only.
5. **PerturBench (NeurIPS 2024)**: Evaluates only transcriptomic readouts.
6. **JUMP-CP consortium (Nature Methods, 2024)**: 75M cells with image + expression
   data, but no prediction framework exploits both modalities for perturbation
   prediction.
7. **MultiPert (PLOS Comp Bio, 2026)**: First multi-omics method, but limited to
   RNA + protein; does not model regulatory flow or chromatin.

## Why This Gap Matters

### Scientific Importance

Understanding how perturbations propagate across molecular layers (DNA -> chromatin ->
RNA -> protein -> phenotype) is fundamental to understanding gene regulation. The
Multiome Perturb-seq finding that chromatin remodeler knockdowns have modality-specific
effects (some alter chromatin without proportional transcriptomic changes) reveals that
the central dogma is not a simple pipeline -- there are feedbacks, delays, and
modality-specific effects at every level. A multi-modal perturbation prediction model
would reveal these cross-modality dynamics.

### Practical Impact

Drug targets are proteins, not mRNA. Predicting perturbation effects at the protein
level, not just the transcriptomic level, is directly relevant to drug development.
Epigenetic therapies (e.g., EZH2 inhibitors, BET inhibitors) act on chromatin -- their
effects should be predicted at the chromatin level. Cell Painting morphological profiling
captures phenotypic changes that may not be evident at any single molecular level.

### Publication Potential

A unified framework that jointly predicts perturbation effects across transcriptome +
epigenome (using Multiome Perturb-seq) or transcriptome + proteome + morphology (using
CITE-seq + Cell Painting data) would advance beyond MultiPert's initial contribution.
The key novelty would be modeling regulatory flow between modalities, not just predicting
each independently. High potential for Nature Computational Science or Nature Methods.

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

Develop a hierarchical multi-modal model that:
1. Learns shared and modality-specific latent representations from multi-modal
   single-cell data (building on MultiVI architecture)
2. Models the **directed regulatory flow** between modalities: chromatin -> RNA ->
   protein (with feedback), informed by biological priors
3. Predicts perturbation effects in each modality, accounting for cross-modal
   regulatory delays and modality-specific effects
4. Validates on Multiome Perturb-seq (RNA + ATAC), Perturb-CITE-seq (RNA + protein),
   and JUMP-CP (expression + morphology) data
5. Tests cross-modal transfer: can chromatin-level perturbation effects be predicted
   from transcriptomic training data, and vice versa?

Key innovation: **Directed regulatory flow modeling** -- not just multi-modal prediction,
but modeling the causal chain (chromatin -> expression -> protein) and identifying where
perturbation effects originate and how they propagate across modalities.

### Required Data

- **Multiome Perturb-seq** (Cell Systems, 2025): Joint RNA + ATAC CRISPRi data for
  13 chromatin remodelers in RPE-1 cells.
- **CAT-ATAC** (Cell Reports Methods, 2025): Joint CRISPR + RNA + ATAC data.
- **Perturb-CITE-seq** (Frangieh et al., Nature Genetics, 2021): CRISPRi + protein
  surface markers.
- **JUMP-CP** (Nature Methods, 2024): 75 million cells with image + expression data
  from chemical and genetic perturbations.
- **SHARE-seq / 10x Multiome data**: Multi-modal single-cell data for pre-training
  cross-modal models (without perturbation).
- **Tahoe-100M**: Transcriptomic perturbation data for transfer learning.

### Required Compute

- Multi-modal VAE/transformer training: 200-500 H200 GPU-hours.
- Cross-modal transfer learning: ~100-200 GPU-hours.
- Image processing for Cell Painting data: ~100 GPU-hours.
- Evaluation and ablation: ~100 GPU-hours.
- Total estimated: 500-900 H200 GPU-hours.

### Required Methods

- Multi-modal variational autoencoders (MultiVI architecture)
- Directed graphical models for regulatory flow (chromatin -> RNA -> protein)
- Transformer architectures for multi-modal integration
- Image feature extraction for Cell Painting (pretrained CNNs)
- Perturbation modeling in shared latent space
- Evaluation metrics for each modality separately and jointly

## Feasibility Assessment

### Technical Feasibility: Medium
Multi-modal single-cell integration is well-established (MultiVI, MOFA+). MultiPert
has demonstrated multi-omics perturbation prediction is feasible. The challenge is
extending to the regulatory flow model and integrating heterogeneous data types
(sequencing + imaging).

### Timeline Feasibility: Medium
A focused model for RNA + ATAC perturbation prediction (using Multiome Perturb-seq and
CAT-ATAC data) is feasible in summer 2026. Extending to protein and morphology would
take longer but could be a follow-up.

### Wet Lab Independence: High
All data is publicly available. No wet lab required.

## Competitive Landscape

### Who Else Might Fill This Gap
- **MultiPert team**: First movers in multi-omics perturbation prediction; natural
  extension to more modalities.
- **Multiome Perturb-seq / CAT-ATAC authors**: Have the data, may develop prediction
  methods.
- **Prophet team**: Already predicting across phenotype types; could extend architecture.
- **MorphDiff team**: Cross-modal prediction (expression -> morphology) could extend.
- **CZI Virtual Cells**: TranscriptFormer could extend to multi-modal.
- **Theis Lab**: Expertise in multi-modal integration (MultiVI, scArches).

### Risk of Being Scooped
**MEDIUM**. MultiPert (March 2026) is the first multi-omics perturbation method but
focuses on RNA + protein. The RNA + chromatin direction (using Multiome Perturb-seq)
and the regulatory flow modeling are both open.

### Differentiation
Focus on **directed regulatory flow modeling** -- not just predicting each modality
independently (as MultiPert does), but modeling the causal chain of how perturbation
effects propagate from one modality to another. The Multiome Perturb-seq data showing
modality-specific effects provides both the motivation and the validation data.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 8 | Regulatory flow modeling across modalities is novel |
| Scientific impact | 8 | Connects perturbation biology with multi-omics regulation |
| Feasibility (computational only) | 6 | Data is available; integration is challenging |
| Timeline (summer 2026) | 6 | RNA+ATAC proof-of-concept feasible, full multi-modal harder |
| Publication potential (Nat Comp Sci) | 8 | Clear gap beyond MultiPert |
| **Overall** | **7.2** | Novel, impactful, feasible for focused contribution |

## References

1. Multiome Perturb-seq Team (2025). Multiome Perturb-seq unlocks scalable discovery
   of integrated perturbation effects on the transcriptome and epigenome. *Cell
   Systems* 16(1):101143.
   https://www.cell.com/cell-systems/fulltext/S2405-4712(24)00366-1
2. CAT-ATAC Team (2025). Simultaneous capture of single cell RNA-seq, ATAC-seq, and
   CRISPR perturbation enables multiomic screens. *Cell Reports Methods*.
   https://www.cell.com/cell-reports-methods/fulltext/S2667-2375(25)00258-9
3. MultiPert Team (2026). MultiPert: An adversarial alignment and dual attention
   framework for single-cell multi-omics perturbation prediction. *PLOS Computational
   Biology*. https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014054
4. Prophet Team (2025). Scalable and universal prediction of cellular phenotypes.
   *bioRxiv* 10.1101/2024.08.12.607533.
5. MorphDiff Team (2025). Prediction of cellular morphology changes under perturbations
   with a transcriptome-guided diffusion model. *Nature Communications*.
   https://www.nature.com/articles/s41467-025-63478-z
6. IMPA Team (2024). Predicting cell morphological responses to perturbations using
   generative modeling. *Nature Communications*.
   https://www.nature.com/articles/s41467-024-55707-8
7. Frangieh, C.J. et al. (2021). Multimodal pooled Perturb-CITE-seq screens in
   patient models define mechanisms of cancer immune evasion. *Nature Genetics*
   53:332-341.
8. JUMP-CP Consortium (2024). Three million images and morphological profiles of cells
   treated with matched chemical and genetic perturbations. *Nature Methods*.
   https://www.nature.com/articles/s41592-024-02241-6
9. Ashuach, T. et al. (2023). MultiVI: deep generative model for the integration
   of multimodal data. *Nature Methods* 20:1222-1231.
10. Argelaguet, R. et al. (2020). MOFA+: a statistical framework for comprehensive
    integration of multi-modal single-cell data. *Genome Biology* 21:111.
11. SIMO Team (2025). Spatial integration of multi-omics single-cell data with SIMO.
    *Nature Communications*. https://www.nature.com/articles/s41467-025-56523-4
12. DBiTplus Team (2025). Integration of imaging-based and sequencing-based spatial
    omics mapping on the same tissue section. *Nature Methods*.
    https://www.nature.com/articles/s41592-025-02948-0
13. Sharma, R. et al. (2025). mRNA-Protein Coordination is Contextualized by
    Metastatic Biological Phenotypes. *bioRxiv*.
14. Zhang, Y. et al. (2025). Benchmarking algorithms for generalizable single-cell
    perturbation response prediction. *Nature Methods*.
15. Hetzel, L. et al. (2024). PerturBench: Benchmarking Machine Learning Models for
    Cellular Perturbation Analysis. *NeurIPS 2024*.

---

# Summary Table: All Identified Gaps

| Gap ID | Gap Title | Novelty | Impact | Feasibility | Timeline | Pub Potential | Overall |
|--------|-----------|---------|--------|-------------|----------|---------------|---------|
| context-perturb-transfer | Cross-Context Perturbation Prediction | 6 | 9 | 9 | 8 | 8 | **8.0** |
| causal-grn-scale | Genome-Scale Causal GRN Inference | 8 | 9 | 6 | 6 | 9 | **7.6** |
| temporal-perturb-dynamics | Temporal Perturbation Dynamics | 8 | 8 | 6 | 6 | 8 | **7.2** |
| spatial-perturb-tissue | Spatial Perturbation Prediction | 8 | 8 | 6 | 6 | 8 | **7.2** |
| multimodal-perturb-predict | Multi-Modal Perturbation Prediction | 8 | 8 | 6 | 6 | 8 | **7.2** |

## Cross-Gap Synergies

Several of these gaps are deeply interconnected and could combine into a larger project:

1. **Context + Causal GRN (Gaps 1 + 2)**: Causal GRNs that are context-specific
   (different regulatory wiring in different cell types) would directly enable
   cross-context perturbation prediction. The GRN provides the mechanistic model;
   context-conditioning provides the adapter. The key question -- "does knowing the
   causal network improve cross-context prediction?" -- bridges both gaps. If
   context-specific GRNs can be inferred from perturbation data and used to predict
   unseen perturbations in unseen contexts, this would demonstrate both the value of
   GRN inference AND the mechanism of context-dependent perturbation effects.

2. **Temporal + Multi-Modal (Gaps 3 + 5)**: Perturbation effects propagate across
   molecular layers (chromatin -> RNA -> protein) with characteristic time delays. A
   temporal model that also predicts cross-modal dynamics would capture the full
   regulatory cascade. The Multiome Perturb-seq finding that some perturbations act
   primarily on chromatin (ARID1A) while others act on expression (DMAP1) suggests
   temporal ordering: chromatin changes may precede or follow expression changes
   depending on the perturbation target.

3. **Spatial + Context (Gaps 4 + 1)**: Spatial microenvironment IS cellular context.
   The "Virtual Cells Need Context" paper argues that context must be made explicit --
   spatial coordinates, tissue architecture, and cell-cell communication are among the
   most informative context features. Connecting spatial biology with context-aware
   perturbation prediction is a natural integration.

4. **All five gaps converge on the "Virtual Cell" vision**: A true virtual cell would
   predict perturbation effects across contexts (Gap 1), using causal regulatory
   networks (Gap 2), over time (Gap 3), in spatial tissue context (Gap 4), across
   multiple molecular modalities (Gap 5). Each gap is a piece of this larger puzzle.
   CZI's Virtual Cells Platform, rBio reasoning model, NVIDIA's SCALE, and Xaira's
   X-Cell are all pieces of this vision -- but none addresses more than one or two
   of these gaps simultaneously.

## Recommended Combinations for Nature Computational Science

**Most feasible and impactful**: **Gap 1 (benchmarking path) + Gap 2**. A rigorous
cross-context benchmarking framework that evaluates whether causal GRN-based perturbation
prediction outperforms direct prediction methods. This would:
- Establish the definitive benchmark for cross-context generalization
- Test the hypothesis that GRN inference adds predictive value
- Use Replogle, X-Atlas/Pisces, and Tahoe-100M data
- Be achievable in summer 2026 with clear deliverables
- Address the most fundamental question: is the intermediate GRN representation useful?

**Most novel**: **Gap 3 + Gap 5**. Temporal multi-modal perturbation prediction using
dose-response data as temporal proxy and Multiome Perturb-seq for multi-modal validation.
This addresses two largely unexplored dimensions simultaneously.

**Most data-driven opportunity**: **Gap 4**. The recent availability of Spatial
Perturb-Seq, PERTURB-CAST, and Perturb-Multimodal data creates a window where
computational methods can be validated against actual experimental data for the first
time. SpatialProp provides the starting architecture but has not been validated on
these datasets.
