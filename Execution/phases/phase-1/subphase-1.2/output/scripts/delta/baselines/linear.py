"""Linear (ridge) regression baseline for Delta (IP §5.3).

Predicts log1p-transformed gene expression as a linear function of perturbation
features. The canonical feature representation here is the one-hot encoding of
(perturbation_id, cell_type_id) — this is the classical "indicator-variable"
baseline from Ahlmann-Eltze 2024, which is the key comparator that IP §14.3
calls out ("DL methods don't beat linear baselines").

Ridge regression (alpha=1.0) is used in place of plain OLS for numerical
stability when perturbation counts are highly unbalanced and the design
matrix becomes rank-deficient.

`fit_predict` contract:
    X_train : (n_train, n_features) design matrix
    Y_train : (n_train, n_genes)    response (log1p counts)
    X_test  : (n_test,  n_features) design matrix (same encoding as train)
    alpha   : float (ridge regularisation)

    returns : (n_test, n_genes) predicted log1p counts
"""
from __future__ import annotations

import numpy as np
from sklearn.linear_model import Ridge


def fit_predict(X_train, Y_train, X_test, alpha: float = 1.0, **_):
    """Fit Ridge(alpha) on (X_train, Y_train), predict on X_test."""
    X_train = np.asarray(X_train, dtype=np.float32)
    Y_train = np.asarray(Y_train, dtype=np.float32)
    X_test = np.asarray(X_test, dtype=np.float32)

    model = Ridge(alpha=alpha, fit_intercept=True, solver="auto", random_state=0)
    model.fit(X_train, Y_train)
    pred = model.predict(X_test).astype(np.float32)
    return pred
