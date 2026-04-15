---
agent: Protein Dynamics & Force Field Reviewer (dynrev)
round: 2
date: 2026-04-15
type: verification-research
---

# Verification Research Report: MLFF Protein Trajectory Feasibility, GEMS Assessment, BioEmu Landscape, and Garnet Contamination

## Reviewing Agent

Mock NCS Reviewer 1 (dynrev). 20+ year veteran of protein MD simulation reviewing
for Nature, NCS, JACS, JCTC, and PNAS. This document reports the results of deep
verification research conducted on the four critical uncertainties identified in my
Round 1 review.

---

## Executive Summary

My Round 1 review identified C1 (no MLFF has demonstrated 50 ns NPT on a solvated
protein) as the central technical risk of the Alpha-M proposal. This verification
research **confirms and strengthens** that finding. The state of the art has not
materially changed since my Round 1 assessment:

- **MACE-OFF24**: Maximum published solvated protein trajectory remains **1.6 ns on
  crambin** (~18,000 atoms). No published work on any protein beyond crambin.
  Confirmed.
- **SO3LR**: Maximum published solvated protein trajectory is **3 ns on crambin**
  (~25,000 atoms), NVT only. A 500 ps glycoprotein run (~48,000 atoms) is the
  largest system. No NPT protein runs published. Confirmed with additional detail.
- **AI2BMD**: Maximum published solvated protein trajectory is **10 ns on chignolin**
  (175 atoms, 10-residue peptide). Only dipeptide-level energy/force evaluations on
  larger proteins. **No production trajectories on any protein beyond chignolin in
  explicit solvent.** Confirmed.
- **GEMS**: 10 ns NPT crambin (~25,257 atoms) is confirmed as the **longest published
  MLFF protein trajectory**. Code/weights NOT publicly released. ~250x slower than
  classical FF. Confirmed with significant caveats on accessibility.
- **Garnet**: GB3 was the only protein used during NMR training. Over-compacts IDPs.
  OpenMM export available via Molly.jl/PyTorch conversion. Confirmed.
- **BioEmu**: Latest release is v1.3.1 (April 2026). No v2.0. Augmented MD preprint
  revised February 2026 (v2). Boltz-2 now competitive on RMSF metrics. Confirmed
  with important updates.

**Bottom line:** The proposal's requirement for 50 ns NPT trajectories on 7 proteins
(56-164 residues) represents a **5x-31x extrapolation** from the longest published
MLFF protein trajectory (GEMS, 10 ns on 46-residue crambin). My Round 1 assessment
that this is the project's critical risk is fully confirmed. The adaptive trajectory-
length protocol I recommended remains essential.

---

## Task D1: Maximum Published MLFF Protein Trajectory Lengths

### D1.1 MACE-OFF24

**Status: Round 1 finding CONFIRMED.**

| Parameter | Verified Value | Source |
|-----------|---------------|--------|
| Longest solvated protein trajectory | 1.6 ns | Kovacs et al., JACS 2025 |
| Protein | Crambin (42 residues) | Kovacs et al., JACS 2025 |
| System size | ~18,000 atoms (protein + water) | Kovacs et al., JACS 2025 |
| Ensemble | Not explicitly stated (likely NVT) | MACE-OFF24 paper |
| GPU | NVIDIA A100 80GB | Kovacs et al., JACS 2025 |
| Throughput | 2.2 x 10^6 steps/day (solvated Ala3) | Kovacs et al., JACS 2025 |
| Stability | RMSF < 1 A for 1 ns; no bond breaking | Kovacs et al., JACS 2025 |

**Key finding 1:** No published work exists demonstrating MACE-OFF24 on ANY protein
beyond crambin. No ubiquitin, no lysozyme, no BPTI. The search was thorough --
I checked arXiv, bioRxiv, JACS, JCTC, PubMed, and GitHub Issues for the MACE
repository. The only peptide work beyond crambin is tripeptide (Ala3) in vacuum
and solvated, and Ala15 in vacuum.

**Key finding 2:** The authors themselves state that "a much longer simulation of
at least several nanoseconds would be required to fully converge the higher
frequency THz region." This is an honest assessment: 1.6 ns was the maximum they
achieved, not a design choice to stop early.

**Key finding 3:** MACE-OFF24(M) was trained on neutral species only. The crambin
test was specifically chosen because it "contains four charged residues" as a
boundary test of the model's capabilities outside its training distribution. For
proteins with more charged residues (ubiquitin: 12 charged residues; T4 lysozyme:
32 charged residues), the model is further outside its training domain.

**Key finding 4:** The computational throughput for solvated systems (2.2 x 10^6
steps/day at 2 fs timestep = 4.4 ns/day for the Ala3 system, but this is a tiny
system of ~1,000 atoms) scales poorly with system size. For an 18,000-atom crambin
system, the effective throughput would be substantially lower. Extrapolating to 50 ns
on ubiquitin (~18,000 atoms with solvent) would require weeks to months of continuous
GPU time per trajectory.

**Verdict:** The proposal's assumption that MACE-OFF24 can produce 50 ns NPT
trajectories on 7 proteins is a 31x extrapolation in trajectory length from the
only published protein data point, with no published evidence of stability beyond
1.6 ns. The risk of failure is HIGH.

---

### D1.2 SO3LR

**Status: Round 1 finding CONFIRMED with additional detail.**

