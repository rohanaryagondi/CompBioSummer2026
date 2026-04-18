---
phase: 1
title: "Pilot Studies and Setup"
date_range: "2026-04-17 to 2026-06-30"
tracks: [alpha-m, gamma, delta]
status: active
created: 2026-04-16
---

# Phase 1: Pilot Studies and Setup

## Executive Summary

Phase 1 transforms the computational infrastructure from Phase 0 into functioning
simulation and analysis pipelines across all three tracks. The primary goal is to
validate that the core methods work at all (D1: MACE/SO3LR software, May 9), that
they produce usable data (D2: MLFF pilot GO/NO-GO, June 30), and that Delta's
methods can handle Tahoe-100M (D3: scope lock, June 6). Phase 0 completed 14 days
ahead of schedule, so Phase 1 starts immediately (April 17) with extra buffer before
D1. This phase is complete when MLFF pilot trajectories exist on >=3 benchmark
proteins, BioEmu ensembles cover >=100 ProteinGym proteins, Gamma's ML pipeline is
operational, and Delta's evaluation framework produces calibrated results on a test
split.

**Phase 0 decisions applied:** BPTI dropped from benchmark (AK3 triggered, 56.1%
SS integrity). HEWL conditionally retained pending sidechain reconstruction results
(Subphase 1.1). Benchmark set: 13 proteins (T5 met with margin).

**Subphase 1.1 outcomes (CLOSED 2026-04-18):** HEWL DROPPED (SG-SG integrity 40.2%).
Benchmark expanded +4 proteins (NTL9, ACBP, FKBP12, EnHD) for T5 margin recovery.
HPr retained but marked non-S2 (citation found empty). T4L reference locked to
Mulder 2000 Biochem 39:12614. **Current benchmark: 16 active proteins, T5 counted
= 14/16 (2-protein margin).** See `shared/notes/1.1-protein-count-canonical.md`
for authoritative counts.

**Subphase 1.1 MACE Phase 2 scope outcome:** Options 2 (OpenMM CUDA rebuild) and
4 (implicit solvent MACE) empirically REJECTED. **Option 5 (H200 OpenCL) committed**
as Phase 2 MACE primary path — measured 2.11 ns/day on hybrid WW = 11.5× RTX 5000
Ada. Phase 2 MACE compute budget revised 47,300 → ~3,300 GPU-hrs. See
`shared/help-needed/sub-1.2-phase2-mlff-scope.md` (resolved) and
`shared/notes/1.1-mace-hybrid-validation.md` §11.

**Subphase 1.1 Delta outcome:** All 5/5 Tier 1 methods installed + GPU-verified
(GEARS, scGPT, CPA, scFoundation, Tahoe-x1). D3 gate upgraded CONDITIONAL → GO.
env-delta split into env-delta-v2 + env-cpa + env-tahoex1. See
`shared/notes/1.1-delta-methods-install.md` and `1.1-env-split.md`.

---

## Subphase Breakdown

| Subphase | Title | Date Range | Tracks | Tasks | Key Deliverable |
|----------|-------|------------|--------|-------|-----------------|
| 1.1 | MLFF Software Validation & Early Setup | Apr 17 - May 2 | Alpha-M, Gamma, Delta | 6 + remediation | **COMPLETE 2026-04-18.** MACE+SO3LR D1 PASS, BioEmu batch 1 (46/47), all 5/5 Delta Tier 1, HEWL DROP, benchmark expanded +4 proteins, MACE Option 5 committed. See `subphase-1.1/completion-report.md` + `shared/notes/1.1-robustness-remediation.md`. |
| 1.2 | Stability Tests & Second Wave Setup | May 3 - May 16 | Alpha-M, Gamma, Delta | 5-7 | NPT stability on 3 proteins, BioEmu batch 2, scFoundation+Tahoe-x1, OSF pre-reg |
| 1.3 | Remaining Setup, Features, Delta Baselines | May 17 - Jun 6 | Alpha-M, Gamma, Delta | 5-7 | Garnet+a99SB-disp, feature extraction pipeline, Delta baselines+AetherCell |
| 1.4 | MLFF Pilot Production & Analysis | Jun 7 - Jun 30 | Alpha-M, Gamma, Delta | 6-8 | MLFF 10-50ns on 3 Tier A/B proteins, ML pipeline, pilot analysis, S2 convergence |

**Note:** Only Subphase 1.1 is planned in detail. Subphases 1.2-1.4 are planned
one-at-a-time after their predecessor completes (the "Only Plan Next" rule).

---

## Resource Allocation

### Compute

| Track | GPU-Hours (this phase) | GPU Type | Notes |
|-------|----------------------|----------|-------|
| Alpha-M | 2,000-3,000 | H200 | MLFF pilots (Sub 1.4) dominate; crambin tests ~20 hrs |
| Gamma | 500-800 | Any | BioEmu generation for ~100 ProteinGym proteins |
| Delta | 2,000-5,000 | RTX 5090 | Method training + evaluation on Tahoe-100M subsets |

### Storage

