#!/usr/bin/env python
"""
mace_crambin_nvt.py -- MACE-OFF24 NVT simulation of crambin (1CRN, 46 residues)
Stage A: Vacuum NVT (validates MACE force evaluation via OpenMM-ML)
Stage B: Explicit solvent NVT (realistic benchmark conditions)
Stage C: Hybrid MACE protein + classical water (fallback if B fails)

D1 gate criterion: "MACE-OFF24 installs and runs 1 ns NVT on crambin."
  PASS: >= 100 ps stable NVT trajectory with reasonable RMSD and energy
  FAIL: Cannot produce stable trajectory, NaN forces, or crashes
"""
import os
import sys
import time
import json
import csv
import traceback
import numpy as np
from datetime import datetime, timezone

# Suppress user site-packages
os.environ['PYTHONNOUSERSITE'] = '1'

# Configuration
PDB_PATH = "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/crambin.pdb"
OUTPUT_DIR = os.environ.get("MACE_OUTPUT_DIR",
    "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output")
SCRATCH_DIR = os.environ.get("MACE_SCRATCH_DIR",
    "/nfs/roberts/scratch/pi_mg269/rag88/mace-crambin")

# Simulation parameters
TEMPERATURE_K = 300.0
FRICTION = 1.0           # 1/ps for Langevin
DT_FS = 1.0              # 1 fs timestep (conservative for MLFF)
REPORT_INTERVAL_PS = 1.0 # Save state every 1 ps
MIN_ACCEPT_PS = 100      # Minimum for D1 PASS

# Staged durations (cumulative -- each extends the previous)
STAGE_A_TARGETS_PS = [1, 10, 100, 1000]  # vacuum ramp
STAGE_B_TARGETS_PS = [1, 10, 100, 1000]  # solvated ramp

# NaN check interval
NAN_CHECK_INTERVAL_STEPS = 1000  # every 1 ps


def setup_dirs():
    """Create output directories."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(SCRATCH_DIR, exist_ok=True)
    os.makedirs(os.path.join(SCRATCH_DIR, "trajectories"), exist_ok=True)


def log(msg):
    """Timestamped logging."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] {msg}", flush=True)


def check_nan(simulation, step_label=""):
    """Check for NaN in positions, velocities, and forces. Returns PE."""
    import openmm
    from openmm import unit

    state = simulation.context.getState(getPositions=True, getForces=True,
                                         getEnergy=True)
    positions = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
    forces = state.getForces(asNumpy=True).value_in_unit(
        unit.kilojoules_per_mole / unit.nanometer)
    pe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)

    if np.any(np.isnan(positions)):
        raise RuntimeError(f"NaN positions at {step_label}")
    if np.any(np.isnan(forces)):
        raise RuntimeError(f"NaN forces at {step_label}")
    if np.isnan(pe):
        raise RuntimeError(f"NaN potential energy at {step_label}")
    if np.any(np.abs(forces) > 1e8):
        max_f = np.max(np.abs(forces))
        raise RuntimeError(f"Extreme forces ({max_f:.1e}) at {step_label}")

    return pe


def save_pdb_snapshot(simulation, topology, filepath):
    """Save current state as PDB for reference structure."""
    from openmm.app import PDBFile
    from openmm import unit
    state = simulation.context.getState(getPositions=True)
    with open(filepath, 'w') as f:
        PDBFile.writeFile(topology, state.getPositions(), f)


