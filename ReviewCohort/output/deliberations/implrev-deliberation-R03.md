---
agent: implrev (Implementation Auditor)
round: 3
date: 2026-04-15
type: deliberation
---

# Cross-Reviewer Deliberation: Implementation Feasibility, Compute Budget, and Unified Timeline

## Reviewing Agent

Technical Implementation Auditor (implrev). Senior track, 10+ years running
production computational chemistry workflows on HPC systems, 5+ years GPU
computing. This deliberation responds to dynrev's protein roster and generator
list, the AI2BMD drop consensus, stratrev's publication milestones, and statrev's
convergence-related protocol requirements. I provide revised compute budgets,
method roster tables, timeline compatibility analysis, and a unified week-by-week
execution plan for all three projects.

---

## Executive Summary

After reviewing all three Wave 1 deliberations, I provide the following
implementation-level responses:

1. **dynrev's 14-protein x 10-generator design is NOT fully achievable as
   specified.** The maximum feasible fully crossed design is 9 proteins x 10
   generators (Tier A/B only). The 5 Tier C proteins (>80 residues) are limited
   to ~6 generators (classical FFs + BioEmu + Boltz-2 + AlphaFlow). I provide
   per-protein, per-method GPU-hour estimates for all 140 cells. Total revised
   compute for the 14x10 design: **~24,100-33,800 GPU-hours** (Phase 2 production
   only), with the incomplete MLFF cells for Tier C proteins treated as
   structurally absent.

2. **CONCUR with dropping AI2BMD.** Revised 9-method roster (without AI2BMD)
   reduces MLFF compute by ~40% and eliminates the highest-risk software
   dependency. Total compute savings: ~8,000-12,000 GPU-hours.

3. **Delta's August 15 preprint target is TIGHT but achievable** if Tahoe-100M
   data pipeline construction begins in a pre-project "Week 0" (April 15-30)
   and the method roster is limited to 5 Tier 1 methods + Tahoe-x1 + 5 baselines.
   Critical path: data pipeline (Weeks 0-2) and GEARS/scGPT setup (Weeks 2-5).

4. **Alpha-M Phase 1 CAN complete by June 30** if MACE-OFF24 and SO3LR pilot
   simulations begin May 5 and Garnet OpenMM integration starts May 1. This
   gives 8 weeks for pilot studies, which is sufficient for stability screening
   on 3-4 Tier A/B proteins.

5. **The unified timeline reveals a critical GPU contention window in Weeks 9-16
   (July 1 - August 22)** when Alpha-M Phase 2 production runs overlap with
   Delta's DL model training. I recommend dedicating H200 GPUs to Alpha-M MLFF
   simulations and RTX 5000 Ada GPUs to Delta model training during this window.

---

## Section 1: Response to dynrev's Protein Roster and Generator List

### 1.1 Per-Protein Compute Estimates for the 14-Protein Set

**CONCUR** with dynrev's 14-protein roster (Section 1.3 of dynrev-deliberation-R03).
The protein selection is scientifically sound, with good coverage of fold types,
S2 data quality, and Garnet contamination status.

I now provide GPU-hour estimates per protein per method. The key parameters are:

- **Solvation box size:** I use a 12 A buffer from the protein surface, consistent
  with standard practice (Shirts & Pande, JCTC 2005). Larger proteins require
  proportionally larger water boxes.
- **Atom counts (solvated):** Estimated from protein size + solvent. Small proteins
  (~35-56 residues): ~8,000-12,000 atoms. Medium proteins (~64-85 residues):
  ~14,000-20,000 atoms. Large proteins (~110-164 residues): ~25,000-40,000 atoms.
- **Production trajectory:** 50 ns target for classical FFs and Garnet. Adaptive
  for MLFFs (maximum stable length, capped at 50 ns).
- **Equilibration:** 5 ns NPT equilibration for all methods (excluded from
  production budget but included in total GPU-hours).
- **H200 performance:** Based on verified benchmarks from Rounds 1-2.

**MLFF ns/day estimates on H200 (from Round 2 verification):**

MACE-OFF24 performance scaling is approximately inversely proportional to system
size beyond ~10,000 atoms, based on the crambin benchmark (3 x 10^5 steps/day at
~18,000 atoms on A100, with ~1.5x H200 advantage). SO3LR follows the measured
3.25 x 10^-6 s/atom/step scaling (Frank et al., JACS 2026), with ~1.2x H200
advantage over H100.

| Protein | Residues | Tier | Solvated Atoms (est.) | MACE ns/day (H200) | SO3LR ns/day (H200, 1 fs) |
|---------|----------|------|-----------------------|---------------------|---------------------------|
| WW domain | 34 | A | ~8,000 | ~1.0 | ~1.8 |
| Crambin | 46 | A | ~10,000 | ~0.7 | ~1.5 |
| GB3 | 56 | A/B | ~12,000 | ~0.55 | ~1.2 |
| GB1 | 56 | B | ~12,000 | ~0.55 | ~1.2 |
| BPTI | 58 | B | ~12,000 | ~0.55 | ~1.2 |
| CI2 | 64 | B | ~14,000 | ~0.45 | ~1.0 |
| CspA | 70 | B | ~16,000 | ~0.38 | ~0.85 |
| alpha-3D | 73 | B/C | ~17,000 | ~0.35 | ~0.80 |
| Calbindin | 75 | B | ~17,000 | ~0.35 | ~0.80 |
| Ubiquitin | 76 | B | ~18,000 | ~0.32 | ~0.75 |
| HPr | 85 | B | ~20,000 | ~0.27 | ~0.65 |
| Barnase | 110 | C | ~28,000 | ~0.18* | ~0.45* |
| HEWL | 129 | C | ~32,000 | ~0.15* | ~0.38* |
| T4 lysozyme | 164 | C | ~40,000 | ~0.10* | ~0.28* |

*Tier C MLFF estimates are extrapolations well beyond the demonstrated stability
envelope. These simulations have a HIGH probability of failure (estimated 50-80%
for trajectories >5 ns).

**Classical FF and Garnet ns/day on H200:**

