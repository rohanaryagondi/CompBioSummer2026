---
agent: ML Force Field & Simulation Engineering Expert (mlffeng)
round: 2
date: 2026-04-14
type: proposal
proposal_id: alpha-m-simulation
---

# Proposal: Alpha-M -- The MLFF Biomolecular Crash Test

## Proposing Agent

**Dr. ML Force Field & Simulation Engineering Expert (mlffeng)**
Senior MD simulation engineer (15+ years molecular dynamics, 5+ years ML force
fields). Practitioner-first perspective: force fields are judged by whether their
trajectories match experiment, not by loss on a DFT benchmark. This proposal
covers the simulation engineering, MLFF selection, compute architecture, NMR
back-calculation pipeline, and risk management for Alpha-M. It is designed to
be picked up and executed by a competent MD practitioner on day one.

---

## Problem Statement

Machine learning force fields (MLFFs) are validated almost exclusively by comparing
predicted energies and forces against density functional theory (DFT) reference
calculations. Models achieving low RMSE on DFT test sets are declared "accurate,"
yet nobody has systematically tested whether these models produce molecular dynamics
trajectories that agree with *experimental* protein observables -- NMR order
parameters, J-couplings, chemical shifts, and SAXS profiles. This is the same
"reality gap" that UniFFBench (Mannan et al., arXiv 2025) exposed for materials
science MLFFs, where top-performing models on computational benchmarks failed
against experimental measurements of lattice constants, elastic moduli, and phonon
spectra. For biomolecular MLFFs, the situation is worse: classical force fields
like AMBER ff19SB and CHARMM36m have been refined against NMR data for 30 years,
while MLFFs have never been tested against these data. Alpha-M fills this gap with
the first systematic benchmark of multiple MLFFs against multiple experimental
observables across multiple proteins.

---

## Vision

After this project succeeds, the biomolecular MLFF community has a clear, quantitative
answer to the question: "Do ML force fields produce physically realistic protein
dynamics?" Every MLFF developer will be able to compare their model against the
Alpha-M benchmark set and know exactly how it performs on S2 order parameters,
J-couplings, chemical shifts, and SAXS profiles relative to experiment and relative
to classical baselines. The benchmark becomes the standard evaluation for new MLFFs,
analogous to how ProteinGym standardized variant effect prediction or how MatBench
standardized materials property prediction. The community shifts from DFT-only
validation to experiment-grounded validation, accelerating the development of MLFFs
that actually work for real biological applications.

---

## Background and Evidence

### Current State of the Art

**Classical force field benchmarking is mature.** Lindorff-Larsen et al. (JCTC 2012)
established a systematic benchmark of 4 classical force fields against 524 NMR
measurements across 9 proteins. Robustelli et al. (PNAS 2018) expanded this to 21
systems and >9,000 experimental data points in developing a99SB-disp. Smith et al.
(J. Phys. Chem. B 2024) established the convergence protocol for S2 order parameters:
100 replicas of 30 ns each across 6 proteins, finding AMBER ff14SB achieves R2 = 0.62
and CHARMM36m R2 = 0.51. These papers define the gold standard for force field
validation.

**MLFF benchmarking is computational only.** The MACE-OFF24 paper (Kovacs et al.,
JACS 2025) validates against Ala3 3J(HN,Ha) couplings (5.70 Hz vs experiment 5.68 Hz)
and crambin power spectra, but does not compute S2, chemical shifts for proteins, or
SAXS profiles. SO3LR (Frank et al., JACS 2026) validates lipid tail order parameters
and polyalanine helix stability, but no protein backbone NMR observables. AI2BMD
(Li et al., Nature 2024) is the only MLFF to compare protein 3J-couplings against
NMR (r = 0.81 for dipeptides), but only on dipeptide fragments, not folded proteins.
AceFF-2.0 (Acellera, 2026) focuses entirely on drug-like molecules.

**No systematic multi-MLFF benchmark against experimental protein observables exists.**
This is the gap. The closest analogue is UniFFBench for materials (Mannan et al.,
arXiv 2508.05762), which benchmarked CHGNet, M3GNet, MACE, MatterSim, SevenNet,
and Orb against experimental lattice constants, elastic moduli, and phonon spectra,
revealing "a substantial reality gap" where "models achieving impressive performance
on computational benchmarks often fail when confronted with experimental complexity."

### Recent Developments That Enable This

1. **Production-ready biomolecular MLFFs (2024-2026):** MACE-OFF24(M) demonstrated
   1.6 ns stable crambin simulation (Kovacs et al., JACS 2025). SO3LR demonstrated
   3 ns crambin, 500 ps glycoprotein at 48K atoms (Frank et al., JACS 2026). AI2BMD
   showed hundreds of nanoseconds on dipeptides (Li et al., Nature 2024). AceFF-2.0
   achieved 36.7 ns/day on RTX 4090 for small molecules (Acellera, 2026).

2. **OpenMM-ML v1.5 (2026):** Unified interface for running MACE-OFF24(M), AceFF-2.0,
   and other MLFFs within the same simulation engine, enabling fair comparison with
   classical baselines. Supports mixed ML/MM systems via createMixedSystem().

3. **NMR back-calculation pipeline maturity:** SPARTA+ (Shen & Bax, 2010) for chemical
   shifts, Karplus equations (Vuister & Bax, 1993) for J-couplings, Lipari-Szabo
   S2 from trajectory autocorrelation, Pepsi-SAXS (Grudinin et al., 2017) for SAXS.
   SPyCi-PDB (Forman-Kay lab, 2024) provides a unified Python interface.

4. **H200 GPUs with 141 GB HBM3e:** 4.8 TB/s memory bandwidth enables MLFF inference
   at ~0.39 ns/day for ~18K atom systems (MACE-OFF24(M)), making 50 ns simulations
   feasible in ~125 GPU-days.

5. **S2 convergence protocol established:** Smith et al. (J. Phys. Chem. B 2024)
   showed that 10-20 replicas of 20-30 ns achieve R2 reproducibility >= 0.95, making
   multi-replica shorter simulations the practical path for MLFF speed constraints.

### Key Prior Work

1. **Kovacs et al. (JACS 2025).** MACE-OFF24(M): 1.6 ns crambin, Ala3 3J(HN,Ha) =
   5.70 Hz (exp: 5.68 Hz). Native OpenMM-ML integration. Speed: 2.2 x 10^6 steps/day
   on A100 for solvated systems (~0.3 ns/day at 1 fs for ~18K atoms).

2. **Frank et al. (JACS 2026).** SO3LR: 3 ns crambin (25K atoms), 2.6 ns/day at
   10K atoms on H100 via JAX-MD. Lipid tail order parameters matched NMR. Scales to
   200K atoms on single GPU.

3. **Li et al. (Nature 2024).** AI2BMD: Protein fragmentation into dipeptides with
   ViSNet ML potential. 3J(HN,Ha) Pearson r = 0.81 vs experiment (classical MM: r =
   0.59). Hundreds of nanoseconds on dipeptides. Custom framework.

4. **Smith et al. (J. Phys. Chem. B 2024).** S2 convergence: 100 replicas x 30 ns
   for 6 proteins with AMBER ff14SB (R2 = 0.62) and CHARMM36m (R2 = 0.51). Ensemble
   of N = 20 replicas achieves average reproducibility R2 >= 0.95.

5. **Robustelli et al. (PNAS 2018).** a99SB-disp benchmark: 21 systems, >9,000
   experimental data points, 6 force fields. Established the standard for systematic
   force field validation against NMR.

6. **Mannan et al. (arXiv 2508.05762, 2025).** UniFFBench: Benchmarked 6 materials
   MLFFs against experimental properties, revealing "a substantial reality gap."
   Our direct narrative predecessor.

