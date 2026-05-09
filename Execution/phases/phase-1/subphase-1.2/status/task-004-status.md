---
task_id: "task-004"
agent: "bioemu-batch2"
subphase: "1.2"
status: slurm-10-of-93-complete
date: 2026-04-25
---

# Status Report: Task 004 -- BioEmu Batch 2 (~100 ProteinGym Proteins)

## Summary

Batch 2 is planned, scripted, and has its first SLURM array submitted.
93 proteins (30-600 aa ProteinGym candidates, minus 47 batch-1 overlap,
minus 10 disorder-screened) are in the manifest with per-protein
`num_samples` computed by the Sub 1.1 class-based oversampling formula.
Precache MSA job (all 93 proteins) and generation batch 1 (proteins 0-9)
are both in the SLURM queue on `gpu` (RTX 5000 Ada). HeadAI will submit
batches 2-10 over the next 7-10 days as the QOS queue allows, then
re-invoke this agent for topup + final summary.

---

## What Was Done

1. **Compiled candidate list (Step 1 of task spec).** Downloaded the
   ProteinGym DMS_substitutions.csv (217 rows, 216 DMS assays) from the
   OATML-Markslab GitHub mirror and cached it at
   `output/scripts/proteingym_dms_substitutions.csv`. Wrote
   `compile_candidates.py` which subtracts the 47 batch-1 UniProt IDs,
   applies 30-600 aa length filter, uses `coarse_selection_type` for the
   5-category ProteinGym label, sorts by selection-priority (Binding >
   Activity > Expression > OrganismalFitness > Stability), deduplicates
   per UniProt, and writes `batch2_candidates.csv` (103 rows).

2. **Built disorder pre-screen (Step 2).** IUPred3 and ESMfold are not
   available in env-bioemu, and installing them would violate the
   non-destructive env-management rule. Instead, `disorder_screen.py`
   implements a peer-reviewed sequence-only heuristic:
   - TOP-IDP propensity scale (Campen 2008) with 15-residue sliding
     window and per-residue threshold 0.15
   - FoldIndex (Prilusky 2005) global + sliding 51-residue windows
   - Compositional-bias escape clause (Q+P+G > 0.40 or top-3 amino
     acids > 55%)

   Calibrated against batch-1 controls: YAP1 (0.7% BioEmu pass)
   disorder_fraction=0.607; SYUA (57%) disorder_fraction=0.629; ubiquitin
   (98%) 0.453 (kept); CALM1 (98%) 0.302 (kept); crambin 0.087 (kept).
   Result on batch-2 candidates: 93 pass, 10 excluded (7 by disorder
   fraction, 3 by global FoldIndex).

3. **Built per-protein oversampling manifest (Step 3).** Wrote
   `batch2_manifest_builder.py` which refines the class label using
   sequence features (disorder_fraction, foldindex_global, hydrophobic
   run count, length thresholds) into 5 classes: structured_globular
   (0.92 pass), idp_like (0.47), transmembrane (0.70), multi_domain
   (0.23), large_globular_long (0.60). Computes per-protein `num_samples
   = ceil(2000 / pass_rate * 1.3)` plus memory + wall-time estimates.
   Final breakdown: 53 structured_globular, 21 idp_like, 19
   large_globular_long, 0 transmembrane, 0 multi_domain (batch-2 has no
   TM or multi-domain candidates outside batch 1). Grand total 348,349
   denoised samples planned; outputs `batch2_manifest.csv` and
   `batch2_manifest.fasta`.

4. **Forked submit script (Step 4).** Created
   `submit_bioemu_batch2.sh` and the companion `bioemu_batch2.sbatch`
   which:
   - Force `--partition=gpu --gres=gpu:rtx_5000_ada:1` (SU policy; Sub
     1.1 saved ~21,000 SU by this rule)
   - Runtime `nvidia-smi` safety check: aborts with exit 99 if GPU is
     not RTX 5000 Ada
   - Read per-protein `num_samples` from `batch2_manifest.csv`
   - `--mem=40G` default per Sub 1.1 SPG1 lesson
   - `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` env export
   - Cryptic 8-char job names via `cryptic_jobname()` bash helper
   - Reuse `bioemu_generate_single.py` from Sub 1.1 (no fork needed)
   - MSA cache shared with batch 1 (scratch
     `.bioemu_embeds_cache/` keyed by sha256 of FASTA content)

