---
phase: <N>
title: "<Phase Title>"
date_range: "<start date> to <end date>"
tracks: [alpha-m, gamma, delta]  # which tracks this phase covers
status: planned | active | complete
created: <ISO date>
---

# Phase <N>: <Title>

## Executive Summary

<3-5 sentences: what this phase accomplishes, why it matters, what must be true
for the phase to be considered complete.>

---

## Subphase Breakdown

| Subphase | Title | Date Range | Tracks | Tasks | Key Deliverable |
|----------|-------|------------|--------|-------|-----------------|
| N.1 | <title> | <dates> | <tracks> | <count> | <deliverable> |
| N.2 | <title> | <dates> | <tracks> | <count> | <deliverable> |

---

## Resource Allocation

### Compute

| Track | GPU-Hours (this phase) | GPU Type | Notes |
|-------|----------------------|----------|-------|
| Alpha-M | <hours> | H200 | <notes> |
| Gamma | <hours> | Any | <notes> |
| Delta | <hours> | RTX 5000 Ada | <notes> |

### Storage

| Data | Size | Location |
|------|------|----------|
| <dataset/artifact> | <size> | <HPC path> |

---

## Decision Gates in This Phase

| Gate | Date | Decision | Criteria | If NO-GO |
|------|------|----------|----------|----------|
| D<X> | <date> | <decision> | <criteria summary> | <fallback> |

---

## Dependencies

### From Prior Phases
- <What this phase needs from prior phases, with specific file paths>

### For Future Phases
- <What future phases will need from this phase>

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| <risk> | <low/med/high> | <description> | <mitigation strategy> |

---

## Success Criteria

This phase is complete when ALL of the following are true:

1. <Specific measurable criterion>
2. <Specific measurable criterion>
3. All subphase completion reports written
4. All relevant gates assessed
5. Dashboards updated
