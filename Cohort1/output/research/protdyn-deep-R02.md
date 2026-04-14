---
agent: protdyn
round: 2
date: 2026-04-14
type: deep-dive
---

# Deep Dive: Dynamics-to-Function Mapping & Ensemble-Aware Mutation Effect Prediction

## Executive Summary

This deep-dive investigates two tightly coupled gaps: (1) the absence of a general framework mapping predicted conformational ensembles to biological function, and (2) the failure of current mutation effect predictors to account for conformational dynamics. After extensive literature review of 2025-2026 publications, these gaps remain **substantially open** but are experiencing rapid convergence of enabling technologies. BioEmu (Microsoft, Science 2025) makes high-throughput ensemble generation newly feasible; ProteinGym provides >2.7M DMS measurements as ground truth; and several recent preprints (SeqDance/ESMDance, DETANGO, QDPR, distogram representations) demonstrate that dynamics information improves variant effect prediction -- but **no unifying framework exists** that connects explicit ensemble properties from generative models to quantitative functional readouts. This represents a clear, high-impact opportunity for a Nature Computational Science paper.

---

## 1. Gap Verification (2026 Preprint Check)

### 1.1 Has anyone built a general ensemble-to-function predictor?

**No.** After systematic search of bioRxiv, arXiv, and published literature through April 2026, no paper presents a general-purpose framework that takes a predicted conformational ensemble as input and outputs quantitative functional properties (kcat, Kd, DMS fitness scores). The closest approaches are:

**Partial solutions that exist:**

1. **SeqDance/ESMDance** (Hou & Shen, PNAS January 2026): Protein language models trained on dynamic biophysical properties from MD simulations and normal mode analyses of >64,000 proteins. ESMDance improves zero-shot mutation effect prediction for designed and viral proteins lacking evolutionary information. However, these models use *implicit* dynamics representations (learned from MD training data) rather than *explicit* ensemble properties from generated conformations. They do not take ensemble input.

2. **QDPR framework** (Burgin, JCIM 2025, vol. 65, pp. 11979-11987): Quantified Dynamics-Property Relationships use MD-derived descriptors and small amounts of experimental labels to predict protein properties. This is the closest conceptual match to our gap, but it requires protein-specific MD simulations and small experimental datasets -- it is not a general, transferable framework.

3. **Ozkan DCIasym GNN** (Ozkan, PNAS 2025, vol. 122, e2502444122): Dynamics-based graph convolutional network using the Asymmetric Dynamic Coupling Index from normal mode analysis. Outperforms existing methods on DMS epistasis prediction across four proteins. Uses *computed* dynamics features, not generated ensembles. Limited to four proteins.

4. **Distogram representations** (bioRxiv January 2026): Uses AlphaFold2 distograms (residue-residue distance probability distributions) as proxy for dynamics in an R-EGNN framework. Improves stability prediction (Spearman correlation from 0.727 to 0.740). Promising but uses distograms as a *proxy* for dynamics rather than explicit ensembles.

5. **Conformational Biasing** (CB; Science 2025): Uses ProteinMPNN inverse folding scores to predict mutations that bias proteins toward desired conformational states. Validated on seven DMS datasets. However, this is a *design* tool (mutations -> conformations) not a *prediction* tool (ensembles -> function).

6. **DETANGO** (bioRxiv February 2026): Disentangles mutation effects on protein stability vs. function using protein language models. Identifies stability-but-inactive variants. Does not use ensemble information.

**What is missing:** A framework that takes an *explicit* conformational ensemble (e.g., 1000-10000 structures from BioEmu) and predicts functional properties. No method connects the statistical properties of generated ensembles (conformational heterogeneity, cryptic pocket occupancy, domain motion amplitudes, local flexibility patterns) to quantitative functional readouts.

### 1.2 Has anyone combined BioEmu with DMS data?

**No.** BioEmu was published in Science in July 2025 (Lewis et al., Science 2025, vol. 369, pp. 270-278). Despite being open-source since early 2025, no published or preprint work uses BioEmu-generated ensembles as features for DMS fitness prediction as of April 2026.

The closest work is:
- **BioEmu augmented molecular simulation** (bioRxiv January 2026): Combines BioEmu ensembles with MD simulations and Markov State Models to study kinase conformational dynamics and mutation-induced population shifts. This demonstrates that BioEmu can capture mutation effects on conformational distributions, but does not connect to DMS fitness data.
- An independent assessment paper (Aryal et al., Int. J. Mol. Sci. 2025, vol. 27, 2896) found that BioEmu "fails to predict a mutation-induced shift in conformational distribution" and "cannot effectively differentiate driver and passenger mutations." This highlights a limitation but also an opportunity: the ensemble-to-function mapping layer could compensate for imperfections in ensemble generation.

### 1.3 Verdict: Gaps remain substantially open

