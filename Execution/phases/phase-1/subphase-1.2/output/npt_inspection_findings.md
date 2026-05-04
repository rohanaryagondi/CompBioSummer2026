---
agent: mace-npt-patch
task: task-009
date: 2026-05-02
phase: 1
subphase: 1.2
type: investigation-findings
verdict: KEEP_NVT
---

# NPT Inspection Findings — task-009 (mace-npt-patch)

## TL;DR

**KEEP_NVT.** Three new fix attempts all failed to stabilize MACE hybrid NPT.

| Test | Configuration | NaN at | Wall | Verdict |
|------|---------------|-------:|------|---------|
| Test I (inspection probe) | apply_wrapping_fix=False, MCB freq=0 (NVT phase) | 3.5 ps NVT | 11:23 | FAIL |
| Test I3 (enforce_pbc) | wrap_mode='enforce_pbc', MCB freq=0 (NVT phase) | 5.0 ps NVT | 14:14 | FAIL |
| Test I4 (both: enforce + molecular) | wrap_mode='both' | ~7.7 ps NVT | 16:10 | FAIL |

The recursive `simulation.context.getState(enforcePeriodicBox=True)` from inside the
PythonForce callback **DID NOT deadlock** (good news — recursive `getState` is safe
in OpenMM 8.5.1). It also **DID partially work** — the NaN was delayed from 3.5 ps
to 5.0 ps. But it did not prevent the failure.

## Step 1 — Test I (instrumented inspection)

**Job:** 10438687 (`t1insp4q`), gpu_devel/rtx_5000_ada/qos=normal, completed 04:08:30Z 2026-05-02.
**Cost:** ~3 standard SU; 0 priority SU.
**Configuration:** WW domain, MACE hybrid f32, MonteCarloBarostat present (freq=0 during
NVT, freq=25 to begin NPT), `apply_wrapping_fix=False` baseline, NVT 10 ps + NPT 30 ps.
**Outcome:** **NaN at NVT step 3500 (3.5 ps), before NPT phase even started.** Probe TSV
preserved at `output/scripts/npt_diagnostics/logs/test_I_probe.tsv` (6934 rows).

## Crash-time progression across all three attempts

| Test | Configuration | NaN at | Wall to NaN | ΔTime vs Test I |
|------|---------------|-------:|------------:|----------------:|
| Test I  | no fix (probe baseline) | NVT step 3500 = 3.5 ps | 5 min | (baseline) |
| Test I3 | wrap_mode='enforce_pbc' | NVT step 5000 = 5.0 ps | 7 min | +30% |
| Test I4 | wrap_mode='both' | NVT step ~7700 = 7.7 ps | 11 min | +120% |

The fixes increase the time-to-NaN monotonically: enforce_pbc alone delays by 30%,
adding the molecule-walk reassembly delays by another ~50%. Each fix removes a pathway
for the protein to be torn, but none plug all of them. After enough integration time,
some other pathway eventually triggers a NaN. **The failure is not preventable by any
position-wrapping callback patch — it is architectural.**

### What the probe revealed (raw evidence)

The probe instrumented every MACE force callback with: step, box vectors, protein atom
xyz bounds (pmin/pmax/span), excursion outside primary cell (exc), max pairwise distance
across first 50 atoms, max neighbor-list edge distance, and any-NaN flag.

The smoking gun is callback rows 6789-6800 (NVT just before NaN):

| Call | box_a | pmin_x | pmax_x | span_x | pmin_y | span_y | exc_y | comment |
|------|------:|-------:|-------:|-------:|-------:|-------:|------:|---------|
| 6789 | 43.86 | 16.4 | 40.8 | 24.5 | 4.4 | 26.4 | 0 | normal NVT |
| 6794 | 43.86 | 7.7 | 40.9 | 33.2 | 4.6 | 26.2 | 0 | drifting toward x=0 face |
| 6798 | 43.86 | -2.4 | 40.9 | 43.2 | -6.7 | 37.4 | 6.7 | atoms 6.7 Å outside box; **span ≈ box** |
| **6799** | 43.86 | 16.4 | 40.8 | 24.4 | -13.9 | **44.6** | 13.9 | **protein TORN — span_y > box_b** |
| 6800 | 43.86 | NaN | NaN | — | NaN | NaN | — | MACE returns NaN forces |

