---
last_updated: 2026-05-05T18:00:00Z
updated_by: head-1.2 (bioemu-reorg subagent; Round-4 #1+#2+#6+#7 applied — 3-tier walltime split + L<200→Standard gpu; arrays 9449458/9449459 cancelled, replaced by 10730244/10730245/10730246)
---

# Active Subphase

| Item | Value |
|------|-------|
| Subphase | 1.2 |
| Title | MLFF Stability Pilots, BioEmu Batch 2, Delta Baselines, OSF Pre-Registration |
| HeadAI | head-1.2 |
| Start date | 2026-04-19 (launched) |
| Target end | 2026-05-16 |
| **Hard deadline** | **OSF deposit 2026-05-15** |
| Status | **MACE NPT FIXED (Round 3 recipe validated 2026-05-02T10:31Z).** After 8 diagnostic configurations across 3 sessions, the production recipe is: **sentinel-bond + protein HBonds constraints + dt=1 fs MACE NPT**. Validated to 100 ps clean on WW (test_P, job 10441986, density 1.041 g/cm³, T 297.6 K, PE stable). Root cause: openmm-ml issue #91 (singleton-molecule scaling under MonteCarloBarostat) + inadvertently stripped protein H-bond constraints. Recipe documented in `shared/notes/1.2-mace-npt-fixed.md`; reproducible from `output/scripts/npt_diagnostics/test_L_hbonds.py`. OSF v3 reverted from NVT-lock to NPT framing. SO3LR 2/5 PASS (GB1+UBQ Tier B). 4/6 task-spec tasks complete; task-004 BioEmu 10/92 done (CD19_HUMAN excluded, 82 PENDING: 9449458+9449459 fair-share blocked). Priority SU consumed so far: 58.8 + ~8.3 (test_P) = ~67/108.5 used; under cap. |

### Task Status

| Task ID | Title | Wave | Status | Agent |
|---------|-------|------|--------|-------|
| task-001 | MACE-OFF24 NPT 5 ns × 3 Tier B (WW, GB3, ubiquitin) on H200 OpenCL hybrid | 1 | **CLOSURE in flight 2026-05-02:** Round 3 recipe FIXED (sentinel-bond + protein HBonds constraints + dt=1 fs; validated 100 ps clean on WW via test_P). Production driver `output/scripts/mace_hybrid_npt_prod.py` written. **Probes submitted on priority_gpu**: GB3 (10458154 b8r3kt5x, 1:30 walltime), UBQ (10458155 c4n7vp2j, 2:00 walltime). WW already validated. Production HELD pending probe verdicts → then 5 ns × 3 on Standard Tier gpu_h200 (~125K standard SU within plan). | mlff-mace-pilot |
| task-002 | SO3LR vacuum NVT 5 ns × 5 Tier A/B (WW, GB3, GB1, NTL9, ubiquitin) on RTX 5000 Ada | 1 | **2/5 PASS (initial); RESCUE LAUNCHED 2026-05-02 16:02Z** for WW + GB3 + NTL9. Strategic finding: GB3 + NTL9 have 0 ARGs each, so PDBFixer LYN/ASH/GLH variants suffice (no custom ARN needed). Neutral prep verified: GB3 864 atoms, NTL9 808 atoms, both side-chain charge=0. **3 gates submitted on priority_gpu/prio_mg269**: WW 10458603 (r4w7q8nx, float64+dt=0.25fs+NHC chain=5), GB3 10458604 (g3b6kt2p, neutral prep), NTL9 10458605 (n9t4mv5h, neutral prep). Total ~19 priority SU. All PENDING. Production HELD pending gate verdicts. Tier-2 fallback ready: counter-ion shell for charged proteins, float64+dt=0.5fs for WW. | mlff-so3lr-pilot (rescue) |
| task-003 | OSF pre-registration drafting + lock | 1 | **v2 DRAFTED** (updated with real power analysis from task-006, 2/5 SO3LR results); user deposits by May 15 | osf-prereg |
| task-004 | BioEmu batch 2 (~100 ProteinGym proteins) with disorder pre-screen + oversampling | 2 | **10/92 COMPLETE, 82 PENDING fair-share** (v1 arrays 9098344-47 cancelled 2026-04-24T22:17Z; resubmitted as 9449458 (41 proteins, 24h) + 9449459 (41 proteins, 24h) on gpu; all PENDING Priority). **CD19_HUMAN EXCLUDED** (scancel 9449459_1 on 2026-04-30; 1.4% actual pass rate, would need ~188K samples). 93→92 proteins. | bioemu-batch2 |
| task-005 | Delta 5 baselines + WMSE evaluation harness | 2 | **COMPLETE** (all 5 baselines + harness tested on 100K Tahoe; D3 retired) | delta-baselines |
| task-006 | Statistical pipeline core (Friedman/Nemenyi, ICC, bootstrap, JZS BF, T_min) | 2 | **COMPLETE** (all 5 components + unit tests; JZS BF matches R to 0.0001%) | stats-pipeline |

### Live SLURM job inventory (2026-05-04T05:00Z)

**Current closure jobs — all on Standard Tier `scavenge_gpu` (1/10 billing) with 3-round-optimized scripts:**

| JobID | Tag | Work | Walltime | State | Notes |
|-------|-----|------|----------|-------|-------|
| 10567503 | q6wmsv5n | MACE WW NPT 5 ns | 23:59:00 | PENDING (Priority) | scavenge_gpu, gpu:h200:1 |
| 10567504 | q6gpsv9k | MACE GB3 NPT 5 ns | 23:59:00 | PENDING (Priority) | scavenge_gpu, gpu:h200:1 |
| 10567505 | g7p4tv8m | SO3LR GB3 5 ns rescue | 1-00:00:00 | PENDING (Priority) | scavenge_gpu, gpu:1 (RTX 5000 Ada) |
| 10567506 | n5h6kx9q | SO3LR NTL9 5 ns rescue | 1-00:00:00 | PENDING (Priority) | scavenge_gpu, gpu:1 |
| 10567507 | w8q4r3xz | SO3LR WW 5 ns rescue (float64+dt=0.25fs+chain=5) | 1-00:00:00 | PENDING (Priority) | scavenge_gpu, gpu:1 |
| **10730244** | **q6sht3az** | **BioEmu batch 2 SHORT (53 idx, L<200)** | 6:00:00 | PENDING (Priority) | **Standard `gpu`**, gpu:rtx_5000_ada:1; reorg 2026-05-05 (was 9449458/9 part) |
| **10730245** | **q6med7kp** | **BioEmu batch 2 MEDIUM (18 idx, L=200-499)** | 12:00:00 | PENDING (Priority) | scavenge_gpu, gpu:rtx_5000_ada:1; reorg 2026-05-05 |
| **10730246** | **q6lng5wm** | **BioEmu batch 2 LONG (11 idx, L≥500)** | 23:59:00 | PENDING (Priority) | scavenge_gpu, gpu:rtx_5000_ada:1; reorg 2026-05-05 |
| **10622876** | **q6kz3m8x** | **NTL9 50ps probe (UBQ option-c substitute)** | 5:55:00 | PENDING | scavenge_gpu, gpu:h200:1; submitted 2026-05-04 |
| **10622885** | **q6uadt05** | **UBQ_alt 1XQQ 50ps probe (UBQ option-d alt-starting-structure)** | 5:55:00 | PENDING | scavenge_gpu, gpu:h200:1; submitted 2026-05-04 |

**Optimization rounds applied (cumulative ~30-35% MACE + ~10-15% SO3LR + 90% billing reduction):**

| Round | MACE script changes | SO3LR script changes |
|-------|---------------------|----------------------|
| R1 (2026-05-03 ~17:00Z) | constant-tensor pre-alloc, NaN/checkpoint cadence, constraint tol 1e-4, drop speed=True | md_steps×5, JAX cache + persistent dir |
| R2 (2026-05-03 ~17:30Z) | DCD 5ps stride, NPT_EQUIL 50→25 ps, OMP/MKL=4, keepalive 5→10 min | md_steps→10000, save-buffer→5; **audit-revert** buffer-sr/lr to defaults 1.25/1.25 (silent NL underflow risk at t=0) |
| R3 (2026-05-03 ~19:30Z) | drop forces from check_nan, MAX_MIN_ITER 500, NUMA OMP_PROC_BIND | XLA Triton GEMM flags |
| R4 (2026-05-05) | check_nan optional-state arg (defensive); progress-JSON write at checkpoint cadence only; drop KE+TE from StateDataReporter | XLA_FLAGS += `--xla_gpu_enable_async_collectives=true`; `XLA_PYTHON_CLIENT_PREALLOCATE=false`; `CUDA_MODULE_LOADING=LAZY` |

**Probe terminal state (2026-05-02 → 2026-05-03):**
- 10458154 (b8r3kt5x): MACE GB3 probe TIMEOUT at 25 ps clean — recipe generalizes ✓
- 10458155 (c4n7vp2j): MACE UBQ probe FAILED NaN @ 7-8 ps (dt=1.0 fs)
- 10463455 (q6u4n8mx): MACE UBQ retry FAILED NaN @ 8-9 ps (dt=0.5 fs, walltime-reduced via scontrol to 1:30)
- 10475183 (q6u4dt25): MACE UBQ Tier-2 retry FAILED NaN @ 9.6 ps (dt=0.25 fs on gpu_devel) — pattern asymptotic, not converging. **Escalated via `head-1.2-mace-ubq-non-generalization.md`.**
- 10458603 (r4w7q8nx): SO3LR WW gate cancelled by SU enforcer (replaced by full 5ns rescue in current cycle)
- 10458604 (g3b6kt2p): SO3LR GB3 gate COMPLETED 500 ps clean ✓
- 10458605 (n9t4mv5h): SO3LR NTL9 gate COMPLETED 500 ps clean ✓

**Cancelled (3 cycles of cancel/resubmit for optimization+audit):**
- gpu_h200/gpu Standard original: 10463584/85, 10465437, 10470003/05
- scavenge_gpu Round 1: 10550447-451
- scavenge_gpu Round 2: 10558479-483

### Live SLURM job inventory (HISTORICAL — 2026-04-30T13:00Z)

**MACE — Test H wrapping fix queued on priority_gpu:**

| Job ID | Cryptic | Partition | Task | State |
|--------|---------|-----------|------|-------|
| 10328941 | 2cp2fn3k | gpu_devel | Test H: MACE NPT f32 wrapping fix (50ps equil + 150ps prod) | **COMPLETED — FAIL** (NaN at ~5ps equil) |

*Test H FAILED 2026-05-01. NPT confirmed not viable. NVT is production path (Path B). Sub 1.3/1.4 implements classical NPT equil → MACE NVT prod per `output/npt_nvt_production_plan.md`.*

**BioEmu — PENDING (reason: Priority):**

| Job ID | Cryptic | Partition | Task | State |
|--------|---------|-----------|------|-------|
| 9449458 | x9sok7yl | gpu | BioEmu batch 2 — 41 proteins (24h) | PENDING (Priority) |
| 9449459 | l5uw4lsy | gpu | BioEmu batch 2 — 41 proteins (24h; CD19_HUMAN idx 1 cancelled) | PENDING (Priority) |

**Terminal failures (all tracked; archived):**

| Job IDs | Tags | Task | Cause | Audit doc |
|---------|------|------|-------|-----------|
| 8885960-62 | m4k2pz9q + 2 | MACE NPT v1 | conda-path bug (4-5s) | 1.2-mace-conda-path-fix.md |
| 8893817-19 | t4x7qn2w + 2 | MACE NPT v2 | NODE_FAIL / various env issues | — |
| 8939395-97 | q3m8p7xd + 2 | MACE NPT v3 | YCRC auto-cancel (0% GPU util, matscipy GIL) | 1.2-gpu-util-efficiency.md |
| 9012190-92 | srf586dh + 2 | MACE NPT v3b | CANCELLED (torch 2.10 CUDA PTX error) | 1.2-mace-throughput-ceiling.md |
| 9287505-07 | cnzm0un1 + 2 | MACE NPT v4 | Accidentally cancelled 2026-04-24T22:17Z (never ran) | — |
| 9449439 | cnzm0un1 | MACE NPT WW v5 | Checkpoint particle mismatch (stale from prior solvation) | mace_npt_config_audit.md |
| 9449440 | jnf64gj4 | MACE NPT GB3 v5 | StateDataReporter _dof AttributeError (monkey-patch skipped _initializeConstants) | mace_npt_config_audit.md |
| 9449441 | y4rdili5 | MACE NPT UBQ v5 | NaN after 1.7 min production (5 ps NPT equil insufficient for 17K atoms) | mace_npt_config_audit.md |
| 8886091-95 | p3v8xt7r + 4 | SO3LR v1 | typing_extensions env-var bug | 1.2-env-so3lr-typing-extensions-fix.md |
| 9096918 | lxtrtfdm | SO3LR | Stale; cancelled intentionally 2026-04-24 | — |
| 8903490 | t0x8pyfc | BioEmu b1 | batch_size=0 + timeout | head-1.2-bioemu-batch-size-zero.md |
| 9098344-47 | kacma9ky + 3 | BioEmu b2 v1 | Accidentally cancelled 2026-04-24T22:17Z (partially ran: 10 success) | — |
| 9546808 | d6v6fxwq | MACE v6 diag (gpu) | Cancelled 2026-04-27; resubmitted as 9612539 on priority_gpu | — |
| 9612539 | d6v6fxwq | MACE v6 diag (priority_gpu) | **NaN at step ~25500/50000 (25ps) of NPT equil** — MC barostat + MACE hybrid instability. 11.2 SU on prio_mg269. | npt_diagnostics/ |
| 9763415,9763417,9763658 | q62v1dan + 2 | NPT diag A/B/F (path bug) | BASH_SOURCE resolves to /var/spool/slurmd/ on compute node; test scripts not found. 0.04 SU total. | — |
| 9804704 | q6byygle | NPT Test A classical | **PASS** — 80 ps clean NPT, T=292-307 K, density 1.02-1.03. Exit 6 from keepalive thread cleanup (not real failure). 0.12 SU. | npt_diagnostics/ |
| 9804705 | q6wjsyhu | NPT Test B freq=100 | **FAIL** — NaN at ~5 ps equil. Barostat frequency does not help. 3.2 SU. | npt_diagnostics/ |
| 9804708 | q6q6ijfi | NPT Test F f64 MACE | **FAIL** — NaN at ~17 ps equil. f64 delays but doesn't fix. 3 healthy checkpoints (5/10/15 ps). 43.9 SU. | npt_diagnostics/ |

### Wave Protocol Summary

**Wave 1 (parallel, 3 agents):** task-001 + task-002 + task-003. Launch immediately.
**Partial-completion trigger for Wave 2:** ALL THREE of:
1. task-001 SLURM jobs *submitted* (multi-day run; do NOT wait for completion)
2. task-002 SLURM jobs *submitted*
3. task-003 `osf-prereg-v1.md` ≥80% complete

**Wave 2 (parallel, 3 agents):** task-004 + task-005 + task-006. Independent of Wave 1 results.

### Compute Budget (Sub 1.2 estimate)

| Task | GPU-hrs | GPU type | Est. SU |
|------|--------:|----------|--------:|
| task-001 MACE NPT diagnostics + Test H | 4 | RTX 5000 Ada (priority_gpu) | ~108.5 (prio SU) |
| task-002 SO3LR vacuum (5 × 5 ns) | 3 | RTX 5000 Ada | ~50 |
| task-003 OSF pre-reg | 0 | (none) | 0 |
| task-004 BioEmu batch 2 | 250 | RTX 5000 Ada | ~3,750 |
| task-005 Delta baselines | 30 | RTX 5000 Ada | ~450 |
| task-006 Stats pipeline | <1 | CPU | <30 |
| **Total** | **~705** | | **~129,300** |

### Gate Evidence Sub 1.2 Will Produce

| Gate | Date | Evidence |
|------|------|----------|
| D2 (June 30) | preliminary | 5-ns MACE NPT on 3 Tier B + 5-ns SO3LR vacuum on 5 Tier A/B = preliminary G1 path validation. D2 G1 formal evidence (≥10 ns × ≥3 Tier B) is Sub 1.4 scope. |
| D3 (June 6) | retiring | task-005 baselines complete fully retires the last D3 outstanding criterion. D3 will be ASSESSED: GO with all 5/5 + baselines after Sub 1.2. |

### Cross-Agent Notes Expected from Sub 1.2

| Note | Tracks | Urgency |
|------|--------|---------|
| `1.2-mace-npt-stability.md` | alpha-m | important |
| `1.2-so3lr-pilot-stability.md` | alpha-m | info |
| `1.2-osf-deposited.md` | alpha-m, gamma, delta, combined | **critical** (locks analysis plan) |
| `1.2-bioemu-batch2-passrates.md` | gamma | important |
| `1.2-delta-baselines-results.md` | delta, combined | important |
| `1.2-stats-pipeline-validation.md` | alpha-m, gamma, delta, combined | important |

### Resolved User Decisions (2026-04-18)

1. **MACE NPT scope: 3 proteins × 5 ns** (highest scope option). Within Phase 1 Alpha-M budget (3,000 GPU-hrs).
2. **OSF deposit: split.** osf-prereg drafts; user deposits; user provides DOI back.
3. **stats-pipeline: Standard Tier only.** No Priority Tier escalation.
