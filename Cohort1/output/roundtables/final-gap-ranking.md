---
agent: orch
round: 3
date: 2026-04-14
type: final-gap-ranking
---

# Final Gap Ranking: Cohort1 Gap Scouts

## Process Summary

- **Round 1**: 7 specialists identified 33 gaps across computational biology
- **Round 2**: Top 10 gaps underwent deep-dive research with feasibility verification
- **Round 3**: All 7 specialists ranked 6 combined projects on novelty, impact,
  feasibility, timeline, and publication potential
- **This document**: Aggregated consensus ranking for the CohortArchitect

---

## Consensus Rankings (Average Score Across 7 Specialists)

| Rank | Project | Avg Score | Top-Pick Votes | Venue Consensus |
|------|---------|-----------|---------------|-----------------|
| **1** | **Delta: PerturbMark** | **8.64** | 2 (protdyn, aiml) | Nature Methods / Nat Comp Sci |
| **2** | **Gamma: Dynamics-to-Function** | **8.30** | 1 (sysnet) | Nature Comp Sci |
| **3** | **Beta: ContextVEP** | **8.17** | 1 (transmed) | Nature Comp Sci / Nat Genetics |
| 4 | Alpha-L: LiveBioBench | 7.99 | 0 | Nature Comp Sci |
| 5 | Alpha-M: MLFF Crash Test | 7.74 | 3 (genchem, multisim, reggeno) | Nature Comp Sci |
| 6 | Alpha-G: Molecular Design Bench | 7.10 | 0 | J Chem Inf Model |

### Best Combination Votes
- **Alpha-M + Gamma**: 4 votes (protdyn, genchem, multisim, reggeno)
- Gamma + Beta: 1 vote (sysnet)
- Delta + Alpha-L: 1 vote (aiml)
- Beta + Delta: 1 vote (transmed)

---

## Individual Specialist Scores

| Project | protdyn | genchem | multisim | reggeno | sysnet | aiml | transmed | **Avg** |
|---------|---------|---------|----------|---------|--------|------|----------|---------|
| Delta | 9.0 | 8.2 | 8.0 | 8.8 | 8.4 | 8.8 | 9.3 | **8.64** |
| Gamma | 8.2 | 8.4 | 8.4 | 8.4 | 8.8 | 8.4 | 7.5 | **8.30** |
| Beta | 7.4 | 7.8 | 7.6 | 8.2 | 8.6 | 8.2 | 9.4 | **8.17** |
| Alpha-L | 8.2 | 7.8 | 7.6 | 8.2 | 7.6 | 8.4 | 8.1 | **7.99** |
| Alpha-M | 8.0 | 8.4 | 8.2 | 8.0 | 8.0 | 7.6 | 6.0 | **7.74** |
| Alpha-G | 6.8 | 7.8 | 6.6 | 6.6 | 6.6 | 7.0 | 8.3 | **7.10** |

### Score Variance Analysis

**Most polarizing project: Alpha-M (MLFF Crash Test)**
- Range: 6.0 (transmed) to 8.4 (genchem) = 2.4 point spread
- Structural/simulation experts love it; translational expert rates it last
- Reason: excellent science but distant from clinical impact, high compute risk

**Most consensus project: Gamma (Dynamics-to-Function)**
- Range: 7.5 (transmed) to 8.8 (sysnet) = 1.3 point spread
- Universally rated highly; never the absolute top pick but never below 7.5
- Reason: scientifically compelling with moderate, well-characterized risk

**Highest ceiling: Delta (PerturbMark)**
- Range: 8.0 (multisim) to 9.3 (transmed) = 1.3 point spread
- Wins on average score; consistent 8+ from every specialist
- Reason: resolves an active controversy, lowest compute, fastest to publish

---

## Top 3 Projects: Detailed Profiles

### #1: Delta -- PerturbMark: Resolving the Perturbation Prediction Crisis

**Consensus score: 8.64 | Venue: Nature Methods (primary), Nature Comp Sci (stretch)**

**The problem:** Deep learning methods for perturbation prediction (GEARS, CPA, scGPT,
X-Cell, AlphaCell) fail to beat simple linear baselines when properly evaluated
(Ahlmann-Eltze et al., Nature Methods 2025). The field is split: one camp says DL
fails, another says it's a metric artifact. Meanwhile, massive new datasets (Tahoe-100M
with 100M cells, CC0 license) remain unevaluated under rigorous conditions.

