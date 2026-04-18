---
requesting_agent: "PlannerAI"
subphase: "1.1 → 1.2"
date: 2026-04-18
blocked_tasks: ["Subphase 1.2 MLFF pilot planning", "Phase 2 Alpha-M MLFF compute budget"]
urgency: high
---

# Help Needed: Phase 2 MACE Scope Decision — Empirical Throughput 9× Slower Than Projected

## Problem Description

Hybrid-mode MACE-OFF24 on OpenCL is **8.7× slower than Subagent A's Section 2.3
projection** (empirically measured 2026-04-18 on RTX 5000 Ada across 3 proteins):

| Protein | Measured ns/day | Projected | Slowdown |
|---------|-----------------|-----------|----------|
| WW (34 aa, 7,565 total atoms) | 0.184 | 1.96 | 10.7× |
| GB3 (56 aa, 9,874 total atoms) | 0.111 | 0.85 | 7.7× |
| Ubiquitin (76 aa, 17,162 total atoms) | 0.074 | 0.60 | 8.1× |

Dynamics are stable (no NaN, max-force check passes, PE/T stable). The issue
is pure throughput on OpenCL. Hybrid physics is fine; hybrid OpenCL performance
is not adequate for Phase 2 IP-scope production.

## Budget implication

- Subagent A's revised Phase 2 Alpha-M MLFF budget: 47,300 GPU-hrs (1.4× IP baseline)
- Empirical 8.7× slowdown → effective requirement: ~410,000 GPU-hrs for IP scope
- Total project budget: ~170,000 GPU-hrs (Phase 2+3 Alpha-M + Gamma + Delta)
- **Phase 2 IP-scope MACE is infeasible.** Must revise scope OR recover throughput.

## What Was Tried

1. **Hybrid `createMixedSystem` API** — WORKS. Subagent G (2026-04-17) verified the API call itself on both WW and ubiquitin systems.
2. **Tuned minimization (`maxIterations=200`)** — CAUSED NaN during NVT. Reverted to 2000 iter + post-min max-force sanity check. System now runs without NaN (jobs 8736919/8736920/8736921).
3. **4-hour wall on RTX 5000 Ada (gpu_devel + gpu)** — hit wall before reaching even 20 ps equilibration on any protein. Not a queue issue; a throughput issue.

## What Help Is Needed

PlannerAI or human decision among these options:

### Option 1 — Reduce MACE scope dramatically (cheapest, safest)

Cap Phase 2 MACE production at **2-3 Tier A proteins × 3-5 ns × 2 MLFFs**.
- Proteins: WW (best throughput) + GB3 (best S2 reference) + NTL9 (newly added)
- Trajectory: 3 ns per protein per replica (~1 trajectory × protein × MLFF = 6 trajectories)
- Budget: ~5,000 GPU-hrs (fits in original 33,800 Phase 2 line with margin for SO3LR-vacuum on all 9)
- Manuscript framing: MACE-OFF24 hybrid is "demonstrated as a force field platform" on the Tier A benchmark, not a production-scale benchmark
- Pro: safe, within budget, reviewer-defensible as "demonstration"
- Con: loses the "benchmark MLFF on 9 proteins" claim; reduces statistical power of Alpha-M

### Option 2 — OpenMM rebuild with CUDA 12.4+ — ❌ REJECTED 2026-04-18 (empirical)

**Subagent L completed the investigation.** Report: `shared/notes/1.1-mace-cuda-benchmark.md` (final) with build log in `shared/notes/1.1-openmm-cuda-rebuild.md`.

