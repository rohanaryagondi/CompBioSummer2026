#!/usr/bin/env python3
"""
Tahoe-100M Dataset Download Script
===================================
Downloads the full Tahoe-100M dataset from Hugging Face (tahoebio/Tahoe-100M)
to HPC scratch storage using huggingface_hub's snapshot_download with resume
support.

Dataset: tahoebio/Tahoe-100M
Format: Parquet (3,388 expression data files + metadata subsets)
Total download size: ~337 GB (expression_data) + metadata (~92 GB other subsets)
License: CC0-1.0

Usage:
    python task-002-download-script.py

The script:
1. Downloads all subsets of tahoebio/Tahoe-100M to the target directory
2. Logs progress with timestamps and byte counts
3. Supports resume on interruption (huggingface_hub handles this natively)
4. Writes a completion marker file when done
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from huggingface_hub import snapshot_download, HfApi

# ============================================================================
# Configuration
# ============================================================================

DATASET_REPO = "tahoebio/Tahoe-100M"
TARGET_DIR = "/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m"
LOG_DIR = "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/output"
COMPLETION_MARKER = os.path.join(TARGET_DIR, ".download_complete")
PROGRESS_LOG = os.path.join(LOG_DIR, "task-002-download-progress.log")

# Subsets to download -- all 7 configurations of the dataset
# The main expression_data is the default config and lives in data/
# Other configs are in separate directories
SUBSETS = [
    "expression_data",        # Main data: ~337 GB, 3388 parquet files, 95.6M rows
    "obs_metadata",           # Cell-level metadata: 101M rows
    "pseudobulk_differential_expression",  # DE results: 4.09B rows
    "gene_metadata",          # Gene annotations: 62.7K rows
    "sample_metadata",        # Sample info: 1.34K rows
    "drug_metadata",          # Drug info: 379 rows
    "cell_line_metadata",     # Cell line info: ~1K rows
]

# ============================================================================
# Logging setup
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(PROGRESS_LOG),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def get_dir_size(path):
    """Get total size of a directory in bytes."""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total


def format_size(size_bytes):
    """Format bytes to human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def download_subset(subset_name, target_base_dir):
    """
    Download a single subset/configuration of the Tahoe-100M dataset.

    Each subset is stored in its own subdirectory under the main repo.
    The huggingface_hub snapshot_download handles resume automatically.
    """
    subset_dir = os.path.join(target_base_dir, subset_name)
    os.makedirs(subset_dir, exist_ok=True)

    logger.info(f"--- Starting download of subset: {subset_name} ---")
    logger.info(f"  Target directory: {subset_dir}")

    start_time = time.time()

    try:
        # snapshot_download downloads the entire repo or specific patterns
        # For the default config (expression_data), files are in data/
        # For other configs, files are in <config_name>/
        if subset_name == "expression_data":
            # The main expression data is in the data/ directory
            result_path = snapshot_download(
                repo_id=DATASET_REPO,
                repo_type="dataset",
                local_dir=subset_dir,
                allow_patterns=["data/*"],
                resume_download=True,
                max_workers=4,
            )
        else:
            # Other subsets are in their own directories
            result_path = snapshot_download(
                repo_id=DATASET_REPO,
                repo_type="dataset",
                local_dir=subset_dir,
                allow_patterns=[f"{subset_name}/*"],
                resume_download=True,
                max_workers=4,
            )

        elapsed = time.time() - start_time
        dir_size = get_dir_size(subset_dir)

        logger.info(f"  Completed: {subset_name}")
        logger.info(f"  Downloaded to: {result_path}")
        logger.info(f"  Size on disk: {format_size(dir_size)}")
        logger.info(f"  Elapsed time: {elapsed:.1f}s ({elapsed/3600:.2f}h)")

        if elapsed > 0:
            rate = dir_size / elapsed
            logger.info(f"  Average rate: {format_size(rate)}/s")

        return {
            "subset": subset_name,
            "status": "success",
            "path": result_path,
            "size_bytes": dir_size,
            "elapsed_seconds": elapsed,
        }

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"  FAILED: {subset_name} after {elapsed:.1f}s: {e}")
        return {
            "subset": subset_name,
            "status": "failed",
            "error": str(e),
            "elapsed_seconds": elapsed,
        }


def main():
    """Main download orchestrator."""
    logger.info("=" * 72)
    logger.info("Tahoe-100M Download Script")
    logger.info(f"  Repository: {DATASET_REPO}")
    logger.info(f"  Target dir: {TARGET_DIR}")
    logger.info(f"  Start time: {datetime.now(timezone.utc).isoformat()}")
    logger.info(f"  Subsets to download: {len(SUBSETS)}")
    logger.info("=" * 72)

    # Check if already completed
    if os.path.exists(COMPLETION_MARKER):
        logger.info("Download already marked as complete. To re-download, remove:")
        logger.info(f"  {COMPLETION_MARKER}")
        return

    os.makedirs(TARGET_DIR, exist_ok=True)

    # Track results
    results = []
    overall_start = time.time()

    # Download each subset
    # Priority order: small metadata first (fast, useful for verification),
    # then the large expression data last
    priority_order = [
        "gene_metadata",          # Tiny, needed for gene mapping
        "drug_metadata",          # Tiny, needed for compound info
        "cell_line_metadata",     # Tiny, needed for cell line info
        "sample_metadata",        # Small, needed for sample linking
        "obs_metadata",           # Medium-large, cell-level annotations
        "expression_data",        # Largest: ~337 GB
        "pseudobulk_differential_expression",  # Large: DE results
    ]

    for subset in priority_order:
        result = download_subset(subset, TARGET_DIR)
        results.append(result)

        # Log cumulative progress
        total_downloaded = sum(
            r.get("size_bytes", 0) for r in results if r["status"] == "success"
        )
        logger.info(f"  Cumulative downloaded: {format_size(total_downloaded)}")

    # Summary
    overall_elapsed = time.time() - overall_start
    total_size = get_dir_size(TARGET_DIR)
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]

    logger.info("")
    logger.info("=" * 72)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("=" * 72)
    logger.info(f"  Total time: {overall_elapsed:.1f}s ({overall_elapsed/3600:.2f}h)")
    logger.info(f"  Total size on disk: {format_size(total_size)}")
    logger.info(f"  Successful subsets: {len(successful)}/{len(SUBSETS)}")
    logger.info(f"  Failed subsets: {len(failed)}/{len(SUBSETS)}")

    if failed:
        logger.warning("  Failed subsets:")
        for r in failed:
            logger.warning(f"    - {r['subset']}: {r.get('error', 'unknown')}")

    # Write completion marker
    if len(failed) == 0:
        marker_data = {
            "status": "complete",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_size_bytes": total_size,
            "total_elapsed_seconds": overall_elapsed,
            "subsets": results,
            "dataset_repo": DATASET_REPO,
        }
        with open(COMPLETION_MARKER, "w") as f:
            json.dump(marker_data, f, indent=2)
        logger.info(f"  Completion marker written: {COMPLETION_MARKER}")
    else:
        logger.warning("  NOT writing completion marker due to failures.")
        logger.warning("  Re-run this script to retry failed subsets (resume support).")

    # Write results JSON for verification script
    results_path = os.path.join(TARGET_DIR, "download_results.json")
    with open(results_path, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "results": results,
                "total_size_bytes": total_size,
                "total_elapsed_seconds": overall_elapsed,
            },
            f,
            indent=2,
        )
    logger.info(f"  Results JSON written: {results_path}")

    # Exit with error code if any subset failed
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