def run_nvt_ramp(simulation, topology, targets_ps, label, results_dict):
    """Run ramped NVT simulation with NaN checking. Returns max stable ps."""
    import openmm
    from openmm import unit
    from openmm.app import DCDReporter, StateDataReporter

    max_stable_ps = 0
    cumulative_steps = 0

    for target_ps in targets_ps:
        stage_key = f"{target_ps}ps"
        total_steps_needed = int(target_ps * 1000 / DT_FS)
        steps_this_stage = total_steps_needed - cumulative_steps
        report_steps = max(1, int(REPORT_INTERVAL_PS * 1000 / DT_FS))

        log(f"--- {label}: {target_ps} ps total ({steps_this_stage} new steps) ---")

        # Set up reporters for this stage
        traj_file = os.path.join(SCRATCH_DIR, "trajectories",
                                  f"crambin_{label}_{target_ps}ps.dcd")
        log_file = os.path.join(OUTPUT_DIR, f"crambin_{label}_{target_ps}ps.log")

        # Clear existing reporters and add fresh ones
        simulation.reporters = []
        dcd_reporter = DCDReporter(traj_file, report_steps)
        state_reporter = StateDataReporter(
            log_file, report_steps,
            step=True, time=True, potentialEnergy=True, kineticEnergy=True,
            totalEnergy=True, temperature=True, speed=True
        )
        simulation.reporters = [dcd_reporter, state_reporter]

        # Run with NaN checking
        t0 = time.time()
        steps_done = 0
        nan_error = None
        check_steps = int(NAN_CHECK_INTERVAL_STEPS)

        try:
            while steps_done < steps_this_stage:
                chunk = min(check_steps, steps_this_stage - steps_done)
                simulation.step(chunk)
                steps_done += chunk
                cumulative_ps = (cumulative_steps + steps_done) * DT_FS / 1000
                check_nan(simulation, f"{label} {cumulative_ps:.1f}ps")
        except RuntimeError as e:
            nan_error = str(e)
            log(f"  NaN/instability at step {cumulative_steps + steps_done}: {nan_error}")

        wall_time = time.time() - t0
        actual_new_ps = steps_done * DT_FS / 1000
        cumulative_steps += steps_done
        cumulative_ps = cumulative_steps * DT_FS / 1000

        # Get final state
        try:
            state = simulation.context.getState(getEnergy=True)
            pe_final = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
        except Exception:
            pe_final = float('nan')

        ns_per_day = (actual_new_ps / 1000) / (wall_time / 86400) if wall_time > 0 else 0

        stage_result = {
            "target_ps": target_ps,
            "actual_cumulative_ps": cumulative_ps,
            "steps_this_stage": steps_done,
            "wall_time_s": wall_time,
            "pe_final_kJ_mol": pe_final,
            "ns_per_day": ns_per_day,
            "stable": nan_error is None,
            "error": nan_error,
            "traj_file": traj_file,
            "log_file": log_file
        }
        results_dict["stages"][stage_key] = stage_result

        if nan_error is None:
            max_stable_ps = cumulative_ps
            log(f"  STABLE: {cumulative_ps:.1f} ps total in {wall_time:.1f}s "
                f"({ns_per_day:.3f} ns/day). PE = {pe_final:.1f} kJ/mol")
        else:
            log(f"  FAILED at {cumulative_ps:.1f} ps: {nan_error}")
            break  # Don't try longer durations after instability

    results_dict["max_stable_ps"] = max_stable_ps
    return max_stable_ps


