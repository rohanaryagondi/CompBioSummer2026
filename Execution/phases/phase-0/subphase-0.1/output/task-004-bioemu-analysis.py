#!/usr/bin/env python3
"""
BioEmu Disulfide Bond Integrity Analysis
=========================================
Generates 100 BioEmu conformations each for BPTI and HEWL, measures SG-SG
distances for all disulfide bonds, computes integrity metrics, generates
visualizations, and writes the threshold assessment report.

Usage (run via SLURM, see task-004-bioemu-slurm.sh):
    python task-004-bioemu-analysis.py
"""

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mdtraj
import numpy as np

# ============================================================================
# Configuration
# ============================================================================

BASE_DIR = Path("/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1")
OUTPUT_DIR = BASE_DIR / "output"
PROTEIN_DIR = BASE_DIR / "proteins"

# BioEmu parameters
NUM_SAMPLES = 100
BATCH_SIZE_100 = 10  # batch size for 100-residue protein
MODEL_NAME = "bioemu-v1.1"

# Disulfide bond definitions (0-indexed residue numbers)
# BPTI (6PTI): Cys5-Cys55, Cys14-Cys38, Cys30-Cys51
# PDB numbering starts at 1, so 0-indexed: 4, 54, 13, 37, 29, 50
# But we need to verify against actual residue indices in the sequence
BPTI_SEQUENCE = "RPDFCLEPPYTGPCKARIIRYFYNAKAGLCQTFVYGGCRAKRNNFKSAEDCMRTCGG"
HEWL_SEQUENCE = "KVFGRCELAAAMKRHGLDNYRGYSLGNWVCAAKFESNFNTQATNRNTDGSTDYGILQINSRWWCNDGRTPGSRNLCNIPCSALLSSDITASVNCAKKIVSDGNGMNAWVAWRNRCKGTDVQAWIRGCRL"

# Disulfide bonds by PDB residue number (1-indexed)
# BPTI: Cys5-Cys55, Cys14-Cys38, Cys30-Cys51
BPTI_SS_BONDS = [
    ("Cys5", "Cys55", 4, 54),     # 0-indexed
    ("Cys14", "Cys38", 13, 37),
    ("Cys30", "Cys51", 29, 50),
]

# HEWL (1AKI): Cys6-Cys127, Cys30-Cys115, Cys64-Cys80, Cys76-Cys94
HEWL_SS_BONDS = [
    ("Cys6", "Cys127", 5, 126),
    ("Cys30", "Cys115", 29, 114),
    ("Cys64", "Cys80", 63, 79),
    ("Cys76", "Cys94", 75, 93),
]

SS_CUTOFF = 2.5  # Angstroms - generous cutoff for intact SS bond

