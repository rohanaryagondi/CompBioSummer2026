---
task_id: task-004
agent: bioemu-test
date: 2026-04-16T02:30:00Z
type: experiment-report
---

# BioEmu Disulfide Bond Integrity Report

**Date:** 2026-04-16T02:30:00Z
**BioEmu model:** bioemu-v1.1 (bioemu v1.3.1)
**Conformations per protein:** 100 requested (BPTI: 98 passed filter, HEWL: 99 passed filter)
**GPU:** RTX 5000 Ada (33.8 GB VRAM), SLURM job 8371740
**Distance metric:** CB-CB (see Methodology Note below)
**Primary cutoff:** 4.5 Angstrom (standard crystallographic CB-CB for disulfide bonds)

---

## Methodology Note: CB-CB vs SG-SG Distance

BioEmu v1.3.1 outputs only 5 atoms per residue: N, CA, C, CB, O. **No sidechain
atoms (including SG) are generated.** Therefore, disulfide bond integrity cannot be
measured using the standard SG-SG distance (typical: ~2.05 A for intact SS bonds).

Instead, we use **CB-CB distance** as a proxy. In crystal structures of proteins
with intact disulfide bonds, the CB-CB distance between bonded cysteines is
typically **3.8 A** (range 3.4-4.2 A). We use a cutoff of **4.5 A** as the
primary threshold, which accounts for thermal fluctuations in the BioEmu-generated
conformational ensemble. We also report at 5.0 A and 5.5 A for sensitivity analysis.

This is a known limitation of BioEmu's backbone-only output format. Any future
pipeline that requires SG-SG distances will need sidechain reconstruction
(e.g., via SCWRL4 or Rosetta packing).

---

## BPTI (57 residues, 3 disulfide bonds)

### At 4.5 A cutoff (primary)

**Overall integrity: 56.1%** (55/98 conformations with ALL 3 bonds intact)

| Bond | Integrity | Mean dist | Std | Min | Max |
|------|-----------|-----------|-----|-----|-----|
| Cys5-Cys55 | 86.7% (85/98) | 6.37 A | 8.01 A | 2.98 A | 44.47 A |
| Cys14-Cys38 | 57.1% (56/98) | 6.44 A | 4.65 A | 3.26 A | 24.59 A |
| Cys30-Cys51 | 90.8% (89/98) | 5.00 A | 4.39 A | 3.13 A | 29.50 A |

### At 5.0 A cutoff

**Overall integrity: 67.3%** (66/98)

| Bond | Integrity |
|------|-----------|
| Cys5-Cys55 | 88.8% (87/98) |
| Cys14-Cys38 | 67.3% (66/98) |
| Cys30-Cys51 | 90.8% (89/98) |

### At 5.5 A cutoff

**Overall integrity: 72.4%** (71/98)

| Bond | Integrity |
|------|-----------|
| Cys5-Cys55 | 88.8% (87/98) |
| Cys14-Cys38 | 72.4% (71/98) |
| Cys30-Cys51 | 90.8% (89/98) |

**Notes:**
- Cys14-Cys38 is the weakest bond, with the lowest per-bond integrity at all cutoffs.
- High standard deviations (4-8 A) indicate a bimodal distribution: most conformations
  keep bonds near native distance, but a significant fraction show large excursions
  (>10 A), suggesting partially unfolded states in the BioEmu ensemble.
- Generation time: 266.2s (4.4 min) for 100 conformations.

---

## HEWL (129 residues, 4 disulfide bonds)

### At 4.5 A cutoff (primary)

**Overall integrity: 70.7%** (70/99 conformations with ALL 4 bonds intact)

| Bond | Integrity | Mean dist | Std | Min | Max |
|------|-----------|-----------|-----|-----|-----|
| Cys6-Cys127 | 90.9% (90/99) | 4.11 A | 1.04 A | 3.03 A | 12.96 A |
| Cys30-Cys115 | 97.0% (96/99) | 3.90 A | 1.10 A | 3.16 A | 12.91 A |
| Cys64-Cys80 | 92.9% (92/99) | 4.04 A | 0.33 A | 3.33 A | 4.90 A |
| Cys76-Cys94 | 88.9% (88/99) | 4.12 A | 0.56 A | 3.31 A | 8.54 A |

