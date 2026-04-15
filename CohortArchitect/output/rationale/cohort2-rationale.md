---
agent: Cohort Architect
date: 2026-04-14
type: rationale
cohort_name: Cohort2
---

# Cohort 2 Design Rationale: Why These Agents, Why This Structure

## The Strategic Decision

Cohort 1 produced a clear recommendation: combine Gamma (Dynamics-to-Function) with
Alpha-M (MLFF Crash Test) as the primary Nature Computational Science submission, and
run Delta (PerturbMark) in parallel as a fast-track Nature Methods publication. The
question for the CohortArchitect is: what team composition optimally develops these
ideas into execution-ready proposals?

---

## Why 6 Agents, Not 7

Cohort 1 used 7 specialists for broad scanning across all of computational biology.
Cohort 2 is more focused: it develops 3 specific projects (2 linked, 1 parallel).
The expertise requirements are well-defined, and 6 agents cover them without redundancy:

- 2 agents for Alpha-M (it's the most technically complex, requiring both simulation
  engineering and experimental validation expertise)
- 1 agent for Gamma (BioEmu + ProteinGym is a cleaner, more self-contained design problem)
- 1 agent for Delta (PerturbMark is computationally simple but methodologically nuanced)
- 2 agents for cross-cutting concerns (evaluation methodology and strategic scoping)

A 7th agent would create redundancy. I considered adding a "protein biologist" who
understands the biological significance of each target protein, but this perspective
is adequately covered by `bioval` (who knows the experimental literature) and `ensfunc`
(who knows the DMS data landscape). Adding a separate biology agent would split expertise
without adding unique knowledge.

---

## Agent Design Decisions

### mlffeng: Why a Simulation Engineer, Not a Force Field Theorist

The Alpha-M project's risk profile is dominated by ENGINEERING challenges, not theoretical
ones: Can each MLFF actually run stable 50 ns trajectories on folded proteins? Are the
OpenMM-ML integrations production-ready? How do you handle different MLFFs' incompatible
atom typing schemes? Can you schedule 180K GPU-hours efficiently on SLURM?

A force field theorist would focus on the physics of equivariant message-passing or the
training loss landscape. `mlffeng` focuses on the practical question: will this simulation
produce a usable trajectory?

I made `mlffeng` a Senior because this person needs deep experience with MD simulation
failure modes. A junior engineer would miss subtle issues like equilibration artifacts,
integrator instabilities at long timesteps, or solvation model incompatibilities.

### bioval: Why a Separate Validation Expert

The temptation was to fold experimental validation into `mlffeng`. I chose to separate
them because the validation layer requires DIFFERENT expertise:

- `mlffeng` knows how to RUN simulations. `bioval` knows how to EVALUATE them against
  experiment.
- NMR back-calculation (SPARTA+, ShiftX2) has its own pitfalls: intrinsic prediction
  error (~1.1 ppm for 13Cα), temperature dependence, pH sensitivity, reference
  chemical shifts.
- SAXS fitting (FOXS, Pepsi-SAXS) has different pitfalls: buffer subtraction, q-range
  selection, concentration effects.
- The protein selection task -- finding 15+ proteins with comprehensive NMR + SAXS data --
  requires someone who knows BMRB and SASBDB intimately.

Splitting these roles also creates a natural check: `bioval` will critique `mlffeng`'s
simulation protocol from the experimentalist's perspective, catching issues that a
simulation-focused engineer would miss.

### ensfunc: Why a Maverick

The Gamma project requires the most creative design work. The key questions are open-ended:
- Which ensemble features predict function? (Nobody knows yet.)
- How should the ML framework be designed? (Multiple valid architectures.)
- How do you handle the BioEmu mutation-sensitivity limitation? (Requires a creative
  workaround.)
- Which ProteinGym assay types will show ensemble signal? (Requires biological intuition.)

A Senior would bring deep expertise in one approach. A Maverick brings willingness to
try unconventional feature representations, combine methods from different fields (e.g.,
graph neural networks on contact frequency matrices, or information-theoretic measures
from MD), and propose the "wildtype ensemble hypothesis" as an alternative to
variant-specific ensembles.

### pertbio: Why a Senior

Delta (PerturbMark) is less about creative design and more about rigorous execution:
the DL-vs-linear debate has specific methods, specific datasets, and a specific
controversy to resolve. A Senior who knows the perturbation prediction literature deeply
-- including the exact claims and counter-claims in Ahlmann-Eltze vs Cole et al. -- will
design a benchmark that definitively resolves the dispute. The risk is not missing
creativity; it's missing a confound that invalidates the result.

