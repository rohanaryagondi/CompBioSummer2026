---
task_id: "task-003"
title: "BioEmu Batch Generation (50 ProteinGym Proteins)"
subphase: "1.1"
track: gamma
wave: 1
agent: "bioemu-gen"
effort: "5-8 days"
status: planned
created: 2026-04-16
---

# Task 003: BioEmu Batch Generation (50 ProteinGym Proteins)

## Objective

Generate BioEmu conformational ensembles (2,000 backbone conformations per protein)
for the first batch of 50 ProteinGym proteins. This is the foundation of the Gamma
track: these ensembles provide the dynamics features (RMSF, SASA variance, contact
frequencies) that are tested against mutation fitness predictions. The first batch
prioritizes binding and activity assays where dynamics features are expected to
provide the strongest signal.

---

## Context

The Gamma proposal tests whether conformational dynamics features improve mutation
fitness prediction beyond sequence-only methods on ProteinGym (217 DMS assays, 97+
methods). Zero existing methods use explicit dynamics features. BioEmu v1.3.1
generates equilibrium backbone conformations from sequence in minutes per protein.

**Phase 0 findings critical for this task:**
- BioEmu API: `from bioemu.sample import main(sequence, num_samples, output_dir, ...)`.
  The `BioEmuSampler` class does NOT exist — do NOT attempt to use it.
- BioEmu outputs 5 atoms per residue (N, CA, C, CB, O) — backbone only, no sidechains.
- Generation times: ~4.4 min for 58 residues (BPTI), ~9.5 min for 129 residues (HEWL).
  Approximately proportional to sequence length.
- The env-bioemu dependency chain is fragile: torch 2.7.1+cu128, tensorflow-cpu 2.15.1,
  protobuf 4.25.9. Do NOT modify these pinned versions.
- First BioEmu run needs internet access from the compute environment for MSA server
  queries. Use `cache_embeds_dir` to cache embeddings after first run.
- BioEmu needs ~34 GB VRAM (tested on RTX 5000 Ada / RTX 5090 in Phase 0).

---

## Detailed Instructions

### Step 1: Download ProteinGym Reference Data

1. Activate env-bioemu: `conda activate env-bioemu`
2. Download ProteinGym reference files:
   ```bash
   # ProteinGym substitution reference
   wget https://marks.hms.harvard.edu/proteingym/DMS_substitutions.csv
   # Or check PyPI/GitHub: https://github.com/OATML-Markslab/ProteinGym
   ```
3. Load and inspect the reference:
   ```python
   import pandas as pd
   ref = pd.read_csv('DMS_substitutions.csv')
   print(ref.columns.tolist())
   print(ref['assay_type'].value_counts())
   ```
4. Identify columns: protein name, UniProt ID, assay type, sequence length, etc.

### Step 2: Select 50 Proteins

**Selection criteria (in priority order):**

1. **Single chain only.** BioEmu handles monomeric proteins. Exclude complexes,
   multi-chain entries, and proteins requiring cofactors for folding.
2. **Length <= 300 residues.** BioEmu generation time scales with length. At 300
   residues, estimate ~45-60 min per protein. Longer proteins are deferred to batch 2.
3. **Assay type distribution:**
   - ~15-20 binding assays (highest dynamics signal expected)
   - ~15-20 activity/catalytic assays (high dynamics signal)
   - ~8-10 expression assays
   - ~5-8 stability assays (low dynamics signal expected, but needed for contrast)
4. **Diverse protein families.** Avoid oversampling a single fold or organism.
5. **ProteinGym data quality.** Prefer assays with >500 variants measured and
   established RSALOR baselines.

Write the selection table to `../../output/task-003-protein-selection.csv` with
columns: protein_name, uniprot_id, assay_id, assay_type, sequence_length,
num_variants, rsalor_spearman, selection_reason.

### Step 3: Extract Sequences

1. For each selected protein, extract the wild-type sequence:
   - From ProteinGym reference if available
   - From UniProt if not in reference
2. Write sequences to `../../output/task-003-sequences.fasta`
3. Verify sequence lengths match ProteinGym metadata

### Step 4: BioEmu Ensemble Generation

1. Set up output directory on HPC scratch:
   ```bash
   SCRATCH=/nfs/roberts/scratch/pi_mg269/rag88
   mkdir -p $SCRATCH/gamma/bioemu-ensembles/batch1
   ```

2. Set up embedding cache:
   ```bash
   mkdir -p $SCRATCH/gamma/bioemu-cache
   ```

3. **First protein — run interactively or on login node** to cache MSA embeddings:
   ```python
   from bioemu.sample import main
   main(
       sequence="MKTL...",  # first protein sequence
       num_samples=2000,
       output_dir="/path/to/scratch/gamma/bioemu-ensembles/batch1/PROTEIN_001",
       cache_embeds_dir="/path/to/scratch/gamma/bioemu-cache"
   )
   ```
   This first run queries the MSA server (needs internet). After this, embeddings
   are cached and subsequent runs do NOT need internet.

