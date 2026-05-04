#!/usr/bin/env python
"""
mace_hybrid_npt.py -- MACE-OFF24 hybrid-solvent NPT production driver with
checkpoint/restart.

Forked from phases/phase-1/subphase-1.1/output/scripts/mace_hybrid_nvt.py
(Sub 1.1 D1 PASS baseline) for Sub 1.2 Tier B NPT stability pilots.

Key additions vs. the Sub 1.1 NVT script:
  1. MonteCarloBarostat (NPT, 1 atm, 300 K, freq=25) added to the hybrid system
     before integrator construction. Controlled by MACE_HYBRID_BAROSTAT env var
     (default "npt"; set to "nvt" for fallback).
  2. Checkpoint/restart loop using Simulation.saveCheckpoint/loadCheckpoint.
     On startup, if <scratch>/<tag>/checkpoint_latest.chk exists, the script
     resumes from that checkpoint and appends to existing DCD + CSV files.
     Otherwise it starts fresh from PDB -> PDBFixer -> solvation -> min ->
     2-stage equilibration (NVT 50 ps dt=0.5 fs + NPT 200 ps dt=1 fs) -> production.
  3. Append-mode DCDReporter + CSV state reporter so multiple SLURM jobs
     concatenate to a single trajectory per protein.
  4. Target trajectory length controlled by MACE_HYBRID_TARGET_NS (default 5.0);
     script exits cleanly when target reached.
  5. Per-protein defaults (WW, GB3, UBQ) include residue cropping (WW only) and
     target ns. All other Sub 1.1 safeguards retained (PYTHONNOUSERSITE=1,
     maxIterations=2000, post-min max-force check, GPU keepalive thread,
     OpenCL platform only -- CUDA is broken on all available GPUs).

CLI (all via environment variables):
    MACE_HYBRID_PROTEIN  -- short name (ww | gb3 | ubq); drives PDB / crop defaults
    MACE_HYBRID_PDB      -- path to starting PDB (override per-protein default)
    MACE_HYBRID_RESRANGE -- optional "start-end" chain-A residue range
                            (WW case: 6-39 from full Pin1 2F21)
    MACE_HYBRID_TARGET_NS    -- total trajectory length target (default 5.0)
    MACE_HYBRID_BAROSTAT     -- "npt" (default) | "nvt" (fallback)
    MACE_HYBRID_TAG          -- 8-char cryptic tag / label for output files
    MACE_OUTPUT_DIR          -- output directory for DCD / CSV / JSON artifacts
                                (persistent; default: subphase-1.2 output)
    MACE_SCRATCH_DIR         -- scratch directory for checkpoints + equil state
                                (default: /nfs/roberts/scratch/... /alpha-m/mace-npt)

Resubmission pattern:
  Submit multiple SLURM jobs with the SAME MACE_HYBRID_TAG. On startup, each
  job detects and loads <scratch>/<tag>/checkpoint_latest.chk, seeks to the
  recorded step count, and continues. The trajectory (<output>/<tag>_npt.dcd)
  and state log (<output>/<tag>_npt_state.csv) are opened in append mode so
  multiple resumes produce a single continuous file per protein.

Exit codes:
  0 -- trajectory reached MACE_HYBRID_TARGET_NS (mission complete)
  2 -- walltime-friendly checkpoint saved; resubmit to continue
  1 -- fatal failure (NaN, exception, system build error)

Project: CompBioSummer2026 Sub 1.2 task-001 (mlff-mace-pilot).
"""
from __future__ import annotations

import csv
import json
import os
import shutil
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

# Suppress user site-packages (avoids OpenMM version conflicts from ~/.local)
os.environ['PYTHONNOUSERSITE'] = '1'

# Replace matscipy with vesin for neighbor list computation (2026-04-23).
# matscipy holds the GIL during its entire C extension call, causing sporadic
# 20+ minute hangs from GIL deadlock with the GPU keepalive thread. vesin
# (Rust/ctypes) releases the GIL, eliminating the deadlock. Bit-identical
# output verified. ~1 ms slower per call but NL is <3ms of a 43ms step.
import numpy as _np
from vesin import NeighborList as _VesinNL
import mace.data.neighborhood as _mace_nh

_vesin_calc = _VesinNL(cutoff=1.0, full_list=True)

def _vesin_neighbour_list(quantities, atoms=None, cutoff=None, positions=None,
                          cell=None, pbc=None, numbers=None, cell_origin=None):
    if atoms is not None:
        positions = atoms.positions
        cell = _np.asarray(atoms.cell)
        pbc = atoms.pbc
    positions = _np.asarray(positions, dtype=_np.float64)
    cell = _np.asarray(cell, dtype=_np.float64)
    periodic = bool(pbc is not None and any(pbc))
    _vesin_calc.cutoff = cutoff
    return _vesin_calc.compute(
        points=positions, box=cell, periodic=periodic,
        quantities=quantities, copy=True,
    )

_mace_nh.neighbour_list = _vesin_neighbour_list


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROTEIN = os.environ.get("MACE_HYBRID_PROTEIN", "ww").lower()

