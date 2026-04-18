---
last_updated: 2026-04-17
updated_by: subagent-c
---

# Decisions Needed

## Active

| # | Decision | Urgency | Deadline | Options | Impact of Delay |
|---|----------|---------|----------|---------|-----------------|
| 1 | Phase 2 MACE scope revision after empirical throughput 8.7× slower than projected | HIGH | Before Sub 1.2 MACE task spec | (1) reduce to 2-3 Tier A × 3-5 ns; (2) OpenMM CUDA 12.4+ rebuild; (3) SO3LR-primary; (4) implicit-solvent MACE pilot | Blocks Sub 1.2 MACE task specification. Every week = 1 week of Phase 2 production lost. D2 (June 30) criterion G1 at risk regardless of choice except Option 3 (SO3LR vacuum path only). |

See `shared/help-needed/sub-1.2-phase2-mlff-scope.md` for full analysis and recommendation.

<!--
OpenMM rebuild placeholder resolved 2026-04-17: Subagent A verdict REJECT
(see `shared/notes/1.1-mace-phase2-feasibility.md` §5 — OpenCL + hybrid mode
covers Phase 2 scope within revised 1.40× budget; rebuild not worth the
effort/risk). No decision surfaced here.
-->

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
