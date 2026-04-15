---
agent: Strategic Scope & Competition Analyst (scopeadv)
round: 2
date: 2026-04-14
type: proposal
proposal_id: strategy-integration
---

# Proposal: Integrated Strategic Recommendation for the CompBioSummer2026 Research Portfolio

## Proposing Agent

Dr. Strategic Scope & Competition Analyst (scopeadv), Cohort2 Deep Divers. Former
academic researcher, scientific program director, and journal editor. This proposal
integrates findings from all 5 other Cohort2 specialists (mlffeng, bioval, ensfunc,
pertbio, evalstat) into a single strategic framework with dated decision points,
compute allocation, publication sequencing, and kill criteria. Every recommendation
is grounded in the April 14, 2026 competitive landscape and the specific compute,
timeline, and data parameters from the specialist proposals.

---

## Problem Statement

The CompBioSummer2026 team has three promising project tracks (Alpha-M, Gamma, Delta)
emerging from Cohort1 Gap Scouts and refined through Cohort2 Round 1 deep research.
Each project independently addresses a genuine gap. The strategic problem is how to
manage all three simultaneously -- allocating compute, personnel, and timeline across
projects with different urgency levels, competition windows, and publication targets --
while maximizing the probability of producing 2 high-impact publications (Nature
Computational Science + Nature Methods) from a single summer of work. The risk is
not that any single project fails, but that spreading resources too thin causes all
three to produce mediocre results, or that poor sequencing causes a time-sensitive
project (Delta) to be scooped while compute-heavy projects (Alpha-M) consume the
cluster.

---

## Vision

By January 2027, this team has posted 3 preprints on bioRxiv and submitted 2 papers:

1. **PerturbMark** (Nature Methods, submitted August 2026): The definitive cross-context
   benchmark for perturbation prediction, resolving the DL-vs-baselines controversy on
   Tahoe-100M with calibrated metrics and 4 difficulty tiers.

2. **From Accurate Ensembles to Biological Function** (Nature Computational Science,
   submitted December 2026): A combined Gamma+Alpha-M paper demonstrating that ML force
   fields produce physically realistic protein dynamics (validated against NMR) and that
   these validated ensembles predict protein function (DMS fitness) beyond sequence-only
   methods.

If Alpha-M compute proves prohibitive, Gamma publishes as a standalone Nature Comp Sci
submission by October 2026, and Alpha-M follows as a separate Nature Methods/JCTC
submission when simulations complete. The portfolio is designed so that the "worst case
still publishes" for every project.

---

## Background and Evidence

### Current State of the Art

This section updates the Round 1 competition scan (April 14, 2026) with findings from
fresh searches and newly discovered developments.

#### Alpha-M: MLFF Biomolecular Crash Test

**State: No direct competitor. Widest competitive moat of all three projects.**

The gap between MLFF computational validation and experimental validation remains
completely open. As of April 14, 2026:

- MACE-OFF24(M) (Kovacs et al., JACS 2025) validates on crambin power spectra and
  Ala3 J-couplings, but does not compute S2 order parameters or chemical shifts for
  folded proteins.
- SO3LR (Frank et al., JACS 2026) validates lipid tail order parameters and polyalanine
  helix stability, but no backbone NMR observables for folded proteins.
- AI2BMD (Li et al., Nature 2024) validates J-couplings on dipeptide fragments
  (r = 0.81), but not on folded proteins.
- Bojan et al. (arXiv 2505.23354, March 2026) use MLFF embeddings (MACE, Egret,
  AIMNet) to build a chemical shift predictor that outperforms UCBShift2-X. This is
  adjacent but different: they use MLFF representations, not MLFF trajectories. Their
  work validates that MLFF features capture NMR-relevant structural information -- good
  supporting evidence for our premise -- but does not test whether MLFF *dynamics*
  match experiment.
- Cavender et al. (LiveCoMS 2025) provide the definitive review of experimental datasets
  for force field benchmarking (NMR, room-temperature crystallography), but explicitly
  do not build the benchmark or test MLFFs.
- UniFFBench (Mannan et al., arXiv 2508.05762) demonstrated the "reality gap" for
  materials science MLFFs, proving the concept we will apply to biology.

**New threat assessment (April 2026):**

| Group | Capability | Current Focus | Threat Level | Change from R01 |
|-------|-----------|---------------|-------------|-----------------|
| MACE (Cambridge) | HIGH | Architecture development, AceFF-2.0 for drugs | LOW-MODERATE | UNCHANGED |
| Microsoft (AI2BMD) | HIGH | BioEmu applications, drug design | LOW | UNCHANGED |
| DeepMind (GEMS) | HIGH | AlphaFold3, protein design | LOW | UNCHANGED |
| SO3LR (Basel/Tuckerman) | HIGH | Method development, lipid bilayers | LOW-MODERATE | UNCHANGED |
| Bojan et al. (Bronstein group) | MODERATE | MLFF representations for NMR | LOW | NEW (complementary, not competing) |

**Competition window: 12-24+ months. Scoop probability <10% in 6 months.**

#### Gamma: Dynamics-to-Function

**State: Gap remains open. Adjacent activity is intensifying but no one is doing this
exact study.**

The most important intelligence update: Microsoft Research's April 2026 blog post
"Exploring the structural changes driving protein function with BioEmu-1" continues
to focus on drug design and protein stability -- with NO mention of ProteinGym, DMS
fitness prediction, or systematic ensemble-to-function mapping at scale. They remain
the team best positioned to scoop us, but they are not pursuing this direction.

Key developments since Round 1:

- SeqDance/ESMDance (Hou et al., PNAS Jan 2026): PLMs trained on MD-derived dynamics.
  ESMDance achieves Spearman ~0.46 on ProteinGym. Uses *implicit* dynamics (learned
  representations), not *explicit* ensemble features. This is complementary: if ESMDance
  shows dynamics matter, Gamma shows *which structural features* explain why.
- Mutational robustness-dynamics correlation (bioRxiv March 2026): Median within-protein
  Spearman rho ~0.6 between mutational sensitivity and RMSF across ~2,000 proteins.
  This is the strongest prior validation of our wildtype ensemble hypothesis.
- eRMSF package (JCIM 2026): Purpose-built for BioEmu ensemble RMSF analysis. Exact
  tooling we need.
- Boltz-2 MD ensembles (Wohlwend et al., 2025-2026): Alternative ensemble generator.
  Potential backup if BioEmu fails for some proteins.

**Competition window: 6-12 months. Scoop probability 15-25% in 6 months.**

#### Delta: PerturbMark

**State: Most crowded landscape. Urgency is CRITICAL.**

The competitive landscape has continued to intensify. Key updates:

- scPPDM (ICLR 2026 submission): A diffusion-based perturbation predictor evaluated on
  Tahoe-100M benchmark under UC (unseen covariate) and UD (unseen drug) splits. Reports
  +13-36% improvement over second-best model on DEG metrics. This is the first paper to
  systematically benchmark on Tahoe-100M with multiple split types. **Direct threat to
  PerturbMark's novelty as "first Tahoe-100M benchmark."**
- Virtual Cell Challenge wrap-up (Cell 2025): 5,000+ registrants. Key finding:
  "perturbation prediction models are not yet consistently outperforming naive baselines
  across all metrics." Winning approaches combined DL + classical features.
- Cole et al. (bioRxiv Feb 2026): 600+ models evaluated. Some foundation models
  significantly improve predictions with sufficient data.
- Tahoe-x1 (bioRxiv Oct 2025): Tahoe Bio's own 3B foundation model. Open-sourced.

