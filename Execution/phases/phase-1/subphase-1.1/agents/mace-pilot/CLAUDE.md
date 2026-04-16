# SubAgent: MACE-OFF24 Crambin 1 ns NVT Simulation

You are a **SubAgent** executing task-001 in subphase 1.1 of the CompBioSummer2026
execution pipeline. You have a narrowly scoped task with explicit success criteria.
Execute your task, write your documentation, and report your results.

---

## Your Task

**Task ID:** task-001
**Title:** MACE-OFF24 crambin 1 ns NVT simulation
**Track:** Alpha-M
**Subphase:** 1.1
**Estimated effort:** 3-5 days

---

## What You Must Accomplish (Zero Compromise)

1. Verify OpenMM-ML integration with MACE-OFF24 in env-mace
2. Run a stable NVT trajectory on crambin (46 residues) using MACE-OFF24
3. Staged approach: vacuum (Stage A) -> explicit solvent (Stage B) -> hybrid (Stage C)
4. Target: 1 ns NVT at 300 K with 1 fs timestep. Minimum acceptable: 100 ps stable.
5. Analyze: RMSD, potential energy, temperature stability
6. Write D1 gate evidence report (pass/fail with specific metrics)
7. Write cross-agent note to `../../../../../shared/notes/1.1-mace-crambin.md`
8. Write status report to `../../status/task-001-status.md`

**D1 gate criterion (May 9):** "MACE-OFF24 installs and runs 1 ns NVT on crambin."
Your output directly determines the D1 gate assessment for MACE.

---

## What You Read

### MUST READ (before starting)

| File | Why |
|------|-----|
| `../../tasks/task-001-mace-crambin-nvt.md` | Your full task specification with step-by-step instructions |
| `../../../../phase-0/subphase-0.1/proteins/manifest.json` | Crambin PDB path and metadata |
| `../../../../../shared/notes/0.1-env-mace-build.md` | MACE env details, OpenMM site-packages warning |
| `../../../../../Proposal/Alpha-M.md` (Sections 2-3) | MACE-OFF24 context, benchmark design |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../phase-0/subphase-0.1/envs/env-mace.yml` | Exact package versions in env-mace |
| `../../../../../Proposal/ImplementationPlan.md` (Section 13) | D1 gate criteria detail |

### DO NOT READ

- Other SubAgents' task specs in `../../tasks/` (not your scope)
- Other SubAgents' output in `../../output/` (not your scope)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)

---

## Detailed Instructions

Follow the step-by-step procedure in your task spec (`../../tasks/task-001-mace-crambin-nvt.md`).
Key points:

1. **Environment:** `conda activate env-mace`
2. **OpenMM-ML:** Install if missing (`pip install openmm-ml`). Check MACE is registered.
3. **Crambin PDB:** Load from Phase 0 proteins directory via manifest.json
4. **Staged approach:**
   - Stage A: Vacuum NVT (validates force evaluation)
   - Stage B: Explicit solvent (realistic conditions)
   - Stage C: Hybrid MACE+classical (if B fails)
5. **Simulation:** 1 ns NVT at 300 K, 1 fs timestep, Langevin thermostat
6. **NaN monitoring:** Check forces every 100 ps. Auto-kill if NaN detected.
7. **SLURM:** gpu_h200 partition, 1 GPU, 4-8 hours wall time
8. **Analysis:** RMSD, energy trace, temperature trace, max stable time

---

## What You Write

### Code and data artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Simulation script | `../../output/scripts/mace_crambin_nvt.py` | Production simulation code |
| SLURM batch script | `../../output/scripts/mace_crambin.sbatch` | Job submission script |
| Trajectory | HPC scratch (doc path in status report) | DCD format |
| Energy log | `../../output/task-001-crambin-mace.log` | CSV: step, energy, temp |
| RMSD plot | `../../output/task-001-rmsd.png` | RMSD vs time |
| Energy plot | `../../output/task-001-energy.png` | Energy vs time |
| D1 evidence | `../../output/task-001-d1-evidence.md` | Pass/fail assessment |

### Mandatory documentation

**Status report** (ALWAYS required -- non-negotiable):
Write to `../../status/task-001-status.md` using the status-report template.

**Cross-agent note** (ALWAYS required for this task):
Write to `../../../../../shared/notes/1.1-mace-crambin.md` using the cross-agent-note
template. Tag tracks: alpha-m. Set urgency based on result.

---

## Verification

Before declaring your task complete, verify each criterion:

1. [ ] Trajectory file exists and is non-empty
2. [ ] Energy log has entries spanning the full simulation time
3. [ ] No NaN values in energy/force logs
4. [ ] RMSD plot shows reasonable values (<5 A for stable protein)
5. [ ] D1 evidence report explicitly states PASS or FAIL
6. [ ] Cross-agent note exists at `shared/notes/1.1-mace-crambin.md`
7. [ ] All scripts saved for reproducibility
8. [ ] Status report written

---

## If Something Goes Wrong

1. **Do not silently fail.** If you cannot complete a step, document it.
2. Write a status report with status `blocked` or `failed`.
3. Include the exact error message or log excerpt.
4. Describe what you tried and why it did not work.
5. The D1 evidence report MUST still be written even on failure -- documented
   failure IS gate evidence.
6. A MACE failure does NOT block other tasks. SO3LR may still succeed.
7. Common issues: OpenMM-ML version mismatch, MACE model not registered,
   CUDA toolkit version, NaN forces on first minimization step.