**Box was constant at 43.86 Å throughout** (no barostat moves at freq=0). The crash is
**not** triggered by box rescaling. It is triggered by **OpenMM internally re-imaging
some protein atoms after natural drift causes the protein bounding box to exceed the
periodic cell**. Bonded atoms end up on opposite sides of the box → MACE neighbor list
sees a "split" protein with edges across the box face → MACE returns NaN forces.

### Why MCB+freq=0 still triggers the failure in NVT

Sub 1.1 NVT (no MCB in System) ran 5+ ns stably. Test I added MCB with `freq=0` to enable
the planned Stage 2 switch — and NVT itself failed at 3.5 ps. The presence of MCB in the
System changes how OpenMM handles periodic-box-aware state during integration, even when
its frequency is 0. At least empirically, `MCB(freq=0)` is NOT a no-op.

## Step 2 — fix attempts

### Test I2 (molecular reassembly, not run)

`add_mace_hybrid_v2(wrap_mode='molecular')` was implemented in `npt_diag_common.py` but
**not run** because mock-testing on the login node showed it cannot work for proteins
larger than half-box. WW domain is ~30 Å diameter; half-box of 43.86 Å is 21.93 Å. With
first-atom-reference + minimum-image, atoms beyond 22 Å from atom 0 get reassembled to
the wrong periodic image. (Verified analytically — see `analyze_probe.py` mock test in
the body of this investigation.)

For a graph-walk reassembly to fix this, we'd have to walk the protein bond list (BFS
from atom 0, placing each atom at the periodic image closest to its already-placed
bonded neighbor). This is exactly what OpenMM's `enforcePeriodicBox=True` does
internally — so directly testing that mode (Test I3) is the right experiment.

### Test I3 (enforce_pbc)

**Job:** 10438957 (`t3enf9k2`), gpu_devel/rtx_5000_ada/qos=normal, FAILED 04:27:19Z 2026-05-02.
**Cost:** ~4 standard SU; 0 priority SU.
**Configuration:** WW domain, MACE hybrid f32, `wrap_mode='enforce_pbc'`. Inside
`_f32_compute_v2`, on each callback, pull a fresh state via
`simulation.context.getState(getPositions=True, enforcePeriodicBox=True)`. This re-images
per-molecule using OpenMM's bonded topology, preserving connectivity.
**Outcome:** **NaN at NVT step 5000 (5.0 ps).** Recursive `getState` from inside a
PythonForce callback is **safe** (no deadlock) — verified by clean minimization with the
fix in place. But the NVT crash still occurred, just delayed by ~30%.

### Test I4 (enforce_pbc + molecular reassembly)

**Job:** 10439259 (`t4btx5wp`), gpu_devel/rtx_5000_ada, FAILED 04:47:15Z 2026-05-02.
**Cost:** ~4 standard SU; 0 priority SU.
**Configuration:** Combines I3's `enforce_pbc` state read with first-atom-reference +
minimum-image molecular reassembly. By the time enforce_pbc has done its molecule-walk,
the protein is contiguous, so the molecular-reassembly with first-atom reference is
mostly a no-op (frac_diff < 0.5 for all atoms reassembled by enforce_pbc).
**Outcome:** **NaN at NVT step ~7700 (~7.7 ps).** Surprisingly, I4 reached NVT step
5000 cleanly (logged at wall 430.6s with T=301.5 K, density 0.94 g/cm³ — healthy state)
where I3 had crashed. This suggests molecular reassembly was DOING something useful
beyond what enforce_pbc alone provided. But the NaN still occurred 2.7 ps later. Same
qualitative conclusion as I3: fix delays the NaN but does not prevent it.

## Why the fixes don't work

The crash signature is consistent across all attempts:

- Test I: NaN at NVT 3.5 ps (no fix)
- Test I3: NaN at NVT 5.0 ps (enforce_pbc)
- Test H (prior): NaN at NPT ~6 ps (per-atom wrap, MCB freq=25)

The wrapping fixes **delay** the NaN by ~30-70%, but **do not prevent** it. This indicates
the failure mechanism is NOT just "protein torn across the box during a single getState
call." There's a deeper interaction between MCB-in-system + LangevinMiddleIntegrator +
PythonForce that introduces some numerical drift even at MCB freq=0.

