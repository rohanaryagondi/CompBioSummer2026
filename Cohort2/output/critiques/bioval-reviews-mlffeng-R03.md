---
agent: bioval
round: 3
date: 2026-04-14
type: critique
proposal_reviewed: alpha-m-simulation
---

# Critique: Alpha-M -- The MLFF Biomolecular Crash Test

## Reviewing Agent

**Biophysical Validation & Experimental Data Expert (bioval)** -- 20+ years in NMR
spectroscopy, SAXS, and computational biophysics. I review this proposal from the
DATA QUALITY perspective: will the simulation protocol produce observables that are
genuinely and fairly comparable to experiment? Are back-calculation choices
appropriate? Are the statistical pass/fail criteria defensible? My critique is
grounded in decades of hard-won experience with the messy realities of matching
computed trajectories to experimental NMR measurements.

## Proposal Summary

mlffeng proposes a systematic benchmark of 3 MLFFs (MACE-OFF24(M), SO3LR, AI2BMD)
plus 2 classical baselines (AMBER ff19SB, CHARMM36m) and BioEmu, evaluated against
experimental NMR observables (S2 order parameters, J-couplings, chemical shifts) and
SAXS profiles across 7 proteins, using 50 ns NVT production runs at 300 K with 1 fs
timestep and 10 replicas x 10 ns for S2 convergence.

---

## Overall Assessment

**Verdict:** Support with Modifications

**One-line take:** A well-engineered simulation protocol with the right MLFF
selection and clear execution plan, but several data-quality issues -- temperature
matching, S2 convergence margins, ensemble choice, and Karplus parametrization --
must be corrected before this benchmark can withstand rigorous peer review at Nature
Computational Science.

---

## Strengths

1. **Excellent MLFF selection and justification:** The choice of MACE-OFF24(M),
   SO3LR, and AI2BMD is well-motivated. These three span distinct architectures
   (equivariant message passing, neural network + universal pairwise, fragmentation +
   ViSNet), distinct simulation engines (OpenMM-ML, JAX-MD, custom), and distinct
   training philosophies. The explicit disqualification of ANI-2x (amorphous ice;
   Waibl et al., JCIM 2025), LiTEN-FF (immature), and GEMS (partially closed) is
   rigorous and transparent. This breadth is the study's scientific moat.

2. **Standardized system preparation pipeline:** The single-PDB-to-all-methods
   pipeline via PDBFixer is exactly right for a fair comparison. Starting every method
   from identical coordinates, identical solvation, and identical ion placement
   eliminates preparation-induced variance. The explicit handling of ML water vs TIP3P
   as a feature (not a confound) is scientifically astute -- reporting the g(r) O-O
   water quality check is a nice diagnostic.

3. **Comprehensive kill criteria and stability monitoring:** The layered stability
   checks (RMSD thresholds, energy drift monitoring, force cutoffs, temperature
   guardrails) reflect genuine simulation engineering experience. The 1 ns Phase 1
   screening for all 21 MLFF-protein combinations before committing to production is
   prudent risk management.

4. **BioEmu inclusion as non-MD comparator:** Including BioEmu at trivial compute
   cost (~200 GPU-hrs) is strategically brilliant. Whether BioEmu ensembles match
   experiment better or worse than MLFF trajectories, the finding is publishable and
   directly bridges to the Gamma project narrative. This is one of the most elegant
   design decisions in the proposal.

5. **Classical baseline at 1 fs for fairness:** Running classical baselines at 1 fs
   without SHAKE -- matching the MLFF integrator exactly -- is the scientifically
   cleaner comparison. The plan to also report standard 2 fs + SHAKE results in
   Supplementary provides the community the numbers they expect while maintaining
   protocol integrity.

6. **Ablation study design:** The trajectory-length convergence analysis (10, 20, 30,
   40, 50 ns checkpoints) and replica-count dependence (N = 3, 5, 7, 10) are
   excellent. These ablations directly test whether conclusions depend on protocol
   choices, pre-empting a major reviewer concern.

## Weaknesses

