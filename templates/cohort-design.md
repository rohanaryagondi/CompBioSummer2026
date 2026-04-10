---
agent: Cohort Architect
date: <YYYY-MM-DD>
type: cohort-design
cohort_name: <e.g., "Cohort2" or "ReviewCohort">
based_on: <e.g., "Cohort1 gap reports and synthesis">
---

# Cohort Design: <Cohort Name> -- <Cohort Purpose>

## Design Rationale

### What the Previous Cohort Produced
<Summary of the key outputs from the preceding cohort that inform this design>

### What This Cohort Must Accomplish
<Clear goal: refine gaps into proposals? Critique and verify? Produce final plan?>

### Why These Agents Were Chosen
<Explain the expertise mapping: which gaps or tasks require which specialist knowledge>

---

## Agent Roster

| # | Agent Name | Short Name | Track | Expertise Focus | Assigned Gaps/Tasks |
|---|-----------|-----------|-------|----------------|-------------------|
| 1 | ... | ... | Senior/Maverick | ... | ... |
| 2 | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... |

### Diversity Analysis
<How does this roster ensure diversity of perspective? What biases are mitigated?>

---

## Round Protocol

### Round 1: <Title>
**Goal:** <...>
**Agents:** <all / subset>
**Input:** <what each agent reads>
**Output:** <file path pattern>
**Launch:** <parallel / sequential>

### Round 2: <Title>
**Goal:** <...>
**Agents:** <...>
**Input:** <...>
**Output:** <...>
**Launch:** <...>

### Round 3+: <Title>
<...>

---

## Agent Persona Specifications

### Agent 1: <Full Name>
**Short name:** <...>
**Track:** <Senior / Maverick>
**Perspective:** <1-2 sentences on their unique angle>

**Expertise:**
- <Domain 1>
- <Domain 2>
- <...>

**Skeptical of:**
- <...>

**Champions:**
- <...>

**Deep research mandate:**
- <Specific databases, journals, queries to explore>

### Agent 2: <Full Name>
<...>

---

## Orchestrator Configuration

### Trigger Phrase
<What the user says to start this cohort, e.g., "run the deep divers">

### Input Files
<Explicit list of files the orchestrator must read before launching agents>

### Output Structure
```
<Cohort>/output/
├── research/
├── proposals/     (or gaps/ for Cohort1-style)
├── critiques/
├── roundtables/
└── directives/
```

### Subagent Prompt Template
<The template the orchestrator uses to construct subagent prompts>

---

## Files to Create

| # | File Path | Description |
|---|-----------|-------------|
| 1 | `<Cohort>/agents/orchestrator/CLAUDE.md` | Orchestrator persona |
| 2 | `<Cohort>/agents/<agent-1>/CLAUDE.md` | Agent 1 persona |
| ... | ... | ... |

---

## Success Criteria

<How do we know this cohort succeeded? What should the output contain?>
