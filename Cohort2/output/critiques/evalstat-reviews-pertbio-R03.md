---
agent: Evaluation Methodology & Statistical Rigor Expert (evalstat)
round: 3
date: 2026-04-14
type: critique
proposal_reviewed: delta-perturbmark
---

# Critique: PerturbMark -- A Cross-Context Benchmark Resolving the Perturbation Prediction Controversy

## Reviewing Agent

Dr. Evaluation Methodology & Statistical Rigor Expert (evalstat). Senior biostatistician
with 20+ years in experimental design, benchmark methodology, and statistical model
comparison for computational biology. This review examines PerturbMark exclusively from
the **methodology perspective**: whether the metric suite is well-calibrated, whether the
statistical testing framework is rigorous enough for Nature Methods, whether the
cross-context splits are scientifically valid, and whether the proposed power analysis
holds under realistic assumptions. I bring the perspective of a hostile but constructive
Reviewer 2 at Nature Methods who will probe every statistical seam in this benchmark.

## Proposal Summary

PerturbMark proposes a cross-context benchmark on Tahoe-100M (100M cells, 50 cell lines,
379 compounds, CC0) evaluating 10+ perturbation prediction methods across 4 difficulty
tiers (Tier 0--3) using a 7-metric suite with calibrated primaries (WMSE, R^2_w(delta)),
5 mandatory linear baselines, 4 batch effect controls, 5 information leakage prevention
measures, and a pre-specified 5% WMSE improvement threshold. The target is a Nature
Methods preprint by July 15, 2026, following a 6-week sprint.

---

## Overall Assessment

**Verdict:** Support with Modifications

**One-line take:** This is the strongest perturbation benchmark proposal I have seen --
methodologically far superior to scPerturBench -- but it contains several statistical
vulnerabilities that a rigorous Nature Methods reviewer would exploit, all of which are
fixable with the modifications below.

---

## Strengths

1. **Calibrated metric primacy is exactly right.** The proposal correctly identifies
   Miller et al. (2025)'s dynamic range fraction framework and positions WMSE and
   R^2_w(delta) as primaries while retaining MSE for backward compatibility with
   explicit calibration warnings. This is the single most important methodological
   advance over scPerturBench (which used 4 of 6 metrics with documented failure modes).
   The DRF meta-metric for self-validating metric quality is a genuine contribution.

2. **Pre-specified effect size threshold.** The 5% WMSE reduction threshold is the first
   instance of a perturbation benchmark pre-specifying what constitutes a practically
   meaningful improvement. This directly addresses the critique that benchmark papers
   cherry-pick favorable thresholds post hoc. The acknowledgment in Open Question 4 that
   this threshold is "somewhat arbitrary" is honest and appropriate.

3. **Tier 0--3 difficulty hierarchy is well-structured.** The four-tier system maps cleanly
   to increasing degrees of extrapolation (interpolation, perturbation generalization,
   context generalization, full transport). Each tier has a clear definition, and the
   monotonic difficulty gradient provides an internal validity check (Tier 0 > Tier 1 >
   Tier 2 > Tier 3 performance for all methods).

4. **Leakage prevention is comprehensive for a first-generation benchmark.** The five
   leakage types (stereoisomer, target overlap, plate batch, cell line family,
   pre-training contamination) cover the major known risks. The Tanimoto > 0.80 threshold
   for compound grouping and the target-sharing constraint are well-calibrated to known
   medicinal chemistry structure-activity relationships.

5. **Batch effect controls have real teeth.** The four controls -- DMSO-only prediction,
   batch-shuffled null, within-vs-across-plate analysis, and cell-line identity test --
   directly address the confounds identified by Systema (Vinas Torne et al., NatBiotech
   2025). The cell-line identity test is particularly valuable because it quantifies the
   "free" performance that comes from merely knowing which cell type you are predicting,
   independent of perturbation effects.

6. **Mandatory linear baselines are non-negotiable.** Requiring every DL method to beat
   all 5 linear baselines (including the CRISPR-informed mean adapted from Wong et al.,
   2025) before claiming superiority is the correct methodological posture. The inclusion
   of a per-gene ridge baseline (Baseline 5) with cell-line features is particularly
   important because it can generalize to Tier 2--3, unlike the simpler baselines.

7. **Gene set sensitivity analysis.** Reporting results across 4 gene sets (per-condition
   DEGs, union DEGs, HVGs, all expressed genes) directly addresses the critique that
   gene set choice determines conclusions. This is far superior to scPerturBench's single
   gene set approach.

## Weaknesses

### 1. The 7-Metric Suite Has Structural Redundancy and a Missing Primary

The proposal specifies 7 metrics but does not adequately analyze their correlation
structure. Based on the formulas provided:

