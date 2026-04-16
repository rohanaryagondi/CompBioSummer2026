---
task_id: "task-006"
title: "scGPT and CPA Setup on Tahoe-100M"
subphase: "1.1"
track: delta
wave: 2
agent: "scgpt-cpa-setup"
effort: "2-3 days"
status: planned
created: 2026-04-16
---

# Task 006: scGPT and CPA Setup on Tahoe-100M

## Objective

Install, configure, and verify scGPT (Transformer) and CPA (VAE) — two perturbation
prediction methods — on the Tahoe-100M dataset. Each method must load Tahoe-100M
data and produce predictions on at least one perturbation condition. Together with
GEARS (task-004), these provide early D3 gate evidence (3 of 5 Tier 1 methods
needed by June 6).

These two methods share similar data patterns (both use AnnData) and have moderate
risk profiles, making them suitable to handle in a single focused agent session.

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
1. GEARS (GNN) — task-004 (separate agent)
2. **scGPT (Transformer) — this task**
3. **CPA (VAE) — this task**
4. scFoundation (Large model) — Subphase 1.2
5. Tahoe-x1 (3B foundation model) — Subphase 1.2

**Key risk:** CPA has a 25% probability of dependency conflicts (last release 2023).
scGPT is lower risk but requires downloading pretrained weights.

---

## Detailed Instructions

### Step 1: Environment Setup

1. Activate env-delta: `conda activate env-delta`
2. Verify base packages: `python -c "import torch, scanpy, anndata; print('OK')"`
3. Create working directories:
   ```bash
   SCRATCH=/nfs/roberts/scratch/pi_mg269/rag88
   mkdir -p $SCRATCH/delta/methods/{scgpt,cpa}
   mkdir -p $SCRATCH/delta/test-outputs/{scgpt,cpa}
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

### Step 3: scGPT Setup

1. **Install:**
   ```bash
   pip install scgpt
   # Or from GitHub: pip install git+https://github.com/bowang-lab/scGPT.git
   ```
   If install fails, try pinning specific version or installing from a tagged release.

2. **Download pretrained model:**
   ```python
   # scGPT provides pretrained checkpoints
   # Check documentation for download instructions
   # Typically: wget or huggingface_hub download
   ```
   Document model size and download location on scratch.

3. **Data adapter:** scGPT uses a specific tokenized input format. Write an adapter
   from Tahoe-100M parquet to scGPT's expected input:
   ```python
   import anndata as ad
   import pyarrow.parquet as pq
   
   def load_tahoe_for_scgpt(parquet_path, metadata_path, cell_line, compound,
                              max_cells=None):
       """Load Tahoe-100M subset and prepare for scGPT inference.
       
       scGPT tokenizes gene expression into bins. The adapter must:
       1. Load expression data via streaming
       2. Filter to the test condition
       3. Format as AnnData with gene names as .var_names
       4. Apply scGPT's tokenization (binning) if required
       """
       pass
   ```
   Save to `../../output/scripts/scgpt_adapter.py`.

4. **Test run:**
   - Load test condition using the adapter
   - Load pretrained scGPT model
   - Run inference (zero-shot perturbation prediction or fine-tune on small subset)
   - Verify predictions are produced in expected format
   
5. **Document:** Model size, VRAM usage, inference time per batch.
   ```python
   import torch
   print(f"Peak GPU: {torch.cuda.max_memory_allocated()/1e9:.2f} GB")
   ```

### Step 4: CPA Setup

1. **Install:**
   ```bash
   pip install cpa-tools  # or from GitHub
   # CPA last release 2023 — may have dependency conflicts
   ```
   If install fails due to version conflicts:
   - Try installing with pinned dependencies: `pip install cpa-tools==X.Y.Z`
   - Try from GitHub: `pip install git+https://github.com/facebookresearch/CPA.git`
   - If torch/anndata version conflicts, try `--no-deps` then install missing deps
   - Document the specific conflict and any workaround

