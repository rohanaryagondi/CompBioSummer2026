# Gamma: Conformational Ensembles Predict Protein Function Beyond Sequence

## Target Venue: Genome Research or Bioinformatics (standalone); Nature Computational Science (if combined with Alpha-M)

## One-Sentence Pitch

A large-scale evaluation of whether conformational ensemble features from BioEmu improve mutation fitness prediction beyond sequence-only methods on the ProteinGym benchmark.

---

## Problem

Current mutation effect predictors rely on evolutionary information (MSAs), static structures, or protein language models -- none incorporates explicit conformational dynamics. The ProteinGym leaderboard has 97+ methods across 217 DMS assays; zero use explicit ensemble dynamics features. Yet protein function fundamentally depends on dynamics: binding requires conformational selection, catalysis requires active-site flexibility, and allosteric regulation requires correlated motions. The convergence of BioEmu (equilibrium ensembles from sequence in minutes) and ProteinGym (ground-truth fitness for 2.7M variants across 217 proteins) creates the opportunity to test whether dynamics adds value -- and this test has never been done.

---

## What We Do

Generate BioEmu conformational ensembles for 150+ ProteinGym proteins, extract dynamics features, and test whether they improve fitness prediction beyond the RSALOR baseline (Spearman 0.465, rank #15 on ProteinGym).

### Pipeline

1. **Ensemble generation:** BioEmu v1.3.1 generates 2,000 backbone conformations per protein (~20 min/protein on H200). Also generate Boltz-2 ensembles for comparison.

2. **Feature extraction:** Per-residue dynamics features from each ensemble:
   - RMSF (root-mean-square fluctuation)
   - Per-residue SASA variance
   - Secondary structure propensity
   - Contact frequency matrices
   - B-factor profiles
   - PCA-based flexibility modes
   - Ensemble RMSF (via eRMSF package)

3. **ML models:** Three architectures tested:
   - MLP (baseline)
   - XGBoost (gradient boosted trees)
   - GATv2 (graph attention network, structure-aware)
   
   Input: ESM2-650M embeddings + RSA + dynamics features per residue.

4. **Central ablation experiment** (the most important analysis):
   ```
   Model 1: ESM2-650M + RSA                    (no dynamics)
   Model 2: ESM2-650M + RSA + RMSF             (add dynamics)
   Model 3: ESM2-650M + RSA + all dynamics      (full feature set)
   Model 4: RSALOR                             (conservation + RSA)
   Model 5: RSALOR + RMSF                      (conservation + dynamics)
   ```
   **If Model 5 > Model 4:** dynamics provides genuinely new information beyond conservation. This is the publishable finding.
   **If Model 5 ~ Model 4:** dynamics is merely re-encoding evolutionary information. Still publishable as a well-powered negative result.

5. **Assay-type stratification** (the primary finding):
   
   | Assay Type | RSALOR Spearman | Beat Target | N assays |
   |------------|----------------|-------------|----------|
   | Binding | 0.416 | Must beat ProSST 0.445 | 14 |
   | Activity | 0.479 | Must beat RSALOR 0.479 | 43 |
   | Expression | 0.427 | Must beat ProSST 0.530 | 17 |
   | Stability | 0.575 | Nearly impossible | 66 |
   | Organismal fitness | -- | -- | 77 |
   
   Dynamics features are expected to help most on binding and activity, where conformational selection and active-site flexibility matter.

### Statistical Framework

- **Primary test:** Paired Wilcoxon signed-rank on per-assay Spearman differences between Gamma and RSALOR, on binding+activity assays (N~57)
- **Secondary test:** Win rate > 57% across all 217 assays
- **Cross-validation:** Homolog-aware 5-fold CV (<30% sequence identity exclusion)
- **Baselines:** RSALOR, ProSST, S3F-MSA per assay type
- **Minimum detectable improvement** at N=217: delta-Spearman ~0.135 (overall). At N=57 (binding+activity): delta ~0.04 is detectable

---

## Key Findings from ReviewCohort

### BioEmu ff14SB Ceiling

BioEmu is trained on AMBER ff14SB MD simulations. ff14SB achieves R^2 = 0.62 vs experimental NMR S2. The signal attenuation chain:

```
Experiment -> ff14SB (R^2=0.62) -> BioEmu (R^2~0.80 vs ff14SB) -> Features -> ML -> Fitness
Signal preserved: ~49% of original dynamics information
```

**Realistic improvement ceilings over RSALOR:**

| Scenario | True dynamics-fitness rho | After attenuation | Delta over RSALOR |
|----------|--------------------------|-------------------|-------------------|
| Optimistic | 0.6 | 0.29 | +0.04-0.06 |
| Moderate | 0.4 | 0.20 | +0.02-0.03 |
| Pessimistic | 0.2 | 0.10 | undetectable |

### RMSF-Conservation Collinearity

RMSF correlates with conservation (r~0.3-0.5) and RSA (r~0.4-0.6) -- the same features in RSALOR. The central experiment (Model 4 vs Model 5) directly tests whether dynamics is redundant with conservation or provides genuinely new information.

### MutRobustness Prior Art

Zuk (bioRxiv March 2026) demonstrated median |rho|~0.6 between dynamics and mutational robustness across 2,000+ proteins. Gamma differentiates by using **experimental** DMS fitness (not predicted ddG) across all ProteinGym assay types.

---

## Timeline

| Phase | Dates | Activities |
|-------|-------|-----------|
| Ensemble generation | May 1 - Jun 15 | BioEmu + Boltz-2 ensembles for 150+ proteins |
| Feature extraction | Jun 1 - Jul 15 | Dynamics features from all ensembles |
| ML pipeline | Jul 1 - Aug 15 | Train/evaluate 3 architectures x 5 model variants |
| Ablation + analysis | Aug 1 - Sep 15 | Central ablation, assay-type stratification |
| Manuscript | Sep 15 - Oct 15 | Writing |

**Compute:** ~2,000 GPU-hours total (trivial compared to Alpha-M).

---

## Kill Criteria

| ID | Criterion | Threshold | Date |
|----|-----------|-----------|------|
| GK1 | BioEmu generation fails | <100 of 150 proteins | July 15 |
| GK2 | Dynamics add nothing | delta-Spearman <0.01 on 50 proteins | Aug 15 |
| GK3 | Static methods surge | ProSST delta >0.10 over RSALOR | Ongoing |
| GK4 | BioEmu scooped for ProteinGym | Preprint appears | Ongoing |

**If GK2 fires:** Pivot to negative-result framing: "Dynamics features do not improve fitness prediction beyond sequence conservation" -- publishable at PLOS Comp Bio with proper power analysis.

---

## What Makes This Novel

1. **First explicit dynamics features on ProteinGym.** Zero of 97 methods use ensemble dynamics.
2. **Assay-type stratification.** First systematic analysis of WHERE dynamics helps (binding/activity) vs WHERE it doesn't (stability).
3. **RSALOR+dynamics ablation.** Directly tests whether dynamics adds beyond conservation.
4. **BioEmu vs Boltz-2 comparison.** Tests whether ensemble diversity (BioEmu) or per-residue accuracy (Boltz-2) matters more for function.
5. **Compute-normalized comparison.** Improvement per GPU-hour -- practical for protein engineers.

---

## References

Key papers: Notin et al. (NeurIPS 2023) ProteinGym; Lewis et al. (Science 2025) BioEmu; Tsishyn et al. (Bioinformatics 2025) RSALOR; Ozkan et al. (PNAS 2025) dynamics GNN; Burgin (JCIM 2025) QDPR; Zuk (bioRxiv 2026) MutRobustness; Hou et al. (PNAS 2026) ESMDance; Aryal et al. (IJMS 2026) BioEmu assessment.
