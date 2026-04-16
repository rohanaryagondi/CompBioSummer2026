"""
CPA Test Script for Perturbation Prediction on Tahoe-100M

Tests:
1. Load CPA model
2. Load Tahoe-100M test conditions via adapter
3. Setup and run CPA training loop (few epochs)
4. Verify loss decreases
5. Profile GPU memory

CPA (Compositional Perturbation Autoencoder) is a VAE-based model
for predicting perturbation responses at single-cell resolution.

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

# Add scripts dir to path for adapter
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)


def main():
    import torch
    from cpa import CPA

    print("=" * 60)
    print("CPA Perturbation Test on Tahoe-100M")
    print("=" * 60)

    OUTPUT_DIR = "/nfs/roberts/scratch/pi_mg269/rag88/delta/test-outputs/cpa"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Check GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    if device.type == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(
            f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB"
        )
        torch.cuda.reset_peak_memory_stats()

    # ---- Step 1: Load test data ----
    print("\n[1/5] Loading Tahoe-100M test data...")
    from cpa_adapter import load_tahoe_for_cpa

    # Load two drugs for perturbation contrast
    drug1 = "Goserelin (acetate)"
    drug2 = "Fusidic acid"
    n_cells = 200

    adata1 = load_tahoe_for_cpa(
        drug=drug1, include_control=False, max_cells=n_cells, n_shards=3
    )
    adata2 = load_tahoe_for_cpa(
        drug=drug2, include_control=False, max_cells=n_cells, n_shards=3
    )

    # Combine and create a "control" group from drug2
    import anndata as ad

    # Use drug2 as pseudo-control for testing
    adata2.obs["control"] = 1
    adata1.obs["control"] = 0
    adata = ad.concat([adata1, adata2], join="outer")
    adata.obs_names_make_unique()

    # Ensure required columns are categorical
    for col in ["perturbation", "cell_type", "condition"]:
        adata.obs[col] = adata.obs[col].astype("category")

    print(f"  Combined AnnData: {adata.shape}")
    print(f"  Treated cells: {(adata.obs['control'] == 0).sum()}")
    print(f"  Control cells: {(adata.obs['control'] == 1).sum()}")
    print(f"  Perturbations: {adata.obs['perturbation'].nunique()}")
    print(f"  Cell types: {adata.obs['cell_type'].nunique()}")

    # ---- Step 2: Reduce gene set for feasibility ----
    print("\n[2/5] Reducing gene set for test...")
    # Use only highly variable genes (top 2000 by variance)
    import scanpy as sc

    # Convert to dense for HVG selection
    if hasattr(adata.X, "toarray"):
        X_dense = adata.X.toarray()
    else:
        X_dense = adata.X

    gene_var = np.var(X_dense, axis=0)
    top_genes = np.argsort(gene_var)[-2000:]
    adata_sub = adata[:, top_genes].copy()
    print(f"  Subset AnnData: {adata_sub.shape}")

    # ---- Step 3: Setup CPA model ----
    print("\n[3/5] Setting up CPA model...")
    try:
        # CPA setup using scvi-tools integration
        CPA.setup_anndata(
            adata_sub,
            perturbation_key="perturbation",
            control_group="control",
            dosage_key="dose_val",
            categorical_covariate_keys=["cell_type"],
            is_count_data=True,
        )

        model = CPA(
            adata_sub,
            n_latent=128,
            recon_loss="nb",  # negative binomial for count data
            doser_type="linear",
        )

        print(f"  CPA model created successfully")
        print(
            f"  Model parameters: {sum(p.numel() for p in model.module.parameters()):,}"
        )

        model_ok = True

    except Exception as e:
        print(f"  CPA setup FAILED: {e}")
        model_ok = False

    if not model_ok:
        # Write failure results
        results = {
            "method": "CPA",
            "version": "0.8.8",
            "installed": True,
            "loads_tahoe": True,
            "model_setup": "FAILED",
            "forward_pass": "SKIPPED",
            "peak_gpu_memory_gb": None,
            "device": str(device),
            "error": str(e) if "e" in dir() else "Unknown",
        }
        with open(os.path.join(OUTPUT_DIR, "cpa_test_results.json"), "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved")
        return

    # ---- Step 4: Training loop (few epochs) ----
    print("\n[4/5] Running training loop (3 epochs)...")
    t_start = time.time()
    train_ok = False
    losses = []

    try:
        model.train(
            max_epochs=3,
            batch_size=64,
            early_stopping=False,
            check_val_every_n_epoch=1,
            plan_kwargs={"lr": 1e-3},
        )
        t_elapsed = time.time() - t_start
        train_ok = True
        print(f"  Training completed in {t_elapsed:.2f}s")

        # Get training history
        if hasattr(model, "history") and model.history is not None:
            hist = model.history
            if "train_loss_epoch" in hist:
                losses = hist["train_loss_epoch"].values.tolist()
                print(f"  Losses: {[f'{l:.4f}' for l in losses]}")
                if len(losses) > 1 and losses[-1] < losses[0]:
                    print("  Loss DECREASED over training (good)")
                else:
                    print("  Loss did not decrease (may need more epochs)")

    except Exception as e:
        t_elapsed = time.time() - t_start
        print(f"  Training FAILED after {t_elapsed:.2f}s: {e}")

    # ---- Step 5: GPU Memory Profile ----
    print("\n[5/5] GPU Memory Profile:")
    if device.type == "cuda":
        peak_mem = torch.cuda.max_memory_allocated() / 1e9
        current_mem = torch.cuda.memory_allocated() / 1e9
        print(f"  Peak GPU memory: {peak_mem:.2f} GB")
        print(f"  Current GPU memory: {current_mem:.2f} GB")
    else:
        peak_mem = 0
        print("  Running on CPU -- no GPU memory to report")

    # ---- Summary ----
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    n_params = (
        sum(p.numel() for p in model.module.parameters()) if model_ok else 0
    )
    print(f"  CPA version: 0.8.8")
    print(f"  Model params: {n_params:,}")
    print(f"  Test drugs: {drug1}, {drug2}")
    print(f"  Test cells: {len(adata_sub)}")
    print(f"  Gene subset: {adata_sub.shape[1]}")
    print(f"  Training: {'PASSED' if train_ok else 'FAILED'}")
    print(f"  Training time: {t_elapsed:.2f}s")
    if losses:
        print(f"  Final loss: {losses[-1]:.4f}")
    if device.type == "cuda":
        print(f"  Peak GPU memory: {peak_mem:.2f} GB")
    print(f"  Device: {device}")

    # Save results
    results = {
        "method": "CPA",
        "version": "0.8.8",
        "installed": True,
        "loads_tahoe": True,
        "model_setup": "PASSED" if model_ok else "FAILED",
        "model_params": n_params,
        "test_drugs": [drug1, drug2],
        "test_cells": len(adata_sub),
        "gene_subset": int(adata_sub.shape[1]),
        "training_completed": train_ok,
        "training_time_s": round(t_elapsed, 2),
        "losses": [round(l, 4) for l in losses] if losses else [],
        "peak_gpu_memory_gb": round(peak_mem, 2) if device.type == "cuda" else None,
        "device": str(device),
    }

    results_path = os.path.join(OUTPUT_DIR, "cpa_test_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")


if __name__ == "__main__":
    main()