**Critical reassessment:** scPPDM's Tahoe-100M benchmark changes the landscape. However,
scPPDM evaluates ONE new method against baselines; PerturbMark evaluates 10+ methods
(including scPPDM) against 4+ linear baselines with calibrated metrics and 4 difficulty
tiers. scPPDM does not include the Miller et al. metric calibration framework, does not
stratify by cross-context difficulty tiers (0-3), and does not include the March 2026
model explosion. PerturbMark remains differentiated, but urgency has increased.

**Competition window: 3-6 months (revised from 4-7). Scoop probability 25-35% in 3
months.**

### Recent Developments That Enable This

1. **Production-ready MLFFs (2024-2026):** MACE-OFF24(M), SO3LR, AI2BMD all demonstrate
   nanosecond-scale protein simulations. OpenMM-ML v1.5 provides unified interface.
2. **BioEmu v1.2 (Science 2025):** MIT licensed, pip-installable, generates equilibrium
   ensembles from sequence in minutes to hours.
3. **ProteinGym v1.3 (NeurIPS 2023):** 2.7M variants, 217 assays, 90+ benchmarked
   methods.
4. **Tahoe-100M (bioRxiv Feb 2025):** 100M cells, 50 cell lines, 379 compounds, CC0.
5. **H200 GPUs:** 141 GB HBM3e, 4.8 TB/s bandwidth. Enables MLFF simulations at
   ~0.4-3 ns/day per system.
6. **Miller et al. calibration framework (bioRxiv Oct 2025):** Solves the metric
   controversy for perturbation prediction.

### Key Prior Work

1. UniFFBench (Mannan et al., arXiv 2508.05762): Materials MLFF "reality gap."
2. Lindorff-Larsen et al. (JCTC 2012): Classical FF benchmark, 524 NMR measurements.
3. Smith et al. (J. Phys. Chem. B 2024): S2 convergence protocol.
4. Kovacs et al. (JACS 2025): MACE-OFF24(M) protein simulations.
5. Frank et al. (JACS 2026): SO3LR biomolecular simulations.
6. Li et al. (Nature 2024): AI2BMD protein dynamics.
7. Jing et al. (Science 2025): BioEmu conformational ensembles.
8. Notin et al. (NeurIPS 2023): ProteinGym benchmarks.
9. Wei et al. (NatMeth 2026): scPerturBench.
10. Miller et al. (bioRxiv Oct 2025): Well-calibrated perturbation metrics.

---

## Proposed Approach

### Overview

This strategic proposal defines the integrated execution plan for all three projects.
The core approach is **parallel execution with staggered deliverables**: Delta sprints
to a July preprint, Gamma delivers in September, and the combined Alpha-M+Gamma paper
lands in November-December. Compute is allocated with Delta-first priority (low cost,
high urgency), Gamma-second (moderate cost, moderate urgency), and Alpha-M receiving
the bulk of GPU time after Delta completes its method runs.

### Component 1: Final Competition Assessment (April 14, 2026)

#### 1.1 Competition Summary Table

| Dimension | Alpha-M | Gamma | Delta |
|-----------|---------|-------|-------|
| Direct competitors | 0 | 0 | 2-3 (scPerturBench, scPPDM) |
| Adjacent competitors | 3-4 | 2-3 | 8+ |
| Competition window | 12-24+ months | 6-12 months | 3-6 months |
| Scoop risk (6 mo) | <10% | 15-25% | 35-50% |
| Scoop risk (12 mo) | 15-25% | 35-50% | 60-75% |
| Key differentiator | Only neutral multi-MLFF vs experiment benchmark | First explicit ensemble-to-DMS at scale | Tahoe-100M + Tier 0-3 + calibrated metrics + 2026 methods |
| Biggest threat | MACE group pivots to benchmark | Microsoft publishes BioEmu-DMS | Consensus resolves controversy before we publish |

#### 1.2 New Competitive Intelligence (April 2026)

**Alpha-M new development:** Bojan et al. (arXiv March 2026) used MLFF intermediate
representations (MACE, Egret, AIMNet) to predict NMR chemical shifts, outperforming
UCBShift2-X. This validates that MLFF features encode NMR-relevant structural
information. It is *supportive* of our thesis, not competitive: they use MLFF
features for prediction, we test whether MLFF *dynamics trajectories* reproduce
experimental observables. We should cite this prominently.

**Gamma new development:** No new papers connecting BioEmu ensembles to DMS fitness
prediction at scale. The mutational robustness-dynamics correlation paper (bioRxiv
March 2026) and eRMSF package (JCIM 2026) both support our approach. Microsoft's blog
(April 2026) confirms they are not pursuing this direction.

**Delta new development:** scPPDM (ICLR 2026 submission) is the most significant new
threat. It benchmarks on Tahoe-100M with UC/UD splits and claims SOTA. However, it
(a) evaluates one method, not 10+; (b) does not use calibrated metrics; (c) does not
define difficulty tiers; (d) does not include March 2026 models. PerturbMark subsumes
scPPDM as one of the methods we evaluate.

### Component 2: Combined vs. Separate Paper Decision Framework

#### 2.1 The Combined Paper Case

**Narrative:** "From Accurate Ensembles to Biological Function: Validating and Applying
ML Protein Dynamics"

This paper tells a two-act story:
- **Act 1 (Alpha-M):** Do ML force fields produce physically realistic protein dynamics?
  Systematic benchmark of 3 MLFFs + 2 classical baselines against experimental NMR
  observables across 7 proteins.
- **Act 2 (Gamma):** Can validated conformational ensembles predict protein function?
  Systematic mapping of BioEmu ensembles to DMS fitness scores across 200 ProteinGym
  proteins.
- **Integration:** The 8 proteins shared between Alpha-M and Gamma (ubiquitin, GB1/GB3,
  T4 lysozyme, barnase, HIV protease, alpha-synuclein, p53, SNase) enable the key
  question: do MLFF ensembles that better match experimental dynamics also produce
  better functional predictions?

**Why combined is stronger:** Nature Comp Sci editors want paradigm-level claims. "This
MLFF is better" is moderate interest. "Ensemble quality determines functional prediction
accuracy" is a paradigm claim that changes how the field validates and applies dynamics.

#### 2.2 The Separate Papers Case

**Gamma standalone:** "Conformational Ensembles Predict Protein Function Beyond Sequence"
- Strong on its own for Nature Comp Sci
- Uses BioEmu ensembles validated by the original BioEmu paper, not by our Alpha-M
  benchmark
- Faster timeline (September preprint vs. November)

**Alpha-M standalone:** "The Reality Gap in ML Force Fields for Protein Dynamics"
- Strong for Nature Methods or JCTC
- Independent contribution regardless of Gamma results
- Slower timeline (November-December preprint)

#### 2.3 Decision Framework

| Decision Date | Criterion | Outcome |
|--------------|-----------|---------|
| **June 30, 2026** | Gamma signal check: does RMSF correlate with DMS fitness for >50% of proteins? | If NO: kill Gamma, Alpha-M proceeds independently |
| **August 15, 2026** | Alpha-M compute progress: are >50% of MVP simulations (4/7 proteins x 3 MLFFs) complete or on track for October? | If NO: Gamma publishes standalone by October; Alpha-M continues independently |
| **September 30, 2026** | Integration test: for the 4 proteins with NMR data and ProteinGym overlap (ubiquitin, GB3, barnase, T4 lysozyme), does ensemble NMR accuracy correlate with fitness prediction accuracy? | If YES: commit to combined paper. If NO: publish separately -- both findings are individually strong |
| **October 15, 2026** | Final go/no-go for combined paper | Deadline: if Alpha-M simulations are not >80% complete by this date, split |

**Default position: Plan for combined, design for separability.** Every analysis step
in both Gamma and Alpha-M must be independently interpretable. The combined paper is
assembled from two modular halves, not written as a monolith.

