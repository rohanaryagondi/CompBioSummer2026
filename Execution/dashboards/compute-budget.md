---
last_updated: 2026-05-04T05:00:00Z
updated_by: head-1.2 (housekeeping subagent; doc-audit batch 2: UBQ option-c+d probes added on scavenge_gpu (free billing); SU tracker unchanged at 231.5/250)
---

# Compute Budget Tracker

## Budget Overview (from Implementation Plan Section 9.1)

| Track | Phase | Allocated GPU-hrs | Used GPU-hrs | Remaining | GPU Type |
|-------|-------|-------------------|-------------|-----------|----------|
| Alpha-M | Phase 0 | <2 | 0.5 | — | Any |
| Alpha-M | Phase 1 (pilot) | 3,000 | ~152 | ~2,848 | H200 |
| Alpha-M | Phase 2 (production) | 47,300 | 0 | 47,300 | H200 / any (revised 1.40× for OpenCL) |
| Alpha-M | Phase 3 (replicas) | 122,900 | 0 | 122,900 | H200 (revised 1.40× for OpenCL) |
| Alpha-M | Contingency (20%) | 34,050 | 0 | 34,050 | H200 (revised 1.50×) |
| Gamma | All phases | 2,000 | ~163 | ~1,837 | Any |
| Delta | All phases | 20,000 | ~2.3 | ~19,998 | RTX 5000 Ada |
| **Total** | | **~229,650** | **~317** | **~229,333** | (revised 2026-04-17; see `shared/notes/1.1-mace-phase2-feasibility.md`) |

## SU Rate Reference

| GPU | SU/hr (Standard) | SU/hr (scavenge_gpu) | Relative Cost (vs RTX 5000 Ada Standard) |
|-----|------------------|----------------------|------------------------------------------|
| RTX 5000 Ada | 15 | **1.5** (10×↓) | 1× / 0.1× |
| RTX Pro 6000 Blackwell | 65 | **6.5** (10×↓) | 4.3× / 0.43× |
| A100 | 100 | (not avail) | 6.7× |
| H200 | 300 | **30** (10×↓) | 20× / 2× |
| B200 | 370 | **37** (10×↓) | 24.7× / 2.5× |
| L40S | (not in standard tiers) | ~1.5 | 0.1× |

**scavenge_gpu policy (added 2026-05-03):** Standard Tier `scavenge_gpu` partition charges **10× lower SU rates** than other Standard partitions. Tradeoff: PreemptMode=REQUEUE (jobs get killed and re-queued when higher-priority work needs the node). Our scripts (mace_hybrid_npt_prod.py, so3lr_rescue_runner.py) have full checkpoint/restart so survive preemption. **All 7 Sub 1.2 closure jobs are on scavenge_gpu** as of 2026-05-03. Per user 3× partition rule, any move OFF scavenge to Standard tier requires explicit user approval.

**Policy:** Prefer RTX 5000 Ada for workloads that fit in 32 GB VRAM. Use H200/B200
only when queue wait >1h or workload needs >32 GB. BioEmu, GEARS, scGPT, CPA all
fit on RTX 5000 Ada.

---

## Subphase 1.1 Compute — Final

| Task | Track | Est. GPU-hrs | Actual GPU-hrs | GPU Type | Notes |
|------|-------|-------------|----------------|----------|-------|
| task-001 MACE crambin NVT | Alpha-M | 5-20 | ~2.5 | H200 | OpenCL fallback |
| task-002 SO3LR crambin NVT | Alpha-M | 5-20 | ~1.8 | RTX 5000 Ada | CLI-based |
| task-003 BioEmu batch 1 | Gamma | 15-20 | ~107 | Mixed → RTX 5000 Ada | 47 proteins + topup |
| task-004 GEARS setup | Delta | 1-3 | ~0.5 | H200 | Short test runs |
| task-005 HEWL sidechain recon | Alpha-M | 0 | 0 | CPU only | PDBFixer |
| task-006 scGPT + CPA setup | Delta | 1-3 | ~0.01 | H200 | Short test runs |
| task-007 Benchmark expansion (post-subphase) | Alpha-M | - | ~0.45 | RTX 5000 Ada | 5 BioEmu jobs (NTL9/ACBP/FKBP12/EnHD/Crambin) + Crambin SG-SG recon |
| MACE hybrid empirical validation (task-007 follow-up) | Alpha-M | - | ~17 | RTX 5000 Ada | 3 rounds of WW/UBQ/GB3 hybrid tests; 2 rounds failed (scavenge preemption, NaN), 1 round TIMEOUT with throughput measured. 2026-04-17/18. |
| Delta Tier 1 completion (task-007 follow-up) | Delta | - | ~0.8 | RTX 5000 Ada | scFoundation + Tahoe-x1 3B GPU smoke tests |
| MACE Option investigation (task-007 follow-up) | Alpha-M | - | ~4 | Mixed (RTX 5000 Ada + H200) | Subagent K implicit (~0.4), Subagent J rebuild probe (~0.8), Subagent L CUDA fix+bench (~0.4), H200 hybrid benchmark (~2.5) |
| **Subphase 1.1 total** | | **~27-66** | **~134** | | |

