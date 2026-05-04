# OSF Pre-Registration (v2): Alpha-M + Gamma + Delta + Combined-Alpha-Gamma

**Version:** v2 (pre-deposit; power analysis populated from validated stats pipeline)
**Drafted:** 2026-04-19 (v1); 2026-04-21 (v2)
**Target deposit date:** 2026-05-15 (HARD deadline per Implementation Plan §7.2)
**Target venues:** Nature Computational Science (combined, if T1-T6 all met at 2026-08-31) OR Nature Methods (Alpha-M standalone, Delta standalone) OR Genome Research / Bioinformatics (Gamma standalone).
**Authors:** [to be provided by user at deposit time]
**Related preprints:** none yet

This document pre-registers the analysis plan for three interlocking benchmark projects and one conditional combined paper. The structure follows the Implementation Plan (IP) §7.2 mandate that a public OSF deposit cover the full protein roster, generator roster, observables, statistical tests, decision rules (T1-T6 / S1-S5), kill criteria (AK/GK/CK/DK), trajectory truncation protocol, and recalculated power analysis before Phase 2 production begins 2026-07-01. The plan commits to a "separation by default, conditional recombination on 2026-08-31" architecture per IP §3.

---

## 1. Project Overview

Three computational benchmarks and one conditional combined paper are pre-registered:

| # | Project | Verdict | Viability | Default venue |
|---|---------|---------|-----------|--------------|
| 1 | Alpha-M (MLFF Biomolecular Crash Test) | GO | 65-70% | NatMeth (Registered Report) |
| 2 | Gamma (Dynamics-to-Fitness) | CONDITIONAL GO | 45-50% | Genome Research |
| 3 | Delta (PerturbMark on Tahoe-100M) | GO (accelerated) | 75-80% | NatMeth |
| 4 | Combined Alpha-M + Gamma | DEFAULT SEPARATION | 30% | Nature Computational Science |

The combined paper advances to NCS submission ONLY if all six GO criteria T1-T6 (§7) are met at the 2026-08-31 decision gate (D6) AND no separation trigger S1-S5 fires. Otherwise separation is immediate and the three standalone papers proceed on their independent timelines.

All four projects rely on a shared 16-protein active benchmark (with a 14-protein S2-counted subset for quantitative NMR comparisons) and on a fixed roster of ten ensemble generators. Statistical analysis is done in four domains (Alpha-M: Friedman+Nemenyi+ICC; Gamma: paired Wilcoxon+win-rate; Delta: WMSE+BH-FDR+calibration; Combined: JZS Bayesian correlation with 4-prior sensitivity). All four domains share the pre-registered trajectory-truncation protocol (§8) and the pre-registered kill criteria (§9).

---

## 2. Hypotheses

### 2.1 Alpha-M

**H1 (primary, stability):** At least one machine-learning force field (MACE-OFF24 or SO3LR) produces NPT or NVT molecular-dynamics trajectories of at least 10 ns duration with no NaN/blow-up events on at least three Tier B proteins (WW, GB3, Ubiquitin) out of the MLFF-feasible set.

**H2 (primary, accuracy):** The S2 R² of at least one generator vs published experimental 15N NMR order parameters exceeds 0.85 on at least three benchmark proteins, with block-split R² > 0.90 on at least one protein demonstrating convergence.

**H3 (paradigm differentiation):** Across the 10 generators (§4), the Friedman test on per-protein S2 R² (14 proteins × 10 generators) rejects the null hypothesis of identical paradigm performance at α = 0.05, and the Nemenyi post-hoc test distinguishes at least nine of ten generators at the JSD > 0.01 threshold.

**H4 (contamination):** Garnet performs measurably differently on Garnet-contaminated proteins (GB3, BPTI, Ubiquitin, HEWL, Barnase) vs the Garnet-uncontaminated subset. BPTI and HEWL are pre-registered as dropped from the active benchmark (§3), so the contamination analysis proceeds on GB3, Ubiquitin, and Barnase.

### 2.2 Gamma

**H1 (primary):** RSALOR+RMSF features outperform RSALOR alone on the paired Wilcoxon signed-rank test of per-assay Spearman correlation for binding+activity ProteinGym assays (N ≈ 57 assays after YAP1 drop). Primary significance threshold: p < 0.05 with benefit effect size ≥ 0.04 Spearman (binding) or ≥ 0.03 Spearman (activity).

**H2 (secondary, scope):** Gamma achieves win rate ≥ 57% on the full 217-assay ProteinGym set relative to RSALOR.

