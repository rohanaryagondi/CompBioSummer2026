#!/usr/bin/env python
"""Test that OpenMM CUDA platform loads without libnvrtc.so.13 errors.

Run via SLURM on a GPU node:
  sbatch --partition=gpu --gres=gpu:1 --cpus-per-task=2 --mem=8G \
         --time=00:05:00 --job-name=t3k9x2m1 \
         --wrap="source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh && conda activate env-mace && python test_cuda_platform.py"
"""
import sys

print("=== OpenMM CUDA Platform Test ===")

# Step 1: Check libnvrtc resolution
import ctypes
try:
    lib = ctypes.CDLL("libnvrtc.so.13")
    print(f"[OK] libnvrtc.so.13 loaded: {lib._name}")
except OSError as e:
    print(f"[FAIL] Cannot load libnvrtc.so.13: {e}")
    sys.exit(1)

# Step 2: Import OpenMM
import openmm
print(f"[OK] OpenMM {openmm.__version__} imported")

# Step 3: Check CUDA platform exists
platform = openmm.Platform.getPlatformByName("CUDA")
print(f"[OK] CUDA platform: {platform.getName()} (speed={platform.getSpeed()})")

# Step 4: Create a minimal system and context on CUDA
from openmm import app
import openmm.unit as u

system = openmm.System()
system.addParticle(12.0 * u.amu)
force = openmm.CustomExternalForce("0.5*k*(x^2+y^2+z^2)")
force.addGlobalParameter("k", 1.0)
force.addParticle(0, [])
system.addForce(force)

integrator = openmm.LangevinIntegrator(300 * u.kelvin, 1.0 / u.picosecond, 0.002 * u.picoseconds)
context = openmm.Context(system, integrator, platform)
context.setPositions([[0.0, 0.0, 0.0]])

state = context.getState(getEnergy=True)
pe = state.getPotentialEnergy().value_in_unit(u.kilojoules_per_mole)
print(f"[OK] Context created on CUDA. PE = {pe:.4f} kJ/mol")

# Step 5: Run 10 steps
integrator.step(10)
state = context.getState(getPositions=True, getEnergy=True)
pe2 = state.getPotentialEnergy().value_in_unit(u.kilojoules_per_mole)
print(f"[OK] 10 steps completed. PE = {pe2:.4f} kJ/mol")

print("\n=== ALL TESTS PASSED ===")
