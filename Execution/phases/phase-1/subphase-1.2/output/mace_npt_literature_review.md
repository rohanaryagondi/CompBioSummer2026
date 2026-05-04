---
agent: mace-npt-litreview
task: task-010
date: 2026-05-01
---
# MACE + NPT: Literature & Community Survey

## Executive summary

Yes — published MACE NPT simulations exist, but **none match our configuration**. Every confirmed-stable MACE NPT run in the literature uses one of two recipes:

1. **ASE** (`ase.md.npt.NPT`) with **continuous Nose-Hoover + Parrinello-Rahman** coupling, MACE running on the entire system (no hybrid ML/MM).
2. **OpenMM MonteCarloBarostat with full classical bonded topology** for the system (e.g., MACE on a small molecule embedded in a fully-bonded classical solvent, where the *protein* is classical).

Our setup — **MACE on protein atoms, classical AMBER14/TIP3P-FB on water, OpenMM `MonteCarloBarostat`** via openmm-ml `createMixedSystem` — has **zero published precedent** that I can verify. The crash is not surprising: source-code analysis (§3) reveals that `createMixedSystem` strips all HarmonicBond / HarmonicAngle / HarmonicTorsion terms for ML-subset atoms, and OpenMM's `findMolecules()` does NOT infer connectivity from `PythonForce` / `TorchForce`. Consequence: the MC barostat sees each protein atom as its own molecule, and at every accepted volume move it scales every protein atom independently around the box origin — gradually destroying bonded distances.

The most defensible production path remains **classical-NPT pre-equilibration → MACE-NVT production** (Galvelis et al. 2023 NNP/MM precedent). The most promising NPT recovery experiment is a **sentinel `CustomBondForce` between protein backbone atoms with k=0** (zero-energy, zero-force) added explicitly so that `findMolecules()` glues the protein into one molecule, restoring rigid-body centroid scaling under the MC barostat. Estimated effort: ~2 hours of code, one 60-SU diagnostic on RTX 5000 Ada.

---

## §1 Confirmed working MACE + NPT setups

| Citation | Engine | Barostat | Thermostat | dt | Precision | System | Length | Stable? | Replicable? |
|---|---|---|---|---|---|---|---|---|---|
| Kovacs et al. 2024 JACS [^MACE-OFF] | ASE | Parrinello-Rahman (bulk water density vs. T) | Nose-Hoover | 1 fs | FP64 forces, FP32 integration | bulk water | not stated; for density-T curve | yes (water density within 2% of expt) | yes (well-documented) |
| Kovacs et al. 2024 JACS, §3.4.2 [^MACE-OFF] | ASE | Parrinello-Rahman | Nose-Hoover | 1 fs (inferred) | FP64 forces | Ala3 in water | **20 ns NPT** | yes (J-couplings match expt) | partial (SI not fetched) |
| Kovacs et al. 2024 JACS, §3.4.4 [^MACE-OFF] | OpenMM | not explicit; system size 18k atoms; Crambin 1.6 ns is described as production but ensemble not stated for that specific run | Langevin | not stated | FP32 integration | Crambin solvated 18k atoms | 1.6 ns | yes (RMSF<1A, no bond breaking) | partial — methods deferred to SI |
| Batatia et al. 2025 (low-precision) [^low-prec] | ASE | Parrinello-Rahman, isotropic, bulk modulus 2.2 GPa, pfactor=(100 fs)^2 * 2.2e9 Pa | Nose-Hoover, ttime=100 fs | 1 fs | FP32 inference (validated) | bulk water + organic liquids | not stated for full duration | yes ("within run-to-run variability") | yes |
| MACE basic-stability paper, arXiv:2503.11537 [^stab-test] | OpenMM | **MonteCarloBarostat** at 300 K, 1 bar | Nose-Hoover (Langevin in some) | **0.5 fs** | FP32 | small drug-like organic molecules in water (no protein) | 0.125 ns production | M and L stable; **S crashed at 44 ps** | yes |
| Sennane et al. (FeNNol/Tinker-HP, 2025) [^fennix-mts] | Tinker-HP | NVT only | Langevin | 1.5 fs inner / 3 fs outer (MTS factor 2) | not stated | lysozyme-phenol | 20 ns | yes | partial |
| `mace-md` (jharrymoore) [^mace-md] | OpenMM | `MonteCarloBarostat(pressure, temperature)` (default freq=25, no scaleMoleculesAsRigid override) | Langevin/Nose-Hoover/RPMD | 1 fs default | configurable | tested on small-molecule + ligand alchemical free-energy systems (replica-exchange hydration FE) | nanosecond-scale | yes for the alchemical/small-mol use case the package targets; **no published large-protein-NPT validation** | code is open |

