#!/usr/bin/env python
"""
test_I_inspect.py -- Diagnostic probe for MACE NPT NaN failure mechanism.

Adds a probe to _f32_compute that logs (every callback) the protein-relevant
state: step number, box vectors, protein atom xyz bounds, max pairwise distance
across the first 50 atoms, and the largest neighbor-list edge distance from
get_neighborhood's `shifts`. This makes it possible to grep/awk the log to
find the LAST clean callback before the NaN and identify what changed.

Configuration intentionally matches the BASELINE failure mode (Test B/v6):
  - MACE hybrid f32 bypass
  - apply_wrapping_fix=False (no per-atom wrap)
  - MonteCarloBarostat freq=25
  - No additional protections.

Run protocol:
  - 10 ps NVT (barostat freq=0) — clean baseline
  - Up to 30 ps NPT (barostat freq=25) — until NaN or completion

Sub 1.2 task-009 NPT-patch attempt; Step 1 (inspection only).
"""
from __future__ import annotations

import os
os.environ['PYTHONNOUSERSITE'] = '1'

import sys
import time
import math
import functools
import numpy as np

# Ensure the local diagnostics dir is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from npt_diag_common import (
    log, build_ww_system, minimize_and_prep,
    start_gpu_keepalive, stop_gpu_keepalive,
    TEMPERATURE_K, PRESSURE_ATM, DT_FS, FRICTION,
)

TEST_NAME = "I_inspect"
EQUIL_NVT_PS = 10.0          # NVT baseline (no barostat)
NPT_TARGET_PS = 30.0         # NPT until NaN or completion
BAROSTAT_FREQ = 25
PROBE_LOG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "logs", "test_I_probe.tsv"
)


