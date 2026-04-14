---
agent: multisim
round: 1
date: 2026-04-14
type: gap-report
---

# Multi-Scale Simulation Expert -- Round 1 Gap Report

## Reporting Agent

**Agent:** Multi-Scale Simulation Expert (multisim)
**Expertise:** MD at scale, ML force fields, free energy methods, QM/MM, coarse-grained models, cellular-scale simulation
**Date:** 2026-04-14
**Round:** 1

---

# Gap 1: A Foundation ML Force Field for Biomolecular Dynamics with Reactive Chemistry and Long-Range Interactions

## Gap ID: `mlff-bio-reactive`

## Gap Description

### What Is Missing

There is no single machine-learned force field (MLFF) that simultaneously achieves: (1) quantum-mechanical accuracy for covalent and non-covalent interactions across diverse biomolecular systems (proteins, nucleic acids, lipids, carbohydrates, cofactors, metal centers); (2) correct treatment of long-range electrostatics and dispersion critical for condensed-phase biomolecular simulations; (3) capability to model reactive events such as proton transfers, bond breaking/formation in enzyme catalysis and post-translational modifications; and (4) computational efficiency sufficient for microsecond-scale simulations of systems with 100,000+ atoms on modern GPU hardware. Current universal MLFFs are either trained on materials data (MACE-MP-0, UMA) and fail on biomolecular specifics, or are biomolecule-focused but lack reactivity (GEMS, SO3LR, MACE-OFF) or long-range physics.

### Current State of the Art

**Universal MLFFs for materials (not biomolecules):**

- **MACE-MP-0** (Batatia et al., 2024): A foundation model trained on 1.6M bulk crystals from the Materials Project (MPTrj dataset), covering 89 elements. Demonstrates qualitative accuracy on diverse systems including a small protein, but trained against PBE DFT data, which is quite inaccurate for barrier heights and intermolecular interactions. Densities of ethanol-water mixtures are qualitatively incorrect (Batatia et al., J. Chem. Phys. 2024).
- **UMA** (Meta FAIR, 2025): Universal Model for Atoms trained on >30 billion atoms from OMol25 (100M+ DFT calculations at wB97M-V/def2-TZVPD), OC20, ODAC23, OMat24 datasets. Uses a novel Mixture of Linear Experts (MoLE) architecture. Covers 83 elements and includes biomolecules, but has not been validated for long biomolecular MD trajectories or reactive chemistry (Kolluru et al., arXiv:2505.08762, 2025).
- **SO3LR** (Kabylda et al., JACS 2025): Combines SO3krates neural network for semilocal interactions with universal pairwise force fields for long-range electrostatics and dispersion. Trained on 4 million neutral and charged molecular complexes at PBE0+MBD level. Scales to ~200k atoms at ~3 us/atom/step on a single H100 GPU. Demonstrated on crambin protein, N-linked glycoprotein, and lipid bilayer -- but only nanosecond-scale simulations, no reactive chemistry, no nucleic acids, no large proteins.

**Biomolecule-specific MLFFs:**

- **AI2BMD** (Zhang et al., Nature 2024): Microsoft's ab initio biomolecular dynamics system. Uses protein fragmentation and ML force fields to achieve DFT-level accuracy for proteins up to 13,728 atoms in explicit solvent. Orders of magnitude faster than DFT but still much slower than classical MD. Limited to proteins -- no nucleic acids, no ligands, no reactive chemistry demonstrated.
- **GEMS** (Unke et al., Science Advances 2024, Google DeepMind): Fragment-based MLFF enabling nanosecond-scale MD of >25,000 atoms at near-ab-initio quality. Correctly predicts helical motif oscillations in polyalanine. Limited system size and no reactive chemistry.
- **MACE-OFF** (Kovacs et al., JACS 2024): Transferable ML force fields for organic molecules with accurate gas- and condensed-phase property predictions. Short-range only -- no long-range electrostatics treatment.
- **ANI-2x** (Devereux et al., 2020): Neural network potential covering H, C, N, O, S, F, Cl. Approximately 8x slower than classical MM on NVIDIA RTX 4090; limited to 0.2-0.3 fs timesteps vs. 2-4 fs for classical MD. No metals, no nucleic acid-specific chemistry.

**Long-range interaction solutions:**

- **Latent Ewald Summation (LES)** (2025): Compatible with MACE, NequIP, Allegro, and other short-range MLIPs. Infers electrostatic interactions and polarization from energy/force training data. A promising framework, but not yet demonstrated for large-scale biomolecular dynamics with reactive chemistry.

**Reactive ML force fields:**

- **Reactive MLIPs** (Chemical Reviews 2025): ML force fields can in principle describe bond breaking/formation since they learn from reference data without preconceived bonding patterns. However, most current implementations are limited to small systems (heterogeneous catalysis surfaces, small molecules) and not biomolecular environments.

### Evidence the Gap Exists

1. No published work demonstrates a single MLFF running stable microsecond-scale MD of a protein-ligand complex in explicit solvent with reactive proton transfer events, despite individual components existing.
2. The 2025 review "The Continuous Evolution of Biomolecular Force Fields" (Structure, 2025) explicitly identifies the trade-offs among accuracy, efficiency, and generalizability as "currently hindering broader adoption" of MLFFs.
3. AI2BMD (Nature, 2024) -- the most advanced biomolecular MLFF -- is limited to proteins in explicit solvent modeled by a polarizable force field. No ligands, no nucleic acids, no membranes, no reactive events.
4. The TEA Challenge 2023 benchmark (Chem. Sci. 2025) showed that ML force fields still struggle with reactive barriers, molecular crystals, and interfacial systems.
5. AMP-BMS/MM (ChemRxiv, 2026) proposes a multiscale neural network potential for protein dynamics and enzymatic reactions, indicating active work but no mature solution exists.

## Why This Gap Matters

### Scientific Importance

Enzyme catalysis, post-translational modifications, and proton-coupled electron transfer are central to biology. Classical force fields cannot model bond breaking. QM/MM is too expensive for extensive sampling. A reactive MLFF that handles full biomolecular systems would transform our ability to study catalytic mechanisms, drug metabolism, and chemical biology at scale.

### Practical Impact

