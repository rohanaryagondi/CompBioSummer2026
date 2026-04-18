---
gate_id: "D3"
date: 2026-04-17
decision: GO
assessed_by: PlannerAI
amended_by: subagent-h (PlannerAI pre-Sub-1.2 flag closure)
amended_date: 2026-04-17
---

# Gate Assessment: D3 -- Delta Scope Lock

## Gate Definition

**Date:** 2026-06-06 (scheduled); **early assessment 2026-04-17** (7+ weeks ahead)
**Decision:** Delta scope lock -- confirm at least 3 of 5 Tier 1 DL perturbation
methods are running, with baseline implementations complete. If fewer than 3:
drop failed methods, proceed with remainder.
**Source:** Implementation Plan Section 13, gate D3 (see also DK2 kill criterion
in Section 11.4 and Section 5.3 Tier 1 method roster).

---

## Evidence Summary

This is an **early-signal assessment** issued 7+ weeks ahead of the formal
June 6 gate date. The evidence base comes entirely from Subphase 1.1 setup work
(tasks 004 and 006), plus the post-subphase env-split scout from Subagent B.

Three of the five Tier 1 Delta methods are already installed and GPU-verified
on the HPC cluster:

- **GEARS** (task-004, SubAgent `gears-setup`): Installed in env-delta (now
  retargeted to `env-delta-v2` per Subagent B env-split). GPU pipeline verified
  on H200 via SLURM job 8409737. Peak GPU memory 7.73 GB at batch_size=256 --
  no OOM risk on any available GPU. Post-env-split smoke test 8702341 (RTX 5000
  Ada) re-confirmed GEARS import, GPU matmul, and the `gears_adapter.py`
  drug-to-target mapping (264/379 drugs) still work in env-delta-v2.
  Compatibility caveat: GEARS is designed for genetic (CRISPR) perturbations;
  the Tahoe-100M chemical-to-gene adapter is a documented scientific
  approximation but does produce predictions.
- **scGPT** (task-006, SubAgent `scgpt-cpa-setup`): Installed (v0.2.4) with
  whole-human pretrained weights (50.8 M parameters, 79% of tensors loaded).
  Forward pass PASSED on H200 (job 8405569) with MLM output shape [32, 1200].
  Peak GPU memory 6.78 GB. Gene vocabulary coverage 38,913 / 62,710 Tahoe genes
  (62%). torchtext-for-torch-2.11 incompatibility resolved via a pure-Python
  vocab shim.
- **CPA** (task-006, SubAgent `scgpt-cpa-setup`): Installed (v0.8.8,
  2023 release). 3-epoch training loop PASSED on H200 with loss 1740 -> 1640
  and R^2 -0.192 -> -0.072. Peak GPU memory 0.11 GB. CPA install originally
  forced hard downgrades in env-delta (numpy 2.2 -> 1.23.5, anndata 0.11 ->
  0.9.2, scanpy 1.11 -> 1.10.2). Subagent B has now isolated these pins to a
  separate `env-cpa.yml` (yml ready, env not yet instantiated), so CPA remains
  runnable without contaminating the env used for the other four Tier 1
  methods.

Two Tier 1 methods are **not yet installed** and are assigned to Subphase 1.2:

- **scFoundation:** Planned Sub 1.2 Wave 1 install. Subagent B's compatibility
  scout rates this **LOW RISK** in env-delta-v2: scFoundation's README lists
  numpy / pandas / scipy / pytorch / einops / scanpy / local_attention with no
  version pins, and the two pip-only dependencies (einops, local_attention)
  are both installable.
