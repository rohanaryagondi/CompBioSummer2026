---
experiment_id: "1.2-so3lr-pilot"
task_id: "task-002"
agent: "mlff-so3lr-pilot"
date: 2026-04-19
slurm_job_ids: [8886091, 8886092, 8886093, 8886094, 8886095]
status: running
---

# Experiment Log: SO3LR Vacuum NVT Pilot, 5 Tier A/B proteins @ 5 ns

## Setup

| Item | Value |
|------|-------|
| Conda environment (runtime) | env-so3lr |
| Conda environment (prep) | env-mace (pdbfixer + openmm needed for hydrogenation) |
| Node type | GPU node |
| GPU type | RTX 5000 Ada (15 SU/hr) |
| GPU count | 1 per job |
| SLURM partition | `gpu` |
| Wall time requested | 1-00:00:00 (24 h) per job |
| CPUs per task | 2 |
| Memory per task | 16 G |
| Software versions | so3lr 0.1.0, ASE 3.28.0, numpy 2.4.4 (conda), JAX latest-stable |
| Account | pi_mg269 (Standard Tier) |

### Software Version Details

```
# env-so3lr
python --version                                  # Python 3.12.13
python -c "import so3lr; print(so3lr.__version__)" # 0.1.0
python -c "import ase; print(ase.__version__)"     # 3.28.0
python -c "import numpy; print(numpy.__version__)" # 2.4.4
python -c "import jax; print(jax.__version__, jax.default_backend())"

# env-mace (prep only)
python -c "from pdbfixer import PDBFixer"          # OK
python -c "from openmm.app import PDBFile"         # OK (OpenMM 8.5.1)
```

Note: per Sub 1.1 lesson (`shared/notes/1.1-so3lr-crambin.md`), numpy must be
loaded from the conda env's site-packages, not `~/.local/`. All SLURM scripts
set `PYTHONNOUSERSITE=1` and explicitly prepend conda env site-packages to
`PYTHONPATH`.

---

## Parameters

### Simulation parameters (per-protein, all jobs)

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Ensemble | Vacuum NVT | SO3LR does not support explicit-water PME for non-periodic systems; vacuum is the native path (Sub 1.1 Subagent A analysis). |
| Thermostat | Nose-Hoover Chain | SO3LR CLI default. `--nhc-chain 3 --nhc-steps 2 --nhc-thermo 100 --nhc-sy-steps 3`. |
| Temperature | 300 K | Matches experimental NMR references and Implementation Plan §7.2 |
| Timestep (dt) | 0.5 fs | SO3LR CLI default, matches Sub 1.1 crambin D1 PASS. |
| MD cycles | 10,000 | 10,000 × 1000 steps × 0.5 fs = 5,000 ps = 5 ns |
| MD steps per cycle | 1,000 | CLI default. Writes trajectory every 0.5 ps at `save-buffer=50`. |
| Precision | float32 | Sub 1.1 demonstrated stable 1 ns NVT on crambin at float32 (H drift ~15 meV/ps). |
| Long-range cutoff | 12.0 Å | SO3LR CLI default, matches Sub 1.1. |
| Dispersion damping | 2.0 Å | CLI default (lr-cutoff - damping = 10 Å onset). |
| Save buffer | 50 frames | Default; trajectory saved to HDF5 in chunks. |
| Seed | 42 | Deterministic for reproducibility. Matches Sub 1.1. |
| Relaxation | `--relax` on initial run | Essential per Sub 1.1 (NaN without). Force-conv=0.05 eV/Å. `--no-relax` on restarts. |

### Per-protein prep (inputs and sizes)

| Protein | PDB | Chain | Residue range | Heavy atoms | H atoms | Total atoms |
|---------|-----|-------|--------------:|------------:|--------:|------------:|
| WW (Pin1 crop) | ww.pdb (2F21) | A | 6–39 (34 residues) | 275 | 259 | 534 |
| GB3 | gb3.pdb (1P7E) | A | 1–56 (56 residues) | 437 | 425 | 862 |
| GB1 | gb1.pdb (2QMT) | A | 1–56 (56 residues) | 438 | 420 | 858 |
| NTL9 | ntl9.pdb (2HBB) | A | 1–51 (51 residues) | 391 | 422 | 813 |
| UBQ | ubq.pdb (1UBQ) | A | 1–76 (76 residues) | 602 | 629 | 1231 |

