---
last_updated: 2026-04-17T23:59:00Z
updated_by: subagent-h (pre-Sub-1.2 flag closure)
---

# Gate Tracker

## Decision Gates (from Implementation Plan Section 13)

| Gate | Date | Decision | Status | Assessment |
|------|------|----------|--------|------------|
| D1 | May 9 | MLFF software GO | ASSESSED: GO | Both MACE + SO3LR pass; MACE via OpenCL (CUDA broken on all GPUs); Phase 2 via hybrid mode, 1.40× compute multiplier |
| D2 | June 30 | MLFF pilot GO (G1-G6) | ON TRACK | G1 achievable on H200 OpenCL. Empirical H200 hybrid WW = 2.11 ns/day measured (SLURM 8789805, 2026-04-18) → 11.5× RTX 5000 Ada speedup. Phase 2 MACE committed to Option 5 (gpu_h200 partition). UBQ extrapolated ~0.85 ns/day → 10 ns in ~12 days, feasible. |
| D3 | June 6 | Delta scope lock | ASSESSED: GO | 5/5 Tier 1 installed + GPU-verified (GEARS, scGPT, CPA, scFoundation, Tahoe-x1). Baselines owed in Sub 1.2. Amended 2026-04-17 from CONDITIONAL. |
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

### D3 Evidence — FULLY MET (upgraded 2026-04-17)

All 5 Tier 1 methods installed and GPU-verified on RTX 5000 Ada:
- GEARS: Working, peak 7.73 GB, no OOM risk (env-delta-v2)
- scGPT: Working, peak 6.78 GB, pretrained model loaded (env-delta-v2)
- CPA: Working, peak 0.11 GB, isolated in env-cpa (yml ready)
- **scFoundation: Working, 119M params, peak 22.2 GB, 99.4% Tahoe gene coverage (env-delta-v2, SLURM 8705048)**
- **Tahoe-x1 3B: Working, 2.7B params, peak 16.7 GB, 100% Tahoe gene coverage (env-tahoex1, SLURM 8709432)**

Baselines (linear, mean, PCA, random, persistence) still owed — scheduled for Sub 1.2.
Detailed install log: `shared/notes/1.1-delta-methods-install.md`.

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
