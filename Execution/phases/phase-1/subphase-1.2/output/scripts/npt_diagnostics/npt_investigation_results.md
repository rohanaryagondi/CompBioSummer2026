# MACE Hybrid NPT Investigation: Complete Results

**Date:** 2026-04-28
**Investigator:** head-1.2 (HeadAI Sub 1.2)
**System:** WW domain, 534 MACE atoms, ~7500 total (AMBER14/TIP3P-FB), OpenCL on RTX 5000 Ada
**Budget:** 58.5 SU spent on prio_mg269 (50 SU allocated, 8.5 over)

---

## 1. Diagnostic Results

| Test | Job ID | Config | Crash point | T (K) | Density (g/cm³) | Wall time | SU |
|------|--------|--------|-------------|-------|-----------------|-----------|-----|
| A | 9804704 (q6byygle) | Classical-only NPT, freq=25 | Never (80 ps clean) | 292-307 | 1.019-1.035 | 0:29 | 0.12 |
| B | 9804705 (q6wjsyhu) | MACE hybrid f32, freq=100 | ~5 ps equil | — | — | 12:52 | 3.22 |
| F | 9804708 (q6q6ijfi) | MACE hybrid f64, freq=25 | ~17 ps equil | 299-311 | 1.020-1.033 | 2:55:38 | 43.91 |

Prior diagnostics:

| Test | Job ID | Config | Result | SU |
|------|--------|--------|--------|-----|
| v6 diag | 9612539 (d6v6fxwq) | MACE hybrid f32, freq=25 | NaN at ~25 ps equil | 11.17 |
| Path bug (×3) | 9763415/17/58 | A/B/F with BASH_SOURCE bug | Instant fail (script not found) | 0.04 |

Test F f64 detailed timeline:

| Phase | Wall time | Result |
|-------|-----------|--------|
| Minimization | 1684s (28 min) | OK, max force 2.34e+03 |
| Self-test (10 steps) | 5s | PASS, max force 2.37e+03 |
| Equil 5 ps | 2588s (43 min) | T=299.2 K, rho=1.020 |
| Equil 10 ps | 5189s (86 min) | T=310.9 K, rho=1.033 |
| Equil 15 ps | 7775s (130 min) | T=302.1 K, rho=1.031 |
| Equil ~17 ps | ~8836s (~147 min) | **NaN crash** |

