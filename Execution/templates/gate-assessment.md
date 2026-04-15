---
gate_id: "D<N>"
date: <ISO date>
decision: GO | NO-GO | CONDITIONAL
assessed_by: PlannerAI
---

# Gate Assessment: D<N> -- <Decision Name>

## Gate Definition

**Date:** <scheduled date>
**Decision:** <what is being decided>
**Source:** Implementation Plan Section 13, gate D<N>

---

## Evidence Summary

<Narrative summary of the evidence available for this gate decision.
Reference specific completion reports, experiment logs, and status reports.>

---

## Criteria Evaluation

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | <criterion from Implementation Plan> | MET / NOT MET / PARTIAL | <specific evidence with file paths> |
| 2 | <criterion> | MET / NOT MET / PARTIAL | <evidence> |
| 3 | <criterion> | MET / NOT MET / PARTIAL | <evidence> |

---

## Verdict

**Decision: <GO / NO-GO / CONDITIONAL>**

<Justification for the verdict. Reference specific criteria, data, and the
Implementation Plan's fallback strategy.>

### If GO
<What proceeds unchanged. Which subphases are unlocked.>

### If NO-GO
<What changes. Reference the specific fallback strategy from the Implementation
Plan (Section 11: Kill Criteria). List which subphases need replanning.>

### If CONDITIONAL
<What conditions must be met. What timeline for re-evaluation. What proceeds
in the meantime.>

---

## Downstream Impact

| Affected Item | Impact |
|--------------|--------|
| Phase plan | <how the phase plan changes> |
| Subphase N.M | <specific changes needed> |
| Compute budget | <budget implications> |
| Timeline | <schedule implications> |
| Publication strategy | <venue or scope changes> |

---

## Action Items

1. <Specific action for PlannerAI: e.g., "replan subphase 1.4 without MLFF tasks">
2. <Specific action for human: e.g., "confirm fallback venue with PI">
3. <Dashboard update: e.g., "update gate-tracker.md with D2: NO-GO">
