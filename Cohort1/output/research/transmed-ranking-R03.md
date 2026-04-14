---
agent: transmed
round: 3
date: 2026-04-14
type: ranking
---

# Round 3 Ranking: Cross-Specialist Evaluation of 6 Combined Projects

**Agent:** Dr. Translational & Clinical Computational Biology Expert (transmed)
**Perspective:** Clinical impact, patient benefit, translation readiness, precision medicine fit, healthcare system relevance

---

## Ranking Framework and Perspective

As the translational specialist, I assess projects through a lens that is complementary to
but distinct from purely methods-focused evaluations. My criteria weight:

1. **Translational relevance**: Does this project address a problem that ultimately matters
   to patients, clinicians, or drug developers? Is the path from computational output to
   clinical or therapeutic action clear?
2. **Publication impact**: Which venue is appropriate, and what clinical/applied community
   would cite this work?
3. **Novelty** from the application standpoint, not just the methods standpoint.
4. **Feasibility** without wet-lab access -- all validation must be computational or via
   existing published data.
5. **Timeline**: Achievable in Summer 2026 by a small team.

I have re-read all six deep-dive reports, the Round 2 synthesis, and conducted additional
web research spanning: ClinVar/VUS reclassification landscape, AlphaMissense failure modes,
BioEmu mutation prediction performance, the perturbation prediction controversy, MLFF
clinical relevance, and the molecular design benchmark gap. I also reviewed the pVEP
preprint (Schilder et al., bioRxiv April 2026) on genetic background and variant effect
heterogeneity, and the gene/domain-calibration paper (Chen et al., bioRxiv March 2026).

My rankings below are deliberately calibrated to penalize projects where the path to
clinical or applied impact is long or indirect, and to reward projects where the
computational contribution directly touches a bottleneck that the field recognizes.

---

## Project Scorecards

---

### Project 1: Gamma -- Dynamics-to-Function Mapping

**Core claim:** BioEmu-generated conformational ensembles + ProteinGym DMS data, bridged
by a learned ensemble-to-function mapping framework.

**Translational assessment:**

This project sits at an intellectually exciting frontier -- the post-AlphaFold question of
whether dynamics determines function -- but its translational path is indirect. The output
is a framework that predicts how variants change conformational ensembles and thereby alter
fitness scores. This is useful for protein engineering and basic mechanistic understanding,
but the connection to patient-relevant decisions (which mutation causes disease? which drug
binding site is accessible?) requires many downstream steps.

Specific concerns from a translational standpoint:
- BioEmu's mutation effect prediction has already shown a key weakness: Aryal et al. (Int.
  J. Mol. Sci. 2026) demonstrated BioEmu "fails to predict mutation-induced shifts in
  conformational distribution" and "cannot effectively differentiate driver and passenger
  mutations." This is not fatal, but the ensemble-to-function mapping layer must compensate
  for upstream ensemble generation errors, which adds risk.
- ProteinGym DMS data (2.7M variants, 217 assays) is a good benchmark, but most DMS assays
  measure stability or growth fitness, not clinically actionable endpoints. The overlap with
  medically actionable variants (e.g., hereditary cancer genes, cardiac channelopathies) is
  small.
- The translation to drug discovery (e.g., predicting allosteric site accessibility) is
  highly speculative from this project's scope and would require substantial follow-on work.
- The 6-18 month competition window is real: Microsoft (BioEmu team) and Marks Lab
  (ProteinGym) are the closest groups, and both have the incentive and resources to do this
  combination.

**What saves it translationally:** Conformational dynamics is genuinely relevant to variant
interpretation (GOF/LOF), allosteric drug targeting, and cryptic pocket discovery -- but
Project Gamma's scope stops at DMS fitness prediction, not at these downstream applications.
It is scientifically excellent but clinically indirect.

**Venue:** Nature Computational Science (strong fit -- methodology, scale, novelty)
**Competing approaches:** BioEmu augmented simulation (Jan 2026 preprint); SeqDance/ESMDance
(PNAS Jan 2026); QDPR (JCIM 2025). None combine ensemble-to-function with DMS at scale.

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Novelty | 8 | First explicit ensemble-to-function mapping; BioEmu+ProteinGym combo unpublished |
| Scientific impact | 8 | Addresses central post-AF question; broad interest |
| Computational feasibility | 8 | BioEmu MIT-licensed, pip-installable; ProteinGym standardized; 8.2K GPU-hrs achievable |
| Timeline feasibility | 8 | 6 weeks on 8 H200s; well-scoped pipeline |
| Publication potential | 8 | Strong Nature Comp Sci fit; clear story arc |
| **Weighted mean** | **8.0** | High across all dimensions; small clinical distance is the limiting factor |

**Translational bonus/penalty:** -0.5 (clinical path is indirect; DMS fitness != patient outcome)
**Final transmed score: 7.5**

---

