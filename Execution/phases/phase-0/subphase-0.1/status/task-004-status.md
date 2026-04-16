---
task_id: "task-004"
agent: "bioemu-test"
status: completed
started: 2026-04-15T16:45:00Z
completed: 2026-04-16T02:30:00Z
---

# Task 004 Status Report: BioEmu Disulfide Bond Test

## Summary

**COMPLETED.** BioEmu v1.3.1 successfully generated 100 conformations each for
BPTI and HEWL. Disulfide bond integrity was measured using CB-CB distances
(BioEmu outputs only backbone atoms, no SG). T3 is NOT MET. AK3 is TRIGGERED
for BPTI at all cutoffs; HEWL's AK3 status depends on cutoff choice.

## SLURM Job History

| Job ID | Partition | Status | Issue |
|--------|-----------|--------|-------|
| 8350490 | gpu_devel | FAILED | torch cu130 incompatible with CUDA 12.8 driver |
| 8352672 | gpu_devel | FAILED | `torch.cuda.get_device_properties(0).total_mem` → `total_memory` typo |
| 8361635 | scavenge_gpu | FAILED | tensorflow-cpu 2.21.0 + protobuf 4.25.9 import crash |
| 8366491 | gpu_devel | FAILED | Same TF import issue (stale 2.21 _api files) |
| 8371739 | scavenge_gpu | FAILED | Likely preempted |
| **8371740** | **gpu_devel** | **COMPLETED** | **Success — RTX 5000 Ada, 33.8 GB VRAM** |

### Environment Fixes Applied

1. `pip install 'torch==2.7.1+cu128'` — fixed CUDA compatibility
2. `pip install --force-reinstall 'tensorflow-cpu>=2.15,<2.16'` — resolved protobuf
   descriptor clash between tensorflow-cpu 2.21 and jaxlib 0.4.35
3. `torch.cuda.get_device_properties(0).total_memory` — fixed PyTorch 2.7 attribute name
4. Added `BIOEMU_EMBEDS_CACHE` env var and `cache_embeds_dir` parameter to bioemu call

Final env-bioemu stack: torch 2.7.1+cu128, tensorflow-cpu 2.15.1, protobuf 4.25.9,
jax 0.4.35, bioemu 1.3.1.

## Results

### Key Finding: BioEmu outputs backbone only (5 atoms/residue)

BioEmu generates N, CA, C, CB, O — **no sidechain atoms**. This means SG atoms
for cysteine are not available. All SS distances are CB-CB, not SG-SG.

### BPTI (57 residues, 3 SS bonds, 98 conformations passed filter)

| Cutoff | Overall | Cys5-55 | Cys14-38 | Cys30-51 |
|--------|---------|---------|----------|----------|
| 4.5 A | 56.1% | 86.7% | 57.1% | 90.8% |
| 5.0 A | 67.3% | 88.8% | 67.3% | 90.8% |

Generation time: 266.2s (4.4 min).

### HEWL (129 residues, 4 SS bonds, 99 conformations passed filter)

| Cutoff | Overall | Cys6-127 | Cys30-115 | Cys64-80 | Cys76-94 |
|--------|---------|----------|-----------|----------|----------|
| 4.5 A | 70.7% | 90.9% | 97.0% | 92.9% | 88.9% |
| 5.0 A | 90.9% | 94.9% | 98.0% | 100.0% | 98.0% |

Generation time: 569.8s (9.5 min).

### Threshold Assessment (at 4.5 A primary cutoff)

- **T3 (>95%):** NOT MET for both proteins
- **AK3 (<80%):** TRIGGERED for BPTI (56.1%), TRIGGERED for HEWL (70.7%)

## Checklist

- [x] 100 BioEmu conformations generated for BPTI (98 passed filter)
- [x] 100 BioEmu conformations generated for HEWL (99 passed filter)
- [x] SS distances computed (CB-CB proxy)
- [x] Distribution plots generated
- [x] Threshold assessment documented
- [x] Cross-agent note written (`shared/notes/0.1-bioemu-disulfide.md`)
- [x] Status report written

## Output Artifacts

| Path | Description |
|------|-------------|
| `output/task-004-bpti/topology.pdb` + `samples.xtc` | BPTI conformations (98 frames) |
| `output/task-004-hewl/topology.pdb` + `samples.xtc` | HEWL conformations (99 frames) |
| `output/task-004-bpti-ss-distances.csv` | BPTI CB-CB distances per conformation |
| `output/task-004-hewl-ss-distances.csv` | HEWL CB-CB distances per conformation |
| `output/task-004-bpti-ss-plot.png` | BPTI SS distribution plot |
| `output/task-004-hewl-ss-plot.png` | HEWL SS distribution plot |
| `output/task-004-combined-ss-histogram.png` | Combined histogram |
| `output/task-004-ss-integrity-report.md` | Full integrity report with threshold assessment |
| `output/task-004-results.json` | Raw results JSON |

## Notes

- BioEmu requires internet access on compute nodes for ColabFold MSA server queries
  on first run. Subsequent runs use cached embeddings (`BIOEMU_EMBEDS_CACHE`).
- The BPTI sequence is 57 residues (not 58). PDB 6PTI numbering starts at 1
  but the extracted chain A sequence has 57 amino acids.
- HEWL generation took ~2x longer than BPTI (569s vs 266s), roughly proportional
  to sequence length ratio (129/57 = 2.26).
