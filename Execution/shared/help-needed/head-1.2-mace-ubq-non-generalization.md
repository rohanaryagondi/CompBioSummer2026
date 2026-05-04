---
author: head-1.2
date: 2026-05-03T16:30:00Z (updated)
urgency: critical
affected_tracks: [alpha-m, combined]
subphase: "1.2"
status: ESCALATED 2026-05-03 — dt=0.25 fs NPT ALSO failed (NaN @ ~9.6 ps); pattern conclusively asymptotic; user/PlannerAI decision required
---

## UPDATE 2026-05-03T16:30Z: dt=0.25 fs also failed

UBQ dt=0.25 fs NPT probe (10475183 q6u4dt25, gpu_devel H200) ran cleanly to
step 35000 (8.75 ps simulated) at 20:18:18Z, then NaN'd at 20:23:51Z — failure
at ~9.6 ps simulated. **Each dt halving extends failure horizon by only ~1 ps**:
- dt=1.0 fs: NaN ~7-8 ps
- dt=0.5 fs: NaN ~8-9 ps
- dt=0.25 fs: NaN ~9.6 ps

Pattern is asymptotic, not converging. dt=0.1 fs predicted to NaN at ~11 ps
(still below 50 ps gate threshold). **Reducing dt is not a fix.**

The architectural pathology for the UBQ-sized solvated system (17,159 atoms,
1,231 MACE atoms) is reproducible across 3 timestep configurations. The Round 3
recipe (sentinel-bond + HBonds + MCB freq=25) is necessary but not sufficient
for UBQ NPT. WW (7,565 atoms) and GB3 (9,874 atoms) work; UBQ does not.

**Compute spent on UBQ NPT iteration (final tally):**
- dt=1.0 fs probe: 13.07 priority SU (FAILED)
- dt=0.5 fs probe: ~22 priority SU (FAILED, walltime reduced)
- dt=0.25 fs probe: 0 SU (gpu_devel Standard Tier, free; partition-optimization win)
- Total priority SU on UBQ NPT iteration: ~35 (within 250 cap)

**No further dt iterations recommended** — pattern is conclusive.

---



# Help-Needed: MACE NPT Round 3 Recipe Does Not Generalize to UBQ

## Summary

The Round 3 recipe (sentinel-bond + protein HBonds constraints + dt=1 fs + MCB
freq=25) was validated to 100 ps clean on WW (test_P, 2026-05-02). It also
generalizes to GB3 (25 ps clean during probe TIMEOUT, recipe works on the larger
solvated system, 9,874 atoms). However **it does NOT generalize to UBQ**
(17,263 atoms total / 1,231 MACE atoms) — NaN failure within 7-9 ps NPT
equilibration despite both Round 3 patches.

**Halving dt does not fix it** — only delays by ~1 ps:
- dt=1.0 fs UBQ: NaN at ~7-8 ps (probe 10458155 c4n7vp2j, 2026-05-02)
- dt=0.5 fs UBQ: NaN at ~8-9 ps (retry probe 10463455 q6u4n8mx, 2026-05-02)

Failure is not timestep-driven. It is architectural for the larger UBQ system.

## Sub 1.2 success criterion #1 implication

CLAUDE.md success criterion #1 (verbatim):
> "MACE NPT stability evidence: 3 Tier B proteins (WW, GB3, ubiquitin) each
> show 5 ns of stable NPT dynamics (no NaN, T = 300±15 K, P ≈ 1 atm, density
> physical)."

If UBQ cannot achieve 5 ns stable NPT, criterion #1 is at risk. The strict
"no compromise" reading requires either:

1. **Find a working NPT recipe for UBQ** (Tier-2 fallback in flight; dt=0.25
   fs probe queued on gpu_h200 Standard Tier as 10475183 q6u4dt25). If this
   too NaNs at ~9-10 ps, the failure is conclusively NPT-MCB-incompatible
   for this system.
