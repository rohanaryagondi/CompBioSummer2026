---
task_id: "task-001"
title: "Create 9 Conda Environments + Export Pinned YAMLs"
subphase: "0.1"
track: infrastructure
wave: 1
agent: "env-builder"
effort: "2-3 days"
status: planned
created: 2026-04-15
---

# Task 001: Create 9 Conda Environments + Export Pinned YAMLs

## Objective

Create all 9 project conda environments with exact version pins, verify each works
with a smoke test, export reproducible YAML files, and confirm HPC cluster access
(SLURM partitions, GPU nodes, scratch storage). This task establishes the software
foundation for every subsequent experiment across all three tracks.

---

## Context

The Implementation Plan (Section 15.1) specifies 9 separate conda environments to
isolate incompatible dependency chains (e.g., MACE uses PyTorch while SO3LR uses JAX).
Phase 1 begins May 1 and requires all environments ready on Day 1. The env-bioemu
environment is the highest priority because it blocks task-004 (BioEmu disulfide test)
in Wave 2 of this subphase. The env-mace and env-so3lr environments are high risk
(15-20% failure probability) and their build results inform the D1 gate (May 9).

---

## Detailed Instructions

### Pre-step: Verify HPC Access

1. Confirm SLURM is accessible: `sinfo` to list partitions
2. Identify partitions with H200, RTX 5000 Ada, and B200 GPUs
3. Submit a trivial test job (1 minute, any partition): `sbatch --wrap="hostname && nvidia-smi" --time=00:01:00 --gres=gpu:1`
4. Verify scratch storage: `df -h /scratch` (or equivalent HPC scratch path). Confirm ≥10 TB available.
5. Check CUDA toolkit: `nvcc --version` or `module avail cuda`
6. Document: partition names, GPU types per partition, CUDA version, scratch path, available space

### Environment Build Order (priority-first)

Build each environment sequentially. For each environment:
- `conda create -n <env-name> python=<version> -y`
- Install packages with exact version pins where known
- Run a smoke test (import key packages, run a trivial operation)
- If smoke test passes: `conda env export --no-builds > envs/env-<name>.yml`
- If smoke test fails: document the error, attempt to fix, document resolution or failure

**Priority 1 — env-bioemu (Wave 2 blocker):**
- Python 3.10+
- PyTorch (latest stable, CUDA-compatible)
- BioEmu v1.3.1 (`pip install bioemu` or from GitHub)
- Smoke test: `python -c "from bioemu import BioEmuSampler; print('BioEmu OK')"`

**Priority 2 — env-delta (Phase 1 Delta track):**
- Python 3.10+
- PyTorch, scanpy, anndata, scDataset
- scGPT dependencies, GEARS dependencies, CPA dependencies
- Smoke test: `python -c "import scanpy, anndata, torch; print('Delta OK')"`

**Priority 3 — env-mace (D1 gate critical, 15% failure risk):**
- Python 3.10+
- PyTorch, mace-torch, OpenMM, OpenMM-ML
- Smoke test: `python -c "import mace; from openmm import app; print('MACE OK')"`
- If build fails: document exact error. Write cross-agent note for D1 gate.

**Priority 4 — env-so3lr (D1 gate critical, 20% failure risk):**
- Python 3.10+
- JAX with CUDA support, JAX-MD, SO3LR
- Smoke test: `python -c "import jax; import jax_md; print('SO3LR OK, JAX devices:', jax.devices())"`
- If build fails: document exact error (common issue: JAX/CUDA version mismatch). Write cross-agent note for D1 gate.

**Priority 5 — env-classical:**
- Python 3.10+
- OpenMM (latest stable), ParmEd, AmberTools (via conda-forge)
- Force fields: AMBER ff14SB, ff19SB, a99SB-disp, CHARMM36m (bundled with OpenMM)
- Smoke test: `python -c "from openmm import app; from openmm.app import ForceField; ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml'); print('Classical OK')"`

**Priority 6 — env-garnet:**
- Python 3.10+
- PyTorch, Garnet (from GitHub if not on PyPI)
- OpenMM integration
- Smoke test: `python -c "import garnet; print('Garnet OK')"`

**Priority 7 — env-boltz:**
- Python 3.10+
- PyTorch, Boltz-2
- Smoke test: `python -c "import boltz; print('Boltz OK')"`

**Priority 8 — env-alphaflow:**
- Python 3.10+
- PyTorch, AlphaFlow
- Smoke test: `python -c "import alphaflow; print('AlphaFlow OK')"`

