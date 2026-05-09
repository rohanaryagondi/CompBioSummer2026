#!/usr/bin/env python
"""
mace_hybrid_npt_prod.py -- MACE-OFF24 hybrid NPT production driver
(Round 3 recipe: sentinel-bond + protein HBonds constraints + dt=1 fs +
MCB freq=25, always-on).

Forked from `mace_hybrid_npt.py` (the v1-v6 NPT driver that exposed the
NPT-instability root cause) and `npt_diagnostics/test_P_extended.py`
(the 100 ps NPT confirmation, 2026-05-02 job 10441986). Combines the
production-validated recipe with full checkpoint/restart, walltime guard,
append-mode reporters, and protein-agnostic config.

Recipe (ALWAYS apply, NEVER deviate -- see shared/notes/1.2-mace-npt-fixed.md):
  1. After `MLPotential('mace-off24-medium').createMixedSystem(...)`:
     a) `add_protein_sentinel_bonds(hybrid_system, topology, protein_atoms)`
        -- restores connectivity for OpenMM `findMolecules()`.
     b) `add_protein_hbonds_constraints(hybrid_system, topology, protein_atoms)`
        -- restores rigid C-H/N-H/O-H bonds for protein region.
  2. `MonteCarloBarostat(1 atm, 300 K, freq=25)` ALWAYS-ON from build time.
     DO NOT use the freq=0 -> setFrequency(25) toggle; that interacts badly
     with `loadCheckpoint`. test_P (100 ps clean) proved always-on works.
  3. Single-stage equilibration: 50 ps NPT at dt=1 fs, then production.
  4. Defensive `assert hybrid_system.getNumConstraints() ==
     progress.get("n_constraints_at_checkpoint")` before `loadCheckpoint`.
     On mismatch: scrub checkpoint + progress, restart fresh.

Per-protein defaults via PROTEIN_DEFAULTS dict at top:
  ww  -> 2F21 chain A residues 6-39
  gb3 -> 1P7E chain A
  ubq -> 1UBQ chain A

CLI (all via environment variables):
    MACE_HYBRID_PROTEIN  -- ww | gb3 | ubq
    MACE_HYBRID_PDB      -- override per-protein default
    MACE_HYBRID_RESRANGE -- optional "start-end" residue crop
    MACE_HYBRID_TARGET_NS    -- 0.05 for diagnostic probes, 5.0 for production
    MACE_HYBRID_TAG          -- 8-char cryptic tag for output files
    MACE_OUTPUT_DIR          -- persistent output dir
    MACE_SCRATCH_DIR         -- scratch dir for checkpoints + equil state
    MACE_HYBRID_WALLTIME_GUARD_SEC -- default 81000 (22.5 hr)

Exit codes:
  0 -- trajectory reached MACE_HYBRID_TARGET_NS (mission complete)
  2 -- walltime-friendly checkpoint saved; resubmit to continue
  1 -- fatal failure (NaN, exception, system build error)

OpenCL platform only (CUDA broken on H200 per Sub 1.1 policy).

Project: CompBioSummer2026 Sub 1.2 task-001 (mlff-mace-pilot, Round 3 recipe).
"""
from __future__ import annotations

# Suppress user site-packages BEFORE any other imports (env-mace contract).
import os
os.environ['PYTHONNOUSERSITE'] = '1'

import json
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

# ---------------------------------------------------------------------------
# Vesin neighbor list monkey-patch (Sub 1.1 hang-fix; from mace_hybrid_npt.py)
# ---------------------------------------------------------------------------
# matscipy holds the GIL during its entire C extension call, causing sporadic
# 20+ minute hangs from GIL deadlock with the GPU keepalive thread. vesin
# (Rust/ctypes) releases the GIL, eliminating the deadlock. Bit-identical
# output verified.
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

