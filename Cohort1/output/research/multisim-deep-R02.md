---
agent: multisim
round: 2
date: 2026-04-14
type: deep-dive
---

# Deep Dive: ML Force Field Biomolecular Validation Benchmark

## Executive Summary

Machine learning force fields (MLFFs) have entered a golden era with multiple universal platforms (AI2BMD, GEMS, SO3LR, MACE-OFF, UMA, LiTEN-FF) claiming near-quantum-mechanical accuracy for protein simulations. Yet a critical gap persists: **none of these MLFFs have been systematically benchmarked against the rich corpus of experimental biophysical observables (NMR chemical shifts, J-couplings, order parameters, RDCs, SAXS profiles, HDX-MS protection factors) that classical force fields were calibrated against over decades.** This deep dive confirms the gap is real, quantifies its dimensions, audits available data, estimates compute costs, and frames a publication strategy.

The gap is **verified and widening**: as of April 2026, at least 8 universal/transferable MLFFs are available for protein simulation, yet only AI2BMD has published any NMR comparison (limited to 3J-couplings on small peptides), and GEMS explicitly acknowledges that "to allow a quantitative comparison, structures should be modeled with GEMS instead of a conventional FF when interpreting the NMR results" -- admitting the comparison has not been done. A systematic "biomolecular crash test" benchmarking MLFFs against experimental observables would fill a critical need and is directly publishable in Nature Computational Science.

---

## 1. Gap Verification

### 1.1 Has Anyone Built This Benchmark?

**No.** After extensive searching of the literature through April 2026, no systematic benchmark comparing multiple MLFFs against experimental protein observables exists. Specific findings:

**What does exist:**
- **UniFFBench** (Mannan et al., arXiv 2508.05762, August 2025): Benchmarks 6 universal MLFFs against ~1,500 mineral structures using experimental crystal structures and elastic properties. This is for **materials science**, not biomolecules. Key finding: a "substantial reality gap" between computational benchmarks and experimental applicability.
- **CHIPS-FF** (2024-2025): Benchmarks 16 MLFFs on 104 materials for elastic constants, phonon spectra, defect energies. Again, **materials only**.
- **TEA Challenge 2023** (Chemical Science, 2025): Crash-tested MACE, SO3krates, sGDML, SOAP/GAP on alanine tetrapeptide, a heptapeptide, graphene surface, and perovskite. Compared to DFT, not experimental NMR/SAXS. Found kernel-based MLFFs could not sustain stable 1 ns dynamics for peptides.
- **Structure-Based Experimental Datasets for Benchmarking Protein Simulation Force Fields** (PMC12823150, 2025): A comprehensive review cataloging ~13 experimental NMR/crystallography datasets suitable for force field validation. Explicitly states these "could be used to benchmark the increasing number of machine learning models" but acknowledges this has not been done.
- **Folding@Home BICePs** (September 2025): Uses Bayesian inference to score 9 classical force fields against 158 NMR measurements on chignolin. Classical FFs only -- no MLFFs included.

**What AI2BMD published:**
- AI2BMD (Li et al., Nature, 2024): Compared 3J-couplings for small peptides (Ace-Ala-NMe, Ace-Gly-NMe) against NMR experiments. This is the **only** MLFF paper to directly compare against NMR observables, and it covered only J-couplings on dipeptides -- not chemical shifts, order parameters, RDCs, or SAXS on folded proteins (Li et al., 2024).

**What GEMS did NOT do:**
- GEMS (Unke et al., Science Advances, 2024): Compared crambin dynamics qualitatively to NMR-derived structural ensembles but did not compute NMR observables (J-couplings, chemical shifts, order parameters) from the simulations. The authors acknowledged this gap explicitly (Unke et al., 2024).

**What MACE-OFF did:**
- MACE-OFF (Kovacs et al., JACS, 2025): Computed 3J-coupling constants for Ala3 peptide, showing "close match" with experiment. Simulated crambin for 1.6 ns but only reported RMSF and power spectra, not NMR observables (Kovacs et al., 2025).

**What SO3LR did:**
- SO3LR (JACS, 2026): Simulated crambin (3 ns) and a glycoprotein (500 ps) but compared only power spectra and bulk properties (bilayer thickness, area per lipid). No NMR observable comparison (Frank et al., 2026).

### 1.2 The Analog from Materials Science

The UniFFBench study is instructive: when MLFFs were finally tested against experimental crystal structures instead of DFT-computed benchmarks, they found "models achieving impressive performance on computational benchmarks often fail when confronted with experimental complexity" (Mannan et al., 2025). The same "reality gap" almost certainly exists for biomolecular MLFFs, but nobody has measured it.

### 1.3 Verdict

