"""
Minimal NL diagnostic: Does get_neighborhood produce nonzero PBC shifts
for a protein-sized cluster centered in a solvation box?
Tests with realistic WW-like geometry. No system building needed.
"""
import os, numpy as np, time
os.environ['PYTHONNOUSERSITE'] = '1'
import torch

def log(msg):
    from datetime import datetime, timezone
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%SZ')}] {msg}", flush=True)

log("=== NL SHIFT DIAGNOSTIC ===")
log(f"GPU: {torch.cuda.get_device_name(0)}")

from mace.data.neighborhood import get_neighborhood
from mace.calculators.foundations_models import mace_off

device = torch.device('cuda:0')
model = mace_off(model='https://github.com/ACEsuit/mace-off/blob/main/mace_off24/MACE-OFF24_medium.model?raw=true',
                 device=str(device), return_raw_model=True).to(device)
cutoff = float(model.r_max.detach())
log(f"MACE cutoff = {cutoff:.1f} A")

# Simulate WW-like protein: 534 atoms in a compact cluster, centered in a ~40A box
np.random.seed(42)
# Compact cluster: atoms within a 15A sphere centered at (20, 20, 20)
center = np.array([20.0, 20.0, 20.0])
pos = center + np.random.randn(534, 3) * 3.0  # ~15A diameter cluster
box = np.diag([40.0, 40.0, 40.0])  # 40A box, 10A padding on each side

log(f"Protein range: x=[{pos[:,0].min():.1f},{pos[:,0].max():.1f}] "
    f"y=[{pos[:,1].min():.1f},{pos[:,1].max():.1f}] "
    f"z=[{pos[:,2].min():.1f},{pos[:,2].max():.1f}]")
frac = pos / np.diag(box)
min_to_face = np.minimum(frac, 1.0 - frac) * np.diag(box)
log(f"Closest to box face: {min_to_face.min():.1f} A (cutoff={cutoff:.1f})")

# Test 1: Centered cluster (should have zero shifts)
edges, shifts, _, _ = get_neighborhood(pos, cutoff, [True, True, True], box)
nonzero = np.any(shifts != 0, axis=1).sum()
log(f"Test 1 (centered, 10A pad): {edges.shape[1]} edges, {nonzero} nonzero shifts")

# Test 2: Cluster near box edge (should have nonzero shifts)
pos_edge = pos.copy()
pos_edge[:, 0] += 15.0  # shift to x=35, within 5A of box face at x=40
edges2, shifts2, _, _ = get_neighborhood(pos_edge, cutoff, [True, True, True], box)
nonzero2 = np.any(shifts2 != 0, axis=1).sum()
log(f"Test 2 (near edge, 5A pad): {edges2.shape[1]} edges, {nonzero2} nonzero shifts")

# Test 3: Use the ACTUAL WW PDB coordinates
log("--- Test 3: Real WW PDB ---")
from openmm.app import PDBFile, Modeller, ForceField
from pdbfixer import PDBFixer
import tempfile

pdb = PDBFile("/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ww.pdb")
modeller = Modeller(pdb.topology, pdb.positions)
std_aa = {'ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE',
          'LEU','LYS','MET','PHE','PRO','SER','THR','TRP','TYR','VAL',
          'HID','HIE','HIP','CYX','CYM','ASH','GLH','LYN'}
non_prot = [r for r in modeller.topology.residues() if r.name not in std_aa]
if non_prot:
    modeller.delete(non_prot)
first_chain = list(modeller.topology.chains())[0].id
other = []
for c in modeller.topology.chains():
    if c.id != first_chain:
        other.extend(c.residues())
if other:
    modeller.delete(other)
to_del = []
for r in modeller.topology.residues():
    try:
        rid = int(r.id)
    except ValueError:
        continue
    if rid < 6 or rid > 39:
        to_del.append(r)
if to_del:
    modeller.delete(to_del)

# Write temp PDB, run PDBFixer on it (matching production flow)
with tempfile.NamedTemporaryFile(suffix='.pdb', mode='w', delete=False) as f:
    PDBFile.writeFile(modeller.topology, modeller.positions, f)
    tmp_pdb = f.name
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

n_prot = modeller.topology.getNumAtoms()
prot_atoms = list(range(n_prot))
log(f"Protein after PDBFixer: {n_prot} atoms")

ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
modeller.addSolvent(ff, padding=1.0 * __import__('openmm').unit.nanometer,
                    ionicStrength=0.15 * __import__('openmm').unit.molar, model='tip3p')
total = modeller.topology.getNumAtoms()

all_pos = np.array([[p.x, p.y, p.z] for p in modeller.positions]) * 10.0
real_prot_pos = all_pos[prot_atoms]
cell_v = modeller.topology.getPeriodicBoxVectors()
real_cell = np.array([[v.x, v.y, v.z] for v in cell_v]) * 10.0
real_box = np.diag(real_cell)