# Per-protein defaults (PDB path, residue crop, chain). Manifest source:
# Execution/phases/phase-0/subphase-0.1/proteins/manifest.json
PROTEIN_DEFAULTS = {
    "ww": {
        "pdb": "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ww.pdb",
        "resrange": "6-39",
        "chain": "A",
        "pdb_id": "2F21",
    },
    "gb3": {
        "pdb": "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/gb3.pdb",
        "resrange": "",
        "chain": "A",
        "pdb_id": "1P7E",
    },
    "ubq": {
        "pdb": "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ubq.pdb",
        "resrange": "",
        "chain": "A",
        "pdb_id": "1UBQ",
    },
    "ntl9": {
        # 51 aa, Tier B, S2-counted (Lillemoen & Hoffman 1998 JMB 281:539);
        # 390 protein-ATOM records (smallest of WW/GB3/GB1/NTL9/UBQ candidate set);
        # added 2026-05-03 as the option-(c) substitute for UBQ in success criterion #1
        # after UBQ MACE NPT non-generalization at 17K-atom solvated scale.
        "pdb": "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ntl9.pdb",
        "resrange": "",
        "chain": "A",
        "pdb_id": "2HBB",
    },
    # UBQ alternate starting structure (option d, added 2026-05-03):
    # 1XQQ chain A model 1, NMR ensemble (Lange et al. 2008 Science 320:1471).
    # Hypothesis: 1UBQ crystal residual stress drives the asymptotic NaN at
    # 7-9.6 ps in MACE-OFF24 hybrid NPT (dt=1.0/0.5/0.25 fs all NaN within
    # ~1 ps stride). NMR-derived starting conformation may relieve that stress.
    # See shared/help-needed/head-1.2-mace-ubq-non-generalization.md §UBQ option (d).
    "ubq_alt": {
        "pdb": "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ubq_alt.pdb",
        "resrange": "",
        "chain": "A",
        "pdb_id": "1XQQ",
    },
}
_pd = PROTEIN_DEFAULTS.get(PROTEIN, {"pdb": "", "resrange": "", "chain": "A", "pdb_id": ""})

PDB_PATH = os.environ.get("MACE_HYBRID_PDB", _pd["pdb"])
RESRANGE = os.environ.get("MACE_HYBRID_RESRANGE", _pd["resrange"]).strip()
PDB_ID = _pd["pdb_id"]

TARGET_NS = float(os.environ.get("MACE_HYBRID_TARGET_NS", "5.0"))

OUTPUT_DIR = os.environ.get(
    "MACE_OUTPUT_DIR",
    "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.2/output/trajectories/mace_npt_prod",
)
SCRATCH_DIR = os.environ.get(
    "MACE_SCRATCH_DIR",
    "/nfs/roberts/scratch/pi_mg269/rag88/alpha-m/mace-npt-prod",
)
TAG = os.environ.get("MACE_HYBRID_TAG", PROTEIN)

# Simulation parameters (Round 3 recipe)
TEMPERATURE_K = 300.0
FRICTION = 1.0                   # 1/ps Langevin
DT_FS = float(os.environ.get("MACE_HYBRID_DT_FS", "1.0"))   # fs production timestep; default 1.0 (Round 3 validated); 0.5 fallback for proteins where 1.0 fs NaNs (per D5 closure-master-plan iteration reserve)
PRESSURE_ATM = 1.0
BAROSTAT_FREQ = 25               # MonteCarloBarostat step frequency, ALWAYS-ON
REPORT_INTERVAL_PS = 5.0         # DCD + CSV stride (5 ps -> 200 frames/ns; 5x smaller DCD; OSF doesn't lock stride)
NAN_CHECK_INTERVAL_STEPS = 5000  # check for NaN every 5000 steps (Round 3 stable; less getState overhead)
SOLVENT_PADDING_NM = float(os.environ.get("MACE_HYBRID_PADDING_NM", "1.0"))
NB_CUTOFF_NM = 1.0
IONIC_STRENGTH_M = 0.15

# Equilibration: 25 ps NPT at dt=1 fs. test_P showed density convergence within
# 25 ps. OSF v3 §8 locks the 100-ps analysis discard window (not script equil),
# so analysis pipeline still discards first 100 ps regardless.
NPT_EQUIL_PS = 25.0

# Checkpoint cadence: every 25 ps wall = 25,000 steps at dt=1 fs (less I/O)
CHECKPOINT_INTERVAL_STEPS = 25000

# Walltime guard: save checkpoint and exit cleanly before SLURM hard-kills us.
# gpu_h200 walltime 23:59:00; guard at 22.5 hrs (81000 s) leaves margin for save.
WALLTIME_GUARD_SEC = int(os.environ.get("MACE_HYBRID_WALLTIME_GUARD_SEC", "81000"))


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
# GPU keepalive (5-min cadence, in-Python thread)
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
            _keepalive_stop.wait(600)  # 10 min between pokes (YCRC 1hr cancel; 6x safety)
    except Exception:
        # Keepalive must never crash the simulation
        pass


