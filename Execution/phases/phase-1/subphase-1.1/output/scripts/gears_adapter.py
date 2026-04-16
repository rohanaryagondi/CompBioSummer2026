#!/usr/bin/env python
"""
GEARS Data Adapter for Tahoe-100M
==================================
Converts Tahoe-100M parquet expression data into GEARS-compatible AnnData format.

Tahoe-100M stores data as:
  - expression_data: sparse (gene_indices, expression_values) per cell
  - obs_metadata: cell metadata with drug, cell_line, etc.
  - gene_metadata: gene_symbol, ensembl_id, token_id

GEARS expects AnnData with:
  - .X: dense or sparse expression matrix (cells x genes)
  - .obs['condition']: perturbation label (drug name or 'ctrl')
  - .obs['cell_type']: cell type/cell line identifier
  - .var['gene_name']: gene symbol
"""

import os
import sys
import numpy as np
import pandas as pd
import anndata as ad
import pyarrow.parquet as pq
import scipy.sparse as sp
from pathlib import Path
from typing import Optional, List, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# Tahoe-100M paths
TAHOE_BASE = "/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m"
EXPR_DIR = os.path.join(TAHOE_BASE, "expression_data", "data")
META_DIR = os.path.join(TAHOE_BASE, "metadata", "metadata")
GENE_META = os.path.join(META_DIR, "gene_metadata.parquet")
OBS_META = os.path.join(META_DIR, "obs_metadata.parquet")
DRUG_META = os.path.join(META_DIR, "drug_metadata.parquet")

# Tahoe-100M vehicle control drug name
CONTROL_DRUG = "DMSO_TF"

# Total number of parquet files
N_PARQUETS = 3388


def load_drug_targets() -> dict:
    """Load drug-to-target gene mapping from Tahoe metadata.

    GEARS was designed for genetic perturbations (gene names as condition labels).
    For chemical perturbations like Tahoe-100M, we map drugs to their known
    target genes. This allows GEARS to use the gene perturbation index feature.

    Returns dict: drug_name -> first target gene symbol (or None if unknown).
    """
    drug_df = pq.read_table(DRUG_META).to_pandas()
    mapping = {}
    for _, row in drug_df.iterrows():
        drug = row['drug']
        targets = row.get('targets', None)
        if targets and targets not in ('None', '', 'unclear'):
            # Take first target gene (e.g., "MTOR, FKBP1A" -> "MTOR")
            first_target = targets.split(',')[0].strip()
            mapping[drug] = first_target
        else:
            mapping[drug] = None
    logger.info(f"Loaded drug targets: {sum(v is not None for v in mapping.values())} "
                f"of {len(mapping)} drugs have known targets")
    return mapping


def load_gene_metadata() -> pd.DataFrame:
    """Load gene metadata (symbol, ensembl_id, token_id)."""
    gene_df = pq.read_table(GENE_META).to_pandas()
    logger.info(f"Loaded {len(gene_df)} genes from gene_metadata")
    return gene_df


def scan_parquets_for_condition(
    drug: str,
    cell_line: Optional[str] = None,
    max_parquets: int = 20,
    max_cells: Optional[int] = None,
) -> Tuple[List[dict], int]:
    """
    Scan parquet files to find cells matching a drug + cell_line condition.

    Returns list of dicts with 'genes', 'expressions', and metadata,
    plus total count found.
    """
    cells = []
    total_found = 0

    for i in range(min(max_parquets, N_PARQUETS)):
        fname = os.path.join(EXPR_DIR, f"train-{i:05d}-of-{N_PARQUETS:05d}.parquet")
        if not os.path.exists(fname):
            continue

        table = pq.read_table(fname)
        df = table.to_pandas()

        # Filter by drug
        mask = df['drug'] == drug
        if cell_line:
            mask = mask & (df['cell_line_id'] == cell_line)

        subset = df[mask]
        total_found += len(subset)

        for _, row in subset.iterrows():
            cells.append({
                'genes': row['genes'],
                'expressions': row['expressions'],
                'drug': row['drug'],
                'cell_line_id': row['cell_line_id'],
                'sample': row['sample'],
            })

            if max_cells and len(cells) >= max_cells:
                logger.info(f"Reached max_cells={max_cells} after scanning {i+1} parquets")
                return cells, total_found

    logger.info(f"Found {len(cells)} cells for drug={drug}, cell_line={cell_line} "
                f"across {min(max_parquets, N_PARQUETS)} parquets")
    return cells, total_found


