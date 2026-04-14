---
agent: genchem
round: 2
date: 2026-04-14
type: deep-dive
---

# Deep Dive: End-to-End Molecular Design Evaluation

## Executive Summary

The evaluation crisis in molecular design is **real, deepening, and still unresolved** as of April 2026. Despite major community efforts -- MolGenBench (November 2025), the "Beyond Affinity" benchmark (January 2026), GenBench3D (2024), and continued expansion of Polaris and TDC-2 -- no existing benchmark connects the full pipeline from target selection through molecular generation, scoring, ADMET filtering, synthesizability, to retrospective validation against drug discovery outcomes. Each benchmark addresses a fragment of the pipeline; none addresses the whole. This gap represents a compelling opportunity for a Nature Computational Science-class contribution that would reshape how the field evaluates generative molecular design.

---

## 1. Gap Verification

### 1.1 Has the Gap Been Filled?

**No.** Despite substantial activity in 2024-2026, the end-to-end evaluation gap persists. Here is the landscape of recent efforts:

**MolGenBench (Preprint November 2025):** The closest attempt. Integrates 120 protein targets, 5,433 chemical series, 220,005 experimentally confirmed active molecules. Includes de novo generation and hit-to-lead (H2L) optimization scenarios. Introduces target-aware metrics. However, MolGenBench still does not include: (1) ADMET filtering, (2) synthesizability assessment, (3) docking/scoring validation, (4) free energy calculations, or (5) retrospective comparison to actual drug progression data. It is a **generation-focused** benchmark, not an end-to-end pipeline benchmark.

**"Beyond Affinity" Benchmark (January 2026, Zhang et al.):** Compares 15 models across 1D, 2D, and 3D paradigms. Uses PoseBusters and PoseCheck for pose quality. Reveals the "affinity-validity trade-off" -- 3D methods excel at binding affinity but fail on chemical validity. However, does not include ADMET, synthesizability, or retrospective outcome validation. Focused on the **generation-to-docking** segment only.

**GenBench3D (Baillif et al., 2024):** Evaluates 3D conformation quality of generated molecules using the Validity3D metric based on Cambridge Structural Database. Found 0-11% of generated molecules have valid conformations before relaxation. Does not extend to ADMET or outcomes.

**Polaris Hub (ongoing, ICML 2024 launch):** Industry-backed benchmarking platform (Recursion, AstraZeneca, Pfizer, Merck, Novartis, etc.). Certified datasets with domain-expert curation. However, Polaris focuses primarily on **property prediction** (ADMET), not generation-to-outcome pipelines. The Antiviral ADME Prediction Challenge (2025) attracted 39 participants, but is single-endpoint focused.

**TDC-2 (Huang et al., 2024):** Massive expansion to ~85 million cells, 10+ modalities, 7 novel ML tasks. Introduces contextual biological information. But TDC-2's molecular design benchmarks still use oracle-limited optimization (e.g., PMO framework), not end-to-end validation.

**MolScore (Thomas et al., 2024):** Unified scoring and evaluation framework. Re-implements GuacaMol, MOSES, MolOpt. Flexible, modular. But is a **scoring/evaluation toolkit**, not a benchmark with ground-truth outcomes.

**Practically Significant Method Comparison Protocols (Ash, Wognum et al., JCIM 2025):** Industry consortium paper from J&J, AstraZeneca, Blueprint Medicines, Nimbus, etc. Proposes guidelines for statistically rigorous method comparison. Establishes domain-appropriate metrics and comparison protocols. Critically important for methodology but does **not** define an end-to-end benchmark.

### 1.2 What Specifically Remains Missing?

The gap has four dimensions:

1. **Pipeline integration:** No benchmark evaluates the sequential decision chain: target -> generation -> docking/scoring -> ADMET -> synthesizability -> comparison-to-known-actives
2. **Retrospective outcome grounding:** No benchmark connects to actual drug progression data (hit -> lead -> preclinical candidate)
3. **Cross-method fairness:** Comparing 1D SMILES generators, 2D graph generators, and 3D structure-based diffusion models requires method-agnostic endpoints
4. **Multi-objective trade-off characterization:** The "affinity-validity trade-off" (Zhang et al., 2026) is just one of many trade-offs (potency vs. selectivity vs. ADMET vs. synthesizability) that remain unquantified

### 1.3 Verification Confidence

**HIGH.** Three independent research efforts in the past 6 months (MolGenBench, Beyond Affinity, MolScore) have each explicitly identified the same gap from different angles. The gap is well-recognized but unsolved.

---

## 2. Existing Benchmark Audit

### 2.1 GuacaMol (Brown et al., JCIM 2019)

- **Coverage:** Distribution learning (validity, uniqueness, novelty, KL divergence, FCD) + 20 goal-directed optimization tasks
- **Limitations:** (1) 2D only -- no 3D structural evaluation; (2) Goals are simplistic (rediscovery of known drugs, QED, isomer scoring); (3) No target awareness; (4) Easily gamed -- genetic algorithms trivially optimize all goals; (5) No ADMET, synthesizability, or biological relevance metrics
- **Known Biases:** Internal diversity metric fails to capture meaningful chemical space coverage; generators produce clusters of highly similar molecules that score well
- **Status:** Saturated. Most modern generators score near-perfect on GuacaMol benchmarks.