1. **Critical: Temperature mismatch at blanket 300 K**
   The proposal specifies 300 K for all production simulations. This is incorrect for
   at least 3 of the 7 MVP proteins:

   - **HEWL:** NMR S2, chemical shifts, and J-couplings were measured at **308 K, pH
     3.8** (Lindorff-Larsen et al., 2012; my own bioval proposal documents this). My
     own proposal explicitly flags this: "Simulate at 308 K to match NMR data."
   - **BPTI:** Key NMR relaxation data collected at **308 K, pH 4.6** (Lindorff-Larsen
     et al., 2012).
   - **T4 Lysozyme:** NMR data collected at **310 K, pH 5.5** (Smith et al., 2024).

   Running these at 300 K introduces a systematic 8-10 K temperature error. S2 order
   parameters are temperature-sensitive: backbone NH S2 decreases by approximately
   0.01-0.02 per 10 K increase due to increased librational motion (Palmer, Chem Rev
   2004). A 10 K mismatch could shift S2 values by an amount comparable to the
   differences between force fields (AMBER ff14SB R2 = 0.62 vs CHARMM36m R2 = 0.51).
   Chemical shifts are less temperature-sensitive but still affected, particularly
   amide 1HN shifts which have a well-known temperature coefficient of approximately
   -4.6 ppb/K (Baxter & Williamson, J Biomol NMR 1997). J-couplings are modestly
   temperature-dependent through Boltzmann-weighted phi angle populations.

   The Brini/Cavender et al. (2025) benchmark review in Living J. Comp. Mol. Sci.
   explicitly warns: "NMR studies are often conducted at moderately low pH (around pH
   6) ... it is essential to assign pH-appropriate protonation states of titratable
   residues." The proposal's blanket pH 7.0 protonation via PDBFixer compounds the
   temperature problem for HEWL (pH 3.8) and BPTI (pH 4.6).

   - **Severity:** Critical
   - **Addressable?** Yes. Simulate each protein at its experimental NMR temperature
     and assign protonation states at the experimental pH using PropKa 3.5 or H++
     server, not PDBFixer's default pH 7.0. For HEWL at pH 3.8, Glu35 and Asp52
     protonation states must be explicitly verified. For BPTI at pH 4.6, all Asp
     residues should be checked. This is standard practice in the classical FF
     benchmark literature (Lindorff-Larsen 2012, Robustelli 2018) and is non-negotiable
     for a study claiming to benchmark against experiment.

2. **Major: S2 convergence at 10 replicas x 10 ns is below recommended minimum**
   The proposal specifies 10 replicas x 10 ns for S2, acknowledging this is a
   "practical compromise" relative to the N = 20 gold standard. Smith et al. (J. Phys.
   Chem. B 2024) found that N = 10 gives R2 reproducibility of approximately 0.90,
   while N = 20 achieves R2 >= 0.95. This 5% gap in reproducibility is a substantial
   fraction of the expected difference between MLFF and classical force field
   performance.

   More concerning: 10 ns per replica is short for the larger proteins. Smith et al.
   used 30 ns per replica. My own proposal specifies that the iRED averaging window
   must be at least 5x the overall tumbling correlation time (tau_c). For T4 lysozyme
   (164 residues, 310 K), tau_c is approximately 10-12 ns (Mandel et al., J Mol Biol
   1995), requiring a minimum simulation length of 50-60 ns per replica for adequate
   rotational averaging. Even for ubiquitin (tau_c approximately 4 ns), 10 ns provides
   only 2.5x coverage -- below the 5x minimum recommended by the iRED protocol
   (Prompers & Bruschweiler, JACS 2002).

   Additionally, the proposal restricts S2 analysis to only 4 of 7 proteins
   (ubiquitin, GB3, HEWL, T4 lysozyme), noting that "BPTI, barnase, and crambin have
   fewer published S2 entries." This overlooks that BPTI has approximately 55 published
   NH S2 values (my inventory) and barnase has approximately 95 NH S2 plus
   approximately 40 methyl S2 values. Both are sufficient for meaningful S2 comparison
   and should be included.

   - **Severity:** Major
   - **Addressable?** Yes, partially. Increase replica count to at least N = 15 for
     the 4 primary S2 proteins (the midpoint between 10 and 20). Increase per-replica
     length to at least 20 ns for small proteins (ubiquitin, GB3, BPTI) and 30 ns for
     larger ones (HEWL, barnase, T4 lysozyme). Include BPTI and barnase in the S2
     analysis -- both have sufficient published data. If compute budget is the
     constraint, reduce from 50 ns production single-trajectory to 30 ns for the less
     critical crambin, and redirect those GPU-hours to S2 replicas. The total compute
     increase is approximately 15,000-20,000 GPU-hours, manageable within the 20%
     contingency budget.

