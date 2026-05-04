# MACE-OFF24 Hybrid NPT Configuration Audit (v6 Fixes)

**Date:** 2026-04-25
**Auditor:** Independent review (Claude Opus 4.6)
**Script:** `output/scripts/mace_hybrid_npt.py` (v6)
**Wrapper:** `output/scripts/submit_mace_npt.sh`
**Context:** 3 Tier B proteins (WW, GB3, UBQ) on H200 OpenCL, 2.56 ns/day throughput

---

## 1. Fix-by-Fix Review

### Fix 1: Checkpoint Particle Mismatch (WW bug) -- PASS

**Lines 575-590.** The try/except around `loadCheckpoint` catches `Exception`,
checks for the substring `"wrong number of particles"` in the error message,
deletes the stale checkpoint and progress file, and sets `resuming = False`.

**Verdict: Correct and well-structured.**

Specifics:
- The catch is broad (`Exception`) which is appropriate here because
  `loadCheckpoint` can throw different exception types across OpenMM versions.
  The substring check narrows it to the specific failure.
- Both `chk_path` and `progress_path` are cleaned up (line 585-587), preventing
  a state where the progress file says "production_started=True" but the
  checkpoint is gone. Good.
- After `resuming = False`, execution falls through to the second `if resuming:`
  block (line 591) which is now False, then continues to the `else:` fresh-start
  path (line 601). Control flow is correct.
- The stale checkpoint files (DCD, CSV) from the prior solvation remain on disk
  but are harmless -- the fresh start will overwrite the topology PDB and the
  production DCD/CSV will be opened in write mode (not append) since
  `os.path.exists(prod_dcd)` will be True from the stale run. **Minor concern:**
  if a stale DCD exists from a prior solvation with a different atom count, the
  fresh run will open it in append mode (line 746), which will produce a corrupt
  DCD (mixed atom counts in the same file). See Concern C1 below.

**Concern C1 (low severity):** When a stale checkpoint triggers the
particle-mismatch path, the existing DCD and CSV files are from the old
(wrong) solvation. The script does not delete or truncate them. On the fresh
start, `DCDReporter(prod_dcd, report_steps, append=os.path.exists(prod_dcd))`
will set `append=True` because the stale DCD exists. This appends frames with
the NEW atom count to a DCD that has a header for the OLD atom count, producing
a corrupt trajectory file. The fix should also delete `prod_dcd` and `prod_csv`
when a particle mismatch is detected, or at minimum set a flag so that the
reporter is opened in write mode rather than append mode.

---

### Fix 2: StateDataReporter `_dof` Missing on Resume (GB3 bug) -- PASS

**Lines 761-764.** After constructing the `StateDataReporter` with a file handle
(append mode), the code sets `sdr._hasInitialized = True` to suppress the header,
then immediately calls `sdr._initializeConstants(simulation)`.

**Verdict: Correct. The `_dof` attribute will be set without writing a header.**

Verification against OpenMM source (`statedatareporter.py` lines 290-318):

- `_initializeConstants` is a standalone method that sets `self._dof` (if
  `self._temperature` is True) and `self._totalMass` (if `self._density` is True).
  It does NOT write any output and does NOT set `_hasInitialized`.
- The original bug: setting `_hasInitialized = True` alone (without calling
  `_initializeConstants`) caused the `report()` method to skip the
  `if not self._hasInitialized:` block entirely (line 187), which is where
  `_initializeConstants` would normally be called. When `report()` later tried
  to compute temperature at line 251, it accessed `self._dof` which was never
  set, raising `AttributeError`.
- The v6 fix calls `_initializeConstants(simulation)` explicitly after the
  monkey-patch, which sets both `_dof` and `_totalMass`. This is correct.

**However, there is a secondary missing-attribute issue (Concern C2):**

The normal initialization path in `report()` (lines 196-198) also sets:
```python
self._initialClockTime = time.time()
self._initialSimulationTime = state.getTime()
self._initialSteps = simulation.currentStep
```