| Parameter | Verified Value | Source |
|-----------|---------------|--------|
| Longest solvated protein trajectory | 3 ns (crambin, 3 runs) | Kabylda et al., JACS 2026 |
| Protein | Crambin (46 residues) | Kabylda et al., JACS 2026 |
| System size | ~25,000 atoms (protein + water) | Kabylda et al., JACS 2026 |
| Ensemble | NVT (power spectrum from 125 ps after 1 ns equilibration) | PMC 12447504 |
| GPU | H100 80GB | Kabylda et al., JACS 2026 |
| Throughput | 3.25 x 10^-6 s/atom/step (~2.6 ns/day for 10k atoms) | PMC 12447504 |
| Stability | "Overall structure stays folded...no bond breaking" | Kabylda et al., JACS 2026 |

**New finding 1:** SO3LR has been tested on systems beyond crambin, but NOT on
extended protein simulations:
- Glycoprotein (PDB: 1K7C): ~48,000 atoms, 500 ps at 300 K (NVT). This is the
  largest biomolecular system tested but the trajectory is 500 ps -- far too short
  for any convergence analysis. The paper notes SO3LR "only sampled anti-conformation
  for the N-linkage dihedral," suggesting limitations in conformational sampling.
- POPC lipid bilayer: 128 lipids + water (~33,000 atoms), 500 ps at 303 K (NPT).
  Area per lipid was 10% underestimated.

**New finding 2:** SO3LR runs in JAX-MD, not standard GROMACS or OpenMM. The code
is available at https://github.com/general-molecular-simulations/so3lr with tutorials.
However, the JAX-MD thermostat/barostat implementation is not the standard Nose-Hoover
or Parrinello-Rahman used in the GROMACS/OpenMM ecosystem. This means NPT simulations
require careful validation -- the 500 ps lipid bilayer NPT is the ONLY published NPT
biomolecular run, and it shows a 10% systematic error in area per lipid.

**New finding 3:** The throughput of 3.25 x 10^-6 s/atom/step on an H100 translates to
approximately:
- For crambin (25k atoms): ~0.08 s/step at 2.5 fs timestep --> ~2.7 ns/day
- For ubiquitin in solvent (~18k atoms): ~3.8 ns/day (estimate)
- For T4 lysozyme in solvent (~50k atoms): ~1.4 ns/day (estimate)
At 1.4 ns/day, a single 50 ns trajectory on T4 lysozyme would take ~36 days.
15 replicas x 30 ns x 7 proteins = 3,150 ns total. At an average of ~2 ns/day,
this requires ~1,575 GPU-days, or ~37,800 GPU-hours. This is within the proposal's
budget but assumes zero failures, restarts, or equilibration overhead.

**Verdict:** SO3LR's longest protein trajectory is 3 ns (crambin, NVT). No NPT
protein run has been published. Extrapolation to 50 ns NPT on larger proteins is a
17x extension in trajectory length, requires an ensemble switch (NVT to NPT), and a
protein-size jump from 46 to 164 residues. The risk is HIGH.

---

### D1.3 AI2BMD

**Status: Round 1 finding CONFIRMED and STRENGTHENED.**

| Parameter | Verified Value | Source |
|-----------|---------------|--------|
| Longest solvated protein trajectory | 10 ns (chignolin) | Li et al., Nature 2024 |
| Protein | Chignolin (10 residues, 175 atoms) | Li et al., Nature 2024 |
| Solvent treatment | AMOEBA 13 for water; MLFF for protein | Li et al., Nature 2024 |
| Number of trajectories | 60 (from folded + unfolded) | Li et al., Nature 2024 |
| GPU | NVIDIA A6000 48GB | Li et al., Nature 2024 |
| Per-step time | 2.610 s for aminopeptidase N (13,728 atoms) | PMC 11602711 |

**Critical finding 1:** AI2BMD does NOT use a fully ML potential for the entire
system. The protein is treated with the AI2BMD MLFF (fragmented into dipeptide
units), but the SOLVENT is treated with the classical AMOEBA 13 polarizable force
field. This is a hybrid scheme. For the Alpha-M benchmark, which compares force
fields head-to-head, this hybrid treatment means AI2BMD is testing the protein
intramolecular potential against a classical water background -- it is NOT a pure
MLFF comparison like MACE-OFF24 or SO3LR.

**Critical finding 2:** The energy/force evaluations on 9 proteins (up to
aminopeptidase N at 13,728 atoms) are SINGLE-POINT calculations, not production
MD runs. The paper computes energy and force errors for snapshots, not trajectories.
The 10 ns production runs were ONLY conducted on chignolin (175 atoms). No extended
trajectory data exists for any protein beyond this 10-residue peptide.

**Critical finding 3:** The fragmentation scheme creates dipeptide units with capping
groups (Ace-NMe). For larger proteins, "as the protein size increased from chignolin
(175 atoms) to PACSIN3 (1,040 atoms), the increase of energy errors could be
attributed to insufficient modelling for the escalating many-body interactions."
This means the fragmentation scheme has DOCUMENTED accuracy degradation with protein
size. Running 50 ns on ubiquitin (76 residues) or T4 lysozyme (164 residues) would
encounter this scaling problem at every timestep, potentially leading to systematic
trajectory drift.

**Critical finding 4:** At 2.610 seconds per step for a 13,728-atom system, a 50 ns
trajectory (at 1 fs timestep) would require 50 x 10^6 steps x 2.6 s = 1.3 x 10^8
seconds = 4.1 years. Even at 2 fs timestep, this would be ~2 years. The computational
cost is prohibitive for proteins larger than chignolin without architectural advances.

