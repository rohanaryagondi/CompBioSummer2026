---
type: optimization-recommendations
subphase: "1.2"
target: mace-hybrid-npt-prod
round: 4
date: 2026-05-05
author: optimization-subagent (round-4-mace)
status: APPLIED 2026-05-05 (items 1, 2, 5 applied to mace_hybrid_npt_prod.py; items 3-4 deferred per "saturated" verdict)
---

# MACE NPT Round 4 Optimization Analysis

## 1. Executive summary

- **Throughput is near-saturated** on the current stack (H200 OpenCL, torch
  2.10, e3nn, vesin NL, f32 bypass). Per `1.2-mace-throughput-ceiling.md`,
  the e3nn float32 forward pass alone is ~25 ms / step (~58-70 % of the step
  budget). Round 1-3 already swept the hot-Python opportunities. Realistic
  Round 4 headroom is in the **3-8 % band** without changing engine, model,
  or precision.
- **Two modest opportunities remain in-script**: cut a per-step `getState`
  copy by reusing an OpenCL `State` for both reporters and progress writes,
  and drop progress-JSON writes to per-checkpoint cadence. Both are
  callback-light and risk-low.
- **Biggest practical win is partition strategy, not script tuning.** Three
  closure-window jobs sat in PENDING for 36 + h on `scavenge_gpu` at LevelFS
  0.27. Moving WW + GB3 to Standard `gpu_h200` would cost ~10 × the SU but
  cut wall by ~1.5 days. NTL9 / ubq-alt 50-ps probes should stay scavenge.

## 2. Opportunities table

| # | Change | Est. throughput Δ | Risk | Quality preservation |
|---|--------|------------------:|:----:|----------------------|
| 1 | Per-chunk `getState` reuse: pass single `State` to NaN check + progress write (currently 2 calls / chunk) | +1-2 % | Very low | Identical numerics |
| 2 | Drop progress-JSON write from every chunk → every checkpoint (every 25 ps) | +0.3-1 % | Very low | Restart granularity unchanged (already capped by `CheckpointReporter`) |
| 3 | Logger `print` flush only on milestone steps (currently every 10 k steps; structural OK, leave as-is) | <0.1 % | None | n/a |
| 4 | `chunk_size` raise from 50 k → 100 k steps (still ≤ checkpoint cadence) | +0.5-1 % | Low | NaN check stride still 5 k |
| 5 | Disable `kineticEnergy` + `totalEnergy` on `StateDataReporter` (PE + T + V + ρ are sufficient for NPT QC) | +0.5-1.5 % | Low | OSF v3 §8 QC checks only need PE / T / V / ρ |
| 6 | Drop `ENERGY_PRECISION_DOUBLE`-style state copies (none currently active; verify no `getEnergy=True` in hot path beyond NaN check) | 0 % | n/a | Already done in R3 |
| 7 | OpenCL workgroup tuning via `OpenCLPrecision=mixed` platform property | -2 to +3 % (variance only) | Medium (numerics drift) | **Reject** — would alter classical force precision |
| 8 | `vesin` cell-list neighbour-list mode (currently `full_list=True`) → check if half-list is acceptable for MACE inputs | +1-2 % | Medium (MACE expects symmetric edges; half-list breaks model) | **Reject** — MACE forward pass requires `full_list=True` |
| 9 | Push GPU keepalive cadence 10 → 15 min | <0.05 % | Low (still 4× under 1-h auto-cancel) | n/a |
| 10 | CUDA graphs for the e3nn forward pass | unknown, blocked | High | **Reject** — requires reworking openmmml's PythonForce; e3nn graph is dynamic (NL changes shape per step) |
| 11 | `openmm-torch` migration (TorchForce + TorchScript MACE) | upstream blocked | n/a | **Reject** — confirmed dead in `1.2-mace-throughput-ceiling.md`: e3nn not TorchScript-compilable |
| 12 | LAMMPS engine swap (native MACE TorchScript) | +15-25 % | Very high (full driver rewrite, lose OpenMM equil + checkpoint) | **Defer to Sub 1.5+** |
| 13 | MIG-slice / multi-GPU H200 | n/a | n/a | **Reject** — single MACE forward is sequential; no parallelism within one trajectory. Per-protein H200 is already 1:1. |

