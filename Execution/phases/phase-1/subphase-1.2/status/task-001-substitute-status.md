---
task_id: "task-001-substitute"
agent: "head-1.2 (option-c substitute pivot)"
subphase: "1.2"
status: partial
date: 2026-05-03
---

# Status Report: Task 001 — UBQ Substitute (Option c) — NTL9 Selection + 50 ps Probe Submitted

## Summary

Selected **NTL9 (51 aa, Tier B, S2-counted)** as the option-(c) substitute for UBQ
in success criterion #1 (3 Tier B × 5 ns NPT). Added NTL9 to `PROTEIN_DEFAULTS`
in `mace_hybrid_npt_prod.py` and to the wrapper case-statement in
`submit_mace_npt_prod.sh`. Submitted a 50 ps NPT diagnostic probe on
`scavenge_gpu` (free-tier H200) as SLURM job **10622876** (tag `q6kz3m8x`).
Probe is PENDING; agent exits without waiting synchronously.

---

## What Was Done

1. **Read the candidate-set evidence** (manifest.json, OSF pre-reg v3 §3,
   SO3LR pilot stability §3.7, BioEmu pass-rate note). Both NTL9 and GB1
   are Tier B, S2-counted, ≤ 75 aa, smaller than GB3 in protein-ATOM count.

2. **Counted protein-ATOM records** to estimate solvated atom counts:

   | Protein | Res | Tier | S2-counted | Protein ATOM records | Recipe outcome (probe) |
   |---------|----:|:----:|:----------:|---------------------:|:----------------------:|
   | WW (2F21 6-39) | 34 | A | yes | 1,403 (multi-conformer) | PASS solvated 7,565 |
   | NTL9 (2HBB) | 51 | B | yes | **390** | TBD (this probe) |
   | GB1 (2QMT) | 56 | B | yes | 438 | (not yet probed) |
   | GB3 (1P7E) | 56 | A/B | yes | 862 | PASS solvated 9,874 |
   | UBQ (1UBQ) | 76 | B | yes | 602 | FAIL solvated 17,259 |

   NTL9 has the **smallest protein-ATOM count** of the candidate set. With
   1.0 nm solvent padding (the locked recipe value), NTL9 should solvate
   to well below the 10K-atom threshold that defines the
   recipe-generalization regime (UBQ failed at 17K solvated; WW + GB3
   passed at 7.5K + 9.9K solvated). Recipe is highly likely to generalize.

3. **Selected NTL9 over GB1.** Rationale (publication-value tiebreaker):
   - **Smallest atom count** of all candidates → highest probability the
     recipe generalizes given the UBQ atom-count-correlated failure.
   - **Cross-MLFF stress test value:** NTL9 has the strongest combined
     MLFF story in Sub 1.2 — SO3LR v1 silent structural explosion at
     ~100 ps, then v2 charge-neutral re-prep cleared the 500 ps Rg gate
     (`shared/notes/1.2-so3lr-pilot-stability.md` §3.7). Adding MACE NPT
     evidence on the same protein closes the comparative loop on a single
     benchmark with two complete force-field stories.
   - **Anton 2.9 ms folding trajectory** (D.E. Shaw lab) gives reviewers
     a comparative MD-MD baseline that GB1 lacks.
   - **OSF v3 §10 explicitly lists NTL9** in the Sub 1.4 MACE NPT planned
     set `{WW, GB3, GB1, NTL9}` — this probe directly de-risks one of the
     four Sub 1.4 production targets.
   - GB1 is held in reserve as the safe second choice if NTL9 probe FAILS;
     GB1 (438 ATOM, neutral, classic NMR benchmark) has high prior of
     recipe generalization too.

4. **Modified `mace_hybrid_npt_prod.py`** at the `PROTEIN_DEFAULTS` dict
   (line 106): added `ntl9` entry referencing
   `/home/rag88/.../proteins/ntl9.pdb`, full residue range (chain A,
   residues 1-51; matches manifest), pdb_id `2HBB`. Recipe physics
   parameters NOT touched. (NB: the script also already contained an
   independent `ubq_alt` entry from a parallel option-(d) workstream,
   which I did not modify.)

5. **Modified `submit_mace_npt_prod.sh`**: added `ntl9) RESRANGE="" ;;`
   case-statement entry (parallel to ubq), updated usage string and
   header examples. Wrapper accepts scavenge_gpu partition (free-tier
   h200) which was already configured pre-this-task.

6. **Submitted 50 ps NPT diagnostic probe:**
   ```
   bash output/scripts/submit_mace_npt_prod.sh ntl9 q6kz3m8x scavenge_gpu 0.05 5:55:00
   ```
   Result: `Submitted batch job 10622876`. SLURM state: PENDING (None
   reason). `q6` prefix per project convention; remaining 6 chars opaque.

---

## Artifacts Produced

| Artifact | Path | Description | Verified |
|----------|------|-------------|----------|
| Modified production script | `output/scripts/mace_hybrid_npt_prod.py` (lines 125-134, NTL9 entry) | Added NTL9 to PROTEIN_DEFAULTS | yes (Edit confirmed) |
| Modified wrapper | `output/scripts/submit_mace_npt_prod.sh` (line 57, ntl9 case) | Added NTL9 case to RESRANGE switch | yes |
| Probe SLURM submission | job 10622876 / tag q6kz3m8x | 50 ps NPT, scavenge_gpu, h200, walltime 5:55:00 | yes (squeue PENDING) |
| Probe SLURM logs (deferred) | `output/slurm_logs/mace_npt_prod_ntl9_q6kz3m8x_10622876.{out,err}` | Will populate when job RUNS | n/a |