### 2.2 MOSES (Polykovskiy et al., Frontiers Pharmacol 2020)

- **Coverage:** Validity, uniqueness, novelty, internal diversity, FCD, fragment/scaffold similarity, SNN, Frechet ChemNet Distance
- **Limitations:** (1) Distribution learning only -- no goal-directed tasks; (2) 2D only; (3) Trained on ZINC Clean Leads (~1.9M molecules), limited chemical diversity; (4) Metrics are insufficient for assessing real drug-likeness
- **Known Biases:** High MOSES scores do not correlate with generation of synthetically accessible or biologically active molecules
- **Status:** Still widely used as a baseline, but recognized as insufficient for modern evaluation.

### 2.3 Practical Molecular Optimization (PMO, Gao et al., 2022)

- **Coverage:** 23 optimization tasks with oracle call budgets. Tasks include docking scores, QED, DRD2 activity prediction, GSK3B/JNK3 scoring
- **Limitations:** (1) Oracle-based -- treats scoring functions as black boxes, hiding their real-world weaknesses; (2) Emphasizes sample efficiency over output quality; (3) Limited biological grounding; (4) No ADMET filtering
- **Known Biases:** Performance heavily dependent on the oracle quality; docking score optimization does not equal binding affinity optimization
- **Status:** Most rigorous 2D benchmark for optimization efficiency, but not a drug discovery benchmark.

### 2.4 MoleculeNet (Wu et al., Chemical Science 2018)

- **Coverage:** 17 datasets across quantum mechanics, physical chemistry, biophysics, physiology
- **Limitations:** (1) Property prediction only -- no generation assessment; (2) Small datasets (hundreds to low thousands); (3) Out-of-distribution generalization unaddressed; (4) Random splits give inflated performance estimates
- **Known Biases:** Well-documented train/test leakage issues in several datasets. Scaffold splits dramatically reduce apparent performance.
- **Status:** Still referenced but largely superseded by TDC for property prediction benchmarking.

### 2.5 Therapeutics Data Commons (TDC, Huang et al., 2021) / TDC-2 (2024)

- **Coverage:** 50+ datasets across 22 ADMET endpoints, drug-target interaction, docking, and generation (via PMO). TDC-2 adds ~85M cells, 10+ modalities, 7 novel tasks
- **Limitations:** (1) Generation tasks use PMO framework (oracle-limited); (2) No 3D structural evaluation; (3) ADMET and generation benchmarks are **separate** -- no pipeline integration; (4) Leaderboard encourages over-fitting to specific metrics
- **Known Biases:** Scaffold splits are used but dataset-specific biases persist. ADMET prediction accuracy varies dramatically by endpoint (BAavg from 0.742 to 0.905 across endpoints).
- **Status:** Most comprehensive platform but modular, not integrated.

### 2.6 PoseBusters (Buttenschoen et al., Chemical Science 2024)

- **Coverage:** Chemical and physical validity checks for protein-ligand poses (bond lengths, angles, ring planarity, steric clashes, stereochemistry)
- **Limitations:** (1) Binary pass/fail -- no graded quality metric; (2) Focuses on single-pose quality, not ensemble evaluation; (3) Does not assess binding affinity accuracy
- **Known Data Points:** DL docking methods PB-validity: DiffDock 38.3%, Uni-Mol 30.3%. Classical docking: AutoDock Vina ~70-85% PB-valid. Structure-based DL generators: 12.6%-54.8% PB-valid vs. 92.7% for AutoGrow4.
- **Status:** Essential for 3D validation but narrow in scope.

### 2.7 Polaris (Valence Labs + Industry Consortium, 2024-)

- **Coverage:** Certified, expert-curated datasets for molecular property prediction. Standardized splits and metrics. Active community competitions.
- **Limitations:** (1) Property prediction focused -- not generation evaluation; (2) Limited to ADMET-type endpoints; (3) Competition format encourages method engineering over understanding
- **Status:** Growing platform with strong industry backing. 39 participants in 2025 Antiviral ADME Challenge.

### 2.8 Summary Table

| Benchmark | Year | Generation | 3D Quality | Docking | ADMET | Synth | Retrospective | Pipeline |
|-----------|------|-----------|-----------|---------|-------|-------|--------------|----------|
| GuacaMol | 2019 | Yes | No | No | No | No | No | No |
| MOSES | 2020 | Yes | No | No | No | No | No | No |
| PMO | 2022 | Yes | No | Partial | No | No | No | No |
| MoleculeNet | 2018 | No | No | No | Partial | No | No | No |
| TDC/TDC-2 | 2021/24 | Via PMO | No | Partial | Yes | No | No | No |
| PoseBusters | 2024 | No | Yes | No | No | No | No | No |
| GenBench3D | 2024 | No | Yes | Partial | No | No | No | No |
| MolGenBench | 2025 | Yes | No | No | No | No | Partial | No |
| Polaris | 2024- | No | No | No | Yes | No | No | No |
| Beyond Affinity | 2026 | Yes | Yes | Yes | No | No | No | No |
| **Proposed** | **2026** | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** |

