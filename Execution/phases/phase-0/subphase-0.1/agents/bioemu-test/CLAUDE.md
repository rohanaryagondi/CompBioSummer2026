# SubAgent: BioEmu Disulfide Bond Test

You are a **SubAgent** executing task-004 in subphase 0.1 of the CompBioSummer2026
execution pipeline. You have a narrowly scoped task with explicit success criteria.
Execute your task, write your documentation, and report your results.

---

## Your Task

**Task ID:** task-004
**Title:** BioEmu v1.3.1 disulfide bond test on BPTI + HEWL
**Track:** Alpha-M
**Subphase:** 0.1
**Estimated effort:** 1-2 days

---

## What You Must Accomplish (Zero Compromise)

1. Generate 100 BioEmu conformations for BPTI (58 res, 3 disulfide bonds)
2. Generate 100 BioEmu conformations for HEWL (129 res, 4 disulfide bonds)
3. Measure S-S distances for all disulfide bonds in all conformations
4. Compute per-bond and overall integrity metrics (% of conformations with all SS <2.5 Å)
5. Produce visualization plots of SS distance distributions
6. Write clear threshold assessment: T3 (>95%) and AK3 (<80%)
7. Write experiment log to `../../output/task-004-experiment.md`
8. Write status report to `../../status/task-004-status.md`

---

## What You Read

### MUST READ (before starting)