# ============================================================================
# Logging
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(OUTPUT_DIR / "task-004-bioemu.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def verify_cysteine_positions(sequence, ss_bonds, protein_name):
    """Verify that the specified positions are actually cysteine residues."""
    for name1, name2, idx1, idx2 in ss_bonds:
        if sequence[idx1] != 'C':
            raise ValueError(
                f"{protein_name}: Expected Cys at position {idx1} ({name1}), "
                f"found {sequence[idx1]}"
            )
        if sequence[idx2] != 'C':
            raise ValueError(
                f"{protein_name}: Expected Cys at position {idx2} ({name2}), "
                f"found {sequence[idx2]}"
            )
    logger.info(f"{protein_name}: All cysteine positions verified.")


def generate_conformations(sequence, protein_name, output_subdir):
    """Generate BioEmu conformations for a protein."""
    from bioemu.sample import main as bioemu_main

    out_path = OUTPUT_DIR / output_subdir
    out_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Generating {NUM_SAMPLES} BioEmu conformations for {protein_name} "
                f"({len(sequence)} residues)...")
    logger.info(f"  Model: {MODEL_NAME}")
    logger.info(f"  Output: {out_path}")

    import torch
    if torch.cuda.is_available():
        logger.info(f"  GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"  GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        logger.warning("  No GPU available! Running on CPU (will be slow).")

    start_time = time.time()

    # Use scratch for embedding cache if env var is set
    cache_embeds = os.environ.get("BIOEMU_EMBEDS_CACHE", None)

    bioemu_main(
        sequence=sequence,
        num_samples=NUM_SAMPLES,
        output_dir=str(out_path),
        batch_size_100=BATCH_SIZE_100,
        model_name=MODEL_NAME,
        base_seed=42,
        cache_embeds_dir=cache_embeds,
    )

    elapsed = time.time() - start_time
    logger.info(f"  Generation completed in {elapsed:.1f}s ({elapsed/60:.1f} min)")

    return out_path, elapsed


def measure_ss_distances(traj_dir, ss_bonds, protein_name):
    """
    Measure SG-SG distances for all disulfide bonds across all conformations.

    Returns:
        distances: dict mapping bond label to array of distances (Angstroms)
    """
    topology_path = traj_dir / "topology.pdb"
    xtc_path = traj_dir / "samples.xtc"

    if not topology_path.exists() or not xtc_path.exists():
        raise FileNotFoundError(
            f"Expected topology.pdb and samples.xtc in {traj_dir}"
        )

    logger.info(f"Loading trajectory for {protein_name}...")
    traj = mdtraj.load_xtc(str(xtc_path), top=str(topology_path))
    logger.info(f"  Loaded {traj.n_frames} frames, {traj.n_atoms} atoms")

    topology = traj.topology
    distances = {}

    for name1, name2, res_idx1, res_idx2 in ss_bonds:
        bond_label = f"{name1}-{name2}"

        # Find SG atoms for the two cysteine residues
        sg1_atoms = topology.select(f"resid {res_idx1} and name SG")
        sg2_atoms = topology.select(f"resid {res_idx2} and name SG")

        if len(sg1_atoms) == 0 or len(sg2_atoms) == 0:
            # Try CB atoms as fallback (BioEmu might not output SG)
            logger.warning(f"  {bond_label}: SG atom not found, trying CB as proxy")
            sg1_atoms = topology.select(f"resid {res_idx1} and name CB")
            sg2_atoms = topology.select(f"resid {res_idx2} and name CB")

            if len(sg1_atoms) == 0 or len(sg2_atoms) == 0:
                logger.error(f"  {bond_label}: Neither SG nor CB atoms found!")
                # List available atoms for debugging
                res1_atoms = topology.select(f"resid {res_idx1}")
                res2_atoms = topology.select(f"resid {res_idx2}")
                logger.error(f"    Residue {res_idx1} atoms: {[topology.atom(a).name for a in res1_atoms]}")
                logger.error(f"    Residue {res_idx2} atoms: {[topology.atom(a).name for a in res2_atoms]}")
                distances[bond_label] = None
                continue

        atom_pairs = np.array([[sg1_atoms[0], sg2_atoms[0]]])
        # mdtraj returns distances in nm, convert to Angstroms
        dists = mdtraj.compute_distances(traj, atom_pairs).flatten() * 10.0

        distances[bond_label] = dists
        logger.info(f"  {bond_label}: mean={dists.mean():.2f} +/- {dists.std():.2f} A, "
                     f"range=[{dists.min():.2f}, {dists.max():.2f}] A")

    return distances


def compute_integrity(distances, protein_name):
    """Compute per-bond and overall disulfide integrity metrics."""
    n_conformations = None
    per_bond = {}

    for bond_label, dists in distances.items():
        if dists is None:
            per_bond[bond_label] = {
                "integrity": None,
                "mean": None, "std": None, "min": None, "max": None,
                "error": "Atom not found"
            }
            continue

        if n_conformations is None:
            n_conformations = len(dists)

        intact = (dists < SS_CUTOFF).sum()
        per_bond[bond_label] = {
            "integrity": float(intact / len(dists) * 100),
            "intact_count": int(intact),
            "total_count": len(dists),
            "mean": float(dists.mean()),
            "std": float(dists.std()),
            "min": float(dists.min()),
            "max": float(dists.max()),
        }

    # Overall integrity: ALL bonds intact simultaneously
    if n_conformations is not None:
        all_intact = np.ones(n_conformations, dtype=bool)
        for bond_label, dists in distances.items():
            if dists is not None:
                all_intact &= (dists < SS_CUTOFF)
        overall_integrity = float(all_intact.sum() / n_conformations * 100)
        overall_intact_count = int(all_intact.sum())
    else:
        overall_integrity = None
        overall_intact_count = None

    result = {
        "protein": protein_name,
        "n_conformations": n_conformations,
        "overall_integrity_pct": overall_integrity,
        "overall_intact_count": overall_intact_count,
        "per_bond": per_bond,
        "ss_cutoff_angstrom": SS_CUTOFF,
    }

    logger.info(f"{protein_name} overall integrity: {overall_integrity:.1f}% "
                f"({overall_intact_count}/{n_conformations})")

    return result


def save_distances_csv(distances, protein_name, output_path):
    """Save distance data to CSV."""
    bond_labels = list(distances.keys())
    n = max(len(d) for d in distances.values() if d is not None)

    with open(output_path, 'w') as f:
        f.write("conformation," + ",".join(bond_labels) + "\n")
        for i in range(n):
            row = [str(i + 1)]
            for label in bond_labels:
                d = distances[label]
                if d is not None and i < len(d):
                    row.append(f"{d[i]:.4f}")
                else:
                    row.append("NA")
            f.write(",".join(row) + "\n")

    logger.info(f"  Saved distances to {output_path}")


def generate_plot(distances, protein_name, ss_bonds, output_path):
    """Generate violin/box plot of SS distance distributions."""
    fig, ax = plt.subplots(figsize=(10, 6))

    bond_labels = [f"{n1}-{n2}" for n1, n2, _, _ in ss_bonds]
    plot_data = []
    for label in bond_labels:
        d = distances.get(label)
        if d is not None:
            plot_data.append(d)
        else:
            plot_data.append(np.array([]))

    positions = range(1, len(bond_labels) + 1)

    # Violin plot
    parts = ax.violinplot(plot_data, positions=positions, showmeans=True, showmedians=True)
    for pc in parts['bodies']:
        pc.set_facecolor('#4C72B0')
        pc.set_alpha(0.6)

    # Box plot overlay
    bp = ax.boxplot(plot_data, positions=positions, widths=0.15, patch_artist=False,
                    showfliers=True, zorder=3)

    # Threshold line
    ax.axhline(y=SS_CUTOFF, color='red', linestyle='--', linewidth=2,
               label=f'Integrity cutoff ({SS_CUTOFF} A)')

    # Typical SS bond length
    ax.axhline(y=2.04, color='green', linestyle=':', linewidth=1,
               label='Typical SS bond (2.04 A)')

    ax.set_xticks(positions)
    ax.set_xticklabels(bond_labels, rotation=45, ha='right')
    ax.set_ylabel('SG-SG Distance (Angstrom)')
    ax.set_title(f'{protein_name}: Disulfide Bond Distance Distributions\n'
                 f'(N={NUM_SAMPLES} BioEmu conformations, model={MODEL_NAME})')
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"  Saved plot to {output_path}")


