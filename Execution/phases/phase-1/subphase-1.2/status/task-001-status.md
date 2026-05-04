---
task_id: "task-001"
agent: "mlff-mace-pilot"
subphase: "1.2"
status: npt-fixed-WW-GB3-VALIDATED-UBQ-NON-GENERALIZING-options-c-d-IN-FLIGHT
date: 2026-05-04
---

## Update 2026-05-04 (05:00Z): UBQ option-c + option-d probes IN FLIGHT

Per user direction post 2026-05-03 escalation, BOTH UBQ remediation paths submitted in parallel on `scavenge_gpu` (free billing) — verdicts pending dispatch:

- **Option (c) — NTL9 substitute**: SLURM 10622876 (tag `q6kz3m8x`), 50 ps NPT probe, walltime 5:55:00. NTL9 has smallest protein-ATOM count of candidate set (390 vs UBQ 602). Detail: `status/task-001-substitute-status.md` + `shared/notes/1.2-mace-npt-prod-launch.md` § option-c.
- **Option (d) — UBQ alternate starting structure (1XQQ chain A model 1, NMR)**: SLURM 10622885 (tag `q6uadt05`), 50 ps NPT probe at dt=0.5 fs, walltime 5:55:00. Tests whether 1UBQ failure is starting-structure stress vs architectural. Detail: `status/task-001-ubq-altstruct-status.md` + `shared/notes/1.2-mace-npt-prod-launch.md` § option-d.

Recipe LOCKED (Round 3); only the starting PDB is varied across probes. Both probes are PENDING at note-write time.

---

## Update 2026-05-03 (20:30Z): probe verdicts terminal + 3 optimization rounds + UBQ escalation

### Probe verdicts

- **GB3** (probe 10458154 b8r3kt5x): **PASS** — 25 ps clean during walltime TIMEOUT. Recipe generalizes to ~9.9K-atom GB3 hybrid system. Production submitted on scavenge_gpu.
- **UBQ** (3 dt-sweep probes ALL FAILED — pattern asymptotic):
  - dt=1.0 fs (10458155 c4n7vp2j): NaN @ 7-8 ps
  - dt=0.5 fs (10463455 q6u4n8mx): NaN @ 8-9 ps
  - dt=0.25 fs (10475183 q6u4dt25): NaN @ 9.6 ps (gpu_devel H200)
- **WW**: production submitted directly (test_P 100 ps had pre-validated)

### UBQ escalation

The Round 3 recipe does NOT generalize to UBQ-class system size (~17K atoms / ~1.2K MACE atoms). dt halving only delays failure by ~1 ps. Pathology is architectural, not numerical. Escalated via `shared/help-needed/head-1.2-mace-ubq-non-generalization.md`. **D-UBQ-1 user decision pending**: (a) NVT pivot per documented R1 fallback (auditor + project reviewer recommend), (b) Tier-3 NPT untested combo, (c) drop UBQ from criterion (silent compromise — avoid), (d) different starting structure.

### 3 optimization rounds applied

R1+R2+R3 (~30-35% MACE throughput cumulative): callback constant-tensor pre-alloc, NaN/checkpoint cadence, constraint tolerance 1e-4, DCD 5ps stride, NPT_EQUIL 25ps, OMP/MKL=4, NUMA pinning, drop forces from check_nan, MAX_MIN_ITER 500. Recipe physics unchanged.

### scavenge_gpu pivot + current jobs

All MACE production now on `scavenge_gpu` (1/10 Standard billing rate, PreemptMode=REQUEUE survivable via checkpoint/restart):
- 10567503 (q6wmsv5n): MACE WW NPT 5 ns
- 10567504 (q6gpsv9k): MACE GB3 NPT 5 ns
- UBQ: HELD pending D-UBQ-1

Cumulative SU savings vs original baseline: ~93% (Sub 1.2 closure ~3,500 SU vs ~38,000 original projection).

### Cancellation history (3 cycles for optimization rounds)
- Original Standard Tier: 10463584/85 (cancelled)
- Round 1 scavenge: 10550447/8 (cancelled)
- Round 2 scavenge: 10558479/80 (cancelled)
- Current: 10567503/4

---

# Status Report: Task 001 -- MACE-OFF24 NPT 5 ns x 3 Tier B (WW / GB3 / Ubiquitin)

## Update 2026-05-02 (16:00Z): Round 3 recipe FIXED; production driver written; probes submitted

**MACE NPT is fixed.** After 3 rounds of NPT diagnostics across 2 sessions (2026-05-01 → 2026-05-02), the production recipe was identified, validated, and committed. test_P (Round 3D, priority queue, job 10441986) ran 100 ps clean NPT on WW with final state density 1.041 g/cm³, T 297.6 K, PE -364,840 kJ/mol — the trajectory was stable throughout with no drift.

**Production recipe (locked, drop-in for Sub 1.4 — see `shared/notes/1.2-mace-npt-fixed.md`):** After `MLPotential('mace-off24-medium').createMixedSystem(...)`, apply two patches BEFORE constructing `Simulation`:

1. `add_protein_sentinel_bonds(hybrid_system, topology, protein_atoms)` — zero-strength HarmonicBondForce along the protein bonded graph. Fixes openmm-ml issue #91 singleton-molecule scaling under MonteCarloBarostat.
2. `add_protein_hbonds_constraints(hybrid_system, topology, protein_atoms)` — re-adds AMBER14 HBonds rigid constraints for protein heavy-atom-H bonds. Fixes the unconstrained-H instability at dt=1 fs.

Then `MonteCarloBarostat(1 atm, 300 K, freq=25)` always-on, `LangevinMiddleIntegrator(300 K, 1/ps, dt=1 fs)`, OpenCL platform.

**Production driver written:** `output/scripts/mace_hybrid_npt_prod.py` (~1000 lines) combines the test_L recipe with checkpoint/restart, walltime guard at 22.5 hr, append-mode reporters with `_initializeConstants` monkey-patch (the v5 GB3 fix), GPU keepalive, Vesin NL monkey-patch. Sbatch wrapper `output/scripts/submit_mace_npt_prod.sh` handles resubmission loop on exit code 2.

### Diagnostic probes submitted 2026-05-02 (priority_gpu, prio_mg269)

Per the diagnostic-first rule, GB3 and UBQ have NEVER been tested with the new recipe. Submitted 50 ps NPT probes:

| Job ID | Tag | Protein | Walltime | Expected SU |
|--------|-----|---------|----------|-------------|
| 10458154 | b8r3kt5x | GB3 | 1:30:00 | ~3-5 priority |
| 10458155 | c4n7vp2j | UBQ | 2:00:00 | ~5-7 priority |

WW does NOT need a re-probe — test_P (job 10441986) already validated the recipe to 100 ps clean on WW.

Probe success criteria (all must hold per protein):
- No NaN through 50 ps
- T 285-315 K rolling 10-ps mean
- Density 1.00-1.06 g/cm³ at end
- Box volume drift <8% in last 25 ps
- progress.json + meta JSON consistent

### Production submission plan (HELD pending probe verdict)

After probes pass, submit 3 production jobs on Standard Tier `gpu_h200` / `pi_mg269`:
- WW: TARGET_NS=5.0, walltime 23:59:00
- GB3: TARGET_NS=5.0, walltime 23:59:00
- UBQ: TARGET_NS=5.0, walltime 23:59:00

Throughput projection (Sub 1.1 §11 + size scaling): WW ~2.56 ns/day, GB3 ~1.6, UBQ ~1.05 (H200 OpenCL hybrid). Resubmits to reach 5 ns: WW ~3, GB3 ~4, UBQ ~6.

Compute envelope: ~125K standard SU on `gpu_h200`; within Sub 1.2 plan (no SU bump for production).

### Compute accounting (priority Sub 1.2 SU)

| Phase | Used Priority SU | Account |
|-------|-----------------:|---------|
| Pre-overnight (Tests A/B/F + v6 + path bugs) | 58.5 | prio_mg269 |
| Round 3D priority (Test P, 100 ps confirmation) | ~8.3 | prio_mg269 |
| GB3 + UBQ probes (estimate, 2026-05-02 launch) | ~10 | prio_mg269 |
| **Total Sub 1.2 priority SU committed/scheduled** | **~77** | (cap ~108.5; remaining ~31.5) |

User-authorized closure-window envelope: ~50 priority SU shared with SO3LR rescue gates (~20 SU). MACE probe + production iteration budget within envelope.

### Cross-agent notes

- `shared/notes/1.2-mace-npt-fixed.md` — CONFIRMED critical (Round 3 recipe + evidence chain)
- `shared/notes/1.2-mace-npt-prod-launch.md` — important (this launch state + production plan)
- `shared/notes/1.2-mace-npt-stability.md` §7 RESOLUTION — appended

### Recipe references

- Reproducible drivers: `output/scripts/npt_diagnostics/test_L_hbonds.py` (25 ps gpu_devel) and `output/scripts/npt_diagnostics/test_P_extended.py` (100 ps priority queue)
- Helpers: `output/scripts/npt_diagnostics/npt_diag_common.py` lines 500-619 (`add_protein_sentinel_bonds`, `add_protein_hbonds_constraints`)

---

## Update 2026-04-30: Test H (Wrapping Fix) SUBMITTED

NPT is NOT dead. The root cause (missing minimum-image wrapping in `_computeMACE`)
has been fixed and is under test.

**Fix:** 3-line minimum-image wrapping patch added to f32 bypass in
`npt_diag_common.py:add_mace_hybrid(apply_wrapping_fix=True)`. Wraps protein
positions into the primary periodic cell before `get_neighborhood` call:
```python
if apply_wrapping_fix and periodic:
    frac = pos @ np.linalg.inv(cell)
    frac -= np.floor(frac)
    pos = frac @ cell
```