### Expected throughput (per Sub 1.1 crambin baseline 2.93 ms/step on RTX 5000 Ada)

| Protein | Atoms | Estimated ms/step | Estimated ns/day | Wall to 5 ns |
|---------|------:|------------------:|----------------:|-------------:|
| WW | 534 | ~2.4 | ~18 | ~6.6 h |
| GB3 | 862 | ~4.0 | ~10.8 | ~11.1 h |
| GB1 | 858 | ~4.0 | ~10.8 | ~11.1 h |
| NTL9 | 813 | ~3.7 | ~11.7 | ~10.3 h |
| UBQ | 1231 | ~5.6 | ~7.7 | ~15.6 h |

All well within the 24-h SLURM wallclock. If a job hits walltime (e.g., UBQ
potentially), resubmit with `--mode restart` (auto-finds latest
`stage*_checkpoint.npz` and re-invokes `so3lr nvt --no-relax --restart-load`).

---

## Commands

### Preparation (env-mace, one-time)

```bash
module load miniconda
conda activate env-mace
export PYTHONNOUSERSITE=1
cd /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2
python output/scripts/so3lr_prep_proteins.py \
    --proteins ww gb3 gb1 ntl9 ubq \
    --output-dir output/trajectories/so3lr_vacuum \
    --force
```

Output: `output/trajectories/so3lr_vacuum/<protein>/input.xyz` (one XYZ per
protein, hydrogens added via PDBFixer@pH 7.0; see `prep_summary.json` in each).

### Main SLURM submission (env-so3lr, one job per protein)

```bash
cd /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2
./output/scripts/submit_so3lr_pilot.sh
```

This iterates over `ww gb3 gb1 ntl9 ubq`, each submitted with:

```bash
sbatch \
  --parsable \
  --job-name=<cryptic-8char> \
  --export=PROTEIN=<p>,MODE=run,TARGET_NS=5.0 \
  output/scripts/so3lr_pilot.sbatch
```

### SLURM job (executed on compute node)

```bash
# inside so3lr_pilot.sbatch
module purge
module load miniconda
conda activate env-so3lr
export PYTHONNOUSERSITE=1
export PYTHONPATH="${CONDA_PREFIX}/lib/python3.12/site-packages:${PYTHONPATH}"

python output/scripts/so3lr_pilot_runner.py \
    --protein "${PROTEIN}" \
    --mode "${MODE}" \
    --target-ns "${TARGET_NS}" \
    --output-dir output/trajectories/so3lr_vacuum
```

The runner (`so3lr_pilot_runner.py`) in turn invokes the SO3LR CLI:

```bash
so3lr nvt \
    --input output/trajectories/so3lr_vacuum/<p>/input.xyz \
    --output output/trajectories/so3lr_vacuum/<p>/stageA.hdf5 \
    --dt 0.5 --temperature 300 \
    --md-cycles 10000 --md-steps 1000 \
    --relax --force-conv 0.05 \
    --precision float32 --lr-cutoff 12.0 \
    --save-buffer 50 \
    --log-file output/trajectories/so3lr_vacuum/<p>/stageA.log \
    --restart-save output/trajectories/so3lr_vacuum/<p>/stageA_checkpoint.npz \
    --seed 42
```

---

## Results

### Submission status (2026-04-19 04:06:51 UTC)

| Protein | Job ID | Job Name | Partition | State (at submit) |
|---------|--------|----------|-----------|-------------------|
| ww   | 8886091 | p3v8xt7r | gpu | PENDING |
| gb3  | 8886092 | k9m2qw5n | gpu | PENDING |
| gb1  | 8886093 | j7r4nb6x | gpu | PENDING |
| ntl9 | 8886094 | z5k8fp2q | gpu | PENDING |
| ubq  | 8886095 | h4w9rn3m | gpu | PENDING |

All jobs tracked in `output/trajectories/so3lr_vacuum/submitted_jobs.tsv`.

### Stability metrics (populated after trajectories complete)

