# NVT Production Plan: Classical-NPT-Box + MACE-NVT

**Date:** 2026-04-28
**Author:** head-1.2
**Status:** ACTIVE — Test H FAILED 2026-05-01. This is the production path for Sub 1.3/1.4.
**Triggered by:** MACE hybrid NPT instability (all 5 diagnostics fail; root cause is MonteCarloBarostat + PythonForce incompatibility)

> **UPDATE 2026-05-01:** Test H (wrapping fix, job 10328941/2cp2fn3k) FAILED —
> NaN at ~5ps equil, identical to Test B without fix. Wrapping was not the root
> cause. NPT is confirmed not viable with MACE hybrid. **This NVT plan (Path B)
> is now the production path.** Sub 1.3/1.4 should implement the two-stage
> protocol described below.

---

## 1. Overview

Two-stage protocol replacing the failed NPT approach:

1. **Stage 1:** Classical-only NPT equilibration (AMBER14 + TIP3P-FB, no MACE) to
   converge box dimensions and density. Outputs a solvated PDB with equilibrated
   coordinates and a JSON file with final box vectors.

2. **Stage 2:** MACE hybrid NVT production using the Stage 1 pre-equilibrated box.
   100 ps NVT re-equilibration (to relax protein under MACE forces), then 5 ns
   (Sub 1.2 target) or 10 ns (Phase 2 target) production.

---

## 2. Scientific Justification

### Why NVT at equilibrium density is valid for our observables

S2 order parameters are local rotational autocorrelations of N-H bond vectors.
They are governed by internal protein dynamics and local solvation, not global
box volume fluctuations. NVT at the correct equilibrium density produces the
same structural ensemble as NPT for these observables because:

- Water is essentially incompressible at biological conditions
- Volume fluctuations in NPT are tiny (~0.1% for a well-equilibrated protein box)
- Local protein dynamics are insensitive to the ~0.1 bar pressure fluctuations
  that NVT introduces vs NPT

### Literature precedent

- **NNP/MM** (Galvelis et al., 2023, JCTC, PMC10577237): The leading hybrid ML/MM
  paper ran ALL production simulations in NVT, not NPT. 10 × 100 ns trajectories
  per protein-ligand system. Deliberate choice.
- **MACE-OFF** (Kovacs et al., 2024, JACS): Water density benchmarks likely used
  ASE NPT (Parrinello-Rahman), but protein simulations did not explicitly report NPT.
- **GEMS** (Unke et al., 2024, Sci Adv): Used continuous Nose-Hoover + Parrinello-Rahman
  in SchNetPack, not OpenMM's MC barostat. Confirms that continuous barostats work
  with ML potentials; discrete MC does not.
- **Standard classical MD practice:** The OpenMM documentation describes NPT equilibration
  → NVT production as a standard workflow.

### Properties affected vs unaffected

| Property | Affected? | Impact on project |
|----------|-----------|-------------------|
| S2 order parameters | No | Primary observable — unaffected |
| RMSF, C-alpha RMSD | No | Key structural metrics — unaffected |
| Protein internal dynamics | No | Core analysis — unaffected |
| Local solvation structure | No | Relevant for ML validation — unaffected |
| Isothermal compressibility | Yes (cannot compute) | Not in analysis plan — irrelevant |
| Long-range density fluctuations | Yes (suppressed) | Not in analysis plan — irrelevant |
| Systematic pressure offset | Possible (<2%) | Document in Methods; negligible effect |

### Why the box dimensions from classical NPT are correct

MACE only handles the protein intramolecular forces. Water-water and water-ion
interactions (which dominate the box density) are treated by the same classical
force field (AMBER14 + TIP3P-FB) in both stages. The protein is a small fraction
of the box volume (~7-10%), so MACE replacing AMBER14 for protein forces has
minimal effect on equilibrium box dimensions.

---

## 3. Stage 1: Classical NPT Equilibration

### Script: `classical_npt_equil.py`

**Derived from:** system-build portion of `mace_hybrid_npt.py` (lines 255-447),
stripped of all MACE/openmmml code.

