#!/usr/bin/env python
"""
mace_cuda_hybrid_ww.py -- Hybrid MACE-OFF24 + classical solvent NVT on WW
domain using the env-mace-cuda CUDA platform.

Benchmark target: exceed OpenCL's 0.184 ns/day baseline (Sub 1.1 §10 empirical).

Strategy:
  - Load full Pin1 PDB, crop to chain A residues 6-39 (WW domain).
  - PDBFixer: add missing heavy atoms + hydrogens at pH 7.
  - Add TIP3P-FB solvent, 1.0 nm padding, 0.15 M NaCl.
  - Build classical AMBER14 + TIP3P-FB system (PME, 1.0 nm cutoff).
  - Use MLPotential.createMixedSystem to treat the 534 protein atoms with
    MACE-OFF24-medium and let classical forces handle waters+ions.
  - Try CUDA first, then OpenCL, then CPU.
  - Run 2 ps minimization + 2 ps equilibration + 3 ps production.
  - Report ns/day for each stage; compare to OpenCL baseline.
"""
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

os.environ['PYTHONNOUSERSITE'] = '1'

PDB_PATH = "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ww.pdb"
OUTPUT_DIR = os.environ.get(
    "MACE_OUTPUT_DIR",
    "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/optj",
)
SCRATCH_DIR = os.environ.get(
    "MACE_SCRATCH_DIR",
    "/nfs/roberts/scratch/pi_mg269/rag88/mace-cuda-hybrid",
)
TAG = os.environ.get("MACE_TAG", "cuda_hybrid_ww")
RESRANGE = os.environ.get("MACE_RESRANGE", "6-39")

# Shortened defaults vs Sub 1.1 to fit in a ~60 min GPU budget
TEMPERATURE_K = 300.0
FRICTION = 1.0
DT_FS = 1.0
EQUIL_PS = float(os.environ.get("MACE_EQUIL_PS", "2"))
PROD_PS = float(os.environ.get("MACE_PROD_PS", "3"))
REPORT_INTERVAL_PS = 1.0
NAN_CHECK_INTERVAL_STEPS = 1000
SOLVENT_PADDING_NM = 1.0
NB_CUTOFF_NM = 1.0
IONIC_STRENGTH_M = 0.15


def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] {msg}", flush=True)


def load_and_crop():
    from openmm.app import PDBFile, Modeller
    log(f"Loading PDB: {PDB_PATH}")
    pdb = PDBFile(PDB_PATH)
    modeller = Modeller(pdb.topology, pdb.positions)
    log(f"  raw: {modeller.topology.getNumAtoms()} atoms, "
        f"{modeller.topology.getNumResidues()} residues")
    std_aa = {
        'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE',
        'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL',
        'HID', 'HIE', 'HIP', 'CYX', 'CYM', 'ASH', 'GLH', 'LYN',
    }
    # Delete non-protein residues
    to_del = [r for r in modeller.topology.residues() if r.name not in std_aa]
    if to_del:
        modeller.delete(to_del)
    # Keep only first chain
    first_chain_id = list(modeller.topology.chains())[0].id
    other_residues = []
    for chain in modeller.topology.chains():
        if chain.id != first_chain_id:
            other_residues.extend(chain.residues())
    if other_residues:
        modeller.delete(other_residues)
    # Crop residues
    if RESRANGE and "-" in RESRANGE:
        s, e = RESRANGE.split("-", 1)
        si, ei = int(s), int(e)
        to_del = []
        for residue in modeller.topology.residues():
            try:
                rid = int(residue.id)
            except ValueError:
                continue
            if rid < si or rid > ei:
                to_del.append(residue)
        if to_del:
            modeller.delete(to_del)
    log(f"  after crop: {modeller.topology.getNumAtoms()} atoms, "
        f"{modeller.topology.getNumResidues()} residues")
    return modeller


