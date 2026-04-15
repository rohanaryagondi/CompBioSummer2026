---
agent: ReviewCohort Orchestrator (orch)
round: 1
date: 2026-04-15
type: roundtable-synthesis
---

# Round 1 Synthesis: Independent Reviews

## Overview

Five specialist reviewers independently evaluated the Cohort 2 proposals
(Alpha-M, Gamma, Delta, and the combined Gamma+Alpha-M paper) over Round 1.
This synthesis identifies areas of consensus, disagreement, and critical
uncertainties that require verification research in Round 2.

**Reviewer outputs (total ~4,545 lines, 145 citations):**

| Reviewer | Lines | Citations | Verdict |
|----------|-------|-----------|---------|
| dynrev   | 869   | 26 | Major Revision (combined) |
| biomlrev | 740   | 26 | Major Revision (combined) / Minor Revision (Delta) |
| statrev  | 1,059 | 30 | Integration INADEQUATE |
| implrev  | 1,022 | 33 | Alpha-M YELLOW / Gamma GREEN / Delta YELLOW |
| stratrev | 855   | 30 | Combined viable (40% probability), accelerate timeline |

---

## Consensus Findings (4+ Reviewers Agree)

### 1. MLFF 50 ns Protein Trajectory Is Unproven [CRITICAL]

**Flagged by: dynrev (C1), implrev (critical), biomlrev (notes), statrev (implicit)**

No existing MLFF has demonstrated a stable 50 ns NPT trajectory on a solvated
protein. The published evidence:

| MLFF | Longest Protein Sim | System | Source |
|------|-------------------|--------|--------|
| MACE-OFF24 | 1.6 ns | Crambin (46 res, ~18K atoms) | Kovacs et al., JACS 2025 |
| SO3LR | ~3 ns | Crambin (46 res) | Frank et al., JACS 2026 |
| AI2BMD | 10 ns | Chignolin (10 res, 175 atoms) | Li et al., Nature 2024 |

