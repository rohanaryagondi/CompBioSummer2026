---
last_updated: 2026-04-15
updated_by: PlannerAI
---

# Gate Tracker

## Decision Gates (from Implementation Plan Section 13)

| Gate | Date | Decision | Status | Assessment |
|------|------|----------|--------|------------|
| D1 | May 9 | MLFF software GO | PENDING | -- |
| D2 | June 30 | MLFF pilot GO (G1-G6) | PENDING | -- |
| D3 | June 6 | Delta scope lock | PENDING | -- |
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

## Gate Assessments

| Gate | Assessment File | Date |
|------|----------------|------|
| (none yet) | -- | -- |
