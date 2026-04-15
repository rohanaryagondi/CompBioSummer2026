---
agent: Strategic Scope & Competition Analyst (scopeadv)
round: 1
date: 2026-04-14
type: research-note
topic: Cross-project competition scan, scoping, publication strategy
---

# Research Note: Cross-Project Competition Scan, Scoping, and Publication Strategy

## Agent

Dr. Strategic Scope & Competition Analyst (scopeadv), Cohort2 Deep Divers. Maverick
track -- former academic researcher, scientific program director, journal editor.
Perspective: editorial + strategic. Papers are evaluated from the vantage of editor,
reviewer, and reader simultaneously.

## Executive Summary

After extensive internet research on April 14, 2026, I have conducted a systematic
competition scan across all three projects (Alpha-M, Gamma, Delta), assessed publication
strategy options, defined minimum viable experiments, constructed realistic timelines,
and built a risk registry with falsifiable kill criteria. My overall assessment:

**Alpha-M (MLFF Crash Test):** Strongest competitive moat of the three. No group has
announced or published a systematic MLFF-vs-experimental-observables benchmark for
biomolecules. The closest precedents are in materials science (CHIPS-FF, UniFFBench,
TEA Challenge 2023), and a 2025 review (Cavender et al.) cataloged the NMR datasets
but did not build the benchmark. The window is wide -- 12-24+ months -- but Microsoft
(AI2BMD), DeepMind (GEMS), and the MACE group (Cambridge) all have the capability to
produce this. The risk is compute cost and timeline, not scooping.

**Gamma (Dynamics-to-Function):** Narrower window but still open. The critical finding
from this scan is that **Microsoft Research is NOT pursuing BioEmu-to-DMS-fitness
mapping** -- their blog (April 2026) focuses on drug design and stability, with no
mention of ProteinGym or mutation effect prediction. SeqDance/ESMDance (PNAS Jan 2026)
uses *implicit* dynamics embeddings, not explicit ensembles -- they are complementary
competitors, not direct threats. The Aryal et al. (IJMS 2026) finding that BioEmu
cannot differentiate driver vs. passenger mutations is a real risk but applies to
*mutation-specific* ensemble generation, not to the wildtype ensemble hypothesis. Window
estimate: **6-12 months**, revised downward from Cohort 1's 6-18 months due to
accelerating activity around BioEmu applications.

**Delta (PerturbMark):** Most crowded competitive landscape, but our specific niche
remains differentiated. The field has exploded since January 2026: X-Cell (March 2026),
AlphaCell (March 2026), AetherCell (March 2026), Scouter (NatCompSci 2026), "Foundation
Models Improve..." (Feb 2026), "Evaluating...Far from Straightforward" (Feb 2026), and
the Arc Institute Virtual Cell Challenge wrap-up. However, NO published work combines
(a) Tahoe-100M with (b) systematic cross-context tiers with (c) calibrated metrics
addressing the DL-vs-baselines controversy. The risk is not that someone does exactly
PerturbMark -- it's that the field resolves the controversy by consensus before we
publish, making our benchmark less impactful. Window: **3-6 months**, urgently
compressed.

**Overall recommendation:** Execute all three in parallel. Delta is the sprinter (submit
by August 2026), Gamma is the middle-distance runner (submit by October 2026), Alpha-M
is the marathon (submit by December 2026). The combined Gamma+Alpha-M paper is the
flagship if both deliver; if Alpha-M compute proves prohibitive, Gamma stands alone.
Delta provides a guaranteed Nature Methods publication regardless of Gamma+Alpha-M
outcomes.

---

## 1. Competition Analysis: Alpha-M (MLFF Biomolecular Crash Test)

### 1.1 Direct Competitor Scan

**Search strategy:** bioRxiv, arXiv, Google Scholar for "MLFF protein benchmark NMR
experimental" (2025-April 2026); lab websites for MACE (Cambridge), AI2BMD (Microsoft),
SO3LR (Basel/Tuckerman), GEMS (DeepMind); NeurIPS/ICML 2026 workshop CFPs.

**Finding: No direct competitor exists as of April 14, 2026.**

The closest works are:

| Work | What It Does | What It Does NOT Do | Gap vs. Alpha-M |
|------|-------------|---------------------|------------------|
| CHIPS-FF (NIST, ACS Mater Lett 2025) | Benchmarks 16 MLFFs on material properties vs experiment | Nothing about proteins or biomolecules | Entire biological domain is missing |
| UniFFBench (arxiv 2508.05762) | Evaluates universal MLFFs vs experimental measurements | Materials only (metals, semiconductors, insulators) | Demonstrates the "reality gap" concept we need for biology |
| TEA Challenge 2023 (Chem Sci 2025) | Crash-tests MLFFs on molecules, materials, interfaces via MD | Only small molecules and materials; no proteins | Shows MLFF MD can break (bond-breaking in kernel-based models) |
| Cavender et al. (LiveCoMS 2025) | Reviews NMR/crystallography datasets for force field benchmarking | Reviews data -- does NOT build a benchmark or test MLFFs | Provides the data roadmap; we provide the benchmark |
| IDPForge (bioRxiv March 2026) | Benchmarks ONE generative model against NMR/SAXS for 32 IDPs | Only IDPs; only one model; not MLFFs; not systematic | Adjacent but different: ensemble generator validation, not FF comparison |
| Ghafouri et al. (NatMeth 2026) | Unified framework for disordered protein ensembles | Framework paper, not benchmark; focuses on IDPs | Provides evaluation methodology context |
| MACE-OFF (JACS 2025) | Shows MACE-OFF23 peptide folding and protein simulation | Benchmarks within paper; not a standalone benchmark | Internal validation, not a community benchmark |
| SO3LR (JACS 2026) | Demonstrates SO3LR on amino acids, peptides, crambin | Benchmarks within paper; not against other MLFFs | Same: internal validation only |
| AI2BMD (Nature 2024) | Protein MD at ab initio accuracy, drug screening | Tests AI2BMD only; no comparison to other MLFFs on NMR | Single-model validation, not cross-model benchmark |

### 1.2 Lab-Specific Threat Assessment

**MACE Group (Cambridge, Csanyi):** Most capable of producing a biomolecular MLFF
benchmark. Published MACE-OFF in JACS 2025 with protein/peptide validation. However,
their focus is on method development (architecture, training), not benchmark curation.
No announcement of a standalone benchmark effort. **Threat level: LOW-MODERATE.**
They could do it in 3-6 months if motivated, but benchmark papers are not their
publication incentive.

**Microsoft Research (AI2BMD):** Published AI2BMD in Nature 2024 with protein
demonstrations. Their recent blog (April 2026) focuses on BioEmu integration for drug
design. No indication of a systematic cross-MLFF benchmark. **Threat level: LOW.** They
have one MLFF (AI2BMD) and little incentive to benchmark competitors.

**DeepMind (GEMS):** Published GEMS in Science Advances 2024. No follow-up indicating
a biomolecular benchmark effort. Their focus appears to have shifted to AlphaFold3
and protein design. **Threat level: LOW.** They are not a benchmarking lab.