The proposal requires 50 ns on proteins up to 164 residues (~25K atoms with
solvent) -- a 30-50x extrapolation from published work. dynrev estimates
40-60% probability that 2 of 3 MLFFs fail to sustain 50 ns trajectories.
implrev identifies specific software risks: AI2BMD has H200 compatibility
issues (GitHub #72), SO3LR has never been run on a solvated protein, and
Garnet runs only in Julia with no standard MD engine integration.

**Round 2 verification target:** Confirm actual maximum published trajectory
lengths and identify any unpublished reports of longer protein MLFF simulations.

### 2. Integration Is Statistically Underpowered [CRITICAL]

**Flagged by: statrev (critical), dynrev (C2), biomlrev (I1-I3)**

The combined paper's central claim ("more accurate ensembles produce better
functional predictions") rests on statistically fragile tests:

| Test | Design | Power at rho=0.5 |
|------|--------|-------------------|
| Wilcoxon signed-rank | 6 per-protein correlations, N=8 generators | ~25-35% |
| Mixed-effects model | N=48 protein-generator pairs, 6 clusters | ~55-65% |
| Bayesian correlation | Informative prior N(0.5, 0.15^2) | ~70% (BF>3) |

statrev: "The paper's central claim rests on a test with approximately 30%
power." The mixed-effects fallback has known problems with only 6 upper-level
clusters (proteins): variance component estimation is unstable (Maas & Hox,
2005) and Type I error can inflate to 10-15% (Li & Redden, 2015). The model
also requires crossed random effects (1|protein) + (1|generator), not just
(1|protein).

**Paths to adequate power (statrev's analysis):**

| Modification | Power at rho=0.5 |
|-------------|-------------------|
| Current (6 proteins, 8 generators) | ~55% (mixed-effects) |
| Add 4 proteins (10 total) | ~75% |
| Add 4 proteins + 2 generators (10x10) | ~85% |
| Current + Bayesian informative prior | ~70% (BF>3) |

### 3. Per-Residue Statistics Are Overstated [CRITICAL]

**Flagged by: dynrev (C2), statrev (1.2)**

The proposal claims "420-560 residues provide substantially more power than
N=7 proteins suggest." Both dynrev and statrev independently show this is
misleading. The effective sample size calculation:

- Within-protein ICC for S2: ~0.75-0.85 (structured regions ~0.90-0.95)
- Design effect (DEFF): 1 + (m-1) x ICC, where m = residues per protein
- For ubiquitin (70 NH, ICC=0.80): DEFF = 56.2, N_eff = 1.2
- **Total effective N across 7 proteins: ~8-10 independent units**

This is only marginally better than treating each protein as a single
observation (N=7). The cluster bootstrap provides a complementary per-residue
perspective but cannot increase the effective N for method-level comparisons.

### 4. Gamma Novelty Has Eroded Since Cohort 2 [CRITICAL]

**Flagged by: biomlrev (C1-C3), stratrev (1.1)**

Five developments narrow Gamma's novelty window:

1. **RSALOR** (Tsishyn et al., Bioinformatics 2025): Conservation + RSA alone
   achieves Spearman 0.473 on ProteinGym -- within striking distance of top
   methods at ~0.50. Gamma must show dynamics adds value BEYOND conservation+RSA.

2. **Ozkan et al.** (PNAS 2025): Dynamics-based GNN (DCIasym) predicts fitness
   on 4 ProteinGym DMS datasets. Exactly "dynamics features + GNN + ProteinGym."

3. **Burgin** (JCIM 2025): QDPR uses MD features (RMSF, H-bond, SASA, PCA) +
   CNNs for fitness on GB1, AvGFP from ProteinGym. Direct prior art not cited.

4. **SeqDance/ESMDance** (PNAS 2026): PLMs trained on MD dynamics achieve
   median Spearman 0.46 on ProteinGym -- BELOW RSALOR (0.473). Training on
   dynamics data does not outperform conservation+RSA.

5. **MutRobustness preprint** (bioRxiv March 2026): rho~0.6 between mutational
   robustness and RMSF/S2 across ~2,000 proteins. Establishes the dynamics-
   fitness link from the reverse direction.

stratrev raises Gamma scoop risk from 25-35% to 35-45%.

### 5. BioEmu Bias Chain Is Deeper Than Acknowledged [MAJOR]

**Flagged by: dynrev (M1), biomlrev (C3, A2)**

BioEmu was trained on ff14SB MD data. Its S2 accuracy is bounded by ff14SB's
(R2 = 0.62 per Smith et al. 2024). Three consequences:

- BioEmu vs experiment tests the COMBINED quality of ff14SB + BioEmu's
  generative model, not BioEmu alone
- Gamma's fitness prediction effectively tests "do ff14SB equilibrium features
  predict fitness?" -- less novel than "do dynamics predict fitness?"
- Missing control: BioEmu vs ff14SB ensemble features for Gamma fitness
  prediction. If both yield identical accuracy, BioEmu is just a fast ff14SB
  approximation.

Additionally, Boltz-2 (bioRxiv June 2025) now matches or exceeds BioEmu on
RMSF prediction, undermining BioEmu's privileged position as the sole
non-MD ensemble generator.

### 6. Compute Budget Underestimated by ~2x [CRITICAL]

**Flagged by: implrev (critical)**

implrev independently calculated per-protein MLFF ns/day rates and found:

| Phase | Proposed GPU-hrs | Revised Estimate | Factor |
|-------|-----------------|------------------|--------|
| Phase 2 (production) | 44,800 | ~56,520 | 1.26x |
| Phase 3 (S2 replicas) | 43,200 | ~120,000-190,000 | 2.8-4.4x |
| **Total Phase 2+3** | **88,000** | **~176,000-246,000** | **2-3x** |

Root cause: the proposal uses an average ns/day across all methods (mixing
MLFF at 0.25 ns/day with classical at 200+ ns/day). T4 lysozyme alone
accounts for 29% of revised MLFF compute. Realistic timeline: 30-35 weeks,
not 14-16 weeks.

### 7. Delta Differentiation Eroding [MAJOR]

**Flagged by: stratrev (1.3), biomlrev (W1)**

Delta's competitive landscape has intensified:

| Competitor | Venue | Year | Key Overlap |
|-----------|-------|------|-------------|
| scPerturBench | Nature Methods | 2025 | 27 methods, 29 datasets, 6 metrics |
| "DL vs baselines" | Nature Methods | 2025 | DL does not outperform linear baselines |
| Systema | Nature Biotechnology | 2025 | Evaluation framework, metric critique |
| Tahoe-x1 | bioRxiv | 2025 | 3B-parameter model on Tahoe-100M |
| Virtual Cell Challenge | Institutional | 2026 | Dataset 4x larger than Tahoe-100M |

stratrev raises differentiation erosion risk to 50-60%. Delta must pivot from
"does DL help?" (already answered) to "WHEN and WHERE does DL help?" -- the
4-tier difficulty hierarchy and Tahoe-100M chemical perturbation focus remain
unique.

---

## Key Disagreements

### A. Combined vs Separate Paper

- **stratrev:** Recommends combined (40% success, highest ceiling). Neither
  Alpha-M nor Gamma alone clears NCS editorial bar reliably.
- **statrev:** Integration is "INADEQUATE -- NEEDS MAJOR MODIFICATION." Power
  <55% for the central claim. Questions viability of combined paper.
- **biomlrev:** Combined requires Major Revision. Gamma standalone faces
  fundamental challenges.
- **dynrev:** Major Revision. Science is worth doing but needs protocol redesign.
- **Consensus direction:** Combined is worth pursuing IF integration overlap
  expands to 10+ proteins AND the crossed mixed-effects model is primary test.

### B. Method Count for Alpha-M

- **implrev:** Reduce to 5-6 methods. Drop AI2BMD (VERY HIGH risk) and Garnet
  (Julia-only). Keep MACE-OFF24, SO3LR, AMBER ff19SB, CHARMM36m, BioEmu, ff14SB.
- **dynrev:** Keep all methods but redesign protocol with adaptive trajectory
  lengths and pre-registered checkpoints.
- **stratrev:** Does not explicitly recommend reduction; focuses on strategic
  positioning.
- **Unresolved:** Whether losing AI2BMD and Garnet weakens the benchmark
  unacceptably, or whether including them risks the timeline.

### C. Gamma Success Threshold

- **Current proposal:** Win rate > 55%
- **biomlrev:** Raise to > 60%
- **statrev:** Raise to > 57% (significance threshold at N=150, alpha=0.05)
- **statrev calculates:** 55% win rate at N=150 is NOT significantly different
  from chance (95% CI: [0.47, 0.63] includes 0.50). Need > 56.7% for p<0.05.

### D. FDR Correction for Delta

- **Current proposal:** BY as primary
- **statrev:** Switch BH to primary (BY excessively conservative under expected
  positive dependence). BY multiplies p-values by H(m)~5.2x for m=100 tests.
  Under positive dependence, BH already controls FDR.

---

## New Findings Not Identified by Cohort 2

### From dynrev

1. **GEMS force field** (Unke et al., Sci. Adv. 2024): 10 ns NPT on solvated
   crambin -- longest published MLFF protein trajectory. Should be included
   as contingency MLFF if MACE-OFF24/SO3LR fail.
2. **BioEmu augmented MD workflow** (bioRxiv Jan 2026): Changes Gamma landscape
   by showing BioEmu ensembles need MD refinement for kinetics.
3. **Garnet IDP failure mode:** Over-compacts IDPs. Alpha-synuclein should be
   excluded from Garnet comparison.
4. **Force field version pinning** needed for reproducibility.
5. **Missing ensemble generators:** AlphaFlow, Boltz-2, BBFlow, P2DFlow, TEMPO.

### From biomlrev

1. **RSALOR baseline** is mandatory (Spearman 0.473 with zero parameters).
2. **ESMDance** achieves Spearman 0.46 -- BELOW RSALOR. Sobering for dynamics hypothesis.
3. **QDPR paper** (Burgin, JCIM 2025) is uncited direct prior art.
4. **Assay-type stratification** should be the primary finding, not the overall
   win rate. ESMDance showed dynamics particularly benefit viral/designed proteins.
5. **NCS editorial warning:** "Straightforward usage of ML algorithms is usually
   outside the journal's scope."
6. **Boltz-2** should be added as mandatory ensemble generator for overlap proteins.

### From statrev

1. **ICC(2,k)>0.80 corresponds to ICC(2,1)=0.21** ("poor" individual reliability).
   Need ICC(2,1)>0.50 minimum.
2. **Portfolio-wide ~512 statistical tests** (92 confirmatory, ~420 exploratory).
   Need Analysis Classification Table.
3. **Multiverse analysis** recommended for integration claim.
4. **Crossed random effects** needed: (1|protein) + (1|generator).
5. **Pre-registration gaps:** S2 metric, fitness computation method, feature set
   for integration, mixed-effects specification, missing data handling -- all
   must be locked before simulation.
6. **Homolog-aware CV** needed for Gamma (sequence identity leakage).

### From implrev

1. **AI2BMD H200 issues** documented in GitHub Issue #72.
2. **SO3LR never demonstrated on solvated protein** (only water boxes).
3. **AceFF-2.0 is NOT a viable fallback** -- it's a small-molecule FF.
4. **Garnet requires Julia/Molly.jl** -- 2-4 week integration task, no OpenMM bridge.
5. **Software installation tax:** 3-5 weeks before production simulations.
6. **Realistic timeline:** 30-35 weeks for Alpha-M, not 14-16.
7. **T4 lysozyme dominates compute:** ~29% of revised MLFF Phase 2 budget.
8. **BioEmu is overbudgeted:** proposal says 200 GPU-hrs, reality is ~2-3 GPU-hrs.

### From stratrev

1. **NCS precedent paper** (Krueger et al., NCS 2025): Sequence-ensemble-function
   for IDPs. Partially overlaps combined paper's conceptual territory.
2. **Scouter** (NCS 2026): NCS published a perturbation prediction paper.
   Confirms NCS interest but reduces Delta's pathway.
3. **Portfolio expected value:** 19.2 impact units. P(>=1 NCS)=40%, P(>=1 NatMeth)=85%.
4. **Monthly competition scans mandatory.** Set alerts for "BioEmu fitness,"
   "BioEmu ProteinGym," "MLFF protein NMR benchmark."
5. **Advance decision point** from September 30 to August 31.
6. **Title recommendation:** "Physical accuracy of protein ensembles predicts
   functional utility across mutation fitness landscapes" (9/10).

---

## Reviewer Verdicts Summary

### Alpha-M

| Reviewer | Verdict | Key Concern |
|----------|---------|-------------|
| dynrev | Major Revision | 50 ns unproven; S2 convergence; per-residue stats overstated |
| biomlrev | Major Revision (combined) | ML novelty insufficient for NCS standalone |
| statrev | Adequate with modifications | ICC uncharacterized; TOST margin arbitrary |
| implrev | YELLOW | Compute 2x underestimated; AI2BMD/Garnet high risk; timeline unrealistic |
| stratrev | Low scoop risk (<10%) | Strongest component; safe as Nature Methods Resource |

### Gamma

| Reviewer | Verdict | Key Concern |
|----------|---------|-------------|
| dynrev | Major Revision (combined) | BioEmu bias chain; missing ff14SB feature comparison |
| biomlrev | Major Revision | RSALOR not included; prior art not cited; standard ML pipeline |
| statrev | Adequate with modifications | Win rate threshold below significance; overfitting risk |
| implrev | GREEN | Trivial compute; production-ready software |
| stratrev | Scoop risk 35-45% | Novelty eroded; must reframe around assay-type stratification |

### Delta

| Reviewer | Verdict | Key Concern |
|----------|---------|-------------|
| biomlrev | Minor Revision | Competitive landscape; Tahoe-x1 missing; distributional metrics |
| statrev | Adequate | BY over-conservative; co-primary metric procedure unspecified |
| implrev | YELLOW | Tier 2 code availability uncertain; 12-week timeline tight |
| stratrev | 50-60% differentiation erosion | Must pivot framing; add Tahoe-x1 |

### Integration

| Reviewer | Verdict | Key Concern |
|----------|---------|-------------|
| dynrev | Partially pre-empted | Per-residue defense overstated; N=6-8 fragile |
| biomlrev | Statistically fragile | N=6 proteins; scatter plot may look like a cloud |
| statrev | **INADEQUATE** | Power <55%; needs 10+ proteins, crossed random effects |
| stratrev | Viable (40% success) | Highest ceiling; advance decision to Aug 31 |

---

## Critical Uncertainties for Round 2

The following uncertainties require targeted verification research before the
cross-reviewer deliberation in Round 3:

### U1. MLFF Trajectory Feasibility

Can any MLFF sustain >10 ns on a solvated protein larger than crambin? Are
there unpublished results, GitHub discussions, or conference presentations
showing longer protein MLFF simulations? What is the actual stability limit
for MACE-OFF24, SO3LR, and AI2BMD?

### U2. BioEmu Competitor Landscape

Has Boltz-2 been validated on the same proteins as BioEmu? What are the
head-to-head metrics? Has BioEmu v2 been announced? Are there other
scalable ensemble generators approaching BioEmu's speed?

### U3. ProteinGym 2026 Leaderboard State

What are the exact current top-10 ProteinGym methods and their Spearman
scores? Has RSALOR performance been characterized per assay type? How close
are the top methods to each other?

### U4. Prior Art Details

What exactly do Ozkan (2025), Burgin (2025), and MutRobustness (2026) show?
How much of Gamma's planned contribution do they already cover?

### U5. Software Readiness

What is the current state of GitHub repositories for MACE-OFF24, SO3LR,
AI2BMD, Garnet, and BioEmu? Have the reported issues been resolved? What is
the actual ns/day on available hardware?

### U6. Competitive Threats (April 2026)

Are there any new preprints on bioRxiv/arXiv from April 2026 that directly
compete with any of the three proposals? Has the BioEmu team published or
preprinted a ProteinGym connection?

### U7. NCS Editorial Standards

What exactly has NCS published in 2025-2026 in terms of benchmark papers,
ensemble papers, and force field papers? What is the bar?

### U8. Statistical Power Under Realistic Assumptions

If we expand to 10 proteins and 10 generators, what power do we achieve?
What if the true effect is rho=0.3 instead of 0.5?

---

## Round 2 Task Preview

Round 2 assigns each reviewer specific verification targets based on the
critical uncertainties above. See `round02-tasks.md` for detailed assignments.
