#!/usr/bin/env python3
"""
SO3LR Crambin NVT Simulation Script
Task 002 - D1 Gate Evidence for SO3LR

This script performs staged NVT simulation of crambin (46 residues, 640 atoms
with hydrogens) using SO3LR MLFF via JAX-MD.

Stages:
  A: 100 ps vacuum NVT (200 cycles x 1000 steps x 0.5 fs = 100 ps)
  B: 1 ns vacuum NVT (2000 cycles x 1000 steps x 0.5 fs = 1 ns)

Usage:
  python so3lr_crambin_nvt.py --stage A   # 100 ps test
  python so3lr_crambin_nvt.py --stage B   # full 1 ns production
"""

import os
import sys
import time
import json
import argparse
import logging
import warnings
import numpy as np

warnings.filterwarnings("ignore", message="scatter inputs have incompatible types")
warnings.filterwarnings("ignore", message="Explicitly requested dtype.*truncated")
warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ---- Setup logging ----
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ---- Parse args ----
parser = argparse.ArgumentParser(description="SO3LR crambin NVT simulation")
parser.add_argument("--stage", choices=["A", "B"], default="A",
                    help="Stage A=100ps test, B=1ns production")
parser.add_argument("--input-pdb", default=None,
                    help="Path to crambin PDB (with hydrogens)")
parser.add_argument("--output-dir", default=".",
                    help="Output directory for trajectories and analysis")
args = parser.parse_args()

# ---- Step 1: JAX GPU verification ----
logger.info("=" * 60)
logger.info("SO3LR Crambin NVT Simulation - Task 002")
logger.info("=" * 60)

import jax
import jax.numpy as jnp

logger.info(f"JAX version: {jax.__version__}")
logger.info(f"JAX backend: {jax.default_backend()}")
logger.info(f"JAX devices: {jax.devices()}")

if jax.default_backend() not in ("gpu", "cuda"):
    logger.warning("JAX is NOT using GPU. Simulation will be very slow on CPU.")
else:
    for dev in jax.devices():
        logger.info(f"  Device: {dev}")
        try:
            stats = dev.memory_stats()
            if stats:
                total_gb = stats.get('bytes_total', 0) / 1e9
                logger.info(f"  GPU memory: {total_gb:.1f} GB")
        except Exception:
            pass

# ---- Step 2: Import SO3LR and dependencies ----
import jax_md
from jax_md import space, partition, simulate, quantity, units
from ase.io import read, write
import so3lr
from so3lr import So3lrPotential
from so3lr.jaxmd_utils import to_jax_md

logger.info(f"SO3LR version: {so3lr.__version__}")
logger.info(f"jax_md imported successfully")

# ---- Step 3: Load and prepare crambin ----
if args.input_pdb is not None:
    input_path = args.input_pdb
else:
    # Default: try to find hydrogenated crambin
    input_path = os.path.join(args.output_dir, "crambin_h_vacuum.xyz")

logger.info(f"Loading structure from: {input_path}")
atoms = read(input_path)
n_atoms = len(atoms)
logger.info(f"Number of atoms: {n_atoms}")
logger.info(f"Formula: {atoms.get_chemical_formula()}")
logger.info(f"Atomic numbers present: {sorted(set(atoms.get_atomic_numbers().tolist()))}")
logger.info(f"Cell: {atoms.cell}")
logger.info(f"PBC: {atoms.pbc}")

# Verify all elements are supported by SO3LR
allowed_z = {1, 6, 7, 8, 9, 15, 16, 17}  # H, C, N, O, F, P, S, Cl
current_z = set(int(x) for x in atoms.get_atomic_numbers())
if not current_z.issubset(allowed_z):
    unsupported = current_z - allowed_z
    logger.error(f"Unsupported elements: {unsupported}")
    sys.exit(1)
logger.info("All elements supported by SO3LR.")

# Convert to JAX arrays
precision = jnp.float32
positions = jnp.array(atoms.get_positions(), dtype=precision)
species = jnp.array(atoms.get_atomic_numbers(), dtype=jnp.int32)
masses = jnp.array(atoms.get_masses(), dtype=precision)

logger.info(f"Positions shape: {positions.shape}")
logger.info(f"Species shape: {species.shape}")

