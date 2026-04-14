---
agent: protdyn
round: 3
date: 2026-04-14
type: ranking
---

# Round 3 Rankings: protdyn

## Preamble

These rankings represent my independent assessment as the Protein Dynamics Expert,
informed by reading all seven Round 2 deep-dive reports and the Round 2 synthesis.
I have tried to be ruthlessly honest about my own project (Gamma) relative to the
others. The ranking criteria are:

- **Novelty (1-10):** How genuinely new is the contribution? Would reviewers say "this
  fills a real gap" or "this is incremental"?
- **Scientific Impact (1-10):** Will it change how researchers work? Does it address a
  central question for the field?
- **Computational Feasibility (1-10):** Can this be completed with available tools,
  data, and the specified HPC, without wet lab?
- **Timeline Feasibility (1-10):** Can a result be published by end of summer 2026?
- **Publication Potential (1-10):** Could this realistically land in Nature Computational
  Science or Nature Methods?

Scores are calibrated against each other -- a 9 means genuinely outstanding on that
criterion, not merely "good."

---

## Project Rankings

---

### 1. Alpha-M: MLFF Biomolecular Crash Test

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | **9** | No systematic benchmark of ML force fields against experimental protein observables exists. The UniFFBench analogy (materials science: "models achieving impressive performance on computational benchmarks often fail when confronted with experimental complexity") almost certainly extends to biomolecules -- but nobody has measured it. The analogy itself is publishable evidence of the gap. Classical force field benchmarks (Lindorff-Larsen et al., 2012; Best et al., 2012; Huang et al., 2017; Tian et al., 2020) represent 30+ years of infrastructure that the MLFF community has entirely bypassed. |
| Scientific Impact | **9** | This benchmark would directly guide the MLFF development community across many groups (Microsoft AI2BMD, DeepMind GEMS, Cambridge MACE-OFF, Meta UMA, Basel SO3LR). It answers a question every computational biophysicist needs answered before trusting MLFF simulations: "Do these produce physically realistic protein dynamics, not just low energy/force RMSE vs DFT?" NMR order parameters (S2), chemical shifts, RDCs, SAXS profiles, and HDX-MS protection factors are the gold standards the field actually uses. |
| Computational Feasibility | **7** | All 6+ MLFFs are open-source. BMRB has ~21,820 NMR entries; SASBDB has 5,272 SAXS datasets; overlap of ~50-100 proteins with paired NMR + SAXS data is well-characterized. OpenMM-ML provides a unified interface (MACE-OFF, ANI-2x, AceFF via the same engine), enabling fair comparison. Key challenge: 180,000-270,000 GPU-hours is a large but not impossible ask on the available HPC with H200 and B200 nodes. The 2-3 month simulation execution window is the binding constraint. Score docked two points for compute risk and the practical difficulty of running 6 different MLFFs through compatible pipelines. |
| Timeline Feasibility | **6** | This is the hardest project to complete in summer 2026. 15 proteins × 3-6 MLFFs × 50 ns trajectories = 180K-270K GPU-hours minimum. Even with H200/B200 parallelism, that is 2-3 months of continuous execution before analysis. A minimal viable experiment (5 proteins × 3 MLFFs × 20 ns) might be achievable in 6-8 weeks, but would be less convincing. The analysis pipeline (computing NMR observables from trajectories with SPARTA+, ShiftX2, or MDAnalysis) is non-trivial to set up correctly. Score penalized for tight timeline. |
| Publication Potential | **9** | This is textbook Nature Computational Science material: a systematic, quantitative benchmark revealing a gap between claimed and actual performance of a fast-moving ML technology. Precedent: CASP assessments, Critical Assessment of Protein Intrinsic Disorder (CAID). Reviewers will not be able to argue the paper is not needed. The main reviewers' attack -- "just compare to classical FFs, not experiment" -- has already been preempted by the design. Nature Methods is a natural backup. |

**Recommended venue:** Nature Computational Science (primary); Nature Methods (backup)

**Strengths:**
- Highest Round 2 score (8.7) and the scoring is well-justified
- Empty competitive space: no group has announced this benchmark
- Community-service framing is immediately convincing to reviewers
- Data infrastructure (BMRB, SASBDB) is mature and well-curated
- OpenMM-ML unification of multiple MLFFs makes fair comparison tractable

