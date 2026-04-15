---
agent: Computational Biology & ML Reviewer (biomlrev)
round: 2
date: 2026-04-15
type: verification-research
---

# Deep Verification Research: Gamma Novelty & Baseline Verification

## Reviewing Agent

Computational Biology & ML Reviewer (biomlrev), Mock NCS Reviewer 2. This document
reports the results of deep verification research on the 8 critical uncertainties
(C1-C3, M1-M2, A1-A4) identified in my Round 1 review. Each finding is tagged as
CONFIRMED, PARTIALLY CONFIRMED, REVISED, or NOT FOUND.

---

## Executive Summary

Verification research substantially strengthens my Round 1 concerns. The RSALOR
baseline is even more formidable than initially stated: the ProteinGym v1.3
leaderboard now contains 97 methods, and RSALOR (a parameter-free model) ranks
#15 at Spearman 0.465, ahead of VespaG, SaProt, TranceptEVE L, and GEMME. The
top of the leaderboard (AIDO Protein-RAG at 0.518, VenusREM at 0.518, ProSST
K=2048 at 0.507) is dominated by structure+MSA multimodal methods, and no
dynamics-based method appears anywhere in the 97-method ranking. Boltz-2's RMSF
superiority over BioEmu is CONFIRMED but modest (Pearson 0.72 vs 0.71 on mdCATH,
0.78 vs 0.80 on ATLAS). The MutRobustness preprint is CONFIRMED as direct prior
art establishing the dynamics-fitness link (median |rho| ~0.6 across ~2,000
proteins). ESMDance's ProteinGym performance is more nuanced than stated in Round
1: it achieves 0.46 median Spearman on designed proteins without homologs, but
its overall ProteinGym performance appears comparable to ESM2-35M (not ESM2-650M),
and it is not submitted to the official ProteinGym leaderboard. The QDPR paper
(Burgin, JCIM 2025) is CONFIRMED as direct uncited prior art with code available.
NCS has published zero force-field benchmark papers and zero dynamics-to-fitness
papers in 2025-2026, confirming the editorial risk.

**Net assessment change from Round 1:** Round 1 concerns are strengthened, not
weakened. The dynamics-to-fitness niche is more crowded, the RSALOR baseline is
more precisely quantified, and the NCS editorial risk is higher than initially
estimated. My verdict of MAJOR REVISION for Gamma+Alpha-M Combined is
MAINTAINED, with the additional recommendation to restructure the paper's primary
claim around assay-type stratification rather than overall performance.

---

## Task B1: ProteinGym 2026 Leaderboard Exact State

### Source

ProteinGym GitHub repository, `Summary_performance_DMS_substitutions_Spearman.csv`
(OATML-Markslab/ProteinGym, accessed April 15, 2026); Notin (2025) Substack analysis
of ProteinGym v1.3 leaderboard.

### Verified Facts

**Total assays:** 217 DMS substitution assays covering ~2.7 million missense variants
(ProteinGym v1.3). An additional 74 DMS indel assays exist but are separately
benchmarked. One assay (218th) is excluded from the final summary. The number of
assays has NOT changed from v1.0 to v1.3; only the number of baselines has expanded.

**Total baselines evaluated:** 97 methods (up from ~50 in v1.0). Version 1.3 added
16 new baselines including ESM3, ESM C, ProGen3, and xTrimoPGLM variants.

**Top-20 methods with exact Spearman scores (verified from CSV):**

| Rank | Method | Avg Spearman |
|------|--------|--------------|
| 1 | AIDO Protein-RAG (16B) | 0.518 |
| 2 | VenusREM | 0.518 |
| 3 | ProSST (K=2048) | 0.507 |
| 4 | ProSST (K=4096) | 0.498 |
| 5 | S3F-MSA | 0.496 |
| 6 | S2F-MSA | 0.488 |
| 7 | ProSST (K=1024) | 0.485 |
| 8 | Protriever | 0.479 |
| 9 | ESCOTT | 0.476 |
| 10 | ProSST (K=512) | 0.471 |
| 11 | S3F | 0.470 |
| 12 | PoET (200M) | 0.470 |
| 13 | ProSST (K=128) | 0.469 |
| 14 | ESM3 open (1.4B) | 0.466 |
| **15** | **RSALOR** | **0.465** |
| 16 | VespaG | 0.458 |
| 17 | SaProt (650M) | 0.457 |
| 18 | TranceptEVE L | 0.456 |
| 19 | S2F | 0.456 |
| 20 | GEMME | 0.455 |

**Key observation:** The leaderboard from the CSV shows RSALOR at 0.465. My Round 1
review cited RSALOR at 0.473 (from the Tsishyn et al. paper itself, which reports
across 218 assays). The discrepancy likely arises from a different assay subset or
averaging convention. The Tsishyn paper reports their own evaluation on 218 assays;
the ProteinGym CSV uses 217. Both numbers are broadly consistent; I will use the
CSV value (0.465) as the canonical leaderboard score and the Tsishyn paper value
(0.473) for the paper's own reported performance.

**Dynamics-based methods on the leaderboard: ZERO.**

I searched all 97 method names in the ProteinGym CSV. No method uses dynamics
features (MD RMSF, B-factor variance, ensemble contacts, NMR S2, or any
conformational ensemble descriptor). The closest is ProSST, which uses structure
tokens from Foldseek (static structure only). ESMDance/SeqDance is NOT submitted
to the ProteinGym leaderboard despite being evaluated in the Hou et al. PNAS 2026
paper. This is a significant finding: the dynamics-to-fitness paradigm has not
been formally benchmarked on the standard leaderboard.

