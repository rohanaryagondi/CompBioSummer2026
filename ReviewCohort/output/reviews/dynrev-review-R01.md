---
agent: Protein Dynamics & Force Field Reviewer (dynrev)
round: 1
date: 2026-04-15
type: review-assessment
scope: cross-cohort
---

# Mock NCS Reviewer 1: Alpha-M and Combined Gamma+Alpha-M Assessment

## Reviewing Agent

I am the reviewer an editor assigns when a paper involves molecular dynamics
simulation, ML force fields, and NMR validation. I have spent 20+ years running
and analyzing protein simulations and reviewing for Nature, Nature Computational
Science, JACS, JCTC, and PNAS. I am the reviewer who writes "the trajectory is
not converged and the authors know it." My review below reflects the standards I
would apply to a manuscript submitted to Nature Computational Science.

## Executive Summary

The combined Gamma+Alpha-M proposal attempts something genuinely ambitious: the
first systematic benchmark of ML force fields against experimental NMR protein
observables, linked to a downstream functional prediction pipeline. The concept
is sound and fills a real gap. However, the proposal contains a critical
structural flaw that the Cohort 2 reviewers did not adequately address: **no
existing MLFF has been demonstrated to run a stable 50 ns NPT trajectory on a
solvated protein.** The longest published MACE-OFF24 protein trajectory is 1.6 ns
on crambin (Kovacs et al., JACS 2025). SO3LR has demonstrated only 3 ns runs
on crambin (Kabylda et al., JACS 2026). AI2BMD has achieved 10 ns on chignolin
(175 atoms) but not on larger solvated proteins at the 50 ns timescale proposed
(Li et al., Nature 2024). The proposal's entire Phase 2 (50 ns production NPT
on 7 proteins with 8 methods = 56 trajectories) rests on an unproven assumption
that represents a 30-50x extrapolation from the state of the art. This is not a
minor concern -- it is the central technical risk of the project. Additionally,
the convergence protocol, while improved from earlier versions, still conflates
per-residue statistics with independent observations, and the BioEmu bias chain
analysis, though acknowledged, remains insufficiently controlled. My verdict is
**Major Revision** -- the science is worth doing but the simulation protocol
requires fundamental redesign to be credible at NCS.

---

## Detailed Critique

### Critical Issues

**C1. The 50 ns MLFF protein trajectory has never been demonstrated.**

This is the single most important point in this review. The proposal assumes
that MACE-OFF24, SO3LR, and AI2BMD can each produce stable 50 ns NPT
trajectories on 7 solvated proteins (56-164 residues + explicit water). The
published evidence does not support this assumption:

- **MACE-OFF24:** The longest solvated protein simulation in Kovacs et al.
  (JACS 2025) is 1.6 ns on crambin (~18,000 atoms total). The backbone RMSF
  remained below 1 A during a 1 ns simulation. The authors themselves state
  that "much longer simulations of at least several nanoseconds would be
  required to fully converge spectral features." Extrapolating from 1.6 ns to
  50 ns is a factor of 31x. No published work has demonstrated MACE-OFF24
  stability beyond ~2 ns on a solvated protein.

- **SO3LR:** Kabylda et al. (JACS 2026) demonstrated crambin simulations of
  ~3 ns (three 3 ns runs). The power spectrum was computed from 125 ps of
  dynamics. No protein larger than crambin (46 residues) has been simulated
  with SO3LR in published literature. Furthermore, SO3LR uses a JAX-MD
  thermostat, not standard GROMACS/OpenMM NPT integrators. The proposal
  mentions a "JAX-MD thermostat issue" in the risk registry (15% probability)
  but this understates the risk considerably -- achieving stable NPT
  equilibrium with a non-standard thermostat/barostat on a multi-nanosecond
  protein simulation is a research project in itself.

- **AI2BMD:** Li et al. (Nature 2024) reported 10 ns simulations on chignolin
  (175 atoms, 10-residue peptide) with 60 independent trajectories. For larger
  proteins, the paper demonstrates the fragmentation scheme but does not report
  50 ns production runs on proteins comparable to ubiquitin (76 residues) or
  T4 lysozyme (164 residues) in explicit solvent. AI2BMD's protein fragmentation
  approach requires reassembling fragment energies, which may introduce artifacts
  at fragment boundaries that accumulate over longer timescales.

- **The TEA Challenge 2023** (Chem. Sci. 2025) systematically tested MLFF
  stability and found that SOAP/GAP and FCHL19* "exhibited insufficient
  stability, rendering them unsuitable for extended MD simulations." Even
  MACE and SO3krates achieved only 1 ns trajectories on peptides (not
  proteins). The challenge found that "training data limitations" rather than
  architectural limitations were the "main bottleneck for atomistic simulations."