**Bottom line for §1:** The only confirmed-stable OpenMM `MonteCarloBarostat` + MACE production is on small-molecule systems (mace-md replica-exchange hydration FE) and on tiny drug-like molecules (Bradley et al. arXiv:2503.11537, with 0.5 fs and dt halved). **Nobody has published OpenMM `MonteCarloBarostat` + MACE on a solvated protein > ~50 atoms of ML region.**

---

## §2 Failed / workaround MACE + NPT attempts

| Failure | Workaround / fix | Source |
|---|---|---|
| MACE-OFF23(S) crashes at 44 ps under MC barostat with dt=0.5 fs (300K, 1 bar, FP32) | Use M or L size; size S explicitly not recommended | arXiv:2503.11537 [^stab-test] |
| MACE downcasts FP64→FP32 produce immediate NaN in LAMMPS thermo | Train and run in same precision | ACEsuit/mace#990 [^mace-990] |
| openmm-ml issue #52: createMixedSystem on whole waterbox produces "box blowing up" because PBC is not properly transmitted to ML atoms | User worked around via custom `CustomNonbondedForce`; **issue still OPEN as of 2026-04** | openmm/openmm-ml#52 [^issue-52] |
| openmm-torch #34: protein unfolding in ANI-2x + AMBER14 hybrid (NVT) | Closed `wontfix`; recommended workaround was switching to PythonForce or alternative wrapping | openmm/openmm-torch#34 [^torch-34] |
| Eastman / OpenMM 8 paper deliberately uses NVT only for ALL ML examples | NPT explicitly listed as future work; no recipe given | Eastman et al. JPC-B 2024 [^openmm8] |
| Galvelis et al. 2023 NNP/MM uses NVT for all production runs (T=310 K, 4 fs MM / 2 fs NNP/MM) | Authors do not justify; the implicit message is "NPT not yet validated for hybrid" | PMC10577237 [^nnpmm] |

The pattern: every group that has tried hybrid ML/MM in OpenMM has chosen NVT for production. The published exceptions all run **pure-ML** systems (full system handled by MACE) and use ASE + Parrinello-Rahman.

---

## §3 openmm-ml specific issues

### Issue #52 — `createMixedSystem` PBC + box-blowup [^issue-52]

- Opened 2023-03-21 by `JohannesKarwou`. **Still OPEN as of 2026-04 (verified)**.
- Reports box "blowing up" under barostat when the entire waterbox is described by ML.
- User's workaround: replace the default `CustomNonbondedForce` inside `CustomCVForce` with a hand-built reaction-field expression. Validates against pure-MM and pure-ML systems.
- No maintainer fix in the 3 years since. No linked PRs that close it. The `mlpotential.py` source has not been substantially modified to address PBC re-replication for the ML atoms.

### Issue #91 — `MonteCarloBarostat` with periodic ML potentials [^issue-91]

- Opened 2025-02-04 by `jchodera` (a chodera-lab maintainer of openmmtools and a long-time OpenMM contributor).
- Status: **OPEN, no comments, no PR**.
- Quote (paraphrased from the visible discussion): when only a periodic ML potential is defined (no classical bonds), `findMolecules()` puts every atom into a separate molecule, and the `MonteCarloBarostat` therefore acts as an **atomic-scaling** barostat rather than a molecular-scaling one. jchodera notes this is the "desired" behavior for water (which can have proton exchange under reactive ML), but the issue is asking only for documentation, NOT a fix.
- **This is precisely our situation.** Our protein has all bonded terms removed by `_removeBonds(system, atoms, allInSet=True, removeConstraints=True)` (verified in `mlpotential.py` source [^mlpot-source]). PythonForce does NOT implement `getBondedParticles()`. Therefore each protein atom appears as a separate molecule to `findMolecules()`, and every MC volume move scales every protein atom independently around the box origin.