**SO3LR Group (Basel/Tuckerman):** Published SO3LR in JACS 2026 with biomolecular
demonstrations including crambin and lipid bilayers. Their paper includes
self-benchmarking but no cross-model comparison. **Threat level: LOW-MODERATE.**
Similar to MACE group -- they develop methods, not benchmarks.

**ANI Group (Isayev):** ANI-2x has been shown to fail at reproducing liquid water
structure (2025 study found it forms amorphous solid). This effectively disqualifies
ANI-2x from a protein benchmark and removes them as competition. **Threat level:
NEGLIGIBLE.**

### 1.3 What Would Make Someone Scoop Alpha-M?

For a genuine scoop, someone would need to:
1. Select 5+ MLFFs for fair comparison
2. Run multi-nanosecond protein simulations with each
3. Back-calculate NMR observables (S2 order parameters, J-couplings, chemical shifts)
4. Compare against BMRB experimental data
5. Include classical FF baselines (AMBER, CHARMM)
6. Write up as a benchmark paper

Estimated time for a well-resourced lab: 6-12 months. The compute requirement
(45K-180K+ GPU-hrs) is the primary barrier. No lab has indicated they are doing this.

### 1.4 Conference Submissions

NeurIPS 2026 abstract deadline: May 4, 2026. ICML 2026: July 6-11 in Seoul, workshops
July 10-11. MLSB 2026 (Machine Learning for Structural Biology): likely co-located with
NeurIPS 2026 in late 2026, no CFP posted yet.

**Assessment:** No workshops have announced MLFF biomolecular benchmark tracks. The TEA
Challenge focused on small molecules and materials. A MLSB 2026 workshop paper could be
a useful companion, but the main publication target should remain Nature Computational
Science.

### 1.5 Alpha-M Competition Summary

| Metric | Assessment |
|--------|-----------|
| Direct competitors | 0 |
| Capable groups | 3-4 (MACE, SO3LR, AI2BMD, GEMS) |
| Active pursuers | 0 known |
| Competition window | 12-24+ months |
| Scoop probability (next 6 months) | <10% |
| Scoop probability (next 12 months) | 15-25% |
| Key differentiator | Neutral third-party benchmark with experimental ground truth |

---

## 2. Competition Analysis: Gamma (Dynamics-to-Function)

### 2.1 Direct Competitor Scan

**Search strategy:** bioRxiv, arXiv, Google Scholar for "BioEmu DMS fitness prediction
mutation ProteinGym 2026"; Microsoft Research publications; Marks Lab (Harvard)
publications.

**Finding: The specific gap remains open, but the adjacent space is filling fast.**

| Work | Relationship to Gamma | Threat Level |
|------|----------------------|-------------|
| SeqDance/ESMDance (PNAS Jan 2026) | PLMs trained on MD-derived dynamics; predict mutation effects from *implicit* dynamic embeddings | COMPLEMENTARY -- uses implicit dynamics, not explicit ensembles. Gamma uses *explicit* BioEmu structures |
| BioEmu Augmented MD (bioRxiv Jan 2026) | Microsoft uses BioEmu + MD to study kinase mutations (CDK2, BRAF V600E) | MODERATE -- same tool, different question. They study mechanism, not quantitative DMS prediction |
| Aryal et al. (IJMS March 2026) | Finds BioEmu fails to differentiate driver/passenger mutations | IMPORTANT CONTEXT -- challenges mutation-specific ensemble generation, but Gamma's wildtype hypothesis circumvents this |
| Mutational Robustness-Dynamics (bioRxiv March 2026) | Shows rho~0.6 between mutational sensitivity and RMSF across ~2,000 proteins | STRONG SUPPORT -- validates that dynamics correlate with fitness; does NOT build a predictive framework |
| Ozkan DCIasym GNN (2025) | Uses MD-derived asymmetric dynamic contact maps for fitness prediction on 4 proteins | PRECURSOR -- 4 proteins is not a benchmark; Gamma does 100+ proteins with BioEmu |
| IDPForge (bioRxiv March 2026) | Ensemble generator for IDPs; benchmarked against NMR/SAXS | ADJACENT -- different tool, different question (ensemble quality vs. function prediction) |
| QDPR (J Phys Chem Lett 2025) | Uses protein-specific MD (not BioEmu) + DMS for conformational sensitivity | PARTIAL OVERLAP -- MD-based, protein-specific, small scale; Gamma is BioEmu-based, general, large scale |

### 2.2 Critical Intelligence: Microsoft Research Is NOT Doing This

The most important finding from my competition scan: Microsoft Research's blog post
"Exploring the structural changes driving protein function with BioEmu-1" (April 2026)
focuses on:
- Drug design and development
- Protein stability prediction
- Understanding protein dynamics for scientific discovery

There is **no mention** of ProteinGym, deep mutational scanning, DMS fitness prediction,
or systematic ensemble-to-function mapping. Their BioEmu augmented MD preprint
(January 2026) studies individual kinases (CDK2, BRAF), not a general framework.

This is strategically significant: the team best positioned to scoop Gamma (they built
BioEmu AND have massive compute) is not pursuing the specific connection between
ensembles and DMS fitness at scale. However, this could change rapidly if they see
our preprint -- a strong argument for the preprint-first strategy.

### 2.3 The Aryal Limitation and the Wildtype Hypothesis

Aryal et al. (IJMS 2026) found that BioEmu "fails to predict a mutation-induced shift
in conformational distribution" and "exhibits a preference for higher-energy
conformations over lower-energy ones." This is a genuine limitation, but it specifically
affects *variant-specific* ensemble generation (sampling the mutant directly with
BioEmu).

Gamma's primary approach is the **wildtype ensemble hypothesis**: extract features from
the wildtype ensemble (RMSF, contact maps, pocket volumes) and correlate these with
DMS fitness scores. This approach does NOT require BioEmu to generate accurate mutant
ensembles -- only accurate wildtype ensembles, which BioEmu does well for globular
proteins (success rates of 55-90% for conformational changes; free-energy errors < 1
kcal/mol).

The ensfunc specialist should design the experiment to test both:
1. Wildtype-only features (robust to Aryal limitation)
2. Variant-specific features (where available; explicitly flagged as speculative)

### 2.4 The SeqDance/ESMDance Question

SeqDance (PNAS Jan 2026) trains protein language models on MD-derived dynamics and
shows improved mutation effect prediction. This is the closest competitor in spirit.

**Key differences from Gamma:**
- SeqDance uses *implicit* dynamics (learned representations from MD data)
- Gamma uses *explicit* structural ensembles (actual 3D conformations from BioEmu)
- SeqDance competes on the ProteinGym leaderboard as a VEP; Gamma asks a scientific
  question about whether explicit dynamics information improves prediction
- SeqDance validates with global ProteinGym correlation; Gamma should stratify by
  protein class, functional mechanism, and dynamic regime

**Strategic implication:** If SeqDance already shows that implicit dynamics improve
prediction, Gamma's contribution is to show that *explicit* structural ensembles
provide additional insight -- identifying WHICH proteins and mutation types benefit
from dynamics, and providing *interpretable* structural features (not just PLM
embeddings). The narrative shifts from "dynamics improves prediction" (SeqDance) to
"explicit ensemble features explain WHY some mutations disrupt function" (Gamma).

