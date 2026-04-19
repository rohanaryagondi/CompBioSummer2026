# SubAgent: MACE-OFF24 NPT 5 ns × 3 Tier B Pilot

You are a **SubAgent** executing task-001 in subphase 1.2 of the CompBioSummer2026
execution pipeline. You have a narrowly scoped task with explicit success criteria.
Execute your task, write your documentation, and report your results.

---

## Your Task

**Task ID:** task-001
**Title:** MACE-OFF24 NPT 5 ns × 3 Tier B (WW, GB3, ubiquitin) on H200 OpenCL hybrid
**Track:** Alpha-M
**Subphase:** 1.2
**Estimated effort:** 8-12 days wall, ~420 GPU-hrs H200, ~125,000 SU

---

## What You Must Accomplish (Zero Compromise)

1. Fork `phases/phase-1/subphase-1.1/output/scripts/mace_hybrid_nvt.py` to a new
   `mace_hybrid_npt.py` at `../../output/scripts/`. Add `MonteCarloBarostat` (NPT)
   + checkpoint/restart support. Keep all Sub 1.1 safeguards (GPU keepalive,
   `PYTHONNOUSERSITE=1`, post-min max-force check, OpenCL platform).
2. Run 5 ns NPT on **WW domain** (residues 6-39 of Pin1, 34 aa) on H200 OpenCL hybrid.
   Trajectory ≥4.5 ns total, T=300±15K, P=1atm±200, density physical, no NaN.
3. Run 5 ns NPT on **GB3** (56 aa) on H200 OpenCL hybrid. Same pass criteria.
4. Run 5 ns NPT on **ubiquitin** (76 aa) on H200 OpenCL hybrid. Same pass criteria.
5. Each protein WILL require ≥2 SLURM submissions (24h walltime per job; trajectories
   take 2-6 days each at H200 OpenCL throughput). Use checkpoint/restart loop.
6. Write per-protein stability report at `../../output/mace_npt_stability_report.md`.
7. Write cross-agent note at `../../../../../shared/notes/1.2-mace-npt-stability.md`.
8. Write status report at `../../status/task-001-status.md`.

---

## What You Read

### MUST READ (before starting)

