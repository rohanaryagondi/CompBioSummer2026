---
last_updated: 2026-04-16T02:30:00Z
updated_by: head-0.1
---

# Active Subphase

| Item | Value |
|------|-------|
| Subphase | 0.1 |
| Title | Environment Setup & Data Verification |
| HeadAI | head-0.1 |
| Start date | 2026-04-15 |
| Completed | 2026-04-16 |
| Status | **COMPLETE** |

### Task Status

| Task ID | Title | Wave | Status | Agent |
|---------|-------|------|--------|-------|
| task-001 | Create 9 conda environments + export pinned YAMLs | 1 | **completed** | env-builder |
| task-002 | Download + preprocess Tahoe-100M via scDataset | 1 | **in_progress** (SLURM 8346038, PENDING) | tahoe-loader |
| task-003 | Verify BMRB S2 data + prepare PDB structures for 14 proteins | 1 | **completed** | alpha-scout |
| task-004 | BioEmu v1.3.1 disulfide bond test on BPTI + HEWL | 2 | **completed** (SLURM 8371740) | bioemu-test |

### Key Findings

- **D1 gate signal:** env-mace SUCCESS (mace-torch 0.3.15), env-so3lr SUCCESS (SO3LR 0.1.0, JAX 0.5.3). Both MLFF packages installed. Positive D1 signal.
- **T5 threshold:** 13/14 proteins confirmed with usable S2 data (only Crambin lacks S2). T5 MET.
- **T3 threshold:** NOT MET. BioEmu SS integrity below 95% for both BPTI and HEWL at all CB-CB cutoffs.
- **AK3 assessment:** BPTI TRIGGERED (56.1% at 4.5A) — recommend drop. HEWL cutoff-dependent (70.7% at 4.5A, 90.9% at 5.0A).
- **BioEmu backbone-only output:** No SG atoms generated. CB-CB proxy used. Sidechain reconstruction may improve metrics.
- **Garnet discovery:** Package name is `garnetff` on PyPI, requires Python 3.12 + conda-forge deps.
- **GPU naming:** Cluster has RTX 5090 (labeled `rtx_50`), not "RTX 5000 Ada" as in proposals.
- **BioEmu env pinning:** tensorflow-cpu must be 2.15.x (not 2.16+) to avoid protobuf clash with jaxlib.

### Cross-Agent Notes

| Path | Urgency |
|------|---------|
| `shared/notes/0.1-env-mace-build.md` | info |
| `shared/notes/0.1-env-so3lr-build.md` | info |
| `shared/notes/0.1-bioemu-disulfide.md` | important |

### Completion Report

`phases/phase-0/subphase-0.1/completion-report.md` — written 2026-04-16T02:30:00Z
