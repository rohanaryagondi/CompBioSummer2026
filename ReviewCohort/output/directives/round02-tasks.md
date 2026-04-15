---
agent: ReviewCohort Orchestrator (orch)
round: 2
date: 2026-04-15
type: directive
---

# Round 2 Directives: Deep Verification Research

## Purpose

Round 1 identified 8 critical uncertainties that could change the go/no-go
decision for each proposal. Round 2 assigns each reviewer targeted verification
tasks to resolve these uncertainties through internet research. Every claim must
be backed by specific evidence: paper citations with numbers, GitHub commit
dates, database entries, or documented impossibility.

**Output:** Each reviewer writes to
`ReviewCohort/output/research/<shortname>-verification-R02.md`

**Deadline:** Complete verification before Round 3 deliberation begins.

---

## dynrev: MLFF Trajectory Feasibility & Convergence Verification

**Output file:** `output/research/dynrev-verification-R02.md`

### Task D1: Maximum Published MLFF Protein Trajectory Lengths

Search for the longest published/documented MLFF trajectories on solvated
proteins. For each MLFF (MACE-OFF24, SO3LR, AI2BMD, GEMS, AceFF), find:

- Longest continuous trajectory (ns) on a solvated protein
- Largest protein system (residues, total atoms with solvent)
- Whether NPT or NVT
- GPU type and ns/day achieved
- Any documented instabilities or crashes

Check: bioRxiv, arXiv, GitHub Issues/Discussions, conference proceedings
(ACS Spring 2026, Biophysical Society 2026), MLIP workshop papers,
OpenMM forum posts.

**Specific questions to answer:**
1. Has anyone run MACE-OFF24 beyond 1.6 ns on any protein larger than crambin?
2. Has SO3LR ever been used on a solvated protein (not just water)?
3. What is the longest continuous AI2BMD protein trajectory (not aggregated from
   many short trajectories)?
4. Has GEMS been tested on any protein beyond crambin?
5. Are there any MLFF stability solutions (StABlE Training, active learning
   loops) that enable longer trajectories?

### Task D2: GEMS Force Field Assessment

You identified GEMS (Unke et al., Sci. Adv. 2024) as a potential fallback.
Verify:
- Current code availability and maintenance status
- Whether it supports solvated protein NPT
- Whether the 10 ns crambin result has been replicated
- Speed (ns/day) on relevant hardware
- Any limitations for the Alpha-M benchmark proteins

### Task D3: BioEmu Updates and Competitors

Search for:
- BioEmu v2 or any announced updates since v1.3.1 (April 2026)
- The BioEmu augmented MD preprint (bioRxiv Jan 2026) -- has it been published?
  Has it been extended to fitness prediction?
- Any Microsoft Research publications connecting BioEmu to ProteinGym or DMS
- Head-to-head comparisons of BioEmu vs Boltz-2 vs AlphaFlow on protein
  ensemble quality metrics (RMSF, S2, contacts)

### Task D4: Garnet Benchmark Contamination Details

Verify the exact Garnet training/validation set:
- Which specific proteins were used for NMR J-coupling training?
- Which were validation only?
- What were the per-protein performance numbers?
- Can Garnet parameters be exported to OpenMM/GROMACS format, or is Molly.jl
  the only option?

---

## biomlrev: Gamma Novelty & Baseline Verification

**Output file:** `output/research/biomlrev-verification-R02.md`

### Task B1: ProteinGym 2026 Leaderboard Exact State

Access proteingym.org and document:
- Current top-20 methods with exact Spearman scores
- RSALOR exact performance by assay type (stability, binding, activity,
  expression, fitness)
- Whether any method explicitly uses dynamics features
- Total number of assays (was 217 in v1.0 -- has it been updated?)
- Any new submission guidelines or evaluation changes

### Task B2: RSALOR Deep Dive

Find and read the Tsishyn et al. (Bioinformatics 2025) paper in detail:
- Exact method: how are conservation and RSA combined?
- Per-assay-type Spearman breakdown (stability, binding, catalysis, expression)
- Which proteins/assays does RSALOR perform best/worst on?
- Does RSALOR use MSA depth as a feature? (If so, how does it handle proteins
  with shallow MSAs?)
- Is code available? Is it trivially reproducible?

### Task B3: Boltz-2 vs BioEmu Head-to-Head

Find the Boltz-2 paper (Wohlwend et al., bioRxiv June 2025) and verify:
- Exact RMSF correlation metrics vs ground-truth MD (which benchmarks?)
- Head-to-head with BioEmu on identical proteins
- Speed comparison (samples/min)
- Does Boltz-2 generate backbone-only or all-atom?
- Is it open-source and production-ready?

### Task B4: Prior Art Paper Details

For each paper, find exact methods and results:

1. **Ozkan et al. (PNAS 2025):** Which 4 ProteinGym proteins? What Spearman
   scores? Does their dynamics-GNN generalize beyond 4 proteins? Is code
   available?

