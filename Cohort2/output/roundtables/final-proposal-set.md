---
agent: orch
round: 3
date: 2026-04-14
type: roundtable-synthesis
---

# Final Proposal Set: Cohort 2 Deep Divers

## Executive Summary

After 3 rounds of research, proposal development, and cross-review by 6 specialists
(18 agent launches, 10 formal documents totaling ~9,000 lines, 250+ citations), the
Cohort 2 Deep Divers deliver three execution-ready research proposals. Each has
survived hostile review by 2-3 domain experts and incorporates their modifications.

**The portfolio:**

| Project | Venue | Compute | Timeline | Scoop Risk | Status |
|---------|-------|---------|----------|------------|--------|
| Gamma+Alpha-M (combined) | Nature Comp Sci | ~110,900 GPU-hrs | 16-18 weeks | <10% (6 mo) | Primary target |
| Delta (PerturbMark) | Nature Methods | ~1,070 GPU-hrs | 12 weeks | Moderate | Parallel track |
| Alpha-M (standalone fallback) | Nature Methods | ~107,800 GPU-hrs | 14-16 weeks | <10% | Fallback |
| Gamma (standalone fallback) | NCS / Genome Res | ~3,100 GPU-hrs | 14 weeks | 25-35% | Fallback |

**Key decision:** Pursue the combined Gamma+Alpha-M paper as the primary target
(Nature Computational Science), with standalone papers as a pre-planned fallback.
Decision point: September 30, 2026. Delta executes in parallel on an independent
timeline.

---

## Part I: Alpha-M -- The MLFF Biomolecular Crash Test

### Final Scope (Post-Review)

**Claim:** The first systematic benchmark of ML force fields against experimental
protein NMR and SAXS observables, revealing whether the "reality gap" identified
for materials MLFFs extends to biomolecular simulation.

**Methods under test (6 total):**
- 3 MLFFs: MACE-OFF24(M), SO3LR, AI2BMD
- 2 classical baselines: AMBER ff19SB, CHARMM36m
- 1 non-MD comparator: BioEmu (free ensemble generator; bridges to Gamma)
- 1 NMR-aware baseline: Garnet (March 2026 arXiv; mandatory per scopeadv review --
  GNN-parameterized classical FF trained on NMR J-couplings from our exact benchmark
  proteins)

**Proteins (7 MVP):**

| Protein | PDB | Residues | T (K) | pH | S2 Data | Shifts | J-couplings | SAXS |
|---------|-----|----------|-------|----|---------|--------|-------------|------|
| Ubiquitin | 1UBQ | 76 | 300 | 6.6 | Yes (extensive) | Yes | Yes | No |
| GB3 | 2OED | 56 | 300 | 6.5 | Yes (extensive) | Yes | Yes | No |
| HEWL | 1IEE | 129 | **308** | **3.8** | Yes | Yes | Yes | Yes (SASBDB) |
| BPTI | 5PTI | 58 | **308** | **4.6** | Yes (~55 NH) | Yes | Yes | No |
| Barnase | 1BNR | 110 | 300 | 6.5 | Yes (~95 NH + methyl) | Yes | No | No |
| T4 Lysozyme | 107L | 164 | **310** | **5.5** | Yes | Yes | No | No |
| Crambin | 1CRN | 46 | 300 | 7.0 | No | Minimal | No | No |

**Critical modifications incorporated from reviews:**

1. **Temperature matching (bioval, Critical):** Simulate HEWL at 308 K, BPTI at 308 K,
   T4 lysozyme at 310 K. Ubiquitin, GB3, barnase at 300 K. Crambin at 300 K.

2. **pH-appropriate protonation (bioval, Critical):** Use PropKa 3.5 or H++ server at
   experimental pH for each protein. HEWL at pH 3.8 (verify Glu35/Asp52 protonation).
   BPTI at pH 4.6 (check all Asp). T4 lysozyme at pH 5.5. NOT PDBFixer default pH 7.0.

3. **iRED method for S2 (bioval, Major):** Adopt iRED (CPPTRAJ `ired` command) as
   primary S2 computation method. Direct Lipari-Szabo fitting as secondary cross-check.

4. **Increased S2 replicas (bioval, Major):** N=15 replicas (up from 10) for the 6
   proteins with S2 data (ubiquitin, GB3, HEWL, BPTI, barnase, T4 lysozyme). Per-replica
   length: 20 ns (small proteins) to 30 ns (large proteins), following Smith et al. (2024)
   5x tumbling correlation time requirement.

