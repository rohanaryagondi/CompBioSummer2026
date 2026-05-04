"""Delta baselines (IP §5.3).

5 mandatory baselines for the Delta benchmark:
  - linear     : ridge regression on perturbation features
  - mean       : per-perturbation mean expression
  - pca        : PCA bottleneck + linear map (explained-variance control)
  - random     : permutation (calibration-test baseline; MUST fail WMSE gate)
  - persistence: transfer baseline — same perturbation, different cell type

Each module exposes `fit_predict(...)` returning an (n_test, n_genes) array.
"""

from . import linear, mean, pca, persistence
from . import random as random_baseline  # avoid shadowing built-in

__all__ = ["linear", "mean", "pca", "persistence", "random_baseline"]
