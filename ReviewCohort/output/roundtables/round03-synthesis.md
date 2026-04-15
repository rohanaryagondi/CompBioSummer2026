---
agent: ReviewCohort Orchestrator (orch)
round: 3
date: 2026-04-15
type: roundtable-synthesis
---

# Round 3 Synthesis: Cross-Reviewer Deliberation

## Overview

Five specialist reviewers engaged in structured cross-reviewer deliberation to
resolve the 8 open questions from Round 2. Wave 1 (dynrev, biomlrev, statrev)
deliberated independently, then Wave 2 (implrev, stratrev) synthesized Wave 1
positions into actionable decisions.

**Deliberation outputs (total ~4,931 lines, 153 citations):**

| Reviewer | Lines | Citations | Key Contribution |
|----------|-------|-----------|-----------------|
| dynrev   | 893   | 32 | 14-protein roster, 10-generator list, GO/NO-GO criteria |
| biomlrev | 965   | 27 | Improvement ceiling analysis, default-to-separation recommendation |
| statrev  | 1,049 | 30 | Truncation protocol, JZS model specification, 21 final recommendations |
| implrev  | 930   | 30 | Per-protein compute budget, unified week-by-week timeline |
| stratrev | 1,094 | 34 | Combined paper decision, scope decisions, titles, kill criteria |

---

## Section 1: Resolved Questions (Reviewer Consensus)

### Q1: Should AI2BMD Be Dropped? -> YES (UNANIMOUS)

