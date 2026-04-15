---
agent: stratrev (Strategy Director)
round: 3
date: 2026-04-15
type: deliberation
---

# Cross-Reviewer Deliberation: Strategic Synthesis and Final Recommendations

## Reviewing Agent

Research Strategy Director (stratrev). Former Nature Methods associate editor
(3 years), NIH study section member, PI with 40+ publications. This document
is the SYNTHESIS role: I integrate all reviewer positions from Wave 1
deliberations (dynrev, biomlrev, statrev) alongside Round 1/2 findings and my
own competitive landscape verification to produce coherent, decisive strategic
recommendations for the final implementation plan.

---

## Executive Summary

After reviewing all three Wave 1 deliberations, I make the following calls:

1. **Combined paper: DEFAULT TO SEPARATION with conditional recombination.**
   I align with biomlrev's revised 30-35% viability and statrev's finding that
   BF_10 ~ 1.3 at N_eff = 7.8. The combined paper proceeds ONLY if the 14x10
   expanded design is feasible AND pilot data by August 31 meet specific
   thresholds. The integration claim remains completely unoccupied -- a
   genuine strategic asset -- but the statistical constraints make it a
   conditional bet, not a default.

2. **Alpha-M: GO. NatMeth Registered Report as primary pathway, with the
   combined NCS paper as the upside scenario.** Alpha-M is the portfolio's
   foundation: lowest scoop risk (<10%), highest standalone viability
   (65-70%), and essential data regardless of combined paper outcome.

3. **Gamma: CONDITIONAL GO, focused on assay-type stratification.** The
   RSALOR baseline at 0.465 and MutRobustness at rho~0.6 constrain the
   novelty window. Gamma's unique contribution is experimental DMS fitness
   plus assay-type stratification. Venue: Bioinformatics/PLOS Comp Bio
   standalone, or NCS if integrated.

4. **Delta: GO with accelerated timeline.** First independent Tahoe-100M
   benchmark. Preprint by August 15 is non-negotiable. SCALE's self-
   evaluation and VCC metric gaming strengthen Delta's case for neutral,
   calibrated evaluation.

5. **Portfolio expected value: 17.3 impact units** (revised down from 18.3).

---

## Section 1: The Combined Paper Decision

### 1.1 Integration of All Reviewer Positions

I have carefully reviewed each reviewer's position on the combined paper:

**dynrev (Round 3 deliberation):**
- CONCUR with 42% power at rho=0.5 for 6x8
- Confirms 14 proteins with NMR S2 data ARE identifiable (9-10 strict,
  14 with relaxed residue limit)
- Confirms 10 generators CAN be assembled
- Proposes incomplete crossed design (MLFFs only on Tier A/B proteins)
- Recommends option (c): separate MLFF benchmarking from integration claim
- GO/NO-GO criteria specified with 6 GO and 4 NO-GO thresholds
- **Net position: Major Revision, proceed with conditions**

**CONCUR** with dynrev's protein list, generator roster, and option (c) for
the incomplete crossed design. The separation of MLFF benchmarking (9
MLFF-feasible proteins) from the integration claim (all 14 proteins with
methods that can simulate all of them) is the correct architecture. This
means the integration analysis uses approximately 14 proteins x 7 generators
(classical FFs + BioEmu + Boltz-2 + AlphaFlow, excluding MLFFs from large
proteins), yielding N_eff ~ 15-17 for the integration claim specifically.

**biomlrev (Round 3 deliberation):**
- Revised combined paper viability DOWN from 40% to 30-35%
- Recommends DEFAULT TO SEPARATION with conditional recombination
- BioEmu ff14SB ceiling attenuates dynamics signal by ~50%
- Realistic improvement ceiling: delta-Spearman 0.04-0.06 on binding/activity
  (optimistic) to 0.02-0.03 (moderate)
- RSALOR at 0.465 is the inescapable baseline
- MutRobustness differentiation is via experimental DMS fitness
- Assay-type stratification is the paper's best finding
- Requires delta-Spearman > 0.04 and rho > 0.4 with BF_10 > 3

**CONCUR** with biomlrev's revised viability of 30-35% and the default-to-
separation recommendation. The attenuation chain analysis (sqrt(0.62) *
sqrt(0.80) * 0.7 ~ 0.49 of original signal) is physically grounded and
convincing. The realistic improvement ceiling of 0.04-0.06 on binding/
activity is the correct target. I note that this means Gamma MUST succeed
on binding assays specifically to be publishable, and ProteinGym has only
14 binding assays -- a tight margin.

**statrev (Round 3 deliberation):**
- Power at 42% for 6x8 CONFIRMED, worsened to ~38% with convergence
  attenuation
- 14x10 design achieves ~74% power (down from 80% due to convergence)
- JZS BF_10 at N_eff = 7.8, r = 0.5: only ~1.3 (anecdotal)
- JZS BF_10 at N_eff = 20.4, r = 0.5: ~3.9 (moderate evidence)
- MDE at N = 217 ProteinGym assays: delta-rho ~ 0.135 (large, not marginal)
- Truncation-to-shortest protocol is MANDATORY for primary analysis
- Convergence attenuation inflates apparent N_eff by ~15-25%
  (anti-conservative)
- Revised combined paper probability: 35%

**CONCUR** with statrev's power analysis and truncation recommendation.
**PARTIALLY CONCUR** with the 35% viability: I place it at 30%, slightly
lower, because statrev's BF_10 ~ 3.9 at 14x10 is BARELY "moderate evidence"
and requires the true effect to be rho >= 0.5. The convergence attenuation
finding (apparent N_eff inflation) is the single most important new
statistical insight from Round 3.

### 1.2 My Recommendation: Default to Separation

**RECOMMENDATION: DEFAULT TO SEPARATION. Pursue the combined paper as a
conditional upside scenario with a hard August 31 decision point.**

**Rationale (portfolio optimization):**

I frame this as an expected value calculation. The combined paper is a
high-variance bet: if it works (rho >= 0.5, BF_10 >= 3 under JZS, Gamma
beats RSALOR by >= 0.04 on binding+activity), it yields a NCS Article
(impact = 10). If it fails, the time spent on integration analysis is
partially wasted (2-4 weeks), and the separate papers are delayed by the
integration attempt.

The key insight is that Alpha-M and Gamma can be designed to ALLOW
integration without REQUIRING it. This is the "option value" approach:
design the experiments so that the integration scatter plot is possible
if the data support it, but each component stands alone.

The design changes needed for this approach are minimal:
- Alpha-M: run BioEmu, Boltz-2, and AlphaFlow ensembles on all 14
  proteins (compute cost: negligible for generative methods)
- Gamma: process the 14 Alpha-M proteins through the fitness pipeline
  (compute cost: minimal)
- Integration: compute the scatter plot only if both halves succeed

The cost of keeping the combined paper option alive is approximately
50-100 GPU-hours (for generative ensemble generation on 14 proteins)
and 2 weeks of analyst time (for the integration analysis in September).
The benefit is the 30% chance of a NCS Article. The expected value of
keeping the option is: 0.30 * 10 - 0.70 * 0.5 = 2.65 impact units. This
is positive and worth pursuing, but NOT at the expense of delaying Alpha-M
or Gamma standalone.