5. **MSA precache script + SLURM wrapper (Step 5a).** Wrote
   `precache_msa.py` which calls `bioemu.get_embeds.get_colabfold_embeds`
   for each manifest protein, populating the MSA cache without
   invoking denoising. Attempted to run on login node first but hit a
   known env-bioemu numpy 2.x / tensorflow ml_dtypes ABI conflict.
   Workaround: submit `precache_msa.sbatch` to gpu partition instead.
   Cost: ~1-4 GPU-hrs on RTX 5000 Ada (~60 SU).

6. **Submitted first SLURM jobs (Step 5b).**
   - Job 8887441 (`ba48ebhw`): MSA precache, all 93 proteins, single GPU
     pass, gpu partition, 4-hr wall-time limit
   - Job 8887446 (`qk5s2dzo`): Generation batch 1, array 0-9 (10
     proteins), gpu partition, 4-hr per-task wall-time limit

---

## Artifacts Produced

| Artifact | Path | Description | Verified |
|----------|------|-------------|----------|
| ProteinGym reference | `.../output/scripts/proteingym_dms_substitutions.csv` | 216 DMS assays | yes (216 rows) |
| Candidate compiler | `.../output/scripts/compile_candidates.py` | Subtracts batch1 + length filter | yes (script runs clean) |
| Disorder screen | `.../output/scripts/disorder_screen.py` | TOP-IDP + FoldIndex, calibrated | yes (calibration match) |
| Manifest builder | `.../output/scripts/batch2_manifest_builder.py` | Per-protein class + oversampling | yes (script runs clean) |
| Candidates CSV | `.../output/scripts/batch2_candidates.csv` | 103 candidates pre-screen | yes (103 rows) |
| Screened CSV | `.../output/scripts/batch2_screened.csv` | All 103 with exclude_reason | yes (93 pass, 10 exclude) |
| Manifest CSV | `.../output/scripts/batch2_manifest.csv` | 93 rows with num_samples, class, batch_index | yes |
| Manifest FASTA | `.../output/scripts/batch2_manifest.fasta` | SLURM-consumable | yes (93 entries) |
| Submit controller | `.../output/scripts/submit_bioemu_batch2.sh` | Incremental batch submission | yes (--status works) |
| Batch sbatch | `.../output/scripts/bioemu_batch2.sbatch` | Per-protein SLURM job | submitted, pending |
| Precache script | `.../output/scripts/precache_msa.py` | MSA prefetch | submitted via sbatch |
| Precache sbatch | `.../output/scripts/precache_msa.sbatch` | gpu-partition wrapper | submitted |
| Batch 2 summary | `.../output/batch2_summary.md` | Results dashboard (stub, v1) | yes |
| Experiment log | `.../output/task-004-experiment.md` | Reproducibility record | yes |
| Cross-agent note | `.../shared/notes/1.2-bioemu-batch2-passrates.md` | v1 planning + exclusions | yes (stub) |

---

## Success Criteria Evaluation

