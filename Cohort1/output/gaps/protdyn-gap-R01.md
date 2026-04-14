---
agent: protdyn
round: 1
date: 2026-04-14
type: gap-report
---

# Protein Dynamics & Conformational Biology -- Round 1 Gap Report

## Reporting Agent

Dr. Protein Dynamics & Conformational Biology Expert (protdyn). Senior specialist
with 20+ years in structural biophysics and computational dynamics. Post-AlphaFold
thinker focused on conformational ensembles, intrinsically disordered proteins,
allosteric communication, and the dynamic landscape governing biological function.

---
---

# Gap 1: Unified Dynamics-to-Function Mapping -- Bridging Conformational Ensembles to Biological Activity Prediction

---
gap_id: dynamics-to-function
---

## Gap Description

### What Is Missing

The field can now generate conformational ensembles for proteins at increasing
scale and quality -- tools like BioEmu (Jing et al., Science, 2025), AlphaFlow
(Jing et al., ICML, 2024), IDPFold2 (bioRxiv, 2026), and TEMPO (NeurIPS, 2025)
produce ensembles that recapitulate experimental observables (SAXS, NMR chemical
shifts, RDCs). However, there is **no general computational framework that maps
predicted conformational ensembles to biological function**. We can generate
ensembles but cannot systematically answer: "Given this ensemble, what does this
protein do, and how do mutations alter that function?"

Specifically, the field lacks:
1. A method to extract functional annotations directly from ensemble properties
   (not just from static structures)
2. A way to predict how perturbations (mutations, ligand binding, post-translational
   modifications) reshape ensembles AND how those reshaped ensembles alter function
3. Benchmarks that pair conformational ensemble data with functional readouts at scale
4. Models that connect ensemble-level descriptors (population distributions,
   inter-state transition rates, correlated motions) to measurable biological
   outputs (catalytic rates, binding affinities, signaling efficacy)

### Current State of the Art

**Ensemble generation** has seen rapid progress:
- **BioEmu** (Microsoft Research, 2025): Generates equilibrium ensembles at
  ~100,000x the speed of MD, trained on >200 ms of simulation data. Captures
  cryptic pocket formation, local unfolding, domain rearrangements. Predicts
  relative free energies with ~1 kcal/mol accuracy. Published in Science.
- **AlphaFlow/ESMFlow** (Jing et al., 2024): Flow-matching framework fine-tuned
  on MD ensembles; generates diverse conformations matching experimental distributions.
- **IDPFold2** (bioRxiv, Jan 2026): Mixture-of-Experts flow matching for multidomain
  proteins and complexes including IDRs.
- **TEMPO** (NeurIPS, 2025): Hierarchical autoregressive framework capturing
  multi-scale temporal dynamics with Markovian process modeling.
- **RocketSHP** (bioRxiv, 2025): Predicts RMSF, generalized correlation coefficients,
  and structural heterogeneity profiles at proteome scale with up to 73% error
  reduction for long proteins.

**Function prediction** remains largely structure-based:
- Current function prediction methods (DeepFRI, ProteInfer, InterPro) use static
  structures or sequences, not ensembles.
- Mutation effect predictors (ESM-1v, ProteinGym benchmarks, EVE) operate on
  sequences or single structures.
- SeqDance/ESMDance (2025) represent a first step: PLMs trained on MD-derived
  dynamic properties that improve mutation effect prediction, but still predict
  proxy properties (RMSF, B-factors), not biological function directly.

**The gap**: No one has built the bridge from "here is a predicted ensemble" to
"here is the predicted biological consequence." This is the central unsolved
problem of post-AlphaFold protein science.

### Evidence the Gap Exists

1. **Review by Chen et al. (Briefings in Bioinformatics, 2025)**: Explicitly states
   that "protein function is not solely determined by static three-dimensional
   structures but is fundamentally governed by dynamic transitions between multiple
   conformational states" and identifies the lack of standardized benchmarks and
   metrics for evaluating dynamic conformations as a significant challenge.

2. **Nature Methods community initiative (March 2026)**: A community-driven
   perspective advocates for a unified framework integrating experimental techniques
   with computational methods for conformational ensemble determination --
   notably, the framework focuses on ensemble determination but does NOT address
   the ensemble-to-function link.

3. **Protein Language Models and dynamics (SeqDance/ESMDance, 2025)**: These models
   demonstrate that incorporating dynamics into PLMs improves mutation effect
   prediction (especially for designed and viral proteins lacking evolutionary
   information), proving the dynamics-function link exists but is not yet
   systematically exploited. However, they predict biophysical properties (RMSF,
   B-factors), not biological function.

4. **PeptoneBench (2025)**: A comprehensive benchmark for evaluating ensemble
   predictions against experimental observables (SAXS, NMR, RDCs, PREs), but
   evaluates only structural agreement, not functional prediction.

5. **Mutational Robustness study (bioRxiv, March 2026)**: Demonstrates that
   mutationally sensitive residues are also dynamically rigid, proving the
   dynamics-mutation-function axis is real but underexploited computationally.

6. **Deep mutational scanning data gap**: ProteinGym provides >200 DMS datasets
   but none are paired with conformational ensemble data. The disconnect between
   mutation effect data and dynamics data is a critical barrier.

## Why This Gap Matters

### Scientific Importance

This is arguably the most important unsolved problem in computational structural
biology. AlphaFold solved the structure prediction problem; the next grand challenge
is predicting how conformational dynamics encode biological function. Every major
biological process -- catalysis, signaling, transport, regulation -- depends on
protein dynamics. A framework connecting ensembles to function would fundamentally
change how we understand protein biology.

### Practical Impact

- **Drug discovery**: Ensemble-aware function prediction would enable identification
  of druggable dynamic states, not just static pockets. The conformational selection
  and induced fit paradigms in drug binding require ensemble-level understanding.
- **Protein engineering**: Predicting how mutations alter function through
  dynamics would transform rational design.
- **Clinical genomics**: Interpreting variants of uncertain significance (VUS)
  through their dynamic and functional consequences.

### Publication Potential

This is a **Nature Computational Science** or **Nature Methods** paper. It
introduces a fundamentally new paradigm: predicting function from dynamics. The
framing is: "AlphaFold2 solved structure prediction; we solve the next problem --
dynamics-to-function prediction."

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

Build a "Dynamics-to-Function" (D2F) framework that:
1. Takes conformational ensembles (from BioEmu, AlphaFlow, MD, etc.) as input
2. Extracts ensemble-level feature vectors: population-weighted descriptors,
   inter-state transition signatures, correlated motion networks, pocket
   occupancy distributions, solvent accessibility fluctuations
3. Maps these to functional annotations (GO terms, EC numbers, binding
   affinities, DMS fitness scores) via a learned model
4. Validates against held-out experimental data (DMS, activity assays, binding data)

### Required Data

- **Ensemble data**: BioEmu's released MD dataset (>100 ms across thousands of
  proteins), ATLAS (>1,300 protein simulations), mdCATH (5,398 domains at 5
  temperatures), ProteinConformers (2.7M structures across 734 proteins)
- **Functional data**: ProteinGym DMS datasets (>200 assays), UniProt functional
  annotations, enzyme kinetics from BRENDA, binding affinity data from BindingDB/PDBbind
- **Validation**: NMR relaxation data (dynamics timescales), HDX-MS data (protection
  factors), SAXS profiles

