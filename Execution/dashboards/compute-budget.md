---
last_updated: 2026-04-16T18:00:00Z
updated_by: PlannerAI
---

# Compute Budget Tracker

## Budget Overview (from Implementation Plan Section 9.1)

| Track | Phase | Allocated GPU-hrs | Used GPU-hrs | Remaining | GPU Type |
|-------|-------|-------------------|-------------|-----------|----------|
| Alpha-M | Phase 0 | <2 | 0.5 | — | Any |
| Alpha-M | Phase 1 (pilot) | 3,000 | 0 | 3,000 | H200 |
| Alpha-M | Phase 2 (production) | 33,800 | 0 | 33,800 | H200 / any |
| Alpha-M | Phase 3 (replicas) | 87,792 | 0 | 87,792 | H200 / any |
| Alpha-M | Contingency (20%) | 22,800 | 0 | 22,800 | H200 |
| Gamma | All phases | 2,000 | 0 | 2,000 | Any |
| Delta | All phases | 20,000 | 0 | 20,000 | RTX 5090 |
| **Total** | | **~169,392** | **0.5** | **~169,392** | |

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

| Period | GPU-hrs Used | Cumulative | Budget Remaining | Notes |
|--------|-------------|-----------|-----------------|-------|
| Phase 0 (Apr 15-16) | 0.5 | 0.5 | ~169,392 | BioEmu SS test only |
| Sub 1.1 (est.) | ~26-65 | ~27-66 | ~169,326 | MLFF + BioEmu + Delta tests |

---

## Alerts

- None. Budget is barely touched. Phase 1 pilot is within expected range.
