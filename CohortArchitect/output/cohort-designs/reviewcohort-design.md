---
agent: Cohort Architect
date: 2026-04-15
type: cohort-design
cohort_name: ReviewCohort
based_on: Cohort2 final proposal set, joint integration critique, all Cohort2 proposals and critiques
---

# Cohort Design: ReviewCohort -- Critical Evaluation & Implementation Planning

## Design Rationale

### What the Previous Cohort Produced

Cohort 2 (Deep Divers) ran 6 domain specialists through 3 rounds:

- **Round 1:** Deep research on assigned project areas (6 research notes, ~5,400 lines)
- **Round 2:** Formal execution-ready proposals (6 proposals, ~6,600 lines)
- **Round 3:** Cross-review and integration critique (9 critiques + 1 joint integration
  critique, ~8,950 lines)

**Consensus output:** A portfolio of 3 execution-ready proposals:

| Project | Venue | Compute | Timeline | Status |
|---------|-------|---------|----------|--------|
| Combined Gamma+Alpha-M | Nature Comp Sci | ~110,900 GPU-hrs | 16-18 weeks | Primary target |
| Delta (PerturbMark) | Nature Methods | ~1,070 GPU-hrs | 12 weeks | Parallel track |
| Alpha-M standalone | Nature Methods | ~107,000 GPU-hrs | 14-16 weeks | Fallback |
| Gamma standalone | NCS / Genome Res | ~2,130 GPU-hrs | 14 weeks | Fallback |

**Key finding:** The joint integration critique identified 5 reviewer attack vectors
that are essentially guaranteed to appear in peer review, each with specific probability
estimates (95%, 80%, 75%, 70%, 60%). The critique recommended the combined paper
(Option A) with standalone papers as a pre-planned fallback.

**Unresolved issues requiring arbitration:**
1. Combined vs separate papers: supported by 3/3 joint critique reviewers, but the
   statistical fragility (8-protein integration at N=6 generators) is acknowledged
2. 7 vs 12-15 proteins for Alpha-M: resolved in favor of 7 with per-residue bootstrap,
   but evalstat dissented
3. Title and framing: current titles are descriptively adequate but editorially weak
4. Competitive landscape: last scanned April 14, 2026. The BioEmu + fitness prediction
   combination is an obvious next step that Microsoft Research could publish any day
5. Implementation feasibility: compute budgets estimated but not verified against actual
   software benchmarks (ns/day, GPU memory)

### What This Cohort Must Accomplish

The ReviewCohort transforms Cohort 2's proposals into an implementation-ready plan by:

1. **Mock peer review:** Simulate the NCS review process with 3 mock reviewers (dynamics
   expert, ML expert, statistician) targeting the 5 identified attack vectors
2. **Feasibility audit:** Verify that the proposed simulations can actually run on the
   available hardware within the stated timelines
3. **Competition update:** Fresh scan for preprints, conference submissions, and lab
   activity that may have appeared since Cohort2
4. **Scope arbitration:** Final decisions on protein set size, combined vs separate, and
   method catalog
5. **Implementation plan:** Week-by-week execution plan with resource allocation,
   milestones, and go/no-go criteria

### Why These Agents Were Chosen

The expertise mapping is driven by the 5 reviewer attack vectors and the unresolved
issues from Cohort2:

**Need 1: Address Attack Vectors 2 & 3 (ff14SB bias, trajectory convergence).**
- `dynrev` is a senior MD simulation expert who knows force field validation intimately.
  This agent stress-tests the Alpha-M simulation protocol -- the most compute-intensive
  and technically risky component of the portfolio.

**Need 2: Address Attack Vectors 4 & 5 (standard ML, marginal improvement).**
- `biomlrev` is a senior ML-for-biology expert who has seen too many "dynamics-informed"
  papers with marginal improvements. This agent evaluates whether the Gamma component
  offers genuine novelty or is "connecting two datasets with standard ML."

**Need 3: Address Attack Vector 1 (N=8 too few) and resolve the 7-vs-12 debate.**
- `statrev` is a biostatistician who provides the independent statistical assessment
  that neither evalstat nor scopeadv could provide (they were advocacy agents, not
  neutral arbiters). This agent settles the protein set size debate with power analysis.

