"""
CPA Data Adapter for Tahoe-100M

Loads Tahoe-100M expression data and converts to AnnData format
expected by CPA (Compositional Perturbation Autoencoder).

CPA requires AnnData with .obs containing:
  - perturbation: compound name
  - dose_val: dose value (float)
  - cell_type: cell line identifier
  - condition: combined perturbation+dose string
  - control: boolean flag for control (DMSO) cells

Tahoe-100M format:
  - Sparse: genes (list[int]) + expressions (list[float])
  - Metadata: drug, cell_line_id, canonical_smiles, sample, plate

Author: scgpt-cpa-setup agent (task-006)
Date: 2026-04-16
"""

import os
import json
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import anndata as ad
from pathlib import Path
from typing import Optional, Tuple, List
from scipy import sparse

# Paths
TAHOE_BASE = "/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m"
EXPR_DIR = os.path.join(TAHOE_BASE, "expression_data/data")
META_DIR = os.path.join(TAHOE_BASE, "metadata/metadata")
GENE_META = os.path.join(META_DIR, "gene_metadata.parquet")
OBS_META = os.path.join(META_DIR, "obs_metadata.parquet")


def load_gene_metadata() -> pd.DataFrame:
    """Load gene metadata mapping token_id -> gene_symbol."""
    gm = pq.read_table(GENE_META).to_pandas()
    return gm.set_index("token_id").sort_index()


def load_tahoe_shard(shard_idx: int, max_rows: Optional[int] = None) -> pd.DataFrame:
    """Load a single expression shard from Tahoe-100M."""
    fname = f"train-{shard_idx:05d}-of-03388.parquet"
    path = os.path.join(EXPR_DIR, fname)
    table = pq.read_table(path)
    if max_rows is not None:
        table = table.slice(0, max_rows)
    return table.to_pandas()


def sparse_to_csr(
    genes_list: List[List[int]],
    expressions_list: List[List[float]],
    n_genes: int = 62710,
) -> sparse.csr_matrix:
    """Convert sparse (gene_idx, expression) pairs to CSR sparse matrix.

    More memory-efficient than dense for large gene counts.
    """
    rows, cols, vals = [], [], []
    for i, (gids, expr_vals) in enumerate(zip(genes_list, expressions_list)):
        for g, v in zip(gids, expr_vals):
            if 0 <= g < n_genes:
                rows.append(i)
                cols.append(g)
                vals.append(v)

    n_cells = len(genes_list)
    return sparse.csr_matrix(
        (vals, (rows, cols)), shape=(n_cells, n_genes), dtype=np.float32
    )


def load_tahoe_for_cpa(
    cell_line: Optional[str] = None,
    drug: Optional[str] = None,
    include_control: bool = True,
    max_cells: int = 500,
    n_shards: int = 5,
    n_genes_total: int = 62710,
    control_drug: str = "DMSO",
) -> ad.AnnData:
    """Load Tahoe-100M subset and prepare for CPA.

    CPA requires .obs with perturbation, dose_val, cell_type, condition,
    and control columns. Also needs both treated and control cells.

    Args:
        cell_line: Filter by cell_line_id (e.g., "CVCL_0334")
        drug: Filter by drug name (e.g., "Goserelin (acetate)")
        include_control: If True, also load DMSO control cells
        max_cells: Maximum cells per condition
        n_shards: Number of shards to scan
        n_genes_total: Total genes in Tahoe vocabulary
        control_drug: Name of control condition (default: "DMSO")

    Returns:
        AnnData with CPA-compatible .obs
    """
    gene_meta = load_gene_metadata()

    treated_rows = []
    control_rows = []

    for shard_idx in range(n_shards):
        df = load_tahoe_shard(shard_idx)

        # Filter treated cells
        if drug is not None:
            treated = df[df["drug"] == drug]
        else:
            treated = df[df["drug"] != control_drug]

        if cell_line is not None:
            treated = treated[treated["cell_line_id"] == cell_line]

        if len(treated) > 0:
            treated_rows.append(treated)

        # Also collect control cells (same cell lines)
        if include_control:
            ctrl = df[df["drug"] == control_drug]
            if cell_line is not None:
                ctrl = ctrl[ctrl["cell_line_id"] == cell_line]
            if len(ctrl) > 0:
                control_rows.append(ctrl)

        total_treated = sum(len(r) for r in treated_rows)
        total_control = sum(len(r) for r in control_rows)
        if total_treated >= max_cells and (
            not include_control or total_control >= max_cells // 2
        ):
            break

    if not treated_rows:
        raise ValueError(
            f"No treated cells found for cell_line={cell_line}, "
            f"drug={drug} in first {n_shards} shards"
        )

    # Combine and limit
    combined_treated = pd.concat(treated_rows, ignore_index=True)
    if len(combined_treated) > max_cells:
        combined_treated = combined_treated.iloc[:max_cells]

    if include_control and control_rows:
        combined_control = pd.concat(control_rows, ignore_index=True)
        n_ctrl = min(len(combined_control), max_cells // 2)
        combined_control = combined_control.iloc[:n_ctrl]
        combined = pd.concat(
            [combined_treated, combined_control], ignore_index=True
        )
    else:
        combined = combined_treated

    # Convert sparse to CSR matrix
    X_sparse = sparse_to_csr(
        combined["genes"].tolist(),
        combined["expressions"].tolist(),
        n_genes=n_genes_total,
    )

    # Build gene names
    gene_names = []
    for i in range(n_genes_total):
        if i in gene_meta.index:
            gene_names.append(gene_meta.loc[i, "gene_symbol"])
        else:
            gene_names.append(f"gene_{i}")

    # Build CPA-compatible obs
    obs = pd.DataFrame(
        {
            "perturbation": combined["drug"].values,
            "dose_val": np.ones(len(combined)),  # Tahoe doesn't have dose in expr
            "cell_type": combined["cell_line_id"].values,
            "condition": combined["drug"].values,  # drug name as condition
            "control": (combined["drug"] == control_drug).astype(int).values,
            "sample": combined["sample"].values,
            "canonical_smiles": combined["canonical_smiles"].values,
        },
        index=[f"cell_{i}" for i in range(len(combined))],
    )

    # Create AnnData
    adata = ad.AnnData(
        X=X_sparse,
        obs=obs,
        var=pd.DataFrame(
            {"gene_name": gene_names},
            index=[f"gene_{i}" for i in range(n_genes_total)],
        ),
    )

    # Add CPA-required annotations
    adata.obs["perturbation"] = adata.obs["perturbation"].astype("category")
    adata.obs["cell_type"] = adata.obs["cell_type"].astype("category")
    adata.obs["condition"] = adata.obs["condition"].astype("category")

    return adata


if __name__ == "__main__":
    print("Testing CPA adapter...")

    # Load a small subset
    adata = load_tahoe_for_cpa(
        drug="Goserelin (acetate)",
        include_control=True,
        max_cells=200,
        n_shards=3,
    )
    print(f"Loaded AnnData: {adata.shape}")
    print(f"Sparse type: {type(adata.X)}")
    print(f"Perturbations: {adata.obs['perturbation'].unique().tolist()}")
    print(f"Cell types: {len(adata.obs['cell_type'].unique())}")
    print(f"Control cells: {adata.obs['control'].sum()}")
    print(f"Treated cells: {(1 - adata.obs['control']).sum()}")
    print(f"Memory: {adata.X.data.nbytes / 1e6:.1f} MB (sparse)")
    print("CPA adapter test PASSED")
