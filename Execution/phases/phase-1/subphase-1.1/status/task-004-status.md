---
task_id: "task-004"
agent: "gears-setup"
subphase: "1.1"
status: complete
date: 2026-04-16
---

# Task 004 Status: GEARS Setup on Tahoe-100M

## Overall Status: COMPLETE

GEARS is installed, the data adapter is built and verified, the full GPU pipeline
works end-to-end on H200, and GPU memory profiling is complete. No GPU OOM risk.

## Success Criteria

1. [x] GEARS installed in env-delta (with version pins for numpy, scipy, networkx, torch_geometric)
2. [x] Data adapter loads Tahoe-100M subset via streaming without loading full dataset
3. [x] GEARS produces predictions on at least one perturbation condition
4. [x] Peak GPU memory documented at each stage
5. [x] OOM assessment: NO GPU OOM risk -- peak 1.023 GB on H200 (150.1 GB). Bottleneck is CPU RAM.
6. [x] Setup report written with all metrics
7. [x] Status report written

## What Was Done

### 1. GEARS Installation

- Installed from GitHub: `pip install git+https://github.com/snap-stanford/GEARS.git`
- Required version pins: numpy==1.26.4, scipy==1.13.1, networkx==3.2.1, torch_geometric==2.5.3
- Current torch version: 2.11.0+cu128 (CUDA 12.8)
- Must use `PYTHONNOUSERSITE=1` due to user site-packages conflicts

### 2. Tahoe-100M Data Exploration

- 100.6M cells, 50 cell lines, 380 drugs (incl. DMSO_TF control)
- Expression stored as sparse (token_id, value) pairs -- NOT 0-indexed
- Gene metadata: 62,710 genes with token_ids 3-62712
- DMSO_TF is vehicle control (2.33M cells)
- Drug targets available for 264/379 drugs

### 3. Data Adapter (gears_adapter.py)

- Streams parquet files for specific drug + cell_line combinations
- Supports multi-drug loading (required for GEARS train/val/test split)
- Maps token_ids to column positions using gene_metadata
- Converts chemical perturbation drug names to target gene names with
  GEARS-compatible format (e.g., "Rapamycin" -> "MTOR+ctrl")
- Filters to HVG while preserving perturbation target genes
- Handles DMSO_TF as 'ctrl' condition

### 4. Critical Compatibility Finding

**GEARS is designed for genetic perturbations (CRISPR), NOT chemical perturbations
(drugs).** Two key adaptations were required:

1. **Condition format:** GEARS expects perturbation labels as "GENE+ctrl" for
   single perturbations. Drug names must be mapped to target gene names
   (e.g., Rapamycin -> MTOR+ctrl). This limits GEARS to the 264 drugs with
   known gene targets.

2. **Split requirements:** GEARS needs >=10 unique perturbation conditions for
   its train/val/test split logic (`int(n_perts * 0.1) >= 1`). Testing with a
   single drug fails. The adapter supports loading 15+ drugs simultaneously.

### 5. GPU Pipeline Verification (H200)

Full pipeline verified on NVIDIA H200 GPU (150.1 GB VRAM):
- Data loading: 3149 cells (15 drugs + ctrl), 4997 genes
- AnnData construction with token_id mapping
- Zero-gene filter: 62,710 -> 28,448 genes
- HVG selection: -> 5,000 genes (with perturbation targets preserved)
- GEARS DE gene computation + PyG cell graph creation
- Model initialization (co-expression network download, GNN construction)
- Forward pass: output shape (32, 4997), 0.3s
- Backward pass: training loss 0.2403, 0.1s

### 6. GPU Memory Profiling Results

**GPU: NVIDIA H200, 150.1 GB VRAM**

#### Per-stage memory (basic test, batch_size=32, 3149 cells):

| Stage | Allocated GB | Peak GB |
|-------|-------------|---------|
| Baseline | 0.000 | 0.000 |
| After data load | 0.000 | 0.000 |
| After data process | 0.000 | 0.000 |
| After model init | 0.018 | 0.018 |
| After forward pass | 0.057 | 0.430 |
| After backward pass | 0.118 | 1.023 |

#### Batch size scaling:

| Batch Size | Peak GPU (GB) | Status |
|-----------|--------------|--------|
| 32 | 1.056 | PASS |
| 64 | 2.005 | PASS |
| 128 | 3.910 | PASS |
| 256 | 7.730 | PASS |

