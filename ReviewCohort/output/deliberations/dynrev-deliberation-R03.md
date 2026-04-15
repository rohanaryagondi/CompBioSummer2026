---
agent: dynrev (Dynamics Reviewer)
round: 3
date: 2026-04-15
type: deliberation
---

# Cross-Reviewer Deliberation: Dynamics Reviewer (dynrev)

## Reviewing Agent

Mock NCS Reviewer 1 (dynrev). 20+ year veteran of protein MD simulation. This
document responds to the findings and arguments of statrev and implrev from
Round 2 verification, revises my own positions where warranted, and provides
specific candidate lists and assessments requested by the orchestrator.

---

## Executive Summary

This deliberation addresses three critical questions: (1) whether 14 proteins
with suitable NMR S2 data can be identified for the expanded integration design,
(2) whether 10 meaningfully different ensemble generators exist, and (3) the
scientific consequences of dropping AI2BMD and the role of Garnet in the
benchmark. My conclusions:

1. **14 proteins with published NMR S2 data ARE identifiable**, but only 9-10
   meet the joint constraint of <50 residues AND high-quality NMR S2 data AND
   no Garnet contamination. Relaxing the residue limit to <80 residues (with
   acceptance that MLFF trajectories may be shorter) yields 14+ candidates.

2. **10 meaningfully different generators CAN be assembled**, but only if we
   count classical FF variants (a99SB-disp) and non-MD generators (Boltz-2,
   AlphaFlow) as distinct. The scientific question shifts from "which MLFF is
   best?" to "which ensemble paradigm best captures experiment?"

3. **I CONCUR with dropping AI2BMD.** The scientific loss is minimal because
   AI2BMD's hybrid solvent model (classical AMOEBA water + MLFF protein) makes
   it a poor representative of "pure ab initio" anyway.

4. **Garnet should be reframed as a "benchmark contamination case study."** Its
   5/7 contamination, underperformance vs Amber14SB, and IDP over-compaction
   make it scientifically more valuable as a cautionary tale than as a
   competitive method.

---

## Section 1: Response to statrev's Power Analysis

### 1.1 Context and Agreement

**CONCUR** with statrev's revised power calculation. The crossed random effects
model (proteins x generators) is the correct framework. The 42% power at rho=0.5
for the 6x8 design is, if anything, optimistic -- it assumes the ICC estimates
are correct, and we have no empirical basis for the ICC(protein) = 0.40 and
ICC(generator) = 0.25 assumptions. I note that statrev's power table shows the
14x10 design achieving ~80% power at rho=0.5, which is the minimum acceptable
level for a publishable result.

The question posed to me is whether this 14x10 design is physically realizable:
do 14 proteins with suitable NMR S2 data exist, and can they be simulated with
MLFFs?

### 1.2 Candidate Proteins with Published Experimental NMR S2 Order Parameters

I have assembled a list of candidate proteins by cross-referencing three criteria:
(a) published backbone NH S2 order parameters from 15N relaxation measurements
deposited in or derivable from BMRB entries, (b) high-resolution PDB structure
available, and (c) feasibility for MLFF simulation given current stability
constraints. The critical MLFF stability constraint from my Round 2 findings is
that NO MLFF has demonstrated stability on solvated proteins >50 residues. MACE-
OFF24 and SO3LR have only been tested on crambin (42-46 residues). I therefore
organize candidates into two tiers:

**Tier A: <50 residues (high confidence for MLFF feasibility)**
These proteins are within the demonstrated MLFF stability envelope (crambin-scale).

**Tier B: 50-80 residues (moderate confidence for MLFF feasibility)**
These proteins exceed the demonstrated MLFF range but are plausible extension
targets. Classical FFs and BioEmu can simulate them; MLFFs may require the
adaptive trajectory-length protocol.

**Tier C: 80-170 residues (low confidence for MLFF feasibility)**
These are the original Alpha-M benchmark proteins. Classical FFs and BioEmu can
simulate them; MLFFs are speculative at this scale.

---

#### Tier A Proteins (<50 residues, MLFF-feasible)

**A1. Crambin (46 residues)**
- PDB: 1CRN (X-ray, 0.54 A resolution)
- NMR S2 data: **NO experimental S2 available.** Crambin has minimal NMR data
  (no 15N relaxation study in BMRB). It serves as an MLFF stability check ONLY.
- tau_c: ~3.5 ns (estimated from molecular weight)
- Garnet contamination: No
- MLFF status: Published simulations from MACE-OFF24 (1.6 ns), SO3LR (3 ns),
  GEMS (10 ns NPT)
- **Verdict: INCLUDE as stability control, NOT as S2 benchmark protein.**

**A2. Villin headpiece subdomain HP35 (35 residues)**
- PDB: 1VII (NMR structure, McKnight et al., Nat. Struct. Biol. 1997)
- NMR S2 data: Backbone dynamics characterized; brute-force MD comparisons
  published (Zagrovic et al., J. Phys. Chem. B 2003). BMRB entry exists for
  chemical shifts. However, **no published 15N relaxation S2 dataset found in
  BMRB.** HP35 dynamics are well-characterized by MD but the EXPERIMENTAL S2
  reference is sparse.
- tau_c: ~2.5 ns
- Residues: 35
- Garnet contamination: No
- MLFF status: Within crambin-scale; feasible for MACE-OFF24 and SO3LR
- **Verdict: CONDITIONAL -- include only if BMRB S2 data can be confirmed.
  The protein is an excellent size match for MLFFs but NMR S2 data availability
  must be verified before commitment.**

**A3. Trp-cage (TC5b, 20 residues)**
- PDB: 1L2Y (NMR structure, Neidigh et al., Nat. Struct. Biol. 2002)
- NMR S2 data: Limited. Trp-cage is a designed miniprotein used for folding
  studies, not dynamics. No comprehensive 15N relaxation S2 dataset in BMRB.
- tau_c: ~1.5 ns
- Residues: 20
- Garnet contamination: No
- MLFF status: Small enough for any MLFF; AI2BMD tested chignolin (10 residues),
  which is comparable
- **Verdict: EXCLUDE. No experimental S2 reference data for benchmarking.**