**Consequence:** The proposal budgets 44,800 GPU-hrs for Phase 2 production
runs. If 2 of 3 MLFFs cannot sustain 50 ns trajectories (which I estimate at
40-60% probability, not the proposal's 30%), this compute is wasted. The kill
criterion (Week 2, 30 ns stability) is sensible but may be reached for ALL
three MLFFs, leaving only classical baselines + BioEmu + Garnet.

**Recommendation:** Restructure the simulation protocol around what is
achievable:
(a) Start with 5 ns stability screening (not 1 ns -- 1 ns is too short to
    detect slow instabilities).
(b) If stable at 5 ns, extend to 10 ns, then 20 ns, then 50 ns, reporting
    convergence diagnostics at each checkpoint.
(c) Pre-register a "maximum achievable trajectory length" design: compare
    methods at their common maximum stable length, not a fixed 50 ns target.
(d) Report the trajectory length limit itself as a finding -- if MACE-OFF24
    crashes at 15 ns but SO3LR is stable to 50 ns, that is a result.
(e) Consider implicit solvent (GB/SA) as a stability backstop for MLFFs that
    fail in explicit solvent -- this removes the water-model problem while
    testing the protein intramolecular potential.

**Severity: Critical.** Without evidence that the proposed simulations are
feasible, the compute budget is not justified and the benchmark design is
aspirational rather than executable.

---

**C2. Per-residue statistics do not provide independent observations.**

The proposal claims to address the N=7 protein limitation by using "per-residue
cluster bootstrap (Davison & Hinkley, 1997) accounting for within-protein
correlation," providing "substantially more statistical power than N=7 proteins
suggest." This claim is misleading and was not adequately challenged by the
Cohort 2 reviewers.

The fundamental problem: residues within a protein are NOT independent
observations. They share the same:
- Trajectory (same simulation box, same thermostat, same initial conditions)
- Global tumbling (all residues in the same protein tumble together)
- Force field (same parameterization applied to all residues)
- Solvation environment (same water model, same box geometry)
- Simulation length and sampling quality

A cluster bootstrap can account for within-protein correlation to some degree,
but it cannot manufacture independent information that does not exist. If a
force field systematically overestimates S2 for ALL residues in a protein
(because, say, the backbone torsional potential is too stiff), then 76 residues
in ubiquitin provide one observation, not 76. The cluster bootstrap will
correctly identify that the 76 residues are correlated, but the resulting
confidence interval will be dominated by the single realization of the
trajectory.

The Smith et al. (2024) study on S2 convergence explicitly showed that
"bootstrapped agreement with experiment" depends on "ensemble size" (number of
replicas), not on the number of residues. The average R2 reaches a limiting
value that depends on the ensemble size used. Increasing from N=5 to N=20
replicas improved R2 by 0.05-0.10. The number of residues is not a substitute
for the number of independent trajectory realizations.

**Quantitative impact:** The proposal claims 420-560 residues across 7 proteins
provide sufficient power. In reality, for a force field comparison, the
effective sample size is closer to N=7 proteins x N=15 replicas = 105 protein-
replica pairs, but these are NOT independent across proteins for the same
method (same force field parameterization). The true effective N for method
comparison is N=7 proteins, with per-protein variance reduced by the 15
replicas. This is a substantial improvement over single-trajectory designs but
does not "substantially" exceed what N=7 suggests -- it approximately matches
it.

**Recommendation:** Be honest about the statistical design. State clearly that
the primary comparison has N=7 proteins, with per-protein uncertainty reduced
by the replica protocol. The per-residue analysis provides insight into WHICH
residues or secondary structure types are better/worse described, but cannot
increase the effective sample size for the method-level comparison. Consider
adding 3-5 more proteins (the proposal's own critique suggested this but was
overruled by scopeadv).

**Severity: Critical.** The statistical claim is central to the proposal's
defense of N=7, and it is overstated.

---

### Major Issues

**M1. BioEmu as "equilibrium" ensemble generator -- the ff14SB bias chain is
deeper than acknowledged.**

The proposal includes three controls for the BioEmu bias chain: (a) stability
circularity control, (b) ff14SB baseline inclusion, (c) assay-type
stratification. These are necessary but insufficient.

The deeper problem is that BioEmu was trained on AMBER ff14SB molecular
dynamics data. Lewis et al. (Science 2025) describe training on "more than
200 milliseconds of molecular dynamics simulations." These are ff14SB
simulations. BioEmu does not learn physics from quantum mechanics -- it learns
to reproduce the equilibrium distribution of ff14SB. This means:

(a) **BioEmu's S2 values will be bounded by ff14SB's S2 accuracy.** Smith
    et al. (2024) showed ff14SB achieves R2 = 0.62 for S2 against experiment.
    BioEmu cannot exceed this ceiling unless its generative model corrects
    ff14SB's systematic errors, which would be an extraordinary finding
    requiring extraordinary evidence.

(b) **The ff14SB baseline is the correct null hypothesis for BioEmu, not
    experiment.** The appropriate test is: "Does BioEmu reproduce ff14SB
    equilibrium distributions?" NOT "Does BioEmu reproduce experiment?" The
    proposal includes ff14SB as a baseline, which is good, but does not
    explicitly frame this as the primary comparison for BioEmu. If BioEmu
    S2 R2 matches ff14SB S2 R2 (both ~0.62), this is a positive result for
    BioEmu (faithful emulation) but NOT evidence that BioEmu captures real
    dynamics.

(c) **The Gamma-side implication:** If BioEmu ensembles are ff14SB
    equilibrium distributions, then Gamma's fitness prediction is effectively
    testing "do ff14SB equilibrium features predict ProteinGym fitness?" This
    is still interesting but substantially less novel than "do protein
    dynamics predict fitness?"

(d) **The Aryal et al. (2026) assessment** in Int. J. Mol. Sci. tested BioEmu
    performance and found it can "effectively reproduce fundamental properties
    including residue flexibility, motion correlations, and local residue
    contacts," but this assessment was against MD (i.e., ff14SB-generated)
    reference data, not experimental data. The proposal does not cite or
    address this study.

**Recommendation:** Add a dedicated section to the paper: "BioEmu as an ff14SB
Emulator." Frame the comparison explicitly: BioEmu vs ff14SB is about emulation
fidelity; BioEmu vs experiment is about the combined quality of ff14SB + BioEmu
generative model. The Gamma analysis should include a control: "Do ff14SB MD
ensemble features (from the 8 overlap proteins' 50 ns trajectories) predict
fitness with equal accuracy to BioEmu ensemble features?" If yes, BioEmu is
simply a fast ff14SB approximation. If no (BioEmu is better), BioEmu adds
value beyond ff14SB. If no (BioEmu is worse), the generative model loses
information.

**Severity: Major.** This affects the interpretation of both Alpha-M and Gamma
results and the combined paper's central claim.

---

**M2. iRED for S2 is appropriate, but the convergence criterion is
insufficiently validated.**

The proposal adopts iRED (Prompers & Bruschweiler, JACS 2002) as the primary
S2 method, which is the right choice -- iRED avoids the need to fit the overall
tumbling correlation time, which is critical when comparing methods that may
produce different effective tumbling times. However:

(a) **The ICC(2,k) > 0.80 convergence criterion** is borrowed from
    psychometric reliability literature and is not standard in the MD
    convergence community. The proposal does not justify why 0.80 is the
    appropriate threshold, nor does it cite precedent for using ICC in this
    context. The standard S2 convergence test is: compute S2 from the first
    half and second half of each trajectory and compare (block-splitting).
    Smith et al. (2024) recommend "10 to 20 replicas of 10-30 ns each" and
    show that R2 plateaus as a function of ensemble size. The ICC criterion
    may be overly permissive: ICC > 0.80 for 15 replicas could be achieved
    even if individual per-residue S2 values have not converged, because ICC
    measures between-method variance relative to within-method variance, not
    absolute convergence.

(b) **The 5x tumbling correlation time requirement** (attributed to Smith
    et al. 2024) is a minimum, not a guarantee. For ubiquitin (tau_c ~4 ns),
    5x = 20 ns, which is achievable. For T4 lysozyme (tau_c ~10 ns), 5x =
    50 ns. This means each of the 15 replicas for T4 lysozyme should be 50 ns,
    but the proposal allocates only 20-30 ns per replica. This is a direct
    contradiction: the proposal states "20 ns (small proteins) to 30 ns (large
    proteins)" but T4 lysozyme at 164 residues requires 50 ns per replica by
    the proposal's own cited criterion.

(c) **The trajectory-length ablation (10/20/30/40/50 ns)** is a good idea
    but is described only for the production runs, not for the S2 replicas.
    The S2 replicas are where convergence matters most. Each of the 15
    replicas should be assessed at multiple time points to establish when S2
    has converged for each protein.

**Recommendation:**
(i) Increase per-replica length for T4 lysozyme to 50 ns (consistent with
    the 5x tau_c requirement).
(ii) Apply the trajectory-length ablation to S2 replicas, not just production
     runs.
(iii) Replace or supplement ICC(2,k) with the standard block-splitting
      convergence test (first half vs second half) and the Smith et al. (2024)
      R2-vs-ensemble-size plateau analysis.
(iv) Report the per-protein tau_c from each method and compare to experimental
     values. Incorrect tau_c indicates incorrect global dynamics, which
     propagates to S2 even with iRED.

**Severity: Major.** Incorrect convergence assessment undermines the entire
benchmark -- unconverged S2 values will show method differences that are
artifacts of sampling, not force field quality.

---

**M3. The 7-protein benchmark set is adequate for a first study but has
exploitable gaps.**

The protein set (ubiquitin, GB3, HEWL, BPTI, barnase, T4 lysozyme, crambin)
is a reasonable starting point. However, a hostile reviewer will attack on
two fronts:

(a) **All proteins are small (46-164 residues).** No protein exceeds 200
    residues. The proposal acknowledges this in the critique but does not
    address it. The reason is practical -- MLFFs slow down dramatically with
    system size -- but the consequence is that the benchmark conclusions may
    not generalize to the proteins where dynamics matter most (enzymes,
    signaling proteins, often 300-600 residues). A reviewer will write: "The
    authors benchmark MLFFs only on small, rigid, well-folded proteins where
    classical FFs already perform well. The interesting question -- can MLFFs
    improve dynamics for larger, more flexible proteins? -- is not addressed."

(b) **No membrane protein, no multidomain protein, no IDP in the primary
    set.** Crambin is a stability check only. The set is dominated by
    globular, single-domain proteins with extensive NMR data. This is the
    "lamppost effect" -- benchmarking where the data is, not where the need
    is.

(c) **Crambin has no experimental S2 data** and "minimal" chemical shifts.
    Including it as a "stability check only" is fine, but it should be
    honestly described as a positive control for MLFF stability, not as a
    benchmark protein.

(d) **HEWL and BPTI require non-standard conditions** (308 K, low pH). The
    proposal correctly adjusts temperature and protonation, but a reviewer
    will ask: "Have the MLFFs been validated at 308 K and low pH? MACE-OFF24
    was trained on SPICE2+DES370K data at standard conditions. Does the
    training data include protonated Asp/Glu residues at low pH?" This is a
    legitimate concern -- ML force fields are only as good as their training
    data coverage.

(e) **The Garnet force field was validated on 4 of these exact 7 proteins**
    (GB3, BPTI, HEWL, ubiquitin; see arXiv:2603.16770). This is both a
    strength (direct comparison) and a weakness (Garnet was trained on NMR
    data from these proteins, so good performance may reflect overfitting to
    the benchmark).

**Recommendation:** Add a frank "Limitations" paragraph acknowledging the
small-protein bias. Consider adding RNase H (155 residues, excellent S2 data,
tau_c ~9 ns) or adenylate kinase (214 residues, S2 data available, known
domain motion) as a stretch target to extend the size range. If these are
impractical for MLFFs, state this explicitly -- "MLFFs cannot currently
simulate proteins larger than ~200 residues in explicit solvent" -- which is
itself a finding.

**Severity: Major.** Reviewers will use the small-protein bias to argue that
the benchmark does not test the hard cases where MLFF advantages would matter
most.

---

**M4. Back-calculation uncertainty is acknowledged but not quantified
for all observables.**

The proposal states: "Compute the 'indistinguishability zone' where method
differences are smaller than back-calculation noise (SPARTA+ 13C-alpha RMSD
1.09 ppm)." This is good practice. However:

(a) **S2 back-calculation uncertainty is not quantified.** The iRED method
    computes S2 directly from the trajectory (no intermediate prediction
    model), so the back-calculation uncertainty is zero in principle. But the
    comparison to experiment has uncertainty from the NMR relaxation analysis
    (R1, R2, NOE fitting with the Lipari-Szabo model). Experimental S2 values
    have typical uncertainties of 0.02-0.05 (Palmer, Chem. Rev. 2004). The
    proposal does not specify how experimental S2 uncertainties will be
    incorporated into the comparison.

(b) **SHIFTX2 and SPARTA+ have different error profiles.** SHIFTX2: 13C-alpha
    RMSD 0.44 ppm; SPARTA+: 13C-alpha RMSD 1.09 ppm (the proposal cites
    these correctly). But these are RMSD values, not per-prediction
    confidence intervals. A force field difference of 0.5 ppm in 13C-alpha
    shift could be within SHIFTX2 error but outside SPARTA+ error, depending
    on the prediction. The proposal should use per-prediction error estimates
    (both SHIFTX2 and SPARTA+ provide these) rather than global RMSD.

(c) **J-coupling Karplus equation uncertainty.** The Karplus equation
    J = A cos^2(phi) + B cos(phi) + C is an empirical model. The Bax (2015)
    parameters have uncertainties that propagate to predicted J values. A
    dihedral angle difference of 5 degrees near the inflection point of the
    cosine curve produces a larger J-coupling change than the same difference
    near the extremum. The proposal should report J-coupling uncertainties
    as a function of phi, not as a global RMSD.

**Recommendation:** For each observable, define the "method resolution limit"
-- the minimum force field difference that is detectable given back-calculation
uncertainty AND experimental uncertainty. If this limit is 0.05 for S2 R2, then
methods differing by less than 0.05 in S2 R2 are declared indistinguishable.
Pre-register this limit.

**Severity: Major.** Without properly quantified back-calculation uncertainty,
the benchmark cannot distinguish real force field differences from measurement
noise.

---

**M5. Garnet's benchmark circularity: trained on NMR data from the
benchmark proteins.**

The Garnet force field (arXiv:2603.16770) is a GNN-parameterized classical FF
"trained on NMR J-couplings from our exact benchmark proteins" (proposal text).
Specifically, Garnet was validated on GB3, BPTI, HEWL, and ubiquitin -- four of
the seven MVP proteins. Including Garnet as a baseline is valuable (it
represents the NMR-aware paradigm), but a reviewer will argue:

(a) **Garnet's good J-coupling performance on GB3, BPTI, HEWL, and ubiquitin
    is expected** because it was trained on data that includes these proteins'
    NMR observables. Testing Garnet on its training set inflates its apparent
    accuracy.

(b) **The fair test for Garnet** is on barnase, T4 lysozyme, and crambin --
    proteins NOT in its training set. If Garnet performs well on these proteins,
    the NMR-aware training generalizes. If it performs well only on its training
    proteins, it has overfit.

(c) **The Garnet paper itself notes**: "In all cases apart from HEWL,
    Amber14SB shows the lowest absolute normalised error (ANE), followed by
    our model and then Espaloma." This means Garnet does NOT clearly outperform
    classical FFs even on its training proteins.

**Recommendation:** Split the Garnet analysis: report performance on
"Garnet-train" proteins (ubiquitin, GB3, HEWL, BPTI) separately from
"Garnet-test" proteins (barnase, T4 lysozyme). Explicitly note the training
overlap. If Garnet underperforms on Garnet-test proteins relative to Garnet-
train proteins, this is evidence of overfitting.

**Severity: Major.** Training-test contamination in a benchmark paper is a
reviewable offense. The proposal must address this explicitly.

---

**M6. MLFF computational cost makes the comparison unfair unless
wall-clock time is reported.**

The proposal compares 50 ns trajectories from MLFFs and classical FFs as if
they are equivalent simulations. They are not:

- **Classical FF (AMBER ff19SB, GROMACS):** 50 ns on ubiquitin in explicit
  water takes ~2-4 hours on a modern GPU (e.g., H200). Cost: ~3 GPU-hrs.
- **MACE-OFF24:** Based on published throughput (~3 us/atom/step for MACE on
  an A100), 50 ns on ubiquitin (~18,000 atoms with water) would take
  approximately 10-20 days on a single GPU. Cost: ~240-480 GPU-hrs.
- **SO3LR:** Reported ~3 us/atom/step on a single H100 for systems up to
  200K atoms. Similar cost to MACE-OFF24.
- **AI2BMD:** Uses a fragmentation scheme that is more expensive per step than
  direct MLFF evaluation. Cost likely higher than MACE-OFF24.

The proposal's compute budget (44,800 GPU-hrs for Phase 2) implicitly
acknowledges this cost, but the paper must explicitly report wall-clock time
per trajectory. A reviewer will ask: "If MACE-OFF24 takes 100x longer than
AMBER ff19SB for the same trajectory length and produces similar or worse S2,
what is the practical value of the MLFF?"

**Recommendation:** Report wall-clock time and cost-per-quality-unit (e.g.,
GPU-hrs per 0.01 improvement in S2 R2) for each method. This is essential for
the paper's practical impact.

**Severity: Major.** A benchmark that does not report computational cost is
incomplete.

---

### Minor Issues

**m1. Temperature/pH matching is correctly addressed but protonation state
assignment needs more detail.**

The proposal states "Use PropKa 3.5 or H++ server at experimental pH for each
protein." This is acceptable but:
- PropKa and H++ can disagree, especially for buried residues (Glu35 in HEWL
  at pH 3.8 is a classic case).
- The same protonation state must be used for ALL methods. If PropKa assigns
  Glu35 as protonated for AMBER but the MLFF uses a different charge model,
  the comparison is confounded.
- Specify: "Protonation states will be determined once using PropKa 3.5 at
  the experimental pH, verified by H++ for discrepant residues, and applied
  identically to all methods."

**Severity: Minor.** Easily addressed with a protocol clarification.

---

**m2. Water model consistency across MLFFs and classical FFs.**

Classical FFs use specific water models (TIP3P for AMBER, TIP3P for CHARMM36m
typically). MLFFs (MACE-OFF24, SO3LR) do not use fixed-charge water models --
they treat water with the same ML potential as the protein. This means:
- The protein-water interaction is fundamentally different across methods.
- SAXS comparisons (Rg, P(r)) are sensitive to solvation shell structure.
- S2 values can be affected by protein-water hydrogen bonding, which affects
  local dynamics.

The proposal mentions a "water model g(r) quality check" as a zero-compute
ablation. This is good but should be elevated to a primary analysis: if an MLFF
produces a radically different water g(r) than experiment, its protein dynamics
may be wrong for reasons unrelated to the protein potential.

**Severity: Minor.** Important context for interpretation but not a design flaw.

---

**m3. BioEmu backbone-only ensembles require side-chain reconstruction.**

The proposal acknowledges that BioEmu generates backbone-only coordinates and
uses HPacker for side-chain reconstruction. However:
- HPacker's accuracy varies by residue type and burial (surface loops vs
  packed core).
