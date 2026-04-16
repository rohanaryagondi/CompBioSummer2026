---
task_id: "task-002"
agent: "tahoe-loader"
type: "data-documentation"
date: 2026-04-16
---

# Tahoe-100M Data Documentation

## Dataset Identity

- **Name:** Tahoe-100M
- **Source:** CZ Biohub / HuggingFace (`recursionpharma/Tahoe-100M`)
- **License:** CC0
- **Download date:** 2026-04-15 to 2026-04-16
- **Total size:** 428.89 GB across 8,852 files

## HPC Location

```
/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/
```

## Directory Structure

```
tahoe-100m/
├── expression_data/
│   └── data/                        # 3,388 parquet files (337.64 GB)
│       ├── train-00000-of-03388.parquet
│       ├── train-00001-of-03388.parquet
│       └── ... (3,388 total)
├── metadata/
│   └── metadata/                    # All metadata files
│       ├── obs_metadata.parquet     # 2.29 GB — per-observation metadata
│       ├── gene_metadata.parquet    # 1.33 MB — gene annotations
│       ├── drug_metadata.parquet    # 0.04 MB — compound metadata
│       ├── cell_line_metadata.parquet  # 0.02 MB — cell line info
│       ├── sample_metadata.parquet  # 0.07 MB — sample-level metadata
│       ├── gene_vocabulary.json     # Gene name vocabulary
│       ├── gene_vocabulary.jsonl    # Gene name vocabulary (line-delimited)
│       └── pseudobulk_differential_expression/  # 1,026 parquet files (88.86 GB)
│           ├── part-00000-*.parquet
│           └── ... (1,026 total)
├── download_results.json            # Download metadata / completion log
└── .download_complete               # Completion marker (expression_data)
```

**Note on nested structure:** HuggingFace `snapshot_download` creates the path
`expression_data/data/` and `metadata/metadata/` because the repo has `data/` and
`metadata/` subdirectories. Phase 1 agents should use the full paths shown above.

## File Sizes by Component

| Component | Files | Size | Format |
|-----------|-------|------|--------|
| expression_data | 3,388 | 337.64 GB | Parquet (sharded) |
| obs_metadata | 1 | 2.29 GB | Parquet |
| pseudobulk_DE | 1,026 | 88.86 GB | Parquet (sharded) |
| gene_metadata | 1 | 1.33 MB | Parquet |
| drug_metadata | 1 | 0.04 MB | Parquet |
| cell_line_metadata | 1 | 0.02 MB | Parquet |
| sample_metadata | 1 | 0.07 MB | Parquet |
| gene_vocabulary | 2 | 6.53 MB | JSON + JSONL |
| **Total** | **8,852** | **428.89 GB** | |

## Expression Data Schema

Each parquet shard contains ~28,225 rows with 10 columns:

| Column | Type | Description |
|--------|------|-------------|
| `genes` | list | Gene names per cell |
| `expressions` | list | Expression values per cell |
| `drug` | string | Compound / treatment name |
| `sample` | string | Sample identifier |
| `BARCODE_SUB_LIB_ID` | string | Barcode-sublibrary ID |
| `cell_line_id` | string | Cell line identifier |
| `moa-fine` | string | Fine-grained mechanism of action |
| `canonical_smiles` | string | SMILES string for the compound |
| `pubchem_cid` | int/string | PubChem compound ID |
| `plate` | string | Plate identifier |

**Important:** The cell line column is named `cell_line_id` (not `cell_type` as
referenced in some documentation).

## Access Patterns for Phase 1

### PyArrow (recommended for exploratory analysis)

```python
import pyarrow.parquet as pq

# Read a single shard
table = pq.read_table(
    "/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/expression_data/data/train-00000-of-03388.parquet"
)
print(table.schema)
print(table.num_rows)  # ~28,225
```

### HuggingFace datasets (recommended for ML training)

```python
from datasets import load_dataset

# Streaming mode — does not load full dataset into memory
dataset = load_dataset(
    "parquet",
    data_dir="/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/expression_data/data/",
    streaming=True,
)
for batch in dataset["train"].iter(batch_size=1000):
    # Process batch
    break
```

### Metadata access

```python
import pyarrow.parquet as pq

meta_base = "/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/metadata/metadata"
obs = pq.read_table(f"{meta_base}/obs_metadata.parquet")
genes = pq.read_table(f"{meta_base}/gene_metadata.parquet")
drugs = pq.read_table(f"{meta_base}/drug_metadata.parquet")
cell_lines = pq.read_table(f"{meta_base}/cell_line_metadata.parquet")
```

## Download Method

The download was executed directly on the login node (not via SLURM) using
`huggingface_hub.snapshot_download` with `hf_transfer` (Rust-based) acceleration.

- **Expression data:** `allow_patterns=["data/*"]` — 3,388 files in ~39 minutes
- **Metadata:** `allow_patterns=["metadata/*"]` — 1,033 files in ~8 minutes
- **SLURM job 8346038** (week partition) was submitted first but never started due to
  queue priority; cancelled after login-node download completed.
- **Resume support:** `huggingface_hub` supports resume on interrupted downloads.

## Known Limitations

- **scDataset not verified:** The task spec called for scDataset streaming verification.
  The actual dataset format on HuggingFace is sharded Parquet (not H5AD), so scDataset
  is not the appropriate loader. PyArrow and HuggingFace `datasets` library are the
  correct interfaces for this data format.
- **Full cell count not independently verified:** The published spec claims ~100.6M cells.
  With 3,388 shards averaging ~28,225 rows each, the estimated total is ~95.6M cells.
  A full count across all shards was not performed (would require reading all 337 GB).
