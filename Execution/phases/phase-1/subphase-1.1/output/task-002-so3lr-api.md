---
task_id: "task-002"
agent: "so3lr-pilot"
subphase: "1.1"
date: 2026-04-16
type: technical-reference
---

# SO3LR API Documentation

## Overview

SO3LR (SO3krates Universal Pairwise Force Field with Long Range Interactions) v0.1.0
is a machine-learned force field built on the so3krates architecture with explicit
long-range interactions (dispersion + electrostatics). It uses JAX/JAX-MD as its
backend, NOT OpenMM or PyTorch.

**Authors:** Adil Kabylda, Thorben Frank
**License:** MIT
**Repository:** https://github.com/thorben-frank/so3lr
**Backend:** JAX 0.5.3, jax-md 0.2.27, mlff 1.0.0
**Python requirement:** 3.12 (not compatible with 3.10)

## Supported Elements

SO3LR supports exactly 8 elements:
- H (1), C (6), N (7), O (8), F (9), P (15), S (16), Cl (17)

This covers most organic/biomolecular systems but excludes metals, halogens
beyond Cl, and heavy elements. Proteins with only standard amino acids are
fully supported (all standard amino acids contain only H, C, N, O, S).

## Package Structure

```
so3lr/
  __init__.py          # Exports: So3lr, So3lrCalculator, So3lrPotential, Graph, to_jax_md
  potential.py         # make_potential_fn -> MLFFPotentialSparse (JAX-MD compatible)
  ase_utils.py         # make_ase_calculator -> ASE Calculator interface
  base_calculator.py   # make_so3lr -> raw JAX forward function
  jaxmd_utils.py       # to_jax_md -> (neighbor_fn, neighbor_fn_lr, energy_fn)
  graph.py             # Graph namedtuple for internal representation
  cli/
    so3lr_cli.py       # Click CLI: so3lr nvt/npt/opt/eval commands
    so3lr_md.py        # Full MD engine: perform_md(), perform_min(), run()
    so3lr_eval.py      # Model evaluation on datasets
    so3lr_finetune.py  # Fine-tuning SO3LR
    md_settings.yaml   # Default MD settings reference
    tune_ewald.py      # Ewald parameter tuning
  params/
    params.pkl         # Pre-trained model weights (2.1 MB)
    hyperparameters.json
    hyperparameters.yaml
    checkpoints/
  config/
    finetune.yaml      # Fine-tuning configuration
```

## Three Interfaces

### 1. CLI Interface (Recommended for production)

The `so3lr` command provides NVT, NPT, NVE, and geometry optimization:

```bash
# NVT simulation (default ensemble)
so3lr --input geometry.xyz --output trajectory.hdf5 \
      --dt 0.5 --temperature 300 --md-cycles 100 --md-steps 100

# NPT simulation
so3lr --input geometry.xyz --pressure 1.0 --md-cycles 100

# Geometry optimization only
so3lr opt --input geometry.xyz --output optimized.xyz

# NVE simulation
so3lr nve --input geometry.xyz --md-cycles 100

# With custom model
so3lr --input geometry.xyz --model /path/to/model/dir
```

**Key CLI options:**
- `--dt`: Timestep in fs (default: 0.5)
- `--temperature`: Target T in K (default: 300)
- `--pressure`: Target P in atm (enables NPT; default: None = NVT)
- `--md-cycles`: Number of MD cycles (default: 100)
- `--md-steps`: Steps per cycle (default: 100)
- `--lr-cutoff`: Long-range cutoff in A (default: 12.0)
- `--precision`: float32 or float64 (default: float32)
- `--relax/--no-relax`: Geometry relaxation before MD (default: --relax)
- `--seed`: Random seed (default: 52)
- `--restart-save/--restart-load`: Checkpoint paths
- `--buffer-sr/--buffer-lr`: Neighbor list buffer multipliers (default: 1.25)
- `--nhc-chain/--nhc-steps/--nhc-thermo/--nhc-baro`: Thermostat params
- `--output`: Trajectory file (.hdf5 recommended, .xyz supported)

**Input format:** Any ASE-readable format (.xyz, .extxyz, .pdb)
**Output format:** HDF5 (recommended, no I/O overhead) or extxyz

### 2. JAX-MD Interface (Programmatic)

Use `So3lrPotential` + `to_jax_md` for custom JAX-MD simulations:

```python
import jax
import jax.numpy as jnp
from jax_md import space, simulate, units, quantity
from so3lr import So3lrPotential
from so3lr.jaxmd_utils import to_jax_md

# Load potential
potential = So3lrPotential(
    dtype=jnp.float32,
    lr_cutoff=12.0,
    dispersion_energy_cutoff_lr_damping=2.0,
)

# Setup space (free = vacuum, periodic_general = PBC)
displacement_fn, shift_fn = space.free()
box = jnp.array([0.0])

# Create JAX-MD compatible functions
neighbor_fn, neighbor_fn_lr, energy_fn = to_jax_md(
    potential,
    displacement_fn,
    box,
    species=species,  # jnp.int32 array of atomic numbers
    fractional_coordinates=False,
)

# Allocate neighbor lists
nbrs = neighbor_fn.allocate(positions, box=box)
nbrs_lr = neighbor_fn_lr.allocate(positions, box=box)

# Energy evaluation
energy = energy_fn(positions, nbrs.idx, nbrs_lr.idx, box=box)

# NVT with Nose-Hoover
unit = units.metal_unit_system()
dt = 0.5 * unit['time']
kT = 300.0 * unit['temperature']

init_fn, apply_fn = simulate.nvt_nose_hoover(
    jax.jit(lambda R, neighbor, neighbor_lr, **kw:
        energy_fn(R, neighbor, neighbor_lr, has_aux=False, **kw)),
    shift_fn,
    dt=dt, kT=kT, box=box,
    thermostat_kwargs={'chain_length': 3, 'chain_steps': 2, 'sy_steps': 3, 'tau': dt*100}
)

state = jax.jit(init_fn)(key, positions, box=box,
    neighbor=nbrs.idx, neighbor_lr=nbrs_lr.idx,
    kT=kT, mass=masses)

# Step function (for fori_loop)
@jax.jit
def step(i, carry):
    state, nbrs, nbrs_lr, box, k_grid = carry
    state = apply_fn(state, neighbor=nbrs.idx, neighbor_lr=nbrs_lr.idx,
                     box=box, k_grid=k_grid)
    nbrs = nbrs.update(state.position, neighbor=nbrs.idx)
    nbrs_lr = nbrs_lr.update(state.position, neighbor=nbrs_lr.idx)
    return (state, nbrs, nbrs_lr, box, k_grid)
```

### 3. ASE Calculator Interface

For single-point energy/force evaluations:

```python
from so3lr import So3lrCalculator
calc = So3lrCalculator()
atoms.calc = calc
energy = atoms.get_potential_energy()
forces = atoms.get_forces()
```

### 4. Raw Forward Function (So3lr)

Low-level access to the model:

```python
from so3lr import So3lr
so3lr_fn = So3lr(lr_cutoff=12.0, calculate_forces=True)
output = so3lr_fn({
    'positions': positions,
    'atomic_numbers': species,
    'idx_i': ..., 'idx_j': ...,
    'displacements': ...,
    ...
})
# output['energy'], output['forces']
```

## Important Technical Details

### Dual Neighbor Lists

SO3LR uses TWO neighbor lists:
1. **Short-range (SR):** cutoff = `potential.cutoff` (model-dependent, typically ~5-6 A)
2. **Long-range (LR):** cutoff = `lr_cutoff` (default 12.0 A)

Both must be allocated, updated, and checked for overflow independently.

### Boundary Conditions

- **Free (vacuum):** `space.free()`, `box = jnp.array([0.0])`
- **Periodic:** `space.periodic_general(box)`, requires orthogonal cell
  - Cell dimensions must be >= 2 * lr_cutoff (24 A minimum)
  - Non-orthogonal cells NOT supported by JAX-MD

### Unit System

SO3LR uses JAX-MD's metal unit system:
- Energy: eV
- Length: Angstrom
- Time: internal units (convert from fs via `units.metal_unit_system()['time']`)
- Temperature: convert K via `units.metal_unit_system()['temperature']`

### JIT Compilation

First evaluation triggers XLA JIT compilation (can take 30-300+ seconds depending
on system size and GPU). Subsequent steps are fast. Use `jax.block_until_ready()`
to ensure synchronization for timing.

### Neighbor List Overflow

After each cycle, check `nbrs.did_buffer_overflow` and `nbrs_lr.did_buffer_overflow`.
If overflow occurs, reallocate with `neighbor_fn.allocate()`.

### NaN Detection

JAX can silently produce NaN. Explicitly check `jnp.any(jnp.isnan(state.position))`
after simulation blocks.

### Default Simulation Parameters

From `md_settings.yaml`:
- dt: 0.5 fs
- T: 300 K
- NHC chain length: 3
- NHC integration steps: 2
- NHC thermostat damping: 100 * dt
- Relaxation before MD: enabled by default
- Save buffer: 50 frames
- Precision: float32

### Performance Reference

From the CLI code, on an A100 GPU, expected time per step:
- ~3.25e-6 seconds per atom per step
- For crambin (640 atoms): ~2.1 ms per step
- At 0.5 fs timestep: ~41 ns/day theoretical

## Caveats for Alpha-M Track

1. **Vacuum only for non-periodic systems:** Proteins without explicit solvent
   run with free boundary conditions. No implicit solvent model built in.

2. **No enhanced sampling:** SO3LR provides bare NVT/NPT/NVE. No metadynamics,
   replica exchange, or other enhanced sampling methods built in.

3. **Hydrogen required:** Unlike some CG models, SO3LR requires explicit hydrogens.
   PDB files typically need H-addition via Open Babel or PDBFixer before use.

4. **Cell size constraints:** For periodic systems, minimum cell dimension is
   2 * lr_cutoff = 24 A. Crambin crystal cell (40.96 x 18.65 x 22.52) has
   non-orthogonal components and one dimension below 24 A -- cannot use PBC
   directly with SO3LR.

5. **Memory:** JIT compilation requires significant RAM. Request >= 64 GB for
   protein simulations.

## CLI Subcommands Reference

```
so3lr                    # Main command (NVT default)
so3lr nvt                # Explicit NVT
so3lr npt                # NPT (requires --pressure)
so3lr nve                # NVE (microcanonical)
so3lr opt                # Geometry optimization
so3lr eval               # Model evaluation on dataset
so3lr finetune           # Fine-tune SO3LR on custom data
so3lr tune-ewald         # Tune Ewald parameters for periodic systems
```
