"""
scGPT Data Adapter for Tahoe-100M

Loads Tahoe-100M expression data (sparse parquet format) and converts it
to the format expected by scGPT's TransformerGenerator for perturbation
prediction.

Tahoe-100M format:
  - genes: list[int]  (indices into 62,710-gene vocabulary)
  - expressions: list[float]  (raw counts, sparse — only nonzero stored)
  - drug: str
  - cell_line_id: str
  - canonical_smiles: str
  - sample: str, plate: str, etc.

scGPT format:
  - AnnData with dense gene expression matrix (cells x genes)
  - .var["gene_name"] = gene symbols
  - Gene vocabulary (vocab.json) maps gene symbols -> token IDs
  - Tokenization bins expression values into discrete tokens

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

# Paths
TAHOE_BASE = "/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m"
EXPR_DIR = os.path.join(TAHOE_BASE, "expression_data/data")
META_DIR = os.path.join(TAHOE_BASE, "metadata/metadata")
GENE_META = os.path.join(META_DIR, "gene_metadata.parquet")
GENE_VOCAB_JSON = os.path.join(META_DIR, "gene_vocabulary.json")
OBS_META = os.path.join(META_DIR, "obs_metadata.parquet")
DRUG_META = os.path.join(META_DIR, "drug_metadata.parquet")


def load_gene_metadata() -> pd.DataFrame:
    """Load gene metadata mapping token_id -> gene_symbol."""
    gm = pq.read_table(GENE_META).to_pandas()
    return gm.set_index("token_id").sort_index()


def load_tahoe_shard(shard_idx: int, max_rows: Optional[int] = None) -> pd.DataFrame:
    """Load a single expression shard from Tahoe-100M.

    Args:
        shard_idx: Shard number (0-3387)
        max_rows: Maximum rows to load (None = all)

    Returns:
        DataFrame with columns: genes, expressions, drug, cell_line_id, etc.
    """
    fname = f"train-{shard_idx:05d}-of-03388.parquet"
    path = os.path.join(EXPR_DIR, fname)
    table = pq.read_table(path)
    if max_rows is not None:
        table = table.slice(0, max_rows)
    return table.to_pandas()


def sparse_to_dense(
    genes_list: List[List[int]],
    expressions_list: List[List[float]],
    n_genes: int = 62710,
) -> np.ndarray:
    """Convert sparse (gene_idx, expression) pairs to dense matrix.

    Args:
        genes_list: List of gene index arrays per cell
        expressions_list: List of expression value arrays per cell
        n_genes: Total number of genes in vocabulary

    Returns:
        Dense matrix of shape (n_cells, n_genes)
    """
    n_cells = len(genes_list)
    dense = np.zeros((n_cells, n_genes), dtype=np.float32)
    for i, (gids, vals) in enumerate(zip(genes_list, expressions_list)):
        for g, v in zip(gids, vals):
            if 0 <= g < n_genes:
                dense[i, g] = v
    return dense


def load_tahoe_for_scgpt(
    cell_line: Optional[str] = None,
    drug: Optional[str] = None,
    max_cells: int = 500,
    n_shards: int = 5,
    n_genes_total: int = 62710,
) -> Tuple[ad.AnnData, pd.DataFrame]:
    """Load Tahoe-100M subset and prepare for scGPT inference.

    Scans up to n_shards parquet files, filters by cell_line and/or drug,
    converts sparse expression to dense AnnData format.

    Args:
        cell_line: Filter by cell_line_id (e.g., "CVCL_0334")
        drug: Filter by drug name (e.g., "Bortezomib")
        max_cells: Maximum number of cells to load
        n_shards: Number of shards to scan
        n_genes_total: Total genes in Tahoe vocabulary

    Returns:
        Tuple of (AnnData, gene_metadata DataFrame)
    """
    gene_meta = load_gene_metadata()

    collected_rows = []
    for shard_idx in range(n_shards):
        df = load_tahoe_shard(shard_idx)

        # Filter
        if cell_line is not None:
            df = df[df["cell_line_id"] == cell_line]
        if drug is not None:
            df = df[df["drug"] == drug]

        if len(df) > 0:
            collected_rows.append(df)

        total = sum(len(r) for r in collected_rows)
        if total >= max_cells:
            break

    if not collected_rows:
        raise ValueError(
            f"No cells found for cell_line={cell_line}, drug={drug} "
            f"in first {n_shards} shards"
        )

    combined = pd.concat(collected_rows, ignore_index=True)
    if len(combined) > max_cells:
        combined = combined.iloc[:max_cells]

    # Convert sparse to dense
    dense_expr = sparse_to_dense(
        combined["genes"].tolist(),
        combined["expressions"].tolist(),
        n_genes=n_genes_total,
    )

    # Build gene names array from gene_meta
    gene_names = []
    for i in range(n_genes_total):
        if i in gene_meta.index:
            gene_names.append(gene_meta.loc[i, "gene_symbol"])
        else:
            gene_names.append(f"gene_{i}")

    # Create AnnData
    adata = ad.AnnData(
        X=dense_expr,
        obs=pd.DataFrame(
            {
                "drug": combined["drug"].values,
                "cell_line_id": combined["cell_line_id"].values,
                "sample": combined["sample"].values,
                "canonical_smiles": combined["canonical_smiles"].values,
            },
            index=[f"cell_{i}" for i in range(len(combined))],
        ),
        var=pd.DataFrame(
            {"gene_name": gene_names},
            index=[f"gene_{i}" for i in range(n_genes_total)],
        ),
    )

    return adata, gene_meta


def prepare_scgpt_inputs(
    adata: ad.AnnData,
    vocab_path: str,
    max_seq_len: int = 1200,
    n_bins: int = 51,
) -> dict:
    """Prepare scGPT-compatible tokenized inputs from AnnData.

    Args:
        adata: AnnData with dense expression matrix
        vocab_path: Path to scGPT vocab.json
        max_seq_len: Maximum sequence length for the transformer
        n_bins: Number of bins for expression value discretization

    Returns:
        Dictionary with gene_ids, binned_values, and metadata
    """
    import warnings
    warnings.filterwarnings("ignore")

    # Load scGPT vocabulary
    from scgpt.tokenizer import GeneVocab

    vocab = GeneVocab.from_file(vocab_path)

    # Map Tahoe gene names to scGPT vocab IDs
    gene_names = adata.var["gene_name"].values
    gene_ids_in_vocab = np.array(
        [vocab[g] if g in vocab else vocab["<pad>"] for g in gene_names],
        dtype=np.int64,
    )

    # Count how many genes are in vocab
    n_matched = np.sum(gene_ids_in_vocab != vocab["<pad>"])
    print(f"Genes matched to scGPT vocab: {n_matched}/{len(gene_names)}")

    # Bin expression values
    X = adata.X.copy()
    # Log1p transform
    X = np.log1p(np.abs(X))
    # Bin into n_bins levels
    nonzero_mask = X > 0
    if nonzero_mask.any():
        nonzero_vals = X[nonzero_mask]
        bins = np.quantile(nonzero_vals, np.linspace(0, 1, n_bins))
        X_binned = np.digitize(X, bins)
    else:
        X_binned = np.zeros_like(X, dtype=np.int64)

    return {
        "gene_ids": gene_ids_in_vocab,
        "expression_values": adata.X,
        "binned_values": X_binned,
        "vocab": vocab,
        "n_matched": int(n_matched),
        "max_seq_len": max_seq_len,
    }


if __name__ == "__main__":
    print("Testing scGPT adapter...")

    # Load a small subset (Goserelin is common in early shards)
    adata, gene_meta = load_tahoe_for_scgpt(
        drug="Goserelin (acetate)",
        max_cells=100,
        n_shards=3,
    )
    print(f"Loaded AnnData: {adata.shape}")
    print(f"Drugs: {adata.obs['drug'].unique()}")
    print(f"Cell lines: {adata.obs['cell_line_id'].unique()}")

    # Prepare scGPT inputs
    vocab_path = (
        "/nfs/roberts/scratch/pi_mg269/rag88/delta/methods/scgpt/"
        "pretrained/scGPT_human/vocab.json"
    )
    inputs = prepare_scgpt_inputs(adata, vocab_path)
    print(f"Gene IDs shape: {inputs['gene_ids'].shape}")
    print(f"Binned values shape: {inputs['binned_values'].shape}")
    print(f"Genes matched: {inputs['n_matched']}")
    print("scGPT adapter test PASSED")
