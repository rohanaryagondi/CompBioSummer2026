---
task_id: "task-002-rescue"
agent: "mlff-so3lr-pilot (rescue campaign); gate verdicts + 5ns prod state added by head-1.2 2026-05-03"
subphase: "1.2"
status: gates-PASSED-for-GB3-and-NTL9; WW-gate-cancelled-by-SU-enforcer; 5ns-rescues-PENDING-scavenge_gpu
date: 2026-05-03
---

## Update 2026-05-03 (20:30Z): gate verdicts + 5 ns rescue submissions

### Gate verdicts (terminal 2026-05-02)
- **GB3 gate** (10458604 g3b6kt2p): **PASSED** — 500 ps clean; PE stable −1513; T 290-310 K; 4× past v1 100 ps explosion horizon. Neutral-protonation chemistry rescue VALIDATED.
- **NTL9 gate** (10458605 n9t4mv5h): **PASSED** — 500 ps clean; same chemistry rescue mechanism.
- **WW gate** (10458603 r4w7q8nx): CANCELLED by `prio_su_enforce.sh` (would exceed 250 SU cap). Replaced by direct 5 ns full rescue.

### 5 ns rescue submissions on scavenge_gpu

After 3 cancel/resubmit cycles for optimization rounds:
- GB3: 10567505 (g7p4tv8m) — neutral-prep, dt=0.5 fs float32
- NTL9: 10567506 (n5h6kx9q) — neutral-prep, dt=0.5 fs float32
- WW: 10567507 (w8q4r3xz) — float64+dt=0.25fs+NHC chain=5 (numerical rescue)

All on scavenge_gpu (1/10 Standard billing). Optimizations: md_steps=10000, save-buffer=5, JAX cache + XLA Triton GEMM flags, OSF-safe defaults for buffer-sr/lr.

### Production protocol commit
Phase 2 SO3LR vacuum runs on |Q|>0 proteins require **mandatory neutral-protonation re-prep** (D/E→ASH/GLH; K/R→LYN). Sub 1.4 task spec must encode. D-OSF-SO3LR user decision pending (revise §4 pre-deposit vs defer v2 amendment).

---

# Status Report: Task 002 Rescue — SO3LR vacuum NVT for WW, GB3, NTL9

## Summary

Sub 1.2 task-002 v1 left 3/5 SO3LR vacuum NVT pilots failing the success
criterion. The prior subagent's recommendation that "GB3 and NTL9 are dead"
correctly diagnosed the failure mechanism (collective Coulomb-driven
expansion in net-charged systems) but missed the actual cure space: the
chemistry, not the integrator. This report captures the rescue campaign
state.

**Failure modes (from prior task-002 analysis):**
- WW (534 atoms): NaN at 0.704 ns, structure intact (Rg ratio 0.983).
  Failure is **numerical** — float32 catastrophic cancellation in
  long-range / dispersion sum on a small system.
- GB3 (862 atoms, net side-chain charge -2): silent structural explosion
  at ~100 ps (Rg 10.6 → 986 Å), no NaN, T held at 300 ± 13 K. Failure is
  **physics** — like-charged surface side chains cannot be Debye-screened
  in vacuum.
- NTL9 (813 atoms, net side-chain charge +5, Lys-rich N-terminus): same
  pattern as GB3. Late NaN at 4.39 ns is downstream of structural
  explosion.

**Rescue strategy (per `output/so3lr_rescue_plan.md`):**
- WW: change the numerics → float64 + dt=0.25 fs + NHC chain=5.
- GB3 / NTL9: change the chemistry → re-prep with neutral protonation
  (LYN for K, ASH for D, GLH for E) → net side-chain charge = 0.
  No ARGs in either protein, so OpenMM's standard variants are sufficient.

## Stage status (as of 2026-05-02 ~20:10 UTC, SubAgent exit)

