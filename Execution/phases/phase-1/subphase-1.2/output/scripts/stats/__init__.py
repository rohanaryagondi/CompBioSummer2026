"""
stats -- Statistical pipeline core for CompBioSummer2026.

Subphase 1.2, task-006. Implements the five load-bearing statistical components
from ImplementationPlan.md §12 + Appendix A.

Modules
-------
- friedman_nemenyi : Friedman test + Nemenyi post-hoc (Alpha-M primary test, IP §12.1)
- icc              : ICC(2,k) / ICC(2,1) with convergence-correction (IP §10.3)
- hierarchical_bootstrap : 2-level resample (proteins, then residues) for CIs (IP §12.1)
- jzs_bf           : JZS Bayesian correlation + 4-prior sensitivity (IP §12.3 + App. A)
- truncation       : T_min trajectory truncation with JSON logging (IP §12.1)

Each module is validated by a synthetic-data unit test in tests/. Run the full
battery with `python tests/test_all.py`.
"""

from . import friedman_nemenyi  # noqa: F401
from . import icc  # noqa: F401
from . import hierarchical_bootstrap  # noqa: F401
from . import jzs_bf  # noqa: F401
from . import truncation  # noqa: F401

__all__ = [
    "friedman_nemenyi",
    "icc",
    "hierarchical_bootstrap",
    "jzs_bf",
    "truncation",
]

__version__ = "0.1.0"