### At 5.0 A cutoff

**Overall integrity: 90.9%** (90/99)

| Bond | Integrity |
|------|-----------|
| Cys6-Cys127 | 94.9% (94/99) |
| Cys30-Cys115 | 98.0% (97/99) |
| Cys64-Cys80 | 100.0% (99/99) |
| Cys76-Cys94 | 98.0% (97/99) |

### At 5.5 A cutoff

**Overall integrity: 93.9%** (93/99)

| Bond | Integrity |
|------|-----------|
| Cys6-Cys127 | 97.0% (96/99) |
| Cys30-Cys115 | 98.0% (97/99) |
| Cys64-Cys80 | 100.0% (99/99) |
| Cys76-Cys94 | 99.0% (98/99) |

**Notes:**
- HEWL is substantially better than BPTI. Lower standard deviations (0.3-1.1 A vs 4-8 A)
  indicate the HEWL ensemble is more structurally coherent.
- Cys64-Cys80 is nearly perfect at all cutoffs (this is a buried bond in the protein core).
- Cys6-Cys127 is the weakest (terminal residues, more flexible).
- Generation time: 569.8s (9.5 min) for 100 conformations.

---

## THRESHOLD ASSESSMENT

### At primary cutoff (4.5 A, CB-CB)

**T3 (>95% integrity for combined paper GO):**
  - BPTI: **NOT MET** (56.1%)
  - HEWL: **NOT MET** (70.7%)

**AK3 (<80% integrity triggers BPTI/HEWL drop from benchmark):**
  - BPTI: **TRIGGERED** (56.1% < 80%)
  - HEWL: **TRIGGERED** (70.7% < 80%)

### Sensitivity to cutoff choice

| Cutoff | BPTI overall | HEWL overall | BPTI AK3 | HEWL AK3 |
|--------|-------------|-------------|-----------|----------|
| 4.5 A | 56.1% | 70.7% | TRIGGERED | TRIGGERED |
| 5.0 A | 67.3% | 90.9% | TRIGGERED | NOT triggered |
| 5.5 A | 72.4% | 93.9% | TRIGGERED | NOT triggered |

### Zone Interpretation

- **BPTI:** RED at all cutoffs. AK3 triggered regardless of cutoff choice.
  The Cys14-Cys38 bond is consistently problematic (57.1-72.4% across cutoffs).
  BPTI should be dropped from the benchmark.

- **HEWL:** AMBER at 4.5 A (AK3 triggered), GREEN at 5.0+ A (AK3 not triggered).
  HEWL's status depends on the cutoff interpretation. At the conservative 4.5 A
  crystallographic cutoff, AK3 is triggered. At a more permissive 5.0 A cutoff
  (accounting for BioEmu's generative noise), HEWL passes with 90.9%.

---

## Recommendations

1. **BPTI should be dropped from the combined benchmark.** AK3 is triggered at
   all reasonable CB-CB cutoffs. This reduces the protein count from 14 to 13,
   which still satisfies T5 (>=12 proteins).

2. **HEWL requires a cutoff interpretation decision.** At the strict 4.5 A cutoff,
   AK3 is triggered and HEWL should also be dropped (leaving 12 proteins, T5 still
   met). At 5.0 A, HEWL passes comfortably. This decision should be made by
   PlannerAI in consultation with the scientific rationale.

3. **The CB-CB proxy limitation should be documented** in the combined paper
   methodology. BioEmu's backbone-only output is a known limitation that affects
   disulfide bond quality assessment.

4. **Cross-agent note required** documenting these findings for Alpha-M and
   combined paper tracks.

---

## Raw Data

- BPTI distances: `output/task-004-bpti-ss-distances.csv`
- HEWL distances: `output/task-004-hewl-ss-distances.csv`
- BPTI conformations: `output/task-004-bpti/topology.pdb` + `samples.xtc` (98 frames)
- HEWL conformations: `output/task-004-hewl/topology.pdb` + `samples.xtc` (99 frames)
- Plots: `output/task-004-bpti-ss-plot.png`, `output/task-004-hewl-ss-plot.png`, `output/task-004-combined-ss-histogram.png`