- **WMSE and R^2_w(delta) will be near-perfectly anti-correlated** when computed on the
  same gene weights. R^2_w(delta) is a variance-explained transform of a weighted sum of
  squared errors. On the same data partition with the same weights, a method that reduces
  WMSE mechanically increases R^2_w(delta). Having both as primaries provides no
  independent information -- it doubles the number of hypothesis tests while adding zero
  additional signal. This is not merely redundant; it inflates the multiple testing
  burden without justification.

- **MSE is a special case of WMSE with uniform weights.** When DRF(MSE) < 0.1 (which the
  proposal anticipates), MSE is already declared unreliable. Retaining it "for backward
  compatibility" still contributes to the multiple testing problem while providing no
  new information beyond what WMSE already captures.

- **The proposal lacks a rank-based primary metric.** My evalstat Round 2 proposal
  specified "Rank correlation on top-k DEGs" (Spearman rho on top 50/100/200 DEGs per
  perturbation) as a Tier 1 primary metric. This is absent from pertbio's 7-metric
  suite. A rank-based metric is critical because it is invariant to monotone
  transformations of predictions and captures whether the model correctly orders genes
  by perturbation effect magnitude, even if it miscalibrates their absolute values. This
  is the metric most directly relevant to downstream use cases (identifying top
  dysregulated genes for target prioritization).

- **Severity:** Major
- **Addressable?** Yes. Designate WMSE as the sole primary metric. Relegate R^2_w(delta)
  to a secondary metric reported for interpretability. Add Spearman rho on top-k DEGs
  as the second primary. This gives two non-redundant primaries: one measuring absolute
  error magnitude (WMSE) and one measuring rank fidelity (Spearman-top-k). This reduces
  the primary metric count from 2 to 2 but eliminates the redundancy.

### 2. BH-FDR Across 120 Correlated Tests Is Insufficiently Conservative

The proposal specifies Benjamini-Hochberg FDR at q = 0.05 across 120 primary tests
(10 methods x 4 tiers x 3 metrics). This is problematic for two reasons:

**Problem A: The tests are not independent.** BH-FDR is proven to control FDR under
independence or positive regression dependency on subsets (PRDS; Benjamini & Yekutieli,
2001). The 120 tests have two strong correlation sources:

- *Same method across tiers:* Tiers 0--3 share training data (Tier 3 test set is the
  intersection of Tier 1 and Tier 2 held-out sets). Performance of the same method at
  Tier 1 and Tier 2 is correlated because both use overlapping training data.
- *Same tier across methods:* All methods are evaluated on the same perturbation-context
  pairs. Their errors are correlated because they share the same data noise structure.

Pfeffer et al. (2025, Genome Biology) demonstrated that BH-FDR can produce
counter-intuitive false positive rates under strong intra-correlations, including
scenarios where nominal FDR = 0.05 yields actual FDR > 0.15 on correlated genomic
datasets with 620,000 unique analysis configurations. The correlation structure in
PerturbMark's 120 tests is structurally similar: nested data partitions and shared
evaluation instances.

**Problem B: The proposal acknowledges this weakness but offers an inadequate fix.**
The proposal (in my evalstat R02 framework, Section 4.5) suggests validating BH with a
synthetic null, which is good but insufficient as a primary correction strategy. The
synthetic null validates that BH is calibrated on *that specific synthetic null*; it
does not guarantee calibration on the real data.

- **Severity:** Major
- **Addressable?** Yes. Adopt a three-tiered correction strategy:

  (1) **Primary analysis:** Benjamini-Yekutieli (BY) procedure, which controls FDR
  under arbitrary dependency at the cost of reduced power. With 120 tests, the BY
  correction factor is sum(1/i, i=1..120) = ~5.19, making the effective threshold
  q_eff = 0.05/5.19 = 0.0096. This is conservative but guarantees FDR control.

  (2) **Sensitivity analysis:** BH-FDR at q = 0.05, reported alongside BY results.
  If BH and BY agree (same tests significant), the conclusion is robust. If they
  disagree, the BY result is primary and the BH result is flagged as "significant
  under FDR but not under arbitrary-dependency FDR."

  (3) **Permutation-based FDR:** Following Westfall & Young (1993), permute method
  labels within each tier (preserving the correlation structure) and compute the
  empirical null distribution of p-values. This directly estimates FDR under the
  actual dependency structure rather than assuming it. Report the number of
  rejections under permutation FDR alongside BY and BH.

  The primary conclusion should be drawn from BY; if BY fails but BH succeeds, the
  result is reported as "suggestive but not robust to dependency correction."

### 3. Organ-Based Cell Line Holdout Introduces a Systematic Confound

