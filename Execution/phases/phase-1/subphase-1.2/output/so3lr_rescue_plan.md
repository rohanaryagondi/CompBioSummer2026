---
author: "mlff-so3lr-pilot (rescue campaign)"
subphase: "1.2"
date: 2026-05-02
type: rescue-plan
affected_tracks: [alpha-m]
---

# SO3LR Vacuum NVT Rescue Plan — WW, GB3, NTL9

## Scope

Three of five SO3LR Tier A/B vacuum NVT pilots (task-002) failed to reach
5 ns of physically meaningful dynamics:

| Protein | Atoms | Failure mode | Diagnosis |
|---------|------:|--------------|-----------|
| WW      | 534   | NaN at 0.704 ns, structure intact (Rg ratio 0.983) | **Numerical** — float32 catastrophic cancellation in long-range / dispersion sum on a small 534-atom system. Rg ~9 Å vs lr_cutoff=12 Å is a tight buffer book-keeping window. |
| GB3     | 862   | Silent structural explosion at ~100 ps (Rg 10.6→986 Å), no NaN, T=300±13 K maintained throughout 5 ns log | **Physics** — net charge -2 (7 K + 0 R = +7; 5 D + 4 E = -9). In vacuum, like-charged surface side chains cannot be Debye-screened; NHC reports kinetic T from sum |v|² but does NOT penalize collective Coulomb-driven expansion. H drift 29.3 eV/ns highest of all 5 (weak indicator). |
| NTL9    | 813   | Same pattern as GB3 (Rg explosion ~100 ps), late NaN at 4.39 ns | **Physics** — net charge +5 (10 K + 0 R = +10; 2 D + 3 E = -5), Lys-rich N-terminus → strong electrostatic stress. |

The prior task-002 SubAgent's recommendation that "GB3 and NTL9 are dead, no
parameter tuning will rescue them at dt=0.5 fs" is correct in scope (integrator
parameters cannot save a charged-protein-in-vacuum failure) but misses the
actual cure: **change the chemistry, not the numerics.**

## Per-protein rescue protocol

### WW: numerical fix (float64 + halved timestep)

Failure is not chemistry-driven; structure is intact at NaN. The 0.704-ns NaN
event in a small 534-atom system points to a precision cliff in the long-range
sum. Cure space:

| Knob | Prior | Rescue | Rationale |
|------|-------|--------|-----------|
| Precision | float32 | **float64** | Eliminates catastrophic cancellation in the lr/dispersion sum. Confirmed via SO3LR CLI `--precision float64` flag. |
| dt | 0.5 fs | **0.25 fs** | Halves the per-step error and reduces accumulation of round-off in the Velocity-Verlet update. Confirmed via SO3LR CLI `--dt 0.25`. |
| NHC chain | 3 | **5** | Slightly longer chain absorbs better; cheap to change. Confirmed via `--nhc-chain 5`. |
| NHC Tdamp | 50 fs | 50 fs (equivalent) | `--nhc-thermo 100` × dt=0.25 fs = 25 fs damping; we restore 50 fs by setting `--nhc-thermo 200` (units: dt × thermo). |
| Other | unchanged | unchanged | Same lr-cutoff 12.0, same buffers 1.25/1.25, seed=42, --relax. |

**Throughput estimate.** WW float32 dt=0.5 fs achieved 17.4 ns/day. Halving dt
roughly halves throughput; float64 typically adds 1.5–1.7× wallclock (memory
bandwidth bound for the long-range neighbor list on a small system). Estimate
~5.5 ns/day → 0.5 ns gate ≈ 2.2 hr. 5 ns full ≈ 22 hr.

**Probability of success.** ~70%. If float64 alone fixes the NaN at dt=0.5 fs,
the dt=0.25 fs is overkill but cheap to keep. If both fail, the failure is in
the SO3LR potential itself for this protein and cannot be patched without
upstream model changes.

**Cost.** Gate: ~2.2 hr × 1 GPU = 2.2 GPU-hr × 15 SU/hr (Standard) = ~33 SU,
or ~9 priority SU if we use prio_mg269 to bypass the queue.

### GB3: chemistry fix (neutralize protonation)

Failure is unambiguously physics, not numerics. SO3LR was trained on
neutral-charge condensed-phase configurations; its long-range Coulomb terms
in vacuum are not screened by water and the integrator cannot dissipate the
net-charge-driven expansion.

**Cure: re-prep at neutral protonation.**

GB3 residue inventory (chain A, residues 1-56): 7 K, 0 R, 5 D, 4 E.
Net charge at pH 7 = +7 - 9 = -2. To neutralize:

- Protonate D side chains (COO⁻ → COOH): use OpenMM Modeller variant **ASH**
- Protonate E side chains (COO⁻ → COOH): use OpenMM Modeller variant **GLH**
- Deprotonate K side chains (NH₃⁺ → NH₂): use OpenMM Modeller variant **LYN**

After neutralization: 0 charged residues → net charge = 0 (electrically neutral
acid/base set). **No ARGs in GB3, so no manual ARN/guanidinium hand-editing
required.**

**Implementation path.** Write a parallel prep script
`output/scripts/so3lr_prep_proteins_neutral.py` that:

1. Strips the input PDB to chain A + residue range (same as v1 prep).
2. Builds an OpenMM Modeller from the stripped PDB.
3. Constructs a per-residue `variants` list: `LYN` for every K, `ASH` for
   every D, `GLH` for every E, `None` (default) for everything else.
4. Calls `Modeller.addHydrogens(forcefield=ff, pH=7.0, variants=variants)`.
5. Writes the resulting topology + positions to:
   - `input_neutral_h.pdb` (audit trail)
   - `input_neutral.xyz` (SO3LR input; same extended-XYZ format as v1)
6. Asserts net formal charge = 0 from the produced topology
   (sum of integer charges over standard residues).

Settings unchanged from v1: dt=0.5 fs, float32, NHC chain=3, lr-cutoff 12.0.

**Probability of success.** ~60%. Risk factors: (a) SO3LR's training set may
include net-charged species, in which case neutralizing K/D/E may move the
system out-of-distribution differently. (b) Local protonation pattern may
distort H-bond network, perturbing folded topology. (c) Modeller's H-placement
for ASH/GLH/LYN is geometric, not energy-minimized; SO3LR's relax step
(--relax + --force-conv 0.05) should still bring the system to a local minimum.

**Throughput estimate.** GB3 v1 ran at 10.13 ns/day. No throughput change
expected (same dt/precision). Gate 0.5 ns ≈ 1.2 hr; full 5 ns ≈ 11.85 hr.

**Cost.** Gate: ~1.2 hr × 15 SU/hr Standard = 18 SU, or ~5 priority SU.

### NTL9: chemistry fix (same as GB3)

NTL9 residue inventory: 10 K, 0 R, 2 D, 3 E. Net charge at pH 7 = +10 - 5 = +5.
Same approach as GB3: LYN for all K, ASH for all D, GLH for all E. Net → 0.

Throughput: NTL9 v1 ran at 10.76 ns/day. Gate 0.5 ns ≈ 1.1 hr; full 5 ns ≈
11.18 hr. Cost: gate ~17 SU Standard, ~5 priority.

## Gate criteria (500 ps pre-screen)

Each rescue gate writes a 500 ps trajectory. ALL of the following must hold:

1. **No NaN through 500 ps** (parsed from stageA.log; no all-NaN frame in
   the HDF5 positions).
2. **Rg ratio < 1.2** at the last cycle vs initial Rg (gentle structural
   tolerance; rejects the 90× explosion mode).
3. **T mean 285-315 K** over 50-500 ps window (drops first 50 ps as
   equilibration).
4. **COM displacement < 5 Å** vs initial frame (a stronger statement than Rg
   alone; catches drift-but-not-explode failure modes).

If gate PASSES → submit full 5 ns rescue (Stage 4).
If gate FAILS → escalation ladder (next section).

## Escalation ladder per protein

### GB3 / NTL9 escalation

If neutral-protonation gate fails (NaN OR explosion):
- **Tier 2 attempt:** counter-ion shell. Place a small Na⁺/Cl⁻ atmosphere
  within 5-7 Å of the protein surface (no PBC, no solvent). Shell should
  exactly compensate the protein's net charge (e.g., 5 Cl⁻ for NTL9 +5; 2 Na⁺
  for GB3 -2). This is more invasive (changes the input system size and
  composition) and is reserved as a fallback.
- **If counter-ion shell also fails:** write
  `shared/help-needed/head-1.2-so3lr-gb3-physics-bound.md` (and analogous for
  NTL9), documenting evidence and proposing PlannerAI scope revision:
  criterion #2 amendment from "5 ns vacuum NVT for ALL 5 proteins" → "5 ns
  SO3LR-suitable MD trajectory: vacuum NVT for net-neutral systems;
  counter-ion-shell or neutralized-protonation NVT for net-charged systems."
  **No silent compromise.**

### WW escalation