### Component 3: Publication Sequence with Dates

#### 3.1 Specific Dated Milestones

**Delta (PerturbMark) -- Sprint Track:**

| Date | Milestone | Deliverable |
|------|-----------|-------------|
| May 1, 2026 | Project launch | Tahoe-100M download initiated; SLURM environment setup |
| May 7, 2026 | Data access confirmed | QC pipeline running; first cell line processed |
| May 15, 2026 | Preprocessing complete | Pseudobulk aggregates for all 50 cell lines ready |
| May 22, 2026 | Tier 0-3 splits defined | Cross-context evaluation framework operational |
| June 1, 2026 | Linear baselines complete | Mean, additive shift, ridge, matrix factorization, CRISPR-informed mean results |
| June 7, 2026 | Method installation checkpoint | Target: 8/10 DL methods running; remediation plan for failures |
| June 21, 2026 | DL method runs complete | All 10+ methods evaluated on all 4 tiers |
| June 28, 2026 | Metric calibration analysis | Miller et al. framework applied; DRF computed for all metrics |
| July 7, 2026 | Analysis complete | All figures, tables, statistical tests finalized |
| July 15, 2026 | Preprint posted | bioRxiv submission |
| August 1, 2026 | Journal submission | Nature Methods |

**Gamma (Ensembles-to-Function) -- Middle-Distance Track:**

| Date | Milestone | Deliverable |
|------|-----------|-------------|
| May 1, 2026 | Project launch | ProteinGym curation; BioEmu pipeline setup |
| May 15, 2026 | Protein list finalized | 200 eligible proteins identified with PDB structures |
| May 30, 2026 | MSA retrieval complete | ColabFold MSAs for all 200 proteins |
| June 15, 2026 | BioEmu Tier 1 sampling complete | 200 proteins x 2,000 conformations |
| June 30, 2026 | **SIGNAL CHECK (Kill Criterion)** | RMSF-fitness correlation across 200 proteins: go/no-go |
| July 15, 2026 | Feature extraction complete | 15 features x 200 proteins |
| August 1, 2026 | ML training complete | MLP, XGBoost, GNN under leave-protein-out CV |
| August 15, 2026 | Ablation analysis complete | Feature importance, assay-type stratification |
| September 1, 2026 | Variant-specific ensemble analysis | 50 proteins x 20 variants |
| September 7, 2026 | Manuscript draft complete | All figures and tables |
| September 15, 2026 | Preprint posted | bioRxiv submission |
| October 1, 2026 | Journal submission (if standalone) | Nature Computational Science |
| October 15, 2026 | Decision: standalone or combined with Alpha-M | Based on Alpha-M progress |

**Alpha-M (MLFF Crash Test) -- Marathon Track:**

| Date | Milestone | Deliverable |
|------|-----------|-------------|
| May 1, 2026 | Project launch | MLFF installation; ubiquitin system preparation |
| May 15, 2026 | Validation run starts | Ubiquitin x MACE-OFF24(M) x 10 ns (1 replica) |
| May 30, 2026 | **STABILITY CHECK (Kill Criterion)** | Ubiquitin stability results for all 3 MLFFs |
| June 1, 2026 | MVP launch (if pass) | 7 proteins x 3 MLFFs x 50 ns x 10 replicas begins |
| June-August 2026 | Simulations running | ~88K GPU-hrs consumed (spread across H200, RTX 5000 Ada) |
| August 15, 2026 | **COMPUTE PROGRESS CHECK** | >50% of simulations complete? |
| September 1, 2026 | MVP simulations complete | All 35 system-MLFF combinations finished |
| September 15, 2026 | Classical baselines complete | AMBER + CHARMM x 7 proteins x 50 ns x 10 replicas |
| October 1, 2026 | NMR back-calculation complete | SPARTA+, Karplus, S2, Pepsi-SAXS for all trajectories |
| October 15, 2026 | Analysis and figures complete | S2 R2, J-coupling RMSD, shift correlations |
| October 30, 2026 | **INTEGRATION DECISION** | Combined with Gamma or standalone? |
| November 15, 2026 | Preprint posted | bioRxiv (combined or standalone) |
| December 1, 2026 | Journal submission | Nature Computational Science (combined) or Nature Methods (standalone) |

#### 3.2 Publication Venue Strategy

| Paper | Primary Venue | Fallback Venue | Key Selling Point |
|-------|-------------|---------------|------------------|
| Delta (PerturbMark) | Nature Methods | Genome Biology | Resolves active NatMeth controversy on NatMeth's own turf |
| Gamma standalone | Nature Computational Science | Genome Research | New modality for variant effect prediction |
| Alpha-M standalone | Nature Methods | JCTC | Community benchmark with practical recommendations |
| Gamma+Alpha-M combined | Nature Computational Science | N/A (split into separate papers) | Paradigm claim: validated dynamics predict function |

### Component 4: Gantt Chart (May-December 2026)

```
2026         May          June         July         Aug          Sep          Oct          Nov          Dec
Week:   1  2  3  4  |1  2  3  4  |1  2  3  4  |1  2  3  4  |1  2  3  4  |1  2  3  4  |1  2  3  4  |1  2  3  4  |

DELTA (PerturbMark)   Target: Nature Methods
[Download/QC ][Preprocess/Splits][Baselines   ][DL Methods        ][Metrics/Analysis  ][Write    ][PP][Sub][ --- Revisions --- ]
  |-data-ok?                                                          |-methods-ok?       |-preprint  |-NatMeth

GAMMA (Ensembles-to-Function)   Target: Nature Computational Science
[Setup/Curate    ][MSA/BioEmu Sampling        ][Features][ML Training   ][Ablation][VarSpec ][Write   ][PP ][Sub?][ -- Decision -- ]
                                                 |-signal?                          |-integ?   |-preprint |-standalone?

ALPHA-M (MLFF Crash Test)   Target: Nature Comp Sci (combined) or Nature Methods (standalone)
[Setup/Validate][Stab][------ MVP Simulations: 7 proteins x 3 MLFFs x 50ns x 10 rep ------][Classical][BackCalc][Analysis][Write ][PP][Sub]
                |-go?                                                      |-compute?                           |-combine?  |-preprint

DECISION POINTS (diamonds):
  May 15: Delta data access confirmed
  May 30: Alpha-M stability check (KILL if 2/3 MLFFs fail)
  June 7: Delta method installation checkpoint
  June 30: Gamma signal check (KILL if no RMSF-fitness correlation)
  July 15: Delta preprint-or-pivot
  Aug 15: Alpha-M compute progress check
  Sep 30: Integration test (4 overlap proteins)
  Oct 15: Final combined/separate decision
  Oct 30: Alpha-M analysis complete
  Nov 15: Final preprints posted

COMPUTE ALLOCATION (GPU-hrs per month):
  May:    Delta ~200 + Gamma ~50 + Alpha-M ~5,000 (validation) = ~5,250
  June:   Delta ~500 + Gamma ~100 + Alpha-M ~25,000 (MVP launch) = ~25,600
  July:   Delta ~300 + Gamma ~200 + Alpha-M ~25,000 (continuing) = ~25,500
  August: Delta ~70 + Gamma ~2,500 (ML) + Alpha-M ~25,000 (finishing) = ~27,570
  Sep:    Gamma ~1,700 (variants) + Alpha-M ~8,000 (classical+backCalc) = ~9,700
  Oct:    Gamma ~200 (supplementary) + Alpha-M ~2,000 (analysis) = ~2,200
  TOTAL:  ~95,820 GPU-hrs (within HPC capacity)
```

### Component 5: Risk Registry (Final)

#### 5.1 Alpha-M: Top 5 Risks