**The gap is confirmed, large, and growing.** Every new MLFF validates on energy/force RMSE against DFT reference calculations. None systematically validate against the experimental observables that the biophysics community actually cares about. The classical force field community spent 30+ years building this validation infrastructure (Lindorff-Larsen et al., 2012; Best et al., 2012; Huang et al., 2017; Tian et al., 2020). The MLFF community has not yet engaged with it.

---

## 2. MLFF Landscape (Open-Source, Runnable, Protein-Ready)

### 2.1 Comprehensive MLFF Audit

| MLFF | Group | Year | Open-Source | Protein-Tested | OpenMM | Max System | Speed (protein) | H200 Compatible |
|------|-------|------|-------------|-----------------|--------|------------|-----------------|-----------------|
| AI2BMD | Microsoft | 2024 | Yes (GitHub) | Yes (10K+ atoms) | Custom | >10K atoms | ~hours/ns | Yes (CUDA) |
| GEMS | DeepMind/Unke | 2024 | Partial | Yes (25K atoms) | Custom | 25K atoms | ~500 ms/step (A100) | Yes |
| MACE-OFF23 | Cambridge | 2025 | Yes (GitHub) | Yes (crambin 18K) | Yes (OpenMM-ML) | ~20K atoms | 0.3M steps/day (A100, crambin) | Yes |
| SO3LR | Basel/Tuckerman | 2026 | Yes | Yes (crambin 25K) | JAX-MD | ~200K atoms | 2.6 ns/day (10K, H100) | Yes |
| UMA | Meta FAIR | 2026 | Yes | Materials focus | Likely via ASE | Large | Fast (MoLE arch) | Yes |
| LiTEN-FF | 2026 | Yes | Yes (chignolin) | Via ASE | ~1K atoms | 10x faster than MACE-OFF | Yes |
| ANI-2x | Roitberg | 2020 | Yes (TorchANI) | Limited | Yes (OpenMM-ML) | ~5K atoms | Fast for small | Yes |
| Allegro | Harvard | 2023 | Yes (GitHub) | Yes (DHFR 23K, Factor IX 91K) | Via LAMMPS | 91K atoms | Stable 3+ ns | Yes |
| NepoIP/MM | 2025 | Yes | Dipeptides only | Custom QM/MM | Small | Moderate | Likely |

### 2.2 OpenMM-ML Integration Status

OpenMM 8+ includes the `openmm-ml` plugin (GitHub: openmm/openmm-ml) supporting:
- **ANI-2x** via TorchANI or NNPOps (5.7x speedup with NNPOps)
- **MACE-OFF23** (S/M/L models) as of OpenMM-ML 1.2
- **AceFF** 1.0, 1.1, 2.0
- **MACE-MPA-0**, **MACE-OMAT-0** (S/M)
- Mixed ML/MM systems via `createMixedSystem()`

This is critical: **OpenMM-ML provides a unified interface** to run multiple MLFFs through the same simulation engine, enabling fair head-to-head comparisons.

### 2.3 Practical Assessment for Benchmarking

**Tier 1 -- Ready for systematic benchmarking (open-source, protein-tested, OpenMM or equivalent):**
- MACE-OFF23 (S/M/L)
- ANI-2x
- SO3LR
- LiTEN-FF

**Tier 2 -- Usable with moderate effort:**
- AI2BMD (custom framework but open-source)
- Allegro (via LAMMPS, not OpenMM)
- UMA (may need adaptation for proteins)

**Tier 3 -- Partial availability:**
- GEMS (not fully open-source simulation stack)
- NepoIP/MM (dipeptides only so far)

---

## 3. Experimental Validation Data Audit

### 3.1 NMR Data (BMRB)

The Biological Magnetic Resonance Bank (BMRB) contains:
- **~21,820 NMR entries** total (as of November 2025)
- **~11,900+ entries** with assigned 1H, 13C, 15N, 31P chemical shifts and coupling constants
- Chemical shift coverage: e.g., alanine H atoms: 112,584 shifts; leucine: 126,572 H shifts
- **RefDB**: 2,429 re-referenced protein chemical shift files with corrected referencing

**Key NMR observable types available:**
1. **Chemical shifts** (1H, 13C, 15N) -- most abundant, fast converging in MD
2. **Scalar J-couplings** (3JHNHa, 3JCaCO, etc.) -- sensitive to backbone dihedrals
3. **Residual Dipolar Couplings (RDCs)** -- sensitive to bond vector orientations relative to alignment tensor
4. **NOE-derived distances** -- short-range and tertiary contacts
5. **Lipari-Szabo S2 order parameters** -- backbone and sidechain dynamics on ps-ns timescale
6. **Spin relaxation rates** (T1, T2, hetNOE) -- dynamical information

### 3.2 Curated Benchmark Datasets (from PMC12823150 review)

