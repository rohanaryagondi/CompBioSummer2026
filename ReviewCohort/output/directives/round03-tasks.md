---
agent: ReviewCohort Orchestrator (orch)
round: 3
date: 2026-04-15
type: directive
---

# Round 3 Directives: Cross-Reviewer Deliberation

## Purpose

Round 3 is a deliberation round. Each reviewer responds to the findings of
other reviewers, revises their own positions where warranted, and works toward
convergent recommendations. Unlike Rounds 1-2 (independent work), Round 3
requires direct engagement with other reviewers' arguments.

## Output Format

Each reviewer writes a deliberation note to:
`output/deliberations/<shortname>-deliberation-R03.md`

Deliberation notes must:
1. Explicitly state which reviewer arguments they are responding to
2. Indicate where they CONCUR, PARTIALLY CONCUR, or DISAGREE
3. Provide revised positions with justification
4. End with a final verdict update (if changed from Round 1/2)

---

## Wave 1 (Parallel): dynrev, biomlrev, statrev

### dynrev — Dynamics Reviewer Deliberation

**Respond to:**

1. **statrev's power analysis (S1):** statrev finds 42% power at rho=0.5
   for the 6x8 design with crossed random effects. The minimum viable
   design is 14 proteins x 10 generators.
   - **Question for dynrev:** Are there 14 proteins with published
     experimental NMR S2 order parameters that are feasible to simulate
     with MLFFs? List candidates with residue count, NMR data quality,
     and expected MLFF stability. Consider the <50 residue MLFF stability
     constraint.
   - **Question for dynrev:** Can 10 meaningfully different ensemble
     generators be identified? The current roster is: MACE-OFF24, SO3LR,
     Garnet, BioEmu, AMBER ff14SB, AMBER ff19SB, CHARMM36m. That's 7.
     What are 3+ additional generators that produce distinct ensembles?
     Consider: Boltz-2, AlphaFlow, OpenFF Sage 2.1.0, a99SB-disp.

2. **implrev's feasibility assessment (I1-I5):** implrev revised Garnet
   risk to MODERATE (OpenMM exists) and SO3LR to MODERATE-HIGH (solvated
   demos exist). implrev recommends DROPPING AI2BMD entirely.
   - **Question for dynrev:** Do you concur with dropping AI2BMD? What is
     lost scientifically if the "pure ab initio" tier has no representative?
   - **Question for dynrev:** Given Garnet's 5/7 contamination AND
     underperformance vs Amber14SB, what is Garnet's actual scientific
     contribution to Alpha-M? Should it be treated as a "case study in
     benchmark contamination" rather than a competitive method?

3. **Revised Alpha-M assessment:** Considering all Round 2 findings,
   provide your updated verdict on Alpha-M with specific conditions
   for GO vs NO-GO at the August 31 decision point.

**Output:** `output/deliberations/dynrev-deliberation-R03.md`

---

### biomlrev — ML/Biology Reviewer Deliberation

**Respond to:**

1. **dynrev's dynamics findings (D3-D4):** dynrev confirms BioEmu ff14SB
   ceiling (R^2 = 0.62), the BioEmu augmented MD preprint, and Boltz-2
   RMSF outperformance (0.76-0.84 vs BioEmu 0.69-0.75).
   - **Question for biomlrev:** Given that BioEmu RMSF correlation is
     0.69-0.75 and ff14SB R^2 = 0.62 vs experiment, what is the realistic
     ceiling for Gamma's dynamics-to-fitness improvement over RSALOR?
     Is the improvement detectable given the noise?
   - **Question for biomlrev:** Should the combined paper include Boltz-2
     ensembles alongside BioEmu? If BioEmu-derived features predict
     fitness, do Boltz-2-derived features predict equally well?

2. **statrev's effect size concerns (S1, S3):** statrev argues that at
   rho=0.5, even the expanded 14x10 design has only ~80% power. The
   Bayesian analysis with JZS prior is the recommended primary test.
   - **Question for biomlrev:** What is the smallest biologically
     meaningful improvement in Spearman correlation over RSALOR that
     would justify the "dynamics adds value" claim? Is rho=0.5 realistic
     given the prior art (Ozkan rho ~0.6 on 4 proteins; QDPR on 2)?
   - **Question for biomlrev:** Given the MutRobustness preprint (2,000+
     proteins, |rho| ~0.6), can Gamma differentiate by using EXPERIMENTAL
     DMS data (not predicted ddG)? How many ProteinGym assays have both
     experimental fitness data AND sufficient protein dynamics information?

3. **Revised Gamma and combined paper assessment:** Provide your updated
   verdict on the combined paper. Should it proceed, or should Alpha-M
   and Gamma be separated? What conditions determine this at August 31?

**Output:** `output/deliberations/biomlrev-deliberation-R03.md`

---

### statrev — Statistics Reviewer Deliberation

**Respond to:**

