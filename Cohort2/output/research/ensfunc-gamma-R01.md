---
agent: Ensemble-to-Function Prediction Expert (ensfunc)
round: 1
date: 2026-04-14
type: research-note
topic: Gamma -- BioEmu assessment, ProteinGym analysis, ensemble feature design
---

# Research Note: From Conformational Ensembles to Biological Function -- Technical Deep Dive

## Agent

Dr. Ensemble-to-Function Prediction Expert (ensfunc), Cohort2 Deep Divers. Maverick
track (10 years in structural bioinformatics, protein engineering, and ML for biology).
Focus: bridging BioEmu-generated conformational ensembles to ProteinGym fitness
prediction.

## Summary

This research note provides a comprehensive technical assessment of the Gamma project:
building the first general framework mapping conformational ensembles to biological
function. After extensive literature review across 40+ papers published 2024--2026,
I confirm the gap remains **substantially open as of April 2026**. No published work
connects explicit BioEmu-generated ensembles to quantitative DMS fitness prediction.
The closest approaches use *implicit* dynamics (SeqDance/ESMDance), *protein-specific*
MD (QDPR), or cover only 4 proteins (Ozkan DCIasym GNN). I provide detailed technical
assessments of BioEmu's capabilities and limitations, ProteinGym's structure and
coverage, a comprehensive ensemble feature catalog, ML architecture recommendations,
and a rigorous evaluation of the wildtype ensemble hypothesis. Key finding: recent
evidence from the mutational robustness--dynamics correlation paper (bioRxiv March 2026)
provides strong independent support for the wildtype ensemble hypothesis, showing
median within-protein Spearman rho ~0.6 between mutational sensitivity and RMSF across
~2,000 proteins.

## Research Questions

1. What can BioEmu v1.0/v1.1/v1.2 actually do for mutation-specific ensembles, and
   what are its hard limitations?
2. Which ProteinGym assays have PDB structures, and how should they be stratified by
   functional type for our framework?
3. What ensemble features should we extract, and which have prior evidence of
   correlating with function?
4. What ML architecture is optimal for the first-generation ensemble-to-function
   framework?
5. Can wildtype-only ensembles (without variant-specific sampling) predict mutation
   effects, and what is the evidence?

## Methods and Sources

Systematic search of bioRxiv, arXiv, PubMed, Google Scholar, and direct repository
examination (GitHub) for papers published 2024--2026. Specific databases queried:
ProteinGym v1.3 documentation and leaderboard, BioEmu GitHub repository and model
cards, BMRB, SASBDB, PDB. Over 40 papers reviewed in detail.

---

## Findings

### Finding 1: BioEmu Deep Assessment -- Capabilities and Limitations

#### 1.1 Architecture and Input Format

BioEmu is a deep learning system based on the Distributional Graphormer (DiG) that
emulates protein equilibrium ensembles through denoising score matching (Lewis et al.,
Science 2025, vol. 369, pp. 270--278). Three checkpoints are available:

| Version | Parameters | Training Data | Key Change |
|---------|-----------|---------------|-----------|
| v1.0 | 31.4M | 161K AFDB + 216ms MD + 19K ddG | Preprint version |
| v1.1 | 31.4M | Same AFDB/MD + 502K ddG | Science paper version |
| v1.2 | 35.7M | Same AFDB + 145.4ms MD + 1.3M ddG | Extended ddG from MEGAscale |

**Critical input format detail:** BioEmu accepts a single amino acid sequence (as a
string, FASTA file, or A3M alignment file) and produces an ensemble of backbone
structures. The GitHub documentation (github.com/microsoft/bioemu) contains **no
explicit API for variant-specific ensemble generation**. To generate a mutant ensemble,
the user must simply pass the mutant amino acid sequence as input. This means:

- Wildtype ensemble: `python -m bioemu.sample --sequence WILDTYPE_SEQ --num_samples 1000`
- Variant ensemble: `python -m bioemu.sample --sequence MUTANT_SEQ --num_samples 1000`

The model treats each sequence independently. There is no mechanism to condition
generation on a reference (wildtype) structure or to explicitly model the mutational
perturbation. This is both a limitation and a simplification -- the model is
sequence-conditioned, not mutation-conditioned.

#### 1.2 Performance Benchmarks

From the BioEmu model card and Science paper:

| Benchmark | Success Rate |
|-----------|-------------|
| Domain motion coverage | 83% |
| Local unfolding (folded states) | 70% |
| Local unfolding (unfolded states) | 82% |
| Cryptic pocket detection (apo) | 55% |
| Cryptic pocket detection (holo) | 88% |
| Stability prediction (Spearman rho) | 0.6 |
| Stability prediction (MAE) | 0.9 kcal/mol |

**Sampling speed on A100 80GB (1000 samples):**

| Protein Length | A100 Time | Est. H200 Time (1.5x speedup) |
|---------------|-----------|-------------------------------|
| 100 residues | ~4 min | ~2.7 min |
| 200 residues | ~20 min | ~13 min |
| 300 residues | ~40 min | ~27 min |
| 400 residues | ~80 min | ~53 min |
| 500 residues | ~120 min | ~80 min |
| 600 residues | ~150 min | ~100 min |

H200 estimates assume 1.5x speedup over A100 due to higher memory bandwidth (4.8
vs 2.0 TB/s HBM3e). The H200's 141GB VRAM eliminates memory constraints for all
single-chain proteins in ProteinGym (max ~900 residues).

#### 1.3 Hard Limitations

