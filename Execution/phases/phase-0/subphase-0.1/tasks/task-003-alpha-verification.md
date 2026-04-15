---
task_id: "task-003"
title: "Verify BMRB S2 Data + Prepare PDB Structures for 14 Proteins"
subphase: "0.1"
track: alpha-m
wave: 1
agent: "alpha-scout"
effort: "1-2 days"
status: planned
created: 2026-04-15
---

# Task 003: Verify BMRB S2 Data + Prepare PDB Structures for 14 Proteins

## Objective

Verify that all 14 Alpha-M benchmark proteins have confirmed BMRB entries with 15N
relaxation S2 order parameter data, document the quality and coverage of each entry,
download and verify PDB structure files for all 14 proteins, and create a comprehensive
manifest file. This task validates the experimental reference data that the entire
Alpha-M benchmark depends on and prepares the input structures needed for Phase 1
molecular dynamics simulations.

---

## Context

The Alpha-M benchmark compares 10 ensemble generators against experimental NMR S2
order parameters across 14 proteins. The combined paper GO threshold T5 requires ≥12
of 14 proteins to have confirmed BMRB S2 data. If fewer than 12 are confirmed, the
combined paper viability drops. The PDB structures prepared here are the starting
point for every simulation in Phase 1 -- incorrect structures (wrong chain, missing
residues, broken disulfide topology) would invalidate all downstream results.

The 14 proteins span three tiers:
- **Tier A (<50 res):** WW domain (34), Crambin (46), GB3 (56)
- **Tier B (50-80 res):** GB1 (56), BPTI (58, 3 SS), CI2 (64), CspA (70), alpha-3D (73), Calbindin D9k (75), Ubiquitin (76), HPr (85)
- **Tier C (80-170 res):** Barnase (110), HEWL (129, 4 SS), T4 lysozyme (164)

---

## Detailed Instructions

### Part A: BMRB S2 Data Verification

For each of the 14 proteins, search the BMRB (Biological Magnetic Resonance Bank,
bmrb.io) for 15N backbone relaxation data containing Lipari-Szabo S2 order parameters.

For each protein, record:

1. **Protein name and residue count**
2. **BMRB accession number** (e.g., bmr12345)
3. **PDB ID cross-referenced** in the BMRB entry
4. **Spectrometer frequency** (MHz) used in the relaxation experiment
5. **Temperature** (K) of the experiment
6. **Number of residues with S2 values** reported
7. **S2 value range** (min, max, mean if available)
8. **Quality assessment:**
   - Excellent: ≥80% residue coverage, recent study, well-characterized protein
   - Good: 60-80% coverage, standard conditions
   - Moderate: 40-60% coverage or unusual conditions
   - None: No 15N relaxation S2 data found in BMRB

**Special cases to investigate:**
- **Crambin (46 res):** The Implementation Plan notes "None (stability only)". Confirm
  there is truly no 15N relaxation S2 data. Crambin serves as a stability control protein
  in the benchmark -- it may not need S2 data. Document this clearly.
- **HPr (85 res):** The Implementation Plan rates quality as "Moderate". Investigate
  why -- is it low residue coverage, old data, or unusual conditions?
- **WW domain (34 res):** Very small protein. Verify which specific WW domain variant
  has BMRB data (there are many WW domains in the literature).

**Search strategy:**
1. Search BMRB by protein name and UniProt ID
2. Use WebSearch to find published papers citing BMRB entries for each protein
3. Cross-reference with the Alpha-M proposal Table 1 (protein list)
4. For proteins with multiple BMRB entries, select the highest-quality one

**Output:** A markdown table in the BMRB verification report with all 14 proteins,
plus a summary count: "X of 14 proteins confirmed with usable S2 data."

### Part B: PDB Structure Preparation

For each of the 14 proteins:

1. **Identify the canonical PDB ID** -- the structure most commonly used in MD benchmark
   studies for this protein. Cross-reference with the BMRB entry's PDB ID.
2. **Download** the PDB file from RCSB PDB (rcsb.org)
3. **Verify structure completeness:**
   - Correct chain ID (select the appropriate chain for multi-chain entries)
   - No missing backbone atoms in the residue range of interest
   - Missing side-chain atoms documented (common for surface residues)
   - Alternate conformations resolved (select highest-occupancy)
   - Crystallographic waters: note their presence (important for some simulations)
4. **For disulfide-containing proteins:**
   - BPTI: Verify 3 SS bonds (Cys5-Cys55, Cys14-Cys38, Cys30-Cys51)
   - HEWL: Verify 4 SS bonds (Cys6-Cys127, Cys30-Cys115, Cys64-Cys80, Cys76-Cys94)
   - Confirm CYS residues are labeled as CYX (or equivalent) in the PDB for bonded cysteines
