---
title: Sub 1.2 head-1.2 successor handoff (2026-05-06 evening)
author: head-1.2 (this session, 2026-05-05 22:30Z → 2026-05-06 ~18:00Z)
date: 2026-05-06T18:00:00Z
supersedes: handoff-successor-2026-05-05.md (still mandatory read for unchanged context — see "READ ORDER" below)
purpose: Delta-only handoff: everything that changed since the 2026-05-05 doc. The 2026-05-05 doc remains the load-bearing structural reference for locked recipes, OSF state, infrastructure, operational practices, gotchas, etc.
---

# READ ORDER (mandatory)

1. **THIS FILE** first — covers all 2026-05-05 22:30Z → 2026-05-06 18:00Z changes.
2. **`handoff-successor-2026-05-05.md`** for everything still valid (locked recipes, OSF v3 state, SU enforcement infra, operational practices, doc audit history, known gotchas, predecessor subagent forensic status, session timeline through 2026-05-05).

If a fact appears in both docs, this 2026-05-06 doc wins (it's the more recent observation).

# TL;DR (45 seconds)

Since 2026-05-05 22:30Z handoff: 5 background subagents launched + landed cleanly (Item H + Item I-RSALOR replacements at 11:42-11:43Z; then 3 unblocker subagents at ~12:00Z for Sub 1.4 planning hooks + RMSF stub fill + RSALOR full unblock). 1 user-approved walltime shortening applied (SO3LR GB3 + NTL9 rescues 24h→18h, ~80% safety buffer over expected ~10h actual runtime). Still 10 SLURM jobs PENDING; SLURM-estimated first dispatch 2026-05-09 (= +3 days = exactly the contingency-trigger boundary). Working tree accumulating uncommitted changes; awaiting user "push" command.

**No transitions to RUNNING in 36+ hours of session window. No D-UBQ-1 verdict yet.**

# WHAT CHANGED SINCE 2026-05-05 22:30Z

## A. Predecessor subagent replacement deliverables (2026-05-06 ~11:42-11:43Z)

**Item H replacement (subagent `ab4abb5892326d6d3`) — DELIVERED:**
- New directory: `phases/phase-1/subphase-1.2/output/scripts/analysis/` with 7 files (1,236 LOC total):
  - `__init__.py` (empty marker)
  - `analyze_mace_npt.py` (217 LOC) — top-level MACE NPT analyzer; orchestrator pattern; writes `<id>_master_summary.json`
  - `analyze_so3lr_vacuum.py` (237 LOC) — SO3LR vacuum NVT analyzer; Rg time series + runaway flag + COM drift + NaN onset (encoded 500 ps gate logic from `1.2-so3lr-rescue-results.md`)
  - `S2_compute.py` (228 LOC) — Lipari-Szabo S2 with block-bootstrap CIs (4 × 1.25 ns blocks, τ=1 ns plateau, 1000 resamples)
  - `density_T_P.py` (228 LOC) — **FULLY IMPLEMENTED, no stubs**; parses StateDataReporter CSV; verdict thresholds T=300±15 K + density 0.85-1.10 g/cm³ from `1.2-mace-npt-fixed.md`
  - `contacts.py` (222 LOC) — Cα-Cα contact map evolution + Q-score per frame
  - `README.md` (~430 words / 104 lines) — module map + I/O conventions + dep notes (env-analysis preferred; MDAnalysis ≈ compute_rmsf_batch1.py)
- All Python files compile clean (verified `python3 -m py_compile`).
- Sub 1.1 reference scripts found and mirrored: `subphase-1.1/output/scripts/{mace_analyze,so3lr_analyze,task007_analyze}.py`.
- 9 NotImplementedError stubs labeled `Sub 1.4 SubAgent: <specific guidance>` (later reduced to 8 — see RMSF stub fill below).

**Item I-RSALOR replacement PARTIAL (subagent `a347f370f0f7131d7`) — RSA half DELIVERED:**
- `compute_rsalor_batch1.py` (447 LOC, dual-mode: RSA-only + FULL via `--msa-dir`).
- 47 per-protein `*_rsalor.csv` + 46 `*_rsalor.npz` (YAP1 properly skipped, matching RMSF cohort behavior).
- `batch1_rsalor.csv` (10,010 residue rows aggregate) + `batch1_rsalor_summary.csv` (47 rows).
- Schema: `uniprot_id, residue_idx_0based, resid, resname, aa1, rsa_absolute_a2, rsa_relative, lor_mean_to_other, lor_max_to_other, rsalor_mean, rsalor_max, n_msa_sequences`.
- RSA columns populated (Shrake-Rupley SASA / Tien 2013 max ASA; biophysically sane means 0.27-0.44).
- LOR columns NaN-stubbed at this point — algorithm clear (Tsishyn et al. 2025 / PyPI rsalor 1.1.9) but MSAs absent + rsalor not installed.

## B. Three unblocker subagents launched + landed (2026-05-06 ~12:00-13:00Z)

### B.1 Sub 1.4 / Phase 2 planning hooks summary (subagent `ac4d9be00f73e692f`)
- New file: `shared/notes/1.4-planning-hooks-from-1.2.md` (10 KB, 1,294 words, 8 sections, frontmatter `urgency: important / status: ready for PlannerAI consumption`).
- Sections: §1 per-protein recipe map / §2 R3+R4 recipe locks / §3 cost-quality directive cross-ref / §4 storage policy cross-ref / §5 R6/R7/R8 elevation candidates / §6 Sub 1.3 unblockers / §7 open user decisions / §8 cross-references index.
- PlannerAI's next planning cycle reads this directly.

### B.2 RMSF stub fill (subagent `a8ae052a598ef82a6`)
- 2 stubs filled in `output/scripts/analysis/`:
  - `analyze_mace_npt.py:89` — delegates to `_rmsf_helpers.mace_compute_rmsf` (MDAnalysis wrapper mirroring `compute_rmsf_batch1.py:99-138`)
  - `analyze_so3lr_vacuum.py:125` — delegates to `_rmsf_helpers.so3lr_compute_ca_rmsf` (pure-numpy Kabsch core)
- New shared helper: `_rmsf_helpers.py` (265 LOC) — 3 entry points (`kabsch_aligned_ca_rmsf`, `mace_compute_rmsf`, `so3lr_compute_ca_rmsf`).
- New tests: `test_rmsf.py` (253 LOC, 6 pytest-compatible test functions). **Verified 6/6 PASS** via plain-script runner with env-analysis Python.
- Tests: identity / oscillation / smoke / translation-invariance / SO3LR wrapper dict / too-short input handling.
- **8 stubs remain** in the analysis package — explicitly DEFERRED to Sub 1.4 SubAgent + domain review:
  - `S2_compute.py`: 2 stubs (`_load_nh_vectors`, `_autocorrelation_s2`) — load-bearing for Alpha-M paper, Sub 1.4 SubAgent's responsibility.
  - `contacts.py`: 2 stubs (`_load_ca_positions`, `_load_reference_ca`) — defer.
  - `analyze_so3lr_vacuum.py`: 4 stubs (HDF5 + log + Cα RMSF reference + topology metadata loaders) — depend on actual SO3LR file format inspection.

### B.3 RSALOR full unblock (subagent `a3500d8b6b0dab42d`) — Sub 1.3 GAMMA UNBLOCKED
- **All 10,010 / 10,010 residue rows in `batch1_rsalor.csv` now have non-NaN LOR.** 46 of 47 batch-1 proteins fully populated (YAP1 correctly skipped).
- ProteinGym v1.3 MSA bundle on scratch (`/nfs/roberts/scratch/pi_mg269/rag88/proteingym/`, 6.3 GB total): 194 `.a2m` files in `DMS_msa_files/` + 47 `by_uniprot/<UNI>.fasta` symlinks for the batch-1 cohort.
- New venv `~/.conda/envs-venv/env-bioemu-rsalor/` created via `python -m venv --system-site-packages` (conda clone OOM-killed twice on login node — clean documented fallback). Inherits env-bioemu's torch/biopython; rsalor 1.1.9 installed.
  - Activation pattern: `PYTHONNOUSERSITE=0 ~/.conda/envs-venv/env-bioemu-rsalor/bin/python <script>`. **NOT** `conda activate`.
- New sibling script: `output/scripts/features/compute_rsalor_full_batch1.py` (16,809 bytes / ~330 LOC) — original `compute_rsalor_batch1.py` is BYTE-IDENTICAL (per HARD constraint). The original's expected rsalor API was wrong for v1.1.9 (which uses `mutation_fasta` strings + capitalized `LOR`/`RSA*LOR` keys + `m.depth`).
- Per-protein invocation + aggregation playbook documented in env-split note (single-process passes were OOM-killed on login around protein 28 due to heavy MSAs like PHOT_CHLRE 1.6M sequences / ENVZ_ECOLI 1.9M sequences).
- Env-split documented: `shared/notes/1.2-env-rsalor-clone.md` (7,754 bytes).
- Sample LOR values biophysically reasonable: lor_mean ~3.7-10.3, rsalor_mean ~2.2-8.5; MSA depth 44-42,145 across proteins.

## C. Walltime shortening applied (2026-05-06 ~16:30Z)

User approved lever #2 (shorten walltimes for safe candidates) with explicit "err on the side of safe" directive.

Per-job runtime analysis determined ONLY 2 of 10 jobs were safe shorten candidates:
- **10567505 (SO3LR GB3 rescue)**: 24:00:00 → **18:00:00** via `scontrol update JobId=10567505 TimeLimit=18:00:00`. Expected runtime ~10h (Sub 1.1 GB3 11.9h × R4 0.87 throughput gain) → 18h gives ~80% safety buffer.
- **10567506 (SO3LR NTL9 rescue)**: 24:00:00 → **18:00:00** (same logic, expected ~10h).
- All 8 other jobs: NO CHANGE — runtime analysis showed they need full window:
  - MACE WW (10567503) ~42h → exceeds 24h cap; needs requeue cycles regardless.
  - MACE GB3 (10567504) ~55h → same.
  - SO3LR WW float64+dt=0.25fs (10567507) ~24h → right at boundary; no margin.
  - UBQ probes (10622876, 10622885) already at 5:55 → keep startup margin.
  - BioEmu cohorts already classified in 2026-05-05 reorg.

Verification: `squeue -j 10567505,10567506` confirms TimeLimit=18:00:00. REASON briefly transitioned to `(None)` post-update (SLURM re-evaluation), now back to `(Priority)` — normal.

## D. SLURM dispatch ETA — concrete estimates from `squeue --start` (as of 2026-05-06 ~14:00Z)

| Job | Tag | Workload | Partition | Est. start | Days |
|---|---|---|---|---|---|
| 10567505 | g7p4tv8m | SO3LR GB3 5ns | scavenge_gpu | 2026-05-09 11:55 | +3 |
| 10567506 | n5h6kx9q | SO3LR NTL9 5ns | scavenge_gpu | 2026-05-09 12:05 | +3 |
| 10567507 | w8q4r3xz | SO3LR WW float64 5ns | scavenge_gpu | 2026-05-09 12:10 | +3 |
| 10730245 | q6med7kp | BioEmu MED (18 prot) | scavenge_gpu | 2026-05-09 17:35 | +3 |
| 10567503 | q6wmsv5n | MACE WW 5ns NPT | scavenge_gpu | 2026-05-09 21:55 | +3 |
| 10730244 | q6sht3az | BioEmu SHORT (53 prot) | gpu (Standard) | 2026-05-10 13:20 | +4 |
| 10567504 | q6gpsv9k | MACE GB3 5ns NPT | scavenge_gpu | 2026-05-10 15:15 | +4 |
| 10622876 | q6kz3m8x | UBQ NTL9 50ps probe | scavenge_gpu | 2026-05-10 16:15 | +4 |
| 10622885 | q6uadt05 | UBQ_alt 1XQQ 50ps probe | scavenge_gpu | 2026-05-10 16:20 | +4 |
| 10730246 | q6lng5wm | BioEmu LONG (11 prot) | scavenge_gpu | 2026-05-12 17:35 | +6 |

**Note:** post-walltime-update, SLURM `--start` projection drifted ~2 days later for the entire queue — this was a queue-wide re-projection (not specific to our walltime change). Cluster got busier in the intervening hours. SLURM `--start` is pessimistic re backfill; real dispatch may beat these times.

**Queue ranks:** scavenge_gpu — our top-priority production jobs are ranks 25-33 of 147 PENDING (top 1/5, behind 24 RUNNING). Standard `gpu` — 51 of 146 PENDING ahead of our 10730244 (top 1/3).

**Fair-share state:** `pi_mg269/rag88` LevelFS = 0.262 (down from 0.273 yesterday — slow recovery). `prio_mg269/rag88` LevelFS = 18.1 (credit-RICH but capped at 250 SU budget, 231.5 used, 18.5 buffer).

## E. Acceleration levers surfaced + USER-APPROVED status (2026-05-06)

| # | Lever | Cost | User decision |
|---|---|---|---|
| 1 | UBQ probes → `gpu_devel` (PriorityTier=4, 5:55 fits walltime cap) | ~600 Standard SU | **NOT YET APPROVED** |
| 2 | Shorten walltimes via `scontrol` | 0 SU | **APPROVED + APPLIED** for SO3LR GB3+NTL9 (24h→18h) |
| 3 | SO3LR rescues → Standard `gpu` | ~1,080 Standard SU | NOT YET APPROVED |
| 4 | MACE prods → Standard `gpu_h200` | ~28,800 Standard SU | NOT YET APPROVED |
| 5 | Raise prio_su_budget cap + UBQ probes → `priority_gpu_h200` (PriorityTier=8) | ~600 priority SU = ~$2.40 | NOT YET APPROVED |
| 6 | Raise cap further + MACE → `priority_gpu_h200` | ~28,800 priority SU = ~$115 | NOT YET APPROVED |
| 7 | Wait — fair-share recovers | 0 | DEFAULT (currently in effect) |
| 8 | Coalesce/cancel + resubmit | 0 | NOT recommended (could rank lower) |

# CURRENT STATE OF PLAY (as of 2026-05-06 18:00Z)

## SLURM job state
All 10 jobs PENDING, no transitions to RUNNING in entire session:

| JobID | Tag | Walltime (current) | Comment |
|---|---|---|---|
| 10567503 | q6wmsv5n | 23:59 | MACE WW NPT — no walltime change |
| 10567504 | q6gpsv9k | 23:59 | MACE GB3 NPT — no walltime change |
| 10567505 | g7p4tv8m | **18:00** | SO3LR GB3 — **shortened 2026-05-06** |
| 10567506 | n5h6kx9q | **18:00** | SO3LR NTL9 — **shortened 2026-05-06** |
| 10567507 | w8q4r3xz | 24:00 | SO3LR WW float64 — no change (at boundary) |
| 10622876 | q6kz3m8x | 5:55 | UBQ NTL9 probe |
| 10622885 | q6uadt05 | 5:55 | UBQ_alt 1XQQ probe |
| 10730244 | q6sht3az | 6:00 | BioEmu SHORT (Standard `gpu`, 53 prot) |
| 10730245 | q6med7kp | 12:00 | BioEmu MED (scavenge, 18 prot) |
| 10730246 | q6lng5wm | 23:59 | BioEmu LONG (scavenge, 11 prot) |

Priority SU tracker: 231.5 / 250 SU, WITHIN_BUDGET (no priority jobs in flight). 18.5 SU buffer.

## Subagent state
- **All 5 background subagents launched this session COMPLETE** (Item H + I-RSALOR replacements 2026-05-06 ~11:42-11:43Z; then planning-hooks + RMSF-stub-fill + RSALOR-full ~12:00-13:00Z).
- **Predecessor's 4 background subagents:** A=COMPLETED (NPZ cleanup logic in `bioemu_batch2*.sbatch`, inherited by 2026-05-05 reorg children), H=REPLACED (2026-05-06 above), I=PARTIAL→FULL (RSA from 2026-05-06 first replacement; LOR from 2026-05-06 RSALOR-full). D=SUPERSEDED by 2026-05-05 BioEmu reorg.
- **No subagents currently in flight.**

## Working tree (uncommitted since 2026-05-04 commit `3a79078`)

Modified (since the 2026-05-05 doc):
- `phases/phase-1/subphase-1.2/output/scripts/analyze_mace_npt.py` (RMSF delegation)
- `phases/phase-1/subphase-1.2/output/scripts/analyze_so3lr_vacuum.py` (RMSF delegation)
- (Plus all the modifications from before the 2026-05-05 doc — see that doc's working-tree section for the older list.)

New (untracked, since 2026-05-05 doc):
- `phases/phase-1/subphase-1.2/output/scripts/analysis/` (entire directory, 7 files)
- `phases/phase-1/subphase-1.2/output/scripts/analysis/_rmsf_helpers.py`
- `phases/phase-1/subphase-1.2/output/scripts/analysis/test_rmsf.py`
- `phases/phase-1/subphase-1.2/output/scripts/features/compute_rsalor_batch1.py` (the RSA-only original from 2026-05-06)
- `phases/phase-1/subphase-1.2/output/scripts/features/compute_rsalor_full_batch1.py` (the rsalor-1.1.9-API sibling)
- `phases/phase-1/subphase-1.2/output/features/*_rsalor.{csv,npz}` (47 + 46 files)
- `phases/phase-1/subphase-1.2/output/features/batch1_rsalor.csv` + `batch1_rsalor_summary.csv`
- `shared/notes/1.4-planning-hooks-from-1.2.md`
- `shared/notes/1.2-env-rsalor-clone.md`
- `phases/phase-1/subphase-1.2/handoff-successor-2026-05-06.md` (this file)

NOT in working tree (intentionally on scratch — per storage tier policy):
- `/nfs/roberts/scratch/pi_mg269/rag88/proteingym/` (6.3 GB MSA bundle)
- `~/.conda/envs-venv/env-bioemu-rsalor/` (the venv)

## Open user decisions

| ID | Status |
|----|--------|
| **D-UBQ-1** (UBQ NPT path) | IN-FLIGHT. Probes 10622876 + 10622885 estimated dispatch 2026-05-10 ~16:00Z. Verdicts trigger options c/d decision tree from `head-1.2-mace-ubq-non-generalization.md`. |
| **2026-05-09 contingency trigger** | 3 days out. Aligns exactly with SLURM-estimated first dispatch. If first dispatch slips past 2026-05-09, surface contingency (move MACE to Standard `gpu_h200`). |
| **Working-tree push** | NOT yet pushed. Awaiting user "push" command. |
| **OSF deposit** | HARD 2026-05-15 (9 days). Target 2026-05-13. Will surface ~2026-05-11 for confirmation. |
| **Acceleration levers #1, #3, #4, #5, #6** | NOT approved. User has applied #2 only. |
| **Sub 1.4 NotImplementedError stubs (8 remaining)** | DEFERRED to Sub 1.4 SubAgent — DO NOT fill speculatively (load-bearing for paper). |
| **R6/R7/R8 risk register elevation** | LOW URGENCY. PlannerAI handles via `1.4-planning-hooks-from-1.2.md` §5 when invoked. |

# SUCCESSOR FIRST RESPONSE (mandatory, before any action)

Respond with this exact 5-item structure:

(a) **Job state:** one-line `squeue -u rag88` summary. Confirm 10-job baseline + walltime shortening on 10567505 + 10567506 (now 18:00:00). Surface ANY transition to RUNNING/terminal IMMEDIATELY.
(b) **Priority SU tracker:** one-line `bash phases/phase-1/subphase-1.2/output/scripts/prio_su_enforce.sh --dry-run`. Expect 231.5 / 250 WITHIN_BUDGET.
(c) **Subagent state acknowledgement:** all 5 this-session subagents complete; all 4 predecessor subagents resolved (A done, H replaced, I done, D superseded). No subagents in flight.
(d) **Open user decisions list:** D-UBQ-1 in-flight (probes ETA 2026-05-10 evening), 2026-05-09 contingency trigger 3 days out, uncommitted working tree, levers #1/#3/#4/#5/#6 not yet approved (only #2 applied), OSF deposit ~2026-05-13/15.
(e) **Planned first 3 actions for next 24 hr.**

# STANDING RULES (delta from 2026-05-05 doc — read 2026-05-05's "WHAT REQUIRES USER APPROVAL" section for full)

Unchanged: 3× partition rule; OSF v3 frozen; CLAUDE.md frozen; no GitHub push without "push"; no priority SU cap raise without approval; no scancel of RUNNING jobs.

New as of 2026-05-06:
- **Walltime modifications via `scontrol update`:** require user approval (treat as a job-state change). Two have been applied (10567505 + 10567506).
- **Sub 1.4 NotImplementedError stubs:** DO NOT fill speculatively. RMSF was filled because it's mirror-from-existing (`compute_rmsf_batch1.py`) and synthetic-tested. The remaining 8 stubs (S2 computation, contacts loaders, SO3LR HDF5/log/topology) are LOAD-BEARING for the Alpha-M paper or depend on actual file format inspection — Sub 1.4 SubAgent + domain review territory.
- **env-bioemu-rsalor venv:** activation via `PYTHONNOUSERSITE=0 ~/.conda/envs-venv/env-bioemu-rsalor/bin/python` — NOT `conda activate`. Documented in `shared/notes/1.2-env-rsalor-clone.md`.

# CRITICAL FILES TO READ (delta — 2026-05-05 doc's "CRITICAL FILES TO READ" still applies for the unchanged 12 paths)

New since 2026-05-05:
1. `phases/phase-1/subphase-1.2/output/optimization-round-4-{mace,so3lr,bioemu}.md` (already in 2026-05-05 doc but now `status: APPLIED 2026-05-05`)
2. `phases/phase-1/subphase-1.2/output/scripts/analysis/README.md` — module map for the new trajectory analysis package
3. `phases/phase-1/subphase-1.2/output/scripts/analysis/test_rmsf.py` — passing test pattern for Sub 1.4 SubAgent to follow when filling remaining stubs
4. `shared/notes/1.4-planning-hooks-from-1.2.md` — PlannerAI consumption-ready (8 sections)
5. `shared/notes/1.2-env-rsalor-clone.md` — env-bioemu-rsalor venv documentation + per-protein OOM workaround playbook

# SESSION TIMELINE (delta — appends to 2026-05-05 doc's timeline)

| Time (UTC) | Event |
|---|---|
| 2026-05-05 22:30Z | 2026-05-05 handoff doc written; predecessor subagent forensic confirmation written |
| 2026-05-05 22:45Z | 2 replacement subagents launched (Item H + Item I-RSALOR) |
| 2026-05-06 00:00Z–11:00Z | Routine wakeup loop overnight; jobs all PENDING |
| 2026-05-06 11:42Z | Item I-RSALOR replacement landed (RSA half delivered, LOR half stubbed) |
| 2026-05-06 11:43Z | Item H replacement landed (6 analysis skeleton files + density_T_P fully implemented) |
| 2026-05-06 12:00Z | 3 unblocker subagents launched (planning hooks + RMSF stub fill + RSALOR full) |
| 2026-05-06 11:55Z–12:08Z | Sub 1.4 planning hooks landed (`1.4-planning-hooks-from-1.2.md`) |
| 2026-05-06 12:00Z | RMSF stub fill landed (`_rmsf_helpers.py` + `test_rmsf.py` + 6/6 PASS) |
| 2026-05-06 12:46Z | RSALOR full unblock landed (10,010 / 10,010 LOR populated; venv + sibling script + env-split doc) |
| 2026-05-06 ~14:00Z | User asked queue-position question → surfaced concrete SLURM `--start` ETAs |
| 2026-05-06 ~16:00Z | User asked acceleration question → surfaced 8-lever ranked table |
| 2026-05-06 ~16:30Z | User approved lever #2 → walltime shortening applied to SO3LR GB3 + NTL9 (24h→18h) |
| 2026-05-06 ~16:35Z | Verified post-update SLURM `--start` projections (drifted later cluster-wide; not our action) |
| 2026-05-06 17:00Z–18:00Z | Routine wakeup loop; jobs still PENDING |
| 2026-05-06 18:00Z | This handoff doc written |

---

End of head-1.2 successor handoff (2026-05-06).
