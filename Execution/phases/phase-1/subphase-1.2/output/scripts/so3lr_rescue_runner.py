#!/usr/bin/env python3
"""
SO3LR Vacuum NVT Rescue Runner (Task 002 Rescue, Subphase 1.2)

Fork of so3lr_pilot_runner.py with the following additions for the rescue
campaign on WW (numerical fix), GB3, and NTL9 (chemistry fix):

  --precision {float32, float64}   pass-through to SO3LR CLI
  --dt-fs                           pass-through (allows 0.25 fs for WW)
  --nhc-chain                       pass-through (NHC chain length)
  --nhc-thermo                      pass-through (Tdamp in dt units)
  --input-xyz                       absolute path override (allows
                                    using neutral-protonation XYZ for
                                    GB3 / NTL9 without re-prepping)

The runner still:
  - Auto-prepares from PDB (--mode prepare-only / run) using the v1
    pilot prep when --input-xyz is NOT supplied.
  - Auto-restarts from the latest stage*_checkpoint.npz when --mode restart.
  - Spawns a GPU keepalive thread before invoking the CLI.

Targets (per the rescue plan):
  - WW   gate: --precision float64 --dt-fs 0.25 --nhc-chain 5 --nhc-thermo 200
                  --target-ns 0.5
  - GB3  gate: (uses neutral XYZ) --precision float32 --dt-fs 0.5 --nhc-chain 3
                  --nhc-thermo 100 --target-ns 0.5
  - NTL9 gate: same as GB3, using NTL9 neutral XYZ
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("so3lr_rescue_runner")

REPO_ROOT = "/home/rag88/projects/CompBioSummer2026"
PROTEIN_DIR = f"{REPO_ROOT}/Execution/phases/phase-0/subphase-0.1/proteins"

PROTEIN_ALIASES = {
    "ww":   {"pdb": f"{PROTEIN_DIR}/ww.pdb",   "chain": "A",
             "resid_range": (6, 39), "residue_count": 34},
    "gb3":  {"pdb": f"{PROTEIN_DIR}/gb3.pdb",  "chain": "A",
             "resid_range": (1, 56), "residue_count": 56},
    "gb1":  {"pdb": f"{PROTEIN_DIR}/gb1.pdb",  "chain": "A",
             "resid_range": (1, 56), "residue_count": 56},
    "ntl9": {"pdb": f"{PROTEIN_DIR}/ntl9.pdb", "chain": "A",
             "resid_range": (1, 51), "residue_count": 51},
    "ubq":  {"pdb": f"{PROTEIN_DIR}/ubq.pdb",  "chain": "A",
             "resid_range": (1, 76), "residue_count": 76},
}

ALLOWED_Z = {1, 6, 7, 8, 9, 15, 16, 17}


def start_gpu_keepalive(interval_sec=300):
    """Daemon thread that exercises the GPU every 5 min to prevent YCRC
    1-hour auto-cancel. Exact pattern from so3lr_pilot_runner.py."""
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


def run_so3lr_nvt(input_xyz: str,
                  out_dir: str,
                  protein: str,
                  target_ns: float,
                  temperature_k: float,
                  dt_fs: float,
                  precision: str,
                  nhc_chain: int,
                  nhc_thermo: float,
                  relax: bool,
                  restart_from: str = None):
    """Invoke the `so3lr nvt` CLI with rescue-specific knobs."""
    # Throughput optimizations (per subagent B 2026-05-03 + audit 2026-05-03):
    # - md-steps 1000 → 10000: fewer fori_loop re-entries; 10× less Python overhead
    # - buffer-sr / buffer-lr: REVERTED to SO3LR defaults (1.25 / 1.25) per audit.
    #   The 1.15/1.10 was SO3LR's own "after equilibration" recommendation, but
    #   MODE=run starts fresh from t=0 — risk of silent NL underflow during
    #   pre-equilibration phase. Auditor flagged as silent failure mode.
    md_steps = 10000
    ps_per_cycle = dt_fs * md_steps / 1000.0  # bug fix: was hardcoded 1000
    cycles = int(round(target_ns * 1000.0 / ps_per_cycle))
    logger.info(f"Target {target_ns} ns at dt={dt_fs} fs → {cycles} cycles "
                f"× {md_steps} steps ({ps_per_cycle:.2f} ps/cycle)")

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
        "--md-steps", str(md_steps),
        "--precision", precision,
        "--lr-cutoff", "12.0",
        # buffer-sr / buffer-lr defaulted to SO3LR's 1.25 / 1.25 (safe-from-t=0).
        # Aggressive buffers (1.15/1.10) only valid after equilibration; can
        # silently NL-underflow during pre-equil → drift toward NaN.
        "--save-buffer", "5",   # with md_steps=10000, write cadence preserved (~25 ps)
        "--nhc-chain", str(nhc_chain),
        "--nhc-thermo", str(nhc_thermo),
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

    keepalive_thread = start_gpu_keepalive()

    # If precision=float64, also export JAX_ENABLE_X64=True. SO3LR's CLI
    # honors --precision but several downstream JAX ops only enable 64-bit
    # math when JAX_ENABLE_X64=True is in the environment.
    env = os.environ.copy()
    if precision == "float64":
        env["JAX_ENABLE_X64"] = "True"
        logger.info("[rescue] JAX_ENABLE_X64=True set for float64 mode")

    t0 = time.time()
    try:
        result = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
        )
    except KeyboardInterrupt:
        logger.error("Interrupted")
        raise
    wall = time.time() - t0

    logger.info(f"SO3LR CLI exit code: {result.returncode}  wall={wall:.1f}s")

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
        "precision": precision,
        "dt_fs": dt_fs,
        "nhc_chain": nhc_chain,
        "nhc_thermo": nhc_thermo,
    }


def main():
    parser = argparse.ArgumentParser(
        description="SO3LR vacuum NVT rescue runner")
    parser.add_argument("--protein", choices=list(PROTEIN_ALIASES.keys()),
                        required=True)
    parser.add_argument("--mode", choices=["run", "restart"], default="run")
    parser.add_argument("--target-ns", type=float, default=0.5,
                        help="Target trajectory length in ns (default 0.5)")
    parser.add_argument("--temperature", type=float, default=300.0)
    parser.add_argument("--dt-fs", type=float, default=0.5)
    parser.add_argument("--precision", choices=["float32", "float64"],
                        default="float32")
    parser.add_argument("--nhc-chain", type=int, default=3)
    parser.add_argument("--nhc-thermo", type=float, default=100.0,
                        help="Thermostat damping factor in dt units "
                             "(actual damping = dt × nhc_thermo)")
    parser.add_argument("--input-xyz", default=None,
                        help="Override XYZ path (e.g., neutral-prepped XYZ "
                             "for GB3/NTL9). If omitted, uses default "
                             "<output-dir>/<protein>/input.xyz.")
    parser.add_argument("--output-dir", required=True,
                        help="Root output directory. Per-protein subdir "
                             "will be created.")
    parser.add_argument("--restart-from", default=None,
                        help="Checkpoint .npz to restart from")
    args = parser.parse_args()

    protein = args.protein
    cfg = PROTEIN_ALIASES[protein]

    protein_out = os.path.join(args.output_dir, protein)
    Path(protein_out).mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info(f"SO3LR Rescue Runner -- protein={protein}  mode={args.mode}")
    logger.info(f"  output_dir = {protein_out}")
    logger.info(f"  target_ns  = {args.target_ns}")
    logger.info(f"  dt_fs      = {args.dt_fs}")
    logger.info(f"  precision  = {args.precision}")
    logger.info(f"  nhc_chain  = {args.nhc_chain}")
    logger.info(f"  nhc_thermo = {args.nhc_thermo}")
    logger.info("=" * 60)

    # Resolve input XYZ
    if args.input_xyz:
        xyz_path = args.input_xyz
        if not os.path.exists(xyz_path):
            logger.error(f"Provided --input-xyz does not exist: {xyz_path}")
            return 2
        logger.info(f"Using override XYZ: {xyz_path}")
    else:
        xyz_path = os.path.join(protein_out, "input.xyz")
        if not os.path.exists(xyz_path):
            logger.error(
                f"Default XYZ not found: {xyz_path}. Run the v1 pilot prep "
                f"first, or supply --input-xyz.")
            return 2
        logger.info(f"Using default XYZ: {xyz_path}")

    relax = (args.mode == "run")
    restart_checkpoint = args.restart_from
    if args.mode == "restart" and not restart_checkpoint:
        candidates = sorted(Path(protein_out).glob("stage*_checkpoint.npz"),
                            key=lambda p: p.stat().st_mtime)
        if not candidates:
            logger.error("Mode=restart but no checkpoint found.")
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
        precision=args.precision,
        nhc_chain=args.nhc_chain,
        nhc_thermo=args.nhc_thermo,
        relax=relax,
        restart_from=restart_checkpoint,
    )

    summary = {
        "protein": protein,
        "mode": args.mode,
        "target_ns": args.target_ns,
        "temperature_k": args.temperature,
        "input_xyz": xyz_path,
        **result,
    }
    summary_path = os.path.join(protein_out, "run_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Wrote run summary: {summary_path}")

    return result["returncode"]


if __name__ == "__main__":
    sys.exit(main())
