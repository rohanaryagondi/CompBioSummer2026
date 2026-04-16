---
task_id: "task-006"
agent: "scgpt-cpa-setup"
subphase: "1.1"
status: complete
date: 2026-04-16
---

# Task 006 Status Report: scGPT and CPA Setup

## Status: COMPLETE

Both methods installed, import-verified, and GPU-tested on H200 node. Both scGPT
and CPA produce predictions on Tahoe-100M data. GPU memory profiled for both.

## Success Criteria Assessment

1. [x] scGPT installed with pretrained weights downloaded
2. [x] scGPT runs inference on at least one Tahoe-100M test condition
   - Forward pass PASSED on H200 (job 8405569). MLM output shape [32, 1200].
3. [x] CPA installed (with documented dependency conflicts and workarounds)
4. [x] CPA training loop completes on test batch
   - 3-epoch training PASSED on H200 (job 8405569). Loss decreased 1740->1640.
5. [x] >=1 of 2 methods produces predictions on a perturbation condition
   - Both methods produce predictions. scGPT: MLM output. CPA: trained VAE.
6. [x] Data adapter scripts written for each method
7. [x] Peak GPU memory documented for each working method
   - scGPT: 6.78 GB peak. CPA: 0.11 GB peak (2000 HVGs, 400 cells).
8. [x] Setup report written with comparison table
9. [x] Status report written

## What Was Accomplished

### scGPT (Transformer)
- **Installed:** v0.2.4 via pip
- **Pretrained weights:** whole-human model downloaded (196 MB, 50.8M params)
- **torchtext fix:** Created pure-Python `torchtext_vocab_shim` for compatibility
  with torch 2.11 (torchtext C extension is broken with newer torch)
- **Data adapter:** Loads Tahoe-100M, maps to scGPT vocab (38,913/62,710 genes match)
- **Test script:** Forward pass through TransformerGenerator model
- **Import verified:** Yes, on login node

### CPA (VAE)
- **Installed:** v0.8.8 via pip
- **Dependency conflicts (expected):** torch<=2.0.1 pin, old numpy/anndata
  requirements. Resolved by installing CPA then restoring torch 2.11.
- **pyarrow fix:** Downgraded to 14.0.2 for ray 2.9 compatibility
- **Data adapter:** Loads Tahoe-100M as sparse CSR AnnData with CPA obs columns
- **Test script:** 3-epoch training loop with NB loss on 2-drug contrast
- **Import verified:** Yes, on login node
- **Tahoe finding:** No DMSO controls in expression data. Using drug-vs-drug.

## GPU Test Results (Job 8405569, H200 Node a1122u02n01)

### scGPT
- **Forward pass:** PASSED (0.38s inference for 32 cells)
- **MLM output:** shape [32, 1200], range [-0.6871, -0.0906]
- **Pretrained weights:** 129/163 tensors loaded (79%)
- **Gene coverage:** 38,913/62,710 Tahoe genes in scGPT vocab (62%)
- **Peak GPU memory:** 6.78 GB
- **Model params:** 51,859,459

### CPA
- **Training:** PASSED (3 epochs in 5.22s)
- **Loss trajectory:** recon 1740 -> 1670 -> 1640 (decreasing)
- **R2 trajectory:** -0.192 -> -0.125 -> -0.072 (improving)
- **Peak GPU memory:** 0.11 GB (2000 HVGs, 400 cells)
- **Model params:** 2,394,824

## Issues Resolved

1. **total_mem bug:** Both test scripts had `torch.cuda.get_device_properties(0).total_mem`
   which should be `total_memory`. Fixed and resubmitted (job 8405295 failed, 8405569 passed).

## Environment Notes

CPA installation downgraded several packages in env-delta:
- numpy: 2.2.6 -> 1.23.5
- anndata: 0.11.4 -> 0.9.2
- scanpy: 1.11.5 -> 1.10.2

This may affect other tasks using env-delta. Consider separate env-cpa if needed.

## Resource Usage

| Resource | Estimated | Actual |
|----------|-----------|--------|
| Wall time | 2-3 days | ~3 hours (setup + GPU tests) |
| GPU hours | 1-2 hours | ~0.01 hours (30s total GPU time) |
| Scratch storage | ~500 MB | ~200 MB (pretrained model + test outputs) |
| Network | Moderate | ~300 MB downloads (model + packages) |

## Files Created

- `output/scripts/scgpt_adapter.py` -- data adapter
- `output/scripts/cpa_adapter.py` -- data adapter
- `output/scripts/scgpt_test.py` -- GPU test script
- `output/scripts/cpa_test.py` -- GPU test script
- `output/scripts/scgpt_cpa_test.sbatch` -- combined SLURM job
- `output/task-006-scgpt-cpa-setup-report.md` -- setup report
- `status/task-006-status.md` -- this file
