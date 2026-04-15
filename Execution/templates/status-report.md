---
task_id: "task-<NNN>"
agent: "<agent-name>"
subphase: "<N.M>"
status: complete | partial | failed | blocked
date: <ISO date>
---

# Status Report: Task <NNN> -- <Title>

## Summary

<2-3 sentences: what was accomplished and what the outcome was.>

---

## What Was Done

<Detailed description of work performed. Include specific commands run,
configurations used, and results observed.>

1. <Action 1 and its result>
2. <Action 2 and its result>
3. <Action 3 and its result>

---

## Artifacts Produced

| Artifact | Path | Description | Verified |
|----------|------|-------------|----------|
| <name> | <path> | <description> | yes/no |

---

## Success Criteria Evaluation

| # | Criterion | Met? | Evidence |
|---|-----------|------|----------|
| 1 | <criterion from task spec> | yes/no/partial | <evidence> |
| 2 | <criterion> | yes/no/partial | <evidence> |

---

## Unexpected Findings

<Anything discovered that was not expected. This is critical for cross-agent
communication. If findings affect other tracks, a cross-agent note should
also be written to shared/notes/.>

- <Finding 1 and its implications>
- <Finding 2>

---

## What the Next Agent Needs to Know

<If another agent needs to continue or build on this work, what do they need
to know? Include file paths, gotchas, workarounds, and context.>

---

## Resource Usage

| Resource | Estimated | Actual |
|----------|-----------|--------|
| GPU-hours | <estimate from task spec> | <actual> |
| Wall time | <estimate> | <actual> |
| Storage | <estimate> | <actual> |
| SLURM job IDs | N/A | <job IDs if applicable> |

---

## Issues and Blockers

<If status is `failed` or `blocked`, provide detailed information:>

- **Problem:** <exact description>
- **Error message:** <exact error text or log excerpt>
- **What was tried:** <attempts to resolve>
- **What help is needed:** <specific ask>
- **Impact:** <which downstream tasks are affected>
