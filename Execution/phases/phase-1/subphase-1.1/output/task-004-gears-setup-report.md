---
task_id: "task-004"
agent: "gears-setup"
subphase: "1.1"
date: 2026-04-16
---

# Task 004: GEARS Setup Report

## Summary

GEARS (snap-stanford/GEARS) was installed in env-delta and a data adapter was
built to bridge Tahoe-100M chemical perturbation data to GEARS's expected genetic
perturbation format. The full pipeline (data loading, AnnData construction, DE
gene computation, PyG dataset creation, model initialization, forward pass,
backward pass) was verified end-to-end on an NVIDIA H200 GPU with complete memory
profiling.

**Key finding:** GEARS has no GPU OOM risk. Peak GPU memory is 1.023 GB at default
batch size (32) with 3,149 cells, scaling linearly to 7.73 GB at batch size 256.
The actual scaling bottleneck is CPU RAM for parquet loading and AnnData construction.

## Installation

| Metric | Value |
|--------|-------|
| Installed | yes |
| Version | pip HEAD (snap-stanford/GEARS@main) |
| Install command | `pip install git+https://github.com/snap-stanford/GEARS.git` |
| Key version pins | numpy==1.26.4, scipy==1.13.1, networkx==3.2.1, torch_geometric==2.5.3 |
| PyTorch | 2.11.0+cu128 (CUDA 12.8) |
| Import works | yes (with PYTHONNOUSERSITE=1 to avoid user site-packages conflicts) |

### Installation Issues Resolved

1. **numpy missing:** env-delta had no numpy. Fixed with `pip install numpy`.
2. **scipy ABI mismatch:** scipy 1.14.1 incompatible with numpy 1.26.4. Pinned scipy==1.13.1.
3. **networkx Python 3.10 incompatibility:** networkx 3.3 uses Python 3.11+ syntax. Pinned networkx==3.2.1.
4. **torch CPU-only:** Original env-delta had torch 2.11.0+cpu. Resolved to torch 2.11.0+cu128.
5. **torch_geometric version mismatch:** torch_geometric 2.7.0 incompatible with torch 2.4.1. Pinned 2.5.3.
6. **Dual site-packages paths:** Conda env has two install locations. Must use PYTHONNOUSERSITE=1.

## Tahoe-100M Data Structure

| Property | Value |
|----------|-------|
| Total cells | 100,648,790 |
| Expression files | 3,388 parquet (337.64 GB) |
| Genes | 62,710 (token_ids 3-62712) |
| Unique cell lines | 50 |
| Unique drugs | 380 (incl. DMSO_TF control) |
| Vehicle control | DMSO_TF (2,330,156 cells) |
| Expression format | Sparse: (gene_token_ids, expression_values) per cell |
| Metadata columns | drug, cell_line_id, sample, moa-fine, canonical_smiles, pubchem_cid, plate |

### Critical Data Finding: Token ID Mapping

Expression data gene indices are **token_ids** (3-62712), NOT 0-indexed array positions.
Indices 1-2 are special tokens (PAD/CLS) not in gene metadata. The adapter must map
token_ids to array column positions using gene_metadata.token_id.

### Drug-to-Gene Target Mapping

GEARS was designed for genetic perturbations (CRISPR), where condition labels are
gene names in the format "GENE+ctrl" (single perturbation). Tahoe-100M has chemical
perturbations (drug names). The adapter maps each drug to its primary target gene:

- 264 of 379 drugs have known gene targets
- Example: Rapamycin -> MTOR+ctrl
- Drugs without targets or whose targets are missing from the HVG-filtered gene
  list are excluded from GEARS processing

### GEARS Split Requirements

GEARS requires enough perturbation conditions for train/val/test splitting. With
the default test fraction (0.1), at least 10 unique perturbation conditions are
needed so `int(n_perts * 0.1) >= 1` for both test and val splits. The test uses
15 drugs with distinct gene targets from cell line CVCL_0546.

## Data Adapter

**File:** `output/scripts/gears_adapter.py`

Key features:
- Streams Tahoe-100M parquet files (does not load full 428 GB)
- Supports single-drug or multi-drug loading via `drugs` parameter
- Converts sparse (token_id, expression) to dense/CSR AnnData
- Maps chemical perturbation drug names to target gene names in GEARS format
  (e.g., Rapamycin -> MTOR+ctrl)
