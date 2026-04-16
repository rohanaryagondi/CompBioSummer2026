---
task_id: "task-004"
agent: "bioemu-test"
type: "experiment-log"
date: 2026-04-16
---

# Experiment Log: BioEmu Disulfide Bond Integrity Test

## Experiment Identity

- **Task:** task-004 — BioEmu v1.3.1 disulfide bond test on BPTI + HEWL
- **Objective:** Generate 100 BioEmu conformations per protein, measure disulfide
  bond integrity using CB-CB distances, assess T3 and AK3 thresholds
- **Date:** 2026-04-15 to 2026-04-16
- **Final SLURM job:** 8371740

## Software Environment

| Component | Version |
|-----------|---------|
| bioemu | 1.3.1 |
| BioEmu model | bioemu-v1.1 |
| torch | 2.7.1+cu128 |
| tensorflow-cpu | 2.15.1 |
| protobuf | 4.25.9 |
| jax | 0.4.35 |
| mdtraj | 1.10.3 |
| Python | 3.10.20 |
| CUDA driver | 570.195.03 |
| CUDA version | 12.8 |

**Critical env vars:**
- `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python`
- `BIOEMU_EMBEDS_CACHE=/nfs/roberts/scratch/pi_mg269/rag88/.bioemu_embeds_cache`
- `HF_HOME=/nfs/roberts/scratch/pi_mg269/rag88/.hf_cache`

## Hardware

- **Node:** a1128u05n01.mghpcc.ycrc.yale.edu
- **GPU:** NVIDIA RTX 5000 Ada Generation
- **GPU memory:** 32,760 MiB (~33.8 GB)
- **Partition:** gpu_devel
- **CPUs:** 4
- **RAM requested:** 32 GB

## SLURM Job History

6 jobs were submitted across debugging iterations. Only the final job succeeded.

| Job ID | Partition | Result | Failure Reason |
|--------|-----------|--------|----------------|
| 8350490 | gpu_devel | FAILED | torch cu130 built against CUDA 13.0, cluster has CUDA 12.8 driver |
| 8352672 | gpu_devel | FAILED | `torch.cuda.get_device_properties(0).total_mem` — PyTorch 2.7 renamed to `.total_memory` |
| 8361635 | scavenge_gpu | FAILED | tensorflow-cpu 2.21.0 protobuf descriptor clash with jaxlib 0.4.35 |
| 8366491 | gpu_devel | FAILED | Same TF issue — stale 2.21 _api files remained after first reinstall |
| 8371739 | scavenge_gpu | FAILED | Likely preempted (scavenge partition) |
| **8371740** | **gpu_devel** | **SUCCESS** | — |

### Fixes Applied Between Jobs

1. **Job 8350490 → 8352672:** `pip install 'torch==2.7.1+cu128'` (downgraded from cu130)
2. **Job 8352672 → 8361635:** Fixed `.total_mem` → `.total_memory` in analysis script
3. **Job 8361635 → 8366491:** `pip install --force-reinstall 'tensorflow-cpu>=2.15,<2.16'` (downgraded from 2.21.0 to 2.15.1)
4. **Job 8366491 → 8371739:** Complete reinstall of tensorflow-cpu 2.15.1 with `--no-cache-dir` to clear stale _api modules
5. **Job 8371739 → 8371740:** Switched from scavenge_gpu to gpu_devel (non-preemptible)

## Generation Parameters

| Parameter | BPTI | HEWL |
|-----------|------|------|
| Sequence length | 57 residues | 129 residues |
| Num samples | 100 | 100 |
| Batch size | 30 | 6 |
| Model | bioemu-v1.1 | bioemu-v1.1 |
| Seed | 42 | 42 |
| Filter samples | True | True |
| Frames after filtering | 98 | 99 |
| Output atoms per residue | 5 (N, CA, C, CB, O) | 5 (N, CA, C, CB, O) |

## Timing

| Phase | BPTI | HEWL |
|-------|------|------|
| Embedding computation (AlphaFold2) | ~250 sec (includes AF2 weight download) | ~504 sec |
| Sampling (batched) | ~16 sec | ~66 sec |
| Total generation | 266.2 sec (4.4 min) | 569.8 sec (9.5 min) |
| SS distance analysis | <1 sec | <1 sec |
| **Total wall time** | **~4.5 min** | **~9.5 min** |

