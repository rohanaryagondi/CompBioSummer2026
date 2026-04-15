---
agent: Ensemble-to-Function Prediction Expert (ensfunc)
round: 2
date: 2026-04-14
type: proposal
proposal_id: gamma-dynamics-function
---

# Proposal: Conformational Ensembles Predict Protein Function Beyond Sequence

## Proposing Agent

Dr. Ensemble-to-Function Prediction Expert (ensfunc), Cohort2 Deep Divers. Ten years
of experience in structural bioinformatics, protein engineering, and machine learning
for biology. Specialist in bridging conformational dynamics and functional prediction.
Champion of the wildtype ensemble hypothesis and systematic feature engineering for
interpretable dynamics-to-function mapping across the ProteinGym benchmark.

---

## Problem Statement

AlphaFold2 solved the protein structure prediction problem for static conformations,
but protein function depends fundamentally on dynamics: the ensemble of conformational
states a protein accesses under physiological conditions. Current mutation effect
predictors rely on evolutionary information (MSAs), static structures, or protein
language models -- none incorporate explicit conformational dynamics. The convergence
of two recent breakthroughs creates a unique opportunity: BioEmu (Lewis et al., Science
2025) generates equilibrium ensembles from sequence in minutes, and ProteinGym v1.3
(Notin et al., NeurIPS 2023) provides ground-truth fitness measurements for 2.7 million
variants across 217 proteins. Despite this, no published work bridges these resources.
The ProteinGym leaderboard (90+ methods as of April 2026) contains zero methods that
use explicit conformational ensemble features. This proposal fills that gap.

---

## Vision

After this project succeeds, the field will have:

1. **A validated framework** demonstrating that conformational ensemble features from
   generative models (BioEmu) systematically improve mutation effect prediction beyond
   sequence-only and static-structure methods, particularly for binding and catalytic
   function assays.

2. **A mechanistic understanding** of which dynamics features matter for which types of
   protein function -- answering the question "when does dynamics information improve
   functional prediction, and why?"

3. **An open benchmark entry** on the ProteinGym leaderboard incorporating dynamics
   features, establishing a new modality for the community to build upon.

4. **An integrated narrative** (with Alpha-M) showing that physically validated
   ensembles -- those whose dynamics properties match experimental NMR observables --
   produce better functional predictions than unvalidated ones.

Downstream users include protein engineers seeking to predict mutation effects for
therapeutic proteins, computational biologists designing enzyme variants, and the
broader ML-for-biology community developing next-generation variant effect predictors.

---

## Background and Evidence

### Current State of the Art

The ProteinGym v1.3 zero-shot DMS substitution benchmark (Notin et al., NeurIPS 2023;
v1.3 released April 2025) evaluates 90+ methods across 217 DMS assays with ~2.7M
missense variants. Top-tier methods achieve average Spearman rho in the range of
0.47--0.52:

| Method | Type | Approx. Spearman rho | Reference |
|--------|------|---------------------|-----------|
| AIDO Protein-RAG (16B) | Retrieval-augmented | ~0.518 | He et al., 2025 |
| VenusREM | MSA + structure | ~0.51 | Li et al., 2025 |
| S3F-MSA | MSA + structure | ~0.50 | -- |
| TranceptEVE | MSA + PLM | ~0.49 | Notin et al., 2022 |
| GEMME | MSA (parameter-free) | ~0.48 | Laine et al., 2019 |
| AlphaMissense | Structure + MSA | ~0.47--0.51 | Cheng et al., 2023 |
| ESMDance | PLM + implicit dynamics | ~0.46 | Hou et al., PNAS 2026 |
| EVE | MSA generative | ~0.45 | Frazer et al., 2021 |
| ESM-1v | PLM (sequence) | ~0.43 | Meier et al., 2021 |

**Critical observation:** These methods span MSA, structure, and PLM modalities, but
none uses explicit conformational ensemble features. Even ESMDance (Hou et al., PNAS
2026), the closest to our approach, uses *implicit* dynamics learned from MD training
data, not *explicit* ensemble properties computed from generated structures. There is
a well-documented performance plateau at 1--4B parameters (Notin, 2026 blog post),
suggesting that sequence scaling alone is insufficient and new modalities are needed.

**Assay-type performance gap:** Structure-aware methods excel on stability assays
(e.g., ESM-IF1 stability rho = 0.624) but show less advantage on binding and catalysis
assays. This is precisely where conformational dynamics should add the most value, since
binding and catalysis depend on conformational selection, induced fit, and active-site
dynamics far more than thermodynamic stability does.

### Recent Developments That Enable This

1. **BioEmu (Lewis et al., Science 2025, vol. 369, pp. 270--278):** First generative
   model to produce equilibrium protein ensembles at scale. MIT licensed, pip-installable
   (`pip install bioemu`), 35.7M parameters (v1.2), trained on 145.4ms MD simulations
   and 1.3M ddG measurements from MEGAscale. Generates 1000 backbone conformations in
   minutes (100 residues) to hours (600 residues) on a single GPU. Validated for domain
   motions (83% success), cryptic pocket detection (55--88%), and stability prediction
   (rho = 0.6, MAE = 0.9 kcal/mol).

2. **Mutational robustness--dynamics correlation (bioRxiv March 2026,
   doi:10.64898/2026.03.19.713008):** Systematic analysis across ~2,000 natural proteins,
   ~400 de novo designs, and 759 NMR-characterized proteins demonstrated median
   within-protein Spearman rho ~0.6 between per-residue mutational sensitivity (std of
   ThermoMPNN-predicted ddG across 19 substitutions) and RMSF from MD simulations. The
   correlation holds for de novo designed proteins lacking evolutionary history, proving
   it is a biophysical effect (tight packing implies rigidity and mutation intolerance)
   rather than a proxy for sequence conservation.

3. **eRMSF package (JCIM 2026, doi:10.1021/acs.jcim.5c02413):** Purpose-built Python
   package for ensemble-based RMSF analysis, explicitly supporting BioEmu-generated
   ensembles, AlphaFold2 subsampling, and MD trajectories. Provides the exact tooling
   we need for feature extraction.

4. **EnsembleFlex (Schneider et al., Structure 2025):** Computational suite for
   dual-scale (backbone and side-chain) flexibility analysis, PCA, UMAP, binding-site
   frequency mapping, and conserved water detection from protein ensemble data.

### Key Prior Work

1. **SeqDance/ESMDance (Hou, Zhao, and Shen, PNAS 2026, vol. 123, e2530466123):**
   PLMs trained on dynamic properties of 64,403 proteins. SeqDance (35M params) trained
   from scratch on MD/NMA-derived dynamics; ESMDance extends ESM2-35M with 1.2M
   trainable dynamics parameters. ESMDance achieves Spearman 0.53 on designed proteins
   (vs 0.02 for ESM2-35M) and ~0.25 on viral proteins (vs ~0.03). Tested on 412
   ProteinGym proteins, reporting median Spearman ~0.46. Predicts 23 dynamic properties
   including RMSF, SASA, secondary structure, dihedral angles, and pairwise correlations.
   **Key limitation:** Uses implicit dynamics learned during training, not explicit
   ensemble features from generated conformations.

2. **DCIasym allosteric GNN (Ozkan et al., PNAS 2025, vol. 122, e2502444122):**
   Dynamics-based GNN using the Asymmetric Dynamic Coupling Index as edge features.
   Outperforms existing methods on DMS datasets for 4 proteins without training on
   experimental epistasis data. **Key limitation:** Only 4 proteins tested; DCIasym
   requires perturbation-response analysis, more expensive than simple RMSF.

