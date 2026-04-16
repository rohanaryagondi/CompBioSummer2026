---
task_id: "task-002"
title: "SO3LR Crambin 1 ns NVT Simulation"
subphase: "1.1"
track: alpha-m
wave: 1
agent: "so3lr-pilot"
effort: "3-5 days"
status: planned
created: 2026-04-16
---

# Task 002: SO3LR Crambin 1 ns NVT Simulation

## Objective

Validate that SO3LR can run a stable 1 ns NVT trajectory on crambin (46 residues)
via JAX-MD. This is the primary D1 gate evidence for SO3LR. The D1 gate (May 9)
requires: "SO3LR installs and runs 1 ns NVT on crambin." Installation was verified
in Phase 0; this task verifies simulation execution.

---

## Context

SO3LR (Frank et al., JACS 2026) is a machine-learning force field built on the
SO(3)-equivariant architecture, designed for protein simulation. Unlike MACE-OFF24,
SO3LR uses JAX-MD (not OpenMM) as its simulation engine. Phase 0 confirmed that
env-so3lr (SO3LR 0.1.0, JAX 0.5.3, Python 3.12) installed successfully. The
cross-agent note `0.1-env-so3lr-build.md` confirmed installation but noted "GPU
verification will happen in Phase 1 when actual simulations run."

SO3LR's JAX-MD simulation paradigm is fundamentally different from OpenMM:
- JAX-MD uses JIT compilation (slow first run, fast subsequent runs)
- Neighbor lists are explicit objects that must be managed
- The simulation loop is often written as a JAX `scan` or Python loop with JAX ops
- GPU memory management differs from PyTorch

The agent MUST study the SO3LR documentation, examples, and tutorials before
attempting simulation setup. The SO3LR GitHub repository likely contains example
scripts for protein simulation.

---

## Detailed Instructions

### Step 1: Environment Verification

1. Activate env-so3lr: `conda activate env-so3lr`
2. Verify Python 3.12: `python --version`
3. Verify SO3LR: `python -c "import so3lr; print(so3lr.__version__)"`
4. Verify JAX GPU: `python -c "import jax; print(jax.devices())"`
   Expect: at least one GPU device listed
5. Verify JAX-MD: `python -c "import jax_md; print('jax_md OK')"`
6. If JAX does not see the GPU:
   - Check CUDA version compatibility: `nvidia-smi`
   - May need: `pip install jax[cuda12]` or equivalent
   - Document the issue and resolution

### Step 2: Study SO3LR API