Drug discovery requires accurate modeling of protein-ligand binding where charge redistribution, proton transfers, and covalent bond formation are common (covalent inhibitors represent ~30% of FDA-approved drugs in recent years). A reactive biomolecular MLFF would enable FEP calculations on covalent inhibitors and metalloproteins that are currently out of reach.

### Publication Potential

A foundation biomolecular MLFF with reactive capability would be a landmark paper. Target venues: Nature, Science, Nature Computational Science. The community is clearly moving in this direction -- AI2BMD in Nature 2024, GEMS in Science Advances 2024, SO3LR in JACS 2025.

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

Build on fragment-based MLFF architectures (AI2BMD/GEMS style) combined with long-range interaction frameworks (LES) and reactive training data from QM calculations of enzymatic reaction pathways. Train on diverse biomolecular fragments spanning proteins, nucleic acids, lipids, cofactors, and metal centers with reactive events.

### Required Data

- OMol25 dataset (100M+ DFT calculations, publicly available from Meta)
- QM datasets for enzyme reaction pathways (would need generation via DFT/CASSCF)
- mdCATH (5,398 protein domain trajectories), ATLAS (1,390+ protein trajectories)
- Existing QM/MM reaction path databases

### Required Compute

- Training: Estimated 10,000-50,000 H200 GPU-hours for foundation model training
- Validation MD: 1,000-5,000 GPU-hours for benchmark simulations
- QM reference data generation: 50,000-100,000 CPU-hours for enzyme reaction paths

### Required Methods

- Equivariant message-passing architectures (MACE, NequIP, Allegro)
- Fragment decomposition schemes
- Long-range electrostatics frameworks (LES, Ewald summation)
- Active learning for reactive chemistry sampling
- Multi-task learning across energy, forces, and charges

## Feasibility Assessment

### Technical Feasibility: Medium

All individual components exist (equivariant architectures, fragment schemes, LES, reactive training data), but integrating them into a single transferable model for diverse biomolecular systems is a significant engineering and scientific challenge. The MoLE architecture from UMA shows how to handle heterogeneous training data.

### Timeline Feasibility: Low-Medium

Building a truly universal reactive biomolecular MLFF from scratch in a single summer is extremely ambitious. A more feasible scope would be to demonstrate the concept on a specific class of enzymes or a particular reactive mechanism, benchmarking against QM/MM gold standards.

### Wet Lab Independence: High

Entirely computational. Validation against published experimental observables (J-couplings, NMR chemical shifts, kinetic isotope effects, reaction rates).

## Competitive Landscape

### Who Else Might Fill This Gap

- Microsoft Research (AI2BMD team) -- best positioned with existing infrastructure
- Google DeepMind (GEMS team) -- strong ML expertise and compute
- Meta FAIR (UMA/OMol25 team) -- massive training data, architecture innovation
- Cambridge group (MACE developers) -- leading MLIP architecture

### Risk of Being Scooped

**High.** This is a recognized grand challenge and multiple well-resourced groups are converging on it. The probability of a fully general solution appearing within 12 months from a major lab is moderate, but a focused demonstration on a specific reactive biomolecular system class remains achievable.

### Differentiation

Focus on a specific underexplored niche: reactive chemistry in enzyme active sites with explicit long-range electrostatics, benchmarked against experimental kinetic isotope effects -- a validation approach no existing MLFF study has done systematically.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 7 | Components exist individually; integration is the novelty |
| Scientific impact | 9 | Would transform computational enzymology and drug design |
| Feasibility (computational only) | 5 | Very ambitious; need to scope carefully |
| Timeline (summer 2026) | 4 | Full solution unlikely in months; focused demo possible |
| Publication potential (Nat Comp Sci) | 8 | Clear Nature-tier if successful |
| **Overall** | **6.6** | High impact but significant feasibility risk |

---

# Gap 2: Proteome-Scale Dynamics -- Connecting Sequence to Conformational Ensembles Across All Human Proteins

## Gap ID: `proteome-dynamics-atlas`

## Gap Description

### What Is Missing

Despite the AlphaFold revolution providing static structures for essentially every known protein, we lack a comprehensive, validated atlas of protein conformational dynamics at the proteome scale. Current dynamics databases cover only a tiny fraction of known proteins: ATLAS has ~1,900 proteins, mdCATH has 5,398 domains (at artificially elevated temperatures), and both exclude membrane proteins, multi-chain complexes, and protein-ligand bound states. Furthermore, no existing approach systematically connects sequence variation (natural polymorphisms, disease mutations, evolutionary divergence) to changes in conformational ensembles. The gap is: a computational framework that predicts, at scale, how every protein in a proteome fluctuates, what alternative conformations it samples, and how mutations alter that ensemble -- validated against experimental data.

### Current State of the Art

**Dynamics databases:**

- **ATLAS** (Vander Meersche et al., Nucleic Acids Res. 2024): Contains MD trajectories for ~1,390 protein chains covering 2,150 ECOD domains, with 548 new proteins added as of November 2024. Uses all-atom MD at 300 K. Covers 97 of the 100 most common ECOD domains. Critical limitation: 1,309 folds not featured are found only in membrane proteins or lack high-resolution X-ray structures.
- **mdCATH** (Aloy et al., Scientific Data 2024): 5,398 protein domains simulated in 5 replicates at 5 temperatures (320-450 K), totaling >62 milliseconds of MD. Uses a single classical force field. Limited to isolated domains -- no multi-chain complexes, no ligands, no membrane environment.
- **GPCRmd** -- specialized database for G-protein-coupled receptor dynamics, narrow scope.

**AI-based dynamics prediction:**

- **BioEmu** (Microsoft, Science 2025): Diffusion model generating thousands of protein equilibrium structures per hour on a single GPU. Trained on >200 ms of MD data. Achieves 1 kcal/mol accuracy for relative free energies. 4-5 orders of magnitude speedup over MD. Limitation: single protein chains only, no multi-chain complexes, no membrane proteins, no ligand-bound states.
- **SeqDance/ESMDance** (Hou & Shen, bioRxiv 2024/2025): Protein language models trained on dynamics data from 64,403 proteins (mdCATH, ATLAS, GPCRmd, PED). Zero-shot mutation effect prediction. Captures local dynamic interactions and global conformational properties from sequence alone.
- **STARLING** (Novak et al., Nature 2026): Generates accurate intrinsically disordered region (IDR) ensembles from sequence using generative deep learning combined with physics-based force fields. Supports environmental conditioning (ionic strength). Published in Nature vol. 652, pp. 240-250.
- **CGSchNet** (Clementi group, Nature Chemistry 2025): Machine-learned transferable coarse-grained model that predicts metastable states of folded, unfolded, and intermediate structures. Several orders of magnitude faster than all-atom models. Trained on diverse all-atom protein simulations.

