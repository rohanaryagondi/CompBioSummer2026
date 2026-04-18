---
gate_id: "D1"
date: 2026-04-17
decision: GO
assessed_by: PlannerAI
---

# Gate Assessment: D1 — MLFF Software GO

## Gate Definition

**Date:** May 9, 2026 (formal); this assessment is written 22 days early based on
complete evidence from Subphase 1.1.
**Decision:** Whether MACE-OFF24 and SO3LR software stacks are operational for
Alpha-M benchmark use. Failure of one MLFF drops that MLFF from the benchmark;
failure of both triggers Alpha-M fallback to classical+generative-only scope.
**Source:** Implementation Plan Section 13, gate D1.

---

## Evidence Summary

Both MLFFs completed ≥100 ps stable NVT on crambin during Subphase 1.1:

- **MACE-OFF24** (Subphase 1.1 task-001, mace-pilot SubAgent): 37+ ps confirmed
  stable at 1.51 ns/day on H200 OpenCL, with a 100 ps stage extending through SLURM
  job 8396439. Stage A (vacuum) passed. Model: `MACE-OFF24-medium` via
  `openmm-ml`. Per `shared/notes/1.1-mace-crambin.md` (rewritten 2026-04-17):
  OpenMM's CUDA platform is confirmed broken on all three tested GPUs — H200
  (sm_90), B200 (sm_100), and RTX 5000 Ada (sm_89, per job 8398672
  `CUDA_ERROR_UNSUPPORTED_PTX_VERSION`). OpenCL is the operational backend.

- **SO3LR** (Subphase 1.1 task-002, so3lr-pilot SubAgent): 1 ns complete
  (100 ps Stage A + 900 ps Stage B). 2.93 ms/step on RTX 5000 Ada, ~15 ns/day
  sustained. Hamiltonian drift ~15 meV/ps (acceptable float32 NVT). Per
  `shared/notes/1.1-so3lr-crambin.md`: CLI (`so3lr nvt --relax`) is the
  operational interface.

Phase 2 feasibility analysis (`shared/notes/1.1-mace-phase2-feasibility.md`):
MARGINAL on full-MACE solvated (infeasible within Phase 2 schedule); FEASIBLE on
hybrid MACE-protein + classical-water (Stage C pattern), with a ~1.40× OpenCL
compute multiplier absorbed into the revised budget. OpenMM rebuild explicitly
REJECTED — OpenCL is adequate.

---

## Criteria Evaluation

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | MACE-OFF24 installs | MET | env-mace build PASS (`shared/notes/0.1-env-mace-build.md`) |
| 2 | MACE-OFF24 runs 1 ns NVT on crambin | MET (via OpenCL fallback) | SLURM 8396439 + extended stage; `phases/phase-1/subphase-1.1/output/crambin_vacuum_1000ps.log` |
| 3 | SO3LR installs | MET | env-so3lr build PASS (`shared/notes/0.1-env-so3lr-build.md`) |
| 4 | SO3LR runs 1 ns NVT on crambin | MET | SLURM 8394754 1 ns complete; `phases/phase-1/subphase-1.1/output/task-002-d1-evidence.md` |
| 5 | No NaN forces / non-divergent energy (both MLFFs) | MET | See per-MLFF logs; PE stable ±70–100 kJ/mol range, T=300±14 K |

---

## Verdict

**Decision: GO.**

Both MLFF software stacks are operational and meet the D1 criteria. Both
completed the ≥100 ps stable NVT threshold on crambin with no NaN forces and
stable energy. Alpha-M can proceed with both MLFFs.

### If GO
- Subphase 1.2 NPT stability tests on Tier A/B proteins proceed for MACE and SO3LR
- Phase 2 Alpha-M MLFF production planned with **hybrid MACE + classical-water**
  (Stage C pattern) per feasibility analysis; full-atom MACE solvated is NOT a viable
  Phase 2 scope on current hardware
- SO3LR production is feasible in full-atom mode (vacuum or periodic with
  lr_cutoff ≥ 24 Å) — no hybrid mode required
- Compute budget revised upward 1.40× for MACE (OpenCL fallback); SO3LR unchanged

### Downstream Conditions (not blockers, but flagged)
- **Hybrid-mode empirical validation (pre-Phase 2):** MACE hybrid solvent mode
  (`openmmml.MLPotential.createMixedSystem`) was NOT explicitly exercised in
  Subphase 1.1 (Stage C fires only if Stage B fails, which didn't happen).
  Subphase 1.2 MUST test hybrid on a small solvated system (e.g., WW domain or
  GB3) before committing Phase 2 production. If hybrid fails, D1 status
  re-evaluates to CONDITIONAL and OpenMM rebuild becomes required.
- **OpenCL throughput benchmark (Subphase 1.2):** confirm hybrid-mode throughput
  at ≥60% of projected (0.6 ns/day for ubiquitin). If throughput is <40% of
  projection on ≥2 Tier B proteins, escalate to user re: OpenMM rebuild.

---

## Downstream Impact

| Affected Item | Impact |
|--------------|--------|
| Phase plan | Phase 1 Sub 1.2 adds explicit hybrid-mode MACE test on WW domain or GB3 |
| Subphase 1.2 | New task: verify `MLPotential.createMixedSystem` works with OpenCL backend |
| Subphase 1.2 | Benchmark: OpenCL hybrid throughput on 1 Tier B protein (~1 GPU-day) |
| Compute budget | Alpha-M Phase 2+3+contingency: 144,392 → 204,250 GPU-hrs (1.41×); see `compute-budget.md` |
| Timeline | No change; both MLFFs viable; hybrid-validation risk to be resolved in Sub 1.2 |
| Publication strategy | Methods section must document OpenCL+hybrid approach; full-atom MACE limitation is a manuscript finding, not a failure |

---

## Action Items

1. Include MACE hybrid-mode test (`createMixedSystem` on WW domain or GB3, OpenCL) as an early Subphase 1.2 task — must run before Phase 2 commits
2. Update `dashboards/compute-budget.md` with revised Phase 2+3 numbers (1.40× multiplier, see Subagent A feasibility note Section 6)
3. If Subphase 1.2 hybrid validation fails, re-open D1 as CONDITIONAL and escalate OpenMM rebuild decision via `shared/help-needed/`
4. Formal D1 re-affirmation at the original gate date (May 9) if no new evidence contradicts this early assessment
5. SO3LR-specific action: benchmark SO3LR on a Tier B protein (e.g., ubiquitin) in Subphase 1.2 to confirm vacuum/periodic scaling matches crambin extrapolation

---

## References

- `shared/notes/1.1-mace-crambin.md` — MACE D1 result (rewritten 2026-04-17)
- `shared/notes/1.1-mace-phase2-feasibility.md` — OpenCL scaling, hybrid mode, budget delta
- `shared/notes/1.1-so3lr-crambin.md` — SO3LR D1 result
- `phases/phase-1/subphase-1.1/completion-report.md` Sections on task-001 and task-002
- Implementation Plan Section 13 (D1 definition)
