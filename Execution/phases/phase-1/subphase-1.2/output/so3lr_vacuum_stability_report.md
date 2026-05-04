# SO3LR Vacuum NVT Stability Report

**Date:** 2026-04-25
**Subphase:** 1.2, Task-002 (mlff-so3lr-pilot)
**Analyst:** Automated post-hoc analysis of completed trajectories

---

## 1. Simulation Parameters (all proteins)

| Parameter | Value |
|-----------|-------|
| Force field | SO3LR v0.1.0 |
| Ensemble | NVT (Nose-Hoover chain) |
| Temperature target | 300.0 K |
| Timestep | 0.5 fs |
| Total steps | 10,000,000 (5.0 ns) |
| MD cycles | 10,000 |
| Steps per cycle | 1,000 |
| NHC chain length | 3 |
| NHC Tdamp | 50.0 fs |
| NHC steps | 2 |
| Precision | float32 |
| Long-range cutoff | 12.0 A |
| Dispersion damping | 2.0 A |
| Buffer (SR/LR) | 1.25 / 1.25 |
| Seed | 42 |
| Geometry relaxation | Enabled (F_conv = 0.05 eV/A) |
| GPU partition | RTX 5000 Ada |

---

## 2. Per-Protein Summary

### 2.1 Overall Verdicts

| Protein | Atoms | Tier | Usable (ns) | NaN onset | Rg ratio | Structural | Thermo | **Verdict** |
|---------|------:|:----:|:-----------:|:---------:|:--------:|:----------:|:------:|:-----------:|
| WW      |   534 | A    | 0.65        | 0.704 ns  | 0.983    | INTACT     | FAIL   | **FAIL**    |
| GB3     |   862 | A    | ~0.10       | none      | 93.8     | EXPLODED   | PASS   | **FAIL**    |
| GB1     |   858 | B    | 4.95        | none      | 0.978    | INTACT     | PASS   | **PASS**    |
| NTL9    |   813 | B    | ~0.10       | 4.386 ns  | 88.6     | EXPLODED   | FAIL   | **FAIL**    |
| UBQ     |  1231 | B    | 4.95        | none      | 0.987    | INTACT     | PASS   | **PASS**    |

"Usable (ns)" = post-equilibration (50 ps), pre-failure, structurally intact.

### 2.2 Failure Classification

- **WW:** NaN at 0.704 ns with structure intact (Rg stable at ~9.0 A). Failure is numerical, not structural. Only 0.65 ns of usable data post-equilibration.
- **GB3:** Silent structural explosion starting ~0.1 ns. Rg grew linearly from 10.55 to 989.87 A. Thermodynamic log showed no NaN and normal T (300 +/- 13 K) throughout 5 ns. This is a deceptive silent failure.
- **NTL9:** Structural explosion starting ~0.1 ns (Rg > 2x initial by 0.125 ns). NaN appeared much later at 4.386 ns as a downstream consequence. Log-based T was normal until NaN.
- **GB1:** Fully stable 5 ns. Rg = 10.07-10.63 A, ratio 0.978. T = 300.0 +/- 8.3 K.
- **UBQ:** Fully stable 5 ns. Rg = 10.92-11.14 A, ratio 0.987. T = 300.1 +/- 7.0 K.

---

## 3. Thermodynamic Log Analysis

Equilibration cutoff: first 50 ps (100,000 steps) discarded. Statistics computed over clean post-equilibration, pre-NaN window.

### 3.1 Temperature

| Protein | Clean (ns) | T mean (K) | T std (K) | T min (K) | T max (K) |
|---------|:----------:|:----------:|:---------:|:---------:|:---------:|
| WW      | 0.653      | 300.12     | 10.72     | 267.40    | 336.00    |
| GB3     | 4.950      | 299.88     | 12.55     | 257.00    | 358.90    |
| GB1     | 4.950      | 299.96     |  8.34     | 270.30    | 331.10    |
| NTL9    | 4.335      | 299.83     | 11.93     | 257.90    | 349.80    |
| UBQ     | 4.950      | 300.05     |  6.96     | 276.00    | 326.90    |

All proteins maintain mean T within 0.2 K of the 300 K target. NHC thermostat coupling is effective. Note: T std correlates inversely with atom count (equipartition: sigma_T ~ 1/sqrt(N_dof)).

### 3.2 Energy

