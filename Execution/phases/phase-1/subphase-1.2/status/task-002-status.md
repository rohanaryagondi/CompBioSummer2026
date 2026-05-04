---
task_id: "task-002"
agent: "mlff-so3lr-pilot"
subphase: "1.2"
status: complete
date: 2026-04-20
---

# Status Report: Task 002 — SO3LR vacuum NVT 5 ns × 5 Tier A/B proteins

## Summary

Initial submission at 2026-04-19T04:06:51Z FAILED within 6-8 s per job
(5/5 jobs, exit 139, segfault after the SO3LR CLI subprocess returned
exit 1 from `ModuleNotFoundError: No module named 'typing_extensions'`).
Root cause: `PYTHONNOUSERSITE=1` in `so3lr_pilot.sbatch` hid the only
installed `typing_extensions` copy (in user-site). The env-so3lr package
tree (flax → so3lr → mlff) relies on several user-site-provided transitive
dependencies (typing_extensions, pandas, rich, pyyaml, dateutil, ...);
they were never bundled into env-so3lr. The Sub 1.1 working SO3LR scripts
(`so3lr_crambin_v5.sbatch`, `so3lr_crambin_cli.sbatch`) explicitly used
`PYTHONNOUSERSITE=0` and prepended user-site to `PYTHONPATH` — that
pattern was not inherited by the Sub 1.2 template (a blanket MACE-style
PYTHONNOUSERSITE=1 was applied by mistake).

**Remediation (2026-04-19, ~05:09 UTC):**
- Fixed `output/scripts/so3lr_pilot.sbatch` to set `PYTHONNOUSERSITE=0`
  and prepend user-site to `PYTHONPATH` AFTER env site-packages. This
  keeps env-first precedence (numpy 2.4.4 still loads from env-so3lr —
  verified) while allowing user-site fallback for truly missing deps.
- env-so3lr was NOT modified (no `pip install` into the env). Clone
  was unnecessary because the regression is not in the env, it is in
  the sbatch script.
- Renamed `slurm-888609[1-5].{err,out}` to `...failed` for audit.
- Generated 5 fresh cryptic 8-char names and resubmitted all 5 jobs.

**New job IDs (PENDING on `gpu` partition, RTX 5000 Ada):**
8890874 (ww, 932e3sz8), 8890875 (gb3, pr32hg7t), 8890876 (gb1, ixgkbzna),
8890877 (ntl9, ubi1w71f), 8890878 (ubq, g6m5vkof).

All code, XYZ inputs, SLURM template, and submit wrapper are committed.
Trajectories will complete in ~1–2 days; analysis (stability report +
cross-agent note) will be populated when the HeadAI re-invokes this
agent.

---

## What Was Done

1. **Parameterized the Sub 1.1 SO3LR runner.** Wrote
   `output/scripts/so3lr_pilot_runner.py` with `--protein {ww,gb3,gb1,ntl9,ubq}`
   arg, invoking the `so3lr nvt` CLI via subprocess (Sub 1.1 lesson:
   use CLI, not custom JAX-MD). Modes: `prepare-only`, `run`, `restart`.
   Includes GPU keepalive thread (5-min cadence) per operational-practices.
   5 ns target = `--md-cycles 10000 --md-steps 1000 --dt 0.5`.

2. **Wrote the preparation script.** Separately,
   `output/scripts/so3lr_prep_proteins.py` runs inside env-mace (which has
   pdbfixer + openmm; env-so3lr does NOT). This converts the cleaned PDBs
   to hydrogenated XYZ for SO3LR input. env-so3lr SLURM jobs only run MD.
   Executed successfully for all 5 proteins:
   - WW (Pin1 6-39):    275 heavy + 259 H =  534 atoms
   - GB3 (1P7E):        437 heavy + 425 H =  862 atoms
   - GB1 (2QMT):        438 heavy + 420 H =  858 atoms
   - NTL9 (2HBB):       391 heavy + 422 H =  813 atoms
   - UBQ (1UBQ):        602 heavy + 629 H = 1231 atoms

3. **Wrote the SLURM template.** `output/scripts/so3lr_pilot.sbatch` targets
   `--partition=gpu` (RTX 5000 Ada), `--gres=gpu:1`, `--cpus-per-task=2`,
   `--mem=16G`, `--time=1-00:00:00`, `--account=pi_mg269`. Initially set
   `PYTHONNOUSERSITE=1` (a mistaken inheritance from the MACE pattern); on
   2026-04-19 post-failure, this was corrected to `PYTHONNOUSERSITE=0` with
   user-site appended to `PYTHONPATH` AFTER env site-packages, matching the
   Sub 1.1 working SO3LR pattern (`so3lr_crambin_v5.sbatch`,
   `so3lr_crambin_cli.sbatch`). Accepts `PROTEIN`, `MODE`, `TARGET_NS` via
   `--export`.