The organ-based hold-out for Tier 2--3 (pancreas, skin, haematopoietic, breast+ovary,
CNS) is designed to ensure biological novelty of held-out cell lines. However, this
creates a systematic confound: **tissue-of-origin gene expression programs dominate
perturbation response heterogeneity.**

Cancer cell lines from the same organ share tissue-specific transcription factor
networks, chromatin accessibility patterns, and baseline gene expression programs that
are far larger in effect size than drug-induced perturbation effects. When an entire
organ is held out:

- The model is not merely predicting perturbation effects in an unseen cell line; it is
  predicting perturbation effects in an unseen *tissue context* with a fundamentally
  different baseline transcriptome.
- This conflates two sources of difficulty: (a) generalization to unseen perturbation
  biology and (b) generalization to unseen tissue biology. A model might correctly
  predict the perturbation-specific delta but fail on Tier 2--3 simply because it
  cannot predict the baseline expression of a held-out organ, inflating the apparent
  difficulty.
- The 5 folds are not exchangeable: holding out CNS (3--4 lines) is a fundamentally
  different task than holding out haematopoietic (4--5 lines, suspension culture,
  entirely different growth conditions). Fold-to-fold variance will be driven by which
  organ was held out, not by stochastic variation, making fold-level aggregation
  misleading.

The proposal partially acknowledges this by specifying delta-referenced metrics
(WMSE weights on perturbation effect, not absolute expression). This mitigates but
does not eliminate the confound, because the perturbation effects themselves are
tissue-dependent: the same drug produces different gene-level effects in CNS vs.
pancreatic cells because of tissue-specific pathway wiring.

- **Severity:** Major
- **Addressable?** Yes, with a two-layer design:

  (1) **Primary Tier 2--3 analysis:** Retain the organ-based hold-out as proposed
  (biologically motivated, harder, more interesting).

  (2) **Sensitivity analysis:** Add a random cell-line hold-out (5-fold, ~9--10
  lines per fold, ignoring organ) as a parallel split. Compare method rankings
  between organ-based and random hold-out. If rankings are concordant (Kendall's
  tau > 0.70), the organ-based confound is not driving conclusions. If they diverge,
  report both and discuss whether tissue-of-origin is the primary barrier to
  cross-context prediction (which would itself be a publishable finding).

  (3) **Tissue covariate analysis:** Include tissue-of-origin as a covariate in a
  mixed-effects model predicting WMSE across perturbation-context pairs. Report the
  variance explained by tissue vs. perturbation identity vs. method identity. This
  decomposes the sources of prediction error.

### 4. Power Analysis for Tier 3 Is Marginal and Uses the Wrong Test

The proposal claims adequate power for Tier 3 based on ~190 test conditions per fold
(~950 across 5 folds), citing a paired t-test power calculation for detecting 0.05
Pearson-delta improvement.

**Problem A: Paired t-test is the wrong test.** The proposal itself specifies Wilcoxon
signed-rank tests for method comparison (Section 4.4 of the evalstat framework). Power
calculations for a t-test do not transfer to a Wilcoxon test. The asymptotic relative
efficiency of the Wilcoxon signed-rank test relative to the paired t-test is 3/pi =
0.955 for normal data but can be much lower for heavy-tailed or skewed distributions.
WMSE differences across perturbation-context pairs are likely right-skewed (a few
conditions have very large errors), reducing the effective sample size.

**Problem B: 190 conditions per fold is insufficient for MOA-stratified analysis.**
With 25 MOA categories and ~190 conditions per fold at Tier 3, many MOA categories
will have fewer than 10 test conditions per fold. The proposal acknowledges this
("some MOA categories may have insufficient power") but does not specify a minimum
sample size per MOA stratum.

**Problem C: The power analysis assumes independent test conditions.** In reality,
perturbation-context pairs are not independent: pairs sharing the same cell line (or
the same drug) have correlated prediction errors. The effective sample size is smaller
than the nominal count.

- **Severity:** Major
- **Addressable?** Yes.

  (1) Re-do the power analysis using the Wilcoxon signed-rank test. For detecting
  a shift of 0.20 standard deviations (corresponding to roughly 5% WMSE reduction
  if the coefficient of variation of WMSE across conditions is ~0.25) with 80% power
  at alpha = 0.05, the Wilcoxon test requires approximately n = 265 paired
  observations per comparison (Lehmann, 1975). With ~190 per fold, power drops
  below 70% per fold. Pooling across 5 folds recovers power only if the folds are
  treated as independent, which they are not (shared training data).

  (2) Pre-specify a minimum of 20 conditions per MOA stratum at Tier 3. Any MOA
  category below this threshold is aggregated into "other." Report the number of
  MOA categories meeting the threshold and the fraction of Tier 3 conditions
  they cover.

  (3) For the pooled analysis across folds, use a mixed-effects model with fold
  as a random effect (or use the robust variance estimator from Liang & Zeger,
  1986, GEE) to account for within-fold correlation. Report the effective sample
  size after accounting for intra-fold correlation.

  (4) Acknowledge in the pre-registration that Tier 3 MOA-stratified analysis is
  exploratory, not confirmatory. Only the pooled Tier 3 comparison (all MOAs
  combined) is confirmatory. This is honest and prevents reviewers from attacking
  underpowered subgroup analyses.

