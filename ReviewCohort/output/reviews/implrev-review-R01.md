---
agent: Technical Implementation Auditor (implrev)
round: 1
date: 2026-04-15
type: review-assessment
scope: cross-cohort
---

# Feasibility Audit: All Proposals

## Reviewing Agent

**Technical Implementation Auditor (implrev).** Senior track, 10+ years running
production computational chemistry workflows on HPC systems, 5+ years GPU computing.
I am the person who actually has to make these simulations run on a real cluster. I
have debugged CUDA OOM errors at 3 AM, waited 6 hours in a SLURM queue, and spent
2 weeks compiling a dependency that the paper said "just install with pip." My job
here is to check whether the software installs, the GPUs have enough memory, the
SLURM jobs will actually finish, and the data pipeline will not choke.

## Executive Summary

Alpha-M is the highest-risk proposal from an implementation standpoint. Its ~107,000
GPU-hr compute budget contains a critical arithmetic discrepancy in Phase 2 that,
once corrected for realistic MLFF ns/day rates, could inflate the true cost by 2-5x.
The proposal assumes 8 methods run smoothly on H200 GPUs, but AI2BMD has documented
H200 compatibility issues (GitHub issue #72), SO3LR has never been demonstrated on a
solvated protein system of this size, and Garnet runs in Julia with no standard MD
engine integration. I rate Alpha-M **YELLOW (feasible with major modifications)** --
specifically, the method count must be reduced to 5-6 and a 2-week pilot phase must
precede any production commitment. Gamma is **GREEN (feasible)** with trivial compute
and well-tested software. Delta is **YELLOW (feasible with modifications)** due to
the unrealistic expectation of setting up 10+ DL methods on Tahoe-100M's 429 GB
dataset in 12 weeks, and the fact that several Tier 2 methods (AlphaCell, X-Cell,
AetherCell) are March 2026 preprints with uncertain code availability.

---

## Part I: Alpha-M Feasibility

### Software Readiness

#### 1. MACE-OFF24 via OpenMM-ML -- READY WITH CAVEATS

**Code availability:** MACE v0.3.13 is actively maintained (GitHub: ACEsuit/mace,
1,800+ stars). The OpenMM interface is documented at mace-docs.readthedocs.io and
runs the full simulation on GPU via the openmm-ml bridge (GitHub: openmm/openmm-ml).

**Protein simulation precedent:** The MACE-OFF24 paper (Kovacs et al., JACS 2025)
demonstrated solvated crambin (46 residues, ~18,000 atoms) on an A100 80 GB GPU,
achieving 3 x 10^5 steps/day. This is the ONLY published protein simulation with
MACE-OFF24. No solvated system larger than crambin has been published.

**T4 lysozyme feasibility (164 residues, ~25,000 atoms with solvent):** T4 lysozyme
is ~40% larger than crambin in atom count. MACE-OFF GPU memory scales roughly
linearly with system size due to the message-passing architecture. At ~18,000 atoms
crambin consumed an A100 (80 GB), so ~25,000 atoms will likely require 80+ GB. The
H200 (80 GB HBM3) has the same capacity as the A100 80 GB but with higher bandwidth
(4.8 TB/s vs 2.0 TB/s). The B200 (192 GB HBM3e) would be the safe choice. Memory
could be tight on H200 for T4 lysozyme; expect 40-60 GB usage for the forward pass
plus optimizer/neighbor list overhead.

**Speed estimate for T4 lysozyme (~25,000 atoms):** Extrapolating from crambin
(3 x 10^5 steps/day at ~18,000 atoms on A100), accounting for the ~1.4x system size
increase and ~1.5x H200 speedup over A100 (due to HBM3 bandwidth), I estimate
~2.2-3.0 x 10^5 steps/day on H200. With 1 fs timestep: **0.22-0.30 ns/day**. For
50 ns production: **167-227 GPU-days per protein per method.** This is a critical
number the proposal does not verify.

**Risk: MODERATE.** MACE-OFF24 is the most production-ready MLFF for this project,
but the speed is ~1000x slower than classical MD, and no one has published T4 lysozyme
or larger protein simulations with it.

**References:**
- Kovacs et al., "MACE-OFF: Short-Range Transferable Machine Learning Force Fields
  for Organic Molecules," JACS 147, 2977 (2025).
- MACE docs, OpenMM interface: https://mace-docs.readthedocs.io/en/latest/guide/openmm.html
- ACEsuit/mace GitHub: https://github.com/ACEsuit/mace
- openmm/openmm-ml GitHub: https://github.com/openmm/openmm-ml

#### 2. SO3LR via JAX-MD -- HIGH RISK

**Code availability:** SO3LR is available on GitHub (general-molecular-simulations/so3lr,
208 stars). Requires JAX 0.5.3, jax-md, and ASE. The CLI supports NPT via Nose-Hoover
chain thermostat/barostat (`so3lr npt --input geometry.xyz ...`).

**Protein simulation precedent:** The SO3LR paper (Frank et al., JACS 2026) benchmarked
on liquid water boxes up to 192,000 atoms and reported 2.6 ns/day for 10,000 atoms on
an H100 80 GB GPU. However, I found NO published solvated protein simulations with
SO3LR. The repository's examples folder does not contain protein simulation examples.
The claim that SO3LR is "scalable to large solvated protein fragments" in the paper
refers to the model architecture, not demonstrated simulations.

**Speed estimate for T4 lysozyme (~25,000 atoms):** SO3LR latency scales as 3.25 x
10^-6 s/atom/step. For 25,000 atoms with 0.5 fs timestep: ~81 ms/step. At 86,400
seconds/day: ~1.07 million steps/day = **0.53 ns/day** (0.5 fs timestep). This is
actually faster than MACE-OFF24, but uses 0.5 fs timestep vs 1 fs.

**JAX JIT compilation overhead:** JAX preallocates 75% of GPU memory by default.
For a 25,000-atom system, the JIT compilation of the force evaluation function will
consume additional memory -- typically 2-3x the forward pass memory due to
intermediate computation graphs. On an H200 (80 GB), this means the compiled model
could try to allocate 60+ GB for a 25,000-atom system. The risk of OOM during JIT
compilation (not during MD) is significant.

**NPT stability:** The SO3LR paper demonstrated NPT on water, not on heterogeneous
protein-water systems. Protein-water NPT with a Nose-Hoover chain barostat in JAX-MD
has not been validated in any publication I can find. Temperature control in
heterogeneous systems (protein + solvent) can exhibit coupling artifacts.

**NOT OpenMM-compatible:** SO3LR uses JAX-MD, which is an entirely separate MD
engine from OpenMM. This means a separate simulation infrastructure, separate
trajectory analysis pipeline, and separate debugging workflow. The proposal must
account for this.

**Risk: HIGH.** No published solvated protein simulations. JAX JIT memory overhead
is unpredictable. NPT stability for protein-water systems is unvalidated. Separate
infrastructure from all other methods.

**References:**
- Frank et al., "Molecular Simulations with a Pretrained Neural Network and Universal
  Pairwise Force Fields," JACS (2026).
- SO3LR GitHub: https://github.com/general-molecular-simulations/so3lr
- JAX-MD documentation, NPT: https://jax-md.readthedocs.io/en/main/examples/npt_simulation.html
- JAX GPU memory allocation: https://docs.jax.dev/en/latest/gpu_memory_allocation.html

#### 3. AI2BMD -- VERY HIGH RISK

**Code availability:** AI2BMD is on GitHub (microsoft/AI2BMD, 574 stars). The ONLY
installation method is Docker. The system fragments proteins into dipeptide units
(21 types, 12-36 atoms each) and uses an Allegro-based MLFF for each fragment.

**Critical GitHub issues (as of April 2026):**
- Issue #72: "Issues with H200" (Aug 2025) -- a user reports problems running on
  H200 GPUs. This is directly relevant since the proposal plans to use H200s.
- Issue #63: "Thermostat detecting temperature runaway conditions" (Apr 2025) --
  thermal stability issues during simulation.
- Issue #70: "Difficulty running custom systems" (Jul 2025) -- external user cannot
  run non-example proteins.
- Issue #65: Request for Singularity support (May 2025) -- Docker is problematic on
  many HPC clusters that use Singularity instead.
- Issue #66: "Protein file preparation fails when adding hydrogen atoms" (Jun 2025).
- 12 open issues total, several from external users reporting fundamental problems.

**Docker on HPC:** Most HPC clusters use Singularity, not Docker, for security
reasons (Docker requires root access). Converting AI2BMD's Docker image to Singularity
is possible but adds complexity and can break GPU passthrough. The request for
Singularity support (issue #65) from May 2025 is STILL OPEN, suggesting this is
not trivially resolved.

**Simulation speed:** The Nature paper (Li et al., Nature 636, 1012, 2024) reports
0.072 s/step for Trp-cage (281 atoms) and 0.125 s/step for albumin-binding domain
(746 atoms). For a protein the size of T4 lysozyme (~2,600 atoms in the protein
alone), the fragmentation scheme must decompose into ~164 overlapping dipeptide units,
each evaluated by the MLFF. With inter-fragment interactions, I estimate 0.3-0.5
s/step. At 1 fs timestep: ~170,000-290,000 steps/day = **0.17-0.29 ns/day** for
the protein fragment evaluation alone. Solvent handling adds additional cost.

**50 ns simulations:** AI2BMD's published simulations are on the order of 100 ps
per trajectory (100 ns total from 1,000 x 100 ps). The proposal requires continuous
50 ns trajectories. No publication has demonstrated continuous 50 ns AI2BMD
trajectories for any protein. The thermostat runaway issue (#63) suggests stability
over long trajectories is not guaranteed.

**Risk: VERY HIGH.** H200 compatibility issues documented. Docker-only installation
problematic for HPC. No published 50 ns protein trajectories. External users report
fundamental difficulties running custom systems.

**References:**
- Li et al., "Ab initio characterization of protein molecular dynamics with AI2BMD,"
  Nature 636, 1012 (2024).
- AI2BMD GitHub: https://github.com/microsoft/AI2BMD
- AI2BMD GitHub issues: https://github.com/microsoft/AI2BMD/issues
- Issue #72 (H200): https://github.com/microsoft/AI2BMD/issues/72
- Issue #63 (thermostat): https://github.com/microsoft/AI2BMD/issues/63
- Issue #70 (custom systems): https://github.com/microsoft/AI2BMD/issues/70

#### 4. BioEmu -- READY

**Code availability:** BioEmu v1.3.1 (released April 15, 2026) is pip-installable
(`pip install bioemu[cuda]`). Linux only. Python 3.10+. The GitHub repository
(microsoft/bioemu, 788 stars) is actively maintained.

**Performance:** On A100 80 GB: 100 residues in ~4 min for 1,000 samples; 300
residues in ~40 min. For 2,000 conformations of T4 lysozyme (164 residues), I
estimate ~15-25 minutes on A100, under 15 minutes on H200. Total for 7 proteins:
under 3 GPU-hours. The proposal's 200 GPU-hr estimate is extremely conservative.

**GPU memory:** ~4 GB for typical proteins. No memory concerns on any GPU in the
cluster.

**Caveat:** BioEmu generates backbone-only coordinates. Side-chain reconstruction
requires additional tooling (e.g., HPacker) and CUDA12-compatible drivers.
AlphaFold2 weights (~3.5 GB) auto-download on first use. Unphysical structures
are filtered, so actual output may be fewer than 2,000.

**Risk: LOW.** Well-maintained, pip-installable, fast, tested.

**References:**
- Lewis, Jing et al., "Scalable Emulation of Protein Equilibrium Ensembles with
  Generative Deep Learning," Science 369, 270-278 (2025).
- BioEmu GitHub: https://github.com/microsoft/bioemu
- BioEmu Nature Methods: https://www.nature.com/articles/s41592-025-02874-1

#### 5. Garnet -- HIGH RISK (INTEGRATION)

**Code availability:** Garnet is from the Greener Group (MRC-LMB, Cambridge).
The paper (arXiv:2603.16770, March 2026) describes a GNN that predicts all MM force
field parameters, trained on DFT data plus protein NMR J-couplings. Code is at
GitHub (greener-group/garnet), written in **Julia** under MIT license.

**Critical problem: Garnet runs in Julia, not in OpenMM or GROMACS.** The Greener
Group's simulation framework (Molly.jl) is Julia-based. There is no documented
OpenMM plugin, no GROMACS topology export, and no Python bridge. To include Garnet
in Alpha-M, you would need to either:
(a) Run simulations entirely in Julia/Molly.jl, requiring a separate simulation
    infrastructure (third one, after OpenMM and JAX-MD), or
(b) Export Garnet parameters to GROMACS/OpenMM format, which is not implemented.

**The proposal lists Garnet as "mandatory" (120 GPU-hrs).** But integrating a
Julia-based force field into a primarily Python/OpenMM pipeline is a 2-4 week
engineering task that is not accounted for in the timeline.

**Speed:** No published benchmarks for Garnet protein simulation speed. As a
GNN-parameterized classical FF, it should be comparable to standard classical FFs
once parameters are generated, but the Julia simulation engine may not match
OpenMM's GPU optimization.

**Risk: HIGH.** Julia-only, no standard MD engine integration, no published
benchmarks, March 2026 preprint.

**References:**
- "Training a force field for proteins and small molecules from scratch,"
  arXiv:2603.16770 (2026).
- Greener Group GitHub: https://github.com/greener-group

#### 6. Classical Baselines (AMBER ff19SB, CHARMM36m, ff14SB) -- READY

**Code availability:** Both force fields are fully supported in OpenMM via
openmmforcefields (GitHub: openmm/openmmforcefields). ff19SB was added via
amber19-all.xml. CHARMM36m is standard.

**Speed estimate for T4 lysozyme (~25,000 atoms with solvent) on H200:** Based on
OpenMM H200 benchmarks showing >500 ns/day for ~44,000 atoms and 84 ns/day for STMV
(>1M atoms), I estimate **200-400 ns/day** for a 25,000-atom system on H200. A 50 ns
simulation completes in **3-6 hours per protein per method.** For all 7 proteins x 3
classical methods: ~63-126 GPU-hours. This is a tiny fraction of the total budget.

**Risk: LOW.** Battle-tested software, well-documented, fast.

**References:**
- OpenMM H200 benchmark: https://github.com/openmm/openmm/issues/4910
- openmmforcefields: https://github.com/openmm/openmmforcefields

#### Software Readiness Summary

| Method | Engine | Install | Protein Precedent | T4 Lys Feasible? | Risk |
|--------|--------|---------|-------------------|------------------|------|
| MACE-OFF24 | OpenMM-ML | pip | Crambin only (46 res) | Likely on H200/B200 | MODERATE |
| SO3LR | JAX-MD | pip + clone | None (water only) | Unknown (JIT risk) | HIGH |
| AI2BMD | Docker | Docker only | Chignolin (10 res) | Unknown (H200 issues) | VERY HIGH |
| BioEmu | pip | pip | Extensively tested | Yes (backbone only) | LOW |
| Garnet | Julia/Molly.jl | Julia pkg | None documented | Unknown (no MD engine) | HIGH |
| AMBER ff19SB | OpenMM | pip | Thousands of studies | Yes | LOW |
| CHARMM36m | OpenMM | pip | Thousands of studies | Yes | LOW |
| ff14SB | OpenMM | pip | Thousands of studies | Yes | LOW |

### Compute Budget Verification

#### Phase 2: The Critical Discrepancy

The proposal states: "Phase 2: Production NPT (50 ns x 7 proteins x 8 methods) =
44,800 GPU-hrs."

**Back-calculation:** 44,800 GPU-hrs / (7 proteins x 8 methods) = 800 GPU-hrs per
protein-method pair = 33.3 GPU-days per simulation.

**At 0.25 ns/day (MACE-OFF24 estimate for T4 lysozyme):** 50 ns requires 200
GPU-days = 4,800 GPU-hrs. Per protein x 3 MLFFs: 14,400 GPU-hrs for MLFFs alone.
For 7 proteins x 3 MLFFs: **100,800 GPU-hrs** for MLFF Phase 2 production.

**At 200 ns/day (classical MD):** 50 ns requires 0.25 GPU-days = 6 GPU-hrs. For
7 proteins x 3 classical methods: **126 GPU-hrs.**

**At 15 min per protein (BioEmu):** Negligible. **~2 GPU-hrs.**

**At unknown speed (Garnet in Julia):** Cannot estimate. Assume comparable to
classical if parameters exported successfully: ~42 GPU-hrs. If running in Julia
simulation engine: likely 5-50x slower.

**Revised Phase 2 total (MLFF + classical + BioEmu + Garnet):**
- MLFFs (MACE + SO3LR + AI2BMD): ~100,800 GPU-hrs (3 MLFFs x 7 proteins x 200 days)
- Classical (ff19SB + CHARMM36m + ff14SB): ~126 GPU-hrs
- BioEmu: ~2 GPU-hrs
- Garnet (optimistic): ~42 GPU-hrs
- **Revised Phase 2 total: ~101,000 GPU-hrs**

**The proposal's 44,800 GPU-hr estimate for Phase 2 is off by a factor of ~2.3x.**
The proposal appears to have used a single average GPU-hr/simulation figure across
all methods, which badly underestimates MLFF cost and overestimates classical cost.

However, this depends critically on the ns/day rate. If the proposal assumed ~1 ns/day
for MLFFs (which would require 50 GPU-days = 1,200 GPU-hrs per simulation), then:
3 MLFFs x 7 proteins x 1,200 = 25,200 GPU-hrs for MLFFs. Combined with classical:
25,200 + 126 + 2 + 42 = ~25,400 for MLFFs+classical+BioEmu+Garnet. This is still
well below 44,800.

**The implicit assumption is ~800 GPU-hrs per simulation = ~1.5 ns/day for all
methods.** This is plausible for small proteins (ubiquitin, GB3, crambin) with
MACE-OFF24, but NOT for T4 lysozyme or barnase. There is no published evidence
any MLFF achieves 1.5 ns/day on a 25,000-atom solvated protein system.

#### Phase 3: S2 Replicas

The proposal states: "Phase 3: S2 replicas (15 x 20-30 ns x 6 proteins x 8 methods)
= 43,200 GPU-hrs."

**Back-calculation:** For 20 ns replicas: 15 x 20 x 6 x 8 = 14,400 simulations x
ns. At 43,200 GPU-hrs, that is 3 GPU-hrs per ns across all methods. This implies an
average simulation speed of 8 ns/day (= 24/3). Again, this average mixes MLFF speeds
(0.25-0.5 ns/day) with classical speeds (200+ ns/day), producing a misleading
average.

**Revised Phase 3 (15 replicas x 20 ns x 6 proteins):**
- Per MLFF method: 15 x 20 x 6 = 1,800 ns. At 0.25 ns/day: 7,200 GPU-days =
  172,800 GPU-hrs per MLFF. For 3 MLFFs: **518,400 GPU-hrs.**
- Per classical method: 1,800 ns at 200 ns/day: 9 GPU-days = 216 GPU-hrs per method.
  For 3 classical: **648 GPU-hrs.**
- BioEmu: Not applicable (generates ensembles, not trajectories).
- Garnet: Assume classical speed if integrated: 216 GPU-hrs.

**Revised Phase 3 total: ~519,264 GPU-hrs.** This is 12x the proposal's estimate.

**However**, S2 replicas for smaller proteins (ubiquitin 76 res, GB3 56 res, BPTI
58 res, crambin 46 res) will be significantly cheaper. Let me recalculate with
per-protein atom counts:

| Protein | Atoms (solvated, est.) | MLFF ns/day (est.) |
|---------|------------------------|--------------------|
| Crambin | ~8,000 | ~1.0 |
| GB3 | ~10,000 | ~0.8 |
| BPTI | ~10,000 | ~0.8 |
| Ubiquitin | ~13,000 | ~0.5 |
| Barnase | ~18,000 | ~0.35 |
| HEWL | ~21,000 | ~0.28 |
| T4 Lysozyme | ~25,000 | ~0.22 |

**Revised Phase 2 (50 ns production, per MLFF method, 7 proteins):**
- Crambin: 50/1.0 = 50 days = 1,200 hrs (but crambin is only 5 ns stability check)
- GB3: 50/0.8 = 62.5 days = 1,500 hrs
- BPTI: 50/0.8 = 62.5 days = 1,500 hrs
- Ubiquitin: 50/0.5 = 100 days = 2,400 hrs
- Barnase: 50/0.35 = 143 days = 3,429 hrs
- HEWL: 50/0.28 = 179 days = 4,286 hrs
- T4 Lysozyme: 50/0.22 = 227 days = 5,455 hrs
- Crambin (5 ns only): 5/1.0 = 5 days = 120 hrs

**Per MLFF Phase 2 total (6 proteins at 50 ns + crambin at 5 ns): 18,690 GPU-hrs.**
For 3 MLFFs: **56,070 GPU-hrs.**
Classical (3 methods, 7 proteins, trivial): **~200 GPU-hrs.**
BioEmu + Garnet: **~250 GPU-hrs.**
**Revised Phase 2 total: ~56,520 GPU-hrs** (vs proposal's 44,800).

This is closer but still 26% higher than the proposal, and critically, the per-protein
variation means the large proteins (T4 lysozyme, HEWL, barnase) dominate the compute.
**T4 lysozyme alone accounts for ~16,365 GPU-hrs (3 MLFFs x 5,455 hrs) -- 29% of
the entire revised Phase 2 MLFF budget.**

**Revised Phase 3 (S2 replicas, 15 x 20-30 ns x 6 proteins x 3 MLFFs):**
Using per-protein speeds and 20 ns for small, 30 ns for large:
- Small (GB3, BPTI, ubiquitin): 15 x 20 ns each = 300 ns per protein.
  At ~0.5-0.8 ns/day: 375-600 days per protein = 9,000-14,400 hrs.
  For 3 proteins x 3 MLFFs: ~27,000-43,200 GPU-hrs.
- Large (barnase, HEWL, T4 lys): 15 x 30 ns each = 450 ns per protein.
  At ~0.22-0.35 ns/day: 1,286-2,045 days per protein = 30,857-49,091 hrs.
  For 3 proteins x 3 MLFFs: ~92,571-147,273 GPU-hrs.

**Revised Phase 3 MLFF total: ~120,000-190,000 GPU-hrs.**
Classical Phase 3 (3 methods): ~2,000 GPU-hrs.
Garnet Phase 3: ~700 GPU-hrs.

**Revised total Phase 2 + Phase 3 for MLFFs alone: ~176,000-246,000 GPU-hrs.**

**This is 2-3x the proposal's combined Phase 2+3 estimate of 88,000 GPU-hrs.**

#### Root Cause of the Discrepancy

The proposal appears to use a blanket "100 GPU-hrs per 50 ns simulation" estimate
(44,800 / 56 simulations in Phase 2 = 800 GPU-hrs each). This would require
~1.5 ns/day, which is:
- Achievable for classical MD on ~25,000 atoms (on CPU, not GPU -- on GPU it's 200+)
- Achievable for MACE-OFF24 on very small molecules (~3,000 atoms)
- NOT achievable for any MLFF on solvated proteins >10,000 atoms

**The proposal's compute budget is built on ns/day assumptions that are not
supported by published benchmarks for the proposed system sizes.**

### Timeline Reality Check

#### Calendar Time vs GPU-hrs

The proposal states 14-16 weeks with "25-30 dedicated H200 GPUs."

**Reality check on GPU allocation:** On a shared HPC cluster, "dedicated" GPUs do not
exist. Typical SLURM fairshare scheduling means:
- Peak demand: 2-4 hour queue waits for H200 jobs
- Sustained multi-week allocation: negotiated priority or preemption rights needed
- "25-30 H200 GPUs for 6-8 weeks" requires institutional commitment

**Assuming 20 H200 GPUs available on average (accounting for queue + contention):**

Phase 1 (stability screening, 1 ns each): Using my revised estimates, 1 ns takes
1-5 GPU-days per MLFF per protein. Total Phase 1: ~400-800 GPU-hrs.
Calendar time at 20 GPUs: 20-40 hrs = **1-2 days.** (Proposal says Weeks 1-2, which
is reasonable when including setup, debugging, and the inevitable "why won't OpenMM
find the CUDA toolkit" errors.)

Phase 2 (50 ns production): Revised ~56,520 GPU-hrs for all methods.
Calendar time at 20 GPUs: 56,520 / (20 x 24) = **118 days = 17 weeks.** The
proposal says 6-8 weeks, which requires 30-40 GPUs running 24/7 with zero queue
time. With realistic queue wait (30% overhead): **22 weeks.**

Phase 3 (S2 replicas): Can partially overlap with Phase 2 for small proteins.
But the large-protein S2 replicas (~120,000+ GPU-hrs for MLFFs) add another
**35+ weeks at 20 GPUs.** Even with overlap and prioritization of small proteins:
**additional 15-20 weeks.**

**Revised timeline:**
- Weeks 1-2: Setup, environment installation, debugging
- Weeks 3-4: Phase 1 stability screening (includes Garnet integration attempt)
- Weeks 5-22: Phase 2 production (17-22 weeks at realistic GPU availability)
- Weeks 10-30+: Phase 3 S2 replicas (overlapping with Phase 2 for small proteins)
- Weeks 25-32: Back-calculation, analysis, writing

**Realistic total: 30-35 weeks, not 14-16 weeks.** This is approximately double the
proposed timeline, and it assumes all three MLFFs actually work on all proteins.

#### The "Software Installation Tax"

The proposal does not budget time for:
- Installing and testing MACE-OFF24 + OpenMM-ML + CUDA compatibility: **3-5 days**
- Installing SO3LR + JAX + JAX-MD + CUDA + GPU verification: **3-5 days** (JAX/CUDA
  version matching is notoriously finicky)
- Installing AI2BMD Docker + Singularity conversion + GPU passthrough: **1-2 weeks**
  (Docker-to-Singularity with GPU support is a common pain point on HPC)
- Garnet Julia installation + Molly.jl + simulation engine testing: **1-2 weeks**
- BioEmu pip install: **30 minutes**
- Classical FFs in OpenMM: **1 hour**
- Total realistic setup: **3-5 weeks** before any production simulation runs

### Storage and Data Management

#### Trajectory Storage

The proposal estimates ~15 GB per 50 ns trajectory (25K atoms, 10 ps saving interval).

**Verification:** 50 ns / 10 ps = 5,000 frames. At 25,000 atoms x 3 coordinates x
8 bytes (double) = 600 KB per frame. 5,000 frames x 600 KB = 3 GB uncompressed.
With velocities and additional data: ~6-10 GB. In XTC/TRR format with compression:
~3-8 GB. The 15 GB estimate includes checkpoints and log files and is reasonable.

**Total trajectory storage:**
- Phase 2 (50 ns x 7 proteins x 8 methods): 56 trajectories x ~10 GB = **560 GB**
- Phase 3 (15 x 20-30 ns x 6 proteins x 8 methods): 720 trajectories x ~5-10 GB =
  **3,600-7,200 GB**
- **Total: ~4-8 TB**

The proposal's ~10 TB estimate is in the right ballpark when including checkpoints,
intermediate files, and analysis data.

**Data management concern:** Writing 4-8 TB to a parallel filesystem (Lustre, GPFS)
from hundreds of concurrent jobs requires careful I/O management. Trajectory files
should be written to local scratch and periodically staged to shared storage. SLURM
epilog scripts for data staging are essential.

**Verdict:** 10 TB is manageable on a modern HPC cluster (typical allocations are
50-100 TB). The concern is I/O throughput, not capacity.

#### Tahoe-100M (Delta)

429 GB dataset in AnnData format. A minified version requires 41 GB.

**Processing:** Scanpy now supports out-of-core analysis via Dask for Tahoe-100M.
Reading in backed mode (`scanpy.read_h5ad(..., backed='r')`) avoids loading the
full dataset into RAM. However, many analysis operations (PCA, clustering) still
require materializing large chunks.

**Minimum RAM for full processing:** 256-512 GB for operations that cannot be
streamed. The DL methods themselves need to batch the data for training.

**Verdict:** Manageable with backed mode and chunked processing, but requires a
high-memory node (512+ GB RAM) for some operations.

### GPU Memory Assessment

| Method | System (T4 Lys) | Est. GPU Mem | H200 (80 GB) | B200 (192 GB) |
|--------|-----------------|-------------|---------------|----------------|
| MACE-OFF24 | ~25K atoms | 40-60 GB | TIGHT | OK |
| SO3LR (JIT) | ~25K atoms | 50-70 GB* | RISKY | OK |
| AI2BMD | Fragmented | ~16-24 GB | OK | OK |
| BioEmu | N/A (generative) | ~4 GB | OK | OK |
| Garnet | ~25K atoms | Unknown | Unknown | Unknown |
| Classical | ~25K atoms | 2-4 GB | OK | OK |

*SO3LR JIT compilation can temporarily require 2-3x runtime memory.

**Key risk:** MACE-OFF24 and SO3LR may require B200 GPUs (192 GB) for the largest
proteins (T4 lysozyme, HEWL). The proposal assumes H200 throughout. If B200 GPUs
are limited in number on the cluster, this constrains parallelism.

**For small proteins (GB3, BPTI, crambin, ubiquitin):** All MLFFs should fit on
H200 with ~8,000-13,000 atoms in the solvated box.

### Failure Mode Analysis

#### Scenario 1: AI2BMD Does Not Compile/Run on the Cluster

**Probability:** 40-50% (based on GitHub issue density and Docker-on-HPC friction)

**Impact:** Lose one of 3 MLFFs. Phase 2 budget decreases by ~33% for MLFFs.

**Proposed mitigation:** AceFF-2.0 fallback. **Problem with this fallback:** AceFF-2.0
(Acellera) is explicitly a small-molecule MLFF. It is "specifically optimized for
small molecules" and uses a hybrid MLIP/MM scheme where "only the ligand is modeled
with the MLIP." It CANNOT serve as a drop-in replacement for AI2BMD's full-protein
ab initio force field. **The proposed AceFF-2.0 fallback is not viable.** A more
realistic fallback is to reduce to 2 MLFFs (MACE-OFF24 + SO3LR) and increase
classical baselines.

#### Scenario 2: SO3LR's JAX Thermostat Produces Drift

**Probability:** 25-35%

**Impact:** Need to diagnose whether the drift is a JAX numerical precision issue
(float32 vs float64), a thermostat coupling issue, or a force field issue. Debugging
JAX-MD simulations is harder than OpenMM because the debugging ecosystem (MDAnalysis,
VMD integration) is less mature.

**Mitigation:** Run alanine dipeptide Ramachandran check first (1-2 days). Monitor
energy conservation in NVE before NVT/NPT. Use float64 (at the cost of 2x memory
and 2x slower speed).

#### Scenario 3: MACE-OFF24 Crashes at 30 ns

**Probability:** 15-25%

**Impact:** Lose trajectory data and GPU-hrs. Need to diagnose whether the crash is
numerical instability, a rare event (e.g., proton transfer), or an OpenMM issue.

**Mitigation:** Save checkpoints every 1 ns. Use Monte Carlo barostat (not
Berendsen) for NPT stability. Pre-test with 10 ns runs before committing to 50 ns.

#### Scenario 4: Garnet Integration Takes >2 Weeks

**Probability:** 70-80%

**Impact:** Either delay the project by 2-4 weeks or drop Garnet entirely.

**Mitigation:** Start Garnet integration in Week 1 on a dedicated team member.
If not running by Week 3, drop it. The paper's narrative can survive without
Garnet (it was only added as a "mandatory baseline" per scopeadv review -- it is
not truly mandatory if it does not have a working MD engine integration).

#### Scenario 5: Insufficient H200 Availability

**Probability:** 50-60% (for the "25-30 dedicated GPUs" assumption)

**Impact:** Timeline extends from 14-16 weeks to 25-35+ weeks.

**Mitigation:** (a) Prioritize small proteins for Phase 2 -- they finish faster
and provide early results for go/no-go decisions. (b) Run classical simulations
on RTX 5000 Ada GPUs (32 GB, ample for classical FF). (c) Negotiate priority
allocation with HPC administrators before the project starts.

### Traffic Light: YELLOW (Feasible with Major Modifications)

Alpha-M is an ambitious and scientifically valuable project, but the current plan
has three critical implementation gaps: (1) the compute budget underestimates MLFF
costs by ~2x, (2) the timeline does not account for software installation, queue
wait, and debugging overhead, and (3) two of the eight proposed methods (AI2BMD,
Garnet) have serious implementation risks. With modifications (see Critical
Modifications below), this project is feasible.

---

## Part II: Gamma Feasibility

### Software Readiness

**BioEmu v1.3.1:** pip-installable, actively maintained, 788 GitHub stars. Generates
2,000 conformations per protein in 15-25 minutes on H200. This is the only software
dependency for ensemble generation. **READY.**

**MDAnalysis, CPPTRAJ:** For feature extraction (RMSF, contacts, S2, etc.). Both are
mature, well-documented packages. CPPTRAJ is available via AmberTools (free). **READY.**

**PocketMiner:** For cryptic pocket detection. Available as a Python package. **READY.**

**ML stack (PyTorch, XGBoost, PyTorch Geometric for GATv2):** Standard ML libraries,
pip-installable. **READY.**

**AMBER ff19SB for 8-protein comparison:** OpenMM integration as described in Part I.
50 ns x 8 proteins = ~48 GPU-hrs on H200. **READY and trivial.**

### Compute Budget

| Component | Proposed GPU-hrs | My Estimate | Assessment |
|-----------|-----------------|-------------|------------|
| BioEmu ensembles (150 x 2,000) | 215 | 50-100 | Overestimate; each protein takes <30 min |
| Convergence pilot (5 x 10,000) | 12 | 5-10 | Reasonable |
| AMBER ff19SB (8 x 50 ns) | 50 | 2-4 | Overestimate (200+ ns/day on H200) |
| ML training + ablation | 1,500 | 1,000-1,500 | Reasonable for GATv2 + XGBoost + sweeps |
| Contingency (20%) | 355 | 200-320 | Fine |
| **Total** | **~2,130** | **~1,300-1,900** | **Conservative, good** |

The Gamma compute budget is conservative (overestimates by ~20-40%), which is the
right direction for budgeting. No concerns.

### Timeline

**Phase 1 (Weeks 1-3): Ensemble generation.** 150 proteins x 25 min each = ~62.5
GPU-hours. On a single H200 running continuously: ~2.6 days. With SLURM scheduling
overhead, can easily parallelize across 4-8 GPUs and finish in 1-2 days. The 3-week
allocation includes the convergence pilot and data QC, which is appropriate. **ON
TRACK.**

**Phase 2 (Weeks 2-4): Feature extraction.** Purely CPU-bound. MDAnalysis and CPPTRAJ
run on standard CPU nodes. 150 proteins x 2,000 conformations = 300,000 structures.
Feature extraction is embarrassingly parallel. **ON TRACK.**

**Phase 3 (Weeks 3-5): AMBER comparisons.** 8 proteins x 50 ns at 200+ ns/day = 8
simulations that each finish in <6 hours. Total: ~2-4 GPU-hrs. Done in 1 day on a
single GPU. **ON TRACK.**

**Phase 4-5 (Weeks 4-9): ML pipeline.** Standard ML training. 150 proteins, ~15
features, 4-stage pipeline. The bottleneck is human iteration time (hyperparameter
tuning, interpretation), not compute. **ON TRACK.**

**Phase 6-7 (Weeks 9-14): Integration, writing.** Depends on Alpha-M data arriving
by Week 12. This is the timeline risk -- if Alpha-M is delayed, integration analysis
pushes to Week 16-18 (per the proposal's own admission). **RISK: ALPHA-M DEPENDENCY.**

### Traffic Light: GREEN (Feasible)

Gamma is a well-scoped, compute-light project with production-ready software. The
only risk is the Alpha-M dependency for the integration analysis, which is correctly
identified and mitigated by the independent AMBER ff19SB comparison.

---

## Part III: Delta Feasibility

### Software Readiness (Per DL Model)

#### Tier 1 (Must Evaluate)

| Method | Publication | GitHub | Stars | Last Commit | Install | Risk |
|--------|-----------|--------|-------|-------------|---------|------|
| GEARS | NeurIPS 2022 | snap-stanford/GEARS | ~400 | Active | pip | LOW |
| scGPT | NatMeth 2024 | bowang-lab/scGPT | ~1,100 | Active | pip | LOW |
| scFoundation | NatMeth 2024 | biomap-research/scFoundation | ~500 | Active | pip | LOW |
| CPA | MSB 2023 | facebookresearch/CPA | ~300 | Moderate | pip | LOW |
| scPPDM | arXiv 2025 | Available | ~50 | Recent | pip | MODERATE |
| scDFM | ICLR 2026 | AI4Science-WestlakeU/scDFM | ~80 | Active | pip | MODERATE |

**Assessment:** Tier 1 methods are all published with available code. GEARS, scGPT,
scFoundation, and CPA are well-tested with community usage. scPPDM and scDFM are
newer but have documented reproducibility. Expect 3-5 days per method for setup,
data formatting, and initial testing. Total for 6 Tier 1 methods: **3-5 weeks of
human effort** (with parallelization across team members).

#### Tier 2 (Evaluate If Available)

| Method | Publication | Code Status | Risk |
|--------|-----------|------------|------|
| AlphaCell | bioRxiv Mar 2026 | Status unclear | HIGH |
| X-Cell | bioRxiv Mar 2026 | Status unclear | HIGH |
| AetherCell | bioRxiv Mar 2026 | Status unclear | HIGH |
| pertTF | bioRxiv Mar 2026 | Status unclear | HIGH |

**Critical concern:** All four Tier 2 methods are March 2026 bioRxiv preprints --
only 2-4 weeks old at the time of this review. Code repositories may not yet be
available or may be in early-release state with minimal documentation. Based on
typical preprint-to-code timelines, I estimate:
- 50% chance code is available at project start (May 2026)
- 30% chance code is available but poorly documented
- 20% chance code requires direct author interaction to reproduce

**Each Tier 2 method that requires debugging adds 1-2 weeks to the timeline.** If
all 4 have issues: **4-8 weeks of additional effort**, which consumes the entire
12-week timeline buffer.

**Recommendation:** Do NOT commit to evaluating all 4 Tier 2 methods. Plan for 1-2
Tier 2 methods maximum, selected based on code availability at project start.

#### Mandatory Baselines (5)

Simple statistical baselines (mean, linear, ridge). These are straightforward to
implement from scratch. **2-3 days total.** LOW risk.

### Tahoe-100M Data Pipeline

**Dataset:** 429 GB in AnnData/H5AD format on Hugging Face (tahoebio/Tahoe-100M).

**Download:** From Hugging Face, which supports streaming. At typical HPC
network speeds (1-10 Gbps), 429 GB takes **6-60 minutes** to download.

**Processing infrastructure:**
- A minified version (41 GB) is available for development
- Full dataset requires backed mode or Dask-based out-of-core processing
- Scanpy supports Tahoe-100M with RAPIDS + Dask integration
- PCA, clustering, and gene selection on 100M cells requires 256-512 GB RAM node

**Per-method data preparation:** Each DL method (GEARS, scGPT, etc.) expects data
in its own format. Converting Tahoe-100M to per-method format requires:
- Understanding each method's data loader
- Train/test split construction with dose-level leakage prevention
- Batch effect control checks
- Estimate: **1-2 weeks** for data pipeline construction

**Storage:** 429 GB raw + ~200-400 GB processed (per-method splits, intermediate
representations) + model checkpoints = **~1-1.5 TB total.** Manageable.

### Compute and Memory

**GPU requirements per DL method:**
- scGPT: Transformer-based, ~8-16 GB for training on typical batch sizes
- scFoundation: Foundation model, may require 24-40 GB for fine-tuning
- GEARS: GNN-based, ~8-16 GB
- CPA: Autoencoder, ~4-8 GB

**The 100M cell challenge:** Training on 100M cells requires careful batching.
Most methods were originally evaluated on datasets of 10K-1M cells. Scaling to
100M introduces:
- Data loading bottlenecks (I/O from disk, not GPU compute, becomes the limit)
- Memory management for gene expression matrices
- Training time: expect 12-48 hours per method per configuration

**Total compute:** The proposal's 1,070 GPU-hrs is reasonable for training +
evaluation across 6-10 methods with multiple configurations.

### Timeline Reality Check

| Task | Proposed Weeks | Realistic Weeks | Notes |
|------|---------------|----------------|-------|
| Data pipeline (download, format, splits) | 1-2 | 2-3 | Backed mode + per-method formatting |
| Baseline implementation | 2 (parallel) | 1-2 | Simple baselines, fast |
| Tier 1 DL methods (6) | 3-4 | 4-6 | 3-5 days each, plus debugging |
| Tier 2 DL methods (2-4) | 2-3 | 3-6 | Code availability uncertain |
| Analysis (Tiers 0-3) | 2 | 2-3 | Statistical framework complex |
| Feature importance + distrib. | 2 | 2 | Straightforward |
| Figures + writing | 2 | 2-3 | Standard |
| **Total** | **12** | **16-23** | **If all Tier 2 included** |

**With Tier 1 only (6 DL methods + 5 baselines):**

| Task | Weeks |
|------|-------|
| Data pipeline | 2-3 |
| Baselines + Tier 1 (parallel) | 4-6 |
| Analysis | 2-3 |
| Feature importance | 2 |
| Writing | 2-3 |
| **Total** | **12-17** |

**The 12-week timeline is achievable only if:**
1. Tier 2 methods are limited to 1-2 with readily available code
2. Data pipeline is pre-built (started in Week 0, before official project start)
3. The team has prior experience with Tahoe-100M and at least 3 of the Tier 1 methods
4. The Systema framework finding (that simple baselines match DL methods on standard
   metrics) does not invalidate the entire benchmark concept before it starts

**Systema Risk:** The Systema paper (Nature Biotechnology 2025) showed that "simple
baselines that exclusively capture average treatment effects surprisingly perform
comparably to state-of-the-art methods." If PerturbMark uses standard metrics and
obtains the same finding, the paper's narrative ("When Does Deep Learning Help?") is
actually strengthened -- but the statistical analysis must be designed to detect the
ABSENCE of improvement, not just its presence. The proposal's WMSE + Spearman-top-k
metric choice is designed to address this, but it requires careful calibration.

### Traffic Light: YELLOW (Feasible with Modifications)

Delta is feasible for Tier 1 methods + baselines within 12-16 weeks. Including all
Tier 2 methods pushes the timeline to 16-23 weeks. The Tahoe-100M data pipeline
requires early investment (pre-project preparation). The proposal should commit to
Tier 1 only as the primary scope and add Tier 2 methods opportunistically.

---

## Critical Modifications Required

### Alpha-M (Priority Order)

1. **Reduce methods to 5-6.** Drop AI2BMD (VERY HIGH risk, Docker-on-HPC, H200
   issues, no 50 ns precedent). Drop Garnet (no MD engine integration, Julia-only).
   Keep: MACE-OFF24, SO3LR, AMBER ff19SB, CHARMM36m, BioEmu, ff14SB. This reduces
   compute by ~30% and eliminates the two highest-risk methods.

2. **Correct the compute budget.** Use per-protein atom-count-adjusted ns/day
   estimates. The revised budget for 6 methods is ~80,000-120,000 GPU-hrs (Phase
   2 + Phase 3), not the proposed 88,000 for 8 methods. If SO3LR also fails, the
   budget drops to ~40,000-60,000 GPU-hrs (MACE-OFF24 + 3 classical + BioEmu).

3. **Mandate a 2-week pilot phase.** Before committing ANY production compute:
   - Week 1: Install all software, verify GPU compatibility
   - Week 2: Run 5 ns test simulations of ubiquitin (smallest protein with S2 data)
     with each MLFF. Measure actual ns/day. Calculate revised compute budget.
   - Go/no-go decision at end of Week 2 based on actual benchmark data.

4. **Extend timeline to 20-24 weeks.** The 14-16 week estimate is unrealistic with
   MLFFs. Budget 3-5 weeks for setup/pilot, 12-16 weeks for production, 4-6 weeks
   for analysis/writing.

5. **Prioritize small proteins first.** Run ubiquitin, GB3, BPTI, crambin (small,
   fast) in Phase 2 before committing to T4 lysozyme, HEWL, barnase (large, slow).
   This provides early go/no-go data and publishable results even if the large
   proteins do not finish.

6. **Secure GPU allocation in advance.** Negotiate with HPC administration for a
   guaranteed allocation of 15-20 H200 GPUs for 12+ weeks. Without this commitment,
   the project timeline is unpredictable.

7. **Replace the AceFF-2.0 fallback.** AceFF-2.0 is a small-molecule FF, not a
   protein MLFF. The fallback for AI2BMD failure should be "reduce to 2 MLFFs" or
   "add a third classical FF" (e.g., OPLS-AA/M), not AceFF-2.0.

8. **Make Garnet optional, not mandatory.** If Garnet integration is achieved within
   Week 3, include it. Otherwise, drop it. Do not block the project on a Julia-only
   force field from a March 2026 preprint.

### Delta (Priority Order)

9. **Commit to Tier 1 only as primary scope.** 6 DL methods + 5 baselines = 11
   methods. Tier 2 methods added only if code is available and verified by Week 4.

10. **Start data pipeline pre-project.** Download Tahoe-100M, construct train/test
    splits, and format data for Tier 1 methods before the 12-week clock starts.

11. **Budget a high-memory node.** Reserve a 512+ GB RAM node for Tahoe-100M
    processing operations that cannot be streamed.

12. **Address the Systema finding in the experimental design.** Explicitly test
    whether DL methods outperform baselines on PerturbMark's metrics, not just
    standard Pearson correlation. If they do not, the paper's finding is "DL does
    not help" -- which is still publishable but requires different framing.

---

## Recommended Execution Strategy

### Week 0 (Pre-Project, 2 Weeks Before Official Start)

- Download Tahoe-100M and begin data pipeline for Delta
- Submit HPC allocation request for 15-20 H200 GPUs x 16 weeks
- Install MACE-OFF24 + OpenMM-ML on cluster test node
- Install SO3LR + JAX-MD on cluster test node
- Attempt AI2BMD Docker-to-Singularity conversion (if proceeding with AI2BMD)
- Install BioEmu (30 min)

### Weeks 1-2: Pilot Phase (Alpha-M)

**Gate 1: Software Verification**
- Run alanine dipeptide NVT + NPT with MACE-OFF24, SO3LR (sanity check)
- Run 1 ns ubiquitin NPT with MACE-OFF24, SO3LR, all classical methods
- Measure actual ns/day for each method on ubiquitin
- Calculate revised compute budget based on measured speeds
- **Go/No-Go decision on each MLFF:** If ns/day < 0.1 for any method on ubiquitin,
  drop that method.

**Gate 2: BioEmu + Gamma**
- Generate BioEmu ensembles for all 7 Alpha-M proteins + 150 Gamma proteins
- Verify feature extraction pipeline on 5-protein convergence pilot
- **Go/No-Go for Gamma:** If BioEmu fails for >2 proteins, investigate and fix
  before proceeding.

### Weeks 3-4: Alpha-M Phase 1 (Stability Screening)

- 1 ns x 7 proteins x surviving methods
- Kill criteria check: if >=2 MLFFs fail stability, reduce scope
- Begin Gamma feature extraction in parallel

### Weeks 3-6: Delta Phase 1 (Data Pipeline + Baselines)

- Finalize train/test splits
- Implement 5 mandatory baselines
- Begin Tier 1 DL method setup (2-3 methods per week)

### Weeks 5-20: Alpha-M Phase 2 (Production)

- Start with smallest proteins (crambin stability, GB3, BPTI)
- Large proteins (T4 lysozyme, HEWL, barnase) start after small proteins validate
- **Gate 3 (Week 8):** If no MLFF has completed a 50 ns trajectory for any protein,
  escalate compute allocation and consider scope reduction

### Weeks 5-9: Gamma ML Pipeline

- RMSF-fitness correlation (Stage 1)
- MLP/XGBoost (Stage 2)
- GATv2 (Stage 3)
- Kill criterion at Week 8 (June 30): RMSF rho < 0.1 for >50% proteins

### Weeks 7-12: Delta DL Method Evaluation

- Run Tier 1 methods on Tahoe-100M (6 methods)
- Tier 2 methods only if code verified and time permits
- Statistical analysis framework implementation

### Weeks 15-20: Alpha-M Phase 3 (S2 Replicas)

- Overlapping with Phase 2 completion for large proteins
- Prioritize proteins with richest S2 data (ubiquitin, GB3)

### Weeks 18-24: Integration + Writing

- Alpha-M back-calculation
- Gamma-Alpha-M integration analysis (if data ready)
- Delta manuscript preparation
- Combined paper decision point at Week 20

### Go/No-Go Gates

| Gate | Timing | Criterion | Action if Failed |
|------|--------|-----------|-----------------|
| G1: Software | Week 2 | All planned MLFFs run 1 ns ubiquitin | Drop failed methods |
| G2: BioEmu | Week 2 | BioEmu generates ensembles for 7 proteins | Debug / contact Microsoft |
| G3: Production | Week 8 | >=1 MLFF completed 50 ns for >=1 protein | Reduce scope to classical + BioEmu |
| G4: Gamma kill | Week 8 | RMSF rho >= 0.1 for >50% proteins | Pivot Gamma scope |
| G5: Alpha-M | Week 14 | >=5 proteins with completed production runs | Reduce to completed set |
| G6: Integration | Week 20 | Integration rho > 0.3 with p < 0.2 | Switch to separate papers |
| G7: Delta methods | Week 8 | >=4 Tier 1 methods evaluated | Reduce method set |

---

## References

1. Kovacs, D.P., et al. "MACE-OFF: Short-Range Transferable Machine Learning Force
   Fields for Organic Molecules." JACS 147, 2977 (2025).
   https://pubs.acs.org/doi/10.1021/jacs.4c07099

2. Frank, M., et al. "Molecular Simulations with a Pretrained Neural Network and
   Universal Pairwise Force Fields." JACS (2026).
   https://pubs.acs.org/doi/10.1021/jacs.5c09558

3. Li, J., et al. "Ab initio characterization of protein molecular dynamics with
   AI2BMD." Nature 636, 1012 (2024).
   https://www.nature.com/articles/s41586-024-08127-z

4. Lewis, J., Jing, B., et al. "Scalable Emulation of Protein Equilibrium Ensembles
   with Generative Deep Learning." Science 369, 270-278 (2025).
   https://www.science.org/doi/10.1126/science.adv9817

5. "Training a force field for proteins and small molecules from scratch."
   arXiv:2603.16770 (2026). https://arxiv.org/abs/2603.16770

6. MACE OpenMM documentation.
   https://mace-docs.readthedocs.io/en/latest/guide/openmm.html

7. ACEsuit/mace GitHub. https://github.com/ACEsuit/mace

8. openmm/openmm-ml GitHub. https://github.com/openmm/openmm-ml

9. SO3LR GitHub. https://github.com/general-molecular-simulations/so3lr

10. AI2BMD GitHub. https://github.com/microsoft/AI2BMD

11. AI2BMD Issue #72 (H200 problems). https://github.com/microsoft/AI2BMD/issues/72

12. AI2BMD Issue #63 (thermostat runaway). https://github.com/microsoft/AI2BMD/issues/63

13. AI2BMD Issue #70 (custom systems). https://github.com/microsoft/AI2BMD/issues/70

14. AI2BMD Issue #65 (Singularity request). https://github.com/microsoft/AI2BMD/issues/65

15. BioEmu GitHub. https://github.com/microsoft/bioemu

16. BioEmu Nature Methods (2025).
    https://www.nature.com/articles/s41592-025-02874-1

17. OpenMM H200 benchmarks. https://github.com/openmm/openmm/issues/4910

18. openmm/openmmforcefields GitHub.
    https://github.com/openmm/openmmforcefields

19. JAX GPU memory allocation documentation.
    https://docs.jax.dev/en/latest/gpu_memory_allocation.html

20. Tahoe-100M Hugging Face.
    https://huggingface.co/datasets/tahoebio/Tahoe-100M

21. scPerturBench GitHub. https://github.com/bm2-lab/scPerturBench

22. Systema framework. "Systema: a framework for evaluating genetic perturbation
    response prediction beyond systematic variation." Nature Biotechnology (2025).
    https://www.nature.com/articles/s41587-025-02777-8

23. GEARS GitHub. https://github.com/snap-stanford/GEARS

24. scGPT GitHub. https://github.com/bowang-lab/scGPT

25. CPA GitHub. https://github.com/facebookresearch/CPA

26. scDFM GitHub. https://github.com/AI4Science-WestlakeU/scDFM

27. scFoundation GitHub. https://github.com/biomap-research/scFoundation

28. AceFF-2.0. "AceFF-2: Bridging the Gap Between Speed and Accuracy in Drug
    Discovery." Acellera (2026).
    https://www.acellera.com/blog/aceff-2-bridging-the-gap-between-speed-and-accuracy-in-drug-discovery

29. Greener Group GitHub. https://github.com/greener-group

30. AlphaCell, bioRxiv (2026).
    https://www.biorxiv.org/content/10.64898/2026.03.02.709176v1

31. AetherCell, bioRxiv (2026).
    https://www.biorxiv.org/content/10.64898/2026.03.13.710968v1

32. X-Cell, bioRxiv (2026).
    https://www.biorxiv.org/content/10.64898/2026.03.18.712807v1

33. pertTF, bioRxiv (2026).
    https://www.biorxiv.org/content/10.64898/2026.03.12.711379v1
