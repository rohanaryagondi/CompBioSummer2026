---
subphase: "1.2"
prior_session: "HeadAISubphase1.2May1 — overnight Round 3 NPT iteration (2026-05-01 → 2026-05-02)"
date: 2026-05-02
reason: "End of overnight session. MACE NPT fixed. Successor reads this to pick up state."
---

# Handoff Notes — Sub 1.2 (Updated 2026-05-02 after MACE NPT fix)

**This supersedes the May 1 handoff content.** Read this entire file first.

---

## 1. Headline result of overnight session

**MACE NPT was fixed.** The May 1 prior session had concluded "NPT not viable, lock NVT." That conclusion was premature — overnight investigation found the actual root cause and a clean fix. Production recipe validated to **100 ps clean NPT** on WW.

### Production recipe (drop-in for Sub 1.4)

After `MLPotential('mace-off24-medium').createMixedSystem(topology, system, protein_atoms, interpolate=False)` returns the hybrid system, apply two patches BEFORE constructing the `Simulation`:

```python
from npt_diag_common import (
    add_protein_sentinel_bonds,
    add_protein_hbonds_constraints,
)

# Patch 1: zero-strength HarmonicBondForce along the protein bonded graph.
# Fixes openmm-ml issue #91 — without this, findMolecules() treats each
# protein atom as a singleton "molecule," and MonteCarloBarostat scales
# each protein atom independently around the box origin per accepted move.
add_protein_sentinel_bonds(hybrid_system, topology, protein_atoms)

# Patch 2: re-add AMBER14 HBonds constraints for protein heavy-atom-H bonds.
# Required because the classical system was built with constraints=None.
# Without rigid C-H/N-H/O-H, dt=1 fs is at the edge of velocity-Verlet
# stability; barostat-driven box rescales drive runaway integration.
add_protein_hbonds_constraints(hybrid_system, topology, protein_atoms)

# Then add MonteCarloBarostat and proceed normally.
hybrid_system.addForce(MonteCarloBarostat(1*atm, 300*K, 25))  # freq=25
integrator = LangevinMiddleIntegrator(300*K, 1/picosecond, 1*femtosecond)
```

Both helpers live in `output/scripts/npt_diagnostics/npt_diag_common.py`. Reproducible from `test_L_hbonds.py` (25 ps gpu_devel) and `test_P_extended.py` (100 ps priority queue confirmation).

### Validation evidence

| Test | Recipe | NPT survived | dt | Verdict |
|------|--------|--------------|------|---------|
| Round 1 (test_I) | baseline | NaN @ 3.5 ps | 1 fs | FAIL |
| Round 1 (test_I3) | enforce_pbc | NaN @ 5.0 ps | 1 fs | FAIL |
| Round 1 (test_I4) | enforce + molecular | NaN @ 7.7 ps | 1 fs | FAIL |
| Round 2 (test_J) | sentinel only | NaN @ 12.5 ps | 1 fs | partial — NVT fixed, NPT fails |
| Round 3A (test_K) | sentinel + dt=0.5 | 13 ps PASS (full target) | 0.5 fs | PASS |
| **Round 3B (test_L)** | **sentinel + HBonds + dt=1** | **25 ps PASS (full target)** | **1 fs** | **PASS — production recipe** |
| Round 3C (test_M) | sentinel + HBonds + dt=0.5 | 14 ps PASS (full target) | 0.5 fs | PASS (kitchen sink) |
| **Round 3D (test_P, priority)** | **sentinel + HBonds + dt=1** | **100 ps PASS (full target)** | **1 fs** | **PASS — production-confirmed** |

test_P final state at 100 ps: density 1.041 g/cm³, T 297.6 K, PE -364,840 kJ/mol (stable trajectory throughout, no drift).

Throughput: ~0.91 ns/day on RTX 5000 Ada at dt=1 fs (matches Sub 1.1 NVT — no throughput penalty). H200 OpenCL hybrid expected ~2.56 ns/day per Sub 1.1 §11.

### Root cause (both bugs needed fixing — fixing one alone delays but doesn't prevent NaN)