### Required Compute

- Feature extraction from ensembles: moderate GPU (can parallelize across proteins)
- Model training: single H200 node for weeks, or multi-GPU for days
- Ensemble generation for proteins without pre-existing data: BioEmu runs thousands
  of structures per hour on a single GPU

### Required Methods

- Ensemble featurization: graph-based representations of dynamic networks,
  persistent homology of conformational landscapes, Wasserstein-based ensemble
  descriptors
- Multi-task learning: predict multiple functional readouts simultaneously
- Transfer learning: fine-tune PLM representations with dynamics features

## Feasibility Assessment

### Technical Feasibility: High
All input data (ensembles, functional annotations, DMS data) are publicly available.
BioEmu and AlphaFlow are open-source. Feature extraction from ensembles is
well-established in the MD community. The ML modeling is standard multi-task
learning.

### Timeline Feasibility: Medium
Summer 2026 is tight for a comprehensive framework. A focused version targeting
one functional axis (e.g., mutation effects on stability and activity, using DMS
data paired with ensemble features) is achievable. Full framework with multiple
functional readouts would need prioritization.

### Wet Lab Independence: High
All data are computational or from published experiments. Validation uses existing
DMS datasets, binding affinity databases, and enzyme kinetics databases.

## Competitive Landscape

### Who Else Might Fill This Gap

- **Microsoft Research (BioEmu team)**: Best positioned -- they have the data and
  the ensemble generator. Their blog post mentions exploring functional
  implications, but no published framework yet.
- **Frank Noe's group (Freie Universitat Berlin)**: Developed BioEmu; could extend
  to function prediction.
- **AlphaFlow developers (MIT)**: Focused on ensemble generation, not function.
- **SeqDance team**: Closest to dynamics-to-function, but predicts biophysical
  proxies, not function directly.

### Risk of Being Scooped: Medium-High
This is an obvious next step. The BioEmu team is likely thinking about this.
Differentiation would come from (a) a more systematic approach using multiple
ensemble sources, (b) a rigorous benchmark, and (c) demonstrating generalization
across diverse functional readouts.

### Differentiation
Focus on building the BENCHMARK first (pairing ensemble data with functional data
at scale), then demonstrate that ensemble features improve function prediction
beyond sequence and structure alone. This benchmark contribution alone would be
highly publishable.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 8 | First systematic dynamics-to-function framework; SeqDance is closest but indirect |
| Scientific impact | 9 | Addresses the central post-AlphaFold challenge; broad community interest |
| Feasibility (computational only) | 8 | All data and tools are public; standard ML methods |
| Timeline (summer 2026) | 6 | Full framework is ambitious; focused version on DMS + ensembles is achievable |
| Publication potential (Nat Comp Sci) | 9 | Perfect fit: new computational paradigm with broad implications |
| **Overall** | **8.0** | High-impact gap with strong feasibility; timeline is the main constraint |

## References

1. Jing, B. et al. "AlphaFold Meets Flow Matching for Generating Protein Ensembles." ICML 2024. https://arxiv.org/abs/2402.04845
2. Jing, B. et al. "Scalable Emulation of Protein Equilibrium Ensembles with Generative Deep Learning." Science, 2025. https://www.science.org/doi/10.1126/science.adv9817
3. Chen, Y. et al. "Beyond static structures: protein dynamic conformations modeling in the post-AlphaFold era." Briefings in Bioinformatics, 26(4), 2025. https://academic.oup.com/bib/article/26/4/bbaf340/8202937
4. Zheng, W. et al. "Extending Conformational Ensemble Prediction to Multidomain Proteins and Protein Complex." bioRxiv, 2026. https://www.biorxiv.org/content/10.64898/2026.01.14.699584v1
5. "Toward a unified framework for determining conformational ensembles of disordered proteins." Nature Methods, 2026. https://www.nature.com/articles/s41592-026-03003-2
6. Chen, Z. et al. "Protein Language Models Trained on Biophysical Dynamics Inform Mutation Effects." 2025. PMC12846831
7. Chen, Z. et al. "Learning Biophysical Dynamics with Protein Language Models." 2024. PMC11507661
8. "Mutational Robustness Predicts Protein Dynamics Across Natural and Designed Proteins." bioRxiv, 2026. https://www.biorxiv.org/content/10.64898/2026.03.19.713008v1
9. Nowicka, M. et al. "Advancing Protein Ensemble Predictions Across the Order-Disorder Continuum (PeptoneBench)." bioRxiv, 2025. https://www.biorxiv.org/content/10.1101/2025.10.18.680935v3
10. Durairaj, J. et al. "ATLAS Dataset." Nature, 2024.
11. Tiemann, J. et al. "mdCATH: A Large-Scale MD Dataset." Scientific Data, 2024. https://www.nature.com/articles/s41597-024-04140-z

---
---

# Gap 2: Standardized Evaluation Framework for Conformational Ensemble Generators -- The "ImageNet Moment" for Protein Dynamics

---
gap_id: ensemble-evaluation-framework
---

## Gap Description

### What Is Missing

The protein conformational ensemble generation field has exploded with methods --
AlphaFlow, BioEmu, IDPFold2, TEMPO, P2DFlow, str2str, Distributional Graphformer,
Boltzmann generators -- but there is **no standardized, comprehensive evaluation
framework** that allows rigorous comparison across methods, protein types, and
functional contexts. Each method is evaluated on its own terms, using different
subsets of proteins, different metrics, and different "ground truth" references.
The field cannot answer the fundamental question: "Which method generates the best
ensembles, and for what types of proteins?"

The specific deficiencies are:

1. **No unified benchmark dataset** spanning the full order-disorder continuum
   with matched experimental data (NMR, SAXS, cryo-EM) AND computational
   reference data (long MD, enhanced sampling)
2. **No consensus on evaluation metrics**: Methods are compared using incompatible
   metrics -- some use RMSD-based measures, others Wasserstein distances, others
   forward-model comparisons to NMR/SAXS. There is no standardized metric suite.
3. **No evaluation of functional relevance**: Current benchmarks evaluate whether
   ensembles look right (structural agreement) but not whether they capture
   functionally important states (cryptic pockets, allosteric states, transition
   states)
4. **Ground truth problem**: Using MD as "ground truth" is circular when many
   methods are trained on MD. Using experimental data requires forward models
   that themselves have uncertain accuracy for disordered systems.
5. **Lack of evaluation across protein types**: Folded globular proteins, IDPs,
   multidomain proteins, membrane proteins, and complexes are almost never
   evaluated in the same framework.

### Current State of the Art

Several partial benchmarking efforts exist:

- **PeptoneBench (2025)**: The most comprehensive attempt. Uses SAXS and NMR
  (chemical shifts, RDCs, PREs) data. Covers 439 SAXS profiles and 659 proteins
  with NMR CS. Includes maximum entropy reweighting. However, it still focuses
  on structural agreement, not functional relevance, and does not include
  MD-based metrics.

- **ATLAS dataset (2024)**: All-atom MD simulations of >1,300 proteins at 3
  temperatures. Used as benchmark by AlphaFlow and others. But ATLAS simulations
  are relatively short (microsecond scale) and may not capture slow functional
  motions.

- **mdCATH (2024)**: 5,398 domains at 5 temperatures. Broader coverage but
  single-domain only, and domain-level representation may miss inter-domain
  dynamics.