### 5. Batch Effect Controls Are Necessary but Insufficient for One Critical Confound

The 4 batch controls are solid for plate-level and processing-level confounds. However,
they miss a critical confound specific to the cell village design: **inter-cell-line
communication artifacts.**

In Tahoe-100M's cell village approach, all 50 cell lines are co-cultured on the same
plate. This eliminates cell-line-level plate batch effects (the claimed advantage) but
introduces a new confound: co-cultured cell lines may influence each other's drug
responses through paracrine signaling, competition for nutrients, or contact inhibition.
A cell line's drug response in a village is not identical to its drug response in
isolation. If the model learns village-specific drug response patterns rather than
cell-autonomous drug responses, its predictions will be biased toward the training
village composition.

None of the 4 controls specifically tests for this. The batch-shuffled null (Control 2)
permutes perturbation labels within plates but preserves the cell village composition,
so it cannot detect village-specific confounds. The within-vs-across-plate analysis
(Control 3) tests plate effects but not village effects (which are plate-constant in a
cell village design).

- **Severity:** Minor (because the cell village confound is intrinsic to Tahoe-100M
  and not fixable without generating new data; however, it should be acknowledged)
- **Addressable?** Partially. Add a fifth control:

  **Control 5: Cross-dataset validation on non-village data.** Validate key findings
  on the Replogle K562 and Norman K562 datasets, which were generated with single
  cell lines in isolation (no village design). If the method ranking on Tahoe-100M
  (village) concordantly reproduces on Replogle/Norman (non-village), the village
  confound is not driving conclusions. Report Kendall's tau between Tahoe-100M and
  Replogle/Norman method rankings as a village-independence check.

  Also add a limitation paragraph explicitly acknowledging the cell village confound
  and its implications for interpreting drug response predictions from Tahoe-100M.

### 6. Information Leakage Prevention Has a Gap: Dose-Level Leakage

The 5 leakage types are comprehensive for compound-level and cell-line-level leakage.
However, they miss **dose-level leakage within compounds.**

Tahoe-100M includes multiple doses per compound. If different doses of the same compound
are split across train and test sets, the model can interpolate between dose levels
rather than predicting the perturbation effect de novo. This is a form of leakage
because knowing the response at 1 uM and 10 uM makes predicting 3 uM trivial for
any smooth dose-response model.

The proposal states that "all doses of a compound [are] in same split" for Tier 1
(perturbation-level split). This is correct and handles the leakage. However, the
constraint is only explicitly stated for Tier 1, not for Tiers 2 and 3. If the
Tier 2--3 splits do not enforce dose-level grouping, dose interpolation leakage
could inflate Tier 2--3 performance estimates.

- **Severity:** Minor
- **Addressable?** Yes. Explicitly state in the split specification for all tiers:
  "All doses of the same compound are assigned to the same split partition in all
  tiers." Add this to the DataSAIL constraint set.

### 7. The 5% WMSE Threshold Lacks Empirical Grounding

The proposal pre-specifies that DL must reduce WMSE by >= 5% relative to the best
linear baseline to be declared "meaningfully better." The evalstat Round 2 framework
(Section 4.6) provides three justifications: (a) below 5%, model complexity is
unjustified; (b) it corresponds to the MDE concept from clinical trials; (c) 1--3%
is within noise.

These justifications are reasonable but **lack empirical calibration against the
actual WMSE scale on Tahoe-100M.** The 5% threshold was set without knowing:

- The absolute WMSE values on Tahoe-100M (which depend on normalization, gene set,
  and the variance of perturbation effects in this specific dataset).
- The between-fold variability of WMSE (which determines whether 5% is large or small
  relative to the noise floor).
- The between-seed variability of WMSE for a given method (which determines whether
  a 5% difference could arise from stochastic optimization rather than model superiority).

If the linear baseline achieves WMSE = 0.50 on Tahoe-100M, a 5% reduction means
WMSE = 0.475 -- a difference of 0.025. If the standard deviation of WMSE across
perturbation-context pairs is 0.20, this is a Cohen's d of 0.125 (negligible).
If the SD is 0.03, the same 5% reduction corresponds to Cohen's d = 0.83 (large).
The meaningfulness of 5% depends entirely on the scale and variability of WMSE
on this specific dataset.

