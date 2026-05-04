---
last_updated: 2026-04-25
---

<!-- Updated 2026-04-18 (PlannerAI Sub 1.2 planning): added head-1.2 + 6 SubAgents -->
<!-- Updated 2026-04-19 (head-1.2 execution): Sub 1.2 agents launched; status updates; sub-1.2-so3lr-fix remediation added -->


# Agent Registry

## System Agents

| Agent | Type | Location | Status |
|-------|------|----------|--------|
| PlannerAI | Orchestrator | `Execution/CLAUDE.md` | Active |
| AdminAI | Auditor | `Execution/agents/admin/CLAUDE.md` | Active |

## HeadAIs

| Agent | Subphase | Tracks | Location | Status |
|-------|----------|--------|----------|--------|
| head-0.1 | 0.1 | Alpha-M, Delta, Infrastructure | `Execution/phases/phase-0/subphase-0.1/CLAUDE.md` | Complete |
| head-1.1 | 1.1 | Alpha-M, Gamma, Delta | `Execution/phases/phase-1/subphase-1.1/CLAUDE.md` | **Complete** (subphase CLOSED 2026-04-18) |
| head-1.2 | 1.2 | Alpha-M, Gamma, Delta, cross-cutting | `Execution/phases/phase-1/subphase-1.2/CLAUDE.md` | **Running** (launched 2026-04-19; Waves 1+2 agents returned; SLURM jobs multi-day) |

## SubAgents (formal HeadAI-launched, subphase tasks)

| Agent | Task ID | Subphase | Track | Location | Status |
|-------|---------|----------|-------|----------|--------|
| env-builder | task-001 | 0.1 | Infrastructure | `Execution/phases/phase-0/subphase-0.1/agents/env-builder/CLAUDE.md` | Complete |
| tahoe-loader | task-002 | 0.1 | Delta | `Execution/phases/phase-0/subphase-0.1/agents/tahoe-loader/CLAUDE.md` | Complete |
| alpha-scout | task-003 | 0.1 | Alpha-M | `Execution/phases/phase-0/subphase-0.1/agents/alpha-scout/CLAUDE.md` | Complete |
| bioemu-test | task-004 | 0.1 | Alpha-M | `Execution/phases/phase-0/subphase-0.1/agents/bioemu-test/CLAUDE.md` | Complete |
| mace-pilot | task-001 | 1.1 | Alpha-M | `Execution/phases/phase-1/subphase-1.1/agents/mace-pilot/CLAUDE.md` | Complete |
| so3lr-pilot | task-002 | 1.1 | Alpha-M | `Execution/phases/phase-1/subphase-1.1/agents/so3lr-pilot/CLAUDE.md` | Complete |
| bioemu-gen | task-003 | 1.1 | Gamma | `Execution/phases/phase-1/subphase-1.1/agents/bioemu-gen/CLAUDE.md` | Complete |
| gears-setup | task-004 | 1.1 | Delta | `Execution/phases/phase-1/subphase-1.1/agents/gears-setup/CLAUDE.md` | Complete |
| sc-recon | task-005 | 1.1 | Alpha-M | `Execution/phases/phase-1/subphase-1.1/agents/sc-recon/CLAUDE.md` | Complete |
| scgpt-cpa-setup | task-006 | 1.1 | Delta | `Execution/phases/phase-1/subphase-1.1/agents/scgpt-cpa-setup/CLAUDE.md` | Complete |
| mlff-mace-pilot | task-001 | 1.2 | Alpha-M | `Execution/phases/phase-1/subphase-1.2/agents/mlff-mace-pilot/CLAUDE.md` | Running (v5 FAILED: WW chk mismatch, GB3 _dof bug, UBQ NaN; v6 fixes applied — 50ps equil, chk mismatch handler, _dof init; diagnostic 9546808 + resubmit pending fair-share) |
| mlff-so3lr-pilot | task-002 | 1.2 | Alpha-M | `Execution/phases/phase-1/subphase-1.2/agents/mlff-so3lr-pilot/CLAUDE.md` | **Complete** (2/5 PASS: GB1+UBQ stable 5 ns; GB3 silent structural explosion Rg 10→990Å despite clean logs; NTL9 explosion@100ps+NaN@4.4ns; WW NaN@0.7ns. CRITICAL: SO3LR exit 0 + clean energy logs do NOT guarantee structural stability — HDF5 Rg check mandatory) |
| osf-prereg | task-003 | 1.2 | cross-cutting | `Execution/phases/phase-1/subphase-1.2/agents/osf-prereg/CLAUDE.md` | v2 drafted (power analysis populated from validated stats pipeline); user deposits by 2026-05-15 |
| bioemu-batch2 | task-004 | 1.2 | Gamma | `Execution/phases/phase-1/subphase-1.2/agents/bioemu-batch2/CLAUDE.md` | Running (10/93 success, 1 partial, 82 pending; resubmitted 9449458+9449459 on gpu; fair-share blocked) |
| delta-baselines | task-005 | 1.2 | Delta | `Execution/phases/phase-1/subphase-1.2/agents/delta-baselines/CLAUDE.md` | **Complete** (5 baselines + WMSE/FDR/calibration/stratified all implemented; random FAILS gate as required; D3 fully retired) |
| stats-pipeline | task-006 | 1.2 | cross-cutting | `Execution/phases/phase-1/subphase-1.2/agents/stats-pipeline/CLAUDE.md` | **Complete** (Friedman/Nemenyi, ICC, 2-level bootstrap, JZS BF matches R to 0.0001%, T_min; new env-stats created) |