| # | Risk | Probability | Impact | Mitigation | Trigger | Owner |
|---|------|------------|--------|------------|---------|-------|
| A1 | MLFF instability: 2/3 MLFFs crash within 10 ns on ubiquitin | LOW (20%) | VERY HIGH | Pre-screen all 3 MLFFs on ubiquitin for 10 ns by May 30. If 1 fails, proceed with 2 MLFFs + note failure. If 2 fail, kill project. | RMSD >5 A or energy explosion within 10 ns | mlffeng |
| A2 | Compute overrun: MVP takes >12 weeks instead of 10 | MODERATE (30%) | HIGH | Budget 30% contingency. Reduce replicas from 10 to 5 for slowest MLFF. Drop crambin (smallest compute value) if needed. Use heterogeneous GPU fleet (H200 + RTX 5000 Ada). | Wall-clock tracking vs. projection at June 30 | mlffeng |
| A3 | No reality gap: all MLFFs match classical FFs on NMR observables | LOW-MOD (25%) | MODERATE | Reframe as positive finding for MLFF adoption. Target JCTC instead of NatCompSci. Narrative: "the materials science reality gap does not extend to biomolecular protein dynamics." | S2 R2 within 0.05 of classical FFs for all 3 MLFFs | bioval |
| A4 | NMR back-calculation pipeline systematic errors | LOW (15%) | HIGH | Validate SPARTA+ and Karplus against published AMBER/CHARMM benchmarks (Smith et al., 2024). Use multiple back-calculation tools (SPARTA+ + ShiftX2). Cross-validate S2 with CPPTRAJ. | Discrepancy >0.1 R2 vs. published classical FF results | bioval |
| A5 | Scooped by MACE/SO3LR group | VERY LOW (8%) | VERY HIGH | Speed. Begin May 1. Post preprint November 15 at latest. Monitor arXiv/bioRxiv weekly for competitor preprints. If scooped: reframe as independent confirmation or extend to different proteins/observables. | Competitor preprint on arXiv/bioRxiv | scopeadv |

#### 5.2 Gamma: Top 5 Risks

| # | Risk | Probability | Impact | Mitigation | Trigger | Owner |
|---|------|------------|--------|------------|---------|-------|
| G1 | No signal: BioEmu ensembles show zero correlation between RMSF and DMS fitness across >50% of proteins | MOD (25%) | VERY HIGH | Stratify by protein class, assay type, dynamic regime before killing. Signal may exist for flexible + binding/catalysis proteins but not for rigid + stability proteins. If confirmed negative across all strata: publish as negative result (PLOS Comp Bio). | June 30 signal check | ensfunc |
| G2 | Microsoft publishes BioEmu-DMS mapping | LOW-MOD (15%) | VERY HIGH | Speed. Post preprint September 15. If scooped: reframe as independent confirmation with different methodology (their approach likely differs in feature engineering and ML architecture). | Monitor Microsoft Research publications weekly | scopeadv |
| G3 | BioEmu quality degradation for >50% of ProteinGym proteins | LOW (15%) | HIGH | Pre-screen BioEmu on first 50 proteins. Check Rg distribution against experimental/AlphaFold values. If >50% fail quality checks: reduce protein set to quality-passing subset. Report failure rate transparently. | Rg deviation >30% from reference for majority of proteins | ensfunc |
| G4 | Ensemble features are a proxy for stability (dG), not dynamics | MOD (30%) | MODERATE | Include ddG_fold (ThermoMPNN-predicted) as explicit baseline feature. Ablation: dynamics features must add signal beyond ddG. If dynamics = ddG proxy: still publishable but reframe as "dynamics encode stability information accessible without evolutionary data." | Feature importance analysis at August 15 | evalstat |
| G5 | Overfitting: 15 features on 217 assays under leave-protein-out CV | MOD (25%) | MODERATE | Nested CV with strict L1 regularization. Start with 5 core features (RMSF, contacts, Rg, SASA, S2). Only add features that survive permutation importance testing. Maximum effective features limited to sqrt(N_proteins) ~15. | Inner CV loss diverges from outer CV by >20% | evalstat |

#### 5.3 Delta: Top 5 Risks

| # | Risk | Probability | Impact | Mitigation | Trigger | Owner |
|---|------|------------|--------|------------|---------|-------|
| D1 | Scooped: another group publishes Tahoe-100M cross-context benchmark | HIGH (30%) | HIGH | Speed. Preprint July 15. Our differentiators (calibrated metrics, 4 tiers, 2026 methods, linear baseline suite) are difficult to replicate quickly. Even if partially scooped, our comprehensive coverage adds value. | Competitor preprint on bioRxiv | scopeadv |
| D2 | Method reproducibility: <6 of 10 DL methods can be run on Tahoe-100M | MOD (35%) | MODERATE | Start method installation May 1. Contact authors of closed/broken repos by May 15. Budget 2-3 weeks for engineering. Use containerized environments. Document all failures transparently as part of benchmark. | June 7 method checkpoint | pertbio |
| D3 | Tahoe-100M data quality issues (batch effects, confounders) | LOW (15%) | MODERATE | Extensive QC pipeline per pertbio proposal (ambient RNA, plate effects, ComBat). Validate against published Tahoe Bio analyses. Flag issues transparently. | >10% variance explained by plate effects on DMSO controls | pertbio |
| D4 | DL-vs-baselines controversy resolves by consensus before publication | MOD (25%) | HIGH | Speed. Post preprint July 15. Even if consensus forms, PerturbMark adds definitive evidence on the largest dataset with the most rigorous methodology. Frame as "the definitive test" rather than "the first test." | Major synthesis paper in Nature/Nature Methods before July 15 | scopeadv |
| D5 | Tahoe-100M download/access failure | VERY LOW (5%) | VERY HIGH | CC0 license on HuggingFace. Multiple mirrors (DNAnexus, HuggingFace). 429 GB is large but manageable. Test download immediately May 1. If HF fails, use DNAnexus. | May 7 data access checkpoint | pertbio |

### Component 6: Kill Criteria (Falsifiable, Dated)

#### 6.1 Hard Kill Criteria

These trigger immediate project termination with resource reallocation.

| Project | Kill Criterion | Date | Assessment Method | Fallback |
|---------|---------------|------|-------------------|----------|
| Alpha-M | 2 of 3 MLFFs fail stability test (RMSD >5 A within 10 ns on ubiquitin) | May 30, 2026 | 10 ns production run with MACE-OFF24(M), SO3LR, AI2BMD on ubiquitin | Redirect 88K GPU-hrs to Gamma variant analysis (expand from 50 to 200 proteins) and exploratory Alpha-M on the 1 surviving MLFF |
| Alpha-M | Total compute exceeds 150K GPU-hrs for MVP with no path to completion by November | June 30, 2026 | Wall-clock extrapolation from first 4 weeks of production | Reduce to 4 proteins x 2 MLFFs; target JCTC |
| Gamma | No ensemble feature adds statistically significant predictive power (paired t-test, p > 0.01 after Bonferroni) beyond ESM-1v for ANY protein functional category | August 30, 2026 | Leave-protein-out CV on 200 proteins, stratified by assay type | Publish negative result (PLOS Comp Bio / Bioinformatics); redirect resources to Alpha-M integration analysis |
| Gamma | BioEmu fails quality check (Rg deviation >30% from reference) for >50% of candidate proteins | June 30, 2026 | Automated Rg comparison against AlphaFold/experimental values | Reduce protein set to quality-passing subset; if <50 proteins pass, KILL |
| Delta | Tahoe-100M inaccessible or corrupted after 7 days of download attempts | May 7, 2026 | Download verification (checksums, row counts) | Pivot to Replogle + Norman + scPerturb datasets; reframe as genetic perturbation benchmark |
| Delta | <6 of 10 target methods reproducible on Tahoe-100M | June 15, 2026 | Method runs on test subset (1 cell line, 10 compounds) | Reduce to methods that work; document failures as finding; if <4 methods, KILL and redirect to meta-analysis paper |

