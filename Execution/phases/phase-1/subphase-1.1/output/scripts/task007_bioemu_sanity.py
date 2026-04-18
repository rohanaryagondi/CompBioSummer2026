#!/usr/bin/env python3
"""
BioEmu sanity-check generation for the 4 new T5-margin proteins + Crambin.

Usage:
    python task007_bioemu_sanity.py --short-name ntl9 --sequence MKVIF... \
        --output-dir /path/to/task-007-ntl9 --cache-dir /path/to/cache \
        --num-samples 100

Generates a small (100-conformation) BioEmu ensemble for a single protein, with
GPU keepalive. Validates output and writes generation_status.json.

Based on phases/phase-1/subphase-1.1/output/scripts/bioemu_generate_single.py.
"""

import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path


def gpu_keepalive(interval=45):
    """Background thread that periodically touches GPU to prevent idle detection.

    YCRC auto-cancels GPU jobs after 1 hour of 0% utilization. BioEmu spends
    time on CPU-bound loading before GPU denoising begins. This keepalive
    runs a small CUDA op every `interval` seconds to maintain GPU util visibility.
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


def validate_output(output_dir, num_samples, seq_len, sequence):
    """Validate BioEmu output."""
    output_dir = Path(output_dir)
    issues = []

    topo = output_dir / "topology.pdb"
    if not topo.exists() or topo.stat().st_size == 0:
        issues.append("topology.pdb missing or empty")

    xtc = output_dir / "samples.xtc"
    if not xtc.exists() or xtc.stat().st_size == 0:
        issues.append("samples.xtc missing or empty")

    npz_files = sorted(output_dir.glob("batch_*.npz"))
    if len(npz_files) == 0:
        issues.append("No batch_*.npz files found")

    conformation_count = None
    pass_rate = None
    if xtc.exists() and topo.exists():
        try:
            import mdtraj
            traj = mdtraj.load(str(xtc), top=str(topo))
            conformation_count = traj.n_frames
            atoms_per_frame = traj.n_atoms
            num_glycines = sequence.count('G')
            expected_atoms = 5 * seq_len - num_glycines
            if atoms_per_frame != expected_atoms:
                issues.append(
                    f"Atom count mismatch: got {atoms_per_frame}, "
                    f"expected {expected_atoms} (5*{seq_len} - {num_glycines} G)"
                )
            pass_rate = conformation_count / num_samples
        except Exception as e:
            issues.append(f"mdtraj validation failed: {e}")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "npz_count": len(npz_files),
        "conformation_count": conformation_count,
        "pass_rate": pass_rate,
    }


def main():
    parser = argparse.ArgumentParser(description="BioEmu sanity check single protein")
    parser.add_argument("--short-name", required=True)
    parser.add_argument("--sequence", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--cache-dir", required=True)
    parser.add_argument("--num-samples", type=int, default=100)
    parser.add_argument("--batch-size-100", type=int, default=10)
    parser.add_argument("--model-name", default="bioemu-v1.1")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    keepalive_stop = gpu_keepalive()

    sequence = args.sequence.strip().upper()
    seq_len = len(sequence)

    print("=" * 70)
    print(f"BioEmu Sanity Check: {args.short_name}")
    print(f"  Seq length: {seq_len}")
    print(f"  Num samples: {args.num_samples}")
    print(f"  Output: {args.output_dir}")
    print(f"  Cache: {args.cache_dir}")
    print(f"  Model: {args.model_name}")
    print("=" * 70)

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.cache_dir, exist_ok=True)

    status = {
        "short_name": args.short_name,
        "sequence": sequence,
        "sequence_length": seq_len,
        "num_samples_requested": args.num_samples,
        "model_name": args.model_name,
        "seed": args.seed,
    }

    t0 = time.time()
    status["start_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    try:
        from bioemu.sample import main as bioemu_main
        bioemu_main(
            sequence=sequence,
            num_samples=args.num_samples,
            output_dir=args.output_dir,
            batch_size_100=args.batch_size_100,
            model_name=args.model_name,
            cache_embeds_dir=args.cache_dir,
            base_seed=args.seed,
        )

        elapsed = time.time() - t0
        status["elapsed_seconds"] = round(elapsed, 1)
        status["elapsed_minutes"] = round(elapsed / 60, 2)
        status["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        val = validate_output(args.output_dir, args.num_samples, seq_len, sequence)
        status["validation"] = val
        status["status"] = "success" if val["valid"] else "partial"

        print(f"\nGenerated in {elapsed/60:.1f} min")
        if val["conformation_count"] is not None:
            print(f"  Physical conformations: {val['conformation_count']}/{args.num_samples} ({val['pass_rate']*100:.1f}%)")
        for issue in val["issues"]:
            print(f"  WARNING: {issue}")

    except Exception as e:
        status["status"] = "failed"
        status["error"] = str(e)
        status["traceback"] = traceback.format_exc()
        status["elapsed_seconds"] = round(time.time() - t0, 1)
        status["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        print(f"\nERROR: {e}")
        traceback.print_exc()

    keepalive_stop.set()

    status_path = Path(args.output_dir) / "generation_status.json"
    with open(status_path, 'w') as f:
        json.dump(status, f, indent=2, default=str)
    print(f"\nStatus written to {status_path}")

    if status["status"] == "failed":
        sys.exit(1)
    elif status["status"] == "partial":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