### Project 2: Delta -- PerturbMark (Cross-Context Perturbation Benchmark)

**Core claim:** Definitive cross-context benchmark resolving the deep learning vs. linear
baseline controversy in perturbation prediction. Centered on Tahoe-100M (100M cells,
1,100 perturbations, 50 cancer cell lines, CC0 license) plus Replogle, Norman, X-Atlas.

**Translational assessment:**

This is the project I find most compelling from a translational standpoint despite it being
a benchmark, not a model. Here is why: the perturbation prediction controversy is not merely
academic. If deep learning models genuinely cannot predict cellular responses to genetic and
chemical perturbations, then the entire premise of "virtual cells" for drug discovery --
which has attracted enormous investment from ARC Institute, CZI, Tahoe Therapeutics (now
with Tx1, a 3B-parameter model), and Recursion -- rests on an unvalidated foundation. A
rigorous independent benchmark that resolves this directly informs:

1. **Drug target identification**: Which genes, when perturbed, cause cancer-relevant
   transcriptional shifts? Can models generalize across cell types to predict drug MoA?
2. **Drug response prediction**: Can single-cell perturbation models predict patient-
   specific drug responses? Tahoe Therapeutics reports "up to 15.04% improvement in
   patient-specific response predictions" using Tahoe-100M, but this claim is not
   independently benchmarked.
3. **Clinical trial design**: Virtual cell predictions are being used to prioritize clinical
   trial designs (Tahoe, Recursion). If the models do not generalize, this is a risk.
4. **The controversy is unresolved**: Ahlmann-Eltze et al. (Nature Methods 2025) says DL
   fails. The "Well-Calibrated Metrics" paper (bioRxiv 2025) says DL wins if you measure
   right. X-Cell (Xaira, March 2026) claims 5x Pearson improvement. No one has applied all
   of these methods to a single, standardized dataset with locked evaluation protocols.
5. **Tahoe-100M as anchor**: The Tahoe dataset's CC0 license, massive scale (50 cancer
   lines x 1,100 small molecules x 100M cells), and direct drug-relevance make it the ideal
   anchor for a clinical-context perturbation benchmark. The Arc Institute Virtual Cell
   Challenge (annual) provides an existing community infrastructure to build on.

Clinical translation chain here is shorter than for most computational projects: perturbation
prediction directly maps to drug MoA, drug response, and target identification.

**Key risks:** Benchmark papers are often Nature Methods rather than Nature Comp Sci;
competitive space from Arc Institute, CZI is real (though none has built the cross-context
benchmark with proper statistical controls). The scouting report notes scPerturBench (Nature
Methods 2025, 27 methods x 29 datasets) already exists -- Delta must substantially extend
this by incorporating Tahoe-100M and applying the "cross-context generalization" framing
with controlled statistical evaluation that scPerturBench lacked.

**Venue:** Nature Methods (primary target, precedent from Ahlmann-Eltze et al., scPerturBench);
Nature Computational Science (possible if framed as resolving a field-wide crisis)
**Clinical relevance:** HIGH -- directly touches drug discovery, virtual cells, and target ID

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Novelty | 7 | The "cross-context with Tahoe-100M + statistical controls" framing is novel; but scPerturBench precedent creates overlap risk |
| Scientific impact | 9 | Resolves the #1 methodological controversy in computational biology right now; cited immediately by Tahoe, CZI, ARC, Recursion |
| Computational feasibility | 10 | 1-2K GPU-hrs is tiny; Tahoe-100M is CC0; all methods open-source |
| Timeline feasibility | 10 | The most feasible project in the set by a large margin |
| Publication potential | 8 | Nature Methods near-certain; Nat Comp Sci possible; community readership perfectly aligned |
| **Weighted mean** | **8.8** | Highest feasibility and impact in the set from transmed view |

**Translational bonus/penalty:** +0.5 (unusually direct clinical translation for a benchmark; drug discovery community is the immediate reader)
**Final transmed score: 9.3**

---

### Project 3: Alpha-M -- MLFF Biomolecular Crash Test

**Core claim:** First systematic benchmark of ML force fields (MACE-OFF23, SO3LR, AI2BMD,
LiTEN-FF, ANI-2x) against experimental biophysical observables (NMR order parameters,
chemical shifts, J-couplings, SAXS profiles, HDX-MS) for folded proteins. ~15 proteins,
50 ns simulations per protein/FF. 180K-270K GPU-hrs.

**Translational assessment:**

Alpha-M is the highest-rated project by R2 score (8.7), and I understand why from a
pure-methods standpoint: it fills a genuine blind spot in the MLFF field. But from a
translational perspective, this project has the most indirect path to clinical or drug
discovery relevance of any in the set.

The clinical path requires two long downstream hops:
1. MLFFs improve over classical FFs for biomolecular simulation
2. Better biomolecular simulations improve drug binding affinity prediction / ADMET / VEP

