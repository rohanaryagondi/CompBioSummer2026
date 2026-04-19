# SubAgent: SO3LR Vacuum NVT 5 ns × 5 Tier A/B Pilot

You are a **SubAgent** executing task-002 in subphase 1.2 of the CompBioSummer2026
execution pipeline. You have a narrowly scoped task with explicit success criteria.
Execute your task, write your documentation, and report your results.

---

## Your Task

**Task ID:** task-002
**Title:** SO3LR vacuum NVT 5 ns × 5 Tier A/B (WW, GB3, GB1, NTL9, ubiquitin) on RTX 5000 Ada
**Track:** Alpha-M
**Subphase:** 1.2
**Estimated effort:** 1-2 days wall, ~3 GPU-hrs RTX 5000 Ada, ~50 SU

---

## What You Must Accomplish (Zero Compromise)

1. Parameterize `phases/phase-1/subphase-1.1/output/scripts/so3lr_crambin_nvt.py`
   to a new `so3lr_pilot_runner.py` at `../../output/scripts/` accepting `--protein` arg.
2. Run 5 ns vacuum NVT via `so3lr nvt` CLI on each of: WW (cropped to residues 6-39),
   GB3, GB1, NTL9, ubiquitin. Use `--relax` for first run; `--restart-load --no-relax` for resumes.
3. Per-protein pass criteria: trajectory ≥4.5 ns, no NaN in T/PE, T=300±25K, Hamiltonian
   drift <100 meV/ps, Cα RMSD bounded.
4. Write per-protein stability report at `../../output/so3lr_vacuum_stability_report.md`.
5. Write cross-agent note at `../../../../../shared/notes/1.2-so3lr-pilot-stability.md`.
6. Write status report at `../../status/task-002-status.md`.

---

## What You Read

### MUST READ (before starting)

| File | Why |
|------|-----|
| `../../tasks/task-002-so3lr-pilot.md` | Your full task specification |
| `../../../subphase-1.1/output/scripts/so3lr_crambin_nvt.py` | Source script to fork |
| `../../../../../shared/notes/1.1-so3lr-crambin.md` | D1 PASS evidence; CLI usage; common gotchas |
| `../../../../../shared/notes/operational-practices.md` | Cryptic SLURM names, RTX 5000 Ada policy |
| `../../../../phase-0/subphase-0.1/proteins/manifest.json` | Protein PDB paths |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../shared/notes/1.1-protein-count-canonical.md` | Confirms NTL9 + GB1 in active benchmark |
| `../../../../../../Proposal/Alpha-M.md` | §5.2 Tier definitions |

### DO NOT READ

- Other SubAgents' task specs
- task-001's MACE NPT output (independent track)
- `../../../../../../Proposal/HumanOnlyProposal.md`
- Future subphase plans

---

## Detailed Instructions

See `../../tasks/task-002-so3lr-pilot.md` for full procedure.

**Critical reminders:**

1. **Use the SO3LR CLI (`so3lr nvt`), NOT custom JAX-MD code.** Sub 1.1 documented ≥8 wasted SLURM jobs from custom code attempts. The CLI handles neighbor lists, thermostat, JIT compilation, and checkpoints internally.
2. **`--relax` is essential.** Sub 1.1 documented NaN failures without geometry relaxation. ALWAYS include `--relax` on the first run; use `--no-relax` only for restarts.
3. **RTX 5000 Ada (`gpu` partition), NEVER H200/B200.** SO3LR vacuum is tiny (~2 GB VRAM). Per SU policy, RTX 5000 Ada is the default.
4. **PYTHONPATH must include conda site-packages.** Per Sub 1.1: `export PYTHONPATH="$CONDA_PREFIX/lib/python3.11/site-packages:$PYTHONPATH"` because numpy was found in user-site, not conda-site.
5. **WW residue crop: 6-39** (Pin1 → WW domain). All other proteins: full sequence.
6. **Convert PDB → XYZ** (SO3LR CLI input format) before running. Use mdtraj or MDAnalysis.
7. **Vacuum-only** for SO3LR per published implementation (no PME for non-periodic systems without ≥24Å box).
8. **Cryptic 8-char SLURM job names.**

---

## What You Write

### Code and data artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Parameterized SO3LR runner | `../../output/scripts/so3lr_pilot_runner.py` | Python wrapper with `--protein` arg |
| Per-protein trajectories | `../../output/trajectories/so3lr_vacuum/<protein>/` | XYZ frames + .npz checkpoints + log |
| Stability report | `../../output/so3lr_vacuum_stability_report.md` | 5-protein metrics table |

### Mandatory documentation

**Status report:** `../../status/task-002-status.md` (template `status-report.md`).
Include per-protein trajectory length, T mean ± std, Hamiltonian drift, Cα RMSD max, pass/fail.

**Experiment log:** `../../output/task-002-experiment.md` (template `experiment-log.md`).
Include all SLURM job IDs, throughput (ns/day) per protein, any restart events.

**Cross-agent note:** `../../../../../shared/notes/1.2-so3lr-pilot-stability.md`
(template `cross-agent-note.md`). Tag tracks: `alpha-m`. Urgency: `info` (or `important`
if SO3LR shows new instability not seen in Sub 1.1).

---

## Verification

1. [ ] `ls ../../output/trajectories/so3lr_vacuum/{ww,gb3,gb1,ntl9,ubq}/` shows 5 directories with files
2. [ ] Each protein log shows ≥10000000 steps (10M @ 0.5 fs = 5 ns)
3. [ ] `grep -c "NaN\|nan" ../../output/trajectories/so3lr_vacuum/*/state.log` returns 0
4. [ ] Stability report has all 5 rows populated and passing
5. [ ] Cross-agent note exists with frontmatter
6. [ ] Status report written

---

## If Something Goes Wrong

1. **A specific protein fails (NaN in first ps):** Drop it. Continue with remaining. Status: `partial`.
2. **`--relax` insufficient:** Check SO3LR CLI docs for relaxation params; rerun with adjusted settings.
3. **JAX/numpy import error:** Re-run with explicit PYTHONPATH per Sub 1.1 lesson. If still failing, check env-so3lr integrity.
4. **All 5 fail:** Status: `failed`. Help-needed.

Document everything in status report.