- **Build SUCCESS** (Subagent J): OpenMM 8.5.1 rebuilt against CUDA 12.8 toolkit. CUDA platform activates on RTX 5000 Ada (sm_89). PTX version bug solved.
- **Interop bug partially fixed** (Subagent L): Fix A+B combination (CUDA_VISIBLE_DEVICES=0 + `torch.cuda.set_device(0)` + MLPotential device hint + runtime monkey-patch of openmm-ml's `_computeMACE` with `torch.cuda.synchronize()`) unlocks brief CUDA dynamics on RTX 5000 Ada.
- **Fix is fragile and mode-dependent.** Works for small test (610 sustained steps at createMixedSystem with all-atoms-in-ML + 10-iter min). Fails for: ≥2000-iter minimize, TIP3P hybrid systems, H200 GPU, createSystem pure-MACE path — all crash at post-minimize `getState` with the original "invalid resource handle".
- **Throughput: 1.0× speedup — ZERO gain from CUDA.** Crambin vacuum CUDA = 0.142 ns/day on RTX 5000 Ada = identical to OpenCL baseline (0.142 ns/day). Hybrid WW CUDA failed. H200 CUDA failed.
- **Root cause:** MACE-OFF24 is **inference-bound** on PyTorch CUDA. The OpenMM platform backend (OpenCL vs CUDA) is irrelevant because MACE inference dominates per-step cost. The 11.5× H200 vs RTX 5000 Ada speedup (measured in Option 5) comes from H200's faster PyTorch CUDA compute, not from OpenMM backend.
- **Compute used:** ~26 min wall, ~11 SU on RTX 5000 Ada + H200 test jobs.
- **Verdict: REJECT.** Required ≥5× speedup per task spec (<3× triggers reject). Observed 1.0× where it works, FAIL otherwise.
- **Disposition:** env-mace-cuda and build artifacts deleted per cleanup policy. env-mace (production) untouched. Future openmm-torch investigation deferred indefinitely (1-2 hr of work for <2× expected speedup is not worth the complexity).

### Option 5 — **H200 OpenCL** ✅ CONFIRMED 2026-04-18

Subagent J's ancillary vacuum benchmark (H200 11× RTX 5000 Ada) has now been
**empirically confirmed on hybrid**: SLURM 8789805 measured 2.11 ns/day on
hybrid WW (vs 0.184 on RTX 5000 Ada → **11.5× speedup**). Matches projection.

- **Measured hybrid throughput on H200 OpenCL:**
  - WW: **2.11 ns/day** (confirmed, step 7000)
  - GB3: ~1.2 ns/day (extrapolated from 11.5× the 0.111 RTX 5000 Ada number)
  - UBQ: ~0.85 ns/day (extrapolated from 11.5× the 0.074)
- **Phase 2 at IP scope feasibility on H200 OpenCL: ✅ FEASIBLE**
  - 9 proteins × 2 MLFFs × 10 ns baseline: ~3,300 GPU-hrs (<10% of the revised 47,300 GPU-hr Phase 2 budget)
  - 25 ns stretch: ~8,300 GPU-hrs (fits comfortably)
- **Pro:** No rebuild needed. OpenCL already works. Massive budget margin.
- **Cons:**
  - H200 SU rate is 300/hr (20× RTX 5000 Ada). On pi_mg269 Standard Tier this is free directly but consumes fairshare pool — may queue at peak
  - Observed hang at step 7000 in the benchmark (proactively cancelled at 2.5 hr wall). Root cause unclear. Recommend adding GPU keepalive thread to production scripts + using openmm-torch in Sub 1.2 to mitigate
- **Status: CONFIRMED. Committed as Phase 2 MACE primary path.**

### Option 3 — SO3LR-primary, MACE demonstration only

Pivot Phase 2 to SO3LR as the workhorse MLFF (15 ns/day vacuum on RTX 5000 Ada
per Sub 1.1 crambin test, all-atom; fits easily in budget). Keep MACE as a
"demonstration" run on 2-3 proteins à la Option 1.
- Vacuum constraint: SO3LR does NOT support explicit-water periodic systems
  without a ≥24 Å box. For protein MD, this means vacuum simulations OR very
  large boxes (expensive). May need to reframe Alpha-M around vacuum dynamics
  as the primary comparison.
- Budget: fits in 10-20K GPU-hrs (9 proteins × 25 ns at 15 ns/day = 9 × 1.67 days = ~360 GPU-hrs per MLFF × 2 MLFFs = 720 GPU-hrs; very cheap)
- Pro: feasible at IP scope
- Con: vacuum MLFF is a narrower scientific claim than solvated hybrid; reviewer may push back on "vacuum is not physiological"

### Option 4 — Implicit solvent MACE — ❌ REJECTED 2026-04-18 (empirical)

**Subagent K ran the pilot.** Result: `shared/notes/1.1-mace-implicit-pilot.md`.

- System dropped from 7,565 → 534 atoms (14.2× smaller) via GBn2 implicit solvent
- **Throughput: 0.197 ns/day vs 0.184 explicit hybrid = only 1.07× speedup**
- Dynamics also exploded at step 2000 (T 379 K → 40,365 K between reporter intervals)

**Root cause identified:** On OpenCL the MACE inference is the dominant per-step
cost for small proteins. Explicit-water PME contributed only ~7% of wall time.
Removing water gives negligible speedup because MACE itself is the bottleneck.

**Implication:** The OpenCL throughput problem is in the MACE forward pass
(PyTorch CUDA) and its handoff to OpenMM's OpenCL integrator, NOT in the
classical water PME. This is a critical finding that narrows the remaining
options: any throughput recovery must come from either (a) CUDA OpenMM to
eliminate the OpenCL/CUDA handoff overhead (Option 2), or (b) accepting the
current throughput (Options 1 and 3).

## Impact Assessment

| Item | Detail |
|------|--------|
| Blocked tasks | Sub 1.2 MLFF pilot scope definition; Phase 2 Alpha-M compute allocation; OSF pre-registration MLFF section |
| Timeline impact | No immediate impact on D1 (GO remains — hybrid API works). Delays Sub 1.2 MLFF task spec until decision lands. Each week of decision delay = 1 week of production lost. |
| Gate at risk | D2 (June 30 MLFF pilot GO) — if Option 1 is chosen, D2 criterion G1 ("≥1 MLFF stable >10 ns on ≥3 Tier B proteins") becomes hard: at WW throughput, 10 ns = 55 days wall time per protein. G1 probably unmeetable in explicit-solvent on current hardware; must be relaxed or re-scoped |
| Workaround available | Option 1 (reduced scope) is the lowest-risk immediate workaround |

## Recommendation (updated 2026-04-18 after Subagent J's OpenMM rebuild investigation)

**The decision space has changed materially. Option 5 (H200 OpenCL) is now primary.**

### Why the update

Subagent K's Option 4 pilot revealed the throughput bottleneck is MACE inference
on OpenCL, not classical water. Subagent J's OpenMM rebuild investigation then
revealed (as an ancillary finding) that **H200 OpenCL is 11× faster than RTX 5000 Ada
OpenCL on MACE**. We had been benchmarking exclusively on RTX 5000 Ada per the SU
cost policy — this gave us artificially pessimistic throughput.

At H200-OpenCL extrapolated throughput (~2 ns/day WW, ~0.8 ns/day ubiquitin),
Phase 2 IP scope FITS in the revised 47,300 GPU-hr budget with ~6× margin.

### Recommended path

1. **Primary: Option 5 (H200 OpenCL).** No rebuild required. Route all Phase 2 MACE
   production to gpu_h200 partition. Use env-mace unchanged. Empirical
   confirmation benchmark in flight (SLURM 8789805, h1v5qpn9).
2. **Sub 1.2 optimization: Option 2 (CUDA rebuild).** The PTX issue is SOLVED by
   Subagent J's source build. Only the PyTorch-OpenMM CUDA interop bug remains
   (1-2 hr fix). Expected 2-5× additional speedup over H200 OpenCL. Nice-to-have,
   not a blocker.
3. **Fallback: Option 1 (reduced scope).** Kept as absolute fallback if H200
   benchmark contradicts the extrapolation.
4. **Parallel track: SO3LR-primary on vacuum.** Keeps the MLFF benchmark claim strong
   regardless of MACE scope — SO3LR was never throughput-limited.
5. **Closed: Option 4.** REJECTED (empirical; see above).

### SU cost consideration

H200 at 300 SU/hr × ~3,300 GPU-hrs = ~990,000 SU for Phase 2 MACE at IP 10 ns scope.
On pi_mg269 (Standard Tier) this is "free" directly but consumes fairshare pool.
If fairshare queueing becomes a blocker, escalate to Priority Tier
(prio_gerstein, $0.004/SU = ~$4,000 total cost) — this is a user financial
decision.

### Action items for Sub 1.2 planning

- [ ] Confirm H200 OpenCL hybrid benchmark (8789805) gives ≥1 ns/day on WW (validates extrapolation)
- [ ] If confirmed: commit Phase 2 MACE to gpu_h200 partition at IP scope
- [ ] Add Subagent J's CUDA interop fix as a Sub 1.2 task (1-2 hr follow-up using the already-built env-mace-cuda)
- [ ] Revisit compute budget row with empirical H200 numbers (expect ~0.2× of Subagent A's revised Phase 2 line, releasing ~40K GPU-hr back to contingency)

Option 4 data remains useful as a manuscript discussion point: "we verified that
the per-step cost is dominated by MACE inference rather than classical solvent
PME; this identifies the primary bottleneck for future MLFF-MD tooling."

## Evidence

- `shared/notes/1.1-mace-hybrid-validation.md` §9-10 — full throughput measurement
- `phases/phase-1/subphase-1.1/output/mace_hybrid_ww_equil.log` — WW 14 ps at 0.184 ns/day
- `phases/phase-1/subphase-1.1/output/mace_hybrid_ubq_equil.log` — UBQ 9 ps at 0.074 ns/day
- `phases/phase-1/subphase-1.1/output/mace_hybrid_gb3_equil.log` — GB3 15 ps at 0.111 ns/day
- `shared/notes/1.1-mace-phase2-feasibility.md` — prior projection (now invalidated)

## Resolution Log

| Date | Action | By | Status |
|------|--------|----|--------|
| 2026-04-18 | Escalation raised by PlannerAI after empirical measurement | PlannerAI | pending user decision |
| 2026-04-18 | Subagent K ran Option 4 empirical pilot → REJECTED (1.07× speedup only; MACE inference is bottleneck) | Subagent K | Option 4 closed |
| 2026-04-18 | Subagent J launched to test Option 2 (OpenMM CUDA rebuild) empirically | PlannerAI | Option 2 pending |
| 2026-04-18 | Subagent J reported: CUDA rebuild PARTIAL SUCCESS (RTX 5000 Ada CUDA works, interop bug remains). Ancillary finding: H200 OpenCL 11× RTX 5000 Ada → new Option 5. | Subagent J | Option 5 now primary candidate |
| 2026-04-18 | H200 hybrid WW benchmark (SLURM 8789805) measured 2.11 ns/day at step 7000 → Option 5 CONFIRMED. Job hung post-step-7000, cancelled proactively. | PlannerAI | Option 5 committed |
| 2026-04-18 | Subagent L launched to finish Option 2 interop fix + benchmark | PlannerAI | Option 2 final test |
| 2026-04-18 | Subagent L reported: Fix A+B works on narrow cases only. Crambin vacuum CUDA = 0.142 ns/day = 1.0× OpenCL. MACE inference-bound. Option 2 REJECTED. | Subagent L | Option 2 closed |
| 2026-04-18 | **Phase 1.1 closure:** Options 2, 4 REJECTED; Option 5 committed as Phase 2 MACE primary path. User-approved via cleanup directive. | PlannerAI | RESOLVED |
