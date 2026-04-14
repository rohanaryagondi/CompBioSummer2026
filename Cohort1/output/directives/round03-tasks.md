---
agent: orch
round: 3
date: 2026-04-14
type: directive
---

# Round 3 Directives: Final Gap Ranking

## Overview

Each specialist ranks ALL 7 combined projects from Round 2, considering the deep-dive
evidence. Rankings aggregate into the final consensus gap list for the CohortArchitect.

## The 7 Projects to Rank

1. **Gamma: Dynamics-to-Function** (protdyn, R2=8.5) -- BioEmu ensembles → DMS function prediction
2. **Delta: PerturbMark** (sysnet, R2=8.6) -- Definitive perturbation prediction benchmark
3. **Alpha-M: MLFF Biomolecular Crash Test** (multisim, R2=8.7) -- MLFFs vs experimental observables
4. **Alpha-L: LiveBioBench** (aiml, R2=8.2) -- Cross-modal temporally-gated FM benchmark
5. **Alpha-G: Molecular Design Benchmark** (genchem, R2=8.2) -- End-to-end drug design evaluation
6. **Beta: ContextVEP** (reggeno+transmed, R2=8.2) -- Context-dependent variant effect prediction

## Ranking Criteria

For each project, score 1-10 on:
- **Novelty**: How new is this idea? Has anyone done something similar?
- **Scientific impact**: How many researchers would this affect? Would it change thinking?
- **Computational feasibility**: Can this be done with available tools and data?
- **Timeline feasibility**: Can this produce a paper by end of summer 2026?
- **Publication potential**: Is this a Nature Comp Sci paper? Nature Methods? Lower?

Also provide:
- **Recommended venue** for each project
- **Top pick**: Which single project would you recommend?
- **Best combination**: Which 2 projects could combine into one paper?

## Output

Each specialist writes: `Cohort1/output/research/<shortname>-ranking-R03.md`
