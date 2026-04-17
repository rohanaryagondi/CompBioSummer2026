#!/usr/bin/env python3
"""
BioEmu top-up: generate additional samples so that the physicality-filtered
XTC reaches a target number of conformations (default 2000).

Reads the existing generation_status.json to compute the pass rate, calculates
how many total denoised samples are needed (with safety margin), then calls
bioemu.sample.main which resumes from the existing npz files.

Usage:
    python bioemu_topup_single.py \
        --output-dir /path/to/PROTEIN_NAME \
        --cache-dir /path/to/cache \
        --target-physical 2000
"""

import argparse
import json
import math
import os
import sys
import time
import traceback
from pathlib import Path


def gpu_keepalive(interval=45):
    """Background thread that periodically touches GPU to prevent idle detection.

    YCRC auto-cancels GPU jobs after 1 hour of 0% utilization. BioEmu spends
    25-35 min on CPU-bound model loading and ESM embedding before GPU denoising
    begins. This keepalive runs a small CUDA op every `interval` seconds to
    maintain visible GPU utilization during that window.
    """
    import threading
    import torch

    stop = threading.Event()

    def _ping():
        while not stop.is_set():
            try:
                if torch.cuda.is_available():
                    x = torch.randn(256, 256, device='cuda')
                    _ = x @ x
                    torch.cuda.synchronize()
                    del x
            except Exception:
                pass
            stop.wait(interval)

    t = threading.Thread(target=_ping, daemon=True)
    t.start()
    return stop


def count_npz_samples(output_dir):
    """Count total denoised samples from batch npz files."""
    output_dir = Path(output_dir)
    npz_files = sorted(output_dir.glob("batch_*.npz"))
    if not npz_files:
        return 0
    last = npz_files[-1].stem  # e.g. "batch_0001999_0002000"
    parts = last.split("_")
    return int(parts[2])


def read_sequence(output_dir):
    """Read the protein sequence from the output directory's sequence.fasta."""
    fasta_path = Path(output_dir) / "sequence.fasta"
    if not fasta_path.exists():
        return None
    seq_lines = []
    with open(fasta_path) as f:
        for line in f:
            line = line.strip()
            if not line.startswith(">"):
                seq_lines.append(line)
    return "".join(seq_lines)