The Structure-Based Experimental Datasets review catalogs ~13 ready-to-use benchmark datasets:

| Dataset | Type | # Proteins | Observables |
|---------|------|-----------|-------------|
| Beauchamp peptides | Short peptides | 31 | J-couplings, chemical shifts |
| Designed beta-hairpins/Trp-cage | Mini-proteins | 92 | J-couplings, NOEs |
| Stroet folded proteins | Folded | 13 | Multiple NMR observables |
| Mao folded proteins | Folded | 41 | J-couplings, RDCs |
| Robustelli a99SB-disp | Mixed folded/IDP | 21 | J-couplings, SAXS, PRE |
| Spin relaxation datasets | Dynamics | 136 | T1, T2, hetNOE, S2 |
| Salt bridge stabilities | Specific | 1 | Free energies |

**Recommended minimal benchmark** (from the review): at least one dataset each of peptides, folded proteins, and disordered proteins, using chemical shifts, J-couplings, and RDCs as priority observables.

### 3.3 SAXS Data (SASBDB)

The Small Angle Scattering Biological Data Bank contains:
- **5,272 experimental SAXS/SANS datasets** (as of March 2026)
- **6,486 models**
- Growth rate: ~32 entries/month since 2018-2019
- Covers proteins from small domains to large complexes
- Provides I(q) scattering profiles that directly probe the radius of gyration and overall shape

SAXS is particularly important for validating IDP ensembles, where chain dimensions are a critical test.

### 3.4 HDX-MS Data

HDX-MS data is less centralized:
- No single comprehensive database equivalent to BMRB/SASBDB
- HDX protection factors can be computed from MD trajectories
- Recent tools: HRaDeX (2025) achieves RMSE of 7.15% in normalized deuterium uptake reconstitution
- Recommendations from Masson et al. (Nature Methods, 2019) standardize reporting but not deposition
- **Estimated ~500-1000 published HDX-MS datasets** across literature, but extraction requires manual curation

### 3.5 Cross-Reference: Proteins with Both Structure AND Experimental Dynamics Data

The critical question is: how many proteins have high-quality PDB structures suitable for MD AND rich NMR dynamics data?

- **ATLAS database**: 1,390 protein chains with 3x100 ns MD each (CHARMM36m)
- **mdCATH**: 5,398 protein domains with 5 temperatures x 5 replicas (CHARMM22*)
- **BMRB spin relaxation**: 136 proteins with S2 order parameters
- **D.E. Shaw benchmark set**: 21 systems with >9,000 experimental data points

**Conservative estimate of overlap**: ~50-100 proteins have both high-resolution crystal structures AND quantitative NMR dynamics data (S2, J-couplings) AND are suitable sizes for MLFF simulation (< ~500 residues).

For a systematic benchmark, selecting **20-30 diverse proteins** spanning folded (alpha, beta, alpha/beta), IDPs, and mini-proteins would be sufficient and tractable.

---

## 4. Classical Force Field Baselines

### 4.1 The Bar MLFFs Must Beat

Classical force fields have been refined against experimental NMR observables for decades. Current state of the art:

**AMBER ff19SB** (Tian et al., JCTC, 2020):
- Amino-acid-specific backbone phi/psi parameters trained against 2D QM energy surfaces
- Validated with ~5 ms of MD simulations
- Improved residue-specific helical propensities and PDB Ramachandran agreement
- S2 order parameters: R2 = 0.62 overall (ranging 0.45-0.86 per protein) (Smith et al., 2024)

**CHARMM36m** (Huang et al., Nature Methods, 2017):
- Refined backbone CMAP potential
- Validated on 15 peptides + 20 proteins with >500 microseconds cumulative simulation
- J-coupling, chemical shift, and hydrodynamic radius agreement
- S2 order parameters: R2 = 0.51 overall (Smith et al., 2024)
- Pressure-dependent J-couplings for hydrogen bonds validated

**OPLS-AA/M** (Robertson et al., JCTC, 2015):
- J-coupling RMSD: 0.35 Hz (improved from 0.97 Hz for OPLS-AA)
- Validated on ubiquitin and GB3

**a99SB-disp** (Robustelli et al., PNAS, 2018):
- D.E. Shaw benchmark: 21 systems, >9,000 experimental data points
- Balanced for both folded proteins and IDPs
- SAXS radii of gyration + NMR J-couplings

**Recent refinements** (2025):
- amber ff03w-sc and amber ff99SBws-STQ' validated against SAXS and NMR for IDPs
- Both accurately reproduced chain dimensions and secondary structure propensities

### 4.2 Quantitative Benchmarks for MLFFs to Match

