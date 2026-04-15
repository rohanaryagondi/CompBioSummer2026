---
agent: ReviewCohort Orchestrator (orch)
round: 2
date: 2026-04-15
type: roundtable-synthesis
---

# Round 2 Synthesis: Verification Research

## Overview

Five specialist reviewers conducted deep verification research on the 8
critical uncertainties identified in Round 1. This synthesis evaluates what
was confirmed, what was revised, what new risks emerged, and what must be
resolved in Round 3 deliberation.

**Reviewer outputs (total ~4,510 lines, 154 citations):**

| Reviewer | Lines | Citations | Key Revisions |
|----------|-------|-----------|---------------|
| dynrev   | 823   | 27 | Garnet contamination worse (5/7); BioEmu disulfide; Boltz-2 data |
| biomlrev | 840   | 27 | ESMDance comparison REVISED; MutRobustness strengthened; NCS benchmark papers exist |
| statrev  | 1,105 | 34 | Power WORSE (42% not 55%); Bayesian prior NOT defensible; FDR field norm = NONE |
| implrev  | 871   | 34 | Garnet risk DOWN (OpenMM exists); SO3LR risk DOWN; AI2BMD worse; Tier 2 code collapse |
| stratrev | 871   | 32 | Delta erosion UP (55-65%); VCC metric gaming; NatMeth Registered Reports confirmed |

---

## Section 1: Verified Claims (Round 1 Confirmed)

### 1.1 MLFF Trajectory Limits [CONFIRMED -- dynrev]

All Round 1 trajectory estimates verified with additional precision:

| MLFF | Published Max | System | Status |
|------|--------------|--------|--------|
| MACE-OFF24 | 1.6 ns | Crambin (18K atoms) | Confirmed |
| SO3LR | ~3 ns | Crambin (solvated) | Confirmed; now has solvated protein demo |
| AI2BMD | 10 ns | Chignolin (175 atoms) + AMOEBA water | Confirmed; hybrid water model |
| GEMS | 10 ns NPT | Crambin | Confirmed BUT weights unreleased, ~250x slower |

No MLFF has demonstrated stability on proteins >50 residues. The 50 ns
target on proteins up to 164 residues remains a 30-50x extrapolation.
**AceFF has no protein simulation capability and should be removed from
any fallback list.** The TEA Challenge 2023 identifies training data, not
architecture, as the bottleneck for MLFF stability.

### 1.2 BioEmu ff14SB Accuracy Ceiling [CONFIRMED -- dynrev, biomlrev]

Aryal et al. (Int. J. Mol. Sci. 2026) independently confirmed BioEmu
"effectively reproduces fundamental properties" when compared to MD --
meaning BioEmu faithfully emulates ff14SB, not experiment. BioEmu S2
accuracy is bounded by ff14SB R^2 = 0.62 vs experiment. This is the bias
chain: Experiment -> ff14SB -> BioEmu.

### 1.3 ProteinGym Landscape [CONFIRMED -- biomlrev]

ProteinGym v1.3 has 97 methods across 217 DMS substitution assays. RSALOR
sits at rank #15 with Spearman 0.465 (0.473 per paper). Per-assay breakdown:

| Assay Type | RSALOR | ProSST | Beat Threshold |
|------------|--------|--------|----------------|
| Binding    | 0.416  | 0.445  | Must beat ProSST 0.445 |
| Activity   | 0.479  | 0.476  | Must beat RSALOR 0.479 |
| Expression | 0.427  | 0.530  | Must beat ProSST 0.530 |
| Stability  | 0.575  | 0.653  | Nearly impossible |

Zero dynamics-based methods appear on the ProteinGym leaderboard.

### 1.4 All Four Prior Art Papers [CONFIRMED -- biomlrev]

- Ozkan et al. (PNAS 2025): ENM dynamics + GNN on 4 proteins
- Burgin QDPR (JCIM 2025): Classical MD features + CNN on GB1 and AvGFP
- MutRobustness (bioRxiv March 2026): dynamics-fitness at 2,000+ protein scale
- ESMDance (PNAS 2026): dynamics-trained PLM, 35M parameters

All confirmed. MutRobustness is STRONGER prior art than initially estimated
(median |rho| ~0.6 across 2,000 natural proteins, 400 de novo designs,
759 NMR proteins).

