# Alpha-M: The MLFF Biomolecular Crash Test

## Target Venue: Nature Methods (Registered Report fallback) or Nature Computational Science (if combined with Gamma)

## One-Sentence Pitch

The first systematic benchmark of machine-learning force fields against experimental NMR protein observables, answering "do ML force fields produce physically realistic protein dynamics?"

---

## Problem

Machine-learning force fields (MLFFs) like MACE-OFF24, SO3LR, and AI2BMD are validated exclusively against DFT calculations -- predicted energies and forces vs quantum chemistry references. Nobody has tested whether these models produce MD trajectories that agree with *experimental* protein observables: NMR S2 order parameters, J-couplings, chemical shifts, and SAXS profiles. Classical force fields (AMBER, CHARMM) have been refined against NMR for 30 years; MLFFs have never been tested. This is the "reality gap" that UniFFBench (Mannan et al., arXiv 2025) exposed for materials MLFFs, where top DFT performers failed against experimental measurements. For biomolecular MLFFs, the situation is worse and the test has never been done.

---

## What We Do

Benchmark 10 ensemble generators -- spanning 4 paradigms (MLFF, ML-classical, generative, classical MD) -- against experimental NMR observables across 14 proteins.

### Ensemble Generators (10)

| # | Generator | Category | Software |
|---|-----------|----------|----------|
| 1 | MACE-OFF24 | MLFF | mace-torch + OpenMM-ML |
| 2 | SO3LR | MLFF | JAX-MD |
| 3 | Garnet | ML-classical (NMR-trained) | PyTorch + OpenMM |
| 4 | BioEmu | Generative (diffusion) | pip install bioemu |
| 5 | Boltz-2 | Generative (structure prediction) | PyTorch |
| 6 | AlphaFlow | Generative (flow matching) | PyTorch |
| 7 | AMBER ff14SB | Classical | OpenMM |
| 8 | AMBER ff19SB | Classical | OpenMM |
| 9 | a99SB-disp | Classical (IDP-specialized) | OpenMM + TIP4P-D |
| 10 | CHARMM36m | Classical | OpenMM/GROMACS |

### Benchmark Proteins (14)

Organized by MLFF feasibility:

**Tier A (<50 residues, MLFF-feasible):**
- WW domain (PIN1-WW, 34 res) -- published S2, not Garnet-contaminated
- Crambin (46 res) -- stability control only (no NMR S2 data)
- GB3 (56 res) -- gold-standard NMR dynamics, multi-field relaxation data

**Tier B (50-80 residues, partial MLFF feasibility):**
- GB1 (56 res), BPTI (58 res, 3 disulfide bonds), CI2 (64 res), CspA (70 res), alpha-3D (73 res), Calbindin D9k (75 res), Ubiquitin (76 res), HPr (85 res)

**Tier C (80-170 residues, classical + generative only):**
- Barnase (110 res), HEWL (129 res), T4 lysozyme (164 res)

### Experimental Observables

| Observable | Back-calculation | Reference Data |
|-----------|-----------------|---------------|
| S2 order parameters | Lipari-Szabo from trajectory autocorrelation (iRED) | NMR 15N relaxation (BMRB) |
| 3J(HN,Ha) couplings | Karplus equation | NMR scalar couplings |
| Chemical shifts | SPARTA+ | Experimental shifts (BMRB) |
| SAXS profiles | Pepsi-SAXS | Published SAXS curves |
| RMSF | Per-residue CA fluctuations | NMR B-factors, RDCs |

### Statistical Framework

- **Primary test:** Friedman test with Nemenyi post-hoc across generators
- **Per-protein metric:** S2 R^2 vs experimental NMR for each generator
- **Clustering:** Hierarchical bootstrap (resample proteins, then residues)
- **Convergence:** ICC(2,k) > 0.80 AND ICC(2,1) > 0.50
- **Trajectory truncation:** All methods truncated to shortest common length per protein (mandatory for fair comparison)
- **Pre-registration:** Full analysis plan on OSF before Phase 2 production

---

## Key Design Decisions (from ReviewCohort)

1. **AI2BMD dropped** (unanimous). Hybrid solvent model (classical AMOEBA water), 22 open GitHub issues, no H200 support, Docker-only. Zero scientific loss.