The gap is real and growing more urgent. The field has the tools (BioEmu, AlphaFlow, Boltz-2) to generate ensembles and the data (ProteinGym, MEGAscale) to measure function, but no one has built the bridge between them. Several groups are approaching this from different angles, creating a narrow window of opportunity.

---

## 2. Tool and Data Accessibility Audit

### 2.1 BioEmu Status

**License:** MIT license (fully open-source)
**Repository:** github.com/microsoft/bioemu
**Installation:** `pip install bioemu` (or `pip install bioemu[cuda]` for GPU support)
**Python requirement:** >= 3.10
**Dependencies:** ColabFold/AlphaFold2 weights (~3.5 GB, auto-download), optional HPacker for side-chain reconstruction

**Model checkpoints available:**
- **v1.0**: 31.4M parameters. Trained on 161K AFDB structures, 216 ms MD, 19K delta-G measurements
- **v1.1**: 31.4M parameters. Same AFDB/MD, expanded to 502K delta-G measurements (Science paper version)
- **v1.2**: 35.7M parameters. Same AFDB, 145.4 ms MD, 1.3M delta-G measurements. Adds residue type and pair embeddings.

**Architecture:** Based on Distributional Graphormer (DiG). Denoising score matching for flexible protein structure distributions. Fine-tuning combines denoising score matching on MD data with property prediction for experimental folding free energies.

**Performance benchmarks (from model card):**
| Metric | Value |
|--------|-------|
| Domain motion coverage | 83% |
| Local unfolding (folded) | 70% |
| Local unfolding (unfolded) | 82% |
| Cryptic pocket detection (apo) | 55% |
| Cryptic pocket detection (holo) | 88% |
| MD equilibrium emulation MAE | 0.9 kcal/mol |
| Protein stability prediction MAE | 0.9 kcal/mol |
| Protein stability Spearman rho | 0.6 |

**Sampling speed on A100 80GB (1000 samples, batch_size_100=20):**
| Protein length | Time |
|---------------|------|
| 100 residues | ~4 min |
| 300 residues | ~40 min |
| 600 residues | ~150 min |

**Protein size limits:** Primarily single-chain monomers. Tested up to 900 residues. Best performance for proteins <500 residues. Multi-chain support experimental/not recommended.

**Key limitation for our project:** Current BioEmu outputs backbone frame representations only. No side-chain atoms (HPacker needed as post-processing). No explicit multi-chain or ligand support. Mutation effects on ensembles are not yet reliable per independent assessment.

**H200 GPU compatibility:** BioEmu requires CUDA12-compatible drivers. H200 GPUs (141 GB HBM3e, 4.8 TB/s bandwidth) are fully CUDA12 compatible and provide ~76% more VRAM than the A100 used for benchmarking. Expected speedup of 1.5-2x over A100 for inference workloads, and the 141 GB VRAM eliminates any memory constraints even for the largest single-chain proteins.

### 2.2 AlphaFlow Status

**License:** MIT license
**Repository:** github.com/bjing2016/alphaflow
**Versions:** AlphaFlow-PDB, AlphaFlow-MD, AlphaFlow-MD+Templates (12-layer and 48-layer)
**Efficiency variant:** AlphaFlow-Lit achieves ~47x sampling acceleration
**Performance:** Surpasses baselines in predicting conformational flexibility, distributional modeling, and ensemble observables

AlphaFlow complements BioEmu: AlphaFlow is better at modeling experimental conformational heterogeneity (PDB-like ensembles), while BioEmu better approximates equilibrium thermodynamic ensembles.

### 2.3 Boltz-2 Status

**License:** Open source
**Repository:** github.com/jwohlwend/boltz
**Key advantage:** First biomolecular co-folding model combining structure prediction with binding affinity prediction. Trained on structural ensembles including local fluctuations and side-chain dynamics. Boltz-sample strategy (January 2026) enables controllable conformational sampling.
**Comparison:** Matches BioEmu and AlphaFlow performance on dynamic property benchmarks.

### 2.4 ProteinGym Coverage

**Substitution benchmark:** ~2.7M missense variants across 217 DMS assays and 2,525 clinical proteins
**Indel benchmark:** ~300K mutants across 74 DMS assays and 1,555 clinical proteins
**Clinical dataset:** ~65K substitution and indel mutations with expert annotations
**Current version:** v1.3 (adds ESM3, ESM C, ProGen3, xTrimoPGLM baselines)

**Overlap with structural data:** 
- 197 protein structures available from PDB for ProteinGym proteins
- 52 of 186 unique UniProt IDs (28%) have matching experimental structures after stringent filtering
- 65 assays with directly matching PDB experimental structures

**Key DMS assay types relevant to our project:**
- Enzyme activity (kcat, catalytic efficiency)
- Binding affinity (protein-protein, protein-ligand)
- Protein stability (ddG)
- Cellular fitness/growth assays
- Fluorescence/expression level

### 2.5 Additional Stability/Function Data

