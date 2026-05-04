"""Tahoe-100M subsample loader.

Returns a dense numpy matrix + obs metadata suitable for the 5 baselines and
the WMSE harness. The key observation from Sub 1.1 is that Tahoe-100M is stored
as per-cell sparse (genes[], expressions[]) columns across 3388 parquet shards,
with drug/cell_line metadata in the same row. Loading is parquet-at-a-time,
stopping once `max_cells` has been collected.

Important:
  * We keep only the top `n_top_genes` by column variance of the loaded sample
    to make the baselines tractable. Full 62,710-gene matrices are OOM at 1M
    cells (~250 GB dense float32).
  * All expression values are log1p-transformed (Tahoe-100M raw counts are
    integer library-normalized values; log1p is the Ahlmann-Eltze default).
  * Control (DMSO_TF) and perturbation cells are loaded together; the ids are
    carried through so the downstream baselines can split on perturbation.

API:
    load_tahoe_subsample(
        max_cells=1_000_000,
        max_parquets=None,
        n_top_genes=2_000,
        perturbations=None,  # list of drug names to load; None = top-K by frequency
        top_k_perts=25,
        cell_line_filter=None,
        include_control=True,
        seed=0,
    ) -> dict with:
        X            : (n_cells, n_genes) float32 log1p counts
        obs          : pd.DataFrame with columns ['drug','cell_line_id','is_control','sample']
        var          : pd.DataFrame with columns ['gene_symbol','ensembl_id','token_id']
        gene_mean    : (n_genes,) float32 — training-set mean (for fallback)
"""
from __future__ import annotations

import logging
import os
from typing import Iterable, Optional

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

TAHOE_BASE = "/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m"
EXPR_DIR = os.path.join(TAHOE_BASE, "expression_data", "data")
GENE_META = os.path.join(TAHOE_BASE, "metadata", "metadata", "gene_metadata.parquet")
CONTROL_DRUG = "DMSO_TF"
N_PARQUETS = 3388


def _load_gene_metadata():
    return pq.read_table(GENE_META).to_pandas()


def _find_frequent_drugs(max_parquets_scan=5, min_count=100, top_k=25):
    """Scan a few parquets to figure out which drugs are well-represented."""
    counts = {}
    for i in range(max_parquets_scan):
        fn = os.path.join(EXPR_DIR, f"train-{i:05d}-of-{N_PARQUETS:05d}.parquet")
        if not os.path.exists(fn):
            continue
        tbl = pq.read_table(fn, columns=["drug"])
        df = tbl.to_pandas()
        for d, c in df["drug"].value_counts().items():
            counts[d] = counts.get(d, 0) + int(c)
    # Drop the control from the perturbation list; we handle it explicitly.
    counts.pop(CONTROL_DRUG, None)
    ordered = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    filt = [d for d, c in ordered if c >= min_count][:top_k]
    logger.info(f"Auto-picked top-{len(filt)} drugs by frequency across "
                f"{max_parquets_scan} parquets (min_count={min_count}).")
    return filt