3. **QDPR framework (Burgin et al., JCIM 2025):** Quantified Dynamics-Property
   Relationships for protein engineering. Uses 6 dynamics descriptors (RMSF, H-bond
   energies, SASA, PCA projections) from per-variant MD simulations. Outperformed
   ProSST 2048 on GB1 and GFP with only 8--16 labeled variants. **Key limitation:**
   Requires protein-specific MD for each variant; not scalable to ProteinGym.

4. **Aryal et al. (Int. J. Mol. Sci. 2026, vol. 27, 2896):** Independent assessment
   of BioEmu. Confirmed: BioEmu reproduces RMSF patterns, motion correlations, and
   local contacts well. Confirmed limitation: BioEmu "fails to predict mutation-induced
   shifts in conformational distribution" and "cannot differentiate driver from passenger
   mutations." This validates our wildtype-focused strategy.

5. **BioEmu augmented MD (Rana et al., bioRxiv 2026.01.07.698041v2):** Combined BioEmu
   with MD and MSMs for kinase dynamics. Captured BRAF V600E mutation effects. Compute
   cost per variant prohibitive for genome-scale prediction.

6. **PocketMiner (Meller et al., Nature Comms 2023, vol. 14, 1177):** GVP-GNN for
   cryptic pocket prediction from single structures. ROC-AUC 0.87 on 39 experimentally
   confirmed cryptic pockets. Applied to human proteome showing >50% of "undruggable"
   proteins likely contain cryptic pockets.

7. **Conformational biasing (Lisanza et al., Science 2025):** Uses ProteinMPNN inverse
   folding scores to predict mutations that bias conformational states. Validated on 6
   DMS datasets. Demonstrates conformational state information is predictive of mutation
   effects.

8. **Boltz-2 MD ensembles (Wohlwend et al., 2025--2026):** MD-conditioned Boltz-2
   matches or outperforms BioEmu on RMSF correlation. Supports multi-chain and
   ligand-bound complexes. Alternative ensemble generator for proteins where BioEmu
   fails.

---

## Proposed Approach

### Overview

We build the first general framework mapping BioEmu-generated conformational ensembles
to deep mutational scanning fitness scores across the ProteinGym benchmark. The approach
proceeds in four stages: (1) generate wildtype BioEmu ensembles for ~200 ProteinGym
proteins, (2) extract 15 physically interpretable ensemble features per residue, (3)
train feature-based MLP and ensemble-aware GNN architectures under leave-protein-out
cross-validation, and (4) perform systematic ablation by feature category and assay
type. The wildtype ensemble hypothesis -- that positional dynamics properties of the
wildtype protein predict mutation tolerance without generating variant-specific
ensembles -- is the central claim. A variant-specific ensemble module on a subset of
50 proteins quantifies incremental signal from mutation-specific conformational changes.

### Method Details

#### Component 1: BioEmu Ensemble Generation Pipeline

**1.1 Input Preparation**

ProteinGym provides mutated_sequence fields for all ~2.7M variants. For each of the
217 DMS assays, we extract the wildtype sequence (first entry in each assay file).
Sequences are formatted as plain strings or single-sequence FASTA files.

```
# Pseudocode (document only -- no code files created)
# For each ProteinGym assay:
#   1. Parse CSV: extract wildtype sequence from reference
#   2. Write FASTA: >{UniProt_ID}_WT\n{sequence}
#   3. Queue for BioEmu sampling
```

**1.2 Wildtype Ensemble Generation (Tier 1: All Proteins)**

For each of the ~200 eligible ProteinGym proteins (excluding 17 with sequence length
>600 residues where BioEmu quality degrades):

- **Samples per protein:** 2,000 conformations (primary) + 500 additional for
  convergence check (total 2,500 generated, 2,000 retained for analysis)
- **Model version:** BioEmu v1.2 (extended MEGAscale training, best stability calibration)
- **Quality control filters:** Default BioEmu steric clash and chain break filters
  enabled. Post-filtering: remove conformations with >2 chain breaks or >5 steric
  clashes per 100 residues
- **Convergence criterion:** Compare RMSF profiles from first 1,000 vs. full 2,000
  samples. Require per-residue RMSF Pearson r > 0.95 between halves. If not met,
  generate additional 1,000 samples and re-evaluate
- **Output format:** PDB/XTC trajectory files per protein, stored in hierarchical
  directory structure

**Estimated generation times on H200 (per protein, 2,000 samples):**

| Protein Length | Est. H200 Time | Proteins in Range | Subtotal GPU-hrs |
|----------------|---------------|-------------------|-----------------|
| <150 residues | ~5 min | ~50 | ~4 |
| 150--300 residues | ~27 min | ~80 | ~36 |
| 300--450 residues | ~70 min | ~45 | ~53 |
| 450--600 residues | ~120 min | ~25 | ~50 |
| **Total Tier 1** | -- | **~200** | **~143 GPU-hrs** |

**1.3 Variant-Specific Ensemble Generation (Tier 2: 50 Proteins)**

For 50 high-priority proteins (selected by criteria in Component 3):

- **Variant selection:** 20 variants per protein spanning the fitness distribution
  (5 benign, 5 mildly deleterious, 5 moderately deleterious, 5 severely deleterious
  based on DMS scores)
- **Samples per variant:** 500 conformations
- **Total:** 50 proteins x 20 variants x 500 samples = 500,000 variant-specific
  conformations
- **Purpose:** Directly test whether variant-specific ensemble changes add predictive
  signal beyond wildtype dynamics
- **Known risk:** Aryal et al. (IJMS 2026) found BioEmu variant ensembles show
  "noise-like shifts rather than biologically meaningful changes." Negative results
  here strengthen the wildtype hypothesis narrative

**Estimated compute for Tier 2:**

| Component | GPU-hrs |
|-----------|---------|
| 50 proteins x 20 variants x 500 samples | ~1,500 |
| Quality control filtering and convergence | ~200 |
| **Total Tier 2** | **~1,700 GPU-hrs** |

**1.4 Handling Edge Cases**

- **Proteins >600 residues (17 proteins):** Exclude from primary analysis; include
  sequence-only baselines for these proteins as comparison set. Document as known
  limitation.
- **Multidomain proteins with flexible linkers:** Flag using domain assignment databases
  (Pfam/InterPro). For flagged proteins, generate 3,000 samples (50% more) to account
  for higher conformational heterogeneity. Report results separately for single-domain
  vs. multidomain.
- **Proteins without PDB structures:** BioEmu requires only sequence + MSA (ColabFold
  retrieval). No PDB structure needed for ensemble generation. PDB structures used
  only for post-hoc validation of ensemble quality (B-factor correlation).
- **IDPs (intrinsically disordered proteins):** Include but flag. BioEmu tested on
  Complexin II (IDP) with reasonable results, but high filtering rates expected.
  Monitor post-filter sample counts; require minimum 500 conformations after filtering.

**1.5 GPU Scheduling on H200**

- **Batch strategy:** Process proteins in length-sorted batches. Short proteins
  (<200 residues) run 4--8 per GPU in sequence. Longer proteins (>400 residues) run
  1 per GPU.
- **SLURM configuration:** Request 4 H200 GPUs per batch job; each GPU runs proteins
  sequentially. Estimated wall time: ~40 hours for full Tier 1 on 4 GPUs.