**The project:** Build PerturbMark, a definitive cross-context perturbation prediction
benchmark with:
- Standardized evaluation across all major methods (10+ models)
- Cross-context difficulty tiers (same cell type → different cell type → different organism)
- Both calibrated and uncalibrated metrics
- Comprehensive linear and mean-shift baselines
- Tahoe-100M as the anchor dataset (never used in any benchmark)

**Why it wins:**
- Resolves the highest-profile methodological controversy in computational biology
- Lowest compute requirement (1,000-2,000 GPU-hrs)
- All data public (CC0), all methods open-source
- Clear publication target (Nature Methods published both the critique and the defense)
- Fast iteration cycle enables thorough ablation studies

**Risks:**
- scPerturBench (Nature Methods, Dec 2025) partially occupies the space -- must
  differentiate with Tahoe-100M, cross-context tiers, and metric calibration
- Benchmark papers can feel "incremental" to Nature Comp Sci reviewers
- The answer (DL helps / DL doesn't help) is unknown -- both outcomes are publishable
  but "DL doesn't help" is a harder paper to place

**Compute:** 1,000-2,000 GPU-hrs (~1 week on small cluster)
**Timeline:** 3-4 months to submission
**Competition window:** Moderate (scPerturBench exists, but no Tahoe-100M benchmark)

---

### #2: Gamma -- Dynamics-to-Function: Connecting Conformational Ensembles to Biology

**Consensus score: 8.30 | Venue: Nature Computational Science**

**The problem:** AlphaFold solved structure prediction, but proteins function as dynamic
ensembles. BioEmu (Microsoft, 2024) and AlphaFlow can now generate conformational
ensembles in minutes rather than months of MD -- but no method connects ensemble
properties to biological function (binding affinity, catalytic rate, DMS fitness).
Current mutation effect predictors (AlphaMissense, ESM-1v, EVE) completely ignore
conformational dynamics.

**The project:** Build the first general framework mapping conformational ensembles to
biological function:
1. Generate variant-specific ensembles with BioEmu for 200+ ProteinGym proteins
2. Extract ensemble features (RMSF, contact maps, pocket volumes, hinge motions)
3. Train ML models predicting DMS fitness from ensemble properties
4. Demonstrate that dynamics-aware predictions outperform sequence-only methods
5. Identify which proteins and mutation types benefit most from ensemble information

**Why it ranks #2:**
- Addresses the central post-AlphaFold question ("structure is solved, but function isn't")
- BioEmu makes this newly feasible (MIT license, pip install, H200-ready)
- ProteinGym 2.7M variants provides the functional readout
- High novelty: no one has published this combination despite BioEmu being 9 months old
- Clear Nature Comp Sci fit: changes how the field thinks about mutation effects
- Overwhelmingly voted best combination partner (4/7 specialists pair it with Alpha-M)

**Risks:**
- 6-18 month competition window (Microsoft/BioEmu team could do this)
- Ensemble quality for non-globular/disordered proteins is unvalidated
- The signal may be weak: dynamics may add only marginally to sequence-based predictions

**Compute:** ~8,200 GPU-hrs (~6 weeks on 8 H200s)
**Timeline:** 4-5 months to submission
**Competition window:** Moderate-narrow (Microsoft Research is the key threat)

---

### #3: Beta -- ContextVEP: Context-Dependent Variant Effect Prediction

**Consensus score: 8.17 | Venue: Nature Comp Sci / Nature Genetics**

**The problem:** Variant effect predictors (AlphaMissense, EVE, REVEL) provide a single
context-free score per variant, but pathogenicity depends on tissue type, disease
context, genetic background, and mechanism of action. The numbers are damning:
- 83.3% false positive rate for AlphaMissense in IRF6 and similar genes
- >231,000 missense VUS in ClinVar with no resolution path
- AUROC 0.48-0.52 (near random) for non-coding GWAS variant effects
- Mean reclassification time: 22-30 months per VUS

**The project:** Build ContextVEP, the first variant effect predictor that accounts for
biological context:
- Inputs: variant + tissue (GTEx/HPA) + disease (HPO/ClinVar) + mechanism (GOF/LOF)
- Architecture: multi-modal transformer with cross-attention fusion
- Training: ClinVar reclassifications + MaveDB + gnomAD constraint
- Validation: ClinVar temporal holdout, UK Biobank phenotype associations, MAVE concordance
- Extension: non-coding variants via AlphaGenome/Borzoi integration

**Why it ranks #3:**
- Highest clinical impact of all projects (1M+ patients affected by VUS)
- Lowest compute (500-1,000 GPU-hrs)
- All data public and well-curated
- Clear successor to AlphaMissense (which set the standard but acknowledged limitations)
- Dual coding + non-coding framing elevates to Nature-level ambition

**Risks:**
- Gap has partially narrowed (DYNA, DIVA, popEVE, pVEP published in 2025-2026)
- Complex multi-modal integration may not yield large improvements
- Clinical validation without wet lab is challenging (but ClinVar reclassifications help)
- Venue uncertainty: too clinical for Nature Comp Sci? too computational for Nature Genetics?

**Compute:** 500-1,000 GPU-hrs (~days)
**Timeline:** 3-4 months to submission
**Competition window:** Moderate (fragments exist but full integration is open)

---

## Recommended Strategy for CohortArchitect

### Primary Recommendation: Gamma + Alpha-M as a Combined Project

Despite Delta winning on consensus score, the **strongest Nature Computational Science
submission** would combine Gamma (Dynamics-to-Function) with Alpha-M (MLFF Crash Test):

**Why this combination:**
- 4 out of 7 specialists independently recommended this pairing
- They form a coherent narrative: Alpha-M establishes which ensemble generators produce
  physically realistic dynamics (validated against NMR/SAXS), then Gamma shows that
  validated ensembles predict mutation effects better than sequence-only methods
- Together they answer: "Can we trust ML-generated protein ensembles, and do better
  ensembles predict function better?"
- Both address the central post-AlphaFold question
- Combined compute: ~190K-280K GPU-hrs (feasible on available HPC)
- Clear Nature Comp Sci scope: paradigm-shifting, multi-system, rigorous validation

**Risk mitigation:** The high compute cost of Alpha-M can be scoped down (15 proteins,
3 MLFFs, 50ns = viable starting point at ~45K GPU-hrs). Gamma is moderate compute.

### Alternative Recommendation: Delta as Fast-Track Publication

If speed and certainty are prioritized over ambition:
- Delta (PerturbMark) is the safest, fastest path to a high-impact publication
- 1-2K GPU-hrs, 3-4 months, Nature Methods target
- Resolves an active controversy with definitive evidence
- Could be executed in parallel with the Gamma+Alpha-M project

### Secondary Projects for Cohort 2 to Consider

- **Beta (ContextVEP)**: Strong clinical impact, low compute, but needs differentiation
  from recent 2025-2026 publications. Best as a second paper after the primary project.
- **Alpha-L (LiveBioBench)**: Important infrastructure but better as a community effort
  or long-term commitment rather than a single summer project.
- **Alpha-G (Molecular Design Benchmark)**: Gap has narrowed significantly (MolGenBench,
  Beyond Affinity, ADMETrix). Curation burden makes summer 2026 timeline risky.

---

## Final Summary

The Cohort1 Gap Scouts process identified **33 gaps**, narrowed to **10**, deep-dived
on **7 combined projects**, and ranked them across **7 independent specialists**.

**The field's biggest meta-gap in 2026 is evaluation**: 4 of 6 final projects are
fundamentally benchmarking efforts, reflecting that computational biology has more
methods than it can properly evaluate.

**The top recommendation for Cohort 2**: Design a combined **Gamma + Alpha-M** project
("From Accurate Ensembles to Biological Function") targeting Nature Computational Science,
with **Delta** as a parallel fast-track publication in Nature Methods.

**For the CohortArchitect**: Build Cohort 2 around the Gamma + Alpha-M core, with
specialists covering:
1. ML force field expertise (running and evaluating MLFFs)
2. Protein dynamics / ensemble analysis
3. Machine learning for function prediction from structural features
4. Benchmark design and evaluation methodology
5. Experimental data curation (NMR, SAXS, DMS)