**MEGAscale dataset** (Tsuboyama et al., Nature 2023):
- ~776,000 high-quality folding stability measurements
- 331 natural + 148 designed protein domains (40-72 amino acids)
- All single amino acid variants + selected double mutants
- 210,118 double mutants at 559 site pairs across 190 domains
- BioEmu v1.2 was fine-tuned on >1.3M MEGAscale measurements

**FireProtDB 2.0** (NAR 2025):
- 12,923,886 measurements aggregated into 5,465,664 experiments
- 2,762 unique proteins
- Supports single/multiple-point substitutions, insertions, deletions
- Stores both absolute (delta-G, Tm) and relative (delta-delta-G, delta-Tm) values

### 2.6 Experimental Dynamics Data (NMR, HDX-MS, SAXS)

**BMRB (Biological Magnetic Resonance Bank):**
- >10,868,000 assigned chemical shifts across 15,451 studies
- Contains relaxation data (R1/R2), order parameters (S2), RDCs, hydrogen exchange rates
- Critical for validation: order parameters directly measure ps-ns dynamics
- Recent work by Wayment-Steele, Ovchinnikov & Kern (bioRxiv March 2025) shows missing NMR signals encode ms-timescale dynamics for ~10,000 proteins in BMRB

**SASBDB (Small Angle Scattering Biological Data Bank):**
- 5,243 experimental datasets and 6,486 models
- Provides global shape and flexibility information
- Useful for validating ensemble radius of gyration distributions

**HDX-MS data:**
- No centralized public database exists (a known limitation)
- Scattered across individual publications
- GitHub resource (hadexversum/HDX-MS-resources) curates software and publications
- HDX-MS measures solvent accessibility dynamics at peptide resolution

**Limitation:** Cross-referencing proteins that have ALL of: DMS data + structural data + dynamics data (NMR/HDX/SAXS) yields a relatively small overlap set. Estimated at 30-50 proteins with high-quality data across all three modalities. This is sufficient for validation but not for large-scale training; the framework must generalize from ensemble statistics alone.

---

## 3. Compute Requirements

### 3.1 Ensemble Generation at Scale

**Target:** Generate BioEmu ensembles for all ProteinGym proteins with available structural data (~200 proteins).

**Per-protein cost (1000 conformations, H200 GPU):**
| Protein size | Estimated time (H200) | GPU-hours |
|-------------|----------------------|-----------|
| 100 residues | ~2.5 min | 0.04 |
| 200 residues | ~15 min | 0.25 |
| 300 residues | ~25 min | 0.42 |
| 400 residues | ~60 min | 1.0 |
| 500 residues | ~100 min | 1.67 |
| 600 residues | ~100 min | 1.67 |

**Note:** H200 estimates assume ~1.5x speedup over A100 due to higher memory bandwidth (4.8 vs 2.0 TB/s) and FP8 support.

**Scaling analysis:**
- 200 proteins x 1000 conformations each x average ~0.5 GPU-hours per protein = **~100 GPU-hours** for initial ensemble generation
- For 10,000 conformations per protein (better statistics): ~1,000 GPU-hours
- For variant-specific ensembles (needed for mutation effect prediction): 200 proteins x 50 key variants x 1000 conformations x 0.5 h = **~5,000 GPU-hours**
- Total ensemble generation budget: **~5,000-10,000 H200 GPU-hours** (achievable in days on the described HPC cluster)

### 3.2 Storage Requirements

- Per conformation: backbone coordinates for 300 residues ~ 7.2 KB (300 residues x 4 atoms x 3 coords x 2 bytes)
- Per protein (10,000 conformations): ~72 MB
- Full dataset (200 proteins x 10,000 conformations): ~14 GB
- With variant-specific ensembles (200 proteins x 50 variants x 1,000 conformations): ~70 GB
- Total with processed features: **~200-500 GB** (trivially manageable)

### 3.3 Model Training

The ensemble-to-function model itself is relatively small compared to foundation models:
- Input: ensemble summary statistics or graph representations per protein variant
- Output: predicted functional readout (fitness score, stability change, etc.)
- Estimated model size: 1-10M parameters (graph neural network or attention-based)
- Training data: ~50,000-200,000 protein-variant-function triplets
- Training cost: **~100-500 H200 GPU-hours** (days, not weeks)

### 3.4 Total Compute Budget

| Phase | GPU-hours (H200) | Wall time (8 GPUs) |
|-------|------------------|--------------------|
| Initial ensemble generation (200 proteins) | 1,000 | ~5 days |
| Variant-specific ensembles (top 50 proteins) | 5,000 | ~4 weeks |
| Ensemble feature extraction | 200 | ~1 day |
| Model training + hyperparameter search | 500 | ~3 days |
| Ablation studies + baselines | 1,000 | ~5 days |
| Validation ensemble generation | 500 | ~3 days |
| **Total** | **~8,200** | **~6 weeks** |

