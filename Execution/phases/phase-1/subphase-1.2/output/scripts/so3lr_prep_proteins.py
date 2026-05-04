#!/usr/bin/env python3
"""
SO3LR Pilot Preparation Script (Task 002, Subphase 1.2)

One-time preparation step that runs INSIDE env-mace (which has pdbfixer+openmm).
Produces per-protein hydrogenated vacuum XYZ files consumable by the SO3LR CLI
(which runs in env-so3lr).

Why two envs:
  - env-so3lr does NOT have pdbfixer/openmm (MLFF-only env).
  - env-mace DOES have pdbfixer (used for MACE/OpenMM integrator).
  - Rather than cross-contaminate envs, we prepare XYZs in env-mace and
    persist them; subsequent SLURM jobs activate env-so3lr only.

Inputs: PDB files from phases/phase-0/subphase-0.1/proteins/
Outputs: output/trajectories/so3lr_vacuum/<protein>/input.xyz
         output/trajectories/so3lr_vacuum/<protein>/input_h.pdb (auditing copy)
         output/trajectories/so3lr_vacuum/<protein>/prep_summary.json
"""

import os
import sys
import json
import io
import logging
import argparse
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("so3lr_prep_proteins")

REPO_ROOT = "/home/rag88/projects/CompBioSummer2026"
PROTEIN_DIR = f"{REPO_ROOT}/Execution/phases/phase-0/subphase-0.1/proteins"

PROTEIN_ALIASES = {
    "ww":   {"pdb": f"{PROTEIN_DIR}/ww.pdb",   "chain": "A", "resid_range": (6, 39)},
    "gb3":  {"pdb": f"{PROTEIN_DIR}/gb3.pdb",  "chain": "A", "resid_range": (1, 56)},
    "gb1":  {"pdb": f"{PROTEIN_DIR}/gb1.pdb",  "chain": "A", "resid_range": (1, 56)},
    "ntl9": {"pdb": f"{PROTEIN_DIR}/ntl9.pdb", "chain": "A", "resid_range": (1, 51)},
    "ubq":  {"pdb": f"{PROTEIN_DIR}/ubq.pdb",  "chain": "A", "resid_range": (1, 76)},
}

ALLOWED_Z = {1, 6, 7, 8, 9, 15, 16, 17}


def strip_pdb_to_chain_and_range(pdb_in: str, chain: str, rng: tuple,
                                  pdb_out: str):
    """Write a stripped PDB with only chain `chain`, residues in `rng`,
    ATOM records only (no HETATM), first model only."""
    n_atoms_written = 0
    n_resid_kept = set()
    in_first_model = True
    with open(pdb_in) as fin, open(pdb_out, "w") as fout:
        for line in fin:
            rec = line[:6].strip()
            if rec == "ENDMDL":
                in_first_model = False
                break
            if rec != "ATOM":
                continue
            ch = line[21:22].strip()
            if ch and chain and ch != chain:
                continue
            try:
                resid = int(line[22:26].strip())
            except ValueError:
                continue
            if rng is not None:
                lo, hi = rng
                if resid < lo or resid > hi:
                    continue
            fout.write(line)
            n_atoms_written += 1
            n_resid_kept.add(resid)
        fout.write("END\n")
    return n_atoms_written, n_resid_kept


