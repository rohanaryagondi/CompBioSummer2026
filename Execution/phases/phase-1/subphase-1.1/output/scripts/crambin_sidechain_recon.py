#!/usr/bin/env python3
"""
Crambin Sidechain Reconstruction and SG-SG Distance Measurement
================================================================
Task 007 continuation - Subphase 1.1, R8 sanity check

Reconstructs full sidechains on BioEmu backbone-only Crambin conformations
using PDBFixer (OpenMM), then measures true SG-SG distances for all 3
disulfide bonds. The purpose is to detect any BPTI-style SS failure
(BPTI was dropped; Crambin has the same disulfide topology complexity).

Background:
  BPTI showed 56.1% CB-CB integrity at 4.5 A (dropped).
  HEWL was confirmed to have AK3 failure at 2.5 A SG-SG.
  Crambin is a "stability control" (no T3 applicability) but we verify
  whether it is also affected so the note can warn future work.

Input:  BioEmu XTC trajectory + topology PDB (backbone only: N, CA, C, CB, O)
Output: Full-atom PDBs (in-memory, not persisted), SG-SG distance CSV, JSON summary

Tool: PDBFixer (OpenMM) - adds missing sidechain atoms using standard
      rotamer placement. Each CYS residue gets its SG atom reconstructed.

Crambin disulfide bonds (from PDB 1CRN, 1-indexed):
  Cys3-Cys40
  Cys4-Cys32
  Cys16-Cys26

Author: protein-addition-executor continuation SubAgent
Date: 2026-04-17
"""

import os
import sys
import csv
import json
import time
import tempfile
import numpy as np
from pathlib import Path

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

CRAMBIN_DIR = Path("/home/rag88/projects/CompBioSummer2026/Execution/"
                   "phases/phase-1/subphase-1.1/output/task-007-crambin")
OUTPUT_DIR = Path("/home/rag88/projects/CompBioSummer2026/Execution/"
                  "phases/phase-1/subphase-1.1/output/task-007-crambin-full-atom")
CSV_PATH = Path("/home/rag88/projects/CompBioSummer2026/Execution/"
                "phases/phase-1/subphase-1.1/output/task-007-crambin-sgsg-distances.csv")
JSON_PATH = Path("/home/rag88/projects/CompBioSummer2026/Execution/"
                 "phases/phase-1/subphase-1.1/output/task-007-crambin-sgsg-results.json")

# Crambin disulfide bonds (1-indexed residue numbers, matching PDB convention)
# BioEmu topology is 0-indexed internally, so script converts via `cys_i - 1`
SS_BONDS = [
    (3, 40),   # Cys3-Cys40
    (4, 32),   # Cys4-Cys32
    (16, 26),  # Cys16-Cys26
]

# SG-SG cutoffs for integrity assessment (Angstroms)
CUTOFFS = [2.5, 2.8, 3.0, 3.5]

# AK3 threshold (matches HEWL script convention)
AK3_THRESHOLD = 0.80


def load_trajectory():
    """Load the BioEmu XTC trajectory with topology."""
    import mdtraj as md
    traj = md.load(
        str(CRAMBIN_DIR / "samples.xtc"),
        top=str(CRAMBIN_DIR / "topology.pdb")
    )
    print(f"Loaded trajectory: {traj.n_frames} frames, "
          f"{traj.n_atoms} atoms, {traj.n_residues} residues")
    return traj


def save_frame_as_pdb(traj, frame_idx, output_path):
    frame = traj[frame_idx]
    frame.save_pdb(str(output_path))


def reconstruct_sidechains(input_pdb, output_pdb):
    """Use PDBFixer to add missing sidechain atoms. Returns dict."""
    from pdbfixer import PDBFixer
    from openmm.app import PDBFile

    result = {
        'success': False,
        'n_atoms_before': 0,
        'n_atoms_after': 0,
        'n_sg_atoms': 0,
        'error': None
    }

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
            sg_count = sum(1 for line in f
                          if line.startswith('ATOM') and ' SG ' in line)
        result['n_sg_atoms'] = sg_count
        # Crambin has 6 CYS residues (3 SS bonds)
        result['success'] = (sg_count == 6)

    except Exception as e:
        result['error'] = str(e)

    return result