2. **Data adapter:** CPA expects AnnData with specific `.obs` columns
   (perturbation, dose, cell_type). Write adapter:
   ```python
   def load_tahoe_for_cpa(parquet_path, metadata_path, cell_line, compound,
                           max_cells=None):
       """Load Tahoe-100M subset for CPA.
       
       CPA requires .obs with:
       - 'perturbation': compound name
       - 'dose': dose value
       - 'cell_type': cell line name
       - 'condition': combined perturbation+dose string
       """
       pass
   ```
   Save to `../../output/scripts/cpa_adapter.py`.

3. **Test run:**
   - Load test condition as AnnData using adapter
   - Instantiate CPA model with default parameters
   - Run a few training iterations (not full training — verify the loop works)
   - Verify: loss decreases over iterations, latent space is computed, predictions
     are generated
   
4. **Document:** Training loop mechanics, memory usage, expected training time
   for full dataset.

### Step 5: Method Comparison Table

Write `../../output/task-006-scgpt-cpa-setup-report.md`:

| Method | Installed | Version | Loads Tahoe | Produces Output | Peak GPU Memory | Notes |
|--------|-----------|---------|-------------|----------------|-----------------|-------|
| scGPT | yes/no | X.Y | yes/no | yes/no | X.XX GB | ... |
| CPA | yes/no | X.Y | yes/no | yes/no | X.XX GB | ... |

Include for each method: install command used, data adapter code path, test
condition details, pretrained model location (scGPT), error messages for failures.

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| `../../tasks/task-006-scgpt-cpa-setup.md` | This task specification |
| `../../../../../Proposal/Delta.md` (Sections 3-4) | Method details, Tahoe-100M description |
| `../../../../phase-0/subphase-0.1/completion-report.md` (Section 2, Task 002) | Tahoe-100M data details |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../Proposal/ImplementationPlan.md` (Sections 5.3, 11.4) | Method roster, Delta kill criteria |
| `../../../../phase-0/subphase-0.1/envs/env-delta.yml` | Exact env-delta packages |
| `../../output/task-004-gears-setup-report.md` | GEARS results (if available — check existence first) |

### DO NOT READ

- Alpha-M or Gamma files (not your track)
- Other SubAgents' task specs (except task-004 report if helpful)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)

---

## Output Artifacts

### Code and data artifacts

| Artifact | Path | Format |
|----------|------|--------|
| scGPT data adapter | `../../output/scripts/scgpt_adapter.py` | Python |
| CPA data adapter | `../../output/scripts/cpa_adapter.py` | Python |
| scGPT test script | `../../output/scripts/scgpt_test.py` | Python |
| CPA test script | `../../output/scripts/cpa_test.py` | Python |
| Setup report | `../../output/task-006-scgpt-cpa-setup-report.md` | Markdown |
| Test outputs | HPC scratch: `.../delta/test-outputs/{scgpt,cpa}/` | Method-specific |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-006-status.md` | `status-report.md` |

---

## Success Criteria (Zero Compromise)

1. [ ] scGPT installed with pretrained weights downloaded
2. [ ] scGPT runs inference on at least one Tahoe-100M test condition
3. [ ] CPA installed (or dependency conflict documented with exact error)
4. [ ] CPA training loop completes on test batch (or failure documented)
5. [ ] >=1 of 2 methods produces predictions on a perturbation condition
6. [ ] Data adapter scripts written for each method
7. [ ] Peak GPU memory documented for each working method
8. [ ] Setup report written with comparison table
9. [ ] Status report written to `../../status/task-006-status.md`

---

## Verification

1. For each working method: adapter loads data + test script produces output
2. Output files exist in test-outputs directory
3. GPU memory values are plausible (4-40 GB range)
4. Setup report has both methods covered with clear pass/fail status

---

## Failure Protocol

1. If scGPT fails to install or download weights: document error, try alternative
   sources (PyPI vs GitHub vs HuggingFace). scGPT is lower risk — push hard.
2. If CPA has 2023 compatibility issues: this is EXPECTED (25% probability).
   Document the specific conflict. Try `--no-deps` install + manual dep resolution.
   If unresolvable, mark CPA as failed and focus on scGPT.
3. If both fail: document everything. D3 gate needs 3 of 5 methods total;
   scFoundation and Tahoe-x1 come in Subphase 1.2 as backup.
4. Write status report with whatever results you obtained