| Observable | Classical FF Accuracy | # Proteins Tested | Key Reference |
|-----------|----------------------|-------------------|---------------|
| 3JHNHa (Hz) | RMSD 0.35-0.97 Hz | 2-41 | Robertson 2015, Mao 2024 |
| Chemical shifts (ppm) | ~1-2 ppm for Calpha | 50+ | Lindorff-Larsen 2012 |
| S2 backbone | R2 = 0.51-0.62 | 6 | Smith et al. 2024 |
| S2 methyl | R2 < 0.8 | ~10 | Showalter & Bruschweiler 2007 |
| Rg (SAXS, Angstrom) | ~2-5% error for folded | 21 | Robustelli 2018 |
| Rg (SAXS, IDP) | 5-15% error | ~10 | Best 2014 |

### 4.3 Known Weaknesses of Classical FFs

These represent areas where MLFFs could potentially demonstrate superiority:
1. **Vibrational spectra**: GEMS showed classical FFs produce "smooth and largely featureless" THz IR spectra vs. experiment, while GEMS matched experimental features (Unke et al., 2024)
2. **Sidechain S2 order parameters**: Classical FFs consistently underperform (R2 < 0.8 for methyls)
3. **IDP radius of gyration**: Historical challenge requiring water model corrections
4. **Loop dynamics**: Systematically too rigid in most classical FFs
5. **Polarization effects**: Fixed-charge FFs miss polarization, which MLFFs trained on QM data implicitly capture

---

## 5. Compute Requirements

### 5.1 MLFF Simulation Speeds (Current Benchmarks)

| MLFF | System | GPU | Speed | Equivalent ns/day |
|------|--------|-----|-------|-------------------|
| MACE-OFF23(S) | Water 600 atoms | A100 80GB | 2.1M steps/day | 2.1 ns/day (1fs) |
| MACE-OFF23(M) | Water 600 atoms | A100 80GB | 1.1M steps/day | 1.1 ns/day |
| MACE-OFF23(L) | Water 600 atoms | A100 80GB | 0.28M steps/day | 0.28 ns/day |
| MACE-OFF23 | Crambin 18K atoms | A100 80GB | 0.3M steps/day | 0.3 ns/day |
| SO3LR | 10K atoms | H100 | -- | 2.6 ns/day |
| SO3LR | General | H100 | 3.25 us/atom/step | Varies |
| GEMS | 25K atoms | A100 | ~500 ms/step | ~0.17 ns/day |
| Classical (GROMACS) | Solvated protein | Single GPU | -- | 100-500 ns/day |

**Key insight**: MLFFs are approximately **40-1000x slower** than classical FFs on the same hardware. SO3LR explicitly reports being "about 40 times slower on a single GPU than GROMOS" (Frank et al., 2026). MACE-OFF on crambin achieves ~0.3 ns/day vs. ~100+ ns/day for classical GROMACS.

### 5.2 Minimum Simulation Requirements

For meaningful comparison to NMR observables:
- **J-couplings**: ~10-50 ns per system (fast convergence)
- **Chemical shifts**: ~10-50 ns per system
- **S2 order parameters**: ~50-100 ns per system, ideally 10-20 replicas of ~10 ns each (Smith et al., 2024)
- **RDCs**: ~10-50 ns per system
- **SAXS Rg**: ~50-100 ns for folded proteins; ~200-500 ns for IDPs
- **HDX protection factors**: ~100+ ns

### 5.3 Benchmark Scope and Compute Budget

**Proposed benchmark scope:**
- 25 proteins (10 folded, 5 IDPs, 5 mini-proteins/peptides, 5 complexes)
- 6 MLFFs (MACE-OFF S/M/L, SO3LR, AI2BMD, LiTEN-FF)
- 3 classical baselines (AMBER ff19SB, CHARMM36m, a99SB-disp)
- Target: 100 ns per system per force field (with 5 replicas of 20 ns for S2)

**Compute estimate per system per MLFF:**

Assumptions: average solvated system ~15,000 atoms, MACE-OFF(M)-like speed ~0.5 ns/day on one H200 GPU.

- 100 ns simulation = 200 GPU-days = **4,800 GPU-hours** per system per MLFF

**Total MLFF compute:**
- 25 proteins x 6 MLFFs x 4,800 GPU-hours = **720,000 GPU-hours**

**Classical baseline compute:**
- 25 proteins x 3 FFs x 100 ns at ~200 ns/day = ~38 GPU-days = **~900 GPU-hours** total (trivial)

**Analysis compute:**
- NMR observable calculation (SHIFTX2, Karplus equations, CRYSOL for SAXS): ~10,000 CPU-hours
- Data processing, statistical analysis: ~5,000 CPU-hours

**Grand total: ~730,000 GPU-hours + 15,000 CPU-hours**

### 5.4 Feasibility with Available Resources

