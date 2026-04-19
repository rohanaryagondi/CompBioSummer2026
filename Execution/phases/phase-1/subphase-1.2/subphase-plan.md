---
subphase: "1.2"
title: "MLFF Stability Pilots, BioEmu Batch 2, Delta Baselines, OSF Pre-Registration"
phase: 1
date_range: "2026-04-19 to 2026-05-16"
tracks: [alpha-m, gamma, delta]
status: planned
created: 2026-04-18
task_count: 6
wave_count: 2
---

# Subphase 1.2: MLFF Stability Pilots, BioEmu Batch 2, Delta Baselines, OSF Pre-Registration

## Overview

Sub 1.2 takes the MLFF software validated on crambin in Sub 1.1 (D1 PASS for both
MACE-OFF24 and SO3LR) and extends stability testing to Tier B proteins (WW, GB3,
ubiquitin for MACE NPT; +GB1, NTL9 for SO3LR vacuum NVT). It produces the second
BioEmu ensemble batch (~100 ProteinGym proteins beyond the 46 in batch 1), implements
the 5 mandatory Delta baselines (overdue per D3 criteria) plus the WMSE evaluation
harness, drafts and locks the OSF pre-registration (HARD deadline 2026-05-15), and
builds the core statistical pipeline code (Friedman/Nemenyi, ICC, hierarchical
bootstrap, JZS Bayesian, T_min truncation) that Sub 1.4 + Phase 2 production
depend on. Sub 1.2 is intentionally NOT MLFF pilot production (10-50 ns) — that
is Sub 1.4 scope and feeds D2.

---

## Task Summary

| Task ID | Name | Track | Wave | Dependencies | Effort | Status |
|---------|------|-------|------|--------------|--------|--------|
| task-001 | MACE-OFF24 NPT 5 ns × 3 Tier B (WW, GB3, ubiquitin) | alpha-m | 1 | None | 8-12 days wall, ~420 GPU-hrs H200 | planned |
| task-002 | SO3LR vacuum NVT 5 ns × 5 Tier A/B | alpha-m | 1 | None | 1-2 days wall, ~3 GPU-hrs RTX 5000 Ada | planned |
| task-003 | OSF pre-registration drafting + lock | cross-cutting | 1 | None | 7-10 days writing | planned |
| task-004 | BioEmu batch 2 (~100 proteins) with disorder pre-screen | gamma | 2 | None | 7-10 days wall, ~250 GPU-hrs RTX 5000 Ada | planned |
| task-005 | Delta 5 baselines + WMSE evaluation harness | delta | 2 | env-delta-v2, env-tahoex1 (Sub 1.1) | 7-10 days, ~30 GPU-hrs RTX 5000 Ada | planned |
| task-006 | Statistical pipeline core (Friedman/Nemenyi, ICC, bootstrap, JZS BF, T_min) | cross-cutting | 2 | None | 7-10 days, CPU only | planned |

---

## Wave Protocol

### Wave 1: MLFF Stability + OSF Drafting

**Agents (parallel, max 3):** task-001 (mlff-mace-pilot), task-002 (mlff-so3lr-pilot), task-003 (osf-prereg)
**Dependencies:** None. All envs and input proteins ready from Sub 1.1.
**Completion criteria for trigger:** ALL THREE of these are true:
1. task-001 SLURM jobs are *submitted* (jobs may run 8-12 days; do NOT wait for completion)
2. task-002 SLURM jobs are *submitted*
3. task-003 first draft (≥80% of sections populated) exists at `output/osf-prereg-v1.md`

### Wave 2: BioEmu Batch 2 + Delta Baselines + Stats Pipeline

**Agents (parallel, max 3):** task-004 (bioemu-batch2), task-005 (delta-baselines), task-006 (stats-pipeline)
**Dependencies:** Wave 1 trigger (NOT Wave 1 results — wave structure is purely concurrency-limited)
**Completion criteria:**
- task-004: ≥90 of selected proteins reach ≥2,000 physical conformations
- task-005: All 5 baselines + WMSE harness operational on ≥1M-cell Tahoe subsample
- task-006: All 5 stat-pipeline components pass synthetic-data unit tests

---

## Dependency Diagram

```
Wave 1 (parallel, all start immediately):
  task-001 mlff-mace-pilot ──┐
  task-002 mlff-so3lr-pilot ─┼──> Wave 1 SLURM submitted + OSF v1 drafted
  task-003 osf-prereg ───────┘
                              │
                              v  (partial-completion trigger)
Wave 2 (parallel):
  task-004 bioemu-batch2 ────┐
  task-005 delta-baselines ──┼──> Wave 2 complete
  task-006 stats-pipeline ───┘
                              │
                              v
                    OSF pre-reg locked & deposited 2026-05-15
                              │
                              v
                       Subphase 1.2 complete
```

**Key non-dependency:** No Wave 2 task requires Wave 1 *results*. The wave structure
exists only to (a) start the longest-running compute jobs first and (b) respect
the 3-SubAgent concurrency limit.

---

## Cross-Subphase Dependencies

### What this subphase needs from prior subphases

- **Sub 1.1 envs (all):** env-mace, env-so3lr, env-bioemu, env-delta-v2, env-tahoex1, env-cpa (yml ready). Locations in `shared/notes/1.1-env-split.md`.
- **Sub 1.1 scripts (reuse + fork):**
  - `phases/phase-1/subphase-1.1/output/scripts/mace_hybrid_nvt.py` → fork to add `MonteCarloBarostat` + checkpoint/restart
  - `phases/phase-1/subphase-1.1/output/scripts/so3lr_crambin_nvt.py` → parameterize for 5 proteins
  - `phases/phase-1/subphase-1.1/output/scripts/submit_bioemu_batches.sh` → fork for batch 2
  - `phases/phase-1/subphase-1.1/output/scripts/bioemu_generate_single.py` → reuse as-is
  - `phases/phase-1/subphase-1.1/output/delta-tier1/{gears,scgpt,cpa,scfoundation,tahoex1}_*.py` → reuse adapters
