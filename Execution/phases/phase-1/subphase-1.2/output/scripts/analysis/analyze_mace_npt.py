#!/usr/bin/env python
"""analyze_mace_npt.py -- Top-level analyzer for MACE-OFF24 NPT 5 ns trajectories.

For each completed Sub 1.4 production run (DCD/HDF5 trajectory + topology +
StateDataReporter log), produces:
  * S2 per residue (block-bootstrap CIs) via S2_compute.compute_s2
  * Per-residue Cα RMSF (matches compute_rmsf_batch1.py conventions)
  * Density / Temperature / Pressure stability via density_T_P.evaluate_log
  * Contact-map drift (Q-score per frame) via contacts.analyze_contacts

I/O contract
    Inputs:
        --input-traj   : DCD/HDF5/XTC trajectory of the production segment
        --input-top    : topology (PDB or PRMTOP)
        --input-log    : StateDataReporter CSV from production
        --output-dir   : output directory for NPZ/JSON/CSV artefacts
        --protein-id   : short identifier, e.g., 'WW', 'GB3', 'ubq'
        --reference    : optional reference PDB for native-contact comparison
        (defaults to frame 0 if omitted)

    Outputs (in --output-dir):
        <protein-id>_S2.npz                    (per-residue S2 + CIs)
        <protein-id>_S2_summary.json
        <protein-id>_rmsf.npz / .csv           (per-residue Cα RMSF)
        <protein-id>_npt_qc.json               (T, P, density stats + verdict)
        <protein-id>_contacts.npz              (Q-score per frame + native pairs)
        <protein-id>_contacts_summary.json
        <protein-id>_master_summary.json       (combined verdict + headlines)

Reference scripts:
    Sub 1.1 mace_analyze.py (parses StateDataReporter CSV; this is generalized
    in density_T_P.parse_state_log)
    compute_rmsf_batch1.py (RMSF conventions: align all to frame 0, compute
    per-residue Cα RMSF in Angstroms, save NPZ + CSV)

Sub 1.4 SubAgent: this is intentionally a thin orchestrator. The heavy
lifting lives in the specialist modules (S2_compute, density_T_P, contacts).
You should be able to run end-to-end after filling in the NotImplementedError
bodies in S2_compute._load_nh_vectors / _autocorrelation_s2 and
contacts._load_ca_positions / _load_reference_ca + the RMSF body in this
file.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Optional

import numpy as np

from . import S2_compute
from . import density_T_P
from . import contacts
from . import _rmsf_helpers


# Default MACE NPT equilibration discard window (per OSF v3 §8): 100 ps.
MACE_NPT_DISCARD_PS = 100.0


def compute_rmsf(traj_path: Path, top_path: Path,
                 discard_first_ps: float = MACE_NPT_DISCARD_PS) -> dict:
    """Per-residue Cα RMSF, matching compute_rmsf_batch1.py conventions.

    Returns dict with keys:
        ok          : bool
        n_frames    : int
        n_residues  : int
        resid       : (N,) int
        resname     : (N,) <U3
        rmsf_A      : (N,) float (per-residue Cα RMSF in Angstroms)
        rmsf_mean   : float
        rmsf_median : float
        rmsf_max    : float
        rmsf_min    : float
        skip_reason : str or None

    Discards the first `discard_first_ps` ps as MACE NPT equilibration
    (default 100 ps per OSF v3 §8). Multi-chain proteins are scoped to the
    first segid (chain A by alphanumeric ordering); single-chain trajectories
    pass through unchanged.

    Mirrors compute_rmsf_batch1.py:99-138: MDAnalysis Universe(in_memory=True)
    -> AlignTraj on Cα -> rms.RMSF on Cα selection. Output column conventions
    match (resid, resname, rmsf_ca_angstrom).
    """
    return _rmsf_helpers.mace_compute_rmsf(
        Path(traj_path), Path(top_path), discard_first_ps=discard_first_ps,
    )


def save_rmsf_artifacts(rmsf: dict, output_dir: Path, protein_id: str) -> None:
    """Save RMSF NPZ + CSV in compute_rmsf_batch1.py-compatible format."""
    if not rmsf.get("ok"):
        return
    np.savez(
        output_dir / f"{protein_id}_rmsf.npz",
        protein_id=protein_id,
        resid=rmsf["resid"],
        resname=rmsf["resname"],
        rmsf_ca_angstrom=rmsf["rmsf_A"],
        n_frames=rmsf["n_frames"],
    )
    csv_path = output_dir / f"{protein_id}_rmsf.csv"
    import csv
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["protein_id", "residue_idx_0based", "resid", "resname",
                    "rmsf_ca_angstrom", "n_frames"])
        for i, (rid, rname, val) in enumerate(zip(rmsf["resid"], rmsf["resname"], rmsf["rmsf_A"])):
            w.writerow([protein_id, i, int(rid), str(rname), f"{val:.6f}", rmsf["n_frames"]])


def run(
    traj_path: str | Path,
    top_path: str | Path,
    log_path: str | Path,
    output_dir: str | Path,
    protein_id: str,
    reference: Optional[str | Path] = None,
    block_ns: float = 1.25,
    tau_ns: float = 1.0,
) -> dict:
    """Top-level pipeline. Returns a master_summary dict."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    summary: dict = {
        "protein_id": protein_id,
        "trajectory": str(traj_path),
        "topology": str(top_path),
        "log": str(log_path),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    # 1. NPT QC (T/P/density)
    t0 = time.time()
    npt_qc = density_T_P.evaluate_log(log_path)
    with (out / f"{protein_id}_npt_qc.json").open("w") as f:
        json.dump(npt_qc, f, indent=2)
    summary["npt_qc"] = {
        "verdict": npt_qc["verdict"],
        "duration_ns": npt_qc["duration_ns"],
        "T_mean": npt_qc["temperature"]["mean"],
        "T_std": npt_qc["temperature"]["std"],
        "density_mean": npt_qc["density"]["mean"],
        "P_mean": npt_qc["pressure"]["mean"],
    }
    summary["npt_qc_seconds"] = time.time() - t0

    # 2. RMSF
    t0 = time.time()
    rmsf = compute_rmsf(Path(traj_path), Path(top_path))
    save_rmsf_artifacts(rmsf, out, protein_id)
    summary["rmsf"] = {
        "ok": rmsf.get("ok", False),
        "rmsf_mean": rmsf.get("rmsf_mean"),
        "rmsf_max": rmsf.get("rmsf_max"),
        "n_residues": rmsf.get("n_residues"),
    }
    summary["rmsf_seconds"] = time.time() - t0

    # 3. S2
    t0 = time.time()
    s2_result = S2_compute.compute_s2(
        traj_path, top_path, block_ns=block_ns, tau_ns=tau_ns,
    )
    S2_compute.save_s2_npz(s2_result, out / f"{protein_id}_S2.npz")
    summary["S2"] = {
        "n_residues": int(s2_result.resid.size),
        "S2_mean": float(np.nanmean(s2_result.s2_mean)),
        "S2_min": float(np.nanmin(s2_result.s2_mean)),
        "n_blocks": s2_result.n_blocks,
    }
    summary["S2_seconds"] = time.time() - t0

    # 4. Contacts
    t0 = time.time()
    contact_result = contacts.analyze_contacts(
        traj_path, top_path, ref_path=reference,
    )
    contacts.save_contact_result(contact_result, out / f"{protein_id}_contacts.npz")
    summary["contacts"] = contacts.summarize(contact_result)
    summary["contacts_seconds"] = time.time() - t0

    summary["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    summary["overall_verdict"] = "PASS" if (
        npt_qc["verdict"] == "PASS"
        and summary["rmsf"]["ok"]
        and summary["contacts"]["Q_min"] >= 0.5  # heuristic; refine in Sub 1.4
    ) else "REVIEW"

    with (out / f"{protein_id}_master_summary.json").open("w") as f:
        json.dump(summary, f, indent=2)
    return summary


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--input-traj", required=True)
    p.add_argument("--input-top", required=True)
    p.add_argument("--input-log", required=True, help="StateDataReporter CSV log")
    p.add_argument("--output-dir", required=True)
    p.add_argument("--protein-id", required=True)
    p.add_argument("--reference", default=None,
                   help="Optional reference PDB for native-contact map (else frame 0)")
    p.add_argument("--block-ns", type=float, default=1.25)
    p.add_argument("--tau-ns", type=float, default=1.0)
    args = p.parse_args()

    summary = run(
        args.input_traj, args.input_top, args.input_log,
        args.output_dir, args.protein_id,
        reference=args.reference,
        block_ns=args.block_ns, tau_ns=args.tau_ns,
    )
    print(f"[mace_npt] {args.protein_id} verdict={summary['overall_verdict']} "
          f"NPT={summary['npt_qc']['verdict']} "
          f"S2_mean={summary['S2']['S2_mean']:.3f} "
          f"Q_min={summary['contacts']['Q_min']:.3f}")
    return 0 if summary["overall_verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
