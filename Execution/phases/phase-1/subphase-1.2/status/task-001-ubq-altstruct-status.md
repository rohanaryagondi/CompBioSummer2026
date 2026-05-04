---
agent: head-1.2
task: task-001 (mlff-mace-pilot, UBQ option-d alternate starting structure)
date: 2026-05-04T03:46:03Z
type: status-report
status: in-flight
slurm_job: 10622885
slurm_tag: q6uadt05
partition: scavenge_gpu
gres: gpu:h200:1
account: pi_mg269
qos: normal
priority_su_cost: 0  # scavenge_gpu (Standard Tier, free; preemptible)
---

# Task 001 — UBQ option (d): MACE NPT with alternate starting structure (1XQQ NMR)

## 1. Goal

Test the hypothesis that the UBQ MACE-OFF24 hybrid NPT failure (asymptotic NaN at
7-9.6 ps across dt=1.0/0.5/0.25 fs probes, see
`shared/help-needed/head-1.2-mace-ubq-non-generalization.md`) is driven by
**residual stress in the 1UBQ crystal starting structure**, not by a
size-dependent architectural pathology of MACE-OFF24 hybrid + MonteCarloBarostat
on a 17 K-atom solvated system.

If the alternate (NMR-derived) starting structure clears 50 ps (= the longest
prior crash horizon × ~5×, well into the regime where 1UBQ-seeded runs all NaN),
the failure mechanism is starting-structure-dependent and Sub 1.2 success
criterion #1 can be retained for UBQ via 1XQQ. If it ALSO NaNs at ~7-10 ps,
the failure is NPT/MCB architectural and Sub 1.2 falls back to option (b)
(NVT pivot for UBQ) or option (c) (NTL9 substitute).

The recipe is **LOCKED** (Round 3: sentinel-bond + protein HBonds + MCB
freq=25 always-on, dt=0.5 fs); the **only** variable is the starting PDB.

## 2. Alternate starting structure

**Choice:** PDB 1XQQ chain A model 1 (UBQ NMR ensemble, room temp/pressure).