3. **Major: iRED method not specified for S2 calculation**
   The proposal describes S2 calculation using direct Lipari-Szabo fitting of the
   autocorrelation function C(t) = S2 + (1-S2)*exp(-t/tau_e), computing the "plateau
   of C(t) directly from long-time asymptote." This is the older, less robust approach.
   The community standard for computing S2 from MD trajectories is the iRED method
   (Isotropic Reorientational Eigenmode Dynamics; Prompers & Bruschweiler, JACS 2002),
   which properly separates internal motion from overall tumbling without requiring
   knowledge of the rotational diffusion tensor.

   Direct plateau fitting of C(t) is problematic because:
   (a) The autocorrelation function may not converge to a clear plateau in 10 ns
   (especially for larger proteins with tau_c > 5 ns).
   (b) It conflates internal dynamics S2 with overall tumbling, producing artificially
   low S2 values unless the overall rotation is removed first.
   (c) It is sensitive to the fitting window chosen for plateau estimation.

   Smith et al. (2024) explicitly used the iRED approach implemented in CPPTRAJ, and
   my own bioval proposal specifies iRED as the primary method with CPPTRAJ
   implementation. The proposal's implementation options list MDAnalysis BAT module,
   CPPTRAJ, custom NumPy code, and SPyCi-PDB -- but does not commit to iRED as the
   primary method.

   - **Severity:** Major
   - **Addressable?** Yes. Adopt iRED (CPPTRAJ `ired` command) as the primary S2
     computation method. Use direct Lipari-Szabo fitting only as a secondary
     cross-check. The iRED method is implemented in CPPTRAJ and validated against
     experimental S2 by Smith et al. (2024). This is a straightforward protocol change
     with no compute cost impact.

4. **Major: NVT ensemble for production -- defensible but needs justification**
   The proposal uses NVT (constant volume) for all production runs. While Lindorff-
   Larsen et al. (2012) showed that NVT and NPT produce equivalent NMR observables for
   ubiquitin and GB3 "within error," there is a practical concern: NVT requires that
   the box density is correct from the start. If PDBFixer solvation produces a box at
   the wrong density (e.g., because ML water has a different equilibrium density than
   TIP3P), the NVT simulation will run at the wrong pressure, potentially affecting
   protein compactness, Rg, and SAXS profiles.

   Notably, MACE-OFF24(M) itself was validated using **NPT dynamics** (Kovacs et al.,
   JACS 2025 -- "20 ns of NPT dynamics sampled with MACE-OFF24(M)"). Running
   production in NVT departs from MACE-OFF24's own validated protocol.

   For SAXS comparison specifically, Rg is sensitive to box pressure/density effects.
   A systematic pressure artifact in NVT could bias SAXS chi2 values.

   - **Severity:** Major
   - **Addressable?** Yes. Either (a) switch to NPT for production (preferred -- this
     matches how NMR experiments are performed at constant pressure, and MACE-OFF24 was
     validated in NPT), or (b) add a short NPT equilibration phase (2-5 ns) before
     switching to NVT production, and verify that the average pressure during NVT is
     within 50 bar of 1 atm. Report the average pressure for each NVT run. For SAXS
     comparison, NPT is strongly preferred because Rg depends on proper volume
     equilibration.

5. **Minor: Karplus parametrization is outdated**
   The proposal uses Vuister & Bax (1993) Karplus parameters: A = 6.51, B = -1.76,
   C = 1.60. My own bioval proposal uses the updated Bax et al. (2015) parameters:
   A = 7.97, B = -1.26, C = 0.63, derived from high-accuracy measurements on GB3 and
   ubiquitin. The intrinsic RMSD between Karplus-predicted and measured 3JHNHa for
   ideal structures is 0.53 Hz with the updated parameters. The 1993 parameters have
   a larger systematic error and are less well-calibrated for the specific proteins in
   our benchmark set.

   Using the older parameters introduces a systematic bias in J-coupling back-
   calculation that could be larger than the differences between force fields.
   Robertson et al. (JCTC 2015) showed that classical FF 3JHNHa RMSD ranges from
   0.35-0.97 Hz. If the Karplus parametrization itself contributes an additional
   approximately 0.3 Hz systematic error, the back-calculation noise approaches the
   signal.

   - **Severity:** Minor
   - **Addressable?** Yes. Adopt the Bax (2015) Karplus parameters as primary, report
     Vuister & Bax (1993) parameters as secondary for comparison with older literature.
     This is a trivial parameter swap with no compute cost.

