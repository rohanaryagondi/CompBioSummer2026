#!/usr/bin/env python
"""
test_J_sentinel.py -- Round 2 fix attempt: zero-strength sentinel HarmonicBondForce
bonds along the protein bonded graph to make OpenMM's findMolecules() see the
protein as one molecule (workaround for openmm-ml issue #91).

Configuration matches Round 1's Test I baseline so the probe TSV is directly
comparable: WW + AMBER14/TIP3P-FB, MACE-OFF24-medium f32, no per-atom wrapping
fix, MonteCarloBarostat freq=25. The ONLY difference is the sentinel-bond patch
applied AFTER createMixedSystem, BEFORE the Simulation is constructed.

Run protocol (matches Test I for direct comparison):
  - 10 ps NVT (barostat freq=0)
  - 90 ps NPT (barostat freq=25) — extended from Test I's 30 ps so a clean PASS
    at 30 ps can be tested against a longer horizon within the same gpu_devel
    1-hour budget.

Sub 1.2 task-011 NPT-patch Round 2; Step 1 (gpu_devel diagnostic).
"""
from __future__ import annotations

import os
os.environ['PYTHONNOUSERSITE'] = '1'

import sys
import time
import math
import numpy as np

# Ensure local diagnostics dir is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from npt_diag_common import (
    log, build_ww_system, minimize_and_prep,
    add_protein_sentinel_bonds,
    start_gpu_keepalive, stop_gpu_keepalive,
    TEMPERATURE_K, PRESSURE_ATM, DT_FS, FRICTION,
)

TEST_NAME = "J_sentinel"
EQUIL_NVT_PS = 10.0          # NVT baseline (no barostat)
NPT_TARGET_PS = 90.0         # NPT extended past Test I's 30 ps
BAROSTAT_FREQ = 25
PROBE_LOG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "logs", "test_J_probe.tsv"
)