7. **TEA Challenge 2023 (Chemical Science 2025).** Crash-tested MLFFs on peptides and
   interfaces. Kernel-based models (SOAP/GAP, FCHL19*) failed to sustain 1 ns
   dynamics. Equivariant architectures (MACE, SO3krates) were stable. Established
   that simulation stability cannot be assumed.

8. **Waibl et al. (JCIM 2025).** ANI-2x produces amorphous solid water. MACE-OFF23(S)
   failed at 44 ps. MACE-OFF23(M/L) substantially more stable. Critical guidance on
   model size selection.

9. **Shen & Bax (J. Biomol. NMR 2010).** SPARTA+: Backbone chemical shift prediction
   from structure. CA RMSE 1.09 ppm, CB RMSE 0.94 ppm, N RMSE 2.45 ppm, HN RMSE
   0.49 ppm, HA RMSE 0.25 ppm. Trained on 580 proteins.

10. **Grudinin et al. (Acta Cryst. D 2017).** Pepsi-SAXS: 7-36x faster than CRYSOL/
    FoXS with comparable accuracy. Essential for trajectory-scale SAXS computation.

---

## Proposed Approach

### Overview

Alpha-M benchmarks 3 production-ready MLFFs (MACE-OFF24(M), SO3LR, AI2BMD) and 2
classical baselines (AMBER ff19SB, CHARMM36m) on 7 proteins spanning diverse folds
and sizes, comparing 50 ns NVT trajectories against experimental NMR observables
(S2 order parameters, 3J-couplings, backbone chemical shifts) and SAXS profiles.
The study uses a standardized system preparation pipeline (PDBFixer), matched
simulation conditions (1 fs, Langevin 300 K, NVT), and a unified analysis pipeline
(SPARTA+, ShiftX2, Karplus equations, Pepsi-SAXS). BioEmu ensembles are included as
a non-MD comparator for Gamma integration.

### Method Details

#### Component 1: Final MLFF Selection and Justification

**Primary MLFFs (3 methods):**

**1. MACE-OFF24(M) [Primary MLFF]**
- Version: MACE-OFF24 Medium; mace v0.3.13; OpenMM-ML v1.5 ('mace-off24-medium')
- License: MIT (ACEsuit/mace, GitHub)
- Architecture: Higher-order equivariant message passing with many-body interactions
- Training: SPICE v2 dataset; 6 Angstrom interaction cutoff
- Engine: OpenMM-ML (native)
- Protein readiness: 1.6 ns crambin (backbone RMSF <1 A, no bond breaking), Ala3
  3J-coupling validated (Kovacs et al., JACS 2025)
- Speed on H200 (estimated): ~0.39-0.40 ns/day for ~18K atom system (crambin-like);
  ~1.3 ns/day for ~5K atom system
- Known failure modes: MACE-OFF23(S) showed vdW repulsion anomalies below 0.12 nm
  and failed at 44 ps. Medium model substantially more stable. No known failures of
  MACE-OFF24(M) to date.
- Why included: Best overall candidate. Native OpenMM-ML integration ensures fairest
  possible comparison with classical baselines. Well-documented protein simulations.

**2. SO3LR [Second MLFF]**
- Version: v1.0 (Frank et al., JACS 2026); general-molecular-simulations/so3lr
- License: CC-BY 4.0
- Architecture: SO3krates equivariant neural network + universal pairwise force fields
  (repulsion, electrostatics, dispersion)
- Training: 4 million neutral and charged molecular complexes at PBE0+MBD level
- Engine: JAX-MD (no direct OpenMM-ML integration)
- Protein readiness: 3 ns crambin (25K atoms), 500 ps glycoprotein (48K atoms);
  scales to 200K atoms (Frank et al., 2026)
- Speed on H200 (estimated): ~2.6-3.0 ns/day for ~10K atoms; ~0.5-1.3 ns/day for
  ~25K atoms
- Known failure modes: Curved carbon systems have increased errors. Glycoprotein
  N-linkage sampled only 1/3 dihedral conformations in 500 ps.
- Why included: Fastest of the three primary MLFFs. Different architecture from MACE.
  Demonstrated on largest protein systems. JAX-MD engine provides diversity in
  simulation framework comparison.

**3. AI2BMD [Third MLFF]**
- Version: Published Nature 2024 (Li et al.); GitHub microsoft/AI2BMD
- License: MIT
- Architecture: Protein fragmentation into dipeptides; each fragment evaluated by
  ViSNet (geometry modeling foundation model)
- Training: 20 million DFT snapshots of dipeptide fragments (largest biomolecular
  DFT dataset)
- Engine: Custom framework (not OpenMM-ML compatible)
- Protein readiness: Hundreds of nanoseconds on dipeptides; protein folding/unfolding
  demonstrated on full proteins >10,000 atoms (Li et al., Nature 2024)
- Speed on H200 (estimated): ~0.5-2.0 ns/day depending on protein length and
  fragment parallelization
- Known failure modes: Fragmentation approach ignores inter-fragment correlation for
  fragments >1 residue apart. Quality depends on physical reasonableness of
  fragmentation scheme.
- Why included: Only MLFF with published protein NMR validation (3J on dipeptides,
  r = 0.81). Fundamentally different architecture (fragmentation vs full system).
  Its inclusion tests whether ab initio-quality per-residue accuracy translates to
  folded-protein observable accuracy.

**Why these 3 (and not others):**
- Together they span 3 different architectures (equivariant message passing, neural
  network + universal pairwise, fragmentation + ViSNet) and 3 different simulation
  engines (OpenMM-ML, JAX-MD, custom). This maximizes scientific insight: any pattern
  that holds across all 3 is robust; any divergence is informative.
- ANI-2x is DISQUALIFIED: produces amorphous solid water (Waibl et al., JCIM 2025).
- LiTEN-FF is immature: 166-atom chignolin is the largest tested protein; no OpenMM
  integration; 10 GitHub stars, 0 issues.
- GEMS is partially closed-source: full simulation stack not publicly available;
  cannot be included in a reproducible benchmark.
- AceFF-2.0 is a strong stretch candidate (native OpenMM-ML, fastest MLFF at ~36.7
  ns/day for small molecules) but has no published protein simulation data. Include
  in expanded scope if Phase 1 stability tests succeed.
- Allegro is Tier 2: LAMMPS-only for production, no OpenMM-ML native support for
  proteins. Include in expanded scope if compute budget allows.

**Classical Baselines (2 methods):**

**1. AMBER ff19SB + TIP3P**
- The current-generation AMBER protein force field (Tian et al., JCTC 2020)
- Run in OpenMM 8.4+ for direct engine comparison with MACE-OFF24(M)
- TIP3P water (standard; enables direct comparison with published benchmarks)
- 2 fs timestep with SHAKE constraints on hydrogen bonds (standard protocol)
- Expected performance: S2 R2 ~ 0.62 (Smith et al., 2024); well-calibrated
  chemical shifts

**2. CHARMM36m + TIP3P**
- Widely used alternative to AMBER (Huang et al., JCTC 2017)
- Run in OpenMM 8.4+ with CHARMM-GUI topology files
- 2 fs timestep with SHAKE constraints
- Expected performance: S2 R2 ~ 0.51 (Smith et al., 2024); slight secondary
  structure biases known
- Inclusion enables the question: "Do MLFFs fall between AMBER and CHARMM, or
  outside both?"

**Non-MD Comparator: BioEmu Ensembles (for Gamma Integration)**
- BioEmu (Jing et al., Science 2025): generative model producing equilibrium
  conformational ensembles from sequence alone
- MIT licensed, pip-installable, H200-compatible
- Generate 1,000-10,000 conformations per protein, compute NMR back-calculations
  from ensemble
- Compute cost: ~100-200 GPU-hours for 7 proteins (trivial relative to MD budget)
- Purpose: Bridges Alpha-M to Gamma by asking "Do ML-generated ensembles produce
  comparable experimental observables to ML-simulated trajectories?"