def load_tahoe_subsample(
    max_cells: int = 1_000_000,
    max_parquets: Optional[int] = None,
    n_top_genes: int = 2_000,
    perturbations: Optional[Iterable[str]] = None,
    top_k_perts: int = 25,
    cell_line_filter: Optional[str] = None,
    include_control: bool = True,
    control_fraction: float = 0.3,
    seed: int = 0,
):
    rng = np.random.default_rng(seed)

    gene_df = _load_gene_metadata()
    n_genes_total = len(gene_df)
    # token_id -> column index mapping (Tahoe stores genes as token_ids 3..62712,
    # with special tokens 1-2 reserved).
    token_to_col = {int(t): i for i, t in enumerate(gene_df["token_id"].values)}

    if perturbations is None:
        perturbations = _find_frequent_drugs(top_k=top_k_perts)
    perturbations = list(perturbations)
    logger.info(f"Target perturbations ({len(perturbations)}): {perturbations[:10]}"
                f"{'...' if len(perturbations) > 10 else ''}")

    target_ctrl = int(control_fraction * max_cells) if include_control else 0
    target_pert = max_cells - target_ctrl

    pert_set = set(perturbations)
    ctrl_set = {CONTROL_DRUG} if include_control else set()
    all_target_drugs = pert_set | ctrl_set

    rows_tokens = []   # list of int arrays
    rows_exprs = []    # list of float arrays
    rows_drugs = []
    rows_cells = []
    rows_samples = []
    rows_is_ctrl = []

    n_pert = 0
    n_ctrl = 0
    if max_parquets is None:
        max_parquets = N_PARQUETS

    for i in range(max_parquets):
        if n_pert >= target_pert and (not include_control or n_ctrl >= target_ctrl):
            break
        fn = os.path.join(EXPR_DIR, f"train-{i:05d}-of-{N_PARQUETS:05d}.parquet")
        if not os.path.exists(fn):
            continue
        tbl = pq.read_table(fn)
        df = tbl.to_pandas()

        mask = df["drug"].isin(all_target_drugs)
        if cell_line_filter:
            mask &= df["cell_line_id"] == cell_line_filter
        sub = df[mask]
        if len(sub) == 0:
            continue

        for _, row in sub.iterrows():
            is_ctrl = row["drug"] == CONTROL_DRUG
            if is_ctrl:
                if not include_control or n_ctrl >= target_ctrl:
                    continue
                n_ctrl += 1
            else:
                if n_pert >= target_pert:
                    continue
                n_pert += 1
            rows_tokens.append(np.asarray(row["genes"], dtype=np.int32))
            rows_exprs.append(np.asarray(row["expressions"], dtype=np.float32))
            rows_drugs.append(row["drug"])
            rows_cells.append(row["cell_line_id"])
            rows_samples.append(row["sample"])
            rows_is_ctrl.append(is_ctrl)
            if n_pert >= target_pert and (not include_control or n_ctrl >= target_ctrl):
                break

        logger.info(f"shard {i:05d}: running totals pert={n_pert} ctrl={n_ctrl}")

    n_cells = len(rows_tokens)
    if n_cells == 0:
        raise RuntimeError("No cells loaded — check perturbations / parquet scan range.")
    logger.info(f"Loaded {n_cells} cells (pert={n_pert}, ctrl={n_ctrl}) from "
                f"parquet shards 0..{i}")

    # Pass 1 (vectorised): per-token sum/sqsum/count across all cells.
    # We build a single long (col_idx, value) pair array by concatenating every
    # row's tokens once, then map tokens -> column indices vectorised, then use
    # np.bincount for the reductions. This replaces a ~8x slower Python loop.
    max_token = max(token_to_col.keys()) + 1
    token_col_lut = np.full(max_token + 1, -1, dtype=np.int64)
    for t, c in token_to_col.items():
        token_col_lut[t] = c

    all_tokens = np.concatenate(rows_tokens).astype(np.int64)
    all_values = np.concatenate(rows_exprs).astype(np.float64)
    # log1p-transform once.
    np.log1p(all_values, out=all_values)

    safe_tokens = np.clip(all_tokens, 0, max_token)
    all_cols = token_col_lut[safe_tokens]
    valid = all_cols >= 0
    all_cols = all_cols[valid]
    all_values = all_values[valid]

    sum_ = np.bincount(all_cols, weights=all_values, minlength=n_genes_total)
    sqsum = np.bincount(all_cols, weights=all_values ** 2, minlength=n_genes_total)
    count = np.bincount(all_cols, minlength=n_genes_total)

    # Sample-level mean/var including implicit zeros: divide by n_cells.
    sample_mean = sum_ / n_cells
    sample_var = sqsum / n_cells - sample_mean ** 2
    sample_var = np.clip(sample_var, 0.0, None)

    # Pick top n_top_genes by sample variance (tie-break by mean).
    order = np.argsort(-(sample_var + 1e-12 * sample_mean))
    top_cols = order[: min(n_top_genes, n_genes_total)]

    # Build compact (cell, gene) -> value triples.
    # We need per-row cell_id, so build a repeated cell index by nonzero count.
    n_genes = len(top_cols)
    col_to_dense = np.full(n_genes_total, -1, dtype=np.int64)
    col_to_dense[top_cols] = np.arange(n_genes)

    row_lengths = np.array([len(t) for t in rows_tokens], dtype=np.int64)
    cell_ids_long = np.repeat(np.arange(n_cells), row_lengths)[valid]
    dense_cols = col_to_dense[all_cols]
    keep = dense_cols >= 0

    X = np.zeros((n_cells, n_genes), dtype=np.float32)
    np.add.at(X, (cell_ids_long[keep], dense_cols[keep]),
              all_values[keep].astype(np.float32))

    obs = pd.DataFrame({
        "drug": rows_drugs,
        "cell_line_id": rows_cells,
        "sample": rows_samples,
        "is_control": rows_is_ctrl,
    })
    var = gene_df.iloc[top_cols].copy().reset_index(drop=True)

    return {
        "X": X,
        "obs": obs,
        "var": var,
        "gene_mean": sample_mean[top_cols].astype(np.float32),
    }