**Why actual >> estimate for task-003:** Original estimate assumed 2,000 samples per
protein with ~90% average pass rate. Actual pass rates ranged 0.7%-99%, requiring
oversampling up to 16,800 denoised samples (SPG1_STRSG, 14.4% pass rate). The topup
round added ~75 GPU-hours to reach >= 2,000 physical conformations for all 46 proteins.

---

## Storage Budget (from Implementation Plan Section 9.2)

| Data | Allocated | Used | Location |
|------|-----------|------|----------|
| Alpha-M trajectories | 8 TB | 0 | HPC scratch |
| BioEmu/Boltz-2/AlphaFlow ensembles | 5 GB | ~2.5 GB | HPC scratch |
| Tahoe-100M raw | 630 GB | 428.89 GB | HPC scratch |
| Tahoe-100M processed | 200 GB | 0 | HPC scratch |
| DL checkpoints | 100 GB | 0 | HPC scratch |
| Analysis output | 10 GB | 0 | HPC scratch |
| **Total** | **~9 TB** | **~431 GB** | |

---

## Burn Rate

| Period | GPU-hrs Used | SU Consumed | Cumulative GPU-hrs | Notes |
|--------|-------------|-------------|-------------------|-------|
| Phase 0 (Apr 15-16) | 0.5 | ~8 | 0.5 | BioEmu SS test only |
| Sub 1.1 (Apr 16-17) | ~112 | ~9,900 | ~112 | MLFF + BioEmu + Delta |
| Sub 1.1 closure (Apr 17-18) | ~22 | ~1,100 | ~134 | Robustness remediation + MACE Options 2/4/5 investigation |
| Sub 1.2 actual (Apr 19-25) | ~130 | ~6,630 | ~264 | SO3LR 58h + MACE failed/diag 16h H200 + BioEmu 56h + Delta 1h; MACE production + BioEmu 83 proteins still pending |
| **Sub 1.2 remaining (est)** | **~575** | **~122,700 (est)** | **~839 (projected)** | MACE NPT 3×5ns H200 (~420h, ~126K SU) + BioEmu 83 remaining (~155h, ~2,300 SU) |

### Sub 1.1 SU Breakdown (Final)

| Task | GPU-hrs | GPU Type | Est. SU |
|------|---------|----------|---------|
| MACE crambin NVT | ~2.5 | H200 | ~750 |
| SO3LR crambin NVT | ~1.8 | RTX 5000 Ada | ~27 |
| BioEmu initial batch | ~32 | Mixed gpu/H200 | ~5,700 |
| BioEmu topup round | ~75 | RTX 5000 Ada | ~1,125 |
| GEARS setup | ~0.5 | H200 | ~150 |
| scGPT+CPA test | ~0.01 | H200 | ~3 |
| Benchmark expansion (task-007) | ~0.45 | RTX 5000 Ada | ~6.72 |
| MACE hybrid empirical (task-007 follow-up) | ~17 | RTX 5000 Ada | ~256 |
| Delta Tier 1 completion (task-007 follow-up) | ~0.8 | RTX 5000 Ada | ~12 |
| Option 2/4/5 MACE investigation | ~4 | Mixed | ~770 (Subagent K 6 + Subagent J 45 + Subagent L 11 + H200 benchmark ~750 via gpu_h200) |
| **Total** | **~134** | | **~8,807** |

**Lesson learned:** BioEmu topup on RTX 5000 Ada cost ~1,125 SU for 75 GPU-hours.
The same work on H200 would have been ~22,500 SU. The shift to RTX 5000 Ada for all
BioEmu work saved ~21,000 SU. Future batches must use RTX 5000 Ada exclusively.

---

## SU Breakdown by Partition (Subphase 1.1)

| Partition | SU Consumed | % of Total |
|-----------|-------------|------------|
| gpu_h200 | ~6,316 | ~65% |
| gpu_b200 | ~2,118 | ~22% |
| gpu (RTX 5000 Ada) | ~1,174 | ~12% |
| gpu_devel | ~205 | ~2% |
| **Total** | **~9,813** | **100%** |

All jobs used Standard Tier (`pi_mg269`). No Priority Tier usage to date.

---

## Gamma Budget Detail