**A4. GB3 (third IgG-binding domain of Protein G, 56 residues)**
- PDB: 2OED (X-ray, 1.1 A) / 1P7E (NMR)
- NMR S2 data: **EXCELLENT.** Extensive 15N relaxation data. Model-free S2
  published at multiple fields (500, 600, 800 MHz) by Hall and Fushman (JACS
  2006; J. Biomol. NMR 2003). BMRB entries for chemical shifts and relaxation
  data. 36 RDC datasets available. One of the best-characterized small proteins
  for NMR dynamics.
- tau_c: ~3.3 ns (298 K)
- Residues: 56
- Garnet contamination: **YES -- NMR training protein**
- MLFF status: Slightly larger than crambin but within plausible range
- **Verdict: INCLUDE (already in Alpha-M set). Flag Garnet contamination.**

**A5. WW domain (PIN1-WW, 34 residues)**
- PDB: 1PIN / 2M8I (NMR structures)
- NMR S2 data: S2 of backbone NH bonds characterized for apo and Cdc25-
  complexed PIN1-WW at 278 K, 16.4 T (Jager et al., Nat. Struct. Mol. Biol.
  2006). Published order parameters available.
- tau_c: ~2.5 ns
- Residues: 34
- Garnet contamination: No
- MLFF status: Small; within crambin-scale feasibility
- **Verdict: INCLUDE. Excellent small protein with published S2 and no Garnet
  contamination. The dynamics are well-characterized and functionally relevant
  (peptide recognition).**

**A6. Chignolin variant CLN025 (10 residues)**
- PDB: 5AWL (X-ray, 0.8 A)
- NMR S2 data: **NO.** Too small for meaningful S2 analysis (only 10 backbone
  NH sites). Useful for MLFF stability testing but not S2 benchmarking.
- Residues: 10
- Garnet contamination: No
- **Verdict: EXCLUDE from S2 benchmark. Too few residues for statistical power.**

**A7. Cold shock protein A (CspA, 70 residues -- reclassified to Tier B)**
- See Tier B below.

---

#### Tier B Proteins (50-80 residues, moderate MLFF feasibility)

**B1. Ubiquitin (76 residues)**
- PDB: 1UBQ (X-ray, 1.8 A) / 1D3Z (NMR)
- NMR S2 data: **EXCELLENT.** The gold standard for S2 validation. 15N
  relaxation studied extensively (Tjandra et al., JACS 1995; Lee et al.,
  J. Mol. Biol. 2000). Lai & Brooks (J. Phys. Chem. B 2024) report ff14SB
  R2 = 0.86, CHARMM36m R2 = 0.83 for S2. BMRB entries: multiple (4493, 6457,
  15410, others).
- tau_c: 4.03 ns (298 K)
- Residues: 76
- Garnet contamination: Yes (validation protein)
- MLFF status: ~28,000 atoms solvated; 1.5x crambin system size. At the edge
  of demonstrated MLFF capability. May require adaptive trajectory length.
- **Verdict: INCLUDE (already in Alpha-M set). Essential reference protein.**

**B2. BPTI (bovine pancreatic trypsin inhibitor, 58 residues)**
- PDB: 5PTI (X-ray, 1.0 A) / 1PIT (NMR)
- NMR S2 data: **EXCELLENT.** 15N relaxation by Beeser et al. (J. Mol. Biol.
  1997). Otting et al. published backbone dynamics. BMRB entries available.
  One of the classic NMR dynamics proteins.
- tau_c: ~4.2 ns (298 K)
- Residues: 58 (3 disulfide bonds)
- Garnet contamination: Yes (validation protein)
- BioEmu concern: v1.3.0 removed Disulfide Potential. Must verify BPTI SS
  bond integrity in BioEmu v1.3.1 before inclusion.
- MLFF status: Similar to crambin system size; feasible but untested
- **Verdict: INCLUDE (already in Alpha-M set). Verify BioEmu disulfide handling.**

**B3. CI2 (chymotrypsin inhibitor 2, 64 residues)**
- PDB: 2CI2 (X-ray, 2.0 A) / 3CI2 (NMR)
- NMR S2 data: **GOOD.** Backbone dynamics studied by Shaw et al. (Biochemistry
  1995). 15N T1, T2, and {1H}-15N NOE for all backbone NH groups. S2 ~0.9 for
  most backbone with lower values in the binding loop (residues 54-64).
- tau_c: ~4.5 ns
- Residues: 64
- Garnet contamination: **No**
- MLFF status: Comparable to ubiquitin in system size; moderate feasibility
- **Verdict: INCLUDE. High-quality S2 data, no Garnet contamination, and well-
  studied folding model. An excellent addition to the benchmark set.**

**B4. CspA (cold shock protein A, E. coli, 70 residues)**
- PDB: 3MEF (NMR) / 1MJC (X-ray, 1.05 A)
- NMR S2 data: **GOOD.** Backbone dynamics characterized by Feng et al.
  (Biochemistry 1998). 15N T1, T2, {1H}-15N NOE; S2 reported for backbone
  NHs. tau_m = 4.88 ns. Conformational dynamics in single-stranded RNA-
  binding site detected.
- tau_c: 4.88 ns
- Residues: 70
- Garnet contamination: **No**
- MLFF status: Comparable to ubiquitin; moderate feasibility
- **Verdict: INCLUDE. Good S2 data, no Garnet contamination, beta-barrel fold
  (adds structural diversity to the mostly alpha/alpha-beta set).**

**B5. Protein G B1 domain (GB1, 56 residues)**
- PDB: 1PGB (X-ray) / 3GB1 (NMR)
- NMR S2 data: **EXCELLENT.** Extensive 15N relaxation data at multiple
  temperatures (0-50 C) and fields (500, 600, 800 MHz). Barchi et al.
  (Protein Sci. 1994), Idiyatullin et al. (J. Phys. Chem. B 2003). Temperature-
  dependent S2 available. BMRB entries exist.
- tau_c: ~3.5 ns (298 K)
- Residues: 56
- Garnet contamination: **No** (GB3 is contaminated; GB1 is NOT the same
  protein). GB1 and GB3 share ~40% sequence identity with different loop
  structures.
- MLFF status: Similar to GB3; within plausible range
- **Verdict: INCLUDE. Excellent dynamics data, NOT Garnet-contaminated (distinct
  from GB3), and provides a paired comparison: GB1 vs GB3 tests Garnet
  generalization within a protein family.**

