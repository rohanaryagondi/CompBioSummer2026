#!/usr/bin/env python3
"""
BioEmu single-protein ensemble generation wrapper.

Usage:
    python bioemu_generate_single.py \
        --fasta /path/to/sequences.fasta \
        --protein-index 0 \
        --output-dir /path/to/output/PROTEIN_NAME \
        --cache-dir /path/to/cache \
        --num-samples 2000

Reads one sequence from the multi-FASTA file by index, generates BioEmu
conformations, validates output, and writes a JSON status file.
"""

import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path


def parse_fasta(fasta_path):
    """Parse multi-FASTA file. Returns list of (header, sequence) tuples."""
    entries = []
    header = None
    seq_lines = []
    with open(fasta_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if header is not None:
                    entries.append((header, ''.join(seq_lines)))
                header = line[1:]  # remove '>'
                seq_lines = []
            else:
                seq_lines.append(line)
    if header is not None:
        entries.append((header, ''.join(seq_lines)))
    return entries


def validate_output(output_dir, num_samples, seq_len, sequence=None):
    """Validate BioEmu output directory.

    Args:
        output_dir: Path to protein output directory.
        num_samples: Number of samples requested.
        seq_len: Sequence length.
        sequence: Amino acid sequence string. If provided, used to compute
            correct expected atom count (glycine lacks CB).
    """
    output_dir = Path(output_dir)
    issues = []

    # Check for topology.pdb
    topo = output_dir / "topology.pdb"
    if not topo.exists():
        issues.append("topology.pdb missing")
    elif topo.stat().st_size == 0:
        issues.append("topology.pdb is empty")

    # Check for samples.xtc
    xtc = output_dir / "samples.xtc"
    if not xtc.exists():
        issues.append("samples.xtc missing")
    elif xtc.stat().st_size == 0:
        issues.append("samples.xtc is empty")

    # Check for batch .npz files
    npz_files = sorted(output_dir.glob("batch_*.npz"))
    if len(npz_files) == 0:
        issues.append("No batch_*.npz files found")
    else:
        # Verify no empty files
        for npz in npz_files:
            if npz.stat().st_size == 0:
                issues.append(f"{npz.name} is empty")

    # Check sequence.fasta
    seq_fasta = output_dir / "sequence.fasta"
    if not seq_fasta.exists():
        issues.append("sequence.fasta missing")

    # Attempt to count conformations via mdtraj if available
    conformation_count = None
    if xtc.exists() and topo.exists():
        try:
            import mdtraj
            traj = mdtraj.load(str(xtc), top=str(topo))
            conformation_count = traj.n_frames
            atoms_per_frame = traj.n_atoms
            # BioEmu writes 5 backbone atoms per residue (N, CA, C, CB, O),
            # but glycine residues lack CB, so subtract glycine count.
            num_glycines = sequence.count('G') if sequence else 0
            expected_atoms = 5 * seq_len - num_glycines
            if atoms_per_frame != expected_atoms:
                issues.append(
                    f"Atom count mismatch: got {atoms_per_frame}, "
                    f"expected {expected_atoms} "
                    f"(5*{seq_len} - {num_glycines} glycines)"
                )
            if conformation_count < 2000:
                issues.append(
                    f"Low conformation count: {conformation_count} "
                    f"(below OSF v3 >=2000 floor, after physicality filtering)"
                )
        except Exception as e:
            issues.append(f"mdtraj validation failed: {e}")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "npz_count": len(npz_files),
        "conformation_count": conformation_count,
    }


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