Neither hop is guaranteed. The history of improved simulation accuracy not translating
to better drug discovery outcomes is long. The TEA Challenge 2023 (Chemical Science 2025)
already "crash-tested" MLFFs against DFT (not NMR) for peptides and found significant
failures -- and that was against a purely computational reference. The UniFFBench (August
2025) found MLFFs showing "a substantial reality gap between computational benchmarks and
experimental applicability" for materials science. Alpha-M will almost certainly find the
same for biomolecules -- which is a scientifically important finding, but one that has been
anticipated and will surprise few.

Specific clinical translation weaknesses:
- NMR order parameters (S2) for small folded proteins are biophysical quality metrics, not
  proxies for drug binding or disease variant interpretation
- Protein systems in this benchmark (crambin, ubiquitin, GB3, etc.) are biophysics
  training proteins, not therapeutic targets or disease-relevant proteins
- The MLFF community is primarily academic/methods-focused; the drug discovery community
  uses classical FFs + FEP (e.g., Schrodinger, OpenFE) and has not adopted MLFFs at scale
- GEMS (DeepMind/Unke, Science Advances 2024) explicitly acknowledged the NMR comparison
  gap but did not do it -- suggesting the community does not yet consider this comparison
  essential for utility

What saves it scientifically: This benchmark would be cited immediately by all MLFF
developers and would influence how the field validates new models. The finding of a
"reality gap" (likely) would be impactful. The compute is available. The competitive space
is empty. But the readership is physics/methods, not clinical/translational.

**Venue:** Nature Computational Science (strong fit for a methods benchmark with definitive
findings); possibly Journal of Chemical Theory and Computation for a more conservative scope.
**Clinical relevance:** LOW-to-MEDIUM (long chain from MLFF quality to drug discovery impact)

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Novelty | 9 | Confirmed: no such benchmark exists despite urgent need; UniFFBench (materials) is the closest analogue |
| Scientific impact | 8 | Will influence the entire MLFF validation paradigm; but impact is methods-community specific |
| Computational feasibility | 5 | 180K-270K GPU-hrs is substantial; 2-3 months of dedicated HPC; tight for Summer 2026 |
| Timeline feasibility | 5 | Most compute-intensive project by 10-100x; protects competitive advantage but limits iteration |
| Publication potential | 8 | Nature Comp Sci appropriate for definitiveness; but scope must be right-sized |
| **Weighted mean** | **7.0** | Strong novelty, lower on feasibility/timeline than reported; compute risk is real |

**Translational bonus/penalty:** -1.0 (clinical path is the most indirect of all 6 projects; biophysics quality metrics do not map to therapeutic outcomes without substantial follow-on)
**Final transmed score: 6.0**

Note: I acknowledge this is a significant departure from the R2 composite score (8.7).
This reflects a genuine perspective difference: from a methods/multisim standpoint, Alpha-M
is the most rigorous contribution. From a translational standpoint, it is the furthest from
the patient. Both views are legitimate; the orchestrator should weight them accordingly.

---

### Project 4: Alpha-L -- LiveBioBench (Cross-Modal FM Benchmark + UQ)

**Core claim:** First cross-modal, temporally-gated, UQ-aware benchmark for biological
foundation models. Applies temporal cutoffs to prevent contamination. Covers protein, DNA,
molecule, and single-cell modalities. Documents GPT-5 28.3% accuracy drop on uncontaminated
data vs. contaminated.

**Translational assessment:**

LiveBioBench occupies an important but ambiguous position. The contamination problem in
biological FM evaluation is real and consequential: if clinical AI models are trained and
evaluated on data that partially leaked into training, their real-world performance will be
systematically overestimated. This matters enormously in precision medicine (variant
interpretation, drug response prediction) where overconfident models can cause harm.

However, the translational path of LiveBioBench itself depends on what modalities and tasks
are included:
- If single-cell and variant interpretation benchmarks are included, the downstream
  beneficiary is clinical genomics and drug discovery
- If it is primarily protein structure prediction tasks, the clinical relevance is lower
- The UQ component is directly translatable: calibrated uncertainty is required for any AI
  model to be clinically usable (FDA guidance on clinical AI requires uncertainty estimation)

Specific translational arguments for LiveBioBench:
1. **Regulatory relevance**: FDA, EMA, and clinical laboratory accreditation bodies (CAP,
   CLIA) are increasingly requiring AI validation on temporally held-out data. LiveBioBench
   provides the first rigorous methodology for temporal validation of biological FMs.
2. **The 28.3% inflation finding**: This is directly actionable. If clinical AI tools in
   genomics (e.g., genome interpretation, pharmacogenomics) show similar contamination-
   driven inflation, their clinical utility is overstated. A cross-modal study that
   documents this across genomic/molecular/protein modalities would be directly cited by
   clinical informaticists and regulators.
