---
type: optimization-recommendations
subphase: "1.2"
target: so3lr-vacuum-nvt-rescue
round: 4
date: 2026-05-05
author: optimization-subagent (round-4-so3lr)
status: APPLIED 2026-05-05 (items O1, O5, O6 applied to so3lr_rescue.sbatch; partition recommendation STAY-scavenge unchanged)
---

# SO3LR Vacuum NVT Rescue — Optimization Round 4 Analysis

## Executive summary

R1-R3 captured the largest, lossless wins (md_steps×10, save-buffer→5, JAX cache, XLA Triton GEMM, latency-hiding scheduler). The script is now close to **JAX/XLA throughput parity**. Remaining opportunities are mostly small (≤5%), narrowly scoped, or partition-related rather than code-related. **Do not pursue aggressive code changes; the highest-leverage move is partition+walltime sizing**, since the 5 ns runs only need ~12-17 hr (well under the current 24 hr ceiling).

The audit-revert on buffer-sr/lr (1.25/1.25) is correctly preserved and not negotiable.

## Opportunities table

| # | Category | Change | Est. Δ throughput | Risk | Quality preserved? |
|---|----------|--------|------------------:|------|--------------------|
| O1 | XLA flag | Add `--xla_gpu_enable_async_collectives=true` | 0-2% | none on single-GPU | yes |
| O2 | XLA flag | Add `--xla_gpu_enable_pipelined_all_gather=true --xla_gpu_enable_pipelined_reduce_scatter=true` | 0% (single-GPU) | NOT useful | n/a — skip |
| O3 | Walltime | Trim WW float64 walltime 24h→18h; GB3/NTL9 24h→14h | −0% wall, **billing fairness** | low (margin still 25%) | yes |
| O4 | save-buffer | Probe save-buffer=10 (vs 5) | ≤2% | minor — frame cadence ~50 ps | yes if cadence acceptable |
| O5 | XLA env | `XLA_PYTHON_CLIENT_PREALLOCATE=false` + `XLA_PYTHON_CLIENT_ALLOCATOR=platform` | <1% (init only) | none | yes |
| O6 | env probe | `CUDA_MODULE_LOADING=LAZY` to defer kernel load | 5-10s init | none | yes |
| O7 | Logging | Drop `nvidia-smi` line + `python -c "import jax; ..."` triple-import in sbatch | ~2-3 s | none | yes |
| O8 | Compile cache | Verify R3 cache hit-rate (audit-only) | should be ≥99% reused | n/a | n/a |
| O9 | md_steps | Probe md_steps=20000 (vs 10000) | <0.5% — likely saturated | minor — checkpoint cadence halved | possibly |
| O10 | Partition | scavenge_gpu vs gpu vs priority_gpu (see § below) | **Major billing Δ** | preemption risk on scavenge | n/a |
| O11 | NL backend | Investigate matscipy vs vesin neighborlist | unknown — needs SO3LR internal | medium | unknown — DEFER |

## Deeper per-opportunity discussion

### O1 — `--xla_gpu_enable_async_collectives=true` (low-risk add)
**File:** `output/scripts/so3lr_rescue.sbatch:94`. Append to existing `XLA_FLAGS`. On single-GPU, async collectives is mostly a no-op, but XLA documentation indicates it can permit overlap of host-device copies with compute when present. Estimated ≤2%. **No quality risk.** Recommend **add as a passive flag**.

### O2 — pipelined collective flags (skip)
Only useful for multi-GPU. Single-GPU SO3LR runs would not see any benefit; mentioning to be explicit that this category is exhausted.

### O3 — Walltime trim (high-leverage on Standard `gpu` only; neutral on scavenge_gpu)
Empirical wall times from §3.6 of pilot stability + 2026-05-02 gates:
- GB3 v1 (float32 dt=0.5): **11.85 hr / 5 ns** → +20% margin = ~14 hr safe
- NTL9 v1 (float32 dt=0.5): **11.18 hr / 5 ns** → ~14 hr safe
- WW float64 dt=0.25: **2× cost vs float32** (precision) × **2× cost** (timestep halved) ≈ 4× → ~28 hr; **24 hr is too tight** — recommend either keep 24h or break into 2 stages

