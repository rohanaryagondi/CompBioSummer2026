---
task_id: "task-002"
title: "SO3LR vacuum NVT 5 ns × 5 Tier A/B (WW, GB3, GB1, NTL9, ubiquitin) on RTX 5000 Ada"
subphase: "1.2"
track: alpha-m
wave: 1
agent: "mlff-so3lr-pilot"
effort: "1-2 days wall, ~3 GPU-hrs RTX 5000 Ada"
status: planned
created: 2026-04-18
---

# Task 002: SO3LR vacuum NVT 5 ns × 5 Tier A/B proteins

## Objective

Validate that SO3LR (the second MLFF in the Alpha-M roster, complementing MACE-OFF24)
produces stable 5-ns vacuum NVT trajectories on five Tier A/B benchmark proteins
(WW 34 aa, GB3 56 aa, GB1 56 aa, NTL9 51 aa, ubiquitin 76 aa). Sub 1.1 demonstrated
stable 1-ns vacuum NVT on crambin via the SO3LR CLI (D1 PASS); this task extends
to 5 proteins at 5 ns each. SO3LR vacuum trajectories are independent of MACE
(Sub 1.1 documented vacuum-only constraint due to the lack of explicit-water PME
in the published SO3LR distribution). Output 5-ns trajectories support the SO3LR
side of the D2 G1 criterion ("≥1 MLFF stable >10 ns on ≥3 Tier B proteins") —
SO3LR can independently satisfy G1 if MACE NPT scope is reduced.

---

## Context

**Why vacuum (not solvated):** Per Sub 1.1 Subagent A analysis and the SO3LR
codebase, SO3LR does NOT support explicit-water PME for non-periodic systems
without ≥24 Å box. For a Tier A/B protein in TIP3P, the box would be impractically
large. Vacuum NVT is the native SO3LR path. This is documented in the help-needed
analysis (`shared/help-needed/sub-1.2-phase2-mlff-scope.md` Option 3).

