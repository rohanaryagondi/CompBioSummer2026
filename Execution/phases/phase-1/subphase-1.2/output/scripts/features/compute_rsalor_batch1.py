#!/usr/bin/env python
"""Pre-compute RSALOR features for BioEmu batch 1 ensembles.

RSALOR (Tsishyn et al., Bioinformatics 2025) combines:
  - RSA (Relative Solvent Accessibility) — per-residue, derived from PDB structure
  - LOR (Log Odd Ratio) — per-mutation, derived from MSA conservation
  - Composite score: RSA * LOR (per-mutation)

For Sub 1.2 ML pipeline (Gamma central ablation: Model 4 RSALOR vs Model 5 RSALOR+RMSF),
we need PER-RESIDUE summaries of these quantities. This script computes:
  - rsa_relative      : per-residue RSA (Shrake-Rupley SASA / Tien 2013 max ASA)
  - rsa_absolute      : per-residue absolute SASA (A^2)
  - lor_mean_to_other : per-residue mean LOR for mutating WT -> 19 other AAs (REQUIRES MSA)
  - lor_max_to_other  : per-residue max LOR over 19 alternates (REQUIRES MSA)
  - rsalor_mean       : per-residue mean RSA*LOR (REQUIRES MSA)
  - rsalor_max        : per-residue max RSA*LOR (REQUIRES MSA)

DELIVERY MODE (this script supports two regimes):

  Mode RSA-ONLY (default if no --msa-dir provided):
    Compute RSA columns immediately. LOR/RSALOR columns written as NaN.
    This unblocks Gamma "Model 1: ESM2-650M + RSA" path while MSAs are
    being precached.

  Mode FULL (when --msa-dir <dir> provided AND rsalor>=1.1.x is installed):
    For each protein, look for <UNIPROT>.a3m or <UNIPROT>.fasta in the MSA
    directory; if present, run rsalor.MSA(...).get_scores() and aggregate
    per-mutation LOR/RSALOR to per-residue summaries. If MSA missing for a
    protein, that protein retains RSA-only output and is logged.

PREREQUISITES FOR MODE FULL (Sub 1.3 SubAgent action items):
  1. pip install rsalor in env-bioemu (PyPI: rsalor-1.1.9)
     (NOT installed at Sub 1.2 close — surfaced in status report.)
  2. Precache MSAs for the 47 batch 1 ProteinGym proteins. Canonical source:
     ProteinGym DMS_substitutions release on Hugging Face / Zenodo
     (https://github.com/OATML-Markslab/ProteinGym, MSA assets bundled with
     the supervised baselines tarball). a3m or FASTA aligned format.
     Naming: <UNIPROT_ID>.a3m so this script can find them.

Run:
  PYTHONNOUSERSITE=1 /home/rag88/.conda/envs/env-bioemu/bin/python \
      compute_rsalor_batch1.py [--msa-dir /path/to/msas]

Pure CPU, login-node OK. ~0.07 s/protein for SASA; LOR cost depends on MSA depth
(typically 0.5-5 s/protein single-thread for canonical ProteinGym MSAs).

Output:
  output/features/<UNIPROT>_rsalor.npz       (per-residue NPZ; NaN columns if RSA-only)
  output/features/<UNIPROT>_rsalor.csv       (per-residue CSV; NaN columns if RSA-only)
  output/features/batch1_rsalor.csv          (aggregated long-format)
  output/features/batch1_rsalor_summary.csv  (one row per protein: counts + means)
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
import warnings
from pathlib import Path

import numpy as np

# Biopython for SASA (Shrake-Rupley); rsalor optional and lazily imported.
warnings.filterwarnings("ignore")
from Bio.PDB import PDBParser
from Bio.PDB.SASA import ShrakeRupley

ENSEMBLE_ROOT = Path("/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch1")
OUT_DIR = Path("/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/features")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MIN_RESIDUES = 5

# Tien et al. 2013 (PLOS ONE) "theoretical" all-atom max ASA from GLY-X-GLY
# tripeptides. Standard reference for RSA normalization in RSALOR and beyond.
TIEN_MAX_ASA = {
    "ALA": 129.0, "ARG": 274.0, "ASN": 195.0, "ASP": 193.0, "CYS": 167.0,
    "GLN": 225.0, "GLU": 223.0, "GLY": 104.0, "HIS": 224.0, "ILE": 197.0,
    "LEU": 201.0, "LYS": 236.0, "MET": 224.0, "PHE": 240.0, "PRO": 159.0,
    "SER": 155.0, "THR": 172.0, "TRP": 285.0, "TYR": 263.0, "VAL": 174.0,
}

# 1-letter <-> 3-letter for cross-reference with rsalor outputs (FASTA-indexed).
THREE_TO_ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
    "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
    "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
    "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}

PER_RES_COLS = [
    "uniprot_id", "residue_idx_0based", "resid", "resname", "aa1",
    "rsa_absolute_a2", "rsa_relative",
    "lor_mean_to_other", "lor_max_to_other",
    "rsalor_mean", "rsalor_max",
    "n_msa_sequences",
]


def compute_rsa(uni_id: str, prot_dir: Path) -> dict:
    """Compute per-residue SASA + relative RSA from topology.pdb. No MSA needed."""
    status = {
        "uniprot_id": uni_id,
        "ok_rsa": False,
        "n_residues": None,
        "rsa_mean": None,
        "rsa_median": None,
        "skip_reason": None,
        "resids": None, "resnames": None, "aa1": None,
        "sasa_abs": None, "rsa_rel": None,
    }

    # Honor generation_status.json drop flag
    gs_path = prot_dir / "generation_status.json"
    if gs_path.exists():
        try:
            gs = json.loads(gs_path.read_text())
            if gs.get("status") == "dropped":
                status["skip_reason"] = f"dropped:{gs.get('drop_reason', 'unknown')}"
                return status
        except Exception as exc:
            status["skip_reason"] = f"bad_generation_status:{exc}"

    pdb = prot_dir / "topology.pdb"
    if not pdb.exists():
        status["skip_reason"] = "missing_topology_pdb"
        return status

    try:
        parser = PDBParser(QUIET=True)
        struct = parser.get_structure("p", str(pdb))
        sr = ShrakeRupley()
        sr.compute(struct, level="R")
    except Exception as exc:
        status["skip_reason"] = f"sasa_failed:{exc}"
        return status

    resids, resnames, aa1, sasa_abs, rsa_rel = [], [], [], [], []
    for chain in struct[0]:
        for res in chain:
            if res.id[0].strip():  # skip HETATM / waters
                continue
            rn = res.resname.upper()
            if rn not in TIEN_MAX_ASA:
                continue
            resids.append(int(res.id[1]))
            resnames.append(rn)
            aa1.append(THREE_TO_ONE[rn])
            abs_sasa = float(getattr(res, "sasa", float("nan")))
            sasa_abs.append(abs_sasa)
            rsa_rel.append(abs_sasa / TIEN_MAX_ASA[rn])

    if len(resids) < MIN_RESIDUES:
        status["skip_reason"] = f"too_few_residues:{len(resids)}"
        return status

    status["ok_rsa"] = True
    status["n_residues"] = len(resids)
    status["resids"] = np.asarray(resids, dtype=np.int64)
    status["resnames"] = np.asarray(resnames, dtype="<U3")
    status["aa1"] = np.asarray(aa1, dtype="<U1")
    status["sasa_abs"] = np.asarray(sasa_abs, dtype=np.float64)
    status["rsa_rel"] = np.asarray(rsa_rel, dtype=np.float64)
    status["rsa_mean"] = float(np.nanmean(rsa_rel))
    status["rsa_median"] = float(np.nanmedian(rsa_rel))
    return status


def compute_lor_from_msa(uni_id: str, prot_dir: Path, msa_dir: Path) -> dict:
    """Compute per-mutation LOR via rsalor package, then aggregate per-residue.

    Returns dict with same length-N arrays as compute_rsa for: lor_mean_to_other,
    lor_max_to_other, rsalor_mean, rsalor_max, n_msa_sequences.
    Returns ok_lor=False if MSA not found, rsalor not importable, or compute fails.
    """
    out = {
        "ok_lor": False,
        "n_msa_sequences": None,
        "lor_mean": None, "lor_max": None,
        "rsalor_mean": None, "rsalor_max": None,
        "skip_reason_lor": None,
    }
    # Locate MSA file
    msa_candidates = [
        msa_dir / f"{uni_id}.a3m",
        msa_dir / f"{uni_id}.fasta",
        msa_dir / f"{uni_id}.fa",
    ]
    msa_path = next((p for p in msa_candidates if p.exists()), None)
    if msa_path is None:
        out["skip_reason_lor"] = f"no_msa_in:{msa_dir}"
        return out

    try:
        from rsalor import MSA  # type: ignore
    except Exception as exc:
        out["skip_reason_lor"] = f"rsalor_import_failed:{exc}"
        return out

    pdb = prot_dir / "topology.pdb"
    try:
        msa = MSA(str(msa_path), str(pdb), "A", num_threads=1)
        scores = msa.get_scores()  # list of per-mutation dicts
    except Exception as exc:
        out["skip_reason_lor"] = f"rsalor_run_failed:{exc}"
        return out

    # Aggregate per-mutation -> per-residue
    # Each score row carries a position, WT AA, mutant AA, LOR, RSA*LOR.
    # Group by FASTA position, aggregate the 19 alternate-AA rows.
    by_pos: dict[int, dict[str, list[float]]] = {}
    for s in scores:
        # rsalor uses keys like "fasta_mutation": "M1A", or fields "position", "wt_aa", "mut_aa".
        # We accept several spellings to be robust.
        pos = s.get("position") or s.get("fasta_pos") or s.get("pos")
        wt = s.get("wt_aa") or s.get("wt")
        mut = s.get("mut_aa") or s.get("mut")
        lor = s.get("lor") or s.get("LOR")
        rl = s.get("rsalor") or s.get("RSALOR") or s.get("rsa_lor") or s.get("score")
        if pos is None or wt is None or mut is None or lor is None:
            continue
        if wt == mut:
            continue  # synonymous identity
        try:
            pos = int(pos)
            lor = float(lor)
            rl = float(rl) if rl is not None else float("nan")
        except Exception:
            continue
        d = by_pos.setdefault(pos, {"lor": [], "rsalor": []})
        d["lor"].append(lor)
        if not math.isnan(rl):
            d["rsalor"].append(rl)

    if not by_pos:
        out["skip_reason_lor"] = "rsalor_empty_scores"
        return out

    out["ok_lor"] = True
    out["by_pos"] = by_pos
    # MSA depth (rsalor exposes len(msa) or msa.n_sequences depending on version)
    n_seq = getattr(msa, "n_sequences", None) or getattr(msa, "num_sequences", None) or len(getattr(msa, "sequences", []) or [])
    out["n_msa_sequences"] = int(n_seq) if n_seq else None
    return out


def fuse(rsa: dict, lor: dict, uni_id: str) -> dict:
    """Combine RSA + LOR into final per-residue arrays. NaN-fills LOR side if missing."""
    n = rsa["n_residues"]
    lor_mean = np.full(n, np.nan, dtype=np.float64)
    lor_max = np.full(n, np.nan, dtype=np.float64)
    rl_mean = np.full(n, np.nan, dtype=np.float64)
    rl_max = np.full(n, np.nan, dtype=np.float64)

    if lor and lor.get("ok_lor"):
        # rsalor positions are 1-based FASTA index; our resids/aa1 are PDB-numbered.
        # We align by FASTA-1-based to per-residue array index (residue_idx_0based + 1).
        for i in range(n):
            fasta_pos = i + 1
            d = lor["by_pos"].get(fasta_pos)
            if not d:
                continue
            if d["lor"]:
                lor_mean[i] = float(np.mean(d["lor"]))
                lor_max[i] = float(np.max(d["lor"]))
            if d["rsalor"]:
                rl_mean[i] = float(np.mean(d["rsalor"]))
                rl_max[i] = float(np.max(d["rsalor"]))

    return {
        "uni_id": uni_id,
        "resids": rsa["resids"], "resnames": rsa["resnames"], "aa1": rsa["aa1"],
        "sasa_abs": rsa["sasa_abs"], "rsa_rel": rsa["rsa_rel"],
        "lor_mean": lor_mean, "lor_max": lor_max,
        "rsalor_mean": rl_mean, "rsalor_max": rl_max,
        "n_msa": (lor or {}).get("n_msa_sequences"),
    }


def write_per_protein(arr: dict) -> None:
    uni = arr["uni_id"]
    n = len(arr["resids"])
    n_msa = arr["n_msa"] if arr["n_msa"] is not None else 0

    npz_path = OUT_DIR / f"{uni}_rsalor.npz"
    np.savez(
        npz_path,
        uniprot_id=uni,
        resid=arr["resids"], resname=arr["resnames"], aa1=arr["aa1"],
        rsa_absolute_a2=arr["sasa_abs"], rsa_relative=arr["rsa_rel"],
        lor_mean_to_other=arr["lor_mean"], lor_max_to_other=arr["lor_max"],
        rsalor_mean=arr["rsalor_mean"], rsalor_max=arr["rsalor_max"],
        n_msa_sequences=n_msa,
    )

    csv_path = OUT_DIR / f"{uni}_rsalor.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(PER_RES_COLS)
        for i in range(n):
            w.writerow([
                uni, i, int(arr["resids"][i]), str(arr["resnames"][i]), str(arr["aa1"][i]),
                f"{arr['sasa_abs'][i]:.4f}", f"{arr['rsa_rel'][i]:.6f}",
                _fmt(arr["lor_mean"][i]), _fmt(arr["lor_max"][i]),
                _fmt(arr["rsalor_mean"][i]), _fmt(arr["rsalor_max"][i]),
                n_msa,
            ])


def _fmt(x: float) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return ""
    return f"{x:.6f}"


def main() -> int:
    ap = argparse.ArgumentParser(description="RSALOR per-residue features for BioEmu batch 1")
    ap.add_argument("--msa-dir", type=Path, default=None,
                    help="Directory with <UNIPROT>.a3m or .fasta MSAs. If omitted, run RSA-only mode.")
    ap.add_argument("--ensemble-root", type=Path, default=ENSEMBLE_ROOT)
    ap.add_argument("--limit", type=int, default=None,
                    help="Process only first N proteins (for smoke testing)")
    args = ap.parse_args()

    have_msa_dir = args.msa_dir is not None and args.msa_dir.exists()
    if args.msa_dir and not have_msa_dir:
        print(f"[rsalor] WARNING: --msa-dir {args.msa_dir} does not exist; falling back to RSA-only mode", flush=True)

    # rsalor importable?
    rsalor_ok = False
    if have_msa_dir:
        try:
            import rsalor  # noqa: F401
            rsalor_ok = True
        except Exception as exc:
            print(f"[rsalor] WARNING: rsalor package not importable ({exc}); falling back to RSA-only", flush=True)

    mode = "FULL" if (have_msa_dir and rsalor_ok) else "RSA-ONLY"
    print(f"[rsalor] mode={mode}; ensemble_root={args.ensemble_root}; out_dir={OUT_DIR}", flush=True)

    proteins = sorted(p.name for p in args.ensemble_root.iterdir() if p.is_dir() and p.name != "logs")
    if args.limit:
        proteins = proteins[: args.limit]
    print(f"[rsalor] {len(proteins)} candidate protein dirs", flush=True)

    summaries = []
    long_rows = []

    for i, uni in enumerate(proteins, 1):
        prot_dir = args.ensemble_root / uni
        t0 = time.time()
        rsa = compute_rsa(uni, prot_dir)

        if not rsa["ok_rsa"]:
            print(f"[rsalor] {i:>2}/{len(proteins)} SKIP {uni:<22} reason={rsa['skip_reason']}", flush=True)
            summaries.append({
                "uniprot_id": uni, "ok_rsa": False, "ok_lor": False,
                "n_residues": rsa["n_residues"], "n_msa": None,
                "rsa_mean": None, "rsa_median": None,
                "lor_mean_global": None, "rsalor_mean_global": None,
                "elapsed_seconds": round(time.time() - t0, 3),
                "skip_reason": rsa["skip_reason"],
            })
            continue

        lor = None
        if mode == "FULL":
            lor = compute_lor_from_msa(uni, prot_dir, args.msa_dir)
        arr = fuse(rsa, lor, uni)
        write_per_protein(arr)

        # Long-rows for aggregate
        n = len(arr["resids"])
        for j in range(n):
            long_rows.append([
                uni, j, int(arr["resids"][j]), str(arr["resnames"][j]), str(arr["aa1"][j]),
                f"{arr['sasa_abs'][j]:.4f}", f"{arr['rsa_rel'][j]:.6f}",
                _fmt(arr["lor_mean"][j]), _fmt(arr["lor_max"][j]),
                _fmt(arr["rsalor_mean"][j]), _fmt(arr["rsalor_max"][j]),
                arr["n_msa"] if arr["n_msa"] is not None else 0,
            ])

        elapsed = time.time() - t0
        ok_lor = bool(lor and lor.get("ok_lor"))
        n_msa = arr["n_msa"] if arr["n_msa"] is not None else 0
        lor_msg = f"lor_mean={float(np.nanmean(arr['lor_mean'])):.3f}" if ok_lor else f"lor=NaN({(lor or {}).get('skip_reason_lor', 'rsa-only')})"
        summaries.append({
            "uniprot_id": uni, "ok_rsa": True, "ok_lor": ok_lor,
            "n_residues": rsa["n_residues"], "n_msa": n_msa,
            "rsa_mean": rsa["rsa_mean"], "rsa_median": rsa["rsa_median"],
            "lor_mean_global": float(np.nanmean(arr["lor_mean"])) if ok_lor else None,
            "rsalor_mean_global": float(np.nanmean(arr["rsalor_mean"])) if ok_lor else None,
            "elapsed_seconds": round(elapsed, 3),
            "skip_reason": "" if ok_lor else (lor or {}).get("skip_reason_lor", "rsa-only-mode"),
        })
        print(f"[rsalor] {i:>2}/{len(proteins)} OK   {uni:<22} N={rsa['n_residues']:<4} rsa_mean={rsa['rsa_mean']:.3f} {lor_msg} t={elapsed:.2f}s", flush=True)

    # Aggregate long-format CSV
    long_csv = OUT_DIR / "batch1_rsalor.csv"
    with long_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(PER_RES_COLS)
        for row in long_rows:
            w.writerow(row)

    # Per-protein summary CSV
    sum_csv = OUT_DIR / "batch1_rsalor_summary.csv"
    with sum_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "uniprot_id", "ok_rsa", "ok_lor", "n_residues", "n_msa_sequences",
            "rsa_mean", "rsa_median", "lor_mean_global", "rsalor_mean_global",
            "elapsed_seconds", "skip_reason",
        ])
        for s in summaries:
            w.writerow([
                s["uniprot_id"], int(s["ok_rsa"]), int(s["ok_lor"]),
                s["n_residues"] if s["n_residues"] is not None else "",
                s["n_msa"] if s["n_msa"] is not None else "",
                "" if s["rsa_mean"] is None else f"{s['rsa_mean']:.6f}",
                "" if s["rsa_median"] is None else f"{s['rsa_median']:.6f}",
                "" if s["lor_mean_global"] is None else f"{s['lor_mean_global']:.6f}",
                "" if s["rsalor_mean_global"] is None else f"{s['rsalor_mean_global']:.6f}",
                s["elapsed_seconds"],
                s["skip_reason"],
            ])

    n_rsa_ok = sum(1 for s in summaries if s["ok_rsa"])
    n_lor_ok = sum(1 for s in summaries if s["ok_lor"])
    print(f"[rsalor] DONE: {n_rsa_ok}/{len(summaries)} RSA-ok, {n_lor_ok}/{len(summaries)} LOR-ok (mode={mode})", flush=True)
    print(f"[rsalor] outputs in {OUT_DIR}", flush=True)
    if mode == "RSA-ONLY":
        print(
            "[rsalor] NOTE: LOR/RSALOR columns are NaN. To populate them, Sub 1.3 must:\n"
            "         (1) precache ProteinGym MSAs (a3m or FASTA) named <UNIPROT>.a3m\n"
            "         (2) pip install rsalor in env-bioemu (PyPI: rsalor)\n"
            "         (3) re-run with --msa-dir /path/to/msas",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