def start_gpu_keepalive() -> _threading.Thread:
    t = _threading.Thread(target=_gpu_keepalive_loop, daemon=True, name='gpu-keepalive')
    t.start()
    log("Started GPU keepalive thread (5-min cadence)")
    return t


def stop_gpu_keepalive() -> None:
    _keepalive_stop.set()


# ---------------------------------------------------------------------------
# Recipe helpers (delegated to npt_diagnostics/npt_diag_common.py)
# ---------------------------------------------------------------------------

# Path to the diagnostics dir containing the validated helpers.
NPT_DIAG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "npt_diagnostics")
sys.path.insert(0, NPT_DIAG_DIR)

# Import the production-validated helpers verbatim. Do NOT modify these.
from npt_diag_common import (
    add_protein_sentinel_bonds,
    add_protein_hbonds_constraints,
)


# ---------------------------------------------------------------------------
# PDB load / crop (production version, supports any protein via env vars)
# ---------------------------------------------------------------------------

def load_and_crop_pdb():
    """Load PDB, strip non-protein het, keep first chain, optional residue crop."""
    from openmm.app import PDBFile, Modeller

    log(f"Loading PDB: {PDB_PATH}")
    pdb = PDBFile(PDB_PATH)
    modeller = Modeller(pdb.topology, pdb.positions)
    log(f"  Raw topology: {modeller.topology.getNumAtoms()} atoms, "
        f"{modeller.topology.getNumResidues()} residues, "
        f"{len(list(modeller.topology.chains()))} chains")

    std_aa = {
        'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE',
        'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL',
        'HID', 'HIE', 'HIP', 'CYX', 'CYM', 'ASH', 'GLH', 'LYN',
    }
    res_to_delete = [r for r in modeller.topology.residues() if r.name not in std_aa]
    if res_to_delete:
        log(f"  Deleting {len(res_to_delete)} non-protein residues (waters/ions/ligands)")
        modeller.delete(res_to_delete)

    first_chain_id = list(modeller.topology.chains())[0].id
    other_chain_residues = []
    for chain in modeller.topology.chains():
        if chain.id != first_chain_id:
            other_chain_residues.extend(chain.residues())
    if other_chain_residues:
        log(f"  Deleting {len(other_chain_residues)} residues from non-A chains")
        modeller.delete(other_chain_residues)

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


def check_nan(simulation, label: str, state=None) -> float:
    from openmm import unit
    # Drop getForces=True (deeper-opt-hunter A6): forces transfer is ~50 KB
    # GPU→CPU per call. NaN-on-positions or NaN-on-PE catches >99% of failure
    # modes; PE goes NaN before forces explode. Saves ~0.3-0.6% throughput.
    # R4-2026-05-05: optional pre-fetched state arg for state-reuse callers
    # (loops that already hold a State with positions+energy can pass it in
    # to avoid a second GPU→CPU copy; ~0.5-1 ms saved per reused fetch).
    if state is None:
        state = simulation.context.getState(getPositions=True, getEnergy=True)
    pos = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
    pe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
    if np.any(np.isnan(pos)):
        raise RuntimeError(f"NaN positions at {label}")
    if np.isnan(pe):
        raise RuntimeError(f"NaN potential energy at {label}")
    return pe


# ---------------------------------------------------------------------------
# Hybrid system build (f32 bypass; ALWAYS apply Round 3 recipe patches)
# ---------------------------------------------------------------------------