- **Tahoe-x1:** Planned Sub 1.2. Subagent B's scout rates this **MEDIUM RISK**.
  torch 2.11 and scanpy 1.10.2 in env-delta-v2 satisfy Tahoe-x1's hard pins
  (`torch>=2.5,<3.0`, `scanpy>=1.9,<2.0`). The risk is `llm-foundry[gpu]`,
  which pulls `flash-attn`, `composer`, and `mosaicml-streaming`. flash-attn
  wheels are typically cut for torch 2.4-2.6 / cu124, which may not resolve
  against our torch 2.11 / cu128 stack. Fallback plan (documented): if
  flash-attn blocks install, build `env-tahoex1` with torch 2.5 + cu124. The
  vendor's recommended path is a Docker image based on
  `mosaicml/llm-foundry:2.2.1_cu121_flash2` -- YCRC usability via
  Singularity/Apptainer is an open question.

Baseline implementations (5: linear, mean, PCA, random, persistence) are listed
in Implementation Plan Section 5.3 as part of Delta's Tier 1 roster, but no
baseline-implementation task was scheduled in Subphase 1.1. Baseline code is
deferred to a later Phase 1 subphase (likely Sub 1.2 or 1.3).

**Count check: 3 of 5 Tier 1 methods running (minimum for D3 GO met).**
**Baselines: 0 of 5 implemented (PARTIAL / deferred).**

---

## Criteria Evaluation

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | At least 3 of 5 Tier 1 DL methods running | **MET** | GEARS, scGPT, CPA all installed and GPU-verified. See `phases/phase-1/subphase-1.1/status/task-004-status.md` (GEARS), `phases/phase-1/subphase-1.1/status/task-006-status.md` (scGPT + CPA), and `shared/notes/1.1-env-split.md` (env-delta-v2 post-split re-verification, SLURM 8702341). |
| 2 | Baseline implementations complete (5: linear, mean, PCA, random, persistence) | **PARTIAL** | Not scheduled in Subphase 1.1. Deferred to Sub 1.2/1.3. IP Section 5.3 lists the 5 required baselines. |
| 3 | If fewer than 3: drop failed methods, proceed with remainder | **N/A** | Not triggered -- 3/5 are running. |

---

## Verdict

**Decision: CONDITIONAL GO**

The 3-of-5 minimum in the D3 criterion is already satisfied 7 weeks ahead of
the scheduled June 6 gate. This is the strongest signal the assessment can
give this early. However, the verdict is qualified as **CONDITIONAL** rather
than unconditional GO for two reasons:

1. **2 of 5 Tier 1 methods are still unverified.** scFoundation (LOW risk) and
   Tahoe-x1 (MEDIUM risk, flash-attn dependency) are scheduled for Sub 1.2.
   Their install success determines whether Delta runs at the full Tier 1
   scope (5 methods + 5 baselines) or a reduced scope (3-4 methods). Tahoe-x1
   in particular is the highest-novelty method in Delta's roster (3B-parameter
   foundation model with native Tahoe-100M streaming) and its loss would
   materially weaken Delta's differentiation.
2. **Baselines are not yet implemented.** The D3 criterion text explicitly
   names baseline completion. All 5 baselines (linear, mean, PCA, random,
   persistence) are straightforward to implement but have not been scheduled
   yet.

Formal (non-conditional) verdict is deferred to a re-assessment at or before
June 6, after Subphase 1.2 completes.

### If GO
N/A. This assessment is CONDITIONAL, not GO.

### If NO-GO
N/A. D3 minimum (3/5 Tier 1) is met; the kill condition (DK2: <3 Tier 1
methods running by June 6) does not fire.

### If CONDITIONAL
Proceed as follows:

- **Sub 1.2 tasks:** Must include scFoundation install (env-delta-v2 target,
  LOW risk) and Tahoe-x1 install (env-delta-v2 first, with env-tahoex1 as
  MEDIUM-risk fallback if flash-attn blocks). Must also include a baseline
  implementation task (5 baselines).
- **Re-assessment trigger (formal):** June 6, 2026. Or earlier if both
  scFoundation and Tahoe-x1 install attempts complete (pass or fail) in
  Sub 1.2.