**Mutation effect prediction:**

- **QresFEP-2** (Communications Chemistry 2025): Hybrid-topology FEP protocol benchmarked on ~600 mutations across 10 protein systems. High accuracy with computational efficiency. But limited to thermodynamic stability -- not full ensemble changes.
- **DynaMut** and related tools: Predict mutation effects on stability and flexibility but rely on empirical approximations, not full dynamics.

### Evidence the Gap Exists

1. ATLAS explicitly excludes 1,309 protein folds found only in membrane proteins (Vander Meersche et al., 2024), which represent ~30% of all human proteins and ~60% of drug targets.
2. BioEmu cannot handle multi-chain complexes or membrane proteins (Microsoft, 2025). Most biologically interesting proteins function as complexes.
3. The human proteome contains ~20,000 proteins; ATLAS + mdCATH combined cover <7,000 non-redundant domains, leaving >65% of the proteome without any dynamics characterization.
4. No existing database or AI model captures how the conformational ensemble changes upon ligand binding, post-translational modification, or disease mutation at proteome scale.
5. SeqDance/ESMDance demonstrate that dynamics-trained language models outperform structure-based approaches for mutation effects, suggesting sequence-dynamics relationships are learnable but current training data is insufficient (64,403 proteins, mostly from classical MD with known force field artifacts).
6. The "continuous evolution of biomolecular force fields" review (Structure 2025) identifies the synergy between deep learning and physics-based approaches for conformational dynamics as a critical future direction.

## Why This Gap Matters

### Scientific Importance

Proteins are dynamic machines. A static structure tells you what a protein looks like, not what it does. Conformational ensembles determine enzyme catalytic rates, allosteric regulation, drug binding, and immune recognition. Without proteome-scale dynamics, we have an incomplete understanding of biology -- analogous to having a genome sequence but no gene expression data.

### Practical Impact

- Drug discovery: ~60% of drug targets are membrane proteins with no dynamics characterization in existing databases.
- Precision medicine: Predicting how patient-specific mutations alter protein dynamics would transform variant interpretation (ClinVar has >2 million variants of uncertain significance).
- Protein engineering: Rational design of thermostable, catalytically active, or allosterically regulated proteins requires understanding the conformational landscape.

### Publication Potential

A proteome-scale dynamics atlas validated against experimental data would be transformative. The analogy to AlphaFold's structure revolution -- but for dynamics -- positions this as a potential Nature or Science paper. BioEmu (Science 2025) and STARLING (Nature 2026) demonstrate the appetite of top journals for this direction.

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

1. Generate a large-scale MD dataset covering underrepresented protein classes: membrane proteins in lipid bilayers, multi-chain complexes, protein-ligand bound states, using enhanced sampling and ML-accelerated MD.
2. Train a foundation model (extending BioEmu/CGSchNet/ESMDance architectures) on this expanded dataset plus existing databases.
3. Predict conformational ensembles for all ~20,000 human proteins and systematically assess mutation effects.
4. Validate against available experimental data: NMR order parameters, SAXS profiles, hydrogen-deuterium exchange (HDX-MS), cryo-EM heterogeneity.

### Required Data

- AlphaFold Protein Structure Database (all human proteins)
- ATLAS, mdCATH, GPCRmd trajectories (publicly available)
- PDB (experimental structures for validation)
- ClinVar, gnomAD (mutation catalogs)
- NMR relaxation data from BMRB
- SAXS data from SASBDB

### Required Compute

- MD data generation: 100,000-500,000 GPU-hours for enhanced sampling of ~5,000 underrepresented proteins (membrane proteins, complexes)
- Model training: 10,000-50,000 GPU-hours for foundation dynamics model
- Inference: ~1,000 GPU-hours for proteome-wide prediction

### Required Methods

- Enhanced sampling (metadynamics, replica exchange, adaptive sampling)
- ML-accelerated MD (coarse-grained models, BioEmu-style generative models)
- Protein language models (ESM-2, sequence-dynamics mapping)
- Experimental validation pipelines (NMR, SAXS forward models)

## Feasibility Assessment

### Technical Feasibility: Medium-High

BioEmu demonstrates that generative models can emulate protein equilibrium ensembles. CGSchNet shows transferable CG models work. The primary challenge is extending to membrane proteins and complexes, which require more complex simulation setups. Existing tools (CHARMM-GUI for membrane systems, Martini 3 for CG) provide infrastructure.

### Timeline Feasibility: Medium

A focused version targeting a specific protein family (e.g., all human kinases, or all GPCRs) is achievable in summer 2026. Full proteome coverage would require a longer timeline.

### Wet Lab Independence: High

All validation uses published experimental data (NMR, SAXS, HDX-MS, cryo-EM) and public databases. No new experiments needed.

## Competitive Landscape

### Who Else Might Fill This Gap

- Microsoft Research (BioEmu team) -- actively expanding BioEmu; most likely to extend to complexes
- DeepMind -- AlphaFold successor with dynamics could appear any time
- Clementi group (FU Berlin) -- CGSchNet provides transferable CG models
- D.E. Shaw Research -- massive MD compute but typically not open-access

### Risk of Being Scooped

**High** for generic proteome dynamics prediction. **Medium** for the specific integration of mutation effects with dynamics at scale, validated against diverse experimental data types.

### Differentiation

Focus on the mutation-dynamics-phenotype axis: systematically predict how disease-associated mutations alter conformational ensembles and connect to clinical phenotypes. No existing work does this at scale with physics-based validation.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 7 | BioEmu/CGSchNet exist; mutation-dynamics integration at scale is new |
| Scientific impact | 9 | Would be the "AlphaFold for dynamics" |
| Feasibility (computational only) | 7 | Building on existing infrastructure; data generation is main cost |
| Timeline (summer 2026) | 6 | Focused scope (one protein family + mutations) is feasible |
| Publication potential (Nat Comp Sci) | 9 | High-profile direction, proven journal interest |
| **Overall** | **7.6** | Excellent combination of impact and feasibility |