**Why these 5 proteins (vs 3 for MACE):** SO3LR is much faster (15 ns/day on
RTX 5000 Ada per Sub 1.1 crambin: 5373 s for 1 ns = ~16 ns/day extrapolated).
At this throughput, 5 ns × 5 proteins = 25 ns ≈ 1.5 days wall on a single GPU.
Adding 2 more proteins (vs MACE's 3) gives D2 G1 broader coverage at zero
incremental cost. WW + GB3 + ubiquitin overlap with task-001 for direct comparison;
GB1 + NTL9 add Tier B diversity (NTL9 is one of the new Sub 1.1 additions).

**Why use the SO3LR CLI (not custom JAX-MD code):** Sub 1.1 documented that
prior agents wasted ≥8 SLURM jobs writing custom JAX-MD wrappers that hit shape
broadcasting bugs and NaN. The `so3lr nvt` CLI handles neighbor lists, thermostat,
JIT compilation, and checkpoints internally. Use it. See `shared/notes/1.1-so3lr-crambin.md`.

**Throughput projections (extrapolated from Sub 1.1 crambin):**
- Crambin (640 atoms vacuum): 2.93 ms/step × 1e6 steps for 0.5 fs dt × 1 ns = 5373 s = ~16 ns/day
- WW (~530 atoms): faster than crambin (smaller); estimate ~20 ns/day → 5 ns ≈ 6 hours
- GB3/GB1 (~870 atoms): ~12 ns/day → 5 ns ≈ 10 hours
- NTL9 (~770 atoms): ~14 ns/day → 5 ns ≈ 9 hours
- Ubiquitin (~1,230 atoms): ~8 ns/day → 5 ns ≈ 15 hours
- **Total wall (sequential):** ~52 hours = 2.2 days; (parallel across 5 GPUs): ~15 hours

---

## Detailed Instructions

### Step 1: Parameterize the Sub 1.1 SO3LR script

Source: `phases/phase-1/subphase-1.1/output/scripts/so3lr_crambin_nvt.py`. Sub 1.1's
script hardcodes crambin paths. Fork to:
`phases/phase-1/subphase-1.2/output/scripts/so3lr_pilot_runner.py`.

**Changes:**

1. Accept `--protein` arg (one of `ww`, `gb3`, `gb1`, `ntl9`, `ubq`).
2. Look up PDB path from manifest: `phases/phase-0/subphase-0.1/proteins/manifest.json` (use `protein_name` → `pdb_path` map).
3. Convert PDB → XYZ (SO3LR CLI input format):
   - Use `MDAnalysis` or `mdtraj` to write XYZ from the cleaned PDB.
   - WW: crop to residues 6-39 (Pin1 → WW) before XYZ conversion.
   - All proteins: ensure no waters or ions in XYZ (vacuum input).
4. Run `so3lr nvt --input <protein>.xyz --dt 0.5 --temperature 300 --md-cycles 10 --md-steps 1000000 --relax`:
   - `--md-cycles 10 --md-steps 1000000` = 10M steps × 0.5 fs = 5 ns (matches target)
   - `--relax` is essential — Sub 1.1 documented NaN failures without geometry relaxation
   - Checkpoints saved automatically by SO3LR CLI as `.npz` files
   - Stdout includes step counter, T, KE, PE — capture to a log file for analysis
5. If a protein is restart-needed (job timed out):
   - Use `so3lr nvt --restart-load <last>.npz --no-relax` (NOT `--relax`, as relaxation would re-trigger geometry change)
6. Output directory per protein: `phases/phase-1/subphase-1.2/output/trajectories/so3lr_vacuum/<protein>/`

### Step 2: SLURM submission

Submit one SLURM job per protein (5 jobs total). Each job:

```bash
#!/bin/bash
#SBATCH --job-name=<8-char-cryptic>
#SBATCH --partition=gpu        # RTX 5000 Ada (15 SU/hr)
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=1-00:00:00
#SBATCH --account=pi_mg269
#SBATCH --output=phases/phase-1/subphase-1.2/output/trajectories/so3lr_vacuum/<protein>/slurm-%j.out

set -euo pipefail
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env-so3lr
export PYTHONNOUSERSITE=1
# numpy must be in conda env's site-packages, not user site (Sub 1.1 lesson)
export PYTHONPATH="$CONDA_PREFIX/lib/python3.11/site-packages:$PYTHONPATH"

python phases/phase-1/subphase-1.2/output/scripts/so3lr_pilot_runner.py \
    --protein <ww|gb3|gb1|ntl9|ubq> \
    --target-ns 5.0 \
    --output-dir phases/phase-1/subphase-1.2/output/trajectories/so3lr_vacuum
```

If a job hits walltime, resubmit with `--restart-load <last>.npz --no-relax` per
the Sub 1.1 protocol.

### Step 3: Stability analysis (per-protein report)

For each protein after 5 ns trajectory complete:

```python
import numpy as np
import pandas as pd
import mdtraj as md

# SO3LR outputs trajectory as XYZ frames (SO3LR CLI default)
# Convert XYZ → DCD for analysis with mdtraj
log = pd.read_csv(f"{output_dir}/{protein}/state.log", sep=r'\s+')

# Stability metrics
T_mean, T_std = log['T_K'].mean(), log['T_K'].std()
PE_drift = log['PE_eV'].iloc[-1000:].mean() - log['PE_eV'].iloc[1000:2000].mean()
H_drift_meV_per_ps = (log['Hamiltonian_eV'].iloc[-1] - log['Hamiltonian_eV'].iloc[0]) * 1000 / log['t_ps'].iloc[-1]

print(f"  T: {T_mean:.1f} ± {T_std:.1f} K (target 300)")
print(f"  PE drift over last 1 ns: {PE_drift:.4f} eV (should be near 0)")
print(f"  Hamiltonian drift: {H_drift_meV_per_ps:.2f} meV/ps (acceptable < 50 meV/ps for NVT float32)")
print(f"  NaN check: {log[['T_K','PE_eV']].isna().sum().sum()} NaN")
```

Pass criteria for each protein:
- Total trajectory ≥4.5 ns
- Zero NaN in T or PE
- T = 300 ± 25 K mean (SO3LR vacuum is noisier than solvated)
- Hamiltonian drift < 100 meV/ps (Sub 1.1 crambin baseline 15 meV/ps)
- C-alpha RMSD bounded < 7 Å (vacuum allows more breathing than solvated)

### Step 4: Cross-protein summary

Aggregate the 5 proteins into a stability table and write to
`../../output/so3lr_vacuum_stability_report.md`:

| Protein | aa | Trajectory ns | T mean (K) | PE drift (eV) | H drift (meV/ps) | Cα RMSD max (Å) | Pass? |
|---------|----|--------------:|-----------:|--------------:|-----------------:|-----------------:|:-----:|
| ww | 34 | ... | ... | ... | ... | ... | YES/NO |
| gb3 | 56 | ... | ... | ... | ... | ... | YES/NO |
| gb1 | 56 | ... | ... | ... | ... | ... | YES/NO |
| ntl9 | 51 | ... | ... | ... | ... | ... | YES/NO |
| ubq | 76 | ... | ... | ... | ... | ... | YES/NO |

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| `../../tasks/task-002-so3lr-pilot.md` | This task spec |
| `../../../subphase-1.1/output/scripts/so3lr_crambin_nvt.py` | Source script to fork |
| `../../../../../shared/notes/1.1-so3lr-crambin.md` | D1 PASS evidence; CLI usage guidance; common gotchas (numpy site-packages, --relax) |
| `../../../../../shared/notes/operational-practices.md` | Cryptic job names, SU policy, jobstats lifecycle |
| `../../../../../../phases/phase-0/subphase-0.1/proteins/manifest.json` | Protein PDB paths and metadata |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../shared/notes/1.1-protein-count-canonical.md` | Confirms NTL9 + GB1 in active benchmark |
| `../../../../../../Proposal/Alpha-M.md` (§5.2) | Tier definitions |

### DO NOT READ

- Other SubAgents' task specs in `../../tasks/`
- task-001's MACE NPT output (independent track)
- `../../../../../../Proposal/HumanOnlyProposal.md`
- Future subphase plans

---

## Output Artifacts

### Code and data artifacts

| Artifact | Path | Format |
|----------|------|--------|
| Parameterized SO3LR runner | `../../output/scripts/so3lr_pilot_runner.py` | Python |
| Per-protein trajectories | `../../output/trajectories/so3lr_vacuum/<protein>/trajectory.xyz` (+ checkpoint .npz, log) | XYZ + NPZ + log |
| Per-protein stability report | `../../output/so3lr_vacuum_stability_report.md` | Markdown table |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-002-status.md` | `templates/status-report.md` |
| Experiment log | `../../output/task-002-experiment.md` | `templates/experiment-log.md` |
| Cross-agent note | `../../../../../shared/notes/1.2-so3lr-pilot-stability.md` | `templates/cross-agent-note.md` |

---

## Success Criteria (Zero Compromise)

1. [ ] `so3lr_pilot_runner.py` exists at `../../output/scripts/` with `--protein` arg support
2. [ ] WW vacuum trajectory: ≥4.5 ns total, stable T, no NaN
3. [ ] GB3 vacuum trajectory: ≥4.5 ns total, stable T, no NaN
4. [ ] GB1 vacuum trajectory: ≥4.5 ns total, stable T, no NaN
5. [ ] NTL9 vacuum trajectory: ≥4.5 ns total, stable T, no NaN
6. [ ] Ubiquitin vacuum trajectory: ≥4.5 ns total, stable T, no NaN
7. [ ] Per-protein stability report at `../../output/so3lr_vacuum_stability_report.md`
8. [ ] Cross-agent note `1.2-so3lr-pilot-stability.md` written
9. [ ] All SLURM job names are 8-char cryptic alphanumeric
10. [ ] Status report written to `../../status/task-002-status.md`

---

## Verification

1. `ls ../../output/trajectories/so3lr_vacuum/{ww,gb3,gb1,ntl9,ubq}/` shows 5 directories with `.xyz` + `.npz` + log files
2. Each protein's log shows ≥10000000 steps (10M @ 0.5 fs = 5 ns)
3. `grep -c "NaN\|nan" ../../output/trajectories/so3lr_vacuum/*/state.log` returns 0
4. Stability report has all 5 rows populated with passing values
5. Status report exists with status `complete`

---

## Failure Protocol

1. **A specific protein fails (NaN in first ps):** Drop it. Continue with remaining proteins. Status: `partial`.
2. **`--relax` insufficient (NaN early in production):** Increase `--md-steps` for relaxation phase per SO3LR CLI docs; rerun.
3. **JAX/numpy import error:** Re-run with explicit `PYTHONPATH` per Sub 1.1 lesson. If still failing, check `env-so3lr` integrity.
4. **All 5 fail:** Status: `failed`. Help-needed doc. SO3LR Phase 2 path at risk.

Document everything in status report.
