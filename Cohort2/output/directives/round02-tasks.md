---
agent: orch
round: 2
date: 2026-04-14
type: directive
---

# Round 2 Directives: Formal Proposals

## Context

Round 1 deep research (6 specialists, 5,426 lines) confirmed all three projects are
feasible and differentiated. Round 2 produces execution-ready proposals.

## Key Decisions Embedded in These Directives

1. **Alpha-M MVP scope:** 7 proteins × 3 MLFFs × 50 ns + S2 replicas. Stretch to 15
   proteins if compute allows.
2. **Gamma uses wildtype ensemble hypothesis** as primary approach, with variant-specific
   ensembles as secondary validation on a subset.
3. **Delta is URGENT:** 3-6 month competitive window. Proposal must be preprint-ready.
4. **Integration:** 8-protein overlap between Alpha-M and Gamma enables combined paper.
   Design for separability.
5. **Parallel execution:** All three projects share HPC but do not compete for compute
   (Delta: ~1K GPU-hrs, Gamma: ~8K, Alpha-M: ~51-80K).

## Assignments

### mlffeng: Alpha-M Full Simulation Protocol Proposal
Write a detailed, execution-ready proposal covering:
- Final MLFF selection (MACE-OFF24(M), SO3LR, AI2BMD) with justification
- Complete simulation protocol: timestep, thermostat, barostat, equilibration, production
- S2 convergence strategy (10 replicas × 10 ns per system)
- SLURM job design for parallel execution on H200/B200 nodes
- Detailed compute budget with contingency (failed runs, debugging)
- MVP timeline (7 proteins) and stretch timeline (15 proteins)
- Risk mitigation plan for MLFF instability

### bioval: Alpha-M Validation Data Pipeline Proposal
Write a detailed proposal covering:
- Final protein selection: 7 MVP proteins + 8 stretch proteins, with all BMRB/SASBDB IDs
- NMR data extraction protocol from BMRB (step-by-step)
- SAXS data extraction protocol from SASBDB
- Back-calculation pipeline: SPARTA+ for shifts, Karplus for J-couplings, Lipari-Szabo
  for S2, Pepsi-SAXS for scattering profiles
- Quality control procedures for experimental reference data
- Statistical pass/fail framework calibrated against classical FF baselines
- Integration with Gamma: which 8 overlap proteins, what DMS data is available

### ensfunc: Gamma Full Proposal
Write a detailed proposal covering:
- BioEmu ensemble generation pipeline (wildtype + variant-specific subset)
- ProteinGym protein selection: which of the 217 assays to prioritize (structural data,
  assay type diversity, variant count)
- Ensemble feature extraction: top 10-15 features with computation methods
- ML framework: MLP baseline → GNN for publication, with architecture details
- Cross-validation strategy: nested leave-protein-out, stratified by assay type
- Baselines: EVE, ESM-1v, AlphaMissense, TranceptEVE, GEMME
- The wildtype ensemble hypothesis: experimental design to test it rigorously
- Integration with Alpha-M: the 8-overlap proteins and what we learn from validated
  vs unvalidated ensembles
- Compute budget breakdown and timeline

### pertbio: Delta Full Proposal (PerturbMark)
Write a detailed proposal covering:
- Complete PerturbMark benchmark specification
- Tahoe-100M preprocessing protocol (normalization, filtering, QC)
- Cross-context split construction: Tier 0-3 with exact cell lines and compounds
- Method evaluation protocol: how to run each of 10+ methods fairly
- 7-metric suite specification with computation details
- Mandatory baseline specifications (mean, additive, CRISPR-informed mean, linear)
- Differentiation narrative from scPerturBench
- Nature Methods publication framing
- 6-week timeline to preprint
- Batch effect control protocol

### evalstat: Unified Evaluation Framework Proposal
Write a proposal that provides:
- Pre-registration protocol for all three projects (what to lock, what to leave flexible)
- Alpha-M: Friedman/Nemenyi framework, sample size considerations, multi-observable
  integration
- Gamma: nested leave-protein-out CV, overfitting controls, feature importance analysis
  plan, win rate threshold
- Delta: metric calibration framework, per-tier significance testing, BH-FDR correction
- Cross-project reporting standards matching Nature Portfolio requirements
- Template for per-project results tables and figures
- Sensitivity analysis plans for each project

### scopeadv: Strategic Integration Proposal
Write a proposal that provides:
- Final competition status for each project (April 2026 snapshot)
- Publication sequence: Delta → Gamma → Gamma+Alpha-M with dates
- Preprint strategy: when to post each, how to order
- Combined vs separate paper analysis: when to decide, what triggers each path
- Gantt chart: all three projects May-November 2026
- Risk registry: top 5 risks per project, probability, impact, mitigation
- Kill criteria with dates: when to evaluate, what evidence triggers pivot
- "Worst case still publishes" analysis for each project
- Narrative framing: suggested titles and one-sentence claims for each paper

## Template

All proposals must use the proposal template from `../../templates/proposal.md`.
Include the full frontmatter and all sections.

## Timeline

Round 2 proposals are due before Round 3 cross-review begins.
