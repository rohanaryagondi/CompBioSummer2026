---
agent: orch
round: 2
date: 2026-04-14
type: roundtable-synthesis
---

# Round 2 Synthesis: Proposal Integration and Cross-Review Assignment

## Overview

Six specialists produced 6,560 lines of execution-ready proposals across all three
projects. Each proposal includes specific compute budgets, timelines, statistical
frameworks, data pipelines, and publication strategies. This synthesis integrates the
proposals, identifies conflicts, drafts the combined Gamma+Alpha-M narrative, and
assigns Round 3 cross-reviews.

---

## Proposal Summary

### Alpha-M (MLFF Biomolecular Crash Test)

**mlffeng proposal (1,024 lines):**
- 3 primary MLFFs: MACE-OFF24(M), SO3LR, AI2BMD + 2 classical baselines + BioEmu as
  non-MD comparator for Gamma integration
- Full simulation protocol: 1 fs timestep, Langevin 300K, NVT, 50 ns production,
  10 replicas × 10 ns for S2
- MVP compute: **~88,400 GPU-hrs** (production + S2 replicas + contingency)
- SLURM design: 155 independent jobs, checkpoint every 1 ns, ~250 GB storage
- Timeline: 12-14 weeks (6 phases)
- New discovery: **Garnet force field** (arXiv March 2026) -- GNN-parameterized classical
  FF trained on protein NMR data, validated on our benchmark proteins. Potential
  additional baseline.

**bioval proposal (934 lines):**
- Final 7 MVP proteins confirmed with complete data inventory:
  ubiquitin, GB3, HEWL, BPTI, barnase, T4 lysozyme, crambin
- **~5,575 experimental data points** across 7 MVP proteins (535 S2, 2,310 shifts,
  275 J-couplings, 2,335 RDCs, 1 SAXS profile)
- NMR extraction: 6-step BMRB pipeline with RefDB re-referencing
- Back-calculation: SHIFTX2 (primary) + SPARTA+ (secondary) + UCBShift 2.0
- S2 via iRED method with 20-replica convergence protocol
- Statistical pass/fail calibrated against classical FFs
- 8-protein Gamma overlap with explicit feature handoff specification

### Gamma (Dynamics-to-Function)

**ensfunc proposal (1,037 lines):**
- 3-tier protein selection: 50 Tier 1 (full analysis), 100 Tier 2 (wildtype only),
  ~50 Tier 3 (sequence-only comparison)
- BioEmu pipeline: Tier 1 wildtype (2,000 conformations, ~143 GPU-hrs) + Tier 2
  variant-specific (50 proteins × 20 variants × 500 conformations, ~1,700 GPU-hrs)