### 1.5 NCS Has Zero FF/Dynamics Papers [CONFIRMED -- biomlrev, stratrev]

"Force field" appears in ZERO NCS titles 2024-2026. NCS has published zero
dynamics-to-fitness papers, zero BioEmu/ProteinGym papers, and zero MLFF
benchmarks. NCS editorial policy: "straightforward usage of machine learning
algorithms is usually outside of the journal's scope."

However: NCS DOES publish benchmark papers (spatial transcriptomics,
autoencoders) when they include novel evaluation FRAMEWORKS and software.

### 1.6 ICC and Effective N [CONFIRMED -- statrev]

Within-protein ICC for S2 estimated at 0.72-0.82 (mean ~0.77) from published
NMR profiles. Total effective N across 6 proteins: ~7.8 independent units.
No published ICC for NMR S2 exists in the literature. The per-residue
analysis provides the same information as treating each protein as a single
observation (N=6-7).

### 1.7 No Comprehensive Tahoe-100M Benchmark Exists [CONFIRMED -- stratrev]

Only self-evaluations exist (Tahoe-x1 from Tahoe Bio, SCALE from NVIDIA).
No independent, neutral multi-method benchmark on Tahoe-100M has been
published. Delta would be first.

---

## Section 2: Revised Claims (Round 1 Modified)

### 2.1 Boltz-2 vs BioEmu: COMPARABLE, Not Superior [REVISED DOWN -- dynrev, biomlrev]

**Round 1 claim:** "Boltz-2 may be superior to BioEmu on dynamics metrics."

**Round 2 finding:** On the full mdCATH/ATLAS benchmarks:

| Method | mdCATH RMSF | ATLAS RMSF |
|--------|-------------|------------|
| Boltz-2 (X-ray) | 0.77 | 0.84 |
| Boltz-2 (MD) | 0.76 | 0.82 |
| BioEmu | 0.69 | 0.75 |

Boltz-2 outperforms on RMSF correlation (0.07-0.09), but BioEmu produces
better ensemble diversity. The "BioEmu is obsolete" concern is overstated.
**Recommendation: Include Boltz-2 as one of several ensemble generators in
the integration plot, but do not treat it as a BioEmu replacement.**

### 2.2 Garnet Feasibility: HIGH Risk -> MODERATE [REVISED DOWN -- implrev]

**Round 1 claim:** Garnet runs only in Julia/Molly.jl, requiring 2-4 weeks
of integration effort.

**Round 2 finding:** Garnet has a PyTorch port and OpenMM integration via
`topology_to_openmm_system()`. Runs at classical FF speed (~300 ns/day).
The Julia integration bottleneck is eliminated. **However, Garnet
underperforms Amber14SB on most NMR benchmark proteins** (the paper states
Amber14SB has lower ANE on all proteins except HEWL).

### 2.3 Garnet Contamination: WORSE Than Round 1 [REVISED UP -- dynrev]

**Round 1 claim:** 4 of 7 benchmark proteins in Garnet training/validation.

**Round 2 finding:** 5 of 7 (barnase in barnase/barstar complex validation).
Only T4 lysozyme is genuinely out-of-distribution (crambin has no NMR data).
The "fair test" of Garnet generalization rests on a SINGLE protein.

### 2.4 SO3LR Feasibility: HIGH -> MODERATE-HIGH [REVISED DOWN -- implrev]

**Round 1 claim:** SO3LR has never been run on a solvated protein.

**Round 2 finding:** SO3LR has published solvated crambin simulations. Speed
estimate revised upward to 0.6-1.3 ns/day for 25K atoms on H200. Setup
estimate: 3-7 days with 25-35% probability of blocking issues (neighbor list
overflow, NPT stability).

### 2.5 ESMDance Comparison to RSALOR: UNFAIR [REVISED -- biomlrev]

**Round 1 claim:** "ESMDance 0.46 < RSALOR 0.473 on ProteinGym."

**Round 2 finding:** ESMDance's 0.46 is on 412 proteins vs ESM2-35M, NOT
the standard 217 ProteinGym assays. ESMDance is NOT on the ProteinGym
leaderboard. ESMDance excels on designed/viral proteins lacking evolutionary
information. The comparison was invalid.