Generation time scales roughly with sequence length: HEWL (129 res) took ~2.1x
longer than BPTI (57 res), matching the length ratio of 2.26.

## Key Discovery: Backbone-Only Output

BioEmu v1.3.1 outputs only 5 atoms per residue: **N, CA, C, CB, O**. No sidechain
atoms (including SG for cysteine) are generated. This means:

- The task spec's SG-SG distance measurement at 2.5 A cutoff is not possible
- All SS distance measurements used **CB-CB** as proxy
- Crystallographic CB-CB distances for intact disulfide bonds are typically 3.8-4.2 A
- A 4.5 A CB-CB cutoff was used as the primary threshold (standard crystallographic value)
- Sensitivity analysis performed at 4.5, 5.0, and 5.5 A cutoffs

The analysis script detected the missing SG atoms and automatically fell back to
CB atoms with appropriate warnings logged.

## Results

### BPTI (98 conformations after filtering)

| Cutoff | Overall | Cys5-55 | Cys14-38 | Cys30-51 |
|--------|---------|---------|----------|----------|
| 4.5 A | 56.1% | 86.7% | 57.1% | 90.8% |
| 5.0 A | 67.3% | 88.8% | 67.3% | 90.8% |
| 5.5 A | 72.4% | 90.8% | 72.4% | 91.8% |

Weakest bond: Cys14-Cys38 (mean 6.44 +/- 4.63 A, range 3.26-24.59 A).

### HEWL (99 conformations after filtering)

| Cutoff | Overall | Cys6-127 | Cys30-115 | Cys64-80 | Cys76-94 |
|--------|---------|----------|-----------|----------|----------|
| 4.5 A | 70.7% | 90.9% | 97.0% | 92.9% | 88.9% |
| 5.0 A | 90.9% | 94.9% | 98.0% | 100.0% | 98.0% |
| 5.5 A | 93.9% | 97.0% | 99.0% | 100.0% | 99.0% |

Weakest bond: Cys76-Cys94 (mean 4.12 +/- 0.56 A, range 3.31-8.54 A).

## Threshold Assessment

At 4.5 A CB-CB cutoff (primary):
- **T3 (>95%):** NOT MET for either protein
- **AK3 (<80%):** TRIGGERED for BPTI (56.1%), TRIGGERED for HEWL (70.7%)

**BPTI:** AK3 triggered at all cutoffs (max 72.4% at 5.5 A). Recommend drop.
**HEWL:** Cutoff-dependent — AK3 triggered at 4.5 A (70.7%), not triggered at 5.0 A (90.9%).

## Physicality Metrics (from BioEmu)

| Metric | BPTI | HEWL |
|--------|------|------|
| CA break mean | 0.0 | 0.0 |
| CA clash mean | 17.0 | 4.0 |
| CA-CA dist mean | 3.846 A | 3.850 A |
| Clash distances mean | 15.234 | 18.800 |

## Output Artifacts

| File | Description |
|------|-------------|
| `output/task-004-bpti/topology.pdb` | BPTI topology |
| `output/task-004-bpti/samples.xtc` | BPTI 98 frames |
| `output/task-004-hewl/topology.pdb` | HEWL topology |
| `output/task-004-hewl/samples.xtc` | HEWL 99 frames |
| `output/task-004-bpti-ss-distances.csv` | BPTI per-frame CB-CB distances |
| `output/task-004-hewl-ss-distances.csv` | HEWL per-frame CB-CB distances |
| `output/task-004-bpti-ss-plot.png` | BPTI distance distribution plot |
| `output/task-004-hewl-ss-plot.png` | HEWL distance distribution plot |
| `output/task-004-combined-ss-histogram.png` | Combined histogram |
| `output/task-004-ss-integrity-report.md` | Full threshold assessment report |
| `output/task-004-results.json` | Raw results JSON |
| `output/task-004-bioemu-analysis.py` | Analysis script |
| `output/task-004-bioemu-slurm.sh` | SLURM job script |
| `output/task-004-bioemu-8371740.log` | Successful job stdout |
| `output/task-004-bioemu-8371740.err` | Successful job stderr |