5. **NPT for production (bioval, Major):** Switch to NPT for production runs. MACE-OFF24
   was validated in NPT (Kovacs et al., JACS 2025). NPT is required for fair SAXS
   comparison (Rg sensitive to volume equilibration).

6. **Updated Karplus parameters (bioval, Minor):** Use Bax (2015) parameters as primary;
   Vuister & Bax (1993) as secondary for literature comparison.

7. **SHIFTX2 as primary shift predictor (bioval, Minor):** Lower prediction errors
   (13Cα RMSD 0.44 ppm vs SPARTA+ 0.94 ppm). SPARTA+ as secondary.

8. **Crambin scope reduction (bioval, Minor):** 5 ns stability check only. No full 50 ns
   production or S2 replicas. Redirect ~5,000 GPU-hrs to S2 replicas for data-rich
   proteins.

9. **Garnet as mandatory baseline (scopeadv, Major):** Bridges classical and ML
   paradigms. Trained on NMR data from our benchmark proteins. ~120 GPU-hrs additional.

10. **AMBER ff14SB as additional baseline (joint critique, Major):** Disentangles
    BioEmu-specific errors from inherited force field biases. Essential for the
    combined paper's bias chain analysis.

### Statistical Framework (Post-Review)

**Modifications from evalstat critique:**

1. **Per-residue cluster bootstrap replaces protein-level expansion.** Stay at N=7
   proteins (not evalstat's recommended 12-15), but use per-residue statistics
   (420-560 residues across 7 proteins) with cluster bootstrap (Davison & Hinkley, 1997)
   accounting for within-protein correlation. This provides substantially more
   statistical power than N=7 proteins suggest, at zero additional GPU cost.
   (Resolution: scopeadv sided with this approach over brute-force protein expansion.)

2. **Bayesian signed-rank test (Benavoli et al., JMLR 2017)** supplements Friedman/
   Nemenyi. Reports posterior probability of superiority for each pairwise comparison,
   not just p-values. Distinguishes "method A is better" from "we cannot tell."

3. **Multi-observable integration:** Per-observable rankings remain primary (no forced
   aggregation). Chi-squared reduced (Lindorff-Larsen, 2012) as secondary integration
   metric. Robust Rank Aggregation (Kolde et al., Bioinformatics 2012) as exploratory.
   Pre-registered: "No single aggregate score determines the overall ranking."

4. **Effect size quantification:** Cliff's delta with BCa bootstrap CI for each
   pairwise comparison. TOST equivalence testing (alpha=0.05, equivalence margin
   delta=0.1 for normalized metrics) to distinguish "method A equals B" from "we
   can't detect a difference."

5. **Pre-registration on OSF (before any simulations):**
   - Primary metrics: per-observable rankings (S2 R², shift RMSD, J-coupling RMSD,
     SAXS χ²)
   - Statistical tests: Friedman omnibus + Bayesian signed-rank pairwise
   - Convergence criterion: ICC(2,k) > 0.80 (raised from 0.70 per evalstat)
   - Multi-observable integration: chi²_red secondary, no forced aggregation
   - Analysis locked; sensitivity analyses declared exploratory

6. **Back-calculation uncertainty propagation:** Compute the "indistinguishability
   zone" where method differences are smaller than back-calculation noise (SPARTA+
   13Cα RMSD 1.09 ppm). Report methods as "indistinguishable within back-calculation
   uncertainty" when differences fall within this zone.

7. **Negative result decision tree:**
   - If all MLFFs match classical FFs → "MLFFs achieve classical accuracy" (positive)
   - If all MLFFs underperform classical FFs → "The MLFF reality gap" (high-impact)
   - If MLFFs and classical FFs are indistinguishable within back-calculation noise →
     "Back-calculation uncertainty limits benchmark resolution" (methods contribution)
   - If MLFFs diverge (some good, some bad) → "Heterogeneous MLFF landscape" (most likely)

8. **Missing ablations added (zero-compute):** Back-calculation tool sensitivity
   (SHIFTX2 vs SPARTA+), Karplus parameter sensitivity (Bax 2015 vs Vuister 1993),
   water model g(r) quality check.

### Compute Budget (Revised)