#### Component 2: Protein Benchmark Set (7 Proteins, MVP)

**Selection rationale:** These 7 proteins were chosen to maximize NMR data richness,
fold diversity, size range, and overlap with established classical FF benchmarks.
All have high-resolution crystal structures (<=2.0 A), extensive BMRB depositions,
and prior use in Lindorff-Larsen (2012), Robustelli (2018), or Smith (2024) benchmark
studies. Four (ubiquitin, GB3, barnase, T4 lysozyme) overlap with ProteinGym DMS
assays, enabling Gamma+Alpha-M integration.

| # | Protein | PDB | Res. | Residues | Solvated Atoms (est.) | Fold | Key NMR Data | ProteinGym |
|---|---------|-----|------|----------|----------------------|------|-------------|-----------|
| 1 | Ubiquitin | 1UBQ | 1.80 A | 76 | ~10,000 | alpha/beta | S2, shifts, 3J, RDC | Yes |
| 2 | GB3 | 2OED | 1.10 A | 56 | ~8,000 | beta | S2, shifts, 3J, 36 RDC sets | Yes |
| 3 | HEWL | 1IEE | 0.94 A | 129 | ~15,000 | alpha+beta | S2, shifts, 3J, SAXS | No |
| 4 | BPTI | 5PTI | 1.00 A | 58 | ~8,000 | beta-rich | S2, shifts, 3J | No |
| 5 | Barnase | 1BNR | 1.50 A | 110 | ~13,000 | alpha/beta | S2, methyl S2, shifts | Yes |
| 6 | T4 Lysozyme | 107L | 1.70 A | 164 | ~20,000 | alpha | S2, shifts | Yes |
| 7 | Crambin | 1CRN | 0.54 A | 46 | ~18,000 | alpha/beta | CS, B-factors | No |

Total unique observables across 7 proteins (estimated from BMRB entries):
- Chemical shifts: ~4,000-5,000 backbone shift measurements
- J-couplings: ~400-600 3J(HN,Ha) measurements
- S2 order parameters: ~300-500 backbone NH S2 values (6 of 7 proteins)
- SAXS: 1 protein (HEWL via SASBDB SASDUE4 consensus data)

**Stretch goal (expand to 15 proteins):** Add RNase H, Cyclophilin A, SH3 domain,
Chignolin, alpha-Synuclein (IDP), Protein L, alpha-3D, Flavodoxin. See bioval
R01 for full Tier A/B/C classification.

#### Component 3: Simulation Protocol (Execution-Ready)

**3.1 System Preparation Pipeline (Identical for All Methods)**

Step 1. Download crystal structure from PDB (rcsb.org)
Step 2. Remove alternate conformations (keep highest occupancy)
Step 3. Remove crystallographic waters
Step 4. Add missing residues and atoms using PDBFixer (OpenMM utility, v1.9+)
Step 5. Assign protonation states at pH 7.0 using PDBFixer (propka3-based)
Step 6. Solvate with cubic water box extending 12 Angstroms from protein surface
  - Classical baselines: TIP3P water model (PDBFixer addSolvent model='tip3p')
  - MLFFs: Use the same solvated coordinates but with ML potential for all
    interactions (ML water, not TIP3P -- this is itself a testable difference)
Step 7. Add counterions (Na+/Cl-) to neutralize and set ionic strength to 150 mM
  - PDBFixer addSolvent(ionicStrength=0.15)
Step 8. Save prepared system as PDB file for all methods to start from

**Critical design decision -- water treatment for MLFFs:** MLFFs compute all
interactions (including water-water and water-protein) from the ML potential. This
means MLFF simulations use "ML water" which may differ from TIP3P/SPC/E. This is
by design: the ML potential's water model is part of what we benchmark. For each
MLFF, we also report water radial distribution function g(r) O-O at the end of
equilibration, comparing first peak position to experiment (2.80 A) and coordination
number (~4.5). Any MLFF that fails the water test (no clear first peak, or peak at
wrong position by >0.1 A) is flagged as having a fundamental water model deficiency.

**Alternative (if needed): ML/MM hybrid.** If any MLFF shows catastrophic water
failure, run it in ML/MM mode using OpenMM-ML createMixedSystem() (ML for protein,
TIP3P for water). Report both full-ML and ML/MM results. This is only a fallback.

**3.2 Equilibration Protocol**

**Phase 1: Energy Minimization**
- Method: Steepest descent, 5,000 steps or until energy change <1.0 kJ/mol per step
- If MLFF lacks native minimizer, use conjugate gradient in ASE interface
- Classical baselines: same protocol in OpenMM
- Purpose: Remove steric clashes from PDBFixer-generated coordinates

**Phase 2: NVT Heating (50 ps)**
- Temperature ramp: 100 K to 300 K over 50 ps (linear ramp)
- Langevin integrator, 1 fs timestep, friction coefficient 1.0 ps^-1
- Position restraints on backbone heavy atoms (CA, C, N, O): 1,000 kJ/mol/nm^2
  harmonic restraints
- Purpose: Gradually introduce thermal energy without disrupting structure

**Phase 3: NVT Equilibration with Restraint Release (500 ps)**
- Temperature: 300 K, Langevin integrator, 1 fs, friction 1.0 ps^-1
- Restraint release schedule:
  - 0-100 ps: 500 kJ/mol/nm^2
  - 100-200 ps: 250 kJ/mol/nm^2
  - 200-300 ps: 100 kJ/mol/nm^2
  - 300-400 ps: 50 kJ/mol/nm^2
  - 400-500 ps: 0 kJ/mol/nm^2 (unrestrained)
- Monitor: RMSD vs crystal structure, Rg, temperature, total energy
- **Kill criterion:** If backbone RMSD exceeds 3.0 Angstroms from crystal structure
  during equilibration, the MLFF has destabilized the protein fold. Document as
  finding; do not proceed to production.

**Phase 4: Production NVT (50 ns)**
- Temperature: 300 K (constant)
- Integrator: Langevin, friction coefficient 1.0 ps^-1
- Timestep: 1 fs for all MLFFs and classical baselines
- Coordinate save interval: every 10 ps (5,000 frames per 50 ns trajectory)
- Energy save interval: every 1 ps (for monitoring stability)
- No constraints (MLFFs do not use SHAKE/LINCS -- unconstrained all-atom dynamics)
- Classical baselines: also 1 fs, no SHAKE (for fair comparison; note: classical FFs
  are typically run at 2 fs with SHAKE, but 1 fs without constraints is equally valid
  and ensures identical integrator treatment)

**Production run monitors (automated, checked every 100 steps):**
- Maximum force on any atom: kill if >10^6 kJ/mol/nm
- Minimum non-bonded distance: kill if any pair <0.5 Angstroms
- Energy drift: flag if >10 kJ/mol/ns sustained over 1 ns window
- Backbone RMSD vs starting structure: kill if >5.0 Angstroms
- Temperature fluctuation: flag if <280 K or >320 K sustained over 1 ns

**3.3 Timestep Justification**

**Why 1 fs (not 0.5 fs):** 0.5 fs would double compute cost with no clear benefit.
MACE-OFF24(M), SO3LR, and AI2BMD all demonstrate stable dynamics at 1 fs in published
work. The TEA Challenge showed that instability in MLFFs is caused by model errors
(out-of-distribution configurations), not by timestep integration error. A 0.5 fs
timestep is retained as a fallback for any MLFF-protein combination that shows energy
drift at 1 fs.

**Why not 2 fs:** MLFFs do not use bond constraints (SHAKE/LINCS), so hydrogen
vibrations are not frozen. The highest-frequency motion in the unconstrained system
(O-H stretch, period ~10 fs) requires a timestep of at most ~1 fs for stable
Verlet-type integration. 2 fs without constraints would likely cause instabilities.
AceFF-2.0 has been validated at 2 fs, but this cannot be assumed for other MLFFs.

