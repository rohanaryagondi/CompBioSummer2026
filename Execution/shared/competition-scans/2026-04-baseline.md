---
author: "competition-scanner (baseline, Subagent E)"
subphase: "1.1"
date: 2026-04-17
affected_tracks: [alpha-m, gamma, delta, combined]
urgency: important
scan_month: 2026-04
---

# Monthly Competition Scan -- 2026-04 (Baseline)

This is the **baseline** scan (project start). It doubles as a proof-of-concept for
the infrastructure built per IP Section 7.3. Window scanned: 2026-04-01 to 2026-04-17
(17 days). Monthly scans proper begin 2026-06-01.

## Summary

- Date range scanned: **2026-04-01 to 2026-04-17**
- bioRxiv corpus fetched in window: 3364 preprints (full API pagination succeeded).
- PubMed window: 2026-01-01 to 2026-04-17 (widened since PubMed indexes slowly).
- arXiv window: 2026-04-01 to 2026-04-17 (no results across all 4 queries).
- Tools used: `monthly_scan.py` (bioRxiv + arXiv), `mcp__claude_ai_PubMed__search_articles`,
  `mcp__claude_ai_PubMed__get_article_metadata`, WebFetch (arXiv confirmation).

| # | Search | bioRxiv hits | arXiv hits | PubMed hits | Verdict |
|---|--------|--------------|------------|-------------|---------|
| 1 | BioEmu + fitness/mutation | 1 | 0 | 3 (2 unique works) | POTENTIALLY OVERLAPPING |
| 2 | MLFF + protein + benchmark + NMR | 0 | 0 | 0 | NOT DETECTED |
| 3 | Tahoe-100M + benchmark | 0 | 0 | 0 | NOT DETECTED |
| 4 | Force field + fitness prediction | 0 | 0 | 0 | NOT DETECTED |

- Overall verdict: **One tangentially related BioEmu paper cluster (cryptic pocket
  thermodynamics benchmark) plus one BioEmu capability assessment. Neither is a
  direct Gamma competitor. No competitor for Alpha-M, Delta, or combined-paper
  scope.**

## Hits

### Search 1: BioEmu + fitness/mutation

Google Scholar (manual review): <https://scholar.google.com/scholar?q=%22BioEmu%22+%28%22fitness%22+OR+%22mutation%22%29&as_ylo=2026&as_yhi=2026&hl=en>

**Hit 1.A (bioRxiv preprint + JCTC journal version -- same work).** Attribution: PubMed.

