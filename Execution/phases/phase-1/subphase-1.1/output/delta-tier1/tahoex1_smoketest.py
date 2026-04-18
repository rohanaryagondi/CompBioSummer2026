"""Tahoe-x1 GPU smoke test.

Strategy:
1. Always test 70m first (fastest download, smallest memory).
2. If size argument given, test only that size.
3. Run forward pass on 100 Tahoe-100M cells loaded from a real parquet.

Env: env-tahoex1 (torch 2.5.1+cu121, flash-attn 2.7.4.post1 cu12torch2.5)
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scanpy as sc
import torch

OUT_DIR = Path("/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/delta-tier1")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _cap_memory(report, stage):
    torch.cuda.synchronize()
    alloc = torch.cuda.memory_allocated() / 1024**3
    peak = torch.cuda.max_memory_allocated() / 1024**3
    report.setdefault("memory_gb", {})[stage] = {"alloc": round(alloc, 3), "peak": round(peak, 3)}
    print(f"[mem {stage}] alloc={alloc:.3f} GB  peak={peak:.3f} GB")


def load_tahoe_sample(n_cells=100):
    """Load a small anndata from Tahoe-100M for forward-pass testing.

    Tahoe-100M parquet schema: columns=[genes, expressions, drug, sample, ...]
    where genes/expressions are sparse per-cell lists. We expand to a dense
    cells x genes matrix over the scFoundation/Tahoe-x1 compatible gene vocab.
    """
    tahoe_parquet = Path("/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/expression_data/data/train-00000-of-03388.parquet")
    gene_meta_path = Path("/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/metadata/metadata/gene_metadata.parquet")

    df = pd.read_parquet(tahoe_parquet).head(n_cells)
    gene_meta = pd.read_parquet(gene_meta_path)
    # Map token_id -> integer index (0-based for AnnData)
    tok_to_idx = dict(zip(gene_meta['token_id'].values.astype(int),
                          np.arange(len(gene_meta))))

    n_genes = len(gene_meta)
    X = np.zeros((n_cells, n_genes), dtype=np.float32)
    for i, row in enumerate(df.itertuples(index=False)):
        gs = np.asarray(row.genes, dtype=int)
        vs = np.asarray(row.expressions, dtype=np.float32)
        # Tahoe token_ids 3..62712 according to existing gears_adapter notes.
        # Skip special-token IDs 0/1/2 (pad/bos/etc.).
        idx = np.array([tok_to_idx.get(int(g), -1) for g in gs])
        keep = idx >= 0
        X[i, idx[keep]] = vs[keep]

    import anndata as ad
    adata = ad.AnnData(
        X=X,
        var=pd.DataFrame({
            'gene_symbol': gene_meta['gene_symbol'].astype(str).values,
            'ensembl_id': gene_meta['ensembl_id'].astype(str).values,
        }, index=gene_meta['ensembl_id'].astype(str).values),
        obs=pd.DataFrame({
            'drug': df['drug'].astype(str).values,
            'cell_line_id': df['cell_line_id'].astype(str).values,
        }, index=[f"cell_{i}" for i in range(n_cells)])
    )
    print(f"Loaded Tahoe-100M: {adata.shape} cells x genes, mean nonzero per cell "
          f"{(adata.X > 0).sum(axis=1).mean():.1f}")
    return adata


def smoke_test(model_size="70m", n_cells=100):
    from tahoe_x1.model import ComposerTX

    report = {
        "env": "env-tahoex1",
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "model_size": model_size,
    }
    assert torch.cuda.is_available(), "GPU required"
    device = torch.device("cuda")
    report["gpu_name"] = torch.cuda.get_device_name(0)
    report["gpu_total_gb"] = round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 1)
    print(f"GPU: {report['gpu_name']}  VRAM: {report['gpu_total_gb']} GB")

    # (1) Load model from HuggingFace
    t0 = time.time()
    print(f"\n=== Loading Tahoe-x1 {model_size} from HuggingFace ===")
    model, vocab, model_cfg, collator_cfg = ComposerTX.from_hf(
        repo_id="tahoebio/Tahoe-x1",
        model_size=model_size,
    )
    report["load_time_s"] = round(time.time() - t0, 1)
    n_params = sum(p.numel() for p in model.parameters())
    report["n_params"] = n_params
    report["vocab_size"] = len(vocab) if hasattr(vocab, "__len__") else None
    print(f"Model loaded: {n_params:,} params in {report['load_time_s']}s")
    print(f"  vocab size: {report['vocab_size']}")
    print(f"  model_cfg keys: {list(model_cfg.keys())[:10] if hasattr(model_cfg, 'keys') else 'n/a'}")

    # Move to GPU
    model = model.to(device).eval()
    _cap_memory(report, "after_load_model")

    # (2) Load a sample of Tahoe-100M cells
    print(f"\n=== Running inference on {n_cells} Tahoe-100M cells ===")
    adata = load_tahoe_sample(n_cells=n_cells)

    # Save a temp h5ad to pass to predict_embeddings (Tahoe-x1 script path)
    tmp_h5ad = OUT_DIR / f"tahoex1_sample_{n_cells}.h5ad"
    adata.write_h5ad(tmp_h5ad)
    print(f"Wrote sample to {tmp_h5ad}")

    # (3) Map our ensembl_ids to the Tahoe-x1 gene vocab and build the
    # adata.var["id_in_vocab"] column that loader_from_adata expects.
    ensembl_ids = adata.var["ensembl_id"].astype(str).values
    id_in_vocab = np.full(len(ensembl_ids), -1, dtype=np.int64)
    vocab_len = len(vocab)
    # Tahoe-x1 vocab uses Ensembl gene IDs; map each column.
    hits = 0
    for j, eid in enumerate(ensembl_ids):
        if eid in vocab:
            id_in_vocab[j] = vocab[eid]
            hits += 1
    print(f"  gene vocab mapping: {hits}/{len(ensembl_ids)} ensembl IDs resolve "
          f"(vocab size {vocab_len})")
    report["vocab_hit_rate"] = round(hits / len(ensembl_ids), 4)

    # Drop unmapped genes so loader_from_adata's assert passes.
    mask = id_in_vocab >= 0
    adata = adata[:, mask].copy()
    adata.var["id_in_vocab"] = id_in_vocab[mask]
    print(f"  adata after vocab filter: {adata.shape}")

    # (4) Run inference via get_batch_embeddings (official task API).
    # get_batch_embeddings() wants the *inner* TXModel (model.model), because its
    # forward-call uses kwargs that match TXModel's signature, not ComposerTX's
    # (ComposerTX.forward takes a batch dict).
    from tahoe_x1.tasks.emb_extractor import get_batch_embeddings
    tx_model = model.model  # TXModel inside ComposerTX
    # Propagate the pad_token_id onto the TXModel so emb_extractor's forward uses it.
    tx_model.pad_token_id = getattr(model, "pad_token_id", collator_cfg["pad_token_id"])
    t0 = time.time()
    try:
        emb = get_batch_embeddings(
            adata=adata,
            model=tx_model,
            vocab=vocab,
            model_cfg=model_cfg,
            collator_cfg=collator_cfg,
            batch_size=8,
            num_workers=2,
            prefetch_factor=2,
            max_length=min(2048, adata.shape[1]),
            return_gene_embeddings=False,
        )
        if isinstance(emb, tuple):
            emb = emb[0]
        report["inference_path"] = "get_batch_embeddings"
        report["cell_embedding_shape"] = list(emb.shape) if hasattr(emb, "shape") else None
        report["cell_embedding_dtype"] = str(getattr(emb, "dtype", "unknown"))
        print(f"  Cell embeddings: shape={emb.shape} dtype={emb.dtype}")
    except Exception as e:
        print(f"  get_batch_embeddings failed: {type(e).__name__}: {e}")
        report["inference_path"] = "failed"
        report["inference_error"] = f"{type(e).__name__}: {e}"
        import traceback
        traceback.print_exc()

    report["forward_time_s"] = round(time.time() - t0, 1)
    print(f"  forward pass time: {report['forward_time_s']}s")
    _cap_memory(report, "after_forward")

    # (5) Done
    report["status"] = "PASS" if report.get("inference_path") == "get_batch_embeddings" else "FAIL"
    with open(OUT_DIR / f"tahoex1_smoke_{model_size}.json", "w") as fh:
        json.dump(report, fh, indent=2, default=str)
    print(f"\n=== TAHOE-X1 {model_size.upper()} SMOKE {report['status']} ===")
    print(json.dumps(report, indent=2, default=str))
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model-size", default="70m", choices=["70m", "1b", "3b"])
    p.add_argument("--n-cells", type=int, default=100)
    args = p.parse_args()
    smoke_test(model_size=args.model_size, n_cells=args.n_cells)