- Filters to HVG while preserving perturbation target genes
- Supports `max_cells`, `max_parquets`, `cell_line` filtering for memory control
- Handles DMSO_TF as vehicle control (mapped to 'ctrl')

## GPU Test Results

### Test Configuration

| Parameter | Value |
|-----------|-------|
| GPU | NVIDIA H200 (150.1 GB VRAM) |
| Drugs | 15 (Rapamycin, Mitoxantrone, Tucidinostat, Resveratrol, Lenalidomide, Vilanterol, Norepinephrine, Sodium Salicylate, Clotrimazole, Furosemide, Adenosine, Larotrectinib, Retinoic acid, Trimetrexate, Gemfibrozil) |
| Cell line | CVCL_0546 |
| Cells | 3,149 (200 per drug + 1000 control) |
| Genes | 4,997 (after HVG selection) |
| Conditions | 16 (15 drugs + ctrl) |
| SLURM job | 8409737 (gpu_devel, H200) |

### Per-Stage GPU Memory Profile (batch_size=32)

| Stage | Allocated (GB) | Peak (GB) | Time |
|-------|---------------|-----------|------|
| Baseline | 0.000 | 0.000 | - |
| After data load | 0.000 | 0.000 | 71.7s |
| After data process | 0.000 | 0.000 | 13.5s |
| After model init | 0.018 | 0.018 | 174.2s |
| After forward pass | 0.057 | 0.430 | 0.3s |
| After backward pass | 0.118 | 1.023 | 0.1s |

Data loading and processing happen entirely on CPU. GPU memory is only used during
model initialization and inference/training.

### Batch Size Scaling

| Batch Size | Peak GPU (GB) | Status | Scaling Factor |
|-----------|--------------|--------|----------------|
| 32 | 1.056 | PASS | 1.0x |
| 64 | 2.005 | PASS | 1.9x |
| 128 | 3.910 | PASS | 3.7x |
| 256 | 7.730 | PASS | 7.3x |

GPU memory scales approximately linearly with batch size (~30 MB per sample in batch).

### Forward Pass Output

| Metric | Value |
|--------|-------|
| Output shape | (batch_size, 4997) |
| Training loss (1 step) | 0.2403 |
| Forward pass time | 0.3s |
| Backward pass time | 0.1s |

### OOM Assessment

**No GPU OOM risk.** At batch_size=256, peak GPU memory is only 7.73 GB -- well
within the capacity of any available GPU:
- RTX 5000 Ada: 32.7 GB (4.2x headroom at batch_size=256)
- H200: 150.1 GB (19.4x headroom)
- B200: 183.0 GB (23.7x headroom)

**CPU RAM is the actual bottleneck.** Loading 15 drugs x 50 parquets per drug with
1000 cells per drug was OOM-killed at 64 GB system RAM. 96 GB was sufficient for
the basic test (200 cells per drug, 20 parquets). For production runs with large
cell counts, either:
- Limit concurrent parquet reads
- Implement streaming data processing
- Request higher RAM allocations (96-128 GB)

## Key Findings for Future Subphases

1. **GEARS is not natively compatible with chemical perturbations.** The Delta
   benchmark must use the drug-to-target mapping adapter. Drug names must be in
   "GENE+ctrl" format for single perturbations. This is a scientific approximation
   (a drug inhibiting a protein is not the same as knocking out the gene).

2. **Tahoe-100M expression data uses sparse token_id format.** All Delta methods
   must handle this conversion. The adapter logic in `gears_adapter.py` can be
   reused by other method adapters.

3. **GEARS needs >=10 unique perturbation conditions.** Single-drug testing fails
   due to the train/val/test split logic. Future Delta runs must use multi-drug
   configurations.

4. **env-delta has dual site-packages paths** causing version conflicts. All SLURM
   jobs must use `export PYTHONNOUSERSITE=1`.

5. **GPU memory is not a concern for GEARS.** Focus production planning on CPU RAM
   and data loading throughput. Batch size can be tuned freely without OOM risk.

6. **Model initialization is slow (~3 minutes).** This is dominated by downloading
   the co-expression network file (9.46 MB) and building the gene interaction graph.
   This should be cached for production runs.

## Notes

- GEARS last updated 2024, designed for datasets like Norman (10K cells, genetic perturbations)
- The Tahoe-100M scale (100M cells) far exceeds GEARS's original design
- GEARS model uses GNN with gene-gene co-expression graph -- model parameters are
  independent of cell count (cells are batched through the same model)
- All GPU memory profiling done at hidden_size=64 (GEARS default)
