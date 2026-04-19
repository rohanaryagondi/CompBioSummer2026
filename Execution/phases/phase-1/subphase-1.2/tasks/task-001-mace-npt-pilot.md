---
task_id: "task-001"
title: "MACE-OFF24 NPT 5 ns × 3 Tier B (WW, GB3, ubiquitin) on H200 OpenCL hybrid"
subphase: "1.2"
track: alpha-m
wave: 1
agent: "mlff-mace-pilot"
effort: "8-12 days wall, ~420 GPU-hrs H200"
status: planned
created: 2026-04-18
---

# Task 001: MACE-OFF24 NPT 5 ns × 3 Tier B (WW, GB3, ubiquitin) on H200 OpenCL hybrid

## Objective

Validate that MACE-OFF24 hybrid (ML solute + classical TIP3P water + PME) produces
stable 5-ns NPT trajectories on three Tier B benchmark proteins (WW domain 34 aa,
GB3 56 aa, ubiquitin 76 aa). This is the first NPT MLFF run in the project. Sub 1.1
established stable NVT vacuum dynamics on crambin (D1 PASS); this task adds
constant-pressure dynamics (MonteCarloBarostat) and extends to larger Tier B
proteins. The output 5-ns NPT trajectories are the precursor evidence for D2 G1
("≥1 MLFF stable >10 ns on ≥3 Tier B proteins") which will be formally satisfied
in Sub 1.4 production at ≥10 ns scope. This task does NOT itself produce D2 G1
evidence — it produces 5-ns stability evidence that informs Sub 1.4 production scope.

---

## Context

**Why NPT (not NVT) for Sub 1.2:** Phase 2 production runs are NPT. Sub 1.2 must
demonstrate that MACE hybrid is stable under constant-pressure barostat coupling
before committing 47,300 GPU-hr Phase 2 production scope. NVT was sufficient for
D1 (software-validation gate) but D2 needs NPT-quality evidence.

**Why H200 OpenCL (not RTX 5000 Ada):** Sub 1.1 Subagent G empirical hybrid throughput
benchmark (`shared/notes/1.1-mace-hybrid-validation.md` §11): RTX 5000 Ada hybrid
WW = 0.184 ns/day; H200 hybrid WW = 2.11 ns/day = **11.5× speedup**. RTX 5000 Ada
makes Sub 1.2 infeasible (~50 days wall for 5 ns ubiquitin); H200 fits comfortably
(~6 days wall for 5 ns ubiquitin). Per the resolved Phase 2 MACE scope decision
(`shared/help-needed/sub-1.2-phase2-mlff-scope.md` Option 5), all Phase 2 MACE
production goes to H200 OpenCL. Sub 1.2 commits the same path.

**Why these 3 proteins:** Implementation Plan §8 Weeks 3-4 names exactly these
three proteins ("NPT stability tests (5 ns) on WW domain, GB3, ubiquitin"). They
span the Tier A/B size range (34, 56, 76 aa) and have excellent BMRB S2 references
(WW Pin1 Seewald 2007 NSMB 14:1120; GB3 BMRB 5839; ubiquitin BMRB 6470).

**Throughput projections (extrapolated from Sub 1.1 §11 measurements):**
- WW (534 MACE atoms / ~7,565 total) on H200 OpenCL hybrid: 2.11 ns/day → 5 ns ≈ **2.4 days wall**
- GB3 (~862 MACE atoms / ~9,874 total) on H200 OpenCL hybrid: ~1.2 ns/day → 5 ns ≈ **4.2 days wall**
- Ubiquitin (~1,231 MACE atoms / ~17,162 total) on H200 OpenCL hybrid: ~0.85 ns/day → 5 ns ≈ **5.9 days wall**

Total wall: ~12.5 days IF run sequentially. Run in parallel across 3 SLURM jobs
to fit ~6-day window. Each job WILL hit its time-limit and require checkpoint/restart
(YCRC max walltime varies by partition; gpu_h200 typically 24h-48h).

---

## Detailed Instructions

### Step 1: Fork and extend the Sub 1.1 hybrid script

Source: `phases/phase-1/subphase-1.1/output/scripts/mace_hybrid_nvt.py` (579 lines).
Fork to: `phases/phase-1/subphase-1.2/output/scripts/mace_hybrid_npt.py`.

**Required modifications:**

1. **Add MonteCarloBarostat for NPT.** Insert after system creation, before
   integrator setup. Use 1 atm reference pressure, 300 K reference temp, freq=25
   steps. Example pattern:
   ```python
   from openmm import MonteCarloBarostat
   from openmm.unit import atmosphere, kelvin
   barostat = MonteCarloBarostat(1.0 * atmosphere, 300 * kelvin, 25)
   system.addForce(barostat)
   ```