def write_threshold_report(bpti_result, hewl_result, gen_times, output_path):
    """Write the threshold assessment report."""
    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "---",
        "task_id: task-004",
        "agent: bioemu-test",
        f"date: {timestamp}",
        "type: experiment-report",
        "---",
        "",
        "# BioEmu Disulfide Bond Integrity Report",
        "",
        f"**Date:** {timestamp}",
        f"**BioEmu model:** {MODEL_NAME} (bioemu v1.3.1)",
        f"**Conformations per protein:** {NUM_SAMPLES}",
        f"**SS integrity cutoff:** {SS_CUTOFF} Angstrom",
        "",
        "---",
        "",
        "## BPTI (58 residues, 3 disulfide bonds)",
        "",
    ]

    bpti_overall = bpti_result["overall_integrity_pct"]
    lines.append(f"**Overall integrity: {bpti_overall:.1f}%** "
                 f"({bpti_result['overall_intact_count']}/{bpti_result['n_conformations']} "
                 f"conformations with ALL 3 bonds intact)")
    lines.append("")
    lines.append("| Bond | Integrity | Mean dist | Std | Min | Max |")
    lines.append("|------|-----------|-----------|-----|-----|-----|")

    for bond_label, stats in bpti_result["per_bond"].items():
        if stats["integrity"] is not None:
            lines.append(
                f"| {bond_label} | {stats['integrity']:.1f}% ({stats['intact_count']}/{stats['total_count']}) | "
                f"{stats['mean']:.2f} A | {stats['std']:.2f} A | {stats['min']:.2f} A | {stats['max']:.2f} A |"
            )
        else:
            lines.append(f"| {bond_label} | ERROR | {stats['error']} | - | - | - |")

    lines.extend([
        "",
        f"Generation time: {gen_times['bpti']:.1f}s ({gen_times['bpti']/60:.1f} min)",
        "",
        "---",
        "",
        "## HEWL (129 residues, 4 disulfide bonds)",
        "",
    ])

    hewl_overall = hewl_result["overall_integrity_pct"]
    lines.append(f"**Overall integrity: {hewl_overall:.1f}%** "
                 f"({hewl_result['overall_intact_count']}/{hewl_result['n_conformations']} "
                 f"conformations with ALL 4 bonds intact)")
    lines.append("")
    lines.append("| Bond | Integrity | Mean dist | Std | Min | Max |")
    lines.append("|------|-----------|-----------|-----|-----|-----|")

    for bond_label, stats in hewl_result["per_bond"].items():
        if stats["integrity"] is not None:
            lines.append(
                f"| {bond_label} | {stats['integrity']:.1f}% ({stats['intact_count']}/{stats['total_count']}) | "
                f"{stats['mean']:.2f} A | {stats['std']:.2f} A | {stats['min']:.2f} A | {stats['max']:.2f} A |"
            )
        else:
            lines.append(f"| {bond_label} | ERROR | {stats['error']} | - | - | - |")

    lines.extend([
        "",
        f"Generation time: {gen_times['hewl']:.1f}s ({gen_times['hewl']/60:.1f} min)",
        "",
        "---",
        "",
        "## THRESHOLD ASSESSMENT",
        "",
    ])

    # T3 assessment
    bpti_t3 = "MET" if bpti_overall is not None and bpti_overall > 95.0 else "NOT MET"
    hewl_t3 = "MET" if hewl_overall is not None and hewl_overall > 95.0 else "NOT MET"

    # AK3 assessment
    bpti_ak3 = "TRIGGERED" if bpti_overall is not None and bpti_overall < 80.0 else "NOT TRIGGERED"
    hewl_ak3 = "TRIGGERED" if hewl_overall is not None and hewl_overall < 80.0 else "NOT TRIGGERED"

    lines.extend([
        f"**T3 (>95% integrity for combined paper GO):**",
        f"  - BPTI: **{bpti_t3}** ({bpti_overall:.1f}%)",
        f"  - HEWL: **{hewl_t3}** ({hewl_overall:.1f}%)",
        "",
        f"**AK3 (<80% integrity triggers BPTI/HEWL drop):**",
        f"  - BPTI: **{bpti_ak3}** ({bpti_overall:.1f}%)",
        f"  - HEWL: **{hewl_ak3}** ({hewl_overall:.1f}%)",
        "",
        "### Zone Interpretation",
        "",
    ])

    for protein, overall in [("BPTI", bpti_overall), ("HEWL", hewl_overall)]:
        if overall is not None:
            if overall >= 95.0:
                zone = "GREEN: T3 met, fully included in benchmark, combined paper viable"
            elif overall >= 80.0:
                zone = "YELLOW: T3 not met (combined paper concern), but remains in benchmark"
            else:
                zone = "RED: AK3 triggered, drop from benchmark (12 proteins remain)"
            lines.append(f"- **{protein}:** {zone}")
        else:
            lines.append(f"- **{protein}:** UNKNOWN (measurement failed)")

    lines.extend([
        "",
        "---",
        "",
        "## Recommendations",
        "",
    ])

    if bpti_overall is not None and hewl_overall is not None:
        if bpti_overall >= 95.0 and hewl_overall >= 95.0:
            lines.append("Both proteins meet T3 threshold. No action needed. "
                         "Proceed with full 14-protein benchmark in Phase 1.")
        elif bpti_overall >= 80.0 and hewl_overall >= 80.0:
            lines.append("Both proteins above AK3 kill threshold but below T3. "
                         "Cross-agent note required flagging T3 risk for combined paper. "
                         "BPTI/HEWL remain in benchmark but combined paper viability is "
                         "reduced on this criterion.")
        else:
            lines.append("One or both proteins below AK3 threshold. "
                         "Cross-agent note required. Consider dropping affected protein(s) "
                         "from benchmark. This reduces protein count toward T5 threshold.")

    with open(output_path, 'w') as f:
        f.write("\n".join(lines) + "\n")

    logger.info(f"Threshold report written to {output_path}")

    return {
        "bpti_t3": bpti_t3, "hewl_t3": hewl_t3,
        "bpti_ak3": bpti_ak3, "hewl_ak3": hewl_ak3,
        "bpti_overall": bpti_overall, "hewl_overall": hewl_overall,
    }


