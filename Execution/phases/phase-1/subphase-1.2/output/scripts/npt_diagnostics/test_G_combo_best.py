#!/usr/bin/env python
"""
test_G_combo_best.py -- Combined best settings: dt=0.5 fs + freq=100 + f64 MACE.

Combines the three most likely individual fixes:
  - dt=0.5 fs (smaller timestep absorbs force spikes)
  - barostat freq=100 (less frequent volume moves)
  - f64 MACE (no precision loss during box rescale)

Runs 30 ps (60,000 steps at 0.5 fs).

Purpose: If individual tests (B, D, F) each show partial improvement, this
combined configuration represents the most stable NPT setup. Even if it is
slower (~2.4x vs production: 2x from halved dt, 1.2x from f64), it provides
a working NPT baseline to relax constraints from in Sub 1.4 production.

Note: Wall time will be ~2.4x production rate due to halved timestep + f64.
At ~0.9 ns/day, 30 ps takes ~48 min on RTX 5000 Ada.

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
    TEMPERATURE_K, PRESSURE_ATM, FRICTION,
)

TEST_NAME = "G_combo_best"
DT_FS = 0.5           # half timestep
BAROSTAT_FREQ = 100   # reduced frequency
USE_F32 = False        # f64 MACE
TARGET_PS = 30.0
EQUIL_PS = 50.0


def main() -> int:
    log(f"=== Test {TEST_NAME}: Combined best (dt=0.5fs + freq=100 + f64) ===")
    log(f"  dt={DT_FS} fs, barostat freq={BAROSTAT_FREQ}, MACE f64")
    log(f"  target={TARGET_PS} ps, equil={EQUIL_PS} ps")

    import openmm
    from openmm import unit, MonteCarloBarostat
    from openmm.app import Simulation

    start_gpu_keepalive()

    try:
        # Build classical system
        topology, positions, system, protein_atoms = build_ww_system()

        # Add MACE hybrid with f64 (no f32 bypass)
        hybrid_system = add_mace_hybrid(system, topology, positions, protein_atoms,
                                        use_f32=USE_F32)

        # Add barostat with freq=100
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
        run_equilibration(simulation, EQUIL_PS, DT_FS, label="equil-combo-best")

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
