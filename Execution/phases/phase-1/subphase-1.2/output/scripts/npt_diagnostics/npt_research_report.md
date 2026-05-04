# MACE-OFF24 Hybrid NPT NaN Crash: Research Report

**Date:** 2026-04-27
**System:** WW domain, 534 protein atoms (MACE-OFF24-medium), 7061 water+ions (AMBER14/TIP3P-FB), 7595 total
**Failure:** `OpenMMException: Particle coordinate is NaN` at ~25 ps (step ~25500 of 50000 equil)
**Platform:** RTX 5000 Ada, OpenCL, float32 MACE bypass mode
**Working baseline:** NVT identical system, 5 ns stable on H200 OpenCL at 2.11 ns/day

---

## 1. Root Cause Hypotheses (ranked by likelihood)

### H1. MACE Float32 Force Evaluation Precision Loss Amplified by Barostat (HIGHEST LIKELIHOOD)

**Evidence:**
- The MACE-OFF JACS paper (Kovacs et al., 2024) explicitly states: "Forces were evaluated in **double precision** and integrated in single precision" for their validated NPT simulations. This is the canonical MACE-OFF validation setup.
- Your system runs MACE in float32 "bypass mode" for a 1.21x speedup. This means forces are computed in single precision, diverging from the validated protocol.
- The low-precision MACE study (Batatia et al., 2025, arXiv:2510.23621) identifies **catastrophic cancellation** as a specific risk during force computation via energy gradients: `F_i = -nabla E` involves subtraction of near-equal quantities, which amplifies float32 rounding errors.
- The same study found that while FP32 inference is generally stable for NVT/NPT, the energy/force deviations from FP64 are O(1) meV / O(10^-2) meV/A. In a hybrid system where the MACE forces must balance against AMBER/TIP3P-FB forces at the ML/MM boundary, even small force errors can create an imbalanced pressure contribution.
- A known MACE issue (ACEsuit/mace#990) documents that downcasting a float64-trained MACE model to float32 for LAMMPS produces **NaN in all thermodynamic quantities from step 1**. While this is a different pathway (compile-time cast vs. runtime bypass), it demonstrates that MACE models have known fragility under precision reduction.
- The MonteCarloBarostat computes acceptance/rejection based on energy difference deltaE before and after coordinate rescaling. If float32 MACE forces produce slightly inaccurate energies, the deltaE calculation can be corrupted, leading to acceptance of unphysical volume moves that push atoms into steric clashes or outside MACE's cutoff.

**Why NVT works but NPT doesn't:** In NVT, small force errors are damped by the Langevin thermostat and do not compound. In NPT, the barostat's MC acceptance criterion is directly sensitive to energy differences -- float32 errors in deltaE corrupt the acceptance probability, potentially accepting large unphysical volume changes.

**Mechanism:** Barostat move -> coordinate rescale -> MACE recomputes energy in float32 -> small rounding error in deltaE -> unphysical volume move accepted -> atom positions become slightly pathological -> next MACE evaluation produces larger errors -> positive feedback loop -> NaN within ~25 ps.

### H2. MACE Neighbor List Not Properly Rebuilt After Barostat Box Rescaling (HIGH LIKELIHOOD)

**Evidence:**
- The MonteCarloBarostat works by "scaling the box vectors and the coordinates of each molecule's center by a factor s" (OpenMM theory docs). This changes the periodic box dimensions.
- MACE-OFF24-medium uses a **6 A cutoff radius**. The TorchForce receives updated box vectors after each barostat move via `setUsesPeriodicBoundaryConditions(True)`.
- However, MACE's internal neighbor list construction happens inside the PyTorch forward pass. When the box is rescaled, the neighbor list must be rebuilt from scratch with the new box vectors. If MACE computes the neighbor list using the old box vectors (from before the barostat rescale) or if the minimum image convention is applied inconsistently, atoms near the cutoff boundary can be missed or double-counted.
- The neighbor list artifacts paper (Goniakowski et al., JCTC 2023) demonstrates that **missed nonbonded interactions due to stale neighbor lists cause errors in the pressure tensor, which in NPT drive incorrect barostat-induced box rescaling**. This creates a positive feedback loop: missed interactions -> wrong pressure -> wrong rescaling -> more missed interactions -> crash.
- The openmmml `createMixedSystem()` source code (mlpotential.py) contains **no explicit handling for neighbor list management or barostat compatibility**. It simply calls `self._impl.addForces()` and leaves the TorchForce to handle PBC internally.
- openmm-ml issue #52 documents that "the PBC is not replicated for the ML portion of the system" in mixed systems, causing "the box blowing up" -- precisely the behavior you observe.

**Why NVT works:** No box rescaling occurs in NVT, so the neighbor list computed at the start of each step is valid for that step's box dimensions. The box never changes, so there is no inconsistency.

### H3. MonteCarloBarostat Molecular Reimaging Disrupts MACE Atom Ordering (MEDIUM LIKELIHOOD)

**Evidence:**
- OpenMM issue #4032 documents that the MonteCarloBarostat "forces the center of each molecule to stay in the main cell" -- it reimages molecules after each volume move.
- In a hybrid ML/MM system, the MACE TorchForce operates on a subset of atoms (534 protein atoms). When the barostat reimages molecules, protein atoms at the edge of the periodic box may be wrapped to the other side. If MACE receives discontinuous atom positions (some wrapped, some not), the neighbor list computation will break, producing garbage forces.
- The barostat "modifies particle positions by scaling the centroid of each molecule, then applying the resulting displacement to each particle in the molecule" (OpenMM theory). For the protein, all 534 atoms are one molecule -- the entire protein is translated as a rigid body. If the protein centroid is near a box face, the translation could place some atoms outside the primary cell, and the subsequent reimaging could split the protein across periodic images in a way that confuses MACE's minimum image convention.

**Mitigating factor:** This is less likely for a well-centered protein in an adequately padded box, but becomes more likely as the system equilibrates and the protein diffuses.

### H4. OpenCL Platform-Specific Precision Issue with Barostat (MEDIUM LIKELIHOOD)

**Evidence:**
- OpenMM issue #1651 documents NaN crashes on GTX-1080 with OpenCL that are eliminated by disabling the barostat. The workaround `{'OpenCLDisablePmeStream':'true'}` helps but doesn't fully resolve it.
- Your system uses RTX 5000 Ada with OpenCL (not CUDA). The RTX 5000 Ada is an Ada Lovelace architecture GPU, which may have different OpenCL precision behavior than the GPUs tested by MACE developers (primarily A100s with CUDA).
- OpenMM's OpenCL platform in "single" precision mode stores positions in single precision with a correction array for double precision integration ("mixed" mode). But the TorchForce/MACE interaction happens entirely through the OpenCL->PyTorch bridge, which may not benefit from this correction mechanism.
- The MACE-OFF paper's validated runs used NVIDIA A100 80GB with CUDA, not OpenCL. No MACE NPT validation on OpenCL has been published.

**Why NVT works:** OpenCL precision issues may only manifest when the barostat triggers force recomputation after coordinate rescaling, creating a specific pathway for error accumulation that doesn't exist in NVT.

### H5. Timestep Too Large for NPT Equilibration with ML Potential (LOWER LIKELIHOOD)

**Evidence:**
- Your 1.0 fs timestep is standard for classical MD NPT but may be aggressive for ML potential NPT.
- The MACE stability testing paper (arXiv:2503.11537, 2025) used **0.5 fs for NPT** condensed-phase simulations with MACE models, half of the typical 1.0 fs.
- The low-precision MACE study (arXiv:2510.23621) also used 1 fs for ASE NPT with a Nose-Hoover/Parrinello-Rahman barostat.
- OpenMM issue #3227 (NaN with barostat) was resolved by adjusting hydrogen mass repartitioning, suggesting timestep-related instabilities are a known class of barostat NaN causes.

**Counterargument:** Your 1.0 fs already conservative compared to standard classical MD (2-4 fs with HBonds constraints). The MACE-OFF paper used 1 fs for NVT successfully. But NPT adds perturbation from volume moves.

### H6. Hybrid System ML/MM Energy Discontinuity at Boundary (LOWER LIKELIHOOD)

**Evidence:**
- openmm-torch issue #34 documents protein unfolding in hybrid ML/MM simulations (ANI-2x + AMBER14), though that was NVT.
- When the barostat rescales coordinates, the ML/MM boundary region (where MACE protein atoms interact with classical water) may experience energy discontinuities. The MACE forces on protein surface atoms depend on nearby water molecules only through the AMBER14 cross-terms, not through MACE's neighbor list. A volume change alters these cross-term distances non-smoothly.

**Counterargument:** This should affect both NVT and NPT equally, and NVT is stable. Unless the barostat-specific coordinate rescaling creates a uniquely unfavorable geometry at the boundary.

---

## 2. What the Literature Does

### 2.1. MACE-OFF Paper (Kovacs et al., JACS 2024)

| Parameter | Value |
|-----------|-------|
| Model | MACE-OFF23(M) and MACE-OFF24(M) |
| Force precision | **Double (float64)** |
| Integration precision | Single |
| Timestep | 1 fs (water NVT at 300 K), 2 fs resolution recording |
| NPT barostat | Nose-Hoover + Parrinello-Rahman (via ASE, NOT OpenMM MonteCarloBarostat) |
| Crambin solvated | ~18,000 atoms, 1.6 ns, A100 80GB CUDA |
| Cutoff | 6 A (MACE-OFF24M), 5 A (MACE-OFF23M) |
| Water NPT density | Within 2% of experiment with 6 A cutoff |
| Stability | RMSF < 1 A, no bond breaking, secondary structure intact |

**Critical note:** The paper used ASE's NPT integrator (Nose-Hoover + Parrinello-Rahman), NOT OpenMM's MonteCarloBarostat. This is a fundamentally different pressure coupling scheme: Nose-Hoover/PR is a continuous thermostat/barostat that modifies equations of motion smoothly, while MC barostat makes discrete, potentially large coordinate rescaling moves.

### 2.2. MACE Stability Testing Paper (arXiv:2503.11537, 2025)

| Parameter | Value |
|-----------|-------|
| NPT conditions | 300 K, 1 bar |
| NPT barostat | Monte Carlo barostat (OpenMM) |
| NPT thermostat | Nose-Hoover |
| **NPT timestep** | **0.5 fs** |
| Duration | 0.125 ns production |
| Precision | 32-bit training |
| Stability finding | MACE-OFF23(S) crashed at 44 ps; M and L stable |
| Recommendation | "MACE models with at least size M are recommended" |

**Critical note:** They used 0.5 fs timestep for NPT, half of your 1.0 fs. Also, MACE-OFF23(S) crashed at 44 ps -- similar timescale to your 25 ps crash, though with a different model size.

### 2.3. Low-Precision MACE Study (arXiv:2510.23621, Batatia et al., 2025)

| Parameter | Value |
|-----------|-------|
| ASE NPT integrator | Yes (not OpenMM MC barostat) |
| Timestep | 1 fs |
| Thermostat tau | 100 fs |
| Barostat | Parrinello-Rahman (isotropic stress, effective bulk modulus 2.2 GPa) |
| FP32 NPT stability | "Energies and thermodynamic observables in NVT/NPT MD remain within run-to-run variability" |
| FP32 force error vs FP64 | O(1) meV energy, O(10^-2) meV/A forces |
| Key risk | Catastrophic cancellation in force gradients |

**Critical note:** FP32 NPT was stable but with Parrinello-Rahman (continuous), not MonteCarloBarostat (discrete MC moves). The combination of FP32 + MC barostat has not been validated.

### 2.4. OpenMM 8 ML Potential Paper (Eastman et al., 2024)

All ML potential examples in the paper use **NVT only**. No NPT examples with ML potentials are provided. The paper explicitly notes that best practices for ML potential NPT dynamics are not yet established.

### 2.5. NNP/MM Paper (Galvelis et al., 2023)

All NNP/MM simulations use **NVT at 310 K** with 2 fs timestep. No barostat. No NPT.

### 2.6. OpenMMDL Paper (2025)

Standard classical MD: Monte Carlo barostat, 1 bar, 300 K. No ML potential NPT examples.

### 2.7. Summary: Who Has Actually Run MACE NPT Successfully?

| Group | Barostat | Platform | Precision | Timestep | Status |
|-------|----------|----------|-----------|----------|--------|
| MACE-OFF paper | **Parrinello-Rahman (ASE)** | A100 CUDA | float64 forces | 1 fs | Stable |
| Low-precision study | **Parrinello-Rahman (ASE)** | GPU CUDA | float32 | 1 fs | Stable |
| Stability testing | MC barostat (OpenMM) | GPU | float32 | **0.5 fs** | M/L stable, S crashed |
| **Nobody published** | MC barostat (OpenMM) | OpenCL | float32 | 1 fs | **Untested** |

Your configuration (MC barostat + OpenCL + float32 + 1 fs) is in untested territory.

---

## 3. Recommended Test Matrix

Ordered by likelihood of success and ascending SU cost. Each test should run 50 ps (50,000 steps at 1 fs) to exceed the 25 ps crash point. Use WW domain as the test case.

### Test 1: Switch MACE to float64 (double precision) [HIGHEST PRIORITY]

**Rationale:** The MACE-OFF paper validated NPT with float64 forces. Your float32 bypass mode is the single largest deviation from validated protocol. This directly addresses H1.

**Implementation:**
```python
# In the MACEPotentialImpl or createMixedSystem call:
potential = MLPotential('mace-off24-medium')
system = potential.createMixedSystem(topology, atoms=protein_indices, precision='double')
# OR if using the MACE model directly:
model = torch.load('mace-off24-medium.model').to(dtype=torch.float64)
```

**Expected effect:** ~2x slower inference but eliminates float32 catastrophic cancellation in force gradients. This is what the MACE authors actually use.

**SU cost:** ~50 SU on RTX 5000 Ada (15 SU/hr x ~3.3 hr for 50 ps at half speed due to float64).

### Test 2: Reduce barostat frequency from 25 to 100 steps [HIGH PRIORITY]

**Rationale:** Fewer MC volume moves = fewer opportunities for force/energy recomputation errors to accumulate. Reduces the rate at which precision-related errors enter the system. Also reduces the frequency of neighbor list disruption (H2).

**Implementation:**
```python
barostat = MonteCarloBarostat(1.0*atmosphere, 300*kelvin, 100)  # was 25
system.addForce(barostat)
```

**Expected effect:** 4x fewer barostat moves. System has more time to relax between volume changes. Pressure equilibration will be slower but should be more stable.

**SU cost:** Negligible difference from baseline (~15 SU for 50 ps at current throughput).

### Test 3: Reduce timestep to 0.5 fs [HIGH PRIORITY]

**Rationale:** The MACE stability testing paper used 0.5 fs for NPT. Your 1.0 fs may amplify force errors per step. Smaller timestep = smaller per-step position changes = less chance of crossing neighbor list boundaries or accumulating errors.

**Implementation:**
```python
integrator = LangevinMiddleIntegrator(300*kelvin, 1.0/picosecond, 0.0005*picoseconds)  # was 0.001
# Note: need 100,000 steps for 50 ps instead of 50,000
```

**Expected effect:** Halves position displacement per step. Reduces discretization error. Wall-clock time doubles but each step is more stable.

**SU cost:** ~30 SU (same wall-clock as test 1 since 2x more steps).

### Test 4: NVT equilibration first, then switch to NPT [MEDIUM PRIORITY]

**Rationale:** Standard MD best practice is to equilibrate NVT first to stabilize temperature before introducing pressure coupling. Your current protocol may be introducing barostat moves on a system that hasn't thermally equilibrated, creating large deltaE values that corrupt barostat acceptance.

**Implementation:**
```python
# Phase 1: NVT equilibration (100 ps)
integrator_nvt = LangevinMiddleIntegrator(300*kelvin, 1.0/picosecond, 0.001*picoseconds)
simulation_nvt = Simulation(topology, system_nvt, integrator_nvt, platform)
simulation_nvt.step(100000)  # 100 ps NVT

# Phase 2: NPT production
# Save NVT state, create new simulation with barostat
state = simulation_nvt.context.getState(getPositions=True, getVelocities=True)
system_npt = copy.deepcopy(system)
system_npt.addForce(MonteCarloBarostat(1.0*atmosphere, 300*kelvin, 100))
simulation_npt = Simulation(topology, system_npt, integrator_npt, platform)
simulation_npt.context.setState(state)
simulation_npt.step(50000)  # 50 ps NPT
```

**SU cost:** ~25 SU total.

### Test 5: Combine tests 1+2+3 (float64 + freq=100 + dt=0.5 fs) [HIGH PRIORITY, DEFINITIVE]

**Rationale:** If individual tests are inconclusive, the combination of all three conservative measures should reproduce the validated MACE-OFF protocol as closely as possible in OpenMM.

**Implementation:**
```python
model = load_mace_model('mace-off24-medium', dtype=torch.float64)
integrator = LangevinMiddleIntegrator(300*kelvin, 1.0/picosecond, 0.0005*picoseconds)
barostat = MonteCarloBarostat(1.0*atmosphere, 300*kelvin, 100)
```

**SU cost:** ~60 SU (float64 + 2x steps).

### Test 6: Use OpenMM CUDA platform instead of OpenCL [MEDIUM PRIORITY]

**Rationale:** All published MACE NPT runs used CUDA. OpenCL has documented NaN issues with barostat (issue #1651). RTX 5000 Ada supports CUDA natively -- if CUDA works with openmm-torch, this eliminates an entire class of platform-specific bugs.

**Implementation:**
```python
platform = Platform.getPlatformByName('CUDA')
properties = {'CudaPrecision': 'mixed'}  # double integration, single forces
```

**Note:** You mentioned "CUDA disabled due to prior compatibility issues." This test requires investigating whether those issues have been resolved. If openmm-torch + MACE + CUDA works on RTX 5000 Ada, this is strongly preferable to OpenCL for NPT.

**SU cost:** ~15 SU for 50 ps (CUDA may be faster than OpenCL).

### Test 7: Disable PME stream on OpenCL [LOW PRIORITY, QUICK]

**Rationale:** OpenMM issue #1651 workaround. May help if the NaN is triggered by asynchronous PME computation on OpenCL.

**Implementation:**
```python
platform = Platform.getPlatformByName('OpenCL')
properties = {'OpenCLDisablePmeStream': 'true'}
```

**SU cost:** ~15 SU.

### Test 8: MonteCarloAnisotropicBarostat instead of isotropic [LOW PRIORITY]

**Rationale:** The anisotropic barostat rescales each box dimension independently. For a solvated protein in an orthorhombic box, this may produce smaller per-move coordinate displacements than isotropic scaling, reducing the magnitude of neighbor list disruption.

**Implementation:**
```python
from openmm import MonteCarloAnisotropicBarostat, Vec3
barostat = MonteCarloAnisotropicBarostat(
    Vec3(1.0, 1.0, 1.0)*atmosphere,  # pressure in x, y, z
    300*kelvin,
    True, True, True,  # scale x, y, z independently
    100  # frequency
)
```

**SU cost:** ~15 SU.

### Diagnostic Test Matrix Summary

| Test | Change | Target Hypothesis | SU Cost | Priority |
|------|--------|-------------------|---------|----------|
| 1 | MACE float64 | H1 (precision) | 50 | HIGHEST |
| 2 | Barostat freq=100 | H1, H2 | 15 | HIGH |
| 3 | dt=0.5 fs | H5 (timestep) | 30 | HIGH |
| 4 | NVT-first protocol | H1, H5 | 25 | MEDIUM |
| 5 | 1+2+3 combined | All | 60 | DEFINITIVE |
| 6 | CUDA platform | H4 (OpenCL) | 15 | MEDIUM |
| 7 | DisablePmeStream | H4 (OpenCL) | 15 | LOW |
| 8 | Anisotropic barostat | H2, H3 | 15 | LOW |

**Recommended execution order:** Test 1 first (most likely fix). If stable, you have your answer. If unstable, run tests 2 and 3 in parallel. If still unstable, run test 5 (belt-and-suspenders). Test 6 if CUDA compatibility can be quickly verified.

**Total SU budget for full matrix:** ~240 SU on RTX 5000 Ada = 16 GPU-hours = negligible.

---

## 4. Alternative Approaches

If standard NPT fixes do not resolve the issue:

### 4A. Use ASE NPT Integrator Instead of OpenMM MonteCarloBarostat

**Rationale:** All successful MACE NPT runs in the literature use ASE's NPT integrator with Nose-Hoover thermostat + Parrinello-Rahman barostat. This is a **continuous** pressure coupling scheme that modifies equations of motion smoothly, unlike OpenMM's MC barostat which makes discrete coordinate rescaling jumps.

**Implementation:** Run MACE NPT through ASE instead of OpenMM. This sacrifices OpenMM's GPU-accelerated classical forces for the water, but guarantees compatibility with validated MACE NPT protocols.

```python
from ase.md.npt import NPT as ASE_NPT
from mace.calculators import MACECalculator

calc = MACECalculator(model_paths='mace-off24-medium.model', device='cuda', default_dtype='float64')
atoms.calc = calc

dyn = ASE_NPT(atoms, timestep=1.0*units.fs, temperature_K=300,
              ttime=100*units.fs,  # thermostat time constant
              pfactor=(100*units.fs)**2 * 2.2e9*units.Pascal,  # barostat
              externalstress=1.01325e5*units.Pascal)  # 1 atm
```

**Drawback:** Pure ASE NPT means the entire system (protein + water) runs through MACE, which is orders of magnitude slower than the hybrid approach. Only viable for very small test systems.

### 4B. NVT Production with Post-Hoc Density Correction

**Rationale:** If NPT cannot be stabilized, run all production in NVT and apply post-hoc corrections for the missing pressure coupling. For protein conformational sampling (the actual scientific goal), NVT and NPT produce very similar structural ensembles for small solvated proteins. The density difference is typically <2%.

**Implementation:** Use NVT (already validated stable) for all production. Report that simulations were run in NVT ensemble. For any density-dependent observables, apply standard thermodynamic corrections.

**Literature support:** Many protein MD studies use NVT for production after NPT equilibration of the box size. The MACE-OFF paper's Crambin stability assessment used NVT.

### 4C. Fixed-Box NPT via Pre-Equilibrated Box

**Rationale:** Equilibrate the box dimensions using classical MD (AMBER14/TIP3P-FB) in NPT, then freeze the box dimensions and run MACE hybrid in NVT with the pre-equilibrated box.

**Implementation:**
1. Run classical AMBER14/TIP3P-FB NPT for 1 ns to equilibrate box dimensions
2. Extract final box dimensions
3. Run MACE hybrid in NVT with those fixed box dimensions

**Advantage:** Gets the correct density without needing MACE to handle barostat moves.

### 4D. Implement Custom Berendsen-Like Pressure Coupling

**Rationale:** Instead of MC barostat's discrete jumps, implement a weak Berendsen-style continuous box rescaling as a CustomIntegrator in OpenMM. Scale box vectors by a small factor every N steps based on the virial pressure.

**Warning:** Berendsen does not produce a correct NPT ensemble, but it does give the correct average density. Suitable for equilibration but not production.

### 4E. Reduce MACE Protein Region + Expand Classical Buffer

**Rationale:** If the crash is caused by the ML/MM boundary interaction during barostat moves, reduce the number of atoms handled by MACE (e.g., only backbone heavy atoms or only the core hydrophobic residues) and expand the classical description to include surface residues and nearby water.

**Drawback:** Defeats the purpose of using MACE for the full protein.

---

## 5. References

### OpenMM Issues
- [#3227: Particle is NaN when barostat is used](https://github.com/openmm/openmm/issues/3227) -- HMR=1.5 fix, SRC kinase system, freq=25
- [#1651: NaN on GTX-1080 with OpenCL](https://github.com/openmm/openmm/issues/1651) -- OpenCL-specific, DisablePmeStream workaround
- [#1854: CustomExternalForce + MonteCarloBarostat](https://github.com/openmm/openmm/issues/1854) -- barostat rejection due to restraint energy
- [#4032: MonteCarloBarostat reimages molecules](https://github.com/openmm/openmm/issues/4032) -- molecule center forced into main cell
- [#3723: Barostat scaling of constrained groups](https://github.com/openmm/openmm/issues/3723) -- molecule-based vs atom-based scaling
- [#3623: Full nonbonded in NPT](https://github.com/openmm/openmm/issues/3623) -- NoCutoff incompatible with MC barostat
- [#3077: Adaptive barostat interval](https://github.com/openmm/openmm/issues/3077) -- unimplemented enhancement request
- [#1786: OpenCL double precision misreported](https://github.com/openmm/openmm/issues/1786) -- platform precision detection bug

### openmm-ml / openmm-torch Issues
- [openmm-ml #42: Periodic box setup](https://github.com/openmm/openmm-ml/issues/42) -- PBC not properly transmitted to ML potential
- [openmm-ml #52: createMixedSystem whole waterbox](https://github.com/openmm/openmm-ml/issues/52) -- "PBC not replicated for ML portion, box blows up"
- [openmm-torch #34: Protein unfolding in hybrid ML/MM](https://github.com/openmm/openmm-torch/issues/34) -- ANI-2x + AMBER14, wontfix
- [openmm-torch #33: Neighbor list accessibility](https://github.com/openmm/openmm-torch/issues/33) -- no solution for external neighbor list access
- [openmm-torch #134: OpenMMException with TorchForce](https://github.com/openmm/openmm-torch/issues/134)

### MACE Issues
- [ACEsuit/mace #990: NaN when float64 model downcast to float32](https://github.com/ACEsuit/mace/issues/990) -- confirmed: float32 cast produces NaN
- [ACEsuit/mace discussions #69: OpenMM/LAMMPS integration status](https://github.com/ACEsuit/mace/discussions/69) -- periodic systems "not yet functional" (Feb 2023, outdated)

### Papers
- Kovacs et al., "MACE-OFF: Short-Range Transferable Machine Learning Force Fields for Organic Molecules," JACS 2024. [DOI: 10.1021/jacs.4c07099](https://pubs.acs.org/doi/10.1021/jacs.4c07099). **Key finding:** float64 forces, ASE NPT integrator, 6A cutoff, Crambin 18k atoms stable.
- Eastman et al., "OpenMM 8: Molecular Dynamics Simulation with Machine Learning Potentials," J. Phys. Chem. B 2024. [PMC10846090](https://pmc.ncbi.nlm.nih.gov/articles/PMC10846090/). **Key finding:** All ML examples NVT only.
- "Basic stability tests of machine learning potentials for molecular simulations in computational drug discovery," arXiv:2503.11537 (2025). **Key finding:** 0.5 fs timestep for NPT, MACE-OFF23(S) crashed at 44 ps, M/L stable.
- "Speeding Up MACE: Low-Precision Tricks for Equivariant Force Fields," arXiv:2510.23621 (Batatia et al., 2025). **Key finding:** FP32 NPT stable with Parrinello-Rahman; catastrophic cancellation risk in force gradients.
- Goniakowski et al., "Neighbor List Artifacts in Molecular Dynamics Simulations," JCTC 2023. [PMC10720336](https://pmc.ncbi.nlm.nih.gov/articles/PMC10720336/). **Key finding:** Stale neighbor lists cause pressure errors -> incorrect barostat rescaling -> system instability.
- Galvelis et al., "NNP/MM: Accelerating Molecular Dynamics Simulations with Machine Learning Potentials and Molecular Mechanics," 2023. [PMC10577237](https://pmc.ncbi.nlm.nih.gov/articles/PMC10577237/). **Key finding:** NNP/MM uses NVT only, 2 fs timestep.

### Documentation
- [OpenMM User Guide: Standard Forces (MonteCarloBarostat theory)](https://docs.openmm.org/latest/userguide/theory/02_standard_forces.html)
- [OpenMM Platform-Specific Properties](https://docs.openmm.org/latest/userguide/library/04_platform_specifics.html)
- [MACE OpenMM Interface docs](https://mace-docs.readthedocs.io/en/latest/guide/openmm.html)
- [openmmml MACEPotentialImpl API](https://openmm.github.io/openmm-ml/dev/generated/openmmml.models.macepotential.MACEPotentialImpl.html)
- [openmm-ml source: mlpotential.py](https://github.com/openmm/openmm-ml/blob/main/openmmml/mlpotential.py)
- [openmm-torch README](https://github.com/openmm/openmm-torch/blob/master/README.md)

---

## 6. Executive Summary (UPDATED 2026-04-28 with experimental results)

**Original hypothesis (H1, f32 precision) was PARTIALLY CONFIRMED but NOT SUFFICIENT.**
f64 MACE delayed the crash from ~5 ps to ~17 ps but did not prevent it.

**Actual root cause identified via source code analysis:** The openmm-ml `_computeMACE`
callback does NOT apply minimum-image wrapping to protein positions before building
the neighbor list. During MC barostat trial moves, coordinate reimaging can place
atoms on opposite sides of the periodic box, producing garbage neighbor lists and
pathological MACE forces → NaN. This is a geometric bug, not a precision issue.

**Production path:** NVT with pre-equilibrated box (classical NPT → MACE NVT).
This is scientifically valid for S2 order parameters and matches the approach
used by the NNP/MM paper (Galvelis 2023, JCTC).

**Optional NPT recovery:** A ~3-line wrapping fix may restore NPT viability.
Untested — requires ~10 SU for one diagnostic.

See `npt_investigation_results.md` for full experimental data, source code
analysis, literature survey, and production plan.
