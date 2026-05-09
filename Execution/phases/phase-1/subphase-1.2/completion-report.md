---
type: completion-report
subphase: "1.2"
title: "MLFF Stability Pilots, BioEmu Batch 2, Delta Baselines, OSF Pre-Registration"
headai: "head-1.2"
status: DRAFT (data-pending; pre-staged 2026-05-04 by housekeeping subagent)
date: 2026-05-04
last_updated: 2026-05-04
author: head-1.2
---

# Completion Report: Subphase 1.2 — MLFF Stability Pilots, BioEmu Batch 2, Delta Baselines, OSF Pre-Registration

> **STATUS: DRAFT — DATA PENDING.** This skeleton was pre-staged 2026-05-04 by a
> housekeeping subagent. The populated portions reflect terminal state at that
> date (Delta baselines + stats pipeline complete; MACE NPT recipe Round 3 fixed
> for WW+GB3 + UBQ non-generalizing escalated; SO3LR rescue gates PASSED for
> GB3+NTL9; OSF v3 deposit-ready). The `[DATA PENDING …]` blocks tell the future
> writer exactly what's missing and where to look. Promote to `status: complete`
> when (a) all 9 PENDING SLURM jobs reach terminal state, (b) OSF DOI recorded,
> (c) UBQ option-c/d probe verdicts terminal, (d) BioEmu batch 2 final counts
> known.

---

## 1. Executive Summary

