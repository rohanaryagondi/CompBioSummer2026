---
agent: Cohort Architect
date: 2026-04-14
type: cohort-design
cohort_name: Cohort2
based_on: Cohort1 gap reports, deep dives, rankings, and final synthesis
---

# Cohort Design: Cohort2 -- Deep Divers

## Design Rationale

### What the Previous Cohort Produced

Cohort 1 (Gap Scouts) ran 7 domain specialists through 3 rounds:

- **Round 1:** 33 gaps identified across 7 domains of computational biology
- **Round 2:** Top 10 gaps deep-dived for feasibility, data availability, compute
  requirements, and competitive landscape
- **Round 3:** All 7 specialists independently ranked 6 combined projects on novelty,
  impact, feasibility, timeline, and publication potential

**Consensus output:** A ranked list of 6 combined projects, with clear recommendations:

| Rank | Project | Score | Target Venue |
|------|---------|-------|-------------|
| 1 | Delta: PerturbMark | 8.64 | Nature Methods |
| 2 | Gamma: Dynamics-to-Function | 8.30 | Nature Comp Sci |
| 3 | Beta: ContextVEP | 8.17 | Nat Comp Sci / Nat Genetics |
| 4 | Alpha-L: LiveBioBench | 7.99 | Nature Comp Sci |
| 5 | Alpha-M: MLFF Crash Test | 7.74 | Nature Comp Sci |
| 6 | Alpha-G: Molecular Design Bench | 7.10 | J Chem Inf Model |

**Key finding:** 4 of 7 specialists independently voted for Alpha-M + Gamma as the
best combination, calling it "deeply intellectually coherent" with a shared thesis:
computational representations of protein dynamics are advancing faster than our ability
to validate them against experiment or connect them to function.

**Strategic recommendation:** Pursue Gamma + Alpha-M as a combined Nature Comp Sci
paper, with Delta as a parallel fast-track Nature Methods publication.

### What This Cohort Must Accomplish

Cohort 2 transforms Cohort 1's gap identification into execution-ready proposals:

1. **For Gamma + Alpha-M combined:** Design the full research protocol -- which MLFFs,
   which proteins, which experimental observables, which ensemble features, which ML
   framework for function prediction, exact compute budget, timeline, publication narrative
2. **For Delta (PerturbMark):** Design the benchmark specification -- which difficulty
   tiers, which methods, which datasets (Tahoe-100M integration), which metrics, how to
   differentiate from scPerturBench
3. **Cross-project integration:** Ensure the three projects can execute in parallel
   without competing for compute, and that each is scoped to be achievable in summer 2026
4. **Risk assessment:** Identify kill criteria, contingency plans, and worst-case scenarios

### Why These Agents Were Chosen

The expertise mapping is driven by three needs:

**Need 1: Alpha-M requires two complementary specialists.**
- `mlffeng` brings hands-on MLFF engineering expertise (which force fields work, how to
  run them, what breaks, compute requirements)
- `bioval` brings experimental data expertise (which proteins have rich NMR/SAXS data,
  how to do back-calculation correctly, what the error bars mean)
- These two agents must work together to produce a single coherent Alpha-M proposal

**Need 2: Gamma requires a specialist who bridges ensemble generation and function prediction.**
- `ensfunc` combines BioEmu expertise with ProteinGym knowledge and ML feature engineering
- This agent must independently assess BioEmu's limitations (Aryal et al., 2025 mutation
  sensitivity failure) and design around them

**Need 3: Delta requires a perturbation biology specialist.**
- `pertbio` brings comprehensive knowledge of the DL-vs-linear controversy, all the
  relevant methods, and the untapped Tahoe-100M dataset
- Must differentiate from scPerturBench (Nature Methods, Feb 2026)

**Need 4: Cross-cutting quality control.**
- `evalstat` ensures all three proposals have bulletproof evaluation methodology
- `scopeadv` ensures all three proposals are competitively positioned and correctly scoped

---

## Agent Roster

| # | Agent Name | Short Name | Track | Expertise Focus | Assigned Projects |
|---|-----------|-----------|-------|----------------|-------------------|
| 1 | ML Force Field Engineer | mlffeng | Senior | MLFF simulation, OpenMM-ML, compute | Alpha-M |
| 2 | Biophysical Validation Expert | bioval | Senior | NMR/SAXS data, back-calculation | Alpha-M |
| 3 | Ensemble-to-Function Expert | ensfunc | Maverick | BioEmu, ProteinGym, ensemble ML | Gamma |
| 4 | Perturbation Biology Expert | pertbio | Senior | Perturbation models, Tahoe-100M | Delta |
| 5 | Evaluation Methodology Expert | evalstat | Senior | Statistics, benchmarks, metrics | All three |
| 6 | Scope & Strategy Analyst | scopeadv | Maverick | Competition, publication, risk | All three |

### Diversity Analysis

- **Track diversity:** 4 Senior + 2 Maverick. Seniors bring depth and rigor; Mavericks
  bring cross-domain thinking and challenge assumptions.
- **Role diversity:** 2 domain experts for the primary project (Alpha-M), 1 domain expert
  each for Gamma and Delta, 1 methodologist, 1 strategist. No redundancy.
