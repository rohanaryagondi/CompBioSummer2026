---
task_id: "task-<NNN>"
original_agent: "<agent-name>"
subphase: "<N.M>"
date: <ISO date>
reason: <agent failure | context limit | task split | reassignment>
---

# Handoff: Task <NNN> -- <Title>

## What Was Done

<Summary of completed work. Reference the status report for details.>

1. <Completed step 1>
2. <Completed step 2>

---

## What Remains

<Explicitly list what the next agent must do to finish this task.>

1. <Remaining step 1>
2. <Remaining step 2>

---

## Critical File Paths

| File | Purpose | State |
|------|---------|-------|
| <path> | <what it is> | <complete / in-progress / not started> |

---

## Known Issues

<Problems the original agent encountered that the next agent should know about.>

- <Issue 1: description and workaround if any>
- <Issue 2>

---

## Environment State

<State of any environments, processes, or resources.>

| Item | State |
|------|-------|
| Conda env | <created / not created / broken> |
| SLURM jobs | <none running / job IDs still active> |
| Data files | <downloaded / partially downloaded / not started> |

---

## Context the Next Agent Needs

<Anything not captured above that would save the next agent from re-discovering.>
