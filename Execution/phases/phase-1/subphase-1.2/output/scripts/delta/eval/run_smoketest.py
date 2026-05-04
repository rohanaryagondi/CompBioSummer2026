"""End-to-end Delta baselines smoke test (Sub 1.2 task-005).

Loads a Tahoe-100M subsample, runs all 5 baselines + (optionally) one method,
and emits a results table validating the WMSE hierarchical harness. The random
baseline MUST fail the WMSE gate (validates IP §12.4 metric-gaming check).

Usage (from an SBATCH script or interactively in env-delta-v2):
    python -m delta.eval.run_smoketest \
        --subsample 100000 \
        --n-top-genes 2000 \
        --top-k-perts 25 \
        --baselines linear,mean,pca,random,persistence \
        --methods none \
        --out-dir $PWD

Outputs:
    {out_dir}/delta_baselines_results.md
    {out_dir}/delta_baselines_results.json
    {out_dir}/figures/reliability_{baseline}.png
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# Make the `delta` package importable when this file is invoked as a path.
HERE = Path(__file__).resolve().parent
PKG_PARENT = HERE.parent.parent  # .../output/scripts
if str(PKG_PARENT) not in sys.path:
    sys.path.insert(0, str(PKG_PARENT))

from delta.baselines import linear as bl_linear
from delta.baselines import mean as bl_mean
from delta.baselines import pca as bl_pca
from delta.baselines import random as bl_random
from delta.baselines import persistence as bl_persistence
from delta.eval.wmse import hierarchical_wmse_spearman
from delta.eval.calibration import ece, save_reliability_plot
from delta.eval.stratified import stratified_evaluation
from delta.eval.fdr import compare_bh_by
from delta.loaders.tahoe import load_tahoe_subsample


def _one_hot_features(drugs, cell_lines, drug_vocab, cell_vocab):
    """One-hot encode (drug, cell_line) as a block-sparse dense matrix."""
    n = len(drugs)
    d_idx = np.array([drug_vocab[d] for d in drugs], dtype=np.int32)
    c_idx = np.array([cell_vocab[c] for c in cell_lines], dtype=np.int32)
    D, C = len(drug_vocab), len(cell_vocab)
    X = np.zeros((n, D + C), dtype=np.float32)
    X[np.arange(n), d_idx] = 1.0
    X[np.arange(n), D + c_idx] = 1.0
    return X


def _train_test_split_by_sample(obs, test_fraction: float = 0.2, seed: int = 0):
    """Split on Tahoe `sample` (a biological replicate). Ensures no leakage of
    the same replicate between train and test, while still letting each drug
    and each cell line appear in both splits.
    """
    rng = np.random.default_rng(seed)
    samples = obs["sample"].astype(str).unique()
    rng.shuffle(samples)
    n_test = max(1, int(len(samples) * test_fraction))
    test_samples = set(samples[:n_test])
    is_test = obs["sample"].astype(str).isin(test_samples).values
    return ~is_test, is_test


def _run_one_baseline(name, X, obs, train_mask, test_mask, feat_train, feat_test,
                      seed=0, top_k=20):
    """Dispatch a baseline by name; return predictions + timing + fallback tier.
    """
    Y_train = X[train_mask]
    Y_test = X[test_mask]
    t0 = time.time()
    fallback = None
    if name == "linear":
        pred = bl_linear.fit_predict(feat_train, Y_train, feat_test)
    elif name == "mean":
        pred = bl_mean.fit_predict(
            Y_train=Y_train,
            perturbation_ids_train=obs["drug"].values[train_mask],
            perturbation_ids_test=obs["drug"].values[test_mask],
        )
    elif name == "pca":
        pred = bl_pca.fit_predict(feat_train, Y_train, feat_test)
    elif name == "random":
        pred = bl_random.fit_predict(Y_train, n_test=int(test_mask.sum()), seed=seed)
    elif name == "persistence":
        pred, fallback = bl_persistence.fit_predict(
            Y_train=Y_train,
            perturbation_ids_train=obs["drug"].values[train_mask],
            cell_types_train=obs["cell_line_id"].values[train_mask],
            perturbation_ids_test=obs["drug"].values[test_mask],
            cell_types_test=obs["cell_line_id"].values[test_mask],
        )
    else:
        raise ValueError(f"unknown baseline {name!r}")
    elapsed = time.time() - t0
    return pred, elapsed, fallback


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--subsample", type=int, default=100_000,
                        help="Max cells to load from Tahoe-100M.")
    parser.add_argument("--n-top-genes", type=int, default=2000)
    parser.add_argument("--top-k-perts", type=int, default=25)
    parser.add_argument("--baselines", type=str,
                        default="linear,mean,pca,random,persistence")
    parser.add_argument("--methods", type=str, default="none",
                        help="Comma-separated. 'none' to skip.")
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument("--top-k-degs", type=int, default=20)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--n-perm", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-parquets", type=int, default=None,
                        help="Cap parquet shards scanned. None = all 3388.")
    parser.add_argument("--out-dir", type=str,
                        default=str((HERE.parent.parent.parent).resolve()))
    parser.add_argument("--quick", action="store_true",
                        help="Tiny run: 2k cells / 500 genes / 5 drugs, smoke only.")
    args = parser.parse_args(argv)

    if args.quick:
        args.subsample = 2_000
        args.n_top_genes = 500
        args.top_k_perts = 5
        args.max_parquets = 2

    out_dir = Path(args.out_dir)
    fig_dir = out_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    print(f"[run_smoketest] out_dir = {out_dir}")

    # --- Load Tahoe subsample ---
    t0 = time.time()
    data = load_tahoe_subsample(
        max_cells=args.subsample,
        max_parquets=args.max_parquets,
        n_top_genes=args.n_top_genes,
        top_k_perts=args.top_k_perts,
        seed=args.seed,
    )
    load_time = time.time() - t0
    X = data["X"]
    obs = data["obs"]
    print(f"[run_smoketest] loaded X.shape={X.shape} in {load_time:.1f}s "
          f"({int(obs['is_control'].sum())} ctrl, "
          f"{int((~obs['is_control']).sum())} pert)")

    # --- Build vocabs + train/test split ---
    drug_vocab = {d: i for i, d in enumerate(sorted(obs["drug"].unique()))}
    cell_vocab = {c: i for i, c in enumerate(sorted(obs["cell_line_id"].unique()))}
    feat_all = _one_hot_features(obs["drug"].values, obs["cell_line_id"].values,
                                 drug_vocab, cell_vocab)
    train_mask, test_mask = _train_test_split_by_sample(
        obs, test_fraction=args.test_fraction, seed=args.seed,
    )
    print(f"[run_smoketest] train={train_mask.sum()}  test={test_mask.sum()}")

    Y_test = X[test_mask]
    feat_train = feat_all[train_mask]
    feat_test = feat_all[test_mask]
    obs_test = obs[test_mask].reset_index(drop=True)

    # --- Classify perturbation type for stratification ---
    # Minimal proxy: control vs chemical. (Tahoe-100M is chemical only; classes
    # are {control, chemical}.) In Phase 2 this will include genetic/combo types
    # from Drug/Perturbation meta but is sufficient for Sub 1.2 harness validation.
    pert_type = np.where(obs_test["is_control"].values, "control", "chemical")

    # --- Run baselines ---
    baselines = [b.strip() for b in args.baselines.split(",") if b.strip()]
    results_rows = []
    per_baseline_payload = {}

    for name in baselines:
        print(f"[baseline:{name}] start")
        pred, elapsed, fallback = _run_one_baseline(
            name, X, obs, train_mask, test_mask,
            feat_train, feat_test, seed=args.seed,
        )
        # Hierarchical WMSE gate.
        wmse_res = hierarchical_wmse_spearman(
            pred, Y_test, top_k=args.top_k_degs,
            alpha=args.alpha, n_perm=args.n_perm, seed=args.seed,
        )
        ece_val = ece(pred, Y_test, n_bins=10)
        # Save reliability diagram.
        fig_path = fig_dir / f"reliability_{name}.png"
        try:
            save_reliability_plot(pred, Y_test, str(fig_path),
                                  n_bins=10, title=f"Reliability: {name}")
        except Exception as e:
            print(f"[baseline:{name}] WARN reliability plot failed: {e}")
        # Stratified.
        strat = stratified_evaluation(
            pred, Y_test,
            cell_type=obs_test["cell_line_id"].values,
            perturbation_type=pert_type,
            expression_level=None,
            min_rows=30,
            top_k=args.top_k_degs, alpha=args.alpha,
            n_perm=max(30, args.n_perm // 3), seed=args.seed,
        )
        ct_summary = {
            k: {
                "wmse": v.get("wmse"),
                "gate": v.get("gate"),
                "n": v.get("n"),
            }
            for k, v in strat["cell_type"].items()
            if isinstance(v, dict) and "wmse" in v
        }
        pt_summary = {
            k: {
                "wmse": v.get("wmse"),
                "gate": v.get("gate"),
                "n": v.get("n"),
            }
            for k, v in strat["perturbation_type"].items()
            if isinstance(v, dict) and "wmse" in v
        }
        el_summary = {
            k: {
                "wmse": v.get("wmse"),
                "gate": v.get("gate"),
                "n": v.get("n"),
            }
            for k, v in strat["expression_level"].items()
            if isinstance(v, dict) and "wmse" in v
        }

        # FDR demo (on per-cell-type gate pvalues).
        ct_pvals = np.array([v.get("wmse_p", 1.0) for v in strat["cell_type"].values()
                             if isinstance(v, dict) and "wmse_p" in v])
        fdr_demo = None
        if len(ct_pvals) >= 2:
            fdr_demo = compare_bh_by(ct_pvals, alpha=args.alpha)

        row = {
            "baseline": name,
            "wmse": round(wmse_res["wmse"], 6),
            "wmse_p": round(wmse_res["wmse_p"], 4),
            "wmse_z": round(wmse_res["wmse_z"], 3),
            "spearman_topk": (round(wmse_res["spearman_topk"], 4)
                              if wmse_res["spearman_topk"] is not None else "N/A"),
            "gate": wmse_res["gate"],
            "ece": round(ece_val, 6) if np.isfinite(ece_val) else "nan",
            "seconds": round(elapsed, 2),
            "n_pass_topk": wmse_res["n_pass_topk"],
        }
        results_rows.append(row)
        per_baseline_payload[name] = {
            "wmse": wmse_res,
            "ece": ece_val,
            "stratified": {
                "cell_type": ct_summary,
                "perturbation_type": pt_summary,
                "expression_level": el_summary,
            },
            "fdr_cell_type": (
                {
                    "n_rejected_bh": fdr_demo["n_rejected_bh"],
                    "n_rejected_by": fdr_demo["n_rejected_by"],
                    "overlap": fdr_demo["overlap"],
                }
                if fdr_demo is not None else None
            ),
            "seconds": elapsed,
            "reliability_png": str(fig_path),
        }
        if fallback is not None:
            per_baseline_payload[name]["fallback_tier_counts"] = {
                int(t): int((fallback == t).sum()) for t in np.unique(fallback)
            }

        print(f"[baseline:{name}] wmse={wmse_res['wmse']:.5f} p={wmse_res['wmse_p']:.3f} "
              f"gate={wmse_res['gate']} spearman_topk={wmse_res['spearman_topk']}")

    # --- Validate: random MUST fail ---
    random_row = next((r for r in results_rows if r["baseline"] == "random"), None)
    random_fail_ok = random_row is not None and random_row["gate"] == "FAIL"
    if random_row is None:
        print("[validate] random baseline not requested — skipping metric-gaming check")
    elif not random_fail_ok:
        print("[validate] !!! HARNESS BUG: random baseline PASSED the WMSE gate. "
              "Aborting before writing results table to avoid shipping a broken harness.")
        # Continue writing results so the user can debug, but note failure.

    # --- Optional: run methods (e.g., GEARS) ---
    methods = [m.strip() for m in args.methods.split(",") if m.strip() and m.strip() != "none"]
    method_rows = []
    for m in methods:
        print(f"[method:{m}] not implemented in smoke harness — Tier-1 method adapters "
              "live in Sub 1.1 delta-tier1 and need their own end-to-end driver. "
              "Recording a placeholder row for the results table.")
        method_rows.append({
            "baseline": f"{m} (method, not run)",
            "wmse": "N/A",
            "wmse_p": "N/A",
            "wmse_z": "N/A",
            "spearman_topk": "N/A",
            "gate": "NOT RUN",
            "ece": "N/A",
            "seconds": 0,
            "n_pass_topk": 0,
        })

    # --- Write outputs ---
    md_path = out_dir / "delta_baselines_results.md"
    json_path = out_dir / "delta_baselines_results.json"

    df = pd.DataFrame(results_rows + method_rows)

    def _df_to_markdown(dframe: pd.DataFrame) -> str:
        """Render a pandas DataFrame as a GitHub-flavoured markdown table.

        Avoids the optional `tabulate` dependency (not in env-delta-v2).
        """
        cols = list(dframe.columns)
        head = "| " + " | ".join(cols) + " |"
        sep = "| " + " | ".join(["---"] * len(cols)) + " |"
        body = []
        for _, row in dframe.iterrows():
            body.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
        return "\n".join([head, sep] + body)

    lines = [
        "# Delta baselines smoke-test results",
        "",
        f"- Subsample: {X.shape[0]} cells × {X.shape[1]} genes",
        f"- Train/test split: sample-stratified, test_fraction={args.test_fraction}",
        f"- train={train_mask.sum()}  test={test_mask.sum()}",
        f"- Top-k DEGs: {args.top_k_degs}   alpha={args.alpha}   n_perm={args.n_perm}",
        f"- Harness metric-gaming check: "
        + ("PASS (random baseline failed WMSE gate as expected)" if random_fail_ok
           else "VIOLATED (random baseline passed — harness bug!)"),
        "",
        "## Per-baseline results",
        "",
        _df_to_markdown(df),
        "",
        "## Stratified summary (per cell_type — wmse / gate / n)",
        "",
    ]
    for name in baselines:
        lines.append(f"### {name}")
        ct = per_baseline_payload[name]["stratified"]["cell_type"]
        if ct:
            for k, v in list(ct.items())[:10]:
                lines.append(f"- {k}: wmse={v['wmse']:.4f}  gate={v['gate']}  n={v['n']}")
            if len(ct) > 10:
                lines.append(f"- ... ({len(ct) - 10} more)")
        else:
            lines.append("- (no cell-type strata above min_rows)")
        lines.append("")

    lines += [
        "## Notes",
        "",
        "- Baselines are implemented in `delta/baselines/{linear,mean,pca,random,persistence}.py`.",
        "- Evaluation harness: `delta/eval/{wmse,fdr,calibration,stratified}.py`.",
        "- Features for linear/pca: one-hot (drug, cell_line) concatenated.",
        "- log1p transform applied at load time.",
        "- Random baseline is the IP §12.4 metric-gaming check.",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    payload = {
        "args": vars(args),
        "X_shape": list(X.shape),
        "train_n": int(train_mask.sum()),
        "test_n": int(test_mask.sum()),
        "baselines": per_baseline_payload,
        "methods": {m: "not-run-in-smoke-harness" for m in methods},
        "random_fail_ok": bool(random_fail_ok),
    }
    json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"[run_smoketest] wrote {md_path}")
    print(f"[run_smoketest] wrote {json_path}")
    return 0 if random_fail_ok or random_row is None else 2


if __name__ == "__main__":
    raise SystemExit(main())
