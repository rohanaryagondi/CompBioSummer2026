---
agent: genchem
round: 3
date: 2026-04-14
type: research-note
---

# Round 3 Rankings: Generative Chemistry Expert Perspective

## Preamble: Evaluator Stance

I am the Generative Chemistry Expert (genchem), and my primary project in this cohort was
**Alpha-G: End-to-End Molecular Design Benchmark**. I am aware of the risk that domain
specialists overvalue their own contribution. This document is an honest attempt to rank
all six combined projects on their merits, drawing on the full body of Round 2 research,
cross-domain reading of all deep-dive reports, and additional targeted literature research
conducted specifically for this round.

My domain is generative molecular design, computational chemistry, ADMET, synthesizability,
and drug discovery pipelines. That expertise is relevant to evaluating **all** projects here:
molecular design benchmarks (Alpha-G, obviously), force field validation (Alpha-M shares
methodological DNA with generative model evaluation), VEP for clinical variants (Beta/ContextVEP
has direct applications in chemical genetics), perturbation prediction (Delta/PerturbMark
directly informs chemical perturbation design), and biophysical ensemble-function relationships
(Gamma touches drug binding site dynamics). I have read every specialist's deep-dive in full
before writing this document.

This ranking represents my independent assessment. Where I disagree with the Round 2 synthesis
scores, I explain why.

---

## Summary Ranking Table

| Rank | Project | R2 Score | Novelty | Impact | Comp Feasi | Time Feasi | Pub Potential | genchem Score | Target Venue |
|------|---------|----------|---------|--------|-----------|-----------|--------------|--------------|-------------|
| 1 | Alpha-M: MLFF Crash Test | 8.7 | 9 | 9 | 7 | 7 | 9 | **8.4** | Nat Comput Sci |
| 2 | Gamma: Dynamics-to-Function | 8.5 | 8 | 9 | 8 | 8 | 9 | **8.4** | Nat Comput Sci |
| 3 | Delta: PerturbMark | 8.6 | 7 | 8 | 9 | 10 | 8 | **8.2** | Nature Methods |
| 4 | Alpha-G: Molecular Design Benchmark | 8.2 | 8 | 8 | 7 | 7 | 8 | **7.8** | Nat Comput Sci |
| 5 | Alpha-L: LiveBioBench | 8.2 | 8 | 7 | 9 | 8 | 7 | **7.8** | Nat Methods/Genome Biol |
| 6 | Beta: ContextVEP | 8.2 | 7 | 7 | 9 | 9 | 7 | **7.8** | Nat Genet/Genome Biol |

**Top pick:** Alpha-M (tied with Gamma; preference to Alpha-M on scientific uniqueness)
**Best combination:** Alpha-M + Gamma (biophysical rigor stack; ensemble quality validated
by NMR, then used for DMS function prediction)

---

## Project-by-Project Detailed Assessments

---

### 1. Alpha-M: MLFF Biomolecular Crash Test

**Round 2 score: 8.7 | genchem score: 8.4**

#### What this project does

Alpha-M proposes the first systematic benchmark of machine learning force fields (MLFFs)
against experimental biophysical observables -- specifically NMR order parameters (S2), J-couplings,
SAXS profiles, and HDX-MS protection factors -- for folded, flexible proteins. The benchmark would
test 6+ open-source MLFFs (AI2BMD, MACE-OFF23, SO3LR, GEMS, LiTEN-FF, ANI-2x) against the
experimental standards that classical force fields have been validated against for 30+ years.

#### Novel verification

My independent research confirms the gap is unambiguously real. The UniFFBench study
(Mannan et al., arXiv 2508.05762, August 2025), which I searched and verified, benchmarked 6 universal
MLFFs against ~1,500 mineral crystal structures and found a "substantial reality gap" between
computational benchmark performance and experimental applicability. This is for materials science,
but the analogy is exact and alarming: when MLFFs were finally tested against experiment rather than DFT,
they frequently failed. The same test has never been done for biomolecular MLFFs.

The TEA Challenge 2023 (Chemical Science, published 2025) crash-tested MACE, SO3krates, sGDML,
and SOAP/GAP on alanine tetrapeptide and a heptapeptide -- the closest thing to an existing protein
MLFF benchmark -- and found kernel-based MLFFs could not even sustain stable 1 ns dynamics. This is
for dipeptides. No one has published similar data for folded proteins with NMR or SAXS observables.

MACE-OFF (Kovacs et al., JACS 2025) computed 3J-couplings for Ala3 peptide and RMSF/power spectra
for crambin but never computed NMR order parameters, chemical shift deviations, or RDCs. SO3LR
(Frank et al., JACS 2026) simulated crambin and a glycoprotein but compared only power spectra and
bilayer properties. The gap is confirmed at the level of specific claims in peer-reviewed literature.

#### Scoring rationale

**Novelty: 9/10.** No comparable benchmark exists for biomolecular MLFFs. The materials science
precedent (UniFFBench, CHIPS-FF) confirms the pattern: the field eventually recognizes this gap and
a group earns high-impact publication credit for filling it first. For biomolecules, no one has
gotten there. The analogous benchmarking effort for classical force fields (Lindorff-Larsen et al.,
JACS 2012; Best et al., J. Chem. Theory Comput. 2012) became highly cited. This could be the
MLFF equivalent.

