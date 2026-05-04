#!/usr/bin/env python
"""Pre-compute Cα RMSF features for BioEmu batch 1 ensembles.

For each protein in /nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch1/:
  - load samples.xtc + topology.pdb
  - keep only physical conformations (already filtered by BioEmu v1.1)
  - align CA to first frame, compute per-residue Cα RMSF
  - write per-protein NPZ + CSV
  - aggregate into long-format batch1_rmsf.csv

Skip proteins flagged as 'dropped' in generation_status.json (e.g., YAP1).
Skip proteins with conformation_count < 100 (cannot compute meaningful RMSF).

Run: PYTHONNOUSERSITE=1 /home/rag88/.conda/envs/env-analysis/bin/python compute_rmsf_batch1.py
Pure CPU, login-node OK. ~1s/protein for typical sizes.

Output:
  output/features/<UNIPROT>_rmsf.npz       (per-residue RMSF + summary)
  output/features/<UNIPROT>_rmsf.csv       (per-residue table, easy join)
  output/features/batch1_rmsf.csv          (aggregated long-format)
  output/features/batch1_rmsf_summary.csv  (one row per protein: mean, max, median, etc.)
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
import MDAnalysis as mda
from MDAnalysis.analysis import align, rms

ENSEMBLE_ROOT = Path("/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch1")
OUT_DIR = Path("/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/features")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MIN_FRAMES = 100  # below this, RMSF is unreliable


def compute_rmsf(uni_id: str, prot_dir: Path) -> dict:
    """Compute Cα RMSF for a single protein. Returns status dict."""
    status = {
        "uniprot_id": uni_id,
        "ok": False,
        "n_frames": None,
        "n_residues": None,
        "rmsf_mean": None,
        "rmsf_median": None,
        "rmsf_max": None,
        "rmsf_min": None,
        "elapsed_seconds": None,
        "skip_reason": None,
    }

    # Honor generation_status.json drop flag
    gs_path = prot_dir / "generation_status.json"
    if gs_path.exists():
        try:
            gs = json.loads(gs_path.read_text())
            if gs.get("status") == "dropped":
                status["skip_reason"] = f"dropped:{gs.get('drop_reason', 'unknown')}"
                return status
            n_conf = gs.get("validation", {}).get("conformation_count")
            if n_conf is not None and n_conf < MIN_FRAMES:
                status["skip_reason"] = f"too_few_conformations:{n_conf}"
                return status
        except Exception as exc:
            status["skip_reason"] = f"bad_generation_status:{exc}"
            # don't return — still try the trajectory

    top = prot_dir / "topology.pdb"
    xtc = prot_dir / "samples.xtc"
    if not top.exists() or not xtc.exists():
        status["skip_reason"] = f"missing_inputs:topology={top.exists()},xtc={xtc.exists()}"
        return status

    t0 = time.time()
    try:
        u = mda.Universe(str(top), str(xtc), in_memory=True)
    except Exception as exc:
        status["skip_reason"] = f"load_failed:{exc}"
        return status

    n_frames = u.trajectory.n_frames
    ca = u.select_atoms("name CA")
    n_res = ca.residues.n_residues
    status["n_frames"] = n_frames
    status["n_residues"] = n_res

    if n_frames < MIN_FRAMES:
        status["skip_reason"] = f"too_few_frames:{n_frames}"
        return status
    if n_res < 5:
        status["skip_reason"] = f"too_few_residues:{n_res}"
        return status

    try:
        # Align all frames to frame 0 on CA atoms (in-place since in_memory=True)
        align.AlignTraj(u, u, select="name CA", in_memory=True, ref_frame=0).run()
        # Per-residue Cα RMSF in Angstrom
        R = rms.RMSF(ca).run()
        rmsf = np.asarray(R.results.rmsf, dtype=np.float64)
    except Exception as exc:
        status["skip_reason"] = f"rmsf_failed:{exc}"
        return status

    elapsed = time.time() - t0

    resids = np.asarray(ca.residues.resids, dtype=np.int64)
    resnames = np.asarray(ca.residues.resnames, dtype="<U3")

    # Save NPZ
    npz_path = OUT_DIR / f"{uni_id}_rmsf.npz"
    np.savez(
        npz_path,
        uniprot_id=uni_id,
        resid=resids,
        resname=resnames,
        rmsf_ca_angstrom=rmsf,
        n_frames=n_frames,
    )

    # Save CSV
    csv_path = OUT_DIR / f"{uni_id}_rmsf.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["uniprot_id", "residue_idx_0based", "resid", "resname", "rmsf_ca_angstrom", "n_frames"])
        for i, (rid, rname, val) in enumerate(zip(resids, resnames, rmsf)):
            w.writerow([uni_id, i, int(rid), str(rname), f"{val:.6f}", n_frames])

    status["ok"] = True
    status["rmsf_mean"] = float(rmsf.mean())
    status["rmsf_median"] = float(np.median(rmsf))
    status["rmsf_max"] = float(rmsf.max())
    status["rmsf_min"] = float(rmsf.min())
    status["elapsed_seconds"] = round(elapsed, 2)
    return status


def main() -> int:
    proteins = sorted(p.name for p in ENSEMBLE_ROOT.iterdir() if p.is_dir() and p.name != "logs")
    print(f"[rmsf] {len(proteins)} candidate protein dirs", flush=True)

    results = []
    long_rows = []
    for i, uni in enumerate(proteins, 1):
        prot_dir = ENSEMBLE_ROOT / uni
        st = compute_rmsf(uni, prot_dir)
        tag = "OK " if st["ok"] else "SKIP"
        msg = f"  rmsf={st['rmsf_mean']:.2f} med={st['rmsf_median']:.2f} max={st['rmsf_max']:.2f}" if st["ok"] else f"  reason={st['skip_reason']}"
        nf = st["n_frames"] if st["n_frames"] is not None else "-"
        nr = st["n_residues"] if st["n_residues"] is not None else "-"
        print(f"[rmsf] {i:>2}/{len(proteins)} {tag} {uni:<22} frames={nf:<5} residues={nr:<5}{msg}", flush=True)
        results.append(st)

        if st["ok"]:
            # rebuild long rows from per-protein csv (avoid double-load)
            csv_path = OUT_DIR / f"{uni}_rmsf.csv"
            with csv_path.open() as f:
                r = csv.DictReader(f)
                for row in r:
                    long_rows.append(row)

    # Aggregated long-format CSV
    long_csv = OUT_DIR / "batch1_rmsf.csv"
    with long_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["uniprot_id", "residue_idx_0based", "resid", "resname", "rmsf_ca_angstrom", "n_frames"])
        for row in long_rows:
            w.writerow([row["uniprot_id"], row["residue_idx_0based"], row["resid"], row["resname"], row["rmsf_ca_angstrom"], row["n_frames"]])

    # Per-protein summary
    sum_csv = OUT_DIR / "batch1_rmsf_summary.csv"
    with sum_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["uniprot_id", "ok", "n_frames", "n_residues", "rmsf_mean", "rmsf_median", "rmsf_max", "rmsf_min", "elapsed_seconds", "skip_reason"])
        for st in results:
            w.writerow([
                st["uniprot_id"],
                int(st["ok"]),
                st["n_frames"] if st["n_frames"] is not None else "",
                st["n_residues"] if st["n_residues"] is not None else "",
                "" if st["rmsf_mean"] is None else f"{st['rmsf_mean']:.6f}",
                "" if st["rmsf_median"] is None else f"{st['rmsf_median']:.6f}",
                "" if st["rmsf_max"] is None else f"{st['rmsf_max']:.6f}",
                "" if st["rmsf_min"] is None else f"{st['rmsf_min']:.6f}",
                "" if st["elapsed_seconds"] is None else st["elapsed_seconds"],
                st["skip_reason"] if st["skip_reason"] else "",
            ])

    n_ok = sum(1 for st in results if st["ok"])
    n_skip = len(results) - n_ok
    print(f"[rmsf] DONE: {n_ok}/{len(results)} ok, {n_skip} skipped", flush=True)
    print(f"[rmsf] outputs in {OUT_DIR}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