def sparse_to_dense(gene_indices: list, expr_values: list, n_genes: int) -> np.ndarray:
    """Convert Tahoe sparse (indices, values) to dense vector."""
    dense = np.zeros(n_genes, dtype=np.float32)
    for idx, val in zip(gene_indices, expr_values):
        if idx < n_genes:
            dense[idx] = val
    return dense


def build_anndata(
    drug: str = None,
    drugs: Optional[List[str]] = None,
    cell_line: Optional[str] = None,
    max_cells: int = 10000,
    max_parquets: int = 50,
    include_control: bool = True,
    max_control_cells: Optional[int] = None,
    n_top_genes: Optional[int] = None,
) -> ad.AnnData:
    """
    Build GEARS-compatible AnnData from Tahoe-100M data.

    Args:
        drug: Single drug name (for backward compatibility).
        drugs: List of drug names. If provided, overrides 'drug'. GEARS needs >=3
               unique perturbation conditions for proper train/val/test splitting.
        cell_line: Optional cell line filter (e.g., 'CVCL_0546').
        max_cells: Maximum perturbation cells to include PER DRUG.
        max_parquets: Maximum parquet files to scan per drug.
        include_control: Whether to include DMSO_TF control cells.
        max_control_cells: Cap on control cells (default: same as max_cells).
        n_top_genes: If set, subset to top N highly variable genes.

    Returns:
        AnnData with .obs['condition'], .obs['cell_type'], .var['gene_name'].
    """
    # Handle single-drug backward compatibility
    if drugs is None:
        if drug is None:
            raise ValueError("Must provide either 'drug' or 'drugs'")
        drugs = [drug]

    logger.info(f"Building AnnData for drugs={drugs}, cell_line={cell_line}, "
                f"max_cells={max_cells}")

    # Load gene metadata
    gene_df = load_gene_metadata()
    n_genes = len(gene_df)

    # Collect perturbation cells for all drugs
    pert_cells = []
    for d in drugs:
        logger.info(f"Scanning for perturbation cells (drug={d})...")
        d_cells, _ = scan_parquets_for_condition(
            drug=d,
            cell_line=cell_line,
            max_parquets=max_parquets,
            max_cells=max_cells,
        )
        logger.info(f"Collected {len(d_cells)} cells for drug={d}")
        pert_cells.extend(d_cells)
    logger.info(f"Total perturbation cells collected: {len(pert_cells)}")

    # Collect control cells
    ctrl_cells = []
    if include_control:
        if max_control_cells is None:
            max_control_cells = max_cells
        logger.info("Scanning for control (DMSO_TF) cells...")
        ctrl_cells, _ = scan_parquets_for_condition(
            drug=CONTROL_DRUG,
            cell_line=cell_line,
            max_parquets=max_parquets,
            max_cells=max_control_cells,
        )
        logger.info(f"Collected {len(ctrl_cells)} control cells")

    all_cells = pert_cells + ctrl_cells
    if len(all_cells) == 0:
        raise ValueError(f"No cells found for drug={drug}, cell_line={cell_line}")

    # Build token_id to column index mapping
    # Expression data uses token_ids (3-62712), not row indices (0-62709)
    # token_ids 1-2 are special tokens (PAD, etc.) not in gene metadata
    token_to_col = {tid: i for i, tid in enumerate(gene_df['token_id'].values)}
    logger.info(f"Token-to-column mapping: {len(token_to_col)} entries, "
                f"token range [{min(token_to_col)}, {max(token_to_col)}]")

    # Build expression matrix (sparse for memory efficiency)
    logger.info(f"Building expression matrix: {len(all_cells)} cells x {n_genes} genes")
    rows, cols, data = [], [], []
    skipped = 0
    for i, cell in enumerate(all_cells):
        for token_id, expr_val in zip(cell['genes'], cell['expressions']):
            col = token_to_col.get(token_id)
            if col is not None:
                rows.append(i)
                cols.append(col)
                data.append(expr_val)
            else:
                skipped += 1  # Special tokens (1, 2) not in gene metadata

    if skipped > 0:
        logger.info(f"Skipped {skipped} entries with unmapped token_ids (special tokens)")

    X = sp.csr_matrix(
        (data, (rows, cols)),
        shape=(len(all_cells), n_genes),
        dtype=np.float32,
    )

    # Build obs DataFrame
    obs_data = []
    for cell in all_cells:
        is_ctrl = cell['drug'] == CONTROL_DRUG
        obs_data.append({
            'condition': 'ctrl' if is_ctrl else cell['drug'],
            'cell_type': cell['cell_line_id'],
            'drug_original': cell['drug'],
            'sample': cell['sample'],
        })
    obs_df = pd.DataFrame(obs_data)
    obs_df.index = [f"cell_{i}" for i in range(len(obs_df))]

    # Build var DataFrame
    var_df = pd.DataFrame({
        'gene_name': gene_df['gene_symbol'].values,
        'ensembl_id': gene_df['ensembl_id'].values,
        'token_id': gene_df['token_id'].values,
    })
    var_df.index = gene_df['gene_symbol'].values

    # Create AnnData
    adata = ad.AnnData(X=X, obs=obs_df, var=var_df)

    # GEARS compatibility: remap drug names to target gene names
    # GEARS expects condition labels to be gene names (for genetic perturbation
    # index lookup). For chemical perturbations, we map each drug to its
    # primary target gene. Drugs without known targets get a synthetic label.
    drug_targets = load_drug_targets()
    gene_set = set(gene_df['gene_symbol'].values)

    def map_condition(cond):
        if cond == 'ctrl':
            return 'ctrl'
        target = drug_targets.get(cond)
        if target and target in gene_set:
            # GEARS expects single perturbation format: "GENE+ctrl"
            # The "+ctrl" suffix tells GEARS this is a single-gene perturbation
            # (vs combo perturbation like "GENE1+GENE2")
            return f"{target}+ctrl"
        # If target not in gene list or no target known, use synthetic label
        # GEARS will skip perturbation index for this condition
        return cond

    adata.obs['condition_drug'] = adata.obs['condition'].copy()  # Keep original
    adata.obs['condition'] = adata.obs['condition'].apply(map_condition)

    # Filter: GEARS requires condition labels to be gene names in var.gene_name
    # Remove cells whose mapped condition is not in the gene list (and is not 'ctrl')
    # Valid conditions are: 'ctrl', 'GENE+ctrl' where GENE is in gene_set
    valid_conditions = {'ctrl'} | {f"{g}+ctrl" for g in gene_set}
    valid_mask = adata.obs['condition'].isin(valid_conditions)
    n_dropped = (~valid_mask).sum()
    if n_dropped > 0:
        logger.warning(f"Dropping {n_dropped} cells with unmapped drug targets "
                       f"(condition not in gene list)")
        adata = adata[valid_mask].copy()

    logger.info(f"AnnData shape: {adata.shape}")
    logger.info(f"Conditions (gene-mapped): {adata.obs['condition'].value_counts().to_dict()}")
    logger.info(f"Cell types: {adata.obs['cell_type'].value_counts().to_dict()}")

    # Optional: subset to highly variable genes for memory reduction
    if n_top_genes and n_top_genes < n_genes:
        import scanpy as sc
        # Filter out genes with zero expression across all cells first
        gene_sums = np.array(adata.X.sum(axis=0)).flatten()
        nonzero_mask = gene_sums > 0
        adata = adata[:, nonzero_mask].copy()
        logger.info(f"After zero-gene filter: {adata.shape}")

        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)

        # Identify perturbation target genes that MUST be retained
        # GEARS needs to find condition gene names in var.gene_name
        # Condition format is "GENE+ctrl", so extract gene names
        raw_conds = set(adata.obs['condition'].unique()) - {'ctrl'}
        pert_genes = set()
        for c in raw_conds:
            for g in c.split('+'):
                if g != 'ctrl':
                    pert_genes.add(g)
        pert_gene_mask = adata.var['gene_name'].isin(pert_genes)
        n_pert_genes = pert_gene_mask.sum()
        logger.info(f"Perturbation target genes to preserve: {n_pert_genes}")

        try:
            target_hvg = max(1, n_top_genes - n_pert_genes)
            sc.pp.highly_variable_genes(adata, n_top_genes=min(target_hvg, adata.shape[1]))
            # Ensure perturbation genes are always marked as highly variable
            adata.var.loc[pert_gene_mask, 'highly_variable'] = True
            adata = adata[:, adata.var.highly_variable].copy()
        except Exception as e:
            logger.warning(f"HVG selection failed ({e}), using variance-based selection")
            if sp.issparse(adata.X):
                variances = np.array(adata.X.power(2).mean(axis=0) -
                                     np.power(adata.X.mean(axis=0), 2)).flatten()
            else:
                variances = np.var(adata.X, axis=0)
            # Always include perturbation target genes
            keep_mask = np.zeros(adata.shape[1], dtype=bool)
            keep_mask[pert_gene_mask.values] = True
            remaining = n_top_genes - keep_mask.sum()
            if remaining > 0:
                var_order = np.argsort(variances)[::-1]
                for idx in var_order:
                    if not keep_mask[idx]:
                        keep_mask[idx] = True
                        remaining -= 1
                        if remaining <= 0:
                            break
            adata = adata[:, keep_mask].copy()
        logger.info(f"After HVG selection: {adata.shape}")
        # Verify perturbation genes are present
        for pg in pert_genes:
            if pg not in adata.var['gene_name'].values:
                logger.error(f"CRITICAL: perturbation gene {pg} missing from var!")

    return adata


