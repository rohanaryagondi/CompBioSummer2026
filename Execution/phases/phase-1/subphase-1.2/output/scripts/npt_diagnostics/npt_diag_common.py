#!/usr/bin/env python
"""
npt_diag_common.py -- Shared utilities for NPT barostat diagnostic tests.

Provides system-building functions that replicate the exact solvation and
MACE hybrid setup from the production script (mace_hybrid_npt.py) without
modifying it. Each diagnostic test imports from here.

Project: CompBioSummer2026 Sub 1.2 task-001 NPT diagnostics.
"""
from __future__ import annotations

import math
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Any

import numpy as np

# ---------------------------------------------------------------------------
# Constants (matched to production script mace_hybrid_npt.py)
# ---------------------------------------------------------------------------

TEMPERATURE_K = 300.0
PRESSURE_ATM = 1.0
DT_FS = 1.0
FRICTION = 1.0           # 1/ps Langevin friction
BAROSTAT_FREQ = 25       # production default
SOLVENT_PADDING_NM = 1.0
NB_CUTOFF_NM = 1.0
IONIC_STRENGTH_M = 0.15

PDB_PATH = "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ww.pdb"
RESRANGE = "6-39"        # WW domain crop from Pin1 2F21

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def log(msg: str) -> None:
    """Timestamped log line to stdout."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# System building (replicates production script logic exactly)
# ---------------------------------------------------------------------------

def _load_and_crop_pdb():
    """Load WW PDB, strip non-protein het, keep first chain, crop to residues 6-39."""
    from openmm.app import PDBFile, Modeller

    log(f"Loading PDB: {PDB_PATH}")
    pdb = PDBFile(PDB_PATH)
    modeller = Modeller(pdb.topology, pdb.positions)
    log(f"  Raw topology: {modeller.topology.getNumAtoms()} atoms, "
        f"{modeller.topology.getNumResidues()} residues")

    # Delete non-protein het atoms
    std_aa = {
        'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE',
        'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL',
        'HID', 'HIE', 'HIP', 'CYX', 'CYM', 'ASH', 'GLH', 'LYN',
    }
    res_to_delete = [r for r in modeller.topology.residues() if r.name not in std_aa]
    if res_to_delete:
        log(f"  Deleting {len(res_to_delete)} non-protein residues")
        modeller.delete(res_to_delete)

    # Keep only first chain
    first_chain_id = list(modeller.topology.chains())[0].id
    other_chain_residues = []
    for chain in modeller.topology.chains():
        if chain.id != first_chain_id:
            other_chain_residues.extend(chain.residues())
    if other_chain_residues:
        modeller.delete(other_chain_residues)

    # Crop to residue range 6-39
    start_i, end_i = 6, 39
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


def build_ww_system():
    """
    Build solvated WW domain system with AMBER14 + TIP3P-FB.

    Returns:
        tuple: (topology, positions, system, protein_atom_indices)
            - topology: OpenMM Topology
            - positions: OpenMM Positions (Quantity)
            - system: OpenMM System (classical AMBER14, no MACE)
            - protein_atom_indices: list[int] of protein atom indices
    """
    from openmm.app import PDBFile, Modeller, ForceField, PME
    from openmm import unit
    from pdbfixer import PDBFixer
    import tempfile

    modeller = _load_and_crop_pdb()

    # PDBFixer: fill missing atoms, add hydrogens
    log("Running PDBFixer (fill missing heavy atoms, add hydrogens at pH 7)...")
    with tempfile.NamedTemporaryFile(suffix='.pdb', mode='w', delete=False) as f:
        tmp_pdb = f.name
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
    os.unlink(tmp_pdb)
    log(f"  After PDBFixer: {modeller.topology.getNumAtoms()} atoms, "
        f"{modeller.topology.getNumResidues()} residues")

    protein_atom_count = modeller.topology.getNumAtoms()
    protein_atoms = list(range(protein_atom_count))

    # Solvate
    log(f"Adding TIP3P-FB solvent (padding={SOLVENT_PADDING_NM} nm, "
        f"ionic strength={IONIC_STRENGTH_M} M)...")
    ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
    modeller.addSolvent(
        ff,
        padding=SOLVENT_PADDING_NM * unit.nanometer,
        ionicStrength=IONIC_STRENGTH_M * unit.molar,
        model='tip3p',
    )
    total = modeller.topology.getNumAtoms()
    log(f"  After solvation: {total} atoms "
        f"(protein={protein_atom_count}, water+ions={total - protein_atom_count})")

    # Build classical system
    log("Building classical AMBER14 + TIP3P-FB system (PME, 1.0 nm cutoff)...")
    system = ff.createSystem(
        modeller.topology,
        nonbondedMethod=PME,
        nonbondedCutoff=NB_CUTOFF_NM * unit.nanometer,
        constraints=None,
        rigidWater=True,
    )

    return modeller.topology, modeller.positions, system, protein_atoms


def add_mace_hybrid(system, topology, positions, protein_atoms, use_f32=True,
                    apply_wrapping_fix=False):
    """
    Replace classical protein forces with MACE-OFF24-medium hybrid.

    Replicates the exact hybrid construction from mace_hybrid_npt.py,
    including the float32 bypass when use_f32=True.

    Args:
        system: OpenMM System (classical AMBER14)
        topology: OpenMM Topology
        positions: OpenMM Positions
        protein_atoms: list[int] of protein atom indices
        use_f32: if True, apply the f32 bypass (production default)

    Returns:
        OpenMM System with MACE hybrid forces
    """
    import openmm
    from openmm import unit
    from openmmml import MLPotential

    # Vesin neighbor list swap (same as production script)
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

    log(f"Creating hybrid MACE-OFF24-medium system "
        f"({len(protein_atoms)} MACE atoms / {system.getNumParticles()} total)...")
    t0 = time.time()
    potential = MLPotential('mace-off24-medium')

    import torch as _torch

    # Build hybrid system with f64 (always works)
    hybrid_system = potential.createMixedSystem(
        topology, system, protein_atoms, interpolate=False,
    )

    if use_f32:
        try:
            _torch.set_default_dtype(_torch.float32)
            from mace.calculators.foundations_models import mace_off as _mace_off
            from mace.tools import utils as _u, to_one_hot as _toh
            from mace.tools import atomic_numbers_to_indices as _ani
            from mace.data.neighborhood import get_neighborhood as _get_nh
            from functools import partial as _partial

            _f32_model = _mace_off(
                model='https://github.com/ACEsuit/mace-off/blob/main/mace_off24/MACE-OFF24_medium.model?raw=true',
                device='cuda', return_raw_model=True).to('cuda').float()
            for _p in _f32_model.parameters():
                _p.requires_grad = False
            _f32_cutoff = float(_f32_model.r_max.detach())
            _f32_dtype = _torch.float32
            _f32_dev = _torch.device('cuda')
            _incl = [list(topology.atoms())[i] for i in protein_atoms]
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
                if apply_wrapping_fix and periodic:
                    frac = pos @ np.linalg.inv(cell)
                    frac -= np.floor(frac)
                    pos = frac @ cell
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

            # Replace PythonForce with f32 version
            for _i in range(hybrid_system.getNumForces()):
                _force = hybrid_system.getForce(_i)
                if isinstance(_force, openmm.PythonForce):
                    _fg = _force.getForceGroup()
                    _pbc_flag = _force.usesPeriodicBoundaryConditions()
                    hybrid_system.removeForce(_i)
                    _cb = _partial(_f32_compute, model=_f32_model,
                                   ptr=_torch.tensor([0, len(protein_atoms)], dtype=_torch.long, device=_f32_dev),
                                   na=_na,
                                   batch=_torch.zeros(len(protein_atoms), dtype=_torch.long, device=_f32_dev),
                                   pbc_t=_torch.tensor([_pbc]*3, dtype=_torch.bool, device=_f32_dev),
                                   idx=_idx, periodic=_pbc, cutoff=_f32_cutoff, dtype=_f32_dtype, dev=_f32_dev)
                    _nf = openmm.PythonForce(_cb)
                    _nf.setForceGroup(_fg)
                    _nf.setUsesPeriodicBoundaryConditions(_pbc_flag)
                    hybrid_system.addForce(_nf)
                    if apply_wrapping_fix:
                        log("  Using float32 MACE (bypass) WITH minimum-image wrapping fix")
                    else:
                        log("  Using float32 MACE (bypass, production default)")
                    break
        except Exception as _e:
            log(f"  Float32 bypass failed ({_e}), using f64")
            _torch.set_default_dtype(_torch.float64)
    else:
        log("  Using float64 MACE (no f32 bypass)")

    t_sys = time.time() - t0
    log(f"  Hybrid system built in {t_sys:.1f}s: "
        f"{hybrid_system.getNumParticles()} particles, "
        f"{hybrid_system.getNumForces()} forces")

    return hybrid_system


def add_mace_hybrid_v2(system, topology, positions, protein_atoms,
                       use_f32=True, wrap_mode='molecular',
                       simulation_holder=None):
    """
    Replace classical protein forces with MACE-OFF24-medium hybrid (v2 fix).

    Differs from add_mace_hybrid() in the position-preprocessing applied INSIDE
    the PythonForce callback (_f32_compute) before building the MACE neighbor
    list. The original add_mace_hybrid(apply_wrapping_fix=True) used per-atom
    minimum-image wrapping, which DESTROYS protein bond connectivity (bonded
    atoms can land on opposite faces of the box). v2 supports three modes:

      - wrap_mode='molecular': translate the WHOLE protein as a rigid blob so
          its centroid lies in [0, box_a) x [0, box_b) x [0, box_c). This
          preserves all bonds and only shifts the protein by an integer
          combination of box vectors.
      - wrap_mode='enforce_pbc': pull a fresh state from `simulation.context`
          with `enforcePeriodicBox=True`. Requires simulation_holder to be a
          dict-like with key 'simulation' set BEFORE the first force call.
      - wrap_mode='both': enforce_pbc first, then molecular wrap.
      - wrap_mode='none': baseline (matches add_mace_hybrid(apply_wrapping_fix=False)).

    Returns OpenMM System with MACE hybrid forces.
    """
    import openmm
    from openmm import unit
    from openmmml import MLPotential

    import numpy as _np
    from vesin import NeighborList as _VesinNL
    import mace.data.neighborhood as _mace_nh
    import torch as _torch
    from functools import partial as _partial
    from mace.calculators.foundations_models import mace_off as _mace_off
    from mace.tools import utils as _u, to_one_hot as _toh
    from mace.tools import atomic_numbers_to_indices as _ani
    from mace.data.neighborhood import get_neighborhood as _get_nh

    if wrap_mode not in ('molecular', 'enforce_pbc', 'both', 'none'):
        raise ValueError(f"Unknown wrap_mode={wrap_mode!r}")

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

    log(f"Creating hybrid MACE-OFF24-medium system v2 (wrap_mode={wrap_mode}) "
        f"({len(protein_atoms)} MACE atoms / {system.getNumParticles()} total)...")
    t0 = time.time()
    potential = MLPotential('mace-off24-medium')

    hybrid_system = potential.createMixedSystem(
        topology, system, protein_atoms, interpolate=False,
    )

    if not use_f32:
        log("  use_f32=False not supported in v2 fix; falling back to f32")
    _torch.set_default_dtype(_torch.float32)
    _f32_model = _mace_off(
        model='https://github.com/ACEsuit/mace-off/blob/main/mace_off24/MACE-OFF24_medium.model?raw=true',
        device='cuda', return_raw_model=True).to('cuda').float()
    for _p in _f32_model.parameters():
        _p.requires_grad = False
    _f32_cutoff = float(_f32_model.r_max.detach())
    _f32_dtype = _torch.float32
    _f32_dev = _torch.device('cuda')
    _incl = [list(topology.atoms())[i] for i in protein_atoms]
    _anums = [a.element.atomic_number for a in _incl]
    _zt = _u.AtomicNumberTable([int(z) for z in _f32_model.atomic_numbers])
    _na = _toh(_torch.tensor(_ani(_anums, z_table=_zt),
               dtype=_torch.long, device=_f32_dev).unsqueeze(-1),
               num_classes=len(_zt)).to(_f32_dtype)
    _idx = np.array(protein_atoms)
    _pbc = True

    use_enforce = wrap_mode in ('enforce_pbc', 'both')
    use_molecular = wrap_mode in ('molecular', 'both')

    # Holder dict capturing the simulation reference. The user must populate
    # holder['simulation'] AFTER the Simulation is constructed but BEFORE
    # the first step() (or first context.getState that triggers force eval).
    holder = simulation_holder if simulation_holder is not None else {}

    def _f32_compute_v2(state, model, ptr, na, batch, pbc_t, idx, periodic,
                        cutoff, dtype, dev):
        _torch.set_default_dtype(_torch.float32)
        eS, lS = 96.4853, 10.0

        # If wrap_mode requests enforce_pbc, pull a fresh, PBC-enforced state
        # from the simulation context (not the trial-move state passed in).
        if use_enforce and 'simulation' in holder and holder['simulation'] is not None:
            try:
                sim = holder['simulation']
                fresh = sim.context.getState(getPositions=True, enforcePeriodicBox=True)
                pos_full = fresh.getPositions(asNumpy=True).value_in_unit(unit.angstrom)
                cell = fresh.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.angstrom) if periodic else np.identity(3)
            except Exception:
                pos_full = state.getPositions(asNumpy=True).value_in_unit(unit.angstrom)
                cell = state.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.angstrom) if periodic else np.identity(3)
        else:
            pos_full = state.getPositions(asNumpy=True).value_in_unit(unit.angstrom)
            cell = state.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.angstrom) if periodic else np.identity(3)

        nA = pos_full.shape[0]
        pos = pos_full[idx]

        if use_molecular and periodic:
            # Robust molecular reassembly via first-atom reference + minimum image.
            # For each non-first protein atom, choose the periodic image closest to atom 0.
            # This reconstructs a contiguous protein blob even if OpenMM has torn it
            # across the box. Then shift the whole blob so its centroid lies in the
            # primary cell. Bonds are preserved (only integer combinations of cell
            # vectors get added).
            inv_cell = np.linalg.inv(cell)
            ref = pos[0].copy()
            diff = pos - ref                    # (n_protein, 3)
            frac_diff = diff @ inv_cell         # fractional differences
            frac_diff -= np.round(frac_diff)    # nearest periodic image
            pos = ref + frac_diff @ cell        # reassembled
            # Now wrap the centroid into the primary cell
            centroid = pos.mean(axis=0)
            frac_cent = centroid @ inv_cell
            offset_frac = -np.floor(frac_cent)
            pos = pos + offset_frac @ cell      # whole-blob translation

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

    for _i in range(hybrid_system.getNumForces()):
        _force = hybrid_system.getForce(_i)
        if isinstance(_force, openmm.PythonForce):
            _fg = _force.getForceGroup()
            _pbc_flag = _force.usesPeriodicBoundaryConditions()
            hybrid_system.removeForce(_i)
            _cb = _partial(_f32_compute_v2, model=_f32_model,
                           ptr=_torch.tensor([0, len(protein_atoms)],
                                             dtype=_torch.long, device=_f32_dev),
                           na=_na,
                           batch=_torch.zeros(len(protein_atoms),
                                              dtype=_torch.long, device=_f32_dev),
                           pbc_t=_torch.tensor([_pbc]*3, dtype=_torch.bool, device=_f32_dev),
                           idx=_idx, periodic=_pbc, cutoff=_f32_cutoff,
                           dtype=_f32_dtype, dev=_f32_dev)
            _nf = openmm.PythonForce(_cb)
            _nf.setForceGroup(_fg)
            _nf.setUsesPeriodicBoundaryConditions(_pbc_flag)
            hybrid_system.addForce(_nf)
            log(f"  v2 callback installed (wrap_mode={wrap_mode}, "
                f"use_enforce={use_enforce}, use_molecular={use_molecular})")
            break

    t_sys = time.time() - t0
    log(f"  Hybrid v2 system built in {t_sys:.1f}s: "
        f"{hybrid_system.getNumParticles()} particles, "
        f"{hybrid_system.getNumForces()} forces")

    return hybrid_system, holder


def add_protein_sentinel_bonds(hybrid_system, topology, protein_atom_indices):
    """
    Add zero-strength HarmonicBondForce bonds along the protein bonded graph
    so that OpenMM's findMolecules() correctly identifies the protein region
    as one connected molecule.

    Workaround for openmm-ml issue #91: createMixedSystem(...) calls
    _removeBonds(system, ml_atoms, allInSet=True, removeConstraints=True),
    which strips all HarmonicBond / HarmonicAngle / PeriodicTorsion / HBonds
    constraints whose atoms all lie in the ML subset. The MACE PythonForce
    wrapper does not implement getBondedParticles(), so OpenMM's
    ContextImpl::findMolecules() sees no connectivity for the ML atoms and
    treats every protein atom as a singleton "molecule." Then
    MonteCarloBarostatImpl::scaleCoordinates and enforcePeriodicBox act
    per-atom on the protein, scaling/re-imaging each protein atom
    independently. Bonded distances are progressively destroyed and MACE
    returns NaN within ~3.5-25 ps (Round 1 Test I observation: WW protein
    span_y went from 24 Å to 44.6 Å > box_b 43.86 Å between probe call
    6789 and 6799, with NaN at call 6800).

    The fix walks topology.bonds() (which PDBFixer populates correctly for
    backbone + side chains) and adds a HarmonicBondForce with k=0 for each
    bond where BOTH atoms are in the ML subset. These contribute exactly
    zero force and zero energy but are visible to findMolecules(), gluing
    the protein into a single molecule for barostat / PBC purposes.

    Args:
        hybrid_system: OpenMM System produced by createMixedSystem
        topology: OpenMM Topology used to build the system
        protein_atom_indices: iterable of int — the ML-subset atom indices

    Returns:
        int: number of sentinel bonds added.
    """
    import openmm
    from openmm import unit

    sentinel = openmm.HarmonicBondForce()
    # Zero-force bonds; PBC choice is irrelevant since k = 0 nullifies any
    # contribution. Setting False keeps the energy expression identical
    # regardless of box state.
    sentinel.setUsesPeriodicBoundaryConditions(False)

    protein_set = set(int(i) for i in protein_atom_indices)
    n_added = 0
    for bond in topology.bonds():
        i = bond.atom1.index
        j = bond.atom2.index
        if i in protein_set and j in protein_set:
            sentinel.addBond(
                i, j,
                0.1 * unit.nanometer,
                0.0 * unit.kilojoule_per_mole / unit.nanometer ** 2,
            )
            n_added += 1

    hybrid_system.addForce(sentinel)
    log(f"  add_protein_sentinel_bonds: added {n_added} zero-k HarmonicBondForce "
        f"sentinel bonds (covers {len(protein_set)} ML atoms)")
    return n_added


def add_protein_hbonds_constraints(hybrid_system, topology, protein_atom_indices):
    """
    Re-add HBonds constraints (heavy-atom-to-H rigid bonds) for the protein
    region of an openmm-ml hybrid system.

    Workaround for the second-order failure mode observed in test_J (Round 2):
    after the sentinel-bond fix made the protein a single molecule for
    findMolecules() purposes, NPT still crashed at 12.5 ps. The likely cause:
    the original classical AMBER14 system was built with constraints=None
    (matching test_J), so protein C-H/N-H/O-H bonds are unconstrained at
    integration time. With dt=1 fs, the C-H stretching mode (~3000 cm^-1,
    period ~10 fs) is at the edge of integrator stability. Once
    MonteCarloBarostat starts perturbing positions, the unconstrained-H
    instability is no longer dominated by Langevin friction, and energy
    accumulates → NaN.

    This function builds a parallel AMBER14 + HBonds reference system
    (matching topology), extracts the heavy-atom-H constraint list, filters
    to those whose atoms are both in the protein subset, and adds them to
    hybrid_system. This restores rigid C-H/N-H/O-H bonds for the protein,
    eliminating the 1 fs unconstrained-H instability without changing any
    other physics.

    Args:
        hybrid_system: OpenMM System produced by createMixedSystem
        topology: OpenMM Topology used to build the system
        protein_atom_indices: iterable of int — the ML-subset atom indices

    Returns:
        int: number of constraints added.
    """
    from openmm.app import ForceField, PME, HBonds
    from openmm import unit
    log("  add_protein_hbonds_constraints: building reference AMBER14 + HBonds "
        "system to extract correct constraint distances...")
    ref_ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
    ref_system = ref_ff.createSystem(
        topology,
        nonbondedMethod=PME,
        nonbondedCutoff=NB_CUTOFF_NM * unit.nanometer,
        constraints=HBonds,
        rigidWater=True,
    )

    protein_set = set(int(i) for i in protein_atom_indices)
    n_added = 0
    n_skipped = 0
    for c_idx in range(ref_system.getNumConstraints()):
        i, j, dist = ref_system.getConstraintParameters(c_idx)
        if i in protein_set and j in protein_set:
            hybrid_system.addConstraint(i, j, dist)
            n_added += 1
        else:
            n_skipped += 1
    log(f"  add_protein_hbonds_constraints: added {n_added} HBonds constraints "
        f"to hybrid_system (skipped {n_skipped} non-protein constraints; "
        f"hybrid_system now has {hybrid_system.getNumConstraints()} constraints)")
    return n_added


def _get_state_data(simulation):
    """Extract temperature, pressure (if NPT), density, energy from current state."""
    from openmm import unit

    state = simulation.context.getState(
        getPositions=True, getForces=True, getEnergy=True,
        getVelocities=True, enforcePeriodicBox=True,
    )

    # Positions / forces / energy
    pos = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
    forces = state.getForces(asNumpy=True).value_in_unit(
        unit.kilojoules_per_mole / unit.nanometer)
    pe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
    ke = state.getKineticEnergy().value_in_unit(unit.kilojoules_per_mole)

    # Temperature from kinetic energy: T = 2*KE / (n_dof * k_B)
    n_particles = simulation.system.getNumParticles()
    n_constraints = simulation.system.getNumConstraints()
    n_dof = max(3 * n_particles - n_constraints - 3, 1)
    kB = 8.314462618e-3  # kJ/mol/K
    temperature = 2.0 * ke / (n_dof * kB)

    # Box volume and density
    box = state.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.nanometer)
    volume_nm3 = abs(np.dot(box[0], np.cross(box[1], box[2])))

    # Rough density estimate: total mass / volume
    # Use average mass ~18 g/mol per water molecule as a quick estimate
    # More accurate: sum all particle masses
    total_mass_amu = 0.0
    for i in range(n_particles):
        total_mass_amu += simulation.system.getParticleMass(i).value_in_unit(unit.dalton)
    # Convert: amu -> g, nm^3 -> cm^3, then g/cm^3
    avogadro = 6.02214076e23
    total_mass_g = total_mass_amu / avogadro
    volume_cm3 = volume_nm3 * 1e-21
    density = total_mass_g / volume_cm3 if volume_cm3 > 0 else 0.0

    # Check for NaN
    has_nan = (np.any(np.isnan(pos)) or np.any(np.isnan(forces)) or
               np.isnan(pe) or np.isnan(ke))
    max_force = float(np.max(np.abs(forces)))

    return {
        "temperature_K": temperature,
        "density_g_cm3": density,
        "volume_nm3": volume_nm3,
        "potential_energy_kJ_mol": pe,
        "kinetic_energy_kJ_mol": ke,
        "total_energy_kJ_mol": pe + ke,
        "max_force_kJ_mol_nm": max_force,
        "has_nan": has_nan,
        "n_particles": n_particles,
    }


def run_npt_test(simulation, test_name: str, n_steps: int,
                 check_interval: int = 1000) -> dict:
    """
    Run simulation steps with periodic NaN checking.

    Args:
        simulation: OpenMM Simulation
        test_name: descriptive name for logging
        n_steps: total steps to run
        check_interval: steps between NaN checks

    Returns:
        dict with keys: passed (bool), final_step, failure_step (if failed),
        temperature_K, density_g_cm3, potential_energy_kJ_mol, total_energy_kJ_mol,
        max_force_kJ_mol_nm, wall_time_s, steps_completed, error (if failed)
    """
    log(f"=== {test_name}: Running {n_steps} steps ===")
    t0 = time.time()
    steps_done = 0
    failure_step = None
    error_msg = None

    try:
        while steps_done < n_steps:
            chunk = min(check_interval, n_steps - steps_done)
            simulation.step(chunk)
            steps_done += chunk

            # Check state
            data = _get_state_data(simulation)
            if data["has_nan"]:
                failure_step = steps_done
                error_msg = f"NaN detected at step {steps_done}"
                log(f"  FAIL: {error_msg}")
                break

            if data["max_force_kJ_mol_nm"] > 1e8:
                failure_step = steps_done
                error_msg = (f"Extreme forces ({data['max_force_kJ_mol_nm']:.1e}) "
                             f"at step {steps_done}")
                log(f"  FAIL: {error_msg}")
                break

            # Progress log every 5000 steps
            if steps_done % 5000 == 0 or steps_done == n_steps:
                ps = steps_done * DT_FS / 1000.0
                elapsed = time.time() - t0
                log(f"  step {steps_done}/{n_steps} ({ps:.1f} ps) | "
                    f"T={data['temperature_K']:.1f} K | "
                    f"rho={data['density_g_cm3']:.4f} g/cm3 | "
                    f"E_pot={data['potential_energy_kJ_mol']:.0f} kJ/mol | "
                    f"max|F|={data['max_force_kJ_mol_nm']:.2e} | "
                    f"wall={elapsed:.1f}s")

    except Exception as e:
        failure_step = steps_done
        error_msg = f"Exception at step {steps_done}: {e}"
        log(f"  FAIL: {error_msg}")
        log(traceback.format_exc())

    wall_time = time.time() - t0
    passed = failure_step is None

    # Get final state data (might be NaN if failed)
    try:
        final = _get_state_data(simulation)
    except Exception:
        final = {
            "temperature_K": float('nan'),
            "density_g_cm3": float('nan'),
            "potential_energy_kJ_mol": float('nan'),
            "total_energy_kJ_mol": float('nan'),
            "max_force_kJ_mol_nm": float('nan'),
        }

    # Compute effective timestep for throughput
    # (some tests change dt; use simulation's actual integrator dt)
    try:
        from openmm import unit
        actual_dt_fs = simulation.integrator.getStepSize().value_in_unit(unit.femtosecond)
    except Exception:
        actual_dt_fs = DT_FS

    ns_simulated = steps_done * actual_dt_fs / 1e6
    throughput = (ns_simulated / wall_time * 86400) if wall_time > 0 else 0.0

    result = {
        "test_name": test_name,
        "passed": passed,
        "steps_completed": steps_done,
        "steps_requested": n_steps,
        "failure_step": failure_step,
        "error": error_msg,
        "temperature_K": final["temperature_K"],
        "density_g_cm3": final["density_g_cm3"],
        "potential_energy_kJ_mol": final["potential_energy_kJ_mol"],
        "total_energy_kJ_mol": final["total_energy_kJ_mol"],
        "max_force_kJ_mol_nm": final["max_force_kJ_mol_nm"],
        "wall_time_s": wall_time,
        "throughput_ns_per_day": throughput,
        "timestep_fs": actual_dt_fs,
        "simulated_ps": steps_done * actual_dt_fs / 1000.0,
    }

    # Print summary
    log("")
    log("=" * 65)
    status = "PASS" if passed else "FAIL"
    log(f"  {test_name}: {status}")
    log(f"  Steps completed: {steps_done}/{n_steps}")
    log(f"  Simulated time:  {result['simulated_ps']:.1f} ps")
    log(f"  Wall time:       {wall_time:.1f} s")
    log(f"  Throughput:      {throughput:.3f} ns/day")
    if passed:
        log(f"  Temperature:     {final['temperature_K']:.1f} K")
        log(f"  Density:         {final['density_g_cm3']:.4f} g/cm3")
        log(f"  Potential E:     {final['potential_energy_kJ_mol']:.0f} kJ/mol")
        log(f"  Max |Force|:     {final['max_force_kJ_mol_nm']:.2e} kJ/mol/nm")
    else:
        log(f"  Failure step:    {failure_step}")
        log(f"  Error:           {error_msg}")
    log("=" * 65)

    return result


def minimize_and_prep(simulation, topology, positions):
    """
    Set positions, minimize, run 10-step self-test, set velocities.
    Replicates the exact production script flow before equilibration.

    Args:
        simulation: OpenMM Simulation (already constructed)
        topology: topology (for logging)
        positions: initial positions
    """
    from openmm import unit

    simulation.context.setPositions(positions)

    log("Minimizing (max 2000 iter, tol 10 kJ/mol/nm)...")
    t0 = time.time()
    simulation.minimizeEnergy(
        maxIterations=2000,
        tolerance=10 * unit.kilojoule_per_mole / unit.nanometer,
    )
    t_min = time.time() - t0

    # Post-min max-force check
    state = simulation.context.getState(getForces=True)
    forces = state.getForces(asNumpy=True).value_in_unit(
        unit.kilojoules_per_mole / unit.nanometer)
    max_f = float(np.max(np.abs(forces)))
    log(f"  Post-min max |force|: {max_f:.2e} kJ/mol/nm (wall {t_min:.1f}s)")
    if max_f > 1e5:
        raise RuntimeError(f"Post-min max force {max_f:.2e} exceeds 1e5 threshold")

    # 10-step self-test
    log("Self-test: 10 integration steps...")
    simulation.step(10)
    data = _get_state_data(simulation)
    if data["has_nan"]:
        raise RuntimeError("NaN in 10-step self-test")
    log(f"  Self-test PASSED (max|F|={data['max_force_kJ_mol_nm']:.2e})")

    # Set velocities
    simulation.context.setVelocitiesToTemperature(TEMPERATURE_K * unit.kelvin)
    log(f"  Velocities initialized at {TEMPERATURE_K} K")


def run_equilibration(simulation, equil_ps: float, dt_fs: float, label: str = "equil"):
    """
    Run equilibration phase with progress logging and NaN checks.

    Args:
        simulation: OpenMM Simulation
        equil_ps: equilibration length in picoseconds
        dt_fs: timestep in femtoseconds (for step count calculation)
        label: label for log messages
    """
    equil_steps = int(equil_ps * 1000 / dt_fs)
    log(f"--- {label}: {equil_ps} ps ({equil_steps} steps at dt={dt_fs} fs) ---")
    t0 = time.time()
    steps_done = 0
    check_interval = 1000

    while steps_done < equil_steps:
        chunk = min(check_interval, equil_steps - steps_done)
        simulation.step(chunk)
        steps_done += chunk

        # Check for NaN
        data = _get_state_data(simulation)
        if data["has_nan"]:
            raise RuntimeError(f"NaN during {label} at step {steps_done} "
                               f"({steps_done * dt_fs / 1000:.1f} ps)")

        # Progress log every 5000 steps
        if steps_done % 5000 == 0:
            elapsed = time.time() - t0
            ps = steps_done * dt_fs / 1000.0
            log(f"  {label}: {steps_done}/{equil_steps} ({ps:.1f} ps) | "
                f"T={data['temperature_K']:.1f} K | "
                f"rho={data['density_g_cm3']:.4f} g/cm3 | "
                f"wall={elapsed:.1f}s")

    t_equil = time.time() - t0
    log(f"  {label} complete: {equil_ps} ps in {t_equil:.1f}s")


# ---------------------------------------------------------------------------
# GPU keepalive (same as production script)
# ---------------------------------------------------------------------------

import threading as _threading
_keepalive_stop = _threading.Event()

def _gpu_keepalive_loop():
    try:
        import torch
        if not torch.cuda.is_available():
            return
        dev = torch.device('cuda:0')
        x = torch.randn(64, 64, device=dev)
        while not _keepalive_stop.is_set():
            y = torch.matmul(x, x).sum().item()
            torch.cuda.synchronize()
            _keepalive_stop.wait(300)
    except Exception:
        pass

def start_gpu_keepalive():
    t = _threading.Thread(target=_gpu_keepalive_loop, daemon=True, name='gpu-keepalive')
    t.start()
    log("Started GPU keepalive thread (5-min cadence)")
    return t

def stop_gpu_keepalive():
    _keepalive_stop.set()