All five reviewers concur. Evidence is overwhelming:
- 22 open issues, H200 untested (issue #72 open 14 months)
- Docker-only, no Singularity support for HPC
- Hybrid solvent model (classical AMOEBA water) makes it a poor "pure MLFF"
  representative -- dynrev's decisive argument
- No new releases in 14 months
- Estimated ~5,000-8,000 GPU-hours savings reallocated to MACE-OFF24/SO3LR replicas

**Decision: AI2BMD removed from all method rosters.**

### Q2: Minimum Viable Integration Design -> 14 proteins x 10 generators (CONSENSUS)

dynrev confirmed 14 proteins with published NMR S2 data organized in three tiers:

| Tier | Residues | Count | MLFF Feasible | Key Proteins |
|------|----------|-------|---------------|-------------|
| A | <50 | 3 | Yes | Crambin (stability only), WW domain (PIN1), GB3 |
| B | 50-80 | 8 | Partial | Ubiquitin, BPTI, CI2, CspA, GB1, Calbindin D9k, alpha-3D, HPr |
| C | 80-170 | 3 | No (MLFFs) | Barnase, HEWL, T4 lysozyme |

10 generators across four paradigms:

| # | Generator | Category |
|---|-----------|----------|
| 1 | MACE-OFF24 | MLFF |
| 2 | SO3LR | MLFF |
| 3 | Garnet | ML-classical |
| 4 | BioEmu | Generative |
| 5 | Boltz-2 | Generative |
| 6 | AlphaFlow | Generative |
| 7 | AMBER ff14SB | Classical |
| 8 | AMBER ff19SB | Classical |
| 9 | a99SB-disp | Classical |
| 10 | CHARMM36m | Classical |

**Critical constraint (dynrev + implrev):** The design is NOT fully crossed.
MLFFs cannot simulate Tier C proteins (>80 residues). The crossed MLFF
benchmark uses 9 proteins x 10 generators. The integration claim uses all 14
proteins x ~7 generators (classical + generative only for Tier C). This gives
N_eff ~ 15-17 for the integration analysis specifically.

implrev compute budget: ~24,100-33,800 GPU-hours for Phase 2 production;
~166,632 GPU-hours total with Phase 3 replicas and contingency.

### Q3: Combined Paper Strategy -> DEFAULT TO SEPARATION (CONSENSUS)

All reviewers converge on separation as the default, with conditional
recombination:

| Reviewer | Combined Viability | Position |
|----------|-------------------|----------|
| dynrev | Major Revision | Proceed with GO/NO-GO at Aug 31 |
| biomlrev | 30-35% | **Default to separation** |
| statrev | 35% (down from 40%) | Inadequate without 14x10 expansion |
| implrev | 30-40% | Implementation is NOT the bottleneck |
| stratrev | 30% | **Default to separation with conditional recombination** |

**Decision:** Combined paper proceeds as a conditional upside, not the
default plan. Separation triggered at August 31 unless ALL of stratrev's
T1-T6 thresholds are met:

| ID | Threshold |
|----|-----------|
| T1 | >=1 MLFF produces stable >10 ns trajectory on >=3 Tier B proteins |
| T2 | S2 block-split R^2 >0.90 for at least 1 protein |
| T3 | BioEmu disulfide integrity >95% for BPTI/HEWL |
| T4 | Integration rank correlation rho >0 (directional) on pilot proteins |
| T5 | >=12 of 14 proteins confirmed with BMRB S2 data |
| T6 | >=9 of 10 generators produce distinguishable ensembles |

**Separation triggers (any one triggers split):**

| ID | Trigger |
|----|---------|
| S1 | Pilot integration rho <=0 |
| S2 | <2 MLFFs operational by June 30 |
| S3 | BF_10 projected <1 under JZS prior at expanded design |
| S4 | Gamma delta-Spearman <0.02 on binding+activity |
| S5 | NCS-relevant scoop published before August 31 |

### Q4: FDR Correction -> BH-PRIMARY (CONSENSUS)

All four major perturbation benchmarks (scPerturBench, PerturBench,
Ahlmann-Eltze, Systema) use NO formal FDR correction. BH already exceeds
the field standard. BY preserves only 28-42% of BH-significant results.

**Decision:** BH primary, BY as sensitivity analysis.

### Q5: Drop AI2BMD Replacement -> No replacement needed (CONSENSUS)

MACE-OFF24 and SO3LR are better "pure MLFF" representatives. Scientific
loss from dropping AI2BMD is zero. Compute savings redistributed.

### Q6: Tahoe-x1 Added to Delta Tier 1 -> YES (CONSENSUS)

Omitting the dataset creators' own model from the benchmark would be a
glaring gap. Tahoe-x1 is the ONLY method with native Tahoe-100M streaming
support.

### Q7: Gamma Success Threshold -> RAISED to 57% (CONSENSUS)

At N=217 assays, 55% win rate has 95% CI [48.4%, 61.6%] which includes 50%
(chance). One-sided significance threshold at alpha=0.05 is 56.7%. Rounded
to 57%. Primary metric is paired Wilcoxon signed-rank on binding+activity
assays (N~57), not the win rate.

### Q8: Pre-registration -> DUAL-TRACK (CONSENSUS)

OSF pre-registration for all projects by May 15. NatMeth Registered Report
for Alpha-M as fallback if separation triggered at August 31. The 3.5-month
delay in Registered Report submission preserves the 30% option value of the
combined NCS paper (~0.60 impact units).

---

## Section 2: Key New Findings from Round 3

### 2.1 Trajectory Truncation Protocol [NEW -- statrev]

The most important new statistical finding: unequal trajectory lengths between
MLFF (1.6-10 ns) and classical MD (50 ns) create heteroscedastic measurement
error in S2 estimates. statrev provides the definitive framework:

- **Primary analysis:** Truncate ALL trajectories to shortest common length
  (T_min) per protein. This ensures identical convergence properties.
- **Sensitivity analysis:** Full-data analysis with convergence covariate.
- **Pre-registration required:** T_min determined after Phase 1 pilots, locked
  before Phase 2 production. Equilibration exclusion: first 10% or 0.5 ns,
  whichever is larger.
- **GO/NO-GO:** If shortest MLFF trajectory <2 ns on any protein, exclude
  that protein from integration analysis.

**Severity: CRITICAL. Non-negotiable for any benchmark publication.**

### 2.2 Convergence Attenuation of ICC [NEW -- statrev]

At 5 ns trajectories, S2 measurement error attenuates the ICC by ~15-25%,
inflating apparent N_eff from ~7.8 to ~9.5-12 (anti-conservative). This
reduces the 14x10 design's power from ~80% to ~74% at rho=0.5. The true
minimum design for 80% power is ~16x10, but 14x10 is the pragmatic ceiling
given protein availability.

### 2.3 BioEmu ff14SB Ceiling: Quantified Attenuation Chain [NEW -- biomlrev]

biomlrev provides the definitive attenuation analysis for the dynamics-to-
fitness signal:

```
Experiment -> ff14SB (R^2=0.62) -> BioEmu (R^2~0.80 vs ff14SB) -> Features -> ML -> Fitness
Signal preserved: sqrt(0.62) * sqrt(0.80) * 0.7 ~ 0.49 (49%)
```

Realistic improvement ceilings over RSALOR (Spearman 0.465):

| Scenario | True dynamics-fitness rho | After attenuation | Delta over RSALOR |
|----------|--------------------------|-------------------|-------------------|
| Optimistic | 0.6 | 0.29 | +0.04-0.06 |
| Moderate | 0.4 | 0.20 | +0.02-0.03 |
| Pessimistic | 0.2 | 0.10 | +0.00-0.01 |

### 2.4 JZS Bayesian Model Fully Specified [NEW -- statrev]

The complete model for the combined paper's central claim:
- Likelihood: Normal with crossed random effects (1|protein) + (1|generator)
- Fixed effect prior: Cauchy(0, 1) on standardized beta (JZS default)
- Random effect priors: Half-Cauchy(0, 0.5)
- Residual prior: Half-Cauchy(0, 1)
- BF_10 at r=0.5, N_eff=7.8: ~1.3 (anecdotal -- insufficient)
- BF_10 at r=0.5, N_eff=20.4 (14x10): ~3.9 (moderate -- minimum publishable)
- Decision rule: BF_10 >3 under JZS AND BF_10 >1 under skeptical prior

### 2.5 Compute Budget Mapped [NEW -- implrev]

implrev provides per-protein, per-method GPU-hour tables:

| Phase | GPU-hours | Notes |
|-------|-----------|-------|
| Phase 1 (pilot) | ~2,000-3,000 | 3-4 Tier A/B proteins, all methods |
| Phase 2 (production) | ~24,100-33,800 | 14 proteins x 10 generators |
| Phase 3 (replicas) | ~87,792 | 5 replicas on priority proteins |
| Contingency (20%) | ~22,800 | |
| **Total** | **~166,632** | |

Critical GPU contention window: Weeks 9-16 (July 1 - August 22) when Alpha-M
Phase 2 overlaps with Delta DL training. Mitigation: H200s for MLFF, RTX 5000
Ada for Delta DL methods.

### 2.6 RMSF-Conservation-RSA Collinearity Test [ELEVATED -- biomlrev]

biomlrev elevates the central experimental test to primary status:

```
Model 1: ESM2-650M + RSA                    (no dynamics)
Model 2: ESM2-650M + RSA + RMSF             (add dynamics)
Model 4: RSALOR                             (conservation + RSA)
Model 5: RSALOR + RMSF                      (conservation + RSA + dynamics)
```

If Model 5 ~ Model 4 but Model 2 > Model 1: dynamics is a proxy for
conservation, not independent information. This ablation must be CENTRAL,
not secondary.

### 2.7 Incomplete Crossed Design Architecture [NEW -- dynrev]

The 14x10 design separates into two sub-analyses:
1. **MLFF benchmark:** 9 proteins (<80 res) x 10 generators (fully crossed)
2. **Integration claim:** 14 proteins x ~7 generators (classical + generative,
   fully crossed; MLFFs present for 9 proteins only)

This avoids the statistical complications of missing MLFF cells for Tier C
proteins while preserving the integration analysis across all 14 proteins.

---

## Section 3: Final Verdicts

### 3.1 Alpha-M Standalone (NatMeth)

| Reviewer | R2 Verdict | R3 Verdict | Change |
|----------|-----------|-----------|--------|
| dynrev | Major Revision | Major Revision | Unchanged; GO/NO-GO criteria specified |
| biomlrev | Minor-Major Rev. | Minor-Major Rev. | Unchanged; defers to dynrev/implrev |
| statrev | Adequate w/ Mods | Adequate w/ Mods | New C1 (truncation); convergence attenuation |
| implrev | YELLOW | YELLOW-GREEN | AI2BMD drop + Garnet OpenMM improve feasibility |
| stratrev | GO | GO | NatMeth Registered Report as fallback |

**Consensus verdict: GO. Viability 65-70%.** Alpha-M is the portfolio's
foundation. Lowest scoop risk (<10%), highest standalone viability. The 14-
protein set and 10-generator roster are confirmed feasible.

### 3.2 Gamma Standalone

| Reviewer | R2 Verdict | R3 Verdict | Change |
|----------|-----------|-----------|--------|
| biomlrev | Major Revision | Major Revision | 45-50% viability; PLOS Comp Bio/Bioinformatics |
| statrev | Adequate w/ Mods | Adequate w/ Mods | Threshold raised to 57% |
| stratrev | Conditional GO | Conditional GO | Assay-type stratification as primary finding |

**Consensus verdict: CONDITIONAL GO. Viability 45-50%.** Gamma succeeds if
dynamics features improve binding+activity by >=0.04 Spearman over RSALOR.
The RMSF-conservation collinearity ablation is the central hypothesis test.

### 3.3 Combined Paper (NCS)

| Reviewer | R2 Verdict | R3 Verdict | Change |
|----------|-----------|-----------|--------|
| biomlrev | 40% viable | 30-35% | Down: ceiling + power |
| statrev | Inadequate | Inadequate (strengthened) | Down: convergence attenuation, BF~1.3 |
| implrev | 40% viable | 30-40% | Implementation not bottleneck |
| stratrev | 40% viable | 30% | Down: default to separation |

**Consensus verdict: DEFAULT TO SEPARATION. Viability 30%.** The integration
claim is completely unoccupied (highest strategic value) but statistically
constrained (BF~1.3 at current design, ~3.9 at expanded 14x10). Conditional
recombination at August 31 if T1-T6 thresholds met.

### 3.4 Delta Standalone (NatMeth)

| Reviewer | R2 Verdict | R3 Verdict | Change |
|----------|-----------|-----------|--------|
| biomlrev | Minor Revision | Minor Revision | 75-80% viability |
| statrev | Adequate | Adequate | BH-primary confirmed |
| implrev | YELLOW | YELLOW | Aug 15 achievable with pre-project start |
| stratrev | GO | GO with acceleration | Preprint Aug 15 non-negotiable |

**Consensus verdict: GO with accelerated timeline. Viability 75-80%.** Delta
is the strongest proposal. First independent Tahoe-100M benchmark. Tahoe-x1
added as Tier 1. Scoop risk 55-65% differentiation erosion (not elimination).

---

## Section 4: Revised Portfolio Assessment

### 4.1 Portfolio Expected Value

| Metric | R1 | R2 | R3 |
|--------|----|----|-----|
| P(>=1 NCS paper) | 40% | 40% | 30% |
| P(>=1 NatMeth paper) | 85% | 82% | 80-85% |
| P(>=2 high-venue papers) | 90% | 87% | 85% |
| P(complete failure) | <1% | <1% | <2% |
| Portfolio EV (impact units) | 19.2 | 18.3 | 17.3 |

The decline in EV is driven by the combined paper's reduced viability (40%
-> 30%) and convergence attenuation effects. The upside portfolio (Delta
NatMeth + Alpha-M NatMeth + Gamma at lower venue) remains robust.

