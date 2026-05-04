---
experiment_id: "1.2-mace-npt-pilot"
task_id: "task-001"
agent: "mlff-mace-pilot"
date: 2026-04-19
slurm_job_ids: [8885960, 8885961, 8885962]
status: running
---

# Experiment Log: MACE-OFF24 Hybrid NPT 5 ns x 3 Tier B (WW / GB3 / Ubiquitin)

## Setup

| Item | Value |
|------|-------|
| Conda environment | env-mace (/home/rag88/.conda/envs/env-mace) |
| Node type | H200 GPU node (any of a1122-a1126 u00-u30) |
| GPU type | NVIDIA H200 (sm_90, 140 GB VRAM) |
| GPU count | 1 per job (3 jobs total) |
| SLURM partition | gpu_h200 |
| Wall time requested | 23:59:00 per job; Python walltime guard at 22.5 hr |
| Software versions | mace-torch 0.3.15, OpenMM 8.5.1, PyTorch 2.5.1+cu121, PDBFixer 1.12.0, openmmml |
| Platform selection | OpenCL (CUDA disabled by Sub 1.1 policy: sm_89/90/100 all incompatible) |

### Software Version Details

```
Confirmed from Sub 1.1 (carried forward; env-mace unchanged):
  mace-torch 0.3.15
  MLPotential name: mace-off24-medium
  OpenMM 8.5.1 (Python, OpenCL backend)
  openmm-ml (openmmml)
  PyTorch 2.5.1+cu121
  PDBFixer 1.12.0 (installed via pip install --no-deps per env-mace patch note)

Env-mace verification command:
  /home/rag88/.conda/envs/env-mace/bin/python -c "import openmm, torch, openmmml, pdbfixer"
```

---

## Parameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Temperature | 300 K | Sub 1.1 baseline; BMRB S2 references ~278-308 K |
| Langevin friction | 1.0 / ps | Sub 1.1 baseline |
| Production timestep | 1.0 fs | Sub 1.1 baseline (MACE needs small dt; hybrid adds no coupling issue) |
| NVT equil timestep | 0.5 fs | Reduced from 1 fs to be safe during hybrid NVT warmup |
| Pressure (NPT) | 1.0 atm | Standard reference |
| Barostat | MonteCarloBarostat freq=25 | Standard freq for liquid-water NPT |
| NVT equilibration | 50 ps @ dt=0.5 fs | Barostat disabled during this phase (freq=0) |
| NPT equilibration | 200 ps @ dt=1 fs | Barostat enabled for full NPT relaxation |
| Production target | 5.0 ns @ dt=1 fs | Task spec §5 pass criterion (>=4.5 ns total) |
| Solvent model | TIP3P-FB | Sub 1.1 baseline; AMBER14 compatible |
| Solvent padding | 1.0 nm | Sub 1.1 baseline |
| Ionic strength | 0.15 M NaCl | Physiological |
| Nonbonded cutoff | 1.0 nm PME | Sub 1.1 baseline |
| Energy min iterations | 2000 | Sub 1.1 REVERT (200 caused NaN; 2000 known-good) |
| Post-min max-force guard | 1e5 kJ/mol/nm fail threshold | Sub 1.1 regression guard |
| Report / DCD interval | 1 ps (1000 steps) | 5000 frames per 5 ns trajectory |
| Checkpoint interval | 100,000 steps (~100 ps wall) | Covers ~55 min wall at 2 ns/day |
| Walltime guard | 81,000 s (22.5 hr) | Save + exit cleanly before SLURM 23:59 kill |

### Per-protein setup

| Protein | Short | PDB | Chain | Residues | Notes |
|---------|-------|-----|-------|----------|-------|
| WW domain (Pin1) | ww | 2F21 | A | 6-39 (cropped) | Sub 1.1 validated at 534 MACE / 7565 total |
| GB3 | gb3 | 1P7E | A | 1-56 (full) | ~862 MACE / ~9874 total (Sub 1.1 projection) |
| Ubiquitin | ubq | 1UBQ | A | 1-76 (full) | ~1231 MACE / ~17162 total (Sub 1.1 measured) |

---

## Commands

### Environment activation (in SLURM job)

```bash
source /home/rag88/miniconda3/etc/profile.d/conda.sh
conda activate env-mace
export PYTHONNOUSERSITE=1
```

### Per-protein submission (wrapper call)

```bash
cd /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2
./output/scripts/submit_mace_npt.sh ww  m4k2pz9q
./output/scripts/submit_mace_npt.sh gb3 n7r9tx4w
./output/scripts/submit_mace_npt.sh ubq q3j8vb6p
```

### Resubmission (when job hits walltime guard and exits with code 2)

```bash
# Same wrapper, same cryptic tag -- script detects checkpoint and resumes.
cd /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2
./output/scripts/submit_mace_npt.sh ww  m4k2pz9q   # resumes from checkpoint
./output/scripts/submit_mace_npt.sh gb3 n7r9tx4w
./output/scripts/submit_mace_npt.sh ubq q3j8vb6p
```

