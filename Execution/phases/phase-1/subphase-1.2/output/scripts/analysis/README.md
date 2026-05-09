# Sub 1.4 Trajectory Analysis Skeletons

Status: **SKELETONS** (not yet executed). Item-H replacement, 2026-05-05.

## Purpose

Sub 1.4 will produce two trajectory families:

1. **MACE-OFF24 NPT 5 ns** trajectories (DCD/HDF5 + topology + StateDataReporter
   CSV log). Recipe locked in `shared/notes/1.2-mace-npt-fixed.md`.
2. **SO3LR vacuum NVT 5 ns** trajectories (SO3LR-CLI HDF5 + log + reference XYZ).
   Protocol in `shared/notes/1.2-so3lr-rescue-results.md`.

These skeletons fix the **API + I/O contract + method choices** so Sub 1.4
SubAgents only need to fill in the numerical bodies. Reference scripts:
`subphase-1.1/output/scripts/mace_analyze.py`, `so3lr_analyze.py`,
`task007_analyze.py`, and `subphase-1.2/output/scripts/features/compute_rmsf_batch1.py`.

## Module map

| File | What it does | Status |
|------|--------------|--------|
| `analyze_mace_npt.py` | Top-level MACE NPT analyzer (orchestrates S2 + RMSF + NPT QC + contacts) | Skeleton + RMSF body TBD |
| `analyze_so3lr_vacuum.py` | Top-level SO3LR vacuum NVT analyzer (Rg, RMSF, COM drift, NaN onset) | Skeleton + HDF5/topo loaders TBD |
| `S2_compute.py` | Lipari-Szabo S2 from N-H autocorrelation, block-bootstrap CIs | Skeleton; loaders + autocorrelation TBD |
| `density_T_P.py` | NPT QC from StateDataReporter CSV (T/P/density mean+std+drift) | **Fully implemented** |
| `contacts.py` | Cα contact-map evolution + Q-score per frame | Skeleton; CA loaders TBD |
| `__init__.py` | Package marker | Empty |

`density_T_P.py` parses logs and computes statistics with no I/O blockers — it
should run as-is on any Sub 1.4 MACE NPT log.

## Library dependencies

Skeletons assume `mdtraj` *or* `MDAnalysis` for trajectory loading; we prefer
**MDAnalysis** for consistency with `compute_rmsf_batch1.py`. Both libraries
are present in the project's analysis envs:

* `env-analysis` — login/CPU analysis (use this for batch S2/RMSF/contacts)
* `env-mace`     — has mdtraj available; use only if running on the same node
                   as the production trajectory write-out
* `env-so3lr`    — has h5py, jax, ase; use for SO3LR HDF5 reads if env-analysis
                   lacks h5py

Other packages: `numpy`, `h5py` (SO3LR HDF5), `matplotlib` optional (no
plotting code in these skeletons; downstream notebooks own that).

## I/O conventions

* **Trajectory inputs:** absolute paths via `--input-traj` and `--input-top`.
  MACE NPT: DCD/HDF5; SO3LR: HDF5.
* **Output files:** under `--output-dir`, one per protein, named
  `<protein_id>_<artifact>.<ext>`. Examples:
    * `WW_S2.npz`, `WW_S2_summary.json`
    * `GB3_rmsf.npz`, `GB3_rmsf.csv` (CSV mirrors `compute_rmsf_batch1.py`)
    * `ubq_npt_qc.json`, `ubq_contacts.npz`, `ubq_master_summary.json`
    * `NTL9_so3lr_qc.json`, `NTL9_rg.npz`, `NTL9_nan_onset.json`
* **Master summary:** each top-level analyzer writes
  `<protein_id>_master_summary.json` (MACE) or `<protein_id>_so3lr_qc.json`
  (SO3LR) — these are the single point of truth for downstream aggregation
  scripts and the OSF amendment.

## How Sub 1.4 SubAgents will use these

```
PYTHONNOUSERSITE=1 /home/rag88/.conda/envs/env-analysis/bin/python -m \
    output.scripts.analysis.analyze_mace_npt \
    --input-traj /scratch/.../mace_ww_npt.dcd \
    --input-top  /scratch/.../mace_ww_top.pdb \
    --input-log  /scratch/.../mace_ww_npt.log \
    --output-dir /home/.../subphase-1.4/output/analysis \
    --protein-id WW \
    --reference  /home/.../inputs/ww_native.pdb
```

The same pattern for SO3LR; the runners are independent and can be invoked
in parallel per-protein on login or short-CPU nodes.

## What Sub 1.4 must implement

Search the source for `NotImplementedError`. Expected bodies:

* `S2_compute._load_nh_vectors`, `_autocorrelation_s2` (mdtraj or manual P2 ACF)
* `contacts._load_ca_positions`, `_load_reference_ca` (mdtraj/MDAnalysis)
* `analyze_mace_npt.compute_rmsf` (mirror `compute_rmsf_batch1.py:99-138`)
* `analyze_so3lr_vacuum.load_so3lr_hdf5`, `parse_so3lr_log`, `compute_ca_rmsf`,
  `load_topology_metadata` (reuse so3lr_analyze patterns + add Kabsch alignment
  for RMSF)

References for S2:
- Lipari & Szabo, JACS 1982 — model-free formalism
- Smith / Lai & Brooks, JPCB 2024 — convergence on short trajectories
- `Proposal/Alpha-M.md` §S2 — table row "S2 order parameters: Lipari-Szabo
  from trajectory autocorrelation (iRED)"

iRED (Prompers & Bruschweiler) is the rigorous extension that handles
anisotropic tumbling — defer to Sub 1.5 if needed; current skeleton assumes
isotropic tumbling has been removed by alignment (caveat documented in
`S2_compute.py` docstring).

## Token / line budget

All 7 files total ~1100 LOC; each Python module under 250 LOC. No production
script was modified; no SLURM job submitted; no env was touched.