**Verdict:** AI2BMD's published protein trajectory capability (10 ns on a 10-residue
peptide with classical solvent) is further from the proposal's requirements than my
Round 1 assessment indicated. The hybrid solvent treatment, documented energy scaling
errors, and prohibitive computational cost for larger proteins make AI2BMD the LEAST
likely of the three proposed MLFFs to achieve 50 ns on the benchmark proteins. The
risk of complete failure for AI2BMD on the Alpha-M protocol is VERY HIGH.

---

### D1.4 GEMS (Potential Fallback)

**Status: Round 1 finding on trajectory length CONFIRMED. New concerns identified.**

| Parameter | Verified Value | Source |
|-----------|---------------|--------|
| Longest solvated protein trajectory | 10 ns (crambin) | Unke et al., Sci. Adv. 2024 |
| Protein | Crambin (46 residues) | Unke et al., Sci. Adv. 2024 |
| System size | 25,257 atoms | PMC 11809612 |
| Ensemble | NPT (300 K, 1.01325 bar) | PMC 11809612 |
| GPU | NVIDIA A100 | PMC 11809612 |
| Per-step time | ~500 ms/step | PMC 11809612 |
| Classical FF comparison | ~2 ms/step (GROMACS) | PMC 11809612 |
| Speed ratio | ~250x slower than classical | PMC 11809612 |

**This is the longest published MLFF protein trajectory in explicit solvent (10 ns
NPT crambin).** This confirmed finding strengthens my Round 1 recommendation that
GEMS should be considered as a contingency MLFF.

**However, three new concerns emerged:**

**Concern 1: Code/weights are NOT publicly released.** The GEMS paper (Unke et al.,
Sci. Adv. 2024; Google DeepMind) released the DFT training data on Zenodo
(zenodo.org/records/10720941) but did NOT release the trained model weights or
simulation code. The SpookyNet architecture code is available
(github.com/OUnke/SpookyNet), but the specific GEMS model trained for biomolecular
dynamics is not publicly available. This means the proposal CANNOT use GEMS without
either (a) contacting DeepMind for model access, or (b) retraining from the published
data, which is itself a significant research project.

**Concern 2: The 250x speed penalty is severe.** At ~500 ms/step on an A100 for
25,257 atoms, a 50 ns trajectory on crambin (at 2.5 fs timestep) requires
50 x 10^6 / 2.5 = 20 x 10^6 steps x 0.5 s = 10^7 seconds = 116 days on a single
GPU. For the 7-protein benchmark with replicas, GEMS alone would require tens of
thousands of GPU-days, potentially exceeding the entire project compute budget.

**Concern 3: No protein beyond crambin has been tested.** GEMS shares this
limitation with MACE-OFF24 and SO3LR: crambin is the only protein. The proposal
cannot assume GEMS will be stable on larger, more flexible proteins.

**Verdict:** GEMS holds the record for longest published MLFF protein trajectory
(10 ns NPT crambin), but its inaccessibility (no public code/weights), extreme
computational cost (~250x classical), and lack of testing beyond crambin make it an
unreliable fallback. My Round 1 recommendation to include GEMS as a contingency is
maintained, but with the qualification that the proposal must secure model access
from DeepMind before Phase 1, or this option is nonviable.

---

### D1.5 AceFF (Proposed Fallback)

**Status: NOT a viable protein MLFF option.**

AceFF (arXiv:2601.00581, January 2026) is a pre-trained machine learning potential
optimized for **small molecule drug discovery**, not protein simulation. AceFF-2
uses TensorNet2 architecture trained on drug-like compounds supporting elements
H, B, C, N, O, F, Si, P, S, Cl, Br, I. While it covers the elements found in
proteins, it was NOT trained on protein conformations, solvated biomolecular systems,
or periodic boundary conditions relevant to protein MD.

**No published protein simulation exists using AceFF.** It benchmarks against
ANI-2x, AIMNet2, and OrbMol on small molecule energy surfaces. The proposal's
mention of AceFF as a fallback MLFF is not supported by evidence that it can
simulate solvated proteins.

**Verdict:** AceFF should be REMOVED from the fallback list unless pilot testing
demonstrates stability on at least crambin in explicit solvent.

---

### D1.6 Stability Solutions (StABlE Training, Pre-training, Active Learning)

**Status: Promising approaches exist but none demonstrated on solvated proteins.**

**StABlE Training** (Raja et al., TMLR 2025; arXiv:2402.13984):
- Multi-modal training combining QM supervision with system observables
- Tested on organic molecules, tetrapeptides, condensed phase systems
- Achieves "significant improvements in simulation stability, data efficiency, and
  agreement with reference observables"
- Enables larger timesteps: "stability improvements cannot be matched by reducing
  the simulation timestep"
- Code publicly available (GitHub, CC BY 4.0)
- **NOT tested on solvated proteins.** Tetrapeptides are the largest systems.

**Pre-training for Stability** (arXiv:2506.14850, "Beyond Force Metrics"):
- Pre-training on OC20 + fine-tuning on MD17 extends trajectory stability by 3x
- "Lower force errors do not necessarily guarantee stable MD simulations"
- Demonstrates that standard force/energy metrics are insufficient predictors of
  trajectory stability
- **NOT tested on biomolecular systems.**

