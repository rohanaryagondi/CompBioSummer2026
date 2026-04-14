---
agent: genchem
round: 1
date: 2026-04-14
type: gap-report
---

# Generative Chemistry & Molecular Design -- Round 1 Gap Reports

**Agent:** Dr. Generative Chemistry & Molecular Design Expert (genchem)
**Expertise:** 15+ years in computational chemistry and molecular ML, specializing in molecular generation, scoring functions, synthesizability, and multi-objective optimization
**Date:** 2026-04-14

---

# Gap 1: The Scoring Function Generalization Crisis -- ML Scoring Functions Fail on Novel Targets Despite Benchmark Success

---
gap_id: genchem-scoring-generalization
---

## Reporting Agent

Dr. Generative Chemistry & Molecular Design Expert. I have tracked the evolution of scoring functions from empirical (Glide SP, ChemScore) through physics-based (MM-GBSA, FEP) to ML-based approaches (OnionNet, PIGNet, GenScore, GEMS). My experience spans over a decade of seeing claimed "advances" in binding affinity prediction fail to translate to real drug discovery campaigns. This gap is the single most consequential bottleneck in computational drug design, and its severity is systematically underestimated by the ML community.

## Gap Description

### What Is Missing

There is no ML scoring function that reliably generalizes from training benchmarks to truly novel protein targets. Current state-of-the-art models achieve Pearson correlations of 0.80-0.91 on CASF-2016 (the standard benchmark), yet when evaluated on genuinely unseen protein families, average correlations collapse to 0.42-0.50, with some target clusters falling below 0.05 -- essentially random performance. The field lacks: (1) a principled understanding of when and why ML scoring functions fail to generalize, (2) a systematic benchmark that measures real-world transfer rather than in-distribution interpolation, and (3) scoring architectures that encode transferable physical principles rather than memorized binding motifs.

### Current State of the Art

**Benchmark performance (CASF-2016):**
- EBA ensemble (2024): R = 0.857 (PDBbind2016 training), R = 0.914 (PDBbind2020 training) (Harren et al., 2024, WIREs Comp Mol Sci)
- GEMS (2025): R = 0.815 (Generalization Beyond Benchmarks, arXiv:2512.05386)
- GEMSATOMICA (2025): R = 0.808 (ibid.)
- iScore (2025): R = 0.814 (JCIM, 2025)
- PIGNet2 (2024): comparable to GenScore (Digital Discovery, RSC, 2024)
- OnionNet: R = 0.78 on CASF-2013 (ACS Omega, 2019)

**Real-world performance on novel targets:**
- GEMS average on unseen target clusters: R = 0.470 -- a 42% drop from CASF performance (arXiv:2512.05386, Generalization Beyond Benchmarks, 2025)
- GEMSATOMICA average: R = 0.498 (ibid.)
- GenScore average on unseen targets: R = 0.422 (ibid.)
- GenScore on cluster 3F3E: R = 0.047 -- essentially random (ibid.)
- Best single novel target: R = 0.736 (ibid.)
- Multiple clusters (3DD0, 2P15, 3F3E, 3O9I) with R < 0.5 for ALL tested methods (ibid.)

**Physics-based methods for comparison:**
- FEP+ (Schrodinger, commercial): ~1 kcal/mol accuracy on congeneric series, but computationally expensive (24h on 8 GPUs for 4 perturbations)
- OpenFE (open source, 2025): RMSE 1.73 kcal/mol (public dataset), 2.44 kcal/mol (private dataset) across 1,700+ ligands (ChemRxiv, 2025)
- AEV-PLIG (2025): After data augmentation, weighted mean PCC improved from 0.41 to 0.59 on FEP benchmarks; 400,000x faster than FEP+ (Communications Chemistry, Nature, 2025)

**The inter-protein scoring noise problem:**
A 2026 ChemRxiv preprint demonstrates that deep learning scoring functions, despite high intra-target ranking, cannot identify the correct protein target for a given active molecule, indicating that generalization of protein-ligand interaction physics is still not achieved and models exhibit "memorizing effects" rather than learning transferable binding principles (ChemRxiv-2025-sf3cs, 2026).

### Evidence the Gap Exists

1. **The CASF-to-reality gap is now quantified.** The 2025 paper "Generalization Beyond Benchmarks" (arXiv:2512.05386) is the first systematic evaluation showing that CASF performance overestimates real-world utility by 0.3+ Pearson correlation points on average. This is devastating: a model that appears excellent (R=0.81) on CASF is mediocre (R=0.47) on novel targets.

2. **PDBbind-CASF similarity inflates results.** Several studies confirm high structural similarity between PDBbind training data and CASF test complexes, meaning benchmark improvements partly reflect data memorization rather than genuine learning (Harren et al., 2024).

3. **The inter-protein scoring noise problem persists.** Classical scoring functions already showed this limitation (inability to rank across different targets), and deep learning has not solved it, despite claims of learning "universal" binding physics (ChemRxiv-2025-sf3cs, 2026).

4. **Docking scores remain weakly correlated with binding affinity.** Empirical docking scoring functions show R^2 ~0.3-0.5 vs experimental binding affinities, and as noted in JCIM (2022): "Generative models should at least be able to design molecules that dock well" -- yet even this low bar is challenging.

5. **Target-dependent weights are ignored.** Current scoring functions assign common weights to individual energy terms, but these weights should be target-dependent, and interactions are nonlinear, not additive (JCIM task-specific scoring, 2017).

## Why This Gap Matters

### Scientific Importance

The scoring function is the oracle that guides all generative molecular design. If the oracle is unreliable, no amount of architectural innovation in generators will produce real drug candidates. Every 3D generative model (DiffSBDD, TargetDiff, MolCRAFT, FLOWR) optimizes against a scoring function; if that function does not generalize, the generated molecules are optimizing noise. This is arguably the single most important unsolved problem in computational drug design.

### Practical Impact

Drug discovery programs routinely encounter novel targets (emerging infections, rare diseases, orphan receptors). A scoring function that only works for targets similar to its training data is of limited value. Solving generalization would enable reliable virtual screening and generative design for any structurally characterized target, potentially reducing the ~$2.6B average drug development cost.

### Publication Potential

A comprehensive study revealing when, why, and how ML scoring functions fail on novel targets -- with a principled solution that demonstrably improves generalization -- would be a landmark paper. The "Generalization Beyond Benchmarks" paper (arXiv:2512.05386) opened this direction but did not propose solutions. A follow-up that both diagnoses failure modes and proposes physics-informed architectures that generalize would be highly impactful.

**Target venues:** Nature Computational Science, Nature Methods, Nature Communications

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

1. **Systematic diagnosis:** Construct a held-out evaluation framework stratified by protein family, fold type, binding site physicochemistry, and ligand chemotype. Quantify exactly which features cause generalization failure (novel folds? unusual binding sites? different interaction patterns?).

