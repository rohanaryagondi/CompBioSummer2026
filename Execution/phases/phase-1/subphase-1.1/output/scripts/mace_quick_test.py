#!/usr/bin/env python
"""Quick CPU test to validate MACE-OFF24 + OpenMM-ML integration before SLURM submission."""
import os
os.environ['PYTHONNOUSERSITE'] = '1'

import sys
import time

PDB_PATH = "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/crambin.pdb"

print("=== MACE-OFF24 Quick Integration Test (CPU only) ===")
print()

# Step 1: Load PDB
print("1. Loading crambin PDB...")
from openmm.app import PDBFile, Modeller
pdb = PDBFile(PDB_PATH)
modeller = Modeller(pdb.topology, pdb.positions)
print(f"   Atoms: {modeller.topology.getNumAtoms()}, Residues: {modeller.topology.getNumResidues()}")

# Step 2: Add hydrogens
print("2. Adding hydrogens...")
modeller.addHydrogens()
n_atoms = modeller.topology.getNumAtoms()
print(f"   After hydrogens: {n_atoms} atoms")

# Step 3: Create MACE potential
print("3. Creating MACE-OFF24-medium potential...")
from openmmml import MLPotential
potential = MLPotential('mace-off24-medium')
print("   Potential created.")

# Step 4: Create system
print("4. Creating system from topology...")
t0 = time.time()
system = potential.createSystem(modeller.topology)
t_sys = time.time() - t0
print(f"   System created in {t_sys:.1f}s: {system.getNumParticles()} particles, {system.getNumForces()} forces")

# Step 5: Create simulation
print("5. Creating simulation (CPU platform)...")
import openmm
from openmm import unit

integrator = openmm.LangevinMiddleIntegrator(
    300 * unit.kelvin, 1 / unit.picosecond, 1 * unit.femtosecond
)
platform = openmm.Platform.getPlatformByName('CPU')
simulation = openmm.app.Simulation(modeller.topology, system, integrator, platform)
simulation.context.setPositions(modeller.positions)
print("   Simulation created.")

# Step 6: Minimize
print("6. Minimizing energy (max 500 iterations)...")
t0 = time.time()
simulation.minimizeEnergy(maxIterations=500)
t_min = time.time() - t0
state = simulation.context.getState(getEnergy=True)
pe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
print(f"   Minimized in {t_min:.1f}s. PE = {pe:.1f} kJ/mol")

# Step 7: Run 10 steps
print("7. Running 10 MD steps (10 fs)...")
simulation.context.setVelocitiesToTemperature(300 * unit.kelvin)
t0 = time.time()
simulation.step(10)
t_steps = time.time() - t0
state = simulation.context.getState(getEnergy=True, getPositions=True)
pe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
import numpy as np
positions = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
has_nan = np.any(np.isnan(positions))
print(f"   10 steps in {t_steps:.1f}s. PE = {pe:.1f} kJ/mol. NaN: {has_nan}")

# Step 8: Run 100 more steps (total 110 fs)
print("8. Running 100 more steps (total 110 fs)...")
t0 = time.time()
simulation.step(100)
t_steps = time.time() - t0
state = simulation.context.getState(getEnergy=True, getPositions=True)
pe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
positions = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
has_nan = np.any(np.isnan(positions))
print(f"   100 steps in {t_steps:.1f}s. PE = {pe:.1f} kJ/mol. NaN: {has_nan}")

print()
if not has_nan:
    print("=== INTEGRATION TEST PASSED ===")
    print("MACE-OFF24-medium + OpenMM-ML works. Ready for GPU SLURM submission.")
    sys.exit(0)
else:
    print("=== INTEGRATION TEST FAILED: NaN detected ===")
    sys.exit(1)