This is well within the described HPC cluster capacity with H200/B200/RTX 5000 Ada GPUs.

---

## 4. Method Landscape

### 4.1 Candidate Architectures for Ensemble-to-Function Mapping

**Option A: Ensemble Summary Statistics + MLP/XGBoost**
- Extract hand-crafted features from each ensemble: RMSF per residue, radius of gyration distribution, contact frequency maps, secondary structure content fluctuations, cryptic pocket occupancy, principal component amplitudes
- Feed into conventional ML model with DMS fitness as target
- Pros: Interpretable, fast, baseline approach
- Cons: Loses rich structural information, requires feature engineering

**Option B: Graph Neural Network on Ensemble Distributions (Preferred)**
- Represent each protein variant as a graph where nodes are residues and edges encode ensemble-averaged distance distributions (similar to distograms but computed from generated ensembles)
- Node features: per-residue RMSF, secondary structure propensities, sequence identity
- Edge features: pairwise distance distributions, contact frequency, correlated motions
- Architecture: SE(3)-equivariant GNN or message-passing network
- Precedent: The Ozkan DCIasym GNN already demonstrates that dynamics-derived graph edges improve fitness/epistasis prediction (PNAS 2025)
- Pros: Captures spatial relationships, handles variable protein sizes, naturally represents ensemble statistics
- Cons: Requires careful feature engineering from ensembles

**Option C: Attention over Conformational States**
- Treat each conformation in an ensemble as a "token"
- Use cross-attention between conformational states to learn which motions matter for function
- Similar spirit to AlphaPPImd transformer (JCTC 2024)
- Pros: Learns which conformational states are functionally relevant
- Cons: Computationally expensive for large ensembles (1000+ states), may overfit

**Option D: Hybrid Approach (Recommended)**
- Phase 1: Extract per-residue and pairwise ensemble statistics from BioEmu-generated conformations
- Phase 2: Encode as a graph with distogram-like edge features computed from the ensemble
- Phase 3: Use an SE(3)-equivariant GNN with additional global readout for functional prediction
- Phase 4: Add attention pooling over a small set of representative conformational clusters
- This combines the efficiency of summary statistics with the expressiveness of graph networks

### 4.2 Key Ensemble Features for Function Prediction

Based on the literature, the most informative ensemble properties include:

1. **Per-residue flexibility (RMSF):** Directly correlates with B-factors; identifies flexible loops, hinge regions
2. **Pairwise distance distributions:** Distogram-like features computed from ensembles. Recent work shows even AF2 distograms improve stability prediction (Spearman 0.727 -> 0.740)
3. **Dynamic coupling indices:** DCIasym (Ozkan, PNAS 2025) quantifies how residue pairs influence each other's flexibility
4. **Conformational state populations:** Relative populations of open/closed/intermediate states from ensemble clustering
5. **Cryptic pocket occupancy:** Fraction of ensemble with transient binding sites exposed (BioEmu reports 55-88% detection rates)
6. **Local unfolding propensity:** Fraction of ensemble showing partial unfolding at each region
7. **Solvent-accessible surface area (SASA) fluctuations:** Dynamic exposure of buried residues
8. **Correlated motions matrix:** Identifies allosteric pathways through ensemble analysis

### 4.3 Training Strategy

**Multi-task learning approach:**
- Primary task: Predict DMS fitness scores for single mutations
- Auxiliary tasks: Predict protein stability (delta-delta-G from MEGAscale), predict NMR order parameters (S2 from BMRB), predict B-factors
- Multi-task learning forces the model to learn physically meaningful ensemble representations
- The DETANGO approach (bioRxiv February 2026) shows that disentangling stability from function improves prediction -- our approach naturally separates these through different ensemble features

**Transfer learning pipeline:**
1. Pre-train on ensemble statistics from all ProteinGym proteins (self-supervised: predict masked ensemble properties)
2. Fine-tune on DMS fitness data using ensemble features as input
3. Evaluate zero-shot performance on held-out proteins (the key test of generalizability)

---

## 5. Competition Assessment

### 5.1 Groups Approaching This Space

**Microsoft Research (Noe, Clementi, Lewis et al.):**
- Created BioEmu. Obvious insiders for any ensemble-to-function project.
- Recent focus: BioEmu augmented MD (January 2026), studying kinase conformational dynamics and mutation effects.
- Risk level: **HIGH.** They have the tools and infrastructure. However, their published work focuses on physics-based applications (free energies, conformational transitions) rather than ML-based function prediction from ensembles.

**Marks Lab (Harvard):**
- Created ProteinGym, EVE, TranceptEVE. Leading variant effect prediction group.
- ProteinGym v1.3 continues expanding baselines but none use explicit ensemble information.
- Risk level: **MEDIUM.** They have the data and evaluation infrastructure but have focused on sequence/evolutionary methods rather than dynamics.