### 2.5 Gamma Competition Summary

| Metric | Assessment |
|--------|-----------|
| Direct competitors (exact gap) | 0 |
| Adjacent competitors | 2-3 (SeqDance, QDPR, BioEmu augmented MD) |
| Capable groups | Microsoft Research (BioEmu), Marks Lab (ProteinGym) |
| Active pursuers of exact gap | 0 known |
| Competition window | 6-12 months (revised from Cohort1's 6-18) |
| Scoop probability (next 6 months) | 15-25% |
| Scoop probability (next 12 months) | 35-50% |
| Key differentiator | First systematic mapping of explicit ensembles to DMS fitness at scale |

---

## 3. Competition Analysis: Delta (PerturbMark)

### 3.1 The Explosion of February-March 2026

The perturbation prediction field has undergone an extraordinary burst of activity since
January 2026. The competitive landscape is far more crowded than Cohort 1 assessed:

**New papers since Cohort 1's analysis (Jan-April 2026):**

| Paper | Date | Key Contribution | Relevance to PerturbMark |
|-------|------|------------------|-------------------------|
| BioEmu Augmented MD | Jan 7, 2026 | BioEmu + MD for kinase dynamics | Not directly relevant |
| "Virtual Cells Need Context" | Feb 4, 2026 | Argues context > scale for virtual cells | Conceptual alignment with PerturbMark's cross-context focus |
| "Evaluating...Far from Straightforward" (Dibaeinia et al.) | Feb 14, 2026 | Shows metrics mislead; DL underperforms baselines | DIRECTLY RELEVANT -- parallel analysis of metric failures |
| "Foundation Models Improve..." (Cole et al.) | Feb 18, 2026 | Shows some FMs improve perturbation prediction with 600+ models | DIRECTLY RELEVANT -- largest model comparison to date |
| AlphaCell | March 2, 2026 | Virtual Cell World Model; zero-shot cross-context | NEW METHOD to include |
| AetherCell | March 13, 2026 | Generative engine for virtual cell perturbation | NEW METHOD to include |
| X-Cell (Xaira) | March 18, 2026 | 4.9B parameter diffusion LM; largest perturbation model | NEW METHOD to include (scaled to X-Cell-Ultra) |
| Scouter | NatCompSci 2026 | LLM embeddings for perturbation; halves GEARS error | NEW METHOD to include (peer-reviewed) |

### 3.2 scPerturBench: How Comprehensive Is It Really?

scPerturBench (Wei et al., Nature Methods 2026) is the primary existing benchmark:
- 27 methods evaluated
- 29 datasets
- 6 evaluation metrics
- Genetic AND chemical perturbations

**Gaps that PerturbMark fills:**

1. **No Tahoe-100M:** scPerturBench uses smaller datasets. Tahoe-100M (100M cells,
   429 compounds, 50 cell lines) is the largest perturbation dataset ever produced
   and is entirely untapped for systematic benchmarking.

2. **No explicit cross-context difficulty tiers:** scPerturBench evaluates
   generalization but does not systematically operationalize Tier 0 (same context) to
   Tier 3 (cross-cell-type, cross-compound) difficulty hierarchies. PerturbMark's
   four-tier system is novel.

3. **No metric calibration analysis:** scPerturBench uses standard metrics. It does NOT
   address the Dibaeinia et al. finding that "widely used metrics are strongly
   influenced by scale, sparsity, and dimensionality." PerturbMark incorporates
   calibrated metrics with positive/negative controls.

4. **Missing 2026 methods:** scPerturBench was likely frozen in late 2025 for review.
   It cannot include AlphaCell, AetherCell, X-Cell-Ultra, Scouter, Stack, or State.
   PerturbMark would be the first benchmark to include the March 2026 generation.

5. **No systematic linear baseline suite:** While scPerturBench includes some baselines,
   PerturbMark mandates a comprehensive set: mean control, additive shift, CRISPR-
   informed mean, matrix factorization, ridge regression.

### 3.3 The Arc Institute Virtual Cell Challenge

The Virtual Cell Challenge 2025 results are critical context:
- 5,000+ registrants, 1,200+ teams, 300+ final submissions
- **Key finding: "perturbation prediction models are not yet consistently outperforming
  naive baselines across all metrics"**
- Winning approaches combined DL + classical statistical features
- Arc Institute released State (their own virtual cell model), which improved
  perturbation discrimination by >50%

This validates PerturbMark's premise: the field needs a definitive benchmark because
the current state is confused. However, it also means the Arc Institute community is
actively working on this problem.

### 3.4 Is Anyone Building a Tahoe-100M-Based Cross-Context Benchmark?

**Tahoe Bio themselves:** Released Tahoe-x1 (3B parameter foundation model, October
2025) trained on Tahoe-100M. Their focus is on building the model, not an independent
benchmark. In January 2026, they announced a partnership with Arc Institute and Biohub
for even larger datasets.

**Cole et al. (Feb 2026):** Evaluated 600+ models but on standard datasets, not
specifically Tahoe-100M cross-context splits.

**Dibaeinia et al. (Feb 2026):** Focus on metric calibration across multiple chemical
perturbation datasets, but do not use Tahoe-100M specifically.

**X-Cell (March 2026):** Uses X-Atlas/Pisces (25.6M cells, CRISPRi) as their primary
dataset. Tahoe-100M is mentioned as complementary but not systematically benchmarked.

**Assessment:** No group is building the specific Tahoe-100M cross-context benchmark
that PerturbMark proposes, but the conceptual territory is being filled from multiple
directions simultaneously. **This is the most time-sensitive project.**

### 3.5 The "DL Beats Baselines" Resolution Risk

A peculiar risk for PerturbMark: the controversy may resolve itself before we publish.

- If "Foundation Models Improve..." (Cole et al.) and X-Cell-Ultra's scaling results
  gain wide acceptance, the "DL beats baselines" side may win by consensus.
- If Dibaeinia et al.'s metric calibration analysis is widely adopted, the field may
  agree on proper evaluation practices without needing PerturbMark.
- Either outcome reduces PerturbMark's impact from "resolves a crisis" to "confirms
  what others have shown."

**Mitigation:** Speed. Submit before consensus forms. Target preprint by July 2026.

### 3.6 Delta Competition Summary

| Metric | Assessment |
|--------|-----------|
| Direct competitors | 2-3 (scPerturBench, Dibaeinia et al., Cole et al.) |
| Adjacent competitors | 5+ (X-Cell, AlphaCell, AetherCell, Scouter, State) |
| Capable groups | Numerous (Arc Institute, Tahoe Bio, Xaira, CZI, many academic labs) |
| Active pursuers | Several, but none with exact PerturbMark scope |
| Competition window | 3-6 months (URGENT) |
| Scoop probability (next 3 months) | 20-30% |
| Scoop probability (next 6 months) | 40-55% |
| Key differentiator | Tahoe-100M + cross-context tiers + calibrated metrics + 2026 methods |

---

## 4. Publication Strategy

### 4.1 Combined Gamma+Alpha-M Paper vs. Two Separate Papers

**Option A: Single combined paper ("From Accurate Ensembles to Biological Function")**

Pros:
- Compelling narrative arc: validate ensembles physically (Alpha-M), then show they
  predict function (Gamma)
- Higher impact -- changes how the field thinks about ensemble quality AND utility
- Nature Computational Science strongly favors papers that connect methods to biological
  insight
- Stronger reviewer case: "we don't just show which MLFFs are better; we show WHY it
  matters"

Cons:
- Dependent on both projects delivering -- if Alpha-M compute fails, entire paper stalls
- Longer timeline (Alpha-M is the bottleneck at 10-14 weeks of simulation)
- Larger supplementary materials; risk of "two papers stapled together" reviewer critique
- If the MLFF results are uninteresting (all MLFFs match classical FFs), the combined
  narrative collapses

**Option B: Two separate papers**

Pros:
- Independent timelines -- Gamma can publish months before Alpha-M
- Each paper has a clean, focused narrative
- If one project fails, the other survives
- Gamma alone is a strong Nature Computational Science submission

Cons:
- Lose the combined narrative
- Two review processes (more total effort)
- Neither paper alone has the paradigm-shifting scope of the combined story

**Recommendation: Plan for combined but design for separability.**

Write the combined paper as two clear modules. If Alpha-M delivers on time, submit the
combined version. If not, submit Gamma standalone and Alpha-M as a companion piece in a
methods journal (JCTC, JCIM). The key is to design the experimental pipeline so Gamma
does NOT depend on Alpha-M results -- Gamma uses BioEmu ensembles validated by the
original BioEmu paper, not by our Alpha-M benchmark.

### 4.2 Venue Analysis

**Nature Computational Science:**
- Impact factor: 6.29 (2024). Acceptance rate: ~8-10% estimated.
- Published benchmark papers: yes, but they need to change how people think, not just
  rank methods.
- Recent examples: Scouter (perturbation, 2026), protein engineering tournament (2026).
- Alpha-M + Gamma combined: STRONG FIT. This says "ensemble quality matters for
  function prediction" -- a paradigm-level claim.
- Alpha-M alone: MODERATE FIT. A benchmark alone may be seen as incremental unless the
  "reality gap" finding is dramatic.
- Gamma alone: STRONG FIT. Connecting ensembles to function is a paradigm question.

**Nature Methods:**
- Impact factor: 32.1. Acceptance rate: ~8-10%.
- Strong track record for benchmark papers: scPerturBench (2026), unified ensemble
  framework (2026).
- Delta: STRONG FIT. Resolves an active controversy published in NatMeth itself.
- Alpha-M: MODERATE-STRONG FIT. Methodological benchmark with practical recommendations
  (which MLFF to use for which application).

**Journal of Chemical Theory and Computation (JCTC):**
- Fallback for Alpha-M if Nature venues reject.
- Strong precedent for force field benchmarks and NMR back-calculation papers.

**Recommended venue strategy:**
1. Delta --> Nature Methods (primary) or Nature Computational Science (if DL-beats-baselines
   finding is dramatic and surprising)
2. Gamma + Alpha-M combined --> Nature Computational Science (primary)
3. Alpha-M standalone (if split) --> Nature Methods (primary), JCTC (fallback)
4. Gamma standalone (if split) --> Nature Computational Science (primary)

### 4.3 Preprint Strategy

**Timing is critical.** Preprints serve dual purposes: (1) establishing priority,
(2) attracting attention and citations before peer review.

**Recommended preprint sequence:**

1. **Delta preprint: July 2026.** Post on bioRxiv immediately upon completion of
   analysis. This is the most time-sensitive project. Preprint establishes priority;
   simultaneous submission to Nature Methods.

2. **Gamma preprint: September 2026.** Post after initial results confirm signal. This
   forces any would-be competitors (Microsoft, Marks Lab) to either collaborate or
   differentiate, rather than scoop.

3. **Alpha-M preprint: November 2026.** Post when simulations are complete and
   back-calculations done. If combined with Gamma, post the combined preprint at this
   point.

4. **Combined revision: December 2026-January 2027.** If Gamma and Alpha-M are combined,
   revise the preprint to integrate both components after Alpha-M results.

**Dual-paper strategy:** If all three succeed, the publication portfolio is:
- Paper 1 (fast-track): PerturbMark (Nature Methods, submitted July 2026)
- Paper 2 (flagship): From Accurate Ensembles to Biological Function (Nature Comp Sci,
  submitted November-December 2026)

This gives two high-impact publications from one summer's work.

### 4.4 Nature Computational Science: What Editors Want

Based on analysis of recent NatCompSci publications (2025-2026):

1. **Paradigm questions, not incremental rankings.** The paper should ask "does X
   change how we think about Y?" not "is model A better than model B?"

2. **Biological insight, not just method development.** Every benchmark result should
   connect to a biological implication. "MACE-OFF23 reproduces S2 order parameters
   better than classical FFs" is less interesting than "MACE-OFF23 captures
   millisecond-timescale dynamics that classical FFs miss, revealing hidden
   conformational states relevant to drug binding."

3. **Reproducibility artifacts.** NatCompSci now requires code, data, and environment
   specifications. Plan for this from the start.

4. **Negative results are publishable if framed correctly.** "All MLFFs match classical
   FFs" would be publishable as "the reality gap that exists in materials science does
   not extend to protein dynamics -- here's why."

### 4.5 Nature Methods: What Editors Want for Benchmark Papers

Based on scPerturBench acceptance and similar papers:

1. **Comprehensive coverage.** All major methods, not a cherry-picked subset.
2. **Practical recommendations.** Practitioners should be able to choose a method after
   reading.
3. **Open-source code AND data.** Mandatory. Plan for this.
4. **Approval rate: ~70-75% desk-rejection rate.** The benchmark must be clearly
   methodological, not a biological finding.
5. **Reproducibility.** "If a competent scientist cannot reproduce your results from
   what you have provided, it will not survive review" (NatMeth submission guidelines).

---

## 5. Scoping Recommendations

### 5.1 Alpha-M Minimum Viable Product (MVP)

**The question:** What is the minimum protein/MLFF/simulation-length combination for a
convincing benchmark paper?

**MVP specification:**

| Parameter | MVP | Full Benchmark | Rationale |
|-----------|-----|---------------|-----------|
| MLFFs tested | 3 (MACE-OFF24(M), SO3LR, AI2BMD) | 5 (add AceFF-2.0, Allegro) | 3 covers the major architectures; 5 is comprehensive |
| Classical baselines | 2 (AMBER ff19SB, CHARMM36m) | 2 (same) | These are the community standards |
| Proteins | 7 | 15 | See protein selection criteria below |
| Simulation length | 50 ns per system | 100 ns per system | S2 order parameters converge at ~20-50 ns with 10+ replicas |
| Replicas | 10 per system | 20 per system | Required for S2 convergence statistics |
| NMR observables | S2 order parameters, 3J HNHa couplings | Add chemical shifts, RDCs, SAXS | S2 and J-couplings are the most discriminating |
| Compute (GPU-hrs) | ~42,000-63,000 | ~225,000-375,000 | MVP is achievable in 6-8 weeks on HPC |

**Protein selection criteria for MVP (7 proteins):**
1. Ubiquitin (1UBQ): Gold standard, extensive NMR data, 76 residues
2. GB3 (2OED): Well-characterized dynamics, 56 residues
3. BPTI (5PTI): Classical FF benchmark protein, 58 residues
4. Lysozyme (1AKI): Medium size, 129 residues
5. Crambin (1CRN): Small, well-folded, used by GEMS/SO3LR
6. Protein L (1HZ6): Beta-sheet rich, 64 residues
7. Calmodulin (1CLL): Domain motion, flexibility, 148 residues

**What can be cut without losing the main claim:**
- Can drop to 3 MLFFs + 2 classical FFs for MVP
- Can reduce to 7 proteins (vs. 15 full)
- Can reduce simulation length to 50 ns if replicas are sufficient
- CANNOT cut S2 order parameters (most discriminating observable)
- CANNOT cut classical FF baselines (the whole point is MLFF vs classical comparison)

### 5.2 Gamma Minimum Viable Product (MVP)

**The question:** How many ProteinGym proteins are needed for a credible claim that
ensemble features predict DMS fitness?

**MVP specification:**

| Parameter | MVP | Full Benchmark | Rationale |
|-----------|-----|---------------|-----------|
| ProteinGym proteins | 50 (with PDB structures) | 150+ | 50 is enough for statistical power; 150+ is comprehensive |
| BioEmu conformations per protein | 100 per WT | 500 per WT | Ensemble convergence at ~100 for RMSF/contacts |
| Ensemble features | 5 core (RMSF, contact maps, Rg, solvent exposure, hinge motions) | 15+ (add pocket volume, correlated motions, etc.) | Core features have the strongest prior evidence |
| ML models | 3 (ridge regression, random forest, MLP) | 5+ (add GNN, attention-based) | Ridge is the sanity check; RF/MLP capture nonlinearity |
| Baselines | 3 (ESM-1v, AlphaMissense, EVE zero-shot) | 5+ (add MSA Transformer, Tranception) | These are the standard sequence/structure VEPs |
| Evaluation | 10-fold CV, stratified by protein | + temporal holdout, leave-protein-out | CV is minimum; temporal holdout for NatCompSci |
| Compute (GPU-hrs) | ~2,000 (BioEmu sampling) + ~200 (ML) | ~8,000 + ~500 | 50 proteins x 100 conformations x ~40 GPU-min/protein |

**Critical success criterion:** Ensemble features must add statistically significant
predictive power BEYOND sequence-only methods for at least a meaningful subset of
proteins. A blanket negative ("dynamics never helps") kills the paper. A stratified
positive ("dynamics helps for X-type proteins but not Y-type") is publishable and
arguably more interesting.

**What can be cut:**
- Can reduce to 50 proteins (from 150+) for MVP
- Can use 100 conformations per protein (vs. 500)
- Can use 5 core features (vs. 15)
- CANNOT cut ESM-1v baseline (the standard bearer)
- CANNOT cut protein stratification (the key insight is WHICH proteins benefit)

### 5.3 Delta Minimum Viable Product (MVP)

**The question:** Beyond Tahoe-100M, which other datasets are essential?

**MVP specification:**

| Parameter | MVP | Full Benchmark | Rationale |
|-----------|-----|---------------|-----------|
| Primary dataset | Tahoe-100M (chemical, 50 cell lines) | Same | Anchor dataset; defines cross-context tiers |
| Secondary datasets | Replogle 2022 (genetic), Norman 2019 (genetic) | + X-Atlas, scPerturb collection, Adamson 2016 | Chemical + genetic perturbation coverage |
| Methods benchmarked | 10 core (GEARS, CPA, scGPT, X-Cell, AlphaCell, Scouter, SCALE, PerturbNet, Ridge, Mean) | 15+ (add AetherCell, State, Stack, pertTF, Tahoe-x1) | 10 covers the major categories |
| Linear baselines | 4 (mean control, additive shift, ridge, matrix factorization) | 5 (add CRISPR-informed mean) | Mandatory for DL-vs-baselines comparison |
| Cross-context tiers | 4 (Tier 0-3) | 4 (same) | This IS the differentiation |
| Metrics | 6 calibrated (with positive/negative controls) | 8+ (add distributional metrics) | Must include Miller et al. calibration framework |
| Compute (GPU-hrs) | 1,000 | 2,000 | Method-agnostic; mostly data processing |

**What can be cut:**
- Can start with Tahoe-100M only (add Replogle/Norman in revision)
- Can reduce to 10 methods (vs. 15)
- CANNOT cut linear baselines (defeats the purpose)
- CANNOT cut Tier 3 cross-context (this is the unique contribution)
- CANNOT cut metric calibration (differentiates from scPerturBench)

### 5.4 Realistic Timeline: All Three Projects in Parallel (May-December 2026)

```
May 2026      June 2026      July 2026      Aug 2026       Sep 2026       Oct 2026       Nov 2026       Dec 2026
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
DELTA:
[Data download/preprocess]
                [Method runs (10 models, Tahoe-100M splits)]
                              [Analysis, metric calibration]
                                            [Write-up + preprint]
                                                          [NatMeth submission]
                                                                         [Revisions if needed]

GAMMA:
[BioEmu pipeline setup]
[Protein selection + PDB curation]
                [BioEmu sampling: 50 proteins x 100 conformations]
                              [Feature extraction + ML training]
                                            [Evaluation + stratification analysis]
                                                          [Write-up + preprint]
                                                                         [If standalone: NatCompSci submit]

ALPHA-M:
[Protocol design + validation on 1 protein]
                [MVP simulations: 7 proteins x 3 MLFFs x 50 ns x 10 replicas]
                              [Continue simulations...]
                                            [NMR back-calculation pipeline]
                                                          [Analysis + comparison]
                                                                         [Write-up + preprint]
                                                                                               [Combined w/ Gamma: NatCompSci submit]
```

**Critical path constraints:**
- Delta is compute-light; bottleneck is method availability (can all 10 methods run?)
- Gamma is BioEmu-bottlenecked; ~2,000 GPU-hrs for sampling
- Alpha-M is heavily compute-bottlenecked; 42K-63K GPU-hrs minimum
- Personnel: assumes 2-3 people full-time across all three projects

**Key decision points:**
- **May 30:** Alpha-M validation run on ubiquitin complete. Go/no-go for full MVP.
- **June 30:** Gamma BioEmu sampling complete for 50 proteins. Preliminary signal check.
- **July 15:** Delta analysis complete. Preprint decision.
- **August 30:** Alpha-M MVP simulations complete. Back-calculation begins.
- **September 30:** Gamma evaluation complete. Standalone vs. combined decision.
- **November 30:** Alpha-M analysis complete. Combined paper decision.

---

## 6. Risk Registry

### 6.1 Alpha-M: Top 5 Risks

| # | Risk | Probability | Impact | Mitigation |
|---|------|-------------|--------|-----------|
| 1 | MLFF instability at protein timescales (bond-breaking, energy drift) | 30% | HIGH | Pre-screen each MLFF on ubiquitin for 10 ns before committing to full benchmark. Adopt TEA Challenge diagnostic framework. |
| 2 | Compute overrun (simulations take 2x longer than estimated) | 25% | HIGH | Start with 7-protein MVP. Parallelize across multiple GPU types (H200, RTX 5000 Ada). Budget 30% contingency. |
| 3 | All MLFFs match classical FFs (no "reality gap") | 20% | MODERATE | Still publishable: "the reality gap that exists in materials science does not extend to proteins" is a novel finding. Reframe as positive for MLFF adoption. |
| 4 | NMR back-calculation pipeline errors systematically bias results | 15% | HIGH | Validate SPARTA+, Karplus equations against published AMBER/CHARMM benchmarks first. Use multiple back-calculation tools for cross-validation. |
| 5 | Scooped by MACE or SO3LR group publishing a protein MLFF benchmark | 10% | VERY HIGH | Speed. Start May 2026. Post preprint as soon as MVP results are analyzable (~October 2026). |

### 6.2 Gamma: Top 5 Risks

| # | Risk | Probability | Impact | Mitigation |
|---|------|-------------|--------|-----------|
| 1 | BioEmu ensembles show NO signal for DMS fitness prediction | 25% | VERY HIGH | Kill criterion. But first check: stratify by protein type. Signal may exist for flexible proteins but not rigid ones. Even a negative result ("which proteins DON'T benefit from dynamics") is publishable if framed correctly. |
| 2 | Microsoft Research publishes BioEmu-to-fitness mapping | 15% | VERY HIGH | Speed + differentiation. Post preprint September 2026. If MS publishes first, reframe as independent confirmation with different methodology. |
| 3 | ESMDance/SeqDance shows dynamics improve prediction, making Gamma incremental | 20% | MODERATE | Frame Gamma as the *structural explanation* for SeqDance's finding. "SeqDance showed dynamics matter implicitly; we show explicitly which structural features drive the improvement." |
| 4 | ProteinGym proteins with PDB structures are biased toward well-studied proteins | 30% | LOW-MODERATE | Acknowledge in paper. Compare ProteinGym-with-PDB vs. ProteinGym-without-PDB characteristics. Argue this is a necessary limitation of any structure-based approach. |
| 5 | BioEmu ensemble quality is poor for a significant fraction of ProteinGym proteins | 20% | MODERATE | Pre-screen: run BioEmu on all candidate proteins, check Rg distribution against experimental values. Exclude proteins where BioEmu fails obvious quality checks. Report failure rate transparently. |

### 6.3 Delta: Top 5 Risks

| # | Risk | Probability | Impact | Mitigation |
|---|------|-------------|--------|-----------|
| 1 | Another group publishes Tahoe-100M cross-context benchmark before us | 25% | VERY HIGH | Speed. Target preprint by July 2026. Start immediately. |
| 2 | DL methods DO beat linear baselines convincingly on Tahoe-100M | 40% | LOW | This is actually a GOOD outcome for the paper. "DL exceeds baselines, but only at Tier 3 with sufficient training data" is a nuanced, publishable finding. |
| 3 | Method reproducibility failures (published code doesn't run on Tahoe-100M) | 35% | MODERATE | Start early method installation. Contact authors. Budget 2-3 weeks for engineering. Use containerized environments. |
| 4 | Tahoe-100M data quality issues (batch effects, confounders) | 15% | MODERATE | Extensive QC pipeline. Compare to published Tahoe Bio analysis. Flag any issues transparently. |
| 5 | The DL-vs-baselines controversy resolves by consensus before publication | 20% | HIGH | Preprint ASAP. Even if consensus forms, PerturbMark adds value as the definitive dataset-specific test. |

### 6.4 Kill Criteria (Pre-Specifiable, Falsifiable)

**Alpha-M kill criteria:**
- KILL if: 2/3 Tier 1 MLFFs fail stability tests on ubiquitin within 10 ns (assessed by
  May 30, 2026)
- KILL if: Total compute exceeds 100K GPU-hrs for MVP with no path to completion by
  November 2026
- PIVOT if: All MLFFs match classical FFs (reframe as "no reality gap" finding, target
  JCTC instead of NatCompSci)

**Gamma kill criteria:**
- KILL if: BioEmu fails to generate reasonable ensembles (Rg within 20% of experimental)
  for >50% of candidate proteins (assessed by June 30, 2026)
- KILL if: No ensemble feature adds statistically significant predictive power (p > 0.05
  after Bonferroni correction) beyond ESM-1v for ANY protein subset (assessed by
  August 30, 2026)
- PIVOT if: Signal exists for only 5-10 proteins (publish as case study in Bioinformatics
  or PLOS Comp Bio instead of NatCompSci)

**Delta kill criteria:**
- KILL if: Tahoe-100M proves inaccessible or corrupted (assessed by May 15, 2026)
- KILL if: Fewer than 6 of 10 target methods can be run reproducibly on Tahoe-100M
  (assessed by June 15, 2026)
- PIVOT if: Results match scPerturBench exactly with no new insight (add novel metric
  calibration analysis as primary contribution, reframe for Genome Biology or
  Bioinformatics)

### 6.5 "Worst Case Still Publishes" Analysis

**Alpha-M worst case:** All MLFFs match classical FFs. S2 correlations are similar.
No "reality gap."
- **Still publishes?** YES, but not in NatCompSci. A systematic "no reality gap"
  finding for proteins is novel and publishable in JCTC or J. Phys. Chem. Lett.
  It would be the first evidence that the materials science reality gap does NOT
  generalize to biomolecules. Frame: "Good news for MLFF adoption -- but not for
  biomolecular accuracy improvement."

**Gamma worst case:** No ensemble feature adds predictive power beyond ESM-1v for any
protein subset.
- **Still publishes?** CONDITIONALLY. A negative result ("explicit dynamics don't improve
  DMS prediction") is publishable ONLY if the analysis is rigorous and the protein set
  is sufficiently large and diverse. Target: PLOS Computational Biology or Bioinformatics.
  Frame: "Sequence-based methods already capture the dynamics-relevant information
  implicitly." This is actually an important finding, but not NatCompSci-level unless
  the analysis is exceptionally thorough and unexpected.

**Delta worst case:** Results match scPerturBench -- DL fails on standard metrics, DL
wins on calibrated metrics, same conclusions.
- **Still publishes?** YES. Even confirming scPerturBench's findings on the 10x-larger
  Tahoe-100M dataset with the cross-context tier framework adds significant value. The
  Tahoe-100M analysis alone is novel. Target: Nature Methods (if sufficiently
  differentiated) or Genome Biology (fallback).

### 6.6 Scenario Analysis: Key "What If" Questions

**What if BioEmu ensembles show NO signal for function prediction?**
- This triggers the Gamma kill criterion at August 30, 2026.
- Before killing: check stratification (flexible vs. rigid proteins, enzymatic vs.
  binding vs. stability assays). The signal may be protein-class-specific.
- If confirmed negative across all strata: publish as negative result (PLOS Comp Bio).
  Allocate freed resources to Alpha-M and Delta.
- Impact on combined paper: Alpha-M proceeds independently, targets Nature Methods or
  JCTC as a standalone MLFF benchmark.

**What if ALL MLFFs match classical FFs (no "reality gap")?**
- This triggers the Alpha-M pivot criterion.
- Reframe: "Classical force fields are already sufficiently accurate for NMR-observable
  protein dynamics -- MLFF adoption is justified by speed, not accuracy."
- Publish in JCTC (strong fit for force field comparison papers).
- Combined paper: Gamma proceeds independently with BioEmu ensembles (BioEmu is not an
  MLFF; it generates ensembles directly).

**What if DL methods DO beat linear baselines on Tahoe-100M?**
- This is actually the most publishable outcome for Delta.
- Frame: "At sufficient scale and with proper metric calibration, DL methods
  substantively outperform linear baselines -- but only under specific conditions
  (Tier 2-3 cross-context, large training sets)."
- This resolves the controversy in favor of DL, with nuance about when and how DL helps.
- Nature Methods fit: STRONG (provides clear answer to active debate).

---

## 7. Strategic Integration: The Portfolio View

### 7.1 Why All Three Projects Should Run in Parallel

| Project | Timeline | Compute | Risk | Independence |
|---------|----------|---------|------|-------------|
| Delta | 3 months | 1-2K GPU-hrs | Moderate (crowded) | Fully independent |
| Gamma | 5 months | ~2.2K GPU-hrs | Moderate (signal risk) | Semi-independent (benefits from Alpha-M but not dependent) |
| Alpha-M | 7 months | 42-63K GPU-hrs | Low-moderate (compute, stability) | Semi-independent (benefits from Gamma but not dependent) |

Total compute for all three MVPs: ~45-67K GPU-hrs. This is well within the available HPC
capacity (H200, RTX 5000 Ada, B200 GPUs with hundreds of CPU nodes).

Personnel allocation:
- Person 1: Delta lead (May-August) then Gamma/Alpha-M integration (September-December)
- Person 2: Gamma lead (May-October)
- Person 3: Alpha-M lead (May-December)

### 7.2 Publication Sequencing

**Optimal sequence (all three succeed):**
1. **July 2026:** Delta preprint on bioRxiv + Nature Methods submission
2. **September 2026:** Gamma preprint on bioRxiv (establishes priority)
3. **November 2026:** Alpha-M + Gamma combined preprint on bioRxiv + Nature Comp Sci
   submission
4. **January 2027:** Delta accepted by Nature Methods (expected timeline)
5. **March-April 2027:** Combined paper accepted by Nature Comp Sci (expected timeline)

**Total output: 2 high-impact publications from one summer's work.**

### 7.3 The "Paper Title" Test

Each project should have a title that passes the "Nature editor reading 50 titles in
10 minutes" test:

- **Delta:** "PerturbMark: Deep Learning Models for Perturbation Prediction Excel at
  Scale but Fail Without Context" (or variant depending on results)
- **Gamma standalone:** "Protein Conformational Ensembles Predict Mutational Fitness
  Through Interpretable Dynamic Features"
- **Alpha-M standalone:** "The Reality Gap in Machine Learning Force Fields for Protein
  Dynamics: A Systematic Benchmark Against NMR Observables"
- **Gamma + Alpha-M combined:** "From Physically Accurate Ensembles to Biological
  Function: Validating and Applying ML-Generated Protein Dynamics"

### 7.4 Reviewer Anticipation

**Likely reviewer objections per project:**

**Alpha-M:**
1. "Why only 7 proteins? This is not comprehensive." --> Address: representative
   selection across size, fold, dynamics. Full benchmark (15 proteins) in revision.
2. "Simulation lengths are too short for convergence." --> Address: convergence analysis
   with error bars, 10 replicas per system.
3. "You didn't include [favorite MLFF]." --> Address: clear inclusion criteria (open
   source, protein-ready, stable in water).
4. "The NMR back-calculation is an approximation." --> Address: validate against
   published experimental values for classical FFs first.

**Gamma:**
1. "You only used wildtype ensembles -- variant-specific dynamics matter." --> Address:
   explicitly discuss Aryal limitation; include variant-specific analysis where feasible.
2. "The comparison to sequence-only methods is unfair (different information)." -->
   Address: the question is whether structural dynamics ADD to sequence information.
3. "Why BioEmu and not MD?" --> Address: scalability; BioEmu enables proteome-scale
   analysis that MD cannot.
4. "The signal may be driven by trivial features (stability, not dynamics)." -->
   Address: include deltaG_fold as a feature and ablate.

**Delta:**
1. "How is this different from scPerturBench?" --> Address: Tahoe-100M, cross-context
   tiers, calibrated metrics, 2026 methods.
2. "You couldn't run all methods due to code issues." --> Address: document all
   reproducibility failures transparently; this IS part of the benchmark.
3. "Linear baselines are trivially good because perturbation effects are small." -->
   Address: explicitly measure effect sizes and contextualize baseline performance.
4. "Sample size in Tier 3 may be too small for statistical conclusions." --> Address:
   power analysis; Tahoe-100M's 50 cell lines provide substantial Tier 3 data.

---

## 8. Conclusion and Recommendations

### 8.1 Priority Actions

1. **Start Delta immediately (May 1, 2026).** This is the most time-sensitive project.
   Download Tahoe-100M, begin method installation, design cross-context splits.

2. **Start Gamma BioEmu pipeline simultaneously (May 1, 2026).** Curate ProteinGym
   proteins with PDB structures, begin BioEmu sampling. The go/no-go signal check at
   June 30 is critical.

3. **Start Alpha-M validation run (May 1, 2026).** Run one protein (ubiquitin) with
   one MLFF (MACE-OFF24) for the full 50 ns protocol. This validates the pipeline and
   informs compute estimates.

4. **Alpha-M full MVP launch: June 2026** (contingent on successful validation run).

5. **Hold combined paper decision until September 30, 2026.** By then, both Gamma
   signal and Alpha-M simulation progress will be known.

### 8.2 What I Want from Other Specialists

- **mlffeng:** Confirm MLFF stability screening protocol for ubiquitin. What are the
  diagnostic criteria for "pass" vs. "fail"?
- **bioval:** Confirm protein selection for MVP (7 proteins). Which have the richest
  NMR data and most discriminating observables?
- **ensfunc:** Confirm ProteinGym protein curation. How many have PDB structures and
  which functional categories are represented?
- **pertbio:** Confirm Tahoe-100M data access status. What is the actual download size
  and preprocessing pipeline?
- **evalstat:** Design the statistical framework for the go/no-go signal check for
  Gamma at June 30. What is the minimum detectable effect size?

### 8.3 Summary of Competitive Windows

| Project | Window | Urgency | Action |
|---------|--------|---------|--------|
| Alpha-M | 12-24+ months | LOW | Start but do not rush; quality over speed |
| Gamma | 6-12 months | MODERATE | Start immediately; preprint by September |
| Delta | 3-6 months | HIGH | Start immediately; preprint by July |

---

## References

1. Batatia, I. et al. (2025). MACE-OFF: Short-Range Transferable Machine Learning Force
   Fields for Organic Molecules. *Journal of the American Chemical Society*.
   https://pubs.acs.org/doi/10.1021/jacs.4c07099

2. Suarez-Dou, S. et al. (2026). Molecular Simulations with a Pretrained Neural Network
   and Universal Pairwise Force Fields (SO3LR). *Journal of the American Chemical Society*.
   https://pubs.acs.org/doi/10.1021/jacs.5c09558

3. Zhang, J. et al. (2024). Ab initio characterization of protein molecular dynamics with
   AI2BMD. *Nature*, 636, 1058-1062. https://www.nature.com/articles/s41586-024-08127-z

4. Unke, O. et al. (2024). Biomolecular dynamics with machine-learned quantum-mechanical
   force fields trained on diverse chemical fragments (GEMS). *Science Advances*.
   https://www.science.org/doi/10.1126/sciadv.adn4397

5. Cavender, C.E. et al. (2025). Structure-Based Experimental Datasets for Benchmarking
   Protein Simulation Force Fields. *Living Journal of Computational Molecular Science*.
   https://pmc.ncbi.nlm.nih.gov/articles/PMC12823150/

6. Lindorff-Larsen, K. et al. (2012). Are Protein Force Fields Getting Better? A Systematic
   Benchmark on 524 Diverse NMR Measurements. *Journal of Chemical Theory and Computation*,
   8(9), 3257-3273. https://pubs.acs.org/doi/abs/10.1021/ct2007814

7. Choudhary, K. et al. (2025). CHIPS-FF: Evaluating Universal Machine Learning Force
   Fields for Material Properties. *ACS Materials Letters*.
   https://pubs.acs.org/doi/10.1021/acsmaterialslett.5c00093

8. Batzner, S. et al. (2025). Crash testing machine learning force fields for molecules,
   materials, and interfaces (TEA Challenge 2023). *Chemical Science*.
   https://pubs.rsc.org/en/content/articlehtml/2025/sc/d4sc06530a

9. Jing, B. et al. (2025). Scalable emulation of protein equilibrium ensembles with
   generative deep learning (BioEmu). *Science*.
   https://www.science.org/doi/10.1126/science.adv9817

10. Microsoft Research (2026). Exploring the structural changes driving protein function
    with BioEmu-1. Blog post, April 2026.
    https://www.microsoft.com/en-us/research/blog/exploring-the-structural-changes-driving-protein-function-with-bioemu-1/

11. Aryal, B. et al. (2026). Assessing the Performance of BioEmu in Understanding Protein
    Dynamics. *International Journal of Molecular Sciences*, 27(6), 2896.
    https://www.mdpi.com/1422-0067/27/6/2896

12. Monteiro da Silva, G. et al. (2026). Accelerated sampling of protein dynamics using
    BioEmu augmented molecular simulation. *bioRxiv*.
    https://www.biorxiv.org/content/10.64898/2026.01.07.698041v2

13. Chen, S. et al. (2026). Protein Language Models Trained on Biophysical Dynamics Inform
    Mutation Effects (SeqDance/ESMDance). *PNAS*, 123(4).
    https://www.pnas.org/doi/10.1073/pnas.2530466123

14. Notin, P. et al. (2024). ProteinGym: Large-Scale Benchmarks for Protein Design and
    Fitness Prediction. *NeurIPS 2023 Datasets and Benchmarks*.
    https://github.com/OATML-Markslab/ProteinGym

15. Meier, N. et al. (2026). IDPForge: Deep Learning of Proteins with Global and Local
    Regions of Disorder. *bioRxiv*.
    https://www.biorxiv.org/content/10.64898/2026.03.25.714313v1

16. Wei, J. et al. (2026). Benchmarking algorithms for generalizable single-cell
    perturbation response prediction (scPerturBench). *Nature Methods*.
    https://www.nature.com/articles/s41592-025-02980-0

17. Dibaeinia, P. et al. (2026). Evaluating Single-Cell Perturbation Response Models Is
    Far from Straightforward. *bioRxiv*.
    https://www.biorxiv.org/content/10.64898/2026.02.14.705879v1

18. Cole, E. et al. (2026). Foundation Models Improve Perturbation Response Prediction.
    *bioRxiv*. https://www.biorxiv.org/content/10.64898/2026.02.18.706454v1

19. Li, Z. et al. (2026). Towards building a World Model to simulate perturbation-induced
    cellular dynamics (AlphaCell). *bioRxiv*.
    https://www.biorxiv.org/content/10.64898/2026.03.02.709176v1

20. Wang, J. et al. (2026). AetherCell: A generative engine for virtual cell perturbation
    and in vivo drug discovery. *bioRxiv*.
    https://www.biorxiv.org/content/10.64898/2026.03.13.710968v1

21. Kim, M. et al. (2026). X-Cell: Scaling Causal Perturbation Prediction Across Diverse
    Cellular Contexts via Diffusion Language Models. *bioRxiv*.
    https://www.biorxiv.org/content/10.64898/2026.03.18.712807v1

22. Zhu, J. & Li, W. (2026). Scouter predicts transcriptional responses to genetic
    perturbations with large language model embeddings. *Nature Computational Science*.
    https://www.nature.com/articles/s43588-025-00912-8

23. Zhang, Z. et al. (2025). Tahoe-100M: A Giga-Scale Single-Cell Perturbation Atlas.
    *bioRxiv*. https://www.biorxiv.org/content/10.1101/2025.02.20.639398v1

24. Virtual Cell Challenge 2025 Wrap-Up: Winners and Reflections. Arc Institute, 2025.
    https://arcinstitute.org/news/virtual-cell-challenge-2025-wrap-up

25. Miller, J. et al. (2025). Deep Learning-Based Genetic Perturbation Models Do
    Outperform Uninformative Baselines on Well-Calibrated Metrics. *bioRxiv*.
    https://www.biorxiv.org/content/10.1101/2025.10.20.683304v1

26. Ghafouri, H. et al. (2026). Toward a unified framework for determining conformational
    ensembles of disordered proteins. *Nature Methods*, 23, 705-719.
    https://www.nature.com/articles/s41592-026-03003-2

27. Tahoe-x1: Scaling Perturbation-Trained Single-Cell Foundation Models to 3 Billion
    Parameters. *bioRxiv*, October 2025.
    https://www.biorxiv.org/content/10.1101/2025.10.23.683759v1

28. Representing local protein environments with machine learning force fields. *arXiv*,
    2025. https://arxiv.org/html/2505.23354

29. A scalable and quantum-accurate foundation model for biomolecular force fields via
    linearly tensorized quadrangle attention (LiTEN-FF). *Nature Communications*, March
    2026. https://www.nature.com/articles/s41467-026-70377-4

30. Ahlmann-Eltze, C. et al. (2025). Deep learning does not outperform classical machine
    learning for cell-type annotation. *Nature Methods*.
