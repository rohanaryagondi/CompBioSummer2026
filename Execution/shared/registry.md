---
last_updated: 2026-04-18
---

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

---

## Notes

- PlannerAI updates this registry whenever it creates new HeadAIs or SubAgents
- AdminAI verifies this registry matches actual files on disk
- Status values: `active` | `complete` | `failed` | `blocked`
- Phase 0 agents marked complete (subphase 0.1 finished 2026-04-16)