**Net script-side ceiling: items 1 + 2 + 4 + 5 = ~3-5 % cumulative.**

## 3. Per-opportunity deeper writeup

### #1 — `getState` reuse in production loop (`mace_hybrid_npt_prod.py:894-905`)

Currently every chunk calls `check_nan` (line 895) which does
`simulation.context.getState(getPositions=True, getEnergy=True)`. The
progress-JSON write right after (lines 899-904) does NOT call `getState`
itself, so this point is fine. But equilibration (lines 754-765) calls
`check_nan` plus an inline state log. Each `getState` on a 17 k-atom
hybrid system is ~0.5-1 ms (positions copy GPU→CPU). At ~30 ms / step,
this is 1-2 % when fired every chunk. Action: thread the single state
through both consumers, do not re-fetch.

### #2 — Progress-JSON cadence (`mace_hybrid_npt_prod.py:898-904`)

Lines 898-904 write progress JSON every chunk (50 k steps). Atomic
write-and-rename costs ~1-2 ms but more importantly creates a steady fsync
load on `/nfs/roberts/scratch`. Recommend: write progress only when
`CheckpointReporter` fires (every 25 k steps via separate path) or when
walltime guard exits. Restart granularity is unchanged because
`progress["last_step"]` only matters when `chk_path` is also valid; the
step counter is already in the OpenMM checkpoint.

### #3 — `chunk_size` raise (`mace_hybrid_npt_prod.py:864`)

