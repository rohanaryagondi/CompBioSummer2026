---
agent: orch
round: 3
date: 2026-04-14
type: directive
---

# Round 3 Directives: Cross-Review and Integration

## Purpose

Each proposal undergoes review by 2-3 agents with different expertise. Reviewers
challenge, strengthen, and refine proposals. The orchestrator then produces the final
integrated proposal set.

## Cross-Review Assignments

### Wave 1 (Parallel)
1. **bioval** reviews Alpha-M (mlffeng) -- data quality perspective
2. **mlffeng** reviews Gamma (ensfunc) -- ensemble quality perspective
3. **evalstat** reviews Delta (pertbio) -- methodology perspective

### Wave 2 (Parallel)
4. **evalstat** reviews Alpha-M (mlffeng) -- methodology perspective
5. **scopeadv** reviews Gamma (ensfunc) -- strategy perspective
6. **scopeadv** reviews Delta (pertbio) -- strategy perspective

### Wave 3 (Parallel)
7. **scopeadv** reviews Alpha-M (mlffeng) -- strategy perspective
8. **ensfunc** reviews Delta (pertbio) -- cross-domain perspective
9. **Joint integration critique** (mlffeng + bioval + ensfunc) -- combined paper

## Critique Template

Use the critique template from `../../templates/critique.md`. Key sections:
- Overall assessment (Strong Support / Support with Modifications / Concerns / Oppose)
- Strengths (3-5 with evidence)
- Weaknesses (3-5 with severity: Critical/Major/Minor and addressability)
- Feasibility assessment (technical, scientific, timeline)
- Suggested modifications (specific, actionable)
- Impact on publication narrative

## Instructions for Reviewers

- Read the proposal you are reviewing AND the relevant Round 1 research note
- Bring YOUR unique perspective -- the value is in cross-domain critique
- Be specific: "This section is weak" is unhelpful; "The S2 convergence protocol
  needs 15 replicas not 10 because Smith et al. showed..." is helpful
- Suggest modifications that strengthen the proposal, not just point out problems
- Address feasibility honestly: can this actually be done in the stated timeline?
- Consider the combined narrative: does this proposal strengthen or complicate
  the overall publication strategy?