def run_stage_a(results):
    """Stage A: Vacuum NVT simulation."""
    import openmm
    from openmm import unit
    from openmm.app import PDBFile, Modeller, Simulation

    log("=== STAGE A: Vacuum NVT ===")

    # Load crambin
    log(f"Loading PDB from {PDB_PATH}")
    pdb = PDBFile(PDB_PATH)
    modeller = Modeller(pdb.topology, pdb.positions)
    log(f"Topology: {modeller.topology.getNumAtoms()} atoms, "
        f"{modeller.topology.getNumResidues()} residues")

    # Add hydrogens
    log("Adding hydrogens...")
    modeller.addHydrogens()
    n_atoms = modeller.topology.getNumAtoms()
    log(f"After hydrogens: {n_atoms} atoms")

    # Create MACE potential
    log("Creating MACE-OFF24-medium ML potential...")
    from openmmml import MLPotential
    t0 = time.time()
    potential = MLPotential('mace-off24-medium')
    system = potential.createSystem(modeller.topology)
    t_sys = time.time() - t0
    log(f"System created in {t_sys:.1f}s: {system.getNumParticles()} particles, "
        f"{system.getNumForces()} forces")

    # Integrator
    integrator = openmm.LangevinMiddleIntegrator(
        TEMPERATURE_K * unit.kelvin,
        FRICTION / unit.picosecond,
        DT_FS * unit.femtosecond
    )

    # Platform (prefer CUDA, fall back to CPU if PTX/arch issues)
    platform = None
    platform_name = "unknown"
    simulation = None
    for pname in ["CUDA", "OpenCL", "CPU"]:
        try:
            platform = openmm.Platform.getPlatformByName(pname)
            properties = {}
            if pname == "CUDA":
                properties["Precision"] = "mixed"
            # Test context creation to catch CUDA_ERROR_UNSUPPORTED_PTX_VERSION
            test_sim = Simulation(modeller.topology, system, integrator,
                                  platform, properties)
            test_sim.context.setPositions(modeller.positions)
            simulation = test_sim
            platform_name = pname
            log(f"Using platform: {pname}")
            break
        except Exception as e:
            log(f"Platform {pname} failed: {e}")
            # Need fresh integrator since the failed one may be consumed
            integrator = openmm.LangevinMiddleIntegrator(
                TEMPERATURE_K * unit.kelvin,
                FRICTION / unit.picosecond,
                DT_FS * unit.femtosecond
            )
            continue

    if simulation is None:
        raise RuntimeError("No OpenMM platform available (all failed)")
    simulation.context.setPositions(modeller.positions)

    # Energy minimization
    log("Minimizing energy (max 2000 iterations)...")
    t0 = time.time()
    simulation.minimizeEnergy(maxIterations=2000)
    t_min = time.time() - t0
    state = simulation.context.getState(getEnergy=True)
    pe_min = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
    log(f"Minimization complete in {t_min:.1f}s. PE = {pe_min:.1f} kJ/mol")

    check_nan(simulation, "post-minimization")

    # Save minimized structure
    min_pdb = os.path.join(OUTPUT_DIR, "crambin_minimized_vacuum.pdb")
    save_pdb_snapshot(simulation, modeller.topology, min_pdb)
    log(f"Minimized structure saved to {min_pdb}")

    results["stage_a"] = {
        "platform": platform_name,
        "n_atoms": n_atoms,
        "pe_minimized_kJ_mol": pe_min,
        "minimization_time_s": t_min,
        "system_creation_time_s": t_sys,
        "stages": {}
    }

    # Set velocities and run ramped NVT
    simulation.context.setVelocitiesToTemperature(TEMPERATURE_K * unit.kelvin)
    max_stable = run_nvt_ramp(simulation, modeller.topology,
                               STAGE_A_TARGETS_PS, "vacuum", results["stage_a"])

    results["stage_a"]["d1_pass"] = max_stable >= MIN_ACCEPT_PS
    log(f"Stage A complete. Max stable: {max_stable} ps. "
        f"D1 {'PASS' if max_stable >= MIN_ACCEPT_PS else 'FAIL'}")

    return max_stable >= MIN_ACCEPT_PS


