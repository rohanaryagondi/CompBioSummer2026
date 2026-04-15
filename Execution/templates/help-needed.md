---
requesting_agent: "head-<N.M>"
subphase: "<N.M>"
date: <ISO date>
blocked_tasks: ["task-<NNN>", "task-<NNN>"]
urgency: low | medium | high | critical
---

# Help Needed: <Topic>

## Problem Description

<Exact description of what went wrong. Include error messages, log excerpts,
and the context in which the problem occurred.>

---

## What Was Tried

<All attempts to resolve the problem, in order. Include commands, approaches,
and why each did not work.>

1. **Attempt 1:** <what was tried>
   - **Result:** <what happened>
   - **Why it failed:** <diagnosis>

2. **Attempt 2:** <what was tried>
   - **Result:** <what happened>
   - **Why it failed:** <diagnosis>

---

## What Help Is Needed

<Specific ask. Be precise about what you need the PlannerAI or human operator
to do. Vague requests like "fix this" are not actionable.>

- <Specific request 1: e.g., "need PlannerAI to adjust the protein set in subphase 1.2 task specs">
- <Specific request 2: e.g., "need human to install CUDA 12.4 on compute nodes">

---

## Impact Assessment

| Item | Detail |
|------|--------|
| Blocked tasks | <task IDs that cannot proceed> |
| Timeline impact | <how many days/weeks this delays the subphase> |
| Gate at risk | <D1-D7 if any gate is threatened> |
| Workaround available | yes/no -- <if yes, describe the workaround and its limitations> |

---

## Resolution Log

<Updated by PlannerAI or human operator when the escalation is addressed.>

| Date | Action | By | Status |
|------|--------|----|--------|
| <date> | <what was done> | <PlannerAI/human> | resolved/ongoing |