- **ProteinConformers (2026)**: 2.7 million structures across 734 proteins with
  energy annotations. Includes ProteinConformers-lite benchmark (381,546
  conformers across 87 CASP14/15 proteins). Addresses landscape coverage but
  limited to CASP proteins.

- **CryoBench (NeurIPS, 2024)**: Focuses on cryo-EM heterogeneity, not general
  ensemble evaluation.

**What is missing**: An integrated benchmark that combines (a) diverse protein
types, (b) multiple experimental observables, (c) MD references at sufficient
timescale, (d) functional annotations, and (e) a standardized metric suite.

### Evidence the Gap Exists

1. **Chen et al. (Briefings in Bioinformatics, 2025)** explicitly identifies "the
   lack of standardized benchmarks and metrics for evaluating dynamic
   conformations" as a significant challenge.

2. **PeptoneBench paper (bioRxiv, 2025)** acknowledges that "evaluating predictions
   for disordered proteins presents inherent difficulties: no single native
   structure exists, and metrics such as RMSD and GDT-TS are ill-posed."

3. **Forward model reliability concern**: "Many forward models have been optimized
   and validated primarily on structured systems, raising concerns about their
   reliability when extrapolated to disordered proteins." (PeptoneBench, 2025)

4. **Method proliferation without comparison**: AlphaFlow (2024), BioEmu (2025),
   IDPFold2 (2026), TEMPO (2025), P2DFlow (2024), Str2Str, and ProteinConformers
   all use different evaluation protocols, making cross-method comparison nearly
   impossible.

5. **Nature Methods perspective (2026)**: A community initiative advocates for a
   unified framework for conformational ensemble determination of disordered
   proteins, explicitly acknowledging the current fragmentation.

## Why This Gap Matters

### Scientific Importance

Without standardized evaluation, the field cannot make progress systematically.
New methods claim superiority based on cherry-picked benchmarks. Researchers
cannot choose the right tool for their protein of interest. This is analogous
to protein structure prediction before CASP -- progress was unclear until a
standardized blind evaluation existed.

### Practical Impact

- Researchers waste time trying multiple ensemble generators because no guidance
  exists on which works best for their protein type
- Drug discovery groups cannot trust ensemble-based screening without validated
  ensemble quality metrics
- The field risks "benchmark hacking" where methods overfit to ATLAS or similar
  datasets

### Publication Potential

This is a **Nature Methods** or **Nature Computational Science** paper. Community
benchmarks have historically been highly cited (CASP, CAPRI, ProteinGym, TAPE).
A comprehensive dynamics benchmark with associated metrics and leaderboard would
be a field-defining contribution.

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

Create **DynaBench**: a multi-tier evaluation framework for protein conformational
ensemble generators:

**Tier 1 -- Structural Fidelity**: Does the ensemble match known structural
data? Metrics: RMSD distributions, TM-score distributions, backbone dihedral
distributions, pairwise distance distributions, Wasserstein distance (RMWD).

**Tier 2 -- Experimental Consistency**: Does the ensemble agree with experimental
observables? Metrics: chi-squared to SAXS profiles, RMSE to NMR chemical shifts,
Q-factor for RDCs, PRE agreement, crystallographic B-factor correlation.

**Tier 3 -- Dynamical Properties**: Does the ensemble capture correct dynamics?
Metrics: RMSF correlation, dynamic contact maps, generalized correlation
coefficients, Markov state model-derived rates vs. NMR relaxation.

**Tier 4 -- Functional Relevance**: Does the ensemble capture functionally
important states? Metrics: cryptic pocket occupancy (vs. known allosteric sites),
active-site geometry populations, known alternative conformations.

### Required Data

- **Protein set**: ~100 proteins spanning: globular (well-folded), IDPs (fully
  disordered), multi-domain (with linkers), proteins with known alternative
  states, proteins with known cryptic pockets, enzyme active-site dynamics
- **Experimental data**: NMR (chemical shifts from BMRB, RDCs, PREs, relaxation),
  SAXS (from SASBDB), cryo-EM multi-conformer data, HDX-MS data
- **Computational references**: Long MD (ATLAS, mdCATH, BioEmu training data),
  enhanced sampling trajectories
- **Functional annotations**: Allosteric sites (ASD, AlloBench), cryptic pockets,
  known conformational changes (CoDNaS database), DMS data

### Required Compute

- Running ensemble generators on the benchmark set: moderate GPU (BioEmu:
  thousands of structures/hour/GPU; AlphaFlow similar)
- Feature extraction and metric computation: mostly CPU, parallelizable
- Long MD simulations for additional references: HPC cluster with H200 GPUs
  would enable microsecond simulations on dozens of proteins

### Required Methods

- Forward model implementations for NMR/SAXS/cryo-EM
- Maximum entropy reweighting framework (BME, ABSURDER)
- Wasserstein distance calculations (WASCO)
- Markov state model construction (PyEMMA, deeptime)
- Pocket detection and tracking (fpocket, DoGSiteScorer)

## Feasibility Assessment

### Technical Feasibility: High
All components exist individually. The challenge is integration, curation, and
scaling. Forward models for NMR and SAXS are available (SPARTA+, SHIFTX2,
CRYSOL, FoXS). Ensemble generators are open-source.

### Timeline Feasibility: Medium
Curating the protein set, collecting experimental data, running all generators,
and computing all metrics is substantial work. A focused version covering 30-50
proteins with 3-4 ensemble generators across 3 tiers is achievable in summer 2026.
The full 100-protein, 4-tier benchmark would require longer.

### Wet Lab Independence: High
All data are from published experiments and public databases.

## Competitive Landscape

### Who Else Might Fill This Gap

- **Peptone Ltd**: PeptoneBench is the closest. But it focuses on IDP/order-disorder
  and lacks the functional relevance tier.
- **CASP organizers**: Could add an ensemble prediction category, but CASP cycles
  are slow and ensemble evaluation was not in CASP16.
- **ATLAS/mdCATH teams**: Could extend their datasets into benchmarks but focus
  on data provision, not method evaluation.

### Risk of Being Scooped: Medium
PeptoneBench is moving in this direction, but its focus is narrower. A
comprehensive benchmark spanning functional relevance would be differentiated.

### Differentiation
The key differentiator is Tier 4 (functional relevance). No existing benchmark
evaluates whether ensembles capture functionally important states. This is where
the highest scientific value lies.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 7 | PeptoneBench exists but lacks functional tier; concept of dynamics benchmark is emerging |
| Scientific impact | 9 | Community benchmarks are highly cited; would define evaluation standards |
| Feasibility (computational only) | 8 | All tools and data exist; integration is the challenge |
| Timeline (summer 2026) | 6 | Full benchmark is ambitious; focused version is achievable |
| Publication potential (Nat Comp Sci) | 8 | Benchmarks in Nature Methods/Nat Comp Sci are common and highly impactful |
| **Overall** | **7.6** | Very high impact with established feasibility; differentiation via functional tier |

## References

