---
last_updated: 2026-05-04T05:00:00Z
updated_by: head-1.2 (housekeeping subagent; doc-audit batch 2: UBQ D-UBQ-1 options c+d probes IN-FLIGHT (10622876 NTL9, 10622885 UBQ_alt 1XQQ); D2 G1 evidence base unchanged from 2026-05-03)
---

# Gate Tracker

## Decision Gates (from Implementation Plan Section 13)

| Gate | Date | Decision | Status | Assessment |
|------|------|----------|--------|------------|
| D1 | May 9 | MLFF software GO | ASSESSED: GO | Both MACE + SO3LR pass; MACE via OpenCL (CUDA broken on all GPUs); Phase 2 via hybrid mode, 1.40× compute multiplier |
| D2 | June 30 | MLFF pilot GO (G1-G6) | ON TRACK | **MULTI-PATH evidence base** as of 2026-05-03: (1) **SO3LR vacuum NVT v1: 2/5 PASS** (GB1+UBQ stable 5 ns; WW/GB3/NTL9 failed via charge runaway); **rescue chemistry validated**: GB3+NTL9 500-ps gates PASSED with neutral-protonation re-prep (D/E protonated, K/R deprotonated, net charge=0); 5 ns full rescues on `scavenge_gpu` PENDING. (2) **MACE NPT Round 3 recipe FIXED for WW + GB3** — validated 100 ps WW (test_P) + 25 ps GB3 (probe TIMEOUT). Recipe (sentinel-bond + HBonds + dt=1 fs + MCB freq=25) documented in `shared/notes/1.2-mace-npt-fixed.md`. **MACE NPT does NOT generalize to UBQ** — NaN @ 7-9.6 ps regardless of dt halving (1.0/0.5/0.25 fs all fail; pattern asymptotic). Escalated via `head-1.2-mace-ubq-non-generalization.md`; D-UBQ-1 user decision pending. **D2 G1** ("≥1 MLFF stable ≥10 ns on ≥3 Tier B") achievable via either MLFF independently: SO3LR rescue 5/5 OR MACE NPT WW + GB3 + GB1/NTL9 (Tier-B-small, untested at production but recipe is architectural). Sub 1.4 production maps per-protein NPT/NVT decision based on Sub 1.2 outcomes. Stats pipeline (task-006) ready for G2/G3/G6 scoring. |
| D3 | June 6 | Delta scope lock | **ASSESSED: GO (RETIRED)** | 5/5 Tier 1 installed + GPU-verified (GEARS, scGPT, CPA, scFoundation, Tahoe-x1). Baselines now COMPLETE (Sub 1.2 task-005 2026-04-19): 5/5 baselines (linear, mean, PCA, random, persistence) + WMSE harness + FDR (BH+BY) + calibration (ECE, reliability diagrams) + stratified (per cell×pert×expression) all operational on 100K Tahoe-100M subsample. Random baseline FAILS WMSE gate (metric-gaming check verified). D3 fully retired 2026-04-19. |
| D4 | July 31 | Integration signal | PENDING | -- |
| D5 | Aug 15 | Delta preprint ready | PENDING | -- |
| **D6** | **Aug 31** | **COMBINED PAPER GO/NO-GO** | **PENDING** | -- |
| D7 | Sept 15 | Phase 3 scope | PENDING | -- |

Status values: PENDING | EVIDENCE AVAILABLE | ASSESSED: GO | ASSESSED: NO-GO | ASSESSED: CONDITIONAL

---

## Gate Criteria Reference

### D1: MLFF Software GO (May 9)
- MACE-OFF24 installs and runs 1 ns NVT on crambin
- SO3LR installs and runs 1 ns NVT on crambin
- If either fails: drop that MLFF, proceed with remainder

### D2: MLFF Pilot GO (June 30) -- dynrev criteria G1-G6
- G1: At least 1 MLFF stable >10 ns on >=3 Tier B proteins
- G2: S2 back-calculation produces non-degenerate values
- G3: ICC(2,k) >0.80 on replicate analysis
- G4: Generator distinctness (JSD >0.01 between >=3 pairs)
- G5: NMR reference data confirmed for >=12 of 14 proteins
- G6: Compute within 2x budget estimate
- If NO-GO: Alpha-M becomes classical + generative benchmark only

### D3: Delta Scope Lock (June 6)
- At least 3 of 5 mandatory Tier 1 DL methods running
- Baseline implementations complete
- If fewer than 3: drop failed methods, proceed with remainder

### D4: Integration Signal (July 31)
- Pilot integration rho > 0 (directional positive)
- If rho <= 0: trigger separation (S1)

### D5: Delta Preprint (August 15)
- Figures complete, manuscript draft complete
- If not ready: 2-week extension maximum

