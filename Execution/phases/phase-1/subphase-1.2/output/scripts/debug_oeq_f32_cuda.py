"""Debug oeq conversion + f32 dtype + CUDA platform. All three in one run."""
import os, sys, time, traceback
os.environ['PYTHONNOUSERSITE'] = '1'
os.environ['LD_LIBRARY_PATH'] = os.environ.get('CONDA_PREFIX','') + '/lib:' + os.environ.get('LD_LIBRARY_PATH','')

import torch
import numpy as np

def log(msg):
    from datetime import datetime, timezone
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%SZ')}] {msg}", flush=True)

log(f"torch {torch.__version__} | GPU: {torch.cuda.get_device_name(0)}")

from mace.calculators.foundations_models import mace_off

# Load model once
log("Loading MACE-OFF24-medium...")
model = mace_off(model='https://github.com/ACEsuit/mace-off/blob/main/mace_off24/MACE-OFF24_medium.model?raw=true',
                 device='cuda', return_raw_model=True).to('cuda')
for p in model.parameters():
    p.requires_grad = False
log(f"Model loaded: {sum(p.numel() for p in model.parameters())} params")

# === FIX 1: OEQ CONVERSION ===
log("=== OEQ CONVERSION DEBUG ===")
try:
    from mace.cli.convert_e3nn_oeq import run as run_e3nn_to_oeq
    oeq_model = run_e3nn_to_oeq(model, device='cuda')
    log("OEQ conversion: SUCCESS")

    # Quick forward pass test
    from mace.tools import utils, to_one_hot, atomic_numbers_to_indices
    zTable = utils.AtomicNumberTable([int(z) for z in oeq_model.atomic_numbers])
    atoms = [6]*10
    na = to_one_hot(torch.tensor(atomic_numbers_to_indices(atoms, z_table=zTable),
                    dtype=torch.long, device='cuda').unsqueeze(-1),
                    num_classes=len(zTable)).to(torch.float64)
    pos = torch.randn(10, 3, dtype=torch.float64, device='cuda') * 2.0
    dists = torch.cdist(pos.unsqueeze(0), pos.unsqueeze(0)).squeeze(0)
    cutoff = float(oeq_model.r_max.detach())
    mask = (dists < cutoff) & (dists > 1e-8)
    s, r = torch.where(mask)
    inp = {
        'ptr': torch.tensor([0, 10], dtype=torch.long, device='cuda'),
        'node_attrs': na, 'batch': torch.zeros(10, dtype=torch.long, device='cuda'),
        'pbc': torch.tensor([False,False,False], device='cuda'),
        'positions': pos, 'edge_index': torch.stack([s, r]),
        'shifts': torch.zeros((s.shape[0], 3), dtype=torch.float64, device='cuda'),
        'cell': torch.eye(3, dtype=torch.float64, device='cuda') * 100,
        'total_charge': torch.tensor([0.0], dtype=torch.float64, device='cuda'),
        'total_spin': torch.tensor([1.0], dtype=torch.float64, device='cuda'),
    }
    res = oeq_model(inp, compute_force=True)
    log(f"OEQ forward pass: E={float(res['interaction_energy'].detach()):.4f} eV — OK")
except Exception as e:
    log(f"OEQ conversion FAILED: {e}")
    traceback.print_exc()
    # Try to identify the exact attribute that's missing
    log("--- Checking model attributes ---")
    for name, mod in model.named_modules():
        if 'symmetric_contraction' in name.lower() or 'weights' in name.lower():
            log(f"  {name}: {type(mod).__name__}")

# === FIX 2: FLOAT32 ===
log("")
log("=== FLOAT32 DEBUG ===")
try:
    model_f32 = mace_off(model='https://github.com/ACEsuit/mace-off/blob/main/mace_off24/MACE-OFF24_medium.model?raw=true',
                         device='cuda', return_raw_model=True).to('cuda')
    model_f32 = model_f32.to(torch.float32)

    # Check ALL tensors in model
    f64_found = []
    for name, param in model_f32.named_parameters():
        if param.dtype == torch.float64:
            f64_found.append(f"PARAM {name}: {param.dtype}")
    for name, buf in model_f32.named_buffers():
        if buf.dtype == torch.float64:
            f64_found.append(f"BUFFER {name}: {buf.dtype}")
    if f64_found:
        log(f"Found {len(f64_found)} float64 tensors after .float():")
        for x in f64_found[:10]:
            log(f"  {x}")
    else:
        log("No float64 params/buffers — model is clean float32")

    # Try forward pass with float32
    from mace.tools import utils as _u2, to_one_hot as _toh2, atomic_numbers_to_indices as _ani2
    zTable2 = _u2.AtomicNumberTable([int(z) for z in model_f32.atomic_numbers])
    na32 = _toh2(torch.tensor(_ani2([6]*10, z_table=zTable2),
                      dtype=torch.long, device='cuda').unsqueeze(-1),
                      num_classes=len(zTable)).to(torch.float32)
    pos32 = torch.randn(10, 3, dtype=torch.float32, device='cuda') * 2.0
    dists32 = torch.cdist(pos32.unsqueeze(0), pos32.unsqueeze(0)).squeeze(0)
    mask32 = (dists32 < cutoff) & (dists32 > 1e-8)
    s32, r32 = torch.where(mask32)
    inp32 = {
        'ptr': torch.tensor([0, 10], dtype=torch.long, device='cuda'),
        'node_attrs': na32, 'batch': torch.zeros(10, dtype=torch.long, device='cuda'),
        'pbc': torch.tensor([False,False,False], device='cuda'),
        'positions': pos32, 'edge_index': torch.stack([s32, r32]),
        'shifts': torch.zeros((s32.shape[0], 3), dtype=torch.float32, device='cuda'),
        'cell': torch.eye(3, dtype=torch.float32, device='cuda') * 100,
        'total_charge': torch.tensor([0.0], dtype=torch.float32, device='cuda'),
        'total_spin': torch.tensor([1.0], dtype=torch.float32, device='cuda'),
    }

    # Set default dtype to catch any internal tensor creation
    torch.set_default_dtype(torch.float32)
    res32 = model_f32(inp32, compute_force=True)
    torch.set_default_dtype(torch.float64)
    log(f"F32 forward pass: E={float(res32['interaction_energy'].detach()):.4f} eV — OK")
except RuntimeError as e:
    torch.set_default_dtype(torch.float64)
    log(f"F32 FAILED: {e}")
    # Get full traceback to find exact line
    traceback.print_exc()

# === FIX 3: CUDA PLATFORM ===
log("")
log("=== CUDA PLATFORM ===")
import openmm
try:
    plat = openmm.Platform.getPlatformByName('CUDA')
    log(f"CUDA platform object: OK (speed={plat.getSpeed()})")
    # Try creating a minimal context
    sys_test = openmm.System()
    sys_test.addParticle(1.0)
    integ = openmm.VerletIntegrator(0.001)
    try:
        ctx = openmm.Context(sys_test, integ, plat)
        log("CUDA context creation: OK")
        del ctx
    except Exception as e:
        log(f"CUDA context creation FAILED: {e}")
        # Check GPU compute capability
        cc = torch.cuda.get_device_capability()
        log(f"GPU compute capability: sm_{cc[0]}{cc[1]}")
except Exception as e:
    log(f"CUDA platform: {e}")

log("=== ALL DONE ===")