- **MSA retrieval:** ColabFold MSA searches run on CPU nodes before GPU sampling.
  Pre-compute all MSAs for 200 proteins in a single batch job (~4 hours on 16 CPU
  cores using MMseqs2).
- **Storage:** ~200 proteins x 2,000 conformations x ~50 KB/PDB = ~20 GB for Tier 1.
  Tier 2 adds ~12 GB. Total storage: ~35 GB.

#### Component 2: ProteinGym Protein Selection (Prioritized Tiers)

**2.1 Selection Criteria**

Proteins are scored on 5 criteria (each 0--2 points, max 10):
1. **Structural data quality** (2 = high-resolution X-ray + NMR dynamics; 1 = X-ray
   only; 0 = AlphaFold model only)
2. **Assay type diversity** (2 = binding or catalysis; 1 = growth or stability;
   0 = expression only)
3. **Variant count** (2 = >1000 variants; 1 = 200--1000; 0 = <200)
4. **Protein size** (2 = <300 residues; 1 = 300--500; 0 = >500)
5. **Alpha-M overlap** (2 = in bioval's NMR overlap set; 1 = has PDB + BMRB data;
   0 = sequence only)

**2.2 Tier 1: 50 High-Priority Proteins (Full Analysis)**

These receive wildtype ensembles, variant-specific ensembles (Tier 2 sampling),
full feature extraction, and all ML architectures. Selected for maximum statistical
power and biological interpretability.

**Candidate Tier 1 proteins (representative set):**

| Protein | UniProt | Length | DMS Assay Type | Variants | Alpha-M Overlap |
|---------|---------|--------|---------------|----------|----------------|
| Ubiquitin | P62988 | 76 | Stability/Growth | ~5,000+ | Yes (S2, shifts, J-couplings) |
| GB1 (Protein G B1) | P06654 | 56 | Stability | ~5,000+ | Yes (S2, 36 RDC sets) |
| T4 Lysozyme | P00720 | 164 | Activity | ~10,000+ | Yes (S2, shifts) |
| Barnase | P00648 | 110 | Activity | ~3,000+ | Yes (S2, methyl S2) |
| TEM-1 beta-lactamase | P62593 | 286 | Activity | ~5,000+ | No |
| GFP (avGFP) | P42212 | 238 | Fluorescence | ~50,000+ | No |
| BRCA1 RING domain | P38398 | ~110 | Growth | ~3,000+ | No |
| HIV Protease | P03366 | 99 | Activity | ~2,000+ | Yes (S2, flap dynamics) |
| Src kinase SH3 | P12931 | ~60 | Binding | ~1,000+ | No |
| hYAP65 WW domain | P46937 | ~38 | Binding/Stability | ~2,000+ | No |
| DHFR (E. coli) | P0ABQ4 | 159 | Activity | ~3,000+ | No |
| Alpha-synuclein | P37840 | 140 | Aggregation | ~1,000+ | Yes (IDP, SAXS, PRE) |
| p53 (DNA-binding) | P04637 | ~200 | Binding | ~2,000+ | Yes (shifts) |
| SNase | P00644 | 149 | Stability | ~3,000+ | Yes (S2, shifts, J-couplings) |
| Influenza HA | Various | ~330 | Growth | ~10,000+ | No |

Plus ~35 additional proteins meeting score >= 6/10 on criteria above.

**2.3 Tier 2: 100 Medium-Priority Proteins (Wildtype Ensemble Only)**

- Receive 2,000-conformation wildtype ensembles
- Full feature extraction (all 15 features)
- MLP and GNN evaluation under leave-protein-out CV
- No variant-specific ensembles

**2.4 Tier 3: Remaining ~50 Proteins (Sequence-Based Comparison)**

- No BioEmu ensemble generation (too long, multidomain, or low DMS quality)
- Serve as comparison set: sequence-only baselines evaluated here to ensure our
  results are not biased by protein selection
- Include all ProteinGym baselines for fair comparison

**2.5 The 8 Alpha-M Integration Proteins**

All are in Tier 1 (highest priority):

| Protein | NMR Observables | DMS Assay Type | Integration Test |
|---------|----------------|----------------|-----------------|
| Ubiquitin (1UBQ) | S2, 13C/15N shifts, J-couplings, RDCs | Stability | S2 agreement vs fitness prediction |
| GB1/GB3 (2OED) | S2, shifts, 36 RDC sets | Stability | Richest dynamics--function link |
| T4 Lysozyme (107L) | S2, shifts | Activity | Large mutant library, enzyme |
| Barnase (1BNR) | S2, methyl S2 | Activity | Enzyme catalysis focus |
| HIV Protease (2PC0) | S2, flap dynamics | Activity | Drug resistance mutations |
| Alpha-synuclein | Shifts, J-couplings, PRE, SAXS | Aggregation | IDP dynamics |
| p53 | Shifts | Binding | Cancer-relevant |
| SNase (1SNO) | S2, shifts, J-couplings | Stability | Classic folding model |

#### Component 3: Ensemble Feature Extraction (Top 15 Features)

All features are computed from the wildtype BioEmu ensemble (2,000 conformations) using
MDAnalysis v2.x, eRMSF, and custom analysis scripts built on established algorithms.

**3.1 Per-Residue Features (5 Features)**

| # | Feature | Computation Method | Tool | Prior Evidence | GPU-hrs/protein |
|---|---------|-------------------|------|----------------|-----------------|
| 1 | **RMSF** | Root-mean-square fluctuation of Ca atoms after alignment to mean structure | eRMSF / MDAnalysis RMSF module | **Strong:** rho ~0.6 with mutational sensitivity (bioRxiv Mar 2026) | <0.01 |
| 2 | **B-factor variance** | Variance of per-residue coordinate fluctuation across conformations, normalized by protein length | MDAnalysis, np.var | **Strong:** well-established dynamics proxy; correlates with crystallographic B-factors | <0.01 |
| 3 | **SASA distribution** (mean + std) | Per-residue solvent accessible surface area across ensemble, Shrake-Rupley algorithm (probe radius 1.4 A) | MDAnalysis.analysis.sasa or FreeSASA | **Medium:** used in QDPR (Burgin, JCIM 2025); identifies burial changes | <0.01 |
| 4 | **Secondary structure propensity** | Fraction of frames in helix, sheet, or coil per residue via DSSP | MDAnalysis + DSSP (mkdssp) | **Medium:** local structural context; used in SeqDance | 0.02 |
| 5 | **Backbone order parameter (S2, predicted)** | Lipari-Szabo S2 from Ca-C bond vector autocorrelation across ensemble | Custom: bond vector variance approach (Bremi and Ernst, 1997) | **Strong:** directly measures ps-ns dynamics; NMR gold standard | 0.01 |

**Encoding:** Each per-residue feature produces a single value at the mutation position.
For features with distributions (SASA), encode as [mean, std, skewness]. Total per-residue
feature vector per mutation: 5 base features expanded to 9 values.

**Normalization:** Z-score normalize within each protein (subtract protein mean, divide
by protein std) to remove protein-level baseline differences. This ensures the model
learns which *positions* within a protein are dynamically unusual, not whether one protein
is more flexible than another overall.

**3.2 Pairwise Features (5 Features)**

