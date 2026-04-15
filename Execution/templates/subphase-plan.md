---
subphase: "<N.M>"
title: "<Subphase Title>"
phase: <N>
date_range: "<start date> to <end date>"
tracks: [alpha-m, gamma, delta]
status: planned | active | complete
created: <ISO date>
task_count: <number>
wave_count: <number>
---

# Subphase <N.M>: <Title>

## Overview

<3-5 sentences: what this subphase accomplishes, how it fits into the phase,
what the HeadAI needs to know to manage it effectively.>

---

## Task Summary

| Task ID | Name | Track | Wave | Dependencies | Effort | Status |
|---------|------|-------|------|-------------|--------|--------|
| task-001 | <name> | <track> | 1 | None | <hours/days> | planned |
| task-002 | <name> | <track> | 1 | None | <hours/days> | planned |
| task-003 | <name> | <track> | 1 | None | <hours/days> | planned |
| task-004 | <name> | <track> | 2 | task-001 | <hours/days> | planned |

---

## Wave Protocol

### Wave 1: <Name>

**Agents (parallel, max 3):** task-001, task-002, task-003
**Dependencies:** None (or: requires <X> from prior subphase)
**Completion criteria:** <What must be true before Wave 2 can start>

### Wave 2: <Name>

**Agents (parallel):** task-004, task-005
**Dependencies:** Wave 1 output -- specifically: <file paths>
**Completion criteria:** <What must be true for this wave to be complete>

---

## Dependency Diagram

```
Wave 1 (parallel):
  task-001 ──┐
  task-002 ──┼──> Wave 1 complete
  task-003 ──┘
                  │
                  v
Wave 2 (parallel):
  task-004 ──┐
  task-005 ──┴──> Wave 2 complete
                  │
                  v
           Subphase complete
```

---

## Cross-Subphase Dependencies

### What this subphase needs from prior subphases
- <Subphase X.Y>: <specific artifact or finding, with file path>

### What future subphases will need from this subphase
- <Description of output that downstream subphases depend on>

---

## Gate Checkpoints

<If a decision gate falls within or immediately after this subphase:>

| Gate | Date | This subphase produces evidence for |
|------|------|-------------------------------------|
| D<X> | <date> | <what evidence this subphase provides> |

---

## Success Criteria

This subphase succeeds ONLY if ALL of the following are true:

1. <Specific measurable criterion>
2. <Specific measurable criterion>
3. All task status reports written to `status/`
4. Completion report written to `completion-report.md`
5. Any cross-track findings written to `shared/notes/`