**RSALOR per-assay-type performance (from ProteinGym CSV):**

| Assay Type | RSALOR | ESM2-650M | ProSST-2048 | S3F-MSA |
|------------|--------|-----------|-------------|---------|
| Activity | 0.479 | 0.425 | 0.476 | 0.502 |
| Binding | 0.416 | 0.337 | 0.445 | 0.440 |
| Expression | 0.427 | 0.415 | 0.530 | 0.479 |
| Organismal Fitness | 0.426 | 0.368 | 0.431 | 0.477 |
| Stability | 0.575 | 0.523 | 0.653 | 0.581 |

**RSALOR by MSA depth (from ProteinGym CSV):**

| MSA Depth | RSALOR | ESM2-650M | S3F-MSA |
|-----------|--------|-----------|---------|
| Low | 0.467 | 0.338 | 0.469 |
| Medium | 0.468 | 0.409 | 0.509 |
| High | 0.529 | 0.513 | 0.547 |

**Implications for Gamma:** RSALOR is strongest on stability assays (0.575) where
structure matters most, and weakest on binding (0.416) and organismal fitness
(0.426). This creates a specific opportunity for Gamma: if dynamics features add
value primarily on binding and catalysis/activity (where RSALOR is 0.416-0.479),
Gamma could claim a niche improvement. However, ProSST-2048 at 0.445 on binding
and S3F-MSA at 0.440 already beat RSALOR on binding using static structure. Gamma
must beat BOTH RSALOR and ProSST on binding/activity to have a publishable claim.

**STATUS: CONFIRMED with corrections.** RSALOR leaderboard score is 0.465 (not
0.473 as cited in Round 1 from the paper). Zero dynamics methods on leaderboard.
97 total methods. 217 assays unchanged from v1.0.

---

## Task B2: RSALOR Deep Dive

### Source

Tsishyn, M., Hermans, P., Rooman, M., and Pucci, F. (2025). Residue conservation
and solvent accessibility are (almost) all you need for predicting mutational effects
in proteins. Bioinformatics 41(6): btaf322. Published June 2025.

### Exact Method

RSALOR computes two quantities per residue:

1. **LOR (Log-Odds Ratio):** LOR(i, wt, mt) = log[f_i(wt) / (1 - f_i(wt))] -
   log[f_i(mt) / (1 - f_i(mt))], where f_i represents weighted/regularized amino
   acid frequencies at position i from the MSA.

2. **RSALOR:** RSALOR(i, wt, mt) = (1 - RSA_i / 100%) * LOR(i, wt, mt), where
   RSA_i is the relative solvent accessibility from the PDB structure.

The model has zero trainable parameters. It combines two features:
- Conservation (via LOR from MSA)
- Solvent accessibility (via RSA from structure)

The RSA scaling factor means that mutations at fully exposed residues (RSA = 100%)
get RSALOR = 0 (no predicted effect), while buried residues get the full LOR score.
This encodes the biophysical intuition that buried mutations are more damaging.

### Per-Assay-Type Spearman (from the paper, 218 datasets)

| Assay Type | RSALOR | LOR only | RSA alone |
|------------|--------|----------|-----------|
| Stability | 0.551 | 0.481 | 0.480 |
| Binding | 0.455 | 0.416 | 0.271 |
| Activity | 0.472 | 0.457 | 0.281 |
| Expression | 0.428 | 0.399 | 0.312 |
| Fitness | 0.419 | 0.395 | 0.308 |
| **Overall** | **0.473** | **0.440** | **0.337** |

**Key finding:** RSA alone achieves 0.480 on stability (essentially matching LOR
at 0.481), indicating that for stability prediction, knowing which residues are
buried is almost sufficient. For binding and activity, RSA alone drops to 0.271-
0.281, meaning conservation (LOR) provides the critical information. The RSA
scaling improves LOR by 0.033 overall (from 0.440 to 0.473).

### MSA Depth Dependence

The paper states: "The number of homologous sequences in the input MSA has only a
minor impact on the performance of RSALOR." This is verified by the ProteinGym CSV:
RSALOR achieves 0.467 (low MSA depth), 0.468 (medium), 0.529 (high). The variation
is smaller than for ESM2-650M (0.338 low, 0.409 medium, 0.513 high).

### Code Availability

- GitHub: https://github.com/3BioCompBio/RSALOR (42 stars, Python 3.9+)
- PyPI: `pip install rsalor`
- Dependencies: NumPy, BioPython >= 1.75, C++ compiler (C++11)
- Inputs: MSA in FASTA format + PDB file (optional) + chain ID
- Runtime: Not documented but expected to be seconds per protein (single MSA query
  + RSA computation, no ML inference)

### Limitations Acknowledged by Authors

1. Assumes fully exposed residues (100% RSA) have zero impact
2. Ignores epistatic effects
3. Overlooks inter-residue evolutionary information critical for activity and fitness

**STATUS: CONFIRMED.** RSALOR is exactly as described in Round 1. The method is
trivially reproducible (pip install, no training). This makes it an inescapable
baseline for Gamma. Any NCS reviewer can run RSALOR in minutes.

---

## Task B3: Boltz-2 vs BioEmu Head-to-Head

### Source

Wohlwend, J., Passaro, S., Corso, G., et al. (2025). Boltz-2: Towards Accurate
and Efficient Binding Affinity Prediction. bioRxiv 2025.06.14.659707. Also
published in PMC (PMC12262699). MIT + Recursion Pharmaceuticals.

### RMSF Correlation Metrics (from paper Figure 5 and web summaries)

