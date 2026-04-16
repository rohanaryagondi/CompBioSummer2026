---
subphase: "1.1"
title: "MLFF Software Validation & Early Setup"
phase: 1
date_range: "2026-04-17 to 2026-05-02"
tracks: [alpha-m, gamma, delta]
status: planned
created: 2026-04-16
task_count: 5
wave_count: 2
---

# Subphase 1.1: MLFF Software Validation & Early Setup

## Overview

This subphase establishes the simulation and analysis infrastructure for all three
project tracks. The primary deliverable is D1 gate evidence: MACE-OFF24 and SO3LR
each running 1 ns NVT on crambin. Simultaneously, Gamma starts BioEmu batch
generation for 50 ProteinGym proteins, Delta begins setting up the first 3 Tier 1
methods on Tahoe-100M, and a sidechain reconstruction test resolves the HEWL
disulfide integrity question from Phase 0. Phase 0 completed 14 days ahead of
schedule, giving this subphase 3 weeks before D1 (May 9) instead of the originally
planned 1 week.

---

## Task Summary

| Task ID | Name | Track | Wave | Dependencies | Effort | Status |
|---------|------|-------|------|-------------|--------|--------|
| task-001 | MACE-OFF24 crambin 1 ns NVT | Alpha-M | 1 | None | 3-5 days | planned |
| task-002 | SO3LR crambin 1 ns NVT | Alpha-M | 1 | None | 3-5 days | planned |
| task-003 | BioEmu batch generation (50 proteins) | Gamma | 1 | None | 5-8 days | planned |
| task-004 | Delta method setup (GEARS, scGPT, CPA) | Delta | 2 | None (wave ordering only) | 3-5 days | planned |
| task-005 | Sidechain reconstruction test (HEWL) | Alpha-M | 2 | None (wave ordering only) | 1-2 days | planned |

---

## Wave Protocol

### Wave 1: MLFF Validation + Gamma Start

**Agents (parallel, 3):** task-001 (mace-pilot), task-002 (so3lr-pilot), task-003 (bioemu-gen)
**Dependencies:** None — all environments and input data ready from Phase 0.
**Completion criteria:** task-001 AND task-002 both report completion (pass or fail).
task-003 may still be running when Wave 2 launches.

**Partial completion trigger for Wave 2:** Launch Wave 2 as soon as BOTH task-001
AND task-002 complete (or report failure). Do NOT wait for task-003 (BioEmu
generation), which is a multi-day GPU task that runs independently.

### Wave 2: Delta Setup + HEWL Resolution

**Agents (parallel, 2):** task-004 (delta-setup), task-005 (sc-recon)
**Dependencies:** Neither task depends on Wave 1 output. They are in Wave 2 purely
for the 3-agent concurrency limit (token cost control).
**Completion criteria:** All Wave 2 tasks complete. Then wait for any remaining
Wave 1 tasks (task-003 BioEmu generation if still running).

---

## Dependency Diagram

```
Wave 1 (parallel, 3 agents):
  task-001 (mace-pilot) ────┐
  task-002 (so3lr-pilot) ───┼──> [partial trigger: both MLFF tasks done]
  task-003 (bioemu-gen) ────┘    task-003 may still be running
                                 │
                                 v
Wave 2 (parallel, 2 agents):
  task-004 (delta-setup) ───┐
  task-005 (sc-recon) ──────┴──> Wave 2 complete
                                 │
                     [wait for task-003 if still running]
                                 │
                                 v
                      Subphase 1.1 complete
```

---

## Cross-Subphase Dependencies

### What this subphase needs from prior subphases
- **Subphase 0.1:** 9 conda environments with pinned YAMLs (`phases/phase-0/subphase-0.1/envs/`)
- **Subphase 0.1:** 14 PDB files + manifest (`phases/phase-0/subphase-0.1/proteins/`)
- **Subphase 0.1:** BMRB S2 verification table (13/14 confirmed, `phases/phase-0/subphase-0.1/output/`)
- **Subphase 0.1:** 100 HEWL backbone conformations (`phases/phase-0/subphase-0.1/output/task-004-hewl/`)
- **Subphase 0.1:** BioEmu API findings (correct API: `bioemu.sample.main`, no `BioEmuSampler` class)
- **Subphase 0.1:** HPC access details (RTX 5090 = `rtx_50` GRES, QOS max 2 pending, scratch path)

### What future subphases will need from this subphase
- **Subphase 1.2:** D1 gate evidence (MACE + SO3LR crambin results) for formal D1 assessment
- **Subphase 1.2:** BioEmu generation patterns and timing data for batch 2 planning
- **Subphase 1.2:** Delta method install documentation for scFoundation and Tahoe-x1 setup
- **Subphase 1.2:** HEWL keep/drop decision for updated protein set
- **Subphase 1.3+:** Gamma protein selection table for feature extraction planning
- **Subphase 1.4:** MLFF simulation protocols established here guide pilot production

---

## Gate Checkpoints

| Gate | Date | This subphase produces evidence for |
|------|------|-------------------------------------|
| D1 | May 9 | PRIMARY: MACE + SO3LR crambin NVT results. D1 criteria: "installs and runs 1 ns NVT on crambin." |
| D3 | June 6 | EARLY SIGNAL: 3 of 5 Delta Tier 1 methods installed (GEARS, scGPT, CPA). |
| D6 | Aug 31 | PARTIAL: Updated T3 assessment with real SG-SG distances from sidechain reconstruction. |

---

## Success Criteria

This subphase succeeds ONLY if ALL of the following are true:

1. MACE-OFF24 crambin NVT test completed with pass/fail documented and specific metrics
2. SO3LR crambin NVT test completed with pass/fail documented and specific metrics
3. D1 gate evidence report written (both MLFFs assessed against D1 criteria)
4. >=45 of 50 BioEmu protein ensembles generated with 2,000 conformations each
5. >=2 of 3 Delta methods (GEARS, scGPT, CPA) installed, verified with Tahoe-100M test
6. HEWL SG-SG integrity measured via sidechain reconstruction; keep/drop recommendation documented
7. Cross-agent notes written for D1-relevant findings and HEWL SG-SG results
8. All 5 task status reports written to `status/`
9. Completion report written to `completion-report.md`
10. Any cross-track findings written to `shared/notes/`