**E2Former-LSR** (arXiv:2601.03774, January 2026):
- Long-range aware message passing for macromolecular systems
- Tested on MolLR25 benchmark (up to 1,200 atoms)
- Fixes discontinuity/error artifacts in MACE at intermediate ranges
- Up to 30% speedup over purely local models
- **Protein-scale benchmarks only for energy/force, not trajectories.**

**TEA Challenge 2023** (Chem. Sci. 2025; D4SC06530A):
- Systematic crash-test of 5 MLFF architectures
- SOAP/GAP and FCHL19* "could not sustain stable dynamics over 1 ns" for peptides
- MACE and SO3krates stable at 300 K on peptides (up to ~100 atoms)
- **Key conclusion: "the main bottleneck for accurate atomistic simulations is
  obtaining high-quality and representative reference data"**
- Training data completeness, not architecture, is the limiting factor

**Verdict on stability solutions:** These are active research areas with real
promise, but NONE has been demonstrated on solvated protein systems at the 50 ns
timescale. The proposal cannot rely on these solutions being available by project
start. However, StABlE Training could potentially be applied to MACE-OFF24 or SO3LR
as a mid-project intervention if initial trajectories are unstable.

---

### D1 Summary Table

| MLFF | Longest Protein Traj. | Protein | Atoms | Ensemble | Code Available | 50 ns Feasibility |
|------|----------------------|---------|-------|----------|---------------|-------------------|
| GEMS | 10 ns | Crambin (46 res) | 25,257 | NPT | NO (weights unreleased) | LOW (cost, access) |
| SO3LR | 3 ns | Crambin (46 res) | 25,000 | NVT | YES (GitHub) | LOW (17x gap, no NPT) |
| MACE-OFF24 | 1.6 ns | Crambin (42 res) | 18,000 | NVT likely | YES (GitHub) | LOW (31x gap) |
| AI2BMD | 10 ns | Chignolin (10 res) | 175 protein | Hybrid | YES (GitHub) | VERY LOW (hybrid, scaling) |
| AceFF | None | N/A | N/A | N/A | YES (GitHub) | NOT APPLICABLE |

**No MLFF has published a solvated protein trajectory longer than 10 ns (GEMS on
crambin), and GEMS model weights are not publicly available.** Among accessible
MLFFs, SO3LR at 3 ns on crambin is the longest. The proposal's 50 ns requirement
remains a 5-17x extrapolation from the accessible state of the art.

---

## Task D2: GEMS Force Field Assessment

### D2.1 Code Availability and Maintenance

**Status: NOT publicly available for use.**

- The GEMS paper (Unke et al., Sci. Adv. 2024) is from Google DeepMind
- DFT training data released on Zenodo (zenodo.org/records/10720941)
- The underlying SpookyNet architecture code is available (github.com/OUnke/SpookyNet)
- **Trained GEMS model weights are NOT released**
- No dedicated GEMS simulation package exists; the paper used SchNetPack MD toolbox
- No GROMACS/OpenMM integration documented
- Maintenance status: Unknown. No GitHub repository for the biomolecular GEMS model

**Implication for Alpha-M:** The proposal CANNOT include GEMS as a benchmark method
without either DeepMind collaboration or a retraining effort from public data. The
retraining effort would require (a) reproducing the fragment-based training pipeline,
(b) QM calculations on the published datasets, (c) training the SpookyNet model, and
(d) validating against the published crambin results. This is months of work and a
subproject in itself.

### D2.2 Solvated Protein NPT Support

**Status: CONFIRMED for crambin only.**

- 10 ns NPT at 300 K, 1.01325 bar confirmed (PMC 11809612)
- 25,257 atoms total (46-residue crambin + 8,205 water molecules)
- Power spectrum analysis from dynamics shows good agreement with THz spectroscopy
- **No protein beyond crambin has been tested**

### D2.3 Computational Performance

**Status: CONFIRMED as ~250x slower than classical FF.**

- ~500 ms per timestep on NVIDIA A100 for crambin (25k atoms)
- Classical GROMACS: ~2 ms per timestep on same hardware
- Speed ratio: ~250x
- For comparison: MACE-OFF24 reports 2.2 x 10^6 steps/day (~46 ns/day for Ala3
  at 2 fs), SO3LR reports ~2.6 ns/day for 10k atoms on H100

**GEMS is the slowest of all MLFFs tested on protein systems.** This is because
SpookyNet incorporates long-range electrostatics and dispersion terms explicitly,
which adds computational cost. However, this is also why it achieved the longest
stable trajectory -- the physics-based long-range treatment may contribute to
stability.

### D2.4 Viability for Alpha-M Benchmark Proteins

| Protein | Residues | Est. System Size (atoms) | Est. 50 ns Wall Time (GPU-days) |
|---------|----------|------------------------|-------------------------------|
| Crambin | 46 | 25,257 | 116 |
| GB3 | 56 | ~20,000 | ~92 |
| BPTI | 58 | ~21,000 | ~97 |
| Ubiquitin | 76 | ~28,000 | ~129 |
| Barnase | 110 | ~40,000 | ~184 |
| HEWL | 129 | ~45,000 | ~207 |
| T4 Lysozyme | 164 | ~55,000 | ~253 |

Total for 7 proteins x 1 trajectory each: ~1,078 GPU-days = ~25,900 GPU-hours.
With 15 replicas x 30 ns: ~310,000 GPU-hours. This EXCEEDS the entire Phase 2
compute budget of 44,800 GPU-hours by 7x.