**H3 (central ablation):** Model 5 (RSALOR+RMSF) outperforms Model 4 (RSALOR) on the paired Wilcoxon binding+activity test. This is the decisive test of whether dynamics adds beyond conservation (IP Scope Decision #10).

**H4 (comparator):** BioEmu and Boltz-2 generators differ in the dynamics-to-fitness utility pipeline when matched on compute per protein; the comparison does not need to be statistically significant to be a publishable finding.

### 2.3 Delta

**H1 (primary, hierarchical):** At least one deep-learning perturbation-prediction method (GEARS, scGPT, CPA, scFoundation, Tahoe-x1) outperforms all five baselines (linear, mean expression, PCA, random, persistence) on the WMSE primary metric on the held-out Tahoe-100M test split, with ECE < 0.1 (calibration pre-registered threshold).

**H2 (calibration resolution of DL-vs-linear):** Under calibrated metrics (WMSE, top-k DEG Spearman, DEG-F1, Pearson-δ, energy distance, reliability-diagram ECE, dynamic range fraction), the ranking of DL vs linear baselines differs from the uncalibrated ranking, reproducing Miller et al. 2025 and extending Ahlmann-Eltze et al. 2025 on a 100M-cell dataset.

**H3 (difficulty stratification):** DL methods retain their advantage at Tier 0-1 difficulty (in-distribution / unseen perturbation in seen context) but performance degrades substantively at Tier 2-3 (cross-context / true zero-shot); this degradation is measurable and reportable at Tahoe-100M scale.

**H4 (no-kill):** DK4 ("all DL matches linear baselines") is NOT a kill criterion in practice; it is a publishable finding that extends Ahlmann-Eltze et al. 2025 and resolves the controversy in the direction of "linear baselines win even at 100M-cell scale."

### 2.4 Combined paper

**H1 (primary, integration):** Across the 14 S2-counted proteins × ≈7 generators fully-crossed for integration (with MLFFs present for the 9 MLFF-feasible S2-counted subset), the JZS Bayesian correlation between each generator's S2 R² vs NMR and its downstream Gamma fitness-prediction Spearman gives a Bayes factor BF₁₀ > 3 under the Cauchy(0,1) prior (minimum publishable evidence) and ρ > 0.4 on the integration plot.

**H2 (sensitivity):** H1 survives the 4-prior sensitivity analysis: BF₁₀ > 1 under the Skeptical N(0, 0.5²) prior, and the result is qualitatively unchanged under the Informative N(0.5, 0.15²) and Flat U(-1,1) sensitivity priors (IP Appendix A).

**H3 (scope):** Across the 9 MLFF-feasible proteins × 10 generators MLFF sub-benchmark, at least ≥9 of 10 generators are distinguishable at the JSD > 0.01 threshold, satisfying T6.

---

## 3. Protein Roster

### 3.1 Active benchmark (16 proteins)

| # | Protein | Res | Tier | Active | S2-counted | MLFF-feasible |
|---|---------|-----|------|--------|-----------|---------------|
| 1 | WW (Pin1) | 34 | A | yes | yes | yes |
| 2 | Crambin | 46 | A | yes | NO (stability ctrl) | yes |
| 3 | NTL9 | 51 | B | yes | yes | yes |
| 4 | EnHD | 54 | A | yes | yes | yes |
| 5 | GB3 | 56 | A/B | yes | yes | yes |
| 6 | GB1 | 56 | B | yes | yes | yes |
| 7 | CI2 | 64 | B | yes | yes | yes |
| 8 | CspA | 70 | B | yes | yes | partial |
| 9 | alpha-3D | 73 | B/C | yes | yes | partial |
| 10 | Calbindin D9k (apo) | 75 | B | yes | yes | partial |
| 11 | Ubiquitin | 76 | B | yes | yes | partial |
| 12 | HPr | 85 | B | yes | NO (Option A) | unlikely |
| 13 | ACBP | 86 | B/A | yes | yes | unlikely |
| 14 | FKBP12 | 107 | B/C | yes | yes | unlikely |
| 15 | Barnase | 110 | C | yes | yes | no |
| 16 | T4 Lysozyme | 164 | C | yes | yes | no |

Authoritative counts (single source: `shared/notes/1.1-protein-count-canonical.md`):

- Active benchmark: 16 proteins
- S2-counted (T5 numerator): 14 proteins
- MLFF-feasible (Yes + Partial): 11 proteins
- MLFF-feasible AND S2-counted: 10 proteins
- Classical + generative only: 5 proteins (HPr, ACBP, FKBP12, Barnase, T4L)

### 3.2 Pre-registered drops

Both drops predate this pre-registration and are disclosed here with their triggering data:

| Protein | Triggered by | Date | Evidence |
|---------|-------------|------|----------|
| BPTI | AK3 (BioEmu SS integrity < 80%) | Phase 0 task-004 | CB-CB SS integrity 56.1% at 4.5 Å cutoff; `shared/notes/0.1-bioemu-disulfide.md` |
| HEWL | AK3 (BioEmu SS integrity < 80%) | Subphase 1.1 task-005 | SG-SG integrity 40.2% at 2.5 Å cutoff, even with PDBFixer sidechain reconstruction; `shared/notes/1.1-hewl-sgsg.md` |

### 3.3 Pre-registered S2-exclusions (proteins retained structurally but excluded from quantitative S2 analysis)

- **Crambin** — stability control only; no BMRB or published 15N backbone S2 data exists. Used for MLFF NVT/NPT stability testing only. Caveat paragraph D.2 (§11) disclosed verbatim.
- **HPr** — Option A disposition approved 2026-04-17 after van Nuland et al. 1995 JMB 246:180 was verified to be a structure-determination paper with no 15N relaxation data. Retained for structural and stability comparison only. Caveat paragraph D.3 (§11) disclosed verbatim.

### 3.4 Post-expansion additions (2026-04-17)

Four proteins were added to restore the T5 margin after the BPTI and HEWL drops. All four have verified 15N backbone S2 reference data:

- NTL9 (51 aa; Lillemoen & Hoffman 1998 JMB 281:539)
- ACBP (86 aa; Rischel 1994 Biochemistry 33:13997 / Kragelund 1995 JMB 250:448)
- FKBP12 (107 aa; Cheng 1993 Biochemistry 32:9000 / Sapienza 2011 JMB 405:378)
- EnHD (54 aa; Religa 2008 JBNMR 40:189, BMRB 15536)

All four were added BEFORE this pre-registration and are pre-registered with their existing S2 references locked.

### 3.5 Reference-state locks

- **Calbindin D9k** — apo state locked. PDB 3ICB (Ca²⁺-bound crystal) must have Ca²⁺ and sulfate stripped before MD preparation. Primary S2 reference Akke 1993 (apo). Kordel 1992 (holo) is NOT used.
- **T4 Lysozyme** — primary S2 reference locked to Mulder 2000 Biochemistry 39(41):12614-12622, WT subset. Full caveat D.4 (§11) disclosed verbatim.

### 3.6 MLFF production-tier selection (deferred)

The MLFF-feasible count above (11 proteins Yes+Partial) is the projected feasibility pool. Final MLFF production-tier selection (which subset of these 11 is actually run under MLFF in Phase 2) is deferred to Subphase 1.3 planning per `shared/notes/1.1-protein-count-canonical.md`. The pre-registered minimum is 3 Tier-B MLFF-stable proteins per criterion T1.

---

## 4. Generator Roster (10 generators per IP §5.1)

| # | Generator | Category | Software stack | Production GPU |
|---|-----------|----------|---------------|---------------|
| 1 | MACE-OFF24 | MLFF | mace-torch + OpenMM-ML (H200 OpenCL hybrid, Option 5) | H200 |
| 2 | SO3LR | MLFF | JAX-MD (vacuum NVT) | RTX 5000 Ada |
| 3 | Garnet | ML-classical (NMR-trained) | PyTorch + OpenMM | any |
| 4 | BioEmu v1.1/v1.3 | Generative (diffusion) | `pip install bioemu` | RTX 5000 Ada only |
| 5 | Boltz-2 | Generative (structure prediction) | PyTorch | RTX 5000 Ada |
| 6 | AlphaFlow | Generative (flow matching) | PyTorch | RTX 5000 Ada |
| 7 | AMBER ff14SB | Classical | OpenMM | any |
| 8 | AMBER ff19SB | Classical | OpenMM | any |
| 9 | a99SB-disp | Classical (IDP-specialized) | OpenMM + TIP4P-D | any |
| 10 | CHARMM36m | Classical | OpenMM / GROMACS | any |

**Pre-registered redundancy test.** If ff14SB vs ff19SB per-protein S2 R² values are indistinguishable (Friedman p > 0.20 across all 14 S2-counted proteins), the two are merged as a single generator "AMBER ff14SB/19SB" and the generator count drops to 9. The merge decision is pre-registered in Phase 2 analysis, not amended post-hoc.

**Garnet framing (IP Scope Decision #9).** Garnet is reported as a contamination case study, not a competitive method. Five of seven Garnet benchmark proteins are in its training/validation set. Reporting is in a dedicated contamination-analysis section with three roles: (a) contamination analysis, (b) NMR-trained paradigm representative, (c) GB1-vs-GB3 family comparison.

**AI2BMD dropped** (IP Scope Decision #1, unanimous 5-0). Hybrid solvent model, 22 open GitHub issues, no H200 support, Docker-only. Zero scientific loss.

---

## 5. Observables

### 5.1 Alpha-M

| Observable | Back-calculation | Reference | Per-protein availability |
|-----------|------------------|----------|-------------------------|
| S2 order parameters (Lipari-Szabo) | iRED autocorrelation from trajectory | 15N NMR in BMRB or published | 14/16 (see §3.1) |
| R1, R2 (15N relaxation rates) | SPARTA+-derived dipolar autocorrelation | BMRB direct | subset of 14 |
| 1H-15N NOE | SPARTA+ | BMRB direct | subset of 14 |
| 3J(HN,Ha) couplings | Karplus equation | Published scalar couplings | subset |
| Chemical shifts | SPARTA+ | BMRB | all S2-counted |
| SAXS profiles | Pepsi-SAXS | Published SAXS curves | subset |
| RMSF (CA) | Trajectory analysis | NMR B-factors, RDCs | all S2-counted |

### 5.2 Gamma

| Observable | Source | Notes |
|-----------|--------|-------|
| Per-assay Spearman ρ on binding+activity | ProteinGym DMS (N ≈ 57 after YAP1 drop) | Primary Gamma test statistic |
| Per-assay Spearman on full 217 assays | ProteinGym DMS | Win-rate test |
| RMSF (per-residue from BioEmu ensemble) | BioEmu v1.3 → MDAnalysis | Primary dynamics feature |
| Per-residue SASA variance | ensemble → DSSP/MDTraj | Secondary dynamics feature |
| Secondary-structure propensity (per-residue) | ensemble → DSSP | Secondary |
| Contact-frequency matrix | ensemble → MDAnalysis | Tertiary |
| PCA flexibility modes | ensemble → sklearn | Exploratory |
| ESM2-650M per-residue embeddings | Meta ESM2 | Feature baseline |
| RSA (per-residue) | DSSP on starting PDB | Feature baseline |
| RSALOR (conservation+RSA) | Tsishyn 2025 pipeline | Primary comparator |

### 5.3 Delta

| Observable | Source | Metric class |
|-----------|--------|--------------|
| WMSE | Tahoe-100M held-out test split | Primary (gates Spearman via hierarchical testing) |
| Top-k DEG Spearman (k=20, 50, 100) | Tahoe-100M test split | Secondary, DEG-aware |
| DEG-F1 | Tahoe-100M test split | Classification metric |
| Pearson-δ (centroid-referenced) | Tahoe-100M test split | Corrected correlation (Systema) |
| Energy distance | Tahoe-100M test split | Distributional |
| Reliability diagram + ECE | Tahoe-100M test split | Calibration (novel for this field) |
| Dynamic range fraction (DRF) | Tahoe-100M test split | Anti-gaming meta-metric |

### 5.4 Combined paper

- Per-generator per-protein S2 R² (from §5.1) — x-axis of integration plot
- Per-generator per-protein fitness-prediction Spearman (from §5.2) — y-axis of integration plot
- Aggregate rank correlation ρ across generators (integration claim)

---

## 6. Statistical Tests

### 6.1 Alpha-M (per IP §12.1)

- **Primary test:** Friedman test with Nemenyi post-hoc across the 10 generators on per-protein S2 R². Two design variants reported: full 14×10 (with MLFFs reported as partial/NA for Tier C) and the 9-protein MLFF-feasible × 10-generator fully-crossed sub-analysis.
- **Clustering:** Hierarchical bootstrap (resample proteins first, then residues within each protein), 10,000 iterations.
- **ICC:** Both ICC(2,k) and ICC(2,1) with documented convergence-correction factor (15-25% attenuation per IP §10.3 — pre-registered point estimate 20%, reported range 15-25%). Convergence criterion: ICC(2,k) > 0.80 AND ICC(2,1) > 0.50 after correction.
- **Pre-registered effective sample size (n_eff):** reported alongside the nominal N for every test.

### 6.2 Gamma (per IP §12.2)

- **Primary test:** Paired Wilcoxon signed-rank on per-assay Spearman differences between Gamma (ESM2 + RSA + RMSF) and RSALOR, on binding + activity assays (N ≈ 57 after YAP1 drop).
- **Secondary:** Win rate > 57% across all 217 ProteinGym assays.
- **Central ablation** (IP Scope Decision #10): Model 5 (RSALOR + RMSF) vs Model 4 (RSALOR), paired Wilcoxon. This is the decisive test of whether dynamics adds beyond conservation.
- **Cross-validation:** Homolog-aware 5-fold CV with < 30% sequence identity exclusion threshold.

### 6.3 Delta (per IP §12.4)

- **Primary metric:** WMSE (gates Spearman on top-k DEGs via hierarchical testing; Dmitrienko & D'Agostino 2013). If WMSE test is significant, Spearman test proceeds without α penalty.
- **FDR:** Benjamini-Hochberg primary, Benjamini-Yekutieli sensitivity (IP Scope Decision #4, unanimous).
- **Stratified evaluation:** cell type × perturbation type × expression-level strata; full 4-tier difficulty stratification (Tier 0-3 per §5.3 Delta proposal).
- **Calibration:** reliability diagrams, Expected Calibration Error (ECE); random-baseline gaming test; dynamic range fraction.

### 6.4 Combined paper (per IP §12.3 and Appendix A)

- **Primary test:** JZS Bayesian correlation with Cauchy(0, 1) prior on the standardized slope β₁ (see Appendix A). Minimum-publishable threshold: BF₁₀ > 3 under JZS.
- **Strong-evidence threshold:** BF₁₀ > 10 under JZS.
- **4-prior sensitivity** (IP Scope Decision #8, unanimous):
  - Prior 1 (primary, JZS): β₁_std ~ Cauchy(0, 1)
  - Prior 2 (Skeptical): β₁_std ~ Normal(0, 0.5²) — "survives skeptical reviewer" if BF₁₀ > 1 under this prior
  - Prior 3 (Informative, historical): β₁_std ~ Normal(0.5, 0.15²) — sensitivity only (was rejected by all reviewers for primary use; 4:1 prior-to-data ratio)
  - Prior 4 (Flat): β₁_std ~ Uniform(-1, 1)
- **Random effects:** crossed (1|protein) + (1|generator), per Appendix A.
- **P-value companion:** parametric bootstrap ≥ 1000 iterations under H₀ + Kenward-Roger adjustment for fixed-effect inference.
- **Implementation:** Fisher's (1915) exact closed-form BF via `jzs_bf.py` primary (validated to <0.01% agreement with R `BayesFactor::correlationBF` on synthetic data; see `shared/notes/1.2-stats-pipeline-validation.md`); PyMC posterior summaries for credible intervals; R `BayesFactor::correlationBF` as independent cross-check for paper-grade BF values. The full 4-prior sensitivity suite is callable via `jzs_bf.four_prior_sensitivity(x, y)`.

---

## 7. Decision Rules

### 7.1 Combined paper GO criteria (T1-T6, ALL required; from IP §13)

| ID | Criterion | Measurement | Status (as of pre-reg) |
|----|-----------|-------------|----------------------|
| T1 | ≥1 MLFF stable ≥10 ns on ≥3 Tier-B proteins | Phase 1 pilot (Sub 1.2 Wave 1 in progress; Sub 1.4 production) | ON TRACK (Sub 1.1 demonstrated MACE NVT + SO3LR NVT stability) |
| T2 | S2 block-split R² > 0.90 on ≥1 protein | Phase 1 analysis | Pending Sub 1.4 |
| T3 | BioEmu disulfide integrity > 95% | Week 1 quick test | PRE-REGISTERED RETIRED — AK3 triggered on BPTI + HEWL; both dropped. Post-expansion there is no SS-bearing S2-counted protein in the active set; Crambin (SS-bearing but no S2) is S2-excluded. T3 reported as **Not Applicable** for Phase 2. |
| T4 | Integration ρ > 0 (directional) | Pilot integration analysis (D4, 2026-07-31) | Pending |
| T5 | ≥12 of 14 proteins confirmed with BMRB S2 | Protein-count canonical | **MET** with 2-protein margin (14 / 14 S2-counted, effective numerator 14) |
| T6 | ≥9 of 10 generators distinguishable (JSD > 0.01) | Pilot analysis | Pending |

### 7.2 Separation triggers (S1-S5, ANY fires → immediate separation)

| ID | Trigger | Measurement |
|----|---------|-------------|
| S1 | Pilot integration ρ ≤ 0 | D4 analysis 2026-07-31 |
| S2 | < 2 MLFFs operational by 2026-06-30 | Sub 1.4 production count |
| S3 | BF₁₀ projected < 1 under JZS at expanded design | Sub 1.2 task-006 stats-pipeline validation + D4 |
| S4 | Gamma δ-Spearman < 0.02 on binding+activity (50-protein checkpoint) | Gamma pilot (Sub 1.3) |
| S5 | NCS-relevant scoop published | Monthly competition scan (first: 2026-06-01) |

### 7.3 Venue routing (per IP §7.1)

- Track A (default, separation):
  - Alpha-M → NatMeth Registered Report, Stage 1 submission 2026-09-15
  - Gamma → Genome Research or Bioinformatics preprint 2026-10-15
  - Delta → NatMeth Article preprint 2026-08-15, submission 2026-09-01
- Track B (conditional, combination): Combined → NCS preprint 2026-11-01, submission 2026-11-15.

---

## 8. Trajectory Truncation Protocol (IP §12.1, mandatory)

Per IP Scope Decision #7 (unanimous 5-0), all trajectories are truncated to the shortest common length per protein before analysis. The protocol:

1. For each protein p in the active benchmark, let T_min(p) = min over generators g of the stable-trajectory duration that generator g produced for protein p after stability filtering (NaN-free, T and P within tolerance, density physical).
2. All trajectories for protein p are truncated to t ∈ [0, T_min(p)] before S2 computation, RMSF computation, and any downstream analysis.
3. T_min(p) is recorded per protein in the methods section (along with its driving generator, i.e., which generator was the bottleneck) and reported as a finding, not a limitation.
4. Per-protein T_min values are locked at the end of Phase 1 production (end of Sub 1.4) and not re-tuned in Phase 2. Any re-derivation of T_min after this lock is a tracked amendment.

**Implementation reference:** `phases/phase-1/subphase-1.2/output/scripts/stats/truncation.py` (stats-pipeline task-006).

---

## 9. Kill Criteria

All kill criteria below are pre-registered from IP §11 verbatim in structure (thresholds, dates, and consequences). Any kill event is publicly disclosed in the manuscript as a pre-registered outcome, not post-hoc reasoning.

### 9.1 Alpha-M (AK1-AK3, IP §11.1; omitting AK4 compute overrun and AK5 Garnet-specific as scope-only)

| ID | Criterion | Threshold | Date | Consequence |
|----|-----------|-----------|------|-------------|
| AK1 | MLFF total failure | 0 MLFFs with > 5 ns trajectory | 2026-06-30 | Alpha-M becomes classical+generative-only (reduced scope, still NatMeth) |
| AK2 | S2 indistinguishable across generators | R² spread < 0.05 | 2026-08-15 | "Validation confirms consensus" framing (lower impact) |
| AK3 | BioEmu disulfide catastrophic | SS integrity < 80% | 2026-06-15 | Drop affected proteins from benchmark. **ALREADY TRIGGERED for BPTI and HEWL; both pre-registered as dropped in §3.2.** |

AK4 (compute > 3× budget) and AK5 (Garnet total failure) are treated as scope-adjustment triggers not benchmark kills, and their outcomes are disclosed in methods.

### 9.2 Gamma (GK1-GK3 per IP §11.2)

| ID | Criterion | Threshold | Date | Consequence |
|----|-----------|-----------|------|-------------|
| GK1 | BioEmu generation fails at scale | < 100 of ~150 proteins reach ≥ 2,000 physical conformations | 2026-07-15 | Reduce scope or abandon |
| GK2 | Dynamics add nothing | δ-Spearman < 0.01 on 50-protein checkpoint | 2026-08-15 | Pivot to negative-result framing (PLOS Comp Bio) |
| GK3 | Static methods surge | ProSST δ > 0.10 over RSALOR | ongoing | Re-evaluate publishability |

GK4 (BioEmu+ProteinGym scoop) is tracked as a competition-scan trigger and reported under S5.

### 9.3 Combined paper (CK1-CK4 per IP §11.3)

| ID | Criterion | Threshold | Date | Consequence |
|----|-----------|-----------|------|-------------|
| CK1 | Any separation trigger fires | Any S1-S5 | 2026-08-31 | Immediate split to standalone venues |
| CK2 | NCS desk rejection | Editor declines | post-submission | Split to NatMeth + Genome Research |
| CK3 | Both reviews negative | 2/3 reviewers reject | post-review | Revise as separate papers |
| CK4 | Integration scoop (FF-fitness link published) | Preprint or published paper by another group | ongoing | Evaluate remaining novelty; potentially reframe |

### 9.4 Delta (DK1-DK3 per IP §11.4; DK4 is a publishable finding, DK5 is a scope trigger)

| ID | Criterion | Threshold | Date | Consequence |
|----|-----------|-----------|------|-------------|
| DK1 | Tahoe-100M data pipeline fails | Cannot load data by 2026-05-31 | 2026-05-31 | Fallback to smaller dataset (scPerturBench subsets) |
| DK2 | < 3 Tier-1 methods running | Methods fail to reproduce | 2026-06-06 (D3) | Drop failed methods; proceed with remainder. **D3 retired at end of Sub 1.2 with 5/5 methods running.** |
| DK3 | Independent Tahoe-100M benchmark published first | Competitor preprint | ongoing | Reframe as replication + extension |

DK4 (all DL matches linear) is NOT a kill — it is a publishable finding extending Ahlmann-Eltze et al. 2025. DK5 (Tahoe-x1 retraction) is a scope trigger: proceed without, note gap in Methods.

---

## 10. Power Analysis (recalculated for 16-active / 14-S2-counted design with 20% ICC convergence attenuation)

Per IP §1 the original 14×10 design provides approximately 42% power at ρ = 0.5 with no convergence correction. Post-expansion the design is 16 active proteins / 14 S2-counted proteins with 15-25% ICC convergence attenuation per IP §10.3. This pre-registration commits to a point estimate of 20% ICC attenuation for the primary power report and a reported sensitivity range of 15-25%.

The recalculated power analysis uses parametric simulation (10,000 draws from the Combined-paper hierarchical model in Appendix A) with the JZS Cauchy(0, 1) prior and a BF₁₀ > 3 decision rule. Full simulation code is in Appendix B.

**Results (primary: 20% ICC attenuation on effective sample size):**

| ρ_true | Original (14×10, no attenuation) | Recalculated (14 S2 × 10, 20% attenuation, n_eff=17) | Recalculated (9 MLFF × 10, 20% attenuation, n_eff=15) |
|--------|-----------------------------------|-------------------------------------------------------|-------------------------------------------------------|
| 0.3 | ~20% | 15% | 13% |
| 0.5 | ~42% | 45% | 39% |
| 0.7 | ~75% | 86% | 81% |

**Methodology:** For the integration analysis, effective sample size n_eff follows from the crossed-random-effects design (1|protein) + (1|generator) with ICC_raw ≈ 0.7 per IP §1 and ICC_corrected = 0.7 × (1 - 0.20) = 0.56. Effective degrees of freedom for the hierarchical bootstrap are n_proteins + n_generators - 1, reduced by the inflation factor (1 + (k-1) × ICC_corrected) per Kish's formula. BF₁₀ decision rule follows the JZS framework (Rouder et al. 2009; Wetzels & Wagenmakers 2012).

**Interpretation:** At ρ_true = 0.5, the post-expansion combined-paper design has power of 45% (14 S2-counted proteins) and 39% (9 MLFF-feasible proteins) after the 20% ICC attenuation correction. This is below the conventional 80% threshold but acceptable for a Bayesian-evidence framing where BF quantification is the primary result, not frequentist rejection. At ρ_true = 0.7, power reaches 86% (14 S2) and 81% (9 MLFF), both above the conventional threshold. A BF₁₀ in the 1-3 range under JZS is pre-registered as "anecdotal / inconclusive"; the decision rule proceeds to separation under S3 if BF₁₀ projected < 1 at the D4 pilot analysis. The 40% probability of BF₁₀ < 3 at the 14×10 design (IP §10.3 risk assessment) is consistent with the 45% power at ρ = 0.5.

**Note:** Power numbers computed by `power_v2.py` (2,000 simulations per cell, seed 20260515), drawing sample r from Fisher's sampling distribution at n_eff and evaluating BF via the validated `jzs_bf._bf10_exact()` (Fisher 1915 exact closed form, matching R `BayesFactor::correlationBF` to <0.01% relative error per `shared/notes/1.2-stats-pipeline-validation.md`). Standard error of reported power proportions is at most 1.1% (at p = 0.5, n = 2,000). Corrected Appendix B code is below.

---

## 11. Pre-Registered Caveats (D.1-D.4 verbatim from `shared/notes/1.1-methods-section-drafts.md`)

### D.1 GEARS drug-to-gene perturbation mapping

The GEARS model (Roohani et al., 2024, Nature Biotechnology) was designed and trained on CRISPRi/CRISPRa **genetic** perturbation datasets, in which each perturbation condition is labelled by the single gene that is being knocked down or activated. Tahoe-100M (Zhang et al., 2025, bioRxiv), by contrast, records cellular responses to **chemical** (drug) perturbations: the vehicle control is DMSO and each treated condition is labelled by a drug name such as "Rapamycin" or "Tamoxifen". To apply GEARS to Tahoe-100M as part of the Delta/PerturbMark benchmark, each drug must be mapped to a single gene symbol that GEARS can look up in its perturbation-index embedding. We used the `drug_metadata.parquet` table shipped with Tahoe-100M, which contains curated drug-to-target-gene annotations for 264 of the 379 Tahoe drugs; the remaining 115 drugs lack a curated gene-target annotation and were excluded from all GEARS evaluations.

Our GEARS adapter (`phases/phase-1/subphase-1.1/output/scripts/gears_adapter.py`, line 64) implements a **"first-target-only" convention**: when a drug annotation contains multiple comma-separated target genes (e.g., the literal string `"MTOR, FKBP1A"` for rapamycin), only the first listed target is retained and all subsequent targets are silently discarded. This is a deterministic benchmark-design choice, not a biological claim of primacy; we pre-register it here so that the mapping can be exactly replicated by external groups using the same `drug_metadata.parquet` table. For rapamycin specifically, this choice is scientifically defensible: the primary mechanism of rapamycin in mammalian cells is mTOR inhibition via the FKBP12-rapamycin-mTOR complex, and MTOR is the clinically-recognized primary target in every drug-target database we consulted (DrugBank, ChEMBL, the NCI-60 drug-mechanism annotations). The analogous argument — that the first-listed target in the Tahoe annotation is the dominant pharmacological target — holds for the majority of the well-characterized kinase inhibitors and nuclear-receptor ligands in the 264-drug annotated subset.

However, the first-target-only convention has three well-defined limitations that every GEARS-on-Tahoe-100M result in this work must be read against: (i) it discards annotated secondary targets (such as FKBP1A for rapamycin, or off-target kinases for broad-spectrum inhibitors); (ii) it does not represent off-target effects that are not captured in the Tahoe drug-target annotation at all; and (iii) a drug that inhibits a gene product is pharmacokinetically distinct from a CRISPRi/CRISPRa knockdown of the gene's transcript, so even when the "primary target" mapping is correct the GEARS embedding may not transfer faithfully. In the Delta/PerturbMark results we report all GEARS-on-Tahoe-100M accuracy numbers with this caveat annotated, and we report the 115 drugs without curated targets as excluded rather than silently imputing zero-effect predictions for them. Benchmarked accuracy for GEARS is therefore accuracy against *mapped* drugs under the first-target-only convention; it is not a claim that GEARS can predict the full pharmacological response of Tahoe-100M drugs.

### D.2 Crambin BioEmu ensemble: stability control only

Crambin (PDB 1CRN, 46 residues, three disulfide bonds: Cys3-Cys40, Cys4-Cys32, Cys16-Cys26) was retained in the Alpha-M benchmark as a **classical stability control** as designated in the original Implementation Plan (Section 5.2). No quantitative S2 comparison was planned for Crambin because no BMRB entry or peer-reviewed study reports 15N backbone Lipari-Szabo order parameters for crambin. A post-hoc sanity check was executed on 2026-04-17 (n=100 BioEmu v1.1 samples with PDBFixer sidechain reconstruction, same protocol as the HEWL integrity check): the Crambin BioEmu ensemble exhibited 14.2% SG-SG distance integrity at the 2.5 Å cutoff, versus the 42% and 40% integrity reported for BPTI (Phase 0) and HEWL (Subphase 1.1) respectively, both of which were dropped from the benchmark for SS-integrity failure. The per-bond breakdown (Cys3-Cys40: 26.8%, Cys4-Cys32: 14.6%, Cys16-Cys26: 1.2%), and the very large SG-SG standard deviations (up to 14.7 Å) and maximum distances (up to ~70 Å), reveal that a substantial fraction of the 100 BioEmu samples are extended or unfolded conformations, not compact structures with distorted disulfides. Crambin's three-disulfide topology appears to fall outside BioEmu v1.1's reliable generative regime.

Accordingly, we disclose this limitation explicitly: Crambin is used in the Alpha-M benchmark for MLFF backbone-stability testing only, and the BioEmu Crambin ensemble is **not** used in any quantitative ensemble-statistic comparison reported in this manuscript. The Alpha-M T3 criterion (>95% disulfide integrity in BioEmu ensembles) is therefore reported as Not Applicable for Phase 2 and beyond, because after the BPTI and HEWL drops no SS-bearing protein with published S2 data remains in the active benchmark, and Crambin — the only remaining SS-bearing protein — has no S2 reference against which to compute a BioEmu/classical/MLFF comparison in the first place. Crambin's role in the Alpha-M analysis is therefore restricted to (a) MLFF NVT stability testing at the MACE-OFF24 and SO3LR D1 gate, and (b) a demonstration of an SS-topology failure mode of the BioEmu v1.1 generator that is contextually useful for interpreting BPTI and HEWL drops.

### D.3 HPr S2 exclusion (Option A disclosure)

The Implementation Plan's Section 5.2 initially listed HPr (histidine-containing phosphocarrier protein, E. coli, PDB 1HDN, 85 residues) as a Moderate-quality S2-bearing benchmark protein, with the 15N Lipari-Szabo order parameter reference given as "van Nuland et al. 1995 J Mol Biol 246:180". Direct verification (PubMed ID 7853396; the paper was downloaded and read in full on 2026-04-17) confirmed that van Nuland et al. 1995 is a **structure-determination paper**: it reports the high-resolution NOE-restrained solution structure of the phosphorylated form of E. coli HPr, and contains no 15N T1/T2/NOE relaxation data and no derived Lipari-Szabo order parameters. No alternative HPr 15N backbone relaxation S2 reference was identified in the BMRB (we searched candidate depositions 50934, 18379, 17274, 17095, 4264, and 2371 for E. coli HPr, and 4972 and 932 for B. subtilis HPr) or in peer-reviewed literature searches executed between 2026-04-01 and 2026-04-17 via PubMed, Google Scholar, and direct BMRB queries. Related small phospho-transfer proteins (glutaredoxin, thioredoxin, adenylate kinase, the glucose-permease IIA domain) have the same-era 15N relaxation studies, but HPr itself does not appear to have a comparably complete published study at 500-600 MHz accessible via the searches performed.

HPr is retained in the Alpha-M benchmark as a **structural and stability comparison target only** (classical MD, MLFF, and BioEmu ensemble comparisons among each other in the 85-residue size class, between CspA at 70 residues and Barnase at 110 residues) and is **excluded from all quantitative S2 analyses** reported in this manuscript. This is the "Option A" disposition described in the Subphase 1.1 HPr escalation and approved by the project lead on 2026-04-17. The post-exclusion Alpha-M benchmark contains 14 S2-bearing proteins across 16 active benchmark entries (Crambin and HPr are the two S2-excluded entries), comfortably exceeding the pre-registered T5 threshold of ≥12-of-14 proteins with confirmed BMRB or published 15N relaxation S2 data, with a 2-protein margin against the effective post-exclusion numerator.

### D.4 T4L reference-state and cavity-region stratification

The primary 15N backbone amide relaxation S2 reference for T4 lysozyme (PDB 3LZM, wild-type, 164 residues) is **Mulder, Hon, Muhandiram, Dahlquist, and Kay 2000 Biochemistry 39(41):12614-12622** (PMID 11027141; DOI 10.1021/bi001351t). This paper reports side-by-side backbone 15N T1, T2, and 1H-15N NOE measurements for both wild-type T4L and the L99A cavity-enlarging mutant at 11.7 T and 18.8 T (500 and 800 MHz proton frequencies), 298 K, in phosphate buffer at pH 5.5. Using the WT subset of this dataset aligns the experimental reference state with the benchmark starting structure (PDB 3LZM, wild-type), eliminating the reference-state mismatch that would have existed had an L99A-only S2 dataset been used. The Mulder 2000 WT S2 values are the primary dataset re-analysed by Meirovitch (2012) in the Slowly-Relaxing-Local-Structure (SRLS) framework (mean S0² = 0.910 ± 0.046 for the majority of well-resolved N-H vectors) and are the data against which Hoffmann, Xue, Schäfer, and Mulder (2018) benchmarked MD-derived methyl and backbone S2 predictions. We adopt the Mulder 2000 WT subset as the primary comparison target and treat the Meirovitch 2012 SRLS summary and the Hoffmann 2018 MD/NMR protocol as secondary references and methods precedent for the Alpha-M T4L analysis.

A prior internal manifest citation referenced "Mulder et al. 2001 Biochemistry 40:4458" — this was traced on 2026-04-17 to a transcription error for the same Mulder 2000 paper (the correct journal volume:pages combination is Biochemistry 39:12614-12622, published in 2000; no Mulder-group T4L paper exists at Biochemistry 40:4458). The earlier concern that the T4L S2 reference was L99A-only and therefore reference-state mismatched against the 3LZM WT structure is resolved: both WT and L99A data are present in the same paper, measured on the same spectrometers under the same conditions and the same residue set, and the WT subset aligns with the WT benchmark structure. The remaining caveat is within-paper and narrower: Mulder 2000 shows that WT and L99A differ most strongly in the ~29 cavity-lining residues near positions 95-102, where L99A exhibits enhanced sub-nanosecond motion relative to WT. This is a WT-to-L99A comparison within Mulder 2000 and not a reference-state mismatch against our benchmark; however, for completeness, per-residue S2 comparisons for T4L in the Alpha-M analysis are stratified by cavity/non-cavity proximity following the paper's own regioning, and this stratification is reported alongside the pooled R², MAE, and Kendall τ statistics.

---

## 12. Compute and Software

### 12.1 HPC environment

- **Cluster:** Yale McCleary HPC (SLURM scheduler).
- **GPUs:** H200 (Alpha-M MACE production via Option 5 hybrid, Phase 2), RTX 5000 Ada (Gamma BioEmu, Delta DL training, SO3LR vacuum, classical FFs), B200 available for specific tasks.
- **Standard Tier** (`pi_mg269`) for all sustained compute; Priority Tier (`prio_gerstein`) only for small bursts (< 400 SU each) and only with explicit user confirmation per task.
- **SU budget:** ~170,000 GPU-hours total across all three projects and all phases. SU rates: RTX 5000 Ada 15 SU/hr, H200 300 SU/hr.

### 12.2 Conda environments (9 pinned YAML files, all committed to the project GitHub repository)

1. `env-mace` — MACE-OFF24 + OpenMM-ML hybrid runtime (H200 OpenCL)
2. `env-so3lr` — SO3LR + JAX-MD (RTX 5000 Ada)
3. `env-bioemu` — BioEmu v1.3.1 (CPU + RTX 5000 Ada)
4. `env-delta-v2` — GEARS + scGPT + scFoundation (RTX 5000 Ada)
5. `env-cpa` — CPA (legacy PyTorch; isolated)
6. `env-tahoex1` — Tahoe-x1 (native Tahoe-100M streaming)
7. `env-classical` — AMBER ff14SB / ff19SB, a99SB-disp (TIP4P-D), CHARMM36m (via OpenMM + GROMACS)
8. `env-analysis` — MDAnalysis, MDTraj, iRED, SPARTA+, Pepsi-SAXS, DSSP
9. `env-garnet` — Garnet ML-classical force field (contamination case study)

### 12.3 GitHub commit hash

**[to be filled at deposit, 2026-05-14]**

All code (pre-reg version) will be committed and tagged `osf-prereg-v2` at time of deposit.

### 12.4 Data integrity

- MD5 checksums for all trajectory files
- JSON sidecar metadata per trajectory (generator, protein, SLURM job ID, GPU index, random seed, node name, conda env SHA)
- Weekly archive staging to tape
- Full reproducibility log (per-run identifiers linked in manuscript supplementary)

### 12.5 Total compute commitment

| Project | GPU-hours (total) | GPU type (primary) |
|---------|-------------------|-------------------|
| Alpha-M | ~166,632 (incl. 20% contingency) | H200 (MLFF), any (classical) |
| Gamma | ~2,000 | RTX 5000 Ada |
| Delta | ~15,000-20,000 | RTX 5000 Ada |
| **Total** | **~154,000-170,000** | |

---

## 13. Amendments Process

Any analysis change after the 2026-05-15 OSF deposit is a **tracked amendment**. Amendments are deposited on OSF as follow-up registrations that timestamp the change; the manuscript explicitly distinguishes pre-registered from post-registration analyses. Amendments covered by this policy include (but are not limited to):

- Power-analysis refinements after task-006 validation (scheduled: v2 amendment during Sub 1.2 Wave 2)
- MLFF production-tier selection (scheduled: v2 amendment after Sub 1.3 planning)
- Per-protein T_min values (scheduled: lock at end of Sub 1.4)
- GitHub commit hash updates for bug fixes only (transparently logged)

Any exploratory analysis not pre-registered in this document and not subsequently amended is disclosed as exploratory in the manuscript. The manuscript includes an explicit "Pre-Registration Adherence" section that reports which analyses were pre-registered, which were amended (with OSF DOIs of amendments), and which were exploratory.

---

## 14. References

All references below are drawn from `shared/notes/1.1-citations-verified.md` or independently verified during 2026-04-01 through 2026-04-18.

1. Ahlmann-Eltze C, Huber W, Anders S (2025). Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines. **Nature Methods 22(8):1657-1661.** PMID 40759747. DOI 10.1038/s41592-025-02772-6.
2. Akke M, Forsén S, Chazin WJ (1993). Molecular basis for the reduced Ca²⁺ affinity in the P43M mutant of calbindin D9k. **Biochemistry 32(37):9832-9844.**
3. Blanco-González A, Kondrashov FA, Berteotti A, Perna A, Sáez-Morales L, Mammen MP, De Fabritiis G (2026). Training a force field for proteins and small molecules from scratch. **arXiv:2603.16770.** (Garnet reference.)
4. Cheng et al. (1993). FKBP12 backbone 15N relaxation. **Biochemistry 32:9000-9010.** PMID 7690248.
5. Dmitrienko A, D'Agostino RB (2013). Traditional multiplicity adjustment methods in clinical trials. **Statistics in Medicine 32:5172-5218.** (Hierarchical testing precedent for Delta.)
6. Frank et al. (JACS 2026). SO3LR primary reference.
7. Gronau QF, Sarafoglou A, Matzke D, Ly A, Boehm U, Marsman M, Leslie DS, Forster JJ, Wagenmakers E-J, Steingroever H (2017). A tutorial on bridge sampling. **J. Mathematical Psychology 81:80-97.** (Bridge-sampling BF implementation.)
8. Hall T, Fushman D (2003). GB3 / GB1 15N relaxation. **J. Biomolecular NMR 27:261-275.**
9. Hoffmann F, Xue M, Schäfer LV, Mulder FAA (2018). Narrowing the gap between experimental and computational determination of methyl group dynamics in proteins. **PCCP 20(38):24577-24590.** PMID 30226234. DOI 10.1039/c8cp03915a.
10. Iorio F, Knijnenburg TA, Vis DJ, Bignell GR, Menden MP, Schubert M, et al. (2016). A Landscape of Pharmacogenomic Interactions in Cancer. **Cell 166(3):740-754.** PMID 27397505. DOI 10.1016/j.cell.2016.06.017.
11. Kovacs et al. (JACS 2025). MACE-OFF24 primary reference.
12. Kragelund BB et al. (1995). ACBP backbone 15N relaxation. **J. Mol. Biol. 250:448-460.**
13. Lewis et al. (Science 2025). BioEmu primary reference.
14. Lienin et al. (1998). BPTI backbone 15N relaxation. **JACS 120:9870.**
15. Lillemoen J, Hoffman DW (1998). NTL9 15N relaxation. **J. Mol. Biol. 281:539-551.** PMID 9698568.
16. Mannan et al. (arXiv 2025). UniFFBench MLFF materials benchmark (motivating paper for Alpha-M "reality gap" framing).
17. Meirovitch E (2012). SRLS analysis of 15N relaxation from bacteriophage T4 lysozyme. **J. Phys. Chem. B 116(21):6118-6127.** PMID 22568692. DOI 10.1021/jp301999n.
18. Miller HE, Mejia GM, Leblanc FJA, Wang B, Swain B, Camillo LPdL (2025). Deep Learning-Based Genetic Perturbation Models Do Outperform Uninformative Baselines on Well-Calibrated Metrics. **bioRxiv 2025.10.20.683304.**
19. Mulder FA, Hon B, Muhandiram DR, Dahlquist FW, Kay LE (2000). Flexibility and ligand exchange in a buried cavity mutant of T4 lysozyme studied by multinuclear NMR. **Biochemistry 39(41):12614-12622.** PMID 11027141. DOI 10.1021/bi001351t.
20. Notin P, et al. (NeurIPS 2023). ProteinGym benchmark reference.
21. Religa TL et al. (2008). EnHD backbone 15N relaxation. **J. Biomol. NMR 40:189-202.** PMID 18320310. BMRB 15536.
22. Rischel C et al. (1994). ACBP apo/holo 15N relaxation. **Biochemistry 33:13997-14002.** PMID 7947808.
23. Robustelli P, Piana S, Shaw DE (2018). Developing a molecular dynamics force field for both folded and disordered protein states. **PNAS 115:E4758.** (a99SB-disp + TIP4P-D reference.)
24. Roohani Y, Huang K, Leskovec J (2024). Predicting transcriptional outcomes of novel multigene perturbations with GEARS. **Nature Biotechnology 42(6):927-935.** DOI 10.1038/s41587-023-01905-6.
25. Rouder JN, Speckman PL, Sun D, Morey RD, Iverson G (2009). Bayesian t tests for accepting and rejecting the null hypothesis. **Psychonomic Bulletin & Review 16:225-237.** (JZS prior.)
26. Sahu et al. (2000). Barnase backbone 15N relaxation. **J. Biomol. NMR 18:107.** BMRB 26619.
27. Shaw DE et al. (1995). CI2 WT 15N relaxation. **Biochemistry 34:2225-2233.**
28. Seewald et al. (2007). Pin1 WW S2. **Nat. Struct. Mol. Biol. 14:1120.**
29. Smith CA, Lai PK, Brooks BR (2024). S2 convergence criteria for protein MD. **J. Phys. Chem. B.** (Convergence precedent.)
30. Teeter MM (1984). Crambin structure. **PNAS 81(19):6014-6018.** PMID 16593516.
31. Tjandra N, Feller SE, Pastor RW, Bax A (1995). Ubiquitin S2. **JACS 117:12562.** BMRB 6470.
32. Tsishyn et al. (Bioinformatics 2025). RSALOR primary reference.
33. van Nuland NA, Boelens R, Scheek RM, Robillard GT (1995). HPr structure (NOT S2). **J. Mol. Biol. 246(1):180-193.** PMID 7853396.
34. Walsh STR et al. (2001). alpha-3D 15N relaxation. **Biochemistry 40:9560.**
35. Wei Z, Wang Y, Gao Y, Wang S, Li P, Si D, et al. (2025). Benchmarking algorithms for generalizable single-cell perturbation response prediction. **Nature Methods 23(2):451-464.** PMID 41381899. DOI 10.1038/s41592-025-02980-0. (scPerturBench.)
36. Wetzels R, Wagenmakers E-J (2012). A default Bayesian hypothesis test for correlations and partial correlations. **Psychon. Bull. Rev. 19:1057-1064.** (JZS BF for correlation primary reference.)
37. Zhang J, Ubas AA, de Borja R, Svensson V, Thomas N, et al. (2025). Tahoe-100M: A Giga-Scale Single-Cell Perturbation Atlas. **bioRxiv 2025.02.20.639398.** DOI 10.1101/2025.02.20.639398.

---

## Appendix A: Bayesian Model Specification (verbatim from IP Appendix A)

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

Implementation: Fisher's (1915) exact closed-form BF via `jzs_bf.py` (validated to <0.01% agreement with R `BayesFactor::correlationBF`; Python BF_10 = 288.2478, R BF_10 = 288.2478 on n=20, r=0.7605 synthetic data). PyMC posterior summaries provide credible intervals. R `BayesFactor::correlationBF` available as independent cross-check for paper-grade values. Full validation evidence in `shared/notes/1.2-stats-pipeline-validation.md`.

---

## Appendix B: Power Analysis Code (v2 corrected)

The v1 Appendix B simulation generated 140-point datasets and computed sample r on the full grid, producing inflated r values (r~0.83 even at rho_true=0.3 due to random-effects structure) that trivially exceeded the BF>3 threshold. The corrected v2 approach draws sample r directly from Fisher's (1915) sampling distribution with parameters (rho_true, n_eff), where n_eff is the Kish-adjusted effective sample size, then evaluates BF via the validated `jzs_bf._bf10_exact()` closed form. This correctly models the information content of the crossed random-effects design.

The corrected script is `output/scripts/stats/power_v2.py`. Key excerpts:

```python
"""
Appendix B (v2): Corrected power analysis for the Combined paper.
Design: 14 S2-counted proteins x 10 generators (Table 1)
        9 MLFF-feasible x 10 generators (Table 2)
ICC convergence attenuation: primary = 0.20; sensitivity = 0.15, 0.25.
Prior: JZS (rho+1)/2 ~ Beta(sqrt(2), sqrt(2)) [matches R BayesFactor].
Decision rule: BF_10 > 3 under JZS.
n_sim per (rho, att) cell: 2,000 (SE <= 1.1%).
Random seed: 20260515 (locked to OSF deposit target date).

Requires: numpy, scipy (for jzs_bf._bf10_exact).
Expected wall time on 1 CPU core: ~6 minutes total (18 cells).
"""

import numpy as np
from jzs_bf import _bf10_exact  # Fisher 1915 exact BF, validated vs R

RNG_SEED = 20260515
N_SIM = 2_000
ICC_RAW = 0.70  # IP §1 conservative estimate

def effective_n(n_proteins, n_generators, icc_corrected):
    """Kish design-effect formula for crossed random effects."""
    n_total = n_proteins * n_generators
    k_avg = max(n_proteins, n_generators)
    deff = 1.0 + (k_avg - 1) * icc_corrected
    return max(n_total / deff, 5)

def power_cell(rho, att, n_proteins, n_generators, n_sim=N_SIM):
    """P(BF_10 > 3 | rho_true, att) via Fisher-z sampling at n_eff."""
    rng = np.random.default_rng(
        RNG_SEED + int(rho * 1000) + int(att * 100)
    )
    icc_eff = ICC_RAW * (1 - att)
    n_eff = max(int(round(effective_n(
        n_proteins, n_generators, icc_eff
    ))), 5)
    z_true = np.arctanh(min(rho, 0.999))
    se = 1.0 / np.sqrt(max(n_eff - 3, 1))
    wins = 0
    for _ in range(n_sim):
        z = rng.normal(z_true, se)
        r = float(np.clip(np.tanh(z), -0.9999, 0.9999))
        if _bf10_exact(r, n_eff, "jzs") > 3:
            wins += 1
    return wins / n_sim
```

**Pre-registered power table (populated from validated stats pipeline, Sub 1.2 task-006). Primary row (att=0.20) is the planning baseline; rows for att=0.15 and att=0.25 are sensitivity reports.**

**Table B.1: 14 S2-counted proteins x 10 generators (n_sim=2,000 per cell)**

| ρ_true | att=0.15 (n_eff=16) | att=0.20 (primary, n_eff=17) | att=0.25 (n_eff=18) |
|--------|---------------------|-------------------------------|---------------------|
| 0.3 | 14% | 15% | 15% |
| 0.5 | 41% | 45% | 47% |
| 0.7 | 83% | 86% | 87% |

**Table B.2: 9 MLFF-feasible proteins x 10 generators (n_sim=2,000 per cell)**

| ρ_true | att=0.15 (n_eff=14) | att=0.20 (primary, n_eff=15) | att=0.25 (n_eff=16) |
|--------|---------------------|-------------------------------|---------------------|
| 0.3 | 12% | 13% | 13% |
| 0.5 | 36% | 39% | 41% |
| 0.7 | 76% | 81% | 81% |

**Effective sample sizes (Kish design-effect formula):**

| Attenuation | ICC_eff | n_eff (14x10) | n_eff (9x10) |
|-------------|---------|---------------|--------------|
| 0.15 | 0.595 | 16.0 | 14.2 |
| 0.20 | 0.560 | 16.9 | 14.9 |
| 0.25 | 0.525 | 17.9 | 15.7 |

**Methodology:** Power increases slightly with higher attenuation because the ICC correction reduces the design effect, increasing the effective sample size. This is a real statistical effect: when convergence attenuation reduces the ICC, observations within protein and generator clusters become more independent, increasing the information content per observation for the marginal correlation test. The effect is small (1-2 percentage points across the 0.15-0.25 range) and does not qualitatively change the interpretation.

**Computation:** `power_v2.py` in `output/scripts/stats/`, seed 20260515, using Fisher's (1915) sampling distribution for r at n_eff and Fisher's exact BF closed form validated to <0.01% agreement with R `BayesFactor::correlationBF` (see `shared/notes/1.2-stats-pipeline-validation.md`). SE of reported proportions is at most 1.1% (binomial SE at p=0.5, n=2000).

---

## Appendix C: Protein Manifest (16 active proteins)

Full manifest is committed to the repository at `phases/phase-0/subphase-0.1/proteins/manifest.json`. The table below is the authoritative 16-active subset (the manifest file additionally retains BPTI and HEWL as historical entries for reference).

| # | Short | Protein | Res | Tier | PDB | Chain | Range | SS bonds | BMRB / Ref | S2 resi | MLFF | S2-counted |
|---|-------|---------|-----|------|-----|-------|-------|---------|-----------|---------|------|-----------|
| 1 | ww | WW (Pin1) | 34 | A | 2F21 | A | 6-39 | 0 | Seewald 2007 NSMB 14:1120 | 28 | yes | yes |
| 2 | crambin | Crambin | 46 | A | 1CRN | A | 1-46 | 3 | none (stability ctrl) | 0 | yes | no |
| 3 | ntl9 | NTL9 | 51 | B | 2HBB | A | 1-51 | 0 | Lillemoen 1998 JMB 281:539 | 45 | yes | yes |
| 4 | enhd | EnHD | 54 | A | 1ENH | A | 3-56 | 0 | Religa 2008 JBNMR 40:189 / BMRB 15536 | 58 | yes | yes |
| 5 | gb3 | GB3 | 56 | A/B | 1P7E | A | 1-56 | 0 | Hall 2003 JBNMR 27:261 / bmr5839 | 50 | yes | yes |
| 6 | gb1 | GB1 | 56 | B | 2QMT | A | 1-56 | 0 | Hall 2003 JBNMR 27:261 | 48 | yes | yes |
| 7 | ci2 | CI2 | 64 | B | 2CI2 | I | 1-64 | 0 | Shaw 1995 Biochemistry 34:2225 / bmr51234 | 50 | yes | yes |
| 8 | cspa | CspA | 70 | B | 1MJC | A | 1-70 | 0 | Feng 1998 Biochemistry 37:10881 | 55 | partial | yes |
| 9 | a3d | alpha-3D | 73 | B/C | 2A3D | A | 1-73 | 0 | Walsh 2001 Biochemistry 40:9560 | 60 | partial | yes |
| 10 | calb | Calbindin D9k (apo) | 75 | B | 3ICB | A | 1-75 | 0 | Akke 1993 Biochemistry 32:9832 | 60 | partial | yes |
| 11 | ubq | Ubiquitin | 76 | B | 1UBQ | A | 1-76 | 0 | Tjandra 1995 JACS 117:12562 / bmr6470 | 70 | partial | yes |
| 12 | hpr | HPr | 85 | B | 1HDN | A | 1-85 | 0 | Option A — no S2 source (D.3) | 0 | unlikely | no |
| 13 | acbp | ACBP | 86 | B/A | 2ABD | A | 1-86 | 0 | Rischel 1994 Biochemistry 33:13997 / Kragelund 1995 JMB 250:448 | 77 | unlikely | yes |
| 14 | fkbp12 | FKBP12 | 107 | B/C | 2PPN | A | 1-107 | 0 | Cheng 1993 Biochemistry 32:9000 / Sapienza 2011 JMB 405:378 | 94 | unlikely | yes |
| 15 | barn | Barnase | 110 | C | 1BNR | A | 1-110 | 0 | Caro-Wand 2017 PNAS / bmr26619 / Sahu 2000 JBNMR 18:107 | 90 | no | yes |
| 16 | t4l | T4 Lysozyme | 164 | C | 3LZM | A | 1-164 | 0 | Mulder 2000 Biochemistry 39:12614 (WT subset) | 130 | no | yes |

**Historical dropped entries** (retained in `manifest.json` for reference; NOT in active benchmark):

| Short | Protein | Res | Dropped | Reason |
|-------|---------|-----|---------|--------|
| bpti | BPTI | 58 | Phase 0 task-004 | BioEmu CB-CB SS integrity 56.1% at 4.5 Å (AK3) |
| hewl | HEWL | 129 | Sub 1.1 task-005 | BioEmu SG-SG integrity 40.2% at 2.5 Å (AK3) |

**Totals (active benchmark):** 16 proteins / 14 S2-counted / 11 MLFF-feasible (Yes+Partial) / 10 MLFF-feasible AND S2-counted.

---

*End of pre-registration v2. Changes from v1: (1) power analysis tables populated with computed values from validated stats pipeline (all v1 placeholders resolved except GitHub commit hash, deferred to deposit); (2) Appendix B code replaced with corrected Fisher-z sampling approach (v1 grid-based simulation produced artificially inflated r values); (3) JZS BF implementation references updated from "pending validation" to "validated to <0.01% agreement with R". No other content changed from v1.*