---

# Gap 3: Automated Multi-Resolution Simulation -- Seamlessly Bridging Quantum, Atomistic, Coarse-Grained, and Cellular Scales

## Gap ID: `auto-multiscale-bridge`

## Gap Description

### What Is Missing

There is no automated computational framework that can seamlessly and adaptively switch between resolution levels -- from quantum mechanics (QM) in an enzyme active site, to all-atom molecular dynamics (MD) in the surrounding protein, to coarse-grained (CG) simulation of a membrane or crowded cellular environment, to agent-based or continuum models at the cellular scale -- with the scale transitions driven by the physics itself rather than manual user setup. Current multi-scale approaches require extensive expert configuration, have ad hoc coupling between scales, and cannot dynamically adjust resolution based on where interesting chemistry or dynamics is occurring. The gap is a learnable, physics-informed scale-bridging framework that automatically determines what resolution is needed where and when.

### Current State of the Art

**Adaptive resolution MD:**

- **AdResS** (Praprotnik et al., 2005-2021): Adaptive resolution molecular dynamics that smoothly couples atomistic and coarse-grained regions with molecules freely diffusing between them. Uses a "healing region" for smooth transitions. Demonstrated on liquids and simple biomolecular systems. Limitation: requires manual definition of regions, limited to two scales (AA/CG), no QM coupling, no cellular scale.

**Multi-scale frameworks:**

- **MuMMI** (Multiscale Machine-Learned Modeling Infrastructure): An automated ensemble-based multiscale approach connecting three resolution scales. The continuum scale can simulate milliseconds of time. Developed at Lawrence Livermore National Laboratory. Impressive but highly specialized (RAS-membrane signaling), requires supercomputer-scale resources, and the coupling between scales is pipeline-based rather than seamless.
- **GOMartini 3** (Nature Communications 2025): Combines elastic network models with Martini 3 for large conformational changes. Improved over previous versions but still a specific two-scale coupling.
- **GENESIS CGDYN** (Nature Communications 2024): Large-scale coarse-grained MD simulation with dynamic load balancing for heterogeneous biomolecular systems. Impressive scaling but single-resolution CG.

**ML-driven scale bridging:**

- **CGSchNet** (Nature Chemistry 2025): Transferable CG model trained on all-atom data. Successful backmapping demonstrated. But only one-way: AA to CG, with separate backmapping.
- **CGBack** (JCIM 2025): Diffusion model for backmapping large-scale CG molecular systems back to all-atom. Addresses the resolution conversion problem but not adaptive, concurrent multi-scale simulation.
- **MSBack** (JCTC 2025): Backmaps highly coarse-grained proteins using constrained diffusion. Again, post-hoc backmapping, not concurrent multi-resolution.

**Whole-cell simulations:**

- **Minimal cell digital twin** (University of Illinois, 2025/2026): Particle-based digital twin of JCVI-syn3A tracking nearly all molecules through a complete cell cycle. Takes ~6 days of GPU compute for 105 minutes of biology. Remarkable but uses highly simplified interaction models -- not physics-based force fields.
- **E. coli whole-cell model** (Covert lab, UC San Diego): Ongoing DARPA-funded $4.1M project. Uses kinetic ODEs, not spatial simulation.

**Crowded cellular environment simulations:**

- Recent review (JCIM 2024) describes progress in modeling macromolecular crowding across spatiotemporal scales. Key challenge identified: "lack of visualization, simulation, and characterization methods for such large, dense, and complex models."

### Evidence the Gap Exists

1. No published framework automatically adjusts resolution during a simulation based on detected reactive events, conformational changes, or binding events. All existing approaches require pre-specified resolution zones.
2. MuMMI is pipeline-based: run CG, analyze, pick hotspots, run AA, feed back. Not concurrent adaptive resolution.
3. The whole-cell digital twin (2025/2026) uses simplified particle-based models because no multi-resolution framework exists to deploy physics-based force fields at cellular scale.
4. The 2025 review on advances in molecular simulations (JPCL 2025) identifies "merging physical models, experiments, and AI to tackle multiscale complexity" as a frontier challenge.
5. No existing tool can start a simulation of a crowded cytoplasm in CG resolution and automatically promote a protein-protein encounter to all-atom resolution when a binding event begins -- this workflow requires manual intervention.
6. The Martini 3 force field, the most widely used CG model for biomolecular simulations, still has fundamental accuracy limitations: overestimating protein-protein interactions (Nature Communications 2024), producing too-compact IDP conformations (Nature Communications 2025), and failing to reproduce phospholipid flip-flop (JCTC 2025).

## Why This Gap Matters

### Scientific Importance

Biology operates across scales: quantum effects in enzyme active sites determine reaction rates, which control metabolic fluxes at the cellular level. Understanding emergent properties requires simulating across scales concurrently. No current computational approach can do this in a principled, automated way.

### Practical Impact

- Drug design in realistic cellular context: How does crowding affect drug-target binding?
- Understanding allosteric signaling: Conformational changes propagate from atomic to cellular scales
- Virtual cell modeling: Current whole-cell models are kinetic, not spatial-structural. Bridging MD to cellular dynamics would enable the next generation of virtual cells.

### Publication Potential

An automated multi-resolution framework with physics-informed scale switching would be a methodological landmark. Target venues: Nature Methods, Nature Computational Science. The virtual cell/digital twin narrative has extremely high visibility (Nature Biotechnology, Science).

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

Develop a learned scale-switching oracle: a neural network that, given local molecular context, predicts when higher resolution is needed (e.g., detecting a forming contact that requires AA or QM treatment). Combine with existing ML backmapping (CGBack/MSBack) and forward-mapping tools to enable on-the-fly resolution changes during simulation. Demonstrate on a biologically meaningful system like enzyme function in a crowded cytoplasm.

### Required Data

- Multi-resolution training data: concurrent AA and CG simulations of the same systems
- QM/MM reaction path data for enzyme systems
- Crowded cellular environment models (from Martini-based whole-cytoplasm simulations)

### Required Compute

- Training data generation: 50,000-200,000 GPU-hours for parallel AA/CG simulations
- Scale-switching oracle training: 5,000-10,000 GPU-hours
- Demonstration simulations: 10,000-50,000 GPU-hours

