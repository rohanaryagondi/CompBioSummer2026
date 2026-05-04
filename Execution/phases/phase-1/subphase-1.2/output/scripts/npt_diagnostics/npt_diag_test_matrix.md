---
title: NPT Barostat Diagnostic Test Matrix
project: CompBioSummer2026 Sub 1.2 task-001
date: 2026-04-27
system: WW domain (residues 6-39), solvated TIP3P-FB, ~7595 atoms
production_failure: NaN at ~25 ps into NPT equilibration with MonteCarloBarostat freq=25
---

# NPT Barostat Diagnostic Test Matrix

## Problem Statement

The MACE-OFF24-medium hybrid NPT production script (`mace_hybrid_npt.py`) fails with
NaN at approximately 25 ps into equilibration. NVT with the same system runs perfectly
for 5 ns at 2.11 ns/day on H200 OpenCL. The failure is specific to NPT: adding a
MonteCarloBarostat triggers instability.

## Test Matrix

| Test | What Changes | dt (fs) | Barostat | Freq | MACE | Steps | ~SU | Purpose |
|------|-------------|---------|----------|------|------|-------|-----|---------|
| A | No MACE (classical only) | 1.0 | MCB isotropic | 25 | None | 30K | 3 | Isolate system build vs MACE |
| B | Barostat freq 100 | 1.0 | MCB isotropic | 100 | f32 | 30K | 5 | Less frequent volume moves |
| C | Barostat freq 500 | 1.0 | MCB isotropic | 500 | f32 | 30K | 5 | Very infrequent volume moves |
| D | Half timestep | 0.5 | MCB isotropic | 25 | f32 | 60K | 8 | Smaller steps through force spikes |
| E | Anisotropic barostat | 1.0 | MCAniso | 25 | f32 | 30K | 5 | One-axis-at-a-time rescaling |
| F | Float64 MACE | 1.0 | MCB isotropic | 25 | f64 | 30K | 6 | Precision loss during rescale |
| G | Combined best | 0.5 | MCB isotropic | 100 | f64 | 60K | 10 | Best-of-all combination |

**Total estimated SU: ~42** (budget: 50 SU)

MCB = MonteCarloBarostat. MCAniso = MonteCarloAnisotropicBarostat.

All tests run 30 ps of production (past the ~25 ps failure point) after 50 ps of
equilibration. The equilibration uses the same protocol as the production script.

## How to Run

### Single test

```bash
# From the npt_diagnostics directory:
./submit_all_diags.sh --test test_A_classical_npt
```

### All tests sequentially

```bash
./submit_all_diags.sh
```

### Dry run (see what would be submitted)

```bash
./submit_all_diags.sh --dry-run
```

### Check job status

```bash
# View the job registry
cat job_registry.json | python3 -m json.tool

# Check SLURM queue
squeue -u $USER --format="%.10i %.10j %.8T %.10M"
```

## Interpreting Results

Each test prints a clear PASS/FAIL summary at the end of its log file in
`npt_diagnostics/logs/`. Key metrics reported:

- **Temperature (K):** Should be 300 +/- 15 K
- **Density (g/cm3):** Should be ~0.99-1.01 g/cm3 for solvated protein
- **Potential Energy (kJ/mol):** Should be stable (not trending)
- **Max |Force| (kJ/mol/nm):** Should stay below 1e5; spikes above 1e8 trigger FAIL
- **Throughput (ns/day):** Informational for production planning

## Decision Tree

```
Test A (classical-only NPT)
  |
  +-- FAIL --> System build problem: solvation, box size, or ions are wrong.
  |            Fix the build before retesting MACE.
  |
  +-- PASS --> Barostat works classically. Problem is MACE + barostat interaction.
       |
       +-- Test B (freq=100)
       |    |
       |    +-- PASS --> Barostat frequency is the fix. Use freq=100 in production.
       |    |            Test C is unnecessary. Consider freq=50 as intermediate.
       |    |
       |    +-- FAIL --> Test C (freq=500)
       |         |
       |         +-- PASS --> Need very infrequent barostat. Use freq=500.
       |         |            Pressure equilibration slower but acceptable.
       |         |
       |         +-- FAIL --> Frequency alone is not the fix.
       |
       +-- Test D (dt=0.5 fs)
       |    |
       |    +-- PASS --> Timestep is the fix. 0.5 fs handles force spikes better.
       |    |            Production at 0.5 fs = ~1 ns/day (half throughput).
       |    |
       |    +-- FAIL --> Timestep alone is not enough.
       |
       +-- Test E (anisotropic barostat)
       |    |
       |    +-- PASS --> One-axis-at-a-time rescaling is more stable with MACE.
       |    |            Use MonteCarloAnisotropicBarostat in production.
       |    |
       |    +-- FAIL --> Barostat type is not the differentiator.
       |
       +-- Test F (f64 MACE)
       |    |
       |    +-- PASS --> f32 precision loss causes NaN during box rescale.
       |    |            Use f64 in production (accept ~20% throughput loss).
       |    |
       |    +-- FAIL --> Precision is not the issue.
       |
       +-- Test G (combined best: dt=0.5 + freq=100 + f64)
            |
            +-- PASS --> Multiple factors compound. Use combined settings.
            |            Throughput ~0.9 ns/day (acceptable for 5 ns pilots).
            |
            +-- FAIL --> NPT with MACE-OFF24 may be fundamentally unstable
                         for this system size/force field combination.
                         Fallback: NVT-only production (proven stable).
```

## Outcome Scenarios

### Best case: One setting fixes it (tests B, D, E, or F pass)
- Apply the single fix to production script
- Minimal throughput impact
- Proceed with NPT production on all 3 Tier B proteins

### Medium case: Combined settings needed (only G passes)
- Use dt=0.5 + freq=100 + f64 in production
- ~2.4x slower (~0.9 ns/day on H200)
- 5 ns takes ~5.5 days per protein instead of ~2.4 days
- Still feasible within Sub 1.2 timeline

### Worst case: All tests fail
- MACE-OFF24 NPT is unstable for this hybrid system
- Proceed with NVT-only production (proven stable at 2.11 ns/day)
- Write cross-agent note documenting NPT as infeasible
- Sub 1.4 production plan adjusts to NVT; observables are still valid
  (most dynamics observables do not require constant pressure)

## Wall Time Estimates

System build (PDBFixer + solvation + MACE hybrid construction): ~5-10 min
Minimization: ~1-2 min
50 ps equilibration at dt=1.0 fs: ~35-40 min on RTX 5000 Ada
50 ps equilibration at dt=0.5 fs: ~70-80 min on RTX 5000 Ada
30 ps production at dt=1.0 fs: ~20-25 min
30 ps production at dt=0.5 fs: ~40-50 min

Total per test: 60-90 min (within the 90 min SLURM walltime).
Test G (slowest) may approach the limit; the sbatch --time=01:30:00 provides margin.
