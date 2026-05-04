"""
Throughput benchmark: test MACE hybrid NPT with different platform/precision combos.
Runs 200 steps of production with each configuration and reports ns/day.
"""
import os, sys, time, numpy as np
os.environ['PYTHONNOUSERSITE'] = '1'

import openmm
from openmm import unit, MonteCarloBarostat
from openmm.app import PDBFile, Modeller, Simulation, ForceField, PME
from openmmml import MLPotential
from pdbfixer import PDBFixer
import tempfile

def log(msg):
    from datetime import datetime, timezone
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%SZ')}] {msg}", flush=True)

def build_system():
    """Build the WW solvated hybrid system (shared across all benchmarks)."""
    pdb = PDBFile("/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ww.pdb")
    modeller = Modeller(pdb.topology, pdb.positions)

    std_aa = {'ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE',
              'LEU','LYS','MET','PHE','PRO','SER','THR','TRP','TYR','VAL',
              'HID','HIE','HIP','CYX','CYM','ASH','GLH','LYN'}
    non_prot = [r for r in modeller.topology.residues() if r.name not in std_aa]
    if non_prot:
        modeller.delete(non_prot)
    first_chain = list(modeller.topology.chains())[0].id
    other = []
    for c in modeller.topology.chains():
        if c.id != first_chain:
            other.extend(c.residues())
    if other:
        modeller.delete(other)
    to_del = [r for r in modeller.topology.residues()
              if int(r.id) < 6 or int(r.id) > 39]
    if to_del:
        modeller.delete(to_del)

    with tempfile.NamedTemporaryFile(suffix='.pdb', mode='w', delete=False) as f:
        PDBFile.writeFile(modeller.topology, modeller.positions, f)
        tmp = f.name
    fixer = PDBFixer(filename=tmp)
    fixer.findMissingResidues()
    fixer.missingResidues = {}
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(pH=7.0)
    modeller = Modeller(fixer.topology, fixer.positions)
    os.unlink(tmp)

    protein_atoms = list(range(modeller.topology.getNumAtoms()))
    ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
    modeller.addSolvent(ff, padding=1.0*unit.nanometer,
                        ionicStrength=0.15*unit.molar, model='tip3p')

    mm_system = ff.createSystem(modeller.topology, nonbondedMethod=PME,
                                nonbondedCutoff=1.0*unit.nanometer,
                                constraints=None, rigidWater=True)
    potential = MLPotential('mace-off24-medium')
    hybrid_system = potential.createMixedSystem(modeller.topology, mm_system,
                                                protein_atoms, interpolate=False)
    hybrid_system.addForce(MonteCarloBarostat(1.0*unit.atmosphere,
                                              300.0*unit.kelvin, 25))

    return modeller, hybrid_system, protein_atoms


def benchmark(modeller, hybrid_system, platform_name, precision_props, label, n_steps=200):
    """Run n_steps and report throughput."""
    try:
        platform = openmm.Platform.getPlatformByName(platform_name)
        props = precision_props if precision_props else {}

        integrator = openmm.LangevinMiddleIntegrator(
            300.0*unit.kelvin, 1.0/unit.picosecond, 1.0*unit.femtosecond)
        sim = Simulation(modeller.topology, hybrid_system, integrator, platform, props)
        sim.context.setPositions(modeller.positions)

        # Quick minimize (100 iter)
        sim.minimizeEnergy(maxIterations=100)
        state = sim.context.getState(getForces=True)
        max_f = float(np.max(np.abs(
            state.getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer))))
        if max_f > 1e5:
            log(f"  {label}: FAIL (max force {max_f:.2e} after minimize)")
            return

        # Check NaN
        pos = sim.context.getState(getPositions=True).getPositions(asNumpy=True)
        if np.any(np.isnan(pos.value_in_unit(unit.nanometer))):
            log(f"  {label}: FAIL (NaN positions)")
            return

        sim.context.setVelocitiesToTemperature(300.0*unit.kelvin)

        # Warmup (50 steps, not timed)
        sim.step(50)

        # Timed run
        t0 = time.time()
        sim.step(n_steps)
        elapsed = time.time() - t0

        # Check for NaN
        state = sim.context.getState(getPositions=True, getEnergy=True)
        pe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
        pos = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        if np.any(np.isnan(pos)) or np.isnan(pe):
            log(f"  {label}: FAIL (NaN after {n_steps} steps)")
            return

        ns_produced = n_steps * 1e-6  # 1 fs steps
        ns_per_day = ns_produced / elapsed * 86400
        ms_per_step = elapsed / n_steps * 1000

        log(f"  {label}: {ns_per_day:.2f} ns/day | {ms_per_step:.1f} ms/step | "
            f"PE={pe:.0f} kJ/mol | max_f={max_f:.0e}")

    except Exception as e:
        log(f"  {label}: ERROR — {e}")


def main():
    import torch
    log("=== MACE THROUGHPUT BENCHMARK ===")
    log(f"GPU: {torch.cuda.get_device_name(0)}")
    log(f"Platforms: {[openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())]}")

    log("Building system...")
    modeller, hybrid_system, protein_atoms = build_system()
    log(f"System: {hybrid_system.getNumParticles()} particles")

    log("Running benchmarks (200 steps each)...")

    # Test 1: OpenCL (current baseline)
    benchmark(modeller, hybrid_system, 'OpenCL', {}, 'OpenCL/f64')

    # Test 2: CUDA platform
    benchmark(modeller, hybrid_system, 'CUDA', {}, 'CUDA/f64')

    # Test 3: CUDA with mixed precision
    benchmark(modeller, hybrid_system, 'CUDA', {'Precision': 'mixed'}, 'CUDA/mixed')

    # Test 4: OpenCL (reference, repeat for variance)
    benchmark(modeller, hybrid_system, 'OpenCL', {}, 'OpenCL/f64 (repeat)')

    log("=== DONE ===")

if __name__ == "__main__":
    main()