---

## 3. End-to-End Benchmark Design

### 3.1 Design Principles

1. **Pipeline completeness:** Evaluate every stage from target to outcome
2. **Method agnosticism:** Support 1D (SMILES/SELFIES), 2D (graph), and 3D (structure-based) generators on equal footing
3. **Retrospective grounding:** Use known drug progression data as ultimate ground truth
4. **Multi-objective realism:** Capture the full trade-off landscape (affinity vs. ADMET vs. synthesizability vs. novelty)
5. **Computational feasibility:** Tiered evaluation -- fast filters before expensive calculations
6. **Reproducibility:** All data public, all code open-source, all results versioned

### 3.2 Proposed Pipeline Architecture

```
TIER 0: TARGET SELECTION
  |--- Curated set of protein targets with known drug progressions
  |--- Structural data (PDB crystal structures, AlphaFold predictions)
  |--- Known actives with progression data from ChEMBL
  |
TIER 1: GENERATION (method-agnostic wrapper)
  |--- Input: Target structure + binding site + (optional) seed fragments
  |--- Output: Ranked set of generated molecules (SMILES + 3D coordinates)
  |--- Metrics: Validity, uniqueness, novelty, diversity, generation speed
  |
TIER 2: 2D CHEMICAL QUALITY
  |--- Drug-likeness (QED, Lipinski, Veber rules)
  |--- Structural alerts (PAINS, Brenk filters)
  |--- MOSES-style distribution metrics
  |--- Scaffold diversity (Bemis-Murcko + extended)
  |
TIER 3: 3D STRUCTURAL QUALITY
  |--- PoseBusters validity checks
  |--- GenBench3D Validity3D metric
  |--- Conformation energy (xTB or DFT-level)
  |--- Strain energy analysis
  |
TIER 4: TARGET INTERACTION
  |--- Molecular docking (AutoDock Vina, Glide, GOLD)
  |--- Consensus docking scores
  |--- Interaction fingerprint analysis (key contacts recapitulated)
  |--- Redocking RMSD for generated poses
  |--- PoseCheck interaction quality
  |
TIER 5: ADMET PREDICTION
  |--- TDC ADMET panel (22 endpoints)
  |--- PharmaBench supplementary endpoints
  |--- Multi-property pass rate (binary: meets all criteria vs. not)
  |--- ADMET-AI ensemble predictions with uncertainty
  |
TIER 6: SYNTHESIZABILITY
  |--- SAScore + RAscore (fast filtering)
  |--- ASKCOS/AiZynthFinder retrosynthetic route finding
  |--- SPARROW-style synthetic cost estimation
  |--- Route length and success probability
  |
TIER 7: RETROSPECTIVE VALIDATION
  |--- Rediscovery rate: Can the generator recover known actives?
  |--- Progression prediction: Can it generate compounds similar to
  |    late-stage vs. early-stage molecules?
  |--- Selectivity: Does it generate compounds active against the
  |    target but not close anti-targets?
  |--- Novelty-in-context: Are generated molecules novel relative to
  |    the known chemical series for this target?
  |
TIER 8: COMPOSITE SCORING
  |--- Pareto frontier analysis across all dimensions
  |--- "Drug-likeness efficiency" composite metric
  |--- Pipeline attrition rate: What fraction survives all filters?
  |--- Cost-effectiveness: Quality per compute dollar
```

### 3.3 Target Selection Criteria

For retrospective validation to work, targets must have:
- Crystal structure(s) in PDB with resolution < 2.5 angstrom
- At least 100 bioactivity measurements in ChEMBL (IC50/Ki < 10 uM)
- At least 3 distinct chemical series
- Known SAR (structure-activity relationship) progression data
- Ideally: approved drug(s) or late-stage clinical candidates

Estimated target count meeting all criteria: **40-80 targets** from ChEMBL 36 (17,803 targets total, but the vast majority lack sufficient progression data).

### 3.4 Key Innovation: The Attrition Funnel Metric

The most novel contribution would be an **attrition funnel metric** that mirrors real drug discovery:

```
Generated molecules:     10,000 (per target, per method)
  --> Pass 2D filters:    X% (Tier 2 survival)
  --> Pass 3D quality:    Y% (Tier 3 survival)
  --> Dock well:          Z% (Tier 4 survival, top 10% docking score)
  --> Pass ADMET:         W% (Tier 5 survival, multi-property)
  --> Synthesizable:      V% (Tier 6 survival, route found)
  --> Retrospective hit:  U% (Tier 7 survival, similar to known actives)
```

This funnel directly mirrors pharma's hit-to-lead attrition and has never been reported for generative models.

---

## 4. Data Availability

### 4.1 ChEMBL 36 (Released July 2025)