2. **Physics-informed architecture:** Design scoring models that explicitly decompose binding into transferable physical components (electrostatics, desolvation, shape complementarity, entropy) rather than learning end-to-end from coordinates. Enforce physical constraints (e.g., electrostatic interactions must decay with distance) as inductive biases.

3. **Cross-target training:** Train with explicit target-stratified cross-validation, potentially using meta-learning or domain adaptation techniques so the model learns to transfer across protein families.

4. **FEP-augmented training data:** Use large-scale open-source FEP calculations (OpenFE, FEP-SPell-ABFE) to generate semi-synthetic binding data for underrepresented target families, expanding training distribution.

5. **Benchmark contribution:** Release a new evaluation benchmark with strict target novelty requirements, designed to replace CASF for measuring real generalization.

### Required Data

- PDBbind 2020 (~23,000 complexes with experimental affinities)
- BindingDB (~2.8M data points)
- ChEMBL bioactivity data (~20M measurements)
- PDB structures for diverse target families
- CASF-2016 (285 complexes) for backward compatibility
- Computed FEP data from OpenFE for augmentation

### Required Compute

- FEP calculations for data augmentation: ~500-1000 GPU-days (H200)
- Model training and hyperparameter search: ~100-200 GPU-days
- Inference and evaluation: minimal
- Total: feasible on HPC with H200/B200 GPUs

### Required Methods

- Graph neural networks (GNNs) with physics-informed inductive biases
- Meta-learning for cross-target transfer (MAML, Reptile variants)
- Free energy perturbation (OpenFE, open-source)
- Molecular dynamics for conformational sampling
- Rigorous statistical evaluation framework

## Feasibility Assessment

### Technical Feasibility (Rating: High)

All required data (PDBbind, ChEMBL, PDB) is publicly available. Open-source FEP tools (OpenFE, FEP-SPell-ABFE) exist for data augmentation. GNN architectures are well-established. The main challenge is designing the right inductive biases, which is an ML research problem, not an infrastructure problem.

### Timeline Feasibility (Rating: Medium)

A comprehensive benchmark + diagnostic analysis is achievable in 2-3 months. A novel physics-informed architecture requires another 2-3 months. Publishing-quality results with proper baselines: 4-6 months total. Tight but feasible for summer 2026.

### Wet Lab Independence (Rating: High)

Entirely computational. All evaluation uses existing experimental data from public databases. No new experimental measurements needed.

## Competitive Landscape

### Who Else Might Fill This Gap

- The Oxford OPIG group (PoseBusters, AEV-PLIG) is actively working on scoring function evaluation and improvement
- Microsoft Research (Graphormer team) has foundation model efforts that could pivot to scoring
- Schrodinger has commercial incentive but publishes less openly
- Academic groups: Olexandr Isayev (CMU), Pat Walters (Relay Therapeutics)

### Risk of Being Scooped

**Medium.** The "Generalization Beyond Benchmarks" paper (Dec 2025) opened the door. Several groups are likely to attempt solutions. However, a comprehensive benchmark + physics-informed solution + systematic diagnosis would be differentiated.

### Differentiation

Most groups focus on either benchmarking OR new architectures. A combined effort that (1) systematically diagnoses failure modes, (2) proposes a new benchmark, and (3) provides a physics-informed architectural solution would be uniquely comprehensive.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 8 | The generalization problem is newly quantified (late 2025); solutions are unexplored |
| Scientific impact | 9 | Scoring is the bottleneck for all computational drug design |
| Feasibility (computational only) | 8 | Public data, open tools, established ML methods |
| Timeline (summer 2026) | 6 | Ambitious scope; needs careful scoping to fit timeline |
| Publication potential (Nat Comp Sci) | 8 | High-impact problem; diagnostic + solution paper is compelling |
| **Overall** | **7.8** | **Top-tier gap with clear path to high-impact publication** |

---

# Gap 2: The Evaluation Crisis -- No End-to-End Benchmark Connects Molecular Generation to Drug Discovery Outcomes

---
gap_id: genchem-evaluation-crisis
---

## Reporting Agent

Dr. Generative Chemistry & Molecular Design Expert. I have evaluated dozens of generative models over the past decade and have seen the same pattern repeatedly: models that achieve high scores on computational benchmarks (GuacaMol, MOSES, Vina score optimization) produce molecules that practicing medicinal chemists immediately reject. The disconnect between computational metrics and drug discovery utility is the field's most consequential methodological failure.

## Gap Description

### What Is Missing

There is no standardized, validated benchmark that measures whether generative molecular design methods produce molecules that would actually advance a drug discovery program. Current benchmarks assess proxy metrics (Vina docking score, QED, SA score, novelty, diversity) that have weak or unvalidated correlation with actual drug developability. The field lacks: (1) a benchmark linking generated molecules to real experimental hit rates, (2) evaluation of the full design-make-test cycle computationally, and (3) metrics that capture what medicinal chemists actually value.

### Current State of the Art

**Existing benchmarks and their limitations:**

- **GuacaMol (2019):** 20 optimization tasks using molecular graph generators. Limitation: scoring functions are simplistic proxies (e.g., optimize similarity to a known drug); top-scoring molecules are often synthetically implausible with unusual substructures (Brown et al., JCIM 2019).

- **MOSES (2020):** Evaluates distribution learning (FCD, SNN, novelty, diversity). Limitation: does not measure drug design utility; a model can score perfectly on MOSES while producing pharmacologically useless molecules (Polykovskiy et al., Front Pharmacol, 2020).

- **Practical Molecular Optimization (PMO, 2022):** Standardized multi-objective optimization. Limitation: still uses computational proxies; high-scoring molecules often have unfavorable MW, cLogP, or contain idiosyncratic substructures.

- **SDDBench (2024):** First benchmark incorporating retrosynthesis validation via round-trip score. Key contribution: three-stage evaluation using retrosynthetic planner + forward reaction model + reconstruction. Key finding: trade-off between pharmacological properties and synthesizability is fundamental -- molecules with best predicted activity are often hardest to synthesize (Liu et al., arXiv:2411.08306, 2024).

- **MolGenBench (2025):** 120 protein targets, 5,433 chemical series, 220,005 experimentally confirmed actives. Evaluates hit-to-lead scenarios. Limitation: still relies on computational scoring for affinity estimation; no direct experimental validation loop.

- **Durian (2025):** 17 metrics for 3D generators including affinity data. Methods tested: LiGAN, Pocket2Mol, DiffSBDD, SBDD, GraphBP, SurfGen. Key finding: all models show "varying degrees of limitations in balancing novelty, structural rationality, and synthetic accessibility" (Nie et al., JCIM 2025).

- **"Are We There Yet?" (2025):** Comprehensive evaluation of 3D SBDD methods revealing that there is "no effective metric to evaluate the chemical plausibility of molecules" and introducing two new chemical plausibility metrics (bioRxiv:2024.12.27.629537).

