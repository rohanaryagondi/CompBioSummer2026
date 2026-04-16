---
task_id: "task-002"
gate: "D1"
agent: "so3lr-pilot"
verdict: PASS
date: 2026-04-16
---

# D1 Gate Evidence: SO3LR Crambin NVT Simulation

## Verdict: PASS

SO3LR v0.1.0 successfully ran a stable 100 ps NVT trajectory on crambin (640 atoms)
in vacuum at 300 K. The D1 minimum criterion (100 ps stable) is met. A 1 ns (Stage B)
continuation run is in progress and expected to complete successfully based on the
stability demonstrated in Stage A.

## Software Versions

| Component | Version |
|-----------|---------|
| SO3LR | 0.1.0 |
| JAX | 0.5.3 |
| JAX-MD | 0.2.27 (bundled with so3lr) |
| Python | 3.12.13 |
| CUDA | 12.8 |
| GPU | NVIDIA RTX 5000 Ada Generation (32 GB) |

## System Details

- **Protein:** Crambin (46 residues, 640 atoms with explicit H, C202H313N55O64S6)
- **Input:** `crambin_h_vacuum.xyz` (XYZ format with explicit hydrogens added by prior agent)
- **Boundary conditions:** Free (vacuum), `space.free()`, no periodic boundary conditions
- **Interface used:** SO3LR CLI (`so3lr nvt ...`), NOT the programmatic JAX-MD interface
- **Conda environment:** `env-so3lr`

## Simulation Parameters

| Parameter | Value |
|-----------|-------|
| Timestep (dt) | 0.5 fs |
| Temperature | 300 K |
| Thermostat | Nose-Hoover Chain (NHC) |
| NHC chain length | 3 |
| NHC integration steps | 2 |
| NHC damping time | 50.0 fs |
| Precision | float32 |
| Long-range cutoff | 12.0 A |
| Dispersion damping | 2.0 A |
| SR/LR buffer | 1.25 |
| Random seed | 42 |

## Stage Results

### Stage A: 100 ps NVT (D1 minimum -- PASS)

- **SLURM job:** 8394754 (gpu_devel partition, RTX 5000 Ada)
- **Setup:** 200 MD cycles x 1000 steps/cycle x 0.5 fs/step = 100 ps
- **Geometry relaxation:** Converged at 140 steps (Fmax = 0.042 eV/A)
- **MD runtime:** 651.07 seconds (10.85 minutes)
- **Average time/step:** 2.93 ms (vs theoretical 2.08 ms on A100)
- **Exit code:** 0 (success)
- **NaN detected:** None

**Energy and temperature summary (200 data points from Stage A log):**

| Quantity | First cycle | Last cycle | Mean | Std | Notes |
|----------|-------------|------------|------|-----|-------|
| Epot (eV) | -1155.26 | -1135.75 | ~-1134.3 | ~1.2 | PE evolving as expected for NVT vacuum |
| Ekin (eV) | 24.34 | 24.46 | ~24.7 | ~0.8 | Normal fluctuations |
| Etot (eV) | -1130.93 | -1111.29 | - | - | System energy (E=KE+PE) |
| H (eV) | -1130.93 | -1129.44 | - | - | NHC Hamiltonian (conserved quantity) |
| T (K) | 294.2 | 295.6 | ~300 | ~10 | Target 300 K well maintained |

**Hamiltonian drift:** ~1.5 eV over 100 ps = 15 meV/ps (acceptable for NVT with NHC in float32)

**Temperature range:** 268-327 K around target 300 K (expected for 640 atoms with NHC thermostat)

### Quick Test: 10 ps NVT (validation -- PASS)

- **SLURM job:** 8394378 (gpu_devel, RTX 5000 Ada)
- **Setup:** 20 cycles x 1000 steps x 0.5 fs = 10 ps
- **MD runtime:** 120.30 seconds total (including JIT + relaxation)
- **Average time/step:** 2.90 ms
- **Exit code:** 0 (success)

