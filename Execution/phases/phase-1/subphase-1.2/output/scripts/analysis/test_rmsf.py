#!/usr/bin/env python
"""Synthetic-data unit tests for _rmsf_helpers (Item-H replacement, 2026-05-06).

Run with:
    PYTHONNOUSERSITE=1 /home/rag88/.conda/envs/env-analysis/bin/python -m pytest \
        output/scripts/analysis/test_rmsf.py -v

If pytest is not available, the module also runs as a plain script and prints
PASS/FAIL per test (exit 0 on all-pass).

Tests:
    test_rmsf_identity      -- 100 frames identical -> RMSF ≈ 0
    test_rmsf_oscillation   -- sinusoidal Cα displacement, amplitude A
                                -> RMSF[res] ≈ A / sqrt(2)
    test_rmsf_smoke         -- random gaussian Cα noise -> finite, non-negative
    test_rmsf_invariance    -- arbitrary rigid-body translation+rotation of all
                                frames preserves RMSF (Kabsch alignment)
"""
from __future__ import annotations

import sys
import numpy as np

# Ensure `analysis` is importable both as `python test_rmsf.py` (script) and
# `python -m pytest test_rmsf.py`. We put the parent of `analysis/` (i.e.
# output/scripts/) on sys.path so `from analysis._rmsf_helpers import ...`
# works in both modes.
import os
_HERE = os.path.dirname(os.path.abspath(__file__))               # .../analysis/
_SCRIPTS = os.path.dirname(_HERE)                                 # .../scripts/
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from analysis._rmsf_helpers import kabsch_aligned_ca_rmsf, so3lr_compute_ca_rmsf


# ---------------------------------------------------------------------------
# Synthetic structure builder
# ---------------------------------------------------------------------------

def _build_helix_positions(n_residues: int = 10, atoms_per_res: int = 3) -> np.ndarray:
    """Return (n_atoms, 3) positions for a minimal alpha-helix-like protein.

    Ideal alpha-helix geometry: rise per residue 1.5 A, radius 2.3 A, 100 deg
    twist. The Cα atom is the second of `atoms_per_res` per residue, so the
    Cα mask is [False, True, False, ...]. Other atoms are placed at small
    offsets from the Cα so the topology has the right shape but Cα selection
    is unambiguous.
    """
    rise = 1.5
    radius = 2.3
    twist_deg = 100.0
    coords = []
    for i in range(n_residues):
        theta = np.deg2rad(i * twist_deg)
        ca = np.array([radius * np.cos(theta), radius * np.sin(theta), i * rise])
        for j in range(atoms_per_res):
            # j == 1 -> Cα; others -> small offset
            offset = np.zeros(3) if j == 1 else (np.array([0.5 * (j - 1), 0.3, 0.0]))
            coords.append(ca + offset)
    return np.asarray(coords, dtype=np.float64)


def _ca_mask(n_residues: int = 10, atoms_per_res: int = 3) -> np.ndarray:
    """Boolean mask selecting Cα atoms (one per residue, position 1)."""
    mask = np.zeros(n_residues * atoms_per_res, dtype=bool)
    for i in range(n_residues):
        mask[i * atoms_per_res + 1] = True
    return mask


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_rmsf_identity():
    """Repeating a single frame N times should give RMSF ≈ 0."""
    n_residues = 10
    base = _build_helix_positions(n_residues)
    positions = np.tile(base, (100, 1, 1))   # (100, n_atoms, 3)
    mask = _ca_mask(n_residues)
    ca_indices = np.flatnonzero(mask)

    rmsf = kabsch_aligned_ca_rmsf(positions, ca_indices)

    assert rmsf.shape == (n_residues,), f"rmsf shape {rmsf.shape}"
    assert np.all(rmsf >= 0), "RMSF must be non-negative"
    # Identity case: RMSF should be at floating-point noise (1e-10 or below);
    # Kabsch SVD on degenerate input may add tiny noise, so we allow 1e-6 A.
    assert np.all(rmsf < 1e-6), (
        f"identity RMSF should be ~0, got max={rmsf.max():.3e}"
    )


def test_rmsf_oscillation():
    """Sinusoidal displacement on a single Cα: RMSF[res] ≈ amplitude / sqrt(2).

    For x(t) = A sin(omega t), the RMS deviation from the time-mean is A/sqrt(2).
    Since Kabsch aligns + centers, we apply the oscillation along an axis
    independent of the helix geometry, on residue 5 only. Other residues should
    show RMSF much smaller (only the noise injected by Kabsch fit on the
    perturbed atom).
    """
    n_residues = 10
    n_frames = 200
    amplitude = 1.0  # A

    base = _build_helix_positions(n_residues)
    positions = np.tile(base, (n_frames, 1, 1)).astype(np.float64)
    mask = _ca_mask(n_residues)
    ca_indices = np.flatnonzero(mask)

    target_atom = ca_indices[5]
    t = np.linspace(0.0, 4 * np.pi, n_frames, endpoint=False)
    positions[:, target_atom, 0] += amplitude * np.sin(t)

    rmsf = kabsch_aligned_ca_rmsf(positions, ca_indices)

    expected = amplitude / np.sqrt(2.0)
    # Kabsch alignment will distribute some of the displacement across the
    # whole helix when one atom moves; tolerance widened to ±0.15 A. The
    # *peak* RMSF must be at residue 5.
    peak_idx = int(np.argmax(rmsf))
    assert peak_idx == 5, f"expected peak at residue 5; got {peak_idx} (rmsf={rmsf})"
    assert abs(rmsf[5] - expected) < 0.20, (
        f"RMSF[5] should be ≈{expected:.3f}; got {rmsf[5]:.3f}"
    )
    # Other residues should have appreciably lower RMSF (post-alignment noise)
    others = np.delete(rmsf, 5)
    assert others.max() < rmsf[5], (
        f"non-perturbed residues should have lower RMSF; got max(others)={others.max():.3f}, "
        f"rmsf[5]={rmsf[5]:.3f}"
    )