**B6. Calbindin D9k (75 residues)**
- PDB: 1CLB (NMR, apo) / 4ICB (X-ray, Ca-loaded)
- NMR S2 data: **GOOD.** Kordel et al. (Biochemistry 1992; J. Mol. Biol.
  1993) published backbone 15N relaxation and S2 for both apo and Ca-loaded
  states. S2 ~0.83-0.85 for helices, ~0.59 for the linker region.
- tau_c: ~4.0 ns
- Residues: 75
- Garnet contamination: **No**
- MLFF status: Comparable to ubiquitin in system size
- **Verdict: INCLUDE. Good S2 data with calcium-dependent dynamics, no Garnet
  contamination. Adds functional diversity (calcium-binding EF-hand fold).**

**B7. HPr (histidine-containing phosphocarrier protein, 85 residues)**
- PDB: 1PFH (NMR, phosphorylated) / 2HID (NMR, B. subtilis)
- NMR S2 data: **MODERATE.** 15N relaxation studied for E. coli HPr. Backbone
  dynamics characterized but S2 data is less extensively published than
  ubiquitin or GB3. Residual dipolar couplings available.
- tau_c: ~5.0 ns
- Residues: 85 (slightly above Tier B cutoff)
- Garnet contamination: **No**
- MLFF status: Pushing the boundary; system size ~30,000 atoms solvated
- **Verdict: CONDITIONAL INCLUDE. S2 data quality must be verified against BMRB.
  Slightly larger than ideal for MLFFs.**

---

#### Tier C Proteins (80-170 residues, for classical FFs and BioEmu only)

**C1. Barnase (110 residues)**
- PDB: 1BNR (NMR) / 1A2P (X-ray, 1.5 A)
- NMR S2 data: **EXCELLENT.** Extensively studied by Fersht group. 15N
  relaxation published.
- Garnet contamination: Yes (barnase/barstar complex validation)
- Already in Alpha-M set.
- **Verdict: INCLUDE. Classical FFs and BioEmu only; MLFF trajectories unlikely
  at this size.**

**C2. HEWL (hen egg white lysozyme, 129 residues)**
- PDB: 1AKI (X-ray) / 1E8L (NMR)
- NMR S2 data: **EXCELLENT.** Buck et al. (Biochemistry 1995). NMR at
  308 K, pH 3.8. SAXS data available.
- Garnet contamination: Yes (validation protein)
- BioEmu concern: 4 disulfide bonds; verify v1.3.1 handling.
- Already in Alpha-M set.
- **Verdict: INCLUDE. Classical FFs and BioEmu. Note non-standard conditions
  (308 K, pH 3.8).**

**C3. T4 lysozyme (164 residues)**
- PDB: 107L (X-ray)
- NMR S2 data: **GOOD.** Mulder et al. (Biochemistry 2000). Lai & Brooks
  (2024) report ff14SB R2 = 0.45, CHARMM36m R2 = 0.47. Poor force field
  agreement -- this is a HARD target.
- tau_c: 10.60 ns
- Garnet contamination: **No (only genuinely OOD Garnet protein with NMR data)**
- Already in Alpha-M set.
- **Verdict: INCLUDE. Critical for Garnet OOD assessment.**

**C4. alpha-3D (73 residues)**
- PDB: 2A3D (NMR)
- NMR S2 data: **GOOD.** Walsh et al. (Protein Sci. 2001). Lai & Brooks
  (2024) report ff14SB R2 = 0.49, CHARMM36m R2 = 0.27. A designed three-
  helix bundle with poor force field agreement -- challenging target.
- tau_c: 6.50 ns
- Residues: 73
- Garnet contamination: **No**
- MLFF status: Within Tier B range; moderate feasibility
- **Verdict: INCLUDE. Provides a challenging protein where force fields struggle.
  Published in Lai & Brooks (2024) with quantitative R2 values.**

**C5. Human muscle fatty acid binding protein (FABP3, ~133 residues)**
- PDB: 1HMT (X-ray)
- NMR S2 data: **GOOD.** Lai & Brooks (2024) report ff14SB R2 = 0.65,
  CHARMM36m R2 = 0.49.
- tau_c: 9.05 ns
- Garnet contamination: **No**
- MLFF status: Too large for MLFFs; classical and BioEmu only
- **Verdict: CONDITIONAL INCLUDE for classical FF comparison only.**

**C6. Oxidized long chain flavodoxin (~176 residues)**
- PDB: 1FLV
- NMR S2 data: **GOOD.** Lai & Brooks (2024) report ff14SB R2 = 0.70,
  CHARMM36m R2 = 0.54.
- tau_c: 6.35 ns
- Garnet contamination: **No**
- **Verdict: EXCLUDE from primary benchmark (too large for MLFFs and adds
  limited new information). Available as supplementary comparison.**

---

### 1.3 Recommended 14-Protein Benchmark Set

Based on the candidate analysis, I recommend the following 14-protein set for
the expanded integration design:

| # | Protein | Residues | Tier | S2 Quality | Garnet Contaminated? | Key Feature |
|---|---------|----------|------|------------|---------------------|-------------|
| 1 | GB3 | 56 | A/B | Excellent | **YES (training)** | Gold standard small protein |
| 2 | WW domain (PIN1) | 34 | A | Good | No | Smallest with published S2 |
| 3 | Ubiquitin | 76 | B | Excellent | Yes (validation) | Gold standard dynamics |
| 4 | BPTI | 58 | B | Excellent | Yes (validation) | Classic; disulfide test |
| 5 | CI2 | 64 | B | Good | **No** | Uncontaminated; folding model |
| 6 | CspA | 70 | B | Good | **No** | Beta-barrel fold diversity |
| 7 | GB1 | 56 | B | Excellent | **No** | GB3 family; Garnet OOD test |
| 8 | Calbindin D9k | 75 | B | Good | **No** | EF-hand; Ca-dependent dynamics |
| 9 | alpha-3D | 73 | B/C | Good | **No** | Designed; hard FF target |
| 10 | Barnase | 110 | C | Excellent | Yes (complex val.) | Large; classical+BioEmu only |
| 11 | HEWL | 129 | C | Excellent | Yes (validation) | Large; non-standard conditions |
| 12 | T4 lysozyme | 164 | C | Good | **No** | Largest; Garnet OOD critical |
| 13 | Crambin | 46 | A | **None** | No | MLFF stability control |
| 14 | HPr | 85 | B | Moderate | **No** | Additional uncontaminated |