4. **Wrote the submit wrapper.** `output/scripts/submit_so3lr_pilot.sh` loops
   over {ww, gb3, gb1, ntl9, ubq} and submits each with an opaque 8-char
   cryptic job name (per operational-practices / user feedback). Records
   submissions to `output/trajectories/so3lr_vacuum/submitted_jobs.tsv`.

5. **Submitted all 5 jobs at 2026-04-19T04:06:51Z.** Job IDs and cryptic names
   recorded. All 5 FAILED within 6-8 s each (exit 139), `typing_extensions`
   missing under `PYTHONNOUSERSITE=1`. See remediation below.

6. **(Remediation 2026-04-19 ~05:09 UTC) Resubmitted all 5 jobs after
   env-var fix.** Before resubmission:
   - Confirmed import works in env-so3lr when `PYTHONNOUSERSITE=0` (tf
     warnings only; `from so3lr import So3lrCalculator` returns OK).
   - Confirmed numpy still loads from env (2.4.4 at
     `/home/rag88/.conda/envs/env-so3lr/...`), NOT user-site, because env
     site-packages is prepended first on PYTHONPATH.
   - Edited `output/scripts/so3lr_pilot.sbatch` (env-var block + header
     comment) to follow Sub 1.1 working pattern.
   - Edited `output/scripts/submit_so3lr_pilot.sh` CRYPTIC_NAMES map with
     5 fresh 8-char alphanumeric names and a comment noting prior failed
     set.
   - Renamed old failed logs `slurm-8886091..5.{err,out}` → `...failed`
     for audit retention (not deleted).
   - Resubmitted via `./output/scripts/submit_so3lr_pilot.sh`. All 5 new
     jobs queued PENDING on `gpu`.

---

## Artifacts Produced

| Artifact | Path | Description | Verified |
|----------|------|-------------|----------|
| Runner script | `output/scripts/so3lr_pilot_runner.py` | Parameterized SO3LR CLI invoker with --protein arg | yes (--help works, subprocess template verified) |
| Prep script | `output/scripts/so3lr_prep_proteins.py` | PDBFixer hydrogenation → XYZ (env-mace) | yes (executed for all 5) |
| SLURM template | `output/scripts/so3lr_pilot.sbatch` | 1 job = 1 protein, RTX 5000 Ada, 24 h | yes (chmod +x, submit succeeded) |
| Submit wrapper | `output/scripts/submit_so3lr_pilot.sh` | Submits all 5 with cryptic names | yes (5 jobs queued) |
| WW XYZ | `output/trajectories/so3lr_vacuum/ww/input.xyz` | 534 atoms, Pin1 6–39 | yes (ASE read OK) |
| GB3 XYZ | `output/trajectories/so3lr_vacuum/gb3/input.xyz` | 862 atoms | yes |
| GB1 XYZ | `output/trajectories/so3lr_vacuum/gb1/input.xyz` | 858 atoms | yes |
| NTL9 XYZ | `output/trajectories/so3lr_vacuum/ntl9/input.xyz` | 813 atoms | yes |
| UBQ XYZ | `output/trajectories/so3lr_vacuum/ubq/input.xyz` | 1231 atoms | yes |
| Per-protein H-PDB (audit) | `output/trajectories/so3lr_vacuum/<p>/input_h.pdb` | Hydrogenated PDB | yes |
| Per-protein prep summary | `output/trajectories/so3lr_vacuum/<p>/prep_summary.json` | JSON with atom counts | yes |
| Top-level prep summary | `output/trajectories/so3lr_vacuum/prep_all_summary.json` | All 5 protein prep stats | yes |
| Submission log | `output/trajectories/so3lr_vacuum/submitted_jobs.tsv` | TSV of all 5 job IDs | yes (5 rows) |
| Experiment log | `output/task-002-experiment.md` | Full experiment parameters | yes |
| Status report | `status/task-002-status.md` | This file | yes |
| Cross-agent note | `../../../shared/notes/1.2-so3lr-pilot-stability.md` | Preliminary submit note | yes |

---

## Success Criteria Evaluation