**Shen Lab (Columbia) / SeqDance team:**
- Published SeqDance/ESMDance (PNAS January 2026) -- dynamics-aware protein language models.
- Risk level: **MEDIUM-HIGH.** Conceptually aligned but uses implicit dynamics (from MD training) not explicit ensembles. A natural competitor if they extend to ensemble-based methods.

**Ozkan Lab:**
- Published DCIasym GNN for dynamics-aware fitness/epistasis prediction (PNAS 2025).
- Risk level: **MEDIUM.** Demonstrated concept on four proteins. Would need to scale dramatically.

**Lindorff-Larsen Lab (Copenhagen):**
- Published review on sequence-ensemble-function relationships for disordered proteins (Current Opinion in Structural Biology 2025).
- Focus on IDPs; may not target general ensemble-to-function mapping for ordered proteins.
- Risk level: **LOW-MEDIUM.**

**Baker Lab (UW):**
- Published PLACER for protein-ligand conformational ensembles (PNAS 2025) and dynamic protein design (Science 2025).
- Focus is on design, not prediction from ensembles.
- Risk level: **LOW.** Different direction.

**Kern & Ovchinnikov:**
- Published work on learning protein dynamics from NMR data (bioRxiv March 2025).
- Focus is on experimental dynamics characterization, not ensemble-to-function prediction.
- Risk level: **LOW.**

### 5.2 Assessment of Window of Opportunity

The window is **narrow but currently open.** Key factors:
- BioEmu open-sourced (February 2025, MIT license) makes this technically feasible for any group
- ProteinGym provides standardized benchmarks
- Multiple groups are approaching adjacent problems (dynamics-aware PLMs, dynamics-based GNNs, conformational biasing)
- But NO group has published the specific combination: explicit ensembles from generative models -> quantitative function prediction at scale

**Estimated time until gap is filled by competitors:** 6-18 months. Multiple groups have the pieces. The first to combine them systematically wins.

---

## 6. Feasibility Reassessment

### 6.1 Strengths

1. **All tools are open-source:** BioEmu (MIT), AlphaFlow (MIT), Boltz-2 (open), ProteinGym (public)
2. **Data is abundant:** 2.7M DMS variants, 776K stability measurements, NMR data for validation
3. **Compute is manageable:** ~8,200 H200 GPU-hours total, achievable in weeks
4. **Concept is validated piecemeal:** DCIasym GNN shows dynamics improve fitness prediction; SeqDance shows dynamics-aware PLMs improve mutation prediction; distograms improve stability prediction
5. **Clear benchmark framework:** ProteinGym enables direct comparison against 50+ existing methods
6. **Hardware match:** H200 GPUs (141 GB VRAM) are ideally suited for BioEmu inference

### 6.2 Risks

1. **BioEmu mutation sensitivity:** Independent assessment found BioEmu struggles with mutation-induced conformational shifts. Mitigation: use ensemble statistics that are robust to per-sample noise; compare wild-type vs. mutant ensemble *distributions* rather than individual structures.

2. **Protein size bias:** BioEmu performs best on proteins <500 residues. Many ProteinGym proteins are larger. Mitigation: focus initial work on the ~100 ProteinGym proteins within BioEmu's sweet spot. Use AlphaFlow or Boltz-2 for larger proteins.

3. **Training data overlap:** Ensemble features may correlate with existing sequence/structure features. Risk of marginal improvement over simpler methods. Mitigation: demonstrate improvement specifically on proteins where sequence-based methods fail (IDPs, allosteric proteins, conformational switches).

4. **Generalization:** Model may overfit to specific protein families in ProteinGym. Mitigation: strict cross-validation with protein-family-level splits; evaluate on entirely held-out assays.

5. **Reviewer skepticism:** "Are the ensemble features just noisy versions of AlphaFold2 structural features?" Mitigation: ablation studies showing dynamics-specific features (RMSF, conformational state populations, correlated motions) contribute beyond static structure; validation against NMR-derived dynamics data.

6. **No wet-lab validation:** Purely computational. Mitigation: frame as computational benchmarking study; use existing experimental dynamics data (NMR, HDX-MS) for independent validation.

### 6.3 Feasibility Rating: 8/10

The project is technically feasible with available tools and data. Main risks are (a) demonstrating clear advantage over simpler methods, and (b) competition from well-resourced groups.

---

## 7. Publication Framing

### 7.1 Proposed Title

"Bridging Ensembles and Function: A General Framework for Predicting Mutation Effects from Protein Conformational Landscapes"

Alternative titles:
- "From Conformational Ensembles to Functional Predictions: Closing the Post-AlphaFold Gap"
- "DynFunc: Mapping AI-Generated Protein Ensembles to Biological Function at Proteome Scale"

### 7.2 Main Claim