def build_instrumented_hybrid(system, topology, positions, protein_atoms, probe_log_handle):
    """
    Build the same hybrid system as add_mace_hybrid(use_f32=True, apply_wrapping_fix=False)
    but inject a per-callback probe that emits one TSV line per call.

    Probe TSV columns (tab-separated):
      step  box_a  box_b  box_c
      pmin_x  pmin_y  pmin_z  pmax_x  pmax_y  pmax_z
      span_x  span_y  span_z   excursion_x  excursion_y  excursion_z
      max_pair50  max_edge_disp_a  max_edge_natom_dist  n_edges
      pe_kjmol  fmax_kjmolnm  any_nan
    """
    import openmm
    from openmm import unit
    from openmmml import MLPotential
    from vesin import NeighborList as _VesinNL
    import mace.data.neighborhood as _mace_nh
    import torch as _torch
    from mace.calculators.foundations_models import mace_off as _mace_off
    from mace.tools import utils as _u, to_one_hot as _toh
    from mace.tools import atomic_numbers_to_indices as _ani
    from mace.data.neighborhood import get_neighborhood as _get_nh

    _vesin_calc = _VesinNL(cutoff=1.0, full_list=True)

    def _vesin_neighbour_list(quantities, atoms=None, cutoff=None, positions=None,
                              cell=None, pbc=None, numbers=None, cell_origin=None):
        if atoms is not None:
            positions = atoms.positions
            cell = np.asarray(atoms.cell)
            pbc = atoms.pbc
        positions = np.asarray(positions, dtype=np.float64)
        cell = np.asarray(cell, dtype=np.float64)
        periodic = bool(pbc is not None and any(pbc))
        _vesin_calc.cutoff = cutoff
        return _vesin_calc.compute(
            points=positions, box=cell, periodic=periodic,
            quantities=quantities, copy=True,
        )

    _mace_nh.neighbour_list = _vesin_neighbour_list

    log(f"Creating instrumented MACE-OFF24-medium hybrid "
        f"({len(protein_atoms)} MACE atoms / {system.getNumParticles()} total)...")
    t0 = time.time()
    potential = MLPotential('mace-off24-medium')
    hybrid_system = potential.createMixedSystem(
        topology, system, protein_atoms, interpolate=False,
    )

    _torch.set_default_dtype(_torch.float32)
    _f32_model = _mace_off(
        model='https://github.com/ACEsuit/mace-off/blob/main/mace_off24/MACE-OFF24_medium.model?raw=true',
        device='cuda', return_raw_model=True).to('cuda').float()
    for _p in _f32_model.parameters():
        _p.requires_grad = False
    _f32_cutoff = float(_f32_model.r_max.detach())
    _f32_dtype = _torch.float32
    _f32_dev = _torch.device('cuda')
    _incl = [list(topology.atoms())[i] for i in protein_atoms]
    _anums = [a.element.atomic_number for a in _incl]
    _zt = _u.AtomicNumberTable([int(z) for z in _f32_model.atomic_numbers])
    _na = _toh(_torch.tensor(_ani(_anums, z_table=_zt),
               dtype=_torch.long, device=_f32_dev).unsqueeze(-1),
               num_classes=len(_zt)).to(_f32_dtype)
    _idx = np.array(protein_atoms)
    _ptr = _torch.tensor([0, len(protein_atoms)], dtype=_torch.long, device=_f32_dev)
    _batch = _torch.zeros(len(protein_atoms), dtype=_torch.long, device=_f32_dev)
    _pbc_t = _torch.tensor([True, True, True], dtype=_torch.bool, device=_f32_dev)

    # Closure-state counter for callback invocations
    counter = {"calls": 0}

    # Header (write once)
    if probe_log_handle.tell() == 0:
        cols = [
            "calls", "box_a", "box_b", "box_c",
            "pmin_x", "pmin_y", "pmin_z",
            "pmax_x", "pmax_y", "pmax_z",
            "span_x", "span_y", "span_z",
            "exc_x", "exc_y", "exc_z",
            "max_pair50", "max_shift_norm", "max_edge_dist", "n_edges",
            "energy_kjmol", "fmax", "any_nan",
        ]
        probe_log_handle.write("\t".join(cols) + "\n")
        probe_log_handle.flush()

    def _f32_compute_probed(state):
        # Compute MACE force/energy AND emit a probe line. Match production semantics
        # (no wrapping fix) so we capture the actual failure trajectory.
        _torch.set_default_dtype(_torch.float32)
        eS, lS = 96.4853, 10.0
        pos_full = state.getPositions(asNumpy=True).value_in_unit(unit.angstrom)
        nA = pos_full.shape[0]
        pos = pos_full[_idx]
        cell = state.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.angstrom)

        # Probe: box diagonals
        box_a = float(cell[0, 0])
        box_b = float(cell[1, 1])
        box_c = float(cell[2, 2])

        # Atom bounds (Å)
        pmin = pos.min(axis=0)
        pmax = pos.max(axis=0)
        span = pmax - pmin

        # Excursion: how far is the bounding-box outside the periodic cell?
        # If pmin > 0 and pmax < box: 0 excursion
        # If pmax > box: positive excursion (atoms beyond box face)
        # If pmin < 0: positive excursion (atoms beyond origin face)
        exc = np.zeros(3)
        for ax, b in enumerate([box_a, box_b, box_c]):
            ex_pos = max(pmax[ax] - b, 0.0)
            ex_neg = max(-pmin[ax], 0.0)
            exc[ax] = max(ex_pos, ex_neg)

        # Max pairwise distance among first 50 atoms (detects "split" protein)
        # 50x50 = 2500 ops, cheap
        npr = min(50, pos.shape[0])
        sub = pos[:npr]
        diffs = sub[:, None, :] - sub[None, :, :]
        d2 = np.einsum("ijk,ijk->ij", diffs, diffs)
        max_pair50 = float(np.sqrt(d2.max())) if npr > 1 else 0.0

        # Build neighbor list (this is what MACE consumes)
        ei, sh, _, _ = _get_nh(pos, _f32_cutoff, [True, True, True], cell)
        n_edges = int(ei.shape[1]) if ei.ndim == 2 else 0

        # max shift magnitude (how far edges wrap; >0 means PBC-mediated edges)
        max_shift_norm = float(np.linalg.norm(sh, axis=1).max()) if sh.shape[0] > 0 else 0.0

        # max edge length (in Å). Edge from atom i to atom j with shift s:
        # vec = pos[j] + s @ cell - pos[i]; |vec| = edge distance
        if n_edges > 0:
            i_idx = ei[0]
            j_idx = ei[1]
            shift_cart = sh @ cell  # (n_edges, 3)
            edge_vec = pos[j_idx] + shift_cart - pos[i_idx]
            edge_d = np.linalg.norm(edge_vec, axis=1)
            max_edge_dist = float(edge_d.max())
        else:
            max_edge_dist = 0.0

        # Run MACE
        inp = {
            "ptr": _ptr, "node_attrs": _na, "batch": _batch, "pbc": _pbc_t,
            "positions": _torch.tensor(pos, dtype=_f32_dtype, device=_f32_dev),
            "edge_index": _torch.tensor(ei, dtype=_torch.int64, device=_f32_dev),
            "shifts": _torch.tensor(sh, dtype=_f32_dtype, device=_f32_dev),
            "cell": _torch.tensor(cell, dtype=_f32_dtype, device=_f32_dev),
            "total_charge": _torch.tensor([0.0], dtype=_f32_dtype, device=_f32_dev),
            "total_spin": _torch.tensor([1.0], dtype=_f32_dtype, device=_f32_dev),
        }
        r = _f32_model(inp, compute_force=True)
        e_eV = float(r["interaction_energy"].detach())
        e_kj = e_eV * eS
        f_torch = r["forces"] * eS * lS
        f = f_torch.detach().cpu().numpy()
        fmax = float(np.max(np.abs(f))) if f.size else 0.0
        any_nan = bool(np.any(np.isnan(f)) or math.isnan(e_kj))

        out = np.zeros((nA, 3), dtype=np.float32)
        out[_idx] = f

        # Emit probe line (only if log handle is still open)
        try:
            counter["calls"] += 1
            row = [
                counter["calls"], box_a, box_b, box_c,
                pmin[0], pmin[1], pmin[2],
                pmax[0], pmax[1], pmax[2],
                span[0], span[1], span[2],
                exc[0], exc[1], exc[2],
                max_pair50, max_shift_norm, max_edge_dist, n_edges,
                e_kj, fmax, int(any_nan),
            ]
            probe_log_handle.write("\t".join(f"{v:.4f}" if isinstance(v, float) else str(v)
                                             for v in row) + "\n")
            # flush every 25 calls so we don't lose data on NaN crash
            if counter["calls"] % 25 == 0:
                probe_log_handle.flush()
        except Exception:
            pass

        return e_kj, out

    # Replace PythonForce with our probed version
    for _i in range(hybrid_system.getNumForces()):
        _force = hybrid_system.getForce(_i)
        if isinstance(_force, openmm.PythonForce):
            _fg = _force.getForceGroup()
            _pbc_flag = _force.usesPeriodicBoundaryConditions()
            hybrid_system.removeForce(_i)
            _nf = openmm.PythonForce(_f32_compute_probed)
            _nf.setForceGroup(_fg)
            _nf.setUsesPeriodicBoundaryConditions(_pbc_flag)
            hybrid_system.addForce(_nf)
            log("  Using INSTRUMENTED float32 MACE (probe TSV emitted per callback)")
            break

    t_sys = time.time() - t0
    log(f"  Hybrid system built in {t_sys:.1f}s: "
        f"{hybrid_system.getNumParticles()} particles, "
        f"{hybrid_system.getNumForces()} forces")
    return hybrid_system