| # | Criterion | Met? | Evidence |
|---|-----------|------|----------|
| 1 | `so3lr_pilot_runner.py` exists with `--protein` arg | yes | `--help` output shows choices={ww,gb3,gb1,ntl9,ubq}; file at `output/scripts/` |
| 2 | WW vacuum trajectory ≥4.5 ns, stable, no NaN | **FAIL** | Job 8890874 → 8903311. Ran 5 ns (6.9h wall) but NaN at 0.704 ns with structure intact (Rg stable ~9.0 Å). Only 0.65 ns usable post-equil. Below T_min (1 ns). |
| 3 | GB3 vacuum trajectory ≥4.5 ns, stable, no NaN | **FAIL** | Job 8890875. Ran 5 ns (11.85h wall), exit 0, clean logs. **SILENT STRUCTURAL EXPLOSION**: Rg grew 10.55→989.87 Å (ratio 93.8×) starting ~100 ps. T/E logs showed no anomaly — deceptive. Zero usable data. |
| 4 | GB1 vacuum trajectory ≥4.5 ns, stable, no NaN | **PASS** | Job 8890876 (11.89h wall). 4.95 ns clean post-equil. Rg 10.07–10.63 Å (ratio 0.978). T = 300.0 ± 8.3 K. No NaN. Fully usable. |
| 5 | NTL9 vacuum trajectory ≥4.5 ns, stable, no NaN | **FAIL** | Job 8890877 (11.18h wall). Structural explosion from ~100 ps (Rg > 2× initial by 125 ps). NaN appeared downstream at 4.386 ns. T log normal until NaN. Zero usable data. |
| 6 | UBQ vacuum trajectory ≥4.5 ns, stable, no NaN | **PASS** | Job 8890878 (16.18h wall). 4.95 ns clean post-equil. Rg 10.92–11.14 Å (ratio 0.987). T = 300.1 ± 7.0 K. Tightest stats of all 5. Fully usable. |
| 7 | Per-protein stability report at `output/so3lr_vacuum_stability_report.md` | **yes** | Written 2026-04-25. 205 lines. 2/5 PASS (GB1, UBQ). Two failure modes: numerical NaN (WW) and silent structural explosion (GB3, NTL9). |
| 8 | Cross-agent note `1.2-so3lr-pilot-stability.md` written | **yes** | Updated with §3 structural analysis + quantitative Rg/T/E data. CRITICAL finding: SO3LR exit 0 + clean energy logs do NOT guarantee structural stability — HDF5 Rg check mandatory. |
| 9 | All SLURM job names are 8-char cryptic alphanumeric | yes | v1 (FAILED): p3v8xt7r, k9m2qw5n, j7r4nb6x, z5k8fp2q, h4w9rn3m. v2 (PENDING): 932e3sz8, pr32hg7t, ixgkbzna, ubi1w71f, g6m5vkof |
| 10 | Status report written to `status/task-002-status.md` | yes | This file (status=slurm-resubmitted) |

---

## Remediation: typing_extensions env-var fix (2026-04-19 ~05:09 UTC)

### Failure signature (5/5 jobs)

All 5 initial jobs (8886091–8886095) died in 6-8 s with exit 139. Per
`slurm-8886091.err.failed`:
```
ModuleNotFoundError: No module named 'typing_extensions'
  File ".../flax/struct.py", line 23, in <module>
    from typing_extensions import (
Segmentation fault (core dumped) python "${RUNNER}" --protein ww --mode run ...
```
The keepalive thread and the runner itself started fine. The segfault
occurred inside the `so3lr nvt` CLI subprocess (which returned exit 1
first due to the import error; the parent's `python "${RUNNER}"` then
segfaulted — a known cpython-on-subprocess-cleanup pattern).

### Diagnosis

1. Confirmed `typing_extensions` is NOT installed in env-so3lr:
   `ls /home/rag88/.conda/envs/env-so3lr/lib/python3.12/site-packages/`
   shows only `jaxtyping`, no `typing_extensions`.
2. Confirmed it IS in user-site (`/home/rag88/.local/lib/python3.12/
   site-packages/typing_extensions.py`, version 4.15.0).
3. Reproduced the failure: with `PYTHONNOUSERSITE=1`,
   `python -c "import typing_extensions"` fails with ModuleNotFoundError.
   Without it, imports succeed.
4. Confirmed deeper: when user-site is hidden, subsequent imports also
   fail (rich, pandas, pyyaml, dateutil). env-so3lr structurally depends
   on user-site for common Python deps that were never pinned into the
   env during its Sub 0.1 build.
5. Found Sub 1.1 working reference: `phases/phase-1/subphase-1.1/output/
   scripts/so3lr_crambin_v5.sbatch` uses
   `export PYTHONPATH="/home/rag88/.local/lib/python3.12/site-packages:${PYTHONPATH}"`
   and does NOT set PYTHONNOUSERSITE=1. That script is the 2026-04-16
   D1-PASS path.