- **Size:** 2.8 million distinct compounds, 17,803 targets, ~21 million bioactivity data points
- **Progression data:** Drug forms include 327 approved drugs (103 more withdrawn since v35), clinical candidate data linked via UniProt/Gene annotations
- **Temporal coverage:** Data from 1974-2024, enabling time-split analyses
- **Useful features:** New 3D cell culture category, updated NLP pipeline for black box warnings (2024-2025 FDA labels), natural product flags from COCONUT 07/2025
- **Key gap:** ChEMBL does not explicitly label compound progression stages (hit/lead/candidate). This must be inferred from assay dates and potency values.

### 4.2 BindingDB (Updated October 2025)

- **Size:** 3,156,460 binding measurements, 1,380,881 small molecules, 11,367 protein targets, 50,458 entries with DOIs
- **Strengths:** Rich in patent data (unique source), Ki/Kd/IC50/EC50 measurements
- **Limitations:** Less structured progression data than ChEMBL. Overlap with ChEMBL is partial.

### 4.3 Drug Target Commons (DTC 2.0)

- **Size:** 14,820,874 bioactivities, 1,746,997 compounds, 13,023 targets
- **Unique value:** Community-curated annotations, 60,000 fully annotated bioactivity values not in ChEMBL or BindingDB
- **Limitations:** Annotation quality varies; many entries awaiting expert review

### 4.4 PDB Structural Data

- **Current:** ~220,000 structures in PDB. AlphaFold Database provides predicted structures for ~200 million proteins.
- **For benchmark targets:** High-quality co-crystal structures (ligand-bound) exist for ~5,000-8,000 unique drug targets
- **Limitation:** Not all ChEMBL targets have experimental structures; AlphaFold predictions for binding sites have variable accuracy

### 4.5 ADMET Data

- **TDC ADMET Group:** 22 datasets covering absorption, distribution, metabolism, excretion, toxicity endpoints
- **PharmaBench:** 11 ADMET property datasets, 52,482 entries, LLM-enhanced annotations
- **ADMET-AI training data:** 41 datasets (10 regression, 31 classification) from TDC
- **Key limitation:** ADMET data is sparser per compound than binding data. Many compounds have data for only 1-2 endpoints.

### 4.6 Synthesizability Data

- **ASKCOS/AiZynthFinder:** Open-source retrosynthetic planners can generate routes for most drug-like molecules
- **USPTO reaction database:** ~3.5 million reactions for training retrosynthetic models
- **Enamine REAL Space:** ~37 billion make-on-demand compounds (as reference for synthesizable chemical space)
- **Key limitation:** Retrosynthetic routes are predictions, not ground truth. Actual synthesis success rates for predicted routes are unknown for most compounds.

### 4.7 Retrospective Drug Progression Data

**This is the most critical and challenging data requirement.** Sources include:

1. **ChEMBL temporal data:** Time-series analysis of bioactivity publications for individual targets can reconstruct approximate hit-to-lead progressions. Handa et al. (J Cheminform 2023) demonstrated this approach on 5 public and 6 proprietary datasets.
2. **DrugBank:** Clinical status labels (approved, investigational, experimental) with target links
3. **ClinicalTrials.gov:** Phase information for compounds linked to molecular identifiers
4. **Patent literature (SureChEMBL 2.0):** Major update in 2025 with enhanced patent-compound links

**Estimated usable targets with full progression data:** 30-50 targets where we can reconstruct hit -> lead -> preclinical candidate trajectories from public data alone. This is sufficient for a benchmark but represents a significant curation effort.

---

## 5. Compute Requirements

### 5.1 Per-Target Computation Budget

Assuming 10,000 molecules generated per method per target:

| Stage | Method | Time per molecule | Total (10K) | GPU? |
|-------|--------|-------------------|-------------|------|
| Generation (3D diffusion) | DiffSBDD/TargetDiff | ~1-2 sec | 3-6 hrs | Yes (1 GPU) |
| Generation (autoregressive) | Pocket2Mol | ~1 sec | ~3 hrs | Yes (1 GPU) |
| Generation (SMILES) | REINVENT | ~0.01 sec | ~2 min | Yes (1 GPU) |
| 2D Filters | RDKit/MOSES | ~0.001 sec | ~10 sec | No |
| 3D Quality | PoseBusters | ~0.1 sec | ~17 min | No |
| Docking (Vina GPU) | AutoDock Vina GPU 2.1 | ~0.5-5 sec | 1.5-14 hrs | Yes (1 GPU) |
| Consensus docking (3 programs) | Vina + Glide + GOLD | ~15 sec total | ~42 hrs | Mixed |
| ADMET prediction | ADMET-AI (41 endpoints) | ~0.05 sec | ~8 min | Yes (1 GPU) |
| Synthesizability | AiZynthFinder | ~5-30 sec | 14-83 hrs | No (CPU) |
| FEP (top 100 compounds) | OpenFE/GROMACS | ~48 hrs/compound | ~4,800 hrs | Yes (1 GPU each) |

### 5.2 Full Benchmark Estimate

**Scope:** 10 generators x 50 targets x 10,000 molecules = 5 million total molecules