#### 6.2 Soft Pivot Criteria

These trigger strategy adjustment, not termination.

| Project | Pivot Criterion | Date | Action |
|---------|----------------|------|--------|
| Alpha-M | All MLFFs match classical FFs (S2 R2 within 0.05) | October 2026 | Reframe as "no biomolecular reality gap" -- still novel. Target JCTC/Nat Methods instead of Nat Comp Sci |
| Gamma | Signal exists for only 10-30 proteins (<15% of dataset) | August 2026 | Publish as targeted case study (PLOS Comp Bio). Focus paper on "which proteins benefit from dynamics and why" |
| Gamma | AlphaMissense + ensemble features does NOT beat AlphaMissense alone | September 2026 | Drop integration narrative. Focus paper on standalone ensemble-only prediction as a new modality |
| Delta | Results match scPerturBench exactly with no new insight | July 2026 | Add novel metric calibration analysis as primary contribution. Target Genome Biology |
| Combined | Alpha-M simulations <50% complete by Oct 15 | October 2026 | Split: Gamma submits standalone (Oct/Nov). Alpha-M submits independently when ready (Dec/Jan) |

### Component 7: Minimum Viable Experiments

#### 7.1 Alpha-M MVP

| Parameter | Minimum | Current Plan | Justification |
|-----------|---------|-------------|---------------|
| MLFFs | 3 (MACE-OFF24(M), SO3LR, AI2BMD) | 3 | Spans 3 architectures (equivariant, neural+pairwise, fragmentation) |
| Classical baselines | 2 (AMBER ff19SB, CHARMM36m) | 2 | Community standards; 30 years of refinement |
| Proteins | 5 (ubiquitin, GB3, HEWL, barnase, T4 lysozyme) | 7 | 5 is absolute minimum; 4 overlap with ProteinGym |
| Simulation length | 30 ns (production) | 50 ns | S2 converges at ~20-50 ns with replicas |
| Replicas per system | 5 | 10 | 5 gives R2 reproducibility ~0.85; 10 gives ~0.90 |
| NMR observables | S2 + 3J(HN,Ha) | S2 + 3J + shifts + SAXS | S2 and J-couplings are most discriminating |
| Compute (GPU-hrs) | ~30,000 | ~88,000 | MVP at 5 proteins x 3 MLFFs x 30ns x 5 rep |
| BioEmu comparator | Yes (for Gamma integration) | Yes | ~200 GPU-hrs; trivial marginal cost |

**Absolute floor (below which paper is not credible):** 3 proteins x 2 MLFFs x 20 ns.
This would be a "preliminary report" level, not Nature Comp Sci.

#### 7.2 Gamma MVP

| Parameter | Minimum | Current Plan | Justification |
|-----------|---------|-------------|---------------|
| ProteinGym proteins | 50 | 200 | 50 proteins give statistical power for stratified analysis |
| BioEmu conformations/protein | 500 | 2,000 | RMSF converges at ~100-500; contacts need ~500 |
| Ensemble features | 5 (RMSF, contacts, Rg, SASA, S2) | 15 | Core features have strongest prior evidence |
| ML models | 2 (ridge regression, XGBoost) | 4 (+ MLP, GNN) | Ridge is the sanity check; XGBoost provides nonlinearity |
| Baselines | 3 (ESM-1v, EVE, GEMME) | 5+ | Must include ESMDance (direct dynamics competitor) |
| Evaluation | 10-fold stratified CV | Leave-protein-out + temporal holdout | CV is minimum; LPO is required for NatCompSci |
| Compute (GPU-hrs) | ~500 (BioEmu) + ~50 (ML) | ~2,000 + ~500 | 50 proteins x 500 conformations |
| Alpha-M overlap proteins | 4 (for integration) | 8 | 4 is minimum for correlation analysis |

**Absolute floor:** 30 proteins x 500 conformations x 5 features x ridge regression.
This is a "proof of concept" level, publishable in Bioinformatics but not Nature.

#### 7.3 Delta MVP

| Parameter | Minimum | Current Plan | Justification |
|-----------|---------|-------------|---------------|
| Primary dataset | Tahoe-100M | Same | The anchor dataset; non-negotiable |
| Secondary datasets | Replogle K562 | + Replogle RPE1, Norman | At least 1 genetic perturbation dataset for generality |
| Methods benchmarked | 8 (5 DL + 3 linear) | 10+ (8 DL + 5 linear) | Must include scPPDM, GEARS, scGPT, CPA, ridge |
| Linear baselines | 3 (mean, additive shift, ridge) | 5 (+ matrix factorization, CRISPR-informed) | 3 mandatory for DL-vs-baselines comparison |
| Cross-context tiers | 4 (Tier 0-3) | 4 | This IS the differentiation; non-negotiable |
| Calibrated metrics | 4 (WMSE, rank-corr, DEG-F1, calibrated PCC) | 7 | Must include Miller et al. DRF framework |
| Positive/negative controls | DMSO controls + interpolated duplicates | Same | Required for metric calibration |
| Compute (GPU-hrs) | ~700 | ~1,070 | Dominated by DL model training/inference |

**Absolute floor:** Tahoe-100M + 5 methods (3 DL + 2 linear) + Tier 0-2 only + 4 metrics.
Tier 3 can be cut if sample size is insufficient, but this weakens the paper significantly.

### Component 8: Narrative Framing

#### 8.1 Delta: PerturbMark

**Paper title:** "PerturbMark: A Cross-Context Benchmark Resolving the Perturbation
Prediction Controversy"

**One-sentence claim:** At sufficient scale and under calibrated metrics, deep learning
methods outperform linear baselines for chemical perturbation prediction, but
generalization degrades sharply with increasing context novelty, with most methods
failing at Tier 3 (unseen compound in unseen cell type).

**Anticipated editor reaction (Nature Methods):** "This directly addresses a controversy
we published. The Tahoe-100M dataset is the right testbed, and the tiered difficulty
framework provides the nuance the field needs. Review it."

**Differentiation from scPerturBench:** scPerturBench benchmarked 27 methods but did not
include Tahoe-100M (10x larger), did not define cross-context difficulty tiers (0-3),
used 4 of 6 metrics with documented failure modes, and froze before the March 2026 model
explosion. PerturbMark is the next-generation benchmark.

**Differentiation from scPPDM:** scPPDM evaluated ONE new method on Tahoe-100M. We
evaluate 10+ methods (including scPPDM) with calibrated metrics, systematic linear
baselines, and difficulty tiers. We are the benchmark; they are one entry in it.

**What if DL beats baselines convincingly?** Still publishes. The story becomes:
"The controversy was a measurement artifact -- under calibrated metrics, DL exceeds
baselines. But generalization is the real frontier." Nature Methods will publish this.

**What if DL fails?** Still publishes. The story becomes: "Even at 100M-cell scale,
deep learning for perturbation prediction does not outperform simple baselines --
the field needs fundamentally different approaches." Nature Methods will also publish
this.

#### 8.2 Gamma (Standalone)

**Paper title:** "Conformational Ensembles Predict Protein Function Beyond Sequence"

**One-sentence claim:** Explicit conformational ensemble features from BioEmu add
statistically significant predictive power for mutation effect prediction beyond
sequence-only and static-structure methods, with the largest gains for binding and
catalytic function assays where dynamics drives function.

**Anticipated editor reaction (Nature Comp Sci):** "This is a new modality for variant
effect prediction that connects biophysics to function. The ProteinGym benchmark makes
it rigorous. If the signal is real and the analysis is clean, review it."

