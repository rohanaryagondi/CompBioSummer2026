#!/usr/bin/env python3
"""
BioEmu Batch 2 Manifest Builder (Sub 1.2 task-004, Step 3).

Reads batch2_screened.csv (from disorder_screen.py), refines the protein
class, looks up the class-based expected pass rate from the Sub 1.1
cross-agent note shared/notes/1.1-bioemu-passrates.md lines 73-81, and
computes per-protein num_samples using the formula:

    num_samples = ceil(2000 / pass_rate * 1.3)

Class table (Sub 1.1 empirical pass rates + safety margin):

    Class                     Pass rate   Recommended num_samples
    ------------------------  ---------   -----------------------
    structured_globular       0.92        2,829
    idp_like                  0.47        5,533
    transmembrane             0.70        3,714
    multi_domain_metastable   0.23       11,305
    large_globular_long       0.60        4,334  (L>=400 + globular)

Class assignment rules (refined from the rough heuristic in
compile_candidates.py using the disorder-screen metrics):

  1. If disorder_fraction > 0.40 OR foldindex_global < -0.10 -> idp_like
  2. Else if L >= 400 AND hydrophobic-run count >= 3 -> transmembrane
     (crude proxy; most multi-helix TMs show this pattern)
  3. Else if L >= 400 -> large_globular_long
  4. Else if L >= 200 AND hydrophobic-run count >= 3 -> transmembrane
  5. Else -> structured_globular

Also applies safety caps (per task spec failure modes):
  - num_samples is clamped to max 10000 for L>500 proteins (memory safety
    per Sub 1.1 SPG1 high-num_samples blowup lesson).
  - num_samples >= 2000 floor (we always want >=2000 raw samples even for
    nominally 100% pass rate classes).

Output columns: protein_id, uniprot_id, sequence, length, selection_type,
source_pdb_id, expected_class, expected_pass_rate, num_samples,
batch_index, memory_gb, sbatch_time_hours.

Batches of ~10 proteins each are assigned by insertion order (which follows
selection-priority from compile_candidates, so Binding+Activity end up
in early batches).
"""

from __future__ import annotations

import argparse
import csv
import math
import os
from pathlib import Path


# Class-based pass rates (Sub 1.1 cross-agent note lines 73-81)
CLASS_PASS_RATE = {
    'structured_globular': 0.92,
    'idp_like': 0.47,
    'transmembrane': 0.70,
    'multi_domain_metastable': 0.23,
    'large_globular_long': 0.60,
}

# Recommended num_samples per class (computed: ceil(2000 / pr * 1.3))
CLASS_NUM_SAMPLES = {
    k: math.ceil(2000 / v * 1.3) for k, v in CLASS_PASS_RATE.items()
}
# Verified values (computed via ceil(2000/pr*1.3) with Python float precision):
# structured_globular:     2827    (2000/0.92*1.3 = 2826.09 -> ceil = 2827)
# idp_like:                5532    (2000/0.47*1.3 = 5531.91 -> ceil = 5532)
# transmembrane:           3715    (2000/0.70*1.3 = 3714.29 -> ceil = 3715)
# multi_domain_metastable: 11305   (2000/0.23*1.3 = 11304.35 -> ceil = 11305)
# large_globular_long:     4334    (2000/0.60*1.3 = 4333.33 -> ceil = 4334)
# Matches the Sub 1.1 cross-agent-note table (lines 77-80 of
# shared/notes/1.1-bioemu-passrates.md: "Structured globular 90-99% -> 2,200-2,900"
# etc. — our 2,827 sits inside that envelope.)


def count_hydro_runs(seq: str, run_len: int = 15) -> int:
    """Count runs of >=run_len consecutive hydrophobic residues (AILMFVWY).
    Proxy for transmembrane helices."""
    hydrophobic = set('AILMFVWY')
    runs = 0
    current = 0
    for a in seq:
        if a in hydrophobic:
            current += 1
        else:
            if current >= run_len:
                runs += 1
            current = 0
    if current >= run_len:
        runs += 1
    return runs


def assign_class(row: dict) -> str:
    seq = row['sequence']
    L = int(row['length'])
    df = float(row['disorder_fraction'])
    fi = float(row['foldindex_global'])
    hydro_runs = count_hydro_runs(seq, run_len=15)

    # Rule 1: disorder-rich -> idp_like
    if df > 0.40 or fi < -0.10:
        return 'idp_like'
    # Rule 2: long + multi-hydrophobic -> transmembrane
    if L >= 400 and hydro_runs >= 3:
        return 'transmembrane'
    # Rule 3: long globular
    if L >= 400:
        return 'large_globular_long'
    # Rule 4: medium + multi-hydrophobic -> transmembrane
    if L >= 200 and hydro_runs >= 3:
        return 'transmembrane'
    # Rule 5: default
    return 'structured_globular'


