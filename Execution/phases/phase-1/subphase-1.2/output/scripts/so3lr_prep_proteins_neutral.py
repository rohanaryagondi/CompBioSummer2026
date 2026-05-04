#!/usr/bin/env python3
"""
SO3LR Pilot Preparation — Neutral Protonation Variant (Task 002 Rescue, Sub 1.2)

Parallel prep for the rescue campaign on GB3 and NTL9. Uses OpenMM Modeller
to assign per-residue protonation variants that yield net charge = 0:

  K (LYS, +1) → LYN (neutral, NH2 instead of NH3+)
  D (ASP, -1) → ASH (neutral, COOH instead of COO-)
  E (GLU, -1) → GLH (neutral, COOH instead of COO-)

H, C, R, Y handling: leave H unchanged (HID/HIE auto), C unchanged (CYS/CYX
auto for disulfides; not present in our proteins), R unchanged (no neutral
ARG variant in OpenMM standard data; no ARGs in GB3 or NTL9 chain A 1-56/1-51
respectively). Y unchanged (Tyr remains neutral).

This script runs INSIDE env-mace (which has openmm + pdbfixer + ase). The
output XYZ is consumed by SO3LR running in env-so3lr (separate env).

Run:
  conda activate env-mace
  python output/scripts/so3lr_prep_proteins_neutral.py \\
      --proteins gb3 ntl9 \\
      --output-dir output/trajectories/so3lr_vacuum_neutral

Outputs (per protein):
  output/trajectories/so3lr_vacuum_neutral/<p>/input_neutral.xyz
  output/trajectories/so3lr_vacuum_neutral/<p>/input_neutral_h.pdb
  output/trajectories/so3lr_vacuum_neutral/<p>/prep_neutral_summary.json
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
logger = logging.getLogger("so3lr_prep_proteins_neutral")

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

# Map of standard residue → variant for net-neutral protonation.
NEUTRAL_VARIANTS = {
    "LYS": "LYN",
    "ASP": "ASH",
    "GLU": "GLH",
}

# Standard formal charges at pH 7 (without variant overrides) for sanity check.
STD_FORMAL_CHARGE = {
    "LYS": +1, "ARG": +1, "HIS": 0,  # HIS treated as neutral (HID/HIE)
    "ASP": -1, "GLU": -1,
}

# Formal charge after applying our variants table.
VARIANT_FORMAL_CHARGE = {
    "LYS": 0,   # LYN
    "ARG": +1,  # unchanged
    "HIS": 0,
    "ASP": 0,   # ASH
    "GLU": 0,   # GLH
}


def strip_pdb_to_chain_and_range(pdb_in: str, chain: str, rng: tuple,
                                  pdb_out: str):
    """Write a stripped PDB with only chain `chain`, residues in `rng`,
    ATOM records only (no HETATM), first model only.

    Identical to the v1 prep behaviour for traceable comparison.
    """
    n_atoms_written = 0
    n_resid_kept = set()
    with open(pdb_in) as fin, open(pdb_out, "w") as fout:
        for line in fin:
            rec = line[:6].strip()
            if rec == "ENDMDL":
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


def neutralize_with_modeller(stripped_pdb: str, xyz_out: str, h_pdb_out: str,
                             protein: str):
    """Use OpenMM Modeller to add hydrogens with neutral variants for K/D/E.
    Writes XYZ for SO3LR and audit PDB.

    Returns dict with element / atom counts and net formal charge.
    """
    # Imports are inside the function so the module's `--help` works without
    # openmm/pdbfixer.
    from pdbfixer import PDBFixer
    from openmm.app import Modeller, ForceField, PDBFile
    from openmm import unit as u

    # We use PDBFixer first to fill missing residues / atoms, then move to
    # Modeller for variant-aware H addition.
    fixer = PDBFixer(filename=stripped_pdb)
    fixer.findMissingResidues()
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()

    # Strip any existing hydrogens from the fixer topology before handing
    # to Modeller; Modeller expects to add H itself with the chosen variants.
    # PDBFixer does not pre-add H by default after addMissingAtoms, but some
    # input PDBs (e.g., GB3 1P7E) ship hydrogens. We must remove them so
    # Modeller's variant logic picks the right protonation.
    modeller = Modeller(fixer.topology, fixer.positions)

    # Delete any pre-existing hydrogens.
    h_atoms = [a for a in modeller.topology.atoms() if a.element is not None
               and a.element.symbol == "H"]
    if h_atoms:
        logger.info(f"[{protein}] Removing {len(h_atoms)} pre-existing "
                    f"hydrogens before re-protonating with variants")
        modeller.delete(h_atoms)

    # Build the variants list — one entry per residue in the topology.
    # Modeller iterates residues in order; the variants list MUST be the same
    # length as topology.residues() generator output, with None for default
    # behaviour.
    variants_list = []
    variant_log = []  # for audit summary
    n_lys = n_asp = n_glu = n_arg = 0
    for r in modeller.topology.residues():
        rname = r.name.upper()
        if rname == "LYS":
            variants_list.append("LYN")
            variant_log.append((r.id, rname, "LYN"))
            n_lys += 1
        elif rname == "ASP":
            variants_list.append("ASH")
            variant_log.append((r.id, rname, "ASH"))
            n_asp += 1
        elif rname == "GLU":
            variants_list.append("GLH")
            variant_log.append((r.id, rname, "GLH"))
            n_glu += 1
        else:
            variants_list.append(None)
            if rname == "ARG":
                n_arg += 1

    # ARG safety check: if any ARGs are present, refuse to proceed since
    # OpenMM has no neutral ARG variant. WW has 3 ARGs (and is rescued via
    # the float64+dt path, not chemistry); GB3 and NTL9 have 0 ARGs by
    # design.
    if n_arg > 0:
        raise RuntimeError(
            f"[{protein}] Topology contains {n_arg} ARG residue(s). "
            f"OpenMM Modeller's standard hydrogens.xml has no neutral ARG "
            f"variant. The neutralization path is not safe for this protein. "
            f"Use the float64+dt rescue path for ARG-containing proteins, "
            f"or implement manual guanidinium hydrogen stripping post-prep.")

    logger.info(f"[{protein}] Variant assignment: "
                f"{n_lys} LYS→LYN, {n_asp} ASP→ASH, {n_glu} GLU→GLH "
                f"(0 ARG present; safe to proceed)")

    # Add hydrogens with explicit variants. We deliberately pass forcefield=None
    # so Modeller falls back to geometric H placement using the built-in
    # hydrogens.xml definitions. With forcefield=Amber14, the chain-terminal
    # residue cannot be matched by the standard residue templates without
    # registering an explicit terminal patch, which is unnecessary for our
    # purpose: SO3LR is a learned all-atom potential and will relax the H
    # geometry itself via --relax + --force-conv during MD startup.
    # Verified: produces correct H names for LYN (HZ1+HZ2 only, no HZ3),
    # ASH (HD2 added), GLH (HE2 added).
    modeller.addHydrogens(forcefield=None, pH=7.0, variants=variants_list)

    # Write hydrogenated PDB (audit trail).
    with open(h_pdb_out, "w") as f:
        PDBFile.writeFile(modeller.topology, modeller.positions, f, keepIds=True)

    # Compute net formal charge by inspecting the actual H-atom names per
    # residue. OpenMM's Modeller renames LYN/ASH/GLH BACK to LYS/ASP/GLU
    # after H placement (the variant is just a hydrogen-template selector,
    # not a residue-rename), so we cannot use the residue name alone to
    # determine charge. Instead we count specific protonation-state-defining
    # H atoms:
    #   LYS (charged, +1):  has HZ3 (3 ammonium hydrogens)
    #   LYN (neutral, 0):   missing HZ3 (only HZ1 + HZ2)
    #   ASP (charged, -1):  no HD2 acid hydrogen
    #   ASH (neutral, 0):   has HD2 acid hydrogen
    #   GLU (charged, -1):  no HE2 acid hydrogen
    #   GLH (neutral, 0):   has HE2 acid hydrogen
    #   ARG (charged, +1):  no neutral variant in OpenMM stdlib
    #   HIS (neutral by default in HID/HIE; +1 if HIP)
    # Termini are also explicitly counted: zwitterionic NH3+/COO- ends
    # contribute +1/-1 respectively. They cancel for a typical protein with
    # one chain, leaving the SIDE-CHAIN-ONLY rearrangement responsible for
    # net charge changes vs. the original.
    net_charge = 0
    side_chain_charge = 0
    residue_charge_breakdown = {}
    residues = list(modeller.topology.residues())
    for idx, r in enumerate(residues):
        rname = r.name.upper()
        h_names = {a.name for a in r.atoms() if a.element.symbol == "H"}
        atom_names = {a.name for a in r.atoms()}
        sc_ch = 0
        if rname == "LYS":
            sc_ch = +1 if "HZ3" in h_names else 0   # LYS=+1, LYN=0
        elif rname == "ASP":
            sc_ch = 0 if "HD2" in h_names else -1   # ASH=0, ASP=-1
        elif rname == "GLU":
            sc_ch = 0 if "HE2" in h_names else -1   # GLH=0, GLU=-1
        elif rname == "ARG":
            sc_ch = +1
        elif rname == "HIS":
            sc_ch = +1 if ("HD1" in h_names and "HE2" in h_names) else 0
        elif rname == "CYS":
            sc_ch = 0
        side_chain_charge += sc_ch
        cur = residue_charge_breakdown.get(rname, [0, 0])
        residue_charge_breakdown[rname] = [cur[0] + 1, cur[1] + sc_ch]

    # Termini handling (single-chain assumption; protein here has 1 chain)
    n_term = residues[0]
    n_term_hs = {a.name for a in n_term.atoms() if a.element.symbol == "H"}
    n_term_charge = +1 if ("H2" in n_term_hs and "H3" in n_term_hs) else 0

    c_term = residues[-1]
    c_term_atoms = {a.name for a in c_term.atoms()}
    c_term_charge = -1 if (
        "OXT" in c_term_atoms and "HXT" not in c_term_atoms
    ) else 0

    net_charge = side_chain_charge + n_term_charge + c_term_charge

    if net_charge != 0:
        raise RuntimeError(
            f"[{protein}] After variant assignment, net formal charge = "
            f"{net_charge:+d}  (side-chain={side_chain_charge:+d}, "
            f"N-term={n_term_charge:+d}, C-term={c_term_charge:+d}). "
            f"Expected 0. Breakdown: {residue_charge_breakdown}. Aborting.")

    logger.info(
        f"[{protein}] Net formal charge = {net_charge:+d} "
        f"(side-chain={side_chain_charge:+d}, N-term={n_term_charge:+d}, "
        f"C-term={c_term_charge:+d}). Verified via H-name inspection.")

    # Extract elements and positions in Angstrom.
    positions_ang = [p.value_in_unit(u.angstrom) for p in modeller.positions]
    elements = [atom.element.symbol for atom in modeller.topology.atoms()]

    # Validate elements vs SO3LR allowed set.
    try:
        from ase.data import atomic_numbers as ase_atomic_numbers
        atomic_numbers = ase_atomic_numbers
    except ImportError:
        atomic_numbers = {"H": 1, "C": 6, "N": 7, "O": 8, "F": 9, "P": 15,
                          "S": 16, "Cl": 17}
    zs = [atomic_numbers.get(e, 0) for e in elements]
    zset = set(zs)
    unsupported = zset - ALLOWED_Z
    if unsupported:
        raise RuntimeError(
            f"[{protein}] Unsupported elements for SO3LR: {unsupported}. "
            f"Aborting.")

    # Write extended-XYZ.
    with open(xyz_out, "w") as f:
        f.write(f"{len(elements)}\n")
        f.write(f'Properties=species:S:1:pos:R:3 pbc="F F F"\n')
        for e, (x, y, z) in zip(elements, positions_ang):
            f.write(f"{e:<2s}  {x:14.8f}  {y:14.8f}  {z:14.8f}\n")

    n_h = sum(1 for e in elements if e == "H")
    n_heavy = len(elements) - n_h

    return {
        "n_atoms": len(elements),
        "n_heavy": n_heavy,
        "n_hydrogens": n_h,
        "net_formal_charge": net_charge,
        "side_chain_charge": side_chain_charge,
        "n_term_charge": n_term_charge,
        "c_term_charge": c_term_charge,
        "n_lys_to_lyn": n_lys,
        "n_asp_to_ash": n_asp,
        "n_glu_to_glh": n_glu,
        "n_arg": n_arg,
        "variants_applied": variant_log,
    }


def main():
    parser = argparse.ArgumentParser(
        description="SO3LR rescue prep — neutral protonation (LYN/ASH/GLH)")
    parser.add_argument("--proteins", nargs="+", default=["gb3", "ntl9"],
                        help="Subset of proteins to prep (default: gb3 ntl9)")
    parser.add_argument("--output-dir", required=True,
                        help="Root output dir for trajectories/<p>/")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing input_neutral.xyz")
    args = parser.parse_args()

    results = {}
    for p in args.proteins:
        if p not in PROTEIN_ALIASES:
            logger.error(f"Unknown protein {p}")
            sys.exit(1)
        cfg = PROTEIN_ALIASES[p]
        out_dir = Path(args.output_dir) / p
        out_dir.mkdir(parents=True, exist_ok=True)
        xyz_out = out_dir / "input_neutral.xyz"
        h_pdb_out = out_dir / "input_neutral_h.pdb"
        stripped_out = out_dir / "input_stripped.pdb"
        summary_out = out_dir / "prep_neutral_summary.json"

        if xyz_out.exists() and not args.force:
            logger.info(f"[{p}] Neutral XYZ already exists; use --force to "
                        f"overwrite")
            continue

        logger.info("=" * 60)
        logger.info(f"[{p}] Neutral-protonation prep from {cfg['pdb']}")
        logger.info("=" * 60)

        n_atoms_stripped, resids_kept = strip_pdb_to_chain_and_range(
            cfg["pdb"], cfg["chain"], cfg["resid_range"], str(stripped_out))
        logger.info(f"[{p}] After strip: {n_atoms_stripped} atoms over "
                    f"{len(resids_kept)} residues")

        neutralize_result = neutralize_with_modeller(
            str(stripped_out), str(xyz_out), str(h_pdb_out), p)
        logger.info(f"[{p}] After neutral protonation: "
                    f"{neutralize_result['n_atoms']} atoms "
                    f"({neutralize_result['n_heavy']} heavy + "
                    f"{neutralize_result['n_hydrogens']} H), "
                    f"net charge = {neutralize_result['net_formal_charge']:+d}")

        summary = {
            "protein": p,
            "pdb_in": cfg["pdb"],
            "chain": cfg["chain"],
            "resid_range": cfg["resid_range"],
            "n_atoms_stripped": n_atoms_stripped,
            "n_residues_kept": len(resids_kept),
            "xyz": str(xyz_out),
            "h_pdb": str(h_pdb_out),
            "approach": "OpenMM Modeller + Amber14 with per-residue variants",
            "variants": "K→LYN, D→ASH, E→GLH (0 ARG present)",
            **neutralize_result,
        }
        # variants_applied list -> simple JSON-friendly form
        summary["variants_applied"] = [
            {"resid": r, "from": fr, "to": to}
            for (r, fr, to) in neutralize_result["variants_applied"]
        ]
        with open(summary_out, "w") as f:
            json.dump(summary, f, indent=2)
        results[p] = summary
        logger.info(f"[{p}] Wrote {xyz_out}  "
                    f"(heavy={neutralize_result['n_heavy']}, "
                    f"H={neutralize_result['n_hydrogens']}, "
                    f"net charge=0)")

    # Write top-level summary
    top = Path(args.output_dir) / "prep_neutral_all_summary.json"
    if top.exists():
        with open(top) as f:
            existing = json.load(f)
        existing.update(results)
        results = existing
    with open(top, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"All neutral prep summaries → {top}")


if __name__ == "__main__":
    sys.exit(main())