- **Severity:** Major
- **Addressable?** Yes, with a two-phase approach:

  (1) **Phase 1 (pre-registration, before full analysis):** Run the 5 linear baselines
  and the batch-shuffled null on a single fold (Week 2 of the sprint). Compute
  baseline WMSE values and their standard deviation across perturbation-context pairs.
  Use this to calibrate the practical significance threshold. Specifically, set the
  threshold as:

  ```
  Practical significance threshold = max(0.05 * WMSE_linear_best, 2 * SD_across_seeds)
  ```

  This ensures the threshold exceeds both a meaningful fraction of absolute performance
  and the noise floor of stochastic optimization.

  (2) **Phase 2 (pre-registration amendment):** After Phase 1 calibration, amend the
  OSF pre-registration with the empirically calibrated threshold. Document the Phase 1
  data that informed the calibration. This is methodologically clean: the threshold is
  set using baseline-only data (no DL results seen), so it cannot be accused of
  post-hoc manipulation.

  (3) **Report multiple thresholds:** Regardless of the calibrated threshold, also
  report results at 1%, 3%, 5%, and 10% reduction levels. This provides a complete
  picture and lets readers draw their own conclusions.

### 8. Metric Shopping Risk Is Acknowledged but Not Structurally Prevented

With 7 metrics (even if reduced to 5 with the modifications above), there is a
temptation to report whichever metric shows the most favorable result. The proposal
includes a "Metric Disagreement Protocol" (report all, compute rank correlation,
cluster by agreement) but does not specify which metric's conclusion is definitive
when metrics disagree.

The proposal states "Present the primary conclusion from calibrated metrics (WMSE,
R^2_w(delta))" -- but if WMSE and R^2_w(delta) are near-perfectly correlated (as
argued in Weakness 1), this is effectively a single metric. And if that single metric
disagrees with DEG-F1 or MMD, which conclusion prevails?

- **Severity:** Minor
- **Addressable?** Yes. Pre-specify a strict metric hierarchy in the pre-registration:

  (1) **Primary conclusion:** Based on WMSE only (the single best-calibrated metric
  per Miller et al., 2025, and the only metric validated by the WMSE-as-loss-function
  result from Camillo et al., 2025).

  (2) **Secondary conclusion:** If WMSE and Spearman-top-k-DEG (the proposed second
  primary) agree, the conclusion is strengthened. If they disagree, the discrepancy
  is reported prominently and the WMSE conclusion is primary.

  (3) **Exploratory conclusions:** DEG-F1, MMD, and MSE are exploratory. They can
  generate hypotheses but cannot override the primary conclusion.

  This hierarchy must be locked in the pre-registration. If the paper's abstract
  reports a conclusion based on an exploratory metric, that is a pre-registration
  violation.

### 9. The 6-Week Timeline Is Unrealistic for a Reproducible Benchmark

The proposal specifies a 6-week sprint to a July 15 preprint, with Weeks 1--2 for
data and baselines, Weeks 3--4 for 8+ DL methods, Week 5 for analysis, and Week 6
for writing. This timeline has three critical pressure points:

**Pressure point A: DL method debugging.** The proposal assumes 8+ DL methods can be
trained/fine-tuned in 2 weeks. In practice, adapting published methods to a new dataset
(Tahoe-100M) involves resolving dependency conflicts, data format mismatches, undocumented
hyperparameter sensitivities, and out-of-memory errors. scPerturBench (Wei et al., 2026)
benchmarked 27 methods but took approximately 6--9 months from conception to publication.
Even with fewer methods, 2 weeks is insufficient for robust DL evaluation.

**Pressure point B: Reproducibility verification.** Weber et al. (2019, Genome Biology)
established that reproducibility verification -- re-running analyses from a clean
environment -- is essential for benchmark papers. The timeline allocates zero time for
independent reproduction. A reviewer at Nature Methods will ask: "Did anyone other
than the authors successfully reproduce these results?"

**Pressure point C: 7 metrics x 4 tiers x 10 methods x 5 folds x 4 gene sets x 2
normalizations.** The combinatorial explosion of analyses is enormous. Just computing
and validating the metrics is a multi-day effort: 7 * 4 * 10 * 5 * 4 * 2 = 11,200
metric computations (plus batch controls, ablations, and sensitivity analyses). Even
at 10 minutes per metric computation (including validation), this is 1,867 hours of
computation time. Parallelization helps but debugging does not parallelize.