### Decision: env-var fix in sbatch script (NOT env modification)

Per operational-practices, the non-destructive options were:
- **(A)** Clone env-so3lr → env-so3lr-v2 and install missing deps into
  the clone. Cost: 5.8 GB copy, 15 min install, risk of version skew vs
  user-site that Sub 1.1 was tested against.
- **(B)** `pip install` missing deps into env-so3lr in place.
  Cost: adds packages whose versions may differ from user-site, changing
  the effective runtime vs Sub 1.1 baseline.
- **(C) [chosen]** Leave env-so3lr alone; fix the sbatch to allow
  user-site (`PYTHONNOUSERSITE=0`) and prepend env site-packages to
  PYTHONPATH so env-resident packages (numpy 2.4.4, jax, so3lr, mlff)
  still win precedence over user-site. This exactly matches the Sub 1.1
  working pattern and is the minimum possible change.

Verified (C) works on the login node (non-GPU) before submitting:
```
$ PYTHONNOUSERSITE=0 PYTHONPATH="$ENV_SP:$USER_SP:..." \
    python -c "from so3lr import So3lrCalculator; print('OK')"
OK - So3lrCalculator imported
$ python -c "import numpy; print(numpy.__file__)"
numpy: 2.4.4 /home/rag88/.conda/envs/env-so3lr/lib/python3.12/site-packages/numpy/__init__.py
```

### Changes made