6. **Minor: Chemical shift primary/secondary tool ordering disagrees with my proposal**
   The proposal designates SPARTA+ as primary and ShiftX2 as secondary. My own bioval
   proposal inverts this: SHIFTX2 primary, SPARTA+ secondary, based on SHIFTX2's
   lower reported prediction errors (13Ca RMSD 0.44 ppm vs SPARTA+ 0.94 ppm;
   Han et al., 2011 vs Shen & Bax, 2010). Additionally, SHIFTX2 is directly
   integrated into MDTraj (`mdtraj.chemical_shifts_shiftx2(traj)`), enabling efficient
   trajectory-scale computation.

   This is a minor disagreement because the proposal correctly plans to run both tools,
   and the cross-predictor consistency check is built into the ablation design. However,
   for the main figures, the more accurate predictor should be primary.

   - **Severity:** Minor
   - **Addressable?** Yes. Use SHIFTX2 as primary for main-text figures and
     statistical comparisons. Report SPARTA+ in Supplementary. If ShiftX2 and SPARTA+
     give discordant rankings, flag this explicitly -- it indicates the back-calculation
     noise exceeds force field differences for that observable/protein combination.

7. **Minor: Crambin provides minimal validation value**
   Crambin (1CRN) has no deposited S2 values, no J-couplings, no RDCs, and minimal
   chemical shifts in BMRB. It is included solely because it is the "de facto MLFF
   protein test case." While reproducing published MLFF results on crambin is useful
   for protocol validation, crambin contributes essentially zero experimental
   validation data points. Yet it consumes approximately 3,000-6,400 GPU-hours across
   the 3 MLFFs (among the most expensive systems due to its 18K solvated atom count).

   The compute spent on crambin production simulations would be better redirected to
   additional S2 replicas for data-rich proteins.

   - **Severity:** Minor
   - **Addressable?** Yes. Retain crambin for a 5 ns stability check (reproducing
     MACE-OFF24 and SO3LR published results). Do NOT run full 50 ns production or
     S2 replicas for crambin. Redirect the saved approximately 5,000 GPU-hours to
     additional S2 replicas for ubiquitin, HEWL, and T4 lysozyme.

---

## Feasibility Assessment

### Technical Feasibility

The proposal is technically feasible with the modifications above. The MLFF software
stack is production-ready: MACE-OFF24(M) via OpenMM-ML, SO3LR via JAX-MD, AI2BMD
via its published framework. The NMR back-calculation tools (SPARTA+, SHIFTX2,
CPPTRAJ, Pepsi-SAXS) are mature and well-documented. The SLURM job design with
checkpoint-restart is standard HPC practice. The main technical risk is AI2BMD
integration (custom framework, fragmentation setup), which the proposal correctly
identifies and has a clear fallback (AceFF-2.0 replacement).

One underappreciated technical risk: SO3LR runs in JAX-MD, which uses a fundamentally
different numerical framework (JAX autodifferentiation) from OpenMM. Verifying
thermostat behavior, energy conservation, and coordinate precision in JAX-MD requires
independent validation beyond just checking temperature. I recommend running a short
(1 ns) SO3LR simulation of alanine dipeptide and comparing the phi/psi Ramachandran
distribution to the published SO3LR results (Frank et al., JACS 2026) as a sanity
check.

### Scientific Feasibility

The study will produce definitive results regardless of outcome. If MLFFs match
classical force fields, that is a positive finding for the MLFF community. If MLFFs
underperform, that is the "reality gap" finding analogous to UniFFBench. If MLFFs
fail outright (crashes, instability), that is itself a critical finding about
production readiness. The study cannot "fail" scientifically -- only the individual
MLFFs can fail. This is a strong design.

The main scientific concern is whether 50 ns is sufficient for all observables to
converge. Chemical shifts and J-couplings converge rapidly (10-20 ns; Lindorff-Larsen
2012). S2 requires the multi-replica protocol. SAXS profiles (Rg, I(q)) converge
within 5-10 ns for well-folded proteins. The proposal's trajectory-length ablation
(10/20/30/40/50 ns checkpoints) directly addresses this concern. The risk is low for
the well-folded MVP protein set; it would be higher for IDPs or proteins with slow
conformational transitions, which are correctly deferred to the stretch set.

