---
agent: scopeadv
round: 3
date: 2026-04-14
type: critique
proposal_reviewed: delta-perturbmark
---

# Critique: PerturbMark -- Strategic Assessment of Competitive Positioning, Timeline, and Publication Viability

## Reviewing Agent

Dr. Strategic Scope & Competition Analyst (scopeadv). Former academic researcher,
scientific program director, and journal editor. This review examines PerturbMark
exclusively from the **strategic perspective**: competitive window, narrative
differentiation from scPerturBench and new entrants, timeline realism, venue
selection, preprint strategy, and the "worst case still publishes" test. I
complement evalstat's methodological review (which identified critical statistical
issues) with the editorial and competitive questions that determine whether a
methodologically sound benchmark actually gets published at a top venue.

My perspective: I am the Nature Methods editor deciding whether to send this to
review. I am the reviewer deciding whether "resolving the perturbation prediction
crisis" is a justified claim or editorial overreach. I am the reader in 2027
deciding whether to cite PerturbMark or its competitors.

## Proposal Summary

PerturbMark proposes the first systematic cross-context benchmark for chemical
perturbation prediction on Tahoe-100M (100M cells, 50 cell lines, 379 compounds),
evaluating 10+ methods across 4 difficulty tiers (Tier 0-3) with a calibrated
7-metric suite and 5 mandatory linear baselines. Target: Nature Methods preprint by
July 15, 2026.

---

## Overall Assessment

**Verdict:** Support with Modifications

**One-line take:** PerturbMark occupies a defensible strategic niche -- the neutral,
calibrated, cross-context Tahoe-100M benchmark -- but the competitive window is
narrower than the proposal acknowledges, the 6-week timeline is strategically
reckless, and the differentiation narrative requires sharpening against at least
three new entrants (scPPDM, scDFM, Cole et al.) that the proposal does not
adequately address.

---

## Strengths

1. **The "neutral referee" positioning is strategically excellent.** Every new
   perturbation method (AlphaCell, X-Cell, AetherCell, SCALE, pertTF, scPPDM, scDFM)
   has benchmarked itself against baselines it chose, on splits it designed, using
   metrics that favor its architecture. The field is drowning in self-reported claims.
   PerturbMark's value proposition -- "we evaluate everyone under the same conditions,
   with metrics the field agrees are calibrated" -- is the single most defensible
   editorial pitch for a benchmark paper. This is exactly what Nature Methods
   published scPerturBench for, and exactly what the field needs as the model
   explosion continues. From an editorial standpoint, this positioning is strong.

2. **Tahoe-100M is the right dataset and the timing is right.** Tahoe-100M has been
   downloaded over 250,000 times since its February 2025 release (per the January 2026
   Tahoe/Arc/Biohub partnership announcement). It is the de facto community resource.
   Yet no independent, systematic benchmark exists on it -- scPPDM evaluated one method,
   Tahoe-x1 evaluated one model, and the Virtual Cell Challenge used a different dataset
   entirely (300K CRISPRi cells in H1 hESCs). The first comprehensive, neutral Tahoe-100M
   benchmark is a paper that Nature Methods needs. This is a genuine editorial gap.

3. **The 15-row differentiation table (Section: "Differentiation from scPerturBench")
   is the proposal's strongest strategic asset.** I have reviewed dozens of benchmark
   papers, and the ability to show 10+ specific feature differences in a single table
   is rare. This table alone would survive the "how is this different from scPerturBench?"
   reviewer question, which is the most predictable and dangerous objection. The
   table needs refinement (see Weaknesses), but the concept is sound.

4. **Calibrated metrics resolve an editorial problem, not just a scientific one.**
   Nature Methods published Ahlmann-Eltze et al. (2025) saying DL fails. Miller et al.
   (bioRxiv 2025) responded saying DL succeeds under calibrated metrics. Nature Methods
   then published scPerturBench (2026) using 4 of 6 metrics with known failure modes.
   PerturbMark gives Nature Methods the opportunity to publish a definitive resolution
   that corrects its own prior benchmark -- an editorially attractive proposition.
   Editors like papers that advance the conversation they started.

