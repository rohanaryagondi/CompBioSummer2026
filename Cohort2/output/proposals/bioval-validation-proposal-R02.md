---
agent: bioval
round: 2
date: 2026-04-14
type: proposal
proposal_id: alpha-m-validation
---

# Proposal: Alpha-M Validation Data Pipeline and Analysis Protocol

## Proposing Agent

**Biophysical Validation & Experimental Data Expert (bioval)**
Senior biophysical validation expert (20+ years structural biology, NMR spectroscopy, SAXS, and computational biophysics). I bridge the gap between simulation and experiment -- I know which databases contain what data, how to extract and curate reference observations, and how to handle the messy realities of comparing computed trajectories to experimental measurements. I champion multi-observable validation, honest uncertainty quantification, and calibration of pass/fail thresholds against established classical force field performance.

---

## Problem Statement

No systematic benchmark has ever evaluated ML force fields (MLFFs) for biomolecular simulation against the full suite of experimental NMR and SAXS observables available for proteins. Existing MLFF papers validate against DFT energies, water properties, or at best one or two J-couplings on a single peptide (e.g., AI2BMD validated 3JHNHa on alanine dipeptide units; Wang et al., Nature 2024). Meanwhile, the classical force field community has spent decades curating benchmark protein sets with rich multi-observable NMR data -- S2 order parameters, chemical shifts, J-couplings, RDCs, and SAXS profiles -- but these benchmarks have never been applied to MLFFs. This proposal provides the complete experimental data pipeline and analysis protocol needed to close this gap: a curated, execution-ready inventory of reference data for 7 MVP proteins (plus 8 stretch-goal proteins), with step-by-step extraction, back-calculation, and statistical comparison protocols.

---

## Vision

After this project succeeds, the computational biophysics community will have a publicly available, reproducible benchmark dataset linking MLFF simulation trajectories to experimental protein observables. Every future MLFF paper will be expected to report its performance on this benchmark, analogous to how UniFFBench (Yang et al., 2024) transformed materials-science MLFF evaluation. For each protein in the benchmark, a "scorecard" will report how well each MLFF reproduces backbone dynamics (S2), local structure (chemical shifts, J-couplings), bond orientation (RDCs), and global shape (SAXS). Classical force fields (AMBER ff19SB, CHARMM36m) serve as calibrated baselines. This transforms MLFF evaluation from "does the simulation crash?" to "does it match reality?"

---

## Background and Evidence

### Current State of the Art

Classical force field validation against NMR observables is mature but limited to a small number of benchmark studies:

- **Lindorff-Larsen et al. (PLoS ONE, 2012):** Tested 8 force fields against NMR data (S2, J-couplings, RDCs, chemical shifts) for 4 folded proteins (ubiquitin, GB3, HEWL, BPTI) using 1.2 us simulations on the Anton supercomputer. Established the multi-observable comparison standard.

- **Robustelli et al. (PNAS, 2018):** Benchmarked 6 force fields across 21 systems (folded proteins, IDPs, peptides) against >9,000 experimental data points. Developed the a99SB-disp force field. Remains the most comprehensive protein FF benchmark.

- **Smith/Gowers et al. (J. Phys. Chem. B, 2024):** Focused specifically on S2 order parameter convergence using 6 proteins (ubiquitin, T4 lysozyme, alpha-3D, MFABP, ALBP, flavodoxin). Demonstrated that 10-20 replicas are required for reproducible S2 values. AMBER ff14SB achieves R2=0.62; CHARMM36m achieves R2=0.51.

- **Raddi et al. (J. Chem. Theory Comput., 2025):** Applied BICePs Bayesian scoring to 9 force fields on chignolin CLN025 using 158 NMR measurements (139 NOEs, 13 chemical shifts, 6 J-couplings). Provides the most rigorous single-protein FF ranking.

No equivalent multi-observable benchmark exists for any MLFF. AI2BMD (Wang et al., Nature 2024) validated 3JHNHa couplings for 18 dipeptide units (Pearson r=0.924 vs 0.543 for classical MM), but never on actual proteins in realistic solvent. MACE-OFF24 (Kovacs et al., JACS 2025) demonstrated a stable 1.6 ns crambin simulation but reported no NMR comparison. SO3LR validated on small peptides only. This is the gap Alpha-M fills.

### Recent Developments That Enable This

1. **MLFF maturity:** MACE-OFF24(M), SO3LR, and AI2BMD can now run stable multi-nanosecond protein simulations in explicit water via OpenMM-ML (see mlffeng Round 1 report). ANI-2x is disqualified (amorphous ice failure), narrowing the field to tractable comparison.

2. **BMRB data richness:** The Biological Magnetic Resonance Bank contains ~21,820 NMR entries, with ~119 deposited S2 datasets and thousands of chemical shift assignments. Programmatic access is available via the BMRB REST API (api.bmrb.io/v2/) and PyNMRSTAR parser.

3. **SASBDB consensus data:** The 2024 SAXS round-robin benchmark (Grudinin et al., IUCrJ 2024) produced maximum-likelihood consensus SAXS profiles for 5 proteins including lysozyme (SASDUE4), providing independently validated SAXS reference standards.

4. **Back-calculation tools:** SHIFTX2, SPARTA+, UCBShift 2.0, SPyCi-PDB, PALES, Pepsi-SAXS, and FoXS are all freely available and well-characterized for accuracy. MDTraj provides integrated SHIFTX2 access for trajectory analysis.

5. **S2 convergence protocol:** Gowers et al. (2024) established that N=20 replicas of tens-of-ns simulations achieve r2>=0.95 agreement, providing the definitive guidance for trajectory length and replica count.

### Key Prior Work

1. **Lindorff-Larsen et al. (2012):** Multi-observable FF benchmark on 4 proteins. PLoS ONE 7(2): e32131.
2. **Robustelli et al. (2018):** a99SB-disp benchmark on 21 systems, >9,000 data points. PNAS 115(21): E4758.
3. **Gowers et al. (2024):** S2 convergence from MD: 10-20 replicas required. J. Phys. Chem. B 128: 10090.
4. **Wang et al. (2024):** AI2BMD Nature paper with 3JHNHa dipeptide validation. Nature 636: 1012.
5. **Kovacs et al. (2025):** MACE-OFF24 stable crambin simulation. JACS 147: 2977.
6. **Grudinin et al. (2024):** SAXS benchmark with ML consensus. IUCrJ 11(5): 834.
7. **Han et al. (2011):** SHIFTX2 chemical shift prediction. J. Biomol. NMR 50: 43.
8. **Shen & Bax (2010):** SPARTA+ chemical shift prediction. J. Biomol. NMR 48: 13.
9. **Li et al. (2024):** UCBShift 2.0 side-chain shift prediction. JACS 146: 33989.
10. **Raddi et al. (2025):** BICePs scoring of 9 FFs on chignolin. J. Chem. Theory Comput.

---

## Proposed Approach

### Overview

This proposal defines the complete experimental validation data pipeline for Alpha-M. It covers: (1) final protein selection with per-protein data inventories, (2) NMR data extraction from BMRB with standardization, (3) SAXS data from SASBDB, (4) back-calculation methods for each observable type, (5) statistical comparison framework with pass/fail thresholds calibrated against classical FFs, and (6) integration with the Gamma project via 8 overlapping ProteinGym proteins. The pipeline is designed so that once MLFF trajectories are generated by mlffeng, validation analysis can be executed in a standardized, reproducible manner.

### Method Details

#### Component 1: Final Protein Selection -- 7 MVP + 8 Stretch

##### MVP Set (7 Proteins)

These 7 proteins form the core benchmark. All have extensive NMR data, classical FF validation precedent, and manageable system sizes for MLFF simulation.

