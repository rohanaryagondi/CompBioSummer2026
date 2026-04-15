---
agent: orch
round: 1
date: 2026-04-14
type: roundtable-synthesis
---

# Round 1 Synthesis: Deep Research Results Across 6 Specialists

## Overview

Six Cohort2 Deep Diver specialists completed Round 1 deep research, producing 5,426
lines of technical analysis across all three projects. Each specialist conducted
extensive internet research (40-60 tool calls per agent) and wrote research notes
with 25-30 citations each. This synthesis integrates their findings, identifies
integration points between Alpha-M and Gamma, flags critical risks and feasibility
concerns, and assigns Round 2 proposal topics.

**Bottom line:** All three projects remain feasible and differentiated as of April 2026.
Alpha-M has the widest competitive moat, Gamma has the strongest scientific narrative,
and Delta has the most urgent timeline. The combined Gamma+Alpha-M paper is strengthened
by an 8-protein overlap between NMR dynamics data and ProteinGym DMS assays.

---

## Key Findings by Project

### Alpha-M (MLFF Biomolecular Crash Test)

**mlffeng findings:**
- **4 MLFFs are production-ready** for systematic benchmarking: MACE-OFF24(M), SO3LR,
  AI2BMD, and AceFF-2.0. Allegro is Tier 2 (via LAMMPS only).
- **ANI-2x is DISQUALIFIED** -- fails to produce stable liquid water (amorphous ice
  structure). This narrows the field but is itself a publishable finding.
- **LiTEN-FF and GEMS are not ready** -- LiTEN-FF lacks OpenMM integration, GEMS is
  partially closed-source. UMA is materials-focused, not protein-ready.
- **Simulation protocol:** 1 fs timestep, Langevin thermostat at 300K, NVT production.
  S2 order parameters require 10-20 replicas of 20 ns each (not one long trajectory).
- **MVP compute:** 7 proteins × 3 MLFFs × 50 ns = ~51,000 GPU-hrs without S2 replicas,
  ~137,000 with S2 replicas on H200.
- **Full benchmark:** 15 proteins × 5 MLFFs × 100 ns + S2 replicas ≈ 706,000 GPU-hrs.
- **MACE-OFF speed on H200:** ~0.39-0.40 ns/day for crambin (~18K atoms). SO3LR:
  ~2.6 ns/day at 10K atoms on H100.

**bioval findings:**
- **25 candidate proteins curated** with PDB IDs, BMRB entries, and available NMR data.
  Final recommended set of **15 proteins** in 3 tiers:
  - Tier A (6 core): ubiquitin (1UBQ), GB3 (2OED), HEWL (1IEE), BPTI (5PTI),
    barnase (1BNR), T4 lysozyme (107L)
  - Tier B (5 extended): RNase H (2RN2), Cyclophilin A (3K0N), crambin (1CRN),
    chignolin (5AWL), SH3 (1SHF)
  - Tier C (4 IDPs/integration): alpha-synuclein, ACTR, p53, Abeta40
- **8 proteins overlap** with ProteinGym DMS assays (ubiquitin, GB1/GB3, T4 lysozyme,
  barnase, HIV protease, alpha-synuclein, p53, SNase) -- critical for Gamma integration.
- **Pass/fail thresholds:** S2 R² ≥ 0.50, 3JHNHα RMSD ≤ 1.0 Hz, SAXS χ² ≤ 5.0
  (calibrated against AMBER ff19SB R²=0.62, CHARMM36m R²=0.51).
- **SAXS reference:** HEWL has SASBDB consensus data (SASDUE4) with 2024 round-robin benchmark.
- GB3 has **36 RDC sets measured in 5 alignment media** -- exceptional data richness.

**evalstat findings for Alpha-M:**
- Friedman/Nemenyi framework for K=8 methods across N=15 proteins.
- Critical difference CD = 2.71 ranks -- 15 proteins provide ~80% power only for
  large effects. **Recommend expanding to 20 proteins if compute allows.**
- Back-calculation uncertainty (SPARTA+ ~1.1 ppm for 13Cα) must be propagated through
  significance testing.
- Require 3-5 simulation replicates with ICC > 0.7 for convergence verification.

