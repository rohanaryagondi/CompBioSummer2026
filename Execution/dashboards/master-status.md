---
last_updated: 2026-04-18T04:00:00Z
updated_by: planner (post-audit cleanup)
---

# Master Status: CompBioSummer2026 Execution

## Current State

| Item | Value |
|------|-------|
| Current phase | Phase 1: Pilot Studies and Setup |
| Current subphase | 1.1: MLFF Software Validation & Early Setup |
| Subphase status | **CLOSED 2026-04-18** (complete + post-subphase robustness remediation + Options 2/4/5 MACE investigation) |
| Next action | Plan subphase 1.2 |

---

## Decision Log

| Decision | Resolution | Date | Impact |
|----------|-----------|------|--------|
| BPTI benchmark drop | **DROP.** AK3 triggered at all cutoffs (56.1-72.4%) | 2026-04-16 | 14 -> 13 proteins. T5 still met. |
| HEWL benchmark drop | **DROP.** SG-SG integrity 40.2% (AK3 triggered at ALL cutoffs) | 2026-04-16 | 13 -> 12 proteins. T5 at boundary. |
| Phase 1 start date | **IMMEDIATE** (April 17). Extra buffer before D1. | 2026-04-16 | 3 weeks before D1 instead of 1 |
| D1 MLFF gate | **BOTH PASS.** MACE + SO3LR stable NVT on crambin | 2026-04-16 | Both MLFFs viable for pilots |
| YAP1_HUMAN drop | **DROP.** 0.7% BioEmu pass rate (IDP, 504 aa). 10K NPZ preserved. | 2026-04-17 | 47→46 proteins, 50→49 assays. 6/7 binding remain. |
| **Benchmark expansion** | **ADD 4: NTL9, ACBP, FKBP12, EnHD.** BioEmu pass rates 96/98/100/99%. 0 SS bonds, Garnet-clean. EnHD has BMRB-confirmed S2. See `shared/notes/1.1-protein-count-canonical.md` for authoritative counts. | 2026-04-17 | 12 → **16 active proteins** (18 manifest entries); T5: 11/12 boundary → **14/16 with 2-protein margin** (post-Option-A HPr) |
| HPr S2 citation invalid | **RESOLVED: Option A.** van Nuland 1995 JMB 246:180 contains NO S2 data; no alternative found. User chose to retain HPr for structural + stability comparison only; excluded from quantitative S2. | 2026-04-17 | T5 survives HPr exclusion: 14/16 MET with 2-protein margin |
| T4L citation locked | **RESOLVED.** Prior "Mulder 2001 Biochemistry 40:4458" was a transcription error for Mulder 2000 Biochemistry 39:12614-12622, which DOES contain WT T4L backbone 15N relaxation side-by-side with L99A. Primary S2 reference locked. See `shared/notes/1.1-t4l-s2-candidates.md`. | 2026-04-17 | No reference-state mismatch; cavity-region caveat narrowed to within-paper stratification |
| Crambin SG-SG | **DOCUMENTED CAVEAT.** 14.2% SG-SG integrity, BioEmu ensemble unreliable. Stability control only, T3 N/A. | 2026-04-17 | Methods-section annotation required |
| D3 Delta scope lock | **UPGRADED CONDITIONAL → GO.** scFoundation (env-delta-v2) + Tahoe-x1 3B (env-tahoex1) installed + GPU-verified. 5/5 Tier 1 methods now running. env-tahoex1 created due to flash-attn/torch incompatibility in env-delta-v2. | 2026-04-17 | D3 formal gate (Jun 6) no longer needs re-assessment; baselines task owed in Sub 1.2 |
| **MACE hybrid throughput** | **ESCALATED — user decision needed.** Empirical RTX 5000 Ada OpenCL throughput 8.7× slower than projected (WW 0.184, GB3 0.111, UBQ 0.074 ns/day). D1 GO holds (API works, stable dynamics). Phase 2 IP-scope MACE infeasible on current hardware. | 2026-04-18 | 4 options in `shared/help-needed/sub-1.2-phase2-mlff-scope.md`: (1) reduce scope 2-3 Tier A × 3-5 ns, (2) OpenMM CUDA 12.4+ rebuild, (3) SO3LR-primary vacuum path, (4) implicit-solvent MACE pilot. D2 G1 criterion AT RISK. Blocks Sub 1.2 MACE task spec. |
| **MACE Option 2 + 4 empirical** | **Option 4 REJECTED** (1.07× speedup; MACE inference is the bottleneck not water). **Option 2 PARTIAL SUCCESS** (CUDA rebuild works on RTX 5000 Ada; interop bug 1-2 hr follow-up). **NEW Option 5 EMERGED**: H200 OpenCL is 11× RTX 5000 Ada OpenCL → Phase 2 IP-scope likely feasible on H200 without rebuild. Empirical H200 hybrid WW benchmark in flight (SLURM 8789805). | 2026-04-18 | Revised recommendation: Option 5 primary + Option 2 as Sub 1.2 optimization. D2 G1 likely OK if H200 benchmark confirms. |
| **Option 5 CONFIRMED** | **H200 hybrid WW = 2.11 ns/day measured** (11.5× RTX 5000 Ada, matches extrapolation). Phase 2 IP-scope MACE committed to H200 OpenCL. Job hung post-step-7000 → cancelled proactively (unrelated to throughput result). Hang investigation deferred to Sub 1.2 via openmm-torch migration + GPU keepalive. | 2026-04-18 | Phase 2 MACE compute budget revised down to ~3,300 GPU-hrs baseline (from 47,300) — releases ~44,000 GPU-hrs to contingency. D2 G1 now achievable. |
| **Option 2 REJECTED** | Subagent L completed the CUDA rebuild investigation. Interop fix (A+B combo) works for narrow cases only. Crambin vacuum CUDA on RTX 5000 Ada = 0.142 ns/day = **1.0× OpenCL baseline — zero speedup**. Hybrid + H200 CUDA failed with interop crash. Root cause: MACE-OFF24 is **inference-bound on PyTorch CUDA**; OpenMM backend choice is irrelevant. | 2026-04-18 | Rebuild not useful. env-mace-cuda + build artifacts deleted. openmm-torch follow-up (originally 1-2 hr) deprioritized — expected speedup is minimal. Phase 2 MACE path unchanged (Option 5). |
| **Phase 1.1 CLOSED** | All remediation and empirical work complete. Options 2+4 REJECTED, Option 5 committed. 16 active benchmark proteins (T5 margin 2). 5/5 Delta Tier 1 methods. D1+D3 GO. Competition scan infra ready. All 10 YELLOW audit items fixed. | 2026-04-18 | Ready for Sub 1.2 planning. |