**Risks:**
- Compute timeline is tight for summer 2026 -- failure to finish simulations would
  be catastrophic
- Running 6 MLFFs through consistent pipelines is technically demanding; silent
  failures (non-equilibrated systems, artifact trajectories) are hard to detect
- Some MLFFs (GEMS, SO3LR) may require forked or custom MD engines, complicating the
  "unified interface" goal
- A MLFF group (Microsoft, DeepMind) could preempt with their own comparison, although
  self-benchmarking is less credible than independent evaluation
- Requires correctly computing NMR back-calculators (SPARTA+, etc.) from MD frames --
  non-trivial calibration required

**Aggregate Score: 40/50 (avg 8.0)**

---

### 2. Delta: PerturbMark

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | **8** | The field genuinely lacks a single, definitive, cross-context benchmark that tests DL vs. linear baselines with proper controls across multiple datasets and cell contexts. Multiple partial attempts exist (scPerturBench with 27 methods on 29 datasets; Systema; Virtual Cell Challenge), but none resolves the controversy because each uses different metrics, datasets, or evaluation protocols. The key novelty is the framework itself: standardized metric suite (addressing the metric debate), mandatory linear baselines, cross-context generalization splits, and a definitive verdict. |
| Scientific Impact | **9** | This is potentially the most field-reshaping project in the list. The perturbation prediction controversy is THE central methodological dispute in computational biology as of 2026 (Nature Methods, Nature Biotechnology, Arc Institute Virtual Cell Challenge). If DL genuinely beats linear baselines under rigorous evaluation, that validates major investments across CZI, Xaira, Genentech, etc. If it does not, the field needs to know immediately. Either answer is high-impact. The Tahoe-100M dataset (CC0 license, 100M cells across 429 compounds in 50 cell lines, 429GB) provides unprecedented scale for cross-context tests that nobody has yet analyzed comprehensively. |
| Computational Feasibility | **10** | This is the most feasible project in the portfolio. All datasets are public (Tahoe-100M CC0, X-Atlas, Replogle, Norman). All models are open-source (GEARS, CPA, scGPT, X-Cell, AlphaCell, SCALE). Compute requirement is 1,000-2,000 GPU-hours -- trivially achievable in days, not months, on the available HPC. No data curation bottleneck. Linear baselines (matrix factorization, mean, additive) run in minutes. The barrier is analytical rigor and clear thinking, not resources. |
| Timeline Feasibility | **10** | With 1-2K GPU-hours, this project can be executed and iterated multiple times within a 4-6 week window. The analysis phase (aggregating and visualizing results across methods and datasets) is the main time investment. A preprint could realistically appear within 2-3 months of starting. This is the clearest summer 2026 deliverable in the portfolio. |
| Publication Potential | **8** | Nature Methods is the natural home for this paper (precedent: Ahlmann-Eltze et al. published there). Nature Computational Science is possible if the benchmark discovers something genuinely surprising (e.g., a previously unrecognized reason DL fails). The risk is that the paper resolves a controversy but does not discover something new -- "DL still does not beat linear baselines" is important but may be perceived as a negative result rather than a discovery. That said, the Virtual Cell Challenge and Nature Methods controversy paper give strong precedent for high-impact benchmark/methods comparison papers. |

**Recommended venue:** Nature Methods (primary); Nature Computational Science if result is surprising

**Strengths:**
- Active controversy guarantees instant field attention upon publication
- Tahoe-100M (100M cells, CC0, 429GB) is entirely new and untapped for this purpose
- Extremely low compute requirement allows rapid iteration and sensitivity analysis
- Nature Methods has strong precedent for exactly this type of paper
- Independent analysis adds credibility that CZI/Arc Institute self-assessments lack
- Definitive framing ("we resolve the debate") is immediately compelling to editors

**Risks:**
- Being scooped: CZI, scPerturb team, and others are likely building similar benchmarks;
  the 6-18 month window estimate may be optimistic
- Result may be "DL still doesn't beat linear, but with caveats" -- nuanced results are
  harder to frame convincingly
- Metric selection is itself a methodological contribution that could be disputed
- A Nature Methods paper does not reach Nature Comp Sci, which may matter for the team's
  goals

**Aggregate Score: 45/50 (avg 9.0)**

---