[DATA PENDING — fill 3-5 sentences when subphase actually closes. Should cover:
(1) Whether all 9 zero-compromise success criteria were met (see §6 below).
(2) The 4 most material findings (see §3 below).
(3) The recommendation for Sub 1.3 planning (see §13).
Source: this report's §3, §6, §13 once populated.]

---

## 2. Task Results

| Task ID | Title | Status | Key Result |
|---------|-------|--------|------------|
| task-001 | MACE-OFF24 NPT 5 ns × 3 Tier B (WW, GB3, UBQ) on H200 OpenCL hybrid | [DATA PENDING — populate when MACE WW/GB3 5 ns trajectories terminate AND UBQ option-c/d probes terminate] | Recipe Round 3 (sentinel-bond + HBonds + dt=1 fs) FIXED for WW+GB3; UBQ non-generalizing at 17K-atom solvated scale (1UBQ); D-UBQ-1 options (c)+(d) IN FLIGHT |
| task-001-substitute | UBQ option-(c) NTL9 substitute (51 aa) | [DATA PENDING — verdict from probe 10622876 q6kz3m8x dispatch + 5 ns production if PASS] | NTL9 selected (smallest protein-ATOM count of candidate set); 50 ps probe submitted on scavenge_gpu |
| task-001-ubq-altstruct | UBQ option-(d) UBQ_alt 1XQQ alternate-starting-structure | [DATA PENDING — verdict from probe 10622885 q6uadt05 dispatch + 5 ns production if PASS] | 1XQQ NMR model 1 vs 1UBQ crystal; tests starting-structure-residual-stress hypothesis vs architectural |
| task-002 | SO3LR vacuum NVT 5 ns × 5 Tier A/B (WW, GB3, GB1, NTL9, UBQ) on RTX 5000 Ada | partial → rescue in flight | v1: 2/5 PASS (GB1, UBQ); v1 fails for WW (numerical), GB3+NTL9 (charge runaway). |
| task-002-rescue | SO3LR rescue: WW (float64+dt=0.25fs), GB3+NTL9 (neutral protonation re-prep) | [DATA PENDING — populate when 5 ns rescue trajectories 10567505/06/07 terminate] | Gates PASSED 2026-05-02: GB3 + NTL9 cleared 500 ps Rg gate; WW gate cancelled by SU enforcer + replaced by direct 5 ns submission |
| task-003 | OSF pre-registration drafting | complete (deposit pending) | v3 drafted + 6-issue fixes applied 2026-05-03 (incl. substantive D-OSF-SO3LR §4 commit to neutral-protonation methodology); deposit-ready |
| task-004 | BioEmu batch 2 (~100 ProteinGym proteins) with disorder pre-screen + oversampling | partial (10/92 done) | 82 PENDING on scavenge_gpu (9449458+9449459 scontrol-moved); CD19_HUMAN excluded (1.4% pass rate); [DATA PENDING — final pass rates from arrays when terminal] |
| task-005 | Delta 5 baselines + WMSE evaluation harness | complete | 5/5 baselines (linear, mean, PCA, random, persistence) + WMSE harness + FDR (BH+BY) + calibration (ECE) + stratified eval all operational on 100K Tahoe-100M subsample. **D3 fully retired 2026-04-19.** |
| task-006 | Statistical pipeline core | complete | 5/5 components pass synthetic-data unit tests; JZS BF matches R `BayesFactor::correlationBF` to 0.0001% (allowed 20%). Phase-2-ready. |

### Task Details

**task-001: MACE-OFF24 NPT 5 ns × 3 Tier B**
- Status: [DATA PENDING — final verdict depends on (a) WW + GB3 5 ns scavenge_gpu jobs 10567503/04 terminating, (b) UBQ option-c/d probe verdicts (10622876, 10622885) and any follow-on production runs.]
- Result (terminal pre-handoff 2026-05-03): Round 3 recipe FIXED for WW (test_P 100 ps clean, density 1.041 g/cm³, T 297.6 K) + GB3 (probe 10458154 b8r3kt5x 25 ps clean during TIMEOUT). UBQ FAILED across dt={1.0, 0.5, 0.25} fs (NaN @ 7-9.6 ps; pattern asymptotic). Pathology architectural for 17K-atom solvated systems. Escalated via `shared/help-needed/head-1.2-mace-ubq-non-generalization.md`.
- Recipe (LOCKED): sentinel-bond + protein HBonds constraints + MCB freq=25 always-on + dt=1 fs + OpenCL platform. Reference: `shared/notes/1.2-mace-npt-fixed.md`.
- Production driver: `phases/phase-1/subphase-1.2/output/scripts/mace_hybrid_npt_prod.py` (~1000 lines; checkpoint/restart, walltime guard 22.5 hr, GPU keepalive, Vesin NL monkey-patch, `_initializeConstants` monkey-patch).
- 3 cumulative optimization rounds (~30-35% MACE throughput): see `shared/notes/1.2-mace-npt-stability.md` §8.
- scavenge_gpu pivot: jobs 10567503 (q6wmsv5n WW) + 10567504 (q6gpsv9k GB3) PENDING (free billing).
- Probe failures (cancelled archive): 8885960-62 (conda-path bug), 8893817-19 (NODE_FAIL/env), 8939395-97 (matscipy GIL), 9012190-92 (CUDA PTX), 9449439-41 (checkpoint mismatch / monkey-patch / equil insufficiency), 10463584/85, 10465437, 10470003/05, 10550447-451, 10558479-483 (Standard + scavenge cancel/resubmit cycles for optimization rounds).
- Issues: UBQ non-generalization. D-UBQ-1 user decision authorized options (c)+(d) probes IN FLIGHT 2026-05-04.

**task-001-substitute: NTL9 substitute (option-c)**
- Status: [DATA PENDING — probe 10622876 q6kz3m8x verdict.] Status report at `phases/phase-1/subphase-1.2/status/task-001-substitute-status.md`.
- Result (terminal pre-handoff): NTL9 (51 aa, 2HBB, S2-counted, BMRB-confirmed) selected on protein-ATOM count (390, smallest of candidate set). Recipe physics LOCKED. 50 ps probe submitted scavenge_gpu/h200 walltime 5:55:00.
- Decision tree: PASS → 5 ns production (criterion #1 → {WW, GB3, NTL9}); FAIL → fallback GB1 (438 ATOM); both fail → option (a) NVT pivot. See `shared/notes/1.2-mace-npt-prod-launch.md` § option-c.

**task-001-ubq-altstruct: UBQ_alt 1XQQ (option-d)**
- Status: [DATA PENDING — probe 10622885 q6uadt05 verdict.] Status report at `phases/phase-1/subphase-1.2/status/task-001-ubq-altstruct-status.md`.
- Result (terminal pre-handoff): 1XQQ chain A model 1 (UBQ NMR ensemble, room T/P) at `phases/phase-0/subphase-0.1/proteins/ubq_alt.pdb`. Recipe LOCKED; only starting PDB varies. dt=0.5 fs probe 50 ps target.
- Decision: PASS → failure was crystal-residual-stress; UBQ retained in criterion #1 via 1XQQ. FAIL → architectural; falls back to (a) or (c). See `shared/notes/1.2-mace-npt-prod-launch.md` § option-d.

**task-002: SO3LR vacuum NVT v1 (5 proteins)**
- Status: partial (2/5 PASS); rescue campaign supersedes for the 3 failing proteins. Status report at `phases/phase-1/subphase-1.2/status/task-002-status.md`.
- Result: GB1 + UBQ stable 5 ns (PASS). WW NaN @ 0.704 ns (numerical). GB3 + NTL9 silent structural explosion @ ~100 ps (Rg → 986/similar; charge runaway in vacuum).
- Strategic finding: prior conclusion that GB3/NTL9 were "dead" was right about mechanism (Coulomb-driven expansion in net-charged vacuum) but wrong about cure space — fix is to remove the unphysical net-charge-in-vacuum condition (neutral protonation), NOT to tune dt/NHC.

**task-002-rescue: SO3LR rescue (WW + GB3 + NTL9)**
- Status: [DATA PENDING — 5 ns full rescue jobs 10567505 (g7p4tv8m GB3), 10567506 (n5h6kx9q NTL9), 10567507 (w8q4r3xz WW) terminate.] Status report at `phases/phase-1/subphase-1.2/status/task-002-rescue-status.md`.
- Gate verdicts (terminal 2026-05-02): GB3 (10458604) PASSED 500 ps clean (PE −1513 stable, T 290-310 K); NTL9 (10458605) PASSED 500 ps clean. WW gate (10458603) CANCELLED by `prio_su_enforce.sh` when projected SU exceeded 250 cap (replaced by direct 5 ns submission).
- Production protocol commit: **all SO3LR vacuum runs on net-charged proteins (|Q|>0) require mandatory neutral-protonation re-prep** (D/E → ASH/GLH; K/R → LYN). Encoded in OSF v3 §4. See `shared/notes/1.2-so3lr-rescue-results.md`.
- Issues: SU enforcer false-positive on WW gate (R8 from closure-master-plan); contingency 3-cycle cancel/resubmit for optimization rounds.

**task-003: OSF pre-registration**
- Status: complete (deposit pending). Status report at `phases/phase-1/subphase-1.2/status/task-003-status.md`.
- Result: v3 deposit-ready at `phases/phase-1/subphase-1.2/output/osf-prereg-v3.md`. v2 → v3 changelog: (1) §4 MACE-OFF24 row annotated with Round 3 production recipe; (2) §4 SO3LR row commits to neutral-protonation methodology (substantive D-OSF-SO3LR fix); (3) §7.1 T1 row updated with multi-path D2 G1 evidence; (4) §10 sensitivity narrative updated for UBQ-NPT non-generalization; (5) §13 amendment provisions clarified. 6 internal-consistency fixes APPLIED 2026-05-03 (5 trivial + 1 substantive).
- Deposit instructions: `phases/phase-1/subphase-1.2/output/osf-deposit-instructions.md`. Target 2026-05-13; HARD 2026-05-15.
- DOI: [DATA PENDING — record from user when deposit lands. Update `dashboards/master-status.md` decision-log AND `shared/notes/1.2-osf-deposited.md` with DOI + deposit date + SHA256 of deposited document.]
- Issues: D-OSF-SO3LR resolved (substantive §4 fix applied pre-deposit); other 5 fixes trivial. Deposit slip >2 days requires PlannerAI replan.

**task-004: BioEmu batch 2**
- Status: partial. Status report at `phases/phase-1/subphase-1.2/status/task-004-status.md`.
- Result: 10/92 complete pre-handoff. CD19_HUMAN EXCLUDED (1.4% pass rate would need ~188K samples). Arrays 9449458 (x9sok7yl, 41 idx) + 9449459 (l5uw4lsy, 41 idx, CD19 excluded) PENDING on scavenge_gpu (scontrol-moved).
- [DATA PENDING — final counts from `phases/phase-1/subphase-1.2/output/batch2_summary.md` when both arrays terminal. Need: # proteins ≥ 2,000 conformations (target ≥90), # exclusions, batch 2 actual pass rates vs predicted (note `1.2-bioemu-batch2-passrates.md` exists), any topup needed for sub-2K proteins.]
- Issues: Fair-share `pi_mg269` 0.0146 → 0.0167; scavenge dispatch slow behind 178+ scavenge users.

**task-005: Delta 5 baselines + WMSE harness**
- Status: complete. Status report at `phases/phase-1/subphase-1.2/status/task-005-status.md`. Cross-agent note `shared/notes/1.2-delta-baselines-results.md`.
- Result: All 5 baselines (linear ridge, mean, PCA, random, persistence) + WMSE → Spearman-top-k-DEG hierarchical harness + FDR (BH + BY sensitivity) + calibration (reliability diagram + ECE) + stratified eval (per cell × pert × expression) operational at `phases/phase-1/subphase-1.2/output/scripts/delta/`. Smoke-tested end-to-end on 100K-cell Tahoe-100M subsample (train 72,810 / test 27,190).
- **Metric-gaming check (IP §12.4 calibration):** random baseline FAILS WMSE gate at top level AND all 48 cell-type strata. Confirms harness robustness.
- Artifacts: `delta/baselines/{linear,mean,pca,random,persistence}.py`, `delta/eval/{wmse,fdr,calibration,stratified}.py`, `delta/eval/synth_unit_test.py` (5/5 pass).
- **D3 gate fully RETIRED 2026-04-19.**

**task-006: Statistical pipeline core**
- Status: complete. Status report at `phases/phase-1/subphase-1.2/status/task-006-status.md`. Cross-agent note `shared/notes/1.2-stats-pipeline-validation.md`.
- Result: 5/5 components implemented at `phases/phase-1/subphase-1.2/output/scripts/stats/`: friedman_nemenyi.py, icc.py (with §10.3 convergence correction), hierarchical_bootstrap.py (2-level, 10K iterations), jzs_bf.py (Fisher-1915 exact closed form + 4-prior sensitivity + R fallback), truncation.py (T_min per protein).
- Headline cross-checks: Python JZS BF matches R `BayesFactor::correlationBF` to 0.0001% (n=20, r=0.7605, both return BF₁₀=288.2478; allowed 20%, achieved 4 orders of magnitude better). Hierarchical bootstrap CI 2.7× wider than naive 1-level (preempts IP §14.1 "per-residue N inflation" reviewer attack). ICC convergence-correction recovers exactly the asymptotic 0.85 from measured 0.68 given 20% attenuation. Coverage sweep: 19/20 hits at nominal 95%.
- env-stats environment created non-destructively (env-mace and env-so3lr unmodified). Python + R cross-tool agreement.
- **Pipeline is Phase-2-ready** for D2 G2/G3/G6 scoring + Phase 2 production analysis (combined-paper BF, Alpha-M convergence ICC, Delta WMSE bootstrap CIs).

---

## 3. Key Findings (affect future subphases / other tracks)

1. **MACE-OFF24 NPT recipe exists and is reproducible (sub-10K-atom solvated scale).** Round 3 recipe (sentinel-bond + HBonds + dt=1 fs + MCB freq=25) is documented at `shared/notes/1.2-mace-npt-fixed.md`. Reproducible from `output/scripts/npt_diagnostics/test_L_hbonds.py` (25 ps) and `test_P_extended.py` (100 ps). **Sub 1.4 production should use NPT, not the NVT fallback,** for all proteins solvating to <10K atoms. WW (7,565) and GB3 (9,874) PASS; GB1 (~438 ATOM, ~9.5K solvated) and NTL9 (~390 ATOM, ~9K solvated) expected to PASS.

2. **MACE-OFF24 NPT recipe does NOT generalize to UBQ-class systems (~17K atoms solvated, ~1.2K MACE atoms) seeded from the 1UBQ crystal structure.** Pattern is architectural for that scale, asymptotic across dt={1.0, 0.5, 0.25} fs. Two parallel remediations IN FLIGHT 2026-05-04: option-(c) NTL9 substitute (10622876) + option-(d) UBQ_alt 1XQQ alternate-starting-structure (10622885). [DATA PENDING — verdicts will determine final criterion #1 mapping. Source: `shared/notes/1.2-mace-npt-stability.md` §9 + `1.2-mace-npt-prod-launch.md` § option-c/d.]

3. **SO3LR vacuum runs on net-charged proteins require mandatory neutral-protonation re-prep.** Strategic insight: prior task-002 conclusion that GB3/NTL9 were "dead" correctly diagnosed the failure mechanism (vacuum surface-charge runaway) but missed the cure space — the fix is chemistry, not numerics. GB3 + NTL9 cleared 500 ps Rg gates after re-prep (D/E → ASH/GLH; K/R → LYN; net side-chain charge = 0). Encoded in OSF v3 §4 as production protocol commit. Source: `shared/notes/1.2-so3lr-rescue-results.md`.

4. **Statistical pipeline cross-tool validated to 0.0001% on JZS BF.** Python implementation matches R `BayesFactor::correlationBF` 4 orders of magnitude better than the 20% tolerance allowed in the task spec. The pipeline preempts the most likely reviewer attacks (per-residue N inflation via 2-level hierarchical bootstrap; ICC convergence attenuation via §10.3 correction; 4-prior sensitivity for combined-paper BF). Phase-2-ready. Source: `shared/notes/1.2-stats-pipeline-validation.md`.

5. **Delta D3 gate fully retired 2026-04-19.** All 5 Tier 1 methods + 5 baselines + WMSE harness + FDR + calibration + stratified eval operational. Random baseline correctly FAILS WMSE gate at top level AND all 48 cell-type strata, confirming the IP §12.4 metric-gaming calibration check is robust. Source: `shared/notes/1.2-delta-baselines-results.md`.

6. **scavenge_gpu pivot achieves ~93% projected SU savings** vs original Sub 1.2 baseline. All 9 closure jobs on `scavenge_gpu` (1/10 Standard tier billing) with full checkpoint/restart support. Scavenge_gpu policy is now the cross-cutting default for all Phase 2 compute that has checkpoint/restart support. Source: `dashboards/compute-budget.md` + `shared/notes/operational-practices.md` § scavenge_gpu policy.

7. **3 cumulative optimization rounds applied** to MACE + SO3LR scripts (~30-35% MACE throughput, ~10-15% SO3LR throughput) with recipe physics LOCKED. Optimizations are transferable to Sub 1.4 production. Source: `shared/notes/1.2-mace-npt-stability.md` §8.

[DATA PENDING — additional findings from in-flight subagents (Item A NPZ cleanup, Item H trajectory skeletons, Item I RMSF+RSALOR, Item D walltime classification proposal) may add bullets when their reports land.]

---

## 4. Cross-Agent Notes Generated

| Note | Path | Affected Tracks | Urgency |
|------|------|----------------|---------|
| MACE NPT recipe FIXED + UBQ caveat | `shared/notes/1.2-mace-npt-fixed.md` | alpha-m, combined | critical |
| MACE NPT prod launch + option-c/d probes | `shared/notes/1.2-mace-npt-prod-launch.md` | alpha-m, combined | important |
| MACE NPT stability (preliminary + §7-9 evolution) | `shared/notes/1.2-mace-npt-stability.md` | alpha-m | important |
| SO3LR rescue results + production protocol commit | `shared/notes/1.2-so3lr-rescue-results.md` | alpha-m | critical |
| SO3LR pilot stability (v1 + rescue) | `shared/notes/1.2-so3lr-pilot-stability.md` | alpha-m | info |
| Closure master plan + R6/R7/R8 risk register | `shared/notes/1.2-closure-master-plan.md` | alpha-m, gamma, delta, combined, infrastructure | critical |
| Delta baselines + harness results (D3 retired) | `shared/notes/1.2-delta-baselines-results.md` | delta, combined | important |
| Statistical pipeline validation | `shared/notes/1.2-stats-pipeline-validation.md` | alpha-m, gamma, delta, combined | important |
| BioEmu batch 2 pass-rate analysis | `shared/notes/1.2-bioemu-batch2-passrates.md` | gamma | important |
| BioEmu precache keepalive fix | `shared/notes/1.2-bioemu-precache-keepalive-fix.md` | gamma, infrastructure | info |
| MACE conda path fix (lesson) | `shared/notes/1.2-mace-conda-path-fix.md` | alpha-m, infrastructure | info |
| env-so3lr typing-extensions fix | `shared/notes/1.2-env-so3lr-typing-extensions-fix.md` | alpha-m, infrastructure | info |
| MACE throughput ceiling investigation | `shared/notes/1.2-mace-throughput-ceiling.md` | alpha-m | info |
| GPU util efficiency lessons | `shared/notes/1.2-gpu-util-efficiency.md` | infrastructure | info |
| OSF deposited (DOI + metadata) | `shared/notes/1.2-osf-deposited.md` | alpha-m, gamma, delta, combined, infrastructure | critical (will be promoted from STUB once DOI recorded) |
| Scope recommendations (forward-looking from Sub 1.1 audit) | `shared/notes/1.2-scope-recommendations.md` | all | info |
| Operational practices (scavenge_gpu policy + SU enforcement + OSF checklist) | `shared/notes/operational-practices.md` | all | info |

[DATA PENDING — in-flight subagents (A/H/I/D) may write additional notes.]

---

## 5. Help-Needed Docs Generated

| Topic | Path | Status |
|-------|------|--------|
| MACE UBQ NPT non-generalization (D-UBQ-1) | `shared/help-needed/head-1.2-mace-ubq-non-generalization.md` | escalated 2026-05-03; options (c)+(d) probes IN FLIGHT |
| Phase 2 MLFF scope (RESOLVED — Option 5 H200 OpenCL committed) | `shared/help-needed/sub-1.2-phase2-mlff-scope.md` | resolved 2026-04-18 |
| BioEmu batch_size=0 bug (RESOLVED — length-aware patch) | `shared/help-needed/head-1.2-bioemu-batch-size-zero.md` | resolved 2026-04-19 |
| SU budget auto-cancel notification (WW SO3LR rescue 2026-05-02) | `shared/help-needed/head-1.2-su-budget-auto-cancel-2026-05-02T22-58-45Z.md` | informational; cancelled job replaced |

[DATA PENDING — additional help-needed escalations if any of the 9 PENDING jobs fail in unrecoverable ways. Update with new doc paths and resolution status.]

---

## 6. Resource Usage

| Resource | Estimated | Actual |
|----------|-----------|--------|
| GPU-hours (Sub 1.2 total) | ~705 | [DATA PENDING — sum from `dashboards/compute-budget.md` Sub 1.2 burn-rate row when subphase closes. Pre-handoff snapshot 2026-05-04: ~134 GPU-hrs cumulative through Sub 1.1 + Sub 1.2 partial; Sub 1.2 specific not yet aggregated post-scavenge-pivot.] |
| Wall time | 2026-04-19 → 2026-05-16 (4 weeks) | [DATA PENDING — record actual closure date.] |
| Storage | <500 GB | [DATA PENDING — `du -sh phases/phase-1/subphase-1.2/output/` at close.] |
| Standard SU | ~129,300 | [DATA PENDING — sum `pi_mg269` partition jobs. Worst-case Sub 1.2 closure projection: ~3,500 SU due to scavenge_gpu pivot (was ~38,000 SU original). ~93% savings.] |
| Priority SU | ~108.5 cap (initial) → 250 cap (revised) | 231.5 / 250 used (~$0.93 cash) — cap reached, no further priority spend planned |

**Burn-rate context (pre-closure):**
- Sub 1.2 actual through 2026-04-25 (per `compute-budget.md`): ~130 GPU-hrs / ~6,630 SU.
- Sub 1.2 remaining (est, post-scavenge pivot): ~3,500 SU worst-case (vs ~122,700 SU original projection).
- Total Sub 1.1 + Sub 1.2 cumulative through 2026-04-25: ~264 GPU-hrs / ~16,500 SU.

[DATA PENDING — post-closure final accounting. Note: scavenge_gpu billing is 1/10 Standard rate; tally must use scavenge-rate accounting for the 9 closure jobs.]

---

## 7. Success Criteria Evaluation (zero-compromise per CLAUDE.md)

| # | Criterion | Met? | Evidence |
|---|-----------|------|----------|
| 1 | MACE NPT 3 Tier B × 5 ns (no NaN, T=300±15K, P≈1atm, density physical) | [DATA PENDING — depends on (a) WW + GB3 5 ns scavenge_gpu jobs 10567503/04 terminating successfully, (b) UBQ option-c/d probe verdicts 10622876 + 10622885, (c) any production runs from PASS verdicts. Currently terminal pre-handoff: WW 100 ps validated (test_P), GB3 25 ps validated (probe 10458154); 5 ns production for both PENDING dispatch on scavenge.] | `shared/notes/1.2-mace-npt-fixed.md` + production logs in `output/trajectories/mace_npt/` |
| 2 | SO3LR 5 Tier A/B × 5 ns vacuum NVT (WW, GB3, GB1, NTL9, UBQ) | [DATA PENDING — depends on 5 ns rescue jobs 10567505 (GB3 neutral) + 10567506 (NTL9 neutral) + 10567507 (WW float64+dt=0.25fs+chain=5) terminating. Currently: GB1 + UBQ v1 stable 5 ns (PASS). GB3 + NTL9 gates PASSED 500 ps Rg pre-screen (chemistry rescue validated). WW gate cancelled by SU enforcer + replaced by direct 5 ns submission.] | `shared/notes/1.2-so3lr-rescue-results.md` + production logs in `output/trajectories/so3lr_vacuum_rescue/` |
| 3 | OSF deposited publicly before 2026-05-15 (HARD) | [DATA PENDING — user deposits target 2026-05-13. v3 deposit-ready. Record DOI in `dashboards/master-status.md` decision-log AND `shared/notes/1.2-osf-deposited.md` upon completion.] | `phases/phase-1/subphase-1.2/output/osf-prereg-v3.md` (deposit-ready) + `output/osf-deposit-instructions.md` |
| 4 | BioEmu batch 2 ≥ 90 of ~100 reach ≥ 2,000 conformations; disorder-pre-screen documented | [DATA PENDING — final counts when arrays 9449458 + 9449459 terminate. Pre-handoff: 10/92 complete; CD19_HUMAN excluded (93 → 92). Acceptable to extend ~3 days into Sub 1.3 per CLAUDE.md.] | `phases/phase-1/subphase-1.2/output/batch2_summary.md` (when complete) + `shared/notes/1.2-bioemu-batch2-passrates.md` |
| 5 | Delta 5 baselines + WMSE harness + FDR + calibration + stratified; D3 retired | **YES** | `shared/notes/1.2-delta-baselines-results.md`; D3 retired 2026-04-19; gate-tracker.md ASSESSED: GO (RETIRED) |
| 6 | Stats pipeline 5 components pass synthetic-data unit tests (Friedman+Nemenyi, ICC, hierarchical bootstrap, JZS BF, T_min) | **YES** | `shared/notes/1.2-stats-pipeline-validation.md`; `python tests/test_all.py` exit 0; JZS BF matches R to 0.0001% |
| 7 | All 6 task status reports exist in `status/` | YES (10 reports total: task-001 + task-001-substitute + task-001-ubq-altstruct + task-002 + task-002-rescue + task-003 + task-004 + task-005 + task-006 + task-009) | `phases/phase-1/subphase-1.2/status/` |
| 8 | Cross-agent notes for findings affecting other tracks | YES (~17 notes; see §4) | `shared/notes/1.2-*.md` |
| 9 | Completion report `completion-report.md` written | [DATA PENDING — promote this skeleton to `status: complete` once §1, §2, §6, §7 PENDING blocks are filled. Final action of subphase.] | this document |

---

## 8. Gate Evidence

| Gate | Evidence Produced | Assessment |
|------|------------------|------------|
| D1 (May 9) | (already ASSESSED: GO 2026-04-17 in Sub 1.1) | GO confirmed |
| D2 (June 30) | **Preliminary G1 evidence base** — see §3 finding 1+2: MACE NPT WW + GB3 fixed, UBQ remediation IN FLIGHT; SO3LR 2/5 v1 + 3/3 rescue gates PASSED. Multi-path achievability for "≥1 MLFF stable ≥10 ns on ≥3 Tier B". [DATA PENDING — final D2 evidence requires Sub 1.4 production at 10 ns scope; Sub 1.2 contributes 5-ns NPT precursor evidence only. Update gate-tracker.md ON TRACK → preliminary verdict when 5 ns NPT/NVT trajectories land.] | ON TRACK preliminary |
| D3 (June 6) | **task-005 baselines complete** + 5/5 Tier 1 methods + WMSE harness fully retiring last D3 outstanding criterion | ASSESSED: GO (RETIRED) 2026-04-19 |

---

## 9. MACE NPT Stability Summary (per-protein)

[DATA PENDING — populate when WW + GB3 5 ns jobs terminate. Required per-protein:
- Trajectory length achieved (ns); SLURM resubmission count
- T mean ± std (K) — pass if 300 ± 15
- P mean ± std (atm) — pass if 1 ± 200 (barostat noisy)
- Density mean ± std (g/mL) — pass if 0.95-1.05
- Box volume drift (last 1 ns vs 1-2 ns window) — pass if <5%
- PE NaN count — pass if 0
- C-alpha RMSD max vs frame 0 — pass if <5 Å
- Throughput ns/day (measured)
- Per-protein verdict: PASS / PARTIAL / FAIL

Sources: `output/trajectories/mace_npt/<tag>_npt_meta.json` + DCD analysis. UBQ row depends on options c/d probe + (if PASS) 5 ns production verdict.]

| Protein | Recipe | Status | Length | T (K) | Density | RMSD | Verdict |
|---------|--------|--------|-------:|------:|--------:|-----:|---------|
| WW | Round 3 | [DATA PENDING from 10567503] | TBD | TBD | TBD | TBD | TBD |
| GB3 | Round 3 | [DATA PENDING from 10567504] | TBD | TBD | TBD | TBD | TBD |
| UBQ (c) NTL9 substitute | Round 3 | [DATA PENDING from 10622876 + production if PASS] | TBD | TBD | TBD | TBD | TBD |
| UBQ (d) 1XQQ alt-starting | Round 3 (dt=0.5 fs) | [DATA PENDING from 10622885 + production if PASS] | TBD | TBD | TBD | TBD | TBD |

---

## 10. SO3LR Vacuum NVT Stability Summary (per-protein)

[DATA PENDING — populate when 5 ns rescue jobs terminate. Required per-protein:
- Trajectory length achieved (ns)
- T mean ± std (K) — pass if 300 ± 15
- Rg ratio (final / initial) — pass if < 1.2
- COM displacement vs frame 0 — pass if < 5 Å
- NaN onset (ps) or N/A
- Per-protein verdict: PASS / FAIL]

| Protein | Protocol | Length | T (K) | Rg ratio | COM (Å) | NaN | Verdict |
|---------|----------|-------:|------:|---------:|--------:|----:|---------|
| WW | float64+dt=0.25fs+chain=5 | [DATA PENDING from 10567507] | TBD | TBD | TBD | TBD | TBD |
| GB3 | neutral protonation re-prep | [DATA PENDING from 10567505] | TBD | TBD | TBD | TBD | TBD |
| GB1 | v1 default | 5.000 | ~300 | <1.05 | <2 | 0 | **PASS (v1)** |
| NTL9 | neutral protonation re-prep | [DATA PENDING from 10567506] | TBD | TBD | TBD | TBD | TBD |
| UBQ | v1 default | 5.000 | ~300 | <1.05 | <2 | 0 | **PASS (v1)** |

Source: `shared/notes/1.2-so3lr-pilot-stability.md` + `1.2-so3lr-rescue-results.md`.

---

## 11. OSF Deposit Metadata

| Field | Value |
|-------|-------|
| Pre-deposit version | v3 (`phases/phase-1/subphase-1.2/output/osf-prereg-v3.md`) |
| Deposit target date | 2026-05-13 |
| Deposit HARD deadline | 2026-05-15 |
| Deposit actual date | [DATA PENDING — record from user] |
| OSF DOI | [DATA PENDING — record from user; will be locked into `dashboards/master-status.md` decision-log + `shared/notes/1.2-osf-deposited.md`] |
| OSF project URL | [DATA PENDING] |
| SHA256 of deposited document | [DATA PENDING — `sha256sum osf-prereg-v3.md` after deposit] |
| Pre-registered analysis plan covers | 16 active proteins / 14 S2-counted; 10 generators; 4 statistical domains (Alpha-M Friedman+Nemenyi+ICC; Gamma paired Wilcoxon+win-rate; Delta WMSE+BH-FDR+calibration; Combined JZS Bayesian correlation w/ 4-prior sensitivity); decision rules T1-T6 / S1-S5; kill criteria AK/GK/CK/DK; T_min trajectory truncation; recalculated power analysis (16-active / 14-S2 design with 20% ICC convergence attenuation). |

---

## 12. BioEmu Batch 2 Final Counts

[DATA PENDING — populate when arrays 9449458 + 9449459 terminate. Required:
- Total proteins selected for batch 2 (initial): ~93 → 92 (CD19_HUMAN excluded)
- Proteins reaching ≥ 2,000 conformations: target ≥ 90
- Proteins requiring topup: list with actual vs predicted pass rates
- Disorder pre-screen exclusion list: documented?
- Actual vs predicted pass rates: reference `shared/notes/1.2-bioemu-batch2-passrates.md`

Source: `phases/phase-1/subphase-1.2/output/batch2_summary.md` (when written). Sub 1.2 success criterion #4 closes when ≥ 90 of ~100 proteins reach ≥ 2,000 physical conformations. Acceptable to extend ~3 days into Sub 1.3 per CLAUDE.md.]

---

## 13. Recommendation for PlannerAI (Sub 1.3 planning)

[DATA PENDING — refine after subphase closes. Key items expected:

1. **Sub 1.4 MACE NPT scope:** based on per-protein outcomes (which proteins generalize at ≥10K-atom solvated scale; whether option-c NTL9 or option-d 1XQQ retains UBQ in criterion #1; whether GB1 + NTL9 also generalize). Default mapping per `shared/notes/1.2-mace-npt-fixed.md`: WW + GB3 + GB1 + NTL9 → MACE NPT; UBQ → NVT-only fallback unless option (d) PASS.
2. **Sub 1.4 SO3LR scope:** if 5 ns rescues PASS, full 5/5 vacuum NVT operational. Phase 2 protocol: mandatory neutral-protonation re-prep for all net-charged proteins.
3. **D2 G1 formal evidence path:** Sub 1.4 production at ≥ 10 ns × ≥ 3 Tier B is the formal gate. Sub 1.2 5 ns NPT/NVT is precursor evidence. ON TRACK.
4. **scavenge_gpu policy:** continue as default for Phase 2 production (≥93% SU savings demonstrated; preemption survivable via checkpoint/restart). Audit trajectory stitching across REQUEUE pre-Sub-1.4 (R6 in closure-master-plan).
5. **Per-protein recipe-fallback compute multiplier (R7):** Sub 1.4 must budget ~3-5× wall for proteins requiring NVT/Tier-2 NPT.
6. **prio_su_enforce.sh failure-mode docs (R8):** address before Sub 1.4 priority work.
7. **OSF v4 amendment:** scheduled after Sub 1.4 planning; SO3LR rescue methodology lock contingent on 5 ns full-rescue PASS + final per-protein recipe mapping.
8. **Items A/H/I/D from in-flight 2026-05-04 background subagents:** cleanup/skeleton work that may inform Sub 1.4 planning if those reports land.
9. **Storage tier policy (BEYOND Sub 1.2 — elevate to `shared/notes/operational-practices.md`):** Per user directive 2026-05-04 informed by the 2026-05-04 disk survey: **use scratch tier whenever a file is large OR non-permanent (e.g., logs, slurm-*.out, intermediate arrays, conda pkg caches, model download caches, computed/regeneratable data).** Use home tier only for code, docs, manifests, and small reference data. Use project tier only for permanent shared resources (conda envs already there, large reference DBs). Survey context that motivated the rule: group `pi_mg269` project tier at 95% bytes / 76% files (binding constraint group-wide); home at 77% (rag88 = whole group share); scratch at 30% group / 4.7% rag88 — ample headroom. Apply when writing future task specs / SLURM wrappers: default output paths under scratch (e.g., `~/scratch60/CompBioSummer2026/<subphase>/<topic>/`); SLURM `--output=`/`--error=` redirect to scratch; conda pkg + model caches (`CONDA_PKGS_DIRS`, `HF_HOME`, `JAX_COMPILATION_CACHE_DIR`, `XDG_CACHE_HOME`) under scratch. **PlannerAI action:** elevate to `shared/notes/operational-practices.md` § Storage tier policy as durable cross-subphase guidance applicable to Sub 1.4+ and Phase 2 production.
10. **Compute-cost vs quality directive (BEYOND Sub 1.2 — elevate to `shared/notes/operational-practices.md` as standing rule for Sub 1.4+ and Phase 2):** Per user directive 2026-05-05: **for every SLURM job, exercise both levers — (a) cheapest viable partition AND (b) most efficient code/parameters — never just one.** The goal is **absolute highest quality with NO compromise on the science** while minimizing SU hours as far as possible. Apply when authoring future task specs, SLURM wrappers, and production drivers:
    - **Partition lever (cost-first):** default to `scavenge_gpu` (1/10 Standard billing) for any workload with checkpoint/restart support. Move to Standard `gpu` (RTX 5000 Ada, 15 SU/hr) only if scavenge dispatch genuinely fails the timeline. Move to `gpu_h200` (300 SU/hr, 11.5× MACE inference speed) only when the workload is throughput-bound AND latency matters. Priority Tier (`prio_mg269`/`prio_gerstein`) reserved for small jobs (<400 SU) where queue bypass justifies the cost. `gpu_devel` (≤6 hr walltime) for diagnostic-first probes.
    - **Code/parameter lever (efficiency-first):** before each new submission, audit whether prior optimization rounds have been exhausted for this workload. Sub 1.2 examples (3 rounds applied 2026-05-03 yielded ~30-35% MACE + ~10-15% SO3LR throughput): pre-allocate constant tensors outside hot loops; relax NaN-check + checkpoint cadence; raise constraint tolerance (`integrator.setConstraintTolerance(1e-4)`); drop forces from NaN check; OMP/MKL=4 + `OMP_PROC_BIND=close OMP_PLACES=cores` NUMA pinning; `XLA_FLAGS="--xla_gpu_triton_gemm_any=true --xla_gpu_enable_latency_hiding_scheduler=true"`; persistent JAX cache via `JAX_COMPILATION_CACHE_DIR`; trim equilibration window; lengthen DCD/StateData reporter strides; relax keepalive cadence. Round-4 candidates documented in `phases/phase-1/subphase-1.2/output/optimization-round-4-{mace,so3lr,bioemu}.md` (subagents landing 2026-05-05).
    - **Quality guardrails — NEVER compromise on:** trajectory length (5 ns minimum per Sub 1.2 criterion #1/#2; 10 ns minimum per D2 G1); numerical precision below what stability demands (Round 3 recipe locks dt=1 fs MACE NPT, dt=0.5 fs SO3LR vacuum standard, dt=0.25 fs SO3LR WW numerical rescue); force-field choice (no swaps without full recipe re-validation); pre-registered statistical thresholds (T1-T6 / S1-S5, JZS BF, Friedman+Nemenyi — OSF v3 deposit-locked); benchmark protein roster (16 active / 14 S2-counted — unchanged unless tracked OSF amendment); BioEmu pass-rate and disorder-pre-screen rules.
    - **Decision flow per submission:** (1) pick the cheapest partition that plausibly meets the timeline; (2) verify all known optimization rounds are applied to the script; (3) submit a small diagnostic-first probe per `operational-practices.md`; (4) only then commit production. If timeline pressure forces a more expensive partition, document the tradeoff + SU delta in a cross-agent note AND flag in completion-report §14 resource accounting.
    - **PlannerAI action:** elevate to `shared/notes/operational-practices.md` § Compute-cost vs quality directive as durable cross-subphase guidance. Every future SubAgent CLAUDE.md should reference this directive in its task-spec preamble.

Update this section with concrete recommendations once all Sub 1.2 outcomes are terminal.]

---

## 14. Resource Accounting Reconciliation

[DATA PENDING — populate when subphase closes. Required:
- GPU-hour estimate vs actual per task (table from CLAUDE.md "Sub 1.2 Compute — Planned" + actuals from sacct).
- SU consumed by partition (gpu_h200 vs gpu_b200 vs gpu vs scavenge_gpu vs gpu_devel).
- Standard SU vs Priority SU split.
- Cumulative project burn through end of Sub 1.2.
- Phase 1 Alpha-M budget remaining after Sub 1.2 (projected was ~2,428 GPU-hrs; track actual).
- Storage actual at close.
- Lessons learned for future SU policy.

Source: `dashboards/compute-budget.md` + sacct queries for all Sub 1.2 jobs.]

---

*End of Sub 1.2 completion report (DRAFT). Promote to `status: complete` once all
[DATA PENDING] blocks resolved. Final action: update `dashboards/master-status.md`
+ `dashboards/active-subphase.md` to mark Sub 1.2 closed and trigger PlannerAI
"plan next subphase".*