### Required Methods

- ML coarse-graining (CGSchNet, Martini 3)
- ML backmapping (CGBack, MSBack diffusion models)
- Anomaly/event detection networks
- Adaptive resolution MD infrastructure
- GPU-accelerated MD engines (OpenMM, GROMACS)

## Feasibility Assessment

### Technical Feasibility: Low-Medium

This is a grand challenge. Individual components exist (ML CG, ML backmapping, adaptive resolution MD) but have never been integrated into an automated, learned framework. The scale-switching oracle is conceptually novel and would need significant development.

### Timeline Feasibility: Low

Full realization is a multi-year effort. A proof-of-concept demonstrating learned scale switching between CG and AA for a single protein system might be achievable in summer 2026.

### Wet Lab Independence: High

Entirely computational.

## Competitive Landscape

### Who Else Might Fill This Gap

- Lawrence Livermore (MuMMI team) -- most experience with multi-scale pipelines
- Praprotnik group -- AdResS developers
- Clementi group -- CGSchNet could extend to adaptive resolution
- Noe group (FU Berlin) -- ML enhanced sampling, potential dynamics experts

### Risk of Being Scooped

**Low-Medium.** This is recognized as important but extremely difficult. No group has published a convincing automated adaptive resolution framework.

### Differentiation

Use modern ML (diffusion model backmapping, learned event detection) rather than the traditional force-matching approaches. The ML angle is what makes this potentially tractable.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 9 | No existing automated multi-resolution framework |
| Scientific impact | 10 | Would transform multi-scale simulation methodology |
| Feasibility (computational only) | 4 | Grand challenge; proof-of-concept feasible |
| Timeline (summer 2026) | 3 | Only a proof-of-concept in months |
| Publication potential (Nat Comp Sci) | 8 | Methodological landmark if achieved |
| **Overall** | **6.8** | Very high impact but high risk |

---

# Gap 4: High-Throughput Free Energy Calculations at Proteome Scale -- From 30 Compounds to 30,000

## Gap ID: `fep-proteome-scale`

## Gap Description

### What Is Missing

Free energy perturbation (FEP) calculations are the gold standard for predicting relative binding affinities in drug discovery, but current workflows are limited to evaluating ~30-100 compounds per target per week, with significant expert intervention required for each setup. There is no automated, high-throughput FEP platform that can: (1) evaluate thousands to tens of thousands of compounds against a single target; (2) simultaneously assess selectivity across multiple targets (the full kinome, for example); (3) handle challenging cases like protein mutations, covalent binders, metalloproteins, and membrane-bound targets without manual intervention; and (4) achieve consistent sub-kcal/mol accuracy across diverse chemical series. The gap between FEP's theoretical promise and practical deployment at scale remains large.

### Current State of the Art

**Open-source FEP platforms:**

- **OpenFE** (2025): The recent large-scale collaborative assessment involving 15 pharmaceutical companies benchmarked OpenFE across >1,700 ligands. Results: public dataset weighted RMSE = 1.73 [1.53, 1.96] kcal/mol (10/58 systems sub-kcal/mol); private dataset weighted RMSE = 2.44 [1.94, 3.06] kcal/mol (2/37 systems sub-kcal/mol). Conclusion: "ready for large-scale industrial applications" but performance is system-dependent with no single dominant error source.
- **PyAutoFEP**: Automated workflow for GROMACS with enhanced sampling integration.
- **Perses** (from OpenMM): Relative binding free energy calculations with automated atom mapping.

**Scaling innovations:**

- **State Function-based Correction (SFC)** (JPCL 2025): Maintains consistent computational efficiency across increasing graph sizes, enabling perturbation networks with up to 50,000 molecules. Key innovation: treats free energy as a state function, correcting cycle closure errors systematically.
- **QligFEP v2.1.0**: Uses spherical boundary conditions, simulating ~6,250 atoms per perturbation leg, completing in <2 hours, costing <$1 on AWS per transformation.
- **FEP+ (Schrodinger)**: Commercial state-of-the-art, achieving RMSE ~1.0-1.5 kcal/mol on well-behaved systems, but requires commercial license.

**ML-accelerated FEP:**

- Machine learning integration (JCIM 2025 review): Active learning and deep learning enhance FEP workflows through sampling strategies, protocol optimization, and force field development. But this is still in early stages.
- NNP/MM hybrid approaches: Using ANI-2x for ligand forces in FEP calculations reduces binding free energy errors from 0.97 to 0.47 kcal/mol (2024 study), but at ~8x computational cost.

**Selectivity and multi-target:**

- Alchemical receptor hopping/swapping (JPCB 2024): Can model binding selectivity between two receptors, yielding selectivity free energies. But limited to pairs, not proteome-scale.
- Absolute binding free energy (ABFE) for multiple proteins (JCIM 2024): Examined selectivity by calculating ABFE to multiple proteins, but prohibitively expensive per compound.

**Mutation effects:**

- **QresFEP-2** (Communications Chemistry 2025): Hybrid-topology FEP for protein stability mutations. Benchmarked on ~600 mutations across 10 proteins. Highest computational efficiency among available FEP protocols.

### Evidence the Gap Exists

1. OpenFE achieves sub-kcal/mol accuracy on only 17% of public benchmark systems and 5% of private systems (2025 large-scale assessment). The median error of ~2 kcal/mol means FEP cannot reliably rank compounds in many practical settings.
2. Current industry practice runs FEP on ~30-100 compounds per project (Cresset/AstraZeneca estimate: ~10 hours per ligand). At this rate, screening a 10,000-compound virtual library takes 100,000 hours = 11.4 years on a single GPU.
3. No published FEP workflow handles covalent inhibitors, metalloproteins, or membrane-bound targets (like GPCRs in a lipid bilayer) without extensive manual setup and custom parametrization.
4. Selectivity assessment via FEP is done pair-wise (one target at a time). Assessing a compound against the full human kinome (518 kinases) is computationally intractable with current methods.
5. The gap between ML-predicted binding affinities (fast but inaccurate, typically >2 kcal/mol MAE) and FEP (accurate but slow) remains unfilled. No method combines the throughput of ML screening with the accuracy of physics-based FEP.

## Why This Gap Matters

### Scientific Importance