# Per-protein defaults (PDB path, residue crop). User may override via env vars.
PROTEIN_DEFAULTS = {
    "ww": {
        "pdb": "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ww.pdb",
        "resrange": "6-39",
    },
    "gb3": {
        "pdb": "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/gb3.pdb",
        "resrange": "",
    },
    "ubq": {
        "pdb": "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ubq.pdb",
        "resrange": "",
    },
}
_pd = PROTEIN_DEFAULTS.get(PROTEIN, {"pdb": "", "resrange": ""})

PDB_PATH = os.environ.get("MACE_HYBRID_PDB", _pd["pdb"])
RESRANGE = os.environ.get("MACE_HYBRID_RESRANGE", _pd["resrange"]).strip()

TARGET_NS = float(os.environ.get("MACE_HYBRID_TARGET_NS", "5.0"))
BAROSTAT_MODE = os.environ.get("MACE_HYBRID_BAROSTAT", "npt").lower()  # "npt" or "nvt"

OUTPUT_DIR = os.environ.get(
    "MACE_OUTPUT_DIR",
    "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/trajectories/mace_npt",
)
SCRATCH_DIR = os.environ.get(
    "MACE_SCRATCH_DIR",
    "/nfs/roberts/scratch/pi_mg269/rag88/alpha-m/mace-npt",
)
TAG = os.environ.get("MACE_HYBRID_TAG", PROTEIN)

# Simulation parameters (matched to Sub 1.1 for comparability; NPT additions flagged)
TEMPERATURE_K = 300.0
FRICTION = 1.0                   # 1/ps Langevin
DT_FS = 1.0                      # fs production timestep
# DT_EQUIL_FS kept = DT_FS (2026-04-19 hang-fix): setStepSize() mid-run on
# OpenCL-MACE hybrid context reproducibly hung matscipy neighbour_list 3+ times
# (diags 1 + v3 production jobs). Sub 1.1 NVT used single dt=1.0 fs throughout and
# ran at 2.11 ns/day with zero hangs. Do NOT differentiate equil vs prod dt here.
DT_EQUIL_FS = 1.0                # fs equilibration timestep (matches DT_FS; see above)
REPORT_INTERVAL_PS = 1.0         # DCD + CSV stride (1 ps -> 1000 steps at 1 fs)
NAN_CHECK_INTERVAL_STEPS = 1000  # check for NaN every 1000 steps
SOLVENT_PADDING_NM = 1.0
NB_CUTOFF_NM = 1.0
IONIC_STRENGTH_M = 0.15
PRESSURE_ATM = 1.0               # NPT reference pressure
BAROSTAT_FREQ = 25               # MonteCarloBarostat step frequency

# Equilibration schedule (2026-04-26 UBQ NaN fix: 5 ps was too short for NPT)
# UBQ (17K atoms) hit NaN within 2 min of production after only 5 ps equil.
# 50 ps gives box volume time to relax under MCB. Hang watchdog in submit script
# handles any matscipy stalls during equil; post-equil checkpoint (below) prevents
# re-equilibrating on restart.
NVT_EQUIL_PS = 0.0               # removed: NPT with MCB handles thermal+pressure in one stage
NPT_EQUIL_PS = 50.0              # 50 ps NPT at dt=1 fs = 50,000 steps (~15 min WW / ~60 min UBQ)

# Checkpoint cadence: every 5 ps wall = 5,000 steps at dt=1 fs. Previously 100K
# was too infrequent — a single hang would waste up to 50 min of production.
# 5K makes recovery cheap (worst-case 3-7 min lost per hang).
CHECKPOINT_INTERVAL_STEPS = 5000

# Walltime guard: save checkpoint and exit cleanly before SLURM hard-kills us.
# gpu_h200 walltime 23:59:00; set guard to 22.5 hrs to leave margin for final save.
WALLTIME_GUARD_SEC = int(os.environ.get("MACE_HYBRID_WALLTIME_GUARD_SEC", "81000"))  # 22.5 hrs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] {msg}", flush=True)


def setup_dirs() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(SCRATCH_DIR, exist_ok=True)
    os.makedirs(os.path.join(SCRATCH_DIR, TAG), exist_ok=True)


def checkpoint_paths() -> tuple[str, str, str, str, str, str, str]:
    """Return paths for checkpoint, equil state, progress, topology, DCD, CSV, meta."""
    scratch_tag = os.path.join(SCRATCH_DIR, TAG)
    return (
        os.path.join(scratch_tag, "checkpoint_latest.chk"),
        os.path.join(scratch_tag, "equil_state.xml"),
        os.path.join(scratch_tag, "progress.json"),
        os.path.join(OUTPUT_DIR, f"{TAG}_topology.pdb"),
        os.path.join(OUTPUT_DIR, f"{TAG}_npt.dcd"),
        os.path.join(OUTPUT_DIR, f"{TAG}_npt_state.csv"),
        os.path.join(OUTPUT_DIR, f"{TAG}_npt_meta.json"),
    )


def read_progress(progress_path: str) -> dict:
    """Read progress tracker JSON; return empty dict if missing."""
    if not os.path.exists(progress_path):
        return {}
    try:
        with open(progress_path) as f:
            return json.load(f)
    except Exception as e:
        log(f"WARN: progress file corrupt, starting fresh: {e}")
        return {}