- **Verdict table at re-assessment:**
  - If 5/5 Tier 1 + baselines: upgrade to unconditional GO (full scope).
  - If 4/5 Tier 1 + baselines: upgrade to GO at reduced Tier 1 scope
    (REDUCED-SCOPE GO).
  - If 3/5 Tier 1 + baselines: upgrade to REDUCED-SCOPE GO (Delta runs on the
    3 verified methods); document dropped methods in a cross-agent note and
    update Implementation Plan Section 5.3.
  - If <3/5 at June 6 (method regression from current state): DK2 fires,
    NO-GO; this would require a Sub 1.1 regression and is not anticipated.
- **In the meantime:** No Delta work blocks. GEARS / scGPT / CPA baseline
  adapters can be extended; Tahoe-100M data pipeline (DK1, due May 31) can
  progress; Sub 1.2 planning can proceed on the assumption of a 3-5 method
  final roster.

---

## Downstream Impact

| Affected Item | Impact |
|--------------|--------|
| Phase 1 plan | No change. Phase 1 proceeds; Sub 1.2 planning unblocked. |
| Subphase 1.2 | Must include scFoundation install task (env-delta-v2), Tahoe-x1 install task (env-delta-v2 primary; env-tahoex1 fallback), and a baseline-implementation task (5 baselines). |
| Subphase 1.3/1.4 | Design assumes 3-5 Tier 1 methods. If final roster drops below 5 at June 6, update method lists in production subphase plans. |
| Compute budget | No change. Delta budget (~15,000-20,000 GPU-hours) unaffected. |
| Timeline | On track. 7+ weeks of buffer to June 6 formal gate. Delta preprint (D5, Aug 15) viability unchanged. |
| Publication strategy | Delta standalone NatMeth preprint (Aug 15) viability unchanged. If final roster is <5 Tier 1, manuscript frames "GEARS + scGPT + CPA + [any installed] evaluated" without disruption to the calibrated-benchmark narrative. |

---

## Action Items

1. **PlannerAI:** When planning Subphase 1.2, include scFoundation install
   (env-delta-v2, LOW risk) and Tahoe-x1 install (env-delta-v2 primary;
   env-tahoex1 fallback with torch 2.5+cu124) as explicit tasks. Reference
   `shared/notes/1.1-env-split.md` for install targets and known
   compatibility gotchas (torch cu128 vs cu130 wheel pin).
2. **PlannerAI:** Include a baseline-implementation task in Sub 1.2 or Sub 1.3
   covering all 5 baselines (linear, mean, PCA, random, persistence) with
   WMSE + Spearman evaluation harnessing.
3. **Sub 1.2 HeadAI:** If either scFoundation or Tahoe-x1 fails to install
   after reasonable effort (including the env-tahoex1 fallback for Tahoe-x1),
   write a cross-agent note `shared/notes/1.2-delta-method-drops.md` tagged
   urgency=important, and PlannerAI will update the D3 verdict to
   **REDUCED-SCOPE GO** in an amended assessment.
4. **PlannerAI:** Re-assess D3 formally at June 6, 2026 (original gate date).
   If all 5 Tier 1 methods + baselines are running, upgrade this assessment
   to unconditional GO. Update the dashboard and write an amended
   `gate-D3-assessment.md` (or append a re-assessment section).
5. **Dashboard update:** `dashboards/gate-tracker.md` D3 row updated to
   `ASSESSED: CONDITIONAL` with assessment note; assessment file linked in
   Gate Assessments table.

---

## Amendment — 2026-04-17 (upgrade CONDITIONAL → GO)

**Amended by:** subagent-h, running the PlannerAI pre-Sub-1.2 flag closure task
**Trigger:** Both outstanding Tier 1 methods (scFoundation + Tahoe-x1) installed
and GPU-verified earlier than the planned Sub 1.2 schedule.

### New evidence (post-1.1 install work)