1. Nowicka, M. et al. "Advancing Protein Ensemble Predictions Across the Order-Disorder Continuum (PeptoneBench)." bioRxiv, 2025.
2. Durairaj, J. et al. "ATLAS: A Large-Scale All-Atom Molecular Dynamics Dataset for Protein Structure Prediction." 2024.
3. Tiemann, J. et al. "mdCATH: A Large-Scale MD Dataset for Data-Driven Computational Biophysics." Scientific Data, 2024.
4. "ProteinConformers: large-scale and energetically profiled descriptions of protein conformational landscapes." bioRxiv, 2026. https://www.biorxiv.org/content/10.64898/2026.02.20.707011v1
5. Chen, Y. et al. "Beyond static structures: protein dynamic conformations modeling in the post-AlphaFold era." Briefings in Bioinformatics, 2025.
6. "Toward a unified framework for determining conformational ensembles of disordered proteins." Nature Methods, 2026.
7. Zamora, W. et al. "WASCO: A Wasserstein-based Statistical Tool to Compare Conformational Ensembles of Intrinsically Disordered Proteins." J. Mol. Biol., 2023.
8. Scherer, M. et al. "PyEMMA 2: A Software Package for Estimation, Validation, and Analysis of Markov Models." JCTC, 2015.
9. CryoBench. NeurIPS 2024. https://arxiv.org/abs/2408.05526
10. AlloBench. "A Data Set Pipeline for the Development and Benchmarking of Allosteric Site Prediction Tools." ACS Omega, 2025.

---
---

# Gap 3: Allosteric Communication Prediction from Sequence Without Molecular Dynamics -- Toward Proteome-Scale Allosteric Mapping

---
gap_id: allostery-from-sequence
---

## Gap Description

### What Is Missing

Predicting allosteric sites and communication pathways in proteins currently
requires either (a) known crystal structures with bound allosteric modulators,
or (b) expensive molecular dynamics simulations followed by network analysis.
There is **no method that can predict allosteric communication networks directly
from protein sequence at proteome scale**. This means that the vast majority
of proteins -- especially those without crystal structures or those with
disordered/flexible regions mediating allostery -- have unknown allosteric
landscapes.

Specifically:
1. Existing allosteric site predictors (PASSer, AlloFusion, AlloPED) require
   3D structures as input and are limited to identifying sites, not communication
   pathways
2. Dynamic network analysis methods (NRI, AlloPool) require MD trajectories
   that take hours to days per protein
3. No method connects sequence variation (e.g., SNPs, cancer mutations) to
   allosteric rewiring at scale
4. The bidirectional nature of allosteric communication (reversed allostery)
   is not captured by current predictors
5. Allosteric effects mediated by disorder or IDRs are essentially invisible
   to current methods

### Current State of the Art

**Structure-based allosteric site prediction:**
- **AlloFusion (JCIM, 2025)**: Residue-level multimodal prediction integrating
  protein language model embeddings, biochemical properties, and evolutionary
  profiles. Achieves AUROC of ~0.80 on ASBench. Requires 3D structure.
- **AlloPED (2025)**: Combines pocket-level and residue-level prediction using
  PLMs and structure features. Two-module design (AlloPED-pocket + AlloPED-site).
  Still structure-dependent.
- **PASSer2.0 (2022)**: Ensemble ML model for allosteric site prediction from
  protein structures.

**Dynamics-based allosteric communication:**
- **Neural Relational Inference (NRI, Nature Comms, 2022)**: GNN-based encoder-
  decoder to infer latent allosteric interactions from MD trajectories. Requires
  simulation data.
- **AlloPool (bioRxiv, 2024)**: Adaptive GNN for dynamic allosteric network
  prediction; requires MD/SMD trajectories.
- **Network-based approaches**: Community network analysis, perturbation response
  scanning -- all require MD.

**Databases:**
- **Allosteric Site Database (ASD)**: 3,102 allosteric sites, 17,627 human
  proteins with predicted potential allosteric sites, 261 allosteric networks.
- **AlloBench (2025)**: 2,141 allosteric sites from 2,034 protein structures
  with 418 unique chains. Integrates ASD, UniProt, M-CSA, and PDB.

**The critical gap**: All prediction methods require 3D structures and/or MD
simulations. There is no sequence-to-allostery method that could be applied
proteome-wide, analogous to how AlphaFold enabled proteome-scale structure
prediction.

### Evidence the Gap Exists

1. **Review by Li et al. (Drug Discovery Today, 2025)**: "Recent advances in
   computational strategies for allosteric site prediction: Machine learning,
   molecular dynamics, and network-based approaches" identifies the integration
   of ML with dynamics as an emerging direction but acknowledges that current
   methods are computationally expensive and structure-dependent.

2. **AlloSitePro (ASD)**: The largest attempt at proteome-scale allosteric site
   prediction covers 17,627 human proteins but uses a simple pocket-based
   approach on predicted structures, not sequence-based prediction. It predicts
   sites, not communication pathways.

3. **AlloFusion (2025)**: While using PLM embeddings, still requires 3D
   coordinates as the base representation. The PLM component improves accuracy
   but does not enable structure-free prediction.

4. **Protein Language Model limitations**: Despite ESM-2 and other PLMs encoding
   rich evolutionary information that likely includes allosteric coupling patterns,
   no one has systematically extracted allosteric communication from PLM attention
   patterns or embeddings.

5. **Reversed allostery concept (Chen et al., 2021)**: The bidirectional nature
   of allosteric communication -- where orthosteric perturbations modulate
   allosteric sites -- is theoretically established but computationally
   unexploited at scale.

## Why This Gap Matters

### Scientific Importance

Allostery is the "second secret of life" (Monod). It governs nearly every
regulated biological process. Yet we cannot predict allosteric behavior for the
vast majority of proteins. A sequence-based allosteric communication predictor
would be as transformative as AlphaFold was for structure -- it would enable
understanding of how signals propagate through proteins and across protein
networks at unprecedented scale.

### Practical Impact

- **Drug discovery**: ~25% of all drugs act through allosteric mechanisms.
  Predicting allosteric sites and pathways from sequence would dramatically
  expand the druggable proteome.
- **Cancer genomics**: Many cancer mutations act allosterically. Predicting
  which mutations rewire allosteric networks would improve variant
  interpretation.
- **Protein engineering**: Designing allosteric switches requires understanding
  communication pathways; sequence-level prediction would accelerate design.

### Publication Potential

A sequence-to-allosteric-communication predictor demonstrated at proteome scale
would be a **Nature** or **Nature Computational Science** paper. The analogy to
AlphaFold (but for dynamics/allostery rather than structure) would generate
enormous interest.

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

1. **Training data generation**: Use existing MD datasets (BioEmu ensembles,
   ATLAS, mdCATH) to compute allosteric communication networks (dynamic
   network analysis, mutual information, perturbation response) for thousands
   of proteins. Label residue pairs as allosterically coupled or not.
2. **Model architecture**: Train a sequence-to-allostery model using PLM
   embeddings (ESM-2) + evolutionary coupling (MSA features) to predict:
   (a) allosteric site locations, (b) communication pathway residue pairs,
   (c) allosteric coupling strength
3. **Validation**: Compare predictions against known allosteric sites (ASD,
   AlloBench), known communication pathways from experimental mutagenesis,
   and held-out MD-derived networks
4. **Proteome-scale application**: Apply to all human proteins; identify
   novel allosteric hotspots and potentially druggable allosteric sites

### Required Data

- **Training**: ATLAS + mdCATH + BioEmu training data (MD trajectories for
  thousands of proteins) with computed dynamic network analysis features