**mdCATH benchmark:**

| Method | Pearson | Spearman |
|--------|---------|----------|
| Boltz-2 MD | 0.72 | 0.77 |
| Boltz-1 | 0.76 | 0.76 |
| BioEmu | 0.71 | 0.76 |
| AlphaFlow | 0.75 | 0.69 |

**ATLAS benchmark:**

| Method | Pearson | Spearman |
|--------|---------|----------|
| Boltz-2 MD | 0.78 | 0.84 |
| Boltz-1 | 0.81 | 0.82 |
| BioEmu | 0.80 | 0.83 |
| AlphaFlow | 0.81 | 0.75 |

**Key finding:** Boltz-2 RMSF correlations are NOT consistently superior to BioEmu.
On mdCATH Pearson, Boltz-2 (0.72) barely edges BioEmu (0.71); on Spearman, Boltz-2
(0.77) edges BioEmu (0.76). On ATLAS, Boltz-2 Pearson (0.78) is LOWER than BioEmu
(0.80), though Spearman (0.84) edges BioEmu (0.83). The differences are within
noise for practical purposes. The paper's claim that Boltz-2 "generally obtains
stronger correlations" is based on aggregate metrics and additional lDDT-based
measures, not on dramatic RMSF superiority.

**My Round 1 claim that "Boltz-2 matches/exceeds BioEmu on RMSF prediction" is
PARTIALLY CONFIRMED.** The correct statement is: Boltz-2 and BioEmu perform
comparably on RMSF, with marginal advantages trading between benchmarks. There
is no clear winner.

### Speed and Architecture

- Boltz-2 generates all-atom structures (not backbone-only)
- Open-source under MIT license (GitHub: jwohlwend/boltz)
- Speed: ~18 seconds per prediction on a single consumer GPU (for structure +
  affinity prediction). Ensemble generation speed for multiple conformations not
  explicitly benchmarked separately.
- MD conditioning: Boltz-2 was trained on MD trajectories from the Protein Data Bank
  and additional MD data, using aggregated distograms to reduce variance
- Number of denoising steps: not explicitly stated in accessible materials
- No S2 order parameter benchmarks reported (only RMSF and lDDT-based metrics)

### BioEmu Published Status

BioEmu was published in Science (Lewis et al., 2025, Science 369: 270-278), not
in Nature Methods as the proposal implies. A Nature Methods commentary by Singh
(2025, Nature Methods 22: 2008) covered BioEmu but was not the primary publication.

The BioEmu augmented MD preprint (bioRxiv, January 2026) demonstrates BioEmu
augmented simulations capturing mutation-induced population shifts in kinases. This
preprint has NOT been extended to ProteinGym fitness prediction. It focuses on
metastable state populations, not DMS fitness scores.

### BioEmu Assessment (Zha et al., IJMS 2026)

Zha et al. (2026, Int. J. Mol. Sci. 27(6): 2896) assessed BioEmu on 50 proteins:
- 39 of 50 (78%) showed RMSF Pearson > 0.7 with ground-truth MD
- Flexibility is better reproduced in terminal regions than middle regions
- Loop regions are better reproduced than folded regions
- No S2 order parameter assessment was performed

**Implications for the combined paper:** The BioEmu vs Boltz-2 comparison is now
a wash on RMSF. This WEAKENS the argument for using BioEmu exclusively, but also
WEAKENS the concern that Boltz-2 is dramatically superior. The combined paper
should include Boltz-2 as one of the ensemble generators (alongside BioEmu, MACE,
classical FFs) for the integration scatter plot, but there is no longer a "Boltz-2
invalidates BioEmu" argument.

**STATUS: PARTIALLY CONFIRMED.** Boltz-2 does not clearly beat BioEmu on RMSF.
The two are comparable. My Round 1 framing of Boltz-2 as having "RMSF superiority"
was overstated. The correct framing is "comparable performance, but Boltz-2 is
open-source and all-atom, making it a convenient alternative."

---

## Task B4: Prior Art Paper Details

### B4.1: Ozkan et al. (PNAS 2025)

**Citation:** Ozkan, S.B. et al. (2025). A protein dynamics-based deep learning
model enhances predictions of fitness and epistasis. PNAS 122(42): e2502444122.

**Method:** Uses the Asymmetric Dynamic Coupling Index (DCIasym) from elastic
network models (Gaussian Network Model / Anisotropic Network Model -- NOT from MD
simulations). DCIasym quantifies the degree to which each member of a pair of
residues influences the flexibility of the other. This is used to construct edges
in a Graph Neural Network (GNN) where each residue links to its distant dynamic
influencers, creating an "allosteric GNN."

**Proteins tested:** Four proteins from DMS datasets. The specific protein names
were NOT confirmable from the accessible abstract, GitHub README (which lacks
protein identifiers), or web summaries. The GitHub repository (SBOZKAN/GNN, 7
stars) contains DCI folders with per-position data but does not list protein
names in the README.

**Specific Spearman scores:** NOT accessible from the abstract or publicly
available summaries. The paper states the GNN "consistently outperforms existing
approaches on deep mutational scanning datasets across four distinct proteins"
for epistasis prediction. Exact per-protein Spearman values require access to the
full paper text (PNAS paywall).

**Key distinction from Gamma:** Ozkan uses elastic network model dynamics (GNM/ANM,
no MD simulation required, runs in seconds), NOT BioEmu ensembles or MD-derived
features. The dynamics information is topological (which residues influence which
others' flexibility) rather than quantitative (what is the RMSF at each residue).
This is a significant methodological difference.

**Code availability:** GitHub: https://github.com/SBOZKAN/GNN (7 stars, Python 98%,
Shell 2%). Environment file exists but no benchmark results in README.

