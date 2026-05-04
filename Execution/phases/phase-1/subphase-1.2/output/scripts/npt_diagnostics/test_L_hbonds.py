#!/usr/bin/env python
"""
test_L_hbonds.py -- Round 3B: sentinel + restore HBonds constraints (dt=1 fs).

Hypothesis: test_J's residual NPT failure at 12.5 ps stems from unconstrained
protein C-H/N-H/O-H bonds (the classical system was built with constraints=None,
and openmm-ml's _removeBonds wouldn't have stripped any anyway since they
weren't there). At dt=1 fs, C-H stretching (~3000 cm^-1, period ~10 fs) is at
the edge of integrator stability. Adding HBonds constraints to the protein region
in the hybrid system should make the integrator stable at dt=1 fs even with the
MCB-driven barostat perturbation.

Configuration: identical to test_J except add_protein_hbonds_constraints() is
called after add_protein_sentinel_bonds(). dt remains 1 fs.

Run protocol: 5 ps NVT + 25 ps NPT (passes test_J's 12.5 ps NPT failure
horizon by 2x). At 1 fs: 5000 + 25000 = 30000 steps × ~0.10 s/step = 50 min.
Plus minimization ~5 min, fits gpu_devel.
"""
from __future__ import annotations

import os
os.environ['PYTHONNOUSERSITE'] = '1'

import sys
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from npt_diag_common import (
    log, build_ww_system, minimize_and_prep,
    add_protein_sentinel_bonds, add_protein_hbonds_constraints,
    start_gpu_keepalive, stop_gpu_keepalive,
    TEMPERATURE_K, PRESSURE_ATM, FRICTION,
)

TEST_NAME = "L_hbonds"
DT_FS_L = 1.0                  # unchanged from test_J
EQUIL_NVT_PS = 5.0             # short NVT (test_J already proved 10 ps NVT clean)
NPT_TARGET_PS = 25.0           # 2× test_J's 12.5 ps failure point
BAROSTAT_FREQ = 25
PROBE_LOG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "logs", "test_L_probe.tsv"
)


def build_instrumented_hybrid(system, topology, positions, protein_atoms,
                              probe_log_handle):
    """Same instrumented hybrid as test_J / test_K (no wrapping fix)."""
    import openmm
    from openmm import unit
    from openmmml import MLPotential
    from vesin import NeighborList as _VesinNL
    import mace.data.neighborhood as _mace_nh

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

    log(f"Creating instrumented MACE-OFF24-medium hybrid for L-test "
        f"({len(protein_atoms)} MACE atoms / {system.getNumParticles()} total)...")
    t0 = time.time()
    potential = MLPotential('mace-off24-medium')

    import torch as _torch
    hybrid_system = potential.createMixedSystem(
        topology, system, protein_atoms, interpolate=False,
    )

    _torch.set_default_dtype(_torch.float32)
    from mace.calculators.foundations_models import mace_off as _mace_off
    from mace.tools import utils as _u, to_one_hot as _toh
    from mace.tools import atomic_numbers_to_indices as _ani
    from mace.data.neighborhood import get_neighborhood as _get_nh
    from functools import partial as _partial

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
    _pbc = True
    _call_count = [0]

    def _f32_compute_probe(state, model, ptr, na, batch, pbc_t, idx, periodic,
                            cutoff, dtype, dev):
        _torch.set_default_dtype(_torch.float32)
        eS, lS = 96.4853, 10.0
        pos = state.getPositions(asNumpy=True).value_in_unit(unit.angstrom)
        nA = pos.shape[0]
        pos_p = pos[idx]
        cell = state.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.angstrom) if periodic else np.identity(3)
        ei, sh, _, _ = _get_nh(pos_p, cutoff, [periodic]*3, cell)
        inp = {"ptr": ptr, "node_attrs": na, "batch": batch, "pbc": pbc_t,
               "positions": _torch.tensor(pos_p, dtype=dtype, device=dev),
               "edge_index": _torch.tensor(ei, dtype=_torch.int64, device=dev),
               "shifts": _torch.tensor(sh, dtype=dtype, device=dev),
               "cell": _torch.tensor(cell, dtype=dtype, device=dev),
               "total_charge": _torch.tensor([0.0], dtype=dtype, device=dev),
               "total_spin": _torch.tensor([1.0], dtype=dtype, device=dev)}
        r = model(inp, compute_force=True)
        e = float(r["interaction_energy"].detach()) * eS
        f = (r["forces"] * eS * lS).detach().cpu().numpy()
        out = np.zeros((nA, 3), dtype=np.float32)
        out[idx] = f
        _call_count[0] += 1
        if _call_count[0] % 50 == 0 or _call_count[0] <= 20:
            try:
                box_a = float(cell[0, 0])
                pmin = pos_p.min(axis=0)
                pmax = pos_p.max(axis=0)
                span = pmax - pmin
                fmax = float(np.max(np.abs(f))) if f.size else 0.0
                any_nan = bool(np.any(np.isnan(f)) or np.any(np.isnan(pos_p)))
                probe_log_handle.write(
                    f"{_call_count[0]}\t{box_a:.4f}\t"
                    f"{pmin[0]:.3f}\t{pmax[0]:.3f}\t{span[0]:.3f}\t"
                    f"{pmin[1]:.3f}\t{pmax[1]:.3f}\t{span[1]:.3f}\t"
                    f"{pmin[2]:.3f}\t{pmax[2]:.3f}\t{span[2]:.3f}\t"
                    f"{e:.4f}\t{fmax:.3e}\t{int(any_nan)}\n"
                )
            except Exception:
                pass
        return e, out

    for _i in range(hybrid_system.getNumForces()):
        _force = hybrid_system.getForce(_i)
        if isinstance(_force, openmm.PythonForce):
            _fg = _force.getForceGroup()
            _pbc_flag = _force.usesPeriodicBoundaryConditions()
            hybrid_system.removeForce(_i)
            _cb = _partial(_f32_compute_probe, model=_f32_model,
                           ptr=_torch.tensor([0, len(protein_atoms)], dtype=_torch.long, device=_f32_dev),
                           na=_na,
                           batch=_torch.zeros(len(protein_atoms), dtype=_torch.long, device=_f32_dev),
                           pbc_t=_torch.tensor([_pbc]*3, dtype=_torch.bool, device=_f32_dev),
                           idx=_idx, periodic=_pbc, cutoff=_f32_cutoff,
                           dtype=_f32_dtype, dev=_f32_dev)
            _nf = openmm.PythonForce(_cb)
            _nf.setForceGroup(_fg)
            _nf.setUsesPeriodicBoundaryConditions(_pbc_flag)
            hybrid_system.addForce(_nf)
            log("  Using INSTRUMENTED float32 MACE for L-test")
            break

    t_sys = time.time() - t0
    log(f"  Hybrid system built in {t_sys:.1f}s: "
        f"{hybrid_system.getNumParticles()} particles, "
        f"{hybrid_system.getNumForces()} forces, "
        f"{hybrid_system.getNumConstraints()} constraints (pre-patches)")

    probe_log_handle.write(
        "call\tbox_a\tpmin_x\tpmax_x\tspan_x\t"
        "pmin_y\tpmax_y\tspan_y\t"
        "pmin_z\tpmax_z\tspan_z\tenergy_kjmol\tfmax\tany_nan\n"
    )
    return hybrid_system


