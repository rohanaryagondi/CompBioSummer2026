---
last_updated: 2026-04-17T23:30:00Z
updated_by: planner
---

# Compute Budget Tracker

## Budget Overview (from Implementation Plan Section 9.1)

| Track | Phase | Allocated GPU-hrs | Used GPU-hrs | Remaining | GPU Type |
|-------|-------|-------------------|-------------|-----------|----------|
| Alpha-M | Phase 0 | <2 | 0.5 | — | Any |
| Alpha-M | Phase 1 (pilot) | 3,000 | ~4.3 | ~2,996 | H200 |
| Alpha-M | Phase 2 (production) | 47,300 | 0 | 47,300 | H200 / any (revised 1.40× for OpenCL) |
| Alpha-M | Phase 3 (replicas) | 122,900 | 0 | 122,900 | H200 (revised 1.40× for OpenCL) |
| Alpha-M | Contingency (20%) | 34,050 | 0 | 34,050 | H200 (revised 1.50×) |
| Gamma | All phases | 2,000 | ~107 | ~1,893 | Any |
| Delta | All phases | 20,000 | ~0.5 | ~19,999 | RTX 5000 Ada |
| **Total** | | **~229,650** | **~112.5** | **~229,537** | (revised 2026-04-17; see `shared/notes/1.1-mace-phase2-feasibility.md`) |

## SU Rate Reference

| GPU | SU/hr | Relative Cost |
|-----|-------|--------------|
| RTX 5000 Ada | 15 | 1x (baseline) |
| RTX Pro 6000 Blackwell | 65 | 4.3x |
| A100 | 100 | 6.7x |
| H200 | 300 | 20x |
| B200 | 370 | 24.7x |

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
| **Used** | **~107** | |
| **Remaining** | **~1,893** | For batch 2 (~100 proteins) + analysis |

Batch 2 estimate: ~100 proteins at ~2.3 GPU-hrs/protein (using pass rate data for
oversampling) = ~230 GPU-hrs. Budget is sufficient with ~1,600 GPU-hrs margin.

---

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
- **SPG1-class proteins:** Proteins with <15% pass rate need `--mem=40G` for XTC assembly
  (>10K NPZ files require ~22 GB RAM).
- **RTX 5000 Ada is the default GPU** for all BioEmu and Delta workloads. H200/B200 only
  when justified by memory or queue requirements.
