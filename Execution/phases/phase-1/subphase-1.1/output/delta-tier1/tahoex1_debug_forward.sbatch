#!/bin/bash
#SBATCH --job-name=pQ3debug
#SBATCH --partition=gpu_devel
#SBATCH --gpus=rtx_5000_ada:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=00:15:00
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err

set -euo pipefail

module purge
module load miniconda/24.11.3
source activate env-tahoex1
export PYTHONNOUSERSITE=1
export HF_HOME=/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m/.hf_cache

cd /home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output/delta-tier1

python -u - <<'PY'
import torch, traceback, sys
from tahoe_x1.model import ComposerTX

model, vocab, model_cfg, collator_cfg = ComposerTX.from_hf(
    repo_id="tahoebio/Tahoe-x1", model_size="70m", use_chem_inf=False,
)
print("loaded")

# Build a tiny dummy batch by hand to mirror the DataLoader contract.
B, S = 2, 64
pad_id = collator_cfg["pad_token_id"]
genes = torch.randint(10, 100, (B, S), device="cuda")
genes[:, -5:] = pad_id
exprs = torch.randn(B, S, device="cuda").abs()
gen_masks = torch.zeros(B, S, dtype=torch.bool, device="cuda")
key_padding_mask = ~genes.eq(pad_id)

# Try ComposerTX first
print("\n--- ComposerTX.forward (batch dict) ---")
try:
    out = model({"gene": genes, "expr": exprs, "gen_mask": gen_masks},
                skip_decoders=True)
    print("  ComposerTX OK, keys:", list(out.keys()))
    if "cell_emb" in out:
        print("  cell_emb shape:", out["cell_emb"].shape)
except Exception as e:
    print(f"  FAIL {type(e).__name__}: {e}")
    traceback.print_exc()

# Try inner TXModel
print("\n--- model.model (TXModel) positional ---")
try:
    out = model.model(genes, exprs, gen_masks, key_padding_mask, skip_decoders=True)
    print("  TXModel OK, keys:", list(out.keys()))
except Exception as e:
    print(f"  FAIL {type(e).__name__}: {e}")
    traceback.print_exc()

# Try the exact kwargs pattern used by get_batch_embeddings
print("\n--- model.model kwargs (like emb_extractor) ---")
try:
    out = model.model(
        genes=genes, values=exprs, gen_masks=gen_masks,
        key_padding_mask=key_padding_mask, drug_ids=None, skip_decoders=True,
    )
    print("  OK, keys:", list(out.keys()))
except Exception as e:
    print(f"  FAIL {type(e).__name__}: {e}")
    traceback.print_exc()

PY
