---
experiment_id: "1.2-bioemu-batch2"
task_id: "task-004"
agent: "bioemu-batch2"
date: 2026-04-19
slurm_job_ids: [8887441, 8887446]
status: running
---

# Experiment Log: BioEmu Batch 2 Generation (Sub 1.2 task-004)

## Setup

| Item | Value |
|------|-------|
| Conda environment | env-bioemu |
| Node type | GPU compute node |
| GPU type | NVIDIA RTX 5000 Ada (32 GB VRAM) |
| GPU count | 1 per job |
| SLURM partition | gpu |
| Wall time requested | 04:00:00 per per-protein job |
| Memory requested | 40G |
| CPUs | 2 (per user memory: BioEmu needs only 2 CPUs, 10G RAM minimum) |

### Software Version Details

```
python 3.10.x (env-bioemu)
bioemu 1.3.1
torch 2.7.1+cu128
numpy 2.2.6
tensorflow-cpu (via bioemu dependency; numpy conflict on login node;
  works on compute nodes because of different CUDA stack presence)
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python (required per Sub 1.1 line 66)
```

---

## Parameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Protein count | 93 | ProteinGym candidates 30-600 aa, minus batch 1, minus disorder-excluded |
| Disorder-exclusion threshold | disorder_fraction > 0.60 | Per Sub 1.1 YAP1 drop (0.7% pass rate with 70%+ disorder) |
| Oversampling formula | `num_samples = ceil(2000/pass_rate*1.3)` | Sub 1.1 cross-agent note (1.1-bioemu-passrates.md) |
| Class pass rates | 0.92 / 0.70 / 0.60 / 0.47 / 0.23 | Class lookup (structured/TM/large/IDP/multi-domain) |
| base_seed | 42 | Reproducibility with Sub 1.1 |
| batch_size_100 | 10 | Sub 1.1 default (physicality-filtered batches of 1,000 in bioemu) |
| model_name | bioemu-v1.1 | Official release version |
| MSA server | colabfold default | Sub 1.1 uses it reliably from compute nodes |
| Partition | gpu (RTX 5000 Ada) | SU policy; NEVER gpu_h200 or gpu_b200 |

### Per-class num_samples

| Class | Count | num_samples | Total denoised samples |
|-------|------:|------------:|-----------------------:|
| structured_globular | 53 | 2,827 | 149,831 |
| idp_like | 21 | 5,532 | 116,172 |
| large_globular_long | 19 | 4,334 | 82,346 |
| transmembrane | 0 | 3,715 | 0 |
| multi_domain_metastable | 0 | 11,305 | 0 |
| Grand total | 93 | — | 348,349 |

---

## Commands

```bash
# --- Step 1: Compile candidate list from ProteinGym CSV ---
cd /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2
python3 output/scripts/compile_candidates.py
# Output: output/scripts/batch2_candidates.csv (103 candidates, 30-600 aa)

# --- Step 2: Disorder pre-screen (sequence-based) ---
python3 output/scripts/disorder_screen.py
# Output: output/scripts/batch2_screened.csv
# Result: 93 pass, 10 excluded (7 disorder_fraction>0.60, 3 foldindex<-0.20)

# --- Step 3: Build per-protein manifest with oversampling ---
python3 output/scripts/batch2_manifest_builder.py
# Output: output/scripts/batch2_manifest.csv and .fasta
# Class counts: 53 structured_globular, 21 idp_like, 19 large_globular_long

# --- Step 4: Submit precache job (all 93 proteins in one GPU pass) ---
sbatch --job-name=ba48ebhw --export=ALL,INDICES=all \
  --time=04:00:00 output/scripts/precache_msa.sbatch
# Job 8887441 submitted (MSA precaching on RTX 5000 Ada)

# --- Step 5: Submit generation batch 1 (proteins 0-9) ---
sbatch --job-name=qk5s2dzo --array=0-9 output/scripts/bioemu_batch2.sbatch
# Job 8887446_[0-9] submitted (generation on RTX 5000 Ada)

# --- Step 6: Subsequent batches (HeadAI-driven as QOS permits) ---
bash output/scripts/submit_bioemu_batch2.sh --batch 2   # proteins 10-19
bash output/scripts/submit_bioemu_batch2.sh --batch 3   # proteins 20-29
# ... through --batch 10 (proteins 90-92)

# --- Status check ---
bash output/scripts/submit_bioemu_batch2.sh --status

# --- Retry failed (if any) ---
bash output/scripts/submit_bioemu_batch2.sh --retry-failed
```

---

## Results

**In progress.** Filled in over the 7-10 day run.

| Metric | Value | Expected | Status |
|--------|-------|----------|--------|
| Proteins submitted | 10 | 93 total | batch 1 of 10 submitted |
| Proteins successful | TBD | ≥90 | pending |
| Conformations generated | TBD | ≥186,000 total (2000 × 93) | pending |
| MSA cache hits (batch 1) | TBD | ≥9/10 after precache | pending |
| SU spent | TBD | ~3,750 (15 SU/hr × 250 hrs) | pending |

### Output Files (growing)

| File | Path | Status |
|------|------|--------|
| Manifest CSV | `.../output/scripts/batch2_manifest.csv` | created |
| Manifest FASTA | `.../output/scripts/batch2_manifest.fasta` | created |
| Candidates CSV | `.../output/scripts/batch2_candidates.csv` | created |
| Screened CSV | `.../output/scripts/batch2_screened.csv` | created |
| ProteinGym reference | `.../output/scripts/proteingym_dms_substitutions.csv` | cached |
| Per-protein ensemble dirs | `/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/<UniProt_ID>/` | being created |
| SLURM logs | `/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/logs/` | being created |

---

## Reproducibility

| Item | Value |
|------|-------|
| Random seed | 42 (base_seed, propagated per-protein) |
| SLURM job IDs | 8887441 (precache), 8887446 (batch 1 array) |
| Start time | 2026-04-19T00:30Z (first submission) |
| End time | TBD (expected 2026-04-29 after all 10 batches + topup) |

---

## Notes

### Tensorflow numpy conflict on login node

The login node (login2.bouchet.ycrc.yale.edu) cannot import tensorflow in
env-bioemu due to numpy 2.x vs ml_dtypes 0.x ABI mismatch. This prevents
running `precache_msa.py` directly on the login node. Workaround: submit
`precache_msa.sbatch` to the gpu partition instead (compute nodes have
different CUDA stack and tensorflow imports succeed there). Cost: ~1-4
GPU-hrs (~60 SU) — within budget.

### MSA server

ColabFold MSA server was reachable from the login node at submission time.
Compute nodes at YCRC also have outbound HTTPS per Sub 1.1 observation
(batch 1 all 47 proteins used MSA server successfully). No MSA cache
server issues expected.

### QOS pending limit

QOS limit is 2 pending per user per gpu partition. Batches 2-10 must be
submitted by HeadAI as earlier batches move to RUNNING. The
`submit_bioemu_batch2.sh --batch N` wrapper performs this check
automatically.

### Cryptic job names

All SLURM jobs use 8-char alphanumeric cryptic names (per user memory +
operational-practices.md):
- Precache: `ba48ebhw`
- Batch 1 (0-9): `qk5s2dzo`
- Subsequent batches: new random name each

### Fallback plan if batch pass rates deviate

If observed batch-2 pass rate for any class deviates from predicted by >15%,
the class table should be recalibrated and stashed in a v2 cross-agent
note for future batches. Batch 2 is the first test of the oversampling
formula at production scale.