Current mutation effect predictors achieve Spearman correlations of 0.45-0.52 on ProteinGym by relying on sequence and static structure information, systematically failing on proteins where function depends on conformational dynamics. We present DynFunc, the first general framework that maps explicit conformational ensemble properties -- generated by BioEmu, AlphaFlow, and Boltz-2 -- to quantitative functional readouts. DynFunc improves ProteinGym benchmark performance by X% overall and by Y% on dynamics-dependent proteins (allosteric enzymes, conformational switches, IDRs), demonstrating that the ensemble-to-function mapping is a critical missing layer in computational protein biology.

### 7.3 Key Figures

**Figure 1: Conceptual framework**
- Panel A: Current paradigm (sequence -> static structure -> function prediction) vs. proposed paradigm (sequence -> ensemble -> ensemble features -> function prediction)
- Panel B: Overview of the DynFunc pipeline: ensemble generation (BioEmu/AlphaFlow/Boltz-2) -> ensemble feature extraction -> graph neural network -> function prediction
- Panel C: Taxonomy of ensemble features (flexibility, conformational states, cryptic pockets, correlated motions)

**Figure 2: Ensemble generation at scale**
- Panel A: BioEmu/AlphaFlow/Boltz-2 ensemble quality vs. MD ground truth across ProteinGym proteins
- Panel B: Compute scaling: GPU-hours vs. protein count for ensemble generation
- Panel C: Ensemble feature distributions across protein families

**Figure 3: Benchmark results on ProteinGym**
- Panel A: Overall ProteinGym Spearman correlation compared to top 10 existing methods (AlphaMissense, ESM-1v, EVE, TranceptEVE, SaProt, GEMME, etc.)
- Panel B: Per-assay improvement, stratified by protein dynamics level (rigid vs. flexible vs. allosteric)
- Panel C: DynFunc shows largest improvement on dynamics-dependent proteins

**Figure 4: Ablation of ensemble features**
- Panel A: Contribution of each feature category (RMSF, distance distributions, conformational states, correlated motions)
- Panel B: Performance vs. ensemble size (100 vs. 1000 vs. 10000 conformations)
- Panel C: Which ensemble generator works best (BioEmu vs. AlphaFlow vs. Boltz-2)

**Figure 5: Dynamics-dependent case studies**
- Panel A: Allosteric enzyme where DynFunc succeeds and AlphaMissense fails
- Panel B: Conformational switch protein (e.g., kinase active/inactive transition)
- Panel C: IDP where ensemble properties predict DMS fitness

**Figure 6: Validation against experimental dynamics**
- Panel A: Predicted ensemble features vs. NMR order parameters (BMRB)
- Panel B: Predicted flexibility vs. HDX-MS exchange rates
- Panel C: Predicted Rg distributions vs. SAXS profiles

**Figure 7: Epistasis prediction**
- Panel A: Multi-mutant fitness prediction using ensemble features
- Panel B: Comparison with Ozkan DCIasym GNN on shared proteins
- Panel C: Ensemble-based epistasis captures non-additive dynamics effects

### 7.4 Target Venue

**Primary:** Nature Computational Science
- Scope match: Computational framework + benchmark + biological insight
- Impact match: First general ensemble-to-function predictor, addresses major post-AlphaFold gap
- Precedent: BioEmu was published in Science; ProteinGym in NeurIPS; this bridges both

**Backup venues:** Nature Methods (if framed more as method), Science (if combined with experimental validation collaboration), Nature Biotechnology (if enzyme engineering angle emphasized)

### 7.5 Reviewer Concerns (Anticipated)

1. **"Is the improvement significant?"** -- Must demonstrate clear, statistically significant improvement on ProteinGym. Target: >5% overall improvement in Spearman correlation; >15% improvement on dynamics-dependent subset.

2. **"Are you just adding noise?"** -- Ablation studies showing each ensemble feature category contributes. Control: compare against random ensemble features.

3. **"BioEmu ensembles are approximate. How do errors propagate?"** -- Compare ensembles from BioEmu, AlphaFlow, Boltz-2, and actual MD. Show robustness to ensemble quality.

4. **"Why not just use sequence-based methods?"** -- Show specific failure modes of sequence-based methods on dynamic proteins. Case studies of proteins where DynFunc succeeds and sequence methods fail.

5. **"No experimental validation."** -- Use existing NMR/HDX-MS/SAXS data as independent validation. The benchmark itself (ProteinGym DMS data) IS experimental ground truth.

6. **"Scalability?"** -- Demonstrate pipeline on 200 proteins. Show compute requirements are modest (weeks, not months).

---

## 8. Combined Project Design

### 8.1 Unified Vision: The Dynamics-to-Function Bridge

The two gaps merge naturally into a single coherent project:

**Gap 1 (Dynamics-to-Function Mapping)** provides the general framework architecture -- how to extract informative features from protein ensembles and map them to function.

**Gap 2 (Ensemble-Aware Mutation Effect Prediction)** provides the specific application and evaluation framework -- using ensemble features to improve DMS fitness prediction on ProteinGym.