**Scientific impact: 9/10.** If MLFFs are being used for protein simulation and drug design without
experimental validation, this benchmark could reveal systematic failures that affect thousands of
downstream applications. The field is currently burning GPU-hours on simulations with unknown
accuracy relative to experiment. A "reality check" on MLFF accuracy for experimental observables
would reshape how the MLFF community calibrates and validates new models. High downstream impact
on drug discovery workflows that rely on ML-simulated protein conformations.

**Computational feasibility: 7/10.** The 180,000-270,000 GPU-hour estimate is the largest in this
cohort, and this is a real constraint. The H200/B200 cluster can handle it, but execution requires
careful SLURM scheduling, robust failure recovery, and 2-3 months of dedicated compute time. A tiered
approach (start with 3 proteins x 3 MLFFs, then scale) reduces risk. The data curation for matching
proteins to both BMRB NMR and SASBDB SAXS records requires bioinformatics work to identify the
~50-100 proteins with high-quality data in both databases (BMRB ~21,820 NMR entries; SASBDB 5,272 SAXS
datasets). This is achievable but labor-intensive. Docking it as 7/10 because the compute footprint
is genuinely the largest in this set and scope creep is a real risk.

**Timeline feasibility: 7/10.** Two-to-three months of GPU execution, preceded by ~4 weeks of
target protein curation and pipeline setup, followed by analysis and writing. This fits in summer
2026 for a team that starts immediately and maintains tight scope discipline. But it is the tightest
timeline in this cohort -- any unexpected MLFF instability (force field crashes on proteins, which
the TEA challenge found was common) will cost weeks. Rating 7/10 because feasible but fragile.

**Publication potential: 9/10.** Nature Computational Science is an ideal fit. The journal has
published several MLFF advances (MACE-OFF was JACS, but Nature Comput Sci has published similar
validation frameworks). A "reality gap" paper showing MLFFs fail to reproduce experimental NMR/SAXS
data would be newsworthy within the structural biology and MD simulation communities. Reviewers
will demand comprehensive coverage (why only 3 MLFFs? why only 15 proteins?) but the tiered approach
addresses scope concerns. The "crash test" framing (analogous to the TEA Challenge paper) is
publishable in its own right.

**Key risks:**
1. MLFF crashes/instability during long simulations -- common in the TEA Challenge for some methods.
   Mitigation: Use only well-tested, protein-ready MLFFs with OpenMM-ML integration.
2. Scope creep -- the full benchmark is 180K GPU-hours, but a selective version (5-8 proteins, 3-4
   MLFFs) is publishable at lower compute cost.
3. Someone at DeepMind/Microsoft/Cambridge could publish a partial version (they have direct access to
   GEMS/AI2BMD/MACE-OFF). Risk is medium -- no published preprint or announcement found as of April 2026.

**Competition window:** No announced competing projects. Medium risk from MLFF development groups
who could run this in-house. Estimated 6-12 months before a major MLFF group "does their own validation."

---

### 2. Gamma: Dynamics-to-Function Mapping

**Round 2 score: 8.5 | genchem score: 8.4**

#### What this project does

Gamma proposes to bridge the gap between protein conformational ensemble generation (via BioEmu)
and biological function (quantified via ProteinGym DMS fitness scores). No existing method takes
explicit ensemble properties -- conformational heterogeneity, cryptic pocket frequencies, flexibility
patterns -- as features to predict quantitative functional readouts.

#### Novel verification

BioEmu was published in Science in July 2025 (Lewis et al., Science 369, pp. 270-278) and is MIT-
licensed, pip-installable, and H200-compatible. My research confirms no published or preprint work
as of April 2026 combines BioEmu-generated ensembles with ProteinGym DMS data.

The independent assessment paper (Aryal et al., Int. J. Mol. Sci. 2025, vol. 27, 2896) is
particularly instructive: it found BioEmu "fails to predict a mutation-induced shift in conformational
distribution" and "cannot effectively differentiate driver and passenger mutations." This is not
a dealbreaker -- it is the scientific motivation. The limitation of BioEmu at the ensemble level
is precisely why an ensemble-to-function mapping layer is needed. If BioEmu ensembles partially
capture conformational shifts caused by mutations, then a learned mapping on top of ensemble statistics
(flexibility, SASA, cryptic pocket occupancy) could extract function signal even from imperfect
ensembles.

ProteinGym v1.3 provides 2.7 million DMS measurements across 217 assays -- extraordinary ground truth
depth. The combination of this ground truth with BioEmu ensemble features has not been explored.

From my generative chemistry perspective, this project is analogous to using 3D conformational
generators in molecular design: the value of the generator is not intrinsic -- it is in how downstream
tasks use the conformational information. Structure-based drug design long ago learned that conformational
ensemble docking outperforms single-structure docking. Gamma applies this same insight to protein
function prediction.

#### Scoring rationale