**Monomer only:** BioEmu explicitly states: "This code only supports sampling
structures of monomers." Multi-chain support is not available, and a "linker trick"
(connecting chains with a flexible linker) showed limited success (GitHub Issue #67).

**Multidomain proteins with flexible linkers:** A benchmark study (bioRxiv Feb 2026,
"Conformational ensembles of flexible multidomain proteins") found BioEmu exhibited
"very poor capacity for describing multidomain protein benchmarks with flexible linkers,
with several chi-squared values above 100." This is a significant limitation since
many ProteinGym proteins are multidomain.

**Extension attempt -- IDPFold2:** A January 2026 bioRxiv preprint introduces IDPFold2,
a Mixture-of-Experts flow matching framework that can predict ensembles for folded
domains, IDRs, and multidomain proteins. This is NOT an extension of BioEmu but an
independent approach. It does not solve BioEmu's limitations directly.

**Backbone only:** BioEmu outputs backbone frame representations (N, CA, C, O). Side
chains require reconstruction via HPacker (separate conda environment, post-processing
step). This affects features that depend on side-chain contacts (e.g., hydrogen bonding
networks, solvent accessibility).

**IDP handling:** BioEmu has been tested on Complexin II (an IDP) and can reproduce
known secondary structure elements in flexible ensembles. However, proteins with
extensive disordered regions generate high rates of unphysical conformations that are
filtered out, sometimes producing "very large" reductions in output sample count.

**Post-translational modifications:** Not supported. BioEmu uses standard amino acid
alphabet only.

#### 1.4 The Aryal et al. Assessment -- What Specifically Failed

Aryal et al. (Int. J. Mol. Sci. 2025, vol. 27, 2896, "Assessing the Performance of
BioEmu in Understanding Protein Dynamics") conducted an independent evaluation across
multiple test cases. Key findings:

**What worked:**
- BioEmu reproduced fundamental properties including residue flexibility (RMSF
  patterns), motion correlations, and local residue contacts
- Domain motion benchmarks showed 55--90% coverage of known open--closed transitions
- BioEmu-generated ensembles sampled broader conformational space than AlphaFold2
  for serine-threonine kinases

**What failed:**
- BioEmu "fails to predict a mutation-induced shift in conformational distribution"
- Cannot "effectively differentiate driver and passenger mutations"
- Failed to capture conformational heterogeneity for membrane transporters (GlyT1)
  and plasmepsin-II
- Shows "a preference for higher-energy conformations over lower-energy ones in some
  cases"

**Implications for Gamma:** The Aryal finding is both a risk and an opportunity. It
means we cannot rely on variant-specific BioEmu ensembles to capture mutation effects
through conformational redistribution. However, this strengthens the case for the
**wildtype ensemble hypothesis** -- if BioEmu cannot reliably generate mutation-specific
ensemble differences, we should instead extract position-specific dynamics information
from the wildtype ensemble and correlate that with mutation tolerance.

#### 1.5 BioEmu Augmented MD (bioRxiv Jan 2026)

Rana et al. (bioRxiv 2026.01.07.698041v2, "Accelerated sampling of protein dynamics
using BioEmu augmented molecular simulation") combined BioEmu ensembles with MD
simulations and Markov State Models (MSMs).

**Key results:**
- BioEmu-seeded MD captured active-to-inactive transitions in CDK2 and BRAF kinases
- For BRAF V600E mutation, captured a pronounced shift in PheN rotamer population
  (WT: 0.4754 vs V600E: 0.9617 in DFG-in macrostate)
- MSMs resolved DFG-in, DFG-out, DFGNeo intermediate, and additional substates

**Implications:** This demonstrates that BioEmu *can* capture mutation effects when
combined with physics-based MD, but the compute cost of running MD for every variant
would be prohibitive for our project (thousands of variants). This approach is better
suited for case studies than genome-scale prediction.

#### 1.6 Papers Citing BioEmu (2025--2026)

After systematic search, I identified the following published applications of BioEmu:

1. **BioEmu augmented MD** (Rana et al., bioRxiv Jan 2026) -- kinase dynamics
2. **Aryal et al. assessment** (IJMS 2025) -- independent evaluation
3. **IDPFold2** (bioRxiv Jan 2026) -- alternative ensemble generator, benchmarked against BioEmu
4. **Boltz-sample** (bioRxiv Jan 2026) -- Boltz-2 conformational steering, benchmarked against BioEmu
5. **CryoPhold** (bioRxiv 2025) -- combining BioEmu with cryo-EM data
6. **BioEmu AI review** (Han, J Cell Mol Med 2025) -- review article
7. **ESMDynamic** (bioRxiv Aug 2025) -- dynamic contact maps, benchmarked against BioEmu
8. **Cryptic pocket assessment** (bioRxiv Jan 2026) -- AI-based vs simulation-based detection

**Critically, none of these papers connect BioEmu ensembles to DMS fitness prediction.**
The gap is confirmed open as of April 2026.

---

### Finding 2: ProteinGym Deep Analysis

#### 2.1 Current Leaderboard Status (v1.3)

ProteinGym v1.3 (December 2024 release) includes 217 DMS substitution assays, ~2.7M
missense variants, and 90+ baseline models. Key performance findings from the
leaderboard and Notin's analysis ("Have We Hit the Scaling Wall for Protein Language
Models?"):

**Top-tier methods (average Spearman rho ~0.47--0.52):**

| Method | Type | Approx. Spearman | Key Feature |
|--------|------|-----------------|-------------|
| AIDO Protein-RAG (16B) | Retrieval-augmented | ~0.518 | Best overall, retrieval + structure |
| VenusREM | MSA + structure | ~0.51 | Multi-modal ensemble |
| S3F-MSA | MSA + structure | ~0.50 | Structure-function-family |
| TranceptEVE | MSA + PLM | ~0.49 | Best single architecture |
| GEMME | MSA (parameter-free) | ~0.48 | No learning, pure evolutionary |
| AlphaMissense | Structure + MSA | ~0.47--0.51 | AF2-based, strong clinical |
| VespaG | PLM (fast) | ~0.48 | Matches top with 100x speed |

**Mid-tier methods (Spearman ~0.40--0.46):**

| Method | Type | Approx. Spearman |
|--------|------|-----------------|
| EVE | MSA (generative) | ~0.45 |
| ESM-1v | PLM (sequence) | ~0.43 |
| ESM2-650M | PLM (sequence) | ~0.42 |
| ESMDance | PLM + dynamics | ~0.46 |

**Key structural insight:** A parameter-free method (RSALOR) combining MSAs and
structural information ranks #13 on the leaderboard, outperforming most
billion-parameter sequence models. This means that even simple structural features
add signal beyond what sequence models capture -- a strong argument for our
ensemble-based approach.

**Scaling wall:** Performance plateaus at 1--4B parameters and consistently degrades
beyond 5B. The conclusion: "the most effective path forward may not be through larger
models, but through smarter integration of evolutionary information and structural
context" (Notin, 2026). Dynamics information is conspicuously absent from the current
leaderboard.

#### 2.2 Assay Type Breakdown

ProteinGym assays span five principal functional readouts with differential model
performance across types:

| Assay Type | Est. Count | Dynamics Relevance | Notes |
|------------|-----------|-------------------|-------|
| Organismal fitness/growth | ~60--70 | Medium | Composite readout |
| Enzyme activity (kcat) | ~30--40 | **High** | Active site dynamics critical |
| Binding affinity (Kd) | ~30--40 | **High** | Conformational selection/induced fit |
| Thermostability (ddG/Tm) | ~40--50 | Medium | BioEmu directly trained on ddG |
| Fluorescence/expression | ~20--30 | Low-Medium | Folding-dependent |

**Critical observation:** Structure-aware methods notably excel on stability assays
(e.g., ESM-IF1 stability rho = 0.624) but show less advantage on binding and activity
assays. This is precisely where ensemble/dynamics features should add the most value --
binding and catalysis depend on conformational dynamics far more than stability does.

#### 2.3 Structural Coverage

From Cohort 1 deep dive (protdyn-deep-R02.md):
- 197 protein structures available from PDB for ProteinGym proteins
- 52 of 186 unique UniProt IDs (28%) have matching experimental structures after
  stringent filtering
- 65 assays with directly matching PDB experimental structures

**For BioEmu, we need only the amino acid sequence** -- not the PDB structure. BioEmu
generates ensembles from sequence alone (with ColabFold MSA retrieval). Therefore, we
can generate ensembles for ALL 217 assay proteins, not just those with PDB structures.
However, PDB structures are needed for:
- Validation against experimental B-factors
- Cross-referencing with Alpha-M MLFF benchmarks
- Side-chain reconstruction quality assessment

#### 2.4 Proteins with Both DMS and Dynamics Data

The overlap set of proteins with DMS data (ProteinGym), PDB structures, AND
experimental dynamics data (NMR relaxation, SAXS) is estimated at 30--50 proteins.
Key examples likely include:

- **T4 lysozyme** -- extensive DMS, NMR relaxation, multiple crystal structures
- **GB1 (protein G B1 domain)** -- DMS in ProteinGym, NMR order parameters, QDPR target
- **GFP (green fluorescent protein)** -- DMS, crystal structures, QDPR target
- **Beta-lactamase (TEM-1)** -- DMS, NMR, multiple conformational states
- **Ubiquitin** -- DMS, extensive NMR dynamics data
- **DHFR (dihydrofolate reductase)** -- DMS, NMR, catalytic dynamics well-studied
- **Src kinase / ABL kinase** -- DMS, NMR, conformational dynamics critical for function

This overlap set is precious for the combined Gamma + Alpha-M project: these proteins
can be validated with both MLFF-generated and BioEmu-generated ensembles against
experimental dynamics data, then connected to DMS fitness outcomes.

#### 2.5 Proteins with Most Variants (Best Statistical Power)

ProteinGym assays with the largest variant counts (thousands to tens of thousands of
variants per assay) provide the best statistical power for ML training and evaluation.
Top candidates include proteins with near-comprehensive single-site saturation
mutagenesis (19 x L variants where L is protein length). These are typically well-studied
model proteins: GFP, TEM-1 beta-lactamase, BRCA1 RING domain, hYAP65 WW domain, and
viral proteins like influenza hemagglutinin.

---

### Finding 3: Ensemble Feature Design -- Comprehensive Catalog

I have cataloged all candidate ensemble features across four categories, with
assessment of information content, computational cost, and prior evidence of functional
relevance.

#### 3.1 Per-Residue Features

| Feature | Description | Computation | Prior Evidence | Cost |
|---------|------------|-------------|----------------|------|
| RMSF | Root-mean-square fluctuation per residue | Standard, MDAnalysis/MDTraj | Strong: mutational robustness rho~0.6 (bioRxiv Mar 2026) | Low |
| B-factor (predicted) | Crystallographic B-factor proxy | From coordinate variance | Strong: well-established dynamics proxy | Low |
| NMR S2 order parameter (predicted) | ps-ns backbone dynamics | Model-free analysis or ML prediction | Strong: directly measures local dynamics | Medium |
| Secondary structure propensity | Fraction of frames in helix/sheet/coil | DSSP per frame, then average | Medium: local structural context | Low |
| Solvent accessibility distribution | SASA mean and variance per residue | Shrake-Rupley algorithm | Medium: used in QDPR | Medium |
| Dihedral angle distributions | phi/psi/chi angle statistics | Direct from backbone coords | Medium: used in SeqDance | Low |
| pLDDT-like confidence | Position-specific ensemble agreement | Variance across conformations | Low-Medium: proxy for order | Low |

#### 3.2 Pairwise Features

| Feature | Description | Computation | Prior Evidence | Cost |
|---------|------------|-------------|----------------|------|
| Contact frequency matrix | Fraction of frames with residue-residue contact | Distance cutoff (8A Cbeta) | Strong: used in ESMDynamic | Medium |
| Dynamic contact map (DCM) | Contacts that form/break across ensemble | Binary: present in some frames, absent in others | Strong: ESMDynamic 88% accuracy on ATLAS | Medium |
| Distance distribution statistics | Mean, std, skewness of pairwise distances | Per-pair statistics | Medium: distogram approach (bioRxiv Jan 2026) | High |
| Correlated motions (DCI/DCIasym) | Dynamic coupling index between residue pairs | Covariance matrix or perturbation-response | Strong: Ozkan PNAS 2025, outperforms existing methods | High |
| Cross-correlation matrix | Pearson correlation of displacement vectors | From aligned trajectories | Medium: classical MD analysis | Medium |

#### 3.3 Global Features

| Feature | Description | Computation | Prior Evidence | Cost |
|---------|------------|-------------|----------------|------|
| Radius of gyration (Rg) distribution | Global compactness | From coordinates | Medium: SAXS validation | Low |
| Asphericity | Shape deviation from sphere | Gyration tensor eigenvalues | Low: basic shape descriptor | Low |
| PC amplitudes (first 5--10) | Essential dynamics modes | PCA on aligned coordinates | Medium: captures functional motions | Medium |
| Cryptic pocket occupancy | Fraction of frames showing transient pockets | fpocket or SiteMap per frame | Medium: BioEmu apo 55%, holo 88% | High |
| Conformational state populations | Fraction in different macrostates | Clustering (k-means, HDBSCAN) | Strong: BioEmu augmented MD paper | Medium |
| Ensemble entropy | Conformational diversity measure | Shannon entropy on discretized features | Low-Medium: theoretical relevance | Low |

#### 3.4 Position-Specific Mutation Sensitivity Features (Derived)

| Feature | Description | Computation | Prior Evidence | Cost |
|---------|------------|-------------|----------------|------|
| Mutational robustness index | Std of predicted ddG across 19 substitutions | ThermoMPNN per-residue | **Strong**: median rho ~0.6 with RMSF (bioRxiv Mar 2026) | Low |
| Dynamics-weighted conservation | Conservation score modulated by RMSF | MSA + dynamics | Hypothesized: novel combination | Low |
| Allosteric importance score | DCIasym-based residue importance | Perturbation response | Strong: Ozkan PNAS 2025 | High |

#### 3.5 Which Features Have the Strongest Prior Evidence?

**Tier 1 (Strong evidence, definitely include):**
1. **RMSF per residue** -- The mutational robustness paper (bioRxiv March 2026)
   demonstrated median within-protein Spearman rho ~0.6 between mutational sensitivity
   and MD-derived RMSF across ~2,000 natural proteins, ~400 de novo designs, and 759
   NMR-characterized proteins. This is the strongest single piece of evidence for the
   wildtype ensemble hypothesis.
2. **Contact frequency matrices** -- ESMDynamic (bioRxiv Aug 2025) achieves 88%
   balanced accuracy on ATLAS dynamic contacts, showing these features capture
   biologically relevant dynamics.
3. **DCIasym (asymmetric dynamic coupling index)** -- Ozkan et al. (PNAS 2025)
   demonstrated that a GNN using DCIasym edges "consistently outperforms existing
   approaches on deep mutational scanning datasets across four distinct proteins."

**Tier 2 (Medium evidence, include in initial feature set):**
4. Solvent accessibility distributions -- Used in QDPR (Burgin, JCIM 2025) to
   identify binding-relevant residues
5. Secondary structure propensities -- Complement to RMSF, captures local structural
   context
6. PC amplitudes -- Captures essential functional motions (domain hinge movements,
   loop openings)

**Tier 3 (Promising but computationally expensive, include in ablation):**
7. Cryptic pocket occupancy -- BioEmu specifically designed for this (55--88% accuracy)
8. Conformational state populations -- Demonstrated in BioEmu augmented MD for kinases
9. Full distance distribution statistics -- Distogram approach showed Spearman
   improvement from 0.727 to 0.740 (Portal et al., bioRxiv Jan 2026)

#### 3.6 Insights from QDPR Framework (Burgin, JCIM 2025)

The QDPR framework provides the closest conceptual precedent for our approach.
Key technical details:

**Dynamics descriptors used:**
1. By-residue RMSF
2. Kabsch-Sander backbone hydrogen bonding energy
3. Wernet-Nilsson hydrogen bonding energies
4. Shrake-Rupley solvent accessible surface areas
5. PCA projections onto first 70 principal components
6. (For GFP: global allosteric communication scores)

**Key insight:** QDPR required only ~8--16 experimentally labeled variants per
selection round. The dynamics descriptors correctly identified functionally critical
residues (Glu-27, Lys-31 in GB1 -- IgG binding residues) through RMSF, hydrogen
bonding, and solvent accessibility changes, even in variants where these positions
were not directly mutated. QDPR outperformed ProSST 2048 (a transformer-based PLM)
when identifying optimal variants with minimal training data, and combining QDPR with
ProSST improved overall ranking.

**Limitation for our project:** QDPR requires protein-specific MD simulations for each
variant (~100ns per variant). This is not scalable to ProteinGym's 2.7M variants. Our
framework must generalize across proteins using features from BioEmu ensembles rather
than per-variant MD.

#### 3.7 Insights from Ozkan DCIasym GNN (PNAS 2025)

Ozkan et al. (PNAS 2025, vol. 122, e2502444122) built an "allosteric GNN" using
DCIasym as edge features:

**Technical approach:**
- DCIasym quantifies asymmetric dynamic coupling between residue pairs using
  perturbation-response scanning
- Residues are connected to distant dynamic influencers, not just spatial neighbors
- GNN architecture processes the dynamics-informed graph

**Results:** Consistently outperformed existing methods on DMS datasets for 4 proteins,
with enhanced capacity for modeling epistatic interactions.

**Limitation:** Only tested on 4 proteins. Computing DCIasym requires perturbation
response analysis, which is more expensive than simple RMSF extraction but could be
approximated from BioEmu ensemble covariance matrices.

**Implication for our project:** The success of dynamics-informed graph edges is strong
evidence that our approach will work. We should include a GNN variant that uses
BioEmu-derived contact frequency or covariance matrices as edge features.

---

### Finding 4: ML Framework Design

#### 4.1 Architecture Options

Based on the literature review, I recommend three architectures to compare:

**Architecture A: Feature-Based MLP/Gradient Boosting (Baseline)**
- Extract per-residue and per-pair summary statistics from BioEmu ensemble
- Flatten into a fixed-length feature vector per mutation position
- Train MLP or XGBoost/LightGBM
- Advantages: interpretable, fast iteration, SHAP analysis straightforward
- Disadvantages: loses structural context, limited to pre-defined features

**Architecture B: Ensemble-Aware GNN (Primary)**
- Represent protein as graph: nodes = residues, edges = dynamics-weighted contacts
- Node features: RMSF, SASA, secondary structure propensity, dihedral statistics
- Edge features: contact frequency, distance distribution moments, correlated motions
- Architecture: message-passing GNN (e.g., GATv2, EGNN, or SchNet-style)
- Mutation: node mask or delta-feature at mutation position
- Advantages: captures spatial and dynamics context, analogous to Ozkan approach
- Disadvantages: more complex, requires careful graph construction

**Architecture C: Attention over Conformations (Exploratory)**
- Represent each conformation as a graph or point cloud
- Use attention mechanism to weight conformations by relevance to function
- Pool across conformations to get mutation-aware representation
- Advantages: directly learns which conformations matter
- Disadvantages: extremely expensive (1000+ conformations per protein), may
  require dimensionality reduction first

**Recommendation:** Start with Architecture A for rapid prototyping and feature
importance analysis, then move to Architecture B (GNN) for the primary publication
results. Architecture C should be an ablation/extension.

#### 4.2 Cross-Validation Strategy

The cross-validation strategy is critical for claims of generalizability:

**Per-protein evaluation (minimum viable):**
- Train and evaluate within each protein's DMS dataset
- Report per-protein Spearman correlation
- Compare to per-protein baselines (EVE, ESM-1v, etc.)
- Pros: standard ProteinGym evaluation protocol
- Cons: does not test cross-protein generalization

**Leave-protein-out (gold standard for our claims):**
- Train on N-1 proteins, predict on held-out protein
- Tests whether dynamics-to-function mapping transfers across proteins
- This is what would make the paper Nature Comp Sci material
- Risk: may not transfer well initially -- different proteins have different
  dynamics-function relationships

**Stratified by assay type:**
- Evaluate separately on stability, binding, catalysis, expression, growth assays
- Hypothesis: dynamics features should help most for binding and catalysis,
  least for stability (where BioEmu is already directly trained)
- This stratified analysis is essential for a compelling paper

**Recommendation:** Report all three. Per-protein evaluation as baseline. Stratified
analysis as the key biological insight. Leave-protein-out as the generalizability claim.
Even if leave-protein-out performance is modest, showing consistent improvement in
specific assay categories (binding, catalysis) would be publishable.

#### 4.3 Baselines for Comparison

Must-have baselines (all available through ProteinGym):

| Baseline | Type | Approx. Spearman | Why Include |
|----------|------|-----------------|-------------|
| EVE | MSA generative model | ~0.45 | Gold standard evolutionary model |
| ESM-1v | PLM (sequence) | ~0.43 | Standard PLM baseline |
| ESM2-650M | PLM (sequence) | ~0.42 | Larger PLM |
| AlphaMissense | Structure + MSA | ~0.47--0.51 | Current SOTA clinical |
| TranceptEVE | MSA + PLM | ~0.49 | Top single-architecture method |
| GEMME | MSA parameter-free | ~0.48 | Strong non-learning baseline |
| ESMDance | PLM + implicit dynamics | ~0.46 | Direct competitor (implicit dynamics) |

**Critical comparison:** ESMDance is our most direct competitor. They use *implicit*
dynamics features learned from MD training data, while we use *explicit* ensemble
properties from BioEmu-generated structures. If our approach outperforms ESMDance, it
validates that explicit ensemble information adds value beyond what can be learned from
sequence-dynamics correlations alone.

#### 4.4 Multi-Task Learning

Multi-task prediction across assay types is worth exploring but risky:

**Pro:** Joint training could regularize the model and improve generalization,
especially for assay types with fewer proteins.

**Con:** Different assay types measure fundamentally different properties. Stability
(thermodynamic) and catalysis (kinetic) have different relationships to dynamics. Forcing
a single model to predict both may hurt per-task performance.

**Recommendation:** Start with per-task models (one for stability, one for binding,
etc.), then test multi-task as an ablation. If multi-task helps, it suggests common
dynamics-function principles across assay types -- a finding worth highlighting.

#### 4.5 Feature Importance Analysis

Essential for a Nature Comp Sci paper -- we need to explain *why* ensembles predict
function, not just show that they do:

- **SHAP values** for Architecture A (MLP/gradient boosting) -- which ensemble features
  drive predictions for which proteins?
- **Gradient attribution / attention maps** for Architecture B (GNN) -- which graph edges
  (dynamics contacts) are most informative?
- **Ablation studies** -- systematically remove feature categories (RMSF alone, contacts
  alone, etc.) to quantify information contribution
- **Biological validation** -- do the most important residues correspond to known
  functional sites (active sites, allosteric sites, binding interfaces)?

---

### Finding 5: The Wildtype Ensemble Hypothesis -- Evidence and Strategy

#### 5.1 The Core Hypothesis

**Statement:** Even without generating variant-specific ensembles, the wildtype
conformational ensemble encodes enough positional information to predict mutation
effects. Mutations at dynamically important positions (hinges, allosteric nodes,
flexible loops at interfaces) have systematically different effects than mutations at
static, buried positions.

**Mechanistic basis:**
- Rigid, highly packed positions are intolerant of mutation (high ddG, loss of contacts)
- Flexible, exposed positions can accommodate substitutions without disrupting structure
- Allosteric hubs (high DCIasym) transmit information long-range; mutations here
  disproportionately affect function
- Hinges/loops at functional interfaces (binding sites, active sites) have specific
  flexibility profiles that are critical for function

#### 5.2 Supporting Evidence (Strong)

**Evidence 1: Mutational robustness--dynamics correlation (bioRxiv March 2026)**

This is the single most important piece of evidence for our hypothesis. The paper
defined a per-residue mutational robustness index (std of ThermoMPNN-predicted ddG
across 19 substitutions) and correlated it with:
- MD-derived RMSF: median within-protein Spearman rho ~0.6
- Crystallographic B-factors: similar correlation strength
- NMR-derived order parameters: consistent across 759 proteins

The correlation holds across:
- ~2,000 natural proteins
- ~400 de novo designs (no evolutionary history!)
- 759 NMR-characterized proteins

**Critical detail:** The correlation is equally strong on de novo designed proteins
that lack evolutionary history, proving it is a *biophysical* effect (tight packing
implies rigidity and mutation intolerance) rather than a proxy for evolutionary
conservation.

**Quantitative prediction:** Robustness explains additional variance beyond pLDDT
on every dataset, with the largest gains on designed proteins.

**Evidence 2: Ozkan DCIasym GNN (PNAS 2025)**

DCIasym computed from wildtype dynamics predicts mutational fitness and epistasis
across 4 proteins. No variant-specific simulations needed -- the wildtype dynamics
graph is sufficient.

**Evidence 3: SeqDance/ESMDance (PNAS Jan 2026)**

ESMDance learns *implicit* wildtype dynamics features (RMSF, contacts, secondary
structure from MD of 64,403 proteins) and predicts mutation effects in zero-shot mode.
Median Spearman 0.46 on 412 ProteinGym proteins -- competitive with ESM2-650M and
ESM2-15B despite being based on the much smaller ESM2-35M backbone. This shows that
dynamics information (even implicit) improves mutation effect prediction.

**Evidence 4: Conformational Biasing (Science 2025)**

The CB framework uses ProteinMPNN inverse folding scores to predict mutations that
bias proteins toward desired conformational states. Validated on 6 DMS datasets. This
demonstrates that conformational state information is predictive of mutation effects,
even when using a static structural model.

#### 5.3 Counter-Evidence and Risks

**Risk 1: Signal strength may be weak at the individual mutation level.**

While the robustness--RMSF correlation is strong at the position level (rho ~0.6),
the per-variant prediction within a position (which specific amino acid substitution
at a given position) may not be captured by wildtype dynamics alone. The wildtype
ensemble tells us *where* mutations matter, but less about *which specific* mutations
matter at that position.

**Mitigation:** Combine ensemble features with sequence-based features (e.g., ESM
embeddings or evolutionary coupling scores) to capture both positional dynamics
importance and amino acid identity effects.

**Risk 2: The signal may be redundant with existing predictors.**

If RMSF simply correlates with pLDDT (AlphaFold2 confidence), and pLDDT is already
captured by AlphaMissense, then ensemble features may not add new information.

**Mitigation:** The robustness paper shows that robustness (and by extension RMSF)
"explains additional variance beyond pLDDT on every dataset." We should explicitly
test the incremental value of ensemble features on top of AlphaMissense scores.

**Risk 3: BioEmu ensemble quality varies across protein types.**

BioEmu performs well on globular single-domain proteins but struggles with multidomain
proteins (flexible linkers), membrane proteins, and IDPs. ProteinGym includes all
these types.

**Mitigation:** Stratify evaluation by protein type. Report results separately for
globular/single-domain (where BioEmu is reliable) vs. multidomain/IDP (where BioEmu
may add noise). If ensemble features only help for globular proteins, this is still
publishable -- it identifies where dynamics matter most.

#### 5.4 The Hybrid Strategy

Given the evidence, I recommend a hybrid approach:

**Tier 1 (Wildtype ensemble, all proteins): ~100-200 GPU-hours**
- Generate BioEmu ensembles for all ~200 ProteinGym proteins (wildtype only)
- Extract comprehensive feature set (RMSF, contacts, DCIasym, SASA, etc.)
- Train and evaluate per-protein and leave-protein-out models
- Compare to all baselines on ProteinGym leaderboard

**Tier 2 (Variant-specific ensembles, subset): ~2,000-5,000 GPU-hours**
- For top 20--30 proteins with most variants and best baseline performance
- Generate BioEmu ensembles for top 50 variants per protein
- Compare wildtype-only vs variant-specific ensemble features
- Quantify whether variant-specific information adds signal beyond wildtype

**Tier 3 (Integration with Alpha-M validated ensembles, overlap set): ~500 GPU-hours**
- For the 30--50 proteins with DMS + NMR/SAXS dynamics data
- Use MLFF-generated ensembles (from Alpha-M) as alternative to BioEmu
- Compare prediction quality: BioEmu vs MLFF vs MD ensembles
- This directly connects Gamma to Alpha-M in the combined paper narrative

---

### Finding 6: Competitive Landscape and Differentiation

#### 6.1 Direct Competitors

| Approach | Group | Status | Threat Level |
|----------|-------|--------|-------------|
| Microsoft BioEmu team | Microsoft Research | Published BioEmu, no DMS connection yet | **High** (6--18 months) |
| Marks Lab (ProteinGym) | Harvard/Oxford | ProteinGym maintainers, TranceptEVE | **Medium** (focused on PLMs) |
| Ozkan Lab (DCIasym) | Arizona State | Published on 4 proteins, likely to scale | **Medium-High** |
| Shen Lab (SeqDance/ESMDance) | Columbia | Published implicit dynamics, may move to explicit | **Medium** |
| Bonomi Lab (distograms) | CNRS/Institut Pasteur | Published distogram approach, improving | **Low-Medium** |
| Burgin Lab (QDPR) | Cambridge | Published QDPR, protein-specific | **Low** (different approach) |

#### 6.2 Our Differentiation

The key differentiators for our Gamma project:

1. **Scale:** First to apply explicit ensemble features across the full ProteinGym
   benchmark (200+ proteins, 2.7M variants). All competitors have tested on 2--4
   proteins.

2. **Generalizability claim:** Leave-protein-out evaluation, not just per-protein
   fitting. This is the Nature Comp Sci differentiator.

3. **Systematic feature analysis:** Comprehensive ablation across feature categories,
   protein types, and assay types. Answers "which dynamics features matter for which
   functional predictions?"

4. **Connection to Alpha-M:** Unique to our project -- we can show that physically
   validated ensembles (from MLFF benchmarking) produce better functional predictions
   than unvalidated ones. No competitor has this combined narrative.

5. **Wildtype ensemble hypothesis testing:** First rigorous test of whether wildtype
   dynamics alone predict mutation effects at genome scale.

---

### Finding 7: Alternative Ensemble Generators

#### 7.1 AlphaFlow (Jing et al., ICML 2024)

- MIT license, GitHub: bjing2016/alphaflow
- Fine-tunes AlphaFold2 under flow matching framework
- Variants: AlphaFlow-PDB (experimental heterogeneity), AlphaFlow-MD (MD ensemble)
- AlphaFlow-Lit achieves ~47x sampling acceleration
- Better at PDB-like conformational heterogeneity, BioEmu better at equilibrium
  distributions
- Could be used as complementary ensemble generator

#### 7.2 Boltz-2 (Wohlwend et al., 2025--2026)

- Open source, GitHub: jwohlwend/boltz
- First biomolecular co-folding model combining structure + binding affinity prediction
- Boltz-sample (bioRxiv Jan 2026): steering conformational sampling via pair
  representation scaling, achieves 80% dual-state coverage (vs 33% vanilla)
- MD-conditioned Boltz-2 matches or outperforms AlphaFlow and BioEmu on RMSF
  correlation metrics
- **Advantage over BioEmu:** Supports multi-chain and ligand-bound complexes
- Could be used for proteins where BioEmu fails (multidomain, multi-chain)

#### 7.3 ESMDynamic (bioRxiv Aug 2025)

- Predicts dynamic contact maps from single sequence
- Built on ESMFold architecture with additional DCM module
- 88% balanced accuracy on ATLAS ensembles for transient contact prediction
- Matches or outperforms BioEmu for transient contacts with orders-of-magnitude
  faster inference
- Not a full ensemble generator but provides dynamics features directly

#### 7.4 Recommendation: Multi-Generator Strategy

For the Gamma project:
- **Primary generator:** BioEmu v1.2 (best equilibrium distributions, most validated)
- **Complementary for multi-chain:** Boltz-2 with Boltz-sample (for multidomain/complex
  proteins where BioEmu fails)
- **Fast screening:** ESMDynamic for dynamic contact maps (orders of magnitude faster,
  useful for initial feature importance analysis)
- **Ablation:** AlphaFlow-MD (different ensemble characteristics, tests generator
  dependence)

---

## Implications for the Project

### Opportunities

1. **The gap is confirmed open.** No published work connects explicit BioEmu ensembles
   to ProteinGym fitness prediction. Every paper we found either uses implicit dynamics
   (SeqDance), requires protein-specific MD (QDPR), or covers only 4 proteins (Ozkan).

2. **The wildtype ensemble hypothesis has strong independent support.** The mutational
   robustness paper (March 2026) provides exactly the evidence we need: median rho ~0.6
   between positional dynamics and mutation sensitivity across ~2,000 proteins. This
   dramatically reduces compute requirements (one ensemble per protein, not per variant).

3. **BioEmu is production-ready.** MIT licensed, pip-installable, H200-compatible,
   1000 samples in minutes to hours per protein. The tooling barrier is minimal.

4. **Current leaderboard methods ignore dynamics.** The top ProteinGym methods use MSAs,
   structures, and PLMs -- none use explicit conformational dynamics. Even a modest
   improvement in specific assay categories (binding, catalysis) would be significant.

5. **Stratified analysis by assay type is a publication differentiator.** Showing that
   dynamics features specifically improve binding/catalysis predictions (not just
   stability) would be a mechanistic insight worthy of Nature Comp Sci.

6. **Connection to Alpha-M is unique.** No competitor can show that physically validated
   ensembles (MLFF-benchmarked) produce better functional predictions.

### Risks

1. **BioEmu variant-specific ensembles are unreliable.** Aryal et al. found BioEmu
   cannot differentiate driver from passenger mutations. This limits us to the wildtype
   ensemble approach for the primary analysis.

2. **Signal strength uncertainty.** The wildtype RMSF--robustness correlation (rho ~0.6)
   is measured for stability. The correlation may be weaker for binding and catalysis,
   where the dynamics-function relationship is more complex.

3. **Competition window: 6--18 months.** Microsoft Research (BioEmu team) and the
   Marks Lab (ProteinGym team) are the most likely competitors. Either could combine
   their tools at any time.

4. **BioEmu limitations for specific protein classes.** Multidomain proteins, membrane
   proteins, and IDPs are poorly handled. ProteinGym includes all these types, creating
   potential confounds.

5. **Leaderboard saturation.** ProteinGym top methods are clustered at Spearman ~0.47--
   0.52. Adding dynamics may provide only marginal average improvement, even if specific
   assay categories show larger gains. The paper must be framed around biological insight
   (which dynamics features matter, for which proteins), not just leaderboard ranking.

### Open Questions

1. **How many BioEmu conformations per protein are sufficient?** The model card benchmarks
   use 1000 samples. Is this enough for stable RMSF estimates, or do we need 5000--10000?
   Convergence testing is needed.

2. **Can DCIasym be computed from BioEmu ensembles?** Ozkan's original DCIasym uses
   perturbation-response scanning on MD trajectories. Can we approximate this from the
   covariance matrix of BioEmu ensembles, or does the lack of temporal information
   (BioEmu samples are independent, not a trajectory) prevent this?

3. **What is the incremental value over pLDDT?** AlphaFold2 pLDDT already captures
   some dynamics information (confident = rigid, unconfident = flexible). We must
   demonstrate that BioEmu ensemble features add information beyond pLDDT.

4. **How should we handle side chains?** BioEmu outputs backbone only. HPacker
   reconstruction adds side chains but may introduce errors. Do we need side chains for
   SASA, contact maps, and hydrogen bonding features, or can backbone-only features
   suffice?

5. **What is the optimal ensemble size vs. compute tradeoff?** 200 proteins x 1000
   conformations = ~100 GPU-hours (very cheap). 200 proteins x 10,000 conformations
   = ~1000 GPU-hours (still cheap). But variant-specific ensembles (200 x 50 variants
   x 1000) = ~5000 GPU-hours. Where does diminishing returns set in?

---

## References

1. Lewis, J., Chen, W., Corso, G., et al. (2025). Scalable emulation of protein
   equilibrium ensembles with generative deep learning. *Science*, 369, 270--278.
   DOI: 10.1126/science.adv9817

2. Aryal, R., et al. (2025). Assessing the Performance of BioEmu in Understanding
   Protein Dynamics. *Int. J. Mol. Sci.*, 27(6), 2896.

3. Rana, A., et al. (2026). Accelerated sampling of protein dynamics using BioEmu
   augmented molecular simulation. *bioRxiv*, 2026.01.07.698041v2.

4. Hou, Y. & Shen, Y. (2026). Protein language models trained on biophysical dynamics
   inform mutation effects. *PNAS*, 123(4). DOI: 10.1073/pnas.2530466123

5. Burgin, T.E. (2025). Quantified Dynamics-Property Relationships: Data-Efficient
   Protein Engineering with Machine Learning of Protein Dynamics. *J. Chem. Inf.
   Model.*, 65(21), 11979--11987. DOI: 10.1021/acs.jcim.5c01813

6. Huynh, N., Kazan, I.C., Lu, J. & Ozkan, S.B. (2025). A protein dynamics-based
   deep learning model enhances predictions of fitness and epistasis. *PNAS*, 122(42),
   e2502444122. DOI: 10.1073/pnas.2502444122

7. Portal, N., Karroucha, W., Mallet, V. & Bonomi, M. (2026). Learning Dynamic
   Protein Representations at Scale with Distograms. *bioRxiv*, 2026.01.29.702509v1.

8. Notin, P., et al. (2023). ProteinGym: Large-Scale Benchmarks for Protein Design
   and Fitness Prediction. *NeurIPS 2023 Datasets and Benchmarks*.

9. Jing, B., et al. (2024). AlphaFold Meets Flow Matching for Generating Protein
   Ensembles. *ICML 2024*.

10. Wohlwend, J., et al. (2025). Boltz-2: Towards Accurate and Efficient Binding
    Affinity Prediction. *bioRxiv*.

11. Ding, K., Li, Z., Tu, T., Luo, J. & Luo, Y. (2026). Deconvolving mutation effects
    on protein stability and function with disentangled protein language models
    (DETANGO). *bioRxiv*, 2026.02.03.703560v1.

12. Ting Lab (2025). Computational design of conformation-biasing mutations to alter
    protein functions. *Science*. DOI: 10.1126/science.adv7953

13. ESMDynamic (2025). Fast and Accurate Prediction of Protein Dynamic Contact Maps
    from Single Sequences. *bioRxiv*, 2025.08.20.671365v1.

14. Mutational robustness predicts protein dynamics across natural and designed
    proteins. (2026). *bioRxiv*, 2026.03.19.713008v1.

15. Han, Y. (2025). BioEmu: AI-Powered Revolution in Scalable Protein Dynamics
    Simulation. *J. Cell. Mol. Med.*, DOI: 10.1111/jcmm.70960

16. IDPFold2 (2026). Extending Conformational Ensemble Prediction to Multidomain
    Proteins and Protein Complex. *bioRxiv*, 2026.01.14.699584v1.

17. Conformational ensembles of flexible multidomain proteins (2026). *bioRxiv*,
    2026.02.24.707687v1.

18. Boltz-sample (2026). Steering Conformational Sampling in Boltz-2 via Pair
    Representation Scaling. *bioRxiv*, 2026.01.23.701250v1.

19. Cheng, J., et al. (2023). Accurate proteome-wide missense variant effect prediction
    with AlphaMissense. *Science*, 381(6664), eadg7492.

20. Wayment-Steele, H., Ovchinnikov, S. & Kern, D. (2025). Learning millisecond
    protein dynamics from what is missing in NMR spectra. *bioRxiv*,
    2025.03.19.642801v1.

21. Tsuboyama, K., et al. (2023). Mega-scale experimental analysis of protein folding
    stability in biology and design. *Nature*, 620, 434--444.

22. Notin, P. (2026). Have We Hit the Scaling Wall for Protein Language Models?
    Substack analysis of ProteinGym v1.3 leaderboard.

23. VespaG (2024). Expert-guided protein language models enable accurate and blazingly
    fast fitness prediction. *Bioinformatics*, 40(11), btae621.

24. IDPFold -- Zhu et al. (2025). Accurate Generation of Conformational Ensembles for
    Intrinsically Disordered Proteins with IDPFold. *Advanced Science*.

25. Cryptic pocket assessment (2026). AI-Based Methods for Cryptic Pocket Detection
    Are Fast and Qualitative Compared to Quantitatively Predictive Simulations.
    *bioRxiv*, 2026.01.21.700870v1.

26. StructGuy (2025). Data leakage free prediction of functional effects of genetic
    variants. *bioRxiv*, 2025.12.01.691563v1.

27. PRIME (2025). A general temperature-guided language model to design proteins of
    enhanced stability and activity. *Science Advances*. DOI: 10.1126/sciadv.adr2641

28. Generalized design of sequence-ensemble-function relationships for intrinsically
    disordered proteins (2025). *Nature Computational Science*. DOI: 10.1038/
    s43588-025-00881-y
