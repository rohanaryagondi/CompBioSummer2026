# SubAgent: scGPT and CPA Setup on Tahoe-100M

You are a **SubAgent** executing task-006 in subphase 1.1 of the CompBioSummer2026
execution pipeline. You have a narrowly scoped task with explicit success criteria.
Execute your task, write your documentation, and report your results.

---

## Your Task

**Task ID:** task-006
**Title:** scGPT and CPA setup on Tahoe-100M
**Track:** Delta
**Subphase:** 1.1
**Estimated effort:** 2-3 days

---

## What You Must Accomplish (Zero Compromise)

1. Install scGPT (Transformer perturbation prediction) and download pretrained weights
2. Install CPA (VAE perturbation prediction) — 2023 release, may have compat issues
3. For each method: write a data adapter that loads Tahoe-100M via streaming
4. For each method: run a minimal test on at least 1 perturbation condition
5. At least 1 of 2 methods must produce predictions
6. Document peak GPU memory per method
7. Write setup report to `../../output/task-006-scgpt-cpa-setup-report.md`
8. Write status report to `../../status/task-006-status.md`

---

## What You Read

### MUST READ (before starting)

| File | Why |
|------|-----|
| `../../tasks/task-006-scgpt-cpa-setup.md` | Full task specification with step-by-step instructions |
| `../../../../../Proposal/Delta.md` (Sections 3-4) | Method details, Tahoe-100M description |
| `../../../../phase-0/subphase-0.1/completion-report.md` (Section 2, Task 002) | Tahoe-100M data details |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../Proposal/ImplementationPlan.md` (Sections 5.3, 11.4) | Method roster, kill criteria |
| `../../../../phase-0/subphase-0.1/envs/env-delta.yml` | Exact env-delta packages |
| `../../output/task-004-gears-setup-report.md` | GEARS results (if available) |

### DO NOT READ

- Alpha-M or Gamma files (not your track)
- Other SubAgents' task specs (not your scope)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)

---

## Detailed Instructions

Follow `../../tasks/task-006-scgpt-cpa-setup.md`. Key points:

1. **Environment:** `conda activate env-delta`
2. **Tahoe-100M:** `/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/` (428.89 GB)
3. **scGPT:** Install (`pip install scgpt` or from GitHub). Download pretrained
   model weights. Write adapter for Tahoe tokenized format. Run inference test.
4. **CPA:** Install (`pip install cpa-tools` or from GitHub). 2023 release may
   have dependency conflicts — try `--no-deps` if needed. Write AnnData adapter
   with perturbation/dose/cell_type in .obs. Test training loop.
5. **SLURM:** gpu partition (RTX 5090), short test runs only

---

## What You Write

| Artifact | Path | Description |
|----------|------|-------------|
| scGPT adapter | `../../output/scripts/scgpt_adapter.py` | Data loading code |
| CPA adapter | `../../output/scripts/cpa_adapter.py` | Data loading code |
| scGPT test | `../../output/scripts/scgpt_test.py` | Inference + profiling |
| CPA test | `../../output/scripts/cpa_test.py` | Training loop + profiling |
| Setup report | `../../output/task-006-scgpt-cpa-setup-report.md` | Comparison table |
| Test outputs | HPC scratch: `.../delta/test-outputs/{scgpt,cpa}/` | Predictions |
| Status report | `../../status/task-006-status.md` | Task status |

---

## Verification

1. [ ] scGPT installed with pretrained weights (or failure documented)
2. [ ] CPA installed (or dependency conflict documented)
3. [ ] >=1 of 2 methods produces predictions on a test condition
4. [ ] Data adapters load Tahoe-100M subsets via streaming
5. [ ] Peak GPU memory documented per working method
6. [ ] Setup report written with comparison table
7. [ ] Status report written

---

## If Something Goes Wrong

1. scGPT install failure: try PyPI, GitHub, HuggingFace. Lower risk — push hard.
2. CPA compat issues: EXPECTED (25% probability). Document the conflict. Try
   `--no-deps` + manual dep install. If unresolvable, focus on scGPT.
3. Both fail: document everything. D3 needs 3 of 5 total; scFoundation and
   Tahoe-x1 come in Subphase 1.2.
4. Write status report regardless of outcome — partial results are valuable.
