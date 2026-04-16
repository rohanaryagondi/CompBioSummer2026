---
last_updated: 2026-04-16
---

# Agent Registry

## System Agents

| Agent | Type | Location | Status |
|-------|------|----------|--------|
| PlannerAI | Orchestrator | `Execution/CLAUDE.md` | Active |
| AdminAI | Auditor | `Execution/agents/admin/CLAUDE.md` | Active |

## HeadAIs

| Agent | Subphase | Tracks | Location | Status |
|-------|----------|--------|----------|--------|
| head-0.1 | 0.1 | Alpha-M, Delta, Infrastructure | `Execution/phases/phase-0/subphase-0.1/CLAUDE.md` | Complete |
| head-1.1 | 1.1 | Alpha-M, Gamma, Delta | `Execution/phases/phase-1/subphase-1.1/CLAUDE.md` | Active |

## SubAgents

| Agent | Task ID | Subphase | Track | Location | Status |
|-------|---------|----------|-------|----------|--------|
| env-builder | task-001 | 0.1 | Infrastructure | `Execution/phases/phase-0/subphase-0.1/agents/env-builder/CLAUDE.md` | Complete |
| tahoe-loader | task-002 | 0.1 | Delta | `Execution/phases/phase-0/subphase-0.1/agents/tahoe-loader/CLAUDE.md` | Complete |
| alpha-scout | task-003 | 0.1 | Alpha-M | `Execution/phases/phase-0/subphase-0.1/agents/alpha-scout/CLAUDE.md` | Complete |
| bioemu-test | task-004 | 0.1 | Alpha-M | `Execution/phases/phase-0/subphase-0.1/agents/bioemu-test/CLAUDE.md` | Complete |
| mace-pilot | task-001 | 1.1 | Alpha-M | `Execution/phases/phase-1/subphase-1.1/agents/mace-pilot/CLAUDE.md` | Active |
| so3lr-pilot | task-002 | 1.1 | Alpha-M | `Execution/phases/phase-1/subphase-1.1/agents/so3lr-pilot/CLAUDE.md` | Active |
| bioemu-gen | task-003 | 1.1 | Gamma | `Execution/phases/phase-1/subphase-1.1/agents/bioemu-gen/CLAUDE.md` | Active |
| delta-setup | task-004 | 1.1 | Delta | `Execution/phases/phase-1/subphase-1.1/agents/delta-setup/CLAUDE.md` | Active |
| sc-recon | task-005 | 1.1 | Alpha-M | `Execution/phases/phase-1/subphase-1.1/agents/sc-recon/CLAUDE.md` | Active |

---

## Notes

- PlannerAI updates this registry whenever it creates new HeadAIs or SubAgents
- AdminAI verifies this registry matches actual files on disk
- Status values: `active` | `complete` | `failed` | `blocked`
- Phase 0 agents marked complete (subphase 0.1 finished 2026-04-16)
