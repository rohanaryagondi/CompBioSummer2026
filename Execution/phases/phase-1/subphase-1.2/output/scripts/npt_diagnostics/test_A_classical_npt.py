#!/usr/bin/env python
"""
test_A_classical_npt.py -- Classical-only NPT (NO MACE).

Pure AMBER14 + TIP3P-FB on the same solvated WW system with the same
MonteCarloBarostat (freq=25). Runs 30 ps past the ~25 ps failure point.

Purpose: Prove solvation and barostat work in classical mode. If this fails,
the problem is in the system build (solvation, box size, ions), not MACE.
If this passes (expected), it confirms the barostat/system interaction with
MACE is the culprit.

Project: CompBioSummer2026 Sub 1.2 task-001 NPT diagnostics.
"""
from __future__ import annotations

import sys
import time

# Suppress user site-packages
import os
os.environ['PYTHONNOUSERSITE'] = '1'

from npt_diag_common import (
    log, build_ww_system, minimize_and_prep, run_equilibration,
    run_npt_test, start_gpu_keepalive, stop_gpu_keepalive,
    TEMPERATURE_K, PRESSURE_ATM, DT_FS, FRICTION, BAROSTAT_FREQ,
)

TEST_NAME = "A_classical_npt"
TARGET_PS = 30.0
EQUIL_PS = 50.0


def main() -> int:
    log(f"=== Test {TEST_NAME}: Classical-only AMBER14+TIP3P-FB NPT ===")
    log(f"  Barostat: MonteCarloBarostat freq={BAROSTAT_FREQ}")
    log(f"  dt={DT_FS} fs, target={TARGET_PS} ps, equil={EQUIL_PS} ps")

    import openmm
    from openmm import unit, MonteCarloBarostat
    from openmm.app import Simulation

    start_gpu_keepalive()

    try:
        # Build classical system (no MACE)
        topology, positions, system, protein_atoms = build_ww_system()

        # Add barostat (same as production)
        log(f"Adding MonteCarloBarostat ({PRESSURE_ATM} atm, {TEMPERATURE_K} K, "
            f"freq={BAROSTAT_FREQ})...")
        barostat = MonteCarloBarostat(
            PRESSURE_ATM * unit.atmosphere,
            TEMPERATURE_K * unit.kelvin,
            BAROSTAT_FREQ,
        )
        system.addForce(barostat)

        # Use OpenCL platform (same as production)
        platform = openmm.Platform.getPlatformByName('OpenCL')
        integrator = openmm.LangevinMiddleIntegrator(
            TEMPERATURE_K * unit.kelvin,
            FRICTION / unit.picosecond,
            DT_FS * unit.femtosecond,
        )
        simulation = Simulation(topology, system, integrator, platform, {})

        # Minimize and prep
        minimize_and_prep(simulation, topology, positions)

        # Equilibration (50 ps, same as production)
        run_equilibration(simulation, EQUIL_PS, DT_FS, label="equil-classical-NPT")

        # Reset step counter for production
        simulation.currentStep = 0

        # Run production test (30 ps)
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