**Conclusion:** GPU memory scales linearly with batch size (~30 MB per sample in
batch). Even at batch_size=256, peak is only 7.73 GB. **No GPU OOM risk on any
available GPU** (RTX 5000 Ada: 32.7 GB, H200: 150 GB, B200: 183 GB).

**Actual bottleneck:** CPU RAM for parquet loading and AnnData construction. With
15 drugs scanning 50 parquets each at 1000 cells/drug, the process was OOM-killed
at 64 GB RAM. 96 GB RAM was sufficient for the basic test. Scaling beyond ~5000
cells per drug with 15 drugs may require >96 GB RAM or streaming optimizations.

## Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Data adapter | `output/scripts/gears_adapter.py` | Complete |
| Test script | `output/scripts/gears_test.py` | Complete |
| SLURM script (H200) | `output/scripts/gears_test_h200.sbatch` | Complete |
| SLURM script (gpu) | `output/scripts/gears_test.sbatch` | Superseded |
| SLURM script (devel) | `output/scripts/gears_test_devel.sbatch` | Superseded |
| Setup report | `output/task-004-gears-setup-report.md` | Complete |
| GPU basic test | `.../delta/test-outputs/gears/gears_basic_test.json` | Complete |
| GPU scaling test | `.../delta/test-outputs/gears/gears_scaling_test.json` | Complete |

## SLURM Jobs

| Job ID | Partition | Status | Purpose |
|--------|-----------|--------|---------|
| 8405887 | gpu | CANCELLED | Initial test (queue congestion) |
| 8406112 | gpu_devel | CANCELLED | Quick test (queue congestion) |
| 8406238 | gpu_devel | COMPLETED | First H200 run (AttributeError fix) |
| 8406544 | gpu_devel | COMPLETED | Second run (split KeyError: 'val') |
| 8407448 | gpu_devel | COMPLETED | Third run (still KeyError: 'val', 5 drugs too few) |
| 8407627 | gpu_devel | OOM KILLED | 15 drugs, 64G RAM insufficient |
| 8408021 | gpu_devel | OOM KILLED | 15 drugs, 96G, scaling test OOM |
| 8408537 | gpu_devel | OOM KILLED | Same, during 5K-cell scaling iteration |
| 8409737 | gpu_devel | COMPLETED | Final: basic + batch scaling, all PASS |

## Issues and Blockers (All Resolved)

1. **RESOLVED: GEARS split with few conditions.** GEARS needs >=10 perturbation
   conditions for `int(n * 0.1) >= 1` in train/val/test split. Adapter updated
   to load 15 drugs with unique gene targets simultaneously.
2. **RESOLVED: Condition format.** GEARS expects "GENE+ctrl" format for single
   perturbations, not bare gene names. Adapter updated to produce this format.
3. **RESOLVED: torch.cuda attribute.** PyTorch 2.11 uses `total_memory` instead of
   `total_mem` in device properties. Fixed with `getattr` fallback.
4. **ONGOING: CPU RAM bottleneck.** Loading 15 drugs x 50 parquets can exceed
   64 GB RAM. Workaround: use 96G RAM and limit parquets. Not a GPU issue.
5. **ONGOING: Chemical perturbation compatibility.** Drug-to-gene mapping is a
   scientific approximation. GEARS treats Rapamycin as equivalent to MTOR
   knockout, which is not biologically accurate.

## Recommendations for Subphase 1.2+

1. For Delta benchmark: GEARS GPU memory is trivial (<8 GB even at batch_size=256).
   Focus compute planning on CPU RAM and data loading time, not GPU.
2. All Delta SLURM jobs should request >=96 GB RAM for multi-drug GEARS runs.
3. For Delta benchmark: consider whether GEARS's drug-to-gene mapping is
   scientifically valid, or if GEARS should be excluded from the perturbation
   prediction comparison.
4. The token_id mapping logic in gears_adapter.py should be reused by
   other method adapters (scGPT, CPA, etc.).
5. All Delta SLURM jobs must include `export PYTHONNOUSERSITE=1`.

## Resource Usage

| Resource | Estimated | Actual |
|----------|-----------|--------|
| CPU time | - | ~3 hours (installation, debugging, testing, iterations) |
| GPU time | 2-4 hours | ~0.5 hours (H200, across all SLURM jobs) |
| Storage | minimal | ~50 MB (PyG datasets, adapter code) |
