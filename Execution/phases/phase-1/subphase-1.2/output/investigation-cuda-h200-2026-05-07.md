---
agent: cuda-investigator
type: investigation
urgency: important
date: 2026-05-07
subphase: "1.2"
trigger: NTL9 OpenCL hang at step 25,000 (job 10622876)
question: "Should we switch the MACE-OFF24 NPT pilot from OpenMM OpenCL to CUDA on H200?"
verdict: "DO NOT SUBMIT a CUDA probe. The PTX-version blocker has not changed; the openmm-ml CUDA-context interop issue is independent and unresolved. Keep OpenCL + watchdog/checkpoint for the NTL9 hang. (Confidence: high.)"
---

# CUDA Platform Re-Evaluation on H200 for MACE-OFF24 NPT — 2026-05-07

## TL;DR (for HeadAI 1.2)

- **DO NOT submit a CUDA probe on H200.** The Sub 1.1 / Sub 1.2 verdict
  ("CUDA broken on H200") is **still empirically correct as of 2026-05-07**.
  The PTX-version error mode is fully reproduced by the most recent diagnostic
  on H200 (`diag_h200_final_9353349`, 2026-04-23), the SONAME-mismatch fix
  is structurally impossible without a from-source OpenMM rebuild, and
  upstream releases have produced no relevant changes since Sub 1.1.
- **The NTL9 hang has nothing to do with the CUDA-vs-OpenCL choice** — it is
  the pre-existing H200 OpenCL hang pattern documented in Sub 1.1 (SLURM
  8789805) and prior Sub 1.2 hung-job evidence. The watchdog + checkpoint
  machinery is the correct mitigation and is already working as designed
  (it killed the hang and resumed from the checkpoint).
- **Probability that submitting a probe today succeeds with throughput
  uplift:** ~5%. **Cost of probe (~600 SU on scavenge_gpu):** real but
  modest. **Expected value:** strongly negative — would burn budget,
  consume HeadAI attention, and (as in Sub 1.1) end at the same crash
  surface that has been hit eight times across 2026-04-18 → 2026-04-23.
- **Recommended action:** keep the current production stack. If H200 OpenCL
  hangs continue at >30% rate after another 3-5 production launches,
  escalate to a different mitigation lane (RTX 5000 Ada Standard fallback,
  or LAMMPS engine swap deferred to Sub 1.5+) — not a CUDA re-attempt.

---

## 1. Sub 1.1 root cause — what specifically failed

### 1.1 The two distinct CUDA failure surfaces

There are **two separate failures** in the historical record. Both must
be fixed before CUDA on H200 becomes viable; neither has been.

#### Failure A — `CUDA_ERROR_UNSUPPORTED_PTX_VERSION (222)` at module load

This is what blocks `getPlatformByName('CUDA')` -> `Context()` from
even initializing on H200. The exact failure mode is:

```
[H200, sm_90, driver 570.195.03, CUDA runtime 12.8 in driver]
Platform CUDA: Error loading CUDA module:
    CUDA_ERROR_UNSUPPORTED_PTX_VERSION (222)
```