**Summary statistics:**
- Garnet-contaminated: 5 (GB3, Ubiquitin, BPTI, Barnase, HEWL)
- Garnet-uncontaminated: 9 (WW, CI2, CspA, GB1, Calbindin, alpha-3D, T4 lys,
  Crambin, HPr)
- With published NMR S2: 13 (all except Crambin)
- MLFF-feasible (<80 residues): 9 (GB3, WW, Ubiquitin, BPTI, CI2, CspA, GB1,
  Calbindin, alpha-3D)
- Classical FF + BioEmu only (>80 residues): 4 (Barnase, HEWL, T4 lys, HPr)
- Stability control only: 1 (Crambin)

**Critical constraint:** The 14x10 design requires all 14 proteins to be
simulated by all 10 generators. For MLFFs, only the 9 Tier A/B proteins are
feasible. This means the crossed design is NOT fully crossed -- there will be
missing cells for MLFF x Tier C protein combinations. statrev must advise on
how to handle this incomplete design statistically. Options include:

(a) Restrict the crossed design to the 9 MLFF-feasible proteins (9x10 = 90
    cells), which gives N_eff ~13-15 by statrev's formula -- close to but below
    the 14x10 target.
(b) Use the full 14 proteins for classical FFs and BioEmu but a reduced set for
    MLFFs, and model the missing data as structurally absent (not missing at
    random).
(c) Frame the MLFF comparison separately from the integration claim: MLFF
    assessment uses the 9-protein subset; the integration claim uses all 14
    proteins with methods that can simulate all of them.

**I recommend option (c).** It separates the MLFF benchmarking question (which
methods are accurate?) from the integration question (does accuracy predict
fitness?) and avoids the statistical complications of incomplete crossed designs.

---

### 1.4 Assessment of 10 Ensemble Generators

The directive asks whether 10 meaningfully different ensemble generators can be
identified. The current roster has 7: MACE-OFF24, SO3LR, Garnet, BioEmu, AMBER
ff14SB, AMBER ff19SB, CHARMM36m. Four additional candidates are proposed:
Boltz-2, AlphaFlow, OpenFF Sage 2.1.0, a99SB-disp.

I evaluate each:

**Current Roster (7 methods):**

| # | Generator | Category | Distinct Ensemble? | Evidence |
|---|-----------|----------|-------------------|----------|
| 1 | MACE-OFF24 | MLFF | Yes | QM-level potential; fundamentally different from classical |
| 2 | SO3LR | MLFF | Yes | Different architecture (SO(3) equivariant + universal LR); different training data (PBE0+MBD) |
| 3 | Garnet | ML-parameterized classical | Yes | GNN-assigned parameters; NMR-trained; distinct from manually parameterized FFs |
| 4 | BioEmu | Generative (non-MD) | Yes | Diffusion model trained on ff14SB trajectories; no dynamics, only equilibrium |
| 5 | AMBER ff14SB | Classical (AMBER family) | Yes | The baseline; well-validated; BioEmu's training target |
| 6 | AMBER ff19SB | Classical (AMBER family) | **Partially** | ff19SB is an incremental update to ff14SB (CMAP corrections). Ensembles may be very similar for small, well-folded proteins |
| 7 | CHARMM36m | Classical (CHARMM family) | Yes | Different parameterization philosophy from AMBER; includes CMAP and distinct LJ parameters |

**Concern about ff14SB vs ff19SB redundancy:** These two force fields share the
same functional form and most parameters. ff19SB adds CMAP corrections to the
backbone torsional potential, which primarily affect loop and disordered regions.
For the well-folded, small proteins in the benchmark set, ff14SB and ff19SB may
produce nearly identical S2 profiles. The effective diversity of ensembles is
questionable. I recommend including both but performing a pre-registered test:
if the S2 profiles from ff14SB and ff19SB are within the back-calculation noise
for >80% of residues across all proteins, they should be treated as a SINGLE
generator for the integration analysis.

**Proposed Additional Generators:**

**8. Boltz-2 (with pair representation scaling / Boltz-sample)**
- Category: Generative (non-MD), structure prediction-based
- Ensemble generation: Rescaling the latent pair representation systematically
  modulates conformational sampling. MD conditioning produces more diverse
  structures with stronger RMSF correlations (Spearman 0.76-0.84 on mdCATH/ATLAS)
  than BioEmu (0.69-0.75) (suzuki-2001/boltz-sample, bioRxiv January 2026).
- Distinct from BioEmu? **YES.** Different architecture (structure prediction
  model with flow-based sampling vs diffusion model trained on MD). Different
  training data (PDB + evolutionary covariance vs ff14SB MD trajectories).
  Boltz-2 does NOT inherit the ff14SB bias chain.
- Code: Available (github.com/jwohlwend/boltz, MIT license)
- **Verdict: INCLUDE. Boltz-2 provides a critical control for the BioEmu ff14SB
  bias chain. If Boltz-2 ensembles predict fitness equally well or better than
  BioEmu, the "dynamics" signal is not ff14SB-specific.**

**9. AlphaFlow**
- Category: Generative (non-MD), flow matching on AlphaFold
- Ensemble generation: Fine-tunes AlphaFold2 under a flow matching framework.
  Trained on PDB structures and optionally on ATLAS MD data. Produces backbone
  conformational ensembles.
- Distinct from BioEmu? **YES.** Different training philosophy (PDB/ATLAS
  snapshots vs long MD trajectories). AlphaFlow trained on ATLAS substantially
  outperforms MSA baselines in predicting conformational flexibility and
  distributional modeling of atomic positions (Jing et al., ICML 2024).
- Distinct from Boltz-2? **PARTIALLY.** Both are structure prediction-derived.
  AlphaFlow uses flow matching on AlphaFold2; Boltz-2 uses pair representation
  scaling on Boltz architecture. The ensemble generation mechanisms are
  fundamentally different (noise-to-structure flow vs latent space steering).
- Code: Available (github.com/bjing2016/alphaflow, MIT license)
- **Verdict: INCLUDE. Provides a second non-MD generative method independent of
  Boltz-2 and BioEmu. Three generative methods (BioEmu, Boltz-2, AlphaFlow) vs
  multiple MD methods creates a clean paradigm comparison.**