Together, they create a project that:
1. Establishes the conceptual framework of ensemble-to-function mapping
2. Implements it concretely for mutation effect prediction
3. Benchmarks against the entire field on ProteinGym
4. Validates against experimental dynamics measurements
5. Demonstrates the general principle that dynamics information improves functional prediction

### 8.2 Project Timeline

**Month 1-2: Ensemble Generation Campaign**
- Set up BioEmu, AlphaFlow, Boltz-2 on HPC cluster
- Generate wild-type ensembles for all ~200 ProteinGym proteins with PDB structures
- Implement ensemble feature extraction pipeline (RMSF, distance distributions, conformational states, etc.)
- Benchmark ensemble quality against available MD simulations

**Month 2-3: Feature Engineering & Baseline Models**
- Extract comprehensive ensemble features for all proteins
- Train baseline models (ensemble statistics + XGBoost) on ProteinGym
- Compare against existing methods to identify where dynamics features help most
- Identify the subset of "dynamics-dependent" proteins

**Month 3-4: Graph Neural Network Development**
- Implement GNN architecture for ensemble-based function prediction
- Multi-task training (fitness + stability + dynamics validation)
- Hyperparameter optimization
- Cross-validation with protein-family-level splits

**Month 4-5: Variant-Specific Ensembles**
- Generate BioEmu ensembles for key mutant variants (top 50 proteins, 50 variants each)
- Compare wild-type vs. mutant ensemble statistics
- Train models incorporating variant-specific ensemble information
- Epistasis prediction experiments

**Month 5-6: Validation, Ablation, & Paper Writing**
- Comprehensive ablation studies
- Validation against NMR order parameters, HDX-MS, SAXS
- Case studies of dynamics-dependent proteins
- Comparison across ensemble generators
- Manuscript preparation

### 8.3 Risk Mitigation Strategy

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| BioEmu poor on variants | High | High | Use WT ensemble features + sequence change; compare generators |
| Marginal improvement | Medium | Critical | Focus on dynamics-dependent protein subset; multi-task learning |
| Competition publishes first | Medium | High | Rapid execution; unique angle of systematic ensemble features |
| Compute insufficient | Low | Medium | HPC cluster has ample resources; scale down if needed |
| Training data insufficient | Low | Medium | 2.7M DMS variants is substantial; augment with stability data |

### 8.4 Minimal Viable Experiment

If resources are constrained, the **minimal experiment** that still constitutes a publishable finding:

1. Generate BioEmu ensembles for the 50 ProteinGym proteins with both experimental structures AND known dynamics-function relationships
2. Extract per-residue RMSF and pairwise distance distributions as ensemble features
3. Train a simple MLP on ensemble features + ESM-2 embeddings to predict DMS fitness
4. Show improvement over ESM-2 alone on the dynamics-dependent protein subset
5. Validate ensemble flexibility against NMR B-factors

This minimal version takes ~4 weeks and ~500 GPU-hours. If successful, expand to the full project.

---

## 9. Updated Impact Scores

### Gap 1: Dynamics-to-Function Mapping

| Criterion | Round 1 Score | Round 2 Score | Rationale |
|-----------|--------------|--------------|-----------|
| Novelty | 8 | **9** | No existing framework; recent preprints confirm gap remains |
| Scientific Impact | 8 | **9** | Addresses the central post-AlphaFold challenge |
| Computational Feasibility | 8 | **8** | All tools open-source; compute is manageable |
| Timeline Feasibility | 7 | **7** | 6 months is tight but achievable for core results |
| Publication Potential (Nat. Comp. Sci.) | 8 | **9** | Perfect fit for venue; bridges two major communities |
| **Combined Score** | **8.0** | **8.4** | |

### Gap 2: Ensemble-Aware Mutation Effect Prediction

| Criterion | Round 1 Score | Round 2 Score | Rationale |
|-----------|--------------|--------------|-----------|
| Novelty | 8 | **8** | SeqDance/QDPR address adjacent space; explicit ensembles still novel |
| Scientific Impact | 8 | **8** | ProteinGym benchmark ensures visibility |
| Computational Feasibility | 8 | **9** | BioEmu MIT license; H200 compatibility confirmed |
| Timeline Feasibility | 7 | **8** | Well-defined benchmark; clear milestones |
| Publication Potential (Nat. Comp. Sci.) | 8 | **9** | Quantitative benchmark improvement is publishable |
| **Combined Score** | **8.0** | **8.4** | |

### Combined Project Gamma: Dynamics-to-Function Mapping

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Novelty | **9** | First systematic ensemble-to-function predictor |
| Scientific Impact | **9** | Addresses post-AlphaFold gap; unifies dynamics and function |
| Computational Feasibility | **8** | ~8,200 GPU-hours; all tools available |
| Timeline Feasibility | **7** | 6 months tight; core results achievable |
| Publication Potential | **9** | Perfect for Nature Computational Science |
| Competition Risk | **7** | Window open but narrowing; 6-18 month estimate |
| **Overall Score** | **8.5** | **Strongest candidate from protein dynamics domain** |