**The 3D vs 2D embarrassment:**
A devastating 2024 benchmark showed that 1D/2D ligand-centric methods (especially AutoGrow4, a genetic algorithm) achieve competitive or superior performance to 3D-aware deep learning methods in SBDD. AutoGrow4 dominates in optimization ability, challenging the assumption that explicit 3D structure utilization improves drug design (arXiv:2406.03403, "Structure-based Drug Design Benchmark: Do 3D Methods Really Dominate?", 2024).

**PoseBusters validity rates for 3D generators (2025 benchmark):**
- AutoGrow4: 92.7% pass rate
- LigBuilderV3: 84.2%
- DiffSBDD: 54.8%
- Pocket2Mol: 48.2%
- MolSnapper: 24.7%
- PocketFlow: 12.6%
- Deep learning methods generate ~30% 3-membered rings, unusual allene bonds, and physically implausible conformations (Benchmarking 3D Structure-Based Molecule Generators, JCIM 2025)

**MOSES filter pass rates (chemical validity):**
- Pocket2Mol: 81.2%
- PocketFlow: 72.1%
- DiffSBDD: 53.4%
- MolSnapper: 49.0%
- LigBuilderV3: 47.2%
- AutoGrow4: 35.6%

Critical finding: "every generator fails most of the tests" for recreating key active site interactions consistently (JCIM 2025 benchmark).

### Evidence the Gap Exists

1. **No benchmark measures real hit rates.** Every existing benchmark uses computational surrogates. The field has no systematic comparison of "molecules generated by method X" against "molecules that actually showed activity in assays."

2. **Computational metrics are weakly correlated with drug outcomes.** Docking scores correlate poorly with binding affinity (R^2 ~0.3-0.5). QED was calibrated to marketed drugs but does not predict clinical success. SA score has limited correlation with actual synthesis difficulty.

3. **Medicinal chemists reject ML-generated molecules.** Anecdotal but consistent reports: molecules that score well computationally contain structural alerts, pharmacokinetically unfavorable features, or synthetically challenging motifs that experienced chemists immediately flag.

4. **Multiple competing benchmarks with different conclusions.** MOSES, GuacaMol, PMO, SDDBench, Durian, and MolGenBench all measure different things and often rank methods differently, creating confusion about what "good performance" actually means.

5. **The 3D vs 2D result is paradigm-shaking.** If simpler 2D methods match or beat 3D deep learning approaches, the field's evaluation methodology is fundamentally flawed, since it means we cannot distinguish genuine structural understanding from docking score exploitation.

## Why This Gap Matters

### Scientific Importance

Without a valid evaluation framework, the field cannot determine whether it is making progress. Each new generative method claims improvements on some subset of metrics while ignoring others. The result is a proliferation of methods without genuine scientific advancement. A proper evaluation framework would enable the field to identify which architectural innovations actually matter.

### Practical Impact

Drug companies need to know which generative tool to deploy. Currently, method selection is based on unreliable benchmarks. An end-to-end evaluation framework that measures drug discovery relevance would directly accelerate pharmaceutical R&D.

### Publication Potential

A comprehensive evaluation framework that reveals the true state of molecular generation -- including embarrassing failures of current methods -- combined with principled metrics that align with drug discovery outcomes, would be a field-defining contribution.

**Target venues:** Nature Computational Science, Nature Methods

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

1. **Retrospective validation:** Take known drug discovery campaigns with published SAR data (e.g., from ChEMBL medicinal chemistry series) and test whether generative methods can rediscover the progression from hit to lead to candidate. Measure against actual experimental activity data, not docking scores.

2. **Multi-dimensional evaluation:** Define a metric suite that captures: (a) synthetic feasibility (retrosynthesis validation, not just SA score), (b) pharmacokinetic plausibility (predicted ADMET within drug-like ranges), (c) selectivity potential (predicted off-target liabilities), (d) novelty relative to existing IP, (e) interaction quality with target (interaction fingerprints, not just Vina score), and (f) chemical plausibility.

3. **Standardized protocol:** Create a protocol that any group can run on any generator, with automated evaluation pipelines and clear success criteria tied to drug discovery milestones (hit identification, lead optimization, candidate nomination).

4. **Leaderboard with medicinal chemistry review:** Incorporate expert review of generated molecules alongside automated metrics, as a ground truth for calibrating computational surrogates.

### Required Data

- ChEMBL medicinal chemistry campaigns (10-20 diverse targets with full SAR series)
- Corresponding PDB structures for protein targets
- Published activity data, selectivity data, ADMET data for retrospective validation
- Experimentally confirmed active molecules for hit-rate calibration

### Required Compute

- Running all major generators on the benchmark set: ~50-100 GPU-days
- Retrosynthesis validation and ADMET predictions: ~20 GPU-days
- FEP-based activity validation for top candidates: ~200 GPU-days
- Total: ~300-400 GPU-days, well within HPC budget

### Required Methods

- Automated retrosynthesis planning (AiZynthFinder, open-source)
- Forward reaction prediction for round-trip validation
- ADMET prediction models (open-source: ADMETlab 3.0)
- Interaction fingerprint analysis (ProLIF, open-source)
- FEP for binding affinity validation (OpenFE)
- Statistical framework for multi-objective evaluation

## Feasibility Assessment

### Technical Feasibility (Rating: High)

All data is publicly available. All evaluation tools are open-source. The main challenge is designing the right metrics and protocol -- this is a research design problem, not a technical barrier.

### Timeline Feasibility (Rating: High)

Benchmark design: 1-2 months. Running evaluations: 1-2 months. Analysis and paper: 1-2 months. Total: 3-5 months, well within summer 2026.

### Wet Lab Independence (Rating: High)

Entirely uses existing published experimental data. No new experiments required. The benchmark evaluates computational tools against retrospective experimental data.

## Competitive Landscape

### Who Else Might Fill This Gap

- The SDDBench team (Shanghai) has made the most progress on synthesis validation
- MolGenBench team (2025) is pursuing application-oriented benchmarks
- Therapeutics Data Commons (TDC) at MIT could extend their benchmark suite
- Patrick Walters (Relay Therapeutics) has written extensively about evaluation problems

### Risk of Being Scooped

**Medium-Low.** Multiple groups are publishing individual benchmarks, but nobody has produced the comprehensive, unified evaluation framework the field needs. The space is fragmented, which creates an opportunity for a unifying contribution.

### Differentiation

Most benchmark papers evaluate one dimension (synthesis, binding, drug-likeness). A unified framework that evaluates the full pipeline -- from generation through synthesis validation, ADMET, selectivity, and retrospective activity -- would be uniquely comprehensive. The key differentiator is connecting computational metrics to real drug discovery outcomes using retrospective data.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 7 | Several groups working on partial solutions; unification is novel |
| Scientific impact | 9 | Evaluation methodology shapes entire field's direction |
| Feasibility (computational only) | 9 | Public data, open tools, straightforward design |
| Timeline (summer 2026) | 8 | Well-scoped; benchmark design is achievable |
| Publication potential (Nat Comp Sci) | 8 | High impact; benchmarks in Nat Comp Sci are precedented |
| **Overall** | **8.2** | **Exceptionally well-positioned for high-impact publication** |