**Novelty: 8/10.** The conceptual gap is clear and confirmed. However, several groups are
approaching from different angles (SeqDance/ESMDance use implicit dynamics; QDPR uses MD-derived
descriptors; Ozkan's GNN uses normal mode analysis). The explicit-ensemble-to-function step is
genuinely novel. Score of 8 rather than 9 because related approaches narrow the novelty somewhat.

**Scientific impact: 9/10.** The central post-AlphaFold question is: "static structures are good,
but what about dynamics?" Gamma directly answers this for one critical application: predicting how
mutations affect function. If BioEmu ensembles improve variant effect prediction beyond sequence-only
or single-structure methods, it validates the ensemble paradigm and opens an entirely new research
direction. The potential for cascading impact (other ensemble generators, other functional readouts,
clinical variant interpretation) is high.

**Computational feasibility: 8/10.** ~8,200 GPU-hours is very manageable on the available HPC cluster.
BioEmu is MIT-licensed and H200-ready. ProteinGym is fully public. The main technical challenge is
the ensemble featurization step -- extracting ensemble statistics that capture biologically relevant
dynamics without including noise. This is a modeling challenge more than a compute challenge, and
it is addressable in the timeframe. Featurization choices (mean/std of SASA, pairwise distances,
cryptic pocket definitions) are the key scientific decision.

**Timeline feasibility: 8/10.** 6 weeks of intensive GPU use (8 H200s) for ensemble generation,
plus compute for feature extraction and model training. Analysis and paper writing fits in summer
2026. The main timeline risk is the 6-18 month estimated competition window: BioEmu is MIT-licensed
and ProteinGym is public, so any well-resourced group could begin this project. But the specific
combination has not appeared in preprints as of April 2026, and the featurization design choices
require careful methodological work that creates a buffer.

**Publication potential: 9/10.** Nature Computational Science is an excellent fit. The paper's
main claim -- "conformational ensembles improve mutation effect prediction beyond sequence-only
methods" -- is directly verifiable against ProteinGym leaderboard. If the method outperforms
current top methods on ProteinGym (current leader is likely ESM-2 or EVE variants, around Spearman
0.45-0.55 depending on protein class), it would be immediately cited by the protein engineering
and drug design communities.

**Key risks:**
1. If BioEmu ensembles are too noisy or too correlated with AlphaFold2 static predictions, the
   additional signal from dynamics may be small. Mitigation: Use diverse functional classes where
   dynamics are known to matter (IDPs, allosteric proteins, membrane proteins).
2. Competition window: Microsoft (BioEmu owners) and the Marks Lab (ProteinGym creators) are both
   aware of this gap. Their silence as of April 2026 is a positive signal but not a guarantee.
3. The project requires careful selection of which ensemble properties to use as features, which
   requires both domain knowledge and experimentation.

**Genchem-specific insight:** From a generative design perspective, Gamma's ensemble-to-function
framework would be immediately applicable to drug binding site characterization. Cryptic pockets
revealed by ensemble generation (BioEmu captures these) are a major target in drug discovery --
characterizing which pockets are functional vs. artifactual using DMS data would be a natural
extension. This cross-domain applicability enhances the paper's impact.

---

### 3. Delta: PerturbMark -- Resolving the Perturbation Prediction Crisis

**Round 2 score: 8.6 | genchem score: 8.2**

#### What this project does

PerturbMark proposes a cross-context, rigorous benchmark for perturbation prediction methods,
resolving the active debate between "DL does not outperform linear baselines" (Ahlmann-Eltze et al.,
Nature Methods 2025) and "DL wins under well-calibrated metrics" (bioRxiv 2025). The benchmark would
use Tahoe-100M (CC0, 100M cells, 1,100 perturbations, 50 cancer cell lines) and standardize
metrics, baselines, and evaluation protocols.

#### Novel verification

My research confirms that the Nature Methods 2025 paper (Ahlmann-Eltze, Huber & Anders) is real,
published, and represents a genuine controversy -- 7 DL models (scGPT, scFoundation, Geneformer,
GEARS, CPA, scBERT, UCE) failed to outperform simple linear baselines on Norman, Adamson, and
Replogle datasets. A counter-paper on bioRxiv (October 2025) claims DL wins under "well-calibrated
metrics" using dynamic range fraction and interpolated duplicate positive controls. This is a genuine
methodological impasse.

Tahoe-100M is confirmed as a real, publicly accessible CC0 dataset (Hugging Face:
tahoebio/Tahoe-100M) with 429GB of single-cell transcriptomic profiles. The scale is unprecedented.
PerturBench (arXiv 2408.10609) and scPerturBench (Nature Methods 2025) represent precursor
benchmarking efforts but use smaller, older datasets and do not include cross-context evaluation
protocols.

#### Scoring rationale

**Novelty: 7/10.** The controversy itself is not new -- PerturBench, scPerturBench, and the
Virtual Cell Challenge 2025 all exist. What would be novel is (a) use of Tahoe-100M's cross-context
design to specifically test context generalization and (b) a definitive adjudication of the metric
debate. The novelty is in the scale, rigor, and adjudicating role -- not in the idea of a perturbation
benchmark itself. Scoring 7 rather than 8 because the benchmark space is genuinely crowded.

**Scientific impact: 8/10.** Resolving this debate would be highly impactful. Every group working
on cell line perturbations, CRISPRi screens, drug response prediction, or virtual cell models
cares about this question. If the answer is "DL never works for perturbation prediction," that
redirects an enormous amount of community effort. If "DL works in context X but fails in context Y,"
that defines productive research directions. The downstream impact on chemical perturbation design
(my domain) is direct: better perturbation prediction models would improve compound screening
prioritization. Impact score of 8 rather than 9 because the controversy may partially resolve itself
as more methods papers are published -- the benchmark becomes less urgent if the field self-corrects.

**Computational feasibility: 9/10.** The 1,000-2,000 GPU-hour estimate is the lowest in this cohort.
Tahoe-100M is public and CC0. All methods (GEARS, CPA, scGPT, X-Cell, SCALE, AlphaCell, AetherCell,
pertTF) are open-source. The main challenge is data engineering at scale (100M cells requires
careful memory management and distributed processing) and careful experimental design (which
perturbations, which cell lines, which contexts, which metrics). But computationally, this is very
accessible. Score of 9.

**Timeline feasibility: 10/10.** With 1,000-2,000 GPU-hours needed, this is the most timeline-
friendly project in the cohort. A focused team could complete data processing, model evaluation,
and analysis within 2-3 months. Summer 2026 timeline is very comfortable. Score of 10.

**Publication potential: 8/10.** Nature Methods is the natural home for a methodological benchmark
paper with this profile. The precedent is strong: Nature Methods has published scPerturBench and the
Ahlmann-Eltze et al. paper in 2025. A definitive cross-context benchmark with Tahoe-100M data
would be a clear acceptance-caliber submission. The caveat for the score of 8 (not 9): benchmark
papers without a new method contribution can be competitive for Nature Methods but not always for
Nature Computational Science. The team would need to be honest about venue targeting. If the paper
adjudicates the metric debate AND introduces a new metric OR a new method, it could reach Nature
Computational Science. As a pure benchmark, Nature Methods is more realistic.

**Key risks:**
1. The controversy may partially resolve before submission. Multiple groups (CZI, scPerturBench
   team, Virtual Cell consortium) are working on this.
2. The competitive space is the most crowded of all projects. PerturBench exists. scPerturBench
   exists. The Arc Institute Virtual Cell Challenge ran in 2025. Differentiation from these
   predecessors requires clear articulation of what cross-context evaluation adds beyond previous
   work.
3. As a benchmark-only paper, Nature Computational Science targeting may be difficult without a
   novel method contribution.

**Genchem-specific insight:** Chemical perturbation prediction (small molecule effects on
transcription) is directly relevant to drug discovery. Tahoe-100M includes 1,100 small molecule
perturbations across 50 cancer cell lines. If PerturbMark specifically evaluates chemical perturbation
prediction (not just genetic), it becomes more relevant to my domain and differentiates from the
purely genetic perturbation benchmarks that dominate the literature.

---

### 4. Alpha-G: End-to-End Molecular Design Benchmark

**Round 2 score: 8.2 | genchem score: 7.8**

#### Conflict of interest disclosure

This is my project. I will score it honestly and critically.

#### What this project does

Alpha-G proposes the first benchmark that evaluates the complete molecular design pipeline:
target selection -> molecular generation -> 3D structural quality -> molecular docking ->
ADMET prediction -> synthesizability -> retrospective validation against drug progression data.
The key innovation is the "attrition funnel" metric that tracks what fraction of generated
molecules survive each filter, mirroring real pharmaceutical drug discovery.

#### Novel verification

My Round 2 deep dive confirmed the gap is real and deepening. MolGenBench (bioRxiv November 2025,
120 targets, 220,005 active molecules) is the closest competitor but stops at generation metrics --
it does not include ADMET, synthesizability, or retrospective outcome validation. The "Beyond
Affinity" benchmark (Zhang et al., January 2026) compares generation-to-docking but not beyond.
GenBench3D (Baillif et al., 2024) covers 3D quality only. No existing benchmark covers the full
pipeline.

My Round 3 research identified a critical new finding: **TANGO** (Guo and Schwaller, Nature
Computational Science 2026) proposes direct optimization for synthesizability in generative
molecular design using retrosynthesis models. SynGFN (Nat Comput Sci 6, 29-38, 2026) models
molecular design as a cascade of simulated chemical reactions. Both papers integrate synthesizability
INTO generation -- this is a different approach from evaluating generation separately, but it
partially narrows the evaluation gap by showing the field cares deeply about synthesizability.
These papers confirm the relevance of our direction but increase competitive pressure.

#### Scoring rationale

**Novelty: 8/10.** The full-pipeline evaluation concept is genuine and unfilled. However, the
space is increasingly active. MolGenBench (November 2025), TANGO (2026), SynGFN (2026), and the
"Beyond Affinity" paper (2026) all represent partial convergence on the problem. The novelty
advantage is eroding faster than for other projects. Score is 8 rather than 9 because the
competitive landscape is busier than I estimated in Round 2.

**Scientific impact: 8/10.** If the benchmark reveals that pipeline attrition rates differ 10-100x
across methods (as I estimated in Round 2), this would substantially redirect the field toward
evaluating practical drug design utility rather than distribution learning metrics. The impact on
pharmaceutical AI is real. However, benchmark papers have diminishing returns -- the field has
many benchmarks, and adoption requires active community buy-in. The Polaris Hub and TDC-2 platforms
are already well-established and have industry backing. A new benchmark must integrate with or
clearly supersede these.

**Computational feasibility: 7/10.** The full benchmark is 80,000-85,000 GPU-hours, but a tiered
approach yields an initial publication at 20,000 GPU-hours. The bottleneck is not GPU compute --
it is CPU compute for retrosynthesis (AiZynthFinder, ASKCOS: ~70,000 CPU-hours). The HPC cluster
has hundreds of CPU nodes, so this is feasible but requires careful orchestration. The most
challenging component is target curation: identifying 30-50 targets with full public progression
data from ChEMBL, BindingDB, and SureChEMBL requires 2-4 weeks of dedicated manual work. This is
not a showstopper, but it is real human effort that could delay the project. Score of 7.

**Timeline feasibility: 7/10.** The ~15-week project timeline is tight. Curating targets,
building the pipeline, running tiered evaluation, and writing the paper within summer 2026 is
feasible for a focused team but leaves little buffer for unexpected obstacles (AiZynthFinder
failures on unusual chemotypes, docking software license issues, ChEMBL data quality problems).
Score of 7. The single most concerning risk is the target curation step -- if fewer than 30 targets
have usable retrospective progression data, the benchmark loses its key differentiator.

**Publication potential: 8/10.** Nature Computational Science has published several molecular
design papers (ECloudGen 2025, SynGFN 2026, TANGO 2026). A definitive pipeline benchmark framed
as revealing systematic attrition failures of AI drug design would fit well. The "benchmark reveals
AI drug design is more broken than believed" narrative is powerful and publishable. Reviewers will
demand (a) why 30-50 targets is enough, (b) comparison to MolGenBench, and (c) justification for
retrospective validation choices. All are answerable. Score of 8.

**Key risks (self-critical assessment):**
1. MolGenBench could extend to include ADMET and synthesizability evaluation between now and
   submission. Their dataset infrastructure (120 targets, 220K actives) is already built. If they
   add the evaluation tiers, Alpha-G loses its primary differentiator. This is my #1 concern.
2. Target curation is harder than estimated. Very few public drug discovery datasets provide
   clean hit -> lead -> candidate progression data. 30-50 targets might be optimistic; 15-20 is
   more realistic.
3. The benchmark's novelty hinges on retrospective validation, which is the component hardest to
   build. If this is dropped for time reasons, the paper becomes less differentiated from MolGenBench.
4. The computational cost is real. At 20,000 GPU-hours minimum, this is competitive with Gamma
   but less impactful per GPU-hour.

**Honest assessment:** As the proposer of Alpha-G, I believe it addresses a real gap. But reviewing
it alongside the other five projects, I concede it is not the top pick. Alpha-M and Gamma have clearer
competitive moats, lower risk of being "scooped" by incremental extensions of existing work, and
higher scientific novelty. Alpha-G would be my recommendation only if Alpha-M and Gamma are both
passed over.

---

### 5. Alpha-L: LiveBioBench -- Cross-Modal Temporally-Gated FM Benchmark

**Round 2 score: 8.2 | genchem score: 7.8**

#### What this project does

Alpha-L proposes a benchmark for biological foundation models that is (a) cross-modal (proteins,
DNA, molecules, single-cell), (b) temporally gated to prevent data contamination, and (c) equipped
with uncertainty quantification metrics. The key finding motivating it: GPT-5 drops 28.3 percentage
points in accuracy on uncontaminated biological data relative to contaminated data.

#### Novel verification

My research confirms the gap. LiveProteinBench (Rongdingyi et al., December 2025, arXiv:2512.22257)
is the closest precedent -- proteins only, continuously updated from UniProt records validated after
January 1, 2025. BioMol-LLM-Bench (April 2026, arXiv:2604.03361) covers 26 tasks across 4 difficulty
levels and 13 models but is static (no temporal gating) and focused on LLM text understanding, not
specialist biological FMs. No cross-modal live benchmark exists.

The 28% contamination inflation finding is compelling but needs verification: which GPT version was
tested, on which tasks, and against which uncontaminated baseline? The aiml specialist report claims
this without specifying the source paper. This is a weakness in the Round 2 case for Alpha-L.

#### Scoring rationale

**Novelty: 8/10.** The gap is confirmed -- no cross-modal temporally-gated benchmark exists. The
temporal gating approach is novel and methodologically sound. LiveProteinBench demonstrates the
technical feasibility. The key novelty claim -- 28% performance inflation from contamination -- is
compelling if verified with a specific citation. Score of 8 rather than 9 because LiveProteinBench
already occupies one modality (protein) and the technical approach is extension rather than invention.

**Scientific impact: 7/10.** This is where I give a lower score than Round 2. The impact of a
benchmark paper depends on whether the community adopts it. There are already multiple competing
benchmark frameworks for biological FMs (PFMBench, BioMol-LLM-Bench, ProteinBench, GUE, BioLLM),
and the field is somewhat saturated with evaluation frameworks. The cross-modal and temporal gating
elements are differentiating, but if major FM developers (Meta, DeepMind, EvolutionaryScale,
CZI) do not adopt this benchmark, impact will be limited. Score of 7 because the causal chain from
benchmark release to changed research practice is longer than for projects that test specific
scientific hypotheses.

**Computational feasibility: 9/10.** 1,550-16,000 GPU-hours per year (depending on scope) is
very manageable. The infrastructure challenge is pipeline automation for continuous updates --
this requires engineering discipline more than compute. Data sources (UniProt, PDB, ChEMBL,
ClinVar, CELLxGENE) all have temporal metadata. Score of 9 because the technical implementation
is straightforward.

**Timeline feasibility: 8/10.** An initial version (v1.0 covering 3-4 modalities with 12-20
tasks) can be built and evaluated within summer 2026. The challenge is maintaining the pipeline
long-term -- a benchmark that stops updating after initial publication has diminishing value. The
team needs to commit to multi-year maintenance, which is a significant commitment for a small team.
Score of 8.

**Publication potential: 7/10.** Nature Methods is the most natural venue; Nature Computational
Science is possible but would require a more novel result than a benchmark alone. The finding that
FMs are 28% overoptimistic due to contamination, if rigorously demonstrated across multiple models
and modalities, is publishable in a top venue. If UQ methods are shown to help calibrate predictions,
that strengthens the case. However, benchmark papers cluster at Nature Methods and Genome Biology
rather than Nature Computational Science. Score of 7.

**Key risks:**
1. The 28% contamination claim needs rigorous verification and sourcing -- if this is the paper's
   headline finding, it must be carefully documented.
2. Maintenance burden: a "live" benchmark that goes stale is worse than a static one.
3. Competitive space: BioMol-LLM-Bench (April 2026) and LiveProteinBench (December 2025) are
   already in the space. Cross-modality is differentiating but must be shown, not just claimed.
4. The UQ component (uncertainty quantification for biological FMs) is underspecified in the
   Round 2 report -- how exactly would UQ be evaluated? Calibration curves? Coverage probabilities?
   Selective prediction? The methodology needs to be nailed down.

---

### 6. Beta: ContextVEP -- Context-Dependent Variant Effect Prediction

**Round 2 score: 8.2 (combined reggeno 7.8 + transmed 7.8) | genchem score: 7.8**

#### What this project does

Beta (ContextVEP) proposes an integrated framework for variant effect prediction that accounts for
tissue context, disease context, mechanism-of-action (GOF/LOF), and genetic background -- targeting
both coding VUS (from the transmed perspective) and non-coding regulatory variants (from the reggeno
perspective). The gap is that existing VEPs (AlphaMissense, popEVE, DYNA, DIVA) each address one
dimension of context but no unified framework addresses all simultaneously.

#### Novel verification

AlphaMissense (Cheng et al., Science 2023): 92% sensitivity, 78% specificity for missense
pathogenicity -- but tissue-agnostic. The February 2026 Genome Biology paper confirms VEP performance
varies significantly by protein and context, with AlphaMissense showing 83% false positive rate in
some gene contexts. popEVE (Nature Genetics, December 2025) adds population-level severity spectrum
but is tissue-agnostic. DYNA (Nature Machine Intelligence 2025) adds disease specificity but is
limited to cardiac/regulatory contexts. IMPPROVE (Nature Communications 2025) shows tissue models
improve over CADD for 90% of phenotypes but uses Random Forest only. The gap is confirmed: no
unified coding + non-coding + tissue + disease + mechanism VEP framework exists.

AlphaGenome (DeepMind, Nature, January 2026) is the critical new context: it achieves AUROC 0.80
for eQTL sign prediction and improves non-coding VEP substantially, but it is for regulatory
variants only and does not handle coding missense variants. It is complementary to, not competitive
with, ContextVEP.

EVEE (bioRxiv April 2026, using Evo 2 embeddings) achieves 0.997 AUROC on 839K ClinVar variants --
impressive, but still tissue-agnostic.

#### Scoring rationale

**Novelty: 7/10.** The gap is real but crowded by partial solutions. DYNA, DIVA, popEVE, IMPPROVE,
and AlphaGenome each chip away at different dimensions. The unified framework claim is valid but will
be challenged by reviewers who will ask "why not just ensemble these existing tools?" The novelty
argument requires a strong answer to this -- why is a unified model better than a pipeline of
specialized models? This is a methodologically important question, and the answer requires careful
framing. Score of 7 because the partial solutions make the "still fully open" claim weaker than in
Round 1.

**Scientific impact: 7/10.** Clinical impact is clear: 1M+ VUS in ClinVar, most unresolvable by
current tools. Context-dependence matters because some variants are pathogenic in one tissue but not
others (incomplete penetrance, tissue-specific expression). This is a genuine clinical need. However,
the path from a computational VEP framework to clinical reclassification of VUS is long and requires
wet-lab functional data for validation -- something this project cannot provide. Score of 7 because
the impact is clear but the translation pathway is indirect.

**Computational feasibility: 9/10.** 500-1,000 GPU-hours is the lowest compute footprint in this
cohort. ClinVar (3M+ variants), GTEx v8, gnomAD v4 (730K exomes), HPA v25 are all public.
AlphaMissense outputs and AlphaGenome predictions can be used as features. Score of 9.

**Timeline feasibility: 9/10.** Given the modest compute requirements and clear data availability,
summer 2026 is very achievable. The main technical challenge is the integration architecture --
how to jointly model coding and non-coding variants in a unified framework. But this is a design
choice made early in the project, not a compute bottleneck. Score of 9.

**Publication potential: 7/10.** Nature Genetics or Genome Biology are appropriate venues. Nature
Computational Science is possible but requires a strong methodological novelty claim. Reviewers
will demand (a) comparison to each individual existing tool, (b) wet-lab validation of novel
predictions (which we cannot provide), and (c) evidence that the unified model outperforms the
best ensemble of existing tools. The lack of wet-lab validation is the hardest constraint. Score
of 7 because the clinical relevance is compelling but methodological novelty is harder to establish
given recent partial solutions.

**Key risks:**
1. AlphaGenome (January 2026) partially narrows the gap faster than anticipated. DeepMind is an
   active competitor; they could release a coding-variant extension of AlphaGenome.
2. Without wet-lab validation, the paper will rely entirely on computational benchmarks (ClinVar
   labels, DMS assay data). Reviewers at top venues often push for prospective experimental validation.
3. Integration of coding and non-coding variants in a single framework requires careful architecture
   choices. This is the hardest design problem in the project.
4. The combined Beta framing (reggeno + transmed) is coherent but requires coordination between
   two different specialist perspectives that may pull in different directions.

---

## Comparative Analysis

### Why Alpha-M and Gamma score equally and top the list

Both Alpha-M and Gamma share three properties that distinguish them from the other four projects:

1. **Unique competitive position:** No published or announced preprint occupies the same space.
   Alpha-M is the first systematic MLFF-vs-experiment benchmark for proteins. Gamma is the first
   ensemble-to-function mapping using BioEmu + ProteinGym. Both have months to a year+ before
   anyone closes the gap. Alpha-G faces MolGenBench as an active incremental competitor. Beta faces
   multiple specialized tools. Delta faces PerturBench and scPerturBench. Alpha-L faces LiveProteinBench
   and the rapidly expanding FM evaluation literature.

2. **Scientific stakes are highest:** Alpha-M's "reality check" on MLFFs directly challenges
   assumptions underlying billions of dollars of ML-guided drug discovery investment. Gamma's
   dynamics-to-function bridge addresses the most fundamental post-AlphaFold question. Both would
   shift community priors significantly if the results are what the proposals anticipate.

3. **Nature Computational Science fit is clearest:** Both have a clear hypothesis (MLFFs fail
   experimental NMR/SAXS benchmarks; ensemble features improve DMS fitness prediction), falsifiable
   predictions, and a strong computational methodology narrative. Nature Comp Sci papers need
   a testable claim and the compute infrastructure to test it rigorously -- both projects have this.

### Why I rank my own project (Alpha-G) fourth

Alpha-G is a real and needed contribution. But I must be honest: MolGenBench (November 2025)
has built substantial infrastructure (120 targets, 220K actives) that partially overlaps. If they
extend to include ADMET and synthesizability evaluation, Alpha-G's differentiation depends entirely
on the retrospective validation component -- which is the hardest to build. A competitor moving
faster on simpler components could produce a competing paper before Alpha-G is ready.

Additionally, the compute requirement (20,000-85,000 GPU-hours) is comparable to Alpha-M but with
lower expected novelty per GPU-hour, because benchmark construction requires more engineering than
discovery. I rank Gamma higher than Alpha-G because Gamma's scientific question (do dynamics improve
function prediction?) is sharper than Alpha-G's benchmark contribution (how bad is pipeline attrition?).