### Other open issues (none directly related to NPT)

- #119 (Feb 2026) CUDA install issue; #137 (Apr 2026) AceFF energy mismatch; #142/143 (Apr 2026) MACE-LES checkpoint and PolarMACE input-dict regressions; #94 (Apr 2025) ANI minimization slow; #95 (Apr 2025) NequIP modernization. **None of these touch barostat behavior.**

### Recent merged PRs of relevance

- #120 (Feb 2026) NequIP→PythonForce conversion. PR #117 (Mar 2026) TorchMDNet→PythonForce. PR #113 (Feb 2026) AIMNet2→PythonForce. PR #132 (Mar 2026) Orb support. PR #144 (Apr 2026) DeepmdPotential pass-args. **None modify MACE NPT path or barostat behavior.**
- Release 1.6 (Mar 2025) adds "periodic boundary conditions for AIMNet2 and TorchMD-Net" but does NOT mention MACE PBC fixes or MonteCarloBarostat fixes [^release-1.6].

### Maintainer status assessment

The OpenMM-ML maintainers are aware of the molecule-definition problem (issue #91) but have not prioritized either documenting or fixing it. The team's current effort is on broadening the model zoo (Orb, FeNNol, DeepMD, etc.) and converting older models to PythonForce. Barostat correctness for hybrid systems appears to be a known but un-addressed gap.

---

## §4 Continuous-barostat options inside OpenMM

OpenMM ships:
- `MonteCarloBarostat` (isotropic MC, default), `MonteCarloAnisotropicBarostat`, `MonteCarloMembraneBarostat`, `MonteCarloFlexibleBarostat`. **All use discrete MC volume moves**, identical mechanism, just different geometry.
- **No native continuous (Nose-Hoover or Parrinello-Rahman) barostat.**

`MonteCarloFlexibleBarostat` does have a `setScaleMoleculesAsRigid(false)` option that makes scaling atom-by-atom even when molecules ARE defined — but the default and the standard `MonteCarloBarostat` already act atom-by-atom for our hybrid system because `findMolecules` returns ~534 single-atom "molecules" for the protein.

### Community alternatives

- **`openmmtools`** (chodera-lab): wraps `MonteCarloBarostat` only. The `ThermodynamicState` automatically inserts `MonteCarloBarostat` for NPT. **No continuous barostat plugin found.** Its `LangevinIntegrator` BAOAB splitting is only a thermostat alternative, not a barostat.
- **OpenMM issue #4238** ("Implementing new barostats?") and **#635** ("New barostat features") request continuous barostats but no implementation has merged. Last activity 2024.
- **`tinker-OpenMM`** has a virial-based Berendsen barostat for AMOEBA on GPUs (Sennane et al. ResearchGate). License: open. Maturity: production for AMOEBA only; no MACE adapter exists.
- **`philipturner/openmm-metal`** is an Apple-Silicon plugin and unrelated.

**Verdict:** Adding a continuous barostat to OpenMM is a multi-week C++/CUDA engineering task. Out of scope for Sub 1.2/1.4. If we MUST run NPT, ASE is the clean path (§5).

---

## §5 ASE + MACE NPT for solvated systems

### Recipe (from MACE-OFF paper SI references and `ase.md.npt`)

```python
from ase.md.npt import NPT
from ase import units
from mace.calculators import MACECalculator

atoms.calc = MACECalculator(model_paths='mace-off24-medium.model',
                            device='cuda',
                            default_dtype='float64')   # FP64 to match validated paper protocol
dyn = NPT(atoms,
          timestep=1.0 * units.fs,
          temperature_K=300,
          ttime=100 * units.fs,                       # Nose-Hoover thermostat
          pfactor=(100 * units.fs)**2 * 2.2e9 * units.Pascal,  # Parrinello-Rahman; 2.2 GPa = water bulk modulus
          externalstress=1.01325e5 * units.Pascal)     # 1 atm
```

### Engineering cost vs. OpenMM

- ASE drives MACE on **the entire system** — including all 7K-17K water atoms. Per the MACE-OFF paper §3.4, throughput on Crambin (~18K atoms) is **3 × 10^5 steps/day on a single A100** = 0.3 ns/day at 1 fs. On a hybrid system with classical water, OpenMM was ~2.1 ns/day on H200 OpenCL (Sub 1.1 §11). **Pure ASE-MACE is ~7× slower than the hybrid OpenMM path** for this size.
- However, ASE-MACE on the hybrid system would not work either: ASE doesn't have a hybrid-ML/MM mode, and `MACECalculator` evaluates MACE on every atom passed to it.
- Compromise: **ASE for protein-only or peptide-only NPT** (Ala3, Ala15, small peptides). Production of solvated proteins via ASE NPT requires running MACE on water + protein, which is throughput-prohibitive for our 14-protein production at 10 ns each.

### Documentation status

- `MACECalculator` ASE docs at `mace-docs.readthedocs.io/en/latest/guide/ase.html`: **only NVT examples shown.** No NPT example in the public docs.
- `mace-tutorials` repo (`ACEsuit/mace-tutorials/mace-users/MACE_users.ipynb`): the file is large (1752 lines, 906 KB) but I could not extract its NPT content via WebFetch. It likely contains an NPT example based on 2023+ community references but I cannot verify directly.

**Verdict:** ASE NPT is the gold-standard validated recipe for MACE NPT. It is not feasible at our hybrid throughput requirement for production, but is a valid fallback for **a single small-protein or peptide demonstrator** in the paper.

---

## §6 JAX-MD + MACE bridge feasibility

- JAX-MD ships native NPT via Nose-Hoover Chains (NHC) on barostat AND thermostat, fully continuous. Better than ASE's PR for stochastic-dynamics correctness.
- **No published MACE-JAX bridge.** MACE is a PyTorch model; JAX-MD requires JAX. The cleanest path (theoretical) is to convert the MACE PyTorch model to ONNX → JAX via `jax2tf`/`onnx2jax`, but the e3nn equivariant ops are not trivially representable in JAX without a port.
- The SO3LR project (which we already use on RTX 5000 Ada) demonstrates that MACE-class equivariant models DO work in JAX-MD (SO3LR's underlying architecture is from the e3nn family). However, SO3LR was trained natively in JAX, not ported from a PyTorch MACE.
- Effort to port MACE-OFF24 weights to a JAX equivariant model: **multi-month**, requires ML engineering. Out of scope.

**Verdict:** JAX-MD + MACE is technically possible via SO3LR's architectural lineage, but **a working bridge does not exist and would take ~3 months to build**. Not actionable within Sub 1.2/1.4.

---

## §7 Multi-time-step (rRESPA) precedent

- arXiv:2510.06562 (Sennane et al. 2025) [^fennix-mts]: MTS factor 2-6× outer/inner steps for FeNNix-Bio1 on bulk water and lysozyme-phenol. Uses Tinker-HP, not OpenMM. **NVT only**, 1.5/3 fs inner/outer. 20 ns lysozyme-phenol stable.
- arXiv:2602.14975 (DMTS distillation): "speedups 3.66 to 5.64×" using a distilled small-NN as the inner force evaluator. No MACE. No NPT.
- **No published MACE + MTS + NPT in OpenMM.** OpenMM has `CustomIntegrator` capable of rRESPA (BAOAB-like splittings supported), but no community example wires MACE through rRESPA + MC barostat.

**Verdict:** MTS is a throughput optimization, not a stability fix. It does NOT address the molecule-definition root cause we identified in §3.

---

## §8 Recommended next experiments for head-1.2

Prioritized: most-likely-to-work first. Each experiment listed with the change, the expected gain, the risk, and effort estimate.

### Recommendation A: Sentinel `CustomBondForce(k=0)` to glue protein into one molecule

**Change:** Add ~533 zero-strength `CustomBondForce` bonds along the protein backbone (CA-CA-CA chain) to the openmm-ml-built hybrid system, AFTER `createMixedSystem` strips the AMBER bonds. Use `CustomBondForce("0.5*k*(r-r0)^2")` with `k=0` per bond. These contribute zero force, zero energy — pure topology.

**Why it should work:** `findMolecules()` traverses connectivity from any `Force` that implements `getBondedParticles()`. `CustomBondForce` does. The backbone-chain placeholder bonds will glue all 534 protein atoms into one molecule, so the `MonteCarloBarostat` will scale the protein centroid as a rigid body — restoring the standard NPT behavior that works for classical proteins.

**Expected effect:** NPT crash should disappear. Pressure tensor and density still come from the classical water (which is the bulk of the system anyway). Protein internal geometry is preserved by MACE forces, NOT by the placeholder bonds.

**Risk:** ~20% — there may be an additional issue we haven't identified. If it crashes anyway, the failure mode will tell us the next thing to test (likely PBC handling per issue #52, requiring a more invasive fix).

**Effort:** ~2 hours code (a function that walks the topology, finds the protein backbone CA atoms, and adds bonds via `CustomBondForce.addBond`). One 60-SU diagnostic on RTX 5000 Ada (50 ps) to test against the existing Test A/B/F crash points.

**Code sketch:**
```python
from openmm import CustomBondForce
sentinel = CustomBondForce("0.5*k*(r-r0)^2")
sentinel.addPerBondParameter("k")
sentinel.addPerBondParameter("r0")
ca_indices = [a.index for a in topology.atoms() if a.name == "CA" and a.index in protein_indices]
for i, j in zip(ca_indices[:-1], ca_indices[1:]):
    sentinel.addBond(i, j, [0.0, 0.38])  # k=0, r0=0.38 nm placeholder
sentinel.setUsesPeriodicBoundaryConditions(True)
system.addForce(sentinel)
```

### Recommendation B: Pre-equilibrate classical NPT, then MACE NVT (fallback / production path)

**Change:** Run AMBER14/TIP3P-FB classical NPT for 1 ns to equilibrate box dimensions (no MACE, no instability). Save the final box vectors and positions. Run MACE-hybrid NVT production from that state.

**Why:** No MACE NPT means no MC-vs-MACE interference. Density is set by the classical pre-equilibration. NVT production is already validated stable in Sub 1.1 (5 ns Crambin, 2.11 ns/day H200 OpenCL hybrid WW).

**Expected effect:** Production trajectories run reliably. S2 order parameters (the actual scientific output for D2 G1) are computed in NVT; this is precisely the protocol used by Galvelis et al. 2023 NNP/MM (NVT, 100 ns × 10 replicas, no barostat).

**Risk:** ~5%. The path is well-trodden. The only "risk" is reviewer pushback on NVT-vs-NPT, which is mitigated by citing Galvelis et al. and including a paragraph in OSF Methods explaining the choice.

**Effort:** Already designed in `output/npt_nvt_production_plan.md`. Implementation cost: rebuild equilibration step in classical-only mode.

### Recommendation C: Reduce barostat frequency dramatically (freq=500-1000)

**Change:** `MonteCarloBarostat(1*atm, 300*K, 1000)` instead of 25 or 100.

**Why:** With ~534 single-atom "molecules" being independently scaled per move, fewer moves = less accumulated damage. The system has more time to relax via MACE forces between volume moves. Pressure equilibration will be slow but the protein internal geometry will not be progressively destroyed.

**Expected effect:** Crash delayed substantially. May or may not survive 5 ns. Only useful if Recommendation A fails AND we still want NPT.

**Risk:** 50%. Untested in our exact configuration; based on inference from §3 root cause.

**Effort:** trivial (one parameter change). 30-50 SU diagnostic.

### Recommendation D: ASE NPT for a single small-protein "validation" run

**Change:** Use the `ase.md.npt.NPT` recipe in §5 on Crambin (the smallest validated MACE-OFF protein, 46 residues, 642 atoms) with explicit water at the same box. Record one validation trajectory of 1 ns, show that ASE NPT and OpenMM NVT give equivalent S2 order parameters.

**Why:** Demonstrates to reviewers that we are aware of the gold-standard recipe and our NVT-with-classical-pre-equilibration choice is not a corner-cutting compromise.

**Expected effect:** A clean methods-section paragraph for the combined paper.

**Risk:** ~20% (ASE-MACE on solvated protein has been demonstrated at 1.6 ns by Kovacs et al.; replication is reasonable but throughput is slow ~0.3 ns/day on A100, so 1 ns = ~3.3 days wall).

**Effort:** ~1 day setup (new ASE driver script), ~3-7 days wall on A100. Defer to Sub 1.4 if budget allows.

### NOT recommended (scoped against)

- **Switch to MonteCarloFlexibleBarostat with `scaleMoleculesAsRigid=False`**: this is what we already effectively have. Will not help.
- **Switch to MonteCarloAnisotropicBarostat**: same atom-scaling issue.
- **Build a continuous barostat as a CustomIntegrator**: multi-month, scope-incompatible.
- **Port MACE to JAX-MD**: multi-month, scope-incompatible.

---

## §9 References

All citations verified at the level indicated. Last verified 2026-05-01.

[^MACE-OFF]: Kovacs, D.P. et al. "MACE-OFF: Short-Range Transferable Machine Learning Force Fields for Organic Molecules." JACS 2024. DOI: [10.1021/jacs.4c07099](https://pubs.acs.org/doi/10.1021/jacs.4c07099). PMC: [PMC12123624](https://pmc.ncbi.nlm.nih.gov/articles/PMC12123624/). arXiv preprint: [arXiv:2312.15211v3](https://arxiv.org/html/2312.15211v3). **Verified abstract + main-text excerpts; SI methods (V.3) deferred — not fetched.** 20 ns NPT on Ala3 explicitly stated; Crambin 1.6 ns ensemble not explicitly NPT.

[^low-prec]: Batatia, I. et al. "Speeding Up MACE: Low-Precision Tricks for Equivariant Force Fields." [arXiv:2510.23621](https://arxiv.org/html/2510.23621v1) (2025). **Verified main text.** ASE NPT, Parrinello-Rahman, ttime=100 fs, pfactor=(100 fs)^2*2.2e9 Pa, FP32 stable.

[^stab-test]: "Basic stability tests of machine learning potentials for molecular simulations in computational drug discovery." [arXiv:2503.11537](https://arxiv.org/abs/2503.11537) (2025). **Verified abstract + key parameters from prior research-report extraction.** OpenMM MC barostat at 0.5 fs, MACE-OFF23(S) crashes at 44 ps; M and L stable.

[^openmm8]: Eastman, P. et al. "OpenMM 8: Molecular Dynamics Simulation with Machine Learning Potentials." J. Phys. Chem. B 2024. PMC: [PMC10846090](https://pmc.ncbi.nlm.nih.gov/articles/PMC10846090/). **Verified abstract + ML-examples list.** All ML examples NVT only; NPT explicitly not addressed.

[^nnpmm]: Galvelis, R. et al. "NNP/MM: Accelerating Molecular Dynamics Simulations with Machine Learning Potentials and Molecular Mechanics." JCIM 2023. PMC: [PMC10577237](https://pmc.ncbi.nlm.nih.gov/articles/PMC10577237/). **Verified methods (NVT 310 K, 4 fs MM / 2 fs NNP/MM, no barostat).** No NPT discussion.

[^mace-md]: jharrymoore/mace-md. [GitHub](https://github.com/jharrymoore/mace-md). **Verified file structure and CLI flag (`--pressure 1.0` for NPT). Source `mace_md/hybrid_md.py` instantiates `MonteCarloBarostat(self.pressure, self.temperature)` (default freq=25, no `scaleMoleculesAsRigid` override).** No solvated-protein NPT validation in tests.

[^fennix-mts]: "Accelerating Molecular Dynamics Simulations with Foundation Neural Network Models using Multiple Time-Step and Distillation." [arXiv:2510.06562v1](https://arxiv.org/html/2510.06562v1) (2025). **Verified abstract + methods.** Tinker-HP, NVT only, MTS factor 2-6×.

[^issue-52]: openmm/openmm-ml issue #52 "createMixedSystem() for switching a whole waterbox." [GitHub](https://github.com/openmm/openmm-ml/issues/52). **Verified open status as of 2026-04. Verified original report content.** No maintainer fix.

[^issue-91]: openmm/openmm-ml issue #91 "Document MonteCarloBarostat behavior with periodic ML potentials?" [GitHub](https://github.com/openmm/openmm-ml/issues/91). **Verified open status, no comments, opened 2025-02-04 by jchodera.** Confirms our root cause.

[^torch-34]: openmm/openmm-torch issue #34 (cited from prior research report). [GitHub](https://github.com/openmm/openmm-torch/issues/34). **Cited via prior research; not re-verified in this survey.**

[^mace-990]: ACEsuit/mace issue #990 (cited from prior research report). [GitHub](https://github.com/ACEsuit/mace/issues/990). **Cited via prior research; not re-verified.**

[^mlpot-source]: openmm-ml `mlpotential.py` source. [GitHub main branch](https://github.com/openmm/openmm-ml/blob/main/openmmml/mlpotential.py). **Verified `_removeBonds(system, atoms, allInSet=True, removeConstraints=True)` semantics: "Removing all bonds, angles, and torsions for which all atoms are in the ML subset" (XML-surgical removal, no replacement bonds added).**

[^mace-pot-source]: openmm-ml `models/macepotential.py` source. [GitHub main branch](https://github.com/openmm/openmm-ml/blob/main/openmmml/models/macepotential.py). **Verified `_computeMACE` rebuilds neighbor list every step using `get_neighborhood(positions, cutoff, [periodic, periodic, periodic], cell)` with cell fetched fresh from `state.getPeriodicBoxVectors()`. PythonForce wrapper used (PR #120 architecture). No `getBondedParticles()` implementation — therefore PythonForce contributes nothing to `findMolecules()` graph.**

[^mc-impl]: openmm/openmm `MonteCarloBarostatImpl.cpp` source. [GitHub main branch](https://github.com/openmm/openmm/blob/master/openmmapi/src/MonteCarloBarostatImpl.cpp). **Verified scaling kernel calls `scaleCoordinates(context, lengthScale, lengthScale, lengthScale)` which uses `context.getMolecules()`. The free-energy term in the MC acceptance criterion (`numMolecules*kT*log(V_new/V_old)`) treats each PythonForce-only atom as its own molecule.**

[^find-molecules]: openmm `ContextImpl.cpp::findMolecules`. [GitHub main branch](https://github.com/openmm/openmm/blob/master/openmmapi/src/ContextImpl.cpp). **Verified algorithm: iterates classical bonds + constraints + virtual sites only. PythonForce / TorchForce do not implement `getBondedParticles()` and therefore do not contribute connectivity. Result: ML-only atoms are returned as singletons.**

[^release-1.6]: openmm-ml release 1.6 notes (Mar 25, 2025). [GitHub Releases](https://github.com/openmm/openmm-ml/releases). **Verified.** Adds MACE-OMOL-0 + Orb + FeNNix; "PBC for AIMNet2 and TorchMD-Net"; no MACE PBC or barostat fixes.

[^mc-doc]: OpenMM User Guide §19, "Standard Forces — MonteCarloBarostat theory." [docs.openmm.org/latest/userguide/theory/02_standard_forces.html](https://docs.openmm.org/latest/userguide/theory/02_standard_forces.html). **Verified text:** "Each Monte Carlo step modifies particle positions by scaling the centroid of each molecule, then applying the resulting displacement to each particle in the molecule." Critical: no documented behavior for systems where atoms have no classical bonds.

[^flexbarostat-doc]: OpenMM `MonteCarloFlexibleBarostat` API reference. [docs.openmm.org](https://docs.openmm.org/latest/api-python/generated/openmm.openmm.MonteCarloFlexibleBarostat.html). **Verified.** `scaleMoleculesAsRigid` exists on the *Flexible* barostat only, NOT on `MonteCarloBarostat`. Default true. Setting false makes scaling atom-by-atom — but this is irrelevant for our case because the MC barostat already does atom-by-atom scaling for our protein due to the molecule-singleton problem.

[^opmm-py-force]: "OpenMM-Python-Force: Deploying Accelerated Python Modules in Molecular Dynamics Simulation." [arXiv:2412.18271](https://arxiv.org/abs/2412.18271) (2024). **Verified abstract only.** Confirms PythonForce is the new wrapper architecture; no NPT or barostat discussion in the abstract.