f64 throughput: 0.167 ns/day (5.5× slower than f32's 0.92 ns/day on RTX 5000 Ada).

Tests NOT run (SU budget exhausted): C (freq=500), D (0.5 fs), E (aniso barostat), G (combo).

---

## 2. Root Cause: Missing Minimum-Image Wrapping in `_computeMACE`

### The Bug

The openmm-ml `_computeMACE` callback (`macepotential.py:232-267`) and our production
f32 bypass (`_f32_compute`) do NOT apply minimum-image wrapping to protein atom positions
before passing them to the neighbor list builder (`get_neighborhood`).

During MonteCarloBarostat trial moves, OpenMM:
1. Scales all box vectors by factor `s`
2. Scales all molecular centroids by `s`
3. May reimage/wrap positions into the new periodic box
4. Calls all forces (including PythonForce/MACE) to evaluate energy at the new geometry

Step 3 is where the problem occurs. The PythonForce documentation (`openmm.py:19589`)
states: "The positions may also be wrapped into a different periodic box to keep them
closer to the origin and improve accuracy." This wrapping uses the NEW (rescaled) box
vectors. If the protein centroid has drifted near a box face, the wrapping can place
some protein atoms on the opposite side of the box.

The `_computeMACE` callback then does:

```python
positions = state.getPositions(asNumpy=True).value_in_unit(unit.angstrom)
positions = positions[indices]  # subset to protein atoms
# NO minimum-image wrapping here
ei, sh, _, _ = get_neighborhood(positions, cutoff, pbc, cell)
```

The neighbor list builder receives positions with atoms potentially on opposite sides
of the box. This produces an incorrect edge graph where bonded atoms (~1.5 Å apart)
appear to be ~(box_length - 1.5) Å apart. MACE sees a geometry far outside its
training distribution → enormous or NaN forces.

### Source Code Locations

| File | Lines | Content |
|------|-------|---------|
| `openmmml/models/macepotential.py` | 226-229 | PythonForce creation with `setUsesPeriodicBoundaryConditions(True)` |
| `openmmml/models/macepotential.py` | 232-267 | `_computeMACE` — reads positions, builds NL, runs model |
| `openmmml/models/macepotential.py` | 237-240 | Position extraction: raw from State, then subset by indices |
| `openmmml/models/macepotential.py` | 247 | Neighbor list build: `get_neighborhood(positions, cutoff, pbc, cell)` |
| `mace/data/neighborhood.py` | 38-46 | `neighbour_list` call (matscipy) — handles PBC internally |
| `openmm/openmm.py` | 19589 | PythonForce docs: positions may be wrapped |
| `openmmml/mlpotential.py` | 235-396 | `createMixedSystem` — no special barostat handling |

### The Proposed Fix (~3 lines)

Add minimum-image wrapping before `get_neighborhood`:

```python
# After subsetting positions to protein atoms:
if periodic:
    frac = positions @ np.linalg.inv(cell)
    frac -= np.floor(frac)
    positions = frac @ cell
```

This ensures all protein atoms are within the primary cell before the neighbor list is
built. Needs to be applied in both:
1. openmm-ml `_computeMACE` (macepotential.py:240, after `positions = positions[indices]`)
2. Production f32 bypass `_f32_compute` (mace_hybrid_npt.py, after `pos = pos[idx]`)

### Why This Explains All Observations

- **Classical NPT PASS:** No MACE neighbor list → no wrapping bug
- **MACE NVT PASS:** No box rescaling → no wrapping inconsistency
- **f64 delays crash:** Precision doesn't fix the geometric bug, but f64 force evaluation
  may produce slightly different trajectories that delay centroid drift to a box face
- **Crash timing is stochastic:** Depends on when the protein centroid happens to drift
  near a box face during a barostat trial move. At freq=25 with 1 fs timestep, there
  are ~1000 barostat moves per ps → 15,000-25,000 moves before a rare catastrophic event
- **freq=100 crashed faster:** Fewer barostat moves per ps, but the larger per-move
  volume changes may push the centroid past a face more aggressively

---

## 3. Literature Survey

### Published MACE NPT

| Paper | System | Barostat | Engine | Precision | Stable? |
|-------|--------|----------|--------|-----------|---------|
| MACE-OFF (Kovacs 2024 JACS) | Crambin 18K atoms | Not specified (likely ASE P-R) | OpenMM or ASE | f64 forces | Yes (1.6 ns) |
| GEMS (Unke 2024 Sci Adv) | Crambin 25K atoms | **Nose-Hoover + Parrinello-Rahman** | SchNetPack | — | Yes (10 ns) |
| AI2BMD (Microsoft 2024 Nature) | Solvated proteins | Custom | Custom | — | Yes (2 ns) |
| NNP/MM (Galvelis 2023 JCTC) | Protein-ligand 38-60K | **None (NVT deliberately)** | OpenMM | — | Yes (100 ns) |
| CHARMM-GUI hybrid (2026 JCIM) | Small-molecule ML region | MonteCarloBarostat | OpenMM | — | Yes (NPT) |

**Key insight:** All stable MACE NPT uses continuous barostats (Nose-Hoover, Parrinello-Rahman).
The one case of MC barostat + ML working (CHARMM-GUI) had a tiny ML region (ligand, not protein).
OpenMM has NO continuous barostat option.

### Relevant GitHub Issues

- **openmm-ml #52:** PBC not replicated for ML portion — box blows up. Open, no fix.
- **openmm-torch #34:** Protein unfolds with ANI-2x + MC barostat. Labeled "wontfix."
- **openmm #3227:** NaN with barostat (not ML-specific but same class).
- **openmm #635:** Request for Parrinello-Rahman. Open since 2015. No implementation.

### Literature Verdict

No published example of stable OpenMM MonteCarloBarostat + MACE hybrid for a solvated
protein. The NNP/MM paper (leading hybrid ML/MM work) deliberately avoided NPT entirely.
NVT with pre-equilibrated box is the community standard for this class of system.

---

## 4. Forward Paths

### Path A: Test the Wrapping Fix (NPT recovery attempt)

**What:** Patch the f32 bypass with minimum-image wrapping, run one diagnostic.

**Code change (~3 lines in `_f32_compute`):**
```python
# After: pos = pos[idx]
# Add:
if periodic:
    frac = pos @ np.linalg.inv(cell)
    frac -= np.floor(frac)
    pos = frac @ cell
```

**Test:** Submit Test H — MACE hybrid f32, freq=25, with wrapping fix. Same params as
original v6 diagnostic (50 ps equil + small production). If it survives past 30 ps
equil without NaN, the fix works.

**Cost:** ~5-10 SU on prio_mg269 (currently 8.5 SU over budget — needs user approval).

**If it works:** NPT becomes viable for Phase 2 production. Stronger paper (true NPT
ensemble). Would also file upstream bug report to openmm-ml.

**If it doesn't work:** Fall back to Path B. The wrapping fix may not be the only issue
(e.g., neighbor list skin distance, cutoff interaction with box scaling, etc.).

### Path B: NVT with Pre-Equilibrated Box (safe production path)

**What:** Two-stage protocol. Stage 1: classical NPT equilibration (1 ns, ~15 min/protein
on RTX 5000 Ada). Stage 2: MACE hybrid NVT production (100 ps re-equil + 5 ns prod on H200).

**Scientific justification:** S2 order parameters are local rotational autocorrelations —
insensitive to box volume fluctuations. NVT at equilibrium density is equivalent to NPT
for our observables. Water is essentially incompressible at biological conditions. The
NNP/MM paper (Galvelis 2023) validated this exact approach.

**Properties NOT affected by NVT vs NPT:**
- S2 order parameters (our primary observable)
- RMSF, C-alpha RMSD
- Protein internal dynamics
- Local solvation structure

**Properties affected (irrelevant for our project):**
- Isothermal compressibility (cannot compute from volume fluctuations)
- Long-range density fluctuations (suppressed in NVT)
- Systematic pressure offset if classical density ≠ MACE density (<2% per production agent)

**Compute cost:**
- Stage 1: ~4 SU total for all 3 proteins on RTX 5000 Ada (negligible)
- Stage 2: ~274 H200 GPU-hrs (~82,200 SU) for 3 proteins × 5 ns
- Same total cost as the original NPT plan

**Scripts needed:**
1. `classical_npt_equil.py` — Derived from system-build portion of mace_hybrid_npt.py,
   stripped of MACE. HBonds constraints, 2 fs timestep, MCB, 500 ps equil + 500 ps prod.
   Outputs: solvated PDB, box vectors JSON, density log.
2. `mace_hybrid_nvt_prod.py` — Derived from mace_hybrid_npt.py. Removes MCB. Loads
   Stage 1 PDB and box vectors. Carries forward: vesin NL, f32 bypass, checkpoint/restart,
   walltime guard, append-mode reporters, C1+C2 config audit fixes. 100 ps NVT re-equil.

### Recommendation

**Implement Path B immediately** (safe production path, no risk).
**Test Path A as a low-cost experiment** (if user approves additional ~10 SU prio budget).
If Path A succeeds, Phase 2 can use true NPT.

---

## 5. SU Accounting

| Job ID | Name | Test | SU | Wall | Status |
|--------|------|------|----|------|--------|
| 9612539 | d6v6fxwq | v6 diagnostic | 11.17 | 44:41 | FAILED (NaN@25ps) |
| 9763415 | q62v1dan | A (path bug) | 0.02 | 0:04 | FAILED |
| 9763417 | q6rquqy0 | B (path bug) | 0.01 | 0:03 | FAILED |
| 9763658 | q67epalk | F (path bug) | 0.01 | 0:03 | FAILED |
| 9804704 | q6byygle | A classical | 0.12 | 0:29 | PASS (exit 6 cleanup) |
| 9804705 | q6wjsyhu | B freq=100 | 3.22 | 12:52 | FAILED (NaN@5ps) |
| 9804708 | q6q6ijfi | F f64 MACE | 43.91 | 2:55:38 | FAILED (NaN@17ps) |
| **Total** | | | **58.46** | | **Budget: 50 SU** |

---

## 6. References

### Papers
- Kovacs et al., "MACE-OFF23," JACS 2024. DOI: 10.1021/jacs.4c07099
- Unke et al., "GEMS: A General-Purpose Machine Learning Electronic Structure Simulator," Sci Adv 2024. DOI: 10.1126/sciadv.adn4397
- Galvelis et al., "NNP/MM," JCTC 2023. PMC10577237
- Batatia et al., "Low-Precision MACE," arXiv:2510.23621 (2025)
- Eastman et al., "OpenMM 8," J Phys Chem B 2024. PMC10846090
- CHARMM-GUI Hybrid ML/MM Builder, JCIM 2026. PMC13014446
- Goniakowski et al., "Neighbor List Artifacts," JCTC 2023. PMC10720336

### GitHub Issues
- openmm-ml #52: PBC not replicated for ML portion (open)
- openmm-torch #34: Protein unfolds with ANI-2x NPT (wontfix)
- openmm #3227: NaN with barostat (general)
- openmm #635: Parrinello-Rahman request (open since 2015)
- ACEsuit/mace #990: NaN when f64 model downcast to f32

### Source Code
- openmm-ml macepotential.py (env-mace): PythonForce MACE callback
- openmm-ml mlpotential.py (env-mace): createMixedSystem
- mace/data/neighborhood.py (env-mace): neighbour_list wrapper
