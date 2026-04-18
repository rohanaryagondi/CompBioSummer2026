---
last_updated: 2026-04-18
updated_by: planner (post-audit cleanup — Phase 2 MACE scope resolved via Option 5)
---

# Decisions Needed

## Active

No pending decisions.

Phase 1.1 closed 2026-04-18 with all decisions resolved; see Resolved Decisions
table below. A fresh PlannerAI planning Sub 1.2 has no open decisions requiring
user input at handoff time.

---

## Template (populated when decisions arise)

| # | Decision | Urgency | Deadline | Options | Impact of Delay |
|---|----------|---------|----------|---------|-----------------|
| 1 | <description> | <low/med/high/critical> | <date> | <option A vs B> | <what happens if not decided by deadline> |

---

## Resolved Decisions

| # | Decision | Date | Resolution | Resolved By |
|---|----------|------|-----------|------------|
| 1 | HPr disposition (post-van-Nuland-1995-citation-invalidation) | 2026-04-17 | Option A: retain HPr for structural + stability comparison only; exclude from quantitative S2 analysis. Manifest updated (bmrb_quality = "None (S2 unavailable)", bmrb_s2_residue_count = 0). Help-needed doc closed. See `shared/help-needed/head-1.1-hpr-s2.md` and `shared/notes/1.1-hpr-s2-verification.md`. | user (Option A) + subagent-c (manifest implementation) |
| 2 | T4L WT S2 reference lock | 2026-04-17 | Primary reference locked to Mulder, Hon, Muhandiram, Dahlquist, Kay 2000 Biochemistry 39(41):12614-12622 (PMID 11027141, DOI 10.1021/bi001351t), which contains side-by-side WT + L99A backbone 15N T1/T2/NOE at 500 and 800 MHz, 298 K. Prior "Biochemistry 40:4458" citation was a transcription error for the same paper. Manifest updated; cavity-region caveat narrowed to within-paper stratification. See `shared/notes/1.1-t4l-s2-candidates.md`. | subagent-c (literature search + manifest) |
| 3 | Phase 2 MACE scope (empirical throughput 8.7× slower than projected) | 2026-04-18 | **Option 5 (H200 OpenCL) committed** as Phase 2 MACE primary path. Measured 2.11 ns/day on hybrid WW = 11.5× RTX 5000 Ada (SLURM 8789805). Options 2 (CUDA rebuild, 1.0× speedup — MACE is inference-bound) and 4 (implicit solvent, 1.07× speedup — water PME not the bottleneck) empirically REJECTED. Phase 2 compute budget revised 47,300 → ~3,300 GPU-hrs (releases ~44K to contingency). D2 criterion G1 achievable on H200. See `shared/help-needed/sub-1.2-phase2-mlff-scope.md` (resolved) and `shared/notes/1.1-mace-hybrid-validation.md` §9-11. | PlannerAI (empirical confirmation) + Subagent L (final CUDA investigation) |
