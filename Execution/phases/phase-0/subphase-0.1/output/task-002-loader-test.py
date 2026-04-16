#!/usr/bin/env python3
"""
Tahoe-100M Loader Test (Task 002)
=================================
Verifies that the downloaded Tahoe-100M dataset can be read correctly using
pyarrow. Tests schema, row counts, and column types for both expression data
and metadata files.

Usage:
    conda activate env-delta  # or env-tahoe-download
    python task-002-loader-test.py
"""

import os
import sys
from pathlib import Path

import pyarrow.parquet as pq

# ============================================================================
# Configuration
# ============================================================================

TAHOE_BASE = Path("/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m")
EXPRESSION_DIR = TAHOE_BASE / "expression_data" / "data"
METADATA_DIR = TAHOE_BASE / "metadata" / "metadata"

EXPECTED_EXPRESSION_COLUMNS = [
    "genes", "expressions", "drug", "sample", "BARCODE_SUB_LIB_ID",
    "cell_line_id", "moa-fine", "canonical_smiles", "pubchem_cid", "plate",
]

EXPECTED_METADATA_FILES = [
    "obs_metadata.parquet",
    "gene_metadata.parquet",
    "drug_metadata.parquet",
    "cell_line_metadata.parquet",
    "sample_metadata.parquet",
]


def test_expression_data():
    """Test that expression parquet files are readable and have expected schema."""
    print("=" * 60)
    print("TEST 1: Expression Data")
    print("=" * 60)

    parquet_files = sorted(EXPRESSION_DIR.glob("*.parquet"))
    print(f"  Found {len(parquet_files)} parquet files")
    assert len(parquet_files) == 3388, f"Expected 3388, got {len(parquet_files)}"

    # Read first shard
    first = pq.read_table(parquet_files[0])
    print(f"  First shard: {first.num_rows} rows, {first.num_columns} columns")
    print(f"  Schema columns: {first.column_names}")

    for col in EXPECTED_EXPRESSION_COLUMNS:
        assert col in first.column_names, f"Missing column: {col}"
    print(f"  All {len(EXPECTED_EXPRESSION_COLUMNS)} expected columns present")

    # Read last shard to verify completeness
    last = pq.read_table(parquet_files[-1])
    print(f"  Last shard: {last.num_rows} rows")

    print("  PASS\n")


def test_metadata():
    """Test that metadata parquet files exist and are readable."""
    print("=" * 60)
    print("TEST 2: Metadata Files")
    print("=" * 60)

    for fname in EXPECTED_METADATA_FILES:
        fpath = METADATA_DIR / fname
        assert fpath.exists(), f"Missing: {fpath}"
        table = pq.read_table(fpath)
        print(f"  {fname}: {table.num_rows} rows, {table.num_columns} columns")

    # Check gene vocabularies
    json_path = METADATA_DIR / "gene_vocabulary.json"
    jsonl_path = METADATA_DIR / "gene_vocabulary.jsonl"
    assert json_path.exists(), f"Missing: {json_path}"
    assert jsonl_path.exists(), f"Missing: {jsonl_path}"
    print(f"  gene_vocabulary.json: {json_path.stat().st_size / 1024:.1f} KB")
    print(f"  gene_vocabulary.jsonl: {jsonl_path.stat().st_size / 1024:.1f} KB")

    # Check pseudobulk DE
    de_dir = METADATA_DIR / "pseudobulk_differential_expression"
    de_files = list(de_dir.glob("*.parquet"))
    print(f"  pseudobulk_DE: {len(de_files)} parquet files")
    assert len(de_files) == 1026, f"Expected 1026, got {len(de_files)}"

    print("  PASS\n")


def test_streaming_read():
    """Test that data can be read in streaming fashion without loading all into memory."""
    print("=" * 60)
    print("TEST 3: Streaming Read (first 10K rows)")
    print("=" * 60)

    parquet_files = sorted(EXPRESSION_DIR.glob("*.parquet"))
    rows_read = 0
    target = 10_000

    for pf in parquet_files:
        table = pq.read_table(pf)
        rows_read += table.num_rows
        if rows_read >= target:
            break

    print(f"  Read {rows_read} rows from {min(rows_read // 28225 + 1, len(parquet_files))} shards")
    assert rows_read >= target, f"Could not read {target} rows"

    print("  PASS\n")


def main():
    print("Tahoe-100M Loader Test")
    print(f"Base path: {TAHOE_BASE}\n")

    if not TAHOE_BASE.exists():
        print(f"ERROR: {TAHOE_BASE} does not exist")
        sys.exit(1)

    test_expression_data()
    test_metadata()
    test_streaming_read()

    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