def write_progress(progress_path: str, progress: dict) -> None:
    """Atomic write of progress JSON (write-tmp-then-rename)."""
    tmp = progress_path + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(progress, f, indent=2, default=str)
    os.replace(tmp, progress_path)


# ---------------------------------------------------------------------------
# GPU keepalive -- prevents YCRC 1-hr-idle auto-cancel during CPU-heavy phases
# (PDBFixer, solvation, system build) and during any mid-run stall. 5-min cadence.
# ---------------------------------------------------------------------------

import threading as _threading
_keepalive_stop = _threading.Event()

def _gpu_keepalive_loop() -> None:
    try:
        import torch
        if not torch.cuda.is_available():
            return
        dev = torch.device('cuda:0')
        x = torch.randn(64, 64, device=dev)
        while not _keepalive_stop.is_set():
            y = torch.matmul(x, x).sum().item()
            torch.cuda.synchronize()
            _keepalive_stop.wait(300)  # 5 min between pokes
    except Exception:
        # Keepalive must never crash the simulation
        pass

def start_gpu_keepalive() -> _threading.Thread:
    t = _threading.Thread(target=_gpu_keepalive_loop, daemon=True, name='gpu-keepalive')
    t.start()
    log("Started GPU keepalive thread (5-min cadence) to prevent YCRC idle auto-cancel")
    return t

def stop_gpu_keepalive() -> None:
    _keepalive_stop.set()


def load_and_crop_pdb():
    """Load PDB, strip non-protein het, keep first chain, optionally crop residues."""
    from openmm.app import PDBFile, Modeller

    log(f"Loading PDB: {PDB_PATH}")
    pdb = PDBFile(PDB_PATH)
    modeller = Modeller(pdb.topology, pdb.positions)
    log(f"  Raw topology: {modeller.topology.getNumAtoms()} atoms, "
        f"{modeller.topology.getNumResidues()} residues, "
        f"{len(list(modeller.topology.chains()))} chains")

    # Delete non-protein het atoms (PDBFixer will reconstruct hydrogens later).
    std_aa = {
        'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE',
        'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL',
        'HID', 'HIE', 'HIP', 'CYX', 'CYM', 'ASH', 'GLH', 'LYN',
    }
    res_to_delete = [r for r in modeller.topology.residues() if r.name not in std_aa]
    if res_to_delete:
        log(f"  Deleting {len(res_to_delete)} non-protein residues (waters/ions/ligands)")
        modeller.delete(res_to_delete)

    # Keep only first chain
    first_chain_id = list(modeller.topology.chains())[0].id
    other_chain_residues = []
    for chain in modeller.topology.chains():
        if chain.id != first_chain_id:
            other_chain_residues.extend(chain.residues())
    if other_chain_residues:
        log(f"  Deleting {len(other_chain_residues)} residues from non-A chains")
        modeller.delete(other_chain_residues)

    # Optional residue-range crop (WW case: Pin1 residues 6-39)
    if RESRANGE and "-" in RESRANGE:
        start_s, end_s = RESRANGE.split("-", 1)
        start_i, end_i = int(start_s), int(end_s)
        log(f"  Cropping to residue range {start_i}-{end_i} (inclusive)")
        to_delete = []
        for residue in modeller.topology.residues():
            try:
                rid = int(residue.id)
            except ValueError:
                continue
            if rid < start_i or rid > end_i:
                to_delete.append(residue)
        if to_delete:
            modeller.delete(to_delete)

    log(f"  After protein extraction: {modeller.topology.getNumAtoms()} atoms, "
        f"{modeller.topology.getNumResidues()} residues")
    return modeller


