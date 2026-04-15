# Cohort 2: Deep Divers

**Purpose:** Take the top gaps identified by Cohort 1 (Gap Scouts) and develop them
into detailed, execution-ready research proposals.

**Focus projects:**
1. **Gamma + Alpha-M** (combined): "From Accurate Ensembles to Biological Function" --
   validate ML force fields against experimental observables, then map validated
   conformational ensembles to biological function via DMS fitness prediction.
   Target: Nature Computational Science.
2. **Delta** (parallel): "PerturbMark -- Resolving the Perturbation Prediction Crisis" --
   definitive cross-context benchmark on Tahoe-100M resolving whether DL beats linear
   baselines. Target: Nature Methods.

---

## Agent Roster

| # | Agent | Short Name | Track | Focus |
|---|-------|-----------|-------|-------|
| 1 | ML Force Field Engineer | mlffeng | Senior | MLFF simulation, OpenMM-ML, compute planning |
| 2 | Biophysical Validation Expert | bioval | Senior | NMR/SAXS data, back-calculation, experimental benchmarks |
| 3 | Ensemble-to-Function Expert | ensfunc | Maverick | BioEmu, ProteinGym, ensemble features to function |
| 4 | Perturbation Biology Expert | pertbio | Senior | Tahoe-100M, perturbation models, benchmark design |
| 5 | Evaluation Methodology Expert | evalstat | Senior | Statistics, cross-validation, ablation, metric design |
| 6 | Scope & Strategy Analyst | scopeadv | Maverick | Competition, scoping, publication strategy, risk |

---

## Round Protocol

| Round | Goal | Output |
|-------|------|--------|
| 1 | Deep research on assigned focus areas | `output/research/` |
| 2 | Formal proposals using proposal template | `output/proposals/` |
| 3 | Cross-review of proposals by 2-3 other agents | `output/critiques/` |
| Final | Orchestrator produces refined proposal set | `output/roundtables/final-proposal-set.md` |

---

## How to Run

```bash
cd Cohort2/agents/orchestrator
claude
```

Then say: **"run the deep divers"**

The orchestrator handles the full 3-round process autonomously.

---

## Input from Cohort 1

This cohort reads:
- `Cohort1/output/roundtables/final-gap-ranking.md`
- `Cohort1/output/roundtables/round02-synthesis.md`
- `Cohort1/output/roundtables/round01-synthesis.md`
- `Cohort1/output/research/*-deep-R02.md` (all deep dives)
- `Cohort1/output/research/*-ranking-R03.md` (all rankings)
- `context/mission-briefing.md`

---

## Output for CohortArchitect

The final output (`output/roundtables/final-proposal-set.md`) serves as input for
the CohortArchitect to design the ReviewCohort (final critical evaluation).