- **Labels**: ASD (3,102 allosteric sites), AlloBench (2,141 sites),
  experimental mutagenesis data on allosteric communication
- **Sequence features**: ESM-2 embeddings, MSA features (evolutionary
  couplings), protein family annotations

### Required Compute

- Dynamic network analysis on existing MD data: moderate HPC (CPU-heavy)
- PLM feature extraction: single GPU per batch
- Model training: multi-GPU (H200 cluster) for days to weeks
- Proteome-scale inference: single GPU, hours

### Required Methods

- Dynamic network analysis (NetworkX, correlationplus, MDAnalysis)
- PLM fine-tuning (ESM-2, LoRA)
- Graph neural networks for residue-pair predictions
- Attention analysis for interpretability

## Feasibility Assessment

### Technical Feasibility: Medium-High
The main challenge is generating high-quality allosteric communication labels
from MD data. Dynamic network analysis is noisy and depends on simulation
length and force field. The ASD database provides structure-based labels but
not pathway-level labels at scale.

### Timeline Feasibility: Medium
Label generation from MD data is the bottleneck. If existing analyzed
trajectories can be leveraged, a focused model predicting allosteric site
locations (not full pathways) from sequence is achievable in summer 2026.

### Wet Lab Independence: High
All training data are computational (MD) or from published databases (ASD).
Validation against experimental mutagenesis uses published data.

## Competitive Landscape

### Who Else Might Fill This Gap

- **Gao group (Shanghai, ASD developers)**: Best positioned due to ASD database
  ownership. But their AlloSitePro remains structure-based.
- **Protein Frustration groups (e.g., Ferreiro, Wolynes)**: Energy landscape
  theory connects frustration to allostery, but no proteome-scale predictor.
- **PLM community (Meta AI/ESM)**: Could extract allosteric signals from PLM
  attention but have not done so.
- **Microsoft Research**: BioEmu ensembles could be mined for allosteric
  networks, but their focus is on ensemble generation, not allostery
  specifically.

### Risk of Being Scooped: Medium
The AlloFusion/AlloPED trajectory is moving toward PLM integration but remains
structure-dependent. No group has published a sequence-only allosteric predictor.
The idea is "in the air" but not yet realized.

### Differentiation
Go beyond site prediction to communication pathway prediction. Demonstrate that
sequence-based features (from PLMs) encode allosteric coupling, not just
individual site properties.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 9 | No sequence-only allosteric communication predictor exists |
| Scientific impact | 9 | Allostery is central to biology; proteome-scale prediction is transformative |
| Feasibility (computational only) | 7 | Label generation from MD is the bottleneck; site prediction is easier than pathway prediction |
| Timeline (summer 2026) | 5 | Full pathway predictor is ambitious; focused site predictor is feasible |
| Publication potential (Nat Comp Sci) | 9 | "AlphaFold for allostery" framing is extremely compelling |
| **Overall** | **7.8** | Very high novelty and impact; feasibility depends on scope management |

## References

1. Li, X. et al. "Recent advances in computational strategies for allosteric site prediction: Machine learning, molecular dynamics, and network-based approaches." Drug Discovery Today, 2025.
2. AlloFusion. "Allosteric Site Prediction Based on Language Models and Multi-Feature Fusion." JCIM, 2025. https://pubs.acs.org/doi/10.1021/acs.jcim.5c01033
3. Allosteric Site Database (ASD). https://mdl.shsmu.edu.cn/ASD/
4. AlloBench. ACS Omega, 2025. https://pubs.acs.org/doi/10.1021/acsomega.5c01263
5. Ghosh, A. and Bhatt, D. "Neural relational inference to learn long-range allosteric interactions in proteins from molecular dynamics simulations." Nature Communications, 2022.
6. AlloPool. bioRxiv, 2024. https://www.biorxiv.org/content/10.1101/2024.11.01.621466v1
7. Guarnera, E. and Berezovsky, I. N. "Allosteric Sites and Allosteric Regulators." Curr. Top. Med. Chem., 2016.
8. Chen, J. et al. "Discovery of cryptic allosteric sites using reversed allosteric communication." Chemical Science, 2021. PMC8178949
9. AlloPED. "Leveraging Protein Language Models and Structure Features for Allosteric Site Prediction." 2025.
10. "Protein Language Models and Structure-Based Machine Learning for Prediction of Allosteric Binding Sites in Protein Kinases." bioRxiv, 2026. https://www.biorxiv.org/content/10.64898/2026.01.05.697819v1

---
---

# Gap 4: Conformational Ensemble-Aware Mutation Effect Prediction -- Connecting Dynamic Perturbation to Functional Consequence

---
gap_id: ensemble-mutation-effects
---

## Gap Description

### What Is Missing

Current mutation effect predictors (ESM-1v, EVE, AlphaMissense, GEMME,
ProteinGym benchmarks) operate on protein sequences and/or static structures.
They predict whether a mutation is deleterious but cannot explain HOW a mutation
disrupts function at the mechanistic level. Specifically, they cannot predict
how a mutation **reshapes the conformational ensemble** and how that reshaped
ensemble leads to altered function.

The missing capability:
1. **Mutation-induced ensemble shifts**: Given a protein and a mutation, predict
   how the population distribution across conformational states changes (not just
   delta-G of folding)
2. **Dynamic mechanism of pathogenicity**: For disease mutations, predict whether
   they act by (a) destabilizing the native fold, (b) shifting populations between
   functional states, (c) disrupting allosteric communication, (d) altering IDP
   ensemble properties, or (e) creating new aberrant conformational states
3. **Ensemble-informed variant interpretation**: Use predicted ensemble changes
   to improve clinical variant classification beyond current sequence-based methods
4. **Multi-mutation ensemble effects**: Predict how combinations of mutations
   interact through ensemble redistribution (epistatic effects through dynamics)

### Current State of the Art

**Sequence-based mutation effect prediction:**
- **AlphaMissense (2023)**: Classifies 89% of 71 million possible human missense
  variants; uses AlphaFold-derived features but not dynamics.
- **ESM-1v (2021)**: Zero-shot mutation effect prediction from PLM. No structural
  or dynamic information.
- **EVE (2021)**: Variational autoencoder on evolutionary sequences. No dynamics.
- **ProteinGym (2023)**: Comprehensive benchmark of >200 DMS datasets, but all
  methods evaluated are sequence/structure-based.

**Dynamics-aware mutation prediction (emerging):**
- **SeqDance/ESMDance (2025)**: PLMs trained on MD-derived dynamics features.
  ESMDance outperforms ESM-2 in zero-shot mutation effect prediction for designed
  and viral proteins. Predicts RMSF changes but not full ensemble shifts.
- **Quantified Dynamics-Property Relationships (2025)**: Demonstrates that
  dynamics features from MD improve prediction of engineered enzyme properties
  but requires running MD for each variant.
- **Mutational Robustness study (bioRxiv, 2026)**: Shows mutationally sensitive
  residues are dynamically rigid, establishing the dynamics-mutation connection
  but not providing a predictive tool.

**The critical gap**: No method predicts mutation-induced conformational ensemble
redistribution at scale. SeqDance/ESMDance predict proxy dynamics properties
(RMSF), not ensemble redistribution. Running MD for each variant is
computationally prohibitive for clinical variant interpretation at scale.

### Evidence the Gap Exists

