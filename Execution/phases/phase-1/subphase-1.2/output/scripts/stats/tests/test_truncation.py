"""
test_truncation -- synthetic-data unit test for truncation.

Design
------
Three sub-tests, all using fake in-memory data (no mdtraj file I/O).

Sub-test A: compute_t_min on a mock trajectory-length dict.
    trajectories = {
        'ww':  {'mace': 10.0, 'so3lr': 8.0, 'amber': 25.0},
        'gb3': {'mace':  5.0, 'so3lr': 7.0, 'amber': 30.0},
    }
Expected: {'ww': 8.0, 'gb3': 5.0}.

Sub-test B: log_truncation_events writes a valid JSON file.
After writing, parse it back and verify:
- Top-level keys present: timestamp_utc, pipeline_version, t_min_per_protein_ns,
  per_trajectory.
- t_min_per_protein_ns matches the input (float-typed).
- per_trajectory entries preserve source_path, timestep_ps, frames_original,
  frames_kept.

Sub-test C: empty-dict edge case.
compute_t_min({'p1': {}}) returns an empty dict (no generators -> no T_min).
compute_t_min({}) returns an empty dict.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

from _util import _ensure_parent_on_path  # noqa: F401

from truncation import compute_t_min, log_truncation_events


def sub_test_A() -> bool:
    trajectories = {
        "ww":  {"mace": 10.0, "so3lr": 8.0, "amber": 25.0},
        "gb3": {"mace":  5.0, "so3lr": 7.0, "amber": 30.0},
    }
    t_min = compute_t_min(trajectories)
    expected = {"ww": 8.0, "gb3": 5.0}
    ok = t_min == expected
    print(f"[truncation/A] t_min={t_min}, expected={expected}, pass={ok}")
    return bool(ok)


def sub_test_B() -> bool:
    t_min = {"ww": 8.0, "gb3": 5.0}
    per_traj = {
        "ww": {
            "mace":  {"source_path": "/data/ww/mace.dcd",  "timestep_ps": 2.0, "frames_original": 5000, "frames_kept": 4000},
            "so3lr": {"source_path": "/data/ww/so3lr.dcd", "timestep_ps": 2.0, "frames_original": 4000, "frames_kept": 4000},
            "amber": {"source_path": "/data/ww/amber.dcd", "timestep_ps": 2.0, "frames_original": 12500, "frames_kept": 4000},
        },
        "gb3": {
            "mace":  {"source_path": "/data/gb3/mace.dcd",  "timestep_ps": 2.0, "frames_original": 2500, "frames_kept": 2500},
            "so3lr": {"source_path": "/data/gb3/so3lr.dcd", "timestep_ps": 2.0, "frames_original": 3500, "frames_kept": 2500},
            "amber": {"source_path": "/data/gb3/amber.dcd", "timestep_ps": 2.0, "frames_original": 15000, "frames_kept": 2500},
        },
    }
    with tempfile.TemporaryDirectory() as td:
        log_path = os.path.join(td, "t_min_log.json")
        out_path = log_truncation_events(t_min, per_traj, log_path, pipeline_version="0.1.0-test")
        exists = os.path.isfile(out_path)
        with open(out_path) as f:
            loaded = json.load(f)

    keys_present = all(
        k in loaded
        for k in ("timestamp_utc", "pipeline_version", "t_min_per_protein_ns", "per_trajectory")
    )
    tmin_ok = loaded["t_min_per_protein_ns"] == {"ww": 8.0, "gb3": 5.0}
    per_ok = (
        loaded["per_trajectory"]["ww"]["mace"]["source_path"] == "/data/ww/mace.dcd"
        and loaded["per_trajectory"]["gb3"]["amber"]["frames_kept"] == 2500
        and loaded["per_trajectory"]["gb3"]["amber"]["timestep_ps"] == 2.0
    )
    version_ok = loaded["pipeline_version"] == "0.1.0-test"
    ok = exists and keys_present and tmin_ok and per_ok and version_ok
    print(
        f"[truncation/B] exists={exists}, keys_present={keys_present}, "
        f"tmin_ok={tmin_ok}, per_ok={per_ok}, version_ok={version_ok}"
    )
    return bool(ok)


def sub_test_C() -> bool:
    ok1 = compute_t_min({"p1": {}}) == {}
    ok2 = compute_t_min({}) == {}
    ok = ok1 and ok2
    print(f"[truncation/C] empty-inner={ok1}, empty-top={ok2}, pass={ok}")
    return bool(ok)


def main() -> int:
    a = sub_test_A()
    b = sub_test_B()
    c = sub_test_C()
    print(f"[truncation] OVERALL: {'PASS' if (a and b and c) else 'FAIL'}")
    return 0 if (a and b and c) else 1


if __name__ == "__main__":
    sys.exit(main())
