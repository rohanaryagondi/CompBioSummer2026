"""Persistence (transfer) baseline for Delta (IP §5.3).

For each test cell tagged `(perturbation=p, cell_type=c_test)`, predict the
mean expression of training cells tagged `(perturbation=p, cell_type != c_test)`.
This tests whether a method has learned anything beyond "the same drug
produces similar average effects across cell types." It is the strongest of
the 5 baselines and the hardest one for a DL method to beat.

Fallback ladder (per `task-005-delta-baselines.md` step 5.3 failure proto):
    1. If no train rows match the same perturbation: use global training mean.
    2. If no OTHER cell type is available for that perturbation (persistence
       test degenerate): use the any-cell-type perturbation mean. This can
       happen with small subsamples and is documented in the smoke-test
       output so the degraded rows can be filtered in downstream stratified
       evaluation.

`fit_predict` contract:
    Y_train                : (n_train, n_genes)
    perturbation_ids_train : length-n_train labels
    cell_types_train       : length-n_train labels
    perturbation_ids_test  : length-n_test  labels
    cell_types_test        : length-n_test  labels

    returns : (n_test, n_genes), plus a per-row `fallback_tier` array
              (0 = persistence-clean, 1 = same-cell-type fallback,
               2 = global-mean fallback) for downstream documentation.
"""
from __future__ import annotations

import numpy as np


def fit_predict(Y_train, perturbation_ids_train, cell_types_train,
                perturbation_ids_test, cell_types_test, **_):
    Y_train = np.asarray(Y_train, dtype=np.float32)
    ptrain = np.asarray(perturbation_ids_train)
    ctrain = np.asarray(cell_types_train)
    ptest = np.asarray(perturbation_ids_test)
    ctest = np.asarray(cell_types_test)

    n_genes = Y_train.shape[1]
    global_mean = Y_train.mean(axis=0)

    # Pre-compute per-perturbation sums + counts AND per-(pert, ct) sums + counts.
    # Prediction for (pert, ct_test) = (pert_sum - pert_ct_test_sum) /
    #                                  max(pert_count - pert_ct_test_count, 1)
    # This is pure numpy — avoids a 27K-row Python loop at 100K scale.
    pert_sum = {}    # pid -> (n_genes,) np.float64
    pert_count = {}  # pid -> int
    pert_ct_sum = {}   # (pid, ct) -> (n_genes,) np.float64
    pert_ct_count = {} # (pid, ct) -> int

    for pid in np.unique(ptrain):
        mask_p = ptrain == pid
        pert_sum[pid] = Y_train[mask_p].sum(axis=0).astype(np.float64)
        pert_count[pid] = int(mask_p.sum())
        # subgroup by cell_type within this perturbation
        cts_in_pert = ctrain[mask_p]
        rows_in_pert = np.where(mask_p)[0]
        for ct in np.unique(cts_in_pert):
            sub = rows_in_pert[cts_in_pert == ct]
            pert_ct_sum[(pid, ct)] = Y_train[sub].sum(axis=0).astype(np.float64)
            pert_ct_count[(pid, ct)] = int(len(sub))

    # Build predictions vectorised per unique (pid, ct_test) key.
    preds = np.empty((len(ptest), n_genes), dtype=np.float32)
    fallback_tier = np.zeros(len(ptest), dtype=np.int8)

    # Group test rows by (pid, ct) to minimise recomputation.
    # Build a (pid, ct) -> list of test-row indices mapping.
    groups = {}
    for i, (pid, ct) in enumerate(zip(ptest, ctest)):
        groups.setdefault((pid, ct), []).append(i)

    for (pid, ct_test), row_indices in groups.items():
        row_indices = np.asarray(row_indices, dtype=np.int64)
        if pid not in pert_sum:
            preds[row_indices] = global_mean
            fallback_tier[row_indices] = 2
            continue
        total_sum = pert_sum[pid]
        total_cnt = pert_count[pid]
        sub_sum = pert_ct_sum.get((pid, ct_test))
        sub_cnt = pert_ct_count.get((pid, ct_test), 0)
        other_cnt = total_cnt - sub_cnt
        if other_cnt > 0:
            num = total_sum - (sub_sum if sub_sum is not None else 0.0)
            mean_vec = (num / other_cnt).astype(np.float32)
            preds[row_indices] = mean_vec
            fallback_tier[row_indices] = 0  # clean
        else:
            mean_vec = (total_sum / max(total_cnt, 1)).astype(np.float32)
            preds[row_indices] = mean_vec
            fallback_tier[row_indices] = 1  # same-ct fallback

    return preds, fallback_tier