- Side-chain-dependent Gamma features (SASA, contact frequency, cryptic pocket
  occupancy) are downstream of HPacker quality, not BioEmu quality.
- The proposal's feature separation into "backbone-robust" and "side-chain-
  dependent" sets addresses this, but the paper should report HPacker
  reconstruction quality metrics (chi1/chi2 accuracy, steric clashes) as a
  sanity check.

**Severity: Minor.** Well-handled by the feature separation design.

---

**m4. The convergence pilot for Gamma (500-10,000 BioEmu samples) is
adequate but should include a hold-out test.**

The proposal plans convergence analysis on 5 proteins at multiple sample sizes.
A stronger design: compute features from 10,000 samples, then compare to
features from 2,000 samples (the planned production size). If the features
differ substantially, 2,000 samples are insufficient. Report the coefficient
of variation (CV) for each feature as a function of sample size.

**Severity: Minor.** The pilot is a good idea; this strengthens it.

---

**m5. The Karplus parameter sensitivity analysis should include
the Habeck (2012) Bayesian parameterization.**

The proposal tests Bax (2015) vs Vuister & Bax (1993) Karplus parameters. A
third set (Habeck, J. Phys. Chem. B, 2012) derived from a Bayesian approach
would provide a more complete sensitivity analysis and is the methodologically
cleanest parameterization.

