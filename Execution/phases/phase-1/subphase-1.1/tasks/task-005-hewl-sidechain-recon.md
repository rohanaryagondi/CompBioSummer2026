---
task_id: "task-005"
title: "Sidechain Reconstruction Test (HEWL SS Bonds)"
subphase: "1.1"
track: alpha-m
wave: 2
agent: "sc-recon"
effort: "1-2 days"
status: planned
created: 2026-04-16
---

# Task 005: Sidechain Reconstruction Test (HEWL SS Bonds)

## Objective

Resolve the HEWL disulfide integrity question from Phase 0 by reconstructing
sidechains on the 100 BioEmu HEWL backbone conformations and measuring true SG-SG
distances. Phase 0 measured CB-CB proxy distances because BioEmu outputs backbone
atoms only. CB-CB at 4.5 A showed 70.7% integrity (AK3 triggered), but at 5.0 A
showed 90.9% (AK3 not triggered). True SG-SG distances will definitively determine
whether HEWL should remain in the Alpha-M benchmark (13 proteins) or be dropped
(12 proteins, T5 boundary).

---

## Context

BioEmu v1.3.1 outputs 5 atoms per residue (N, CA, C, CB, O). No sidechain atoms
are generated. In Phase 0 (task-004), disulfide bond integrity was assessed using
CB-CB distance as a proxy for the standard SG-SG measurement. The CB-CB distance
overestimates the actual bond distance because CB is farther from the bond center
than SG.

**HEWL has 4 disulfide bonds:**
- Cys6-Cys127
- Cys30-Cys115
- Cys64-Cys80
- Cys76-Cys94

**Phase 0 results (CB-CB proxy):**

| Cutoff | Integrity | AK3 (<80%) |
|--------|-----------|-----------|
| 4.5 A | 70.7% | TRIGGERED |
| 5.0 A | 90.9% | Not triggered |
| 5.5 A | 93.9% | Not triggered |

The question: when sidechain atoms are reconstructed and true SG-SG distances are
measured at the standard 2.5 A crystallographic cutoff, does HEWL pass AK3?

**AK3 threshold:** SS integrity <80% triggers protein drop from benchmark.
**T5 threshold:** >=12 proteins with usable S2 data. Currently 13 without BPTI
(already dropped). Dropping HEWL would leave 12 (T5 boundary, no margin).

---

## Detailed Instructions

### Step 1: Locate Phase 0 HEWL Conformations

1. Find HEWL conformations from Phase 0 task-004:
   ```
   ../../phase-0/subphase-0.1/output/task-004-hewl/
   ```
2. Count files: expect 100 PDB files (or fewer — Phase 0 reported 99 valid of 100)
3. Verify format: backbone atoms only (N, CA, C, CB, O per residue)
4. Note: HEWL has 129 residues, so expect 129 * 5 = 645 atoms per conformation
   (minus any residues where CB is absent, e.g., Gly)

### Step 2: Install Sidechain Reconstruction Tool

**Option A: SCWRL4 (preferred — fast, widely validated)**
1. Check if SCWRL4 is available: `which scwrl4` or `module avail scwrl`
2. If not available, download from http://dunbrack.fccc.edu/SCWRL3.php
   (free for academic use, requires registration)
3. Install binary to a local path

**Option B: Rosetta fixbb (more accurate, slower)**
1. Check if Rosetta is available: `which rosetta_scripts` or `module avail rosetta`
2. If available, use the fixbb protocol for sidechain packing
3. If not available: this requires a large install (~30 GB). Skip to Option C.

**Option C: PDBFixer + OpenMM (fallback — available in env-classical)**
1. Activate env-classical: `conda activate env-classical`
2. Use PDBFixer to add missing atoms including sidechains:
   ```python
   from pdbfixer import PDBFixer
   fixer = PDBFixer(filename='hewl_conf_001.pdb')
   fixer.findMissingResidues()
   fixer.findMissingAtoms()
   fixer.addMissingAtoms()
   # Then extract SG positions
   ```

**Option D: MDAnalysis + simple rotamer library (last resort)**
1. Use MDAnalysis to build sidechains from a rotamer library
2. Less accurate but fully programmatic

Choose whichever option is available and practical. Document the choice and rationale.

### Step 3: Reconstruct Sidechains

For each of the ~99-100 HEWL conformations:

1. Read the backbone-only PDB
2. Reconstruct all sidechain atoms (especially Cys SG atoms)
3. Save the full-atom PDB to a new directory:
   ```bash
   mkdir -p ../../output/task-005-hewl-full-atom/
   ```
4. Verify that SG atoms are present for all 8 Cys residues (6, 30, 64, 76, 80, 94, 115, 127)

### Step 4: Measure SG-SG Distances

```python
import mdtraj as md
import numpy as np

results = []
for conf_file in sorted(conf_files):
    traj = md.load(conf_file)
    
    # Find SG atom indices for the 4 SS bonds
    ss_bonds = [
        (6, 127),   # Cys6-Cys127
        (30, 115),  # Cys30-Cys115
        (64, 80),   # Cys64-Cys80
        (76, 94),   # Cys76-Cys94
    ]
    
    for cys_i, cys_j in ss_bonds:
        # Find SG atoms (adjust for 0-indexing and atom selection)
        sg_i = traj.topology.select(f'resid {cys_i-1} and name SG')
        sg_j = traj.topology.select(f'resid {cys_j-1} and name SG')
        
        if len(sg_i) == 1 and len(sg_j) == 1:
            dist = md.compute_distances(traj, [[sg_i[0], sg_j[0]]])[0, 0]
            dist_angstrom = dist * 10  # nm to Angstrom
            results.append({
                'conformation': conf_file,
                'bond': f'Cys{cys_i}-Cys{cys_j}',
                'sg_sg_distance_A': dist_angstrom,
                'intact': dist_angstrom < 2.5  # standard SS bond cutoff
            })
```