def measure_sg_sg_distances(pdb_path, conf_id):
    """Measure SG-SG distances for all 3 Crambin SS bonds."""
    import mdtraj as md

    measurements = []
    try:
        traj = md.load(str(pdb_path))

        for cys_i, cys_j in SS_BONDS:
            sg_i_sel = traj.topology.select(f'resid {cys_i - 1} and name SG')
            sg_j_sel = traj.topology.select(f'resid {cys_j - 1} and name SG')

            if len(sg_i_sel) == 0 or len(sg_j_sel) == 0:
                # Fallback via resSeq
                sg_i_atoms = []
                sg_j_atoms = []
                for atom in traj.topology.atoms:
                    if atom.name == 'SG':
                        if atom.residue.resSeq == cys_i:
                            sg_i_atoms.append(atom.index)
                        elif atom.residue.resSeq == cys_j:
                            sg_j_atoms.append(atom.index)

                if len(sg_i_atoms) == 1 and len(sg_j_atoms) == 1:
                    sg_i_sel = np.array(sg_i_atoms)
                    sg_j_sel = np.array(sg_j_atoms)
                else:
                    measurements.append({
                        'conformation': conf_id,
                        'bond_id': f'Cys{cys_i}-Cys{cys_j}',
                        'residue1': cys_i,
                        'residue2': cys_j,
                        'sg_sg_distance_A': float('nan'),
                        'error': f'SG not found: i={len(sg_i_atoms)}, j={len(sg_j_atoms)}'
                    })
                    continue

            dist_nm = md.compute_distances(
                traj, [[sg_i_sel[0], sg_j_sel[0]]])[0, 0]
            dist_A = float(dist_nm * 10.0)

            measurements.append({
                'conformation': conf_id,
                'bond_id': f'Cys{cys_i}-Cys{cys_j}',
                'residue1': cys_i,
                'residue2': cys_j,
                'sg_sg_distance_A': dist_A,
                'error': None
            })

    except Exception as e:
        for cys_i, cys_j in SS_BONDS:
            measurements.append({
                'conformation': conf_id,
                'bond_id': f'Cys{cys_i}-Cys{cys_j}',
                'residue1': cys_i,
                'residue2': cys_j,
                'sg_sg_distance_A': float('nan'),
                'error': str(e)
            })

    return measurements


def compute_integrity(all_measurements, cutoffs=CUTOFFS):
    """Per-bond and overall SS integrity at multiple cutoffs."""
    from collections import defaultdict

    bond_distances = defaultdict(list)
    for m in all_measurements:
        if not np.isnan(m['sg_sg_distance_A']):
            bond_distances[m['bond_id']].append(m['sg_sg_distance_A'])

    results = {
        'per_bond': {},
        'overall': {},
        'stats': {},
        'n_conformations': 0,
        'n_valid_measurements': 0
    }

    for bond_id, distances in sorted(bond_distances.items()):
        distances = np.array(distances)
        results['stats'][bond_id] = {
            'mean': float(np.mean(distances)),
            'std': float(np.std(distances)),
            'min': float(np.min(distances)),
            'max': float(np.max(distances)),
            'median': float(np.median(distances)),
            'n': len(distances)
        }

        results['per_bond'][bond_id] = {}
        for cutoff in cutoffs:
            intact = float(np.sum(distances < cutoff) / len(distances))
            results['per_bond'][bond_id][cutoff] = intact

    all_distances = []
    for distances in bond_distances.values():
        all_distances.extend(distances)
    all_distances = np.array(all_distances)

    results['n_valid_measurements'] = len(all_distances)

    valid_confs = set()
    for m in all_measurements:
        if not np.isnan(m['sg_sg_distance_A']):
            valid_confs.add(m['conformation'])
    results['n_conformations'] = len(valid_confs)

    for cutoff in cutoffs:
        if len(all_distances) > 0:
            intact = float(np.sum(all_distances < cutoff) / len(all_distances))
        else:
            intact = 0.0
        results['overall'][cutoff] = intact

    return results