| # | Feature | Computation Method | Tool | Prior Evidence | GPU-hrs/protein |
|---|---------|-------------------|------|----------------|-----------------|
| 6 | **Contact frequency matrix** | Fraction of frames with Cb-Cb distance < 8 A between residue pairs | MDAnalysis contact analysis | **Strong:** ESMDynamic 88% accuracy on ATLAS contacts | 0.05 |
| 7 | **Distance distribution moments** | Mean, std, and kurtosis of pairwise Ca distances for mutation site to all other residues | MDAnalysis dist module | **Medium:** distogram approach (Portal et al., bioRxiv Jan 2026) improved rho by ~0.01 | 0.05 |
| 8 | **Correlated motions (MI)** | Mutual information between displacement vectors of Ca atoms; computed via covariance matrix diagonalization | MDAnalysis or custom numpy | **Strong:** DCIasym GNN outperformed baselines (Ozkan, PNAS 2025) | 0.10 |
| 9 | **Inter-domain distances** | For multidomain proteins: distance between domain centroids across ensemble | MDAnalysis center_of_mass per domain (Pfam annotation) | **Medium:** captures hinge dynamics; relevant for multidomain proteins | 0.01 |
| 10 | **H-bond persistence** | Fraction of frames maintaining backbone H-bonds at mutation site and neighbors (i to i+4 for helix, i to j for sheets) | MDAnalysis HydrogenBondAnalysis (backbone N-H...O=C only, since BioEmu outputs backbone) | **Medium:** used in QDPR; captures local stability | 0.03 |

**Encoding for GNN:** Contact frequency and correlated motions provide edge features
for the graph. At the mutation site: extract the local neighborhood (k=10 nearest
contacts by frequency) and encode the 10-dimensional contact profile + 10-dimensional
correlation profile. Total pairwise features per mutation: 25 values (for MLP) or
full graph edge features (for GNN).

**3.3 Global Features (5 Features)**

| # | Feature | Computation Method | Tool | Prior Evidence | GPU-hrs/protein |
|---|---------|-------------------|------|----------------|-----------------|
| 11 | **Rg distribution** | Mean and std of radius of gyration across ensemble | MDAnalysis Rg calculation | **Medium:** SAXS validation proxy; global compactness | <0.01 |
| 12 | **Asphericity** | Shape anisotropy from gyration tensor eigenvalues (l1, l2, l3): asphericity = l1 - 0.5*(l2+l3) | Custom numpy from inertia tensor | **Low:** basic shape descriptor; novel in this context | <0.01 |
| 13 | **PC amplitude ratios** | Variance explained by first 3 PCs from PCA on aligned Ca coordinates; ratio = PC1/(PC1+PC2+PC3) | MDAnalysis PCA or scikit-learn PCA | **Medium:** captures essential functional motions (domain hinges, loop openings) | 0.05 |
| 14 | **Cryptic pocket occupancy** | PocketMiner score at mutation site: probability of pocket formation from BioEmu-generated structures | PocketMiner GVP-GNN (Meller et al., NatComms 2023) applied to 20 representative conformations | **Medium:** BioEmu apo 55%, holo 88% detection; relevant for binding | 0.10 |
| 15 | **Surface flexibility index** | Product of SASA_mean and RMSF at mutation site, normalized; captures exposed flexible positions | Derived from features 1 and 3 | **Medium-Low:** composite feature; captures druggable/mutable surfaces | <0.01 |

**Encoding:** Global features are identical for all mutations within the same protein.
They provide context about overall protein dynamics that modulate the impact of local
mutations. Total global features per mutation: 7 values (Rg mean, Rg std, asphericity,
PC1 ratio, PC2 ratio, pocket score, surface flex).

**3.4 Feature Summary**

| Category | # Features | Values per Mutation | Compute/protein | Prior Evidence |
|----------|-----------|-------------------|-----------------|---------------|
| Per-residue | 5 | 9 | ~0.04 GPU-hrs | Strongest (RMSF) |
| Pairwise | 5 | 25 (MLP) / graph (GNN) | ~0.24 GPU-hrs | Strong (contacts, MI) |
| Global | 5 | 7 | ~0.16 GPU-hrs | Medium |
| **Total** | **15** | **41 (MLP)** | **~0.44 GPU-hrs** | -- |

Total feature extraction for 200 proteins: ~88 GPU-hrs.

**3.5 Feature Normalization and Encoding Strategy**

1. **Within-protein Z-score:** All per-residue and pairwise features are Z-scored
   within each protein. This removes protein-level differences (e.g., IDPs have higher
   global RMSF than globular proteins) and focuses the model on positional dynamics
   within each protein.

2. **Cross-protein scaling:** Global features are min-max scaled across the full
   protein dataset to [0, 1]. This allows the model to learn that globally compact
   proteins (low Rg) may respond differently to mutations than extended ones.

3. **Mutation identity encoding:** At the mutation position, we also include a 20-dim
   one-hot encoding of the wild-type amino acid and 20-dim of the mutant amino acid
   (total 40). This ensures the model can combine "what position" (dynamics) with
   "what change" (amino acid identity) information.

4. **Missing values:** For features that cannot be computed (e.g., inter-domain distance
   for single-domain proteins), encode as 0.0 with a binary indicator flag.

#### Component 4: ML Framework

**4.1 Stage 1: Statistical Baseline (No ML)**

Before any machine learning, establish the raw signal:

- **Per-protein RMSF-fitness correlation:** For each of the 200 proteins, compute
  Spearman rho between RMSF at the mutation position and the DMS fitness score.
  Aggregate as median across proteins.
- **Expected result:** Based on the mutational robustness paper (bioRxiv March 2026),
  we expect median per-protein rho of ~0.3--0.5 for stability assays (RMSF correlates
  with mutation tolerance) and potentially lower for binding/catalysis.
- **Interpretation:** If RMSF alone shows significant positive correlation (rho > 0.1)
  across >50% of proteins, the wildtype ensemble hypothesis is supported before any
  ML is applied.
- **Compute:** Negligible (minutes on CPU).

**4.2 Stage 2: Feature-Based MLP (Rapid Prototyping)**

**Architecture:**
- Input: 41-dimensional feature vector (9 per-residue + 25 pairwise + 7 global) +
  40-dim amino acid encoding = 81-dimensional input
- Hidden layers: [256, 128, 64] with ReLU activation and batch normalization
- Dropout: 0.3 per layer
- Output: 1 (predicted fitness score)
- Loss: MSE with L1 regularization (lambda = 0.01, tuned in inner CV)
- Optimizer: AdamW (lr=1e-3, weight decay=1e-4)
- Training: 200 epochs with early stopping (patience=20) on inner validation set

**Variant: Gradient Boosted Trees (XGBoost/LightGBM)**
- Same 81-dim input
- Hyperparameters tuned via inner CV: max_depth [3,5,7], n_estimators [100,500,1000],
  learning_rate [0.01, 0.05, 0.1], L1 regularization [0, 0.1, 1.0]
- Advantages: natively supports SHAP analysis; robust to small datasets

**4.3 Stage 3: Ensemble-Aware GNN (Primary Publication Architecture)**

**Graph Construction:**
- **Nodes:** Residues of the protein (N = protein length)
- **Node features (per residue):** [RMSF_z, B-factor_var_z, SASA_mean_z, SASA_std_z,
  SS_helix, SS_sheet, SS_coil, S2_pred, 20-dim AA one-hot] = 28-dim per node
- **Edges:** Connect residues with contact frequency > 0.1 (dynamic contacts from
  BioEmu ensemble). This creates a dynamics-informed graph distinct from the static
  distance-based graphs used by AlphaMissense.