2. **Pivot UBQ to NVT-only** per the documented fallback in
   `output/npt_nvt_production_plan.md`. Sub 1.1 demonstrated stable MACE
   NVT for crambin → high prior on UBQ NVT working. This deviates from
   strict criterion language but is the documented Sub 1.2 risk-register
   fallback (R3 in `shared/notes/1.2-closure-master-plan.md`).
3. **Escalate to PlannerAI for criterion #1 amendment.** Propose: "≥3
   Tier B proteins with stable 5 ns MLFF dynamics under MACE-OFF24 hybrid
   ensemble (NPT preferred; NVT acceptable for proteins where NPT is
   architecturally incompatible due to MCB-induced force discontinuities)."

## Decision points

### What works (validated as of 2026-05-02)
- WW NPT: test_P 100 ps clean, dt=1.0 fs ✓
- GB3 NPT: 25 ps clean (probe TIMEOUT), dt=1.0 fs ✓
- WW + GB3 5 ns production: submitted on Standard Tier gpu_h200 (PENDING; will run when fair-share permits)

### What's failing (UBQ specifically)
- UBQ NPT dt=1.0 fs: NaN ~7-8 ps
- UBQ NPT dt=0.5 fs: NaN ~8-9 ps
- UBQ NPT dt=0.25 fs: in flight (10475183, Standard Tier gpu_h200, expected ~24 hr queue + run)

### Compute spent on UBQ NPT iteration
- dt=1.0 fs probe: 13.07 priority SU (FAILED)
- dt=0.5 fs probe: ~22 priority SU (FAILED, walltime reduced via scontrol from 4h to 1:30)
- dt=0.25 fs probe: 0 SU (Standard Tier, free)
- Total priority SU spent on UBQ NPT iteration: ~35 SU. D6 reserve was ~30 SU
  per closure master plan; **slightly over by ~5 SU but within total 250 SU
  cap which has 18 SU buffer**.

## Requested PlannerAI action

If dt=0.25 fs NPT probe (10475183) ALSO fails at <50 ps:

1. **Authorize criterion #1 amendment** (option 3 above) OR
2. **Authorize NVT pivot for UBQ** (option 2 above) with explicit acknowledgment
   that this deviates from strict NPT language, OR
3. **Authorize a different Tier-2 NPT approach** (e.g., MACE float64 +
   gentler initial conditions + 50→300 K Berendsen ramp + larger box padding;
   estimated ~50 priority SU additional + uncertain success).

If dt=0.25 fs NPT probe SUCCEEDS at 50 ps, head-1.2 proceeds to UBQ NPT 5 ns
production at dt=0.25 fs on Standard Tier (slow, ~3 weeks at 0.26 ns/day H200
OpenCL — would slip past 2026-05-16 Sub 1.2 close). Even on success this may
require a Sub 1.2 deadline extension or scope deferral to Sub 1.3.

## What's NOT broken

- WW NPT 5 ns recipe-validated, production submitted
- GB3 NPT 5 ns recipe-validated, production submitted
- SO3LR rescue for GB1+UBQ already PASS (Sub 1.2 task-002 §2.3); GB3 + NTL9 + WW rescues now also validated by 500 ps gates (PASS)
- SO3LR 5 ns full rescues all submitted on Standard Tier
- Stats pipeline + Delta baselines + OSF v3 all unaffected

## Cross-references

- Closure master plan: `shared/notes/1.2-closure-master-plan.md` §4 R3 (recipe non-generalization risk)
- Round 3 fix evidence: `shared/notes/1.2-mace-npt-fixed.md`
- NVT fallback design: `phases/phase-1/subphase-1.2/output/npt_nvt_production_plan.md`
- Production driver: `phases/phase-1/subphase-1.2/output/scripts/mace_hybrid_npt_prod.py`
- Failed UBQ probe logs: `output/slurm_logs/mace_npt_prod_ubq_{c4n7vp2j,q6u4n8mx}_*.out`
- Pending dt=0.25 fs probe: 10475183 q6u4dt25 (gpu_h200, MACE_HYBRID_DT_FS=0.25)