### 4.2 Probability-Weighted Outcomes (implrev)

| Scenario | Probability | Publications |
|----------|------------|-------------|
| Best case | 15% | Combined NCS + Delta NatMeth |
| Likely case | 50% | Alpha-M NatMeth standalone + Delta NatMeth + Gamma PLOS/Bioinformatics |
| Pessimistic | 25% | Alpha-M classical-only JCTC + Delta NatMeth (delayed) + Gamma standalone |
| Worst case | 10% | Alpha-M delayed + Delta delayed |

---

## Section 5: Scope Decisions Summary

| # | Decision | Choice | Vote | Rationale |
|---|----------|--------|------|-----------|
| 1 | Drop AI2BMD | YES | 5-0 | Overwhelming evidence; zero scientific loss |
| 2 | Add Tahoe-x1 to Delta Tier 1 | YES | 5-0 | Glaring gap if omitted |
| 3 | Raise Gamma threshold to 57% | YES | 5-0 | 55% not significant at alpha=0.05 |
| 4 | BH-primary FDR for Delta | YES | 5-0 | Field standard is no correction |
| 5 | Pre-registration: dual-track | YES | 5-0 | OSF May 15 + NatMeth RR fallback |
| 6 | Default to separation | YES | 4-1 (dynrev: proceed with conditions) | 30% combined viability too risky as default |
| 7 | Truncation protocol mandatory | YES | 5-0 | Only fair benchmark comparison |
| 8 | JZS prior as primary Bayesian test | YES | 5-0 | N(0.5, 0.15^2) not defensible |

