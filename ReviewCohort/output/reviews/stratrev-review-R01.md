---
agent: Research Strategy Director (stratrev)
round: 1
date: 2026-04-15
type: review-assessment
scope: cross-cohort
---

# Strategic Assessment: Portfolio Evaluation and Publication Strategy

## Reviewing Agent

I am the Research Strategy Director -- a former Nature Methods associate editor (3 years),
NIH study section member, and PI with 40+ publications. I optimize for portfolio expected
value, not individual project perfection. My job is to answer: given our compute, timeline,
and competitive landscape, what publication strategy maximizes total impact?

## Executive Summary

The portfolio is well-constructed but faces three strategic realities that the Cohort 2
proposals underestimate. First, the competitive landscape for Gamma has shifted: the
Ozkan et al. PNAS 2025 paper and the SeqDance/ESMDance PNAS 2026 paper both connect
protein dynamics to mutation fitness prediction, narrowing our novelty window. Second,
the Delta (PerturbMark) landscape has intensified dramatically: scPerturBench is now
published in Nature Methods (2025), the "DL does not outperform linear baselines" paper
is in Nature Methods (2025), and at least four additional perturbation benchmarking
efforts have appeared in 2025-2026. Third, the NCS editorial bar has risen -- the
journal published a sequence-ensemble-function paper (Krueger et al., 2025) that
partially overlaps with our combined paper's conceptual territory for disordered proteins.
Despite these challenges, the portfolio remains viable. I recommend an accelerated
timeline with a preprint-first mandate, scope narrowing for Delta's differentiation,
and a decisive combined-vs-separate decision by August 31 rather than September 30.

---

## Part I: Competition Scan

### 1.1 BioEmu + Function/Fitness (Gamma Scoop Risk)

**Assessment: ELEVATED from 25-35% to 35-45% over 6 months.**

The Cohort 2 estimate of 25-35% scoop risk was based on the April 14 scan. My fresh
scan (April 15, 2026) identifies the following developments:

**Direct threats:**

