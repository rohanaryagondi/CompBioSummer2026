"""Synthetic-data unit tests for the Delta harness + baselines.

Goal: exercise every public function in `delta.{baselines,eval,loaders}` without
touching Tahoe-100M. This establishes that:

    1. All 5 baselines import and produce correct-shaped outputs.
    2. The WMSE gate distinguishes an informative prediction (mean baseline on
       well-conditioned synthetic data) from a random prediction.
    3. The random baseline FAILS the WMSE gate on synthetic data too
       (metric-gaming calibration check).
    4. Reliability / ECE / stratified return finite values.
    5. FDR BH and BY return arrays of the right shape with BH >= BY rejections.

Run (from the subphase-1.2 root):
    conda activate env-delta-v2
    cd output/scripts
    python -m delta.eval.synth_unit_test

Exits non-zero if any assertion fails.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG_PARENT = HERE.parent.parent  # .../output/scripts
if str(PKG_PARENT) not in sys.path:
    sys.path.insert(0, str(PKG_PARENT))

import numpy as np

from delta.baselines import linear as bl_linear
from delta.baselines import mean as bl_mean
from delta.baselines import pca as bl_pca
from delta.baselines import random as bl_random
from delta.baselines import persistence as bl_persistence
from delta.eval.wmse import wmse, hierarchical_wmse_spearman
from delta.eval.calibration import ece, reliability_diagram
from delta.eval.stratified import stratified_evaluation
from delta.eval.fdr import fdr_bh, fdr_by, compare_bh_by


def _make_synthetic(n_cells=600, n_genes=80, n_perts=6, n_cell_types=3, seed=0):
    rng = np.random.default_rng(seed)
    # Per-perturbation and per-cell-type gene-expression signatures.
    pert_sig = rng.normal(0, 1.0, size=(n_perts, n_genes)).astype(np.float32)
    ct_sig = rng.normal(0, 0.5, size=(n_cell_types, n_genes)).astype(np.float32)
    perts = rng.integers(0, n_perts, size=n_cells)
    cts = rng.integers(0, n_cell_types, size=n_cells)
    noise = rng.normal(0, 0.2, size=(n_cells, n_genes)).astype(np.float32)
    Y = pert_sig[perts] + ct_sig[cts] + noise
    return Y, perts, cts


def test_baselines_shapes():
    Y, perts, cts = _make_synthetic(n_cells=300, n_genes=50)
    split = 240
    Y_tr, Y_te = Y[:split], Y[split:]
    p_tr, p_te = perts[:split], perts[split:]
    c_tr, c_te = cts[:split], cts[split:]

    # One-hot features for linear/pca.
    X_tr = np.zeros((split, 6 + 3), dtype=np.float32)
    X_tr[np.arange(split), p_tr] = 1.0
    X_tr[np.arange(split), 6 + c_tr] = 1.0
    X_te = np.zeros((Y_te.shape[0], 6 + 3), dtype=np.float32)
    X_te[np.arange(Y_te.shape[0]), p_te] = 1.0
    X_te[np.arange(Y_te.shape[0]), 6 + c_te] = 1.0

    p_lin = bl_linear.fit_predict(X_tr, Y_tr, X_te)
    p_mean = bl_mean.fit_predict(Y_tr, p_tr, p_te)
    p_pca = bl_pca.fit_predict(X_tr, Y_tr, X_te, n_components=10)
    p_rnd = bl_random.fit_predict(Y_tr, n_test=Y_te.shape[0], seed=7)
    p_per, fallback = bl_persistence.fit_predict(Y_tr, p_tr, c_tr, p_te, c_te)

    for name, p in [("linear", p_lin), ("mean", p_mean), ("pca", p_pca),
                    ("random", p_rnd), ("persistence", p_per)]:
        assert p.shape == Y_te.shape, f"{name}: shape {p.shape} != {Y_te.shape}"
    assert fallback.shape == (Y_te.shape[0],)
    print("[ok] test_baselines_shapes")
    return Y_tr, Y_te, p_tr, p_te, c_tr, c_te, X_tr, X_te


def test_wmse_gate_pass_fail():
    Y_tr, Y_te, p_tr, p_te, c_tr, c_te, X_tr, X_te = test_baselines_shapes()

    # Informative prediction: per-perturbation mean — should PASS the gate.
    p_mean = bl_mean.fit_predict(Y_tr, p_tr, p_te)
    res_pass = hierarchical_wmse_spearman(p_mean, Y_te, n_perm=100, seed=1)
    assert res_pass["gate"] == "PASS", f"mean baseline should pass gate, got {res_pass}"
    assert res_pass["wmse_p"] < 0.05

    # Random prediction: shuffle Y_tr rows — should FAIL the gate.
    p_rnd = bl_random.fit_predict(Y_tr, n_test=Y_te.shape[0], seed=7)
    res_fail = hierarchical_wmse_spearman(p_rnd, Y_te, n_perm=100, seed=1)
    assert res_fail["gate"] == "FAIL", f"random baseline should fail gate, got {res_fail}"
    assert res_fail["spearman_topk"] is None

    print(f"[ok] test_wmse_gate_pass_fail  mean wmse={res_pass['wmse']:.4f} "
          f"(p={res_pass['wmse_p']:.3f})  random wmse={res_fail['wmse']:.4f} "
          f"(p={res_fail['wmse_p']:.3f})")


def test_calibration():
    rng = np.random.default_rng(11)
    y = rng.normal(0, 1, size=2000)
    yhat = y + rng.normal(0, 0.5, size=2000)
    bp, bt, bc = reliability_diagram(yhat, y, n_bins=10)
    assert bp.shape == bt.shape == bc.shape == (10,)
    assert bc.sum() == 2000
    ece_val = ece(yhat, y, n_bins=10)
    assert np.isfinite(ece_val)
    print(f"[ok] test_calibration  ece={ece_val:.4f}")


def test_stratified():
    Y_tr, Y_te, p_tr, p_te, c_tr, c_te, X_tr, X_te = test_baselines_shapes()
    p_mean = bl_mean.fit_predict(Y_tr, p_tr, p_te)
    strat = stratified_evaluation(
        p_mean, Y_te,
        cell_type=c_te.astype(str),
        perturbation_type=np.where(p_te == 0, "control", "chemical"),
        min_rows=5, n_perm=30, seed=2,
    )
    assert "cell_type" in strat and "perturbation_type" in strat and "expression_level" in strat
    print(f"[ok] test_stratified  strata: cell={len(strat['cell_type'])} "
          f"pert={len(strat['perturbation_type'])} expr={len(strat['expression_level'])}")


def test_fdr():
    rng = np.random.default_rng(3)
    # 50 very-small pvals + 150 nulls — BH should reject some, BY will be more conservative.
    p = np.concatenate([rng.uniform(0, 1e-4, size=50), rng.uniform(0, 1, size=150)])
    bh = fdr_bh(p)
    by = fdr_by(p)
    assert bh["reject"].shape == by["reject"].shape == (200,)
    assert int(bh["reject"].sum()) >= int(by["reject"].sum())
    assert int(bh["reject"].sum()) >= 40, "BH should reject most strong pvals"
    cmp = compare_bh_by(p)
    assert cmp["n_rejected_bh"] >= cmp["n_rejected_by"]
    print(f"[ok] test_fdr  BH={cmp['n_rejected_bh']} BY={cmp['n_rejected_by']} "
          f"overlap={cmp['overlap']}")


def main():
    test_baselines_shapes()
    test_wmse_gate_pass_fail()
    test_calibration()
    test_stratified()
    test_fdr()
    print("\nALL SYNTHETIC UNIT TESTS PASSED")


if __name__ == "__main__":
    main()