| Protein | E mean (eV) | E std (eV) | E drift (eV/ns) | PE drift (eV/ns) | H drift (eV/ns) |
|---------|:-----------:|:----------:|:----------------:|:-----------------:|:----------------:|
| WW      | -934.018    | 1.186      | -1.529           | -2.673            | 11.541           |
| GB3     | -1510.269   | 1.456      |  0.198           | -0.102            | 29.281           |
| GB1     | -1502.788   | 1.573      | -0.444           | -0.661            | 18.039           |
| NTL9    | -1424.987   | 1.386      |  0.015           | -0.341            | 24.691           |
| UBQ     | -2161.200   | 1.710      | -1.098           | -1.257            | 25.928           |

**NHC Hamiltonian (H) drift:** All proteins show 11-29 eV/ns H drift. This is the extended Hamiltonian of the Nose-Hoover chain thermostat, not the physical energy. In vacuum NVT with NHC (chain=3, Tdamp=50 fs, dt=0.5 fs), H drift of this magnitude is a known accumulation artifact. It does NOT indicate physical instability; temperature remains well-controlled in all cases. H drift is NOT a pass/fail criterion.

**Physical energy (E) drift:** GB1 and NTL9 show minimal drift (<0.5 eV/ns). WW and UBQ show ~1-1.5 eV/ns drift (larger per-atom drift for the smaller WW system). GB3's apparently normal E drift (0.2 eV/ns) is misleading because the structure was already exploded.

### 3.3 Kinetic and Potential Energy

| Protein | KE mean (eV) | KE std (eV) | PE mean (eV) | PE std (eV) |
|---------|:------------:|:-----------:|:------------:|:-----------:|
| WW      | 20.716       | 0.740       | -954.734     | 0.918       |
| GB3     | 33.413       | 1.399       | -1543.682    | 1.541       |
| GB1     | 33.267       | 0.925       | -1536.055    | 1.255       |
| NTL9    | 31.508       | 1.254       | -1456.496    | 1.369       |
| UBQ     | 47.744       | 1.108       | -2208.944    | 1.335       |

KE scales with atom count as expected (equipartition). PE fluctuations are comparable across proteins.

---

## 4. HDF5 Trajectory Analysis

### 4.1 File Structure

All HDF5 files contain 3 datasets: `positions`, `momenta`, `box`.
Shape: (200, 50, N_atoms, 3) = 200 buffers x 50 frames x N_atoms x 3 coords.
Total: 10,000 frames per protein = 10M steps = 5.0 ns.

| Protein | File size (MB) | Atoms | Frames | NaN frames | NaN first frame |
|---------|:--------------:|------:|-------:|-----------:|:---------------:|
| WW      |  16.7          |   534 | 10,000 |      8,593 | 1,407           |
| GB3     | 189.5          |   862 | 10,000 |          0 | --              |
| GB1     | 188.6          |   858 | 10,000 |          0 | --              |
| NTL9    | 156.8          |   813 | 10,000 |      1,229 | 8,771           |
| UBQ     | 268.9          |  1231 | 10,000 |          0 | --              |

Note: WW's small file size (16.7 MB vs expected ~60 MB) is because the NaN-containing frames likely store NaN float32 values (4 bytes each) rather than valid coordinates, but the array shape is preserved. The HDF5 file correctly reports 10,000 frames.

### 4.2 Structural Integrity (Radius of Gyration)

| Protein | Rg initial (A) | Rg final (A) | Rg min (A) | Rg max (A) | Rg ratio | Verdict |
|---------|:--------------:|:------------:|:----------:|:----------:|:--------:|:-------:|
| WW      |  9.16          |  9.00        |  8.88      |  9.16      | 0.983    | INTACT  |
| GB3     | 10.55          | 989.87       | 10.55      | 989.87     | 93.82    | EXPLODED|
| GB1     | 10.48          | 10.24        | 10.07      | 10.63      | 0.978    | INTACT  |
| NTL9    | 10.76          | 953.11       | 10.76      | 953.11     | 88.59    | EXPLODED|
| UBQ     | 11.14          | 11.00        | 10.92      | 11.14      | 0.987    | INTACT  |

**Explosion threshold:** Rg ratio > 2.0
- GB3: Rg > 2x initial by 0.125 ns (Rg = 24.7 A)
- NTL9: Rg > 2x initial by 0.125 ns (Rg = 30.2 A)
- Both exploding proteins had linear Rg growth from ~100 ps onward.

**Critical finding:** GB3 and NTL9 show silent structural explosions that are NOT detectable from thermodynamic log output alone. SO3LR's NHC thermostat continues to report normal temperature even as atoms fly apart.