### Why Delta (PerturbMark) ranks third despite the highest R2 score

Delta has the highest Round 2 score (8.6) and is the most computationally tractable project in
this cohort. However, I rank it third rather than first or second because:

1. The benchmark space is already crowded. PerturBench, scPerturBench, and the Virtual Cell
   Challenge 2025 are all recent. The differentiation argument ("cross-context with Tahoe-100M")
   is strong but must be made aggressively against reviewer skepticism.
2. Benchmark papers have lower ceiling publication potential than novel framework papers. Nature
   Methods is very achievable but Nature Computational Science is harder without a method contribution.
3. The scientific question ("does DL outperform linear?") may be resolved by the field itself
   as more methods are published, reducing the urgency of the benchmark.

Delta is the safest project in the cohort -- most likely to succeed within the timeline with
lowest compute risk. If risk management is paramount, Delta might be a better choice than the
top two. But for maximum impact, Alpha-M or Gamma is preferable.

---

## Best Project Combination

**Recommended combination: Alpha-M + Gamma (Biophysical Rigor Stack)**

These two projects are methodologically complementary in a way no other pair achieves:

Alpha-M validates MLFF quality against experimental observables (NMR, SAXS). It answers:
"Can we trust MLFF-generated protein ensembles?"

Gamma uses MLFF-quality ensembles (or BioEmu as a faster proxy) to predict biological function
from conformational distributions. It answers: "If we have good ensembles, can we predict function?"

