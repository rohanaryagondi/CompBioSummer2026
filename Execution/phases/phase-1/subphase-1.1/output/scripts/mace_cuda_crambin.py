#!/usr/bin/env python
"""
mace_cuda_crambin.py -- Test the env-mace-cuda CUDA platform on crambin vacuum.

The env-mace-cuda conda environment was created by cloning env-mace and swapping
its OpenMM 8.5.1 package to the `py310hc82e367_0` build variant which links
against cuda-nvrtc 12.9 (rather than the 13.2 variant used in env-mace). The
hypothesis is that the OpenMM CUDA platform will now work because cuda-nvrtc
12.9 emits PTX that is compatible with the cluster's GPU driver 570.195.03 /
CUDA 12.8.

This script runs the same vacuum crambin NVT as Sub 1.1's D1 test, but forces
CUDA as the FIRST-CHOICE platform. If CUDA fails, it falls back to OpenCL for
comparison.

Emits:
  - crambin_cuda_vacuum_<duration>ps.log  (StateDataReporter CSV)
  - mace_cuda_crambin_results.json (throughput + verdict)
"""
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

os.environ['PYTHONNOUSERSITE'] = '1'

PDB_PATH = "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/crambin.pdb"
OUTPUT_DIR = os.environ.get(
    "MACE_OUTPUT_DIR",
    "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/optj",
)
SCRATCH_DIR = os.environ.get(
    "MACE_SCRATCH_DIR",
    "/nfs/roberts/scratch/pi_mg269/rag88/mace-cuda",
)
TAG = os.environ.get("MACE_TAG", "cuda_crambin")

TEMPERATURE_K = 300.0
FRICTION = 1.0
DT_FS = 1.0
DURATION_PS = float(os.environ.get("MACE_DURATION_PS", "10"))
REPORT_INTERVAL_PS = 1.0


