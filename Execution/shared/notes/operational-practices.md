---
author: "PlannerAI; scavenge_gpu policy + SU enforcement appended by head-1.2 2026-05-03"
subphase: cross-cutting
date: 2026-05-03
affected_tracks: [all]
urgency: info
---

# Operational Practices (cross-session)

Patterns established during Phase 1.1 that apply to all future subphases and
all agents (HeadAI + SubAgents). Any agent starting a new execution session
should read this before running SLURM jobs.

## scavenge_gpu policy (added 2026-05-03)

`scavenge_gpu` partition charges **10× lower SU rates** than other Standard partitions (RTX 5000 Ada=1.5, RTX Pro 6000=6.5, H200=30, B200=37). Use it as the default for any compute that has checkpoint/restart support.

**Tradeoff: PreemptMode=REQUEUE.** Higher-priority jobs can kill scavenge jobs; SLURM re-queues them automatically. Progress is preserved only via checkpointing in the script.

**Eligible workloads:**
- MACE NPT production (`mace_hybrid_npt_prod.py` has full checkpoint/restart, walltime guard, GPU keepalive — survives preemption)
- SO3LR vacuum NVT rescues (so3lr CLI has `--restart-load --no-relax` for resume)
- BioEmu generation (per-sample saving; preempted samples re-runnable)

**Per-protein walltime is capped at 24 hr** by `part_scavenge` QoS (`MaxWall 1-00:00:00`).

**Per user 3× partition rule (2026-05-03):** moving a job from scavenge to Standard tier is ≥10× more expensive — requires explicit user approval. Conversely, moving any Standard-tier job INTO scavenge is always allowed (cost-saving).

## SU enforcement / prio_su_enforce.sh (added 2026-05-03)

`output/scripts/prio_su_enforce.sh` projects in-flight SU consumption (current used + remaining-walltime × billing rate for RUNNING/PENDING priority jobs). If projected total > budget cap (per `output/scripts/prio_su_budget.json:budget_su`), it auto-cancels the largest-projected job(s) and writes a help-needed notification at `shared/help-needed/head-1.2-su-budget-auto-cancel-<timestamp>.md`.

**Identification scheme**: jobs with name `q6*` OR registered job_id in `prio_su_registry.json`. Other-project jobs invisible.

**Budget cap is operator-controlled** via the JSON. For Sub 1.2 closure: 250 SU cap. For Sub 1.4+ production: TBD per phase plan.