With H200 nodes (8 GPUs each):
- 730,000 GPU-hours / 8 GPUs per node = 91,250 node-hours
- At 100% utilization with 10 nodes dedicated: ~380 days (too long)
- At 100% utilization with 50 nodes: ~76 days (~2.5 months)
- **With aggressive parallelization (25 proteins x 6 MLFFs = 150 independent jobs on 150 GPUs)**: ~4,800 hours = **200 days per GPU = ~6.7 months on 150 GPUs**

**Feasibility strategies:**
1. **Reduce to 50 ns per system** (sufficient for J-couplings and chemical shifts): halves compute to ~365,000 GPU-hours
2. **Focus on Tier 1 MLFFs only** (MACE-OFF M, SO3LR, LiTEN-FF = 3 MLFFs): reduces to ~360,000 GPU-hours
3. **Reduce to 15 proteins**: ~216,000 GPU-hours for 3 MLFFs = achievable in ~3 months on ~100 GPUs
4. **Use faster MLFFs where possible**: LiTEN-FF claims 10x faster than MACE-OFF for ~1K atom systems

**Minimum viable benchmark**: 15 proteins x 3 MLFFs x 50 ns = ~180,000-270,000 GPU-hours. **Feasible in 2-3 months on available HPC.**

---

## 6. Competition Assessment

### 6.1 Who Could Build This?

**D.E. Shaw Research:**
- Built the definitive classical FF benchmark (21 proteins, 9,000+ data points) for a99SB-disp (Robustelli et al., 2018)
- Could certainly extend to MLFFs, but their focus appears to be on classical FF refinement and long-timescale sampling, not MLFF validation
- Recent work on reversible simulation for FF training (PNAS 2025) is adjacent but different

**Microsoft Research (AI2BMD team):**
- Already showed 3J-coupling comparison in AI2BMD paper
- Could extend, but their incentive is to validate their own model, not provide a fair multi-model benchmark
- Partial conflict of interest for a neutral benchmark

**DeepMind/Google (GEMS team):**
- Explicitly deferred NMR comparison in their Science Advances paper
- Focus appears to have shifted to other projects
- Same conflict of interest concern

**Cambridge (MACE team):**
- Active development of MACE-OFF with OpenMM integration
- Good position to extend, but focus is architecture development, not benchmarking
- Published Ala3 J-coupling but not systematic protein benchmarks

**Folding@Home (Voelz lab):**
- BICePs framework is ideal for scoring force fields against experiment
- Currently focused on classical FFs (9 tested in 2025 blog)
- Natural extension to MLFFs, but would need compute for MLFF simulations

**Meta FAIR (UMA team):**
- UMA trained on 30 billion atoms across multiple datasets
- Focus is materials science / catalysis, not biomolecular validation

### 6.2 Risk of Being Scooped

**Medium risk, but timing is favorable.** Several converging factors create urgency:
- The Structure-Based Experimental Datasets review (2025) explicitly calls for ML models to be benchmarked against its curated datasets
- The UniFFBench "reality gap" finding for materials MLFFs creates narrative pressure to check biomolecular MLFFs
- The TEA Challenge showed crash-testing is a publishable and impactful format
- Multiple MLFF teams are expanding protein coverage (LiTEN-FF in Nature Communications 2026)

**However:**
- No preprint or conference abstract currently announces this benchmark
- The compute cost (hundreds of thousands of GPU-hours) is a significant barrier
- The expertise to do it right (NMR observable calculation, proper convergence assessment, statistical analysis) is non-trivial
- This is a **benchmark paper**, not a methods paper -- it requires different skills (careful experimentation, fair comparison, statistical rigor) that MLFF developers may not prioritize

**Window of opportunity: 6-12 months** before someone inevitably does this. The first comprehensive, fair, multi-MLFF biomolecular benchmark paper will be highly cited.

### 6.3 Differentiation Strategy

Our benchmark would be differentiated by:
1. **Breadth**: 3+ MLFFs + 3 classical baselines, not just testing one model
2. **Experimental grounding**: Direct comparison to NMR/SAXS, not just DFT
3. **Diverse proteins**: Folded, disordered, mini-proteins -- not just alanine peptides
4. **Practical focus**: "Which MLFF should a biophysicist use in 2026?" not "which has lowest force RMSE"
5. **Reproducibility**: All simulations through OpenMM-ML or equivalent open-source stacks
6. **Statistical rigor**: Proper convergence assessment, bootstrapped confidence intervals, multiple replicas

---

## 7. Feasibility Reassessment

### 7.1 Technical Feasibility

