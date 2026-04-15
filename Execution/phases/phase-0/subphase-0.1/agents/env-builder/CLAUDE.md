# SubAgent: Create 9 Conda Environments

You are a **SubAgent** executing task-001 in subphase 0.1 of the CompBioSummer2026
execution pipeline. You have a narrowly scoped task with explicit success criteria.
Execute your task, write your documentation, and report your results.

---

## Your Task

**Task ID:** task-001
**Title:** Create 9 conda environments + export pinned YAMLs
**Track:** Infrastructure
**Subphase:** 0.1
**Estimated effort:** 2-3 days

---

## What You Must Accomplish (Zero Compromise)

1. Verify HPC access: SLURM partitions reachable, GPU test job completes, scratch ≥10 TB
2. Create all 9 conda environments (env-bioemu, env-delta, env-mace, env-so3lr, env-classical, env-garnet, env-boltz, env-alphaflow, env-analysis)
3. Each successful environment passes its smoke test (import key packages)
4. Export each successful environment as a pinned YAML file to `envs/env-<name>.yml`
5. Write cross-agent notes for env-mace and env-so3lr build results (success or failure)
6. Write status report to `../../status/task-001-status.md`

**CRITICAL:** Build env-bioemu FIRST. It blocks task-004 in Wave 2. After env-bioemu
passes its smoke test, continue building the remaining 8 environments in priority order.

---

## What You Read

### MUST READ (before starting)

| File | Why |
|------|-----|
| `../../tasks/task-001-env-setup.md` | Your full task specification with detailed build instructions |
| `../../../../../Proposal/ImplementationPlan.md` (Section 15.1) | Environment specs and version requirements |
| `../../../../../Proposal/Alpha-M.md` (Section 3) | Generator-specific software: MACE, SO3LR, Garnet, BioEmu, Boltz-2, AlphaFlow, OpenMM |
| `../../../../../Proposal/Delta.md` (Section 4) | DL framework dependencies: scGPT, GEARS, CPA, scFoundation |
| `../../../../../context/mission-briefing.md` | HPC specs: GPU types, partitions, module system |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../Proposal/Gamma.md` | BioEmu version requirements |

### DO NOT READ

- Other SubAgents' task specs in `../../tasks/` (not your scope)
- Other SubAgents' output in `../../output/` (unless listed as a dependency)
- Phase plans or subphase plans (your HeadAI manages the orchestration)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)

---

## Detailed Instructions

### Pre-step: HPC Access Verification

1. Run `sinfo` to list SLURM partitions. Record partition names and GPU types.
2. Run `squeue -u $USER` to confirm job submission works.
3. Submit test job: `sbatch --wrap="hostname && nvidia-smi" --time=00:01:00 --gres=gpu:1 -p <partition>`
4. Wait for job completion. Verify nvidia-smi output shows GPU.
5. Check scratch space: `df -h $SCRATCH` (or equivalent). Verify ≥10 TB available.
6. Check CUDA: `nvcc --version` or `module avail cuda`. Record CUDA version.
7. Write HPC access findings to `output/task-001-hpc-access.md`.

### Environment Build (priority order)

Build each environment sequentially. For EACH environment:

```bash
conda create -n <env-name> python=3.10 -y
conda activate <env-name>
# Install packages (see task spec for specific packages per env)
# Run smoke test
conda deactivate
conda env export --no-builds -n <env-name> > envs/env-<name>.yml
```

**Build order:**
1. env-bioemu (FIRST — Wave 2 blocker)
2. env-delta
3. env-mace (D1 gate — write cross-agent note regardless of outcome)
4. env-so3lr (D1 gate — write cross-agent note regardless of outcome)
5. env-classical
6. env-garnet
7. env-boltz
8. env-alphaflow
9. env-analysis

If an environment build fails:
- Document the exact error message
- Try at least one alternative approach (different version, different install order)
- If still fails: mark as failed, document what was tried, continue to next environment
- DO NOT stop building remaining environments because one failed

### Final: Environment Summary

Create `output/task-001-env-summary.md` with a table:

| Environment | Status | Python | Key Packages | Issues |
|-------------|--------|--------|-------------|--------|
| env-bioemu | success/failed | 3.10.x | BioEmu 1.3.1, PyTorch X.Y | none |
| ... | ... | ... | ... | ... |

---

## What You Write

### Code and data artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| 9 environment YAMLs | `envs/env-<name>.yml` | Pinned conda environment exports |
| HPC access report | `output/task-001-hpc-access.md` | SLURM partitions, GPU types, CUDA version, scratch space |
| Environment summary | `output/task-001-env-summary.md` | Status table for all 9 environments |

### Mandatory documentation

**Status report** (ALWAYS required -- non-negotiable):
Write to `../../status/task-001-status.md` using the status-report template.

**Cross-agent notes** (ALWAYS required for env-mace and env-so3lr):
- `../../../../../../shared/notes/0.1-env-mace-build.md` — success or failure details
- `../../../../../../shared/notes/0.1-env-so3lr-build.md` — success or failure details

---

## Verification

Before declaring your task complete, verify each criterion:

1. [ ] `sinfo` output recorded; test SLURM job completed
2. [ ] `conda env list` shows all 9 environment names
3. [ ] `ls envs/env-*.yml` shows 9 YAML files (or fewer if some envs failed)
4. [ ] Each environment activates without error: `conda activate <name>`
5. [ ] Each environment passes smoke test: `python -c "<import check>"`
6. [ ] Cross-agent notes exist at `shared/notes/0.1-env-mace-build.md` and `0.1-env-so3lr-build.md`
7. [ ] Status report written

---

## If Something Goes Wrong

1. **Do not silently fail.** If you cannot complete a step, document it.
2. Write a status report with status `blocked` or `failed`.
3. Include the exact error message or log excerpt.
4. Describe what you tried and why it did not work.
5. Suggest what might fix the issue (if you have ideas).
6. Your HeadAI will read your status report and decide next steps.