2. **Burgin QDPR (JCIM 2025):** Which MD features exactly? What ML method?
   Results on GB1 and AvGFP? Is this replicable at scale?

3. **MutRobustness preprint (bioRxiv March 2026):** Exact correlation values.
   Which proteins tested? Is this from ThermoMPNN predictions only or also
   experimental data? How does it intersect with Gamma's planned analysis?

4. **ESMDance/SeqDance (PNAS 2026):** Exact Spearman on ProteinGym (overall
   and per-assay-type). How was it trained? Does it provide per-residue
   predictions or per-protein? Is the improvement over ESM2 consistent?

### Task B5: NCS 2025-2026 Benchmark Paper Acceptances

Search Nature Computational Science for:
- All papers published in 2025-2026 that are primarily benchmarks or
  evaluation studies
- Papers connecting conformational ensembles to biological function
- Papers using BioEmu, ProteinGym, or ML force fields
- The exact editorial policy on "straightforward ML" -- find the editorial
  statement and any clarifications

---

## statrev: Power Analysis & Statistical Framework Verification

**Output file:** `output/research/statrev-verification-R02.md`

### Task S1: Integration Power Under Realistic Scenarios

Conduct a systematic conceptual power analysis for the integration test under
multiple scenarios. For each, estimate power using published approximations:

| Scenario | Proteins | Generators | True rho | ICC(protein) | Test |
|----------|----------|-----------|----------|-------------|------|
| Current | 6 | 8 | 0.3 | 0.40 | Mixed-effects |
| Current | 6 | 8 | 0.5 | 0.40 | Mixed-effects |
| Expanded | 8 | 8 | 0.3 | 0.40 | Mixed-effects |
| Expanded | 8 | 8 | 0.5 | 0.40 | Mixed-effects |
| Expanded | 10 | 10 | 0.3 | 0.40 | Mixed-effects |
| Expanded | 10 | 10 | 0.5 | 0.40 | Mixed-effects |
| Current + Boltz-2 | 6 | 10 | 0.5 | 0.40 | Mixed-effects |
| Large | 14 | 10 | 0.3 | 0.40 | Mixed-effects |

For each, report: estimated power, minimum detectable effect at 80% power,
and whether Kenward-Roger correction is sufficient for the cluster count.

### Task S2: Cluster Bootstrap Bias with High ICC

Search for published simulation studies on cluster bootstrap performance with:
- Very high within-cluster ICC (>0.70)
- Small number of clusters (5-10)
- Continuous outcomes

Verify Huang (2018) findings and determine whether they apply to our design.
What is the expected bias in standard error estimates? What alternative
approaches (wild cluster bootstrap, multi-level bootstrap) perform better?

### Task S3: Bayesian Prior Defensibility

Research Bayesian correlation analysis with small samples:
- What priors have been used in similar contexts (method comparison with
  N~50 observations)?
- How sensitive is the Bayes Factor to prior choice at N_eff~15?
- Find published examples of Bayesian signed-rank or correlation tests in
  bioinformatics with comparable sample sizes.
- Assess whether the proposed prior N(0.5, 0.15^2) is defensible or whether
  the range should be broader.

### Task S4: Delta BY vs BH Survival Rate Estimation

For the Delta benchmark design (~80 primary comparisons), compute:
- Expected number of surviving significant results under BY at various
  effect size distributions
- Same under BH
- Compare to Westfall-Young permutation FDR
- Find published perturbation benchmarks and their actual FDR correction
  choices (what did scPerturBench, Systema, and PerturBench use?)

### Task S5: ICC Estimation for S2 from Published Data

Search for published per-protein S2 profiles:
- Find S2 values for ubiquitin, GB3, BPTI, and barnase from published MD
  studies (ideally Smith et al. 2024 or Lindorff-Larsen 2012)
- Estimate the within-protein ICC for S2 from the published per-residue values
- If possible, find published estimates of ICC for NMR S2 values

---

## implrev: Software Readiness & Infrastructure Verification

**Output file:** `output/research/implrev-verification-R02.md`

### Task I1: GitHub Repository Status Check (April 2026)

For each tool, check the GitHub repository and document:

| Repository | Check Items |
|-----------|------------|
| ACEsuit/mace | Latest release, open issues count, recent commits, protein examples, OpenMM-ML compatibility |
| general-molecular-simulations/so3lr | Latest version, solvated protein examples (any?), JAX version requirements, NPT on protein? |
| microsoft/AI2BMD | Issue #72 (H200) status, Issue #63 (thermostat) status, Issue #70 (custom systems), Singularity support (#65) |
| microsoft/bioemu | Latest version (confirm v1.3.1), known issues, CUDA requirements |
| greener-group/garnet | Code release status, Julia version, Molly.jl version, any OpenMM export tools? |

### Task I2: ns/day Benchmarks for MLFF on Protein Systems

