---
agent: ReviewCohort Orchestrator (orch)
round: 4
date: 2026-04-15
type: final-implementation-plan
---

# Final Implementation Plan: CompBioSummer2026 Research Portfolio

## Document Status

This document is the **definitive output** of the ReviewCohort critical
evaluation pipeline. It integrates 3 rounds of review by 5 specialist
reviewers (dynrev, biomlrev, statrev, implrev, stratrev) across ~14,000
lines of analysis with 460+ citations. All decisions below reflect reviewer
consensus unless noted otherwise.

---

## 1. Executive Summary of Reviewer Consensus

**Where all 5 reviewers AGREE:**

1. AI2BMD should be dropped (zero scientific loss; hybrid solvent model,
   22 open issues, no HPC support).
2. The integration claim ("does ensemble physical accuracy predict functional
   utility?") remains completely unoccupied in the literature as of April
   2026 -- the portfolio's highest-value target.
3. The 6x8 design has only ~42% power at rho=0.5. The minimum viable design
   is 14 proteins x 10 generators.
4. The N(0.5, 0.15^2) Bayesian prior is not defensible (4:1 prior-to-data
   ratio). JZS default prior is the only acceptable primary test.
5. Trajectory truncation to shortest common length is mandatory for fair
   benchmark comparison.
6. Delta is the strongest proposal (75-80% viability) and must preprint by
   August 15.
7. BH is the correct primary FDR method for Delta (field standard is no
   correction at all).
8. Pre-registration on OSF by May 15 is essential for credibility.

**Where reviewers DISAGREE:**

1. Combined paper viability: dynrev (proceed with conditions) vs biomlrev/
   stratrev (default to separation, 30% viability). **Resolution:** Default
   to separation with conditional recombination at August 31.
2. Whether 14x10 is achievable: statrev (required for power) vs implrev
   (9x10 is the maximum fully crossed MLFF design). **Resolution:** Split
   into two sub-analyses (9-protein MLFF benchmark + 14-protein integration).
3. Combined paper probability: ranges from 30% (stratrev) to 40% (implrev
   on implementation grounds). **Resolution:** Use 30% as planning baseline.
4. Convergence attenuation: statrev quantifies ~15-25% ICC attenuation;
   dynrev acknowledges but notes effect is partially offset by adaptive
   protocol. **Resolution:** Report both raw and corrected ICC; use
   corrected for power calculations.

**Portfolio expected value: 17.3 impact units** (down from 19.2 at Round 1).

---

## 2. Verdict Per Proposal

### 2.1 Alpha-M: MLFF Force Field Benchmark

**Verdict: GO. Viability 65-70%.**

Alpha-M is the portfolio foundation. It produces essential data regardless
of whether the combined paper succeeds, has the lowest scoop risk (<10%),
and is publishable as a standalone NatMeth paper.

| Attribute | Value |
|-----------|-------|
| Target venue | NatMeth (standalone) or NCS (if combined) |
| Protein set | 14 proteins across 3 tiers (see Section 5.2) |
| Generator roster | 10 generators across 4 paradigms (see Section 5.3) |
| Primary observables | S2 order parameters, J-couplings, RMSF, chemical shifts |
| Experimental reference | NMR 15N relaxation (BMRB), NOE, RDC, SAXS |
| Compute budget | ~166,632 GPU-hours total (Phases 1-3 + contingency) |
| Timeline | May 1 - October 15 (Phase 1: May-June; Phase 2: July-Sept; Phase 3: Sept-Oct) |
| Statistical framework | Friedman test with Nemenyi post-hoc; hierarchical bootstrap; ICC estimation |

**Key requirements (from reviewer consensus):**
- Trajectory truncation protocol (statrev C1)
- Pre-registered analysis plan (statrev C4)
- Garnet reported as contamination case study, not competitive method
- Adaptive trajectory-length protocol for MLFFs (dynrev)
- BioEmu disulfide verification for BPTI and HEWL (Week 1 test)

### 2.2 Gamma: Dynamics-to-Fitness Prediction

**Verdict: CONDITIONAL GO. Viability 45-50%.**

Gamma's unique contribution is connecting experimental DMS fitness to
dynamics features, with assay-type stratification as the primary finding.
The RMSF-conservation-RSA collinearity ablation is the central hypothesis
test.

| Attribute | Value |
|-----------|-------|
| Target venue | Genome Research or Bioinformatics (standalone); NCS (if combined) |
| Proteins | 150+ ProteinGym proteins with BioEmu ensembles |
| Baseline | RSALOR (Spearman 0.465), ProSST, S3F-MSA |
| Success threshold | >57% win rate on binding+activity (N~57 assays); paired Wilcoxon p<0.05 |
| Minimum delta | >=0.04 Spearman on binding; >=0.03 on activity |
| Central test | RSALOR + RMSF vs RSALOR (does dynamics add beyond conservation?) |
| Compute budget | ~2,000 GPU-hours (BioEmu ensemble generation) |
| Timeline | May 1 - October 15 |

**Kill condition (GK2):** If delta-Spearman <0.01 on binding+activity after
first 50 proteins, pivot to negative-result framing at PLOS Comp Bio.

### 2.3 Combined Paper: Alpha-M + Gamma Integration

**Verdict: DEFAULT TO SEPARATION. Viability 30%.**

The combined paper is the portfolio's highest-ceiling outcome (NCS, impact=10)
but the statistically riskiest. The integration claim is completely
unoccupied, giving it unique strategic value. It proceeds as a conditional
upside, not the default plan.

| Attribute | Value |
|-----------|-------|
| Target venue | Nature Computational Science |
| Central claim | Physical accuracy of protein ensemble generators correlates with their utility for predicting mutation fitness effects |
| Design | 14 proteins x ~7 generators (integration); 9 proteins x 10 generators (MLFF benchmark sub-analysis) |
| Primary test | JZS Bayesian correlation (BF_10 >3 required) |
| Decision point | August 31, 2026 |
| Minimum evidence | BF_10 >3 under JZS, rho >0.4, Gamma delta >0.03, >=12 proteins confirmed |

**Decision architecture:**
- If T1-T6 all met at August 31: proceed with combined NCS submission (Nov 15)
- If any S1-S5 trigger fires: immediate separation
- Alpha-M -> NatMeth RR Stage 1 (Sept 15)
- Gamma -> standalone manuscript (preprint Oct 15)

### 2.4 Delta: Perturbation Biology Benchmark

**Verdict: GO with accelerated timeline. Viability 75-80%.**

Delta is the strongest, most independent proposal. First independent neutral
benchmark on Tahoe-100M with calibrated evaluation metrics.

| Attribute | Value |
|-----------|-------|
| Target venue | NatMeth |
| Dataset | Tahoe-100M (429 GB, 100M cells, CC0 license) |
| Tier 1 methods | GEARS, scGPT, CPA, scFoundation, Tahoe-x1 (new), + 5 baselines |
| Tier 2 methods | AetherCell (sole viable candidate) |
| Primary metrics | WMSE (gates Spearman on top-k DEGs via hierarchical testing) |
| FDR | BH primary, BY sensitivity |
| Compute budget | ~15,000-20,000 GPU-hours |
| Timeline | May 1 - August 15 (preprint), September 1 (submission) |
| Differentiation | Neutrality, calibrated metrics, difficulty stratification, cross-context evaluation |

**Non-negotiable:** Preprint by August 15. Scoop risk (55-65%) makes speed
the primary competitive advantage.

---

## 3. Combined vs Separate Publication Decision

### 3.1 Default Strategy: Separation

The portfolio is designed to produce high-value publications under
separation:

| Paper | Venue | Viability | Submission |
|-------|-------|-----------|-----------|
| Alpha-M standalone | NatMeth (Registered Report) | 65-70% | Stage 1: Sept 15 |
| Gamma standalone | Genome Research / Bioinformatics | 45-50% | Preprint: Oct 15 |
| Delta standalone | NatMeth (Article) | 75-80% | Preprint: Aug 15 |

### 3.2 Conditional Recombination

If ALL of the following are true at August 31:

**GO thresholds (T1-T6, ALL required):**

| ID | Criterion | Measurement |
|----|-----------|-------------|
| T1 | >=1 MLFF stable >10 ns on >=3 Tier B proteins | Phase 1 pilot data |
| T2 | S2 block-split R^2 >0.90 on >=1 protein | Phase 1 analysis |
| T3 | BioEmu disulfide integrity >95% for BPTI/HEWL | Week 1 quick test |
| T4 | Integration rank correlation rho >0 (directional) | Pilot analysis |
| T5 | >=12 of 14 proteins confirmed with BMRB S2 data | Literature verification |
| T6 | >=9 of 10 generators distinguishable (JSD >0.01) | Pilot analysis |

Then proceed with combined NCS submission (preprint Nov 1, submission Nov 15).

**SEPARATE triggers (ANY one fires):**

| ID | Trigger | Measurement |
|----|---------|-------------|
| S1 | Pilot integration rho <=0 | Phase 1 analysis |
| S2 | <2 MLFFs operational by June 30 | Software testing |
| S3 | BF_10 projected <1 under JZS at expanded design | Statistical projection |
| S4 | Gamma delta-Spearman <0.02 on binding+activity | Gamma pilot |
| S5 | NCS-relevant scoop published | Competition scan |

---

## 4. Scope Decisions

All decisions below are final and have unanimous (5-0) or near-unanimous
(4-1) reviewer support.

| # | Decision | Choice | Vote |
|---|----------|--------|------|
| 1 | Drop AI2BMD | YES | 5-0 |
| 2 | Add Tahoe-x1 to Delta Tier 1 | YES | 5-0 |
| 3 | Gamma win rate threshold | 57% (raised from 55%) | 5-0 |
| 4 | Delta FDR method | BH primary, BY sensitivity | 5-0 |
| 5 | Pre-registration | Dual-track: OSF May 15 + NatMeth RR fallback | 5-0 |
| 6 | Default publication strategy | Separation with conditional recombination | 4-1 |
| 7 | Trajectory truncation | Mandatory for primary analysis | 5-0 |
| 8 | Bayesian primary test | JZS default prior | 5-0 |
| 9 | Garnet treatment | Contamination case study, not competitive | 5-0 |
| 10 | Gamma central test | RSALOR+RMSF vs RSALOR ablation | 5-0 |

---

## 5. Method Rosters and Protein Set

### 5.1 Alpha-M: 10 Generators

| # | Generator | Category | Software | Risk Level |
|---|-----------|----------|----------|-----------|
| 1 | MACE-OFF24 | MLFF | mace-torch + OpenMM-ML | MODERATE |
| 2 | SO3LR | MLFF | JAX-MD | MODERATE-HIGH |
| 3 | Garnet | ML-classical | PyTorch + OpenMM | LOW (contamination study) |
| 4 | BioEmu | Generative | pip install bioemu | LOW |
| 5 | Boltz-2 | Generative | PyTorch | LOW |
| 6 | AlphaFlow | Generative | PyTorch | LOW |
| 7 | AMBER ff14SB | Classical | OpenMM | BASELINE |
| 8 | AMBER ff19SB | Classical | OpenMM | BASELINE |
| 9 | a99SB-disp | Classical | OpenMM + TIP4P-D | LOW-MODERATE |
| 10 | CHARMM36m | Classical | OpenMM / GROMACS | BASELINE |

Note: ff14SB/ff19SB redundancy test pre-registered. If indistinguishable
(Friedman p >0.20 on S2 across all proteins), merge as single generator.

### 5.2 Alpha-M: 14 Proteins

| # | Protein | Res. | Tier | S2 Quality | Garnet Contaminated | MLFF Feasible |
|---|---------|------|------|-----------|-------------------|--------------|
| 1 | WW domain (PIN1) | 34 | A | Good | No | Yes |
| 2 | Crambin | 46 | A | None (stability only) | No | Yes |
| 3 | GB3 | 56 | A/B | Excellent | Yes (training) | Yes |
| 4 | GB1 | 56 | B | Excellent | No | Yes |
| 5 | BPTI | 58 | B | Excellent | Yes (validation) | Yes |
| 6 | CI2 | 64 | B | Good | No | Yes |
| 7 | CspA | 70 | B | Good | No | Partial |
| 8 | alpha-3D | 73 | B/C | Good | No | Partial |
| 9 | Calbindin D9k | 75 | B | Good | No | Partial |
| 10 | Ubiquitin | 76 | B | Excellent | Yes (validation) | Partial |
| 11 | HPr | 85 | B | Moderate | No | Unlikely |
| 12 | Barnase | 110 | C | Excellent | Yes (complex val.) | No |
| 13 | HEWL | 129 | C | Excellent | Yes (validation) | No |
| 14 | T4 lysozyme | 164 | C | Good | No | No |

- Garnet-uncontaminated: 9 proteins
- MLFF-feasible (<80 res): 9-10 proteins
- Classical + generative only (>80 res): 4 proteins
- Stability control (no S2): 1 (Crambin)

### 5.3 Delta: Method Roster

**Tier 1 (mandatory):**

| # | Method | Type | Code Status |
|---|--------|------|------------|
| 1 | GEARS | GNN | Available; needs memory optimization for Tahoe-100M |
| 2 | scGPT | Transformer | Available |
| 3 | CPA | VAE | Available; last release 2023 |
| 4 | scFoundation | Large model | Available |
| 5 | Tahoe-x1 | Foundation model (3B) | Available; native Tahoe-100M streaming |

**Tier 2 (if feasible):**

| # | Method | Status |
|---|--------|--------|
| 1 | AetherCell | Sole viable Tier 2 (15 stars, code available) |

**Baselines (5):** Linear regression, mean expression, PCA-based, random
(calibration control), persistence (same cell type, different perturbation).

**Dropped:** scPPDM (no code), AlphaCell (no code), X-Cell (no weights),
pertTF (no code), AI2BMD (all methods).

---

## 6. Title Recommendations

| Scenario | Title | Venue |
|----------|-------|-------|
| Combined paper | "Physical accuracy of protein ensembles predicts functional utility across mutation fitness landscapes" | NCS |
| Alpha-M standalone | "Machine-learning force fields for proteins: how close are we to experiment?" | NatMeth |
| Delta standalone | "When does deep learning help? Calibrated perturbation benchmarking across cellular contexts on Tahoe-100M" | NatMeth |
| Gamma positive | "Protein conformational ensembles encode mutation fitness effects beyond sequence information" | Genome Research |
| Gamma null | "Dynamics features do not improve fitness prediction beyond sequence conservation" | PLOS Comp Bio |

---

## 7. Publication Strategy

### 7.1 Dual-Track Architecture

```
Track A (default): SEPARATION
  Alpha-M -> NatMeth Registered Report (Stage 1: Sept 15)
  Gamma   -> Genome Research / Bioinformatics (preprint: Oct 15)
  Delta   -> NatMeth Article (preprint: Aug 15, submit: Sept 1)

Track B (conditional): COMBINATION
  Combined -> NCS (preprint: Nov 1, submit: Nov 15)
  Delta    -> NatMeth Article (same timeline)
  
Decision point: August 31, 2026
```

### 7.2 Pre-Registration Plan

| Date | Action | Scope |
|------|--------|-------|
| May 15 | OSF pre-registration | All 3 projects: protein set, generators, observables, statistical tests, decision rules, truncation protocol |
| Aug 31 | Decision point | GO criteria (T1-T6) / SEPARATE triggers (S1-S5) |
| Sept 15 | NatMeth RR Stage 1 (if separation) | Alpha-M: adapted from OSF pre-registration |

The OSF pre-registration document covers BOTH the combined and separate
scenarios. It explicitly states the August 31 decision rules.

### 7.3 Competition Monitoring

Monthly scans on the 1st of each month (June-November):

| Search | Sources | Escalation |
|--------|---------|-----------|
| "BioEmu" + "fitness" / "mutation" | bioRxiv, arXiv | If found: accelerate Gamma preprint by 4 weeks |
| "MLFF" + "protein" + "benchmark" + "NMR" | bioRxiv, arXiv | If found: evaluate overlap with Alpha-M |
| "Tahoe-100M" + "benchmark" | bioRxiv, Google Scholar | If found: accelerate Delta preprint |
| "force field" + "fitness prediction" | bioRxiv, arXiv | If found: combined paper scoop -- trigger S5 |

---

## 8. Execution Timeline (Week-by-Week)

### Phase 0: Pre-Project Setup (April 15-30)

| Task | Owner | Deliverable |
|------|-------|-------------|
| Tahoe-100M download + preprocessing pipeline | Delta lead | Verified data loader (scDataset) |
| BioEmu v1.3.1 disulfide test (BPTI, HEWL) | Alpha-M lead | SS bond integrity report |
| BMRB S2 data verification for 14 proteins | Alpha-M lead | Confirmed BMRB entries |
| Conda environment specs for all methods | All | 9 pinned environment YAML files |

### Phase 1: Pilot Studies and Setup (Weeks 1-9, May 1 - June 30)

| Week | Alpha-M | Gamma | Delta |
|------|---------|-------|-------|
| 1-2 | Install MACE-OFF24, SO3LR. Test on crambin (1 ns NVT) | BioEmu ensemble generation (batch 1: 50 proteins) | Method setup: GEARS, scGPT, CPA |
| 3-4 | NPT stability tests (5 ns) on WW domain, GB3, ubiquitin | BioEmu ensemble generation (batch 2: 50 proteins) | Method setup: scFoundation, Tahoe-x1 |
| 5-6 | Garnet OpenMM integration. a99SB-disp TIP4P-D setup | Feature extraction pipeline | Baseline implementation. AetherCell setup |
| 7-8 | MLFF pilot production: 10-50 ns on 3 Tier A/B proteins | ML pipeline (MLP, XGBoost, GATv2) | Cross-validation framework. Calibration metrics |
| 9 | Phase 1 analysis: S2 convergence, generator distinctness | Pilot fitness predictions (50 proteins) | Full method runs on test split |

**Decision D2 (June 30):** MLFF pilot GO/NO-GO based on dynrev criteria G1-G6.

### Phase 2: Production (Weeks 10-17, July 1 - August 22)

| Week | Alpha-M | Gamma | Delta |
|------|---------|-------|-------|
| 10-11 | Phase 2 production: Tier A/B MLFF runs + all classical | Full ProteinGym evaluation (all 150+ proteins) | Full Tahoe-100M evaluation (all methods) |
| 12-13 | Phase 2 production: Tier C classical/generative | Ablation experiments (5 model variants) | Cross-context evaluation. Difficulty stratification |
| 14-15 | Back-calculation (SPARTA+, Pepsi-SAXS). Analysis pipeline | Assay-type stratification analysis | Calibration analysis. Metric gaming tests |
| 16-17 | ICC estimation. Friedman/Nemenyi tests | Boltz-2 vs BioEmu comparison | Figures. Manuscript draft |

**GPU allocation (Weeks 10-17):** H200 GPUs dedicated to Alpha-M MLFF
simulations. RTX 5000 Ada GPUs for Delta DL model training. BioEmu and
Boltz-2 on any available GPU (<8 GB needed).

### Phase 3: Decision and Manuscripts (Weeks 18-30, August 23 - November 30)

| Date | Milestone |
|------|-----------|
| Aug 15 | **Delta preprint** (D5) |
| Aug 31 | **COMBINED PAPER GO/NO-GO** (T1-T6 / S1-S5) |
| Sept 1 | Delta NatMeth submission |
| Sept 1-15 | Alpha-M Phase 3 replicas (5 replicas on 6 priority proteins) |
| Sept 15 | If separation: Alpha-M NatMeth RR Stage 1 submission |
| Oct 15 | If separation: Gamma standalone preprint |
| Oct 15 | Alpha-M standalone preprint (if not combined) |
| Nov 1 | If combined: NCS preprint |
| Nov 15 | If combined: NCS submission |

---

## 9. Resource Allocation

### 9.1 Compute Budget

| Project | Phase | GPU-hours | GPU Type |
|---------|-------|-----------|---------|
| Alpha-M | Phase 1 (pilot) | 2,000-3,000 | H200 |
| Alpha-M | Phase 2 (production) | 24,100-33,800 | H200 (MLFF), any (classical) |
| Alpha-M | Phase 3 (replicas) | 87,792 | H200 (MLFF), any (classical) |
| Alpha-M | Contingency (20%) | 22,800 | H200 |
| Gamma | BioEmu ensembles + ML | 2,000 | Any GPU |
| Delta | DL training + eval | 15,000-20,000 | RTX 5000 Ada (training), any (eval) |
| **Total** | | **~154,000-170,000** | |

### 9.2 Storage

| Dataset | Size | Location |
|---------|------|----------|
| Alpha-M trajectories (Phase 2+3) | 5-8 TB | HPC scratch |
| BioEmu/Boltz-2/AlphaFlow ensembles | ~5 GB | Persistent |
| Tahoe-100M (raw + processed) | ~630-830 GB | HPC scratch |
| DL model checkpoints | 50-100 GB | Persistent |
| Analysis outputs + figures | ~10 GB | Persistent |
| **Total** | **~6-9 TB** | |

### 9.3 Engineer Time

| Period | Alpha-M | Gamma | Delta | Total FTE |
|--------|---------|-------|-------|-----------|
| Weeks 1-3 | 1.0 | 0.5 | 1.0 | 2.5 |
| Weeks 4-9 | 1.0 | 0.5 | 1.0 | 2.5 |
| Weeks 10-17 | 0.5 | 0.5 | 0.5 | 1.5 |
| Weeks 18-28 | 1.0 | 0.5 | 0.25 | 1.75 |

Peak: 2.5 FTE (Weeks 1-9). A team of 3 people can handle this.

---

## 10. Risk Mitigation

### 10.1 Technical Risks

| Risk | Probability | Mitigation |
|------|------------|-----------|
| MLFF trajectory failure (MACE-OFF24 or SO3LR unstable on all proteins) | 25% | Proceed with 1 MLFF if the other works; if both fail, Alpha-M becomes classical+generative benchmark |
| BioEmu disulfide failure on BPTI/HEWL | 15% | Drop BPTI and HEWL; proceed with 12 proteins |
| Garnet produces no usable data | 10% | Drop Garnet; reframe without NMR-aware FF comparison |
| SO3LR JAX environment incompatibility | 20% | 3-7 day setup window; dedicated JAX environment |
| Tahoe-100M memory issues with GEARS | 30% | Use scDataset streaming; cap loaded cells |
| ff14SB/ff19SB indistinguishable | 40% | Merge as single generator; total drops to 9 |

### 10.2 Strategic Risks

| Risk | Probability | Mitigation |
|------|------------|-----------|
| BioEmu + ProteinGym scoop (Gamma) | 35-45% | Monthly scan; accelerate preprint by 4 weeks if detected |
| Delta differentiation erosion (SCALE, VCC) | 55-65% | Frame as "neutral, calibrated" evaluation; emphasize difficulty stratification |
| NCS desk rejection of combined paper | 40% | Pre-written cover letter; immediate split to NatMeth + Genome Research |
| Dynamics add nothing to fitness prediction | 30% | Pivot to negative-result framing at PLOS Comp Bio |

### 10.3 Statistical Risks

| Risk | Probability | Mitigation |
|------|------------|-----------|
| Integration BF <3 at 14x10 design | 40% | JZS prior + 4-prior sensitivity; frame as "first evidence" if BF 1-3 |
| Convergence attenuation reduces power below 70% | 30% | Report corrected ICC; add proteins if available |
| Gamma delta <0.03 on binding+activity | 35% | Supplement with 5-10 additional binding DMS datasets |

---

## 11. Kill Criteria

### 11.1 Alpha-M

| ID | Criterion | Threshold | Date | Consequence |
|----|-----------|-----------|------|-------------|
| AK1 | MLFF total failure | 0 MLFFs with >5 ns trajectory | June 30 | Classical+generative benchmark (reduced scope) |
| AK2 | All S2 indistinguishable | R^2 spread <0.05 | Aug 15 | "Validation confirms consensus" (lower impact) |
| AK3 | BioEmu disulfide catastrophic | SS integrity <80% | June 15 | Drop BPTI/HEWL from set |
| AK4 | Compute budget >3x | >330K GPU-hrs | July 31 | Reduce to 10x8 design |
| AK5 | Garnet total failure | All proteins fail | July 15 | Drop Garnet; 9 generators |

### 11.2 Gamma

| ID | Criterion | Threshold | Date | Consequence |
|----|-----------|-----------|------|-------------|
| GK1 | BioEmu generation fails | <100 of 150 proteins | July 15 | Reduce scope or abandon |
| GK2 | Dynamics add nothing | delta-Spearman <0.01 on 50 proteins | Aug 15 | Negative-result paper (PLOS Comp Bio) |
| GK3 | Static methods surge | ProSST delta >0.10 over RSALOR | Ongoing | Re-evaluate publishability |
| GK4 | BioEmu scooped for ProteinGym | Preprint appears | Ongoing | Accelerate or abandon |

### 11.3 Combined Paper

| ID | Criterion | Threshold | Date | Consequence |
|----|-----------|-----------|------|-------------|
| CK1 | Separation triggered | Any S1-S5 | Aug 31 | Immediate split |
| CK2 | NCS desk rejection | Editor declines | Post-submission | Split to NatMeth + Genome Research |
| CK3 | Both reviews negative | 2/3 reviewers reject | Post-review | Revise as separate papers |
| CK4 | Integration scoop | Someone publishes FF-fitness link | Ongoing | Evaluate remaining novelty |

### 11.4 Delta

| ID | Criterion | Threshold | Date | Consequence |
|----|-----------|-----------|------|-------------|
| DK1 | Tahoe-100M data pipeline fails | Cannot load data by May 31 | May 31 | Fallback to smaller dataset |
| DK2 | <3 Tier 1 methods running | Methods fail to reproduce | June 6 | Drop failed methods; proceed with remainder |
| DK3 | Independent benchmark published first | Competitor preprint | Ongoing | Reframe as replication+extension |
| DK4 | All DL methods match linear baselines | No DL method beats linear | Aug 1 | "DL still doesn't help" (Ahlmann-Eltze extension) |
| DK5 | Tahoe-x1 unavailable | Weights retracted or license changed | May 15 | Proceed without; note gap |

---

## 12. Statistical Framework Summary

### 12.1 Alpha-M (Benchmark)

| Component | Method |
|-----------|--------|
| Primary test | Friedman test with Nemenyi post-hoc across generators |
| Effect size | S2 R^2 vs experimental NMR, per protein per generator |
| Clustering | Hierarchical bootstrap (resample proteins, then residues) |
| ICC | Estimate from pilot; report raw and convergence-corrected |
| Convergence | ICC(2,k) >0.80 AND ICC(2,1) >0.50 |
| Truncation | All trajectories to T_min per protein (from Phase 1) |

### 12.2 Gamma (Prediction)

| Component | Method |
|-----------|--------|
| Primary test | Paired Wilcoxon signed-rank on binding+activity assays (N~57) |
| Secondary test | Win rate >57% on all 217 assays |
| Central ablation | RSALOR+RMSF vs RSALOR (is dynamics redundant with conservation?) |
| Cross-validation | Homolog-aware (<30% seq identity) 5-fold CV |
| Baselines | RSALOR, ProSST, S3F-MSA per assay type |
| Feature importance | Full ablation: ESM2+RSA vs +RMSF vs +all dynamics |

### 12.3 Combined Paper (Integration)

| Component | Method |
|-----------|--------|
| Primary test | JZS Bayesian correlation (Cauchy(0,1) prior) |
| Decision rule | BF_10 >3 under JZS AND BF_10 >1 under skeptical prior |
| Sensitivity | 4 priors: JZS, Skeptical(0.5), Informative N(0.5,0.15^2), Flat U(-1,1) |
| Random effects | Crossed: (1|protein) + (1|generator) |
| P-value | Parametric bootstrap (1,000+ iterations under H0) alongside Kenward-Roger |
| Design | 14 proteins x ~7 generators (integration); incomplete crossing for MLFFs |
| Pre-registration | All choices locked on OSF before Phase 2 |

### 12.4 Delta (Benchmark)

| Component | Method |
|-----------|--------|
| Primary metric | WMSE (gates Spearman via hierarchical testing) |
| FDR | BH primary, BY sensitivity |
| Stratification | By cell type, perturbation type, expression level |
| Calibration | Reliability diagrams, ECE, against random baseline |
| Baselines | Linear, mean, PCA, random, persistence |

---

## 13. Go/No-Go Decision Points

| # | Date | Decision | Inputs | Outcomes |
|---|------|----------|--------|----------|
| D1 | May 9 | MLFF software GO | MACE + SO3LR installation | If NO: drop failed MLFF |
| D2 | June 30 | MLFF pilot GO | Phase 1 pilot data (G1-G6) | If NO: Alpha-M classical-only |
| D3 | June 6 | Delta scope lock | Method availability | Drop non-running methods |
| D4 | July 31 | Integration signal | Pilot analysis (G4) | If NO: separate publications |
| D5 | Aug 15 | Delta preprint | Figures + text | If MISS: 2-week extension |
| D6 | Aug 31 | **COMBINED PAPER** | All Phase 2 + pilot (T1-T6/S1-S5) | GO: NCS. NO-GO: separate |
| D7 | Sept 15 | Phase 3 scope | Phase 2 analysis | Select priority proteins for replicas |

---

## 14. Reviewer Attack Pre-emption

### 14.1 Anticipated NCS Reviewer Attacks (Combined Paper)

| Attack | Pre-emption |
|--------|-------------|
| "N=14 proteins is too small" | Pre-registered Bayesian analysis with JZS prior. Report BF, not p-values. Frame as "first evidence," not "proof." |
| "Per-residue analysis inflates N" | ICC estimation + hierarchical bootstrap. Report effective N alongside nominal N. |
| "BioEmu just emulates ff14SB" | Explicit bias chain section. Include Boltz-2 (no ff14SB bias) for comparison. |
| "The MLFF trajectories are too short" | Truncation protocol ensures fair comparison. Report trajectory length as a finding, not a limitation. |
| "Garnet is contaminated" | Dedicated contamination analysis section. Report clean vs contaminated results separately. |
| "Why not experimental dynamics?" | NMR S2 is experimental. The innovation is connecting experimental validation to fitness. |
| "This is just a correlation" | Bayesian analysis quantifies evidence strength. Four-prior sensitivity. Pre-registered predictions. |

### 14.2 Anticipated NatMeth Reviewer Attacks (Alpha-M)

| Attack | Pre-emption |
|--------|-------------|
| "MLFFs can't do proteins yet" | That IS the finding. Characterize exactly where the boundary is. |
| "Only 2 MLFFs is not comprehensive" | 10 generators total across 4 paradigms. MLFFs are 2 of 10. |
| "50 ns is not enough for convergence" | ICC convergence criterion. Report S2 at multiple checkpoints. |

### 14.3 Anticipated NatMeth Reviewer Attacks (Delta)

| Attack | Pre-emption |
|--------|-------------|
| "DL methods don't beat linear baselines" | Cite Ahlmann-Eltze. Test whether Tahoe-100M scale changes the answer. |
| "This is just scPerturBench on bigger data" | Calibrated metrics, difficulty stratification, cross-context evaluation are novel. |
| "VCC already did this" | VCC was a competition with gameable metrics. Delta is a neutral benchmark. |

---

## 15. Infrastructure Recommendations

### 15.1 Environment Management

9 separate conda environments required (env-mace, env-so3lr, env-garnet,
env-bioemu, env-boltz, env-alphaflow, env-classical, env-analysis, env-delta).
Version-pin ALL dependencies in YAML files committed to repository.

### 15.2 SLURM Job Management

- ~130 SLURM jobs for Phase 2 + ~90 for Phase 3
- Job arrays for classical FF runs
- Job dependencies for sequential phases
- Checkpoint/restart: every 2 ns (MLFF), every 10 ns (classical)
- NaN force monitoring with auto-kill + notification

### 15.3 Data Integrity

- MD5 checksums for all trajectory files
- JSON sidecar metadata per trajectory
- Weekly archive staging to tape
- Full reproducibility log (SLURM job IDs, node names, GPU indices, seeds)

---

## Appendix A: Bayesian Model Specification (Combined Paper)

```
# Likelihood
S2_R2_ij ~ Normal(mu_ij, sigma^2)
mu_ij = beta_0 + beta_1 * Fitness_Spearman_ij + u_i + v_j

# Priors (JZS default)
beta_1_standardized ~ Cauchy(0, 1)     # JZS default
beta_0 ~ Normal(0, 10)                  # Weakly informative intercept
u_i ~ Normal(0, sigma_protein^2)        # Protein random effect
v_j ~ Normal(0, sigma_generator^2)      # Generator random effect

# Hyperpriors
sigma_protein ~ Half-Cauchy(0, 0.5)
sigma_generator ~ Half-Cauchy(0, 0.5)
sigma ~ Half-Cauchy(0, 1)

# Sensitivity priors for beta_1
Prior 1 (JZS):        Cauchy(0, 1)           # Primary
Prior 2 (Skeptical):  Normal(0, 0.5^2)       # Skeptical reviewer
Prior 3 (Informative): Normal(0.5, 0.15^2)   # Proposal's original
Prior 4 (Flat):        Uniform(-1, 1)         # Referee-proof

# Decision rules
BF_10 > 3 under Prior 1 (JZS):   "Moderate evidence for integration"
BF_10 > 10 under Prior 1 (JZS):  "Strong evidence for integration"
BF_10 > 1 under Prior 2:         "Evidence survives skeptical prior"
```

Implementation: brms (R) or PyMC (Python) with Stan backend. Bridge
sampling for BF computation (Gronau et al., 2017).

---

## Appendix B: Portfolio Expected Value Calculation

```
Scenario                  P(scenario)  Impact  EV contribution
---------------------------------------------------------------
Combined NCS + Delta NM     0.24       18.0    4.32
Separate: AM(NM) + G(GR)
  + Delta(NM)               0.40       16.0    6.40
Separate: AM(NM) + G(null)
  + Delta(NM)               0.15       13.0    1.95
AM classical-only(JCTC)
  + Delta(NM)               0.12       10.0    1.20
Delays (AM 2027 + Delta
  delayed)                  0.07        6.0    0.42
Major failure               0.02        0.0    0.00
---------------------------------------------------------------
TOTAL                       1.00              14.29*

* Note: this differs from stratrev's 17.3 due to different scenario
  weighting. The range across reviewer models is 14.3-17.3.
```

---

*This implementation plan was produced by the ReviewCohort Orchestrator after
4 rounds of structured evaluation by 5 specialist reviewers. Total analytical
output: ~18,000 lines across 20 documents with 460+ unique citations.*

*The plan is designed to maximize expected publication impact while providing
clear decision points and kill criteria at every stage. The default-to-
separation strategy ensures that no single failure mode jeopardizes the
entire portfolio.*