### Timeline Feasibility

The 12-14 week timeline is tight but achievable IF compute allocation is secured
early. The critical path is Phase 2 production runs (6 weeks with 21+ concurrent
GPUs). With the modifications I suggest (increased S2 replicas, temperature matching),
the compute budget increases by approximately 15,000-20,000 GPU-hours, stretching
the total to approximately 103,000-108,000 GPU-hours. This requires approximately
25-30 dedicated H200 GPUs for 8 weeks, which is substantial but within the project's
stated HPC allocation.

The AI2BMD integration risk is the most likely timeline threat. If AI2BMD setup takes
more than 2 weeks, it will delay all downstream analysis. The fallback to AceFF-2.0
is sound but should be triggered at the end of Week 1, not Week 2.

---

## Suggested Modifications

1. **Match simulation temperature to NMR experimental temperature for each protein.**
   Ubiquitin and GB3 at 298 K. HEWL at 308 K. BPTI at 308 K. Barnase at 298 K.
   T4 Lysozyme at 310 K. Crambin at 298 K (structural stability only). This is
   non-negotiable for a credible benchmark.

2. **Assign protonation states at experimental pH, not pH 7.0.** Use PropKa 3.5 or
   H++ to assign protonation states at: ubiquitin pH 6.5, GB3 pH 5.6, HEWL pH 3.8,
   BPTI pH 4.6, barnase pH 6.5, T4 lysozyme pH 5.5. For HEWL at pH 3.8, this will
   affect Glu35, Asp52, and several His residues. Document all protonation state
   assignments in the supplementary materials. Note that some MLFFs may not support
   non-standard protonation states gracefully -- if an MLFF cannot handle protonated
   Glu, document this as a limitation of the MLFF, not of the benchmark.

3. **Increase S2 replica protocol: N = 15 replicas, 20-30 ns per replica.** Target R2
   reproducibility >= 0.93 (splitting the difference between N = 10 and N = 20
   performance). Increase per-replica length to 20 ns for small proteins (ubiquitin,
   GB3, BPTI) and 30 ns for larger proteins (HEWL, barnase, T4 lysozyme). Include BPTI
   and barnase in the S2 analysis (both have adequate published data: approximately 55
   and approximately 95 backbone NH S2 values respectively).

4. **Adopt iRED as the primary S2 method.** Use CPPTRAJ `ired` command. Report
   convergence diagnostics: S2 vs number of replicas for 3 representative residues per
   protein (one rigid, one intermediate, one flexible). Compute ICC (intraclass
   correlation) across replicas as recommended by evalstat.

5. **Switch to NPT for production runs, or add NPT equilibration validation.** If NVT
   is retained, add a 2-5 ns NPT equilibration phase, verify average pressure during
   NVT is within 50 bar of 1 atm, and report average pressure for each system. For
   SAXS comparison, consider running HEWL in NPT specifically.

6. **Update Karplus parameters to Bax (2015).** A = 7.97, B = -1.26, C = 0.63.
   Report 1993 parameters as secondary in Supplementary.

7. **Reduce crambin scope.** 5 ns stability check only; no 50 ns production or S2
   replicas. Redirect compute to S2 replicas for data-rich proteins.

8. **Use SHIFTX2 as primary chemical shift predictor.** SPARTA+ as secondary
   cross-check. Both reported in all cases.

9. **Add ionic strength matching.** The proposal specifies 150 mM NaCl via PDBFixer.
   Most NMR experiments use 50-100 mM phosphate or acetate buffer with variable salt.
   Ubiquitin NMR data is typically at 50-100 mM phosphate with no added NaCl. While
   ionic strength effects on backbone NMR observables are small for well-folded
   proteins, explicitly matching to the experimental buffer concentration (protein by
   protein) demonstrates rigor. At minimum, document the ionic strength mismatch for
   each protein.