3. **LiveProteinBench precedent** (December 2025): The protein-only version is already
   published. LiveBioBench's extension to cross-modal is the novel contribution.
4. **Competition risk**: The competitive space is described as "entirely empty" -- but
   this is the kind of benchmark that large groups (CZI, Arc, EMBL-EBI) could build quickly
   once the concept is validated by the protein-only version.

Translational weakness: The benchmark itself does not generate new biological knowledge --
it characterizes the quality of existing tools. The clinical community uses benchmarks as
evidence to adopt or reject AI tools, but the direct translational chain requires that the
benchmarked tools are clinically relevant. Alpha-L must include clinically relevant tasks
(variant pathogenicity, drug response, splicing) to have translational weight.

**Venue:** Nature Methods (most likely precedent from LiveBench, scPerturBench, PFMBench);
Nature Computational Science (possible if framed as the first rigorous FM evaluation standard)
**Clinical relevance:** MEDIUM (indirect but real; regulatory and clinical validation require this type of evidence)

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Novelty | 8 | Cross-modal + temporal gating + UQ in combination is novel; LiveProteinBench covers protein-only |
| Scientific impact | 8 | Documents 28% FM inflation; influences how clinical tools are validated |
| Computational feasibility | 9 | 1.5K-16K GPU-hrs depending on scope; well-scoped and modular |
| Timeline feasibility | 9 | Can ship incrementally; protein + one additional modality is a complete paper |
| Publication potential | 8 | Nature Methods near-certain; scope expansion enables Nat Comp Sci |
| **Weighted mean** | **8.4** | High across all dimensions; modest translational discount for indirectness |

**Translational bonus/penalty:** -0.3 (slightly indirect; translational impact conditional on including clinically-relevant tasks like variant interpretation or pharmacogenomics)
**Final transmed score: 8.1**

---

### Project 5: Alpha-G -- End-to-End Molecular Design Benchmark

**Core claim:** First benchmark evaluating the full drug design pipeline: target selection
→ molecular generation → docking/scoring → ADMET filtering → synthesizability → retrospective
validation against actual drug progression data. 30-50 targets with documented clinical
progression. 20K-85K GPU-hrs.

**Translational assessment:**

Alpha-G is perhaps the most directly relevant project to the pharmaceutical industry of the
six, but it is also the most logistically challenging. My deep-dive read and web research
confirms the gap: MolGenBench (November 2025) covers generation + activity but not ADMET
or synthesizability. "Beyond Affinity" (January 2026) covers generation + docking but not
ADMET or outcomes. No benchmark integrates all pipeline stages with retrospective validation.

The translational case for Alpha-G is strong:
1. **Drug attrition crisis**: The pharmaceutical industry loses ~90% of drug candidates in
   clinical trials, with ADMET failures and off-target effects accounting for ~50% of
   attrition. If computational drug design methods are evaluated only on binding affinity,
   they optimize for the wrong target. Alpha-G would reframe evaluation around multi-
   objective success metrics that actually predict clinical outcomes.
2. **Industry alignment**: The "Practically Significant Method Comparison Protocols" paper
   (Ash, Wognum et al., JCIM 2025) from J&J, AstraZeneca, Blueprint Medicines, and others
   establishes the methodological need. Alpha-G would be the actual benchmark they called for.
3. **Retrospective validation**: Using ChEMBL (2.8M compounds), BindingDB (3.15M entries),
   and documented drug progression data from ChEMBL drug indications and approved drugs,
   the benchmark can test whether computational methods would have selected known clinical
   successes over failures in retrospective scenarios.
4. **Clear publication impact**: The "affinity-validity trade-off" (Zhang et al., 2026) is
   an established finding in the field. Alpha-G would characterize the full multi-objective
   trade-off landscape, which is the paper that drug discovery researchers need.

Translational weaknesses:
- **Massive curation effort**: 30-50 targets with curated clinical progression data,
  ADMET annotations, synthesizability assessments, and docking results requires extensive
  manual work -- potentially the largest curation effort of any project in the set.
- **Retrospective validation is imperfect**: Drug progression data reflects decisions made
  under incomplete information; using it as ground truth has known confounders (regulatory
  decisions, business choices, IP). This must be carefully handled.
- **Compute is substantial**: 85K GPU-hrs for the comprehensive version, which may push
  Summer 2026 timeline for a complete publication.
- **Scoop risk is real**: MolGenBench, Polaris Hub, and industry consortia are all moving
  toward similar goals. Being second with an incremental extension is worse than being first.