### D6: COMBINED PAPER GO/NO-GO (August 31)
GO requires ALL of T1-T6:
- T1: >=1 MLFF stable >10 ns on >=3 proteins
- T2: S2 block-split R^2 >0.90
- T3: BioEmu disulfide integrity >95%
- T4: Integration rho >0 (directional)
- T5: >=12 of 14 proteins confirmed
- T6: >=9 generators distinguishable (JSD >0.01)

SEPARATE if ANY of S1-S5:
- S1: Integration rho <=0
- S2: <2 MLFFs operational
- S3: BF projected <1 under JZS
- S4: Gamma delta <0.02 on binding+activity
- S5: NCS-relevant scoop published

### D7: Phase 3 Scope (September 15)
- Select priority proteins for Phase 3 replicas based on Phase 2 results

---

## Early Evidence (Subphase 1.1)

### D1 Evidence (formal assessment at May 9)

| Criterion | MACE | SO3LR |
|-----------|------|-------|
| Installs successfully | PASS | PASS |
| Runs NVT on crambin | PASS (OpenCL fallback, CUDA broken on H200/B200) | PASS (CLI, RTX 5000 Ada) |
| >=100 ps stable | PASS (37+ ps confirmed) | PASS (1 ns complete) |
| No NaN forces | PASS | PASS |

Both MLFFs pass. MACE has CUDA incompatibility on H200/B200 (uses OpenCL at ~2x slower).
RTX 5000 Ada CUDA test pending (job 8398672).

### D3 Evidence — FULLY RETIRED (2026-04-19)

All 5 Tier 1 methods installed and GPU-verified on RTX 5000 Ada:
- GEARS: Working, peak 7.73 GB, no OOM risk (env-delta-v2)
- scGPT: Working, peak 6.78 GB, pretrained model loaded (env-delta-v2)
- CPA: Working, peak 0.11 GB, isolated in env-cpa (yml ready)
- **scFoundation: Working, 119M params, peak 22.2 GB, 99.4% Tahoe gene coverage (env-delta-v2, SLURM 8705048)**
- **Tahoe-x1 3B: Working, 2.7B params, peak 16.7 GB, 100% Tahoe gene coverage (env-tahoex1, SLURM 8709432)**

**Baselines COMPLETE 2026-04-19** (Sub 1.2 task-005):
- linear, mean, PCA, random, persistence — all 5 implemented at `phases/phase-1/subphase-1.2/output/scripts/delta/baselines/`
- WMSE harness at `.../eval/wmse.py` with `hierarchical_wmse_spearman`
- FDR (`fdr.py`: BH primary, BY sensitivity)
- Calibration (`calibration.py`: reliability diagram, ECE)
- Stratified eval (`stratified.py`: per cell×perturbation×expression)
- Smoke test ran end-to-end on 100K-cell Tahoe-100M subsample (train 72,810 / test 27,190)
- **Metric-gaming check: random baseline FAILS WMSE gate at top level AND all 48 cell-type strata** (IP §12.4 calibration check is robust)

Detailed install log: `shared/notes/1.1-delta-methods-install.md`.
Baselines results + D3 retirement note: `shared/notes/1.2-delta-baselines-results.md`.

### T3 Evidence (effectively retired)

HEWL SG-SG integrity = 40.2% at 2.5A cutoff (AK3 triggered at ALL cutoffs). BPTI
dropped earlier (56.1% CB-CB). Crambin (stability control only) also triggers
AK3 at 14.2% SG-SG. With all 3 SS-bearing proteins either dropped or
stability-control-only, T3 has no benchmark subjects — criterion effectively
retired. Methods section should note this explicitly.

### T5 Evidence (post-expansion, 2026-04-17)

Benchmark expanded from 12 to 16 proteins (added NTL9, ACBP, FKBP12, EnHD; all 0
SS bonds, Garnet-clean). BioEmu v1.1 pass rates: NTL9 96%, ACBP 98%, FKBP12
100%, EnHD 99%. All viable. S2 provenance: EnHD has BMRB-confirmed 58 S2 entries
(BMRB 15536); NTL9/ACBP/FKBP12 have paper-supplement S2.

Concurrent HPr S2 verification found the cited paper (van Nuland 1995 JMB
246:180) contains no relaxation data. Post-expansion T5 survives HPr exclusion
with margin: 14/16 PASS (HPr excluded) or 15/16 PASS (HPr retained
non-quantitatively). Previous boundary (12/12) eliminated.

T5 **status: MET with 2-3 protein margin.**

## Gate Assessments

| Gate | Assessment File | Date | Verdict |
|------|----------------|------|---------|
| D3 (early + amended) | [phases/phase-1/gate-D3-assessment.md](../phases/phase-1/gate-D3-assessment.md) | 2026-04-17 | GO (upgraded from CONDITIONAL same-day after scFoundation + Tahoe-x1 installs) |
| D1 (early) | [phases/phase-1/gate-D1-assessment.md](../phases/phase-1/gate-D1-assessment.md) | 2026-04-17 | GO |
