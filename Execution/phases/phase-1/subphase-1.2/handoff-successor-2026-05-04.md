---
title: Sub 1.2 head-1.2 successor handoff
author: head-1.2 (predecessor session)
date: 2026-05-04T00:30:00Z
supersedes: handoff-notes.md (2026-05-02 overnight summary — out of date)
purpose: Complete state transfer to the successor head-1.2 with no loss.
---

# READ THIS FIRST (TL;DR — 60 seconds)

You are **head-1.2**, the HeadAI for subphase 1.2. The Round 3 MACE NPT recipe was fixed 2026-05-02. Since then, in chronological order:

1. Closure plan launched 2026-05-02 — 6 SubAgents executed Wave 1+2.
2. **UBQ MACE NPT does NOT generalize** at 17K-atom solvated scale (NaN @ 7-9.6 ps regardless of dt halving 1.0/0.5/0.25 fs). Pattern asymptotic. Help-needed escalation written.
3. **3 cumulative optimization rounds** applied to MACE/SO3LR scripts (~30-35% MACE + ~10-15% SO3LR throughput).
4. **scavenge_gpu pivot** — all 7 closure jobs migrated (1/10 Standard tier billing rate).
5. **SU budget cap reduced 800 → 250** + `prio_su_enforce.sh` projected-budget enforcement.
6. **Doc audit batch 1 applied** (13 files updated for currency).
7. **OSF v3 — 6 internal-consistency fixes APPLIED 2026-05-03** including substantive D-OSF-SO3LR fix (§4 commits to neutral-protonation methodology for net-charged proteins).
8. **CLAUDE.md MUST-READ list updated** — 6 critical 2026-05-02/03 docs added.
9. **UBQ paths (c) + (d) IN FLIGHT** — NTL9 substitute probe (10622876 q6kz3m8x) + UBQ_alt 1XQQ probe (10622885 q6uadt05), both on scavenge_gpu.
10. **6 background subagents launched** — 2 completed (UBQ-c, UBQ-d); 4 still running (A NPZ cleanup, H trajectory skeletons, I RMSF/RSALOR, D walltime classification).

**Hard deadlines:** OSF deposit by 2026-05-15 (target 2026-05-13). Sub 1.2 close 2026-05-16.

**Your immediate task:** verify state below, wait for the 4 in-flight subagents to land + 9 in-flight jobs to dispatch, run periodic check-ins, surface UBQ probe verdicts to user when they land.

---

# CURRENT JOB STATE (squeue -u rag88)

All on `scavenge_gpu` Standard Tier (10× cheaper billing):

| JobID | Tag | Work | Walltime | State |
|-------|-----|------|----------|-------|
| 10567503 | q6wmsv5n | MACE WW NPT 5 ns | 23:59 | PENDING |
| 10567504 | q6gpsv9k | MACE GB3 NPT 5 ns | 23:59 | PENDING |
| 10567505 | g7p4tv8m | SO3LR GB3 5 ns rescue (neutral prep) | 1-00:00 | PENDING |
| 10567506 | n5h6kx9q | SO3LR NTL9 5 ns rescue (neutral prep) | 1-00:00 | PENDING |
| 10567507 | w8q4r3xz | SO3LR WW 5 ns rescue (float64+dt=0.25fs+chain=5) | 1-00:00 | PENDING |
| 9449458 | x9sok7yl | BioEmu batch 2 array (41 idx) | 1-00:00 | PENDING |
| 9449459 | l5uw4lsy | BioEmu batch 2 array (41 idx, CD19 excluded) | 23:59 | PENDING |
| **10622876** | **q6kz3m8x** | **NTL9 50 ps probe (UBQ option c substitute)** | 5:55 | PENDING |
| **10622885** | **q6uadt05** | **UBQ_alt 1XQQ 50 ps probe (UBQ option d)** | 5:55 | PENDING |

User's other-project jobs (do NOT touch): 9611901 cc_tmol_qq, 10618193 cc_tmol_qqd.