def compute_num_samples(cls: str, L: int) -> int:
    base = CLASS_NUM_SAMPLES[cls]
    # Safety cap: if L > 500, cap num_samples at 10000 even if class suggests more
    if L > 500:
        base = min(base, 10000)
    # Floor: always >=2000
    return max(base, 2000)


def compute_memory_gb(cls: str, L: int, num_samples: int) -> int:
    """Memory request in GB. Sub 1.1 default was 40G for SPG1/YAP1 at >=200aa;
    smaller proteins can use 24G. Scale by L and num_samples."""
    if L >= 300 or num_samples > 5000:
        return 40
    return 24


def compute_time_hours(cls: str, L: int, num_samples: int) -> int:
    """Wall-time estimate. Sub 1.1 observed ~15-45 min per protein for small
    (<=100 aa) globular at num_samples=2000. Scales with L and num_samples:

        time (min) ~= 2 min + 0.12 * L + 0.005 * num_samples

    Round up to whole hours, cap at 6 h (the existing bioemu_batch.sbatch
    ceiling; we split per-protein rather than batching within a job).
    """
    time_min = 2 + 0.12 * L + 0.005 * num_samples
    h = max(1, math.ceil(time_min / 60))
    return min(h, 6)


def build_manifest(args):
    inp = Path(args.input)
    out = Path(args.output)
    batch_size = args.batch_size

    rows_in = []
    with open(inp, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r.get('exclude_reason', '').strip():
                continue  # skip disorder-excluded proteins
            rows_in.append(r)

    out_rows = []
    class_counts = {k: 0 for k in CLASS_PASS_RATE}
    for i, r in enumerate(rows_in):
        cls = assign_class(r)
        L = int(r['length'])
        num_samples = compute_num_samples(cls, L)
        mem_gb = compute_memory_gb(cls, L, num_samples)
        time_h = compute_time_hours(cls, L, num_samples)
        class_counts[cls] += 1
        batch_idx = i // batch_size + 1
        out_rows.append({
            'protein_id': r['protein_id'],
            'uniprot_id': r['uniprot_id'],
            'sequence': r['sequence'],
            'length': L,
            'selection_type': r['selection_type'],
            'source_pdb_id': r.get('source_pdb_id', ''),
            'expected_class': cls,
            'expected_pass_rate': f'{CLASS_PASS_RATE[cls]:.2f}',
            'num_samples': num_samples,
            'batch_index': batch_idx,
            'memory_gb': mem_gb,
            'sbatch_time_hours': time_h,
        })

    os.makedirs(out.parent, exist_ok=True)
    fieldnames = ['protein_id', 'uniprot_id', 'sequence', 'length',
                  'selection_type', 'source_pdb_id', 'expected_class',
                  'expected_pass_rate', 'num_samples', 'batch_index',
                  'memory_gb', 'sbatch_time_hours']
    with open(out, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in out_rows:
            writer.writerow(r)

    # Also write a pure FASTA version for --cache-first and for
    # submit_bioemu_batch2.sh consumption.
    fasta_path = out.with_suffix('.fasta')
    with open(fasta_path, 'w') as f:
        for r in out_rows:
            header = (f">{r['uniprot_id']}|{r['protein_id']}|len={r['length']}"
                      f"|class={r['expected_class']}|n={r['num_samples']}")
            f.write(header + '\n')
            seq = r['sequence']
            for i in range(0, len(seq), 80):
                f.write(seq[i:i+80] + '\n')

    # Report
    print(f"Input screened: {len(rows_in)}")
    print(f"Manifest rows:  {len(out_rows)}")
    print(f"Class counts:   {class_counts}")
    print(f"num_samples totals by class:")
    ns_by_cls = {}
    for r in out_rows:
        ns_by_cls.setdefault(r['expected_class'], []).append(r['num_samples'])
    for k, v in ns_by_cls.items():
        print(f"  {k:26s} n={len(v):3d}  min={min(v):>6d}  max={max(v):>6d}  mean={sum(v)//len(v):>6d}  total_samples={sum(v):>7d}")
    total = sum(sum(v) for v in ns_by_cls.values())
    total_gpu_hours = sum(r['sbatch_time_hours'] for r in out_rows)
    print(f"Grand total denoised samples: {total:,}")
    print(f"Estimated GPU-hrs (sum of per-protein ceilings): {total_gpu_hours}")
    print(f"Number of batches of {batch_size}: {math.ceil(len(out_rows)/batch_size)}")
    print(f"Wrote manifest CSV:   {out}")
    print(f"Wrote manifest FASTA: {fasta_path}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',
                   default='/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/batch2_screened.csv')
    p.add_argument('--output',
                   default='/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/batch2_manifest.csv')
    p.add_argument('--batch-size', type=int, default=10,
                   help='Proteins per SLURM batch (default 10, matching Sub 1.1 pattern)')
    args = p.parse_args()
    build_manifest(args)


if __name__ == '__main__':
    main()