A combined project could be structured as:
1. Use Alpha-M's validation data (experimental NMR/SAXS on a subset of proteins) to identify which
   ensemble generation approaches (specific MLFFs vs. BioEmu) best reproduce experimental dynamics.
2. Use Gamma's ProteinGym DMS data to show that ensemble quality correlates with downstream
   function prediction accuracy.
3. The combined message: "MLFF/generative ensemble quality matters -- better ensembles yield better
   functional predictions, and here is how to measure ensemble quality against experiment."

This framing would be publishable as a single Nature Computational Science paper with two interlinked
contributions: (1) benchmarking ensemble quality vs. experiment (Alpha-M component) and (2) showing
that ensemble quality predicts functional readout accuracy (Gamma component). The paper would be
longer and more compute-intensive (~190K GPU-hours combined) but would answer a more complete
scientific question than either project alone.

**Alternative combination: Delta + Beta (Regulatory Resolution Stack)**

If the team prefers lower compute risk, Delta (PerturbMark) + Beta (ContextVEP) form a coherent
clinical genomics package:
- Delta resolves the perturbation prediction debate, establishing what computational methods can
  reliably predict about cellular responses to genetic or chemical perturbation.
- Beta uses that knowledge to build context-aware VEP, applying principled perturbation prediction
  methodology to the variant interpretation problem.