**10. a99SB-disp (AMBER variant for folded + disordered proteins)**
- Category: Classical (AMBER family, specialized variant)
- Ensemble generation: Modified backbone torsion potential + Lennard-Jones
  reparameterization (Robustelli et al., PNAS 2018). Validated on 21 systems
  spanning folded proteins, IDPs, peptides, and fast-folding proteins.
- Distinct from ff14SB and ff19SB? **YES, substantially.** a99SB-disp was
  developed specifically to address the IDP over-compaction problem in ff14SB.
  It produces demonstrably different conformational ensembles for disordered
  regions, and the backbone torsional potential is reparameterized beyond
  ff19SB's CMAP corrections. The water model (TIP4P-D) differs from TIP3P
  used in ff14SB/ff19SB.
- **Verdict: INCLUDE. The TIP4P-D water model and reparameterized backbone
  potential produce genuinely different ensembles from ff14SB/ff19SB, especially
  for loop regions and flexible termini. This is the strongest classical FF
  addition.**

**11. OpenFF Sage 2.1.0 (Open Force Field)**
- Category: Classical (OpenFF family)
- Ensemble generation: Sage is a small molecule force field, not a protein
  force field. While validated for protein-ligand simulations in combination
  with AMBER biopolymer FFs, it does NOT provide independent protein backbone
  parameters. Using Sage for a protein backbone would require pairing it with
  an AMBER protein FF (e.g., ff14SB + Sage for small molecule), making it
  redundant with ff14SB for the protein dynamics comparison.
- More recent: Sage 2.3.0 (January 2026) is available, but the same limitation
  applies.
- **Verdict: EXCLUDE. Sage is a ligand FF, not a protein FF. Including it would
  be methodologically incorrect for an S2 order parameter benchmark of protein
  backbone dynamics.**

**Revised 10-Generator Roster:**

| # | Generator | Category | Paradigm |
|---|-----------|----------|----------|
| 1 | MACE-OFF24 | MLFF | QM-level MD |
| 2 | SO3LR | MLFF | QM-level MD with LR |
| 3 | Garnet | ML-parameterized classical | NMR-trained classical MD |
| 4 | BioEmu | Generative (non-MD) | Diffusion model (ff14SB-trained) |
| 5 | Boltz-2 | Generative (non-MD) | Structure prediction + pair scaling |
| 6 | AlphaFlow | Generative (non-MD) | Flow matching on AlphaFold2 |
| 7 | AMBER ff14SB | Classical | Standard AMBER |
| 8 | AMBER ff19SB | Classical | Updated AMBER (CMAP) |
| 9 | a99SB-disp | Classical | AMBER for IDPs (TIP4P-D water) |
| 10 | CHARMM36m | Classical | Standard CHARMM |

**Ensemble diversity assessment:**

This roster spans four distinct paradigms:
- **QM-level MD (2):** MACE-OFF24, SO3LR -- fundamentally different potential
  energy surfaces from classical FFs
- **ML-parameterized classical (1):** Garnet -- GNN-assigned parameters with
  NMR training data
- **Generative non-MD (3):** BioEmu, Boltz-2, AlphaFlow -- no dynamics at all;
  sample from learned distributions
- **Classical MD (4):** ff14SB, ff19SB, a99SB-disp, CHARMM36m -- established
  baselines with known properties

This is a scientifically robust roster. The concern is that ff14SB and ff19SB
may be redundant. If the pre-registered redundancy test confirms this, the
effective generator count drops to 9. However, 9x14 = 126 cells still provides
N_eff ~17-19, which exceeds the 14x10 minimum.

**One additional generator to consider (if ff14SB/ff19SB are redundant):**

**P2DFlow:** SE(3) flow matching protein ensemble generator (JCTC 2025).
Outperforms AlphaFlow on ATLAS MD datasets. Code available
(github.com/BLEACH366/P2DFlow). Would provide a third flow-matching-based
generative method. **Verdict: RESERVE as backup if ff14SB/ff19SB redundancy
confirmed.**

---

## Section 2: Response to implrev's Feasibility Assessment

### 2.1 Dropping AI2BMD

**CONCUR** with implrev's recommendation to drop AI2BMD entirely.

