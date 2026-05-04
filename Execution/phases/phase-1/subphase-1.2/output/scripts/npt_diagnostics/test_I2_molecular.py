#!/usr/bin/env python
"""
test_I2_molecular.py -- MACE hybrid NPT with MOLECULAR (centroid-based) wrapping.

The prior Test H used per-atom minimum-image wrapping, which destroys protein
bond connectivity. This test instead translates the whole protein as a rigid
blob so its centroid stays in the primary cell. Bonded atoms remain bonded.

Protocol: 10 ps NVT (warmup, no barostat) + 90 ps NPT (barostat freq=25).
Success: passes 30 ps NPT without NaN (Test H crashed at ~6 ps).

Sub 1.2 task-009 NPT-patch attempt; Step 2 / mode='molecular'.
"""
from __future__ import annotations

import os
os.environ['PYTHONNOUSERSITE'] = '1'

import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from npt_diag_common import (
    log, build_ww_system, add_mace_hybrid_v2, minimize_and_prep,
    run_equilibration, run_npt_test, start_gpu_keepalive, stop_gpu_keepalive,
    TEMPERATURE_K, PRESSURE_ATM, DT_FS, FRICTION, BAROSTAT_FREQ,
)

TEST_NAME = "I2_molecular"
NVT_PS = 10.0
NPT_PS = 90.0


def main() -> int:
    log(f"=== Test {TEST_NAME}: NPT with v2 molecular (centroid) wrap ===")
    log(f"  dt={DT_FS} fs, NVT={NVT_PS} ps, NPT={NPT_PS} ps, freq={BAROSTAT_FREQ}")

    import openmm
    from openmm import unit, MonteCarloBarostat
    from openmm.app import Simulation

    start_gpu_keepalive()

    try:
        topology, positions, system, protein_atoms = build_ww_system()

        holder = {}
        hybrid_system, _ = add_mace_hybrid_v2(
            system, topology, positions, protein_atoms,
            use_f32=True, wrap_mode='molecular', simulation_holder=holder
        )

        log(f"Adding MonteCarloBarostat at {PRESSURE_ATM} atm, {TEMPERATURE_K} K (initially disabled)...")
        barostat = MonteCarloBarostat(
            PRESSURE_ATM * unit.atmosphere,
            TEMPERATURE_K * unit.kelvin,
            0,  # disabled until NPT stage
        )
        bar_idx_in_sys = hybrid_system.addForce(barostat)

        platform = openmm.Platform.getPlatformByName('OpenCL')
        integrator = openmm.LangevinMiddleIntegrator(
            TEMPERATURE_K * unit.kelvin,
            FRICTION / unit.picosecond,
            DT_FS * unit.femtosecond,
        )
        simulation = Simulation(topology, hybrid_system, integrator, platform, {})
        holder['simulation'] = simulation  # in case any callback needs it (no-op for molecular)

        minimize_and_prep(simulation, topology, positions)

        # NVT warmup
        log("=== NVT warmup ===")
        run_equilibration(simulation, NVT_PS, DT_FS, label="nvt_warmup")

        # Enable barostat for NPT
        log(f"=== Enabling barostat (freq={BAROSTAT_FREQ}) for NPT ===")
        for i in range(simulation.system.getNumForces()):
            f_obj = simulation.system.getForce(i)
            if isinstance(f_obj, MonteCarloBarostat):
                f_obj.setFrequency(BAROSTAT_FREQ)
                break
        simulation.context.reinitialize(preserveState=True)

        log(f"=== NPT production: {NPT_PS} ps ===")
        simulation.currentStep = 0
        n_steps = int(NPT_PS * 1000 / DT_FS)
        result = run_npt_test(simulation, TEST_NAME, n_steps, check_interval=1000)

        stop_gpu_keepalive()
        return 0 if result["passed"] else 1

    except Exception as e:
        log(f"FATAL: {e}")
        import traceback
        log(traceback.format_exc())
        stop_gpu_keepalive()
        return 1


if __name__ == "__main__":
    sys.exit(main())