- `output/scripts/so3lr_pilot.sbatch`:
  - Header comment block: updated to explain env-so3lr's user-site
    contract (opposite of env-mace's PYTHONNOUSERSITE=1 contract).
  - Env-setup block: `PYTHONNOUSERSITE=1` → `PYTHONNOUSERSITE=0`;
    PYTHONPATH now = `${CONDA_PREFIX}/lib/python3.12/site-packages:/home/rag88/.local/lib/python3.12/site-packages:${PYTHONPATH:-}`.
- `output/scripts/submit_so3lr_pilot.sh`:
  - Updated `CRYPTIC_NAMES` map with 5 fresh names
    (932e3sz8, pr32hg7t, ixgkbzna, ubi1w71f, g6m5vkof) and added a
    comment recording the prior v1 FAILED names for audit.
- Failed logs retained: `output/trajectories/so3lr_vacuum/<p>/
  slurm-8886091..5.{err,out}.failed`.
- Cross-agent notes:
  - Updated `shared/notes/1.2-so3lr-pilot-stability.md` with an
    "Env Remediation 2026-04-19" section and bumped urgency info → important.
  - Added `shared/notes/1.2-env-so3lr-typing-extensions-fix.md`
    documenting root cause, decision, fix, verification for future
    reference.

### Resubmission log

```
2026-04-19T05:09:19Z	ww	8890874	932e3sz8	run	5.0
2026-04-19T05:09:19Z	gb3	8890875	pr32hg7t	run	5.0
2026-04-19T05:09:19Z	gb1	8890876	ixgkbzna	run	5.0
2026-04-19T05:09:19Z	ntl9	8890877	ubi1w71f	run	5.0
2026-04-19T05:09:19Z	ubq	8890878	g6m5vkof	run	5.0
```

All 5 confirmed PENDING via `sacct -j 8890874..8890878 --format=JobID,JobName,State,Partition`.

---

## Unexpected Findings

1. **env-so3lr does NOT include pdbfixer/openmm.** Sub 1.1 crambin was
   already hydrogenated in a separate env before being handed to SO3LR. The
   same two-env pattern applies here: prep in env-mace (pdbfixer+openmm),
   MD in env-so3lr. No change to env-so3lr required; the runner and SLURM
   script correctly isolate the envs.

2. **Python version is 3.12 in env-so3lr (not 3.11 as task spec assumed).**
   The task spec line
   `export PYTHONPATH="$CONDA_PREFIX/lib/python3.11/site-packages:$PYTHONPATH"`
   needed to be updated to `python3.12`. Verified with
   `python --version` and checking actual site-packages location. The SLURM
   template uses the correct path.

3. **GB3 PDB (1P7E) already has hydrogens** (425 H out of 862 atoms =
   complete all-atom); other 4 PDBs are heavy-atom-only. pdbfixer adds H
   only where needed; GB3 XYZ output = same atom count as input (862).
   PDBFixer handled both cases uniformly.

4. **Runner uses subprocess to invoke the SO3LR CLI,** deliberately not the
   programmatic JAX-MD interface used in Sub 1.1's
   `so3lr_crambin_nvt.py`. Sub 1.1 Subagent A wasted ≥8 SLURM jobs with
   custom JAX-MD code that hit shape broadcasting bugs and NaN. The CLI
   handles neighbor lists, thermostat chain, JIT compilation, and
   checkpoints internally and was the D1-PASS path.

---

## What the Next Agent Needs to Know

**HeadAI re-invocation protocol:** Once all 5 SLURM jobs reach a terminal
state (COMPLETED, TIMEOUT, or FAILED), re-invoke this agent for stability
analysis. The analysis step:

1. For each protein, parse `output/trajectories/so3lr_vacuum/<p>/stageA.log`
   (SO3LR CLI log; columns include step, time, T, KE, PE, total energy).
2. Compute stability metrics: T mean ± std, Hamiltonian drift (meV/ps),
   PE drift (eV over last 1 ns), NaN check, trajectory length achieved.
3. For each protein, load the HDF5 trajectory and compute Cα RMSD vs the
   initial frame. Vacuum RMSD is allowed to be larger than solvated (target
   ≤ 7 Å).
4. Write `output/so3lr_vacuum_stability_report.md` with a table of the 5
   proteins (trajectory length, T, Hamiltonian drift, Cα RMSD, pass verdict).
5. Update `shared/notes/1.2-so3lr-pilot-stability.md` with actual stability
   results (currently the note only documents submission; needs the
   post-run summary for D2 G1 evidence).

**If a job TIMEOUTS** (24 h SLURM wall not enough for 5 ns — possible for
UBQ): resubmit with `MODE=restart`:
```bash
cd /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2
./output/scripts/submit_so3lr_pilot.sh --mode restart ubq
```

**If a job FAILS** (NaN in relaxation or early dynamics): check
`slurm-<jid>.err` for the JAX/SO3LR traceback. The runner propagates the
CLI exit code so SLURM sees non-zero. Failure modes to look for:
- `NaN in positions`: geometry too close to clashes. Try increasing
  `--force-conv` strictness (0.01 eV/Å) or float64. This is the Sub 1.1
  fallback ladder.
- `ModuleNotFoundError: typing_extensions` (or rich / pandas / pyyaml):
  env-so3lr user-site contract broken. Confirm `so3lr_pilot.sbatch` has
  `PYTHONNOUSERSITE=0` and `/home/rag88/.local/lib/python3.12/
  site-packages` is on PYTHONPATH (see remediation section above).
- `ModuleNotFoundError: numpy` or numpy loaded from user-site: env
  precedence broken. Verify env's site-packages is FIRST on PYTHONPATH
  (before user-site). `PYTHONNOUSERSITE=0` is correct for SO3LR —
  do NOT flip it back to 1.

**Restart already handles partial progress:** the runner auto-finds
`stage*_checkpoint.npz` and passes `--restart-load` so the continuation
picks up from the last checkpoint. Stage naming increments (A → B → C).

---

## Resource Usage

| Resource | Estimated | Actual |
|----------|-----------|--------|
| GPU-hours | ~55 (sum across 5 jobs, spread 6.6–15.6 h each) | ~58 (WW 6.9 + GB3 11.85 + GB1 11.89 + NTL9 11.18 + UBQ 16.18) |
| Wall time | 1–2 days (parallel) | ~16.2h wall (parallel; limited by UBQ) |
| Storage | < 10 GB total (XYZ frames + NPZ checkpoints per protein) | ~820 MB total HDF5 (WW 16.7 + GB3 189.5 + GB1 188.6 + NTL9 156.8 + UBQ 268.9 MB) |
| SLURM job IDs (v1 FAILED) | N/A | 8886091 (ww), 8886092 (gb3), 8886093 (gb1), 8886094 (ntl9), 8886095 (ubq) — typing_extensions failure |
| SLURM job IDs (v2 PRODUCTION) | N/A | 8890874 (ww→NODE_FAIL), 8890875 (gb3), 8890876 (gb1), 8890877 (ntl9), 8890878 (ubq). WW resubmitted as 8903311. |
| SU (compute accounting) | ~55 × 15 SU/hr ≈ 825 SU | ~58 × 15 = ~870 SU |

---

## Issues and Blockers

None at submission. Jobs queued normally. If any of the following arise, a
help-needed doc will be filed:

- **All 5 jobs fail (NaN in relax):** sub-1.2-so3lr-pilot-relax-failure.md
- **Python/numpy import error:** sub-1.2-so3lr-pilot-env.md
- **Queue wait >24 h with no starts:** sub-1.2-so3lr-pilot-queue.md
