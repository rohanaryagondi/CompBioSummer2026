---
task_id: "task-001"
agent: "env-builder"
type: "hpc-access-report"
date: 2026-04-15
---

# HPC Access Report

## SLURM Cluster

- **Scheduler:** SLURM
- **Login node:** mghpcc.ycrc.yale.edu
- **CUDA driver:** 570.195.03 (CUDA 12.8) on compute nodes; no GPU on login nodes

## GPU Partitions

| Partition | GPU Type | GPUs/Node | CPUs/Node | Memory/Node | Notes |
|-----------|----------|-----------|-----------|-------------|-------|
| gpu_h200 | H200 | 8 | 48 | ~2 TB | Production |
| gpu_b200 | B200 | 8 | 128 | ~2.3 TB | Production |
| gpu | RTX 5000 Ada | 4 | 48 | ~490 GB | Default GPU partition |
| gpu_devel | H200 + RTX 5000 Ada | varies | varies | varies | Development / testing |
| gpu_rtx6000 | RTX Pro 6000 Blackwell | 8 | 128 | ~2.3 TB | Blackwell generation |
| scavenge_gpu | L40S, H200, RTX 5000 Ada | varies | varies | varies | Preemptible |
| priority_gpu | All types | varies | varies | varies | Priority access |

**GPU naming discrepancy:** The proposal documents reference "RTX 5000 Ada" GPUs.
The actual cluster GRES name is `rtx_5000_ada` (32,760 MiB / ~33.8 GB VRAM).
The SLURM test job (8344719) confirmed the full name is "NVIDIA RTX 5000 Ada Generation."
There are no "RTX 5090" GPUs despite earlier reports — the GRES label `rtx_50` was
misread. The correct name is RTX 5000 Ada Generation.

## CPU Partitions

| Partition | CPUs/Node | Memory/Node | Notes |
|-----------|-----------|-------------|-------|
| day (default) | 64 | ~1 TB | 24-hour default |
| week | 64 | ~1 TB | 7-day jobs |
| bigmem | 64 | ~4 TB | High-memory nodes |
| devel | 64 | ~1 TB | Development |
| mpi | 64 | ~500 GB | MPI workloads |
| day_amd | 128 | ~2.3 TB | AMD nodes |
| priority | 64 | ~1 TB | Priority access |

## Scratch Storage

- **Path:** `/nfs/roberts/scratch/pi_mg269/rag88/`
- **Filesystem:** NFS, 10 TB total allocation
- **Available at time of check:** 8.8 TB (13% used)
- **Sufficient for:** Tahoe-100M (~429 GB) + all experiment data

## SLURM Test Job

- **Job ID:** 8344719
- **Partition:** gpu_devel
- **Node:** a1128u08n01.mghpcc.ycrc.yale.edu
- **GPU detected:** NVIDIA RTX 5000 Ada Generation, 32,760 MiB VRAM
- **CUDA driver:** 570.195.03, CUDA 12.8
- **Status:** COMPLETED

```
nvidia-smi output:
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 570.195.03             Driver Version: 570.195.03     CUDA Version: 12.8     |
|   0  NVIDIA RTX 5000 Ada Gene...    On  |   00000000:BD:00.0 Off |                  Off |
| 30%   36C    P8             18W /  250W |       2MiB /  32760MiB |      0%      Default |
+-----------------------------------------------------------------------------------------+
```

## QOS Limits

- Max 2 pending jobs per user (observed during task-004 SLURM submissions)
- `week` partition has low scheduling priority (task-002 SLURM job 8346038 never started)

## Module System

- `module load miniconda/24.11.3` — primary conda activation path
- Conda profile: `/apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh`