5. **Record metadata:** resolution, method (X-ray/NMR), deposition date, organism

### Part C: Create Manifest File

Create `proteins/manifest.json` with the following structure for each protein:

```json
{
  "proteins": [
    {
      "name": "Ubiquitin",
      "short_name": "ubq",
      "residue_count": 76,
      "tier": "B",
      "pdb_id": "1UBQ",
      "pdb_chain": "A",
      "residue_range": "1-76",
      "disulfide_bonds": [],
      "bmrb_accession": "bmrXXXXX",
      "bmrb_field_mhz": 600,
      "bmrb_temperature_k": 298,
      "bmrb_s2_residue_count": 70,
      "bmrb_quality": "Excellent",
      "pdb_resolution_a": 1.8,
      "pdb_method": "X-ray",
      "notes": ""
    }
  ],
  "summary": {
    "total_proteins": 14,
    "confirmed_s2": 13,
    "t5_threshold_met": true,
    "proteins_without_s2": ["Crambin"]
  }
}
```

Also create `proteins/` directory and save each PDB file there as `<short_name>.pdb`.

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| `../../../../Proposal/Alpha-M.md` (Section 2: Protein list, Section 5: NMR observables) | Complete protein list with tiers, residue counts, known S2 data status |
| `../../../../Proposal/ImplementationPlan.md` (Section 5.2: Protein table; Section 8: Phase 0 tasks) | Protein quality assessments, T5 threshold definition |
| `../../../../Proposal/Combined-Alpha-Gamma.md` (Section 3.2: GO thresholds) | T5 threshold: ≥12 of 14 proteins confirmed |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../Proposal/Gamma.md` | Which of these proteins overlap with ProteinGym |
| `../../../../context/mission-briefing.md` | General constraints |

### DO NOT READ

- `../../../../Proposal/HumanOnlyProposal.md` -- off-limits to all AI agents
- Other SubAgent task specs in `../tasks/` -- not your scope
- Delta proposal -- different track

---

## Output Artifacts

### Code and data artifacts

| Artifact | Path | Format |
|----------|------|--------|
| BMRB verification table | `output/task-003-bmrb-verification.md` | Markdown |
| PDB files (14 proteins) | `proteins/<short_name>.pdb` | PDB |
| Protein manifest | `proteins/manifest.json` | JSON |
| PDB preparation notes | `output/task-003-pdb-notes.md` | Markdown |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-003-status.md` | `status-report.md` |
| Cross-agent note (if <12 proteins confirmed) | `../../../../../../shared/notes/0.1-bmrb-coverage.md` | `cross-agent-note.md` |

---

## Success Criteria (Zero Compromise)

This task is complete ONLY if ALL of the following are true:

1. [ ] BMRB verification table complete for all 14 proteins (accession ID, field, temperature, residue coverage, quality)
2. [ ] Count of confirmed proteins with usable S2 data documented (compare to T5 threshold ≥12)
3. [ ] 14 PDB files downloaded and saved to `proteins/` directory
4. [ ] Each PDB file verified for chain selection, residue completeness, and alternate conformations
5. [ ] BPTI disulfide bonds verified (3 SS: Cys5-Cys55, Cys14-Cys38, Cys30-Cys51)
6. [ ] HEWL disulfide bonds verified (4 SS: Cys6-Cys127, Cys30-Cys115, Cys64-Cys80, Cys76-Cys94)
7. [ ] Manifest file created at `proteins/manifest.json` with complete metadata for all 14 proteins
8. [ ] If <12 proteins confirmed: cross-agent note written flagging T5 risk
9. [ ] Status report written to `../../status/task-003-status.md`

---

## Verification

Before declaring this task complete, verify:

1. `ls proteins/*.pdb | wc -l` returns 14
2. `proteins/manifest.json` is valid JSON and contains 14 protein entries
3. BMRB verification table has entries for all 14 proteins (no blanks)
4. For BPTI: `grep "CYS" proteins/bpti.pdb | grep "SG"` shows 6 sulfur atoms (3 SS bonds)
5. For HEWL: `grep "CYS" proteins/hewl.pdb | grep "SG"` shows 8 sulfur atoms (4 SS bonds)
6. Summary count in manifest matches the BMRB table count

---

## Failure Protocol

If this task cannot be completed:

1. Write a status report with status `failed` or `blocked`
2. Document exactly what went wrong (error messages, log excerpts)
3. Document what was tried and why it did not work
4. Identify what help is needed for the HeadAI to resolve or escalate
5. DO NOT silently skip steps or lower the success criteria
6. **Partial success is valuable:** If BMRB verification is complete but some PDB files have issues, document the issues and provide what you have. Phase 1 agents can address specific PDB problems.
