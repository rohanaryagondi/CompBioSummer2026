#!/usr/bin/env python
"""
test_B_barostat_freq100.py -- MACE hybrid NPT with barostat frequency=100.

Same hybrid system as production but MonteCarloBarostat frequency=100 instead
of 25. Runs 30 ps.

Purpose: Test if less frequent MC volume moves help stability. With freq=25,
the barostat attempts a volume change every 25 steps (25 fs at dt=1 fs).
MACE's energy surface may have discontinuities that amplify when the box
rescales every 25 steps. freq=100 reduces the perturbation rate 4x.

Project: CompBioSummer2026 Sub 1.2 task-001 NPT diagnostics.
"""
from __future__ import annotations

import sys
import time

import os
os.environ['PYTHONNOUSERSITE'] = '1'

from npt_diag_common import (
    log, build_ww_system, add_mace_hybrid, minimize_and_prep,
    run_equilibration, run_npt_test, start_gpu_keepalive, stop_gpu_keepalive,
    TEMPERATURE_K, PRESSURE_ATM, DT_FS, FRICTION,
)

TEST_NAME = "B_barostat_freq100"
BAROSTAT_FREQ = 100  # override production default of 25
TARGET_PS = 30.0
EQUIL_PS = 50.0


def main() -> int:
    log(f"=== Test {TEST_NAME}: MACE hybrid NPT, barostat freq={BAROSTAT_FREQ} ===")
    log(f"  dt={DT_FS} fs, target={TARGET_PS} ps, equil={EQUIL_PS} ps")

    import openmm
    from openmm import unit, MonteCarloBarostat
    from openmm.app import Simulation

    start_gpu_keepalive()

    try:
        # Build classical system
        topology, positions, system, protein_atoms = build_ww_system()

        # Add MACE hybrid (f32, production default)
        hybrid_system = add_mace_hybrid(system, topology, positions, protein_atoms,
                                        use_f32=True)

        # Add barostat with freq=100
        log(f"Adding MonteCarloBarostat ({PRESSURE_ATM} atm, {TEMPERATURE_K} K, "
            f"freq={BAROSTAT_FREQ})...")
        barostat = MonteCarloBarostat(
            PRESSURE_ATM * unit.atmosphere,
            TEMPERATURE_K * unit.kelvin,
            BAROSTAT_FREQ,
        )
        hybrid_system.addForce(barostat)

        # OpenCL platform
        platform = openmm.Platform.getPlatformByName('OpenCL')
        integrator = openmm.LangevinMiddleIntegrator(
            TEMPERATURE_K * unit.kelvin,
            FRICTION / unit.picosecond,
            DT_FS * unit.femtosecond,
        )
        simulation = Simulation(topology, hybrid_system, integrator, platform, {})

        # Minimize and prep
        minimize_and_prep(simulation, topology, positions)

        # Equilibration
        run_equilibration(simulation, EQUIL_PS, DT_FS, label="equil-MACE-freq100")

        # Reset step counter
        simulation.currentStep = 0

        # Run production test
        n_steps = int(TARGET_PS * 1000 / DT_FS)
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