---

# Gap 3: Synthesis-Aware Generation Remains Disconnected from Real Chemistry -- The Reaction Feasibility Problem

---
gap_id: genchem-synthesis-reality
---

## Reporting Agent

Dr. Generative Chemistry & Molecular Design Expert. Synthesizability is the perennial Achilles' heel of generative molecular design. I have seen the field progress from SA scores (which are crude heuristics) to retrosynthesis-based scoring (which hallucinates reactions) to reaction-constrained generation (which restricts chemical space). None of these approaches truly solves the problem: ensuring that generated molecules can actually be made in a real chemistry lab with reasonable effort and cost.

## Gap Description

### What Is Missing

Current molecular generators produce molecules without meaningful guarantees of synthetic feasibility. Post-hoc synthesizability assessment (SA score, retrosynthesis planning) is either too crude to be useful or too unreliable to be trusted. Reaction-constrained generators (SynFlowNet, RxnFlow) guarantee synthetic accessibility by construction but dramatically restrict chemical diversity. The field lacks: (1) validated reaction feasibility prediction (distinguishing reactions that work in practice from those that only work on paper), (2) cost-aware synthesis planning integrated into generation, and (3) methods that maintain high chemical diversity while ensuring synthesizability.

### Current State of the Art

**Post-hoc synthesizability scoring:**
- **SA Score:** Widely used but crude. Based on fragment frequencies from known molecules. Does not account for reaction complexity, protecting group chemistry, or real-world failure modes. Correlation with actual synthesis difficulty is weak, especially for novel scaffolds (Ertl & Schuffenhauer, J Cheminf 2009; critical assessment: Thakkar et al., J Cheminf 2023).

- **BR-SAScore (2024):** Enhanced version integrating building block availability and reaction knowledge from synthesis planning programs. Better differentiation of fragments inherent in building blocks vs those requiring synthesis. Improvement over SA score but still heuristic (J Cheminformatics, 2024).

- **Retrosynthesis-based scoring (AiZynthFinder):** Used to evaluate whether a synthesis route exists. Key limitation: "overly lenient, as it fails to ensure that the proposed routes are actually capable of synthesizing the target molecules... retrosynthesis models are prone to predicting unrealistic or hallucinated reactions" (Liu et al., arXiv:2411.08306, SDDBench 2024).

**Round-trip validation (SDDBench, 2024):**
Three-stage approach: retrosynthetic planner predicts routes -> forward reaction model validates each step -> reconstruction of target molecule. This is the most rigorous evaluation to date. Key finding: many "synthesizable" molecules fail round-trip validation, revealing that retrosynthesis planning alone is insufficient (Liu et al., arXiv:2411.08306, 2024).

**Reaction-constrained generators:**
- **SynFlowNet (ICLR 2025):** GFlowNet using chemical reactions and buyable reactants. SA scores and retrosynthesis success significantly improved (62% AiZynthFinder success for trajectory length 3). Diversity: pairwise Tanimoto distance 0.81. Key limitation: constrained to known reaction templates, limiting exploration of novel chemistry (Cretu et al., ICLR 2025).

- **RxnFlow (ICLR 2025):** Synthesis-oriented GFlowNet on a large action space. Scalable reaction-based generation (Seo et al., 2025).

- **Directly optimizing synthesizability (Chemical Science, 2025):** Models generating molecules while optimizing with retrosynthesis models in the loop. "Moving to other classes of molecules such as functional materials shows current heuristics' correlations diminish, creating an advantage to incorporating retrosynthesis models directly" (Pubs RSC, 2025).

**The diversity-synthesizability tradeoff:**
Reaction-constrained generators show a fundamental tension: restricting generation to known reactions and purchasable building blocks ensures synthesizability but limits chemical diversity to known reaction product space. SynFlowNet with trajectory length 3 achieves 62% AiZynthFinder success but at the cost of chemical novelty. Increasing trajectory length to 4 drops success to 40% while improving diversity.

### Evidence the Gap Exists

1. **Retrosynthesis models hallucinate reactions.** Current retrosynthesis tools predict reactions that cannot be executed in practice. The SDDBench round-trip score (2024) quantified this: many predicted routes fail when validated with forward reaction models, demonstrating that retrosynthesis "success" does not equal practical synthesizability.

2. **SA score correlates poorly with real synthesis difficulty.** A critical assessment (Thakkar et al., J Cheminformatics 2023) showed that SA score has limited discriminative power for distinguishing easy-to-synthesize from hard-to-synthesize molecules, especially for structurally novel compounds.

3. **Cost is ignored entirely.** No current approach considers synthesis cost (reagent availability, number of steps, yield per step, purification difficulty). A molecule with a 12-step synthesis route using rare reagents is scored the same as a one-step reaction from commercial building blocks.

4. **Reaction conditions and compatibility are ignored.** Retrosynthesis tools predict disconnections without considering protecting group strategies, functional group compatibility, or the practical challenges of sequential reaction steps.

5. **The diversity-synthesizability tradeoff is unsolved.** SynFlowNet and RxnFlow restrict chemical space to known reaction products. The field cannot generate novel scaffolds that are also provably synthesizable.

## Why This Gap Matters

### Scientific Importance

The purpose of molecular generation is ultimately to produce molecules that can be tested. If generated molecules cannot be synthesized, the entire computational exercise is academic. Closing the gap between generated molecules and synthesizable molecules would transform generative design from a theoretical exercise into a practical tool.

### Practical Impact

Medicinal chemistry teams report that >50% of computationally suggested molecules are rejected at the synthesis planning stage. Reducing this rejection rate would dramatically accelerate the design-make-test-analyze (DMTA) cycle.

### Publication Potential

A paper demonstrating validated reaction feasibility prediction integrated into molecular generation -- showing that generated molecules have demonstrably higher synthesis success rates (validated computationally via stringent round-trip analysis) while maintaining chemical diversity -- would address one of the field's most persistent complaints.

**Target venues:** Nature Computational Science, Chemical Science

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

1. **Reaction feasibility scoring:** Train models on actual reaction databases (USPTO, Reaxys open data) that distinguish successful reactions from failed ones. Move beyond binary "route exists" to probabilistic "route likely succeeds with estimated yield."

2. **Cost-aware synthesis planning:** Integrate building block pricing (eMolecules, MolPort catalogs are partially open), step count, and predicted yield into a unified synthesis cost metric.

3. **Diversity-preserving constrained generation:** Develop approaches that use reaction constraints as soft penalties rather than hard constraints, allowing exploration of novel scaffolds while biasing toward synthesizable regions.