def run_with_probe(simulation, label, target_ps, probe_log_handle, dt_fs):
    n_steps = int(target_ps * 1000 / dt_fs)
    log(f"--- {label}: {target_ps} ps ({n_steps} steps at dt={dt_fs} fs) ---")
    t0 = time.time()
    steps_done = 0
    chunk = 1000
    failed = False
    failure_step = None
    while steps_done < n_steps:
        this_chunk = min(chunk, n_steps - steps_done)
        try:
            simulation.step(this_chunk)
        except Exception as e:
            log(f"  FAIL: integration exception at step {steps_done + this_chunk}: {e}")
            failure_step = steps_done + this_chunk
            failed = True
            break
        steps_done += this_chunk
        try:
            from openmm import unit
            state = simulation.context.getState(getEnergy=True, getPositions=True)
            pe = state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
            pos = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
            box = state.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.angstrom)
            if np.isnan(pe) or np.any(np.isnan(pos)):
                log(f"  FAIL: NaN at step {steps_done} ({steps_done * dt_fs / 1000:.2f} ps)")
                failure_step = steps_done
                failed = True
                break
        except Exception as e:
            log(f"  state extraction failed at step {steps_done}: {e}")
            failure_step = steps_done
            failed = True
            break
        if steps_done % 1000 == 0 or steps_done == n_steps:
            ps = steps_done * dt_fs / 1000.0
            elapsed = time.time() - t0
            log(f"  {label}: step {steps_done}/{n_steps} ({ps:.2f} ps) | "
                f"E_pot={pe:.0f} kJ/mol | box_a={box[0,0]:.3f} A | wall={elapsed:.1f}s")
    wall_s = time.time() - t0
    return {"passed": not failed, "steps_done": steps_done,
            "wall_s": wall_s, "failure_step": failure_step}


