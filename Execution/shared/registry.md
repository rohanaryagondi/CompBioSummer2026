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
| (none yet -- created when PlannerAI plans subphases) | | | | |

## SubAgents

| Agent | Task ID | Subphase | Track | Location | Status |
|-------|---------|----------|-------|----------|--------|
| (none yet -- created when PlannerAI plans subphases) | | | | | |

---

## Notes

- PlannerAI updates this registry whenever it creates new HeadAIs or SubAgents
- AdminAI verifies this registry matches actual files on disk
- Status values: `active` | `complete` | `failed` | `blocked`
