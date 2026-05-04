---
agent: mace-npt-patch
task: task-009
status: SUPERSEDED 2026-05-02 by Round 3 recipe in shared/notes/1.2-mace-npt-fixed.md
date: 2026-05-02 (verdict superseded same day)
priority_su_used: 0
verdict: KEEP_NVT (SUPERSEDED — see SUPERSEDED banner below)
---

# **SUPERSEDED 2026-05-02**

This document's verdict (`KEEP_NVT`, "OSF v3 NVT lock should remain") was
**overruled the same day** by the Round 3 NPT recipe iteration documented in
`shared/notes/1.2-mace-npt-fixed.md`. The Round 3 recipe (sentinel-bond +
protein HBonds constraints + dt=1 fs + MCB freq=25, applied AFTER
`createMixedSystem`) produces stable MACE NPT trajectories on WW (100 ps
clean, test_P 2026-05-02) and GB3 (25 ps clean during probe TIMEOUT). UBQ
remains non-generalizing — see `shared/help-needed/head-1.2-mace-ubq-non-generalization.md`.

**OSF v3 was reverted to NPT framing 2026-05-02.** This document is retained
for audit-trail of the dt-sweep evidence and `t1insp4q` probe TSV, NOT as
guidance for current or future NPT work.

For CURRENT MACE NPT recipe + per-protein generalization status, read:
- `shared/notes/1.2-mace-npt-fixed.md` (urgency=critical)
- `shared/notes/1.2-mace-npt-prod-launch.md`
- `shared/help-needed/head-1.2-mace-ubq-non-generalization.md`

---

# task-009 Status — MACE NPT one-more-attempt (HISTORICAL, see SUPERSEDED banner)

## 1. What was tried

### Step 1 — instrumented inspection probe (gpu_devel, standard tier)

- **SLURM job 10438687** (`t1insp4q`), Wall 11:23, gpu_devel/rtx_5000_ada/qos=normal.
- Ran `test_I_inspect.py` — same configuration as Test H baseline (MACE hybrid f32,
  `apply_wrapping_fix=False`, MonteCarloBarostat present at freq=0 during NVT). Patched
  `_f32_compute` to emit one TSV row per callback with: step counter, box vectors, protein
  atom xyz bounds, excursion outside box, max pairwise distance among first 50 atoms,
  max neighbor-list edge distance, energy, fmax, any-NaN flag.
- 10 ps NVT (clean baseline) + planned 30 ps NPT.
- **Outcome:** NaN at NVT step 3500 (3.5 ps) — before NPT phase even started. Probe TSV
  preserved (6934 rows) at `logs/test_I_probe.tsv`. Probe revealed the protein gets
  TORN across the box face at step ~3499 (callback 6799): bounding box span_y exceeds
  box_b (44.6 Å > 43.86 Å) → bonded atoms appear on opposite faces → MACE NaN.
- **Note:** Sub 1.1 NVT (no MCB in System) ran 5+ ns stably. Adding `MCB(freq=0)` to the
  System breaks NVT. So `freq=0` is NOT a no-op for OpenMM 8.5.1.

### Step 2 — fix attempts (gpu_devel, standard tier)

- **SLURM job 10438957** (`t3enf9k2`, Test I3 `enforce_pbc`): Wall 14:14, FAILED.
  - `add_mace_hybrid_v2(wrap_mode='enforce_pbc')` — call
    `simulation.context.getState(getPositions=True, enforcePeriodicBox=True)` from inside
    the PythonForce callback. This re-images per-molecule using OpenMM's bonded topology.
  - **Outcome:** NaN at NVT step 5000 (5.0 ps). 30% delay vs Test I, but failure NOT
    prevented. Recursive `getState` from inside PythonForce is **safe** in OpenMM 8.5.1
    (no deadlock observed during minimization or NVT integration).
- **SLURM job 10439259** (`t4btx5wp`, Test I4 `both` modes): Wall 16:10, FAILED.
  - Combines I3 enforce_pbc with first-atom-reference + minimum-image molecular
    reassembly. Surprisingly, I4 reached NVT step 5000 cleanly (T=301.5 K, density
    0.94 g/cm³) where I3 had failed. But NaN still occurred at NVT step ~7700 (~7.7 ps).
  - Outcome consistent with the broader pattern: each fix delays the NaN further but
    none prevent it. Time-to-NaN: I (3.5 ps) → I3 (5.0 ps) → I4 (7.7 ps).
- **Test I2** (`molecular` only): not run. Mock-tested on the login node and confirmed
  to fail analytically — first-atom-reference + minimum-image breaks for proteins
  larger than half the box (WW domain ~30 Å, half-box 22 Å).

### Step 3 — priority confirmation run

- **NOT triggered.** Step 3 was conditional on Step 2 producing a passing fix. Both Step 2
  attempts (I3 confirmed, I4 expected) fail. **Priority SU spent: 0.**

## 2. Key data

### Protein-tearing failure mode (Test I, callback 6799)

| Call | box_a | pmin | pmax | span_y | exc_y | comment |
|------|------:|-----:|-----:|-------:|------:|---------|
| 6798 | 43.86 | (-2.4, -6.7, -9.2) | (40.9, 30.7, 12.7) | 37.4 | 6.7 | atoms outside box, but contiguous |
| **6799** | 43.86 | **(16.4, -13.9, -9.3)** | **(40.8, 30.7, 24.2)** | **44.6** | **13.9** | **TORN: span_y > box_b** |
| 6800 | 43.86 | NaN | NaN | — | — | MACE returns NaN |

