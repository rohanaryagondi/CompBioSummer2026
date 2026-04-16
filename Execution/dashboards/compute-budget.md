---
last_updated: 2026-04-16T15:15:00Z
updated_by: head-1.1
---

# Compute Budget Tracker

## Budget Overview (from Implementation Plan Section 9.1)

| Track | Phase | Allocated GPU-hrs | Used GPU-hrs | Remaining | GPU Type |
|-------|-------|-------------------|-------------|-----------|----------|
| Alpha-M | Phase 0 | <2 | 0.5 | — | Any |
| Alpha-M | Phase 1 (pilot) | 3,000 | ~4.3 | ~2,996 | H200 |
| Alpha-M | Phase 2 (production) | 33,800 | 0 | 33,800 | H200 / any |
| Alpha-M | Phase 3 (replicas) | 87,792 | 0 | 87,792 | H200 / any |
| Alpha-M | Contingency (20%) | 22,800 | 0 | 22,800 | H200 |
| Gamma | All phases | 2,000 | ~15 | ~1,985 | Any |
| Delta | All phases | 20,000 | ~0.5 | ~19,999 | RTX 5000 Ada |
| **Total** | | **~169,392** | **~20** | **~169,372** | |

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

## Subphase 1.1 Compute Estimates

| Task | Track | Est. GPU-hrs | GPU Type | Notes |
|------|-------|-------------|----------|-------|
| task-001 MACE crambin NVT | Alpha-M | 5-20 | H200 | 1 ns NVT, staged approach |
| task-002 SO3LR crambin NVT | Alpha-M | 5-20 | H200 | 1 ns NVT, JAX JIT overhead |
| task-003 BioEmu 50 proteins | Gamma | 15-20 | H200/Any | ~20 min/protein x 50 |
| task-004 GEARS setup | Delta | 1-3 | RTX 5090 | OOM profiling may need multiple runs |
| task-005 HEWL sidechain recon | Alpha-M | 0 | CPU only | SCWRL4 is CPU |
| task-006 scGPT + CPA setup | Delta | 1-3 | RTX 5090 | Short test runs only |
| **Subphase 1.1 total** | | **~27-66** | | |

---

## Storage Budget (from Implementation Plan Section 9.2)

| Data | Allocated | Used | Location |
|------|-----------|------|----------|
| Alpha-M trajectories | 8 TB | 0 | HPC scratch |
| BioEmu/Boltz-2/AlphaFlow ensembles | 5 GB | ~500 MB | HPC scratch |
| Tahoe-100M raw | 630 GB | 428.89 GB | HPC scratch |
| Tahoe-100M processed | 200 GB | 0 | HPC scratch |
| DL checkpoints | 100 GB | 0 | HPC scratch |
| Analysis output | 10 GB | 0 | HPC scratch |
| **Total** | **~9 TB** | **~429 GB** | |

---

## Burn Rate

| Period | GPU-hrs Used | SU Consumed | Cumulative GPU-hrs | Notes |
|--------|-------------|-------------|-------------------|-------|
| Phase 0 (Apr 15-16) | 0.5 | ~8 | 0.5 | BioEmu SS test only |
| Sub 1.1 (Apr 16, ongoing) | ~20 | ~3,930 | ~20.5 | MLFF + BioEmu + Delta |

### Sub 1.1 SU Breakdown

| Task | GPU-hrs | GPU Type | SU |
|------|---------|----------|-----|
| MACE crambin NVT | ~2.5 | H200 | ~750 |
| SO3LR crambin NVT | ~1.8 | RTX 5000 Ada | ~27 |
| BioEmu batch (ongoing) | ~15 | Mixed gpu/H200 | ~3,000 |
| GEARS setup | ~0.5 | H200 | ~150 |
| scGPT+CPA test | ~0.01 | H200 | ~3 |

**Observation:** BioEmu on H200 consumed ~3000 SU for ~15 GPU-hrs. On RTX 5000 Ada
the same work would have been ~225 SU (13x cheaper). Future BioEmu batches should
use RTX 5000 Ada.

---

## SU Breakdown by Partition (Subphase 1.1)

| Partition | SU Consumed | % of Total |
|-----------|-------------|------------|
| gpu_h200 | 6,316 | 72.7% |
| gpu_b200 | 2,118 | 24.4% |
| gpu_devel | 205 | 2.4% |
| gpu | 49 | 0.6% |
| **Total** | **8,689** | **100%** |

All jobs used Standard Tier (`pi_mg269`). No Priority Tier usage to date.

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

**Example:** `sbatch -A prio_gerstein -p priority_gpu --gres=gpu:rtx_5000_ada:1 script.sbatch`

### Money Spent

| Tier | SU Consumed | Cost |
|------|-------------|------|
| Standard (pi_mg269) | 8,689 | $0.00 (free) |
| Priority (prio_gerstein) | 0 | $0.00 |
| **Total** | **8,689** | **$0.00** |

---

## Alerts

- **SU efficiency:** BioEmu batch 1 used H200 extensively due to gpu queue congestion.
  Future batches should prefer RTX 5000 Ada (15 vs 300 SU/hr). Budget in GPU-hours
  is fine; SU consumption is the concern for fairshare priority.