def main():
    logger.info("=" * 72)
    logger.info("BioEmu Disulfide Bond Integrity Analysis")
    logger.info(f"  Start time: {datetime.now(timezone.utc).isoformat()}")
    logger.info("=" * 72)

    # Verify cysteine positions
    verify_cysteine_positions(BPTI_SEQUENCE, BPTI_SS_BONDS, "BPTI")
    verify_cysteine_positions(HEWL_SEQUENCE, HEWL_SS_BONDS, "HEWL")

    gen_times = {}

    # --- BPTI ---
    logger.info("\n" + "=" * 40)
    logger.info("PHASE 1: BPTI Conformation Generation")
    logger.info("=" * 40)

    bpti_dir, bpti_time = generate_conformations(
        BPTI_SEQUENCE, "BPTI", "task-004-bpti"
    )
    gen_times["bpti"] = bpti_time

    logger.info("\nMeasuring BPTI disulfide distances...")
    bpti_distances = measure_ss_distances(bpti_dir, BPTI_SS_BONDS, "BPTI")
    bpti_result = compute_integrity(bpti_distances, "BPTI")

    save_distances_csv(
        bpti_distances, "BPTI",
        OUTPUT_DIR / "task-004-bpti-ss-distances.csv"
    )
    generate_plot(
        bpti_distances, "BPTI", BPTI_SS_BONDS,
        OUTPUT_DIR / "task-004-bpti-ss-plot.png"
    )

    # --- HEWL ---
    logger.info("\n" + "=" * 40)
    logger.info("PHASE 2: HEWL Conformation Generation")
    logger.info("=" * 40)

    hewl_dir, hewl_time = generate_conformations(
        HEWL_SEQUENCE, "HEWL", "task-004-hewl"
    )
    gen_times["hewl"] = hewl_time

    logger.info("\nMeasuring HEWL disulfide distances...")
    hewl_distances = measure_ss_distances(hewl_dir, HEWL_SS_BONDS, "HEWL")
    hewl_result = compute_integrity(hewl_distances, "HEWL")

    save_distances_csv(
        hewl_distances, "HEWL",
        OUTPUT_DIR / "task-004-hewl-ss-distances.csv"
    )
    generate_plot(
        hewl_distances, "HEWL", HEWL_SS_BONDS,
        OUTPUT_DIR / "task-004-hewl-ss-plot.png"
    )

    # --- Combined histogram ---
    logger.info("\nGenerating combined histogram...")
    all_dists = []
    for d in list(bpti_distances.values()) + list(hewl_distances.values()):
        if d is not None:
            all_dists.extend(d.tolist())

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(all_dists, bins=50, edgecolor='black', alpha=0.7, color='#4C72B0')
    ax.axvline(x=SS_CUTOFF, color='red', linestyle='--', linewidth=2,
               label=f'Integrity cutoff ({SS_CUTOFF} A)')
    ax.axvline(x=2.04, color='green', linestyle=':', linewidth=1,
               label='Typical SS bond (2.04 A)')
    ax.set_xlabel('SG-SG Distance (Angstrom)')
    ax.set_ylabel('Count')
    ax.set_title(f'All Disulfide Bond Distances (BPTI + HEWL, N={NUM_SAMPLES} each)')
    ax.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "task-004-combined-ss-histogram.png", dpi=150)
    plt.close()

    # --- Threshold report ---
    logger.info("\nWriting threshold assessment report...")
    assessment = write_threshold_report(
        bpti_result, hewl_result, gen_times,
        OUTPUT_DIR / "task-004-ss-integrity-report.md"
    )

    # --- Save raw results JSON ---
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": MODEL_NAME,
        "bioemu_version": "1.3.1",
        "num_samples": NUM_SAMPLES,
        "ss_cutoff_angstrom": SS_CUTOFF,
        "bpti": bpti_result,
        "hewl": hewl_result,
        "generation_times": gen_times,
        "assessment": assessment,
    }
    with open(OUTPUT_DIR / "task-004-results.json", 'w') as f:
        json.dump(results, f, indent=2)

    logger.info("\n" + "=" * 72)
    logger.info("ANALYSIS COMPLETE")
    logger.info(f"  BPTI integrity: {bpti_result['overall_integrity_pct']:.1f}%")
    logger.info(f"  HEWL integrity: {hewl_result['overall_integrity_pct']:.1f}%")
    logger.info(f"  T3 (>95%): BPTI={assessment['bpti_t3']}, HEWL={assessment['hewl_t3']}")
    logger.info(f"  AK3 (<80%): BPTI={assessment['bpti_ak3']}, HEWL={assessment['hewl_ak3']}")
    logger.info(f"  End time: {datetime.now(timezone.utc).isoformat()}")
    logger.info("=" * 72)


if __name__ == "__main__":
    main()
