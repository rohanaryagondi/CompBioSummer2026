"""
Diagnostic: isolate whether the float32 matmul dtype mismatch is caused by:
  (A) input size (10 atoms vs 534 atoms), or
  (B) something OpenMM's _computeMACE does that raw model() doesn't.

Tests model(input_dict) directly at WW-domain size (534 atoms) in float32.
Also inspects ScriptModule submodules for float64 constants.
"""
import os, sys, traceback
os.environ['PYTHONNOUSERSITE'] = '1'

import torch
import numpy as np

def log(msg):
    from datetime import datetime, timezone
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%SZ')}] {msg}", flush=True)

log(f"torch {torch.__version__} | GPU: {torch.cuda.get_device_name(0)}")
torch.set_default_dtype(torch.float32)

# === Load model ===
from mace.calculators.foundations_models import mace_off
log("Loading MACE-OFF24-medium...")
model = mace_off(
    model='https://github.com/ACEsuit/mace-off/blob/main/mace_off24/MACE-OFF24_medium.model?raw=true',
    device='cuda', return_raw_model=True
).to('cuda').to(torch.float32)
for p in model.parameters():
    p.requires_grad = False
log(f"Model on CUDA, all params float32: {all(p.dtype==torch.float32 for p in model.parameters())}")

# === Phase 1: Inspect ScriptModule submodules for float64 constants ===
log("")
log("=== PHASE 1: ScriptModule constant inspection ===")
f64_script_constants = []
for name, mod in model.named_modules():
    if isinstance(mod, torch.jit.ScriptModule):
        # Try to inspect parameters/buffers inside the ScriptModule
        try:
            for pname, p in mod.named_parameters():
                if p.dtype == torch.float64:
                    f64_script_constants.append(f"ScriptModule {name}.{pname}: {p.shape} {p.dtype}")
            for bname, b in mod.named_buffers():
                if b.dtype == torch.float64:
                    f64_script_constants.append(f"ScriptModule {name}.{bname}: {b.shape} {b.dtype}")
        except Exception as e:
            log(f"  Cannot inspect {name}: {e}")
    # Also check GraphModule (fx)
    if isinstance(mod, torch.fx.GraphModule):
        for attr_name in dir(mod):
            if attr_name.startswith('_tensor_constant'):
                try:
                    t = getattr(mod, attr_name)
                    if isinstance(t, torch.Tensor) and t.dtype == torch.float64:
                        f64_script_constants.append(f"GraphModule {name}.{attr_name}: {t.shape} {t.dtype}")
                except:
                    pass

if f64_script_constants:
    log(f"FOUND {len(f64_script_constants)} float64 constants in submodules:")
    for c in f64_script_constants:
        log(f"  {c}")
else:
    log("No float64 constants found in ScriptModule/GraphModule submodules")

# === Phase 2: Check graph_opt_main modules specifically ===
log("")
log("=== PHASE 2: graph_opt_main inspection ===")
for name, mod in model.named_modules():
    if 'graph_opt' in name:
        log(f"  {name}: type={type(mod).__name__}")
        if hasattr(mod, 'graph'):
            for node in mod.graph.nodes:
                if node.op == 'get_attr':
                    try:
                        val = getattr(mod, node.target, None)
                        if isinstance(val, torch.Tensor):
                            log(f"    {node.target}: {val.shape} {val.dtype}")
                            if val.dtype == torch.float64:
                                log(f"    *** FLOAT64 CONSTANT FOUND: {node.target} ***")
                    except:
                        pass

# === Phase 3: Build WW-sized input (534 atoms) and test ===
log("")
log("=== PHASE 3: 534-atom forward pass ===")
from openmm.app import PDBFile, Modeller
pdb = PDBFile("/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ww.pdb")
m = Modeller(pdb.topology, pdb.positions)
std = {'ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE','LEU','LYS',
       'MET','PHE','PRO','SER','THR','TRP','TYR','VAL','HID','HIE','HIP','CYX',
       'CYM','ASH','GLH','LYN'}
m.delete([r for r in m.topology.residues() if r.name not in std])
ch0 = list(m.topology.chains())[0].id
oth = []
for c in m.topology.chains():
    if c.id != ch0:
        oth.extend(c.residues())
if oth:
    m.delete(oth)

from openmm import unit as u
positions = np.array([[p.x, p.y, p.z] for p in m.positions]) * 10.0  # nm -> Angstrom
natoms = positions.shape[0]
log(f"WW domain: {natoms} atoms")

