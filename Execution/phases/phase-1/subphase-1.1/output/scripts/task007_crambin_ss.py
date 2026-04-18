#!/usr/bin/env python3
"""
Crambin SS integrity analysis (per R8: BPTI-style BioEmu sanity check).

Based on phases/phase-1/subphase-1.1/output/scripts/hewl_sidechain_recon.py.

Pipeline:
  1. Load BioEmu backbone-only XTC for Crambin (task-007-crambin output)
  2. For each frame: save to temp PDB, run PDBFixer to add sidechains
  3. Measure SG-SG for 3 disulfide bonds: C3-C40, C4-C32, C16-C26
  4. Report integrity at 2.5 A and 3.0 A cutoffs
  5. Compare with BPTI (which was dropped at 56.1% at 4.5 A CB-CB)
"""

import csv
import json
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

CRAMBIN_DIR = Path("/home/rag88/projects/CompBioSummer2026/Execution/"
                   "phases/phase-1/subphase-1.1/output/task-007-crambin")
OUTPUT_DIR = Path("/home/rag88/projects/CompBioSummer2026/Execution/"
                  "phases/phase-1/subphase-1.1/output/task-007-crambin-full-atom")
CSV_PATH = Path("/home/rag88/projects/CompBioSummer2026/Execution/"
                "phases/phase-1/subphase-1.1/output/task-007-crambin-sgsg.csv")
RESULTS_PATH = Path("/home/rag88/projects/CompBioSummer2026/Execution/"
                    "phases/phase-1/subphase-1.1/output/task-007-crambin-ss-results.json")

SS_BONDS = [
    (3, 40),
    (4, 32),
    (16, 26),
]

CUTOFFS = [2.5, 2.8, 3.0, 3.5]
AK3_THRESHOLD = 0.80


def load_trajectory():
    import mdtraj as md
    traj = md.load(str(CRAMBIN_DIR / "samples.xtc"),
                   top=str(CRAMBIN_DIR / "topology.pdb"))
    print(f"Loaded: {traj.n_frames} frames, {traj.n_atoms} atoms, "
          f"{traj.n_residues} residues")
    return traj


def reconstruct_sidechains(input_pdb, output_pdb):
    from pdbfixer import PDBFixer
    from openmm.app import PDBFile
    result = dict(success=False, n_atoms_before=0, n_atoms_after=0,
                  n_sg_atoms=0, error=None)
    try:
        fixer = PDBFixer(filename=str(input_pdb))
        result['n_atoms_before'] = fixer.topology.getNumAtoms()
        fixer.findMissingResidues()
        fixer.findMissingAtoms()
        fixer.addMissingAtoms()
        result['n_atoms_after'] = fixer.topology.getNumAtoms()
        with open(str(output_pdb), 'w') as f:
            PDBFile.writeFile(fixer.topology, fixer.positions, f)
        with open(str(output_pdb)) as f:
            sg_count = sum(1 for line in f if line.startswith('ATOM') and ' SG ' in line)
        result['n_sg_atoms'] = sg_count
        result['success'] = (sg_count == 6)  # Crambin has 6 CYS residues
    except Exception as e:
        result['error'] = str(e)
    return result


def measure_sg_sg_distances(pdb_path, conf_id):
    import mdtraj as md
    measurements = []
    try:
        traj = md.load(str(pdb_path))
        for cys_i, cys_j in SS_BONDS:
            sg_i_atoms = []
            sg_j_atoms = []
            for atom in traj.topology.atoms:
                if atom.name == 'SG':
                    if atom.residue.resSeq == cys_i:
                        sg_i_atoms.append(atom.index)
                    elif atom.residue.resSeq == cys_j:
                        sg_j_atoms.append(atom.index)
            if len(sg_i_atoms) == 1 and len(sg_j_atoms) == 1:
                d_nm = md.compute_distances(traj, [[sg_i_atoms[0], sg_j_atoms[0]]])[0, 0]
                d_A = float(d_nm * 10.0)
                measurements.append(dict(conformation=conf_id,
                                         bond_id=f'Cys{cys_i}-Cys{cys_j}',
                                         residue1=cys_i, residue2=cys_j,
                                         sg_sg_distance_A=d_A, error=None))
            else:
                measurements.append(dict(conformation=conf_id,
                                         bond_id=f'Cys{cys_i}-Cys{cys_j}',
                                         residue1=cys_i, residue2=cys_j,
                                         sg_sg_distance_A=float('nan'),
                                         error=f'SG not found: i={len(sg_i_atoms)}, j={len(sg_j_atoms)}'))
    except Exception as e:
        for cys_i, cys_j in SS_BONDS:
            measurements.append(dict(conformation=conf_id,
                                     bond_id=f'Cys{cys_i}-Cys{cys_j}',
                                     residue1=cys_i, residue2=cys_j,
                                     sg_sg_distance_A=float('nan'),
                                     error=str(e)))
    return measurements