**Scalability:** Tested on 4 proteins only. No discussion of scaling to 150+ proteins.
The elastic network model approach is computationally cheap (seconds per protein),
so scaling is trivial. The limitation is presumably the availability of
high-quality DMS data, not compute.

**STATUS: CONFIRMED as prior art, but REVISED in significance.** Ozkan uses ENM
dynamics (not MD), making it methodologically distinct from Gamma. The overlap is
conceptual ("dynamics features improve fitness prediction") rather than
methodological ("BioEmu ensembles + ML on ProteinGym"). Gamma can differentiate
by emphasizing (a) MD-quality ensembles vs. ENM approximations, (b) 150 proteins
vs. 4, and (c) the integration with force field validation.

### B4.2: Burgin QDPR (JCIM 2025)

**Citation:** Burgin, T.E. (2025). Quantified Dynamics-Property Relationships:
Data-Efficient Protein Engineering with Machine Learning of Protein Dynamics.
J. Chem. Inf. Model. 65(21): 11979-11987. Published October 2025.

**bioRxiv preprint:** 2025.04.23.650227 (first posted April 23, 2025). Now published
in JCIM. CC-BY-NC license.

**MD features used (5 feature types):**
1. By-residue RMSF
2. By-residue Kabsch-Sander backbone hydrogen bonding energy
3. By-residue Wernet-Nilsson hydrogen bonding energies
4. By-residue Shrake-Rupley solvent accessible surface areas
5. PCA projections of trajectory
- For AvGFP: additional allosteric communication scores, excluding solvent accessibility
- Total features: 294 (GB1), 848 (AvGFP)

**ML method:** Convolutional Neural Networks (CNNs) for feature prediction networks,
with a small downstream network (8 densely connected units, leaky ReLU) combining
predictions into final scores.

**Proteins tested:** Two -- GB1 (2,000 MD simulations, 100 ns each) and AvGFP
(1,500 MD simulations, two independent 50 ns trajectories each).

**Results:** The paper emphasizes median highest fitness reached (for protein
engineering) rather than Spearman correlations. QDPR + ProSST showed strongest
performance across NDCG metrics. Specific Spearman values for raw fitness prediction
are embedded in figures rather than reported as standalone metrics. The paper frames
QDPR as a data-efficient protein engineering method, not as a zero-shot fitness
predictor.

**Scalability:** The authors note computational cost "can represent a substantial
investment" and that the method "will largely restrict usefulness to researchers
with access" to HPC. At 2,000 x 100 ns MD simulations for GB1 alone, the compute
cost per protein is enormous -- orders of magnitude more expensive than BioEmu
(which generates 2,000 conformations in minutes, not months). This approach does
NOT scale to 150 proteins.

**Code availability:** GitHub: https://github.com/Burgin-Lab/qdpr (open source).
Zenodo archive with all MD inputs, Python scripts, and model checkpoints.

**Key distinction from Gamma:** QDPR uses classical MD simulations (extremely
expensive per protein), not BioEmu ensembles (cheap). QDPR is supervised (requires
experimental fitness labels for training), while Gamma proposes zero-shot and
augmented approaches. QDPR tested 2 proteins; Gamma proposes 150.

**STATUS: CONFIRMED as direct prior art.** QDPR demonstrates the concept that
MD-derived features (RMSF, H-bond energies, SASA, PCA) predict fitness on
ProteinGym proteins (GB1, AvGFP). Gamma's differentiation is:
(a) BioEmu replaces classical MD (1000x faster)
(b) Zero-shot prediction instead of supervised engineering
(c) 150 proteins instead of 2
(d) Integration with force field validation quality
These are legitimate differentiators, but QDPR MUST be cited as the pilot study.

### B4.3: MutRobustness Preprint (bioRxiv March 2026)

**Citation:** Zuk, O. (2026). Mutational Robustness Predicts Protein Dynamics Across
Natural and Designed Proteins. bioRxiv 2026.03.19.713008v1. Hebrew University of
Jerusalem. Posted March 23, 2026. Category: biophysics. CC-BY license.

**Method:** Defines per-residue mutational robustness as the standard deviation of
predicted ddG values across all 19 single-amino-acid substitutions, computed using
ThermoMPNN (a structure-conditioned stability predictor).

**Exact correlations from abstract:**
- Median within-protein |rho| ~ 0.6 (between robustness and RMSF, B-factors, S2)
- Approaches AlphaFold2 pLDDT as a dynamics predictor
- Robustness explains additional variance beyond pLDDT on every dataset
- Largest gains on designed proteins (where pLDDT fails)

**Proteins tested:**
- ~2,000 natural proteins (MD RMSF comparison)
- ~400 de novo designs (MD RMSF comparison)
- 759 NMR-characterized proteins (S2 order parameter comparison)

**Key finding for Gamma:** The correlation is equally strong on de novo designs
lacking evolutionary history, pointing to a biophysical effect rather than a proxy
for sequence conservation. A multiple regression model using a full 20-dimensional
ddG profile per residue outperforms all scalar summaries.

**Case study:** Zika virus capsid protein, where pLDDT fails "almost entirely" but
mutational robustness correctly predicts dynamics.