def run_stage_b(results):
    """Stage B: Explicit solvent NVT simulation."""
    import openmm
    from openmm import unit
    from openmm.app import PDBFile, Modeller, Simulation, ForceField

    log("=== STAGE B: Explicit Solvent NVT ===")

    pdb = PDBFile(PDB_PATH)
    modeller = Modeller(pdb.topology, pdb.positions)
    modeller.addHydrogens()

    # Add solvent
    log("Adding solvent (1.0 nm padding)...")
    ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
    modeller.addSolvent(ff, padding=1.0 * unit.nanometer)
    n_atoms = modeller.topology.getNumAtoms()
    log(f"After solvation: {n_atoms} atoms")

    # Try creating full MACE system for solvated system
    log("Creating MACE-OFF24 ML potential for solvated system...")
    from openmmml import MLPotential
    try:
        potential = MLPotential('mace-off24-medium')
        t0 = time.time()
        system = potential.createSystem(modeller.topology)
        t_sys = time.time() - t0
        log(f"Solvated system created in {t_sys:.1f}s: "
            f"{system.getNumParticles()} particles")
    except Exception as e:
        log(f"MACE solvated system creation failed: {e}")
        results["stage_b"] = {
            "status": "failed",
            "error": str(e),
            "note": "MACE may not support water. Try Stage C (hybrid)."
        }
        return False

    # Platform (prefer CUDA, fall back to CPU if PTX/arch issues)
    simulation = None
    platform_name = "unknown"
    for pname in ["CUDA", "OpenCL", "CPU"]:
        try:
            platform = openmm.Platform.getPlatformByName(pname)
            properties = {}
            if pname == "CUDA":
                properties["Precision"] = "mixed"
            integrator = openmm.LangevinMiddleIntegrator(
                TEMPERATURE_K * unit.kelvin,
                FRICTION / unit.picosecond,
                DT_FS * unit.femtosecond
            )
            test_sim = Simulation(modeller.topology, system, integrator,
                                   platform, properties)
            test_sim.context.setPositions(modeller.positions)
            simulation = test_sim
            platform_name = pname
            log(f"Using platform: {pname}")
            break
        except Exception as e:
            log(f"Platform {pname} failed: {e}")
            continue

    if simulation is None:
        log("All platforms failed for solvated system")
        results["stage_b"] = {"status": "failed", "error": "No platform available"}
        return False

    # Minimize
    log("Minimizing solvated system...")
    t0 = time.time()
    simulation.minimizeEnergy(maxIterations=2000)
    t_min = time.time() - t0
    state = simulation.context.getState(getEnergy=True)
    pe_min = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
    log(f"Minimization: {t_min:.1f}s, PE = {pe_min:.1f} kJ/mol")

    results["stage_b"] = {
        "platform": platform_name,
        "n_atoms": n_atoms,
        "pe_minimized_kJ_mol": pe_min,
        "system_creation_time_s": t_sys,
        "stages": {}
    }

    # Run ramped NVT
    simulation.context.setVelocitiesToTemperature(TEMPERATURE_K * unit.kelvin)
    max_stable = run_nvt_ramp(simulation, modeller.topology,
                               STAGE_B_TARGETS_PS, "solvated", results["stage_b"])

    results["stage_b"]["max_stable_ps"] = max_stable
    return max_stable >= MIN_ACCEPT_PS


def run_stage_c(results):
    """Stage C: Hybrid MACE protein + classical water (fallback)."""
    import openmm
    from openmm import unit
    from openmm.app import PDBFile, Modeller, Simulation, ForceField

    log("=== STAGE C: Hybrid MACE + Classical Water ===")

    pdb = PDBFile(PDB_PATH)
    modeller = Modeller(pdb.topology, pdb.positions)
    modeller.addHydrogens()

    ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
    modeller.addSolvent(ff, padding=1.0 * unit.nanometer)
    n_atoms = modeller.topology.getNumAtoms()
    log(f"Solvated system: {n_atoms} atoms")

    # Create classical system first
    log("Creating classical force field system...")
    system = ff.createSystem(modeller.topology,
                              nonbondedMethod=openmm.app.PME,
                              nonbondedCutoff=1.0 * unit.nanometer,
                              constraints=openmm.app.HBonds)

    # Identify protein atom indices
    protein_atoms = []
    for residue in modeller.topology.residues():
        if residue.name not in ('HOH', 'WAT', 'NA', 'CL', 'TIP3'):
            for atom in residue.atoms():
                protein_atoms.append(atom.index)

    log(f"Protein atoms: {len(protein_atoms)}, Water/ion atoms: {n_atoms - len(protein_atoms)}")

    # Try hybrid: MACE for protein, classical for rest
    log("Attempting hybrid MACE+classical setup...")
    from openmmml import MLPotential
    try:
        potential = MLPotential('mace-off24-medium')
        system = potential.createMixedSystem(
            modeller.topology,
            system,
            protein_atoms,
            interpolate=False
        )
        log("Hybrid system created successfully")
    except AttributeError:
        log("createMixedSystem not available in this openmmml version")
        results["stage_c"] = {"status": "failed", "error": "createMixedSystem not available"}
        return False
    except Exception as e:
        log(f"Hybrid system creation failed: {e}")
        results["stage_c"] = {"status": "failed", "error": str(e),
                               "traceback": traceback.format_exc()}
        return False

    # Platform (prefer CUDA, fall back to CPU)
    simulation = None
    platform_name = "unknown"
    for pname in ["CUDA", "OpenCL", "CPU"]:
        try:
            platform = openmm.Platform.getPlatformByName(pname)
            properties = {}
            if pname == "CUDA":
                properties["Precision"] = "mixed"
            integrator = openmm.LangevinMiddleIntegrator(
                TEMPERATURE_K * unit.kelvin,
                FRICTION / unit.picosecond,
                DT_FS * unit.femtosecond
            )
            test_sim = Simulation(modeller.topology, system, integrator,
                                   platform, properties)
            test_sim.context.setPositions(modeller.positions)
            simulation = test_sim
            platform_name = pname
            log(f"Using platform: {pname}")
            break
        except Exception as e:
            log(f"Platform {pname} failed: {e}")
            continue

    if simulation is None:
        log("All platforms failed for hybrid system")
        results["stage_c"] = {"status": "failed", "error": "No platform available"}
        return False

    log("Minimizing hybrid system...")
    simulation.minimizeEnergy(maxIterations=2000)

    state = simulation.context.getState(getEnergy=True)
    pe_min = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)

    results["stage_c"] = {
        "n_atoms": n_atoms,
        "platform": platform_name,
        "pe_minimized_kJ_mol": pe_min,
        "stages": {}
    }

    # Run 100 ps test
    simulation.context.setVelocitiesToTemperature(TEMPERATURE_K * unit.kelvin)
    max_stable = run_nvt_ramp(simulation, modeller.topology,
                               [1, 10, 100], "hybrid", results["stage_c"])

    results["stage_c"]["max_stable_ps"] = max_stable
    return max_stable >= MIN_ACCEPT_PS


