# Combined Paper: Physical Accuracy of Protein Ensembles Predicts Functional Utility

## Target Venue: Nature Computational Science

## One-Sentence Pitch

The first demonstration that the physical accuracy of protein ensemble generators -- validated against NMR experiment -- correlates with their utility for predicting mutation fitness effects, connecting force field development directly to biological applications.

---

## The Claim (Completely Unoccupied)

No published paper connects force field validation quality to downstream fitness prediction. As of April 2026, this integration claim is completely unoccupied in the literature. This is confirmed by exhaustive search across bioRxiv, arXiv, and journal databases. The claim is the portfolio's highest-value target.

**The central question:** Does getting the physics right (better S2 agreement with NMR) translate to getting the biology right (better prediction of which mutations are harmful)?

---

## What This Paper Contains

The combined paper merges Alpha-M (force field benchmark) and Gamma (dynamics-to-fitness prediction) into a single narrative with three acts:

### Act 1: Benchmark (Alpha-M Component)

Benchmark 10 ensemble generators against experimental NMR S2 order parameters across 14 proteins. Establish which generators produce the most physically accurate protein dynamics.

Key finding: Quantitative ranking of generators by S2 R^2 vs experiment.

### Act 2: Prediction (Gamma Component)

Use each generator's ensembles to extract dynamics features, then predict mutation fitness on ProteinGym. Establish which generators produce the most functionally useful dynamics.

Key finding: Dynamics features improve fitness prediction on binding/activity assays by delta-Spearman >= 0.04 over RSALOR.

### Act 3: Integration (The Novel Claim)

Plot each generator's S2 accuracy (x-axis) against its fitness prediction performance (y-axis). Test whether better physics -> better predictions.

Key finding: Positive correlation (rho > 0.4) between physical accuracy and functional utility, with BF_10 > 3 under JZS prior.

---

## Statistical Design

### Integration Analysis

- **Design:** 14 proteins x ~7 generators (classical + generative, fully crossed for integration; MLFFs present for 9 proteins only)
- **Effective N:** ~15-17 independent observations (accounting for ICC)
- **Primary test:** JZS Bayesian correlation

```
Likelihood: S2_R2_ij ~ Normal(mu_ij, sigma^2)
mu_ij = beta_0 + beta_1 * Fitness_Spearman_ij + u_i + v_j

Priors (JZS default):
  beta_1_standardized ~ Cauchy(0, 1)
  u_i ~ Normal(0, sigma_protein^2)
  v_j ~ Normal(0, sigma_generator^2)
  sigma_protein ~ Half-Cauchy(0, 0.5)
  sigma_generator ~ Half-Cauchy(0, 0.5)
  sigma ~ Half-Cauchy(0, 1)

Decision rules:
  BF_10 > 3 under JZS:    "Moderate evidence" (minimum publishable)
  BF_10 > 10 under JZS:   "Strong evidence"
  BF_10 > 1 under skeptical prior: "Survives skeptical analysis"
```

- **Sensitivity:** 4 priors tested (JZS, Skeptical, Informative, Flat)
- **Power:** ~74% at rho=0.5 with the 14x10 design (after convergence attenuation)

### Why Not Frequentist?

The frequentist approach has only ~42% power at rho=0.5 with 6x8 design, and ~74% with 14x10. The Bayesian approach with JZS prior provides interpretable evidence quantification (BF) that works at small effective N.

The informative prior N(0.5, 0.15^2) originally proposed was rejected by all reviewers -- it contributes ~59 effective observations vs ~15 from data (4:1 prior-to-data ratio), dominating the posterior.

---

## Viability Assessment

**Consensus: 30% viable. Default to separation.**

The combined paper is the portfolio's highest-ceiling outcome but statistically riskiest:

| Factor | Assessment |
|--------|-----------|
| Integration claim unoccupied | YES -- strongest strategic asset |
| Statistical power | ~74% at rho=0.5 (14x10 design) |
| BF at N_eff=7.8 | ~1.3 (anecdotal -- insufficient) |
| BF at N_eff=20.4 (14x10) | ~3.9 (moderate -- minimum publishable) |
| BioEmu ff14SB ceiling | Attenuates signal by ~50% |
| NCS editorial precedent | Zero FF/dynamics papers at NCS 2024-2026 |

### Decision Architecture

**August 31, 2026: GO/NO-GO**

**GO if ALL of:**
- T1: >=1 MLFF stable >10 ns on >=3 proteins
- T2: S2 block-split R^2 >0.90
- T3: BioEmu disulfide integrity >95%
- T4: Integration rho >0 (directional)
- T5: >=12 of 14 proteins confirmed
- T6: >=9 generators distinguishable

**SEPARATE if ANY of:**
- S1: Integration rho <=0
- S2: <2 MLFFs operational
- S3: BF projected <1
- S4: Gamma delta <0.02 on binding+activity
- S5: NCS-relevant scoop published

### If Separation Is Triggered

| Component | Venue | Timeline |
|-----------|-------|----------|
| Alpha-M | NatMeth Registered Report (Stage 1: Sept 15) | Viability: 65-70% |
| Gamma | Genome Research / Bioinformatics (preprint: Oct 15) | Viability: 45-50% |

---

## Timeline (Combined Track)

```
May 1:      Alpha-M pilot + Gamma ensemble generation begin
May 15:     OSF pre-registration (covers both combined and separate)
June 30:    Alpha-M Phase 1 complete (D2 GO/NO-GO)
July 31:    Pilot integration analysis (D4)
August 31:  COMBINED PAPER GO/NO-GO
Sept-Oct:   Integration analysis + manuscript
Nov 1:      NCS preprint
Nov 15:     NCS submission
```

---

## Anticipated NCS Reviewer Attacks

| Attack | Pre-emption |
|--------|-------------|
| "N=14 is too small" | Pre-registered Bayesian with JZS. Report BF not p-values. "First evidence" framing. |
| "Per-residue inflates N" | ICC estimation + hierarchical bootstrap. Report effective N alongside nominal N. |
| "BioEmu just emulates ff14SB" | Explicit bias chain section. Include Boltz-2 (no ff14SB bias) for comparison. |
| "MLFF trajectories too short" | Truncation protocol. Report trajectory length as finding. |
| "Garnet is contaminated" | Dedicated contamination analysis. Report separately. |
| "This is just a correlation" | Bayesian evidence quantification. Four-prior sensitivity. Pre-registered. |

---

## Cover Letter Pitch

"We establish, for the first time, that the physical accuracy of protein ensemble generators -- validated against NMR and SAXS experiment -- correlates with their utility for predicting mutation fitness effects, connecting force field development directly to biological applications."

---

## References

Key papers: All Alpha-M and Gamma references, plus: Wetzels & Wagenmakers (2012) JZS test; Lindorff-Larsen et al. (PLoS ONE 2012) FF benchmark; NCS editorial standards.