### 3. Gamma: Dynamics-to-Function

*Note: This is my own project. I have tried to score it objectively.*

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | **9** | As of April 2026, no published or preprint work connects explicit BioEmu-generated conformational ensembles to quantitative functional readouts from DMS data at scale. The partial solutions (SeqDance/ESMDance use implicit dynamics; QDPR requires protein-specific MD; Ozkan DCIasym covers 4 proteins; distogram representations are a proxy) leave the core gap open. The combination of BioEmu + ProteinGym is specifically unexplored -- confirmed by absence of any paper using BioEmu-generated ensembles as features for fitness prediction in 9 months since its public availability. |
| Scientific Impact | **8** | The dynamics-to-function question is central to post-AlphaFold protein science. If ensemble properties can predict functional outcomes better than static structure-based methods, this changes how the field thinks about what conformational heterogeneity means for biology. ProteinGym's 2.7M DMS variants across 217 assays provides the most comprehensive functional ground truth available. The practical downstream impact -- better mutation effect predictors, better protein design -- is large and tangible. Score is 8 rather than 9 because the immediate beneficiaries (protein engineers, drug designers) are somewhat downstream; this is primarily a fundamental science contribution. |
| Computational Feasibility | **8** | BioEmu is MIT-licensed, pip-installable, and H200-compatible (141GB VRAM eliminates memory constraints). ProteinGym v1.3 has 197 protein structures available from PDB. The sampling speed benchmarks (4 min/1000 samples for 100-residue proteins, 40 min for 300-residue proteins on A100) scale well to H200. Estimated 8,200 GPU-hours is comfortable on the available HPC. Key feasibility risks: BioEmu limitations for non-globular proteins and the independent assessment finding that BioEmu "cannot effectively differentiate driver and passenger mutations" -- this is a limitation of the tool we are building on, not necessarily fatal to the framework. |
| Timeline Feasibility | **8** | 8,200 GPU-hours can be completed in 3-4 weeks on 8 H200 GPUs running in parallel. The pipeline (BioEmu sampling → ensemble feature extraction → ML model training → ProteinGym evaluation) is straightforward and well-defined. No curation bottleneck. The 6-18 month competition window is the primary risk, not the execution timeline. A preprint in 2-3 months is realistic. |
| Publication Potential | **8** | Nature Computational Science is the target. The paper would position as: "we build the first general framework connecting conformational ensembles to function, resolving a central post-AlphaFold question." This framing is strong. Reviewers' likely attacks: (1) BioEmu quality is imperfect; (2) Is the framework generalizable beyond ProteinGym proteins? Both are addressable. The paper needs to show that the ensemble-based approach outperforms state-of-the-art static methods (ESM-1v, EVE) on ProteinGym benchmarks -- this is the minimal viable experiment and is achievable. |

**Recommended venue:** Nature Computational Science

**Strengths:**
- Highest scientific narrative quality: "what does a protein's conformational ensemble
  tell us about its function?" is a question every structural biologist cares about
- BioEmu is newly available (Science 2025) and largely unexplored for this application
- ProteinGym provides rigorous, large-scale ground truth
- Feasible compute and clear execution pipeline
- Directly improves mutation effect prediction, which has immediate practical applications

**Risks:**
- 6-18 month competition window: Microsoft (BioEmu group) and Marks Lab (ProteinGym group)
  are the most dangerous potential competitors; if either publishes this combination first,
  the paper loses most of its impact
- BioEmu performs poorly on non-globular proteins and has known limitations for predicting
  mutation-induced conformational shifts (Aryal et al., 2025)
- The ML framework connecting ensemble features to function requires careful design choices
  (what features? what model architecture?) that could underperform expectations
- IDPs, which are the most dynamically complex proteins, are precisely where BioEmu is
  weakest -- limiting the framework's coverage of the most interesting cases

**Aggregate Score: 41/50 (avg 8.2)**

---