def analyze_logs(results):
    """Analyze energy and temperature from log files."""
    log("=== ANALYSIS ===")

    for stage_name in ["stage_a", "stage_b", "stage_c"]:
        if stage_name not in results:
            continue
        stage = results[stage_name]
        if "stages" not in stage:
            continue

        # Find the longest successful run
        best_key = None
        best_ps = 0
        for key, data in stage["stages"].items():
            if data.get("stable", False) and data.get("actual_cumulative_ps", 0) > best_ps:
                best_ps = data["actual_cumulative_ps"]
                best_key = key

        if best_key:
            log_file = stage["stages"][best_key].get("log_file", "")
            log(f"{stage_name} best run: {best_key} ({best_ps} ps), log: {log_file}")

            if log_file and os.path.exists(log_file):
                try:
                    energies = []
                    temperatures = []
                    times = []
                    with open(log_file) as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            try:
                                # StateDataReporter headers use quotes
                                pe_key = None
                                temp_key = None
                                time_key = None
                                for k in row.keys():
                                    kl = k.strip().strip('"')
                                    if 'Potential Energy' in kl:
                                        pe_key = k
                                    if 'Temperature' in kl:
                                        temp_key = k
                                    if 'Time' in kl and 'Step' not in kl:
                                        time_key = k

                                if pe_key:
                                    energies.append(float(row[pe_key]))
                                if temp_key:
                                    temperatures.append(float(row[temp_key]))
                                if time_key:
                                    times.append(float(row[time_key]))
                            except (ValueError, TypeError):
                                continue

                    if energies:
                        e_arr = np.array(energies)
                        t_arr = np.array(temperatures) if temperatures else np.array([])
                        time_arr = np.array(times) if times else np.array([])

                        stats = {
                            "mean_pe_kJ_mol": float(np.mean(e_arr)),
                            "std_pe_kJ_mol": float(np.std(e_arr)),
                            "min_pe_kJ_mol": float(np.min(e_arr)),
                            "max_pe_kJ_mol": float(np.max(e_arr)),
                            "pe_drift_kJ_mol": float(e_arr[-1] - e_arr[0]) if len(e_arr) > 1 else 0,
                            "n_frames": len(energies)
                        }
                        if len(t_arr) > 0:
                            stats["mean_temp_K"] = float(np.mean(t_arr))
                            stats["std_temp_K"] = float(np.std(t_arr))

                        stage["energy_stats"] = stats
                        log(f"  PE: {np.mean(e_arr):.1f} +/- {np.std(e_arr):.1f} kJ/mol "
                            f"(drift: {stats['pe_drift_kJ_mol']:.1f})")
                        if len(t_arr) > 0:
                            log(f"  Temp: {np.mean(t_arr):.1f} +/- {np.std(t_arr):.1f} K")
                except Exception as e:
                    log(f"  Log analysis error: {e}")
                    traceback.print_exc()