This combination targets Nature Methods (Delta) + Nature Genetics (Beta) as separate papers,
rather than a single high-impact submission. Lower risk, lower ceiling.

---

## Final Recommendations for the Orchestrator

1. **Pursue Alpha-M + Gamma as the primary combined project.** The scientific question is clearest,
   the competitive moats are strongest, and the Nature Computational Science fit is most direct.

2. **Delta as a fast-track secondary.** Given its very low compute requirements and clear timeline
   feasibility, Delta (PerturbMark) can be executed in parallel with minimal additional resource
   demand. If Alpha-M or Gamma stalls (force field instability, competition appears), Delta provides
   a fallback with high probability of publication in Nature Methods.

3. **Alpha-G should be deprioritized relative to my Round 2 assessment.** The MolGenBench
   competitive risk is higher than I estimated, and the target curation work is more labor-intensive
   than initially projected. If the team has bandwidth after Alpha-M + Gamma, Alpha-G is a worthwhile
   secondary project. But it should not be the primary if Alpha-M and Gamma are both advancing.

4. **Alpha-L and Beta are solid projects but face more crowded competitive landscapes.** Both
   should be considered only if the top three fail to advance.

---

## References

Ahlmann-Eltze C, Huber W, Anders S. "Deep-learning-based gene perturbation effect prediction does
not yet outperform simple linear baselines." Nature Methods (2025). PubMed: 40759747.

