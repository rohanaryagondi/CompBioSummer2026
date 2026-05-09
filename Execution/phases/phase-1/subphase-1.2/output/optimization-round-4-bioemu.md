---
type: optimization-recommendations
subphase: "1.2"
target: bioemu-batch2-generation
round: 4
date: 2026-05-05
author: optimization-subagent (round-4-bioemu)
status: PROPOSED — head-1.2 reviews + decides
---

# BioEmu Batch 2 Round 4 Optimization Analysis

## 1. Executive summary

R1-R3 shipped: length-aware `batch_size_100`, keepalive, MSA on-the-fly,
disorder pre-screen, oversampling formula, RTX 5000 Ada lock, NPZ cleanup,
12h/24h split. Baseline (11 status JSONs): AICDA L=198/ns=2827 → 67.6 min
⇒ `runtime ≈ 1.21e-4 × L × ns` min. Of 82 PENDING: **76/92 ≤4 h, 17/92 in
4-8 h, 0 in 8-24 h.** Arrays 9449458/9449459 `scontrol`-moved to
`scavenge_gpu` 2026-04-25; PENDING Priority 10+ days.

**Top-3 untapped wins:**

1. **3-tier walltime (6/12/24 h) + L<200 → Standard `gpu`.** Saves 7-9 d queue; +205 SU.
2. **XTC-only writes** (skip NPZ; lose resume). +3-7 % wall, –70 % I/O.
3. **`--mem=24G` for 52 short L<200 proteins.** FS boost; ~0 SU change.

## 2. Opportunities table

| # | Change | Per-protein Δ | Risk | Quality |
|---|---|---|:--:|---|
| 1 | Walltime 6/12/24 h classification | ≈0 SU; 1-3 d wall | V.low | Yes |
| 2 | `--write-mode xtc-only` | +3-7 % wall, –70 % I/O | Med | Yes |
| 3 | Persistent worker (cold-start amortise) | –20-25 min × N | Med-high | Yes |
| 4 | Drop `kineticEnergy`/`temperature` reporters | <0.5 % | V.low | Yes |
| 5 | `batch_size_100 = max(10, ceil(3·(L/100)²))` | Done R1 | n/a | Yes |
| 6 | `--cpus-per-task` 2→4 | +1-2 % | Low | Yes |
| 7 | `--mem=24G` for L<200 | +1-2 % FS | Low | Yes |
| 8 | RTX 5000 Ada constraint | Locked | n/a | Locked |
| 9 | `gpu_devel` (4h cap) | Reject — no margin | n/a | n/a |
| 10 | Move 71 short → Standard `gpu` 6h | +5 SU; <1 d dispatch | Low | Yes |
| 11 | `denoising_steps` 200→150 | Reject (alters output, OSF v3 §7) | n/a | n/a |
| 12 | Disorder threshold 0.60→0.55 | Locked | Locked | Locked |
| 13 | Recalibrate `num_samples` from v2 | 5-8 % wall idp_like | Med | If margin ≥1.3× |
| 14 | BS=6 for L<200 | +5-10 % wall, 2× VRAM | Med-high | Cautious only |
| 15 | Mark MSA precache deprecated | 0 SU; doc | None | Yes |

**Net R4 ceiling without scope change: 1+2+7+10 ≈ 10-15 % wall + 2-3 d queue.**

## 3. Per-opportunity deeper writeup

### #1 Walltime classification (biggest win)

All 82 PENDING request `1-00:00:00`. At 1.7× safety pad: 6 h tier (L<200)
71 proteins, 12 h (200-499) 19, 24 h (≥500 idp) 2. Add `bioemu_batch2_6h.sbatch`
(`--time=06:00:00 --mem=24G`). FS+backfill reward shorter walltimes — 71
short clear in hours not days.

### #2 XTC-only write mode

NPZ per chunk → final concat (sample.py:275); NPZs ~73 % bytes/dir.
Resume counts NPZs (sample.py:244). Mitigation: disable resume; full
re-run on failure (<5 % failure post-R3 — cheaper than I/O cost).

### #3 Persistent worker

11 completed paid ~25 min cold start ⇒ ~34 GPU-hr overhead across 82
PENDING. SQLite queue + 1 launcher/node. Breaks array isolation; trial
5-protein cohort first.

### #13 num_samples recalibration

v2: structured_globular actual=0.92 (pred 0.92, N=7); idp_like
actual=0.33 (pred 0.47, N=3). Defer until N≥20/class — locked formula
has 1.3× margin.

## 4. Exhaustion assessment

Untapped R4 levers: walltime classification, XTC-only writes, persistent
worker, mem right-sizing, num_workers. Locked: denoising_steps, disorder
threshold, partition tier. R4 ≈10-15 % wall + 2-3 d queue. R5 needs unlock.

## 5. Partition recommendation

Current: 9449458/9449459 → `scavenge_gpu` since 2026-04-25 PENDING 10+ days.
Standard `gpu` cost for 82-remainder ≈ 2,650 SU vs scavenge ≈ 265 SU
(10× cheaper) — but stalled.

**Hybrid:**

| Cohort | Partition | Walltime | SU/p | Total | Rationale |
|---|---|:--:|:--:|--:|---|
| 71 short (L<200, ≤6h) | `gpu` | 06:00:00 | ~6 | ~426 | Cuts queue 10 d → <1 d |
| 19 medium (≤12h) | `scavenge_gpu` | 12:00:00 | ~1.8 | ~34 | Absorbs re-queues |
| 2 long (≥500 idp) | `scavenge_gpu` | 24:00:00 | ~3.6 | ~7 | Already running |
| **Total** | mix | — | — | **~470** | vs ~265 stalled |

**Decision rule:** if `scavenge_gpu`-pending wait > `5 × est_runtime_hr`,
move to Standard. 71 short crossed (20 h threshold) days ago.
**Recommend immediate `scontrol`-move of L<200 → Standard `gpu --time=06:00:00`.**
Net +205 SU, save 7-9 d end-to-end. Worth ~30 SU/day saved schedule.

## 6. Verification

#1: bucketing dry-run, spot-check 5 vs the 11 completed.
#2: trial 1 short protein; verify XTC bit-identical.
#1+7+10 combined: 3-protein A/B/C trial before bulk re-submit.

End of report.
