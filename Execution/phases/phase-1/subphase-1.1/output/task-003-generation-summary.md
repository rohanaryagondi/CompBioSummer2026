---
task_id: "task-003"
agent: "bioemu-gen"
subphase: "1.1"
type: "generation-summary"
date: 2026-04-16
---

# Task 003: BioEmu Batch Generation Summary

## Overview

Generate BioEmu conformational ensembles (2,000 backbone conformations per protein)
for 50 ProteinGym DMS assays covering 47 unique protein sequences.

## Protein Selection

### Selection Criteria

1. **Single chain only** -- BioEmu is monomeric
2. **Length <= 504 residues** -- extended from 300 to capture binding/activity assays
3. **Assay type diversity** -- prioritized binding and activity (dynamics signal strongest)
4. **>=100 single mutants** -- sufficient for ML training
5. **Diverse protein families** -- enzymes, receptors, signaling, structural proteins
6. **3 paired assays** -- proteins with both expression and function/binding assays

### Assay Type Distribution

| Assay Type | Count | Key Examples |
|------------|-------|--------------|
| Activity | 18 | PTEN, ADRB2, PAI-1, caspases, HRAS, MET RTK |
| OrganismalFitness | 10 | TEM beta-lactamase, VIM-2, DHFR, SUMO1, UBC9 |
| Expression | 8 | KCNE1, KRAS, VKORC1, NUDT15, TPMT, GCK |
| Binding | 7 | KRAS-DARPin, CCR5, HLA-A, GB1, CYP2C9, YAP1 |
| Stability | 7 | estA, Protein A, Protein G, Lambda Cro, EphB2 |
| **Total** | **50** | |

### Paired Assays (Same Protein, Different Readout)

These are especially valuable for the Gamma ablation analysis:

| Protein | UniProt | Assay 1 | Assay 2 |
|---------|---------|---------|---------|
| KRAS | RASK_HUMAN | Binding (DARPin K55) | Expression (abundance) |
| KCNE1 | KCNE1_HUMAN | Activity (function) | Expression |
| VKORC1 | VKOR1_HUMAN | Activity | Expression (abundance) |

### Unique Sequences for BioEmu

47 unique protein sequences (3 proteins have paired assays sharing the same sequence).

### Sequence Length Distribution

- **Minimum:** 55 residues (Protein A, SPA_STAAU)
- **Maximum:** 504 residues (YAP1)
- **Mean:** 220 residues
- **Median:** 198 residues

## BioEmu Generation Parameters

| Parameter | Value |
|-----------|-------|
| Model | bioemu-v1.1 |
| num_samples | 2000 per protein |
| batch_size_100 | 10 (1000 per batch) |
| filter_samples | True (default) |
| base_seed | 42 |
| Output format | 5 atoms/residue (N, CA, C, CB, O) |
| Output files | batch_*.npz, samples.xtc, topology.pdb, sequence.fasta |

## SLURM Submission

| Parameter | Value |
|-----------|-------|
| Partition | gpu |
| GRES | gpu:rtx_5000_ada:1 |
| Memory | 40 GB |
| CPUs | 4 |
| Time limit | 2 hours per protein |
| QOS | normal (max 8 concurrent jobs) |

### Job IDs

| Batch | Array Range | Job ID | Status |
|-------|-------------|--------|--------|
| 1 | 0-9 | 8392692 | SUBMITTED |
| 2 | 10-19 | 8392694 | SUBMITTED |
| 3 | 20-29 | 8392695 | SUBMITTED |
| 4 | 30-39 | 8392696 | SUBMITTED |
| 5 | 40-46 | 8392697 | SUBMITTED |

## Estimated Resources

| Resource | Estimate |
|----------|----------|
| Total GPU-hours | ~13.3 hours |
| Time per protein (avg) | ~17 min |
| Time per protein (min) | ~4.2 min (55 residues) |
| Time per protein (max) | ~38.2 min (504 residues) |
| Wall clock (8 concurrent) | ~2-3 hours |
| Storage per protein | ~10-50 MB (varies with length) |
| Total storage | ~1-2 GB |

## Output Locations

| Artifact | Path |
|----------|------|
| Ensemble data | `/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch1/<UniProt_ID>/` |
| Embedding cache | `/nfs/roberts/scratch/pi_mg269/rag88/.bioemu_embeds_cache/` |
| SLURM logs | `/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch1/logs/` |
| Protein selection CSV | `output/task-003-protein-selection.csv` |
| Sequences FASTA | `output/task-003-sequences.fasta` |
| Generation scripts | `output/scripts/bioemu_generate_single.py`, `output/scripts/bioemu_batch.sbatch` |

## Monitoring Commands

```bash
# Check job status
squeue -u rag88

# Check generation progress
bash output/scripts/submit_bioemu_batches.sh --status

# Check specific job logs
cat /nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch1/logs/bioemu-<JOBID>_<ARRAYIDX>.log

# Retry failed proteins
bash output/scripts/submit_bioemu_batches.sh --retry-failed
```

## Generation Progress (as of 2026-04-16T15:10Z)

| Category | Count | Conformation Range | Notes |
|----------|-------|-------------------|-------|
| Usable (1000+ conf) | 28 | 1,146 – 1,979 | Proteins 0-21, 30-35 |
| Running (H200) | 4 | — | Proteins 26-29, ~30-50 min remaining |
| Retry queue (H200) | 15 | — | Job 8448809, 4h limit, ~4-5h to complete |

### Race Condition Incident

Multi-partition submission (gpu + H200 + B200) caused 14 race-condition failures
when two jobs targeted the same protein simultaneously. BioEmu's `sample.py:247`
resume logic computes `range(existing_num_samples, num_samples, batch_size)` — when
a concurrent job has already written all batch files, `batch_size` becomes 0, crashing
with `ValueError: range() arg 3 must not be zero`. Three additional proteins had
`Not sure why ... already exists` errors from concurrent write collisions.

**Resolution:** Cancelled all duplicate-partition jobs, cleaned corrupted directories,
submitted single-partition H200-only retry (job 8448809).

### Timing Data (from completed proteins)

| Protein | Length (aa) | Time (min) | NPZ Files | Conformations |
|---------|-----------|------------|-----------|---------------|
| CASP3_HUMAN | 258 | 72.3 | 2000 | 1430 |
| KKA2_KLEPN | 264 | 74.3 | 2000 | 1893 |
| A4GRB6_PSEAI | 266 | 75.3 | 2000 | 1739 |
| MET_HUMAN | 287 | 79.0 | 2000 | 1848 |
| BLAT_ECOLX | 286 | 81.4 | 2000 | 1852 |
| CASP7_HUMAN | 281 | 82.7 | 2000 | 1151 |

**Empirical rate:** ~0.3 min per amino acid for full 2000-sample generation.

## Notes

1. BioEmu's `filter_samples=True` removes physically implausible structures.
   Actual sample loss is 5-30% (NOT 1-5% as originally estimated). For 2000
   requested samples, expect 1400-1950 valid conformations. This is sufficient
   for the ProteinGym benchmark.

2. The embedding cache stores per-protein MSA embeddings. First run ~3-5 min
   for embedding computation; subsequent runs reuse the cache.

3. Compute nodes have internet access — MSA server queries work directly.

4. **SU cost:** H200 = 300 SU/hr, RTX 5000 Ada = 15 SU/hr. BioEmu runs on
   either GPU. Prefer RTX 5000 Ada for future batches to minimize SU.

5. **Never submit same protein to multiple partitions.** BioEmu's resume logic
   is not concurrent-safe. Use single-partition submission only.
