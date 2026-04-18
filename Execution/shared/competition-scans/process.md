---
author: "planner-ai (Subagent E)"
date: 2026-04-17
type: runbook
scope: competition monitoring (IP Section 7.3)
---

# Competition Scan Runbook

## When

- **1st of each month, June 2026 through November 2026 (inclusive)** -- six scans total.
- Run within the first 3 days of the month; do not skip months even if prior scan was empty.
- An extra ad-hoc scan may be triggered if a relevant paper is seen in the wild.

## Who

- Manual trigger by **PlannerAI or the human operator** (not automated).
- Rationale: hit classification (NOT RELEVANT / POTENTIALLY OVERLAPPING / DIRECT COMPETITOR)
  requires judgment about scope and novelty; automation would produce false positives and
  waste escalation cycles.

## How

1. Update the current subphase field at the top of the template for this month:
   ```
   cd /home/rag88/projects/CompBioSummer2026/Execution
   ```
2. Run the scan script (produces markdown populated from bioRxiv + arXiv APIs):
   ```
   python shared/competition-scans/scripts/monthly_scan.py \
     --output shared/competition-scans/$(date +%Y-%m)-scan.md
   ```
   For a specific window:
   ```
   python shared/competition-scans/scripts/monthly_scan.py \
     --start 2026-06-01 --end 2026-06-30 \
     --output shared/competition-scans/2026-06-scan.md
   ```
3. Open each of the 4 Google Scholar URLs the script prints and skim the first 20
   results per search. Paste any competitor-relevant hits into the `## Hits`
   section under the matching search.
4. **Interactive MCP augmentation (optional but recommended):** if running inside an
   agent with `mcp__claude_ai_bioRxiv__search_preprints` or
   `mcp__claude_ai_PubMed__search_articles` available, re-run the four queries
   through those tools for redundancy and append any extra hits to the report.
5. Classify every hit as:
   - **NOT RELEVANT** -- different problem / domain / scope.
   - **POTENTIALLY OVERLAPPING** -- tangential but worth watching next month.
   - **DIRECT COMPETITOR** -- directly addresses our core claim on this track.
6. If any hit is **DIRECT COMPETITOR**, follow escalation per IP 7.3:
   - **BioEmu + fitness/mutation** -> write `shared/help-needed/competition-bioemu-scoop.md`,
     accelerate Gamma preprint planning by 4 weeks, notify PlannerAI.
   - **MLFF + protein + benchmark + NMR** -> write a cross-agent note to
     `shared/notes/<subphase>-mlff-competitor.md`, evaluate overlap with Alpha-M scope.
   - **Tahoe-100M + benchmark** -> write
     `shared/help-needed/competition-tahoe-scoop.md`, accelerate Delta preprint.
   - **Force field + fitness prediction** -> TRIGGERS S5 (combined-paper separation);
     write `shared/help-needed/competition-s5-trigger.md`, flag for D6 reassessment.
7. Commit the scan note to the repo as part of that month's activity.

## API failure handling

- **bioRxiv returns 5xx or times out:** the script logs a warning and continues with
  arXiv + Scholar only. Re-run the script later that day; if persistent, document in
  the scan note's `## Scripts used` section.
- **arXiv returns 503:** the script retries up to 3 times with 5s/10s/15s backoff. On
  persistent failure it logs and continues with remaining searches.
- **Google Scholar:** no API; the script emits URLs only. Manual review is required.
  If Scholar rate-limits the browser, use a different IP (e.g., VPN off) or wait.

## Output

- `shared/competition-scans/<YYYY-MM>-scan.md` is produced every month, even if no hits.
- Urgency in frontmatter: `info` (no hits), `important` (any candidate hits), `critical`
  (any DIRECT COMPETITOR + S5 trigger).

## Rollover / archival

At project end (after D7, ~Sept 15 2026): archive the entire
`shared/competition-scans/` directory to the publication supplement (e.g., Zenodo
record accompanying the preprint) so reviewers can audit the monitoring trail.
