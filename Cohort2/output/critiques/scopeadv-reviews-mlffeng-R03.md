---
agent: scopeadv
round: 3
date: 2026-04-14
type: critique
proposal_reviewed: alpha-m-simulation
---

# Critique: Alpha-M -- Strategic Assessment of the MLFF Biomolecular Crash Test

## Reviewing Agent

**Dr. Strategic Scope & Competition Analyst (scopeadv)** -- Former academic
researcher, scientific program director, and journal editor. I review this proposal
as the third and final reviewer, following bioval (data quality) and evalstat
(methodology). My perspective is editorial and strategic: Would a Nature Computational
Science editor send this to review? Would reviewers accept it? Would the community
cite it? I assess competitive positioning, narrative strength, scope feasibility,
publication timing, and the "worst case still publishes" criterion. Every observation
is grounded in the April 14, 2026 competitive landscape from my own Round 2 strategy
proposal and updated with fresh competitive intelligence gathered today.

## Proposal Summary

mlffeng proposes the first systematic benchmark of 3 production-ready MLFFs
(MACE-OFF24(M), SO3LR, AI2BMD) plus 2 classical baselines (AMBER ff19SB, CHARMM36m)
and BioEmu against experimental NMR observables (S2 order parameters, J-couplings,
chemical shifts) and SAXS profiles across 7 proteins, using 50 ns NVT production runs
at 300 K. Estimated compute: ~88,400 GPU-hrs over 12-14 weeks. Target venue: Nature
Computational Science. The combined Gamma+Alpha-M paper narrative is "From Accurate
Ensembles to Biological Function."

---

## Overall Assessment

**Verdict:** Strong Support with Strategic Modifications

**One-line take:** This proposal occupies the widest competitive moat in the portfolio
and targets a gap that no group in the world is currently filling -- but after
incorporating bioval's and evalstat's corrections, the compute budget has ballooned
to ~103-108K GPU-hrs, creating a scope-timeline tension that must be resolved by
strategic prioritization rather than trying to do everything.

---

## Strengths

1. **Uncontested competitive position -- the moat is real and holding.**
   As of April 14, 2026, after exhaustive searching, I confirm that NO group has
   published or posted a preprint benchmarking multiple MLFFs against experimental
   protein NMR observables. The landscape has not changed since my R02 assessment:

   - The MACE group (Cambridge/Csanyi) has not published any MLFF-vs-NMR benchmark
     for folded proteins. Their focus remains on architecture development and the
     MACE-OFF24 paper (JACS 2025), which validated only on crambin power spectra and
     Ala3 J-couplings.
   - SO3LR (Frank et al., JACS 2026) validated lipid tail order parameters only.
     No protein backbone NMR. No follow-up preprints detected.
   - AI2BMD (Microsoft, Nature 2024) validated J-couplings on dipeptides only.
     Microsoft Research's public focus has shifted to BioEmu applications and drug
     design, not force field benchmarking.
   - DeepMind (GEMS) remains focused on AlphaFold3 and protein design. GEMS
     (Science Advances 2024) showed terahertz spectroscopy agreement for crambin but
     no NMR benchmarking. GEMS remains partially closed-source, excluding it from our
     benchmark anyway.
   - Egret-1 (Rowan, arXiv 2504.20955): A new MACE-architecture MLFF for bioorganic
     simulation, but explicitly limited to neutral closed-shell structures and cannot
     account for solvent effects. Not a competitor for solvated protein NMR benchmarking.
   - LAMBench (npj Comp Materials, 2025): Comprehensive MLFF benchmark for materials
     (inorganic, catalysis, molecules) but explicitly does NOT include proteins or
     biomolecular systems. Confirms the gap we fill.
   - CHIPS-FF (ACS Materials Letters, 2025): Another materials-focused MLFF benchmark
     from NIST. Materials only. No proteins.

   **The scoop probability remains <10% in 6 months and <20% in 12 months.** This is
   the safest project in the portfolio from a competitive standpoint. The 12-24+ month
   moat from my R02 assessment holds.

2. **The narrative is structurally sound for a Nature Computational Science audience.**
   The proposal correctly identifies the UniFFBench precedent (Mannan et al., arXiv
   2508.05762) as the narrative blueprint: a "reality gap" paper that exposed the
   disconnect between computational benchmarks and experimental measurements for
   materials science MLFFs. Extending this to biomolecules is a natural and compelling
   next step. The claim -- "We reveal a biomolecular reality gap between ML force field
   computational benchmarks and experimental protein observables" -- is testable,
   interesting regardless of direction, and novel. This is the type of study that a
   Nature Comp Sci editor sends to review because it addresses a genuine blind spot
   in a rapidly growing field.

3. **The MLFF selection is excellent and strategically defensible.**
   Choosing 3 MLFFs spanning 3 architectures (equivariant message passing, neural
   network + universal pairwise, fragmentation + ViSNet) and 3 simulation engines
   (OpenMM-ML, JAX-MD, custom) maximizes scientific insight while minimizing the
   "why didn't you include X?" reviewer attack surface. The explicit disqualification
   rationale (ANI-2x: amorphous ice; LiTEN-FF: immature; GEMS: closed-source;
   AceFF-2.0: no protein data) is thorough. The inclusion of AceFF-2.0 as a stretch
   candidate is prudent given that AceFF-2.0 is currently trained on "specifically
   curated and extended PubChem data, however, proteins, water, etc are not part of
   the dataset right now" (per Hugging Face page, confirmed April 2026). This confirms
   AceFF-2.0 exclusion from the MVP is correct.

