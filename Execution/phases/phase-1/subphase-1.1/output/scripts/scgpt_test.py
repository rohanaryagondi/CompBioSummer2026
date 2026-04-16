"""
scGPT Test Script for Perturbation Prediction on Tahoe-100M

Tests:
1. Load pretrained scGPT whole-human model
2. Load Tahoe-100M test condition via adapter
3. Run forward pass through the model
4. Profile GPU memory usage
5. Verify output predictions

Author: scgpt-cpa-setup agent (task-006)
Date: 2026-04-16
"""

import os
import sys
import json
import time
import warnings

warnings.filterwarnings("ignore")

# Fix LD_LIBRARY_PATH for conda-forge ICU/sqlite
os.environ["LD_LIBRARY_PATH"] = (
    "/home/rag88/.conda/envs/env-delta/lib:"
    + os.environ.get("LD_LIBRARY_PATH", "")
)

import numpy as np
import torch
from pathlib import Path

# Add scripts dir to path for adapter
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from scgpt_adapter import load_tahoe_for_scgpt


def main():
    print("=" * 60)
    print("scGPT Perturbation Test on Tahoe-100M")
    print("=" * 60)

    # Paths
    PRETRAINED_DIR = Path(
        "/nfs/roberts/scratch/pi_mg269/rag88/delta/methods/scgpt/"
        "pretrained/scGPT_human"
    )
    OUTPUT_DIR = Path(
        "/nfs/roberts/scratch/pi_mg269/rag88/delta/test-outputs/scgpt"
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    model_file = PRETRAINED_DIR / "best_model.pt"
    vocab_file = PRETRAINED_DIR / "vocab.json"
    config_file = PRETRAINED_DIR / "args.json"

    # Check GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    if device.type == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        torch.cuda.reset_peak_memory_stats()

    # ---- Step 1: Load vocabulary ----
    print("\n[1/5] Loading scGPT vocabulary...")
    from scgpt.tokenizer import GeneVocab

    vocab = GeneVocab.from_file(str(vocab_file))
    special_tokens = ["<pad>", "<cls>", "<eoc>"]
    for s in special_tokens:
        if s not in vocab:
            vocab.insert_token(s, len(vocab))
    ntokens = len(vocab)
    print(f"  Vocabulary size: {ntokens}")

    # ---- Step 2: Load model config and build model ----
    print("\n[2/5] Loading pretrained model...")
    with open(config_file) as f:
        model_config = json.load(f)

    embsize = model_config.get("embsize", 512)
    d_hid = model_config.get("d_hid", 512)
    nlayers = model_config.get("nlayers", 12)
    nheads = model_config.get("nheads", 8)
    n_layers_cls = model_config.get("n_layers_cls", 3)

    from scgpt.model.generation_model import TransformerGenerator

    model = TransformerGenerator(
        ntoken=ntokens,
        d_model=embsize,
        nhead=nheads,
        d_hid=d_hid,
        nlayers=nlayers,
        nlayers_cls=n_layers_cls,
        n_cls=1,
        vocab=vocab,
        dropout=0.0,  # inference mode
        pad_token="<pad>",
        pad_value=-2,
        pert_pad_id=2,
        use_fast_transformer=False,  # no flash_attn
    )

    # Load pretrained weights (partial - encoder layers only)
    pretrained_dict = torch.load(model_file, map_location="cpu", weights_only=False)
    model_dict = model.state_dict()

    # Filter for matching keys (some keys won't match due to model differences)
    matched_keys = []
    for k, v in pretrained_dict.items():
        if k in model_dict and v.shape == model_dict[k].shape:
            model_dict[k] = v
            matched_keys.append(k)

    model.load_state_dict(model_dict, strict=False)
    print(f"  Loaded {len(matched_keys)}/{len(pretrained_dict)} pretrained weight tensors")
    print(f"  Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    model = model.to(device)
    model.eval()

    # ---- Step 3: Load test data ----
    print("\n[3/5] Loading Tahoe-100M test condition...")
    test_drug = "Goserelin (acetate)"
    n_test_cells = 32  # small batch for memory profiling

    adata, gene_meta = load_tahoe_for_scgpt(
        drug=test_drug,
        max_cells=n_test_cells,
        n_shards=3,
    )
    print(f"  Loaded {adata.shape[0]} cells, {adata.shape[1]} genes")
    print(f"  Drug: {test_drug}")
    print(f"  Cell lines: {len(adata.obs['cell_line_id'].unique())}")

    # ---- Step 4: Prepare inputs and run forward pass ----
    print("\n[4/5] Running forward pass...")

    # Map gene names to vocab IDs
    gene_names = adata.var["gene_name"].values
    gene_ids = np.array(
        [vocab[g] if g in vocab else vocab["<pad>"] for g in gene_names],
        dtype=np.int64,
    )

    # For scGPT perturbation, we need to tokenize per-cell
    # Each cell: select nonzero genes, map to vocab IDs, create input tensors
    from scgpt.tokenizer.gene_tokenizer import tokenize_and_pad_batch

    X = adata.X.copy()
    max_seq_len = min(model_config.get("max_seq_len", 1200), 1200)

    # Tokenize and pad
    batch_data = tokenize_and_pad_batch(
        X,
        gene_ids,
        max_len=max_seq_len,
        vocab=vocab,
        pad_token="<pad>",
        pad_value=-2,
        append_cls=True,
        include_zero_gene=False,
        cls_token="<cls>",
    )

    input_gene_ids = batch_data["genes"].to(device)
    input_values = batch_data["values"].to(device)

    print(f"  Input gene IDs shape: {input_gene_ids.shape}")
    print(f"  Input values shape: {input_values.shape}")

    # Create perturbation flags (all zeros for baseline — no perturbation applied)
    pert_flags = torch.zeros_like(input_gene_ids, dtype=torch.long, device=device)

    # Create source key padding mask
    src_key_padding_mask = input_gene_ids.eq(vocab["<pad>"])

    # Forward pass
    t_start = time.time()
    with torch.no_grad():
        try:
            output_dict = model(
                input_gene_ids,
                input_values,
                pert_flags,
                src_key_padding_mask=src_key_padding_mask,
                CLS=False,
                CCE=False,
            )
            t_elapsed = time.time() - t_start

            # Extract outputs
            if isinstance(output_dict, dict):
                mlm_output = output_dict.get("mlm_output", None)
                cls_output = output_dict.get("cls_output", None)
                print(f"  Forward pass completed in {t_elapsed:.2f}s")
                if mlm_output is not None:
                    print(f"  MLM output shape: {mlm_output.shape}")
                    print(f"  MLM output range: [{mlm_output.min():.4f}, {mlm_output.max():.4f}]")
                if cls_output is not None:
                    print(f"  CLS output shape: {cls_output.shape}")
            else:
                print(f"  Output type: {type(output_dict)}")
                if hasattr(output_dict, 'shape'):
                    print(f"  Output shape: {output_dict.shape}")

            forward_pass_ok = True

        except Exception as e:
            t_elapsed = time.time() - t_start
            print(f"  Forward pass FAILED after {t_elapsed:.2f}s: {e}")
            forward_pass_ok = False

    # ---- Step 5: GPU Memory Profile ----
    print("\n[5/5] GPU Memory Profile:")
    if device.type == "cuda":
        peak_mem = torch.cuda.max_memory_allocated() / 1e9
        current_mem = torch.cuda.memory_allocated() / 1e9
        print(f"  Peak GPU memory: {peak_mem:.2f} GB")
        print(f"  Current GPU memory: {current_mem:.2f} GB")
    else:
        peak_mem = 0
        print("  Running on CPU — no GPU memory to report")

    # ---- Summary ----
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  scGPT version: 0.2.4")
    print(f"  Model: whole-human pretrained (scGPT_human)")
    print(f"  Model params: {sum(p.numel() for p in model.parameters()):,}")
    print(f"  Pretrained weights loaded: {len(matched_keys)}/{len(pretrained_dict)}")
    print(f"  Tahoe genes matched to vocab: {int(np.sum(gene_ids != vocab['<pad>']))}/{len(gene_names)}")
    print(f"  Test drug: {test_drug}")
    print(f"  Test cells: {n_test_cells}")
    print(f"  Sequence length: {input_gene_ids.shape[1]}")
    print(f"  Forward pass: {'PASSED' if forward_pass_ok else 'FAILED'}")
    print(f"  Inference time: {t_elapsed:.2f}s")
    if device.type == "cuda":
        print(f"  Peak GPU memory: {peak_mem:.2f} GB")
    print(f"  Device: {device}")

    # Save results
    results = {
        "method": "scGPT",
        "version": "0.2.4",
        "model": "whole-human (scGPT_human)",
        "model_params": sum(p.numel() for p in model.parameters()),
        "pretrained_weights_loaded": f"{len(matched_keys)}/{len(pretrained_dict)}",
        "tahoe_genes_matched": int(np.sum(gene_ids != vocab["<pad>"])),
        "tahoe_genes_total": len(gene_names),
        "test_drug": test_drug,
        "test_cells": n_test_cells,
        "seq_len": int(input_gene_ids.shape[1]),
        "forward_pass": "PASSED" if forward_pass_ok else "FAILED",
        "inference_time_s": round(t_elapsed, 2),
        "peak_gpu_memory_gb": round(peak_mem, 2) if device.type == "cuda" else None,
        "device": str(device),
    }

    results_path = OUTPUT_DIR / "scgpt_test_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")


if __name__ == "__main__":
    main()