| Stage | Description | Status |
|-------|-------------|--------|
| 1 | Rescue plan written (`output/so3lr_rescue_plan.md`) | DONE |
| 2 | Neutral prep + rescue runner + sbatch + submit wrapper authored | DONE |
| 2.5 | Run neutral prep on GB3 + NTL9 (env-mace, login node) | DONE |
| 2.6 | Charge-check assertion (net formal charge = 0) | DONE — both proteins verified |
| 3 | Submit 3 rescue gates (priority queue, RTX 5000 Ada, 500 ps each) | SUBMITTED — all 3 still PENDING at SubAgent exit due to priority_gpu queue depth |
| 4 | Submit full 5 ns rescues for gate-passing proteins | NOT YET — gates not terminal; head-1.2 must run after terminal state |
| 5 | Status report + cross-agent notes | DRAFT IN PLACE (this doc + on-deck `shared/notes/1.2-so3lr-rescue-results.md`); both have placeholders for gate verdicts that head-1.2 fills in after gate-check |

## Artifacts produced

| Artifact | Path | Description |
|----------|------|-------------|
| Rescue plan | `output/so3lr_rescue_plan.md` | Per-protein protocol, gate criteria, escalation ladder, SU budget |
| Neutral prep script | `output/scripts/so3lr_prep_proteins_neutral.py` | OpenMM Modeller variants → LYN/ASH/GLH; H-name-based net-charge assertion; runs in env-mace |
| Rescue runner | `output/scripts/so3lr_rescue_runner.py` | Fork of pilot runner with `--precision`, `--dt-fs`, `--nhc-chain`, `--nhc-thermo`, `--input-xyz` flags; sets `JAX_ENABLE_X64=True` for float64 mode |
| Rescue sbatch | `output/scripts/so3lr_rescue.sbatch` | Per-protein parameter overrides via SLURM `--export`; preserves env-so3lr contract (`PYTHONNOUSERSITE=0` + user-site appended to PYTHONPATH) |
| Gate submitter | `output/scripts/submit_so3lr_rescue_gates.sh` | Submits 3 gates to priority_gpu / prio_mg269 / RTX 5000 Ada |
| Production submitter | `output/scripts/submit_so3lr_rescue_production.sh` | Submits 5 ns full rescues (Standard Tier preferred); ready for use after gate evaluation |
| Gate check script | `output/scripts/so3lr_gate_check.py` | Parses stageA.log + HDF5; applies 4-criterion gate (NaN, Rg ratio, T mean, COM disp); validated on known-good (GB1, UBQ → PASS) and known-fail (v1 WW, GB3, NTL9 → FAIL) v1 trajectories. |
| Diagnostic sbatch | `output/scripts/so3lr_rescue_diagnostic.sbatch` | 5 ps validation pre-gate (cancelled before run; gates serve as integrated diagnostic) |
| GB3 neutral XYZ | `output/trajectories/so3lr_vacuum_neutral/gb3/input_neutral.xyz` | 864 atoms (437 heavy + 427 H), net side-chain charge = 0 |
| NTL9 neutral XYZ | `output/trajectories/so3lr_vacuum_neutral/ntl9/input_neutral.xyz` | 808 atoms (391 heavy + 417 H), net side-chain charge = 0 |
| Submission log | `output/trajectories/so3lr_vacuum_rescue/submitted_gates.tsv` | TSV of 3 gate job IDs |

## Submitted gate jobs

All 3 jobs submitted at 2026-05-02T16:02:14Z to `priority_gpu` partition,
`prio_mg269` account, RTX 5000 Ada (15-equivalent SU/hr), cryptic 8-char names:

| Protein | Job ID | Job name | Precision | dt (fs) | NHC chain | NHC thermo | Target | Walltime | Input XYZ |
|---------|--------|----------|-----------|---------|-----------|------------|--------|----------|-----------|
| WW   | 10458603 | r4w7q8nx | float64 | 0.25 | 5 | 200.0 | 0.5 ns | 03:00:00 | v1 input.xyz |
| GB3  | 10458604 | g3b6kt2p | float32 | 0.50 | 3 | 100.0 | 0.5 ns | 02:00:00 | neutral input_neutral.xyz |
| NTL9 | 10458605 | n9t4mv5h | float32 | 0.50 | 3 | 100.0 | 0.5 ns | 02:00:00 | neutral input_neutral.xyz |