**Priority 9 — env-analysis:**
- Python 3.10+
- MDAnalysis, MDTraj, NumPy, SciPy, scikit-learn, matplotlib, seaborn
- SPARTA+ (external binary, check if available via module or manual install)
- Pepsi-SAXS (external binary)
- Smoke test: `python -c "import mdanalysis, mdtraj, numpy, scipy; print('Analysis OK')"`

### Final Step: Export and Organize

1. Create `envs/` directory in the repository root (or appropriate location)
2. Export all successful environments: `conda env export --no-builds > envs/env-<name>.yml`
3. Create a summary table documenting each environment's status (success/failure), Python version, key package versions, and any issues encountered

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| `../../../../Proposal/ImplementationPlan.md` (Section 15.1) | Environment specifications and version requirements |
| `../../../../Proposal/Alpha-M.md` (Section 3) | Generator-specific software dependencies |
| `../../../../Proposal/Delta.md` (Section 4) | DL framework dependencies for perturbation methods |
| `../../../../context/mission-briefing.md` | HPC specs: GPU types, partitions, module system |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../Proposal/Gamma.md` | BioEmu-specific version requirements |
| `../../../../Proposal/Combined-Alpha-Gamma.md` | Cross-track dependency notes |

### DO NOT READ

- `../../../../Proposal/HumanOnlyProposal.md` -- off-limits to all AI agents
- Any files in `../../../../Cohort1/`, `../../../../Cohort2/`, `../../../../ReviewCohort/` -- ideation pipeline, not needed
- Other SubAgent task specs in `../tasks/` -- not your scope

---

## Output Artifacts

### Code and data artifacts

| Artifact | Path | Format |
|----------|------|--------|
| env-bioemu YAML | `envs/env-bioemu.yml` | Conda YAML |
| env-delta YAML | `envs/env-delta.yml` | Conda YAML |
| env-mace YAML | `envs/env-mace.yml` | Conda YAML |
| env-so3lr YAML | `envs/env-so3lr.yml` | Conda YAML |
| env-classical YAML | `envs/env-classical.yml` | Conda YAML |
| env-garnet YAML | `envs/env-garnet.yml` | Conda YAML |
| env-boltz YAML | `envs/env-boltz.yml` | Conda YAML |
| env-alphaflow YAML | `envs/env-alphaflow.yml` | Conda YAML |
| env-analysis YAML | `envs/env-analysis.yml` | Conda YAML |
| HPC access report | `output/task-001-hpc-access.md` | Markdown |
| Environment summary | `output/task-001-env-summary.md` | Markdown |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-001-status.md` | `status-report.md` |
| Cross-agent note (env-mace) | `../../../../../../shared/notes/0.1-env-mace-build.md` | `cross-agent-note.md` |
| Cross-agent note (env-so3lr) | `../../../../../../shared/notes/0.1-env-so3lr-build.md` | `cross-agent-note.md` |

---

## Success Criteria (Zero Compromise)

This task is complete ONLY if ALL of the following are true:

1. [ ] All 9 conda environments created (or failure documented for each that could not be built)
2. [ ] Each successful environment passes its smoke test
3. [ ] Each successful environment exported as a pinned YAML file
4. [ ] SLURM test job completed successfully (confirms cluster access)
5. [ ] Scratch storage confirmed ≥10 TB available
6. [ ] Cross-agent note written for env-mace build result (success or failure) with details
7. [ ] Cross-agent note written for env-so3lr build result (success or failure) with details
8. [ ] Environment summary document created listing all 9 environments with status, versions, and issues
9. [ ] Status report written to `../../status/task-001-status.md`

---

## Verification

Before declaring this task complete, verify:

1. `conda env list` shows all 9 environment names
2. Each YAML file exists at `envs/env-<name>.yml` and is non-empty
3. For each environment: `conda activate <name> && python -c "<smoke test>"` exits with code 0
4. SLURM test job log shows GPU detected (nvidia-smi output present)
5. Cross-agent notes exist at `shared/notes/0.1-env-mace-build.md` and `shared/notes/0.1-env-so3lr-build.md`

---

## Failure Protocol

If this task cannot be completed:

1. Write a status report with status `failed` or `blocked`
2. Document exactly what went wrong (error messages, log excerpts)
3. Document what was tried and why it did not work
4. Identify what help is needed for the HeadAI to resolve or escalate
5. DO NOT silently skip steps or lower the success criteria
6. **Critical:** Even if some environments fail, complete ALL environments that CAN be built. A partial success (e.g., 7 of 9 environments) is far more valuable than stopping at the first failure.