1. **dynrev's convergence findings (D1-D2):** dynrev confirms that all
   MLFF trajectories max out at 1.6-10 ns for proteins. The adaptive
   trajectory-length design means different methods contribute different
   trajectory lengths to the same analysis.
   - **Question for statrev:** How should unequal trajectory lengths be
     handled statistically? If MACE-OFF24 produces 5 ns and ff14SB
     produces 50 ns on the same protein, the S2 estimates have different
     convergence properties. Should the analysis truncate all methods to
     the shortest trajectory, or model convergence as a covariate?
   - **Question for statrev:** The ICC analysis assumes converged S2
     values. With 5 ns trajectories, S2 convergence is questionable.
     How does partial convergence affect the ICC estimates and power
     calculations?

2. **biomlrev's improvement magnitude (B1-B4):** biomlrev confirms RSALOR
   at 0.465 and identifies the per-assay-type beat targets.
   - **Question for statrev:** What sample size (number of ProteinGym
     assays) is needed to detect a Spearman improvement of 0.03 (from
     0.465 to 0.495) at 80% power? This is the "dynamics adds marginal
     value" scenario.
   - **Question for statrev:** For the combined paper's central claim
     ("better ensembles -> better fitness prediction"), is there a
     Bayesian framing that works at N_eff=7.8 without the controversial
     informative prior? Specify the exact model and prior.

3. **Revised statistical recommendations:** Finalize your list of
   CRITICAL, MAJOR, and MINOR statistical recommendations across all
   proposals. Flag any that are non-negotiable go/no-go criteria.

**Output:** `output/deliberations/statrev-deliberation-R03.md`

---

## Wave 2 (Parallel): implrev, stratrev

Wave 2 launches after Wave 1 completes, so these reviewers also see
Wave 1 deliberation notes.

### implrev — Implementation Auditor Deliberation

**Respond to:**

1. **dynrev's simulation protocol (D1-D4 + Wave 1):** dynrev will assess
   whether 14 proteins are feasible and whether 10 generators exist.
   - **Question for implrev:** For the proteins dynrev identifies, provide
     compute estimates (GPU-hours per protein per method) and a revised
     total compute budget. Is the 14x10 design achievable within the
     available HPC allocation?
   - **Question for implrev:** If AI2BMD is dropped, what is the revised
     method roster and total compute? Provide a table.

2. **stratrev's timeline (T4 + Wave 1):** stratrev's publication milestones
   require Delta preprint by August 15 and combined paper decision by
   August 31.
   - **Question for implrev:** Is the Delta 12-14 week timeline compatible
     with the August 15 preprint target if work begins May 1? What are
     the critical path items?
   - **Question for implrev:** Can Alpha-M Phase 1 (pilot simulations,
     MLFF stability tests) complete by June 30 to inform the August 31
     decision? What must happen in the first 8 weeks?

3. **Revised timeline and resource allocation:** Provide a unified
   week-by-week timeline for all three projects, identifying parallel
   vs sequential work streams and resource conflicts (GPU contention,
   engineer time).

**Output:** `output/deliberations/implrev-deliberation-R03.md`

---

### stratrev — Strategy Director Deliberation

**Respond to ALL Wave 1 reviewers plus implrev.**

This is the synthesis role. stratrev must integrate all reviewer positions
into coherent strategic recommendations.

1. **The combined paper decision:** Given dynrev's dynamics assessment,
   biomlrev's improvement magnitude estimates, statrev's power analysis,
   and implrev's feasibility assessment:
   - **Make a RECOMMENDATION on combined vs separate publication.** If
     combined, specify what the minimum viable evidence looks like. If
     separate, specify the fallback venue for each component.
   - **What evidence at the August 31 decision point would trigger the
     switch from combined to separate?** Be specific about thresholds.

2. **Scope decisions:** Based on all deliberations:
   - Should AI2BMD be dropped? (dynrev + implrev input)
   - Should Tahoe-x1 be added to Delta Tier 1? (implrev input)
   - Should the Gamma success threshold be raised from 55% to 57%?
     (statrev input)
   - Should FDR be BH-primary? (statrev input)
   - Should pre-registration be on OSF only or as a NatMeth Registered
     Report? (stratrev's own analysis + all input)

3. **Title and framing:** Provide your FINAL title recommendation for
   each publication scenario (combined, separate, Delta standalone).

4. **Kill criteria:** Define explicit, measurable criteria for abandoning
   each project component. These become the go/no-go checklist in the
   final implementation plan.

5. **Executive summary of reviewer consensus:** Draft a 200-word summary
   of where all 5 reviewers agree and where they disagree. This becomes
   the opening of the final implementation plan.

**Output:** `output/deliberations/stratrev-deliberation-R03.md`

---

## Deliverables

| Reviewer | File | Wave | Depends On |
|----------|------|------|-----------|
| dynrev | `deliberations/dynrev-deliberation-R03.md` | 1 | R1 + R2 all |
| biomlrev | `deliberations/biomlrev-deliberation-R03.md` | 1 | R1 + R2 all |
| statrev | `deliberations/statrev-deliberation-R03.md` | 1 | R1 + R2 all |
| implrev | `deliberations/implrev-deliberation-R03.md` | 2 | R1 + R2 all + Wave 1 |
| stratrev | `deliberations/stratrev-deliberation-R03.md` | 2 | R1 + R2 all + Wave 1 |