**Protocol:**
1. Load PDB, crop (WW: residues 6-39; GB3: 1-56; UBQ: 1-76)
2. PDBFixer (fill missing heavy atoms, add hydrogens at pH 7)
3. Solvate with TIP3P-FB (padding=1.0 nm, ionic strength=0.15 M NaCl)
4. Build classical system: `ForceField('amber14-all.xml', 'amber14/tip3pfb.xml').createSystem()`
   with PME, 1.0 nm cutoff, rigid water, HBonds constraints
5. Add `MonteCarloBarostat(1 atm, 300 K, freq=25)` — proven stable (Test A: 80 ps clean)
6. `LangevinMiddleIntegrator(300 K, 1/ps, 2 fs)` — classical can safely use 2 fs with
   HBonds constraints
7. Minimize (maxIterations=2000, tol=10 kJ/mol/nm)
8. Set velocities to temperature
9. Run 500 ps NPT equilibration (monitoring density, volume, T, P every 1 ps)
10. Run 500 ps NPT production (same monitoring)
11. Save outputs:
    - `{protein}_equil.pdb` — final coordinates with equilibrated box
    - `{protein}_box_vectors.json` — box vectors: `{"a": [x,y,z], "b": [x,y,z], "c": [x,y,z]}`
    - `{protein}_equil_log.csv` — density, volume, T, P time series
    - `{protein}_equil_summary.json` — final density, volume stats over last 200 ps
12. Verify convergence: density 0.99-1.03 g/cm³, volume drift over last 200 ps < 1%

**Key differences from mace_hybrid_npt.py:**
- No MACE imports, no `openmmml`, no `MLPotential`, no PythonForce
- HBonds constraints + 2 fs timestep (classical gold standard)
- No checkpoint/restart needed (entire run fits in one SLURM job)
- Outputs box vectors as JSON for Stage 2 consumption

**Retained from existing code:**
- GPU keepalive thread (5-min cadence)
- `PYTHONNOUSERSITE=1`
- PDB loading/cropping logic
- PDBFixer pipeline
- Solvation with TIP3P-FB
- Logging infrastructure

### Compute Estimate

| Protein | Total atoms | Throughput (est.) | 1 ns wall | Partition | SU cost |
|---------|-------------|-------------------|-----------|-----------|---------|
| WW | ~7,500 | ~400 ns/day | ~3.5 min | gpu (RTX 5000 Ada) | ~1 SU |
| GB3 | ~10,000 | ~300 ns/day | ~5 min | gpu (RTX 5000 Ada) | ~1.3 SU |
| UBQ | ~17,000 | ~200 ns/day | ~7.2 min | gpu (RTX 5000 Ada) | ~1.8 SU |
| **Total** | | | **~16 min** | | **~4 SU** |

Run on RTX 5000 Ada (15 SU/hr). No reason to burn H200 SU for classical equilibration.
All 3 proteins can run sequentially in a single SLURM job.

---

## 4. Stage 2: MACE Hybrid NVT Production

### Script: `mace_hybrid_nvt_prod.py`

**Derived from:** `mace_hybrid_npt.py` with the following modifications.

**Protocol:**
1. Load Stage 1 output PDB (`{protein}_equil.pdb`) — pre-solvated, equilibrated coordinates
2. Read Stage 1 box vectors from JSON
3. Identify protein atoms from topology (residue names in standard amino acid set)
4. Build MACE hybrid system: `MLPotential('mace-off24-medium').createMixedSystem()` with
   f32 bypass, vesin NL replacement
5. **Do NOT add MonteCarloBarostat** — this is the critical change
6. Set periodic box vectors from Stage 1: `simulation.context.setPeriodicBoxVectors(*box_vectors)`
7. `LangevinMiddleIntegrator(300 K, 1/ps, 1 fs)` — same as current
8. Minimize (maxIterations=2000, tol=10 kJ/mol/nm)
9. Self-test (10 steps, NaN check)
10. Run 100 ps MACE NVT re-equilibration (see §5 justification)
11. Save post-equilibration checkpoint
12. Reset step counter, run NVT production to TARGET_NS (5 ns Sub 1.2, 10 ns Phase 2)
13. Checkpoint/restart loop with walltime guard (same as NPT script)

### Improvements carried forward from NPT script

