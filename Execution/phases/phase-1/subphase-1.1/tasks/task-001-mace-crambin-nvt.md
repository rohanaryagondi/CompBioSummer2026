---
task_id: "task-001"
title: "MACE-OFF24 Crambin 1 ns NVT Simulation"
subphase: "1.1"
track: alpha-m
wave: 1
agent: "mace-pilot"
effort: "3-5 days"
status: planned
created: 2026-04-16
---

# Task 001: MACE-OFF24 Crambin 1 ns NVT Simulation

## Objective

Validate that MACE-OFF24 can run a stable 1 ns NVT trajectory on crambin (46
residues) via the OpenMM-ML integration. This is the primary D1 gate evidence for
MACE-OFF24. The D1 gate (May 9) requires: "MACE-OFF24 installs and runs 1 ns NVT
on crambin." Installation was verified in Phase 0; this task verifies simulation
execution.

---

## Context

MACE-OFF24 (Kovacs et al., JACS 2025) is a machine-learning force field trained on
the SPICE dataset. It is one of 2 MLFFs in the Alpha-M benchmark (the other is
SO3LR). Phase 0 confirmed that env-mace (mace-torch 0.3.15, PyTorch) installed
successfully. However, the cross-agent note `0.1-env-mace-build.md` flagged that
"OpenMM was found in user site-packages rather than installed fresh. Phase 1 HeadAI
should verify OpenMM-ML integration works with MACE for actual MD simulations."

The OpenMM-ML integration (openmm-ml package) provides the bridge between MACE's
ML potential and OpenMM's simulation engine. This integration has NOT been tested
yet — it is the key validation target for this task.

Crambin (PDB: 1CRN, 46 residues, 3 disulfide bonds) is the smallest Tier A protein
and the ideal MLFF validation target: small enough for fast iteration, large enough
to test real protein dynamics.

---

## Detailed Instructions

### Step 1: Environment Verification

1. Activate env-mace: `conda activate env-mace`
2. Verify mace-torch: `python -c "import mace; print(mace.__version__)"`
   Expected: 0.3.15
3. Check if openmm-ml is installed: `python -c "from openmmml import MLPotential; print('OK')"`
4. If openmm-ml is NOT installed:
   ```bash
   pip install openmm-ml
   ```
5. List available ML potentials:
   ```python
   from openmmml import MLPotential
   print(MLPotential.getRegisteredPotentials())
   ```
   Expect to see 'maceoff' or 'mace-off24' in the list.
6. Verify OpenMM GPU access:
   ```python
   import openmm
   platform = openmm.Platform.getPlatformByName('CUDA')
   print(f"CUDA platform: {platform.getName()}")
   ```

### Step 2: Load Crambin Structure

1. Locate crambin PDB from Phase 0:
   `../../phase-0/subphase-0.1/proteins/crambin.pdb`
   or check `../../phase-0/subphase-0.1/proteins/manifest.json` for exact path.
2. If crambin.pdb uses a non-standard name (e.g., `1crn.pdb`), find it via manifest.
3. Load with OpenMM:
   ```python
   from openmm.app import PDBFile
   pdb = PDBFile('path/to/crambin.pdb')
   ```
4. Add hydrogens if not present:
   ```python
   from openmm.app import Modeller
   modeller = Modeller(pdb.topology, pdb.positions)
   modeller.addHydrogens()
   ```

### Step 3: Staged Simulation Approach

Execute in order. Proceed to the next stage only if the current stage succeeds.

**Stage A: Vacuum NVT (validates MACE force evaluation)**

```python
from openmmml import MLPotential
potential = MLPotential('maceoff')  # or 'mace-off24' — check registered name
system = potential.createSystem(modeller.topology)

# NVT setup
from openmm import LangevinMiddleIntegrator
from openmm.unit import kelvin, picosecond, femtosecond
integrator = LangevinMiddleIntegrator(300*kelvin, 1/picosecond, 1*femtosecond)

from openmm.app import Simulation
simulation = Simulation(modeller.topology, system, integrator)
simulation.context.setPositions(modeller.positions)

# Minimize
simulation.minimizeEnergy(maxIterations=1000)

# Short test: 1 ps (1000 steps)
simulation.step(1000)

# Check for NaN
state = simulation.context.getState(getEnergy=True)
energy = state.getPotentialEnergy()
print(f"Energy after 1 ps: {energy}")
# If energy is NaN or extreme, STOP and document
```

If Stage A succeeds for 1 ps, extend to 100 ps (100,000 steps), then to 1 ns
(1,000,000 steps).

**Stage B: Explicit Solvent NVT (realistic benchmark conditions)**

```python
from openmm.app import Modeller
# Add water box
modeller.addSolvent(potential.createSystem, boxSize=...)  # or use ForceField water
```

Note: MACE-OFF24 may or may not handle water molecules. If it does, create a full
explicit solvent system. If it does NOT:

**Stage C: Hybrid (MACE protein + classical water)**

Use OpenMM-ML's mixed system capability:
```python
system = potential.createMixedSystem(
    topology, 
    pdb.positions,
    atomSubset=protein_atom_indices,  # MACE for protein only
    # Classical FF for water
)
```

The OpenMM-ML documentation describes this hybrid approach. Consult it if needed.

### Step 4: Production Run