### 4. Alpha-L: LiveBioBench

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | **8** | LiveProteinBench (December 2025) demonstrates temporal gating for proteins, but it covers only one modality and focuses on LLMs rather than specialist biological FMs. No benchmark combines temporal gating + cross-modal coverage (protein, DNA/RNA, small molecule, single-cell) + mandatory UQ evaluation for specialist biological FMs. The 28.3 percentage-point GPT-5 accuracy drop on uncontaminated data is a striking, specific finding that anchors the novelty claim. BioMol-LLM-Bench (April 2026) covers 26 tasks but is static and focused on text understanding, not specialist FM performance. |
| Scientific Impact | **8** | Demonstrating systematic contamination-driven performance inflation across biological FM modalities would be a genuinely important methodological contribution. The annually renewable nature of the benchmark (new proteins, new sequences, new cell data each year) gives it lasting infrastructure value. The UQ component adds a second pillar: not just "is the FM accurate?" but "does it know when it is uncertain?" Both are central to whether biological FMs can be trusted for scientific discovery. |
| Computational Feasibility | **9** | All data sources support temporal metadata: UniProt, PDB, ChEMBL, ClinVar, CELLxGENE. All FMs are open-source. Compute ranges from 1,550 GPU-hours (protein-only initial version) to 16,000 GPU-hours (full cross-modal). Infrastructure development (temporal gating pipeline, automated data pulling) is the main bottleneck, not compute. Score is 9 because the main challenge is engineering and data curation, not scientific uncertainty. |
| Timeline Feasibility | **8** | An initial protein-only version could be completed in 4-6 weeks. The full cross-modal version requires the temporal gating infrastructure to be built correctly first, adding another 4-6 weeks. A preprint demonstrating the contamination problem across modalities is achievable in summer 2026. The annually renewable design means the initial publication does not need to be complete -- a proof-of-concept demonstrating the contamination issue and providing the framework is sufficient. |
| Publication Potential | **8** | Nature Computational Science is appropriate: this is a methodology paper that changes how the community evaluates biological FMs. The "GPT-5 drops 28% on uncontaminated data" framing will generate immediate attention. The closest precedent is the NLP LiveBench and HELM papers, which were highly cited and influential. Reviewers' main attack: "is the performance drop really due to contamination, or just different data difficulty?" This requires careful controls (same task types, different temporal splits) to address convincingly. |

**Recommended venue:** Nature Computational Science

**Strengths:**
- Entirely empty competitive space at the intersection of cross-modal + temporal gating
  + UQ + specialist biological FMs (not LLMs)
- 28% performance drop is a specific, dramatic, immediately publishable finding
- Annually renewable: long-term citation impact as the community adopts it as standard
- Relatively low compute requirement compared to Alpha-M
- Addresses a problem that affects every biological FM paper published in the past 2 years

**Risks:**
- Infrastructure development is non-trivial: temporal gating requires careful handling
  of data release dates, which are not always precisely recorded in databases
- Broad scope (protein + DNA + molecule + single-cell) risks being unfocused without
  strong editorial framing
- Maintaining the benchmark long-term requires ongoing effort beyond summer 2026
- The UQ component requires designing tasks with known uncertainty -- not straightforward
  for all biological modalities
- A protein-only version might be perceived as insufficient; a full cross-modal version
  might be too ambitious for one summer

**Aggregate Score: 41/50 (avg 8.2)**

---

### 5. Alpha-G: Molecular Design Benchmark

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | **7** | The end-to-end pipeline framing (target → generation → docking → ADMET → synthesizability → retrospective validation) is genuinely new. Existing benchmarks (GuacaMol, MOSES, PMO, MolGenBench, "Beyond Affinity") each address fragments. The "pipeline attrition rate" concept -- measuring how many generated molecules survive each sequential filter -- is a novel metric. However, this gap is well-recognized (three independent efforts in 6 months all independently identified it from different angles), which is a double-edged signal: it means the community agrees the gap exists, but also means multiple groups are converging on filling it. |
| Scientific Impact | **8** | Drug discovery is the highest-impact application domain in computational biology. Showing that state-of-the-art molecular generators produce candidates that fail at ADMET, synthesizability, or retrospective clinical validation -- even when they score well on existing benchmarks -- would be a genuine contribution with immediate practical consequences. The "pipeline attrition" framing specifically addresses why molecular design has not produced more clinical candidates despite years of ML investment. |
| Computational Feasibility | **6** | The technical tools all exist (ChEMBL 36, BindingDB, standard docking and ADMET software). But the data curation burden is high: selecting 30-50 targets with full progression data (hit → lead → clinical candidate) requires substantial manual work, and the quality of retrospective validation depends critically on that curation. Running 10-15 generative models through the full pipeline (generation → docking → ADMET → synthesis scoring) requires 20K-85K GPU-hours for a comprehensive analysis. The curation bottleneck, not the compute, is the limiting factor. Score 6 because silent errors in pipeline integration are common and hard to detect. |
| Timeline Feasibility | **6** | The 20K GPU-hours for an initial publication is achievable, but the curation of 30-50 well-characterized targets is likely a 2-3 month effort even with ChEMBL and BindingDB as sources. The pipeline integration (ensuring all 10-15 generative models produce output compatible with the docking and ADMET tools) adds another month. A complete paper by end of summer 2026 is feasible but tight. A reduced-scope version (10 targets, 5 generators, 3 pipeline stages) is more realistic. |
| Publication Potential | **7** | Nature Computational Science is the right venue for impact, but this benchmark competes with GuacaMol, PMO, and MolGenBench as predecessors. Reviewers will ask: "why is this substantially better than MolGenBench or Beyond Affinity?" The answer -- retrospective clinical validation and ADMET integration -- is good, but requires the curated target set to be compelling. Journal of Chemical Information and Modeling or Nature Methods are strong backup options. The scoop risk from MolGenBench follow-ups is non-trivial. |

