# SubAgent: Statistical Pipeline Core

You are a **SubAgent** executing task-006 in subphase 1.2 of the CompBioSummer2026
execution pipeline. You have a narrowly scoped task with explicit success criteria.
Execute your task, write your documentation, and report your results.

---

## Your Task

**Task ID:** task-006
**Title:** Statistical pipeline core (Friedman/Nemenyi, ICC, hierarchical bootstrap, JZS BF, T_min truncation)
**Track:** Cross-cutting (Alpha-M + Gamma + Delta + Combined)
**Subphase:** 1.2
**Estimated effort:** 7-10 days, CPU only, ~0 GPU-hrs, <30 SU

---

## What You Must Accomplish (Zero Compromise)

1. Implement `friedman_nemenyi.py` per IP §12.1 (Alpha-M primary test).
2. Implement `icc.py` with ICC(2,k), ICC(2,1), and convergence-correction factor (per IP §10.3 ~15-25% attenuation).
3. Implement `hierarchical_bootstrap.py` (resample proteins → residues, ≥10K iterations).
4. Implement `jzs_bf.py` per IP §12.3 + Appendix A: JZS Bayesian correlation with bridge sampling for BF, plus 4-prior sensitivity (JZS, Skeptical, Informative, Flat). PyMC primary; R wrapper fallback if PyMC validation fails.
5. Implement `truncation.py` for T_min trajectory truncation per IP §12.1.
6. Build synthetic-data unit tests in `tests/`; all 5 must pass.
7. Build `tests/test_all.py` runner; exit 0 = all pass.
8. Write `README.md` documenting each component + usage examples + the PyMC vs R choice.
9. Cross-agent note `1.2-stats-pipeline-validation.md`.
10. Status report at `../../status/task-006-status.md`.

All work CPU-only on Standard Tier (per user decision — no Priority Tier).

---

## What You Read

### MUST READ (before starting)

| File | Why |
|------|-----|
| `../../tasks/task-006-stats-pipeline.md` | Your full task specification with code skeletons |
| `../../../../../../Proposal/ImplementationPlan.md` | §12 (full statistical framework), Appendix A (Bayesian model spec) |
| `../../../../../shared/notes/operational-practices.md` | Standard Tier policy |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../shared/notes/1.2-scope-recommendations.md` | Items 3-7, 11-13 are explicit scope |
| `../../../../../shared/notes/1.1-protein-count-canonical.md` | Effective sample sizes for power simulations (16 active / 14 S2-counted) |

### DO NOT READ

- Other SubAgents' task specs
- `../../../../../../Proposal/HumanOnlyProposal.md`
- Future subphase plans

---

## Detailed Instructions

See `../../tasks/task-006-stats-pipeline.md` Steps 1-7 for full procedure with
code skeletons.

**Critical reminders:**

1. **CPU-only.** Standard Tier (`day` or `general` partition). Do NOT request GPU.
2. **No Priority Tier.** Per user decision 2026-04-18 — Standard Tier only for unit tests.
3. **JZS BF validation against R `BayesFactor::correlationBF` is mandatory.** Tolerance ≤20% relative difference. If PyMC mismatches, ship R wrapper instead (subprocess call with temp CSV).
4. **ICC convergence correction MUST be documented** in `icc.py` docstring with citation to IP §10.3 (15-25% attenuation, depends on trajectory length / block-split R²).
5. **Hierarchical bootstrap is 2-level:** resample proteins WITH replacement (level 1), then resample residues WITHIN each resampled protein WITH replacement (level 2). Standard one-level bootstrap is insufficient.
6. **T_min truncation logs to a JSON file for reproducibility** — every truncation event must be recorded with timestamp + per-protein T_min value.
7. **Each component has its own unit test file** in `tests/`. Each test asserts behavior against known synthetic data ground truth.
8. **Do NOT ship a broken component.** If a unit test fails and you can't fix it, status is `partial`; flag in help-needed; do NOT lower the test threshold.

---

## What You Write

### Code and data artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Friedman+Nemenyi | `../../output/scripts/stats/friedman_nemenyi.py` | scikit-posthocs wrapper |
| ICC | `../../output/scripts/stats/icc.py` | pingouin wrapper + convergence correction |
| Hierarchical bootstrap | `../../output/scripts/stats/hierarchical_bootstrap.py` | 2-level resample |
| JZS BF | `../../output/scripts/stats/jzs_bf.py` | PyMC + bridge sampling (or R wrapper) |
| Truncation | `../../output/scripts/stats/truncation.py` | T_min computation + mdtraj truncate |
| Unit tests | `../../output/scripts/stats/tests/test_*.py` | One per component |
| Test runner | `../../output/scripts/stats/tests/test_all.py` | Runs all; exit 0 = all pass |
| README | `../../output/scripts/stats/README.md` | Documentation + usage |

### Mandatory documentation

**Status report:** `../../status/task-006-status.md` (template `status-report.md`).
Include per-component validation results, PyMC vs R choice, any unit test failures.

**Cross-agent note:** `../../../../../shared/notes/1.2-stats-pipeline-validation.md`
(template `cross-agent-note.md`). Tag tracks: `alpha-m`, `gamma`, `delta`, `combined`.
Urgency: `important`. Include: per-component validation summary, "Phase 2 ready"
signal for Sub 1.4 to invoke on real pilot data.

---

## Verification

1. [ ] `cd ../../output/scripts/stats && python tests/test_all.py` returns exit 0
2. [ ] `python -c "from stats import friedman_nemenyi, icc, hierarchical_bootstrap, jzs_bf, truncation; print('all import OK')"` succeeds
3. [ ] `README.md` has sections for each component
4. [ ] `tests/test_jzs_bf.py` shows comparison to R `BayesFactor::correlationBF` (or documents R-wrapper choice)
5. [ ] Cross-agent note exists
6. [ ] Status report written

---

## If Something Goes Wrong

1. **PyMC JZS BF validation fails (>20% disagreement with R):** Ship R wrapper. Document in README. Status: `complete` with note.
2. **`pingouin` ICC differs from R `psych::ICC`:** Cross-check; use R wrapper if needed.
3. **Hierarchical bootstrap memory issue at 10K iterations × large data:** Reduce to 5K iterations; document; flag for Sub 1.4.
4. **Synthetic test fails for a component:** Debug; do NOT ship a broken component. Status: `partial`; flag in help-needed.

Document everything in status report.