**Venue:** Nature Computational Science (strong fit -- interdisciplinary methods benchmark
with clear drug discovery framing); Nature Methods also plausible.
**Clinical relevance:** HIGH -- drug discovery industry and regulatory science are the direct beneficiaries

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Novelty | 8 | End-to-end pipeline benchmark does not exist; MolGenBench, Beyond Affinity are partial |
| Scientific impact | 9 | Directly addresses the drug attrition crisis; industry-cited immediately |
| Computational feasibility | 7 | 20K GPU-hrs for initial version feasible; 85K for full version stretches Summer 2026 |
| Timeline feasibility | 6 | Curation effort is the bottleneck; 30-50 targets with full pipeline is 3-6 months of work |
| Publication potential | 8 | Strong fit for Nature Comp Sci or Nature Methods; industry relevance ensures readership |
| **Weighted mean** | **7.6** | Strong scientifically; curation bottleneck and timeline risk are real concerns |

**Translational bonus/penalty:** +0.7 (highest direct clinical/industrial translation of any project; drug discovery industry is the primary beneficiary)
**Final transmed score: 8.3**

---

### Project 6: Beta -- ContextVEP (Context-Dependent Variant Effect Prediction)

**Core claim:** First variant effect predictor integrating tissue context (GTEx 54 tissues),
disease context (HPO hierarchy, disease text), mechanism-of-action (GOF/LOF classification),
and penetrance estimation into a unified multi-task framework. Applied to 1M+ VUS. Addresses
AlphaMissense 83% false positive rate in genes like IRF6.

**Translational assessment:**

Beta is the project most directly aligned with my expertise and the one I have the greatest
depth of evidence on. My assessment is nuanced: this is the most clinically important problem
in the set, but the competitive landscape has shifted enough to create real publication risk.

**The clinical urgency is overwhelming:**
- ~231,000 missense VUS in ClinVar (70% of 330K clinical missense variants)
- In multigene cancer panel testing of 1.69M individuals, 41% had at least one VUS (JAMA
  2023) -- meaning millions of patients receive VUS results annually
- Mean time to VUS reclassification: 30.7 months to benign, 22.4 months to pathogenic
- Variant classification inequity: VUS rates disproportionately higher in non-European
  ancestry populations due to underrepresentation in reference databases
- AlphaMissense 83% false positive rate in IRF6 (Frontiers in Genetics 2024); high false
  positive rates in CFTR (PLoS One 2024); unreliable for sarcomeric cardiac genes (Circulation
  Genomic PM 2024); poor for DDR genes in cancer
- Recent gene/domain calibration paper (Chen et al., bioRxiv March 2026) shows calibrated
  VEPs assign evidence to 10.6% more variants and improve discrimination -- but still uses
  standard genome-wide models; multi-context integration is explicitly called for but absent

**The competitive landscape has shifted:**
The pVEP preprint (Schilder et al., bioRxiv April 4, 2026 -- published just 10 days ago)
addresses genetic background as a context variable. DYNA, DIVA, IMPPROVE, popEVE, ML-
Penetrance, and V2P each address fragments. The gene/domain calibration work (Chen et al.
2026) directly improves clinical utility through a different route. No single tool integrates
all four dimensions (tissue, disease, mechanism, penetrance), but the field is converging.

**The remaining gap is real but narrower than Round 1:**
The matrix shows that no existing tool jointly models tissue context + disease context +
mechanism-of-action + penetrance + proteome-wide scale. This is the core Beta claim. But:
- IMPPROVE (Nature Communications 2025) already shows 90% of phenotypes have better single-
  cell tissue-specific prediction than CADD alone -- the tissue context component is partially
  validated
- V2P covers 23 HPO categories across SNVs and indels (disease context partially covered)
- ML-Penetrance covers 10 autosomal dominant diseases
- The integration is the differentiator, and it is still genuinely open

**The language model VUS gap paper (medRxiv February 2026)** shows that ~17% of VUS lack
explicit evidence in ClinVar summaries but could be reclassified using NLP -- this
complements Beta's approach and would strengthen the paper if cited as a parallel route.

**MAVE data is the training data key**: MaveDB (7M+ measurements) and MaveMD (438K
measurements across 32 clinically relevant genes) can reclassify 75% of ClinVar VUS in
covered genes. If Beta incorporated MAVE supervision as a training signal, it would be
substantially stronger.

**Venue:** Nature Genetics (primary target -- variant interpretation is a core NatGen topic);
Nature Medicine (if clinical utility is demonstrated via reclassification); Nature Computational
Science (if framed as an algorithmic advance in multi-context VEP). The specific venue
choice matters: Nature Genetics gives the highest clinical genomics readership.
**Clinical relevance:** VERY HIGH -- directly addresses VUS crisis affecting millions of patients

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Novelty | 7 | Unified multi-context VEP is novel; but pVEP (April 2026), gene-calibration (March 2026), IMPPROVE (2025), DIVA (2025) all reduce novelty. The integration remains open. |
| Scientific impact | 9 | Addresses VUS crisis with 231K+ affected missense variants; AlphaMissense successor framing is compelling; cited by clinical labs immediately |
| Computational feasibility | 9 | 500-1K GPU-hrs is the smallest compute footprint of any project; ESM-2 embeddings pre-computable; GTEx/ClinVar all public |
| Timeline feasibility | 9 | 6-8 weeks of active development once design is finalized; fastest to publishable result |
| Publication potential | 8 | Nature Genetics or Nature Medicine are natural homes; strong clinical readership; but competitor papers in 2026 raise the bar for novelty |
| **Weighted mean** | **8.4** | Excellent across most dimensions; novelty narrowing is the critical risk |

