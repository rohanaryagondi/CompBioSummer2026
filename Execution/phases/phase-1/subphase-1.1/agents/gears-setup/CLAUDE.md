# SubAgent: GEARS Setup on Tahoe-100M

You are a **SubAgent** executing task-004 in subphase 1.1 of the CompBioSummer2026
execution pipeline. You have a narrowly scoped task with explicit success criteria.
Execute your task, write your documentation, and report your results.

---

## Your Task

**Task ID:** task-004
**Title:** GEARS setup on Tahoe-100M
**Track:** Delta
**Subphase:** 1.1
**Estimated effort:** 2-3 days

---

## What You Must Accomplish (Zero Compromise)

1. Install GEARS (GNN perturbation prediction method) in env-delta
2. Write a data adapter that loads Tahoe-100M subsets via streaming into GEARS format
3. Run a minimal test on at least 1 perturbation condition
4. Profile GPU memory at each stage (data load, model init, forward pass)
5. If OOM: document the maximum feasible cell count — this IS the key deliverable
6. Write setup report to `../../output/task-004-gears-setup-report.md`
7. Write status report to `../../status/task-004-status.md`

**GEARS has a 30% OOM risk.** If it OOMs, your job is to find the ceiling, not
to declare failure. Document max feasible cells at 10K/20K/50K/100K thresholds.

---

## What You Read

### MUST READ (before starting)

| File | Why |
|------|-----|
| `../../tasks/task-004-gears-setup.md` | Full task specification with step-by-step instructions |
| `../../../../../Proposal/Delta.md` (Sections 3-4) | GEARS context, Tahoe-100M description |
| `../../../../phase-0/subphase-0.1/completion-report.md` (Section 2, Task 002) | Tahoe-100M data details |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../Proposal/ImplementationPlan.md` (Sections 5.3, 11.4) | Method roster, kill criteria |
| `../../../../phase-0/subphase-0.1/envs/env-delta.yml` | Exact env-delta packages |

### DO NOT READ

- Alpha-M or Gamma files (not your track)
- Other SubAgents' task specs or output (not your scope)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)

---

## Detailed Instructions

Follow `../../tasks/task-004-gears-setup.md`. Key points:

1. **Environment:** `conda activate env-delta`
2. **Tahoe-100M:** `/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/` (428.89 GB)
3. **Install:** `pip install git+https://github.com/snap-stanford/GEARS.git`
4. **Data adapter:** Tahoe parquet -> AnnData with perturbation labels for GEARS
5. **Test:** Forward pass on 1 perturbation condition, then a few training iterations
6. **Memory profile:** Log GPU memory at every stage. Find OOM ceiling if needed.
7. **SLURM:** gpu partition (RTX 5090), short test run only

---

## What You Write

| Artifact | Path | Description |
|----------|------|-------------|
| Data adapter | `../../output/scripts/gears_adapter.py` | Tahoe -> GEARS loading code |
| Test script | `../../output/scripts/gears_test.py` | Forward pass + memory profiling |
| Setup report | `../../output/task-004-gears-setup-report.md` | Results table |
| Test outputs | HPC scratch: `.../delta/test-outputs/gears/` | Model predictions |
| Status report | `../../status/task-004-status.md` | Task status |

---

## Verification

1. [ ] GEARS installed (or failure documented with exact error after 2+ attempts)
2. [ ] Data adapter loads Tahoe-100M subset via streaming
3. [ ] Forward pass produces predictions (or OOM ceiling documented)
4. [ ] Peak GPU memory documented at each stage
5. [ ] Setup report written with all metrics
6. [ ] Status report written

---

## If Something Goes Wrong

1. Install failure: try pinned version, manual clone + editable install, then document
2. OOM: this is EXPECTED. Find the ceiling (10K -> 20K -> 50K -> 100K cells). Try
   gradient checkpointing and mixed precision. Document max feasible size.
3. Data format mismatch: document the schema gap, write partial adapter
4. Even partial results are valuable — document everything for Subphase 1.3 planning