def main():
    log(f"=== Test {TEST_NAME}: sentinel + HBonds constraints (dt={DT_FS_L} fs) ===")
    log(f"  Hypothesis: HBonds constraints stabilize unconstrained C-H/N-H modes")
    log(f"  that drove test_J's NPT failure at 12.5 ps despite sentinel-bond fix.")
    log(f"  Stage 1: {EQUIL_NVT_PS} ps NVT (barostat freq=0)")
    log(f"  Stage 2: {NPT_TARGET_PS} ps NPT (barostat freq={BAROSTAT_FREQ})")

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

        # Sentinel-bond fix (Round 2)
        n_sentinel = add_protein_sentinel_bonds(hybrid_system, topology, protein_atoms)
        if n_sentinel == 0:
            raise RuntimeError("No sentinel bonds added")

        # NEW: HBonds constraints (Round 3B)
        n_hbonds = add_protein_hbonds_constraints(hybrid_system, topology, protein_atoms)
        if n_hbonds == 0:
            log("  WARNING: no HBonds constraints added (no heavy-H protein bonds found)")

        # Add MCB
        log(f"Adding MonteCarloBarostat ({PRESSURE_ATM} atm, {TEMPERATURE_K} K)...")
        barostat = MonteCarloBarostat(
            PRESSURE_ATM * unit.atmosphere,
            TEMPERATURE_K * unit.kelvin,
            0,
        )
        hybrid_system.addForce(barostat)

        platform = openmm.Platform.getPlatformByName('OpenCL')
        integrator = openmm.LangevinMiddleIntegrator(
            TEMPERATURE_K * unit.kelvin,
            FRICTION / unit.picosecond,
            DT_FS_L * unit.femtosecond,
        )
        simulation = Simulation(topology, hybrid_system, integrator, platform, {})

        try:
            mols = simulation.context.getMolecules()
            mol_sizes = sorted((len(m) for m in mols), reverse=True)
            log(f"  context.getMolecules(): {len(mols)} molecules total "
                f"(largest={mol_sizes[0]}, top5 sizes={mol_sizes[:5]})")
        except Exception as e:
            log(f"  context.getMolecules() probe failed: {e}")

        minimize_and_prep(simulation, topology, positions)

        log("=== Stage 1: NVT (barostat freq=0) ===")
        nvt_result = run_with_probe(simulation, "stage1_NVT", EQUIL_NVT_PS,
                                    probe_log_handle, DT_FS_L)

        log(f"=== Stage 2: NPT (enabling barostat freq={BAROSTAT_FREQ}) ===")
        for i in range(simulation.system.getNumForces()):
            f_obj = simulation.system.getForce(i)
            if isinstance(f_obj, MonteCarloBarostat):
                f_obj.setFrequency(BAROSTAT_FREQ)
                break
        simulation.context.reinitialize(preserveState=True)
        log(f"  Barostat re-enabled (freq={BAROSTAT_FREQ}); context reinitialized")
        npt_result = run_with_probe(simulation, "stage2_NPT", NPT_TARGET_PS,
                                    probe_log_handle, DT_FS_L)

        # Final state
        try:
            final_state = simulation.context.getState(
                getPositions=True, getEnergy=True, enforcePeriodicBox=True)
            box = final_state.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.nanometer)
            vol_nm3 = abs(np.dot(box[0], np.cross(box[1], box[2])))
            pe_final = final_state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
            total_mass = sum(simulation.system.getParticleMass(i).value_in_unit(unit.dalton)
                             for i in range(simulation.system.getNumParticles()))
            density = (total_mass / 6.02214076e23) / (vol_nm3 * 1e-21) if vol_nm3 > 0 else 0.0
            ke = final_state.getKineticEnergy().value_in_unit(unit.kilojoule_per_mole)
            n_dof = max(3 * simulation.system.getNumParticles()
                        - simulation.system.getNumConstraints() - 3, 1)
            T_final = 2.0 * ke / (n_dof * 8.314462618e-3)
            log("")
            log("=" * 65)
            log("  FINAL STATE")
            log(f"  Box (nm):  a={box[0,0]:.4f} b={box[1,1]:.4f} c={box[2,2]:.4f}")
            log(f"  Volume:    {vol_nm3:.3f} nm^3")
            log(f"  Density:   {density:.4f} g/cm^3")
            log(f"  PE:        {pe_final:.0f} kJ/mol")
            log(f"  T:         {T_final:.1f} K")
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
                f"({npt_result['failure_step'] * DT_FS_L / 1000:.2f} ps)")
        log("=" * 65)

        probe_log_handle.flush()
        probe_log_handle.close()
        stop_gpu_keepalive()
        return 0 if (nvt_result['passed'] and npt_result['passed']) else 1

    except Exception as e:
        log(f"FATAL: {e}")
        import traceback
        log(traceback.format_exc())
        try:
            probe_log_handle.close()
        except Exception:
            pass
        stop_gpu_keepalive()
        return 2


if __name__ == "__main__":
    sys.exit(main())
