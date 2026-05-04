#!/usr/bin/env python3
"""
MSA Pre-cache for BioEmu Batch 2 (Sub 1.2 task-004).

Runs ONLY the colabfold MSA + embedding step for each protein in
batch2_manifest.fasta, without any denoising. This:
  1. Uses the login node's internet access to reach colabfold's MSA server
  2. Populates the shared MSA embed cache on scratch
  3. Is CPU-safe (no GPU denoising is invoked)
  4. Short runtime per protein (~1-3 min for MSA + cache write)

After this script runs, every SLURM batch job reuses the cached embeddings
and skips the MSA server entirely. This avoids rate-limit issues and makes
each compute-node job fully offline-capable.

Usage:
  python precache_msa.py --manifest-fasta batch2_manifest.fasta \
                          --cache-dir /nfs/roberts/scratch/pi_mg269/rag88/.bioemu_embeds_cache \
                          --indices 0        # single protein
                          --indices 0,1,2,3  # comma-separated
                          --indices all      # entire manifest
"""

from __future__ import annotations

import argparse
import os
import sys
import threading
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# GPU keepalive — prevents YCRC 1-hr-idle auto-cancel while MSA building (CPU).
# Matches the pattern in phases/phase-1/subphase-1.1/output/scripts/mace_hybrid_nvt.py.
# ---------------------------------------------------------------------------
_keepalive_stop = threading.Event()


def _gpu_keepalive_loop() -> None:
    try:
        import torch
        if not torch.cuda.is_available():
            return
        dev = torch.device('cuda:0')
        x = torch.randn(64, 64, device=dev)
        while not _keepalive_stop.is_set():
            y = torch.matmul(x, x).sum().item()
            torch.cuda.synchronize()
            _keepalive_stop.wait(300)  # 5 min between pokes
    except Exception:
        pass  # keepalive must never crash MSA work


def start_gpu_keepalive() -> threading.Thread:
    t = threading.Thread(target=_gpu_keepalive_loop, daemon=True, name='gpu-keepalive')
    t.start()
    print('[keepalive] GPU keepalive thread started (5-min cadence)', flush=True)
    return t


def stop_gpu_keepalive() -> None:
    _keepalive_stop.set()


def parse_fasta(fasta_path: Path):
    entries = []
    header = None
    seq_lines = []
    with open(fasta_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if header is not None:
                    entries.append((header, ''.join(seq_lines)))
                header = line[1:]
                seq_lines = []
            else:
                seq_lines.append(line)
    if header is not None:
        entries.append((header, ''.join(seq_lines)))
    return entries


def parse_indices(s: str, total: int) -> list[int]:
    if s == 'all':
        return list(range(total))
    result = []
    for part in s.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            lo, hi = part.split('-')
            result.extend(range(int(lo), int(hi) + 1))
        else:
            result.append(int(part))
    return [i for i in result if 0 <= i < total]


def precache_one(sequence: str, cache_dir: Path, uid: str):
    """Call bioemu's colabfold embedding function, which computes MSA via
    the colabfold server and writes to cache_dir keyed by sequence hash."""
    from bioemu.get_embeds import get_colabfold_embeds
    t0 = time.time()
    single_file, pair_file = get_colabfold_embeds(
        seq=sequence,
        cache_embeds_dir=str(cache_dir),
        # msa_host_url defaults to colabfold's remote server
    )
    dt = time.time() - t0
    exists_s = os.path.exists(single_file)
    exists_p = os.path.exists(pair_file)
    print(f"    uid={uid}  single={'OK' if exists_s else 'MISS'}  pair={'OK' if exists_p else 'MISS'}  dt={dt:.1f}s")
    return exists_s and exists_p


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest-fasta',
                   default='/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/batch2_manifest.fasta')
    p.add_argument('--cache-dir',
                   default='/nfs/roberts/scratch/pi_mg269/rag88/.bioemu_embeds_cache')
    p.add_argument('--indices', default='0',
                   help='Which manifest indices to precache. Examples: "0", '
                        '"0,1,2", "0-9", "all". Default: "0".')
    args = p.parse_args()

    # Environment tweaks (match Sub 1.1 submit script)
    os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
    os.environ.setdefault('HF_HOME', '/nfs/roberts/scratch/pi_mg269/rag88/.hf_cache')
    os.environ['MPLBACKEND'] = 'Agg'

    # Start GPU keepalive BEFORE any MSA work (MSA building is CPU-heavy; without
    # this the YCRC 1-hr idle-GPU policy auto-cancels the SLURM job).
    start_gpu_keepalive()

    cache_dir = Path(args.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    entries = parse_fasta(Path(args.manifest_fasta))
    indices = parse_indices(args.indices, len(entries))
    print(f"Manifest has {len(entries)} proteins; pre-caching {len(indices)}: {indices[:10]}{'...' if len(indices)>10 else ''}")

    successes = 0
    failures = []
    for i in indices:
        header, seq = entries[i]
        uid = header.split('|')[0]
        print(f"[{i:3d}/{len(indices)}] uid={uid} len={len(seq)}")
        try:
            ok = precache_one(seq, cache_dir, uid)
            if ok:
                successes += 1
            else:
                failures.append(uid)
        except Exception as e:
            print(f"    FAILED: {type(e).__name__}: {e}")
            failures.append(uid)

    print()
    print(f"Pre-cache summary: {successes} / {len(indices)} succeeded")
    if failures:
        print(f"Failures: {failures[:20]}{'...' if len(failures)>20 else ''}")
        sys.exit(2)


if __name__ == '__main__':
    main()