# ---- Step 4: Setup SO3LR potential ----
logger.info("Creating SO3LR potential...")
t_potential_start = time.time()
potential = So3lrPotential(
    dtype=precision,
    lr_cutoff=12.0,
    dispersion_energy_cutoff_lr_damping=2.0,
)
t_potential_end = time.time()
logger.info(f"Potential created in {t_potential_end - t_potential_start:.2f} s")
logger.info(f"Short-range cutoff: {potential.cutoff}")
logger.info(f"Long-range cutoff: {potential.long_range_cutoff}")

# ---- Step 5: Setup space and neighbor lists ----
# Free boundary conditions (vacuum simulation)
displacement_fn, shift_fn = space.free()
box = jnp.array([0.0])
fractional_coordinates = False

logger.info("Setting up neighbor lists...")
t_nl_start = time.time()
neighbor_fn, neighbor_fn_lr, energy_fn = to_jax_md(
    potential,
    displacement_fn,
    box,
    species=species,
    dr_threshold=0.0,
    capacity_multiplier=1.25,
    buffer_size_multiplier_sr=1.25,
    buffer_size_multiplier_lr=1.25,
    fractional_coordinates=fractional_coordinates,
)
t_nl_end = time.time()
logger.info(f"Neighbor list setup in {t_nl_end - t_nl_start:.2f} s")

# Allocate neighbor lists
logger.info("Allocating neighbor lists...")
nbrs = neighbor_fn.allocate(positions, box=box)
nbrs_lr = neighbor_fn_lr.allocate(positions, box=box)
logger.info("Neighbor lists allocated.")

# ---- Step 6: Setup NVT simulation ----
# Simulation parameters
dt_fs = 0.5   # femtoseconds
T_kelvin = 300.0

# Convert units using jax_md metal unit system
unit = units.metal_unit_system()
dt = dt_fs * unit['time']
kT = T_kelvin * unit['temperature']

# NHC thermostat parameters
nhc_kwargs = {
    'chain_length': 3,
    'chain_steps': 2,
    'sy_steps': 3,
    'tau': dt * 100.0,  # damping timescale
}

# Stage parameters
if args.stage == "A":
    md_cycles = 200    # 200 cycles
    md_steps = 1000    # 1000 steps per cycle
    total_steps = md_cycles * md_steps  # 200,000 steps = 100 ps at 0.5 fs
    total_time_ps = total_steps * dt_fs / 1000.0
    logger.info(f"Stage A: {total_steps} steps = {total_time_ps} ps")
elif args.stage == "B":
    md_cycles = 2000   # 2000 cycles
    md_steps = 1000    # 1000 steps per cycle
    total_steps = md_cycles * md_steps  # 2,000,000 steps = 1 ns at 0.5 fs
    total_time_ps = total_steps * dt_fs / 1000.0
    logger.info(f"Stage B: {total_steps} steps = {total_time_ps} ps")

# Create energy function for NVT
energy_fn_jit = jax.jit(lambda R, neighbor, neighbor_lr, **kwargs:
    energy_fn(R, neighbor, neighbor_lr, has_aux=False, **kwargs))

logger.info("Creating NVT Nose-Hoover chain integrator...")
init_fn, apply_fn = simulate.nvt_nose_hoover(
    energy_fn_jit,
    shift_fn,
    dt=dt,
    kT=kT,
    box=box,
    thermostat_kwargs=nhc_kwargs,
)
init_fn = jax.jit(init_fn)
apply_fn = jax.jit(apply_fn)

# ---- Step 7: Initialize state ----
logger.info("Initializing simulation state...")
rng_key = jax.random.PRNGKey(42)
state = init_fn(
    rng_key,
    positions,
    box=box,
    neighbor=nbrs.idx,
    neighbor_lr=nbrs_lr.idx,
    kT=kT,
    mass=masses,
)
logger.info("State initialized.")

# ---- Step 8: Create step function ----
@jax.jit
def step_fn(i, carry):
    state, nbrs, nbrs_lr, box_val, k_grid = carry
    state = apply_fn(
        state,
        neighbor=nbrs.idx,
        neighbor_lr=nbrs_lr.idx,
        box=box_val,
        k_grid=k_grid,
    )
    nbrs = nbrs.update(state.position, neighbor=nbrs.idx)
    nbrs_lr = nbrs_lr.update(state.position, neighbor=nbrs_lr.idx)
    return (state, nbrs, nbrs_lr, box_val, k_grid)

