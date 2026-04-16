#!/usr/bin/env python3
"""Verify Tahoe-100M download completeness and test streaming loader."""

import os
import sys

TARGET = "/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m"

def count_files(path, ext=None):
    count = 0
    total_bytes = 0
    for dp, dn, fnames in os.walk(path):
        for fn in fnames:
            if ext is None or fn.endswith(ext):
                fp = os.path.join(dp, fn)
                if os.path.isfile(fp):
                    count += 1
                    total_bytes += os.path.getsize(fp)
    return count, total_bytes

print("=== Tahoe-100M Download Verification ===\n")

# 1. Expression data
expr_dir = os.path.join(TARGET, "expression_data", "data")
if os.path.isdir(expr_dir):
    n, sz = count_files(expr_dir, ".parquet")
    print(f"expression_data:  {n} parquet files, {sz/1e9:.2f} GB")
    assert n == 3388, f"Expected 3388, got {n}"
    print(f"  PASS (3388 files)")
else:
    print(f"  FAIL: {expr_dir} not found")
    sys.exit(1)

# 2. Metadata files
meta_dir = os.path.join(TARGET, "metadata", "metadata")
if os.path.isdir(meta_dir):
    # Small metadata parquets at top level
    for name in ["cell_line_metadata", "drug_metadata", "gene_metadata",
                  "obs_metadata", "sample_metadata"]:
        fp = os.path.join(meta_dir, f"{name}.parquet")
        if os.path.isfile(fp):
            sz = os.path.getsize(fp)
            print(f"{name}:  {sz/1e6:.2f} MB  PASS")
        else:
            print(f"{name}:  MISSING")

    # Pseudobulk DE
    de_dir = os.path.join(meta_dir, "pseudobulk_differential_expression")
    if os.path.isdir(de_dir):
        n, sz = count_files(de_dir, ".parquet")
        print(f"pseudobulk_DE:  {n} parquet files, {sz/1e9:.2f} GB")
        assert n == 1026, f"Expected 1026, got {n}"
        print(f"  PASS (1026 files)")
    else:
        print(f"  pseudobulk_DE dir not found")
else:
    print(f"  metadata dir not found at {meta_dir}")

# 3. Gene vocabulary
for fn in ["gene_vocabulary.json", "gene_vocabulary.jsonl"]:
    fp = os.path.join(meta_dir, fn)
    if os.path.isfile(fp):
        print(f"{fn}:  {os.path.getsize(fp)/1e6:.2f} MB  PASS")
    else:
        print(f"{fn}:  MISSING")

# 4. Total size
n_total, sz_total = count_files(TARGET)
print(f"\nTotal: {n_total} files, {sz_total/1e9:.2f} GB")

# 5. Test streaming loader
print("\n=== Streaming Loader Test ===")
try:
    import pyarrow.parquet as pq
    # Read first expression file
    test_file = os.path.join(expr_dir, "train-00000-of-03388.parquet")
    table = pq.read_table(test_file)
    print(f"Expression file schema: {len(table.schema)} columns, {len(table)} rows")
    print(f"  Columns (first 10): {table.schema.names[:10]}")
    print(f"  PASS: streaming loader works")

    # Read a metadata file
    obs_file = os.path.join(meta_dir, "obs_metadata.parquet")
    if os.path.isfile(obs_file):
        obs = pq.read_table(obs_file, columns=["cell_type"])
        print(f"obs_metadata: {len(obs)} rows")
        print(f"  PASS: metadata readable")
except Exception as e:
    print(f"  Loader test failed: {e}")

print("\n=== Verification Complete ===")