- Vesin neighbor list (eliminates GIL deadlock, matscipy replacement)
- Float32 MACE bypass (1.21× speedup: 2.56 vs 2.13 ns/day)
- Checkpoint/restart loop with `progress.json` atomic write
- Append-mode DCD reporter
- Append-mode StateDataReporter with C2 fix (`_initialClockTime`, `_initialSimulationTime`,
  `_initialSteps` set on resume)
- Walltime guard at 22.5 hr
- 5000-step checkpoint interval
- 1000-step NaN checks
- 5000-step progress logging during equilibration
- Self-diagnostic 10-step test post-minimization
- Meta JSON with per-session tracking
- Topology PDB output
- C1 fix: stale-checkpoint particle mismatch also deletes prod_dcd and prod_csv

### Key differences from NPT script

- No `MonteCarloBarostat` (the central change)
- No `BAROSTAT_MODE`, `PRESSURE_ATM`, `BAROSTAT_FREQ` config vars
- Loads Stage 1 PDB instead of building from raw PDB (avoids re-solvation, guarantees
  same atom count/ordering for checkpoint compatibility)
- Sets box vectors from Stage 1 JSON
- Does not report `volume` or `density` in StateDataReporter (constant in fixed-box NVT)
- 100 ps equilibration (not 50 ps)

### Key differences from Sub 1.1 NVT script

- Uses Stage 1 pre-equilibrated box (Sub 1.1 used whatever Modeller produced)
- Full checkpoint/restart infrastructure
- Vesin NL and f32 bypass (Sub 1.1 had neither)
- Walltime guard
- Per-protein defaults table with PDB paths and crop ranges
- Longer equilibration (100 ps vs 50 ps)
- Much longer production target (5000 ps vs 100 ps)

### System Build Approach

The Stage 2 script loads the Stage 1 PDB directly (which includes protein + water + ions
in the equilibrated box). This avoids:
- Re-solvation (which could produce different atom count)
- PDBFixer re-run (already done in Stage 1)
- Any mismatch between Stage 1 and Stage 2 topologies

The script identifies protein atoms from the loaded topology (standard amino acid
residue names), then builds the MACE hybrid system treating those as the ML region.

### Compute Estimate

Throughput based on measured WW data (2.56 ns/day on H200 OpenCL with f32 bypass).
Larger proteins scale roughly inversely with MACE atom count.

| Protein | MACE atoms | Total atoms | ns/day (H200) | 100 ps equil | 5 ns prod | Total wall | H200 GPU-hrs | SU |
|---------|-----------|-------------|---------------|-------------|-----------|-----------|-------------|-----|
| WW | 534 | ~7,500 | 2.56 (measured) | ~56 min | ~47 hr | ~48 hr | 48 | 14,400 |
| GB3 | ~862 | ~10,000 | ~1.5 (projected) | ~1.6 hr | ~80 hr | ~82 hr | 82 | 24,600 |
| UBQ | ~1,231 | ~17,000 | ~0.85 (projected) | ~2.8 hr | ~141 hr | ~144 hr | 144 | 43,200 |
| **Total** | | | | | | **~274 hr** | **274** | **82,200** |

SLURM resubmits (24h wall each): WW ~3, GB3 ~4, UBQ ~7. Total: ~14 resubmits.

Budget impact: 274 H200 GPU-hrs = ~9.1% of remaining Phase 1 Alpha-M budget (~2,996 GPU-hrs).

---

## 5. MACE NVT Re-Equilibration Justification

A re-equilibration phase is essential when switching from classical to MACE forces:

1. **Force discontinuity at the switch.** MACE-OFF24 produces different forces than
   AMBER14 on the same geometry. Protein coordinates equilibrated under classical forces
   have systematic strain under the ML potential.

2. **Precedent.** Both the Sub 1.1 NVT script (50 ps) and the NPT script (50 ps) include
   MACE hybrid equilibration. The config audit recommended 100 ps for Phase 2.

3. **Duration: 100 ps.**
   - 2× the NPT script's 50 ps (which was called "marginal for UBQ")
   - Wall-time cost: ~56 min for WW, ~2.8 hr for UBQ. Acceptable.
   - Temperature is already correct (Langevin thermostat, Maxwell-Boltzmann init at 300 K)
   - Box is already at correct density (from Stage 1)
   - Only protein internal DOFs need to relax under MACE potential