def run_with_probe(simulation, label: str, target_ps: float,
                   probe_log_handle, dt_fs: float = DT_FS) -> dict:
    """Run target_ps of dynamics, checking for NaN. Returns result dict."""
    n_steps = int(target_ps * 1000 / dt_fs)
    log(f"--- {label}: {target_ps} ps ({n_steps} steps at dt={dt_fs} fs) ---")
    t0 = time.time()
    steps_done = 0
    chunk = 250  # smaller chunk so we can flush probe TSV often
    failure_step = None

    try:
        while steps_done < n_steps:
            this_chunk = min(chunk, n_steps - steps_done)
            simulation.step(this_chunk)
            steps_done += this_chunk

            # Check positions for NaN
            from openmm import unit
            state = simulation.context.getState(getPositions=True, getEnergy=True,
                                               enforcePeriodicBox=False)
            pos = state.getPositions(asNumpy=True).value_in_unit(unit.angstrom)
            pe = state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
            if np.any(np.isnan(pos)) or math.isnan(pe):
                failure_step = steps_done
                log(f"  FAIL: NaN at step {steps_done} ({steps_done * dt_fs / 1000:.2f} ps)")
                break

            if steps_done % 1000 == 0:
                elapsed = time.time() - t0
                ps = steps_done * dt_fs / 1000.0
                log(f"  {label}: step {steps_done}/{n_steps} ({ps:.2f} ps) | "
                    f"E_pot={pe:.0f} kJ/mol | wall={elapsed:.1f}s")
                probe_log_handle.flush()

    except Exception as e:
        failure_step = steps_done
        log(f"  EXCEPTION at step {steps_done}: {e}")

    probe_log_handle.flush()
    return {
        "label": label,
        "passed": failure_step is None,
        "steps_done": steps_done,
        "failure_step": failure_step,
        "wall_s": time.time() - t0,
    }


