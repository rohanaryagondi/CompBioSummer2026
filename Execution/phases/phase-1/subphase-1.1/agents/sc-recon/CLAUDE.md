# SubAgent: Sidechain Reconstruction Test (HEWL SS Bonds)

You are a **SubAgent** executing task-005 in subphase 1.1 of the CompBioSummer2026
execution pipeline. You have a narrowly scoped task with explicit success criteria.
Execute your task, write your documentation, and report your results.

---

## Your Task

**Task ID:** task-005
**Title:** Sidechain reconstruction test (HEWL disulfide bonds)
**Track:** Alpha-M
**Subphase:** 1.1
**Estimated effort:** 1-2 days

---

## What You Must Accomplish (Zero Compromise)

1. Reconstruct sidechains on ~100 BioEmu HEWL backbone conformations from Phase 0
2. Measure true SG-SG distances for all 4 disulfide bonds per conformation
3. Compute SS integrity at 2.5 A SG-SG cutoff (primary) and sensitivity cutoffs
4. Compare with Phase 0 CB-CB proxy results
5. Write clear HEWL keep/drop recommendation based on AK3 threshold (<80%)
6. Write cross-agent note to `../../../../../shared/notes/1.1-hewl-sgsg.md`
7. Write status report to `../../status/task-005-status.md`

**HEWL has 4 disulfide bonds:** Cys6-Cys127, Cys30-Cys115, Cys64-Cys80, Cys76-Cys94

---

## What You Read

### MUST READ (before starting)

| File | Why |
|------|-----|
| `../../tasks/task-005-hewl-sidechain-recon.md` | Full task specification with 4 tool options |
| `../../../../phase-0/subphase-0.1/output/task-004-hewl/` | 100 HEWL backbone PDB files (INPUT) |
| `../../../../../shared/notes/0.1-bioemu-disulfide.md` | Phase 0 CB-CB results, bond details |
| `../../../../phase-0/subphase-0.1/completion-report.md` (Section 2, Task 004) | HEWL results detail |
| `../../../../phase-0/subphase-0.1/proteins/manifest.json` | HEWL PDB reference metadata |

### MAY READ (optional context)

| File | Why |
|------|-----|
| `../../../../../Proposal/Alpha-M.md` (Section 5) | AK3 kill criteria |

### DO NOT READ

- Other SubAgents' task specs, Delta/Gamma files (not your scope)
- `../../../../../Proposal/HumanOnlyProposal.md` (off-limits)

---

## Detailed Instructions

Follow `../../tasks/task-005-hewl-sidechain-recon.md`. Key points:

1. **Input:** `../../phase-0/subphase-0.1/output/task-004-hewl/` (~100 PDB files)
2. **Sidechain reconstruction** — try in order:
   - Option A: SCWRL4 (fast, preferred) — check `which scwrl4` or `module avail`
   - Option B: Rosetta fixbb — check `which rosetta_scripts`
   - Option C: PDBFixer in env-classical — `from pdbfixer import PDBFixer`
   - Option D: MDAnalysis-based reconstruction
3. **Measure SG-SG:** For each conformation, for all 4 SS bonds
4. **Cutoffs:** Primary 2.5 A, sensitivity at 2.8, 3.0, 3.5 A
5. **AK3 threshold:** <80% integrity triggers drop recommendation
6. **Compare:** CB-CB proxy (Phase 0) vs SG-SG (this task)
7. **CPU-only job.** No GPU needed. SCWRL4 takes ~1 sec/structure.

---

## What You Write

| Artifact | Path | Description |
|----------|------|-------------|
| Recon script | `../../output/scripts/hewl_sidechain_recon.py` | Reconstruction + measurement |
| Full-atom PDBs | `../../output/task-005-hewl-full-atom/` | Reconstructed structures |
| Distance CSV | `../../output/task-005-hewl-sgsg-distances.csv` | All SG-SG measurements |
| Integrity report | `../../output/task-005-hewl-integrity-report.md` | Results + recommendation |
| Cross-agent note | `../../../../../shared/notes/1.1-hewl-sgsg.md` | HEWL decision for other tracks |
| Status report | `../../status/task-005-status.md` | Task status |

---

## Verification

1. [ ] >=95 conformations have sidechains reconstructed
2. [ ] `grep ' SG ' conf_001.pdb` shows 8 SG atoms (8 Cys residues)
3. [ ] Distance CSV has ~400 rows (4 bonds x ~100 conformations)
4. [ ] Integrity report has comparison table and clear keep/drop recommendation
5. [ ] Cross-agent note written with urgency: important
6. [ ] Status report written

---

## If Something Goes Wrong

1. If no sidechain tool available: document what was tried, write `blocked` status
2. If reconstruction fails on some conformations: report partial results
3. Even "can't reconstruct reliably" is a useful finding — document it
4. The HEWL decision can be deferred if blocked, but make every effort to resolve it