---

## Per-Track Status

| Track | Status | Latest Milestone | Next Milestone |
|-------|--------|-----------------|----------------|
| Alpha-M | D1 evidence collected + benchmark expanded to 16 active; HPr + T4L resolved | MACE/SO3LR D1 PASS; +NTL9/ACBP/FKBP12/EnHD; HPr Option A; T4L Mulder 2000 locked | MLFF pilot on Tier 1 proteins |
| Gamma | Batch 1 complete | 46/47 proteins, 112,351 physical conformations | Feature extraction, batch 2 planning |
| Delta | 5/5 Tier 1 methods installed | GEARS + scGPT + CPA + **scFoundation + Tahoe-x1 3B** all GPU-verified; D3 upgraded to GO | Baselines (linear, mean, PCA, random, persistence); Sub 1.2 ML pipeline |
| Combined | HEWL dropped, 12 proteins | T3 resolved (DROP), T5 at boundary | Depends on Alpha-M + Gamma progress |

---

## Timeline: Planned vs Actual

| Phase | Planned Start | Planned End | Actual Start | Actual End | Status |
|-------|-------------|------------|-------------|------------|--------|
| Phase 0 | Apr 15 | Apr 30 | Apr 15 | Apr 16 | **Complete** |
| Phase 1 | Apr 17 | Jun 30 | Apr 16 | — | **In progress (sub 1.1 complete)** |
| Phase 2 | Jul 1 | Aug 22 | — | — | Not started |
| Phase 3 | Aug 23 | Nov 30 | — | — | Not started |

---

## Active Blockers

None.

---

## Decisions Needed

1. **Phase 2 MACE scope** (HIGH urgency, 2026-04-18). Empirical OpenCL hybrid throughput 8.7× slower than projected; IP scope infeasible on current hardware. 4 options in `shared/help-needed/sub-1.2-phase2-mlff-scope.md`. Recommended: Option 1 (reduced scope) + Option 4 diagnostic (implicit-solvent pilot). Blocks Sub 1.2 MACE task spec.

---

## Upcoming Milestones

| Date | Milestone | Gate |
|------|-----------|------|
| ~~Apr 30~~ | ~~Phase 0 complete~~ | — | **Done (Apr 16)** |
| ~~May 2~~ | ~~Subphase 1.1 complete (target)~~ | — | **Done (Apr 17)** |
| May 9 | MLFF software GO | D1 |
| May 15 | OSF pre-registration | — |
| ~~May 31~~ | ~~Tahoe-100M download deadline~~ | ~~DK1~~ | **Done (Apr 16)** |
| Jun 6 | Delta scope lock | D3 |
| Jun 30 | MLFF pilot GO | D2 |
| Jul 31 | Integration signal | D4 |
| Aug 15 | Delta preprint | D5 |
| Aug 31 | Combined paper GO/NO-GO | D6 |
| Sep 15 | Phase 3 scope | D7 |