**Severity: Minor.**

---

**m6. Missing competitor ensemble generators in Alpha-M.**

The proposal benchmarks BioEmu as the sole non-MD ensemble generator. Since
submission, several competitors have emerged:
- **AlphaFlow** (Jing et al., 2024): AlphaFold + flow matching for ensembles
- **Boltz-2** with pair representation scaling (bioRxiv Jan 2026): steered
  conformational sampling
- **BBFlow** (Grater group, 2025): faster than AlphaFlow, backbone geometry
  only
- **P2DFlow** (JCTC 2025): SE(3) flow matching, outperforms AlphaFlow
- **TEMPO** (NeurIPS 2025): temporal multi-scale autoregressive generation

Including at least one additional non-MD generator (AlphaFlow is the most
mature) would strengthen the benchmark by testing whether the BioEmu findings
are specific to BioEmu or general to generative models.

**Severity: Minor** for Alpha-M standalone (BioEmu is the most validated), but
**Major** for Gamma if BioEmu shows poor S2 -- the paper needs to demonstrate
that the result is not BioEmu-specific.

---

## Assessment of Attack Vector Pre-emptions

### Attack Vector 1: "N=8 proteins too few for integration claim" (95%)

**Assessment: Partially pre-empted, but the statistical defense is overstated.**

