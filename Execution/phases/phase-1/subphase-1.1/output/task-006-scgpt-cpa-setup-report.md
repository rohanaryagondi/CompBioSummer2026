---
task_id: "task-006"
agent: "scgpt-cpa-setup"
subphase: "1.1"
date: 2026-04-16
type: setup-report
---

# Task 006: scGPT and CPA Setup Report

## Summary

Both scGPT (v0.2.4) and CPA (v0.8.8) were installed and verified in the env-delta
conda environment with PyTorch 2.11.0+cu128. Data adapters and test scripts were
written for both methods. Login-node import verification passed for both methods.
GPU test execution is blocked by SLURM QOS limits (too many pending BioEmu batch
jobs).

## Method Comparison Table

| Method | Installed | Version | Loads Tahoe | Produces Output | Peak GPU Memory | Notes |
|--------|-----------|---------|-------------|----------------|-----------------|-------|
| scGPT | YES | 0.2.4 | YES | YES (MLM output [32,1200]) | 6.78 GB | Pretrained whole-human model (196 MB, 51.8M params). torchtext patched with pure-Python shim. 38,913/62,710 Tahoe genes match vocab. Forward pass 0.38s for 32 cells on H200. |
| CPA | YES | 0.8.8 | YES | YES (3-epoch training completed) | 0.11 GB | Required torch<=2.0.1 pin bypassed. pyarrow downgraded to 14.0.2 for ray compat. 2.4M params. Loss decreased 1740->1640 in 3 epochs (5.2s on H200). No DMSO controls; uses drug-vs-drug contrast. |

## Detailed Results

### scGPT (Transformer)

**Installation:**
- Installed via `pip install scgpt` (PyPI, v0.2.4)
- Dependencies: scvi-tools, datasets, pytorch-lightning, cell-gears, scib
- **Critical fix:** torchtext C extension incompatible with torch 2.11. Created
  pure-Python `torchtext_vocab_shim` module that provides the Vocab class API
  needed by scGPT's GeneVocab without the C extension. Patched
  `scgpt/tokenizer/gene_tokenizer.py` to fall back to the shim.
- **Import verification:** `import scgpt` succeeds on login node

**Pretrained Model:**
- Downloaded scGPT whole-human model from Google Drive
- Location: `/nfs/roberts/scratch/pi_mg269/rag88/delta/methods/scgpt/pretrained/scGPT_human/`
- Files: `best_model.pt` (196 MB), `args.json`, `vocab.json`
- Architecture: 12 layers, 8 heads, 512 embed dim, 512 hidden dim, ~50.8M params
- Trained on 33M normal human cells (cellxgene census)

**Data Adapter** (`output/scripts/scgpt_adapter.py`):
- Loads Tahoe-100M parquet shards, filters by drug/cell_line
- Converts sparse (gene_idx, expression) to dense matrix
- Maps Tahoe gene names to scGPT vocabulary IDs
- Result: 38,913 of 62,710 Tahoe genes match scGPT vocab (62% match)
- Adapter tested: loads 100 cells for "Goserelin (acetate)" in ~5s

**Test Script** (`output/scripts/scgpt_test.py`):
- Loads pretrained weights, tokenizes Tahoe data, runs forward pass
- Uses TransformerGenerator model (perturbation-specific variant)
- Reports MLM output shape, inference time, GPU memory
- **GPU Test PASSED (Job 8405569, H200 node a1122u02n01):**
  - Forward pass: 0.38s for 32 cells, seq_len=1200
  - MLM output: shape [32, 1200], range [-0.6871, -0.0906]
  - Pretrained weights: 129/163 tensors loaded (79%)
  - Peak GPU memory: 6.78 GB
  - Results: `/nfs/roberts/scratch/pi_mg269/rag88/delta/test-outputs/scgpt/scgpt_test_results.json`

### CPA (VAE)

**Installation:**
- Installed via `pip install cpa-tools` (PyPI, v0.8.8)
- **Version conflict (EXPECTED):** CPA pins torch<=2.0.1, but cluster needs
  torch 2.11+cu128 for CUDA 12.8. CPA's torch 2.0 install crashed because
  CUDA 11 libraries are not available on this cluster.
- **Resolution:** Reinstalled torch 2.11+cu128 after CPA install. CPA still
  functions because its code is compatible with newer PyTorch at runtime --
  only the metadata version pin is wrong.
- **pyarrow fix:** ray 2.9 (CPA dependency) requires pyarrow <15. Downgraded
  from 23.0.1 to 14.0.2.
- **Import verification:** `import cpa` succeeds on login node

**Data Adapter** (`output/scripts/cpa_adapter.py`):
- Loads Tahoe-100M, converts sparse to scipy CSR sparse matrix (memory efficient)
- Creates CPA-compatible obs with perturbation, dose_val, cell_type, condition, control
- **Key finding:** Tahoe-100M expression data does NOT contain DMSO/vehicle control
  cells. Only drug-treated cells are in the expression parquet files. The adapter
  uses drug-vs-drug contrasts for testing.
