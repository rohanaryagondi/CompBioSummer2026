---
session: HeadAISubphase1.2May1 (overnight)
date: 2026-05-02
session_end: ~10:40Z
---

# Overnight Summary — MACE NPT Iteration (2026-05-01 → 2026-05-02)

## TL;DR

**MACE NPT is fixed.** Production recipe validated to **100 ps clean** on WW.
Sub 1.4 will use **MACE NPT** (not the NVT fallback).

The fix is **two patches applied after `MLPotential.createMixedSystem(...)`:**

1. **Sentinel HarmonicBondForce** with k=0 along the protein bonded graph
   (`add_protein_sentinel_bonds` in `output/scripts/npt_diagnostics/npt_diag_common.py`).
   Fixes openmm-ml issue #91 (singleton-molecule scaling under MonteCarloBarostat).

2. **Restored AMBER14 HBonds constraints** for protein heavy-atom-to-H bonds
   (`add_protein_hbonds_constraints` in the same file). Fixes the unconstrained
   C-H stretching instability at dt=1 fs.

Both fixes are necessary; either alone delays but doesn't prevent failure.

## Iteration timeline

| Round | Test | Recipe | NPT survived | Verdict |
|-------|------|--------|--------------|---------|
| Round 1 (prior session) | I, I3, I4 | wrapping fixes only | 3.5–7.7 ps | KEEP_NVT (premature) |
| Round 2 | J | sentinel only | 12.5 ps | partial (NVT fixed, NPT failed) |
| Round 3A | K | sentinel + dt=0.5 fs | 13 ps full target | PASS |
| **Round 3B** | **L** | **sentinel + HBonds + dt=1 fs** | **25 ps full target** | **PASS — production recipe** |
| Round 3C | M | sentinel + HBonds + dt=0.5 fs | 14 ps full target | PASS (kitchen-sink confirmation) |
| **Round 3D** | **P (priority queue)** | **sentinel + HBonds + dt=1 fs** | **100 ps full target** | **PASS — production-confirmed** |

## What the user needs to know

1. **OSF v3 is reverted to NPT framing.** Sections 2.1, 4, 7.1, 8, 10 all updated.
   The deposit-ready document is `output/osf-prereg-v3.md`. Suggested final review
   pass before deposit on May 15.

2. **Cross-agent note** at `shared/notes/1.2-mace-npt-fixed.md` (urgency=critical)
   has the full evidence chain and recommended Sub 1.4 implementation.

3. **Dashboards synced**: master-status, active-subphase, gate-tracker, compute-budget
   all reflect the fix (timestamp 2026-05-02T10:35Z).

4. **Compute used overnight:**
   - Standard SU (gpu_devel, free under 1 hr): tests I (~2.85), I3 (~3.55), I4 (~4.05),
     J (~10.0), K (~12.2), L (~13.2), M (~13.5) = ~59 SU total
   - Priority SU (priority_gpu, prio_mg269): test P 2:44:57 wall × 3 SU/hr ≈ **~8.3 SU**
   - **Total priority SU committed Sub 1.2: ~67/108.5** (well under cap)

5. **No actions blocked.** BioEmu arrays still PENDING fair-share (unchanged from
   handoff). Sub 1.3 planning can proceed: implement `mace_hybrid_npt_prod.py` reusing
   the test_L recipe (the two helpers + dt=1 fs + freq=25 MCB).

## Files changed overnight

### New files
- `output/scripts/npt_diagnostics/test_K_halfstep.py` (Round 3A)
- `output/scripts/npt_diagnostics/test_L_hbonds.py` (Round 3B — production recipe)
- `output/scripts/npt_diagnostics/test_M_combined.py` (Round 3C)
- `output/scripts/npt_diagnostics/test_P_extended.py` (Round 3D, 100 ps confirmation)
- `output/scripts/npt_diagnostics/run_test_{K,L,M,P}.sbatch` — SLURM wrappers
- `shared/notes/1.2-mace-npt-fixed.md` — CONFIRMED cross-agent note
- `output/mace_npt_literature_review.md` — earlier literature SubAgent's analysis (kept)

### Modified files
- `output/scripts/npt_diagnostics/npt_diag_common.py` — added
  `add_protein_hbonds_constraints` (additive; existing functions untouched)
- `output/osf-prereg-v3.md` — 5 reverse-edits to NVT framing back to NPT
- `dashboards/master-status.md`, `active-subphase.md`, `gate-tracker.md`, `compute-budget.md`
- `shared/notes/1.2-mace-npt-stability.md` — appended §7 RESOLUTION

## Known caveats / what to verify

1. **Recipe validated only on WW** (~534 atoms after solvation). Recipe is
   architectural (fixes openmm-ml), so it should generalize to GB3/GB1/NTL9/UBQ,
   but Sub 1.4 production will be the ground truth. If a specific protein fails,
   the two-stage NVT fallback (`output/npt_nvt_production_plan.md`) is still valid.

2. **100 ps is 1% of the Sub 1.4 10-ns production target.** Energy was stable
   throughout test_P with no drift, but slow drift at longer timescales is
   theoretically possible. Sub 1.4 production should monitor PE drift and Rg
   stability per protein.

3. **Throughput: 0.91 ns/day on RTX 5000 Ada at dt=1 fs**, matching test_J's
   pre-failure rate. The HBonds constraints add no throughput penalty. H200
   OpenCL hybrid should reach ~2.56 ns/day per Sub 1.1 §11 measurements.

4. **Upstream:** Worth filing a comment on openmm-ml issue #91 with the
   sentinel-bond workaround and minimal reproducer. Optional — not blocking.