| Component | GPU-hrs | Notes |
|-----------|---------|-------|
| Phase 1: Stability screening (1 ns × 7 × 8 methods) | 800 | Includes Garnet, ff14SB |
| Phase 2: Production NPT (50 ns × 7 × 8) | 44,800 | NPT, temperature-matched |
| Phase 3: S2 replicas (15 × 20-30 ns × 6 proteins × 8) | 43,200 | Increased from original |
| Phase 4: BioEmu ensembles (7 proteins) | 200 | Trivial |
| Phase 5: Back-calculation + analysis | 200 | CPU-dominated |
| Contingency (20%) | 17,840 | Failed runs, debugging |
| **Total** | **~107,000** | Up from 88,400 |

**Timeline:** 14-16 weeks (extended from 12-14 due to increased S2 replicas and
additional baselines). Critical path: Phase 2 production runs (6-8 weeks with
~25-30 dedicated H200 GPUs).

### Kill Criteria

1. If ≥2 of 3 MLFFs fail to sustain stable 30 ns protein trajectories by **Week 2**
   → pivot to reduced scope (2 MLFFs, 5 proteins)
2. If AI2BMD integration takes >2 weeks → replace with AceFF-2.0 (trigger at end of
   **Week 1**, not Week 2 per bioval recommendation)
3. If all 8 methods produce S2 R² within back-calculation uncertainty (ICC < 0.50) for
   ≥5 of 7 proteins → pivot to "benchmark resolution" paper (the back-calculation noise
   is the finding)

---

## Part II: Gamma -- Conformational Ensembles Predict Protein Function

### Final Scope (Post-Review)

**Claim:** Wildtype conformational ensemble properties, captured by BioEmu, predict
mutation fitness effects across diverse ProteinGym assays, with the strongest signal
for binding and catalysis -- demonstrating that protein dynamics encode functional
information beyond what sequence alone captures.

**Modifications incorporated from reviews:**

1. **Scope reduction (scopeadv, Major):** Reduce from 200 to 150 proteins. Defer
   Tier 2 variant-specific sampling (1,700 GPU-hrs, 56% of compute) to post-
   publication follow-up. Focus on wildtype ensembles for the initial paper.

2. **Feature separation by backbone robustness (mlffeng, Major):** Split 15 features
   into "backbone-robust" (8: RMSF, B-factor variance, SS propensity, S2, Rg,
   asphericity, PCA amplitudes, inter-domain distance) and "side-chain-dependent"
   (5: SASA, H-bond persistence, contact frequency, cryptic pocket occupancy, surface
   flexibility). Run ML pipeline on each set independently. If backbone-robust features
   alone carry the signal, the paper avoids the side-chain reconstruction confound.

3. **Convergence pilot (mlffeng, Major):** Run convergence analysis on 5 proteins
   using 500, 1,000, 2,000, 5,000, 10,000 BioEmu samples. Compute CV for each feature
   across bootstrap resamples. Publish convergence profiles in supplementary. For MI:
   use multivariate Gaussian approximation (Hacisuleyman & Erman, 2024).

4. **Increase cryptic pocket evaluation (mlffeng, Minor):** From 20 to all 2,000
   conformations. Trivial compute cost.

5. **Replace kurtosis with bimodality coefficient (mlffeng, Minor):** More robust
   to sample size.

6. **Stability circularity control (mlffeng + joint critique, Major):** For stability
   assays, regress out BioEmu's direct ddG predictions before evaluating RMSF-fitness
   correlation. If RMSF predicts fitness even after controlling for BioEmu ddG, the
   dynamics signal is genuine.

7. **Acknowledge AMBER ff14SB bias explicitly (mlffeng, Major):** State in the paper
   that BioEmu ensembles approximate AMBER ff14SB equilibrium distributions. Elevate
   Alpha-M integration from supplementary to co-primary analysis.

8. **Recalibrate success threshold (scopeadv, Moderate):** Define success as additive
   value over ESM2-650M (not ESMDance, which is below GEMME and TranceptEVE).
   Win rate >55% against the top-5 ProteinGym baseline on binding/catalysis assays.

9. **Generate AMBER ff19SB ensembles independently (joint critique):** For the 8
   overlap proteins, run short (50 ns) AMBER ff19SB MD simulations (~50 GPU-hrs) during
   Gamma Weeks 3-5. This decouples Gamma's critical path from Alpha-M and provides a
   "BioEmu vs. classical MD" fitness comparison before MLFF data arrives.

10. **Add distogram/ICed-ENM/PEGASUS as baselines (scopeadv, Minor):** These occupy
    adjacent conceptual territory and should be compared.

### Ensemble Features (Revised: 15 → 13 primary + 2 secondary)

