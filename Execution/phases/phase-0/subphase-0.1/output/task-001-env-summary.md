---
task_id: "task-001"
agent: "env-builder"
type: "environment-summary"
date: 2026-04-15
---

# Environment Summary: All 9 Conda Environments

## Overview

All 9 environments built successfully, smoke-tested, and exported as pinned YAML
files to `envs/`. Build time: ~2.5 hours total.

## Environment Table

| # | Environment | Python | Key Package | Version | Backend | Smoke Test | YAML |
|---|-------------|--------|-------------|---------|---------|------------|------|
| 1 | env-bioemu | 3.10 | bioemu | 1.3.1 | PyTorch 2.7.1+cu128 | PASS | `envs/env-bioemu.yml` |
| 2 | env-delta | 3.10 | datasets, huggingface_hub | 3.6.0, 0.30.2 | PyTorch | PASS | `envs/env-delta.yml` |
| 3 | env-mace | 3.10 | mace-torch | 0.3.15 | PyTorch | PASS | `envs/env-mace.yml` |
| 4 | env-so3lr | 3.12 | so3lr | 0.1.0 | JAX 0.5.3 | PASS | `envs/env-so3lr.yml` |
| 5 | env-classical | 3.10 | openmm | 8.2.0 | — | PASS | `envs/env-classical.yml` |
| 6 | env-garnet | 3.12 | garnetff | 0.1.0 | PyTorch | PASS | `envs/env-garnet.yml` |
| 7 | env-boltz | 3.10 | boltz | installed | PyTorch | PASS | `envs/env-boltz.yml` |
| 8 | env-alphaflow | 3.10 | alphaflow | installed | PyTorch | PASS | `envs/env-alphaflow.yml` |
| 9 | env-analysis | 3.10 | mdanalysis | 2.9.0 | — | PASS | `envs/env-analysis.yml` |

**Result: 9/9 PASS**

## Notable Build Issues

### env-bioemu (Priority 1)

- **API discrepancy:** Task spec referenced `from bioemu import BioEmuSampler` — this
  class does not exist. Correct API: `from bioemu.sample import main(sequence,
  num_samples, output_dir, ...)`.
- **Model names:** Available models are `bioemu-v1.0`, `bioemu-v1.1`, `bioemu-v1.2`
  (not v1.3.1 despite the package version being 1.3.1).
- **Critical dependency chain:** torch 2.7.1+cu128, tensorflow-cpu 2.15.1,
  protobuf 4.25.9, jax 0.4.35. The vendored AlphaFold2 code inside BioEmu imports
  tensorflow, which creates a protobuf descriptor clash with jaxlib unless TF is
  pinned to 2.15.x (not 2.16+).
- **ColabFold inlined:** BioEmu has inlined ColabFold; no separate installation needed.
  First run requires internet access from compute nodes for MSA server queries.
  Subsequent runs use `cache_embeds_dir`.
- **Env var needed:** `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` avoids C++
  protobuf crash at runtime.

### env-so3lr (Priority 4)

- **Python 3.12 required** (task spec assumed 3.10).
- **JAX backend** (not PyTorch). Uses JAX 0.5.3.
- **Install from GitHub:** `pip install git+https://github.com/general-molecular-simulations/so3lr.git`
  (not on PyPI).

### env-garnet (Priority 6)

- **Package name:** `garnetff` on PyPI (not `garnet`).
- **Python 3.12 required.**
- **conda-forge dependencies:** openff-toolkit-base, rustworkx, rdkit, openmm,
  pyxdg, gemmi.
- **Additional pip:** openff-pablo from GitHub.
- **LD_LIBRARY_PATH hook:** Required for GLIBCXX_3.4.29. Activation hook created at
  `$CONDA_PREFIX/etc/conda/activate.d/env_vars.sh`.

### env-analysis (Priority 9)

- **Warning:** RDKit numpy version conflict (user site-packages has rdkit compiled
  against numpy 1.x, env has numpy 2.x). Cosmetic warning only; imports succeed.

## D1 Gate Implications

Both MLFF environments (env-mace and env-so3lr) built successfully:
- **env-mace:** mace-torch 0.3.15, PyTorch backend — ready for MACE-OFF24 pilot
- **env-so3lr:** SO3LR 0.1.0, JAX 0.5.3 backend — ready for SO3LR pilot

**D1 preliminary signal: POSITIVE.** Software installation hurdle cleared.

## Phase 1 Guidance

1. **Do NOT modify env-bioemu pinned versions** — the dependency chain is fragile.
2. **env-so3lr tasks must account for JAX** — different GPU memory management and
   JIT compilation overhead compared to PyTorch.
3. **env-garnet requires conda activate** with LD_LIBRARY_PATH hook — scripts must
   source the activation hook or use `conda run`.
4. **BioEmu tasks must set** `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` and
   provide `cache_embeds_dir` parameter.
