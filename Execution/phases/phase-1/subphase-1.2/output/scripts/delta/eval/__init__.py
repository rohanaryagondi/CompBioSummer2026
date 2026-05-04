"""Delta evaluation harness (IP §12.4).

  - wmse.py        : WMSE primary metric + hierarchical WMSE -> Spearman-top-k DEG gate
  - fdr.py         : BH primary + BY sensitivity multiple-testing correction
  - calibration.py : reliability diagram + ECE against a random baseline
  - stratified.py  : per cell-type / perturbation-type / expression-level breakdown
  - run_smoketest  : end-to-end driver that exercises all 5 baselines on Tahoe subsample
"""

from . import wmse, fdr, calibration, stratified  # noqa: F401

__all__ = ["wmse", "fdr", "calibration", "stratified"]
