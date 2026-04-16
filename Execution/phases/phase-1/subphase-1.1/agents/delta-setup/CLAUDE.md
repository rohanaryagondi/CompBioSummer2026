# SubAgent: Delta Method Setup (GEARS, scGPT, CPA)

You are a **SubAgent** executing task-004 in subphase 1.1 of the CompBioSummer2026
execution pipeline. You have a narrowly scoped task with explicit success criteria.
Execute your task, write your documentation, and report your results.

---

## Your Task

**Task ID:** task-004
**Title:** Delta method setup (GEARS, scGPT, CPA)
**Track:** Delta
**Subphase:** 1.1
**Estimated effort:** 3-5 days

---

## What You Must Accomplish (Zero Compromise)

1. Install GEARS, scGPT, and CPA in env-delta
2. For each method: write a data adapter that loads Tahoe-100M via scDataset streaming
3. For each method: run a minimal test on at least 1 perturbation condition
4. Document peak GPU memory per method
5. >=2 of 3 methods must produce predictions (1 failure is acceptable)
6. Write method setup report with comparison table
7. Write status report to `../../status/task-004-status.md`

---

## What You Read

### MUST READ (before starting)

| File | Why |
|------|-----|
| `../../tasks/task-004-delta-method-setup.md` | Full task specification |
| `../../../../../Proposal/Delta.md` (Sections 3-4) | Method details, Tahoe-100M |
| `../../../../phase-0/subphase-0.1/completion-report.md` (Section 2, Task 002) | Tahoe-100M data details |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../Proposal/ImplementationPlan.md` (Sections 5.3, 11.4) | Method roster, kill criteria |
| `../../../../phase-0/subphase-0.1/envs/env-delta.yml` | Exact env-delta packages |

### DO NOT READ

- Alpha-M or Gamma files (not your track)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)

---

## Detailed Instructions

Follow `../../tasks/task-004-delta-method-setup.md`. Key points:

1. **Environment:** `conda activate env-delta`
2. **Tahoe-100M:** `/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/` (428.89 GB)
3. **GEARS:** Install from GitHub. Known 30% OOM risk. Use scDataset streaming.
4. **scGPT:** Install + download pretrained model weights. Run inference test.
5. **CPA:** Install (2023 release, may have compat issues). Test training loop.
6. **For all:** Write data adapters (Tahoe parquet -> method input format)
7. **SLURM:** gpu partition (RTX 5090), short test runs only

---

## What You Write

| Artifact | Path | Description |
|----------|------|-------------|
| GEARS adapter | `../../output/scripts/gears_adapter.py` | Data loading code |
| scGPT adapter | `../../output/scripts/scgpt_adapter.py` | Data loading code |
| CPA adapter | `../../output/scripts/cpa_adapter.py` | Data loading code |
| Setup report | `../../output/task-004-method-setup-report.md` | Comparison table |
| Test outputs | HPC scratch: `.../delta/test-outputs/` | Method predictions |
| Status report | `../../status/task-004-status.md` | Task status |

---

## Verification

1. [ ] >=2 of 3 methods installed and produce predictions
2. [ ] Data adapters load Tahoe-100M subsets for each working method
3. [ ] Peak GPU memory documented per method
4. [ ] Setup report has comparison table
5. [ ] Status report written

---

## If Something Goes Wrong

1. Method install failure: try 2 alternative approaches, then document as failed
2. GEARS OOM: cap cells at 10K, 50K, 100K — document max feasible size
3. CPA compat issues: expected. Document and proceed with other 2 methods.
4. Even 1 working method is progress — document everything for Subphase 1.2
