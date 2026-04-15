---
last_updated: 2026-04-15
updated_by: PlannerAI
---

# Compute Budget Tracker

## Budget Overview (from Implementation Plan Section 9.1)

| Track | Phase | Allocated GPU-hrs | Used GPU-hrs | Remaining | GPU Type |
|-------|-------|-------------------|-------------|-----------|----------|
| Alpha-M | Phase 1 (pilot) | 3,000 | 0 | 3,000 | H200 |
| Alpha-M | Phase 2 (production) | 33,800 | 0 | 33,800 | H200 / any |
| Alpha-M | Phase 3 (replicas) | 87,792 | 0 | 87,792 | H200 / any |
| Alpha-M | Contingency (20%) | 22,800 | 0 | 22,800 | H200 |
| Gamma | All phases | 2,000 | 0 | 2,000 | Any |
| Delta | All phases | 20,000 | 0 | 20,000 | RTX 5000 Ada |
| **Total** | | **~169,392** | **0** | **~169,392** | |

---

## Storage Budget (from Implementation Plan Section 9.2)

| Data | Allocated | Used | Location |
|------|-----------|------|----------|
| Alpha-M trajectories | 8 TB | 0 | HPC scratch |
| BioEmu/Boltz-2/AlphaFlow ensembles | 5 GB | 0 | HPC scratch |
| Tahoe-100M raw | 630 GB | 0 | HPC scratch |
| Tahoe-100M processed | 200 GB | 0 | HPC scratch |
| DL checkpoints | 100 GB | 0 | HPC scratch |
| Analysis output | 10 GB | 0 | HPC scratch |
| **Total** | **~9 TB** | **0** | |

---

## Burn Rate

No compute used yet. This section will be populated as subphases complete.

| Week | GPU-hrs Used | Cumulative | Budget Remaining | Projected Exhaustion |
|------|-------------|-----------|-----------------|---------------------|
| -- | -- | -- | -- | -- |

---

## Alerts

- None. Budget tracking begins when Phase 0 subphases start executing.