- **Severity:** Major
- **Addressable?** Yes.

  (1) Extend the timeline to 10--12 weeks. Week 1--2: data. Week 3--4: baselines.
  Week 5--8: DL methods (4 weeks, not 2). Week 9--10: analysis and sensitivity.
  Week 11--12: writing, internal review, and reproducibility verification.

  (2) Alternatively, scope down to a "core benchmark" (5 baselines + 3 DL methods:
  CPA, scGPT, and one 2026 model) for the initial preprint. Add additional methods
  in a v1.1 update before journal submission. This preserves speed while maintaining
  rigor.

  (3) Budget 1 week for independent reproduction by a team member who was not involved
  in the primary analysis. This is the minimum for Nature Methods credibility.

---

## Feasibility Assessment

### Technical Feasibility

**High.** The proposal uses well-established tools (scanpy, pertpy, DataSAIL) and
publicly available data. The metric formulas are specified precisely enough for
unambiguous implementation. The compute budget (~1,070 GPU-hrs) is well within the
allocated 1,000--2,000 GPU-hr range. The primary technical risk is the 429 GB data
download and preprocessing at scale, but HuggingFace streaming mode and pre-computed
pseudobulk tables mitigate this.

### Scientific Feasibility

**High with caveats.** The benchmark will produce results regardless of outcome.
The scientific risk is not "will it work?" but "will the results be interpretable?"
The primary interpretability risk is the organ-based hold-out confound (Weakness 3):
if Tier 3 results are dominated by tissue-of-origin effects rather than perturbation
prediction difficulty, the "difficulty tier" narrative collapses. The random hold-out
sensitivity analysis proposed in Weakness 3 is essential for interpretability.

A secondary risk is that the "controversy resolution" framing may be premature. If
calibrated and uncalibrated metrics continue to disagree (DL wins on WMSE, loses on
MSE), the paper resolves nothing -- it merely confirms that the answer depends on the
metric, which is already known. The paper must go beyond this by demonstrating WHY
calibrated metrics are correct (the DRF framework does this) and by identifying the
specific conditions (tier, MOA, cell lineage) under which DL does or does not help.

### Timeline Feasibility

**Low in the 6-week proposal; moderate at 10--12 weeks.** See Weakness 9. The
scPerturBench precedent (27 methods, ~6--9 months) and the Weber et al. (2019)
guidelines for benchmark reproducibility verification both argue for a longer timeline.
The competitive pressure (6--18 month window) justifies urgency but not at the cost
of methodological rigor. A methodologically flawed benchmark is worse than no benchmark.

---

## Suggested Modifications

1. **Reduce primary metrics from 2 to 2 (non-redundant pair).** Designate WMSE as
   the sole error-magnitude primary. Add Spearman rho on top-k DEGs as the rank-fidelity
   primary. Relegate R^2_w(delta) to secondary. This eliminates redundancy while
   preserving information diversity.

2. **Adopt BY-FDR as primary correction; BH-FDR and permutation-FDR as sensitivity.**
   The Benjamini-Yekutieli procedure controls FDR under arbitrary dependency. This is
   essential given the nested correlation structure of 120 tests. Report all three
   correction methods for transparency.

3. **Add random cell-line hold-out as Tier 2--3 sensitivity analysis.** Run the organ-
   based hold-out (proposed) and a random hold-out in parallel. Compare rankings
   between the two. This isolates the tissue-of-origin confound from the perturbation
   generalization challenge.

4. **Re-do power analysis with Wilcoxon assumptions and effective sample sizes.** The
   current t-test-based power calculation overestimates power. Compute effective sample
   sizes accounting for within-fold correlation (via the design effect: DEFF = 1 +
   (n_cluster - 1) * ICC, where n_cluster is the number of pairs per fold and ICC
   is the intra-fold correlation). Report power at the effective sample size.

5. **Calibrate the 5% threshold empirically in Phase 1.** Run baselines on one fold,
   compute WMSE scale and variability, and set the threshold as max(0.05 * WMSE_best,
   2 * SD_seeds). Amend the pre-registration with this calibrated threshold before
   any DL results are analyzed.

6. **Pre-specify a strict metric hierarchy in the pre-registration.** WMSE is primary.
   Spearman-top-k is confirmatory secondary. All other metrics are exploratory. The
   abstract conclusion is determined by WMSE. No exceptions.

7. **Extend timeline to 10--12 weeks or scope down to 3 core DL methods for v1.0.**
   Budget 1 week for independent reproducibility verification. The competitive window
   argument does not justify shipping a methodologically incomplete benchmark.

8. **Add a cell-village confound acknowledgment and cross-dataset concordance check.**
   Compare Tahoe-100M method rankings to Replogle/Norman rankings as a village-
   independence control.

9. **Add dose-level grouping constraint explicitly to all tier split specifications.**
   Currently only explicit for Tier 1.