def compute_integrity(all_meas, cutoffs=CUTOFFS):
    bond_distances = defaultdict(list)
    for m in all_meas:
        if not np.isnan(m['sg_sg_distance_A']):
            bond_distances[m['bond_id']].append(m['sg_sg_distance_A'])

    per_bond = {}
    stats = {}
    for bid, dists in sorted(bond_distances.items()):
        dists = np.array(dists)
        stats[bid] = dict(mean=float(np.mean(dists)), std=float(np.std(dists)),
                          min=float(np.min(dists)), max=float(np.max(dists)),
                          median=float(np.median(dists)), n=len(dists))
        per_bond[bid] = {c: float(np.sum(dists < c) / len(dists)) for c in cutoffs}

    # Overall: fraction of conformations where ALL 3 bonds are within cutoff
    conf_ok = defaultdict(lambda: {c: True for c in cutoffs})
    conf_valid = defaultdict(lambda: {c: True for c in cutoffs})
    for m in all_meas:
        if np.isnan(m['sg_sg_distance_A']):
            for c in cutoffs:
                conf_valid[m['conformation']][c] = False
            continue
        for c in cutoffs:
            if m['sg_sg_distance_A'] >= c:
                conf_ok[m['conformation']][c] = False

    confs = set(m['conformation'] for m in all_meas)
    overall = {}
    for c in cutoffs:
        ok = 0
        total = 0
        for cf in confs:
            if conf_valid[cf][c]:
                total += 1
                if conf_ok[cf][c]:
                    ok += 1
        overall[c] = (ok / total) if total else 0.0

    return dict(per_bond=per_bond, overall=overall, stats=stats,
                n_conformations=len(confs),
                n_valid_measurements=sum(len(v) for v in bond_distances.values()))


def main():
    print("=" * 70)
    print("Crambin SS integrity analysis (task-007)")
    print("=" * 70)
    t0 = time.time()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    traj = load_trajectory()
    n_frames = traj.n_frames

    print(f"\n[Step 1] Reconstructing sidechains for {n_frames} frames...")
    recon = []
    failed = []
    for i in range(n_frames):
        conf_id = f"cram_{i:03d}"
        tmp = Path(tempfile.mktemp(suffix='.pdb'))
        out = OUTPUT_DIR / f"{conf_id}.pdb"
        traj[i].save_pdb(str(tmp))
        r = reconstruct_sidechains(tmp, out)
        r['conf_id'] = conf_id; r['frame_idx'] = i
        recon.append(r)
        try: tmp.unlink()
        except OSError: pass
        if not r['success']:
            failed.append(i)
        if (i + 1) % 20 == 0:
            print(f"  Frame {i+1}/{n_frames}")
    n_ok = sum(1 for r in recon if r['success'])
    print(f"  Recon OK: {n_ok}/{n_frames} (failed: {failed})")

    print(f"\n[Step 2] Measuring SG-SG for 3 disulfide bonds...")
    all_meas = []
    for i in range(n_frames):
        if not recon[i]['success']:
            continue
        conf_id = f"cram_{i:03d}"
        pdb = OUTPUT_DIR / f"{conf_id}.pdb"
        all_meas.extend(measure_sg_sg_distances(pdb, conf_id))
    print(f"  Measurements: {len(all_meas)}")

    with open(CSV_PATH, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['conformation', 'bond_id', 'residue1',
                                          'residue2', 'sg_sg_distance_A', 'error'])
        w.writeheader()
        w.writerows(all_meas)
    print(f"  CSV: {CSV_PATH}")

    integrity = compute_integrity(all_meas)
    print(f"\n[Step 3] Integrity")
    print(f"  Valid conformations: {integrity['n_conformations']}")
    for c in CUTOFFS:
        pct = integrity['overall'][c] * 100
        tag = "TRIGGERED" if integrity['overall'][c] < AK3_THRESHOLD else "not triggered"
        print(f"  {c:.1f} A: {pct:.1f}% (AK3 {tag})")
    print(f"\n  Per-bond at 2.5 A:")
    for bid in sorted(integrity['per_bond'].keys()):
        pct = integrity['per_bond'][bid][2.5] * 100
        s = integrity['stats'][bid]
        print(f"    {bid}: {pct:.1f}% (mean={s['mean']:.2f}, std={s['std']:.2f}, range=[{s['min']:.2f}, {s['max']:.2f}])")

    results = dict(n_frames=n_frames, n_successful_recon=n_ok,
                   n_failed_recon=len(failed), failed_frames=failed,
                   integrity=integrity, tool='PDBFixer (OpenMM)',
                   ss_bonds=[list(b) for b in SS_BONDS],
                   elapsed_seconds=time.time() - t0)
    with open(RESULTS_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results: {RESULTS_PATH}")

    primary = integrity['overall'][2.5]
    print(f"\nSUMMARY: Crambin SS integrity at 2.5 A SG-SG = {primary*100:.1f}%")
    if primary >= AK3_THRESHOLD:
        print(f"  -> AK3 NOT triggered. Stability-control role intact (not a drop).")
    else:
        print(f"  -> AK3 triggered. Note: Crambin is a STABILITY CONTROL, not an S2 target,")
        print(f"     so AK3 triggering does not force a drop (as it did for BPTI/HEWL which are S2 targets).")

    return results


if __name__ == '__main__':
    main()