def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] {msg}", flush=True)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(SCRATCH_DIR, exist_ok=True)
    os.makedirs(os.path.join(SCRATCH_DIR, "trajectories"), exist_ok=True)

    results = {
        "task": "mace-cuda-vacuum-crambin",
        "env": "env-mace-cuda",
        "started": datetime.now(timezone.utc).isoformat(),
        "parameters": {
            "duration_ps": DURATION_PS,
            "timestep_fs": DT_FS,
            "temperature_K": TEMPERATURE_K,
        },
        "platforms_tried": [],
    }
    results_path = os.path.join(OUTPUT_DIR, f"mace_{TAG}_results.json")

    try:
        import openmm
        from openmm import unit
        from openmm.app import PDBFile, Modeller, Simulation, DCDReporter, StateDataReporter
        from openmmml import MLPotential
        import torch

        log(f"OpenMM {openmm.__version__}")
        log(f"PyTorch {torch.__version__}")
        log(f"CUDA available (torch): {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            log(f"  GPU: {torch.cuda.get_device_name(0)}")
            log(f"  Capability: {torch.cuda.get_device_capability(0)}")
        results["openmm_version"] = openmm.__version__
        results["torch_version"] = torch.__version__
        results["torch_cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            results["gpu_name"] = torch.cuda.get_device_name(0)
            results["gpu_capability"] = list(torch.cuda.get_device_capability(0))

        log(f"Platforms registered in OpenMM:")
        for i in range(openmm.Platform.getNumPlatforms()):
            p = openmm.Platform.getPlatform(i)
            log(f"  [{i}] {p.getName()} speed={p.getSpeed()}")

        # Load crambin
        log(f"Loading {PDB_PATH}")
        pdb = PDBFile(PDB_PATH)
        modeller = Modeller(pdb.topology, pdb.positions)
        modeller.addHydrogens()
        n_atoms = modeller.topology.getNumAtoms()
        log(f"Topology: {n_atoms} atoms")

        # Build MACE system
        t0 = time.time()
        potential = MLPotential('mace-off24-medium')
        system = potential.createSystem(modeller.topology)
        t_sys = time.time() - t0
        log(f"MACE system built in {t_sys:.1f}s")
        results["n_atoms"] = n_atoms
        results["system_build_time_s"] = t_sys

        # Try CUDA first, then OpenCL, then CPU
        simulation = None
        platform_name = None
        for pname in ["CUDA", "OpenCL", "CPU"]:
            try:
                platform = openmm.Platform.getPlatformByName(pname)
                properties = {"Precision": "mixed"} if pname == "CUDA" else {}
                integrator = openmm.LangevinMiddleIntegrator(
                    TEMPERATURE_K * unit.kelvin,
                    FRICTION / unit.picosecond,
                    DT_FS * unit.femtosecond,
                )
                sim = Simulation(modeller.topology, system, integrator, platform, properties)
                sim.context.setPositions(modeller.positions)
                # Actually test: try to compute one step
                t_probe = time.time()
                sim.step(1)
                t_probe_dt = time.time() - t_probe
                state = sim.context.getState(getEnergy=True)
                pe_probe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
                simulation = sim
                platform_name = pname
                log(f"Platform {pname} ACTIVE: probe step in {t_probe_dt*1000:.1f}ms, PE={pe_probe:.1f}")
                results["platforms_tried"].append({
                    "name": pname,
                    "status": "OK",
                    "probe_step_ms": t_probe_dt * 1000,
                    "probe_pe_kJ_mol": pe_probe,
                })
                break
            except Exception as e:
                err = f"{type(e).__name__}: {e}"
                log(f"Platform {pname} FAILED: {err}")
                results["platforms_tried"].append({
                    "name": pname,
                    "status": "FAILED",
                    "error": err,
                })
                continue

        if simulation is None:
            results["verdict"] = "FAIL"
            results["verdict_reason"] = "No platform available"
            with open(results_path, "w") as fh:
                json.dump(results, fh, indent=2, default=str)
            return 1

        results["platform_selected"] = platform_name

        # Minimize energy
        log("Minimizing energy (max 2000 iter)...")
        t0 = time.time()
        simulation.minimizeEnergy(maxIterations=2000)
        t_min = time.time() - t0
        state = simulation.context.getState(getEnergy=True)
        pe_min = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
        log(f"Minimization: {t_min:.1f}s, PE = {pe_min:.1f} kJ/mol")
        results["minimization"] = {"wall_time_s": t_min, "pe_kJ_mol": pe_min}

        # NVT run
        simulation.context.setVelocitiesToTemperature(TEMPERATURE_K * unit.kelvin)
        steps = int(DURATION_PS * 1000 / DT_FS)
        report_steps = max(1, int(REPORT_INTERVAL_PS * 1000 / DT_FS))
        log_file = os.path.join(OUTPUT_DIR, f"crambin_{TAG}_{int(DURATION_PS)}ps.log")
        traj_file = os.path.join(SCRATCH_DIR, "trajectories", f"crambin_{TAG}.dcd")
        simulation.reporters = [
            DCDReporter(traj_file, report_steps),
            StateDataReporter(
                log_file, report_steps,
                step=True, time=True, potentialEnergy=True, kineticEnergy=True,
                totalEnergy=True, temperature=True, speed=True,
            ),
        ]
        log(f"Running NVT: {DURATION_PS} ps ({steps} steps) on {platform_name}...")
        t0 = time.time()
        simulation.step(steps)
        t_run = time.time() - t0
        ns_per_day = (DURATION_PS / 1000.0) / (t_run / 86400.0) if t_run > 0 else 0.0
        log(f"NVT done: {t_run:.1f}s ({ns_per_day:.3f} ns/day)")

        state = simulation.context.getState(getEnergy=True, getPositions=True, getForces=True)
        pe_final = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
        pos = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        forces = state.getForces(asNumpy=True).value_in_unit(unit.kilojoule_per_mole / unit.nanometer)
        any_nan = bool(np.any(np.isnan(pos)) or np.any(np.isnan(forces)) or np.isnan(pe_final))
        max_force = float(np.max(np.abs(forces)))

        results["nvt"] = {
            "wall_time_s": t_run,
            "ns_per_day": ns_per_day,
            "steps": steps,
            "pe_final_kJ_mol": pe_final,
            "max_abs_force": max_force,
            "any_nan": any_nan,
        }

        if any_nan or max_force > 1e7:
            results["verdict"] = "FAIL"
            results["verdict_reason"] = (
                f"NaN encountered" if any_nan else f"max force {max_force:.2e}"
            )
        else:
            results["verdict"] = "PASS"
            results["verdict_reason"] = (
                f"{platform_name} ran {DURATION_PS} ps stable at {ns_per_day:.3f} ns/day"
            )

        results["completed"] = datetime.now(timezone.utc).isoformat()
        with open(results_path, "w") as fh:
            json.dump(results, fh, indent=2, default=str)
        log("=========================================================")
        log(f"VERDICT: {results['verdict']}")
        log(f"Platform: {platform_name}")
        log(f"Throughput: {ns_per_day:.3f} ns/day  (crambin vacuum, {n_atoms} atoms)")
        log(f"Results JSON: {results_path}")
        log("=========================================================")
        return 0 if results["verdict"] == "PASS" else 1
    except Exception as e:
        log(f"FATAL: {e}")
        log(traceback.format_exc())
        results["fatal_exception"] = {"error": str(e), "traceback": traceback.format_exc()}
        results["verdict"] = "FAIL"
        results["completed"] = datetime.now(timezone.utc).isoformat()
        with open(results_path, "w") as fh:
            json.dump(results, fh, indent=2, default=str)
        return 1


if __name__ == "__main__":
    sys.exit(main())