1. **SeqDance paper (2025)**: "Current state-of-the-art protein deep learning
   models such as AlphaFold2 and ESM focus on static structures and sequences,
   which fail to directly capture protein dynamics." The paper demonstrates that
   dynamics features improve mutation effect prediction but acknowledges the
   approach is indirect.

2. **ProteinGym benchmark**: None of the >40 methods evaluated use conformational
   ensemble information. The entire benchmark operates on sequence or single-
   structure inputs.

3. **Quantified Dynamics-Property Relationships (PMC12606628, 2025)**: "Molecular-
   scale dynamics information has been largely excluded from state-of-the-art
   protein engineering approaches, despite evidence that mutation effects often
   cannot be explained based only on static structures."

4. **Deep mutational scanning disconnect**: ProteinGym contains >200 DMS datasets
   with mutation-function measurements. MD datasets (ATLAS, mdCATH) contain
   dynamics data for thousands of wild-type proteins. These two data sources
   have never been systematically integrated.

5. **Clinical variant interpretation gap**: ClinVar contains >1 million variants,
   most classified as "uncertain significance" (VUS). Current computational
   classifiers cannot explain mechanism. Dynamics-based mechanism classification
   would be transformative for clinical genetics.

## Why This Gap Matters

### Scientific Importance

Understanding how mutations reshape conformational ensembles is fundamental to
molecular biology. Mutations in enzymes often affect catalysis through subtle
shifts in conformational populations rather than structural disruption. Cancer
driver mutations frequently act through allosteric ensemble redistribution.
Disease mutations in IDPs alter phase separation through ensemble changes. A
method connecting mutations to ensemble changes would advance our understanding
of genotype-to-phenotype relationships at the molecular level.

### Practical Impact

- **Clinical variant interpretation**: Improve VUS classification in ClinVar
  from ~50% uncertain to substantially less by providing mechanistic explanations
- **Enzyme engineering**: Predict which mutations alter catalytic dynamics, not
  just stability
- **Cancer biology**: Identify driver mutations that act through conformational
  redistribution
- **Pharmacogenomics**: Predict which patient variants alter drug binding through
  ensemble effects

### Publication Potential

**Nature Computational Science** or **Nature Methods**. The paper would demonstrate
that incorporating dynamics information into mutation effect prediction improves
accuracy and provides mechanistic insight. The clinical relevance (VUS
classification) adds translational impact.

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

1. **Generate variant-specific ensembles at scale**: Use BioEmu or AlphaFlow to
   generate ensembles for wild-type and mutant proteins in parallel. BioEmu can
   generate thousands of structures per hour on one GPU, making variant-specific
   ensemble generation feasible.
2. **Extract ensemble-shift features**: For each mutation, compute how the
   ensemble changes: population shifts between metastable states, RMSF changes,
   pocket occupancy changes, inter-domain distance changes, dynamic contact
   map differences.
3. **Build predictive models**: Train ML models that combine ensemble-shift
   features with sequence features (ESM-2 embeddings) to predict DMS fitness
   scores (from ProteinGym) and clinical pathogenicity (from ClinVar).
4. **Classify mutation mechanisms**: Categorize mutations by their dynamic
   mechanism: stability-disrupting, population-shifting, allostery-disrupting,
   aggregation-promoting, etc.

### Required Data

- **DMS data**: ProteinGym (>200 assays, millions of variants)
- **Clinical data**: ClinVar (~1M variants), HGMD
- **Ensemble generation**: BioEmu (open-source, runs on single GPU)
- **Wild-type dynamics references**: ATLAS, mdCATH, BioEmu training data
- **Structural data**: AlphaFold DB for starting structures

### Required Compute

- Ensemble generation: BioEmu on GPU cluster; ~1,000 structures per variant per
  hour per GPU. For 10,000 variants across 50 proteins: ~500 GPU-hours.
  Feasible on HPC cluster with H200s.
- Feature extraction: CPU-parallel, moderate
- Model training: single GPU for days

### Required Methods

- BioEmu/AlphaFlow for ensemble generation
- Markov state modeling for population analysis (PyEMMA)
- Ensemble comparison metrics (Wasserstein, Jensen-Shannon divergence)
- Multi-task ML for joint fitness and pathogenicity prediction

## Feasibility Assessment

### Technical Feasibility: High
BioEmu is open-source and fast. DMS data are abundant in ProteinGym. ClinVar
is public. The ML modeling is standard.

### Timeline Feasibility: Medium
The main bottleneck is generating ensembles for thousands of variants. With
BioEmu's speed, this is feasible on a GPU cluster within weeks. Feature
extraction and model training add weeks. A focused study on 20-30 ProteinGym
proteins with ensemble-based mutation effect prediction is achievable in
summer 2026.

### Wet Lab Independence: High
All data are from published experiments (DMS assays, ClinVar annotations) and
computational tools. No new experimental data needed.

## Competitive Landscape

### Who Else Might Fill This Gap

- **SeqDance/ESMDance team**: Most aligned with this direction but focused on
  proxy properties, not full ensemble shifts.
- **BioEmu/Microsoft Research**: Could extend BioEmu to variant analysis, but
  no published indication they are doing so.
- **AlphaMissense team (Google DeepMind)**: Could add dynamics features, but
  their approach is sequence/structure-based and unlikely to pivot.
- **ProteinGym developers**: Maintain the benchmark; could add dynamics-based
  methods but focus on evaluation, not method development.

### Risk of Being Scooped: Medium
The SeqDance work signals growing interest, but full ensemble-based mutation
effect prediction has not been published. BioEmu's release democratizes
ensemble generation, making this approach newly feasible.

### Differentiation
Go beyond predicting proxy dynamic properties (RMSF) to predicting full ensemble
redistribution. Provide mechanistic classification of mutation effects (not
just "deleterious/benign" but "why").

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 8 | Ensemble-based mutation effect prediction is unexplored at scale |
| Scientific impact | 9 | Connects genotype to phenotype through dynamics; clinical relevance |
| Feasibility (computational only) | 8 | BioEmu makes variant ensembles newly feasible; DMS data are abundant |
| Timeline (summer 2026) | 7 | Focused study on 20-30 proteins is achievable; full ProteinGym coverage needs more time |
| Publication potential (Nat Comp Sci) | 8 | Strong combination of novelty, impact, and clinical relevance |
| **Overall** | **8.0** | High impact and newly feasible due to BioEmu; clear path to implementation |

## References

1. Cheng, J. et al. "Accurate proteome-wide missense variant effect prediction with AlphaMissense." Science, 2023.
2. Meier, J. et al. "Language models enable zero-shot prediction of the effects of mutations on protein function." NeurIPS, 2021.
3. Frazer, J. et al. "Disease variant prediction with deep generative models of evolutionary data." Nature, 2021.
4. Notin, P. et al. "ProteinGym: Large-Scale Benchmarks for Protein Fitness Prediction and Design." NeurIPS, 2023.
5. Chen, Z. et al. "Learning Biophysical Dynamics with Protein Language Models." 2024.
6. Chen, Z. et al. "Protein Language Models Trained on Biophysical Dynamics Inform Mutation Effects." 2025.
7. "Quantified Dynamics-Property Relationships: Data-Efficient Protein Engineering with Machine Learning of Protein Dynamics." PMC12606628, 2025.
8. "Mutational Robustness Predicts Protein Dynamics Across Natural and Designed Proteins." bioRxiv, 2026.
9. Jing, B. et al. "Scalable Emulation of Protein Equilibrium Ensembles with Generative Deep Learning (BioEmu)." Science, 2025.
10. Landrum, M. et al. "ClinVar: improvements to accessing data." Nucleic Acids Research, 2020.