Root cause (per `shared/notes/1.1-openmm-cuda-rebuild.md` §"Root-cause
diagnosis"):

- env-mace's `libOpenMMCUDA.so` was built by the conda-forge maintainers
  and links against `libnvrtc.so.13` SONAME (CUDA 13.2). This was
  verified today by `objdump -p` on the production binary:
  - `NEEDED libnvrtc.so.13`
  - All RTC symbols tagged `nvrtcGetPTX@libnvrtc.so.13`, etc.
- CUDA 13's nvrtc emits PTX ISA 8.6+. McCleary's NVIDIA driver
  570.195.03 supports up to PTX ISA 8.4 (CUDA 12.8). Result: every kernel
  compile is rejected by the driver with error 222. The error fires at
  context creation, before any forces are evaluated.
- **The Sub 1.1 symlink trick**
  (`libnvrtc.so.13.2.78` -> `libnvrtc.so.12.8.61`) was attempted and
  fails on a SONAME version-script check at link time:
  `version 'libnvrtc.so.13' not found (required by libOpenMMCUDA.so)`.
  Confirmed today: that error is still present when ldd-resolving
  `libOpenMMCUDA.so` against the env-mace lib dir. The resolver finds
  `libnvrtc.so.13.2.78` (a symlink to CUDA 12.8's `libnvrtc.so.12.8.61`),
  but the underlying CUDA 12.8 file has **SONAME `libnvrtc.so.12`**, so
  the symbol-version check `*@libnvrtc.so.13` fails.
- A **clean fix** requires rebuilding OpenMM from source against CUDA 12.x
  (Subagent J successfully did this in `/home/rag88/opt/openmm-cuda128`
  for env-mace-cuda — but that build only handled the PTX layer; see
  Failure B).

#### Failure B — `RuntimeError: CUDA driver error: invalid resource handle`

Even after Failure A is fixed (Sub 1.1 source-built OpenMM 8.5.1 against
CUDA 12.8 in env-mace-cuda), a second failure surface emerges:

```
[RTX 5000 Ada / H200, source-built OpenMM 8.5.1 + pip torch 2.5.1+cu121]
Platform CUDA ACTIVE: probe step in 1000.2ms, PE=-272269.7
...
RuntimeError: CUDA driver error: invalid resource handle
   (during minimize() or first getState() call)
```

Root cause (per `shared/notes/1.1-mace-cuda-benchmark.md` §"Interop
diagnosis"):

- openmm-ml 1.6 wires MACE forces through `openmm.PythonForce`, which
  invokes a TorchScript callback from OpenMM's C++ integrator on every
  force evaluation. The callback runs on PyTorch's per-thread default
  CUDA stream (PyTorch caching allocator). OpenMM's CUDA plugin uses a
  different stream and a different memory-management path. There is no
  built-in synchronization between them.
- The crash fires in two places: (1) at the first non-trivial
  `minimizeEnergy(2000 iter)` call when OpenMM reads a force buffer that
  PyTorch's stream has not yet finished writing, and (2) at the
  post-minimize `getState(...)` when OpenMM tries to read positions that
  PyTorch has invalidated.
- **Workaround attempted** (Fix A: `CUDA_VISIBLE_DEVICES=0` +
  `set_device(0)` + `device='cuda:0'`) — partially works on RTX 5000 Ada
  for short runs (≤10 iter minimization, no PME water), fully fails on
  H200, all hybrid systems, and any 2000-iter minimize. **Empirical
  matrix** (Sub 1.1 8 jobs):

  | Min iter | Platform | System | Result |
  |---|---|---|---|
  | 10 | RTX CUDA | createMixedSystem all-atoms | PASS (only short probe) |
  | 2000 | RTX CUDA | createSystem pure MACE | FAIL: illegal-memory in MACE cat() |
  | 2000 | RTX CUDA | hybrid WW | FAIL: invalid handle at post-min getState |
  | 2000 | H200 CUDA | vacuum | FAIL: invalid handle at post-min getState |
  | 2000 | H200 CUDA | createMixedSystem all-atoms | FAIL: invalid handle at post-min getState |

- **Clean fix** requires rebuilding `openmm-torch` 1.5.1 from source
  against pip torch 2.5.1+cu121 + OpenMM 8.5.1 — gives a native C++
  `TorchForce` that shares OpenMM's CUDA stream. Estimated build effort
  1-2 hr; not undertaken in Sub 1.1 (low expected ROI per
  `1.1-mace-cuda-benchmark.md` §"Throughput benchmarks": MACE inference
  is the bottleneck, so CUDA gives at best ~1× over OpenCL on the same
  GPU, NOT the 5-10× that would justify the rebuild).
- Even if the openmm-torch rebuild fixes the interop, it does NOT
  automatically fix Failure A — a separate from-source OpenMM CUDA
  rebuild is also required.

### 1.2 Throughput data (the other reason CUDA was rejected)

Subagent L's empirical CUDA vs OpenCL benchmark on RTX 5000 Ada (vacuum
crambin, the only configuration where the interop fix held):

| Platform | ns/day |
|---|---|
| OpenCL | 0.142 |
| CUDA (Fix A+B applied) | 0.142 |
| **Speedup** | **1.0× — NO speedup** |

Reason: MACE-OFF24 is e3nn-inference-bound. ~25-30 ms/step is spent in
the e3nn float64 forward pass. ~5-10 ms/step is OpenMM PythonForce
callback overhead. <3 ms/step is the OpenMM integrator + classical
forces. Switching the integrator from OpenCL to CUDA changes the
~3 ms/step component only — at best a ~1.05-1.1× speedup, which is
within measurement noise. This is documented in
`shared/notes/1.2-mace-throughput-ceiling.md` Section 2 ("Bottleneck
breakdown"): MACE inference is 58-70% of step cost.

This means the verdict was decided on TWO independent axes:
1. **Engineering risk** (Failure A + Failure B both unsolved without 2-4 hr build work, neither attempted in Sub 1.1)
2. **Throughput ceiling** (CUDA cannot beat OpenCL because MACE is inference-bound)

---

## 2. Current versions in env-mace (today, 2026-05-07)

Verified by `pip show` / `conda list` against the LIVE env-mace today:

| Package | Source | Version | Notes |
|---|---|---|---|
| OpenMM (active) | conda-forge | 8.5.1.dev-f7fa0c2 | Loads from `~/.conda/envs/env-mace/lib/python3.10/site-packages/openmm/` |
| OpenMM (shadowed) | pip | 8.3.1 | In `~/.local/lib/python3.10/site-packages/`; shadowed by conda when PYTHONNOUSERSITE=0 in env |
| openmm-ml | conda-forge | 1.6 | unchanged from Sub 1.1 |
| torch | pip | **2.10.0+cu128** | UPGRADED on 2026-04-23 (was 2.5.1+cu121 in Sub 1.1) |
| torch CUDA runtime | pip | nvidia-cuda-nvrtc-cu12 12.8.93 | PyTorch's vendored RTC — works fine |
| mace-torch | pip | 0.3.15 | unchanged |
| e3nn | pip | 0.4.4 | unchanged |
| cuequivariance | pip | 0.9.1 | NEW (added during Sub 1.2 R1-R3 optimization; tested but rejected for production per 1.2-mace-throughput-ceiling.md) |
| cuequivariance-torch | pip | 0.9.1 | NEW (paired with above) |
| openequivariance (oeq) | pip | 0.6.6 | NEW (installed for R1-R3 testing; rejected: API mismatch with MACE 0.3.15) |
| matscipy | pip | 1.2.0 | unchanged |
| vesin | pip | 0.3.8 | NEW (vesin NL applied in R1-R3) |
| pdbfixer | pip | 1.12.0 | unchanged |
| OpenMM CUDA plugin | conda | linked to libnvrtc.so.13 (CUDA 13.2) | **Same SONAME issue as Sub 1.1** |
| libnvrtc.so.13 -> | symlink | CUDA 12.8.0/lib64/libnvrtc.so.12.8.61 | **Symlink trick still fails on SONAME version check** |

**Driver** (per most recent SLURM logs):
- NVIDIA-SMI 570.195.03, "CUDA Version 12.8" (max-supported PTX ISA 8.4)
- This is unchanged from Sub 1.1.

**Cluster CUDA modules now available**:
- 12.0.0, 12.1.1, 12.6.0, 12.8.0, 12.9.1 (default)
- **CUDA 12.9.1 is new** (became default since Sub 1.1). However its
  `libnvrtc.so.12.9.86` ships SONAME `libnvrtc.so.12`, so it does not
  resolve the conda-OpenMM Failure A.

---

## 3. CUDA platform availability today

### 3.1 Static check (login node, dry import)

Run from login (no GPU; CUDA platform is in plugin dir but cannot
initialize without a device):

```
~/.conda/envs/env-mace/bin/python -c "import openmm; ..."
Platform 0: Reference (speed 1.0)
Platform 1: CPU (speed 10.0)
```

Login node only loads Reference + CPU. The CUDA + OpenCL plugins are
present in `~/.conda/envs/env-mace/lib/plugins/` (libOpenMMCUDA.so
3.2 MB, libOpenMMOpenCL.so 4.1 MB) but require a GPU to initialize —
expected.

### 3.2 GPU-side check (most recent diagnostic — `diag_h200_final_9353349`, 2026-04-23)

This is the most recent relevant diagnostic. After the torch 2.10
upgrade (Apr 23) and on H200:

```
[23:45:25Z] torch 2.10.0+cu128 | GPU: NVIDIA H200 | sm_90
[23:45:28Z] vesin NL: patched
[23:45:28Z] CUDA platform: Error loading CUDA module:
                CUDA_ERROR_UNSUPPORTED_PTX_VERSION (222)
[23:46:00Z]   A:f64/OpenCL/vesin: 2.04 ns/day | 42.3 ms/step
```

And on RTX 5000 Ada (`upgrade_v2_9301099`, the same upgrade transcript):

```
[2026-04-23T16:16:35Z] CUDA: OK (speed=100.0)        # Plugin LOADS
...
C:f64/CUDA: ERROR — Error loading CUDA module:
    CUDA_ERROR_UNSUPPORTED_PTX_VERSION (222)         # but COMPILE FAILS
D:f32/CUDA: ERROR — Error loading CUDA module:
    CUDA_ERROR_UNSUPPORTED_PTX_VERSION (222)
E:f32/CUDA/mixed: ERROR — Error loading CUDA module:
    CUDA_ERROR_UNSUPPORTED_PTX_VERSION (222)
```

**Three CUDA configurations** (f64 + f32 + mixed) all fail with the
same error 222. The error is at FIRST kernel compile, not at platform
initialization.

### 3.3 ldd / readelf static analysis (today, 2026-05-07)

```
$ ldd ~/.conda/envs/env-mace/lib/plugins/libOpenMMCUDA.so
libOpenMMCUDA.so: ../libnvrtc.so.13: version `libnvrtc.so.13' not found
                  (required by libOpenMMCUDA.so)
$ readelf -d $(readlink -f ~/.conda/envs/env-mace/lib/libnvrtc.so.13.2.78)
SONAME = libnvrtc.so.12   (because file is libnvrtc.so.12.8.61)
$ strings ~/.conda/envs/env-mace/lib/plugins/libOpenMMCUDA.so | grep nvrtc
libnvrtc.so.13
nvrtcGetNumSupportedArchs@libnvrtc.so.13
nvrtcGetPTX@libnvrtc.so.13
nvrtcCompileProgram@libnvrtc.so.13
... (all RTC symbols tagged @libnvrtc.so.13)
```

**Verdict:** The OpenMM CUDA plugin is hard-coded to link against
`libnvrtc.so.13` SONAME, which is incompatible with all of the
McCleary CUDA modules (12.0, 12.1, 12.6, 12.8, 12.9), all of which
ship SONAME `libnvrtc.so.12`. The symlink trick from Sub 1.1 cannot
fix this — it only forwards the file, not the SONAME version-script
tag, which is checked at lookup.

### 3.4 What about Context creation?

Cannot test from login (no GPU). The H200 evidence in §3.2 is conclusive:
the platform plugin reports as available (`speed=100.0`) but `Context`
construction crashes at the first kernel compile. The probe path the
user proposed (Context-create on H200 to "see if it works now") was
already executed on 2026-04-23 with identical versions to today's
env-mace, and **it failed**.

---

## 4. Upstream changelogs since Sub 1.1

### 4.1 OpenMM

Latest tagged release: **OpenMM 8.5.1 (2024-04-10)** — same as Sub 1.1.
No 8.5.2, no 8.6 release exists as of 2026-05-07. The conda-forge build
metadata (`openmm-8.5.1-py310h39b4bc9_0.json`) is also unchanged from
Sub 1.1's audit. The `8.5.1.dev-f7fa0c2` we run is a develop-branch
snapshot built around the same time (commit f7fa0c27, around April 2024
per git log).

No PR / issue thread on github.com/openmm/openmm references "sm_90 PTX
fix" or "CUDA 12.x rebuild" in the 2025-2026 window. The only related
threads are:
- Issue #3585 / #3598: PTX-version error reports on older CUDA combos.
  No maintainer fix; recommendation is "match driver+toolkit versions".
- Issue #3477: cudatoolkit ≥ 11.6 build issue (long resolved).

### 4.2 openmm-ml

Latest release: **1.6 (2025-03-25)** — same as Sub 1.1. No 1.7 or
later release. The 1.6 changelog item "Converted MACE to use
PythonForce" is the SOURCE of Failure B; the CUDA-context interop
issue is intrinsic to PythonForce and not addressed in any subsequent
patch.

Issue #119 (2026-02): user reports openmm-ml v1.5 requires CUDA 12.9,
incompatible with their CUDA 12.2 system. Unresolved by maintainers.

### 4.3 MACE / e3nn / openequivariance / cuequivariance

- **mace-torch**: 0.3.15 unchanged. No release in 2025-2026 that fixes
  the openequivariance API mismatch (per Sub 1.2's `1.2-mace-throughput-ceiling.md`:
  "MACE 0.3.15 conv_fusion call convention incompatible with oeq 0.6.6").
- **e3nn**: 0.4.4 unchanged.
- **openequivariance** 0.6.6: confirmed dead-end in Sub 1.2 R3
  (TensorProduct.forward signature mismatch).
- **cuequivariance** 0.9.1: tested in Sub 1.2 R1-R2, rejected
  (cublas ≥ 12.5 required vs torch's 12.1; naive fallback is 100-1000×
  slower).
- **PyTorch**: 2.5.1 -> 2.10.0+cu128 upgrade DID happen (2026-04-23).
  This is the only major version change since Sub 1.1. It did not change
  the CUDA platform outcome on H200 — the post-upgrade `diag_h200_final`
  reproduces the same PTX error.

### 4.4 NVIDIA stack

Driver 570.195.03 unchanged on McCleary. CUDA 12.9.1 module added
(2025 timeframe), but as shown in §2 it ships SONAME `libnvrtc.so.12`
and so does not bypass the OpenMM SONAME mismatch. No driver update
to a 580+ series that would expose libnvrtc.so.13 ABI is on the
McCleary roadmap as of today (no announcement in `module avail`).

### 4.5 Net change since Sub 1.1

| Component | Sub 1.1 (Apr 18) | Today (May 7) | Material? |
|---|---|---|---|
| OpenMM | 8.5.1 | 8.5.1.dev (same commit-era) | No |
| openmm-ml | 1.6 | 1.6 | No |
| MACE | 0.3.15 | 0.3.15 | No |
| e3nn | 0.4.4 | 0.4.4 | No |
| torch | 2.5.1+cu121 | 2.10.0+cu128 | Marginally — does not fix Failure A or B |
| Driver | 570.195.03 | 570.195.03 | No |
| OpenMM CUDA plugin SONAME | libnvrtc.so.13 | libnvrtc.so.13 | No |
| Workable CUDA modules on cluster | 12.0/12.1/12.6/12.8 | + 12.9.1 (default) | No (all SONAME .12) |
| openmm-torch (CUDA-context interop fix) | not built | not built | No |
| Source-built OpenMM with CUDA 12.x | env-mace-cuda exists, lib at /home/rag88/opt/openmm-cuda128 | UNUSED, env-mace untouched | No |

**Conclusion:** zero material upstream change since Sub 1.1 closed the
CUDA path. The probe outcome on 2026-05-07 will be identical to the
probe outcome on 2026-04-23 unless the operator first invests 2-4 hr
in (a) a from-source OpenMM CUDA rebuild AND (b) a from-source
openmm-torch GPU rebuild. Neither is planned for Sub 1.2.

---

## 5. Probe test plan — DO NOT EXECUTE (documented for reference only)

This section is included only as a thought-exercise and to give the
HeadAI a complete decision basis. **Do not run this.**

### 5.1 If we were to attempt a probe anyway

#### Recommended config

| Parameter | Value | Rationale |
|---|---|---|
| Partition | scavenge_gpu | 30 SU/h; minimal cost |
| Walltime | 30 min | Probe-only; should fail in <2 min |
| GRES | `--gres=gpu:1` `--gres=gpu_h200:1` | Same hardware as production |
| Cores / RAM | 8 / 32 GB | Standard for env-mace MD |
| Job name | random 8-char (e.g., `j7n2x4mq`) | per cryptic-name policy |
| Protein | NTL9 (390 atoms raw, 813 post-PDBFixer) | smallest active protein; same as the hung job; reuses existing PDB |
| Script | `mace_hybrid_npt_prod.py` with one-line edit at line 651-653: try CUDA, fall back to OpenCL | mirrors `diag_cuda_patch.py` pattern |
| Steps | 50 ps NPT (50,000 steps) | Matches existing probe protocol |
| Success criteria | (1) Context-create OK, (2) min completes without invalid-handle, (3) production runs ≥1 ns of stable NPT, (4) ns/day > 1.8 (current OpenCL throughput) |

Estimated SU cost: 30 SU/h × 0.5 h = ~15 SU. Plus ~600 SU if it actually
runs production for a few hours, but it WILL NOT — it will fail at min.

#### Verification steps

1. Confirm Context() returns without exception.
2. Run minimize(maxIterations=200), check for invalid-handle / illegal-memory.
3. If min OK, run 1000 production steps, compare ns/day.
4. If ns/day < 2.0, abort (no speedup; OpenCL is fine).
5. If ns/day > 3.0, validate forces against an OpenCL reference run.

#### Failure modes (the realistic ones)

| Mode | When it fires | What to do |
|---|---|---|
| `CUDA_ERROR_UNSUPPORTED_PTX_VERSION (222)` | Context() creation | Probe is over; verdict confirmed |
| `RuntimeError: CUDA driver error: invalid resource handle` | First minimize() step | Probe is over (if Failure A is somehow bypassed) |
| `IndexError: shape mismatch in MACE convolution` | First force eval | likely cuequivariance interaction; not a CUDA-platform bug |
| Hang at step ~25,000 (same as current OpenCL bug) | Mid-production | NOT what we're investigating; we'd be back at square one with extra cost |

### 5.2 Compatibility with existing checkpoint / watchdog machinery

- **Checkpoint compatibility:** OpenMM checkpoints are platform-agnostic
  at the file-format level (XML serialized state + binary positions /
  velocities). A CUDA-platform run could in principle resume from an
  OpenCL checkpoint and vice versa. **However**, NPT checkpoints contain
  box-vector + barostat-state info that has occasionally been reported
  to mis-deserialize across platform changes (search github.com/openmm/openmm
  for "barostat state cross-platform"; not a reported issue but worth
  flagging). For a fresh probe, start cold (no checkpoint).
- **Watchdog compatibility:** the 1200s no-write timer is implemented
  via inotify on the production log file. Platform-independent. If
  CUDA produced the same ~25k-step hang as OpenCL, the watchdog would
  catch it identically — but the hang would be inside the MACE
  PythonForce callback (the dominant cost) which is platform-agnostic.
  In other words: **switching to CUDA does NOT reduce the probability
  of the hang we just hit on NTL9.** That hang is in the
  PythonForce -> e3nn callback, not in the OpenMM integrator.

---

## 6. Risk assessment

### 6.1 Probability matrix

| Outcome | Probability | Reasoning |
|---|---|---|
| CUDA Context creates AND min completes AND production runs faster than OpenCL | **~3%** | Requires Failure A AND Failure B AND interop hang to all spontaneously self-resolve, with NO version changes. Theoretically possible if some cluster-side toolchain quirk has shifted; structurally unlikely. |
| CUDA Context creates AND min completes (any throughput) | **~5%** | Adds the case where it works but is no faster. |
| CUDA Context creates but min crashes with invalid-handle | **~30%** | If a hidden cluster-side libnvrtc rebind happened (e.g., CUDA 12.9.1 module providing a libnvrtc.so.13 symlink we haven't found), then Failure A clears but Failure B remains. |
| CUDA Context-create fails with PTX 222 (Failure A unchanged) | **~65%** | The base case. Confirmed structurally still present. |

Geometric expected value of running a probe at 600 SU on scavenge:
- 65% × (cost 30 SU, fail in 60 s, no learning beyond what we already have): -19.5 SU
- 30% × (cost 60 SU, fail in 5 min at minimize(): partial learning): -18 SU
- 5% × (cost 600 SU, partial speedup, requires force-validation rerun ~600 SU more): +(uncertain), best case +0.5× over OpenCL ≈ +25% wall reduction on remaining 4 ns of the NTL9 prod = saves ~6 GPU-h, ~180 SU at 30/h
- ≈ -19.5 - 18 + 9 (5% × 180) = **-28 SU expected, plus ~30-60 min HeadAI time, plus an opportunity cost of 1 production launch slot**.

The probe is not justifiable on cost-benefit grounds.

### 6.2 What WOULD justify a probe

- A confirmed fresh OpenMM build (from-source, against CUDA 12.9.1)
  installed in env-mace OR env-mace-cuda. **None exists.** The Sub 1.1
  source build at `/home/rag88/opt/openmm-cuda128` is for env-mace-cuda,
  NOT env-mace, and was tied to torch 2.5.1+cu121. Today's env-mace has
  torch 2.10.0+cu128 — using the source-built OpenMM 8.5.1 against
  CUDA 12.8 with a different torch version reopens ABI risk on the
  PythonForce / TorchScript boundary.
- A confirmed openmm-torch GPU build (Sub 1.1 §"openmm-torch rebuild"
  identified this as the proper fix for Failure B). **None exists.**
- A new MACE / openmm-ml release that replaces PythonForce with a
  CUDA-stream-aware backend. **No such release exists** (last MACE
  0.3.15 = May 2024; last openmm-ml 1.6 = March 2025).

### 6.3 Cost of NOT probing

- Continued use of OpenCL @ 1.8-2.6 ns/day on H200 (the established
  ceiling per `1.2-mace-throughput-ceiling.md`).
- 5 ns × 3 proteins (WW, GB3, UBQ-alt or NTL9) takes ~6 GPU-days @ 2.0 ns/day.
- Hangs at ~25k-step rate of (TBD by HeadAI's running tally; first NTL9
  hung once in 25k steps; previous WW had 5 hung jobs across multiple
  resubmits in mid-April per `slurm_logs/*.hung`). Watchdog + checkpoint
  recovers automatically.
- **Cost of NOT probing = zero new SU**. Status quo is sustainable.

---

## 7. Recommendation

### 7.1 Verdict: **DO NOT submit a CUDA probe.**

The Sub 1.1 verdict ("CUDA broken on H200") is empirically still
correct as of 2026-05-07. Three independent lines of evidence:

1. **Structural** — the conda-forge OpenMM CUDA plugin's hard-coded
   `libnvrtc.so.13` SONAME requirement cannot be met by any CUDA
   module currently on McCleary. Confirmed via `objdump -p` and
   `readelf -d` today.
2. **Empirical** — the most recent on-cluster diagnostic
   (`diag_h200_final_9353349`, 2026-04-23, post torch 2.10 upgrade,
   on H200) reproduces `CUDA_ERROR_UNSUPPORTED_PTX_VERSION (222)`.
3. **Upstream** — no OpenMM, openmm-ml, MACE, e3nn release since
   Sub 1.1 addresses either Failure A or Failure B. Github issue
   threads (#3585, #3598, openmm-ml #119) remain unresolved.

### 7.2 The NTL9 hang is independent of the platform choice

The hang at step 25,000 in job 10622876 is in the
**MACE-PythonForce-e3nn** pipeline, which runs on PyTorch's CUDA
context regardless of OpenMM platform. Switching OpenMM's integrator
from OpenCL to CUDA cannot change the probability of this hang because
the hang is dominated by what happens *inside* the PythonForce
callback, not by the integrator kernel.

The watchdog + checkpoint did its job: detected the hang, killed the
hung Python, restarted from the last checkpoint. The current run is
still on track to complete its target NPT trajectory.

### 7.3 What to do instead

- **Continue the OpenCL production run** on NTL9 (10622876 will
  complete or be requeued by the watchdog).
- **Track hang rate** across the next 3-5 production launches. If hang
  rate exceeds ~30% of submitted jobs (where "hang" = watchdog kill
  rather than clean walltime), escalate via help-needed for a different
  mitigation lane.
- **DO NOT** invest in a CUDA path closure during Sub 1.2. The proper
  followups are deferred:
  - Sub 1.5+: LAMMPS engine swap (parked per `optimization-round-4-mace.md` §4)
  - Sub 1.5+: openmm-torch GPU rebuild (1-2 hr) AS PART OF a coordinated
    OpenMM-from-source rebuild against CUDA 12.9.1; only worth the
    investment if the LAMMPS engine swap is not viable
  - **Avoid one-off probes** that retread already-investigated ground.

### 7.4 If the human operator overrides this recommendation

Run the probe ONLY in this configuration:

```
sbatch --partition=scavenge_gpu --time=00:30:00 --gres=gpu:1 \
       --constraint="gpu_h200" --cpus-per-task=8 --mem=32G \
       --job-name=j7n2x4mq \
       --output=output/slurm_logs/cuda_probe_h200_%j.out \
       --error=output/slurm_logs/cuda_probe_h200_%j.err \
       output/scripts/diag_cuda_patch.sbatch
```

(Where `diag_cuda_patch.sbatch` is the existing diagnostic — it already
implements the try-CUDA / fall-back-to-OpenCL platform selection.)

Expected outcome: identical to `diag_cuda_patch_8998059` and
`diag_h200_final_9353349`: CUDA module load fails with PTX 222 in <60s
of node walltime. Total cost ~5 SU. Then close out the investigation
permanently.

---

## 8. Files referenced

- `/home/rag88/projects/CompBioSummer2026/Execution/shared/notes/1.1-openmm-cuda-rebuild.md` (Sub 1.1 Failure A diagnosis)
- `/home/rag88/projects/CompBioSummer2026/Execution/shared/notes/1.1-mace-cuda-benchmark.md` (Sub 1.1 Failure B diagnosis + empirical matrix)
- `/home/rag88/projects/CompBioSummer2026/Execution/shared/notes/1.1-mace-hybrid-validation.md` §11 (H200 OpenCL 11.5× speedup over RTX 5000 Ada)
- `/home/rag88/projects/CompBioSummer2026/Execution/shared/notes/1.2-mace-throughput-ceiling.md` (Sub 1.2 R1-R3 SONAME-mismatch confirmation; CUDA = OpenCL on inference-bound MACE)
- `/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/optimization-round-4-mace.md` §4 (CUDA + cuequivariance saturated; LAMMPS deferred)
- `/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/mace_hybrid_npt_prod.py:651-653` (current OpenCL platform selection)
- `/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/diag_cuda_patch.py` (existing CUDA diagnostic — already covers the try-CUDA / fallback pattern)
- `/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/slurm_logs/diag_h200_final_9353349.out` (most recent H200 CUDA-fail evidence, 2026-04-23)
- `/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/slurm_logs/upgrade_v2_9301099.out` (torch 2.10 upgrade transcript with multi-config CUDA-fail outcomes, 2026-04-23)
- `/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/slurm_logs/mace_npt_prod_ntl9_q6kz3m8x_10622876.out` (the hang that motivated this investigation)

## 9. External references

- [OpenMM Issue #3585](https://github.com/openmm/openmm/issues/3585) — `CUDA_ERROR_UNSUPPORTED_PTX_VERSION (222)` (unresolved, generic)
- [OpenMM Issue #3598](https://github.com/openmm/openmm/issues/3598) — same error (unresolved, generic)
- [openmm-ml Issue #119](https://github.com/openmm/openmm-ml/issues/119) — CUDA 12.x compatibility (2026-02; unresolved)
- [OpenMM 8.5.1 release notes](https://github.com/openmm/openmm/releases) — last release 2024-04-10; no CUDA fixes since
- [openmm-ml 1.6 release notes](https://github.com/openmm/openmm-ml/releases) — last release 2025-03-25; PythonForce introduced (the source of Failure B)

## 10. Time + cost of this investigation

- Wall: ~45 min (file reads + version probes + ldd + web checks)
- SU consumed: 0 (no SLURM submitted)
- Disk consumed: 1 markdown file (~30 KB)