**scopeadv findings for Alpha-M:**
- **Widest competitive moat:** 12-24+ months. No direct competitor exists.
- **Scoop probability in next 6 months: <10%.** MACE group (Cambridge) is most
  capable but focused on method development, not benchmark curation.
- **Kill criterion:** If 2 of 3 primary MLFFs fail to sustain stable 30 ns protein
  trajectories by May 30, 2026, pivot to reduced scope.

### Gamma (Dynamics-to-Function Mapping)

**ensfunc findings:**
- **Gap confirmed open:** No paper connects explicit BioEmu ensembles to ProteinGym
  DMS fitness prediction as of April 2026. Eight papers citing BioEmu identified;
  none attempts this connection.
- **BioEmu input format:** Accepts mutant sequences directly (no special mutation API).
  Pass mutant amino acid sequence → get mutant-specific ensemble. No conditioning on
  wildtype reference structure.
- **BioEmu limitations confirmed:** Aryal et al. (IJMS 2025) finding stands -- BioEmu
  cannot differentiate driver from passenger mutations at the conformational distribution
  level. But this applies to *variant-specific* ensembles, not to the wildtype hypothesis.
- **Wildtype ensemble hypothesis STRONGLY SUPPORTED:** Mutational robustness paper
  (bioRxiv March 2026) shows median Spearman ρ ≈ 0.6 between positional dynamics (RMSF)
  and mutation sensitivity across ~2,000 proteins. This holds even for de novo designed
  proteins, confirming a biophysical (not evolutionary) effect.
- **ProteinGym state:** Top methods score Spearman ~0.47-0.52. Dynamics features are
  **entirely absent** from the leaderboard -- this is our entry point.
- **20 ensemble features cataloged** across per-residue (RMSF, B-factors, SASA
  distributions), pairwise (contact frequencies, distance distributions, correlated
  motions), and global (Rg, asphericity, PC amplitudes, pocket occupancy) categories.
- **Architecture recommendation:** Start with feature-based MLP for rapid prototyping
  and interpretability, then advance to ensemble-aware GNN for publication results.
- **Compute confirmed:** ~8,200 GPU-hrs total (wildtype ensembles: ~100-200 GPU-hrs;
  variant-specific subset: ~2,000-5,000; training + ablation: ~1,500).

**evalstat findings for Gamma:**
- Leave-protein-out CV is **mandatory** (not leave-variant-out, which inflates results).
- 187 unique UniProt IDs in ProteinGym -- detects Δ ≥ 0.05 Spearman at >80% power.
- **Severe overfitting risk:** 20 features / 187 proteins requires nested CV, L1
  regularization, and permutation tests.
- Win rate threshold: ensemble method must outperform best baseline on **>55% of proteins**.
- Stratification by 6 assay types is pre-specified: thermostability, binding,
  catalysis, growth, fluorescence, expression.
- Compute-matched comparison table required (8,200 GPU-hrs vs. minutes for sequence-only).