**Verdict: GEMS is computationally infeasible for the Alpha-M protocol even if
model access were obtained.** It could serve as a single-protein validation point
(crambin only) but not as a benchmark method across 7 proteins.

---

## Task D3: BioEmu Updates and Competitors

### D3.1 BioEmu Version History

**Status: Latest is v1.3.1 (April 15, 2026). No v2.0.**

| Version | Date | Key Changes |
|---------|------|------------|
| v1.3.1 | Apr 15, 2026 | HPacker docs fix, packaging improvements |
| v1.3.0 | Mar 30, 2026 | Steering to avoid chain breaks/clashes; inlined ColabFold & AlphaFold2; removed Disulfide Potential |
| v1.2.0 | Nov 24, 2025 | PPFT training support; KDTree optimization |
| v1.1.0 | Jun 27, 2025 | Model name validation; sequence validity checks |
| v1.0.0pre | Jun 24, 2025 | Pre-release |

**Key observation:** BioEmu v1.3.0 (March 2026) added "steering to avoid chain
breaks and clashes," which suggests the model was producing unphysical structures
(chain breaks, steric clashes) at a rate sufficient to warrant an explicit fix.
The v1.3.0 also "removed Disulfide Potential," which may affect disulfide-bonded
proteins in the benchmark set (BPTI has 3 disulfide bonds; HEWL has 4).

**The proposal should specify v1.3.1 as the pinned version** and verify that the
disulfide potential removal does not affect BPTI and HEWL ensemble quality. This is
a new concern not identified in Round 1.

### D3.2 BioEmu Augmented MD Preprint

**Status: CONFIRMED. bioRxiv v2 posted February 21, 2026.**

- Title: "Accelerated sampling of protein dynamics using BioEmu augmented molecular
  simulation"
- Workflow: BioEmu ensembles + physics-based MD + Markov State Models
- Proteins tested: CDK2 and BRAF (serine-threonine kinases)
- Captured active-to-inactive transitions; resolved V600E mutation effects
- **Failure cases: Glycine transporter 1 (GlyT1, membrane protein) and plasmepsin-II**
- Not yet peer-reviewed (preprint status)

**Implication for Gamma proposal (A2):** This preprint demonstrates that:
(a) Raw BioEmu ensembles need MD refinement to capture kinetic information (e.g.,
    transition rates between metastable states). The Gamma proposal uses raw BioEmu
    ensembles for feature extraction.
(b) BioEmu fails on membrane proteins and some non-kinase targets, limiting
    generalizability.
(c) The augmented workflow is more powerful than raw BioEmu but requires MD
    simulation time, which reduces BioEmu's speed advantage.

If this preprint is published before the Gamma paper submission, the reviewers will
ask: "Why use raw BioEmu ensembles when augmented BioEmu+MD is demonstrably better?"
The proposal should pre-empt this by either (a) including augmented BioEmu as a
comparison, or (b) explicitly arguing that raw BioEmu is sufficient for the feature
extraction task (with evidence).

### D3.3 BioEmu Performance Assessment (Aryal et al., 2026)

**Status: CONFIRMED. Published in Int. J. Mol. Sci. 2026, 27(6), 2896.**

Key findings from this independent assessment:
- BioEmu "can generate multiple conformations and effectively reproduce fundamental
  properties including residue flexibility, motion correlations, and local residue
  contacts"
- Assessment focused on proteins within 100-400 residues
- **BioEmu ensembles reproduce the TENDENCY of intrinsic flexibility profiles, but
  exact RMSF values can differ from MD trajectories**
- Tested on tasks: flexibility, motion correlations, residue contacts, mutational
  effects, conformational bias, ensemble docking

**Critical implication:** The Aryal et al. assessment compared BioEmu to MD (which
uses ff14SB), not to experiment. This confirms my Round 1 concern (M1): BioEmu's
accuracy ceiling is bounded by ff14SB because BioEmu was trained to reproduce ff14SB
equilibrium distributions. Good BioEmu-vs-MD agreement means BioEmu faithfully
emulates ff14SB, NOT that BioEmu captures real dynamics.

### D3.4 Boltz-2 as Competitor Ensemble Generator

**Status: NEW competitor data available.**

Boltz-2 with MD conditioning (bioRxiv January 2026) now provides head-to-head
comparison on the mdCATH and ATLAS datasets:

**RMSF Spearman Correlation (held-out test sets):**

| Method | mdCATH | ATLAS |
|--------|--------|-------|
| Boltz-2 (X-ray cond.) | 0.77 | 0.84 |
| Boltz-2 (MD cond.) | 0.76 | 0.82 |
| Boltz-1 | 0.76 | 0.83 |
| AlphaFlow | 0.70 | 0.75 |
| BioEmu | 0.69 | 0.75 |

Boltz-2 outperforms BioEmu on RMSF correlation by 0.07-0.09 (Spearman). However,
"BioEmu and AlphaFlow more closely align with the reference diversity from the
simulation," meaning BioEmu produces better ensemble diversity even if per-residue
fluctuations are less correlated.

Additionally, Boltz-sample (pair representation scaling in Boltz-2) "significantly
improves the recovery of both alternative states and ensemble coverage" compared
to standard Boltz-2 inference, including membrane transporters where BioEmu fails.

**Implication for Alpha-M/Gamma proposals:**
(a) Boltz-2 should be considered as an additional non-MD ensemble generator in
    Alpha-M (minor issue m6 from Round 1, now elevated to Major given quantitative
    data showing BioEmu underperformance on RMSF).