| Stage | Estimate | Notes |
|-------|----------|-------|
| Generation | ~2,500 GPU-hours | Varies by method (10 methods x 50 targets) |
| 2D Filters | ~1 CPU-hour | Negligible |
| 3D Quality | ~140 CPU-hours | PoseBusters on 5M molecules |
| Docking (Vina GPU) | ~7,500 GPU-hours | Single program, all molecules |
| Consensus Docking | ~21,000 GPU/CPU-hours | 3 programs |
| ADMET | ~70 GPU-hours | Fast inference |
| Synthesizability | ~70,000 CPU-hours | Major bottleneck |
| FEP (top candidates) | ~50,000 GPU-hours | 100 compounds x 50 targets x 10 methods, heavily filtered |

**Total estimated compute:**
- GPU: ~80,000-85,000 GPU-hours (primarily FEP + docking)
- CPU: ~70,000 CPU-hours (primarily retrosynthesis)

**On HPC cluster with H200/B200 GPUs:** With 50 GPUs, the GPU-intensive stages complete in ~1,700 hours (~70 days). With hundreds of CPU nodes for retrosynthesis, CPU stages take ~1 week.

**Tiered execution strategy:** Run Tiers 0-3 first (cheap, ~5,000 GPU-hours), then Tier 4-6 on surviving molecules (dramatically reduces FEP cost by pre-filtering), then Tier 7 on the final set. This reduces effective cost by 5-10x.

### 5.3 Cost Comparison to Prior Benchmarks

- GuacaMol/MOSES: ~10 GPU-hours total
- PMO: ~100-500 GPU-hours (depending on oracle)
- PoseBusters: ~50 CPU-hours
- MolGenBench: ~500-1,000 GPU-hours (estimated)
- **Proposed benchmark: ~20,000-85,000 GPU-hours** (tiered: 20K minimal, 85K comprehensive)

This is substantially more expensive but feasible on a well-resourced HPC cluster. The expense is itself a contribution -- demonstrating what proper evaluation costs reveals about method quality.

---

## 6. Competition Assessment

### 6.1 Active Groups and Initiatives

| Group/Platform | Affiliation | Focus | Threat Level |
|---------------|-------------|-------|-------------|
| Polaris Hub | Valence Labs + 10 pharma companies | Property prediction benchmarking | Medium -- complementary, not competing |
| TDC (Harvard/Zitnik Lab) | Harvard | Multi-modal benchmarks | Medium -- broad scope, not end-to-end |
| MolGenBench | Academic (bioRxiv 2025) | Generation benchmarking | High -- closest competitor, but incomplete |
| Beyond Affinity | Stanford (Zhang et al.) | 1D/2D/3D comparison | Medium -- generation-to-docking only |
| SPARROW (MIT/Coley Lab) | MIT | Synthetic cost-aware design | Low -- framework, not benchmark |
| MolScore (Cambridge/Thomas) | Cambridge + industry | Scoring framework | Low -- toolkit, not benchmark |
| Ash, Wognum et al. | Industry consortium | Method comparison protocols | Low -- guidelines, not benchmark |
| GenBench3D (Baillif et al.) | GSK | 3D quality benchmarking | Low -- narrow scope |

### 6.2 Gap in Competition

No group is building the **full pipeline benchmark with retrospective validation.** The closest:

- **MolGenBench** has the best target coverage (120 targets, 220K actives) but stops at generation metrics. It does not include docking, ADMET, synthesizability, or temporal progression analysis.
- **Polaris** has the best industry backing but focuses on property prediction, not generation.
- **TDC-2** has the broadest scope but treats each task modularly.

### 6.3 Differentiation Strategy

Our proposed benchmark is unique in three ways:

1. **Pipeline integration:** First benchmark to evaluate all stages sequentially, capturing attrition at each step
2. **Retrospective grounding:** First benchmark to use temporal drug progression data as ground truth
3. **Method-agnostic evaluation:** First benchmark to fairly compare 1D, 2D, and 3D generators on identical downstream endpoints

### 6.4 Risk: Someone Publishes First

**Medium risk.** The MolGenBench group (published November 2025) could extend their benchmark. The Polaris consortium could announce a pipeline benchmark. However, the retrospective validation component requires substantial data curation that takes months, creating a timing buffer. The key is to move quickly on data curation while building the pipeline.

---

## 7. Feasibility Reassessment

### 7.1 Technical Feasibility: HIGH

- All components exist individually (generators, docking tools, ADMET models, retrosynthetic planners)
- The challenge is integration and curation, not novel algorithm development
- Open-source tools available for every pipeline stage: RDKit, PoseBusters, AutoDock Vina GPU, ADMET-AI, AiZynthFinder, OpenFE/GROMACS
- MolScore provides a flexible framework for scoring integration

### 7.2 Data Feasibility: HIGH (with effort)

- ChEMBL 36 provides sufficient bioactivity and target data
- PDB provides structural data for targets
- The bottleneck is curating temporal progression data -- achievable but requires ~2-4 weeks of dedicated effort
- Estimated 30-50 targets with full public progression data

### 7.3 Compute Feasibility: HIGH

