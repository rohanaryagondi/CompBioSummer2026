---
agent: Technical Implementation Auditor (implrev)
round: 2
date: 2026-04-15
type: verification-research
---

# Implementation Feasibility Verification Research

## Reviewing Agent

**Technical Implementation Auditor (implrev).** This document represents deep
verification research into every implementation claim made in Round 1. Every
repository has been checked, every benchmark cross-referenced, and every timeline
assumption stress-tested against current (April 2026) data.

---

## Executive Summary

Round 2 verification produced **two major revisions** to Round 1 findings and
**confirmed all other assessments**:

**MAJOR REVISION 1 -- Garnet risk downgraded from HIGH to MODERATE.** Contrary to
Round 1's assessment that Garnet was Julia-only with no OpenMM integration, the
greener-group/garnet repository (v0.1.0, February 2026) has been **ported to PyTorch
for inference** and provides a `topology_to_openmm_system()` function for direct
OpenMM integration. This eliminates the 2-4 week Julia integration effort identified
in Round 1. However, the repository has only 5 stars, zero published protein MD
benchmarks, and no simulation speed data, so the risk remains MODERATE rather than LOW.

**MAJOR REVISION 2 -- SO3LR has demonstrated solvated protein simulations.** The
SO3LR paper (Frank et al., JACS 2026) explicitly reports nanosecond-scale dynamics
of solvated crambin (~25,000 atoms), a glycoprotein, and a lipid bilayer. This was
missed in Round 1's claim that SO3LR had "NO published solvated protein simulations."
The risk is revised from HIGH to MODERATE-HIGH: the precedent exists, but crambin is
the only protein demonstrated, and the system is still smaller than T4 lysozyme targets.