**Classical baseline exception:** Classical baselines could use 2 fs with SHAKE
(standard protocol), but for strict fairness we use 1 fs without constraints for all
methods. This ensures the only difference is the potential energy function.

**3.4 S2 Order Parameter Protocol (Multi-Replica)**

S2 backbone NH order parameters require special treatment due to convergence challenges
(Smith et al., J. Phys. Chem. B 2024).

**Protocol:**
- Run 10 replicas per protein per MLFF, each 10 ns
- Each replica starts from the same equilibrated structure but with different
  initial velocities (drawn from Maxwell-Boltzmann distribution at 300 K with
  different random seeds)
- Save coordinates every 1 ps (10,000 frames per replica)
- Compute S2 from the last 8 ns of each replica (discard first 2 ns as additional
  equilibration)
- Report: mean S2 across replicas, standard deviation, and the resulting R2 vs
  experiment

**Why 10 replicas x 10 ns (not 20 replicas x 20 ns):** Given MLFF speed constraints
(~0.5 ns/day), 20 replicas x 20 ns = 400 ns per system per MLFF would require 800
GPU-days per system. Smith et al. showed S2 converges within tens of nanoseconds per
replica; the key is having enough replicas. 10 replicas x 10 ns = 100 ns total is a
practical compromise: Smith et al. found N = 10 gives R2 reproducibility of ~0.90.
We document this as a limitation relative to the N = 20 gold standard (R2 >= 0.95).

**Proteins for S2 analysis (4 of 7 MVP):** Ubiquitin, GB3, HEWL, T4 Lysozyme
(all have published S2 reference data). BPTI, barnase, and crambin have fewer
published S2 entries; include if data is available in BMRB.

**3.5 Cross-Engine Fairness**

The fundamental challenge: MACE-OFF24(M) runs in OpenMM, SO3LR in JAX-MD, AI2BMD
in its custom framework. Fair comparison requires controlling all variables except
the force field.

**Controls:**
1. All methods start from identical prepared structures (same PDB after PDBFixer
   processing, same solvation box, same ion placement)
2. All methods use the same integrator type (Langevin), same temperature (300 K),
   same friction coefficient (1.0 ps^-1), same timestep (1 fs)
3. All trajectories are analyzed by the same pipeline (MDAnalysis v2.8+ for
   structural analysis; SPARTA+ and ShiftX2 for shifts; same Karplus parameters
   for J-couplings)
4. Convergence assessment: block-averaged errors computed identically for all methods
5. Classical baselines run in the same OpenMM engine as MACE-OFF24(M) -- this provides
   an engine-controlled comparison for the OpenMM methods

**Engine equivalence validation (once, pre-production):**
- Run AMBER ff19SB on ubiquitin in both OpenMM and GROMACS for 10 ns
- Compare backbone RMSD, Rg, and phi/psi distributions
- If results agree within statistical error (expected), engine differences are
  negligible for equilibrium properties
- This validation is a one-time check (~24 CPU-hours) and establishes precedent

**3.6 Handling Engine-Specific Quirks**

| Engine | Thermostat | Cutoff Handling | Special Notes |
|--------|-----------|-----------------|--------------|
| OpenMM (MACE-OFF, classical) | LangevinMiddleIntegrator | PME for electrostatics (classical); cutoff per MLFF model (6 A for MACE-OFF24) | Native vdW cutoff switching (10-12 A for classical) |
| JAX-MD (SO3LR) | Langevin via JAX-MD API | Universal pairwise for long-range; SO3krates cutoff for short-range | Verify temperature equilibration independently |
| Custom (AI2BMD) | Custom Langevin | Fragmentation handles cutoffs implicitly | Fragment boundary effects documented |

**Electrostatics for MLFFs:** MLFFs handle electrostatics differently from classical
PME. MACE-OFF24(M) uses a 6 A cutoff for the ML potential. SO3LR includes explicit
universal pairwise long-range electrostatics. AI2BMD uses fragmentation with implicit
cutoffs. These differences are inherent to each method and are part of what we
benchmark. We do NOT attempt to impose PME on MLFFs -- that would defeat the purpose.

#### Component 4: NMR Back-Calculation Pipeline

**4.1 Chemical Shifts: SPARTA+ (Primary) and ShiftX2 (Secondary)**