def main() -> int:
    log(f"=== Test {TEST_NAME}: NPT failure-mode inspection probe ===")
    log(f"  Goal: identify what changes in the protein/box state immediately before NaN.")
    log(f"  Stage 1: {EQUIL_NVT_PS} ps NVT (clean baseline)")
    log(f"  Stage 2: {NPT_TARGET_PS} ps NPT (barostat freq={BAROSTAT_FREQ}; expect NaN ~5-25 ps)")
    log(f"  Probe TSV: {PROBE_LOG_PATH}")

    import openmm
    from openmm import unit, MonteCarloBarostat
    from openmm.app import Simulation

    start_gpu_keepalive()

    # Open probe log; truncate any prior run
    os.makedirs(os.path.dirname(PROBE_LOG_PATH), exist_ok=True)
    probe_log_handle = open(PROBE_LOG_PATH, "w", buffering=1)

    try:
        topology, positions, system, protein_atoms = build_ww_system()

        hybrid_system = build_instrumented_hybrid(
            system, topology, positions, protein_atoms, probe_log_handle
        )

        # Add MonteCarloBarostat (initially disabled by setting frequency=0)
        log(f"Adding MonteCarloBarostat ({PRESSURE_ATM} atm, {TEMPERATURE_K} K)...")
        barostat = MonteCarloBarostat(
            PRESSURE_ATM * unit.atmosphere,
            TEMPERATURE_K * unit.kelvin,
            0,  # disabled at start
        )
        hybrid_system.addForce(barostat)

        platform = openmm.Platform.getPlatformByName('OpenCL')
        integrator = openmm.LangevinMiddleIntegrator(
            TEMPERATURE_K * unit.kelvin,
            FRICTION / unit.picosecond,
            DT_FS * unit.femtosecond,
        )
        simulation = Simulation(topology, hybrid_system, integrator, platform, {})

        minimize_and_prep(simulation, topology, positions)

        # Stage 1: NVT (barostat OFF)
        log("=== Stage 1: NVT ===")
        nvt_result = run_with_probe(simulation, "stage1_NVT", EQUIL_NVT_PS,
                                    probe_log_handle, DT_FS)

        # Re-enable barostat for NPT stage
        log(f"=== Stage 2: NPT (enabling barostat freq={BAROSTAT_FREQ}) ===")
        # Get the barostat by iterating the system's forces
        barostat_idx = None
        for i in range(simulation.system.getNumForces()):
            f_obj = simulation.system.getForce(i)
            if isinstance(f_obj, MonteCarloBarostat):
                barostat_idx = i
                break
        if barostat_idx is None:
            raise RuntimeError("Could not locate MonteCarloBarostat in system")
        bar_force = simulation.system.getForce(barostat_idx)
        bar_force.setFrequency(BAROSTAT_FREQ)
        # IMPORTANT: must reinitialize the context to apply the force change
        simulation.context.reinitialize(preserveState=True)
        log(f"  Barostat re-enabled (freq={bar_force.getFrequency()}); context reinitialized")

        npt_result = run_with_probe(simulation, "stage2_NPT", NPT_TARGET_PS,
                                    probe_log_handle, DT_FS)

        log("")
        log("=" * 65)
        log(f"  NVT stage : {'PASS' if nvt_result['passed'] else 'FAIL'} "
            f"({nvt_result['steps_done']} steps, {nvt_result['wall_s']:.1f}s)")
        log(f"  NPT stage : {'PASS' if npt_result['passed'] else 'FAIL'} "
            f"({npt_result['steps_done']} steps, {npt_result['wall_s']:.1f}s)")
        if npt_result.get("failure_step"):
            log(f"  Failure step (NPT): {npt_result['failure_step']} "
                f"({npt_result['failure_step'] * DT_FS / 1000:.2f} ps)")
        log("=" * 65)

        probe_log_handle.flush()
        probe_log_handle.close()
        stop_gpu_keepalive()
        # Return 0 always — we want the inspection log even on failure
        return 0

    except Exception as e:
        log(f"FATAL: {e}")
        import traceback
        log(traceback.format_exc())
        try:
            probe_log_handle.flush()
            probe_log_handle.close()
        except Exception:
            pass
        stop_gpu_keepalive()
        return 1


if __name__ == "__main__":
    sys.exit(main())
