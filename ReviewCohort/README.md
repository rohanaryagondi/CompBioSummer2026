# ReviewCohort -- Critical Evaluation & Implementation Planning

The **ReviewCohort** is the final cohort in the CompBioSummer2026 research discovery
pipeline. It critically evaluates the 3 execution-ready proposals produced by Cohort2
(Deep Divers) and produces the definitive implementation plan for summer 2026.

## Purpose

Cohort1 (Gap Scouts) identified gaps. Cohort2 (Deep Divers) developed proposals. The
ReviewCohort stress-tests those proposals through hostile mock peer review, verifies
technical claims, resolves unresolved disputes, and produces the final execution plan.

## Team

| Agent | Short Name | Role | Track |
|-------|-----------|------|-------|
| Protein Dynamics & Force Field Reviewer | dynrev | Mock NCS Reviewer 1: MD simulation, convergence, NMR | Senior |
| Computational Biology & ML Reviewer | biomlrev | Mock NCS Reviewer 2: ML novelty, baselines, ablation | Senior |
| Statistical Rigor Reviewer | statrev | Statistical audit: power, multiplicity, pre-registration | Senior |
| Technical Implementation Auditor | implrev | Feasibility: software, compute, timeline, failure modes | Senior |
| Research Strategy Director | stratrev | Competition, scope, titles, publication strategy | Maverick |

## Round Protocol

| Round | Goal | Output |
|-------|------|--------|
| 1: Independent Reviews | Each reviewer evaluates proposals independently | `output/reviews/` |
| 2: Deep Verification | Targeted research to verify/refute critical claims | `output/research/` |
| 3: Cross-Reviewer Deliberation | Reviewers engage with each other's critiques | `output/deliberations/` |
| 4: Final Implementation Plan | Orchestrator synthesizes into definitive plan | `output/roundtables/` |

## Trigger

Say **"run the review cohort"** to the orchestrator to begin.

## What It Reads

- All Cohort2 output: proposals, critiques, syntheses, final proposal set
- The joint integration critique (identifies the 5 key attack vectors)
- Mission briefing and department rules
- Cohort1 final gap ranking (for context)

## What It Produces

The **final implementation plan** -- the single document that tells the team exactly
what to do:

1. Go/no-go decision for each project
2. Combined vs separate paper decision
3. Final scope, protein set, method catalog
4. Title recommendations
5. Week-by-week execution timeline
6. Resource allocation (GPU-hours, storage, personnel)
7. Risk mitigation and kill criteria
8. Reviewer attack pre-emption strategies

## How to Run

```
# Start the ReviewCohort orchestrator
# Trigger: "run the review cohort"
```

The orchestrator reads all prior cohort output, launches 5 reviewers through
4 rounds, and produces the final implementation plan.