**Need 4: Verify implementation feasibility (not addressed by any Cohort2 agent).**
- `implrev` is the only agent in the entire pipeline with HPC engineering expertise.
  Cohort2's agents designed simulations but never verified whether the software actually
  runs, whether GPU memory is sufficient, or whether the compute estimates are accurate.
  This is the gap most likely to cause project failure after the planning phase ends.

**Need 5: Fresh competition scan + scope arbitration + publication strategy.**
- `stratrev` brings the editorial/strategic perspective that scopeadv provided in
  Cohort2, but with the advantage of fresh eyes and updated intelligence. This agent
  makes the final calls on combined vs separate, title, and publication timeline.

---

## Agent Roster

| # | Agent Name | Short Name | Track | Expertise Focus | Assigned Proposals |
|---|-----------|-----------|-------|----------------|-------------------|
| 1 | Protein Dynamics & Force Field Reviewer | dynrev | Senior | MD simulation, NMR validation, convergence, BioEmu | Alpha-M, Combined |
| 2 | Computational Biology & ML Reviewer | biomlrev | Senior | ML for biology, fitness prediction, novelty, baselines | Gamma, Combined, Delta |
| 3 | Statistical Rigor Reviewer | statrev | Senior | Power analysis, multilevel models, pre-registration | All proposals |
| 4 | Technical Implementation Auditor | implrev | Senior | HPC, GPU computing, software readiness, compute budgets | All proposals |
| 5 | Research Strategy Director | stratrev | Maverick | Competition, scope, titles, publication, resource allocation | Portfolio-level |

### Diversity Analysis

- **Track diversity:** 4 Senior + 1 Maverick. Heavy Senior weighting is intentional for
  a review cohort: the goal is rigorous evaluation, not creative ideation. The single
  Maverick (stratrev) provides the strategic and editorial perspective that seniors
  may undervalue.
- **Role diversity:** 3 domain reviewers (dynamics, ML, statistics) + 1 implementation
  expert + 1 strategic director. No redundancy. Each brings expertise that no other
  agent has.
- **Bias mitigation:**
  - **Anchoring on Cohort2 output:** Round 1 is INDEPENDENT review with no cross-
    contamination. Reviewers assess proposals without seeing other reviewers' opinions.
  - **Confirmation bias:** Each reviewer is explicitly instructed to be HOSTILE.
    Their job is to find weaknesses, not validate strengths.
  - **Availability bias:** implrev brings a completely new perspective (HPC engineering)
    not represented in any prior cohort.
  - **Groupthink:** The 4-round protocol ensures reviewers engage with disagreements in
    Round 3, not just converge on a comfortable consensus.
  - **Expert blind spots:** dynrev may overvalue simulation rigor at the expense of
    publication impact; biomlrev may undervalue dynamics because sequence-based methods
    are simpler. statrev provides the neutral statistical arbitration.

---

## Round Protocol

### Round 1: Independent Reviews

**Goal:** Each reviewer independently evaluates the Cohort2 proposals from their
perspective. No cross-contamination ensures independent judgment.