2. **Garnet treated as contamination case study**, not competitive method. 5 of 7 Garnet benchmark proteins are in its training/validation set. Only T4 lysozyme is genuinely out-of-distribution. Garnet also underperforms AMBER ff14SB on most proteins. Reported separately with three roles: (a) contamination analysis, (b) NMR-trained paradigm representative, (c) GB1-vs-GB3 family comparison.

3. **Incomplete crossed design.** MLFFs cannot simulate Tier C proteins (>80 residues). The MLFF benchmark uses 9 proteins x 10 generators (fully crossed). Tier C proteins use ~7 generators (classical + generative only).

4. **Adaptive trajectory-length protocol.** MLFF trajectory lengths are limited (MACE-OFF24: ~1.6-5 ns; SO3LR: ~3-10 ns). Report maximum stable length as a finding. Truncate all methods to shortest common length for fair comparison.

---

## Timeline

| Phase | Dates | Activities |
|-------|-------|-----------|
| Phase 0 | Apr 15-30 | BioEmu disulfide test (BPTI, HEWL); BMRB S2 verification; conda environments |
| Phase 1 (Pilot) | May 1 - Jun 30 | Install MLFFs, stability tests on 3-4 Tier A/B proteins, NPT testing, pilot S2 |
| Phase 2 (Production) | Jul 1 - Sep 15 | Full 14x10 production simulations; back-calculation; analysis |
| Phase 3 (Replicas) | Sep 1 - Oct 15 | 5 replicas on 6 priority proteins for ICC |
| Manuscript | Oct 15 - Nov 15 | Writing, figures, submission |

**GO/NO-GO (June 30):** At least 1 MLFF must produce stable >10 ns trajectory on >=3 Tier B proteins. If both MLFFs fail: proceed with classical + generative benchmark (reduced scope, still publishable at NatMeth).

---

## Compute Budget

| Phase | GPU-hours |
|-------|-----------|
| Phase 1 (pilot) | 2,000-3,000 |
| Phase 2 (production) | 24,100-33,800 |
| Phase 3 (replicas) | 87,792 |
| Contingency (20%) | 22,800 |
| **Total** | **~166,632** |

Storage: 5-8 TB trajectory data (HPC scratch).

---

## Risks and Mitigations

| Risk | Probability | Mitigation |
|------|------------|-----------|
| MLFF total failure (neither stable >5 ns) | 25% | Classical + generative benchmark (still NatMeth) |
| BioEmu disulfide failure (BPTI/HEWL) | 15% | Drop those 2 proteins; 12 remain |
| SO3LR JAX environment issues | 20% | 3-7 day setup window; dedicated env |
| All generators indistinguishable | 10% | "Consensus confirms" framing (lower impact) |
| Scoop (<10% probability) | <10% | Lowest scoop risk of all proposals |

---

## Kill Criteria

| ID | Criterion | Threshold | Date |
|----|-----------|-----------|------|
| AK1 | MLFF total failure | 0 MLFFs with >5 ns | June 30 |
| AK2 | S2 indistinguishable | R^2 spread <0.05 | Aug 15 |
| AK3 | BioEmu disulfide catastrophic | SS integrity <80% | June 15 |
| AK4 | Compute >3x budget | >330K GPU-hrs | July 31 |
| AK5 | Garnet total failure | All proteins crash | July 15 |

---

## What Makes This Novel

1. **First multi-MLFF benchmark against experimental protein observables.** No one has done this.
2. **Four paradigms compared head-to-head:** MLFF, ML-classical, generative, classical.
3. **NMR is the ground truth**, not DFT. This is how force fields should be validated.
4. **Open benchmark framework** for the community to test future MLFFs.
5. **Garnet contamination case study** -- first systematic analysis of training data leakage in FF benchmarks.

---

## References

Key papers: Kovacs et al. (JACS 2025) MACE-OFF24; Frank et al. (JACS 2026) SO3LR; Li et al. (Nature 2024) AI2BMD; Smith/Lai & Brooks (J. Phys. Chem. B 2024) S2 convergence; Robustelli et al. (PNAS 2018) a99SB-disp; Mannan et al. (arXiv 2025) UniFFBench; Aryal et al. (IJMS 2026) BioEmu assessment; Blanco-Gonzalez et al. (arXiv 2026) Garnet.