**Test H submission:**
| Field | Value |
|-------|-------|
| Job ID | 10328941 (prev: 10328719 scavenge_gpu cancelled — 95 ahead; 10321551 gpu_devel cancelled — 11th/11; 10315976 priority_gpu cancelled) |
| Job name | 2cp2fn3k |
| Partition | gpu_devel (RTX 5000 Ada) |
| Wall time | 3:10:00 (standard SU, not priority) |
| Protocol | 50 ps equil + 150 ps production |
| Success metric | Survives past 30 ps equil (v6 crashed at ~25 ps without fix) |
| SU budget | Uses standard tier (pi_mg269). Priority SU preserved: 58.5/108.5 used |
| Est. start | Backfill eligible — could start any time |
| Script | `output/scripts/npt_diagnostics/run_test_H.sbatch` (self-contained, no env var dependency) |
| Stale cache | `__pycache__` deleted pre-submission |

**RESULT: FAIL.** NaN at ~5-6 ps equil (step ~5500). Wrapping fix made no difference vs Test B (also NaN at ~5ps without fix). Last good state: step 5000, T=299.9 K, rho=1.0240 g/cm³. The root cause is NOT minimum-image wrapping — it is a deeper incompatibility between MonteCarloBarostat trial moves and the MACE hybrid PythonForce callback.

**Decision: NPT is NOT viable. NVT is the production path (Path B).** Two-stage protocol: classical NPT equilibration (box density) → MACE hybrid NVT production. Design in `output/npt_nvt_production_plan.md`.

**Full diagnostic history:**
| Test | Fix | Crashed at | Conclusion |
|------|-----|-----------|------------|
| Test A | Classical NPT (no MACE) | PASS (80 ps clean) | Barostat works without MACE |
| Test B | MACE f32, freq=100 | ~5 ps | Barostat freq doesn't help |
| Test F | MACE f64 | ~17 ps | f64 delays but doesn't fix |
| v6 | MACE f32, freq=25 | ~25 ps | Production settings crash |
| **Test H** | **MACE f32 + wrapping fix** | **~5 ps** | **Wrapping fix ineffective** |

**Priority SU accounting (final):**
| Phase | SU used | Budget |
|-------|---------|--------|
| Prior diagnostics (Tests A/B/F + v6 + path bugs) | 58.5 | 50 (original) |
| Test H (2cp2fn3k, ~0.3 SU actual) | 0.3 | 50 (new, user directive 2026-04-30) |
| Total used | 58.8 | 108.5 cap |

---

## Remediation 2026-04-19T01:37Z (head-1.2 resume session)

v1 jobs 8885960/61/62 FAILED exit 1:0 in 4-5s each due to conda-path
regression in `submit_mace_npt.sh` (hardcoded `/home/rag88/miniconda3/`
path does not exist; correct path is
`/apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh`).
Fix: 1 line in sbatch wrapper. env-mace untouched. No Python script
changed. Failed logs preserved as `.failed` suffix. 3 fresh SLURM jobs
submitted with new cryptic tags:

| Protein | Fresh tag | SLURM ID | State     |
|---------|-----------|---------:|-----------|
| WW      | t4x7qn2w  | 8893817  | PENDING   |
| GB3     | f9b3rk6h  | 8893818  | PENDING   |
| UBQ     | p8m5dz1g  | 8893819  | PENDING   |

See remediation cross-agent note: `shared/notes/1.2-mace-conda-path-fix.md`.
Stability cross-agent note updated with v1 FAILED / v2 PENDING job IDs.

---

## Summary

Forked the Sub 1.1 MACE hybrid NVT script into a Sub 1.2 NPT production driver
with MonteCarloBarostat, 2-stage equilibration (NVT 50 ps + NPT 200 ps),
OpenMM checkpoint/restart, append-mode DCD + CSV reporters, and a 22.5-hr
walltime guard. Submitted 3 SLURM jobs to `gpu_h200` (OpenCL, per Sub 1.1
Option 5): WW (tag `m4k2pz9q` = 8885960), GB3 (`n7r9tx4w` = 8885961),
ubiquitin (`q3j8vb6p` = 8885962). All jobs are PENDING on gpu_h200 as of
2026-04-19T04:04 UTC. Production runs will take 8-12 days wall with multiple
24h resubmissions per protein; completion + stability verdicts are deferred
to HeadAI follow-up.

---

## What Was Done

1. **Read the task spec** and Sub 1.1 reference artifacts (source NVT script,
   §11 H200 OpenCL hybrid WW benchmark, Crambin D1 PASS note, operational
   practices).

2. **Created output directories:**
   - `output/scripts/` (Python driver + SLURM wrapper)
   - `output/trajectories/mace_npt/` (DCDs, topologies, state logs, meta JSONs)
   - `output/slurm_logs/` (stdout/stderr per job)
   - `/nfs/roberts/scratch/pi_mg269/rag88/alpha-m/mace-npt/{tag}/` (checkpoints,
     progress tracking, equilibration-end state)

