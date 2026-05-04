---
agent: "bioemu-batch2"
task_id: "task-004"
subphase: "1.2"
date: 2026-04-19
status: in-progress
---

# BioEmu Batch 2 Summary (Sub 1.2 task-004)

**Status:** stub -- will be populated as proteins complete over the next
7-10 days. First SLURM batch submitted 2026-04-19T00:30Z on gpu partition
(RTX 5000 Ada).

## Manifest Overview

| Metric | Value |
|--------|-------|
| Candidates compiled (post-filter) | 103 (30-600 aa, ProteinGym minus batch-1 overlap) |
| Passed disorder screen | 93 |
| Excluded by disorder screen | 10 (7 disorder_fraction>0.60, 3 foldindex_global<-0.20) |
| Manifest rows (final batch 2) | 93 |
| SLURM batches of ~10 | 10 (batch 10 = 3 proteins: indices 90-92) |

### Class breakdown

| Class | Count | Pass rate | num_samples per protein | Class total samples |
|-------|------:|----------:|-----------------------:|-------------------:|
| structured_globular | 53 | 0.92 | 2,827 | 149,831 |
| idp_like | 21 | 0.47 | 5,532 | 116,172 |
| large_globular_long | 19 | 0.60 | 4,334 | 82,346 |
| transmembrane | 0 | 0.70 | 3,715 | 0 |
| multi_domain_metastable | 0 | 0.23 | 11,305 | 0 |
| **Total** | **93** | — | — | **348,349** |

(Batch 2 selection happens to have zero transmembrane or multi-domain
metastable candidates. The ProteinGym proteins with >3 hydrophobic runs
are mostly already in batch 1, e.g. OPSD/ADRB2/CCR5/GLPA/KCNE1.)

## Per-Protein Status Table (populated over 7-10 days)

Fill in from `--status` query (`bash submit_bioemu_batch2.sh --status`):

| idx | UniProt_ID | Length | Class | Expected pass | Actual pass | Conformations | Status |
|---:|------------|------:|-------|--------------:|-----------:|--------------:|:------:|
| 0 | GCN4_YEAST | 281 | idp_like | 0.47 | TBD | TBD | pending |
| 1 | DLG4_RAT | 558 | idp_like | 0.47 | TBD | TBD | pending |
| 2 | ACE2_HUMAN | 554 | idp_like | 0.47 | TBD | TBD | pending |
| ... | ... | ... | ... | ... | ... | ... | ... |

(Full table populated by HeadAI at subphase close. See
`batch2_manifest.csv` for the authoritative ordered protein list.)

## SLURM Job IDs

| Job ID | Name | Array | Partition | Submitted | Purpose |
|-------:|------|:-----:|:---------:|:---------:|---------|
| 8887441 | ba48ebhw | -- | gpu | 2026-04-19T00:29Z | MSA precache (all 93, one GPU pass) |
| 8887446 | qk5s2dzo | 0-9 | gpu | 2026-04-19T00:30Z | Generation batch 1 (proteins 0-9) |

(Additional batches 2-10 to be submitted by HeadAI as earlier batches
complete and QOS pending slots become available. See `submit_bioemu_batch2.sh
--batch N` where N goes 2..10.)

## Expected Resource Usage

| Resource | Estimate | Notes |
|----------|---------:|-------|
| GPU-hours | ~250 | Sum of per-protein RTX 5000 Ada time (class-weighted) |
| SU consumption | ~3,750 | 15 SU/hr × ~250 GPU-hrs (RTX 5000 Ada) |
| Storage | ~80 GB | scratch batch2/ dir; ~850 MB/protein avg |
| Wall time | 7-10 days | Limited by QOS pending queue (2 per user) |

## Disorder-Screen Exclusions (10 proteins)

Proteins excluded from batch 2 per disorder screen (sequence-based TOP-IDP +
FoldIndex heuristic; see `disorder_screen.py` for the calibration). These
are flagged for alternative treatment (e.g., domain extraction if the DMS
is regional) but NOT included in batch 2 generation:

| Protein ID | Length | Reason |
|------------|------:|--------|
| TAT_HV1BR_Fernandes_2016 | 86 | disorder_fraction=0.70>0.60 |
| CUE1_YEAST_Tsuboyama_2023_2MYX | 52 | disorder_fraction=0.69>0.60 |
| YAIA_ECOLI_Tsuboyama_2023_2KVT | 52 | disorder_fraction=0.65>0.60 |
| ISDH_STAAW_Tsuboyama_2023_2LHR | 55 | disorder_fraction=0.80>0.60 |
| SBI_STAAM_Tsuboyama_2023_2JVG | 56 | disorder_fraction=0.84>0.60 |
| DNJA1_HUMAN_Tsuboyama_2023_2LO1 | 65 | disorder_fraction=0.75>0.60 |
| MBD11_ARATH_Tsuboyama_2023_6ACV | 66 | disorder_fraction=0.73>0.60 |
| TCRG1_MOUSE_Tsuboyama_2023_1E0L | 37 | foldindex_global=-0.200<-0.20 |
| PIN1_HUMAN_Tsuboyama_2023_1I6C | 39 | foldindex_global=-0.249<-0.20 |
| NKX31_HUMAN_Tsuboyama_2023_2L9R | 61 | foldindex_global=-0.232<-0.20 |

## Comparison to Sub 1.1 Batch 1

| Metric | Batch 1 | Batch 2 |
|--------|--------:|--------:|
| Proteins submitted | 47 | 93 |
| Proteins successful (target) | 46 | ≥90 |
| Total denoised samples | ~95K | ~348K |
| GPU-hrs on RTX 5000 Ada | ~107 | ~250 (est) |
| Avg sample per protein | ~2,000 | ~3,745 |
| Oversampling applied? | Post-hoc topup | Upstream per-class |
| Disorder pre-screen? | No (YAP1 lost) | Yes (10 excluded) |

## Open Items

- [ ] Precache job `ba48ebhw` (8887441) completion status
- [ ] Batch 1 of 10 generation array (proteins 0-9) completion status
- [ ] Batches 2-10 submission timing (depends on QOS queue)
- [ ] Per-protein `generation_status.json` validation
- [ ] Final per-protein pass-rate vs predicted (feeds back into future batches)
- [ ] Topup round for any protein falling below 2,000 conformations
