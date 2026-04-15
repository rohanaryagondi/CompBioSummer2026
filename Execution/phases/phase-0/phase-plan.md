---
phase: 0
title: "Pre-Project Setup"
date_range: "2026-04-15 to 2026-04-30"
tracks: [alpha-m, delta, infrastructure]
status: planned
created: 2026-04-15
---

# Phase 0: Pre-Project Setup

## Executive Summary

Phase 0 establishes the computational foundation for all three project tracks before
any experiments begin. It creates and version-pins all 9 conda environments, downloads
the 429 GB Tahoe-100M dataset for Delta, verifies BMRB NMR reference data and prepares
PDB input structures for the 14 Alpha-M benchmark proteins, and runs the BioEmu
disulfide bond integrity test on BPTI and HEWL. Failures detected here -- particularly
environment build failures for MACE-OFF24 or SO3LR -- provide maximum lead time before
the first decision gate (D1: May 9). Phase 0 is complete when all environments are
exported as pinned YAMLs, the Tahoe-100M streaming loader is verified, BMRB coverage
is confirmed for ≥12 proteins, and the BioEmu disulfide integrity metric is computed.

---

## Subphase Breakdown

| Subphase | Title | Date Range | Tracks | Tasks | Key Deliverable |
|----------|-------|------------|--------|-------|-----------------|
| 0.1 | Environment Setup & Data Verification | Apr 15 – Apr 30 | Alpha-M, Delta, Infrastructure | 4 | 9 pinned env YAMLs, Tahoe-100M loader, BMRB table, SS integrity report |

---

## Resource Allocation

### Compute

| Track | GPU-Hours (this phase) | GPU Type | Notes |
|-------|----------------------|----------|-------|
| Alpha-M | <2 | Any | BioEmu disulfide test only (~30-60 min per protein) |
| Delta | 0 | -- | Download is CPU + network only |
| Infrastructure | <0.1 | Any | SLURM access test job only |

### Storage

| Data | Size | Location |
|------|------|----------|
| Tahoe-100M raw | ~630 GB | HPC scratch |
| 14 PDB structure files | <100 MB | Repository |
| 9 conda environment YAMLs | <1 MB | Repository |
| BioEmu test conformations (BPTI + HEWL) | <500 MB | HPC scratch |

---

## Decision Gates in This Phase

| Gate | Date | Decision | Criteria | If NO-GO |
|------|------|----------|----------|----------|
| (none) | -- | No gates fall within Phase 0 | -- | -- |

Phase 0 produces early-warning evidence for D1 (May 9): env-mace and env-so3lr build
results are documented as cross-agent notes regardless of success or failure.

---

## Dependencies

### From Prior Phases
- None (this is the first phase)

### For Future Phases
- Phase 1 requires all 9 conda environments (from task-001)
- Phase 1 Delta track requires Tahoe-100M data loader (from task-002)
- Phase 1 Alpha-M track requires BMRB table, PDB structures, and manifest (from task-003)
- Phase 1 Alpha-M track requires BioEmu SS integrity results to confirm BPTI/HEWL inclusion (from task-004)
- Phase 1 planning requires cross-agent notes on env-mace/env-so3lr build results (D1 gate inputs)

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Tahoe-100M download >5 days | 30% | Delays Phase 1 Delta start | Resume support, parallel streams; DK1 deadline May 31 gives 45-day buffer |
| SO3LR JAX environment fails | 20% | Early D1 gate warning | Cross-agent note; does not block Phase 0; D1 is May 9 |
| BMRB S2 data missing for 3+ proteins | 15% | T5 threshold risk (≥12 needed) | Search alternate databases; document gaps thoroughly |
| BioEmu SS integrity <95% | 15% | T3 threshold risk (combined paper) | If <80%: AK3 fires, drop BPTI/HEWL; If 80-95%: flag for D6 planning |
| MACE-OFF24 environment fails | 15% | Early D1 gate warning | Cross-agent note; does not block Phase 0 |
| HPC scratch quota insufficient | 10% | Blocks data-intensive work | env-builder verifies quota as pre-step |

---

## Success Criteria

This phase is complete when ALL of the following are true:

1. All 9 conda environments created, smoke-tested, and exported as pinned YAML files
2. Tahoe-100M dataset fully downloaded and streaming loader verified with test query
3. BMRB S2 verification table complete for all 14 proteins with accession IDs
4. PDB structures downloaded and manifest file created for all 14 proteins
5. BioEmu disulfide integrity metric computed for BPTI and HEWL with clear threshold assessment
6. Cross-agent notes written for env-mace and env-so3lr build results (D1 early warning)
7. All subphase completion reports written
8. All relevant gates assessed (none in Phase 0, but early-warning notes produced)
9. Dashboards updated
