---
last_updated: 2026-04-18T21:30:00Z
updated_by: planner
---

# Active Subphase

| Item | Value |
|------|-------|
| Subphase | 1.2 |
| Title | MLFF Stability Pilots, BioEmu Batch 2, Delta Baselines, OSF Pre-Registration |
| HeadAI | head-1.2 |
| Start date | 2026-04-19 (target) |
| Target end | 2026-05-16 |
| **Hard deadline** | **OSF deposit 2026-05-15** |
| Status | **PLANNED, ready for HeadAI launch** |

### Task Status

| Task ID | Title | Wave | Status | Agent |
|---------|-------|------|--------|-------|
| task-001 | MACE-OFF24 NPT 5 ns × 3 Tier B (WW, GB3, ubiquitin) on H200 OpenCL hybrid | 1 | planned | mlff-mace-pilot |
| task-002 | SO3LR vacuum NVT 5 ns × 5 Tier A/B (WW, GB3, GB1, NTL9, ubiquitin) on RTX 5000 Ada | 1 | planned | mlff-so3lr-pilot |
| task-003 | OSF pre-registration drafting + lock | 1 | planned | osf-prereg |
| task-004 | BioEmu batch 2 (~100 ProteinGym proteins) with disorder pre-screen + oversampling | 2 | planned | bioemu-batch2 |
| task-005 | Delta 5 baselines + WMSE evaluation harness | 2 | planned | delta-baselines |
| task-006 | Statistical pipeline core (Friedman/Nemenyi, ICC, bootstrap, JZS BF, T_min) | 2 | planned | stats-pipeline |

### Wave Protocol Summary

**Wave 1 (parallel, 3 agents):** task-001 + task-002 + task-003. Launch immediately.
**Partial-completion trigger for Wave 2:** ALL THREE of:
1. task-001 SLURM jobs *submitted* (multi-day run; do NOT wait for completion)
2. task-002 SLURM jobs *submitted*
3. task-003 `osf-prereg-v1.md` ≥80% complete

**Wave 2 (parallel, 3 agents):** task-004 + task-005 + task-006. Independent of Wave 1 results.

### Compute Budget (Sub 1.2 estimate)

| Task | GPU-hrs | GPU type | Est. SU |
|------|--------:|----------|--------:|
| task-001 MACE NPT (3 × 5 ns) | 420 | H200 (gpu_h200) | ~125,000 |
| task-002 SO3LR vacuum (5 × 5 ns) | 3 | RTX 5000 Ada | ~50 |
| task-003 OSF pre-reg | 0 | (none) | 0 |
| task-004 BioEmu batch 2 | 250 | RTX 5000 Ada | ~3,750 |
| task-005 Delta baselines | 30 | RTX 5000 Ada | ~450 |
| task-006 Stats pipeline | <1 | CPU | <30 |
| **Total** | **~705** | | **~129,300** |

### Gate Evidence Sub 1.2 Will Produce

| Gate | Date | Evidence |
|------|------|----------|
| D2 (June 30) | preliminary | 5-ns MACE NPT on 3 Tier B + 5-ns SO3LR vacuum on 5 Tier A/B = preliminary G1 path validation. D2 G1 formal evidence (≥10 ns × ≥3 Tier B) is Sub 1.4 scope. |
| D3 (June 6) | retiring | task-005 baselines complete fully retires the last D3 outstanding criterion. D3 will be ASSESSED: GO with all 5/5 + baselines after Sub 1.2. |

### Cross-Agent Notes Expected from Sub 1.2

| Note | Tracks | Urgency |
|------|--------|---------|
| `1.2-mace-npt-stability.md` | alpha-m | important |
| `1.2-so3lr-pilot-stability.md` | alpha-m | info |
| `1.2-osf-deposited.md` | alpha-m, gamma, delta, combined | **critical** (locks analysis plan) |
| `1.2-bioemu-batch2-passrates.md` | gamma | important |
| `1.2-delta-baselines-results.md` | delta, combined | important |
| `1.2-stats-pipeline-validation.md` | alpha-m, gamma, delta, combined | important |

### Resolved User Decisions (2026-04-18)

1. **MACE NPT scope: 3 proteins × 5 ns** (highest scope option). Within Phase 1 Alpha-M budget (3,000 GPU-hrs).
2. **OSF deposit: split.** osf-prereg drafts; user deposits; user provides DOI back.
3. **stats-pipeline: Standard Tier only.** No Priority Tier escalation.