| File | Why |
|------|-----|
| `../../tasks/task-004-bioemu-disulfide.md` | Your full task specification with thresholds and measurement protocol |
| `../proteins/manifest.json` | Protein metadata: PDB paths, disulfide bond definitions |
| `../../../../../Proposal/Alpha-M.md` (Section 2.2, Section 7: AK3) | BPTI/HEWL details, kill criterion |
| `../../../../../Proposal/Combined-Alpha-Gamma.md` (Section 3.2: T3) | Combined paper GO threshold for disulfide integrity |
| `../../../../../Proposal/ImplementationPlan.md` (Section 8, Section 10.1: AK3) | Task requirements, kill criteria |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../status/task-001-status.md` | Confirm env-bioemu was built successfully |
| `../../status/task-003-status.md` | Confirm PDB files are ready |

### DO NOT READ

- Other SubAgents' task specs (task-001, task-002) -- not your scope
- Phase plans or subphase plans (your HeadAI manages the orchestration)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)
- Delta proposal (different track)

---

## Detailed Instructions

### Step 1: Setup

```bash
conda activate env-bioemu
python -c "from bioemu import BioEmuSampler; print('BioEmu OK')"
```

Load PDB files from task-003:
- BPTI: `../proteins/bpti.pdb`
- HEWL: `../proteins/hewl.pdb`

### Step 2: Generate BPTI Conformations

```python
from bioemu import BioEmuSampler
sampler = BioEmuSampler()
# Load BPTI sequence (58 residues)
# Generate 100 conformations
# Save to output/task-004-bpti-conformations.pdb
```

Log: generation time, GPU used, memory usage, BioEmu version, any warnings.

### Step 3: Measure BPTI SS Distances

For each of 100 conformations, measure SG-SG distances (Å) for:
- Cys5-Cys55
- Cys14-Cys38
- Cys30-Cys51

Use MDAnalysis, BioPython, or direct coordinate extraction.

Save raw data: `output/task-004-bpti-ss-distances.csv`
Format: `conformation_id, cys5_cys55, cys14_cys38, cys30_cys51`

### Step 4: Generate HEWL Conformations

Same as Step 2 but for HEWL (129 residues).
Save to `output/task-004-hewl-conformations.pdb`.

### Step 5: Measure HEWL SS Distances

For each of 100 conformations, measure SG-SG distances (Å) for:
- Cys6-Cys127
- Cys30-Cys115
- Cys64-Cys80
- Cys76-Cys94

Save raw data: `output/task-004-hewl-ss-distances.csv`
Format: `conformation_id, cys6_cys127, cys30_cys115, cys64_cys80, cys76_cys94`

### Step 6: Compute Metrics

For each protein:
- **Per-bond integrity:** fraction of conformations where that bond's SS distance < 2.5 Å
- **Overall integrity:** fraction where ALL bonds simultaneously < 2.5 Å
- **Distance stats:** mean, std, min, max per bond

### Step 7: Generate Plots

- Violin/box plot: SS distance per bond for BPTI (3 subplots)
- Violin/box plot: SS distance per bond for HEWL (4 subplots)
- Mark the 2.5 Å threshold line on each plot
- Save as PNG: `output/task-004-bpti-ss-plot.png`, `output/task-004-hewl-ss-plot.png`

### Step 8: Threshold Assessment

Write `output/task-004-ss-integrity-report.md` with:
- Exact percentages for per-bond and overall integrity
- Clear MET/NOT MET verdict for T3 (>95%)
- Clear TRIGGERED/NOT TRIGGERED verdict for AK3 (<80%)
- Recommendation for downstream planning

---

## What You Write

### Code and data artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Analysis script | `output/task-004-bioemu-analysis.py` | Full analysis pipeline |
| BPTI conformations | `output/task-004-bpti-conformations.pdb` | 100 BioEmu structures |
| HEWL conformations | `output/task-004-hewl-conformations.pdb` | 100 BioEmu structures |
| BPTI SS distances | `output/task-004-bpti-ss-distances.csv` | Raw distance measurements |
| HEWL SS distances | `output/task-004-hewl-ss-distances.csv` | Raw distance measurements |
| BPTI SS plot | `output/task-004-bpti-ss-plot.png` | Distance distribution visualization |
| HEWL SS plot | `output/task-004-hewl-ss-plot.png` | Distance distribution visualization |
| Integrity report | `output/task-004-ss-integrity-report.md` | Threshold assessment |

### Mandatory documentation

**Status report** (ALWAYS required -- non-negotiable):
Write to `../../status/task-004-status.md` using the status-report template.

**Experiment log** (ALWAYS required -- this is a computational experiment):
Write to `../../output/task-004-experiment.md` using the experiment-log template.

**Cross-agent note** (if integrity <95% for either protein):
Write to `../../../../../../shared/notes/0.1-bioemu-disulfide.md` using the cross-agent-note template.
Tag: `alpha-m`, `combined`. Urgency: `important` if 80-95%, `critical` if <80%.

---

## Verification

Before declaring your task complete, verify each criterion:

1. [ ] BPTI conformation file contains 100 models
2. [ ] HEWL conformation file contains 100 models
3. [ ] BPTI CSV has 100 rows × 3 distance columns (no NaN, no negative values)
4. [ ] HEWL CSV has 100 rows × 4 distance columns (no NaN, no negative values)
5. [ ] Integrity percentages are between 0-100% and manually verifiable from CSV
6. [ ] Plot files are non-empty PNGs
7. [ ] Integrity report has explicit MET/NOT MET for T3, TRIGGERED/NOT TRIGGERED for AK3
8. [ ] Experiment log records BioEmu version, GPU type, generation time
9. [ ] Status report written

---

## If Something Goes Wrong

1. **Do not silently fail.** If you cannot complete a step, document it.
2. Write a status report with status `blocked` or `failed`.
3. Include the exact error message or log excerpt.
4. Describe what you tried and why it did not work.
5. Suggest what might fix the issue (if you have ideas).
6. Your HeadAI will read your status report and decide next steps.

**Common issues:**
- BioEmu import error → check env-bioemu (read task-001 status report)
- GPU out of memory on HEWL (129 res) → try CPU mode or reduce to 50 conformations
- BioEmu crash → check version (must be v1.3.1), report exact error
- PDB files not at expected path → check task-003 status, check manifest.json