3. **Forked `mace_hybrid_nvt.py` (Sub 1.1, 579 lines) to
   `output/scripts/mace_hybrid_npt.py` (~580 lines)** with these modifications:
   - Added `MonteCarloBarostat(1 atm, 300 K, freq=25)` to the hybrid system,
     toggled between disabled (NVT stage) and enabled (NPT stage) via
     `setFrequency(0)` / `setFrequency(25)`.
   - Added a resume-from-checkpoint branch using
     `simulation.context.loadCheckpoint(bytes)` / `.createCheckpoint()`.
   - Append-mode `DCDReporter(path, stride, append=True)` on resumes.
   - File-handle-based `StateDataReporter` with suppressed duplicate header on
     resumes.
   - Periodic `CheckpointReporter(path, 100000)` = ~100 ps wall at 1 fs step.
   - Walltime guard: monitors `time.time() - t_session_start` and exits with
     exit code 2 once it exceeds 81,000 s (22.5 hr), saving a final
     checkpoint and progress update first.
   - 2-stage equilibration: 50 ps NVT at dt=0.5 fs (barostat disabled) + 200 ps
     NPT at dt=1 fs (barostat enabled). Production starts after equilibration,
     with `simulation.currentStep` reset to 0 for clean ns bookkeeping.
   - Per-protein env-var driven config: `MACE_HYBRID_PROTEIN` selects WW/GB3/UBQ
     defaults; `MACE_HYBRID_TAG`, `MACE_OUTPUT_DIR`, `MACE_SCRATCH_DIR`,
     `MACE_HYBRID_TARGET_NS`, `MACE_HYBRID_BAROSTAT` control individual runs.
   - All Sub 1.1 safeguards retained verbatim: `PYTHONNOUSERSITE=1`,
     `maxIterations=2000` for minimization, post-min max-force <1e5 check,
     GPU keepalive thread (5-min matmul cadence), OpenCL platform only.

4. **Wrote SLURM wrapper `output/scripts/submit_mace_npt.sh`:**
   - Takes `<protein>` + `<tag>` positional args.
   - Submits to `gpu_h200` with `--gres=gpu:h200:1`, `--time=23:59:00`,
     `--mem=32G`, `--cpus-per-task=4`, `--account=pi_mg269`.
   - Cryptic 8-char job name (from the `<tag>` arg).
   - Passes all MACE_* env vars through `--export=ALL,...`.
   - Activates env-mace via `conda activate env-mace` + `PYTHONNOUSERSITE=1`.
   - Output logs to `output/slurm_logs/mace_npt_<protein>_<tag>_<jobid>.out/.err`.

5. **Verified script Python syntax** via `ast.parse()` in env-mace interpreter.
   Syntax OK; no import-time errors observed in the wrapper's env-verification
   preamble (inherited from Sub 1.1 wrapper design).

6. **Submitted 3 SLURM jobs:**
   - `./submit_mace_npt.sh ww  m4k2pz9q` -> SLURM 8885960 (PENDING)
   - `./submit_mace_npt.sh gb3 n7r9tx4w` -> SLURM 8885961 (PENDING)
   - `./submit_mace_npt.sh ubq q3j8vb6p` -> SLURM 8885962 (PENDING)

7. **Verified job state:** all 3 jobs confirmed in `squeue -u rag88` as
   PENDING on gpu_h200 with the expected cryptic job names. No errors in
   SLURM submission response.

8. **Wrote experiment log** at `output/task-001-experiment.md` documenting
   setup, parameters, commands, expected outcomes per-protein, and the
   resume/restart protocol for HeadAI.

9. **Wrote cross-agent note** at `shared/notes/1.2-mace-npt-stability.md`
   with preliminary approach, extrapolated throughput, per-protein resource
   estimates, risks, and fallback paths. Tracks: alpha-m; urgency: important.

---

## Artifacts Produced

| Artifact | Path | Description | Verified |
|----------|------|-------------|----------|
| Forked NPT production script | output/scripts/mace_hybrid_npt.py | ~580 LOC Python; NPT + checkpoint/restart | yes (ast.parse OK) |
| SLURM submission wrapper | output/scripts/submit_mace_npt.sh | Bash; H200 OpenCL; per-protein + tag args | yes (chmod +x, 3 submits) |
| Experiment log | output/task-001-experiment.md | Full setup + expected outcome + resume protocol | yes |
| Cross-agent note | shared/notes/1.2-mace-npt-stability.md | Preliminary approach + extrapolated throughput | yes |
| Output dirs initialized | output/trajectories/mace_npt/, output/slurm_logs/ | Empty; will populate when jobs run | yes |
| Scratch dirs initialized | /nfs/roberts/scratch/pi_mg269/rag88/alpha-m/mace-npt/{m4k2pz9q,n7r9tx4w,q3j8vb6p}/ | Empty; will populate on first checkpoint | yes |

### Artifacts pending (produced by SLURM jobs, not by this SubAgent run)

| Artifact | Path | When |
|----------|------|------|
| WW NPT DCD | output/trajectories/mace_npt/ww_npt.dcd | After 1st job saves equilibration state and begins production |
| WW NPT state log | output/trajectories/mace_npt/ww_npt_state.csv | Same |
| WW topology | output/trajectories/mace_npt/ww_topology.pdb | Written at end of equilibration |
| WW meta JSON | output/trajectories/mace_npt/ww_npt_meta.json | Updated at each session exit |
| WW checkpoint | /nfs/roberts/scratch/pi_mg269/rag88/alpha-m/mace-npt/m4k2pz9q/checkpoint_latest.chk | First save at ~100 ps production wall |
| GB3 / UBQ ditto | Same pattern with gb3/ubq tags | Same |
| Per-protein stability report | output/mace_npt_stability_report.md | After all 3 proteins reach >=4.5 ns (HeadAI follow-up) |