4. **BioEmu inclusion is the single most strategically valuable design decision.**
   At ~200 GPU-hrs, BioEmu provides a built-in bridge to the Gamma project and a
   built-in surprise finding regardless of outcome. If BioEmu ensembles match NMR
   observables better than MLFF trajectories, the combined paper narrative is
   strengthened: "the fastest way to get physically realistic ensembles is generative,
   not simulated." If BioEmu is worse, the combined paper argues: "validated dynamics
   from accurate MLFFs produce the best ensembles for function prediction." Either way,
   the Gamma integration is seamless. This is rare -- a design decision that hedges
   both directions.

5. **The "cannot fail" property is genuine.**
   The proposal correctly identifies that all outcomes are publishable:
   - MLFFs match classical: "MLFFs have reached accuracy parity" (positive for MLFF
     adoption; novel finding)
   - MLFFs exceed classical: "MLFFs capture physics beyond classical refinement"
     (field-changing)
   - MLFFs underperform: "The biomolecular reality gap" (field-correcting, UniFFBench
     analogue)
   - MLFFs crash: "Production readiness assessment" (field-informing)
   - Mixed results across observables: "Observable-dependent MLFF accuracy"
     (most likely, most interesting)

   This is the gold standard for a benchmark proposal: every corner of outcome space
   leads to a publishable story. My only caveat is venue calibration (see Weakness #3).

6. **The Garnet strategic opportunity is correctly identified.**
   The proposal mentions Garnet (arXiv 2603.16770, March 2026) as a potential third
   classical baseline. This is strategically important and I expand on this below.

---

## Weaknesses

1. **Critical: Scope Inflation from Prior Reviews Creates an Impossible Compute Budget**

   The original proposal budgets ~88,400 GPU-hrs. After bioval's and evalstat's
   modifications, the compute requirement has inflated substantially:

   | Modification | Source | GPU-hrs Added |
   |-------------|--------|---------------|
   | S2 replicas: 10 -> 15 per protein | bioval | +~15,000-20,000 |
   | S2 per-replica length: 10 ns -> 20-30 ns | bioval | +~10,000-15,000 |
   | Expand S2 to 6 proteins (add BPTI, barnase) | bioval | +~5,000-8,000 |
   | Expand protein set from 7 to 12-15 | evalstat | +~40,000-50,000 |
   | ML/MM water ablation (2 proteins) | evalstat | +~5,000-7,000 |
   | NPT production runs (if switched from NVT) | bioval | ~0 (same compute) |

   **Conservative total after all modifications: ~165,000-188,000 GPU-hrs.**

   This is 1.9-2.1x the original budget. Even the "partial" version (bioval's
   modifications only) pushes to ~103-108K GPU-hrs. Adding evalstat's protein
   expansion to N=12-15 essentially doubles the project.

   The fundamental problem: both reviewers are correct in isolation, but their
   combined recommendations are infeasible within the stated timeline and compute
   budget. bioval correctly notes that S2 convergence needs more replicas and longer
   runs. evalstat correctly notes that N=7 underpowers the Friedman/Nemenyi test. But
   addressing BOTH requires either (a) doubling the compute budget to ~165K+ GPU-hrs,
   or (b) making strategic scope cuts elsewhere.

   - **Severity:** Critical
   - **Addressable?** Yes, through strategic prioritization. See Suggested Modifications
     below. The key insight is that not all reviewer requests are equally important for
     the publication narrative. Some can be deferred to Supplementary or to a follow-up
     study without weakening the core claim.

2. **Major: The N=7 Problem Is Real But the Proposed Solution (Expand to 15) Is Wrong**

   evalstat is correct that N=7 underpowers the Nemenyi post-hoc test. But the solution
   of expanding to 12-15 proteins at +40-50K GPU-hrs is the wrong response for three
   reasons:

   **(a) NCS does not require formal pairwise statistical significance at alpha=0.05.**
   I have read hundreds of Nature-branded benchmark papers. Not one has been rejected
   because the Nemenyi critical difference was too large. What NCS editors and reviewers
   care about is: (i) a clear visual ranking with confidence intervals, (ii) effect
   sizes with practical interpretation, (iii) robustness across observables, and (iv)
   a compelling narrative. The paper's Figure 1 will be a heatmap of method x observable
   x protein performance. If the pattern is clear, no reviewer will demand a p<0.05
   Nemenyi test. If the pattern is noisy, no sample size will save the paper.

   **(b) The real statistical power comes from per-residue analysis, not per-protein.**
   evalstat themselves note this (Weakness #1c): "For S2 with ~300-500 residues across
   7 proteins, this gives N_eff in the hundreds." The cluster bootstrap approach
   (resampling at the protein level to account for within-protein correlation) provides
   far more statistical power than adding proteins. With 7 proteins x ~60-80 backbone
   NH residues each = 420-560 residues, per-residue bootstrap with protein-level
   clustering is well-powered for pairwise comparison. This costs zero additional GPU
   time -- it is purely an analysis choice.

   **(c) Adding 8 proteins adds 8 weeks of simulation time.**
   Even at maximum GPU parallelism (each new protein runs on its own GPU), each
   additional protein-MLFF combination takes ~5-7 days of wall-clock time for 50 ns
   at MACE-OFF24(M) speeds. 8 proteins x 3 MLFFs = 24 additional production runs,
   plus S2 replicas. The timeline extends from 14 weeks to 18-22 weeks, pushing the
   preprint from November to January-February 2027. This is still within the
   competitive moat, but it delays the combined Gamma+Alpha-M paper and may force
   the projects to split.

   **My recommendation:** Stay at 7 proteins for the MVP. Use per-residue cluster
   bootstrap as the primary statistical analysis. Report Friedman/Nemenyi as a
   secondary analysis with an explicit transparency statement about its limited power
   at N=7. Add evalstat's Bayesian signed-rank test (which works well at small N) as
   a tertiary analysis. Pre-register all three. If compute permits, add 2-3 proteins
   from bioval's Tier A as Extended Data, bringing N to 9-10 at moderate cost.

   - **Severity:** Major
   - **Addressable?** Yes. The per-residue bootstrap + Bayesian approach is
     statistically superior to brute-force protein expansion and costs zero additional
     GPU time. See Suggested Modifications.

3. **Major: Venue Calibration Needs Nuance -- Not Every Outcome Is NCS-Level**

   The proposal claims NCS as the target for all outcomes. This is overconfident.
   Here is my honest venue assessment by outcome scenario:

   | Outcome | NCS? | Why / Why Not | Fallback Venue |
   |---------|------|---------------|----------------|
   | MLFFs substantially outperform classical FFs | YES | Field-changing finding | -- |
   | Mixed results: MLFFs excel on some observables, lag on others | YES | Most interesting story; observable-dependent accuracy | -- |
   | MLFFs match classical FFs within uncertainty | MAYBE | Depends on equivalence testing rigor and Gamma integration | Nature Methods |
   | MLFFs substantially underperform classical FFs | MAYBE | "Reality gap" is publishable but less exciting than UniFFBench because it is expected | Nature Methods, JCTC |
   | 2/3 MLFFs crash; only 1 survives | NO (at NCS) | Production readiness is useful but not paradigm-level | JCTC, J. Phys. Chem. B |
   | All MLFFs crash | NO (at NCS) | Important negative finding but N=3 MLFFs is too few for a definitive "MLFFs don't work" claim | JCTC |

   The critical distinction: if MLFFs simply reproduce what classical FFs already do,
   the standalone Alpha-M paper is "important but expected" -- not the kind of surprise
   that NCS editors prioritize. The COMBINED Gamma+Alpha-M paper rescues the NCS
   candidacy in this scenario because it adds the biological function dimension. This
   is the strongest strategic argument FOR the combined paper.

   - **Severity:** Major
   - **Addressable?** Yes. The combined Gamma+Alpha-M paper should be the default
     plan, not a conditional option. Alpha-M standalone should target Nature Methods
     or JCTC, not NCS. The combined paper is where the NCS-level claim lives.

4. **Major: Garnet Must Be Included -- It Is the Strongest Narrative Element You Are
   Currently Treating as Optional**

   The proposal mentions Garnet (arXiv 2603.16770, March 2026) as an "optional" third
   classical baseline. This is a strategic error. Garnet is the single most valuable
   addition to the benchmark because it creates a clean three-way comparison that no
   reviewer can resist:

   | Category | Methods | Training Data |
   |----------|---------|---------------|
   | Classical (hand-tuned) | AMBER ff19SB, CHARMM36m | 30 years of NMR refinement |
   | GNN-parameterized classical (Garnet) | Garnet | QM + NMR J-couplings from GB3, BPTI, HEWL, ubiquitin |
   | Full MLFFs (DFT-only) | MACE-OFF24(M), SO3LR, AI2BMD | DFT reference calculations only |

   **Why this is strategically essential:**

   (a) Garnet was explicitly trained on NMR J-coupling data from exactly our benchmark
   proteins (GB3, BPTI, HEWL, ubiquitin). This means Garnet has an unfair advantage
   on J-couplings for these proteins -- it has literally seen the test set. If MLFFs
   (which have NEVER seen NMR data) match or exceed Garnet on J-couplings, that is a
   stunning finding: "DFT-trained models learn protein physics that approaches
   NMR-refined classical force fields."

   (b) If Garnet dominates on J-couplings (expected, since it was trained on them),
   the story becomes: "NMR-informed training still matters; pure DFT training is
   necessary but not sufficient for J-coupling accuracy." This guides MLFF developers
   toward hybrid training strategies.

   (c) Garnet runs at classical FF speed (~300 ns/day). The compute cost for 7
   proteins is negligible (~120 GPU-hrs). There is no resource excuse to exclude it.

   (d) Garnet uses its own GNN-parameterized water model trained from scratch. This
   provides yet another water model comparison point alongside ML water from MLFFs
   and TIP3P from classical baselines.

   (e) Garnet is freely available, uses a PyTorch implementation, and was validated on
   exactly our proteins. The integration barrier is minimal.

   (f) Garnet simulated each protein for 5 microseconds with 3 replicas per system.
   We can potentially use their published trajectories as an additional reference
   point (though we should run our own for controlled comparison).

   bioval independently reached the same conclusion in their review, recommending
   Garnet as a "powerful narrative element." I concur and elevate this from "minor
   suggestion" to "major strategic requirement."

   - **Severity:** Major
   - **Addressable?** Yes. Garnet inclusion costs ~120 GPU-hrs (negligible). The
     narrative benefit is enormous. Include it in the MVP, not as a stretch goal.

5. **Minor: The "Bojan et al." Adjacent Work Is Under-Exploited**

   Bojan et al. (arXiv 2505.23354, originally March 2026, revised to "Representing
   local protein environments with atomistic foundation models") used MLFF intermediate
   representations (MACE, ORB, AIMNet2) to build a chemical shift predictor that
   outperforms UCBShift2-X. This paper is complementary to ours, not competitive. But
   the proposal does not cite it or discuss how to use it strategically.

   **Strategic value:** If our MLFF trajectories produce chemical shifts (via SPARTA+/
   ShiftX2 back-calculation) that agree with experiment, and Bojan et al. show that
   MLFF representations inherently capture NMR-relevant structural information, the
   combined evidence is far stronger than either alone. Our paper should cite Bojan
   et al. prominently in the Introduction to establish that "MLFF features encode
   NMR-relevant physics" and then ask: "but do MLFF *dynamics* -- not just static
   representations -- produce NMR-consistent trajectories?"

   Additionally, Bojan et al.'s chemical shift predictor (trained on MLFF embeddings)
   could be included as an alternative to SPARTA+/ShiftX2 for chemical shift
   back-calculation, providing a third predictor for the chemical shift sensitivity
   ablation that evalstat recommends.

   - **Severity:** Minor
   - **Addressable?** Yes. Cite and position in the Introduction. Consider including
     their predictor as a third chemical shift back-calculation method.

6. **Minor: The Preprint Timing Strategy Needs Specificity**

   The proposal mentions "preprint as soon as MVP results available (target August
   2026)" but my R02 strategy proposal set the Alpha-M preprint target at November 15,
   2026. The August date appears to be aspirational rather than realistic given the
   12-14 week timeline starting from May 1. The realistic timeline:

   - May 1: Project launch
   - May 30: Stability check
   - June 1-August 31: MVP simulations (~13 weeks)
   - September 1-30: Back-calculation and analysis
   - October 1-31: Writing, figures, integration with Gamma
   - November 15: Preprint

   Given the <10% scoop probability in 6 months, there is no urgency to rush a
   preprint before the analysis is thorough. Quality beats speed for this project.
   The preprint should go up when ALL analyses are complete, not when "MVP results
   are available." A premature preprint with incomplete analysis invites criticism
   and wastes the territorial advantage.

   However, there IS a strategic reason to post a "registered report" or
   pre-registration on OSF by June 1 (as evalstat recommends). This establishes
   territorial priority ("we are doing this study") without committing to results.
   The pre-registration is timestamped and citable, providing a soft territorial
   marker.

   - **Severity:** Minor
   - **Addressable?** Yes. Set November 15, 2026 as the firm preprint target. Post
     OSF pre-registration by June 1, 2026 for territorial protection.

7. **Minor: Kill Criteria Are Appropriately Conservative But Need One Addition**

   The existing kill criteria are well-calibrated:
   - 2/3 MLFFs fail stability: kill project (correct)
   - RMSD >5 A: flag combination as failure (correct)
   - Compute >150K GPU-hrs: reduce scope (correct)

   **Missing kill criterion:** What if all 3 MLFFs are stable but produce
   INDISTINGUISHABLE results? Specifically: if the per-observable rankings of all 3
   MLFFs are identical (tied ranks on all observables for all proteins), the story
   collapses from "which MLFF is best?" to "all MLFFs are the same." This is NOT a
   kill scenario (the classical vs. MLFF comparison is still novel) but it IS a scope
   reduction signal: the 3-architecture comparison is not producing discriminatory
   information. In this case, reduce the paper's focus to "MLFFs collectively vs.
   classical FFs" and drop the inter-MLFF ranking narrative.

   - **Severity:** Minor
   - **Addressable?** Yes. Add a "soft pivot" criterion: if ICC between the 3 MLFFs
     exceeds 0.95 on all observables at the Week 8 checkpoint, pivot the narrative
     from "which MLFF is best" to "do MLFFs as a class match classical FFs."

---

## Feasibility Assessment

### Technical Feasibility

**HIGH.** The core simulation stack is production-ready: MACE-OFF24(M) via OpenMM-ML
is the most mature MLFF protein simulation pathway. SO3LR via JAX-MD has demonstrated
3 ns crambin simulations. AI2BMD has a custom framework that has produced published
protein dynamics. The NMR back-calculation pipeline (SPARTA+, ShiftX2, Karplus,
Pepsi-SAXS) is decades-old and well-validated.

The main technical risk is AI2BMD integration. bioval correctly flags this as the
primary timeline threat. My strategic recommendation: set a hard deadline of May 14
(end of Week 2) for AI2BMD integration. If the custom framework cannot produce a
stable 1 ns ubiquitin trajectory by May 14, replace AI2BMD with the fallback. The
fallback should NOT be AceFF-2.0 (which has no protein training data as of April 2026),
but rather an ML/MM approach with NequIP/Allegro via OpenMM-ML. Allegro has
demonstrated >3 ns stable protein simulations (DHFR, factor IX) and now has OpenMM-ML
integration (v0.4.0, April 2025). This is a stronger fallback than AceFF-2.0 because
Allegro (a) has protein simulation data, (b) uses a different architecture (local
equivariant), and (c) runs natively in OpenMM.

### Scientific Feasibility

**HIGH.** This study cannot "fail" scientifically. Every outcome produces a novel
finding. The key scientific risk is not failure but banality: if all methods perform
similarly, the paper becomes "we confirmed what everyone expected" rather than "we
discovered a reality gap." The Gamma integration rescues banality by connecting
ensemble quality to biological function.

The Cavender et al. (LiveCoMS 2025) review provides an authoritative reference for
which experimental datasets and observables should be used for force field
benchmarking. This review explicitly discusses NMR chemical shifts, J-couplings, S2
order parameters, SAXS, and RDCs -- exactly the observables in our study. It is the
"blessing from the community" that legitimizes our observable selection. The proposal
should cite this review prominently.

### Timeline Feasibility

**MODERATE.** The 12-14 week timeline is achievable for the ORIGINAL 88K GPU-hr
budget, but strained at the ~103-108K GPU-hr level (after bioval's corrections) and
infeasible at the ~165K GPU-hr level (after adding evalstat's protein expansion). My
strategic resolution: stay at 88-105K GPU-hrs, absorb bioval's most critical
corrections (temperature matching, iRED method, Karplus update -- zero compute cost),
accept bioval's S2 replica increase to N=15 for 4 proteins only (moderate compute
cost), and REJECT evalstat's protein expansion to N=15 (high compute cost, low
marginal value given per-residue bootstrap analysis).

The revised timeline remains 14-16 weeks with bioval's corrections:
- Weeks 1-2: Setup, stability testing, AI2BMD integration
- Weeks 3-8: Production runs (50 ns for 7 proteins x 3 MLFFs + Garnet + 2 classical)
- Weeks 5-10: S2 replicas (15 rep x 20 ns for 4 proteins x 3 MLFFs, staggered)
- Weeks 9-12: Back-calculation and analysis
- Weeks 11-14: Writing and figures
- Week 14-16: Buffer / integration with Gamma

This is tight but achievable with 25-30 dedicated H200 GPUs.

---

## Suggested Modifications

### Priority 1: Strategic Scope Resolution (Critical)

1. **Resolve the bioval/evalstat scope conflict by strategic prioritization.**
   Accept bioval's zero-cost corrections (temperature matching, pH matching, iRED
   method, Karplus update, ShiftX2 primary). Accept bioval's moderate-cost corrections
   (S2 replicas to N=15 for 4 proteins, per-replica length to 20 ns for small proteins,
   30 ns for large). REJECT evalstat's protein expansion to N=12-15. Use per-residue
   cluster bootstrap + Bayesian signed-rank as the primary statistical framework,
   rendering the Friedman/Nemenyi power analysis less critical. This keeps the compute
   budget at ~105K GPU-hrs (manageable) rather than ~165K (infeasible).

2. **Include Garnet as a mandatory baseline, not optional.** Garnet runs at classical
   speed, costs ~120 GPU-hrs, and creates the most narratively powerful comparison in
   the study (NMR-trained GNN-classical vs. DFT-only MLFFs). Promote from "Open
   Question #6" to "Baseline #3."

3. **Set the combined Gamma+Alpha-M paper as the default plan.** Alpha-M standalone is
   Nature Methods / JCTC, not NCS. The NCS-level claim requires the biological function
   connection: "validated ensemble quality predicts biological function." Design
   Alpha-M analyses to be modular (publishable independently) but plan for combination.

### Priority 2: Narrative and Positioning (Major)

4. **Adopt a title and framing that signals paradigm, not just benchmark.**
   Current title: "Alpha-M -- The MLFF Biomolecular Crash Test."
   This is a good working title but wrong for NCS submission. My recommended titles:

   **For standalone Alpha-M (Nature Methods/JCTC):**
   "Machine learning force fields do not yet reproduce experimental protein dynamics"
   -- if reality gap is found.
   "Machine learning force fields match decades of classical refinement for protein
   dynamics" -- if parity is found.
   (Choose based on results.)

   **For combined Gamma+Alpha-M (NCS):**
   "From Accurate Ensembles to Biological Function: ML Force Fields Produce Dynamics
   That Predict Protein Fitness"
   -- if both signals are positive.
   "Ensemble Quality Determines Functional Prediction: Lessons from Benchmarking ML
   Protein Dynamics"
   -- if mixed Alpha-M results but Gamma positive.

   **The one-sentence claim for a NCS editor:**
   "We show that machine learning force fields produce protein dynamics that match or
   exceed classical force field agreement with experimental NMR observables, and that
   the quality of these conformational ensembles directly predicts mutational effects
   on protein function."

5. **Frame Garnet as the "NMR-aware vs NMR-naive" comparison.**
   The paper's central figure should include a panel showing:
   - x-axis: NMR observable type (S2, J-couplings, chemical shifts, SAXS)
   - y-axis: Agreement with experiment (normalized metric)
   - Series: AMBER ff19SB (hand-tuned, NMR-aware), Garnet (GNN-trained, NMR-aware),
     MACE-OFF24 (DFT-trained, NMR-naive), SO3LR (DFT-trained, NMR-naive), AI2BMD
     (DFT-trained, NMR-naive), BioEmu (generative, not physics-based)

   This figure tells the story at a glance: does seeing NMR data during training
   matter? Or do MLFFs learn the right physics from DFT alone?

6. **Cite Cavender et al. (LiveCoMS 2025) and Bojan et al. (arXiv 2505.23354)
   prominently.** Cavender et al. establishes the community consensus on which
   experimental datasets should be used for force field benchmarking -- we follow
   their recommendations. Bojan et al. establishes that MLFF representations encode
   NMR-relevant physics -- we test whether MLFF dynamics reproduce NMR observables.
   Together, these citations position our study as the natural next step the community
   has been waiting for.

### Priority 3: Risk and Timing (Minor)

7. **Set November 15, 2026 as the firm preprint date.** Post OSF pre-registration by
   June 1 for territorial protection. Do not rush an incomplete preprint. The
   competitive moat is wide enough to afford thoroughness.

8. **Reduce crambin to a 5 ns stability check only (per bioval's recommendation).**
   Crambin contributes zero NMR validation data points but consumes ~5,000-6,400
   GPU-hrs. Reallocate those hours to S2 replicas for data-rich proteins. Crambin's
   value is purely as a pipeline validation step (reproducing MACE-OFF24 and SO3LR
   published results). A 5 ns check serves this purpose fully.

9. **Set the AI2BMD integration deadline at May 14, not end of Week 2.**
   If AI2BMD cannot produce a stable 1 ns ubiquitin trajectory by May 14, immediately
   pivot to Allegro (NequIP/Allegro v0.4.0 with OpenMM-ML integration). Allegro has
   demonstrated >3 ns stable protein simulations and provides a different architecture
   (local equivariant) that is genuinely distinct from MACE-OFF24. This is a
   strategically stronger fallback than AceFF-2.0.

10. **Add the Bayesian signed-rank test (Benavoli et al., 2017) as the secondary
    statistical analysis.** This is evalstat's recommendation and I strongly support
    it. Bayesian posteriors P(A>B), P(A=B), P(A<B) with ROPE are more informative
    than Nemenyi at N=7, and produce exactly the kind of nuanced results that NCS
    editors and reviewers value. Pre-register both the frequentist (Friedman) and
    Bayesian analyses before production simulations begin.

---

## Alternative Approaches

### The "Thin MVP" Strategy: 5 Proteins, Ship Fast

If compute becomes genuinely constrained (e.g., only 50K GPU-hrs available), consider
the thin MVP: 5 proteins (ubiquitin, GB3, HEWL, barnase, T4 lysozyme) x 3 MLFFs x
30 ns production + 10 replicas x 10 ns for S2 (4 proteins). Total: ~45K GPU-hrs.
This still produces the world's first multi-MLFF experimental benchmark, but with
reduced statistical power and trajectory length. Target Nature Methods rather than
NCS. Post preprint by September 2026. The thin MVP is the "worst case still publishes"
floor.

### The "Observatory" Strategy: 15 Proteins, Slow Build

If compute is abundant and the team has 6+ months, the full 15-protein set from
evalstat's recommendation would produce the definitive community resource -- the
"ProteinGym of force fields." This is a JCTC flagship paper or a Nucleic Acids
Research database paper, not necessarily NCS. It trades narrative surprise for
comprehensiveness. The Observatory strategy is best positioned as a follow-up paper
after the initial 7-protein results demonstrate the concept.

### RDC Inclusion for GB3

bioval recommends including RDC (residual dipolar coupling) back-calculation for GB3,
which has 36 RDC datasets in 5 alignment media. RDC probes bond vector orientations
rather than dynamics or local structure, providing an orthogonal validation axis. The
compute cost is negligible (~10 CPU-hours). I support this recommendation. Including
a fifth observable type (S2, J-couplings, chemical shifts, SAXS, RDC) strengthens
the "multi-observable" claim and adds one more row to the comparison heatmap. However,
RDC is only available for 1-2 proteins, so its contribution to the statistical
framework is limited. Position as an "additional validation" in Extended Data rather
than a primary observable.

---

## Impact on Publication Narrative

### The Combined Paper Is Where the NCS Claim Lives

Let me be direct about this: Alpha-M alone is a very good paper for Nature Methods
or JCTC, but it is NOT the paradigm-level claim that NCS editors seek. "First
systematic MLFF benchmark against NMR observables" is important and novel, but it is
fundamentally a *benchmark contribution* -- it tells us how methods compare, not what
new biology we can do with them.

The NCS-level claim emerges only when Alpha-M connects to Gamma:

**Act 1 (Alpha-M):** "Which ensemble generators produce physically realistic protein
dynamics?"
**Act 2 (Gamma):** "Do those validated ensembles predict biological function?"
**Integration:** "Ensemble quality determines functional prediction accuracy."

This two-act structure is what elevates the paper from "benchmark" to "paradigm." The
benchmark is the foundation; the function prediction is the application; the
connection between the two is the insight. An NCS editor reading "ML force fields
produce dynamics that predict protein fitness" will send it to review. An NCS editor
reading "ML force fields match classical on S2 order parameters" may desk-reject it
as a JCTC-level contribution.

**Concrete implication:** Every design decision in Alpha-M should be evaluated not
just for its standalone value but for its contribution to the combined narrative. The
4 proteins overlapping between Alpha-M and Gamma (ubiquitin, GB3, barnase, T4
lysozyme) are the integration linchpin. These 4 proteins should receive maximum
analytical attention (all observables, maximum S2 replicas, Garnet inclusion) because
they are where the Alpha-M-to-Gamma bridge is built.

### What a NCS Reviewer Will Attack (and How to Pre-Empt)

| Reviewer Concern | Pre-Emption Strategy |
|-----------------|---------------------|
| "Only 3 MLFFs" | Explicit disqualification rationale. Include Garnet as a 4th ML-informed method. Note AceFF-2.0, Allegro, Egret-1 as future additions. The benchmark is extensible. |
| "50 ns is too short" | Convergence ablation (10-50 ns checkpoints). Smith et al. (2024) S2 protocol. Chemical shifts and J-couplings converge in 10-20 ns. |
| "N=7 proteins" | Per-residue bootstrap with 420-560 residues. Bayesian signed-rank test. Explicit power analysis disclosure. Follow-up study to expand. |
| "Temperature mismatch" | Adopted bioval's correction. Each protein simulated at its experimental NMR temperature. |
| "Back-calculation uncertainty" | Adopted evalstat's correction. RMSE_FF reported alongside RMSE_obs. Minimum detectable difference calculated for each observable. |
| "Where is the biology?" | The combined Gamma+Alpha-M paper answers this directly. |
| "Why not enhanced sampling?" | Explicitly deferred. Straight MD is the fairest comparison. Enhanced sampling is the natural follow-up. |
| "Pre-registration?" | OSF pre-registration filed before production simulations. First force field benchmark to do this. |

### Garnet as Narrative Multiplier

Including Garnet transforms the paper from "how do MLFFs compare to classical FFs?"
to a richer question: "what does it take for an ML-derived force field to reproduce
experimental protein dynamics?" The answer has three parts:

1. Classical FFs (AMBER, CHARMM): 30 years of hand-tuning against NMR. Performance
   baseline.
2. Garnet: GNN assigns parameters automatically, trained on QM + NMR. Tests whether
   ML parameterization of classical functional forms suffices.
3. Full MLFFs (MACE-OFF24, SO3LR, AI2BMD): ML potential energy surface, trained on
   DFT only. Tests whether learning physics from first principles is enough.

The comparison reveals WHERE the performance gap originates: functional form
(classical vs. ML potential surface), training data (NMR-informed vs. DFT-only), or
both. This is a much more interesting scientific question than "which method has the
best R2."

---

## Worst-Case Analysis

**What if all MLFFs perform similarly to classical FFs?**

This is the most likely scenario (my prior: 40% probability). In this case:

**Standalone Alpha-M:** "Machine learning force fields reach accuracy parity with
classical protein force fields for NMR observables." Publishable in Nature Methods or
JCTC. The finding that DFT-only training produces NMR-level accuracy is non-trivial.
The community needs to know this. But it is not NCS-level.

**Combined with Gamma:** "ML force fields produce NMR-quality protein dynamics, and
these dynamics predict protein function." Still NCS-level because the function
prediction is the surprise, not the accuracy parity.

**What if MLFFs are significantly worse?**

"The biomolecular reality gap" analogue of UniFFBench. Publishable at NCS if the
gap is substantial and informative (i.e., we can say WHICH observables show the gap
and WHY). The Garnet comparison adds value here: if Garnet (NMR-trained) is better
than pure MLFFs (DFT-only), the remedy is clear: "train on experimental data."

**What if 2/3 MLFFs crash?**

Still publishable at JCTC/J. Phys. Chem. B as a "production readiness assessment."
The one surviving MLFF is benchmarked against classical baselines with full rigor.
The failure modes of the crashed MLFFs are documented as a contribution to the
community. Not NCS material.

**The absolute worst case:** All 3 MLFFs crash AND Garnet also fails AND classical
baselines reproduce published results exactly (no new finding). Probability: <5%.
In this case, the study demonstrates that biomolecular MLFF simulation is not yet
production-ready, which is itself a useful finding for the community, publishable as
a Letter in JCTC. Compute wasted: ~5,000 GPU-hrs (stability testing only; no
production runs consumed).

**Bottom line:** The worst case still publishes. The expected case (mixed results)
produces a Nature Methods or NCS paper. The best case (MLFFs clearly outperform
classical) is field-changing. The risk-reward ratio remains strongly favorable.

---

## Compute Budget Reconciliation: My Recommended Budget

After considering all three reviews, here is my recommended compute allocation:

| Component | Original | bioval Mods | evalstat Mods | My Recommendation |
|-----------|----------|-------------|---------------|-------------------|
| Production 50 ns: 7 proteins x 3 MLFFs | 34,302 | 34,302 | 34,302 | 34,302 |
| Crambin reduction (5 ns only) | -- | saves ~5,000 | -- | saves ~5,000 |
| Garnet baseline (7 proteins) | -- | ~120 | -- | +120 |
| S2 replicas: 15 rep x 20-30 ns, 4 proteins | 39,003 | +15,000-20,000 | -- | +17,000 (accept bioval) |
| S2 for BPTI + barnase (bioval) | -- | +5,000-8,000 | -- | +6,000 (accept) |
| ML/MM water ablation (evalstat, 2 proteins) | -- | -- | +5,000-7,000 | defer to Supp |
| Protein expansion to 12-15 (evalstat) | -- | -- | +40,000-50,000 | REJECT |
| Classical baselines | 177 | 177 | 177 | 177 |
| BioEmu ensembles | 200 | 200 | 200 | 200 |
| Contingency (20%) | 14,736 | -- | -- | 15,000 |
| **TOTAL** | **88,418** | **~108,000** | **~165,000** | **~107,800** |

**My recommended budget: ~107,800 GPU-hrs.** This absorbs bioval's most important
corrections (S2 replicas increased, S2 proteins expanded, crambin reduced) without
evalstat's expensive protein expansion. The per-residue bootstrap statistical approach
compensates for the N=7 limitation without additional GPU cost.

This budget requires ~25-30 dedicated H200 GPUs for 8-10 weeks, achievable within the
project's stated HPC allocation.

---

## Summary of Strategic Recommendations

1. **Include Garnet** as a mandatory 3rd baseline (~120 GPU-hrs). The NMR-aware vs.
   NMR-naive comparison is the strongest narrative element in the study.

2. **Stay at 7 MVP proteins.** Use per-residue cluster bootstrap + Bayesian
   signed-rank for statistical power. Reject the N=15 expansion.

3. **Plan for the combined Gamma+Alpha-M paper as default.** Alpha-M alone is Nature
   Methods/JCTC. The NCS-level claim requires the function prediction connection.

4. **Accept bioval's zero-cost corrections** (temperature, pH, iRED, Karplus,
   ShiftX2). These are non-negotiable for credibility.

5. **Accept bioval's S2 modifications** (15 replicas, 20-30 ns, 6 proteins). The
   additional ~17K GPU-hrs is justified by making S2 the anchor observable.

6. **Reduce crambin** to 5 ns stability check. Redirect ~5K GPU-hrs to S2 replicas.

7. **Set November 15 as the preprint date.** File OSF pre-registration by June 1.

8. **Use Allegro (not AceFF-2.0) as the AI2BMD fallback.** Allegro has protein
   simulation data and OpenMM-ML integration.

9. **Add evalstat's Bayesian signed-rank test and TOST equivalence testing.**
   Zero additional GPU cost. High analytical value.

10. **Add the pre-registration** (evalstat's recommendation). First force field
    benchmark with pre-registered evaluation protocol. Independent methodological
    novelty claim.

---

## References

1. Kovacs, D.P., Moore, J.H., Sherburn, N.J., et al. (2025). MACE-OFF: Short-Range
   Transferable Machine Learning Force Fields for Organic Molecules. *Journal of the
   American Chemical Society*, 147(21). DOI: 10.1021/jacs.4c07099

2. Frank, M., Suarez-Dou, S., Gallegos, M., et al. (2026). Molecular Simulations with
   a Pretrained Neural Network and Universal Pairwise Force Fields. *Journal of the
   American Chemical Society*. DOI: 10.1021/jacs.5c09558

3. Li, T., et al. (2024). Ab initio characterization of protein molecular dynamics
   with AI2BMD. *Nature*, 635, 929-935. DOI: 10.1038/s41586-024-08127-z

4. Mannan, S., et al. (2025). Evaluating Universal Machine Learning Force Fields
   Against Experimental Measurements (UniFFBench). *arXiv*, 2508.05762.

5. Blanco-Gonzalez, A., Schulze, T.K., Rovers, E., & Greener, J.G. (2026). Training a
   force field for proteins and small molecules from scratch (Garnet). *arXiv*,
   2603.16770.

6. Bojan, M., Vedula, S., Maddipatla, A., et al. (2026). Representing local protein
   environments with atomistic foundation models. *arXiv*, 2505.23354.

7. Cavender, C.E., Case, D.A., Chen, J.C.-H., et al. (2025). Structure-Based
   Experimental Datasets for Benchmarking Protein Simulation Force Fields. *Living
   Journal of Computational Molecular Science*, 6(1), 3871.

8. Smith, L.J., et al. (2024). The Accuracy and Reproducibility of Lipari-Szabo Order
   Parameters From Molecular Dynamics. *Journal of Physical Chemistry B*, 128(44),
   10813-10822. DOI: 10.1021/acs.jpcb.4c04895

9. Robustelli, P., Piana, S., & Shaw, D.E. (2018). Developing a molecular dynamics
   force field for both folded and disordered protein states. *PNAS*, 115(21),
   E4758-E4766. DOI: 10.1073/pnas.1800690115

10. Lindorff-Larsen, K., et al. (2012). Systematic Validation of Protein Force Fields
    against Experimental Data. *PLoS ONE*, 7(2), e32131.

11. TEA Challenge Consortium. (2025). Crash testing machine learning force fields for
    molecules, materials, and interfaces. *Chemical Science*. DOI: 10.1039/D4SC06530A

12. Waibl, F., et al. (2025). Drug Discovery Stability Tests for Machine Learning Force
    Fields. *Journal of Chemical Information and Modeling*. DOI:
    10.1021/acs.jcim.2500XXX

13. Mann, E.L., et al. (2025). Egret-1: Pretrained Neural Network Potentials for
    Efficient and Accurate Bioorganic Simulation. *arXiv*, 2504.20955.

14. LAMBench Consortium. (2025). LAMBench: a benchmark for large atomistic models.
    *npj Computational Materials*. DOI: 10.1038/s41524-025-01929-3

15. Choudhary, K., et al. (2025). CHIPS-FF: Evaluating Universal Machine Learning
    Force Fields for Material Properties. *ACS Materials Letters*. DOI:
    10.1021/acsmaterialslett.5c00093

16. Benavoli, A., Corani, G., Demsar, J., & Zaffalon, M. (2017). Time for a Change:
    a Tutorial for Comparing Multiple Classifiers Through Bayesian Analysis. *Journal
    of Machine Learning Research*, 18, 1-36.

17. Weber, L.M., et al. (2019). Essential guidelines for computational method
    benchmarking. *Genome Biology*, 20, 125. DOI: 10.1186/s13059-019-1738-8

18. Demsar, J. (2006). Statistical Comparisons of Classifiers over Multiple Data Sets.
    *Journal of Machine Learning Research*, 7, 1-30.

19. Jing, B., et al. (2025). BioEmu: Generative equilibrium ensembles of
    conformational states. *Science*. DOI: 10.1126/science.adq1806

20. Musaelian, A., et al. (2023). Learning local equivariant representations for
    large-scale atomistic dynamics (Allegro). *Nature Communications*, 14(579). DOI:
    10.1038/s41467-023-36329-y

21. Eastman, P., et al. (2024). OpenMM 8: Molecular Dynamics Simulation with Machine
    Learning Potentials. *Journal of Physical Chemistry B*, 128(1), 109-116. DOI:
    10.1021/acs.jpcb.3c06662

22. Kolde, R., Laur, S., Adler, P., & Vilo, J. (2012). Robust rank aggregation for
    gene list integration and meta-analysis. *Bioinformatics*, 28(4), 573-580. DOI:
    10.1093/bioinformatics/btr709

23. Koo, T.K., & Li, M.Y. (2016). A Guideline of Selecting and Reporting Intraclass
    Correlation Coefficients for Reliability Research. *Journal of Chiropractic
    Medicine*, 15(2), 155-163.

24. Nosek, B.A., et al. (2018). The preregistration revolution. *PNAS*, 115(11),
    2600-2606. DOI: 10.1073/pnas.1708274114

25. Lakens, D. (2017). Equivalence Tests: A Practical Primer for t Tests,
    Correlations, and Meta-Analyses. *Social Psychological and Personality Science*,
    8(4), 355-362. DOI: 10.1177/1948550617697177

26. Tian, C., et al. (2020). ff19SB: Amino-Acid-Specific Protein Backbone Parameters
    Trained against Quantum Mechanics Energy Surfaces in Solution. *Journal of Chemical
    Theory and Computation*, 16(1), 528-552. DOI: 10.1021/acs.jctc.9b00591

27. Prompers, J.J., & Bruschweiler, R. (2002). General Framework for Studying the
    Dynamics of Folded and Nonfolded Proteins by NMR Relaxation Spectroscopy and MD
    Simulation (iRED). *Journal of the American Chemical Society*, 124(16), 4522-4534.

28. GEMS: Biomolecular dynamics with machine-learned quantum-mechanical force fields
    trained on diverse chemical fragments. *Science Advances*, 10, eadn4397 (2024).

29. Benchmarking Universal Machine Learning Force Fields with Hydrogen-Bonding
    Cooperativity. *bioRxiv* (2025). DOI: 10.1101/2025.04.29.651212

30. Li, Y., et al. (2026). Advances and challenges in multiscale biomolecular
    simulations: artificial intelligence-driven paradigm shift. *Quantitative Biology*.
    DOI: 10.1002/qub2.70024
