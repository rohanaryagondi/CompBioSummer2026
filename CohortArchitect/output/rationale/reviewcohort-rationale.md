---
agent: Cohort Architect
date: 2026-04-15
type: rationale
cohort_name: ReviewCohort
---

# ReviewCohort Design Rationale: Why These Agents, Why This Structure

## The Strategic Decision

Cohort 2 produced a well-designed portfolio of 3 execution-ready proposals totaling
~22,500 lines of output with ~630 citations. The proposals have survived hostile
cross-review by 6 specialists across 3 rounds. However, Cohort2 was designed to
DEVELOP proposals, not to independently VERIFY them. The ReviewCohort exists to
provide the independent verification, feasibility assessment, and final arbitration
that Cohort2's advocacy-oriented agents could not.

The key distinction: Cohort2 agents were assigned to projects (mlffeng owned Alpha-M,
ensfunc owned Gamma). Even cross-reviewers (evalstat, scopeadv) had exposure to the
proposals during development, creating familiarity bias. The ReviewCohort sees the
proposals for the FIRST TIME, providing the fresh-eyes evaluation that simulates what
NCS reviewers will experience.

---

## Why 5 Agents, Not 7

The Cohort2 rationale document suggested a ReviewCohort with 5 agents:
- 2 journal reviewers
- 1 senior technical implementer
- 1 junior implementer
- 1 program director

I modified this template based on what Cohort2 actually produced and what needs
independent verification:

### What I Changed

**Replaced "2 journal reviewers" with 3 specialized domain reviewers (dynrev, biomlrev,
statrev).** The joint integration critique identified 5 specific attack vectors, each
requiring different expertise to assess:

| Attack Vector | Required Expertise | Assigned To |
|--------------|-------------------|-------------|
| N=8 too few (95%) | Biostatistics, power analysis | statrev |
| ff14SB bias chain (80%) | MD simulation, force field physics | dynrev |
| 50 ns too short (75%) | Protein dynamics, convergence | dynrev |
| Standard ML, no novelty (70%) | ML for biology, NCS criteria | biomlrev |
| Marginal improvement (60%) | Fitness prediction, benchmarks | biomlrev |

Two generic "journal reviewers" could not cover these 5 vectors as effectively as
3 specialized reviewers. The trade-off is losing one agent slot, which I addressed by:

**Removed "junior implementer."** The Cohort2 rationale suggested both a senior and
junior implementer. I kept only the senior (`implrev`) because:
- The "junior catches details seniors miss" theory sounds good but in practice, a well-
  briefed senior with an implementation focus catches the same details
- The junior implementer role overlaps with implrev's mandate
- Saving one agent slot for the third domain reviewer (statrev) is a better use of
  resources given that the statistical fragility of the integration is the single
  highest-probability attack vector

**Kept the program director as `stratrev` (Maverick).** This is the same role but
with expanded responsibilities: fresh competition scan, title workshop, scope
arbitration, and final implementation plan. The Maverick designation ensures this
agent challenges consensus rather than rubber-stamping it.

---

## Agent Design Decisions

### dynrev: Why a Senior Simulation Expert

Attack vectors 2 (ff14SB bias) and 3 (50 ns convergence) are the most technically
demanding concerns to evaluate. A reviewer who doesn't understand the relationship
between S2 order parameters and tumbling correlation time, or who doesn't know that
NPT MLFF stability is uncharted territory for proteins, would miss critical issues.

I gave dynrev 20+ years of experience because force field validation is a field where
accumulated experience matters enormously. The subtleties of pH-dependent protonation,
water model effects on S2, and integrator choice for MLFFs require decades of domain
knowledge.

dynrev explicitly does NOT review Delta -- perturbation biology is outside their
expertise, and forcing a dynamics expert to comment on single-cell DL models would
produce shallow reviews.

### biomlrev: Why a Senior ML Expert, Not an NCS Editor

I considered making this agent an "NCS editor" persona who evaluates editorial fit.
I chose a domain ML expert instead because:

