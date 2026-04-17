---
last_updated: 2026-04-17T18:00:00Z
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
| Status | **COMPLETE** |

### Task Status

| Task ID | Title | Wave | Status | Agent |
|---------|-------|------|--------|-------|
| task-001 | MACE-OFF24 crambin 1 ns NVT | 1 | **COMPLETE (D1 PASS)** | mace-pilot |
| task-002 | SO3LR crambin 1 ns NVT | 1 | **COMPLETE (D1 PASS)** | so3lr-pilot |
| task-003 | BioEmu batch generation (50 proteins) | 1 | **COMPLETE** (46/47 proteins, 49/50 assays, YAP1 dropped) | bioemu-gen |
| task-004 | GEARS setup on Tahoe-100M | 2 | **COMPLETE** | gears-setup |
| task-005 | Sidechain reconstruction test (HEWL) | 2 | **COMPLETE (DROP)** | sc-recon |
| task-006 | scGPT and CPA setup on Tahoe-100M | 2 | **COMPLETE** | scgpt-cpa-setup |

### Key Results

- **D1 gate: BOTH PASS.** MACE stable 37+ ps (OpenCL fallback), SO3LR stable 1 ns.
- **HEWL: DROP.** SG-SG integrity 40.2%, AK3 triggered at all cutoffs. 12 proteins remain.
- **Delta: 3/3 methods working.** GEARS, scGPT, CPA all GPU-verified on Tahoe-100M.
- **BioEmu: 46/47 complete.** 112,351 physical conformations across 46 proteins. All >= 2,000.
  YAP1_HUMAN dropped (0.7% pass rate, IDP). Cross-agent note with pass rate analysis and
  batch 2 oversampling formula written.

### Gate Evidence Produced

| Gate | Evidence | Result |
|------|----------|--------|
| D1 (May 9) | MACE + SO3LR crambin NVT | **BOTH PASS** |
| D3 (Jun 6) | Delta methods installed | 3/5 already (GEARS, scGPT, CPA) |
| D6 (Aug 31) | HEWL SG-SG integrity | **DROP** (40.2%, benchmark → 12 proteins) |

### Cross-Agent Notes

| Note | Urgency | Summary |
|------|---------|---------|
| `1.1-mace-crambin.md` | important | D1 PASS + CUDA incompatibility on H200/B200 |
| `1.1-so3lr-crambin.md` | info | D1 PASS + use CLI not programmatic API |
| `1.1-hewl-sgsg.md` | important | DROP (40.2%), CB-CB proxy unreliable |
| `1.1-bioemu-passrates.md` | important | Pass rates by protein class, YAP1 drop, batch 2 oversampling formula |
