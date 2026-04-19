---
task_id: "task-004"
title: "BioEmu batch 2 (~100 ProteinGym proteins) with disorder pre-screen + oversampling"
subphase: "1.2"
track: gamma
wave: 2
agent: "bioemu-batch2"
effort: "7-10 days wall, ~250 GPU-hrs RTX 5000 Ada"
status: planned
created: 2026-04-18
---

# Task 004: BioEmu Batch 2 (~100 ProteinGym Proteins)

## Objective

Generate the second BioEmu v1.1 ensemble batch covering ~100 additional ProteinGym
proteins, applying the lessons from Sub 1.1 batch 1 (46/47 complete, 112,351
physical conformations): pre-screen for predicted disorder >60% (exclude per
YAP1 lesson), apply the oversampling formula `num_samples = ceil(2000 / pass_rate * 1.3)`
using class-based pass rates from Sub 1.1, and use RTX 5000 Ada exclusively for
the SU policy (Sub 1.1 saved ~21,000 SU by shifting BioEmu off H200/B200). Target:
≥90 of selected proteins reach ≥2,000 physical conformations on first generation
pass (no major topup round).

---

## Context

**Why batch 2 now (vs Sub 1.3 or later):** Phase 1 IP §8 W3-4 originally placed
BioEmu batch 2 in Sub 1.2. Sub 1.1 batch 1 finished one round early (the pre-Sub-1.2
remediation pass). Sub 1.2 must produce batch 2 ensembles in time for Sub 1.3
feature extraction (RMSF + RSALOR computation). Without batch 2, Gamma's "150+
ProteinGym proteins" claim has insufficient ensemble support.

**Why ~100 (not all remaining ~104):** Gamma's evaluation set is "150+ ProteinGym
proteins". Batch 1 covered 46. Batch 2 targets the next ~100 to bring total to
~146 — enough for the IP §12.2 "N=57 binding+activity assays" plus the 217-assay
secondary win-rate. Some proteins will be excluded by disorder pre-screen; others
may fail generation. Final count expected 90-100 successful in batch 2.

