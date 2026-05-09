---
last_updated: 2026-05-05T18:00:00Z
updated_by: head-1.2 (bioemu-reorg subagent; Round-4 BioEmu reorg #1+#2+#6+#7 applied — arrays 9449458/9449459 replaced by 3-tier 10730244/10730245/10730246 split with L<200→Standard gpu)
---

# Master Status: CompBioSummer2026 Execution

## Current State

| Item | Value |
|------|-------|
| Current phase | Phase 1: Pilot Studies and Setup |
| Current subphase | **1.2: MLFF Stability Pilots, BioEmu Batch 2, Delta Baselines, OSF Pre-Registration** |
| Subphase status | **CLOSURE WINDOW IN FLIGHT 2026-05-05 (BioEmu reorg applied)** — 10 jobs PENDING: MACE WW prod 10567503 (q6wmsv5n) + MACE GB3 prod 10567504 (q6gpsv9k) + SO3LR rescues 10567505/06/07 (g7p4tv8m/n5h6kx9q/w8q4r3xz) all on `scavenge_gpu`; **BioEmu batch 2 reorganized 2026-05-05 from arrays 9449458/9449459 → 3-tier split**: 10730244 (q6sht3az, 53 short L<200, **Standard `gpu` 6h**), 10730245 (q6med7kp, 18 medium L=200-499, scav 12h), 10730246 (q6lng5wm, 11 long L≥500, scav 24h); plus NTL9 50ps probe 10622876 (q6kz3m8x; UBQ option-c) + UBQ_alt 1XQQ 50ps probe 10622885 (q6uadt05; UBQ option-d). **Probe verdicts (terminal pre-handoff)**: GB3 MACE PASSED 25 ps clean; UBQ MACE NPT non-generalizing across dt={1.0/0.5/0.25} fs (NaN @ 7-9.6 ps regardless) — escalated via `shared/help-needed/head-1.2-mace-ubq-non-generalization.md`; SO3LR GB3+NTL9+WW gates submitted on priority then cancelled (WW gate cancelled by SU enforcer; rescues now full 5ns on scavenge). **3 cumulative optimization rounds applied** (~30-35% MACE throughput, ~10-15% SO3LR; full audit-trail in 1.2-mace-npt-stability §8 + 1.2-so3lr-rescue-results). **SU enforcement**: `prio_su_enforce.sh` + budget cap reduced 800→250 SU; tracker shows 231.5/250 used. **OSF v3 6-issue fixes APPLIED 2026-05-03** (incl. substantive D-OSF-SO3LR §4 commit to neutral-protonation methodology). **D-UBQ-1 PARTIALLY UNBLOCKED**: options (c) NTL9 substitute + (d) UBQ_alt 1XQQ both probed; verdicts pending dispatch. **4 background subagents in flight** (Item A NPZ cleanup, Item H trajectory skeletons, Item I RMSF+RSALOR, Item D walltime classification). |
| Next action | Wait for scavenge_gpu dispatch of 9 PENDING jobs. Surface UBQ option-c/d probe verdicts to user when terminal. User to deposit OSF target 2026-05-13. If no scavenge dispatch by 2026-05-09, surface contingency move to Standard tier (10× more expensive, requires user approval per 3× partition rule). |
| Handoff doc | [phases/phase-1/subphase-1.2/handoff-successor-2026-05-04.md](../phases/phase-1/subphase-1.2/handoff-successor-2026-05-04.md) (supersedes 2026-05-02 `handoff-notes.md`) |

---

## Decision Log

| Decision | Resolution | Date | Impact |
|----------|-----------|------|--------|
| **BioEmu batch 2 Round-4 reorg** | Per round-4 study + user approval (recs #1+#2+#6+#7): cancelled PENDING arrays 9449458 (x9sok7yl) + 9449459 (l5uw4lsy) on `scavenge_gpu` (PENDING-Priority for 10+ days) and resubmitted as 3-tier walltime split: **10730244 q6sht3az** (53 short L<200, 6h, Standard `gpu`, mem=24G), **10730245 q6med7kp** (18 medium L=200-499, 12h, scavenge_gpu, mem=40G), **10730246 q6lng5wm** (11 long L≥500, 23:59h, scavenge_gpu, mem=40G). All on RTX 5000 Ada with `--cpus-per-task=4` (was 2). 3 new sbatch files in `output/scripts/` reuse all locked logic (env-bioemu, GPU keepalive, length-aware batch_size_100, oversampling formula, NPZ cleanup). | 2026-05-05 | Expected: short cohort (53 proteins) clears within hours via Standard `gpu` backfill (LevelFS unrelated to scavenge); medium cohort gets shorter walltime ceiling on scavenge → improved backfill; long cohort unchanged. +205 SU acceptable per user approval. No physics/output-distribution change (OSF v3 §7 LOCKED settings preserved verbatim). |
| **scavenge_gpu pivot + 3 optimization rounds applied** | All 7 closure jobs moved to `scavenge_gpu` (1/10 Standard billing). 3 cumulative optimization rounds: (R1) MACE constant-tensor pre-alloc, NaN/checkpoint cadence, constraint tol 1e-4, drop speed=True; SO3LR md_steps×5, JAX cache. (R2) MACE DCD 5ps stride, equil 25ps, OMP/MKL=4; SO3LR md_steps→10000, save-buffer→5; audit-revert SO3LR buffers to defaults 1.25/1.25 (silent NL underflow risk at t=0). (R3) XLA Triton GEMM flags, NUMA OMP_PROC_BIND, drop forces from check_nan, MAX_MIN_ITER 500. Total ~30-35% MACE throughput + ~10-15% SO3LR + 90% billing reduction = ~92-93% SU savings vs original baseline. | 2026-05-03 | Sub 1.2 closure SU footprint: ~3,500 SU worst-case (vs ~38,000 original projection). Optimizations transferable to Sub 1.4 production. Recipe physics LOCKED — Round 3 recipe per OSF §4 unchanged. |
| **UBQ MACE NPT non-generalizing** | Recipe NaN @ 7-9.6 ps regardless of dt halving (1.0/0.5/0.25 fs all fail; pattern asymptotic). Failure is architectural for UBQ-class system size (~17K atoms / ~1.2K MACE atoms). Help-needed `head-1.2-mace-ubq-non-generalization.md` written. Auditor + project-context reviewer both recommend option (a) NVT pivot (documented R1 fallback per closure-master-plan; OSF §10 sensitivity tables B.3/B.4 already pre-register tracked-amendment for this case). | 2026-05-03 | **D-UBQ-1 awaiting user decision.** WW + GB3 NPT proceed regardless. UBQ path (a/b/c/d) determines whether criterion #1 closes at 3-of-3 NPT or 2-of-3 NPT + 1 NVT. |
| **SU budget cap 800 → 250 SU** | `prio_su_enforce.sh` script written for projected-budget enforcement (auto-cancel jobs that would push priority SU past cap; writes `head-1.2-su-budget-auto-cancel-*.md` notification). Cap lowered per user directive aggressive-SU-minimization. Tracker shows 231.5/250 used (no further priority spend planned). | 2026-05-03 | All future closure work on Standard scavenge_gpu (free, 10× cheaper than Standard gpu_h200). |
| **Sub 1.2 closure plan approved** | User authorized full no-compromise closure plan (D1-D6): ~80 priority SU bump (~$0.32) for diagnostic probes + per-protein iteration; MACE NPT 3-protein production on Standard Tier gpu_h200 (~125K standard SU within plan); SO3LR rescue with chemistry changes (neutral protonation for GB3+NTL9; float64+dt=0.25 fs for WW); escalation posture to PlannerAI via help-needed if SO3LR rescue exhausts; OSF deposit target 2026-05-13 (HARD 2026-05-15). Two execution SubAgents launched in parallel. Closure master plan documented in `shared/notes/1.2-closure-master-plan.md`. | 2026-05-02 | Sub 1.2 enters 14-day closure window. All 9 zero-compromise success criteria addressed. SO3LR strategic insight: prior task-002 conclusion that GB3/NTL9 were "dead for vacuum NVT" was right about failure mechanism (charge runaway) but wrong about cure space — fix is to neutralize protonation, not parameter-sweep dt/NHC. |
| **MACE NPT FIXED (Round 3)** | **Sentinel-bond + protein HBonds constraints + dt=1 fs recipe; validated 100 ps clean (test_P, density 1.041, T 297.6 K). Root cause: openmm-ml issue #91 singleton-molecule scaling + inadvertently stripped protein H-bond constraints.** Both fixes required — fixing only one extends but doesn't prevent failure (test_J fixed singleton-molecule, NPT extended 3.5→12.5 ps; test_L added HBonds, 25 ps clean; test_P at 100 ps confirmed). | 2026-05-02 | Sub 1.4 production uses MACE NPT (NOT NVT fallback). OSF v3 reverted from NVT-lock to NPT framing. D2 G1 achievable via MACE NPT. ~36 standard SU + ~8.3 priority SU spent in Round 3 iteration. Cross-agent note: `shared/notes/1.2-mace-npt-fixed.md`. |
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
| **Sub 1.2 PLANNED** | 6 tasks across 2 waves. Wave 1: MACE NPT 5ns × 3 Tier B (H200, 3 props × 5 ns per user scope decision), SO3LR vacuum 5 ns × 5 props (RTX 5000 Ada), OSF pre-reg drafting. Wave 2: BioEmu batch 2 (~100 props), Delta 5 baselines + WMSE harness, statistical pipeline core (Friedman/Nemenyi, ICC, bootstrap, JZS BF, T_min). HARD deadline OSF deposit 2026-05-15. Est ~705 GPU-hrs / ~129K SU. | 2026-04-18 | Ready for head-1.2 launch. User approved scope: MACE 3×5 ns, OSF "I draft, you deposit", stats Standard Tier only. |
| **Sub 1.2 LAUNCHED** | Wave 1 + Wave 2 both launched 2026-04-19. Wave 1 partial-completion trigger fired after task-001 + task-002 SLURM submits + task-003 v1 draft. Wave 2 tasks 005 (Delta baselines) and 006 (stats pipeline) ALREADY COMPLETE (code-only); task-004 (BioEmu batch 2) has 93-protein manifest + batch 1 submitted. | 2026-04-19 | 2/6 tasks complete; 4/6 in-flight with multi-day SLURM. OSF v1 drafted early (Day 1 vs Day 7 target). |
| **SO3LR task-002 COMPLETE** | All 5/5 SO3LR vacuum NVT 5 ns runs COMPLETED: GB3 (11.9h), GB1 (11.9h), NTL9 (11.2h), UBQ (16.2h) all exit 0. WW ran to full 5 ns completion (6.9h wall, "Simulation completed successfully!") — the NODE_FAIL occurred AFTER the simulation finished; trajectory intact (16.7 MB HDF5). | 2026-04-20 | 3/6 tasks now complete. SO3LR D2 G1 evidence: 5 Tier A/B proteins with stable 5 ns vacuum NVT. |
| **MACE CUDA optimization** | All prior MACE H200 jobs YCRC-cancelled (0% GPU util due to matscipy GIL-blocking CPU neighbor list). Root cause: matscipy.neighbour_list holds Python GIL ~50% of per-step wall → GPU idles → YCRC auto-cancel at 2-3h. Fix deployed: `mace_cuda_patch.py` replaces matscipy with GPU-native `torch.cdist` neighbor list + converts MACE model to cuequivariance format. Installed: `cuequivariance 0.9.1`, `cuequivariance-torch 0.9.1`, `torch-cluster 1.6.3+cu121` in env-mace. Diagnostic confirmed cueq conversion + GPU NL work; production resubmitted with built-in self-test. | 2026-04-20 | 3 fresh MACE NPT jobs queued on gpu_h200: 9012190 (WW, srf586dh), 9012191 (GB3, hzi3zjmw), 9012192 (UBQ, 5sosapi9). Expected GPU util: ~50% → near-100%. |
| **BioEmu batch 2 partial** | First 10-protein array (8903490): 5 COMPLETED, 4 FAILED, 1 TIMEOUT. Precache job (8887441) YCRC-cancelled. Batches 2-10 (remaining 83 proteins) not yet submitted. | 2026-04-20 | Needs batch 2-10 submission + topup for failed proteins. |
| **Sub 1.2 SO3LR remediation** | Task-002 v1 SLURM jobs (5) FAILED in 6-8s due to `PYTHONNOUSERSITE=1` in new sbatch script hiding user-site transitive deps (typing_extensions, rich, pandas, pyyaml, dateutil) required by flax/mlff. Root cause: new script's env-var pattern diverged from Sub 1.1 working crambin pattern. Fix (Option C): sbatch env-var change only (`=0` with user-site on PYTHONPATH); env-so3lr itself untouched. 5 v2 jobs resubmitted with fresh cryptic names (8890874-78). See `shared/notes/1.2-env-so3lr-typing-extensions-fix.md`. | 2026-04-19 | Lesson: all future env-so3lr SLURM scripts must use `PYTHONNOUSERSITE=0` with user-site on PYTHONPATH. env-mace's opposite contract (`=1`) must not propagate. |
| **Sub 1.2 MACE remediation** | Task-001 v1 SLURM jobs (3) FAILED exit 1:0 in 4-5s due to `submit_mace_npt.sh` line 80 hardcoding `/home/rag88/miniconda3/etc/profile.d/conda.sh` (path does not exist on this cluster; correct path is `/apps/software/system/software/miniconda/24.11.3/...` per Sub 1.1 bioemu_*.sbatch pattern). 1-line fix; env-mace + Python script untouched. 3 v2 jobs resubmitted with fresh cryptic tags (8893817 t4x7qn2w WW, 8893818 f9b3rk6h GB3, 8893819 p8m5dz1g UBQ) on gpu_h200. See `shared/notes/1.2-mace-conda-path-fix.md`. | 2026-04-19 | Lesson: all future SLURM wrapper scripts must use the shared miniconda path `/apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh`. Never guess conda paths; copy verbatim from a known-good Sub 1.1 script. |
| **Sub 1.2 overnight NODE_FAIL + BioEmu bug fix** | Cluster NODE_FAIL event at 2026-04-19T07:59:35Z killed MACE WW v2 (8893817, no usable checkpoint) + SO3LR WW v2 (8890874, was already stalled at step 498K/0.25 ns for 5.5 h before). BioEmu batch 1 array: 4 FAILED `batch_size=0` (L > 340 aa, bioemu bug in sample.py:239), 5 TIMEOUT at 4h walltime (14-43% sampling). User directive (16:00Z): "no compromise, best data, bump walltime, never accept partial data." Actions: (a) MACE WW v3 resubmitted as 8903308 w2n5cq8v; (b) SO3LR WW v3 resubmitted as 8903311 h6k3vr9m (fresh — stale artifacts archived as *.hang); (c) bioemu_batch2.sbatch patched with length-aware `batch_size_100 = max(10, ceil(3 * (L/100)²))` + walltime 4h→12h (ensures batch_size≥3 at all lengths, eliminates TIMEOUTs); (d) all 10 batch 1 scratch dirs wiped; batch 1 resubmitted as array 8903490 t0x8pyfc. 13 jobs now running healthy. | 2026-04-19 | Lesson: bioemu's default `batch_size_100=10` underflows for L>316 aa; always compute length-aware. Clean resubmit (wipe + re-run) preferred over partial-resume when batch_size differs. NODE_FAIL is infrastructure, not script — resubmit with fresh tag. |
| **D3 fully RETIRED** | task-005 (delta-baselines) completed 2026-04-19: 5 baselines (linear, mean, PCA, random, persistence) + WMSE harness + FDR (BH+BY) + calibration (ECE + reliability diagrams) + stratified eval all operational on 100K Tahoe-100M subsample. Random baseline correctly FAILS WMSE gate at top-level and all 48 cell-type strata (metric-gaming check works). All D3 criteria now MET. | 2026-04-19 | gate-tracker.md should be updated: D3 status from "ASSESSED: GO (baselines owed)" → "ASSESSED: GO (retired)". |
| **stats pipeline operational** | task-006 complete 2026-04-19: 5 components (friedman_nemenyi, icc with §10.3 convergence correction, 2-level hierarchical_bootstrap, jzs_bf with 4-prior sensitivity, T_min truncation); 5/5 synthetic unit tests pass; JZS BF matches R `BayesFactor::correlationBF` to 0.0001% (task spec allowed 20%); new env-stats created non-destructively. Pipeline is Phase-2-ready. | 2026-04-19 | OSF pre-reg v2 can use real validated power-analysis numbers from task-006 in Appendix B. |

---

## Per-Track Status

| Track | Status | Latest Milestone | Next Milestone |
|-------|--------|-----------------|----------------|
| Alpha-M | **MACE NPT prod driver launched + probes submitted; SO3LR rescue in flight** | MACE NPT: production driver `output/scripts/mace_hybrid_npt_prod.py` written (Round 3 recipe + checkpoint/restart + 22.5 hr walltime guard). 50 ps NPT probes submitted on priority_gpu: GB3 (10458154 b8r3kt5x), UBQ (10458155 c4n7vp2j). WW already validated by test_P 100 ps. Production held pending probe verdicts. SO3LR: rescue SubAgent writing neutral-protonation re-prep for GB3+NTL9 + float64+dt=0.25 fs runner for WW; 500 ps Rg pre-screen gates queued. | MACE: probe verdicts → 5 ns × 3 production on gpu_h200. SO3LR: gate verdicts → 5 ns × 3 rescues on gpu RTX 5000 Ada. Both target completion before 2026-05-13. |
| Gamma | Batch 2: 10/92 done (CD19_HUMAN excluded); 82 PENDING reorganized 2026-05-05 into 3-tier split | 46/47 batch 1 done; batch 2: 10 success + 82 PENDING split into 10730244 (53 short, Std gpu 6h), 10730245 (18 medium, scav 12h), 10730246 (11 long, scav 24h); 9449458/9449459 cancelled | Complete batch 2 generation (≥90 of 92 proteins to ≥2K conformations); short cohort dispatch expected within hours-to-days |
| Delta | **D3 retired; baselines + harness complete** | 5/5 methods + 5/5 baselines + WMSE/FDR/calibration/stratified harness all operational | Sub 1.3 ML pipeline on full Tahoe-100M |
| Combined | Stats pipeline Phase-2-ready | JZS BF matches R to 0.0001%; OSF v1 drafted (8,420 words) | OSF deposit by May 15; v2 refinement with validated power-analysis |

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

**scavenge_gpu queue depth + UBQ NPT escalation.** All 7 closure jobs PENDING on `scavenge_gpu` (PriorityTier=2, behind 178+ scavenge users). pi_mg269 fair-share recovering slowly (0.0167; from 0.013). UBQ NPT non-generalizing — D-UBQ-1 user decision needed. If scavenge dispatch stalled by 2026-05-09, contingency move to Standard tier (10× more expensive, requires user approval per 3× partition rule).

---

## Decisions Needed

**OPEN as of 2026-05-04:**
- **D-UBQ-1 — UBQ NPT path:** (a) NVT pivot per documented R1 fallback (RECOMMENDED by auditor + project reviewer); (b) Tier-3 NPT untested combo (~50 priority SU); (c) drop UBQ from criterion #1 / NTL9 substitute (PROBE IN FLIGHT 10622876 q6kz3m8x); (d) different starting structure UBQ_alt 1XQQ probe (PROBE IN FLIGHT 10622885 q6uadt05). See `shared/help-needed/head-1.2-mace-ubq-non-generalization.md` + `status/task-001-substitute-status.md` + `status/task-001-ubq-altstruct-status.md`.

**Resolved 2026-05-03 (post handoff doc audit):**
- **D-OSF-SO3LR**: §4 commits to neutral-protonation methodology pre-deposit (substantive fix applied to v3).
- **OSF v3 internal-consistency fixes (6 issues)**: ALL APPLIED 2026-05-03 (5 trivial + 1 substantive D-OSF-SO3LR §4).
- **Sub 1.2 CLAUDE.md MUST-READ list update**: APPLIED — 6 critical 2026-05-02/03 docs added (per handoff-successor-2026-05-04.md).

**Resolved 2026-04-18:**
- MACE NPT scope: 3 proteins × 5 ns (~420 GPU-hrs H200, ~125K SU; within Phase 1 Alpha-M budget)
- OSF deposit: agent drafts, user deposits on OSF account
- stats-pipeline: Standard Tier only (no Priority Tier)

The previously open "Phase 2 MACE scope" item (2026-04-18) was RESOLVED: Option 5 (H200 OpenCL) committed; see `shared/help-needed/sub-1.2-phase2-mlff-scope.md`.

---

## Upcoming Milestones

| Date | Milestone | Gate |
|------|-----------|------|
| ~~Apr 30~~ | ~~Phase 0 complete~~ | — | **Done (Apr 16)** |
| ~~May 2~~ | ~~Subphase 1.1 complete (target)~~ | — | **Done (Apr 17)** |
| ~~May 9~~ | ~~MLFF software GO~~ | ~~D1~~ | **Done (Apr 17) — ASSESSED: GO** |
| May 15 | OSF pre-registration | — |
| ~~May 31~~ | ~~Tahoe-100M download deadline~~ | ~~DK1~~ | **Done (Apr 16)** |
| ~~Jun 6~~ | ~~Delta scope lock~~ | ~~D3~~ | **Done (Apr 19) — ASSESSED: GO (RETIRED)** |
| Jun 30 | MLFF pilot GO | D2 |
| Jul 31 | Integration signal | D4 |
| Aug 15 | Delta preprint | D5 |
| Aug 31 | Combined paper GO/NO-GO | D6 |
| Sep 15 | Phase 3 scope | D7 |
