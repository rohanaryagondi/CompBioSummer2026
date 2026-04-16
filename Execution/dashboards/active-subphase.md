---
last_updated: 2026-04-16T15:15:00Z
updated_by: head-1.1
---

# Active Subphase

| Item | Value |
|------|-------|
| Subphase | 1.1 |
| Title | MLFF Software Validation & Early Setup |
| HeadAI | head-1.1 |
| Start date | 2026-04-16 |
| Target end | 2026-05-02 |
| Status | **NEAR-COMPLETE** (BioEmu generation finishing) |

### Task Status

| Task ID | Title | Wave | Status | Agent |
|---------|-------|------|--------|-------|
| task-001 | MACE-OFF24 crambin 1 ns NVT | 1 | **COMPLETE (D1 PASS)** | mace-pilot |
| task-002 | SO3LR crambin 1 ns NVT | 1 | **COMPLETE (D1 PASS)** | so3lr-pilot |
| task-003 | BioEmu batch generation (50 proteins) | 1 | **IN PROGRESS** (28/47 usable, 19 running/retrying) | bioemu-gen |
| task-004 | GEARS setup on Tahoe-100M | 2 | **COMPLETE** | gears-setup |
| task-005 | Sidechain reconstruction test (HEWL) | 2 | **COMPLETE (DROP)** | sc-recon |
| task-006 | scGPT and CPA setup on Tahoe-100M | 2 | **COMPLETE** | scgpt-cpa-setup |

### Key Results

- **D1 gate: BOTH PASS.** MACE stable 37+ ps (OpenCL fallback), SO3LR stable 1 ns.
- **HEWL: DROP.** SG-SG integrity 40.2%, AK3 triggered at all cutoffs. 12 proteins remain.
- **Delta: 3/3 methods working.** GEARS, scGPT, CPA all GPU-verified on Tahoe-100M.
- **BioEmu: 28/47 usable.** Race condition from multi-partition submission caused 14 failures. Retry submitted (job 8448809, H200 only, 4h limit). Est. 4-5h remaining.

### Gate Evidence Produced

| Gate | Evidence | Result |
|------|----------|--------|
| D1 (May 9) | MACE + SO3LR crambin NVT | **BOTH PASS** |
| D3 (Jun 6) | Delta methods installed | 3/5 already (GEARS, scGPT, CPA) |
| D6 (Aug 31) | HEWL SG-SG integrity | **DROP** (40.2%, benchmark → 12 proteins) |