def add_hydrogens_and_write_xyz(stripped_pdb: str,
                                 xyz_out: str,
                                 h_pdb_out: str):
    """Use pdbfixer to fill missing atoms + add hydrogens at pH 7.0.
    Write XYZ (for SO3LR CLI) and a copy of the hydrogenated PDB.
    """
    from pdbfixer import PDBFixer
    from openmm.app import PDBFile

    fixer = PDBFixer(filename=stripped_pdb)
    fixer.findMissingResidues()
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    # Do NOT add solvent -- vacuum prep.
    fixer.addMissingHydrogens(pH=7.0)

    # Save hydrogenated PDB (audit trail)
    with open(h_pdb_out, "w") as f:
        PDBFile.writeFile(fixer.topology, fixer.positions, f, keepIds=True)

    # Extract positions and symbols, write XYZ.
    # fixer.positions is a list of openmm Quantity (nm); convert to Å.
    positions = fixer.positions.value_in_unit_system(__import__("openmm.unit",
                                                     fromlist=[""]).md_unit_system)
    # md_unit_system uses nanometers for length; we want angstroms for ASE/SO3LR
    # Use explicit conversion instead.
    from openmm import unit as u
    positions_ang = [p.value_in_unit(u.angstrom) for p in fixer.positions]
    elements = [atom.element.symbol for atom in fixer.topology.atoms()]

    # Validate elements
    try:
        from ase.data import atomic_numbers
    except ImportError:
        # ASE not in env-mace; map manually for common organic atoms
        atomic_numbers = {"H": 1, "C": 6, "N": 7, "O": 8, "F": 9, "P": 15,
                          "S": 16, "Cl": 17}
    zs = [atomic_numbers.get(e, 0) for e in elements]
    zset = set(zs)
    unsupported = zset - ALLOWED_Z
    if unsupported:
        raise RuntimeError(
            f"Unsupported elements for SO3LR: {unsupported}. Aborting.")

    # Write extended-XYZ for ASE round-trip compatibility.
    with open(xyz_out, "w") as f:
        f.write(f"{len(elements)}\n")
        f.write(f'Properties=species:S:1:pos:R:3 pbc="F F F"\n')
        for e, (x, y, z) in zip(elements, positions_ang):
            f.write(f"{e:<2s}  {x:14.8f}  {y:14.8f}  {z:14.8f}\n")

    return len(elements), sum(1 for z in zs if z == 1)


def main():
    parser = argparse.ArgumentParser(description="SO3LR pilot protein prep")
    parser.add_argument("--proteins", nargs="+", default=list(PROTEIN_ALIASES),
                        help="Subset of proteins to prep (default: all 5)")
    parser.add_argument("--output-dir", required=True,
                        help="Root output dir for trajectories/so3lr_vacuum/<p>/")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing input.xyz")
    args = parser.parse_args()

    results = {}
    for p in args.proteins:
        if p not in PROTEIN_ALIASES:
            logger.error(f"Unknown protein {p}")
            sys.exit(1)
        cfg = PROTEIN_ALIASES[p]
        out_dir = Path(args.output_dir) / p
        out_dir.mkdir(parents=True, exist_ok=True)
        xyz_out = out_dir / "input.xyz"
        h_pdb_out = out_dir / "input_h.pdb"
        stripped_out = out_dir / "input_stripped.pdb"
        summary_out = out_dir / "prep_summary.json"

        if xyz_out.exists() and not args.force:
            logger.info(f"[{p}] XYZ already exists; use --force to overwrite")
            continue

        logger.info("=" * 60)
        logger.info(f"[{p}] Preparing from {cfg['pdb']}")
        logger.info("=" * 60)

        n_atoms_stripped, resids_kept = strip_pdb_to_chain_and_range(
            cfg["pdb"], cfg["chain"], cfg["resid_range"], str(stripped_out))
        logger.info(f"[{p}] After strip: {n_atoms_stripped} atoms over "
                    f"{len(resids_kept)} residues")

        n_atoms_h, n_hydrogens = add_hydrogens_and_write_xyz(
            str(stripped_out), str(xyz_out), str(h_pdb_out))
        logger.info(f"[{p}] After H: {n_atoms_h} atoms, {n_hydrogens} H")

        summary = {
            "protein": p,
            "pdb_in": cfg["pdb"],
            "chain": cfg["chain"],
            "resid_range": cfg["resid_range"],
            "n_atoms_stripped": n_atoms_stripped,
            "n_residues_kept": len(resids_kept),
            "n_atoms_hydrogenated": n_atoms_h,
            "n_hydrogens_added": n_hydrogens,
            "xyz": str(xyz_out),
            "h_pdb": str(h_pdb_out),
        }
        with open(summary_out, "w") as f:
            json.dump(summary, f, indent=2)
        results[p] = summary
        logger.info(f"[{p}] Wrote {xyz_out}  (heavy={n_atoms_h - n_hydrogens}, H={n_hydrogens})")

    # Write top-level summary
    top = Path(args.output_dir) / "prep_all_summary.json"
    if top.exists():
        with open(top) as f:
            existing = json.load(f)
        existing.update(results)
        results = existing
    with open(top, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"All prep summaries → {top}")


if __name__ == "__main__":
    sys.exit(main())
