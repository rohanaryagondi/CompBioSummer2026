---
task_id: "task-004"
title: "GEARS Setup on Tahoe-100M"
subphase: "1.1"
track: delta
wave: 2
agent: "gears-setup"
effort: "2-3 days"
status: planned
created: 2026-04-16
---

# Task 004: GEARS Setup on Tahoe-100M

## Objective

Install, configure, and verify GEARS (a GNN-based perturbation prediction method)
on the Tahoe-100M dataset. GEARS must load Tahoe-100M data via a streaming adapter
and produce predictions on at least one perturbation condition. This provides early
D3 gate evidence (3 of 5 Tier 1 methods needed by June 6).

GEARS has the highest risk of the three Tier 1 methods in this subphase — the
Implementation Plan estimates a 30% probability of memory issues with Tahoe-100M.
This task gets a dedicated agent so that OOM debugging receives focused attention.

---

## Context

The Delta track (PerturbMark) benchmarks perturbation prediction methods on
Tahoe-100M (100M cells, 50 cell lines, 379 compounds, CC0 license). GEARS
(Roohani et al., Nature Biotechnology 2024) is a GNN that predicts post-perturbation
gene expression from gene regulatory graphs.

**Phase 0 provided:**
- Tahoe-100M downloaded at `/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/`
  (428.89 GB, 8852 files). Expression data: 3388 parquet files (337.64 GB).
  Metadata: 1033 files (91.16 GB).
- env-delta environment with Python 3.10, PyTorch, scanpy, anndata, datasets.
- Streaming loader verified with pyarrow (10 columns, reads correctly).

**Key risk:** GEARS has a 30% probability of memory issues with Tahoe-100M
(Implementation Plan Section 10.1). The scDataset streaming loader is the
primary mitigation. If OOM occurs, the critical output is documenting the maximum
feasible cell count — this informs Subphase 1.3 Delta baselines planning.

---

## Detailed Instructions

### Step 1: Environment Setup

1. Activate env-delta: `conda activate env-delta`
2. Verify base packages: `python -c "import torch, scanpy, anndata; print('OK')"`
3. Create working directories:
   ```bash
   SCRATCH=/nfs/roberts/scratch/pi_mg269/rag88
   mkdir -p $SCRATCH/delta/methods/gears
   mkdir -p $SCRATCH/delta/test-outputs/gears
   ```

### Step 2: Verify Tahoe-100M Data Access

1. Confirm data path: `ls /nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/`
2. Test streaming loader:
   ```python
   import pyarrow.parquet as pq
   table = pq.read_table(
       '/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/expression/part-00000.parquet'
   )
   print(table.schema)
   print(f"Rows: {len(table)}")
   ```
3. Identify a small test condition (1 cell line, 1 compound) for method testing.
   Document the test condition (cell line name, compound name, number of cells).

### Step 3: Install GEARS

1. **Install from GitHub:**
   ```bash
   pip install git+https://github.com/snap-stanford/GEARS.git
   ```
   If install fails, try:
   - Pinning a specific release tag
   - Installing from a specific commit
   - Manual clone + `pip install -e .`

2. **Verify import:**
   ```python
   import gears
   print(gears.__version__)
   ```
   If import fails, document the error and try alternative install approaches.

### Step 4: Write Data Adapter

GEARS expects AnnData format with specific perturbation metadata. Write an adapter
that bridges Tahoe-100M parquet to GEARS input:

```python
import anndata as ad
import pyarrow.parquet as pq
import numpy as np

def load_tahoe_for_gears(parquet_path, metadata_path, cell_line, compound,
                          max_cells=None):
    """Load a Tahoe-100M perturbation condition for GEARS.

    Returns AnnData with .obs containing perturbation labels.
    """
    # 1. Load expression subset via streaming
    # 2. Filter to specific cell line + compound
    # 3. Convert to AnnData
    # 4. Set .obs with perturbation columns expected by GEARS
    # 5. Optionally cap at max_cells for memory control
    pass
```

Key requirements:
- Stream data from parquet (do NOT load all 100M cells into memory)
- Filter to a specific perturbation condition before converting to AnnData
- Include perturbation labels in `.obs` (compound, dose, cell_type)
- Accept a `max_cells` parameter for memory-limited testing

Save adapter to `../../output/scripts/gears_adapter.py`.

### Step 5: Test Run