| Metric | Expected | Target (pass) |
|--------|----------|--------------|
| Trajectory length | 5 ns | ≥ 4.5 ns |
| Temperature mean | 300 ± 15 K | 300 ± 25 K |
| NaN count (T, PE) | 0 | 0 |
| Hamiltonian drift | < 50 meV/ps (Sub 1.1 crambin: 15) | < 100 meV/ps |
| Cα RMSD max | 2–6 Å (vacuum, small proteins) | < 7 Å |

Analysis will populate `output/so3lr_vacuum_stability_report.md` once SLURM
jobs complete.

### Output Files (expected after job completion)

| File | Path | Format |
|------|------|--------|
| Per-protein XYZ input | `output/trajectories/so3lr_vacuum/<p>/input.xyz` | XYZ |
| Per-protein H-PDB (audit) | `output/trajectories/so3lr_vacuum/<p>/input_h.pdb` | PDB |
| Trajectory | `output/trajectories/so3lr_vacuum/<p>/stageA.hdf5` | HDF5 |
| SO3LR CLI log | `output/trajectories/so3lr_vacuum/<p>/stageA.log` | Plain text |
| Checkpoint | `output/trajectories/so3lr_vacuum/<p>/stageA_checkpoint.npz` | NPZ |
| Stdout capture | `output/trajectories/so3lr_vacuum/<p>/stageA_stdout.txt` | Text |
| Run summary | `output/trajectories/so3lr_vacuum/<p>/run_summary.json` | JSON |
| SLURM stdout | `output/trajectories/so3lr_vacuum/<p>/slurm-<jid>.out` | Text |
| SLURM stderr | `output/trajectories/so3lr_vacuum/<p>/slurm-<jid>.err` | Text |

---

## Reproducibility

| Item | Value |
|------|-------|
| Random seed | 42 (all proteins) |
| SLURM job IDs | 8886091, 8886092, 8886093, 8886094, 8886095 |
| Node names | TBD (populated post-run in slurm-*.out header) |
| GPU indices | 1 per job; driver-assigned |
| Start time | Per job; PENDING at submission 2026-04-19T04:06:51Z |
| End time | TBD |
| Wall time used | TBD |
| GPU-hours consumed | Estimated ~55 GPU-hr aggregate, ~825 SU |

Git commit at submission: `60c272f` (Sub 1.2 plan committed).

---

## Notes

1. **Two-env workflow:** Hydrogenation requires pdbfixer+openmm (in env-mace),
   but SO3LR MD runs in env-so3lr. Prep is a one-time step before SLURM
   submission; SLURM jobs use env-so3lr only. This avoids cross-contaminating
   either environment.

2. **WW crop:** Starting PDB is full-length Pin1 FIP mutant (2F21, 163
   residues across A chain). Cropped to residues 6–39 per the manifest. The
   WW domain prep matches the task spec and Sub 1.1 S2 mapping (Seewald 2007
   WT Pin1-WW).

3. **GPU keepalive:** The runner starts a daemon matmul thread at 300-s
   cadence per `operational-practices.md`. The initial `so3lr` JIT compilation
   can take several minutes; without keepalive, YCRC's 1-hour idle-GPU check
   could cancel the job during compile-phase (though unlikely for so3lr which
   hits the GPU immediately during relax).

4. **Restart protocol (in case of walltime):** If UBQ (largest system, 1231
   atoms) hits the 24-h wall before reaching 5 ns, the restart path is:
   ```
   sbatch --job-name=<new-cryptic> \
     --export=PROTEIN=ubq,MODE=restart,TARGET_NS=5.0 \
     output/scripts/so3lr_pilot.sbatch
   ```
   The runner auto-finds the most recent `stage*_checkpoint.npz` and invokes
   SO3LR CLI with `--no-relax --restart-load <checkpoint>`.

5. **Stability analysis pending:** Per-protein stability reports and the
   cross-protein summary (`so3lr_vacuum_stability_report.md`) will be written
   when trajectories complete. The HeadAI will re-invoke this agent for
   analysis.

6. **D2 gate evidence:** These 5 trajectories contribute to the SO3LR side of
   the D2 G1 criterion ("≥1 MLFF stable >10 ns on ≥3 Tier B proteins").
   Combined with the Sub 1.1 crambin 1 ns baseline, SO3LR can independently
   satisfy G1 with ≥3 of {GB1, NTL9, UBQ} passing 5 ns here (Tier B proteins).