---

## Success Criteria Evaluation

Per-task spec (pre-production; HeadAI will re-evaluate after trajectories land):

| # | Criterion | Met? | Evidence |
|---|-----------|------|----------|
| 1 | mace_hybrid_npt.py exists at output/scripts/ with NPT support + checkpoint/restart | yes | File created; MonteCarloBarostat + save/loadCheckpoint + append-mode reporters + walltime guard all present |
| 2 | WW domain trajectory >=4.5 ns, stable T/P/density, zero NaN | pending | Job submitted (8885960, PENDING). Production TBD. |
| 3 | GB3 trajectory >=4.5 ns, stable T/P/density, zero NaN | pending | Job submitted (8885961, PENDING). Production TBD. |
| 4 | Ubiquitin trajectory >=4.5 ns, stable T/P/density, zero NaN | pending | Job submitted (8885962, PENDING). Production TBD. |
| 5 | Per-protein stability report | pending | Template written in experiment log; full analysis after all 3 trajectories complete |
| 6 | Cross-agent note 1.2-mace-npt-stability.md | yes (preliminary) | Written; will be amended with empirical stability data once trajectories complete |
| 7 | SLURM job names are 8-char cryptic alphanumeric | yes | m4k2pz9q / n7r9tx4w / q3j8vb6p all 8-char alpha+numeric |
| 8 | H200 SU consumption documented | yes (estimate) | Estimated ~126,000 SU total (23.98h * 300 SU/hr * 3 jobs * ~6 resubmits avg). Actual will be logged post-completion. |
| 9 | Status report written to status/task-001-status.md | yes | This file |

---

## Unexpected Findings

None at this stage -- all steps ran exactly as planned. The SLURM cluster is
responsive (gpu_h200 showing multiple `alloc` and `mix` nodes; jobs entered
PENDING queue immediately). Env-mace is intact from Sub 1.1; no regressions
observed during the env verification step in the wrapper preamble.