### evalstat: The Hostile Reviewer

This agent exists because benchmark papers live or die on their evaluation methodology.
If a Nature Computational Science reviewer finds a statistical flaw (leaky cross-validation,
inadequate baseline, cherry-picked metric), the paper is dead. `evalstat` plays this
role proactively: find the flaws before submission.

I made `evalstat` a Senior because statistical rigor requires decades of experience.
A junior statistician might apply standard tests without recognizing that the data
violates the test's assumptions.

### scopeadv: The Devil's Advocate

This is the most unusual agent in the roster. Its job is to CHALLENGE the team's plans:

- Is the competitive window actually 6-18 months, or is Microsoft about to publish?
- Is Nature Comp Sci realistic, or should we target Nature Methods?
- Can the combined Gamma + Alpha-M project really finish in one summer?
- What happens if BioEmu ensembles show zero signal for fitness prediction?

I made `scopeadv` a Maverick because this role requires willingness to disagree with
consensus and ask uncomfortable questions. A Senior might defer to domain experts;
a Maverick will push back.

The "former journal editor" framing is deliberate: `scopeadv` reads proposals the way
an editor reads submissions, looking for the fatal flaw that makes them say "reject
without review."

---

## What I Deliberately Excluded

### No wet-lab liaison
All projects are purely computational. A wet-lab perspective would waste agent capacity
on constraints that don't apply.

### No pure ML/DL architecture expert
Cohort 1's `aiml` agent provided useful perspective on evaluation methodology, but
Cohort 2's ML needs are specific to each project (ensemble ML for Gamma, not generic
ML). `ensfunc` and `pertbio` each have the ML knowledge relevant to their projects.
A separate ML expert would provide generic advice that doesn't help with specific
design decisions.

### No ContextVEP or LiveBioBench specialists
Cohort 1's ranking placed Beta (ContextVEP) at 8.17 and Alpha-L (LiveBioBench) at 7.99.
Both are strong projects, but the strategic decision is to focus Cohort 2 on the top
recommendations (Gamma + Alpha-M + Delta). ContextVEP could become a secondary project
if Gamma or Delta finishes early, but designing agents for it now would dilute Cohort 2's
focus.

### No separate protein selection agent
I considered a "Data Curation Specialist" who selects the protein benchmark set. This
task is better split between `bioval` (who knows the experimental data landscape) and
`ensfunc` (who knows the ProteinGym landscape). A separate curation agent would need
input from both and would add a communication overhead without adding unique expertise.

---

## Sequential Building: How Cohort 2 Reads Cohort 1

Every Cohort 2 agent receives in its prompt:
1. The full Cohort 1 final gap ranking (consensus scores, project descriptions)
2. The Round 2 synthesis (feasibility verification, compute estimates, competition)
3. Their relevant Cohort 1 deep-dive reports (e.g., `mlffeng` gets `multisim-deep-R02.md`)

This ensures Cohort 2 BUILDS ON Cohort 1's work rather than repeating it. The
orchestrator is responsible for embedding the right Cohort 1 context in each prompt.

---

## Cognitive Bias Mitigation Strategy

| Bias | Risk | Mitigation |
|------|------|-----------|
| Anchoring on Cohort 1 scores | Agents treat Cohort 1 rankings as fixed | `scopeadv` explicitly challenges Cohort 1 framing |
| Confirmation bias | Agents find evidence supporting their assigned project | `evalstat` requires negative result reporting; `scopeadv` tests kill criteria |
| Sunk cost | Team commits to failing project mid-summer | `scopeadv` defines kill criteria BEFORE work starts |
| Groupthink | All agents converge on same recommendation | Cross-review in Round 3 forces explicit disagreement |
| Domain bias | Structural biology dominates (3 agents) | `evalstat` + `scopeadv` evaluate all three projects equally |
| Optimism bias | Compute/timeline estimates are too aggressive | `mlffeng` provides ground-truth compute estimates; `scopeadv` stress-tests timelines |

---

## What Comes After Cohort 2

If Cohort 2 succeeds, the CohortArchitect should design a **ReviewCohort** with:
- 2 journal reviewers (Nature Comp Sci / Nature Methods editorial board perspective)
- 1 senior technical implementer (catches execution risks)
- 1 junior implementer (catches practical details)
- 1 program director (prioritizes across projects, allocates resources)

The ReviewCohort would evaluate Cohort 2's final proposals and produce the definitive
implementation plan for summer 2026.