**Recommended venue:** Nature Computational Science (stretch); Nature Methods (realistic)

**Strengths:**
- Drug discovery stakes guarantee broad interest
- Pipeline attrition framing is genuinely novel and intuitive
- The "affinity-validity trade-off" (Zhang et al., 2026) is already documented; this
  project extends to the full multi-stage trade-off space
- ChEMBL 36 (2.8M compounds) and BindingDB (3.15M bioactivity records) provide
  sufficient raw material
- Industry collaboration is natural and would strengthen the paper significantly

**Risks:**
- High curation burden: selecting and validating 30-50 targets with real progression
  data requires deep domain expertise and may take longer than summer 2026
- MolGenBench (November 2025) and "Beyond Affinity" (January 2026) reduce the novelty
  space; reviewers will need convincing differentiation
- Pipeline integration failures (docking scoring inaccuracies, ADMET model disagreements)
  could produce results that are hard to interpret
- Generative model comparison is complicated by different input modalities (1D/2D/3D);
  method-agnostic evaluation is harder than it sounds

**Aggregate Score: 34/50 (avg 6.8)**

---

### 6. Beta: ContextVEP

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Novelty | **6** | The gap has significantly narrowed since Round 1. AlphaGenome (Nature, January 2026) achieves eQTL AUROC 0.80. EMO integrates DNA sequence with chromatin accessibility at single-cell resolution. DYNA and DIVA introduce disease context. IMPPROVE integrates GTEx single-cell data with CADD scores across 1,866 HPO phenotypes. popEVE adds population-level severity scoring. DYNA/DIVA/IMPPROVE/popEVE each address fragments; no single tool integrates tissue, disease, mechanism (GOF/LOF), and genetic background simultaneously for coding VUS. But the novelty bar is harder to clear after these publications. Score 6 because reviewers will ask what is truly new beyond combining known approaches. |
| Scientific Impact | **7** | The 1M+ VUS in ClinVar (with 61% classified as "uncertain significance") represents a real clinical burden. AlphaMissense's 83% false-positive rate in some gene families is a specific, documented limitation. A context-dependent VEP that reduces FPR by integrating tissue expression (GTEx v8, HPA v25), disease context, and GOF/LOF mechanism would have immediate clinical utility. However, the clinical impact is clearer than the scientific impact -- this is more translational than fundamental. |
| Computational Feasibility | **9** | All data is public: GTEx v8, HPA v25, ClinVar 3M+ variants, gnomAD v4 (730K exomes), ClinGen, OMIM. AlphaMissense scores available for 216M+ missense variants. Compute requirement is 500-1,000 GPU-hours -- the most compute-efficient project in the portfolio. The integration framework (tissue expression + variant scores + disease context) is well-understood methodologically. No wet-lab components. |
| Timeline Feasibility | **9** | With 500-1,000 GPU-hours and well-defined data sources, this is achievable in 4-6 weeks of computation. The main time investment is designing the integration framework and validating against known pathogenic and benign variants. A preprint is realistically achievable in 6-8 weeks from start. |
| Publication Potential | **6** | The clinical relevance is clear, but the publication venue is uncertain. Nature Genetics is the natural target for VEP papers (AlphaMissense appeared there). Nature Computational Science is a stretch given that the primary contribution is integration rather than methodological innovation. The risk is that reviewers perceive this as "better AlphaMissense with more features" rather than a fundamental advance. The gap's partial narrowing since Round 1 (reggeno: 7.8, transmed: 7.8) already reflects this concern. The combined Beta framing (coding + non-coding in one framework) strengthens the novelty claim. |