| Component | Status | Risk |
|-----------|--------|------|
| MLFF software availability | 3-4 models ready via OpenMM-ML | Low |
| NMR data availability | BMRB + curated datasets readily available | Low |
| SAXS data availability | SASBDB 5,272 datasets | Low |
| NMR observable calculators | SHIFTX2, SPARTA+, Karplus equations well-established | Low |
| SAXS profile calculators | CRYSOL, FoXS well-established | Low |
| MD setup/analysis pipeline | MDAnalysis, MDTraj, OpenMM mature | Low |
| MLFF stability for 50-100 ns | TEA Challenge showed instabilities possible | Medium |
| Convergence in MLFF timescales | S2 needs 10-20 replicas; SAXS needs long sampling | Medium |
| H200 GPU compatibility | All major frameworks support CUDA | Low |

**Rating: HIGH** -- All components exist; the challenge is integration and scale.

### 7.2 Timeline Feasibility

| Phase | Duration | Activity |
|-------|----------|----------|
| Month 1 | 4 weeks | Curate protein set, prepare inputs, test MLFF stability |
| Month 2-3 | 8 weeks | Production simulations (150+ parallel GPU jobs) |
| Month 3-4 | 4 weeks | Analysis: compute NMR/SAXS observables, statistical tests |
| Month 4-5 | 4 weeks | Figures, tables, manuscript writing |

**Total: ~5 months.** Tight but feasible for summer 2026 if launched immediately.

**Rating: MEDIUM** -- feasible but requires immediate start and aggressive parallelization.

### 7.3 Wet Lab Independence

**Rating: HIGH** -- completely computational. All experimental data comes from published databases (BMRB, SASBDB, literature). No new experiments needed.

### 7.4 Key Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| MLFF simulations crash before 50 ns | Medium | High | Report instabilities as findings; use shorter trajectories where needed |
| Insufficient convergence for S2 | Medium | Medium | Focus on J-couplings/chemical shifts which converge faster |
| Compute budget exceeded | Low | Medium | Reduce to 15 proteins, 3 MLFFs |
| Scooped by MLFF developers | Low-Medium | High | Move fast; focus on breadth (multi-model) they cannot easily replicate |
| NMR observable calculators inaccurate for MLFF geometries | Low | Medium | Use multiple calculators, report uncertainty |

---

## 8. Publication Framing

### 8.1 Target Venue

**Primary: Nature Computational Science**
- Precedent: Lindorff-Larsen et al. (2012) "Are Protein Force Fields Getting Better?" in JCTC has >2,000 citations. A Nature Comp Sci version for the MLFF era would be transformative.
- Fits the "new way of thinking" criterion: forces the MLFF community to adopt experimental validation standards.

**Secondary: Nature Methods** (if framed as a benchmarking methodology/platform) or **JACS** (if MLFF chemistry focus)

### 8.2 Proposed Title

**"The Reality Gap: Systematic Evaluation of Machine Learning Force Fields Against Experimental Protein Observables"**

Alternative: "Crash Testing Machine Learning Force Fields for Biomolecular Simulation: A Systematic Benchmark Against NMR and SAXS"

### 8.3 Main Claim

"We present the first systematic benchmark of universal machine learning force fields against experimental protein observables, revealing a substantial reality gap between computational accuracy metrics and biophysical agreement. While MLFFs achieve impressive energy/force accuracy relative to quantum mechanics, their agreement with NMR chemical shifts, J-couplings, order parameters, and SAXS profiles is highly variable and does not consistently surpass decades-old classical force fields -- except in specific domains (vibrational spectra, conformational flexibility) where QM accuracy provides genuine advantages."

### 8.4 Expected Key Figures

1. **Figure 1**: Overview schematic -- MLFF validation pipeline (structure to MD to NMR/SAXS observables to experiment comparison)
2. **Figure 2**: Head-to-head comparison of J-coupling RMSD across all MLFFs and classical baselines for peptides and folded proteins
3. **Figure 3**: Chemical shift agreement (Calpha, Cbeta, HN) for all force fields across 25 proteins -- heatmap
4. **Figure 4**: S2 order parameter correlation plots -- classical vs. MLFF vs. experiment (one panel per protein)
5. **Figure 5**: SAXS profile chi-squared for IDPs and folded proteins
6. **Figure 6**: "Reality gap" summary -- MLFF force RMSE rank vs. experimental observable rank (are they correlated?)
7. **Figure 7**: Cost-accuracy Pareto frontier -- ns/GPU-hour vs. NMR agreement for each force field
8. **Supplementary**: Individual protein analyses, convergence assessment, stability analysis

### 8.5 What Reviewers Would Attack

1. **"Insufficient sampling"** -- MLFFs are slow, so 50-100 ns may not converge for some observables
   - *Mitigation*: Explicit convergence analysis (block averaging), focus on fast-converging observables, report convergence status per system
