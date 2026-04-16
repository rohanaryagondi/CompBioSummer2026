# SubAgent: BioEmu Batch Generation (50 ProteinGym Proteins)

You are a **SubAgent** executing task-003 in subphase 1.1 of the CompBioSummer2026
execution pipeline. You have a narrowly scoped task with explicit success criteria.
Execute your task, write your documentation, and report your results.

---

## Your Task

**Task ID:** task-003
**Title:** BioEmu batch generation (50 ProteinGym proteins)
**Track:** Gamma
**Subphase:** 1.1
**Estimated effort:** 5-8 days

---

## What You Must Accomplish (Zero Compromise)

1. Download ProteinGym reference metadata and select 50 proteins
2. Prioritize binding and activity assays (where dynamics signal is strongest)
3. Generate 2,000 BioEmu backbone conformations per protein
4. Validate output: correct atom count (5 per residue), no truncated files
5. Log generation times and GPU usage per protein
6. Write protein selection table and generation summary
7. Write status report to `../../status/task-003-status.md`

**CRITICAL API NOTE:** BioEmu API is `from bioemu.sample import main(sequence,
num_samples, output_dir, ...)`. The `BioEmuSampler` class does NOT exist. Use
`cache_embeds_dir` parameter to cache MSA embeddings.

---

## What You Read

### MUST READ (before starting)

| File | Why |
|------|-----|
| `../../tasks/task-003-bioemu-batch-gen.md` | Full task specification with selection criteria |
| `../../../../../Proposal/Gamma.md` | Gamma pipeline, ProteinGym context, assay types |
| `../../../../../shared/notes/0.1-bioemu-disulfide.md` | BioEmu API details, generation times |
| `../../../../phase-0/subphase-0.1/completion-report.md` (Section 2, Task 001, 004) | BioEmu env details |
| `../../../../phase-0/subphase-0.1/envs/env-bioemu.yml` | Exact package versions |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../Proposal/Combined-Alpha-Gamma.md` | How Gamma feeds into combined paper |

### DO NOT READ

- Alpha-M specific files, Delta files (not your track)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)

---

## Detailed Instructions

Follow `../../tasks/task-003-bioemu-batch-gen.md`. Key points:

1. **Environment:** `conda activate env-bioemu`. Do NOT modify pinned package versions.
2. **ProteinGym data:** Download DMS_substitutions.csv reference
3. **Select 50 proteins:** Single-chain, <=300 residues, balanced assay types,
   ~20 binding/activity, ~15 expression, ~15 stability
4. **First protein on login node** (needs internet for MSA server). Cache embeddings.
5. **Batch via SLURM:** Respect QOS limit (max 2 pending jobs). ~20 min/protein.
6. **Output:** `/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch1/`
7. **Cache:** `/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-cache/`
8. **Validate:** 2,000 PDB files per protein, 5 atoms per residue

---

## What You Write

| Artifact | Path | Description |
|----------|------|-------------|
| Protein selection CSV | `../../output/task-003-protein-selection.csv` | 50 proteins with metadata |
| Sequences FASTA | `../../output/task-003-sequences.fasta` | Wild-type sequences |
| Generation script | `../../output/scripts/bioemu_generate.py` | Wrapper script |
| SLURM script | `../../output/scripts/bioemu_batch.sbatch` | Batch submission |
| Ensembles | HPC scratch (path above) | 50 dirs of PDB files |
| Generation summary | `../../output/task-003-generation-summary.md` | Stats and results |
| Status report | `../../status/task-003-status.md` | Task completion status |

---

## Verification

1. [ ] >=45 of 50 protein directories created with 2,000 PDB files each
2. [ ] Spot-check 3 proteins: atom count = 5 * sequence_length per frame
3. [ ] Selection covers binding, activity, expression, and stability assays
4. [ ] Generation summary has total GPU-hours and per-protein timing
5. [ ] Status report written

---

## If Something Goes Wrong

1. If a protein fails: log error, skip, continue batch. Do NOT stop the whole run.
2. If MSA server unreachable: run first protein on login node for caching
3. If GPU OOM: try smaller proteins first, document memory threshold
4. Do NOT modify env-bioemu packages — dependency chain is fragile
5. Write status report with partial results even if <45 proteins complete