1. The novelty concern (attack vector 4) requires understanding of what IS and ISN'T
   novel in the fitness prediction landscape. An editor might flag "standard ML" without
   knowing why it's standard. biomlrev knows ESMDance (PNAS 2026) attempted dynamics-
   informed prediction and fell below GEMME -- this specific precedent is critical for
   evaluating Gamma's prospects.

2. The marginal improvement concern (attack vector 5) requires quantitative judgment
   about what Spearman improvements mean in the ProteinGym context. An editor sees
   "0.02 improvement" and may not know whether this is meaningful. biomlrev knows the
   leaderboard and can assess whether the expected improvement is within noise.

3. The editorial perspective is covered by stratrev, who has the former-editor framing.

### statrev: The Neutral Arbiter

This is the most strategically important agent in the ReviewCohort. The Cohort2 debate
between evalstat (who recommended 12-15 proteins) and scopeadv (who recommended 7 with
per-residue bootstrap) was resolved by the orchestrator siding with scopeadv, but
evalstat's concerns were never fully addressed -- they were acknowledged and partially
mitigated.

statrev is designed as a neutral arbiter who has NO stake in either position. This agent
brings fresh statistical expertise to the question: "given the expected effect size
(rho = 0.4-0.6), the proposed sample structure (7 proteins, 420-560 residues, 6
generators), and the analysis plan (cluster bootstrap, multilevel model, Bayesian
signed-rank), what is the actual power and what are the actual confidence interval
widths?"

I made statrev a Senior (not Maverick) because statistical rigor requires discipline,
not creativity. The goal is to compute exact power curves, not to propose novel
statistical frameworks.

### implrev: The Missing Perspective

This is the agent that fills the biggest gap in the entire Cohort1-Cohort2 pipeline.
Neither Cohort1 nor Cohort2 had an agent who checked whether the proposed software
actually installs, whether the GPU memory is sufficient, or whether the compute
estimates are calibrated against real benchmarks.

The gap is critical because:
- MACE-OFF24 via OpenMM-ML has version-matching dependencies (PyTorch + CUDA + OpenMM)
  that can block installation for days
- SO3LR runs on JAX-MD, not OpenMM, requiring a completely separate infrastructure
- AI2BMD uses custom fragmentation that has not been tested by external users at
  production scale
- Tahoe-100M is 429 GB and requires careful memory management to process
- The ~107K GPU-hr estimate for Alpha-M may be off by 2-3x depending on actual ns/day
  performance

implrev is the only agent designed to catch these practical issues. I made them a
Senior because HPC debugging experience is critical -- a junior would know the theory
but not the failure modes.

### stratrev: The Portfolio Optimizer

This agent combines three roles:
1. **Competition scout:** Fresh preprint scan (the landscape may have shifted since
   April 14 when Cohort2 last checked)
2. **Scope arbiter:** Final decisions on combined vs separate, protein set, method
   catalog
3. **Publication strategist:** Title engineering, preprint timing, venue selection

I made stratrev a Maverick because strategic decisions require willingness to override
consensus. If the competitive landscape has shifted (e.g., a BioEmu + ProteinGym
preprint appeared), stratrev needs the authority to recommend a dramatic pivot (e.g.,
"abandon combined paper, rush Alpha-M standalone to preprint").

---

## What I Deliberately Excluded

### No Delta-specific reviewer
Delta (PerturbMark) is the safest project in the portfolio: low compute, clear
differentiation, well-defined scope. It has already been reviewed by 3 Cohort2 agents
(pertbio, evalstat, scopeadv) plus cross-reviewed by ensfunc. Adding a dedicated Delta
reviewer would be redundant. Instead, biomlrev evaluates Delta's ML methodology,
statrev audits its statistical design, implrev checks Tahoe-100M feasibility, and
stratrev updates its competitive position. Four-agent coverage is adequate for Delta.