The v6 fix does NOT set these three attributes. The `speed` column is enabled
(`speed=True` at line 758). When the first `report()` call happens, it will
reach line 257:
```python
elapsedDays = (clockTime - self._initialClockTime) / 86400.0
```
and raise `AttributeError: 'StateDataReporter' object has no attribute '_initialClockTime'`.

**Concern C2 (medium severity):** The monkey-patched append-mode
`StateDataReporter` will crash on the first report because `_initialClockTime`,
`_initialSimulationTime`, and `_initialSteps` are never set. The fix should add
these three lines after `_initializeConstants`:
```python
sdr._initialClockTime = time.time()
sdr._initialSimulationTime = simulation.context.getState(getTime=True).getTime()
sdr._initialSteps = simulation.currentStep
```
Alternatively, if the `speed` column is not needed on resumed sessions (it is
cosmetic), pass `speed=False` in the append-mode constructor. But the safest
fix is to set all three attributes.

**UPDATE on C2 severity:** I re-examined the control flow. The `speed=True` is
set at line 758. When `report()` is called, since `_hasInitialized` is already
True, it jumps straight to `_checkForErrors` (line 202) and then
`_constructReportValues` (line 205). Inside `_constructReportValues`, line 256-261
accesses `self._initialClockTime`. This WILL crash. **This is a real bug that
will manifest on the first reporting step of any resumed session where the CSV
already exists.** The crash will look like an `AttributeError` and exit code 1,
which the submit wrapper treats as FATAL (line 147: `elif [ $EXIT_CODE -eq 1 ] && [ $HUNG -eq 0 ]`),
killing the entire SLURM job chain.

---

### Fix 3: NPT Equilibration Increased to 50 ps (UBQ NaN bug) -- PASS WITH CAVEATS

**Lines 155-161.** `NPT_EQUIL_PS` changed from 5.0 to 50.0. `NVT_EQUIL_PS` set
to 0.0 (single-stage NPT equilibration).

**Verdict: 50 ps is a reasonable minimum for these system sizes, but marginal
for UBQ (17K atoms).**

Literature context:

- Standard practice for explicit-solvent NPT equilibration of small proteins
  (10-20K atoms) is 100-500 ps (Braun et al., Living J. Comp. Mol. Sci. 2019;
  Shirts & Chodera, J. Chem. Phys. 2008). GROMACS tutorials typically use 100 ps
  NVT + 100 ps NPT as the minimum.
- The MonteCarloBarostat in OpenMM operates by randomly scaling box dimensions
  every N steps. At freq=25, that is one volume-move attempt every 25 fs (at
  dt=1 fs). Over 50 ps = 50,000 steps, there are 2,000 barostat trial moves.
  This is sufficient for the box volume to converge for systems of this size.
- However, 50 ps is on the short side for full pressure equilibration of the
  LARGEST system (UBQ, ~17K atoms). The density may still be drifting slightly
  at 50 ps. For a 5 ns production run, the first ~10-50 ps of production will
  absorb any residual drift, which is acceptable if you discard initial frames.
- The root cause of the UBQ NaN was almost certainly that 5 ps (only 200 barostat
  moves) left significant density/pressure inhomogeneities that created clashes
  at the water-protein interface under full production dynamics.

**Recommendation:** 50 ps is adequate for the Sub 1.2 pilot (5 ns target).
For Phase 2 production (10+ ns), consider increasing to 100 ps, especially for
UBQ and HPr (the two largest Tier B systems). The wall-time cost at 2.56 ns/day
is only ~55 min for 100 ps vs ~28 min for 50 ps -- a trivial difference against
multi-day production runs. The post-equilibration checkpoint means this cost is
paid only once per protein.

**Regarding the single-stage approach:** Removing the separate NVT stage
(`NVT_EQUIL_PS = 0.0`) and running NPT from the start with MCB active is valid.
The Langevin thermostat at 300 K + MCB at 1 atm will jointly equilibrate
temperature and pressure. There is no physical requirement for a separate NVT
warmup phase, especially since `setVelocitiesToTemperature(300 K)` initializes
velocities from the Maxwell-Boltzmann distribution at the target temperature.
The older two-stage convention is a legacy of velocity-rescaling thermostats
that needed separate temperature equilibration.

