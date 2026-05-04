"""Shared helpers for the stats unit tests."""
from __future__ import annotations

import os
import sys


def _ensure_parent_on_path():
    """Add the stats/ directory (parent of tests/) to sys.path so tests can
    import the modules without needing a package install."""
    here = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.abspath(os.path.join(here, ".."))
    if parent not in sys.path:
        sys.path.insert(0, parent)


_ensure_parent_on_path()
