#!/usr/bin/env python3
"""
SO3LR Vacuum NVT Pilot Runner (Task 002, Subphase 1.2)

Parameterized runner that invokes the `so3lr nvt` CLI on one of five Tier A/B
proteins to produce a 5 ns vacuum NVT trajectory. This is the Sub 1.2 successor
to so3lr_crambin_nvt.py from Sub 1.1, which pre-dated the D1-PASS lesson
("use CLI, not programmatic JAX-MD"). Accordingly, this runner delegates the
actual MD to the SO3LR CLI via subprocess.

Supported proteins:
  --protein ww    : Pin1 WW domain, residues 6-39 (crop from full Pin1)
  --protein gb3   : Protein G B3 domain, residues 1-56
  --protein gb1   : Protein G B1 domain, residues 1-56
  --protein ntl9  : NTL9, residues 1-51
  --protein ubq   : Ubiquitin, residues 1-76

Modes:
  --mode prepare-only   : Only convert PDB → XYZ (stage 1). Skip MD.
  --mode run            : Prepare XYZ if needed AND run 5 ns NVT via CLI.
  --mode restart        : Resume from last checkpoint (--no-relax).

Usage:
  # First-run (fresh 5 ns):
  python so3lr_pilot_runner.py --protein ww --mode run --target-ns 5.0

  # Resume after SLURM walltime:
  python so3lr_pilot_runner.py --protein ww --mode restart

Output structure:
  output/trajectories/so3lr_vacuum/<protein>/
      input.xyz                    # vacuum XYZ (H-stripped, chain A, range applied)
      input_h.xyz                  # with hydrogens (optional, not required)
      stageA.hdf5                  # SO3LR CLI trajectory (first run)
      stageA.log                   # SO3LR CLI log (stdout captured)
      stageA_checkpoint.npz        # SO3LR restart checkpoint
      stageB.hdf5, ...             # Restart continuations (if any)
      state.log                    # Parsed per-frame: step, t_ps, T, PE, H

Env contract (per shared/notes/1.1-so3lr-crambin.md):
  conda activate env-so3lr
  export PYTHONNOUSERSITE=1   # Critical -- numpy must be conda's, not user-site
  The SLURM sbatch sets this before invoking the runner.
"""

import os
import sys
import time
import json
import math
import argparse
import logging
import subprocess
import threading
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("so3lr_pilot_runner")

# ---------------------------------------------------------------------------
# Protein registry (short_name → PDB file + optional residue crop)
# ---------------------------------------------------------------------------
# Manifest authoritative paths (from phases/phase-0/subphase-0.1/proteins/manifest.json).
# Only 5 target proteins for this task.
REPO_ROOT = "/home/rag88/projects/CompBioSummer2026"
PROTEIN_DIR = f"{REPO_ROOT}/Execution/phases/phase-0/subphase-0.1/proteins"
MANIFEST_PATH = f"{PROTEIN_DIR}/manifest.json"

PROTEIN_ALIASES = {
    "ww": {
        "pdb": f"{PROTEIN_DIR}/ww.pdb",
        "chain": "A",
        "resid_range": (6, 39),   # Pin1 WW crop (manifest residue_range)
        "residue_count": 34,
    },
    "gb3": {
        "pdb": f"{PROTEIN_DIR}/gb3.pdb",
        "chain": "A",
        "resid_range": (1, 56),
        "residue_count": 56,
    },
    "gb1": {
        "pdb": f"{PROTEIN_DIR}/gb1.pdb",
        "chain": "A",
        "resid_range": (1, 56),
        "residue_count": 56,
    },
    "ntl9": {
        "pdb": f"{PROTEIN_DIR}/ntl9.pdb",
        "chain": "A",
        "resid_range": (1, 51),
        "residue_count": 51,
    },
    "ubq": {
        "pdb": f"{PROTEIN_DIR}/ubq.pdb",
        "chain": "A",
        "resid_range": (1, 76),
        "residue_count": 76,
    },
}

# SO3LR supports these atomic numbers (from shared/notes/1.1-so3lr-crambin.md).
ALLOWED_Z = {1, 6, 7, 8, 9, 15, 16, 17}  # H, C, N, O, F, P, S, Cl