---

## Section 6: Final Statistical Recommendations (statrev)

### CRITICAL (5)

| ID | Recommendation | Applies To |
|----|---------------|-----------|
| C1 | Truncation protocol for unequal trajectory lengths | Alpha-M, Combined |
| C2 | Expand to >=14 proteins x >=10 generators | Combined |
| C3 | JZS default prior as primary Bayesian test | Combined |
| C4 | Pre-register ALL analysis choices before Phase 2 | Combined, Alpha-M |
| C5 | BH-primary FDR, BY as sensitivity | Delta |

### MAJOR (8)

| ID | Recommendation | Applies To |
|----|---------------|-----------|
| M1 | Crossed random effects model | Combined |
| M2 | ICC estimation from pilot data (raw + corrected) | Alpha-M |
| M3 | Win rate threshold >=57% | Gamma |
| M4 | Hierarchical bootstrap for per-residue analyses | Alpha-M |
| M5 | ICC(2,1) >0.50 convergence criterion | Alpha-M |
| M6 | Homolog-aware cross-validation | Gamma |
| M7 | Hierarchical testing (WMSE gates Spearman) | Delta |
| M8 | Parametric bootstrap p-value calibration | Combined |

### MINOR (7)

m1-m7: DEFF reporting, multiverse analysis, TOST margins, XGBoost constraints,
MDE per stratum, permutation tests, analysis classification table.