| Item | GPU-hrs | Notes |
|------|---------|-------|
| Allocated (all phases) | 2,000 | |
| Batch 1 generation | ~32 | Initial 47 proteins |
| Batch 1 topup | ~75 | 32 proteins oversampled |
| Batch 2 partial (10/93 complete) | ~56 | 10 proteins done; 83 resubmitted (9449458+9449459 PENDING) |
| **Used** | **~163** | |
| **Remaining** | **~1,837** | For batch 2 remaining (~83 proteins) + analysis |

Batch 2 estimate: ~100 proteins at ~2.3 GPU-hrs/protein (using pass rate data for
oversampling) = ~230 GPU-hrs. Budget is sufficient with ~1,600 GPU-hrs margin.

---

## Sub 1.2 Closure SU Enforcement (2026-05-03)

| Item | Value |
|------|-------|
| Priority budget cap | **250 SU** (reduced from 800; further reduced from original 108.5 cap) |
| Priority used | 231.5 SU (16 jobs incl. UBQ NPT iteration) |
| Priority remaining | 18.5 SU |
| Status | WITHIN_BUDGET (projected) |
| Enforcement script | `output/scripts/prio_su_enforce.sh` — projects in-flight SU + auto-cancels offenders + writes `head-1.2-su-budget-auto-cancel-*.md` notification |
| Wrappers wired with pre-check | `submit_mace_npt_prod.sh`, `submit_so3lr_rescue_production.sh` (only fires when partition=priority_gpu) |
| Auto-cancel events | 1 (10463305 WW SO3LR rescue cancelled 2026-05-02 22:58Z when projected exceeded cap; resubmitted on Standard `gpu` then moved to scavenge_gpu) |

## Priority Tier

| Item | Value |
|------|-------|
| Account | `prio_gerstein` |
| CPU partition | `priority` |
| GPU partition | `priority_gpu` |
| GPU types | rtx_5000_ada, rtx_pro_6000_blackwell, h200, b200 |
| Rate | $0.004 / SU |
| Fairshare | Separate pool from Standard Tier |

**Policy:** Use Priority Tier for small jobs (<400 SU total). Always confirm with
user before submitting. Priority and Standard Tier have separate fairshare pools,
so priority usage does not affect standard queue position.

### Money Spent

| Tier | SU Consumed | Cost |
|------|-------------|------|
| Standard (pi_mg269) | ~9,813 | $0.00 (free) |
| Priority (prio_gerstein) | 0 | $0.00 |
| **Total** | **~9,813** | **$0.00** |

---

## Alerts

- **BioEmu batch 2 planning:** Use oversampling formula from `shared/notes/1.1-bioemu-passrates.md`:
  `num_samples = ceil(2000 / pass_rate * 1.3)`. Pre-screen for disorder (>60% = exclude).
  Sub 1.2 task-004 implements the upstream screen.
- **SPG1-class proteins:** Proteins with <15% pass rate need `--mem=40G` for XTC assembly
  (>10K NPZ files require ~22 GB RAM).
- **RTX 5000 Ada is the default GPU** for all BioEmu and Delta workloads. H200/B200 only
  when justified by memory or queue requirements.
- **Sub 1.2 H200 burn (~125K SU):** task-001 MACE NPT will consume the largest single-task
  SU outlay so far. This is justified by Option 5 commitment (H200 OpenCL is 11.5× faster
  than RTX 5000 Ada for MACE hybrid). All MACE Phase 2 production will follow same pattern.

---

## Sub 1.2 Compute — Planned

| Task | Track | Est. GPU-hrs | GPU Type | Notes |
|------|-------|-------------|----------|-------|
| task-001 MACE NPT (3 × 5 ns) | Alpha-M | 420 | H200 (gpu_h200) | WW ~95, GB3 ~140, UBQ ~185 GPU-hrs (extrapolated from Sub 1.1 §11). Checkpoint/restart mandatory. |
| task-002 SO3LR vacuum (5 × 5 ns) | Alpha-M | 3 | RTX 5000 Ada | ~15 ns/day per protein. |
| task-003 OSF pre-reg | (cross) | 0 | — | Pure writing. |
| task-004 BioEmu batch 2 | Gamma | 250 | RTX 5000 Ada | ~100 proteins × ~2.5 GPU-hrs avg with oversampling. |
| task-005 Delta baselines + harness | Delta | 30 | RTX 5000 Ada | Tahoe-100M 1M-cell subsample. |
| task-006 Stats pipeline | (cross) | <1 | CPU only | Standard Tier per user. |
| **Sub 1.2 total** | | **~705** | | **~129,300 SU est** |

Phase 1 Alpha-M budget remaining after Sub 1.2 (projected): ~2,428 GPU-hrs (3,000 - 152 used to date - 420 remaining MACE production est = ~2,428).