### 2.6 Power Analysis: WORSE Than Round 1 [REVISED UP -- statrev]

**Round 1 estimate:** ~55% power at rho=0.5 for 6x8 design.

**Round 2 finding with crossed random effects:** ~42% power at rho=0.5.
MDE at 80% power requires rho >= 0.84. Minimum viable design: 14 proteins
x 10 generators. Even with expansion, the integration should be framed
as "first evidence," not "proof."

### 2.7 Bayesian Prior: NOT Defensible [REVISED -- statrev]

**Round 1 flag:** Prior N(0.5, 0.15^2) may be strong.

**Round 2 finding:** The proposed prior contributes ~59 effective
observations vs ~15 from data -- a 4:1 prior-to-data ratio. This dominates
the posterior and is not defensible for a first-of-kind study. JZS default
prior (Wetzels & Wagenmakers, 2012) should be primary. Report four priors
as sensitivity analysis.

### 2.8 FDR Correction: Field Norm Is NONE [REVISED -- statrev]

**Round 1 recommendation:** BY primary, BH secondary.

**Round 2 finding:** All four major perturbation benchmarks (scPerturBench,
PerturBench, Ahlmann-Eltze, Systema) use NO formal FDR correction. BH
already controls FDR under the expected positive dependence (PRDS). BY
preserves only 28-42% of BH-significant results. **Delta's use of ANY formal
correction is above the field standard.** Recommendation: BH primary, BY
as sensitivity analysis.

---

## Section 3: New Risks Discovered in Round 2

### 3.1 BioEmu v1.3.0 Disulfide Potential Removal [NEW -- dynrev]

BioEmu v1.3.0 removed the Disulfide Potential. BPTI (3 SS bonds) and HEWL
(4 SS bonds) are in the Alpha-M benchmark set. The proposal must verify
BioEmu v1.3.1 handles disulfide-bonded proteins before committing. Quick
test: generate 100 BioEmu samples for BPTI and check SS bond integrity.

### 3.2 BioEmu Augmented MD Preprint [NEW -- dynrev]

bioRxiv v2 (February 2026) demonstrates BioEmu ensembles + MD + MSMs
capture kinetics on CDK2 and BRAF. The Gamma proposal uses raw BioEmu
ensembles for feature extraction. Reviewers will ask: "Why raw BioEmu when
augmented BioEmu+MD is demonstrably better?" Gamma must pre-empt this.

### 3.3 Garnet IDP Over-Compaction [NEW -- dynrev]

Garnet explicitly documented to over-compact alpha-synuclein and other IDPs.
If alpha-synuclein is in the exploratory integration set, Garnet results
must be excluded or interpreted with the known failure mode acknowledged.

### 3.4 AI2BMD Has 22 Open Issues [WORSENED -- implrev]