`chunk_size = min(CHECKPOINT_INTERVAL_STEPS, NAN_CHECK_INTERVAL_STEPS * 10)`
= `min(25_000, 50_000) = 25_000`. Currently dominated by checkpoint
interval; if we relax progress-JSON to checkpoint cadence (#2), the per-chunk
overhead drops, so any further raise gives <0.5 %. Leave as-is.

### #5 — `StateDataReporter` columns (`mace_hybrid_npt_prod.py:836-851`)

`StateDataReporter` with `kineticEnergy=True` + `totalEnergy=True` triggers
an extra getState path with `getVelocities` for KE and `getEnergy` (already
on for PE). With `report_steps = 5000` (every 5 ps) the cost is small
(~1 / 5000 of stepping), but compound across 5 ns × 3 proteins = 3 k reports.
Conservatively +0.5-1 %. OSF v3 §8 QC list is `T, ρ, V, PE` — KE / TE are
diagnostic only. Drop them; leave `temperature=True, volume=True,
density=True, potentialEnergy=True`.

### #9 — Keepalive cadence

`gpu_keepalive.py` is 5 min (line 36, `cadence=300`); the in-Python
backup in `mace_hybrid_npt_prod.py:257` is 10 min. YCRC auto-cancel
threshold is 1 h; we have 12 × and 6 × safety margins respectively. Going
to 15 min on the external process saves ~1 / 5000 forward passes — sub-noise.
Don't bother.

### #10/11/12 — Engine-level paths (rejected)

- **CUDA graphs**: e3nn's `convolution.spherical_harmonics` is dynamic
  in edge count; the graph would need re-capture every step. Negative ROI.
- **openmm-torch**: confirmed dead in `1.2-mace-throughput-ceiling.md`.
  No new MACE / e3nn release in 2026 changes this.
- **LAMMPS**: real ~15-25 % win but requires re-implementing equilibration,
  HBonds-constraint patch, sentinel-bond patch, walltime checkpointing.
  At 5 ns × 3 proteins, dev cost > runtime savings. Park for Sub 2 (10 ns
  baselines).

## 4. Honest exhaustion assessment

The following categories are **saturated** on the current stack:

- **Hot-loop Python / callback overhead** — R1 already pre-allocated
  constant tensors (lines 417-418). Remaining callback time is dominated
  by `_get_nh` (vesin, Rust, GIL-released) and the `model(inp,
  compute_force=True)` call itself. Both are non-Python.
- **CUDA / cueq tuning** — exhausted per `1.2-mace-throughput-ceiling.md`
  (cueq cublas mismatch, oeq API mismatch, openmm-cuda PTX failure).
- **Vesin NL parameters** — cutoff is fixed at 1.0 nm by the MACE-OFF24
  cut-off radius (`r_max`); buffer cannot drop without correctness loss.
- **GPU NL on torch** — explored in `mace_cuda_patch.py`; force match
  1e-15, but only 2.5 % gain because matscipy/vesin is already <2 ms /step.
  Disabled in production.
- **Float-32 bypass** — already applied (lines 391-467); 1.21 × confirmed.
- **Constraint tolerance** — already 1e-4 (line 653, R1).
- **Equilibration trim** — already 25 ps (line 181, R2).
- **MAX_MIN_ITER** — already 500 (line 709, R3).
- **Reporter strides** — DCD 5 ps (R2), CSV 5 ps, NaN 5 k (R1), checkpoint
  25 k (R1).

**Recommendation**: stop hunting Python micro-optimizations. The 3-5 %
script-side gain from items 1, 2, 4, 5 is real but not worth the risk of
touching production scripts mid-closure. Take it only if a fresh env
rebuild or a re-test cycle is already planned.

## 5. Partition recommendation

Current state per `dashboards/active-subphase.md`: 9 jobs PENDING on
`scavenge_gpu` for ~36 h with LevelFS 0.27 for `pi_mg269/rag88`. At
~2.56 ns/day, 5 ns per protein takes ~47 h of GPU wall-time once started.
Total wall = queue + runtime.

**SU/wall trade-off (5 ns × 1 protein, H200 hybrid)**:

| Tier | SU rate | Runtime SU | Queue wait (current) | Total wall | Verdict |
|------|---------|-----------:|---------------------:|------------|---------|
| `scavenge_gpu` | 30 SU/h | ~1,400 SU | 36-72 h | 80-120 h | **Default for closure-window 5 ns runs**. Free-tier; checkpoint survives REQUEUE. |
| Standard `gpu_h200` | 300 SU/h | ~14,000 SU | <1 h | ~48 h | **Use only when scavenge LevelFS<0.3 for >48 h AND deadline pressure exists**. 10 × cost for ~1.5-day savings. Single-protein cost (~$420 SU equivalent) is justifiable for one job near deadline. |
| Standard `gpu` (RTX 5000 Ada) | 15 SU/h | ~5,000 SU (×~2 wall at ~1 ns/day) | 0-12 h | ~120 h | **Reject for 5 ns** — wall is worse than scavenge_gpu_h200 due to RTX 5000 Ada being ~2.5 × slower. Useful only for <500 ps probes. |
| `priority_gpu` | 15 SU/h | ~5,000 SU (RTX 5000 Ada, ~2.5 × slower) | <1 h | ~120 h | **Reject** — budget is ~18.5 SU left; would blow cap on a single 5 ns run. Reserved for short probes. |

### When to leave `scavenge_gpu`

- **Stay on scavenge** if any of:
  - Deadline > 5 days out (closure deadline 2026-05-15 is +10 days; OK)
  - LevelFS climbing back toward 0.5+ within 24-48 h
  - Multiple proteins still queued (better to throttle than burn 10 ×)
- **Move to `gpu_h200` Standard** if **all** of:
  - LevelFS stays <0.3 for >48 h with no PENDING-→-RUNNING progress
  - We are within 4 days of OSF deposit and need NPT evidence on the deposit
  - User explicitly approves the 10 × SU multiplier (per operational-practices
    `Per user 3× partition rule`: scavenge → Standard requires explicit OK)
- **Never** move 50-ps probes off scavenge — they're trivial in SU and the
  queue rotates them within hours.

### Concrete recommendation for current run

WW (10567503) and GB3 (10567504) are the two productions that block
criterion #1. If they have not started by **2026-05-08T00:00Z** (3 days
from now, leaving 7 days to deposit), escalate: ask user to approve a
single same-tag resubmission of WW on Standard `gpu_h200` (~14 k SU).
GB3 stays on scavenge. NTL9 + ubq-alt probes stay scavenge regardless.

## 6. Final verdict

Script: ~3-5 % theoretical gain from items 1, 2, 4, 5 — **defer unless
a routine re-edit cycle is opening**. Risk of touching production driver
mid-closure outweighs the marginal throughput.

Operational: **partition timing is the live optimization knob**. Keep
scavenge as default; stage Standard `gpu_h200` upgrade as a deadline
escape valve, not a baseline.

Engine: parked. LAMMPS for Sub 2; openmm-torch / cueq / oeq still upstream-blocked.
