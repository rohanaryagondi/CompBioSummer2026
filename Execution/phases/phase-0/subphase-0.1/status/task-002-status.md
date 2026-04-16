---
task_id: "task-002"
agent: "tahoe-loader"
status: in_progress
started: 2026-04-15T16:00:00Z
completed: null
slurm_job_id: 8346038
---

# Task 002 Status Report

## Summary

Download script written and submitted to SLURM as job **8346038** on the `week` partition.
The download of the full Tahoe-100M dataset (~429 GB) is expected to take 1-5 days.

## Download Details

- **Method:** HuggingFace `snapshot_download` via `huggingface_hub` library
- **Dataset:** `tahoebio/Tahoe-100M` (Parquet format, 7 subsets)
- **Target path:** `/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/`
- **Expected size:** ~429 GB
- **SLURM job:** 8346038, partition=week, time limit=5 days, 4 CPUs, 32 GB RAM

## What's Done

- [x] Download environment created (`env-tahoe-download`)
- [x] Dataset researched (HuggingFace, 7 subsets, Parquet format)
- [x] Download script written (`output/task-002-download-script.py`)
- [x] SLURM batch script written (`output/task-002-download-slurm.sh`)
- [x] SLURM job submitted (job 8346038)

## What Remains (after download completes)

- [ ] Verify data integrity (~100.6M cells, 50 cell lines, 379 compounds)
- [ ] Set up scDataset streaming loader
- [ ] Profile loading performance at 10K, 100K, 1M cell scales
- [ ] Write data documentation
- [ ] Write verification/performance scripts

## Monitoring

```bash
squeue -j 8346038                    # Check job status
tail -f output/tahoe-download-8346038.log   # Monitor progress
cat /nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/.download_complete  # Check completion
```