The proposal's pre-emption relies heavily on the per-residue cluster bootstrap
argument (see C2 above), which inflates the apparent effective N. The multilevel
modeling approach (N=48 protein-generator pairs) is more defensible but still
has only 8 truly independent protein observations and 8 generator observations,
with complex crossed dependencies.

The precedent argument (Lindorff-Larsen 2012 used 4 proteins; Robustelli 2018
used 21 systems) is partially valid but misleading:
- Lindorff-Larsen 2012 compared 5 force fields on 32 model systems including
  dipeptides, tripeptides, and small proteins -- NOT 4 proteins. The protein-
  level comparison was indeed limited, but the total NMR dataset was 524
  measurements.
- Robustelli 2018 used 21 systems spanning folded proteins, IDPs, and peptides
  with >9,000 experimental measurements.

The proposal's 7 proteins with 8 methods is a reasonable design for a FIRST
study, but the integration claim across 6-8 proteins with Spearman correlation
is statistically fragile. The proposal should frame this honestly: "We test the
integration hypothesis on 6 primary overlap proteins. This provides sufficient
power to detect large effects (rho > 0.8 at N=8 generators) but not moderate
effects (rho ~0.5)."

**Verdict: Partially pre-empted.** The honest framing is "first evidence,"
which is what the proposal now states. But the per-residue bootstrap argument
should be removed from the statistical defense of the integration claim.