- **Edge features:** [contact_frequency, distance_mean, distance_std, MI_score,
  H-bond_persistence] = 5-dim per edge
- **Mutation encoding:** Binary mask (1 at mutation position, 0 elsewhere) + mutant
  amino acid one-hot appended to node feature at mutation site

**Architecture:**
- 4-layer GATv2 (Graph Attention Network v2) with 8 attention heads per layer
- Hidden dimension: 128
- Edge feature integration: concatenate edge features with attention scores
  (Brody et al., ICLR 2022, modified for edge-attributed attention)
- Global readout: attention-weighted sum over all nodes + direct mutation-site
  node features (concatenated)
- Prediction head: MLP [256, 128, 1] with ReLU + batch norm + dropout (0.2)
- Loss: MSE + L2 regularization (weight decay=1e-4)
- Optimizer: AdamW (lr=5e-4, cosine annealing to 1e-6 over 100 epochs)
- Training: 100 epochs with early stopping (patience=15)

**Why GATv2 and not EGNN or SchNet:**
- We need edge-attributed message passing (contact frequency, MI as edge features).
  GATv2 with edge features is well-suited.
- SE(3)-equivariance (EGNN) is less critical here because we operate on covariance-
  derived features, not raw 3D coordinates.
- Ozkan et al. (PNAS 2025) demonstrated that dynamics-informed graph edges outperform
  static edges. Our approach generalizes this from 4 proteins to 200.

**4.4 Stage 4: Ensemble-Augmented Baselines (Integration)**

Combine ensemble features with existing top methods:

- **ESM2-650M + ensemble features:** Concatenate ESM2 per-residue embeddings (1280-dim)
  with our 9-dim per-residue ensemble features. Train MLP on combined representation.
- **AlphaMissense + ensemble delta:** Use AlphaMissense pathogenicity scores as a
  feature alongside ensemble features. Train simple linear combination or MLP.
- **TranceptEVE + ensemble features:** Same concatenation approach.

Purpose: Test whether ensemble features provide *additive* information beyond existing
modalities. If AlphaMissense + ensemble > AlphaMissense alone, dynamics adds signal
beyond static structure.

**4.5 Baselines to Beat**

All baselines available through ProteinGym precomputed scores:

| Baseline | Type | Approx. Spearman | Why Critical |
|----------|------|-----------------|-------------|
| AIDO Protein-RAG | Retrieval + structure | ~0.518 | Current SOTA |
| TranceptEVE | MSA + PLM | ~0.49 | Top single architecture |
| GEMME | MSA (parameter-free) | ~0.48 | Non-learning baseline |
| AlphaMissense | Structure + MSA | ~0.47--0.51 | Clinical gold standard |
| ESMDance | PLM + implicit dynamics | ~0.46 | Direct dynamics competitor |
| EVE | MSA generative | ~0.45 | Classic evolutionary model |
| ESM-1v | PLM (sequence) | ~0.43 | PLM baseline |
| RMSF-only (our Stage 1) | Single feature | ~0.3--0.5 (est.) | Our own minimal baseline |

**Success threshold:** The ensemble-aware GNN must achieve either:
(a) Higher average Spearman than ESMDance (~0.46) across all proteins, OR
(b) Win rate >55% against ESMDance in per-protein head-to-head comparison, OR
(c) Statistically significant improvement on binding + catalysis assay subsets even
if overall average is not SOTA

**4.6 Multi-Task Learning**

We test two training regimes:

- **Per-assay-type models:** Separate models for stability, binding, catalysis, growth,
  fluorescence, expression. Hypothesis: different assay types have different
  dynamics-function relationships.
- **Multi-task model:** Single model predicting fitness across all assay types, with
  assay-type ID as an additional categorical input. Hypothesis: common dynamics-function
  principles exist across types.

Compare per-assay-type vs. multi-task. If multi-task helps, it suggests universal
dynamics-function principles; if per-assay-type is better, it reveals assay-specific
biology.

#### Component 5: Cross-Validation Strategy

**5.1 Nested Leave-Protein-Out Cross-Validation**

The gold-standard evaluation protocol for claims of cross-protein generalizability:

**Outer loop (evaluation):**
- N = ~200 proteins (Tier 1 + Tier 2)
- Each fold: hold out 1 protein, train on remaining N-1
- Evaluate: Spearman rho on held-out protein
- Report: median, mean, and per-protein Spearman across all N folds

**Inner loop (hyperparameter tuning):**
- Within each outer training set (N-1 proteins): 5-fold protein-grouped CV
- Tune: learning rate, L1/L2 lambda, dropout rate, hidden dimensions, number of
  GNN layers, edge threshold
- Select best hyperparameters per outer fold

**Computational cost of nested CV:**
- Outer: ~200 folds x inner: 5 folds = ~1,000 model trainings
- Per training: ~5 min for MLP on CPU, ~15 min for GNN on GPU
- MLP total: ~83 CPU-hrs (trivial)
- GNN total: ~250 GPU-hrs

**5.2 Stratified Analysis by Assay Type**

Pre-specified stratification into 6 assay categories (following evalstat's
recommendation):

| Assay Category | Est. Proteins | Dynamics Hypothesis |
|---------------|--------------|-------------------|
| Thermostability (ddG/Tm) | ~40--50 | Moderate: RMSF correlates with packing; BioEmu directly trained on ddG |
| Binding affinity (Kd) | ~30--40 | **Strong:** conformational selection/induced fit drives binding |
| Enzyme catalysis (kcat) | ~30--40 | **Strong:** active site dynamics critical for catalysis |
| Organismal growth | ~60--70 | Moderate: composite readout, dynamics indirect |
| Fluorescence | ~15--20 | Moderate: folding-dependent, chromophore dynamics |
| Expression/abundance | ~10--15 | Weak: primarily folding/degradation |