2. **"Unfair comparison -- MLFFs weren't trained on this data"** -- Classical FFs were calibrated against NMR
   - *Mitigation*: This IS the point. The question is whether QM-level accuracy transfers to experimental agreement. Explicitly discuss this distinction.
3. **"Missing state-of-the-art MLFFs"** -- Field moves fast
   - *Mitigation*: Include most recent available models; provide code/pipeline for easy extension
4. **"NMR back-calculators are approximate"** -- Karplus equation has ~0.5-1 Hz error
   - *Mitigation*: Use multiple back-calculators; quantify prediction uncertainty; same calculators for all FFs

### 8.6 Comparison Baselines Required

**Minimum viable baselines:**
- AMBER ff19SB (current state-of-the-art AMBER)
- CHARMM36m (current state-of-the-art CHARMM)
- a99SB-disp (D.E. Shaw optimized for folded + IDP balance)

**Desirable additional baselines:**
- OPLS-AA/M
- DES-Amber (D.E. Shaw variant)

---

## 9. Connection to Dynamics-to-Function Theme

### 9.1 Bridging the Gap Between MLFFs and Biological Insight

This benchmark directly connects to protdyn's identified gap around dynamics-to-function mapping. The chain of reasoning:

1. **MLFFs promise more accurate dynamics** -- If they capture QM-level physics, protein motions should be more realistic than classical FFs
2. **But nobody has verified this** -- Without experimental validation of dynamics (S2 order parameters, relaxation rates), we don't know if MLFF dynamics are actually better
3. **If MLFFs produce better dynamics**, they could unlock the dynamics-to-function connection that classical FFs have struggled with
4. **If MLFFs produce worse dynamics** (e.g., due to training data gaps or instabilities), the field needs to know before investing computational resources

### 9.2 Specific Connections

- **Conformational ensembles**: GEMS showed "substantially more flexible" crambin dynamics than classical FFs. Is this flexibility real (matching NMR S2) or an artifact?
- **Helix-coil equilibria**: MACE-OFF showed alpha/310 helix oscillation in Ala15. Do the populations match NMR chemical shifts?
- **IDP dimensions**: MLFFs trained on QM data may handle solvent-solute interactions differently. Do SAXS-derived Rg values improve?
- **Allosteric pathways**: If MLFF dynamics are more physically accurate, they could reveal allosteric communication pathways missed by classical simulations
- **Protein folding**: AI2BMD demonstrated folding/unfolding. Do the folded state dynamics match NMR?

### 9.3 Enabling Future Dynamics Research

A validated MLFF benchmark would:
1. **Identify which MLFF to trust for dynamics studies** -- essential for any proteome-scale dynamics effort
2. **Reveal which experimental observables are most discriminating** -- guiding future MLFF training
3. **Establish the MLFF accuracy frontier** -- setting expectations for what's achievable computationally vs. what requires experimental validation
4. **Create a reusable benchmark pipeline** -- as new MLFFs appear, they can be immediately tested

---

## 10. Revised Impact Score

| Criterion | Score (1-10) | Justification |
|-----------|-------------|---------------|
| Novelty | 9 | First systematic multi-MLFF biomolecular benchmark against experiment. UniFFBench analog for biology. |
| Scientific impact | 9 | Would reshape how MLFFs are developed, validated, and adopted for biomolecular simulation. |
| Computational feasibility | 8 | All tools exist; challenge is scale. 180K-730K GPU-hours is significant but within reach. |
| Timeline (summer 2026) | 7 | Tight at 5 months. Requires immediate start and compute allocation. |
| Publication potential (Nat Comp Sci) | 9 | Perfect fit: new benchmark methodology, broad community interest, paradigm-shifting framing. |
| Wet lab independence | 10 | Entirely computational; uses published experimental data. |
| **Overall** | **8.7** | **Strongest gap identified in Round 1. High impact, feasible, timely.** |

---

## References

1. Li, T., et al. "Ab initio characterization of protein molecular dynamics with AI2BMD." *Nature* 636, 624-630 (2024). DOI: 10.1038/s41586-024-08127-z

2. Unke, O.T., et al. "Biomolecular dynamics with machine-learned quantum-mechanical force fields trained on diverse chemical fragments." *Science Advances* 10, eadn4397 (2024). DOI: 10.1126/sciadv.adn4397

3. Kovacs, D.P., et al. "MACE-OFF: Short-Range Transferable Machine Learning Force Fields for Organic Molecules." *JACS* (2025). DOI: 10.1021/jacs.4c07099

4. Frank, J.T., et al. "Molecular Simulations with a Pretrained Neural Network and Universal Pairwise Force Fields." *JACS* (2026). DOI: 10.1021/jacs.5c09558

