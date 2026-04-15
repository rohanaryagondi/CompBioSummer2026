---
task_id: "task-004"
title: "BioEmu v1.3.1 Disulfide Bond Test on BPTI + HEWL"
subphase: "0.1"
track: alpha-m
wave: 2
agent: "bioemu-test"
effort: "1-2 days"
status: planned
created: 2026-04-15
---

# Task 004: BioEmu v1.3.1 Disulfide Bond Test on BPTI + HEWL

## Objective

Generate 100 BioEmu conformations each for BPTI (58 residues, 3 disulfide bonds) and
HEWL (129 residues, 4 disulfide bonds), measure S-S distances for all disulfide bonds
in every conformation, compute the disulfide integrity metric (fraction of conformations
with all SS bonds intact), and produce a clear GO/NO-GO assessment against the T3 and
AK3 thresholds. This is the first computational experiment in the project and provides
critical early evidence for the combined paper decision (D6, August 31).

---

## Context

BioEmu is a generative diffusion model trained on AMBER ff14SB trajectories. It
generates protein backbone conformations but does not explicitly model covalent bonds
like disulfide bridges. There is a risk that generated conformations will have broken
disulfide bonds -- sulfur atoms too far apart (>2.5 Å) to be considered bonded.

**Thresholds from the Implementation Plan:**
- **T3 (Combined paper GO threshold):** BioEmu disulfide integrity >95% for both proteins
- **AK3 (Kill criterion, June 15):** If integrity <80%, drop BPTI and HEWL from the Alpha-M benchmark

**Zone interpretation:**
- ≥95%: T3 met, BPTI/HEWL fully included, combined paper viable on this criterion
- 80-95%: BPTI/HEWL remain in benchmark, but T3 fails (combined paper concern)
- <80%: AK3 fires, BPTI/HEWL dropped from benchmark (12 proteins remain)

**Dependencies:** This task depends on:
- `env-bioemu` from task-001 (conda environment with BioEmu v1.3.1 installed)
- BPTI and HEWL PDB files from task-003 (with disulfide topology verified)

---

## Detailed Instructions

### Step 1: Environment and Input Setup

1. Activate the env-bioemu environment: `conda activate env-bioemu`
2. Verify BioEmu is importable: `python -c "from bioemu import BioEmuSampler; print('OK')"`
3. Locate the BPTI PDB file from task-003 output: `proteins/bpti.pdb`
4. Locate the HEWL PDB file from task-003 output: `proteins/hewl.pdb`
5. Verify BPTI has 3 disulfide bonds in the PDB (Cys5-Cys55, Cys14-Cys38, Cys30-Cys51)
6. Verify HEWL has 4 disulfide bonds in the PDB (Cys6-Cys127, Cys30-Cys115, Cys64-Cys80, Cys76-Cys94)

### Step 2: Generate BioEmu Conformations for BPTI

1. Initialize BioEmuSampler with default parameters
2. Load BPTI sequence (58 residues)
3. Generate 100 backbone conformations
4. Save all conformations to a multi-model PDB or trajectory file
5. Log: generation time, GPU memory usage, any warnings

### Step 3: Measure BPTI Disulfide Distances

For each of the 100 conformations, measure the S-S (SG atom) distance for:
- Cys5-Cys55 (distance in Angstroms)
- Cys14-Cys38 (distance in Angstroms)
- Cys30-Cys51 (distance in Angstroms)

Use MDAnalysis or BioPython to extract SG atom coordinates and compute distances.

**Integrity definition:** A conformation has "intact" disulfide bonds if ALL SS
distances are <2.5 Å (typical SS bond length: 2.03-2.05 Å; using 2.5 Å as generous cutoff).

Compute:
- Per-bond integrity: fraction of 100 conformations where that specific SS distance < 2.5 Å
- Overall integrity: fraction of 100 conformations where ALL 3 SS bonds are simultaneously intact
- Distance statistics: mean, std, min, max for each SS bond across all conformations

### Step 4: Generate BioEmu Conformations for HEWL

1. Load HEWL sequence (129 residues)
2. Generate 100 backbone conformations
3. Save all conformations
4. Log: generation time, GPU memory usage, any warnings

### Step 5: Measure HEWL Disulfide Distances

For each of the 100 conformations, measure S-S distances for:
- Cys6-Cys127
- Cys30-Cys115
- Cys64-Cys80
- Cys76-Cys94

Compute the same metrics as for BPTI (per-bond, overall, distance statistics).

### Step 6: Generate Visualizations

Create the following plots:
1. **Violin/box plot:** SS distance distribution per bond for BPTI (3 bonds, 100 values each)
2. **Violin/box plot:** SS distance distribution per bond for HEWL (4 bonds, 100 values each)
3. **Histogram:** Overall SS distance distribution for all bonds combined
4. Mark the 2.5 Å threshold on all plots

Save plots as PNG files.

### Step 7: Threshold Assessment

Write a clear assessment document:

```
BPTI (58 res, 3 SS bonds):
  Overall integrity: XX.X% (XX of 100 conformations with ALL 3 bonds intact)
  Per-bond integrity:
    Cys5-Cys55:   XX.X% (mean dist: X.XX ± X.XX Å)
    Cys14-Cys38:  XX.X% (mean dist: X.XX ± X.XX Å)
    Cys30-Cys51:  XX.X% (mean dist: X.XX ± X.XX Å)

HEWL (129 res, 4 SS bonds):
  Overall integrity: XX.X% (XX of 100 conformations with ALL 4 bonds intact)
  Per-bond integrity:
    Cys6-Cys127:  XX.X% (mean dist: X.XX ± X.XX Å)
    Cys30-Cys115: XX.X% (mean dist: X.XX ± X.XX Å)
    Cys64-Cys80:  XX.X% (mean dist: X.XX ± X.XX Å)
    Cys76-Cys94:  XX.X% (mean dist: X.XX ± X.XX Å)

THRESHOLD ASSESSMENT:
  T3 (>95%): [MET / NOT MET] for BPTI, [MET / NOT MET] for HEWL
  AK3 (<80%): [TRIGGERED / NOT TRIGGERED] for BPTI, [TRIGGERED / NOT TRIGGERED] for HEWL
```

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| `../../tasks/task-003-alpha-verification.md` | Understand where PDB files and manifest are located |
| `../proteins/manifest.json` | Protein metadata, PDB paths, disulfide bond definitions |
| `../../../../Proposal/Alpha-M.md` (Section 2.2: BPTI/HEWL details; Section 7: Kill criteria AK3) | Disulfide bond specifics and failure thresholds |
| `../../../../Proposal/Combined-Alpha-Gamma.md` (Section 3.2: T3 threshold) | Combined paper GO threshold for disulfide integrity |
| `../../../../Proposal/ImplementationPlan.md` (Section 8: Phase 0 BioEmu test; Section 10.1: AK3) | Task requirements and kill criteria |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../status/task-001-status.md` | Confirm env-bioemu was successfully built |
| `../../status/task-003-status.md` | Confirm PDB files are ready |

### DO NOT READ

- `../../../../Proposal/HumanOnlyProposal.md` -- off-limits to all AI agents
- Other SubAgent task specs (task-001, task-002) -- not your scope
- Delta proposal -- different track

---

## Output Artifacts

### Code and data artifacts

| Artifact | Path | Format |
|----------|------|--------|
| BioEmu analysis script | `output/task-004-bioemu-analysis.py` | Python |
| BPTI conformations | `output/task-004-bpti-conformations.pdb` | Multi-model PDB |
| HEWL conformations | `output/task-004-hewl-conformations.pdb` | Multi-model PDB |
| BPTI SS distance data | `output/task-004-bpti-ss-distances.csv` | CSV |
| HEWL SS distance data | `output/task-004-hewl-ss-distances.csv` | CSV |
| BPTI SS distribution plot | `output/task-004-bpti-ss-plot.png` | PNG |
| HEWL SS distribution plot | `output/task-004-hewl-ss-plot.png` | PNG |
| Threshold assessment | `output/task-004-ss-integrity-report.md` | Markdown |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-004-status.md` | `status-report.md` |
| Experiment log | `../../output/task-004-experiment.md` | `experiment-log.md` |
| Cross-agent note (if <95%) | `../../../../../../shared/notes/0.1-bioemu-disulfide.md` | `cross-agent-note.md` |

---

## Success Criteria (Zero Compromise)

This task is complete ONLY if ALL of the following are true:

1. [ ] 100 BioEmu conformations generated for BPTI
2. [ ] 100 BioEmu conformations generated for HEWL
3. [ ] S-S distances measured for all disulfide bonds in all conformations
4. [ ] Per-bond and overall integrity metrics computed for both proteins
5. [ ] Distance statistics (mean, std, min, max) computed for each bond
6. [ ] Visualization plots generated for both proteins
7. [ ] Clear threshold assessment: T3 (>95%) and AK3 (<80%) evaluated for both proteins
8. [ ] If integrity <95% for either protein: cross-agent note written flagging T3 risk
9. [ ] If integrity <80% for either protein: cross-agent note written flagging AK3 kill
10. [ ] Experiment log written with BioEmu version, GPU used, generation time, parameters
11. [ ] Status report written to `../../status/task-004-status.md`

---

## Verification

Before declaring this task complete, verify:

1. Conformation files exist and contain 100 models each
2. CSV distance files have correct dimensions (100 rows x 3 columns for BPTI, 100 x 4 for HEWL)
3. No NaN or negative distance values in CSV files
4. Integrity percentages sum correctly (manual spot-check: count rows where all distances < 2.5 Å)
5. Plot files are non-empty PNG images
6. Threshold assessment document has explicit MET/NOT MET for T3 and TRIGGERED/NOT TRIGGERED for AK3

---

## Failure Protocol

If this task cannot be completed:

1. Write a status report with status `failed` or `blocked`
2. Document exactly what went wrong (error messages, log excerpts)
3. Document what was tried and why it did not work
4. Identify what help is needed for the HeadAI to resolve or escalate
5. DO NOT silently skip steps or lower the success criteria
6. **Common failure modes:**
   - BioEmu import error → check env-bioemu was built correctly (read task-001 status)
   - BioEmu crashes on HEWL (129 res, larger than typical) → try with fewer conformations (50), document the issue
   - GPU out of memory → try CPU generation (slower but should work), document memory requirements
   - PDB files not found → check task-003 status, verify paths in manifest.json