4. **Rigorous validation:** Use the SDDBench round-trip protocol as a minimum standard, with additional forward reaction prediction models to validate each step of proposed routes.

### Required Data

- USPTO reaction database (~3.5M reactions)
- eMolecules building block catalog (commercial availability data, partially open)
- Enamine REAL building blocks (public catalog of purchasable reactants)
- PDB protein structures for target-aware generation
- ChEMBL activity data for multiparameter optimization

### Required Compute

- Reaction feasibility model training: ~50-100 GPU-days
- Generator training with synthesis constraints: ~100-200 GPU-days
- Retrosynthesis + forward validation: ~50 GPU-days
- Total: ~200-400 GPU-days

### Required Methods

- Reaction prediction models (Molecular Transformer, open-source)
- Retrosynthesis planning (AiZynthFinder, ASKCOS, open-source)
- GFlowNets or RL-based generators
- Bayesian optimization for multi-objective (activity + synthesizability)
- Statistical comparison frameworks

## Feasibility Assessment

### Technical Feasibility (Rating: Medium)

The core challenge is training a reliable reaction feasibility predictor, which requires negative data (failed reactions) that is poorly documented. USPTO provides successful reactions but few explicitly recorded failures. Creative approaches to negative data generation (perturbed reactions, known incompatibilities) would be needed.

### Timeline Feasibility (Rating: Medium)

Reaction feasibility model: 2-3 months. Integration with generator: 1-2 months. Evaluation: 1-2 months. Total: 4-6 months. Feasible but tight for summer 2026.

### Wet Lab Independence (Rating: Medium-High)

All validation is computational (round-trip scores, forward reaction prediction). However, ultimate validation of synthesizability requires wet lab. The paper would need to frame results as "computationally validated synthesis feasibility" with appropriate caveats. Retrospective validation against known successful syntheses from literature could partially substitute.

## Competitive Landscape

### Who Else Might Fill This Gap

- The SynFlowNet team (Mila, Montreal) is actively extending reaction-constrained generation
- AstraZeneca's Molecular AI team (AiZynthFinder) has infrastructure for synthesis planning
- Recursion/Exscientia have commercial synthesis planning tools
- The SDDBench team has the round-trip evaluation framework

### Risk of Being Scooped

**Medium-High.** This is an active area. SynFlowNet and RxnFlow are recent ICLR 2025 papers. Multiple groups are working on synthesis-aware generation. The specific angle of reaction feasibility validation (as opposed to just retrosynthesis success) is less crowded.

### Differentiation

Focus on the reaction feasibility problem specifically (not just "does a route exist?" but "will this route work?") differentiates from existing work. Combining feasibility prediction with cost-aware planning and diversity analysis would be unique.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 6 | Active area; specific angle (feasibility vs existence) is newer |
| Scientific impact | 8 | Synthesizability is universally acknowledged bottleneck |
| Feasibility (computational only) | 6 | Lack of negative reaction data is a challenge |
| Timeline (summer 2026) | 6 | Tight timeline for the full vision |
| Publication potential (Nat Comp Sci) | 7 | Strong practical relevance but incremental risk |
| **Overall** | **6.6** | **Important gap but execution risk is higher** |

---

# Gap 4: Selectivity-Aware Molecular Design is Essentially Absent -- Generating for One Target While Ignoring the Proteome

---
gap_id: genchem-selectivity-design
---

## Reporting Agent

Dr. Generative Chemistry & Molecular Design Expert. Throughout my career I have witnessed molecular design papers celebrate binding affinity improvements without once addressing selectivity. In drug discovery, a molecule that binds its target at 1 nM but also hits 50 off-targets at 100 nM is a liability, not a success. Yet virtually every generative model in the field optimizes for single-target binding, treating the rest of the proteome as invisible.

## Gap Description

### What Is Missing

Current generative molecular design methods optimize for binding to a single target protein. They do not model, predict, or optimize selectivity against off-targets. The field lacks: (1) generative models that explicitly design for selectivity profiles rather than single-target potency, (2) reliable proteome-wide off-target prediction methods that can be integrated into generation loops, and (3) benchmarks that evaluate selectivity as a primary design objective.

### Current State of the Art

**Single-target design dominance:**
Every major 3D generative model (DiffSBDD, TargetDiff, MolCRAFT, Pocket2Mol, FLOWR) generates molecules for a single binding pocket. None considers whether the generated molecule would also bind related pockets. The CrossDocked2020 training set, used by most 3D generators, contains pocket-ligand pairs without selectivity annotations.

**Multi-target design (emerging, but different from selectivity):**
- **LaMGen (Nature Communications, 2026):** LLM-based framework for multi-target drug design. Uses ESM-C protein embeddings and rotation-aware ligand tokens. Outperforms diffusion models on multi-target tasks. Dataset: MTD2025 with 600,000+ conformations and 700,000+ multi-target associations. Key limitation: optimizes for binding multiple desired targets simultaneously, but does NOT address selectivity (avoiding unwanted off-targets).

- **POLYGON (2024):** VAE with generative RL to design dual-target inhibitors. Demonstrates multi-target feasibility but does not address selectivity against anti-targets.

- **De novo generation of multi-target compounds (Nature Communications, 2024):** Automated generative deep learning for dual-target design. Same limitation: designs for on-targets without modeling off-targets.

**Polypharmacology prediction:**
- MTDNN models: ~85% accuracy (ROC-AUC ~0.8) on KINOMEscan kinase panels. These are classification models, not generators (LINCS KINOMEscan, 2024).
- Proteochemometric (PCM) modeling: combines ligand and protein descriptors for kinome-wide prediction. Useful for retrospective analysis but not integrated into generation loops.
- "Data incompleteness currently limits most approaches to comprehensively predict selectivity" (Expert Opinion on Drug Discovery, 2024).

**Free energy perturbation for selectivity:**
- FEP+ can predict selectivity between two specific targets (PDE selectivity case study, JCIM 2019). Computational cost: enormous.
- Recent kinome-wide FEP study (Nature Communications, 2025): demonstrated selectivity optimization for Wee1 kinase inhibitors. Important proof-of-concept but limited to one target/kinase family.
- OpenFE (open-source): RMSE 1.73-2.44 kcal/mol. Not yet accurate enough for routine selectivity prediction.

**The selectivity data problem:**
- ChEMBL contains bioactivity data across many targets, but selectivity ratios are rarely reported directly. Researchers must mine pairwise comparisons.
- Kinase selectivity panels (e.g., DiscoverX KINOMEscan) provide kinome-wide profiling for some compounds, but coverage is sparse.
- Most drug design datasets lack systematic off-target profiling.

### Evidence the Gap Exists

1. **No generative model optimizes for selectivity.** A literature survey of all major 3D generative models (2022-2026) reveals zero methods that include an off-target avoidance term in their training objective or generation process.

