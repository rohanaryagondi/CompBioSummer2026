#!/usr/bin/env python
"""
cuda_interop_probe.py -- minimal reproducer + fix harness for the
PyTorch <-> OpenMM CUDA context interop crash that blocked Subagent J.

Crash seen by Subagent J (SLURM 8789011):
  - `simulation.minimizeEnergy(maxIterations=2000)` on a hybrid vacuum crambin
    system compiled via MLPotential('mace-off24-medium').createMixedSystem(...)
  - Platform = OpenMM CUDA (Subagent J's source-built 8.5.1)
  - After ~5-30 seconds: RuntimeError "CUDA driver error: invalid resource handle"
    inside TorchScript -> MACE forward pass.

Strategy (tried in order of increasing invasiveness; probe exits at the first
one that works):

  Fix A  — Align CUDA device/context:
             os.environ['CUDA_VISIBLE_DEVICES']='0'
             torch.cuda.init(); torch.cuda.set_device(0)
             pass `device='cuda:0'` through MLPotential.createMixedSystem
             set OpenMM CUDA platform property DeviceIndex='0', Precision='mixed'
             call torch.cuda.synchronize() after model preparation, before sim.

  Fix B  — Patch openmmml.models.macepotential._computeMACE to call
             torch.cuda.synchronize() before reading the state and after
             producing forces. Done via runtime monkey-patch — no file edit.

  Fix C  — (not applied in this script) install openmm-torch and switch to
             openmmtorch.TorchForce. Would need a separate subagent pass.

Invocation is environment-driven:
  PROBE_MODE=reproduce   -> reproduce original Subagent J crash (no fixes)
  PROBE_MODE=fixA        -> apply Fix A only
  PROBE_MODE=fixAB       -> apply Fix A + Fix B (default)
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

os.environ.setdefault('PYTHONNOUSERSITE', '1')

# Capture mode early so the CUDA device pin happens before torch is first
# imported (Fix A requires that the env var be set before torch.cuda inits).
PROBE_MODE = os.environ.get('PROBE_MODE', 'fixAB').lower()
if PROBE_MODE in ('fixa', 'fixab'):
    os.environ.setdefault('CUDA_VISIBLE_DEVICES', '0')

import numpy as np


PDB_PATH = "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/crambin.pdb"
OUTPUT_DIR = os.environ.get(
    "PROBE_OUTPUT_DIR",
    "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/optl",
)
TAG = os.environ.get("PROBE_TAG", f"probe_{PROBE_MODE}")
RESULTS_PATH = os.path.join(OUTPUT_DIR, f"cuda_interop_{TAG}.json")


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] {msg}", flush=True)


def apply_fix_b_monkey_patch() -> None:
    """Insert torch.cuda.synchronize() around the MACE forward pass."""
    import openmmml.models.macepotential as mp
    original = mp._computeMACE

    def _computeMACE_sync(state, **kw):  # type: ignore[no-redef]
        import torch
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        energy, forces = original(state, **kw)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        return energy, forces

    mp._computeMACE = _computeMACE_sync
    log("Fix B applied: _computeMACE now wraps torch.cuda.synchronize().")


def main() -> int:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    results: dict = {
        "task": "cuda_interop_probe",
        "mode": PROBE_MODE,
        "started": datetime.now(timezone.utc).isoformat(),
        "env": {
            "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
        },
    }

    try:
        import torch
        import openmm
        from openmm import unit
        from openmm.app import PDBFile, Modeller, Simulation
        from openmmml import MLPotential

        results["env"]["torch_version"] = torch.__version__
        results["env"]["openmm_version"] = openmm.__version__
        results["env"]["torch_cuda_available"] = torch.cuda.is_available()

        log(f"MODE: {PROBE_MODE}")
        log(f"Torch {torch.__version__}, OpenMM {openmm.__version__}")
        log(f"CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES','')}")
        log(f"torch.cuda.is_available(): {torch.cuda.is_available()}")

        if torch.cuda.is_available():
            if PROBE_MODE in ('fixa', 'fixab'):
                torch.cuda.init()
                torch.cuda.set_device(0)
                log(f"torch.cuda.set_device(0) -> "
                    f"current_device={torch.cuda.current_device()}, "
                    f"name={torch.cuda.get_device_name(0)}")
                results["env"]["torch_cuda_device"] = 0
                results["env"]["torch_cuda_name"] = torch.cuda.get_device_name(0)

        if PROBE_MODE == 'fixab':
            apply_fix_b_monkey_patch()

        # ---- Build system (classical AMBER14 -> createMixedSystem hybrid) ----
        log(f"Loading PDB {PDB_PATH}")
        pdb = PDBFile(PDB_PATH)
        modeller = Modeller(pdb.topology, pdb.positions)
        modeller.addHydrogens()
        n_atoms = modeller.topology.getNumAtoms()
        log(f"Topology: {n_atoms} atoms (vacuum)")

        # Force hybrid path (createMixedSystem) even on vacuum so we exercise
        # the same code path that crashed for Subagent J. We give it a classical
        # AMBER14 system as the MM part and pass ALL atoms as MACE atoms.
        from openmm.app import ForceField
        ff = ForceField('amber14-all.xml')
        mm_system = ff.createSystem(
            modeller.topology,
            nonbondedMethod=openmm.app.NoCutoff,
            constraints=None,
        )
        log(f"MM system built: {mm_system.getNumForces()} forces")

        t0 = time.time()
        # Pass device='cuda:0' so MACE model lives on the same GPU ordinal OpenMM uses.
        device_kwarg = 'cuda:0' if (PROBE_MODE in ('fixa', 'fixab')
                                     and torch.cuda.is_available()) else None
        potential = MLPotential('mace-off24-medium')
        all_atoms = list(range(n_atoms))
        if device_kwarg:
            hybrid_system = potential.createMixedSystem(
                modeller.topology, mm_system, all_atoms,
                interpolate=False, device=device_kwarg,
            )
        else:
            hybrid_system = potential.createMixedSystem(
                modeller.topology, mm_system, all_atoms, interpolate=False,
            )
        t_sys = time.time() - t0
        log(f"Hybrid system built in {t_sys:.1f}s: "
            f"{hybrid_system.getNumParticles()} particles, "
            f"{hybrid_system.getNumForces()} forces")
        results["hybrid_build_s"] = t_sys

        if torch.cuda.is_available() and PROBE_MODE in ('fixa', 'fixab'):
            torch.cuda.synchronize()
            log("torch.cuda.synchronize() after hybrid build OK")

        # ---- Select CUDA platform ----
        platform = openmm.Platform.getPlatformByName('CUDA')
        properties = {"Precision": "mixed"}
        if PROBE_MODE in ('fixa', 'fixab'):
            properties["DeviceIndex"] = "0"
            properties["DeterministicForces"] = "false"

        integrator = openmm.LangevinMiddleIntegrator(
            300.0 * unit.kelvin,
            1.0 / unit.picosecond,
            1.0 * unit.femtosecond,
        )
        sim = Simulation(modeller.topology, hybrid_system, integrator,
                         platform, properties)
        sim.context.setPositions(modeller.positions)
        log("Simulation (CUDA, hybrid) created OK")

        # Probe: one force evaluation
        t0 = time.time()
        state = sim.context.getState(getEnergy=True)
        pe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
        log(f"Probe getState(getEnergy): {(time.time()-t0)*1000:.1f} ms, PE={pe:.1f} kJ/mol")
        results["probe_getstate_pe_kJ_mol"] = pe

        if torch.cuda.is_available() and PROBE_MODE in ('fixa', 'fixab'):
            torch.cuda.synchronize()

        # Probe: one step
        t0 = time.time()
        sim.step(1)
        log(f"Probe step(1) in {(time.time()-t0)*1000:.1f} ms")
        results["probe_step_ok"] = True

        # ---- THE FAILURE POINT for Subagent J ----
        log("Entering minimizeEnergy(maxIterations=10) — this is where SubJ crashed")
        t0 = time.time()
        sim.minimizeEnergy(maxIterations=10)
        t_min = time.time() - t0
        log(f"minimizeEnergy(10 iter): {t_min:.2f} s — NO CRASH!")
        state = sim.context.getState(getEnergy=True)
        pe_after = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
        log(f"PE after min: {pe_after:.1f} kJ/mol")
        results["minimize_s"] = t_min
        results["pe_after_min_kJ_mol"] = pe_after

        # ---- Extended dynamics — scan to find the crash point ----
        # Subagent L found Fix A+B survives minimize + 10 steps but crashes
        # during a 10000-step production run. Probe the step-count axis.
        step_chunks = [10, 100, 500, 1000, 2000, 5000]
        n_survived = 0
        crash_at_step = None
        for chunk in step_chunks:
            t0 = time.time()
            try:
                sim.step(chunk)
                if torch.cuda.is_available():
                    torch.cuda.synchronize()
                dt = time.time() - t0
                n_survived += chunk
                # 1 step = 1 fs = 1e-6 ns (DT_FS=1)
                ns_per_day = (chunk * 1e-6) / (dt / 86400.0) if dt > 0 else 0.0
                log(f"  +{chunk} steps OK (total {n_survived}): {dt:.2f}s "
                    f"({ns_per_day:.3f} ns/day)")
            except Exception as ex:
                crash_at_step = n_survived + chunk
                log(f"  CRASH after attempting +{chunk} steps "
                    f"(total survived={n_survived}): {type(ex).__name__}: {ex}")
                results["crash_at_step"] = crash_at_step
                results["crash_exception"] = str(ex)
                break
        results["steps_survived"] = n_survived
        state = sim.context.getState(getEnergy=True)
        pe_final = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
        log(f"PE after dynamics (survived {n_survived} steps): {pe_final:.1f} kJ/mol")
        results["pe_after_dynamics_kJ_mol"] = pe_final

        results["verdict"] = "PASS"
        results["verdict_reason"] = (
            f"Probe + minimization + dynamics all succeeded in mode {PROBE_MODE}"
        )
        results["completed"] = datetime.now(timezone.utc).isoformat()
        with open(RESULTS_PATH, "w") as fh:
            json.dump(results, fh, indent=2, default=str)
        log(f"Verdict: PASS. Results -> {RESULTS_PATH}")
        return 0

    except Exception as e:
        tb = traceback.format_exc()
        log(f"FATAL: {type(e).__name__}: {e}")
        log(tb)
        results["verdict"] = "FAIL"
        results["error"] = f"{type(e).__name__}: {e}"
        results["traceback"] = tb
        results["completed"] = datetime.now(timezone.utc).isoformat()
        try:
            with open(RESULTS_PATH, "w") as fh:
                json.dump(results, fh, indent=2, default=str)
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