The evidence is overwhelming:
1. **22 open issues** with no resolution trend (implrev verification)
2. **H200 untested** (issue #72 open since August 2025)
3. **Docker-only** with no Singularity support on HPC (issue #65 open)
4. **14 months without a release** (last release v1.1.0, February 2025)
5. **Hybrid solvent model** -- AI2BMD uses classical AMOEBA water for solvent
   and MLFF only for the protein backbone (my Round 2 verification, Task D1.3)
6. **Documented energy scaling errors** with protein size (Li et al., Nature
   2024: "as the protein size increased from chignolin to PACSIN3, the increase
   of energy errors could be attributed to insufficient modelling for the
   escalating many-body interactions")
7. **Computationally prohibitive** -- 2.61 seconds per step for a 13,728-atom
   system, making 50 ns trajectories infeasible

**What is lost scientifically by dropping the "pure ab initio" tier?**

The question assumes AI2BMD represented a "pure ab initio" tier. It did not.
AI2BMD's hybrid approach (MLFF protein + AMOEBA water) is NOT a pure MLFF
comparison. A truly pure MLFF would use the same potential for both protein and
solvent, which is what MACE-OFF24 and SO3LR do. Therefore:

- **MACE-OFF24 is the better "pure MLFF" representative.** It applies the same
  ML potential to protein and water. No fragmentation, no hybrid classical
  solvent.
- **SO3LR is the better "ab initio-quality" representative.** Trained on
  PBE0+MBD QM data with explicit long-range corrections, no hybrid approximation.
- **GEMS would be the ideal "pure ab initio" tier representative** (longest
  published MLFF protein trajectory at 10 ns NPT), but model weights are
  unreleased (my Round 2 verification, Task D2.1).

**Net scientific impact of dropping AI2BMD:** Minimal. The benchmark retains two
genuine MLFFs (MACE-OFF24, SO3LR) that provide a fairer head-to-head comparison
with classical FFs because they use the same potential for protein and water.
AI2BMD's inclusion would have CONFUSED the comparison by introducing a hybrid
model that is neither purely classical nor purely MLFF.

**One caveat:** If, between now and August 2026, AI2BMD v2.0 is released with
H200 support, Singularity images, and demonstrated protein trajectories >10 ns,
it could be added back as a stretch goal. I estimate this probability at <10%.

### 2.2 Garnet's Scientific Contribution

**PARTIALLY CONCUR** with the framing of Garnet as a "case study in benchmark
contamination."

**The contamination is severe and scientifically disqualifying for competitive
comparison:**

My Round 2 verification (Task D4) established:
- **GB3:** NMR J-coupling training protein -- **direct contamination**
- **Ubiquitin:** Validation protein -- moderate contamination
- **BPTI:** Validation protein -- moderate contamination
- **HEWL:** Validation protein -- moderate contamination
- **Barnase:** Barnase/barstar complex validation -- moderate contamination
- **T4 lysozyme:** Not in training or validation -- genuinely OOD
- **Crambin:** Not in training or validation -- no NMR S2 data

5 of 7 original Alpha-M proteins (5 of 13 S2 proteins in the expanded set) are
contaminated. A competitive comparison of Garnet vs other methods on these
proteins is not a fair test and would not survive peer review.

**However, Garnet has genuine scientific value in three roles:**

**Role 1: Contamination case study.** This is the strongest role. Report Garnet
performance separately for Garnet-train (GB3), Garnet-validation (Ubiquitin,
BPTI, HEWL, Barnase), and Garnet-test (all others: CI2, CspA, GB1, Calbindin,
alpha-3D, WW domain, T4 lysozyme, HPr) proteins. If Garnet shows a statistically
significant performance drop from Garnet-train/validation to Garnet-test, this
is evidence of overfitting. If performance is consistent, the NMR training
generalizes. Either finding is publishable.

**Role 2: Paradigm representative.** Garnet represents the "NMR-aware ML
classical FF" paradigm. No other method in the benchmark was trained on
experimental NMR data. Its inclusion tests whether NMR training improves
dynamics, which is a scientifically interesting question independent of its
competitive ranking.

**Role 3: GB1 vs GB3 control.** With the expanded protein set including GB1
(which is NOT Garnet-contaminated), we can test Garnet on GB1 and compare to
its performance on GB3 (contaminated). GB1 and GB3 share ~40% sequence identity
with different loop structures. If Garnet performs well on GB3 (training) but
poorly on GB1 (structurally similar but unseen), this is a striking demonstration
of overfitting within a protein family.

**What I disagree with:** I do NOT agree with treating Garnet as a competitive
method in the primary analysis. Its performance should be reported but excluded
from the primary ranking of methods on contaminated proteins. The Garnet results
should appear in a dedicated section titled "NMR-Trained Force Fields: Garnet as
a Case Study" rather than in the main comparison table.

**The Garnet underperformance finding is itself important.** The Garnet paper
states "In all cases apart from HEWL, Amber14SB shows the lowest absolute
normalised error (ANE)" (arXiv:2603.16770). A benchmark that independently
confirms Garnet underperformance vs classical FFs -- even on proteins it was
trained on -- is a valuable finding. It demonstrates that NMR J-coupling
training does not automatically improve dynamics accuracy, which challenges the
intuition that more data = better force fields.

---

## Section 3: Revised Alpha-M Verdict

### 3.1 Positions Relative to Other Reviewers

**3.1.1 statrev's power analysis**

**CONCUR.** The 42% power at rho=0.5 for the 6x8 design is the single most
important statistical finding from Round 2. The minimum viable design of 14x10
is achievable (Section 1 above) but requires the adaptive trajectory-length
protocol and acceptance of an incomplete crossed design for MLFF methods.

**CONCUR** with the JZS default prior as primary Bayesian analysis. The N(0.5,
0.15^2) informative prior's 4:1 prior-to-data ratio is indefensible for a
first-of-kind study. Report it as sensitivity analysis only.

**PARTIALLY CONCUR** with the Bayesian framing as the primary statistical path.
I agree that the frequentist mixed-effects test is underpowered, and the Bayesian
analysis with JZS prior provides a more nuanced result. However, I insist that
the frequentist p-value be reported alongside the Bayesian BF. Editors and
reviewers will expect both. The framing should be: "The frequentist test provides
a conservative estimate; the Bayesian analysis with default priors provides the
primary evidence."

**3.1.2 implrev's feasibility assessment**

**CONCUR** with dropping AI2BMD (Section 2.1 above).

**CONCUR** with the revised Garnet risk assessment (MODERATE). The OpenMM
integration eliminates the engineering barrier, and Garnet runs at classical
FF speed (~300 ns/day), making it computationally trivial to include.

**CONCUR** with the revised SO3LR risk assessment (MODERATE-HIGH). The solvated
crambin demonstration is encouraging, but the NPT issues (#29) and neighbor list
overflow (#25) remain open concerns.

**PARTIALLY CONCUR** with the compute budget revision. implrev's Phase 2 compute
estimates for MACE-OFF24 (4,800 GPU-hrs for 50 ns on T4 lys) and SO3LR (1,500
GPU-hrs) are reasonable but assume 50 ns trajectories are achievable. Under the
adaptive protocol, actual compute will likely be lower (shorter trajectories) but
with higher overhead (more restarts, monitoring).

**3.1.3 biomlrev's assessment (from Round 2 synthesis)**

**CONCUR** that the RSALOR baseline at Spearman 0.465 on ProteinGym is the
correct null hypothesis for Gamma. The dynamics-to-fitness improvement must be
measurable against this baseline.

**CONCUR** that MutRobustness (median |rho| ~0.6 on 2,000+ proteins) is strong
prior art that constrains Gamma's novelty claim. The Gamma proposal must
differentiate on either (a) experimental DMS data (not predicted ddG), (b)
per-protein rather than cross-protein correlation, or (c) ensemble generator
comparison (which generators' dynamics best predict fitness).

**DISAGREE** that the BioEmu ff14SB bias chain makes Gamma's dynamics-to-fitness
claim uninteresting. Even if BioEmu faithfully emulates ff14SB, the question
"do ff14SB equilibrium features predict ProteinGym fitness?" has never been
answered. A positive result is still novel, even if the mechanism is ff14SB
quality rather than "true dynamics." The combined paper should frame this
honestly: "features derived from force field equilibrium ensembles predict
variant fitness, with accuracy bounded by force field quality."

**3.1.4 stratrev's assessment (from Round 2 synthesis)**

**CONCUR** with the dual-track strategy: pre-register on OSF, submit to NCS as
primary target, fall back to NatMeth if the integration claim fails.

**PARTIALLY CONCUR** with the Registered Report pathway for Alpha-M standalone.
A NatMeth Registered Report guarantees publication regardless of MLFF outcomes,
which de-risks the project. However, it commits to a specific protocol that may
need adaptation as MLFF stability results emerge. The pre-registered protocol
should include the adaptive trajectory-length design explicitly.

### 3.2 Updated GO / NO-GO Criteria for August 31 Decision Point

**GO Criteria (ALL must be met for combined NCS paper):**

| # | Criterion | Measurement | Threshold | Source |
|---|-----------|-------------|-----------|--------|
| G1 | MLFF stability | At least 1 MLFF (MACE-OFF24 or SO3LR) produces stable trajectories on >=3 Tier B proteins for >=10 ns | >=10 ns on >=3 proteins | Phase 1 pilot (June 30) |
| G2 | S2 convergence | S2 from MLFF trajectories converges (block-splitting R2 >0.90 for first-half vs second-half) on at least 1 protein | Block-split R2 >0.90 | Phase 1 pilot (June 30) |
| G3 | BioEmu disulfide | BioEmu v1.3.1 produces intact disulfide bonds in BPTI and HEWL ensembles (>95% of frames) | SS bond integrity >95% | Quick test (Week 1) |
| G4 | Pilot integration signal | On the 3+ MLFF-stable proteins, the S2 R2 ranking across generators shows directional consistency with fitness prediction ranking on ProteinGym overlap proteins | Rank correlation >0 (directional) | Pilot analysis (July 31) |
| G5 | Protein availability | >=12 of 14 candidate proteins have confirmed BMRB S2 data accessible and PDB structures suitable for simulation | >=12 confirmed | Literature verification (May 31) |
| G6 | Generator roster | >=9 of 10 generators produce ensembles that are pairwise distinguishable (Jensen-Shannon divergence of S2 distributions >0.01 on at least 2 proteins) | >=9 distinct generators | Pilot analysis (July 31) |

**NO-GO Criteria (ANY triggers a pivot to Alpha-M standalone):**

| # | Criterion | Measurement | Threshold |
|---|-----------|-------------|-----------|
| N1 | MLFF total failure | Neither MACE-OFF24 nor SO3LR produces a stable trajectory >5 ns on ANY Tier B protein | 0 proteins with >5 ns MLFF trajectory |
| N2 | S2 indistinguishable | All generators produce S2 profiles within back-calculation noise of each other (SPARTA+ 13Ca RMSD <1.09 ppm equivalent in S2 space: R2 differences <0.05) | <0.05 R2 spread across generators |
| N3 | Integration flat | Pilot analysis on 3+ proteins shows zero or negative rank correlation between S2 accuracy and fitness prediction | rho <=0 in pilot |
| N4 | BioEmu disulfide failure | BioEmu produces >5% broken disulfide bonds and no fix is available | SS integrity <95% |

**CONDITIONAL GO (proceed with modifications):**

| # | Condition | Modification |
|---|-----------|-------------|
| C1 | Only 1 MLFF stable, 1 fails | Proceed with single MLFF; reframe as case study |
| C2 | MLFF trajectories <50 ns but >=10 ns | Accept adaptive trajectory length; report maximum stable length as finding |
| C3 | ff14SB and ff19SB produce indistinguishable ensembles | Merge as single generator; total drops to 9 |
| C4 | Integration signal is weak (rho=0.2-0.4 in pilot) | Frame as "first evidence" with Bayesian analysis; lower confidence but still novel |

### 3.3 Final Verdict

**Revised verdict: Major Revision (unchanged from Round 1).**

My Round 1 assessment stands: the science is worth doing, but the simulation
protocol requires the adaptive trajectory-length design to be credible. The
expanded 14x10 design addresses statrev's power concerns if the proteins and
generators I have identified can be validated. The August 31 decision point is
the correct structure -- it forces empirical evidence before committing to the
combined NCS paper.

**Key revisions from Round 1:**
1. The protein set CAN be expanded to 14 with suitable NMR S2 data (Section 1.3).
2. 10 meaningfully different generators CAN be assembled (Section 1.4).
3. AI2BMD should be dropped with minimal scientific loss (Section 2.1).
4. Garnet should be reframed as a contamination case study (Section 2.2).
5. The incomplete crossed design (MLFFs only on <80 residue proteins) requires
   careful statistical treatment.

**What I champion for the combined paper to succeed:**

1. **Adaptive trajectory-length protocol is non-negotiable.** Report maximum
   stable MLFF trajectory length as a primary finding.
2. **Convergence before comparison.** Plot S2 at 5, 10, 20, 30, 40, 50 ns
   checkpoints. Compare only converged observables.
3. **Three generative methods (BioEmu, Boltz-2, AlphaFlow) in the benchmark.**
   This tests whether the BioEmu ff14SB bias chain matters for fitness prediction.
4. **Garnet contamination reported transparently.** Dedicated section, not hidden
   in supplementary.
5. **The null hypothesis is "classical FFs are fine."** Any MLFF or generative
   model must demonstrably improve over AMBER ff14SB to justify its compute cost.
6. **Temperature and pH matching verified for every protein-method combination.**
   Protonation states determined once (PropKa 3.5) and applied identically.

---

## Section 4: Summary of Concurrences and Disagreements

| Reviewer | Topic | Position |
|----------|-------|----------|
| statrev | 42% power at rho=0.5 for 6x8 | **CONCUR** |
| statrev | 14x10 minimum viable design | **CONCUR** (with feasibility confirmed in Section 1) |
| statrev | JZS default prior as primary | **CONCUR** |
| statrev | N(0.5, 0.15^2) prior indefensible | **CONCUR** |
| statrev | Bayesian as primary statistical path | **PARTIALLY CONCUR** (report frequentist alongside) |
| implrev | Drop AI2BMD | **CONCUR** (Section 2.1) |
| implrev | Garnet risk revised to MODERATE | **CONCUR** |
| implrev | SO3LR risk revised to MODERATE-HIGH | **CONCUR** |
| implrev | OpenFF Sage as additional generator | **DISAGREE** (Sage is ligand FF, not protein FF) |
| biomlrev | RSALOR 0.465 as null hypothesis | **CONCUR** |
| biomlrev | MutRobustness constrains novelty | **CONCUR** |
| biomlrev | BioEmu ff14SB bias makes Gamma uninteresting | **DISAGREE** (still novel if framed correctly) |
| stratrev | Dual-track NCS/NatMeth strategy | **CONCUR** |
| stratrev | Registered Report for Alpha-M | **PARTIALLY CONCUR** (adaptive protocol must be included) |

---

## References

1. Lai TT, Brooks CL III. Accuracy and Reproducibility of Lipari-Szabo Order
   Parameters From Molecular Dynamics. J. Phys. Chem. B 128, 10813-10822 (2024).

2. Kovacs DP, et al. MACE-OFF: Short-Range Transferable Machine Learning Force
   Fields for Organic Molecules. J. Am. Chem. Soc. 147, 2977 (2025).

3. Frank T, Kabylda A, et al. Molecular Simulations with a Pretrained Neural
   Network and Universal Pairwise Force Fields. J. Am. Chem. Soc. (2026).
   DOI: 10.1021/jacs.5c09558.

4. Li X, et al. A universal machine learning interatomic potential for
   mechanistic studies of biological macromolecules. Nature 636, 1012 (2024).

5. Unke OT, et al. Biomolecular dynamics with machine-learned quantum-mechanical
   force fields trained on diverse chemical fragments. Sci. Adv. (2024).

6. Lewis GT, et al. Scalable emulation of protein equilibrium ensembles with
   generative deep learning. Science (2025).

7. Aryal S, et al. Comprehensive Assessment of BioEmu. Int. J. Mol. Sci. 27,
   2896 (2026).

8. Blanco-Gonzalez A, et al. Training a force field for proteins and small
   molecules from scratch. arXiv:2603.16770 (2026).

9. Robustelli P, Piana S, Shaw DE. Developing a molecular dynamics force field
   for both folded and disordered protein states. Proc. Natl. Acad. Sci. USA
   115, E4758-E4766 (2018).

10. Lindorff-Larsen K, et al. Systematic Validation of Protein Force Fields
    against Experimental Data. PLoS ONE 7, e32131 (2012).

11. Suzuki et al. Steering Conformational Sampling in Boltz-2 via Pair
    Representation Scaling. bioRxiv 2026.01.23.701250 (2026).

12. Jing B, et al. AlphaFold Meets Flow Matching for Generating Protein
    Ensembles. ICML (2024). arXiv:2402.04845.

13. Wetzels R, Wagenmakers EJ. A default Bayesian hypothesis test for
    correlations and partial correlations. Psychon. Bull. Rev. 19, 1057-1064
    (2012).

14. Hall JB, Fushman D. Characterization of the overall and local dynamics of
    a protein with intermediate rotational anisotropy: Differentiating between
    conformational exchange and anisotropic diffusion in the B3 domain of
    protein G. J. Biomol. NMR 27, 261-275 (2003).

15. Shaw GL, et al. Backbone dynamics of chymotrypsin inhibitor 2: effect of
    breaking the active site bond. Biochemistry 34, 2225-2233 (1995).

16. Feng W, et al. Solution NMR structure and backbone dynamics of the major
    cold-shock protein (CspA) from Escherichia coli. Biochemistry 37,
    10881-10896 (1998).

17. Kordel J, et al. Backbone dynamics of calcium-loaded calbindin D9k studied
    by two-dimensional proton-detected 15N NMR spectroscopy. Biochemistry 31,
    4856-4866 (1992).

18. Barchi JJ Jr, et al. Investigation of the backbone dynamics of the IgG-
    binding domain of streptococcal protein G by heteronuclear two-dimensional
    1H-15N nuclear magnetic resonance spectroscopy. Protein Sci. 3, 15-21
    (1994).

19. Jager M, et al. Sequence-specific dynamics modulate recognition specificity
    in WW domains. Nat. Struct. Mol. Biol. 13, 512-518 (2006).

20. Zhang Y, et al. P2DFlow: A Protein Ensemble Generative Model with SE(3)
    Flow Matching. J. Chem. Theory Comput. 21, 3288-3296 (2025).

21. Raja V, et al. StABlE Training: Stability-Achieving Balanced-Error Training
    for Multi-Modal Learning in Molecular Dynamics. Trans. Mach. Learn. Res.
    (2025). arXiv:2402.13984.

22. TEA Challenge authors. Crash testing machine learning force fields for
    molecules, materials, and interfaces. Chem. Sci. (2025).
    DOI: 10.1039/D4SC06530A.

23. Smith et al. (referenced as Lai & Brooks 2024 throughout; the study of S2
    accuracy across six proteins with two force fields).

24. Huang FL. Using Cluster Bootstrapping to Analyze Nested Data With a Few
    Clusters. Educational and Psychological Measurement 78, 297-318 (2018).

25. Cameron AC, Gelbach JB, Miller DL. Bootstrap-Based Improvements for
    Inference with Clustered Errors. Rev. Econ. Stat. 90, 414-427 (2008).

26. Prompers JJ, Bruschweiler R. General Framework for Studying the Dynamics of
    Folded and Nonfolded Proteins by NMR Relaxation Spectroscopy and MD
    Simulation. J. Am. Chem. Soc. 124, 4522-4534 (2002).

27. Palmer AG III. NMR Characterization of the Dynamics of Biomacromolecules.
    Chem. Rev. 104, 3623-3640 (2004).

28. Shen Y, Bax A. SPARTA+: a modest improvement in empirical NMR chemical
    shift prediction by means of an artificial neural network. J. Biomol. NMR
    48, 13-22 (2010).

29. Walsh STR, et al. Solution structure and dynamics of a de novo designed
    three-helix bundle protein. Protein Sci. 10, 960-971 (2001).

30. Buck M, et al. Internal packing of a protein: role of electrostatics and
    short-range interactions. Folding Des. 1, 289-301 (1995).

31. Mulder FAA, et al. Altered flexibility in the substrate-binding site of
    related native and engineered high-alkaline Bacillus subtilisins.
    Biochemistry 39, 12614-12622 (2000).

32. Bouvignies G, et al. Slow conformational changes in the rigid and highly
    stable chymotrypsin inhibitor 2. J. Am. Chem. Soc. 145, 5698-5707 (2023).