(b) For Gamma, the finding that BioEmu produces better ensemble diversity than
    Boltz-2 is actually favorable -- fitness prediction may depend more on
    conformational diversity than per-residue RMSF accuracy.
(c) The "BioEmu-only" design is increasingly difficult to defend when Boltz-2
    provides comparable or better dynamics metrics.

### D3.5 BioEmu-ProteinGym Connection

**Status: NOT FOUND.**

I found no published work connecting BioEmu ensemble features to ProteinGym DMS
fitness prediction. This means the Gamma proposal's central hypothesis (BioEmu
ensemble dynamics features predict variant fitness) is genuinely untested. This is
both a risk and a novelty claim -- no one has done it, which means either (a) it
is a real gap worth filling, or (b) it does not work and previous groups found this
but did not publish.

---

## Task D4: Garnet Benchmark Contamination Details

### D4.1 Exact Training and Validation Proteins

**Status: CONFIRMED with additional detail.**

**Training:** GB3 was the ONLY protein used during NMR J-coupling training via
ensemble reweighting. The paper states this explicitly: "GB3, which was used during
training, to assess possible overtraining by the model."

**Validation (folded proteins):** Four proteins assessed via 5 microsecond
simulations:
1. GB3 (used during training)
2. BPTI
3. HEWL
4. Ubiquitin

**Validation (protein complexes):** Four complexes tested:
- Barnase/barstar
- CD2/CD58
- ColE7/Im7
- SGPB/OMTKY3

**Validation (IDPs):** Four intrinsically disordered proteins:
- drkN SH3
- NTAIL
- PaaA2
- alpha-synuclein

### D4.2 Per-Protein Performance

**Status: CONFIRMED. Garnet does NOT clearly outperform classical FFs.**

Key finding from the Garnet paper (arXiv:2603.16770):
- "In all cases apart from HEWL, Amber14SB shows the lowest absolute normalised
  error (ANE), followed by our model and then Espaloma"
- RMSD remains below 3 A for all four folded proteins
- J-coupling RMSE for GB3 (training protein) is similar to Amber14SB
- J-coupling RMSE for ubiquitin is ~0.05 Hz higher error than Amber14SB

**This means Garnet underperforms Amber14SB on most benchmark proteins.** The
proposal must note this: Garnet is not expected to outperform classical FFs on NMR
observables. Its value is as a representative of the "NMR-aware ML classical FF"
paradigm, not as the best performer.

### D4.3 Contamination Analysis for Alpha-M Benchmark

| Protein | In Garnet Training? | In Garnet Validation? | Expected Bias |
|---------|--------------------|-----------------------|---------------|
| Ubiquitin | No | Yes (folded) | Moderate |
| GB3 | **YES** (NMR training) | Yes | **HIGH** |
| HEWL | No | Yes (folded) | Moderate |
| BPTI | No | Yes (folded) | Moderate |
| Barnase | No | Yes (complex: barnase/barstar) | **Moderate** |
| T4 Lysozyme | No | **No** | Low (genuinely out-of-distribution) |
| Crambin | No | No | Low |

**New finding:** Barnase appears in the Garnet protein complex validation
(barnase/barstar complex). This means 5 of 7 Alpha-M proteins (not 4 as stated in
Round 1) have been seen by Garnet during development. Only T4 lysozyme and crambin
are genuinely out-of-distribution for Garnet.

**Revised recommendation:** The Garnet contamination split should be:
- Garnet-train: GB3 (NMR training data)
- Garnet-validation: Ubiquitin, BPTI, HEWL, Barnase (development/validation)
- Garnet-test: T4 Lysozyme (only genuinely unseen protein with NMR data)
- Not applicable: Crambin (no NMR data for S2 comparison)

This means the "fair test" of Garnet generalization rests on a SINGLE protein
(T4 Lysozyme), which is insufficient for any statistical claim about Garnet's
generalization vs overfitting.

### D4.4 OpenMM/GROMACS Export

**Status: OpenMM available via PyTorch conversion. GROMACS NOT documented.**

- Garnet is implemented in Julia (Molly.jl) for differentiable simulation
- "Converted to PyTorch to allow convenient inference by users using the trained
  parameters in the OpenFF and OpenMM software ecosystems"
- GROMACS compatibility: Not documented in the paper
- Molly.jl has experimental GROMACS file reading support, but no Garnet-to-GROMACS
  export pipeline exists

**Implication:** The Alpha-M proposal can use Garnet via OpenMM, which is acceptable
for the benchmark. However, the Molly.jl simulation engine is "approximately 5x
slower than OpenMM on CUDA GPUs" (Greener, Chem. Sci. 2024). The proposal should
use the PyTorch/OpenMM pathway, not native Molly.jl, for production runs.

### D4.5 IDP Failure Mode for alpha-synuclein

**Status: CONFIRMED.**

The Garnet paper explicitly states that Garnet "over-compacts IDPs" on four tested
systems: drkN SH3, NTAIL, PaaA2, and alpha-synuclein. The compaction is "not as
severe" as Amber14SB but worse than the specialist a99SB-disp force field. The
authors note uncertainty about whether this arises from NMR training on the folded
protein GB3 or would arise from QM training alone.

