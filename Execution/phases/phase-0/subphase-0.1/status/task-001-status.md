---
task_id: "task-001"
agent: "env-builder"
status: completed
started: 2026-04-15T15:00:00Z
completed: 2026-04-15T17:30:00Z
---

# Task 001 Status Report: Create 9 Conda Environments + Export Pinned YAMLs

## Summary

All 9 conda environments successfully created, smoke-tested, and exported as
pinned YAML files. HPC access verified (SLURM partitions, scratch storage).
GPU test job submitted but still pending priority at time of writing.

## Environment Build Results

| # | Environment | Python | Key Package | Version | Smoke Test | YAML Exported |
|---|-------------|--------|-------------|---------|------------|---------------|
| 1 | env-bioemu | 3.10 | bioemu | 1.3.1 | PASS | Yes |
| 2 | env-delta | 3.10 | datasets, huggingface_hub | 3.6.0, 0.30.2 | PASS | Yes |
| 3 | env-mace | 3.10 | mace-torch | 0.3.15 | PASS | Yes |
| 4 | env-so3lr | 3.12 | so3lr | 0.1.0 | PASS | Yes |
| 5 | env-classical | 3.10 | openmm | 8.2.0 | PASS | Yes |
| 6 | env-garnet | 3.12 | garnetff | 0.1.0 | PASS | Yes |
| 7 | env-boltz | 3.10 | boltz | installed | PASS | Yes |
| 8 | env-alphaflow | 3.10 | alphaflow | installed | PASS | Yes |
| 9 | env-analysis | 3.10 | mdanalysis, scipy, scikit-learn | 2.9.0, 1.15.2, 1.7.0 | PASS | Yes |

**All 9/9 environments: PASS**

## Notable Build Issues and Resolutions

### env-bioemu
- **Issue:** `from bioemu import BioEmuSampler` (from task spec) does not exist.
  Actual API: `from bioemu.sample import main`.
- **Resolution:** Smoke test adjusted. API confirmed: `main(sequence, num_samples, output_dir, ...)`.
  Model names are `bioemu-v1.0`, `bioemu-v1.1`, `bioemu-v1.2` (not v1.3.1 despite package version).

### env-so3lr
- **Issue:** SO3LR requires Python >= 3.12 (initially tried 3.10). Also requires
  installation from GitHub, not PyPI.
- **Resolution:** Created with Python 3.12. Installed via
  `pip install git+https://github.com/general-molecular-simulations/so3lr.git`.
  Uses JAX 0.5.3 backend (not PyTorch).

### env-garnet
- **Issue:** Package name is `garnetff` (not `garnet`). Requires Python 3.12,
  conda-forge dependencies (openff-toolkit-base, rustworkx, rdkit, openmm, pyxdg, gemmi),
  plus openff-pablo from GitHub. Also needed `libstdcxx-ng` for GLIBCXX_3.4.29
  and LD_LIBRARY_PATH activation hook.
- **Resolution:** Full install completed. Activation hook created at
  `$CONDA_PREFIX/etc/conda/activate.d/env_vars.sh` to set LD_LIBRARY_PATH.

### env-analysis
- **Warning:** RDKit numpy version conflict warnings (user site-packages has rdkit
  compiled against numpy 1.x, env has numpy 2.x). Cosmetic only -- imports succeed.

## HPC Access Verification

### SLURM Partitions

| Partition | GPU Type | GPUs/Node | Time Limit | Status |
|-----------|----------|-----------|------------|--------|
| gpu_h200 | H200 | 8 | infinite | Available |
| gpu_b200 | B200 | 8 | infinite | Available |
| gpu (default) | RTX 5090 | varies | infinite | Available |
| gpu_rtx6000 | RTX 6000 Ada | varies | infinite | Available |
| gpu_devel | H200, RTX 5090 | 8 | infinite | Available |
| scavenge_gpu | H200, RTX 5090, L40S | varies | infinite | Available |
| priority_gpu | All types | varies | infinite | Available |
| education_gpu | RTX 5090 | varies | 1 day | Available |

**Note:** The task spec mentioned "RTX 5000 Ada" -- the actual GPU name on this
cluster is "RTX 5090" (rtx_50 GRES). No "RTX 5000 Ada" partition exists.
H200 and B200 are confirmed available.

### Scratch Storage

- **Path:** `/nfs/roberts/scratch/pi_mg269/rag88/`
- **Filesystem:** 10 TB total, 9.2 TB available (9% used)
- **Status:** Sufficient for Tahoe-100M (~429 GB) and all experiment data

### GPU Test Job

- **Job ID:** 8348898
- **Partition:** gpu_devel
- **Status:** PENDING (Priority) at time of writing
- **Note:** Login nodes have CUDA driver 12080; GPU nodes expected to have newer drivers.
  PyTorch CUDA warnings on login node are expected and non-blocking.

## Output Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| env-bioemu.yml | `envs/env-bioemu.yml` | Created |
| env-delta.yml | `envs/env-delta.yml` | Created |
| env-mace.yml | `envs/env-mace.yml` | Created |
| env-so3lr.yml | `envs/env-so3lr.yml` | Created |
| env-classical.yml | `envs/env-classical.yml` | Created |
| env-garnet.yml | `envs/env-garnet.yml` | Created |
| env-boltz.yml | `envs/env-boltz.yml` | Created |
| env-alphaflow.yml | `envs/env-alphaflow.yml` | Created |
| env-analysis.yml | `envs/env-analysis.yml` | Created |

## Success Criteria Assessment

- [x] All 9 conda environments created and smoke-tested
- [x] All 9 pinned YAML files exported to `envs/`
- [x] SLURM partition access verified (sinfo confirms all GPU partitions)
- [x] HPC scratch quota confirmed >= 10 TB (9.2 TB available)
- [x] GPU test job submitted (8348898, pending priority)
- [x] env-mace build: SUCCESS (cross-agent note written)
- [x] env-so3lr build: SUCCESS (cross-agent note written)

## Cross-Agent Notes Generated

1. `shared/notes/0.1-env-mace-build.md` -- env-mace SUCCESS, positive D1 signal
2. `shared/notes/0.1-env-so3lr-build.md` -- env-so3lr SUCCESS, requires Python 3.12 + JAX

## Recommendations for Future Phases

1. **BioEmu API:** Use `from bioemu.sample import main`, not `BioEmuSampler`. Task-004
   spec should reference this corrected API.
2. **Garnet:** Package is `garnetff` on PyPI. Requires LD_LIBRARY_PATH activation hook.
   Phase 1 Garnet tasks should note this dependency.
3. **SO3LR + JAX:** env-so3lr uses JAX, not PyTorch. Phase 1 SO3LR tasks must account
   for JAX-specific GPU memory management and compilation overhead.
4. **GPU naming:** Cluster has RTX 5090 (not "RTX 5000 Ada" as in proposals). Update
   references in future task specs.