10. **Add a Garnet validation control run.** Garnet (arXiv 2603.16770) was trained on
    NMR data from exactly our benchmark proteins (GB3, BPTI, HEWL, ubiquitin) and ran
    5 microsecond simulations at 300 K with J-coupling comparison. Including Garnet as
    a third baseline (alongside AMBER ff19SB and CHARMM36m) directly tests whether a
    GNN-parameterized classical force field trained on NMR data outperforms pure MLFFs
    that have never seen NMR data. This is a powerful narrative element: the "NMR-aware
    vs NMR-naive" comparison. Since Garnet is OpenMM-compatible and freely available,
    the integration cost is low. Compute cost for 7 proteins at classical speed
    (approximately 300 ns/day) is negligible.

---

## Alternative Approaches

### S2 from BioEmu ensembles: a conceptual challenge

The proposal plans to compute S2 from BioEmu-generated conformational ensembles. This
requires careful thought about what "S2 from an ensemble" means. S2 is defined as the
plateau of the NH bond vector autocorrelation function, which requires *time-ordered*
trajectory data. BioEmu generates independent samples from an equilibrium distribution
-- it has no time axis. Computing S2 from BioEmu therefore requires either:

(a) Treating BioEmu samples as a structural ensemble and computing S2 as the variance
of N-H bond vector orientations across samples (the "structural" S2). This
approximates the true S2 only if the ensemble adequately samples all relevant
conformational states.

(b) Computing an alternative order parameter (e.g., circular variance of phi/psi
angles, RMSF-based proxy) from BioEmu ensembles and comparing to experimental S2
indirectly.

The proposal does not specify which approach will be used. I recommend approach (a)
with the Prompers-Bruschweiler iRED-like angular variance computation, explicitly
acknowledging that BioEmu "S2" is not identical to the time-correlation-derived S2
from MD. This distinction should be clearly stated in the methods section to avoid
conflating fundamentally different quantities. The difference between structural and
dynamic S2 is itself an interesting finding: if BioEmu's structural S2 matches
experiment well but misses slow-timescale motions captured by MD, this reveals
something fundamental about what BioEmu does and does not capture.

### RDC back-calculation for GB3

The proposal mentions GB3's 36 RDC datasets but does not include RDC in the primary
analysis plan. This is a missed opportunity. GB3 has the richest RDC dataset of any
protein (36 datasets in 5 independent alignment media, approximately 50-56 values per
set; BMRB 25807). RDC back-calculation via PALES or DC (Bax lab) is computationally
trivial. The Q-factor metric is well-calibrated: classical FFs achieve Q approximately
0.15-0.30 for GB3. Including RDC for GB3 adds a fifth observable type that probes
bond vector orientations rather than dynamics or local structure, providing an
orthogonal validation axis. My bioval proposal includes RDC analysis for GB3 and
ubiquitin via PALES SVD fitting.

Recommendation: add RDC back-calculation for GB3 (primary) and ubiquitin (secondary)
using PALES. Compute cost: negligible (approximately 10 CPU-hours).

---

## Impact on Publication Narrative

### Strengthening the combined Gamma + Alpha-M paper

The temperature matching correction is essential for the combined paper narrative.
If Alpha-M concludes that "MLFF X produces the best S2 agreement," but that
conclusion was obtained at the wrong temperature (300 K instead of 308 K for HEWL),
the Gamma project's downstream analysis inherits this systematic error. The Gamma
claim -- "MLFFs that produce more physically realistic dynamics also generate
ensembles that better predict biological function" -- is only as strong as the
Alpha-M validation underlying it. Running at the wrong temperature would give
reviewers an easy target to dismiss the entire combined narrative.

### The Garnet comparison strengthens the story

Including Garnet alongside pure MLFFs and classical baselines creates a clean three-way
comparison:

1. Classical FFs (AMBER ff19SB, CHARMM36m): hand-tuned parameters, refined against
   NMR data for decades.
2. Garnet: GNN-parameterized classical FF, explicitly trained against NMR J-couplings
   from our benchmark proteins.
3. MLFFs (MACE-OFF24, SO3LR, AI2BMD): trained on DFT data only, never exposed to
   NMR observables.

If MLFFs match or beat Garnet despite never being trained on NMR data, this is a
powerful statement about the quality of DFT-learned potentials. If Garnet wins because
it saw the NMR answer during training, this motivates the next generation of MLFFs to
incorporate experimental data in training -- a concrete, actionable recommendation.
Either way, the comparison enriches the paper.

### BioEmu as the bridge