1. **Singleton-molecule bug (openmm-ml issue #91, jchodera 2025-02-04, still open):** `createMixedSystem` calls `_removeBonds(allInSet=True, removeConstraints=True)`, which strips all `HarmonicBondForce`/`HarmonicAngleForce`/`PeriodicTorsionForce`/HBonds-constraint terms whose atoms all lie in the ML subset. The MACE `PythonForce` wrapper does NOT implement `getBondedParticles()`. So OpenMM's `ContextImpl::findMolecules()` sees zero connectivity for the protein region and treats each protein atom as its own "molecule." `MonteCarloBarostat::scaleCoordinates` and `enforcePeriodicBox` then operate per-atom on the protein, gradually destroying bonded distances → NaN within 5–25 ps.

2. **Unconstrained-H instability:** The same bond stripping leaves protein C-H/N-H/O-H bonds unconstrained. At dt=1 fs the C-H stretching mode (~3000 cm⁻¹, period ~10 fs) is at the edge of velocity-Verlet stability. Barostat-driven box rescales add small perturbations that compound with H atom flexibility → runaway integration.

The literature SubAgent identified bug #1 from openmm-ml issues. Round 1 SubAgent's empirical probe TSV showed bug #2 directly (protein span exploded from 28 Å to 113 Å in 14 callbacks before NaN). Both fixes are required — sentinel-bond alone (Round 2) extends NPT failure horizon from 3.5 ps to 12.5 ps but does not prevent it.

---

## 2. Sub 1.2 task status (final, 2026-05-02)

| Task | Status | Notes |
|------|--------|-------|
| **task-001 MACE NPT** | **FIXED 2026-05-02 via Round 3 recipe** | Production recipe validated to 100 ps clean. Sub 1.4 = MACE NPT (NOT NVT fallback). |
| task-002 SO3LR | COMPLETE — 2/5 PASS | GB1+UBQ Tier B stable 5 ns; WW/GB3/NTL9 failed (NaN or silent structural explosion). Mandatory 500-ps Rg pre-screen now part of SO3LR production protocol. |
| task-003 OSF pre-reg | v3 deposit-ready | Reverted from NVT-lock to NPT framing 2026-05-02. User deposits by 2026-05-15 (HARD deadline). |
| task-004 BioEmu batch 2 | 10/92 DONE, 82 PENDING | Arrays 9449458 (x9sok7yl) + 9449459 (l5uw4lsy) on `gpu` partition, fair-share blocked (`pi_mg269` at 0.013). CD19_HUMAN excluded (1.4% pass rate). Will dispatch as fair-share recovers (days). |
| task-005 Delta baselines | COMPLETE | All 5 baselines + WMSE harness + FDR + calibration + stratified eval. D3 retired. |
| task-006 Stats pipeline | COMPLETE | All 5 components pass synthetic-data unit tests. JZS BF matches R `BayesFactor::correlationBF` to 0.0001%. |

---

## 3. What remains for Sub 1.2

### Critical path

1. **OSF deposit (HARD deadline 2026-05-15).** User deposits `output/osf-prereg-v3.md` on OSF, returns DOI to head-1.2.
   - Document path: `phases/phase-1/subphase-1.2/output/osf-prereg-v3.md`
   - User-facing instructions: `phases/phase-1/subphase-1.2/output/osf-deposit-instructions.md`
   - After deposit: record DOI in `dashboards/master-status.md` decision-log AND upgrade `shared/notes/1.2-osf-deposited.md` from stub (urgency=info) to urgency=critical with DOI/timestamp/SHA256.

2. **BioEmu batch 2 completion.** 82 array indices PENDING on fair-share. When the arrays dispatch and complete, verify ≥2,000 conformations per protein at `/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/`. Acceptable if ≥90 of 92 reach 2K conformations. If <70 reach 2K, topup needed (oversampling formula in `shared/notes/1.1-bioemu-passrates.md`).

3. **Completion report (`completion-report.md`).** Once OSF is deposited and BioEmu is at terminal state, write the Sub 1.2 completion report covering all 14 items per CLAUDE.md "Documentation-First Rule." This is the input for PlannerAI to plan Sub 1.3.

4. **Final dashboard + registry updates.** Mark all 6 SubAgents Complete in `shared/registry.md`; final master-status, compute-budget, gate-tracker pass.

### Non-blocking but useful

- **File a comment on openmm-ml issue #91** with the sentinel-bond + HBonds workaround and a minimal reproducer. Optional. Could be a Sub 1.3 follow-up.
- **Sub 1.4 implementation**: when planning Sub 1.4, the SubAgent for MACE production should reuse `test_L_hbonds.py`'s structure with checkpoint/restart added (already exists for the old `mace_hybrid_npt.py` — combine its checkpoint/restart with the Round 3 recipe).

---

## 4. Compute usage (Sub 1.2 priority SU accounting)

| Phase | Used SU | Account |
|-------|--------:|---------|
| Pre-overnight (Tests A/B/F + v6 + path bugs from prior sessions) | 58.5 | prio_mg269 |
| Test H (gpu_devel standard tier) | ~0.3 | pi_mg269 (standard) |
| Round 1 overnight (Tests I, I3, I4 — gpu_devel) | ~10.5 | pi_mg269 (standard) |
| Round 2 (Test J — gpu_devel) | ~10.0 | pi_mg269 (standard) |
| Round 3 gpu_devel (Tests K, L, M) | ~38.9 | pi_mg269 (standard) |
| **Round 3D priority (Test P, 100 ps confirmation)** | **~8.3** | **prio_mg269** |
| **Total priority SU consumed Sub 1.2** | **~67/108.5** | (well under cap) |

---

## 5. Key files / what's where

### Production recipe
- `output/scripts/npt_diagnostics/npt_diag_common.py` — `add_protein_sentinel_bonds()` and `add_protein_hbonds_constraints()` helpers
- `output/scripts/npt_diagnostics/test_L_hbonds.py` — reference recipe driver (25 ps gpu_devel)
- `output/scripts/npt_diagnostics/test_P_extended.py` — 100 ps priority queue confirmation
- `output/scripts/npt_diagnostics/test_K_halfstep.py` — alternative dt=0.5 fs recipe (slower but extra-stable)
- `output/scripts/npt_diagnostics/test_M_combined.py` — kitchen-sink reference

### Cross-agent notes
- `shared/notes/1.2-mace-npt-fixed.md` — **CONFIRMED note** with full evidence chain (urgency=critical)
- `shared/notes/1.2-mace-npt-stability.md` — historical NPT investigation, §7 RESOLUTION appended
- `shared/notes/1.2-so3lr-pilot-stability.md` — SO3LR 2/5 results
- `shared/notes/1.2-bioemu-batch2-passrates.md` — preliminary batch 2 (will need updating after dispatch)
- `shared/notes/1.2-delta-baselines-results.md` — Delta complete
- `shared/notes/1.2-stats-pipeline-validation.md` — stats pipeline complete
- `shared/notes/1.2-osf-deposited.md` — STUB awaiting DOI

### Status reports (per-task)
- `status/task-001-status.md` — needs FINAL update (currently shows `npt-failed-nvt-fallback`; should be updated to `npt-fixed-recipe-validated` post-Round-3)
- `status/task-002-status.md` — complete
- `status/task-003-status.md` — v2-drafted (the SubAgent didn't update for v3)
- `status/task-004-status.md` — slurm-10-of-93-complete
- `status/task-005-status.md` — complete
- `status/task-006-status.md` — complete

### OSF
- `output/osf-prereg-v3.md` — DEPOSIT-READY (NPT framing, 2026-05-02)
- `output/osf-deposit-instructions.md` — user-facing deposit guide
- `output/osf-prereg-v2.md` — historical v2

### Overnight summary
- `phases/phase-1/subphase-1.2/overnight-summary-2026-05-02.md` — focused log of overnight work
- `phases/phase-1/subphase-1.2/handoff-notes.md` — THIS FILE

### Production plans
- `output/npt_nvt_production_plan.md` — RETAINED as documented fallback (2-stage classical-NPT-equil → MACE-NVT) if MACE NPT fails on a specific Sub 1.4 protein

### Literature & investigation reports
- `output/mace_npt_literature_review.md` — literature SubAgent's survey identifying openmm-ml issue #91
- `output/npt_inspection_findings.md` — Round 1 SubAgent's protein-tearing observation

### Dashboards (all synced 2026-05-02T10:35Z)
- `../../../dashboards/master-status.md`
- `../../../dashboards/active-subphase.md`
- `../../../dashboards/gate-tracker.md`
- `../../../dashboards/compute-budget.md`

---

## 6. SLURM state (2026-05-02 ~10:40Z)

| Job ID | Name | Partition | State | Notes |
|--------|------|-----------|-------|-------|
| 9449458 | x9sok7yl | gpu | PENDING | BioEmu batch 2 — 41 indices (24h), Priority |
| 9449459 | l5uw4lsy | gpu | PENDING | BioEmu batch 2 — 41 indices (24h, CD19_HUMAN cancelled), Priority |
| 9611901 | cc_tmol_qq | gpu | PENDING | (unrelated job, do not interfere) |

Fair-share `pi_mg269`: 0.013 (deeply depleted). Recovers over days. No further compute jobs needed for Sub 1.2 NPT work.

---

## 7. Known caveats / what to verify in Sub 1.4

1. **Recipe validated only on WW** (~534 atoms after solvation). Sub 1.4 production runs (10 ns target) on WW/GB3/GB1/NTL9/UBQ are the ground truth for generalization. The fix is architectural (openmm-ml + AMBER14 constraints), so it should generalize, but per-protein verification at production timescales is the real test.

2. **100 ps is 1% of the 10-ns Sub 1.4 production target.** Energy was stable throughout test_P with no drift, but slow drift at longer timescales is theoretically possible. Sub 1.4 production should monitor PE drift and Rg stability per protein and have a 10-ns target with checkpoint/restart.

3. **The two-stage NVT fallback** (`output/npt_nvt_production_plan.md`) is retained as a documented backup if reviewers later request a strict-NVT comparison or if MACE NPT fails on a specific Sub 1.4 protein.

4. **HBonds constraints** add no throughput penalty (test_L hit ~0.91 ns/day, same as test_J's pre-failure rate). They DO change the velocity initialization slightly — `setVelocitiesToTemperature` now has fewer DoF, which is correct but worth noting.

5. **Check the production sbatch convention** when implementing Sub 1.4: cryptic 8-char job names; `gpu_h200` for production (per Option 5 commit); checkpoint/restart at 22.5 hr walltime guard (reuse from `mace_hybrid_npt.py` original); `PYTHONNOUSERSITE=1`; `LD_LIBRARY_PATH` includes `${CONDA_PREFIX}/lib`; OpenCL platform.

---

## 8. Compute environments

All conda environments unchanged:
- `env-mace`: MACE + OpenMM (`PYTHONNOUSERSITE=1`)
- `env-so3lr`: SO3LR (`PYTHONNOUSERSITE=0` + user-site PYTHONPATH)
- `env-bioemu`: BioEmu (login-node ABI conflict — use SLURM gpu for precache)
- `env-delta-v2`: GEARS + scGPT + scFoundation
- `env-tahoex1`: Tahoe-x1 3B
- `env-stats`: Sub 1.2 stats pipeline (Python 3.11 + PyMC + R BayesFactor)

---

## 9. Calendar

| Date | Milestone | Status |
|------|-----------|--------|
| ~~May 9~~ | D1 gate | DONE — ASSESSED: GO |
| **May 15** | **OSF pre-reg deposit** | **HARD DEADLINE — v3 ready** |
| May 16 | Sub 1.2 target end | Blocked on BioEmu fair-share |
| ~~Jun 6~~ | D3 gate | DONE — ASSESSED: GO (RETIRED) |
| Jun 30 | D2 gate | ON TRACK (MACE NPT fixed; Sub 1.4 to confirm at 10 ns) |