**Translational bonus/penalty:** +1.0 (highest direct clinical benefit of any project; VUS resolution affects patient management, genetic counseling, cascade testing decisions, and health equity for underrepresented populations)
**Final transmed score: 9.4**

---

## Summary Scoring Table

| Project | Code | Novelty | Sci Impact | Comp Feasibility | Timeline | Pub Potential | Raw Mean | Transmed Adj | Final Score |
|---------|------|---------|------------|------------------|----------|---------------|----------|--------------|-------------|
| ContextVEP | Beta | 7 | 9 | 9 | 9 | 8 | 8.4 | +1.0 | **9.4** |
| PerturbMark | Delta | 7 | 9 | 10 | 10 | 8 | 8.8 | +0.5 | **9.3** |
| Molecular Design Benchmark | Alpha-G | 8 | 9 | 7 | 6 | 8 | 7.6 | +0.7 | **8.3** |
| LiveBioBench | Alpha-L | 8 | 8 | 9 | 9 | 8 | 8.4 | -0.3 | **8.1** |
| Dynamics-to-Function | Gamma | 8 | 8 | 8 | 8 | 8 | 8.0 | -0.5 | **7.5** |
| MLFF Crash Test | Alpha-M | 9 | 8 | 5 | 5 | 8 | 7.0 | -1.0 | **6.0** |

*Transmed adjustment reflects the translational specialist's view of direct clinical/applied impact.*
*Raw mean is computed across the five standard criteria. Final score = Raw mean + Transmed Adj.*

---

## Venue Mapping

| Project | Primary Venue | Secondary Venue | Clinical Readership |
|---------|--------------|-----------------|---------------------|
| Beta (ContextVEP) | Nature Genetics | Nature Medicine | Clinical genetics labs, genetic counselors, precision medicine |
| Delta (PerturbMark) | Nature Methods | Nature Comp Sci | Computational drug discovery, virtual cell researchers |
| Alpha-G (Mol Design) | Nature Comp Sci | Nature Methods | Drug discovery, pharma R&D, cheminformatics |
| Alpha-L (LiveBioBench) | Nature Methods | Nature Comp Sci | Biological AI/ML methods community, regulatory science |
| Gamma (Dynamics-fn) | Nature Comp Sci | Nature Structural Mol Biol | Protein engineering, structural biology |
| Alpha-M (MLFF) | Nature Comp Sci | J. Chem. Theory Comput. | Computational chemistry, biophysics |

---

## Top Pick: Beta (ContextVEP)

**Rationale:** From a translational perspective, Beta is the top pick by a meaningful margin.

The VUS problem is one of the most significant unresolved challenges in clinical genetics,
directly affecting millions of patients annually. The gap between what is possible
computationally (integrating tissue context, disease mechanism, penetrance, population
diversity) and what is deployed clinically (predominantly AlphaMissense with its well-
documented false positive rates) is large and consequential. A unified ContextVEP that
integrates all four context dimensions would be an immediate tool for clinical labs, genetic
counselors, and precision medicine programs.

The compute requirement is the smallest of any project (500-1K GPU-hrs), the timeline is
fastest, and all data are public. The partial addressing by recent tools (pVEP April 2026,
gene-calibration March 2026, IMPPROVE 2025) confirms that the field recognizes the problem
and is making progress -- but the full integration gap remains open.

The health equity dimension of Beta is also compelling: VUS rates are disproportionately
higher in non-European populations, and a context-aware model trained to account for
population diversity (gnomAD v4 with 730K exomes from diverse populations) would directly
address variant interpretation inequity. This is a publishable narrative beyond the pure
methods contribution.

The competitive risk is real but manageable: no existing preprint presents the four-context
integrated architecture at proteome scale. The beta project must prioritize submission speed
(which its small compute footprint enables) and must clearly differentiate from pVEP (which
addresses background context, not tissue/disease/mechanism integration).

**For CohortArchitect guidance:** Beta should be paired with ReggEno's non-coding VEP gap in
a unified "ContextVEP 2.0" that covers both coding and non-coding variants in an integrated
framework. The compute (still under 2K GPU-hrs combined) is well within limits, and the
joint coding + non-coding claim is substantially more novel and harder to scoop than either
alone.

---

## Best Combination: Beta + Delta

**Why this combination works:**

Beta (ContextVEP) and Delta (PerturbMark) represent complementary translational contributions:

1. **Beta** solves the variant interpretation bottleneck (static, individual-level): given a
   patient's variant, what does it do in their specific tissue and disease context?

2. **Delta** solves the perturbation prediction bottleneck (dynamic, population-level):
   given a drug or genetic perturbation across cancer cell lines, can we reliably predict the
   transcriptional response and generalize to new contexts?

Together, they form a coherent story about the failure of context-agnostic computational
tools in clinical settings -- one at the variant level, one at the cellular level -- and
provide validated replacements.

**Practical combination arguments:**
- Both have very low compute requirements (Delta: 1-2K GPU-hrs; Beta: 500-1K GPU-hrs)
- Both are achievable in Summer 2026 as independent papers with potential cross-citation
- The VUS clinical context (Beta) feeds naturally into drug discovery (Delta): once a variant
  is classified, the next question is which therapeutic perturbations will correct the
  cellular phenotype
- Both target clinical translation audiences that are actively reading the field

**Alternative combination: Beta + Alpha-G**
If the orchestrator wants a single drug discovery paper rather than two separate papers, Beta
(which resolves which variants matter) combined with Alpha-G (which tests whether drug design
methods can then design molecules against the validated targets) creates a coherent end-to-end
precision medicine story. The curation burden of Alpha-G is the limiting factor.

---

## Observations and Disagreements with R2 Rankings

**Alpha-M overranked from translational standpoint:** The R2 composite score of 8.7 reflects
the multisim specialist's correctly high assessment of the methods contribution. However, the
translational impact is limited by the choice of benchmark proteins (biophysics training
proteins, not therapeutic targets) and the long chain from improved MLFF accuracy to clinical
or drug discovery outcomes. The compute requirement (180K-270K GPU-hrs) is also a real risk
for Summer 2026 timeline -- 2-3 months of dedicated HPC for simulations alone, leaving little
time for analysis, iteration, and writing. The 8.7 R2 score reflects pure methods quality;
the lower transmed score (6.0) reflects the clinical/applied distance.

**Beta underranked from translational standpoint:** The R2 score of 8.2 (post-combination with
reggeno) reflects the narrowing of the gap by DYNA/DIVA/IMPPROVE. But from a translational
standpoint, partial competitors that address fragments are strong evidence of clinical need,
not of gap closure. The fact that DYNA is cardiac-specific, DIVA lacks tissue/penetrance,
IMPPROVE uses Random Forest (not deep learning), and popEVE ignores all context dimensions
means the clinical utility of each is limited. A unified ContextVEP would supersede all of
them clinically, which is the Nature Genetics/Nature Medicine story.

**Delta slightly underrated in R2:** The R2 score of 8.6 appropriately recognizes PerturbMark's
strength. From the translational lens, the clinical translation chain from perturbation
prediction accuracy to drug discovery outcomes is more direct than the R2 synthesis
acknowledges. The Tahoe Therapeutics "15.04% improvement in patient-specific response
predictions" claim is unvalidated by any independent benchmark -- Delta would fill exactly
that validation gap.

---

## Conclusion and CohortArchitect Recommendation

For Cohort 2, the translational specialist recommends that CohortArchitect prioritize:

**Primary: Beta (ContextVEP)** -- highest clinical urgency, lowest compute risk, fastest
timeline, most direct benefit to patients. Should be expanded to include combined coding +
non-coding (incorporate reggeno gap). MAVE data integration should be explicitly included
as a training signal.

**Secondary: Delta (PerturbMark)** -- resolves the most consequential methodological
controversy in computational drug discovery; aligns with drug discovery industry's active
interest; defines ground truth for Tahoe-x1 and competing virtual cell models.

**Tertiary: Alpha-G (Molecular Design Benchmark)** -- strong translational case but curation
bottleneck is the risk; Cohort 2 should assess whether the curation effort is achievable
within Summer 2026 or requires scoping down to 10-15 targets.

**Deprioritize for Cohort 2 (from translational standpoint):**
- Alpha-M: Excellent methods contribution; low translational urgency; reserve compute for
  more clinically-relevant projects
- Gamma: Strong scientifically; but limited clinical translation in current scope
- Alpha-L: Important for the FM evaluation community; but secondary to the above three
  for translational impact

---

## References

1. Ahlmann-Eltze C, Huber W, Anders S. "Deep-learning-based gene perturbation effect
   prediction does not yet outperform simple linear baselines." Nature Methods (2025).

2. Aryal M et al. "Assessing the Performance of BioEmu in Understanding Protein Dynamics."
   Int. J. Mol. Sci. (2025), vol. 27, 2896. [BioEmu fails to differentiate driver/passenger
   mutations and mutation-induced conformational shifts.]

3. Chen Y, Fayer S et al. "Gene- and domain-aware calibration increases the clinical utility
   of variant effect predictors." bioRxiv (March 31, 2026). doi:10.64898/2026.02.17.706269.

