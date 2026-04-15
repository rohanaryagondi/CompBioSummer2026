---
subphase: "0.1"
title: "Environment Setup & Data Verification"
phase: 0
date_range: "2026-04-15 to 2026-04-30"
tracks: [alpha-m, delta, infrastructure]
status: planned
created: 2026-04-15
task_count: 4
wave_count: 2
---

# Subphase 0.1: Environment Setup & Data Verification

## Overview

This is the only subphase in Phase 0. It establishes the computational foundation
for all three project tracks: creating 9 version-pinned conda environments, downloading
the 429 GB Tahoe-100M dataset, verifying BMRB NMR reference data and PDB structures
for the 14 Alpha-M benchmark proteins, and running the BioEmu disulfide bond integrity
test. Wave 1 launches three independent agents in parallel (environment builder, Tahoe
downloader, Alpha-M data scout). Wave 2 launches the BioEmu test agent once its
dependencies (env-bioemu and PDB files) are ready -- it does NOT wait for the full
Tahoe download or remaining environments to complete.

---

## Task Summary

| Task ID | Name | Track | Wave | Dependencies | Effort | Status |
|---------|------|-------|------|-------------|--------|--------|
| task-001 | Create 9 conda environments + export pinned YAMLs | Infrastructure | 1 | None | 2-3 days | planned |
| task-002 | Download + preprocess Tahoe-100M via scDataset | Delta | 1 | None | 3-5 days | planned |
| task-003 | Verify BMRB S2 data + prepare PDB structures for 14 proteins | Alpha-M | 1 | None | 1-2 days | planned |
| task-004 | BioEmu v1.3.1 disulfide bond test on BPTI + HEWL | Alpha-M | 2 | task-001 (env-bioemu), task-003 (PDB files) | 1-2 days | planned |

---

## Wave Protocol

### Wave 1: Foundation

**Agents (parallel, max 3):** task-001 (env-builder), task-002 (tahoe-loader), task-003 (alpha-scout)
**Dependencies:** None (first subphase of the project)
**Completion criteria:** All three tasks report status. Partial completion trigger:
Wave 2 may launch as soon as BOTH of these conditions are met:
1. env-bioemu from task-001 is built, smoke-tested, and YAML exported
2. task-003 is fully complete (BMRB table done, BPTI and HEWL PDB files prepared)

Note: task-001 may still be building remaining environments (env-mace, env-so3lr, etc.)
and task-002 may still be downloading Tahoe-100M when Wave 2 launches. This is expected.

### Wave 2: Validation

**Agents (parallel):** task-004 (bioemu-test)
**Dependencies:** Wave 1 partial output -- specifically:
- `env-bioemu` conda environment (from task-001, built first in priority order)
- BPTI PDB file with disulfide topology verified (from task-003)
- HEWL PDB file with disulfide topology verified (from task-003)
**Completion criteria:** BioEmu disulfide integrity metric computed for both BPTI
and HEWL, with clear assessment against T3 (>95%) and AK3 (<80%) thresholds.

---

## Dependency Diagram

```
Wave 1 (parallel):
  task-001 (env-builder) ──────┐
  task-002 (tahoe-loader) ─────┼──> Wave 1 complete
  task-003 (alpha-scout) ──────┘
                                │
        [partial trigger:       │
         env-bioemu ready       │
         + task-003 done]       │
                                v
Wave 2:
  task-004 (bioemu-test) ──────> Wave 2 complete
                                │
        [wait for task-001      │
         remaining envs +       │
         task-002 download]     │
                                v
                     Subphase 0.1 complete
```

---

## Cross-Subphase Dependencies

### What this subphase needs from prior subphases
- None (this is the first subphase in the project)

### What future subphases will need from this subphase
- **Phase 1 all tracks:** 9 conda environment YAML files (from task-001)
- **Phase 1 Delta:** Tahoe-100M data on HPC scratch + verified streaming loader (from task-002)
- **Phase 1 Alpha-M:** BMRB verification table, 14 PDB files, manifest.json (from task-003)
- **Phase 1 Alpha-M:** BioEmu SS integrity results for BPTI/HEWL (from task-004)
- **Phase 1 planning (PlannerAI):** Cross-agent notes on env-mace and env-so3lr build success/failure (D1 gate early warning)

---

## Gate Checkpoints

| Gate | Date | This subphase produces evidence for |
|------|------|-------------------------------------|
| D1 | May 9 | env-mace and env-so3lr build results (cross-agent notes) |
| D2 | June 30 | BioEmu SS integrity results feed into G5 (NMR reference data) and T3 (disulfide integrity) |
| D6 | Aug 31 | T3 (BioEmu disulfide >95%) and T5 (≥12 proteins with BMRB S2) are assessed here |

---

## Success Criteria

This subphase succeeds ONLY if ALL of the following are true:

1. All 9 conda environments created, smoke-tested, and exported as version-pinned YAML files
2. SLURM partition access verified with a test job submission
3. HPC scratch quota confirmed ≥10 TB available
4. Tahoe-100M dataset fully downloaded to HPC scratch (~630 GB)
5. scDataset streaming loader verified with 10K-cell test query returning correct schema
6. BMRB S2 verification table complete for all 14 proteins (accession IDs, field, temperature, coverage)
7. ≥12 of 14 proteins confirmed with usable S2 order parameter data (T5 threshold)
8. 14 PDB structure files downloaded and verified
9. Protein manifest file (manifest.json) created with complete metadata
10. 100 BioEmu conformations generated for BPTI; SS integrity metric computed
11. 100 BioEmu conformations generated for HEWL; SS integrity metric computed
12. Clear T3/AK3 threshold assessment documented for both proteins
13. Cross-agent notes written for env-mace and env-so3lr build results
14. All task status reports written to `status/`
15. Completion report written to `completion-report.md`
16. Any cross-track findings written to `shared/notes/`
