# Handoff Prompt for New Claude Code Session

Copy everything below the `---` line and paste it as the first message to a new Claude Code
session started from `/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2`.

---

You are resuming as **head-1.2**, the HeadAI for subphase 1.2. The prior overnight session (2026-05-01 → 2026-05-02) iterated on a MACE NPT bug and found a working fix.

Before responding, read these files in this order:

1. `handoff-notes.md` — START HERE. Complete state transfer including the MACE NPT fix, all 6 task statuses, and what remains.
2. `overnight-summary-2026-05-02.md` — focused log of the overnight Round 3 NPT iteration.
3. `CLAUDE.md` — your HeadAI persona, success criteria, failure handling.
4. `../../../shared/notes/1.2-mace-npt-fixed.md` — cross-agent note (urgency=critical) with full evidence chain for the MACE NPT fix.
5. `../../../shared/notes/1.2-mace-npt-stability.md` — historical NPT investigation, §7 RESOLUTION at the bottom.
6. `output/scripts/npt_diagnostics/test_L_hbonds.py` and `test_P_extended.py` — production recipe drivers.
7. `output/scripts/npt_diagnostics/npt_diag_common.py` — `add_protein_sentinel_bonds` and `add_protein_hbonds_constraints` (the two helpers that ARE the fix).
8. `output/osf-prereg-v3.md` — deposit-ready OSF document (NPT framing).
9. `../../../dashboards/master-status.md`, `active-subphase.md`, `gate-tracker.md`, `compute-budget.md` — current state.

Once you've read all of those, give me:

1. **One-paragraph summary of what happened overnight** — what was attempted, what worked, why.
2. **Sub 1.2 status** — task-by-task (all 6), with focus on what's blocking and what's done.
3. **What's left to close out Sub 1.2** — concrete remaining work items in priority order.
4. **MACE NPT detail** — the production recipe in plain English, the validation evidence, what's been confirmed vs what still needs to be verified in Sub 1.4. I'm particularly interested in this part — be specific about the recipe and how confident we should be in it for Sub 1.4 production.

Keep your summary tight. After that I'll tell you what to do next.