Search for any published or reported ns/day benchmarks for MLFFs on solvated
protein systems. Check:
- Published papers (especially supplementary information)
- GitHub benchmarks or READMEs
- Conference presentations (slides, posters)
- Community forums (OpenMM discuss, JAX GitHub)

For each benchmark found, record: system size (atoms), GPU type, ns/day,
simulation type (NVT/NPT), and stability duration.

### Task I3: Tahoe-100M Data Pipeline Verification

Verify the Tahoe-100M dataset logistics:
- Current size and format on Hugging Face
- Is the minified version (41 GB) documented and up to date?
- What processing tools are recommended (scanpy backed mode, Dask)?
- Has anyone published a tutorial or pipeline for running DL methods on
  Tahoe-100M?
- What is Tahoe-x1's data preprocessing -- can PerturbMark reuse it?

### Task I4: DL Model Code Availability (Tier 1 and Tier 2)

For each Delta method, verify current code availability:

| Method | GitHub URL | Stars | Last Commit | Tahoe-100M compatible? | Install docs? |
|--------|-----------|-------|-------------|----------------------|--------------|
| GEARS | | | | | |
| scGPT | | | | | |
| scFoundation | | | | | |
| CPA | | | | | |
| scPPDM | | | | | |
| scDFM | | | | | |
| AlphaCell | | | | | |
| X-Cell | | | | | |
| AetherCell | | | | | |
| pertTF | | | | | |
| Tahoe-x1 | | | | | |

### Task I5: HPC Compatibility Assessment

For AI2BMD specifically:
- Has the H200 issue (#72) been resolved?
- Is Docker-to-Singularity conversion documented anywhere?
- Has anyone successfully run AI2BMD on an HPC cluster with Singularity?
- What CUDA version does AI2BMD require?

For SO3LR:
- What JAX version is required? Does it work with CUDA 12.x on H200?
- Has anyone documented protein simulation with SO3LR (even informally)?

---

## stratrev: Competition Scan & Publication Strategy Verification

**Output file:** `output/research/stratrev-verification-R02.md`

### Task T1: Deep Competition Scan (April 2026)

Search bioRxiv and arXiv for preprints posted in April 2026 (since April 1)
in the following areas:

1. **BioEmu + fitness/function:** Any preprint connecting BioEmu ensembles to
   mutation effects, fitness prediction, or functional assays
2. **MLFF + protein dynamics benchmark:** Any systematic MLFF comparison on
   proteins against experimental observables
3. **Perturbation prediction benchmark:** Any new benchmark, method evaluation,
   or Tahoe-100M analysis
4. **Dynamics-fitness connection:** Any paper predicting mutation effects from
   conformational dynamics

For each found, assess: threat level (direct/adjacent/peripheral), timeline
to publication, and impact on our differentiation.

### Task T2: NCS 2025-2026 Table of Contents Analysis

Systematically review Nature Computational Science volumes from January 2025
to April 2026. For each issue, identify:
- All Research Articles (not Reviews, Comments, or News)
- Categorize by: computational method + biological domain
- Flag any that overlap with our proposals' conceptual territory
- Identify the editorial pattern: what gets in, what doesn't?

### Task T3: Title Testing Against NCS Editorial Criteria

For the top 3 combined-paper titles from Round 1:
1. "Physical accuracy of protein ensembles predicts functional utility across
   mutation fitness landscapes"
2. "From validated dynamics to biological function: connecting force field
   accuracy to mutation effect prediction"
3. "Does ensemble accuracy matter? Benchmarking ML force fields and connecting
   physical fidelity to protein fitness prediction"

Search NCS for published papers with similar title structures. Assess:
- Which format (claim, narrative arc, question) appears most in NCS?
- Character count (NCS prefers short titles, <100 characters)
- Whether "force field" appears in any NCS title (or if it's too technical)

### Task T4: scPerturBench and Tahoe-100M Extensions

Check whether:
- scPerturBench has been extended to Tahoe-100M (or announced plans to)
- The Virtual Cell Challenge has published evaluation criteria
- Tahoe Bio has published analysis guidelines for Tahoe-100M
- Any group has published a comprehensive evaluation of methods on Tahoe-100M
  (beyond Tahoe-x1's self-evaluation)

### Task T5: Pre-registration Precedents in Computational Biology

Search for examples of pre-registered computational biology studies:
- Has anyone pre-registered a benchmark study at OSF or equivalent?
- What level of detail is expected in the pre-registration?
- Are there NCS or Nature Methods papers that cite pre-registration as a
  strength?

---

## Research Standards for All Round 2 Agents

1. **Every claim must have a specific citation** (author, year, journal, and
   key finding or number).
2. **Use WebSearch and WebFetch** to find current information. Do not rely on
   knowledge cutoff.
3. **Distinguish between "confirmed" and "not found."** If you cannot find
   evidence for or against a claim, say so explicitly.
4. **Report negative results.** "I searched for X and found no evidence" is
   a valuable finding.
5. **Quantify everything.** Numbers, not adjectives.
6. **Output must be 300+ lines** with 15+ citations per reviewer.