- **Title:** *How Well Can AI and Physics-Based Simulations Predict the Probability a Cryptic Pocket Is Open?*
- **Authors:** Zhang, S.; Miller, J. J.; Bowman, G. R. (U. Pennsylvania Biochemistry & Biophysics)
- **Dates:** bioRxiv 2026-04-01 (PMID 41648445); J. Chem. Theory Comput. 2026-04-07 (PMID 41945898)
- **DOIs:**
  - bioRxiv: [10.64898/2026.01.21.700870](https://doi.org/10.64898/2026.01.21.700870)
  - JCTC: [10.1021/acs.jctc.6c00135](https://doi.org/10.1021/acs.jctc.6c00135)
- **What it does:** Benchmarks AlphaFlow, BioEmu, PocketMiner, CryptoBank, and
  physics-based MD against experimentally characterized cryptic pockets in Ebola
  VP35 and TEM beta-lactamase. Evaluates whether methods predict the direction of
  point-mutation effects on cryptic-pocket opening probability and the absolute
  probability of opening.
- **Key findings (from abstract):** Multiple methods "remarkably successful" at
  predicting mutation direction. None reliably predicts absolute opening probability.
  MD is close for wild types; methods struggle for pockets <1% open experimentally.
  BioEmu captures trends for variants with populations >1% but has systematic errors.

**Hit 1.B.** Attribution: PubMed.

- **Title:** *Assessing the Performance of BioEmu in Understanding Protein Dynamics*
- **Authors:** Zha, J.; Li, N.; Li, M.; Liu, X.; Zhu, R.; Feng, L.; Lu, X.; Zhang, J.
  (Shanghai Jiao Tong U. School of Medicine)
- **Date:** Int. J. Mol. Sci. 2026-03-23 (PMID 41898756)
- **DOI:** [10.3390/ijms27062896](https://doi.org/10.3390/ijms27062896)
- **What it does:** Tests BioEmu on multiple protein-dynamics tasks: residue
  flexibility, motion correlations, local contacts, mutation-induced distribution
  shifts, Boltzmann-weighting, and ensemble docking.
- **Key findings (from abstract):** BioEmu reproduces flexibility, correlations,
  and local contacts. **It FAILS to predict a mutation-induced shift in
  conformational distribution** and shows preference for higher-energy conformations
  in some cases ("does not reproduce a right Boltzmann-weighted ensemble"). Only
  limited improvement in ensemble docking.

### Search 2: MLFF + protein + benchmark + NMR

Google Scholar (manual review): <https://scholar.google.com/scholar?q=%22MLFF%22+%22protein%22+%22benchmark%22+%22NMR%22&as_ylo=2026&as_yhi=2026&hl=en>

_No API hits (bioRxiv 0, arXiv 0, PubMed 0)._

### Search 3: Tahoe-100M + benchmark

Google Scholar (manual review): <https://scholar.google.com/scholar?q=%22Tahoe-100M%22+benchmark&as_ylo=2026&as_yhi=2026&hl=en>

_No API hits (bioRxiv 0, arXiv 0, PubMed 0)._

### Search 4: Force field + fitness prediction

Google Scholar (manual review): <https://scholar.google.com/scholar?q=%22force+field%22+%22fitness+prediction%22&as_ylo=2026&as_yhi=2026&hl=en>

_No API hits (bioRxiv 0, arXiv 0, PubMed 0)._

## Relevance assessment

- **Hit 1.A (Zhang/Bowman JCTC/bioRxiv):** **POTENTIALLY OVERLAPPING (low risk).**
  This paper benchmarks BioEmu for *cryptic pocket opening thermodynamics* and
  mutation-directional prediction on **2 proteins (Ebola VP35, TEM beta-lactamase)**.
  Gamma's scope is **fitness prediction from BioEmu ensembles across 150+
  ProteinGym proteins with a Boltz-2 ablation**. Scope and task differ (cryptic
  pocket probability vs. DMS fitness landscapes; 2 vs 150+ proteins). No scoop
  risk; this work actually strengthens motivation for Gamma (shows BioEmu has
  both strengths and failure modes that a fitness-scale benchmark can quantify).

- **Hit 1.B (Zha et al. IJMS):** **POTENTIALLY OVERLAPPING (monitor).** A BioEmu
  assessment paper that explicitly reports BioEmu **fails** at mutation-induced
  distribution shift. This is adjacent to Gamma's question ("can BioEmu predict
  fitness, which is mutation-driven?"). Two interpretations:
  1. Confirms our motivating hypothesis that single-point-mutation BioEmu
     fitness prediction is an open problem -- Gamma's contribution is intact.
  2. A reviewer may cite this to argue BioEmu cannot predict fitness at all.
  Action: read the full paper in Subphase 1.1 and cite it in Gamma's related-work.

- **Search 2-4 hits:** None detected -- baseline clear for Alpha-M, Delta, combined paper.

## Recommended actions

- **Search 1:** **No escalation.** Zhang/Bowman is tangential (cryptic pockets,
  n=2 proteins). Zha et al. is assessment, not fitness-prediction. Gamma team should:
  - Read both papers fully during Phase 1 (Subphase 1.1 or 1.2).
  - Add both to Gamma's related-work and frame as motivation, not scoop.
  - Watch for follow-on work from either group in subsequent monthly scans.
- **Search 2:** No action. Alpha-M MLFF+NMR benchmarking niche remains uncontested.
- **Search 3:** No action. Tahoe-100M benchmarking remains open for Delta.
- **Search 4:** No action. S5 trigger not activated.

## Operational notes (baseline run)

- bioRxiv API pagination required a longer timeout (raised to 60 s in-script) to
  fetch all 3364 records at cursor 0 - 3300 in ~6 minutes.
- arXiv API confirmed zero results across all four queries via independent
  WebFetch calls -- no need to retry.
- PubMed MCP experienced one transient "session terminated" error; a direct
  re-invocation succeeded. This is a known MCP idiosyncrasy, not a scan bug.
- Google Scholar URLs emitted; no manual scholar review performed for baseline
  (will be performed starting 2026-06 when monthly scans go live). URL format
  verified to load Scholar with the right year filter and query.

## Scripts used

```
python shared/competition-scans/scripts/monthly_scan.py \
    --start 2026-04-01 --end 2026-04-17 \
    --output shared/competition-scans/2026-04-baseline.md

# Augmented interactively via:
#   mcp__claude_ai_PubMed__search_articles  (x4)
#   mcp__claude_ai_PubMed__get_article_metadata  (PMIDs 41945898, 41898756, 41648445)
#   WebFetch (arXiv API, 4 queries)  -- all returned zero entries.
```