## Ad-hoc research/remediation SubAgents (PlannerAI-launched post-subphase 1.1)

These were launched directly by PlannerAI during the 2026-04-17 → 2026-04-18
post-subphase remediation pass (no formal HeadAI / persona files — they were
one-off research or execution tasks driven by inline prompts). All complete.

| Label | Purpose | Primary Deliverable | Status |
|-------|---------|---------------------|--------|
| t5-margin-scout | Find additional benchmark proteins | `shared/notes/1.1-t5-margin-candidates.md` | Complete |
| protein-auditor | Audit 12-protein benchmark integrity | `shared/notes/1.1-protein-verification.md` | Complete |
| protein-addition-executor | Add 4 proteins + BioEmu validate | `shared/notes/1.1-benchmark-expansion.md` | Complete |
| documentation-fixer | Remediate 10 YELLOW audit items | `shared/notes/1.1-audit-remediation.md` | Complete |
| subagent-A | MACE CUDA + Phase 2 feasibility | `shared/notes/1.1-mace-phase2-feasibility.md` | Complete |
| subagent-B | env-delta audit + env-cpa/env-delta-v2 split | `shared/notes/1.1-env-split.md` | Complete |
| subagent-C | T4L lit + HPr impl + protein count reconciliation | `shared/notes/1.1-protein-count-canonical.md` | Complete |
| subagent-D | Methods-section text bundle (4 caveats) | `shared/notes/1.1-methods-section-drafts.md` | Complete |
| subagent-E | Competition scan infrastructure | `shared/competition-scans/` + `shared/notes/1.1-competition-scan-infra.md` | Complete |
| subagent-F | D3 gate assessment | `phases/phase-1/gate-D3-assessment.md` | Complete |
| subagent-G | MACE hybrid empirical + Crambin SS check | `shared/notes/1.1-mace-hybrid-validation.md` | Complete |
| subagent-H | scFoundation + Tahoe-x1 installs | `shared/notes/1.1-delta-methods-install.md` | Complete |
| subagent-I | T4L cavity mask + citation verification | `shared/notes/1.1-t4l-cavity-mask.md`, `1.1-citations-verified.md` | Complete |
| subagent-J | OpenMM CUDA rebuild from source | `shared/notes/1.1-openmm-cuda-rebuild.md` | Complete |
| subagent-K | Implicit-solvent MACE pilot | `shared/notes/1.1-mace-implicit-pilot.md` | Complete |
| subagent-L | CUDA interop fix + hybrid CUDA benchmark | `shared/notes/1.1-mace-cuda-benchmark.md` | Complete |
| sub-1.2-so3lr-fix | SO3LR sbatch PYTHONNOUSERSITE regression fix + resubmit (2026-04-19) | `shared/notes/1.2-env-so3lr-typing-extensions-fix.md` | Complete |

---

## Notes

- PlannerAI updates this registry whenever it creates new HeadAIs or SubAgents
- AdminAI verifies this registry matches actual files on disk
- Status values: `active` | `complete` | `failed` | `blocked`
- Phase 0 agents marked complete (subphase 0.1 finished 2026-04-16)
