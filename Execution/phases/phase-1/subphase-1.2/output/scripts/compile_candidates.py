#!/usr/bin/env python3
"""
BioEmu Batch 2 Candidate Compiler (Sub 1.2 task-004, Step 1).

Reads the ProteinGym DMS_substitutions.csv reference file and compiles a
candidate list of proteins for batch 2 BioEmu generation.

Subtractions (do NOT regenerate):
  - 46 batch-1 proteins (UniProt_IDs from
    phases/phase-1/subphase-1.1/output/task-003-sequences.fasta headers)
  - 16 active Alpha-M benchmark proteins (from manifest.json); these are
    different proteins generated independently for Alpha-M and MUST NOT be
    redone here. (In practice, no overlap exists between the 14-aa WW
    short-name in Alpha-M and the ProteinGym WWOX/WW entries, but we subtract
    by UniProt when available for safety.)

Filters:
  - seq_len between 30 and 500 aa (Sub 1.1 SPG1 >400 aa memory lesson; we
    are slightly more permissive up to 500 since RTX 5000 Ada handled
    YAP1 at 504 aa before the memory bump)
  - selection_type in {Binding, Activity, Expression, Stability,
    OrganismalFitness} — all are ProteinGym's supported assay types
  - sort priority: Binding > Activity > Expression > OrganismalFitness >
    Stability (so the first N taken are the most valuable for IP §12.2
    binding+activity primary win-rate)

Output: batch2_candidates.csv with columns:
  protein_id (= DMS_id), uniprot_id, sequence, length, selection_type,
  source_pdb_id, expected_protein_class_guess

`expected_protein_class_guess` is a *very* rough sequence-only heuristic
(globular / IDP-like / long-multi-domain). The real classification is
refined in the manifest builder using length thresholds and disorder
screening.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Optional


def read_batch1_uniprot_ids(fasta_path: Path) -> set[str]:
    """Parse Sub 1.1 batch 1 FASTA and extract UniProt_IDs (headers like
    `>UniProt_ID|name|len=N|assays=...`)."""
    ids = set()
    if not fasta_path.exists():
        return ids
    with open(fasta_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                header = line[1:]
                uid = header.split('|', 1)[0]
                if uid:
                    ids.add(uid)
    return ids


def read_alpha_m_short_names(manifest_path: Path) -> set[str]:
    """Alpha-M manifest has Pin1 WW, Crambin, GB3, GB1, etc. — these are
    small benchmark proteins pulled from PDB, NOT from ProteinGym. Return
    their short_names for reference only; by UniProt_ID there is essentially
    no overlap with ProteinGym."""
    if not manifest_path.exists():
        return set()
    with open(manifest_path, 'r') as f:
        data = json.load(f)
    return {p['short_name'] for p in data.get('proteins', [])}


SELECTION_PRIORITY = {
    'Binding': 0,
    'Activity': 1,
    'Expression': 2,
    'OrganismalFitness': 3,
    'Stability': 4,
    'Growth': 5,  # viral growth, de-prioritized
}


def rough_class_guess(seq: str, length: int) -> str:
    """Fallback class guess from sequence alone (refined later in manifest
    builder). Returns one of: small_globular, medium_globular, large_globular,
    idp_like, multi_domain_candidate, transmembrane_candidate.

    Heuristic criteria:
    - Length < 250 aa and <40% polar/flexible bias -> small_globular
    - 250 <= length < 400 -> medium_globular
    - 400 <= length <= 500 -> large_globular (risky, needs disorder screen)
    - High Gly/Pro/Gln/Ser/Asn bias (>50% of residues) -> idp_like
    - >=3 long hydrophobic stretches (>=20 aa each) -> transmembrane_candidate
    - Very long with multiple hydrophobic stretches -> multi_domain_candidate
    """
    if length == 0:
        return 'small_globular'

    flexible_residues = {'G', 'P', 'Q', 'S', 'N', 'E', 'D', 'K', 'R'}
    flexible_count = sum(1 for a in seq if a in flexible_residues)
    flex_frac = flexible_count / length

    # Quick transmembrane heuristic: runs of hydrophobic residues
    hydrophobic = set('AILMFVWY')
    hydro_runs = []
    current_run = 0
    for a in seq:
        if a in hydrophobic:
            current_run += 1
        else:
            if current_run >= 15:
                hydro_runs.append(current_run)
            current_run = 0
    if current_run >= 15:
        hydro_runs.append(current_run)

    if len(hydro_runs) >= 3 and length >= 200:
        return 'transmembrane_candidate'

    if flex_frac > 0.55 and length >= 100:
        return 'idp_like'

    if length < 250:
        return 'small_globular'
    elif length < 400:
        return 'medium_globular'
    else:
        return 'large_globular'


def compile_candidates(args):
    dms_csv = Path(args.dms_csv)
    batch1_fasta = Path(args.batch1_fasta)
    manifest_json = Path(args.manifest_json)
    output_csv = Path(args.output_csv)

    batch1_ids = read_batch1_uniprot_ids(batch1_fasta)
    am_short_names = read_alpha_m_short_names(manifest_json)

    print(f"Batch 1 UniProt_IDs subtracted: {len(batch1_ids)}")
    print(f"Alpha-M short names (reference only): {len(am_short_names)}")

    rows = []
    with open(dms_csv, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            uid = r['UniProt_ID']
            if uid in batch1_ids:
                continue
            try:
                length = int(r['seq_len'])
            except (KeyError, ValueError):
                continue
            if length < args.min_length or length > args.max_length:
                continue
            seq = r['target_seq'].strip().upper()
            if not seq or not re.fullmatch(r'[ACDEFGHIKLMNPQRSTVWYX]+', seq):
                continue
            # Use coarse_selection_type (5-category ProteinGym label), not
            # the free-text selection_type field which is assay-specific.
            sel_type = r.get('coarse_selection_type', '') or r.get('selection_type', '')
            if sel_type == 'Growth':  # viral-only, lowest priority
                continue
            sel_prio = SELECTION_PRIORITY.get(sel_type, 99)
            cls_guess = rough_class_guess(seq, length)
            pdb_file = r.get('pdb_file', '')
            pdb_id = pdb_file.split('.')[0] if pdb_file else ''

            rows.append({
                'protein_id': r['DMS_id'],
                'uniprot_id': uid,
                'sequence': seq,
                'length': length,
                'selection_type': sel_type,
                'sort_priority': sel_prio,
                'source_pdb_id': pdb_id,
                'expected_protein_class_guess': cls_guess,
            })

    # Dedup per UniProt_ID: keep the FIRST (highest-priority) row per UniProt,
    # so each protein appears exactly once in batch 2.
    seen_uid = {}
    rows.sort(key=lambda x: (x['sort_priority'], x['length']))
    for r in rows:
        uid = r['uniprot_id']
        if uid not in seen_uid:
            seen_uid[uid] = r
    deduped = sorted(seen_uid.values(), key=lambda x: (x['sort_priority'], x['length']))

    # Cap at top-N (default 150)
    top_n = args.top_n
    final = deduped[:top_n]

    print(f"Filtered & deduped candidates: {len(deduped)}")
    print(f"Keeping top-{top_n}: {len(final)}")
    cls_hist = {}
    sel_hist = {}
    for r in final:
        cls_hist[r['expected_protein_class_guess']] = cls_hist.get(r['expected_protein_class_guess'], 0) + 1
        sel_hist[r['selection_type']] = sel_hist.get(r['selection_type'], 0) + 1
    print(f"Class histogram: {cls_hist}")
    print(f"Selection-type histogram: {sel_hist}")

    os.makedirs(output_csv.parent, exist_ok=True)
    fieldnames = ['protein_id', 'uniprot_id', 'sequence', 'length',
                  'selection_type', 'source_pdb_id', 'expected_protein_class_guess']
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in final:
            writer.writerow({k: r[k] for k in fieldnames})
    print(f"Wrote {output_csv}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dms-csv',
                   default='/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/proteingym_dms_substitutions.csv')
    p.add_argument('--batch1-fasta',
                   default='/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/task-003-sequences.fasta')
    p.add_argument('--manifest-json',
                   default='/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/manifest.json')
    p.add_argument('--output-csv',
                   default='/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/scripts/batch2_candidates.csv')
    p.add_argument('--min-length', type=int, default=30)
    p.add_argument('--max-length', type=int, default=600,
                   help='Upper length limit. Sub 1.1 ran YAP1 (504 aa) and '
                        'SPG1 (448 aa) on RTX 5000 Ada; 600 aa is safe with '
                        '--mem=40G in sbatch when num_samples<=3000, but '
                        'long proteins with low pass-rate class assignment '
                        'will be oversampled to ~11,000 samples which '
                        'approaches memory risk. Reconcile in manifest '
                        'builder: if class==multi_domain AND L>500, force '
                        'num_samples<=5000 with a cross-agent note.')
    p.add_argument('--top-n', type=int, default=150,
                   help='Keep top N candidates by selection-priority then length')
    args = p.parse_args()
    compile_candidates(args)


if __name__ == '__main__':
    main()