**Differentiation from ESMDance:** ESMDance uses implicit dynamics learned during
training. Gamma uses explicit structural ensembles from generated conformations.
ESMDance shows dynamics matter; Gamma shows *which structural features* drive the
effect and provides interpretable, physically grounded explanations.

**What if signal exists only for subset?** Still publishes. "Dynamics helps for
[binding/catalysis/flexible] proteins but not [stability/rigid] proteins" is a more
nuanced and arguably more interesting finding than a blanket positive.

#### 8.3 Combined: Gamma + Alpha-M

**Paper title:** "From Accurate Ensembles to Biological Function: Validating and
Applying ML Protein Dynamics"

**One-sentence claim:** ML force fields produce physically realistic protein dynamics
that match experimental NMR observables, and these validated conformational ensembles
predict protein function (DMS fitness) better than static structures alone, establishing
a new paradigm linking ensemble quality to functional prediction.

**Anticipated editor reaction (Nature Comp Sci):** "This is a rare paper that bridges
computational methods validation and biological application. The combined narrative --
validate, then apply -- is compelling. The 8-protein overlap set provides the key
integration test. High priority for review."

**Differentiation from all prior work:** No paper has (a) systematically benchmarked
multiple MLFFs against experimental protein observables AND (b) shown that ensemble
quality affects functional prediction. The closest precursors are in separate domains
(UniFFBench for materials; ESMDance for dynamics-function) -- we bridge them for the
first time.

**The integration claim (the key figure):** For the 4+ proteins in both Alpha-M and
Gamma, plot: (x-axis) MLFF NMR agreement (S2 R2) vs. (y-axis) Gamma functional
prediction accuracy (Spearman rho improvement over ESM-1v). If the correlation is
positive, the paper's central thesis is validated: "better physics produces better
biology."

#### 8.4 The "Nature Editor Reading 50 Titles" Test

Each title must communicate (a) what is new, (b) the main finding, and (c) why it
matters, in <15 words:

- **Delta:** "PerturbMark" immediately signals benchmark; "Cross-Context" signals
  novelty; "Controversy" signals impact.
- **Gamma:** "Conformational Ensembles" signals dynamics; "Predict Function" signals
  application; "Beyond Sequence" signals paradigm shift.
- **Combined:** "Accurate Ensembles" = validation; "Biological Function" = application;
  "ML Protein Dynamics" = method.

All three titles pass. An editor can tell at a glance what is new and why it matters.

### Component 9: Compute Resource Allocation

#### 9.1 Total Compute Budget

| Project | Specialist Estimate | My Revised Estimate | Phase |
|---------|-------------------|-------------------|-------|
| Delta | ~1,070 GPU-hrs (pertbio) | ~1,200 GPU-hrs (10% buffer) | May-July 2026 |
| Gamma | ~3,000 GPU-hrs (ensfunc: 143 Tier1 + 1,700 Tier2 + 500 ML + buffer) | ~3,200 GPU-hrs | May-September 2026 |
| Alpha-M | ~88,000 GPU-hrs (mlffeng: 7 proteins x 5 methods x 50ns x 10 rep) | ~95,000 GPU-hrs (10% buffer) | May-November 2026 |
| **TOTAL** | **~92,000** | **~99,400** | -- |

#### 9.2 Monthly Compute Allocation and GPU Priority Queue

| Month | Delta | Gamma | Alpha-M | Total | Priority |
|-------|-------|-------|---------|-------|----------|
| May 2026 | 200 | 50 | 5,000 | 5,250 | Delta data prep > Alpha-M validation > Gamma setup |
| June 2026 | 500 | 100 | 25,000 | 25,600 | Alpha-M production > Delta methods > Gamma sampling |
| July 2026 | 300 | 200 | 25,000 | 25,500 | Alpha-M production > Delta analysis > Gamma features |
| August 2026 | 70 | 2,500 | 25,000 | 27,570 | Alpha-M production > Gamma ML > Delta wrap-up |
| September 2026 | 0 | 1,700 | 8,000 | 9,700 | Alpha-M classical > Gamma variants > -- |
| October 2026 | 0 | 200 | 2,000 | 2,200 | Alpha-M back-calc > Gamma supplementary > -- |
| November 2026 | 0 | 100 | 1,000 | 1,100 | Alpha-M analysis > Gamma revision > -- |
| **TOTAL** | **1,070** | **4,850** | **91,000** | **96,920** | -- |

#### 9.3 GPU Type Assignment

| GPU | Count (est.) | Assignment | Rationale |
|-----|-----------|-----------|-----------|
| H200 (141 GB HBM3e) | Primary | Alpha-M MLFF simulations | MLFFs need maximum memory bandwidth; H200's 4.8 TB/s is essential for MACE/SO3LR inference |
| RTX 5000 Ada | Secondary | Alpha-M overflow + Gamma BioEmu sampling | BioEmu runs on any modern GPU; RTX 5000 Ada sufficient for medium proteins |
| B200 | Available | Alpha-M large proteins (T4 lysozyme, barnase) | B200 for systems >15K atoms if available |
| CPU nodes | Hundreds | Delta preprocessing + NMR back-calculation + Gamma MSA retrieval | Delta is CPU-dominated; SPARTA+ runs on CPU; MMseqs2 for MSAs |

#### 9.4 Priority Queue Strategy

**Rule 1: Delta first for CPU.** Delta's data preprocessing (429 GB Tahoe-100M) is
CPU-intensive and blocking. Allocate 16-32 CPU cores immediately May 1.

**Rule 2: Alpha-M gets GPU priority June-August.** This is the compute bottleneck for
the entire portfolio. Alpha-M simulations should occupy 80%+ of H200 GPUs during this
period.

**Rule 3: Gamma gets remaining GPU scraps May-July, then priority in August-September.**
BioEmu sampling can run on any GPU and is not time-critical until August.

**Rule 4: Never let GPUs sit idle.** If Alpha-M simulations queue for >4 hours, run
Gamma BioEmu sampling in the gap.

**Rule 5: After July 15 (Delta preprint), reallocate all Delta CPU resources to Alpha-M
back-calculation pipeline.**

### Component 10: Worst Case Still Publishes

#### 10.1 Alpha-M Worst Case

**Scenario:** All 3 MLFFs produce S2 R2 values within 0.05 of classical FFs (AMBER
ff19SB R2 ~0.62, CHARMM36m R2 ~0.51). No "reality gap."

**Still publishes?** YES.

**Paper:** "Machine Learning Force Fields Match Classical Force Fields for Protein
NMR Observables: The Reality Gap Does Not Extend to Biomolecular Dynamics"

**Venue:** JCTC (primary), J. Phys. Chem. Lett. (secondary)

**Argument:** The materials science reality gap (UniFFBench) was a major concern for
the MLFF community. Showing that this gap does NOT exist for proteins is a positive
and actionable finding: researchers can confidently use MLFFs for protein dynamics
without accuracy concerns. This also raises the question of WHY proteins are easier
than materials for MLFFs (softer interactions, more training data at relevant scales,
less sensitivity to long-range effects).

**Impact:** Moderate. JCTC acceptance likely. Not Nature-level but still a solid,
useful contribution.

#### 10.2 Gamma Worst Case

**Scenario:** No ensemble feature adds statistically significant predictive power
beyond ESM-1v for ANY protein functional category, across all 200 proteins.

**Still publishes?** CONDITIONALLY.

**Paper:** "Explicit Conformational Dynamics Do Not Improve Deep Mutational Scanning
Fitness Prediction: Sequence Models Already Capture Dynamics-Relevant Information"

**Venue:** PLOS Computational Biology (primary), Bioinformatics (secondary)

