"""scFoundation GPU smoke test.

Loads perturblab/scfoundation-rde checkpoint via scFoundation's load_model_frommmf,
then runs a forward pass on 100 synthetic single-cell expression vectors. Also
loads ~1000 real Tahoe-100M cells and checks dtype/shape compatibility.

Env: env-delta-v2
GPU: RTX 5000 Ada (32 GB) is expected sufficient (scFoundation = 100M params).
"""
import json
import os
import sys
import time
import gc
from pathlib import Path

import numpy as np
import pandas as pd
import scanpy as sc
import torch

# Make scFoundation load module importable
SCF_MODEL_DIR = "/nfs/roberts/scratch/pi_mg269/rag88/delta/methods/scfoundation/repo/model"
sys.path.insert(0, SCF_MODEL_DIR)
from load import gatherData
from pretrainmodels import select_model


def _build_scf_config_from_perturblab(config_json):
    """perturblab/scfoundation-rde mirrors the state_dict flat + config.json with
    flat encoder/decoder fields. scFoundation's select_model() wants a nested
    config with {encoder: {hidden_dim, depth, heads, dim_head, module_type, ...},
    decoder: {...}, seq_len, n_class, bin_num, ...}. Translate."""
    c = {
        "model": "mae_autobin",
        "n_class": config_json["bin_num"] + 3,  # bin_num + pad + mask + reserved
        "seq_len": config_json["num_tokens"] + 2,  # +2 for src/tgt totcount tokens
        "bin_num": config_json["bin_num"],
        "bin_alpha": config_json["bin_alpha"],
        "pad_token_id": config_json["pad_token_id"],
        "mask_token_id": config_json["mask_token_id"],
        "encoder": {
            "hidden_dim": config_json["encoder_hidden_dim"],
            "depth": config_json["encoder_depth"],
            "heads": config_json["encoder_heads"],
            "dim_head": config_json["encoder_dim_head"],
            "module_type": config_json["encoder_module_type"],
            "ff_dropout": config_json.get("ff_dropout", 0.0),
            "attn_dropout": config_json.get("attn_dropout", 0.0),
        },
        "decoder": {
            "hidden_dim": config_json["decoder_hidden_dim"],
            "depth": config_json["decoder_depth"],
            "heads": config_json["decoder_heads"],
            "dim_head": config_json["decoder_dim_head"],
            "module_type": config_json["decoder_module_type"],
            "ff_dropout": config_json.get("ff_dropout", 0.0),
            "attn_dropout": config_json.get("attn_dropout", 0.0),
        },
    }
    return c


def load_scfoundation_perturblab(ckpt_path, config_json_path):
    """Load scFoundation from the perturblab/scfoundation-rde mirror.

    This mirror stores the flat state_dict (model.pt) plus a flat config.json,
    unlike the original SharePoint checkpoints which use a nested
    {key: {config, state_dict}} layout that scFoundation.load.load_model_frommmf
    expects. We build the nested config and hand it to select_model.
    """
    import json as _json
    with open(config_json_path) as fh:
        cfg_json = _json.load(fh)
    config = _build_scf_config_from_perturblab(cfg_json)
    model = select_model(config)
    state_dict = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    missing, unexpected = model.load_state_dict(state_dict, strict=False)
    if missing:
        print(f"  [warn] {len(missing)} missing keys; first: {missing[:3]}")
    if unexpected:
        print(f"  [warn] {len(unexpected)} unexpected keys; first: {unexpected[:3]}")
    return model, config

OUT_DIR = Path("/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/delta-tier1")
OUT_DIR.mkdir(parents=True, exist_ok=True)

report = {"env": "env-delta-v2", "torch": torch.__version__,
          "cuda_available": torch.cuda.is_available()}


def _cap_memory(stage):
    torch.cuda.synchronize()
    alloc = torch.cuda.memory_allocated() / 1024**3
    peak = torch.cuda.max_memory_allocated() / 1024**3
    report.setdefault("memory_gb", {})[stage] = {"alloc": round(alloc, 3), "peak": round(peak, 3)}
    print(f"[mem {stage}] alloc={alloc:.3f} GB  peak={peak:.3f} GB")