# ---- Step 9: Run MD ----
logger.info("=" * 60)
logger.info(f"Starting NVT MD simulation: {md_cycles} cycles x {md_steps} steps")
logger.info(f"dt = {dt_fs} fs, T = {T_kelvin} K, total = {total_time_ps} ps")
logger.info("=" * 60)

# Storage for analysis
energies = []
temperatures = []
positions_traj = []
times_ps = []
cycle_wall_times = []

# Initial quantities
# masses must be reshaped to (n_atoms, 1) for broadcasting with momentum (n_atoms, 3)
masses_col = masses.reshape(-1, 1)

def compute_temp(state):
    """Compute instantaneous temperature from kinetic energy."""
    # Compute KE = sum(p^2 / (2*m)) over all atoms and dimensions
    ke = jnp.sum(state.momentum**2 / masses_col) * 0.5
    ndof = 3 * n_atoms - 6  # non-linear molecule
    temp = 2.0 * ke / (ndof * unit['temperature'])
    return ke, temp

def compute_pe(state, nbrs, nbrs_lr):
    """Compute potential energy."""
    pe = energy_fn_jit(state.position, nbrs.idx, nbrs_lr.idx, box=box)
    return pe

# Log initial state
ke0, temp0 = compute_temp(state)
pe0 = compute_pe(state, nbrs, nbrs_lr)
logger.info(f"Initial: PE={float(pe0):.4f} eV, KE={float(ke0):.4f} eV, "
            f"E={float(pe0+ke0):.4f} eV, T={float(temp0):.1f} K")

k_grid = None  # no k-space grid for vacuum

# JIT compilation timing (first cycle)
logger.info("Running first cycle (includes JIT compilation)...")
t_jit_start = time.time()
result = jax.block_until_ready(
    jax.lax.fori_loop(0, md_steps, step_fn, (state, nbrs, nbrs_lr, box, k_grid))
)
t_jit_end = time.time()
jit_time = t_jit_end - t_jit_start
logger.info(f"First cycle (JIT + execution): {jit_time:.2f} s")

state, nbrs, nbrs_lr, box_val, _ = result

# Check for overflow
if nbrs.did_buffer_overflow:
    logger.warning("Short-range neighbor list overflowed! Reallocating...")
    nbrs = neighbor_fn.allocate(state.position, box=box)
if nbrs_lr.did_buffer_overflow:
    logger.warning("Long-range neighbor list overflowed! Reallocating...")
    nbrs_lr = neighbor_fn_lr.allocate(state.position, box=box)