def save_for_gears(adata: ad.AnnData, output_dir: str, dataset_name: str = "tahoe_test"):
    """Save AnnData in GEARS-expected format."""
    save_dir = os.path.join(output_dir, dataset_name)
    os.makedirs(save_dir, exist_ok=True)
    h5ad_path = os.path.join(save_dir, "perturb_processed.h5ad")
    adata.write_h5ad(h5ad_path)
    logger.info(f"Saved AnnData to {h5ad_path}")
    return save_dir


if __name__ == "__main__":
    """Quick test: build a small AnnData for GEARS validation."""

    # Test with a small condition
    print("=" * 60)
    print("GEARS Adapter Test: Loading Tahoe-100M subset")
    print("=" * 60)

    # Use Rapamycin as test drug (well-known mTOR inhibitor, common in perturbation studies)
    test_drug = "Rapamycin"
    test_cell_line = None  # All cell lines
    test_max_cells = 500

    adata = build_anndata(
        drug=test_drug,
        cell_line=test_cell_line,
        max_cells=test_max_cells,
        max_parquets=20,
        include_control=True,
        max_control_cells=500,
    )

    print(f"\nAnnData created: {adata.shape}")
    print(f"Conditions: {dict(adata.obs['condition'].value_counts())}")
    print(f"Cell types: {dict(adata.obs['cell_type'].value_counts())}")
    print(f"Has gene_name: {'gene_name' in adata.var.columns}")
    print(f"Has condition: {'condition' in adata.obs.columns}")
    print(f"Has cell_type: {'cell_type' in adata.obs.columns}")
    print(f"X dtype: {adata.X.dtype}, sparse: {sp.issparse(adata.X)}")
    print(f"\nMemory usage: X={adata.X.data.nbytes / 1e6:.1f} MB")
    print("\nAdapter test PASSED")
