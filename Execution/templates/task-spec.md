---
task_id: "task-<NNN>"
title: "<Task Title>"
subphase: "<N.M>"
track: <alpha-m | gamma | delta | infrastructure>
wave: <N>
agent: "<agent-name>"
effort: "<estimated hours or days>"
status: planned | in-progress | complete | blocked | failed
created: <ISO date>
---

# Task <NNN>: <Title>

## Objective

<One paragraph: what this task accomplishes and why it matters for the project.>

---

## Context

<Brief context: how this task fits into the subphase, what depends on it,
what it depends on. Reference specific sections of the Implementation Plan
or proposal documents if relevant.>

---

## Detailed Instructions

<Step-by-step technical procedure. Be specific enough that the SubAgent
can execute without guessing. Include:
- Exact commands or command patterns
- Configuration parameters
- Expected output formats
- File paths for inputs and outputs
- SLURM parameters if applicable (partition, GPU type, time limit)
- Conda environment to use>

1. <Step 1>
2. <Step 2>
3. <Step 3>

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| <path> | <what this file provides> |

### MAY READ (optional context)

| File | Why |
|------|-----|
| <path> | <what this file provides> |

### DO NOT READ

- <path or pattern> -- <reason: out of scope, different track, etc.>

---

## Output Artifacts

### Code and data artifacts

| Artifact | Path | Format |
|----------|------|--------|
| <name> | <path on HPC or in repo> | <format> |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-<NNN>-status.md` | `status-report.md` |
| Experiment log (if applicable) | `../../output/task-<NNN>-experiment.md` | `experiment-log.md` |
| Cross-agent note (if applicable) | `../../../../../../shared/notes/<subphase>-<topic>.md` | `cross-agent-note.md` |

---

## Success Criteria (Zero Compromise)

This task is complete ONLY if ALL of the following are true:

1. [ ] <Specific measurable criterion with exact metric or artifact>
2. [ ] <Specific measurable criterion>
3. [ ] <Specific measurable criterion>
4. [ ] Status report written to `../../status/task-<NNN>-status.md`

---

## Verification

Before declaring this task complete, verify:

1. <Specific check: e.g., "file exists at /path/to/output">
2. <Specific check: e.g., "SLURM job exited with code 0">
3. <Specific check: e.g., "output contains expected columns/fields">
4. <Specific check: e.g., "MD5 checksum matches expected value">

---

## Failure Protocol

If this task cannot be completed:

1. Write a status report with status `failed` or `blocked`
2. Document exactly what went wrong (error messages, log excerpts)
3. Document what was tried and why it did not work
4. Identify what help is needed for the HeadAI to resolve or escalate
5. DO NOT silently skip steps or lower the success criteria
