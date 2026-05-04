"""
Targeted diagnostic: compare GPU NL (torch.cdist) vs matscipy on the actual
WW solvated system. Identifies whether the GPU NL is the source of the
2.15e9 kJ/mol/nm force anomaly.
"""
import os, sys, time, numpy as np
os.environ['PYTHONNOUSERSITE'] = '1'

import torch

def log(msg):
    from datetime import datetime, timezone
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%SZ')}] {msg}", flush=True)

def main():
    log("=== NL COMPARISON DIAGNOSTIC ===")
    log(f"GPU: {torch.cuda.get_device_name(0)}")

    # Build the exact same WW system as production
    import openmm
    from openmm import unit
    from openmm.app import PDBFile, Modeller, ForceField, PME
    from openmmml import MLPotential
    from pdbfixer import PDBFixer

    pdb_path = "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ww.pdb"
    pdb = PDBFile(pdb_path)
    modeller = Modeller(pdb.topology, pdb.positions)

    std_aa = {'ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE',
              'LEU','LYS','MET','PHE','PRO','SER','THR','TRP','TYR','VAL',
              'HID','HIE','HIP','CYX','CYM','ASH','GLH','LYN'}
    non_protein = [r for r in modeller.topology.residues() if r.name not in std_aa]
    if non_protein:
        modeller.delete(non_protein)

    to_delete = []
    for residue in modeller.topology.residues():
        try:
            rid = int(residue.id)
        except ValueError:
            continue
        if rid < 6 or rid > 39:
            to_delete.append(residue)
    if to_delete:
        modeller.delete(to_delete)

    fixer = PDBFixer(filename=pdb_path)
    fixer.findMissingResidues()
    fixer.missingResidues = {}
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(pH=7.0)
    modeller = Modeller(fixer.topology, fixer.positions)

    # Re-crop after PDBFixer (it may add terminal residues)
    non_protein2 = [r for r in modeller.topology.residues() if r.name not in std_aa]
    if non_protein2:
        modeller.delete(non_protein2)
    to_delete2 = []
    for residue in modeller.topology.residues():
        try:
            rid = int(residue.id)
        except ValueError:
            continue
        if rid < 6 or rid > 39:
            to_delete2.append(residue)
    if to_delete2:
        modeller.delete(to_delete2)

    protein_atoms = list(range(modeller.topology.getNumAtoms()))
    n_prot = len(protein_atoms)
    log(f"Protein: {n_prot} atoms")

    ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
    modeller.addHydrogens(ff)
    protein_atoms = list(range(modeller.topology.getNumAtoms()))
    n_prot = len(protein_atoms)

    modeller.addSolvent(ff, padding=1.0*unit.nanometer,
                        ionicStrength=0.15*unit.molar, model='tip3p')
    total = modeller.topology.getNumAtoms()
    log(f"Solvated: {total} atoms (protein={n_prot})")

    # Get initial positions
    positions = np.array([[p.x, p.y, p.z] for p in modeller.positions]) * 10.0  # nm -> Angstrom
    prot_pos = positions[protein_atoms]
    cell_vectors = modeller.topology.getPeriodicBoxVectors()
    cell = np.array([[v.x, v.y, v.z] for v in cell_vectors]) * 10.0  # nm -> Angstrom
    box_lengths = np.diag(cell)

    log(f"Protein positions range: x=[{prot_pos[:,0].min():.1f}, {prot_pos[:,0].max():.1f}] "
        f"y=[{prot_pos[:,1].min():.1f}, {prot_pos[:,1].max():.1f}] "
        f"z=[{prot_pos[:,2].min():.1f}, {prot_pos[:,2].max():.1f}]")
    log(f"Box: {box_lengths[0]:.1f} x {box_lengths[1]:.1f} x {box_lengths[2]:.1f} A")

    # Check min distance to box face
    frac = prot_pos / box_lengths
    min_to_face = np.minimum(frac, 1.0 - frac) * box_lengths
    closest = min_to_face.min()
    log(f"Closest protein atom to box face: {closest:.2f} A")

    # Load MACE model
    from mace.calculators.foundations_models import mace_off
    device = torch.device('cuda:0')
    model = mace_off(model='https://github.com/ACEsuit/mace-off/blob/main/mace_off24/MACE-OFF24_medium.model?raw=true',
                     device=str(device), return_raw_model=True).to(device)
    for p in model.parameters():
        p.requires_grad = False
    cutoff = float(model.r_max.detach())
    log(f"MACE r_max = {cutoff:.1f} A")
    log(f"Safety margin (closest_to_face - cutoff) = {closest - cutoff:.2f} A")

    # === MATSCIPY NL ===
    from mace.data.neighborhood import get_neighborhood
    t0 = time.time()
    ref_edges, ref_shifts, _, ref_cell = get_neighborhood(
        prot_pos, cutoff, [True, True, True], cell)
    t_matscipy = time.time() - t0
    n_ref = ref_edges.shape[1]
    nonzero_shifts = np.any(ref_shifts != 0, axis=1).sum()
    log(f"matscipy: {n_ref} edges in {t_matscipy*1000:.1f}ms, {nonzero_shifts} with nonzero shifts")

    # === GPU NL (torch.cdist) ===
    pos_t = torch.tensor(prot_pos, dtype=torch.float64, device=device)
    t0 = time.time()
    dists = torch.cdist(pos_t.unsqueeze(0), pos_t.unsqueeze(0)).squeeze(0)
    mask = (dists < cutoff) & (dists > 1e-8)
    s, r = torch.where(mask)
    t_gpu = time.time() - t0
    n_gpu = s.shape[0]
    log(f"GPU NL:   {n_gpu} edges in {t_gpu*1000:.1f}ms")

    # === COMPARE ===
    ref_set = set(zip(ref_edges[0].tolist(), ref_edges[1].tolist()))
    gpu_set = set(zip(s.cpu().tolist(), r.cpu().tolist()))
    missing = ref_set - gpu_set
    extra = gpu_set - ref_set
    log(f"Missing from GPU: {len(missing)} | Extra in GPU: {len(extra)}")

    if nonzero_shifts > 0:
        log(f"WARNING: {nonzero_shifts} matscipy edges have nonzero PBC shifts!")
        log("  GPU NL with zero shifts will compute WRONG distances for these pairs")
        log("  This is likely the cause of the force anomaly")

    # === FORCE COMPARISON ===
    from mace.tools import utils, to_one_hot, atomic_numbers_to_indices
    includedAtoms = [list(modeller.topology.atoms())[i] for i in protein_atoms]
    atomicNumbers = [atom.element.atomic_number for atom in includedAtoms]
    dtype = torch.float64
    zTable = utils.AtomicNumberTable([int(z) for z in model.atomic_numbers])
    nodeAttrs = to_one_hot(
        torch.tensor(atomic_numbers_to_indices(atomicNumbers, z_table=zTable),
                     dtype=torch.long, device=device).unsqueeze(-1),
        num_classes=len(zTable)).to(dtype)

    # Force with MATSCIPY edges
    input_matscipy = {
        "ptr": torch.tensor([0, n_prot], dtype=torch.long, device=device),
        "node_attrs": nodeAttrs,
        "batch": torch.zeros(n_prot, dtype=torch.long, device=device),
        "pbc": torch.tensor([True, True, True], dtype=torch.bool, device=device),
        "positions": pos_t,
        "edge_index": torch.tensor(ref_edges, dtype=torch.int64, device=device),
        "shifts": torch.tensor(ref_shifts, dtype=dtype, device=device),
        "cell": torch.tensor(cell, dtype=dtype, device=device),
        "total_charge": torch.tensor([0.0], dtype=dtype, device=device),
        "total_spin": torch.tensor([1.0], dtype=dtype, device=device),
    }
    results_m = model(input_matscipy, compute_force=True)
    f_matscipy = results_m["forces"].detach().cpu().numpy()
    e_matscipy = float(results_m["interaction_energy"].detach())

    # Force with GPU NL edges (zero shifts)
    input_gpu = dict(input_matscipy)
    input_gpu["edge_index"] = torch.stack([s, r])
    input_gpu["shifts"] = torch.zeros((n_gpu, 3), dtype=dtype, device=device)
    results_g = model(input_gpu, compute_force=True)
    f_gpu = results_g["forces"].detach().cpu().numpy()
    e_gpu = float(results_g["interaction_energy"].detach())

    log(f"Energy  matscipy: {e_matscipy:.4f} eV | GPU NL: {e_gpu:.4f} eV | diff: {abs(e_gpu-e_matscipy):.4e}")
    log(f"Max |F| matscipy: {np.max(np.abs(f_matscipy)):.4e} eV/A | GPU NL: {np.max(np.abs(f_gpu)):.4e} eV/A")
    log(f"Force diff max: {np.max(np.abs(f_gpu - f_matscipy)):.4e} eV/A")

    if np.max(np.abs(f_gpu - f_matscipy)) > 0.1:
        log("DIAGNOSIS: GPU NL produces DIFFERENT forces — the zero-shift assumption is wrong for this system")
    else:
        log("DIAGNOSIS: Forces match — issue is elsewhere")

    log("=== DONE ===")

if __name__ == "__main__":
    main()