5. Mannan, S., et al. "Evaluating Universal Machine Learning Force Fields Against Experimental Measurements." *arXiv* 2508.05762 (2025).

6. Yang, Z., et al. "CHIPS-FF: Evaluating Universal Machine Learning Force Fields for Material Properties." *ACS Materials Letters* (2025). DOI: 10.1021/acsmaterialslett.5c00093

7. "Structure-Based Experimental Datasets for Benchmarking Protein Simulation Force Fields [Article v1.0]." *PMC* 12823150 (2025).

8. Tian, C., et al. "ff19SB: Amino-Acid-Specific Protein Backbone Parameters Trained against Quantum Mechanics Energy Surfaces in Solution." *JCTC* 16, 528-552 (2020). DOI: 10.1021/acs.jctc.9b00591

9. Huang, J., et al. "CHARMM36m: An Improved Force Field for Folded and Intrinsically Disordered Proteins." *Nature Methods* 14, 71-73 (2017).

10. Robustelli, P., Piana, S., Shaw, D.E. "Developing a molecular dynamics force field for both folded and disordered protein states." *PNAS* 115, E4758-E4766 (2018).

11. Lindorff-Larsen, K., et al. "Systematic Validation of Protein Force Fields against Experimental Data." *PLOS ONE* 7, e32131 (2012).

12. Smith, L.J., et al. "The Accuracy and Reproducibility of Lipari-Szabo Order Parameters From Molecular Dynamics." *J. Phys. Chem. B* (2024). DOI: 10.1021/acs.jpcb.4c04895

13. Showalter, S.A. & Bruschweiler, R. "Quantitative Molecular Ensemble Interpretation of NMR Dipolar Couplings without Restraints." *JACS* (2007).

14. Robertson, M.J., et al. "Improved Peptide and Protein Torsional Energetics with the OPLS-AA Force Field." *JCTC* 11, 3499-3509 (2015). DOI: 10.1021/acs.jctc.5b00356

15. Musaelian, A., et al. "Learning local equivariant representations for large-scale atomistic dynamics." *Nature Communications* 14, 579 (2023).

16. Batatia, I., et al. "MACE: Higher Order Equivariant Message Passing Neural Networks for Fast and Accurate Force Fields." *arXiv* 2206.07697 (2022).

17. Zheng, L., et al. "UMA: A Family of Universal Models for Atoms." *arXiv* 2506.23971 (2025/2026).

18. "A scalable and quantum-accurate foundation model for biomolecular force fields via linearly tensorized quadrangle attention." *Nature Communications* (2026). DOI: 10.1038/s41467-026-70377-4

19. Vander Meersche, Y., et al. "ATLAS: protein flexibility description from atomistic molecular dynamics simulations." *Nucleic Acids Research* 52, D384-D392 (2024).

20. Durumeric, A.E.P., et al. "mdCATH: A Large-Scale MD Dataset for Data-Driven Computational Biophysics." *Scientific Data* 11, 1287 (2024).

21. Kofinger, J., et al. "Crash testing machine learning force fields for molecules, materials, and interfaces: molecular dynamics in the TEA challenge 2023." *Chemical Science* (2025). DOI: 10.1039/D4SC06530A

22. Thaler, S. & Bhowmik, D. "Reversible molecular simulation for training classical and machine-learning force fields." *PNAS* (2025). DOI: 10.1073/pnas.2426058122

23. Voelz, V., et al. "Quantifying the accuracy of protein simulation models." *Folding@Home Blog* (September 2025).

24. Eastman, P., et al. "OpenMM 8: Molecular Dynamics Simulation with Machine Learning Potentials." *J. Phys. Chem. B* 128, 109-116 (2024).

25. "OpenMM-ML: High level API for using machine learning models in OpenMM simulations." GitHub: openmm/openmm-ml (2024-2026).

26. Best, R.B. "Computational and theoretical advances in studies of intrinsically disordered proteins." *Current Opinion in Structural Biology* 42, 147-154 (2017).

27. Masson, G.R., et al. "Recommendations for performing, interpreting and reporting hydrogen deuterium exchange mass spectrometry (HDX-MS) experiments." *Nature Methods* 16, 595-602 (2019).

28. Chen, J., et al. "NepoIP/MM: Toward Accurate Biomolecular Simulation with a Machine Learning/Molecular Mechanics Model Incorporating Polarization Effects." *JCTC* (2025). DOI: 10.1021/acs.jctc.5c00372

29. Dill, K.A. & MacCallum, J.L. "The protein-folding problem, 50 years on." *Science* 338, 1042-1046 (2012).

30. "Recent advances in artificial intelligence-driven biomolecular dynamics simulations based on machine learning force fields." *Current Opinion in Structural Biology* (2025). DOI: 10.1016/j.sbi.2025.102925
