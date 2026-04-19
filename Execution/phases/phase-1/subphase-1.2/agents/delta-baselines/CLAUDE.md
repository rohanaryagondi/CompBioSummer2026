# SubAgent: Delta 5 Baselines + WMSE Evaluation Harness

You are a **SubAgent** executing task-005 in subphase 1.2 of the CompBioSummer2026
execution pipeline. You have a narrowly scoped task with explicit success criteria.
Execute your task, write your documentation, and report your results.

---

## Your Task

**Task ID:** task-005
**Title:** Delta 5 baselines + WMSE evaluation harness
**Track:** Delta
**Subphase:** 1.2
**Estimated effort:** 7-10 days, ~30 GPU-hrs RTX 5000 Ada, ~450 SU

**This task fully retires the D3 gate.** D3 was upgraded CONDITIONAL → GO on
2026-04-17 contingent on this baselines work. Completing it eliminates the
last outstanding D3 criterion.

---

## What You Must Accomplish (Zero Compromise)

1. Implement 5 baselines per IP §5.3 + §12.4 at `../../output/scripts/delta/baselines/`:
   `linear.py`, `mean.py`, `pca.py`, `random.py`, `persistence.py`
2. Implement WMSE harness at `../../output/scripts/delta/eval/wmse.py` with
   `hierarchical_wmse_spearman` function (WMSE gates Spearman on top-k DEGs).
3. Implement FDR (`fdr.py`: BH primary, BY sensitivity), calibration
   (`calibration.py`: reliability diagram, ECE), stratified eval (`stratified.py`:
   per cell type × perturbation type × expression level).
4. Run end-to-end smoke test on ≥1M-cell Tahoe-100M subsample (or 100K fallback).
   Test all 5 baselines + ≥1 method (GEARS).
5. Random baseline MUST FAIL the WMSE gate (validates the calibration test).
6. Write `delta_baselines_results.md` with results table.
7. Cross-agent note `1.2-delta-baselines-results.md`.
8. Status report at `../../status/task-005-status.md`.

---

## What You Read

### MUST READ (before starting)

| File | Why |
|------|-----|
| `../../tasks/task-005-delta-baselines.md` | Your full task specification |
| `../../../../../shared/notes/1.1-delta-methods-install.md` | Env paths, adapter locations, smoke test patterns |
| `../../../../../shared/notes/1.1-env-split.md` | env-delta-v2 vs env-cpa vs env-tahoex1 mapping |
| `../../../../../shared/notes/operational-practices.md` | RTX 5000 Ada policy, env hygiene |
| `../../../subphase-1.1/output/delta-tier1/gears_adapter.py` | Reusable adapter for Tahoe-100M |
| `../../../subphase-1.1/output/delta-tier1/scgpt_adapter.py` | scGPT adapter |
| `../../../../../../Proposal/Delta.md` | §3 Tahoe-100M, §4 methods, §12 stats |
| `../../../../../../Proposal/ImplementationPlan.md` | §5.3 baselines spec, §12.4 WMSE harness spec |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../shared/notes/1.2-scope-recommendations.md` | Items 14-17, 24 are explicit scope for this task |
| `../../../subphase-1.1/output/delta-tier1/scfoundation_smoketest.py` | Pattern for HuggingFace model loading |
| `../../../subphase-1.1/output/delta-tier1/tahoex1_smoketest.py` | Tahoe-x1 pattern (env-tahoex1) |

### DO NOT READ

- Other SubAgents' task specs
- `../../../../../../Proposal/HumanOnlyProposal.md`
- Future subphase plans

---

## Detailed Instructions

See `../../tasks/task-005-delta-baselines.md` Steps 1-5 for full procedure.

**Critical reminders:**

1. **Use env-delta-v2 for baselines + GEARS/scGPT/scFoundation.** Use env-tahoex1 for Tahoe-x1. Use env-cpa for CPA. NEVER mix envs in a single SLURM job.
2. **DO NOT modify env-delta-v2 or env-tahoex1 in place.** If you need a new package, escalate to HeadAI for env-X-v3 split per Sub 1.1 lesson.
3. **HF_HOME must point to scratch:** `export HF_HOME=/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/.hf_cache` (HuggingFace models are 10+ GB; do not pull to home).
4. **PYTHONNOUSERSITE=1 mandatory.**
5. **RTX 5000 Ada (`gpu` partition).** Tahoe-x1 3B fits in 16.7 GB on RTX 5000 Ada per Sub 1.1.
6. **Random baseline MUST fail the WMSE gate.** This is the IP §12.4 calibration test for metric-gaming. If random passes the gate, the harness is broken.
7. **Cross-agent note must be explicit about D3 retirement.** Notify HeadAI to update `dashboards/gate-tracker.md`.

---

## What You Write

### Code and data artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| 5 baselines | `../../output/scripts/delta/baselines/{linear,mean,pca,random,persistence}.py` | Each `fit_predict(...)` function |
| WMSE harness | `../../output/scripts/delta/eval/wmse.py` | `hierarchical_wmse_spearman()` |
| FDR | `../../output/scripts/delta/eval/fdr.py` | BH primary, BY sensitivity |
| Calibration | `../../output/scripts/delta/eval/calibration.py` | Reliability diagram, ECE |
| Stratified | `../../output/scripts/delta/eval/stratified.py` | Per cell × pert × expression |
| Smoke test runner | `../../output/scripts/delta/eval/run_smoketest.py` | End-to-end test on Tahoe subsample |
| Results table | `../../output/delta_baselines_results.md` | Markdown |
| Reliability figures | `../../output/figures/reliability_*.png` | PNG |

### Mandatory documentation

**Status report:** `../../status/task-005-status.md` (template `status-report.md`).
Include subsample size used (1M or 100K fallback), per-baseline metrics, GEARS smoke test result, D3 retirement confirmation.

**Cross-agent note:** `../../../../../shared/notes/1.2-delta-baselines-results.md`
(template `cross-agent-note.md`). Tag tracks: `delta`, `combined`. Urgency: `important`.
Include: D3 retirement notice, baseline performance summary, harness validation status.

---

## Verification

1. [ ] `ls ../../output/scripts/delta/baselines/` shows 5 .py files
2. [ ] `ls ../../output/scripts/delta/eval/` shows 5 .py files (wmse, fdr, calibration, stratified, run_smoketest)
3. [ ] `python -c "from delta.baselines import linear, mean, pca, random, persistence; print('all import OK')"` succeeds
4. [ ] `delta_baselines_results.md` has ≥6 rows (5 baselines + ≥1 method)
5. [ ] The "random" row shows WMSE gate = FAIL
6. [ ] Cross-agent note exists
7. [ ] Status report written

---

## If Something Goes Wrong

1. **Tahoe-100M loader OOMs at 1M cells:** Reduce to 100K. Status: `complete` (the harness is what matters).
2. **GEARS smoke test fails (env-delta-v2 broken):** Use scGPT or scFoundation as alternative method. Both also in env-delta-v2.
3. **Persistence baseline can't find matching cell-type pairs:** Use cell-type clustering as proxy; document.
4. **All baselines produce identical (nonsensical) output:** Status: `failed`. Help-needed. Likely env or data loader bug.
5. **Random baseline PASSES the WMSE gate:** STOP. The harness has a bug. Debug before declaring complete; do NOT ship a broken harness.

Document everything in status report.
