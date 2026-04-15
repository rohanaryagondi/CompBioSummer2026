# Execution System -- CompBioSummer2026

The Execution system transforms the CompBioSummer2026 research portfolio from plans
into results. It takes the Implementation Plan produced by the ideation pipeline
(Cohort1 -> Cohort2 -> ReviewCohort) and executes it through a three-tier AI agent
hierarchy.

## How It Works

### Three-Tier Hierarchy

```
PlannerAI (plans the work -- documents only, never code)
    |
    v
HeadAIs (manage subphases -- you interact with these directly)
    |
    v
SubAgents (execute tasks -- write code, run experiments, analyze data)
```

**PlannerAI** reads the Implementation Plan and produces detailed phase/subphase
plans one at a time. It creates all the documentation and agent personas that
HeadAIs and SubAgents need. It maintains project dashboards and processes
escalations. It never writes code.

**HeadAIs** are per-subphase managers. You `cd` into a subphase directory and
start Claude. The HeadAI reads its plan, launches SubAgents in waves (max 3
parallel), monitors their output, writes completion reports, and escalates
problems it cannot resolve.

**SubAgents** are task-level executors. They write Python scripts, submit SLURM
jobs, analyze data, and produce figures. Each SubAgent has a narrowly scoped task
with explicit success criteria and file access boundaries.

### The Workflow

```
1. Start PlannerAI:  cd Execution && claude
2. Say: "plan the next phase"
3. PlannerAI reads Implementation Plan, creates phase plan + first subphase
4. Execute subphase: cd phases/phase-N/subphase-N.M && claude
5. HeadAI launches SubAgents, manages waves, writes completion report
6. Return to PlannerAI: cd ../../.. && claude
7. Say: "plan next subphase"
8. Repeat until phase complete
9. Say: "assess gate D[N]" at decision points
10. Say: "plan the next phase" for the next phase
```

### Trigger Phrases (for PlannerAI)

| Trigger | What it does |
|---------|-------------|
| "plan the next phase" | Creates phase plan + first subphase docs |
| "plan next subphase" | Creates next subphase based on prior results |
| "update dashboards" | Refreshes all dashboard files |
| "process escalations" | Reads help-needed docs, adjusts plans |
| "assess gate D[N]" | Evaluates decision gate, writes assessment |

## Directory Layout

```
Execution/
├── CLAUDE.md              # PlannerAI persona
├── README.md              # This file
├── templates/             # 12 document templates
├── dashboards/            # Live project status (5 dashboards)
├── shared/                # Cross-agent communication
│   ├── notes/             # Cross-track findings
│   ├── help-needed/       # Escalation docs
│   └── registry.md        # Master agent list
├── phases/                # Active phase directories
│   └── phase-N/
│       ├── phase-plan.md
│       └── subphase-N.M/
│           ├── CLAUDE.md          # HeadAI persona
│           ├── subphase-plan.md   # Task breakdown
│           ├── tasks/             # Task specifications
│           ├── agents/            # SubAgent personas
│           ├── output/            # Work products
│           ├── status/            # Task status reports
│           └── completion-report.md
└── archive/               # Completed phases
```

## Key Design Principles

1. **Only plan next.** PlannerAI never plans ahead -- each subphase is planned
   after the previous one completes, informed by actual results.

2. **Documentation-first.** Every SubAgent writes a status report. Every HeadAI
   writes a completion report. Any agent can pick up where another left off.

3. **Cross-agent communication.** Shared notes propagate findings across tracks.
   Every HeadAI reads all shared notes before starting.

4. **Structured escalation.** HeadAIs write help-needed docs when blocked.
   PlannerAI processes them and adjusts plans or flags decisions for the human.

5. **Gate-driven decisions.** Seven decision gates (D1-D7) from the Implementation
   Plan are assessed by PlannerAI with specific criteria and fallback strategies.

## The Research Portfolio

| Project | Venue | Compute | Viability |
|---------|-------|---------|-----------|
| Alpha-M (MLFF benchmark) | Nature Methods / NCS | ~166K GPU-hrs | 65-70% |
| Gamma (dynamics-to-fitness) | Genome Research / NCS | ~2K GPU-hrs | 45-50% |
| Delta (perturbation benchmark) | Nature Methods | ~15-20K GPU-hrs | 75-80% |
| Combined (Alpha-M + Gamma) | Nature Comp Sci | (included above) | 30% |

Default strategy: **separation** with conditional recombination at August 31 (gate D6).
