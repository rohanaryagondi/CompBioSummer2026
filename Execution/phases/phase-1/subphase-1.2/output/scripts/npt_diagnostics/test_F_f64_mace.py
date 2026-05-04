#!/usr/bin/env python
"""
test_F_f64_mace.py -- MACE hybrid NPT with float64 MACE (no f32 bypass).

Same as production but WITHOUT the float32 bypass. Uses default float64 MACE
via openmmml. Barostat freq=25 (unchanged). Runs 30 ps.

Purpose: Test if the f32 precision loss causes NaN during barostat moves.
The production script uses an f32 bypass for 1.21x speedup. However, when the
MonteCarloBarostat rescales the box, it recomputes all forces at the new
geometry. If f32 MACE produces slightly inconsistent energies before/after
the rescale (due to rounding), the Metropolis accept/reject criterion may
produce energy jumps that accumulate into NaN. f64 has ~7 more decimal digits
of precision, which may smooth this out.

Note: This test will be ~20% slower than production due to f64 overhead.

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

TEST_NAME = "F_f64_mace"
TARGET_PS = 5.0   # reduced from 30 to fit SU budget; 30ps equil already proves stability past 25ps crash
EQUIL_PS = 30.0   # reduced from 50; must exceed 25ps (original crash point)


def main() -> int:
    log(f"=== Test {TEST_NAME}: MACE hybrid NPT, float64 (no f32 bypass) ===")
    log(f"  Barostat: MonteCarloBarostat freq={BAROSTAT_FREQ}")
    log(f"  dt={DT_FS} fs, target={TARGET_PS} ps, equil={EQUIL_PS} ps")

    import openmm
    from openmm import unit, MonteCarloBarostat
    from openmm.app import Simulation

    start_gpu_keepalive()

    try:
        # Build classical system
        topology, positions, system, protein_atoms = build_ww_system()

        # Add MACE hybrid with f64 (use_f32=False)
        hybrid_system = add_mace_hybrid(system, topology, positions, protein_atoms,
                                        use_f32=False)

        # Add barostat (freq=25, same as production)
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
        run_equilibration(simulation, EQUIL_PS, DT_FS, label="equil-MACE-f64")

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