**scopeadv findings for Gamma:**
- **Window revised to 6-12 months** (narrowed from Cohort 1's 6-18 months).
- **Critical intelligence:** Microsoft Research is NOT pursuing BioEmu-to-DMS-fitness
  mapping. Their April 2026 blog focuses on drug design and stability.
- SeqDance/ESMDance uses implicit dynamics (complementary, not competitive).
- Kill criterion: If wildtype ensemble features show ρ < 0.1 across >50% of proteins
  by June 30, 2026, pivot to variant-specific ensembles or alternative generators.

### Delta (PerturbMark)

**pertbio findings:**
- **Tahoe-100M deep audit:** 100.6M cells, 50 cancer cell lines (47 with sufficient
  representation), 379 distinct compounds, 17,813 unique cell-line-drug conditions.
  Sparse tokenized format, raw counts, plate-matched DMSO controls. CC0 license,
  429 GB on HuggingFace.
- **18+ methods cataloged** with April 2026 availability status. 5 task-specific DL
  models, 10 foundation models, 6 linear baselines identified.
- **Metric controversy resolved** with a proposed 7-metric core suite: WMSE,
  centroid-referenced Pearson-delta, PDS, DES, DEG-F1, Dynamic Range Fraction, MMD.
  Avoids all known failure modes identified by Dibaeinia et al. and "Diversity by Design."
- **Tier 0-3 hierarchy precisely defined** with construction protocols from Tahoe-100M.
  Tier 3 (unseen perturbation + unseen cell line) is the key differentiator from
  scPerturBench.
- **10 specific gaps vs scPerturBench** identified, including: Tahoe-100M evaluation,
  Tier 3 cross-context, calibrated metrics, March 2026 models, CRISPR-informed mean
  baseline, MOA-stratified analysis.
- **Compute:** ~1,070 GPU-hrs. Timeline: 6-8 weeks to submission-ready manuscript.

**evalstat findings for Delta:**
- Primary metrics: WMSE and R²_w(delta) (calibrated). Secondary: MSE and Pearson-delta
  (with calibration warnings).
- Dynamic Range Fraction calibration with interpolated duplicate baseline.
- Benjamini-Hochberg FDR across 120 primary tests (10 methods × 4 tiers × 3 metrics).
- DL must reduce WMSE by ≥5% to be declared better (pre-specified effect size threshold).
- Batch effect controls: negative control baseline, batch-shuffled null,
  within-vs-across-batch split.

**scopeadv findings for Delta:**
- **Most crowded landscape** but specific niche remains differentiated.
- **Window: 3-6 months -- URGENT.** Massive burst of activity Feb-March 2026.
- No published work combines Tahoe-100M + cross-context tiers + calibrated metrics.
- **Kill criterion:** If scPerturBench publishes a Tahoe-100M follow-up before we
  preprint (check by July 15, 2026), reassess differentiation.

---

## Integration Points: Gamma + Alpha-M

The 8-protein overlap between bioval's curated NMR/dynamics set and ProteinGym DMS
assays is the linchpin for the combined narrative:

| Protein | NMR Data | ProteinGym DMS | Integration Value |
|---------|----------|----------------|-------------------|
| Ubiquitin (1UBQ) | S2, shifts, J-couplings, RDCs | Yes (stability) | Gold standard for both |
| GB1/GB3 (2OED) | S2, shifts, 36 RDC sets | Yes (stability) | Richest NMR data |
| T4 Lysozyme (107L) | S2, shifts | Yes (activity) | Large, diverse mutant library |
| Barnase (1BNR) | S2, methyl S2 | Yes (activity) | Enzyme catalysis assay |
| HIV Protease (2PC0) | S2, flap dynamics | Yes (activity) | Drug resistance mutations |
| alpha-Synuclein | Shifts, J-couplings, PRE, SAXS | Yes (aggregation) | IDP dynamics |
| p53 | Shifts | Yes (binding) | Cancer-relevant mutations |
| SNase (1SNO) | S2, shifts, J-couplings | Yes (stability) | Classic folding model |

**Combined narrative:** For these 8 proteins, we can:
1. **Alpha-M:** Test whether MLFFs reproduce experimental NMR observables
2. **Gamma:** Test whether wildtype ensemble features predict DMS fitness scores
3. **Integration:** Test whether MLFFs that produce more physically realistic dynamics
   (better S2 agreement) also generate ensembles that predict function better

This creates a question neither project can answer alone: "Do more physically accurate
ensemble generators produce better functional predictions?"

---

## Revised Scope and Compute Summary

| Project | MVP Compute | Full Compute | Timeline | Window | Venue |
|---------|-------------|--------------|----------|--------|-------|
| Alpha-M | ~51K GPU-hrs | ~706K GPU-hrs | 10-14 wks | 12-24+ months | Nat Comp Sci |
| Gamma | ~8,200 GPU-hrs | ~8,200 GPU-hrs | 6-8 wks | 6-12 months | Nat Comp Sci |
| Delta | ~1,070 GPU-hrs | ~2,000 GPU-hrs | 6-8 wks | 3-6 months | Nat Methods |
| **Total (MVP)** | **~60K GPU-hrs** | -- | -- | -- | -- |

**Key compute insight from mlffeng:** The S2 convergence requirement (10-20 replicas)
dramatically increases Alpha-M compute. The MVP with S2 replicas jumps from ~51K to
~137K GPU-hrs. This must be factored into timeline planning.

---

## Risk Assessment

### Critical Risks (Flagged by ≥2 Specialists)

1. **Alpha-M compute timeline** (mlffeng, evalstat, scopeadv): At 137K GPU-hrs with
   S2 replicas, Alpha-M alone consumes 6-8 weeks of focused HPC time. If any MLFF
   proves unstable, debugging adds weeks.
   - *Mitigation:* Start with 5 core proteins × 3 MLFFs, validate pipeline, then expand.

2. **BioEmu mutation sensitivity** (ensfunc, evalstat): Aryal et al. showed BioEmu
   can't differentiate driver/passenger mutations. If variant-specific ensembles carry
   no signal, we rely entirely on the wildtype hypothesis.
   - *Mitigation:* Wildtype hypothesis has strong independent support (ρ ≈ 0.6).
   - *Fallback:* Include AlphaFlow and Boltz-2 as alternative ensemble generators.

3. **Delta competitive urgency** (pertbio, scopeadv): 3-6 month window. scPerturBench
   already published in Nature Methods (Feb 2026).
   - *Mitigation:* Preprint by July 2026. Tahoe-100M + Tier 3 + calibrated metrics
     are the differentiation.

4. **Cross-engine fairness for Alpha-M** (mlffeng, bioval): Different MLFFs run on
   different engines (OpenMM-ML vs LAMMPS vs custom). Perfect fair comparison requires
   identical thermostats, integrators, and system preparation.
   - *Mitigation:* Use OpenMM-ML where possible. Document all protocol choices transparently.

5. **Overfitting in Gamma** (evalstat, ensfunc): 20 features on 187 proteins invites
   overfitting. ProteinGym's assay type heterogeneity complicates evaluation.
   - *Mitigation:* Nested leave-protein-out CV, L1 regularization, permutation tests,
     stratification by assay type.

---

## Decisions for Round 2

### Scope Decision: Alpha-M MVP

Based on mlffeng's compute analysis and scopeadv's timeline assessment, the Alpha-M MVP
for summer 2026 is:
- **7 proteins** (ubiquitin, GB3, HEWL, BPTI, barnase, crambin, T4 lysozyme)
- **3 MLFFs** (MACE-OFF24(M), SO3LR, AI2BMD) + **2 classical baselines** (AMBER ff19SB,
  CHARMM36m)
- **50 ns production** + **10 replicas × 10 ns for S2** = ~51,000-80,000 GPU-hrs
- **Stretch goal:** Expand to 15 proteins and add AceFF-2.0 if timeline allows

### Integration Decision: Gamma + Alpha-M

The 8-protein overlap enables but does not require a combined paper. The proposal set
should be designed for **separability**: each project must work as a standalone paper,
but the combined version adds a unique integrative claim. scopeadv's recommendation:
publish Delta by August, Gamma by October, combined Gamma+Alpha-M by November.

### Urgency Decision: Delta Timeline

Delta launches immediately in parallel. pertbio's 6-8 week timeline to submission-ready
manuscript means a July 2026 preprint is achievable if Round 2 proposals are tight.

---

## Round 2 Assignments

Each specialist writes a **formal proposal** using the proposal template, incorporating
Round 1 research findings and the integration decisions above.

| Agent | Proposal | Output File |
|-------|----------|-------------|
| mlffeng | Alpha-M full simulation protocol, MLFF selection, compute plan, SLURM design | `proposals/mlffeng-alpha-m-proposal-R02.md` |
| bioval | Alpha-M validation data pipeline, protein final selection, analysis protocol | `proposals/bioval-validation-proposal-R02.md` |
| ensfunc | Gamma full proposal: BioEmu pipeline, feature extraction, ML framework, evaluation | `proposals/ensfunc-gamma-proposal-R02.md` |
| pertbio | Delta full proposal: PerturbMark benchmark specification | `proposals/pertbio-delta-proposal-R02.md` |
| evalstat | Unified evaluation framework for all three projects | `proposals/evalstat-evaluation-proposal-R02.md` |
| scopeadv | Strategic recommendation: scope, timeline, publication strategy, risk mitigation | `proposals/scopeadv-strategy-proposal-R02.md` |

All proposals must include: compute budget, data sources, timeline, baselines,
evaluation plan, publication framing, risk assessment.