If float64 + dt=0.25 fs gate fails (NaN before 500 ps):
- **Tier 2 attempt:** float64 alone (dt=0.5 fs). Cheaper than
  float64+halved-dt; isolates which lever cures the NaN and guides Phase 2
  parameter selection.
- **If float64 alone also fails:** write
  `shared/help-needed/head-1.2-so3lr-ww-rescue-exhausted.md`. Failure mode
  is intrinsic to SO3LR for small systems; no further parameter tuning is
  expected to help.

## SU budget

Total rescue gate envelope (priority): 9 (WW) + 5 (GB3) + 5 (NTL9) = **~19
priority SU**. Well under the 25-SU per-task ceiling and the 50-SU shared
envelope with MACE NPT probes. User has authorized this campaign.

Production 5 ns rescues (per passing gate, Standard Tier): ~12 hr × 15 SU/hr
= 180 SU. Three passing → ~540 Standard SU total. Acceptable.

If Standard Tier (`pi_mg269`, fair-share 0.0146) queue blocks past 2026-05-08,
escalate to head-1.2 for limited priority Tier authorization (~30 priority SU
per 5 ns rescue, ~90 priority SU total worst-case). Budget exists; user has
not objected.

## Scripts to be authored

1. `output/scripts/so3lr_prep_proteins_neutral.py` — parallel prep that
   uses OpenMM Modeller's variants kwarg to neutralize K/D/E.
2. `output/scripts/so3lr_rescue_runner.py` — fork of `so3lr_pilot_runner.py`
   that adds `--precision`, `--dt-fs`, `--nhc-chain`, `--nhc-thermo` flags
   passed to the SO3LR CLI. Also accepts `--input-xyz` override so
   neutral-prepped XYZs can be used.
3. `output/scripts/so3lr_rescue.sbatch` — fork of `so3lr_pilot.sbatch` with
   per-protein parameter overrides via SLURM `--export`. Preserves env-so3lr
   contract (`PYTHONNOUSERSITE=0` + user-site appended to `PYTHONPATH`).
4. `output/scripts/submit_so3lr_rescue.sh` — submitter that submits gate jobs
   first; production submitted only after gate passes (manual verification).

## Order of operations

1. Stage 1 (this doc): rescue plan ✓
2. Stage 2: write neutral prep, rescue runner, sbatch, submit wrapper
3. Stage 2.5: run neutral prep on GB3 and NTL9 (env-mace, login node, < 1 min)
4. Stage 2.6: write a charge-check helper that asserts net formal charge = 0
   on the new XYZ (parse PDB topology, sum standard formal charges)
5. Stage 3: submit 3 gate jobs (priority queue, prio_mg269, RTX 5000 Ada,
   500 ps each, cryptic 8-char names)
6. Stage 4: when gate passes, submit 5 ns full rescue (Standard preferred,
   priority fallback)
7. Stage 5: status report + cross-agent note(s)

## Hard constraints (carried forward from task spec)

- Cryptic 8-char alphanumeric job names.
- env-so3lr contract: `PYTHONNOUSERSITE=0` + user-site appended to PYTHONPATH
  AFTER env site-packages.
- DO NOT modify env-so3lr or env-mace.
- DO NOT exceed 25 priority SU on this campaign.
- DO NOT skip the 500 ps gate before committing to 5 ns.
- DO NOT silently compromise. If 5/5 not achievable after exhausting 2 rescue
  protocols per failed protein, escalate via help-needed doc.

## References

- `shared/notes/1.2-so3lr-pilot-stability.md` (§2-3 failure analysis)
- `output/so3lr_vacuum_stability_report.md` (per-protein metrics)
- `phases/phase-1/subphase-1.1/output/scripts/so3lr_crambin_v5.sbatch` (D1
  PASS reference; env-so3lr contract)
- `shared/notes/1.2-env-so3lr-typing-extensions-fix.md` (env-so3lr SLURM
  contract)
- `shared/notes/operational-practices.md` (cryptic names, SU policy,
  diagnostic-first rule)
- OpenMM Modeller.addHydrogens documentation (variants: LYN, ASH, GLH;
  no ARN — n/a here since GB3 and NTL9 have 0 ARG)
- Frank et al., 2024, "A Euclidean transformer for fast and stable machine
  learned force fields" (Nat Commun 15:6539); SO3LR Sec. 5.x discusses
  vacuum-NVT applicability to neutral systems.
- SO3LR CLI: `so3lr nvt --help` (confirms `--precision float32|float64`,
  `--dt`, `--nhc-chain`, `--nhc-thermo`, `--total-charge` flags)