**One observation for the cross-agent note:** `output/scripts/so3lr_pilot_runner.py`
is also present in this directory (2026-04-19 00:04, presumably the sibling
task-002 SubAgent's script). This is expected per the HeadAI wave structure
(WAVE 1 launches task-001 + task-002 + task-003 in parallel). No conflict --
each task writes to its own trajectory subdir.

---

## What the Next Agent Needs to Know

### HeadAI 1.2 (immediate follow-up)

1. **Arm jobstats auto-monitor NOW** -- first SLURM job is in queue. See the
   reference implementation in `shared/notes/operational-practices.md`.
   Run it as a background bash loop that polls `squeue -u rag88 -t R` every
   10 min and emits `LOW_GPU_UTIL` events when any running job has GPU util
   <10% for >30 min. Stop the monitor when the last of these 3 (plus the
   task-002 SO3LR jobs) reaches a terminal state.

2. **Expect the first checkpoint_latest.chk to appear at ~100 ps production.**
   For WW at 2.11 ns/day H200 OpenCL throughput, that is ~55 min wall after
   the ~7 min system build + ~10-30 min minimization + ~250 ps equilibration
   (another ~1.2 hr wall for equilibration alone at the equil-specific dt=0.5fs
   for NVT stage). **Full first-session timeline estimate: ~4-5 hr wall to
   reach first production checkpoint on WW; 6-9 hr on UBQ (largest system).**

3. **Exit codes to monitor:**
   - `0` = trajectory reached target 5 ns; protein done.
   - `2` = walltime exit; resubmit same tag to continue.
   - `1` = fatal (NaN, OpenCL hang escalated to exception, barostat explode).
     Read `<tag>_npt_meta.json` `fatal_exception.traceback` to diagnose.

4. **Fallback decision tree** (documented in cross-agent note and experiment log):
   - NaN during NPT equilibration -> fall back to NVT (`BAROSTAT_MODE=nvt`) for that protein.
   - OpenCL hang on 3+ consecutive resumes -> fall back to RTX 5000 Ada (slower).
   - All 3 jobs fail consistently -> escalate as help-needed; re-examine Option 5 commitment.

### Wave 2 HeadAI (on partial-completion trigger)

Per HeadAI protocol, Wave 2 launches as soon as all 3 Wave 1 jobs are in
SLURM (done -- 8885960/61/62 confirmed PENDING). Wave 2 launch is NOT
gated on MACE NPT stability results -- those deploy over ~6-12 days after
this note. Wave 2 tasks (004-006) have no dependencies on task-001 outputs.

### Sub 1.4 planner

Sub 1.4 production scope depends on Sub 1.2 MACE NPT stability evidence:

- If all 3 proteins succeed at 5 ns NPT: Sub 1.4 production proceeds NPT at
  10 ns baseline on ~9 MLFF-feasible proteins.
- If 1-2 succeed: Sub 1.4 uses NPT on those, NVT on the failures.
- If 0 succeed: Sub 1.4 uses NVT only on all proteins (Sub 1.1 demonstrated
  stable). D2 G1 (>=1 MLFF stable >=10 ns on >=3 Tier B) still achievable in
  NVT.

---

## Resource Usage

| Resource | Estimated | Actual |
|----------|-----------|--------|
| GPU-hours | ~420 H200-GPU-hr (8-12 days x 3 jobs) | TBD (jobs still PENDING) |
| Wall time | 8-12 days total (parallel 3 jobs) | TBD |
| Storage | ~150 MB trajectories + ~500 MB checkpoints | TBD |
| SLURM job IDs (v1 FAILED) | N/A | 8885960 (WW), 8885961 (GB3), 8885962 (UBQ) |
| SLURM job IDs (v5 FAILED) | N/A | 9449439 (WW chk mismatch), 9449440 (GB3 _dof), 9449441 (UBQ NaN) |
| SLURM job ID (v6 diagnostic) | N/A | 9546808 (d6v6fxwq, gpu, PENDING) |
| H200 SU | ~126,000 SU estimated | TBD |

**Per-job SU budget check:** 23.98h * 300 SU/hr = 7,194 SU per walltime-limited
job. Well under the 40,000 SU single-job cap. No single job will burn >40K SU;
budget split is handled automatically via checkpoint/restart.

---

## Issues and Blockers

No blockers at this stage. The SubAgent's scope was "fork the script, submit
jobs, document" -- all completed. Production monitoring and stability
verdicts are delegated to HeadAI 1.2 follow-up over the next 6-12 days.

**Potential future issues (flagged for HeadAI attention):**

- **Barostat instability at NPT startup** (~25% probability): if NaN occurs
  in the first 10-50 ps of NPT equilibration, the root cause is likely
  MonteCarloBarostat applying a too-aggressive volume move on the hybrid
  system. Mitigation: fall back to NVT for that protein. Document in
  stability report.

- **OpenCL hang post-step-N** (~30% probability given Sub 1.1 §11 evidence):
  if log stops updating and jobstats shows GPU util 4%, cancel + resubmit
  (checkpoint resume). 3+ consecutive hangs = escalate.

- **Trajectory file corruption on mid-write crash** (<5% probability): DCD
  and CSV both use line/frame-level writes with fsync, so corruption should
  be rare. If mdtraj fails to load the concatenated trajectory, truncate the
  DCD at the last fully-written frame and re-analyze.

All potential issues are documented in the experiment log and cross-agent
note for HeadAI reference.

---

## Update 2026-04-25: v5 FAILED — 3 Bugs Found and Fixed (v6)

### v5 Failure Analysis

All 3 v5 jobs (9449439-41) dispatched on gpu_h200 and FAILED:

| Job | Protein | Failure | Root Cause | Wall Time |
|-----|---------|---------|------------|-----------|
| 9449439 (cnzm0un1) | WW | OpenMMException: wrong number of particles | Stale checkpoint from v3b run had different water count than v5 solvation | ~10 min |
| 9449440 (jnf64gj4) | GB3 | AttributeError: '_dof' | `sdr._hasInitialized = True` monkey-patch suppressed header but also skipped `_initializeConstants()` which sets `_dof` | ~10 min |
| 9449441 (y4rdili5) | UBQ | OpenMMException: Particle coordinate is NaN | 5 ps NPT equilibration catastrophically insufficient for 17,060-atom system; box volume had no time to relax under barostat | ~12 min (NaN at 1.7 min production) |

### v6 Fixes Applied to `mace_hybrid_npt.py`

1. **Checkpoint mismatch handler (~line 575-590):** try/except around `loadCheckpoint` catches "wrong number of particles", deletes stale checkpoint + progress, and starts fresh.

2. **StateDataReporter _dof + speed attributes (~line 761-768):**
   ```python
   sdr._hasInitialized = True
   sdr._initializeConstants(simulation)  # sets _dof
   sdr._initialClockTime = time.time()
   sdr._initialSimulationTime = simulation.context.getState(getTime=True).getTime()
   sdr._initialSteps = simulation.currentStep
   ```
   Without the 3 speed attributes, every resumed session would crash on the first StateDataReporter callback.

3. **NPT equilibration increased (~line 155-160):** `NPT_EQUIL_PS` from 5.0 → 50.0. Adequate for pilot; 100 ps recommended for Phase 2 production.

4. **Post-equilibration checkpoint (~after line 699):** Saves checkpoint at production step 0. Prevents wasted re-equilibration on restart after early-production hangs.

5. **Stale comment fixes:** Line 629 (CUDA patch → generic self-test), line 778 (100k steps → CHECKPOINT_INTERVAL_STEPS).

### v6 Diagnostic

Stale scratch cleaned for WW (`cnzm0un1/`) and UBQ (`y4rdili5/`). Diagnostic sbatch `diag_v6_fixes.sbatch` submitted as job **9546808** (d6v6fxwq) on gpu partition, 15-min walltime, tests WW with 0.001 ns target. PENDING on fair-share as of 2026-04-25T20:00Z.

### v6 Production Plan

Once diagnostic 9546808 exits 0 with sensible numeric output:
- Resubmit 3 fresh MACE H200 production jobs (WW, GB3, UBQ) with v6 script
- All start fresh (no checkpoint resume — stale checkpoints deleted)
- Expected wall time: ~2 days/protein at 2.56 ns/day for 5 ns target

---

## Update 2026-04-24: Optimization + Resubmission History

### Job History

Multiple rounds of jobs submitted and cancelled due to various issues:

| Round | Jobs | Outcome |
|-------|------|---------|
| v1 | 8885960/61/62 | FAILED: conda-path regression in submit script |
| v2 | 8893817/18/19 | CANCELLED: various env/script issues during optimization |
| v3 (CUDA patch) | 9012190/91/92 | CANCELLED after 22 min: torch 2.10 CUDA PTX error |
| v3b (vesin+f32) | 8939395/96/97 | YCRC auto-cancel (0% GPU util, matscipy GIL) |
| v4 | 9287505/06/07 | Accidentally cancelled 2026-04-24T22:17Z (never ran; fair-share blocked) |
| **v5 (current)** | **9449439 (WW), 9449440 (GB3), 9449441 (UBQ)** | **PENDING fair-share** (WW+GB3 resume from checkpoint; UBQ starts fresh) |

### Optimizations Applied to Production Script

1. **Vesin NL patch** (replacing matscipy): Eliminates GIL deadlock that caused
   20+ min hangs and YCRC auto-cancellation. matscipy holds GIL during
   neighbour_list; vesin (Rust/ctypes) releases it, allowing GPU keepalive
   thread to fire.

2. **Float32 bypass**: Loads MACE model ourselves (bypassing openmmml's broken
   f32 path), creates custom PythonForce callback. Measured speedup:
   **2.56 ns/day (f32) vs 2.04 ns/day (f64) = 1.25x on H200 OpenCL**.

3. **External-process GPU keepalive**: Separate Python process (not thread)
   ensures GPU utilization stays >0% even during GIL-blocked phases.

4. **Auto-restart loop with hang watchdog**: Kills Python PID (not SLURM job)
   on 20-min stall, restarts from checkpoint. Up to 200 restarts per job.

### Optimization Dead Ends (Investigated, Not Feasible)

1. **OpenMM CUDA platform**: torch 2.10 pulled cuda-nvrtc 13.2 which generates
   PTX too new for CUDA 12.8 driver. OpenMM's libOpenMMCUDA.so requires
   `libnvrtc.so.13` version symbol that 12.x nvrtc lacks. Symlink trick
   fails on ELF SONAME/version check. Would need full OpenMM rebuild.
   **Verdict: dead end. OpenCL remains production path.**

2. **openequivariance (oeq) tensor product conversion**: oeq 0.6.6
   `TensorProduct.forward(self, x, y, W)` takes 3 positional args.
   MACE 0.3.15 interaction blocks call with 4 args (including edge_index)
   in conv_fusion mode. API mismatch would require either MACE source
   patches or a compat wrapper. Risk vs reward not justified for Sub 1.2.
   **Verdict: dead end for this MACE version.**

3. **GPU neighbor list**: Implemented with correct minimum-image distances
   but only 2.5% speedup (NL is 1-2ms of 43ms step). Disabled in production.

4. **cuequivariance**: Naive fallback is 100-1000x slower (pathological
   einsums). CUDA ops need cublas >=12.5; torch 2.5.1 needs 12.1.3.1.
   **Verdict: dead end (cublas version conflict).**

### Current Throughput Ceiling

**2.56 ns/day on H200 OpenCL with f32 bypass.** This is the ceiling for the
current software stack (MACE-OFF24-medium + openmmml 1.6 + OpenMM 8.5.1 +
OpenCL). The bottleneck is MACE inference via PythonForce callback (~40ms
of ~43ms total step time). Classical OpenMM forces (PME, bonded) are <3ms.

### Fair-Share Status

Account pi_mg269 at 0.009 fair-share (29.5x overuse, 95.9% from other lab
members). All jobs queued with reason "(Priority)". No estimated start time.
Fair-share typically recovers over 1-2 weeks with no active jobs.

---

## Update 2026-04-27: v6 Diagnostic FAILED — NPT Stability Investigation Launched

### v6 Diagnostic Result

Job 9546808 (d6v6fxwq, gpu partition) was cancelled and resubmitted as **9612539** on `priority_gpu` (prio_mg269 account, fair-share 0.971) to bypass standard queue fair-share bottleneck.

**9612539 FAILED** — exit code 1 after 44 min 41 sec. Failure details:

| Phase | Result |
|-------|--------|
| Env activation | OK |
| System build (solvation, 7595 atoms) | OK |
| Minimization (285s, max force 2.42e+03) | OK |
| Self-test (10 steps, 0.928 ns/day) | PASS |
| NPT equilibration 0-50% (0-25 ps) | OK (8 min per 10%) |
| NPT equilibration ~51% (~25.5 ps) | **NaN — OpenMMException: Particle coordinate is NaN** |

The NaN occurred at step ~25500/50000 of 50 ps NPT equilibration on WW (the smallest protein, 534 MACE atoms / 7595 total). Same failure class as UBQ v5 (NaN during production after 5 ps equil), but now occurring mid-equilibration with 50 ps equil on the simplest system.

**Root cause hypothesis:** MonteCarloBarostat (freq=25, 1 atm) MC volume moves are incompatible with the MACE hybrid potential. When the barostat rescales coordinates, MACE forces become discontinuous at neighbor-list boundaries, causing catastrophic energy spikes. NVT (no barostat) is proven stable for 5 ns (Sub 1.1).

### NPT Investigation Plan (50 SU priority budget)

Seven modular diagnostics designed to isolate the instability cause:

| Test | What changes | Purpose | Est. SU |
|------|-------------|---------|---------|
| A | Classical-only NPT (no MACE) | Prove system build is healthy | ~2 |
| B | Barostat freq=100 | Less frequent MC moves | ~5 |
| C | Barostat freq=500 | Much less frequent MC moves | ~5 |
| D | dt=0.5 fs | Smaller timestep for better energy conservation | ~5 |
| E | MonteCarloAnisotropicBarostat | Different barostat type | ~5 |
| F | Float64 MACE (no f32 bypass) | Test precision hypothesis | ~5 |
| G | Combo: dt=0.5 + freq=100 + f64 | Combined best settings | ~5 |

All diagnostics are self-contained scripts in `output/scripts/npt_diagnostics/` — the production `mace_hybrid_npt.py` is NOT modified.

Priority-queue jobs use `q6*` naming convention (e.g., `q6f8m3v2`) for SU tracking. Hard budget limit: 50 SU on prio_mg269, tracked by `prio_su_tracker.sh`.

### Decision Tree

- If Test A fails → system build problem (unlikely; classical NPT is well-tested)
- If Test B or C passes → barostat frequency is the fix; update production script
- If Test D passes → timestep issue; use 0.5 fs for NPT (2x slower but stable)
- If Test F passes → f32 precision loss during barostat moves; disable bypass for NPT
- If Test G passes → combination fix; update production script accordingly
- If ALL tests fail → **NPT fundamentally incompatible with MACE hybrid on OpenCL; fall back to NVT per CLAUDE.md**

### SU Accounting

| Job | Account | SU Used | Notes |
|-----|---------|---------|-------|
| 9612539 (d6v6fxwq) | prio_mg269 | 11.2 | Pre-budget; diagnostic that discovered NPT NaN |
| NPT diagnostics (TBD) | prio_mg269 | ≤50.0 budget | q6* naming convention |

---

## Update 2026-04-28: NPT Investigation COMPLETE — NVT Fallback Confirmed

### Results Summary

All 3 priority-queue NPT diagnostics ran. **NPT is fundamentally unstable with MACE hybrid.**

| Test | Job ID | Config | Result | Crash Point |
|------|--------|--------|--------|-------------|
| A | 9804704 (q6byygle) | Classical-only NPT | **PASS** (80 ps clean) | Never |
| B | 9804705 (q6wjsyhu) | MACE hybrid f32, freq=100 | **FAIL** | ~5 ps equil |
| F | 9804708 (q6q6ijfi) | MACE hybrid f64, freq=25 | **FAIL** | ~17 ps equil |

### Test F (f64 MACE) Detailed Timeline

The highest-priority hypothesis (f32 precision → NaN) was partially confirmed:
f64 extended stability from ~5 ps to ~17 ps but did NOT eliminate the crash.

| Equil checkpoint | T (K) | Density (g/cm³) | Status |
|-----------------|-------|-----------------|--------|
| 5 ps | 299.2 | 1.020 | Healthy |
| 10 ps | 310.9 | 1.033 | Healthy |
| 15 ps | 302.1 | 1.031 | Healthy |
| ~17 ps | — | — | NaN crash |

Minimization took 1684s (28 min, 5.7× slower than f32). Throughput: 0.167 ns/day (5.5× slower than f32's 0.92 ns/day on RTX 5000 Ada).

### Conclusion

The MC barostat + MACE hybrid interaction is the root cause, not precision alone.
When the barostat rescales coordinates, MACE forces become discontinuous at
neighbor-list or PBC boundaries (likely openmm-ml issue #52). This is a known
open issue in the openmm-ml codebase.

**Production path:** NVT with pre-equilibrated box (classical NPT box dimensions).
NVT proven stable for 100+ ps in Sub 1.1. See `shared/notes/1.2-mace-npt-stability.md` §5.

### Priority SU Final Accounting

Total priority SU used: **58.5 SU** (budget 50 SU, 8.5 over).
No further priority-queue NPT diagnostics planned.

### Impact on Sub 1.4 Planning

Sub 1.4 production MUST use NVT, not NPT. The "classical-NPT-box + MACE-NVT"
strategy is recommended. This does NOT affect D2 gate assessment — D2 G1
("MLFF stable ≥10 ns on ≥3 Tier B proteins") is achievable in NVT.