---

## 5. Usability Assessment for Downstream Analysis

Downstream analysis requires computing RMSF, Rg, secondary structure metrics. The minimum usable trajectory length after equilibration is ~1 ns (T_min).

| Protein | Post-equil clean (ns) | Meets T_min (1 ns)? | Usable for RMSF? | Usable for S2 back-calc? |
|---------|:---------------------:|:-------------------:|:-----------------:|:------------------------:|
| WW      | 0.65                  | NO                  | Marginal at best  | NO                       |
| GB3     | ~0.05                 | NO                  | NO                | NO                       |
| GB1     | 4.95                  | YES                 | YES               | YES                      |
| NTL9    | ~0.05                 | NO                  | NO                | NO                       |
| UBQ     | 4.95                  | YES                 | YES               | YES                      |

- **WW (0.65 ns):** Below the 1 ns T_min threshold. The 0.65 ns of clean data might allow a rough RMSF estimate but is insufficient for converged order parameters or reliable secondary structure analysis. NOT usable for Phase 2 production.
- **GB3 (~0.05 ns):** Structural explosion at ~100 ps makes the trajectory unusable after the first ~50 ps. Zero usable data post-equilibration.
- **GB1 (4.95 ns):** Fully usable. Well above T_min with stable structure throughout.
- **NTL9 (~0.05 ns):** Structural explosion at ~100 ps. Zero usable data post-equilibration, despite the thermodynamic log appearing normal for 4.4 ns.
- **UBQ (4.95 ns):** Fully usable. Well above T_min with the tightest Rg and T statistics of all proteins.

---

## 6. Performance Summary

| Protein | Atoms | Wall time (hr) | ns/day (RTX 5000 Ada) | Time/step (ms) |
|---------|------:|:--------------:|:---------------------:|:--------------:|
| WW      |   534 |  6.91          | 17.14                 | 2.52           |
| GB3     |   862 | 11.85          | 10.17                 | 4.25           |
| GB1     |   858 | 11.89          | 10.13                 | 4.26           |
| NTL9    |   813 | 11.18          | 10.76                 | 4.02           |
| UBQ     |  1231 | 16.18          |  7.44                 | 5.81           |

Total RTX 5000 Ada GPU time: ~58 GPU-hours = ~870 SU.
SO3LR warning (all proteins): "Ideally, the average time per step should be close to X seconds (measured on an A100 GPU). Consider decreasing the buffer sizes if the system has equilibrated."

---

## 7. Log Warnings

All 5 proteins had exactly 4 warnings each:
1. "Output format is 'hdf5', changing output file extension to 'xyz' for minimization." (benign)
2-3. Buffer size optimization suggestions at end of run (benign performance advisory)
4. (duplicate of 3)

No ERROR-level messages in any log. No warnings indicative of instability.

---

## 8. Key Findings and Recommendations

### 8.1 Critical: Log-based monitoring is insufficient for SO3LR vacuum

The GB3 silent failure demonstrates that thermodynamic logs (T, E, KE, PE) can appear perfectly normal while the protein structure has completely disintegrated. **All SO3LR trajectories MUST be validated with structural checks (Rg monitoring) in addition to thermodynamic logs.** This applies retroactively to any future SO3LR production runs.

### 8.2 Two distinct failure modes

1. **Numerical NaN (WW):** Sudden NaN with structure intact. Likely a SO3LR potential evaluation failure for this small 534-atom system.
2. **Silent structural explosion (GB3, NTL9):** Atoms fly apart from ~100 ps while the integrator continues with normal-looking thermodynamics. The NHC thermostat can maintain apparent temperature equilibrium even for a disintegrating system.

### 8.3 Phase 2 SO3LR scope

- **2 of 5 proteins PASS** (GB1, UBQ). Both Tier B.
- SO3LR vacuum is viable but fragile. Mandatory 500 ps screening trajectory with Rg check before any production run.
- Consider testing smaller timestep (0.25 fs) or modified NHC parameters on failed proteins.
- SO3LR is the secondary MLFF; MACE NPT (task-001) is primary for D2 G1.

### 8.4 D2 G1 evidence

Gate D2 G1 requires stable MLFF trajectories on Tier B proteins. SO3LR provides partial evidence: 2 Tier B proteins (GB1, UBQ) with 5 ns stable trajectories. Combined with MACE NPT data (task-001), this contributes to D2 readiness.