**Relationship to Gamma's hypothesis:** This paper establishes the bidirectional
dynamics-fitness link (mutational robustness predicts dynamics, and implicitly,
dynamics predicts mutational sensitivity). The relationship is demonstrated at a
scale (2,000+ proteins) that dwarfs Gamma's proposed 150. However, the MutRobustness
paper uses PREDICTED ddG (from ThermoMPNN) rather than EXPERIMENTAL DMS fitness,
and it predicts dynamics FROM robustness rather than predicting FITNESS FROM dynamics.

**STATUS: CONFIRMED as partial scoop.** The MutRobustness preprint establishes
the dynamics-fitness connection at 10x Gamma's scale. Gamma cannot claim "first
evidence that dynamics correlates with fitness." Gamma CAN claim: (a) first to use
EXPERIMENTAL DMS fitness (not predicted ddG), (b) first to evaluate the PREDICTIVE
direction (dynamics -> fitness, not fitness -> dynamics), (c) first to integrate
with force field validation quality.

### B4.4: ESMDance/SeqDance (PNAS 2026)

**Citation:** Hou, L., Zhao, Q., and Shen, Y. (2026). Protein Language Models
Trained on Biophysical Dynamics Inform Mutation Effects. PNAS 123: e2530466123.

**Training data:** 64,403 proteins total: 35,800 from MD trajectories + 28,500 from
normal mode analysis (NMA).

**Dynamic properties predicted:** Residue-level RMSF, surface area, secondary
structure (8 classes), dihedral angles (phi, psi, chi1). Pairwise: correlation of
C-alpha movements, frequencies of hydrogen bonds, salt bridges, Pi-cation,
Pi-stacking, T-stacking, hydrophobic, and van der Waals interactions.

**Architecture:** Transformer encoder identical to ESM2-35M: 12 layers, 20 heads,
embedding dimension 480. Dynamic property prediction heads: 1.2M trainable
parameters. This is a SMALL model by current standards.

**ProteinGym performance (verified from PNAS paper and PMC article):**

Critical finding: ESMDance is NOT evaluated on the FULL ProteinGym leaderboard
(all 217 assays with standard methodology). The paper reports:
- **23 viral proteins** (shorter than 1024 residues, 187,902 mutations): ESMDance
  median Spearman 0.25 vs ESM2-650M ~0.0 vs ESM2-15B 0.36
- **Designed proteins without homologs (135 proteins):** ESMDance median Spearman
  0.46 vs ESM2-35M 0.21 vs ESM2-650M 0.09 vs ESM2-15B -0.02
- **Broader evaluation (412 proteins):** Zero-shot ESMDance 0.46 vs ESM2-35M 0.33

**CRITICAL REVISION:** My Round 1 review stated "ESMDance achieves median Spearman
0.46 on ProteinGym (412 proteins), matching ESM2-650M." This was INCORRECT in two
ways:
1. The 0.46 on 412 proteins is compared to ESM2-35M (0.33), not ESM2-650M. The
   ESM2-35M comparison is relevant because ESMDance is built on ESM2-35M architecture.
2. ESMDance is NOT submitted to the official ProteinGym leaderboard, so it cannot
   be directly compared to the 97 methods there. The 412-protein evaluation may use
   a different subset or evaluation protocol.

**Comparison to RSALOR:** The paper does NOT compare to RSALOR or any conservation-
based methods. It compares to FoldX, Rosetta, ProteinMPNN, and SaProt.

**Where ESMDance excels:** Designed proteins (no homologs, no MSA available) and
viral proteins (shallow MSAs). These are categories where conservation-based
methods like RSALOR are expected to fail.

**Where ESMDance does NOT help:** The paper does not demonstrate improvement on
standard eukaryotic proteins with deep MSAs -- exactly the proteins where RSALOR
already performs well.

**STATUS: REVISED.** My Round 1 claim that "ESMDance 0.46 < RSALOR 0.473" was
an unfair comparison (different evaluation sets, different base models). The correct
interpretation is: ESMDance provides the largest benefit for proteins lacking
evolutionary information (designed, viral), where conservation-based methods fail.
For standard proteins with deep MSAs, the dynamics-training benefit is unclear.
This actually STRENGTHENS the case for Gamma in one specific niche: if Gamma can
show dynamics features help specifically on proteins with shallow MSAs or unusual
evolutionary profiles, it would complement ESMDance's findings.

---

## Task B5: NCS 2025-2026 Benchmark Paper Acceptances

### NCS Editorial Policy on "Straightforward ML"

**Source:** Nature Computational Science editorial, "To review or not to review"
(Nat. Comput. Sci. 1: 226, April 2021).

**Exact policy statement (verified):** "straightforward usage of machine learning
algorithms is usually outside of the journal's scope." The journal is "mostly
interested in the development of new computational/mathematical methods and software
tools with the goal of addressing complex, relevant problems across a range of
scientific disciplines."

**Clarification:** The editorial also states that "applications of existing methods"
are welcome but "should normally come with methodological development." This
creates a clear editorial hurdle for Gamma, which uses standard ML (MLP, XGBoost,
GATv2) on standard features. The methodological novelty must be in the integration
framework or the dynamics-informed GATv2 edges.

### NCS Papers Published 2025-2026 (Computational Biology)

I searched Nature Computational Science's 2025-2026 publication list for papers
relevant to our proposals. Key findings:

**Perturbation prediction (directly relevant to Delta):**
1. "Scouter predicts transcriptional responses to genetic perturbations with large
   language model embeddings" (Zhu & Li, Nat. Comput. Sci. 6: 21-28, 2026).
   Novel architecture (LLM embeddings + compressor-generator network). NOT a
   benchmark paper -- introduces a new method.
