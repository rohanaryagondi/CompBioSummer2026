---
agent: orch
round: 2
date: 2026-04-14
type: directive
---

# Round 2 Directives: Deep-Dive Research Assignments

## Overview

Round 1 produced 33 gaps across 7 specialists. The top 10 gaps (score >= 8.0) advance
to deep-dive research. Each specialist is assigned 1-2 gaps for intensive investigation,
including cross-domain assignments where themes converge.

## Assignments

### protdyn: Dynamics-to-Function + Ensemble Mutation Effects
- Deep dive on gaps #6 (dynamics-to-function) and #7 (ensemble-mutation-effects)
- Verify BioEmu accessibility and ensemble quality
- Assess DMS/ProteinGym data coverage for ensemble-function mapping
- Estimate compute requirements for proteome-scale ensemble generation
- Check for 2026 preprints filling this gap
- Explore Combined Project Gamma framing

### genchem: End-to-End Evaluation Crisis in Molecular Design
- Deep dive on gap #4 (evaluation-crisis)
- Survey all existing benchmarks (GuacaMol, MOSES, PMO, TDC, Polaris, PoseBusters)
- Identify what an end-to-end benchmark would require
- Assess data availability for retrospective validation
- Check for 2026 benchmark papers
- Consider connection to Theme A (cross-domain evaluation crisis)

### multisim: ML Force Field Experimental Validation Benchmark
- Deep dive on gap #8 (mlff-experimental-validation)
- Survey experimental data available for validation (NMR, SAXS, HDX-MS in PDB/BMRB)
- Assess which MLFFs are open-source and runnable (MACE, ANI, Allegro, eSEN)
- Estimate GPU-hours for benchmark suite
- Check for competing benchmarks in preparation
- Consider connection to protdyn dynamics gaps

### reggeno: Complex Trait Non-Coding Variant Effect Prediction
- Deep dive on gap #1 (complex-trait-vep)
- Verify near-random performance claims with specific papers and numbers
- Assess Borzoi/AlphaGenome availability and performance
- Survey fine-mapping data (SuSiE credible sets, Open Targets)
- Identify specific trait/disease systems for proof-of-concept
- Explore connection to transmed context-vus (Combined Project Beta)

### sysnet: Cross-Context Perturbation Generalization + Perturbation Crisis
- Deep dive on gaps #9 (context-perturb-transfer) and #2 (perturbation-prediction-crisis)
- Verify linear baseline results from Nature Methods 2025
- Assess X-Atlas/Tahoe-100M data accessibility and format
- Survey all perturbation prediction methods with reproduction potential
- Scope a definitive cross-context benchmark
- Explore Combined Project Delta framing

### aiml: Foundation Model Evaluation Crisis + Uncertainty Quantification
- Deep dive on gaps #5 (fm-evaluation-crisis) and #10 (uncertainty-aware-bio-fm)
- Survey LiveProteinBench methodology and extensibility
- Assess contamination evidence across modalities
- Identify UQ methods applicable to biological FMs
- Scope LiveBioBench design across protein/DNA/single-cell/molecules
- Check for competing cross-modal benchmark efforts

### transmed: Context-Dependent VUS Resolution
- Deep dive on gap #3 (context-vus)
- Quantify VUS backlog by gene, disease, and clinical impact
- Assess tissue-specific expression data (GTEx, HPA) for context modeling
- Survey ClinVar reclassification patterns for training data
- Scope modular architecture for context-dependent prediction
- Explore connection to reggeno complex-trait-vep (Combined Project Beta)

## Output Format

Each specialist writes: `Cohort1/output/research/<shortname>-deep-R02.md`

Deep-dive reports should include:
1. **Gap verification**: Does the gap still exist? Any 2026 preprints?
2. **Data audit**: Specific datasets, sizes, formats, accessibility
3. **Method survey**: What tools/methods would be needed? What exists vs. what's new?
4. **Compute estimate**: GPU-hours, storage, timeline
5. **Feasibility reassessment**: Updated ratings after deep research
6. **Competition check**: Who is working on this? Preprints? Conference papers?
7. **Publication framing**: Specific paper title, main claim, target venue
8. **Combined project assessment**: How would this gap combine with related gaps?
