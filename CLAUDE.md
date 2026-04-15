# CompBioSummer2026 -- Department-Wide Rules

These rules apply to ALL agents across ALL cohorts in this system. The orchestrator
of each cohort embeds this document (or its key rules) into every subagent prompt.

---

## Cohort Organization

This project uses **sequential cohorts** that build on each other's output. Unlike
independent-cohort systems, each subsequent cohort reads and refines the previous
cohort's work.

```
CompBioSummer2026/
├── CLAUDE.md              # This file (shared rules)
├── context/               # Shared mission context
├── templates/             # Shared document templates
├── Cohort1/               # Gap Scouts -- identify field gaps
│   ├── agents/            # Specialist personas + orchestrator
│   └── output/            # Research, gaps, roundtables
├── CohortArchitect/       # Meta-AI that designs future cohorts
│   ├── CLAUDE.md          # Architect persona
│   └── output/            # Cohort designs + rationale
├── Cohort2/               # Deep Divers -- develop top gaps into proposals
│   ├── agents/            # 6 specialists + orchestrator
│   └── output/            # Research, proposals, critiques, roundtables
├── ReviewCohort/          # Critical evaluation & implementation planning
│   ├── agents/            # 5 specialist reviewers + orchestrator
│   └── output/            # Reviews, verification research, deliberations, final plan
```

**Shared resources** (at project root): `context/mission-briefing.md`, `templates/`.
**Cohort-specific**: Each cohort has its own `agents/` and `output/` directories.

### Sequential Building

Each cohort reads the previous cohort's output. This is by design:
- Cohort 2 agents MUST read Cohort 1's gap reports and synthesis
- Cohort 3 agents MUST read Cohort 2's proposals and critiques
- ReviewCohort agents MUST read all prior cohort output
- The CohortArchitect reads completed cohort output to design the next one

---

## Mission

Discover a novel, ambitious computational biology research project suitable for
publication in **Nature Computational Science** or an equivalent top venue.

The project must be:
- **Purely computational** -- no wet lab access, only open data and open-source tools
- **Compute-enabled** -- leverage significant GPU/CPU resources (HPC cluster with
  H200, RTX 5000 Ada, B200 GPUs, hundreds of CPU nodes)
- **Ambitious** -- a genuinely novel contribution that changes how researchers think
  about a problem, not an incremental improvement
- **Feasible** -- achievable within months, not years, by a small team
- **Impactful** -- addresses a real gap that the field cares about

---

## Non-Negotiable Rules

### 1. No Code Changes

Agents produce **documents only**. Never create or modify source code, tests, configs,
scripts, or any computational artifacts. The purpose of this system is ideation and
research planning, not implementation.

### 2. Read-Only Access to External Resources

Agents may READ public resources for context:
- Published papers, preprints (arXiv, bioRxiv, chemRxiv)
- Public databases (PDB, ChEMBL, UniProt, ENCODE, GTEx, etc.)
- Open-source tool documentation (GitHub repos, readthedocs)
- Conference proceedings and workshop papers

But never download, modify, or create datasets or code.

### 3. Scientific Honesty

- Never overclaim. Distinguish between "published evidence shows X" and "we speculate X."
- Cite specific papers, databases, and data points. Vague claims are not acceptable.
- When proposing an idea, explicitly state what is novel vs. what is established.
- Acknowledge limitations and failure modes of every proposal.
- If a gap has already been filled by a recent paper, say so.

### 4. Deep Research Mandate

Every specialist agent MUST spend extensive time on internet research before writing.
This means:

- Use `WebSearch` to find recent papers, methods, benchmarks, and tools
- Use `WebFetch` to read specific pages from databases, GitHub repos, journals
- Find **specific numbers**: accuracy metrics, dataset sizes, compute costs, timelines
- Cite papers with authors, year, journal, and key findings
- Research notes should contain **real data**, not hand-wavy speculation

The expectation is that each agent's output is 500+ lines with 20+ citations and
specific quantitative findings.

### 5. Document Conventions

All documents follow these conventions:

- **Frontmatter**: Every document starts with YAML frontmatter:
  ```yaml
  ---
  agent: <full agent name>
  round: <round number>
  date: <ISO date>
  type: <gap-report | research-note | proposal | critique | review-assessment | cohort-design>
  ---
  ```
- **Citations**: Use inline citations: `(Author et al., Year)` with a References
  section at the bottom containing full citations
- **Timestamps**: Always UTC ISO format

### 6. Output Organization

All agent output goes to their cohort's `output/` subdirectories:

| Directory | Contents | Who Writes |
|-----------|----------|-----------|
| `output/research/` | Deep literature surveys, database queries, method reviews | All specialists |
| `output/gaps/` | Identified gap reports (Cohort1 only) | Specialists |
| `output/proposals/` | Formal project proposals (Cohort2+) | Specialists |
| `output/critiques/` | Cross-agent reviews (Cohort2+, ReviewCohort) | Specialists |
| `output/roundtables/` | Synthesis documents | Orchestrator only |
| `output/directives/` | Round instructions | Orchestrator only |

### 7. Publication Framing

All proposals must be framed in terms of publication impact:

- What venue is this targeting? (Nature Comp Sci, Nature Methods, Genome Research, etc.)
- What would the paper's main claim be?
- What would reviewers attack?
- What comparison baselines are needed?
- What is the minimal viable experiment?

### 8. Feasibility Constraints

Proposals must account for real constraints:

- **Compute**: HPC cluster with H200, RTX 5000 Ada, B200 GPUs; hundreds of CPU nodes;
  SLURM scheduler. Significant compute budget available.
- **Data**: Public databases only (PDB, ChEMBL, UniProt, ENCODE, GTEx, TCGA,
  ClinVar, gnomAD, etc.). No proprietary or restricted-access data.
- **Software**: Python ecosystem, PyTorch, open-source bioinformatics tools.
  No commercial licenses (Schrodinger, MOE, etc.).
- **Wet lab**: NONE. All validation must be computational or use existing published data.
- **Timeline**: Summer 2026. Prefer approaches achievable in months, not years.
- **Team**: Small computational team. No collaborators assumed.

### 9. What NOT to Propose

- Incremental improvements to existing methods (+2% accuracy on a benchmark)
- Me-too approaches (another protein structure predictor, another molecular generator)
- Purely theoretical work with no computational validation plan
- Projects requiring proprietary data or commercial tools
- Projects requiring wet-lab validation to be convincing
- Projects that have already been done (check preprints carefully!)

### 10. Agent Short Names

**Cohort1 (Gap Scouts):**
- `protdyn`, `genchem`, `multisim`, `reggeno`, `sysnet`, `aiml`, `transmed`
- Orchestrator: `orch`

**Cohort2 (Deep Divers):**
- `mlffeng`, `bioval`, `ensfunc`, `pertbio`, `evalstat`, `scopeadv`
- Orchestrator: `orch`

**ReviewCohort (Critical Evaluation):**
- `dynrev`, `biomlrev`, `statrev`, `implrev`, `stratrev`
- Orchestrator: `orch`

**System-wide:**
- CohortArchitect: `architect`