**On `scavenge_gpu`**: walltime trimming has **no SU benefit** since scavenge is preemptible and you pay only for what runs. Do not bother.
**On Standard `gpu`**: trimming saves nothing on RTX 5000 Ada; SU bills for actual run time.
**On `priority_gpu`**: SU enforcer (`prio_su_enforce.sh`) projects via remaining-walltime × billing. Tight walltime here matters for budget pre-check. Trim is **only valuable if moving to priority_gpu** — which the rescue plan generally does not.

**Verdict:** No trim needed for current scavenge submissions. If a 5 ns run gets re-routed to priority_gpu later, set walltime to actual+25%.

### O4 — save-buffer=10 probe (small)
Currently 5 (R2). With md_steps=10000 and dt=0.5 fs, frame write cadence = 5 × 10000 × 0.5 fs = 25 ps. Bumping to 10 → 50 ps cadence. The pilot had save-buffer=50 (250 ps cadence) historically. **2,000 conformations target** for downstream analysis only requires ≥1-2 ps stride at minimum. 50 ps is fine for trajectory length QC and Rg checks but coarser than ideal for the back-calculation step. **Marginal benefit (<2%). Defer.**

### O5 — XLA Python client memory flags (init-only)
Add to sbatch:
```
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_ALLOCATOR=platform
```
This avoids 90% pre-allocation of GPU memory at JAX startup. SO3LR's working set is small (vacuum, ≤1.3K atoms). Saves no throughput but improves **cohabitation** if jobstats arms interactive checks. Estimated <1%. **Low risk; nice-to-have.**

### O6 — `CUDA_MODULE_LOADING=LAZY`
NVIDIA driver flag that defers kernel loading until actually called. Saves ~5-10 s of init per job on float32 path, ~10-15 s on float64. Across 3 jobs that's ~30-45 s. **Negligible at 5 ns (~12 hr) timescale (<0.1%).** **Low risk; OK to add as a hygiene flag.**

### O7 — sbatch preamble trim (cosmetic)
Lines 96-100 of sbatch run 4 separate Python invocations (`numpy`, `so3lr`, `jax`) and `nvidia-smi`. Each cold-imports `jax` (~3-5 s with cache, ~30-60 s without). On a hot cache this is ~15-25 s wasted. The runner imports JAX again. **Recommend: combine into one Python invocation** `python -c "import numpy, so3lr, jax; ..."` — saves ~10 s per job. **Negligible at 12 hr scale.** Keep as-is for clarity.

### O8 — Compile-cache hit-rate audit (REQUIRED — verify, do not change)
R3 set `JAX_COMPILATION_CACHE_DIR=/home/rag88/.cache/jax_compilation`. If the cache directory is **empty or missing** at submission time, R3's promised 30-60s→1-2s saving is not actually being realized. **head-1.2 should verify cache state pre-submission**:
```bash
ls -la /home/rag88/.cache/jax_compilation/  # should show .pb cache shards
```
If empty: first-run will populate it; subsequent runs benefit. **No code change required**, but flag for awareness.