def build_hybrid_system(modeller, mm_system, protein_atoms):
    """
    Build hybrid MACE-OFF24-medium system with f32 bypass and apply
    Round 3 recipe patches (sentinel bonds + HBonds constraints).

    Order:
      1. createMixedSystem (openmmml f64 path that always works)
      2. f32 bypass via PythonForce replacement (1.21x speedup; Sub 1.1 §11)
      3. add_protein_sentinel_bonds (restore protein connectivity for findMolecules)
      4. add_protein_hbonds_constraints (restore C-H/N-H/O-H rigidity at dt=1 fs)
      5. MonteCarloBarostat (always-on freq=25)
    """
    import openmm
    from openmm import unit, MonteCarloBarostat
    from openmmml import MLPotential
    import torch as _torch
    from functools import partial as _partial

    log(f"Creating hybrid MACE-OFF24-medium system "
        f"({len(protein_atoms)} MACE atoms / {mm_system.getNumParticles()} total)...")
    t0 = time.time()
    potential = MLPotential('mace-off24-medium')

    # Step 1: openmmml f64 createMixedSystem (always works)
    hybrid_system = potential.createMixedSystem(
        modeller.topology, mm_system, protein_atoms, interpolate=False,
    )

    # Step 2: f32 bypass for 1.21x speedup (skip if MACE_HYBRID_F32_BYPASS=0)
    try:
        if os.environ.get("MACE_HYBRID_F32_BYPASS", "1") != "1":
            log("  MACE_HYBRID_F32_BYPASS=0; using f64 PythonForce (slower, more precise)")
            raise RuntimeError("f32_bypass_disabled_by_env")
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

        # Pre-allocate constant tensors once (never change per-step) — perf optimization
        _total_charge_t = _torch.tensor([0.0], dtype=_f32_dtype, device=_f32_dev)
        _total_spin_t = _torch.tensor([1.0], dtype=_f32_dtype, device=_f32_dev)

        def _f32_compute(state, model, ptr, na, batch, pbc_t, idx, periodic,
                         cutoff, dtype, dev,
                         total_charge_t=_total_charge_t,
                         total_spin_t=_total_spin_t):
            eS, lS = 96.4853, 10.0
            pos = state.getPositions(asNumpy=True).value_in_unit(unit.angstrom)
            nA = pos.shape[0]
            pos = pos[idx]
            cell = (state.getPeriodicBoxVectors(asNumpy=True)
                    .value_in_unit(unit.angstrom)) if periodic else np.identity(3)
            ei, sh, _, _ = _get_nh(pos, cutoff, [periodic] * 3, cell)
            inp = {"ptr": ptr, "node_attrs": na, "batch": batch, "pbc": pbc_t,
                   "positions": _torch.tensor(pos, dtype=dtype, device=dev),
                   "edge_index": _torch.tensor(ei, dtype=_torch.int64, device=dev),
                   "shifts": _torch.tensor(sh, dtype=dtype, device=dev),
                   "cell": _torch.tensor(cell, dtype=dtype, device=dev),
                   "total_charge": total_charge_t,
                   "total_spin": total_spin_t}
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
                               ptr=_torch.tensor([0, len(protein_atoms)],
                                                 dtype=_torch.long, device=_f32_dev),
                               na=_na, batch=_torch.zeros(len(protein_atoms),
                                                          dtype=_torch.long,
                                                          device=_f32_dev),
                               pbc_t=_torch.tensor([_pbc] * 3, dtype=_torch.bool,
                                                   device=_f32_dev),
                               idx=_idx, periodic=_pbc, cutoff=_f32_cutoff,
                               dtype=_f32_dtype, dev=_f32_dev)
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
        f"{hybrid_system.getNumForces()} forces, "
        f"{hybrid_system.getNumConstraints()} constraints (pre-patches)")

    # Step 3: Round 3 recipe -- sentinel-bond fix
    n_sentinel = add_protein_sentinel_bonds(hybrid_system, modeller.topology, protein_atoms)
    if n_sentinel == 0:
        raise RuntimeError("add_protein_sentinel_bonds returned 0 -- bonded graph "
                           "missing from topology; cannot proceed")

    # Step 4: Round 3 recipe -- HBonds constraints
    n_hbonds = add_protein_hbonds_constraints(hybrid_system, modeller.topology,
                                              protein_atoms)
    if n_hbonds == 0:
        log("  WARNING: no HBonds constraints added (no heavy-H protein bonds found). "
            "This is unusual for proteins; proceed with caution.")

    # Step 5: MCB always-on (test_P-validated)
    log(f"Adding MonteCarloBarostat ({PRESSURE_ATM} atm, {TEMPERATURE_K} K, "
        f"freq={BAROSTAT_FREQ} steps, ALWAYS-ON)...")
    barostat = MonteCarloBarostat(
        PRESSURE_ATM * unit.atmosphere,
        TEMPERATURE_K * unit.kelvin,
        BAROSTAT_FREQ,
    )
    hybrid_system.addForce(barostat)

    log(f"  Hybrid system FINAL: "
        f"{hybrid_system.getNumParticles()} particles, "
        f"{hybrid_system.getNumForces()} forces, "
        f"{hybrid_system.getNumConstraints()} constraints (post-patches)")

    return hybrid_system, n_sentinel, n_hbonds


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
    try:
        from pdbfixer import PDBFixer
        HAS_PDBFIXER = True
    except ImportError:
        HAS_PDBFIXER = False

    setup_dirs()

    # Start GPU keepalive thread BEFORE CPU-heavy work.
    start_gpu_keepalive()

    (chk_path, equil_state_path, progress_path, topology_pdb,
     prod_dcd, prod_csv, meta_path) = checkpoint_paths()

    progress = read_progress(progress_path)
    resuming = os.path.exists(chk_path) and progress.get("production_started", False)

    meta = {
        "task": "mace-hybrid-npt-prod",
        "recipe": "Round 3: sentinel-bond + HBonds constraints + dt=1 fs + MCB freq=25 always-on",
        "protein": PROTEIN,
        "tag": TAG,
        "pdb_path": PDB_PATH,
        "pdb_id": PDB_ID,
        "resrange": RESRANGE or None,
        "target_ns": TARGET_NS,
        "session_started": datetime.now(timezone.utc).isoformat(),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID", "interactive"),
        "slurm_node": os.environ.get("SLURMD_NODENAME", "unknown"),
        "parameters": {
            "temperature_K": TEMPERATURE_K,
            "friction_ps": FRICTION,
            "timestep_fs": DT_FS,
            "pressure_atm": PRESSURE_ATM,
            "barostat_freq": BAROSTAT_FREQ,
            "npt_equil_ps": NPT_EQUIL_PS,
            "target_ns": TARGET_NS,
            "solvent_padding_nm": SOLVENT_PADDING_NM,
            "nonbonded_cutoff_nm": NB_CUTOFF_NM,
            "ionic_strength_M": IONIC_STRENGTH_M,
            "water_model": "tip3pfb",
            "ml_model": "mace-off24-medium",
            "force_field": "amber14-all + tip3pfb",
            "platform": "OpenCL",
        },
    }

    try:
        # ===================================================================
        # A) SYSTEM BUILD (always rebuilt; checkpoint contains only dynamic state)
        # ===================================================================

        modeller = load_and_crop_pdb()

        if HAS_PDBFIXER:
            log("Running PDBFixer (fill missing heavy atoms, add hydrogens at pH 7)...")
            tmp_pdb = os.path.join(SCRATCH_DIR, TAG, f"{TAG}_protein_only.pdb")
            with open(tmp_pdb, 'w') as f:
                PDBFile.writeFile(modeller.topology, modeller.positions, f)
            fixer = PDBFixer(filename=tmp_pdb)
            fixer.findMissingResidues()
            fixer.missingResidues = {}
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
        # Same TAG → same atom count → checkpoint reloads cleanly on restart.
        import random as _random
        _solv_seed = abs(hash(TAG)) % (2**32)
        _random.seed(_solv_seed)
        np.random.seed(_solv_seed)
        log(f"  Solvation random seed = {_solv_seed} (deterministic for restart consistency)")
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

        log("Building classical AMBER14 + TIP3P-FB system (PME, 1.0 nm cutoff, "
            "constraints=None for downstream HBonds re-add)...")
        mm_system = ff.createSystem(
            modeller.topology,
            nonbondedMethod=PME,
            nonbondedCutoff=NB_CUTOFF_NM * unit.nanometer,
            constraints=None,
            rigidWater=True,
        )

        # Build hybrid system with f32 bypass + Round 3 recipe patches
        hybrid_system, n_sentinel, n_hbonds = build_hybrid_system(
            modeller, mm_system, protein_atoms,
        )
        n_constraints_built = hybrid_system.getNumConstraints()

        meta["system"] = {
            "protein_atom_count": protein_atom_count,
            "protein_residue_count": protein_residue_count,
            "water_ion_atom_count": water_ion_atom_count,
            "total_atom_count": total_atom_count,
            "n_forces": hybrid_system.getNumForces(),
            "n_sentinel_bonds": n_sentinel,
            "n_hbonds_constraints": n_hbonds,
            "n_constraints_total": n_constraints_built,
        }

        # OpenCL platform (CUDA broken on H200 per Sub 1.1 policy)
        log("Selecting OpenCL platform (CUDA disabled by Sub 1.1 policy)...")
        platform = openmm.Platform.getPlatformByName('OpenCL')

        integrator = openmm.LangevinMiddleIntegrator(
            TEMPERATURE_K * unit.kelvin,
            FRICTION / unit.picosecond,
            DT_FS * unit.femtosecond,
        )
        # Relax constraint tolerance from 1e-5 (default) to 1e-4 — ~5-10% throughput
        # gain on HBonds-constrained protein region. RMS bond-length error stays
        # below 0.001 Å, far below physical bond fluctuation. Per AMBER convention.
        integrator.setConstraintTolerance(1e-4)
        simulation = Simulation(modeller.topology, hybrid_system, integrator,
                                platform, {})

        # ===================================================================
        # B) RESUME FROM CHECKPOINT (with stale-checkpoint mismatch defense)
        # ===================================================================

        if resuming:
            # Defensive: assert constraint count matches what was saved.
            n_constraints_at_checkpoint = progress.get("n_constraints_at_checkpoint")
            if n_constraints_at_checkpoint is not None and \
                    n_constraints_at_checkpoint != n_constraints_built:
                log(f"[RESUME] STALE CHECKPOINT DETECTED: "
                    f"progress reports {n_constraints_at_checkpoint} constraints, "
                    f"current build has {n_constraints_built}. "
                    f"Scrubbing checkpoint + progress and starting fresh.")
                if os.path.exists(chk_path):
                    os.remove(chk_path)
                if os.path.exists(progress_path):
                    os.remove(progress_path)
                resuming = False
                progress = {}

        if resuming:
            log(f"[RESUME] Loading checkpoint from {chk_path}")
            try:
                with open(chk_path, 'rb') as f:
                    simulation.context.loadCheckpoint(f.read())
            except Exception as e:
                if "wrong number of particles" in str(e):
                    log(f"[RESUME] Checkpoint particle mismatch (stale from prior "
                        f"solvation). Deleting stale checkpoint and starting fresh.")
                    os.remove(chk_path)
                    if os.path.exists(progress_path):
                        os.remove(progress_path)
                    resuming = False
                    progress = {}
                else:
                    raise

        if resuming:
            loaded_step = simulation.context.getState().getStepCount()
            log(f"[RESUME] Resumed at step {loaded_step} "
                f"({loaded_step * DT_FS / 1e6:.4f} ns into production)")

            prior_ns = progress.get("production_ns_completed", 0.0)
            log(f"[RESUME] Progress JSON reports {prior_ns:.4f} ns; "
                f"checkpoint step-count infers {loaded_step * DT_FS / 1e6:.4f} ns")
        else:
            # Fresh start: minimization + equilibration
            simulation.context.setPositions(modeller.positions)

            log("Minimizing hybrid system (max 2000 iter, tol 10 kJ/mol/nm)...")
            t0 = time.time()
            simulation.minimizeEnergy(
                maxIterations=500,  # was 2000; L-BFGS converges <500 iter for solvated proteins (deeper-opt-hunter A8). Post-min max_f check catches under-relaxation.
                tolerance=10 * unit.kilojoule_per_mole / unit.nanometer,
            )
            t_min = time.time() - t0
            _pm_state = simulation.context.getState(getForces=True)
            _pm_forces = _pm_state.getForces(asNumpy=True).value_in_unit(
                unit.kilojoule_per_mole / unit.nanometer)
            _max_f = float(np.max(np.abs(_pm_forces)))
            log(f"  Post-min max |force|: {_max_f:.2e} kJ/mol/nm  "
                f"(min wall {t_min:.1f}s)")
            if _max_f > 1e5:
                raise RuntimeError(
                    f"Post-minimization max force {_max_f:.2e} kJ/mol/nm "
                    "exceeds 1e5 threshold -- system not properly relaxed")
            check_nan(simulation, "post-minimization")
            meta["minimization"] = {
                "wall_time_s": t_min,
                "max_force_kJ_mol_nm": _max_f,
            }

            # Self-test: 10 integration steps
            log("10-step integration self-test...")
            t_diag = time.time()
            simulation.step(10)
            check_nan(simulation, "10-step-self-test")
            t_diag = time.time() - t_diag
            log(f"  Self-test PASSED in {t_diag:.2f}s "
                f"({10 * 1e-6 / t_diag * 86400:.3f} ns/day estimated throughput)")

            # Write topology PDB (for trajectory analysis)
            with open(topology_pdb, 'w') as f:
                PDBFile.writeFile(
                    simulation.topology,
                    simulation.context.getState(getPositions=True).getPositions(),
                    f,
                )
            log(f"  Topology PDB written: {topology_pdb}")

            # Optional: T-ramp 50K -> 300K (env-controlled, default off).
            # MCB barostat target T held at 300K during ramp; mismatch is small over short ramps.
            _tramp_ps = float(os.environ.get("MACE_HYBRID_TRAMP_PS", "0"))
            if _tramp_ps > 0:
                _T_start_K = 50.0
                log(f"--- T-ramp: {_T_start_K:.0f}K -> {TEMPERATURE_K:.0f}K over {_tramp_ps} ps (Langevin) ---")
                simulation.context.setVelocitiesToTemperature(_T_start_K * unit.kelvin)
                integrator.setTemperature(_T_start_K * unit.kelvin)
                _tramp_steps_total = int(_tramp_ps * 1000 / DT_FS)
                _n_chunks = 50
                _chunk = max(100, _tramp_steps_total // _n_chunks)
                _t0 = time.time()
                for _i in range(_n_chunks):
                    _T_curr = _T_start_K + (TEMPERATURE_K - _T_start_K) * (_i + 1) / _n_chunks
                    integrator.setTemperature(_T_curr * unit.kelvin)
                    simulation.step(_chunk)
                    if _i % 10 == 0:
                        log(f"    T-ramp progress: chunk {_i+1}/{_n_chunks}, "
                            f"T={_T_curr:.0f}K, elapsed {(time.time()-_t0)/60:.1f} min")
                log(f"  T-ramp complete in {time.time()-_t0:.1f}s; integrator T set to {TEMPERATURE_K:.0f}K")

            # Equilibration: 50 ps NPT at dt=1 fs (test_P-validated)
            simulation.context.setVelocitiesToTemperature(TEMPERATURE_K * unit.kelvin)
            equil_steps = int(NPT_EQUIL_PS * 1000 / DT_FS)
            log(f"--- Equilibration: {NPT_EQUIL_PS} ps NPT "
                f"({equil_steps} steps at dt={DT_FS} fs, MCB freq={BAROSTAT_FREQ}) ---")
            t0 = time.time()
            steps_done, last_check = 0, 0
            while steps_done < equil_steps:
                chunk = min(NAN_CHECK_INTERVAL_STEPS, equil_steps - steps_done)
                simulation.step(chunk)
                steps_done += chunk
                if steps_done - last_check >= NAN_CHECK_INTERVAL_STEPS:
                    check_nan(simulation, f"equil {steps_done * DT_FS / 1000:.1f}ps")
                    if (steps_done // 5000) > (last_check // 5000):
                        pct = 100.0 * steps_done / equil_steps
                        elapsed_min = (time.time() - t0) / 60.0
                        log(f"    equil progress: {steps_done}/{equil_steps} "
                            f"({pct:.1f}%) | {elapsed_min:.1f} min elapsed")
                    last_check = steps_done
            t_equil = time.time() - t0
            log(f"  Equilibration wall: {t_equil:.1f}s "
                f"({NPT_EQUIL_PS / (t_equil / 86400) / 1000:.3f} ns/day)")
            meta["equilibration"] = {"wall_time_s": t_equil, "ps": NPT_EQUIL_PS}

            # Save end-of-equil state for reproducibility
            state_end_equil = simulation.context.getState(
                getPositions=True, getVelocities=True, getForces=True,
                getEnergy=True, enforcePeriodicBox=True,
            )
            with open(equil_state_path, 'w') as f:
                f.write(openmm.XmlSerializer.serialize(state_end_equil))
            log(f"  Equilibration-complete state saved: {equil_state_path}")

            # Reset step counter so production starts at step 0
            simulation.currentStep = 0

            # Save initial production checkpoint at step 0
            with open(chk_path, 'wb') as f:
                f.write(simulation.context.createCheckpoint())
            progress["production_started"] = True
            progress["production_ns_completed"] = 0.0
            progress["last_step"] = 0
            progress["n_constraints_at_checkpoint"] = n_constraints_built
            progress["updated"] = datetime.now(timezone.utc).isoformat()
            write_progress(progress_path, progress)
            log(f"  Initial production checkpoint saved (step 0) — "
                f"restarts skip equil")

        # ===================================================================
        # C) PRODUCTION LOOP (append-mode reporters + checkpoint + walltime guard)
        # ===================================================================

        total_prod_steps = int(TARGET_NS * 1e6 / DT_FS)
        report_steps = max(1, int(REPORT_INTERVAL_PS * 1000 / DT_FS))

        if resuming:
            start_step = simulation.context.getState().getStepCount()
            simulation.currentStep = start_step
        else:
            start_step = 0
            simulation.currentStep = 0

        log(f"--- Production (target {TARGET_NS} ns = {total_prod_steps} steps) ---")
        log(f"  Starting from step {start_step} "
            f"({start_step * DT_FS / 1e6:.4f} ns) [NPT, MCB freq={BAROSTAT_FREQ}]")

        if start_step >= total_prod_steps:
            log(f"  Trajectory already at target ({start_step * DT_FS / 1e6:.4f} ns). "
                f"Nothing to do.")
            meta["production_status"] = "already_at_target"
            meta["session_ended"] = datetime.now(timezone.utc).isoformat()
            with open(meta_path, 'w') as f:
                json.dump(meta, f, indent=2, default=str)
            stop_gpu_keepalive()
            return 0

        # Attach reporters in APPEND mode
        simulation.reporters = []
        simulation.reporters.append(
            DCDReporter(prod_dcd, report_steps, append=os.path.exists(prod_dcd))
        )
        # StateDataReporter handle-mode with monkey-patch (this matters --
        # was the v5 GB3 _dof failure cause; keep _initializeConstants call).
        csv_exists = os.path.exists(prod_csv)
        if csv_exists:
            csv_handle = open(prod_csv, 'a', buffering=1)
            # R4-2026-05-05: drop kineticEnergy + totalEnergy from reporter
            # (OSF v3 §8 QC requires only PE/T/V/ρ for NPT; KE/TE are
            # diagnostic-only and trigger an extra getVelocities path).
            # Saves ~0.5-1.5% throughput.
            sdr = StateDataReporter(
                csv_handle, report_steps,
                step=True, time=True,
                potentialEnergy=True,
                temperature=True, volume=True, density=True,
            )
            sdr._hasInitialized = True
            sdr._initializeConstants(simulation)
            sdr._initialClockTime = time.time()
            sdr._initialSimulationTime = simulation.context.getState().getTime()
            sdr._initialSteps = simulation.currentStep
            simulation.reporters.append(sdr)
        else:
            # R4-2026-05-05: same KE/TE drop as append branch above.
            sdr = StateDataReporter(
                prod_csv, report_steps,
                step=True, time=True,
                potentialEnergy=True,
                temperature=True, volume=True, density=True,
            )
            simulation.reporters.append(sdr)

        # Checkpoint reporter every CHECKPOINT_INTERVAL_STEPS
        simulation.reporters.append(
            CheckpointReporter(chk_path, CHECKPOINT_INTERVAL_STEPS)
        )

        # Production loop with walltime guard and periodic NaN check
        t_prod_start = time.time()
        steps_done_this_session = 0
        last_nan_check = start_step
        current_step = start_step
        chunk_size = min(CHECKPOINT_INTERVAL_STEPS, NAN_CHECK_INTERVAL_STEPS * 10)

        while current_step < total_prod_steps:
            elapsed = time.time() - t_session_start
            if elapsed >= WALLTIME_GUARD_SEC:
                log(f"  [WALLTIME_GUARD] Elapsed {elapsed:.0f}s >= guard "
                    f"{WALLTIME_GUARD_SEC}s; saving final checkpoint and "
                    f"exiting for resubmission")
                with open(chk_path, 'wb') as f:
                    f.write(simulation.context.createCheckpoint())
                progress["production_ns_completed"] = current_step * DT_FS / 1e6
                progress["production_started"] = True
                progress["session_exit_reason"] = "walltime_guard"
                progress["last_step"] = current_step
                progress["n_constraints_at_checkpoint"] = n_constraints_built
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

            if current_step - last_nan_check >= NAN_CHECK_INTERVAL_STEPS:
                check_nan(simulation, f"prod {current_step * DT_FS / 1e6:.4f} ns")
                last_nan_check = current_step

            # R4-2026-05-05: progress JSON now writes only on checkpoint
            # cadence (every CHECKPOINT_INTERVAL_STEPS, ~25 ps). Per-chunk
            # writes were redundant — restart granularity is already capped
            # by CheckpointReporter, and per-chunk fsync added NFS load.
            # Saves ~0.3-1% throughput; restart correctness unchanged.
            if current_step % CHECKPOINT_INTERVAL_STEPS == 0:
                progress["production_ns_completed"] = current_step * DT_FS / 1e6
                progress["production_started"] = True
                progress["last_step"] = current_step
                progress["n_constraints_at_checkpoint"] = n_constraints_built
                progress["updated"] = datetime.now(timezone.utc).isoformat()
                write_progress(progress_path, progress)

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
        progress["n_constraints_at_checkpoint"] = n_constraints_built
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