1. Load the test condition from Step 2 using the adapter
2. Instantiate GEARS model with default parameters
3. Run a forward pass (single batch, no full training):
   ```python
   # Instantiate model
   # Feed test batch
   # Verify output shape matches expected (predicted expression vector)
   ```
4. If forward pass succeeds, run a few training iterations to verify the
   optimization loop works

### Step 6: Memory Profiling

This is CRITICAL — the primary risk for GEARS is OOM.

```python
import torch
# Before loading data
print(f"Baseline GPU: {torch.cuda.memory_allocated()/1e9:.2f} GB")

# After loading data
print(f"After data load: {torch.cuda.memory_allocated()/1e9:.2f} GB")

# After model instantiation
print(f"After model: {torch.cuda.memory_allocated()/1e9:.2f} GB")

# After forward pass
print(f"After forward: {torch.cuda.memory_allocated()/1e9:.2f} GB")
print(f"Peak GPU: {torch.cuda.max_memory_allocated()/1e9:.2f} GB")
```

**If OOM occurs:**
1. Start with max_cells=10000, test forward pass
2. Double: 20K, 50K, 100K — find the ceiling
3. Document the maximum feasible cell count and corresponding GPU memory
4. Test whether gradient checkpointing or mixed precision helps
5. This ceiling is the KEY output if OOM occurs — it determines how GEARS
   will be used in Subphase 1.3 baselines

### Step 7: Setup Report

Write `../../output/task-004-gears-setup-report.md`:

| Metric | Value |
|--------|-------|
| Installed | yes/no |
| Version | X.Y.Z |
| Loads Tahoe subset | yes/no |
| Produces predictions | yes/no |
| Peak GPU memory | X.XX GB |
| Max feasible cells | N (if OOM) |
| Install command | `pip install ...` |
| Test condition | cell_line / compound / N cells |
| Notes | ... |

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| `../../tasks/task-004-gears-setup.md` | This task specification |
| `../../../../../Proposal/Delta.md` (Sections 3-4) | GEARS details, Tahoe-100M description |
| `../../../../phase-0/subphase-0.1/completion-report.md` (Section 2, Task 002) | Tahoe-100M data details |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../Proposal/ImplementationPlan.md` (Sections 5.3, 11.4) | Method roster, Delta kill criteria |
| `../../../../phase-0/subphase-0.1/envs/env-delta.yml` | Exact env-delta packages |

### DO NOT READ

- Alpha-M or Gamma files (not your track)
- Other SubAgents' task specs or output (not your scope)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)

---

## Output Artifacts

### Code and data artifacts

| Artifact | Path | Format |
|----------|------|--------|
| GEARS data adapter | `../../output/scripts/gears_adapter.py` | Python |
| GEARS test script | `../../output/scripts/gears_test.py` | Python |
| Setup report | `../../output/task-004-gears-setup-report.md` | Markdown |
| Test outputs | HPC scratch: `.../delta/test-outputs/gears/` | Method-specific |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-004-status.md` | `status-report.md` |

---

## Success Criteria (Zero Compromise)

1. [ ] GEARS installed in env-delta (or failure documented with exact error after 2+ attempts)
2. [ ] Data adapter loads Tahoe-100M subset via streaming without loading full dataset
3. [ ] GEARS produces predictions on at least one perturbation condition (or OOM documented)
4. [ ] Peak GPU memory documented at each stage (data load, model init, forward pass)
5. [ ] If OOM: maximum feasible cell count documented at 10K/20K/50K/100K thresholds
6. [ ] Setup report written with all metrics
7. [ ] Status report written to `../../status/task-004-status.md`

---

## Verification

1. `python gears_adapter.py` exits 0 and loads data without OOM
2. `python gears_test.py` produces prediction output (or documents the OOM ceiling)
3. GPU memory values are plausible (4-40 GB range)
4. Setup report has all rows filled

---

## Failure Protocol

1. If GEARS fails to install: document exact error, try 2 alternative approaches
2. If GEARS OOMs: THIS IS EXPECTED (30% probability). The task is NOT failed if
   you document the OOM ceiling. Documenting max feasible cells IS the deliverable.
3. If Tahoe-100M data format is incompatible: document the schema mismatch,
   write a partial adapter that demonstrates the gap
4. Write status report with whatever results you obtained — partial data is valuable