- Tiered approach reduces compute from 85K to ~20K GPU-hours for initial publication
- HPC cluster with H200/B200 GPUs can handle this in weeks
- FEP stage (most expensive) can be optional/"premium tier" or run on top-N candidates only
- Retrosynthesis on CPU nodes is embarrassingly parallel

### 7.4 Timeline: Summer 2026 (FEASIBLE)

| Phase | Duration | Activities |
|-------|----------|------------|
| Month 1 | 4 weeks | Target curation, progression data extraction, pipeline architecture |
| Month 2 | 4 weeks | Pipeline implementation, generator integration, initial runs |
| Month 3 | 4 weeks | Full benchmark execution (tiered), analysis, FEP on selected compounds |
| Month 4 | 2-3 weeks | Paper writing, supplementary materials, code release |

**Total: ~14-15 weeks.** Tight but feasible for a focused team.

### 7.5 Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Progression data insufficient | Medium | High | Fall back to rediscovery-only retrospective validation |
| Compute exceeds estimate | Low | Medium | Tiered execution, reduce target count |
| Generator integration difficulties | Medium | Low | Use published checkpoints, standardize I/O |
| Someone publishes similar first | Medium | High | Move fast, emphasize retrospective grounding as unique angle |
| Reviewers demand wet-lab validation | Medium | High | Retrospective design explicitly avoids wet-lab; frame as computational methodology contribution |

---

## 8. Publication Framing

### 8.1 Title Options

1. **"The Molecular Design Attrition Funnel: An End-to-End Benchmark Reveals That Most Generated Molecules Fail Before They Begin"**
2. **"From Generation to Drug: A Comprehensive Benchmark Connecting Molecular Design to Drug Discovery Outcomes"**
3. **"Closing the Evaluation Gap in Computational Molecular Design: A Retrospectively-Grounded Pipeline Benchmark"**

### 8.2 Central Claim

Current molecular design evaluation is fragmented and misleading. Methods that appear to perform well on generation metrics (validity, novelty, docking scores) show dramatically different rankings when evaluated through an end-to-end pipeline that mirrors real drug discovery attrition. We present the first comprehensive benchmark that connects molecular generation to drug discovery outcomes using retrospective progression data from 50 protein targets, revealing that (a) pipeline attrition rates differ by 10-100x across methods, (b) 2D generators match or exceed 3D generators on downstream metrics despite worse binding scores, and (c) synthesizability is the most discriminating filter, eliminating >80% of molecules from most generators.

### 8.3 Expected Key Findings (Hypotheses)

Based on existing literature, we predict:

1. **Attrition is catastrophic for DL generators:** PoseBusters validity of 12-55% for DL 3D generators means >50% are eliminated at Tier 3 alone. After ADMET and synthesizability filters, <1% of generated molecules may survive for most methods.

2. **Rankings invert:** Methods ranked highly on docking scores (3D diffusion models) may rank poorly on pipeline-survival metrics. SMILES-based generators with post-hoc docking may show higher pipeline throughput.

3. **Synthesizability is the killer:** Based on critical assessment of synthetic accessibility scores (Skoraczynski et al., J Cheminform 2023), and the finding that retrosynthetic route-finding is "overly lenient" (many predicted routes would fail experimentally), realistic synthesizability filtering will eliminate the vast majority of DL-generated molecules.

4. **Retrospective validation exposes generators:** Handa et al. (2023) found that REINVENT recovered only 0.04% of late-stage compounds for proprietary targets. We expect similarly low recovery rates across all generators, with the pipeline benchmark quantifying exactly where each method fails.

5. **The "affinity-validity trade-off" extends to ADMET:** Methods that optimize for binding affinity likely generate molecules with poor ADMET profiles (common failure mode in real drug discovery).

### 8.4 Key Experiments

1. **The Funnel Experiment:** Run 10+ generators through all 8 tiers for 50 targets. Report survival rates at each tier. This is the paper's centerpiece figure.

2. **Method Ranking Inversion:** Show that method rankings on Tier 1 metrics (generation quality) differ dramatically from rankings on Tier 7/8 metrics (retrospective validation). Correlation analysis between tier-specific scores.

3. **Multi-Objective Pareto Analysis:** For each method, compute the Pareto frontier across affinity, ADMET, synthesizability, and novelty. Quantify the "price" of each property in terms of others.

4. **Temporal Validation:** Train generators on pre-2020 data only, evaluate whether they generate molecules resembling post-2020 actives. This tests true prospective generative capability using a time-split.

5. **Cost-Effectiveness Analysis:** GPU-hours per pipeline-surviving molecule for each method. This directly addresses the practical question: which method gives the most "usable" output per compute dollar?

### 8.5 Venue

**Primary target: Nature Computational Science.** The journal has published multiple molecular design papers (SPARROW, SynGFN, molecular design collections) and benchmarking papers (spatial transcriptomics alignment, quantum computing software). An end-to-end evaluation benchmark fits their scope perfectly.

**Backup venues:** Nature Methods (as a resource/benchmark paper), Nature Machine Intelligence (broader ML audience), or JCIM (faster review, still high-impact in the field).

### 8.6 Anticipated Reviewer Concerns