2. **Add checkpoint/restart support.** OpenMM has built-in `Simulation.saveCheckpoint(path)`
   and `Simulation.loadCheckpoint(path)`. Implementation:
   - Every 100 ps wall: save checkpoint to `<scratch>/<protein>/checkpoint_step_<N>.chk` AND `<scratch>/<protein>/checkpoint_latest.chk` (atomic mv)
   - At job startup: if `checkpoint_latest.chk` exists, load it and resume from saved step count; else start fresh from PDB → PDBFixer → solvation → minimization
   - Append-mode for trajectory: use `DCDReporter(path, interval, append=True)` so multiple SLURM jobs concatenate to one trajectory
   - Append-mode for state log: open StateDataReporter file in append mode if checkpoint loaded

3. **Add restart-friendly env vars.** Extend the env-var pattern from Sub 1.1:
   - `MACE_HYBRID_PROTEIN`: `ww` | `gb3` | `ubq`
   - `MACE_HYBRID_PDB`: explicit path (overrides protein default)
   - `MACE_HYBRID_RESRANGE`: optional residue crop (WW: 6-39 to crop Pin1 to WW domain)
   - `MACE_HYBRID_TARGET_NS`: total trajectory length target (5.0 for Sub 1.2)
   - `MACE_HYBRID_BAROSTAT`: `npt` | `nvt` (default `npt` for Sub 1.2; `nvt` for fallback)
   - `MACE_OUTPUT_DIR`: output dir on persistent storage
   - `MACE_SCRATCH_DIR`: scratch dir for checkpoints + active trajectory
   - `MACE_HYBRID_TAG`: 8-char alphanumeric tag for SLURM job

4. **Keep all Sub 1.1 safeguards:**
   - `os.environ['PYTHONNOUSERSITE'] = '1'` at top of file (line 40 in original)
   - Energy minimization: `maxIterations=2000` (DO NOT reduce — Sub 1.1 NaN regression)
   - Post-minimization max-force safety check: if max force > 1e5 kJ/mol/nm, fail fast
   - GPU keepalive thread (5-min cadence, 64×64 matmul, daemon thread) — copy from Sub 1.1
   - OpenCL platform (NOT CUDA) — required per Sub 1.1 Subagent A finding (CUDA broken on H200/B200/RTX 5000 Ada with sm_89/sm_90/sm_100)

5. **Add NPT-specific stability checks.** In the trajectory analysis (post-run):
   - Density: physical (~1000 kg/m³ ± 50 for water-dominated systems)
   - Pressure: 1 atm ± 200 atm tolerated (barostat fluctuations)
   - Box volume: monotonic equilibration in first ~1 ns then stable
   - All Sub 1.1 NVT checks (T = 300 ± 15 K, no NaN, energy non-divergent)

### Step 2: Stage A — equilibration (NVT 50 ps + NPT 200 ps) for each protein

For each of WW, GB3, ubiquitin:

1. PDB source: `phases/phase-0/subphase-0.1/proteins/<name>.pdb`. WW requires
   residue crop 6-39 from Pin1 (per Sub 1.1 pattern).
2. PDBFixer pipeline (already in Sub 1.1 script): add missing atoms, add hydrogens
   at pH 7.0, solvate with TIP3P (1.0 nm padding), add Na+/Cl- to neutralize at 0.15 M.
3. Energy minimization: maxIterations=2000, tolerance=10 kJ/mol/nm. Verify post-min
   max force < 1e5 kJ/mol/nm.
4. NVT equilibration: 50 ps at 300 K, LangevinMiddleIntegrator dt=0.5 fs (smaller
   than Sub 1.1 1 fs to be safe with hybrid forces during equilibration).
5. NPT equilibration: 200 ps at 300 K, 1 atm, MonteCarloBarostat freq=25 steps,
   integrator dt=1 fs.
6. Save state at end of equilibration as `<scratch>/<protein>/equil_state.xml`.

### Step 3: Stage B — production NPT (4.75 ns target after 250 ps equil)

For each protein:

1. Load equil state.
2. Production NPT: 4.75 ns at 300 K, 1 atm, MonteCarloBarostat freq=25, dt=1 fs.
3. Trajectory: DCD every 1 ps (4,750 frames per protein, ~50 MB per protein).
4. State log: every 100 steps (T, KE, PE, E, V, P, Density).
5. Checkpoint: every 100,000 steps (every ~100 ps wall under good throughput).
6. Total wall per protein: see throughput projections above (2.4 / 4.2 / 5.9 days).
   Each will hit 24h SLURM walltime ≥3-6 times → checkpoint/restart loop required.

### Step 4: SLURM submission

Submit one SLURM job per protein (3 jobs total in Wave 1). Each job:

```bash
#!/bin/bash
#SBATCH --job-name=<8-char-cryptic>
#SBATCH --partition=gpu_h200
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=23:59:00
#SBATCH --account=pi_mg269
#SBATCH --output=<output_dir>/slurm-%j.out
#SBATCH --error=<output_dir>/slurm-%j.err

set -euo pipefail
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env-mace
export PYTHONNOUSERSITE=1
export MACE_HYBRID_PROTEIN=<ww|gb3|ubq>
export MACE_HYBRID_TARGET_NS=5.0
export MACE_HYBRID_BAROSTAT=npt
export MACE_HYBRID_TAG=<same-cryptic-tag>
export MACE_OUTPUT_DIR=phases/phase-1/subphase-1.2/output/trajectories/mace_npt
export MACE_SCRATCH_DIR=/nfs/roberts/scratch/pi_mg269/rag88/alpha-m/mace-npt

python phases/phase-1/subphase-1.2/output/scripts/mace_hybrid_npt.py
```

**Resubmission protocol when job hits walltime:**
- Submit a fresh job with the same `MACE_HYBRID_TAG` (NOT a SLURM dependency chain — those are fragile under preemption). The script detects the existing checkpoint and resumes.
- Use a wrapper bash script that loops: submit job, wait for it to terminate, check progress.txt for `total_ns >= 5.0`, if not, resubmit. Limit to 10 iterations to prevent infinite loops.

### Step 5: Stability analysis (per-protein report)

After each protein reaches 5 ns total trajectory, run analysis:

```python
import mdtraj as md
import numpy as np
import pandas as pd

traj = md.load(f"{output_dir}/{protein}_npt.dcd", top=f"{output_dir}/{protein}_topology.pdb")
state_log = pd.read_csv(f"{output_dir}/{protein}_state.csv")

# Stability metrics
print(f"  Total frames: {traj.n_frames}")
print(f"  Trajectory length: {traj.n_frames * 0.001} ns (1 ps stride)")
print(f"  T mean ± std: {state_log['Temperature (K)'].mean():.1f} ± {state_log['Temperature (K)'].std():.1f} K")
print(f"  P mean ± std: {state_log['Pressure (atm)'].mean():.1f} ± {state_log['Pressure (atm)'].std():.1f} atm")
print(f"  Density mean ± std: {state_log['Density (g/mL)'].mean():.4f} ± {state_log['Density (g/mL)'].std():.4f} g/mL")
print(f"  Box volume drift (last 1 ns vs first 1 ns): {abs(state_log['Box Volume (nm^3)'][-1000:].mean() - state_log['Box Volume (nm^3)'][1000:2000].mean()):.2f} nm³")
print(f"  PE NaN check: {state_log['Potential Energy (kJ/mole)'].isna().sum()} NaN values")
print(f"  C-alpha RMSD vs frame 0: {md.rmsd(traj, traj, 0, atom_indices=traj.top.select('name CA')).max() * 10:.2f} Å")
```

Pass criteria for each protein:
- Total trajectory ≥4.5 ns (90% of 5 ns target — small allowance for restart loss)
- Zero NaN in PE / KE / T
- T = 300 ± 15 K mean
- P = 1 atm ± 200 atm mean (barostat noisy; what matters is no drift)
- Density physical: 0.95-1.05 g/mL for water-dominated systems
- Box volume converged (drift < 5% from 1-2 ns to last 1 ns)
- C-alpha RMSD bounded < 5 Å (no protein unfolding)

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| `../../tasks/task-001-mace-npt-pilot.md` | This task spec |
| `../../../subphase-1.1/output/scripts/mace_hybrid_nvt.py` | Source script to fork |
| `../../../../../shared/notes/1.1-mace-hybrid-validation.md` | §11 H200 OpenCL throughput; §9-10 hybrid validation context |
| `../../../../../shared/notes/1.1-mace-crambin.md` | D1 PASS evidence; OpenMM ML potential name (`mace-off24-medium`) and platform fallback pattern |
| `../../../../../shared/notes/operational-practices.md` | Cryptic job names, jobstats lifecycle, GPU keepalive, SU policy |
| `../../../../../../phases/phase-0/subphase-0.1/proteins/manifest.json` | Protein metadata (PDB paths, residue ranges) |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../shared/notes/1.1-mace-phase2-feasibility.md` | Phase 2 MACE feasibility analysis context |
| `../../../../../shared/help-needed/sub-1.2-phase2-mlff-scope.md` | Resolved Option 5 commitment + 4-option analysis |
| `../../../../../../Proposal/Alpha-M.md` (§5.2) | Tier A/B/C definitions for context on protein selection |

### DO NOT READ

- Other SubAgents' task specs in `../../tasks/` (not your scope)
- Other SubAgents' output (unless listed as a dependency)
- `../../../../../../Proposal/HumanOnlyProposal.md` (off-limits)
- Future subphase plans (1.3, 1.4 do not exist yet)

---

## Output Artifacts

### Code and data artifacts

| Artifact | Path | Format |
|----------|------|--------|
| Forked production script | `../../output/scripts/mace_hybrid_npt.py` | Python |
| WW NPT trajectory | `../../output/trajectories/mace_npt/ww_npt.dcd` (+ topology + state log) | DCD + PDB + CSV |
| GB3 NPT trajectory | `../../output/trajectories/mace_npt/gb3_npt.dcd` (+ topology + state log) | DCD + PDB + CSV |
| Ubiquitin NPT trajectory | `../../output/trajectories/mace_npt/ubq_npt.dcd` (+ topology + state log) | DCD + PDB + CSV |
| Per-protein stability report | `../../output/mace_npt_stability_report.md` | Markdown table per protein |
| Aggregate experiment log | `../../output/task-001-experiment.md` | Experiment-log template |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-001-status.md` | `templates/status-report.md` |
| Experiment log | `../../output/task-001-experiment.md` | `templates/experiment-log.md` |
| Cross-agent note | `../../../../../shared/notes/1.2-mace-npt-stability.md` | `templates/cross-agent-note.md` |