2. **Multi-target design does not equal selectivity design.** LaMGen, POLYGON, and similar methods design molecules to hit desired targets. They do not model or avoid anti-targets. Selectivity is a fundamentally different objective: it requires simultaneously optimizing for binding to target A while minimizing binding to targets B, C, D, ...

3. **Selectivity failures drive drug attrition.** Off-target toxicity is a leading cause of clinical failure. Computational drug design that ignores selectivity produces candidates that will fail later in development. According to published analyses, ~30% of drug candidate failures in clinical trials are attributed to safety/toxicity, much of which traces to off-target pharmacology.

4. **Even kinase selectivity prediction is limited.** Despite kinases being the best-studied target family for selectivity (due to KINOMEscan data), computational prediction models achieve only ~85% accuracy at the classification level, insufficient for guiding design.

5. **Integration gap between prediction and generation.** Even where selectivity prediction tools exist (PCM models, kinome-wide FEP), they are not integrated into generative workflows. Generation and selectivity assessment remain separate, sequential steps rather than a unified optimization.

## Why This Gap Matters

### Scientific Importance

Selectivity is a fundamental property of drug molecules, arguably as important as potency. A drug that binds everything is not a drug -- it is a toxin. Developing generative methods that can design for selectivity profiles rather than single-target potency would represent a fundamental advance in how the field thinks about molecular design.

### Practical Impact

Selectivity-aware generation would directly reduce late-stage drug attrition from off-target effects, potentially saving years and hundreds of millions of dollars per program.

### Publication Potential

A paper demonstrating the first generative model that designs molecules with specified selectivity profiles -- selectively binding target A while avoiding targets B and C -- supported by retrospective validation against known selectivity data, would be highly publishable.

**Target venues:** Nature Computational Science, Nature Chemical Biology

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

1. **Selectivity-aware objective function:** Define generation objectives that include both on-target potency (maximize) and off-target binding (minimize). Use multi-task scoring models that predict binding across target panels.

2. **Proteome-wide binding profile prediction:** Train models on ChEMBL bioactivity data to predict binding across target families. Focus initially on kinases (best data availability) as proof-of-concept.

3. **Selectivity-constrained generation:** Integrate selectivity prediction into RL-based or GFlowNet-based generators as a reward/penalty term. Generate molecules conditioned on desired selectivity profiles.

4. **Retrospective validation:** Validate generated molecules against known selective compounds from ChEMBL. Test whether the generator can reproduce known selectivity patterns.

### Required Data

- ChEMBL bioactivity data across protein families (especially kinases: ~200,000 kinase-ligand activity measurements)
- KINOMEscan selectivity data (available for ~70,000 compounds)
- PDB structures for target families (kinases: 6,000+ structures)
- Known selective drug molecules for retrospective validation

### Required Compute

- Multi-task binding model training: ~100-200 GPU-days
- Generator training with selectivity reward: ~200-300 GPU-days
- Evaluation and FEP validation: ~100 GPU-days
- Total: ~400-600 GPU-days

### Required Methods

- Multi-task graph neural networks for binding profile prediction
- PCM modeling for cross-target generalization
- RL or GFlowNet generators with selectivity reward
- Free energy perturbation (OpenFE) for selectivity validation
- Kinase-focused evaluation using KINOMEscan data

## Feasibility Assessment

### Technical Feasibility (Rating: Medium)

The main challenge is reliable off-target prediction. Current PCM models achieve ~85% ROC-AUC for kinase activity classification, but this may be insufficient for guiding generation (a 15% error rate in the reward signal is substantial). Starting with kinases (best data) mitigates this risk.

### Timeline Feasibility (Rating: Medium)

Multi-task binding model: 2 months. Selectivity-aware generator: 2-3 months. Evaluation: 1-2 months. Total: 5-7 months. Achievable but ambitious for summer 2026.

### Wet Lab Independence (Rating: High)

All validation uses existing ChEMBL/KINOMEscan data. FEP calculations provide additional computational validation. No wet lab needed.

## Competitive Landscape

### Who Else Might Fill This Gap

- LaMGen team (multi-target, Nature Comms 2026) could extend to selectivity
- Novartis (kinase selectivity with ML is an active program)
- Relay Therapeutics (motion-based drug design, includes selectivity considerations)
- Academic groups at MIT (Barzilay lab) working on multi-property optimization

### Risk of Being Scooped

**Medium.** Multi-target design is active (LaMGen, POLYGON), but explicit selectivity-aware generation (designing molecules that avoid specific off-targets) is a distinct problem that fewer groups are addressing. The conceptual distinction between "hitting two targets" and "hitting one target while avoiding another" is underappreciated.

### Differentiation

Focus on selectivity as a design objective (not just multi-target potency) is the key differentiator. Integration of proteome-wide binding prediction into the generation loop, with validation on kinase selectivity data, would be unique.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 8 | Multi-target exists but selectivity-aware generation does not |
| Scientific impact | 9 | Selectivity is fundamental to drug design; largely ignored by generative methods |
| Feasibility (computational only) | 6 | Off-target prediction reliability is a bottleneck |
| Timeline (summer 2026) | 5 | Ambitious scope; kinase-focused proof-of-concept is more realistic |
| Publication potential (Nat Comp Sci) | 8 | Would redefine how the field thinks about generative design objectives |
| **Overall** | **7.2** | **High-impact gap with significant execution challenges** |

---

# Gap 5: The Conformational Ensemble Blindspot -- Molecular Generators Ignore Target Flexibility and Dynamic Binding

---
gap_id: genchem-conformational-ensemble
---

## Reporting Agent

Dr. Generative Chemistry & Molecular Design Expert. My expertise spans the interface between molecular generation and protein dynamics. I have long observed that virtually all 3D molecular generators treat the protein target as a frozen, rigid body -- typically using a single crystal structure. This ignores the fundamental biophysical reality that proteins are dynamic, flexible molecules that sample conformational ensembles. Drug binding is inherently a dynamic process involving induced fit, conformational selection, and allosteric communication. Generating molecules for a static snapshot of a protein is generating molecules for a fiction.

## Gap Description

### What Is Missing

All current 3D structure-based molecular generators condition on a single, static protein structure. They do not account for protein conformational flexibility, induced-fit effects, cryptic binding sites that appear only in certain conformations, or the dynamic nature of binding. The field lacks: (1) generators that condition on conformational ensembles rather than single structures, (2) methods that design molecules for dynamic rather than static binding, and (3) evaluation of generated molecules against conformational ensembles to assess robustness.

### Current State of the Art

**Static protein assumption in current generators:**
- DiffSBDD, TargetDiff, MolCRAFT, Pocket2Mol, FLOWR: all condition on a single pocket structure from the PDB
- CrossDocked2020 dataset: contains cross-docked poses but each complex uses a single protein conformation
- No major 3D generator trains on or generates molecules for multiple protein conformations

**Protein conformational ensembles (recent advances):**
- **PLACER (PNAS, 2025):** Models protein-small molecule conformational ensembles. From Baker lab. Represents a major advance in modeling the coupled dynamics of protein-ligand systems but is focused on prediction, not molecular design.