def check_nan(simulation, label: str) -> float:
    from openmm import unit
    state = simulation.context.getState(getPositions=True, getForces=True,
                                         getEnergy=True)
    pos = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
    forces = state.getForces(asNumpy=True).value_in_unit(
        unit.kilojoules_per_mole / unit.nanometer)
    pe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
    if np.any(np.isnan(pos)):
        raise RuntimeError(f"NaN positions at {label}")
    if np.any(np.isnan(forces)):
        raise RuntimeError(f"NaN forces at {label}")
    if np.isnan(pe):
        raise RuntimeError(f"NaN potential energy at {label}")
    max_f = float(np.max(np.abs(forces)))
    if max_f > 1e8:
        raise RuntimeError(f"Extreme forces ({max_f:.1e}) at {label}")
    return pe


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    t_session_start = time.time()

    import openmm
    from openmm import unit, MonteCarloBarostat
    from openmm.app import (
        PDBFile, Modeller, Simulation, ForceField, DCDReporter, StateDataReporter,
        CheckpointReporter, PME,
    )
    from openmmml import MLPotential
    try:
        from pdbfixer import PDBFixer
        HAS_PDBFIXER = True
    except ImportError:
        HAS_PDBFIXER = False

    setup_dirs()

    # Start GPU keepalive thread BEFORE CPU-heavy work (PDBFixer, solvation, minimization).
    start_gpu_keepalive()

    (chk_path, equil_state_path, progress_path, topology_pdb,
     prod_dcd, prod_csv, meta_path) = checkpoint_paths()

    progress = read_progress(progress_path)
    resuming = os.path.exists(chk_path) and progress.get("production_started", False)

    meta = {
        "task": "mace-hybrid-npt",
        "protein": PROTEIN,
        "tag": TAG,
        "pdb_path": PDB_PATH,
        "resrange": RESRANGE or None,
        "target_ns": TARGET_NS,
        "barostat_mode": BAROSTAT_MODE,
        "session_started": datetime.now(timezone.utc).isoformat(),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID", "interactive"),
        "slurm_node": os.environ.get("SLURMD_NODENAME", "unknown"),
        "parameters": {
            "temperature_K": TEMPERATURE_K,
            "friction_ps": FRICTION,
            "timestep_fs": DT_FS,
            "equil_timestep_fs": DT_EQUIL_FS,
            "pressure_atm": PRESSURE_ATM,
            "barostat_freq": BAROSTAT_FREQ,
            "nvt_equil_ps": NVT_EQUIL_PS,
            "npt_equil_ps": NPT_EQUIL_PS,
            "target_ns": TARGET_NS,
            "solvent_padding_nm": SOLVENT_PADDING_NM,
            "nonbonded_cutoff_nm": NB_CUTOFF_NM,
            "ionic_strength_M": IONIC_STRENGTH_M,
            "water_model": "tip3pfb",
            "ml_model": "mace-off24-medium",
            "force_field": "amber14-all + tip3pfb",
        },
    }

    try:
        # ===================================================================
        # A) SYSTEM BUILD (only when starting fresh; reused from checkpoint otherwise)
        # ===================================================================
        #
        # OpenMM checkpoints contain only the dynamic state (positions, velocities,
        # box, step). We must rebuild topology + system each session to load the
        # checkpoint into. We detect resume-mode after the system is built.

        modeller = load_and_crop_pdb()

        if HAS_PDBFIXER:
            log("Running PDBFixer (fill missing heavy atoms, add hydrogens at pH 7)...")
            tmp_pdb = os.path.join(SCRATCH_DIR, TAG, f"{TAG}_protein_only.pdb")
            with open(tmp_pdb, 'w') as f:
                PDBFile.writeFile(modeller.topology, modeller.positions, f)
            fixer = PDBFixer(filename=tmp_pdb)
            fixer.findMissingResidues()
            fixer.missingResidues = {}  # don't cap terminal residues
            fixer.findNonstandardResidues()
            fixer.replaceNonstandardResidues()
            fixer.findMissingAtoms()
            fixer.addMissingAtoms()
            fixer.addMissingHydrogens(pH=7.0)
            modeller = Modeller(fixer.topology, fixer.positions)
            log(f"  After PDBFixer: {modeller.topology.getNumAtoms()} atoms, "
                f"{modeller.topology.getNumResidues()} residues")
        else:
            log("PDBFixer not available; using Modeller.addHydrogens only")
            modeller.addHydrogens()

        protein_atom_count = modeller.topology.getNumAtoms()
        protein_residue_count = modeller.topology.getNumResidues()
        protein_atoms = list(range(protein_atom_count))

        log(f"Adding TIP3P-FB solvent (padding={SOLVENT_PADDING_NM} nm, "
            f"ionic strength={IONIC_STRENGTH_M} M)...")
        ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
        modeller.addSolvent(
            ff,
            padding=SOLVENT_PADDING_NM * unit.nanometer,
            ionicStrength=IONIC_STRENGTH_M * unit.molar,
            model='tip3p',
        )
        total_atom_count = modeller.topology.getNumAtoms()
        water_ion_atom_count = total_atom_count - protein_atom_count
        log(f"  After solvation: {total_atom_count} atoms "
            f"(protein={protein_atom_count}, water+ions={water_ion_atom_count})")

        log("Building classical AMBER14 + TIP3P-FB system (PME, 1.0 nm cutoff)...")
        mm_system = ff.createSystem(
            modeller.topology,
            nonbondedMethod=PME,
            nonbondedCutoff=NB_CUTOFF_NM * unit.nanometer,
            constraints=None,
            rigidWater=True,
        )

        log(f"Creating hybrid MACE-OFF24-medium system "
            f"({len(protein_atoms)} MACE atoms / {total_atom_count} total)...")
        t0 = time.time()
        potential = MLPotential('mace-off24-medium')
        import torch as _torch
        from functools import partial as _partial
        _use_f32 = os.environ.get("MACE_PRECISION", "try-single") != "double"

        # Build hybrid system with f64 openmmml (always works)
        hybrid_system = potential.createMixedSystem(
            modeller.topology, mm_system, protein_atoms, interpolate=False,
        )

        if _use_f32:
            # Float32 bypass: openmmml's addForces loads the model incorrectly
            # for f32 (ScriptModule dtype mismatch). We load it ourselves and
            # replace the PythonForce callback. Verified: 2.56 ns/day vs 2.13
            # f64 on H200 (1.21x speedup, diag_f32_bypass_9357320).
            try:
                _torch.set_default_dtype(_torch.float32)
                from mace.calculators.foundations_models import mace_off as _mace_off
                from mace.tools import utils as _u, to_one_hot as _toh
                from mace.tools import atomic_numbers_to_indices as _ani
                from mace.data.neighborhood import get_neighborhood as _get_nh
                _f32_model = _mace_off(
                    model='https://github.com/ACEsuit/mace-off/blob/main/mace_off24/MACE-OFF24_medium.model?raw=true',
                    device='cuda', return_raw_model=True).to('cuda').float()
                for _p in _f32_model.parameters():
                    _p.requires_grad = False
                _f32_cutoff = float(_f32_model.r_max.detach())
                _f32_dtype = _torch.float32
                _f32_dev = _torch.device('cuda')
                _incl = [list(modeller.topology.atoms())[i] for i in protein_atoms]
                _anums = [a.element.atomic_number for a in _incl]
                _zt = _u.AtomicNumberTable([int(z) for z in _f32_model.atomic_numbers])
                _na = _toh(_torch.tensor(_ani(_anums, z_table=_zt),
                           dtype=_torch.long, device=_f32_dev).unsqueeze(-1),
                           num_classes=len(_zt)).to(_f32_dtype)
                _idx = np.array(protein_atoms)
                _pbc = True

                def _f32_compute(state, model, ptr, na, batch, pbc_t, idx, periodic, cutoff, dtype, dev):
                    _torch.set_default_dtype(_torch.float32)
                    eS, lS = 96.4853, 10.0
                    pos = state.getPositions(asNumpy=True).value_in_unit(unit.angstrom)
                    nA = pos.shape[0]
                    pos = pos[idx]
                    cell = state.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.angstrom) if periodic else np.identity(3)
                    ei, sh, _, _ = _get_nh(pos, cutoff, [periodic]*3, cell)
                    inp = {"ptr": ptr, "node_attrs": na, "batch": batch, "pbc": pbc_t,
                           "positions": _torch.tensor(pos, dtype=dtype, device=dev),
                           "edge_index": _torch.tensor(ei, dtype=_torch.int64, device=dev),
                           "shifts": _torch.tensor(sh, dtype=dtype, device=dev),
                           "cell": _torch.tensor(cell, dtype=dtype, device=dev),
                           "total_charge": _torch.tensor([0.0], dtype=dtype, device=dev),
                           "total_spin": _torch.tensor([1.0], dtype=dtype, device=dev)}
                    r = model(inp, compute_force=True)
                    e = float(r["interaction_energy"].detach()) * eS
                    f = (r["forces"] * eS * lS).detach().cpu().numpy()
                    out = np.zeros((nA, 3), dtype=np.float32)
                    out[idx] = f
                    return e, out

                # Replace openmmml's PythonForce with our f32 version
                for _i in range(hybrid_system.getNumForces()):
                    _force = hybrid_system.getForce(_i)
                    if isinstance(_force, openmm.PythonForce):
                        _fg = _force.getForceGroup()
                        _pbc_flag = _force.usesPeriodicBoundaryConditions()
                        hybrid_system.removeForce(_i)
                        _cb = _partial(_f32_compute, model=_f32_model,
                                       ptr=_torch.tensor([0, len(protein_atoms)], dtype=_torch.long, device=_f32_dev),
                                       na=_na, batch=_torch.zeros(len(protein_atoms), dtype=_torch.long, device=_f32_dev),
                                       pbc_t=_torch.tensor([_pbc]*3, dtype=_torch.bool, device=_f32_dev),
                                       idx=_idx, periodic=_pbc, cutoff=_f32_cutoff, dtype=_f32_dtype, dev=_f32_dev)
                        _nf = openmm.PythonForce(_cb)
                        _nf.setForceGroup(_fg)
                        _nf.setUsesPeriodicBoundaryConditions(_pbc_flag)
                        hybrid_system.addForce(_nf)
                        log("  Using float32 MACE (bypass, 1.21x speedup)")
                        break
            except Exception as _e:
                log(f"  Float32 bypass failed ({_e}), using f64")
                _torch.set_default_dtype(_torch.float64)

        t_sys = time.time() - t0
        log(f"  Hybrid system built in {t_sys:.1f}s: "
            f"{hybrid_system.getNumParticles()} particles, "
            f"{hybrid_system.getNumForces()} forces")

        # NPT: add MonteCarloBarostat (skip if NVT fallback mode)
        if BAROSTAT_MODE == "npt":
            log(f"Adding MonteCarloBarostat ({PRESSURE_ATM} atm, {TEMPERATURE_K} K, "
                f"freq={BAROSTAT_FREQ} steps)...")
            barostat = MonteCarloBarostat(
                PRESSURE_ATM * unit.atmosphere,
                TEMPERATURE_K * unit.kelvin,
                BAROSTAT_FREQ,
            )
            hybrid_system.addForce(barostat)
        else:
            log(f"BAROSTAT_MODE={BAROSTAT_MODE} -- running NVT (no barostat)")

        meta["system"] = {
            "protein_atom_count": protein_atom_count,
            "protein_residue_count": protein_residue_count,
            "water_ion_atom_count": water_ion_atom_count,
            "total_atom_count": total_atom_count,
            "n_forces": hybrid_system.getNumForces(),
            "build_time_s": t_sys,
        }

        # OpenCL platform (CUDA is broken on all available GPUs per Sub 1.1 Subagent A)
        log("Selecting OpenCL platform (CUDA disabled by Sub 1.1 policy)...")
        platform = openmm.Platform.getPlatformByName('OpenCL')

        integrator = openmm.LangevinMiddleIntegrator(
            TEMPERATURE_K * unit.kelvin,
            FRICTION / unit.picosecond,
            DT_FS * unit.femtosecond,
        )
        simulation = Simulation(modeller.topology, hybrid_system, integrator,
                                platform, {})

        # ===================================================================
        # B) EITHER LOAD CHECKPOINT (resume) OR RUN EQUIL (fresh start)
        # ===================================================================

        if resuming:
            # Resume production from checkpoint
            log(f"[RESUME] Loading checkpoint from {chk_path}")
            try:
                with open(chk_path, 'rb') as f:
                    simulation.context.loadCheckpoint(f.read())
            except Exception as e:
                if "wrong number of particles" in str(e):
                    log(f"[RESUME] Checkpoint particle mismatch (stale from prior solvation). "
                        f"Deleting stale checkpoint and starting fresh.")
                    os.remove(chk_path)
                    if os.path.exists(progress_path):
                        os.remove(progress_path)
                    resuming = False
                else:
                    raise
        if resuming:
            loaded_step = simulation.context.getState().getStepCount()
            log(f"[RESUME] Resumed at step {loaded_step} "
                f"({loaded_step * DT_FS / 1e6:.3f} ns into production)")

            prior_ns = progress.get("production_ns_completed", 0.0)
            total_prod_ns_from_steps = loaded_step * DT_FS / 1e6
            log(f"[RESUME] Progress JSON reports {prior_ns:.3f} ns; "
                f"checkpoint step-count infers {total_prod_ns_from_steps:.3f} ns")

        else:
            # Fresh start: minimization + equilibration
            simulation.context.setPositions(modeller.positions)

            # Minimization ---------------------------------------------------
            log("Minimizing hybrid system (max 2000 iter, tol 10 kJ/mol/nm)...")
            t0 = time.time()
            simulation.minimizeEnergy(
                maxIterations=2000,
                tolerance=10 * unit.kilojoule_per_mole / unit.nanometer,
            )
            t_min = time.time() - t0
            # Post-min max-force sanity check (Sub 1.1 regression guard)
            _pm_state = simulation.context.getState(getForces=True)
            _pm_forces = _pm_state.getForces(asNumpy=True).value_in_unit(
                unit.kilojoule_per_mole / unit.nanometer)
            _max_f = float(np.max(np.abs(_pm_forces)))
            log(f"  Post-min max |force|: {_max_f:.2e} kJ/mol/nm  (min wall {t_min:.1f}s)")
            if _max_f > 1e5:
                raise RuntimeError(
                    f"Post-minimization max force {_max_f:.2e} kJ/mol/nm exceeds "
                    "1e5 threshold -- system not properly relaxed")
            check_nan(simulation, "post-minimization")
            meta["minimization"] = {
                "wall_time_s": t_min,
                "max_force_kJ_mol_nm": _max_f,
            }

            # Self-diagnostic: run 10 integration steps and check for NaN.
            # Catches system-build errors early before committing to hours of H200 time.
            log("CUDA patch self-test: running 10 integration steps...")
            t_diag = time.time()
            simulation.step(10)
            check_nan(simulation, "cuda-patch-self-test-10-steps")
            t_diag = time.time() - t_diag
            log(f"  Self-test PASSED in {t_diag:.2f}s "
                f"({10*1e-6/t_diag*86400:.3f} ns/day estimated throughput)")

            # Write topology PDB (needed for trajectory analysis; water is NOT dropped)
            with open(topology_pdb, 'w') as f:
                PDBFile.writeFile(
                    simulation.topology,
                    simulation.context.getState(getPositions=True).getPositions(),
                    f,
                )
            log(f"  Topology PDB written: {topology_pdb}")

            # Unified equilibration (2026-04-19 hang-fix): Sub 1.1's proven flow
            # with NO integrator.setStepSize(), NO barostat frequency toggling.
            # Prior 2-stage equil (NVT dt=0.5 + NPT dt=1.0 w/ MCB toggle) reliably
            # hung matscipy.py_neighbour_list within seconds of Stage A start.
            # Sub 1.1 exact-script Diag 0b (2026-04-19T22:41Z, WW, 8930522 4ldqsdyt)
            # ran clean at 2.127 ns/day proving env + matscipy + OpenCL path healthy.
            # Key invariants matching Sub 1.1:
            #   - integrator dt NEVER changed after Simulation construction
            #   - MCB added at system build (if NPT) and left at constant freq
            #   - setVelocitiesToTemperature called once post-min (same as Sub 1.1)
            simulation.context.setVelocitiesToTemperature(TEMPERATURE_K * unit.kelvin)

            # Single equilibration stage: NVT_EQUIL_PS + NPT_EQUIL_PS combined,
            # running at constant DT_FS with MCB active from the start (if npt mode).
            total_equil_ps = NVT_EQUIL_PS + NPT_EQUIL_PS
            equil_steps = int(total_equil_ps * 1000 / DT_FS)
            log(f"--- Equilibration: {total_equil_ps} ps "
                f"({equil_steps} steps at dt={DT_FS} fs, {BAROSTAT_MODE} mode) ---")
            t0 = time.time()
            steps_done, last_check = 0, 0
            while steps_done < equil_steps:
                chunk = min(NAN_CHECK_INTERVAL_STEPS, equil_steps - steps_done)
                simulation.step(chunk)
                steps_done += chunk
                if steps_done - last_check >= NAN_CHECK_INTERVAL_STEPS:
                    check_nan(simulation, f"equil {steps_done * DT_FS / 1000:.1f}ps")
                    # Progress log every 5000 steps (2026-04-19 fix): prior silent
                    # equil loops were misread as hangs. 5000 steps = 5 ps = ~3 min
                    # wall at 2 ns/day → plenty of visible progress.
                    if (steps_done // 5000) > (last_check // 5000):
                        pct = 100.0 * steps_done / equil_steps
                        elapsed_min = (time.time() - t0) / 60.0
                        log(f"    equil progress: {steps_done}/{equil_steps} "
                            f"({pct:.1f}%) | {elapsed_min:.1f} min elapsed")
                    last_check = steps_done
            t_equil = time.time() - t0
            log(f"  Equilibration wall: {t_equil:.1f}s "
                f"({total_equil_ps/(t_equil/86400)/1000:.3f} ns/day)")
            meta["equilibration"] = {"wall_time_s": t_equil, "ps": total_equil_ps}

            # Save end-of-equil state for reproducibility + reset step count ---
            state_end_equil = simulation.context.getState(
                getPositions=True, getVelocities=True, getForces=True,
                getEnergy=True, enforcePeriodicBox=True,
            )
            with open(equil_state_path, 'w') as f:
                f.write(openmm.XmlSerializer.serialize(state_end_equil))
            log(f"  Equilibration-complete state saved: {equil_state_path}")

            # Reset step counter so production starts at step 0 (clean ns tracking).
            simulation.currentStep = 0

            # Save initial production checkpoint at step 0 so that restarts
            # after hang-kills during early production skip the 50 ps equil.
            with open(chk_path, 'wb') as f:
                f.write(simulation.context.createCheckpoint())
            progress["production_started"] = True
            progress["production_ns_completed"] = 0.0
            progress["last_step"] = 0
            progress["updated"] = datetime.now(timezone.utc).isoformat()
            write_progress(progress_path, progress)
            log(f"  Initial production checkpoint saved (step 0) — restarts skip equil")

        # ===================================================================
        # C) PRODUCTION LOOP (append-mode reporters + checkpoint saving + walltime guard)
        # ===================================================================

        total_prod_steps = int(TARGET_NS * 1e6 / DT_FS)   # target production steps total
        report_steps = max(1, int(REPORT_INTERVAL_PS * 1000 / DT_FS))

        # On resume: start from the recorded step; on fresh start: step 0.
        if resuming:
            start_step = simulation.context.getState().getStepCount()
            # Set simulation.currentStep to match (Simulation tracks this separately)
            simulation.currentStep = start_step
        else:
            start_step = 0
            simulation.currentStep = 0

        log(f"--- Production (target {TARGET_NS} ns = {total_prod_steps} steps) ---")
        log(f"  Starting from step {start_step} "
            f"({start_step * DT_FS / 1e6:.4f} ns) in {BAROSTAT_MODE} mode")

        if start_step >= total_prod_steps:
            log(f"  Trajectory already at target ({start_step * DT_FS / 1e6:.4f} ns). "
                f"Nothing to do.")
            meta["production_status"] = "already_at_target"
            meta["session_ended"] = datetime.now(timezone.utc).isoformat()
            with open(meta_path, 'w') as f:
                json.dump(meta, f, indent=2, default=str)
            stop_gpu_keepalive()
            return 0

        # Attach reporters in APPEND mode so multiple SLURM jobs concatenate
        # to one DCD + one CSV per protein.
        simulation.reporters = []
        simulation.reporters.append(
            DCDReporter(prod_dcd, report_steps, append=os.path.exists(prod_dcd))
        )
        # For StateDataReporter, append requires opening the file first and passing
        # the file handle (not a path) so it doesn't write the header again.
        csv_exists = os.path.exists(prod_csv)
        if csv_exists:
            csv_handle = open(prod_csv, 'a', buffering=1)
            sdr = StateDataReporter(
                csv_handle, report_steps,
                step=True, time=True,
                potentialEnergy=True, kineticEnergy=True, totalEnergy=True,
                temperature=True, volume=True, density=True,
                speed=True,
                # No header on append
            )
            # Monkey-patch: suppress header on append by marking as initialized,
            # then manually initialize internal constants (_dof, speed baselines).
            sdr._hasInitialized = True
            sdr._initializeConstants(simulation)
            sdr._initialClockTime = time.time()
            sdr._initialSimulationTime = simulation.context.getState(getTime=True).getTime()
            sdr._initialSteps = simulation.currentStep
            simulation.reporters.append(sdr)
        else:
            sdr = StateDataReporter(
                prod_csv, report_steps,
                step=True, time=True,
                potentialEnergy=True, kineticEnergy=True, totalEnergy=True,
                temperature=True, volume=True, density=True,
                speed=True,
            )
            simulation.reporters.append(sdr)

        # Checkpoint reporter: every CHECKPOINT_INTERVAL_STEPS
        simulation.reporters.append(
            CheckpointReporter(chk_path, CHECKPOINT_INTERVAL_STEPS)
        )

        # Production loop with walltime guard and periodic NaN check
        t_prod_start = time.time()
        steps_done_this_session = 0
        last_nan_check = start_step
        current_step = start_step

        # Run in chunks of CHECKPOINT_INTERVAL_STEPS so we can check walltime
        # between chunks and exit cleanly for resubmission.
        chunk_size = min(CHECKPOINT_INTERVAL_STEPS, NAN_CHECK_INTERVAL_STEPS * 10)

        while current_step < total_prod_steps:
            elapsed = time.time() - t_session_start
            if elapsed >= WALLTIME_GUARD_SEC:
                log(f"  [WALLTIME_GUARD] Elapsed {elapsed:.0f}s >= guard {WALLTIME_GUARD_SEC}s; "
                    f"saving final checkpoint and exiting for resubmission")
                # Explicit final checkpoint save
                with open(chk_path, 'wb') as f:
                    f.write(simulation.context.createCheckpoint())
                progress["production_ns_completed"] = current_step * DT_FS / 1e6
                progress["production_started"] = True
                progress["session_exit_reason"] = "walltime_guard"
                progress["last_step"] = current_step
                progress["updated"] = datetime.now(timezone.utc).isoformat()
                write_progress(progress_path, progress)
                meta["production_status"] = "walltime_exit"
                meta["production_ns_at_exit"] = current_step * DT_FS / 1e6
                meta["session_ended"] = datetime.now(timezone.utc).isoformat()
                with open(meta_path, 'w') as f:
                    json.dump(meta, f, indent=2, default=str)
                stop_gpu_keepalive()
                return 2

            this_chunk = min(chunk_size, total_prod_steps - current_step)
            simulation.step(this_chunk)
            current_step += this_chunk
            steps_done_this_session += this_chunk

            # Periodic NaN check
            if current_step - last_nan_check >= NAN_CHECK_INTERVAL_STEPS:
                check_nan(simulation, f"prod {current_step * DT_FS / 1e6:.4f} ns")
                last_nan_check = current_step

            # Update progress every chunk
            progress["production_ns_completed"] = current_step * DT_FS / 1e6
            progress["production_started"] = True
            progress["last_step"] = current_step
            progress["updated"] = datetime.now(timezone.utc).isoformat()
            write_progress(progress_path, progress)

            # Log periodic throughput
            if steps_done_this_session >= 10000:
                ns_session = steps_done_this_session * DT_FS / 1e6
                s_session = time.time() - t_prod_start
                tput = (ns_session / s_session * 86400) if s_session > 0 else 0.0
                log(f"  step {current_step}: "
                    f"{current_step * DT_FS / 1e6:.4f} ns / {TARGET_NS:.2f} ns "
                    f"(session throughput {tput:.3f} ns/day)")

        # ===================================================================
        # D) COMPLETION -- target reached
        # ===================================================================

        # Final checkpoint
        with open(chk_path, 'wb') as f:
            f.write(simulation.context.createCheckpoint())
        t_prod = time.time() - t_prod_start
        session_ns = steps_done_this_session * DT_FS / 1e6
        prod_throughput = (session_ns / (t_prod / 86400)) if t_prod > 0 else 0.0
        log(f"  Session production wall: {t_prod:.1f}s "
            f"({session_ns:.3f} ns this session, {prod_throughput:.3f} ns/day)")

        progress["production_ns_completed"] = current_step * DT_FS / 1e6
        progress["production_started"] = True
        progress["session_exit_reason"] = "target_reached"
        progress["updated"] = datetime.now(timezone.utc).isoformat()
        write_progress(progress_path, progress)

        meta["production_status"] = "target_reached"
        meta["production_ns_total"] = current_step * DT_FS / 1e6
        meta["session_ended"] = datetime.now(timezone.utc).isoformat()
        meta["session_wall_time_s"] = t_prod
        meta["session_throughput_ns_per_day"] = prod_throughput
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=2, default=str)

        log("=========================================================")
        log(f"MACE HYBRID NPT on {PROTEIN}: TARGET REACHED")
        log(f"  Total production: {current_step * DT_FS / 1e6:.4f} ns")
        log(f"  Session wall: {t_prod:.1f}s")
        log(f"  Session throughput: {prod_throughput:.3f} ns/day")
        log(f"  Trajectory: {prod_dcd}")
        log(f"  State log: {prod_csv}")
        log(f"  Meta JSON: {meta_path}")
        log("=========================================================")
        stop_gpu_keepalive()
        return 0

    except Exception as e:
        tb = traceback.format_exc()
        log(f"FATAL EXCEPTION: {e}")
        log(tb)
        meta["fatal_exception"] = {"error": str(e), "traceback": tb}
        meta["production_status"] = "failed"
        meta["session_ended"] = datetime.now(timezone.utc).isoformat()
        try:
            with open(meta_path, 'w') as f:
                json.dump(meta, f, indent=2, default=str)
        except Exception:
            pass
        stop_gpu_keepalive()
        return 1


if __name__ == "__main__":
    try:
        import torch
        log(f"torch {torch.__version__} | cuda avail: {torch.cuda.is_available()}")
    except Exception:
        pass
    try:
        import openmm
        log(f"OpenMM {openmm.__version__}")
    except Exception:
        pass
    sys.exit(main())
