---
task_id: "task-004"
title: "Delta Method Setup (GEARS, scGPT, CPA)"
subphase: "1.1"
track: delta
wave: 2
agent: "delta-setup"
effort: "3-5 days"
status: planned
created: 2026-04-16
---

# Task 004: Delta Method Setup (GEARS, scGPT, CPA)

## Objective

Install, configure, and verify the first 3 Delta Tier 1 perturbation prediction
methods (GEARS, scGPT, CPA) on the Tahoe-100M dataset. Each method must
successfully load Tahoe-100M data via the scDataset streaming loader verified in
Phase 0 and produce predictions on at least one perturbation condition. This
provides early D3 gate evidence (3 of 5 Tier 1 methods needed by June 6).

---

## Context

The Delta track (PerturbMark) benchmarks perturbation prediction methods on
Tahoe-100M (100M cells, 50 cell lines, 379 compounds, CC0 license). The field
cannot agree whether DL outperforms linear baselines (Ahlmann-Eltze et al. 2025
says no; Miller et al. 2025 says yes under calibrated metrics). Delta resolves
this with neutral, calibrated evaluation.

**Phase 0 provided:**
- Tahoe-100M downloaded at `/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/`
  (428.89 GB, 8852 files). Expression data: 3388 parquet files (337.64 GB).
  Metadata: 1033 files (91.16 GB).
- env-delta environment with Python 3.10, PyTorch, scanpy, anndata, datasets.
- Streaming loader verified with pyarrow (10 columns, reads correctly).

**Tier 1 methods for Delta (from Implementation Plan Section 5.3):**
1. GEARS (GNN) — this task
2. scGPT (Transformer) — this task
3. CPA (VAE) — this task
4. scFoundation (Large model) — Subphase 1.2
5. Tahoe-x1 (3B foundation model) — Subphase 1.2

**Key risk:** GEARS has a 30% probability of memory issues with Tahoe-100M
(Implementation Plan Section 10.1). The scDataset streaming loader is the
primary mitigation.

---

## Detailed Instructions

### Step 1: Environment Setup

1. Activate env-delta: `conda activate env-delta`
2. Verify base packages: `python -c "import torch, scanpy, anndata; print('OK')"`
3. Create a working directory:
   ```bash
   SCRATCH=/nfs/roberts/scratch/pi_mg269/rag88
   mkdir -p $SCRATCH/delta/methods/{gears,scgpt,cpa}
   mkdir -p $SCRATCH/delta/test-outputs
   ```

### Step 2: Verify Tahoe-100M Data Access

1. Confirm data path: `ls /nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/`
2. Test streaming loader:
   ```python
   import pyarrow.parquet as pq
   # Load first parquet file to verify schema
   table = pq.read_table('/nfs/roberts/scratch/.../tahoe-100m/expression/part-00000.parquet')
   print(table.schema)
   print(f"Rows: {len(table)}")
   ```
3. Identify a small test condition (1 cell line, 1 compound) for method testing.
   Document the test condition (cell line name, compound name, number of cells).

### Step 3: GEARS Setup

1. **Install:**
   ```bash
   pip install git+https://github.com/snap-stanford/GEARS.git
   # If install fails, try pinning version or installing from specific commit
   ```

2. **Data adapter:** GEARS expects AnnData format. Write an adapter that:
   - Loads a subset of Tahoe-100M via scDataset/pyarrow streaming
   - Converts to AnnData format expected by GEARS
   - Includes perturbation labels (compound, dose, cell line)
   ```python
   import anndata as ad
   import scanpy as sc
   # Load subset -> convert to AnnData -> set .obs with perturbation info
   ```

3. **Test run:**
   - Load the test condition identified in Step 2
   - Instantiate GEARS model with default parameters
   - Run a forward pass (single batch, no full training)
   - Verify output shape matches expected (predicted expression vector)

4. **Memory profiling:**
   ```python
   import torch
   print(f"GPU memory: {torch.cuda.memory_allocated()/1e9:.1f} GB")
   ```
   Document peak memory for: data loading, model instantiation, forward pass.

5. **If OOM:** Try reducing number of loaded cells (cap at 10K, 50K, 100K).
   Document the maximum feasible batch size.

### Step 4: scGPT Setup

1. **Install:**
   ```bash
   pip install scgpt
   # Or from GitHub: pip install git+https://github.com/bowang-lab/scGPT.git
   ```