---

### Attack Vector 2: "BioEmu ff14SB bias chain = force field artifact" (80%)

**Assessment: Substantially pre-empted but with a remaining gap.**

The three controls (stability circularity, ff14SB baseline, assay-type
stratification) are well-designed. The addition of ff14SB as a direct baseline
is particularly strong -- it allows separating BioEmu emulation quality from
ff14SB inherent accuracy.

**Remaining gap:** The proposal does not include a "BioEmu vs ff14SB ensemble
feature" comparison for the Gamma fitness prediction task. If BioEmu ensemble
features and ff14SB MD ensemble features produce identical fitness prediction
accuracy, then BioEmu is adding speed but not information. This comparison
(see M1 above) is essential for the combined paper's novelty claim.

**Verdict: Mostly pre-empted.** Add the BioEmu-vs-ff14SB-features comparison
to close the gap.

---

### Attack Vector 3: "50 ns too short for converged dynamics" (75%)

**Assessment: Partially pre-empted, but fundamentally undermined by C1.**

The S2 replica protocol (15 replicas x 20-30 ns) is designed to address S2
convergence, and the trajectory-length ablation tests sensitivity. For S2
specifically, this is likely adequate for small proteins (ubiquitin, GB3, BPTI)
where tau_c = 4-5 ns and 20 ns replicas provide 4-5x tau_c.

**However, the pre-emption fails on three fronts:**

(a) For T4 lysozyme (tau_c ~10 ns), 30 ns replicas provide only 3x tau_c,
    which is below the 5x minimum. See M2.

(b) The 50 ns production runs are for chemical shifts and J-couplings, which
    the proposal claims "converge in 10-20 ns." This is true for chemical
    shifts (local property) but J-couplings depend on dihedral angle
    distributions, which can require 50-100 ns to converge for flexible
    residues. Lindorff-Larsen (2012) used microsecond aggregate simulation
    for a reason.

(c) The comparison to BioEmu is asymmetric: BioEmu generates samples from
    the (approximate) equilibrium distribution, while MLFFs generate
    time-correlated trajectories. Even at 50 ns, the MLFF trajectories may
    not have explored the full conformational space that BioEmu samples. This
    is acknowledged in the critique (Attack Vector 3 pre-emption point e) but
    not quantitatively addressed.

**Verdict: Partially pre-empted for S2, inadequately pre-empted for production
runs.** The fundamental problem (C1) that 50 ns may not be achievable at all
for MLFFs makes this discussion somewhat academic.

---

### Attack Vector 4: "Standard features/ML, no methodological novelty" (70%)

**Assessment: Adequately pre-empted for the combined paper, weak for Gamma
standalone.**

The combined paper's novelty is in the INTEGRATION, not the individual methods.
This is a sound argument. The "Dynamics Quality-Function Plane" figure makes the
case visually. NCS has published paradigm papers before (the UniFFBench
analogy is apt -- standard benchmarks with novel analysis framework).

For Gamma standalone, this attack vector is harder to deflect. MLP + XGBoost on
standard features with leave-protein-out CV is good science but not NCS-level
methodology. The GATv2 with dynamics-informed edges is moderately novel but
incremental.

**Verdict: Adequately pre-empted** for the combined paper. The novelty is real
and defensible: no one has connected force field validation quality to
functional prediction quality.

---

### Attack Vector 5: "Marginal improvement doesn't justify compute cost" (60%)

**Assessment: Partially pre-empted.**

