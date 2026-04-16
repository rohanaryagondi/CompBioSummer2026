#!/bin/bash
#SBATCH --job-name=mace-cuda-test
#SBATCH --partition=gpu
#SBATCH --gres=gpu:rtx_5000_ada:1
#SBATCH --time=00:10:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=2
#SBATCH --output=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/mace_cuda_test_%j.out
#SBATCH --error=/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/mace_cuda_test_%j.err

# Quick test: Does OpenMM CUDA platform work on RTX 5000 Ada (sm_89)?
# This helps determine if CUDA is viable for future MACE production runs.

echo "MACE CUDA Test on RTX 5000 Ada"
echo "Node: $(hostname)"
echo "GPU: $(nvidia-smi --query-gpu=name,compute_cap,memory.total --format=csv,noheader 2>/dev/null)"
echo "Date: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"

ENV_PYTHON=/home/rag88/.conda/envs/env-mace/bin/python
export PYTHONNOUSERSITE=1

${ENV_PYTHON} -c "
import torch
print(f'PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'  GPU: {torch.cuda.get_device_name(0)}')
    props = torch.cuda.get_device_properties(0)
    print(f'  Compute capability: {props.major}.{props.minor}')

import openmm
from openmm import unit
from openmm.app import PDBFile, Modeller, Simulation
print(f'OpenMM: {openmm.__version__}')

# Try CUDA platform specifically
try:
    platform = openmm.Platform.getPlatformByName('CUDA')
    print(f'CUDA platform found (speed: {platform.getSpeed()})')
except Exception as e:
    print(f'CUDA platform lookup error: {e}')
    import sys; sys.exit(1)

# Load crambin and create MACE system
pdb = PDBFile('/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/crambin.pdb')
modeller = Modeller(pdb.topology, pdb.positions)
modeller.addHydrogens()
print(f'Crambin: {modeller.topology.getNumAtoms()} atoms')

from openmmml import MLPotential
potential = MLPotential('mace-off24-medium')
system = potential.createSystem(modeller.topology)
print('MACE system created')

# Try creating simulation with CUDA
integrator = openmm.LangevinMiddleIntegrator(300*unit.kelvin, 1/unit.picosecond, 1*unit.femtosecond)
try:
    sim = Simulation(modeller.topology, system, integrator, platform, {'Precision': 'mixed'})
    sim.context.setPositions(modeller.positions)

    # Quick energy check
    state = sim.context.getState(getEnergy=True)
    pe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
    print(f'CUDA Context created successfully! PE = {pe:.1f} kJ/mol')

    # Run 100 steps
    sim.step(100)
    state = sim.context.getState(getEnergy=True)
    pe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
    print(f'100 steps completed. PE = {pe:.1f} kJ/mol')
    print('RESULT: CUDA WORKS on RTX 5000 Ada')
except Exception as e:
    print(f'CUDA simulation FAILED: {e}')
    print('RESULT: CUDA BROKEN on RTX 5000 Ada')
"
echo "Test complete at $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