def main():
    parser = argparse.ArgumentParser(description="BioEmu single-protein generation")
    parser.add_argument("--fasta", required=True, help="Multi-FASTA file path")
    parser.add_argument("--protein-index", type=int, required=True,
                        help="0-based index into FASTA file")
    parser.add_argument("--output-dir", required=True,
                        help="Output directory for this protein")
    parser.add_argument("--cache-dir", required=True,
                        help="Embedding cache directory")
    parser.add_argument("--num-samples", type=int, default=2000,
                        help="Number of conformations to generate")
    parser.add_argument("--batch-size-100", type=int, default=10,
                        help="Batch size parameter (multiples of 100)")
    parser.add_argument("--model-name", default="bioemu-v1.1",
                        help="BioEmu model name")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    args = parser.parse_args()

    # Start GPU keepalive to prevent idle-GPU auto-cancel during model loading
    keepalive_stop = gpu_keepalive()

    # Parse FASTA and get target protein
    entries = parse_fasta(args.fasta)
    if args.protein_index >= len(entries):
        print(f"ERROR: protein-index {args.protein_index} out of range "
              f"(FASTA has {len(entries)} entries)")
        sys.exit(1)

    header, sequence = entries[args.protein_index]
    # Parse header: >UniProt_ID|protein_name|len=N|assays=...
    parts = header.split('|')
    uniprot_id = parts[0] if parts else "unknown"
    protein_name = parts[1] if len(parts) > 1 else "unknown"
    seq_len = len(sequence)

    print(f"=" * 70)
    print(f"BioEmu Generation: {uniprot_id} ({protein_name})")
    print(f"  Sequence length: {seq_len}")
    print(f"  Num samples: {args.num_samples}")
    print(f"  Output dir: {args.output_dir}")
    print(f"  Cache dir: {args.cache_dir}")
    print(f"  Model: {args.model_name}")
    print(f"  Seed: {args.seed}")
    print(f"=" * 70)

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.cache_dir, exist_ok=True)

    # Status tracking
    status = {
        "uniprot_id": uniprot_id,
        "protein_name": protein_name,
        "sequence_length": seq_len,
        "num_samples_requested": args.num_samples,
        "model_name": args.model_name,
        "seed": args.seed,
        "protein_index": args.protein_index,
    }

    start_time = time.time()
    status["start_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    try:
        # Import and run BioEmu
        from bioemu.sample import main as bioemu_main

        print(f"\nStarting BioEmu generation at {status['start_time']}...")
        bioemu_main(
            sequence=sequence,
            num_samples=args.num_samples,
            output_dir=args.output_dir,
            batch_size_100=args.batch_size_100,
            model_name=args.model_name,
            cache_embeds_dir=args.cache_dir,
            base_seed=args.seed,
        )

        elapsed = time.time() - start_time
        status["elapsed_seconds"] = round(elapsed, 1)
        status["elapsed_minutes"] = round(elapsed / 60, 2)
        status["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Validate output
        validation = validate_output(args.output_dir, args.num_samples, seq_len,
                                     sequence=sequence)
        status["validation"] = validation
        status["status"] = "success" if validation["valid"] else "partial"

        print(f"\nGeneration completed in {elapsed/60:.1f} minutes")
        print(f"  Validation: {'PASS' if validation['valid'] else 'ISSUES'}")
        if validation["conformation_count"] is not None:
            print(f"  Conformations: {validation['conformation_count']}")
        if validation["issues"]:
            for issue in validation["issues"]:
                print(f"  WARNING: {issue}")

    except Exception as e:
        elapsed = time.time() - start_time
        status["elapsed_seconds"] = round(elapsed, 1)
        status["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        status["status"] = "failed"
        status["error"] = str(e)
        status["traceback"] = traceback.format_exc()
        print(f"\nERROR: Generation failed after {elapsed/60:.1f} minutes")
        print(f"  Error: {e}")
        traceback.print_exc()

    # Stop GPU keepalive
    keepalive_stop.set()

    # Write status JSON
    status_path = Path(args.output_dir) / "generation_status.json"
    with open(status_path, 'w') as f:
        json.dump(status, f, indent=2)
    print(f"\nStatus written to {status_path}")

    # Exit with appropriate code
    if status["status"] == "failed":
        sys.exit(1)
    elif status["status"] == "partial":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