# Get atomic numbers
from openmm.app import Element
atomic_nums = []
for a in m.topology.atoms():
    atomic_nums.append(a.element.atomic_number)
log(f"Elements: {set(atomic_nums)}")

# Build MACE input dict
from mace.tools import utils, to_one_hot, atomic_numbers_to_indices
from mace.data.neighborhood import get_neighborhood

zTable = utils.AtomicNumberTable([int(z) for z in model.atomic_numbers])
indices = atomic_numbers_to_indices(atomic_nums, z_table=zTable)
node_attrs = to_one_hot(
    torch.tensor(indices, dtype=torch.long, device='cuda').unsqueeze(-1),
    num_classes=len(zTable)
).to(torch.float32)

cutoff = float(model.r_max.detach())
cell = np.eye(3) * 100.0  # large non-periodic cell
edge_index, shifts, _, _ = get_neighborhood(positions, cutoff, [False, False, False], cell)
log(f"Edges: {edge_index.shape[1]} (cutoff={cutoff:.1f} A)")

input_dict = {
    'ptr': torch.tensor([0, natoms], dtype=torch.long, device='cuda'),
    'node_attrs': node_attrs,
    'batch': torch.zeros(natoms, dtype=torch.long, device='cuda'),
    'pbc': torch.tensor([False, False, False], device='cuda'),
    'positions': torch.tensor(positions, dtype=torch.float32, device='cuda'),
    'edge_index': torch.tensor(edge_index, dtype=torch.long, device='cuda'),
    'shifts': torch.tensor(shifts, dtype=torch.float32, device='cuda'),
    'cell': torch.tensor(cell, dtype=torch.float32, device='cuda'),
    'total_charge': torch.tensor([0.0], dtype=torch.float32, device='cuda'),
    'total_spin': torch.tensor([1.0], dtype=torch.float32, device='cuda'),
}

# Verify all inputs are float32
for k, v in input_dict.items():
    if isinstance(v, torch.Tensor) and v.is_floating_point():
        log(f"  input[{k}]: {v.dtype} {v.shape}")
        assert v.dtype == torch.float32, f"{k} is {v.dtype}!"

log("Calling model(input_dict, compute_force=True)...")
try:
    with torch.no_grad():
        result = model(input_dict, compute_force=True)
    E = float(result['interaction_energy'].detach())
    F = result['forces'].detach()
    log(f"SUCCESS: E={E:.4f} eV, F shape={F.shape}, F dtype={F.dtype}")
    log(">>> Conclusion: the bug is in OpenMM's _computeMACE, NOT the model")
except RuntimeError as e:
    log(f"FAILED: {e}")
    traceback.print_exc()
    log("")
    log(">>> Conclusion: the bug is in the model itself at this input size")
    log(">>> Next: hook into each submodule to find the exact layer")

    # === Phase 4: Hook-based layer-by-layer dtype tracing ===
    log("")
    log("=== PHASE 4: Layer-by-layer dtype trace ===")
    hooks = []
    def make_hook(layer_name):
        def hook_fn(module, input, output):
            # Check inputs
            for i, inp in enumerate(input):
                if isinstance(inp, torch.Tensor) and inp.is_floating_point():
                    if inp.dtype != torch.float32:
                        log(f"  !!! {layer_name} input[{i}]: {inp.dtype} {inp.shape}")
                elif isinstance(inp, dict):
                    for k, v in inp.items():
                        if isinstance(v, torch.Tensor) and v.is_floating_point() and v.dtype != torch.float32:
                            log(f"  !!! {layer_name} input[{i}][{k}]: {v.dtype} {v.shape}")
            # Check output
            if isinstance(output, torch.Tensor) and output.is_floating_point():
                if output.dtype != torch.float32:
                    log(f"  !!! {layer_name} output: {output.dtype} {output.shape}")
            elif isinstance(output, dict):
                for k, v in output.items():
                    if isinstance(v, torch.Tensor) and v.is_floating_point() and v.dtype != torch.float32:
                        log(f"  !!! {layer_name} output[{k}]: {v.dtype} {v.shape}")
        return hook_fn

    for name, mod in model.named_modules():
        if not isinstance(mod, (torch.jit.ScriptModule,)):  # can't hook ScriptModules
            h = mod.register_forward_hook(make_hook(name))
            hooks.append(h)

    log("Running with hooks...")
    try:
        with torch.no_grad():
            result = model(input_dict, compute_force=True)
    except RuntimeError:
        log("(Crashed with hooks — trace above shows the culprit layer)")

    for h in hooks:
        h.remove()

log("")
log("=== DONE ===")
