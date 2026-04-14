---
agent: orch
round: 2
date: 2026-04-14
type: roundtable-synthesis
---

# Round 2 Synthesis: Deep-Dive Results and Revised Rankings

## Overview

Seven specialists completed deep-dive research on the top 10 gaps from Round 1. Each
verified their gap against 2026 preprints, audited data/tool availability, estimated
compute requirements, assessed competition, and proposed publication framing.

Key outcomes: **Some gaps narrowed (reggeno, transmed), some strengthened (multisim,
sysnet, protdyn), and all confirmed feasibility within the summer 2026 timeline.**

---

## Revised Gap Rankings After Deep Dives

| Rank | Agent | Gap | R1 Score | R2 Score | Change | Key Finding |
|------|-------|-----|----------|----------|--------|-------------|
| 1 | multisim | MLFF Experimental Validation | 8.0 | **8.7** | +0.7 | 6 MLFFs ready; rich NMR/SAXS data; no competing benchmark; 180K GPU-hrs |
| 2 | sysnet | Perturbation Prediction Crisis | 8.0/8.4 | **8.6** | +0.2 | DL-vs-linear debate unresolved; Tahoe-100M public; 1-2K GPU-hrs; NatMeth target |
| 3 | protdyn | Dynamics-to-Function | 8.0 | **8.5** | +0.5 | BioEmu MIT-licensed, H200-ready; ProteinGym 2.7M variants; 8.2K GPU-hrs |
| 4 | aiml | FM Evaluation + UQ | 8.2/8.0 | **8.2** | 0 | GPT-5 drops 28% on uncontaminated data; no cross-modal benchmark exists |
| 5 | genchem | Molecular Design Evaluation | 8.2 | **8.2** | 0 | No full-pipeline benchmark; 20K GPU-hrs for initial pub; medium scoop risk |
| 6 | reggeno | Non-Coding Variant VEP | 8.4 | **7.8** | -0.6 | AlphaGenome partly narrows; integration still open; combined Beta scores 8.2 |
| 7 | transmed | Context-Dependent VUS | 8.4 | **7.8** | -0.6 | DYNA/DIVA/popEVE narrow fragments; full integration open; combined Beta 8.2 |

---

## Feasibility Verification Summary

### Confirmed Feasible (High Confidence)

**1. MLFF Biomolecular Benchmark (multisim, 8.7)**
- Tools: MACE-OFF23, SO3LR, AI2BMD, LiTEN-FF, ANI-2x all open-source
- Data: BMRB ~21,820 NMR entries; SASBDB 5,272 SAXS datasets; ~50-100 proteins with both
- Baselines: AMBER ff19SB (S2 R2=0.62), CHARMM36m (S2 R2=0.51) well-characterized
- Compute: 180K-270K GPU-hrs for 15 proteins x 3 MLFFs x 50ns (2-3 months on HPC)
- Competition: No group announced this; neutral benchmark is the differentiation

**2. Perturbation Prediction Benchmark (sysnet, 8.6)**
- Methods: GEARS, CPA, scGPT, X-Cell, SCALE, AlphaCell all available
- Data: Tahoe-100M (CC0, 429GB), X-Atlas (25.6M cells), Replogle, Norman all public
- Compute: 1,000-2,000 GPU-hrs (very modest)
- Key finding: Field is split -- Ahlmann-Eltze says DL fails, "Well-Calibrated Metrics"
  paper says it's a metric artifact. A definitive benchmark resolves this controversy.
- Competition: scPerturb team, CZI, but none building cross-context with proper controls

**3. Dynamics-to-Function (protdyn, 8.5)**
- BioEmu: MIT license, pip-installable, H200-compatible (141GB VRAM sufficient)
- Data: ProteinGym v1.3 = 2.7M DMS variants across 217 assays
- Compute: ~8,200 GPU-hrs (6 weeks on 8 H200s)
- Competition: Microsoft (BioEmu), Marks Lab (ProteinGym) closest but haven't published
  this combination. 6-18 month window estimated.

**4. LiveBioBench (aiml, 8.2)**
- Data sources all support temporal metadata: UniProt, PDB, ChEMBL, ClinVar, CELLxGENE
- Compute: 1,550-16,000 GPU-hrs/year depending on scope
- Key finding: GPT-5 accuracy drops 28.3 percentage points on uncontaminated data
- Competition: Entirely empty at the intersection of cross-modal + temporal + UQ-aware

**5. Molecular Design Benchmark (genchem, 8.2)**
- Data: ChEMBL 36 (2.8M compounds), BindingDB (3.15M), 30-50 targets with progression
- Compute: 20K GPU-hrs for initial publication; 85K for comprehensive
- Key finding: Pipeline attrition rates differ 10-100x across methods

### Partially Narrowed but Still Open

