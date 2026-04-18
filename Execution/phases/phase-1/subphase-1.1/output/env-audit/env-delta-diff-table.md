---
subphase: "1.1"
topic: "env-delta-audit-diff"
date: 2026-04-17
source_file: phases/phase-0/subphase-0.1/envs/env-delta.yml
observed_env: env-delta (after Sub 1.1 task-006 CPA install)
---

# env-delta Diff: Baseline (phase-0 yml) vs. Observed (post-CPA install)

## Scope

Compare packages pinned in `phases/phase-0/subphase-0.1/envs/env-delta.yml`
(exported BEFORE the task-006 CPA install) against the current installed versions
in the live `env-delta` conda environment.

## Methodology

- `conda list -n env-delta > env-delta-current-list.txt` (326 packages observed)
- `conda list -n env-delta --explicit > env-delta-current-explicit.txt`
- Cross-referenced against the 29 pip entries in `env-delta.yml` (lines 33-60)

## Packages with Changed Versions (Downgrades / Upgrades)

| Package | env-delta.yml (baseline) | Observed (current) | Direction | Likely cause |
|---|---|---|---|---|
| **numpy** | 2.2.6-ish (observed on task-004) | **1.23.5** | **DOWNGRADE** | **CPA pin (task-006)** |
| **anndata** | 0.11.4 | **0.9.2** | **DOWNGRADE** | **CPA pin (task-006)** |
| **scanpy** | 1.11.5 | **1.10.2** | **DOWNGRADE** | **CPA pin (task-006)** |
| numba | 0.65.0 | 0.58.1 | downgrade | CPA transitive (numba-llvm pinning) |
| llvmlite | 0.47.0 | 0.41.1 | downgrade | numba 0.58 compat |
| umap-learn | 0.5.12 | 0.5.7 | downgrade | CPA transitive |
| scikit-learn | not in yml | 1.5.1 | pip-added | required by CPA/GEARS |
| scipy | not in yml | 1.15.3 | pip-added | required by GEARS/scGPT/CPA |
| pandas | not in yml | 2.2.2 | pip-added | CPA/GEARS/scGPT |
| torch | not in yml | 2.11.0+cu128 (also 2.4.1+cu124 ghost entry) | pip-added | GEARS/scGPT install; CPA tried to pin torch<=2.0.1 then task-006 restored 2.11.0 |
| pyarrow | not in yml | 14.0.2 | pip-added | downgraded by CPA for ray 2.9 |
| ray | not in yml | 2.9.3 | pip-added | CPA ray dep |
| pytorch-lightning | not in yml | 1.9.5 | pip-added | CPA (OLD lightning) |
| lightning | not in yml | 2.2.5 | pip-added | scGPT (NEW lightning) |
| torchmetrics | not in yml | 1.9.0 | pip-added | scGPT |
| torch-geometric | not in yml | 2.5.3 | pip-added | GEARS |
| networkx | not in yml (pip didn't pin; task-004 wanted 3.2.1) | 3.4.2 | upgrade | scGPT/other |
| cell-gears | not in yml | 0.0.2 | pip-added | GEARS |
| cpa-tools | not in yml | 0.8.8 | pip-added | CPA |
| scgpt | not in yml | 0.2.4 | pip-added | scGPT |
| datasets | not in yml | 2.21.0 | pip-added | scGPT transitive |
| h5py | 3.16.0 | 3.16.0 | same | — |
| scdataset | 0.3.0 | 0.3.0 | same | — |
| pynndescent | 0.6.0 | 0.6.0 | same | — |
| patsy | 1.0.2 | 1.0.2 | same | — |
| legacy-api-wrap | 1.5 | 1.5 | same | — |

## Critical Observations

1. **Three CPA-forced downgrades are the load-bearing conflict with Sub 1.2 tools.**
   - `numpy 1.23.5` vs. Tahoe-x1 requires scanpy>=1.9 but will also pull modern numpy.
     Modern scFoundation/Tahoe-x1 workflows typically use numpy>=1.26 or >=2.0.
   - `anndata 0.9.2` is OLD. Sub 1.2 tools that use recent `AnnData.obsm['X_pca']`
     APIs (scFoundation preprocessing) may fail.
   - `scanpy 1.10.2` is outside Tahoe-x1's explicit `scanpy>=1.9.0,<2.0` range but
     on the LOW end. Minor risk.

2. **Two conflicting lightning versions coexist:**
   - `pytorch-lightning 1.9.5` (legacy CPA API)
   - `lightning 2.2.5` (scGPT API)
   This is fragile but functional — Python will resolve to whichever `import` line
   uses. In env-delta-v2, keep only the new `lightning` package.

3. **torch 2.11+cu128 is the required build on this cluster.** McCleary driver
   570.195 is CUDA 12.8. Default pip now ships torch `cu130` wheels, which will
   FAIL with `CUDA initialization: NVIDIA driver is too old (found 12080)`.
   Must install torch with `pip install torch==2.11.0 --index-url
   https://download.pytorch.org/whl/cu128`. This was the single CRITICAL
   gotcha during env-delta-v2 build.
   scFoundation and Tahoe-x1 may ship wheels only for torch 2.4–2.6 (cu121/cu124).
   Keep torch 2.11 in env-delta-v2 for GEARS/scGPT parity. Tahoe-x1 may
   eventually need env-tahoex1 with torch 2.5+cu124.

4. **CPA's hard-floor downgrades ARE the reason CPA must live in env-cpa.**
   The CPA maintainers have not updated pins since 2023 (task-006 status).

## Recommendation

- Keep env-delta as-is (working CPA, working GEARS, working scGPT) as rollback.
- Build env-delta-v2 from `env-delta-clean.yml` for Sub 1.2 (scFoundation, Tahoe-x1).
- Build env-cpa from `env-cpa.yml` for any future CPA training in Sub 1.2+.
- After env-delta-v2 is validated with GEARS smoke test, the HeadAI for Sub 1.2
  should activate env-delta-v2 for all new work.
