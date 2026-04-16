---
task_id: "task-005"
agent: "sc-recon"
subphase: "1.1"
status: complete
date: 2026-04-16
---

# Task 005 Status Report: Sidechain Reconstruction Test (HEWL SS Bonds)

## Status: COMPLETE

## Summary

Sidechains were reconstructed on all 99 BioEmu HEWL backbone conformations using
PDBFixer (OpenMM 8.3.1). True SG-SG distances were measured for all 4 disulfide
bonds. The results are unambiguous: HEWL fails AK3 with 40.2% SG-SG integrity at
2.5 A (threshold: <80%).

**HEWL recommendation: DROP from Alpha-M benchmark.**

## Success Criteria Evaluation

1. [x] Sidechains reconstructed for >=95 of ~100 HEWL conformations
   - **99/99 successful (100%).** All conformations reconstructed. Input had 99
     valid frames (not 100 as originally estimated).

2. [x] SG atoms present for all 8 Cys residues in reconstructed structures
   - **Verified.** All 99 PDBs contain exactly 8 SG atoms (spot-checked 3 conformations).

3. [x] SG-SG distances measured for all 4 disulfide bonds per conformation
   - **396 measurements** (99 conformations x 4 bonds). No errors or missing values.

4. [x] SS integrity computed at 2.5 A SG-SG cutoff (primary) and 2.8, 3.0, 3.5 A (sensitivity)
   - **Primary (2.5A): 40.2%** -- AK3 TRIGGERED
   - 2.8A: 43.4%, 3.0A: 43.9%, 3.5A: 51.8% -- all trigger AK3

5. [x] Comparison table: CB-CB proxy (Phase 0) vs SG-SG (this task)
   - CB-CB at 4.5A: 70.7% vs SG-SG at 2.5A: 40.2%
   - CB-CB was optimistic, not conservative. Important methodological finding.

6. [x] Clear HEWL keep/drop recommendation with supporting evidence
   - **DROP.** 40.2% is 40 percentage points below the 80% threshold. No ambiguity.

7. [x] Cross-agent note written to `shared/notes/1.1-hewl-sgsg.md`
   - Written with urgency: important, tracks: alpha-m, combined

8. [x] Status report written (this document)

## Key Results

| Metric | Value |
|--------|-------|
| Conformations processed | 99/99 (100%) |
| Reconstruction tool | PDBFixer (OpenMM 8.3.1) |
| SG-SG integrity at 2.5 A | **40.2%** |
| AK3 threshold | <80% -> DROP |
| Best bond (Cys6-Cys127) | 71.7% at 2.5 A |
| Worst bond (Cys30-Cys115) | 15.2% at 2.5 A |
| HEWL recommendation | **DROP** |
| Benchmark size after drop | 12 proteins (T5 boundary) |

## Artifacts Produced

| Artifact | Path | Size |
|----------|------|------|
| Reconstruction script | `output/scripts/hewl_sidechain_recon.py` | 7.4 KB |
| Full-atom PDBs (99) | `output/task-005-hewl-full-atom/` | ~99 MB |
| SG-SG distance CSV | `output/task-005-hewl-sgsg-distances.csv` | 16 KB |
| Integrity report | `output/task-005-hewl-integrity-report.md` | 5.6 KB |
| Results JSON | `output/task-005-results.json` | 1.8 KB |
| Cross-agent note | `shared/notes/1.1-hewl-sgsg.md` | 2.8 KB |

## Resource Usage

| Resource | Estimated | Actual |
|----------|-----------|--------|
| Wall time | 2-4 hours | **~17 minutes** |
| GPU-hours | 0 | 0 |
| CPU | Single core | Single core |
| Storage | ~100 MB | ~99 MB |

## Issues Encountered

1. **NumPy/scipy not installed in system Python.** Required `pip3 install --user
   numpy scipy` before mdtraj could import. PDBFixer and OpenMM were already
   installed in user site-packages.

2. **SCWRL4 and Rosetta not available on HPC.** Fell back to Option C (PDBFixer),
   which worked perfectly and was faster than expected.

3. **Input was 99 frames, not 100.** The XTC trajectory had 99 valid frames (as
   documented in Phase 0 completion report -- 99 valid of 100 generated).

## Recommendations for Next Steps

1. **Update Alpha-M protein set to 12 proteins** in all Subphase 1.2+ planning
2. **Flag T5 boundary risk** -- no margin for further protein drops
3. **Document CB-CB vs SG-SG methodological finding** in the paper methods section
4. **Consider sidechain reconstruction** as part of the standard BioEmu postprocessing
   pipeline for any future SS-containing proteins