**Argument:** This is an important negative result IF the analysis is rigorous (200
proteins, 15 features, proper CV, clear ablations). The finding implies that protein
language models have already learned to encode dynamics-relevant information from
evolutionary sequences, making explicit structural ensembles redundant for fitness
prediction. This has practical implications: skip the expensive ensemble generation.

**Condition for publication:** Must demonstrate that the negative result is not due
to BioEmu quality issues, insufficient protein coverage, or methodological failures.
The analysis must be as thorough as a positive result paper.

**Impact:** Low-moderate. Important for the community to know, but not high-impact.

#### 10.3 Delta Worst Case

**Scenario:** PerturbMark results match scPerturBench conclusions exactly. DL fails
on standard metrics, DL wins on calibrated metrics, same tier-independent patterns.

**Still publishes?** YES.

**Paper:** "PerturbMark Confirms and Extends the Perturbation Prediction Benchmark on
100-Million-Cell Scale: Cross-Context Difficulty Is the Frontier"

**Venue:** Genome Biology (primary), Nature Methods (if tier framework adds sufficient
novelty)

**Argument:** Even confirming prior findings on a 10x larger dataset (Tahoe-100M) with
a more rigorous methodology (calibrated metrics, 4 difficulty tiers, 2026 methods) adds
substantial value. The Tahoe-100M-specific results are novel regardless. The tier
framework shows WHERE the field needs to improve (Tier 3 cross-context generalization).

**Impact:** Moderate. Genome Biology acceptance likely. Nature Methods possible if the
tier framework and 2026 method inclusion are seen as sufficiently novel.

#### 10.4 Portfolio Worst Case

**Absolute worst case:** Alpha-M shows no gap, Gamma shows no signal, Delta confirms
prior findings.

**Still publishes?** YES. Three papers: JCTC (Alpha-M), PLOS Comp Bio (Gamma), Genome
Biology (Delta). None are Nature-level, but the team produces three solid contributions
with rigorous methodology. Total citations likely >50 each within 2 years.

**This scenario is UNLIKELY.** The probability that all three show null results is the
product of individual null probabilities: ~0.25 x 0.25 x 0.15 = 0.9%. The expected
outcome is at least one project producing a high-impact result.

---

## Impact Assessment

### Publication Strategy

**Target venue (portfolio):** Nature Computational Science + Nature Methods

**Main claims:**
1. (Delta) The DL-vs-baselines controversy is resolved by proper metrics and scale
2. (Combined) Validated ML dynamics predict protein function -- a new paradigm

**Expected reviewer concerns:**

For Delta:
- "How is this different from scPerturBench?" -- Tahoe-100M, tiers, calibrated metrics
- "You couldn't run all methods." -- Document failures transparently as findings
- "Sample size in Tier 3 is too small." -- Power analysis shows adequacy; 190 conditions
  per fold across 5 folds = 950 total

For Combined:
- "Two papers stapled together." -- The integration (4-8 overlap proteins) is the glue
- "Simulation lengths too short for MLFFs." -- Convergence analysis with block-averaged
  errors and multi-replica design
- "BioEmu ensembles are not MLFFs." -- Explicitly distinguished; BioEmu is a comparator
  (non-MD), not an MLFF

**Comparison baselines:**
- Alpha-M: AMBER ff19SB, CHARMM36m (30 years of optimization)
- Gamma: ESM-1v, EVE, GEMME, AlphaMissense, ESMDance
- Delta: Mean control, additive shift, ridge, CRISPR-informed mean, matrix factorization

### Novelty Assessment

| Project | Genuinely Novel | Engineering of Existing |
|---------|----------------|----------------------|
| Alpha-M | First systematic multi-MLFF vs experimental protein NMR benchmark | Pipeline (OpenMM-ML, SPARTA+, Karplus) uses established tools |
| Gamma | First mapping of explicit ensemble features to DMS fitness at scale | BioEmu, ProteinGym, feature extraction are existing tools |
| Delta | Tier 0-3 cross-context framework + calibrated metrics on Tahoe-100M | Method evaluation uses existing implementations |
| Combined | Integration: ensemble quality predicts functional accuracy | Individual components are engineering; the connection is novel |

### Broader Impact

- **Alpha-M:** Shifts MLFF evaluation from DFT-only to experiment-grounded. Every future
  MLFF paper will need to report NMR agreement.
- **Gamma:** Opens a new modality for variant effect prediction. Downstream: protein
  engineering, therapeutic antibody design, enzyme optimization.
- **Delta:** Provides the field's standard benchmark for perturbation prediction. Downstream:
  drug discovery, cellular programming, virtual cell development.
- **Combined:** Establishes "validated dynamics predict function" as a paradigm. Downstream:
  drug design pipelines that use MLFF ensembles for target validation.

---

## Evaluation Plan

### Primary Metrics

**Alpha-M:** S2 R2 (coefficient of determination vs. experimental S2), J-coupling RMSE
(Hz), chemical shift RMSE (ppm per nucleus), SAXS chi-squared. Aggregated via
Friedman/Nemenyi multi-level framework (evalstat).

**Gamma:** Spearman rho (per-protein), win rate vs. baselines (head-to-head), delta-rho
improvement over ESM-1v stratified by assay type. Bonferroni-corrected paired testing.

**Delta:** WMSE (primary calibrated metric), rank-correlation, DEG-F1, calibrated PCC,
DEG logFC recovery, Energy distance, Wasserstein distance (reported but not primary).
Dynamic Range Fraction for each metric.

### Baselines

See Component 7 (MVP) for complete baseline specifications per project.

### Ablation Studies

**Alpha-M:** MLFF vs. classical FF vs. BioEmu (non-MD comparator). Per-observable
analysis (S2 alone, J-coupling alone, shifts alone). Water model comparison
(full-ML vs. ML/MM).

**Gamma:** Feature category ablation (per-residue only, pairwise only, global only).
Single-feature ablation (RMSF alone, contacts alone). Architecture ablation (ridge vs.
XGBoost vs. MLP vs. GNN). Ensemble size ablation (100 vs. 500 vs. 1000 vs. 2000
conformations). Wildtype-only vs. wildtype + variant-specific ensembles.

**Delta:** Metric sensitivity (calibrated vs. uncalibrated). Tier sensitivity (results
by tier). Gene set sensitivity (DEGs vs. HVGs vs. all genes). Normalization sensitivity
(log1p vs. Pearson residuals). Batch correction sensitivity (none vs. ComBat vs. DMSO
normalization).

### Validation Strategy

All validation is computational, using existing published experimental data:

- Alpha-M: NMR data from BMRB, SAXS from SASBDB
- Gamma: DMS fitness data from ProteinGym, pre-computed baseline scores
- Delta: Single-cell data from Tahoe-100M (CC0), Replogle (Figshare)

No wet lab required.

---

## Risks and Mitigations

See Component 5 (Risk Registry) for the comprehensive 15-risk table with probability,
impact, mitigation, triggers, and owners.

**Portfolio-level risk summary:**

| Risk Level | Alpha-M | Gamma | Delta |
|-----------|---------|-------|-------|
| Scoop risk | LOW (<10%) | MODERATE (15-25%) | HIGH (25-35%) |
| Technical risk | LOW-MODERATE (stability, compute) | MODERATE (signal may not exist) | LOW (engineering, not research) |
| Timeline risk | HIGH (12-14 weeks of simulation) | LOW-MODERATE (11 weeks) | LOW (6 weeks) |
| Publication risk | LOW (worst case: JCTC) | MODERATE (worst case: PLOS Comp Bio) | LOW (worst case: Genome Biology) |

**Expected outcome (80th percentile):** 2 high-impact publications (Nature Comp Sci +
Nature Methods), posted as preprints July-November 2026.