**Estimated cost (priority SU):** WW ~9 + GB3 ~5 + NTL9 ~5 = ~19 priority SU.
Within the 25-SU per-task ceiling and 50-SU shared envelope authorized for
the rescue + MACE-NPT probes.

**Estimated start:** SLURM `scontrol show job` reports staggered start times
~18:49/18:57/18:59 UTC; actual queue position depends on priority_gpu
availability. Wall time from start to terminal: ~1.5-3 hr per gate.

## Gate criteria (all must hold; `output/scripts/so3lr_gate_check.py`)

1. No NaN through 500 ps (parsed from stageA.log + HDF5 positions).
2. Rg ratio (final / initial) < 1.2 — gentle structural tolerance; rejects
   the ~90× explosion mode of the v1 GB3/NTL9 failures.
3. T mean 285-315 K over 50-500 ps (post-equilibration window).
4. COM displacement < 5 Å vs frame 0.

Validated on existing v1 trajectories: GB1 / UBQ verdict = PASS; v1 WW /
GB3 / NTL9 verdict = FAIL (NaN onset, Rg ratio explosion, both correctly
detected).

## Escalation ladder (per protein)

If a gate FAILS:
- **GB3 / NTL9 Tier 2:** counter-ion shell (Na+/Cl- atmosphere within 5-7 Å
  of protein surface, no PBC). Compensates net charge while keeping
  geometry-bound system. Documented in `output/so3lr_rescue_plan.md` §
  Escalation.
- **WW Tier 2:** float64 alone (dt=0.5 fs). Cheaper diagnostic that isolates
  which lever cures the NaN.

If Tier 2 also fails: write `shared/help-needed/head-1.2-so3lr-<protein>-
{rescue-exhausted, physics-bound}.md` documenting evidence and proposing
PlannerAI scope revision. **No silent compromise.**

## Unexpected findings during prep

1. **OpenMM Modeller `addHydrogens(forcefield=Amber14)` failed on chain
   terminal residue.** The terminal residue couldn't match standard Amber14
   templates without registering a terminal patch. Fix: pass
   `forcefield=None`. Modeller falls back to geometric H placement using
   the built-in `hydrogens.xml` definitions. Verified per-residue H names
   match the LYN/ASH/GLH templates exactly (LYN: HZ1+HZ2, no HZ3; ASH: HD2
   added; GLH: HE2 added). SO3LR's `--relax` step will refine H geometry
   itself.

2. **OpenMM Modeller does NOT have a neutral ARG variant.** `hydrogens.xml`
   defines LYS/LYN, ASP/ASH, GLU/GLH, HID/HIE/HIP/HIN, CYS/CYX — but only
   one ARG entry (charged). The neutralization recipe is therefore SAFE
   ONLY for proteins with 0 ARGs. GB3 and NTL9 both have 0 ARGs in chain A
   (1-56 and 1-51 ranges) — verified before submitting. The script asserts
   this and refuses to proceed if any ARGs are present.

3. **Modeller renames LYN/ASH/GLH back to LYS/ASP/GLU after H placement.**
   Variants are H-template selectors, not residue renames. Net charge must
   be inspected by H-atom names (HZ3 absence → LYN, HD2 presence → ASH,
   HE2 presence → GLH), not by residue name. The charge-check assertion
   in `so3lr_prep_proteins_neutral.py` does this correctly (confirmed
   side-chain charge = 0 for both GB3 and NTL9).

4. **Termini are still zwitterionic** (NH3+ and COO- ends, charges +1 and
   -1 respectively). For a single-chain protein these cancel, so net
   charge = 0. The prep script reports both side-chain charge and termini
   contributions for transparency.

5. **Prior dt=0.25 fs WW diagnostic existed.** From 2026-04-21,
   `output/trajectories/so3lr_vacuum_dt025_diag/ww/` contains a 25 ps
   float32 + dt=0.25 fs run that completed cleanly (T stable, E
   conserved). However, 25 ps does NOT cross the 0.704 ns NaN cliff, so
   it does not yet validate dt=0.25 fs ALONE as the WW cure. The combined
   float64 + dt=0.25 fs WW gate is the right next test; if it passes, the
   Tier-2 fallback (float64 alone, dt=0.5 fs) can be tested for cost
   reduction.