---

### Post-Equilibration Checkpoint (step 0 save) -- PASS

**Lines 698-710.** After equilibration completes, `simulation.currentStep` is
reset to 0, a checkpoint is saved, and `progress["production_started"]` is set
to True.

**Verdict: Correct. The resume path will load this checkpoint properly.**

Verification:
- On startup, `resuming` is set to True only if BOTH the checkpoint file exists
  AND `progress.get("production_started", False)` is True (line 357). The
  post-equil checkpoint satisfies both conditions.
- `simulation.currentStep = 0` (line 699) resets the Python-side step counter,
  but `context.getState().getStepCount()` reflects the Context's internal
  counter which includes the 10 self-diagnostic steps + all equil steps. The
  checkpoint captures the Context state. On resume, `getStepCount()` will return
  a number > 0 reflecting the accumulated internal steps.
- **Minor inconsistency:** On resume, `loaded_step` (line 592) comes from
  `context.getState().getStepCount()` (the Context's internal counter), but
  `total_prod_steps` (line 716) is computed from `TARGET_NS * 1e6 / DT_FS`.
  If the Context counter includes equil steps, the comparison
  `current_step < total_prod_steps` at line 791 could be wrong -- production
  might appear "already at target" because the step counter includes equil.

  However, this is mitigated by line 699 (`simulation.currentStep = 0`) on fresh
  start, which resets the Python-side counter. The Context counter is NOT reset
  by this line -- only `simulation.currentStep` is. But `createCheckpoint()`
  at line 704 captures the Context state including its internal step counter
  (which still includes equil steps). On resume, `loadCheckpoint` restores that
  internal counter.

  **Concern C3 (medium severity):** The checkpoint saved at step 0 contains a
  Context with an internal step count that includes the 10 diagnostic steps +
  50,000 equil steps = ~50,010 steps. On resume, `loaded_step = getStepCount()`
  returns ~50,010, not 0. The script sets `simulation.currentStep = start_step`
  (line 723) and then `current_step = start_step` (line 785). The production
  loop runs `while current_step < total_prod_steps` where `total_prod_steps`
  = 5,000,000 (5 ns at 1 fs). So `current_step` starts at ~50,010 and the
  loop will run until 5,000,000, producing ~4.95 ns instead of 5.0 ns. This is
  a 1% shortfall, which is negligible for the pilot but should be documented.

  On subsequent resumes (after production has advanced), the step count correctly
  reflects production progress + the equil offset, so the trajectory will be
  ~4.95 ns, not 5.0 ns. Acceptable for Sub 1.2.

---

## 2. Submit Wrapper Review (`submit_mace_npt.sh`)

### Restart Loop -- PASS

**Lines 108-161.** The loop runs up to `MAX_RESTARTS=200` iterations. Python is
launched in background, a watchdog monitors stdout file mtime, and if stalled
for `HANG_TIMEOUT=1200` seconds (20 min), it kills the Python process.

**Specifics:**
- Exit code 0 (target reached): breaks out of loop. Correct.
- Exit code 1 with `HUNG=0` (true fatal, not watchdog kill): breaks. Correct.
- Exit code 2 (walltime guard): breaks. Correct.
- Any other exit code or exit 1 with `HUNG=1` (watchdog killed a hang):
  increments restart counter, sleeps 5s, restarts. Correct.
- `stall_sec` and `last_mtime` are properly reset to 0 on each restart
  (line 157-158). Good.

### Hang Watchdog Timeout (1200s = 20 min) -- PASS

**Lines 106, 130-137.** The watchdog checks stdout mtime every 60 seconds. If
unchanged for 1200 seconds (20 iterations of the inner loop), it kills Python.

- 20 min is appropriate. At 2.56 ns/day, the script processes ~5,000 steps
  (5 ps) between checkpoint saves, which takes ~3 min. With the vesin NL fix
  (eliminating GIL deadlock), true hangs should be rare. 20 min gives ample
  margin for legitimate slow periods (e.g., OpenCL context rebuild after resume)
  while catching genuine stalls.
- The two-stage kill (SIGTERM then SIGKILL after 2s) is correct.
- **Minor note:** `kill -0 $PY_PID` in the watchdog loop (line 120) checks if
  the process exists but does not distinguish zombie processes. After Python
  exits normally, `kill -0` will fail and the loop will exit to `wait`. This is
  correct behavior.

### Exit Code Handling -- PASS WITH ONE CONCERN

**Lines 144-160.** After `wait $PY_PID`, `$?` captures the exit status.

- **Concern C4 (low severity):** When the watchdog kills Python with SIGTERM
  (signal 15), `wait` returns 128+15=143. The script checks `EXIT_CODE -eq 1`
  (line 147), which is False for 143, so it falls to the else branch and
  restarts. This is the intended behavior. However, if Python catches SIGTERM
  and exits with code 1 (e.g., via the exception handler at line 878), then
  `EXIT_CODE=1` and `HUNG=1`, which also correctly triggers restart. Good.
- If the SIGKILL is needed (line 134), `wait` returns 128+9=137, also handled
  correctly by the else branch.
- `set -euo pipefail` (line 72 inside the wrap block): the `kill ... || true`
  patterns prevent the script from dying on signal-send failures. Correct.

### External GPU Keepalive -- PASS

**Lines 92-98.** Separate Python process spawned for GPU keepalive, killed on
exit via trap. This correctly addresses the GIL-blocking issue where the
in-process keepalive thread cannot run during matscipy calls.

---

## 3. Optimization Assessment

### Confirmed Dead Ends

| Path | Status | Notes |
|------|--------|-------|
| CUDA platform | Dead end | PTX version mismatch (cuda-nvrtc 13.2 vs driver 12.8) |
| openequivariance (oeq) | Dead end | API arg count mismatch (MACE 0.3.15 vs oeq 0.6.6) |
| cuequivariance CUDA kernels | Dead end | cublas >=12.5 required, torch needs 12.1 |
| GPU neighbor list | Dead end | Only 2.5% gain; matscipy is 1-2 ms of 43 ms step |
| cuequivariance naive fallback | Dead end | 100-1000x slower pathological einsums |
| TorchForce compiled model | Dead end | e3nn not TorchScript-compilable |

These are all legitimate dead ends with clear technical blockers.

### Current Configuration Assessment

| Parameter | Value | Assessment |
|-----------|-------|------------|
| Timestep | 1.0 fs | Conservative but correct (see below) |
| Barostat freq | 25 steps | Standard, appropriate |
| NB cutoff | 1.0 nm | Standard for MACE-OFF24 |
| Friction | 1.0 /ps | Standard Langevin |
| Precision | float32 bypass | Optimal for current stack |
| Neighbor list | vesin (Rust) | Optimal (GIL-free) |
| Checkpoint interval | 5000 steps (5 ps) | Good balance of recovery cost vs I/O |
| Report interval | 1 ps | Fine for pilot; could increase for Phase 2 |

### Remaining Optimization Opportunities

**O1: Timestep increase from 1.0 fs to 2.0 fs (potential 2x speedup)**

This is the single largest remaining opportunity. The script uses `constraints=None`
(line 443) which means no bond constraints, requiring the small 1 fs timestep. If
`rigidWater=True` is already set (it is, line 444) and hydrogen mass repartitioning
(HMR) is applied, a 2 fs timestep becomes stable:

- HMR redistributes mass from heavy atoms to bonded hydrogens (typically 3x
  hydrogen mass), increasing the fastest vibrational period. With HMR, 2 fs is
  standard for classical MD (Hopkins et al., J. Chem. Theory Comput. 2015).
- OpenMM's `HydrogenMassRepartitioning()` method or manual mass redistribution
  on the System object can be applied to the classical water subsystem.
- For the MACE protein subsystem, HMR may need validation: the ML potential's
  forces are not parametrized assuming HMR, but since HMR only changes masses
  (not the potential energy surface), it should be safe. Requires a short
  validation run comparing 1 fs vs 2 fs HMR energetics.
- **Expected impact:** Close to 2x throughput (5.1 ns/day). This would halve
  wall time for Phase 2 production.
- **Risk:** MACE-OFF24 was trained on 1 fs MD data. Using 2 fs may introduce
  integration artifacts in the ML region that are not present in the training
  distribution. A 100 ps validation against 1 fs reference would quantify this.
- **Recommendation:** Test in Sub 1.3 or early Sub 1.4 with a single protein
  (WW) before committing to Phase 2 production.

**O2: Reducing report interval from 1 ps to 5 or 10 ps**

Each DCD frame write and CSV line has I/O overhead. At 1 ps reporting, there
are 5,000,000 frames in a 5 ns trajectory (5 GB+ DCD for 17K atoms). Increasing
to 10 ps reduces I/O by 10x and produces more manageable file sizes.

- For observables like S2 order parameters, 10 ps sampling is standard (1 ps is
  oversampled).
- **Expected impact:** 1-3% throughput improvement from reduced I/O overhead.
  More significant benefit is reduced storage and faster analysis.
- **Recommendation:** Change to 10 ps for Phase 2 production. Keep 1 ps for
  pilot validation where fine-grained diagnostics matter.

**O3: Barostat frequency tuning**

`BAROSTAT_FREQ = 25` means one volume-move attempt every 25 fs. This is frequent.
OpenMM documentation suggests 25-100 as reasonable. Increasing to 100 reduces
barostat overhead marginally.

- **Expected impact:** <1%. The MonteCarloBarostat's cost per trial is small.
- **Recommendation:** Not worth changing for Sub 1.2. Could test 100 for Phase 2.

**O4: LAMMPS as MD engine (major refactor)**

As noted in `1.2-mace-throughput-ceiling.md`, LAMMPS has native MACE integration
via TorchScript that eliminates the PythonForce callback overhead (~5-10 ms/step,
12-23% of total). Expected ~15-25% improvement.

- **Expected impact:** ~3.1-3.4 ns/day (from 2.56).
- **Risk:** Major refactor. Need to rebuild solvation pipeline, reporters,
  checkpoint/restart in LAMMPS. Not trivial.
- **Recommendation:** Not feasible for Sub 1.2 or 1.3. Consider only if Phase 2
  production timeline is tight.

**O5: Mixed precision for classical forces**

The classical AMBER14/TIP3P-FB forces computed by OpenMM on OpenCL already use
the platform's default precision. OpenCL on H200 may default to double precision.
Forcing single precision for classical forces could provide a small speedup.

- **Expected impact:** <5%. Classical forces are <3 ms of 43 ms step.
- **Recommendation:** Low priority. Test with
  `{'Precision': 'single'}` in Platform properties if desired.

**O6: Cutoff increase from 1.0 nm to 0.9 nm**

Reducing the nonbonded cutoff from 1.0 to 0.9 nm decreases the neighbor list
size and PME real-space cost. However, MACE-OFF24 was trained with a specific
cutoff radius encoded in the model (`r_max`). The cutoff must match the model's
training cutoff.

- **Verdict:** Do NOT change. The 1.0 nm cutoff matches MACE-OFF24's `r_max`.
  Reducing it would miss interactions the model expects to see.

---

## 4. Summary of Concerns

| ID | Severity | Description | Affected Path |
|----|----------|-------------|---------------|
| C1 | Low | Stale DCD/CSV not cleaned on particle-mismatch fallback; append mode will corrupt DCD | Fresh-start after stale checkpoint |
| **C2** | **HIGH** | `_initialClockTime`, `_initialSimulationTime`, `_initialSteps` not set on append-mode SDR; `speed=True` will crash with `AttributeError` on first report of resumed session | Every resumed session with existing CSV |
| C3 | Low | Context step counter includes equil steps (~50K); production will be ~4.95 ns not 5.0 ns | Post-equil-checkpoint resume |
| C4 | Info | SIGTERM exit code 143 handled correctly by restart loop | Submit wrapper |

### C2 Is a Blocking Bug

**C2 will crash every resumed SLURM session.** The sequence is:
1. Session 1: fresh start, runs production, walltime guard fires, exits code 2.
2. Session 2: resumes, CSV exists, append-mode SDR is created with
   `_hasInitialized = True` + `_initializeConstants()`, but without
   `_initialClockTime` etc.
3. First production step triggers `report()`, which skips the `if not _hasInitialized`
   block, goes to `_constructReportValues`, and crashes at line 257 of
   `statedatareporter.py` accessing `self._initialClockTime`.
4. Python exits code 1. Submit wrapper sees exit 1 + HUNG=0, treats as FATAL,
   breaks out of restart loop. SLURM job terminates.

**Fix (3 lines, after line 764):**
```python
sdr._initialClockTime = time.time()
sdr._initialSimulationTime = simulation.context.getState(getTime=True).getTime()
sdr._initialSteps = simulation.currentStep
```

Alternatively, remove `speed=True` from the append-mode constructor (line 758).
The speed column is cosmetic and redundant with the throughput logging already
in the production loop (lines 831-837).

---

## 5. Recommendations for Phase 2 Production

1. **Fix C2 immediately** before submitting any resubmission jobs. This is a
   crash bug on every resume.

2. **Fix C1 before Phase 2.** Add cleanup of stale DCD/CSV files in the
   particle-mismatch fallback path. Low urgency for Sub 1.2 (the mismatch
   scenario requires a very specific failure mode), but important for
   reliability in Phase 2's multi-week production runs.

3. **Investigate HMR + 2 fs timestep (O1)** in Sub 1.3. If validated, this
   doubles throughput to ~5 ns/day, cutting Phase 2 wall time in half.

4. **Increase report interval to 10 ps (O2)** for Phase 2 production. Keep
   1 ps for the remaining Sub 1.2 pilot runs.

5. **Increase equilibration to 100 ps for Phase 2** (Fix 3 follow-up). 50 ps
   is adequate for the 5 ns pilot but marginal for UBQ. The extra ~28 min of
   wall time is negligible against multi-day production.

6. **Stale comment on line 629:** "Self-diagnostic: verify CUDA patch" -- this
   comment references the abandoned CUDA patch approach. The code itself (10
   integration steps + NaN check) is still useful as a general self-test. Update
   the comment to reflect its actual purpose.

7. **Stale comment on line 776:** "Checkpoint reporter: every 100k steps = 100 ps
   wall" -- the actual interval is `CHECKPOINT_INTERVAL_STEPS = 5000` (5 ps).
   Update the comment.

8. **File handle leak (minor):** Line 752 opens `csv_handle` but never closes it
   explicitly. The `StateDataReporter.__del__` method (statedatareporter.py
   line 365) only closes files it opened itself (`self._openedFile`). Since a
   file handle was passed (not a string), `_openedFile` is False and `__del__`
   will not close it. The handle will be closed on process exit by the OS, but
   for correctness, consider using a context manager or explicit close in the
   finally/cleanup path.

---

## 6. Overall Verdict

The v6 fixes address the three bugs correctly in principle:
- **Fix 1 (checkpoint mismatch):** Sound logic, minor DCD corruption edge case (C1).
- **Fix 2 (_dof):** Core fix correct, but **introduces a new crash bug (C2)** on
  resumed sessions due to missing `_initialClockTime` / `_initialSimulationTime` /
  `_initialSteps` attributes when `speed=True`.
- **Fix 3 (equilibration):** 50 ps is adequate for Sub 1.2; recommend 100 ps for
  Phase 2.
- **Post-equil checkpoint:** Correct, with minor step-counter offset (C3).
- **Submit wrapper:** Solid restart loop and watchdog logic.

**The script should NOT be submitted for production resubmission until C2 is
fixed.** The fix is 3 lines (or removal of `speed=True` from the append-mode
constructor). All other concerns are low-severity and can be deferred.
