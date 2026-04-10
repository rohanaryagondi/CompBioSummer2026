# Mission Briefing: CompBioSummer2026

## The Goal

Find a **novel, ambitious computational biology research project** that:
1. Is publishable in **Nature Computational Science** (or equivalent top venue)
2. Is purely computational (no wet lab access)
3. Leverages significant compute resources (GPUs, CPUs, HPC cluster)
4. Is feasible within the summer 2026 timeline
5. Represents a genuine advance, not an incremental improvement

---

## What We Have

### Compute Resources
- **GPU nodes**: NVIDIA H200 (8 GPUs/node, 80GB each), RTX 5000 Ada (4 GPUs/node,
  32GB each), RTX Pro 6000 Blackwell (8 GPUs/node), B200 (8 GPUs/node)
- **CPU nodes**: Hundreds of nodes with 32-128 cores each
- **Storage**: Large scratch storage for intermediate data
- **Scheduler**: SLURM with priority queue access
- **Scale**: Can run hundreds of concurrent jobs; substantial GPU-hours available

### Software & Data
- Python ecosystem (PyTorch, JAX, TensorFlow)
- Full bioinformatics toolkit (RDKit, Biopython, OpenMM, GROMACS, etc.)
- Public databases: PDB (220K+ structures), ChEMBL (2.4M+ compounds), UniProt
  (250M+ sequences), ENCODE, GTEx, TCGA, ClinVar, gnomAD, STRING, BioGRID
- Pre-trained models: ESM-2, AlphaFold2/3, ProtTrans, OpenFold, RFdiffusion
- Molecular simulation: OpenMM, GROMACS, NAMD, AMBER (open-source tools)

### What We Don't Have
- Wet lab access (all validation must be computational or use published data)
- Proprietary databases or commercial software licenses
- Established collaborator network (but can cite and build on public work)

---

## What Makes a Nature Computational Science Paper

Based on recent publications (2023-2026), Nature Comp Sci papers share these traits:

### Novelty
- Introduces a **new way of thinking** about a problem, not just a better method
- Examples: AlphaFold (structure prediction paradigm shift), CellTypist (cell
  annotation at scale), scGPT (foundation models for single-cell)
- The reviewer should say "I hadn't thought about it this way" not "this is 5% better"

### Scope
- Not a single-dataset result; demonstrates **generalizability**
- Typically validated across multiple systems, organisms, or conditions
- Often introduces a new benchmark, dataset, or evaluation framework
- Computational experiments are large-scale and comprehensive

### Impact
- Addresses a problem the **broad** comp bio community cares about
- Enables new research directions for others (tools, data, insights)
- Has potential downstream implications (even if purely computational)

### Rigor
- Thorough baselines and ablation studies
- Statistical analysis with confidence intervals
- Honest discussion of limitations
- Code and data release

---

## Areas of Interest (Non-Exhaustive)

We are broadly interested in computational biology, with particular interest in
(but not limited to) these areas:

### Structural Biology & Molecular Design
- Post-AlphaFold structural biology: what problems remain unsolved?
- Protein dynamics, conformational ensembles, intrinsically disordered proteins
- Molecular design (drug design, materials, enzymes)
- Protein-protein interactions, molecular recognition
- Cryptic binding sites, allosteric mechanisms

### Genomics & Gene Regulation
- Regulatory genomics: enhancer-promoter prediction, gene regulation models
- Non-coding genome function and variation interpretation
- Single-cell multi-omics integration
- Spatial transcriptomics and tissue architecture

### Systems & Network Biology
- Multi-scale biological modeling (molecular to cellular to tissue)
- Biological network inference and perturbation prediction
- Cell fate and differentiation modeling
- Synthetic biology and pathway design

### AI/ML Methods for Biology
- Foundation models for biological sequences and structures
- Geometric deep learning for molecular systems
- Transfer learning and few-shot learning in biology
- Benchmark and evaluation methodology for bio-ML

### Translational & Clinical
- Precision medicine and patient stratification (computational only)
- Drug repurposing using computational methods
- Biomarker discovery from omics data
- Clinical variant interpretation

---

## The Bar

Ask yourself: **"Would this change how researchers approach this problem?"**

- If the answer is "it would give them a slightly better tool" → too incremental
- If the answer is "it would make them rethink their approach" → promising
- If the answer is "it would open an entirely new line of research" → ideal

We want ideas at the "rethink" or "new line of research" level.

---

## What to Search For

When doing deep research, look for:

1. **Recent reviews** that explicitly list open problems and future directions
2. **Workshop reports** from top conferences (NeurIPS, ICML, ISMB) identifying field gaps
3. **Failed or abandoned approaches** that could be revisited with modern compute/methods
4. **Cross-domain opportunities** where methods from one field could transform another
5. **Data bottlenecks** that have recently been removed (new databases, new data types)
6. **Paradigm tensions** where the field is split and a unifying approach could win

---

## Timeline Context

- **Current date**: April 2026
- **Target completion**: End of summer 2026
- **Publication target**: Nature Computational Science or equivalent
- **Recent milestones in the field** (2024-2026):
  - AlphaFold3 (protein-nucleic acid-ligand complexes, 2024)
  - ESM3 / ESMFold updates (protein language models)
  - Foundation models for single-cell biology (scGPT, Geneformer, scBERT)
  - Molecular generation advances (FLOWR, DynamicBind, DiffDock-L)
  - Long-read sequencing revolution (Oxford Nanopore, PacBio)
  - Spatial omics becoming mainstream (Visium, MERFISH, Slide-seq)