**Recommended venue:** Nature Genetics (primary); Nature Computational Science (stretch)

**Strengths:**
- Highest clinical immediacy: 1M+ VUS and demonstrated AlphaMissense limitations create
  clear unmet need
- Very low compute requirement -- extremely feasible execution
- All data public and well-curated (GTEx, ClinVar, gnomAD)
- Combined coding + non-coding integration would be genuinely comprehensive
- Clinical genetics community is large and will cite a useful tool

**Risks:**
- Gap has narrowed significantly since Round 1 (DYNA, DIVA, IMPPROVE, popEVE, AlphaGenome
  all published in 2025-2026) -- differentiation argument requires careful framing
- AlphaMissense + tissue context is an obvious next step; multiple groups likely pursuing
  this independently
- The integration framework (how to combine tissue expression, disease context, mechanism)
  requires methodological innovation that is not yet specified
- "Combine existing tools" projects can struggle at Nature Comp Sci without a clear
  theoretical advance
- Without wet-lab validation, the paper depends entirely on held-out ClinVar variants --
  reviewers will question whether this is truly a new prediction or curve-fitting on
  known variants

**Aggregate Score: 37/50 (avg 7.4)**

---

## Summary Table

| Project | Nov | Imp | Feas | Time | Pub | Avg | Venue |
|---------|-----|-----|------|------|-----|-----|-------|
| Alpha-M: MLFF Crash Test | 9 | 9 | 7 | 6 | 9 | **8.0** | Nat Comp Sci |
| Delta: PerturbMark | 8 | 9 | 10 | 10 | 8 | **9.0** | Nat Methods |
| Gamma: Dynamics-to-Function | 9 | 8 | 8 | 8 | 8 | **8.2** | Nat Comp Sci |
| Alpha-L: LiveBioBench | 8 | 8 | 9 | 8 | 8 | **8.2** | Nat Comp Sci |
| Alpha-G: Mol Design Bench | 7 | 8 | 6 | 6 | 7 | **6.8** | Nat Methods |
| Beta: ContextVEP | 6 | 7 | 9 | 9 | 6 | **7.4** | Nat Genetics |

*Rankings sorted by the aggregate score reported in the Round 2 synthesis, not by
my scores alone. The summary table reflects my independent calibration.*

---

## Top Pick

**Delta: PerturbMark (9.0 avg)**

I am recommending Delta as the top project despite it being outside my primary domain
(protein dynamics). This is a deliberate choice, not a convenient one.

The reasons:

1. **The field urgency is real and immediate.** The perturbation prediction controversy
   is the central methodological dispute in computational biology right now, playing out
   in Nature Methods, Nature Biotechnology, and the Arc Institute Virtual Cell Challenge
   simultaneously. A definitive independent benchmark will be read by everyone in single-
   cell genomics, computational biology, and cell biology.

2. **The feasibility floor is uniquely low.** 1,000-2,000 GPU-hours means this project
   can be executed, iterated, and polished in weeks rather than months. Low compute
   also means rapid sensitivity analysis -- the paper can test many metric choices and
   baseline definitions without waiting months for results.

3. **Tahoe-100M is entirely untapped.** This dataset (CC0 license, 100M cells, 429
   compounds, 50 cell lines) was released without comprehensive analysis. Being the first
   paper to provide a rigorous cross-context perturbation benchmark on Tahoe-100M gives
   a strong novelty claim independent of the method comparison findings.

4. **Both possible outcomes are high-impact.** If DL beats linear baselines under proper
   evaluation: validates major community investment and definitively ends one side of the
   debate. If DL still does not beat linear baselines: nature methods article with
   immediate practical consequences for how the field allocates research resources.