### Stage B: 1 ns NVT (D1 target -- IN PROGRESS)

- **SLURM job:** 8394754 (continuation within same job)
- **Setup:** 1800 cycles x 1000 steps x 0.5 fs = 900 ps (plus 100 ps from Stage A = 1 ns total)
- **Restart:** Loading from `stageA_checkpoint.npz`
- **Expected runtime:** ~88 minutes
- **Status:** Running (started 2026-04-16T06:18:44Z)

## JIT Compilation Performance

| Phase | JIT Time | Notes |
|-------|----------|-------|
| First energy evaluation (minimizer) | ~30 s | One-time cost |
| First NVT cycle | ~10 s | One-time cost for NVT loop |
| Subsequent MD cycles | 2.9 ms/step | Production speed |

## Prior Failure Resolution

A prior agent attempted this task using the programmatic JAX-MD interface (custom
`so3lr_crambin_nvt.py` script) and failed due to:

1. Shape broadcasting bugs in custom code (species/masses arrays)
2. NaN detection in positions (likely from bad initialization without relaxation)
3. Missing numpy on compute nodes (user site-packages not in PYTHONPATH)

**Resolution:** Used the SO3LR CLI (`so3lr nvt`) instead of writing custom JAX-MD
code. The CLI handles neighbor lists, thermostat setup, JIT compilation, and
checkpoint saving internally, avoiding the shape broadcasting issues. Also installed
numpy into the conda environment's site-packages and set PYTHONPATH explicitly in
the SLURM script.

## Key Observations for Alpha-M Track

1. **CLI is the recommended interface** for SO3LR production runs. The programmatic
   JAX-MD interface requires careful handling of species arrays, masses, neighbor
   list allocation, and energy function signatures.

2. **Geometry relaxation before MD is essential.** The `--relax` flag converges the
   structure to Fmax < 0.05 eV/A in ~140 steps. Without relaxation, the raw PDB
   structure can produce NaN in the first few MD steps.

3. **Performance on RTX 5000 Ada:** 2.9 ms/step for 640 atoms. Extrapolating:
   - 1 ns crambin: ~1.5 hours
   - 10 ns crambin: ~15 hours
   - Larger proteins will scale with neighbor list size

4. **Vacuum-only simulations.** SO3LR does not have implicit or explicit solvent
   built in for non-periodic systems. Crambin in vacuum is the correct test case.

5. **float32 is sufficient** for stable 100+ ps trajectories. float64 would reduce
   Hamiltonian drift but is not needed for D1 evidence.

## Output Files

| File | Path | Size |
|------|------|------|
| Stage A trajectory | `/nfs/roberts/scratch/pi_mg269/rag88/alpha-m/so3lr-crambin/stageA.hdf5` | 2.87 MB |
| Stage A checkpoint | `/nfs/roberts/scratch/pi_mg269/rag88/alpha-m/so3lr-crambin/stageA_checkpoint.npz` | 29 KB |
| Stage A log | `/nfs/roberts/scratch/pi_mg269/rag88/alpha-m/so3lr-crambin/stageA.log` | 25 KB |
| Stage A optimized structure | `/nfs/roberts/scratch/pi_mg269/rag88/alpha-m/so3lr-crambin/stageA_opt.xyz` | 994 KB |
| Stage B trajectory | `/nfs/roberts/scratch/pi_mg269/rag88/alpha-m/so3lr-crambin/stageB.hdf5` | (growing) |
| Stage B log | `/nfs/roberts/scratch/pi_mg269/rag88/alpha-m/so3lr-crambin/stageB.log` | (growing) |
| SLURM output | `output/so3lr_cli_8394754.out` | - |
| SLURM errors | `output/so3lr_cli_8394754.err` | - |
| SLURM script | `output/scripts/so3lr_crambin_cli.sbatch` | - |
| Analysis script | `output/scripts/so3lr_analyze.py` | - |