**Backbone-robust (primary, 8 features):**
1. RMSF (per-residue Cα fluctuation)
2. B-factor variance (ensemble B-factor spread)
3. Secondary structure propensity (DSSP across ensemble)
4. S2 order parameter (backbone N-H vector autocorrelation)
5. Radius of gyration (Rg)
6. Asphericity (gyration tensor)
7. PCA amplitude ratios (PC1-3 explained variance)
8. Inter-domain distance distributions

**Side-chain-dependent (secondary, reported separately):**
9. SASA distribution (report both Cα-SASA and HPacker-reconstructed)
10. Contact frequency (Cα-Cα at 8 Å)
11. Mutual information (Gaussian approximation for convergence)
12. Bimodality coefficient (replaces kurtosis)
13. Cryptic pocket occupancy (all 2,000 conformations, PocketMiner)

**Renamed:** H-bond persistence → "Secondary structure hydrogen bond persistence"
(backbone H-bonds only, per mlffeng recommendation).

**Surface flexibility index dropped** (composite of SASA + RMSF; redundant if SASA
reported separately).

### ML Pipeline (4-stage, unchanged)

1. **Stage 1:** Raw RMSF-fitness correlation (kill criterion at June 30)
2. **Stage 2:** MLP/XGBoost baseline (SHAP feature importance)
3. **Stage 3:** GATv2 GNN with dynamics-informed edges (BioEmu contact frequency)
4. **Stage 4:** Ensemble-augmented baselines (ESM2 + RMSF, AlphaMissense + RMSF)

### Compute Budget (Revised)

| Component | GPU-hrs | Notes |
|-----------|---------|-------|
| Tier 1 wildtype ensembles (150 proteins × 2,000 conf) | 215 | Increased from 143 |
| Convergence pilot (5 proteins × 10,000 conf) | 12 | New |
| AMBER ff19SB comparison (8 overlap proteins × 50 ns) | 50 | New, decouples from Alpha-M |
| ML training + ablation | 1,500 | Unchanged |
| Contingency (20%) | 355 | |
| **Total** | **~2,130** | Down from 3,037 (variant sampling deferred) |

**Variant-specific sampling (deferred):** 1,700 GPU-hrs allocated as post-publication
follow-up if wildtype hypothesis is confirmed.

### Timeline (Revised: 14 weeks)

| Phase | Weeks | Activity |
|-------|-------|----------|
| 1 | 1-3 | Ensemble generation (Tier 1) + convergence pilot |
| 2 | 2-4 | Feature extraction (backbone-robust primary) |
| 3 | 3-5 | AMBER ff19SB comparisons for 8 overlap proteins |
| 4 | 4-7 | ML pipeline Stages 1-3 |
| 5 | 7-9 | Ablation, stratification, feature importance |
| 6 | 9-11 | Integration with Alpha-M data (when available) |
| 7 | 11-14 | Figures + writing |

### Kill Criteria

1. **June 30:** If RMSF ρ < 0.1 across >50% of Tier 1 proteins → pivot to variant-
   specific ensembles or alternative generators (AlphaFlow, Boltz-2)
2. **July 31:** If win rate <45% against any top-5 baseline on binding/catalysis →
   reframe as negative result paper
3. **Monthly scooping scan:** Check bioRxiv/arXiv for BioEmu+DMS fitness papers.
   If detected, accelerate preprint timeline.

---

## Part III: The Combined Paper -- From Accurate Ensembles to Biological Function

### Recommendation: Combined Paper as Primary Target

**The joint integration critique unanimously recommends Option A (combined paper) as
the primary target, with standalone papers as pre-planned fallback.**

**Reasoning:**
1. The integration claim ("validated ensembles predict function better") is the paper's
   scientific moat -- neither standalone component reaches NCS alone
2. Risk is managed by decoupled critical paths and pre-planned fallback
3. The decision can be deferred to September 30 with no additional cost
4. All outcomes (positive, negative, partial integration) are publishable

### Integration Design

**The 8-Protein Overlap (refined to 6 primary + 2 exploratory):**

Primary integration set (6 folded, well-characterized proteins):

| Protein | Alpha-M Metric | Gamma Metric | Integration |
|---------|---------------|-------------|-------------|
| Ubiquitin | S2 R², shift RMSD, J RMSD | Stability fitness ρ | Gold standard |
| GB3 | S2 R², shift RMSD, J RMSD, 36 RDC sets | Stability fitness ρ | Richest NMR |
| T4 Lysozyme | S2 R², shift RMSD | Activity fitness ρ | Enzyme dynamics |
| Barnase | S2 R², methyl S2 | Activity fitness ρ | Catalysis |
| p53 | Shift RMSD | Binding fitness ρ | Cancer relevance |
| SNase | S2 R², shift RMSD, J RMSD | Stability fitness ρ | Classic folding |