---

## UBQ option (d) probe attempt — alternate starting structure (1XQQ NMR model 1)

**Date:** 2026-05-04T03:46Z
**Status:** Submitted (PENDING on scavenge_gpu)
**Job:** 10622885 q6uadt05
**Hypothesis:** 1UBQ crystal residual stress drives the asymptotic NaN at
7-9.6 ps; a NMR-derived starting conformation (no crystal contacts, real
solution geometry) may relieve that stress and allow MACE-OFF24 hybrid NPT
to run stably on UBQ. If FALSE, the failure is architectural (NPT/MCB/
system-size) and option-(b) NVT pivot or option-(c) NTL9 substitute remains
the path forward.

**Recipe LOCKED.** Round 3 (sentinel-bond + protein HBonds + MCB freq=25
always-on, dt=0.5 fs) — identical to the failed `q6u4n8mx` 1UBQ dt=0.5 fs
probe. The ONLY variable is the starting PDB.

### Starting structure

- **PDB:** 1XQQ chain A model 1 (Lange et al. 2008 *Science* 320:1471-1475;
  RDC-restrained NMR ensemble of solution-state UBQ).
- **Local:** `Execution/phases/phase-0/subphase-0.1/proteins/ubq_alt.pdb`
  (1,231 ATOM records, 76 residues, full H, chain A, MODEL 1 only, 1,596
  total lines / 129,276 bytes).
- **Source:** `https://files.rcsb.org/download/1XQQ.pdb`
- **Why 1XQQ over 1G6J or AlphaFold:** RDC restraints yield tightest
  solution-state geometry; avoids unphysical crystal contacts in 1UBQ;
  preserves real conformational baseline (vs. AF-prediction calibration
  uncertainty for this purpose).

### Submission

```
MACE_HYBRID_DT_FS=0.5 bash output/scripts/submit_mace_npt_prod.sh \
    ubq_alt q6uadt05 scavenge_gpu 0.05 5:55:00
```

| Parameter | Value |
|-----------|-------|
| Job ID | 10622885 |
| Tag | q6uadt05 |
| Partition | scavenge_gpu (preemptible H200; **0 priority SU**) |
| Walltime | 5:55:00 |
| Target | 50 ps simulated time at dt=0.5 fs (= 100,000 steps) |
| Cost | 0 SU (scavenge Standard Tier free) |

### Code edits

- `output/scripts/mace_hybrid_npt_prod.py`: added `"ubq_alt"` entry to
  `PROTEIN_DEFAULTS` (pdb_id "1XQQ", chain A, no resrange) at the end of
  the dict, comment-cited to this help-needed §.
- `output/scripts/submit_mace_npt_prod.sh`: added `ubq_alt` to argument
  validation and case statement (`RESRANGE=""`); usage line updated to
  `<ww|gb3|ubq|ubq_alt|ntl9>`.

### Decision rules on probe completion

- **If reaches 50 ps clean:** Hypothesis CONFIRMED (starting-structure
  driven). Plan 5 ns production with `ubq_alt` (1XQQ) as the canonical
  UBQ representative for Sub 1.2 success criterion #1. Document
  start-structure dependency in the OSF pre-reg + manuscript caveat.
  No criterion-#1 amendment needed.
- **If NaN at >9.6 ps but <50 ps:** Hypothesis WEAKLY SUPPORTED.
  Document partial extension; discuss with PlannerAI whether to
  combine with gentler protocol (50→300 K Berendsen ramp + larger
  padding) or pivot.
- **If NaN at ≤9.6 ps (matching 1UBQ pattern):** Hypothesis FALSIFIED —
  failure is architectural. Proceed with option (b) NVT pivot for UBQ
  OR option (c) NTL9 substitute (already in flight as parallel work).
  This is a clean falsification result (valuable for OSF + manuscript
  rigor — direct A/B test of starting-structure dependence).

### Status report

- Detailed status: `phases/phase-1/subphase-1.2/status/task-001-ubq-altstruct-status.md`