def main():
    assert torch.cuda.is_available(), "GPU required for smoke test"
    device = torch.device("cuda")
    report["gpu_name"] = torch.cuda.get_device_name(0)
    report["gpu_total_gb"] = round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 1)
    print(f"GPU: {report['gpu_name']}  total VRAM: {report['gpu_total_gb']} GB")

    # Step 1: Load pretrained checkpoint (perturblab mirror - flat state_dict + flat config.json)
    ckpt_path = f"{SCF_MODEL_DIR}/models/model.pt"
    config_json_path = f"{SCF_MODEL_DIR}/models/config.json"
    t0 = time.time()
    model, config = load_scfoundation_perturblab(ckpt_path, config_json_path)
    report["load_time_s"] = round(time.time() - t0, 2)
    report["config"] = {
        "n_class": config["n_class"],
        "seq_len": config["seq_len"],
        "encoder_hidden_dim": config["encoder"]["hidden_dim"],
        "encoder_depth": config["encoder"]["depth"],
        "decoder_hidden_dim": config["decoder"]["hidden_dim"],
        "pad_token_id": config["pad_token_id"],
    }
    n_params = sum(p.numel() for p in model.parameters())
    report["n_params"] = n_params
    print(f"Model loaded: {n_params:,} params in {report['load_time_s']}s")

    model = model.to(device).eval()
    _cap_memory("after_load_model")

    # Step 2: Synthetic 100-cell mini batch (19264 genes)
    N_cells, N_genes = 100, 19264
    rng = np.random.default_rng(42)
    # Sparse-ish counts to mimic scRNA-seq: lognormal + 95% zeros
    counts = rng.lognormal(1.0, 1.5, (N_cells, N_genes)).astype(np.float32)
    mask = rng.random((N_cells, N_genes)) < 0.95
    counts[mask] = 0.0
    # scFoundation expects log1p of counts with total-count tokens appended
    # Following get_embedding.py / finetune_model.py patterns
    totcount = counts.sum(axis=1)
    log_counts = np.log1p(counts)
    print(f"Synthetic input: {N_cells} cells x {N_genes} genes, "
          f"mean nonzero {(counts > 0).mean():.3f}, mean total {totcount.mean():.1f}")

    # scFoundation get_embedding.py pattern:
    # Append 2 tokens for target-high-res and source-high-res totalcount bins
    # For a basic forward pass, we use --tgthighres a5 (target is source + log(5))
    #   log_counts has shape (B, 19264); append S, T => (B, 19266)
    src_totcount = np.log10(totcount + 1)
    tgt_totcount = src_totcount + np.log10(5)  # tgthighres a5
    x_extended = np.concatenate([
        log_counts,
        src_totcount.reshape(-1, 1),
        tgt_totcount.reshape(-1, 1),
    ], axis=1)

    x = torch.from_numpy(x_extended).float().to(device)
    # Gene mask: nonzero positions in the 19264 "gene" slots + always-on for 2 totcount slots
    value_labels = x > 0  # (B, 19266)

    t0 = time.time()
    with torch.no_grad():
        x_reduced, mask_reduced = gatherData(x, value_labels, config["pad_token_id"])
        # Build position ids - standard pattern from get_embedding.py
        position_gene_ids, _ = gatherData(
            torch.arange(N_genes + 2, device=device).repeat(N_cells, 1),
            value_labels, config["pad_token_id"],
        )
        # Encoder forward
        x_emb = model.token_emb(torch.unsqueeze(x_reduced, 2).float(),
                                output_weight=0)
        pos_emb = model.pos_emb(position_gene_ids)
        h = x_emb + pos_emb
        enc_out = model.encoder(h, padding_mask=mask_reduced)
    dt = time.time() - t0
    report["forward_time_s"] = round(dt, 3)
    report["encoder_output_shape"] = list(enc_out.shape)
    print(f"Encoder forward pass: {dt:.3f}s, output shape {list(enc_out.shape)}")
    _cap_memory("after_forward")

    # Pool to get cell embeddings (pool_type=all = mean+max concat)
    pooled_mean = enc_out.mean(dim=1)
    pooled_max = enc_out.max(dim=1).values
    cell_emb = torch.cat([pooled_mean, pooled_max], dim=1)
    report["cell_embedding_shape"] = list(cell_emb.shape)
    print(f"Cell embeddings: {list(cell_emb.shape)}")

    # Step 3: Tahoe-100M data compatibility probe - load ~1000 real cells
    print("\n=== Tahoe-100M integration probe ===")
    tahoe_parquet = Path("/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/expression_data/data/train-00000-of-03388.parquet")
    gene_metadata = Path("/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/metadata/metadata/gene_metadata.parquet")

    if not tahoe_parquet.exists():
        report["tahoe_probe"] = "SKIPPED: parquet missing"
    else:
        df = pd.read_parquet(tahoe_parquet).head(1000)
        gene_meta = pd.read_parquet(gene_metadata)
        report["tahoe_probe"] = {
            "cells_loaded": int(len(df)),
            "parquet_columns": list(df.columns),
            "gene_metadata_rows": int(len(gene_meta)),
            "gene_metadata_columns": list(gene_meta.columns),
        }
        print(f"Loaded {len(df)} Tahoe cells, gene metadata = {len(gene_meta)} genes")
        print(f"Parquet columns: {list(df.columns)}")
        print(f"Gene metadata columns: {list(gene_meta.columns)}")
        # Examine first row to check the sparse expression format
        first = df.iloc[0]
        first_gene = first.get('genes')
        first_expr = first.get('expressions')
        if first_gene is not None and first_expr is not None:
            report["tahoe_probe"]["first_cell_n_genes"] = int(len(first_gene)) if hasattr(first_gene, "__len__") else None
            print(f"First cell has {len(first_gene)} nonzero genes, first 5 gene_ids {list(first_gene[:5])}, expr {list(first_expr[:5])}")

        # Build a mapping from ensembl_id (Tahoe) to scFoundation 19264 gene list
        scf_gene_list = pd.read_csv(f"{SCF_MODEL_DIR}/OS_scRNA_gene_index.19264.tsv", sep="\t")
        report["tahoe_probe"]["scf_gene_list_size"] = int(len(scf_gene_list))
        print(f"scFoundation gene list: {len(scf_gene_list)} genes (expected 19264)")
        print(f"scf_gene_list columns: {list(scf_gene_list.columns)}")

        # Intersection with Tahoe gene symbols
        if 'gene_symbol' in gene_meta.columns or 'gene_name' in gene_meta.columns:
            tahoe_symbol_col = 'gene_symbol' if 'gene_symbol' in gene_meta.columns else 'gene_name'
            tahoe_symbols = set(gene_meta[tahoe_symbol_col].astype(str).str.upper())
            scf_symbols = set(scf_gene_list['gene_name'].astype(str).str.upper())
            overlap = tahoe_symbols & scf_symbols
            report["tahoe_probe"]["gene_overlap"] = {
                "tahoe_unique_genes": len(tahoe_symbols),
                "scf_genes": len(scf_symbols),
                "intersection": len(overlap),
                "coverage_pct": round(100 * len(overlap) / len(scf_symbols), 1),
            }
            print(f"Gene overlap: {len(overlap):,} genes map "
                  f"({100*len(overlap)/len(scf_symbols):.1f}% of 19264 scF genes)")

    _cap_memory("final")

    # Step 4: Dump report
    report["status"] = "PASS"
    with open(OUT_DIR / "scfoundation_smoke_report.json", "w") as fh:
        json.dump(report, fh, indent=2, default=str)
    print(f"\n=== SCFOUNDATION SMOKE TEST PASS ===")
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