### O9 — md_steps=20000 probe
R2 took md_steps from 5000→10000 (R1) → 10000 (R2). Each doubling halves Python-overhead per ps. At md_steps=10000 the Python overhead is already <1% of step time (the runner's `subprocess.run` blocks for the full duration, JAX+XLA do all the heavy lifting inside). **Doubling to 20000 likely yields <0.5%**. Risk: checkpoint write frequency halves (one checkpoint per 100 ps instead of 50 ps) — not great for scavenge_gpu preemption. **Defer; saturated.**

### O10 — Partition (see dedicated § below)

### O11 — NL backend (matscipy vs vesin)
SO3LR uses an internal neighborlist; both matscipy and vesin are common JAX-friendly options. Unknown without source inspection of the SO3LR package. Risk: changing NL backend can change cutoff edge cases. **Out of scope for round 4** — would be a multi-day investigation including correctness regression. **DEFER to Sub 1.4 if SO3LR throughput becomes a bottleneck for production scale.**

## Exhaustion assessment

The optimization landscape for SO3LR is **largely saturated**:

- **Compute kernels**: JAX/XLA via Triton GEMM is at or near optimal for tensor products.
- **Python overhead**: md_steps×10 reduced this to <1% of total time.
- **JIT compilation**: persistent cache means ~2 s overhead on repeats.
- **Memory**: vacuum systems are tiny (≤7K floats), GPU is bandwidth-saturated regardless.
- **NL choice**: untouched but high-risk; not a round-4 candidate.

**Net round-4 estimated upside: 2-5%** if O1+O5+O6 stack. Below the noise floor of GPU-to-GPU variation on RTX 5000 Ada.

The high-leverage round-4 move is **partition** (below), not script.

## Partition recommendation

Current state: 3 SO3LR jobs PENDING on `scavenge_gpu` (10567505 GB3, 10567506 NTL9, 10567507 WW). Job `q6w8q4r3xz` etc. submitted 2026-05-03.

**SU/$ comparison (per 5 ns rescue, RTX 5000 Ada, ~12 hr typical run):**

| Tier | Partition | Acct | Bill rate | Per-job cost | 3-job total | Wait risk | Preempt risk |
|------|-----------|------|----------:|-------------:|------------:|-----------|--------------|
| Free-ish | scavenge_gpu | pi_mg269 | **1.5 SU/hr** | ~18 SU | ~54 SU | low (preempt-friendly) | **HIGH — REQUEUE on demand** |
| Standard | gpu | pi_mg269 | 15 SU/hr | ~180 SU | ~540 SU | medium (fair-share 0.0146 deeply depleted) | none |
| Priority | priority_gpu | prio_mg269 | priority SU (small budget) | ~12 priority SU | ~36 priority SU | low | none, but SU enforcer pre-check |

### Decision matrix for the 3 SO3LR rescue 5 ns runs

1. **Default (current state): scavenge_gpu** is correct.
   - 10× billing reduction = ~54 SU vs 540 SU on Standard. Massive saving.
   - Preemption risk is mitigated by the runner's checkpoint/restart support (per docstring lines 17-18 + `--restart-load --no-relax`).
   - **Stay on scavenge_gpu unless preemption thrashes >2× restarts.**

2. **Move to Standard `gpu` only if**: scavenge preemption rate exceeds ~50% (i.e., 2+ requeue per job in <24 hr). Even then, cost penalty is 10×. **Requires user approval** per operational-practices.md "3× partition rule".

3. **Move to priority_gpu only if**: a 5 ns rescue is critical-path and Standard backlog blocks past **2026-05-08** (per submit_so3lr_rescue_production.sh comment lines 8-9). Priority is small budget but jobs run quickly. **Requires user approval** + SU enforcer pre-check.

### Specific recommendation for current state

**STAY on scavenge_gpu.** All 3 jobs PENDING since 2026-05-03; no preemption observed yet. The script has correct restart logic. Re-evaluate only if a job hits its 3rd preemption — at that point, weigh ~50 SU saved vs schedule risk and consider promotion.

**WW (float64 dt=0.25) is a special case**: at 4× cost it may need ~36-48 hr of compute. scavenge_gpu's 24 hr cap means **at least one restart is forced.** Plan for it. If WW fails to make progress past the 50%-mark in 24 hr, flag for partition decision.

## Summary recommendations to head-1.2

| Priority | Action | Effort | Risk |
|----------|--------|--------|------|
| 1 | **No script change required.** R1-R3 cumulative ~10-15% gain stands. | 0 | 0 |
| 2 | Verify JAX compile cache populated pre-submit (one-line `ls`) | 1 min | 0 |
| 3 | (Optional) Add `--xla_gpu_enable_async_collectives=true` to existing XLA_FLAGS | 1 line edit | 0 |
| 4 | (Optional) Add `XLA_PYTHON_CLIENT_PREALLOCATE=false` + `CUDA_MODULE_LOADING=LAZY` | 2 lines | 0 |
| 5 | **Stay on scavenge_gpu** for current 3 jobs. Monitor preempt rate. | 0 | scavenge inherent |
| 6 | If WW float64 fails to reach 50% in first 24 hr → flag for partition decision | watch | none |

**Bottom line: SO3LR is throughput-saturated at the script level. Any round-4 effort is best spent on partition decisions and post-run analysis, not flag tweaking.**