10. **For Tier 3 MOA-stratified analysis, pre-register it as exploratory** with a
    minimum 20-condition threshold per MOA category. Only the pooled Tier 3 analysis
    is confirmatory.

---

## Alternative Approaches

**Alternative 1: Friedman/Nemenyi framework instead of pairwise Wilcoxon.**

Rather than running 120 pairwise Wilcoxon tests (each DL method vs. best linear baseline),
consider using the Friedman test with Iman-Davenport correction as the global test,
followed by Nemenyi post-hoc for all-pairwise comparisons and Bonferroni-Dunn for
DL-vs-linear control comparisons. This is the approach specified in the evalstat Round 2
proposal for Alpha-M and is the gold standard for multi-method comparison across multiple
datasets (Demsar, 2006, JMLR).

The advantage: a single Friedman test per tier per metric (4 * 2 = 8 tests, not 120)
provides a global statement ("method performance differs significantly across this tier")
before any pairwise comparisons. The Nemenyi post-hoc then identifies which pairs
differ. This dramatically reduces the multiple testing burden while providing the same
information.

The disadvantage: the Friedman test treats perturbation-context pairs as "datasets" and
ranks methods within each pair. This requires computing per-pair method ranks for all
~17,000 (Tier 0) to ~190 (Tier 3) pairs, which is computationally intensive but
feasible. It also requires that each method is evaluated on the same pairs (which the
proposal already ensures).

I recommend using the Friedman/Nemenyi framework as the primary statistical analysis and
the pairwise Wilcoxon tests as a sensitivity analysis. Cite Demsar (2006) and the
evalstat Round 2 proposal for methodological justification. This reduces 120 primary
tests to 8 global tests + targeted post-hoc comparisons with built-in multiplicity
control.

**Alternative 2: Bayesian model comparison as secondary analysis.**

Following Benavoli et al. (2017, JMLR), compute Bayesian signed-rank posteriors for
each method pair. This yields P(DL > linear), P(DL = linear), and P(DL < linear)
rather than binary reject/fail-to-reject. The "rope of practical equivalence" (ROPE)
parameter can be set to the calibrated 5% WMSE threshold, providing a principled way to
distinguish "DL is better," "DL is equivalent," and "DL is worse." This addresses the
frequent reviewer critique that p-values are uninformative about the magnitude and
direction of effects.

---

## Impact on Publication Narrative

### Positive Impacts