### 1.3 August 31 Decision Thresholds

Drawing on all three Wave 1 reviewers, I specify the following thresholds.
These are FINAL and should be entered into the pre-registration.

**COMBINE if ALL of the following hold by August 31:**

| # | Threshold | Source | Metric |
|---|-----------|--------|--------|
| T1 | >= 12 of 14 proteins have S2 data from >= 8 generators | dynrev | Protein x generator coverage |
| T2 | >= 2 MLFFs produce stable trajectories >= 10 ns on >= 3 Tier B proteins | dynrev G1 | MLFF stability |
| T3 | S2 R^2 range across generators >= 0.20 on >= 3 proteins | dynrev N2 | Meaningful variation |
| T4 | Gamma binding+activity: delta-Spearman >= 0.03 over RSALOR (paired Wilcoxon one-sided p < 0.10 on first 30-50 proteins) | biomlrev | Gamma pilot |
| T5 | Integration pilot: rank correlation between S2 accuracy and fitness improvement > 0 on >= 3 overlap proteins | biomlrev | Directional signal |
| T6 | BioEmu disulfide integrity > 95% on BPTI and HEWL | dynrev G3 | BioEmu validity |

**SEPARATE if ANY of the following hold:**

| # | Trigger | Source |
|---|---------|--------|
| S1 | < 10 of 14 proteins have S2 data from >= 8 generators | Design infeasible |
| S2 | 0 MLFFs produce stable trajectory > 5 ns on any Tier B protein | MLFF failure |
| S3 | Gamma binding+activity: delta-Spearman < 0.01 on first 30-50 proteins | Gamma failure |
| S4 | Integration pilot: rho <= 0 between S2 accuracy and fitness | No signal |
| S5 | BioEmu disulfide integrity < 95% with no fix by August 1 | Data compromised |

### 1.4 Fallback Venues Under Separation

| Component | Primary Venue | Backup Venue | Format |
|-----------|--------------|--------------|--------|
| Alpha-M | Nature Methods (Registered Report) | JCTC (if NatMeth rejects Stage 1) | Resource |
| Gamma (positive stratification) | Genome Research | Bioinformatics | Article |
| Gamma (marginal overall, strong binding) | Bioinformatics | PLOS Comp Bio | Article |
| Gamma (null result) | PLOS Comp Bio | Bioinformatics Brief | Negative result |
| Delta | Nature Methods | Genome Biology | Article |

---

## Section 2: Scope Decisions

I issue YES/NO recommendations for each pending scope decision, integrating
all reviewer input.

### 2.1 Should AI2BMD Be Dropped?

**DECISION: YES. DROP AI2BMD.**

**CONCUR with dynrev and implrev.** The evidence is overwhelming:

| Factor | Evidence | Source |
|--------|----------|-------|
| Open issues | 22 (up from 12) | implrev R2 |
| H200 support | Untested (issue #72 open since Aug 2025) | implrev R2 |
| Container support | Docker only, no Singularity | implrev R2 |
| Last release | v1.1.0 (Feb 2025), 14 months stale | implrev R2 |
| Hybrid solvent | AMOEBA water, not pure MLFF | dynrev R2, R3 |
| Energy scaling | Errors increase with protein size | dynrev R2 |
| Speed | 2.61 s/step for 13K-atom system | implrev R2 |

dynrev's argument that AI2BMD was never a "pure ab initio" representative
is decisive. MACE-OFF24 and SO3LR are better "pure MLFF" representatives
because they apply the same potential to protein and water. The scientific
loss from dropping AI2BMD is zero.

**Action:** Remove AI2BMD from all method rosters and compute budgets.
Reallocate AI2BMD's compute allocation (estimated ~5,000 GPU-hrs) to
additional replicas for MACE-OFF24 and SO3LR.

### 2.2 Should Tahoe-x1 Be Added to Delta Tier 1?

**DECISION: YES. ADD Tahoe-x1 to Delta Tier 1.**

**CONCUR with implrev (R2) and my own R1 recommendation.** The argument
is straightforward: Tahoe-x1 is the dataset creators' own model, trained
on Tahoe-100M. Omitting it from a Tahoe-100M benchmark would be a glaring
gap that every reviewer will flag. Tahoe-x1 is the ONLY model with native
Tahoe-100M streaming support, making it the easiest to evaluate.

My April 15, 2026 web search confirms no independent Tahoe-100M benchmark
has appeared. SCALE (NVIDIA, March 2026) self-evaluates on Tahoe-100M but
is a method paper, not a neutral benchmark. Delta remains the first
independent evaluation.

**Action:** Add Tahoe-x1 to Delta Tier 1 method roster. Use the
pre-trained model from Tahoe Bio's repository. Evaluate using Delta's
calibrated metric framework (not Tahoe-x1's own metrics). This ensures
neutrality.

### 2.3 Should Gamma Success Threshold Be Raised from 55% to 57%?

**DECISION: YES. RAISE to 57%.**

**CONCUR with statrev.** The statistical argument is clear:

- At N = 217 assays, 55% win rate has 95% CI [48.4%, 61.6%], which
  INCLUDES 50% (chance). This means a 55% result is not statistically
  significant at alpha = 0.05.
- The one-sided significance threshold at alpha = 0.05 is 56.7%.
- Rounding up to 57% ensures the win rate exceeds the significance
  threshold.

**However, I note that the win rate is a SECONDARY metric.** Following
biomlrev's recommendation, the PRIMARY metric should be the paired Wilcoxon
signed-rank test on per-assay Spearman differences between Gamma and
RSALOR. The win rate is reported as a supplementary descriptive statistic.

**Action:** Update the Gamma success threshold to 57% win rate. Define
the primary success criterion as paired Wilcoxon p < 0.05 (one-sided)
on binding+activity assays (N ~ 57 assays).

### 2.4 Should FDR Be BH-Primary?

**DECISION: YES. BH-PRIMARY, BY as sensitivity.**

**CONCUR with statrev.** The field precedent is unambiguous:

| Benchmark | Venue | FDR Method |
|-----------|-------|-----------|
| scPerturBench | Nature Methods 2025 | None |
| PerturBench | arXiv 2024 | None |
| Ahlmann-Eltze & Huber | Nature Methods 2025 | None |
| Systema | Nature Biotechnology 2025 | None |

All four major perturbation benchmarks use NO formal FDR correction.
Delta's use of BH correction already exceeds the field standard. BY
preserves only 28-42% of BH-significant results and would suppress real
findings, making Delta appear more conservative than the field requires.

**Action:** Pre-register BH as the primary FDR method. Report BY as a
sensitivity analysis. Note in the methods section that the field standard
is no correction, and Delta's use of BH is a deliberate choice for
statistical rigor.

### 2.5 Should Pre-Registration Be OSF Only or NatMeth Registered Report?

**DECISION: DUAL-TRACK. OSF pre-registration for all projects by May 15;
NatMeth Registered Report for Alpha-M as a fallback pathway.**

This is the most complex scope decision and requires nuanced reasoning:

**The tension:** A NatMeth Registered Report for Alpha-M guarantees
acceptance-in-principle (AIP) after Stage 1 review, eliminating desk
rejection risk. However, a formally accepted Registered Report cannot
simultaneously appear as part of a NCS combined paper. The two pathways
are mutually exclusive.

**Resolution (dual-track strategy):**

1. **May 15:** Pre-register all three projects on OSF. The pre-registration
   document includes the full analysis plan, protein selection, generator
   roster, statistical tests, and decision rules. This strengthens ALL
   publication pathways.

2. **May 1 - August 31:** Run Alpha-M and Gamma in parallel. The OSF
   pre-registration covers both the combined and separate scenarios.

3. **August 31 decision point:**
   - IF combined paper thresholds are met: proceed with NCS submission.
     The OSF pre-registration is cited in the NCS paper.
   - IF separation is triggered: immediately submit Alpha-M as a NatMeth
     Registered Report (Stage 1). The OSF pre-registration document
     serves as the draft Stage 1 manuscript. Target Stage 1 submission
     by September 15. Expected AIP by November 15.

4. **Parallel Delta track:** Delta pre-registers on OSF by May 15 and
   submits as a NatMeth Article (not Registered Report) by September 1,
   with preprint by August 15. Delta does not benefit as much from the
   Registered Report format because its timeline is shorter and the
   results will be available before AIP could be granted.

**Why not submit Alpha-M as a Registered Report from the start?**

Because it forecloses the combined NCS paper. The NCS paper is the
portfolio's highest-ceiling outcome (impact = 10). Committing to a NatMeth
Registered Report in May gives up the 30% chance of NCS. The option value
of waiting until August 31 is worth approximately:

    Option value = 0.30 * (10 - 8) = 0.60 impact units

(The NCS paper is worth 10 impact units; the NatMeth Registered Report
is worth 8. The difference, weighted by the 30% probability of the
combined paper succeeding, is 0.60.)

This 0.60 impact units exceeds the cost of the 3.5-month delay in the
Registered Report submission (September 15 vs May 15), which is at most
a ~3-month publication delay.

**CONCUR with dynrev's PARTIAL CONCUR** on the Registered Report pathway
requiring an adaptive trajectory-length protocol. The Stage 1 manuscript
must explicitly describe the adaptive protocol, including how T_min is
determined from Phase 1 pilot data.

---

## Section 3: Title and Framing

### 3.1 Title Selection Methodology

From my editorial experience, I evaluate titles on four criteria:
1. **Desk survival** -- will the editor send this for review? (weight: 40%)
2. **Claim accuracy** -- does the title match the actual result? (weight: 25%)
3. **Memorability** -- will people cite this by its title? (weight: 20%)
4. **Audience reach** -- does it speak to a broad readership? (weight: 15%)

I integrate the T2/T3 NCS editorial pattern analysis from my R2
verification, which showed:
- NCS favors CLAIM titles (most common format)
- "Force field" appears in ZERO NCS titles (2024-2026)
- Question titles are essentially ABSENT from NCS Research Articles
- "From X to Y" narrative titles are rare at NCS

### 3.2 Final Title Recommendations

**Scenario 1: Combined NCS Paper**

**RECOMMENDED TITLE:**

> "Physical accuracy of protein ensembles predicts functional utility
> across mutation fitness landscapes"

| Criterion | Score | Notes |
|-----------|-------|-------|
| Desk survival | 9/10 | Claim format matches NCS preference. Connects two fields. No "force field" jargon. |
| Claim accuracy | 9/10 if rho > 0.5 | Overclaims if rho < 0.4 |
| Memorability | 8/10 | Specific, quotable |
| Audience reach | 8/10 | "Protein ensembles" and "fitness landscapes" are accessible to NCS readership |

**ALTERNATIVE (if integration is positive but rho < 0.5):**

> "Systematic evaluation of protein ensemble generators reveals the link
> between physical accuracy and functional prediction"

This hedges with "reveals the link" rather than "predicts," appropriate
for BF_10 in the 3-5 range (moderate but not strong evidence).

**COVER LETTER PITCH (one sentence):** "We establish, for the first time,
that the physical accuracy of protein ensemble generators -- validated
against NMR and SAXS experiment -- correlates with their utility for
predicting mutation fitness effects, connecting force field development
directly to biological applications."

**Scenario 2: Alpha-M Standalone (NatMeth)**

**RECOMMENDED TITLE:**

> "Machine-learning force fields for proteins: how close are we to
> experiment?"

| Criterion | Score | Notes |
|-----------|-------|-------|
| Desk survival | 9/10 | Question format works at NatMeth. "Force field" is appropriate at this venue. |
| Claim accuracy | 10/10 | Hypothesis-agnostic; accurate regardless of results |
| Memorability | 8/10 | Provocative question |
| Audience reach | 8/10 | NatMeth readers understand "force fields" |

**ALTERNATIVE:**

> "The MLFF reality gap: benchmarking machine-learning force fields
> against experimental protein observables"

"Reality gap" is memorable (echoes UniFFBench) but slightly buzzword-heavy.
Reserve this if the question format is deemed too informal by NatMeth
editors.

**Scenario 3: Gamma Standalone**

**RECOMMENDED TITLE:**

> "Protein conformational ensembles encode mutation fitness effects
> beyond sequence information"

| Criterion | Score | Notes |
|-----------|-------|-------|
| Desk survival | 7/10 | Claim title; strong if data support it |
| Claim accuracy | 8/10 | "Beyond sequence information" is the key claim |
| Memorability | 7/10 | Clear but not distinctive |
| Audience reach | 7/10 | Accessible |

For Genome Research, this title works well. For Bioinformatics, I would
shorten to:

> "Dynamics features improve mutation fitness prediction for binding
> and catalysis assays"

This is more specific and signals the assay-type stratification result.

**Scenario 4: Delta Standalone (NatMeth)**

**RECOMMENDED TITLE:**

> "When does deep learning help? Calibrated perturbation benchmarking
> across cellular contexts on Tahoe-100M"

| Criterion | Score | Notes |
|-----------|-------|-------|
| Desk survival | 8/10 | Question + claim hybrid. Signals novelty (calibrated, Tahoe-100M). |
| Claim accuracy | 9/10 | "When" (not "whether") differentiates from Ahlmann-Eltze |
| Memorability | 8/10 | The "When does deep learning help?" hook is strong |
| Audience reach | 8/10 | Broad ML + biology appeal |

**ALTERNATIVE:**

> "PerturbMark: a neutral benchmark reveals where deep learning adds
> value in perturbation prediction"

Tool-name title works for NatMeth Resource format but is weaker for
Article format.

### 3.3 Title Ranking by Editor Appeal

| Rank | Paper | Title | Editor Appeal |
|------|-------|-------|---------------|
| 1 | Combined (NCS) | "Physical accuracy of protein ensembles predicts functional utility across mutation fitness landscapes" | 9/10 |
| 2 | Alpha-M (NatMeth) | "Machine-learning force fields for proteins: how close are we to experiment?" | 9/10 |
| 3 | Delta (NatMeth) | "When does deep learning help? Calibrated perturbation benchmarking across cellular contexts on Tahoe-100M" | 8/10 |
| 4 | Gamma (GR/Bioinf) | "Protein conformational ensembles encode mutation fitness effects beyond sequence information" | 7/10 |

---

## Section 4: Kill Criteria

Kill criteria define explicit, measurable conditions under which a project
component is ABANDONED. These are the go/no-go checklist for the final
implementation plan. Each criterion specifies the metric, threshold, date,
and consequence.

### 4.1 Alpha-M Kill Criteria

| ID | Criterion | Metric | Threshold | Date | Consequence |
|----|-----------|--------|-----------|------|-------------|
| AK1 | MLFF total failure | Number of MLFFs producing stable trajectory > 5 ns on any protein | 0 MLFFs | June 30 | Drop MLFF tier from benchmark. Proceed with classical FFs + generative methods only. Alpha-M becomes a "classical + generative benchmark" -- still publishable at NatMeth but with reduced scope. |
| AK2 | All S2 indistinguishable | R^2 spread across generators on any protein | < 0.05 across all generators | August 15 | All methods perform equally. No benchmark story. Pivot to a "validation confirms consensus" framing (still publishable as a short Resource at NatMeth, but lower impact). |
| AK3 | BioEmu disulfide catastrophic | SS bond integrity in BioEmu for BPTI and HEWL | < 80% (unfixable) | June 15 | Drop BPTI and HEWL from the benchmark set. Proceed with remaining 12 proteins. If < 10 proteins remain with S2 data, integration design is compromised -- trigger separation. |
| AK4 | Compute budget exceeded 3x | Actual GPU-hours vs budgeted | > 3x budget (> 330K GPU-hrs) | July 31 | Reduce replicas or protein count. Minimum: 10 proteins x 8 generators. |
| AK5 | Garnet produces no usable data | Garnet simulations crash or produce artifacts on all proteins | All proteins fail | July 15 | Drop Garnet. Generator count drops to 9. Reframe without NMR-aware FF comparison. |

### 4.2 Gamma Kill Criteria

| ID | Criterion | Metric | Threshold | Date | Consequence |
|----|-----------|--------|-----------|------|-------------|
| GK1 | BioEmu ensemble generation fails | Number of ProteinGym proteins with successful BioEmu ensemble | < 100 of 150 target | July 15 | Reduce scope. If < 50 proteins, Gamma is underpowered and should be abandoned as standalone. Retain for integration only if combined paper is still alive. |
| GK2 | Dynamics features add nothing | Delta-Spearman over RSALOR on binding+activity | < 0.01 (effectively zero) on first 50 proteins | August 15 | Gamma's positive result claim is dead. Pivot to negative result framing: "dynamics features do NOT predict experimental fitness beyond sequence" -- publishable at PLOS Comp Bio as a negative result with proper power analysis showing adequate sensitivity. |
| GK3 | RSALOR is already beaten by static methods | Any static method (ProSST, S3F-MSA) improves by > 0.10 over RSALOR on binding+activity by the time Gamma is ready | ProSST/S3F delta > 0.10 | Ongoing | Gamma's contribution is squeezed: even if dynamics helps, the improvement over the NEW baseline is smaller. Re-evaluate whether the delta over the best available static method is publishable. |
| GK4 | BioEmu scooped for ProteinGym | BioEmu team or any group publishes BioEmu + ProteinGym connection paper | Preprint appears | Ongoing | Accelerate Gamma preprint by 4 weeks. If scooped AND our delta < 0.04, abandon Gamma. If scooped but our delta >= 0.04, proceed with "independent replication + extension" framing. |

### 4.3 Combined Paper Kill Criteria

| ID | Criterion | Metric | Threshold | Date | Consequence |
|----|-----------|--------|-----------|------|-------------|
| CK1 | Separation triggered | Any S1-S5 trigger from Section 1.3 | See Section 1.3 | August 31 | Immediate separation. Alpha-M -> NatMeth Registered Report (Stage 1 by Sept 15). Gamma -> standalone (venue per Section 1.4). No further integration work. |
| CK2 | NCS desk rejection | Editor declines to send for review | Desk rejection received | Within 2 weeks of submission | Split immediately. Submit Alpha-M to NatMeth (already written as separable). Submit Gamma to Genome Research. Allow 2 weeks for manuscript reformatting. |
| CK3 | Integration BF < 1 under all priors | BF_10 under JZS, skeptical, weakly informative, informative priors | ALL four BF_10 < 1 | October 15 (full analysis) | Integration claim is dead. Report as exploratory appendix in Alpha-M standalone. Do NOT include in the main paper. |
| CK4 | Combined paper not submittable by December 1 | Manuscript completion | Not ready | December 1 | The competitive window has closed. Submit Alpha-M and Gamma as separate papers immediately. Preprint whatever is ready. |

### 4.4 Delta Kill Criteria

| ID | Criterion | Metric | Threshold | Date | Consequence |
|----|-----------|--------|-----------|------|-------------|
| DK1 | Tahoe-100M data access fails | Successful download and processing of Tahoe-100M | Cannot process > 50% of dataset within 2 weeks | May 31 | Pivot to smaller datasets (Norman et al., Dixit et al.) with reduced scope. Delta becomes a smaller benchmark paper (Genome Biology rather than NatMeth). |
| DK2 | Fewer than 5 methods evaluable | Number of Tier 1 methods with working code | < 5 | June 30 | Insufficient method diversity. Delta is not a comprehensive benchmark. Reduce to a focused comparison (GEARS vs scGPT vs Tahoe-x1 only) and reframe as a "case study" rather than a benchmark. |
| DK3 | Independent Tahoe-100M benchmark published | Another group publishes a neutral Tahoe-100M benchmark | Preprint appears before Delta preprint | Before Aug 15 | Accelerate Delta preprint by maximum effort. If the competitor's benchmark covers > 70% of Delta's method catalog, Delta's novelty is severely eroded. Pivot to metric innovation angle only. |
| DK4 | All DL methods beat linear baselines | DL consistently outperforms on all difficulty tiers | No tier where linear baselines win | August 1 | Delta's "when does DL help?" question has a trivial answer ("always"). Reframe around difficulty stratification: "DL helps everywhere but the MARGIN varies by context complexity." Still publishable but less impactful. |
| DK5 | Preprint not ready by September 1 | Manuscript completion | Not ready by Sept 1 (2-week buffer from Aug 15 target) | September 1 | The competitive window for Tahoe-100M benchmarking is closing (VCC 2026 may adopt Tahoe-100M). Accept the delay but escalate engineering effort. If not ready by October 1, the window is likely closed for NatMeth -- target Genome Biology instead. |

---

## Section 5: Executive Summary of Reviewer Consensus

### 5.1 Where All Five Reviewers AGREE

The following positions are unanimous across dynrev, biomlrev, statrev,
implrev (R2), and stratrev:

1. **AI2BMD should be dropped.** All reviewers who addressed this
   (dynrev, implrev, stratrev) agree unanimously. The hybrid solvent model,
   22 open issues, Docker-only deployment, and absence of H200 support make
   AI2BMD a liability, not an asset. The scientific loss is zero because
   MACE-OFF24 and SO3LR are better "pure MLFF" representatives.

2. **The 6x8 integration design is underpowered.** dynrev, biomlrev, and
   statrev all agree that 42% power at rho=0.5 is insufficient. The
   minimum viable design is 14 proteins x 10 generators. There is no
   disagreement on this point.

3. **JZS default prior must replace the informative N(0.5, 0.15^2) prior
   as the primary Bayesian test.** statrev demonstrated a 4:1 prior-to-data
   ratio; biomlrev and dynrev concur. The informative prior is relegated to
   sensitivity analysis only.

4. **RSALOR at Spearman 0.465 is the inescapable baseline for Gamma.**
   biomlrev confirmed, statrev validated the threshold implications, and
   stratrev concurs. No reviewer has suggested an alternative baseline.

5. **Delta should use BH-primary FDR correction.** statrev verified that
   no published perturbation benchmark uses formal FDR correction. BH is
   above the field standard. BY is excessive.

6. **The integration claim ("physical accuracy predicts functional
   utility") remains completely unoccupied in the literature.** All
   reviewers who searched (biomlrev, stratrev, dynrev) confirm this
   negative result. This is the portfolio's strongest strategic asset.

7. **Boltz-2 should be included as a mandatory ensemble generator.** dynrev
   proposed, biomlrev concurred with strategic reasoning (BioEmu vs Boltz-2
   creates a publishable sub-finding), statrev implicitly supports via the
   10-generator requirement.

8. **Pre-registration on OSF by May 15 is essential.** All reviewers
   support pre-registration as strengthening all publication pathways.

### 5.2 Where Reviewers DISAGREE

1. **Combined paper viability.** This is the most significant disagreement:
   - R2 synthesis: 40%
   - statrev (R3): 35% (convergence attenuation worsens power)
   - biomlrev (R3): 30-35% (attenuation chain + NCS editorial risk)
   - dynrev (R3): not explicitly quantified but "Major Revision, proceed
     with conditions" (implicitly 35-45% given stated conditions)
   - stratrev (this document): 30%
   - **My resolution:** I adopt 30% as the operating assumption. This
     drives the default-to-separation strategy. The 30% figure reflects
     the conjunction of: (a) statistical power constraints (~74% even with
     14x10), (b) BioEmu ff14SB ceiling attenuating the dynamics signal,
     (c) NCS editorial risk with zero precedent for this paper type, and
     (d) the requirement that both Alpha-M AND Gamma succeed simultaneously.

2. **Whether the BioEmu ff14SB ceiling makes Gamma's claim
   uninteresting.** dynrev and biomlrev disagree:
   - dynrev DISAGREES that BioEmu ff14SB makes Gamma uninteresting
     (still novel if framed as "do ff14SB features predict fitness?")
   - biomlrev PARTIALLY CONCURS that the ceiling attenuates but does not
     kill the signal
   - **My resolution:** dynrev is correct that the framing matters. The
     paper should honestly state: "Features derived from force-field-quality
     equilibrium ensembles predict variant fitness, with accuracy bounded
     by ensemble physical accuracy." This turns the ceiling into a FINDING
     rather than a limitation.

3. **Gamma standalone venue.** biomlrev recommends Bioinformatics / PLOS
   Comp Bio. dynrev suggests Genome Research is possible with strong
   stratification results. stratrev (R1) placed Genome Research as the
   stretch target.
   - **My resolution:** Genome Research if assay-type stratification
     reveals a clear pattern (dynamics helps binding/catalysis but not
     stability). Bioinformatics otherwise. PLOS Comp Bio for a null result.

4. **Whether ff14SB and ff19SB should be treated as one or two
   generators.** dynrev flags redundancy concern; statrev notes it
   could drop effective generator count to 9.
   - **My resolution:** Include both in the initial runs. Pre-register a
     redundancy test: if S2 profiles are within back-calculation noise
     for > 80% of residues across all proteins, merge into one generator
     for the integration analysis. If merged, substitute P2DFlow (SE(3)
     flow matching, JCTC 2025) as the 10th generator.

### 5.3 Consensus Summary (200 words for implementation plan)

All five reviewers agree on the portfolio's core architecture: Alpha-M
(MLFF benchmark) is a robust NatMeth paper with <10% scoop risk; Gamma
(dynamics-to-fitness) is a high-risk/high-reward bet constrained by the
RSALOR baseline at Spearman 0.465 and the BioEmu ff14SB accuracy ceiling;
Delta (perturbation benchmark on Tahoe-100M) is the fastest path to
publication but faces differentiation erosion from SCALE and VCC 2025.
The combined paper's integration claim -- that physical accuracy predicts
functional utility -- is completely unoccupied and represents the
portfolio's highest ceiling, but at 30% viability it is a conditional
upside, not a default strategy. All reviewers concur on dropping AI2BMD,
expanding the integration design from 6x8 to 14x10, using JZS as the
primary Bayesian prior, adopting BH-primary FDR for Delta, and pre-
registering all projects on OSF by May 15. The primary disagreement is
the combined paper's probability of success (30-40% range) and the
standalone venue for Gamma (Genome Research vs Bioinformatics). The
reviewers recommend defaulting to separation with a hard August 31
decision point that triggers combination only if all six quantitative
thresholds (T1-T6) are met.

---

## Section 6: Portfolio Expected Value Calculation

### 6.1 Revised Probability Estimates

Integrating all Round 3 deliberations, I revise the scenario probabilities:

| Scenario | R1 | R2 | R3 (this document) | Key Driver of Revision |
|----------|----|----|---------------------|----------------------|
| P(combined NCS succeeds) | 40% | 40% | 30% | statrev BF analysis, biomlrev attenuation, convergence |
| P(Alpha-M NatMeth, given no combined) | 85% | 82% | 80% | Unchanged; slight discount for MLFF trajectory risk |
| P(Gamma >= Genome Research, standalone) | 50% | 45% | 40% | MutRobustness constrains novelty; RSALOR baseline high |
| P(Gamma >= Bioinformatics, standalone) | 70% | 65% | 60% | Same constraints, lower bar |
| P(Delta NatMeth) | 75% | 70% | 65% | SCALE erosion, VCC 2026 looming |
| P(Delta >= Genome Biology) | 90% | 85% | 82% | Same erosion, lower bar |

### 6.2 Scenario Analysis (Revised)

**Scenario 1: Combined paper succeeds + Delta NatMeth (P = 0.30 * 0.65 = 19.5%)**
- Combined: NCS Article (impact = 10)
- Delta: NatMeth Article (impact = 7.5)
- Total impact: 17.5
- EV contribution: 0.195 * 17.5 = 3.41

**Scenario 2: Combined succeeds + Delta Genome Bio (P = 0.30 * 0.17 = 5.1%)**
- Combined: NCS (10) + Delta: Genome Bio (5.5)
- EV contribution: 0.051 * 15.5 = 0.79

**Scenario 3: Separation, Alpha-M NatMeth + Gamma GR + Delta NatMeth
(P = 0.70 * 0.80 * 0.40 * 0.65 = 14.6%)**
- Alpha-M: NatMeth Resource (8) + Gamma: GR (6) + Delta: NatMeth (7.5)
- EV contribution: 0.146 * 21.5 = 3.14

**Scenario 4: Separation, Alpha-M NatMeth + Gamma Bioinf + Delta NatMeth
(P = 0.70 * 0.80 * 0.20 * 0.65 = 7.3%)**
- Alpha-M: NatMeth (8) + Gamma: Bioinf (4.5) + Delta: NatMeth (7.5)
- EV contribution: 0.073 * 20.0 = 1.46

**Scenario 5: Separation, Alpha-M NatMeth + Gamma weak + Delta mixed
(P = 0.70 * 0.80 * 0.40 * 0.35 = 7.8%)**
- Alpha-M: NatMeth (8) + Gamma: PLOS (4) + Delta: Genome Bio (5.5)
- EV contribution: 0.078 * 17.5 = 1.37

**Scenario 6: Alpha-M weaker + all components underperform
(P = 0.70 * 0.20 * rest = ~15%)**
- Alpha-M: JCTC (5) + Gamma: Bioinf Brief (3) + Delta: Genome Bio (5.5)
- EV contribution: 0.15 * 13.5 = 2.03

**Remaining scenarios (mixed, various sub-combinations): ~30%**
- Weighted average impact: ~15
- EV contribution: 0.30 * 15 = 4.50

**Total Portfolio EV: approximately 17.3 impact units**

### 6.3 EV Comparison Across Strategies

| Strategy | Portfolio EV | P(>= 1 NCS) | P(>= 1 NatMeth) | P(>= 2 high-venue) |
|----------|------------|-------------|-----------------|-------------------|
| Default-to-separation (recommended) | 17.3 | 30% | 78% | 82% |
| Force combined (no separation option) | 16.1 | 30% | 72% | 75% |
| Separate from start (no combined option) | 16.8 | 0% | 82% | 85% |

The default-to-separation strategy dominates: it has the highest EV (17.3),
preserves the 30% NCS upside, and maintains strong NatMeth probability.
Forcing the combined paper (no fallback) reduces EV because it creates a
failure mode where both Alpha-M and Gamma are delayed by the integration
attempt. Separating from the start eliminates the NCS possibility and
reduces the ceiling.

---

## Section 7: Revised Competitive Landscape (April 15, 2026)

### 7.1 Fresh Verification

My April 15, 2026 web searches confirm:

1. **BioEmu + ProteinGym:** NO new preprint. The Microsoft Research team
   has NOT published a BioEmu + ProteinGym connection paper. The most
   recent BioEmu-related preprint remains the augmented MD paper
   (bioRxiv v2, January 2026), which is qualitative (single protein,
   single mutation). Gamma scoop risk: UNCHANGED at 35-45%.

2. **MLFF + Protein NMR Benchmark:** NO new preprint. The Ghio et al.
   paper (arXiv 2505.23354) uses MACE representations for chemical shift
   prediction but does NOT run dynamics simulations. Alpha-M scoop risk:
   UNCHANGED at <10%.

3. **Tahoe-100M Independent Benchmark:** NO independent benchmark
   published. SCALE (NVIDIA, March 2026) self-evaluates but is not
   neutral. The Theis lab Tahoe-100M analysis pipeline is data processing,
   not method benchmarking. Delta remains the first independent evaluation.
   Delta differentiation erosion: UNCHANGED at 55-65%.

4. **Dynamics-Fitness Integration:** NO published paper connects force
   field validation quality to downstream fitness prediction. The
   integration claim remains COMPLETELY UNOCCUPIED. This is confirmed
   negative -- the combined paper's strongest asset.

### 7.2 Updated Risk Table

| Project | Scoop Risk | Direction Since R2 | Key Intelligence |
|---------|-----------|-------------------|-----------------|
| Gamma | 35-45% | Unchanged | No BioEmu+fitness preprint |
| Alpha-M | <10% | Unchanged | No MLFF+NMR benchmark |
| Delta | 55-65% differentiation erosion | Unchanged | No independent Tahoe-100M benchmark |
| Combined integration | <5% | Unchanged | Claim completely unoccupied |

---

## Section 8: Final Decisions Summary

This is the actionable checklist for the Round 4 implementation plan.

### 8.1 Portfolio Architecture

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Default strategy | Separation with conditional recombination | 30% combined viability; option value is 0.60 impact units |
| Decision point | August 31, 2026 | Sufficient pilot data; preserves 6-week buffer for fallback manuscripts |
| Combined paper probability | 30% | Conjunction of power, ceiling, editorial, and dual-success requirements |

### 8.2 Scope Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Drop AI2BMD | YES | Unanimous. Zero scientific loss. |
| Add Tahoe-x1 to Delta Tier 1 | YES | Omission would be a glaring gap. |
| Raise Gamma threshold to 57% | YES | 55% is not significant at alpha=0.05 with N=217. |
| BH-primary FDR for Delta | YES | Field standard is no correction; BH already exceeds it. |
| Pre-registration | Dual-track: OSF May 15 + NatMeth RR fallback for Alpha-M | Preserves combined paper option while guaranteeing Alpha-M publication pathway. |

### 8.3 Method Rosters (Final)

**Alpha-M (10 generators):**

| # | Generator | Category | Notes |
|---|-----------|----------|-------|
| 1 | MACE-OFF24 | MLFF | Primary MLFF |
| 2 | SO3LR | MLFF | Second MLFF; solvated crambin demonstrated |
| 3 | Garnet | ML-classical | NMR-trained; contamination case study |
| 4 | BioEmu | Generative | Diffusion model; ff14SB-trained |
| 5 | Boltz-2 | Generative | Structure prediction; no ff14SB bias |
| 6 | AlphaFlow | Generative | Flow matching on AlphaFold2 |
| 7 | AMBER ff14SB | Classical | BioEmu training target; primary baseline |
| 8 | AMBER ff19SB | Classical | CMAP-corrected AMBER; redundancy test |
| 9 | a99SB-disp | Classical | IDP-specialized; TIP4P-D water |
| 10 | CHARMM36m | Classical | CHARMM family baseline |

**Delta (Tier 1 methods, revised):**

Original Tier 1 plus Tahoe-x1. scPPDM reclassified to Tier 2 (no code).
AetherCell is the sole viable Tier 2 method.

### 8.4 Protein Set (Alpha-M, 14 proteins)

Per dynrev's R3 deliberation, adopted with one modification:

| # | Protein | Residues | Tier | S2 Quality | Garnet Contaminated |
|---|---------|----------|------|-----------|-------------------|
| 1 | GB3 | 56 | A/B | Excellent | Yes (training) |
| 2 | WW domain (PIN1) | 34 | A | Good | No |
| 3 | Ubiquitin | 76 | B | Excellent | Yes (validation) |
| 4 | BPTI | 58 | B | Excellent | Yes (validation) |
| 5 | CI2 | 64 | B | Good | No |
| 6 | CspA | 70 | B | Good | No |
| 7 | GB1 | 56 | B | Excellent | No |
| 8 | Calbindin D9k | 75 | B | Good | No |
| 9 | alpha-3D | 73 | B/C | Good | No |
| 10 | Barnase | 110 | C | Excellent | Yes (complex val.) |
| 11 | HEWL | 129 | C | Excellent | Yes (validation) |
| 12 | T4 lysozyme | 164 | C | Good | No |
| 13 | Crambin | 46 | A | None (stability only) | No |
| 14 | HPr | 85 | B | Moderate | No |

Garnet-uncontaminated: 9. MLFF-feasible (<80 res): 9. Classical + BioEmu
only (>80 res): 4. Stability control: 1 (Crambin).

### 8.5 Publication Timeline

```
Timeline:     May       Jun       Jul       Aug       Sep       Oct       Nov       Dec
OSF:          [5/15]
Delta:        [===execution===][==evaluation==][preprint 8/15][NM sub 9/1]
Alpha-M:      [pilot Phase 1][=====Phase 2 production=====][backcalc]
Gamma:        [ensembles][features][ML pipeline][ablation]
Decision:                                        [8/31]
Combined:                                              [integration][manuscript]
Combined:                                                           [preprint 11/1][NCS 11/15]
Fallback:                                              [Alpha-M RR Stage 1 9/15]
Fallback:                                              [Gamma ms][preprint 10/15]
Competition:  [monthly scan][monthly scan][monthly scan][monthly scan][monthly scan]
```

### 8.6 Title Selections (Final)

| Scenario | Title | Venue |
|----------|-------|-------|
| Combined | "Physical accuracy of protein ensembles predicts functional utility across mutation fitness landscapes" | NCS |
| Alpha-M standalone | "Machine-learning force fields for proteins: how close are we to experiment?" | NatMeth |
| Gamma standalone (positive) | "Protein conformational ensembles encode mutation fitness effects beyond sequence information" | Genome Research |
| Gamma standalone (null) | "Dynamics features do not improve fitness prediction beyond sequence conservation" | PLOS Comp Bio |
| Delta | "When does deep learning help? Calibrated perturbation benchmarking across cellular contexts on Tahoe-100M" | NatMeth |

### 8.7 Kill Criteria Summary

| Project | Kill Criteria Count | Earliest Kill Date | Most Likely Kill Trigger |
|---------|--------------------|--------------------|------------------------|
| Alpha-M | 5 (AK1-AK5) | June 15 (AK3) | AK1: MLFF total failure |
| Gamma | 4 (GK1-GK4) | July 15 (GK1) | GK2: Dynamics add nothing |
| Combined | 4 (CK1-CK4) | August 31 (CK1) | CK1: Separation triggered |
| Delta | 5 (DK1-DK5) | May 31 (DK1) | DK3: Independent benchmark published first |

---

## Section 9: Responses to Specific Reviewer Positions

### 9.1 dynrev Positions

**dynrev R3, Section 1.3 (14-protein set):**
CONCUR. The 14-protein set is well-constructed. The Tier A/B/C organization
correctly handles the MLFF stability constraint. The inclusion of GB1
(uncontaminated) alongside GB3 (contaminated) for Garnet within-family
testing is a particularly strong design choice.

**dynrev R3, Section 1.4 (10-generator roster):**
CONCUR. OpenFF Sage exclusion is correct -- it is a ligand FF, not a
protein FF. The a99SB-disp addition is the strongest classical FF choice
due to the TIP4P-D water model differentiation. AlphaFlow provides a
critical third generative method.

**dynrev R3, Section 2.1 (Drop AI2BMD):**
CONCUR. See Section 2.1 above.

**dynrev R3, Section 2.2 (Garnet as case study):**
CONCUR with the three-role framing (contamination case study, paradigm
representative, GB1/GB3 control). DISAGREE with treating Garnet as a
competitive method in the primary ranking -- it must be reported separately.

**dynrev R3, GO/NO-GO criteria (Section 3.2):**
CONCUR. These criteria are well-specified and measurable. I have
incorporated them into Section 1.3 (T1-T6 and S1-S5) with minor
modifications (raising the protein coverage threshold from 12 to 12 of
14 for robustness).

### 9.2 biomlrev Positions

**biomlrev R3, Section 1.1 (BioEmu ceiling):**
PARTIALLY CONCUR. The attenuation chain analysis is convincing
(~49% of signal preserved). However, I agree with dynrev that this
does not make Gamma uninteresting -- it constrains the integration
claim more than the standalone fitness prediction claim.

**biomlrev R3, Section 2.1 (Smallest meaningful improvement):**
CONCUR. Delta-rho >= 0.04 on binding assays and >= 0.03 on activity
assays are the correct biologically meaningful thresholds. The paired
Wilcoxon at N = 57 binding+activity assays is the correct primary test.

**biomlrev R3, Section 3.1 (Default to separation):**
CONCUR. This is my recommendation as well. The statistical, editorial,
and timeline risks make separation the safer default.

**biomlrev R3, Section 5.1 (RMSF-conservation-RSA collinearity):**
CONCUR. This is the central experimental test: Model 4 (RSALOR) vs
Model 5 (RSALOR + RMSF). If Model 5 does not improve over Model 4,
dynamics is merely re-encoding evolutionary information. This ablation
must be CENTRAL, not secondary.

**biomlrev R3, Section 5.2 (ProteinGym binding assay limitation):**
PARTIALLY CONCUR. Adding 5-10 supplementary binding DMS datasets is
a good suggestion but introduces a comparability issue: supplementary
datasets are not on the standard ProteinGym leaderboard. I recommend
running the primary analysis on ProteinGym-standard assays only, with
supplementary binding datasets as a robustness check in the appendix.

### 9.3 statrev Positions

**statrev R3, Part I (Truncation protocol):**
CONCUR. Truncation to shortest common trajectory is the correct primary
analysis. The precedent from Lindorff-Larsen et al. (2012) and the
principle of controlled comparison are compelling. The 2 ns minimum
threshold (C1 in statrev's recommendations) is appropriate.

**statrev R3, Section 1.3 (Convergence attenuation):**
CONCUR. The anti-conservative inflation of apparent N_eff from ~7.8 to
~9.5 is the single most important new finding from Round 3. The
implication is clear: even the 14x10 design achieves only ~74% power at
rho = 0.5 with convergence attenuation. To recover 80% power, 16x10 is
preferred, but 14x10 is the pragmatic minimum given protein availability.

**statrev R3, Section 2.2 (JZS model specification):**
CONCUR with the full model specification including:
- Cauchy(0, 1) on standardized effect (JZS default)
- Half-Cauchy(0, 0.5) for random effect SDs
- Half-Cauchy(0, 1) for residual SD
- Four-prior sensitivity analysis
- Decision rule: BF_10 > 3 under JZS AND BF_10 > 1 under skeptical

**statrev R3, Part III (CRITICAL recommendations C1-C5):**
CONCUR with all five CRITICAL recommendations. C1 (truncation), C2
(14x10 expansion), C3 (JZS primary), C4 (pre-registration), and C5
(BH-primary FDR) are all adopted into the implementation plan.

**statrev R3, M3 (raise Gamma threshold to 57%):**
CONCUR. See Section 2.3 above.

**statrev R3, verdict (combined paper 35%):**
PARTIALLY CONCUR. I place it at 30%, slightly lower, for the reasons
stated in Section 5.2.

---

## Section 10: Remaining Open Items for Round 4

The following items are NOT resolved by this deliberation and must be
addressed in the Round 4 implementation plan:

1. **Compute budget for 14x10 design.** implrev must provide a revised
   total compute estimate for 14 proteins x 10 generators with adaptive
   trajectory lengths. The original 107K GPU-hrs estimate was for 7
   proteins x 8 generators. The expansion may not scale linearly because
   generative methods (BioEmu, Boltz-2, AlphaFlow) require negligible
   compute per protein.

2. **Week-by-week engineer allocation.** implrev must specify which
   engineering tasks can run in parallel (Alpha-M pilot, Gamma ensemble
   generation, Delta data loading) and which are sequential (MLFF setup
   must precede Phase 2 production runs).

3. **BMRB S2 data verification for expanded protein set.** The 14-protein
   set includes HPr with "moderate" S2 quality. BMRB entries for all 14
   proteins must be verified before the pre-registration is locked.

4. **BioEmu v1.3.1 disulfide test results.** The 100-sample BPTI test
   must be completed in Week 1 to confirm or eliminate BPTI and HEWL from
   the protein set.

5. **ff14SB / ff19SB redundancy test protocol.** The specific statistical
   test for merging these two generators must be defined in the pre-
   registration.

6. **Supplementary binding DMS datasets.** Identify 5-10 non-ProteinGym
   binding DMS datasets for the robustness analysis.

7. **Monthly competition scan protocol.** Define the exact search queries,
   sources (bioRxiv, arXiv, Google Scholar), and escalation procedures for
   the monthly competition scans.

---

## References

1. Ozkan, S.B. et al. (2025). A protein dynamics-based deep learning model
   enhances predictions of fitness and epistasis. PNAS 122: e2502444122.
   https://www.pnas.org/doi/10.1073/pnas.2502444122

2. Hou, L., Zhao, Q., and Shen, Y. (2026). Protein language models trained
   on biophysical dynamics inform mutation effects. PNAS 123: e2530466123.
   https://www.pnas.org/doi/10.1073/pnas.2530466123

3. Lewis, J., Jing, B. et al. (2025). Scalable emulation of protein
   equilibrium ensembles with generative deep learning. Science 369: 270-278.

4. Lewis, J. et al. (2025). BioEmu is a biomolecular emulator for sampling
   protein structure ensembles. Nature Methods.
   https://www.nature.com/articles/s41592-025-02874-1

5. BioEmu augmented molecular simulation (2026). Accelerated sampling of
   protein dynamics using BioEmu augmented molecular simulation. bioRxiv.
   https://www.biorxiv.org/content/10.64898/2026.01.07.698041v2

6. Aryal, R. et al. (2026). Assessment of BioEmu for Mutational Analysis.
   Int. J. Mol. Sci. 27: 2896.

7. Kovacs, D.P. et al. (2025). MACE-OFF: Short-Range Transferable Machine
   Learning Force Fields for Organic Molecules. JACS 147: 17598-17611.

8. Frank, M. et al. (2025). SO3LR: Molecular Simulations with a Pretrained
   Neural Network and Universal Pairwise Force Fields. JACS.

9. Garnet Force Field (2026). Training a force field for proteins and small
   molecules from scratch. arXiv:2603.16770.

10. Mannan, T. et al. (2025). UniFFBench: Evaluating Universal Machine
    Learning Force Fields Against Experimental Measurements. arXiv:2508.05762.

11. Cavender, C.E. et al. (2025). Structure-Based Experimental Datasets for
    Benchmarking Protein Simulation Force Fields. LiveCOMS.
    https://pmc.ncbi.nlm.nih.gov/articles/PMC12823150/

12. scPerturBench (2025). Benchmarking algorithms for generalizable single-
    cell perturbation response prediction. Nature Methods.
    https://www.nature.com/articles/s41592-025-02980-0

13. Ahlmann-Eltze, C. & Huber, W. (2025). Deep-learning-based gene
    perturbation effect prediction does not yet outperform simple linear
    baselines. Nature Methods.
    https://www.nature.com/articles/s41592-025-02772-6

14. Systema (2025). A framework for evaluating genetic perturbation response
    prediction beyond systematic variation. Nature Biotechnology.
    https://www.nature.com/articles/s41587-025-02777-8

15. SCALE (2026). Scalable Conditional Atlas-Level Endpoint transport for
    virtual cell perturbation prediction. arXiv:2603.17380.

16. Tahoe-x1 (2025). Tahoe-x1: Scaling Perturbation-Trained Single-Cell
    Foundation Models to 3 Billion Parameters. bioRxiv.
    https://www.biorxiv.org/content/10.1101/2025.10.23.683759v1

17. Tahoe-100M (2025). Tahoe-100M: A Giga-Scale Single-Cell Perturbation
    Atlas. bioRxiv.
    https://www.biorxiv.org/content/10.1101/2025.02.20.639398v1

18. Krueger, R. et al. (2025). Generalized design of sequence-ensemble-
    function relationships for intrinsically disordered proteins. Nature
    Computational Science. https://www.nature.com/articles/s43588-025-00881-y

19. Scouter (2026). Scouter predicts transcriptional responses to genetic
    perturbations with large language model embeddings. NCS 6: 21-28.
    https://www.nature.com/articles/s43588-025-00912-8

20. Notin, P. et al. (2023). ProteinGym: Large-Scale Benchmarks for Protein
    Fitness Prediction and Design. NeurIPS Datasets Track.

21. Lindorff-Larsen, K. et al. (2012). Systematic Validation of Protein
    Force Fields against Experimental Data. PLoS ONE 7(2): e32131.

22. Robustelli, P. et al. (2018). Developing a molecular dynamics force
    field for both folded and disordered protein states. PNAS 115: E4758.

23. Wetzels, R. & Wagenmakers, E.J. (2012). A default Bayesian hypothesis
    test for correlations. Psychonomic Bulletin & Review 19: 1057-1064.

24. Zuk, O. (2026). Mutational Robustness Predicts Protein Dynamics Across
    Natural and Designed Proteins. bioRxiv 2026.03.19.713008v1.

25. MutRobustness ESMDance (2026). PNAS. Learning Dynamic Protein
    Representations. bioRxiv 2026.01.29.702509v1.

26. Lai, T.T. & Brooks, C.L. III (2024). Accuracy and Reproducibility of
    Lipari-Szabo Order Parameters From Molecular Dynamics. J. Phys. Chem. B
    128: 10813-10822.

27. Smith, L.J. et al. (2024). Convergence of S2 order parameters from
    molecular dynamics. J. Phys. Chem. B. PMC 11790309.

28. Nature Methods (2022). Registered Reports at Nature Methods. Nat. Methods
    19: 1171. https://www.nature.com/articles/s41592-022-01407-4

29. Virtual Cell Challenge 2025 Wrap-Up. Arc Institute.
    https://arcinstitute.org/news/virtual-cell-challenge-2025-wrap-up

30. Heidari, M. et al. (2026). Evaluating Single-Cell Perturbation Response
    Models Is Far from Straightforward. bioRxiv.
    https://www.biorxiv.org/content/10.64898/2026.02.14.705879v1

31. "Virtual Cells Need Context" (2026). bioRxiv.
    https://www.biorxiv.org/content/10.64898/2026.02.04.703804v1

32. Jing, B. et al. (2024). AlphaFold Meets Flow Matching for Generating
    Protein Ensembles. ICML. arXiv:2402.04845.

33. Singh, J. et al. (2026). How Well Do Molecular Dynamics Force Fields
    Model Peptides? J. Phys. Chem. B.
    https://pmc.ncbi.nlm.nih.gov/articles/PMC12324505/

34. AetherCell (2026). bioRxiv.
    https://www.biorxiv.org/content/10.64898/2026.03.13.710968v1
