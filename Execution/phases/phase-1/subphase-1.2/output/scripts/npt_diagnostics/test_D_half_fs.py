#!/usr/bin/env python
"""
test_D_half_fs.py -- MACE hybrid NPT with dt=0.5 fs (half production timestep).

Same hybrid system as production with MonteCarloBarostat freq=25 (unchanged),
but integrator timestep reduced from 1.0 fs to 0.5 fs. Runs 30 ps (60,000
steps instead of 30,000).

Purpose: Test if smaller timestep prevents force discontinuity from
accumulating. MACE's energy surface has slight discontinuities at neighbor
list updates; these produce instantaneous force spikes. With dt=0.5 fs, the
integrator takes smaller steps through these spikes, reducing the chance that
a single large force kick + barostat volume rescale compounds into NaN.

Note: This test takes ~2x wall time since it needs 2x steps for the same
simulated time.

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
    TEMPERATURE_K, PRESSURE_ATM, FRICTION, BAROSTAT_FREQ,
)

TEST_NAME = "D_half_fs"
DT_FS = 0.5  # half the production timestep
TARGET_PS = 30.0
EQUIL_PS = 50.0


def main() -> int:
    log(f"=== Test {TEST_NAME}: MACE hybrid NPT, dt={DT_FS} fs ===")
    log(f"  Barostat freq={BAROSTAT_FREQ}, target={TARGET_PS} ps, equil={EQUIL_PS} ps")

    import openmm
    from openmm import unit, MonteCarloBarostat
    from openmm.app import Simulation

    start_gpu_keepalive()

    try:
        # Build classical system
        topology, positions, system, protein_atoms = build_ww_system()

        # Add MACE hybrid (f32)
        hybrid_system = add_mace_hybrid(system, topology, positions, protein_atoms,
                                        use_f32=True)

        # Add barostat (freq=25, same as production)
        log(f"Adding MonteCarloBarostat ({PRESSURE_ATM} atm, {TEMPERATURE_K} K, "
            f"freq={BAROSTAT_FREQ})...")
        barostat = MonteCarloBarostat(
            PRESSURE_ATM * unit.atmosphere,
            TEMPERATURE_K * unit.kelvin,
            BAROSTAT_FREQ,
        )
        hybrid_system.addForce(barostat)

        # OpenCL platform with dt=0.5 fs
        platform = openmm.Platform.getPlatformByName('OpenCL')
        integrator = openmm.LangevinMiddleIntegrator(
            TEMPERATURE_K * unit.kelvin,
            FRICTION / unit.picosecond,
            DT_FS * unit.femtosecond,
        )
        simulation = Simulation(topology, hybrid_system, integrator, platform, {})

        # Minimize and prep
        minimize_and_prep(simulation, topology, positions)

        # Equilibration at dt=0.5 fs
        run_equilibration(simulation, EQUIL_PS, DT_FS, label="equil-MACE-half-fs")

        # Reset step counter
        simulation.currentStep = 0

        # Run production test: 30 ps at 0.5 fs = 60,000 steps
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
