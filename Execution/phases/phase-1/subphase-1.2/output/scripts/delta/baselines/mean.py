"""Per-perturbation mean-expression baseline for Delta (IP §5.3).

For each test cell, predict the mean expression profile of training cells that
share the same perturbation id. If a test perturbation is unseen in training
(cold-start), fall back to the global control mean.

This is the "no signal beyond the conditional mean" baseline and is the
weakest biologically-grounded reference.

`fit_predict` contract:
    Y_train                : (n_train, n_genes)
    perturbation_ids_train : length-n_train array of hashable perturbation labels
    perturbation_ids_test  : length-n_test  array of hashable perturbation labels

    returns : (n_test, n_genes)
"""
from __future__ import annotations

import numpy as np


def fit_predict(Y_train, perturbation_ids_train, perturbation_ids_test, **_):
    Y_train = np.asarray(Y_train, dtype=np.float32)
    ptrain = np.asarray(perturbation_ids_train)
    ptest = np.asarray(perturbation_ids_test)

    # Global mean is the cold-start fallback.
    global_mean = Y_train.mean(axis=0)

    # Compute per-perturbation means once.
    pert_means = {}
    for pid in np.unique(ptrain):
        mask = ptrain == pid
        if mask.sum() > 0:
            pert_means[pid] = Y_train[mask].mean(axis=0)

    pred = np.stack(
        [pert_means.get(pid, global_mean) for pid in ptest]
    ).astype(np.float32)
    return pred
