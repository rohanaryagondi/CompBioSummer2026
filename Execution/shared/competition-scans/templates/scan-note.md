---
author: "competition-scanner (monthly)"
subphase: "<N.M at scan time>"
date: <YYYY-MM-DD>
affected_tracks: [alpha-m, gamma, delta, combined]
urgency: <info | important | critical>  # info if no hits, important if candidate hits, critical if S5 triggered
scan_month: <YYYY-MM>
---

# Monthly Competition Scan -- <YYYY-MM>

## Summary

- Date range scanned: **<YYYY-MM-DD> to <YYYY-MM-DD>**
- Total hits across all 4 searches: **<N>**
  - Search 1 (BioEmu + fitness/mutation): <N> hit(s)
  - Search 2 (MLFF + protein + benchmark + NMR): <N> hit(s)
  - Search 3 (Tahoe-100M + benchmark): <N> hit(s)
  - Search 4 (Force field + fitness prediction): <N> hit(s)
- Overall verdict: **<No competitors detected | Hits present -- classify below>**

## Hits

### Search 1: BioEmu + fitness/mutation

Google Scholar (manual review): <URL>

<ranked list; "No API hits." if empty>

### Search 2: MLFF + protein + benchmark + NMR

Google Scholar (manual review): <URL>

<ranked list>

### Search 3: Tahoe-100M + benchmark

Google Scholar (manual review): <URL>

<ranked list>

### Search 4: Force field + fitness prediction

Google Scholar (manual review): <URL>

<ranked list>

## Relevance assessment

<For each hit, judgement: NOT RELEVANT | POTENTIALLY OVERLAPPING | DIRECT COMPETITOR.
If no hits, state "No hits to assess.">

## Recommended actions

- **Search 1 (BioEmu + fitness/mutation):** If DIRECT COMPETITOR: accelerate Gamma preprint by 4 weeks (write `shared/help-needed/competition-bioemu-scoop.md`).
- **Search 2 (MLFF + protein + benchmark + NMR):** If DIRECT COMPETITOR: evaluate overlap with Alpha-M (write cross-agent note to `shared/notes/`).
- **Search 3 (Tahoe-100M + benchmark):** If DIRECT COMPETITOR: accelerate Delta preprint (write `shared/help-needed/competition-tahoe-scoop.md`).
- **Search 4 (Force field + fitness prediction):** If DIRECT COMPETITOR: TRIGGERS S5 (combined-paper separation) -- write `shared/help-needed/competition-s5-trigger.md`.

## Scripts used

```
python shared/competition-scans/scripts/monthly_scan.py --output shared/competition-scans/<YYYY-MM>-scan.md
```