2. **Download pretrained model:**
   ```python
   # scGPT provides pretrained checkpoints
   # Check documentation for download instructions
   # Typically: wget or huggingface_hub download
   ```

3. **Data adapter:** scGPT may need data in specific tokenized format.
   Write adapter from Tahoe-100M parquet to scGPT input format.

4. **Test run:**
   - Load test condition
   - Load pretrained model
   - Run inference (zero-shot or fine-tune on small subset)
   - Verify predictions are produced

5. **Document:** Model size, VRAM usage, inference time per batch.

### Step 5: CPA Setup

1. **Install:**
   ```bash
   pip install cpa-tools  # or from GitHub
   # CPA last release 2023 — may have dependency conflicts
   ```
   If install fails due to version conflicts:
   - Try installing in a sub-environment or with pinned dependencies
   - Document the specific conflict and workaround

2. **Data adapter:** CPA expects AnnData with specific .obs columns
   (perturbation, dose, cell_type). Map Tahoe-100M metadata accordingly.

3. **Test run:**
   - Load test condition as AnnData
   - Instantiate CPA model
   - Run a few training iterations (not full training — just verify the loop works)
   - Verify: loss decreases, latent space is computed, predictions are generated

4. **Document:** Training loop mechanics, expected training time for full dataset.

### Step 6: Method Comparison Table

Write `../../output/task-004-method-setup-report.md`:

| Method | Installed | Version | Loads Tahoe | Produces Output | Peak GPU Memory | Notes |
|--------|-----------|---------|-------------|----------------|-----------------|-------|
| GEARS | yes/no | X.Y | yes/no | yes/no | X GB | ... |
| scGPT | yes/no | X.Y | yes/no | yes/no | X GB | ... |
| CPA | yes/no | X.Y | yes/no | yes/no | X GB | ... |

Include: install commands used, data adapter code paths, test condition details,
error messages for failures.

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| `../../tasks/task-004-delta-method-setup.md` | This task specification |
| `../../../../../Proposal/Delta.md` (Sections 3-4) | Method details, Tahoe-100M description |
| `../../../../phase-0/subphase-0.1/completion-report.md` (Section 2, Task 002) | Tahoe-100M data details |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../Proposal/ImplementationPlan.md` (Sections 5.3, 11.4) | Method roster, Delta kill criteria |
| `../../../../phase-0/subphase-0.1/envs/env-delta.yml` | Exact env-delta packages |

### DO NOT READ

- Alpha-M or Gamma files (not your track)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)

---

## Output Artifacts

### Code and data artifacts

| Artifact | Path | Format |
|----------|------|--------|
| GEARS data adapter | `../../output/scripts/gears_adapter.py` | Python |
| scGPT data adapter | `../../output/scripts/scgpt_adapter.py` | Python |
| CPA data adapter | `../../output/scripts/cpa_adapter.py` | Python |
| Method setup report | `../../output/task-004-method-setup-report.md` | Markdown |
| Test outputs | HPC scratch: `.../delta/test-outputs/` | Method-specific |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-004-status.md` | `status-report.md` |

---

## Success Criteria (Zero Compromise)

1. [ ] GEARS installed and loads Tahoe-100M subset without OOM (or OOM documented with max feasible size)
2. [ ] scGPT installed with pretrained weights and runs inference on test condition
3. [ ] CPA installed and training loop completes on test batch (or failure documented)
4. [ ] >=2 of 3 methods produce predictions on at least one perturbation condition
5. [ ] Peak GPU memory documented for each method
6. [ ] Data adapter scripts written for each method (Tahoe-100M -> method input format)
7. [ ] Method setup report written with comparison table
8. [ ] Status report written to `../../status/task-004-status.md`

---

## Verification

1. For each working method: `python adapter.py && python test_method.py` exits 0
2. Output files exist in test-outputs directory
3. GPU memory values are plausible (4-40 GB range)
4. Method setup report covers all 3 methods with clear status

---

## Failure Protocol

1. If a method fails to install: document exact error, try 2 alternative approaches, then mark as failed
2. If a method OOMs: document max feasible cell count, suggest mitigation for Subphase 1.3
3. If CPA has 2023 compatibility issues: this is expected (25% probability). Document and move on.
4. Even if only 1 of 3 methods works, the task provides value — document everything
5. D3 gate (June 6) needs 3 of 5 methods total; scFoundation and Tahoe-x1 come in Subphase 1.2