# ---------------------------------------------------------------------------
# GPU keepalive (per operational-practices.md)
# ---------------------------------------------------------------------------
def start_gpu_keepalive(interval_sec=300):
    """Daemon thread that exercises the GPU every 5 min to prevent YCRC
    1-hour auto-cancel during CPU-heavy startup or long MD runs.

    Uses JAX (already imported by so3lr CLI; matmul is free of side effects).
    """
    def _tick():
        import jax
        import jax.numpy as jnp
        logger.info(f"[keepalive] thread started, interval={interval_sec}s")
        while True:
            try:
                a = jnp.ones((64, 64), dtype=jnp.float32)
                _ = jax.block_until_ready(a @ a)
                logger.info("[keepalive] tick (matmul OK)")
            except Exception as e:
                logger.warning(f"[keepalive] tick failed: {e}")
            time.sleep(interval_sec)

    t = threading.Thread(target=_tick, daemon=True, name="gpu_keepalive")
    t.start()
    return t


# ---------------------------------------------------------------------------
# PDB → XYZ preparation
# ---------------------------------------------------------------------------
def prepare_xyz_from_pdb(pdb_path: str,
                         chain: str,
                         resid_range: tuple,
                         xyz_out: str,
                         protein_name: str):
    """Read a PDB, select chain + residue range, strip waters/ions/HETATM,
    optionally add hydrogens (if pdbfixer available), then write an XYZ.

    Uses ASE (always available in env-so3lr). Hydrogens must already be present
    in the PDB for stable MLFF dynamics; if they are not, we warn but continue.
    """
    from ase import Atoms
    from ase.io import write as ase_write

    logger.info(f"Preparing XYZ for {protein_name} from {pdb_path}")
    logger.info(f"  chain={chain}  resid_range={resid_range}")

    # Lightweight PDB parser: filter ATOM records, keep hydrogens if present.
    elements = []
    positions = []
    kept_resids = set()
    skipped_hetatm = 0
    has_hydrogens = False
    skipped_nonchain = 0

    with open(pdb_path) as f:
        for line in f:
            if line.startswith("ENDMDL"):
                # Only keep the first model (NMR structures have multiple)
                if positions:
                    break
                continue
            if not (line.startswith("ATOM") or line.startswith("HETATM")):
                continue
            record = line[:6].strip()
            if record == "HETATM":
                skipped_hetatm += 1
                continue

            ch = line[21:22].strip()
            if ch and chain and ch != chain:
                skipped_nonchain += 1
                continue

            try:
                resid = int(line[22:26].strip())
            except ValueError:
                continue

            if resid_range is not None:
                lo, hi = resid_range
                if resid < lo or resid > hi:
                    continue
            kept_resids.add(resid)

            # Element column (cols 77-78, 1-indexed 77-78 → python 76:78). PDB spec.
            elem = line[76:78].strip()
            if not elem:
                # Fall back to the first letter of the atom name (cols 13-14).
                atom_name = line[12:16].strip()
                # Strip leading digits; use first letter
                stripped = atom_name.lstrip("0123456789")
                elem = stripped[0] if stripped else ""
            elem = elem.capitalize()
            if elem == "H":
                has_hydrogens = True
            try:
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
            except ValueError:
                continue
            elements.append(elem)
            positions.append([x, y, z])

    if not elements:
        raise RuntimeError(
            f"No atoms kept from {pdb_path} (chain={chain} range={resid_range}). "
            f"Aborting.")

    n_atoms = len(elements)
    n_residues = len(kept_resids)
    logger.info(
        f"  parsed {n_atoms} atoms across {n_residues} residues "
        f"(skipped {skipped_hetatm} HETATM, {skipped_nonchain} non-chain)")
    logger.info(f"  has_hydrogens: {has_hydrogens}")

    # Validate all elements are SO3LR-supported.
    from ase.data import atomic_numbers
    bad = []
    zs = []
    for e in elements:
        if e not in atomic_numbers:
            bad.append(e)
            zs.append(0)
        else:
            zs.append(atomic_numbers[e])

    if bad:
        logger.error(f"Unknown element symbols in PDB: {set(bad)}")
        sys.exit(1)

    zset = set(zs)
    unsupported = zset - ALLOWED_Z
    if unsupported:
        logger.error(
            f"PDB contains elements not supported by SO3LR: {unsupported}. "
            f"SO3LR supports Z in {ALLOWED_Z}.")
        sys.exit(1)

    atoms = Atoms(symbols=elements, positions=positions, cell=None, pbc=False)

    if not has_hydrogens:
        logger.warning(
            f"{protein_name}: PDB has NO hydrogens. SO3LR is an all-atom "
            f"potential and expects H. Attempting to add hydrogens with "
            f"openmm+pdbfixer if available; otherwise trajectory will start "
            f"from heavy-atom-only geometry (will likely fail in relax).")
        # Try pdbfixer path
        try:
            _add_hydrogens_with_pdbfixer(pdb_path, chain, resid_range, xyz_out,
                                          protein_name)
            return
        except ImportError:
            logger.warning("pdbfixer/openmm not available -- writing heavy-atom XYZ")

    Path(xyz_out).parent.mkdir(parents=True, exist_ok=True)
    ase_write(xyz_out, atoms, format="xyz")
    logger.info(f"  wrote {xyz_out} ({n_atoms} atoms)")
    return xyz_out