1. Check SO3LR documentation: `python -c "import so3lr; help(so3lr)"` or browse
   the SO3LR GitHub repo (https://github.com/thorben-frank/so3lr or similar)
2. Look for example scripts in the SO3LR package:
   ```python
   import so3lr, os
   print(os.path.dirname(so3lr.__file__))
   # Check for examples/ directory
   ```
3. Identify the correct API for:
   - Loading/creating the SO3LR potential
   - Building a simulation system from a PDB structure
   - Setting up NVT thermostat in JAX-MD
   - Running production MD
4. Document the API you discover — this is critical for future Alpha-M tasks

### Step 3: Load Crambin Structure

1. Locate crambin PDB from Phase 0:
   `../../phase-0/subphase-0.1/proteins/manifest.json` for path
2. Parse structure for JAX-MD:
   - JAX-MD typically works with positions as JAX arrays
   - May need MDTraj or ASE to read the PDB and extract coordinates
   ```python
   import mdtraj as md  # or ase.io
   traj = md.load('crambin.pdb')
   positions = traj.xyz[0]  # (n_atoms, 3) in nm
   ```
3. Identify atom types and build topology for SO3LR

### Step 4: Staged Simulation

**Stage A: Short vacuum test (100 ps)**

1. Create SO3LR potential for crambin
2. Initialize JAX-MD neighbor list
3. Set up Nose-Hoover or Langevin thermostat at 300 K
4. Run 100 ps with 1 fs timestep (100,000 steps)
5. Check for NaN in positions/energies after each block
6. If successful, proceed to Stage B

**Stage B: Extended vacuum (1 ns)**

1. Continue simulation to 1 ns (1,000,000 steps total)
2. Save coordinates every 1 ps
3. Monitor energy conservation and temperature
4. Log positions, energies, and temperature at each save point

**Stage C: Explicit solvent (if SO3LR supports it)**

1. If SO3LR can handle water molecules:
   - Solvate crambin in water box
   - Run 1 ns NVT with explicit solvent
2. If not: document that SO3LR is vacuum/implicit-only for this version
   and the vacuum result is the D1 evidence

### Step 5: Production Run via SLURM

1. Write simulation script: `scripts/so3lr_crambin_nvt.py`
2. Write SLURM batch script:
   ```bash
   #!/bin/bash
   #SBATCH --job-name=so3lr-crambin
   #SBATCH --partition=gpu_h200
   #SBATCH --gres=gpu:1
   #SBATCH --time=08:00:00
   #SBATCH --mem=64G
   #SBATCH --output=slurm-%j.out
   
   conda activate env-so3lr
   python scripts/so3lr_crambin_nvt.py
   ```
   Note: SO3LR/JAX may need more memory for JIT compilation (request 64 GB).
3. Submit and monitor: `sbatch scripts/so3lr_crambin.sbatch`

### Step 6: Analysis

1. Compute RMSD vs starting structure (backbone atoms)
2. Compute potential energy trace
3. Compute temperature trace
4. Determine maximum stable simulation time
5. Generate plots (RMSD, energy, temperature vs time)
6. Save to `../../output/task-002-*.png`

### Step 7: D1 Evidence Report

Write `../../output/task-002-d1-evidence.md`:
- SO3LR version and JAX/JAX-MD versions
- Which stage succeeded (A/B/C)
- Maximum stable trajectory length
- RMSD, energy, temperature assessment
- JAX JIT compilation time (first step vs subsequent)
- Pass/Fail against D1 criterion
- If failure: exact error, what was tried

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| `../../tasks/task-002-so3lr-crambin-nvt.md` | This task specification |
| `../../../../phase-0/subphase-0.1/proteins/manifest.json` | Crambin PDB path |
| `../../../../../shared/notes/0.1-env-so3lr-build.md` | SO3LR env details, JAX version |
| `../../../../../Proposal/Alpha-M.md` (Sections 2-3) | SO3LR details |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../Proposal/ImplementationPlan.md` (Section 13: D1 gate) | D1 gate criteria |
| `../../../../phase-0/subphase-0.1/envs/env-so3lr.yml` | Exact env-so3lr packages |

### DO NOT READ

- Other SubAgents' task specs (not your scope)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)

---

## Output Artifacts

### Code and data artifacts

| Artifact | Path | Format |
|----------|------|--------|
| Simulation script | `../../output/scripts/so3lr_crambin_nvt.py` | Python |
| SLURM batch script | `../../output/scripts/so3lr_crambin.sbatch` | Shell |
| Trajectory | HPC scratch (path in status report) | NPZ or XYZ |
| Energy/temperature log | `../../output/task-002-crambin-so3lr.log` | CSV |
| RMSD plot | `../../output/task-002-rmsd.png` | PNG |
| Energy plot | `../../output/task-002-energy.png` | PNG |
| D1 evidence report | `../../output/task-002-d1-evidence.md` | Markdown |
| SO3LR API notes | `../../output/task-002-so3lr-api.md` | Markdown |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-002-status.md` | `status-report.md` |
| Cross-agent note (D1) | `../../../../../shared/notes/1.1-so3lr-crambin.md` | `cross-agent-note.md` |

---

## Success Criteria (Zero Compromise)

This task is complete ONLY if ALL of the following are true:

1. [ ] SO3LR runs on crambin without NaN/Inf for at least 100 ps
2. [ ] Maximum stable trajectory length documented (target: 1 ns)
3. [ ] RMSD vs starting structure computed and plotted
4. [ ] Potential energy trace computed and plotted
5. [ ] Temperature stability verified
6. [ ] SO3LR API documented (how to set up simulation from PDB)
7. [ ] D1 evidence report written with clear pass/fail
8. [ ] Cross-agent note written to `shared/notes/1.1-so3lr-crambin.md`
9. [ ] Status report written to `../../status/task-002-status.md`

---

## Verification

1. Trajectory file exists and is non-empty
2. Energy log has entries for full simulation duration
3. No NaN/Inf in logs
4. RMSD plot shows reasonable values
5. D1 evidence report explicitly states pass or fail
6. SO3LR API notes document the working simulation setup

---

## Failure Protocol

1. Write status report with `failed` or `blocked`
2. Document maximum stage reached and exact failure point
3. Include error messages and SLURM job IDs
4. Common JAX issues: CUDA version mismatch, OOM, NaN from bad initialization
5. D1 evidence report MUST still be written — failure IS evidence
6. If SO3LR fails: D1 may still GO if MACE-OFF24 succeeds
7. Document what the SO3LR authors' examples look like for comparison