Do NOT use SLURM --dependency chains (fragile under H200 preemption). Instead
monitor the previous job's exit code and resubmit manually (or via a wrapper
loop -- see §Resume/Restart Protocol below).

### Initial submission log (2026-04-19T04:04 UTC)

```
$ ./output/scripts/submit_mace_npt.sh ww  m4k2pz9q
Submitted batch job 8885960
$ ./output/scripts/submit_mace_npt.sh gb3 n7r9tx4w
Submitted batch job 8885961
$ ./output/scripts/submit_mace_npt.sh ubq q3j8vb6p
Submitted batch job 8885962
```

---

## Results

### Current status (snapshot at log write time)

| Metric | Value |
|--------|-------|
| Jobs submitted | 3 (WW, GB3, UBQ) |
| Jobs state | All PENDING on gpu_h200 (2026-04-19T04:04 UTC) |
| Trajectories completed | 0 (production pending) |
| Wall time consumed | ~0 (queue wait only) |
| H200 SU consumed | ~0 (queue wait is free) |

### Expected outcome (extrapolated from Sub 1.1 §11 H200 benchmark)

| Protein | MACE atoms | Total atoms | Expected ns/day (H200 OpenCL) | 5 ns wall (single-stream) | SLURM resubmits expected |
|---------|-----------|-------------|-------------------------------|---------------------------|--------------------------|
| WW | ~534 | ~7,565 | 2.11 (measured) | ~2.4 days | 3 (24h each) |
| GB3 | ~862 | ~9,874 | ~1.2 (projected) | ~4.2 days | 5 |
| Ubiquitin | ~1,231 | ~17,162 | ~0.85 (projected) | ~5.9 days | 6 |

**Total wall estimate:** ~12.5 days if sequential, ~6 days in parallel across 3 SLURM jobs.
**Total GPU-hours estimate:** ~420 H200-GPU-hrs = ~126,000 SU.
**Single-job SU cost:** 23.98 hr * 300 SU/hr = 7,194 SU. Under 40,000 SU single-job cap.

### Output Files (expected paths)

| File | Path | Notes |
|------|------|-------|
| WW topology | output/trajectories/mace_npt/ww_topology.pdb | Written at end of equilibration |
| WW trajectory | output/trajectories/mace_npt/ww_npt.dcd | Append across resubmits |
| WW state log | output/trajectories/mace_npt/ww_npt_state.csv | Append across resubmits |
| WW meta | output/trajectories/mace_npt/ww_npt_meta.json | Session info + verdict |
| GB3 ditto | output/trajectories/mace_npt/gb3_* | |
| UBQ ditto | output/trajectories/mace_npt/ubq_* | |
| WW checkpoint | /nfs/roberts/scratch/pi_mg269/rag88/alpha-m/mace-npt/m4k2pz9q/checkpoint_latest.chk | Scratch; overwritten ~every 100 ps |
| WW progress | /nfs/roberts/scratch/pi_mg269/rag88/alpha-m/mace-npt/m4k2pz9q/progress.json | ns_completed tracker |

---

## Reproducibility

| Item | Value |
|------|-------|
| Random seed(s) | OpenMM defaults (not seeded; MonteCarloBarostat uses OpenMM internal RNG) |
| SLURM job ID(s) | 8885960 (WW), 8885961 (GB3), 8885962 (UBQ) |
| Node name(s) | TBD (PENDING at write time; jobstats will record post-start) |
| GPU index(es) | H200 idx 0 (allocated per --gres=gpu:h200:1) |
| Start time (submit) | 2026-04-19T04:04 UTC |
| End time | TBD (8-12 days wall total expected) |
| Wall time used | TBD |
| GPU-hours consumed | TBD |

---

## Notes

### Design decisions

1. **Two-stage equilibration (50 ps NVT + 200 ps NPT) before production.** The Sub 1.1
   retry note (§9-10) showed that NVT with `maxIterations=200` failed with NaN due
   to residual high-force atoms. Here we use `maxIterations=2000` plus a 50 ps NVT
   at the smaller dt=0.5 fs to safely dissipate any residual energy before turning
   on the barostat, then 200 ps NPT to relax volume before production. Total 250 ps
   of equilibration. Total production target is 5 ns on top of that.

2. **Barostat disabled during NVT stage via `setFrequency(0)`.** The MonteCarloBarostat
   is added to the system once (before integrator construction), then its frequency
   is toggled between 0 (disabled) and `BAROSTAT_FREQ=25` (enabled) across the
   NVT-then-NPT equilibration stages. This avoids rebuilding the system between
   stages.

3. **Production `simulation.currentStep` reset to 0 at equilibration end.** Ensures
   a clean "production ns" counter regardless of equil stage counts. The checkpoint
   still captures the full `getStepCount()` value for production; on resume the
   script reads that counter and treats it as the production ns index.

