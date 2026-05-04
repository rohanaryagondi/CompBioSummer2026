"""PCA-bottleneck baseline for Delta (IP §5.3).

Controls for explained-variance: project Y_train to its top-K principal
components, fit a linear map from perturbation features X to that latent
space, then invert the projection. A perturbation-response model that only
learns the dominant modes of gene-expression variation cannot outperform
this baseline.

Pipeline:
    1. Center Y_train by the mean and keep the mean vector.
    2. PCA(n_components=K) on Y_train_centered -> (n_train, K).
    3. Ridge regression X_train -> PCA scores.
    4. Predict PCA scores for X_test, inverse-transform, add the mean back.

`fit_predict` contract:
    X_train, Y_train, X_test as in linear.py
    n_components : int, default 50
    alpha        : float, ridge regularisation

    returns : (n_test, n_genes)
"""
from __future__ import annotations

import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge


def fit_predict(X_train, Y_train, X_test, n_components: int = 50,
                alpha: float = 1.0, **_):
    X_train = np.asarray(X_train, dtype=np.float32)
    Y_train = np.asarray(Y_train, dtype=np.float32)
    X_test = np.asarray(X_test, dtype=np.float32)

    n_components = int(min(n_components, min(Y_train.shape) - 1, max(X_train.shape) - 1))
    n_components = max(n_components, 1)

    pca = PCA(n_components=n_components, svd_solver="auto", random_state=0)
    Y_latent_train = pca.fit_transform(Y_train)  # already subtracts PCA's own mean

    model = Ridge(alpha=alpha, fit_intercept=True, solver="auto", random_state=0)
    model.fit(X_train, Y_latent_train)

    Y_latent_pred = model.predict(X_test)
    pred = pca.inverse_transform(Y_latent_pred).astype(np.float32)
    return pred