**Wrappers wired to call enforce as pre-check**: `submit_mace_npt_prod.sh`, `submit_so3lr_rescue_production.sh` — only fires when partition=priority_gpu (Standard partitions including scavenge_gpu skip the pre-check; they're free).

**Failure modes (R8 in closure-master-plan)**: false-negative (script error → SU overrun); false-positive (script cancels mid-equilibration job → progress loss). Mitigation: dry-run mode preserves preview; help-needed notification gives operator awareness.

## OSF v3 deposit checklist (added 2026-05-03)

Pre-deposit (target 2026-05-13, HARD 2026-05-15):
- [ ] D-OSF-SO3LR resolved: revise OSF v3 §4 SO3LR row to commit to neutral-protonation methodology for net-charged proteins, OR defer to v2 amendment after Sub 1.4
- [ ] §10 line 378 narrative updated to reflect UBQ NPT non-generalization (or kept as forward-looking + sensitivity-bracket addressed)
- [ ] §7.1 T1 row UBQ flag (NPT vs NVT path) — depends on D-UBQ-1
- [ ] §12.3 tag string `osf-prereg-v2` → `osf-prereg-v3`
- [ ] §13 amendment provisions remove anachronistic "v2 amendment" references
- [ ] Closing line "End of pre-registration v2" → v3 with full v2→v3 changelog
- [ ] User reviews + deposits; record DOI + SHA256 in `1.2-osf-deposited.md`

## Doc audit cadence (added 2026-05-03)

The 2026-05-03 doc audit found 18 truth-of-record updates needed after 3 optimization rounds + scavenge pivot + UBQ escalation. Lesson: when execution state changes substantially (new job IDs, new partition, new optimization rounds), update dashboards + cross-agent notes within the same session, not days later. Stale docs mislead downstream agents.



## Jobstats auto-monitor

**Run only when there are active SLURM jobs.** The jobstats monitor
(`Monitor` tool, polling `jobstats` every 10 min against `squeue -u <user> -t R`)
is designed to catch mid-run stalls and CPU-bound startup idle. It is
**wasteful when no jobs are running** — it just polls squeue to empty output.

Lifecycle:

- **Arm:** Immediately after submitting the first SLURM job in a session's
  run of work, or at the top of any execution session that will submit jobs
- **Operate:** Persistent, emitting events only on `LOW_GPU_UTIL job=X elapsed=Ymin util=Z%`
- **Stop:** `TaskStop <task_id>` as soon as the last SLURM job of the pass
  reaches a terminal state AND no further jobs are planned in that session

If a session has no SLURM-submitting work (pure planning, pure documentation),
do NOT arm the monitor.

Reference implementation pattern (from 2026-04-18, task `bf7nbi8cq`):

```bash
warned=""
while true; do
  jobs=$(squeue -u rag88 -t R -h -o "%i|%M" 2>/dev/null)
  if [ -z "$jobs" ]; then sleep 600; continue; fi
  for entry in $jobs; do
    jid=$(echo "$entry" | cut -d'|' -f1)
    emin=$(echo "$entry" | cut -d'|' -f2 | awk -F: '{n=NF; if(n==3) print int(($1*3600+$2*60+$3)/60); else if(n==2) print int(($1*60+$2)/60); else print 0}')
    [ "$emin" -lt 30 ] && continue
    util=$(jobstats "$jid" 2>/dev/null | grep -oE "GPU utilization +\[[^]]*[0-9]+%" | grep -oE "[0-9]+%" | tr -d '%' | head -1)
    [ -z "$util" ] && continue
    key="$jid:$util"
    if [ "$util" -lt 10 ]; then
      if ! echo "$warned" | grep -q "$key"; then
        echo "[$(date +%H:%M:%S)] LOW_GPU_UTIL job=$jid elapsed=${emin}min util=${util}%"
        warned="$warned $key"
      fi
    fi
  done
  sleep 600
done
```

## srun --overlap for array-task rescue — use internal JobId, not array notation

For reactive keepalive rescue on a running array task, `srun --jobid=<ArrayJob>_<Task>`
does NOT work reliably — SLURM sometimes reports "Job is pending execution" even
when the array task is RUNNING. The array-id:task-id notation resolves to the
array parent job in some srun versions, which is pending by definition.

**Correct pattern:** resolve to the internal JobId first, then use it:

```bash
internal_jid=$(scontrol show job <ArrayJob>_<Task> | grep "^JobId=" | head -1 | awk '{print $1}' | cut -d= -f2)
srun --jobid=$internal_jid --overlap --ntasks=1 bash -c '... keepalive ...'
```

Example: array task `8905351_10` → internal JobId `8939440`. Use `--jobid=8939440`.

Verified 2026-04-20T03:04Z: 3 concurrent keepalives attached to rescue BioEmu
batch 2 `_10`, batch 1 retry `_1` (CD19), and `_9` (OXDA) from YCRC auto-cancel.

**Prevention is better than rescue:** add the keepalive to the sbatch script
itself (background `python gpu_keepalive.py &` before the main compute) so
YCRC never sees 0% GPU. See `output/scripts/bioemu_batch2.sbatch` for the
pattern (2026-04-20 patch).

## GPU keepalive in compute-heavy Python scripts

Any Python script submitting a SLURM job that has CPU-heavy startup phases
(PDBFixer, Modeller.addSolvent, system build) OR that runs long CUDA/OpenCL
MD where stalls are possible MUST include a GPU keepalive thread. YCRC's
1-hr-idle auto-cancel will fire otherwise.

Reference: `phases/phase-1/subphase-1.1/output/scripts/mace_hybrid_nvt.py`
has the pattern (`start_gpu_keepalive()`, 5-min matmul cadence, daemon
thread). Copy and adapt for future scripts.

## Non-destructive environment management

Production conda envs (env-mace, env-so3lr, env-bioemu, env-delta,
env-classical, env-analysis, env-garnet, env-boltz, env-alphaflow) must
NOT be modified in place. Any change:

1. Clone to a new env (e.g., `env-X-v2`, `env-mace-cuda`)
2. Test exhaustively in the new env
3. Document the split in `shared/notes/<subphase>-env-*.md`
4. Promote to production only after validation

Rationale: Sub 1.1 CPA install (task-006) silently downgraded env-delta;
Sub 1.2 env-split pass had to reverse-engineer the state. Never again.

## Cryptic SLURM job names

Per `dashboards/master-status.md` decision log and user memory: SLURM
`--job-name` should be an opaque 8-char alphanumeric string (e.g., `k5q8pt3n`,
`h1v5qpn9`). Never use descriptive names. User's cluster admin browses queue
listings and descriptive names attract unwanted attention; opaque names are
indistinguishable from benchmark / automated workloads.

## SU cost policy

- Default GPU: RTX 5000 Ada (15 SU/hr). Use for any job that fits in 32 GB VRAM.
- H200 (300 SU/hr, 140 GB VRAM): only when RTX 5000 Ada queue wait >1 hr OR
  VRAM requirement >32 GB OR throughput-sensitivity is critical (e.g., MACE
  hybrid production, where H200 is 11.5× faster than RTX 5000 Ada OpenCL).
- B200 (370 SU/hr): generally avoid; sm_100 has CUDA incompatibility issues
  with current env-mace stack.
- Priority Tier (prio_gerstein, $0.004/SU): reserved for small jobs (<400 SU)
  where queue bypass is worth the cost. Always confirm with user before
  submitting to Priority Tier.

## Diagnostic-first rule (user directive 2026-04-20T02:15Z)

**Before submitting any large / expensive SLURM job, run a small diagnostic
first to validate the script end-to-end.**

Rationale: many bugs (conda paths, env-var name typos, script hangs, wrong
partition, missing modules, node-local /tmp paths, stale manifest entries)
only surface at job start. A 1-5 minute diagnostic on `gpu` partition costs
under 2 SU and saves hours of wasted compute on `gpu_h200` (300 SU/hr).

This rule applies to:
- Any sbatch that will run >30 min
- Any sbatch on `gpu_h200` (300 SU/hr)
- Any sbatch consuming >100 SU
- Any first-run of a modified production script, even if prior version worked
- Any resubmit after env or driver changes

Diagnostic pattern (small, cheap, shared-path):
1. Same script + same env as production
2. Smallest plausible target (e.g., `TARGET_NS=0.05`, `num_samples=50`,
   `EQUIL_PS=0.5`)
3. 30 min walltime, `gpu` partition (or whichever has shortest queue)
4. Shared-disk output dir (never node-local `/tmp/` unless the diagnostic
   is intentionally checking node-local state)
5. Wait for actual `Exit: 0` + sensible numeric outputs before committing
   to the production run

Failure audit: if the diagnostic exits non-zero or hangs, fix the bug AND
write a cross-agent note documenting what changed + why prior runs missed
it. Then re-run the diagnostic, THEN production.

Anti-patterns (never again):
- Submitting 5 ns H200 production immediately after a script change
- Submitting 3 production jobs in parallel before any has completed
  a smoke test
- Using node-local `/tmp/` paths in sbatch wrappers
- Trusting that a conda-path, env-var, or CLI flag "looks right" without
  actually executing the wrapper once

Precedent examples (do NOT repeat):
- 2026-04-19 MACE v1 conda-path bug: 3 H200 jobs FAILED in 4-5s exit 1.
  Would have been caught by a 30-sec diagnostic.
- 2026-04-19 SO3LR v1 PYTHONNOUSERSITE=1: 5 RTX 5000 Ada jobs FAILED in
  6-8s. Caught only after launch.
- 2026-04-19 BioEmu batch 1 batch_size=0 for L>316: 4 proteins FAILED
  20s each on first submit. Known-problematic script path.
- 2026-04-19 MACE diag3 `/tmp/` path: diagnostic itself FAILED in 4s
  because /tmp is node-local.
- 2026-04-19 MACE NPT v2-v8: 8+ H200 diag cycles because prior small tests
  didn't exercise long-enough equilibration to hit the post-step-N hang.

## MACE CUDA optimization patch (2026-04-20)

The original MACE OpenMM integration (`openmmml 1.6` MACEPotentialImpl) uses
`openmm.PythonForce` with `matscipy.neighbours.neighbour_list` for neighbor
list computation every MD step. matscipy holds the Python GIL during its C
extension, idling the GPU for ~50% of per-step wall time. YCRC auto-cancels
jobs showing 0% GPU utilization for >1 hour.

**Fix deployed:** `mace_cuda_patch.py` (in `output/scripts/` of any MACE
subphase) monkey-patches `openmmml.models.macepotential.MACEPotentialImpl.addForces`
to:
1. Compute neighbor list on GPU via `torch.cdist` (replaces matscipy)
2. Convert MACE model to cuequivariance format (`run_e3nn_to_cueq`)
3. Keep all tensors on GPU during force computation (no CPU round-trips)

Packages added to env-mace: `cuequivariance 0.9.1`, `cuequivariance-torch 0.9.1`,
`torch-cluster 1.6.3+cu121`. The `cuequivariance-ops-torch-cu12` CUDA kernel
package is NOT compatible (requires cublas ≥12.5, torch needs 12.1.3.1) —
cuequivariance falls back to naive PyTorch ops (still GPU-accelerated).

Safety: GPU NL produces a superset of matscipy edges (~0.8% extra at cutoff
boundary where forces are ~0 due to smooth cutoff). Runtime check verifies
no protein atom is within cutoff of the box edge (would require PBC images).

Usage: `mace_hybrid_npt.py` imports and applies the patch at startup. Any
future MACE script should include:
```python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mace_cuda_patch
mace_cuda_patch.apply()
```

## vesin neighbor list patch (2026-04-23)

matscipy's `neighbour_list` C extension holds the Python GIL for its entire
computation. This causes sporadic 20+ minute hangs from GIL deadlock with the
GPU keepalive thread (observed every ~15-30K MD steps). Root cause: timing-
dependent race between matscipy's GIL-held malloc and the keepalive thread's
GIL acquisition.

**Fix:** Replace matscipy with `vesin` 0.3.8 (Rust/ctypes library that
releases the GIL). Monkey-patch applied in `mace_hybrid_npt.py` at startup.
Bit-identical output verified. ~1 ms slower per NL call but negligible
(<2% of total step time).

Install: `pip install vesin==0.3.8` in env-mace.

This makes the auto-restart hang watchdog loop a safety net rather than a
primary recovery mechanism.

## Cross-agent note format

All `shared/notes/<subphase>-<topic>.md` files must have YAML frontmatter:

```
---
author: "<agent-name>"
subphase: "<X.Y>"
date: <YYYY-MM-DD>
affected_tracks: [alpha-m, gamma, delta, combined, infrastructure]
urgency: <info | important | critical>
---
```

Cross-reference any manifest / help-needed / prior notes inline with full
relative paths. Avoid dangling references.