5. **The kill criteria are well-defined and pre-committed.** Kill criterion 1 ("a
   paper combining Tahoe-100M + Tier 3 + calibrated metrics appears before our
   preprint") is the right trigger. The specificity of this criterion -- not just
   "any Tahoe-100M paper" but the specific combination of Tahoe-100M + Tier 3 +
   calibrated metrics -- is calibrated to exclude partial competitors like scPPDM
   (which lacks Tier 3 and calibrated metrics). This is strategically sophisticated.

6. **The "both outcomes are publishable" structure.** Whether DL wins or loses on
   calibrated metrics at Tier 3, the paper produces a publishable result. If DL
   wins: "the controversy is resolved; DL advantage is real but tier-dependent."
   If DL loses: "even calibrated metrics cannot rescue DL at true cross-context
   prediction." Either way, the Tier 0-3 stratification provides the nuance that
   makes the result interesting regardless of direction. This is the mark of a
   well-designed benchmark.

---

## Weaknesses

### 1. The Competitive Window Is Narrower Than Acknowledged: Three Threats Not Addressed

The proposal identifies scPerturBench follow-up as the primary competitive threat but
underestimates three specific developments that have emerged since Round 1.

**Threat A: scPPDM (arXiv October 2025, ICLR 2026 submission)**

scPPDM is the first paper to systematically benchmark a method on Tahoe-100M with
structured split types (UC: unseen covariate combinations; UD: unseen drugs). It
reports +13-36% improvement over baselines on DEG metrics. My Round 2 strategy
proposal flagged this as a direct threat. The pertbio proposal mentions it in the
method catalog (Priority 3) but does not address it in the competitive analysis.

**Critical point:** scPPDM's Tahoe-100M evaluation, while limited to one method, has
partially filled the "first Tahoe-100M benchmark" gap. PerturbMark can no longer
claim "first benchmark on Tahoe-100M" without qualification. It can claim "first
*comprehensive, multi-method, calibrated-metric* benchmark on Tahoe-100M," but
reviewers will note scPPDM. The differentiation table must include a column for
scPPDM's Tahoe-100M evaluation.

**Threat B: scDFM (ICLR 2026 accepted paper)**

scDFM (Distributional Flow Matching) was accepted at ICLR 2026. It proposes a flow
matching framework for perturbation prediction, reducing MSE by 19.6% over the
strongest baseline in combinatorial settings. The PAD-Transformer architecture is
novel and explicitly addresses gene interaction graphs. scDFM's acceptance at ICLR
2026 means it will have high visibility in the community by the time PerturbMark
posts. PerturbMark should include scDFM in its method catalog if code is released
by May 15, 2026.

**Threat C: Cole et al. (bioRxiv February 2026) -- 600+ model evaluation**

This paper evaluated 600+ models and found that "some foundation models significantly
improve predictions with sufficient data." Its scale (600+ models) dwarfs PerturbMark's
proposed 10+ methods. However, Cole et al. does not use Tahoe-100M, does not use
calibrated metrics (WMSE), and does not define cross-context difficulty tiers.
PerturbMark's depth (Tahoe-100M + calibrated metrics + Tier 0-3) trumps Cole et al.'s
breadth (600+ models on smaller datasets). But reviewers may ask: "Why should we care
about 10 methods when Cole et al. tested 600?" The paper must preempt this by arguing
that depth of evaluation on the right dataset with calibrated metrics is more
informative than breadth of evaluation on smaller datasets with flawed metrics.

- **Severity:** Major
- **Addressable?** Yes.
  1. Add scPPDM's Tahoe-100M evaluation to the differentiation table as a third
     comparison column (scPerturBench | scPPDM Tahoe-100M eval | PerturbMark).
  2. Include scDFM in the Priority 2 method list.
  3. Add a paragraph explicitly addressing Cole et al.'s 600+ model evaluation and
     explaining why PerturbMark's depth-over-breadth approach is the right design.
  4. Update the claim from "first Tahoe-100M benchmark" to "first comprehensive,
     neutral, multi-method benchmark on Tahoe-100M with calibrated metrics and
     cross-context difficulty tiers."

### 2. The 6-Week Timeline Is Not Just Unrealistic -- It Is Strategically Dangerous

evalstat flagged the timeline as unrealistic from a methodological perspective
(DL debugging, reproducibility verification, combinatorial analysis space) and
recommended 10-12 weeks. I agree with evalstat's conclusion but add the strategic
dimension.

**The strategic risk of shipping too fast is worse than shipping too slow.**

A benchmark paper that ships with methodological errors, unreproducible results, or
missing methods will be destroyed in Nature Methods review. The review process at
Nature Methods averages 146 days from submission to acceptance (Academic Accelerator,
2026 data). This means a paper submitted August 1 would not be accepted until roughly
January 2027, with revision cycles. If the benchmark has errors discovered during
review, the revision cycle extends further, and competitors have time to publish
their own benchmarks. A flawed fast preprint is worse than a rigorous slightly-later
preprint.

**Timeline recalculation with evalstat's recommendations incorporated:**

evalstat's modifications add substantial work: random cell-line hold-out sensitivity
analysis (doubles the Tier 2-3 computation), BY-FDR correction (trivial compute but
adds analysis time), Phase 1 threshold calibration (requires completing baselines
before starting DL runs -- this is already in the proposal but the calibration step
adds 2-3 days), Friedman/Nemenyi framework as primary analysis (adds 1-2 days of
implementation and validation), and independent reproducibility verification (1 week
minimum). These additions, combined with the intrinsic complexity of adapting 8+ DL
methods to Tahoe-100M, push the realistic timeline to 10-12 weeks.

**My recommendation:** Target August 15, 2026 for the preprint, not July 15. This
gives 12 weeks from a May 1 start. The competitive window analysis from my Round 2
strategy proposal estimated 3-6 months (scoop probability 35-50% in 3 months). An
August 15 preprint is 3.5 months from now -- still within the window but without the
reckless compression that risks quality.

**NeurIPS 2026 Evaluations & Datasets Track:** The abstract deadline is May 4, 2026
and the full paper deadline is May 6, 2026. PerturbMark could submit to this track
as a dual-submission strategy: post the preprint on bioRxiv in August 2026, and submit
a conference-format version to NeurIPS 2026 E&D Track in May 2027 (for NeurIPS 2027).
However, the May 2026 NeurIPS deadline is in 20 days -- far too soon for PerturbMark.
This is a missed opportunity, but not a critical one; the Nature Methods track is
the correct primary venue.

- **Severity:** Critical
- **Addressable?** Yes.
  1. Move the preprint target from July 15 to August 15, 2026.
  2. Adopt evalstat's 10-12 week timeline framework.
  3. Budget Week 11 for independent reproducibility verification.
  4. Week 12 for writing, internal review, and preprint preparation.
  5. Accept that August 15 is still within the 3-6 month competitive window.
  6. If a competitor posts a Tahoe-100M + calibrated metrics benchmark between now
     and August 15, invoke kill criterion 1 and reassess.

### 3. The Tahoe/Arc/Biohub Partnership Announcement Changes the Strategic Landscape

In January 2026, Tahoe Therapeutics, Arc Institute, and CZ Biohub announced a
partnership to generate a new perturbation dataset that will be "over 4x more
perturbation-rich than Tahoe-100M" (120M+ cells, 225,000 drug-patient interactions).
This dataset will become a centerpiece of the Virtual Cell Challenge, Arc's annual
benchmarking competition.

**Strategic implication 1: Tahoe-100M may be superseded as the community benchmark
within 12-18 months.** If the new Tahoe/Arc/Biohub dataset is released in late 2026
or early 2027, PerturbMark's value as "the Tahoe-100M benchmark" will depreciate.
A new benchmark on the larger dataset will be needed, and PerturbMark's methodology
(Tier 0-3, calibrated metrics, leakage prevention) will be adopted by whoever builds
it.

**Strategic implication 2: The Virtual Cell Challenge may become the de facto community
benchmark.** With 5,000+ registrants in 2025 and institutional backing from Arc,
Tahoe, and Biohub, the Virtual Cell Challenge has the network effects and resources
to establish the community standard for perturbation benchmarking. PerturbMark needs
to position itself as the *scientific complement* to the competition, not a competitor
to it. Competitions optimize for leaderboard performance; PerturbMark optimizes for
scientific understanding (calibrated metrics, difficulty tiers, mechanism-of-action
stratification). These are complementary, and the paper should say so explicitly.

**Strategic implication 3: The new dataset partnership validates PerturbMark's premise.**
The fact that the community's leading data generators and infrastructure providers are
investing in larger perturbation datasets confirms that the field needs better
evaluation infrastructure. PerturbMark on Tahoe-100M is the right benchmark for right
now; the new dataset will need a PerturbMark v2.0.

- **Severity:** Major
- **Addressable?** Yes.
  1. Add a "Future Directions" section acknowledging the Tahoe/Arc/Biohub partnership
     and positioning PerturbMark as the methodology template for future benchmarks.
  2. Design the benchmark code for dataset-agnostic extensibility: Tier 0-3 splits,
     metric computation, and evaluation pipeline should work on any perturbation
     dataset, not just Tahoe-100M.
  3. Frame PerturbMark as "the benchmark for 2026" with explicit acknowledgment that
     larger datasets will emerge. This is honest and makes the contribution clear:
     PerturbMark establishes the *methodology*, Tahoe-100M provides the first
     application.
  4. Reference the Tahoe/Arc/Biohub partnership in the Discussion section as
     validation of the benchmark's premise.

### 4. Venue Selection: Nature Methods vs. Nature Computational Science

The proposal targets Nature Methods as the primary venue, with Nature Computational
Science as an alternative "if findings reveal a surprising computational principle."
This is backward.

**Argument for Nature Methods (pertbio's position):**
- scPerturBench was published in NatMeth (Feb 2026)
- Ahlmann-Eltze et al. was published in NatMeth (2025)
- NatMeth has demonstrated editorial appetite for perturbation benchmarks
- Benchmark papers are a core NatMeth format

**Argument for Nature Computational Science (my counterargument):**
- NatMeth just published scPerturBench in February 2026 -- publishing a second
  perturbation benchmark 6 months later is editorially awkward. Journal editors
  avoid publishing multiple papers on the same topic in quick succession unless the
  second paper is clearly a major advance. PerturbMark is a major advance, but the
  optics of "another perturbation benchmark so soon" are a risk.
- NatCompSci has not published a perturbation benchmark. Being the first gives
  PerturbMark a "first in venue" advantage.
- NatCompSci IF was 27.6 in 2025 vs. NatMeth IF of 32.1. Both are high-impact. But
  NatCompSci publishes fewer papers (more selective), and a benchmark that "resolves
  a computational controversy" fits NatCompSci's scope (computational methods) better
  than NatMeth's scope (biological methods and tools).

**My assessment:** This is a judgment call, not a clear winner. The deciding factor is
the result. If PerturbMark produces a clean "DL wins at Tier 0-1, loses at Tier 2-3"
result (i.e., a surprising computational insight about the limits of generalization),
NatCompSci is the better venue. If the result is primarily a methodology contribution
(calibrated metrics resolve the controversy, here are the rankings), NatMeth is correct.

**Recommendation:** Prepare for both. Write the manuscript with a NatMeth-style
structure (benchmark-first, methodology contribution) but ensure the Discussion
contains a "computational insight" section that could be elevated to the main narrative
for a NatCompSci submission. The decision should be made after results are in, not
before.

- **Severity:** Minor (both venues are strong targets)
- **Addressable?** Yes. Defer venue decision until results are available. Prepare
  a NatMeth-first manuscript with NatCompSci-compatible framing.

### 5. The "Resolving the Perturbation Prediction Crisis" Narrative Is Overreaching

The proposal's framing -- "PerturbMark resolves the perturbation prediction crisis"
-- is editorially risky. A benchmark paper resolves nothing; it provides data. The
crisis is not whether DL beats linear baselines; the crisis is that the field lacks
consensus evaluation standards. PerturbMark can claim to provide the evaluation
standard, but claiming to "resolve" the controversy implies the answer will be
definitive, which it may not be.

**The danger of the "resolution" claim:**
- If calibrated and uncalibrated metrics continue to disagree, reviewers will argue
  PerturbMark confirms what was already known (metric choice determines the answer)
  rather than resolving anything.
- If the Tier 3 results show DL fails even on calibrated metrics, the "resolution"
  is "DL doesn't work for cross-context prediction" -- a negative result that is
  publishable but not a "resolution" in the way the title implies.
- The word "crisis" is inflammatory. The field has a disagreement, not a crisis. Using
  "crisis" in the title invites editorial pushback and reviewer skepticism.

**Better framing options:**
1. "PerturbMark: Calibrated Evaluation of Chemical Perturbation Prediction Across
   Context" -- factual, avoids overclaiming
2. "When Does Deep Learning Help? Cross-Context Perturbation Prediction on 100 Million
   Cells" -- question-driven, more compelling to readers
3. "Beyond Aggregate Accuracy: A Tier-Stratified Benchmark for Chemical Perturbation
   Prediction" -- emphasizes the methodological contribution

I prefer option 2. It makes the reader curious (when does DL help?), it signals the
Tier 0-3 stratification, and it avoids both overclaiming and underselling. The
"100 million cells" number is the attention-grabber. Every computational biologist
will read a paper with "100 million cells" in the title.

- **Severity:** Major
- **Addressable?** Yes. Adopt a question-driven title. Reserve "resolving the
  controversy" language for the Discussion, not the title or abstract. The data
  should speak for itself.

### 6. Preprint Strategy: Immediate Posting Is Correct but Needs a Media Plan

The proposal assumes posting to bioRxiv upon completion. This is correct -- in a
competitive field, preprint-first is essential for establishing priority. But the
proposal lacks a preprint amplification strategy.

**Why this matters:** A preprint without visibility is just a PDF on a server. In the
perturbation prediction field, 8+ preprints posted in March 2026 alone (AlphaCell,
X-Cell, AetherCell, SCALE, pertTF, and others). The signal-to-noise ratio on bioRxiv
is terrible. PerturbMark needs to cut through the noise.

**Recommended amplification:**
1. **Simultaneous code and data release.** The benchmark splits, metric code, and
   evaluation pipeline should be released on GitHub at the exact time the preprint
   posts. This is what gives a benchmark paper adoption power. scPerturBench's
   GitHub repo is what made it the community standard, not just the paper.
2. **Twitter/X thread on the day of posting.** A concise thread highlighting: (a) the
   15-row differentiation table, (b) the Tier 0-3 stratification results (with one
   key figure), (c) the calibrated vs. uncalibrated metric comparison (the "plot
   twist" figure). This is standard practice for high-impact computational biology
   preprints.
3. **Contact scPerturBench authors directly.** Send the preprint to Wei et al. before
   or on the day of posting. Frame PerturbMark as complementary ("we extend your work
   to Tahoe-100M with calibrated metrics"). This increases the probability that
   scPerturBench authors cite PerturbMark rather than view it as a competitor.
4. **Submit to the Virtual Cell Challenge mailing list or forum.** With 5,000+
   registrants, this is the largest community of perturbation prediction practitioners.

- **Severity:** Minor
- **Addressable?** Yes. Add a dissemination plan to the proposal.

### 7. The 15-Row Differentiation Table Needs a Third Column

The scPerturBench vs. PerturbMark comparison table (Section "Differentiation from
scPerturBench") is a strong strategic asset. But it is incomplete. As of April 2026,
the comparison landscape includes at least four relevant benchmarks/evaluations:

| Dimension | scPerturBench (NatMeth 2026) | scPPDM Tahoe eval (ICLR 2026) | Cole et al. (bioRxiv Feb 2026) | PerturbMark |
|-----------|---------------------------|------------------------------|-------------------------------|-------------|
| Primary dataset | 29 scPerturb datasets | Tahoe-100M | Multiple (not Tahoe) | Tahoe-100M |
| Methods tested | 27 | 1 (scPPDM) + baselines | 600+ | 10+ |
| Calibrated metrics | No | No | No | Yes (WMSE, DRF) |
| Tier 3 cross-context | No | UC/UD (partial) | No | Yes (Tier 0-3) |
| Independent/neutral | Yes (benchmark paper) | No (method paper) | Yes (meta-analysis) | Yes (benchmark paper) |
| March 2026 models | No | No | No | Yes |
| Leakage prevention | Minimal | Minimal | Varies | Comprehensive (5 types) |
| Batch controls | No | No | Varies | Yes (4 controls) |

This expanded table makes PerturbMark's differentiation even stronger than the
proposal's 2-column version suggests. PerturbMark is the only entry with all of:
Tahoe-100M + calibrated metrics + Tier 3 + neutrality + March 2026 models + leakage
prevention + batch controls. No competitor has more than 2 of these 7 features.

- **Severity:** Minor
- **Addressable?** Yes. Expand the differentiation table to include scPPDM and
  Cole et al. as comparison columns.

### 8. What If scPerturBench Authors Are Already Working on a Tahoe-100M Follow-Up?

This is the elephant in the room. The bm2-lab (Wei et al.) published scPerturBench
in Nature Methods in February 2026 with 27 methods on 29 datasets. The obvious
follow-up is to extend scPerturBench to Tahoe-100M. They have the codebase, the
evaluation framework, the Nature Methods relationship, and the institutional
credibility. If they post a "scPerturBench v2: Tahoe-100M" preprint before August
2026, PerturbMark's core novelty claim is severely damaged.

**My intelligence assessment (April 14, 2026):**

I searched for evidence of scPerturBench Tahoe-100M activity. I found:
- The bm2-lab GitHub repository (github.com/bm2-lab/scPerturBench) shows no evidence
  of Tahoe-100M integration in the current codebase or README.
- No preprint on bioRxiv from Wei et al. on Tahoe-100M benchmarking.
- No announcements on the scPerturBench reproducibility page or lab website.
- The January 2026 Tahoe/Arc/Biohub partnership announcement focuses on a NEW dataset,
  not benchmarking the existing Tahoe-100M.

**Assessment: LOW-MODERATE risk in the next 4 months.** The scPerturBench team has
not publicly signaled Tahoe-100M follow-up work. However, this is the kind of
obvious next step that a well-resourced lab would pursue without announcing it. The
absence of evidence is not evidence of absence.

**Mitigation:** Speed is the primary mitigation. An August 15 preprint beats the most
likely timeline for a scPerturBench follow-up (which would need to add Tahoe-100M
support to their existing pipeline, rerun 27+ methods, and write up results -- a
minimum 3-4 month effort even with the existing codebase). PerturbMark's secondary
mitigation is the calibrated metrics + Tier 3 + March 2026 models package, which
scPerturBench v2 would need to independently develop.

- **Severity:** Major
- **Addressable?** Yes. Maintain the August 15 preprint target as a hard deadline.
  Monitor bm2-lab GitHub weekly for Tahoe-100M commits. If evidence of scPerturBench
  Tahoe-100M activity appears, accelerate to a "core benchmark" preprint (5 baselines
  + 3 DL methods + Tier 0-3 + WMSE) that can be posted within 2 weeks, with the full
  benchmark following as a v2.

### 9. AlphaCell, AetherCell, and SCALE: The Code Availability Bet

The proposal places AlphaCell, AetherCell, and SCALE in Priority 3 ("include if
code/weights become public by May 15, 2026"). This is correct operationally, but the
strategic implication needs discussion.

**AlphaCell update (April 14, 2026):** The bioRxiv preprint (March 2, 2026) describes
a "World Model" for cellular dynamics. It claims zero-shot cross-context prediction.
No code or weights have been publicly released. The team has not announced a code
release timeline. Given that this is a major proprietary model from a well-funded
group, I estimate <30% probability of code release by May 15.

**Strategic implication of missing AlphaCell/AetherCell/SCALE:** If none of the March
2026 models release code, PerturbMark evaluates CPA, PerturbNet, scGPT, Scouter,
State, Tahoe-x1, and possibly LPM -- methods from 2023-2025, not 2026. The "first
independent evaluation of March 2026 foundation models" selling point collapses.
The paper becomes "a comprehensive benchmark of established methods on Tahoe-100M,"
which is still valuable but less editorially exciting.

**Recommendation:** Split the narrative in advance. The core paper evaluates available
methods under calibrated metrics on Tahoe-100M with Tier 0-3 stratification. This is
the primary contribution. The evaluation of March 2026 models is framed as a "rolling
update" -- new methods will be added to the benchmark as code becomes available, with
updates posted to GitHub and a v1.1 preprint. This framing turns a potential weakness
(missing new models) into a strength (the benchmark is a living resource).

- **Severity:** Moderate
- **Addressable?** Yes. Restructure the narrative to make "living benchmark" the
  core framing rather than "first evaluation of 2026 models."

### 10. The XPert Paper Is a Missed Reference

XPert (Nature Machine Intelligence, January 2026) is a biologically informed
dual-branch transformer for drug-induced perturbation prediction that achieves 36.7%
higher Pearson correlation and 78.2% lower MSE in cold-cell generalization. It
explicitly addresses dose-time dynamics and clinical context transfer. PerturbMark
does not reference or plan to include XPert.

**Strategic relevance:** XPert is published in Nature Machine Intelligence -- a
Springer Nature journal. Including it in PerturbMark would strengthen the
"comprehensive" claim and provide coverage of a method published in a sister journal
to the submission target.

- **Severity:** Minor
- **Addressable?** Yes. Add XPert to the Priority 2 method list. It addresses
  chemical perturbation prediction with dose-time dynamics, making it directly
  relevant to the Tahoe-100M chemical perturbation benchmark. Reference: doi:
  10.1038/s42256-025-01165-w.

---

## Feasibility Assessment

### Technical Feasibility

**HIGH.** The technical feasibility is not in question. Tahoe-100M is publicly
available (CC0, HuggingFace streaming, 250,000+ downloads). The metric formulas are
specified. The linear baselines are implementable in days. The DL methods have
published code (for Priority 1 methods). The compute budget (~1,070 GPU-hrs) is well
within the allocated 1,000-2,000 GPU-hr range and trivial relative to the HPC
cluster's capacity. The primary technical risk -- adapting 8+ DL methods to a new
dataset -- is real but manageable with the extended timeline.

### Scientific Feasibility

**HIGH with the "no surprise" caveat.** The benchmark will produce results regardless
of outcome. The scientific question ("does DL beat linear baselines on calibrated
metrics at each difficulty tier?") has a definite answer. The risk is not that the
experiment fails but that the answer is boring: "DL wins at Tier 0-1, loses at Tier
2-3, and the answer depends on the metric just as Miller et al. already showed." The
Tier 0-3 stratification and MOA-stratified analysis are the insurance against this
outcome -- they will produce publishable nuance even if the headline result is
predictable.

The deeper scientific feasibility question is whether Tahoe-100M's cell village
design creates artifacts that make the benchmark results unreliable. evalstat's
review raised this as a minor concern but correctly noted it is intrinsic to the
dataset and cannot be fixed without new data. The cross-dataset validation on
Replogle/Norman (non-village) is the correct mitigation.

### Timeline Feasibility

**LOW at 6 weeks. MODERATE at 10-12 weeks. HIGH at 14 weeks.**

The 6-week timeline is strategically reckless for three reasons beyond the
methodological concerns evalstat raised:

1. **Nature Methods review precedent.** scPerturBench was submitted approximately
   6-9 months before publication (accepted November 2025, published February 2026,
   implying submission around May-August 2025). This was for a team that already had
   the evaluation pipeline built. PerturbMark has no existing pipeline.

2. **The "one-shot" nature of benchmark preprints.** Unlike method papers, where a
   flawed preprint can be revised, a benchmark preprint that reports wrong rankings
   or uses flawed splits is catastrophic. The field will adopt the rankings from the
   preprint, and corrections posted later will not propagate. The preprint must be
   correct at posting.

3. **Reviewer expectations for reproducibility.** Weber et al. (Genome Biology 2019)
   established that benchmark papers should have independent reproducibility
   verification. Nature Methods reviewers will ask about this. One week of
   independent verification (evalstat's recommendation) is the minimum.

My recommendation: 12-week timeline (May 1 to August 1 preprint, with 2 weeks buffer
to August 15 hard deadline). This incorporates evalstat's extensions while maintaining
the competitive window.

---

## Suggested Modifications

### Priority 1 (Must-do before proceeding)

1. **Move the preprint target from July 15 to August 15, 2026.** The competitive
   window analysis supports this: no evidence of imminent scPerturBench Tahoe-100M
   follow-up, scPPDM is a method paper not a benchmark, and the March 2026 models
   have not released code. August 15 is within the 3-6 month competitive window.

2. **Adopt a 12-week timeline** incorporating evalstat's modifications:
   - Weeks 1-2: Data preprocessing, QC, split construction
   - Weeks 3-4: Linear baselines, Phase 1 threshold calibration
   - Weeks 5-8: DL methods (4 weeks, not 2), including debugging
   - Weeks 9-10: Analysis, sensitivity analyses, ablations
   - Week 11: Independent reproducibility verification
   - Week 12: Writing, figures, preprint preparation

3. **Revise the "resolving the crisis" narrative.** Adopt a question-driven title:
   "When Does Deep Learning Help? Cross-Context Perturbation Prediction on 100 Million
   Cells." Reserve resolution claims for the Discussion.

4. **Update the competitive landscape.** Add scPPDM, scDFM, Cole et al. (600+ models),
   and XPert (NatMachIntell 2026) to the competitive analysis and method catalog.

### Priority 2 (Important for publication success)

5. **Expand the differentiation table to 4 columns:** scPerturBench | scPPDM
   Tahoe eval | Cole et al. | PerturbMark. This strengthens the differentiation
   narrative by showing PerturbMark is the only entry with all key features.

6. **Add a "living benchmark" framing.** The core paper evaluates available methods.
   New methods (AlphaCell, AetherCell, SCALE) are added via GitHub updates and
   v1.1 preprint. This turns missing models from a weakness into a feature.

7. **Defer venue decision until results are in.** Prepare a NatMeth-first manuscript
   with NatCompSci-compatible framing. The result (methodology contribution vs.
   computational insight) determines the venue.

8. **Acknowledge the Tahoe/Arc/Biohub partnership** and position PerturbMark as the
   methodology template for future larger-scale benchmarks.

9. **Add XPert (NatMachIntell 2026) to the method catalog.** It is a chemical
   perturbation method published in a Springer Nature journal with cold-cell
   generalization results.

### Priority 3 (Strengthening measures)

10. **Add a preprint amplification plan.** Simultaneous code release, Twitter thread,
    direct contact with scPerturBench authors, Virtual Cell Challenge community
    outreach.

11. **Prepare a "core benchmark" emergency preprint.** If competitive intelligence
    signals an imminent scPerturBench Tahoe-100M follow-up, a minimal preprint (5
    baselines + 3 DL methods + Tier 0-3 + WMSE) can be posted within 2 weeks, with
    the full benchmark following.

12. **Consider Nature Methods Registered Report format.** Nature Methods offers a
    Registered Report format for benchmark papers where the experimental design and
    analysis plan are peer-reviewed before data collection. Stage 1 submission of
    PerturbMark's evaluation protocol could be submitted quickly, locking the
    methodology and establishing priority before results are in. However, this adds
    administrative complexity and may delay the overall timeline. Assess feasibility
    only if the competitive window lengthens.

---

## Alternative Approaches

### Alternative 1: NeurIPS 2027 Evaluations & Datasets Track as Primary Venue

PerturbMark fits the NeurIPS E&D Track perfectly: it is a benchmark paper with
dataset, code, and evaluation methodology contributions. NeurIPS 2027 would have a
submission deadline around May 2027, giving ample time for a thorough benchmark.
The advantage: NeurIPS E&D papers are highly cited in the ML-for-biology community,
acceptance rates are higher than Nature Methods (8-10%), and the format (8 pages +
unlimited appendix) forces a concise narrative.

**I do NOT recommend this as primary.** NeurIPS lacks the biological audience that
Nature Methods reaches. The perturbation prediction controversy is a biology
debate happening in biology journals. The benchmark should be published where the
debate lives. But NeurIPS E&D could serve as a secondary submission for a
conference-format version, or as a fallback if Nature Methods rejects.

### Alternative 2: Scope Down to "Calibrated Metrics for Perturbation Prediction"

If the competitive window closes (scPerturBench posts Tahoe-100M follow-up), pivot
PerturbMark to a focused methodology paper: "Calibrated Metrics Resolve the
Perturbation Prediction Controversy: WMSE, DRF, and the Case Against MSE." This
paper would:
- Demonstrate the calibrated metric framework on Tahoe-100M (original contribution)
- Show that metric choice determines the DL-vs-linear conclusion (confirmation)
- Provide the metric computation library as a community resource

This is a smaller paper (Nature Methods Brief Communication or Genome Research),
but it is scoop-proof because no competitor is focusing on the calibration methodology
itself. It can be published even if scPerturBench v2 appears, because the
methodological contribution (calibrated metrics on Tahoe-100M) is independent of the
benchmark comprehensiveness.

### Alternative 3: Pre-Register and Fast-Track

Submit a Nature Methods Registered Report (Stage 1) immediately. This locks
PerturbMark's evaluation protocol in the peer review system, establishing dated
priority for the methodology before results are in. Stage 1 reviews the protocol
only; Stage 2 reviews the results. This is the most robust defense against scooping:
even if a competitor publishes a Tahoe-100M benchmark while PerturbMark is in Stage 2
review, the Stage 1 acceptance date proves independent conception.

**Risk:** Stage 1 review adds 2-4 months, pushing the full paper to late 2026. In a
3-6 month competitive window, this delay is dangerous.

**My assessment:** Do not pursue Registered Report unless the competitive window
expands to 9+ months.

---

## Impact on Publication Narrative

### Positive Impacts on the Portfolio

PerturbMark is the fastest path to a first publication from the CompBioSummer2026
portfolio. Its 12-week timeline (May 1 to August 15 preprint) means the team has a
bioRxiv preprint establishing priority before Gamma or Alpha-M are ready. This has
two strategic benefits:

1. **Credibility signal.** A strong benchmark preprint in August 2026 establishes
   the team's credibility and rigor. When the Gamma and Alpha-M preprints follow in
   September-November, reviewers and editors will recognize the team as serious
   contributors.

2. **Methodology template.** The evaluation methodology developed for PerturbMark
   (pre-registration, calibrated metrics, Tier 0-3 stratification, Friedman/Nemenyi
   statistical framework) can be adapted for Alpha-M and Gamma. This creates a
   coherent methodological identity across the portfolio.

### Risks to the Portfolio

1. **Compute contention.** PerturbMark's 1,070 GPU-hrs are trivial, but the 12-week
   timeline overlaps with Alpha-M's launch (which requires 25,000+ GPU-hrs in June).
   Ensure Delta's DL method runs (Weeks 5-8, June) are prioritized on the SLURM
   scheduler before Alpha-M's simulations, or use a separate GPU partition.

2. **Personnel overextension.** A 12-week full-time effort on PerturbMark means the
   team member(s) executing Delta cannot simultaneously contribute to Alpha-M or
   Gamma during May-August. The portfolio plan must account for this.

### The "Worst Case Still Publishes" Test

**Worst case 1: DL methods uniformly beat linear baselines at all tiers.**
Publication: Yes. "Calibrated metrics confirm DL advantage, stratified by tier and
mechanism of action." The Tier 0-3 stratification provides nuance even if the headline
is "DL wins." Nature Methods interest: moderate (confirmation of Miller et al.).

**Worst case 2: DL methods uniformly lose to linear baselines at all tiers.**
Publication: Yes. "Even calibrated metrics cannot rescue DL for chemical perturbation
prediction at any difficulty tier." This is a strong negative result. Nature Methods
interest: high (confirms and extends Ahlmann-Eltze et al. with much more data).

**Worst case 3: Method rankings are unstable across folds (ICC < 0.7).**
Publication: Yes, but reframe as methodology paper. "Perturbation benchmark
reliability is lower than assumed: ranking instability across cross-validation folds
on Tahoe-100M." This is a cautionary contribution to the benchmarking literature.
Target: Genome Biology rather than Nature Methods.

**Worst case 4: scPerturBench publishes Tahoe-100M follow-up before our preprint.**
Publication: Diminished. Fall back to Alternative 2 (calibrated metrics methodology
paper). Or, if PerturbMark has additional features (Tier 3, March 2026 models, batch
controls) that scPerturBench v2 lacks, publish as a "complementary benchmark with
calibrated evaluation." Nature Methods interest: low-moderate (second benchmark on
same dataset). Genome Biology interest: moderate.

**Worst case 5: Key DL methods crash on Tahoe-100M and only 3 DL methods run.**
Publication: Yes. "PerturbMark v1.0: 3 DL methods + 5 baselines on Tahoe-100M."
The Tier 0-3 and calibrated metrics contributions survive regardless of method count.
Add methods in v1.1 as code becomes available.

**All five worst cases produce a publishable paper.** The proposal passes the
worst-case test, though the venue drops from Nature Methods to Genome Biology in
worst cases 3 and 4.

---

## Kill Criteria Evaluation (April 14, 2026)

### Kill Criterion 1: "Tahoe-100M + Tier 3 + calibrated metrics paper appears before our preprint"

**Status: NOT TRIGGERED.** No such paper exists on bioRxiv or arXiv as of April 14,
2026. The closest threat is scPPDM, which evaluates on Tahoe-100M with UC/UD splits
but does not use calibrated metrics (WMSE) or define Tier 3 cross-context. The bm2-lab
GitHub shows no evidence of Tahoe-100M integration. Cole et al. uses 600+ models but
not on Tahoe-100M with calibrated metrics. The kill criterion is intact and the
competitive window remains open.

**Monitoring cadence:** Check bioRxiv, arXiv, and bm2-lab GitHub weekly starting
May 1. If any paper matching the kill criterion appears, invoke emergency assessment
within 48 hours.

### Kill Criterion 2: "Data quality failure (>30% conditions with <30 cells)"

**Status: NOT ASSESSABLE.** Requires Tahoe-100M preprocessing (Week 1-2). The
pre-computed pseudobulk table (4.09B rows on HuggingFace) suggests adequate cell
counts per condition, but this must be verified empirically.

### Kill Criterion 3: "Metric failure (DRF < 0.05 for WMSE and R^2_w(delta))"

**Status: NOT ASSESSABLE.** Requires baseline evaluation (Week 3-4). Miller et al.
(2025) found WMSE well-calibrated on their 14 datasets, but Tahoe-100M is
qualitatively different (larger, chemical perturbations, cell village design). DRF
must be validated on this specific dataset.

### Kill Criterion 4: "Pre-submission feedback concludes insufficient differentiation"

**STATUS: PARTIALLY ASSESSABLE.** The 15-row differentiation table (expanded to
4 columns per Suggested Modification 5) provides strong differentiation. My assessment
as a strategic reviewer: PerturbMark is sufficiently differentiated from scPerturBench
for Nature Methods consideration, provided the calibrated metrics and Tier 3 analysis
deliver meaningful insights. The differentiation is methodological, not just
incremental (bigger dataset, more methods). The calibrated metrics, Tier 0-3
framework, and batch controls are genuine contributions absent from any competitor.

---

## Summary: The Strategic Case for PerturbMark

PerturbMark occupies a defensible niche: the neutral, calibrated, cross-context
benchmark on the community's most important perturbation dataset. Its competitive
advantages (WMSE/DRF calibration, Tier 0-3 hierarchy, batch controls, leakage
prevention, mandatory baselines) are genuine differentiators that no competitor
currently offers. The kill criteria are well-defined, the worst-case outcomes are
publishable, and the field clearly needs this contribution.

The three changes that will make or break this proposal are:

1. **Timeline: Move to 12 weeks.** The 6-week timeline is the single biggest risk to
   the entire project. A methodologically flawed benchmark is worse than no benchmark.

2. **Narrative: Question, not resolution.** "When does DL help?" is stronger than
   "resolving the crisis." Let the data speak.

3. **Competitive awareness: Track the landscape weekly.** scPPDM, scDFM, Cole et al.,
   and the Tahoe/Arc/Biohub partnership change the context. PerturbMark must position
   itself in this updated landscape, not the landscape of February 2026.

With these modifications, PerturbMark has a 65-75% probability of Nature Methods
publication and an 85-90% probability of publication at a high-impact venue (NatMeth,
NatCompSci, or Genome Biology). Without them, the probability drops to 40-50% for
NatMeth (primarily due to timeline-driven quality issues) and 60-70% for any
high-impact venue.

---

## References

1. Wei Z, Wang Y, Gao Y, et al. "Benchmarking algorithms for generalizable
   single-cell perturbation response prediction." Nature Methods 23: 451-464 (2026).
   doi:10.1038/s41592-025-02980-0

2. Ahlmann-Eltze C, Huber W, Anders S. "Deep-learning-based gene perturbation
   effect prediction does not yet outperform simple linear baselines." Nature Methods
   (2025). doi:10.1038/s41592-025-02772-6

3. Miller HE, Mejia GM, Leblanc FJA, et al. "Deep Learning-Based Genetic
   Perturbation Models Do Outperform Uninformative Baselines on Well-Calibrated
   Metrics." bioRxiv (2025). doi:10.1101/2025.10.20.683304

4. scPPDM Team. "scPPDM: A Diffusion Model for Single-Cell Drug-Response
   Prediction." arXiv:2510.11726 (2025). ICLR 2026 submission. Evaluated on
   Tahoe-100M with UC/UD splits, reporting +13-36% over baselines on DEG metrics.

5. scDFM Team. "scDFM: Distributional Flow Matching Model for Robust Single-Cell
   Perturbation Prediction." arXiv:2602.07103 (2026). Accepted at ICLR 2026.
   PAD-Transformer architecture, 19.6% MSE reduction in combinatorial settings.

6. Cole E, Huizing GJ, Addagudi S, et al. "Foundation Models Improve Perturbation
   Response Prediction." bioRxiv (2026). doi:10.64898/2026.02.18.706454. 600+ models
   evaluated; some foundation models significantly improve predictions with sufficient
   data.

7. XPert Team. "Modelling drug-induced cellular perturbation responses with a
   biologically informed dual-branch transformer." Nature Machine Intelligence (2026).
   doi:10.1038/s42256-025-01165-w. 36.7% higher Pearson, 78.2% lower MSE in cold-cell
   generalization.

8. AlphaCell Team. "Towards building a World Model to simulate perturbation-induced
   cellular dynamics by AlphaCell." bioRxiv (2026). doi:10.64898/2026.03.02.709176

9. Xaira Therapeutics. "X-Cell: Scaling Causal Perturbation Prediction Across Diverse
   Cellular Contexts via Diffusion Language Models." bioRxiv (2026).
   doi:10.64898/2026.03.18.712807

10. Zhang S, Gandhi S, et al. "Tahoe-100M: A Giga-Scale Single-Cell Perturbation
    Atlas." bioRxiv (2025). doi:10.1101/2025.02.20.639398

11. Tahoe Therapeutics, Arc Institute, and CZ Biohub. "Partnership to Generate the
    Largest Perturbation Dataset for Virtual Cell Models." Press release, January 12,
    2026. New dataset >4x more perturbation-rich than Tahoe-100M; 120M+ cells,
    225,000 drug-patient interactions.

12. Virtual Cell Challenge Consortium. "Virtual Cell Challenge: Toward a Turing test
    for the virtual cell." Cell (2025). doi:10.1016/j.cell.2025.06.675. 5,000+
    registrants, recurring annual benchmark competition.

13. Arc Institute. "Virtual Cell Challenge 2025 Wrap-Up: Winners and Reflections."
    Arc Institute News, 2025. Over 1,200 teams, 300+ final submissions.

14. Dibaeinia P, et al. "Evaluating Single-Cell Perturbation Response Models Is Far
    from Straightforward." bioRxiv (2026). doi:10.64898/2026.02.14.705879

15. Camillo LP, et al. "Diversity by Design: Addressing Mode Collapse Improves
    scRNA-seq Perturbation Modeling on Well-Calibrated Metrics." arXiv:2506.22641
    (2025).

16. Weber LM, Saelens W, Cannoodt R, et al. "Essential guidelines for computational
    method benchmarking." Genome Biology 20: 125 (2019).

17. Vinas Torne R, Wiatrak M, Piran Z, et al. "Systema: a framework for evaluating
    genetic perturbation response prediction beyond systematic variation." Nature
    Biotechnology (2025).

18. NeurIPS 2026 Evaluations & Datasets Track. Call for Papers. Abstract deadline:
    May 4, 2026. Full paper deadline: May 6, 2026.
    https://neurips.cc/Conferences/2026/CallForEvaluationsDatasets

19. Nature Methods. "Registered Reports." Submission guidelines.
    https://www.nature.com/nmeth/submission-guidelines/registered-reports

20. Academic Accelerator. "Nature Methods Peer-Review Duration." 2026 data. Average
    146 days from submission to editorial acceptance decision.

21. Hummer AM, Blumenthal DB, Kalinina OV. "Data splitting to avoid information
    leakage with DataSAIL." Nature Communications 16: 3337 (2025).

22. Wong DR, Hill AS, Moccia R. "Simple controls exceed best deep learning algorithms
    and reveal foundation model effectiveness for predicting genetic perturbations."
    Bioinformatics 41(6): btaf317 (2025).

23. Gandhi S, et al. "Tahoe-x1: Scaling Perturbation-Trained Single-Cell Foundation
    Models to 3 Billion Parameters." bioRxiv (2025).

24. Miladinovic D, Hoppe P, et al. "In silico biological discovery with large
    perturbation models." Nature Computational Science 5: 1029-1040 (2025).

25. ICLR 2026 Conference. 19,525 submissions; 5,355 accepted (27.4% acceptance rate).
    https://iclr.cc/Conferences/2026

26. Peidli S, et al. "scPerturb: harmonized single-cell perturbation data." Nature
    Methods (2024). doi:10.1038/s41592-023-02144-y

27. Arc Institute. "State: Predicting cellular responses to perturbation across
    diverse contexts." bioRxiv (2025). doi:10.1101/2025.06.26.661135

28. SCALE Team. "SCALE: Scalable Conditional Atlas-Level Endpoint transport for
    virtual cell perturbation prediction." bioRxiv (2026).

29. AetherCell Team. "AetherCell: A generative engine for virtual cell perturbation
    and in vivo drug discovery." bioRxiv (2026).

30. pertTF Team. "pertTF: context-aware AI modeling for genome-scale and cross-system
    perturbation prediction." bioRxiv (2026).