1. Write a Python script: `scripts/mace_crambin_nvt.py`
2. Add trajectory output: save coordinates every 1 ps (1000 steps)
   ```python
   from openmm.app import DCDReporter, StateDataReporter
   simulation.reporters.append(DCDReporter('crambin_mace.dcd', 1000))
   simulation.reporters.append(StateDataReporter('crambin_mace.log', 1000,
       step=True, potentialEnergy=True, temperature=True, time=True))
   ```
3. Add NaN force check every 100 ps:
   ```python
   import numpy as np
   # Check periodically in a loop
   for i in range(10):  # 10 blocks of 100 ps
       simulation.step(100000)
       state = simulation.context.getState(getForces=True)
       forces = state.getForces(asNumpy=True)
       if np.any(np.isnan(forces)):
           print(f"NaN detected at {(i+1)*100} ps!")
           break
   ```
4. Submit as SLURM job:
   ```bash
   sbatch --job-name=mace-crambin \
          --partition=gpu_h200 \
          --gres=gpu:1 \
          --time=08:00:00 \
          --mem=32G \
          --output=slurm-%j.out \
          scripts/mace_crambin_nvt.py
   ```
   Wrap in a SLURM batch script that activates env-mace first.

### Step 5: Analysis

1. Load trajectory with MDTraj or MDAnalysis:
   ```python
   import mdtraj as md
   traj = md.load('crambin_mace.dcd', top='crambin.pdb')
   ```
2. Compute RMSD vs starting structure (backbone atoms)
3. Compute potential energy trace from log file
4. Compute temperature trace from log file
5. Determine maximum stable simulation time (before any instability/drift)
6. Generate plots: RMSD vs time, energy vs time, temperature vs time
7. Save plots to `../../output/task-001-*.png`

### Step 6: D1 Evidence Report

Write a summary document at `../../output/task-001-d1-evidence.md`:
- MACE-OFF24 version and OpenMM-ML version
- Which stage succeeded (A/B/C)
- Maximum stable trajectory length
- RMSD range and stability assessment
- Energy drift (if any)
- Pass/Fail assessment against D1 criterion
- If failure: exact error, what was tried, recommended next steps

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| `../../tasks/task-001-mace-crambin-nvt.md` | This task specification |
| `../../../../phase-0/subphase-0.1/proteins/manifest.json` | Crambin PDB path and metadata |
| `../../../../../shared/notes/0.1-env-mace-build.md` | MACE env details, OpenMM warning |
| `../../../../../Proposal/Alpha-M.md` (Sections 2-3) | MACE-OFF24 details, benchmark design |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../Proposal/ImplementationPlan.md` (Section 13: D1 gate) | D1 gate criteria details |
| `../../../../phase-0/subphase-0.1/envs/env-mace.yml` | Exact env-mace package versions |

### DO NOT READ

- Other SubAgents' task specs in `../../tasks/` (not your scope)
- Delta or Gamma proposal documents (not relevant to this task)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)

---

## Output Artifacts

### Code and data artifacts

| Artifact | Path | Format |
|----------|------|--------|
| Simulation script | `../../output/scripts/mace_crambin_nvt.py` | Python |
| SLURM batch script | `../../output/scripts/mace_crambin.sbatch` | Shell |
| Trajectory | HPC scratch (path documented in status report) | DCD |
| Energy/temperature log | `../../output/task-001-crambin-mace.log` | CSV |
| RMSD plot | `../../output/task-001-rmsd.png` | PNG |
| Energy plot | `../../output/task-001-energy.png` | PNG |
| D1 evidence report | `../../output/task-001-d1-evidence.md` | Markdown |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-001-status.md` | `status-report.md` |
| Cross-agent note (D1) | `../../../../../shared/notes/1.1-mace-crambin.md` | `cross-agent-note.md` |

---

## Success Criteria (Zero Compromise)

This task is complete ONLY if ALL of the following are true:

1. [ ] MACE-OFF24 runs on crambin without NaN forces for at least 100 ps
2. [ ] Maximum stable trajectory length documented (target: 1 ns)
3. [ ] RMSD vs starting structure computed and plotted
4. [ ] Potential energy trace computed and plotted
5. [ ] Temperature stability verified (300 K +/- reasonable range)
6. [ ] D1 evidence report written with clear pass/fail assessment
7. [ ] Cross-agent note written to `shared/notes/1.1-mace-crambin.md`
8. [ ] Simulation script saved (reproducibility)
9. [ ] Status report written to `../../status/task-001-status.md`

---

## Verification

Before declaring this task complete, verify:

1. Trajectory file exists and is non-empty
2. Energy log file has entries for the full simulation duration
3. No NaN values in energy or force logs
4. RMSD plot shows reasonable values (typically <5 A for a stable protein)
5. D1 evidence report explicitly states pass or fail
6. Cross-agent note exists at `shared/notes/1.1-mace-crambin.md`
7. Status report written with all artifacts listed

---

## Failure Protocol

If this task cannot be completed:

1. Write a status report with status `failed` or `blocked`
2. Document the maximum stage reached (A/B/C) and where it failed
3. Include exact error messages and SLURM job IDs
4. Document what was tried (e.g., different timesteps, different setup approaches)
5. The D1 evidence report must still be written — a documented failure IS D1 evidence
6. If MACE fails entirely: this does NOT block other tasks. D1 may still be GO if SO3LR succeeds.
7. Suggest what might fix the issue (version change, different integration approach)