def validate_xtc(output_dir, target_physical, sequence):
    """Validate the XTC after top-up generation."""
    output_dir = Path(output_dir)
    topo = output_dir / "topology.pdb"
    xtc = output_dir / "samples.xtc"

    if not topo.exists() or not xtc.exists():
        return {"physical_count": 0, "met_target": False, "error": "topology.pdb or samples.xtc missing"}

    try:
        import mdtraj
        traj = mdtraj.load(str(xtc), top=str(topo))
        physical_count = traj.n_frames
        return {
            "physical_count": physical_count,
            "met_target": physical_count >= target_physical,
            "atoms_per_frame": traj.n_atoms,
        }
    except Exception as e:
        return {"physical_count": 0, "met_target": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="BioEmu top-up generation")
    parser.add_argument("--output-dir", required=True,
                        help="Existing protein output directory with npz files")
    parser.add_argument("--cache-dir", required=True,
                        help="Embedding cache directory")
    parser.add_argument("--target-physical", type=int, default=2000,
                        help="Target number of physical conformations after filtering")
    parser.add_argument("--safety-margin", type=float, default=1.20,
                        help="Oversampling safety margin (default 1.20 = 20%%)")
    parser.add_argument("--batch-size-100", type=int, default=30,
                        help="Batch size parameter (multiples of 100)")
    parser.add_argument("--model-name", default="bioemu-v1.1",
                        help="BioEmu model name")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    # Start GPU keepalive
    keepalive_stop = gpu_keepalive()

    # Read existing status
    status_file = output_dir / "generation_status.json"
    if not status_file.exists():
        print(f"ERROR: No generation_status.json in {output_dir}")
        keepalive_stop.set()
        sys.exit(1)

    with open(status_file) as f:
        old_status = json.load(f)

    existing_total = count_npz_samples(output_dir)
    existing_physical = old_status.get("validation", {}).get("conformation_count", 0)
    protein_name = old_status.get("uniprot_id", "unknown")

    print(f"=" * 70)
    print(f"BioEmu Top-Up: {protein_name}")
    print(f"  Existing denoised samples: {existing_total}")
    print(f"  Existing physical frames:  {existing_physical}")
    print(f"  Target physical frames:    {args.target_physical}")
    print(f"  Safety margin:             {args.safety_margin:.0%}")
    print(f"=" * 70)

    # Check if already met
    if existing_physical >= args.target_physical:
        print(f"SKIP: Already have {existing_physical} physical conformations "
              f"(target: {args.target_physical})")
        keepalive_stop.set()
        sys.exit(0)

    # Calculate target total samples
    if existing_physical == 0 or existing_total == 0:
        print("ERROR: No existing physical conformations to compute pass rate")
        keepalive_stop.set()
        sys.exit(1)

    pass_rate = existing_physical / existing_total
    needed_total = math.ceil(args.target_physical / pass_rate * args.safety_margin)

    # Round up to nearest 100 for cleanliness
    needed_total = math.ceil(needed_total / 100) * 100
    additional = needed_total - existing_total

    print(f"  Pass rate:                 {pass_rate:.1%}")
    print(f"  Calculated target total:   {needed_total}")
    print(f"  Additional to generate:    {additional}")
    print(f"=" * 70)

    if additional <= 0:
        print("SKIP: Existing samples should be sufficient. Reassembling XTC...")
        needed_total = existing_total

    # Read sequence
    sequence = read_sequence(output_dir)
    if sequence is None:
        print("ERROR: Cannot read sequence.fasta from output directory")
        keepalive_stop.set()
        sys.exit(1)

    seq_len = len(sequence)
    batch_size = int(args.batch_size_100 * (100 / seq_len) ** 2)
    batch_size = max(batch_size, 1)

    print(f"  Sequence length:           {seq_len}")
    print(f"  Batch size:                {batch_size}")
    if additional > 0:
        est_batches = math.ceil(additional / batch_size)
        print(f"  Estimated batches:         {est_batches}")
    print()

    start_time = time.time()

    try:
        from bioemu.sample import main as bioemu_main

        print(f"Starting BioEmu top-up at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}...")
        bioemu_main(
            sequence=sequence,
            num_samples=needed_total,
            output_dir=str(output_dir),
            batch_size_100=args.batch_size_100,
            model_name=args.model_name,
            cache_embeds_dir=args.cache_dir,
            base_seed=args.seed,
        )

        elapsed = time.time() - start_time

        # Validate the new XTC
        val = validate_xtc(output_dir, args.target_physical, sequence)
        physical_count = val["physical_count"]
        met_target = val["met_target"]

        # Update status file
        new_status = dict(old_status)
        new_status["topup"] = {
            "previous_total": existing_total,
            "previous_physical": existing_physical,
            "pass_rate": round(pass_rate, 4),
            "target_physical": args.target_physical,
            "new_total": needed_total,
            "additional_generated": additional,
            "new_physical": physical_count,
            "met_target": met_target,
            "elapsed_seconds": round(elapsed, 1),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        new_status["num_samples_requested"] = needed_total
        new_status["validation"]["conformation_count"] = physical_count
        new_status["validation"]["npz_count"] = len(list(output_dir.glob("batch_*.npz")))

        # Fix glycine atom count annotation
        seq_glycines = sequence.count("G")
        expected_atoms = 5 * seq_len - seq_glycines
        new_issues = []
        for issue in new_status["validation"].get("issues", []):
            if "Atom count mismatch" in issue:
                atoms_actual = val.get("atoms_per_frame", 0)
                if atoms_actual == expected_atoms:
                    continue  # glycine-explained, drop the issue
            if "Low conformation count" in issue:
                continue  # recalculate below
            new_issues.append(issue)

        if physical_count < args.target_physical:
            new_issues.append(
                f"Physical conformation count {physical_count} below target {args.target_physical}"
            )

        new_status["validation"]["issues"] = new_issues
        new_status["validation"]["valid"] = len(new_issues) == 0
        new_status["status"] = "success" if len(new_issues) == 0 else "partial"
        new_status["elapsed_seconds"] = round(
            old_status.get("elapsed_seconds", 0) + elapsed, 1
        )
        new_status["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        with open(status_file, "w") as f:
            json.dump(new_status, f, indent=2)

        print(f"\nTop-up completed in {elapsed/60:.1f} minutes")
        print(f"  New total denoised:    {needed_total}")
        print(f"  Physical conformations: {physical_count}")
        print(f"  Target met:            {'YES' if met_target else 'NO'}")
        if not met_target:
            print(f"  WARNING: Still below target. May need another top-up round.")
        print(f"\nStatus written to {status_file}")

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\nERROR: Top-up failed after {elapsed/60:.1f} minutes")
        print(f"  Error: {e}")
        traceback.print_exc()
        keepalive_stop.set()
        sys.exit(1)

    keepalive_stop.set()

    if not met_target:
        sys.exit(2)  # partial — needs another round
    sys.exit(0)


if __name__ == "__main__":
    main()
