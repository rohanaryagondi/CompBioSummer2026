---
requesting_agent: "head-1.1 (via documentation-fixer SubAgent)"
subphase: "1.1"
date: 2026-04-17
blocked_tasks: []
urgency: info
---

# Help Needed: HPr 15N Relaxation S2 Reference Cannot Be Verified

## Problem Description

The Alpha-M benchmark manifest cites `van Nuland et al., 1995, JMB 246:180` as
the S2 source for HPr (PDB 1HDN). The verification audit (2026-04-17) and
subsequent direct PubMed verification (PMID 7853396) confirm that this paper
is a structure-determination paper based on NOE distance restraints; it
contains NO 15N T1/T2/NOE relaxation data and NO derived S2 order parameters.
The citation is incorrect.

A targeted literature and BMRB search found no deposited T1/T2/NOE data or
S2 values for E. coli or B. subtilis HPr in BMRB entries (50934, 18379,
17274, 17095, 4264, 2371 for E. coli; 4972, 932 for B. subtilis). PubMed
searches for "HPr" + relaxation + S2 / Lipari-Szabo did not return a
dedicated dynamics paper. The Implementation Plan's "Moderate quality, 65%
coverage" rating for HPr S2 may derive from the incorrect van Nuland 1995
citation.

## What Was Tried

1. **Attempt 1**: Direct WebFetch of PubMed 7853396 (van Nuland 1995 JMB).
   - **Result**: Confirmed structure paper, not dynamics. NO T1/T2/NOE/S2.
   - **Why it failed**: The citation in the manifest was itself wrong.

2. **Attempt 2**: Google-search "HPr" + "15N relaxation" + "S2" / "order
   parameter" / "Lipari-Szabo" / "model-free" / "backbone dynamics".
   - **Result**: No dedicated HPr dynamics paper surfaced. Returned related
     proteins (glutaredoxin, adenylate kinase, glucose permease IIA domain)
     but not HPr itself.
   - **Why it failed**: Such a paper may not exist, or may be in a journal
     not well-indexed by the search tools available (e.g., Mag Reson Chem,
     older JBNMR issues).

3. **Attempt 3**: Search BMRB instant-search for "HPr" — 8+ entries found but
   none with visible relaxation data (only chemical shifts + one kinetic rates).
   - **Why it failed**: No relaxation data appears to be publicly deposited
     for HPr.

## What Help Is Needed

PlannerAI or human decision on one of three options:

- **Option A — Retain HPr with S2 unverified caveat**. Keep HPr in the
  Alpha-M benchmark as a "structural + classical-MD + generative comparison
  only" protein, analogous to Crambin. Remove HPr from quantitative S2
  comparison. Document in methods as a known limitation.

- **Option B — Deeper literature search**. Human or librarian access to
  Web of Science, Google Scholar time-filtered search, or a manual review
  of JBNMR / Biochemistry / JMB 1995-2010 issues to locate any HPr
  15N-relaxation paper. Could also contact Klevit lab (University of
  Washington) who published HPr structures in the 1990s and may have
  relaxation data.

- **Option C — Drop HPr from Alpha-M entirely**. T5 count drops to 11
  (from 12 originally). Once the 4 new proteins (NTL9, ACBP, FKBP12, EnHD)
  are added by the concurrent agent, post-addition T5 count = 15, still
  comfortably above the T5 threshold of 12. This is the cleanest option
  if no S2 source can be verified.

## Recommendation

**Option A** is the minimal-disruption path. HPr's 85-residue size class
(between CspA at 70 aa and Barnase at 110 aa) adds size diversity to the
benchmark without making unfounded S2 claims. This preserves stability and
classical-MD comparisons while being honest about the missing S2 reference.

## Impact Assessment

| Item | Detail |
|------|--------|
| Blocked tasks | None. This is a documentation / analysis-planning issue. |
| Timeline impact | None if Option A chosen. ~1 week if Option B requires a literature survey. |
| Gate at risk | D2 (Jun 30) Alpha-M pilot — marginal. S2 coverage may be ~7% less if HPr removed from S2 pool. T5 (>= 12 proteins) NOT at risk due to the 4 concurrent additions. |
| Workaround available | yes — Option A (retain as stability-only) is straightforward. |

## Resolution Log

| Date | Action | By | Status |
|------|--------|----|--------|
| 2026-04-17 | Escalation raised by documentation-fixer SubAgent | documentation-fixer | ongoing |
| 2026-04-17 | Option A chosen by user; manifest updated (non-S2); methods-section caveat written by Subagent D | planner + subagent-c | RESOLVED |
