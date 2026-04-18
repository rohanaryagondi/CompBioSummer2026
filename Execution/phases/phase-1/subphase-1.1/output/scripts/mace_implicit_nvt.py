#!/usr/bin/env python
"""
mace_implicit_nvt.py -- MACE-OFF24 hybrid-mode NVT with IMPLICIT SOLVENT.

Variant of mace_hybrid_nvt.py that replaces the explicit TIP3P-FB water shell
with a classical continuum dielectric (GBn2 or OBC2 Generalized Born model).
Eliminates ~7-15K explicit water atoms per system, yielding a 10-14x expected
speedup on OpenCL relative to the hybrid explicit-water benchmark measured
2026-04-18.

Purpose: Option 4 feasibility pilot for the Phase 2 MACE scope decision (see
shared/help-needed/sub-1.2-phase2-mlff-scope.md).

Key differences vs mace_hybrid_nvt.py:
  - ForceField uses 'amber14-all.xml' + 'implicit/gbn2.xml' (or 'implicit/obc2.xml')
  - NO addSolvent (no explicit water, no ion shell)
  - nonbondedMethod = NoCutoff (continuum dielectric is handled by CustomGBForce)
  - No periodic box: the system is aperiodic
  - Smaller system = smaller memory, much faster minimization + dynamics

CLI (env var driven):
    MACE_IMPL_PROTEIN   -- short name (ww | gb3 | etc.)
    MACE_IMPL_PDB       -- path to starting PDB
    MACE_IMPL_RESRANGE  -- optional "start-end" chain-A residue range to crop
    MACE_IMPL_MODEL     -- implicit solvent model (gbn2 | obc2; default gbn2)
    MACE_IMPL_EQUIL_PS  -- equilibration picoseconds (default 30)
    MACE_IMPL_PROD_PS   -- production picoseconds (default 60)
    MACE_OUTPUT_DIR     -- output directory for logs + results JSON
    MACE_SCRATCH_DIR    -- scratch directory for trajectories
    MACE_IMPL_TAG       -- label for output files (default MACE_IMPL_PROTEIN)

Exit code 0 on success (hybrid built + throughput measured), 1 on failure.
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

# Suppress user site-packages so we get env-mace's OpenMM 8.5.1 (not the
# ~/.local OpenMM 8.3.1, which lacks openmm.PythonForce and therefore
# cannot run openmmml hybrid systems).
os.environ['PYTHONNOUSERSITE'] = '1'


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROTEIN = os.environ.get("MACE_IMPL_PROTEIN", "ww").lower()
PDB_PATH = os.environ["MACE_IMPL_PDB"]
RESRANGE = os.environ.get("MACE_IMPL_RESRANGE", "").strip()
IMPL_MODEL = os.environ.get("MACE_IMPL_MODEL", "gbn2").lower()

# Map of implicit-solvent XML files shipped with OpenMM (verified present in
# env-mace's OpenMM 8.5.1 installation).
IMPL_XML_MAP = {
    "gbn2": "implicit/gbn2.xml",
    "obc2": "implicit/obc2.xml",
    "obc1": "implicit/obc1.xml",
    "gbn":  "implicit/gbn.xml",
}
if IMPL_MODEL not in IMPL_XML_MAP:
    raise SystemExit(
        f"Unknown implicit solvent model '{IMPL_MODEL}'. "
        f"Valid choices: {list(IMPL_XML_MAP.keys())}"
    )
IMPL_XML = IMPL_XML_MAP[IMPL_MODEL]

DEFAULTS = {
    "ww":  {"equil_ps": 30, "prod_ps": 60},
    "gb3": {"equil_ps": 30, "prod_ps": 60},
    "ubq": {"equil_ps": 30, "prod_ps": 60},
}
_def = DEFAULTS.get(PROTEIN, {"equil_ps": 30, "prod_ps": 60})
EQUIL_PS = float(os.environ.get("MACE_IMPL_EQUIL_PS", _def["equil_ps"]))
PROD_PS = float(os.environ.get("MACE_IMPL_PROD_PS", _def["prod_ps"]))

OUTPUT_DIR = os.environ.get(
    "MACE_OUTPUT_DIR",
    "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output",
)
SCRATCH_DIR = os.environ.get(
    "MACE_SCRATCH_DIR",
    "/nfs/roberts/scratch/pi_mg269/rag88/mace-implicit",
)
TAG = os.environ.get("MACE_IMPL_TAG", PROTEIN)

# Simulation parameters (parallel to mace_hybrid_nvt.py for comparability)
TEMPERATURE_K = 300.0
FRICTION = 1.0           # 1/ps Langevin
DT_FS = 1.0              # fs
REPORT_INTERVAL_PS = 1.0
NAN_CHECK_INTERVAL_STEPS = 1000


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


def load_and_crop_pdb():
    """Load PDB and optionally crop to chain A residue range."""
    from openmm.app import PDBFile, Modeller
    from openmm import Vec3, unit

    log(f"Loading PDB: {PDB_PATH}")
    pdb = PDBFile(PDB_PATH)
    modeller = Modeller(pdb.topology, pdb.positions)
    log(f"  Raw topology: {modeller.topology.getNumAtoms()} atoms, "
        f"{modeller.topology.getNumResidues()} residues, "
        f"{len(list(modeller.topology.chains()))} chains")

    std_aa = {
        'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE',
        'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL',
        'HID', 'HIE', 'HIP', 'CYX', 'CYM', 'ASH', 'GLH', 'LYN',
    }
    res_to_delete = [r for r in modeller.topology.residues() if r.name not in std_aa]
    if res_to_delete:
        log(f"  Deleting {len(res_to_delete)} non-protein residues")
        modeller.delete(res_to_delete)

    first_chain_id = list(modeller.topology.chains())[0].id
    other_chain_residues = []
    for chain in modeller.topology.chains():
        if chain.id != first_chain_id:
            other_chain_residues.extend(chain.residues())
    if other_chain_residues:
        log(f"  Deleting {len(other_chain_residues)} residues from non-A chains")
        modeller.delete(other_chain_residues)

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
        NoCutoff, HBonds,
    )
    from openmmml import MLPotential
    try:
        from pdbfixer import PDBFixer
        HAS_PDBFIXER = True
    except ImportError:
        HAS_PDBFIXER = False

    setup_dirs()

    results: dict = {
        "task": "mace-implicit-pilot",
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
            "implicit_model": IMPL_MODEL,
            "implicit_xml": IMPL_XML,
            "nonbonded_method": "NoCutoff",
            "ml_model": "mace-off24-medium",
            "force_field": f"amber14-all + {IMPL_XML}",
        },
        "stages": {},
    }
    results_path = os.path.join(OUTPUT_DIR, f"mace_impl_{TAG}_results.json")

    try:
        # 1) Load + crop protein PDB -----------------------------------------
        modeller = load_and_crop_pdb()

        # 2) PDBFixer: fill missing atoms, add H at pH 7 --------------------
        if HAS_PDBFIXER:
            log("Running PDBFixer (fill missing heavy atoms, add hydrogens)...")
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
            log(f"  After PDBFixer: {modeller.topology.getNumAtoms()} atoms, "
                f"{modeller.topology.getNumResidues()} residues")
        else:
            log("PDBFixer not available; using Modeller.addHydrogens only")
            modeller.addHydrogens()

        protein_atom_count = modeller.topology.getNumAtoms()
        protein_residue_count = modeller.topology.getNumResidues()
        total_atom_count = protein_atom_count  # no water -> total == protein
        protein_atoms = list(range(protein_atom_count))

        # 3) Classical AMBER14 + implicit solvent system --------------------
        log(f"Building classical AMBER14 + {IMPL_MODEL.upper()} implicit system "
            f"(NoCutoff)...")
        ff = ForceField('amber14-all.xml', IMPL_XML)
        mm_system = ff.createSystem(
            modeller.topology,
            nonbondedMethod=NoCutoff,
            constraints=None,  # no constraints -> hybrid needs all DOF
            rigidWater=False,   # no water
        )
        log(f"  Classical system: {mm_system.getNumParticles()} particles, "
            f"{mm_system.getNumForces()} forces")

        # 4) Hybrid MACE + classical implicit-solvent system ----------------
        log(f"Creating hybrid MACE-OFF24-medium system "
            f"({len(protein_atoms)} MACE atoms / {total_atom_count} total atoms)...")
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
            "water_ion_atom_count": 0,
            "total_atom_count": total_atom_count,
            "n_forces": hybrid_system.getNumForces(),
        }

        # 5) OpenCL platform --------------------------------------------------
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

        # 6) Energy minimization ---------------------------------------------
        log("Minimizing hybrid system (max 2000 iter, tol 10 kJ/mol/nm)...")
        t0 = time.time()
        simulation.minimizeEnergy(
            maxIterations=2000,
            tolerance=10 * unit.kilojoule_per_mole / unit.nanometer,
        )
        t_min = time.time() - t0
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
            "post_min_max_force_kJ_mol_nm": _max_f,
        }

        # 7) Equilibration ---------------------------------------------------
        simulation.context.setVelocitiesToTemperature(TEMPERATURE_K * unit.kelvin)
        equil_steps = int(EQUIL_PS * 1000 / DT_FS)
        report_steps = max(1, int(REPORT_INTERVAL_PS * 1000 / DT_FS))
        equil_log = os.path.join(OUTPUT_DIR, f"mace_impl_{TAG}_equil.log")
        equil_traj = os.path.join(SCRATCH_DIR, "trajectories",
                                    f"mace_impl_{TAG}_equil.dcd")
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

        # 8) Production ------------------------------------------------------
        prod_steps = int(PROD_PS * 1000 / DT_FS)
        prod_log = os.path.join(OUTPUT_DIR, f"mace_impl_{TAG}_prod.log")
        prod_traj = os.path.join(SCRATCH_DIR, "trajectories",
                                  f"mace_impl_{TAG}_prod.dcd")
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

        # 9) Verdict --------------------------------------------------------
        stable = (
            results["hybrid_createMixedSystem"]["status"] == "OK"
            and "mean_pe_kJ_mol" in energy_stats
            and not np.isnan(energy_stats.get("mean_pe_kJ_mol", float("nan")))
        )
        results["verdict"] = "PASS" if stable else "FAIL"
        results["verdict_reason"] = (
            "Implicit-solvent hybrid ran and produced stable PE/T"
            if stable else "Energy stats missing or NaN"
        )
        results["completed"] = datetime.now(timezone.utc).isoformat()
        with open(results_path, 'w') as fh:
            json.dump(results, fh, indent=2, default=str)

        log("=========================================================")
        log(f"IMPLICIT MACE on {PROTEIN} ({IMPL_MODEL.upper()}): {results['verdict']}")
        log(f"  Protein atoms (MACE-handled): {protein_atom_count}")
        log(f"  Total atoms (no water in implicit): {total_atom_count}")
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
