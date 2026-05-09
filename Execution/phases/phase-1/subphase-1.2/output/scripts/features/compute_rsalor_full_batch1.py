#!/usr/bin/env python
"""Sub 1.3 unblock: full-mode RSALOR (RSA + LOR) for BioEmu batch 1.

This is a SIBLING of `compute_rsalor_batch1.py` that uses the actual rsalor 1.1.9
API (which differs from what the original script anticipated). The original script
remains the canonical RSA-only path; this script writes the same per-protein NPZ/CSV
files at the same paths but populates LOR/RSALOR columns from precomputed MSAs.

WHY A SIBLING (NOT AN EDIT):
  Per Sub 1.2 single-shot RSALOR-rescue task constraints (2026-05-06), the
  existing `compute_rsalor_batch1.py` must not be modified. This file is a
  separate implementation that produces the same output schema.

WHAT'S DIFFERENT FROM THE ORIGINAL:
  1. rsalor.MSA.get_scores() returns dicts keyed by `mutation_fasta` (e.g. "K1A"),
     not by `position`/`wt_aa`/`mut_aa`. We parse that string.
  2. The score keys are `LOR` and `RSA*LOR` (capitalized; `RSA*LOR` has a literal
     star). We probe a list of accepted keys.
  3. MSA depth is exposed as `m.depth`, not `n_sequences`.

INPUTS:
  - BioEmu ensembles at `/nfs/roberts/scratch/.../bioemu-ensembles/batch1/<UNI>/topology.pdb`
  - Per-UniProt MSAs at `<msa-dir>/<UNI>.fasta` (or `.a3m`/`.fa`/`.a2m`)
    Note: `.a2m` is a FASTA-syntactic format (lowercase = insert state). rsalor
    accepts it transparently. ProteinGym v1.3 ships `.a2m`.

OUTPUTS (same paths as compute_rsalor_batch1.py):
  - output/features/<UNI>_rsalor.npz       per-residue NPZ
  - output/features/<UNI>_rsalor.csv       per-residue CSV
  - output/features/batch1_rsalor.csv      aggregated long-format
  - output/features/batch1_rsalor_summary.csv  per-protein summary

Run:
  PYTHONNOUSERSITE=0 /home/rag88/.conda/envs-venv/env-bioemu-rsalor/bin/python \
      compute_rsalor_full_batch1.py \
      --msa-dir /nfs/roberts/scratch/pi_mg269/rag88/proteingym/msas/by_uniprot/
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import time
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
from Bio.PDB import PDBParser
from Bio.PDB.SASA import ShrakeRupley

ENSEMBLE_ROOT = Path("/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch1")
OUT_DIR = Path("/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/features")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MIN_RESIDUES = 5

# Tien et al. 2013 (PLOS ONE) max ASA, GLY-X-GLY tripeptide reference.
TIEN_MAX_ASA = {
    "ALA": 129.0, "ARG": 274.0, "ASN": 195.0, "ASP": 193.0, "CYS": 167.0,
    "GLN": 225.0, "GLU": 223.0, "GLY": 104.0, "HIS": 224.0, "ILE": 197.0,
    "LEU": 201.0, "LYS": 236.0, "MET": 224.0, "PHE": 240.0, "PRO": 159.0,
    "SER": 155.0, "THR": 172.0, "TRP": 285.0, "TYR": 263.0, "VAL": 174.0,
}

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
    """Compute per-residue SASA + relative RSA from topology.pdb."""
    status = {
        "uniprot_id": uni_id, "ok_rsa": False, "n_residues": None,
        "rsa_mean": None, "rsa_median": None, "skip_reason": None,
        "resids": None, "resnames": None, "aa1": None,
        "sasa_abs": None, "rsa_rel": None,
    }

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
            if res.id[0].strip():
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


# rsalor 1.1.9 mutation_fasta strings look like "K1A" (one-letter WT, FASTA pos, mut)
# Position is 1-based FASTA index. Some entries may be insertions ("K1AA"?) — we
# only accept the canonical single-mut form.
_MUT_RE = re.compile(r"^([ACDEFGHIKLMNPQRSTVWY])(\d+)([ACDEFGHIKLMNPQRSTVWY])$")


def _pick(d: dict, keys: list[str]):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def compute_lor_from_msa(uni_id: str, prot_dir: Path, msa_dir: Path) -> dict:
    """Compute per-mutation LOR via rsalor; aggregate per FASTA position."""
    out = {
        "ok_lor": False, "n_msa_sequences": None,
        "by_pos": None, "skip_reason_lor": None,
    }
    msa_candidates = [
        msa_dir / f"{uni_id}.fasta",
        msa_dir / f"{uni_id}.a3m",
        msa_dir / f"{uni_id}.a2m",
        msa_dir / f"{uni_id}.fa",
    ]
    msa_path = next((p for p in msa_candidates if p.exists()), None)
    if msa_path is None:
        out["skip_reason_lor"] = f"no_msa_in:{msa_dir}"
        return out

    try:
        from rsalor import MSA
    except Exception as exc:
        out["skip_reason_lor"] = f"rsalor_import_failed:{exc}"
        return out

    pdb = prot_dir / "topology.pdb"
    try:
        msa = MSA(str(msa_path), str(pdb), "A", num_threads=1, verbose=False)
        scores = msa.get_scores()
    except Exception as exc:
        out["skip_reason_lor"] = f"rsalor_run_failed:{exc}"
        return out

    by_pos: dict[int, dict[str, list[float]]] = {}
    for s in scores:
        # rsalor 1.1.9: mutation in field "mutation_fasta" (e.g. "K1A").
        mut_str = _pick(s, ["mutation_fasta", "mutation_fasta_trimmed"])
        if mut_str is None:
            continue
        m = _MUT_RE.match(str(mut_str))
        if not m:
            continue
        wt, pos_str, mt = m.groups()
        if wt == mt:
            continue  # identity
        try:
            pos = int(pos_str)
        except Exception:
            continue
        lor = _pick(s, ["LOR", "lor"])
        rsa_lor = _pick(s, ["RSA*LOR", "rsa_lor", "rsalor"])
        try:
            lor_v = float(lor) if lor is not None else float("nan")
            rl_v = float(rsa_lor) if rsa_lor is not None else float("nan")
        except Exception:
            continue
        if math.isnan(lor_v):
            continue
        d = by_pos.setdefault(pos, {"lor": [], "rsalor": []})
        d["lor"].append(lor_v)
        if not math.isnan(rl_v):
            d["rsalor"].append(rl_v)

    if not by_pos:
        out["skip_reason_lor"] = "rsalor_empty_scores"
        return out

    n_seq = getattr(msa, "depth", None) or getattr(msa, "n_sequences", None) \
        or getattr(msa, "num_sequences", None) \
        or len(getattr(msa, "sequences", []) or [])

    out["ok_lor"] = True
    out["by_pos"] = by_pos
    out["n_msa_sequences"] = int(n_seq) if n_seq else None
    return out


def fuse(rsa: dict, lor: dict, uni_id: str) -> dict:
    n = rsa["n_residues"]
    lor_mean = np.full(n, np.nan, dtype=np.float64)
    lor_max = np.full(n, np.nan, dtype=np.float64)
    rl_mean = np.full(n, np.nan, dtype=np.float64)
    rl_max = np.full(n, np.nan, dtype=np.float64)

    n_msa = None
    if lor and lor.get("ok_lor"):
        n_msa = lor.get("n_msa_sequences")
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
        "n_msa": n_msa,
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
    ap = argparse.ArgumentParser(description="Full-mode RSALOR per-residue features for BioEmu batch 1")
    ap.add_argument("--msa-dir", type=Path, required=True,
                    help="Directory with <UNIPROT>.{fasta,a3m,a2m,fa} MSAs.")
    ap.add_argument("--ensemble-root", type=Path, default=ENSEMBLE_ROOT)
    ap.add_argument("--limit", type=int, default=None,
                    help="Process only first N proteins (smoke testing)")
    ap.add_argument("--only", type=str, default=None,
                    help="Process only this single UniProt ID (smoke testing)")
    args = ap.parse_args()

    if not args.msa_dir.exists():
        print(f"[rsalor-full] FATAL: --msa-dir {args.msa_dir} does not exist", flush=True)
        return 1

    try:
        import rsalor  # noqa: F401
    except Exception as exc:
        print(f"[rsalor-full] FATAL: rsalor not importable ({exc})", flush=True)
        return 1

    print(f"[rsalor-full] mode=FULL; ensemble_root={args.ensemble_root}; out_dir={OUT_DIR}", flush=True)

    proteins = sorted(p.name for p in args.ensemble_root.iterdir() if p.is_dir() and p.name != "logs")
    if args.only:
        proteins = [p for p in proteins if p == args.only]
    if args.limit:
        proteins = proteins[: args.limit]
    print(f"[rsalor-full] {len(proteins)} candidate protein dirs", flush=True)

    summaries = []
    long_rows = []

    for i, uni in enumerate(proteins, 1):
        prot_dir = args.ensemble_root / uni
        t0 = time.time()
        rsa = compute_rsa(uni, prot_dir)

        if not rsa["ok_rsa"]:
            print(f"[rsalor-full] {i:>2}/{len(proteins)} SKIP {uni:<22} reason={rsa['skip_reason']}", flush=True)
            summaries.append({
                "uniprot_id": uni, "ok_rsa": False, "ok_lor": False,
                "n_residues": rsa["n_residues"], "n_msa": None,
                "rsa_mean": None, "rsa_median": None,
                "lor_mean_global": None, "rsalor_mean_global": None,
                "elapsed_seconds": round(time.time() - t0, 3),
                "skip_reason": rsa["skip_reason"],
            })
            continue

        lor = compute_lor_from_msa(uni, prot_dir, args.msa_dir)
        arr = fuse(rsa, lor, uni)
        write_per_protein(arr)

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
        if ok_lor:
            lor_arr = arr["lor_mean"]
            lor_finite = lor_arr[np.isfinite(lor_arr)]
            covered = int(lor_finite.size)
            if covered > 0:
                lor_msg = f"lor_mean={float(np.mean(lor_finite)):.3f} cov={covered}/{n}"
            else:
                lor_msg = "lor=NaN(empty_alignment)"
        else:
            lor_msg = f"lor=NaN({(lor or {}).get('skip_reason_lor', 'rsa-only')})"
        summaries.append({
            "uniprot_id": uni, "ok_rsa": True, "ok_lor": ok_lor,
            "n_residues": rsa["n_residues"], "n_msa": n_msa,
            "rsa_mean": rsa["rsa_mean"], "rsa_median": rsa["rsa_median"],
            "lor_mean_global": float(np.nanmean(arr["lor_mean"])) if ok_lor else None,
            "rsalor_mean_global": float(np.nanmean(arr["rsalor_mean"])) if ok_lor else None,
            "elapsed_seconds": round(elapsed, 3),
            "skip_reason": "" if ok_lor else (lor or {}).get("skip_reason_lor", "rsa-only-mode"),
        })
        print(f"[rsalor-full] {i:>2}/{len(proteins)} OK   {uni:<22} N={rsa['n_residues']:<4} rsa_mean={rsa['rsa_mean']:.3f} {lor_msg} t={elapsed:.2f}s", flush=True)

    # Aggregate long-format CSV (only when full pass)
    if not args.only and not args.limit:
        long_csv = OUT_DIR / "batch1_rsalor.csv"
        with long_csv.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(PER_RES_COLS)
            for row in long_rows:
                w.writerow(row)

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
    print(f"[rsalor-full] DONE: {n_rsa_ok}/{len(summaries)} RSA-ok, {n_lor_ok}/{len(summaries)} LOR-ok", flush=True)
    print(f"[rsalor-full] outputs in {OUT_DIR}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