# Check for NaN
pos_arr = np.array(state.position)
if np.any(np.isnan(pos_arr)):
    logger.error("NaN detected in positions after first cycle! Simulation unstable.")
    # Still write reports documenting failure
    results = {
        "stage": args.stage,
        "status": "FAILED",
        "failure_reason": "NaN in positions after first cycle",
        "jit_compilation_time_s": jit_time,
        "n_atoms": n_atoms,
        "dt_fs": dt_fs,
        "T_kelvin": T_kelvin,
    }
    results_path = os.path.join(args.output_dir, f"so3lr_results_stage{args.stage}.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    sys.exit(1)

# Record first cycle data
ke1, temp1 = compute_temp(state)
pe1 = compute_pe(state, nbrs, nbrs_lr)
energies.append(float(pe1 + ke1))
temperatures.append(float(temp1))
positions_traj.append(np.array(state.position))
times_ps.append(md_steps * dt_fs / 1000.0)
cycle_wall_times.append(jit_time)

logger.info(f"Cycle 1/{md_cycles}: PE={float(pe1):.4f} eV, "
            f"E={float(pe1+ke1):.4f} eV, T={float(temp1):.1f} K, "
            f"wall={jit_time:.2f} s")

# Production cycles
nan_detected = False
for cycle in range(1, md_cycles):
    t_cycle_start = time.time()

    result = jax.block_until_ready(
        jax.lax.fori_loop(0, md_steps, step_fn, (state, nbrs, nbrs_lr, box, k_grid))
    )
    state, nbrs, nbrs_lr, box_val, _ = result

    t_cycle_end = time.time()
    wall = t_cycle_end - t_cycle_start
    cycle_wall_times.append(wall)

    # Check overflow
    if nbrs.did_buffer_overflow:
        logger.warning(f"Cycle {cycle+1}: SR neighbor list overflow, reallocating...")
        nbrs = neighbor_fn.allocate(state.position, box=box)
    if nbrs_lr.did_buffer_overflow:
        logger.warning(f"Cycle {cycle+1}: LR neighbor list overflow, reallocating...")
        nbrs_lr = neighbor_fn_lr.allocate(state.position, box=box)

    # Check NaN
    pos_arr = np.array(state.position)
    if np.any(np.isnan(pos_arr)):
        logger.error(f"NaN detected at cycle {cycle+1}! Simulation unstable.")
        nan_detected = True
        break

    # Record data every cycle (every 0.5 ps)
    ke_c, temp_c = compute_temp(state)
    pe_c = compute_pe(state, nbrs, nbrs_lr)
    total_e = float(pe_c + ke_c)
    temp_val = float(temp_c)

    energies.append(total_e)
    temperatures.append(temp_val)
    times_ps.append((cycle + 1) * md_steps * dt_fs / 1000.0)

    # Save positions every 10 cycles (5 ps) to limit memory
    if (cycle + 1) % 10 == 0:
        positions_traj.append(np.array(state.position))

    # Log every 50 cycles
    if (cycle + 1) % 50 == 0 or cycle == md_cycles - 1:
        avg_wall = np.mean(cycle_wall_times[-50:])
        logger.info(f"Cycle {cycle+1}/{md_cycles}: PE={float(pe_c):.4f} eV, "
                    f"E={total_e:.4f} eV, T={temp_val:.1f} K, "
                    f"avg_wall={avg_wall:.4f} s/cycle")

# ---- Step 10: Analysis ----
logger.info("=" * 60)
logger.info("Analysis")
logger.info("=" * 60)

completed_cycles = len(energies)
completed_time_ps = times_ps[-1] if times_ps else 0
completed_steps = completed_cycles * md_steps

logger.info(f"Completed: {completed_cycles}/{md_cycles} cycles = {completed_time_ps:.1f} ps")

# Energy analysis
energies = np.array(energies)
temperatures = np.array(temperatures)
times_ps = np.array(times_ps)

# Energy drift
if len(energies) > 10:
    e_mean = np.mean(energies)
    e_std = np.std(energies)
    e_drift = (energies[-1] - energies[0]) / (times_ps[-1] - times_ps[0])  # eV/ps
    e_drift_per_atom = e_drift / n_atoms  # eV/ps/atom
    logger.info(f"Energy: mean={e_mean:.4f} eV, std={e_std:.4f} eV")
    logger.info(f"Energy drift: {e_drift:.6f} eV/ps ({e_drift_per_atom:.8f} eV/ps/atom)")
else:
    e_mean = np.mean(energies) if len(energies) > 0 else 0
    e_std = np.std(energies) if len(energies) > 0 else 0
    e_drift = 0
    e_drift_per_atom = 0

# Temperature analysis
if len(temperatures) > 0:
    t_mean = np.mean(temperatures)
    t_std = np.std(temperatures)
    logger.info(f"Temperature: mean={t_mean:.1f} K, std={t_std:.1f} K (target={T_kelvin} K)")
else:
    t_mean = 0
    t_std = 0

# RMSD analysis
if len(positions_traj) > 1:
    ref_pos = positions_traj[0]
    rmsds = []
    for pos in positions_traj:
        diff = pos - ref_pos
        rmsd = np.sqrt(np.mean(np.sum(diff**2, axis=1)))
        rmsds.append(rmsd)
    rmsds = np.array(rmsds)
    logger.info(f"RMSD (vs initial): final={rmsds[-1]:.3f} A, max={np.max(rmsds):.3f} A, mean={np.mean(rmsds):.3f} A")
    rmsd_final = float(rmsds[-1])
    rmsd_max = float(np.max(rmsds))
else:
    rmsd_final = 0
    rmsd_max = 0

# Timing analysis
wall_production = cycle_wall_times[1:] if len(cycle_wall_times) > 1 else cycle_wall_times
avg_wall_per_cycle = np.mean(wall_production) if len(wall_production) > 0 else 0
avg_wall_per_step = avg_wall_per_cycle / md_steps if md_steps > 0 else 0
total_wall_time = sum(cycle_wall_times)
ns_per_day = (completed_time_ps / 1000.0) / (total_wall_time / 86400.0) if total_wall_time > 0 else 0

logger.info(f"JIT compilation time: {jit_time:.2f} s")
logger.info(f"Avg wall time per cycle: {avg_wall_per_cycle:.4f} s")
logger.info(f"Avg wall time per step: {avg_wall_per_step:.6f} s")
logger.info(f"Total wall time: {total_wall_time:.1f} s")
logger.info(f"Performance: {ns_per_day:.2f} ns/day")

# ---- Step 11: Save results ----
results = {
    "stage": args.stage,
    "status": "FAILED" if nan_detected else "COMPLETED",
    "failure_reason": "NaN detected" if nan_detected else None,
    "n_atoms": n_atoms,
    "dt_fs": dt_fs,
    "T_kelvin": T_kelvin,
    "total_steps_planned": total_steps,
    "completed_cycles": completed_cycles,
    "completed_steps": completed_steps,
    "completed_time_ps": float(completed_time_ps),
    "jit_compilation_time_s": jit_time,
    "avg_wall_per_cycle_s": float(avg_wall_per_cycle),
    "avg_wall_per_step_s": float(avg_wall_per_step),
    "total_wall_time_s": float(total_wall_time),
    "ns_per_day": float(ns_per_day),
    "energy_mean_eV": float(e_mean),
    "energy_std_eV": float(e_std),
    "energy_drift_eV_per_ps": float(e_drift),
    "energy_drift_eV_per_ps_per_atom": float(e_drift_per_atom),
    "temperature_mean_K": float(t_mean),
    "temperature_std_K": float(t_std),
    "rmsd_final_A": rmsd_final,
    "rmsd_max_A": rmsd_max,
    "jax_backend": str(jax.default_backend()),
    "jax_version": jax.__version__,
    "so3lr_version": so3lr.__version__,
}

results_path = os.path.join(args.output_dir, f"so3lr_results_stage{args.stage}.json")
with open(results_path, 'w') as f:
    json.dump(results, f, indent=2)
logger.info(f"Results saved to: {results_path}")

# Save energy and temperature traces
traces_path = os.path.join(args.output_dir, f"so3lr_traces_stage{args.stage}.npz")
np.savez(traces_path,
         times_ps=times_ps,
         energies=energies,
         temperatures=temperatures)
logger.info(f"Traces saved to: {traces_path}")

# Save trajectory snapshots (sparse - every 10 cycles)
if len(positions_traj) > 0:
    traj_path = os.path.join(args.output_dir, f"so3lr_traj_stage{args.stage}.npz")
    np.savez(traj_path, positions=np.array(positions_traj))
    logger.info(f"Trajectory saved to: {traj_path}")

# ---- Summary ----
logger.info("=" * 60)
d1_pass = (not nan_detected and completed_time_ps >= 100.0)
logger.info(f"D1 GATE EVIDENCE: {'PASS' if d1_pass else 'FAIL'}")
logger.info(f"  Stable time: {completed_time_ps:.1f} ps (threshold: >= 100 ps)")
logger.info(f"  NaN detected: {nan_detected}")
logger.info(f"  Energy drift: {e_drift_per_atom:.8f} eV/ps/atom")
logger.info(f"  Temperature: {t_mean:.1f} +/- {t_std:.1f} K (target: {T_kelvin} K)")
logger.info(f"  RMSD final: {rmsd_final:.3f} A")
logger.info("=" * 60)

if d1_pass:
    logger.info("SO3LR D1 criterion MET: stable NVT trajectory achieved.")
else:
    logger.info("SO3LR D1 criterion NOT MET.")
    if nan_detected:
        logger.info("Reason: numerical instability (NaN)")
    elif completed_time_ps < 100.0:
        logger.info(f"Reason: only {completed_time_ps:.1f} ps completed (need >= 100 ps)")