def _add_hydrogens_with_pdbfixer(pdb_path, chain, resid_range, xyz_out, protein_name):
    """Optional branch: add hydrogens via pdbfixer. Only invoked if pdbfixer
    is importable in env-so3lr (rare; usually env-mace has it)."""
    from pdbfixer import PDBFixer
    from openmm.app import PDBFile
    from ase.io import read as ase_read, write as ase_write
    tmp_in = f"{xyz_out}.tmp_stripped.pdb"
    tmp_out = f"{xyz_out}.tmp_h.pdb"
    # Strip to chain+range first
    with open(pdb_path) as fin, open(tmp_in, "w") as fout:
        for line in fin:
            if line.startswith("ENDMDL"):
                break
            if not line.startswith("ATOM"):
                continue
            ch = line[21:22].strip()
            if ch and chain and ch != chain:
                continue
            try:
                resid = int(line[22:26].strip())
            except ValueError:
                continue
            if resid_range is not None:
                lo, hi = resid_range
                if resid < lo or resid > hi:
                    continue
            fout.write(line)
        fout.write("END\n")
    fixer = PDBFixer(filename=tmp_in)
    fixer.findMissingResidues()
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(pH=7.0)
    PDBFile.writeFile(fixer.topology, fixer.positions, open(tmp_out, "w"),
                      keepIds=True)
    atoms = ase_read(tmp_out)
    Path(xyz_out).parent.mkdir(parents=True, exist_ok=True)
    ase_write(xyz_out, atoms, format="xyz")
    logger.info(f"  pdbfixer+H → {xyz_out} ({len(atoms)} atoms)")
    os.remove(tmp_in)