4. **Discard equilibration frames from analysis.** First 100 ps not used for S2 calculations.

---

## 6. SLURM Workflow

1. Submit 3 classical NPT equilibration jobs to `gpu` (RTX 5000 Ada). All complete
   in under 15 minutes. Can run sequentially in one job.
2. Verify Stage 1 output: density ~1.0 g/cm³, volume converged, no NaN.
3. Submit 3 MACE NVT production jobs to `gpu_h200` with checkpoint/restart wrapper.
   - Job names: cryptic 8-char alphanumeric (per operational practices)
   - Wall time: 23:59:00 per submission
   - Walltime guard: 22.5 hr (saves checkpoint before SLURM kill)
   - Resubmit until TARGET_NS reached
4. Monitor via `progress.json` and SLURM resubmission pattern.

### Stability monitoring during production

| Criterion | Threshold | Source |
|-----------|-----------|--------|
| Temperature | 300 ± 15 K | StateDataReporter |
| PE NaN count | 0 | NaN checks every 1000 steps |
| PE drift | < 5% secular trend | StateDataReporter |
| C-alpha RMSD vs frame 0 | < 5 Å | Post-analysis (mdtraj) |
| Box dimensions | Constant (by construction) | Fixed in NVT |
| Density vs Stage 1 | Within 0.5% | Verify at start of Stage 2 |

---

## 7. Optional Path A: NPT Wrapping Fix Test

If user approves additional priority SU (~10 SU), a single diagnostic can test
whether the minimum-image wrapping fix makes NPT viable.

### Test H: MACE hybrid f32, freq=25, WITH wrapping fix

**Script change:** In the `_f32_compute` callback, after `pos = pos[idx]`, add:

```python
if periodic:
    frac = pos @ np.linalg.inv(cell)
    frac -= np.floor(frac)
    pos = frac @ cell
```

**Test parameters:** Same as original v6 diagnostic (50 ps equil + 1 ps production).
If it survives past 30 ps equil without NaN, the fix likely works.

**If it works:** NPT becomes viable for Phase 2. File upstream bug report to openmm-ml.
Update OSF pre-reg to note NPT (not NVT) as the production ensemble.

**If it doesn't work:** Confirms that wrapping is not the only issue. Commit fully to
Path B (NVT). No further NPT experiments.

---

## 8. Risks and Mitigations

| Risk | Prob. | Mitigation |
|------|-------|------------|
| MACE NVT crashes after switching from classical coords | Low | 100 ps re-equilibration; Sub 1.1 proved NVT stable from PDBFixer-only coords (harsher starting point) |
| Density mismatch (classical vs MACE equilibrium) | Low | MACE handles <10% of box volume; verify initial density matches Stage 1 within 0.5% |
| Stage 1 PDB atom count mismatch on reload | Near-zero | Verify count in Stage 2 startup; abort with clear error |
| H200 OpenCL hangs | ~30%/job | Checkpoint/restart + hang watchdog (carried forward) |
| Fair-share queue delays | High | Stage 1 can use scavenge_gpu; Stage 2 needs gpu_h200 (fair-share dependent) |

---

## 9. Implementation Timeline

| Step | Owner | When | Effort |
|------|-------|------|--------|
| Write `classical_npt_equil.py` | Sub 1.3 SubAgent or head-1.2 | Sub 1.3 start | 1-2 days |
| Write `mace_hybrid_nvt_prod.py` | Sub 1.3 SubAgent or head-1.2 | Sub 1.3 start | 2-3 days |
| Run Stage 1 (3 proteins) | SubAgent | Same day as script | <1 hour |
| Submit Stage 2 (3 proteins) | SubAgent | After Stage 1 verify | 6 days wall (parallel) |
| ~~(Optional) Test H wrapping fix~~ | ~~head-1.2~~ | **SUBMITTED 2026-04-30** (job 10315976/q67steb9, priority_gpu, wall 3:10:00, 50 SU) | Results pending (~May 1) |