Understanding molecular recognition quantitatively -- not just qualitatively -- is a fundamental scientific goal. Free energy is the currency of molecular biology: binding, folding, catalysis, and signaling are all free energy-driven processes. Scaling FEP from dozens to thousands of systems would transform our understanding of molecular recognition principles.

### Practical Impact

Drug discovery spends billions on experimental screening because computational methods cannot reliably predict binding affinities at scale. A 100x scaling of FEP throughput with maintained accuracy would: (1) reduce experimental screening costs; (2) enable virtual selectivity profiling across off-target panels; (3) predict drug resistance mutations before they emerge clinically.

### Publication Potential

The OpenFE large-scale benchmark (ChemRxiv 2025) from 15 pharma companies demonstrates enormous community interest. A method that demonstrably achieves sub-kcal/mol accuracy at 10,000+ compound scale would target Nature Computational Science, Nature Chemistry, or JACS.

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

Develop an ML-accelerated FEP pipeline that: (1) uses ML force fields (MACE-OFF/ANI-2x) for rapid initial screening to select compounds likely to benefit from full FEP; (2) employs learned collective variables for enhanced sampling in FEP simulations; (3) uses graph-based perturbation networks with SFC cycle closure; (4) automates setup for challenging targets (membranes, metals, covalent binders) using AlphaFold structures + ML parametrization. Benchmark on a complete kinase selectivity panel.

### Required Data

- Public FEP benchmark datasets (OpenFE, Wang et al. JACS 2015)
- PDB structures of kinase family
- ChEMBL bioactivity data for training ML pre-screens
- Kinase selectivity panels (DiscoverX/Eurofins KINOMEscan data)

### Required Compute

- FEP calculations: 50,000-200,000 GPU-hours for 10,000+ ligand-target combinations
- ML model training: 5,000-10,000 GPU-hours
- Enhanced sampling calibration: 10,000 GPU-hours

### Required Methods

- OpenFE platform
- ML force fields (MACE-OFF, ANI-2x)
- Graph-based perturbation network design (SFC)
- ML-driven enhanced sampling
- Automated membrane system setup (CHARMM-GUI integration)

## Feasibility Assessment

### Technical Feasibility: Medium-High

OpenFE provides a solid foundation. SFC enables large perturbation networks. ML force fields for ligands are maturing. The main challenge is achieving consistent accuracy across diverse targets, especially challenging ones.

### Timeline Feasibility: Medium-High

A focused study on scaling FEP for a single target family (e.g., kinases) with ML acceleration is achievable in summer 2026. The infrastructure exists; the novelty is in the scaling and automation.

### Wet Lab Independence: High

Validation against published IC50/Ki data from ChEMBL and selectivity panels. No new experiments needed.

## Competitive Landscape

### Who Else Might Fill This Gap

- Schrodinger (FEP+) -- commercial leader, but closed-source
- OpenFE consortium (15 pharma companies) -- open-source, active development
- Rowan Sciences -- commercial ML-accelerated FEP platform
- Multiple academic groups (Jorgensen, Cournia, Gilson)

### Risk of Being Scooped

**Medium-High.** The scaling direction is obvious and many groups are working on it. But the combination of ML acceleration + automated setup for challenging targets + comprehensive selectivity assessment at scale has not been demonstrated.

### Differentiation

Focus on the selectivity problem: not just binding affinity to one target, but systematic profiling across an entire target family. This is what industry needs but nobody has demonstrated computationally at FEP accuracy.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 6 | Scaling existing methods; novelty in integration and automation |
| Scientific impact | 8 | Would transform structure-based drug design |
| Feasibility (computational only) | 8 | Builds on mature tools; mainly an engineering + benchmarking effort |
| Timeline (summer 2026) | 7 | Focused kinase selectivity study achievable |
| Publication potential (Nat Comp Sci) | 7 | Strong if benchmark is comprehensive and results beat state of art |
| **Overall** | **7.2** | Very good balance of impact and feasibility |

---

# Gap 5: Connecting ML Force Field Dynamics to Experimentally Observable Properties -- The Validation Crisis

## Gap ID: `mlff-validation-crisis`

## Gap Description

### What Is Missing

The field of ML force fields is producing increasingly powerful models (AI2BMD, GEMS, SO3LR, MACE-OFF, UMA) but there is a critical gap in systematic, rigorous validation of these models against experimental observables from molecular dynamics. Most MLFF papers validate on energy and force prediction errors (MAE on test sets) and perhaps a few bulk properties (density, RDF), but do not demonstrate that the resulting MD trajectories reproduce the rich set of experimental observables that classical force fields have been painstakingly calibrated against over decades: NMR J-couplings, chemical shifts, order parameters, NOE distances; SAXS/WAXS profiles; crystallographic B-factors; hydrogen-deuterium exchange rates; Raman and IR spectra; dielectric constants; diffusion coefficients; and free energies of solvation/binding. Without this validation, we cannot know whether ML force fields actually improve biomolecular simulations or merely achieve lower errors on energy/force test sets that do not translate to physical accuracy.

### Current State of the Art

**MLFF validation practices:**

- **AI2BMD** (Nature 2024): Validated on J-coupling, enthalpy, heat capacity, folding free energy, melting temperature, and pKa -- the most thorough biomolecular MLFF validation to date. But limited to a handful of small proteins (up to 13,728 atoms). Did not test on membrane proteins, nucleic acids, or protein-ligand systems.
- **GEMS** (Science Advances 2024): Validated on alanine dipeptide free energy landscape, polyalanine helix dynamics, liquid water RDF. Limited experimental validation.
- **SO3LR** (JACS 2025): Demonstrated "applicability and stability" in nanosecond simulations of crambin, glycoprotein, and lipid bilayer. No systematic comparison with experimental observables.
- **MACE-OFF** (JACS 2024): Validated on organic molecule gas-phase properties and molecular crystal densities. No protein dynamics validation.
- **ANI-2x**: Conformational ensemble comparison with classical force fields showed "no substantially different conformational ensembles" (2024 study), questioning whether ML potentials actually improve sampling.

**Classical force field validation:**

