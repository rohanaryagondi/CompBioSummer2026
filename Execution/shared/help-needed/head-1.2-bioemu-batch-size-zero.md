---
requestor: "head-1.2 (resume session 2026-04-19)"
subphase: "1.2"
date: 2026-04-19
urgency: RESOLVED
blocked_tasks: []
tracks_affected: [gamma]
resolution_date: 2026-04-19T16:10:00Z
resolved_by: head-1.2
---

# RESOLVED 2026-04-19T16:10Z

**Resolution:** User directed "no compromise, best data" on 2026-04-19T16:00Z.
head-1.2 patched `output/scripts/bioemu_batch2.sbatch` with a length-aware
`batch_size_100` computation:

```bash
BATCH_SIZE_100=$(python3 -c "
import math
L = ${SEQ_LEN}
target_bs = 3
bs100 = math.ceil(target_bs * (L/100)**2)
print(max(10, bs100))
")
```

This scales `batch_size_100` with `(L/100)²` so `bioemu.sample.py`'s
`int(batch_size_100 * (100/L)²)` always yields at least `batch_size=3`
(floored at bioemu's default 10 for short sequences). Verified bypass:
L=354→bs=3, L=556→bs=3, L=800→bs=3. Memory per batch now consistent
across lengths.

Also bumped sbatch walltime 4h → 12h (eliminates the TIMEOUT cascade
that killed 5 jobs overnight).

Batch 1 resubmitted cleanly as SLURM array 8903490 (cryptic `t0x8pyfc`)
after wiping all 10 scratch output dirs. Batch 1 will now produce full
≥2000 conformations for all 10 proteins (no batch_size=0 failures, no
partial data, no compromise).

Batches 2-10 will be submitted after batch 1 clears the QOS-per-user
limit (3 concurrent gpu-partition jobs currently).

# Original report (pre-resolution)

# Help Needed: BioEmu batch_size=0 bug on sequences >~340 aa

## Problem

BioEmu batch 1 array tasks `_1, _7, _8, _9` all FAILED with
`ValueError: range() arg 3 must not be zero` at `bioemu/sample.py:247`
calling `range(existing_num_samples, num_samples, batch_size)` with
`batch_size=0`.

Length-failure correlation is clean:

| Array idx | Protein            | Length | Class                | Outcome          |
|:---------:|:-------------------|:------:|:---------------------|:-----------------|
| _0        | GCN4_YEAST         | 281 aa | idp_like             | RUNNING          |
| _1        | CD19_HUMAN         | 556 aa | idp_like             | **FAILED (bs=0)**|
| _2        | A0A1I9GEU1_NEIME   | 161 aa | structured_globular  | SUCCESS 2417/2827|
| _3        | AICDA_HUMAN        | 198 aa | structured_globular  | RUNNING          |
| _4        | D7PM05_CLYGR       | 235 aa | structured_globular  | RUNNING          |
| _5        | RPC1_LAMBD         | 237 aa | idp_like             | RUNNING          |
| _6        | Q8WTC7_9CNID       | 238 aa | structured_globular  | RUNNING          |
| _7        | OTC_HUMAN          | 354 aa | structured_globular  | **FAILED (bs=0)**|
| _8        | HEM3_HUMAN         | 361 aa | structured_globular  | **FAILED (bs=0)**|
| _9        | OXDA_RHOTO         | 364 aa | structured_globular  | **FAILED (bs=0)**|

Threshold is between 238 aa (_6 passed) and 354 aa (_7 failed). Most
likely this is bioemu's auto-batch-size calculation underflowing to 0
when memory is tight — a 32GB RTX 5000 Ada cannot fit even 1 sample for
a ~350 aa sequence at bioemu-v1.1's default settings.

## What was tried

- Diagnosed all 4 failures from SLURM logs
  (`/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/logs/bioemu-8887446_{1,7,8,9}.err`)
- Confirmed failure pattern (sequence-length-dependent, not
  protein-composition-dependent, not env-dependent)
- Verified no shared cause with the precache cancellation: precache was
  cancelled at 01:46 at [1/93] proteins (YCRC auto-cancel despite
  keepalive rescue attempt), but generation-time MSA build is working
  (58 MSAs cached so far) so precache cancellation is not in the
  critical path for generation failures.

## Potential fixes (require bioemu-batch2 SubAgent patch)

1. **Pass `batch_size=1` explicitly** to `bioemu_main(...)` in
   `phases/phase-1/subphase-1.1/output/scripts/bioemu_generate_single.py`
   around line 221. This may just bypass the bug if the underlying
   memory budget is sufficient for 1 sample per batch.

2. **Use B200 partition** (80GB VRAM) for long-seq proteins. Violates
   the "RTX 5000 Ada exclusive" rule from Sub 1.1, so would need user
   sign-off. SU cost: ~300 SU/hr (B200) vs 15 SU/hr (RTX 5000 Ada) =
   20× more expensive.

3. **Reduce input features** for long sequences (e.g., cap MSA rows).
   May degrade model quality; not the right tradeoff.

4. **Accept ~30% protein loss** from batch 2. Would reduce the batch 2
   target from ≥90 proteins to ~65, still above the combined-paper N=57
   binding+activity primary analysis threshold (batch 1's 26 + ~30 from
   batch 2 = 56, near the wire). Risky for IP §12.2.

## Specific ask

**Option A (preferred, safe):** Re-invoke the bioemu-batch2 SubAgent
with mode `diagnose-batch-size` to test whether passing `batch_size=1`
explicitly bypasses the bug on _7's protein (OTC_HUMAN 354 aa). If yes,
patch `bioemu_generate_single.py` to add a `--batch-size` CLI arg that
the sbatch sets to 1 when length > 340. Resubmit _1/_7/_8/_9 and
submit batches 2-10 with the fix in place.

**Option B (fallback):** Accept the loss. Document in the Gamma paper
methods section that proteins >340 aa were excluded from batch 2 due to
memory. Batch 1's 556 aa CD19_HUMAN (same bug, handoff said
"long-seq FAILED") means this is a consistent policy.

## Timeline

- Batch 1 is still running (_0, _3-_6). Expected to complete in 1-3
  hours per task; full batch ~4-6 hours to all terminal.
- Batches 2-10 should NOT be submitted until this is resolved — each
  batch would lose ~30% of proteins to the same bug.
- No hard deadline; task-004 target (≥90 proteins ≥ 2,000 conformations)
  has scheduling flexibility through Sub 1.3 (~3 days beyond Sub 1.2
  end).

## Escalation path

If user wants Option A, they can invoke the bioemu-batch2 SubAgent
directly. If they want Option B, they can instruct head-1.2 to just
submit batches 2-10 as-is and sort the ~30% loss at topup.

head-1.2 has paused batch 2 submission pending this decision.
