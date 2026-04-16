---
last_updated: 2026-04-16T18:00:00Z
updated_by: PlannerAI
---

# Master Status: CompBioSummer2026 Execution

## Current State

| Item | Value |
|------|-------|
| Current phase | Phase 1: Pilot Studies and Setup |
| Current subphase | 1.1: MLFF Software Validation & Early Setup |
| Subphase status | **PLANNED** (ready for HeadAI launch) |
| Next action | Human: cd into subphase-1.1 and launch HeadAI |

---

## Phase 0 Decision Log

| Decision | Resolution | Date | Impact |
|----------|-----------|------|--------|
| BPTI benchmark drop | **DROP.** AK3 triggered at all cutoffs (56.1-72.4%) | 2026-04-16 | 14 -> 13 proteins. T5 still met. |
| HEWL cutoff interpretation | **CONDITIONAL KEEP.** Sidechain reconstruction test in Sub 1.1 | 2026-04-16 | Final decision after SG-SG data |
| Phase 1 start date | **IMMEDIATE** (April 17). Extra buffer before D1. | 2026-04-16 | 3 weeks before D1 instead of 1 |

---

## Per-Track Status

| Track | Status | Latest Milestone | Next Milestone |
|-------|--------|-----------------|----------------|
| Alpha-M | Phase 1 ready | Envs built, BMRB verified, BioEmu tested | MACE + SO3LR crambin NVT (D1 gate May 9) |
| Gamma | Phase 1 ready | env-bioemu working, API characterized | BioEmu batch 1 (50 proteins) |
| Delta | Phase 1 ready | Tahoe-100M downloaded (428.89 GB) | GEARS + scGPT + CPA setup |
| Combined | Decision pending (Aug 31) | T3 NOT MET (CB-CB), T5 MET | Depends on Alpha-M + Gamma progress |

---

## Timeline: Planned vs Actual

| Phase | Planned Start | Planned End | Actual Start | Actual End | Status |
|-------|-------------|------------|-------------|------------|--------|
| Phase 0 | Apr 15 | Apr 30 | Apr 15 | Apr 16 | **Complete** |
| Phase 1 | Apr 17 | Jun 30 | — | — | **Ready to launch** |
| Phase 2 | Jul 1 | Aug 22 | — | — | Not started |
| Phase 3 | Aug 23 | Nov 30 | — | — | Not started |

---

## Active Blockers

None.

---

## Decisions Needed

None currently. BPTI/HEWL/start-date decisions resolved.

---

## Upcoming Milestones

| Date | Milestone | Gate |
|------|-----------|------|
| ~~Apr 30~~ | ~~Phase 0 complete~~ | — | **Done (Apr 16)** |
| May 2 | Subphase 1.1 complete (target) | — |
| May 9 | MLFF software GO | D1 |
| May 15 | OSF pre-registration | — |
| ~~May 31~~ | ~~Tahoe-100M download deadline~~ | ~~DK1~~ | **Done (Apr 16)** |
| Jun 6 | Delta scope lock | D3 |
| Jun 30 | MLFF pilot GO | D2 |
| Jul 31 | Integration signal | D4 |
| Aug 15 | Delta preprint | D5 |
| Aug 31 | Combined paper GO/NO-GO | D6 |
| Sep 15 | Phase 3 scope | D7 |