### Step 5: Compute SS Integrity Metrics

1. **Per-bond integrity:** For each of 4 SS bonds, what fraction of conformations
   have SG-SG distance < 2.5 A?
2. **Overall integrity:** Average across all bonds and conformations
3. **Sensitivity analysis:** Also compute at 2.8 A, 3.0 A, 3.5 A cutoffs
4. **Compare with Phase 0 CB-CB results:**

   | Metric | CB-CB (Phase 0, 4.5A) | CB-CB (Phase 0, 5.0A) | SG-SG (this task, 2.5A) |
   |--------|----------------------|----------------------|------------------------|
   | Overall | 70.7% | 90.9% | ? |
   | Weakest bond | Cys76-Cys94: 88.9% | ? | ? |

### Step 6: HEWL Recommendation

Based on SG-SG results:

- **If SG-SG integrity >= 80% at 2.5 A:** KEEP HEWL. The CB-CB proxy was overly
  pessimistic. Document this as a methodological finding (CB-CB vs SG-SG for
  backbone-only models).

- **If SG-SG integrity < 80% at 2.5 A:** DROP HEWL. Both proxy and true measurements
  confirm poor SS bond integrity. Benchmark goes to 12 proteins (T5 boundary).

- **If SG-SG integrity is 70-80% at 2.5 A:** BORDERLINE. Recommend keeping with
  documented limitation. Report both measurements in the paper.

Write the recommendation with supporting evidence.

---

## File Access

### MUST READ (required before starting)

| File | Why |
|------|-----|
| `../../tasks/task-005-hewl-sidechain-recon.md` | This task specification |
| `../../../../phase-0/subphase-0.1/output/task-004-hewl/` | HEWL backbone conformations (input) |
| `../../../../../shared/notes/0.1-bioemu-disulfide.md` | Phase 0 CB-CB results, bond details |
| `../../../../phase-0/subphase-0.1/completion-report.md` (Section 2, Task 004) | HEWL results detail |
| `../../../../phase-0/subphase-0.1/proteins/manifest.json` | HEWL PDB metadata |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../Proposal/Alpha-M.md` (Section 5) | Kill criteria AK3 details |
| `../../phase-0/subphase-0.1/output/task-004-ss-integrity-report.md` | Full Phase 0 SS report |

### DO NOT READ

- Other SubAgents' task specs (not your scope)
- Delta or Gamma files (not relevant)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)

---

## Output Artifacts

### Code and data artifacts

| Artifact | Path | Format |
|----------|------|--------|
| Reconstruction script | `../../output/scripts/hewl_sidechain_recon.py` | Python |
| Full-atom conformations | `../../output/task-005-hewl-full-atom/` | PDB |
| SG-SG distance table | `../../output/task-005-hewl-sgsg-distances.csv` | CSV |
| Integrity report | `../../output/task-005-hewl-integrity-report.md` | Markdown |

### Mandatory documentation

| Document | Path | Template |
|----------|------|----------|
| Status report | `../../status/task-005-status.md` | `status-report.md` |
| Cross-agent note | `../../../../../shared/notes/1.1-hewl-sgsg.md` | `cross-agent-note.md` |

---

## Success Criteria (Zero Compromise)

1. [ ] Sidechains reconstructed for >=95 of ~100 HEWL conformations
2. [ ] SG atoms present for all 8 Cys residues in reconstructed structures
3. [ ] SG-SG distances measured for all 4 disulfide bonds per conformation
4. [ ] SS integrity computed at 2.5 A SG-SG cutoff (primary) and 2.8, 3.0, 3.5 A (sensitivity)
5. [ ] Comparison table: CB-CB proxy (Phase 0) vs SG-SG (this task)
6. [ ] Clear HEWL keep/drop recommendation with supporting evidence
7. [ ] Cross-agent note written to `shared/notes/1.1-hewl-sgsg.md` (urgency: important, tracks: alpha-m, combined)
8. [ ] Status report written to `../../status/task-005-status.md`

---

## Verification

1. `ls ../../output/task-005-hewl-full-atom/ | wc -l` shows >=95 PDB files
2. Spot-check 3 conformations: `grep ' SG ' conf_001.pdb` shows 8 SG atoms
3. Distance CSV has rows for all 4 bonds x ~100 conformations = ~400 rows
4. Integrity report includes the comparison table and clear recommendation
5. Cross-agent note exists at `shared/notes/1.1-hewl-sgsg.md`

---

## Failure Protocol

1. If no sidechain reconstruction tool is available: document what was tried,
   recommend human install SCWRL4 or Rosetta, write status report as `blocked`
2. If reconstruction produces physically unreasonable SG positions: document the
   issue, try alternative method, report in status
3. If >=5 conformations fail reconstruction: investigate common cause, report partial
   results
4. This task provides a clear answer even if the answer is "we can't reconstruct
   sidechains reliably" — that itself informs the HEWL decision (keep with CB-CB
   limitation documented)