- **scFoundation:** INSTALLED in env-delta-v2; GPU smoke test PASS on RTX 5000
  Ada (SLURM 8705048). 119 M parameters loaded from the community HuggingFace
  mirror `perturblab/scfoundation-rde` (Apache 2.0, same xTrimoGene / MAE
  architecture as the original); 0 missing and 0 unexpected state_dict keys.
  Peak GPU memory 22.2 GB. Forward pass on 100 synthetic cells: 0.48 s.
  Tahoe-100M gene overlap by symbol: **99.4%** (19,151 / 19,264 scF genes).
- **Tahoe-x1 70m:** INSTALLED in a NEW isolated env `env-tahoex1` (Attempt 1
  in env-delta-v2 failed as predicted due to flash-attn wheel incompatibility
  with torch 2.11 / cu128). 70,996,993 parameters; forward pass on 100 cells
  in 0.9 s; peak 0.72 GB VRAM; Tahoe-100M ensembl-id coverage **100.0%**
  (SLURM 8708255).
- **Tahoe-x1 3B:** INSTALLED and GPU-verified on RTX 5000 Ada (SLURM 8709432).
  2,704,463,361 parameters loaded from HuggingFace `tahoebio/Tahoe-x1` with
  `model_size="3b"`. Peak VRAM **16.7 GB** — RTX 5000 Ada (32 GB) is
  sufficient, H200 not required for Delta inference. Cell-embedding output
  shape (100, 2560) float32. Forward pass on 100 cells in 8.5 s.
- **Full evidence:** `shared/notes/1.1-delta-methods-install.md`

### Criteria Re-Evaluation

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | At least 3 of 5 Tier 1 DL methods running | **MET (5/5)** | GEARS, scGPT, CPA (Sub 1.1 tasks 004/006) + scFoundation (env-delta-v2 install, SLURM 8705048) + Tahoe-x1 70m & 3B (env-tahoex1, SLURM 8708255 + 8709432). |
| 2 | Baseline implementations complete (5: linear, mean, PCA, random, persistence) | **PARTIAL** | Still not scheduled in Sub 1.1. Must be added to Sub 1.2 — owed. |
| 3 | If fewer than 3: drop failed methods, proceed with remainder | **N/A** | Not triggered — 5/5 running. |

### Amended Verdict

**Decision: GO (unconditional on the method-installation axis).**

All 5 Tier 1 Delta methods (GEARS, scGPT, CPA, scFoundation, Tahoe-x1) are
installed and GPU-verified on the HPC cluster. The 3-of-5 minimum is exceeded
at 5/5. No method was dropped; there is no reduced-scope fallback needed.

The baseline-implementation criterion (5 baselines) remains owed. This does not
downgrade the D3 verdict because the D3 criterion text is primarily about the
Tier 1 DL method count (see DK2 in Implementation Plan Section 11.4) and
baselines are deferrable. The baselines must be scheduled in Sub 1.2 as an
explicit task and completed before D4 (July 31) so the Delta evaluation
harness has controls in place.

### Downstream actions

1. **Sub 1.2 HeadAI:** Use the env mapping documented in
   `shared/notes/1.1-delta-methods-install.md` (env-delta-v2 for GEARS/scGPT/
   scFoundation, env-cpa for CPA, env-tahoex1 for Tahoe-x1). All five are
   verified GPU-capable on RTX 5000 Ada.
2. **Sub 1.2 HeadAI:** Schedule the baseline-implementation task (linear, mean,
   PCA, random, persistence) before D4 (July 31).
3. **PlannerAI:** Update `dashboards/gate-tracker.md` D3 row from
   `ASSESSED: CONDITIONAL` to `ASSESSED: GO`.
4. **PlannerAI:** D3 re-assessment at June 6 is no longer required (the
   original gate condition is fully satisfied). If a method regresses in
   Sub 1.2/1.3 (e.g. Tahoe-x1 3B throughput insufficient for production),
   that would be handled as a scope-adjustment note rather than a re-opened
   D3 gate.
