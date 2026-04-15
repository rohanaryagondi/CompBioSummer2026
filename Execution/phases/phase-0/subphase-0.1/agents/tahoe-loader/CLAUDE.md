# SubAgent: Download + Preprocess Tahoe-100M

You are a **SubAgent** executing task-002 in subphase 0.1 of the CompBioSummer2026
execution pipeline. You have a narrowly scoped task with explicit success criteria.
Execute your task, write your documentation, and report your results.

---

## Your Task

**Task ID:** task-002
**Title:** Download + preprocess Tahoe-100M via scDataset
**Track:** Delta
**Subphase:** 0.1
**Estimated effort:** 3-5 days

---

## What You Must Accomplish (Zero Compromise)

1. Create a minimal Python environment with scDataset and cellxgene_census (independent of env-delta)
2. Download the complete Tahoe-100M dataset (~429 GB) to HPC scratch storage
3. Verify data integrity: ~100.6M cells, 50 cell lines, 379 compounds
4. Set up scDataset streaming pipeline and verify with a 10K-cell test query
5. Profile loading performance at 10K, 100K, and 1M cell scales
6. Document data layout, file paths, schema, and access patterns for Phase 1 agents
7. Write status report to `../../status/task-002-status.md`

---

## What You Read

### MUST READ (before starting)

| File | Why |
|------|-----|
| `../../tasks/task-002-tahoe-download.md` | Your full task specification with detailed download steps |
| `../../../../../Proposal/Delta.md` (Section 3: Dataset) | Tahoe-100M specifications, scDataset pipeline details |
| `../../../../../Proposal/ImplementationPlan.md` (Section 8, Section 10.3: DK1) | Phase 0 requirements and kill criteria |
| `../../../../../context/mission-briefing.md` | HPC storage specs, scratch path |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../Proposal/Delta.md` (Sections 4-7) | Method evaluation plans that will use this data |

### DO NOT READ

- Other SubAgents' task specs in `../../tasks/` (not your scope)
- Other SubAgents' output in `../../output/` (unless listed as a dependency)
- Phase plans or subphase plans (your HeadAI manages the orchestration)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)
- Alpha-M or Gamma proposals (different track)

---

## Detailed Instructions

### Step 1: Create Minimal Download Environment

You are running concurrently with task-001 (environment builder). Do NOT depend on
env-delta. Create your own minimal environment:

```bash
conda create -n env-tahoe-download python=3.10 -y
conda activate env-tahoe-download
pip install cellxgene-census scDataset anndata scanpy tiledbsoma
```

### Step 2: Locate Dataset

Use the CZ CELLxGENE Census API or web interface to find Tahoe-100M:
- Dataset: Tahoe-100M (CZ Biohub)
- License: CC0
- Expected size: ~429 GB, 100.6M cells
- 50 cancer cell lines, 379 compounds, 17,813 conditions

Record: exact dataset version, DOI, download URL or API endpoint.

### Step 3: Download

Download to HPC scratch (e.g., `$SCRATCH/tahoe-100m/`).
- Use resume-capable downloads (interrupted downloads should resume, not restart)
- Log: start time, end time, total size, download speed
- If download takes >48 hours, document in status report and estimate completion

### Step 4: Verify Integrity

```python
import anndata as ad
# Or use scDataset/Census API to verify counts
# Verify: n_obs ~ 100.6M, n_vars = gene count
# Verify: metadata has cell_line (50 unique), compound (379 unique)
```

### Step 5: Set Up scDataset Streaming

```python
from scDataset import scDataset
dataset = scDataset(path="$SCRATCH/tahoe-100m/")
# Verify streaming works without full memory load
```

### Step 6: Test Query (10K cells)

Load 10,000 cells and verify:
- Gene expression matrix shape and dtype
- Cell metadata columns: cell_line, compound, dose, timepoint
- 50 unique cell lines present in full dataset
- Gene names are standard symbols

### Step 7: Performance Profile

Benchmark at three scales:
- 10K cells: time to load, memory usage
- 100K cells: time to load, memory usage
- 1M cells: time to load, memory usage

Document wall time and peak memory for each.

### Step 8: Write Data Documentation

Create `output/task-002-data-documentation.md`:
- File path on HPC scratch
- Dataset version, DOI, download date
- File format and directory structure
- Schema: column names, data types, value ranges
- scDataset configuration for streaming access
- Performance profile summary
- Recommended access patterns for Phase 1 agents

---

## What You Write

### Code and data artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Tahoe-100M data | `$SCRATCH/tahoe-100m/` | Full dataset on HPC scratch |
| Download script | `output/task-002-download-script.sh` | Reproducible download commands |
| Loader test script | `output/task-002-loader-test.py` | Data verification and test query script |
| Data documentation | `output/task-002-data-documentation.md` | Complete data layout and access guide |
| Performance profile | `output/task-002-performance.md` | Loading benchmarks at 3 scales |

### Mandatory documentation

**Status report** (ALWAYS required -- non-negotiable):
Write to `../../status/task-002-status.md` using the status-report template.

---

## Verification

Before declaring your task complete, verify each criterion:

1. [ ] Dataset files exist on HPC scratch at documented path
2. [ ] Total size approximately matches expected (~429-630 GB)
3. [ ] Test query returns correct schema and metadata
4. [ ] Cell count verification: ~100.6M
5. [ ] Performance profile document exists with timing for 3 scales
6. [ ] Data documentation is complete with paths, schema, and access instructions
7. [ ] Status report written

---

## If Something Goes Wrong

1. **Do not silently fail.** If you cannot complete a step, document it.
2. Write a status report with status `blocked` or `failed`.
3. Include the exact error message or log excerpt.
4. Describe what you tried and why it did not work.
5. Suggest what might fix the issue (if you have ideas).
6. Your HeadAI will read your status report and decide next steps.

**Common issues:**
- Network timeouts during download → use resume support, try alternative download method
- Disk quota exceeded → check scratch quota, contact HPC admin if needed
- scDataset import fails → check Python version, try alternative loading (tiledbsoma)
- Memory error loading large subset → reduce test query size, use streaming
