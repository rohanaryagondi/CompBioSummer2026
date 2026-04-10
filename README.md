# CompBioSummer2026 -- Multi-Cohort Research Discovery System

An AI-powered research discovery pipeline that uses sequential cohorts of specialist
agents to identify gaps in computational biology, develop them into ambitious project
proposals, and refine them into publication-ready research plans targeting
**Nature Computational Science**.

---

## How It Works

```
Cohort 1 (Gap Scouts)          Cohort Architect          Cohort 2+ (Designed dynamically)
7 domain specialists    --->   Meta-AI reads output  --> Tailored agents for top gaps
scan comp bio for gaps         designs next cohort        refine gaps into proposals
3-round deep research          writes personas/protocol   deep-dive research + proposals
ranked gap report              creates orchestrator       cross-review + synthesis
                                       |
                                       v
                              Review Cohort (Final)
                              Critique, verify, prioritize
                              --> Final project proposal
```

### Key Innovation: The Cohort Architect

Unlike fixed-roster systems, this pipeline uses a **Cohort Architect** -- a meta-AI
that reads completed cohort output and dynamically designs the next cohort's agent
roster, expertise mix, and round protocol based on what gaps were actually identified.

---

## Quick Start

### Step 1: Run Cohort 1 (Gap Identification)

```bash
cd Cohort1/agents/orchestrator
claude
# Say: "run the gap scouts"
```

This launches 7 specialist agents who scan computational biology for underexplored
gaps through 3 rounds of deep internet research. Output: ranked gap report.

### Step 2: Run the Cohort Architect

```bash
cd CohortArchitect
claude
# Say: "design the next cohort"
```

The Architect reads Cohort 1's output and creates Cohort 2 -- a team of agents
tailored to the specific gaps identified. It writes all persona files, orchestrator
docs, and round protocols.

### Step 3: Run Subsequent Cohorts

```bash
cd Cohort2/agents/orchestrator  # (created by Architect)
claude
# Say: "run the cohort"
```

Repeat Steps 2-3 until the ideas are refined enough for a final review.

### Step 4: Run the Review Cohort

```bash
cd ReviewCohort/agents/orchestrator  # (created by Architect)
claude
# Say: "run the review cohort"
```

The Review Cohort critically evaluates all proposals and produces the definitive
project plan.

---

## Constraints

- **Computational only** -- no wet lab access
- **Lots of compute** -- GPUs (H200, RTX 5000 Ada, B200), CPUs, HPC cluster
- **Open data and tools** -- must use publicly available datasets and open-source software
- **Ambitious** -- targeting Nature Computational Science (impact factor ~12)
- **Timeline** -- Summer 2026

---

## Directory Structure

```
CompBioSummer2026/
├── CLAUDE.md                  # Department-wide rules (all cohorts)
├── README.md                  # This file
├── context/
│   └── mission-briefing.md    # Shared mission context
├── templates/                 # Document templates (6 files)
├── Cohort1/                   # Gap Scouts (7 agents, pre-built)
│   ├── agents/                # Agent personas + orchestrator
│   └── output/                # Research, gaps, roundtables
├── CohortArchitect/           # Meta-AI that designs future cohorts
│   ├── CLAUDE.md              # Architect persona + instructions
│   └── output/                # Cohort designs + rationale
├── Cohort2/                   # (Created by CohortArchitect)
├── Cohort3/                   # (Created by CohortArchitect, if needed)
└── ReviewCohort/              # (Created by CohortArchitect)
```