- **Bias mitigation:**
  - **Anchoring:** `scopeadv` explicitly challenges the Cohort 1 framing. The Maverick
    track means it is designed to push back on consensus.
  - **Confirmation bias:** `evalstat` requires negative results to be reported and designs
    tests to falsify claims, not just confirm them.
  - **Sunk cost:** `scopeadv` defines kill criteria before projects start, preventing
    commitment to failing approaches.
  - **Domain bias:** `evalstat` and `scopeadv` evaluate across all three projects, ensuring
    no single domain dominates the recommendations.

---

## Round Protocol

### Round 1: Deep Research

**Goal:** Each specialist researches their focus area in depth, extending Cohort 1's
findings with new data, tools, and competitive intelligence.

**Agents:** All 6 (two waves of 3)
**Input:** All Cohort 1 output + mission briefing
**Output:** `Cohort2/output/research/<shortname>-*-R01.md`
**Launch:** Parallel (Wave 1: mlffeng, ensfunc, pertbio; Wave 2: bioval, evalstat, scopeadv)

### Round 2: Formal Proposals

**Goal:** Produce detailed, execution-ready proposals using the proposal template.

**Agents:** All 6 (two waves of 3)
**Input:** Round 1 synthesis + all Round 1 research notes
**Output:** `Cohort2/output/proposals/<shortname>-*-R02.md`
**Launch:** Parallel (Wave 1: mlffeng, ensfunc, pertbio; Wave 2: bioval, evalstat, scopeadv)

### Round 3: Cross-Review

**Goal:** Each proposal reviewed by 2-3 other agents for weaknesses and improvements.

**Agents:** All 6, assigned as reviewers of proposals outside their primary domain
**Input:** Round 2 synthesis + all Round 2 proposals
**Output:** `Cohort2/output/critiques/<reviewer>-reviews-<proposer>-R03.md`
**Launch:** Parallel (three waves of 3)

### Final Output

The orchestrator produces:
- `Cohort2/output/roundtables/final-proposal-set.md`: Definitive proposals with all
  reviewer modifications incorporated

---

## Orchestrator Configuration

### Trigger Phrase
**"run the deep divers"** (or: "Start Cohort2", "run the proposals", "develop the proposals")

### Input Files
```
Cohort1/output/roundtables/final-gap-ranking.md
Cohort1/output/roundtables/round02-synthesis.md
Cohort1/output/roundtables/round01-synthesis.md
Cohort1/output/research/*-deep-R02.md
Cohort1/output/research/*-ranking-R03.md
context/mission-briefing.md
templates/proposal.md
templates/critique.md
templates/research-note.md
```

### Output Structure
```
Cohort2/output/
├── research/         (Round 1: 6 deep research notes)
├── proposals/        (Round 2: 6 formal proposals)
├── critiques/        (Round 3: ~9 cross-reviews)
├── roundtables/      (Orchestrator syntheses + final proposal set)
└── directives/       (Round assignments)
```

---

## Files Created

| # | File Path | Description |
|---|-----------|-------------|
| 1 | `Cohort2/agents/orchestrator/CLAUDE.md` | Orchestrator persona and round protocol |
| 2 | `Cohort2/agents/mlff-engineer/CLAUDE.md` | ML Force Field Engineer persona |
| 3 | `Cohort2/agents/biophysical-validation/CLAUDE.md` | Biophysical Validation Expert persona |
| 4 | `Cohort2/agents/ensemble-function/CLAUDE.md` | Ensemble-to-Function Expert persona |
| 5 | `Cohort2/agents/perturbation-biology/CLAUDE.md` | Perturbation Biology Expert persona |
| 6 | `Cohort2/agents/evaluation-methodology/CLAUDE.md` | Evaluation Methodology Expert persona |
| 7 | `Cohort2/agents/scope-strategy/CLAUDE.md` | Scope & Strategy Analyst persona |
| 8 | `Cohort2/README.md` | Cohort overview and instructions |
| 9 | `Cohort2/output/{research,proposals,critiques,roundtables,directives}/.gitkeep` | Output directories |

---

## Success Criteria

Cohort 2 succeeds if the final proposal set contains:

1. **For Gamma + Alpha-M combined:** A single coherent proposal with:
   - Exact protein list (15+ proteins with PDB IDs, BMRB entries, SAXS data, ProteinGym coverage)
   - MLFF simulation protocol (which MLFFs, timestep, thermostat, run length, replicas)
   - Ensemble feature extraction pipeline (which features, how computed)
   - ML framework for fitness prediction (architecture, cross-validation, baselines)
   - Compute budget within available HPC capacity
   - Timeline fitting summer 2026
   - Publication narrative for Nature Computational Science
   - Kill criteria and contingency plans

2. **For Delta:** A standalone benchmark specification with:
   - Tahoe-100M integration plan (which cell lines, which perturbations, cross-context splits)
   - Method catalog (10+ methods with availability and compute requirements)
   - Metric suite with calibration controls
   - Differentiation from scPerturBench
   - Publication narrative for Nature Methods

3. **Cross-project:** A parallel execution plan showing how all three can run simultaneously
   within the available compute budget and summer 2026 timeline.