**Protein 1: Ubiquitin**
- **PDB ID:** 1UBQ (resolution 1.80 A)
- **Chain length:** 76 residues
- **BMRB entries:** 68 (chemical shifts), 4769 (chemical shifts + 15N relaxation), 5387 (chemical shifts), 17769 (backbone S2 order parameters + T1/T2/hetNOE), 6457 (S2 order parameters)
- **S2 data:** ~65-70 backbone NH S2 values; ~20 methyl CH3 S2 values (from selected studies)
- **Chemical shifts:** Complete backbone (13Ca, 13Cb, 13C', 15N, 1HN, 1Ha) + near-complete side chains. RefDB re-referenced entries available.
- **J-couplings:** ~70+ 3JHNHa values from multiple Bax lab studies. Gold-standard Karplus reparametrization derived from ubiquitin data (Wang & Bax, JACS 1996).
- **RDCs:** 5+ datasets in multiple alignment media (phage, bicelle, PEG/hexanol), ~65 NH RDCs per set.
- **SAXS:** Published Rg ~13.0-13.5 A (multiple studies). No full I(q) profile in SASBDB; use literature Rg.
- **ProteinGym overlap:** YES. UBI4_YEAST (P0CG63). Roscoe et al. (2013) and Mavor et al. (2016): yeast growth fitness, ~1,500-2,000 single-point mutants.
- **Measurement conditions:** pH 6.5, 298 K, 50-100 mM phosphate buffer
- **Classical FF precedent:** Lindorff-Larsen 2012, Smith/Gowers 2024, Robustelli 2018
- **Rationale:** The single most extensively characterized protein by NMR. Gold standard.

**Protein 2: GB3 (Protein G B3 domain)**
- **PDB ID:** 2OED (resolution 1.10 A)
- **Chain length:** 56 residues
- **BMRB entries:** 5909 (chemical shifts), 7280 (chemical shifts), 15283 (solid-state CS, published Biomol. NMR Assign. 2007), 25807 (RDC data for side-chain chi1 distributions, JACS 2015)
- **S2 data:** ~50-54 backbone NH S2 values. RDC-derived dynamic information in 25807.
- **Chemical shifts:** Complete backbone (13Ca, 13Cb, 13C', 15N, 1HN, 1Ha). Multiple depositions for cross-validation.
- **J-couplings:** ~50+ 3JHNHa values from Bax/Tjandra labs.
- **RDCs:** 36 RDC datasets in 5 independent alignment media (~50-56 values per set). Richest RDC dataset of any protein. Chi1 side-chain distributions from RDC (Chou et al., JACS 2015).
- **SAXS:** Published Rg from literature; no SASBDB entry.
- **ProteinGym overlap:** YES (via GB1 homolog, SPG1_STRSG). Olson et al. (2014): IgG binding, ~500-800 variants. GB3 and GB1 share 96% structural identity.
- **Measurement conditions:** pH 5.6, 298 K, 50 mM sodium phosphate
- **Classical FF precedent:** Lindorff-Larsen 2012, Best 2012, Robustelli 2018
- **Rationale:** RDC gold standard; smallest protein in set; excellent for testing bond vector orientations.

**Protein 3: HEWL (Hen Egg White Lysozyme)**
- **PDB ID:** 1IEE (resolution 0.94 A, atomic resolution)
- **Chain length:** 129 residues
- **BMRB entries:** 4562 (chemical shifts), 18304 (backbone NH S2 + T1/T2/hetNOE), 18305 (methyl S2)
- **S2 data:** ~120 backbone NH S2 + ~60 methyl CH3 S2 values. Both backbone and side-chain dynamics available.
- **Chemical shifts:** Extensive backbone (13Ca, 13Cb, 13C', 15N, 1HN, 1Ha) and side chains.
- **J-couplings:** ~110+ 3JHNHa values from multiple laboratories.
- **RDCs:** 1-2 sets in phage alignment, ~120 values.
- **NOEs:** 2,043 distance restraints used in structural ensemble determination.
- **SAXS:** SASDUE4 -- consensus SAXS data from 2024 round-robin benchmark (Grudinin et al., IUCrJ 2024). Additional: SASDMG2 (0.4 mg/mL, 10 C) and SASDMF2 (0.9 mg/mL, 10 C) SWAXS data. Rg ~14.5 A.
- **ProteinGym overlap:** NO
- **Measurement conditions:** pH 3.8, 308 K (NOTE: low pH, elevated temperature)
- **Classical FF precedent:** Lindorff-Larsen 2012, Smith/Gowers 2024, SASBDB round-robin
- **Rationale:** Best multi-observable protein. Unique combination of atomic-resolution crystal structure, comprehensive NMR dynamics (backbone + methyl), AND high-quality consensus SAXS. The definitive multi-observable validation case.
- **CAUTION:** pH 3.8 requires explicit protonation state assignment using PropKa or H++. Simulate at 308 K to match NMR data.

**Protein 4: BPTI (Bovine Pancreatic Trypsin Inhibitor)**
- **PDB ID:** 5PTI (resolution 1.00 A)
- **Chain length:** 58 residues
- **BMRB entries:** 1093 (chemical shifts, related relaxation data), 4021 (additional chemical shifts)
- **S2 data:** ~50-55 backbone NH S2 values from classic Lipari-Szabo analysis.
- **Chemical shifts:** Backbone 13Ca, 13Cb, 15N, 1HN, 1Ha. Moderate side-chain coverage.
- **J-couplings:** ~45+ 3JHNHa values (Lindorff-Larsen 2012 dataset).
- **RDCs:** 1-2 sets in standard alignment, ~45 values.
- **SAXS:** Published Rg ~11.5-12.0 A (Best et al. estimates). No SASBDB entry.
- **ProteinGym overlap:** NO
- **Measurement conditions:** pH 4.6, 308 K (elevated temperature)
- **Classical FF precedent:** Lindorff-Larsen 2012, Robustelli 2018
- **Rationale:** Classic dynamics test case; contains 3 disulfide bonds (tests MLFF handling of S-S bonds); small and fast to simulate.
- **NOTE:** 3 disulfide bonds (Cys5-Cys55, Cys14-Cys38, Cys30-Cys51) must be correctly modeled.

**Protein 5: Barnase**
- **PDB ID:** 1BNR (resolution 1.50 A)
- **Chain length:** 110 residues
- **BMRB entries:** 7139 (chemical shifts + 2H methyl relaxation data for free barnase and barnase-barstar complex, J. Mol. Biol. 2007), 26619 (additional NMR data)
- **S2 data:** ~95 backbone NH S2 values + ~40 methyl CH3 S2 values from 2H relaxation (Showalter & Bruschweiler 2007 and related studies).
- **Chemical shifts:** Backbone 13Ca, 13Cb, 13C', 15N, 1HN. Moderate side-chain coverage.
- **J-couplings:** Limited published 3JHNHa data; back-calculate from trajectory phi angles.
- **RDCs:** Limited; not a primary RDC test protein.
- **SAXS:** Published Rg from literature. No SASBDB entry.
- **ProteinGym overlap:** YES. RNBR_BACAM. Stiffler et al. (2015): catalytic activity, ~1,800+ single-point mutants.
- **Measurement conditions:** pH 6.5, 298 K, standard buffer
- **Classical FF precedent:** Showalter & Bruschweiler 2007
- **Rationale:** Excellent methyl dynamics dataset. The backbone + methyl S2 combination probes both backbone and side-chain accuracy simultaneously. DMS overlap provides the enzyme dynamics-to-function link.

**Protein 6: T4 Lysozyme**
- **PDB ID:** 107L (resolution 1.70 A)
- **Chain length:** 164 residues
- **BMRB entries:** 915 (backbone 1H + 15N assignments, Biochemistry 1990), 26823 (additional assignments), multiple entries with relaxation data
- **S2 data:** ~140-150 backbone NH S2 values. Some missing loop data. Largest folded protein in the S2 benchmark set.
- **Chemical shifts:** Backbone 13Ca, 15N, 1HN. Moderate coverage.
- **J-couplings:** Limited published 3JHNHa.
- **RDCs:** Limited.
- **SAXS:** Published Rg from literature. No SASBDB entry.
- **ProteinGym overlap:** YES. LYSB_BPT4 (P00720). Klesmith et al. (2015): thermostability; Leuenberger et al. (2017): proteome stability. ~2,500+ single-point mutants.
- **Measurement conditions:** pH 5.5, 310 K (elevated temperature)
- **Classical FF precedent:** Smith/Gowers 2024
- **Rationale:** Largest folded protein in MVP, providing the scale test for MLFFs. Extensive DMS data with diverse functional readouts (thermostability AND activity). S2 coverage probes dynamics across a 164-residue alpha-helical protein.
- **NOTE:** Simulate at 310 K to match NMR conditions.

**Protein 7: Crambin**
- **PDB ID:** 1CRN (resolution 0.54 A, ultra-high resolution)
- **Chain length:** 46 residues
- **BMRB entries:** Limited backbone chemical shifts.
- **S2 data:** No deposited S2 order parameters. B-factors from ultra-high-resolution crystal structure serve as proxy for positional disorder.
- **Chemical shifts:** Limited backbone only.
- **J-couplings:** Not available in BMRB.
- **RDCs:** Not available.
- **SAXS:** Not available in SASBDB.
- **ProteinGym overlap:** NO
- **Measurement conditions:** N/A (crystal structure only; neutron data at 15 K, 295 K)
- **Classical FF precedent:** Already tested by MACE-OFF24 and SO3LR (primary MLFF test system)
- **Rationale:** Included because it is the de facto MLFF protein test case (MACE-OFF24's 1.6 ns stable simulation was on crambin). Ultra-high resolution structure provides the best possible starting coordinates. Validation limited to structural stability metrics (RMSD, RMSF, secondary structure retention, B-factor comparison) rather than full NMR multi-observable analysis. Essential for cross-referencing our protocol with published MLFF results.

##### Stretch Set (8 Additional Proteins)

These 8 proteins add fold diversity, IDP coverage, and ProteinGym integration. They are prioritized for inclusion if compute and timeline allow.

**Protein 8: RNase H (E. coli)**
- **PDB ID:** 2RN2 (resolution 1.48 A)
- **Chain length:** 155 residues
- **BMRB entries:** 27721 (backbone + methyl chemical shifts, 2H relaxation data at 475/950 MHz, J. Biomol. NMR 2024)
- **S2 data:** ~130 backbone NH S2 + ~50 methyl CH3 S2 from 2H relaxation. Best methyl side-chain dynamics dataset.
- **Chemical shifts:** Extensive (13Ca, 13Cb, 13C', 15N, 1HN, 1Ha).
- **ProteinGym overlap:** NO
- **Measurement conditions:** pH 5.5, 300 K
- **Rationale:** Gold-standard methyl dynamics; tests MLFF side-chain accuracy.

**Protein 9: Cyclophilin A (CypA)**
- **PDB ID:** 3K0N (resolution 0.87 A, near-atomic)
- **Chain length:** 165 residues
- **BMRB entries:** Multiple entries with backbone S2 and chemical shifts.
- **S2 data:** ~140-150 backbone NH S2 values. Multi-state dynamics detected.
- **Room-temperature crystallography:** Fraser et al. (eLife 2015) mapped conformational heterogeneity at 100-310 K using 8 synchrotron datasets. Alternative conformations transition from single to multi-state between 180-240 K.
- **ProteinGym overlap:** NO
- **Measurement conditions:** pH 6.5, 298 K
- **Rationale:** Tests MLFF ability to capture conformational heterogeneity; orthogonal crystallographic validation.

**Protein 10: Chignolin (CLN025)**
- **PDB ID:** 5AWL (NMR structure)
- **Chain length:** 10 residues
- **BMRB entries:** Multiple entries with chemical shifts and J-couplings.
- **NMR data:** 158 measurements total: 139 NOE distances, 13 chemical shifts, 6 3JHNHa.
- **ProteinGym overlap:** NO
- **Measurement conditions:** Variable; multiple published studies
- **Rationale:** BICePs-scored mini-protein with 9 classical FF scores (Raddi et al., 2025). Direct comparison to published BICePs ranking. Fastest to simulate (10 residues).

**Protein 11: SH3 Domain (Fyn Kinase)**
- **PDB ID:** 1SHF (resolution 1.80 A)
- **Chain length:** 58 residues
- **BMRB entries:** Multiple entries with backbone S2, chemical shifts, J-couplings, RDCs.
- **S2 data:** ~50-55 backbone NH S2 values.
- **ProteinGym overlap:** NO
- **Measurement conditions:** pH 6.0, 298 K
- **Rationale:** Beta-barrel fold diversity; dynamics on multiple timescales; accelerated MD validated.

**Protein 12: alpha-Synuclein**
- **PDB ID:** None (IDP; use extended chain or ensemble starting structures)
- **Chain length:** 140 residues
- **BMRB entries:** 7 depositions with chemical shifts, J-couplings.
- **NMR data:** Complete backbone CS (13Ca, 13Cb, 13C', 15N, 1HN), ~130+ 3JHNHa values, 2+ RDC sets (strained gels, bicelle), PRE data for long-range contacts.
- **SAXS:** SASBDB entries available. Published Rg ~28-35 A (condition-dependent). Refinement studies (Frontiers Mol. Biosci. 2021) provide force-field-calibrated ensemble Rg.
- **ProteinGym overlap:** YES. SYUA_HUMAN. Aggregation assays, ~1,000+ variants.
- **Measurement conditions:** pH 6.5-7.4, 288-298 K, 100 mM NaCl
- **Rationale:** Most-studied IDP; Parkinson's disease relevance; combined NMR+SAXS data tests MLFF IDP performance. ProteinGym aggregation DMS.

**Protein 13: HIV-1 Protease**
- **PDB ID:** 2PC0 (resolution 1.10 A)
- **Chain length:** 99x2 (dimer, 198 residues total)
- **BMRB entries:** Multiple entries with backbone S2, chemical shifts, flap dynamics data.
- **ProteinGym overlap:** YES. POL_HV1N5. Boucher et al. (2014): drug resistance/fitness, ~1,000+ variants.
- **Measurement conditions:** Variable pH (4.7-6.5), 293-298 K
- **Rationale:** Drug-relevant; flap dynamics are functionally critical; dimer tests MLFF oligomer handling.
- **CAUTION:** Homodimer requires careful MLFF setup; may need special treatment for interchain contacts.

**Protein 14: p53 (DNA-Binding Domain)**
- **PDB ID:** 2XWR (resolution 1.90 A)
- **Chain length:** 195 residues
- **BMRB entries:** Multiple entries with chemical shifts, backbone S2.
- **ProteinGym overlap:** YES. P53_HUMAN. Giacomelli et al. (Nature Genetics 2018): transcription activity (loss-of-function, dominant-negative, DNA damage repair), ~8,200+ single-point mutants. Largest DMS dataset in ProteinGym.
- **Measurement conditions:** pH 7.0-7.5, 298 K
- **Rationale:** Largest DMS dataset enables highest-powered Gamma integration. Cancer relevance. Alpha/beta fold at 195 residues tests MLFF scale.
- **NOTE:** Contains Zn2+ binding site (Cys176, His179, Cys238, Cys242). MLFF handling of metal coordination must be verified.

**Protein 15: SNase (Staphylococcal Nuclease)**
- **PDB ID:** 1SNO (resolution 1.65 A)
- **Chain length:** 149 residues
- **BMRB entries:** Multiple entries with backbone S2, chemical shifts, 3JHNHa couplings, T1/T2 relaxation.
- **ProteinGym overlap:** YES. NUC_STAAU. Shortle mutant library: enzymatic activity, ~500+ variants.
- **Measurement conditions:** pH 5.5-7.0, 298-303 K
- **Rationale:** Classic folding model; Shortle's extensive mutant library provides well-characterized stability/activity landscape.

##### Data Completeness Summary: MVP Proteins

| Protein | S2 (n) | CS Nuclei | 3JHNHa (n) | RDC Sets | SAXS | ProteinGym | Sim. T (K) |
|---------|--------|-----------|------------|----------|------|------------|------------|
| Ubiquitin | ~70 NH | 6 types | ~70 | 5+ | Rg only | YES | 298 |
| GB3 | ~54 NH | 6 types | ~50 | 36 (5 media) | Rg only | YES (GB1) | 298 |
| HEWL | ~120 NH + ~60 CH3 | 6 types | ~110 | 1-2 | SASDUE4 consensus | NO | 308 |
| BPTI | ~55 NH | 5 types | ~45 | 1-2 | Rg only | NO | 308 |
| Barnase | ~95 NH + ~40 CH3 | 5 types | limited | limited | Rg only | YES | 298 |
| T4 Lysozyme | ~150 NH | 3 types | limited | limited | Rg only | YES | 310 |
| Crambin | none | limited | none | none | none | NO | 298 |

**Total NMR data points across 7 MVP proteins:** ~1,500-2,000 (S2 + CS + J-couplings + RDCs)

---

#### Component 2: NMR Data Extraction Protocol

##### Step 1: BMRB Entry Identification and Download

For each protein, identify all relevant BMRB entries using:
1. BMRB query grid (bmrb.io/search/query_grid) -- search by PDB ID
2. BMRB featured systems pages (bmrb.io/featuredSys/) for ubiquitin, lysozyme
3. BMRB REST API (api.bmrb.io/v2/) for programmatic batch queries

Download NMR-STAR 3.1 format files for all identified entries. Use PyNMRSTAR (bmrb-io/PyNMRSTAR on GitHub) for programmatic parsing.

##### Step 2: Chemical Shift Extraction and Standardization

**Extraction:**
- Parse chemical shift lists from NMR-STAR saveframes tagged `_Chem_shift_list`
- Extract per-residue values for backbone nuclei: 13Ca, 13Cb, 13C', 15N, 1HN, 1Ha
- Extract side-chain shifts where available (13C, 1H, 15N)

**Re-referencing:**
- Apply RefDB corrections (refdb.wishartlab.com; Zhang et al., J. Biomol. NMR 2003). Nearly 25% of BMRB entries with 13C assignments and 27% with 15N assignments contain significant referencing errors.
- For proteins with RefDB-corrected entries, use those directly.
- For proteins without RefDB entries, apply BaMORC (Hsu et al., 2021) for automated 13C reference correction.
- Convert all shifts to IUPAC nomenclature.

**Quality control:**
- Flag chemical shifts >3 SD from random coil values (Platzer et al., J. Biomol. NMR 2014, pH-dependent random coil shifts from BMRB statistics page)
- For proteins with multiple BMRB entries (e.g., ubiquitin: 12+ entries), compute inter-entry SD to quantify experimental uncertainty
- Require >=80% backbone assignment completeness for inclusion
- Verify temperature and pH match between BMRB entry and intended simulation conditions

##### Step 3: S2 Order Parameter Extraction

**Source identification:**
- S2 order parameters are deposited in BMRB as model-free analysis results within relaxation data saveframes
- Search for entries containing `_Order_param` tags
- Cross-reference with published literature for specific BMRB entries (listed per-protein above)

**Data extraction:**
- Extract residue number, S2 value, and S2 error (if deposited)
- Distinguish backbone NH S2 from methyl CH3 S2 (axis order parameter) and report separately
- Verify Lipari-Szabo model used (model-free, extended model-free, spectral density mapping)
- Record spectrometer field strength(s) used for relaxation measurements

**Quality control:**
- Exclude residues with S2 error > 0.10 (unreliable model-free fits)
- Exclude residues in exchange (Rex > 2 s-1 from model-free fits) unless Rex is explicitly modeled
- For proteins with multiple S2 studies, use the most recent and comprehensive dataset
- Report number of usable S2 values per protein

##### Step 4: J-Coupling Extraction

**Extraction:**
- Parse 3JHNHa coupling constants from NMR-STAR files tagged `_Coupling_constant`
- Where BMRB data is incomplete, extract from published supplementary materials of Lindorff-Larsen (2012) and Robustelli (2018) benchmark sets
- Record measurement method (HNHA, quantitative J-correlation, etc.) and estimated error

**Quality control:**
- Flag 3JHNHa values < 2 Hz or > 12 Hz as potential errors (outside Karplus range for standard backbone geometry)
- Exclude glycine residues (Karplus parametrization differs for glycine)
- Exclude proline residues (no NH amide)

##### Step 5: RDC Extraction

**Extraction:**
- Parse RDC values from NMR-STAR saveframes tagged `_RDC_constraint`
- For GB3: extract all 36 RDC datasets from 5 alignment media (BMRB 25807 and related entries)
- For ubiquitin: extract 5+ datasets from multiple alignment media
- Record alignment medium, coupling type (NH, CaHa, CaCb), and estimated error

**Quality control:**
- Verify alignment tensor consistency within each dataset (PALES best-fit Q-factor)
- Exclude datasets with Q-factor > 0.5 on the reference crystal structure
- For multi-medium datasets, check SECONDA analysis for internal consistency

##### Step 6: Format Standardization

All extracted data organized into standardized CSV files per protein:

```
experimental_data/
  {protein_name}/
    structure/
      {pdb_id}.pdb                    # Reference crystal structure
    nmr/
      chemical_shifts_backbone.csv    # residue, atom_name, shift_ppm, error, bmrb_entry
      chemical_shifts_sidechain.csv   # residue, atom_name, shift_ppm, error, bmrb_entry
      S2_backbone_NH.csv              # residue, S2, S2_error, model, bmrb_entry
      S2_methyl_CH3.csv               # residue, atom_name, S2_axis, S2_error, bmrb_entry
      j_couplings_3JHNHa.csv          # residue, J_Hz, J_error, method, bmrb_entry
      rdc_NH.csv                      # residue, RDC_Hz, error, alignment_medium, bmrb_entry
    saxs/
      I_q_experimental.dat            # q_A-1, I_q, sigma_q (SASBDB format)
      Rg_published.txt                # Rg_A, Rg_error, source_reference
    metadata.yaml                     # T_K, pH, ionic_strength_mM, buffer, bmrb_entries, sasbdb_entries
```

---

#### Component 3: SAXS Data Extraction and Processing

##### SASBDB Data Download (HEWL and alpha-Synuclein)

**HEWL (primary SAXS benchmark protein):**
1. Download SASDUE4 (updated consensus SAXS data) from sasbdb.org/data/SASDUE4/
2. Download SASDMG2 (SWAXS, 0.4 mg/mL, 10 C) and SASDMF2 (SWAXS, 0.9 mg/mL, 10 C) for concentration-dependent analysis
3. Extract I(q), sigma(q), q-range, Rg from Guinier fit, molecular weight from I(0)

**Quality assessment checklist:**
- Guinier linearity: Rg * qmax < 1.3
- P(r) consistency: Rg from Guinier agrees within 5% with Rg from P(r)
- Molecular weight: I(0)-derived MW agrees within 10% of sequence-predicted MW (14,300 Da for HEWL)
- Concentration independence: Rg does not vary > 3% across concentrations

**alpha-Synuclein:**
1. Search SASBDB by UniProt SYUA_HUMAN or protein name
2. Download I(q) profile(s); record buffer conditions
3. Note condition-dependent Rg (range 28-35 A depending on salt, pH)

**Other proteins -- Literature Rg only:**
For ubiquitin, GB3, BPTI, barnase, T4 lysozyme, crambin: extract published Rg values from literature and record source. These will be compared to Rg computed from MLFF trajectory ensemble.

##### q-Range Selection for Comparison

- **SAXS comparison range:** 0.01 < q < 0.30 A-1 (standard SAXS regime)
- **WAXS extension (if available):** up to q = 2.0 A-1 for HEWL SWAXS data
- Exclude q < 0.005 A-1 (inter-particle interference) and q > 0.5 A-1 for standard SAXS comparison
- For SWAXS data, separate analysis in SAXS (q < 0.3) and WAXS (0.3 < q < 2.0) regions

---

#### Component 4: Back-Calculation Pipeline

##### 4.1 S2 Order Parameters from MD Trajectories

**Method: iRED (Isotropic Reorientational Eigenmode Dynamics)**

The iRED method (Prompers & Bruschweiler, JACS 2002) is the standard approach for computing S2 from MD trajectories, validated by Smith/Gowers et al. (2024). Implementation available in CPPTRAJ (Amber-MD/cpptraj on GitHub).

**Protocol:**
1. For each protein and each force field/MLFF, run N=20 independent replicas of 10-20 ns each
2. Start each replica from the minimized and equilibrated crystal structure with different random velocity seeds
3. Save coordinates every 1 ps (1000 frames per ns)
4. For each replica, compute the NH bond vector autocorrelation function C(t) = <P2(cos theta(0)) * P2(cos theta(t))>
5. Fit C(t) to the Lipari-Szabo model: C(t) = (1-S2)*exp(-t/tau_e) + S2
6. Alternatively, use iRED eigenvalue decomposition (CPPTRAJ `ired` command) for isotropic tumbling
7. Average S2 values across N=20 replicas; compute standard error of the mean

**Convergence criteria:**
- S2 mean across replicas must stabilize to within 0.02 units when adding additional replicas
- Compute ICC (intraclass correlation) across replicas; require ICC > 0.7 (evalstat recommendation)
- Report convergence diagnostic plots: S2 vs. number of replicas for 3 representative residues (rigid, intermediate, flexible)

**Window length requirements:**
- The iRED averaging window must be >=5x the overall tumbling correlation time (tau_c)
- For proteins in this set, tau_c ranges from ~4 ns (ubiquitin, 76 res, 298 K) to ~12 ns (T4 lysozyme, 164 res, 310 K)
- Minimum simulation length per replica: 20 ns (provides 5x coverage for tau_c ~4 ns) to 60 ns (for tau_c ~12 ns)
- Recommended: 20 ns per replica for small proteins (<=100 residues), 50 ns per replica for larger proteins (>100 residues)

**Methyl S2 axis:**
- For proteins with methyl S2 data (HEWL, barnase, RNase H): compute methyl CH3 axis order parameter S2_axis using iRED on C-CH3 bond vectors
- Apply methyl symmetry correction: S2_observed = S2_axis * P2(cos(109.5)) = S2_axis * 0.111

##### 4.2 Chemical Shift Back-Calculation

**Primary tool: SHIFTX2 (Han et al., J. Biomol. NMR 2011)**

- Highest accuracy for backbone nuclei:
  - 13Ca: RMSD 0.44 ppm, r = 0.9959
  - 13Cb: RMSD 0.52 ppm, r = 0.9992
  - 13C': RMSD 0.53 ppm
  - 15N: RMSD 1.12 ppm, r = 0.9800
  - 1HN: RMSD 0.17 ppm
  - 1Ha: RMSD 0.12 ppm
- MDTraj provides integrated SHIFTX2 access: `mdtraj.chemical_shifts_shiftx2(traj)`
- Compute per-frame chemical shifts for N=1000 trajectory snapshots (every 50 ps from a 50 ns trajectory)
- Report ensemble-averaged shift per residue

**Secondary tool: SPARTA+ (Shen & Bax, J. Biomol. NMR 2010)**

- Independent neural network predictor; accuracy:
  - 13Ca: RMSD 0.94 ppm
  - 13Cb: RMSD 1.14 ppm
  - 13C': RMSD 1.09 ppm
  - 15N: RMSD 2.45 ppm
  - 1HN: RMSD 0.49 ppm
  - 1Ha: RMSD 0.25 ppm
- Compute for same trajectory snapshots as SHIFTX2

**Side-chain chemical shifts: UCBShift 2.0 (Li et al., JACS 2024)**

- MAE 0.80 ppm for 13C, 0.16 ppm for 1H, 0.99 ppm for 15N side chains
- ~2x improvement over SHIFTX2 for side-chain predictions
- Apply to proteins with side-chain chemical shift data (ubiquitin, GB3, RNase H)

**Back-calculation uncertainty estimation:**
- The difference between SHIFTX2 and SPARTA+ predictions provides a lower bound on back-calculation systematic error
- If |SHIFTX2 - SPARTA+| > |MLFF - experiment| for a given nucleus at a given residue, that comparison is uninformative (back-calculation noise exceeds signal)
- Report the fraction of residues where back-calculation uncertainty is smaller than force field differences

**IDP chemical shifts: SPyCi-PDB (Wang et al., Bioinformatics 2024)**
- For alpha-synuclein and other IDPs in the stretch set
- SPyCi-PDB's `cs` module wraps UCBShift for ensemble-averaged CS from conformational ensembles
- Designed for IDP/IDR ensemble analysis; integrates with Monte Carlo/Bayesian reweighting

##### 4.3 J-Coupling Back-Calculation

**Method: Karplus Equation**

3JHNHa = A*cos2(phi - 60) + B*cos(phi - 60) + C

**Parametrization (Bax et al., JACS 2015):**
- A = 7.97 Hz
- B = -1.26 Hz
- C = 0.63 Hz
- Derived from high-accuracy measurements on GB3 and ubiquitin
- Intrinsic RMSD between Karplus-predicted and measured 3JHNHa for ideal structures: 0.53 Hz (this is the "floor" -- differences smaller than 0.53 Hz are not meaningful)

**Protocol:**
1. Extract backbone phi dihedral angles from each trajectory frame
2. Compute 3JHNHa per frame using Karplus equation with Bax 2015 parameters
3. Average 3JHNHa over all frames to get ensemble-averaged coupling
4. Report per-residue 3JHNHa and RMSD against experimental values

**Exclusions:**
- Glycine (different Karplus parametrization)
- Proline (no NH)
- Residues i+1 to proline (phi angle affected by proline ring)

**Additional J-couplings (where data available):**
- 3JHNHb, 3JHaCb, 3JC'C' can be back-calculated using their respective Karplus parametrizations
- For chignolin: use all 6 J-coupling types measured in BICePs study

##### 4.4 RDC Back-Calculation

**Applicable proteins:** GB3 (primary), ubiquitin (secondary), HEWL, BPTI, SH3 (limited)

**Method: SVD Alignment Tensor Fitting with PALES**

PALES (Prediction of ALignmEnt from Structure; Zweckstetter, Nature Protocols 2008) computes predicted RDCs from a 3D structure by:
1. Predicting the steric alignment tensor from the molecular shape (PALES simulation mode)
2. Best-fitting the alignment tensor to experimental RDCs using SVD (requires minimum 5 RDCs)

**Protocol for MD ensemble:**
1. Extract N=200-500 representative conformations from the trajectory (cluster centroids or evenly spaced)
2. For each conformation, fit the alignment tensor to experimental RDCs using PALES SVD
3. Back-calculate RDCs from the fitted alignment tensor
4. Compute per-frame Q-factor: Q = RMS(D_calc - D_exp) / RMS(D_exp)
5. Average Q-factor across ensemble; compare across force fields

**Q-factor interpretation:**
- Q < 0.2: excellent agreement
- 0.2 < Q < 0.4: good agreement (typical for well-refined structures)
- Q > 0.5: poor agreement
- Classical FFs achieve Q ~0.15-0.30 for ubiquitin and GB3

**GB3 special protocol (36 RDC sets):**
- For GB3's 36 RDC datasets in 5 media, compute Q-factor for each dataset
- Report distribution of Q-factors across datasets
- Use multi-medium RDC data to probe bond vector orientation more stringently
- Chi1 side-chain RDCs (from Chou et al., JACS 2015) probe side-chain conformational sampling

##### 4.5 SAXS Profile Back-Calculation

**Primary tool: Pepsi-SAXS 3.0 (Grudinin, Acta Crystallogr. D 2017)**
- Multipole expansion + coarse-grained hydration layer correction
- 7x faster than CRYSOL; comparable accuracy
- Suitable for high-throughput ensemble-averaged profile computation

**Secondary tool: FoXS 2.21.0 (Schneidman-Duhovny et al., NAR 2010)**
- Debye equation with adaptive multipoles
- Highest median accuracy (chi = 1.96 in 2013 benchmark)
- Independent method from Pepsi-SAXS for cross-validation

**Protocol:**
1. Extract N=500-1000 conformations evenly spaced from production trajectory
2. Compute I(q) for each conformation using Pepsi-SAXS
3. Average I(q) across conformations: I_ens(q) = (1/N) * sum(I_i(q))
4. Compare ensemble-averaged I_ens(q) to experimental I(q) using chi2:
   chi2 = (1/Nq) * sum[ (I_calc(q) - c*I_exp(q))2 / sigma(q)2 ]
   where c is the scaling factor (fit to minimize chi2)
5. Extract Rg from Guinier fit of I_ens(q)
6. Compute Kratky plot: I(q)*q2 vs q for qualitative folded/unfolded assessment
7. Repeat with FoXS as independent check; report spread

**Hydration shell treatment:**
- Pepsi-SAXS uses a density-based implicit hydration model (adjustable contrast of hydration layer)
- For publication figures, consider explicit-solvent SAXS computation using WAXSiS (Grishaev et al., J. Chem. Theory Comput. 2023) for HEWL (the only protein with full I(q) SASBDB data)

---

#### Component 5: Statistical Framework

##### 5.1 Per-Protein Scorecards

For each protein x each force field (3 MLFFs + 2 classical baselines = 5 methods), compute:

```
PROTEIN SCORECARD: [Protein Name] -- [Force Field]
=================================================
Observable           | Calc. Value | Exp. Value | Delta  | vs ff19SB | vs c36m  | Verdict
---------------------|-------------|------------|--------|-----------|----------|--------
S2 backbone R2       | 0.XX        | --         | --     | +/- X%    | +/- X%   | PASS/FAIL
S2 backbone RMSD     | 0.XX        | --         | --     | +/- X     | +/- X    | PASS/FAIL
S2 methyl R2 (if)    | 0.XX        | --         | --     | n/a       | n/a      | PASS/FAIL
CS 13Ca RMSD (ppm)   | X.XX        | --         | --     | --        | --       | INFO
CS 15N RMSD (ppm)    | X.XX        | --         | --     | --        | --       | INFO
3JHNHa RMSD (Hz)     | X.XX        | --         | X.XX   | +/- X     | +/- X    | PASS/FAIL
3JHNHa Pearson r     | 0.XX        | --         | --     | +/- X     | +/- X    | PASS/FAIL
RDC Q-factor (if)    | 0.XX        | --         | --     | +/- X     | +/- X    | PASS/FAIL
SAXS chi2 (if)       | X.XX        | --         | --     | +/- X     | +/- X    | PASS/FAIL
Rg deviation (%)     | X.X%        | --         | --     | +/- X%    | +/- X%   | PASS/FAIL
```

##### 5.2 Pass/Fail Threshold Calibration

Thresholds are calibrated against classical FF performance (Gowers et al. 2024, Lindorff-Larsen 2012):

| Observable | Classical FF Range | MLFF "Pass" | MLFF "Excellent" | Floor (back-calc. limit) |
|---|---|---|---|---|
| S2 backbone R2 | ff14SB: 0.62; c36m: 0.51 | >= 0.50 | >= 0.70 | N/A |
| S2 backbone RMSD | 0.12-0.14 | <= 0.15 | <= 0.10 | N/A |
| 3JHNHa RMSD (Hz) | 0.35-0.97 | <= 1.0 | <= 0.60 | 0.53 (Karplus floor) |
| 3JHNHa Pearson r | 0.85-0.95 | >= 0.85 | >= 0.93 | N/A |
| RDC Q-factor (NH) | 0.15-0.30 | <= 0.35 | <= 0.20 | N/A |
| SAXS chi2 (folded) | 1.5-5.0 | <= 5.0 | <= 2.0 | ~1.0 (experimental error) |
| Rg deviation (%) | 2-5% (folded) | <= 5% | <= 3% | ~1% (experimental error) |
| CS 13Ca RMSD (ppm) | -- | informational | informational | SHIFTX2: 0.44; SPARTA+: 0.94 |

**Key calibration principle:** An MLFF "passes" if it reaches the lower bound of classical FF performance. An MLFF is "excellent" if it matches or exceeds the best classical FF. This is deliberately conservative -- the purpose is to determine whether MLFFs are competitive with mature classical FFs for producing experimentally-verifiable dynamics, not to declare premature superiority.

##### 5.3 Multi-Observable Aggregate Scoring

**Normalized score per observable per protein:**

Score_obs = (MLFF_metric - worst_baseline) / (best_baseline - worst_baseline)

where baselines are ff19SB and CHARMM36m. Score interpretation:
- Score > 1.0: MLFF exceeds best classical FF
- Score = 1.0: MLFF matches best classical FF
- Score = 0.0: MLFF matches worst classical FF
- Score < 0.0: MLFF is worse than all classical FFs

**Aggregate per MLFF:**
- Mean normalized score across all observables and proteins (equally weighted)
- Median normalized score (robust to outliers)
- Win rate: fraction of protein-observable pairs where MLFF > both classical FFs

**Summary visualizations:**
1. Heatmap: proteins (rows) x observables (columns), colored by normalized score, one panel per MLFF
2. Radar/spider plot: per-protein profile across all observables for each MLFF
3. Ranking bar chart: MLFFs ranked by mean normalized score with bootstrap 95% CI

##### 5.4 Pairwise Statistical Comparison

**Within each observable, across proteins:**
1. Wilcoxon signed-rank test (non-parametric, paired, N=7 for MVP) for MLFF vs. classical FF
2. Friedman test across all 5 methods (3 MLFFs + 2 classical) with N=7 proteins
3. Post-hoc Nemenyi test for pairwise method comparisons
4. Effect size: rank-biserial correlation (r_rb)

**Multiple testing correction:**
- Bonferroni correction across K=5 pairwise MLFF comparisons per observable
- Benjamini-Hochberg FDR correction across all tests (5 methods x 6 observables x 7 proteins = 210 potential comparisons; reduced by only testing meaningful comparisons)

**Power analysis:**
- With N=7 proteins (MVP), Friedman test can detect large rank differences (CD ~2.71 for K=5 at alpha=0.05) but not subtle ones
- With N=15 proteins (full set), power increases to ~80% for moderate effects
- Report exact power achieved alongside each test result

##### 5.5 Uncertainty Propagation

**Sources of uncertainty in the comparison:**

1. **MD sampling uncertainty:** Quantified by bootstrap over N=20 replicas. Compute S2 (and J-couplings) for each replica independently; report mean +/- SEM.

2. **Back-calculation uncertainty:** Quantified by predictor disagreement.
   - Chemical shifts: |SHIFTX2 - SPARTA+| provides lower bound
   - J-couplings: Karplus equation floor of 0.53 Hz RMSD
   - SAXS: |Pepsi-SAXS - FoXS| provides spread estimate

3. **Experimental uncertainty:**
   - S2: typically ~0.02-0.05 (from Lipari-Szabo model fitting errors; often not deposited)
   - Chemical shifts: typically ~0.05-0.1 ppm for 13C (from inter-entry comparison where multiple BMRB entries exist)
   - J-couplings: typically ~0.1-0.3 Hz
   - RDCs: typically ~0.5-1.0 Hz
   - SAXS I(q): point-by-point sigma from SASBDB files

4. **Combined uncertainty:** sqrt(sigma_MD^2 + sigma_backcalc^2 + sigma_exp^2)
   Only declare a force field "significantly better" when the delta between force fields exceeds combined uncertainty.

---

#### Component 6: Per-Protein Data Quality Inventory

##### Quantified Data Availability for MVP Proteins

| Protein | S2 NH (n) | S2 CH3 (n) | CS Nuclei (total n) | 3JHNHa (n) | RDC NH (n) | SAXS I(q) | Total Data Points |
|---|---|---|---|---|---|---|---|
| Ubiquitin | 65-70 | ~20 | ~400+ | ~70 | ~325+ (5 sets) | Rg only | ~880+ |
| GB3 | 50-54 | 0 | ~280+ | ~50 | ~1,800+ (36 sets) | Rg only | ~2,180+ |
| HEWL | ~120 | ~60 | ~550+ | ~110 | ~120 | Yes (SASDUE4) | ~960+ |
| BPTI | ~55 | 0 | ~230+ | ~45 | ~90 | Rg only | ~420+ |
| Barnase | ~95 | ~40 | ~400+ | limited | limited | Rg only | ~535+ |
| T4 Lysozyme | ~150 | 0 | ~400+ | limited | limited | Rg only | ~550+ |
| Crambin | 0 | 0 | ~50 | 0 | 0 | None | ~50 |
| **TOTAL** | **~535-544** | **~120** | **~2,310+** | **~275+** | **~2,335+** | **1 full** | **~5,575+** |

**Data richness ranking:** GB3 > HEWL > Ubiquitin > Barnase > T4 Lysozyme > BPTI >> Crambin

**Critical finding:** GB3 has by far the richest RDC data (36 datasets); HEWL has the best combined NMR+SAXS; ubiquitin has the most balanced coverage across all observable types. Crambin has minimal NMR data and serves only as a structural stability test.

---

#### Component 7: Integration with Gamma Project

##### 8 Overlap Proteins: NMR + ProteinGym DMS

| Protein | NMR Observables Available | ProteinGym DMS Assay | Functional Readout | # Variants (approx.) | Integration Value |
|---|---|---|---|---|---|
| Ubiquitin | S2, CS, 3J, RDC, NOE | UBI4_YEAST (Roscoe 2013, Mavor 2016) | Yeast growth fitness | ~1,500-2,000 | **Highest** |
| GB1/GB3 | S2, CS, 3J, RDC (36 sets) | SPG1_STRSG (Olson 2014) | IgG binding | ~500-800 | **High** |
| T4 Lysozyme | S2, CS | LYSB_BPT4 (Klesmith 2015) | Thermostability | ~2,500+ | **High** |
| Barnase | S2(NH+CH3), CS | RNBR_BACAM (Stiffler 2015) | Catalytic activity | ~1,800+ | **High** |
| p53 (DBD) | S2, CS, dynamics | P53_HUMAN (Giacomelli 2018) | Transcription activity | ~8,200+ | **High** |
| HIV-1 Protease | S2, CS, flap dynamics | POL_HV1N5 (Boucher 2014) | Drug resistance | ~1,000+ | **Moderate** |
| alpha-Synuclein | CS, 3J, RDC, PRE, SAXS | SYUA_HUMAN | Aggregation propensity | ~1,000+ | **Moderate** |
| SNase | S2, CS, 3J | NUC_STAAU (Shortle) | Enzymatic activity | ~500+ | **Moderate** |

##### Integration Pipeline

The connection between Alpha-M (MLFF validation) and Gamma (dynamics-to-function) operates through these 8 proteins via a 3-step pipeline:

**Step 1 (Alpha-M):** For each overlap protein, compute the multi-observable scorecard for each MLFF. Identify which MLFF produces the most physically realistic dynamics (highest aggregate normalized score).

**Step 2 (Gamma):** For the same proteins, use BioEmu to generate wildtype conformational ensembles. Extract 20 dynamics features (RMSF, contact frequencies, SASA distributions, correlated motions, etc.). Correlate ensemble features with ProteinGym DMS fitness scores.

**Step 3 (Integration):** For the 8 overlap proteins, test whether the MLFF with the best S2 agreement (from Alpha-M) also produces ensemble features that predict DMS fitness more accurately (from Gamma). Compute the correlation between MLFF validation rank (Alpha-M scorecard) and Gamma prediction performance (Spearman rho on DMS).

**This creates the paper's central integrative claim:** "MLFFs that produce more physically realistic dynamics also generate ensembles that better predict biological function."

##### Ensemble Feature Handoff Specification

For each overlap protein, Alpha-M will deliver to Gamma:
1. Per-residue S2 values (backbone and methyl)
2. Per-residue RMSF (Ca and all-atom)
3. Per-residue contact frequency matrix (5 A cutoff)
4. Per-residue SASA mean and variance
5. Global Rg mean and variance
6. First 10 PCA modes (Ca coordinates)
7. Correlation matrix of backbone dihedral fluctuations

These features, computed from the best-validated MLFF trajectories, provide the input for Gamma's dynamics-to-function ML model.

---

### Data Requirements

| Data Source | Content | Access Method | Size (est.) |
|---|---|---|---|
| BMRB (bmrb.io) | S2, CS, J-couplings, RDCs | REST API + PyNMRSTAR | ~100 MB NMR-STAR files |
| SASBDB (sasbdb.org) | SAXS I(q) profiles | Direct download | ~10 MB |
| PDB (rcsb.org) | Crystal structures | REST API | ~10 MB |
| RefDB (refdb.wishartlab.com) | Re-referenced chemical shifts | Direct download | ~50 MB |
| ProteinGym (proteingym.org) | DMS fitness scores | GitHub download | ~500 MB |
| Published literature | Supplementary datasets | Manual extraction | Variable |

### Compute Requirements

The validation analysis pipeline itself is computationally lightweight (the expensive part is running the MLFF simulations, which is mlffeng's domain):

| Component | Compute | Time (est.) |
|---|---|---|
| SHIFTX2 back-calculation (7 proteins x 5 FFs x 1000 frames) | ~50 CPU-hours | 1-2 days |
| SPARTA+ back-calculation | ~100 CPU-hours | 2-3 days |
| iRED S2 calculation (CPPTRAJ) | ~200 CPU-hours | 2-3 days |
| Pepsi-SAXS forward modeling (HEWL) | ~20 CPU-hours | 4-6 hours |
| FoXS forward modeling (HEWL) | ~20 CPU-hours | 4-6 hours |
| PALES RDC back-calculation (GB3 + ubiquitin) | ~10 CPU-hours | 2-3 hours |
| Statistical analysis + visualization | ~10 CPU-hours | 1 day |
| **Total analysis pipeline** | **~410 CPU-hours** | **~1 week** |

### Implementation Timeline

| Phase | Duration | Deliverable |
|---|---|---|
| Phase 0: Data extraction | Weeks 1-2 | Standardized experimental data files for all 7 MVP proteins |
| Phase 1: Pipeline validation | Week 3 | Back-calculation pipeline tested on published classical FF trajectories (reproduce Gowers 2024 S2 results for ubiquitin as positive control) |
| Phase 2: MVP analysis | Weeks 4-8 | Scorecards for 7 proteins x 5 force fields (3 MLFFs + 2 baselines), concurrent with MLFF simulations |
| Phase 3: Stretch analysis | Weeks 8-12 | Expand to 15 proteins (pending compute availability) |
| Phase 4: Integration | Weeks 10-14 | Gamma overlap analysis for 8 integration proteins |
| Phase 5: Manuscript | Weeks 12-16 | Figures, tables, and validation sections for the Alpha-M paper |

---

## Impact Assessment

### Publication Strategy

**Target venue:** Nature Computational Science (combined Gamma + Alpha-M paper) or standalone in Nature Methods / JCTC

**Main claim:** "The first systematic benchmark of ML force fields against experimental protein observables reveals that [best MLFF] achieves classical force field-level accuracy for backbone dynamics while identifying specific failure modes in [observable X] for [MLFF Y]."

**Expected reviewer concerns:**
1. "Why only 7 proteins?" -- Addressed by calibration against Lindorff-Larsen (4 proteins), Smith/Gowers (6 proteins); our 7 MVP + 8 stretch exceeds all precedents.
2. "S2 convergence with MLFF timescales." -- Addressed by 20-replica protocol from Gowers et al. and explicit convergence diagnostics.
3. "Back-calculation accuracy confounds force field differences." -- Addressed by dual-predictor uncertainty estimation and reporting the back-calculation floor.
4. "Fair comparison across different MLFF engines." -- Addressed in coordination with mlffeng's standardized protocol (same thermostats, integrators where possible).
5. "Why not include more recent MLFFs?" -- Addressed by explicit inclusion criteria (OpenMM-ML compatible, stable >30 ns protein simulation, open-source).

**Comparison baselines:** AMBER ff19SB (Tian et al., JCTC 2020) and CHARMM36m (Huang et al., Nature Methods 2017) as the two most widely used classical protein force fields.

### Novelty Assessment

**Genuinely new:**
- First MLFF-vs-NMR multi-observable benchmark for proteins
- First application of the S2 convergence protocol (Gowers 2024) to MLFF trajectories
- First SAXS validation of MLFF protein ensembles using SASBDB consensus data
- First per-protein scorecard approach for ranking MLFFs across observables
- Combined Alpha-M + Gamma narrative linking MLFF accuracy to functional prediction

**Engineering of established methods:**
- Individual back-calculation tools (SHIFTX2, SPARTA+, PALES, Pepsi-SAXS) are well-established
- The Karplus equation and Lipari-Szabo model-free analysis are standard
- Statistical comparison frameworks (Friedman/Nemenyi) are textbook methods

### Broader Impact

This benchmark dataset and analysis protocol will become the community standard for evaluating future MLFFs in the biomolecular domain. Just as ImageNet transformed computer vision model evaluation, Alpha-M transforms MLFF evaluation by requiring comparison to experimental reality -- not just DFT energies. Every MLFF paper published after this will need to report its Alpha-M scorecard.

---

## Evaluation Plan

### Primary Metrics

1. **S2 R2 (backbone NH):** Per-protein and aggregate across MVP set
2. **3JHNHa RMSD (Hz):** Per-protein and aggregate
3. **RDC Q-factor (NH):** For GB3 (36 datasets) and ubiquitin (5+ datasets)
4. **SAXS chi2:** For HEWL (SASDUE4 consensus data)
5. **Normalized aggregate score:** Per-MLFF across all observables

### Baselines

1. AMBER ff19SB (Tian et al., JCTC 2020)
2. CHARMM36m (Huang et al., Nature Methods 2017)
3. Literature values from Lindorff-Larsen 2012 and Gowers 2024 (for validation of our pipeline)

### Ablation Studies

1. **Replica count:** Compute S2 with N=5, 10, 15, 20 replicas to demonstrate convergence
2. **Trajectory length:** Compare S2 from 10, 20, 50 ns per replica
3. **Back-calculator choice:** Report SHIFTX2 vs SPARTA+ for all CS comparisons
4. **SAXS method:** Report Pepsi-SAXS vs FoXS vs WAXSiS (for HEWL)
5. **Temperature sensitivity:** For HEWL and T4 lysozyme, test +/- 5 K from experimental T

### Validation Strategy

**Positive control:** Reproduce published classical FF results:
- Gowers et al. (2024) S2 for ubiquitin with ff14SB (should match R2 ~0.62)
- Lindorff-Larsen (2012) J-coupling and RDC metrics for GB3 and ubiquitin
- Raddi et al. (2025) BICePs scores for chignolin (if included in stretch set)

**Negative control:** If an MLFF crashes or produces physically unreasonable trajectories (RMSD > 5 A from crystal structure within first 1 ns), it receives a "FAIL" on all observables for that protein without requiring the full analysis pipeline.

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| BMRB data has referencing errors for some proteins | Medium | Medium | Use RefDB re-referenced data; manual inspection of outliers; inter-entry comparison for ubiquitin (12+ entries) |
| S2 experimental uncertainty > force field differences | Medium | High | Bootstrap CIs from 20 replicas; focus on proteins with multiple independent S2 studies; report combined uncertainty |
| SAXS data scarce for most MVP proteins | High | Medium | Only HEWL has SASBDB data; use Rg-only comparison for others; accept SAXS as supplementary not primary metric |
| Temperature mismatch: HEWL at pH 3.8/308K, T4L at 310K | Medium | Medium | Simulate at experimental conditions (mandatory); report temperature sensitivity ablation |
| Back-calculation tools fail on MLFF-generated geometries | Low-Medium | High | Test SHIFTX2 and SPARTA+ on short MLFF trajectory segments before full analysis; flag anomalous geometries |
| ProteinGym DMS constructs differ from NMR study constructs | Medium | Medium | Verify sequence alignment; report construct differences; use intersecting residues only |
| p53 Zn2+ coordination site: MLFFs may mishandle metal ions | High | Medium | Monitor Zn-Cys/His distances during simulation; if MLFF fails, exclude p53 from MLFF analysis (keep for BioEmu/Gamma only) |
| Small N (7 proteins MVP) limits statistical power | High | Medium | Pre-specify analyses; use non-parametric tests; expand to 15 proteins if compute allows |

---

## Open Questions

1. **Crambin data gap:** Crambin has essentially no NMR dynamics data beyond chemical shifts. Should it remain in the MVP set as a structural stability control, or be replaced by a protein with richer NMR data (e.g., chignolin or SH3)? Current recommendation: keep crambin for MLFF literature cross-referencing but do not include in multi-observable statistical analysis.

2. **Methyl S2 weighting:** Should methyl S2 be weighted equally with backbone NH S2 in the aggregate score? Methyl S2 is harder for classical FFs (R2 < 0.8 typically) and probes side-chain accuracy, which may be more discriminating. Recommendation: report backbone and methyl S2 separately; do not combine into a single S2 metric.

3. **IDP validation protocol:** For alpha-synuclein (stretch set), MLFF simulation of a 140-residue IDP in explicit water will require very long trajectories (>>100 ns) for conformational sampling. Should we use ensemble reweighting (Maximum Entropy or BioEn) to compare to experiment, or compare raw ensemble averages? Recommendation: start with raw ensemble averages; add reweighting as sensitivity analysis.

4. **RDC alignment tensor treatment:** Should we use a single best-fit alignment tensor per trajectory, or re-fit the tensor for each snapshot? The latter is more rigorous but computationally expensive for 36 GB3 datasets. Recommendation: fit per-snapshot for a subset (every 50th frame); compare to single-tensor result.

5. **Chemical shift reference frame:** Some older BMRB entries may use DSS vs TSP reference. Should we re-reference all entries to a common standard before comparison? Recommendation: yes, use RefDB-corrected entries wherever available; apply BaMORC correction otherwise.

---

## References

1. Lindorff-Larsen, K. et al. (2012). Systematic validation of protein force fields against experimental data. PLoS ONE, 7(2), e32131.

2. Robustelli, P., Piana, S. & Shaw, D.E. (2018). Developing a molecular dynamics force field for both folded and disordered protein states. Proc. Natl. Acad. Sci. USA, 115(21), E4758-E4766.

3. Gowers, S.A. et al. (2024). The accuracy and reproducibility of Lipari-Szabo order parameters from molecular dynamics. J. Phys. Chem. B, 128, 10090-10101.

4. Wang, S. et al. (2024). Ab initio characterization of protein molecular dynamics with AI2BMD. Nature, 636, 1012-1019.

5. Kovacs, D.P. et al. (2025). MACE-OFF: Short-range transferable machine learning force fields for organic molecules. J. Am. Chem. Soc., 147, 2977-2990.

6. Han, B. et al. (2011). SHIFTX2: significantly improved protein chemical shift prediction. J. Biomol. NMR, 50, 43-57.

7. Shen, Y. & Bax, A. (2010). SPARTA+: a modest improvement in empirical NMR chemical shift prediction by means of an artificial neural network. J. Biomol. NMR, 48, 13-22.

8. Li, J. et al. (2024). UCBShift 2.0: Bridging the gap from backbone to side chain protein chemical shift prediction for protein structures. J. Am. Chem. Soc., 146, 33989-34001.

9. Wang, Y. et al. (2024). SPyCi-PDB: A modular command-line interface for back-calculating experimental datatypes of protein structures. Bioinformatics, 40(5), btae199.

10. Bax, A. et al. (2015). High accuracy of Karplus equations for relating three-bond J couplings to protein backbone torsion angles. J. Am. Chem. Soc., 137, 1506-1514.

11. Zweckstetter, M. (2008). NMR: prediction of molecular alignment from structure using the PALES software. Nature Protocols, 3, 679-690.

12. Grudinin, S. et al. (2024). Benchmarking predictive methods for small-angle X-ray scattering from atomic coordinates of proteins using maximum likelihood consensus data. IUCrJ, 11(5), 834-847.

13. Schneidman-Duhovny, D. et al. (2010). FoXS: a web server for rapid computation and fitting of SAXS profiles. Nucleic Acids Res., 38(suppl_2), W540-W544.

14. Raddi, R.M. et al. (2025). Model selection using replica averaging with Bayesian inference of conformational populations. J. Chem. Theory Comput., 21(12), 5891-5903.

15. Tian, C. et al. (2020). ff19SB: Amino-acid-specific protein backbone parameters trained against quantum mechanics energy surfaces in solution. J. Chem. Theory Comput., 16, 528-552.

16. Huang, J. et al. (2017). CHARMM36m: an improved force field for folded and intrinsically disordered proteins. Nature Methods, 14, 71-73.

17. Zhang, H. et al. (2003). RefDB: a database of uniformly referenced protein chemical shifts. J. Biomol. NMR, 25, 173-195.

18. Showalter, S.A. & Bruschweiler, R. (2007). Quantitative molecular ensemble interpretation of NMR dipolar couplings without restraints. J. Am. Chem. Soc., 129, 4158-4159.

19. Nodet, G. et al. (2021). Refinement of alpha-synuclein ensembles against SAXS data: Comparison of force fields and methods. Front. Mol. Biosci., 8, 654333.

20. Fraser, J.S. et al. (2015). Mapping the conformational landscape of a dynamic enzyme by multitemperature and XFEL crystallography. eLife, 4, e07574.

21. Roscoe, B.P. et al. (2013). Analyses of the effects of all ubiquitin point mutants on yeast growth rate. J. Mol. Biol., 425, 1363-1377.

22. Giacomelli, A.O. et al. (2018). Mutational processes shape the landscape of TP53 mutations in human cancer. Nature Genetics, 50, 1381-1387.

23. Mavor, D. et al. (2016). Determination of ubiquitin fitness landscapes under different chemical stresses in a classroom setting. eLife, 5, e15802.

24. Cavender, C.E. et al. (2025). Structure-based experimental datasets for benchmarking protein simulation force fields. Living J. Comput. Mol. Sci., 6(1), 3871.

25. Hsu, C.H. et al. (2021). BaMORC: A software package for accurate and robust 13C reference correction of protein NMR spectra. J. Biomol. NMR, 75, 205-217.

26. Prompers, J.J. & Bruschweiler, R. (2002). General framework for studying the dynamics of folded and nonfolded proteins by NMR relaxation spectroscopy and MD simulation. J. Am. Chem. Soc., 124, 4522-4534.

27. Wang, A.C. & Bax, A. (1996). Determination of the backbone dihedral angles phi in human ubiquitin from reparametrized empirical Karplus equations. J. Am. Chem. Soc., 118, 2483-2494.

28. Chou, J.J. et al. (2015). Sidechain chi1 distribution in B3 domain of protein G from extensive sets of residual dipolar couplings. J. Am. Chem. Soc., 137, 14798-14811.
