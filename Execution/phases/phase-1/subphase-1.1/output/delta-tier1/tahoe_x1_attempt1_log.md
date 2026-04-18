# Tahoe-x1 Install Attempt 1: env-delta-v2 — FAILED (flash-attn)

Date: 2026-04-17
Env: env-delta-v2 (torch 2.11.0+cu128, Python 3.10.20)

## Commands attempted
```bash
conda activate env-delta-v2
export PYTHONNOUSERSITE=1
pip install tahoe-x1 --no-build-isolation --dry-run
```

## Failure mode
`tahoe-x1` pulls `llm-foundry[gpu]>=0.17.1,<1.0` which pins
`flash-attn==2.7.4.post1`. Attempting to resolve flash-attn 2.7.4.post1:

1. PyPI sdist only (no wheel) — build from source needed.
2. Build fails on CPU login node: `OSError: CUDA_HOME environment variable
   is not set`, and earlier `ModuleNotFoundError: No module named 'torch'`
   under default `--build-isolation`.
3. Prebuilt wheels from the flash-attn GitHub release exist only for
   torch 2.2/2.3/2.4/2.5/2.6/2.7 + cu12 (cu121 binary, `cxx11abiFALSE/TRUE`).
   There is NO torch 2.11 wheel, nor a cu128 wheel.

## Root cause
flash-attn 2.7.4.post1 prebuilt-wheel matrix (from
https://github.com/Dao-AILab/flash-attention/releases/tag/v2.7.4.post1 —
50 assets, confirmed via GitHub API):

| torch | CUDA | cxx11 FALSE | cxx11 TRUE |
|-------|------|-------------|------------|
| 2.2 | cu12 | yes | yes |
| 2.3 | cu12 | yes | yes |
| 2.4 | cu12 | yes | yes |
| 2.5 | cu12 | yes | yes |
| 2.6 | cu12 | yes | yes |
| 2.7 | cu12 | yes | yes |
| **2.11** | **cu128** | **NO** | **NO** |

env-delta-v2 has torch 2.11.0+cu128, which is outside this matrix.

## Decision
Do NOT force-build flash-attn against torch 2.11 (ABI mismatch risk, multi-hour
nvcc compile on a GPU node). Do NOT downgrade torch in env-delta-v2 (would
break the modern-stack invariant that unblocks GEARS/scGPT/scFoundation).

Proceed to Deliverable 3: create a dedicated `env-tahoex1` conda env pinned to
torch 2.5 + cu121 (flash-attn 2.7.4.post1 has prebuilt cu12torch2.5 wheels).
Driver 570.195 (CUDA 12.8) is forward-compatible with cu121 binaries.