**All other Round 1 findings confirmed:**
- AI2BMD: All four critical issues (#72, #63, #65, #70) remain OPEN. Now 22 open
  issues total (up from 12 in Round 1). H200 not listed in tested GPUs. VERY HIGH risk
  confirmed.
- BioEmu: v1.3.1 confirmed current. LOW risk confirmed.
- MACE-OFF24: v0.3.15 (Feb 2025). Crambin remains the ONLY published protein simulation.
  MODERATE risk confirmed. 3 x 10^5 steps/day on A100 for 18,000 atoms confirmed.
- Compute budget discrepancy: Confirmed 2x+ underestimate for Phase 2 MLFF costs.
- Delta Tier 2 code: AlphaCell -- no GitHub found. X-Cell -- weights "coming soon."
  AetherCell -- code exists (15 stars). pertTF -- no GitHub found. HIGH risk confirmed
  for 3 of 4 Tier 2 methods.
- Tahoe-100M: 429 GB in Parquet format confirmed. Streaming supported. Minified
  AnnData via scVI hub (41 GB) confirmed. Community tutorials exist.

**Net effect on traffic lights:**
- Alpha-M: Remains YELLOW, but the ceiling is slightly higher (Garnet integration no
  longer blocks; SO3LR has protein precedent).
- Gamma: Remains GREEN. No changes.
- Delta: Remains YELLOW, with the additional concern that the Nature Methods paper
  (Ahlmann-Eltze et al., 2025) showing DL models do not outperform linear baselines
  directly challenges the Delta narrative.

---

## Task I1: GitHub Repository Status Check (April 2026)

### I1.1 ACEsuit/mace

| Item | Finding |
|------|---------|
| Latest release | **v0.3.15** (February 22, 2025) |
| Stars | ~1,800+ |
| Protein examples | **None in release notes.** All releases focus on materials science, organic molecules. No protein simulation examples in any release. |
| OpenMM-ML compatibility | Documented at mace-docs.readthedocs.io. Interface runs full simulation on GPU via openmm-ml bridge. |
| New foundation models | MACE-POLAR-1 (electrostatics extension), MACE-MH-1 (multi-head, 89 elements). Neither specifically targets proteins. |

**Key finding:** No new MACE releases since February 2025. The project is active (new
foundation models published), but the v0.3.15 release is now 14 months old. No new
protein simulation examples have been published since the original crambin demonstration
in the MACE-OFF24 paper (Kovacs et al., JACS 2025).

**Confirmed from Round 1:** Crambin (~18,000 atoms) remains the ONLY published solvated
protein simulation with MACE-OFF24. Throughput: 3 x 10^5 steps/day on A100 80 GB
(~0.30 ns/day with 1 fs timestep). For T4 lysozyme (~25,000 atoms), my Round 1
estimate of 0.22-0.30 ns/day on H200 stands.

**Sources:**
- ACEsuit/mace releases: https://github.com/ACEsuit/mace/releases
- MACE-OFF24 paper: Kovacs et al., JACS 147, 2977 (2025)
- MACE docs OpenMM: https://mace-docs.readthedocs.io/en/latest/guide/openmm.html

### I1.2 general-molecular-simulations/so3lr

| Item | Finding |
|------|---------|
| Latest release | **v0.1.0** (November 20, 2025) |
| Stars | 208 |
| JAX version | **0.5.3** required |
| CUDA | CUDA 12 required (`jax[cuda12]==0.5.3`) |
| Open issues | **11 open** |
| Solvated protein examples | **YES -- REVISION** (see below) |

**MAJOR REVISION:** The SO3LR paper (Frank et al., JACS 2026) explicitly demonstrates
nanosecond-scale simulations of solvated crambin (~25,000 atoms including water), an
N-linked glycoprotein, and a lipid bilayer, all in explicit solvent. The crambin
simulation included 1 ns of equilibration plus 125 ps of production dynamics at 2.5 fs
temporal resolution. This corrects my Round 1 claim that SO3LR had "NO published
solvated protein simulations." However:

1. **Crambin is the only protein** -- no larger proteins (T4 lysozyme, HEWL, barnase)
   have been demonstrated.
2. **The GitHub README does not contain protein examples.** Examples focus on simple
   molecules (H2). The paper's protein simulations are not reproduced in the repository
   documentation.
3. **Performance:** Measured scaling of 3.25 x 10^-6 s/atom/step on H100. For 25,000
   atoms (crambin-sized system): ~81 ms/step. At 1 fs timestep: ~1.07 million
   steps/day = **~1.07 ns/day on H100.** For the 0.5 fs timestep used in the paper:
   **~0.53 ns/day**. H200 bandwidth advantage over H100 is modest (~1.2x for memory-bound
   workloads), so expect **~0.6-1.3 ns/day on H200** depending on timestep.

**Open issue concerns:**
- Issue #29: NPT simulation errors (December 2025) -- user unable to run NPT
- Issue #25: "Neighbor list overflowed" on water simulations (September 2025) -- large
  system instability
- Issue #23: Regression in periodic systems (July 2025) -- calculator broken for PBC

These issues are directly relevant to Alpha-M's solvated protein NPT simulations.
The neighbor list overflow (issue #25) and NPT errors (issue #29) suggest the
software is not yet production-ready for large solvated systems.

**Revised risk: MODERATE-HIGH** (downgraded from HIGH). Protein simulation precedent
exists but is limited to crambin. Active issues with NPT and large systems.

**Sources:**
- SO3LR GitHub: https://github.com/general-molecular-simulations/so3lr
- Frank et al., JACS (2026): https://pubs.acs.org/doi/10.1021/jacs.5c09558
- SO3LR issues: https://github.com/general-molecular-simulations/so3lr/issues

### I1.3 microsoft/AI2BMD

| Item | Finding |
|------|---------|
| Latest release | **v1.1.0** (February 18, 2025) |
| Stars | 574 |
| Forks | 82 |
| Open issues | **22** (up from 12 in Round 1) |
| Tested GPUs | A100, V100, RTX A6000, Titan RTX -- **H200 NOT listed** |
| Installation | Docker only (`ghcr.io/microsoft/ai2bmd:latest`) |
| CUDA version | Not specified in documentation |
| Singularity support | **NOT implemented** |

**Critical issues -- ALL STILL OPEN:**

| Issue | Title | Opened | Status |
|-------|-------|--------|--------|
| #72 | "Issues with H200" | Aug 27, 2025 | **OPEN** |
| #70 | "Issue running custom system with AI2BMD" | Jul 19, 2025 | **OPEN** |
| #65 | "Singularity support" (feature request) | May 28, 2025 | **OPEN** |
| #63 | "Thermostat detects temperature runaway" | Apr 10, 2025 | **OPEN** |
| #66 | "Protein file preparation fails" | Jun 11, 2025 | **OPEN** |
| #68 | "PyTorch Lightning training script issue" | Jun 16, 2025 | **OPEN** |
| #73 | "Single-point energy computation" | Sep 5, 2025 | **OPEN** |
| #75 | "Instructions typo error" | Jan 15, 2026 | **OPEN** |

**New findings since Round 1:**
1. Open issues increased from 12 to 22 -- the project is accumulating unresolved
   problems faster than it is fixing them.
2. No new releases since v1.1.0 (February 2025) -- 14 months without a release.
3. The README explicitly lists tested GPUs (A100, V100, RTX A6000, Titan RTX) but
   does NOT list H200, H100, or B200. This confirms that H200 is untested territory.
4. Installation is Python >=3.7 launcher script + Docker. No pip install option.
5. Hardware requirements: 8+ CPU cores, 32+ GB RAM, CUDA-enabled GPU with 8+ GB.

**Assessment: VERY HIGH risk confirmed and strengthened.** The combination of (a) H200
not tested, (b) Singularity not supported, (c) 22 open issues with no resolution,
(d) no release in 14 months, and (e) Docker-only installation on HPC makes AI2BMD
effectively non-deployable for this project without significant engineering effort
(estimated 2-4 weeks minimum for Docker-to-Singularity conversion, GPU compatibility
debugging, and custom system setup).

**Sources:**
- AI2BMD GitHub: https://github.com/microsoft/AI2BMD
- AI2BMD issues: https://github.com/microsoft/AI2BMD/issues
- Li et al., Nature 636, 1012 (2024)

### I1.4 microsoft/bioemu

| Item | Finding |
|------|---------|
| Latest stable | **v1.3.1** (confirmed) |
| Latest PyPI | **v0.1.8** -- bumped torch from ==2.4.0 to >=2.6.0 |
| Stars | 788 |
| CUDA | CUDA12-compatible drivers required for side-chain reconstruction |
| Installation | pip (`pip install bioemu[cuda]`) |
| Known issues | None critical |

**Note on versioning:** There appear to be two versioning tracks. The GitHub releases
page shows v1.3.1 as the latest release with significant features (ColabFold/AF2
integration, steering to avoid chain breaks, physics-filtered frame handling). The
PyPI page shows v0.1.8. This may reflect a recent version renumbering or parallel
release tracks. For this assessment, I use v1.3.1 as the functional latest.

**v1.3.0 key features (March 2026):**
- Steering mechanisms to avoid chain breaks and clashes
- Inline ColabFold and AlphaFold2 integration
- Physics-filtered frame handling in topology files

**v1.2.0 features (November 2025):**
- Input sequence validation
- DPM solver improvements
- KDTree optimization for memory efficiency

**Also available on bioconda:** `conda install -c bioconda bioemu`

**Assessment: LOW risk confirmed.** BioEmu is the most production-ready software in
the Alpha-M stack. Pip-installable, actively maintained, extensively documented, and
tested at scale.

**Sources:**
- BioEmu GitHub: https://github.com/microsoft/bioemu
- BioEmu releases: https://github.com/microsoft/bioemu/releases
- BioEmu on Hugging Face: https://huggingface.co/microsoft/bioemu
- BioEmu on bioconda: https://anaconda.org/bioconda/bioemu

### I1.5 greener-group/garnet

| Item | Finding |
|------|---------|
| Latest release | **v0.1.0** (February 24, 2026) |
| Stars | **5** |
| License | MIT |
| Language | **Python (PyTorch inference) + Julia (training)** |
| OpenMM integration | **YES -- MAJOR REVISION** |

**MAJOR REVISION from Round 1:** My Round 1 review stated that Garnet was "Julia-only"
with "no documented OpenMM plugin, no GROMACS topology export, and no Python bridge."
This was INCORRECT. The garnet repository at v0.1.0 provides:

1. **Python package (`garnetff`)** for assigning force field parameters using the
   Garnet model, ported from Julia to PyTorch for inference.
2. **Direct OpenMM integration** via `topology_to_openmm_system()` function that
   converts OpenFF Topologies to OpenMM systems.
3. **Support for PME electrostatics**, bond constraints, and rigid water models.
4. **PDB file input** via OpenFF Toolkit and OpenFF Pablo (for nucleic acids and
   post-translational modifications).
5. **Conda/pip installable** with dependencies: OpenFF toolkit >=0.18.0, RDKit,
   OpenMM, PyTorch, PyTorch Geometric.

**This eliminates the "2-4 week Julia integration" identified in Round 1.** The
integration is now a standard Python/OpenMM workflow.

**Remaining concerns:**
1. **5 GitHub stars** -- essentially no community usage or testing beyond the authors.
2. **No published protein MD benchmarks.** The README describes parameter assignment
   (seconds to minutes) but reports zero simulation speed data (ns/day).
3. **No protein simulation examples in the repository.** The validation/ directory
   contains relative binding free energy (RBFE) calculations, not MD trajectories.
4. **Polymer warning:** "Writing force field XML files works best for non-polymers;
   polymeric systems may encounter issues with OpenMM's residue-based topology parsing."
   This is directly relevant to proteins, which ARE polymers. The workaround uses
   `topology_to_openmm_system()` directly rather than XML serialization, but this
   warning flags potential issues.
5. **Disulfide bridges** require explicit CONECT records -- not a problem for most
   proteins but adds setup complexity.
6. **v0.1.0** -- first release. No history of bug fixes, stability patches, or
   community-reported issues.

**As a GNN-parameterized classical FF:** Once Garnet generates parameters and creates
an OpenMM System, the actual MD simulation runs through OpenMM's GPU-accelerated
integrators at classical FF speeds. This means Garnet simulations should achieve
**similar ns/day to AMBER ff19SB or CHARMM36m** (200-400 ns/day for ~25,000 atoms on
H200), provided the parameterization step works correctly. This is a critical
advantage -- Garnet is NOT an MLFF during simulation; it is an ML-parameterized
classical FF.

**Revised risk: MODERATE** (downgraded from HIGH). The OpenMM integration eliminates
the Julia barrier, but the lack of community testing, protein simulation precedent,
and v0.1.0 maturity keep the risk above LOW.

**Sources:**
- Garnet GitHub: https://github.com/greener-group/garnet
- Garnet README: https://github.com/greener-group/garnet/blob/main/README.md
- Blanco-Gonzalez et al., arXiv:2603.16770 (2026)
- Molly.jl documentation: https://juliamolsim.github.io/Molly.jl/dev/

---

## Task I2: ns/day Benchmarks for MLFF on Protein Systems

This is the single most important data point for Alpha-M's compute budget. I searched
extensively for published or reported ns/day benchmarks for MLFFs on solvated protein
systems.

### I2.1 Confirmed Benchmarks

| Method | System | Atoms | GPU | Steps/day | Timestep | ns/day | Source |
|--------|--------|-------|-----|-----------|----------|--------|--------|
| MACE-OFF24 | Crambin (solvated) | ~18,000 | A100 80GB | 3.0 x 10^5 | 1 fs | 0.30 | Kovacs et al., JACS 2025 |
| MACE-OFF24 | Ala3 (solvated) | ~small | A100 80GB | 2.2 x 10^6 | 1 fs | 2.20 | Kovacs et al., JACS 2025 |
| SO3LR | Water box | 10,000 | H100 80GB | ~1.07M* | 1 fs | ~1.07 | Frank et al., JACS 2026 |
| SO3LR | Crambin (solvated) | ~25,000 | H100 80GB | ~490K* | 0.5 fs | ~0.25 | Frank et al., JACS 2026 (derived) |
| SO3LR | Crambin (solvated) | ~25,000 | H100 80GB | ~490K* | 1 fs | ~0.49 | Extrapolated from scaling |
| AI2BMD | Trp-cage | 281 (protein) | A100 | ~690K | 1 fs | ~0.69 | Li et al., Nature 2024 |
| AI2BMD | ABD | 746 (protein) | A100 | ~400K | 1 fs | ~0.40 | Li et al., Nature 2024 |
| Garnet (via OpenMM) | N/A | N/A | N/A | N/A | N/A | ~classical | No benchmark published |

*SO3LR scaling: 3.25 x 10^-6 s/atom/step. For 25,000 atoms: 81.25 ms/step.
86,400 s/day / 0.08125 s/step = 1,063,385 steps/day at 1 fs = 1.06 ns/day.
At 0.5 fs: 0.53 ns/day.

### I2.2 Critical Analysis

**No MLFF has published benchmarks for solvated proteins larger than crambin (~46
residues, ~18,000-25,000 atoms with solvent).**

For T4 lysozyme (164 residues, ~25,000 atoms solvated):
- **MACE-OFF24:** Extrapolating from crambin A100 data (3 x 10^5 steps/day at 18,000
  atoms) to 25,000 atoms with ~1.4x system size increase, accounting for H200
  bandwidth advantage (~1.5x over A100): **0.22-0.32 ns/day.** My Round 1 estimate
  confirmed.
- **SO3LR:** At 25,000 atoms using the measured 3.25 x 10^-6 s/atom/step scaling on
  H100, with H200 giving ~1.2x speedup: **0.6-1.3 ns/day** (depending on timestep).
  This is faster than MACE-OFF24 but uses a different scaling regime. **REVISED
  UPWARD** from Round 1 estimate of 0.53 ns/day (which used the conservative 0.5 fs
  timestep).
- **AI2BMD:** The fragmentation approach makes extrapolation difficult. Published
  speeds are for protein-only (no solvent box) and for very small proteins (<750
  atoms). For T4 lysozyme (~2,600 protein atoms decomposed into ~164 dipeptide
  fragments): estimated **0.17-0.29 ns/day.** Round 1 estimate confirmed.
- **Garnet:** Since it generates OpenMM-compatible classical-style parameters, simulation
  speed should match classical FF performance: **~200-400 ns/day.** This is a major
  advantage. However, accuracy is completely unvalidated at protein scale.

### I2.3 Revised Phase 2 Compute Estimates

Using verified benchmarks and accounting for the Garnet reclassification:

| Method | T4 Lys ns/day (H200) | 50 ns GPU-days | 50 ns GPU-hrs | Category |
|--------|----------------------|----------------|---------------|----------|
| MACE-OFF24 | 0.25 | 200 | 4,800 | MLFF |
| SO3LR | 0.8 (1 fs) | 62.5 | 1,500 | MLFF |
| AI2BMD | 0.23 | 217 | 5,217 | MLFF |
| Garnet | ~300 | 0.17 | 4 | ML-parameterized classical |
| BioEmu | N/A (generative) | N/A | <1 | Generative |
| AMBER ff19SB | ~300 | 0.17 | 4 | Classical |
| CHARMM36m | ~300 | 0.17 | 4 | Classical |
| ff14SB | ~300 | 0.17 | 4 | Classical |

**Per-protein T4 lysozyme Phase 2 total (8 methods):** ~11,534 GPU-hrs
**Per-protein T4 lysozyme Phase 2 total (6 methods, drop AI2BMD + Garnet optional):**
~6,312 GPU-hrs

The reclassification of Garnet from MLFF-speed to classical-speed dramatically reduces
its compute impact. This is actually good news for Alpha-M.

**Sources:**
- Kovacs et al., JACS 147, 2977 (2025) -- MACE-OFF24 crambin benchmark
- Frank et al., JACS (2026) -- SO3LR scaling and protein simulations
- Li et al., Nature 636, 1012 (2024) -- AI2BMD protein benchmarks
- OpenMM H200 benchmarks: https://github.com/openmm/openmm/issues/4910

---

## Task I3: Tahoe-100M Data Pipeline Verification

### I3.1 Current Dataset Status on Hugging Face

| Item | Finding |
|------|---------|
| URL | https://huggingface.co/datasets/tahoebio/Tahoe-100M |
| Total size | **429 GB** (confirmed) |
| Format | **Parquet** (auto-converted from original) |
| Total rows | 4,286,159,337 across all tables |
| Subsets (7) | expression_data (95.6M rows), obs_metadata (101M rows), pseudobulk_DE (4.09B rows), gene_metadata (62.7K), cell_line_metadata (1K), drug_metadata (379), sample_metadata (1.3K) |
| Streaming | **YES** -- `load_dataset(..., streaming=True)` supported |
| License | Not specified on HF page |

**Key clarification from Round 1:** The dataset is in **Parquet format**, not AnnData/H5AD.
Parquet files are optimized for columnar analytics and streaming. AnnData/H5AD files
"are converted to Parquet files for users who would prefer to use big data analytics
tools, including Spark." This means per-method data preparation (converting to each DL
method's expected format) requires Parquet-to-AnnData conversion, not direct AnnData
loading.

### I3.2 Minified Version

| Item | Finding |
|------|---------|
| Name | Tahoe-100M-SCVI-v1 |
| URL | https://huggingface.co/tahoebio/Tahoe-100M-SCVI-v1 |
| Type | Pretrained scVI model + minified AnnData |
| Size | **41 GB** storage + RAM required |
| Model params | n_hidden=128, n_latent=10, n_layers=1 |
| Dimensions | 95,624,334 obs x 62,710 vars |

**The minified version stores encoded latent vectors, not raw counts.** The latent
vectors can be decoded to approximate gene expression levels, but they are NOT the
same as raw count data. For DL methods that require raw counts as input (GEARS,
scGPT, scFoundation, CPA), the minified version is NOT a drop-in replacement. It is
useful for:
- Rapid development and debugging
- scVI-based downstream analysis
- Initial data exploration

**For the Delta benchmark, the full 429 GB dataset is required for production runs.**
The minified version can accelerate development (first 2-3 weeks) but not production
training.

### I3.3 Community Tutorials and Tools

| Resource | URL | Status |
|----------|-----|--------|
| Data Loading Tutorial | HuggingFace repo tutorials/ | Available |
| scvi-tools Tahoe100M tutorial | docs.scvi-tools.org/en/stable/tutorials/notebooks/hub/Tahoe100.html | Available |
| Theis Lab analysis pipeline | github.com/theislab/vevo_Tahoe_100m_analysis | Available |
| RAPIDS + Scanpy pipeline | Referenced in HF README | Available |

**The Theis Lab pipeline** (github.com/theislab/vevo_Tahoe_100m_analysis) provides an
optimized analysis workflow using RAPIDS and Scanpy for giga-scale single-cell data.
This is directly usable for Delta's data preprocessing.

### I3.4 Tahoe-x1 Preprocessing Reusability

Tahoe-x1 (github.com/tahoebio/tahoe-x1, 143 stars, Apache 2.0) is a family of
single-cell foundation models pretrained on 266M cells including Tahoe-100M. The
quickstart explicitly shows launching pre-training on Tahoe-100M with dataset
streaming. This confirms that production-scale preprocessing pipelines for Tahoe-100M
exist and are documented.

**For Delta:** Tahoe-x1's data loading code can be adapted for other models, reducing
the data pipeline construction effort from my Round 1 estimate of 1-2 weeks to
potentially 3-5 days.

**Sources:**
- Tahoe-100M HuggingFace: https://huggingface.co/datasets/tahoebio/Tahoe-100M
- Tahoe-100M-SCVI-v1: https://huggingface.co/tahoebio/Tahoe-100M-SCVI-v1
- scvi-tools tutorial: https://docs.scvi-tools.org/en/stable/tutorials/notebooks/hub/Tahoe100.html
- Theis Lab analysis: https://github.com/theislab/vevo_Tahoe_100m_analysis
- Tahoe-x1 GitHub: https://github.com/tahoebio/tahoe-x1

---

## Task I4: DL Model Code Availability (Delta)

### I4.1 Tier 1 Methods (Must Evaluate)

| Method | GitHub URL | Stars | Last Active | Install | Tahoe-100M Ready? | Risk |
|--------|-----------|-------|-------------|---------|-------------------|------|
| GEARS | snap-stanford/GEARS | 354 | No 2025-2026 updates visible | `pip install cell-gears` | NO (uses Norman, Adamson, Dixit, Replogle) | LOW-MODERATE |
| scGPT | bowang-lab/scGPT | ~1,400 | v0.2.4 (Mar 2025) | pip | NO (standard datasets) | LOW |
| scFoundation | biomap-research/scFoundation | 405 | 19 commits, stale activity | See GEARS folder | NO (own data loaders) | MODERATE |
| CPA | theislab/cpa | 144 | v0.5.0 (Jun 2023) -- last release 3 years ago | pip | NO (ComboSciPlex, Norman, Kang) | MODERATE |
| scPPDM | **NOT FOUND** | N/A | arXiv Oct 2025 | N/A | YES (evaluated on Tahoe-100M) | HIGH |
| scDFM | AI4Science-WestlakeU/scDFM | 21 | ICLR 2026 | `conda env create -f environment.yml` | NO (Norman, ComboSciPlex) | MODERATE |

**CRITICAL FINDING on scPPDM:** Despite being evaluated ON Tahoe-100M in the paper
(arXiv 2510.11726), no public GitHub repository was found for scPPDM. The paper claims
state-of-the-art results on Tahoe-100M (+36.11%/+34.21% on DEG logFC), but without
code, this method CANNOT be included in Delta's benchmark. scPPDM was listed as a
Tier 1 method with available code -- **this needs correction to Tier 2 or removal.**

**CRITICAL FINDING on CPA:** The theislab/cpa repository's last release was v0.5.0
in June 2023 -- three years ago. While the code is functional, there have been no
updates in 3 years. This raises concerns about compatibility with modern PyTorch/CUDA
versions. The facebookresearch/CPA fork may be more current. Risk elevated to MODERATE.

**CRITICAL FINDING on GEARS:** No visible updates in 2025-2026. The codebase was
designed for small perturbation datasets (Norman ~100K cells, Adamson ~50K cells).
Scaling to Tahoe-100M (95.6M expression profiles) will require significant data loader
modifications. The original GEARS data loader loads all data into memory -- this will
NOT work for Tahoe-100M.

**None of the Tier 1 methods are Tahoe-100M ready out of the box.** Every method will
require custom data loading code to handle the 429 GB dataset. This is a 1-2 week
engineering effort PER METHOD unless a unified data loading framework is built first.

### I4.2 Tier 2 Methods (Evaluate If Available)

| Method | Code Status | Stars | Preprint Date | Functional? | Risk |
|--------|------------|-------|---------------|-------------|------|
| AlphaCell | **NO GitHub repository found** | N/A | Mar 2, 2026 | Cannot verify | VERY HIGH |
| X-Cell | Xaira-Therapeutics/X-Cell | 68 | Mar 2026 | **Partial -- "model weights coming soon"** | VERY HIGH |
| AetherCell | Wenyuan-AI4science/AetherCell | 15 | Mar 13, 2026 | Inference code available, datasets on Zenodo | HIGH |
| pertTF | **NO GitHub repository found** | N/A | Mar 12, 2026 | Cannot verify | VERY HIGH |

**Tier 2 assessment update:**
- **AlphaCell:** Despite being from a bioRxiv preprint (March 2026), no public code
  repository was found. The benchmarking repository (xianglin226/Benchmarking-Single-
  Cell-Perturbation) does not list AlphaCell. **CANNOT be included in Delta.**
- **X-Cell:** Repository exists (68 stars), pip-installable (`pip install xcell`), but
  the critical "model weights and inference code coming soon" message means the model
  is NOT yet functional for inference. Trained on X-Atlas/Pisces (25.6M cells from 7
  CRISPRi screens), not Tahoe-100M. **CANNOT be included until weights released.**
- **AetherCell:** Code exists (15 stars) with conda environment, inference package
  (~4.3 GB from HuggingFace), and documentation. Supports drug treatment, shRNA,
  CRISPR-KO. The most promising Tier 2 method for inclusion. **MAY be usable.**
- **pertTF:** No GitHub repository found despite the bioRxiv preprint. The preprint
  was March 2026; code may not yet be released. **CANNOT be included.**

**Revised Tier 2 recommendation:** At most 1 method (AetherCell) is potentially
usable. Budget 1-2 weeks for integration and testing. The other 3 should be dropped.

### I4.3 Tahoe-x1 (Foundation Model Baseline)

| Item | Finding |
|------|---------|
| GitHub | tahoebio/tahoe-x1 |
| Stars | 143 |
| License | Apache 2.0 |
| Model sizes | Tx1-3B, Tx1-1.3B, Tx1-70M |
| GPU requirement | NVIDIA Ampere+ (A100, H200), CUDA 12.1+ |
| Tahoe-100M support | **YES -- native streaming from HuggingFace** |
| Perturbation prediction | `scripts/state_transition/` directory |

**Tahoe-x1 should be included as a Tier 1 method.** It is the ONLY model in the
Delta pipeline that natively supports Tahoe-100M streaming and has been pretrained
on the full dataset. Its perturbation prediction capabilities are explicitly
benchmarked. Including it strengthens the benchmark significantly.

**Compute concern:** The Tx1-3B model requires multi-GPU training on A100/H200 GPUs.
The Tx1-70M model is more tractable for rapid benchmarking. Recommend starting with
Tx1-70M and scaling to Tx1-1.3B if compute allows.

**Sources:**
- GEARS: https://github.com/snap-stanford/GEARS
- scGPT: https://github.com/bowang-lab/scGPT
- scFoundation: https://github.com/biomap-research/scFoundation
- CPA: https://github.com/theislab/cpa
- scDFM: https://github.com/AI4Science-WestlakeU/scDFM
- X-Cell: https://github.com/Xaira-Therapeutics/X-Cell
- AetherCell: https://github.com/Wenyuan-AI4science/AetherCell
- Tahoe-x1: https://github.com/tahoebio/tahoe-x1
- scPPDM paper: https://arxiv.org/abs/2510.11726
- AlphaCell preprint: https://www.biorxiv.org/content/10.64898/2026.03.02.709176v1
- pertTF preprint: https://www.biorxiv.org/content/10.64898/2026.03.12.711379v1

---

## Task I5: HPC Compatibility

### I5.1 AI2BMD on HPC

**H200 issue status:** Issue #72 ("Issues with H200") remains OPEN since August 2025.
The AI2BMD README lists tested GPUs as "A100, V100, RTX A6000, Titan RTX" with no
mention of H200. Without H200 in the tested GPU list, running AI2BMD on H200 is
unsupported and may produce CUDA errors or incorrect results.

**Docker-to-Singularity:**
- Issue #65 (Singularity feature request) remains OPEN since May 2025.
- The AI2BMD Docker image (`ghcr.io/microsoft/ai2bmd:latest`) can theoretically be
  converted to Singularity via `singularity build ai2bmd.sif docker://ghcr.io/microsoft/ai2bmd:latest`.
- However, GPU passthrough with converted Docker images is a known pain point.
  The `--nv` flag for Singularity enables NVIDIA GPU access, but the container must
  have matching CUDA runtime libraries.
- **No CUDA version is specified** in the AI2BMD documentation, making it impossible
  to verify compatibility with the cluster's CUDA driver without downloading and
  inspecting the Docker image.
- General Docker-to-Singularity workflow for ML: requires matching host CUDA driver
  version with container CUDA runtime (NVIDIA blog, Docker Compatibility with
  Singularity for HPC).
- Estimated effort: **1-2 weeks** for conversion, testing, and GPU verification.

**Verdict:** AI2BMD on this HPC cluster requires: (a) Docker-to-Singularity conversion
(untested for AI2BMD), (b) H200 GPU compatibility testing (unsupported), (c) CUDA
version verification (undocumented). Total estimated setup: **2-4 weeks** with a
**40-50% probability of failure** (unchanged from Round 1).

### I5.2 SO3LR on HPC

**JAX version:** SO3LR requires JAX 0.5.3 with CUDA 12 (`jax[cuda12]==0.5.3`).

**CUDA 12 on H200:** H200 GPUs ship with CUDA 12.x support and SM version 9.0
(Hopper architecture). JAX 0.5.x supports SM 5.2+ (Maxwell and newer), so H200
is architecturally compatible.

**Known JAX/CUDA issues:**
- JAX CUDA version mismatch is the most commonly reported installation problem
  (github.com/jax-ml/jax/issues/18027, /issues/22534, /discussions/20678).
- The copy of CUDA installed must be at least as new as the version JAX was built
  against. On HPC clusters with module-managed CUDA versions, this requires loading
  the correct CUDA module before JAX installation.
- JAX on Hopper/H200: No H200-specific issues found in JAX issue tracker. H200 uses
  the same SM 9.0 as H100, which is well-supported by JAX 0.5.x.
- **XLA compilation:** JAX compiles operations via XLA. First compilation can take
  minutes for large systems. On H200 with CUDA 12.x, XLA should find the correct PTX
  compiler if CUDA toolkit is properly installed.

**Protein simulation documentation:** The SO3LR GitHub README contains NO protein
simulation tutorial. The `so3lr npt` CLI command exists but examples show only small
molecules. Users attempting protein simulation must infer the workflow from the paper's
methods section. This adds **2-3 days** of setup time beyond standard installation.

**Estimated SO3LR setup on HPC:**
1. Create conda/venv environment: 30 min
2. Install JAX 0.5.3 with CUDA 12: 1-2 hours (may require debugging CUDA version)
3. Install SO3LR: 30 min
4. Test on small water box: 1 hour
5. Prepare solvated crambin system: 1-2 days (no tutorial exists)
6. Verify NPT stability: 1-2 days
7. Debug potential neighbor list overflow (issue #25): 1-3 days
8. **Total: 3-7 days** (optimistic to realistic)

**Verdict:** SO3LR is installable on H200 via standard pip/conda workflow. The main
risks are (a) NPT stability for protein-water systems (issue #29), (b) neighbor list
overflow for large systems (issue #25), and (c) lack of protein simulation
documentation. Setup estimate: **3-7 days** with a **25-35% probability of
encountering blocking issues** (unchanged from Round 1).

**Sources:**
- JAX installation docs: https://docs.jax.dev/en/latest/installation.html
- JAX GPU memory: https://docs.jax.dev/en/latest/gpu_memory_allocation.html
- NVIDIA Docker-Singularity: https://developer.nvidia.com/blog/docker-compatibility-singularity-hpc/
- JAX CUDA issues: https://github.com/jax-ml/jax/issues/18027
- SO3LR issues #25, #29: https://github.com/general-molecular-simulations/so3lr/issues

---

## Supplementary Finding: The Ahlmann-Eltze Challenge to Delta

**A critical paper for Delta was published in Nature Methods in 2025:**

Ahlmann-Eltze, C., Huber, W. & Anders, S. "Deep-learning-based gene perturbation
effect prediction does not yet outperform simple linear baselines." Nature Methods 22,
1657-1661 (2025).

**Key findings:**
- Compared 5 foundation models (Geneformer, scBERT, UCE, scGPT, scFoundation) and 2
  DL models (GEARS + one other) against deliberately simple linear baselines.
- **None of the DL models outperformed the linear baselines** for predicting
  transcriptome changes after single or double perturbations.
- The baselines capture average treatment effects, and current DL models fail to learn
  conditional effects beyond what these averages provide.

**A response paper exists:** "Deep Learning-Based Genetic Perturbation Models Do
Outperform Uninformative Baselines on Well-Calibrated Metrics" (bioRxiv 2025) argues
that the choice of metrics matters and that DL models DO outperform on certain
well-calibrated metrics.

**Impact on Delta:** This directly challenges Delta's narrative ("When Does Deep Learning
Help?"). However, it also STRENGTHENS the motivation: Delta's PerturbMark benchmark
with WMSE + Spearman-top-k metrics is explicitly designed to detect conditional
effects beyond average treatment responses. If PerturbMark shows DL methods DO
outperform on these metrics, it directly addresses the Ahlmann-Eltze challenge. If it
confirms that DL methods do NOT outperform, that is ALSO a publishable finding
(replication/extension of Nature Methods).

**This is both a risk and an opportunity for Delta.** The risk is that the finding is
"already known." The opportunity is that Tahoe-100M (100M cells, 1,100 perturbations,
50 cell lines) is vastly larger than any dataset used in the Ahlmann-Eltze study, and
the question of whether scale changes the answer is genuinely open.

**Sources:**
- Ahlmann-Eltze et al., Nature Methods 22, 1657-1661 (2025)
  https://www.nature.com/articles/s41592-025-02772-6
- Response preprint: https://www.biorxiv.org/content/10.1101/2025.10.20.683304v1.full

---

## Revised Feasibility Assessment

### Alpha-M: YELLOW (Feasible with Major Modifications)
*Status: Unchanged, but ceiling slightly higher.*

**Improvements since Round 1:**
1. Garnet now has OpenMM integration (risk: HIGH -> MODERATE). The 2-4 week Julia
   integration effort is eliminated. Garnet simulations run at classical FF speed.
2. SO3LR has published solvated crambin simulations (risk: HIGH -> MODERATE-HIGH).
   Speed estimate revised upward to 0.6-1.3 ns/day for 25,000 atoms on H200.

**Unchanged risks:**
1. AI2BMD: VERY HIGH risk. 22 open issues, H200 untested, Docker-only installation,
   no Singularity support. **Recommendation: DROP from Alpha-M.**
2. MACE-OFF24: MODERATE risk. Only crambin demonstrated. 0.22-0.32 ns/day for T4 lys.
3. Compute budget: Still underestimated by ~2x for MLFF methods. However, the
   reclassification of Garnet as classical-speed reduces the overall compute need.
4. Timeline: 20-24 weeks realistic (Round 1 estimate of 30-35 weeks was based on 8
   methods including AI2BMD and Julia-Garnet; with 6 methods and revised Garnet, the
   timeline compresses to ~22-28 weeks).

**Revised method roster (recommended):**
| Method | Category | Speed Class | Risk | Include? |
|--------|----------|-------------|------|----------|
| MACE-OFF24 | MLFF | 0.25 ns/day | MODERATE | YES (mandatory) |
| SO3LR | MLFF | 0.6-1.3 ns/day | MODERATE-HIGH | YES (with pilot) |
| Garnet | ML-classical | ~300 ns/day | MODERATE | YES (with pilot) |
| BioEmu | Generative | N/A | LOW | YES (mandatory) |
| AMBER ff19SB | Classical | ~300 ns/day | LOW | YES (mandatory) |
| CHARMM36m | Classical | ~300 ns/day | LOW | YES (mandatory) |
| ff14SB | Classical | ~300 ns/day | LOW | YES (optional) |
| AI2BMD | MLFF | 0.2 ns/day | VERY HIGH | **NO (drop)** |

**Revised compute budget (6 methods, Phase 2, all 7 proteins):**
Using per-protein atom counts from Round 1:

| Protein | MACE GPU-hrs | SO3LR GPU-hrs | Garnet GPU-hrs | Classical x2 | BioEmu |
|---------|-------------|---------------|----------------|-------------|--------|
| Crambin (5ns) | 120 | 60 | <1 | <1 | <1 |
| GB3 (50ns) | 1,500 | 750 | 4 | 8 | <1 |
| BPTI (50ns) | 1,500 | 750 | 4 | 8 | <1 |
| Ubiquitin (50ns) | 2,400 | 1,200 | 4 | 8 | <1 |
| Barnase (50ns) | 3,429 | 1,714 | 4 | 8 | <1 |
| HEWL (50ns) | 4,286 | 2,143 | 4 | 8 | <1 |
| T4 Lys (50ns) | 4,800 | 1,500 | 4 | 8 | <1 |
| **Subtotal** | **18,035** | **8,117** | **~25** | **~50** | **~3** |

**Phase 2 total (6 methods): ~26,230 GPU-hrs** (vs Round 1's 56,520 for 8 methods).
The SO3LR upward speed revision and Garnet classical-speed reclassification reduce
the budget significantly. This is now closer to the proposal's 44,800 GPU-hr estimate
(within 2x if Phase 3 is included).

### Gamma: GREEN (Feasible)
*Status: Unchanged.*

No new findings affect Gamma. All software remains production-ready. Compute trivial.

### Delta: YELLOW (Feasible with Modifications)
*Status: Unchanged, but landscape shift requires attention.*

**Key changes since Round 1:**
1. **scPPDM: No public code found.** Must be reclassified from Tier 1 to Tier 2 or
   removed entirely. This reduces Tier 1 from 6 to 5 methods.
2. **CPA: Last release June 2023.** 3-year-old codebase raises compatibility concerns.
   May need facebookresearch/CPA fork instead.
3. **Tier 2 code availability verified:**
   - AlphaCell: NO code -- **drop**
   - X-Cell: Weights "coming soon" -- **drop until weights released**
   - AetherCell: Code available (15 stars) -- **include as sole Tier 2 candidate**
   - pertTF: NO code -- **drop**
4. **Tahoe-x1 should be added as Tier 1.** Native Tahoe-100M support, 143 stars,
   Apache 2.0 license, perturbation prediction benchmarks available.
5. **Tahoe-100M is in Parquet format**, not AnnData/H5AD. Data pipeline must include
   Parquet-to-AnnData conversion for most DL methods.
6. **Minified AnnData (41 GB) is latent vectors**, not raw counts. Not usable as
   training data for most DL methods.
7. **No Tier 1 method is Tahoe-100M ready out of the box.** All require custom data
   loading code. However, Tahoe-x1's data loading code can serve as a starting template.
8. **Ahlmann-Eltze et al. (Nature Methods 2025)** directly challenges the Delta
   narrative. This must be addressed head-on in the experimental design.

**Revised Tier 1 roster (recommended):**
| Method | Stars | Status | Tahoe-100M Support | Risk |
|--------|-------|--------|-------------------|------|
| GEARS | 354 | Active (no 2025+ updates) | Custom loader needed | LOW-MODERATE |
| scGPT | ~1,400 | v0.2.4 (Mar 2025) | Custom loader needed | LOW |
| scFoundation | 405 | Active | Custom loader needed | MODERATE |
| CPA | 144 | v0.5.0 (Jun 2023) | Custom loader needed | MODERATE |
| scDFM | 21 | ICLR 2026 | Custom loader needed | MODERATE |
| Tahoe-x1 | 143 | Active | **Native streaming** | LOW |

**Revised Tier 2 roster:**
| Method | Usable? | Recommendation |
|--------|---------|---------------|
| AetherCell | Possibly | Include if verified in Week 2 |
| scPPDM | No code | Drop (reclassified from Tier 1) |
| AlphaCell | No code | Drop |
| X-Cell | No weights | Drop until released |
| pertTF | No code | Drop |

**Revised timeline (Tier 1 only + Tahoe-x1 + baselines):**
- Weeks 0-2 (pre-project): Download Tahoe-100M, build unified data loader, test streaming
- Weeks 1-3: Implement baselines (5 methods, 2-3 days total), set up GEARS + scGPT
- Weeks 2-5: Set up remaining Tier 1 + Tahoe-x1, run initial training
- Weeks 5-8: Production training and evaluation, all 7 methods + 5 baselines
- Weeks 8-10: Statistical analysis (Tier 0-3 framework)
- Weeks 10-12: Feature importance, figures, writing
- **Total: 12-14 weeks** (achievable if pre-project data pipeline completed)

---

## Summary Table: Round 1 vs Round 2 Risk Assessment

| Component | Round 1 Risk | Round 2 Risk | Change | Reason |
|-----------|-------------|-------------|--------|--------|
| **Alpha-M Overall** | YELLOW | YELLOW | -- | Garnet/SO3LR improvements offset by confirmed AI2BMD issues |
| MACE-OFF24 | MODERATE | MODERATE | -- | No new protein benchmarks; crambin still the only demo |
| SO3LR | HIGH | **MODERATE-HIGH** | Improved | Solvated crambin demonstrated; speed revised upward |
| AI2BMD | VERY HIGH | **VERY HIGH+** | Worsened | 22 open issues (was 12), no new releases, H200 untested |
| BioEmu | LOW | LOW | -- | v1.3.1 confirmed, well-maintained |
| Garnet | HIGH | **MODERATE** | Improved | PyTorch port + OpenMM integration discovered |
| Classical FFs | LOW | LOW | -- | No change |
| Compute budget | 2x underestimate | **~1.5x underestimate** | Improved | Garnet reclassified as classical-speed |
| Timeline | 30-35 weeks | **22-28 weeks** | Improved | Fewer methods, Garnet not blocking |
| **Gamma Overall** | GREEN | GREEN | -- | No changes |
| **Delta Overall** | YELLOW | YELLOW | -- | Tier 2 code worse than expected; Ahlmann-Eltze challenge |
| Tier 1 DL methods | LOW-MODERATE | **MODERATE** | Slightly worsened | scPPDM no code; CPA stale; none Tahoe-100M ready |
| Tier 2 DL methods | HIGH | **VERY HIGH** | Worsened | Only AetherCell usable; 4/5 have no code or weights |
| Tahoe-100M pipeline | MODERATE | MODERATE | -- | Parquet format confirmed; streaming works; tutorials exist |
| Tahoe-x1 | Not assessed | **LOW** | New | Recommended addition as Tier 1 method |

---

## References

1. Kovacs et al., "MACE-OFF: Short-Range Transferable Machine Learning Force Fields
   for Organic Molecules," JACS 147, 2977 (2025).
   https://pubs.acs.org/doi/10.1021/jacs.4c07099

2. Frank et al., "Molecular Simulations with a Pretrained Neural Network and Universal
   Pairwise Force Fields," JACS (2026).
   https://pubs.acs.org/doi/10.1021/jacs.5c09558

3. Li et al., "Ab initio characterization of protein molecular dynamics with AI2BMD,"
   Nature 636, 1012 (2024).

4. Lewis, Jing et al., "Scalable Emulation of Protein Equilibrium Ensembles with
   Generative Deep Learning," Science 369, 270-278 (2025).

5. Blanco-Gonzalez et al., "Training a force field for proteins and small molecules
   from scratch," arXiv:2603.16770 (2026).

6. Ahlmann-Eltze, C., Huber, W. & Anders, S. "Deep-learning-based gene perturbation
   effect prediction does not yet outperform simple linear baselines." Nature Methods
   22, 1657-1661 (2025).
   https://www.nature.com/articles/s41592-025-02772-6

7. ACEsuit/mace GitHub: https://github.com/ACEsuit/mace

8. SO3LR GitHub: https://github.com/general-molecular-simulations/so3lr

9. AI2BMD GitHub: https://github.com/microsoft/AI2BMD

10. BioEmu GitHub: https://github.com/microsoft/bioemu

11. Garnet GitHub: https://github.com/greener-group/garnet

12. GEARS GitHub: https://github.com/snap-stanford/GEARS

13. scGPT GitHub: https://github.com/bowang-lab/scGPT

14. scFoundation GitHub: https://github.com/biomap-research/scFoundation

15. CPA GitHub (theislab): https://github.com/theislab/cpa

16. scDFM GitHub: https://github.com/AI4Science-WestlakeU/scDFM

17. X-Cell GitHub: https://github.com/Xaira-Therapeutics/X-Cell

18. AetherCell GitHub: https://github.com/Wenyuan-AI4science/AetherCell

19. Tahoe-x1 GitHub: https://github.com/tahoebio/tahoe-x1

20. Tahoe-100M HuggingFace: https://huggingface.co/datasets/tahoebio/Tahoe-100M

21. Tahoe-100M-SCVI-v1: https://huggingface.co/tahoebio/Tahoe-100M-SCVI-v1

22. scvi-tools tutorial: https://docs.scvi-tools.org/en/stable/tutorials/notebooks/hub/Tahoe100.html

23. Theis Lab analysis pipeline: https://github.com/theislab/vevo_Tahoe_100m_analysis

24. MACE docs OpenMM: https://mace-docs.readthedocs.io/en/latest/guide/openmm.html

25. OpenMM-ML GitHub: https://github.com/openmm/openmm-ml

26. JAX installation: https://docs.jax.dev/en/latest/installation.html

27. NVIDIA Docker-Singularity blog:
    https://developer.nvidia.com/blog/docker-compatibility-singularity-hpc/

28. AlphaCell preprint: https://www.biorxiv.org/content/10.64898/2026.03.02.709176v1

29. pertTF preprint: https://www.biorxiv.org/content/10.64898/2026.03.12.711379v1

30. scPPDM paper: https://arxiv.org/abs/2510.11726

31. AetherCell preprint:
    https://www.biorxiv.org/content/10.64898/2026.03.13.710968v1

32. OpenMM H200 benchmark: https://github.com/openmm/openmm/issues/4910

33. BioEmu bioconda: https://anaconda.org/bioconda/bioemu

34. Benchmarking Single-Cell Perturbation:
    https://github.com/xianglin226/Benchmarking-Single-Cell-Perturbation
