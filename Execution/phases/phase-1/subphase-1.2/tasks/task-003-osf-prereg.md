---
task_id: "task-003"
title: "OSF pre-registration drafting + lock (HARD deadline 2026-05-15)"
subphase: "1.2"
track: cross-cutting
wave: 1
agent: "osf-prereg"
effort: "7-10 days writing (no compute)"
status: planned
created: 2026-04-18
---

# Task 003: OSF Pre-Registration Drafting + Lock

## Objective

Draft the OSF pre-registration document that locks the analysis plan for the
combined Alpha-M + Gamma + Delta paper (and the separate-publication fallback)
BEFORE Phase 2 production begins on July 1. The document must cover the full
protein roster (16 active / 14 S2-counted), all 10 generators, observables,
statistical tests (Friedman+Nemenyi, paired Wilcoxon, JZS Bayesian with 4-prior
sensitivity), decision rules T1–T6 / S1–S5, T_min trajectory truncation protocol,
all kill criteria (AK1-AK3, GK1-GK3, CK1-CK4, DK1-DK3), and the recalculated
power analysis for the post-expansion 16/14 design. The drafted document is
deposited PUBLICLY on OSF by the human user (you do not have OSF credentials).
**HARD deadline: 2026-05-15 23:59 UTC.**

---

## Context

**Why pre-registration matters:** Implementation Plan §7.2 mandates an OSF
pre-registration deposited by 2026-05-15 covering all three projects. This is
a credibility commitment: any analysis path NOT in the pre-reg requires either
(a) pre-deposit amendment with timestamp, or (b) post-hoc disclosure as
exploratory analysis. Reviewers will check the OSF DOI against the manuscript
during peer review. A late or missing pre-reg seriously damages publication
prospects (especially at NCS, NatMeth where pre-registration is increasingly
expected for benchmark papers).

**Why now (Sub 1.2, not later):** The IP §7.2 deadline is 2026-05-15. Sub 1.2
runs 2026-04-19 → 2026-05-16, which is the only window. Sub 1.3 is too late.