**Primary hypothesis:** Ensemble features improve predictions most for binding and
catalysis assays (where dynamics are mechanistically important), moderately for
stability assays (partially captured by BioEmu's ddG training), and least for
expression assays (primarily sequence-determined).

**Statistical test:** For each assay type, paired Wilcoxon signed-rank test comparing
per-protein Spearman of ensemble method vs. best baseline. Bonferroni correction for
6 tests (p < 0.0083 for significance).

**5.3 Permutation Tests**

For each model:
- Shuffle DMS fitness labels 1,000 times (within each protein)
- Re-train and evaluate on shuffled data
- Compare actual performance to null distribution
- Report p-value: fraction of permutations achieving equal or better Spearman

This is essential given the overfitting risk with 15+ features on 187 proteins. The
permutation test establishes that our model captures real signal, not noise.

**Compute cost:** 1,000 permutation trainings x ~5 min = ~83 CPU-hrs (MLP) or ~250
GPU-hrs (GNN). Budget for MLP permutation tests only in the MVP; GNN permutation tests
if results warrant.

**5.4 Feature Importance Analysis**

Essential for mechanistic interpretation and publication impact:

1. **SHAP values (MLP/XGBoost):** TreeSHAP for gradient boosted trees; KernelSHAP
   for MLP. Compute per-feature importance across all mutations, stratified by assay
   type. Expected: RMSF and contact frequency dominate for stability; MI and pocket
   occupancy for binding.

2. **Attention analysis (GNN):** Extract GATv2 attention weights to identify which
   graph edges (dynamics contacts) are most informative for fitness prediction. Map
   to protein structure for visualization.

3. **Group ablation (all architectures):**
   - RMSF-only model (1 feature)
   - Per-residue only (5 features)
   - Per-residue + pairwise (10 features)
   - Full model (15 features)
   - Full model + amino acid identity (15 + 40)
   - Each feature ablated individually (15 ablation experiments)

4. **Biological validation of feature importance:** For top-10 most important positions
   per protein (by SHAP), check against known functional annotations:
   - Active site residues (UniProt annotation)
   - Allosteric sites (literature)
   - Binding interfaces (PDB complex structures)
   - If dynamics-important positions coincide with known functional sites at >2x random
     chance, this validates the biological interpretability of our model.

**5.5 Addressing the "Does Dynamics Help?" Question**

The central statistical test, pre-registered before experiments:

**Paired comparison (per protein):**
- For each protein i: compute delta_i = Spearman(ensemble_method, protein_i) -
  Spearman(best_baseline, protein_i)
- Across all N proteins: Wilcoxon signed-rank test on {delta_i}
- Report: median delta, IQR, number of proteins where ensemble wins vs. loses
- Win rate = fraction of proteins with delta_i > 0. Threshold: >55% (pre-specified
  per evalstat recommendation).

**Compute-matched comparison table (per evalstat):**
- Report Spearman improvement per GPU-hr invested
- Our method: ~8,200 GPU-hrs for ~0.02--0.05 improvement (estimated)
- ESMDance: ~10 GPU-hrs training (but 64,403 proteins of MD data for pretraining)
- Sequence baselines: minutes

This table is critical for reviewers who will ask "is the compute cost justified?"

#### Component 6: Integration with Alpha-M

**6.1 The 8 Overlap Proteins**

For each of the 8 proteins with both NMR dynamics data (from Alpha-M) and ProteinGym
DMS assays:

| Protein | Alpha-M Deliverable | Gamma Deliverable | Integration Test |
|---------|-------------------|-------------------|-----------------|
| Ubiquitin | S2 from MLFFs vs NMR | RMSF → fitness prediction | Do MLFFs with better S2 produce RMSF that better predicts fitness? |
| GB1/GB3 | S2, shifts, RDCs from MLFFs | RMSF → fitness prediction | Same, with richest NMR data |
| T4 Lysozyme | S2 from MLFFs | RMSF → activity prediction | Enzyme dynamics--catalysis link |
| Barnase | S2 from MLFFs | RMSF → activity prediction | Catalytic dynamics |
| HIV Protease | S2, flap dynamics | RMSF → activity prediction | Drug resistance mutations |
| Alpha-synuclein | Disorder parameters | RMSF → aggregation prediction | IDP dynamics |
| p53 | Chemical shifts | RMSF → binding prediction | Cancer mutations |
| SNase | S2, shifts, J-couplings | RMSF → stability prediction | Classic folding model |

**6.2 The Key Integration Question**

"Do ensemble generators that better reproduce experimental NMR observables also produce
ensembles that better predict protein function?"

**Experimental design:**
1. From Alpha-M: rank ensemble generators (BioEmu, MACE-OFF24, SO3LR, AI2BMD, AMBER
   ff19SB, CHARMM36m) by S2 order parameter agreement with NMR data (R^2 metric)
2. For the same 8 proteins: compute RMSF and ensemble features from each generator
3. Train separate Gamma models using ensembles from each generator
4. Compute per-protein fitness prediction Spearman for each generator
5. Correlate: S2 agreement rank vs. fitness prediction rank across generators

**Expected outcome:** Positive correlation would validate that ensemble physical
accuracy matters for functional prediction -- a finding neither project can make alone.

**Null hypothesis:** S2 agreement rank does not predict fitness prediction quality
(rho = 0). If confirmed, it means functional prediction is robust to ensemble quality
variations, which is also an interesting finding.

**Statistical power:** 8 proteins x 6 generators = 48 data points for rank correlation.
Sufficient for detecting strong effects (rho > 0.5) but not subtle ones.

### Data Requirements

| Dataset | Source | Size | Format | Access |
|---------|--------|------|--------|--------|
| ProteinGym v1.3 substitutions | proteingym.org / AWS | ~2 GB | CSV per assay | CC-BY 4.0, direct download |
| ProteinGym precomputed baselines | proteingym.org | ~500 MB | CSV | CC-BY 4.0 |
| BioEmu v1.2 model weights | PyPI / HuggingFace | ~3.5 GB | PyTorch | MIT license |
| AlphaFold2 weights (bundled) | Bundled with BioEmu | ~3.5 GB | JAX/TF | Apache 2.0 |
| ColabFold MSA database | MMseqs2 servers | API calls | A3M | Open |
| PDB structures (for 8 overlap proteins) | RCSB PDB | ~10 MB | PDB/CIF | Open |
| PocketMiner weights | GitHub | ~100 MB | PyTorch | MIT |
| SeqDance/ESMDance weights | HuggingFace | ~150 MB | PyTorch | GPL-3.0 |

### Compute Requirements

| Phase | Component | GPU-hrs | CPU-hrs | Storage |
|-------|-----------|---------|---------|---------|
| 1 | BioEmu Tier 1 (200 proteins, WT) | 143 | 50 (MSA) | 20 GB |
| 1 | BioEmu Tier 2 (50 proteins, variants) | 1,700 | 20 | 12 GB |
| 2 | Feature extraction (all) | 88 | 200 | 5 GB |
| 3 | MLP/XGBoost training + nested CV | 0 | 250 | 1 GB |
| 3 | GNN training + nested CV | 250 | 50 | 2 GB |
| 3 | Permutation tests (MLP) | 0 | 250 | 1 GB |
| 3 | Ensemble-augmented baselines | 50 | 100 | 1 GB |
| 4 | Feature importance (SHAP, ablation) | 100 | 200 | 2 GB |
| 4 | Alpha-M integration analysis | 200 | 50 | 5 GB |
| -- | Contingency (20%) | 506 | 234 | 10 GB |
| **Total** | -- | **3,037** | **1,404** | **59 GB** |

Note: The 8,200 GPU-hr estimate from Round 1 included generous contingency and
variant-specific ensembles. The refined estimate above (3,037 GPU-hrs including 20%
contingency) reflects tighter scoping. The difference is available for Alpha-M
integration and expanded variant-specific analysis if warranted.

### Implementation Timeline

| Phase | Duration | Deliverable | Dependencies |
|-------|----------|-------------|-------------|
| **Phase 1: Ensemble Generation** | Weeks 1--3 | 200 WT ensembles + 50 x 20 variant ensembles | BioEmu installed, SLURM jobs |
| **Phase 2: Feature Extraction** | Weeks 2--4 (overlaps Phase 1) | Feature matrices for all proteins | Completed ensembles (Tier 1 first) |
| **Phase 3: ML Training & CV** | Weeks 4--6 | MLP, XGBoost, GNN results with nested CV | Feature matrices complete |
| **Phase 4: Ablation & Integration** | Weeks 6--8 | Feature importance, assay-type analysis, Alpha-M integration | Phase 3 results + Alpha-M data |
| **Phase 5: Analysis & Figures** | Weeks 8--9 | Main figures, supplementary analysis, statistics | All experiments complete |
| **Phase 6: Writing** | Weeks 9--11 | Draft manuscript for Nature Comp Sci | Phase 5 complete |
| **Total** | **~11 weeks** | Submission-ready manuscript | -- |

**Critical path:** Phase 1 (ensemble generation) is the bottleneck. Feature extraction
can begin as soon as the first batch of ensembles completes. ML training cannot start
until at least 100 proteins have features extracted.

---

## Impact Assessment

### Publication Strategy

**Target venue:** Nature Computational Science

**Main claim:** Conformational ensemble features derived from BioEmu systematically
improve mutation effect prediction beyond sequence-only and static-structure methods,
with the largest improvements for binding and catalytic function assays, demonstrating
that protein dynamics encode functional information not captured by current approaches.

**Title options:**
1. "Conformational Ensembles Predict Protein Function Beyond Sequence"
2. "Dynamics-Informed Mutation Effect Prediction Across 200 Proteins"
3. "Wildtype Conformational Dynamics Predict Mutational Tolerance at Genome Scale"

**Expected reviewer concerns and pre-planned responses:**

| Concern | Response |
|---------|---------|
| "Compute cost is too high for ~0.03 Spearman improvement" | Present compute-matched comparison table; emphasize that we open a new modality (dynamics) not explored before; comparable methods (AlphaMissense) required far more compute for training |
| "BioEmu ensembles are not physically validated" | Point to Alpha-M integration: for 8 proteins, BioEmu RMSF validated against NMR S2; report correlation between ensemble quality and prediction quality |
| "Overfitting with 15 features on 200 proteins" | Nested leave-protein-out CV; permutation tests (p < 0.05); L1 regularization; group ablation shows signal persists in simplified models |
| "Improvement is only on specific assay types" | Stratified analysis is pre-specified; showing where dynamics helps (binding, catalysis) vs. where it does not (expression) is a finding, not a failure |
| "Why not use ESMDance (implicit dynamics)?" | Direct comparison included; explicit ensembles provide interpretable features (which positions, which dynamics modes matter) that implicit models cannot |
| "Leave-protein-out may show weak generalization" | Per-protein evaluation and win rate analysis supplement leave-protein-out; even modest cross-protein generalization + strong within-protein improvement is publishable |

**Comparison baselines:** AIDO Protein-RAG, TranceptEVE, GEMME, AlphaMissense,
ESMDance, EVE, ESM-1v, ESM2-650M (all available through ProteinGym precomputed scores).

**Negative result publishability:** If ensemble features do NOT improve predictions,
the paper becomes: "Why conformational ensembles fail to predict mutation effects:
a systematic analysis across 200 proteins" -- publishable in Bioinformatics or PLOS
Computational Biology. Key insights would include: (a) BioEmu ensemble quality is
insufficient for functional inference, (b) dynamics-function relationships are too
protein-specific to generalize, (c) sequence models already capture dynamics information
implicitly.

### Novelty Assessment

**Genuinely novel:**
1. First systematic connection of explicit BioEmu ensembles to ProteinGym fitness
   prediction (confirmed gap open as of April 2026)
2. First genome-scale test of the wildtype ensemble hypothesis (prior work limited to
   4 proteins maximum)
3. First stratified analysis showing differential dynamics-function relationships across
   assay types
4. First integration of ensemble physical accuracy (NMR validation) with functional
   prediction quality (combined Gamma + Alpha-M)

**Engineering of existing methods:**
- Feature extraction pipeline uses established tools (MDAnalysis, eRMSF, DSSP)
- ML architectures (MLP, GATv2, XGBoost) are standard
- Leave-protein-out CV is the standard ProteinGym protocol

### Broader Impact

This work establishes a new modality (conformational dynamics) for protein fitness
prediction, complementary to existing evolutionary (MSA) and structural (static
coordinates) modalities. If successful, it motivates:
- Integration of dynamics features into next-generation variant effect predictors
- Development of faster and more accurate ensemble generators optimized for functional
  prediction (not just structural accuracy)
- Systematic studies of dynamics-function relationships across protein families
- Therapeutic applications: prioritizing mutations in therapeutic proteins based on
  dynamics profiles

---

## Evaluation Plan

### Primary Metrics

1. **Average Spearman rho** across held-out proteins (leave-protein-out CV) --
   compared to all ProteinGym baselines
2. **Win rate** against best baseline per protein -- fraction of proteins where
   ensemble method achieves higher Spearman
3. **Stratified Spearman** by assay type (6 categories) -- identifies where dynamics
   helps most

### Baselines

All ProteinGym precomputed baselines (90+ methods), with focus on:
- ESMDance (direct dynamics competitor)
- AlphaMissense (structure-based SOTA)
- TranceptEVE (MSA+PLM SOTA)
- GEMME (non-learning baseline)
- Our RMSF-only statistical baseline (Stage 1)

### Ablation Studies

| Ablation | Tests | Expected Outcome |
|----------|-------|-----------------|
| RMSF-only vs. full 15 features | Information content of additional features | Full model > RMSF-only by ~0.02--0.05 |
| Per-residue only vs. + pairwise vs. + global | Value of structural context | Pairwise features add most for binding |
| Wildtype-only vs. wildtype + variant-specific | Added value of variant ensembles | Wildtype sufficient (Aryal finding) |
| BioEmu ensemble vs. AlphaFlow vs. Boltz-2 | Generator dependence | BioEmu best for stability, Boltz-2 for multidomain |
| MLP vs. XGBoost vs. GNN | Architecture sensitivity | GNN best overall, XGBoost best for interpretability |
| Ensemble features alone vs. ensemble + ESM2 | Complementarity with PLMs | Combination > either alone |
| Per-assay models vs. multi-task | Assay specificity vs. universality | Per-assay slightly better for binding/catalysis |

### Validation Strategy

**Computational validation only (no wet lab):**

1. **Internal consistency:** Leave-protein-out CV ensures predictions are on held-out
   proteins, preventing overfitting
2. **Permutation test:** Establishes that model signal exceeds chance (p < 0.05)
3. **Biological plausibility:** Top-contributing residues validated against known
   functional annotations (UniProt active sites, binding interfaces)
4. **Cross-generator validation:** Ensemble features from BioEmu vs. AlphaFlow vs.
   Boltz-2 tested on same proteins -- consistent improvement across generators
   indicates robustness
5. **NMR cross-validation (Alpha-M integration):** For 8 overlap proteins, BioEmu
   RMSF validated against experimental NMR S2 order parameters

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **BioEmu variant ensembles carry no signal** | High (Aryal evidence) | Medium | Wildtype hypothesis is primary; variant analysis is supplementary |
| **Wildtype RMSF--fitness correlation < 0.1 across most proteins** | Low (contradicted by March 2026 paper showing rho ~0.6) | **Critical** | Kill criterion: if rho < 0.1 for >50% of proteins by June 30, pivot to alternative generators or dynamics predictors |
| **Leave-protein-out shows no generalization** | Medium | High | Publish stratified per-protein analysis instead; negative generalization result is also informative |
| **Overfitting with 15 features / 200 proteins** | Medium | Medium | Nested CV, L1 regularization, permutation tests, RMSF-only baseline, group ablation |
| **BioEmu fails on multidomain/IDP proteins** | Medium-High | Low | Exclude from primary analysis; report separately; use Boltz-2 as alternative |
| **Competition: Microsoft or Marks Lab publishes first** | Low-Medium (6-12 months window; neither currently pursuing this) | High | Submit preprint by October 2026; our scale (200 proteins) and integration (Alpha-M) are hard to replicate quickly |
| **Ensemble features are redundant with pLDDT** | Medium | Medium | Explicit test: regress out pLDDT and show residual dynamics signal; March 2026 paper shows dynamics adds beyond pLDDT |
| **Feature extraction pipeline fails for some proteins** | Low | Low | Robust error handling; require 80% feature completeness per protein; exclude proteins with <80% |
| **GNN training unstable on small dataset** | Medium | Medium | Fallback to MLP/XGBoost; GNN is publication-optimal but not required |
| **Compute allocation delayed** | Low | Medium | Tier 1 ensemble generation needs only 143 GPU-hrs; can start immediately on minimal allocation |

### Kill Criteria (Pre-Specified)

1. **Kill Criterion 1 (June 30, 2026):** If RMSF at mutation position shows Spearman
   rho < 0.1 with DMS fitness across >50% of Tier 1 proteins (50 proteins), abort
   the wildtype hypothesis approach. Pivot to: (a) variant-specific ensemble focus,
   (b) alternative dynamics predictors (ESMDynamic, SeqDance), or (c) reconceive
   the project as a negative-result paper.

2. **Kill Criterion 2 (July 31, 2026):** If the best ML model (MLP or GNN) does not
   achieve win rate >45% against any single baseline in the top-5 on ProteinGym
   across the full protein set, scope down to assay-type-specific claims only. If
   no assay type shows significant improvement (Wilcoxon p > 0.05 after Bonferroni),
   write negative-result paper.

3. **Pivot Criterion (July 15, 2026):** If a preprint appears connecting BioEmu to
   ProteinGym fitness prediction before our submission, assess differentiation. If
   their analysis covers <50 proteins or lacks leave-protein-out CV, proceed with
   scale and rigor as differentiators. If comprehensive, pivot to integration angle
   (Gamma + Alpha-M combined narrative only).

---

## Open Questions

1. **Optimal number of BioEmu samples per protein:** We specified 2,000 based on
   convergence of RMSF, but contact frequency and MI may require more samples for
   convergence. Should we run a pilot study (5 proteins, 500/1000/2000/5000 samples)
   to determine the convergence profile for each feature type?

2. **Side-chain reconstruction for SASA and contacts:** BioEmu outputs backbone only.
   HPacker can reconstruct side chains but adds computation and potential noise. Should
   we use backbone-only contacts (Ca-Ca 8A) throughout, or invest in side-chain
   reconstruction for a subset? Initial recommendation: backbone-only for primary
   analysis; side-chain reconstruction as sensitivity test.

3. **Handling correlated features:** RMSF, B-factor variance, S2, and surface
   flexibility index are partially correlated. Should we use PCA on features before
   ML training, or rely on L1 regularization to select among correlated features?
   Recommendation: report both; L1 regularization is more interpretable.

4. **BioEmu v1.2 vs v1.1:** v1.2 uses extended MEGAscale ddG data (1.3M measurements).
   Does this make its ensembles biased toward stability-related dynamics? Should we
   compare v1.1 (502K ddG) and v1.2 to test for bias?

5. **Multi-mutant analysis:** ProteinGym includes some multi-mutant assays. Our feature
   extraction is designed for single-site mutations. Should we extend to double/triple
   mutants? Recommendation: defer to stretch goals; single-site is sufficient for the
   primary paper.

6. **Interaction with Alpha-M timeline:** The integration analysis (Component 6)
   depends on Alpha-M delivering MLFF ensemble data for 8 proteins. If Alpha-M is
   delayed, our standalone Gamma analysis is unaffected, but the combined narrative
   weakens. Should we pre-generate AMBER ff19SB ensembles for 8 proteins as a
   backup comparison?

---

## References

1. Lewis, M. et al. (2025). Scalable emulation of protein equilibrium ensembles with
   generative deep learning. *Science*, 369, 270--278.

2. Notin, P. et al. (2023). ProteinGym: Large-Scale Benchmarks for Protein Fitness
   Prediction and Design. *Advances in Neural Information Processing Systems (NeurIPS
   2023)*.

3. Hou, C., Zhao, H., and Shen, Y. (2026). Protein language models trained on
   biophysical dynamics inform mutation effects. *PNAS*, 123(4), e2530466123.

4. [Mutational robustness paper] (2026). Mutational Robustness Predicts Protein
   Dynamics Across Natural and Designed Proteins. *bioRxiv*, doi:10.64898/2026.03.19.
   713008.

5. Ozkan, S. et al. (2025). A protein dynamics-based deep learning model enhances
   predictions of fitness and epistasis. *PNAS*, 122, e2502444122.

6. Burgin, D. et al. (2025). Quantified Dynamics-Property Relationships: Data-Efficient
   Protein Engineering with Machine Learning of Protein Dynamics. *JCIM*.

7. Aryal, R. et al. (2026). Assessing the Performance of BioEmu in Understanding
   Protein Dynamics. *Int. J. Mol. Sci.*, 27(6), 2896.

8. Rana, M. et al. (2026). Accelerated sampling of protein dynamics using BioEmu
   augmented molecular simulation. *bioRxiv*, doi:10.64898/2026.01.07.698041v2.

9. Frazer, J. et al. (2021). Disease variant prediction with deep generative models
   of evolutionary data. *Nature*, 599, 91--95.

10. Meier, J. et al. (2021). Language models enable zero-shot prediction of the
    effects of mutations on protein function. *Advances in NeurIPS*.

11. Cheng, J. et al. (2023). Accurate proteome-wide missense variant effect prediction
    with AlphaMissense. *Science*, 381, 1303--1308.

12. Laine, E., Karami, Y., and Bhatt, T. (2019). GEMME: A Simple and Fast Global
    Epistatic Model Predicting Mutational Effects. *Mol. Biol. Evol.*, 36(11),
    2604--2619.

13. Meller, A. et al. (2023). Predicting locations of cryptic pockets from single
    protein structures using the PocketMiner graph neural network. *Nature Comms*,
    14, 1177.

14. Brody, S. et al. (2022). How Attentive are Graph Attention Networks? *ICLR 2022*.

15. Notin, P. (2026). Have We Hit the Scaling Wall for Protein Language Models?
    Blog post, Pascal Notin.

16. [eRMSF] (2026). eRMSF: A Python Package for Ensemble-Based RMSF Analysis of
    Biomolecular Systems. *JCIM*, doi:10.1021/acs.jcim.5c02413.

17. Schneider, M. et al. (2025). EnsembleFlex: Protein Structure Ensemble Analysis
    Made Easy. *Structure*.

18. Lisanza, S. et al. (2025). Computational design of conformation-biasing mutations
    to alter protein functions. *Science*.

19. Wohlwend, J. et al. (2025--2026). Boltz-2: Towards Accurate and Efficient Binding
    Affinity Prediction. *bioRxiv*.

20. Jing, B. et al. (2024). AlphaFold Meets Flow Matching for Generating Protein
    Ensembles. *ICML 2024*.

21. [IDPFold2] (2026). Extending Conformational Ensemble Prediction to Multidomain
    Proteins and Protein Complexes. *bioRxiv*, doi:10.64898/2026.01.14.699584.

22. [ESMDynamic] (2025). Predicting Dynamic Contact Maps from Single Sequence.
    *bioRxiv*.

23. Portal, M. et al. (2026). Conformational ensembles improve protein fitness
    prediction via distogram features. *bioRxiv*.

24. He, K. et al. (2025). AIDO Protein-RAG: Retrieval-Augmented Generation for
    Protein Fitness Prediction.

25. Kabsch, W. and Sander, C. (1983). Dictionary of protein secondary structure:
    pattern recognition of hydrogen-bonded and geometrical features. *Biopolymers*,
    22, 2577--2637.