PerturbMark is the strongest candidate for a standalone Nature Methods publication among
the three Cohort 2 projects. Its clear framing ("resolving the DL-vs-linear
controversy"), well-defined scope (Tahoe-100M + calibrated metrics + Tier 0--3), and
direct engagement with the ongoing published debate (Ahlmann-Eltze vs. Miller vs.
Dibaeinia) make it editorially compelling. The scPerturBench precedent at the same
journal establishes clear editorial appetite.

### Risks to Narrative

1. **The "no surprise" risk.** If the result confirms what Miller et al. (2025) already
   showed (DL wins on calibrated metrics, loses on uncalibrated metrics), the paper
   becomes "larger-scale confirmation" rather than "controversy resolution." To mitigate
   this, the tier-stratified and MOA-stratified analyses must reveal something new:
   e.g., "DL outperforms at Tier 0--1 but not Tier 2--3," or "DL advantage is
   mechanism-specific (kinase inhibitors: yes, DNA-damaging agents: no)." The proposal's
   richness of stratification makes this likely but not guaranteed.

2. **The "metric determines the answer" meta-narrative.** If calibrated and uncalibrated
   metrics produce opposite conclusions, a cynical reviewer might argue that "the
   controversy is about metric choice, not about DL performance." PerturbMark must
   preempt this by providing rigorous evidence (via DRF) that calibrated metrics are
   objectively superior, not merely different. The DRF calibration data must be
   compelling.

3. **Scope creep undermines the timeline.** With 7 metrics, 4 tiers, 10+ methods, 4
   gene sets, 2 normalizations, 4 batch controls, 5 ablations, and MOA stratification,
   the analysis space is combinatorially explosive. The risk is that the paper becomes
   a 50-page supplement with a 10-page main text that cannot tell a clear story. The
   metric hierarchy (Suggested Modification 6) and the Friedman/Nemenyi framework
   (Alternative Approach 1) both help by imposing analytical discipline.

### Integration with Alpha-M and Gamma

PerturbMark operates independently of the Alpha-M and Gamma projects. There is no
methodological dependency. However, the pre-registration protocol proposed in the
evalstat Round 2 framework covers all three projects jointly. If Delta's pre-registration
is finalized first (which the 6--12 week timeline implies), it serves as a template for
Alpha-M and Gamma pre-registrations. This creates a positive precedent: the first set of
computational biology benchmarks with locked-before-analysis evaluation protocols.

---

## References

1. Benjamini Y, Hochberg Y. "Controlling the false discovery rate: a practical and
   powerful approach to multiple testing." Journal of the Royal Statistical Society
   Series B 57(1): 289--300 (1995).

2. Benjamini Y, Yekutieli D. "The control of the false discovery rate in multiple
   testing under dependency." Annals of Statistics 29(4): 1165--1188 (2001).

3. Benavoli A, Corani G, Demsar J, Zaffalon M. "Time for a change: a tutorial for
   comparing multiple classifiers through Bayesian analysis." Journal of Machine
   Learning Research 18: 1--36 (2017).

4. Demsar J. "Statistical comparisons of classifiers over multiple data sets." Journal
   of Machine Learning Research 7: 1--30 (2006).

5. Pfeffer M, Rade M, Pein F, Boulesteix AL. "Beware of counter-intuitive levels of
   false discoveries in datasets with strong intra-correlations." Genome Biology (2025).

6. Westfall PH, Young SS. *Resampling-Based Multiple Testing: Examples and Methods for
   p-Value Adjustment.* New York: Wiley (1993).

7. Weber LM, Saelens W, Cannoodt R, et al. "Essential guidelines for computational
   method benchmarking." Genome Biology 20: 125 (2019).

8. Lehmann EL. *Nonparametrics: Statistical Methods Based on Ranks.* San Francisco:
   Holden-Day (1975).

9. Liang KY, Zeger SL. "Longitudinal data analysis using generalized linear models."
   Biometrika 73(1): 13--22 (1986).

10. Hummer AM, Blumenthal DB, Kalinina OV. "Data splitting to avoid information leakage
    with DataSAIL." Nature Communications 16: 3337 (2025).
    doi:10.1038/s41467-025-58606-8

11. Miller HE, Mejia GM, Leblanc FJA, et al. "Deep Learning-Based Genetic Perturbation
    Models Do Outperform Uninformative Baselines on Well-Calibrated Metrics." bioRxiv
    (2025). doi:10.1101/2025.10.20.683304

12. Camillo LP, et al. "Diversity by Design: Addressing Mode Collapse Improves scRNA-seq
    Perturbation Modeling on Well-Calibrated Metrics." arXiv:2506.22641 (2025).

13. Dibaeinia P, et al. "Evaluating Single-Cell Perturbation Response Models Is Far from
    Straightforward." bioRxiv (2026). doi:10.64898/2026.02.14.705879

14. Vinas Torne R, Wiatrak M, Piran Z, et al. "Systema: a framework for evaluating
    genetic perturbation response prediction beyond systematic variation." Nature
    Biotechnology (2025).

15. Wei Z, Wang Y, Gao Y, et al. "Benchmarking algorithms for generalizable single-cell
    perturbation response prediction." Nature Methods 23: 451--464 (2026).

16. Niessl C, Herrmann M, Greven S, Boulesteix AL. "Over-optimism in benchmark studies
    and the multiplicity of design and analysis options when interpreting their results."
    WIREs Data Mining and Knowledge Discovery 12(2): e1441 (2022).

17. Nosek BA, Ebersole CR, DeHaven AC, Mellor DT. "The preregistration revolution."
    Proceedings of the National Academy of Sciences 115(11): 2600--2606 (2018).

18. Harrell FE. *Regression Modeling Strategies.* 2nd ed. New York: Springer (2015).

19. Koo TK, Li MY. "A guideline of selecting and reporting intraclass correlation
    coefficients for reliability research." Journal of Chiropractic Medicine 15(2):
    155--163 (2016).

20. Romano J, Kromrey JD, Coraggio J, Skowronek J. "Appropriate statistics for ordinal
    level data: Should we really be using t-test and Cohen's d for evaluating group
    differences on the NSSE and similar surveys?" Annual Meeting of the Florida
    Association of Institutional Research (2006).

21. Phipson B, Smyth GK. "Permutation P-values should never be zero: calculating exact
    P-values when permutations are randomly drawn." Statistical Applications in Genetics
    and Molecular Biology 9(1): Article 39 (2010).

22. Efron B, Tibshirani RJ. *An Introduction to the Bootstrap.* New York: Chapman &
    Hall (1994).

23. Ahlmann-Eltze C, Huber W, Anders S. "Deep-learning-based gene perturbation effect
    prediction does not yet outperform simple linear baselines." Nature Methods (2025).
    doi:10.1038/s41592-025-02772-6

24. Zhang S, Gandhi S, et al. "Tahoe-100M: A Giga-Scale Single-Cell Perturbation Atlas
    for Context-Dependent Gene Function and Cellular Modeling." bioRxiv (2025).
    doi:10.1101/2025.02.20.639398
