---
title: Sub 1.2 head-1.2 successor handoff (2026-05-05 evening)
author: head-1.2 (this session, 2026-05-04 ~10:30Z → 2026-05-05 ~22:00Z)
date: 2026-05-05T22:00:00Z
supersedes: handoff-successor-2026-05-04.md (2026-05-04 ~00:30Z; still useful as historical context for events 2026-05-02 → 2026-05-04)
purpose: Complete state transfer to the next head-1.2 with no loss. Encode every action this session took + everything still in flight.
---

# READ THIS FIRST (TL;DR — 60 seconds)

You are **head-1.2**, the HeadAI for subphase 1.2. The previous (2026-05-04) successor session ran from 2026-05-04 ~10:30Z to 2026-05-05 ~22:00Z. In that window, no SLURM job dispatched (10 jobs PENDING the entire session). What changed:

1. **Doc audit batch 2 applied** (14 truth-of-record edits across 9/12 audited files; pre-staged `completion-report.md` skeleton + `1.2-osf-deposited.md` stub).
2. **Storage tier policy** — encoded as recommendation #9 in `completion-report.md §13` (per user directive 2026-05-04). PlannerAI to elevate to `operational-practices.md` on next planning cycle.
3. **Compute-cost vs quality directive** — encoded as recommendation #10 in `completion-report.md §13` (per user directive 2026-05-05). Same elevation path.
4. **Round-4 optimization studies** completed for MACE, SO3LR, BioEmu — at `output/optimization-round-4-{mace,so3lr,bioemu}.md`. Net verdict: code-side is near-exhausted (3-5% per workload at most). Partition is the live knob.
5. **MACE + SO3LR round-4 small wins APPLIED 2026-05-05** to `mace_hybrid_npt_prod.py` and `so3lr_rescue.sbatch`. Forward-looking only (in-flight jobs use R3 scripts).
6. **BIG ACTION: BioEmu walltime + partition reorg APPLIED 2026-05-05.** scancelled 9449458 + 9449459. Submitted 3 new arrays: 10730244 (Standard `gpu`, 6h, 53 short proteins L<200), 10730245 (scavenge_gpu, 12h, 18 medium L=200-499), 10730246 (scavenge_gpu, 24h, 11 long L≥500). Estimated +205 Standard SU at most; saves 7-9 days dispatch.
7. **Comprehensive disk-usage survey** done. CompBio footprint: 981 MiB home / ~84.4 GiB project (conda envs) / ~426 GiB scratch. Group `pi_mg269` project tier at 95% bytes / 76% files (binding constraint NOT caused by us).
8. **GitHub push** (commit 3a79078, 2026-05-04). 194 files, 38,506 insertions. Working tree has accumulated more changes since then — uncommitted.
9. **Updated CLAUDE.md MUST-READ context** carries forward from predecessor.
10. **Round-4 OPS scripts under their own commit policy:** the 3 new BioEmu sbatches + R4 code edits + new docs are uncommitted in the working tree as of 2026-05-05 22:00Z. Push when user authorizes.

**Hard deadlines:** OSF deposit by **2026-05-15** (target 2026-05-13). Sub 1.2 close **2026-05-16**. Today is **2026-05-05** — 10 days to OSF deadline / 11 to subphase close.

**Your immediate task:** verify state below; the periodic 30-min wakeup loop is active; surface UBQ probe verdicts the moment they land; surface BioEmu Standard `gpu` first-dispatch the moment it lands.

---

# CURRENT JOB STATE (squeue -u rag88 as of 2026-05-05 ~22:00Z)

All 10 of our jobs are PENDING with reason `Priority`. No transitions in 36+ hours.

| JobID | Tag | Work | Partition | Walltime | State |
|-------|-----|------|-----------|----------|-------|
| 10567503 | q6wmsv5n | MACE WW NPT 5 ns | scavenge_gpu (h200) | 23:59 | PENDING |
| 10567504 | q6gpsv9k | MACE GB3 NPT 5 ns | scavenge_gpu (h200) | 23:59 | PENDING |
| 10567505 | g7p4tv8m | SO3LR GB3 5 ns rescue (neutral prep) | scavenge_gpu (rtx_5000) | 1-00:00 | PENDING |
| 10567506 | n5h6kx9q | SO3LR NTL9 5 ns rescue (neutral prep) | scavenge_gpu (rtx_5000) | 1-00:00 | PENDING |
| 10567507 | w8q4r3xz | SO3LR WW 5 ns rescue (float64+dt=0.25fs+chain=5) | scavenge_gpu (rtx_5000) | 1-00:00 | PENDING |
| **10622876** | **q6kz3m8x** | **NTL9 50 ps probe (UBQ option-c substitute)** | scavenge_gpu (h200) | 5:55 | PENDING |
| **10622885** | **q6uadt05** | **UBQ_alt 1XQQ 50 ps probe (UBQ option-d)** | scavenge_gpu (h200) | 5:55 | PENDING |
| **10730244** | **q6sht3az** | **BioEmu batch 2 SHORT cohort (53 proteins L<200)** | **`gpu` (Standard, rtx_5000_ada)** | 6:00 | PENDING |
| **10730245** | **q6med7kp** | **BioEmu batch 2 MEDIUM cohort (18 proteins L=200-499)** | scavenge_gpu (rtx_5000) | 12:00 | PENDING |
| **10730246** | **q6lng5wm** | **BioEmu batch 2 LONG cohort (11 proteins L≥500)** | scavenge_gpu (rtx_5000) | 23:59 | PENDING |