Exploratory (reported separately with caveats):

| Protein | Concern | Integration |
|---------|---------|-------------|
| HIV Protease | Dimer complexity, MLFF may not produce fair comparison | Drug resistance |
| Alpha-synuclein | IDP, requires different analysis (Rg/PRE, not S2) | Aggregation |

### Statistical Framework for Integration

1. **Primary test:** Within-protein Spearman correlation between S2 R² (validation
   quality) and fitness prediction ρ (prediction quality) across 8 generators
   (6 original + Garnet + ff14SB), for each protein. Yields 6 correlation values.
   One-sample Wilcoxon signed-rank test on the 6 correlations against zero.

2. **Secondary test:** Multilevel modeling treating protein-generator pairs as nested
   data (N=48, generators nested within proteins). Mixed-effects regression:
   fitness_rho ~ S2_R2 + (1|protein). This properly accounts for non-independence.

3. **Tertiary test:** Bayesian correlation with informative prior (expected rho =
   0.4-0.6 based on the chain: S2 → RMSF → features → fitness). Report Bayes factor
   and credible interval.

4. **Pre-registered on OSF:** Integration metric, proteins, generators, significance
   threshold, decision rule for combined vs separate.

### The Killer Figure: Dynamics Quality-Function Plane

**Panel A:** Scatter plot. X = mean S2 R² across 6 primary overlap proteins.
Y = mean Spearman ρ on DMS fitness across same proteins. Points: 8 generators
(MACE-OFF24, SO3LR, AI2BMD, AMBER ff19SB, CHARMM36m, BioEmu, Garnet, ff14SB).
Error bars: 95% CI from bootstrap. Trend line with R² and p-value. Quadrant
annotations: "Accurate AND predictive" (top-right), "Predictive but inaccurate"
(top-left, surprising), "Accurate but not predictive" (bottom-right), "Neither"
(bottom-left).

**Panel B:** Per-protein waterfall. X = 6 proteins. Y = Δ Spearman when switching
from least to most accurate generator. Bars colored by assay type.

### Force Field Bias Chain Controls

1. **Stability circularity control:** Regress out BioEmu ddG predictions before
   evaluating RMSF-fitness correlation for stability assays.
2. **ff14SB baseline inclusion:** Disentangles BioEmu-specific error from inherited FF
   bias. If BioEmu S2 ≈ ff14SB S2 < ff19SB S2 < experiment → BioEmu is faithful to
   training data (not a BioEmu failure).
3. **Assay-type stratification:** Report integration results separately for stability
   (where circularity exists) and binding/catalysis (where it does not).

### Timeline Alignment (Decoupled)

```
Week:  1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  16  17  18
Alpha: [setup][---production 50ns---][S2 replicas][backcalc][     writing     ]
Gamma: [ensembles][features][AMBER comp][---ML pipeline---][ablation][writing]
Integ:                      [BioEmu v AMBER]              [full 8-gen integration]
Paper:                                                              [combined ms]
```

Gamma generates AMBER ff19SB comparisons independently (Weeks 3-5, 50 GPU-hrs).
When Alpha-M back-calculation data arrives (Week 12), full 8-generator integration
replaces the 2-generator preliminary. Combined manuscript: Weeks 15-18.

### Combined vs Separate Decision Points

| Date | Checkpoint | Criterion | Action if Failed |
|------|-----------|-----------|-----------------|
| June 30 | Gamma kill | RMSF ρ < 0.1 for >50% proteins | Pivot Gamma to variant-specific |
| Aug 15 | Alpha-M progress | ≥5 of 7 proteins with completed production runs | Reduce Alpha-M scope |
| Sep 30 | Integration | 8-protein integration ρ < 0.3 with p > 0.2 | Switch to separate papers |
| Oct 15 | Combined draft | Reviewable manuscript draft exists | Switch to separate papers |

---

## Part IV: Delta -- PerturbMark

### Final Scope (Post-Review)

**Claim:** PerturbMark is the first neutral, calibrated, cross-context benchmark for
chemical perturbation prediction, evaluating 10+ methods on Tahoe-100M across 4
difficulty tiers with standardized metrics and mandatory baselines, resolving whether
deep learning adds value beyond linear models for perturbation response prediction.