- AMBER ff19SB, CHARMM36m, OPLS-AA/M: Decades of careful validation against NMR relaxation, J-couplings, SAXS, crystal properties. These force fields have known failure modes (IDP collapse, helix propensity) that have been identified through extensive experimental comparison.
- The Martini 3 CG force field continues to have systematic issues: overestimating protein-protein interactions (Nature Communications 2024), producing too-compact IDP conformations (Nature Communications 2025), and limitations in phospholipid flip-flop dynamics (JCTC 2025).

**Benchmarking efforts:**

- **TEA Challenge 2023** (Chem. Sci. 2025): "Crash testing" ML force fields for molecules, materials, and interfaces. Found significant failures on reactive barriers, molecular crystals, and interfacial systems.
- **MS25 benchmark** (JCIM 2025): Materials-science-focused benchmark for MLIPs testing energy, forces, stresses, and physical observables. Showed that models reaching comparable accuracy on simple error metrics diverge on physical observables.
- No equivalent of TEA/MS25 exists specifically for biomolecular dynamics validation.

### Evidence the Gap Exists

1. The MS25 benchmark (2025) explicitly showed that test-set force/energy errors do not predict performance on physical observables like lattice constants and reaction barriers. The same is almost certainly true for biomolecular properties.
2. ANI-2x, despite having lower torsional energy errors than classical force fields, does not produce substantially different protein conformational ensembles (2024 benchmark) -- suggesting that lower energy errors do not translate to improved dynamics.
3. No MLFF paper has compared predicted NMR order parameters, SAXS profiles, or HDX protection factors against experimental data across a diverse set of proteins. AI2BMD tested J-couplings on a few small proteins; nobody has done systematic validation across protein sizes, folds, and conditions.
4. The Martini 3 validation failures (2024-2025) demonstrate that even well-established force fields have fundamental issues that are only revealed through comparison with specific experimental observables. MLFFs have not been subjected to equivalent scrutiny.
5. A 2025 user-perspective comparison of MLIPs found that "for the Al-Cu-Zr system, MACE and Allegro offered the highest accuracy, while NequIP outperformed them for Si-O" -- performance is system-specific, and we lack biomolecular-specific benchmarks to guide users.

## Why This Gap Matters

### Scientific Importance

Without rigorous validation against experimental observables, the ML force field revolution risks producing beautiful but wrong simulations. The field could spend years developing models optimized for the wrong metrics (energy/force test errors) while failing to improve the physical properties that matter for biological understanding. This is a fundamental epistemological gap in computational biophysics.

### Practical Impact

Practitioners need to know: should I use AI2BMD/GEMS/SO3LR instead of AMBER/CHARMM for my protein simulation? Currently, there is no systematic answer. This uncertainty slows adoption and prevents the community from realizing the benefits of ML force fields.

### Publication Potential

A comprehensive "crash test" of ML force fields for biomolecular dynamics -- systematically comparing MLFFs against classical force fields on dozens of experimental observables across diverse protein systems -- would be highly cited and impactful. The TEA Challenge and MS25 for materials science demonstrate the appetite for such benchmarks. A biomolecular equivalent does not exist.

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

1. Define a comprehensive biomolecular validation benchmark: select 50-100 proteins spanning diverse folds, sizes, and conditions with rich experimental data (NMR, SAXS, HDX-MS, crystallographic B-factors).
2. Run equivalent MD simulations using: (a) classical force fields (AMBER ff19SB, CHARMM36m, OPLS-AA/M); (b) ML force fields (AI2BMD, SO3LR, MACE-OFF/fine-tuned); (c) CG models (Martini 3, CGSchNet).
3. Compute forward models of experimental observables from trajectories.
4. Systematically compare, identifying where MLFFs improve over classical FF, where they fail, and what validation metrics are most informative.

### Required Data

- Protein structures from PDB (well-studied systems with rich experimental data)
- NMR data from BMRB (chemical shifts, J-couplings, order parameters, NOEs)
- SAXS profiles from SASBDB
- HDX-MS data (from published literature)
- Crystallographic B-factors from PDB

### Required Compute

- MD simulations: 50,000-100,000 GPU-hours (50 proteins x 3-4 force fields x microsecond timescales)
- Forward model calculations: 5,000 CPU-hours
- Analysis: 1,000 GPU-hours

### Required Methods

- MD engines: OpenMM (most MLFF-compatible), GROMACS
- MLFF implementations: AI2BMD, SO3LR, MACE-OFF
- Classical FF: AMBER ff19SB, CHARMM36m
- Forward models: SPARTA+ (chemical shifts), PALES (RDCs), CRYSOL (SAXS), HDXer (HDX)
- Statistical comparison frameworks

## Feasibility Assessment

### Technical Feasibility: High

All tools exist. The challenge is the scale of the benchmarking effort and ensuring apples-to-apples comparisons (same simulation protocols, same analysis pipelines).

### Timeline Feasibility: Medium-High

A focused benchmark on 20-30 proteins with 2-3 MLFFs and 2 classical FFs, comparing 5-6 experimental observable types, is achievable in summer 2026.

### Wet Lab Independence: High

Uses only published experimental data from public databases.

## Competitive Landscape

### Who Else Might Fill This Gap

- TEA Challenge organizers (Tkatchenko group) -- could extend to biomolecules
- MACE developers (Cambridge) -- have the tools but focus on materials
- Classical FF developers (AMBER, CHARMM teams) -- would benefit but may not have ML expertise
- OpenMM community -- platform enables multi-FF comparisons

### Risk of Being Scooped

**Medium.** Individual labs may compare their specific MLFF against one or two observables, but a comprehensive, systematic cross-FF biomolecular benchmark has not been attempted and requires significant expertise and compute.

### Differentiation

The breadth of the comparison: no existing study compares >2 MLFFs against >2 classical FFs on >5 experimental observable types across diverse protein systems. This is not incremental -- it answers a fundamental question the field needs answered.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 7 | Benchmarking is not new; biomolecular MLFF benchmarking at this scale is |
| Scientific impact | 8 | Would guide the entire MLFF community toward biologically relevant metrics |
| Feasibility (computational only) | 9 | All tools exist; mainly compute and careful execution |
| Timeline (summer 2026) | 8 | Focused benchmark achievable in months |
| Publication potential (Nat Comp Sci) | 8 | High citation potential; benchmark papers drive fields |
| **Overall** | **8.0** | Best overall: high impact with excellent feasibility |

---

# Summary: Ranked Gaps