**Why RTX 5000 Ada exclusively:** Sub 1.1 documented that BioEmu fits in <8 GB VRAM
(no need for H200's 140 GB), and the SU rate differential (15 vs 300 SU/hr) means
RTX 5000 Ada saves ~95% on SU consumption. Sub 1.1 batch 1 topup on RTX 5000 Ada
cost ~1,125 SU vs the same work on H200 would have been ~22,500 SU.

**Why disorder pre-screen:** Sub 1.1 dropped YAP1 (504 aa, IDP) at 0.7% pass rate
after generating 10,368 NPZ files for nothing. The cross-agent note recommends
excluding proteins with >60% predicted disorder. This task implements that screen
upstream, before any generation.

---

## Detailed Instructions

### Step 1: Compile candidate list (Day 1)

1. Read ProteinGym 2024 manifest (mirror at `/nfs/roberts/scratch/pi_mg269/rag88/proteingym/manifest.csv`
   or download from `https://github.com/OATML-Markslab/ProteinGym/`).
2. Subtract the 46 proteins already in batch 1 (list at
   `phases/phase-1/subphase-1.1/output/task-003-sequences.fasta` headers + `dashboards/master-status.md` Per-Track Status table).
3. Apply ProteinGym DMS substitution mode filter (binding + activity primary; expression secondary).
4. Sort by assay quality / utility per IP §12.2.
5. Take top 150 candidates → save list to
   `phases/phase-1/subphase-1.2/output/scripts/batch2_candidates.csv` with columns:
   `protein_id, sequence, length, source_pdb_id (if available), expected_protein_class`.

### Step 2: Disorder pre-screen (Day 1-2)

Build script `phases/phase-1/subphase-1.2/output/scripts/disorder_screen.py`:

1. For each candidate sequence:
   - Use IUPred3 (lightweight, no GPU; CLI: `iupred3 --short --type long <fasta>`)
     OR use ESMfold pLDDT proxy (fraction of residues with pLDDT < 50 = disorder estimate)
   - Compute disorder fraction = (residues with disorder score > 0.5) / total residues
2. Mark exclude if disorder_fraction > 0.60.
3. Exclude any sequence > 500 aa (memory blowup risk per Sub 1.1 SPG1 lesson; user has only ~32 GB on RTX 5000 Ada).
4. Write `phases/phase-1/subphase-1.2/output/scripts/batch2_screened.csv` with columns:
   `protein_id, sequence, length, disorder_fraction, exclude_reason (if applicable)`.
5. Target: ≥100 candidates pass screening. If <100, expand to top 200 candidates and re-screen.

### Step 3: Build oversampling manifest (Day 2-3)

Build script `phases/phase-1/subphase-1.2/output/scripts/batch2_manifest_builder.py`:

1. For each surviving protein, classify by `expected_protein_class` (small globular, IDP, transmembrane, multi-domain, metastable):
   - Use sequence features (length, hydrophobicity, transmembrane prediction via TMHMM if available, structural motifs from PDB if available)
   - Default to "small globular" if uncertain (most ProteinGym proteins)
2. Look up class-based pass rate from `shared/notes/1.1-bioemu-passrates.md` lines 73-81:
   - Structured globular: 92% (use 0.92)
   - IDP / transmembrane: 47% (use 0.47)
   - Multi-domain / metastable: 23% (use 0.23)
   - Largely disordered (>60% disorder): excluded already
3. Compute `num_samples = ceil(2000 / pass_rate * 1.3)`:
   - Globular: ~2,829 samples
   - IDP-like: ~5,532 samples
   - Multi-domain: ~11,304 samples
4. Write `phases/phase-1/subphase-1.2/output/scripts/batch2_manifest.csv` with columns:
   `protein_id, sequence, length, expected_class, expected_pass_rate, num_samples, batch_index (1-10 for ~10 proteins/batch)`

### Step 4: Fork submit script (Day 3)

Source: `phases/phase-1/subphase-1.1/output/scripts/submit_bioemu_batches.sh`. Fork to:
`phases/phase-1/subphase-1.2/output/scripts/submit_bioemu_batch2.sh`.

**Changes:**
1. Parameterize FASTA path: read from `batch2_manifest.csv` (convert to FASTA on the fly)
2. Parameterize output dir: `/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/<protein_id>/`
3. Parameterize per-protein `num_samples` (Sub 1.1 used a global default; batch 2 is per-protein)
4. **Force RTX 5000 Ada partition (`gpu`)** — never `gpu_h200` or `gpu_b200`
5. **Memory bump for high-num_samples proteins:** if `num_samples > 10000`, request `--mem=40G` (Sub 1.1 SPG1 lesson)
6. Keep all Sub 1.1 safeguards:
   - `export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` (line 66 in original)
   - `--cache-first` step on login node BEFORE submitting batches (caches MSA embeddings)
   - QOS limit: max 2 pending jobs (use `--batch N` to submit incrementally)
   - Cryptic 8-char job names

### Step 5: Submit batches (Day 4-10)

1. Run cache step on login node: `bash submit_bioemu_batch2.sh --cache-first`
2. Submit batches incrementally: `--batch 1` through `--batch ~10` (10 proteins per batch, ~50 GPU-hrs each)
3. Monitor via `--status` daily; resubmit failed via `--retry-failed`
4. Apply topup ONLY for proteins that fall below 2,000 physical (Sub 1.1 pattern)

### Step 6: Validate output (Day 10)

For each protein directory at `/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/<protein>/`:

```bash
ls topology.pdb samples.xtc batch_*.npz | wc -l   # samples.xtc must exist
python -c "import mdtraj; t=mdtraj.load('samples.xtc', top='topology.pdb'); print(t.n_frames)"   # ≥2000
cat generation_status.json   # status: success
```

Aggregate per-protein status into:
`phases/phase-1/subphase-1.2/output/batch2_summary.md`:

| Protein | Length | Class | Expected pass | Actual pass | Conformations | Status |
|---------|-------:|-------|--------------:|-----------:|--------------:|:------:|
| ... | ... | ... | ... | ... | ... | success/partial/failed |

### Step 7: Cross-agent note

Write `shared/notes/1.2-bioemu-batch2-passrates.md` comparing:
- Predicted pass rate (from Sub 1.1 class table)
- Actual pass rate (this batch)
- Diff per class — is the predictive model accurate?

Recommend batch 3 (if any) sizing adjustments.

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| `../../tasks/task-004-bioemu-batch2.md` | This task spec |
| `../../../subphase-1.1/output/scripts/submit_bioemu_batches.sh` | Source script to fork |
| `../../../subphase-1.1/output/scripts/bioemu_generate_single.py` | Single-protein wrapper to reuse |
| `../../../../../shared/notes/1.1-bioemu-passrates.md` | Class-based pass rates + oversampling formula |
| `../../../../../shared/notes/operational-practices.md` | RTX 5000 Ada policy, cryptic names |
| `../../../../../../phases/phase-0/subphase-0.1/proteins/manifest.json` | Manifest entries (for sanity-check on existing proteins) |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../../Proposal/Gamma.md` | §2 BioEmu pipeline, §5 features |
| `../../../subphase-1.1/output/task-003-sequences.fasta` | Batch 1 protein list (subtract from candidates) |
| `../../../../../shared/notes/1.1-protein-count-canonical.md` | Active benchmark proteins (DO NOT regenerate; batch 2 is for ProteinGym beyond benchmark) |

### DO NOT READ

- Other SubAgents' task specs
- `../../../../../../Proposal/HumanOnlyProposal.md`
- Future subphase plans

---

## Output Artifacts

### Code and data artifacts

| Artifact | Path | Format |
|----------|------|--------|
| Disorder screen script | `../../output/scripts/disorder_screen.py` | Python |
| Manifest builder script | `../../output/scripts/batch2_manifest_builder.py` | Python |
| Forked submit script | `../../output/scripts/submit_bioemu_batch2.sh` | Bash |
| Candidate list | `../../output/scripts/batch2_candidates.csv` | CSV |
| Screened list | `../../output/scripts/batch2_screened.csv` | CSV |
| Final manifest | `../../output/scripts/batch2_manifest.csv` | CSV |
| BioEmu ensembles | `/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/<protein>/` | XTC + PDB + NPZ |
| Batch 2 summary | `../../output/batch2_summary.md` | Markdown |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-004-status.md` | `templates/status-report.md` |
| Experiment log | `../../output/task-004-experiment.md` | `templates/experiment-log.md` |
| Cross-agent note | `../../../../../shared/notes/1.2-bioemu-batch2-passrates.md` | `templates/cross-agent-note.md` |

---

## Success Criteria (Zero Compromise)

1. [ ] `disorder_screen.py` exists and produces `batch2_screened.csv` with ≥100 candidates passing screen
2. [ ] `batch2_manifest_builder.py` exists and produces `batch2_manifest.csv` with per-protein num_samples values
3. [ ] `submit_bioemu_batch2.sh` exists and is parameterized (no hardcoded paths)
4. [ ] All BioEmu jobs ran on RTX 5000 Ada (`gpu` partition); zero jobs on H200/B200
5. [ ] ≥90 of selected proteins reach ≥2,000 physical conformations
6. [ ] `batch2_summary.md` written with per-protein status
7. [ ] Cross-agent note `1.2-bioemu-batch2-passrates.md` written
8. [ ] All SLURM job names are 8-char cryptic alphanumeric
9. [ ] Status report written to `../../status/task-004-status.md`

---

## Verification

1. `ls /nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/ | wc -l` returns ≥90
2. For each protein dir, `samples.xtc` + `topology.pdb` + `generation_status.json` exist
3. `python -c "import json; print(json.load(open('.../<protein>/generation_status.json'))['conformation_count'])"` returns ≥2000 for ≥90 proteins
4. `sacct -j <bioemu-jobs> -o Partition` shows only `gpu` (no `gpu_h200`, `gpu_b200`)
5. Status report exists with status `complete`

---

## Failure Protocol

1. **Disorder screening tool unavailable:** Try ESMfold pLDDT as fallback; if neither works, use NetSurfP-2 or just sequence-based heuristic (>60% low-complexity = exclude). Document the choice.
2. **<70 proteins reach 2,000 conformations after topup:** Status: `partial`. Help-needed doc with diagnostics. PlannerAI plans batch 3 strategy in Sub 1.3.
3. **MSA cache server unreachable from login node:** Use Sub 1.1 fallback (run first protein on login node, then SLURM for rest).
4. **All proteins fail (BioEmu environment broken):** Status: `failed`. Help-needed. Reinstall env-bioemu from Phase 0 yml.

Document everything in status report.