def main():
    print("=" * 70)
    print("Crambin Sidechain Reconstruction and SG-SG Distance Analysis")
    print("Task 007 continuation - Subphase 1.1 (R8 sanity)")
    print("=" * 70)

    start_time = time.time()

    print("\n[Step 1] Loading BioEmu trajectory...")
    traj = load_trajectory()
    n_frames = traj.n_frames

    print(f"\n[Step 2] Reconstructing sidechains for {n_frames} conformations...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    recon_results = []
    failed_frames = []

    for i in range(n_frames):
        conf_id = f"crambin_conf_{i:03d}"
        tmp_pdb = Path(tempfile.mktemp(suffix='.pdb'))
        out_pdb = OUTPUT_DIR / f"{conf_id}.pdb"

        save_frame_as_pdb(traj, i, tmp_pdb)
        result = reconstruct_sidechains(tmp_pdb, out_pdb)
        result['conf_id'] = conf_id
        result['frame_idx'] = i
        recon_results.append(result)

        try:
            tmp_pdb.unlink()
        except OSError:
            pass

        status = "OK" if result['success'] else "FAIL"
        if not result['success']:
            failed_frames.append(i)
        if (i + 1) % 10 == 0 or not result['success']:
            print(f"  Frame {i+1:3d}/{n_frames}: {status} "
                  f"({result['n_atoms_before']}->{result['n_atoms_after']} atoms, "
                  f"{result['n_sg_atoms']} SG atoms)")

    n_success = sum(1 for r in recon_results if r['success'])
    print(f"\n  Reconstruction complete: {n_success}/{n_frames} successful")
    if failed_frames:
        print(f"  Failed frames: {failed_frames}")

    print(f"\n[Step 3] Measuring SG-SG distances...")
    all_measurements = []

    for i in range(n_frames):
        if not recon_results[i]['success']:
            continue
        conf_id = f"crambin_conf_{i:03d}"
        pdb_path = OUTPUT_DIR / f"{conf_id}.pdb"
        measurements = measure_sg_sg_distances(pdb_path, conf_id)
        all_measurements.extend(measurements)

        if (i + 1) % 20 == 0:
            print(f"  Measured {i+1}/{n_frames} conformations...")

    print(f"  Total measurements: {len(all_measurements)}")

    print(f"\n[Step 4] Writing distance CSV to {CSV_PATH}...")
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CSV_PATH, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'conformation', 'bond_id', 'residue1', 'residue2',
            'sg_sg_distance_A', 'error'
        ])
        writer.writeheader()
        writer.writerows(all_measurements)

    print(f"\n[Step 5] Computing SS integrity metrics...")
    integrity = compute_integrity(all_measurements)

    print(f"\n  Valid conformations: {integrity['n_conformations']}")
    print(f"  Valid measurements: {integrity['n_valid_measurements']}")

    print(f"\n  Overall integrity:")
    for cutoff in CUTOFFS:
        pct = integrity['overall'][cutoff] * 100
        ak3 = "TRIGGERED" if integrity['overall'][cutoff] < AK3_THRESHOLD else "not triggered"
        print(f"    {cutoff:.1f} A: {pct:.1f}% ({ak3})")

    print(f"\n  Per-bond integrity at 2.5 A primary cutoff:")
    for bond_id in sorted(integrity['per_bond'].keys()):
        pct = integrity['per_bond'][bond_id][2.5] * 100
        stats = integrity['stats'][bond_id]
        print(f"    {bond_id}: {pct:.1f}% "
              f"(mean={stats['mean']:.2f} A, std={stats['std']:.2f} A, "
              f"range=[{stats['min']:.2f}, {stats['max']:.2f}] A)")

    results_json = {
        'protein': 'crambin',
        'n_frames': n_frames,
        'n_successful_recon': n_success,
        'n_failed_recon': len(failed_frames),
        'failed_frames': failed_frames,
        'n_valid_measurements': integrity['n_valid_measurements'],
        'integrity': integrity,
        'tool': 'PDBFixer (OpenMM)',
        'ss_bonds': [f'Cys{a}-Cys{b}' for a, b in SS_BONDS],
        'elapsed_seconds': time.time() - start_time,
    }

    with open(JSON_PATH, 'w') as f:
        json.dump(results_json, f, indent=2)
    print(f"\n  Results JSON written to {JSON_PATH}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    primary_integrity = integrity['overall'][2.5]
    if primary_integrity >= AK3_THRESHOLD:
        tag = "NOT TRIGGERED"
        msg = (f"SG-SG integrity at 2.5 A = {primary_integrity*100:.1f}% "
               f">= {AK3_THRESHOLD*100:.0f}% threshold")
    else:
        tag = "TRIGGERED"
        msg = (f"SG-SG integrity at 2.5 A = {primary_integrity*100:.1f}% "
               f"< {AK3_THRESHOLD*100:.0f}% threshold (BPTI-style failure)")

    print(f"  Crambin AK3 equivalent: **{tag}**")
    print(f"  Finding: {msg}")
    print(f"  Note: Crambin is stability control; T3 does NOT apply.")
    print(f"  Elapsed time: {time.time() - start_time:.1f} seconds")

    return results_json


if __name__ == '__main__':
    results = main()
