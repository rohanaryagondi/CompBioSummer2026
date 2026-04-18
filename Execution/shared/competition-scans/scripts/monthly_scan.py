#!/usr/bin/env python3
"""
monthly_scan.py -- Competition scan for CompBioSummer2026 (IP Section 7.3).

Executes four scoped searches against bioRxiv + arXiv APIs and emits a Google
Scholar URL for the fourth manual-review category. Writes a markdown report
matching `templates/scan-note.md`.

Usage:
    python monthly_scan.py                       # last 30 days, prints to stdout
    python monthly_scan.py --dry-run             # run searches but do not write
    python monthly_scan.py --output scan.md      # write to file
    python monthly_scan.py --start 2026-04-01 --end 2026-04-30 --output out.md

Notes on sources (IP 7.3):
    1. "BioEmu" + "fitness" / "mutation"     -> bioRxiv + arXiv
    2. "MLFF" + "protein" + "benchmark" + "NMR" -> bioRxiv + arXiv
    3. "Tahoe-100M" + "benchmark"             -> bioRxiv + Google Scholar (manual)
    4. "force field" + "fitness prediction"   -> bioRxiv + arXiv

API failure modes and handling:
    - bioRxiv API: HTTP 5xx or timeout -> log warning, skip that source, continue.
    - arXiv API:   HTTP 503 (rate-limit) or timeout -> exponential-backoff retry
                   (up to 3 tries), then skip on persistent failure.
    - Google Scholar: no public API. A manual-click URL is emitted; the human
                      reviewer inspects results and records hits in the final note.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Callable


# ----------------------------------------------------------------------------
# Config (hardcoded from IP Section 7.3; do not change without updating the IP)
# ----------------------------------------------------------------------------

BIORXIV_DETAILS_URL = "https://api.biorxiv.org/details/biorxiv/{start}/{end}/0"
ARXIV_QUERY_URL = "http://export.arxiv.org/api/query"
SCHOLAR_SEARCH_URL = "https://scholar.google.com/scholar"

USER_AGENT = "CompBioSummer2026-competition-scan/1.0 (rag88@yale)"
HTTP_TIMEOUT_SECS = 60
ARXIV_MAX_RETRIES = 3
ARXIV_BACKOFF_BASE = 5  # seconds
BIORXIV_MAX_RETRIES = 2
BIORXIV_BACKOFF_BASE = 3

# Each search: (id, label, biorxiv_terms, arxiv_query, scholar_query, escalation)
SEARCHES: list[dict] = [
    {
        "id": 1,
        "label": "BioEmu + fitness/mutation",
        # For bioRxiv we use title+abstract keyword filtering below.
        "biorxiv_keywords": [
            ("bioemu", "fitness"),
            ("bioemu", "mutation"),
        ],
        "arxiv_query": 'all:"BioEmu" AND (all:fitness OR all:mutation)',
        "scholar_query": '"BioEmu" ("fitness" OR "mutation")',
        "escalation": (
            "If DIRECT COMPETITOR: accelerate Gamma preprint by 4 weeks "
            "(write shared/help-needed/competition-bioemu-scoop.md)"
        ),
    },
    {
        "id": 2,
        "label": "MLFF + protein + benchmark + NMR",
        "biorxiv_keywords": [("mlff", "protein", "nmr")],
        "arxiv_query": (
            '(all:"MLFF" OR all:"machine learning force field") '
            'AND all:protein AND all:benchmark AND all:NMR'
        ),
        "scholar_query": '"MLFF" "protein" "benchmark" "NMR"',
        "escalation": (
            "If DIRECT COMPETITOR: evaluate overlap with Alpha-M "
            "(write cross-agent note to shared/notes/)"
        ),
    },
    {
        "id": 3,
        "label": "Tahoe-100M + benchmark",
        "biorxiv_keywords": [("tahoe-100m",), ("tahoe 100m",)],
        "arxiv_query": '(all:"Tahoe-100M" OR all:"Tahoe 100M") AND all:benchmark',
        "scholar_query": '"Tahoe-100M" benchmark',
        "escalation": (
            "If DIRECT COMPETITOR: accelerate Delta preprint "
            "(write shared/help-needed/competition-tahoe-scoop.md)"
        ),
    },
    {
        "id": 4,
        "label": "Force field + fitness prediction",
        "biorxiv_keywords": [("force field", "fitness prediction")],
        "arxiv_query": 'all:"force field" AND all:"fitness prediction"',
        "scholar_query": '"force field" "fitness prediction"',
        "escalation": (
            "If DIRECT COMPETITOR: TRIGGERS S5 (combined-paper separation) "
            "-- write shared/help-needed/competition-s5-trigger.md"
        ),
    },
]


# ----------------------------------------------------------------------------
# Data types
# ----------------------------------------------------------------------------


@dataclass
class Hit:
    title: str
    authors: str
    date: str
    doi_or_url: str
    abstract_snippet: str
    source: str  # "biorxiv" | "arxiv"

    def to_markdown(self) -> str:
        snippet = (self.abstract_snippet or "").replace("\n", " ").strip()
        if len(snippet) > 280:
            snippet = snippet[:277] + "..."
        return (
            f"- **{self.title.strip()}**  \n"
            f"  {self.authors} ({self.date}) [{self.source}]  \n"
            f"  <{self.doi_or_url}>  \n"
            f"  _{snippet}_"
        )


@dataclass
class SearchResult:
    search_id: int
    label: str
    hits: list[Hit] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    scholar_url: str = ""
    escalation: str = ""


# ----------------------------------------------------------------------------
# HTTP helpers
# ----------------------------------------------------------------------------


def http_get(url: str, timeout: int = HTTP_TIMEOUT_SECS) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def arxiv_get_with_retry(url: str) -> bytes | None:
    """arXiv rate-limits aggressively; retry with backoff on 503/timeout."""
    for attempt in range(1, ARXIV_MAX_RETRIES + 1):
        try:
            return http_get(url)
        except urllib.error.HTTPError as e:
            if e.code == 503 and attempt < ARXIV_MAX_RETRIES:
                sleep_s = ARXIV_BACKOFF_BASE * attempt
                print(
                    f"  [arxiv] HTTP 503 (try {attempt}); backing off {sleep_s}s",
                    file=sys.stderr,
                )
                time.sleep(sleep_s)
                continue
            print(f"  [arxiv] HTTPError {e.code}: {e}", file=sys.stderr)
            return None
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < ARXIV_MAX_RETRIES:
                sleep_s = ARXIV_BACKOFF_BASE * attempt
                print(
                    f"  [arxiv] network error (try {attempt}): {e}; "
                    f"backing off {sleep_s}s",
                    file=sys.stderr,
                )
                time.sleep(sleep_s)
                continue
            print(f"  [arxiv] persistent network failure: {e}", file=sys.stderr)
            return None
    return None


# ----------------------------------------------------------------------------
# bioRxiv
# ----------------------------------------------------------------------------


def _biorxiv_get_with_retry(url: str) -> bytes | None:
    last_exc: Exception | None = None
    for attempt in range(1, BIORXIV_MAX_RETRIES + 1):
        try:
            return http_get(url)
        except (urllib.error.URLError, TimeoutError, urllib.error.HTTPError) as e:
            last_exc = e
            if attempt < BIORXIV_MAX_RETRIES:
                time.sleep(BIORXIV_BACKOFF_BASE * attempt)
                continue
    if last_exc is not None:
        print(f"  [biorxiv] giving up after {BIORXIV_MAX_RETRIES} tries: {last_exc}",
              file=sys.stderr)
    return None


def fetch_biorxiv_range(start: dt.date, end: dt.date) -> tuple[list[dict], list[str]]:
    """Fetch all bioRxiv preprints in the date range.

    The bioRxiv details API paginates with /0, /100, /200 cursors.
    Returns (preprints, errors).
    """
    all_records: list[dict] = []
    errors: list[str] = []
    cursor = 0
    while True:
        url = (
            f"https://api.biorxiv.org/details/biorxiv/"
            f"{start.isoformat()}/{end.isoformat()}/{cursor}"
        )
        raw = _biorxiv_get_with_retry(url)
        if raw is None:
            errors.append(f"bioRxiv fetch failed at cursor {cursor} (after retries)")
            break
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as e:
            errors.append(f"bioRxiv JSON decode failed at cursor {cursor}: {e}")
            break
        collection = payload.get("collection", [])
        if not collection:
            break
        all_records.extend(collection)
        messages = payload.get("messages", [{}])
        count = int(messages[0].get("count", len(collection))) if messages else len(collection)
        total = int(messages[0].get("total", 0)) if messages else 0
        cursor += count
        if total and cursor >= total:
            break
        if count == 0:
            break
        # Safety cap: bioRxiv publishes ~200/day; a month ~6000; break if huge
        if cursor > 20000:
            errors.append(f"bioRxiv result cap (20000) hit; truncating")
            break
    return all_records, errors


def biorxiv_matches_keywords(record: dict, keyword_groups: list[tuple[str, ...]]) -> bool:
    """Return True if ANY keyword group matches (AND within group, OR across)."""
    haystack = (
        (record.get("title", "") or "")
        + " "
        + (record.get("abstract", "") or "")
    ).lower()
    for group in keyword_groups:
        if all(kw.lower() in haystack for kw in group):
            return True
    return False


def biorxiv_record_to_hit(rec: dict) -> Hit:
    doi = rec.get("doi", "")
    url = f"https://www.biorxiv.org/content/{doi}v{rec.get('version', '1')}" if doi else ""
    authors = rec.get("authors", "") or ""
    return Hit(
        title=rec.get("title", "(no title)"),
        authors=(authors[:200] + "...") if len(authors) > 200 else authors,
        date=rec.get("date", ""),
        doi_or_url=url or doi,
        abstract_snippet=rec.get("abstract", "") or "",
        source="biorxiv",
    )


# ----------------------------------------------------------------------------
# arXiv
# ----------------------------------------------------------------------------


ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def fetch_arxiv(query: str, start: dt.date, end: dt.date) -> tuple[list[Hit], list[str]]:
    """Fetch arXiv results matching `query`; filter by submittedDate range.

    arXiv `submittedDate` range syntax: submittedDate:[YYYYMMDD0000 TO YYYYMMDD2359]
    """
    errors: list[str] = []
    date_clause = (
        f"submittedDate:[{start.strftime('%Y%m%d')}0000 "
        f"TO {end.strftime('%Y%m%d')}2359]"
    )
    full_query = f"({query}) AND {date_clause}"
    params = {
        "search_query": full_query,
        "start": "0",
        "max_results": "50",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = f"{ARXIV_QUERY_URL}?{urllib.parse.urlencode(params)}"
    raw = arxiv_get_with_retry(url)
    if raw is None:
        errors.append(f"arXiv fetch failed for query: {query}")
        return [], errors

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        errors.append(f"arXiv XML parse failed: {e}")
        return [], errors

    hits: list[Hit] = []
    for entry in root.findall("atom:entry", ATOM_NS):
        title_el = entry.find("atom:title", ATOM_NS)
        summary_el = entry.find("atom:summary", ATOM_NS)
        pub_el = entry.find("atom:published", ATOM_NS)
        id_el = entry.find("atom:id", ATOM_NS)
        authors = [
            (a.find("atom:name", ATOM_NS).text or "").strip()
            for a in entry.findall("atom:author", ATOM_NS)
            if a.find("atom:name", ATOM_NS) is not None
        ]
        title = (title_el.text or "").strip() if title_el is not None else "(no title)"
        summary = (summary_el.text or "").strip() if summary_el is not None else ""
        pub = (pub_el.text or "")[:10] if pub_el is not None else ""
        arxiv_url = (id_el.text or "").strip() if id_el is not None else ""
        hits.append(
            Hit(
                title=title,
                authors=", ".join(authors),
                date=pub,
                doi_or_url=arxiv_url,
                abstract_snippet=summary,
                source="arxiv",
            )
        )
    return hits, errors


# ----------------------------------------------------------------------------
# Google Scholar URL builder (no scraping)
# ----------------------------------------------------------------------------


def scholar_url(query: str, start: dt.date, end: dt.date) -> str:
    params = {
        "q": query,
        "as_ylo": str(start.year),
        "as_yhi": str(end.year),
        "hl": "en",
    }
    return f"{SCHOLAR_SEARCH_URL}?{urllib.parse.urlencode(params)}"


# ----------------------------------------------------------------------------
# Main driver
# ----------------------------------------------------------------------------


def run_one_search(
    spec: dict,
    start: dt.date,
    end: dt.date,
    biorxiv_records: list[dict] | None,
    biorxiv_errors: list[str],
) -> SearchResult:
    result = SearchResult(
        search_id=spec["id"],
        label=spec["label"],
        escalation=spec["escalation"],
        scholar_url=scholar_url(spec["scholar_query"], start, end),
    )

    # bioRxiv: filter pre-fetched corpus by keyword groups
    if biorxiv_records is None:
        # fetch failed upstream
        if biorxiv_errors:
            result.errors.extend(biorxiv_errors)
    else:
        for rec in biorxiv_records:
            if biorxiv_matches_keywords(rec, spec["biorxiv_keywords"]):
                result.hits.append(biorxiv_record_to_hit(rec))

    # arXiv
    arxiv_hits, arxiv_errors = fetch_arxiv(spec["arxiv_query"], start, end)
    result.hits.extend(arxiv_hits)
    result.errors.extend(arxiv_errors)

    return result


def render_report(
    results: list[SearchResult],
    start: dt.date,
    end: dt.date,
    biorxiv_errors: list[str],
    invocation: str,
) -> str:
    scan_month = start.strftime("%Y-%m")
    today = dt.date.today().isoformat()
    total_hits = sum(len(r.hits) for r in results)

    # urgency heuristic: info unless a search returns hits
    urgency = "info" if total_hits == 0 else "important"

    lines: list[str] = []
    lines.append("---")
    lines.append('author: "competition-scanner (monthly)"')
    lines.append(f'subphase: "1.1"  # update to current subphase at scan time')
    lines.append(f"date: {today}")
    lines.append("affected_tracks: [alpha-m, gamma, delta, combined]")
    lines.append(f"urgency: {urgency}")
    lines.append(f"scan_month: {scan_month}")
    lines.append("---")
    lines.append("")
    lines.append(f"# Monthly Competition Scan -- {scan_month}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(
        f"- Date range scanned: **{start.isoformat()} to {end.isoformat()}**"
    )
    lines.append(f"- Total hits across all 4 searches: **{total_hits}**")
    for r in results:
        lines.append(
            f"  - Search {r.search_id} ({r.label}): {len(r.hits)} hit(s)"
            + (f"; {len(r.errors)} error(s)" if r.errors else "")
        )
    if biorxiv_errors:
        lines.append("")
        lines.append("**bioRxiv-level errors:**")
        for e in biorxiv_errors:
            lines.append(f"  - {e}")
    lines.append("")
    lines.append(
        "- Overall verdict: "
        + (
            "**No competitors detected.**"
            if total_hits == 0
            else "**Hits present -- classify below.**"
        )
    )
    lines.append("")

    # Hits sections
    lines.append("## Hits")
    lines.append("")
    for r in results:
        lines.append(f"### Search {r.search_id}: {r.label}")
        lines.append("")
        lines.append(f"Google Scholar (manual review): {r.scholar_url}")
        lines.append("")
        if not r.hits:
            lines.append("_No API hits._")
        else:
            for h in r.hits:
                lines.append(h.to_markdown())
        if r.errors:
            lines.append("")
            lines.append("**Errors:**")
            for e in r.errors:
                lines.append(f"  - {e}")
        lines.append("")

    lines.append("## Relevance assessment")
    lines.append("")
    if total_hits == 0:
        lines.append(
            "No hits to assess. Baseline: no competitors on any of the 4 monitored fronts."
        )
    else:
        lines.append(
            "Human reviewer: classify each hit as **NOT RELEVANT**, "
            "**POTENTIALLY OVERLAPPING**, or **DIRECT COMPETITOR**."
        )
        for r in results:
            if r.hits:
                lines.append("")
                lines.append(f"**Search {r.search_id} ({r.label}):**")
                for h in r.hits:
                    lines.append(f"- `{h.title[:80]}` -> _TBD by reviewer_")
    lines.append("")

    lines.append("## Recommended actions")
    lines.append("")
    for r in results:
        lines.append(f"- **Search {r.search_id} ({r.label}):** {r.escalation}")
    lines.append("")

    lines.append("## Scripts used")
    lines.append("")
    lines.append("```")
    lines.append(invocation)
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Monthly competition scan (IP Section 7.3)."
    )
    parser.add_argument("--start", help="Start date YYYY-MM-DD (default: 30 days ago)")
    parser.add_argument("--end", help="End date YYYY-MM-DD (default: today)")
    parser.add_argument("--output", help="Path to write markdown report")
    parser.add_argument("--dry-run", action="store_true", help="Do not write output")
    args = parser.parse_args()

    today = dt.date.today()
    end = dt.date.fromisoformat(args.end) if args.end else today
    start = (
        dt.date.fromisoformat(args.start)
        if args.start
        else end - dt.timedelta(days=30)
    )

    invocation = "python " + " ".join(sys.argv)
    print(f"[scan] range: {start} -> {end}", file=sys.stderr)

    # Fetch bioRxiv once for the whole range, then filter per search
    print("[scan] fetching bioRxiv corpus...", file=sys.stderr)
    biorxiv_records, biorxiv_errors = fetch_biorxiv_range(start, end)
    print(
        f"[scan] bioRxiv: {len(biorxiv_records)} records, "
        f"{len(biorxiv_errors)} errors",
        file=sys.stderr,
    )

    results: list[SearchResult] = []
    for spec in SEARCHES:
        print(f"[scan] search {spec['id']}: {spec['label']}", file=sys.stderr)
        r = run_one_search(
            spec,
            start,
            end,
            biorxiv_records if not (biorxiv_errors and not biorxiv_records) else None,
            biorxiv_errors,
        )
        results.append(r)
        # Be gentle with arXiv
        time.sleep(3)

    report = render_report(results, start, end, biorxiv_errors, invocation)

    if args.dry_run:
        print("[scan] --dry-run set; not writing output.", file=sys.stderr)
        print(report)
        return 0

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"[scan] wrote {args.output}", file=sys.stderr)
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