- **OpenComplex2 (bioRxiv, 2025):** A generative model integrating diverse molecular inputs with diffusion-based sampling through a FloydNetwork architecture. Enables conformational landscape sampling in hours rather than weeks. Examines induced-fit transitions and allosteric mechanisms. Still focused on prediction/sampling, not molecule design.

- **Deep learning-guided design of dynamic proteins (Science, 2025):** Designs proteins with intended dynamic behaviors. Demonstrates that generative models can incorporate dynamics. However, this designs proteins, not small molecules.

- **AlphaFold-based ensemble generation:** AlphaFold's MSA subsampling produces limited conformational diversity. Dedicated ensemble methods (Distributional Graphormer, EigenFold, str2str) are emerging but not integrated with molecular design.

**The induced-fit problem:**
Many drug targets undergo significant conformational changes upon ligand binding. Classic examples:
- Kinases: DFG-in/out conformational switch
- GPCRs: active/inactive states with distinct binding pockets
- Allosteric sites: only visible in certain conformations (cryptic sites)
A molecule designed for the DFG-in conformation may not bind or may bind differently to the DFG-out conformation. Ignoring this leads to molecules that bind only one state.

**Ensemble docking (existing but not integrated with generation):**
- Ensemble docking uses multiple protein conformations for virtual screening. Improves hit rates but is computationally expensive and not integrated with generative workflows.
- MD-based ensemble generation followed by docking: linear workflow, not iterative.

### Evidence the Gap Exists

1. **No generator conditions on ensembles.** A survey of all major 3D generative models (2022-2026) confirms that every method uses a single protein structure as input. None accepts multiple conformations or an ensemble distribution.

2. **Crystal structures are static snapshots.** PDB structures represent one conformation, often influenced by crystal packing forces, crystallization conditions, and the presence of specific ligands. Designing molecules for this single conformation may miss the true dynamic binding pocket.

3. **Induced fit is well-documented but ignored.** Kinase conformational flexibility (DFG-in/out, C-helix in/out) is textbook knowledge, yet 3D generators trained on CrossDocked2020 do not model these states.

4. **Cryptic binding sites are invisible to current methods.** Some of the most promising drug targets (e.g., KRAS) have cryptic allosteric sites that are only revealed by MD simulations or specific ligand binding. Generators that see only the apo crystal structure cannot design for these sites.

5. **The PLACER/OpenComplex2 gap.** These methods demonstrate that conformational ensemble modeling is computationally feasible. The gap is specifically in using ensemble information for molecular design, not just prediction.

## Why This Gap Matters

### Scientific Importance

Accounting for protein dynamics in molecular design would represent a fundamental advance in how the field approaches structure-based drug design. It would bridge the gap between the static structural biology paradigm (one structure = one drug target) and the biophysical reality of dynamic binding.

### Practical Impact

Molecules designed against conformational ensembles would be more robust across biological conditions and more likely to show activity in cellular and in vivo contexts, where proteins sample multiple conformations.

### Publication Potential

A paper demonstrating ensemble-aware molecular generation -- generating molecules that bind robustly across protein conformational states -- with validation against known conformation-dependent binders (e.g., kinase DFG-in vs DFG-out binders), would be a significant advance.

**Target venues:** Nature Computational Science, Nature Methods, PNAS

## What Filling the Gap Would Look Like

### Proposed Approach (High-Level)

1. **Ensemble-conditioned generation:** Modify 3D generative architectures (diffusion, flow matching) to accept multiple protein conformations as input. Represent the binding pocket as a distribution over conformations rather than a single structure.

2. **Conformation-robust scoring:** Score generated molecules against the full conformational ensemble. Favor molecules that bind well across multiple conformations (robust binders) over those that bind well to only one state.

3. **Dynamic pocket representation:** Use graph-based representations that capture pocket flexibility, encoding both mean positions and positional variance of key residues.

4. **Validation on kinase conformational switches:** Use kinases as a model system (DFG-in/out states are well-characterized, extensive SAR data exists). Test whether ensemble-aware generation produces molecules that bind both conformational states.

### Required Data

- PDB structures covering multiple conformations of the same protein (kinases: thousands of structures spanning DFG-in/out states)
- MD simulation trajectories for ensemble generation (can be generated computationally)
- Activity data for conformation-selective vs pan-conformation binders from ChEMBL
- CrossDocked2020 for baseline comparison

### Required Compute

- MD simulations for ensemble generation: ~200-500 GPU-days (H200)
- Ensemble-conditioned generator training: ~200-300 GPU-days
- Evaluation and docking: ~50-100 GPU-days
- Total: ~450-900 GPU-days (significant but feasible with HPC)

### Required Methods

- Molecular dynamics (OpenMM, GROMACS, open-source)
- ML force fields (MACE, ANI) for accelerated sampling
- Modified diffusion/flow matching architectures for ensemble conditioning
- Graph neural networks for dynamic pocket representation
- Free energy perturbation across conformational states

## Feasibility Assessment

### Technical Feasibility (Rating: Medium)

The main challenges are: (1) efficiently representing conformational ensembles as conditioning information for generators, (2) generating sufficient ensemble data for training, and (3) evaluating "conformational robustness" of generated molecules. MD simulations for ensemble generation are computationally expensive but feasible with HPC.

### Timeline Feasibility (Rating: Low-Medium)

MD ensemble generation: 2-3 months. Architecture development: 2-3 months. Evaluation: 1-2 months. Total: 5-8 months. Ambitious for summer 2026; a focused proof-of-concept on kinases might fit.

### Wet Lab Independence (Rating: High)

All conformational data can be generated computationally (MD simulations, AlphaFold variants). Validation uses existing activity data from ChEMBL. No wet lab needed.

## Competitive Landscape

### Who Else Might Fill This Gap

- Baker lab (PLACER) is best positioned to extend ensemble modeling to design
- Microsoft Research (protein structure/dynamics teams)
- Isomorphic Labs (DeepMind spinoff, integrating dynamics into drug design)
- The Distributional Graphormer team could extend to drug design applications

### Risk of Being Scooped

**Medium-High.** PLACER (PNAS, 2025) and OpenComplex2 (2025) show the field is moving toward ensemble-aware methods. The leap from ensemble prediction to ensemble-conditioned generation is natural and multiple groups are likely pursuing it.

### Differentiation

Most groups are focused on ensemble prediction (sampling conformations). The specific focus on using ensembles to improve molecular generation -- with validation showing improved conformation robustness -- would be differentiated. The kinase conformational switch as a model system provides a clean, well-characterized test case.

## Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 8 | Ensemble-conditioned generation is unexplored despite clear need |
| Scientific impact | 8 | Bridges structural biology and molecular design paradigms |
| Feasibility (computational only) | 6 | MD ensembles are expensive; architecture design is complex |
| Timeline (summer 2026) | 4 | Full implementation is very ambitious; proof-of-concept possible |
| Publication potential (Nat Comp Sci) | 8 | Compelling story connecting dynamics to design |
| **Overall** | **6.8** | **Scientifically exciting but timeline risk is high** |