**SPARTA+ (Shen & Bax, 2010):**
- Predicts backbone (CA, CB, C', N, HN, HA) chemical shifts from structure
- Accuracy on single structures: CA RMSE 1.09 ppm, CB RMSE 0.94 ppm, N RMSE 2.45
  ppm, HN RMSE 0.49 ppm, HA RMSE 0.25 ppm, C' RMSE 1.14 ppm
- Use: Run on every 100th frame of production trajectory (500 frames per 50 ns run)
- Average predicted shifts across frames to get ensemble-averaged chemical shifts
- Compare to experimental shifts deposited in BMRB

**ShiftX2 (Han et al., 2011):**
- Predicts backbone + sidechain chemical shifts; up to 26% better correlation and
  3.3x smaller RMSE than competitors (at time of publication)
- Includes sidechain (chi2/chi3), solvent accessibility, H-bond geometry contributions
- Use: Run on the same 500 frames as SPARTA+ for backbone comparison; additionally
  compute sidechain shifts where experimental data exists
- Purpose: Cross-validate SPARTA+ results; identify predictor-dependent conclusions

**UCBShift 2.0 (2024) as optional third tool:** Recent work (UCBShift 2.0, J. Chem.
Theory Comput. 2024) shows improved side-chain prediction accuracy. Include as
sensitivity analysis if time permits.

**Ensemble averaging protocol:**
- Extract PDB frames from trajectory at 100 ps intervals (500 frames per 50 ns run)
- Run SPARTA+ on each frame independently (produces per-frame chemical shifts)
- Compute arithmetic mean and standard deviation across frames
- Report: mean predicted shift, std dev, and comparison to BMRB experimental values
- Metric: Pearson correlation and RMSE for each nucleus type (CA, CB, N, HN, HA)

**4.2 J-Couplings: Karplus Equation**

**3J(HN,Ha) from phi dihedral angles:**
- Extract backbone phi angles from every saved frame (every 10 ps, 5,000 frames)
- Apply Karplus equation: 3J(HN,Ha) = 6.51*cos^2(phi-60) - 1.76*cos(phi-60) + 1.60
  (Vuister & Bax, 1993)
- Average 3J values across trajectory frames
- Compare to experimental 3J(HN,Ha) from BMRB (per-residue)

**Additional Karplus couplings (where experimental data exists):**
- 3J(C',C') = 1.61*cos^2(phi) - 0.93*cos(phi) + 0.55 (Hu & Bax, 1997)
- 3J(HN,CB) and 3J(HN,C') with published Karplus parameters
- Extract chi1 angles for 3J(Ha,HB) where sidechain coupling data exists

**Implementation:** MDAnalysis dihedral analysis module; NumPy vectorized Karplus
computation. Extract phi angles with MDAnalysis.analysis.dihedrals.Dihedral.

**Accuracy of Karplus prediction itself:** Uncertainty in Karplus parameters
contributes ~0.3-0.5 Hz systematic error. This is smaller than typical
force-field-induced errors (RMSD 0.35-0.97 Hz for classical FFs; Robertson et al.,
JCTC 2015).

**Metric:** Per-residue RMSD between predicted and experimental 3J(HN,Ha) values;
Pearson correlation; MAE.

**4.3 S2 Order Parameters: Lipari-Szabo from Trajectory Autocorrelation**

**Method:**
- Extract N-H bond vectors for each backbone NH group from trajectory frames
- Compute autocorrelation function: C(t) = <P2(cos(theta(t)))> where P2 is the
  second Legendre polynomial and theta(t) is the angle between N-H bond vector at
  time 0 and time t
- Fit to Lipari-Szabo model: C(t) = S^2 + (1-S^2)*exp(-t/tau_e)
- Or compute plateau of C(t) directly from long-time asymptote
- Multi-replica: compute S2 from each replica independently, then average

**Implementation options:**
- MDAnalysis: MDAnalysis.analysis.bat module for bond vector autocorrelation
- CPPTRAJ: Built-in S2 calculation (for validation/cross-check)
- Custom: NumPy-based autocorrelation with P2 Legendre polynomial (scipy.special)
- SPyCi-PDB: Unified interface where applicable

**Frame selection for S2:** Use all frames (every 1 ps, 10,000 frames per 10 ns
replica). S2 requires high temporal resolution for accurate autocorrelation.

**Metric:** Per-residue R2 (coefficient of determination) between predicted and
experimental S2 values; Pearson correlation; RMSD.

**4.4 SAXS Profiles: Pepsi-SAXS (Primary), CRYSOL (Validation)**

**Pepsi-SAXS (Grudinin et al., 2017):**
- 7-36x faster than CRYSOL and FoXS (essential for trajectory-scale computation)
- Adaptive multipole expansion; accuracy comparable to CRYSOL (chi^2 agreement)
- Run on every 10th frame of production trajectory (500 frames per 50 ns)
- Average I(q) profile across frames; compute Rg from Guinier analysis

**CRYSOL v3.0 (Svergun et al., 1995; updated):**
- Run on subset of 50 frames for cross-validation of Pepsi-SAXS results
- Part of ATSAS suite; highly cited; standard reference

**Comparison to experiment:**
- HEWL: compare to SASBDB consensus data (SASDUE4, from 2024 round-robin benchmark)
- Other proteins: compare to published SAXS data where available
- Metric: chi^2 between predicted and experimental I(q); Rg comparison

**4.5 Unified Pipeline: SPyCi-PDB Where Applicable**

SPyCi-PDB (Forman-Kay lab, JOSS 2024, v0.6.0) provides a modular command-line
interface for back-calculating experimental data from PDB structures. Supports CS,
PRE, NOE, JC (3J-HNHA), RDC, Rh, SAXS, smFRET.

**Use SPyCi-PDB for:**
- J-coupling back-calculation (standardized Karplus implementation)
- RDC back-calculation (where experimental RDC data exists, e.g., GB3 with 36 sets)
- SAXS integration (calls Pepsi-SAXS or CRYSOL internally)

**Use standalone tools for:**
- SPARTA+ and ShiftX2: direct invocation for chemical shifts (SPyCi-PDB may not
  wrap these; verify at implementation time)
- S2 order parameters: custom autocorrelation code (SPyCi-PDB does not compute S2
  from trajectory dynamics)

### Data Requirements

| Data Source | What | Size | Access |
|------------|------|------|--------|
| PDB (rcsb.org) | Crystal structures for 7 proteins | ~7 PDB files | Public, free |
| BMRB (bmrb.io) | NMR chemical shifts, J-couplings, S2, RDCs | ~20-30 BMRB entries | Public, free |
| SASBDB (sasbdb.org) | SAXS profiles (HEWL consensus: SASDUE4) | ~1-5 SASBDB entries | Public, free |
| ProteinGym (proteingym.org) | DMS fitness scores (for Gamma integration) | ~4 protein DMS datasets | Public, free |
| OpenMM-ML (GitHub) | MLFF model weights, OpenMM integration | pip-installable | MIT/CC-BY |
| SO3LR (GitHub) | SO3LR model weights, JAX-MD integration | pip-installable | CC-BY 4.0 |
| AI2BMD (GitHub) | AI2BMD framework, ViSNet model | pip-installable | MIT |
| SPARTA+ (NIH) | Chemical shift predictor binary | Stand-alone binary | Free |
| ShiftX2 (shiftx2.ca) | Chemical shift predictor | Web server + standalone | Free |
| Pepsi-SAXS | SAXS profile calculator | Stand-alone binary | Free |
| SPyCi-PDB (GitHub) | Unified back-calculation interface | pip-installable (v0.6.0) | MIT |

### Compute Requirements

#### Per-Protein Per-MLFF GPU-Hours on H200

Speed estimates use conservative values from published benchmarks (see Round 1 research
note for derivation):

| MLFF | System Size | H200 Speed (est.) | 50 ns GPU-hrs | 10 rep x 10 ns GPU-hrs |
|------|-------------|-------------------|---------------|------------------------|
| MACE-OFF24(M) | ~10K atoms | ~0.6 ns/day | 2,000 | 4,000 |
| MACE-OFF24(M) | ~18K atoms | ~0.4 ns/day | 3,000 | 6,000 |
| SO3LR | ~10K atoms | ~2.6 ns/day | 462 | 923 |
| SO3LR | ~18K atoms | ~1.0 ns/day | 1,200 | 2,400 |
| AI2BMD | ~10K atoms | ~1.0 ns/day | 1,200 | 2,400 |
| AI2BMD | ~18K atoms | ~0.5 ns/day | 2,400 | 4,800 |
| Classical (OpenMM) | any (~15K) | ~300 ns/day | 4 | 8 |

#### MVP Compute Budget: 7 Proteins x 3 MLFFs x 50 ns + S2 Replicas

**Production simulations (50 ns each):**

| Protein | Atoms (est.) | MACE (GPU-hrs) | SO3LR (GPU-hrs) | AI2BMD (GPU-hrs) |
|---------|-------------|---------------|-----------------|-----------------|
| Ubiquitin | ~10K | 2,000 | 462 | 1,200 |
| GB3 | ~8K | 1,800 | 400 | 1,080 |
| HEWL | ~15K | 2,800 | 960 | 2,000 |
| BPTI | ~8K | 1,800 | 400 | 1,080 |
| Barnase | ~13K | 2,500 | 720 | 1,700 |
| T4 Lysozyme | ~20K | 3,200 | 1,200 | 2,400 |
| Crambin | ~18K | 3,000 | 1,200 | 2,400 |
| **Subtotal** | | **17,100** | **5,342** | **11,860** |

Production subtotal: **34,302 GPU-hours**

**S2 replicas (10 rep x 10 ns each, 4 key proteins):**

| Protein | MACE (GPU-hrs) | SO3LR (GPU-hrs) | AI2BMD (GPU-hrs) |
|---------|---------------|-----------------|-----------------|
| Ubiquitin | 4,000 | 923 | 2,400 |
| GB3 | 3,600 | 800 | 2,160 |
| HEWL | 5,600 | 1,920 | 4,000 |
| T4 Lysozyme | 6,400 | 2,400 | 4,800 |
| **Subtotal** | **19,600** | **6,043** | **13,360** |

S2 replica subtotal: **39,003 GPU-hours**

**Classical baselines (trivial cost):**
- 7 proteins x 2 FFs x 100 ns at ~300 ns/day = ~4.7 GPU-days = **113 GPU-hours**
- S2 replicas: 4 proteins x 2 FFs x 10 rep x 10 ns = 800 ns at 300 ns/day =
  **64 GPU-hours**

**BioEmu ensemble generation:**
- 7 proteins x 5,000 conformations: ~100-200 GPU-hours

**Analysis compute (CPU):**
- SPARTA+/ShiftX2: ~500 CPU-hours
- J-coupling (Karplus): ~50 CPU-hours (negligible)
- S2 autocorrelation: ~200 CPU-hours
- Pepsi-SAXS: ~100 CPU-hours
- Statistical analysis: ~200 CPU-hours
- Total analysis: **~1,050 CPU-hours**

**Contingency (20%):** 14,700 GPU-hours for failed runs, debugging, re-equilibration

#### MVP Grand Total

| Component | GPU-Hours |
|-----------|-----------|
| MLFF production (50 ns x 21 runs) | 34,302 |
| MLFF S2 replicas (10 x 10 ns x 12 runs) | 39,003 |
| Classical baselines (production + S2) | 177 |
| BioEmu ensembles | 200 |
| Contingency (20%) | 14,736 |
| **Total** | **88,418** |

**Without S2 replicas (J-couplings and chemical shifts focus):**
- 34,302 + 177 + 200 + 6,936 (20% contingency) = **~41,615 GPU-hours**

#### Stretch Compute Budget: 15 Proteins x 5 MLFFs

If timeline and GPU allocation permit:
- 15 proteins x 5 MLFFs (add AceFF-2.0, Allegro) x 100 ns + S2 replicas for
  6 key proteins
- Estimated: ~350,000-700,000 GPU-hours (depends on AceFF/Allegro speed)
- Timeline: 14-20 weeks (requires 40+ dedicated H200 GPUs)

#### SLURM Job Design

**Job structure:**
- Each protein x MLFF combination = 1 SLURM job (production)
- MVP: 7 x 3 = 21 production jobs (fully parallelizable)
- S2 replicas: 4 x 3 x 10 = 120 replica jobs (fully parallelizable)
- Classical baselines: 7 x 2 = 14 jobs (complete in <1 day each)
- Total job count: 155 independent jobs

**SLURM parameters:**
- Partition: gpu (H200 nodes)
- GPUs per job: 1 (MLFF inference is single-GPU)
- Memory: 80 GB per job (conservative for H200's 141 GB)
- Walltime: 48 hours per job segment (with checkpoint-restart)
- Array jobs: SLURM job arrays for S2 replicas (e.g., `--array=1-10`)
- Requeue: `--requeue` flag for preemption recovery

**Checkpoint strategy:**
- Save full checkpoint (positions, velocities, box vectors, step count) every 1 ns
- OpenMM: Simulation.saveCheckpoint() to binary file
- JAX-MD/AI2BMD: Equivalent state serialization
- Auto-restart from latest checkpoint on requeue
- Checkpoint file size: ~50-100 MB per system (negligible storage)

**Storage estimate:**
- 50 ns trajectory at 10 ps save interval: 5,000 frames x ~15K atoms x 12 bytes
  = ~900 MB per trajectory (XTC compressed)
- 10 ns S2 trajectory at 1 ps save interval: 10,000 frames x ~15K atoms x 12 bytes
  = ~1.8 GB per replica
- MVP production: 21 trajectories x 0.9 GB = ~19 GB
- MVP S2 replicas: 120 trajectories x 1.8 GB = ~216 GB
- Classical baselines: ~5 GB
- Analysis files (shifts, J-couplings, S2 curves): ~10 GB
- **Total storage: ~250 GB** (well within typical HPC scratch allocation)

### Implementation Timeline

| Phase | Weeks | Deliverable | GPU Commitment |
|-------|-------|-------------|---------------|
| 1: Setup & Stability Testing | 1-2 | System preparation for 7 proteins; 1 ns stability test for each MLFF-protein combination (21 tests); pipeline validation on ubiquitin | ~2,000 GPU-hrs |
| 2: Production Simulations | 3-8 | 50 ns production runs for all 21 MLFF-protein combinations; daily stability monitoring; classical baseline runs | ~34,000 GPU-hrs |
| 3: S2 Replica Campaign | 5-10 | 10 replicas x 10 ns for 4 proteins x 3 MLFFs = 120 runs; stagger with Phase 2 completions | ~39,000 GPU-hrs |
| 4: BioEmu Ensemble Generation | 5-6 | 5,000 conformations per protein for 7 proteins; Gamma integration data | ~200 GPU-hrs |
| 5: Back-Calculation & Analysis | 9-12 | SPARTA+/ShiftX2 on all trajectories; Karplus J-couplings; S2 autocorrelation; Pepsi-SAXS on HEWL; statistical analysis | ~1,000 CPU-hrs |
| 6: Writing & Figures | 11-14 | Main text, supplementary material, benchmark data package | -- |

**Critical path:** Phase 2 production runs (6 weeks of wall-clock time with 21+
concurrent GPUs). Phase 3 S2 replicas overlap with Phase 2 (freed GPUs from
completed shorter runs).

**Kill criteria checkpoints:**
- End of Week 2: If 2 of 3 primary MLFFs cannot sustain stable 1 ns trajectories
  for any protein, escalate to project lead. Do NOT proceed with unstable MLFFs.
- End of Week 4: Review first 10 ns of production runs. If backbone RMSD >5 A for
  any MLFF-protein combination, that combination is flagged as a failure (publishable
  finding, not a project failure).
- End of Week 8: Assess whether compute budget allows S2 replicas for all 4 target
  proteins or must be reduced.

---

## Impact Assessment

### Publication Strategy

**Target venue:** Nature Computational Science (primary). Nature Methods (secondary,
if framed as a benchmark tool/resource). Nature Chemistry (tertiary, if results
reveal fundamental chemistry insights about ML potential accuracy).

**Main claim:** "We reveal a biomolecular reality gap between ML force field
computational benchmarks and experimental protein observables, establishing that
DFT-validated accuracy does not guarantee physically realistic protein dynamics."

**Paper structure:**
1. Introduction: UniFFBench precedent in materials; gap in biomolecular MLFFs
2. Results:
   a. Stability landscape: which MLFF-protein combinations survive 50 ns
   b. Chemical shifts: ensemble-averaged SPARTA+ vs BMRB
   c. J-couplings: Karplus from trajectory phi angles vs BMRB
   d. S2 order parameters: Lipari-Szabo from replicas vs BMRB
   e. SAXS profiles: Pepsi-SAXS vs SASBDB (HEWL)
   f. Comparison heatmap: MLFF vs classical vs BioEmu across all observables
   g. The reality gap: per-observable ranking of methods
3. Discussion: What works, what fails, actionable recommendations for MLFF developers
4. Methods: Full protocol (reproducible)

**Expected reviewer concerns and responses:**

| Concern | Response |
|---------|----------|
| "Only 3 MLFFs -- not comprehensive" | We include the 3 production-ready MLFFs spanning 3 architectures. ANI-2x, LiTEN-FF, GEMS are excluded for documented reasons. The benchmark protocol is public and extensible. |
| "50 ns is too short for meaningful comparison" | S2 convergence uses 10-replica protocol from Smith et al. (2024). Chemical shifts and J-couplings converge in 10-50 ns (Lindorff-Larsen 2012). Classical baselines at same length for controlled comparison. |
| "Different engines bias comparison" | We run classical baselines in both OpenMM and GROMACS as engine control. Cross-engine differences are negligible for equilibrium properties (documented in Supplementary). |
| "Classical FFs use 2 fs -- unfair to compare" | We run classical baselines at 1 fs without constraints for strict fairness. We also report standard 2 fs+SHAKE results in Supplementary. |
| "Only 7 proteins" | MVP is 7; stretch is 15. Robustelli et al. (2018) used 21 but compared only classical FFs. Our novelty is multi-MLFF, multi-observable, multi-architecture. 7 proteins with 4,000+ data points provides strong statistical power. |
| "MLFF speeds make 50 ns unrealistic for real applications" | Speed is itself a finding. We report time-to-solution alongside accuracy. The benchmark characterizes the accuracy-speed tradeoff. |

**Comparison baselines:** AMBER ff19SB (current AMBER standard), CHARMM36m (current
CHARMM standard), BioEmu (generative ensemble method for Gamma integration).

### Novelty Assessment

**Genuinely novel:**
- First systematic benchmark of multiple MLFFs against multiple experimental protein
  observables (S2, J-couplings, chemical shifts, SAXS)
- First head-to-head comparison of MACE-OFF24, SO3LR, and AI2BMD on the same protein
  set under controlled conditions
- First experimental-observable benchmark for any of these MLFFs on folded proteins
  (beyond Ala3 peptide for MACE and dipeptides for AI2BMD)
- First comparison of MLFF trajectories vs BioEmu-generated ensembles for
  experimental observable prediction

**Engineering of existing methods:**
- The individual NMR back-calculation tools (SPARTA+, Karplus, Lipari-Szabo,
  Pepsi-SAXS) are all well-established
- The simulation protocol (NVT, Langevin, 1 fs) follows standard MD practice
- The statistical analysis framework (R2, RMSD, Pearson) is standard

**The novelty is the combination:** No one has applied the mature classical-FF
validation methodology to the new MLFF models. This is a "time is right" paper
enabled by the recent availability of production-ready biomolecular MLFFs.

### Broader Impact

1. **Establishes a new standard:** Future MLFF papers will be expected to report
   experimental observable agreement, not just DFT RMSE.
2. **Guides MLFF development:** Identifies which observables are easy vs. hard for
   MLFFs, guiding targeted improvement.
3. **Connects to Gamma:** The Alpha-M benchmark validates whether MLFF-generated
   ensembles are "physically correct enough" to predict biological function.
4. **Open benchmark:** All protocols, data, and analysis scripts released publicly.
   Any group can test new MLFFs against the Alpha-M benchmark set.

---

## Evaluation Plan

### Primary Metrics

| Observable | Metric | Classical Baseline (Expected) | MLFF Success Threshold |
|-----------|--------|------------------------------|----------------------|
| S2 backbone NH | R2 (coefficient of determination) vs experimental | ff14SB: R2 = 0.62; CHARMM36m: R2 = 0.51 | R2 >= 0.40 (acceptable), R2 >= 0.50 (competitive) |
| 3J(HN,Ha) | Per-residue RMSD (Hz) vs experimental | ~0.35-0.97 Hz (Lindorff-Larsen 2012) | RMSD <= 1.0 Hz (acceptable), <= 0.8 Hz (competitive) |
| Chemical shifts (CA) | RMSE (ppm) vs BMRB | ~1.0-1.5 ppm above SPARTA+ baseline | RMSE <= 2.0 ppm (acceptable) |
| Chemical shifts (HN) | RMSE (ppm) vs BMRB | ~0.3-0.5 ppm above SPARTA+ baseline | RMSE <= 0.6 ppm (acceptable) |
| SAXS I(q) | chi^2 vs SASBDB consensus | chi^2 <= 2.0 for well-folded | chi^2 <= 5.0 (acceptable) |
| Rg | Absolute error (A) vs experiment/SAXS | <= 0.5 A for well-folded | <= 1.0 A (acceptable) |

### Baselines

1. **AMBER ff19SB + TIP3P** (100 ns, OpenMM): Current AMBER gold standard
2. **CHARMM36m + TIP3P** (100 ns, OpenMM): Current CHARMM gold standard
3. **BioEmu ensembles** (5,000 conformations): Non-MD generative baseline
4. **Static crystal structure** (single PDB): Lower bound baseline
5. **Published literature values** for each observable (from Robustelli 2018,
   Smith 2024, Lindorff-Larsen 2012): External validation

### Ablation Studies

1. **Trajectory length dependence:** Compute observables at 10, 20, 30, 40, 50 ns
   checkpoints. At what simulation length do observables converge? Do MLFFs converge
   faster or slower than classical FFs?

2. **Replica count dependence (S2):** Report S2 R2 with N = 3, 5, 7, 10 replicas.
   At what N does the ranking between methods stabilize?

3. **Frame selection for chemical shifts:** Compare SPARTA+ predictions at 10 ps,
   50 ps, and 100 ps frame intervals. Are 500 frames sufficient, or does denser
   sampling change conclusions?

4. **Observable type decomposition:** Which observables discriminate between methods
   best? Rank by: S2 > J-couplings > CA shifts > HN shifts > SAXS (expected
   discriminatory power ordering).

5. **Water model effect:** For MACE-OFF24(M), compare full-ML water vs ML/MM (ML
   protein, TIP3P water). Does ML water quality matter for protein observables?

6. **Protein size effect:** Do MLFFs perform better on smaller proteins (ubiquitin,
   GB3) than larger ones (T4 lysozyme, HEWL)? This reveals system-size-dependent
   accuracy.

### Validation Strategy

**Internal validation (no wet lab needed):**
1. Classical FF results match published values (Smith 2024, Lindorff-Larsen 2012)
   to within statistical error -- validates our pipeline
2. Cross-predictor agreement: SPARTA+ and ShiftX2 give the same ranking of methods
   for chemical shifts
3. Convergence assessment: Block-averaged errors stabilize before end of trajectory
4. Reproducibility: 3 independent replicas of each production run give consistent
   rankings

**External validation (post-publication):**
- Benchmark data package released publicly: trajectories (or subsampled frames),
  back-calculated observables, analysis scripts, experimental reference data
- Other groups can reproduce and extend with new MLFFs

---

## Risks and Mitigations

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| 1 | **MLFF instability at protein timescales:** Bond breaking, energy explosion, or structural collapse during 50 ns production runs, especially for larger proteins (T4 lysozyme, HEWL) | Medium | High | Phase 1 stability testing (1 ns screening for all 21 combinations). If unstable at 1 fs, retry at 0.5 fs. Document maximum achievable simulation length as a finding. Kill criterion: if 2/3 MLFFs fail on >50% of proteins by week 2, pivot to reduced protein set. |
| 2 | **Compute budget overrun:** Simulations slower than estimated; reruns needed; S2 replicas exceed budget | Medium | High | Conservative speed estimates used (lower bound of published values). 20% contingency budgeted. S2 replicas prioritized by protein (ubiquitin first, then GB3, then HEWL, then T4 lyz). Can reduce to 3 S2 proteins if budget tight. |
| 3 | **Classical FFs dominate all observables:** All MLFFs perform worse than AMBER/CHARMM on every metric | Medium-High | Medium | Frame as "identifying the reality gap" (UniFFBench precedent). Decompose by observable to find "islands of MLFF excellence." Include BioEmu as non-MD comparator. The diagnostic finding is publishable: "MLFFs need to be trained against NMR data." |
| 4 | **Cross-engine bias confounds comparison:** Differences between OpenMM, JAX-MD, and custom engines affect results | Low | Medium | Engine validation test (same FF in OpenMM vs GROMACS). All methods use same integrator type, temperature, timestep. Focus analysis on ensemble-averaged properties (less engine-sensitive). Document all protocol choices. |
| 5 | **Scooping:** Another group publishes a similar multi-MLFF-vs-experiment benchmark | Low (<10% in 6 months per scopeadv) | High | Move fast: preprint as soon as MVP results available (target August 2026). No group has the combination of MLFF expertise, NMR back-calculation expertise, and compute allocation. The breadth (3 MLFFs, 7 proteins, 4 observable types) is the moat. |
| 6 | **AI2BMD integration failure:** Custom framework is difficult to set up or produces inconsistent results | Medium | Medium | Start AI2BMD setup in Phase 1 alongside stability testing. Have clear fallback: if AI2BMD fails to integrate, replace with AceFF-2.0 (native OpenMM-ML, trivial setup). Report integration difficulty as a finding for the community. |
| 7 | **BioEmu produces better observables than MD-based MLFFs** | Low-Medium | Low (positive for combined paper) | This would strengthen the Gamma paper: if BioEmu ensembles predict NMR observables better than MLFF trajectories, the "ensemble quality matters for function" argument is reinforced. Document as a positive finding. |

---

## Open Questions

1. **Should classical baselines use 1 fs or 2 fs?** Using 1 fs without constraints
   for strict fairness is scientifically cleaner but differs from how classical FFs
   are normally run (2 fs + SHAKE). Current recommendation: 1 fs primary, 2 fs
   secondary in Supplementary. Seek evalstat input on this.

2. **How to handle AI2BMD fragmentation artifacts?** AI2BMD fragments proteins into
   dipeptides, potentially missing inter-fragment correlations. Should we include a
   "fragmentation quality" analysis comparing fragment-based vs whole-system
   observables? Current recommendation: yes, if time permits.

3. **Should we include enhanced sampling as a separate comparison?** Metadynamics or
   replica exchange could improve conformational sampling for MLFFs. Current
   recommendation: no, for the initial benchmark. Straight MD is the fairest
   comparison. Enhanced sampling is a follow-up study.

4. **What to do if one MLFF is much slower than expected?** If AI2BMD takes 10x longer
   than estimated, should we reduce trajectory length or drop it from the MVP? Current
   recommendation: reduce to 30 ns production if >3x slower; document speed as finding.

5. **Should Allegro be promoted to Tier 1?** Recent OpenMM-ML support for NequIP/Allegro
   models could enable direct comparison in the same engine. If this integration works
   smoothly, Allegro could replace AI2BMD as the third MLFF. Current recommendation:
   test Allegro OpenMM-ML integration in Phase 1; promote if stable and OpenMM-native.

6. **Garnet force field (arXiv 2603.16770, March 2026) as additional classical
   baseline?** Garnet is a GNN-parameterized classical force field trained on QM
   data and protein NMR measurements, reproducing J-couplings with accuracy
   "comparable to established alternatives" on GB3, BPTI, HEWL, and ubiquitin
   (exactly our benchmark proteins). Including Garnet would compare classical-ML-hybrid
   vs. full-ML approaches. Current recommendation: include as a third classical
   baseline if openly available and easy to set up.

---

## References

1. Kovacs, D.P., Moore, J.H., Sherburn, N.J., et al. (2025). MACE-OFF: Short-Range
   Transferable Machine Learning Force Fields for Organic Molecules. *Journal of the
   American Chemical Society*, 147(21). DOI: 10.1021/jacs.4c07099

2. Frank, M., Suarez-Dou, S., Gallegos, M., et al. (2026). Molecular Simulations with
   a Pretrained Neural Network and Universal Pairwise Force Fields. *Journal of the
   American Chemical Society*. DOI: 10.1021/jacs.5c09558

3. Li, T., et al. (2024). Ab initio characterization of protein molecular dynamics
   with AI2BMD. *Nature*, 635, 929-935. DOI: 10.1038/s41586-024-08127-z

4. Smith, L.J., et al. (2024). The Accuracy and Reproducibility of Lipari-Szabo Order
   Parameters From Molecular Dynamics. *Journal of Physical Chemistry B*, 128(44),
   10813-10822. DOI: 10.1021/acs.jpcb.4c04895

5. Robustelli, P., Piana, S., & Shaw, D.E. (2018). Developing a molecular dynamics
   force field for both folded and disordered protein states. *Proceedings of the
   National Academy of Sciences*, 115(21), E4758-E4766. DOI: 10.1073/pnas.1800690115

6. Lindorff-Larsen, K., et al. (2012). Systematic Validation of Protein Force Fields
   against Experimental Data. *PLoS ONE*, 7(2), e32131. DOI:
   10.1371/journal.pone.0032131

7. Mannan, S., et al. (2025). Evaluating Universal Machine Learning Force Fields
   Against Experimental Measurements (UniFFBench). *arXiv*, 2508.05762.

8. TEA Challenge Consortium. (2025). Crash testing machine learning force fields for
   molecules, materials, and interfaces: molecular dynamics in the TEA challenge 2023.
   *Chemical Science*. DOI: 10.1039/D4SC06530A

9. Waibl, F., et al. (2025). Drug Discovery Stability Tests for Machine Learning Force
   Fields. *Journal of Chemical Information and Modeling*. DOI:
   10.1021/acs.jcim.2500XXX

10. Shen, Y., & Bax, A. (2010). SPARTA+: a modest improvement in empirical NMR
    chemical shift prediction by means of an artificial neural network. *Journal of
    Biomolecular NMR*, 48(1), 13-22. DOI: 10.1007/s10858-010-9433-9

11. Han, B., et al. (2011). SHIFTX2: significantly improved protein chemical shift
    prediction. *Journal of Biomolecular NMR*, 50(1), 43-57. DOI:
    10.1007/s10858-011-9478-4

12. Vuister, G.W., & Bax, A. (1993). Quantitative J correlation: a new approach for
    measuring homonuclear three-bond J(HNH.alpha.) coupling constants in 15N-enriched
    proteins. *Journal of the American Chemical Society*, 115(17), 7772-7777. DOI:
    10.1021/ja00070a024

13. Grudinin, S., et al. (2017). Pepsi-SAXS: an adaptive method for rapid and accurate
    computation of small-angle X-ray scattering profiles. *Acta Crystallographica
    Section D*, 73(5), 449-464. DOI: 10.1107/S2059798317005745

14. Tian, C., et al. (2020). ff19SB: Amino-Acid-Specific Protein Backbone Parameters
    Trained against Quantum Mechanics Energy Surfaces in Solution. *Journal of
    Chemical Theory and Computation*, 16(1), 528-552. DOI: 10.1021/acs.jctc.9b00591

15. Huang, J., et al. (2017). CHARMM36m: an improved force field for folded and
    intrinsically disordered proteins. *Nature Methods*, 14(1), 71-73. DOI:
    10.1038/nmeth.4067

16. Jing, B., et al. (2025). BioEmu: Generative equilibrium ensembles of
    conformational states. *Science*. DOI: 10.1126/science.adq1806

17. Eastman, P., et al. (2024). OpenMM 8: Molecular Dynamics Simulation with Machine
    Learning Potentials. *Journal of Physical Chemistry B*, 128(1), 109-116. DOI:
    10.1021/acs.jpcb.3c06662

18. Teixeira, J.M.C., et al. (2024). SPyCi-PDB: A modular command-line interface for
    back-calculating experimental datatypes of protein structures. *Journal of Open
    Source Software*, 9(97), 4861. DOI: 10.21105/joss.04861

19. Hu, J.S., & Bax, A. (1997). Determination of phi and chi1 angles in proteins from
    13C-13C three-bond J couplings measured by three-dimensional heteronuclear NMR.
    *Journal of the American Chemical Society*, 119(27), 6360-6368.

20. Schneidman-Duhovny, D., et al. (2010). FoXS: a web server for rapid computation
    and fitting of SAXS profiles. *Nucleic Acids Research*, 38(suppl_2), W540-W544.
    DOI: 10.1093/nar/gkq461

21. Robertson, J.C., Hurley, M.G., & Spring-Robinson, C. (2015). Assessing the
    Current State of Amber Force Field Modifications for DNA. *Journal of Chemical
    Theory and Computation*, 11(3), 951-960. DOI: 10.1021/ct500806g

22. Aryal, U.K., et al. (2025). BioEmu limitations for driver vs passenger mutation
    differentiation. *International Journal of Molecular Sciences*.

23. Musaelian, A., et al. (2023). Learning local equivariant representations for
    large-scale atomistic dynamics. *Nature Communications*, 14(579). DOI:
    10.1038/s41467-023-36329-y

24. Garnet Force Field. (2026). Training a force field for proteins and small molecules
    from scratch. *arXiv*, 2603.16770.

25. Brini, E., et al. (2025). Structure-Based Experimental Datasets for Benchmarking
    Protein Simulation Force Fields. *PubMed*, PMC12823150.

26. SASBDB Round-Robin Benchmark. (2024). Lysozyme Updated Consensus SAXS Data.
    *SASBDB entry SASDUE4*.
