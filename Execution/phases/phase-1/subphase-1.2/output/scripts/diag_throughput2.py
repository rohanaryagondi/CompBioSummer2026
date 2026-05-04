"""
Throughput benchmark round 2: test MACE float32 precision + HMR timestep options.
"""
import os, sys, time, numpy as np
os.environ['PYTHONNOUSERSITE'] = '1'

import openmm
from openmm import unit, MonteCarloBarostat
from openmm.app import PDBFile, Modeller, Simulation, ForceField, PME, HBonds
from openmmml import MLPotential
from pdbfixer import PDBFixer
import tempfile

def log(msg):
    from datetime import datetime, timezone
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%SZ')}] {msg}", flush=True)

def build_ww():
    pdb = PDBFile("/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ww.pdb")
    modeller = Modeller(pdb.topology, pdb.positions)
    std_aa = {'ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE',
              'LEU','LYS','MET','PHE','PRO','SER','THR','TRP','TYR','VAL',
              'HID','HIE','HIP','CYX','CYM','ASH','GLH','LYN'}
    non_prot = [r for r in modeller.topology.residues() if r.name not in std_aa]
    if non_prot: modeller.delete(non_prot)
    first_chain = list(modeller.topology.chains())[0].id
    other = []
    for c in modeller.topology.chains():
        if c.id != first_chain: other.extend(c.residues())
    if other: modeller.delete(other)
    to_del = [r for r in modeller.topology.residues()
              if int(r.id) < 6 or int(r.id) > 39]
    if to_del: modeller.delete(to_del)

    with tempfile.NamedTemporaryFile(suffix='.pdb', mode='w', delete=False) as f:
        PDBFile.writeFile(modeller.topology, modeller.positions, f)
        tmp = f.name
    fixer = PDBFixer(filename=tmp)
    fixer.findMissingResidues(); fixer.missingResidues = {}
    fixer.findNonstandardResidues(); fixer.replaceNonstandardResidues()
    fixer.findMissingAtoms(); fixer.addMissingAtoms()
    fixer.addMissingHydrogens(pH=7.0)
    modeller = Modeller(fixer.topology, fixer.positions)
    os.unlink(tmp)
    return modeller

def run_benchmark(modeller, precision, dt_fs, constraints, label, n_steps=200):
    try:
        protein_atoms = list(range(534))  # WW protein atoms
        ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
        # Need fresh modeller copy for solvation (can't re-solvate)
        # Actually, topology is shared — need to rebuild each time
        # Shortcut: we'll reuse the same hybrid system but vary integrator

        mm_system = ff.createSystem(modeller.topology, nonbondedMethod=PME,
                                    nonbondedCutoff=1.0*unit.nanometer,
                                    constraints=constraints, rigidWater=True)

        potential = MLPotential('mace-off24-medium')
        kwargs = {}
        if precision:
            kwargs['precision'] = precision
        hybrid_system = potential.createMixedSystem(
            modeller.topology, mm_system, protein_atoms, interpolate=False, **kwargs)
        hybrid_system.addForce(MonteCarloBarostat(1.0*unit.atmosphere, 300.0*unit.kelvin, 25))

        platform = openmm.Platform.getPlatformByName('OpenCL')
        integrator = openmm.LangevinMiddleIntegrator(
            300.0*unit.kelvin, 1.0/unit.picosecond, dt_fs*unit.femtosecond)
        sim = Simulation(modeller.topology, hybrid_system, integrator, platform, {})
        sim.context.setPositions(modeller.positions)

        sim.minimizeEnergy(maxIterations=200)
        state = sim.context.getState(getForces=True)
        max_f = float(np.max(np.abs(
            state.getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer))))
        if max_f > 1e5:
            log(f"  {label}: FAIL (max force {max_f:.2e})")
            return

        sim.context.setVelocitiesToTemperature(300.0*unit.kelvin)
        sim.step(50)  # warmup

        t0 = time.time()
        sim.step(n_steps)
        elapsed = time.time() - t0

        state = sim.context.getState(getPositions=True, getEnergy=True)
        pe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
        pos = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        if np.any(np.isnan(pos)) or np.isnan(pe):
            log(f"  {label}: FAIL (NaN)")
            return

        ns_produced = n_steps * dt_fs * 1e-6
        ns_per_day = ns_produced / elapsed * 86400
        ms_per_step = elapsed / n_steps * 1000
        log(f"  {label}: {ns_per_day:.2f} ns/day | {ms_per_step:.1f} ms/step | dt={dt_fs}fs")

    except Exception as e:
        log(f"  {label}: ERROR — {e}")

def main():
    import torch
    log("=== THROUGHPUT BENCHMARK v2 ===")
    log(f"GPU: {torch.cuda.get_device_name(0)}")

    log("Building WW protein...")
    modeller_base = build_ww()
    n_prot = modeller_base.topology.getNumAtoms()
    log(f"Protein: {n_prot} atoms (pre-solvation)")

    # Solvate once, reuse topology
    ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
    modeller_base.addSolvent(ff, padding=1.0*unit.nanometer,
                             ionicStrength=0.15*unit.molar, model='tip3p')
    log(f"Solvated: {modeller_base.topology.getNumAtoms()} atoms")

    log("--- Benchmarks ---")

    # A: Baseline (current production: OpenCL, f64, 1fs, no constraints)
    run_benchmark(modeller_base, None, 1.0, None, "A: f64/1fs/no-constr")

    # B: Single precision MACE (OpenCL, f32, 1fs)
    run_benchmark(modeller_base, 'single', 1.0, None, "B: f32/1fs/no-constr")

    # C: f64 with HBonds constraints + 2fs timestep
    run_benchmark(modeller_base, None, 2.0, HBonds, "C: f64/2fs/HBonds")

    # D: f32 + HBonds + 2fs (best expected combo)
    run_benchmark(modeller_base, 'single', 2.0, HBonds, "D: f32/2fs/HBonds")

    # E: f32 + 4fs (aggressive — may be unstable with MACE)
    run_benchmark(modeller_base, 'single', 4.0, HBonds, "E: f32/4fs/HBonds")

    log("=== DONE ===")

if __name__ == "__main__":
    main()