**What "lock" means:** Once deposited on OSF, the document is publicly timestamped.
Any change after May 15 is a tracked amendment. Therefore the draft must be
substantively complete and reviewer-defensible before deposit. The Sub 1.1
robustness remediation (`shared/notes/1.1-robustness-remediation.md`) closed
8 risks and 6 flags — the pre-reg can leverage that closure (e.g., "we
pre-registered the BPTI/HEWL drops based on AK3 evidence collected in Phase 0
and Sub 1.1; see [appendix]").

**Deposit handoff (PER USER DECISION 2026-04-18):** The osf-prereg SubAgent
DRAFTS the markdown document. The HUMAN deposits it on OSF (account owner
authentication required). The HUMAN provides the resulting DOI back to head-1.2
for documentation in `dashboards/master-status.md`. Do NOT attempt to authenticate
to OSF programmatically; do not request OSF API tokens.

---

## Detailed Instructions

### Step 1: Information gathering (Day 1-2)

Read in order:
1. `Proposal/ImplementationPlan.md` (full) — especially §7.2 (pre-reg scope), §11 (kill criteria), §12 (statistical framework), §13 (gates), Appendix A (Bayesian model spec)
2. `Proposal/Alpha-M.md` (§5.2 protein tiers)
3. `Proposal/Gamma.md` (§2 BioEmu pipeline, §5 features, §12 stats)
4. `Proposal/Delta.md` (§3 Tahoe-100M, §4 methods, §12 stats)
5. `Proposal/Combined-Alpha-Gamma.md` (integration analysis spec)
6. `shared/notes/1.1-protein-count-canonical.md` — authoritative protein counts (18 manifest / 16 active / 14 S2-counted)
7. `shared/notes/1.1-methods-section-drafts.md` — 4 caveat paragraphs already drafted (D.1-D.4) for GEARS, Crambin, HPr, T4L
8. `shared/notes/1.1-citations-verified.md` — verified citation registry
9. `shared/notes/1.1-bioemu-passrates.md` — disorder exclusion + oversampling formula (relevant for "we will exclude proteins with >60% predicted disorder")
10. `shared/notes/1.2-scope-recommendations.md` — items 1, 7 are explicit pre-reg requirements

**Recalculate power analysis** (item 7 in scope-recommendations):
- Original IP §1: 14×10 design ~42% power at ρ=0.5 with no convergence correction
- Post-expansion: 16 active / 14 S2-counted; need recomputed power assuming 15-25% ICC convergence attenuation per IP §10.3
- Use Python (`statsmodels.stats.power` or analytic formula for hierarchical bootstrap) to compute power for ρ ∈ {0.3, 0.5, 0.7} with corrected ICC
- Document the calculation in an appendix; cite the input ICC values from Sub 1.4 (when available — for the OSF v1, use IP §1 conservative estimate ICC=0.7 with 20% attenuation)

### Step 2: Document structure (Day 3-5)

Write `phases/phase-1/subphase-1.2/output/osf-prereg-v1.md` following this structure:

```
# OSF Pre-Registration: Alpha-M + Gamma + Delta + Combined-Alpha-Gamma

## 1. Project Overview
- 3 projects + 1 combined paper (T1-T6 trigger combined; S1-S5 trigger separation)
- Date locked: 2026-05-15
- Authors: <to be provided by user>
- Related preprints: <none yet>

## 2. Hypotheses (3 projects + combined)
### 2.1 Alpha-M
H1: At least 1 MLFF (MACE-OFF24, SO3LR) produces stable trajectories matching
    NMR S2 R² > 0.85 on >=3 Tier B proteins.
H2: ...

### 2.2 Gamma
H1: BioEmu RMSF + RSALOR features improve binding+activity assay prediction
    over RSALOR alone (paired Wilcoxon p < 0.05, N=57 assays).
H2: ...

### 2.3 Delta
H1: At least one DL method (GEARS, scGPT, CPA, scFoundation, Tahoe-x1) outperforms
    all 5 baselines on WMSE → top-k DEG Spearman, with calibrated probability
    estimates (ECE < 0.1).
H2: ...

### 2.4 Combined paper
H1: Across 14 S2-counted proteins × 10 generators, BF_10 > 3 under JZS prior for
    correlation between physical accuracy (S2 R² to NMR) and Gamma fitness
    prediction (assay Spearman).
H2: ...

## 3. Protein Roster
### 3.1 Active benchmark (16 proteins)
[table from `1.1-protein-count-canonical.md`]
- Pre-registered drops: BPTI, HEWL (AK3 triggers, BioEmu SS-integrity)
- Pre-registered additions (post-expansion): NTL9, ACBP, FKBP12, EnHD
- Pre-registered exclusions from quantitative S2: Crambin (stability control),
  HPr (Option A; van Nuland 1995 invalid)

### 3.2 Tier classification
[Tier A/B/C from IP §5.2 + post-expansion]

### 3.3 MLFF-feasible subset
11 proteins (per `1.1-protein-count-canonical.md`)

## 4. Generator Roster (10 generators, IP §5.1)
[List]

## 5. Observables
### 5.1 Alpha-M
- S2 (Lipari-Szabo order parameter) per residue per protein
- R1, R2, NOE relaxation rates (back-calculated via SPARTA+)
- SAXS profiles (back-calculated via Pepsi-SAXS)
- ...

### 5.2 Gamma
- Spearman ρ on binding+activity assays (N=57)
- Win rate on all 217 assays
- ...

### 5.3 Delta
- WMSE on Tahoe-100M test split
- Top-k DEG Spearman (k=20, 50, 100)
- Reliability diagram + ECE
- ...

## 6. Statistical Tests
### 6.1 Alpha-M (per IP §12.1)
- Friedman test with Nemenyi post-hoc across generators
- Hierarchical bootstrap (resample proteins → residues), 10,000 iterations
- ICC(2,k) >0.80 AND ICC(2,1) >0.50 with documented convergence-correction
  factor (15-25% attenuation per IP §10.3)

### 6.2 Gamma (per IP §12.2)
- Paired Wilcoxon signed-rank on binding+activity (N=57), α=0.05
- Win rate >57% on all 217 assays
- Central ablation (RSALOR+RMSF vs RSALOR), paired Wilcoxon
- Homolog-aware 5-fold CV (<30% sequence identity threshold)

### 6.3 Combined (per IP §12.3 + Appendix A)
- JZS Bayesian correlation (Cauchy(0,1) prior); BF_10 > 3 = "moderate evidence
  for integration"; BF_10 > 10 = "strong evidence"
- 4-prior sensitivity: JZS, Skeptical N(0,0.5²), Informative N(0.5,0.15²),
  Flat U(-1,1)
- Crossed random effects: (1|protein) + (1|generator)
- Parametric bootstrap ≥1000 iterations under H0 + Kenward-Roger
- Implementation: PyMC + bridgesampling (Gronau et al. 2017) — fallback to R
  brms + BayesFactor if PyMC validation fails

### 6.4 Delta (per IP §12.4)
- WMSE primary, gates Spearman via hierarchical testing
- FDR: BH primary, BY sensitivity
- Stratified evaluation: cell type × perturbation type × expression level
- Calibration: reliability diagram, ECE, vs random baseline (metric-gaming test)

## 7. Decision Rules

### 7.1 Combined paper GO criteria (T1-T6, ALL required) [from IP §13]
- T1: ≥1 MLFF stable >10 ns on ≥3 proteins
- T2: S2 block-split R² >0.90
- T3: BioEmu disulfide integrity >95% [PRE-REGISTERED RETIRED — see §3.1]
- T4: Integration ρ >0 (directional)
- T5: ≥12 of 14 proteins confirmed [post-expansion: ≥12 of 14 S2-counted; current 14/14]
- T6: ≥9 generators distinguishable (JSD >0.01)

### 7.2 Separation triggers (S1-S5, ANY triggers) [from IP §13]
- S1: Integration ρ ≤0
- S2: <2 MLFFs operational
- S3: BF projected <1 under JZS
- S4: Gamma δ <0.02 on binding+activity
- S5: NCS-relevant scoop published

## 8. Trajectory Truncation Protocol
All trajectories per protein are truncated to T_min(protein) = the shortest
trajectory length that all generators achieved for that protein. Per IP §12.1,
this is mandatory for fair comparison. Implementation: `phases/phase-1/subphase-1.2/output/scripts/stats/truncation.py`.

## 9. Kill Criteria
### 9.1 Alpha-M (AK1-AK3)
- AK1: 0 MLFFs with >5 ns trajectory by June 30 → classical+generative only
- AK2: All S2 indistinguishable (R² spread <0.05) by Aug 15 → "validation
  confirms consensus" framing
- AK3: BioEmu SS integrity <80% → drop affected proteins [PRE-REGISTERED ALREADY
  TRIGGERED for BPTI + HEWL]

### 9.2 Gamma (GK1-GK3)
[from IP §11.2]

### 9.3 Combined (CK1-CK4)
[from IP §11.3]

### 9.4 Delta (DK1-DK3)
[from IP §11.4]

## 10. Power Analysis
Recalculated for 16 active / 14 S2-counted design with 20% ICC convergence
attenuation. Power table for ρ ∈ {0.3, 0.5, 0.7}:

| ρ_true | Original (14×10, no attenuation) | Recalculated (14×10, 20% attenuation) |
|--------|---------------------------------|---------------------------------------|
| 0.3    | ...                              | ...                                    |
| 0.5    | ~42%                             | ...                                    |
| 0.7    | ...                              | ...                                    |

Methodology: parametric simulation (10,000 reps), JZS BF, BF_10 > 3 threshold.
Code: appendix.

## 11. Pre-Registered Caveats (from `1.1-methods-section-drafts.md`)
### D.1 GEARS first-target-only heuristic
[D.1 paragraph, verbatim]
### D.2 Crambin BioEmu stability-only
[D.2 paragraph, verbatim]
### D.3 HPr Option A (non-S2)
[D.3 paragraph, verbatim]
### D.4 T4L Mulder 2000 reference lock
[D.4 paragraph, verbatim]

## 12. Compute and Software
- HPC: Yale McCleary cluster
- GPUs: H200 (MACE Phase 2), RTX 5000 Ada (BioEmu, Delta, SO3LR)
- Total budget: ~170,000 GPU-hrs across all phases
- Software: 9 conda envs (env-mace, env-so3lr, env-bioemu, env-delta-v2, env-cpa,
  env-tahoex1, env-classical, env-analysis, env-garnet); pinned YAML files in repo
- All code committed to GitHub before deposit; commit hash recorded

## 13. Amendments Process
Any analysis change after 2026-05-15 requires (a) timestamped amendment on OSF
or (b) disclosure as exploratory analysis in the manuscript.

## 14. References
[full citation list from `1.1-citations-verified.md` + IP citations]

## Appendix A: Bayesian Model Specification (verbatim from IP App. A)
[full code block]

## Appendix B: Power Analysis Code
[Python script with simulation results]

## Appendix C: Protein Manifest
[full table from `phases/phase-0/subphase-0.1/proteins/manifest.json`]
```

### Step 3: Iterate to v1 (Day 5-6)

After completing the v1 draft, output to `phases/phase-1/subphase-1.2/output/osf-prereg-v1.md`.
Notify head-1.2 that the v1 trigger condition is met (≥80% of sections populated).

### Step 4: Refine to final (Day 7-9)

Address any HeadAI or self-identified gaps. Outputs `osf-prereg-final.md`.
Final document should be ~3,000-6,000 words; OSF supports markdown rendering.

### Step 5: Hand off to user for OSF deposit (Day 10-11)

1. Write a deposit-instructions document at `phases/phase-1/subphase-1.2/output/osf-deposit-instructions.md` with:
   - URL: https://osf.io/dashboard
   - "Create new project" → Project name suggestion: "CompBioSummer2026: MLFF Force Field + Dynamics-to-Fitness + Perturbation Benchmark Pre-Registration"
   - "Pre-registrations" → "Create new" → choose "OSF Standard Pre-Registration" template
   - Paste contents of `osf-prereg-final.md` as the main document
   - Files to attach: `osf-prereg-final.md`, the protein manifest JSON, the appendix code
   - "Register" → confirm deposit; OSF generates a DOI
2. Notify HeadAI when the deposit-instructions document is ready.
3. After user provides the DOI back, write `phases/phase-1/subphase-1.2/output/osf-deposited.md` with:
   - DOI URL
   - Deposit timestamp
   - SHA256 of the deposited document
4. Cross-agent note `shared/notes/1.2-osf-deposited.md` (urgency: critical) so all future agents know the analysis plan is locked.

### Step 6: Update dashboards (Day 11)

Notify head-1.2 to update `dashboards/master-status.md` with the OSF DOI in the
Decision Log.

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| `../../tasks/task-003-osf-prereg.md` | This task spec |
| `../../../../../../Proposal/ImplementationPlan.md` | §7.2, §11, §12, §13, App. A — primary source |
| `../../../../../../Proposal/Alpha-M.md` | §5.2 protein tiers |
| `../../../../../../Proposal/Gamma.md` | §2, §5, §12 |
| `../../../../../../Proposal/Delta.md` | §3, §4, §12 |
| `../../../../../../Proposal/Combined-Alpha-Gamma.md` | Integration analysis spec |
| `../../../../../shared/notes/1.1-protein-count-canonical.md` | Authoritative counts |
| `../../../../../shared/notes/1.1-methods-section-drafts.md` | 4 caveat paragraphs (D.1-D.4) — paste verbatim |
| `../../../../../shared/notes/1.1-citations-verified.md` | Verified citations |
| `../../../../../shared/notes/1.1-bioemu-passrates.md` | Disorder exclusion criterion |
| `../../../../../shared/notes/1.2-scope-recommendations.md` | Items 1, 7 are explicit pre-reg requirements |
| `../../../../../../phases/phase-0/subphase-0.1/proteins/manifest.json` | Protein manifest for Appendix C |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../shared/notes/1.1-robustness-remediation.md` | Background on pre-registered drops + risks closed |
| `../../../../../shared/competition-scans/2026-04-baseline.md` | Pre-reg may reference competition landscape |
| `../../../../../shared/notes/1.1-mace-hybrid-validation.md` | §11 throughput → influences MLFF Phase 2 budget claims |

### DO NOT READ

- Other SubAgents' task specs in `../../tasks/`
- `../../../../../../Proposal/HumanOnlyProposal.md` (off-limits)
- Future subphase plans

---

## Output Artifacts

### Documents

| Artifact | Path | Format |
|----------|------|--------|
| Pre-reg v1 (≥80% complete, triggers Wave 2) | `../../output/osf-prereg-v1.md` | Markdown, 3,000-6,000 words |
| Pre-reg final (locked, ready for deposit) | `../../output/osf-prereg-final.md` | Markdown |
| OSF deposit instructions for user | `../../output/osf-deposit-instructions.md` | Markdown step-by-step |
| OSF deposited record (after user provides DOI) | `../../output/osf-deposited.md` | Markdown with DOI + timestamp + SHA |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-003-status.md` | `templates/status-report.md` |
| Cross-agent note | `../../../../../shared/notes/1.2-osf-deposited.md` | `templates/cross-agent-note.md` (urgency: critical) |

---

## Success Criteria (Zero Compromise)

1. [ ] `osf-prereg-v1.md` exists at `../../output/` by **2026-04-26** (Day 7) for HeadAI partial-completion trigger
2. [ ] `osf-prereg-final.md` exists at `../../output/` by **2026-05-13** (Day 24)
3. [ ] All 14 sections (§1-§14) substantively populated; no placeholder "TODO" markers in final
4. [ ] All 4 D-paragraph caveats (GEARS, Crambin, HPr, T4L) included verbatim from `1.1-methods-section-drafts.md`
5. [ ] Power analysis recalculated and tabulated with code in Appendix B
6. [ ] All 10 generators listed (per IP §5.1)
7. [ ] All decision rules T1-T6 / S1-S5 explicitly stated with thresholds
8. [ ] All kill criteria AK1-AK3, GK1-GK3, CK1-CK4, DK1-DK3 explicitly stated
9. [ ] OSF deposit instructions document at `../../output/osf-deposit-instructions.md` for user
10. [ ] Cross-agent note `1.2-osf-deposited.md` written AFTER user provides DOI (HeadAI may write this; coordinate)
11. [ ] Status report written to `../../status/task-003-status.md`

---

## Verification

1. `wc -w ../../output/osf-prereg-final.md` returns 3000-6000 words
2. `grep -c "TODO\|FIXME\|XXX\|<placeholder>" ../../output/osf-prereg-final.md` returns 0
3. All section headers (`## 1.` through `## 14.`) present
4. Appendix A contains the verbatim Bayesian model spec from IP App. A
5. Appendix C contains all 16 active proteins from `1.1-protein-count-canonical.md`
6. Status report exists with status `complete`

---

## Failure Protocol

1. **Cannot complete a section due to missing IP detail:** Use the most reasonable default consistent with IP §12 + your readings; flag the section with a `[v1 placeholder, will refine in v2 amendment]` annotation.
2. **User cannot deposit on May 15:** Slip to May 16 (1-day grace). Slipping >2 days requires PlannerAI replan + user notification.
3. **OSF technical issue (site down):** Document the attempt; use Open Science Framework public alternative (Zenodo) as fallback ONLY if OSF unavailable for >48 hours; deposit MUST happen before May 16.
4. **Caveat paragraph needs amendment (e.g., new T4L finding):** Update verbatim from `1.1-methods-section-drafts.md` if updated post-Sub-1.1; otherwise note divergence in pre-reg.

In all cases: write status report with detailed disposition.
