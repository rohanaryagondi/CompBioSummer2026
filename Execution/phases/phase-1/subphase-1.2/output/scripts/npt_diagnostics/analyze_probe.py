#!/usr/bin/env python
"""
analyze_probe.py -- Summarize probe TSV output from test_I_inspect.

Usage:
  python analyze_probe.py <probe.tsv>

Prints:
  - first/last lines
  - max excursion across the whole run
  - max edge distance evolution
  - the LAST clean callback line (any_nan==0) and the FIRST any_nan==1 line if present
  - sudden box-vector changes (per-call delta)
  - sudden atom-bound changes (per-call delta)
"""
import sys
import csv

def main(path):
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    if not rows:
        print("No rows in probe TSV")
        return 1

    print(f"Probe rows: {len(rows)}")
    print(f"First call: {rows[0]['calls']}; Last call: {rows[-1]['calls']}")

    nan_rows = [r for r in rows if int(r['any_nan']) == 1]
    print(f"Rows with any_nan=1: {len(nan_rows)}")
    if nan_rows:
        print(f"  First NaN at call: {nan_rows[0]['calls']}")
        last_clean = next((r for r in reversed(rows[:rows.index(nan_rows[0])])), None)
        if last_clean:
            print(f"  Last clean call: {last_clean['calls']}")

    # Per-call deltas
    print("\n--- Box vector evolution ---")
    box_a_first = float(rows[0]['box_a'])
    box_a_last = float(rows[-1]['box_a'])
    print(f"  box_a: first={box_a_first:.3f}  last={box_a_last:.3f}  delta={box_a_last-box_a_first:+.3f}")

    # Find biggest single-step box change
    max_box_delta = 0.0
    max_box_idx = 0
    for i in range(1, len(rows)):
        d = abs(float(rows[i]['box_a']) - float(rows[i-1]['box_a']))
        if d > max_box_delta:
            max_box_delta = d
            max_box_idx = i
    if max_box_idx > 0:
        r = rows[max_box_idx]
        print(f"  Largest single-call box_a delta: {max_box_delta:.4f} at call {r['calls']}")
        print(f"    box_a: {rows[max_box_idx-1]['box_a']} -> {r['box_a']}")

    # Excursion analysis
    print("\n--- Atom excursions outside primary cell (Å) ---")
    for axis in ('exc_x', 'exc_y', 'exc_z'):
        max_exc = max(float(r[axis]) for r in rows)
        max_exc_idx = max(range(len(rows)), key=lambda i: float(rows[i][axis]))
        print(f"  {axis}: max={max_exc:.3f} at call {rows[max_exc_idx]['calls']}")

    # Edge distance analysis
    print("\n--- Neighbor list edge distances (Å) ---")
    max_edge = max(float(r['max_edge_dist']) for r in rows)
    max_edge_idx = max(range(len(rows)), key=lambda i: float(rows[i]['max_edge_dist']))
    print(f"  max_edge_dist: max={max_edge:.3f} at call {rows[max_edge_idx]['calls']}")

    max_pair = max(float(r['max_pair50']) for r in rows)
    max_pair_idx = max(range(len(rows)), key=lambda i: float(rows[i]['max_pair50']))
    print(f"  max_pair50:    max={max_pair:.3f} at call {rows[max_pair_idx]['calls']}")

    # Print last 8 rows (so we see the lead-up to a crash)
    print("\n--- Last 8 rows ---")
    cols = ['calls', 'box_a', 'pmin_x', 'pmax_x', 'exc_x', 'exc_y', 'exc_z',
            'max_pair50', 'max_edge_dist', 'fmax', 'any_nan']
    print('\t'.join(cols))
    for r in rows[-8:]:
        print('\t'.join(r.get(c, '?') for c in cols))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
