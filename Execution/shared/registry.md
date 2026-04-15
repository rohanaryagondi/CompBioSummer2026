---
last_updated: 2026-04-15
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
| head-0.1 | 0.1 | Alpha-M, Delta, Infrastructure | `Execution/phases/phase-0/subphase-0.1/CLAUDE.md` | Active |

## SubAgents

| Agent | Task ID | Subphase | Track | Location | Status |
|-------|---------|----------|-------|----------|--------|
| env-builder | task-001 | 0.1 | Infrastructure | `Execution/phases/phase-0/subphase-0.1/agents/env-builder/CLAUDE.md` | Active |
| tahoe-loader | task-002 | 0.1 | Delta | `Execution/phases/phase-0/subphase-0.1/agents/tahoe-loader/CLAUDE.md` | Active |
| alpha-scout | task-003 | 0.1 | Alpha-M | `Execution/phases/phase-0/subphase-0.1/agents/alpha-scout/CLAUDE.md` | Active |
| bioemu-test | task-004 | 0.1 | Alpha-M | `Execution/phases/phase-0/subphase-0.1/agents/bioemu-test/CLAUDE.md` | Active |

---

## Notes

- PlannerAI updates this registry whenever it creates new HeadAIs or SubAgents
- AdminAI verifies this registry matches actual files on disk
- Status values: `active` | `complete` | `failed` | `blocked`