- **Sub 1.1 protein manifest:** `phases/phase-0/subphase-0.1/proteins/manifest.json` (18 entries; 16 active per `1.1-protein-count-canonical.md`)
- **Sub 1.1 BioEmu pass rate data:** `shared/notes/1.1-bioemu-passrates.md` (oversampling formula + class-based rates)
- **Sub 1.1 MACE H200 throughput:** `shared/notes/1.1-mace-hybrid-validation.md` §11 (2.11 ns/day hybrid WW)

### What future subphases will need from this subphase

- **Sub 1.3:** MLFF stability evidence (task-001 NPT report) → informs Sub 1.4 production scope. BioEmu batch 2 ensembles → input for Sub 1.3 feature extraction. Delta baselines + WMSE harness → input for Sub 1.3 cross-validation framework.
- **Sub 1.4:** Statistical pipeline code (task-006) → input for Sub 1.4 pilot analysis (S2 R², ICC, JSD). MLFF stability tested in Sub 1.2 → informs which proteins survive into Sub 1.4 production scope.
- **Phase 2 (all):** OSF pre-reg LOCKED → all Phase 2 analysis bound by it (no more pivoting after May 15).

---

## Gate Checkpoints

| Gate | Date | This subphase produces evidence for |
|------|------|-------------------------------------|
| D1 | May 9 | None new (already ASSESSED: GO 2026-04-17). Formal gate-tracker check only. |
| D2 | Jun 30 | task-001 NPT 5-ns stability on 3 Tier B → preliminary G1 path validation. task-002 SO3LR vacuum 5-ns NVT on 5 proteins → full G1 path for SO3LR. task-006 statistical pipeline ready to score G2/G3/G6. (D2 G1 formally needs ≥10 ns on ≥3 Tier B; that's Sub 1.4 scope.) |
| D3 | Jun 6 | task-005 baselines complete → satisfies the "Baseline implementations complete" criterion (currently the only outstanding D3 item). **D3 will be fully retired after Sub 1.2.** |

---

## Compute Budget

| Task | GPU-hrs (est) | GPU type | Est. SU | Notes |
|------|---------------|----------|---------|-------|
| task-001 MACE NPT (3 proteins × 5 ns) | 420 | H200 (gpu_h200) | ~125,000 | WW ~95, GB3 ~140, UBQ ~185 GPU-hrs (extrapolated from §11 throughput). Within Phase 1 Alpha-M budget (3,000 GPU-hrs). |
| task-002 SO3LR vacuum (5 proteins × 5 ns) | 3 | RTX 5000 Ada (gpu) | ~50 | ~15 ns/day per protein per Sub 1.1. |
| task-003 OSF pre-reg | 0 | None | 0 | Pure writing/research. |
| task-004 BioEmu batch 2 | 250 | RTX 5000 Ada (gpu) | ~3,750 | ~100 proteins × ~2.5 GPU-hrs avg with oversampling. RTX 5000 Ada per SU policy. |
| task-005 Delta baselines + harness | 30 | RTX 5000 Ada | ~450 | Tahoe-100M 1M-cell subsample. |
| task-006 Stats pipeline | 0 | CPU only (Standard Tier) | <30 | Pure Python. |
| **Sub 1.2 total** | **~705** | | **~129,300** | Dominated by MACE NPT on H200 (97% of SU). |

---

## Success Criteria

This subphase succeeds ONLY if ALL of the following are true:

1. **MACE NPT stability evidence:** 3 Tier B proteins (WW, GB3, ubiquitin) each show 5 ns of stable NPT dynamics (no NaN, T = 300±15 K, P ≈ 1 atm, density physical). Trajectories may be stitched across multiple SLURM jobs via checkpoint/restart.
2. **SO3LR vacuum NVT evidence:** 5 Tier A/B proteins (WW, GB3, GB1, NTL9, ubiquitin) each show 5 ns of stable vacuum NVT dynamics.
3. **OSF pre-registration deposited publicly on OSF before 2026-05-15** (HARD deadline). Document covers 16 active / 14 S2-counted proteins, 10 generators, observables, statistical tests, decision rules T1-T6/S1-S5, T_min truncation, AK/GK/CK/DK kill criteria, recalculated power analysis. URL recorded in `dashboards/master-status.md`.
4. **BioEmu batch 2:** ≥90 of ~100 selected ProteinGym proteins reach ≥2,000 physical conformations. Disorder-pre-screen exclusion list documented.
5. **Delta baselines:** All 5 baselines (linear, mean, PCA, random, persistence) implemented and produce predictions on 1M-cell Tahoe-100M subsample. WMSE → Spearman-top-k-DEG harness operational. FDR (BH+BY) + calibration (ECE, reliability diagram) + stratified eval all run end-to-end. **D3 fully retired.**
6. **Statistical pipeline:** All 5 components (Friedman+Nemenyi, ICC with convergence correction, hierarchical bootstrap, JZS BF with 4-prior sensitivity, T_min truncation) pass synthetic-data unit tests with documented expected behavior.
7. All 6 task status reports exist in `status/`.
8. Cross-agent notes written for any Sub 1.2 finding affecting other tracks.
9. Completion report written to `completion-report.md`.
10. Dashboards updated: `master-status.md`, `gate-tracker.md` (D3 retired), `compute-budget.md` (Sub 1.2 actuals).
11. Registry updated: head-1.2 + 6 SubAgents added to `shared/registry.md`.
