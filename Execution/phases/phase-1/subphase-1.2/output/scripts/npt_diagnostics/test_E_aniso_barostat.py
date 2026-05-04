#!/usr/bin/env python
"""
test_E_aniso_barostat.py -- MACE hybrid NPT with MonteCarloAnisotropicBarostat.

Replaces the isotropic MonteCarloBarostat with MonteCarloAnisotropicBarostat
that allows independent box dimension scaling. Runs 30 ps.

Purpose: The isotropic MonteCarloBarostat rescales all three box dimensions
simultaneously. If the MACE energy surface is sensitive to uniform box rescaling
(which changes all interatomic distances in the protein simultaneously), an
anisotropic barostat that changes one dimension at a time may be more stable.
Each MC move perturbs fewer coordinates, giving the MACE forces a smaller
discontinuity to absorb.

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
    TEMPERATURE_K, PRESSURE_ATM, DT_FS, FRICTION, BAROSTAT_FREQ,
)

TEST_NAME = "E_aniso_barostat"
TARGET_PS = 30.0
EQUIL_PS = 50.0


def main() -> int:
    log(f"=== Test {TEST_NAME}: MACE hybrid NPT, anisotropic barostat ===")
    log(f"  Barostat: MonteCarloAnisotropicBarostat freq={BAROSTAT_FREQ}")
    log(f"  dt={DT_FS} fs, target={TARGET_PS} ps, equil={EQUIL_PS} ps")

    import openmm
    from openmm import unit, MonteCarloAnisotropicBarostat, Vec3
    from openmm.app import Simulation

    start_gpu_keepalive()

    try:
        # Build classical system
        topology, positions, system, protein_atoms = build_ww_system()

        # Add MACE hybrid (f32)
        hybrid_system = add_mace_hybrid(system, topology, positions, protein_atoms,
                                        use_f32=True)

        # Add anisotropic barostat (all three axes allowed to change independently)
        pressure = PRESSURE_ATM * unit.atmosphere
        log(f"Adding MonteCarloAnisotropicBarostat "
            f"({PRESSURE_ATM} atm x/y/z, {TEMPERATURE_K} K, "
            f"scaleX=True, scaleY=True, scaleZ=True, freq={BAROSTAT_FREQ})...")
        barostat = MonteCarloAnisotropicBarostat(
            Vec3(pressure, pressure, pressure),
            TEMPERATURE_K * unit.kelvin,
            True,   # scaleX
            True,   # scaleY
            True,   # scaleZ
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
        run_equilibration(simulation, EQUIL_PS, DT_FS, label="equil-MACE-aniso")

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