---

# Summary of Identified Gaps

| Gap ID | Title | Overall Score | Key Strength | Key Risk |
|--------|-------|--------------|-------------|----------|
| genchem-scoring-generalization | Scoring Function Generalization Crisis | 7.8 | Newly quantified problem with clear solution path | Timeline tight for full scope |
| genchem-evaluation-crisis | End-to-End Evaluation Framework | 8.2 | Highest feasibility; shapes field direction | Needs buy-in for adoption |
| genchem-synthesis-reality | Synthesis-Aware Generation & Reaction Feasibility | 6.6 | Universally acknowledged bottleneck | Negative reaction data scarcity |
| genchem-selectivity-design | Selectivity-Aware Molecular Design | 7.2 | Redefines design objectives | Off-target prediction reliability |
| genchem-conformational-ensemble | Conformational Ensemble-Aware Generation | 6.8 | Bridges dynamics and design | Very ambitious timeline |

**Top recommendation for Cohort1 priority:** Gap 2 (Evaluation Crisis) and Gap 1 (Scoring Generalization) are the most promising for a Nature Computational Science publication within the summer 2026 timeline. They are the most tractable, address the most fundamental methodological problems, and have the clearest paths to high-impact results.

**Cross-domain opportunities:**
- Gap 5 (Conformational Ensemble) intersects strongly with the Protein Dynamics Expert's domain
- Gap 4 (Selectivity) intersects with Translational CompBio and Systems Biology domains
- Gap 1 (Scoring) intersects with AI/ML Methods and Multi-Scale Simulation domains
- Gap 2 (Evaluation) is relevant to every specialist in the cohort

---

## References

1. Buttenschoen, M., Morris, G.M., & Deane, C.M. (2024). PoseBusters: AI-based docking methods fail to generate physically valid poses or generalise to novel sequences. Chemical Science, 15, 3433-3445.

2. Harren, T. et al. (2024). Modern machine-learning for binding affinity estimation of protein-ligand complexes: Progress, opportunities, and challenges. WIREs Computational Molecular Science, e1716.

3. Harris, C., Didi, K., Sherif, A.R., et al. (2025). Benchmarking 3D Structure-Based Molecule Generators. Journal of Chemical Information and Modeling, 2025.

4. Tripp, A., Pineda, C., & Hernandez-Lobato, J.M. (2024). Structure-based Drug Design Benchmark: Do 3D Methods Really Dominate? arXiv:2406.03403.

5. Nie, W., Zhao, L., et al. (2025). Durian: A Comprehensive Benchmark for Structure-Based 3D Molecular Generation. Journal of Chemical Information and Modeling.

6. Liu, M., et al. (2024). SDDBench: Evaluating Molecule Synthesizability via Retrosynthetic Planning and Reaction Prediction. arXiv:2411.08306.

7. Cretu, A., et al. (2025). SynFlowNet: Design of Diverse and Novel Molecules with Synthesis Constraints. ICLR 2025.

8. Seo, S., et al. (2025). RxnFlow: Generative Flows on Synthetic Pathway for Drug Design. ICLR 2025.

9. Guo, J., et al. (2025). Generalization Beyond Benchmarks: Evaluating Learnable Protein-Ligand Scoring Functions on Unseen Targets. arXiv:2512.05386.

10. Buttenschoen, M., et al. (2025). Narrowing the gap between machine learning scoring functions and free energy perturbation using augmented data. Communications Chemistry, Nature.

11. Brown, N., Fiscato, M., Segler, M.H.S., & Vaucher, A.C. (2019). GuacaMol: Benchmarking Models for de Novo Molecular Design. Journal of Chemical Information and Modeling, 59(3), 1096-1108.

12. Polykovskiy, D., et al. (2020). Molecular Sets (MOSES): A Benchmarking Platform for Molecular Generation Models. Frontiers in Pharmacology.

13. Loeffler, H.H., et al. (2025). Large-scale collaborative assessment of binding free energy calculations for drug discovery using OpenFE. ChemRxiv.

14. Qu, Y., et al. (2024). MolCRAFT: Structure-Based Drug Design in Continuous Parameter Space. arXiv:2404.12141.

15. Ertl, P. & Schuffenhauer, A. (2009). Estimation of synthetic accessibility score of drug-like molecules based on molecular complexity and fragment contributions. Journal of Cheminformatics, 1(1), 8.

16. Thakkar, A., et al. (2023). Critical assessment of synthetic accessibility scores in computer-assisted synthesis planning. Journal of Cheminformatics.

17. Anishchenko, I., et al. (2025). Modeling protein-small molecule conformational ensembles with PLACER. PNAS.

18. Chen, J., et al. (2026). LaMGen: LLM-based 3D molecular generation for multi-target drug design. Nature Communications.

19. Loeffler, H., et al. (2025). Harnessing free energy calculations for kinome-wide selectivity in drug discovery campaigns with a Wee1 case study. Nature Communications.

20. Munson, B.P., et al. (2024). De novo generation of multi-target compounds using deep generative chemistry. Nature Communications.

21. Blay, V., Tolani, B., Ho, S.P., & Bhatt, M.R. (2024). Polypharmacology prediction: the long road toward comprehensively anticipating small-molecule selectivity to de-risk drug discovery. Expert Opinion on Drug Discovery, 19(9).

22. Singh, A. (2025). A Comprehensive Benchmarking Platform for Deep Generative Models in Molecular Design. arXiv:2505.12848.

23. Yang, J., et al. (2025). 3D Structure-based Generative Small Molecule Drug Design: Are We There Yet? bioRxiv:2024.12.27.629537.

24. Gusev, F., et al. (2020). iScore: A ML-Based Scoring Function for De Novo Drug Discovery. Journal of Chemical Information and Modeling, 2025.

25. ChemRxiv (2026). A new benchmark for deep learning based affinity prediction: Solving the inter-protein scoring noise problem. ChemRxiv-2025-sf3cs.

26. Loeffler, H., et al. (2024). FEP-SPell-ABFE: An Open-Source Automated Alchemical Absolute Binding Free-Energy Calculation Workflow. JCIM.

27. Ma, H., et al. (2024). Estimating the synthetic accessibility of molecules with building block and reaction-aware SAScore. Journal of Cheminformatics.

28. Lee, J., et al. (2024). PIGNet2: a versatile deep learning-based protein-ligand interaction prediction model. Digital Discovery, RSC.

29. Liu, A., et al. (2025). A Multi-Objective Molecular Generation Method Based on Pareto Algorithm and Monte Carlo Tree Search. Advanced Science.

30. Guan, J. et al. (2024). 3D molecular generative framework for interaction-guided drug design. Nature Communications.