User's other-project jobs (DO NOT touch): cycling `cc_tmol_q5` instances, currently 10767130 on `gpu` (13:00 walltime).

**Standard `gpu` short cohort (10730244 q6sht3az) is the canary:** PriorityTier=4 + 6h walltime. If even ONE array task starts RUNNING, that confirms the BioEmu unblock worked. As of 2026-05-05 ~22:00Z it has NOT yet dispatched.

**Cohort indices (precise):**
- 10730244 (short, 53 proteins): array `[20-23,44-92]`
- 10730245 (med, 18 proteins): array `[11,18-19,24-38]`
- 10730246 (long, 11 proteins): array `[12-17,39-43]`

# JOB ACCOUNTING

- **Priority SU tracker (per `prio_su_enforce.sh --dry-run`):** 231.5 / 250 SU used. WITHIN_BUDGET. Buffer = 18.5 SU. **Cap is operator-controlled** via `output/scripts/prio_su_budget.json` (currently `budget_su: 250.0`). Reduced 800 → 250 per user directive 2026-05-02.
- **Standard SU:** Phase 1 Alpha-M budget remaining ~2,996 GPU-hrs at session start; minimal Standard burn this session (only the 53-protein BioEmu short cohort moved to Standard `gpu`, est. +205 SU). No standard SU enforcement script — tracked in `dashboards/compute-budget.md`.
- **Fair-share (load-bearing for dispatch ETA):**
  - `pi_mg269/rag88` (Standard) LevelFS = **0.27** — DEPRESSED. Dispatch suppression on `gpu`, `gpu_h200`, `scavenge_gpu` etc. fed from this account.
  - `prio_mg269/rag88` (Priority) LevelFS = **18.1** — CREDIT-RICH. Underused. Priority Tier (PriorityTier=8) is our natural lever, but the 250 SU operator-cap is the constraint.

# RECIPES — LOCKED, DO NOT CHANGE

**MACE-OFF24 NPT Round 3 recipe** (per `shared/notes/1.2-mace-npt-fixed.md`):
After `MLPotential('mace-off24-medium').createMixedSystem(...)`:
1. `add_protein_sentinel_bonds(hybrid_system, topology, protein_atoms)` — fixes openmm-ml issue #91 singleton-molecule scaling
2. `add_protein_hbonds_constraints(hybrid_system, topology, protein_atoms)` — fixes unconstrained-H instability
3. `MonteCarloBarostat(1 atm, 300 K, freq=25)` — ALWAYS-ON from build
4. `LangevinMiddleIntegrator(300 K, 1 ps⁻¹, dt=1 fs)`
5. OpenCL platform only (CUDA broken on H200)

**Validates on:** WW (test_P 100 ps clean), GB3 (probe 25 ps clean during TIMEOUT).
**Does NOT generalize to:** UBQ at 17K-atom solvated scale (NaN @ 7-9.6 ps regardless of dt halving 1.0/0.5/0.25 fs). Pattern architectural, not numerical.

**SO3LR rescue protocol** (per `shared/notes/1.2-so3lr-rescue-results.md` + OSF v3 §4):
- **Net-charged proteins:** mandatory neutral-protonation re-prep (D/E → ASH/GLH; K/R → LYN). GB3 + NTL9 PASSED 500 ps gates 2026-05-02.
- **WW (small system):** float64 + dt=0.25 fs + NHC chain=5 + thermo=200 dt-units (numerical fix; not chemical).
- **Production:** 5 ns target on Standard Tier `gpu` (now scavenge_gpu).
- **Buffer-sr/lr:** kept at SO3LR defaults 1.25/1.25 per audit-revert (silent NL underflow risk at t=0 if tightened).

# ROUND 4 SCRIPT EDITS APPLIED 2026-05-05 (forward-looking only)

Per user approval 2026-05-05 of round-4 small code wins. **In-flight jobs were submitted before R4 and use R3 scripts; they are unaffected.** R4 takes effect for any new submission OR any auto-REQUEUE of preempted scavenge jobs.

`output/scripts/mace_hybrid_npt_prod.py` (4 edits, all marked `# R4-2026-05-05:`):
- **Line ~349:** `check_nan` accepts optional pre-fetched `state=None` arg (defensive API refactor — current call sites unchanged so 0% gain today, but unlocks future state-threading callers per round-4 report)
- **Line ~837:** dropped `kineticEnergy=True, totalEnergy=True` from `StateDataReporter(...)` — append branch
- **Line ~854:** same drop in new-file branch
- **Line ~907:** progress-JSON write wrapped in `if current_step % CHECKPOINT_INTERVAL_STEPS == 0` (every 25k steps now, not every chunk)

`output/scripts/so3lr_rescue.sbatch` (3 edits, all marked `# R4-2026-05-05:`):
- **Line ~94:** `XLA_FLAGS` extended with `--xla_gpu_enable_async_collectives=true`
- **Line ~101:** added `export XLA_PYTHON_CLIENT_PREALLOCATE=false`
- **Line ~105:** added `export CUDA_MODULE_LOADING=LAZY`

**Diagnostic:** `~/.cache/jax_compilation/` is COLD (does not exist yet). First SO3LR submission post-R4 pays full ~30-60 s JIT compile; subsequent runs hit cache. The sbatch's `mkdir -p` will create the directory on first run.