**6-7. Context-Aware VEP (reggeno 7.8 + transmed 7.8 → Combined 8.2)**
- AlphaGenome (Nature Jan 2026) improves eQTL AUROC to 0.80 but doesn't do integration
- DYNA/DIVA/popEVE each address fragments, not the full context-dependent picture
- All data available: GTEx v8, HPA v25, ClinVar 3M+ variants, gnomAD v4 730K exomes
- Compute: 500-1000 GPU-hrs (very modest)
- Strongest as combined coding + non-coding framework

---

## Combined Project Rankings (Revised)

### Tier 1: Strongest Candidates

**Project Gamma: Dynamics-to-Function Mapping (8.5)**
- Agent: protdyn
- Claim: First framework connecting conformational ensembles to biological function via
  BioEmu + ProteinGym DMS data
- Strengths: High novelty, tools all available, central post-AF question, clear Nature
  Comp Sci fit, feasible compute
- Risks: 6-18 month competition window; ensemble quality for non-globular proteins
- Compute: ~8,200 GPU-hrs

**Project Delta: PerturbMark -- Resolving the Perturbation Prediction Crisis (8.6)**
- Agent: sysnet
- Claim: Definitive cross-context benchmark resolving whether DL beats linear baselines
  for perturbation prediction
- Strengths: Resolves active Nature Methods controversy; massive new datasets (Tahoe-100M);
  very low compute; high feasibility
- Risks: Competitive space; benchmark alone may not reach Nature Comp Sci (Nature Methods
  more likely)
- Compute: 1,000-2,000 GPU-hrs

### Tier 1.5: Very Strong with Broader Scope

**Project Alpha-M: MLFF Biomolecular Crash Test (8.7)**
- Agent: multisim
- Claim: First systematic benchmark of ML force fields against experimental protein
  observables (NMR, SAXS, HDX-MS)
- Strengths: Highest revised score; rich data; no competition; guides entire MLFF community
- Risks: High compute requirement (180K+ GPU-hrs); 2-3 month execution
- Compute: 180,000-270,000 GPU-hrs

**Project Alpha-L: LiveBioBench (8.2)**
- Agent: aiml
- Claim: First cross-modal, temporally-gated, UQ-aware benchmark for biological FMs
- Strengths: Demonstrates 28% FM performance inflation; empty competitive space; annually
  renewable
- Risks: Broad scope needs scoping; maintaining infrastructure long-term
- Compute: 1,550-16,000 GPU-hrs/year

### Tier 2: Strong with Integration Needed

**Project Beta: ContextVEP -- Context-Aware Variant Effect Prediction (8.2)**
- Agents: reggeno + transmed
- Claim: First variant effect predictor accounting for tissue, disease, mechanism, and
  genetic background
- Strengths: Massive clinical need (1M+ VUS); all data public; clear AlphaMissense successor
- Risks: Complex integration; gap partially narrowed by recent tools
- Compute: 500-1,000 GPU-hrs

**Project Alpha-G: End-to-End Molecular Design Benchmark (8.2)**
- Agent: genchem
- Claim: First benchmark testing the full drug design pipeline (target→molecule→activity→
  ADMET→synthesis→retrospective validation)
- Strengths: Fundamental problem; pipeline attrition as metric is novel
- Risks: Massive curation effort; 30-50 targets need careful selection
- Compute: 20,000-85,000 GPU-hrs

---

## Key Insights from Round 2

1. **The benchmark/evaluation gaps are the most feasible.** Projects Delta (perturbation),
   Alpha-M (MLFF), and Alpha-L (LiveBioBench) all have: (a) public data, (b) open-source
   methods, (c) clear evaluation frameworks, (d) achievable compute.

2. **Dynamics-to-function is the most scientifically exciting.** Project Gamma addresses
   the central post-AlphaFold question and all tools are newly available (BioEmu 2024).
   But it has a narrower competition window.

3. **The variant prediction gaps narrowed.** Both reggeno and transmed saw their gaps
   partially filled by 2026 publications. The combined Project Beta is still strong but
   requires more differentiation from recent work.

4. **Compute ranges vary enormously.** From 1K GPU-hrs (PerturbMark) to 270K GPU-hrs
   (MLFF benchmark). All are feasible on the available HPC, but the lighter projects
   offer faster iteration.

5. **Nature Comp Sci vs Nature Methods targeting matters.** Benchmark papers may fit
   better in Nature Methods (established precedent), while novel frameworks (dynamics-to-
   function, ContextVEP) are more Nature Comp Sci.

---

## Recommendations for Round 3

Round 3 should produce the **final ranked gap list** considering:

1. Which projects are most achievable in summer 2026?
2. Which would make the strongest Nature Comp Sci paper?
3. Which have the safest competition window?
4. Which could combine into a single coherent submission?

Each specialist will rank all 7 projects on novelty, impact, feasibility, timeline, and
publication potential. The orchestrator will aggregate into a consensus ranking.