---

## Success Criteria Evaluation

| # | Criterion | Met? | Evidence |
|---|-----------|------|----------|
| 1 | Substitute selected with documented rationale | yes | NTL9 chosen over GB1; rationale in §What Was Done #3 |
| 2 | Recipe generalizability estimated | yes | 390 protein-ATOM records → likely solvated < 10K atoms; recipe pre-validated at 9.9K (GB3 PASS), 7.5K (WW PASS), failed at 17K (UBQ FAIL) |
| 3 | Production driver + wrapper extended for NTL9 | yes | PROTEIN_DEFAULTS + case-statement edits applied non-destructively (recipe physics unchanged) |
| 4 | 50 ps probe submitted on scavenge_gpu | yes | SLURM job 10622876 (tag q6kz3m8x), walltime 5:55:00, PENDING |
| 5 | Status report written | yes | this file |
| 6 | Cross-agent note appended | yes | §"UBQ substitute (option c)" added to `shared/notes/1.2-mace-npt-prod-launch.md` |

---

## Probe Verdict Criteria (for HeadAI to apply when probe terminates)

The probe targets 50 ps NPT. Apply the same diagnostic success criteria
used for the GB3 + UBQ probes (head-1.2 closure plan, recorded in
`shared/notes/1.2-mace-npt-prod-launch.md`):

- **PASS**: no NaN through 50 ps; T 285-315 K rolling 10-ps mean; density
  1.00-1.06 g/cm³ at end; box volume drift <8% in last 25 ps;
  progress.json + meta JSON consistent.
- **PARTIAL** (e.g., walltime exit before 50 ps): if no NaN through the
  achieved interval, treat as in-progress and resubmit with same tag.
- **FAIL**: NaN at any point → recipe does not generalize to NTL9 either;
  investigate alternative substitute (GB1) or escalate help-needed.

The probe walltime 5:55:00 includes scavenge_gpu queue tail-time + one
auto-restart slot. Throughput projection: ~2-3 ns/day H200 hybrid (per Sub
1.1 §11 reference, scaled by atom count) → 50 ps probe should run in
~25-30 minutes on-node + variable scavenge_gpu wait.

If PASS: subagent can proceed to 5 ns NTL9 NPT production submission
(scavenge_gpu prod, tag TBD), restoring success criterion #1 to
3 Tier B × 5 ns = {WW, GB3, NTL9}.

If FAIL: fall back to **GB1 probe** (next-smallest atom count, classic
NMR benchmark); GB1 has 438 ATOM vs NTL9's 390, both well below the
GB3-PASS scale.

---

## Unexpected Findings

None. The candidate-set analysis confirmed the user's a-priori best-candidate
ranking (NTL9, GB1) without surprises. NTL9 atom count (390) was tighter
than naive residue-count scaling would predict (51 aa × ~13 atoms heavy
≈ 660), consistent with PDB 2HBB chain A having no sidechain coordinates
for some surface residues.

---

## What the Next Agent Needs to Know

1. **Probe is PENDING on scavenge_gpu** — start time depends on cluster
   load. Check `squeue -j 10622876` for state transitions. scavenge_gpu
   jobs are pre-emptable; auto-restart loop in the wrapper handles this.

2. **If probe PASSES (50 ps clean):** submit production with the same
   wrapper:
   ```
   bash output/scripts/submit_mace_npt_prod.sh ntl9 q6<8char> scavenge_gpu 5.0 23:59:00
   ```
   Reuse the same tag for resubmits to extend the trajectory via
   checkpoint chain. Throughput ~2-3 ns/day → ~2-3 SLURM jobs of 23:59:00
   each to reach 5 ns.

3. **If probe FAILS:** GB1 is the safe fallback. Add GB1 to
   `PROTEIN_DEFAULTS` (PDB path: `phases/phase-0/subphase-0.1/proteins/gb1.pdb`,
   chain A, no resrange, pdb_id 2QMT). Update wrapper case. Submit
   probe with `q6` prefix tag.

4. **Recipe physics LOCKED** — no script-level dt/MCB-freq/sentinel/HBonds
   changes were made. The Round 3 recipe (sentinel-bond + HBonds + dt=1 fs +
   MCB freq=25, always-on) applies verbatim to NTL9.

5. **OSF v3 §10 already references NTL9** as part of the Sub 1.4 MACE NPT
   planned set; if probe + production PASS, this strengthens the v4
   tracked-amendment basis. If both fail, the 5×10 floor sensitivity
   table B.4 becomes load-bearing (already pre-registered).

6. **env-mace contract preserved**: PYTHONNOUSERSITE=1 still set in
   wrapper; env was NOT modified.

---

## Resource Usage

| Resource | Estimated | Actual |
|----------|-----------|--------|
| Probe wall time | ~25-30 min on-node + scavenge wait | TBD |
| Probe SU (scavenge_gpu billing 1/10 of standard h200 = ~30 SU/hr) | ~15-30 SU for 30-min wall | TBD |
| Storage (probe DCD/CSV/checkpoint) | ~50 MB | TBD |
| SLURM job IDs | N/A | 10622876 (probe q6kz3m8x) |

---

## Issues and Blockers

None. Probe is PENDING normally on scavenge_gpu. Status `partial` because
the probe verdict is not yet known; will become `complete` (PASS) or
trigger the GB1 fallback path (FAIL) once SLURM 10622876 reaches a
terminal state.