4. **Batch remaining proteins via SLURM:**

   Write a wrapper script `scripts/bioemu_generate.py`:
   ```python
   import sys
   from bioemu.sample import main
   
   protein_id = sys.argv[1]
   sequence = sys.argv[2]
   output_dir = sys.argv[3]
   cache_dir = sys.argv[4]
   
   main(sequence=sequence, num_samples=2000,
        output_dir=output_dir, cache_embeds_dir=cache_dir)
   ```

   Submit as SLURM jobs (respect QOS: max 2 pending jobs):
   ```bash
   # Submit 1-2 at a time, monitor completion, submit next batch
   sbatch --job-name=bioemu-P001 \
          --partition=gpu_h200 \
          --gres=gpu:1 \
          --time=02:00:00 \
          --mem=48G \
          --output=slurm-bioemu-%j.out \
          scripts/bioemu_batch.sbatch PROTEIN_001 "MKTL..." /path/to/out /path/to/cache
   ```

   Alternatively, write a master script that submits jobs sequentially with
   dependency chaining to respect QOS limits.

5. **Monitor progress:** Track completed proteins in a log file.
   Expected: ~20 min per protein average, ~17 GPU-hours total for 50 proteins.

### Step 5: Validation

For each generated ensemble:
1. Verify output directory contains 2,000 PDB files (or a single multi-model PDB)
2. Check atom count: each frame should have 5 atoms per residue (N, CA, C, CB, O)
3. Verify no truncated or empty files
4. Record generation time per protein

### Step 6: Summary

Write generation summary to `../../output/task-003-generation-summary.md`:
- Total proteins attempted: 50
- Successfully generated: N
- Failed: list with reasons
- Total GPU-hours used
- Average generation time per protein
- Storage used

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| `../../tasks/task-003-bioemu-batch-gen.md` | This task specification |
| `../../../../../Proposal/Gamma.md` | Gamma pipeline details, ProteinGym context |
| `../../../../../shared/notes/0.1-bioemu-disulfide.md` | BioEmu API details, generation times |
| `../../../../phase-0/subphase-0.1/envs/env-bioemu.yml` | Exact env-bioemu package versions |
| `../../../../phase-0/subphase-0.1/completion-report.md` | BioEmu API notes (Section 2, Task 001) |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../Proposal/Combined-Alpha-Gamma.md` | How Gamma feeds into combined paper |

### DO NOT READ

- Alpha-M specific files (not your track)
- Delta files (not your track)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)

---

## Output Artifacts

### Code and data artifacts

| Artifact | Path | Format |
|----------|------|--------|
| Protein selection table | `../../output/task-003-protein-selection.csv` | CSV |
| Sequences | `../../output/task-003-sequences.fasta` | FASTA |
| Generation script | `../../output/scripts/bioemu_generate.py` | Python |
| SLURM batch script | `../../output/scripts/bioemu_batch.sbatch` | Shell |
| Ensembles (50 dirs) | HPC scratch: `/nfs/roberts/scratch/.../gamma/bioemu-ensembles/batch1/` | PDB |
| Embedding cache | HPC scratch: `/nfs/roberts/scratch/.../gamma/bioemu-cache/` | BioEmu format |
| Generation summary | `../../output/task-003-generation-summary.md` | Markdown |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-003-status.md` | `status-report.md` |

---

## Success Criteria (Zero Compromise)

1. [ ] 50 ProteinGym proteins selected with documented rationale and assay type distribution
2. [ ] >=45 of 50 proteins have 2,000 conformations successfully generated
3. [ ] Selection covers all 4 major assay types (binding, activity, expression, stability)
4. [ ] Output validated: correct atom count, no truncated files
5. [ ] Generation times and GPU usage logged per protein
6. [ ] Protein selection CSV written with all metadata columns
7. [ ] Generation summary document written
8. [ ] Status report written to `../../status/task-003-status.md`

---

## Verification

1. `ls /path/to/scratch/gamma/bioemu-ensembles/batch1/ | wc -l` shows >=45 directories
2. Each directory contains 2,000 PDB files (or verified multi-model PDB)
3. Spot-check 3 proteins: atom count = 5 * sequence_length per frame
4. Generation summary total GPU-hours is ~15-20 hours (not anomalously high)

---

## Failure Protocol

1. If BioEmu fails on a protein: log the error, skip to next protein, continue batch
2. If MSA server is unreachable: try login node, try cached embeddings from Phase 0
3. If GPU OOM: try smaller proteins first, document memory threshold
4. If >5 proteins fail: investigate common cause, adjust batch parameters
5. DO NOT modify env-bioemu package versions — the dependency chain is fragile
6. Write status report with partial results even if not all 50 complete