### No biology-only reviewer
I considered adding a "wet-lab biologist" who evaluates whether the proposed projects
ask biologically meaningful questions. I excluded this because: (a) all projects are
purely computational, (b) the biological significance was extensively discussed in
Cohort1 and Cohort2, and (c) biomlrev has sufficient biological knowledge to evaluate
the fitness prediction framing.

### No additional Maverick/devil's advocate
Cohort2 had scopeadv as a devil's advocate. The ReviewCohort's entire PURPOSE is
devil's advocacy -- all 5 agents are hostile reviewers. An additional "devil's
advocate" would be redundant. The diversity comes from domain specialization, not
from a designated contrarian.

### No data curation specialist
The protein selection and data curation were handled extensively by bioval and ensfunc
in Cohort2. The ReviewCohort trusts this work and focuses on verification (dynrev
spot-checks NMR data availability) rather than re-curation.

---

## Why 4 Rounds, Not 3

Cohort1 and Cohort2 used 3 rounds. The ReviewCohort uses 4 because the review process
has fundamentally different dynamics:

1. **Round 1 (Independent):** Same as Cohort1/2 Round 1, but the task is review rather
   than research. Fresh eyes, no cross-contamination.

2. **Round 2 (Verification):** This round has NO parallel in Cohort1/2. It exists
   because review without verification is just opinion. When dynrev says "MACE-OFF24
   may crash at 50 ns," the next step should be "did anyone test this?" not "noted."
   Round 2 sends reviewers to check their claims against real data.

3. **Round 3 (Deliberation):** Same as Cohort2 Round 3 (cross-review), but the task is
   deliberation among reviewers rather than cross-review of proposals. The goal is
   convergence on recommendations, not additional critiques.

4. **Round 4 (Final Plan):** Orchestrator-only. This has no parallel because previous
   cohorts produced syntheses, not implementation plans. The final implementation plan
   is a different genre: it makes DECISIONS, not SUMMARIES.

---

## Sequential Building: How ReviewCohort Reads Cohort2

Every ReviewCohort reviewer receives:
1. The Cohort2 final proposal set (the primary document under review)
2. The joint integration critique (the most important single document -- contains
   the 5 attack vectors and the integration analysis)
3. Mission briefing context

The orchestrator additionally reads all 6 Cohort2 proposals and all 10 critiques,
embedding relevant context in reviewer prompts as needed. This ensures reviewers have
the FINAL, refined proposals (not earlier drafts) while the orchestrator can reference
the full development history.

---

## Cognitive Bias Mitigation Strategy

| Bias | Risk | Mitigation |
|------|------|-----------|
| Anchoring on Cohort2 output | Reviewers validate rather than challenge | Round 1 is HOSTILE review. Agents are explicitly told to find weaknesses |
| Confirmation bias | Reviewers find evidence supporting Cohort2's conclusions | Each reviewer has a research mandate with specific counter-evidence to find |
| Familiarity effect | Reviewers become sympathetic to proposals after reading them | Round 1 is independent (no cross-contamination). Fresh-eyes design |
| Authority bias | Reviewers defer to Cohort2's 6 specialists | Reviewers are told they outrank Cohort2 agents in this process |
| Groupthink | 5 reviewers converge on comfortable consensus | Round 3 deliberation requires EXPLICIT engagement with disagreements |
| Expert blind spots | dynrev overvalues rigor, biomlrev undervalues dynamics | Deliberation forces domain experts to engage with each other's critiques |

---

## What Comes After the ReviewCohort

The ReviewCohort is the FINAL cohort. Its output -- the implementation plan -- is the
document that the human operator uses to begin execution. There is no further cohort
design needed.

If the implementation plan reveals that a project needs redesign (e.g., "abandon
Gamma, design a new project around Delta + ContextVEP"), the CohortArchitect would
design a new specialist cohort. But this is a contingency, not an expected outcome.

The expected outcome is: the implementation plan confirms the portfolio with specific
modifications, and execution begins in May 2026.