Aryal R, et al. "Assessing the Performance of BioEmu in Understanding Protein Dynamics."
Int. J. Mol. Sci. 2025, 27(6), 2896.

Best RB, et al. "Optimization of the Additive CHARMM All-Atom Protein Force Field Targeting
Improved Sampling of the Backbone phi, psi and Side-Chain chi1 and chi2 Dihedral Angles."
J. Chem. Theory Comput. 2012, 8, 3257-3273.

Buttenschoen M, Morris GM, Deane CM. "PoseBusters: AI-based docking methods fail to generate
physically valid poses or generalise to novel sequences." Chemical Science (2024).

Cheng J, et al. "Accurate proteome-wide missense variant effect prediction with AlphaMissense."
Science 381, eadg7492 (2023).

Frank R, et al. "Molecular Simulations with a Pretrained Neural Network and Universal Pairwise Force
Fields." Journal of the American Chemical Society (2026).

Guo Z, Schwaller P. "TANGO: direct optimization of constrained synthesizability for generative
molecular design." Nature Computational Science (2026).

Huang J, et al. "CHARMM36m: an improved force field for folded and intrinsically disordered proteins."
Nature Methods 14, 71-73 (2017).

Kovacs DP, et al. "MACE-OFF: Short-Range Transferable Machine Learning Force Fields for Organic
Molecules." Journal of the American Chemical Society (2025). PMC12123624.