| # | Criterion | Met? | Evidence |
|---|-----------|------|----------|
| 1 | `disorder_screen.py` exists; `batch2_screened.csv` with ≥100 candidates passing | **partial** | Script exists; 93/103 candidates pass (<100). ProteinGym's actual composition capped candidates at 103 in the 30-600 aa, non-batch-1, non-IDP-exclusion pool. Relaxing length to 650 aa would yield 98 — still not 100. This is not a script limitation but a data-pool limitation; 93 successful generations exceed the 90-protein target in criterion 5. |
| 2 | `batch2_manifest_builder.py` exists; `batch2_manifest.csv` with per-protein num_samples | **yes** | Script exists, manifest built with 93 rows, num_samples in {2827, 4334, 5532} by class |
| 3 | `submit_bioemu_batch2.sh` exists; parameterized (no hardcoded paths) | **yes** | Script exists; reads manifest.csv; supports --cache-first/--batch/--status/--retry-failed |
| 4 | All BioEmu jobs on RTX 5000 Ada; zero on H200/B200 | **yes (so far)** | Submitted jobs 8887441 + 8887446 both on gpu partition (RTX 5000 Ada only). Runtime safety check aborts non-RTX 5000 Ada allocations. |
| 5 | ≥90 of selected proteins reach ≥2,000 physical conformations | **pending** | Generation runs over next 7-10 days. 93-protein manifest gives margin above 90. |
| 6 | `batch2_summary.md` written | **yes (stub v1)** | File created; per-protein status table fills in as generation completes |
| 7 | Cross-agent note `1.2-bioemu-batch2-passrates.md` written | **yes (v1)** | Planning + exclusions documented; v2 pending batch 2 completion |
| 8 | All SLURM job names are 8-char cryptic alphanumeric | **yes** | `ba48ebhw`, `qk5s2dzo` both match pattern |
| 9 | Status report written | **yes** | This file |

**Overall partial status:** All upstream infrastructure is complete and
validated; the deliverable (93 generated ensembles) is in progress across
the SLURM queue. HeadAI tracks downstream via `--status` and re-invokes
for topup + final validation.

---

## Unexpected Findings

1. **ProteinGym candidate pool is finite.** After subtracting batch 1's
   47 UniProts and applying 30-600 aa + disorder + quality filters, only
   103 ProteinGym proteins remain as candidates. The task spec's ~100
   target is achievable but not with much headroom. Downstream implication:
   if pass rates come in below predicted, the available pool for batch 3
   is very small and alternative protein sources (e.g., stability-assay
   Tsuboyama 2023 proteins at 72-aa truncation) would need to be
   considered.

2. **Binding/Activity coverage concentrated in batch 1.** Of 56 ProteinGym
   Binding+Activity DMS assays, 26 are already in batch 1 (Sub 1.1 was
   well-targeted). Only 11 unique Binding+Activity UniProts (12 DMS rows)
   pass the batch-2 filter. IP §12.2 N=57 binding+activity primary analysis
   depends on batch 1's 26 + batch 2's 11 = 37; the remaining ~20 come from
   Expression/OrganismalFitness assays that can proxy Activity. This is
   acceptable but worth flagging to the Delta/Gamma feature-extraction
   subagents.

3. **Zero transmembrane or multi-domain candidates in batch 2.** Most of
   ProteinGym's TM proteins (OPSD, ADRB2, CCR5, GLPA, KCNE1) are already
   in batch 1. Batch 2 is therefore a "clean test" of structured-globular
   + idp_like + large_globular pass rates, without the high-uncertainty
   TM or multi-domain classes.

4. **Tensorflow-cpu numpy 2.x ABI conflict on login node.** env-bioemu
   on login2.bouchet.ycrc.yale.edu cannot `import bioemu` due to
   tensorflow's ml_dtypes vs numpy 2.x incompatibility. Compute nodes are
   unaffected (different library stack). This means the Sub 1.1-style
   `--cache-first` cannot run on login node in the current env state;
   submitted a dedicated gpu-partition precache SLURM job as workaround.

---

## What the Next Agent Needs to Know

### For HeadAI (subsequent batch submissions over 7-10 days)

- **Pending queue:** As of submission, 1 gpu-partition pending job
  (`ba48ebhw`, 8887441). Batch 1 (`qk5s2dzo`, 8887446) is the second.
  Wait for at least the precache job to START RUNNING before submitting
  batch 2.
- **Submission cadence:** Use `bash submit_bioemu_batch2.sh --batch N`
  (N=2..10). The script enforces a 2-pending-job safeguard. Expect
  ~7-10 days total for all 92 proteins (CD19_HUMAN excluded).
- **Status query:** `bash submit_bioemu_batch2.sh --status` shows all
  92 proteins with conformation counts.