**Modifications incorporated from reviews:**

1. **WMSE as sole primary metric (evalstat, Major):** Designate WMSE as the single
   primary metric. Add Spearman ρ on top-k DEGs as the second primary (non-redundant:
   one measures absolute error magnitude, one measures rank fidelity). Relegate
   R²_w(delta) to secondary.

2. **Benjamini-Yekutieli correction (evalstat, Major):** Replace BH-FDR with
   three-tiered correction: (1) BY procedure as primary (controls FDR under arbitrary
   dependency), (2) BH-FDR as sensitivity analysis, (3) Westfall-Young permutation-
   based FDR to estimate FDR under actual dependency structure.

3. **Random cell-line holdout sensitivity analysis (evalstat, Major):** Add a random
   5-fold cell-line holdout (ignoring organ) parallel to the organ-based holdout.
   Compare rankings via Kendall's tau > 0.70. Include tissue covariate in mixed-effects
   model.

4. **Wilcoxon power analysis (evalstat, Major):** Redo power analysis using Wilcoxon
   signed-rank (not paired t-test). Pre-specify minimum 20 conditions per MOA stratum
   at Tier 3. Pooled Tier 3 MOA-stratified analysis is exploratory, not confirmatory.

5. **Cell village confound acknowledgment (evalstat, Minor):** Add Control 5:
   cross-dataset validation on Replogle K562 and Norman K562 (non-village design).
   Report Kendall's tau between Tahoe-100M and Replogle/Norman rankings as village-
   independence check.

6. **Dose-level leakage prevention (evalstat, Minor):** Group all doses of the same
   compound together in train/test splits. Never split doses of the same compound
   across partitions.

7. **Timeline extension to 12 weeks (evalstat + scopeadv):** Move preprint target
   from July 15 to **August 15, 2026**. A flawed benchmark is worse than no benchmark.
   12 weeks allows proper statistical validation.

8. **Add scDFM to method catalog (scopeadv, Minor):** Accepted at ICLR 2026. Flow
   matching for perturbation prediction.

9. **Revise narrative framing (scopeadv, Major):** Change from "Resolving the
   Perturbation Prediction Crisis" to a question-driven title: **"When Does Deep
   Learning Help? A Calibrated Cross-Context Benchmark for Perturbation Prediction."**
   Let data speak rather than overclaiming resolution.

10. **Expand differentiation table (scopeadv, Minor):** 4-column comparison
    (PerturbMark vs scPerturBench vs scPPDM vs Cole et al.) showing PerturbMark as the
    only entry with all 7 key features.

11. **Feature Importance module (ensfunc, Major):** Add a "what drives predictions?"
    analysis. Test whether specific feature types (gene programs, pathway activities,
    embedding components) predict perturbation effects. Use CKA (centered kernel
    alignment) to compare model representations. This addresses the feature-vs-model
    blind spot.

12. **Distributional evaluation (ensfunc, Major):** Elevate cell-level distributional
    metrics from supplementary to co-primary for Tier 0-1. Biological replicates within
    conditions are cellular ensembles -- pseudobulk aggregation discards distributional
    information (Mixscale, Nat Cell Biol 2025; MrVI, Nat Methods 2025).

13. **Leaderboard anti-gaming measures (ensfunc, Minor):** Time-stamped submissions,
    code + environment submission requirement, hidden holdout tier (subset of Tier 3
    released only for final evaluation), data hash verification.

### Methods (Updated Catalog)

**Tier 1 (Must evaluate, fully supported):**
1. GEARS (NeurIPS 2022)
2. scGPT (Nature Methods 2024)
3. scFoundation (Nature Methods 2024)
4. CPA (Molecular Systems Biology 2023)
5. scPPDM (arXiv 2025, ICLR 2026)
6. scDFM (ICLR 2026) -- NEW

**Tier 2 (Evaluate if available):**
7. AlphaCell (bioRxiv March 2026)
8. X-Cell
9. AetherCell
10. pertTF

**Mandatory baselines (5):**
1. Mean expression (per cell line)
2. Mean + additive perturbation effect
3. CRISPR-informed mean (Wong et al., 2025)
4. Per-gene linear model (cell-line features)
5. Per-gene ridge regression (cell-line + drug features)

### Metric Suite (Revised)