4. Findlay GM et al. "Accurate classification of BRCA1 variants with saturation genome
   editing." Nature (2018), vol. 562, 217-222. [BRCA1 VUS classification at scale.]

5. Hecher MS et al. "Language models reveal evidence gaps in variants of uncertain
   significance." medRxiv (February 2026). doi:10.64898/2026.02.28.26347206.

6. Huang J, MacKerell AD. "CHARMM36m: an improved force field for folded and intrinsically
   disordered proteins." Nature Methods (2017), vol. 14, 71-73.

7. Lewis AM et al. (BioEmu). "Scalable emulation of protein equilibrium ensembles with
   generative deep learning." Science (2025), vol. 369, 270-278.

8. Mannan et al. "UniFFBench: Benchmarking universal machine learning force fields."
   arXiv:2508.05762 (August 2025). [Materials MLFFs show substantial reality gap vs.
   experimental data.]

9. Nguyen et al. "Tahoe-100M: A Giga-Scale Single-Cell Perturbation Atlas for Context-
   Dependent Gene Function and Cellular Modeling." bioRxiv (February 2025).
   doi:10.1101/2025.02.20.639398.

10. Notin P et al. "ProteinGym: Large-Scale Benchmarks for Protein Design and Fitness
    Prediction." NeurIPS (2023); PMC10723403.

11. Omoyele O et al. "IMPPROVE: Phenotype-Specific Models for Variant Pathogenicity."
    Nature Communications (2025). [90% of phenotypes have better single-cell tissue-specific
    VEP performance than CADD alone.]

12. Pejaver V et al. "Evidence-based calibration of computational tools for missense variant
    pathogenicity classification and ClinGen recommendations for clinical use of PP3/BP4
    criteria." bioRxiv (2022). doi:10.1101/2022.03.17.484479.

13. Schilder BM et al. "Genetic background shapes AI-predicted variant effects." bioRxiv
    (April 4, 2026). doi:10.64898/2026.04.04.715328. [pVEP: genetic context across 3,819
    globally diverse genomes shapes variant pathogenicity predictions.]

14. Skinnider MA et al. "Combinatorial prediction of therapeutic perturbations using
    causally inspired neural networks." Nature Biomedical Engineering (2025), vol. 9.
    doi:10.1038/s41551-025-01481-x.

15. Tahoe Therapeutics. "Tahoe-x1: Scaling Perturbation-Trained Single-Cell Foundation
    Models to 3 Billion Parameters." bioRxiv (October 2025). doi:10.1101/2025.10.23.683759.

16. Thomas M et al. "MolScore: A scoring and evaluation framework for generative molecular
    design." JCIM (2024). [Comprehensive evaluation toolkit exposing gaps in current
    molecular design evaluation.]

17. Tilli TM et al. "Variants of uncertain significance in precision oncology: nuance or
    nuisance?" PMC11299927. Cancer discovery challenge with VUS in oncology context.

18. Unke OT et al. "GEMS: Generalized Equivariant Machine-learning Simulations." Science
    Advances (2024). [GEMS explicitly acknowledges NMR comparison has not been done.]

19. Vinas Torne et al. (Systema). "Systematic evaluation of perturbation prediction methods
    reveals that models learn systematic variation rather than perturbation biology."
    Nature Biotechnology (August 2025). [Perturbation models learn confounders, r=0.91 for
    scGPT vs. systematic variation.]

20. Wang W et al. "AI2BMD: Biomolecular dynamics with machine-learned quantum-mechanical
    force fields trained on diverse chemical fragments." Science Advances (2024).
    [Only MLFF to publish NMR comparison; limited to dipeptides.]

21. Wong D, Hill C, Moccia M. "CRISPR-informed mean baseline surpasses DL models by
    4.7x-213.9x." Bioinformatics (June 2025). [Further evidence against DL perturbation
    prediction.]

22. Zhang et al. "Beyond Affinity: Benchmark of 15 molecular design models revealing
    affinity-validity trade-off." bioRxiv (January 2026). [3D methods exceed binding
    affinity but fail chemical validity -- end-to-end benchmark is needed.]

23. Zhao N et al. "Organ-specific prioritization and annotation of non-coding regulatory
    variants in the human genome." bioRxiv (January 2026). doi:10.1101/2023.09.07.556700.
    [RegulomeDB v2 expansion for organ-specific variant prioritization -- Beta complement.]

24. ClinVar statistics 2025. National Library of Medicine. https://www.ncbi.nlm.nih.gov/clinvar/.
    [>3M submitted variant interpretations; ~231K missense VUS.]

25. MaveDB. https://www.mavedb.org/. [>7 million variant effect measurements; MaveMD: 74
    curated datasets, 438K measurements across 32 clinically relevant genes; enables
    reclassification of 75% of ClinVar VUS in covered genes.]
