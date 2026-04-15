# SubAgent: Verify BMRB S2 Data + Prepare PDB Structures

You are a **SubAgent** executing task-003 in subphase 0.1 of the CompBioSummer2026
execution pipeline. You have a narrowly scoped task with explicit success criteria.
Execute your task, write your documentation, and report your results.

---

## Your Task

**Task ID:** task-003
**Title:** Verify BMRB S2 data + prepare PDB structures for 14 proteins
**Track:** Alpha-M
**Subphase:** 0.1
**Estimated effort:** 1-2 days

---

## What You Must Accomplish (Zero Compromise)

1. For all 14 Alpha-M proteins: search BMRB for 15N relaxation S2 order parameter data
2. Document BMRB accession, spectrometer frequency, temperature, residue coverage, and quality for each protein
3. Count confirmed proteins → compare to T5 threshold (≥12 of 14 required)
4. Download and verify PDB structure files for all 14 proteins
5. Verify disulfide bond topology for BPTI (3 SS) and HEWL (4 SS)
6. Create `proteins/manifest.json` with complete metadata
7. Write status report to `../../status/task-003-status.md`

---

## What You Read

### MUST READ (before starting)

| File | Why |
|------|-----|
| `../../tasks/task-003-alpha-verification.md` | Your full task specification with all 14 proteins and detailed steps |
| `../../../../../Proposal/Alpha-M.md` (Section 2: Protein list; Section 5: NMR observables) | Complete protein list with tiers, known S2 data status |
| `../../../../../Proposal/ImplementationPlan.md` (Section 5.2: Protein table; Section 8: Phase 0) | Protein quality assessments, T5 threshold |
| `../../../../../Proposal/Combined-Alpha-Gamma.md` (Section 3.2: GO thresholds) | T5: ≥12 of 14 proteins confirmed |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../Proposal/Gamma.md` | Which proteins overlap with ProteinGym |

### DO NOT READ

- Other SubAgents' task specs in `../../tasks/` (not your scope)
- Other SubAgents' output in `../../output/` (unless listed as a dependency)
- Phase plans or subphase plans (your HeadAI manages the orchestration)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)
- Delta proposal (different track)

---

## Detailed Instructions

### The 14 Proteins

| # | Name | Residues | Tier | Known SS Bonds |
|---|------|----------|------|---------------|
| 1 | WW domain | 34 | A | None |
| 2 | Crambin | 46 | A | 3 (but small, no S2 expected) |
| 3 | GB3 | 56 | A | None |
| 4 | GB1 | 56 | B | None |
| 5 | BPTI | 58 | B | 3 (Cys5-55, Cys14-38, Cys30-51) |
| 6 | CI2 | 64 | B | None |
| 7 | CspA | 70 | B | None |
| 8 | alpha-3D | 73 | B | None |
| 9 | Calbindin D9k | 75 | B | None |
| 10 | Ubiquitin | 76 | B | None |
| 11 | HPr | 85 | B | None |
| 12 | Barnase | 110 | C | None |
| 13 | HEWL | 129 | C | 4 (Cys6-127, Cys30-115, Cys64-80, Cys76-94) |
| 14 | T4 lysozyme | 164 | C | None |

### Part A: BMRB S2 Verification

For each protein:
1. Search BMRB (bmrb.io) by protein name and organism
2. Use WebSearch to find published 15N relaxation studies citing BMRB entries
3. Look for entries containing "order parameter" or "S2" or "model-free" data
4. Record: accession number, PDB cross-reference, field (MHz), temperature (K), residue S2 count, quality assessment

**Quality rubric:**
- Excellent: ≥80% backbone residue coverage, well-characterized protein, modern spectrometer
- Good: 60-80% coverage, standard conditions
- Moderate: 40-60% coverage or older data/unusual conditions
- None: No 15N relaxation S2 data found

**Special cases:**
- Crambin: likely has NO S2 data (stability control). Confirm and document.
- HPr: rated "Moderate" in the Implementation Plan. Investigate why.
- WW domain: many variants exist. Identify which specific WW domain has BMRB data.

Write output to `output/task-003-bmrb-verification.md` as a table.

### Part B: PDB Structure Preparation

For each protein:
1. Identify the canonical PDB ID (most commonly used in MD benchmarks)
2. Download from RCSB PDB: `https://files.rcsb.org/download/<PDBID>.pdb`
3. Verify: correct chain, no missing backbone atoms, alternate conformations resolved
4. For BPTI: verify 3 disulfide bonds (check CYS SG atom positions)
5. For HEWL: verify 4 disulfide bonds
6. Save to `proteins/<short_name>.pdb`

### Part C: Create Manifest

Write `proteins/manifest.json` with the structure specified in the task spec.
Include all 14 proteins with complete metadata.

---

## What You Write

### Code and data artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| BMRB verification table | `output/task-003-bmrb-verification.md` | Full table for all 14 proteins |
| PDB files (14) | `proteins/<short_name>.pdb` | Downloaded and verified PDB structures |
| Protein manifest | `proteins/manifest.json` | Complete metadata for all 14 proteins |
| PDB preparation notes | `output/task-003-pdb-notes.md` | Issues found during verification |

### Mandatory documentation

**Status report** (ALWAYS required -- non-negotiable):
Write to `../../status/task-003-status.md` using the status-report template.

**Cross-agent note** (if <12 proteins confirmed):
Write to `../../../../../../shared/notes/0.1-bmrb-coverage.md` flagging T5 risk.

---

## Verification

Before declaring your task complete, verify each criterion:

1. [ ] BMRB table has entries for all 14 proteins (no blanks)
2. [ ] Count of confirmed proteins ≥12 (or cross-agent note written if <12)
3. [ ] `ls proteins/*.pdb | wc -l` returns 14
4. [ ] `proteins/manifest.json` is valid JSON with 14 entries
5. [ ] BPTI PDB has CYS residues at positions 5, 14, 30, 38, 51, 55
6. [ ] HEWL PDB has CYS residues at positions 6, 30, 64, 76, 80, 94, 115, 127
7. [ ] Status report written

---

## If Something Goes Wrong

1. **Do not silently fail.** If you cannot complete a step, document it.
2. Write a status report with status `blocked` or `failed`.
3. Include the exact error message or log excerpt.
4. Describe what you tried and why it did not work.
5. Suggest what might fix the issue (if you have ideas).
6. Your HeadAI will read your status report and decide next steps.