| Metric | Role | Type |
|--------|------|------|
| WMSE | **Primary 1** | Error magnitude (DEG-weighted) |
| Spearman ρ on top-k DEGs | **Primary 2** | Rank fidelity |
| R²_w(delta) | Secondary | Variance explained |
| MSE | Secondary (with DRF calibration warning) | Backward compatibility |
| PDS | Secondary | Distribution distance |
| DEG-F1 | Secondary | Classification |
| DRF | Meta-metric | Metric quality validation |

### Compute Budget (Unchanged)

~1,070 GPU-hrs. This is the least compute-intensive project in the portfolio.

### Timeline (Revised: 12 weeks)

| Phase | Weeks | Activity |
|-------|-------|----------|
| 1 | 1-2 | Tahoe-100M preprocessing, split construction |
| 2 | 3-4 | Baseline implementation + validation |
| 3 | 3-6 | DL method evaluation (parallel with baselines) |
| 4 | 6-8 | Tier 0-3 analysis, batch controls |
| 5 | 8-10 | Feature importance, distributional evaluation |
| 6 | 10-12 | Figures, writing, preprint preparation |

**Preprint:** bioRxiv **August 15, 2026**
**Nature Methods submission:** September 1, 2026

### Kill Criteria

1. If scPerturBench publishes a Tahoe-100M follow-up before our preprint → reassess
   differentiation (check monthly via bioRxiv/PubMed alerts)
2. If Tahoe-100M data proves too noisy for Tier 3 analysis (baseline performance at
   random chance) → reduce to Tier 0-2 and reframe

---

## Part V: Risk Registry (Final, All Projects)

### Alpha-M Risks

| Risk | Probability | Impact | Mitigation | Trigger |
|------|------------|--------|------------|---------|
| MLFF instability (crashes, NaN) | 30% | High | Phase 1 screening, AceFF-2.0 fallback | Week 2 |
| Compute timeline overrun | 40% | Medium | Prioritize 5 core proteins, defer 2 | Week 8 |
| AI2BMD integration failure | 25% | Medium | AceFF-2.0 replacement (Week 1 trigger) | Week 1 |
| All methods indistinguishable | 20% | Low | "Benchmark resolution" paper | Week 12 |
| SO3LR JAX-MD thermostat issue | 15% | Medium | Ala dipeptide Ramachandran sanity check | Week 1 |

### Gamma Risks

| Risk | Probability | Impact | Mitigation | Trigger |
|------|------------|--------|------------|---------|
| BioEmu RMSF shows no fitness signal | 20% | High | Kill criterion June 30, pivot to variant-specific | June 30 |
| Scooped by Microsoft/Marks Lab | 25-35% (6 mo) | High | Preprint ASAP, Alpha-M integration as moat | Monthly scan |
| Overfitting (20 features, 150 proteins) | 30% | Medium | Nested leave-protein-out CV, L1, permutation tests | Stage 2 |
| BioEmu fails Alpha-M validation | 30% | Low-Medium | Reframe as "topology matters more than accuracy" | Week 12 |
| Allosteric mutation failure mode | 40% | Low | Pre-register as known limitation, stratify by mutation type | Stage 3 |

### Delta Risks

| Risk | Probability | Impact | Mitigation | Trigger |
|------|------------|--------|------------|---------|
| scPerturBench Tahoe-100M follow-up | 20% | High | Monthly scan, differentiation on metrics/tiers | Monthly |
| DL method reproducibility failures | 35% | Medium | 4-week buffer in 12-week timeline | Week 4 |
| Tahoe-100M batch effects dominate | 25% | Medium | 5 batch controls including village check | Week 4 |
| Insufficient Tier 3 power | 30% | Low | Pre-register Tier 3 MOA as exploratory | Week 6 |
| Cell village confound | 20% | Low | Cross-dataset validation on Replogle/Norman | Week 8 |

### Portfolio-Level Risk

- **Probability all three fail to publish:** <1% (scopeadv estimate 0.9%)
- **Probability of at least one NCS paper:** ~50-60% (combined paper)
- **Probability of at least one NatMethods paper:** ~80% (Delta or standalone Alpha-M)
- **Expected publications:** 2-3 papers at high-quality venues

---

## Part VI: Publication Strategy

### Primary Path (Combined + Delta)

```
Timeline:    May    Jun    Jul    Aug    Sep    Oct    Nov    Dec
Delta:       [====execution====][preprint][NatMeth sub]
Alpha-M:     [=====production======][S2 replicas][backcalc][writing]
Gamma:       [ensembles][features][ML pipeline][ablation][writing]
Combined:                                           [integration][combined ms]
                                                                 [preprint][NCS sub]
```

