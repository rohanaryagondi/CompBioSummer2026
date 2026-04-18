#!/usr/bin/env python
"""
mace_cuda_bench.py -- MACE-OFF24 CUDA benchmark harness for env-mace-cuda.

Applies Fix A+B (the combination Subagent L validated as the minimal working
fix for the PyTorch<->OpenMM CUDA-context interop bug that Subagent J hit):

  Fix A. CUDA_VISIBLE_DEVICES=0 + torch.cuda.set_device(0) + pass device='cuda:0'
         to MLPotential.createSystem/createMixedSystem + OpenMM CUDA properties
         DeviceIndex='0', Precision='mixed'.

  Fix B. Runtime monkey-patch openmmml.models.macepotential._computeMACE to
         wrap torch.cuda.synchronize() before AND after the MACE forward pass.
         This prevents OpenMM's subsequent getState() from seeing an invalidated
         CUDA stream handle set up on PyTorch's context.

Modes:
  BENCH_MODE=vacuum   -> crambin, pure MACE (MLPotential.createSystem), 10 ps
  BENCH_MODE=hybrid   -> WW hybrid MACE + TIP3P-FB water, 2 ps (short; just
                         enough for a throughput number within a 2h wall)

The script records OpenMM platform used, ns/day for equilibration+production,
max force, PE drift, and NaN status.
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

os.environ.setdefault('PYTHONNOUSERSITE', '1')
os.environ.setdefault('CUDA_VISIBLE_DEVICES', '0')  # Fix A part 1

import numpy as np


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BENCH_MODE = os.environ.get('BENCH_MODE', 'vacuum').lower()
OUTPUT_DIR = os.environ.get(
    "BENCH_OUTPUT_DIR",
    "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/optl",
)
SCRATCH_DIR = os.environ.get(
    "BENCH_SCRATCH_DIR",
    "/nfs/roberts/scratch/pi_mg269/rag88/mace-cuda-bench",
)
TAG = os.environ.get("BENCH_TAG", f"{BENCH_MODE}_cuda")

CRAMBIN_PDB = "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/crambin.pdb"
WW_PDB = "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ww.pdb"

# Hybrid defaults (keep small to avoid wall blowout while we still only have
# ~3h of Subagent L time — we want a throughput number, not a long prod run).
VACUUM_PROD_PS = float(os.environ.get('BENCH_VACUUM_PS', '10'))
HYBRID_EQUIL_PS = float(os.environ.get('BENCH_HYBRID_EQUIL_PS', '2'))
HYBRID_PROD_PS = float(os.environ.get('BENCH_HYBRID_PROD_PS', '5'))

TEMP_K = 300.0
FRICTION = 1.0
DT_FS = 1.0
REPORT_INTERVAL_PS = 1.0

RESULTS_PATH = os.path.join(OUTPUT_DIR, f"mace_cuda_bench_{TAG}.json")


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] {msg}", flush=True)


def apply_cuda_interop_fix() -> None:
    """Fix A (device pin) + Fix B (monkey-patch synchronize)."""
    import torch
    if torch.cuda.is_available():
        torch.cuda.init()
        torch.cuda.set_device(0)
        log(f"Fix A: torch.cuda.set_device(0) -> {torch.cuda.get_device_name(0)}")

    import openmmml.models.macepotential as mp
    original = mp._computeMACE

    def _computeMACE_sync(state, **kw):
        import torch
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        energy, forces = original(state, **kw)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        return energy, forces

    mp._computeMACE = _computeMACE_sync
    log("Fix B: _computeMACE now wraps torch.cuda.synchronize()")


def make_cuda_platform():
    import openmm
    platform = openmm.Platform.getPlatformByName('CUDA')
    properties = {
        "Precision": "mixed",
        "DeviceIndex": "0",
        "DeterministicForces": "false",
    }
    return platform, properties


def setup_vacuum_system():
    """Build vacuum crambin. Force the createMixedSystem path because that
    is the only one Subagent L found survives the interop bug with Fix A+B
    on RTX 5000 Ada (see note 1.1-mace-cuda-benchmark). createSystem()
    crashes at post-min getState even for pure vacuum — a separate failure
    mode in the openmm-ml PythonForce path."""
    import openmm
    from openmm.app import PDBFile, Modeller, ForceField
    from openmmml import MLPotential

    log(f"Loading {CRAMBIN_PDB}")
    pdb = PDBFile(CRAMBIN_PDB)
    modeller = Modeller(pdb.topology, pdb.positions)
    modeller.addHydrogens()
    n_atoms = modeller.topology.getNumAtoms()
    log(f"Vacuum crambin topology: {n_atoms} atoms")

    # Build a trivial classical AMBER14 system with NoCutoff as the MM backdrop.
    ff = ForceField('amber14-all.xml')
    mm_system = ff.createSystem(
        modeller.topology,
        nonbondedMethod=openmm.app.NoCutoff,
        constraints=None,
    )

    potential = MLPotential('mace-off24-medium')
    all_atoms = list(range(n_atoms))
    t0 = time.time()
    system = potential.createMixedSystem(
        modeller.topology, mm_system, all_atoms,
        interpolate=False, device='cuda:0',
    )
    t_sys = time.time() - t0
    log(f"Hybrid (all-atoms ML) system built in {t_sys:.1f}s: "
        f"{system.getNumForces()} forces")
    return modeller, system, n_atoms, t_sys


def setup_hybrid_system():
    import openmm
    from openmm import unit
    from openmm.app import PDBFile, Modeller, ForceField, PME
    from openmmml import MLPotential
    try:
        from pdbfixer import PDBFixer
    except ImportError:
        PDBFixer = None

    log(f"Loading {WW_PDB}")
    pdb = PDBFile(WW_PDB)
    modeller = Modeller(pdb.topology, pdb.positions)

    # Strip non-protein, keep chain A residues 6-39 (WW domain per manifest).
    std_aa = {
        'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE',
        'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL',
        'HID', 'HIE', 'HIP', 'CYX', 'CYM', 'ASH', 'GLH', 'LYN',
    }
    to_delete = []
    for r in modeller.topology.residues():
        if r.name not in std_aa:
            to_delete.append(r)
    if to_delete:
        modeller.delete(to_delete)
    first_chain_id = list(modeller.topology.chains())[0].id
    other_chains = []
    for chain in modeller.topology.chains():
        if chain.id != first_chain_id:
            other_chains.extend(chain.residues())
    if other_chains:
        modeller.delete(other_chains)
    # Crop to 6-39
    to_delete = []
    for r in modeller.topology.residues():
        try:
            rid = int(r.id)
        except ValueError:
            continue
        if rid < 6 or rid > 39:
            to_delete.append(r)
    if to_delete:
        modeller.delete(to_delete)
    log(f"After WW extraction: {modeller.topology.getNumAtoms()} atoms, "
        f"{modeller.topology.getNumResidues()} residues")

    if PDBFixer is not None:
        log("Running PDBFixer...")
        tmp_pdb = os.path.join(SCRATCH_DIR, f"{TAG}_ww_only.pdb")
        os.makedirs(os.path.dirname(tmp_pdb), exist_ok=True)
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
    else:
        modeller.addHydrogens()

    protein_atom_count = modeller.topology.getNumAtoms()

    log("Adding TIP3P-FB solvent...")
    ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
    modeller.addSolvent(
        ff,
        padding=1.0 * unit.nanometer,
        ionicStrength=0.15 * unit.molar,
        model='tip3p',
    )
    total_atom_count = modeller.topology.getNumAtoms()
    log(f"After solvation: {total_atom_count} atoms "
        f"(protein={protein_atom_count}, water+ions={total_atom_count-protein_atom_count})")

    log("Building classical AMBER14+TIP3P-FB MM system...")
    mm_system = ff.createSystem(
        modeller.topology,
        nonbondedMethod=PME,
        nonbondedCutoff=1.0 * unit.nanometer,
        constraints=None,
        rigidWater=True,
    )

    log(f"Creating hybrid MACE system (protein {protein_atom_count} / total {total_atom_count})...")
    protein_atoms = list(range(protein_atom_count))
    potential = MLPotential('mace-off24-medium')
    t0 = time.time()
    hybrid_system = potential.createMixedSystem(
        modeller.topology, mm_system, protein_atoms,
        interpolate=False, device='cuda:0',
    )
    t_sys = time.time() - t0
    log(f"Hybrid system built in {t_sys:.1f}s, {hybrid_system.getNumForces()} forces")
    return modeller, hybrid_system, protein_atom_count, total_atom_count, t_sys


def run_benchmark(modeller, system, equil_ps: float, prod_ps: float,
                  tag: str) -> dict:
    import openmm
    from openmm import unit
    from openmm.app import Simulation, StateDataReporter

    platform, properties = make_cuda_platform()
    integrator = openmm.LangevinMiddleIntegrator(
        TEMP_K * unit.kelvin,
        FRICTION / unit.picosecond,
        DT_FS * unit.femtosecond,
    )
    sim = Simulation(modeller.topology, system, integrator, platform, properties)
    sim.context.setPositions(modeller.positions)

    import torch
    if torch.cuda.is_available():
        torch.cuda.synchronize()

    # Minimize
    log("Minimizing (max 2000 iter, tol 10 kJ/mol/nm)...")
    t0 = time.time()
    sim.minimizeEnergy(maxIterations=2000,
                       tolerance=10 * unit.kilojoule_per_mole / unit.nanometer)
    t_min = time.time() - t0
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    state = sim.context.getState(getEnergy=True, getForces=True)
    pe_min = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
    forces = state.getForces(asNumpy=True).value_in_unit(
        unit.kilojoule_per_mole / unit.nanometer)
    max_f = float(np.max(np.abs(forces)))
    log(f"Min: {t_min:.1f}s, PE={pe_min:.1f} kJ/mol, max|F|={max_f:.2e} kJ/mol/nm")
    if max_f > 1e5:
        raise RuntimeError(f"Post-min max force {max_f:.2e} exceeds 1e5 — aborting")

    report_steps = max(1, int(REPORT_INTERVAL_PS * 1000 / DT_FS))

    # Equilibration
    if equil_ps > 0:
        sim.context.setVelocitiesToTemperature(TEMP_K * unit.kelvin)
        equil_steps = int(equil_ps * 1000 / DT_FS)
        equil_log = os.path.join(OUTPUT_DIR, f"mace_cuda_{tag}_equil.log")
        sim.reporters = [StateDataReporter(
            equil_log, report_steps,
            step=True, time=True, potentialEnergy=True, kineticEnergy=True,
            totalEnergy=True, temperature=True, speed=True,
        )]
        log(f"Equilibration: {equil_ps} ps ({equil_steps} steps)...")
        t0 = time.time()
        sim.step(equil_steps)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t_equil = time.time() - t0
        equil_ns_day = (equil_ps / 1000) / (t_equil / 86400) if t_equil else 0
        log(f"Equil: {t_equil:.1f}s ({equil_ns_day:.3f} ns/day)")
    else:
        equil_ns_day = 0.0
        t_equil = 0.0
        equil_log = None

    # Production
    prod_steps = int(prod_ps * 1000 / DT_FS)
    prod_log = os.path.join(OUTPUT_DIR, f"mace_cuda_{tag}_prod.log")
    sim.reporters = [StateDataReporter(
        prod_log, report_steps,
        step=True, time=True, potentialEnergy=True, kineticEnergy=True,
        totalEnergy=True, temperature=True, speed=True,
    )]
    log(f"Production: {prod_ps} ps ({prod_steps} steps)...")
    t0 = time.time()
    sim.step(prod_steps)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    t_prod = time.time() - t0
    prod_ns_day = (prod_ps / 1000) / (t_prod / 86400) if t_prod else 0
    log(f"Prod: {t_prod:.1f}s ({prod_ns_day:.3f} ns/day)")

    state = sim.context.getState(getEnergy=True, getPositions=True, getForces=True)
    pe_final = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
    pos = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
    forces = state.getForces(asNumpy=True).value_in_unit(
        unit.kilojoule_per_mole / unit.nanometer)
    any_nan = bool(np.any(np.isnan(pos)) or np.any(np.isnan(forces))
                   or np.isnan(pe_final))
    max_force = float(np.max(np.abs(forces)))

    return {
        "minimize_s": t_min,
        "pe_minimized_kJ_mol": pe_min,
        "max_force_post_min": max_f,
        "equil_s": t_equil,
        "equil_ns_per_day": equil_ns_day,
        "equil_ps": equil_ps,
        "equil_log": equil_log,
        "prod_s": t_prod,
        "prod_ns_per_day": prod_ns_day,
        "prod_ps": prod_ps,
        "prod_log": prod_log,
        "pe_final_kJ_mol": pe_final,
        "max_force_final": max_force,
        "any_nan": any_nan,
    }


def main() -> int:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(SCRATCH_DIR, exist_ok=True)
    results: dict = {
        "task": "mace_cuda_bench",
        "mode": BENCH_MODE,
        "tag": TAG,
        "started": datetime.now(timezone.utc).isoformat(),
        "env": {},
    }

    try:
        apply_cuda_interop_fix()

        import openmm
        import torch
        results["env"]["openmm_version"] = openmm.__version__
        results["env"]["torch_version"] = torch.__version__
        results["env"]["cuda_device_name"] = (torch.cuda.get_device_name(0)
                                              if torch.cuda.is_available() else None)
        results["env"]["cuda_capability"] = (list(torch.cuda.get_device_capability(0))
                                             if torch.cuda.is_available() else None)

        log(f"Mode: {BENCH_MODE}")
        if BENCH_MODE == 'vacuum':
            modeller, system, n_atoms, t_sys = setup_vacuum_system()
            results["n_atoms"] = n_atoms
            results["system_build_s"] = t_sys
            run_result = run_benchmark(modeller, system,
                                       equil_ps=0, prod_ps=VACUUM_PROD_PS,
                                       tag=TAG)
            results.update(run_result)
        elif BENCH_MODE == 'hybrid':
            (modeller, hybrid_system, protein_count, total_count,
             t_sys) = setup_hybrid_system()
            results["protein_atom_count"] = protein_count
            results["total_atom_count"] = total_count
            results["system_build_s"] = t_sys
            run_result = run_benchmark(modeller, hybrid_system,
                                       equil_ps=HYBRID_EQUIL_PS,
                                       prod_ps=HYBRID_PROD_PS, tag=TAG)
            results.update(run_result)
        else:
            raise ValueError(f"Unknown BENCH_MODE={BENCH_MODE}")

        stable = (not results.get("any_nan", True)
                  and results.get("prod_ns_per_day", 0) > 0)
        results["verdict"] = "PASS" if stable else "FAIL"
        results["completed"] = datetime.now(timezone.utc).isoformat()
        with open(RESULTS_PATH, 'w') as fh:
            json.dump(results, fh, indent=2, default=str)

        log("=" * 60)
        log(f"VERDICT: {results['verdict']}  mode={BENCH_MODE}")
        log(f"Production throughput: {results.get('prod_ns_per_day', 0):.3f} ns/day")
        log(f"Results JSON: {RESULTS_PATH}")
        log("=" * 60)
        return 0 if stable else 1

    except Exception as e:
        tb = traceback.format_exc()
        log(f"FATAL: {type(e).__name__}: {e}")
        log(tb)
        results["verdict"] = "FAIL"
        results["error"] = f"{type(e).__name__}: {e}"
        results["traceback"] = tb
        results["completed"] = datetime.now(timezone.utc).isoformat()
        try:
            with open(RESULTS_PATH, 'w') as fh:
                json.dump(results, fh, indent=2, default=str)
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