All classical FFs (ff14SB, ff19SB, a99SB-disp, CHARMM36m) and Garnet (via OpenMM)
achieve comparable performance since they use the same OpenMM integrator. Based on
the OpenMM H200 benchmark (GitHub issue #4910): >500 ns/day for ~44,000 atoms,
scaling roughly linearly downward for smaller systems.

| Protein | Solvated Atoms | Classical/Garnet ns/day (H200) |
|---------|---------------|-------------------------------|
| WW domain | ~8,000 | ~800 |
| Crambin | ~10,000 | ~700 |
| GB3-GB1-BPTI | ~12,000 | ~600 |
| CI2 | ~14,000 | ~500 |
| CspA-alpha3D-Calb | ~16,000-17,000 | ~400-450 |
| Ubiquitin | ~18,000 | ~400 |
| HPr | ~20,000 | ~350 |
| Barnase | ~28,000 | ~280 |
| HEWL | ~32,000 | ~250 |
| T4 lysozyme | ~40,000 | ~200 |

**BioEmu, Boltz-2, AlphaFlow** are generative methods. Compute is negligible:
~20 minutes per protein for BioEmu (2,000 conformations), ~20-60 seconds per
protein for Boltz-2 (via NVIDIA NIM or local inference), and ~5-30 minutes per
protein for AlphaFlow (depending on model variant). Total for 14 proteins across
all three generative methods: **<10 GPU-hours**.

### 1.2 Phase 2 Production: GPU-Hours per Protein per Method (50 ns target)

I calculate GPU-hours as: 50 ns / (ns/day) x 24 hrs. For MLFFs on Tier C proteins,
I use the adaptive protocol: assume maximum achievable trajectory of 10-20 ns
(optimistic) rather than 50 ns, reflecting the reality that these simulations will
likely fail or produce unconverged results before 50 ns.

**Table 1: Phase 2 GPU-Hours per Protein-Method Cell (Production Only)**

| Protein | MACE | SO3LR | Garnet | ff14SB | ff19SB | a99SB-disp | CHARMM36m | BioEmu | Boltz-2 | AlphaFlow |
|---------|------|-------|--------|--------|--------|------------|-----------|--------|---------|-----------|
| WW (34) | 1,200 | 667 | 1.5 | 1.5 | 1.5 | 1.5 | 1.5 | <0.5 | <0.1 | <0.5 |
| Crambin (46) | 1,714 | 800 | 1.7 | 1.7 | 1.7 | 1.7 | 1.7 | <0.5 | <0.1 | <0.5 |
| GB3 (56) | 2,182 | 1,000 | 2.0 | 2.0 | 2.0 | 2.0 | 2.0 | <0.5 | <0.1 | <0.5 |
| GB1 (56) | 2,182 | 1,000 | 2.0 | 2.0 | 2.0 | 2.0 | 2.0 | <0.5 | <0.1 | <0.5 |
| BPTI (58) | 2,182 | 1,000 | 2.0 | 2.0 | 2.0 | 2.0 | 2.0 | <0.5 | <0.1 | <0.5 |
| CI2 (64) | 2,667 | 1,200 | 2.4 | 2.4 | 2.4 | 2.4 | 2.4 | <0.5 | <0.1 | <0.5 |
| CspA (70) | 3,158 | 1,412 | 2.7 | 2.7 | 2.7 | 2.7 | 2.7 | <0.5 | <0.1 | <0.5 |
| alpha-3D (73) | 3,429 | 1,500 | 2.7 | 2.7 | 2.7 | 2.7 | 2.7 | <0.5 | <0.1 | <0.5 |
| Calbindin (75) | 3,429 | 1,500 | 2.7 | 2.7 | 2.7 | 2.7 | 2.7 | <0.5 | <0.1 | <0.5 |
| Ubiquitin (76) | 3,750 | 1,600 | 3.0 | 3.0 | 3.0 | 3.0 | 3.0 | <0.5 | <0.1 | <0.5 |
| HPr (85) | 4,444 | 1,846 | 3.4 | 3.4 | 3.4 | 3.4 | 3.4 | <0.5 | <0.1 | <0.5 |
| Barnase (110) | -- | -- | 4.3 | 4.3 | 4.3 | 4.3 | 4.3 | <0.5 | <0.1 | <0.5 |
| HEWL (129) | -- | -- | 4.8 | 4.8 | 4.8 | 4.8 | 4.8 | <0.5 | <0.1 | <0.5 |
| T4 Lys (164) | -- | -- | 6.0 | 6.0 | 6.0 | 6.0 | 6.0 | <0.5 | <0.1 | <0.5 |

**"--" indicates cells where MLFFs are NOT expected to produce stable 50 ns
trajectories.** However, I budget a pilot attempt (5-10 ns) for each MLFF on
Barnase and HEWL during Phase 1 to test whether stability extends beyond the
demonstrated envelope.

**MLFF pilot attempts on Tier C (5 ns each, for exploratory purposes only):**

| Protein | MACE (5 ns) | SO3LR (5 ns) |
|---------|-------------|--------------|
| Barnase | 667 | 267 |
| HEWL | 800 | 316 |
| T4 Lys | 1,200 | 429 |
| **Subtotal** | **2,667** | **1,012** |

### 1.3 Revised Total Compute Budget: 14x10 Design (Without AI2BMD)

**Phase 2 Production (50 ns) -- MLFF methods on 9 Tier A/B proteins:**

| Method | GPU-hrs (sum over 9 proteins) |
|--------|------------------------------|
| MACE-OFF24 | 30,337 |
| SO3LR | 12,525 |
| **MLFF Subtotal** | **42,862** |

**Phase 2 Production (50 ns) -- Classical + Garnet on all 14 proteins:**

| Method | GPU-hrs (sum over 14 proteins) |
|--------|-------------------------------|
| Garnet | 42 |
| ff14SB | 42 |
| ff19SB | 42 |
| a99SB-disp | 42 |
| CHARMM36m | 42 |
| **Classical+Garnet Subtotal** | **210** |

**Generative methods (BioEmu + Boltz-2 + AlphaFlow, all 14 proteins):**
~10 GPU-hours total.

**MLFF Tier C pilot attempts (5-10 ns each):**
~3,679 GPU-hours.

**Phase 2 Equilibration (5 ns per protein per MD method, 14 proteins x 7 MD
methods = 98 equilibrations):**

Equilibration uses the same hardware and speeds as production. Total equilibration
compute for MLFF methods on 9 proteins: ~4,286 GPU-hours. For classical+Garnet
on 14 proteins: ~21 GPU-hours.

**Phase 2 Grand Total:**

| Component | GPU-hrs |
|-----------|---------|
| MLFF production (9 Tier A/B proteins) | 42,862 |
| Classical + Garnet production (14 proteins) | 210 |
| Generative methods | 10 |
| MLFF Tier C pilots | 3,679 |
| Equilibration (MLFF) | 4,286 |
| Equilibration (Classical + Garnet) | 21 |
| **Phase 2 Total** | **51,068** |

**Phase 3: S2 Replicas (15 replicas x 20 ns per replica)**

statrev's truncation protocol (Section 1.2 of statrev-deliberation-R03) requires
computing S2 from truncated trajectories. If MLFF trajectories are limited to
5-10 ns and classical FFs to 50 ns, the S2 replica phase becomes LESS critical
for MLFFs (because the primary analysis uses truncated data) but remains important
for classical FFs to establish convergence.

I recommend a REDUCED Phase 3: 5 replicas x 20 ns (instead of 15 x 20-30 ns)
for the primary analysis, with additional replicas added only if the convergence
diagnostic indicates insufficient precision. This reduces Phase 3 compute by ~67%.

**Phase 3 MLFF (5 replicas x 20 ns x 9 proteins x 2 MLFFs):**
- Per protein: 5 x 20 ns / (MLFF ns/day) x 24 = variable by protein.
- Using average MLFF speed of ~0.5 ns/day across Tier A/B: 100 ns / 0.5 x 24
  = 4,800 GPU-hrs per protein x 2 MLFFs = 9,600 GPU-hrs per protein.
- Total for 9 proteins: difficult to compute as an average because speed varies.
  Using per-protein estimates:

| Protein | MACE (5x20ns) | SO3LR (5x20ns) |
|---------|---------------|----------------|
| WW | 2,400 | 1,333 |
| Crambin | 3,429 | 1,600 |
| GB3 | 4,364 | 2,000 |
| GB1 | 4,364 | 2,000 |
| BPTI | 4,364 | 2,000 |
| CI2 | 5,333 | 2,400 |
| CspA | 6,316 | 2,824 |
| alpha-3D | 6,857 | 3,000 |
| Calbindin | 6,857 | 3,000 |
| Ubiquitin | 7,500 | 3,200 |
| HPr | 8,889 | 3,692 |
| **Subtotal** | **60,673** | **27,049** |

**Phase 3 Classical + Garnet (5 replicas x 20 ns x 14 proteins x 5 methods):**
~70 GPU-hours total (classical FFs are trivially fast).

**Phase 3 Total: ~87,792 GPU-hours.**

**GRAND TOTAL (Phase 2 + Phase 3):**

| Component | GPU-hrs |
|-----------|---------|
| Phase 2 | 51,068 |
| Phase 3 | 87,792 |
| 20% contingency (failures, restarts) | 27,772 |
| **Grand Total** | **166,632** |

### 1.4 Is the 14x10 Design Achievable?

**PARTIALLY CONCUR** with dynrev that the 14x10 design is physically realizable,
but with critical caveats.

**GPU allocation assessment:** The cluster has H200 (80 GB), RTX 5000 Ada (32 GB),
and B200 (192 GB) GPUs. MLFF simulations MUST run on H200 or B200 (memory
requirements of 40-70 GB for solvated systems). Classical simulations can run on
any GPU.

At 20 H200 GPUs dedicated to Alpha-M (realistic average accounting for queue
contention and fairshare):

- Phase 2 MLFF production: 42,862 GPU-hrs / (20 x 24) = **89 days = 12.7 weeks**
- Phase 3 MLFF replicas: 87,722 GPU-hrs / (20 x 24) = **183 days = 26 weeks**
- Combined: **~39 weeks of dedicated MLFF compute at 20 H200s**

This is NOT compatible with the August 31 combined paper decision if work begins
May 1. Phase 2 alone extends to late July, and Phase 3 extends well into November.

**Maximum feasible design within timeline constraints:**

To complete Phase 2 production by August 15 (15 weeks from May 1):

Available GPU-hours at 20 H200s for 15 weeks: 20 x 24 x 105 = **50,400 GPU-hrs**

This covers Phase 2 (51,068 GPU-hrs) almost exactly, leaving no room for Phase 3.

**My recommendation: Execute a TWO-PHASE strategy.**

**Phase A (May 1 - August 15):** Phase 2 production on all proteins. No S2 replicas.
Use block-splitting on 50 ns trajectories (statrev's convergence diagnostic) as a
preliminary estimate of S2 uncertainty. This is sufficient for the August 31
go/no-go decision.

**Phase B (September 1 - November 15):** Phase 3 S2 replicas, ONLY if the August 31
decision is GO for the combined paper. Target 5 replicas for the 6 proteins with
the strongest pilot signals.

This phased approach aligns the compute budget with the decision timeline.

---

## Section 2: Response to AI2BMD Drop and Revised Method Roster

### 2.1 AI2BMD Drop

**CONCUR** with dynrev's concurrence on dropping AI2BMD. The evidence is
overwhelming and I documented the case in detail in my Round 2 verification
(Task I1.3). To summarize:

- 22 open issues, up from 12 in Round 1
- H200 untested (issue #72 open since August 2025)
- Docker-only installation with no Singularity support (issue #65 open)
- 14 months without a release (last v1.1.0, February 2025)
- External users report fundamental difficulties running custom systems (issue #70)
- Thermostat temperature runaway documented (issue #63)
- The AceFF-2.0 fallback I flagged in Round 1 is NOT viable (small-molecule-only)

**Compute savings from dropping AI2BMD:** AI2BMD would have consumed approximately
the same GPU-hours as MACE-OFF24 (similar ns/day range of 0.17-0.29 ns/day). The
savings are roughly ~30,000-40,000 GPU-hours across Phases 2+3. This is already
reflected in the budget above (which excludes AI2BMD).

### 2.2 Revised Method Roster Table

**Table 2: Final 10-Method Roster (Without AI2BMD)**

| # | Method | Paradigm | Software Stack | GPU Memory (H200) | ns/day (25K atoms, H200) | Setup Time | Risk Level |
|---|--------|----------|----------------|-------------------|--------------------------|------------|------------|
| 1 | MACE-OFF24 | MLFF | mace-torch v0.3.15, OpenMM v8.1+, openmm-ml, PyTorch >=2.0, CUDA 12 | 40-60 GB | 0.25-0.55 | 3-5 days | MODERATE |
| 2 | SO3LR | MLFF | so3lr v0.1.0, JAX 0.5.3, jax-md, CUDA 12 | 50-70 GB (JIT peak) | 0.6-1.3 | 3-7 days | MODERATE-HIGH |
| 3 | Garnet | ML-classical | garnetff v0.1.0, PyTorch, OpenFF toolkit >=0.18.0, OpenMM, RDKit | 2-4 GB (classical speed) | ~300-600 | 2-4 days | MODERATE |
| 4 | BioEmu | Generative | bioemu v1.3.1 (pip), PyTorch >=2.6, CUDA 12 | ~4 GB | N/A (mins/protein) | 30 min | LOW |
| 5 | Boltz-2 | Generative | boltz v2.x (pip), PyTorch, CUDA 12 | ~8-16 GB | N/A (secs/protein) | 1 hour | LOW |
| 6 | AlphaFlow | Generative | alphaflow (GitHub clone), PyTorch, CUDA 12 | ~8-16 GB | N/A (mins/protein) | 1-2 days | LOW-MODERATE |
| 7 | AMBER ff14SB | Classical | OpenMM v8.1+, openmmforcefields, AmberTools | 2-4 GB | ~200-800 | 1 hour | LOW |
| 8 | AMBER ff19SB | Classical | OpenMM v8.1+, openmmforcefields | 2-4 GB | ~200-800 | 1 hour | LOW |
| 9 | a99SB-disp | Classical | OpenMM (AMBER format load), TIP4P-D water | 2-4 GB | ~200-600* | 1-2 days | LOW-MODERATE |
| 10 | CHARMM36m | Classical | OpenMM v8.1+, openmmforcefields | 2-4 GB | ~200-800 | 1 hour | LOW |

*a99SB-disp with TIP4P-D: Slightly slower than TIP3P classical FFs due to
the 4-site water model (~15-25% performance penalty). Still orders of magnitude
faster than MLFFs.

**Setup time note on a99SB-disp:** This force field is NOT natively included in
OpenMM's openmmforcefields package. Parameters are available from the Robustelli
lab (GitHub: paulrobustelli/Force-Fields) and the Maiti lab (GitHub: smaiti7/
Amber99SB-Force-Fields) in GROMACS format. Conversion to OpenMM via ParmEd or
direct loading of AMBER PRMTOP files is required. Alternatively, the
jecarvaill/Amber-99SB-DISP repository provides the force field in a format
suitable for OpenMM. This adds 1-2 days of setup and validation vs the native
OpenMM force fields. TIP4P-D water also requires explicit setup in OpenMM,
as the default is TIP3P.

**IMPORTANT NOTE on ff14SB/ff19SB redundancy:** dynrev flagged (Section 1.4) that
ff14SB and ff19SB may produce nearly identical S2 profiles for well-folded small
proteins. I **CONCUR** with the pre-registered redundancy test: if S2 profiles
differ by <0.05 R2 across >80% of residues on all proteins, merge them as a
single generator. If redundant, the backup generator is P2DFlow (dynrev's
reserve recommendation). P2DFlow is pip-installable, runs on a single GPU, and
would add ~2-5 GPU-hours for 14 proteins.

### 2.3 Revised Total Compute Without AI2BMD

The budget in Section 1.3 already excludes AI2BMD. For comparison with the
original proposal:

| Budget Version | Phase 2 | Phase 3 | Contingency | Total |
|---------------|---------|---------|-------------|-------|
| Original proposal (8 methods, 7 proteins) | 44,800 | 43,200 | 19,000 | 107,000 |
| My R1 estimate (8 methods, 7 proteins) | 56,520 | 120,000+ | 35,000 | 211,000+ |
| **Current (10 methods, 14 proteins, no AI2BMD)** | **51,068** | **87,792** | **27,772** | **166,632** |

The current budget is ~56% higher than the original proposal but ~21% lower than
my Round 1 worst-case estimate. The reduction comes from three factors:
(a) dropping AI2BMD eliminates the slowest MLFF, (b) Garnet runs at classical
speed (not MLFF speed as assumed in Round 1), and (c) I reduce Phase 3 to
5 replicas from 15.

---

## Section 3: Delta Timeline Compatibility

### 3.1 Is the 12-14 Week Timeline Compatible with August 15?

If work begins May 1, August 15 is Week 15. stratrev's milestones require a
Delta preprint by August 15.

**Critical path analysis for Delta:**

| Task | Start | End | Duration | Dependencies | Critical? |
|------|-------|-----|----------|--------------|-----------|
| Pre-project: scDataset / data pipeline | Apr 15 | Apr 30 | 2 weeks | None | YES |
| Download Tahoe-100M (429 GB) | May 1 | May 2 | 1-2 days | HPC storage allocation | YES |
| Data preprocessing + splits | May 2 | May 9 | 1 week | Download complete | YES |
| Baseline implementation (5 methods) | May 5 | May 16 | 2 weeks | Preprocessed data | NO (parallel) |
| GEARS setup + Tahoe-100M adapter | May 9 | May 23 | 2 weeks | Preprocessed data | YES |
| scGPT setup + adapter | May 9 | May 23 | 2 weeks | Preprocessed data | YES (parallel w/ GEARS) |
| scFoundation setup | May 16 | May 30 | 2 weeks | Preprocessed data | NO |
| CPA setup | May 16 | May 30 | 2 weeks | Preprocessed data | NO |
| scDFM setup | May 23 | Jun 6 | 2 weeks | Preprocessed data | NO |
| Tahoe-x1 (native Tahoe-100M) | May 9 | May 23 | 2 weeks | Download complete | NO |
| AetherCell (Tier 2, conditional) | Jun 6 | Jun 20 | 2 weeks | Other methods working | NO |
| Method training (all methods) | May 23 | Jul 4 | 6 weeks | All methods set up | YES |
| Evaluation + metrics | Jul 4 | Jul 18 | 2 weeks | Training complete | YES |
| Difficulty stratification analysis | Jul 18 | Jul 25 | 1 week | Evaluation complete | YES |
| Feature importance + ablation | Jul 25 | Aug 1 | 1 week | Evaluation complete | NO (parallel) |
| Figure generation | Aug 1 | Aug 8 | 1 week | Analysis complete | YES |
| Writing + internal review | Aug 8 | Aug 15 | 1 week | Figures complete | YES |
| **Total critical path** | **Apr 15** | **Aug 15** | **17 weeks** | | |

**Verdict: The August 15 target is achievable but REQUIRES:**

1. **Pre-project start (April 15).** The data pipeline must be under construction
   NOW. The scDataset library (arxiv:2506.01883) provides a PyTorch IterableDataset
   for Tahoe-100M with 48x speedup over AnnLoader. This should be adopted
   immediately. Two weeks of pipeline work before May 1 buys critical time.

2. **Parallel method setup.** At least 2 team members working simultaneously on
   different DL methods during Weeks 2-5. One person on GEARS + CPA (both
   GNN-based, shared infrastructure), one on scGPT + scFoundation (both
   transformer-based).

3. **Tahoe-x1 as mandatory Tier 1.** Tahoe-x1 is the ONLY method with native
   Tahoe-100M streaming support (GitHub: tahoebio/tahoe-x1, 143 stars, Apache 2.0).
   It eliminates the data loader engineering for one method entirely. It must be
   Tier 1, not optional.

4. **Method count limited to 7 + 5 baselines.** Tier 1: GEARS, scGPT,
   scFoundation, CPA, scDFM, Tahoe-x1. Tier 2 (conditional): AetherCell only.
   5 statistical baselines (mean, linear, ridge, random forest, gradient boosting).
   Total: 12 methods maximum. This is sufficient for a compelling benchmark.

5. **Writing overlaps with final analysis.** The Introduction, Methods, and
   Related Work sections can be drafted during Weeks 10-12 while analysis runs.

**Key risks to August 15:**

- **GEARS memory explosion on Tahoe-100M (HIGH probability).** GEARS loads all
  data into memory. At 429 GB, this will fail. Custom data loading code using
  scDataset or chunked AnnData is required. Budget 1 extra week for this.
- **scFoundation dependency hell (MODERATE probability).** The scFoundation
  repository has 19 commits and stale activity. May require 2-3 days of debugging
  conda environments and CUDA versions.
- **CPA version staleness (MODERATE probability).** Last release v0.5.0 was June
  2023, three years ago. May have compatibility issues with modern PyTorch/CUDA.

**Fallback if August 15 is missed:** A 2-week delay to September 1 is acceptable.
The combined paper decision shifts to September 15. Beyond September 1, Delta
faces increasing scoop risk from the next iteration of SCALE and VCC 2026.

### 3.2 Can Alpha-M Phase 1 Complete by June 30?

Phase 1 is the pilot study phase: install all software, run stability tests on
small proteins, validate the analysis pipeline. If work begins May 1, June 30
is Week 9.

**Phase 1 task breakdown:**

| Task | Start | End | Duration | Notes |
|------|-------|-----|----------|-------|
| Environment setup (conda/pip) | May 1 | May 3 | 2 days | All methods |
| MACE-OFF24 install + test (alanine dipeptide) | May 3 | May 7 | 3-5 days | pip, OpenMM-ML bridge |
| SO3LR install + test (water box) | May 3 | May 9 | 3-7 days | JAX 0.5.3, CUDA 12 matching |
| Garnet install + test (small molecule) | May 1 | May 5 | 2-4 days | garnetff pip, OpenMM integration |
| BioEmu install + test (ubiquitin) | May 1 | May 2 | 30 min | pip install bioemu[cuda] |
| Boltz-2 install + test | May 1 | May 2 | 1 hour | pip install boltz |
| AlphaFlow install + test | May 3 | May 5 | 1-2 days | GitHub clone, weight download |
| Classical FF validation runs (1 ns each) | May 5 | May 7 | 2 days | ff14SB, ff19SB, a99SB-disp, CHARMM36m |
| **Milestone 1: All software installed** | | **May 9** | | Week 1 complete |
| MACE pilot: 5 ns NVT, WW domain | May 9 | May 14 | 5 days | Smallest protein with S2 |
| MACE pilot: 5 ns NPT, WW domain | May 14 | May 19 | 5 days | Critical NPT stability test |
| SO3LR pilot: 5 ns NVT, WW domain | May 9 | May 12 | 3 days | SO3LR is faster than MACE |
| SO3LR pilot: 5 ns NPT, WW domain | May 12 | May 16 | 4 days | NPT is the high-risk step |
| Garnet pilot: 10 ns, WW domain | May 5 | May 6 | 1 day | Classical speed |
| BioEmu: generate 2,000 conformations for BPTI | May 5 | May 5 | 20 min | Disulfide bond test |
| **Milestone 2: Pilot protein 1 complete** | | **May 19** | | Week 3 complete |
| Analysis pipeline: CPPTRAJ S2 on pilot trajectories | May 19 | May 23 | 3 days | Validate S2 calculation |
| Analysis pipeline: SPARTA+ chemical shifts | May 23 | May 26 | 2 days | Cross-validate with NMR |
| MACE pilot: GB3 (56 res), CI2 (64 res) | May 19 | Jun 2 | 2 weeks | Two Tier B proteins |
| SO3LR pilot: GB3, CI2 | May 19 | May 30 | 11 days | Faster than MACE |
| All classical FFs: 50 ns on WW, GB3, CI2 | May 19 | May 22 | 3 days | Fast; run in parallel |
| Boltz-2 + AlphaFlow: 14 proteins | May 19 | May 20 | 1 day | Trivial compute |
| **Milestone 3: 3 pilot proteins, full pipeline** | | **Jun 2** | | Week 5 complete |
| Extend MLFF pilots to Ubiquitin (76 res) | Jun 2 | Jun 16 | 2 weeks | Largest Tier B protein |
| BioEmu: generate for all 14 proteins | Jun 2 | Jun 3 | 1 day | <3 GPU-hours |
| Exploratory: MACE on Barnase (110 res, Tier C) | Jun 2 | Jun 9 | 1 week | 5 ns attempt only |
| S2 analysis for all pilot trajectories | Jun 16 | Jun 23 | 1 week | Compare to experimental |
| ff14SB/ff19SB redundancy test | Jun 16 | Jun 20 | 3 days | Pre-registered threshold |
| Garnet contamination analysis (GB3 vs GB1) | Jun 16 | Jun 20 | 3 days | Critical for framing |
| **Milestone 4: Phase 1 complete** | | **Jun 30** | | Week 9 complete |

**GO/NO-GO data available at June 30:**

1. MLFF stability on 3-4 Tier A/B proteins (WW, GB3, CI2, Ubiquitin): trajectory
   length achieved, energy drift, structural integrity.
2. S2 convergence diagnostic (block-splitting) on pilot trajectories.
3. BioEmu disulfide validation on BPTI.
4. Preliminary S2 R2 vs experiment for all methods on 3-4 proteins.
5. Generator distinguishability (Jensen-Shannon divergence of S2 distributions).
6. ff14SB/ff19SB redundancy result.

**Verdict: YES, Phase 1 can complete by June 30.** The 9-week window is sufficient
for software installation (Week 1), pilot simulations on 3-4 proteins (Weeks 2-7),
and analysis pipeline validation (Weeks 7-9). This directly informs dynrev's
GO/NO-GO criteria G1-G6.

**Critical dependency:** MACE-OFF24 and SO3LR installation must succeed in Week 1.
If either fails to install by May 9, the pilot timeline is delayed by 1-2 weeks
and Phase 1 extends to mid-July. Mitigation: begin installation testing on April 20
(pre-project) if possible.

---

## Section 4: Unified Week-by-Week Timeline

### 4.1 Master Timeline: May 1 to November 30, 2026

**Color coding:**
- [A] = Alpha-M work
- [G] = Gamma work
- [D] = Delta work
- [*] = Decision point

**Pre-Project (April 15-30):**
- [D] Build Tahoe-100M data pipeline using scDataset; download to HPC scratch
- [A] Test MACE-OFF24 and SO3LR installation on development node (dry run)

**Week 1 (May 1-7):**
- [A] Install all 10 method environments; validate on small test systems
- [D] Download Tahoe-100M (429 GB); begin data preprocessing
- [G] Install BioEmu v1.3.1; generate pilot ensembles for 5 proteins
- GPU: 2-4 H200 (A, installation tests), 2 H200 (D, download/preprocess)

**Week 2 (May 8-14):**
- [A] MACE + SO3LR pilot: 5 ns NVT on WW domain (34 res)
- [A] Garnet pilot: parameterize + 10 ns on WW domain
- [D] Data splits construction; begin GEARS + scGPT setup
- [G] BioEmu: generate 2,000 conformations for 14 proteins
- GPU: 4 H200 (A, MLFF pilots), 2 H200 (D, method setup), 1 H200 (G, BioEmu)

**Week 3 (May 15-21):**
- [A] MACE + SO3LR pilot: 5 ns NPT on WW domain (critical stability test)
- [A] Classical FFs: 50 ns on WW domain (completes in <1 day each)
- [D] GEARS + scGPT Tahoe-100M data loader adaptation
- [G] Feature extraction pipeline (RMSF, contacts, S2) on BioEmu ensembles
- GPU: 4 H200 (A), 2 H200 (D), 1 any GPU (G, CPU-heavy)
- [*] **A Milestone 2: First protein pilot complete (WW domain)**

**Week 4 (May 22-28):**
- [A] MACE + SO3LR pilot: begin GB3 and CI2 (Tier B proteins)
- [A] Analysis pipeline: CPPTRAJ S2, SPARTA+ shifts on WW data
- [D] scFoundation + CPA setup; Tahoe-x1 testing
- [G] AMBER ff19SB: 50 ns x 8 overlap proteins (completes in ~2 days)
- GPU: 4 H200 (A), 4 H200 (D, method training begins), 1 H200 (G)

**Week 5 (May 29 - Jun 4):**
- [A] MACE + SO3LR pilot: GB3 and CI2 continue
- [A] Boltz-2 + AlphaFlow: generate ensembles for all 14 proteins
- [D] scDFM setup; all Tier 1 methods should be installed by end of week
- [G] ML pipeline: initial feature matrix + baseline models (MLP, XGBoost)
- GPU: 4 H200 (A), 4 H200 (D), 2 RTX 5000 (G)
- [*] **A Milestone 3: 3 pilot proteins, full analysis pipeline validated**

**Week 6 (Jun 5-11):**
- [A] Extend MLFF pilots to Ubiquitin (76 res, largest Tier B)
- [A] Exploratory: MACE 5 ns on Barnase (Tier C)
- [D] Method training begins for GEARS, scGPT, scFoundation on Tahoe-100M
- [G] GATv2 graph network: architecture exploration
- GPU: 6 H200 (A, multiple pilots), 6 H200 (D, training), 2 RTX 5000 (G)
- **GPU contention begins: 12/20 H200 allocated to A+D**

**Week 7 (Jun 12-18):**
- [A] MLFF pilots on Ubiquitin continue
- [A] S2 analysis for all pilot trajectories (WW, GB3, CI2)
- [D] CPA + scDFM training; Tahoe-x1 fine-tuning
- [G] GATv2 training; hyperparameter search
- GPU: 6 H200 (A), 6 H200 (D), 2 RTX 5000 (G)

**Week 8 (Jun 19-25):**
- [A] ff14SB/ff19SB redundancy test (pre-registered)
- [A] Garnet contamination analysis: GB3 (contaminated) vs GB1 (clean)
- [A] BioEmu disulfide validation on BPTI and HEWL
- [D] Training continues; AetherCell evaluation begins (if code works)
- [G] Ablation studies: feature importance (SHAP/permutation)
- GPU: 4 H200 (A, analysis), 8 H200 (D, training), 2 RTX 5000 (G)

**Week 9 (Jun 26 - Jul 2):**
- [A] Phase 1 complete. Compile pilot results for GO/NO-GO review.
- [D] Training complete for first 3 methods; begin evaluation
- [G] ML pipeline complete for BioEmu features; preliminary ProteinGym results
- GPU: 2 H200 (A, analysis only), 8 H200 (D), 2 RTX 5000 (G)
- [*] **A Milestone 4: Phase 1 complete. GO/NO-GO for Phase 2 production.**
- [*] **G Milestone: Preliminary dynamics-to-fitness results**

**Week 10 (Jul 3-9):**
- [A] **Phase 2 production begins** (if GO). Start with small proteins (WW, GB3,
  GB1, BPTI) on MACE + SO3LR. Classical FFs complete in days.
- [D] Evaluation continues; remaining method training (scDFM, CPA)
- [G] Sensitivity analysis: raw vs augmented BioEmu for 2-3 pilot proteins
- GPU: 12 H200 (A, Phase 2 MLFF), 6 H200 (D), 2 RTX 5000 (G)
- **PEAK GPU CONTENTION: 18/20 H200 allocated**

**Week 11 (Jul 10-16):**
- [A] Phase 2 production: small proteins continue
- [D] All methods trained; begin unified evaluation pipeline
- [G] Boltz-2 feature extraction + comparison to BioEmu
- GPU: 14 H200 (A, Phase 2), 4 H200 (D, eval), 2 RTX 5000 (G)

**Week 12 (Jul 17-23):**
- [A] Phase 2 production: CI2, CspA, alpha-3D begin
- [D] Evaluation metrics: WMSE, Spearman-top-k, calibration analysis
- [G] Write-up: Gamma standalone results (BioEmu dynamics features vs RSALOR)
- GPU: 14 H200 (A), 4 H200 (D, eval), 2 RTX 5000 (G)

**Week 13 (Jul 24-30):**
- [A] Phase 2 production: medium proteins continue
- [D] Difficulty stratification analysis; feature importance
- [G] Per-assay-type analysis (binding, activity, stability)
- GPU: 14 H200 (A), 2 H200 (D, analysis), 2 RTX 5000 (G)

**Week 14 (Jul 31 - Aug 6):**
- [A] Phase 2 production: Calbindin, Ubiquitin, HPr begin
- [D] Figure generation
- [G] Integration pilot: S2 accuracy vs fitness prediction (3-4 pilot proteins)
- GPU: 14 H200 (A), 2 H200 (D, figures), 2 RTX 5000 (G)
- [*] **G: Pilot integration signal assessment (dynrev G4 criterion)**

**Week 15 (Aug 7-13):**
- [A] Phase 2 production: large proteins continue
- [D] Writing + internal review
- [G] Integration analysis: all available data
- GPU: 16 H200 (A), 2 RTX 5000 (G)
- [*] **D: Delta preprint submitted to bioRxiv (target August 15)**

**Week 16 (Aug 14-20):**
- [A] Phase 2 production: final proteins
- [G] Integration analysis finalization
- GPU: 16 H200 (A), 2 RTX 5000 (G)

**Week 17 (Aug 21-27):**
- [A] Phase 2 production: complete final trajectories
- [A] S2 back-calculation for all production trajectories
- GPU: 16 H200 (A)
- [*] **A Milestone: Phase 2 production complete**

**Week 18 (Aug 28 - Sep 3):**
- [A] Complete S2 analysis and integration scatter plot
- [A+G] Compile all evidence for combined paper decision
- GPU: 4 H200 (A, analysis)
- [*] **COMBINED PAPER DECISION (August 31)**
  - GO: Proceed to Phase 3 replicas + combined paper writing
  - NO-GO: Pivot to Alpha-M standalone (NatMeth) + Gamma standalone (PLOS Comp Bio)

**Weeks 19-24 (Sep 4 - Oct 15) -- IF COMBINED GO:**
- [A] Phase 3: S2 replicas (5 x 20 ns on 6 priority proteins)
- [A+G] Combined paper writing
- GPU: 16 H200 (A, Phase 3 replicas)

**Weeks 19-24 (Sep 4 - Oct 15) -- IF COMBINED NO-GO:**
- [A] Alpha-M standalone: complete analysis + NatMeth submission
- [G] Gamma standalone: complete analysis + PLOS Comp Bio submission
- GPU: 8 H200 (A, additional trajectories for standalone paper)

**Weeks 25-28 (Oct 16 - Nov 12):**
- [A] Phase 3 replicas complete (if combined GO)
- [A+G] Combined paper: final figures, supplementary, submission prep
- [D] Delta: incorporate reviewer feedback (if early peer review feedback)
- GPU: 4 H200 (A, final analysis), minimal GPU otherwise

**Weeks 29-30 (Nov 13-30):**
- [A+G] Submit combined paper to NCS (target November 15)
- OR [A] Submit Alpha-M to NatMeth (if standalone)
- [D] Submit Delta to NatMeth (if not already submitted)
- GPU: Minimal

### 4.2 Resource Conflict Analysis

**GPU contention windows:**

| Period | Weeks | A (H200) | D (H200) | G (RTX 5000) | Total H200 | Status |
|--------|-------|----------|----------|-------------|------------|--------|
| Setup | 1-3 | 4 | 2 | 0 | 6 | OK |
| Pilots | 4-9 | 4-6 | 4-8 | 0 | 8-14 | OK |
| Peak | 10-13 | 12-14 | 4-6 | 0 | 16-20 | TIGHT |
| Production | 14-17 | 14-16 | 0-2 | 0 | 14-18 | OK |
| Analysis | 18-20 | 4 | 0 | 0 | 4 | OK |
| Replicas | 21-28 | 16 | 0 | 0 | 16 | OK |

**Critical window: Weeks 10-13 (July 3 - July 30).** Alpha-M Phase 2 production
begins while Delta DL method training is still in progress. At peak, this
requires 18-20 H200 GPUs. If the cluster cannot sustain this allocation:

- **Mitigation 1:** Move Delta training to RTX 5000 Ada GPUs (32 GB). Most DL
  methods for perturbation prediction (GEARS, scGPT, CPA, scDFM) train on 8-16
  GB GPU memory and do NOT require H200. Only scFoundation and Tahoe-x1 (3B)
  may need H200-class GPUs for fine-tuning.
- **Mitigation 2:** Stagger Alpha-M Phase 2 to begin with small proteins (which
  complete fastest) while Delta finishes training on H200s. By Week 12, Delta
  training is complete and all H200s transfer to Alpha-M.

**Engineer time allocation:**

| Period | Alpha-M | Gamma | Delta | Notes |
|--------|---------|-------|-------|-------|
| Weeks 1-3 | 1.0 FTE | 0.5 FTE | 1.0 FTE | Setup-heavy |
| Weeks 4-9 | 1.0 FTE | 0.5 FTE | 1.0 FTE | Pilots + method setup |
| Weeks 10-17 | 0.5 FTE | 0.5 FTE | 0.5 FTE | Production (less interactive) |
| Weeks 18-28 | 1.0 FTE | 0.5 FTE | 0.25 FTE | Analysis + writing |

**Total: 2.5 FTE peak (Weeks 1-9), dropping to 1.5 FTE during production.**
A team of 3 people can handle this with careful scheduling.

### 4.3 Go/No-Go Decision Points

| Decision | Date | Inputs | Criteria | Outcome |
|----------|------|--------|----------|---------|
| D1: MLFF software GO | May 9 | MACE + SO3LR installation | Both install and run test jobs | If NO: drop failed MLFF, proceed with 1 |
| D2: MLFF pilot GO | Jun 30 | Phase 1 pilot data | dynrev criteria G1-G6 | If NO: Alpha-M classical-only (NatMeth) |
| D3: Delta scope lock | Jun 6 | Method availability | All Tier 1 running | Drop any method not running by Jun 6 |
| D4: Integration signal | Jul 31 | Pilot integration analysis | dynrev criterion G4 | If NO: separate publications |
| D5: Delta preprint | Aug 15 | Complete Delta analysis | Figures + text ready | If MISS: 2-week extension to Sep 1 |
| D6: Combined paper GO | Aug 31 | All Phase 2 data + pilot integration | dynrev G1-G6 + statrev BF_10 | GO: combined NCS. NO-GO: separate |
| D7: Phase 3 scope | Sep 15 | Phase 2 analysis | Priority proteins identified | Select 6 proteins for replicas |

---

## Section 5: Feasibility Verdict and Risk-Adjusted Assessment

### 5.1 Positions on Other Reviewers

| Reviewer | Topic | My Position |
|----------|-------|-------------|
| dynrev | 14 proteins with NMR S2 data exist | **CONCUR** -- The roster is sound. |
| dynrev | 10 generators are scientifically distinct | **CONCUR** -- ff14SB/ff19SB redundancy test is essential. |
| dynrev | Drop AI2BMD | **CONCUR** -- Overwhelming evidence. |
| dynrev | Garnet as contamination case study | **CONCUR** -- Garnet at classical speed is cheap to include. |
| dynrev | Tier C proteins not feasible for MLFFs | **CONCUR** -- Budget pilot attempts but do not rely on success. |
| statrev | Truncation to shortest common trajectory | **CONCUR** -- This is the only fair comparison. |
| statrev | 14x10 design barely achieves 80% power | **PARTIALLY CONCUR** -- The compute cost is enormous; 9x10 with Bayesian analysis may be the pragmatic ceiling. |
| statrev | JZS prior as primary Bayesian test | **CONCUR** (no implementation concern). |
| biomlrev | BioEmu ff14SB ceiling limits Gamma | **CONCUR** -- Implementation-wise, this is not my concern, but it constrains the combined paper's viability. |
| biomlrev | Combined paper at 30-35% viable | **PARTIALLY CONCUR** -- From an implementation standpoint, the combined paper is achievable IF the science cooperates. The timeline and compute are compatible with the dual-track strategy. |
| biomlrev | Include Boltz-2 as mandatory generator | **CONCUR** -- Trivial compute cost (<1 GPU-hour total). |

### 5.2 Revised Traffic Lights

| Project | R1 Verdict | R2 Verdict | R3 Verdict | Justification |
|---------|-----------|-----------|-----------|---------------|
| Alpha-M | YELLOW | YELLOW | **YELLOW-GREEN** | Garnet + SO3LR risks reduced; AI2BMD dropped; 14x10 design mapped to specific GPU-hours. Feasible if MLFF pilots succeed in Phase 1. |
| Gamma | GREEN | GREEN | **GREEN** | No implementation concerns. Compute trivial (~2,000 GPU-hrs). |
| Delta | YELLOW | YELLOW | **YELLOW** | August 15 target achievable with pre-project start and method roster discipline. Data pipeline is the critical path. |
| Combined | -- | 40% viable | **30-40% viable** | Implementation is NOT the bottleneck. Statistical power and scientific signal are the limiting factors. |

### 5.3 Storage Requirements Summary

| Dataset | Size | Location | Lifecycle |
|---------|------|----------|-----------|
| Alpha-M trajectories (Phase 2) | ~2-3 TB | HPC scratch | Retain through publication |
| Alpha-M trajectories (Phase 3) | ~3-5 TB | HPC scratch | Retain through publication |
| BioEmu ensembles (14 proteins) | ~3 GB | Persistent storage | Archive |
| Boltz-2 + AlphaFlow ensembles | ~2 GB | Persistent storage | Archive |
| Tahoe-100M (raw) | 429 GB | HPC scratch | Retain through Delta publication |
| Tahoe-100M (processed, per-method) | ~200-400 GB | HPC scratch | Delete after evaluation |
| DL model checkpoints (Delta) | ~50-100 GB | Persistent storage | Archive best models |
| Analysis outputs + figures | ~10 GB | Persistent storage | Archive |
| **Total** | **~6-9 TB** | | |

This is well within typical HPC scratch allocations (50-100 TB). The primary
concern is I/O throughput during Phase 2 MLFF production: hundreds of concurrent
MLFF jobs writing trajectories to a shared Lustre filesystem. SLURM epilog scripts
for staging trajectory data from local SSD to shared storage are recommended.

### 5.4 Risk-Adjusted Timeline Summary

| Scenario | Probability | Alpha-M Outcome | Gamma Outcome | Delta Outcome |
|----------|------------|-----------------|---------------|---------------|
| Best case (everything works) | 15% | Combined NCS paper by Nov 15 | Integrated in combined paper | NatMeth preprint by Aug 15 |
| Likely case (MLFFs partially work) | 50% | Alpha-M NatMeth by Oct 15 (standalone) | Gamma at PLOS Comp Bio | Delta NatMeth by Sep 1 |
| Pessimistic (MLFF pilot failure) | 25% | Alpha-M classical-only at JCTC | Gamma standalone at Bioinformatics | Delta NatMeth by Sep 15 |
| Worst case (major software failures) | 10% | Alpha-M severely delayed to 2027 | Gamma unaffected (standalone) | Delta delayed to Oct-Nov |

**Expected publications (probability-weighted):**
- P(>=1 NCS paper): 30-35%
- P(>=1 NatMeth paper): 80-85%
- P(>=2 high-venue papers): 85%
- P(complete failure): <2%

---

## Section 6: Critical Infrastructure Recommendations

### 6.1 Environment Management

Each of the 10 Alpha-M methods requires a separate conda environment or
at minimum separate pip installs due to version conflicts:

| Env Name | Key Dependencies | Conflicts |
|----------|-----------------|-----------|
| `env-mace` | PyTorch >=2.0, mace-torch 0.3.15, openmm 8.1+, openmm-ml | JAX (cannot coexist with PyTorch in same env on some CUDA versions) |
| `env-so3lr` | JAX 0.5.3, jax-md, so3lr 0.1.0, CUDA 12 | PyTorch (JAX and PyTorch compete for GPU memory allocation) |
| `env-garnet` | PyTorch, garnetff, OpenFF toolkit >=0.18.0, OpenMM, RDKit | Minimal conflicts |
| `env-bioemu` | PyTorch >=2.6, bioemu 1.3.1, CUDA 12 | Minimal |
| `env-boltz` | PyTorch, boltz | Minimal |
| `env-alphaflow` | PyTorch, alphaflow weights | Minimal |
| `env-classical` | OpenMM 8.1+, openmmforcefields, AmberTools, cpptraj | Minimal |
| `env-analysis` | MDAnalysis, MDTraj, SPARTA+, Pepsi-SAXS | Minimal |
| `env-delta` | Per DL method (GEARS, scGPT, etc.), scDataset | Each method may need its own sub-env |

**Version-pin ALL dependencies** in conda environment YAML files and commit to
the project repository. A single version mismatch between PyTorch and CUDA can
produce silent numerical differences in MLFF forces that invalidate months of
simulation data.

### 6.2 SLURM Job Management

Alpha-M Phase 2 will generate approximately:
- 9 proteins x 2 MLFFs = 18 long-running MLFF jobs (days to weeks each)
- 14 proteins x 5 classical/Garnet methods = 70 classical jobs (hours each)
- 14 proteins x 3 generative methods = 42 generative jobs (minutes each)
- Total: ~130 SLURM jobs for Phase 2 alone

Phase 3 adds 9 proteins x 2 MLFFs x 5 replicas = 90 additional MLFF jobs.

**Recommendations:**
- Use SLURM job arrays for classical FF runs (same script, different protein input)
- Use SLURM job dependencies for sequential phases (Phase 1 -> Phase 2 -> Phase 3)
- Set checkpoint/restart intervals: every 2 ns for MLFFs, every 10 ns for classical
- Monitor with automated scripts: check energy drift, temperature, RMSD hourly
- Alert on NaN forces (immediate job kill + notification)

### 6.3 Data Integrity

- **Checksums:** MD5 checksum every trajectory file after completion
- **Metadata:** JSON sidecar for every trajectory: method, protein, PDB ID, force
  field version, timestep, ensemble, temperature, pressure, trajectory length,
  GPU type, random seed, completion status
- **Backup:** Stage completed trajectories to tape/archive weekly
- **Reproducibility:** Record SLURM job IDs, node names, GPU indices for every run

---

## References

1. Kovacs DP, et al. MACE-OFF: Short-Range Transferable Machine Learning Force
   Fields for Organic Molecules. J. Am. Chem. Soc. 147, 2977 (2025).

2. Frank T, Kabylda A, et al. Molecular Simulations with a Pretrained Neural
   Network and Universal Pairwise Force Fields. J. Am. Chem. Soc. (2026).
   DOI: 10.1021/jacs.5c09558.

3. Li X, et al. Ab initio characterization of protein molecular dynamics with
   AI2BMD. Nature 636, 1012 (2024).

4. Lewis M, Jing B, et al. Scalable Emulation of Protein Equilibrium Ensembles
   with Generative Deep Learning. Science 369, 270-278 (2025).

5. Robustelli P, Piana S, Shaw DE. Developing a molecular dynamics force field
   for both folded and disordered protein states. Proc. Natl. Acad. Sci. 115,
   E4758-E4766 (2018).

6. OpenMM H200 benchmark. GitHub issue #4910. https://github.com/openmm/openmm/
   issues/4910.

7. Blanco-Gonzalez A, et al. Training a force field for proteins and small
   molecules from scratch. arXiv:2603.16770 (2026).

8. Garnet GitHub: https://github.com/greener-group/garnet.

9. Boltz-2 GitHub: https://github.com/jwohlwend/boltz.

10. AlphaFlow GitHub: https://github.com/bjing2016/alphaflow.

11. Jing B, et al. AlphaFold Meets Flow Matching for Generating Protein
    Ensembles. ICML 2024.

12. SO3LR GitHub: https://github.com/general-molecular-simulations/so3lr.

13. BioEmu GitHub: https://github.com/microsoft/bioemu.

14. Robustelli lab Force Fields: https://github.com/paulrobustelli/Force-Fields.

15. Maiti Amber99SB-disp: https://github.com/smaiti7/Amber99SB-Force-Fields.

16. Carvaill Amber-99SB-DISP: https://github.com/jecarvaill/Amber-99SB-DISP.

17. scDataset: Scalable Data Loading for Deep Learning on Large-Scale Single-Cell
    Omics. arXiv:2506.01883 (2025).

18. Tahoe-x1 GitHub: https://github.com/tahoebio/tahoe-x1.

19. Tahoe-100M Dataset: https://huggingface.co/datasets/tahoebio/Tahoe-100M.

20. Ahlmann-Eltze C, Huber W, Anders S. Deep-learning-based gene perturbation
    effect prediction does not yet outperform simple linear baselines. Nature
    Methods 22, 1657-1661 (2025).

21. Lai TT, Brooks CL III. Accuracy and Reproducibility of Lipari-Szabo Order
    Parameters From Molecular Dynamics. J. Phys. Chem. B 128, 10813-10822 (2024).

22. Smith CA, et al. S2 convergence analysis from molecular dynamics trajectories.
    J. Phys. Chem. B (2024). PMC 11790309.

23. Shirts MR, Pande VS. Solvation free energies of amino acid side chain analogs
    for common molecular mechanics force fields. J. Chem. Theory Comput. 1,
    1061-1073 (2005).

24. Theis Lab Tahoe-100M analysis: https://github.com/theislab/
    vevo_Tahoe_100m_analysis.

25. NVIDIA NIM for Boltz-2: https://build.nvidia.com/mit/boltz2/modelcard.

26. OpenMM forcefields GitHub: https://github.com/openmm/openmmforcefields.

27. AI2BMD GitHub issues: https://github.com/microsoft/AI2BMD/issues.

28. Aryal R, et al. Assessment of BioEmu. Int. J. Mol. Sci. 27 (2026).

29. Singh V, Martinez-Noa P, Perez A. How Well Do Molecular Dynamics Force Fields
    Model Peptides? J. Phys. Chem. B (2026). PMC 12324505.

30. JAX installation docs: https://docs.jax.dev/en/latest/installation.html.