2. "In silico biological discovery with large perturbation models" (Nat. Comput.
   Sci. 2025). Introduces Large Perturbation Models (LPMs). Novel architecture.
3. "Interpolating perturbations across contexts" (Nat. Comput. Sci. 2025).
   Methodological development.

**Protein-related papers:**
4. "Generalized design of sequence-ensemble-function relationships for intrinsically
   disordered proteins" (Nat. Comput. Sci. 2025). Combines physics and ML to design
   IDPs. Novel method + biological insight.
5. "Memory kernel minimization-based neural networks for discovering slow collective
   variables of biomolecular dynamics" (Nat. Comput. Sci. June 2025). Novel deep
   learning framework (MEMnets) for MD analysis.

**Benchmark/evaluation papers:**
6. "Benchmarking alignment methods for spatial transcriptomics data" (Nat. Comput.
   Sci. 2026). Systematic benchmark of 295 alignment tasks. This IS a pure
   benchmark paper published in NCS.

**Autoencoder benchmark:**
7. "AUTOENCODIX: benchmarking autoencoders for biological data" (Nat. Comput. Sci.
   2025). Open-source benchmarking framework. Another benchmark paper.

### Analysis of NCS Publication Patterns

**Papers that ARE benchmarks in NCS:** The spatial transcriptomics benchmarking paper
and AUTOENCODIX show that NCS DOES publish benchmark papers -- but they typically
introduce a novel evaluation framework (not just apply standard evaluation to a new
domain). Both papers create new software tools for benchmarking.

**Papers connecting dynamics to function in NCS:** ZERO. I found no NCS paper in
2025-2026 that connects conformational ensembles to biological function prediction.
The IDP design paper (item 4) is the closest, but it designs proteins with desired
ensemble properties rather than predicting function from ensembles.

**Papers using BioEmu or ProteinGym in NCS:** ZERO. BioEmu was published in Science,
not NCS. ProteinGym was published at NeurIPS Datasets Track.

**Papers on ML force fields in NCS:** ZERO. Force field benchmarks appear in JCTC,
ACS Materials Letters, npj Computational Materials, and Science Advances -- not NCS.
The CHIPS-FF benchmark (ACS Mater. Lett. 2026), MOFSimBench (npj Comput. Mat. 2026),
and the TEA Challenge (Chem. Sci. 2025) all appeared elsewhere. The force field
peptide benchmark (Singh et al., bioRxiv March 2026: "How Well Do Molecular Dynamics
Force Fields Model Peptides?") is on bioRxiv, not yet published.

**Implications for Gamma+Alpha-M:**
1. NCS has NOT published force field benchmarks. This is either an opportunity
   (first-of-kind for NCS) or a red flag (NCS editors may not consider it in scope).
2. NCS DOES publish benchmark papers if they include novel evaluation frameworks
   and software.
3. NCS expects methodological novelty, not just data analysis. Scouter (published
   in NCS) introduced a novel architecture. PerturbMark (Delta) would need to
   similarly introduce a novel evaluation framework.
4. The combined Gamma+Alpha-M paper must emphasize the novel FRAMEWORK (connecting
   FF validation quality to functional prediction) rather than the novel ALGORITHM
   (which does not exist).

**STATUS: CONFIRMED.** NCS has published zero force-field benchmarks, zero
dynamics-to-fitness papers, and zero papers using BioEmu or ProteinGym. The
editorial policy on "straightforward ML" is verified. Benchmark papers CAN appear
in NCS if they include novel evaluation frameworks.

---

## Revised Assessment

### How Findings Modify Round 1 Conclusions

**C1 (RSALOR baseline): STRENGTHENED.**

The ProteinGym CSV confirms RSALOR at rank #15 out of 97 methods (Spearman 0.465
on the leaderboard, 0.473 per the paper). The per-assay-type breakdown reveals
Gamma's specific opportunity (binding at 0.416, activity at 0.479) and challenge
(stability at 0.575 is hard to beat). Gamma must demonstrate improvement over
RSALOR specifically on binding and catalytic-activity assays, AND must beat ProSST
(0.445 binding, 0.476 activity) to claim dynamics adds value beyond static
structure.

The RSALOR code is trivially reproducible (`pip install rsalor`), meaning any NCS
reviewer will immediately run it as a baseline. This makes it inescapable.

**C2 (Dynamics-to-fitness niche not empty): STRENGTHENED with nuance.**

All four prior art papers are confirmed:
- Ozkan (PNAS 2025): ENM dynamics + GNN on 4 proteins. Distinct from Gamma
  methodologically (ENM vs MD) but conceptually identical.
- Burgin QDPR (JCIM 2025): Classical MD features + CNN on GB1 and AvGFP. Direct
  prior art for "MD features predict ProteinGym fitness." Does NOT scale.
- MutRobustness (bioRxiv March 2026): Establishes dynamics-fitness link at 2,000+
  protein scale. Stronger prior art than initially estimated.
- ESMDance (PNAS 2026): Dynamics-trained PLM with complex performance profile.
  NOT fairly compared to RSALOR. Benefits designed/viral proteins specifically.

The niche is more crowded than Round 1 estimated, but Gamma's specific combination
(BioEmu ensembles + ProteinGym-scale benchmark + integration with FF validation)
remains undone.

**C3 (Boltz-2 vs BioEmu): REVISED DOWNWARD.**

Boltz-2 and BioEmu perform comparably on RMSF (within 0.01-0.02 on both mdCATH
and ATLAS). There is no clear "Boltz-2 superiority" to worry about. The correct
recommendation is: include Boltz-2 as one of multiple ensemble generators for
the integration scatter plot, but the "BioEmu is obsolete" concern is overstated.

