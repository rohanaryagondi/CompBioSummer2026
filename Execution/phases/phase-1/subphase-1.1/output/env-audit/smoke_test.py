#!/usr/bin/env python
"""env-delta-v2 GEARS smoke test (on GPU)."""
import os, sys, platform, warnings
warnings.filterwarnings('ignore')

print('=== env-delta-v2 smoke test ===')
print('Python:', platform.python_version())

import numpy, scipy, pandas, anndata, scanpy, torch, networkx
print(f'numpy    {numpy.__version__}')
print(f'scipy    {scipy.__version__}')
print(f'pandas   {pandas.__version__}')
print(f'anndata  {anndata.__version__}')
print(f'scanpy   {scanpy.__version__}')
print(f'torch    {torch.__version__}')
print(f'networkx {networkx.__version__}')

print('torch.cuda.is_available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('device name:', torch.cuda.get_device_name(0))
    print('device count:', torch.cuda.device_count())

import gears
from gears import PertData, GEARS
print('GEARS import OK')

# Sanity: small tensor op on GPU
if torch.cuda.is_available():
    x = torch.randn(32, 32, device='cuda')
    y = x @ x.t()
    torch.cuda.synchronize()
    print('GPU matmul OK, result shape:', tuple(y.shape))

# Sanity: gears_adapter.py still works
sys.path.insert(0, '/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/scripts')
import gears_adapter
m = gears_adapter.load_drug_targets()
mapped = sum(v is not None for v in m.values())
print(f'gears_adapter load_drug_targets: {mapped}/{len(m)}')
assert mapped > 200, 'drug target mapping unexpectedly small'
print('=== SMOKE TEST PASS ===')