# ---------------------------------------------------------------------------
# SO3LR CLI invocation
# ---------------------------------------------------------------------------
def run_so3lr_nvt(input_xyz: str,
                  out_dir: str,
                  protein: str,
                  target_ns: float,
                  temperature_k: float,
                  dt_fs: float,
                  relax: bool,
                  restart_from: str = None):
    """Invoke the `so3lr nvt` CLI as a subprocess.

    md-cycles × md-steps × dt = total time
    We use md-steps = 1000 (per cycle), dt = 0.5 fs → 0.5 ps / cycle.
    md-cycles = target_ns * 2000  (e.g., 5 ns = 10,000 cycles)
    """
    cycles = int(round(target_ns * 1000.0 / (dt_fs * 1000 / 1000.0)))
    # For dt=0.5, md-steps=1000: cycle = 0.5 ps. 5 ns = 10,000 cycles.
    # Re-derive to be explicit:
    ps_per_cycle = dt_fs * 1000 / 1000.0  # 0.5 fs × 1000 steps = 500 fs = 0.5 ps
    cycles = int(round(target_ns * 1000.0 / ps_per_cycle))  # 10,000 for 5 ns
    logger.info(f"Target {target_ns} ns → {cycles} cycles × 1000 steps × {dt_fs} fs")

    stage = "B" if restart_from else "A"
    output_hdf5 = os.path.join(out_dir, f"stage{stage}.hdf5")
    log_file = os.path.join(out_dir, f"stage{stage}.log")
    checkpoint = os.path.join(out_dir, f"stage{stage}_checkpoint.npz")

    cmd = [
        "so3lr", "nvt",
        "--input", input_xyz,
        "--output", output_hdf5,
        "--dt", str(dt_fs),
        "--temperature", str(temperature_k),
        "--md-cycles", str(cycles),
        "--md-steps", "1000",
        "--precision", "float32",
        "--lr-cutoff", "12.0",
        "--save-buffer", "50",
        "--log-file", log_file,
        "--restart-save", checkpoint,
        "--seed", "42",
    ]

    if relax:
        cmd += ["--relax", "--force-conv", "0.05"]
    else:
        cmd += ["--no-relax"]

    if restart_from:
        cmd += ["--restart-load", restart_from]

    logger.info("Invoking SO3LR CLI:")
    logger.info("  " + " \\\n  ".join(cmd))

    # Start the keepalive thread BEFORE the subprocess -- JAX needs to be
    # imported here so the thread can use it.
    keepalive_thread = start_gpu_keepalive()

    t0 = time.time()
    try:
        result = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except KeyboardInterrupt:
        logger.error("Interrupted")
        raise
    wall = time.time() - t0

    logger.info(f"SO3LR CLI exit code: {result.returncode}  wall={wall:.1f}s")

    # Write stdout to file
    stdout_path = os.path.join(out_dir, f"stage{stage}_stdout.txt")
    with open(stdout_path, "w") as f:
        f.write(result.stdout or "")

    return {
        "returncode": result.returncode,
        "wall_seconds": wall,
        "log_file": log_file,
        "checkpoint": checkpoint,
        "output_hdf5": output_hdf5,
        "stage": stage,
        "cycles_requested": cycles,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="SO3LR vacuum NVT pilot runner")
    parser.add_argument("--protein", choices=list(PROTEIN_ALIASES.keys()),
                        required=True, help="Target protein short-name")
    parser.add_argument("--mode", choices=["prepare-only", "run", "restart"],
                        default="run", help="Workflow mode")
    parser.add_argument("--target-ns", type=float, default=5.0,
                        help="Target trajectory length in ns (default 5.0)")
    parser.add_argument("--temperature", type=float, default=300.0)
    parser.add_argument("--dt-fs", type=float, default=0.5)
    parser.add_argument("--output-dir", required=True,
                        help="Root output directory. Per-protein subdir "
                             "will be created.")
    parser.add_argument("--restart-from", default=None,
                        help="Checkpoint .npz to restart from (required for "
                             "--mode restart)")
    args = parser.parse_args()

    protein = args.protein
    cfg = PROTEIN_ALIASES[protein]

    protein_out = os.path.join(args.output_dir, protein)
    Path(protein_out).mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info(f"SO3LR Pilot Runner -- protein={protein}  mode={args.mode}")
    logger.info(f"  output_dir = {protein_out}")
    logger.info(f"  target_ns = {args.target_ns}")
    logger.info("=" * 60)

    # Stage 1: Prepare XYZ from PDB
    xyz_path = os.path.join(protein_out, "input.xyz")
    if not os.path.exists(xyz_path):
        prepare_xyz_from_pdb(
            cfg["pdb"], cfg["chain"], cfg["resid_range"], xyz_path, protein)
    else:
        logger.info(f"XYZ already exists: {xyz_path} (skipping prep)")

    if args.mode == "prepare-only":
        logger.info("Mode=prepare-only → done after XYZ prep.")
        return 0

    # Stage 2: Run SO3LR nvt CLI
    relax = (args.mode == "run")
    restart_checkpoint = args.restart_from
    if args.mode == "restart":
        if not restart_checkpoint:
            # Auto-find latest stageA_checkpoint.npz
            candidates = sorted(Path(protein_out).glob("stage*_checkpoint.npz"),
                                key=lambda p: p.stat().st_mtime)
            if not candidates:
                logger.error("Mode=restart but no checkpoint found. Aborting.")
                return 2
            restart_checkpoint = str(candidates[-1])
            logger.info(f"Auto-restart from: {restart_checkpoint}")

    result = run_so3lr_nvt(
        input_xyz=xyz_path,
        out_dir=protein_out,
        protein=protein,
        target_ns=args.target_ns,
        temperature_k=args.temperature,
        dt_fs=args.dt_fs,
        relax=relax,
        restart_from=restart_checkpoint,
    )

    # Dump a summary file for HeadAI consumption.
    summary = {
        "protein": protein,
        "mode": args.mode,
        "target_ns": args.target_ns,
        "temperature_k": args.temperature,
        "dt_fs": args.dt_fs,
        "cycles_requested": result["cycles_requested"],
        "stage": result["stage"],
        "cli_returncode": result["returncode"],
        "wall_seconds": result["wall_seconds"],
        "output_hdf5": result["output_hdf5"],
        "log_file": result["log_file"],
        "checkpoint": result["checkpoint"],
    }
    summary_path = os.path.join(protein_out, "run_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Wrote run summary: {summary_path}")

    return result["returncode"]


if __name__ == "__main__":
    sys.exit(main())