| Rank | Gap ID | Title | Overall Score |
|------|--------|-------|---------------|
| 1 | `mlff-validation-crisis` | ML Force Field Validation Against Experimental Observables | 8.0 |
| 2 | `proteome-dynamics-atlas` | Proteome-Scale Dynamics with Mutation Effects | 7.6 |
| 3 | `fep-proteome-scale` | High-Throughput FEP at Proteome Scale | 7.2 |
| 4 | `auto-multiscale-bridge` | Automated Multi-Resolution Simulation | 6.8 |
| 5 | `mlff-bio-reactive` | Foundation Reactive ML Force Field for Biomolecules | 6.6 |

**Key observation:** The highest-scoring gaps balance ambition with feasibility. The MLFF validation benchmark (Gap 5) scores highest because it addresses a critical community need with excellent feasibility. The proteome-scale dynamics atlas (Gap 2) combines transformative impact with manageable scope if focused on a specific protein family. The FEP scaling gap (Gap 4) leverages mature tools for a clear practical need. The more ambitious gaps (automated multi-scale, reactive MLFF) score lower due to timeline risk but represent the highest-impact possibilities if achieved.

**Cross-domain synergies:** Gaps 1 and 5 are synergistic -- better MLFFs (Gap 1) need better validation (Gap 5), and systematic benchmarking (Gap 5) reveals what MLFFs need to improve. Gaps 2 and 4 also connect: proteome-scale dynamics (Gap 2) would benefit from high-throughput FEP (Gap 4) for mutation free energy predictions.

---

## References

1. Batatia, I. et al. "A foundation model for atomistic materials chemistry." J. Chem. Phys. 163, 184110 (2024). MACE-MP-0.
2. Batatia, I. et al. "MACE: Higher Order Equivariant Message Passing Neural Networks for Fast and Accurate Force Fields." NeurIPS 2022.
3. Kovacs, D. P. et al. "MACE-OFF: Short-Range Transferable Machine Learning Force Fields for Organic Molecules." JACS 146, 22671 (2024).
4. Kolluru, A. et al. "The Open Molecules 2025 (OMol25) Dataset, Evaluations, and Models." arXiv:2505.08762 (2025). Meta FAIR UMA.
5. Kabylda, A. et al. "Molecular Simulations with a Pretrained Neural Network and Universal Pairwise Force Fields." JACS 147, 33723 (2025). SO3LR.
6. Zhang, T. et al. "Ab initio characterization of protein molecular dynamics with AI2BMD." Nature 635, 1042-1048 (2024).
7. Unke, O. et al. "Biomolecular dynamics with machine-learned quantum-mechanical force fields trained on diverse chemical fragments." Science Advances 10, eadn4397 (2024). GEMS.
8. Vander Meersche, Y. et al. "ATLAS: protein flexibility description from atomistic molecular dynamics simulations." Nucleic Acids Research 52, D384-D392 (2024).
9. Mirarchi, A. et al. "mdCATH: A Large-Scale MD Dataset for Data-Driven Computational Biophysics." Scientific Data 11, 1275 (2024).
10. Joshi, S. Y. et al. "Scalable emulation of protein equilibrium ensembles with generative deep learning." Science (2025). BioEmu.
11. Novak, B. et al. "Accurate predictions of disordered protein ensembles with STARLING." Nature 652, 240-250 (2026).
12. Husic, B. E. et al. "Navigating protein landscapes with a machine-learned transferable coarse-grained model." Nature Chemistry (2025). CGSchNet.
13. OpenFE Consortium. "Large-scale collaborative assessment of binding free energy calculations for drug discovery using OpenFE." ChemRxiv (2025).
14. State Function-Based Correction (SFC). "A Simple and Efficient Free-Energy Correction Algorithm for Large-Scale Relative Binding Free-Energy Calculations." JPCL (2025).
15. Hou, J. & Shen, Y. "Protein Language Models Trained on Biophysical Dynamics Inform Mutation Effects." bioRxiv (2024/2025). SeqDance/ESMDance.
16. Souza, P. C. T. et al. "GOMartini 3: From large conformational changes in proteins to environmental bias corrections." Nature Communications (2025).
17. Nguyen, T. et al. "Rescaling protein-protein interactions improves Martini 3 for flexible proteins in solution." Nature Communications 15, 6745 (2024).
18. Ahmad, S. et al. "Martini3-IDP: improved Martini 3 force field for disordered proteins." Nature Communications 16, 2569 (2025).
19. GENESIS CGDYN. "Large-scale coarse-grained MD simulation with dynamic load balancing for heterogeneous biomolecular systems." Nature Communications 15, 3370 (2024).
20. Stevens, J. A. et al. "Whole-cell particle-based digital twin simulations from 4D lattice light-sheet microscopy data." bioRxiv (2025).
21. Thornton, A. et al. "Martinize2: Simplified Coarse-Grained Topology Generation for Proteins." J. Chem. Theory Comput. (2024).
22. Sabantsev, A. et al. "The continuous evolution of biomolecular force fields." Structure (2025).
23. Recent advances in AI-driven biomolecular dynamics simulations based on ML force fields. Current Opinion in Structural Biology (2025).
24. TEA Challenge 2023. "Crash testing machine learning force fields for molecules, materials, and interfaces." Chemical Science (2025).
25. MS25 Benchmark. "Materials Science-Focused Benchmark Data Set for Machine Learning Interatomic Potentials." JCIM (2025).
26. Long-range electrostatics for machine learning interatomic potentials. J. Chem. Phys. 164, 060901 (2025). LES framework.
27. Reactive Machine Learning Interatomic Potentials for Chemistry and Materials Science. Chemical Reviews (2025).
28. QresFEP-2. "Accurate predictions of protein mutational effects accelerated with a hybrid-topology free energy protocol." Communications Chemistry (2025).
29. CGBack. "Diffusion Model for Backmapping Large-Scale and Complex Coarse-Grained Molecular Systems." JCIM (2025).
30. MSBack. "Multiscale Backmapping of Highly Coarse-Grained Proteins Using Constrained Diffusion." JCTC (2025).
31. Recent Progress in Modeling and Simulation of Biomolecular Crowding and Condensation Inside Cells. JCIM (2024).
32. Enhanced Sampling in the Age of Machine Learning: Algorithms and Applications. Chemical Reviews (2025).
