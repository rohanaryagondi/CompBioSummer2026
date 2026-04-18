#!/usr/bin/env python3
"""
Analyze the 5 BioEmu sanity-check outputs (task-007):
  - NTL9, ACBP, FKBP12, EnHD: pass-rate only (expected >=80% for globular)
  - Crambin: pass-rate + SS-SS integrity (3 disulfides)

Emits: task-007-summary.json with per-protein metrics.
"""

import json
import subprocess
import sys
from pathlib import Path

OUTPUT_BASE = Path("/home/rag88/projects/CompBioSummer2026/Execution/"
                   "phases/phase-1/subphase-1.1/output")

TARGETS = ["ntl9", "acbp", "fkbp12", "enhd", "crambin"]


def summarize_generation(short_name):
    d = OUTPUT_BASE / f"task-007-{short_name}"
    gen_status = d / "generation_status.json"
    if not gen_status.exists():
        return dict(short_name=short_name, status="missing",
                    error=f"{gen_status} does not exist")
    with open(gen_status) as f:
        g = json.load(f)
    out = dict(
        short_name=short_name,
        sequence_length=g.get("sequence_length"),
        num_samples_requested=g.get("num_samples_requested"),
        status=g.get("status"),
        elapsed_minutes=g.get("elapsed_minutes"),
    )
    val = g.get("validation") or {}
    out["conformation_count"] = val.get("conformation_count")
    out["pass_rate"] = val.get("pass_rate")
    out["issues"] = val.get("issues", [])
    if g.get("error"):
        out["error"] = g["error"]
    return out


def main():
    summary = {}
    for t in TARGETS:
        summary[t] = summarize_generation(t)

    print("=" * 70)
    print("Task-007 BioEmu sanity-check summary")
    print("=" * 70)
    print(f"{'Protein':10s} {'Len':>4s} {'Samp':>5s} {'Pass':>6s} {'PassRate':>9s} {'Status':>12s} {'Elapsed':>8s}")
    for t in TARGETS:
        s = summary[t]
        passrate = f"{s.get('pass_rate', 0)*100:.1f}%" if s.get("pass_rate") is not None else "n/a"
        print(f"{t:10s} {s.get('sequence_length', '-'):>4} "
              f"{s.get('num_samples_requested', '-'):>5} "
              f"{s.get('conformation_count', '-'):>6} "
              f"{passrate:>9s} "
              f"{s.get('status', '?'):>12s} "
              f"{s.get('elapsed_minutes', '?'):>8}")

    # Thresholds
    print("\nVerdict (threshold: structured globular >=80% per 1.1-bioemu-passrates.md):")
    for t in TARGETS:
        s = summary[t]
        pr = s.get("pass_rate")
        if pr is None:
            v = "NO_DATA"
        elif t == "crambin":
            v = "RUN_SS_ANALYSIS"
        elif pr >= 0.80:
            v = "PASS"
        elif pr >= 0.50:
            v = "CONCERN"
        else:
            v = "FAIL"
        s["verdict"] = v
        print(f"  {t}: {v}")

    out_path = OUTPUT_BASE / "task-007-summary.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary JSON: {out_path}")

    # For crambin, run SS analysis if samples.xtc exists
    cram_xtc = OUTPUT_BASE / "task-007-crambin" / "samples.xtc"
    if cram_xtc.exists():
        print("\nRunning Crambin SS-SS integrity analysis...")
        ret = subprocess.run(
            ["python", str(OUTPUT_BASE / "scripts" / "task007_crambin_ss.py")],
            capture_output=True, text=True,
        )
        print(ret.stdout[-3000:] if len(ret.stdout) > 3000 else ret.stdout)
        if ret.returncode != 0:
            print("SS analysis stderr:")
            print(ret.stderr[-2000:])
    else:
        print(f"\nCrambin samples.xtc not yet available at {cram_xtc}")


if __name__ == '__main__':
    main()
