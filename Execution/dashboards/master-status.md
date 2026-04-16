---
last_updated: 2026-04-16T15:15:00Z
updated_by: head-1.1
---

# Master Status: CompBioSummer2026 Execution

## Current State

| Item | Value |
|------|-------|
| Current phase | Phase 1: Pilot Studies and Setup |
| Current subphase | 1.1: MLFF Software Validation & Early Setup |
| Subphase status | **NEAR-COMPLETE** (BioEmu generation finishing, all other tasks done) |
| Next action | Wait for BioEmu retry jobs (~4-5h), then plan subphase 1.2 |

---

## Decision Log

| Decision | Resolution | Date | Impact |
|----------|-----------|------|--------|
| BPTI benchmark drop | **DROP.** AK3 triggered at all cutoffs (56.1-72.4%) | 2026-04-16 | 14 -> 13 proteins. T5 still met. |
| HEWL benchmark drop | **DROP.** SG-SG integrity 40.2% (AK3 triggered at ALL cutoffs) | 2026-04-16 | 13 -> 12 proteins. T5 at boundary. |
| Phase 1 start date | **IMMEDIATE** (April 17). Extra buffer before D1. | 2026-04-16 | 3 weeks before D1 instead of 1 |
| D1 MLFF gate | **BOTH PASS.** MACE + SO3LR stable NVT on crambin | 2026-04-16 | Both MLFFs viable for pilots |

---

## Per-Track Status

| Track | Status | Latest Milestone | Next Milestone |
|-------|--------|-----------------|----------------|
| Alpha-M | D1 evidence collected | MACE D1 PASS, SO3LR D1 PASS, HEWL DROP | MLFF pilot on Tier 1 proteins |
| Gamma | BioEmu generating | 28/47 proteins usable, 19 running/retrying | Batch 1 completion, feature extraction |
| Delta | 3/5 methods installed | GEARS + scGPT + CPA verified on Tahoe | scFoundation + Tahoe-x1 setup |
| Combined | HEWL dropped, 12 proteins | T3 resolved (DROP), T5 at boundary | Depends on Alpha-M + Gamma progress |

---

## Timeline: Planned vs Actual

| Phase | Planned Start | Planned End | Actual Start | Actual End | Status |
|-------|-------------|------------|-------------|------------|--------|
| Phase 0 | Apr 15 | Apr 30 | Apr 15 | Apr 16 | **Complete** |
| Phase 1 | Apr 17 | Jun 30 | Apr 16 | — | **In progress (sub 1.1 near-complete)** |
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