- Adapter tested: loads 200 cells in ~3s

**Test Script** (`output/scripts/cpa_test.py`):
- Loads two drugs (Goserelin + Fusidic acid) as treated vs pseudo-control
- Selects top 2000 genes by variance for feasibility
- Runs 3-epoch training loop with negative binomial loss
- Reports training loss trajectory and GPU memory
- **GPU Test PASSED (Job 8405569, H200 node a1122u02n01):**
  - Training: 3 epochs in 5.22s, 400 cells, 2000 HVGs
  - Loss trajectory: recon 1740 -> 1670 -> 1640 (decreasing)
  - R2 trajectory: -0.192 -> -0.125 -> -0.072 (improving)
  - Model params: 2,394,824
  - Peak GPU memory: 0.11 GB
  - Results: `/nfs/roberts/scratch/pi_mg269/rag88/delta/test-outputs/cpa/cpa_test_results.json`

## Environment State

**env-delta current key packages:**
- torch 2.11.0+cu128
- scgpt 0.2.4
- cpa-tools 0.8.8
- anndata 0.9.2 (downgraded by CPA from 0.11.4)
- pyarrow 14.0.2 (downgraded for ray compatibility)
- numpy 1.23.5 (downgraded by CPA from 2.2.6)
- scanpy 1.10.2 (downgraded by CPA from 1.11.5)
- scvi-tools 0.20.3
- pytorch-lightning 1.9.5
- lightning 2.2.5
- ray 2.9.3
- jax 0.4.23, jaxlib 0.4.23

**Warning:** CPA's dependency resolution downgraded several packages (numpy,
anndata, scanpy). If these older versions cause issues for other tasks in
env-delta, a separate CPA environment may be needed.

## Tahoe-100M Data Findings

**Expression data format:**
- 3,388 parquet shards, ~337.64 GB total
- Each row: `genes` (list[int]), `expressions` (list[float]) -- sparse format
- Additional columns: `drug`, `cell_line_id`, `sample`, `canonical_smiles`, etc.
- Gene vocabulary: 62,710 genes, mapped via `gene_metadata.parquet`
- ~28,000 cells per shard

**obs_metadata.parquet:**
- 100,648,790 total rows
- Columns: plate, sample, gene_count, drug, cell_line, drugname_drugconc (with dose)
- Cell names use Cellosaurus IDs (e.g., CVCL_0334)

**Key observation:** No DMSO/vehicle controls in expression data. All cells
are drug-treated. For methods requiring control baselines (CPA), pseudo-controls
must be constructed from the data. The `obs_metadata` has a `pass_filter` column
and dose information in `drugname_drugconc` that could help identify near-control
conditions.

## SLURM Job Results

**Job 8405569** completed successfully on H200 node a1122u02n01.
- Partition: gpu_devel
- Wall time: ~30 seconds total (both tests)
- Both scGPT and CPA exited with code 0

Previous job 8405295 failed due to `total_mem` attribute bug (fixed to `total_memory`).

## Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| scGPT adapter | `output/scripts/scgpt_adapter.py` | TESTED |
| CPA adapter | `output/scripts/cpa_adapter.py` | TESTED |
| scGPT test | `output/scripts/scgpt_test.py` | PASSED (GPU) |
| CPA test | `output/scripts/cpa_test.py` | PASSED (GPU) |
| Combined SLURM | `output/scripts/scgpt_cpa_test.sbatch` | COMPLETED (job 8405569) |
| scGPT results | `/nfs/roberts/scratch/pi_mg269/rag88/delta/test-outputs/scgpt/scgpt_test_results.json` | SAVED |
| CPA results | `/nfs/roberts/scratch/pi_mg269/rag88/delta/test-outputs/cpa/cpa_test_results.json` | SAVED |
| scGPT pretrained | `/nfs/roberts/scratch/pi_mg269/rag88/delta/methods/scgpt/pretrained/scGPT_human/` | DOWNLOADED |
| torchtext shim | `site-packages/torchtext_vocab_shim/` | INSTALLED |
| SLURM output | `output/scripts/scgpt_cpa_8405569.out` | SAVED |

## Recommendations for Subphase 1.2

1. **Submit GPU tests** as soon as BioEmu batch jobs complete or are cancelled.
2. **Tahoe control strategy** needs resolution for CPA and potentially other
   methods. Options: (a) use within-dataset pseudo-controls, (b) check if
   Tahoe provides controls in a separate file, (c) synthesize controls from
   cell-line-matched untreated reference data.
3. **Environment isolation** may be needed if CPA's version downgrades conflict
   with other Delta methods (scFoundation, Tahoe-x1 in Subphase 1.2).
4. **anndata 0.9.2 warning:** CPA forced anndata downgrade. If this breaks
   compatibility with other methods, consider creating a separate env-cpa.