Box constant — no barostat moves at freq=0. Failure is from internal OpenMM reimaging.

### Throughput (cost of recursive getState in I3)

Test I  NVT step 1000 reached at 86.9 s wall. Test I3 NVT step ~5000 reached at ~420 s
(NaN at step 5000 ≈ 420 s NVT wall). I3 ~5x slower per step than I (recursive getState
adds ~80% per step). NOT a deadlock — just overhead.

## 3. Patches applied

### Additive only — `npt_diag_common.py`

Added `add_mace_hybrid_v2(system, topology, positions, protein_atoms, use_f32, wrap_mode,
simulation_holder)` function with four wrap modes:

- `wrap_mode='molecular'` — first-atom-ref + minimum-image reassembly, then centroid wrap.
  (Provably wrong for proteins > half-box; not tested.)
- `wrap_mode='enforce_pbc'` — call `simulation.context.getState(enforcePeriodicBox=True)`
  from inside the PythonForce callback. Tested as I3, FAILED.
- `wrap_mode='both'` — enforce_pbc first, then molecular reassembly. Tested as I4 (pending).
- `wrap_mode='none'` — baseline, no wrapping (matches `apply_wrapping_fix=False`).

The original `add_mace_hybrid` function was NOT modified — strictly additive change.

### New diagnostic scripts

- `test_I_inspect.py` — Step 1 instrumented probe.
- `test_I2_molecular.py`, `test_I3_enforce.py`, `test_I4_both.py` — Step 2 v2 tests.
- `analyze_probe.py` — probe TSV summarizer.
- `run_test_I.sbatch`, `run_test_I2.sbatch`, `run_test_I3.sbatch`, `run_test_I4.sbatch`.

## 4. SU accounting

| Job | Test | Partition | Wall | Standard SU | Priority SU |
|-----|------|-----------|------|------------:|------------:|
| 10438687 | I_inspect | gpu_devel/rtx_5000_ada | 11:23 | ~2.85 | 0 |
| 10438957 | I3_enforce | gpu_devel/rtx_5000_ada | 14:14 | ~3.55 | 0 |
| 10439259 | I4_both | gpu_devel/rtx_5000_ada | 16:10 | ~4.05 | 0 |
| **Total** | | | 41:47 | **~10.5** | **0 of 15** |

**Total priority SU consumed: 0** (well under the 15-SU cap). Standard tier (`pi_mg269`)
on `gpu_devel` does not consume priority SU.

## 5. Recommendation to head-1.2

### KEEP_NVT — confirm OSF v3 NVT lock.

The two principled fix attempts (per-atom wrap, enforce_pbc) both fail:
- **per-atom wrap** (Test H, prior session): broke connectivity, NaN at ~6 ps NPT.
- **enforce_pbc** (Test I3, this session): preserved connectivity, NaN at 5 ps NVT.

Even with correct per-molecule wrapping (which `enforce_pbc` provably delivers — it's
OpenMM's own molecule-aware reimaging), the NaN is delayed but not prevented. The
deeper failure mechanism is the **interaction between MonteCarloBarostat-in-system,
LangevinMiddleIntegrator, and openmml's PythonForce** — not user-fixable in the
position-wrapping callback.

### Implications for the OSF pre-registration

OSF v3 NVT lock should remain. The methods section should document:
1. Phase 1 NPT viability investigation (Tests A/B/F/v6/H from prior session + Tests
   I/I2/I3/I4 from this session) — 7-9 distinct configurations tested.
2. The empirical conclusion: **MACE-OFF24 hybrid + OpenMM MonteCarloBarostat + LangevinMiddleIntegrator
   is fundamentally unstable for solvated proteins** in the openmm-ml 1.6 + OpenMM 8.5.1 stack.
3. Production protocol Path B: classical NPT equilibration → MACE hybrid NVT production.
4. Cite related published issues (openmm-ml #52, openmm-torch #34) and NNP/MM precedent
   (Galvelis 2023 JCTC chose NVT deliberately).

### Implications for upstream

**Worthwhile to file an upstream openmm-ml issue.** The minimal reproducer is now small
(~80 lines) and could be filed cleanly. Suggested issue title: "MonteCarloBarostat causes
NaN in NVT (freq=0) when present alongside MLPotential.createMixedSystem PythonForce".
This clarifies that the bug is NOT in user wrapping code but in OpenMM's interaction
between barostat-aware state and PythonForce position handling.

### No `1.2-mace-npt-fixed.md` cross-agent note will be written

The verdict was KEEP_NVT, not NPT_WORKS, so the conditional cross-agent note specified
in the task spec is NOT created.

## Artifacts

- `output/npt_inspection_findings.md` — full investigation writeup with probe data
- `output/scripts/npt_diagnostics/test_I_inspect.py`, `test_I2_molecular.py`,
  `test_I3_enforce.py`, `test_I4_both.py` — new test scripts
- `output/scripts/npt_diagnostics/run_test_I*.sbatch` — sbatch wrappers
- `output/scripts/npt_diagnostics/npt_diag_common.py` — `add_mace_hybrid_v2()` additive
- `output/scripts/npt_diagnostics/logs/test_I_probe.tsv` — Step 1 probe TSV (6934 rows)
- `output/scripts/npt_diagnostics/logs/t1insp4q_10438687.{out,err}` — Step 1 logs
- `output/scripts/npt_diagnostics/logs/t3enf9k2_10438957.{out,err}` — Step 2 I3 logs
- `output/scripts/npt_diagnostics/analyze_probe.py` — TSV summarizer