4. **DCD append mode + StateDataReporter handle-based append.** OpenMM's
   `DCDReporter(path, interval, append=True)` is documented and works. The
   `StateDataReporter` does NOT accept `append` as a kwarg (it only accepts a
   file path or file handle); to avoid a duplicate header on resumes, we open
   the CSV in Python append-mode and pass the file handle, then set
   `sdr._hasInitialized = True` to suppress the header write.

5. **Walltime guard at 22.5 hr (81,000 s).** SLURM `--time=23:59:00` hard-kills
   without saving. The Python guard exits at 22.5 hr so the script always has
   time to save the final checkpoint and update `progress.json` before SLURM
   terminates the process. Without the guard, one ~hour of production would
   be lost per resubmit.

6. **OpenCL platform only.** Sub 1.1 Subagent A definitively verified CUDA
   broken on all available GPUs (sm_89/90/100). OpenCL is the only backend.

### Risks and monitoring

1. **MACE NPT barostat instability at startup (~25% probability per HeadAI risk
   register).** If any of the 3 jobs fails with NaN during NPT equilibration or
   early production, fall back to NVT for that protein by setting
   `MACE_HYBRID_BAROSTAT=nvt` and resubmitting with a new tag (skips the NPT
   equil stage but still runs 50 ps NVT equil).

2. **H200 OpenCL hang post-step-N (~30% probability per Sub 1.1 SLURM 8789805
   observation).** If a job stops making progress (jobstats util drops to ~4%,
   log stops updating), cancel the job and resubmit with the same tag (checkpoint
   resume). If 3+ resumes fail at the same step, fall back to RTX 5000 Ada
   (slower but stable -- ~0.184 ns/day for WW), accepting scope reduction to
   1-2 proteins.

3. **Trajectory corruption on resume.** Append-mode DCD with a mid-trajectory
   crash could leave a partial frame. DCDReporter writes one frame at a time
   and calls fsync after each write, so partial frames should be rare; but if
   mdtraj fails to load the concatenated trajectory, the repair protocol is
   to truncate the DCD at the last fully-written frame (use `mdtraj.open(path)`
   and read `n_frames` -- rewrite up to that count).

### Cross-job coordination

The three jobs are independent -- each protein runs its own PDB, its own
checkpoint, its own DCD. No shared state between jobs. GPU allocation is
single-GPU (`--gres=gpu:h200:1`), so three concurrent jobs need three H200
GPU slots (the cluster has 8 H200 nodes x 8 GPUs = 64 H200s; easy).

### Jobstats auto-monitor

Per `shared/notes/operational-practices.md`, HeadAI 1.2 is responsible for
arming the jobstats auto-monitor immediately after the first SLURM submission
(WW, 8885960). The monitor's STOP signal should fire when the last MACE
trajectory reaches a terminal state (either all 3 complete 5 ns, or all 3
are cancelled/failed).

### Resume/Restart Protocol (handoff to HeadAI)

When a SLURM job ends, read the SLURM exit code (in `sacct -j <id> -o ExitCode`)
and the script's meta JSON (`output/trajectories/mace_npt/<tag>_npt_meta.json`).

| Exit code | `production_status` in meta | Action |
|-----------|-----------------------------|--------|
| 0 | "target_reached" | Protein done; no action |
| 0 | "already_at_target" | Protein was already done on entry |
| 2 | "walltime_exit" | Resubmit: `./output/scripts/submit_mace_npt.sh <protein> <same-tag>` |
| 1 | "failed" | Check meta JSON `fatal_exception.traceback`. If NaN/barostat: fall back to NVT. If OpenCL hang on retry: fall back to RTX 5000 Ada. Document in cross-agent note. |

**Automated resubmission loop (optional bash pattern for HeadAI):**

```bash
TAG=m4k2pz9q; PROTEIN=ww; META=output/trajectories/mace_npt/${TAG}_npt_meta.json
for attempt in 1 2 3 4 5 6 7 8 9 10; do
    # Submit
    JOB=$(./output/scripts/submit_mace_npt.sh $PROTEIN $TAG | grep -oE '[0-9]+$')
    echo "attempt $attempt: job $JOB"
    # Wait for termination (poll sacct)
    while true; do
        STATE=$(sacct -j $JOB -n -o State --parsable2 | head -1 | tr -d ' ')
        case "$STATE" in
            COMPLETED|FAILED|TIMEOUT|CANCELLED*) break ;;
        esac
        sleep 600
    done
    # Check meta
    STATUS=$(python3 -c "import json; print(json.load(open('$META')).get('production_status', ''))")
    echo "attempt $attempt: state=$STATE status=$STATUS"
    case "$STATUS" in
        target_reached|already_at_target) exit 0 ;;
        walltime_exit) continue ;;
        failed) echo "FATAL"; exit 1 ;;
    esac
done
echo "Gave up after 10 attempts"; exit 1
```

HeadAI 1.2 should NOT start this loop as a background process from within a
Claude session -- use a separate detached `tmux`/`screen` session on the login
node, OR invoke the loop manually after each completion. This keeps the SubAgent
context clean.