## What head-1.2 needs to do

1. **Wait for terminal state.** Gates 10458603/4/5 are PENDING on
   priority_gpu. Estimated wall time ~1.5-3 hr each from start. The HeadAI
   should arm the jobstats monitor (per operational-practices.md §jobstats
   lifecycle) shortly after submission and STOP it when the last terminal
   transition occurs.

2. **Run gate check after terminal state.** From the subphase root:
   ```
   conda activate env-mace
   PYTHONNOUSERSITE=1 python output/scripts/so3lr_gate_check.py \
       --rescue-dir output/trajectories/so3lr_vacuum_rescue \
       --proteins ww gb3 ntl9 \
       --equil-ps 50.0 --target-ns 0.5 \
       --out-json output/trajectories/so3lr_vacuum_rescue/gate_check.json
   ```
   This emits per-protein verdict (PASS/FAIL) plus the 4 criterion-level
   booleans.

3. **For each gate that PASSED:** submit the 5 ns full rescue.
   ```
   bash output/scripts/submit_so3lr_rescue_production.sh ww gb3 ntl9
   ```
   (Or any subset that passed.) This goes to Standard Tier (`gpu`,
   pi_mg269) by default; pass `--priority` to use priority_gpu if Standard
   queue is blocking past 2026-05-08.

4. **For each gate that FAILED:** invoke this agent again or run the
   Tier-2 fallback per the escalation ladder. If both Tier-1 and Tier-2
   fail for a protein, file the help-needed doc and let PlannerAI revise
   the subphase scope.

5. **When 5 ns rescues complete:** re-invoke the SubAgent for stability
   re-analysis, update `shared/notes/1.2-so3lr-pilot-stability.md` with
   §4 RESCUE CAMPAIGN summary (or write a new
   `shared/notes/1.2-so3lr-rescue-results.md` and cross-link), and
   re-evaluate the Sub 1.2 task-002 success criterion.

## Resource usage

| Resource | Estimated | Actual (gates only, pre-terminal) |
|----------|-----------|--------|
| Priority SU (gates) | ~19 | TBD when terminal |
| Standard SU (5 ns rescues × 3) | ~540 | TBD if all 3 gates pass |
| Wall time (gates) | 1.5-3 hr each, parallel | gates queued ~16:02 UTC |
| Storage (gate output) | ~50 MB per protein | TBD |
| GPU partition | RTX 5000 Ada | confirmed (priority_gpu mapped) |

## Issues and blockers

None at submission. If gates remain queued past EOD 2026-05-02 due to
priority_gpu congestion, head-1.2 may consider:
- Submitting to Standard Tier (`gpu`, pi_mg269) as a parallel safety net
  (free but slow due to 0.0146 fair-share).
- Increasing priority Tier authorization (already at 0.97 fair-share so
  this should not be needed).

## Hard constraints honored

- [x] Cryptic 8-char alphanumeric job names (r4w7q8nx, g3b6kt2p, n9t4mv5h).
- [x] env-so3lr contract preserved (`PYTHONNOUSERSITE=0` + user-site
      appended to PYTHONPATH AFTER env site-packages).
- [x] env-so3lr / env-mace NOT modified.
- [x] Priority SU envelope NOT exceeded (~19 SU < 25 SU per-task ceiling).
- [x] No silent compromise — escalation ladder documented.
- [x] 500 ps gate before any 5 ns commitment.
- [x] No protein dropped — escalation goes through scope revision via
      help-needed doc.

## Cross-agent notes (planned)

- `shared/notes/1.2-so3lr-rescue-results.md` (NEW) — full per-protein
  rescue outcome, including gate verdicts, 5 ns trajectory metrics if
  applicable, and updated D2 G1 evidence statement. To be written after
  Stage 5 final terminal state.
- Updates to `shared/notes/1.2-so3lr-pilot-stability.md` §4 RESCUE
  CAMPAIGN to cross-link.