def build_instrumented_hybrid(system, topology, positions, protein_atoms,
                              probe_log_handle):
    """
    Build hybrid MACE system identical to Test I (no wrapping fix) and inject
    the same per-callback probe so test_J probe TSV is directly comparable.
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

    log(f"Creating instrumented MACE-OFF24-medium hybrid for J-test "
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

    counter = {"calls": 0}

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
        _torch.set_default_dtype(_torch.float32)
        eS, lS = 96.4853, 10.0
        pos_full = state.getPositions(asNumpy=True).value_in_unit(unit.angstrom)
        nA = pos_full.shape[0]
        pos = pos_full[_idx]
        cell = state.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.angstrom)

        box_a = float(cell[0, 0])
        box_b = float(cell[1, 1])
        box_c = float(cell[2, 2])

        pmin = pos.min(axis=0)
        pmax = pos.max(axis=0)
        span = pmax - pmin

        exc = np.zeros(3)
        for ax, b in enumerate([box_a, box_b, box_c]):
            ex_pos = max(pmax[ax] - b, 0.0)
            ex_neg = max(-pmin[ax], 0.0)
            exc[ax] = max(ex_pos, ex_neg)

        npr = min(50, pos.shape[0])
        sub = pos[:npr]
        diffs = sub[:, None, :] - sub[None, :, :]
        d2 = np.einsum("ijk,ijk->ij", diffs, diffs)
        max_pair50 = float(np.sqrt(d2.max())) if npr > 1 else 0.0

        ei, sh, _, _ = _get_nh(pos, _f32_cutoff, [True, True, True], cell)
        n_edges = int(ei.shape[1]) if ei.ndim == 2 else 0

        max_shift_norm = float(np.linalg.norm(sh, axis=1).max()) if sh.shape[0] > 0 else 0.0

        if n_edges > 0:
            i_idx = ei[0]
            j_idx = ei[1]
            shift_cart = sh @ cell
            edge_vec = pos[j_idx] + shift_cart - pos[i_idx]
            edge_d = np.linalg.norm(edge_vec, axis=1)
            max_edge_dist = float(edge_d.max())
        else:
            max_edge_dist = 0.0

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
            if counter["calls"] % 25 == 0:
                probe_log_handle.flush()
        except Exception:
            pass

        return e_kj, out

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
            log("  Using INSTRUMENTED float32 MACE (probe TSV per callback) for J-test")
            break

    t_sys = time.time() - t0
    log(f"  Hybrid system built in {t_sys:.1f}s: "
        f"{hybrid_system.getNumParticles()} particles, "
        f"{hybrid_system.getNumForces()} forces (pre-sentinel)")
    return hybrid_system


def run_with_probe(simulation, label, target_ps, probe_log_handle, dt_fs=DT_FS):
    """Run target_ps of dynamics, checking for NaN. Returns result dict."""
    n_steps = int(target_ps * 1000 / dt_fs)
    log(f"--- {label}: {target_ps} ps ({n_steps} steps at dt={dt_fs} fs) ---")
    t0 = time.time()
    steps_done = 0
    chunk = 250
    failure_step = None

    try:
        while steps_done < n_steps:
            this_chunk = min(chunk, n_steps - steps_done)
            simulation.step(this_chunk)
            steps_done += this_chunk

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
                # Box state for tracking NPT volume drift
                box = state.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.angstrom)
                box_a = float(box[0, 0])
                log(f"  {label}: step {steps_done}/{n_steps} ({ps:.2f} ps) | "
                    f"E_pot={pe:.0f} kJ/mol | box_a={box_a:.3f} A | wall={elapsed:.1f}s")
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


def main():
    log(f"=== Test {TEST_NAME}: NPT with sentinel HarmonicBondForce fix ===")
    log("  Goal: verify that ~540 zero-k sentinel bonds along the protein bonded")
    log("  graph cause findMolecules() to treat the protein as one molecule, so")
    log("  MonteCarloBarostat and enforcePeriodicBox act per-molecule rather than")
    log("  per-atom, preventing the protein-tearing failure observed in Test I.")
    log(f"  Stage 1: {EQUIL_NVT_PS} ps NVT (barostat freq=0)")
    log(f"  Stage 2: {NPT_TARGET_PS} ps NPT (barostat freq={BAROSTAT_FREQ})")
    log(f"  Probe TSV: {PROBE_LOG_PATH}")

    import openmm
    from openmm import unit, MonteCarloBarostat
    from openmm.app import Simulation

    start_gpu_keepalive()

    os.makedirs(os.path.dirname(PROBE_LOG_PATH), exist_ok=True)
    probe_log_handle = open(PROBE_LOG_PATH, "w", buffering=1)

    try:
        topology, positions, system, protein_atoms = build_ww_system()

        hybrid_system = build_instrumented_hybrid(
            system, topology, positions, protein_atoms, probe_log_handle
        )

        # ---- THE FIX: add sentinel HarmonicBondForce along protein bonded graph ----
        n_forces_before = hybrid_system.getNumForces()
        log(f"  forces BEFORE sentinel patch: {n_forces_before}")
        n_sentinel = add_protein_sentinel_bonds(hybrid_system, topology, protein_atoms)
        n_forces_after = hybrid_system.getNumForces()
        log(f"  forces AFTER sentinel patch:  {n_forces_after} "
            f"(added 1 HarmonicBondForce containing {n_sentinel} sentinel bonds)")

        if n_sentinel == 0:
            raise RuntimeError(
                "No sentinel bonds added — topology.bonds() returned no protein bonds")

        # Sanity: verify exactly one HarmonicBondForce exists in hybrid_system
        n_hbf = sum(1 for i in range(hybrid_system.getNumForces())
                    if isinstance(hybrid_system.getForce(i), openmm.HarmonicBondForce))
        log(f"  HarmonicBondForce count in hybrid_system: {n_hbf} (expected 1)")
        if n_hbf < 1:
            raise RuntimeError("Sentinel HarmonicBondForce not found after addForce")

        # Add MonteCarloBarostat (initially disabled by setting frequency=0)
        log(f"Adding MonteCarloBarostat ({PRESSURE_ATM} atm, {TEMPERATURE_K} K)...")
        barostat = MonteCarloBarostat(
            PRESSURE_ATM * unit.atmosphere,
            TEMPERATURE_K * unit.kelvin,
            0,  # disabled at start; enabled for stage 2
        )
        hybrid_system.addForce(barostat)

        platform = openmm.Platform.getPlatformByName('OpenCL')
        integrator = openmm.LangevinMiddleIntegrator(
            TEMPERATURE_K * unit.kelvin,
            FRICTION / unit.picosecond,
            DT_FS * unit.femtosecond,
        )
        simulation = Simulation(topology, hybrid_system, integrator, platform, {})

        # ---- Probe findMolecules: how many molecules does OpenMM see? ----
        try:
            mols = simulation.context.getMolecules()
            n_mols = len(mols)
            mol_sizes = sorted((len(m) for m in mols), reverse=True)
            log(f"  context.getMolecules(): {n_mols} molecules total "
                f"(largest={mol_sizes[0]}, top5 sizes={mol_sizes[:5]})")
            # With sentinel: expect protein collapses to one molecule of size ~534
            # Without sentinel (Test I baseline): protein contributes 534 singletons
            protein_mol_present = any(len(m) >= 200 and
                                      set(m).intersection(set(protein_atoms))
                                      for m in mols)
            log(f"  protein-as-single-molecule detected: {protein_mol_present}")
        except Exception as e:
            log(f"  context.getMolecules() probe failed (non-fatal): {e}")

        minimize_and_prep(simulation, topology, positions)

        # Stage 1: NVT (barostat OFF, freq=0)
        log("=== Stage 1: NVT (barostat freq=0) ===")
        nvt_result = run_with_probe(simulation, "stage1_NVT", EQUIL_NVT_PS,
                                    probe_log_handle, DT_FS)

        # Stage 2: enable barostat
        log(f"=== Stage 2: NPT (enabling barostat freq={BAROSTAT_FREQ}) ===")
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
        simulation.context.reinitialize(preserveState=True)
        log(f"  Barostat re-enabled (freq={bar_force.getFrequency()}); "
            f"context reinitialized")

        npt_result = run_with_probe(simulation, "stage2_NPT", NPT_TARGET_PS,
                                    probe_log_handle, DT_FS)

        # Final state
        try:
            from openmm import unit
            final_state = simulation.context.getState(
                getPositions=True, getEnergy=True, enforcePeriodicBox=True)
            box = final_state.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.nanometer)
            vol_nm3 = abs(np.dot(box[0], np.cross(box[1], box[2])))
            pe_final = final_state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)

            # Density estimate
            total_mass = sum(simulation.system.getParticleMass(i).value_in_unit(unit.dalton)
                             for i in range(simulation.system.getNumParticles()))
            avogadro = 6.02214076e23
            density = (total_mass / avogadro) / (vol_nm3 * 1e-21) if vol_nm3 > 0 else 0.0

            # Temperature from KE
            ke = final_state.getKineticEnergy().value_in_unit(unit.kilojoule_per_mole)
            n_dof = max(3 * simulation.system.getNumParticles()
                        - simulation.system.getNumConstraints() - 3, 1)
            kB = 8.314462618e-3
            T_final = 2.0 * ke / (n_dof * kB)

            log("")
            log("=" * 65)
            log("  FINAL STATE")
            log(f"  Box vectors (nm):  a={box[0,0]:.4f} b={box[1,1]:.4f} c={box[2,2]:.4f}")
            log(f"  Volume:            {vol_nm3:.3f} nm^3")
            log(f"  Density:           {density:.4f} g/cm^3")
            log(f"  Potential energy:  {pe_final:.0f} kJ/mol")
            log(f"  Temperature:       {T_final:.1f} K")
            log("=" * 65)
        except Exception as e:
            log(f"  Final state extraction failed: {e}")

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
        # Return 0 on full PASS (NVT + 30 ps NPT minimum), 1 otherwise
        # Definition of provisional PASS: NVT clean + ≥30 ps NPT clean
        npt_30ps_passed = (npt_result['passed'] or
                           (npt_result['steps_done'] >= 30000))
        success = nvt_result['passed'] and npt_30ps_passed
        return 0 if success else 1

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