1. **Ozkan et al. (PNAS 2025): "A protein dynamics-based deep learning model enhances
   predictions of fitness and epistasis."** This is the closest existing competitor. The
   paper builds an allosteric GNN using the Asymmetric Dynamic Coupling Index (DCIasym),
   a physics-based dynamics metric, to predict mutation fitness across four DMS datasets.
   Despite not training on experimental epistasis data, their GNN outperforms existing
   approaches. This paper occupies adjacent conceptual territory: dynamics features
   predict fitness. However, it uses normal-mode analysis (ENM-based dynamics), not MD
   ensembles, and tests only 4 proteins. Our Gamma proposal uses BioEmu ensembles
   across 150 proteins -- a substantial scope expansion. But the novelty claim "dynamics
   predict fitness" is no longer virgin territory.
   (Source: https://www.pnas.org/doi/10.1073/pnas.2502444122)

2. **SeqDance/ESMDance (PNAS 2026, published January 2026): "Protein language models
   trained on biophysical dynamics inform mutation effects."** Hou, Zhao, and Shen trained
   protein language models on dynamic properties from MD simulations of 64,000+ proteins.
   ESMDance substantially outperforms ESM2 on zero-shot mutation effect prediction for
   designed and viral proteins. This paper directly connects protein dynamics to mutation
   fitness prediction. The key difference from our Gamma: SeqDance/ESMDance learns a
   dynamics-aware embedding from sequence, while Gamma extracts explicit dynamics features
   from BioEmu ensembles. Our approach is orthogonal (explicit ensembles vs. learned
   embeddings) but the conceptual territory is shared.
   (Source: https://www.pnas.org/doi/10.1073/pnas.2530466123)

3. **ICed-ENM (bioRxiv March 2026): "Mutation-induced reshaping of protein conformational
   dynamics."** An essential-dynamics-refined elastic network model that captures
   mutation-induced side-chain effects on conformational dynamics. Not a direct competitor
   (ENM-based, not ensemble-based), but occupies "dynamics predict mutation effects"
   space and is referenced in our own proposal as a baseline.
   (Source: https://www.biorxiv.org/content/10.64898/2026.03.29.715126v1)

**Adjacent threats:**

4. **BioEmu augmented molecular simulation (bioRxiv January 2026):** This Microsoft
   Research preprint demonstrates BioEmu-initiated MD simulations capturing active-to-
   inactive transitions in CDK2 and BRAF kinases, including how the V600E disease
   mutation drives population shifts. This is NOT a fitness prediction paper, but it
   shows the BioEmu team is connecting ensembles to mutation effects. The step from
   "qualitative population shifts for individual mutations" to "systematic fitness
   prediction across DMS assays" is exactly what Gamma proposes. Microsoft Research has
   every incentive to make this connection.
   (Source: https://www.biorxiv.org/content/10.64898/2026.01.07.698041v2)

5. **BioEmu published in Nature Methods (2025):** BioEmu is now a citable, peer-reviewed
   tool (Lewis, Jing et al., Science 2025; also Nature Methods 2025). This legitimizes
   BioEmu-based analyses but also means other groups can readily use it.
   (Source: https://www.nature.com/articles/s41592-025-02874-1)

6. **Aryal et al. (Int. J. Mol. Sci. 2026): "Assessment of BioEmu for Mutational
   Analysis."** An independent assessment of BioEmu's performance on mutational analysis.
   This paper exists and partially validates BioEmu for mutation-related applications,
   further reducing our novelty.
   (Source: https://www.mdpi.com/1422-0067/27/6/2896)

**My assessment:** The "dynamics predict fitness" conceptual space is no longer empty.
Ozkan et al. (2025) demonstrated it with ENM-derived features on 4 proteins. SeqDance
(2026) demonstrated it with PLM-learned dynamics on 64K proteins. Our Gamma novelty
must be repositioned from "first to show dynamics predict fitness" to "first systematic
connection of physics-based equilibrium ensembles (BioEmu) to large-scale fitness
benchmarks (ProteinGym), establishing which dynamical features carry functional
information and whether ensemble physical accuracy matters." This is still novel, but
the framing must be sharper.

**Scoop risk revision:** I raise the 6-month scoop risk from 25-35% to 35-45%, driven
primarily by the BioEmu augmented simulation preprint showing Microsoft Research is
actively connecting BioEmu to mutation effects.

### 1.2 MLFF + Protein Benchmark (Alpha-M Scoop Risk)

**Assessment: LOW, maintaining <10%.**

The MLFF benchmarking landscape has evolved but no group has published the specific
comparison Alpha-M proposes:

1. **MACE-OFF24 (Kovacs et al., JACS 2025):** Published May 2025. Validates MACE-OFF
   against experimental NMR (3J-couplings from Ramachandran distributions for Ala3
   peptide) and demonstrates nanosecond protein simulations (Crambin). However, this
   is a single-protein demonstration, not a systematic benchmark across 7 proteins
   against S2, shifts, J-couplings, and SAXS. Alpha-M's scope is vastly broader.
   (Source: https://pubs.acs.org/doi/10.1021/jacs.4c07099)

2. **SO3LR (Frank et al., JACS 2025):** Demonstrates polypeptide folding and nanosecond
   dynamics of proteins in explicit solvent. Validates on molecular properties but does
   not systematically benchmark against experimental NMR observables across multiple
   proteins.
   (Source: https://pubs.acs.org/doi/10.1021/jacs.5c09558)

3. **Garnet (arXiv March 2026):** A GNN-parameterized classical force field trained on
   QM data AND protein NMR data. Garnet is trained on NMR J-couplings from the same
   benchmark proteins Alpha-M will use. This is both a competitor and a mandatory
   baseline -- which the proposal already incorporates. Garnet's publication validates
   that NMR-benchmarking of force fields is a live research direction.
   (Source: https://arxiv.org/abs/2603.16770)

4. **UniFFBench (Mannan et al., arXiv August 2025):** Benchmarks universal MLFFs against
   experimental measurements -- but for MINERALS, not proteins. This is the materials-
   science analogue of Alpha-M. Its publication validates the "reality gap" framing.
   (Source: https://arxiv.org/abs/2508.05762)

5. **Cavender et al. (LiveCOMS 2025): "Structure-Based Experimental Datasets for
   Benchmarking Protein Simulation Force Fields."** A review cataloging NMR and RT-
   crystallography datasets suitable for force field benchmarking. This review paper
   sets the stage for exactly the kind of benchmark Alpha-M proposes but does not
   perform the benchmark itself.
   (Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC12823150/)

6. **BioKinema (bioRxiv February 2026):** A physically grounded generative model for
   all-atom biomolecular dynamics. Not a benchmarking paper but a new method that could
   become an additional comparator.
   (Source: https://www.biorxiv.org/content/10.64898/2026.02.15.705956v1)

**My assessment:** No group has published a systematic multi-protein MLFF benchmark
against experimental NMR/SAXS observables. The Garnet paper validates the direction
but does not perform the cross-method comparison. Alpha-M remains uniquely positioned.
The scoop risk is genuinely low (<10% in 6 months) because the execution barrier is
high (~107K GPU-hrs of simulations).

### 1.3 Perturbation Benchmarking (Delta Scoop Risk)

**Assessment: SUBSTANTIALLY ELEVATED from Moderate to HIGH (50-60% for differentiation erosion).**

The perturbation benchmarking space has become crowded since the Cohort 2 proposals
were finalized:

1. **scPerturBench (Nature Methods 2025):** Now peer-reviewed and published.
   Benchmarked 27 methods across 29 datasets using 6 evaluation metrics. This is the
   definitive first-generation benchmark. Delta must clearly differentiate from
   scPerturBench, not just claim to be better.
   (Source: https://www.nature.com/articles/s41592-025-02980-0)

2. **"Deep-learning-based gene perturbation effect prediction does not yet outperform
   simple linear baselines" (Nature Methods 2025):** This paper directly establishes
   one of Delta's key findings (DL vs. linear baselines) as already known. Five
   foundation models and two DL models failed to outperform simple baselines.
   Delta's "when does deep learning help?" framing is now partially answered.
   (Source: https://www.nature.com/articles/s41592-025-02772-6)

3. **PerturBench (arXiv 2408.10609, 2024; Altos Labs):** Another comprehensive
   benchmarking framework. Modular, user-friendly platform with diverse datasets.
   (Source: https://arxiv.org/abs/2408.10609)

4. **"Evaluating Single-Cell Perturbation Response Models Is Far from Straightforward"
   (bioRxiv February 2026):** Demonstrates that widely used metrics including
   correlation-based measures and distributional distances are influenced by scale,
   sparsity, and dimensionality, often misrepresenting model performance. This
   directly supports Delta's metric criticism but also means another group is
   independently reaching similar conclusions.
   (Source: https://www.biorxiv.org/content/10.64898/2026.02.14.705879v1)

5. **Systema (Nature Biotechnology 2025):** A framework for evaluating genetic
   perturbation response prediction beyond systematic variation. Demonstrates that
   common metrics are susceptible to confounders, leading to overestimated performance.
   (Source: https://www.nature.com/articles/s41587-025-02777-8)

6. **Tahoe-x1 (bioRxiv October 2025):** Tahoe Bio's own foundation model, trained on
   Tahoe-100M, achieving SOTA on perturbation response prediction. The dataset creators
   have their own model. Any benchmark using Tahoe-100M will inevitably be compared
   against Tahoe-x1.
   (Source: https://www.biorxiv.org/content/10.1101/2025.10.23.683759v1)

7. **New methods appearing rapidly:** AlphaCell (bioRxiv March 2026), X-Cell (bioRxiv
   March 2026), pertTF (bioRxiv March 2026), scDFM (ICLR 2026), scREPA (2026). The
   method catalog is expanding faster than Delta can evaluate.
   (Sources: multiple bioRxiv and conference papers)

8. **Virtual Cell Challenge:** Tahoe Therapeutics, Arc Institute, and Biohub announced
   a partnership to generate the largest perturbation dataset and establish a recurring
   benchmark competition. This is an institutional effort that could subsume Delta's
   niche.

**My assessment:** Delta's differentiation has eroded substantially. The "DL does not
beat linear baselines" finding is published in Nature Methods. scPerturBench is published
in Nature Methods. The metric critique is independently confirmed by multiple groups.
Delta must be repositioned from "first calibrated benchmark" to "first cross-context,
chemical-perturbation-focused benchmark on Tahoe-100M with calibrated metrics." The
Tahoe-100M focus and 4-tier difficulty hierarchy remain unique, but the window is
narrowing. I estimate a 50-60% risk of significant differentiation erosion within 6
months if we do not accelerate.

### 1.4 Overall Competitive Assessment

| Project | Scoop Risk (Cohort 2 est.) | Revised Risk (stratrev) | Key New Threat |
|---------|---------------------------|------------------------|----------------|
| Gamma | 25-35% | 35-45% | Ozkan PNAS 2025, SeqDance PNAS 2026, BioEmu augmented sim |
| Alpha-M | <10% | <10% (unchanged) | Garnet (March 2026) validates direction but not a scoop |
| Delta | Moderate | 50-60% differentiation erosion | scPerturBench NatMeth, DL-vs-baselines NatMeth |
| Combined | <10% for integration | 15-20% for conceptual overlap | NCS IDP ensemble-function paper |

**Bottom line:** Alpha-M is safe. Gamma is under increasing conceptual pressure but
retains a scope advantage (150 proteins, explicit BioEmu ensembles, ProteinGym-scale).
Delta is the most threatened project in the portfolio and requires immediate strategic
repositioning. The combined paper's integration claim remains novel but must be framed
carefully against the Ozkan and SeqDance precedents.

---

## Part II: NCS Precedent Analysis

### 2.1 Recent NCS Publications (2025-2026)

My scan of NCS 2025-2026 content reveals the following relevant precedents:

1. **Krueger, Shrinivas, Brenner et al. (NCS 2025): "Generalized design of sequence-
   ensemble-function relationships for intrinsically disordered proteins."** This paper
   directly connects conformational ensembles to biological function through computational
   design of IDPs with tunable ensemble properties. The conceptual framing -- that
   ensembles encode function -- overlaps with our combined paper's thesis. Key
   difference: this is about IDP design, not folded-protein fitness prediction.
   (Source: https://www.nature.com/articles/s43588-025-00881-y)

2. **Scouter (Zhu & Li, NCS 2026): "Scouter predicts transcriptional responses to
   genetic perturbations with large language model embeddings."** NCS vol. 6, pp. 21-28.
   NCS published a perturbation prediction paper using LLM embeddings, demonstrating
   the journal's interest in this space. Reduces Delta's pathway to NCS if scoped up,
   but confirms NCS will consider perturbation-related computational biology.
   (Source: https://www.nature.com/articles/s43588-025-00912-8)

3. **AUTOENCODIX (NCS 2025):** A benchmarking framework for autoencoder architectures in
   biological data. Demonstrates NCS publishes benchmark papers when they provide novel
   insights, not just method comparisons.

4. **FedProt (NCS 2025, Resource):** A federated proteomics resource. Confirms NCS
   publishes Resource-format papers for community tools.

5. **Network biology foundation models (NCS 2025):** Paper demonstrating that prediction
   accuracy in network biology scales with larger foundation models. Confirms NCS
   interest in scaling laws for biological ML.

### 2.2 Benchmark Papers at NCS

NCS has published benchmark/evaluation papers in 2024-2025, but they share a pattern:
benchmark papers succeed at NCS when they **reveal a principle**, not just rank methods.
The AUTOENCODIX paper revealed that specific autoencoder architectures are suited for
specific data types. The "DL doesn't beat baselines" finding at Nature Methods revealed
a sobering principle about perturbation prediction. The Scouter paper at NCS showed LLM
embeddings capture biological knowledge better than GO-term-based methods.

**Implication for our portfolio:** Alpha-M must reveal a principle ("the MLFF reality gap
extends to biomolecular simulation" or "ensemble accuracy is orthogonal to functional
prediction") beyond just ranking methods. A pure leaderboard paper will be desk-rejected.

### 2.3 Integration/Connection Papers

No NCS paper published in 2025-2026 has explicitly connected force field validation to
biological application. The Krueger IDP paper connects ensembles to function for
disordered proteins through design, but does not validate ensemble generators against
experiment. The gap our combined paper fills -- "does ensemble physical accuracy predict
functional utility?" -- remains open at NCS.

### 2.4 Editorial Bar Assessment

Based on my analysis of recent NCS content:

- **Desk rejection rate:** ~60-70% (unchanged from my prior estimate)
- **Key editorial criterion:** "An advance in understanding likely to influence thinking
  in the field" -- this is the decisive sentence
- **What passes the desk:** Papers that either (a) introduce a new computational method
  with demonstrated biological utility, (b) reveal a principle through systematic
  computational analysis, or (c) provide a resource that enables new kinds of
  investigation
- **What gets desk-rejected:** Pure benchmarks without insight, incremental method
  improvements, and papers where the computational sophistication is standard

**For our portfolio:**
- Combined paper: STRONG fit for NCS if the integration reveals a principle. The
  "Dynamics Quality-Function Plane" figure tells a story that changes thinking.
- Alpha-M standalone: MARGINAL for NCS. A benchmark paper without biological application.
  Better fit for Nature Methods (Resource format).
- Gamma standalone: MARGINAL for NCS. Standard ML on standard features, even if the
  application is novel. Better fit for NCS if framed as revealing a principle about
  which dynamics modalities encode which biological functions.
- Delta: POOR fit for NCS despite Scouter precedent, because Delta is a benchmark paper
  (Scouter was a method). Better fit for Nature Methods.

---

## Part III: Scope Arbitration

### 3.1 Combined vs Separate Recommendation

**Recommendation: Pursue the combined paper as primary target, but advance the decision
point from September 30 to August 31.**

**Reasoning:**

1. The combined paper's integration claim remains the strongest possible NCS
   contribution. Neither Alpha-M nor Gamma alone clears the NCS editorial bar
   reliably. The combined paper's "Dynamics Quality-Function Plane" concept is
   genuinely novel -- no published paper connects force field validation quality
   to downstream functional prediction quality.

2. The competitive pressure on Gamma (Ozkan, SeqDance, BioEmu augmented sim) makes
   the combined paper MORE important, not less. As a standalone, Gamma must defend its
   novelty against these precedents. As part of the combined paper, Gamma's contribution
   is the APPLICATION that validates the Alpha-M benchmark's relevance -- a much stronger
   position.

3. The statistical fragility of the 8-protein integration (Attack Vector #1, 95%
   probability) remains the weakest link. However, the proposed multilevel modeling
   approach (N=48 protein-generator pairs) and the within-protein correlation analysis
   provide more statistical power than the naive N=6 generators analysis.

4. The timeline risk is real but manageable. Advancing the decision point to August 31
   (rather than September 30) buys 4 weeks of buffer for the separate-papers fallback.
   By August 31, Alpha-M should have preliminary back-calculation results for at least
   5 proteins, and Gamma should have Stage 2 ML results. This is sufficient data to
   assess whether integration is plausible.

**Key conditions for the combined paper to proceed:**
- By June 30: Gamma RMSF-fitness correlation rho > 0.1 for at least 50% of proteins
- By August 15: Alpha-M production runs complete for at least 5 of 7 proteins
- By August 31: Preliminary integration analysis (BioEmu vs. AMBER on 6-8 overlap
  proteins) shows a positive trend (not necessarily significant)
- If any condition fails: immediate switch to separate papers with no delay

### 3.2 Seven vs 12-15 Proteins

**Recommendation: Stay at 7 proteins for Alpha-M, but expand the integration overlap
to 8-10 proteins by adding BPTI and barnase to the overlap set.**

**Precedent analysis:**

| Benchmark Study | N Proteins | Venue | Year |
|----------------|-----------|-------|------|
| Lindorff-Larsen et al. | 4 | PLoS ONE | 2012 |
| Robustelli et al. | 21 (classical FFs only) | PNAS | 2018 |
| MACE-OFF24 (Kovacs et al.) | 1 (Crambin) | JACS | 2025 |
| SO3LR (Frank et al.) | 1 (protein) | JACS | 2025 |
| Garnet | Multiple (not specified) | arXiv | 2026 |
| UniFFBench (materials) | ~1,500 minerals | arXiv | 2025 |
| Cavender et al. (review) | Endorses 4-15 | LiveCOMS | 2025 |

N=7 proteins with 8 methods (6+Garnet+ff14SB) is defensible against the Lindorff-Larsen
standard (4 proteins) and the Cavender review's endorsement of 4-15 proteins. The
per-residue cluster bootstrap approach (420-560 residues across 7 proteins) provides
substantially more statistical power than N=7 suggests.

However, N=7 will be attacked by reviewers expecting a larger set given the compute
resources available. The defense must be: (a) quality of NMR reference data, not
quantity of proteins, is the limiting factor, (b) we deliberately chose proteins with
the richest multi-observable NMR data, and (c) expanding to poorly-characterized
proteins would weaken, not strengthen, the benchmark.

### 3.3 Format Recommendations

| Paper | Recommended Format | Rationale |
|-------|-------------------|-----------|
| Combined (Gamma+Alpha-M) | NCS Article | The integration claim is a conceptual advance, not a resource. 50,000-character limit is tight but manageable with Supplementary Methods. |
| Alpha-M standalone | Nature Methods Resource | Benchmark data package is a community resource. Resource papers have no strict length limit. |
| Gamma standalone | NCS Article (stretch) or Genome Research | If framed as revealing principles about dynamics-function relationships. Genome Research is safer. |
| Delta | Nature Methods Article | Benchmark with insights. Resource format possible if leaderboard is included. |

---

## Part IV: Title Workshop

### 4.1 Combined Paper Titles (Ranked)

I rank titles by three criteria: (1) editor appeal (would this survive desk rejection?),
(2) accuracy (does this reflect the actual contribution?), (3) memorability (would
people cite this by its title?).

**Tier 1 (Strongest -- claim or question titles):**

1. **"Physical accuracy of protein ensembles predicts functional utility across
   mutation fitness landscapes"**
   - Editor appeal: 9/10. Makes a specific, testable claim. Connects two fields.
   - Accuracy: High if integration correlation is significant.
   - Risk: Overclaims if integration is suggestive but not significant.

2. **"From validated dynamics to biological function: connecting force field accuracy
   to mutation effect prediction"**
   - Editor appeal: 8/10. Clean narrative arc. "From X to Y" is an NCS-friendly format.
   - Accuracy: High. Describes the paper's structure.
   - Risk: Slightly generic.

3. **"Does ensemble accuracy matter? Benchmarking ML force fields and connecting
   physical fidelity to protein fitness prediction"**
   - Editor appeal: 8/10. Question titles signal hypothesis-agnostic work; NCS editors
     value this.
   - Accuracy: High regardless of integration result.
   - Risk: Question titles can signal uncertainty to some editors.

**Tier 2 (Good -- descriptive or framing titles):**

4. **"The biomolecular reality gap: ML force fields, experimental benchmarks, and
   functional consequences"**
   - Editor appeal: 7/10. "Reality gap" is memorable (UniFFBench precedent). Connects
     to a known concept from materials science.
   - Risk: Slightly buzzword-heavy.

5. **"Benchmarking protein ensemble generators from physical accuracy to functional
   prediction"**
   - Editor appeal: 7/10. Clear scope statement.
   - Risk: Reads like a methods paper.

6. **"Protein dynamics at a crossroads: when do accurate ensembles predict biological
   function?"**
   - Editor appeal: 7/10. Provocative question.
   - Risk: Slightly oversells the drama.

**Tier 3 (Backup -- conservative):**

7. **"Systematic evaluation of ML force fields reveals the link between ensemble
   quality and mutation fitness prediction"**
   - Editor appeal: 6/10. Accurate but reads like a Journal of Chemical Theory paper.

### 4.2 Alpha-M Standalone Titles

1. **"The MLFF biomolecular crash test: systematic benchmark of machine-learning force
   fields against experimental protein observables"** (8/10 -- memorable, clear scope)
2. **"Machine-learning force fields for proteins: how close are we to experiment?"**
   (8/10 -- question format works for Nature Methods)
3. **"Benchmarking ML force fields against NMR and SAXS across seven proteins reveals
   a persistent reality gap"** (7/10 -- specific, result-oriented)
4. **"Beyond small molecules: evaluating transferable ML force fields for protein
   dynamics"** (7/10 -- clear framing)

### 4.3 Gamma Standalone Titles

1. **"Protein conformational ensembles encode mutation fitness effects beyond sequence
   information"** (8/10 -- strong claim)
2. **"BioEmu ensembles predict mutation fitness across diverse protein functions"**
   (7/10 -- specific but tool-centric)
3. **"What conformational dynamics reveal about protein fitness landscapes"**
   (7/10 -- question format)
4. **"Dynamics-informed mutation effect prediction at ProteinGym scale"**
   (6/10 -- jargon-heavy)

### 4.4 Delta (PerturbMark) Titles

1. **"When does deep learning help? A calibrated cross-context benchmark for
   perturbation prediction"** (8/10 -- the current working title; strong question format)
2. **"PerturbMark: a neutral benchmark reveals where deep learning adds value in
   perturbation prediction"** (7/10 -- tool name + finding)
3. **"Beyond correlations: calibrated evaluation of perturbation prediction across
   cellular contexts"** (7/10 -- differentiates from metric-flawed benchmarks)
4. **"Benchmarking perturbation response prediction on Tahoe-100M across four
   difficulty tiers"** (6/10 -- specific but dry)

**Strategic note on Delta titles:** Given that the "DL doesn't beat baselines" finding
is now published (Nature Methods 2025), Delta's title must signal what is NEW. The
"when does deep learning help?" framing implies Delta will identify CONDITIONS under
which DL adds value, not just confirm the negative result. This is the critical
repositioning.

---

## Part V: Publication Strategy

### 5.1 Timeline (Revised)

I recommend an accelerated timeline driven by competitive pressure on Gamma and Delta:

```
Timeline:    May    Jun    Jul    Aug    Sep    Oct    Nov    Dec
Delta:       [====execution====][preprint 8/15][NatMeth sub 9/1]
Alpha-M:     [=====production======][S2 replicas][backcalc]
Gamma:       [ensembles][features][ML pipeline][ablation]
Decision:                                   [8/31]
Combined:                                        [integration][manuscript]
Combined:                                                     [preprint 11/1][NCS sub 11/15]
Fallback:                                        [Alpha-M ms][Gamma ms]
Fallback:                                                    [preprints 10/15]
```

**Key changes from Cohort 2 timeline:**
- Combined preprint target: November 1 (moved up from November 15)
- Combined NCS submission: November 15 (moved up from December 1)
- Decision point: August 31 (moved up from September 30)
- Delta preprint: August 15 (unchanged -- still the fastest path to publication)
- Fallback preprints: October 15 (not November, buying 2 weeks)

### 5.2 Venue Strategy

**Primary path:**

| Paper | Primary Venue | Backup Venue | Format |
|-------|-------------|-------------|--------|
| Combined | Nature Comp Sci | Split to Alpha-M + Gamma | Article |
| Delta | Nature Methods | Genome Biology | Article |

**Fallback path (if combined fails at August 31):**

| Paper | Primary Venue | Backup Venue | Format |
|-------|-------------|-------------|--------|
| Alpha-M | Nature Methods | NCS (if reviewer feedback positive) | Resource |
| Gamma | Genome Research | Bioinformatics | Article |
| Delta | Nature Methods | Genome Biology | Article |

**Cascade strategy for desk rejection:**
- If NCS desk-rejects the combined paper: immediately split and submit Alpha-M to
  Nature Methods and Gamma to Genome Research within 2 weeks (manuscripts already
  structured for separability).
- If Nature Methods desk-rejects Delta: submit to Genome Biology within 1 week.
  If Genome Biology rejects, submit to Bioinformatics within 1 week.

### 5.3 Preprint Strategy

**Preprint-first is MANDATORY for all papers.** The competitive landscape demands it.

| Paper | bioRxiv Date | Rationale |
|-------|-------------|-----------|
| Delta | August 15, 2026 | Fastest to completion; establishes priority in perturbation benchmarking space before Virtual Cell Challenge subsumes the niche |
| Combined (or fallbacks) | November 1, 2026 | Before MLML/NeurIPS 2026 proceedings; establishes priority before BioEmu team connects to ProteinGym |
| Twitter/X announcement | Same day as preprint | Tag BioEmu team, ProteinGym team, Tahoe team. Academic Twitter drives NCS editor attention. |

**Preprint-to-submission gap:** 2 weeks maximum. Submit journal version while the
preprint is generating attention.

### 5.4 Cover Letter Elements

**For NCS (Combined paper):**

Key points to include in the cover letter:

1. **The gap statement:** "No study has connected the physical accuracy of protein
   ensemble generators -- validated against experimental NMR and SAXS observables --
   to their utility for predicting mutation fitness effects. We close this gap."

2. **The principle revealed:** "We establish that ensemble physical accuracy [does/does
   not] predict functional utility, a finding that changes how the field thinks about
   both force field validation and fitness prediction."

3. **The scope:** "Our analysis spans 7 proteins with 8 ensemble generators (Alpha-M)
   and 150 proteins with ProteinGym-scale fitness benchmarks (Gamma), connected through
   an 8-protein integration analysis with pre-registered statistical tests."

4. **Reviewer suggestions:** Suggest reviewers who span both domains:
   - MD simulation: Kresten Lindorff-Larsen (Copenhagen), Stefano Piana (DE Shaw)
   - ML for fitness: Pascal Notin or Debora Marks (Harvard/Oxford)
   - Ensemble methods: Frank Noe (FU Berlin / Microsoft Research -- conflict?)
   - Integration/statistics: A statistical reviewer (e.g., Witten lab, Stanford)
   - EXCLUDE: Ozkan group (direct competitor), Shen lab (SeqDance, competitor)

5. **Why NCS:** "This paper sits at the intersection of molecular simulation,
   machine learning, and protein biology -- the core remit of Nature Computational
   Science. The finding that [accurate/all] ensembles predict function [better/equally]
   establishes a new paradigm for computational protein science."

### 5.5 Conference Calendar Integration

| Conference | Dates | Relevance | Action |
|-----------|-------|-----------|--------|
| ICML 2026 | July 2026 | ML community visibility | Poster for Delta if accepted as workshop paper |
| MLCB 2026 (NeurIPS workshop) | December 2026 | ML + Comp Bio | Submit extended abstract for combined paper |
| Biophysical Society 2027 | February 2027 | Alpha-M community | Submit abstract October 2026 |
| ISMB 2027 | July 2027 | Comp Bio flagship | Submit Gamma/combined abstract |

---

## Part VI: Portfolio Expected Value

### 6.1 Scenario Analysis

I model the portfolio expected value (EV) across four scenarios, assigning impact scores
on a 1-10 scale where 10 = NCS Article, 8 = Nature Methods Article, 6 = Genome Research,
4 = Bioinformatics/PLOS Comp Bio.

**Scenario 1: Combined paper succeeds (probability: 40%)**
- Combined paper: NCS Article (impact = 10)
- Delta: Nature Methods Article (impact = 8)
- Total impact: 18
- EV contribution: 0.40 x 18 = 7.2

**Scenario 2: Combined fails, both components strong separately (probability: 30%)**
- Alpha-M: Nature Methods Resource (impact = 8)
- Gamma: Genome Research Article (impact = 6)
- Delta: Nature Methods Article (impact = 8)
- Total impact: 22
- EV contribution: 0.30 x 22 = 6.6

**Scenario 3: Gamma shows weak signal, Alpha-M strong (probability: 20%)**
- Alpha-M: Nature Methods Resource (impact = 8)
- Gamma: PLOS Comp Bio (negative result) (impact = 4)
- Delta: Nature Methods Article (impact = 8)
- Total impact: 20
- EV contribution: 0.20 x 20 = 4.0

**Scenario 4: Multiple components underperform (probability: 10%)**
- Alpha-M: JCTC or equivalent (impact = 5)
- Gamma: Bioinformatics Brief (impact = 3)
- Delta: Genome Biology (impact = 6)
- Total impact: 14
- EV contribution: 0.10 x 14 = 1.4

**Portfolio Expected Value: 19.2 impact units**

**Expected number of publications: 2.4 papers**
- P(at least 1 NCS paper): ~40%
- P(at least 1 Nature Methods paper): ~85%
- P(at least 2 papers at high-quality venues): ~90%
- P(at least 3 papers): ~30%
- P(complete failure, 0 papers): <1%

### 6.2 Resource Allocation

| Resource | Alpha-M | Gamma | Delta | Integration | Total |
|----------|---------|-------|-------|-------------|-------|
| GPU-hrs | 107,000 | 2,130 | 1,070 | 50 | 110,250 |
| % of total | 97.1% | 1.9% | 1.0% | <0.1% | 100% |
| Personnel (FTE-weeks) | 16 | 14 | 12 | 2 | 44 |
| Expected impact per GPU-hr | Low | Very High | Very High | Extreme | -- |

**The paradox:** Alpha-M consumes 97% of compute but contributes ~40% of expected
portfolio impact (through the combined paper). Gamma and Delta together consume <3%
of compute but contribute ~60% of expected impact. This is the correct allocation
because (a) Alpha-M's benchmark data enables the combined paper's integration, and
(b) Alpha-M produces a valuable community resource regardless of publication outcome.

**Recommendation: Do not reduce Alpha-M compute.** The simulations are the hard part;
the analysis is cheap. Cutting corners on simulation length or replica count would
weaken the benchmark's credibility and endanger the combined paper's statistical power.

### 6.3 Risk-Adjusted Assessment

**Highest risk-adjusted return: Delta.**
- Low compute (1,070 GPU-hrs), short timeline (12 weeks), high probability of Nature
  Methods publication (~75-80%). However, differentiation has eroded. Must reposition.

**Highest ceiling: Combined paper.**
- If it works, it is a paradigm-establishing NCS paper. The integration claim is
  genuinely novel. But probability of full success is ~40%.

**Most robust: Alpha-M.**
- Produces a valuable benchmark regardless of outcome. Nature Methods Resource is
  near-certain if simulations complete. The "reality gap" framing works even with
  negative results.

**Most vulnerable: Gamma standalone.**
- Without the combined paper's Alpha-M integration, standalone Gamma faces stiff
  competition from Ozkan (2025), SeqDance (2026), and the BioEmu augmented simulation
  group. Must be paired with Alpha-M for maximum impact.

---

## Specific Recommendations

1. **CRITICAL: Advance the combined vs. separate decision from September 30 to
   August 31.** The competitive clock is ticking. Every month of delay increases the
   probability that the BioEmu team or Marks Lab publishes a BioEmu+ProteinGym
   connection paper. August 31 provides enough data to decide (preliminary Alpha-M
   back-calculations for 5+ proteins, Gamma Stage 2 ML results) while preserving
   6 weeks for manuscript preparation.

2. **CRITICAL: Reframe Gamma's novelty.** The "dynamics predict fitness" claim is
   no longer novel after Ozkan (2025) and SeqDance (2026). Gamma's novelty must be:
   (a) first use of physics-based equilibrium ensembles (not ENM or PLM surrogates) at
   ProteinGym scale, (b) identification of which dynamical features carry which
   functional signals (assay-type stratification), and (c) the integration with
   experimental validation (combined paper). Update all Gamma framing documents.

3. **CRITICAL: Reposition Delta immediately.** The "DL vs. linear baselines" finding
   is published. Delta must pivot from "does DL help?" to "WHEN and WHERE does DL help?"
   The 4-tier difficulty hierarchy and cross-context evaluation on Tahoe-100M are Delta's
   remaining unique contributions. The title "When Does Deep Learning Help?" becomes more
   specific: "Where deep learning adds value: difficulty-stratified perturbation
   benchmarking across cellular contexts on Tahoe-100M." Also add Tahoe-x1 as a
   mandatory evaluation target.

4. **IMPORTANT: Add Tahoe-x1 (3B parameter model) to Delta's method catalog.** The
   dataset creators' own model must be evaluated. Omitting it would be a glaring gap
   that reviewers will notice.

5. **IMPORTANT: Conduct monthly competition scans.** Set bioRxiv/Google Scholar alerts
   for: "BioEmu fitness," "BioEmu ProteinGym," "MLFF protein NMR benchmark,"
   "perturbation benchmark Tahoe." If a preprint appears from the BioEmu team connecting
   to ProteinGym fitness, immediately accelerate the Gamma preprint timeline.

6. **IMPORTANT: Title the combined paper as a claim, not a question, if the integration
   result is positive.** "Physical accuracy of protein ensembles predicts functional
   utility across mutation fitness landscapes" is my top recommendation. Question titles
   are appropriate for hypothesis-agnostic work; if the data support the claim, make it.

7. **MODERATE: For Alpha-M, benchmark Garnet as planned but also consider adding
   MACE-POLAR-1 (Batatia et al., 2026) if it becomes available for protein systems.**
   The Csanyi group is actively developing polarizable MLFFs. If MACE-POLAR-1 supports
   protein simulation by the time Alpha-M runs, it would be a high-profile addition.

8. **MODERATE: For the combined paper cover letter, explicitly address the Ozkan and
   SeqDance precedents.** State: "While recent work has connected coarse dynamics
   proxies (ENM, SeqDance) to mutation effects on small protein sets, no study has
   used physics-based equilibrium ensembles at scale or connected ensemble physical
   accuracy (validated against NMR experiment) to functional prediction quality."

9. **MODERATE: Preregister all three projects on OSF by May 15, 2026 -- before any
   simulations begin.** Pre-registration strengthens the statistical credibility of all
   projects and addresses reviewer concerns about post-hoc analysis choices.

10. **LOW: Consider a companion Delta preprint focused purely on metric criticism
    (Tahoe-100M-specific issues with correlation metrics, sparsity, scale effects) as
    a "letter" or "correspondence" in Nature Methods, referencing both scPerturBench
    and the "DL vs. baselines" paper.** This establishes Delta's metric contribution
    independently of the full benchmark, and a published correspondence can be
    referenced in the full Delta paper.

---

## References

1. Ozkan, S.B. et al. (2025). A protein dynamics-based deep learning model enhances
   predictions of fitness and epistasis. PNAS 122: e2502444122.
   https://www.pnas.org/doi/10.1073/pnas.2502444122

2. Hou, L., Zhao, Q., and Shen, Y. (2026). Protein language models trained on
   biophysical dynamics inform mutation effects. PNAS 123: e2530466123.
   https://www.pnas.org/doi/10.1073/pnas.2530466123

3. Lewis, J., Jing, B. et al. (2025). Scalable emulation of protein equilibrium
   ensembles with generative deep learning. Science 369: 270-278.
   https://www.science.org/doi/10.1126/science.adv9817

4. Lewis, J. et al. (2025). BioEmu is a biomolecular emulator for sampling protein
   structure ensembles. Nature Methods.
   https://www.nature.com/articles/s41592-025-02874-1

5. BioEmu augmented molecular simulation (2026). Accelerated sampling of protein
   dynamics using BioEmu augmented molecular simulation. bioRxiv.
   https://www.biorxiv.org/content/10.64898/2026.01.07.698041v2

6. Aryal, R. et al. (2026). Assessment of BioEmu for Mutational Analysis.
   Int. J. Mol. Sci. 27: 2896. https://www.mdpi.com/1422-0067/27/6/2896

7. Kovacs, D.P. et al. (2025). MACE-OFF: Short-Range Transferable Machine Learning
   Force Fields for Organic Molecules. JACS 147: 17598-17611.
   https://pubs.acs.org/doi/10.1021/jacs.4c07099

8. Frank, M. et al. (2025). SO3LR: Molecular Simulations with a Pretrained Neural
   Network and Universal Pairwise Force Fields. JACS.
   https://pubs.acs.org/doi/10.1021/jacs.5c09558

9. Garnet Force Field (2026). Training a force field for proteins and small molecules
   from scratch. arXiv:2603.16770. https://arxiv.org/abs/2603.16770

10. Mannan, T. et al. (2025). UniFFBench: Evaluating Universal Machine Learning Force
    Fields Against Experimental Measurements. arXiv:2508.05762.
    https://arxiv.org/abs/2508.05762

11. Cavender, C.E. et al. (2025). Structure-Based Experimental Datasets for Benchmarking
    Protein Simulation Force Fields. LiveCOMS 6(1): 3871.
    https://pmc.ncbi.nlm.nih.gov/articles/PMC12823150/

12. scPerturBench (2025). Benchmarking algorithms for generalizable single-cell
    perturbation response prediction. Nature Methods.
    https://www.nature.com/articles/s41592-025-02980-0

13. "DL does not outperform linear baselines" (2025). Deep-learning-based gene
    perturbation effect prediction does not yet outperform simple linear baselines.
    Nature Methods. https://www.nature.com/articles/s41592-025-02772-6

14. Heidari, M. et al. (2026). Evaluating Single-Cell Perturbation Response Models Is
    Far from Straightforward. bioRxiv.
    https://www.biorxiv.org/content/10.64898/2026.02.14.705879v1

15. Systema (2025). Systema: a framework for evaluating genetic perturbation response
    prediction beyond systematic variation. Nature Biotechnology.
    https://www.nature.com/articles/s41587-025-02777-8

16. Tahoe-x1 (2025). Tahoe-x1: Scaling Perturbation-Trained Single-Cell Foundation
    Models to 3 Billion Parameters. bioRxiv.
    https://www.biorxiv.org/content/10.1101/2025.10.23.683759v1

17. Tahoe-100M (2025). Tahoe-100M: A Giga-Scale Single-Cell Perturbation Atlas for
    Context-Dependent Gene Function and Cellular Modeling. bioRxiv.
    https://www.biorxiv.org/content/10.1101/2025.02.20.639398v1

18. AlphaCell (2026). Towards building a World Model to simulate perturbation-induced
    cellular dynamics by AlphaCell. bioRxiv.
    https://www.biorxiv.org/content/10.64898/2026.03.02.709176v1

19. X-Cell (2026). X-Cell: Scaling Causal Perturbation Prediction Across Diverse
    Cellular Contexts via Diffusion Language Models. bioRxiv.
    https://www.biorxiv.org/content/10.64898/2026.03.18.712807v1

20. Scouter (2026). Scouter predicts transcriptional responses to genetic perturbations
    with large language model embeddings. Nature Computational Science 6: 21-28.
    https://www.nature.com/articles/s43588-025-00912-8

21. Krueger, R. et al. (2025). Generalized design of sequence-ensemble-function
    relationships for intrinsically disordered proteins. Nature Computational Science.
    https://www.nature.com/articles/s43588-025-00881-y

22. BioKinema (2026). Physically Grounded Generative Modeling of All-Atom Biomolecular
    Dynamics. bioRxiv. https://www.biorxiv.org/content/10.64898/2026.02.15.705956v1

23. ICed-ENM (2026). Mutation-induced reshaping of protein conformational dynamics
    revealed by a coarse-grained modeling framework. bioRxiv.
    https://www.biorxiv.org/content/10.64898/2026.03.29.715126v1

24. Notin, P. et al. (2023). ProteinGym: Large-Scale Benchmarks for Protein Fitness
    Prediction and Design. NeurIPS Datasets Track.
    https://proteingym.org/

25. Lindorff-Larsen, K. et al. (2012). Systematic Validation of Protein Force Fields
    against Experimental Data. PLoS ONE 7(2): e32131.

26. Robustelli, P. et al. (2018). Developing a molecular dynamics force field for both
    folded and disordered protein states. PNAS 115: E4758-E4766.

27. PerturBench (2024). PerturBench: Benchmarking Machine Learning Models for Cellular
    Perturbation Analysis. arXiv:2408.10609. https://arxiv.org/abs/2408.10609

28. Li, J. et al. (2024). AI2BMD: Accurate Biomolecular Dynamics. Nature 636: 1012.
    https://www.nature.com/articles/s41586-024-08127-z

29. AceFF (2026). AceFF: A State-of-the-Art Machine Learning Potential for Small
    Molecules. arXiv:2601.00581. https://arxiv.org/abs/2601.00581

30. Batatia, I. et al. (2026). MACE-POLAR-1: A Polarisable Electrostatic Foundation
    Model for Molecular Chemistry. Cambridge/Csanyi group.