**BioEmu R4 wins:** applied via the 3 new sbatch wrappers (see next section): `--cpus-per-task=4` (was 2); `--mem=24G` for short cohort (was 40G blanket); R4 reporter trim N/A for BioEmu (it doesn't use OpenMM `StateDataReporter`).

# BIOEMU REORG APPLIED 2026-05-05

**Action chain (executed 2026-05-05 ~09:55Z by reorg subagent):**
1. Read `batch2_manifest.csv` for 92-protein name + length.
2. Determined PENDING task indices in 9449458 + 9449459 (82 PENDING).
3. Classified by length: 53 short (L<200) + 18 med (200-499) + 11 long (≥500). Sums to 82 ✓.
4. Created 3 new sbatch wrappers in `output/scripts/`:
   - `bioemu_batch2_short_6h_std.sbatch` — `--partition=gpu --time=06:00:00 --mem=24G --cpus-per-task=4 --gres=gpu:rtx_5000_ada:1`
   - `bioemu_batch2_med_12h_scav.sbatch` — `--partition=scavenge_gpu --time=12:00:00 --mem=40G --cpus-per-task=4 --gres=gpu:rtx_5000_ada:1`
   - `bioemu_batch2_long_24h_scav.sbatch` — `--partition=scavenge_gpu --time=23:59:00 --mem=40G --cpus-per-task=4 --gres=gpu:rtx_5000_ada:1`
5. Submitted all 3 → captured new SLURM IDs.
6. **Verified 3 new arrays in queue BEFORE scancelling old.** Order strictly enforced — no work lost.
7. scancelled 9449458 + 9449459.
8. Re-verified squeue (3 new arrays present, old gone).
9. Updated `dashboards/master-status.md` (timestamp + decision-log + Subphase status + Gamma row), `dashboards/active-subphase.md` (replaced rows), `shared/notes/1.2-bioemu-batch2-passrates.md` (appended `## 2026-05-05 reorg`), `phases/phase-1/subphase-1.2/status/task-004-status.md` (appended `## Update 2026-05-05`).

**Why the reorg:** 24h-blanket walltime hurt scavenge backfill; 76 of 92 proteins finish ≤4h actual per BioEmu round-4 empirical timing (1.21e-4 min per L×ns). Group fair-share LevelFS=0.27 was depressing dispatch on both Standard and scavenge for our pi_mg269 account — the partition move alone wouldn't help, but shorter walltime = better backfill candidate. The L<200 cohort moved to Standard `gpu` PriorityTier=4 to additionally lift it above scavenge users. Estimated cost: +205 Standard SU; estimated benefit: 7-9 days saved end-to-end per BioEmu R4 report.

**Locked invariants preserved:** RTX 5000 Ada GPU type, env-bioemu env, GPU keepalive, length-aware `batch_size_100`, oversampling formula `num_samples = ceil(2000 / pass_rate * 1.3)`, disorder pre-screen, NPZ cleanup logic, OSF v3 §7 invariants (denoising_steps), CD19_HUMAN exclusion.

# OSF V3 STATE (DEPOSIT-READY — DO NOT EDIT)

`phases/phase-1/subphase-1.2/output/osf-prereg-v3.md` is **deposit-ready** following 6 internal-consistency fixes applied 2026-05-03 (5 trivial + 1 substantive D-OSF-SO3LR §4 commit to neutral-protonation methodology for net-charged proteins).

- **Target deposit:** Wed 2026-05-13 (preferred) / Thu 2026-05-14 (backup) / Fri 2026-05-15 (HARD).
- **User deposits manually on OSF and provides DOI.** head-1.2 records DOI + SHA256 in `shared/notes/1.2-osf-deposited.md` (stub already pre-staged 2026-05-04).
- **Standing rule:** any further OSF v3 edit requires explicit user approval. Treat the file as frozen.

The `1.2-osf-deposited.md` stub has frontmatter status `STUB — awaits user OSF deposit + DOI`, with `[PENDING]` placeholders for DOI / deposit date / SHA256 / OSF project URL. Promote to `urgency: critical` post-deposit; mirror v2→v3 changelog from OSF v3 head matter.

# SU ENFORCEMENT INFRASTRUCTURE

- `output/scripts/prio_su_tracker.sh` — current SU accounting; filters by `q6*` job-name OR registry job_id
- `output/scripts/prio_su_enforce.sh` — projects in-flight SU + auto-cancels offenders + writes notification at `shared/help-needed/head-1.2-su-budget-auto-cancel-<ts>.md`
- `output/scripts/prio_register_job.sh` — adds job to registry post-submission
- `output/scripts/prio_su_budget.json` — `budget_su: 250.0`
- `output/scripts/prio_su_registry.json` — runtime mutating; not committed
- `output/scripts/prio_su_status.json` — runtime mutating; not committed
- `output/scripts/prio_su_tracker_doc.md` — operator documentation

Wrappers (`submit_mace_npt_prod.sh`, `submit_so3lr_rescue_production.sh`) call enforce as a pre-check on `priority_gpu` submissions only (Standard + scavenge_gpu skip — they're not in the priority pool).

**Use:** `bash phases/phase-1/subphase-1.2/output/scripts/prio_su_enforce.sh --dry-run` for routine checks (safe; no scancel). Without `--dry-run` it scancels offending jobs.

# DOC AUDIT BATCHES APPLIED

**Batch 1 (predecessor session, 2026-05-03 ~20:30Z, 13 files + 1 recreated stub):** see predecessor's handoff doc.

**Batch 2 (this session, 2026-05-04 ~11:50Z, 14 minimal Edit operations across 9 of 12 audited files):**
1. `dashboards/master-status.md` — frontmatter + Subphase status row + Decisions Needed updates
2. `dashboards/active-subphase.md` — frontmatter + Live SLURM job inventory header retitled + 2 new probe rows appended
3. `dashboards/gate-tracker.md` — frontmatter only (substance unchanged)
4. `dashboards/compute-budget.md` — frontmatter only
5. `shared/notes/1.2-mace-npt-fixed.md` — frontmatter + UBQ option-c/d in-flight block in "Generalization status"
6. `shared/notes/1.2-mace-npt-prod-launch.md` — frontmatter + new "UBQ alternate-starting-structure (option d)" section
7. `shared/notes/1.2-mace-npt-stability.md` — new §9 "UBQ option-c + option-d probes IN FLIGHT (2026-05-04)"
8. `shared/notes/1.2-so3lr-rescue-results.md` — no drift (SO3LR doc was already 2026-05-03 current)
9. `shared/notes/1.2-closure-master-plan.md` — frontmatter + "Annotations from 2026-05-04" block
10. `shared/notes/operational-practices.md` — no drift
11. `phases/phase-1/subphase-1.2/status/task-001-status.md` — frontmatter + "Update 2026-05-04 (05:00Z)" prepended
12. `phases/phase-1/subphase-1.2/status/task-002-rescue-status.md` — no drift

**Batch 3 (this session, 2026-05-05 ~09:50Z, MACE+SO3LR R4 docs subagent):**
13. `dashboards/active-subphase.md` — appended R4 row to "Optimization rounds applied" table
14. `shared/notes/1.2-mace-npt-stability.md` — added R4 (2026-05-05) subsection
15. `shared/notes/1.2-so3lr-rescue-results.md` — added R4 (2026-05-05) subsection
16. `output/optimization-round-4-mace.md` — frontmatter status → APPLIED 2026-05-05
17. `output/optimization-round-4-so3lr.md` — frontmatter status → APPLIED 2026-05-05

**Batch 4 (this session, 2026-05-05 ~10:00Z, BioEmu reorg subagent):** dashboards + status report + cross-agent note documenting the reorg (see BIOEMU REORG section above).

# OPEN USER DECISIONS

| ID | Decision | Status as of 2026-05-05 22:00Z |
|----|----------|--------------------------------|
| **D-UBQ-1** | UBQ NPT path. User picked **(c)+(d)** — both probes IN FLIGHT (10622876 NTL9 substitute + 10622885 UBQ_alt 1XQQ). Verdicts pending dispatch. Fallback: (d)→(c)→(b NVT pivot). | IN-FLIGHT (probes have not dispatched yet — same scavenge fair-share suppression) |
| **D-OSF-SO3LR** | Resolved 2026-05-03 via OSF v3 §4 substantive edit (commits to neutral-protonation methodology for net-charged proteins). | RESOLVED |
| **R6/R7/R8 risk-register elevation** | Forward-looking; PlannerAI handles when invoked. | LOW URGENCY (deferred) |
| **Sub 1.4 planning hooks** | Forward-looking; PlannerAI handles when invoked next. PlannerAI reads completion-report.md (with §13 recommendations 1-10) + shared/notes/. | LOW URGENCY (deferred) |
| **3× partition rule** | Recorded in operational-practices §scavenge_gpu policy + completion-report §13 #10. | RECORDED |
| **Working-tree push** | Working tree has accumulated changes since 2026-05-04 push (commit 3a79078). Not yet pushed. | AWAITING USER DIRECTION |
| **2026-05-09 contingency trigger** | If no scavenge dispatch by 2026-05-09, surface contingency to move MACE production to Standard `gpu_h200` (10× more SU) — requires user approval per 3× partition rule. | 4 days out |

# IN-FLIGHT BACKGROUND SUBAGENTS — STATE AS OF 2026-05-05 22:30Z (forensic filesystem confirmation)

**Predecessor session's 4 background subagents (launched 2026-05-04 ~00:00Z) — DEFINITIVE STATUS as of 2026-05-05 22:30Z (forensic filesystem confirmation):**

- **Item A (BioEmu NPZ cleanup, ad4c3017610976831): COMPLETED.** NPZ cleanup logic IS in production. Baked into `output/scripts/bioemu_batch2.sbatch` and `bioemu_batch2_24h.sbatch` (both at mtime 2026-05-03 23:46Z) under the comment header `# Post-success NPZ cleanup (2026-05-03 patch — head-1.2 Item A storage saver)`. The cleanup runs only when (1) `EXIT_CODE == 0`, (2) `samples.xtc` exists at `OUTPUT_DIR`, (3) NPZs are non-empty — gated on full success per the design. The 3 new BioEmu sbatches created 2026-05-05 (short_6h_std, med_12h_scav, long_24h_scav) inherited this logic via the reorg subagent's "preserve all settings from bioemu_batch2_24h.sbatch" instruction. **All current and future BioEmu submissions will execute the cleanup.**

- **Item H (trajectory analysis skeletons, a690a20f8e4384b1a): DID NOT LAND.** No analysis script files matching the spec (`mace_analyze`, `task007_analyze`, `S2_*`, `density_T_P*`, `contacts*`) exist anywhere in `phases/phase-1/subphase-1.2/output/`. No `output/scripts/analysis/` directory. The only `*analyze*` script is the pre-existing `output/scripts/npt_diagnostics/analyze_probe.py` (R3 probe analyzer, not Item H's deliverable). Item H either timed out, failed, or was lost to the notification-routing gap. **Sub 1.4 will need analysis skeletons; either re-spawn Item H equivalent or the Sub 1.4 SubAgents write their own.**

- **Item I (RMSF + RSALOR pre-compute, aac5894fd33506375): PARTIAL — RMSF DONE, RSALOR NOT DONE.** RMSF outputs are complete: `output/features/` has 47 per-protein `*_rmsf.csv` + 46 `*_rmsf.npz` + aggregate `batch1_rmsf.csv` (376 KB) + `batch1_rmsf_summary.csv` (3 KB), all mtimes 2026-05-03 23:48 → 2026-05-04 00:00. The compute script `output/scripts/features/compute_rmsf_batch1.py` is also in tree. **However: zero RSALOR files** — `find -iname '*rsalor*'` returns nothing. The RSALOR half of Item I's mandate did not execute. **Sub 1.3 ML pipeline will need RSALOR features; this is OUTSTANDING.**

- **Item D (walltime classification proposal, a7a141bdd631dc472): DID NOT LAND as a standalone doc, but its intent was SUPERSEDED.** No `*walltime*` markdown file exists in `shared/notes/` or `phases/phase-1/subphase-1.2/output/`. The intent (3-tier walltime classification for BioEmu batch 2) was effectively delivered by the 2026-05-05 BioEmu round-4 study (`output/optimization-round-4-bioemu.md`) and physically implemented by the BioEmu reorg subagent (`bioemu_batch2_short_6h_std.sbatch` + `bioemu_batch2_med_12h_scav.sbatch` + `bioemu_batch2_long_24h_scav.sbatch`). **No further action needed for Item D — superseded by 2026-05-05 work.**

**Net effect of the 4 predecessor subagents on Sub 1.2:**
- **A applied (NPZ cleanup runs on every BioEmu success).**
- **H lost** → **REPLACED 2026-05-06 ~11:43Z** by subagent `ab4abb5892326d6d3`. Delivered 7 files at `output/scripts/analysis/` (1236 LOC total): `analyze_mace_npt.py` (217 LOC), `analyze_so3lr_vacuum.py` (237), `S2_compute.py` (228), `density_T_P.py` (228, FULLY IMPLEMENTED — no stubs), `contacts.py` (222), `__init__.py`, `README.md` (104 lines / ~430 words). All Python files parse-clean. Sub 1.1 reference scripts found and mirrored: `subphase-1.1/output/scripts/{mace_analyze,so3lr_analyze,task007_analyze}.py`. NotImplementedError stubs clearly labeled `Sub 1.4 SubAgent: <specific guidance>` in analyze_mace_npt (compute_rmsf), analyze_so3lr_vacuum (4 load functions), S2_compute (load_nh_vectors + autocorrelation_s2), contacts (load_ca_positions + load_reference_ca). All argparse CLIs + JSON/NPZ writers + density_T_P + S2 orchestration + contacts orchestration + SO3LR Rg/COM/NaN-onset functions are fully implemented.
- **I half-applied** → **REPLACED PARTIAL 2026-05-06 ~11:42Z** by subagent `a347f370f0f7131d7`. RSA half FULLY DELIVERED: `compute_rsalor_batch1.py` (447 LOC, dual-mode RSA-only + FULL via `--msa-dir`); 47 per-protein `*_rsalor.csv` + 46 `*_rsalor.npz`; `batch1_rsalor.csv` (10,010 residue rows aggregate); `batch1_rsalor_summary.csv` (47 rows); RSA columns `rsa_absolute_a2` + `rsa_relative` populated (Shrake-Rupley SASA / Tien 2013 max ASA, biophysically sane means 0.27–0.44). Cohort 100% match with RMSF (47/47 verified by `diff`). LOR/RSALOR columns NaN-stubbed (algorithm clear per Tsishyn et al. 2025 / PyPI `rsalor` v1.1.9, but MSAs absent on filesystem AND `rsalor` package not installed in any env). **Sub 1.3 unblocking actions documented:** (i) fetch MSAs from ProteinGym `DMS_substitutions` bundle (https://github.com/OATML-Markslab/ProteinGym); (ii) `pip install rsalor` into env-bioemu; (iii) re-run `compute_rsalor_batch1.py --msa-dir <path>` (script handles per-protein MSA-missing gracefully).
- **D superseded (walltime classification implemented by 2026-05-05 reorg).**

**Hypothesis on the notification gap:** the predecessor's subagents were spawned by the predecessor's session ID; their completion notifications did not route to the successor session. The forensic confirmation above is what determines status — not notifications. The 2026-05-06 H+I-RSALOR replacement subagents were spawned by the current session and delivered their reports normally.

**This session's subagents (all completed by 2026-05-05 ~10:00Z):**
- closure-prep housekeeping (a086ba4c044f874f0) — DONE
- disk-usage survey (aeb76143eca7f5160) — DONE
- MACE round-4 study (a7f6cca0ebc555875) — DONE
- SO3LR round-4 study (abd7e3aa6df7b2d24) — DONE
- BioEmu round-4 study (a8c962cfee2163216) — DONE
- BioEmu reorg subagent (a2fc6144ab130ebc4) — DONE
- MACE+SO3LR R4 code edits subagent (a5c9748a2dbbd1650) — DONE

# CRITICAL FILES TO READ (in order)

Before doing anything, the successor must read:

1. **THIS FILE** — `phases/phase-1/subphase-1.2/handoff-successor-2026-05-05.md`
2. `phases/phase-1/subphase-1.2/CLAUDE.md` — your spec (carries over from predecessor)
3. `phases/phase-1/subphase-1.2/handoff-successor-2026-05-04.md` — predecessor handoff for 2026-05-02 → 2026-05-04 events context (still useful)
4. `phases/phase-1/subphase-1.2/completion-report.md` — pre-staged with §13 recommendations 1-10 INCLUDING the storage tier policy (#9) and compute-cost-vs-quality directive (#10) for PlannerAI elevation
5. `shared/notes/1.2-closure-master-plan.md` — strategy backbone (urgency=critical)
6. `shared/notes/1.2-mace-npt-fixed.md` — locked recipe + UBQ caveat (urgency=critical) + R4 row
7. `shared/notes/1.2-so3lr-rescue-results.md` — chemistry rescue + production protocol (urgency=critical) + R4 row
8. `shared/help-needed/head-1.2-mace-ubq-non-generalization.md` — UBQ escalation + options c/d state (urgency=critical)
9. `shared/notes/operational-practices.md` — scavenge policy + SU enforcement + OSF deposit checklist + diagnostic-first rule
10. `dashboards/master-status.md` + `dashboards/active-subphase.md` — current job state + decision-log + R4 + reorg
11. `phases/phase-1/subphase-1.2/output/osf-prereg-v3.md` — deposit-ready document (DO NOT EDIT)
12. `phases/phase-1/subphase-1.2/output/optimization-round-4-{mace,so3lr,bioemu}.md` — round-4 reports + applied edits log

# SUCCESSOR FIRST RESPONSE (mandatory state-confirmation, before any action)

After reading the critical files, respond to the user with this exact structure (5 items):

(a) **Job state:** one-line `squeue -u rag88` summary. Confirm 10-job baseline. Surface ANY job transitioned to RUNNING/terminal immediately.
(b) **Priority SU tracker:** one-line from `bash phases/phase-1/subphase-1.2/output/scripts/prio_su_enforce.sh --dry-run`. Expect 231.5 / 250 WITHIN_BUDGET.
(c) **Predecessor's 4 background subagents (Items A/H/I/D):** acknowledge notification gap; commit to filesystem-based discovery. Item I landed (output/features/, 94 files); Item D's intent executed via 2026-05-05 BioEmu work; A/H uncertain.
(d) **Open user decisions:** D-UBQ-1 IN-FLIGHT, 2026-05-09 contingency 4 days out, uncommitted working tree, others deferred.
(e) **Planned first 3 actions for next 24 hr.**

Do not act before delivering this response. The user will give next direction.

# FIRST ACTIONS (for the successor — after the (a)-(e) response is delivered)

1. Read this file end-to-end + the predecessor handoff (handoff-successor-2026-05-04.md) for full context.
2. Spot-check job state: `squeue -u rag88` — confirm 10 of our jobs PENDING (5 production + 2 UBQ probes + 3 BioEmu cohorts).
3. Spot-check tracker: `bash phases/phase-1/subphase-1.2/output/scripts/prio_su_enforce.sh --dry-run` — confirm WITHIN_BUDGET 231.5/250.
4. Spot-check filesystem for any predecessor-subagent outputs that might have landed: `find Execution/ -newer phases/phase-1/subphase-1.2/handoff-successor-2026-05-05.md -type f \! -path '*/.git/*' \! -path '*__pycache__*' -printf '%T+ %p\n' | sort -r | head -20`
5. Resume the routine 30-min ScheduleWakeup loop. Watch:
   - **10730244 q6sht3az** (BioEmu short cohort on Standard `gpu`) — first-dispatch confirms reorg worked
   - **10622876 q6kz3m8x** + **10622885 q6uadt05** (UBQ probes) — verdicts trigger D-UBQ-1 decision tree from `head-1.2-mace-ubq-non-generalization.md` §UBQ option (d)
   - **10567503-7** (5 production jobs) — long-running, no expected progress soon
6. Surface UBQ probe verdicts immediately:
   - Both PASS → submit corresponding 5 ns production on scavenge_gpu (criterion #1 has multiple paths)
   - NTL9 PASS / UBQ_alt FAIL → criterion #1 substitution; UBQ stays NVT or scope-revision
   - NTL9 FAIL / UBQ_alt PASS → keep UBQ via 1XQQ; surprise positive result
   - Both FAIL → escalate (b) NVT pivot or PlannerAI scope-revision per closure plan
7. **2026-05-09 contingency check:** if no scavenge dispatch by then, surface to user the option to move MACE production to Standard gpu_h200 (10× more SU; requires user approval per 3× partition rule).
8. **OSF deposit hard deadline 2026-05-15 — preferred 2026-05-13.** Surface to user a few days before to confirm deposit intent.
9. **Push uncommitted working tree** when user authorizes. Currently uncommitted (since 3a79078): R4 script edits, 3 new BioEmu sbatches, 3 round-4 reports, doc updates from batches 3+4, completion-report §13 #9 + #10 directives.

# WHAT'S LOCKED — DO NOT CHANGE

- **Round 3 MACE NPT recipe** (per OSF v3 §4: sentinel + HBonds + dt=1 fs + MCB freq=25). All edits must preserve.
- **Round 4 small wins** already APPLIED to scripts (lines 349/837/854/907 of mace_hybrid_npt_prod.py + lines 94-105 of so3lr_rescue.sbatch). Do not revert.
- **OSF v3** — pre-deposit-ready. Don't make further edits without user approval.
- **CLAUDE.md MUST-READ list** — current.
- **env-mace, env-so3lr, env-bioemu** — never modify.
- **Conda path** — `/apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh` (verbatim).
- **scavenge_gpu pivot** — don't move off without user approval (3× rule).
- **BioEmu reorg state** — 3 new arrays (10730244/5/6) submitted; old arrays scancelled. Don't undo.
- **prio_su_budget.json: 250 SU cap** — don't raise without user approval.

# WHAT'S OPEN — ROOM TO ACT WITHOUT FURTHER USER CLEARANCE

- Periodic squeue + sshare check-ins (every 30-60 min)
- Updates to dashboards as facts change (master-status, active-subphase, gate-tracker, compute-budget)
- Status report appendices when new evidence lands
- Cross-agent notes when findings affect other tracks
- prio_su_enforce.sh re-runs (dry-run) if budget concerns emerge
- Submit production runs only IF probes pass (UBQ option-c/d) — DO NOT submit production for UBQ until probe verdicts in
- Standard Tier `gpu` Sub 1.2 closure work (no priority SU cost) — already in plan via BioEmu short cohort
- Doc audits (batch 5+) when execution state changes substantively
- Filesystem-based discovery of predecessor-subagent outputs (Items A/H/I/D) since notification routing is broken

# WHAT REQUIRES USER APPROVAL

- Any partition move ≥3× more expensive (per task #24 + completion-report §13 #10)
- Priority SU spend that would push past 250 cap (would require raising prio_su_budget.json)
- Any OSF v3 edit beyond what's already applied
- Any CLAUDE.md edit
- Cancellation of jobs that have been RUNNING + accumulating data (free-tier cancellation of PENDING is fine; we just did this for BioEmu reorg under approval)
- Any scope-revision help-needed escalation
- Any GitHub push (`git commit` + `git push`) — push only when user explicitly says "push"

# OPERATIONAL PRACTICES — KEEP THESE GOING

Per `shared/notes/operational-practices.md` (carry forward from predecessor):

1. **Cryptic 8-char job names**, q6 prefix preferred (q6XXXXXX). Never descriptive names. **Existing names to avoid clashes with:** q6wmsv5n, q6gpsv9k, q6kz3m8x, q6uadt05, q6sht3az, q6med7kp, q6lng5wm, q6u4n8mx (cancelled UBQ retry), q6byygle (Test A classical, complete), q6wjsyhu, q6q6ijfi (cancelled tests), p3w7m9kc (test_P), 4fm5g4wu / 4ldqsdyt (Sub 1.1 logs), k5q8pt3n / h1v5qpn9 (older).

2. **scavenge_gpu first** — 1/10 Standard billing. Eligible workloads have checkpoint/restart support (all our scripts do).

3. **Diagnostic-first rule** — small probe (priority_gpu 50 ps OR scavenge_gpu) before any expensive submission.

4. **Doc-audit cadence** — when execution state changes substantively, update dashboards + cross-agent notes within the same session, not days later. (Now 4 batches deep this subphase.)

5. **Trust subagent reports** — don't re-do their work. Verify via spot-check (squeue, scontrol, `ls`, `wc -l`) only. **Honest deviations are valuable** — Round-4 MACE subagent surfaced that win #1 had no current consumer to thread state to; implemented as defensive API instead.

6. **ScheduleWakeup cadence:** 1800s (30 min) routine while jobs PENDING. Pass the same /loop prompt back so the next firing repeats the task.

7. **Storage tier policy (per completion-report §13 #9):** scratch for large/non-permanent; home for code/docs/manifests/<10 MB ref data; project for permanent shared resources only.

8. **Compute-cost vs quality (per completion-report §13 #10):** every SLURM job exercises BOTH levers — cheapest viable partition AND most efficient code/parameters. Quality guardrails LOCKED (trajectory length, force-field accuracy, statistical thresholds, OSF v3 pre-registration, benchmark roster).

9. **Filesystem discovery for predecessor's subagent outputs:** Items A/H/I/D notifications won't route to your session. Use `find ... -newer <handoff-anchor> -type f` to discover what's landed.

# WORKING TREE STATE

As of 2026-05-05 22:00Z, working tree has uncommitted changes (since 3a79078 push 2026-05-04):

**Modified:**
- `Execution/dashboards/active-subphase.md` (R4 + reorg)
- `Execution/dashboards/master-status.md` (R4 + reorg)
- `Execution/phases/phase-1/subphase-1.2/completion-report.md` (§13 #9 + #10 directives)
- `Execution/phases/phase-1/subphase-1.2/output/scripts/mace_hybrid_npt_prod.py` (R4 edits)
- `Execution/phases/phase-1/subphase-1.2/output/scripts/so3lr_rescue.sbatch` (R4 edits)
- `Execution/shared/notes/1.2-bioemu-batch2-passrates.md` (reorg)
- `Execution/shared/notes/1.2-mace-npt-stability.md` (R4 row)
- `Execution/shared/notes/1.2-so3lr-rescue-results.md` (R4 row)
- `Execution/phases/phase-1/subphase-1.2/status/task-004-status.md` (reorg)

**New (untracked, but should commit on next push):**
- `Execution/phases/phase-1/subphase-1.2/output/optimization-round-4-mace.md`
- `Execution/phases/phase-1/subphase-1.2/output/optimization-round-4-so3lr.md`
- `Execution/phases/phase-1/subphase-1.2/output/optimization-round-4-bioemu.md`
- `Execution/phases/phase-1/subphase-1.2/output/scripts/bioemu_batch2_short_6h_std.sbatch`
- `Execution/phases/phase-1/subphase-1.2/output/scripts/bioemu_batch2_med_12h_scav.sbatch`
- `Execution/phases/phase-1/subphase-1.2/output/scripts/bioemu_batch2_long_24h_scav.sbatch`
- `Execution/phases/phase-1/subphase-1.2/handoff-successor-2026-05-05.md` (this file)

**Skip on push (correctly excluded by previous push policy):** SLURM .out/.err logs, output/features/ (computed RMSF), output/slurm_logs/, output/scripts/npt_diagnostics/logs/, prio_su_registry.json, prio_su_status.json, mace_hybrid_*.log/json from Sub 1.1, Execution/phases/shared/ (empty misplaced dir).

# KNOWN GOTCHAS

- `prio_su_enforce.sh --dry-run` is safe; without `--dry-run` it scancels jobs. Use `--dry-run` for routine checks.
- `task-009-status.md` has SUPERSEDED banner; future readers should follow it to `1.2-mace-npt-fixed.md`.
- `submit_mace_npt_prod.sh` `--check-fit` mode for projected SU pre-check on new submissions is NOT yet wired (task #17 follow-up). Current pre-check uses `prio_su_tracker.sh`.
- Existing handoff-notes.md (2026-05-02 overnight) is OUTDATED — DO NOT follow that doc; superseded by handoff-successor-2026-05-04.md, which is now itself superseded by THIS doc (handoff-successor-2026-05-05.md).
- Predecessor session's 4 background subagents (Items A/H/I/D) won't deliver completion notifications to your (successor) session. Item I clearly produced outputs in `output/features/` (94 files) and Item D's intent was executed by BioEmu round-4 work. A and H status remains uncertain — discover via filesystem inspection.
- `priority_gpu` partition does NOT have `rtx_5000_ada` GPUs in its node list; only h200/b200/rtx_pro_6000_blackwell. Don't request `--gres=gpu:rtx_5000_ada:1` on priority_gpu.
- BioEmu locked to RTX 5000 Ada (per Sub 1.1 lesson + user memory) — ALL future BioEmu work must use `--gres=gpu:rtx_5000_ada:1` and never H200/B200/rtx_pro_6000.
- `output/scripts/features/compute_rmsf_batch1.py` is a script (one Python file), not feature data — don't confuse with `output/features/` which is computed RMSF arrays.
- The `getquota` command shows USER total (rag88 across all projects), not CompBio-only. Use the disk-usage survey approach for project-specific tallies.
- JAX compilation cache `~/.cache/jax_compilation/` was COLD as of 2026-05-05 — first SO3LR submission post-R4 pays full ~30-60 s JIT compile.

# APPENDIX: SESSION TIMELINE (2026-05-04 → 2026-05-05)

| Time (UTC approx) | Event |
|---|---|
| 2026-05-04 ~10:30Z | Successor session begins; predecessor's handoff-successor-2026-05-04.md read |
| 2026-05-04 ~11:00Z | Closure-prep housekeeping subagent launched (a086ba4c044f874f0) |
| 2026-05-04 ~11:50Z | Closure-prep subagent landed: doc audit batch 2 + completion-report.md skeleton + 1.2-osf-deposited.md stub |
| 2026-05-04 ~13:00Z | Disk-usage survey subagent launched (aeb76143eca7f5160) |
| 2026-05-04 ~13:10Z | Disk-usage survey landed; key insight: pi_mg269 project tier at 95% (binding constraint) |
| 2026-05-04 ~13:20Z | User directive: storage tier policy → encoded as completion-report §13 #9 |
| 2026-05-04 ~14:00Z | User: "push docs to github" → commit 3a79078, 194 files, 38,506 insertions; pushed to origin/main |
| 2026-05-04 ~14:30Z → 2026-05-05 ~09:00Z | Routine 30-min wakeup loop overnight; date rolled to 2026-05-05; jobs all PENDING |
| 2026-05-05 ~09:00Z | User: faster partitions? + launch optimization subagents |
| 2026-05-05 ~09:10Z | Partition survey + 3 round-4 optimization subagents launched in parallel (mace, so3lr, bioemu) + completion-report §13 #10 directive added |
| 2026-05-05 ~09:20Z | MACE round-4 subagent landed: near-saturated; partition is the live knob |
| 2026-05-05 ~09:25Z | SO3LR round-4 subagent landed: saturated; XLA flags optional below noise floor |
| 2026-05-05 ~09:30Z | BioEmu round-4 subagent landed: BIG win — walltime split + Standard gpu for L<200 saves 7-9 days |
| 2026-05-05 ~09:50Z | User: approve 1, 2, 3; stay-the-course for 4 |
| 2026-05-05 ~09:55Z | BioEmu reorg subagent + MACE+SO3LR R4 code-edit subagent launched in parallel |
| 2026-05-05 ~10:00Z | BioEmu reorg landed: 3 new arrays (10730244 + 10730245 + 10730246) submitted, 9449458 + 9449459 scancelled |
| 2026-05-05 ~10:00Z | MACE+SO3LR R4 code-edit subagent landed: 4 MACE markers + 3 SO3LR env vars |
| 2026-05-05 ~10:00Z → ~22:00Z | Routine 30-min wakeup loop; 10 jobs all PENDING the entire window; no transitions; user inactivity |
| 2026-05-05 22:00Z | Successor handoff doc written (this file) |

---

End of head-1.2 successor handoff (2026-05-05). Hand to successor with the prompt in the user-facing message that accompanies this doc.
