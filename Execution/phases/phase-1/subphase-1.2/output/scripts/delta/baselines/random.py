"""Random (permutation) baseline for Delta (IP §5.3).

Calibration-test baseline: predict a random draw from the training response
distribution, ignoring the perturbation covariate entirely. This baseline is
the reference against which all other methods must demonstrate statistical
improvement — and the WMSE hierarchical harness (IP §12.4) is designed so
that `random` FAILS the gate (p > alpha). If `random` passes, the harness has
a bug or the test data is degenerate.

Strategy: for each test row draw one random training row without replacement
(falling back to with-replacement if n_test > n_train).

`fit_predict` contract:
    Y_train : (n_train, n_genes)
    n_test  : int (number of test rows to draw)
    seed    : int, default 42

    returns : (n_test, n_genes)
"""
from __future__ import annotations

import numpy as np


def fit_predict(Y_train, n_test: int, seed: int = 42, **_):
    Y_train = np.asarray(Y_train, dtype=np.float32)
    rng = np.random.default_rng(seed)

    n_train = Y_train.shape[0]
    replace = n_test > n_train
    idx = rng.choice(n_train, size=n_test, replace=replace)
    return Y_train[idx].copy()