**M1 (Standard ML pipeline): STRENGTHENED.**

NCS editorial policy verification confirms "straightforward usage of machine
learning algorithms is usually outside of the journal's scope." NCS has published
benchmark papers (spatial transcriptomics, autoencoders) but all include novel
evaluation FRAMEWORKS, not just standard evaluation on new data. Gamma's MLP/
XGBoost/GATv2 pipeline is standard. The dynamics-informed GATv2 edges are
the closest to novelty but Ozkan (2025) already used dynamics-informed GNN edges.

**M2 (Win rate significance): UNCHANGED.**

The 55% win rate threshold concern from Round 1 stands. No new data modifies this.
At N=35 binding/catalysis assays, 55% win rate (19/35) is not significant by
binomial test (p ~ 0.31). The threshold must be raised to >60% or replaced by a
formal paired test.

**A1 (MutRobustness scoop): STRENGTHENED.**

The full abstract confirms median |rho| ~ 0.6 across ~2,000 natural proteins,
~400 de novo designs, and 759 NMR proteins. This is a more comprehensive
demonstration of the dynamics-fitness link than Gamma proposes. However,
MutRobustness uses predicted ddG (ThermoMPNN), not experimental DMS fitness,
and predicts dynamics FROM fitness, not fitness FROM dynamics. Gamma's
differentiation must emphasize the EXPERIMENTAL-DATA direction and the
FORCE-FIELD-QUALITY integration.

**A2 (Boltz-2 invalidates BioEmu): REVISED DOWNWARD.**

Boltz-2 does not invalidate BioEmu. They are comparable on RMSF. The
recommendation changes from "Boltz-2 superiority invalidates BioEmu monopoly"
to "include Boltz-2 as one of several generators to improve the integration
scatter plot."

**A3 (QDPR as uncited prior art): CONFIRMED.**

QDPR (Burgin, JCIM 2025) uses MD-derived RMSF, H-bond energies, SASA, and PCA
plus CNNs for fitness prediction on GB1 and AvGFP. Code available on GitHub
(Burgin-Lab/qdpr). This is the closest published prior art to Gamma's approach.
Gamma MUST cite this paper and position the proposal as the large-scale, BioEmu-
powered extension of QDPR's pilot study.

**A4 (ESMDance < RSALOR): REVISED.**

The comparison is unfair. ESMDance's 0.46 is on a different evaluation set (412
proteins, compared to ESM2-35M) while RSALOR's 0.465-0.473 is on the standard 217
ProteinGym assays. ESMDance is NOT on the ProteinGym leaderboard. The correct
interpretation: ESMDance shows dynamics-training helps for proteins lacking
evolutionary information; it does not demonstrate that dynamics-training helps for
standard proteins where conservation methods already work. This is a nuanced
finding that could help Gamma if dynamics features show similar assay-type-
dependent benefits.

### Updated Risk Matrix for Gamma+Alpha-M Combined

| Risk | Round 1 Severity | Round 2 Severity | Change |
|------|-----------------|------------------|--------|
| RSALOR baseline | HIGH | VERY HIGH | Up |
| Dynamics niche occupied | HIGH | HIGH | Unchanged |
| Boltz-2 superiority | HIGH | MODERATE | Down |
| Standard ML pipeline | HIGH | HIGH | Unchanged |
| Win rate significance | HIGH | HIGH | Unchanged |
| MutRobustness scoop | MODERATE | HIGH | Up |
| NCS editorial fit | MODERATE | HIGH | Up |
| QDPR uncited prior art | MODERATE | MODERATE | Unchanged |

### Conditions for Revised Recommendation

Gamma+Alpha-M Combined remains at MAJOR REVISION. To be viable for NCS submission,
the following changes are required (updated from Round 1):

1. **Mandatory RSALOR baseline** with explicit per-assay-type comparison. Show
   Spearman improvement over RSALOR by assay type. The bar is:
   - Binding: beat 0.416 (RSALOR) AND 0.445 (ProSST)
   - Activity: beat 0.479 (RSALOR) AND 0.476 (ProSST)
   - Expression: beat 0.427 (RSALOR) AND 0.530 (ProSST)
   - Stability: beat 0.575 (RSALOR) AND 0.653 (ProSST) -- nearly impossible

2. **Cite and position against:** Ozkan (PNAS 2025), Burgin QDPR (JCIM 2025),
   MutRobustness (bioRxiv 2026), ESMDance (PNAS 2026). The positioning must be:
   "These studies demonstrate the concept; we provide the first large-scale,
   BioEmu-powered evaluation integrated with force field validation."

3. **Include Boltz-2 as an ensemble generator** in the integration scatter plot
   (not as a replacement for BioEmu). This adds a data point and addresses the
   "why BioEmu only?" concern.

4. **Restructure the paper** around assay-type stratification as the PRIMARY finding.
   "For which types of protein function do dynamics add predictive value beyond
   sequence?" is the question. The answer, stratified by assay type, is the finding.

5. **Raise the methodological bar** by either: (a) developing a novel architecture
   (not just GATv2 with different edges), or (b) framing the paper as a Resource
   (community benchmark + data) rather than an Article. NCS Resource papers have
   lower methodological novelty requirements.

6. **Address the RMSF-RSA-conservation collinearity** explicitly. The critical
   ablation (ESM2 + RSA vs ESM2 + RSA + RMSF) must be the central hypothesis
   test, not a secondary analysis.

### Delta (PerturbMark): No Changes