---

## References

1. Lewis, S., Hempel, T., Jimenez-Luna, J., Gastegger, M., Xie, Y., et al. (2025). Scalable emulation of protein equilibrium ensembles with generative deep learning. *Science*, 369, 270-278.

2. Notin, P., Kollasch, A.W., Ritter, D., van Niekerk, L., et al. (2023). ProteinGym: Large-Scale Benchmarks for Protein Fitness Prediction and Design. *NeurIPS Datasets and Benchmarks*.

3. Jing, B., Berger, B., & Jaakkola, T. (2024). AlphaFold Meets Flow Matching for Generating Protein Ensembles. *ICML 2024*.

4. Hou, Y. & Shen, Y. (2026). Protein Language Models Trained on Biophysical Dynamics Inform Mutation Effects. *PNAS*, 123(4).

5. Ozkan, S.B. (2025). A protein dynamics-based deep learning model enhances predictions of fitness and epistasis. *PNAS*, 122(42), e2502444122.

6. Burgin, T.E. (2025). Quantified Dynamics-Property Relationships: Data-Efficient Protein Engineering with Machine Learning of Protein Dynamics. *JCIM*, 65(21), 11979-11987.

7. Wohlwend, J., et al. (2025). Boltz-2: Towards Accurate and Efficient Binding Affinity Prediction. *bioRxiv*.

8. Tsuboyama, K., Dauparas, J., Chen, J., et al. (2023). Mega-scale experimental analysis of protein folding stability in biology and design. *Nature*, 620, 434-444.

9. Cheng, T., et al. (2025). Computational design of conformation-biasing mutations to alter protein functions. *Science*.

10. Lu, J., Chen, X., et al. (2025). Aligning Protein Conformation Ensemble Generation with Physical Feedback. *ICML 2025*.

11. Anishchenko, I., et al. (2025). Modeling protein-small molecule conformational ensembles with PLACER. *PNAS*.

12. Lee, B.H., Scaramozzino, D., Piticchio, S., Orellana, L. (2026). Mutation-induced reshaping of protein conformational dynamics revealed by a coarse-grained modeling framework. *bioRxiv*, 2026.03.29.715126.

13. von Bulow, S., Tesei, G., Lindorff-Larsen, K. (2025). Machine learning methods to study sequence-ensemble-function relationships in disordered proteins. *Curr. Opin. Struct. Biol.*.

14. Wayment-Steele, H.K., El Nesr, G., Hettiarachchi, R., Ovchinnikov, S., Kern, D. (2025). Learning millisecond protein dynamics from what is missing in NMR spectra. *bioRxiv*, 2025.03.19.642801.

15. Watson, J.L., et al. (2025). Deep learning-guided design of dynamic proteins. *Science*.

16. Learning Dynamic Protein Representations at Scale with Distograms. (2026). *bioRxiv*, 2026.01.29.702509.

17. DETANGO: Deconvolving mutation effects on protein stability and function with disentangled protein language models. (2026). *bioRxiv*, 2026.02.03.703560.

18. Accelerated sampling of protein dynamics using BioEmu augmented molecular simulation. (2026). *bioRxiv*, 2026.01.07.698041.

19. IDPForge: Deep Learning of Proteins with Global and Local Regions of Disorder. (2026). *bioRxiv*, 2026.03.25.714313.

20. Advancing Protein Ensemble Predictions Across the Order-Disorder Continuum. (2025). *bioRxiv*, 2025.10.18.680935.

21. Cheng, J., Novati, G., Pan, J., et al. (2023). Accurate proteome-wide missense variant effect prediction with AlphaMissense. *Science*, 381(6664), eadg7492.

22. Aryal, S., et al. (2025). Assessing the Performance of BioEmu in Understanding Protein Dynamics. *Int. J. Mol. Sci.*, 27(6), 2896.

23. Steering Conformational Sampling in Boltz-2 via Pair Representation Scaling. (2026). *bioRxiv*, 2026.01.23.701250.

24. Han, Y. et al. (2025). BioEmu: AI-Powered Revolution in Scalable Protein Dynamics Simulation. *J. Cell. Mol. Med.*.

25. Mukherjee, S., et al. (2025). Assessing variant effect predictors and disease mechanisms in intrinsically disordered proteins. *PLOS Computational Biology*.

26. FireProtDB 2.0: large-scale manually curated database of the protein stability data. (2025). *Nucleic Acids Research*.

27. EnsembleFlex: Protein structure ensemble analysis made easy. (2025). *Structure*.

28. Zheng, S., et al. (2024). Predicting equilibrium distributions for molecular systems with deep learning. *Nature Machine Intelligence*.