---

## Success Criteria (Zero Compromise)

This task is complete ONLY if ALL of the following are true:

1. [ ] `mace_hybrid_npt.py` exists at `../../output/scripts/` with NPT support + checkpoint/restart
2. [ ] WW domain trajectory: ≥4.5 ns total (5 ns target with 10% restart-loss tolerance), stable T/P/density, zero NaN
3. [ ] GB3 trajectory: ≥4.5 ns total, stable T/P/density, zero NaN
4. [ ] Ubiquitin trajectory: ≥4.5 ns total, stable T/P/density, zero NaN
5. [ ] Per-protein stability report at `../../output/mace_npt_stability_report.md` with the metrics from Step 5
6. [ ] Cross-agent note `1.2-mace-npt-stability.md` written summarizing per-protein results, comparing to Sub 1.1 NVT crambin results, flagging any concerns for Sub 1.4 production scope
7. [ ] All SLURM job names are 8-char cryptic alphanumeric (no descriptive names)
8. [ ] H200 SU consumption documented (estimate before submitting; record actual after)
9. [ ] Status report written to `../../status/task-001-status.md`

---

## Verification

Before declaring this task complete, verify:

1. `ls ../../output/trajectories/mace_npt/` shows 3 .dcd + 3 topology .pdb + 3 state .csv files
2. For each .dcd file: `python -c "import mdtraj; t=mdtraj.load('$file', top='$top'); print(t.n_frames)"` returns ≥4500
3. `grep -c "NaN\|nan" ../../output/trajectories/mace_npt/*_state.csv` returns 0
4. Stability report contains per-protein T/P/density/RMSD with all values within pass criteria
5. Cross-agent note `1.2-mace-npt-stability.md` exists with frontmatter + tracks tag + summary
6. Status report at `../../status/task-001-status.md` exists with status `complete`

---

## Failure Protocol

If this task cannot be completed:

1. **MACE NPT crashes (barostat instability):** Fall back to NVT (Sub 1.1 demonstrated stable). Re-run all 3 proteins as NVT for 5 ns. Document NPT failure in cross-agent note. Status: `partial-fallback-nvt`. HeadAI accepts and proceeds.

2. **MACE H200 OpenCL hangs persistently (3+ resumes):** Fall back to RTX 5000 Ada (slower but stable per Subagent L data). Reduce scope to 1 Tier B protein × 5 ns or 3 proteins × 1 ns. Document the throughput regression. Status: `partial`. Escalate to HeadAI as help-needed if scope reduction breaks D2 path.

3. **Specific protein fails repeatedly (e.g., GB3 unfolds):** Drop that protein from the report; document in cross-agent note as a candidate-for-Sub-1.4-investigation finding. Continue with remaining 2 proteins. Status: `partial`. HeadAI assesses whether 2 proteins suffice for Sub 1.2 evidence (yes — D2 G1 needs ≥3 in Sub 1.4, not in Sub 1.2).

4. **OpenCL platform itself broken (Sub 1.1 used 1.51 ns/day, regression to <0.5 ns/day on H200):** Diagnose with simple crambin smoke test in env-mace (Sub 1.1 baseline known-good). If env regressed, reinstall env-mace from `phases/phase-0/subphase-0.1/envs/env-mace.yml`. If hardware/driver regressed, escalate to HeadAI as help-needed.

5. **All 3 proteins fail:** Status: `failed`. Write help-needed doc with full diagnostics. MACE Phase 2 path is at risk; PlannerAI must reassess Option 5 commitment.

In all failure cases: write status report with status (`complete` | `partial` | `partial-fallback-nvt` | `failed`), document exactly what went wrong (error messages, log excerpts, partial trajectory lengths), document what was tried, identify what help is needed.