**Implication:** Alpha-synuclein is in the proposal's "exploratory integration set."
Garnet will produce a systematically compacted alpha-synuclein ensemble. The proposal
must either (a) exclude alpha-synuclein from Garnet comparisons, (b) include
a99SB-disp as a specialist IDP baseline, or (c) acknowledge the known failure mode
and interpret results cautiously.

---

## Revised Assessment

### C1 (Critical): 50 ns MLFF trajectory -- CONFIRMED AND STRENGTHENED

**Original assessment:** No MLFF has demonstrated 50 ns NPT on a solvated protein.
MACE-OFF24 max 1.6 ns crambin; SO3LR max 3 ns crambin; AI2BMD max 10 ns chignolin.

**Revised assessment after verification:** FULLY CONFIRMED. Additionally:
1. GEMS holds the record at 10 ns NPT crambin, but weights are unreleased and cost
   is 250x classical
2. AI2BMD uses hybrid solvent (classical water), documented energy scaling errors,
   and is computationally prohibitive for proteins >100 atoms
3. AceFF has no protein simulation capability (should be removed from fallback)
4. No stability solution (StABlE, pre-training) has been demonstrated on solvated
   proteins
5. The TEA Challenge 2023 confirms training data, not architecture, as the
   bottleneck

**Severity upgrade considered but not applied.** C1 remains Critical. The proposal's
adaptive trajectory-length design (my Round 1 recommendation) is the correct
mitigation. The project should proceed with the understanding that 50 ns may not be
achievable and that the maximum stable trajectory length is itself a finding.

### C2 (Critical): Per-residue effective N -- CONFIRMED

**Original assessment:** Effective N for method comparison is ~8-10 proteins, not
420-560 residues.

**Revised assessment:** CONFIRMED. The Smith et al. (2024) paper on Lipari-Szabo
order parameter accuracy (J. Phys. Chem. B 128, 10813-10822) confirms that:
- ff14SB R2 vs experiment = 0.62 (confirmed)
- CHARMM36m R2 vs experiment = 0.51 (confirmed)
- "10 to 20 replicas" needed for reproducible S2 (confirmed)
- Per-protein R2 varies enormously (ubiquitin: 0.84-0.87; T4L: 0.46-0.48;
  alpha-3D: 0.28-0.61 depending on force field)
- **The per-protein variance DOMINATES the per-residue variance**, confirming that
  the effective N for method comparison is determined by the number of proteins,
  not residues.

### M1 (Major): BioEmu ff14SB bias chain -- CONFIRMED

**Original assessment:** BioEmu S2 bounded by ff14SB R2 = 0.62.

**Revised assessment:** CONFIRMED. Aryal et al. (Int. J. Mol. Sci. 2026) tested
BioEmu against MD (not experiment) and found it "effectively reproduces fundamental
properties" when compared to MD reference. This is exactly the ff14SB emulation
finding I predicted. BioEmu faithfully reproduces ff14SB; it does not independently
access experimental dynamics.

The v1.3.0 removal of the Disulfide Potential is a NEW concern for BPTI (3 SS bonds)
and HEWL (4 SS bonds) in the benchmark set.

### M2 (Major): ICC convergence criterion -- NO ADDITIONAL EVIDENCE FOUND

**Original assessment:** ICC(2,k) > 0.80 is borrowed from psychometrics; ICC(2,1) =
0.21 ("poor"). No precedent in MD convergence literature.

**Revised assessment:** I found NO published precedent for using ICC to assess
S2 convergence in MD simulations. The standard approach (Smith et al., 2024) uses
R2-vs-ensemble-size plateau analysis and block-splitting (first-half vs second-half).
The ICC criterion remains non-standard and I maintain the recommendation to
supplement or replace it.

### M3 (Major): Small-protein bias -- CONFIRMED

**Revised assessment:** All published MLFF protein trajectories are on crambin (42-46
residues) or chignolin (10 residues). No MLFF has demonstrated stability on proteins
>50 residues. The benchmark set (56-164 residues) already pushes beyond the tested
regime. The small-protein bias in the benchmark is FORCED by the state of the art,
not a design choice, which is itself a finding.

### M5 (Major): Garnet training contamination -- CONFIRMED AND WORSENED

**Original assessment:** 4 of 7 benchmark proteins in Garnet training/validation.

**Revised assessment:** 5 of 7 benchmark proteins (GB3, ubiquitin, BPTI, HEWL,
barnase) have been seen by Garnet during development. Only T4 lysozyme is genuinely
out-of-distribution (crambin has no NMR data). The contamination is worse than
initially assessed.

### A1 (Advisory): GEMS as fallback -- CONFIRMED BUT PRACTICALLY NONVIABLE

**Original assessment:** GEMS demonstrated 10 ns NPT crambin; consider as contingency.

**Revised assessment:** GEMS 10 ns NPT crambin confirmed, but (a) model weights not
public, (b) ~250x slower than classical, (c) no protein beyond crambin tested. GEMS
is NOT a viable fallback unless DeepMind collaboration is secured pre-project.

### A2 (Advisory): BioEmu augmented MD -- CONFIRMED

**Original assessment:** Preprint changes the Gamma landscape.

**Revised assessment:** CONFIRMED. Preprint revised February 2026 (v2). Shows BioEmu
ensembles need MD refinement for kinetics. Fails on membrane proteins (GlyT1) and
plasmepsin-II. The Gamma proposal should address this competitive result.

### A3 (Advisory): Garnet IDP failure for alpha-synuclein -- CONFIRMED