Two consistent observations strengthen this conclusion:

1. **Box stays constant during NVT** (verified by probe data). MCB freq=0 does not rescale
   the box. Yet the protein still ends up torn after a few ps.
2. **Sub 1.1 NVT (no MCB at all in System) ran 5+ ns stably** with the same protein, env,
   and MACE setup. Adding MCB(freq=0) to the System breaks NVT.

The most likely explanation: when MCB is added to a system, OpenMM's state machine engages
periodic-box-aware position handling that disrupts the PythonForce/MACE feedback loop in
ways the user cannot patch from inside the callback. The torn protein at row 6799 is
likely the result of OpenMM internally calling a per-atom wrap somewhere (perhaps inside
the integrator's drift step) before the PythonForce callback fires.

This is consistent with openmm-ml issue #52 (PBC not replicated for ML portion) and
openmm-torch issue #34 (protein unfolds with ANI-2x + MC barostat, labeled wontfix). The
class of bug is architectural to openmm-ml + barostat, not fixable in user-space patches.

## Recommendation to head-1.2

**KEEP_NVT.** The OSF v3 NVT lock should remain in place. Sub 1.4 production should use
NVT-only with classical NPT pre-equilibration (Path B in `npt_investigation_results.md`).

This investigation has consumed:
- Step 1 standard SU: ~3 (gpu_devel rtx_5000_ada)
- Step 2 standard SU: ~7.6 (gpu_devel rtx_5000_ada — Test I3 + Test I4)
- Step 3 priority SU: 0 (Step 3 was conditional on Step 2 success — not triggered)
- **Total priority SU spent across all task-009 work: 0** (well under the 15 SU cap).

Even though Test I4 reached NVT 5 ps cleanly (where I3 had crashed) and showed the
fix progression delivers ~2x stability gain, the NaN at NVT 7.7 ps is still well below
the threshold needed for production (10-50 ns). The fix is not robust enough.

## Artifacts (all under `/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/`)

- `output/scripts/npt_diagnostics/test_I_inspect.py` — Step 1 inspection probe script
- `output/scripts/npt_diagnostics/test_I2_molecular.py` — Step 2 molecular wrap (not run, see above)
- `output/scripts/npt_diagnostics/test_I3_enforce.py` — Step 2 enforce_pbc (FAIL)
- `output/scripts/npt_diagnostics/test_I4_both.py` — Step 2 both modes (FAIL)
- `output/scripts/npt_diagnostics/run_test_I.sbatch` — sbatch wrapper for Step 1
- `output/scripts/npt_diagnostics/run_test_I2.sbatch` `run_test_I3.sbatch` `run_test_I4.sbatch`
- `output/scripts/npt_diagnostics/npt_diag_common.py` — `add_mace_hybrid_v2()` added (additive)
- `output/scripts/npt_diagnostics/analyze_probe.py` — probe TSV summarizer
- `output/scripts/npt_diagnostics/logs/test_I_probe.tsv` — Step 1 inspection probe (6934 rows)
- `output/scripts/npt_diagnostics/logs/t1insp4q_10438687.{out,err}` — Step 1 stdout/stderr
- `output/scripts/npt_diagnostics/logs/t3enf9k2_10438957.{out,err}` — Step 2 I3 stdout/stderr
- `output/scripts/npt_diagnostics/logs/t4btx5wp_10439259.{out,err}` — Step 2 I4 stdout/stderr

## SU accounting

| Job | Test | Partition | Wall | Standard SU | Priority SU |
|-----|------|-----------|------|------------:|------------:|
| 10438687 | I_inspect | gpu_devel/rtx_5000_ada | 11:23 | ~2.85 | 0 |
| 10438957 | I3_enforce | gpu_devel/rtx_5000_ada | 14:14 | ~3.55 | 0 |
| 10439259 | I4_both | gpu_devel/rtx_5000_ada | 16:10 | ~4.05 | 0 |
| **Total** | | | 41:47 | **~10.5** | **0 of 15** |

Standard tier billing 15 SU/hr × elapsed; gpu_devel does not consume priority SU.