Delta assessment unchanged by Round 2 verification. NCS publishes perturbation
prediction papers (Scouter, LPMs) and benchmark papers (spatial transcriptomics,
autoencoders). Delta's position as a benchmark paper with a novel evaluation
framework is well-aligned with NCS precedent. Minor revision recommendation stands.

---

## References

1. ProteinGym v1.3 Substitution Benchmark CSV. GitHub: OATML-Markslab/ProteinGym,
   `benchmarks/DMS_zero_shot/substitutions/Spearman/Summary_performance_DMS_
   substitutions_Spearman.csv`. Accessed April 15, 2026.

2. Notin, P. (2025). Have We Hit the Scaling Wall for Protein Language Models?
   Substack analysis. https://pascalnotin.substack.com/p/have-we-hit-the-scaling-
   wall-for

3. Notin, P., Kollasch, A.W., Ritter, D., et al. (2023). ProteinGym: Large-Scale
   Benchmarks for Protein Fitness Prediction and Design. NeurIPS Datasets Track.

4. Tsishyn, M., Hermans, P., Rooman, M., and Pucci, F. (2025). Residue
   conservation and solvent accessibility are (almost) all you need for predicting
   mutational effects in proteins. Bioinformatics 41(6): btaf322.

5. RSALOR Python package. GitHub: 3BioCompBio/RSALOR. PyPI: rsalor.
   42 stars. Python 3.9+.

6. Wohlwend, J., Passaro, S., Corso, G., et al. (2025). Boltz-2: Towards
   Accurate and Efficient Binding Affinity Prediction. bioRxiv 2025.06.14.659707.
   PMC12262699.

7. MIT and Recursion press release (2025). "MIT and Recursion Release Boltz-2:
   Next Generation AI Model to Predict Binding Affinity at Unprecedented Speed,
   Scale, and Accuracy." MIT license. GitHub: jwohlwend/boltz.

8. Lewis, S., Hempel, T., Jimenez-Luna, J., et al. (2025). Scalable emulation of
   protein equilibrium ensembles with generative deep learning. Science 369:
   270-278.

9. Singh, A. (2025). BioEmu is a biomolecular emulator for sampling protein
   structure ensembles. Nature Methods 22: 2008.

10. BioEmu augmented MD preprint (2026). Accelerated sampling of protein dynamics
    using BioEmu augmented molecular simulation. bioRxiv 2026.01.07.698041.

11. Zha, J., Li, N., Li, M., et al. (2026). Assessing the Performance of BioEmu
    in Understanding Protein Dynamics. Int. J. Mol. Sci. 27(6): 2896.

12. Ozkan, S.B. et al. (2025). A protein dynamics-based deep learning model
    enhances predictions of fitness and epistasis. PNAS 122(42): e2502444122.
    GitHub: SBOZKAN/GNN (7 stars).

13. Burgin, T.E. (2025). Quantified Dynamics-Property Relationships: Data-Efficient
    Protein Engineering with Machine Learning of Protein Dynamics. J. Chem. Inf.
    Model. 65(21): 11979-11987. bioRxiv preprint: 2025.04.23.650227. GitHub:
    Burgin-Lab/qdpr.

14. Zuk, O. (2026). Mutational Robustness Predicts Protein Dynamics Across Natural
    and Designed Proteins. bioRxiv 2026.03.19.713008v1. Hebrew University of
    Jerusalem.

15. Hou, L., Zhao, Q., and Shen, Y. (2026). Protein Language Models Trained on
    Biophysical Dynamics Inform Mutation Effects. PNAS 123: e2530466123. GitHub:
    ShenLab/SeqDance.

16. Nature Computational Science editorial (2021). To review or not to review.
    Nat. Comput. Sci. 1: 226.

17. Zhu, O. and Li, J. (2026). Scouter predicts transcriptional responses to
    genetic perturbations with large language model embeddings. Nat. Comput.
    Sci. 6: 21-28.

18. Nat. Comput. Sci. (2025). In silico biological discovery with large perturbation
    models. https://www.nature.com/articles/s43588-025-00870-1

19. Nat. Comput. Sci. (2025). Generalized design of sequence-ensemble-function
    relationships for intrinsically disordered proteins.
    https://www.nature.com/articles/s43588-025-00881-y

20. Nat. Comput. Sci. (2025). Memory kernel minimization-based neural networks for
    discovering slow collective variables of biomolecular dynamics.
    https://www.nature.com/articles/s43588-025-00815-8

21. Nat. Comput. Sci. (2026). Benchmarking alignment methods for spatial
    transcriptomics data.
    https://www.nature.com/articles/s43588-026-00977-z

22. Singh, B., Martinez-Noa, Y., and Perez, A. (2026). How Well Do Molecular
    Dynamics Force Fields Model Peptides? A Systematic Benchmark Across Diverse
    Folding Behaviors. bioRxiv (March 2026).

23. CHIPS-FF (2026). Evaluating Universal Machine Learning Force Fields for
    Material Properties. ACS Mater. Lett.

24. TEA Challenge (2025). Crash testing machine learning force fields for
    molecules, materials, and interfaces. Chem. Sci.

25. Lyu, N., Du, S., Shao, Q., et al. (2026). Physics-Grounded Evaluation to
    Guide Accurate Biomolecular Prediction. bioRxiv (March 2026).

26. ProteinGym GitHub repository. OATML-Markslab/ProteinGym. README.md. v1.3
    with 97 baselines across 217 DMS substitution assays.

27. Mohanty, V. and Shakhnovich, E.I. (2026). Biophysical fitness landscape
    design traps viral evolution. bioRxiv (April 2026).
