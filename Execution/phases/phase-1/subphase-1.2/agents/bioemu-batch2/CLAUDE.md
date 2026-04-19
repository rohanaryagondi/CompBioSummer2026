# SubAgent: BioEmu Batch 2 (~100 ProteinGym Proteins)

You are a **SubAgent** executing task-004 in subphase 1.2 of the CompBioSummer2026
execution pipeline. You have a narrowly scoped task with explicit success criteria.
Execute your task, write your documentation, and report your results.

---

## Your Task

**Task ID:** task-004
**Title:** BioEmu batch 2 (~100 ProteinGym proteins) with disorder pre-screen + oversampling
**Track:** Gamma
**Subphase:** 1.2
**Estimated effort:** 7-10 days wall, ~250 GPU-hrs RTX 5000 Ada, ~3,750 SU

---

## What You Must Accomplish (Zero Compromise)

1. Compile candidate list of ProteinGym proteins beyond batch 1 (the 46 already
   generated). Save to `../../output/scripts/batch2_candidates.csv`.
2. Build `disorder_screen.py` to filter candidates with >60% predicted disorder
   (per Sub 1.1 YAP1 lesson). Use IUPred3 or ESMfold pLDDT proxy.
3. Build `batch2_manifest_builder.py` applying class-based pass rates from
   `1.1-bioemu-passrates.md` and oversampling formula `num_samples = ceil(2000 / pass_rate * 1.3)`.
4. Fork `submit_bioemu_batches.sh` to `submit_bioemu_batch2.sh` with parameterized
   manifest + output dir.
5. Cache MSA embeddings on login node (`--cache-first`) BEFORE submitting batches.
6. Submit batches incrementally (`--batch 1` ... `--batch ~10`); monitor via `--status`; topup failed.
7. **All BioEmu jobs MUST run on RTX 5000 Ada (`gpu` partition); zero on H200/B200.**
8. Target: ≥90 of selected proteins reach ≥2,000 physical conformations.
9. Write `batch2_summary.md` and cross-agent note `1.2-bioemu-batch2-passrates.md`.
10. Status report at `../../status/task-004-status.md`.

---

## What You Read

### MUST READ (before starting)

| File | Why |
|------|-----|
| `../../tasks/task-004-bioemu-batch2.md` | Your full task specification |
| `../../../subphase-1.1/output/scripts/submit_bioemu_batches.sh` | Source script to fork |
| `../../../subphase-1.1/output/scripts/bioemu_generate_single.py` | Reusable single-protein wrapper |
| `../../../../../shared/notes/1.1-bioemu-passrates.md` | Class-based pass rates + oversampling formula (lines 73-81) |
| `../../../../../shared/notes/operational-practices.md` | RTX 5000 Ada policy, cryptic SLURM names |
| `../../../../phase-0/subphase-0.1/proteins/manifest.json` | Existing benchmark proteins (do NOT regenerate) |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../../Proposal/Gamma.md` | §2 BioEmu pipeline, §5 features |
| `../../../subphase-1.1/output/task-003-sequences.fasta` | Batch 1 protein list (subtract from candidates) |
| `../../../../../shared/notes/1.1-protein-count-canonical.md` | Active benchmark proteins |

### DO NOT READ

- Other SubAgents' task specs
- `../../../../../../Proposal/HumanOnlyProposal.md`
- Future subphase plans

---

## Detailed Instructions

See `../../tasks/task-004-bioemu-batch2.md` Steps 1-7 for full procedure.

**Critical reminders:**

1. **RTX 5000 Ada exclusively.** Sub 1.1 saved ~21,000 SU by shifting BioEmu off H200/B200. NEVER `--partition=gpu_h200` or `--partition=gpu_b200`. Force `--partition=gpu`.
2. **Disorder pre-screen UPSTREAM, not post-hoc.** Sub 1.1 wasted 10,368 NPZ on YAP1 because no upstream screen. Apply >60% threshold BEFORE submitting any BioEmu job.
3. **Oversampling formula by protein class:** `num_samples = ceil(2000 / pass_rate * 1.3)`. Globular ~2,829; IDP-like ~5,532; multi-domain ~11,304.
4. **Memory bump for high-num_samples proteins:** if `num_samples > 10000`, request `--mem=40G` (Sub 1.1 SPG1 lesson — XTC assembly OOM at 22 GB for 10K+ NPZ).
5. **`--cache-first` step on login node MANDATORY before SLURM submissions.** Without it, every job re-computes MSA embeddings, wasting GPU hours.
6. **`export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python`** required (Sub 1.1 line 66 of submit script).
7. **Cryptic 8-char SLURM job names.**
8. **DO NOT regenerate batch 1 proteins.** Subtract from candidates; only NEW proteins in batch 2.
9. **DO NOT regenerate the 16 active benchmark proteins (Alpha-M).** Those are independently generated; not Gamma's scope.

---

## What You Write

### Code and data artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Disorder screen | `../../output/scripts/disorder_screen.py` | IUPred3 or ESMfold pLDDT wrapper |
| Manifest builder | `../../output/scripts/batch2_manifest_builder.py` | Per-protein num_samples computation |
| Forked submit script | `../../output/scripts/submit_bioemu_batch2.sh` | Parameterized batch submitter |
| Candidates CSV | `../../output/scripts/batch2_candidates.csv` | All candidates before screen |
| Screened CSV | `../../output/scripts/batch2_screened.csv` | After disorder + length filters |
| Final manifest | `../../output/scripts/batch2_manifest.csv` | Per-protein num_samples + class |
| BioEmu ensembles | `/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/<protein>/` | XTC + topology + NPZ |
| Batch 2 summary | `../../output/batch2_summary.md` | Per-protein status table |

### Mandatory documentation

**Status report:** `../../status/task-004-status.md` (template `status-report.md`).
Include final protein count (≥2K conformations), exclusion list, GPU-hrs consumed, any topup rounds.

**Experiment log:** `../../output/task-004-experiment.md` (template `experiment-log.md`).
Include all SLURM job IDs, batch submission timeline, per-protein generation time.

**Cross-agent note:** `../../../../../shared/notes/1.2-bioemu-batch2-passrates.md`
(template `cross-agent-note.md`). Tag tracks: `gamma`. Urgency: `important`. Include:
- Predicted vs actual pass rates per class
- Diff per class (is the Sub 1.1 model accurate?)
- Recommendations for batch 3 sizing (if any)

---

## Verification

1. [ ] `ls /nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/ | wc -l` returns ≥90
2. [ ] For each protein dir: `samples.xtc` + `topology.pdb` + `generation_status.json` exist
3. [ ] `cat .../<protein>/generation_status.json` shows `conformation_count >= 2000` for ≥90 proteins
4. [ ] `sacct -j <bioemu-jobs> -o Partition` shows only `gpu` (no `gpu_h200`, `gpu_b200`)
5. [ ] `batch2_summary.md` populated
6. [ ] Cross-agent note exists
7. [ ] Status report written

---

## If Something Goes Wrong

1. **Disorder screening tool unavailable:** Try ESMfold pLDDT fallback; if neither, use sequence-based heuristic; document.
2. **<70 proteins reach 2,000 conformations after topup:** Status: `partial`. Help-needed doc with diagnostics.
3. **MSA cache server unreachable from login node:** Use Sub 1.1 fallback (run first protein on login node, then SLURM for rest).
4. **All proteins fail (env-bioemu broken):** Status: `failed`. Help-needed. Reinstall env-bioemu from Phase 0 yml.

Document everything in status report.