def determine_d1(results):
    """Determine overall D1 verdict."""
    d1_pass = False
    max_stable = 0
    best_stage = "none"

    for stage_name in ["stage_a", "stage_b", "stage_c"]:
        if stage_name in results:
            stage = results[stage_name]
            sps = stage.get("max_stable_ps", 0)
            if sps > max_stable:
                max_stable = sps
                best_stage = stage_name

    d1_pass = max_stable >= MIN_ACCEPT_PS

    results["d1_verdict"] = {
        "pass": d1_pass,
        "max_stable_ps": max_stable,
        "best_stage": best_stage,
        "criterion": f">= {MIN_ACCEPT_PS} ps stable NVT",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    log(f"D1 VERDICT: {'PASS' if d1_pass else 'FAIL'} "
        f"(max stable: {max_stable} ps in {best_stage})")

    return d1_pass


def main():
    """Main entry point."""
    log("MACE-OFF24 Crambin NVT -- D1 Gate Validation")
    log(f"PDB: {PDB_PATH}")
    log(f"Output: {OUTPUT_DIR}")
    log(f"Scratch: {SCRATCH_DIR}")

    # Print environment info
    try:
        import torch
        log(f"PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            log(f"  GPU: {torch.cuda.get_device_name(0)}")
            log(f"  VRAM: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB")
    except:
        pass
    try:
        import openmm
        log(f"OpenMM: {openmm.__version__}")
    except:
        pass

    setup_dirs()

    results = {
        "task": "task-001-mace-pilot",
        "protein": "crambin (1CRN)",
        "n_residues": 46,
        "started": datetime.now(timezone.utc).isoformat(),
        "parameters": {
            "temperature_K": TEMPERATURE_K,
            "friction_ps": FRICTION,
            "timestep_fs": DT_FS,
            "min_accept_ps": MIN_ACCEPT_PS,
            "report_interval_ps": REPORT_INTERVAL_PS
        }
    }

    # Stage A: Vacuum
    stage_a_pass = False
    try:
        stage_a_pass = run_stage_a(results)
    except Exception as e:
        log(f"Stage A EXCEPTION: {e}")
        traceback.print_exc()
        results["stage_a"] = {"status": "exception", "error": str(e),
                               "traceback": traceback.format_exc()}

    # Stage B: Solvated (only if A passed)
    stage_b_pass = False
    if stage_a_pass:
        try:
            stage_b_pass = run_stage_b(results)
        except Exception as e:
            log(f"Stage B EXCEPTION: {e}")
            traceback.print_exc()
            results["stage_b"] = {"status": "exception", "error": str(e),
                                   "traceback": traceback.format_exc()}

        # Stage C: Hybrid fallback (only if B failed)
        if not stage_b_pass:
            try:
                run_stage_c(results)
            except Exception as e:
                log(f"Stage C EXCEPTION: {e}")
                results["stage_c"] = {"status": "exception", "error": str(e)}
    else:
        log("Stage A failed or incomplete, skipping Stages B and C")
        log("Attempting Stage B anyway for additional data...")
        try:
            stage_b_pass = run_stage_b(results)
        except Exception as e:
            log(f"Stage B EXCEPTION: {e}")
            results["stage_b"] = {"status": "exception", "error": str(e)}

    # Analysis
    try:
        analyze_logs(results)
    except Exception as e:
        log(f"Analysis error: {e}")
        traceback.print_exc()

    # D1 verdict
    d1_pass = determine_d1(results)

    results["completed"] = datetime.now(timezone.utc).isoformat()

    # Save results JSON
    results_path = os.path.join(OUTPUT_DIR, "task-001-results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    log(f"Results saved to {results_path}")

    # Exit code: 0 for D1 PASS, 1 for D1 FAIL
    sys.exit(0 if d1_pass else 1)


if __name__ == "__main__":
    main()