| File | Why |
|------|-----|
| `../../tasks/task-001-mace-npt-pilot.md` | Your full task specification with step-by-step instructions |
| `../../../subphase-1.1/output/scripts/mace_hybrid_nvt.py` | Source script to fork |
| `../../../../../shared/notes/1.1-mace-hybrid-validation.md` | §11 H200 OpenCL throughput; §9-10 hybrid validation context |
| `../../../../../shared/notes/1.1-mace-crambin.md` | D1 PASS evidence; ML potential name; platform fallback pattern |
| `../../../../../shared/notes/operational-practices.md` | Cryptic SLURM job names, jobstats lifecycle, GPU keepalive, SU policy |
| `../../../../phase-0/subphase-0.1/proteins/manifest.json` | Protein PDB paths and metadata (WW, GB3, ubq) |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../shared/notes/1.1-mace-phase2-feasibility.md` | Phase 2 MACE feasibility analysis |
| `../../../../../shared/help-needed/sub-1.2-phase2-mlff-scope.md` | Resolved Option 5 commitment + 4-option analysis |
| `../../../../../shared/notes/1.1-mace-cuda-benchmark.md` | Why CUDA was rejected; OpenCL is the only path |
| `../../../../../../Proposal/Alpha-M.md` | §5.2 Tier A/B/C definitions |

### DO NOT READ

- Other SubAgents' task specs in `../../tasks/` (not your scope)
- Other SubAgents' output (independent tracks)
- `../../../../../../Proposal/HumanOnlyProposal.md` (off-limits)
- Future subphase plans (1.3, 1.4 do not exist yet)

---

## Detailed Instructions

See `../../tasks/task-001-mace-npt-pilot.md` for the full step-by-step procedure
(Step 1: fork script; Step 2: equilibration; Step 3: production NPT; Step 4:
SLURM submission; Step 5: stability analysis).

**Critical reminders:**

1. **Use OpenCL platform, NOT CUDA.** Sub 1.1 documented CUDA broken on all GPUs (sm_89/sm_90/sm_100). Subagent L confirmed CUDA rebuild yields zero speedup. OpenCL is mandatory.
2. **Use H200 (`gpu_h200` partition), NOT RTX 5000 Ada.** H200 OpenCL is 11.5× faster (Sub 1.1 §11; 2.11 ns/day hybrid WW measured). RTX 5000 Ada makes Sub 1.2 infeasible.
3. **Cryptic 8-char SLURM job names.** Per user memory + operational-practices.md. Examples: `m4k2pz9q`, `p3v8xt7r`. NEVER descriptive names.
4. **GPU keepalive thread mandatory.** Copy from Sub 1.1's `mace_hybrid_nvt.py`. 5-min cadence. Daemon thread.
5. **Energy minimization: maxIterations=2000.** Sub 1.1 reverted from 200 due to NaN regression. Do NOT lower.
6. **Post-minimization max-force check.** If max force > 1e5 kJ/mol/nm, fail fast. Already in Sub 1.1 script.
7. **Checkpoint/restart MUST be in `mace_hybrid_npt.py`.** Without it, ubiquitin (5.9 day wall) cannot fit any single SLURM job. Use `Simulation.saveCheckpoint()` and `loadCheckpoint()`. Save every 100 ps wall.
8. **Resubmission protocol:** Same `MACE_HYBRID_TAG` env var across resubmissions. Script auto-detects existing checkpoint. Do NOT use SLURM dependency chains (fragile under preemption).

---

## What You Write

### Code and data artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Forked production script | `../../output/scripts/mace_hybrid_npt.py` | NPT-capable hybrid script with checkpoint/restart |
| WW NPT trajectory | `../../output/trajectories/mace_npt/ww_npt.dcd` (+ topology, state log) | OpenMM DCD; ≥4500 frames @ 1ps |
| GB3 NPT trajectory | `../../output/trajectories/mace_npt/gb3_npt.dcd` (+ topology, state log) | Same |
| Ubiquitin NPT trajectory | `../../output/trajectories/mace_npt/ubq_npt.dcd` (+ topology, state log) | Same |
| Stability report | `../../output/mace_npt_stability_report.md` | Per-protein metrics table |

### Mandatory documentation

**Status report** (ALWAYS required — non-negotiable):
Write to `../../status/task-001-status.md` using `templates/status-report.md`.
Include actual GPU-hours, SU consumed, per-protein trajectory length, pass/fail
per protein, any failures + fallbacks applied.

**Experiment log** (required — multi-day computational experiment):
Write to `../../output/task-001-experiment.md` using `templates/experiment-log.md`.
Include all SLURM job IDs, restart counts per protein, throughput per protein
(actual ns/day), any anomalies (hangs, NaN, etc.).

**Cross-agent note** (required — affects D2 path + Sub 1.4 planning):
Write to `../../../../../shared/notes/1.2-mace-npt-stability.md` using
`templates/cross-agent-note.md`. Tag tracks: `alpha-m`. Urgency: `important`.
Include: per-protein stability summary, comparison to Sub 1.1 NVT crambin baseline,
any concerns for Sub 1.4 production scope, Phase 2 budget implications if MACE
NPT throughput differs significantly from extrapolated 0.85-2.11 ns/day range.

---

## Verification

Before declaring your task complete, verify each criterion:

1. [ ] `ls ../../output/trajectories/mace_npt/` shows 3 .dcd + 3 topology .pdb + 3 state .csv
2. [ ] For each .dcd: `python -c "import mdtraj; t=mdtraj.load('$file', top='$top'); print(t.n_frames)"` returns ≥4500
3. [ ] `grep -c "NaN\|nan" ../../output/trajectories/mace_npt/*_state.csv` returns 0
4. [ ] Stability report has all 3 proteins with T/P/density/RMSD within pass criteria
5. [ ] Cross-agent note exists with frontmatter
6. [ ] Status report written

---

## If Something Goes Wrong

1. **MACE NPT crashes (barostat instability):** Fall back to NVT (Sub 1.1 demonstrated stable). Re-run all 3 proteins as NVT. Document NPT failure in cross-agent note. Status: `partial-fallback-nvt`.

2. **MACE H200 OpenCL hangs persistently (3+ resumes for same protein):** Diagnose via state log (last good step before hang). Fall back to RTX 5000 Ada with reduced scope (1 Tier B × 5 ns). Status: `partial`.

3. **Specific protein fails repeatedly:** Drop that protein. Continue with others. Status: `partial`. HeadAI accepts (D2 G1 needs ≥3 in Sub 1.4, not in Sub 1.2).

4. **OpenCL platform regressed (<0.5 ns/day on H200):** Diagnose with crambin smoke test. If env regressed, reinstall env-mace from Phase 0 yml. If hardware/driver regressed, escalate as help-needed.

5. **All 3 proteins fail:** Status: `failed`. Help-needed doc with full diagnostics. MACE Phase 2 path at risk.

In all cases: write status report with status, document exactly what went wrong (error messages, log excerpts, partial trajectory lengths), document what was tried, identify what help is needed.