---

## Open Questions

1. **Alpha-M compute allocation across GPU types:** How much does H200 vs. RTX 5000 Ada
   vs. B200 affect MLFF simulation speed? Need benchmarking data for MACE-OFF24(M) on
   each GPU type to optimize SLURM scheduling. mlffeng should run a 100-step timing test
   on each GPU type for ubiquitin.

2. **BioEmu v1.2 vs. v1.0 quality for ProteinGym proteins:** Has BioEmu v1.2 been
   validated on a diverse protein set beyond the original paper? ensfunc should check
   whether the MEGAscale training data overlaps with ProteinGym proteins (potential
   circular validation concern).

3. **scPPDM availability:** Is the scPPDM code publicly available for inclusion in
   PerturbMark? pertbio should check the ICLR 2026 submission for code/model release.
   If not available, contact authors immediately.

4. **Classical FF baseline timing:** Can AMBER ff19SB and CHARMM36m complete 7 proteins x
   50 ns x 10 replicas in <4 weeks on CPU nodes? These run at ~100 ns/day in OpenMM on
   modern CPUs, so 3,500 ns total should take ~35 CPU-days of wall time. Confirm with
   mlffeng.

5. **Metric calibration for Alpha-M:** evalstat defined Friedman/Nemenyi for MLFF
   comparison, but should we also compute a composite "overall NMR agreement" score that
   combines S2, J-couplings, and shifts into a single ranking? This simplifies the
   narrative but loses nuance. Need evalstat's recommendation.

6. **Personnel allocation:** The timeline assumes 3 people full-time. If only 2 are
   available, Delta must be prioritized (fastest to complete, highest urgency), with
   Gamma second and Alpha-M third. Alpha-M can tolerate delay (widest competition window).

7. **Pre-registration:** evalstat recommends pre-registering all three evaluation protocols
   on OSF before analysis begins. This strengthens the publication case but adds 2-3 days
   of setup. Recommendation: pre-register Delta and Gamma (highest-stakes claims);
   Alpha-M can be pre-registered during the simulation compute phase.

---

## References

1. Kovacs, D. P. et al. (2025). MACE-OFF: Short-Range Transferable Machine Learning Force
   Fields for Organic Molecules. *Journal of the American Chemical Society*.
   https://pubs.acs.org/doi/10.1021/jacs.4c07099

2. Frank, M. et al. (2026). Molecular Simulations with a Pretrained Neural Network and
   Universal Pairwise Force Fields (SO3LR). *Journal of the American Chemical Society*.
   https://pubs.acs.org/doi/10.1021/jacs.5c09558

3. Li, Z. et al. (2024). Ab initio characterization of protein molecular dynamics with
   AI2BMD. *Nature*, 636, 1058-1062. https://www.nature.com/articles/s41586-024-08127-z

4. Mannan, A. et al. (2025). UniFFBench: Benchmarking Universal Machine Learning Force
   Fields Against Experimental Data. *arXiv*, 2508.05762.

5. Lindorff-Larsen, K. et al. (2012). Are Protein Force Fields Getting Better? A Systematic
   Benchmark on 524 Diverse NMR Measurements. *Journal of Chemical Theory and Computation*,
   8(9), 3257-3273.

6. Smith, M. et al. (2024). Convergence of S2 Order Parameters from Molecular Dynamics
   Simulations. *Journal of Physical Chemistry B*.

7. Cavender, C. E. et al. (2025). Structure-Based Experimental Datasets for Benchmarking
   Protein Simulation Force Fields. *Living Journal of Computational Molecular Science*,
   6(1), e3871.

8. Jing, B. et al. (2025). Scalable emulation of protein equilibrium ensembles with
   generative deep learning (BioEmu). *Science*, 369, 270-278.

9. Aryal, B. et al. (2026). Assessing the Performance of BioEmu in Understanding Protein
   Dynamics. *International Journal of Molecular Sciences*, 27(6), 2896.

10. Hou, S., Zhao, C., & Shen, H. (2026). Protein Language Models Trained on Biophysical
    Dynamics Inform Mutation Effects (SeqDance/ESMDance). *PNAS*, 123(4).

11. Notin, P. et al. (2023). ProteinGym: Large-Scale Benchmarks for Protein Design and
    Fitness Prediction. *NeurIPS Datasets and Benchmarks*.

12. Wei, J. et al. (2026). Benchmarking algorithms for generalizable single-cell perturbation
    response prediction (scPerturBench). *Nature Methods*, 23, 451-464.

13. Miller, J. et al. (2025). Deep Learning-Based Genetic Perturbation Models Do Outperform
    Uninformative Baselines on Well-Calibrated Metrics. *bioRxiv*.

14. Dibaeinia, P. et al. (2026). Evaluating Single-Cell Perturbation Response Models Is Far
    from Straightforward. *bioRxiv*.

15. Cole, E. et al. (2026). Foundation Models Improve Perturbation Response Prediction.
    *bioRxiv*.

16. Zhang, Z. et al. (2025). Tahoe-100M: A Giga-Scale Single-Cell Perturbation Atlas.
    *bioRxiv*.

17. Li, Z. et al. (2026). Towards building a World Model to simulate perturbation-induced
    cellular dynamics (AlphaCell). *bioRxiv*.

18. Wang, J. et al. (2026). AetherCell: A generative engine for virtual cell perturbation
    and in vivo drug discovery. *bioRxiv*.

19. Kim, M. et al. (2026). X-Cell: Scaling Causal Perturbation Prediction Across Diverse
    Cellular Contexts via Diffusion Language Models. *bioRxiv*.

20. Zhu, J. & Li, W. (2026). Scouter predicts transcriptional responses to genetic
    perturbations with large language model embeddings. *Nature Computational Science*.

21. scPPDM (2026). A Diffusion Model for Single-Cell Drug-Response Prediction. *arXiv*,
    2510.11726 / *ICLR 2026 submission*.

22. Bojan, M. et al. (2026). Representing local protein environments with machine learning
    force fields. *arXiv*, 2505.23354.

23. Virtual Cell Challenge 2025 Wrap-Up: Winners and Reflections. Arc Institute.
    https://arcinstitute.org/news/virtual-cell-challenge-2025-wrap-up

24. Tahoe-x1 (2025). Scaling Perturbation-Trained Single-Cell Foundation Models to 3 Billion
    Parameters. *bioRxiv*.

25. Robustelli, P. et al. (2018). Developing a molecular dynamics force field for both folded
    and disordered protein states. *PNAS*, 115(21), E4758-E4766.

26. Monteiro da Silva, G. et al. (2026). Accelerated sampling of protein dynamics using BioEmu
    augmented molecular simulation. *bioRxiv*.

27. Mutational robustness-dynamics correlation (2026). *bioRxiv*, March 2026.

28. eRMSF (2026). Ensemble-based RMSF analysis package. *Journal of Chemical Information
    and Modeling*.

29. Unke, O. et al. (2024). Biomolecular dynamics with machine-learned quantum-mechanical
    force fields trained on diverse chemical fragments (GEMS). *Science Advances*.

30. Batzner, S. et al. (2025). Crash testing machine learning force fields for molecules,
    materials, and interfaces (TEA Challenge 2023). *Chemical Science*.

31. Waibl, F. et al. (2025). ANI-2x produces amorphous solid water. *Journal of Chemical
    Information and Modeling*.

32. Shen, Y. & Bax, A. (2010). SPARTA+: Protein backbone chemical shift prediction.
    *Journal of Biomolecular NMR*, 48(1), 13-22.

33. Grudinin, S. et al. (2017). Pepsi-SAXS: An adaptive method for rapid and accurate
    computation of SAXS profiles. *Acta Crystallographica D*, 73, 449-464.