| Paper | Preprint | Submission | Venue |
|-------|----------|-----------|-------|
| Delta (PerturbMark) | August 15 | September 1 | Nature Methods |
| Combined (Gamma+Alpha-M) | November 15 | December 1 | Nature Comp Sci |

### Fallback Path (Separate Papers)

Triggered at September 30 if integration data does not support combined paper.

| Paper | Preprint | Submission | Venue |
|-------|----------|-----------|-------|
| Delta (PerturbMark) | August 15 | September 1 | Nature Methods |
| Alpha-M (standalone) | November 1 | November 15 | Nature Methods / NCS |
| Gamma (standalone) | November 15 | December 1 | NCS / Genome Research |

### Pre-Registration

All three projects pre-register on OSF before execution begins:
- Alpha-M: primary metrics, statistical tests, convergence criteria, protein set
- Gamma: kill criteria, features, CV strategy, success threshold
- Delta: primary metrics (WMSE + Spearman-top-k), correction procedure (BY),
  effect size threshold (5% WMSE reduction), Tier 3 MOA as exploratory

---

## Part VII: Compute Summary

| Project | GPU-hrs | % of Total | Timeline |
|---------|---------|-----------|----------|
| Alpha-M | ~107,000 | 96.2% | 14-16 weeks |
| Gamma (excl. Alpha-M overlap) | ~2,130 | 1.9% | 14 weeks |
| Delta | ~1,070 | 1.0% | 12 weeks |
| Alpha-M+Gamma integration overhead | ~50 | <0.1% | Weeks 3-5 (Gamma) |
| Contingency (included in per-project) | ~18,200 | -- | -- |
| **Total** | **~110,250** | 100% | 18 weeks max |

Alpha-M dominates compute. Delta and Gamma are essentially "free" in comparison.
This reinforces the portfolio strategy: Delta and Gamma can execute even if Alpha-M
faces compute constraints.

---

## Part VIII: Recommendations for CohortArchitect

### Input for ReviewCohort Design

The CohortArchitect should design a ReviewCohort that provides:

1. **External sanity check on the combined paper narrative.** The joint integration
   critique identified the "Dynamics Quality-Function Plane" as the killer figure --
   a ReviewCohort should stress-test whether this figure survives scrutiny.

2. **Mock Nature Computational Science review.** Assign 3-4 ReviewCohort agents to
   write mock reviews as if they were NCS Reviewer 1, 2, 3, and the editor. The
   5 reviewer attack vectors identified in the joint critique should be the starting
   point.

3. **Delta competitive intelligence update.** By the time ReviewCohort runs, the
   Delta competitive landscape may have shifted. A fresh scan is needed.

4. **Scope arbitration.** The tension between evalstat (expand to 12-15 proteins) and
   scopeadv (stay at 7 with per-residue bootstrap) was resolved in favor of scopeadv,
   but a ReviewCohort could independently assess this.

5. **Title and framing workshop.** The joint critique noted that current Gamma titles
   are weak. scopeadv provided alternatives but a ReviewCohort could refine further.

### What This Cohort Produced

| Output | Lines | Citations | Location |
|--------|-------|-----------|----------|
| 6 Round 1 research notes | ~5,426 | ~165 | `output/research/` |
| 6 Round 2 proposals | ~6,560 | ~174 | `output/proposals/` |
| 9 Round 3 critiques | ~7,900 | ~260 | `output/critiques/` |
| 1 joint integration critique | ~1,053 | 32 | `output/critiques/` |
| 3 round syntheses | ~780 | -- | `output/roundtables/` |
| 2 round directives | ~106 | -- | `output/directives/` |
| **This final proposal set** | ~680 | -- | `output/roundtables/` |
| **Total** | **~22,500** | **~630** | -- |

### Bottom Line

The Cohort 2 Deep Divers have produced three execution-ready proposals that have
survived hostile cross-review. The combined Gamma+Alpha-M paper is the highest-ceiling
contribution -- a genuinely novel paper connecting force field validation quality to
downstream functional prediction quality, filling a gap no group in the world is
currently addressing. Delta (PerturbMark) is the safest bet -- a well-differentiated
benchmark paper targeting Nature Methods with a 12-week timeline. The portfolio is
designed for resilience: even in the worst case, at least 2 papers publish at
high-quality venues.

The projects are ready to execute. The next step is implementation.
