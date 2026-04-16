---
last_updated: 2026-04-16T18:00:00Z
updated_by: PlannerAI
---

# Active Subphase

| Item | Value |
|------|-------|
| Subphase | 1.1 |
| Title | MLFF Software Validation & Early Setup |
| HeadAI | head-1.1 |
| Start date | 2026-04-17 |
| Target end | 2026-05-02 |
| Status | **PLANNED** (awaiting HeadAI launch) |

### Task Status

| Task ID | Title | Wave | Status | Agent |
|---------|-------|------|--------|-------|
| task-001 | MACE-OFF24 crambin 1 ns NVT | 1 | planned | mace-pilot |
| task-002 | SO3LR crambin 1 ns NVT | 1 | planned | so3lr-pilot |
| task-003 | BioEmu batch generation (50 proteins) | 1 | planned | bioemu-gen |
| task-004 | GEARS setup on Tahoe-100M | 2 | planned | gears-setup |
| task-005 | Sidechain reconstruction test (HEWL) | 2 | planned | sc-recon |
| task-006 | scGPT and CPA setup on Tahoe-100M | 2 | planned | scgpt-cpa-setup |

### Key Dependencies

- Wave 2 starts when task-001 AND task-002 complete (partial trigger; task-003 may still run)
- None of the Wave 2 tasks depend on Wave 1 output (wave ordering for concurrency only)

### Gate Evidence This Subphase Produces

| Gate | Evidence |
|------|----------|
| D1 (May 9) | MACE + SO3LR crambin NVT results (primary) |
| D3 (Jun 6) | Early: 3 of 5 Delta methods installed |
| D6 (Aug 31) | Updated T3: HEWL SG-SG integrity |