**Agents:** All 5 (two waves: 3 + 2)
**Input:** Cohort2 final proposal set + joint integration critique + mission briefing
**Output:** `ReviewCohort/output/reviews/<shortname>-review-R01.md`
**Template:** `review-assessment.md` or `critique.md` (agent's choice)
**Launch:** Wave 1 (dynrev, biomlrev, statrev) then Wave 2 (implrev, stratrev)

### Round 2: Deep Verification Research

**Goal:** Targeted internet research to verify or refute critical claims from Round 1.
This is the fact-checking round. Each reviewer pursues specific verification tasks
assigned by the orchestrator based on Round 1 findings.

**Agents:** All 5 (two waves: 3 + 2)
**Input:** Round 1 synthesis + all Round 1 reviews + specific verification assignments
**Output:** `ReviewCohort/output/research/<shortname>-verification-R02.md`
**Template:** `research-note.md`
**Launch:** Wave 1 (dynrev, biomlrev, statrev) then Wave 2 (implrev, stratrev)

### Round 3: Cross-Reviewer Deliberation

**Goal:** Reviewers read all prior output and engage with each other's critiques.
They refine positions, resolve disagreements, and produce final assessments.

**Agents:** All 5 (two waves: 3 + 2)
**Input:** All Round 1 reviews + all Round 2 verification reports + Round 1-2 syntheses
**Output:** `ReviewCohort/output/deliberations/<shortname>-deliberation-R03.md`
**Template:** Free-form (but structured by response-to-other-reviewers)
**Launch:** Wave 1 (dynrev, biomlrev, statrev) then Wave 2 (implrev, stratrev)

### Round 4: Final Implementation Plan (Orchestrator Only)

**Goal:** The orchestrator synthesizes all 4 rounds into the definitive implementation
plan. No subagent launches.

**Output:** `ReviewCohort/output/roundtables/final-implementation-plan.md`

This document is the PRIMARY OUTPUT of the entire CompBioSummer2026 pipeline.

---

## Orchestrator Configuration

### Trigger Phrase
**"run the review cohort"** (or: "start the ReviewCohort", "evaluate the proposals",
"run the reviews")

### Input Files
```
Cohort2/output/roundtables/final-proposal-set.md
Cohort2/output/critiques/joint-integration-critique-R03.md
Cohort2/output/roundtables/round01-synthesis.md
Cohort2/output/roundtables/round02-synthesis.md
Cohort2/output/proposals/*.md (all 6 proposals)
Cohort2/output/critiques/*.md (all 9 critiques)
Cohort1/output/roundtables/final-gap-ranking.md
context/mission-briefing.md
templates/review-assessment.md
templates/critique.md
templates/research-note.md
```

### Output Structure
```
ReviewCohort/output/
├── reviews/         (Round 1: 5 independent review assessments)
├── research/        (Round 2: 5 verification research notes)
├── deliberations/   (Round 3: 5 cross-reviewer deliberation notes)
├── roundtables/     (Orchestrator syntheses + final implementation plan)
└── directives/      (Round assignments)
```

---

## Files Created

| # | File Path | Description |
|---|-----------|-------------|
| 1 | `ReviewCohort/agents/orchestrator/CLAUDE.md` | Orchestrator persona and round protocol |
| 2 | `ReviewCohort/agents/dynamics-reviewer/CLAUDE.md` | Mock NCS Reviewer 1 persona |
| 3 | `ReviewCohort/agents/ml-biology-reviewer/CLAUDE.md` | Mock NCS Reviewer 2 persona |
| 4 | `ReviewCohort/agents/statistics-reviewer/CLAUDE.md` | Statistical auditor persona |
| 5 | `ReviewCohort/agents/implementation-auditor/CLAUDE.md` | Technical feasibility auditor persona |
| 6 | `ReviewCohort/agents/strategy-director/CLAUDE.md` | Research strategy director persona |
| 7 | `ReviewCohort/README.md` | Cohort overview and instructions |
| 8 | `ReviewCohort/output/{reviews,research,deliberations,roundtables,directives}/.gitkeep` | Output directories |

---

## Success Criteria

The ReviewCohort succeeds if the final implementation plan contains:

1. **Clear go/no-go for each project** with specific justification
2. **Resolved scope decisions** (combined vs separate, protein set size, method catalog)
   with evidence-based reasoning, not just opinion
3. **Verified feasibility** -- every compute estimate checked, every software dependency
   confirmed available, every timeline adjusted for real-world overhead
4. **Updated competitive intelligence** -- fresh scan confirming the competitive window
   is still open (or flagging new threats with mitigation strategies)
5. **Pre-emption strategies for all 5 attack vectors** -- specific text or analysis that
   can be included in the paper to address each anticipated reviewer concern
6. **Week-by-week execution plan** from May 1, 2026 through November 30, 2026 with
   milestones, go/no-go checkpoints, and contingency plans
7. **Title recommendations** -- at least 3 candidates per paper, tested against NCS/NM
   editorial criteria
8. **Resource allocation** -- GPU-hours per project per month, personnel assignments,
   storage plan