**Original assessment:** Garnet over-compacts IDPs.

**Revised assessment:** CONFIRMED. Garnet explicitly documented to over-compact
alpha-synuclein. The proposal must exclude alpha-synuclein from Garnet comparisons
or acknowledge the known limitation.

### NEW FINDING: BioEmu v1.3.0 removed Disulfide Potential

This is relevant for BPTI (3 disulfide bonds) and HEWL (4 disulfide bonds). The
proposal should verify that BioEmu v1.3.1 correctly handles disulfide-bonded proteins
before committing to the benchmark. A quick test: generate 100 BioEmu samples for
BPTI and check whether the three disulfide bonds are intact.

### NEW FINDING: Boltz-2 competitive with BioEmu on dynamics metrics

Boltz-2 (RMSF Spearman: 0.76-0.84) now outperforms BioEmu (0.69-0.75) on per-
residue fluctuation metrics. This elevates my Round 1 minor concern (m6) about
missing competitor ensemble generators to a more serious consideration. The Alpha-M
paper will face reviewer questions about why only BioEmu was included.

---

## References

1. Kovacs DP, Moore JH, Browning NJ, et al. MACE-OFF: Short-Range Transferable
   Machine Learning Force Fields for Organic Molecules. JACS. 2025;147:11085-11098.

2. Kabylda A, Vassilev-Galindo V, Chmiela S, et al. Molecular Simulations with a
   Pretrained Neural Network and Universal Pairwise Force Fields. JACS. 2026.
   doi:10.1021/jacs.5c09558.

3. Li T, Zhu Z, Yang B, et al. Ab initio characterization of protein molecular
   dynamics with AI2BMD. Nature. 2024;635:1027-1033.

4. Unke OT, Chmiela S, Gastegger M, et al. Biomolecular dynamics with machine-
   learned quantum-mechanical force fields trained on diverse chemical fragments.
   Sci. Adv. 2024;10:eadn4397.

5. Blanco-Gonzalez A, Schulze TK, Rovers E, Greener JG. Training a force field for
   proteins and small molecules from scratch. arXiv:2603.16770. March 2026.

6. Lewis SE, Kortemme T, et al. Scalable emulation of protein equilibrium ensembles
   with generative deep learning. Science. 2025.

7. Aryal R, et al. Assessing the Performance of BioEmu in Understanding Protein
   Dynamics. Int. J. Mol. Sci. 2026;27(6):2896.

8. Raja S, Amin I, Pedregosa F, Krishnapriyan AS. Stability-Aware Training of
   Neural Network Interatomic Potentials with Differentiable Boltzmann Estimators.
   Trans. Mach. Learn. Res. 2025. arXiv:2402.13984.

9. Luk HL, et al. The Accuracy and Reproducibility of Lipari-Szabo Order Parameters
   From Molecular Dynamics. J. Phys. Chem. B. 2024;128:10813-10822.

10. BioEmu GitHub releases. https://github.com/microsoft/bioemu/releases.
    Accessed April 15, 2026.

11. Greener JG. Differentiable simulation to develop molecular dynamics force fields
    for disordered proteins. Chem. Sci. 2024;15:4897-4909.

12. Accelerated sampling of protein dynamics using BioEmu augmented molecular
    simulation. bioRxiv. 2026. doi:10.64898/2026.01.07.698041v2.

13. TEA Challenge 2023. Crash testing machine learning force fields for molecules,
    materials, and interfaces: molecular dynamics. Chem. Sci. 2025. doi:10.1039/
    D4SC06530A.

14. Wohlwend J, et al. Boltz-2: Towards Accurate and Efficient Binding Affinity
    Prediction. 2025.

15. Suzuki K, et al. Steering Conformational Sampling in Boltz-2 via Pair
    Representation Scaling. bioRxiv. 2026. doi:10.64898/2026.01.23.701250v1.

16. Zheng S, et al. Beyond Force Metrics: Pre-Training MLFFs for Stable MD
    Simulations. arXiv:2506.14850. 2025.

17. SpookyNet reference implementation. https://github.com/OUnke/SpookyNet.

18. SO3LR code repository. https://github.com/general-molecular-simulations/so3lr.

19. AI2BMD code repository. https://github.com/microsoft/AI2BMD.

20. Wang Y, et al. AceFF: A State-of-the-Art Machine Learning Potential for Small
    Molecules. arXiv:2601.00581. January 2026.

21. Bonneau M, et al. Breaking the Barriers of Molecular Dynamics With Deep-
    Learning: Opportunities, Pitfalls, and How to Navigate Them. WIREs Comput.
    Mol. Sci. 2026. doi:10.1002/wcms.70064.

22. E2Former-LSR. Scalable Machine Learning Force Fields for Macromolecular Systems
    Through Long-Range Aware Message Passing. arXiv:2601.03774. January 2026.

23. Palmer AG. NMR Characterization of the Dynamics of Biomacromolecules. Chem. Rev.
    2004;104:3623-3640.

24. Prompers JJ, Bruschweiler R. General Framework for Studying the Dynamics of
    Folded and Nonfolded Proteins by NMR Relaxation Spectroscopy and MD Simulation.
    JACS. 2002;124:4522-4534.

25. Molly.jl. https://github.com/JuliaMolSim/Molly.jl.

26. ProteinGym. https://github.com/OATML-Markslab/ProteinGym.

27. BioEmu benchmarks repository. https://github.com/microsoft/bioemu-benchmarks.