- **Retry failed:** `bash submit_bioemu_batch2.sh --retry-failed`
  resubmits any protein with status `failed` or `partial`.

### For the bioemu-batch2 agent (re-invocation for topup + final summary)

- Expect HeadAI to re-invoke with updated `--status` output.
- Populate `batch2_summary.md` per-protein table from all
  `generation_status.json` files.
- Compute actual vs predicted pass rates per class; update cross-agent
  note v2.
- Identify any proteins below 2,000 conformations; compute topup
  `num_samples` via Sub 1.1 topup pattern (`bioemu_topup_single.py` from
  subphase-1.1/output/scripts/).

### For downstream Sub 1.3 feature extraction

- Ensemble outputs at
  `/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/<UniProt_ID>/`
  in the same format as batch 1: `topology.pdb`, `samples.xtc`,
  `batch_*.npz`, `generation_status.json`, `sequence.fasta`.
- 92 protein UniProts listed in `batch2_manifest.csv` column `uniprot_id` (CD19_HUMAN excluded 2026-04-30).
- Per-protein DMS assay ID listed in `batch2_manifest.csv` column
  `protein_id` (format `UniProt_Author_Year_PDB`).

---

## Resource Usage

| Resource | Estimated | Actual |
|----------|-----------|--------|
| GPU-hours | ~250 | ~56 actual (10/93 done) + ~194 remaining est |
| Wall time | 7-10 days | in progress (fair-share blocked) |
| Storage | ~80 GB scratch | ~8 GB actual (10 proteins) + ~72 GB remaining est |
| SLURM job IDs (initial) | -- | 8887441 (precache, cancelled), 8887446 (batch 1 array, partial) |
| SLURM job IDs (retry) | -- | 8903490 (batch 1 retry) |
| SLURM job IDs (current) | -- | 9449458 (x9sok7yl, 41 prots, gpu), 9449459 (l5uw4lsy, 42 prots, gpu) |
| SU consumption | ~3,810 (250 GPU-hrs × 15 SU/hr + 60 SU precache) | ~840 actual + ~2,910 remaining est |

---

## Issues and Blockers

None blocking. One workaround (env-bioemu numpy ABI on login node)
documented above. Proceeding as planned.

---

## Update 2026-04-25: Batch History and Current State

### Job History

| Round | Job IDs | Outcome |
|-------|---------|---------|
| Precache | 8887441 (ba48ebhw) | YCRC-cancelled (NODE_FAIL) |
| Batch 1 array | 8887446 (qk5s2dzo, 10 proteins) | 5 COMPLETED, 4 FAILED (batch_size=0, L>340aa), 1 TIMEOUT |
| Batch 1 retry | 8903490 (t0x8pyfc, 10 proteins) | Resubmitted with length-aware batch_size + 12h walltime |
| Topup round | Various | GCN4, A0A1I9GEU1, OXDA topups completed |
| v1 batch 2-10 arrays | 9098344-47 (kacma9ky+3) | Accidentally cancelled 2026-04-24T22:17Z (partially ran: 10 success) |
| **v2 resubmission (current)** | **9449458 (x9sok7yl, 41 prots, 24h) + 9449459 (l5uw4lsy, 41 prots, 24h; CD19_HUMAN idx 1 cancelled)** | **PENDING (Priority) on gpu** |

### Current Counts

- **10/92 proteins COMPLETE** (≥2,000 conformations each)
- **82 proteins PENDING** in resubmitted arrays (9449458 + 9449459)
- **CD19_HUMAN: EXCLUDED** (2026-04-30). `scancel 9449459_1`. Reason: 1.4% actual pass rate (90 conformations from 6,500 samples). Would need ~188,000 samples (~632 GPU-hours) to reach 2,000 — impractical. 93→92 proteins in batch 2.

### Script Fixes Applied

- `bioemu_batch2.sbatch`: Length-aware `batch_size_100 = max(10, ceil(3 * (L/100)²))` + walltime 4h→12h (short array) / 24h (long array). Eliminates batch_size=0 bug for L>316 aa and prevents TIMEOUTs.