1. **"Why not include wet-lab validation?"** -- Response: The entire point is that computational evaluation can be rigorous without wet-lab access. Retrospective validation using known drug progression data provides ground truth. Wet-lab validation is important but represents a different, subsequent study.

2. **"The benchmark is too expensive to reproduce"** -- Response: Tiered design allows partial reproduction. Tiers 0-3 require ~5,000 GPU-hours. We provide pre-computed results for all tiers. The expense itself is a finding (proper evaluation is costly).

3. **"Generator checkpoints may not be optimal"** -- Response: Use published, best-available checkpoints. The benchmark evaluates methods as they are provided to the community, not idealized versions.

4. **"ADMET predictions are not experimental ground truth"** -- Response: Correct, but (a) they are what the field uses for in silico evaluation, (b) retrospective data provides experimental ground truth for binding, and (c) we use ensemble predictions with uncertainty quantification.

5. **"50 targets is not enough"** -- Response: 50 targets with full progression data exceeds MolGenBench (120 targets but no progression data). Quality over quantity. The target selection criteria ensure meaningful retrospective analysis.

---

## 9. Cross-Domain Connections (Theme A: The Evaluation Crisis)

### 9.1 Parallels with Perturbation Prediction Evaluation

The evaluation crisis in molecular design directly mirrors findings in cellular perturbation prediction:

- **Wrong metrics inflate performance:** In perturbation prediction, Pearson correlation on gene expression profiles is misleading because systematic variation between perturbed and control cells creates a confounding baseline (Systema, Nature Biotech 2025). In molecular design, docking scores and generation metrics similarly inflate perceived method quality by ignoring downstream failures.

- **Simple baselines outperform complex models:** The Nature Methods 2025 paper (Peidli et al.) showed that simple linear baselines outperform scGPT, GEARS, and other foundation models on perturbation prediction. In molecular design, 2D SMILES generators match or exceed 3D deep learning generators on multiple metrics (Beyond Affinity, Zhang et al. 2026), and AutoGrow4 (a simple genetic algorithm) achieves 92.7% PoseBusters validity vs. 12.6-54.8% for DL generators.

- **Evaluation frameworks reshape the field:** Systema for perturbation prediction, PerturBench for cellular perturbation analysis, and our proposed pipeline benchmark for molecular design all address the same fundamental problem -- the field measures the wrong things.

### 9.2 Parallels with Foundation Model Evaluation

"The crisis of biomedical foundation models" (Journal of Biomedical Informatics, 2025) argues that the field produces new foundation models faster than it evaluates them. The same applies to molecular generators:

- Multiple new 3D generators appear monthly (DiffSBDD, TargetDiff, MolSnapper, FlexSBDD, PAFlow, MolFORM, BInD, FragFM, etc.)
- None are comprehensively evaluated end-to-end
- Each paper cherry-picks metrics favorable to its method
- Community cannot determine which methods actually advance the state of the art

### 9.3 Parallels with Dynamics Benchmarking

The molecular dynamics community faces analogous challenges:
- Force field benchmarking requires standardized test systems and evaluation protocols
- Recent work (2025) systematically benchmarks 11 force fields across 12 peptides with 19+ metrics
- The lesson: comprehensive, multi-metric benchmarking is essential for meaningful progress
- Our pipeline benchmark imports this philosophy to molecular generation

### 9.4 The Unifying Theme

Across all four domains (molecular design, perturbation prediction, foundation models, dynamics), the evaluation crisis has the same structure:

```
1. Metrics are disconnected from outcomes of interest
2. Simple baselines are underappreciated
3. Method proliferation outpaces method evaluation
4. The field optimizes for publication metrics, not scientific utility
```

A coordinated attack on the evaluation crisis -- with domain-specific benchmarks that share methodological principles -- would constitute a transformative contribution to computational biology. The molecular design benchmark we propose is one pillar of this larger effort.

### 9.5 Potential for Combined Impact

If the orchestrator selects the evaluation crisis as a unifying theme across domains, a suite of papers could be proposed:

1. **This paper:** End-to-end molecular design evaluation (genchem focus)
2. **Companion:** Perturbation prediction evaluation with outcome grounding (sysnet/reggeno focus)
3. **Companion:** Foundation model evaluation across biological domains (aiml focus)
4. **Perspective:** "The Evaluation Crisis in Computational Biology" -- cross-domain synthesis

This suite would maximize impact and cross-citation, potentially anchoring a special issue or collection.

---

## References

1. Brown, N., Fiscato, M., Segler, M. H., & Vaucher, A. C. (2019). GuacaMol: Benchmarking models for de novo molecular design. *Journal of Chemical Information and Modeling*, 59(3), 1096-1108.

2. Polykovskiy, D., Zhebrak, A., Sanchez-Lengeling, B., et al. (2020). Molecular Sets (MOSES): A benchmarking platform for molecular generation models. *Frontiers in Pharmacology*, 11, 565644.

3. Gao, W., Fu, T., Sun, J., & Coley, C. W. (2022). Sample efficiency matters: A benchmark for practical molecular optimization. *NeurIPS 2022*.