- 15 ensemble features: 5 per-residue, 5 pairwise, 5 global
- 4-stage ML framework: statistical baseline → MLP/XGBoost → GATv2 GNN → ensemble-augmented baselines
- Compute **refined to ~3,037 GPU-hrs** (down from Cohort 1's 8,200 estimate)
- Timeline: ~11 weeks
- Success threshold: win rate >55% against ESMDance on binding/catalysis assays
- Kill criteria: RMSF ρ < 0.1 across >50% proteins by June 30

### Delta (PerturbMark)

**pertbio proposal (1,050 lines):**
- Complete PerturbMark benchmark specification with Tahoe-100M preprocessing protocol
- 10+ methods in 3 priority tiers + 5 mandatory linear baselines
- Tier 0-3 framework with organ-based cell line holdout for cross-context splits
- 7-metric calibrated suite with exact formulas (WMSE, R²_w(delta), DRF, etc.)
- 4 batch effect control experiments
- 5 information leakage prevention measures (DataSAIL integration)
- Compute: **~1,070 GPU-hrs**
- **6-week sprint** to bioRxiv by July 15, 2026
- 15-row feature comparison table vs scPerturBench

### Evaluation Framework

**evalstat proposal (1,529 lines):**
- Pre-registration protocol for all three projects (OSF)
- 6 pre-specified hypotheses (H1-H6)
- Alpha-M: Friedman/Nemenyi with exact critical differences, ICC > 0.70 convergence,
  recommendation to expand to 20 proteins for power
- Gamma: nested leave-protein-out CV, 4-condition "dynamics helps" decision criterion,
  1,000 permutation tests with Phipson-Smyth exact p-values
- Delta: DRF calibration, BH-FDR across 120 tests, 5% WMSE reduction threshold
- Figure and table templates for Nature Portfolio compliance
- Sensitivity analyses: 7 for Alpha-M, 8 for Gamma, 9 for Delta
- Negative result strategy for all projects

### Strategy

**scopeadv proposal (986 lines):**
- Updated competition: scPPDM is a new Tahoe-100M entrant compressing Delta's window
- Combined vs separate decision: 4 dated decision points (June 30, Aug 15, Sep 30, Oct 15)
- Publication sequence with specific dates (Delta preprint July 15, Gamma Sep 15,
  Combined Nov 15)
- ASCII Gantt chart May-December 2026
- 15 risks (5 per project) with probability, impact, mitigation, trigger, owner
- 6 hard kill criteria + 5 soft pivots, all dated
- Total compute: ~99,400 GPU-hrs over 7 months
- Portfolio worst-case probability: 0.9% (all three fail to publish)

---

## Conflicts and Resolutions

### Conflict 1: Alpha-M Compute -- MVP vs Full

mlffeng estimates 88,400 GPU-hrs for MVP (7 proteins × 3 MLFFs + replicas + contingency).
evalstat recommends 20 proteins for statistical power. scopeadv sets the absolute floor
at 5 proteins × 3 MLFFs × 30 ns.

**Resolution:** Start with 7 MVP proteins. If simulations complete faster than expected
(Phase 2 finishes by Week 6 instead of Week 8), expand to 10-12 proteins. The decision
point is August 15 (scopeadv kill criterion).

### Conflict 2: Gamma Compute Estimate

ensfunc refined compute to ~3,037 GPU-hrs (down from Cohort 1's 8,200). This is
substantially lower because the wildtype ensemble hypothesis reduces variant-specific
sampling needs.

**Resolution:** Accept the refined estimate. The compute savings allow more resources
for Alpha-M. Allocate saved GPU-hrs as Alpha-M contingency.

### Conflict 3: Garnet Force Field

mlffeng discovered Garnet (March 2026) -- a GNN-parameterized classical FF trained on
protein NMR data, validated on our exact benchmark proteins (GB3, BPTI, HEWL, ubiquitin).

**Resolution:** Include Garnet as an additional baseline. It bridges classical and ML
paradigms and strengthens the benchmark narrative. This is a new finding that Cohort 1
did not have.

### Conflict 4: Combined Paper Decision Timeline

scopeadv wants the combined Gamma+Alpha-M decision by October 15. ensfunc needs Gamma
results by September to write. mlffeng needs simulations complete by August for analysis.

**Resolution:** Accept scopeadv's timeline. The decision is designed for separability --
Gamma can publish standalone if Alpha-M is delayed. The 4-checkpoint system
(June 30 → Aug 15 → Sep 30 → Oct 15) provides adequate decision points.

---

## The Combined Gamma+Alpha-M Narrative (Draft)

**Title:** "From Accurate Ensembles to Biological Function: Validating and Applying
ML Protein Dynamics"

**One-sentence claim:** We establish which protein ensemble generators produce
physically realistic dynamics by comparing against NMR/SAXS observables, then
demonstrate that physically accurate ensembles predict mutation effects on protein
function better than static or sequence-only methods.

**Structure:**
1. Introduction: post-AlphaFold, the dynamics question
2. Part I (Alpha-M): MLFF benchmark against experimental observables for 7-15 proteins
3. Part II (Gamma): Ensemble features predict DMS fitness for 200 ProteinGym proteins
4. Part III (Integration): For 8 overlap proteins, MLFF validation quality correlates
   with fitness prediction quality
5. Discussion: implications for ensemble methods, which MLFFs to trust, when dynamics
   matters for function

**Key integration question:** "Do more physically accurate ensemble generators produce
better functional predictions?" This cannot be answered by either project alone.

---

## Delta Parallel Track

Delta runs independently with its own publication timeline:
- Preprint: July 15, 2026
- Nature Methods submission: August 1, 2026
- Independent of Gamma+Alpha-M outcome

---

## Round 3 Cross-Review Assignments

Each proposal is reviewed by 2-3 agents bringing different perspectives.

### Cross-Review Matrix

| Proposal | Reviewer 1 | Reviewer 2 | Reviewer 3 |
|----------|-----------|-----------|-----------|
| Alpha-M simulation (mlffeng) | bioval (data quality) | evalstat (methodology) | scopeadv (strategy) |
| Gamma (ensfunc) | mlffeng (ensemble quality) | evalstat (methodology) | scopeadv (strategy) |
| Delta (pertbio) | evalstat (methodology) | scopeadv (strategy) | ensfunc (cross-domain) |

### Additional Integration Review

| Combined Gamma+Alpha-M | Reviewers |
|------------------------|-----------|
| Integration critique | mlffeng + bioval + ensfunc (joint review) |

### Output Files

| Reviewer | Proposal Reviewed | Output |
|----------|-------------------|--------|
| bioval | Alpha-M (mlffeng) | `critiques/bioval-reviews-mlffeng-R03.md` |
| evalstat | Alpha-M (mlffeng) | `critiques/evalstat-reviews-mlffeng-R03.md` |
| scopeadv | Alpha-M (mlffeng) | `critiques/scopeadv-reviews-mlffeng-R03.md` |
| mlffeng | Gamma (ensfunc) | `critiques/mlffeng-reviews-ensfunc-R03.md` |
| evalstat | Gamma (ensfunc) | `critiques/evalstat-reviews-ensfunc-R03.md` |
| scopeadv | Gamma (ensfunc) | `critiques/scopeadv-reviews-ensfunc-R03.md` |
| evalstat | Delta (pertbio) | `critiques/evalstat-reviews-pertbio-R03.md` |
| scopeadv | Delta (pertbio) | `critiques/scopeadv-reviews-pertbio-R03.md` |
| ensfunc | Delta (pertbio) | `critiques/ensfunc-reviews-pertbio-R03.md` |

### Launch Order (3 waves of 3)

**Wave 1:** bioval reviews Alpha-M, mlffeng reviews Gamma, evalstat reviews Delta
**Wave 2:** evalstat reviews Alpha-M, scopeadv reviews Gamma, scopeadv reviews Delta
**Wave 3:** scopeadv reviews Alpha-M, ensfunc reviews Delta, joint integration critique
