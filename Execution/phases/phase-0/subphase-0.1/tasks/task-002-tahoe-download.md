---
task_id: "task-002"
title: "Download + Preprocess Tahoe-100M via scDataset"
subphase: "0.1"
track: delta
wave: 1
agent: "tahoe-loader"
effort: "3-5 days"
status: planned
created: 2026-04-15
---

# Task 002: Download + Preprocess Tahoe-100M via scDataset

## Objective

Download the complete Tahoe-100M dataset (~429 GB, 100.6M cells, 50 cell lines,
379 compounds) from CZ CELLxGENE Discover to HPC scratch storage, set up the
scDataset streaming pipeline, verify data integrity and schema correctness, and
profile loading performance. This provides the data foundation for the entire
Delta track (PerturbMark benchmark).

---

## Context

Tahoe-100M is the largest publicly available perturbation biology dataset (CC0 license,
published by the CZ Biohub). The Delta track benchmarks 10 perturbation prediction
methods on this dataset. The scDataset library provides a streaming interface that
avoids loading the entire dataset into memory (claimed 48x speedup over naive loading).
Kill criterion DK1 (May 31) requires a working data pipeline, giving 45 days of buffer
from Phase 0. However, the download itself may take 3-5 days depending on network
bandwidth, so starting immediately is critical.

**Key constraint:** This task runs concurrently with task-001 (environment setup).
It CANNOT depend on env-delta. The agent must create its own minimal Python environment
for scDataset and cellxgene_census.

---

## Detailed Instructions

### Step 1: Create Minimal Download Environment

```bash
conda create -n env-tahoe-download python=3.10 -y
conda activate env-tahoe-download
pip install cellxgene-census scDataset anndata scanpy
```

This is a temporary environment for download/verification only. The full env-delta
(with DL frameworks) is being built by task-001 concurrently.

### Step 2: Locate and Verify Dataset Metadata

1. Use the CZ CELLxGENE Census API to locate Tahoe-100M:
   ```python
   import cellxgene_census
   census = cellxgene_census.open_soma()
   # Navigate to the Tahoe-100M collection
   ```
2. Alternatively, check the dataset page on CZ CELLxGENE Discover for direct download links
3. Confirm: CC0 license, ~100.6M cells, 50 cell lines, 379 compounds, 17,813 conditions
4. Record the exact dataset version, DOI, and download URL

### Step 3: Download Dataset

1. Identify the optimal download method:
   - CZ CELLxGENE Census API (streaming, recommended)
   - Direct HTTP download with resume support (if available)
   - `aria2c` for parallel download streams (if direct links available)
2. Download to HPC scratch: `$SCRATCH/tahoe-100m/` (or equivalent path)
3. Use resume support -- if the download is interrupted, it should continue from where it left off
4. Monitor download progress and estimate total time
5. Log total download size and elapsed time

### Step 4: Verify Data Integrity

1. Verify total file size matches published specification (~429 GB)
2. If checksums are provided by the data source, verify them
3. Count total cells: should be ~100.6M
4. Verify cell line count: should be 50
5. Verify compound count: should be 379
6. Verify condition count: should be ~17,813

### Step 5: Set Up scDataset Streaming Pipeline

1. Configure scDataset to read from the downloaded data:
   ```python
   from scDataset import scDataset
   dataset = scDataset(path="$SCRATCH/tahoe-100m/")
   ```
2. Verify the streaming interface works without loading full dataset into memory
3. Test iteration: read first 100 batches, verify batch structure

### Step 6: Run Test Query

1. Load 10,000 cells and verify schema:
   ```python
   # Expected schema fields:
   # - Gene expression matrix (obs x var)
   # - Cell metadata: cell_line, compound, dose, timepoint
   # - Gene names (var_names)
   # Verify: 50 unique cell lines, correct gene count
   ```
2. Verify perturbation labels are present and well-formatted
3. Check for any obvious data quality issues (NaN proportions, zero-expression genes)

### Step 7: Profile Loading Performance

1. Benchmark: time to load 10K, 100K, and 1M cells via scDataset streaming
2. Compare with naive loading (load full .h5ad into memory) if feasible on a high-memory node
3. Document the actual speedup factor (compare to the claimed 48x)
4. Document memory usage at each scale

### Step 8: Document Data Layout

Create a data documentation file with:
- Exact file path on HPC scratch
- Dataset version, DOI, download date
- File format and directory structure
- Schema: column names, data types, value ranges
- Cell line list (all 50)
- Compound list (sample of 379)
- scDataset configuration for streaming access
- Recommended access patterns for Phase 1 agents

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| `../../../../Proposal/Delta.md` (Section 3: Dataset) | Tahoe-100M specifications, scDataset details |
| `../../../../Proposal/ImplementationPlan.md` (Section 8: Phase 0 tasks; Section 10.3: DK1 kill criterion) | Task requirements and failure thresholds |
| `../../../../context/mission-briefing.md` | HPC storage specs, scratch path |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../Proposal/Delta.md` (Section 4-7) | Method evaluation plans that will use this data |

### DO NOT READ

- `../../../../Proposal/HumanOnlyProposal.md` -- off-limits to all AI agents
- Other SubAgent task specs in `../tasks/` -- not your scope
- Alpha-M or Gamma proposal docs -- different track

---

## Output Artifacts

### Code and data artifacts

| Artifact | Path | Format |
|----------|------|--------|
| Tahoe-100M raw data | `$SCRATCH/tahoe-100m/` | H5AD / Census format |
| Download script | `output/task-002-download-script.sh` | Bash |
| Data loader test script | `output/task-002-loader-test.py` | Python |
| Data documentation | `output/task-002-data-documentation.md` | Markdown |
| Performance profile | `output/task-002-performance.md` | Markdown |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-002-status.md` | `status-report.md` |

---

## Success Criteria (Zero Compromise)

This task is complete ONLY if ALL of the following are true:

1. [ ] Tahoe-100M dataset fully downloaded to HPC scratch (~429 GB, ~630 GB on disk)
2. [ ] Data integrity verified (cell count ~100.6M, 50 cell lines, 379 compounds)
3. [ ] scDataset streaming loader configured and functional
4. [ ] Test query on 10,000 cells returns expected schema (gene expression matrix, cell metadata with cell_line/compound/dose/timepoint)
5. [ ] Loading performance profiled at 10K, 100K, and 1M cell scales
6. [ ] Data documentation created with file paths, schema, and access patterns for Phase 1 agents
7. [ ] Status report written to `../../status/task-002-status.md`

---

## Verification

Before declaring this task complete, verify:

1. `ls -lh $SCRATCH/tahoe-100m/` shows expected files and total size ~429-630 GB
2. Python script successfully loads 10,000 cells and prints correct schema
3. `dataset.n_obs` returns ~100.6M (or equivalent cell count check)
4. Performance profile document exists with timing data for 3 scales
5. Data documentation file exists with complete schema and access instructions

---

## Failure Protocol

If this task cannot be completed:

1. Write a status report with status `failed` or `blocked`
2. Document exactly what went wrong (error messages, log excerpts)
3. Document what was tried and why it did not work
4. Identify what help is needed for the HeadAI to resolve or escalate
5. DO NOT silently skip steps or lower the success criteria
6. **Partial success is valuable:** If the download completes but scDataset fails, document the raw data location and the scDataset error. Phase 1 agents can potentially use an alternative loading strategy.