**Dispatch is slow** — scavenge has PriorityTier=2 behind ~178+ scavenge users. Fair-share `pi_mg269` = 0.0167 (slowly recovering). If no dispatches by 2026-05-09, surface contingency to move MACE production back to Standard `gpu_h200` (10× more expensive, **requires user approval per 3× partition rule** — task #24).

# JOB ACCOUNTING (priority SU)

- Tracker: 231.5 / 250 SU used (cap reduced from 800)
- Auto-cancel event 2026-05-02 22:58Z: WW SO3LR rescue 10463305 cancelled; recreated as 10470003 → eventually became 10567507. Notification at `shared/help-needed/head-1.2-su-budget-auto-cancel-2026-05-02T22-58-45Z.md`.
- All 7 production jobs are on scavenge_gpu (free billing). Only UBQ option (c)+(d) probes might consume small priority SU (but submitted on scavenge_gpu in the end — also free).

# RECIPE — LOCKED, DO NOT CHANGE

**MACE-OFF24 NPT Round 3 recipe** (per `shared/notes/1.2-mace-npt-fixed.md`):
After `MLPotential('mace-off24-medium').createMixedSystem(...)`:
1. `add_protein_sentinel_bonds(hybrid_system, topology, protein_atoms)` — fixes openmm-ml issue #91
2. `add_protein_hbonds_constraints(hybrid_system, topology, protein_atoms)` — fixes unconstrained-H instability
3. `MonteCarloBarostat(1 atm, 300 K, freq=25)` — ALWAYS-ON from build
4. `LangevinMiddleIntegrator(300 K, 1 ps⁻¹, dt=1 fs)`
5. OpenCL platform only (CUDA broken on H200)

**Validates on:** WW (test_P 100 ps clean), GB3 (probe 25 ps clean during TIMEOUT).
**Does NOT generalize to:** UBQ (~17K solvated atoms — NaN @ 7-9.6 ps regardless of dt). Pattern architectural, not numerical.

**SO3LR rescue protocol** (per `shared/notes/1.2-so3lr-rescue-results.md`, OSF v3 §4):
- Net-charged proteins: mandatory neutral-protonation re-prep (D/E → ASH/GLH; K/R → LYN). GB3+NTL9 PASSED 500 ps gates.
- WW: float64+dt=0.25fs+NHC chain=5 (numerical fix; not chemical).
- Production: 5 ns target on Standard Tier `gpu` (now scavenge_gpu).

# SCRIPT EDITS APPLIED (3 optimization rounds + audit + UBQ-c/d additions)

`output/scripts/mace_hybrid_npt_prod.py`:
- Constant tensors `_total_charge_t` / `_total_spin_t` pre-allocated outside callback
- Dropped redundant `_torch.set_default_dtype` from callback
- `NAN_CHECK_INTERVAL_STEPS` 1000 → 5000
- `CHECKPOINT_INTERVAL_STEPS` 5000 → 25000
- `integrator.setConstraintTolerance(1e-4)` (was default 1e-5)
- Dropped `speed=True` from StateDataReporter
- `REPORT_INTERVAL_PS` 1.0 → 5.0
- `NPT_EQUIL_PS` 50 → 25
- Keepalive cadence 5 → 10 min
- `check_nan` drops `getForces=True` (~0.5% throughput)
- `MAX_MIN_ITER` 2000 → 500
- `MACE_HYBRID_DT_FS` env-var support (defaults to 1.0)
- `PROTEIN_DEFAULTS` extended with `ntl9` (UBQ option c substitute) and `ubq_alt` (UBQ option d, 1XQQ NMR model 1)

`output/scripts/so3lr_rescue_runner.py`:
- `md_steps` 1000 → 10000 (with bug-fix on ps_per_cycle calculation)
- `--save-buffer` 50 → 5 (preserves cadence at 25 ps with 10× larger md_steps)
- `--buffer-sr/lr` AT SO3LR DEFAULTS 1.25/1.25 (audit reverted aggressive 1.15/1.10 — silent NL underflow risk at t=0)

`output/scripts/so3lr_rescue.sbatch`:
- `JAX_COMPILATION_CACHE_DIR=/home/rag88/.cache/jax_compilation`
- `JAX_PERSISTENT_CACHE_MIN_ENTRY_SIZE_BYTES=0`
- `XLA_FLAGS="--xla_gpu_triton_gemm_any=true --xla_gpu_enable_latency_hiding_scheduler=true"`

`output/scripts/submit_mace_npt_prod.sh`:
- Added `scavenge_gpu` partition support
- `OMP_NUM_THREADS=4`, `MKL_NUM_THREADS=4`, `OPENBLAS_NUM_THREADS=4`
- `OMP_PROC_BIND=close`, `OMP_PLACES=cores`
- `ntl9` and `ubq_alt` cases added
- Wired with `prio_su_tracker.sh` pre-check + `prio_register_job.sh` auto-register (priority_gpu only)

`output/scripts/submit_so3lr_rescue_production.sh`:
- Added `--scavenge` flag for scavenge_gpu submissions
- Same priority SU pre-check + auto-register wiring

# SU ENFORCEMENT INFRASTRUCTURE (new 2026-05-02/03)

- `output/scripts/prio_su_tracker.sh` — current SU accounting, filters by `q6*` name OR registry job_id
- `output/scripts/prio_su_enforce.sh` — projects in-flight SU + auto-cancels offenders + writes `shared/help-needed/head-1.2-su-budget-auto-cancel-<ts>.md` notification
- `output/scripts/prio_register_job.sh` — adds job to registry post-submission
- `output/scripts/prio_su_budget.json` — `budget_su: 250.0` (current cap)
- `output/scripts/prio_su_registry.json` — registry of project priority jobs

# OSF V3 EDITS APPLIED 2026-05-03

`phases/phase-1/subphase-1.2/output/osf-prereg-v3.md`:
1. **§4 SO3LR row** — committed to mandatory neutral-protonation re-prep methodology for net-charged proteins (D-OSF-SO3LR resolved by user 2026-05-03)
2. **§7.1 T1 row** — multi-path D2 G1 evidence; UBQ pivots to NVT (architectural fallback)
3. **§10 line 378** — narrative updated (UBQ NPT non-generalization; planned NPT set is {WW, GB3, GB1, NTL9})
4. **§12.3** — code tag string `osf-prereg-v2` → `osf-prereg-v3`
5. **§13** — amendment provisions cleaned (v4 schedule for Sub 1.4 lock)
6. **Closing line** — "End of pre-registration v3" with full v2→v3 changelog

# DOC AUDIT BATCH 1 APPLIED 2026-05-03 (13 files)

Truth-of-record fixes — all dashboards + cross-agent notes + status reports current as of 2026-05-03 ~20:30Z:
1. `shared/notes/1.2-mace-npt-fixed.md` — UBQ caveat + per-protein generalization status
2. `phases/phase-1/subphase-1.2/status/task-009-status.md` — SUPERSEDED banner
3. `dashboards/master-status.md` — frontmatter + status + decision-log entries (3 new)
4. `dashboards/active-subphase.md` — current SLURM inventory + 3-round optimization audit
5. `dashboards/gate-tracker.md` — frontmatter fix + D2 multi-path
6. `dashboards/compute-budget.md` — scavenge tier + SU enforcement section
7. `shared/notes/1.2-mace-npt-prod-launch.md` — probe outcomes + UBQ-c/d additions
8. `shared/notes/1.2-mace-npt-stability.md` — §8 UBQ + 3 rounds + scavenge
9. `shared/notes/1.2-so3lr-rescue-results.md` — gate verdicts + 5 ns prod + production-protocol commit
10. `phases/phase-1/subphase-1.2/status/task-001-status.md` — 2026-05-03 update
11. `phases/phase-1/subphase-1.2/status/task-002-rescue-status.md` — gate verdicts
12. `shared/notes/operational-practices.md` — scavenge_gpu policy + SU enforcement + OSF deposit checklist + doc audit cadence
13. `shared/notes/1.2-closure-master-plan.md` — annotated 2026-05-02/03 actuals + R6/R7/R8 risks
14. `shared/help-needed/head-1.2-su-budget-auto-cancel-2026-05-02T22-58-45Z.md` — RECREATED stub (auditor flagged absent)

CLAUDE.md MUST-READ updated with 6 critical 2026-05-02/03 docs.

# OPEN USER DECISIONS (still PENDING)

| ID | Decision | Status |
|----|----------|--------|
| **D-UBQ-1** | UBQ NPT path. User picked **(c)+(d)** — both probes IN FLIGHT (10622876 NTL9 substitute + 10622885 UBQ_alt 1XQQ). Verdict via probe completions. Fallback chain: (d)→(c)→(b NVT pivot). | IN-FLIGHT |
| **R6/R7/R8 risk-register** | Reviewer-flagged risks: scavenge preemption integrity, per-protein recipe-fallback compute multiplier, prio_su_enforce.sh failure modes. Already added to closure-master-plan. Task #22 — could be elevated to operational-practices for Sub 1.4+. | LOW URGENCY |
| **Sub 1.4 planning hooks** | Task #23 — write summary doc for PlannerAI. | LOW URGENCY (PlannerAI handles this when invoked) |
| **3× partition rule** | Task #24 — recorded in operational-practices §scavenge_gpu policy. **Standing rule:** ask before any partition move ≥3× more expensive (i.e., off scavenge to Standard, ever). | RECORDED |

# IN-FLIGHT BACKGROUND SUBAGENTS (4 remaining)

Launched 2026-05-04 ~00:00Z with `Agent` tool, run_in_background=true:
- **Item A — BioEmu NPZ cleanup** (subagent ad4c3017610976831): adds post-success NPZ cleanup gated on xtc-write completing. Saves ~43% storage.
- **Item H — trajectory analysis skeletons** (subagent a690a20f8e4384b1a): adapts Sub 1.1 mace_analyze.py + task007_analyze.py for Sub 1.4 needs (S2, RMSF, density/T/P, contacts). CPU/login work, zero SU.
- **Item I — RMSF + RSALOR pre-compute for batch1** (subagent aac5894fd33506375): extracts features for Sub 1.3 ML pipeline. CPU/login work.
- **Item D — walltime 24h→12h classification proposal** (subagent a7a141bdd631dc472): documents proposal only; no edits to PENDING jobs.

When each lands, you'll get a task-notification with full report. **Trust their reports, don't duplicate work.**

Already-completed subagents (review their reports if needed):
- UBQ-c (a9baa710e4defc30d): NTL9 selected, probe 10622876 submitted
- UBQ-d (a51d996fa6d3d7b94): UBQ_alt 1XQQ NMR model 1, probe 10622885 submitted

# IN-FLIGHT JOB MONITORING (next 24-72 hr)

**Critical signals to watch:**
- **NTL9 probe (10622876 q6kz3m8x)** — when it dispatches: ~80 min run for 50 ps target on H200. PASS = recipe generalizes to NTL9 (390 ATOM records, smaller than GB3); criterion #1 substitution viable.
- **UBQ_alt probe (10622885 q6uadt05)** — same throughput. PASS past 9.6 ps = 1XQQ NMR structure stabilizes UBQ; falsifies "architectural" hypothesis. FAIL ≤9.6 ps = same pattern as 1UBQ; option (d) falsified, fall back to (c) NTL9 or (b) NVT.
- **5 production jobs** — 5 ns runs, ~12 hr SO3LR / 47-75 hr MACE WW/GB3. Will queue on scavenge for some time.

# WHAT'S LOCKED — DO NOT CHANGE

- **Round 3 MACE NPT recipe** (per OSF v3 §4: sentinel + HBonds + dt=1 fs + MCB freq=25). All edits must preserve.
- **OSF v3 (now revised)** — pre-deposit-ready. Don't make further edits without user approval.
- **CLAUDE.md MUST-READ list** — current.
- **env-mace, env-so3lr, env-bioemu** — never modify.
- **Conda path** — `/apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh` (verbatim).
- **scavenge_gpu pivot** — all 7 closure jobs there. **Don't move off without user approval (3× rule).**

# WHAT'S OPEN — ROOM TO ACT WITHOUT FURTHER USER CLEARANCE

- Periodic squeue + sshare check-ins (every 30-60 min)
- Updates to dashboards as facts change (master-status, active-subphase, gate-tracker, compute-budget)
- Status report appendices when new evidence lands
- Cross-agent notes when findings affect other tracks
- prio_su_enforce.sh re-runs if budget concerns emerge
- Submit production runs only IF probes pass — DO NOT submit production for UBQ until probe verdicts in
- Standard Tier `gpu` Sub 1.2 closure work (no priority SU cost) — within Sub 1.2 budget

# WHAT REQUIRES USER APPROVAL

- Any partition move ≥3× more expensive (per task #24)
- Priority SU spend that would push past 250 cap
- Any OSF v3 edit beyond what's already applied
- Any CLAUDE.md edit
- Cancellation of jobs that have been RUNNING + accumulating data (free-tier cancellation of PENDING is fine)
- Any scope-revision help-needed escalation (PlannerAI sees these and may re-plan)

# OPERATIONAL PRACTICES — KEEP THESE GOING

- **Cryptic 8-char job names**, q6 prefix preferred (q6XXXXXX). Never descriptive names.
- **scavenge_gpu first** — 1/10 Standard billing. Eligible workloads have checkpoint/restart support (all our scripts do).
- **Diagnostic-first rule** — small probe (priority_gpu 50 ps OR scavenge_gpu) before any expensive submission.
- **Doc-audit cadence** — when execution state changes substantively, update dashboards + cross-agent notes within the same session, not days later.
- **Trust subagent reports** — don't re-do their work. Verify via spot-check (squeue, scontrol, `ls`) only.

# CRITICAL FILES YOU MUST READ

In order, before doing anything:
1. **THIS FILE** — `phases/phase-1/subphase-1.2/handoff-successor-2026-05-04.md`
2. `phases/phase-1/subphase-1.2/CLAUDE.md` — your spec
3. `shared/notes/1.2-closure-master-plan.md` — strategy backbone (urgency=critical)
4. `shared/notes/1.2-mace-npt-fixed.md` — locked recipe + UBQ caveat (urgency=critical)
5. `shared/notes/1.2-so3lr-rescue-results.md` — chemistry rescue + production protocol (urgency=critical)
6. `shared/help-needed/head-1.2-mace-ubq-non-generalization.md` — UBQ escalation + options c/d state (urgency=critical)
7. `shared/notes/operational-practices.md` — scavenge policy + SU enforcement (recently appended)
8. `dashboards/master-status.md` + `dashboards/active-subphase.md` — current job state
9. `phases/phase-1/subphase-1.2/output/osf-prereg-v3.md` — deposit-ready document (post-2026-05-03 edits)

# FIRST ACTIONS

1. Read this file end-to-end.
2. Spot-check job state: `squeue -u rag88` — confirm 9 of our jobs PENDING (7 production + 2 UBQ probes).
3. Spot-check tracker: `bash phases/phase-1/subphase-1.2/output/scripts/prio_su_enforce.sh --dry-run` — confirm WITHIN_BUDGET.
4. Wait for the 4 in-flight subagents to land. When task-notifications arrive, read the report and spot-check via filesystem (don't re-launch unless required).
5. Surface NTL9 + UBQ_alt probe verdicts to user as soon as they terminate. **Apply decision tree from `head-1.2-mace-ubq-non-generalization.md` §UBQ option (d)**:
   - Both PASS → submit corresponding 5 ns production on scavenge_gpu; criterion #1 has multiple paths
   - NTL9 PASS / UBQ_alt FAIL → criterion #1 substitution; UBQ stays NVT or scope-revision
   - NTL9 FAIL / UBQ_alt PASS → keep UBQ via 1XQQ; surprise positive result
   - Both FAIL → escalate (b) NVT pivot or PlannerAI scope-revision per closure plan
6. Periodic check-ins via ScheduleWakeup at 30-60 min cadence while jobs PENDING.
7. **OSF deposit Hard deadline 2026-05-15 — preferred 2026-05-13.** Surface to user a few days before to confirm.

# KNOWN GOTCHAS

- `prio_su_enforce.sh --dry-run` is safe; without `--dry-run` it will scancel jobs that exceed projected budget. Use `--dry-run` for routine checks.
- Doc audit found `head-1.2-su-budget-auto-cancel-*.md` was missing despite enforce script reporting it wrote. Recreated 2026-05-03 from audit trail. If enforce fires again, verify file lands.
- `task-009-status.md` has SUPERSEDED banner; future readers should follow it to `1.2-mace-npt-fixed.md`.
- `submit_mace_npt_prod.sh` `--check-fit` mode for projected SU pre-check on new submissions is NOT yet wired (task #17 follow-up). Current pre-check uses `prio_su_tracker.sh` which only sees current usage.
- Existing handoff-notes.md (2026-05-02 overnight) is OUTDATED — DO NOT follow that doc; this file (handoff-successor-2026-05-04.md) supersedes.