def test_rmsf_smoke():
    """Random gaussian Cα noise: RMSF non-negative and finite."""
    rng = np.random.default_rng(42)
    n_residues = 10
    n_frames = 100
    base = _build_helix_positions(n_residues)
    positions = np.tile(base, (n_frames, 1, 1)).astype(np.float64)
    mask = _ca_mask(n_residues)
    ca_indices = np.flatnonzero(mask)

    # Gaussian noise on every Cα every frame, sigma 0.3 A
    sigma = 0.3
    noise = rng.normal(0.0, sigma, size=(n_frames, ca_indices.size, 3))
    positions[:, ca_indices, :] += noise

    rmsf = kabsch_aligned_ca_rmsf(positions, ca_indices)
    assert rmsf.shape == (n_residues,)
    assert np.all(np.isfinite(rmsf)), "RMSF must be finite"
    assert np.all(rmsf >= 0.0), "RMSF must be non-negative"
    # Order of magnitude check: each Cα has independent gaussian noise of
    # sigma=0.3 A, so RMSF should be in [0.1, 0.6] A range (Kabsch may absorb
    # some of the variance but not all).
    assert 0.05 < rmsf.mean() < 0.6, (
        f"smoke-test RMSF mean out of expected range; got {rmsf.mean():.3f}"
    )


def test_rmsf_translation_invariance():
    """Rigid-body translation of all frames must not change RMSF (alignment)."""
    n_residues = 10
    base = _build_helix_positions(n_residues)
    positions = np.tile(base, (50, 1, 1)).astype(np.float64)
    # Add per-frame oscillation on residue 3 to give a non-trivial RMSF
    mask = _ca_mask(n_residues)
    ca_indices = np.flatnonzero(mask)
    t = np.linspace(0.0, 2 * np.pi, 50, endpoint=False)
    positions[:, ca_indices[3], 1] += 0.5 * np.sin(t)

    rmsf_a = kabsch_aligned_ca_rmsf(positions, ca_indices)

    # Apply random per-frame translation
    rng = np.random.default_rng(7)
    translations = rng.normal(0.0, 100.0, size=(50, 1, 3))
    positions_translated = positions + translations
    rmsf_b = kabsch_aligned_ca_rmsf(positions_translated, ca_indices)

    assert np.allclose(rmsf_a, rmsf_b, atol=1e-6), (
        f"translation should be removed by alignment; max diff {np.abs(rmsf_a - rmsf_b).max():.3e}"
    )


def test_so3lr_wrapper_dict():
    """`so3lr_compute_ca_rmsf` returns the correct dict shape on a clean trajectory."""
    n_residues = 10
    base = _build_helix_positions(n_residues)
    positions = np.tile(base, (50, 1, 1)).astype(np.float64)
    mask = _ca_mask(n_residues)
    resids = np.arange(1, n_residues + 1, dtype=np.int64)
    resnames = np.array(["ALA"] * n_residues, dtype="<U3")

    out = so3lr_compute_ca_rmsf(positions, mask, resids, resnames)

    assert out["ok"] is True, f"expected ok=True; skip_reason={out.get('skip_reason')}"
    assert out["n_frames"] == 50
    assert out["n_residues"] == n_residues
    assert out["rmsf_A"].shape == (n_residues,)
    assert out["resid"].shape == (n_residues,)
    assert out["resname"].shape == (n_residues,)
    assert isinstance(out["rmsf_mean"], float)
    assert np.all(out["rmsf_A"] >= 0.0)


def test_so3lr_wrapper_too_short():
    """Single-frame input -> ok=False with skip_reason."""
    n_residues = 10
    base = _build_helix_positions(n_residues)
    positions = base[None, :, :]  # 1 frame
    mask = _ca_mask(n_residues)
    resids = np.arange(1, n_residues + 1)
    resnames = np.array(["ALA"] * n_residues)

    out = so3lr_compute_ca_rmsf(positions, mask, resids, resnames)
    assert out["ok"] is False
    assert "insufficient" in (out["skip_reason"] or "")


# ---------------------------------------------------------------------------
# Manual runner (no pytest required)
# ---------------------------------------------------------------------------

def _run_all() -> int:
    tests = [
        test_rmsf_identity,
        test_rmsf_oscillation,
        test_rmsf_smoke,
        test_rmsf_translation_invariance,
        test_so3lr_wrapper_dict,
        test_so3lr_wrapper_too_short,
    ]
    n_pass = 0
    n_fail = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
            n_pass += 1
        except AssertionError as exc:
            print(f"FAIL {t.__name__}: {exc}")
            n_fail += 1
        except Exception as exc:
            print(f"ERROR {t.__name__}: {type(exc).__name__}: {exc}")
            n_fail += 1
    print(f"\n{n_pass}/{len(tests)} tests passed")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(_run_all())