---

## Update 2026-05-05: Round-4 BioEmu reorganization (3-tier walltime split + Standard `gpu` for L<200)

**Trigger.** Arrays 9449458 + 9449459 had been PENDING-Priority on `scavenge_gpu`
for 10+ days due to depressed `pi_mg269` LevelFS (0.27) + the 24h-blanket walltime
hurting backfill. Round-4 BioEmu optimization study identified a 3-tier walltime
split + L<200 cohort move to Standard `gpu` as the highest-value queue-time win.
User approved Round-4 recommendations #1, #2, #6, #7.

**Action.** Reorg subagent (this update) executed the following — order strictly
preserved (submit new arrays FIRST, verify, then cancel old):

1. **Classified 82 PENDING proteins** (from `scontrol show job 9449458/9449459 ArrayTaskId`) into 3 cohorts using `batch2_manifest.csv` length column: 53 short (L<200), 18 medium (L=200-499), 11 long (L≥500). Sums to 82 ✓.

2. **Wrote 3 new sbatch files** in `output/scripts/`, each forked from `bioemu_batch2_24h.sbatch` with knobs adjusted; ALL locked logic preserved verbatim (env-bioemu, GPU keepalive, length-aware batch_size_100, oversampling formula, NPZ cleanup, RTX 5000 Ada assertion, OSF v3 §7 invariants):
   - `bioemu_batch2_short_6h_std.sbatch` — `--partition=gpu --time=06:00:00 --cpus-per-task=4 --mem=24G --gres=gpu:rtx_5000_ada:1`
   - `bioemu_batch2_med_12h_scav.sbatch` — `--partition=scavenge_gpu --time=12:00:00 --cpus-per-task=4 --mem=40G --gres=gpu:rtx_5000_ada:1`
   - `bioemu_batch2_long_24h_scav.sbatch` — `--partition=scavenge_gpu --time=23:59:00 --cpus-per-task=4 --mem=40G --gres=gpu:rtx_5000_ada:1`

3. **Submitted 3 new array jobs** with cryptic 8-char names:
   - **10730244 q6sht3az** — short (L<200), array `[20-23,44-92]` (53 idx), Standard `gpu`, 6h
   - **10730245 q6med7kp** — medium (L=200-499), array `[11,18-19,24-38]` (18 idx), scavenge_gpu, 12h
   - **10730246 q6lng5wm** — long (L≥500), array `[12-17,39-43]` (11 idx), scavenge_gpu, 24h

4. **Verified queue state** via `squeue -u rag88` — all 3 arrays present, PENDING-Priority.

5. **Cancelled old arrays** `scancel 9449458 9449459` (`exit=0`).

6. **Re-verified queue** — 9449458 and 9449459 gone; 3 new arrays remain PENDING-Priority.

**Expected impact.**
- L<200 cohort (53 proteins, 65% of PENDING) moves to Standard `gpu` partition where the LevelFS bottleneck doesn't apply; 6h walltime + reduced 24G mem improves backfill chance dramatically. Expected dispatch within hours-to-days.
- L=200-499 cohort (18 proteins) keeps scavenge_gpu but with shorter 12h walltime ceiling → improved backfill.
- L≥500 cohort (11 proteins) unchanged 24h on scavenge_gpu (expected runtime ≈ 13-17h per round-4 timing model).
- Net SU change: ~+205 SU (Standard `gpu` charges full RTX 5000 Ada rate for the short cohort vs scavenge's 10× discount). Acceptable per user approval.

**No physics or output-distribution change.** Locked invariants per OSF v3 §7
(denoising_steps, batch_size_100 formula, num_samples oversampling formula,
disorder pre-screen, GPU type, env-bioemu version) all preserved verbatim.

**Files now superseded.** `9449458` and `9449459` are gone; `bioemu_batch2_24h.sbatch`
and `bioemu_batch2.sbatch` retained as historical reference but NOT used for current
PENDING work.