AI2BMD open issues rose from 12 (Round 1) to 22. H200 issue (#72) open
since August 2025. No new releases. Docker-only installation with no
Singularity support. **Recommendation: DROP AI2BMD from Alpha-M.**

### 3.5 scPPDM Code Not Found [NEW -- implrev]

scPPDM was listed as Tier 1 for Delta with available code. Despite being
evaluated ON Tahoe-100M in its paper, no public GitHub repository exists.
Must be reclassified from Tier 1 to Tier 2 or removed.

### 3.6 Tier 2 Code Collapse [NEW -- implrev]

Of 5 Tier 2 methods for Delta:
- AlphaCell: No code found -> DROP
- X-Cell: Weights "coming soon" -> DROP until released
- AetherCell: Code available (15 stars) -> SOLE viable Tier 2 candidate
- pertTF: No code found -> DROP
- scPPDM: No code (reclassified from Tier 1) -> DROP

### 3.7 No Tier 1 Method Is Tahoe-100M Ready [NEW -- implrev]

Every Tier 1 DL method requires custom data loading code for Tahoe-100M.
GEARS loads all data into memory -- will not work for 429 GB dataset.
Tahoe-x1 is the ONLY model with native streaming support. Unified data
loader is 1-2 weeks engineering per method.

### 3.8 Ahlmann-Eltze Challenge to Delta [NEW -- implrev]

"Deep-learning-based gene perturbation effect prediction does not yet
outperform simple linear baselines" (Nature Methods 2025). Directly
challenges Delta's narrative. However, Tahoe-100M (100M cells) is vastly
larger than datasets in that study, and the question of whether scale
changes the answer is genuinely open.

### 3.9 VCC Metric Gaming [NEW -- stratrev]

The Virtual Cell Challenge 2025 exposed exploitable evaluation metrics:
random data with proper transformations outperformed legitimate models
on MAE. This STRENGTHENS Delta's motivation for calibrated, game-resistant
metrics but requires explicit framing.

### 3.10 Delta Scoop Risk Elevated to 55-65% [WORSENED -- stratrev]

SCALE (NVIDIA, March 2026) now establishes Tahoe-100M evaluation baselines.
VCC metric gaming erodes the evaluation landscape. "Virtual Cells Need
Context" (bioRxiv February 2026) overlaps with cross-context evaluation.
Delta must differentiate on neutrality, calibrated metrics, and difficulty
stratification.

---

## Section 4: Revised Risk Matrix

### Alpha-M

| Risk | R1 Severity | R2 Severity | Direction |
|------|------------|------------|-----------|
| 50 ns MLFF trajectory | CRITICAL | CRITICAL | -- Confirmed |
| Per-residue effective N | CRITICAL | CRITICAL | -- Confirmed |
| AI2BMD feasibility | VERY HIGH | VERY HIGH+ | Up (22 issues) |
| Garnet contamination | HIGH | VERY HIGH | Up (5/7 proteins) |
| SO3LR stability | HIGH | MODERATE-HIGH | Down (solvated demo) |
| Garnet integration | HIGH | MODERATE | Down (OpenMM exists) |
| BioEmu disulfide removal | -- | MODERATE | NEW |
| Compute budget | 2x underestimate | ~1.5x | Improved |
| Timeline | 30-35 weeks | 22-28 weeks | Improved |

**Overall: YELLOW (unchanged). Garnet/SO3LR gains offset by AI2BMD and
contamination worsening.**

### Gamma + Combined

| Risk | R1 Severity | R2 Severity | Direction |
|------|------------|------------|-----------|
| RSALOR baseline | HIGH | VERY HIGH | Up |
| Dynamics niche occupied | HIGH | HIGH | -- |
| Boltz-2 vs BioEmu | HIGH | MODERATE | Down |
| Standard ML pipeline | HIGH | HIGH | -- |
| MutRobustness scoop | MODERATE | HIGH | Up |
| NCS editorial fit | MODERATE | HIGH | Up |
| Integration power | CRITICAL | CRITICAL+ | Up (42% not 55%) |
| Bayesian prior | MODERATE | HIGH | Up (4:1 ratio) |

**Overall: MAJOR REVISION (unchanged for combined). Integration design
INADEQUATE verdict STRENGTHENED.**

### Delta

| Risk | R1 Severity | R2 Severity | Direction |
|------|------------|------------|-----------|
| Scoop (SCALE, VCC) | MODERATE | HIGH | Up (55-65%) |
| Tier 2 code availability | HIGH | VERY HIGH | Up (4/5 unusable) |
| Tahoe-100M data pipeline | MODERATE | MODERATE | -- |
| Ahlmann-Eltze challenge | -- | MODERATE | NEW |
| FDR correction choice | MODERATE | LOW | Down (field uses none) |

**Overall: YELLOW, with landscape shift requiring strategic response.**

---

## Section 5: Revised Verdicts Summary

| Proposal | R1 Verdict | R2 Verdict | Change |
|----------|-----------|-----------|--------|
| Alpha-M standalone | Major Revision | Major Revision | Garnet/SO3LR improve; AI2BMD/contamination worsen |
| Gamma standalone | Major Revision | Major Revision | RSALOR/MutRobustness risks up; Boltz-2 risk down |
| Combined paper | 40% viable | 40% viable | Integration power worse; claim still unoccupied |
| Delta | Minor Revision | Minor-to-Major Revision | Scoop risk up; Tier 2 collapsed; Ahlmann-Eltze |

### Portfolio EV: 18.3 (down from 19.2)

| Metric | R1 | R2 |
|--------|----|----|
| P(>=1 NCS paper) | 40% | 40% |
| P(>=1 NatMeth paper) | 85% | 82% |
| P(>=2 high-venue papers) | 90% | 87% |
| P(complete failure) | <1% | <1% |

---

## Section 6: Key Questions for Round 3 Deliberation

The following unresolved disagreements and open questions must be addressed
in cross-reviewer deliberation:

### Q1: Should AI2BMD Be Dropped Entirely?

- implrev says YES (22 open issues, H200 untested, Docker-only)
- dynrev says YES (hybrid water model compromises comparison)
- The proposal loses its "pure MLFF" tier diversity. What replaces it?

### Q2: What Is the Minimum Viable Integration Design?

- statrev says 14 proteins x 10 generators for 80% power at rho=0.5
- implrev must assess whether 14 proteins with NMR S2 data exist and
  are feasible to simulate
- dynrev must assess whether 10 force field generators produce meaningfully
  different ensembles
- The 6x8 -> 14x10 expansion has compute and feasibility implications

### Q3: Can the Combined Paper's Central Claim Survive?

- At 42% power, the frequentist test is underpowered
- The Bayesian analysis with JZS prior may be the primary path
- stratrev must decide: is "first evidence with Bayesian support" enough
  for NCS, or should the combined paper be abandoned?

### Q4: Should Gamma Pivot to NCS Resource Format?

- biomlrev identifies NCS's "straightforward ML" editorial bar as HIGH
- The MLP/XGBoost/GATv2 pipeline is standard
- An NCS Resource (benchmark + data + software) has lower novelty bar
- But Resource papers typically require novel software, which Gamma lacks

### Q5: What Is Delta's Differentiation Strategy Post-SCALE?

- SCALE establishes Tahoe-100M baselines
- VCC metric gaming motivates calibrated evaluation
- Ahlmann-Eltze motivates the "when does DL help?" question
- stratrev proposes framing Delta as "the neutral, calibrated benchmark"
- How does Delta avoid becoming an incremental extension of SCALE?

### Q6: Should Alpha-M Pre-Register as a NatMeth Registered Report?

- stratrev identifies this as the safest publication pathway
- But it creates tension with the combined NCS paper strategy
- The dual-track approach (OSF pre-reg + NCS primary + NatMeth fallback)
  needs all reviewers to weigh in

### Q7: How Should the Garnet Contamination Be Handled?

- dynrev documents 5/7 contamination with only T4 lysozyme as fair test
- implrev notes Garnet underperforms Amber14SB on most proteins anyway
- Options: (a) restrict Garnet results to T4 lys only, (b) report with
  contamination caveats, (c) add additional uncontaminated proteins

### Q8: Revised Method Roster and Timeline

- Drop AI2BMD? Add Tahoe-x1 to Delta? What's the final method roster
  for each proposal?
- implrev's revised Alpha-M timeline (22-28 weeks) vs stratrev's
  publication milestones (Delta preprint August 15, decision August 31)

---

## Section 7: Orchestrator Assessment

Round 2 verification substantially sharpened the picture. The proposals are
neither as strong as the original Cohort 2 framing suggested nor as weak as
the most pessimistic Round 1 reviews implied.

**Key strategic reality:** The combined paper's integration claim ("physical
accuracy predicts functional utility") remains COMPLETELY UNOCCUPIED in the
literature. This is confirmed by both biomlrev and stratrev. Despite the
statistical challenges (42% power, 7.8 effective N), this claim is the
portfolio's highest-value target. The question for Round 3 is not WHETHER
to pursue it, but HOW to frame it given the statistical constraints.

**The three most impactful Round 2 findings:**

1. **Power is worse than thought.** The 6x8 design has ~42% power at rho=0.5
   with crossed random effects. This is the single most important revision.
   The minimum viable design (14x10) must be assessed for feasibility.

2. **Garnet is more feasible but less useful.** The OpenMM integration
   eliminates the engineering bottleneck, but 5/7 contamination and
   underperformance vs Amber14SB limit its scientific contribution.

3. **Delta's landscape shifted.** SCALE, VCC metric gaming, and Ahlmann-Eltze
   collectively change the competitive environment. Delta's value proposition
   must be reframed around neutrality and calibrated evaluation.

Round 3 deliberation will resolve the 8 questions above through direct
cross-reviewer exchange.