| Data | Size | Location |
|------|------|----------|
| MLFF pilot trajectories (crambin + 3 proteins) | ~50 GB | HPC scratch |
| BioEmu ensembles (100 proteins x 2000 conf) | ~2 GB | HPC scratch |
| Delta method checkpoints + test outputs | ~20 GB | HPC scratch |
| Gamma feature matrices | ~5 GB | HPC scratch |

---

## Decision Gates in This Phase

| Gate | Date | Decision | Criteria | If NO-GO |
|------|------|----------|----------|----------|
| D1 | May 9 | MLFF software GO | MACE + SO3LR each run 1 ns NVT on crambin | Drop failed MLFF, proceed with remainder |
| D3 | June 6 | Delta scope lock | >=3 of 5 Tier 1 DL methods running | Drop failed methods, proceed with remainder |
| D2 | June 30 | MLFF pilot GO (G1-G6) | >=1 MLFF stable >10 ns on >=3 Tier B proteins; S2 non-degenerate; ICC >0.80; JSD >0.01 for >=3 pairs | Alpha-M becomes classical+generative only |

---

## Dependencies

### From Prior Phases
- Phase 0: All 9 conda environments (env-mace, env-so3lr, env-bioemu, env-delta, etc.)
- Phase 0: 14 PDB files + manifest.json (`phases/phase-0/subphase-0.1/proteins/`)
- Phase 0: BMRB S2 verification table (13/14 proteins confirmed)
- Phase 0: BioEmu SS integrity results (BPTI drop, HEWL conditional)
- Phase 0: Tahoe-100M downloaded at `/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/`
- Phase 0: env-mace and env-so3lr build notes (D1 early signal: both positive)

### Updated after Sub 1.1 closure (2026-04-18)

Current benchmark state for Sub 1.2+ planning:
- **Proteins:** 18 manifest entries / 16 active (BPTI+HEWL kept as historical
  records but dropped from benchmark) / 14 S2-counted (Crambin is stability
  control only, HPr is non-S2 per Option A). See
  `shared/notes/1.1-protein-count-canonical.md` for authoritative counts.
- **New proteins added:** NTL9, ACBP, FKBP12, EnHD (all BioEmu-validated).
- **Envs:** env-delta split into env-delta-v2 (primary) + env-cpa (CPA-only,
  yml ready) + env-tahoex1 (Tahoe-x1 only). env-mace has pdbfixer==1.12.0
  added. See `shared/notes/1.1-env-split.md`.
- **Delta Tier 1:** 5/5 methods installed + GPU-verified (GEARS, scGPT, CPA,
  scFoundation, Tahoe-x1). D3 gate = GO.
- **Phase 2 MACE path:** Option 5 (H200 OpenCL) committed. Measured 2.11 ns/day
  on hybrid WW. Phase 2 MACE budget ~3,300 GPU-hrs. See
  `shared/help-needed/sub-1.2-phase2-mlff-scope.md` (resolved).

### For Future Phases
- Phase 2 requires: MLFF pilot trajectories, established simulation protocols, S2 back-calculation pipeline
- Phase 2 requires: BioEmu ensembles for >=100 proteins, feature extraction pipeline
- Phase 2 requires: Delta evaluation framework with calibrated metrics, all methods running
- Phase 2 requires: OSF pre-registration (May 15) locking analysis plan
- Phase 2 requires: D2 GO/NO-GO decision (determines MLFF scope for production)

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| MACE-OFF24 OpenMM-ML integration fails | 25% | D1 partial failure for MACE | Stage A/B/C approach: vacuum -> explicit -> hybrid. If all fail, drop MACE. |
| SO3LR JAX-MD simulation fails on GPU | 20% | D1 partial failure for SO3LR | Consult SO3LR docs/examples. JAX GPU issues often version-related. |
| Both MLFFs fail on crambin | 10% | D1 NO-GO for both | Alpha-M continues as classical+generative benchmark (still NatMeth publishable) |
| GEARS memory exceeds available GPU RAM on Tahoe-100M | 30% | Delta method gap | scDataset streaming, cap loaded cells, subsample perturbation conditions |
| BioEmu MSA server unreachable from compute nodes | 20% | Delays Gamma batch gen | Run first protein on login node to cache embeddings, then SLURM for rest |
| CPA (2023 release) incompatible with current PyTorch | 25% | Delta method gap | Try pinned version; if fails, document and proceed with 2 of 3 methods |
| HEWL sidechain recon shows <80% SG-SG integrity | 30% | Drop HEWL, 12 proteins (T5 boundary) | Still meets T5; document CB-CB vs SG-SG comparison as methodological finding |

---

## Success Criteria

This phase is complete when ALL of the following are true:

1. D1 gate assessed: MACE and SO3LR crambin NVT results documented
2. D2 gate assessed: MLFF pilot GO/NO-GO with G1-G6 criteria evaluated
3. D3 gate assessed: Delta scope lock with method availability documented
4. >=1 MLFF produces stable trajectory on crambin AND >=1 Tier B protein
5. BioEmu ensembles generated for >=100 ProteinGym proteins
6. Gamma feature extraction pipeline produces per-residue dynamics features
7. Delta evaluation framework produces calibrated metric results on test split
8. OSF pre-registration submitted by May 15
9. HEWL disposition finalized (keep or drop based on SG-SG data)
10. All subphase completion reports written
11. All gate assessments written
12. Dashboards updated