Lewis JE, et al. "Scalable emulation of protein equilibrium ensembles with generative deep learning."
Science (2025).

Li G, et al. "Biomolecular dynamics with machine-learned quantum-mechanical force fields trained on
diverse chemical fragments." Science Advances (AI2BMD). 2024.

Lindorff-Larsen K, et al. "How fast-folding proteins fold." Science 334, 517-520 (2011).

Mannan RS, et al. "Evaluating Universal Machine Learning Force Fields Against Experimental
Measurements." arXiv:2508.05762 (2025).

Marin M, et al. "Advancing regulatory variant effect prediction with AlphaGenome." Nature (2026).
PMC12851941.

MolGenBench: "Benchmarking Real-World Applicability of Molecular Generative Models from De novo
Design to Lead Optimization." bioRxiv 2025.11.03.686215 (2025).

popEVE consortium. "Proteome-wide model for human disease genetics." Nature Genetics (2025).

Rongdingyi et al. "LiveProteinBench: A Contamination-Free Benchmark for Assessing Models'
Specialized Capabilities in Protein Science." arXiv:2512.22257 (December 2025).

SynGFN: "Learning across chemical space with generative flow-based molecular discovery."
Nature Computational Science 6, 29-38 (2026).

Tahoe-100M: "A Giga-Scale Single-Cell Perturbation Atlas for Context-Dependent Gene Function
and Cellular Modeling." bioRxiv 2025.02.20.639398 (2025). Hugging Face: tahoebio/Tahoe-100M.

UniFFBench / Mannan RS et al.: arXiv:2508.05762 (August 2025). "Evaluating Universal Machine
Learning Force Fields Against Experimental Measurements."

Vinas Torne C, et al. (Systema). "Perturbation prediction models learn systematic variation,
not biology." Nature Biotechnology (August 2025).

Zhang L, et al. "Beyond Affinity: Benchmarking 3D Structure-Based Molecule Generators." (2026).
See also: PMC12344697.

Zhang Y, et al. "DYNA: A disease-specific language model for variant pathogenicity in cardiac
and regulatory genomics." Nature Machine Intelligence (2025).