4. Wu, Z., Ramsundar, B., Feinberg, E. N., et al. (2018). MoleculeNet: A benchmark for molecular machine learning. *Chemical Science*, 9(2), 513-530.

5. Buttenschoen, M., Morris, G. M., & Sherborne, B. (2024). PoseBusters: AI-based docking methods fail to generate physically valid poses or generalise to novel sequences. *Chemical Science*, 15, 3413-3431.

6. Baillif, B., Cole, J., & Sherborne, B. (2024). Benchmarking structure-based three-dimensional molecular generative models using GenBench3D: Ligand conformation quality matters. arXiv:2407.04424.

7. Thomas, M., O'Boyle, N. M., Bender, A., & De Graaf, C. (2024). MolScore: A scoring, evaluation and benchmarking framework for generative models in de novo drug design. *Journal of Cheminformatics*, 16, 67.

8. Huang, K., Fu, T., Gao, W., et al. (2021). Therapeutics Data Commons: Machine learning datasets and tasks for drug discovery and development. *NeurIPS 2021 Datasets and Benchmarks Track*.

9. Huang, K., et al. (2024). TDC-2: Multimodal Foundation for Therapeutic Science. *bioRxiv*, 2024.06.12.598655.

10. Zhang, Z., et al. (2026). Beyond Affinity: A Benchmark of 1D, 2D, and 3D Methods Reveals Critical Trade-offs in Structure-Based Drug Design. arXiv:2601.14283.

11. MolGenBench Authors (2025). Benchmarking Real-World Applicability of Molecular Generative Models from De novo Design to Lead Optimization with MolGenBench. *bioRxiv*, 2025.11.03.686215.

12. Handa, K., Thomas, M. C., Kageyama, M., Iijima, T., & Bender, A. (2023). On the difficulty of validating molecular generative models realistically: A case study on public and proprietary data. *Journal of Cheminformatics*, 15, 102.

13. Peidli, S., et al. (2025). Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines. *Nature Methods*, 22(8), 1657-1661.

14. Fromer, J. C., & Coley, C. W. (2024). An algorithmic framework for synthetic cost-aware decision making in molecular design. *Nature Computational Science*, 4, 440-450.

15. Ash, J. R., Wognum, C., Rodriguez-Perez, R., et al. (2025). Practically Significant Method Comparison Protocols for Machine Learning in Small Molecule Drug Discovery. *Journal of Chemical Information and Modeling*, 65(18), 9398-9411.

16. Norden, M. V., et al. (2025). Strategies for robust, accurate, and generalizable benchmarking of drug discovery platforms. *Bioinformatics*, 41(11), btaf604.

17. Mendez, D., et al. (2023). The ChEMBL Database in 2023: A drug discovery platform spanning multiple bioactivity data types and time periods. *Nucleic Acids Research*, 52(D1), D1180-D1192.

18. Gilson, M. K., et al. (2024). BindingDB in 2024: A FAIR knowledgebase of protein-small molecule binding data. *Nucleic Acids Research*, 53(D1), D1633-D1641.

19. Tang, J., et al. (2018). Drug Target Commons 2.0: A community platform for systematic analysis of drug-target interaction profiles. *Database*, 2018, bay083.

20. Skoraczynski, G., et al. (2023). Critical assessment of synthetic accessibility scores in computer-assisted synthesis planning. *Journal of Cheminformatics*, 15, 6.

21. Benchmarking 3D Structure-Based Molecule Generators (2025). *Journal of Chemical Information and Modeling*. DOI: 10.1021/acs.jcim.5c01020.

22. PharmaBench: Enhancing ADMET benchmarks with large language models (2024). *Scientific Data*. DOI: 10.1038/s41597-024-03793-0.

23. Drug and Clinical Candidate Drug Data in ChEMBL (2025). *Journal of Medicinal Chemistry*. DOI: 10.1021/acs.jmedchem.5c00920.

24. Acceleration of the GROMACS Free-Energy Perturbation Calculations on GPUs (2025). *ACS Omega*. DOI: 10.1021/acsomega.5c00151.

25. Large-scale collaborative assessment of binding free energy calculations for drug discovery using OpenFE (2025). *ChemRxiv*. DOI: 10.26434/chemrxiv-2025-7sthd.

26. How successful are AI-discovered drugs in clinical trials? A first analysis and emerging lessons (2024). *Drug Discovery Today*, 29(6), 134002.

27. The crisis of biomedical foundation models (2025). *Journal of Biomedical Informatics*. DOI: 10.1016/j.jbi.2025.104867.

28. Generative molecular design and its value in modern drug discovery (2026). *Expert Opinion on Drug Discovery*, 21(3). DOI: 10.1080/17460441.2026.2636192.

29. Systema: A framework for evaluating genetic perturbation response prediction beyond systematic variation (2025). *Nature Biotechnology*. DOI: 10.1038/s41587-025-02777-8.

30. Benchmarking algorithms for generalizable single-cell perturbation response prediction (2025). *Nature Methods*. DOI: 10.1038/s41592-025-02980-0.
