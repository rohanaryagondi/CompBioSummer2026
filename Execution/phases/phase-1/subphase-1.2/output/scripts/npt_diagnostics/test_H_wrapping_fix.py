#!/usr/bin/env python
"""
test_H_wrapping_fix.py -- MACE hybrid NPT with minimum-image wrapping fix.

Patches the f32 bypass to wrap protein atom positions into the primary periodic
cell before building the neighbor list. This addresses the root cause of NPT NaN
crashes: during MonteCarloBarostat trial moves, OpenMM may reimage positions so
that some protein atoms land on opposite sides of the box, producing a garbage
neighbor list for MACE.

Test protocol: 50 ps equil + 150 ps production (wall-limited to ~3h).
Success metric: survives past 30 ps equil (where v6 diagnostic crashed without fix).

Project: CompBioSummer2026 Sub 1.2 task-001 NPT wrapping fix validation.
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

TEST_NAME = "H_wrapping_fix"
TARGET_PS = 150.0
EQUIL_PS = 50.0


def main() -> int:
    log(f"=== Test {TEST_NAME}: MACE hybrid NPT f32 with minimum-image wrapping fix ===")
    log(f"  dt={DT_FS} fs, equil={EQUIL_PS} ps, target={TARGET_PS} ps")
    log(f"  barostat freq={BAROSTAT_FREQ} (production default)")
    log(f"  Key change: apply_wrapping_fix=True in add_mace_hybrid")
    log(f"  Previous without fix: v6 crashed at ~25 ps, Test B at ~5 ps, Test F at ~17 ps")

    import openmm
    from openmm import unit, MonteCarloBarostat
    from openmm.app import Simulation

    start_gpu_keepalive()

    try:
        topology, positions, system, protein_atoms = build_ww_system()

        hybrid_system = add_mace_hybrid(system, topology, positions, protein_atoms,
                                        use_f32=True, apply_wrapping_fix=True)

        log(f"Adding MonteCarloBarostat ({PRESSURE_ATM} atm, {TEMPERATURE_K} K, "
            f"freq={BAROSTAT_FREQ})...")
        barostat = MonteCarloBarostat(
            PRESSURE_ATM * unit.atmosphere,
            TEMPERATURE_K * unit.kelvin,
            BAROSTAT_FREQ,
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

        run_equilibration(simulation, EQUIL_PS, DT_FS, label="equil-MACE-wrapping-fix")

        log("=== Equilibration survived — wrapping fix appears effective ===")

        simulation.currentStep = 0

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