log(f"Solvated: {total} atoms, box={real_box[0]:.1f}x{real_box[1]:.1f}x{real_box[2]:.1f} A")
log(f"Protein pos range: x=[{real_prot_pos[:,0].min():.1f},{real_prot_pos[:,0].max():.1f}] "
    f"y=[{real_prot_pos[:,1].min():.1f},{real_prot_pos[:,1].max():.1f}] "
    f"z=[{real_prot_pos[:,2].min():.1f},{real_prot_pos[:,2].max():.1f}]")
frac_real = real_prot_pos / real_box
min_face_real = np.minimum(frac_real, 1.0 - frac_real) * real_box
log(f"Closest protein atom to face: {min_face_real.min():.2f} A")

edges3, shifts3, _, _ = get_neighborhood(real_prot_pos, cutoff, [True, True, True], real_cell)
nonzero3 = np.any(shifts3 != 0, axis=1).sum()
log(f"Real WW: {edges3.shape[1]} edges, {nonzero3} nonzero shifts")

if nonzero3 > 0:
    log("ROOT CAUSE CONFIRMED: Real WW system has PBC-crossing edges!")
    log("GPU NL with zero shifts CANNOT work for this system")
    log("FIX: Use matscipy in the PythonForce callback (revert to original path)")
    # Show which atoms cross
    cross_mask = np.any(shifts3 != 0, axis=1)
    cross_edges = edges3[:, cross_mask]
    for i in range(min(5, cross_edges.shape[1])):
        a, b = cross_edges[0, i], cross_edges[1, i]
        d_raw = np.linalg.norm(real_prot_pos[a] - real_prot_pos[b])
        d_pbc = np.linalg.norm(real_prot_pos[a] - real_prot_pos[b] + shifts3[cross_mask][i])
        log(f"  Edge {a}->{b}: raw dist={d_raw:.1f}, PBC dist={d_pbc:.1f} A")
else:
    log("NO PBC-crossing edges for real WW system")
    log("GPU NL with zero shifts should be correct")
    log("Force anomaly has a different root cause — investigate further")

    # Do force comparison
    from mace.tools import utils, to_one_hot, atomic_numbers_to_indices
    atomicNumbers = [a.element.atomic_number for a in list(modeller.topology.atoms())[:n_prot]]
    dtype = torch.float64
    zTable = utils.AtomicNumberTable([int(z) for z in model.atomic_numbers])
    nodeAttrs = to_one_hot(
        torch.tensor(atomic_numbers_to_indices(atomicNumbers, z_table=zTable),
                     dtype=torch.long, device=device).unsqueeze(-1),
        num_classes=len(zTable)).to(dtype)
    pos_t = torch.tensor(real_prot_pos, dtype=dtype, device=device)

    inp = {
        "ptr": torch.tensor([0, n_prot], dtype=torch.long, device=device),
        "node_attrs": nodeAttrs, "batch": torch.zeros(n_prot, dtype=torch.long, device=device),
        "pbc": torch.tensor([True,True,True], dtype=torch.bool, device=device),
        "positions": pos_t,
        "edge_index": torch.tensor(edges3, dtype=torch.int64, device=device),
        "shifts": torch.tensor(shifts3, dtype=dtype, device=device),
        "cell": torch.tensor(real_cell, dtype=dtype, device=device),
        "total_charge": torch.tensor([0.0], dtype=dtype, device=device),
        "total_spin": torch.tensor([1.0], dtype=dtype, device=device),
    }
    r1 = model(inp, compute_force=True)
    e1 = float(r1["interaction_energy"].detach())
    f1 = r1["forces"].detach().cpu().numpy()

    # Same but zero shifts
    inp2 = dict(inp)
    s, r = torch.where((torch.cdist(pos_t.unsqueeze(0), pos_t.unsqueeze(0)).squeeze(0) < cutoff) &
                        (torch.cdist(pos_t.unsqueeze(0), pos_t.unsqueeze(0)).squeeze(0) > 1e-8))
    inp2["edge_index"] = torch.stack([s, r])
    inp2["shifts"] = torch.zeros((s.shape[0], 3), dtype=dtype, device=device)
    r2 = model(inp2, compute_force=True)
    e2 = float(r2["interaction_energy"].detach())
    f2 = r2["forces"].detach().cpu().numpy()

    log(f"Energy: matscipy={e1:.4f} | GPU_NL={e2:.4f} | diff={abs(e2-e1):.4e} eV")
    log(f"Max|F|: matscipy={np.max(np.abs(f1)):.4e} | GPU_NL={np.max(np.abs(f2)):.4e} eV/A")
    log(f"Max force diff: {np.max(np.abs(f2-f1)):.4e} eV/A")

log("=== DONE ===")