5. **The paper writes itself.** The controversy provides the introduction, the datasets
   provide the methods, and the verdict provides the conclusion. Clear narrative is a
   real advantage for getting through review quickly.

My hesitation: Nature Methods rather than Nature Computational Science may be the
realistic landing zone, unless the findings are genuinely surprising. The team should
evaluate whether Nature Methods is the desired outcome.

---

## Best Combination

**Alpha-M (MLFF Crash Test) + Gamma (Dynamics-to-Function)**

These two projects are deeply intellectually coherent and create a stronger combined
submission than either alone.

**The shared thesis:** Computational representations of protein dynamics -- whether from
ML force fields or from generative ensemble models -- are advancing faster than our
ability to validate them against experiment or connect them to function. Both projects
address this gap from complementary angles.

**Alpha-M** asks: "Are ML force field trajectories physically realistic?" It answers
with experimental NMR/SAXS observables as the ground truth.

**Gamma** asks: "Can predicted conformational ensembles predict biological function?"
It answers with ProteinGym DMS measurements as the ground truth.

**Combined contribution:** Together, they form a two-part framework:
1. First, establish which ensemble generation methods produce physically realistic
   dynamics (Alpha-M validation layer)
2. Then, use those validated ensembles to predict functional consequences (Gamma
   prediction layer)

This combination answers a question neither project can answer alone: "Do the ensemble
generation methods that produce realistic physical dynamics also produce better functional
predictions?" The validated MLFFs from Alpha-M become direct inputs to the Gamma
ensemble-feature pipeline, creating a coherent experimental design rather than two
independent papers.

**Why not Delta + Gamma?** Delta addresses single-cell perturbation prediction, which
is methodologically distant from protein dynamics. Combining them would require two
separate introductions and two separate methodological sections with no shared
infrastructure. The combined story would feel forced.

**Why not Alpha-M + Delta?** No direct intellectual connection. These would remain
two independent benchmark papers published together by coincidence of timing.

**Why Alpha-M + Gamma is better than either alone:**
- Validates the tool before using it (BioEmu ensembles → MLFF validation → ensemble-
  to-function mapping uses validated ensembles)
- Natural Computational Science narrative: "We close the gap between ensemble prediction
  and experimental validation, then show what validated ensembles can tell us about
  function"
- Shared protein test set: proteins with NMR + SAXS data (Alpha-M validation set) can
  be the same proteins used for DMS function prediction (Gamma set), provided ProteinGym
  coverage overlaps -- this creates a dataset where we know both the physical accuracy of
  the ensemble AND its functional accuracy
- Combined compute (8,200 + ~100K GPU-hours for a focused Alpha-M component) is still
  within the available HPC budget

**Risk of combination:** The Alpha-M timeline (180K-270K GPU-hours over 2-3 months) is
the binding constraint. A reduced Alpha-M (5-7 proteins, 3 MLFFs) combined with Gamma
is more realistic for summer 2026 than the full Alpha-M specification.

---

## Reasoning and Cross-Domain Observations

### Why I Changed My Initial Ranking

Entering Round 3, my prior was that Gamma (my own project) would rank first. Having
read all seven deep-dive reports carefully, I revise that. Delta's combination of
maximal feasibility, active controversy, and immediate field impact makes it the
safest and highest-expected-value project for summer 2026. Gamma remains scientifically
more interesting to me personally -- the dynamics-to-function question is deeper -- but
"scientifically interesting to me" is not the right criterion for this ranking.

### The Benchmark Cluster

Four of the six projects are fundamentally benchmarking papers (Alpha-M, Delta, Alpha-L,
Alpha-G). This is notable: the field's biggest gaps in 2026 are in *evaluation*, not in
generating new methods. We have proliferated models faster than our ability to evaluate
them. This convergence on benchmarking as the core gap is itself an interesting finding
for the orchestrator's synthesis.

### Dynamics-to-Function Remains the Most Scientifically Novel

Despite ranking Delta first on aggregate, Gamma remains the most scientifically novel
contribution in the strict sense: it proposes a genuinely new type of analysis
(ensemble properties → quantitative function), not a better version of an existing
analysis type (benchmark). If the team's goal is to make a lasting contribution to
protein science rather than to resolve an existing controversy, Gamma is the better
choice -- but with the awareness that the competition window is narrower.

### The Alpha-M Timing Problem Is Real