The compute-matched comparison table is a strong defense. The argument that
Gamma ensemble generation costs only 143 GPU-hrs (vs AlphaMissense's millions)
is compelling. The assay-type stratification (binding/catalysis may show larger
improvements than the overall average) is also a good pre-emption.

**However:** The proposal does not pre-empt the cost of Alpha-M (~107K GPU-hrs)
relative to its marginal value. If Alpha-M shows that all MLFFs perform
comparably to classical FFs, the benchmark is valuable as a community resource
but the compute cost is high for a "negative" result. The proposal should frame
Alpha-M as a community resource (like a reference database) whose value is
independent of the outcome.

**Verdict: Partially pre-empted.** Strengthen the "community resource" framing
for Alpha-M compute.

---

## Additional Concerns Not Raised by Cohort 2

**A1. The GEMS force field (Unke et al., Science Advances 2024) is missing
from the benchmark.**

GEMS has demonstrated 10 ns NPT simulations of solvated crambin (~25,000 atoms)
-- the longest published MLFF protein trajectory in explicit solvent. If the
proposal's Phase 1 screening finds that MACE-OFF24 and SO3LR are unstable
beyond a few nanoseconds, GEMS may be the only MLFF capable of the production
runs. It should be included as a contingency MLFF alongside the proposed
AceFF-2.0 fallback.

**A2. The BioEmu augmented MD workflow (bioRxiv Jan 2026) changes the
landscape for Gamma.**

A recent bioRxiv preprint describes a workflow combining BioEmu ensembles with
physics-based MD and Markov State Models. This workflow captured active-to-
inactive transitions in kinases and resolved metastable states. If published
before the Gamma paper, this changes the competitive landscape -- it shows
that BioEmu ensembles need MD refinement to capture kinetics, which undermines
the assumption that raw BioEmu ensembles capture functionally relevant
dynamics.

**A3. Garnet's known IDP failure mode is relevant for alpha-synuclein.**

The Garnet paper (arXiv:2603.16770) explicitly notes that Garnet "over-compacts
IDPs...unlike the specialist force field a99SB-disp." Since alpha-synuclein is
in the exploratory integration set, Garnet's IDP limitation should be
acknowledged and alpha-synuclein should be excluded from the Garnet comparison.

**A4. The proposal does not specify force field version pinning.**

MLFFs are updated frequently. MACE-OFF24 has had multiple releases (MACE-OFF23,
MACE-OFF24, MACE-OFF24-SC). The proposal should specify exact model checkpoint
versions and pin them at the start of the project to ensure reproducibility.

---

## Verdict

**Major Revision.**

The combined Gamma+Alpha-M proposal is scientifically ambitious and fills a
genuine gap. The concept of connecting force field validation quality to
functional prediction quality is novel and would be a real contribution to
Nature Computational Science. The statistical framework (pre-registration,
Bayesian signed-rank, effect size quantification) is substantially more
rigorous than most MD benchmark papers. The risk management (kill criteria,
fallback paths) is commendable.

However, three issues require resolution before this is ready for execution:

1. **The 50 ns MLFF trajectory assumption is unproven (Critical).** The
   proposal must redesign the simulation protocol to accommodate the reality
   that no MLFF has demonstrated stable 50 ns protein trajectories. An
   adaptive trajectory-length design with pre-registered checkpoints would
   address this.

2. **The per-residue statistical power argument is overstated (Critical).**
   The effective sample size for method comparison is N=7 proteins, not
   420-560 residues. The proposal should be honest about this and frame the
   integration claim accordingly.

3. **The BioEmu bias chain needs one additional control (Major):** a direct
   comparison of BioEmu ensemble features vs ff14SB MD ensemble features for
   the Gamma fitness prediction task.

If these three issues are addressed, the proposal would be at the threshold of
NCS. With the current protocol, I would recommend Major Revision at NCS peer
review, with a high probability of favorable outcome after revision.

**Summary of required changes:**

| Issue | Severity | Required Action |
|-------|----------|-----------------|
| C1: 50 ns MLFF trajectory unproven | Critical | Adaptive trajectory-length protocol with checkpoints |
| C2: Per-residue stats overstated | Critical | Honest framing of N=7, remove per-residue from integration defense |
| M1: BioEmu bias chain incomplete | Major | Add BioEmu vs ff14SB feature comparison for Gamma |
| M2: S2 convergence criterion | Major | Fix T4 lysozyme replica length; add block-splitting test |
| M3: Small-protein bias | Major | Acknowledge; add 1 larger protein if feasible |
| M4: Back-calculation uncertainty | Major | Per-prediction errors, not global RMSD |
| M5: Garnet training overlap | Major | Split analysis by Garnet-train vs Garnet-test proteins |
| M6: Computational cost reporting | Major | Wall-clock time and cost-per-quality-unit |
| m1-m6: Various minor | Minor | See individual recommendations |

---

## References

1. Kovacs, D.P., et al. (2025). MACE-OFF: Short-Range Transferable Machine
   Learning Force Fields for Organic Molecules. J. Am. Chem. Soc. 147: 17598.
   -- Longest MACE-OFF24 solvated protein simulation: 1.6 ns on crambin.

2. Kabylda, A., Frank, T., et al. (2026). SO3LR: Molecular Simulations with
   a Pretrained Neural Network and Universal Pairwise Force Fields. J. Am.
   Chem. Soc. -- Crambin simulations of ~3 ns; ~3 us/atom/step on H100.

3. Li, J., et al. (2024). AI2BMD: Ab initio characterization of protein
   molecular dynamics. Nature 636: 1012. -- 10 ns simulations on chignolin
   (175 atoms); fragmentation-based approach for larger proteins.

4. Smith, D.G.A., et al. (2024). The Accuracy and Reproducibility of
   Lipari-Szabo Order Parameters from Molecular Dynamics. J. Phys. Chem. B
   128: 10090. -- N=10-20 replicas recommended; AMBER ff14SB R2=0.62,
   CHARMM36m R2=0.51; convergence within 10-30 ns per replica.

5. Lewis, J., Jing, B., et al. (2025). Scalable Emulation of Protein
   Equilibrium Ensembles with Generative Deep Learning. Science 369: 270-278.
   -- BioEmu trained on >200 ms of ff14SB MD; backbone-only output.

6. Aryal, R., et al. (2026). Assessing the Performance of BioEmu in
   Understanding Protein Dynamics. Int. J. Mol. Sci. 27: 2896. -- BioEmu
   reproduces RMSF, contacts, and correlations vs MD (ff14SB reference).

7. Prompers, J.J. and Bruschweiler, R. (2002). General Framework for Studying
   the Dynamics of Folded and Nonfolded Proteins by NMR Relaxation. J. Am.
   Chem. Soc. 124: 4522-4534. -- iRED method for S2 computation.

8. Palmer, A.G. (2004). NMR Characterization of the Dynamics of
   Biomacromolecules. Chem. Rev. 104: 3623-3640. -- Experimental S2
   uncertainties: 0.02-0.05.

9. Lindorff-Larsen, K., et al. (2012). Systematic Validation of Protein Force
   Fields against Experimental Data. PLoS ONE 7: e32131. -- 524 NMR
   measurements, 32 model systems, >25 us aggregate simulation.

10. Robustelli, P., Piana, S., and Shaw, D.E. (2018). Developing a molecular
    dynamics force field for both folded and disordered protein states. PNAS
    115: E4758-E4766. -- 21 systems, >9,000 experimental measurements.

11. Unke, O.T., et al. (2024). Biomolecular dynamics with machine-learned
    quantum-mechanical force fields trained on diverse chemical fragments.
    Science Advances 10: eadn4397. -- GEMS: 10 ns NPT on solvated crambin.

12. Garnet force field. (2026). Training a force field for proteins and small
    molecules from scratch. arXiv:2603.16770. -- Validated on GB3, BPTI, HEWL,
    ubiquitin; Amber14SB outperforms on 3 of 4 proteins; IDPs over-compacted.

13. TEA Challenge. (2025). Crash testing machine learning force fields for
    molecules, materials, and interfaces. Chem. Sci. -- MLFF stability limited;
    SOAP/GAP unsuitable for extended MD; training data is main bottleneck.

14. Mannan, T., et al. (2025). UniFFBench: Evaluating Universal Machine
    Learning Force Fields Against Experimental Measurements. arXiv 2508.05762.
    -- Materials MLFFs show "substantial reality gap" vs experiment.

15. Davison, A.C. and Hinkley, D.V. (1997). Bootstrap Methods and their
    Application. Cambridge University Press. -- Cluster bootstrap methodology.

16. Benavoli, A., et al. (2017). Time for a Change: A Tutorial for Comparing
    Multiple Classifiers Through Bayesian Analysis. J. Mach. Learn. Res. 18:
    1-36. -- Bayesian signed-rank test for method comparison.

17. Shen, Y. and Bax, A. (2010). SPARTA+: A Modest Improvement in Empirical
    NMR Chemical Shift Prediction. J. Biomol. NMR 48: 13-22. -- SPARTA+ 13Ca
    RMSD 1.09 ppm.

18. Han, B., et al. (2011). SHIFTX2: Significantly Improved Protein Chemical
    Shift Prediction. J. Biomol. NMR 50: 43-57. -- SHIFTX2 13Ca RMSD 0.44 ppm.

19. BioEmu augmented MD. (2026). Accelerated sampling of protein dynamics using
    BioEmu augmented molecular simulation. bioRxiv
    10.64898/2026.01.07.698041v2. -- BioEmu + MD + MSM workflow for kinases.

20. Jing, B., et al. (2024). AlphaFold Meets Flow Matching for Generating
    Protein Ensembles. arXiv 2402.04845. -- AlphaFlow as competitor ensemble
    generator.

21. P2DFlow. (2025). A Protein Ensemble Generative Model with SE(3) Flow
    Matching. J. Chem. Theory Comput. 21: 3288-3296. -- Outperforms AlphaFlow.

22. TEMPO. (2025). Temporal Multi-scale Autoregressive Generation of Protein
    Conformational Ensembles. NeurIPS 2025. -- Hierarchical autoregressive
    ensemble generation.

23. BBFlow. (2025). Learning conformational ensembles of proteins based on
    backbone geometry. arXiv 2503.05738. -- Faster than AlphaFlow, no
    pre-trained weights needed.

24. Structure-based benchmarking datasets. (2025). Structure-Based
    Experimental Datasets for Benchmarking Protein Simulation Force Fields.
    Living J. Comp. Mol. Sci. -- Tiered experimental dataset recommendations.

25. StABlE Training. (2025). Stability-Aware Training of Machine Learning
    Force Fields with Differentiable Boltzmann Estimators. OpenReview. --
    MLFF stability solutions for extended trajectories.

26. Tian, C., et al. (2020). ff19SB: Amino-Acid-Specific Protein Backbone
    Parameters Trained against Quantum Mechanics Energy Surfaces in Solution.
    J. Chem. Theory Comput. 16: 528-552. -- ff19SB improved backbone phi/psi.