def check_nan(sim, label):
    from openmm import unit
    state = sim.context.getState(getPositions=True, getForces=True, getEnergy=True)
    pos = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
    forces = state.getForces(asNumpy=True).value_in_unit(
        unit.kilojoule_per_mole / unit.nanometer)
    pe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
    if np.any(np.isnan(pos)) or np.any(np.isnan(forces)) or np.isnan(pe):
        raise RuntimeError(f"NaN at {label}")
    max_f = float(np.max(np.abs(forces)))
    if max_f > 1e8:
        raise RuntimeError(f"Extreme force {max_f:.2e} at {label}")
    return pe


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(SCRATCH_DIR, exist_ok=True)
    os.makedirs(os.path.join(SCRATCH_DIR, "trajectories"), exist_ok=True)

    results = {
        "task": "mace-cuda-hybrid-ww",
        "env": "env-mace-cuda",
        "started": datetime.now(timezone.utc).isoformat(),
        "resrange": RESRANGE,
        "parameters": {
            "equil_ps": EQUIL_PS,
            "prod_ps": PROD_PS,
            "temperature_K": TEMPERATURE_K,
            "timestep_fs": DT_FS,
            "solvent_padding_nm": SOLVENT_PADDING_NM,
            "ionic_strength_M": IONIC_STRENGTH_M,
        },
        "platforms_tried": [],
    }
    results_path = os.path.join(OUTPUT_DIR, f"mace_{TAG}_results.json")

    try:
        import openmm
        from openmm import unit
        from openmm.app import (
            PDBFile, Modeller, Simulation, ForceField, DCDReporter,
            StateDataReporter, PME, HBonds,
        )
        from openmmml import MLPotential
        from pdbfixer import PDBFixer
        import torch

        log(f"OpenMM {openmm.__version__}  PyTorch {torch.__version__}")
        log(f"CUDA avail: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            log(f"  GPU: {torch.cuda.get_device_name(0)}  cap={torch.cuda.get_device_capability(0)}")
        results["openmm_version"] = openmm.__version__
        results["torch_version"] = torch.__version__
        if torch.cuda.is_available():
            results["gpu_name"] = torch.cuda.get_device_name(0)
            results["gpu_capability"] = list(torch.cuda.get_device_capability(0))

        modeller = load_and_crop()

        # PDBFixer
        log("Running PDBFixer...")
        tmp_pdb = os.path.join(SCRATCH_DIR, f"{TAG}_protein_only.pdb")
        with open(tmp_pdb, 'w') as f:
            PDBFile.writeFile(modeller.topology, modeller.positions, f)
        fixer = PDBFixer(filename=tmp_pdb)
        fixer.findMissingResidues()
        fixer.missingResidues = {}
        fixer.findNonstandardResidues()
        fixer.replaceNonstandardResidues()
        fixer.findMissingAtoms()
        fixer.addMissingAtoms()
        fixer.addMissingHydrogens(pH=7.0)
        modeller = Modeller(fixer.topology, fixer.positions)
        protein_atom_count = modeller.topology.getNumAtoms()
        log(f"  after PDBFixer: {protein_atom_count} atoms")
        protein_atoms = list(range(protein_atom_count))

        # Solvate
        log(f"Adding TIP3P-FB solvent, padding {SOLVENT_PADDING_NM} nm, {IONIC_STRENGTH_M} M NaCl")
        ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
        modeller.addSolvent(
            ff,
            padding=SOLVENT_PADDING_NM * unit.nanometer,
            ionicStrength=IONIC_STRENGTH_M * unit.molar,
            model='tip3p',
        )
        total_atom_count = modeller.topology.getNumAtoms()
        log(f"  after solvate: {total_atom_count} atoms ({protein_atom_count} MACE + "
            f"{total_atom_count - protein_atom_count} classical)")

        # Classical system
        log("Building classical AMBER14 + TIP3P-FB system (PME, 1.0 nm)")
        mm_system = ff.createSystem(
            modeller.topology,
            nonbondedMethod=PME,
            nonbondedCutoff=NB_CUTOFF_NM * unit.nanometer,
            constraints=None,
            rigidWater=True,
        )

        # Hybrid MACE system
        log(f"Creating hybrid MACE-OFF24-medium system ({protein_atom_count} MACE atoms)")
        t0 = time.time()
        potential = MLPotential('mace-off24-medium')
        hybrid_system = potential.createMixedSystem(
            modeller.topology,
            mm_system,
            protein_atoms,
            interpolate=False,
        )
        t_sys = time.time() - t0
        log(f"  hybrid built in {t_sys:.1f}s")
        results["protein_atom_count"] = protein_atom_count
        results["total_atom_count"] = total_atom_count
        results["hybrid_build_time_s"] = t_sys

        # Platform selection
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
                sim = Simulation(modeller.topology, hybrid_system, integrator,
                                 platform, properties)
                sim.context.setPositions(modeller.positions)
                # Probe: 1 step
                t_probe = time.time()
                sim.step(1)
                t_probe_dt = time.time() - t_probe
                state = sim.context.getState(getEnergy=True)
                pe_probe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
                log(f"Platform {pname} ACTIVE: probe step {t_probe_dt*1000:.1f}ms, PE={pe_probe:.1f}")
                results["platforms_tried"].append({
                    "name": pname, "status": "OK",
                    "probe_step_ms": t_probe_dt * 1000, "probe_pe": pe_probe,
                })
                simulation = sim
                platform_name = pname
                break
            except Exception as e:
                err = f"{type(e).__name__}: {e}"
                log(f"Platform {pname} FAILED: {err}")
                results["platforms_tried"].append({
                    "name": pname, "status": "FAILED", "error": err,
                })
                continue

        if simulation is None:
            results["verdict"] = "FAIL"
            results["verdict_reason"] = "No platform usable"
            with open(results_path, 'w') as fh:
                json.dump(results, fh, indent=2, default=str)
            return 1
        results["platform_selected"] = platform_name

        # Minimize
        log("Minimizing energy (max 2000 iter, tol 10 kJ/mol/nm)...")
        t0 = time.time()
        simulation.minimizeEnergy(
            maxIterations=2000,
            tolerance=10 * unit.kilojoule_per_mole / unit.nanometer,
        )
        t_min = time.time() - t0
        post_min_state = simulation.context.getState(getForces=True, getEnergy=True)
        post_min_forces = post_min_state.getForces(asNumpy=True).value_in_unit(
            unit.kilojoule_per_mole / unit.nanometer)
        max_f = float(np.max(np.abs(post_min_forces)))
        pe_min = post_min_state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
        log(f"  min: {t_min:.1f}s, PE={pe_min:.1f}, max_force={max_f:.2e} kJ/mol/nm")
        if max_f > 1e5:
            raise RuntimeError(f"Post-min max force {max_f:.2e} too high")
        check_nan(simulation, "post-min")
        results["minimization"] = {
            "wall_time_s": t_min,
            "pe_kJ_mol": pe_min,
            "max_force": max_f,
        }

        # Equilibration
        simulation.context.setVelocitiesToTemperature(TEMPERATURE_K * unit.kelvin)
        equil_steps = int(EQUIL_PS * 1000 / DT_FS)
        report_steps = max(1, int(REPORT_INTERVAL_PS * 1000 / DT_FS))
        equil_log = os.path.join(OUTPUT_DIR, f"hybrid_{TAG}_equil.log")
        equil_traj = os.path.join(SCRATCH_DIR, "trajectories", f"{TAG}_equil.dcd")
        simulation.reporters = [
            DCDReporter(equil_traj, report_steps),
            StateDataReporter(
                equil_log, report_steps,
                step=True, time=True, potentialEnergy=True, kineticEnergy=True,
                totalEnergy=True, temperature=True, speed=True,
            ),
        ]
        log(f"Equilibration: {EQUIL_PS} ps ({equil_steps} steps) on {platform_name}")
        t0 = time.time()
        steps_done, last_check = 0, 0
        while steps_done < equil_steps:
            chunk = min(NAN_CHECK_INTERVAL_STEPS, equil_steps - steps_done)
            simulation.step(chunk)
            steps_done += chunk
            if steps_done - last_check >= NAN_CHECK_INTERVAL_STEPS:
                check_nan(simulation, f"equil {steps_done * DT_FS / 1000:.1f}ps")
                last_check = steps_done
        t_equil = time.time() - t0
        equil_ns_day = (EQUIL_PS / 1000.0) / (t_equil / 86400.0) if t_equil > 0 else 0.0
        log(f"  equil: {t_equil:.1f}s ({equil_ns_day:.3f} ns/day)")
        results["equilibration"] = {
            "wall_time_s": t_equil,
            "ns_per_day": equil_ns_day,
            "ps": EQUIL_PS,
        }

        # Production
        prod_steps = int(PROD_PS * 1000 / DT_FS)
        prod_log = os.path.join(OUTPUT_DIR, f"hybrid_{TAG}_prod.log")
        prod_traj = os.path.join(SCRATCH_DIR, "trajectories", f"{TAG}_prod.dcd")
        simulation.reporters = [
            DCDReporter(prod_traj, report_steps),
            StateDataReporter(
                prod_log, report_steps,
                step=True, time=True, potentialEnergy=True, kineticEnergy=True,
                totalEnergy=True, temperature=True, speed=True,
            ),
        ]
        log(f"Production: {PROD_PS} ps ({prod_steps} steps) on {platform_name}")
        t0 = time.time()
        steps_done, last_check = 0, 0
        while steps_done < prod_steps:
            chunk = min(NAN_CHECK_INTERVAL_STEPS, prod_steps - steps_done)
            simulation.step(chunk)
            steps_done += chunk
            if steps_done - last_check >= NAN_CHECK_INTERVAL_STEPS:
                check_nan(simulation, f"prod {steps_done * DT_FS / 1000:.1f}ps")
                last_check = steps_done
        t_prod = time.time() - t0
        prod_ns_day = (PROD_PS / 1000.0) / (t_prod / 86400.0) if t_prod > 0 else 0.0
        log(f"  prod: {t_prod:.1f}s ({prod_ns_day:.3f} ns/day)")
        results["production"] = {
            "wall_time_s": t_prod,
            "ns_per_day": prod_ns_day,
            "ps": PROD_PS,
        }
        # Baseline from Sub 1.1 §10 (WW OpenCL empirical) = 0.184 ns/day
        opencl_baseline = 0.184
        results["vs_opencl_baseline"] = {
            "opencl_ns_per_day": opencl_baseline,
            "measured_ns_per_day": prod_ns_day,
            "speedup_factor": prod_ns_day / opencl_baseline if opencl_baseline > 0 else None,
        }
        log(f"Speedup vs OpenCL: {prod_ns_day / opencl_baseline:.2f}× "
            f"({prod_ns_day:.3f} / {opencl_baseline:.3f})")

        results["verdict"] = "PASS"
        results["verdict_reason"] = f"{platform_name} hybrid stable at {prod_ns_day:.3f} ns/day"
        results["completed"] = datetime.now(timezone.utc).isoformat()
        with open(results_path, 'w') as fh:
            json.dump(results, fh, indent=2, default=str)
        return 0

    except Exception as e:
        log(f"FATAL: {e}")
        log(traceback.format_exc())
        results["fatal_exception"] = {"error": str(e), "traceback": traceback.format_exc()}
        results["verdict"] = "FAIL"
        results["completed"] = datetime.now(timezone.utc).isoformat()
        with open(results_path, 'w') as fh:
            json.dump(results, fh, indent=2, default=str)
        return 1


if __name__ == "__main__":
    sys.exit(main())