The BioEmu comparator is the linchpin of the combined paper. If BioEmu ensembles
reproduce NMR observables as well as or better than MLFF trajectories (despite having
no explicit physics), this raises the question: does physical accuracy matter for
function prediction, or is statistical accuracy (matching the equilibrium distribution)
sufficient? This is the central question of the Gamma project. Alpha-M provides the
first half of the answer (which methods produce physically realistic dynamics);
Gamma provides the second half (which methods predict function). BioEmu appearing in
both connects them.

The key risk: if BioEmu S2 computation is not well-defined (see "Alternative
Approaches" above), this bridge weakens. Resolve the S2 definition for BioEmu
ensembles before launch.

---

## Garnet as an Informative Addition: Extended Analysis

The proposal correctly flags Garnet (arXiv 2603.16770, March 2026) as a potential
third classical baseline in its Open Questions section. Based on my research, I
can now confirm that Garnet:

- Was benchmarked against NMR J-couplings on exactly our proteins (GB3, BPTI, HEWL,
  ubiquitin) using 5 microsecond simulations at 300 K with 3 independent replicates.
- Is OpenMM-compatible (used OpenMM for GPU simulations during training).
- Is freely available.
- Showed J-coupling performance "comparable to" AMBER14SB and Espaloma, slightly
  underperforming on ubiquitin by approximately 0.05 Hz ANE.
- Uses hydrogen mass repartitioning with 4 fs timestep (different from our 1 fs --
  will need a separate 1 fs run for fair comparison, or report at 4 fs in
  Supplementary).

Including Garnet promotes it from "open question" to "confirmed third baseline." The
compute cost is negligible (classical-speed simulation). The scientific value is high:
it directly tests whether training on NMR data provides an advantage over learning from
DFT alone.

---

## Data Completeness Cross-Check

Comparing the proposal's data estimates to my own curated inventory:

| Protein | Proposal S2 Proteins | bioval S2 Count | Discrepancy |
|---------|---------------------|-----------------|-------------|
| Ubiquitin | Included (4/7) | ~70 NH | Consistent |
| GB3 | Included (4/7) | ~54 NH | Consistent |
| HEWL | Included (4/7) | ~120 NH + ~60 CH3 | Consistent |
| BPTI | Excluded | ~55 NH | **Include** |
| Barnase | Excluded | ~95 NH + ~40 CH3 | **Include** |
| T4 Lysozyme | Included (4/7) | ~150 NH | Consistent |
| Crambin | Excluded (no data) | 0 | Consistent |

The proposal's total NMR data estimate ("~4,000-5,000 backbone shift measurements,
~400-600 3J measurements, ~300-500 S2 values") is roughly consistent with my detailed
inventory of approximately 5,575 total data points across 7 proteins. The discrepancy
is primarily in S2: including BPTI and barnase adds approximately 150 NH S2 values and
approximately 40 methyl S2 values, increasing statistical power substantially.

---

## Summary of Required Changes (Priority Order)

| Priority | Change | Compute Impact | Scientific Impact |
|----------|--------|---------------|------------------|
| 1 (Critical) | Temperature matching per protein | None | Eliminates systematic bias |
| 2 (Critical) | pH-matched protonation states | None | Eliminates systematic bias |
| 3 (Major) | Increase S2 replicas to N=15, 20-30 ns | +15-20K GPU-hrs | Convergence credibility |
| 4 (Major) | Adopt iRED for S2 | None | Methodological correctness |
| 5 (Major) | NPT production or pressure validation | Negligible | Density/SAXS accuracy |
| 6 (Minor) | Karplus 2015 parameters | None | Reduced systematic error |
| 7 (Minor) | SHIFTX2 primary | None | Higher accuracy predictor |
| 8 (Minor) | Reduce crambin scope | Saves ~5K GPU-hrs | Compute reallocation |
| 9 (Enhancement) | Add Garnet baseline | ~100 GPU-hrs | Enriches narrative |
| 10 (Enhancement) | Add RDC for GB3 | ~10 CPU-hrs | Orthogonal validation |

Total compute budget after modifications: approximately 103,000-108,000 GPU-hrs
(original 88,400 + approximately 15,000 additional S2 replicas, minus approximately
5,000 crambin savings, plus negligible Garnet).

---

## References

1. Smith, L.J., et al. (2024). The Accuracy and Reproducibility of Lipari-Szabo
   Order Parameters From Molecular Dynamics. *J. Phys. Chem. B*, 128(44), 10813-10822.
   DOI: 10.1021/acs.jpcb.4c04895

2. Prompers, J.J. & Bruschweiler, R. (2002). General Framework for Studying the
   Dynamics of Folded and Nonfolded Proteins by NMR Relaxation Spectroscopy and MD
   Simulation. *JACS*, 124(16), 4522-4534. DOI: 10.1021/ja012750u

3. Lindorff-Larsen, K., et al. (2012). Systematic Validation of Protein Force Fields
   against Experimental Data. *PLoS ONE*, 7(2), e32131. DOI:
   10.1371/journal.pone.0032131

4. Robustelli, P., Piana, S., & Shaw, D.E. (2018). Developing a molecular dynamics
   force field for both folded and disordered protein states. *PNAS*, 115(21),
   E4758-E4766. DOI: 10.1073/pnas.1800690115

5. Cavender, C.E., Case, D.A., Lindorff-Larsen, K., Gilson, M.K., et al. (2025).
   Structure-Based Experimental Datasets for Benchmarking Protein Simulation Force
   Fields. *Living J. Comp. Mol. Sci.*, 6(1), e3871.

6. Palmer, A.G. III. (2004). NMR Characterization of the Dynamics of
   Biomacromolecules. *Chem. Rev.*, 104(8), 3623-3640. DOI: 10.1021/cr030413t

7. Baxter, N.J. & Williamson, M.P. (1997). Temperature dependence of 1H chemical
   shifts in proteins. *J. Biomol. NMR*, 9(4), 359-369.

8. Kovacs, D.P., et al. (2025). MACE-OFF: Short-Range Transferable Machine Learning
   Force Fields for Organic Molecules. *JACS*, 147(21). DOI: 10.1021/jacs.4c07099

9. Frank, M., et al. (2026). Molecular Simulations with a Pretrained Neural Network
   and Universal Pairwise Force Fields. *JACS*. DOI: 10.1021/jacs.5c09558

10. Garnet Force Field. (2026). Training a force field for proteins and small molecules
    from scratch. *arXiv*, 2603.16770.

11. Han, B., et al. (2011). SHIFTX2: significantly improved protein chemical shift
    prediction. *J. Biomol. NMR*, 50(1), 43-57. DOI: 10.1007/s10858-011-9478-4

12. Shen, Y. & Bax, A. (2010). SPARTA+: a modest improvement in empirical NMR
    chemical shift prediction. *J. Biomol. NMR*, 48(1), 13-22. DOI:
    10.1007/s10858-010-9433-9

13. Vuister, G.W. & Bax, A. (1993). Quantitative J correlation: a new approach for
    measuring homonuclear three-bond J(HNHa) coupling constants. *JACS*, 115(17),
    7772-7777.

14. Mandel, A.M., Akke, M., & Palmer, A.G. III. (1995). Backbone dynamics of
    Escherichia coli ribonuclease HI: correlations with structure and function in an
    active enzyme. *J. Mol. Biol.*, 246(1), 144-163.

15. Zweckstetter, M. (2008). NMR: prediction of molecular alignment from structure
    using the PALES software. *Nat. Protocols*, 3(4), 679-690.

16. Robertson, J.C., et al. (2015). Assessing the Current State of Amber Force Field
    Modifications for DNA. *JCTC*, 11(3), 951-960.

17. Li, T., et al. (2024). Ab initio characterization of protein molecular dynamics
    with AI2BMD. *Nature*, 635, 929-935.

18. Waibl, F., et al. (2025). Drug Discovery Stability Tests for Machine Learning
    Force Fields. *JCIM*.

19. Mannan, S., et al. (2025). Evaluating Universal Machine Learning Force Fields
    Against Experimental Measurements (UniFFBench). *arXiv*, 2508.05762.

20. Jing, B., et al. (2025). BioEmu: Generative equilibrium ensembles of
    conformational states. *Science*. DOI: 10.1126/science.adv9817

21. Grudinin, S., et al. (2017). Pepsi-SAXS: an adaptive method for rapid and
    accurate computation of SAXS profiles. *Acta Cryst. D*, 73(5), 449-464.

22. Teixeira, J.M.C., et al. (2024). SPyCi-PDB: A modular command-line interface for
    back-calculating experimental datatypes of protein structures. *JOSS*, 9(97), 4861.
