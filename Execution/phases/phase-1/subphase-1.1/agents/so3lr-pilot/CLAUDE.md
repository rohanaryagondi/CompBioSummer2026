# SubAgent: SO3LR Crambin 1 ns NVT Simulation

You are a **SubAgent** executing task-002 in subphase 1.1 of the CompBioSummer2026
execution pipeline. You have a narrowly scoped task with explicit success criteria.
Execute your task, write your documentation, and report your results.

---

## Your Task

**Task ID:** task-002
**Title:** SO3LR crambin 1 ns NVT simulation
**Track:** Alpha-M
**Subphase:** 1.1
**Estimated effort:** 3-5 days

---

## What You Must Accomplish (Zero Compromise)

1. Study the SO3LR API and JAX-MD simulation setup (this is NOT OpenMM — different paradigm)
2. Run a stable NVT trajectory on crambin (46 residues) using SO3LR via JAX-MD
3. Staged approach: vacuum short test -> vacuum 1 ns -> explicit solvent (if supported)
4. Target: 1 ns NVT at 300 K with 1 fs timestep. Minimum acceptable: 100 ps stable.
5. Analyze: RMSD, potential energy, temperature stability
6. Document the SO3LR simulation API (critical for future Alpha-M tasks)
7. Write D1 gate evidence report (pass/fail with specific metrics)
8. Write cross-agent note to `../../../../../shared/notes/1.1-so3lr-crambin.md`
9. Write status report to `../../status/task-002-status.md`

**D1 gate criterion (May 9):** "SO3LR installs and runs 1 ns NVT on crambin."

---

## What You Read

### MUST READ (before starting)

| File | Why |
|------|-----|
| `../../tasks/task-002-so3lr-crambin-nvt.md` | Your full task specification |
| `../../../../phase-0/subphase-0.1/proteins/manifest.json` | Crambin PDB path |
| `../../../../../shared/notes/0.1-env-so3lr-build.md` | SO3LR env: JAX 0.5.3, Python 3.12 |
| `../../../../../Proposal/Alpha-M.md` (Sections 2-3) | SO3LR context |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../phase-0/subphase-0.1/envs/env-so3lr.yml` | Exact package versions |

### DO NOT READ

- Other SubAgents' task specs (not your scope)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)

---

## Detailed Instructions

Follow `../../tasks/task-002-so3lr-crambin-nvt.md`. Key points:

1. **Environment:** `conda activate env-so3lr` (Python 3.12, JAX 0.5.3, SO3LR 0.1.0)
2. **CRITICAL FIRST STEP:** Study the SO3LR API. It uses JAX-MD, NOT OpenMM.
   - Check SO3LR GitHub for example scripts
   - Run `python -c "import so3lr; help(so3lr)"` to discover the API
   - Look for `examples/` in the package directory
3. **Verify JAX sees GPU:** `python -c "import jax; print(jax.devices())"`
4. **Crambin PDB:** Load via MDTraj/ASE, convert to JAX arrays
5. **Simulation:** JAX-MD neighbor lists, thermostat, integration loop
6. **JIT compilation:** First step is slow (JAX compiles). Time it separately.
7. **NaN check:** JAX can silently produce NaN. Check positions/energies explicitly.
8. **SLURM:** gpu_h200, 1 GPU, 8 hours, 64 GB memory (JAX JIT needs extra RAM)

**IMPORTANT:** Document the SO3LR API you discover in
`../../output/task-002-so3lr-api.md`. This is critical for future tasks that
use SO3LR on larger proteins.

---

## What You Write

### Code and data artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Simulation script | `../../output/scripts/so3lr_crambin_nvt.py` | Production code |
| SLURM batch script | `../../output/scripts/so3lr_crambin.sbatch` | Job submission |
| Trajectory | HPC scratch (path in status report) | NPZ/XYZ |
| Energy log | `../../output/task-002-crambin-so3lr.log` | CSV |
| RMSD plot | `../../output/task-002-rmsd.png` | PNG |
| Energy plot | `../../output/task-002-energy.png` | PNG |
| D1 evidence | `../../output/task-002-d1-evidence.md` | Pass/fail report |
| API documentation | `../../output/task-002-so3lr-api.md` | SO3LR usage guide |

### Mandatory documentation

**Status report:** `../../status/task-002-status.md`
**Cross-agent note:** `../../../../../shared/notes/1.1-so3lr-crambin.md`

---

## Verification

1. [ ] Trajectory file exists and is non-empty
2. [ ] No NaN/Inf in energy or position logs
3. [ ] RMSD plot shows reasonable protein dynamics
4. [ ] D1 evidence report explicitly states PASS or FAIL
5. [ ] SO3LR API notes document how to run simulation from PDB
6. [ ] Cross-agent note written
7. [ ] Status report written

---

## If Something Goes Wrong

1. Document everything. Failure IS evidence for the D1 gate.
2. Common JAX issues: CUDA version mismatch, XLA compilation errors, OOM
3. SO3LR may require specific input formats — study docs carefully
4. If SO3LR fails: MACE (task-001) may still succeed. D1 needs only 1 MLFF.
5. Even partial results (100 ps instead of 1 ns) have value — report max stable time.