Alpha-M is the highest-scoring individual project (8.7 in Round 2, 8.0 in my avg)
but I rank it below Delta because the timeline risk is substantial. 180K-270K GPU-hours
needs to start immediately if it is to finish by summer 2026. Any pipeline failures,
MLFF version incompatibilities, or trajectory instabilities (TEA Challenge 2023 found
that some MLFFs cannot sustain stable 1 ns dynamics for peptides, let alone 50 ns for
folded proteins) would cascade into missed deadlines. The higher scientific ceiling
comes with higher execution risk.

### Beta: ContextVEP Should Not Be Top Priority

I score Beta lowest (7.4 avg) because the gap has genuinely narrowed since Round 1.
AlphaGenome, EMO, DYNA, DIVA, IMPPROVE, and popEVE together represent substantial
recent progress. The combined coding + non-coding framing is stronger than either alone,
but this project requires the most careful novelty positioning. It should not be the
primary project; if resources allow, it could be a secondary contribution by the same
team.

---

## References

1. Lewis, A.M. et al. (2025). "BioEmu: Democratizing Protein Conformational Ensemble
   Prediction at Scale." *Science*, 369, 270-278.
2. Aryal, S. et al. (2025). "BioEmu Fails to Predict Mutation-Induced Conformational
   Distribution Shifts." *Int. J. Mol. Sci.*, 27, 2896.
3. Ahlmann-Eltze, C., Huber, W., & Anders, S. (2025). "Deep-learning-based gene
   perturbation effect prediction does not yet outperform simple linear baselines."
   *Nature Methods*, 2025.
4. Vinas Torne, R. et al. (2025). "Systema: Performance on perturbation datasets
   correlates with systematic variation, not biology." *Nature Biotechnology*, Aug 2025.
5. Wong, E., Hill, A., & Moccia, R. (2025). "CRISPR-informed mean baseline surpasses
   deep learning models." *Bioinformatics*, Jun 2025.
6. Mannan, S. et al. (2025). "UniFFBench: Universal Force Field Benchmark Reveals
   Reality Gap." *arXiv*, 2508.05762.
7. Li, Y. et al. (2024). "AI2BMD: Accurate Protein Simulation with AI." *Nature*, 2024.
8. Kovacs, D. et al. (2025). "MACE-OFF23: Transferable Machine Learning Force Fields
   for Organic Molecules." *JACS*, 2025.
9. Frank, M. et al. (2026). "SO3LR: Scalable Machine Learning Force Field for
   Biological Systems." *JACS*, 2026.
10. Marin, F. et al. (2026). "AlphaGenome: Unified Sequence Model for Regulatory
    Genomics." *Nature*, Jan 2026.
11. Rongdingyi, Z. et al. (2025). "LiveProteinBench: Temporally Gated Protein Benchmark."
    *arXiv*, 2512.22257.
12. Unke, O. et al. (2024). "GEMS: General Machine Learning Potential for Biomolecular
    Simulations." *Science Advances*, 2024.
13. Lindorff-Larsen, K. et al. (2012). "Systematic Validation of Protein Force Fields
    Against Experimental Data." *PLoS ONE*, 7(2).
14. Best, R.B. et al. (2012). "Optimization of the Additive CHARMM All-Atom Protein
    Force Field." *J. Chem. Theory Comput.*, 8(9), 3257-3273.
15. Hou, J. & Shen, Y. (2026). "ESMDance: Protein Language Models with Dynamic
    Biophysical Properties Improve Mutation Effect Prediction." *PNAS*, Jan 2026.
16. Burgin, O. et al. (2025). "QDPR: Quantified Dynamics-Property Relationships."
    *JCIM*, 65, 11979-11987.
17. Ozkan, O. et al. (2025). "Dynamics-Based Graph Neural Networks for Epistasis
    Prediction." *PNAS*, 122, e2502444122.
18. Dibaeinia, P. et al. (2026). "Virtual Cells Need Context, Not Just Scale."
    *bioRxiv*, Feb 2026.
19. Arc Institute Virtual Cell Challenge (2025). *Final Report*, Dec 2025.
20. Zhang, Y. et al. (2026). "Beyond Affinity: Benchmarking Molecular Design Across
    1D, 2D, and 3D Paradigms." *bioRxiv*, Jan 2026.