---
---

# Gap 5: Bridging Coarse-Grained Dynamics and All-Atom Accuracy for Biomolecular Condensate Simulation -- Multiscale Ensemble Prediction for Phase-Separating Systems

---
gap_id: condensate-multiscale-ensembles
---

## Gap Description

### What Is Missing

Biomolecular condensates formed through liquid-liquid phase separation (LLPS)
involve hundreds to thousands of disordered protein chains interacting through
multivalent contacts. Simulating these systems requires capturing both (a) the
collective phase behavior (requiring large system sizes and long timescales,
only accessible via coarse-grained models) and (b) the atomistic details of
inter-chain contacts that drive phase separation (requiring all-atom resolution).
**No existing method can simultaneously capture both scales for condensate
systems, and current multiscale bridging approaches (backmapping from CG to
all-atom) have not been validated for condensate phases.**

Specific deficiencies:
1. **Coarse-grained models disagree on phase diagrams**: Recent benchmarks show
   that different CG force fields (HPS, Mpipi, CALVADOS) predict different
   critical temperatures and dense-phase densities for the same protein, with
   no consensus on accuracy.
2. **Backmapping from CG to all-atom is unreliable for condensates**: New
   diffusion-based backmapping methods (CGBack, MSBack) work well for single
   chains but have not been validated for dense multi-chain condensate phases
   where steric clashes and inter-chain contacts create unique challenges.
3. **No method predicts how sequence mutations alter phase behavior through
   atomistic mechanisms**: We can predict phase separation propensity from
   sequence (phase separation predictors) but cannot explain WHY at the
   atomistic level.
4. **Condensate aging/maturation is computationally inaccessible**: The
   transition from liquid-like to gel-like or amyloid-like states occurs on
   timescales far beyond current simulation capabilities.

### Current State of the Art

**CG condensate simulation:**
- **HPS model**: One-bead-per-residue CG model widely used for IDP phase
  separation. Fast but sacrifices chemical accuracy.
- **CALVADOS (2023)**: Improved CG model with better treatment of charge-charge
  interactions. Better phase diagrams but still disagreements.
- **Mpipi (2022)**: CG model incorporating pi-pi stacking interactions,
  important for FUS/TDP-43 type condensates.
- **Benchmark by Tejedor et al. (PLoS Comp Biol, 2025)**: Systematic comparison
  of residue-resolution CG models for condensate simulation reveals significant
  disagreements: "different CG force fields predict different critical
  temperatures and dense-phase densities for the same protein."

**Backmapping methods:**
- **CGBack (JCIM, 2025)**: Diffusion-based backmapping that "accurately
  backmaps both single-chain and multichain molecular systems, including
  densely packed intrinsically disordered proteins in condensates." The first
  method claiming condensate backmapping, but validation is preliminary.
- **Progressive Backmapping (bioRxiv, 2026)**: Hierarchical CG-to-all-atom
  reconstruction supporting virus-like particles; potential for condensates
  but not yet demonstrated.
- **MSBack (JCTC, 2025)**: Constrained diffusion backmapping; demonstrated on
  single proteins, not condensates.

**Machine-learned CG force fields:**
- **Nature Chemistry (2025)**: A transferable ML-CG force field trained on
  diverse all-atom simulations that captures metastable states, IDP
  fluctuations, and folding free energies. "Several orders of magnitude faster
  than all-atom." But not yet applied to condensate phase behavior.

**Phase separation prediction:**
- **SSPSPredictor (bioRxiv, 2026)**: Sequence + structure based prediction of
  phase separation propensity. Binary classification, not quantitative phase
  diagrams.
- **Phase separation propensity from sequence (PNAS, 2025)**: Predicts whether
  a protein phase separates but not the quantitative conditions or mechanisms.

### Evidence the Gap Exists

1. **Tejedor et al. (PLoS Comp Biol, 2025)**: Benchmarking CG models for
   condensates reveals "significant disagreements" between models, demonstrating
   that CG accuracy for condensates is an unsolved problem.

2. **Review by Ward & Bhatt (2025)**: "Modeling biomolecular condensates across
   scales: atomistic, coarse-grained, and data-driven approaches" identifies the
   multiscale bridging challenge as a key open problem.

3. **CGBack paper (2025)**: While claiming condensate backmapping, acknowledges
   that validation is limited to a few test cases and does not systematically
   evaluate whether atomistic properties (hydrogen bonds, pi-stacking geometries,
   cation-pi contacts) are faithfully recovered in the dense phase.

4. **Phase separation predictor evaluation (bioRxiv, 2026)**: "A Systematic
   Evaluation of Protein Phase Separation Predictors Across Diverse Protein
   Landscapes" reveals that predictors have "inherent issues" including "lack
   of protein diversity and likely inclusion of false negatives" in negative
   sets.

5. **Condensate aging gap**: No computational method can predict the liquid-to-
   gel transition timescale or the sequence determinants of condensate aging.
   This is acknowledged in recent work on charged peptides and condensate aging
   (Nature Comms, 2025).

## Why This Gap Matters

### Scientific Importance

Biomolecular condensates are one of the most important discoveries in cell
biology in the past decade. They organize cellular processes from transcription
to stress response to neurodegenerative disease. Understanding the atomistic
basis of condensate formation, composition, and aging is essential for both
basic science and therapeutic development. The IDP community and the condensate
community are currently using incompatible simulation scales -- bridging this
gap is a fundamental computational challenge.

### Practical Impact

- **Drug discovery for condensate diseases**: ALS, FTD, Huntington's involve
  aberrant condensate formation. Designing drugs that modulate condensate
  behavior requires atomistic understanding.
- **Condensate engineering**: Designing synthetic condensates for biotechnology
  requires predicting how sequence changes affect phase behavior at atomic
  resolution.
- **Understanding neurodegeneration**: The liquid-to-solid transition in
  TDP-43/FUS condensates drives ALS; predicting this transition computationally
  would be transformative.

### Publication Potential

A validated multiscale framework for condensate simulation -- demonstrating
that ML-enhanced backmapping faithfully recovers atomistic contacts driving
phase separation -- would be a **Nature Computational Science** or **Nature
Chemistry** paper. The condensate field is intensely active and highly cited.

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

1. **Benchmark CG models against all-atom condensate simulations**: Use the
   HPC cluster with H200 GPUs to run all-atom simulations of small condensate
   systems (5-20 chains of well-studied IDPs like FUS-LC, LAF-1 RGG) at
   microsecond scale. Compare CG models' dense-phase properties against
   all-atom references.
2. **Develop and validate condensate backmapping**: Apply CGBack and MSBack
   to CG condensate configurations. Systematically evaluate recovery of
   inter-chain hydrogen bonds, pi-stacking contacts, cation-pi interactions,
   and solvent structure. Develop condensate-specific backmapping refinement.
3. **Build a multiscale pipeline**: CG slab simulation (phase diagram) -->
   backmapping to all-atom --> short all-atom refinement. Validate that the
   pipeline preserves both macroscopic phase behavior and atomistic contacts.
