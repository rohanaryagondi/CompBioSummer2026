---
author: prio_su_enforce.sh (auto-generated; recreated 2026-05-03 from audit trail)
date: 2026-05-02T22:58:45Z (event); 2026-05-03T20:30:00Z (recreated)
urgency: critical
affected_tracks: [alpha-m, infrastructure]
status: RESOLVED — cancelled job's work was resubmitted on Standard Tier `gpu` then moved to scavenge_gpu
note: "This file was reported as written by prio_su_enforce.sh on 2026-05-02 but doc-audit 2026-05-03 found it absent. Recreated from audit trail (master-status decision-log + scontrol records) for completeness."
---

# Auto-cancellation: priority SU projected over budget

The `prio_su_enforce.sh` script cancelled the following job because its
remaining walltime would push priority SU consumption past the cap.

## Budget state at cancellation

| Field | Value |
|-------|-------|
| Budget cap | 250 SU (just-reduced from 800 per user directive same session) |
| Used (terminated) | ~225.5 SU |
| In-flight projected (pre-cancel) | ~390 SU |
| Projected total (pre-cancel) | ~615 SU |
| Excess to remove | ~365 SU |

## Cancelled jobs

| JobID | Name | State | Walltime | Elapsed | Projected SU saved |
|-------|------|-------|----------|---------|---------------------|
| 10463305 | w8q4r3xz | RUNNING | 1-00:00:00 | 01:02:19 | ~344.42 |

This was the SO3LR WW gate (extended-walltime version submitted at 16:50Z 2026-05-02 after I cancelled the original 10458603 walltime-too-short gate per user "be thorough" directive). At dt=0.25 fs + float64 throughput ~0.95 ns/day on RTX 5000 Ada priority, 24 hr walltime × billing=15 = 360 SU max. Tracker projection determined this would push closure-window total past 250 SU cap.

## head-1.2 action taken

1. Resubmitted WW SO3LR rescue on Standard Tier `gpu` (free, billing=15 SU/hr but no priority cost), as job 10470003 with same tag `w8q4r3xz`.
2. Later (2026-05-03) moved 10470003 to `scavenge_gpu` (1/10 billing rate) when scavenge optimization pivot applied.
3. Current state: 10567507 (w8q4r3xz) on scavenge_gpu after 3 cancel/resubmit cycles for optimization rounds.

No silent compromise — WW SO3LR rescue work is preserved + on cheaper partition. Budget enforcement worked as designed.

## Cross-references

- `output/scripts/prio_su_enforce.sh` — the enforcement script
- `output/scripts/prio_su_budget.json` — cap=250 (was 800 pre-cancel)
- `dashboards/master-status.md` decision-log — "SU budget cap 800 → 250 SU" entry 2026-05-03
- `shared/notes/1.2-so3lr-rescue-results.md` — current WW rescue state
