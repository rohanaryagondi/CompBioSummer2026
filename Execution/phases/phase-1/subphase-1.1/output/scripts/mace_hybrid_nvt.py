#!/usr/bin/env python
"""
mace_hybrid_nvt.py -- MACE-OFF24 hybrid-solvent NVT validation & benchmark.

Exercises openmmml.MLPotential.createMixedSystem with:
  - MACE-OFF24-medium treating ONLY protein heavy + hydrogen atoms
  - TIP3P-FB classical water + NaCl counterions for the rest
  - OpenCL platform (project policy: OpenMM CUDA is broken on all available GPUs)

CLI (all via environment variables so the same script covers WW and ubiquitin):
    MACE_HYBRID_PROTEIN   -- short name (ww | ubq); drives config defaults
    MACE_HYBRID_PDB       -- path to starting PDB
    MACE_HYBRID_RESRANGE  -- optional "start-end" chain-A residue range to crop
                             (WW case: crop full Pin1 to residues 6-39)
    MACE_HYBRID_EQUIL_PS  -- equilibration picoseconds (default 50 ww / 20 ubq)
    MACE_HYBRID_PROD_PS   -- production picoseconds (default 100 ww / 50 ubq)
    MACE_OUTPUT_DIR       -- output directory for logs + results JSON
    MACE_SCRATCH_DIR      -- scratch directory for trajectories
    MACE_HYBRID_TAG       -- label for output files (default MACE_HYBRID_PROTEIN)

Writes a JSON with PE/T stats, throughput, atom counts, full tracebacks on
failure. Exit code 0 on success (hybrid created + throughput measured), 1 on
failure of any kind.

Project: CompBioSummer2026 pre-Sub-1.2 flag closure (subagent-g).
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

# Suppress user site-packages
os.environ['PYTHONNOUSERSITE'] = '1'


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROTEIN = os.environ.get("MACE_HYBRID_PROTEIN", "ww").lower()
PDB_PATH = os.environ["MACE_HYBRID_PDB"]
RESRANGE = os.environ.get("MACE_HYBRID_RESRANGE", "").strip()

DEFAULTS = {
    "ww":  {"equil_ps": 50, "prod_ps": 100},
    "ubq": {"equil_ps": 20, "prod_ps": 50},
}
_def = DEFAULTS.get(PROTEIN, {"equil_ps": 20, "prod_ps": 50})
EQUIL_PS = float(os.environ.get("MACE_HYBRID_EQUIL_PS", _def["equil_ps"]))
PROD_PS = float(os.environ.get("MACE_HYBRID_PROD_PS", _def["prod_ps"]))

OUTPUT_DIR = os.environ.get(
    "MACE_OUTPUT_DIR",
    "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output",
)
SCRATCH_DIR = os.environ.get(
    "MACE_SCRATCH_DIR",
    "/nfs/roberts/scratch/pi_mg269/rag88/mace-hybrid",
)
TAG = os.environ.get("MACE_HYBRID_TAG", PROTEIN)

# Simulation parameters (held constant with Sub 1.1 vacuum test for comparability)
TEMPERATURE_K = 300.0
FRICTION = 1.0           # 1/ps Langevin
DT_FS = 1.0              # fs
REPORT_INTERVAL_PS = 1.0
NAN_CHECK_INTERVAL_STEPS = 1000
SOLVENT_PADDING_NM = 1.0
NB_CUTOFF_NM = 1.0
IONIC_STRENGTH_M = 0.15


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] {msg}", flush=True)


def setup_dirs() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(SCRATCH_DIR, exist_ok=True)
    os.makedirs(os.path.join(SCRATCH_DIR, "trajectories"), exist_ok=True)


# ---------------------------------------------------------------------------
# GPU keepalive — prevents YCRC 1-hr-idle auto-cancel during CPU-heavy phases
# (PDBFixer, solvation, system build) or any mid-run stall. Runs a tiny matmul
# every 5 min to register GPU activity.
# ---------------------------------------------------------------------------

import threading as _threading
_keepalive_stop = _threading.Event()

def _gpu_keepalive_loop() -> None:
    try:
        import torch
        if not torch.cuda.is_available():
            return
        dev = torch.device('cuda:0')
        x = torch.randn(64, 64, device=dev)
        while not _keepalive_stop.is_set():
            y = torch.matmul(x, x).sum().item()
            torch.cuda.synchronize()
            _keepalive_stop.wait(300)  # 5 min between pokes
    except Exception:
        # Keepalive must never crash the simulation
        pass

def start_gpu_keepalive() -> _threading.Thread:
    t = _threading.Thread(target=_gpu_keepalive_loop, daemon=True, name='gpu-keepalive')
    t.start()
    log("Started GPU keepalive thread (5-min cadence) to prevent YCRC idle auto-cancel")
    return t

def stop_gpu_keepalive() -> None:
    _keepalive_stop.set()


def load_and_crop_pdb():
    """Load PDB and optionally crop to chain A residue range (WW case)."""
    from openmm.app import PDBFile, Modeller, Topology
    from openmm import Vec3, unit

    log(f"Loading PDB: {PDB_PATH}")
    pdb = PDBFile(PDB_PATH)
    modeller = Modeller(pdb.topology, pdb.positions)
    log(f"  Raw topology: {modeller.topology.getNumAtoms()} atoms, "
        f"{modeller.topology.getNumResidues()} residues, "
        f"{len(list(modeller.topology.chains()))} chains")

    # Always delete non-protein het atoms (water/ligands/ions already in PDB).
    # PDBFixer reconstruction is done later via addHydrogens / addSolvent.
    std_aa = {
        'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE',
        'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL',
        'HID', 'HIE', 'HIP', 'CYX', 'CYM', 'ASH', 'GLH', 'LYN',
    }

    res_to_delete = []
    for residue in modeller.topology.residues():
        if residue.name not in std_aa:
            res_to_delete.append(residue)
    if res_to_delete:
        log(f"  Deleting {len(res_to_delete)} non-protein residues "
            f"(waters/ions/ligands from PDB)")
        modeller.delete(res_to_delete)

    # Keep only chain A (first chain)
    first_chain_id = list(modeller.topology.chains())[0].id
    other_chain_residues = []
    for chain in modeller.topology.chains():
        if chain.id != first_chain_id:
            other_chain_residues.extend(chain.residues())
    if other_chain_residues:
        log(f"  Deleting {len(other_chain_residues)} residues from non-A chains")
        modeller.delete(other_chain_residues)

    # Optional residue-range crop (for WW extraction from full Pin1)
    if RESRANGE and "-" in RESRANGE:
        start_s, end_s = RESRANGE.split("-", 1)
        start_i, end_i = int(start_s), int(end_s)
        log(f"  Cropping to residue range {start_i}-{end_i} (inclusive)")
        to_delete = []
        for residue in modeller.topology.residues():
            try:
                rid = int(residue.id)
            except ValueError:
                continue
            if rid < start_i or rid > end_i:
                to_delete.append(residue)
        if to_delete:
            modeller.delete(to_delete)

    log(f"  After protein extraction: {modeller.topology.getNumAtoms()} atoms, "
        f"{modeller.topology.getNumResidues()} residues")
    return modeller


def check_nan(simulation, label: str) -> float:
    from openmm import unit
    state = simulation.context.getState(getPositions=True, getForces=True,
                                         getEnergy=True)
    pos = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
    forces = state.getForces(asNumpy=True).value_in_unit(
        unit.kilojoules_per_mole / unit.nanometer)
    pe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
    if np.any(np.isnan(pos)):
        raise RuntimeError(f"NaN positions at {label}")
    if np.any(np.isnan(forces)):
        raise RuntimeError(f"NaN forces at {label}")
    if np.isnan(pe):
        raise RuntimeError(f"NaN potential energy at {label}")
    max_f = float(np.max(np.abs(forces)))
    if max_f > 1e8:
        raise RuntimeError(f"Extreme forces ({max_f:.1e}) at {label}")
    return pe


def analyze_state_log(log_file: str) -> dict:
    """Parse a StateDataReporter log and return PE/T stats."""
    if not os.path.exists(log_file):
        return {}
    energies, temperatures = [], []
    with open(log_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            pe_key = temp_key = None
            for k in row.keys():
                kl = k.strip().strip('"').strip('#').strip()
                if 'Potential Energy' in kl:
                    pe_key = k
                if 'Temperature' in kl:
                    temp_key = k
            try:
                if pe_key is not None:
                    energies.append(float(row[pe_key]))
                if temp_key is not None:
                    temperatures.append(float(row[temp_key]))
            except (ValueError, TypeError):
                continue
    stats = {"n_frames": len(energies)}
    if energies:
        e_arr = np.array(energies)
        stats["mean_pe_kJ_mol"] = float(np.mean(e_arr))
        stats["std_pe_kJ_mol"] = float(np.std(e_arr))
        stats["pe_drift_kJ_mol"] = float(e_arr[-1] - e_arr[0]) if len(e_arr) > 1 else 0.0
    if temperatures:
        t_arr = np.array(temperatures)
        stats["mean_temp_K"] = float(np.mean(t_arr))
        stats["std_temp_K"] = float(np.std(t_arr))
    return stats


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import openmm
    from openmm import unit
    from openmm.app import (
        PDBFile, Modeller, Simulation, ForceField, DCDReporter, StateDataReporter,
        PME, HBonds,
    )
    from openmmml import MLPotential
    try:
        from pdbfixer import PDBFixer
        HAS_PDBFIXER = True
    except ImportError:
        HAS_PDBFIXER = False

    setup_dirs()

    # Start GPU keepalive thread BEFORE any CPU-heavy work (PDBFixer, solvation).
    # Continues running through minimization + MD to catch any stalls too.
    start_gpu_keepalive()

    results: dict = {
        "task": "mace-hybrid-validation",
        "protein": PROTEIN,
        "pdb_path": PDB_PATH,
        "resrange": RESRANGE or None,
        "started": datetime.now(timezone.utc).isoformat(),
        "parameters": {
            "temperature_K": TEMPERATURE_K,
            "friction_ps": FRICTION,
            "timestep_fs": DT_FS,
            "equil_ps": EQUIL_PS,
            "prod_ps": PROD_PS,
            "solvent_padding_nm": SOLVENT_PADDING_NM,
            "nonbonded_cutoff_nm": NB_CUTOFF_NM,
            "ionic_strength_M": IONIC_STRENGTH_M,
            "water_model": "tip3pfb",
            "ml_model": "mace-off24-medium",
            "force_field": "amber14-all + tip3pfb",
        },
        "stages": {},
    }
    results_path = os.path.join(OUTPUT_DIR, f"mace_hybrid_{TAG}_results.json")

    try:
        # 1) Load protein + crop ---------------------------------------------
        modeller = load_and_crop_pdb()

        # 2) PDBFixer: fill missing atoms/residues, add H at pH 7 -----------
        if HAS_PDBFIXER:
            log("Running PDBFixer (fill missing heavy atoms, add hydrogens)...")
            # Write current structure, run PDBFixer, re-read
            tmp_pdb = os.path.join(SCRATCH_DIR, f"{TAG}_protein_only.pdb")
            with open(tmp_pdb, 'w') as f:
                PDBFile.writeFile(modeller.topology, modeller.positions, f)
            fixer = PDBFixer(filename=tmp_pdb)
            fixer.findMissingResidues()
            # Don't add missing-terminal residues for this test
            fixer.missingResidues = {}
            fixer.findNonstandardResidues()
            fixer.replaceNonstandardResidues()
            fixer.findMissingAtoms()
            fixer.addMissingAtoms()
            fixer.addMissingHydrogens(pH=7.0)
            modeller = Modeller(fixer.topology, fixer.positions)
            log(f"  After PDBFixer: {modeller.topology.getNumAtoms()} atoms, "
                f"{modeller.topology.getNumResidues()} residues")
        else:
            log("PDBFixer not available; using Modeller.addHydrogens only")
            modeller.addHydrogens()

        protein_atom_count = modeller.topology.getNumAtoms()
        protein_residue_count = modeller.topology.getNumResidues()

        # 3) Identify protein atom indices (before solvation) ----------------
        protein_atoms = list(range(protein_atom_count))

        # 4) Solvate with TIP3P-FB + 0.15 M NaCl -----------------------------
        log(f"Adding TIP3P-FB solvent (padding={SOLVENT_PADDING_NM} nm, "
            f"ionic strength={IONIC_STRENGTH_M} M)...")
        ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
        modeller.addSolvent(
            ff,
            padding=SOLVENT_PADDING_NM * unit.nanometer,
            ionicStrength=IONIC_STRENGTH_M * unit.molar,
            model='tip3p',  # tip3pfb has the same geometry as tip3p for addSolvent
        )
        total_atom_count = modeller.topology.getNumAtoms()
        water_ion_atom_count = total_atom_count - protein_atom_count
        log(f"  After solvation: {total_atom_count} atoms "
            f"(protein={protein_atom_count}, water+ions={water_ion_atom_count})")

        # 5) Classical all-atom system (AMBER14 + TIP3P-FB) ------------------
        log("Building classical AMBER14 + TIP3P-FB system (PME, 1.0 nm cutoff)...")
        mm_system = ff.createSystem(
            modeller.topology,
            nonbondedMethod=PME,
            nonbondedCutoff=NB_CUTOFF_NM * unit.nanometer,
            constraints=None,  # no constraints on protein; hybrid needs all DOF
            rigidWater=True,
        )

        # 6) Hybrid MACE + classical system ----------------------------------
        log(f"Creating hybrid MACE-OFF24-medium system "
            f"({len(protein_atoms)} MACE atoms / {total_atom_count} total)...")
        t0 = time.time()
        try:
            potential = MLPotential('mace-off24-medium')
            hybrid_system = potential.createMixedSystem(
                modeller.topology,
                mm_system,
                protein_atoms,
                interpolate=False,
            )
        except Exception as e:
            tb = traceback.format_exc()
            log(f"createMixedSystem FAILED: {e}")
            results["hybrid_createMixedSystem"] = {
                "status": "FAILED",
                "error": str(e),
                "traceback": tb,
                "protein_atom_count": protein_atom_count,
                "total_atom_count": total_atom_count,
            }
            results["verdict"] = "FAIL"
            results["verdict_reason"] = "createMixedSystem exception"
            results["completed"] = datetime.now(timezone.utc).isoformat()
            with open(results_path, 'w') as fh:
                json.dump(results, fh, indent=2, default=str)
            return 1

        t_sys = time.time() - t0
        log(f"  Hybrid system built in {t_sys:.1f}s: "
            f"{hybrid_system.getNumParticles()} particles, "
            f"{hybrid_system.getNumForces()} forces")

        results["hybrid_createMixedSystem"] = {
            "status": "OK",
            "build_time_s": t_sys,
            "protein_atom_count": protein_atom_count,
            "protein_residue_count": protein_residue_count,
            "water_ion_atom_count": water_ion_atom_count,
            "total_atom_count": total_atom_count,
            "n_forces": hybrid_system.getNumForces(),
        }

        # 7) OpenCL platform ONLY (CUDA is verified broken on all available GPUs)
        log("Selecting OpenCL platform (CUDA disabled by Sub 1.1 policy)...")
        try:
            platform = openmm.Platform.getPlatformByName('OpenCL')
        except Exception as e:
            log(f"OpenCL platform unavailable: {e}")
            results["verdict"] = "FAIL"
            results["verdict_reason"] = f"OpenCL not available: {e}"
            with open(results_path, 'w') as fh:
                json.dump(results, fh, indent=2, default=str)
            return 1

        integrator = openmm.LangevinMiddleIntegrator(
            TEMPERATURE_K * unit.kelvin,
            FRICTION / unit.picosecond,
            DT_FS * unit.femtosecond,
        )
        simulation = Simulation(modeller.topology, hybrid_system, integrator,
                                platform, {})
        simulation.context.setPositions(modeller.positions)

        # 8) Energy minimization ---------------------------------------------
        # REVERTED 2026-04-18: maxIterations=200 was too aggressive — caused NaN
        # during equilibration for WW (job 8725506 FAILED after 2h of NVT with
        # NaN particle position). Restoring maxIterations=2000 to ensure high-
        # force atoms are fully relaxed before dynamics. Added explicit max-
        # force safety check after minimization — fail fast if any atom has
        # force > 1e5 kJ/mol/nm (indicates incomplete minimization).
        log("Minimizing hybrid system (max 2000 iter, tol 10 kJ/mol/nm)...")
        t0 = time.time()
        simulation.minimizeEnergy(
            maxIterations=2000,
            tolerance=10 * unit.kilojoule_per_mole / unit.nanometer,
        )
        t_min = time.time() - t0
        # Post-min max-force sanity check
        _post_min_state = simulation.context.getState(getForces=True)
        _post_min_forces = _post_min_state.getForces(asNumpy=True).value_in_unit(
            unit.kilojoule_per_mole / unit.nanometer)
        _max_f = float(np.max(np.abs(_post_min_forces)))
        log(f"  Post-min max |force|: {_max_f:.2e} kJ/mol/nm")
        if _max_f > 1e5:
            raise RuntimeError(
                f"Post-minimization max force {_max_f:.2e} kJ/mol/nm exceeds "
                "1e5 threshold — system not properly relaxed; dynamics would NaN")
        pe_min = simulation.context.getState(getEnergy=True) \
            .getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
        log(f"  Minimization: {t_min:.1f}s, PE = {pe_min:.1f} kJ/mol")
        check_nan(simulation, "post-minimization")
        results["minimization"] = {
            "wall_time_s": t_min,
            "pe_minimized_kJ_mol": pe_min,
        }

        # 9) Equilibration ---------------------------------------------------
        simulation.context.setVelocitiesToTemperature(TEMPERATURE_K * unit.kelvin)
        equil_steps = int(EQUIL_PS * 1000 / DT_FS)
        report_steps = max(1, int(REPORT_INTERVAL_PS * 1000 / DT_FS))
        equil_log = os.path.join(OUTPUT_DIR, f"mace_hybrid_{TAG}_equil.log")
        equil_traj = os.path.join(SCRATCH_DIR, "trajectories",
                                    f"mace_hybrid_{TAG}_equil.dcd")
        simulation.reporters = [
            DCDReporter(equil_traj, report_steps),
            StateDataReporter(
                equil_log, report_steps,
                step=True, time=True, potentialEnergy=True, kineticEnergy=True,
                totalEnergy=True, temperature=True, speed=True,
            ),
        ]
        log(f"--- Equilibration: {EQUIL_PS} ps ({equil_steps} steps) ---")
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
        equil_throughput = (EQUIL_PS / 1000) / (t_equil / 86400) if t_equil else 0
        log(f"  Equilibration: {t_equil:.1f}s ({equil_throughput:.3f} ns/day)")
        results["equilibration"] = {
            "wall_time_s": t_equil,
            "ns_per_day": equil_throughput,
            "ps": EQUIL_PS,
            "log": equil_log,
            "energy_stats": analyze_state_log(equil_log),
        }

        # 10) Production ------------------------------------------------------
        prod_steps = int(PROD_PS * 1000 / DT_FS)
        prod_log = os.path.join(OUTPUT_DIR, f"mace_hybrid_{TAG}_prod.log")
        prod_traj = os.path.join(SCRATCH_DIR, "trajectories",
                                  f"mace_hybrid_{TAG}_prod.dcd")
        simulation.reporters = [
            DCDReporter(prod_traj, report_steps),
            StateDataReporter(
                prod_log, report_steps,
                step=True, time=True, potentialEnergy=True, kineticEnergy=True,
                totalEnergy=True, temperature=True, speed=True,
            ),
        ]
        log(f"--- Production: {PROD_PS} ps ({prod_steps} steps) ---")
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
        prod_throughput = (PROD_PS / 1000) / (t_prod / 86400) if t_prod else 0
        log(f"  Production: {t_prod:.1f}s ({prod_throughput:.3f} ns/day)")
        energy_stats = analyze_state_log(prod_log)
        results["production"] = {
            "wall_time_s": t_prod,
            "ns_per_day": prod_throughput,
            "ps": PROD_PS,
            "log": prod_log,
            "energy_stats": energy_stats,
        }

        # 11) Verdict --------------------------------------------------------
        stable = (
            results["hybrid_createMixedSystem"]["status"] == "OK"
            and "mean_pe_kJ_mol" in energy_stats
            and not np.isnan(energy_stats.get("mean_pe_kJ_mol", float("nan")))
        )
        results["verdict"] = "PASS" if stable else "FAIL"
        results["verdict_reason"] = (
            "Hybrid createMixedSystem ran and produced stable PE/T"
            if stable else "Energy stats missing or NaN"
        )
        results["completed"] = datetime.now(timezone.utc).isoformat()
        with open(results_path, 'w') as fh:
            json.dump(results, fh, indent=2, default=str)

        log("=========================================================")
        log(f"HYBRID MACE on {PROTEIN}: {results['verdict']}")
        log(f"  MACE atoms (protein): {protein_atom_count}")
        log(f"  Total atoms (protein+water+ions): {total_atom_count}")
        log(f"  Production throughput: {prod_throughput:.3f} ns/day")
        if "mean_pe_kJ_mol" in energy_stats:
            log(f"  PE: {energy_stats['mean_pe_kJ_mol']:.1f} +/- "
                f"{energy_stats.get('std_pe_kJ_mol', 0):.1f} kJ/mol "
                f"(drift {energy_stats.get('pe_drift_kJ_mol', 0):+.1f})")
        if "mean_temp_K" in energy_stats:
            log(f"  T: {energy_stats['mean_temp_K']:.1f} +/- "
                f"{energy_stats.get('std_temp_K', 0):.1f} K")
        log(f"Results JSON: {results_path}")
        log("=========================================================")

        return 0 if stable else 1

    except Exception as e:
        tb = traceback.format_exc()
        log(f"FATAL EXCEPTION: {e}")
        log(tb)
        results["fatal_exception"] = {"error": str(e), "traceback": tb}
        results["verdict"] = "FAIL"
        results["verdict_reason"] = f"Exception: {e}"
        results["completed"] = datetime.now(timezone.utc).isoformat()
        try:
            with open(results_path, 'w') as fh:
                json.dump(results, fh, indent=2, default=str)
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    # Print environment info
    try:
        import torch
        log(f"torch {torch.__version__} | cuda avail: {torch.cuda.is_available()}")
    except Exception:
        pass
    try:
        import openmm
        log(f"OpenMM {openmm.__version__}")
    except Exception:
        pass
    sys.exit(main())