4. **Apply to condensate mutants**: Predict how disease-linked mutations
   (FUS P525L, TDP-43 Q331K) alter phase behavior through the multiscale
   pipeline.

### Required Data

- **Protein sequences**: FUS-LC, LAF-1 RGG, TDP-43 LCD, hnRNPA1 LCD,
  Ddx4 (well-studied LLPS systems)
- **CG force fields**: HPS, CALVADOS, Mpipi (all open-source)
- **All-atom force fields**: CHARMM36m or Amber ff19SB
- **Experimental validation data**: phase diagrams from published literature,
  NMR on condensate systems
- **Disease mutations**: FUS mutations from ALS databases

### Required Compute

- All-atom condensate simulations (5-20 chains, microsecond): **significant**
  GPU resources. Each system: ~10,000-50,000 atoms. With H200 GPUs, microsecond
  timescales are achievable in weeks.
- CG simulations: CPU-parallel, fast (hours per phase diagram)
- Backmapping and refinement: GPU hours per configuration
- ML force field training: multi-GPU for days

### Required Methods

- OpenMM/GROMACS for MD
- CG toolkits (HOOMD-blue for HPS/CALVADOS)
- CGBack for backmapping
- MDAnalysis for contact analysis
- ML CG force fields (Nature Chemistry 2025 model)

## Feasibility Assessment

### Technical Feasibility: Medium
All-atom condensate simulations at meaningful scale are at the edge of current
capability. With H200 GPUs, microsecond simulations of 10-20 chain systems are
feasible. Backmapping validation is straightforward. The main risk is whether
current CG-to-all-atom backmapping produces physically reasonable condensate
configurations.

### Timeline Feasibility: Medium-Low
All-atom condensate simulations take weeks per system. A focused study comparing
2-3 CG models against all-atom for 2-3 IDP systems, with backmapping validation,
is achievable in summer 2026. A comprehensive multiscale framework spanning many
systems would require longer.

### Wet Lab Independence: High
All validation uses published experimental data (phase diagrams, NMR, FRET).

## Competitive Landscape

### Who Else Might Fill This Gap

- **Zheng et al. (Nature Chemistry, 2025)**: Their ML-CG force field is the
  closest to enabling multiscale condensate simulation but has not been applied
  to condensates.
- **CGBack developers**: Could extend their condensate backmapping validation
  but focus is on the backmapping method, not the full multiscale pipeline.
- **Condensate simulation groups (Dignon, Mittal, Pappu)**: Experts in CG
  condensate simulation but generally do not bridge to all-atom.
- **Lindorff-Larsen group**: Expert in IDP simulation and force fields; could
  address the CG accuracy question.

### Risk of Being Scooped: Medium-Low
The multiscale condensate problem is well-recognized but computationally
demanding. Few groups have both the condensate expertise and the GPU resources
for all-atom condensate simulations.

### Differentiation
The key contribution would be the first systematic validation of whether CG
condensate simulations, when backmapped to all-atom, faithfully represent the
atomistic contacts that drive phase separation. This bridges two communities
(CG simulation and condensate biology) that have been operating independently.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 7 | Multiscale simulation is established but not for condensates with modern ML backmapping |
| Scientific impact | 8 | Condensates are a hot topic; atomistic understanding is needed |
| Feasibility (computational only) | 6 | All-atom condensate simulations are computationally demanding; H200 GPUs help |
| Timeline (summer 2026) | 5 | Focused study on 2-3 systems is achievable; comprehensive framework needs more time |
| Publication potential (Nat Comp Sci) | 7 | Highly relevant to the condensate community; multiscale methods are of broad interest |
| **Overall** | **6.6** | Important gap with high scientific impact but more challenging feasibility and timeline |

## References

1. Tejedor, A.R. et al. "Benchmarking residue-resolution protein coarse-grained models for simulations of biomolecular condensates." PLoS Computational Biology, 2025.
2. Ward, M. and Bhatt, R. "Modeling biomolecular condensates across scales: atomistic, coarse-grained, and data-driven approaches." 2025.
3. CGBack. JCIM, 2025. https://pubs.acs.org/doi/10.1021/acs.jcim.5c01281
4. Progressive Backmapping. bioRxiv, 2026. https://www.biorxiv.org/content/10.64898/2026.03.02.709104v1
5. MSBack. JCTC, 2025. https://pubs.acs.org/doi/10.1021/acs.jctc.5c00459
6. Zheng, L. et al. "Navigating protein landscapes with a machine-learned transferable coarse-grained model." Nature Chemistry, 2025.
7. "A Systematic Evaluation of Protein Phase Separation Predictors Across Diverse Protein Landscapes." bioRxiv, 2026.
8. "Prediction of phase-separation propensities of disordered proteins from sequence." PNAS, 2025.
9. SSPSPredictor. bioRxiv, 2026.
10. "Charged peptides enriched in aromatic residues decelerate condensate ageing driven by cross-beta-sheet formation." Nature Communications, 2025.

---
---

# Cross-Cutting Summary and Prioritization

## Gap Ranking (protdyn perspective)

| Rank | Gap ID | Overall Score | Key Strength | Key Risk |
|------|--------|--------------|-------------|---------|
| 1 | dynamics-to-function | 8.0 | Addresses central post-AF challenge | Microsoft Research competition |
| 2 | ensemble-mutation-effects | 8.0 | BioEmu makes it newly feasible; clinical impact | SeqDance team may extend their work |
| 3 | allostery-from-sequence | 7.8 | Very high novelty; "AF for allostery" framing | Timeline risk for full pathway prediction |
| 4 | ensemble-evaluation-framework | 7.6 | Community infrastructure; highly citable | PeptoneBench is moving in this direction |
| 5 | condensate-multiscale-ensembles | 6.6 | Hot topic; needed science | Compute-intensive; timeline challenging |

## Cross-Domain Connections

1. **Gaps 1 and 4 are synergistic**: A dynamics-to-function framework (Gap 1)
   naturally enables ensemble-aware mutation effect prediction (Gap 4). They
   could be a single large project.

2. **Gap 2 enables all others**: A standardized evaluation framework (Gap 2) is
   needed to rigorously validate any ensemble-based prediction method. It could
   be the foundational contribution upon which Gaps 1, 3, and 4 build.

3. **Gap 3 connects to translational medicine**: Sequence-based allosteric
   prediction (Gap 3) has direct applications in drug target identification
   and variant interpretation, connecting to the translational comp bio agenda.

4. **Gap 5 connects to systems biology**: Condensate simulation (Gap 5) bridges
   molecular-scale dynamics to cellular-scale organization, connecting to the
   systems biology and network analysis agendas.

## Recommended Combinations for Maximum Impact

**Option A (Highest Impact, Moderate Risk)**: Combine Gaps 1 + 4 into a
"Dynamics-to-Function" project that uses conformational ensembles to predict
mutation effects. Build the benchmark (Gap 2) as the evaluation framework.
This yields a single coherent project with Nature Comp Sci potential.

**Option B (Highest Novelty, Higher Risk)**: Gap 3 as a standalone
"AlphaFold for Allostery" project. Very high ceiling but more technically
challenging and competitive.

**Option C (Infrastructure Play, Lower Risk)**: Gap 2 as a community
benchmark. Lower ceiling than the others but high probability of impact
and citation.