- **PDB ID:** 1XQQ
- **Reference:** Lange et al. 2008 *Science* 320:1471-1475
  ("Recognition Dynamics Up to Microseconds Revealed from an RDC-Derived
  Ubiquitin Ensemble in Solution").
- **Why 1XQQ over 1G6J or AlphaFold:**
  - 1XQQ is a *high-quality solution-state* NMR ensemble (RDC-restrained;
    128 models). Model 1 is the centroid-like representative.
  - Avoids unphysical crystal contacts present in 1UBQ that can imprint
    subtle distortions on MACE force calls.
  - Preserves real conformational diversity baseline (rather than an
    AF prediction whose calibration vs. solution dynamics is unproven for
    this purpose).
  - 1G6J is similar (NMR, smaller ensemble) but 1XQQ's RDC restraints
    yield tighter solution-state geometry.
- **Source URL:** https://files.rcsb.org/download/1XQQ.pdb (RCSB PDB)
- **Local path:** `Execution/phases/phase-0/subphase-0.1/proteins/ubq_alt.pdb`
- **Preparation:**
  - Downloaded full 1XQQ.pdb (128 models, 158,316 lines).
  - Filtered to MODEL 1 only, chain A only, including all H atoms.
  - Preserved HEADER/TITLE/COMPND/SOURCE/KEYWDS/EXPDTA/AUTHOR/REVDAT/JRNL/REMARK/
    DBREF/SEQADV/SEQRES/HELIX/SHEET/LINK/SSBOND/CRYST1/ORIGX/SCALE/MTRIX/MASTER
    headers; one MODEL/ENDMDL pair retained.
  - Final file: 1,596 lines, 1,231 ATOM records (76 residues full UBQ,
    chain A, hydrogens included), 129,276 bytes.
- **Comparison vs. existing 1UBQ:**
  - 1UBQ (`ubq.pdb`): crystal structure, 602 atoms (heavy + crystal-resolved H),
    76 residues, no MODEL records, includes 58 crystallographic waters.
  - 1XQQ model 1 (`ubq_alt.pdb`): NMR model 1, 1,231 atoms (all H included),
    76 residues, chain A only, no crystal waters or contacts.
- PDBFixer + `MLPotential.createMixedSystem` downstream will solvate identically
  to the 1UBQ pipeline (PDB 1UBQ → SOLVATE 1.0 nm padding → 0.15 M NaCl →
  PDBFixer addHydrogens). Atom-count differences in the input file do not
  bias the production pipeline.

## 3. Code edits

| File | Change |
|------|--------|
| `output/scripts/mace_hybrid_npt_prod.py` line 135 area | Added `"ubq_alt"` entry to `PROTEIN_DEFAULTS` dict pointing at `proteins/ubq_alt.pdb` with pdb_id "1XQQ", chain A, no resrange. |
| `output/scripts/submit_mace_npt_prod.sh` lines 42, 53-60 | Added `ubq_alt` to argument validation, case statement (`RESRANGE=""`), and unknown-protein error message. |

**Round 3 recipe untouched.** dt=0.5 fs (matches the failed dt=0.5 fs UBQ run for
direct comparability), MCB freq=25 always-on, sentinel-bond, HBonds constraints.

## 4. SLURM submission

```
MACE_HYBRID_DT_FS=0.5 bash output/scripts/submit_mace_npt_prod.sh \
    ubq_alt q6uadt05 scavenge_gpu 0.05 5:55:00
```

| Parameter | Value |
|-----------|-------|
| Job ID | **10622885** |
| Cryptic tag | `q6uadt05` (q6 + uadt05 = "ubq alt dt05") |
| Partition | scavenge_gpu (preemptible; H200 node when backfilled) |
| GRES | gpu:h200:1 |
| Account / QOS | pi_mg269 / normal |
| Walltime | 5:55:00 (21300 s); walltime guard 19170 s (90%) |
| Target | 0.05 ns = 50 ps simulated time |
| dt | 0.5 fs (100,000 steps total) |
| Estimated walltime if no NaN | ~3-4 hours at H200 OpenCL throughput observed in Sub 1.1 (UBQ ~0.4-0.5 ns/day for full 17K-atom system at dt=1.0 fs; halving dt halves throughput → ~0.2-0.25 ns/day → 50 ps in ~5-6 h). Probe walltime sized to fit. |
| Cost | 0 priority SU (scavenge_gpu Standard Tier; **free** but preemptible). |

Job is currently PENDING on scavenge_gpu queue (None reason) as of 2026-05-04T03:46:03Z.

## 5. Verdict criteria

**SUCCESS (clear past 9.6 ps with PE/T/density stable):**
- Reaches step ≥20,000 (10 ps simulated) without NaN in PE, KE, T, V, or
  positions.
- T = 300 ± 15 K throughout; barostat-converged density physical (≈1.0 g/mL
  for solvated UBQ); pressure ≈ 1 atm (with MCB noise envelope).
- **If reaches 50 ps clean** (target_ns=0.05): hypothesis CONFIRMED — 1UBQ
  crystal residual stress was the failure driver. Plan a 5 ns production with
  `ubq_alt` on Standard Tier as the UBQ representative for criterion #1.
  Update `output/scripts/mace_hybrid_npt_prod.py` PROTEIN_DEFAULTS to make
  `ubq_alt` the canonical UBQ entry, or keep both and document.

**PARTIAL (clears prior 9.6 ps record but eventually NaN before 50 ps):**
- Hypothesis weakly supported. Document failure horizon and discuss with
  PlannerAI whether starting-structure variation alone is sufficient or
  whether a different protocol (e.g., gentler 50→300 K Berendsen ramp +
  larger box padding) is needed.

**FAILURE (NaN at ≤9.6 ps, matching 1UBQ pattern):**
- Hypothesis FALSIFIED — failure is architectural (NPT/MCB/system-size).
  Proceed immediately with option (b) NVT pivot for UBQ or option (c) NTL9
  substitute, per `shared/help-needed/head-1.2-mace-ubq-non-generalization.md`
  decision tree. Document this run as a clean falsification of the
  starting-structure hypothesis (valuable for OSF + manuscript).

## 6. Expected log signatures

- Output log: `output/slurm_logs/mace_npt_prod_ubq_alt_q6uadt05_10622885.out`
- Trajectory: `output/trajectories/mace_npt_prod/q6uadt05_npt.dcd`
- State CSV: `output/trajectories/mace_npt_prod/q6uadt05_npt_state.csv`
- Topology: `output/trajectories/mace_npt_prod/q6uadt05_topology.pdb`
- Meta: `output/trajectories/mace_npt_prod/q6uadt05_npt_meta.json`
- Checkpoint: `/nfs/roberts/scratch/pi_mg269/rag88/alpha-m/mace-npt-prod/q6uadt05/checkpoint_latest.chk`

## 7. Cross-references

- Help-needed (parent issue): `shared/help-needed/head-1.2-mace-ubq-non-generalization.md`
- Closure master plan: `shared/notes/1.2-closure-master-plan.md` §4 R3
- Round 3 recipe: `shared/notes/1.2-mace-npt-fixed.md`
- NVT fallback design: `output/npt_nvt_production_plan.md`
- Production driver: `output/scripts/mace_hybrid_npt_prod.py`

## 8. Operational

- Jobstats monitor: already armed (multiple SLURM jobs in queue from concurrent
  UBQ option-c NTL9 / GB1 work; this submission did not require additional
  arm).
- SU impact: 0 priority SU (scavenge_gpu free); 0 budget delta vs.
  `prio_su_budget.json`.
- Scavenge_gpu preemption risk: medium. If preempted, the production driver
  re-loads from `/nfs/roberts/scratch/.../q6uadt05/checkpoint_latest.chk` on
  resubmit (recipe-locked so no checkpoint-incompatibility risk). Resubmit
  command identical to above with the same tag `q6uadt05`.
- No GPU keepalive concerns (external-process keepalive already in submit
  wrapper).
