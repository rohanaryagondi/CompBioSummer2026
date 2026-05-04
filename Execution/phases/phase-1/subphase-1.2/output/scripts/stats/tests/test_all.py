"""
test_all -- run every synthetic-data unit test for the stats pipeline.

Usage
-----
    python tests/test_all.py

Returns exit 0 iff every sub-test passes; 1 otherwise. Each sub-test is run
as a subprocess with the same Python interpreter that invoked ``test_all``.

Environment
-----------
Expects env-stats active (see README.md). Passes ``SKIP_JZS_TEST`` through
if set (useful for operator-driven validation runs without PyMC).
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

TESTS = [
    "test_friedman_nemenyi.py",
    "test_icc.py",
    "test_hierarchical_bootstrap.py",
    "test_truncation.py",
    "test_jzs_bf.py",  # last because it is the slowest
]


def main() -> int:
    results = {}
    t_total = time.time()
    for t in TESTS:
        path = os.path.join(HERE, t)
        t0 = time.time()
        print(f"\n===== RUNNING {t} =====")
        proc = subprocess.run(
            [sys.executable, path],
            cwd=HERE,
            env=os.environ.copy(),
        )
        elapsed = time.time() - t0
        results[t] = (proc.returncode, elapsed)

    print("\n===== SUMMARY =====")
    all_ok = True
    for t, (code, elapsed) in results.items():
        tag = "PASS" if code == 0 else "FAIL"
        print(f"  {tag}  {t}  ({elapsed:.1f}s)")
        if code != 0:
            all_ok = False
    print(f"TOTAL elapsed: {time.time() - t_total:.1f}s")
    print("OVERALL:", "PASS" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