---

## Section 7: Kill Criteria Summary (stratrev)

| Project | Criteria | Earliest Kill | Most Likely Trigger |
|---------|----------|---------------|-------------------|
| Alpha-M | 5 (AK1-AK5) | June 15 | AK1: MLFF total failure |
| Gamma | 4 (GK1-GK4) | July 15 | GK2: Dynamics add nothing |
| Combined | 4 (CK1-CK4) | August 31 | CK1: Separation triggered |
| Delta | 5 (DK1-DK5) | May 31 | DK3: Independent benchmark published first |

Total: 18 explicit, measurable kill criteria with dates and consequences.

---

## Section 8: Title Recommendations (stratrev)

| Scenario | Title | Venue | Editor Appeal |
|----------|-------|-------|---------------|
| Combined | "Physical accuracy of protein ensembles predicts functional utility across mutation fitness landscapes" | NCS | 9/10 |
| Alpha-M | "Machine-learning force fields for proteins: how close are we to experiment?" | NatMeth | 9/10 |
| Delta | "When does deep learning help? Calibrated perturbation benchmarking across cellular contexts on Tahoe-100M" | NatMeth | 8/10 |
| Gamma (positive) | "Protein conformational ensembles encode mutation fitness effects beyond sequence information" | Genome Research | 7/10 |
| Gamma (null) | "Dynamics features do not improve fitness prediction beyond sequence conservation" | PLOS Comp Bio | -- |

---

## Section 9: Timeline Milestones

```
May 1      : All three projects begin. Alpha-M pilot + Delta data pipeline
May 15     : OSF pre-registration for all projects
June 15    : AK3 kill date (BioEmu disulfide)
June 30    : Alpha-M Phase 1 complete (D2 MLFF pilot GO/NO-GO)
July 15    : AK5 kill date (Garnet); GK1 kill date (BioEmu generation)
July 31    : D4 integration signal check
August 15  : Delta preprint (non-negotiable); D5 deadline
August 31  : COMBINED PAPER GO/NO-GO DECISION (T1-T6 / S1-S5)
September 1: Delta NatMeth submission
September 15: If separation: Alpha-M NatMeth RR Stage 1 submission
October 15 : If separation: Gamma standalone preprint
November 1 : If combined: NCS preprint
November 15: If combined: NCS submission
```

GPU contention window: Weeks 9-16 (July 1 - August 22). Mitigation: H200 for
MLFF, RTX 5000 Ada for Delta DL methods. Peak staffing: 2.5 FTE (Weeks 1-9).

---

## Section 10: Orchestrator Assessment

Round 3 deliberation achieved its goal: converting the 8 open questions from
Round 2 into actionable decisions with measurable thresholds. The five
reviewers converge on a coherent portfolio strategy.

**The most important Round 3 outcome** is the shift from "combined paper as
default" to "separation as default with conditional recombination." This is
driven by three reinforcing findings: (1) statrev's BF analysis showing only
anecdotal evidence at the current design size, (2) biomlrev's attenuation chain
showing ~49% signal preservation through BioEmu, and (3) the convergence
attenuation further reducing power from 80% to 74% at the expanded design.

**The strategic asset that survives** is the completely unoccupied integration
claim. No one has connected force field validation quality to downstream
fitness prediction. This is confirmed by both biomlrev and stratrev through
April 2026. The claim's value increases with time -- but only until someone
else publishes it first.

**The portfolio is well-hedged.** Even under the pessimistic scenario (MLFF
pilot failure + Gamma null result), the portfolio produces Alpha-M at a lower
venue and Delta at NatMeth. Complete failure probability remains <2%.

Round 4 will integrate all deliberation findings into the definitive
implementation plan.
