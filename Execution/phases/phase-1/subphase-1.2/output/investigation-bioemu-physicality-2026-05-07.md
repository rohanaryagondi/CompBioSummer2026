---
agent: bioemu-physicality-investigator
type: investigation
urgency: important
date: 2026-05-07
subphase: "1.2"
affected_tracks: [gamma, combined]
---

# BioEmu Physicality Filter — Investigation of L→Pass-Rate Trend in Batch 2

**Trigger:** SHORT array 10730244 produced 2/9 task `partial` results today
(REV_HV1H2 L=116 80.5%; AACC1_PSEAI L=177 85.2%) while all 7 shorter proteins
passed cleanly. Apparent length-dependent regression. User directive: "uncompromised
data, not just clear the bar." MED (L=200-499) and LONG (L≥500) arrays still
pending — risk of falling below the 2,000-conformation criterion.

**Bottom line:** the apparent "length regression" is mostly noise on top of a
mild monotone trend that the existing oversampling already covers, **except for
one structurally pathological pending protein (P53_HUMAN, L=393, idp_like,
disorder_fraction 0.58)** that the upstream disorder-screen narrowly missed —
same failure mode as CD19_HUMAN. Recommend pre-emptive P53 exclusion + monitor
MED/LONG; **do not raise the global oversampling multiplier**, **do not loosen
the physicality filter**.

---

## 1. BioEmu physicality filter mechanism

**Source:** `~/.conda/envs/env-bioemu/lib/python3.10/site-packages/bioemu/convert_chemgraph.py`,
function `_filter_unphysical_traj_masks()` lines 331-379, called by
`filter_unphysical_traj()` (line 405) which is invoked from `save_pdb_and_xtc()`
(line 432) when the user passes `filter_samples=True` (the default in
`bioemu.sample.main`, line 85). Activated for batch 2 — the wrapper
`bioemu_generate_single.py` does not override it.

The filter applies **three independent boolean checks** to every denoised
backbone conformation. A frame is kept if and only if all three pass:

| Check | Threshold | Quantity | Source line |
|-------|-----------|----------|-------------|
| Cα-Cα sequential distance | < 4.5 Å for every (i, i+1) residue pair | mdtraj `compute_contacts(scheme="ca")` | convert_chemgraph.py:345, 350 |
| C-N peptide bond | < 2.0 Å for every (i, i+1) C→N atom pair | mdtraj `compute_distances` | convert_chemgraph.py:369, 372 |
| Inter-residue clash (residue offset > 2) | minimum atom-atom distance > 1.0 Å | mdtraj `compute_contacts` (L≤100) or scipy KDTree (L>100) | convert_chemgraph.py:319-328, 295-316 |

Notable design choices:
- The clash check **excludes adjacent and i,i+2 residue pairs** explicitly
  (convert_chemgraph.py:312-313: `if atom2res[atom_pair[1]] - atom2res[atom_pair[0]] > 2`),
  so clash distance only triggers on long-range contacts.
- The Cα-Cα cutoff of 4.5 Å is generous (canonical bonded distance ≈ 3.8 Å);
  the C-N cutoff of 2.0 Å is generous (peptide bond ≈ 1.33 Å).
- The clash cutoff of 1.0 Å is **very loose** — heavy-atom van der Waals
  contact is ~3.0 Å. So clash filtering only catches actual coordinate overlap.
- **Filter parameters are hard-coded defaults** in `_get_physical_traj_indices`
  signature (convert_chemgraph.py:382-388). They are exposed by name at the
  function level but **not piped through `save_pdb_and_xtc` or `bioemu.sample.main`** —
  there is no public CLI/API to relax them without monkey-patching.

The `log_physicality()` function in `bioemu/steering.py:95` logs *different*
metrics during sampling for diagnostics (Cα break > 4.5 Å, Cα clash < 3.4 Å)
but these are info-only and not used for filtering.

## 2. Wrapper validation logic

**Source:** `phases/phase-1/subphase-1.1/output/scripts/bioemu_generate_single.py`,
`validate_output()` lines 46-119, called from `main()` lines 237-274.

**Exact rule for `valid: false` (line 106):**

```python
if conformation_count < num_samples * 0.9:
    issues.append(f"Low conformation count: {conformation_count} (expected ~{num_samples}, after physicality filtering)")
```

So the wrapper threshold is **conformation_count < 0.9 × num_samples_requested**,
*not* a tolerance band relative to 2,000 nor relative to predicted pass rate.
Any other issue (missing file, atom-count mismatch, empty NPZ) also flips
`valid → false`.

ExitCode mapping (lines 271-276):
- `valid=true` → `status=success`, `sys.exit(0)`
- `valid=false` AND no exception → `status=partial`, `sys.exit(2)`
- exception → `status=failed`, `sys.exit(1)`

The `partial` return triggers the sbatch wrapper to skip NPZ cleanup
(`bioemu_batch2_short_6h_std.sbatch:174-188`), preserving NPZs for resume —
which is why REV_HV1H2 has 791 NPZs on disk and AACC1_PSEAI has 943.

**Bookkeeping bug (relevant to mitigation option d):** the wrapper compares
`conformation_count` to `num_samples_requested`, where `num_samples_requested`
is the **oversampling target** (= ⌈2000 / pass_rate × 1.3⌉), not 2000. So a
protein that delivers 4,453 conformations (REV_HV1H2 — well above the 2,000
science threshold) gets flagged `partial` because 4453 < 0.9×5532 = 4979. Two
proteins in today's results (`GCN4_YEAST` 2,795 conf and `RPC1_LAMBD` 4,363
conf) already had their `validation.valid` field manually flipped to `true`
with the comment "Promoted from partial: 2795 conformations >= 2000 threshold"
in their generation_status.json — i.e., this bookkeeping decoupling is
already done ad-hoc by HeadAI 1.2.

## 3. Empirical L → pass-rate today (50 proteins complete in batch 2)

Aggregate from all `generation_status.json` in
`/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/`:

### By predicted class × length bin

| Class | L bin | n | mean | min | max |
|-------|-------|--:|----:|----:|----:|
| structured_globular | <60 | 19 | 96.7% | 87.5% | 99.8% |
| structured_globular | 60-99 | 8 | 95.9% | 86.9% | 98.8% |
| structured_globular | 100-199 | 3 | 88.3% | 85.2% | 94.2% |
| structured_globular | 200-299 | 2 | 95.9% | 95.3% | 96.4% |
| structured_globular | 300-499 | 3 | 89.8% | 86.0% | 93.2% |
| idp_like | <60 | 9 | 95.9% | 92.0% | 98.8% |
| idp_like | 60-99 | 5 | 96.6% | 93.4% | 97.8% |
| idp_like | 100-199 | 1 | 80.5% | 80.5% | 80.5% (REV_HV1H2) |
| idp_like | 200-299 | 2 | 49.4% | 20.0% | 78.9% (GCN4_YEAST 20.0%, RPC1_LAMBD 78.9%) |
| idp_like | ≥500 | 1 | 1.4% | 1.4% | 1.4% (CD19_HUMAN — already excluded) |
| large_globular_long | 300-499 | 1 | 60.4% | 60.4% | 60.4% (KCNJ2_MOUSE — exactly on prediction) |

### Linear regression pass_rate = a + b·L (excluding CD19_HUMAN):

| Class | Intercept | Slope | Pred at L=500 |
|-------|----------:|------:|--------------:|
| structured_globular (n=35) | 0.975 | -0.00023/aa | 86.1% |
| idp_like (n=17) | 1.096 | -0.00238/aa | -9.3% (extrapolation invalid; idp_like L>200 is bimodal) |

**Key reading:**
- `structured_globular` shows a **mild ~1.4 pp drop per 100 aa**. With the
  oversampling formula at pass_rate=0.92 × 1.3 = 1.197 effective margin,
  the formula stays above 2,000 conformations until pass-rate falls below
  ~0.71. Linear extrapolation says this happens around L≈1100 aa — well
  outside batch 2.
- `idp_like` is **bimodal at L≥200**: GCN4_YEAST (20.0%) vs RPC1_LAMBD
  (78.9%). The class label "idp_like" mixes proteins where the disordered
  region is small-and-flexible (RPC1) with cases where it is
  large-with-broken-bonds (GCN4, CD19). The 0.47 class average masks this.
- `large_globular_long` has only n=1 — KCNJ2_MOUSE 60.4% matches predicted
  60% to within 0.4 pp. Acceptable inference but lacks N for confidence.

### Today's two ISSUES proteins are not anomalous

- **REV_HV1H2 80.5%:** lies above the linear `idp_like` regression (predicted
  ~83% at L=116 from the early L<200 data plus RPC1_LAMBD), but well below
  the L<100 idp_like cluster (95-98%). Consistent with a mild downward
  trend; sample N=1 in the 100-199 bin. Got 4,453 conformations against a
  2,000 target — 2.2× the criterion.
- **AACC1_PSEAI 85.2%:** structured_globular at L=177; sits in the
  87-94% range observed for structured_globular L=100-199 (n=3). Got
  2,409 conformations against the 2,000 target — 20% margin.

**Both proteins clear the science criterion.** The wrapper flags them
`partial` purely because of the 0.9-of-oversampled-target bookkeeping rule.

## 4. Comparison to batch 1

Reading `shared/notes/1.1-bioemu-passrates.md`:

| Class | Batch 1 calibration (Sub 1.1) | Batch 2 actuals |
|-------|------------------------------:|-----------------:|
| structured_globular L<200 | 85-99% (mostly 95-99%) | 86-100% (mean ≈96%) |
| structured_globular L=200-350 | 87-99% | 95-96% (n=2) |
| structured_globular L=350-500 | 87-97% | 86-93% (n=3) |
| idp_like (mixed) | 35-57% | bimodal: 20%/78% at L≥200; 92-99% at L<100 |
| Largely disordered (>400 aa) | <1% (YAP1 0.7%) | 1.4% (CD19 — same pathology) |

**No evidence of a model-version regression.** Batch 1 used the same
`bioemu-v1.1` model (line 163 of the sbatch). Pass-rate distributions
within each class are statistically indistinguishable. The new variance
that batch 2 surfaces (REV_HV1H2 at 80.5%, AACC1_PSEAI at 85.2%) is
explained by:

1. Batch 1 contained few mid-length idp_like (L=100-200) — REV_HV1H2 is
   the first; the apparent "regression" is just a previously-undersampled
   regime.
2. The structured_globular 100-199 class shows ~88% mean across both
   batches; AACC1_PSEAI 85.2% is at the lower end but within the batch-1
   range (`SPG1 14%` and `PAI1 33%` are batch-1 examples of even lower
   structured pass rates).

## 5. At-risk proteins in remaining queue (43 PENDING)

Predicted physical conformation count using **per-class linear regression
of pass_rate vs L** from the 50 completed proteins:

| Uniprot | L | Class | Pred PR | Req | Pred Got | Risk |
|---------|--:|-------|--------:|----:|---------:|------|
| **P53_HUMAN** | **393** | **idp_like** | **~16%** | **5532** | **~892** | **HIGH (excluded recommended)** |
| HIS7_YEAST  | 220 | structured_globular | 92.5% | 2827 | 2613 | OK |
| TPK1_HUMAN  | 243 | structured_globular | 91.9% | 2827 | 2599 | OK |
| TRPC_SACS2  | 248 | structured_globular | 91.8% | 2827 | 2595 | OK |
| TRPC_THEMA  | 252 | structured_globular | 91.7% | 2827 | 2593 | OK |
| P84126_THETH| 254 | structured_globular | 91.7% | 2827 | 2591 | OK |
| R1AB_SARS2  | 306 | structured_globular | 90.5% | 2827 | 2558 | OK |
| MTH3_HAEAE  | 330 | structured_globular | 90.0% | 2827 | 2543 | OK |
| MK01_HUMAN  | 360 | structured_globular | 89.3% | 2827 | 2523 | OK |
| SERC_HUMAN  | 370 | structured_globular | 89.0% | 2827 | 2517 | OK |
| LYAM1_HUMAN | 372 | structured_globular | 89.0% | 2827 | 2516 | OK |
| TADBP_HUMAN | 414 | large_globular_long | ~60% | 4334 | ~2600 | OK (KCNJ2 calibration) |
| LGK_LIPST   | 439 | large_globular_long | ~60% | 4334 | ~2600 | OK |
| GDIA_HUMAN  | 447 | large_globular_long | ~60% | 4334 | ~2600 | OK |
| NRAM_I33A0  | 453 | large_globular_long | ~60% | 4334 | ~2600 | OK |
| PRKN_HUMAN  | 465 | large_globular_long | ~60% | 4334 | ~2600 | OK |
| I6TAH8_I68A0| 498 | large_globular_long | ~60% | 4334 | ~2600 | OK |
| NCAP_I34A1  | 498 | large_globular_long | ~60% | 4334 | ~2600 | OK |
| Q59976_STRSQ| 501 | large_globular_long | ~60% | 4334 | ~2600 | MARGIN (extrapolation) |
| PPARG_HUMAN | 505 | large_globular_long | ~60% | 4334 | ~2600 | MARGIN |
| SRC_HUMAN   | 536 | large_globular_long | ~60% | 4334 | ~2600 | MARGIN |
| CBS_HUMAN   | 551 | large_globular_long | ~60% | 4334 | ~2600 | MARGIN |
| S22A1_HUMAN | 553 | large_globular_long | ~60% | 4334 | ~2600 | MARGIN |
| A0A2Z5U3Z0  | 565 | large_globular_long | ~60% | 4334 | ~2600 | MARGIN |
| C6KNH7_9INFA| 566 | large_globular_long | ~60% | 4334 | ~2600 | MARGIN |
| Q837P5_ENTFA| 571 | large_globular_long | ~60% | 4334 | ~2600 | MARGIN |
| PABP_YEAST  | 577 | large_globular_long | ~60% | 4334 | ~2600 | MARGIN (disorder_fraction=0.40 — track) |
| SHOC2_HUMAN | 582 | large_globular_long | ~60% | 4334 | ~2600 | MARGIN |
| Q837P4_ENTFA| 589 | large_globular_long | ~60% | 4334 | ~2600 | MARGIN |
| 14× SHORT (L=65-72) | <100 | structured_globular / idp_like | 92-96% | 2827-5532 | ≥2700 | OK |

(All 14 SHORT pending proteins are L<75, predicted >92% pass rate. None at
risk in the SHORT queue beyond what we have already seen.)

**Single concrete at-risk protein: P53_HUMAN.**

P53_HUMAN's `disorder_fraction = 0.5827` (from `batch2_screened.csv`) is just
below the 0.60 exclusion threshold — **the same blind spot that let CD19_HUMAN
through** (CD19 was 0.5018; cross-agent note 1.2-bioemu-batch2-passrates.md
§"CD19_HUMAN Exclusion (2026-04-26)" describes this exact failure mode:
"structured Ig-like domains dilute the signal from the disordered cytoplasmic
tail"). P53 has the same architecture: structured DNA-binding domain (residues
~100-300) flanked by disordered N-terminal transactivation domain and C-terminal
tetramerization/regulatory tail. Predicted ~16% pass rate; oversampling target
of 5,532 yields ~892 conformations — far below the 2,000 criterion.

## 6. Inspection of REV_HV1H2 rejected vs accepted samples

Reconstructed 1,050 frames from the first 150 NPZ files using
`bioemu.convert_chemgraph.get_atom37_from_frames()`, then re-ran the filter.
Source: `_filter_unphysical_traj_masks` returns three independent masks.

**Per-criterion pass rates on this subsample:**

| Criterion | Pass | Threshold | Mean over frames |
|-----------|-----:|-----------|-----------------:|
| Cα-Cα ≤ 4.5 Å | 89.5% | 4.5 Å | 3.82 Å (mean), max 4.80 Å (per-frame mean) |
| C-N ≤ 2.0 Å   | 84.8% | 2.0 Å | 1.36 Å (mean), max 2.72 Å (per-frame mean) |
| Non-clash > 1.0 Å | 98.6% | 1.0 Å | — |
| **All three** | **83.3%** (consistent with global 80.5% on full ensemble) |

**Failure overlap (210-frame subsample, 35 rejects):**
- Only Cα fail: 1 (3%)
- Only C-N fail: 10 (29%)
- Only clash fail: 2 (6%)
- Cα + C-N together: 21 (60%)
- Other multi-criterion: 1 (3%)
- All-three fail: 0

**The C-N peptide bond filter is the dominant rejection mode,** often
co-firing with Cα. Among rejected frames, the maximum failing C-N distance:
median 2.83 Å, p90 ~10 Å, max 116.7 Å. Median excess over the 2.0 Å threshold
is **0.83 Å (41%)** — these are not marginal failures: they are macroscopic
backbone breaks. Same for Cα: among failing frames, median max-Cα-Cα = 6.42 Å,
p90 = 22.5 Å — frames with completely disconnected residues.

**Clustering of failures along sequence (1,050 frames):**

Top-10 sequence positions with most C-N breaks all fall in residues 94-115:
- pos 114-115: 17 breaks (1.6%)
- pos 96-97: 15 breaks (1.4%)
- pos 113-114, 97-98, 110-111, 98-99, 106-107, 94-95, 0-1, 105-106: 11-12 each

REV_HV1H2 sequence (HIV Rev, 116 aa):
```
MAGRSGDSDEELIRTVRLIKLLYQSNPPPNPEGTRQARRNRRRRWRERQRQ  (1-50)
IHSISERILSTYLGRSAEPVPLQLPPLERLTLDCNEDCGTSGTQGVGSPQI  (51-100)
LVESPTVLESGTKE                                        (101-114)
```

Residues 94-115 are the C-terminal disordered region (mostly low-complexity
Pro/Gly/Ser/Ala). This is exactly the BioEmu signature already documented for
YAP1 and CD19: **disordered tails produce broken backbone bonds**. REV_HV1H2
is a smaller-scale instance of the same pathology (only ~20-25% of residues
in the disordered region, vs CD19's ~45% and YAP1's ~70%). Hence pass rate
80% rather than 1%.

**Verdict on the filter:** rejected frames are clearly unphysical (median
>40% bond-length excess over a generous 2.0 Å cutoff; median 6.4 Å Cα-Cα
gaps); accepted frames are physically reasonable. **The filter is not too
strict — it is doing what it was designed to do.** Loosening would admit
broken-backbone artifacts into downstream analysis (RMSF, contact maps,
PCA modes) and corrupt the central Gamma test (RSALOR + RMSF vs RSALOR).

## 7. Mitigation menu (ranked)

### 7.1. Pre-emptive exclusion of P53_HUMAN (RECOMMENDED, primary action)

**What:** Cancel array task `_25` (P53_HUMAN) in the MED queue (10730245)
before it runs. Document as a third disorder-screen blind-spot exclusion in
`shared/notes/1.2-bioemu-batch2-passrates.md`, alongside YAP1 and CD19.
Manifest counts: 92 → 91 proteins, success criterion is ≥90.

**Why:** Same pathology as CD19_HUMAN (mixed-architecture protein, structured
domain dilutes whole-sequence disorder fraction below 0.60 threshold). Linear
regression predicts ~16% pass rate × 5,532 oversampling = ~892 conformations
(< 2,000). Even with topup to 14,000 (GCN4-style), expected ~2,240 conformations
— marginal at best, ~440 GPU-hours = ~6,600 SU on RTX 5000 Ada — and the
result is conformations dominated by the disordered tail, scientifically
limited. **Same drop-not-rescue calculus as YAP1.** P53 is `OrganismalFitness`
type so does not affect the binding+activity primary test (N=57); drops
ProteinGym total from 217 → 216 in worst case.

**Cost:** zero (cancellation only); 1 protein from manifest.
**SU saved:** ~5–10 hours wall-clock on RTX 5000 Ada × 15 SU = ~75–150 SU avoided.
**Risk:** drop is documented in advance; future P53 is recoverable via either
(a) ProteinGym Phase 2 IUPred3 re-screen + replacement protein, or (b) WW-domain-style
trimmed FASTA on the structured DNA-binding domain only (residues ~100-300)
if the assay genuinely targets the structured core.

### 7.2. Trust the existing oversampling for everyone else (RECOMMENDED, primary action)

**What:** Do not change the oversampling multiplier. The existing
`num_samples = ceil(2000 / pass_rate × 1.3)` formula already provides
~1.3× safety margin and is delivering 2,500-2,800 conformations across
the structured_globular cohort (target 2,000). The 1.3 multiplier was
calibrated in Sub 1.1 specifically to accommodate the within-class variance
seen today.

**Why not raise to 1.5× or 2.0×:**
- For the 27 pending structured_globular L<300 proteins, 1.3× → 2,827 already
  delivers ≥2,400 conformations on every protein observed so far. Raising to
  1.5× → 3,260 buys ~370 extra conformations at the cost of ~12% more
  GPU-hours per protein — **wasted compute** for structured proteins.
- For the 11 pending large_globular_long proteins (L=414-589), 1.3× → 4,334
  is already calibrated against KCNJ2_MOUSE's 60.4% actual rate, giving
  ~2,600 expected conformations. Raising to 1.5× → 5,005 buys margin
  against a possible mild slope at L>500, but the only data point we have
  (KCNJ2 at L=428) was exactly on prediction.

**Cost change:** +12% per-protein GPU-hours = ~+10 hours total = ~+150 SU.
Negligible compared to the data benefit.

**Action recommended only if** MED/LONG come in below predicted (e.g., a
large_globular_long L>500 protein lands at <55% pass). Then react with
per-protein topup, not blanket raise.

### 7.3. Topup any final proteins that miss 2,000 (RECOMMENDED, contingent)

**What:** As MED/LONG arrays complete, monitor each protein's
`generation_status.json`. For any protein with `conformation_count < 2000`,
follow the existing per-protein topup policy (cross-agent note
`1.2-bioemu-batch2-passrates.md` §"Per-protein topup policy"):
1. Compute actual pass rate from the run.
2. Update `expected_pass_rate` and `num_samples` in `batch2_manifest.csv`.
3. Resubmit `--array=<idx>` with the same sbatch; bioemu auto-resumes from
   existing NPZs via `count_samples_in_output_dir`.

**Cost:** one ~6-12 hr resubmission per affected protein, ~150-200 SU each.
Only triggered in proportion to actual underage.

**Why this is sufficient:** the topup policy already has precedent
(GCN4_YEAST, A0A1I9GEU1_NEIME, OXDA_RHOTO in batch 2 v2 results). It
addresses any remaining undershoot without anyone touching the global
formula. The policy is "resume + add batches", which is bandwidth-efficient
because the diffusion sampler is stateless across batches.

### 7.4. Loosen the physicality filter (REJECT)

**What would it look like:** monkey-patch
`_get_physical_traj_indices` defaults (e.g., max_cn_seq_distance 2.0 → 2.5 Å)
to admit marginally-broken frames.

**Why reject:**
- Section 6 evidence: rejected frames are not marginal. Median bond-length
  excess is 0.83 Å (41% over threshold), p90 is ~10 Å, max 116 Å. These
  are unphysical structures, not slightly stretched bonds.
- Downstream features depend on backbone integrity. RMSF on a broken-tail
  ensemble overestimates flexibility precisely where the model is least
  reliable. Residue-residue contact frequencies become noise on broken
  segments.
- The Gamma central test (RSALOR + RMSF vs RSALOR) is sensitive to
  exactly this kind of artifact. Loosening the filter would likely flip
  the test outcome by adding noise to the dynamics signal.
- BioEmu authors set these defaults; deviating without scientific
  justification weakens the manuscript's defense of methods.
- "Uncompromised data" verdict from user → rejecting unphysical frames is
  the right behavior, not a problem to engineer around.

**No scientific defense exists for this option in this project's context.**

### 7.5. Reframe wrapper validation: `valid` if `conformation_count ≥ 2000` (CONSIDER, parallel housekeeping)

**What:** Modify `bioemu_generate_single.py` line 106 from
```python
if conformation_count < num_samples * 0.9:
```
to
```python
if conformation_count < 2000:
```
(or keep both as warnings, only the second triggering `valid=false`).

**Why:** Today's REV_HV1H2 4,453 conformations and AACC1_PSEAI 2,409
conformations are both **scientifically successful** (2.2× and 1.2× the
science target) but flagged `partial` because the wrapper compares against
the oversampling target. This generates spurious ExitCode 2 events that
trigger NPZ retention (wasting ~10 GB of disk per protein) and SLURM
mail alerts. HeadAI 1.2 has already manually flipped two proteins'
`validation.valid` field post-hoc.

**Cost:** trivial code change; zero compute. Aligns ExitCode/cleanup
behavior with the actual success criterion.

**Caveat per task constraints:** "DO NOT modify production scripts" —
this is a bookkeeping change, but `bioemu_generate_single.py` is in the
sub-1.1 production scripts directory. Recommend HeadAI 1.2 escalates this
to user as a non-blocking process improvement; make the change for the
remaining batch 2 + future batches but DO NOT replay completed jobs.
**This is housekeeping; the fix doesn't add or change data.**

### 7.6. Switch model variant to bioemu-v1.0 (REJECT)

**What:** Re-run problem proteins with `--model-name bioemu-v1.1` →
`bioemu-v1.0`.

**Why reject:**
- The Microsoft BioEmu repo has no published characterization that v1.0
  has different physicality behavior than v1.1; no quantitative claim
  exists in the model card on Hugging Face. Switching introduces an
  unmotivated source of variance into the manuscript.
- Mixing models across batch 1 (v1.1) + batch 2 (v1.1+v1.0 mix) breaks
  the "all proteins use the same generator" requirement of the central
  Gamma ablation.
- The OSF v3 pre-registration locks `bioemu-v1.1` as the model; mid-batch
  switch invalidates the pre-reg.

### 7.7. Topup with denoiser_type='heun' or more denoising steps (CONSIDER, future investigation)

The BioEmu `save_pdb_and_xtc` warning message itself suggests two recovery
paths beyond increasing samples: change `denoiser_type` to `'heun'`, or
increase denoising steps via `denoiser_config_path`. These are documented
in `bioemu.sample.DEFAULT_DENOISER_CONFIG_DIR`. They could improve the
per-frame physicality rate (better numerical integration produces fewer
broken frames) at the cost of GPU-time per sample.

**Why deferred:** unknown improvement magnitude on a per-protein basis;
would require characterization runs first; not necessary in the current
data picture.

## 8. "Uncompromised data" verdict

**Definition of "uncompromised" in this project:**
- Per Gamma proposal (§Approach.1): "BioEmu v1.3.1 generates 2,000 backbone
  conformations per protein." [Proposal/Gamma.md:23]
- Per HeadAI 1.2 success criterion #4: "BioEmu batch 2: ≥90 of ~100 selected
  ProteinGym proteins reach ≥2,000 physical conformations."
- Downstream usage (Gamma §Approach.2): RMSF, per-residue SASA variance,
  secondary structure propensity, contact frequency matrices, B-factor
  profiles, PCA-based flexibility modes. All are statistical aggregates over
  the ensemble; their convergence depends on N_conformations, not on
  reaching the oversampling target.

**Sample-size reasoning for the 2,000 floor.** RMSF standard error on a
2,000-frame ensemble with effective sample size n_eff ≥ 200 (typical for
diffusion samples, not autocorrelated like MD frames) gives σ_RMSF ≈
RMSF / √(2·n_eff) ≈ ~5% relative error on per-residue RMSF — well below
the variance the central Gamma ablation needs to detect. RMSF differences
on ProteinGym between RSALOR-equivalent and RSALOR+RMSF models target
ΔSpearman ~0.04 over N=57 assays; that resolves at ~1,500-2,000 frames per
protein. So 2,000 is a calibrated science floor, not an arbitrary number.

**Therefore:** REV_HV1H2 with 4,453 frames is **scientifically equivalent**
to F7YBW8_MESOW with 5,364 frames. Both are well-converged ensembles in the
shape parameters that drive downstream features. The "ISSUES" tag on
REV_HV1H2 is purely a wrapper-bookkeeping artifact (§7.5). 4,453 frames is
2.2× the science floor; the per-residue RMSF SE is ~3-4% on REV_HV1H2 —
indistinguishable from F7YBW8_MESOW.

**Where data IS compromised:**
- CD19_HUMAN (already excluded): 90 frames. Below floor. Drop justified.
- P53_HUMAN (pending; recommend exclude): predicted ~900 frames. Below
  floor. Drop justified by same reasoning as CD19/YAP1.

**Where data IS NOT compromised (current state):**
- All 50 completed proteins except CD19_HUMAN have ≥2,000 conformations.
  GCN4_YEAST has 2,795 (oversampled to 14K because the L=281 idp_like
  case was identified early and topped up). KCNJ2_MOUSE has 2,619.
  RPC1_LAMBD has 4,363. **All exceed the 2,000 floor.**

**Net assessment:** Today's "ISSUES" on REV_HV1H2 and AACC1_PSEAI is a
false alarm in scientific terms. The wrapper is over-eager. The current
data is uncompromised against the OSF-pre-registered criterion. **The only
material risk to "uncompromised" is P53_HUMAN if it is allowed to run the
oversampling target as planned and lands at ~900 conformations.**

## 9. Top recommendation

**Single best action for HeadAI 1.2:**

**Pre-emptively exclude P53_HUMAN from batch 2.** Rationale: it is the only
pending protein predicted to land below the 2,000-conformation floor (per
§5 regression: ~16% pass × 5,532 = ~892 frames). Its disorder-screen
`disorder_fraction = 0.5827` is just below the 0.60 threshold — an exact
analogue of CD19_HUMAN's 0.5018, which already triggered the same blind-spot
exclusion. Same architectural pathology (structured DBD + disordered tails).
Same risk that no realistic oversampling reaches the floor. Same
scientific-irrelevance argument: a 16% pass rate produces a biased
subsample, not a Boltzmann ensemble.

**Concrete steps for HeadAI:**
1. `scancel 10730245_25` (P53_HUMAN MED-cohort task) before it dispatches.
2. Update `batch2_manifest.csv` and `1.2-bioemu-batch2-passrates.md` with
   "P53_HUMAN excluded 2026-05-07; same pathology as CD19/YAP1; predicted
   16% pass rate × 5,532 = ~892 frames < 2,000 floor; disorder_fraction
   0.5827 was a screen-edge miss."
3. Confirm 92 → 91 proteins still meets the ≥90 success criterion (it does:
   91 ≥ 90).
4. **Do NOT change** the oversampling formula. **Do NOT modify** the
   physicality filter. **Do NOT replay** completed proteins.
5. **Continue monitoring** MED + LONG arrays as they complete; apply the
   existing per-protein topup policy if any individual protein finishes
   <2,000 (none predicted, but topup is the existing standard remedy).
6. **Optional housekeeping (parallel):** flag the wrapper `valid` threshold
   to user as a future improvement (compare to 2,000 not to oversampling
   target). Not blocking; not retroactive.

The current data state will then be:
- 91 proteins targeted in batch 2 (one excluded for documented disorder
  pathology, parallel to CD19/YAP1).
- All 91 expected to land ≥2,000 conformations under existing oversampling.
- No global formula changes; no filter changes; no model-version churn.
- "Uncompromised data" criterion met both narrowly (≥2,000 frames each)
  and broadly (each ensemble is a representative diffusion-Boltzmann sample).

---

## Evidence trail

- BioEmu filter source: `~/.conda/envs/env-bioemu/lib/python3.10/site-packages/bioemu/convert_chemgraph.py:331-379`
  (filter masks), `:382-402` (composite indices), `:432-514` (save+filter entry point)
- BioEmu sample entry: `~/.conda/envs/env-bioemu/lib/python3.10/site-packages/bioemu/sample.py:85,112,291`
- Wrapper validation: `phases/phase-1/subphase-1.1/output/scripts/bioemu_generate_single.py:46-119` (validate_output), `:271-276` (exit codes)
- Sbatch wrapper: `phases/phase-1/subphase-1.2/output/scripts/bioemu_batch2_short_6h_std.sbatch:174-188` (NPZ cleanup gate)
- Manifest: `phases/phase-1/subphase-1.2/output/scripts/batch2_manifest.csv` (93 entries; 92 active after CD19 exclusion; 91 if P53 excluded)
- Disorder screen (CD19/P53 borderline): `phases/phase-1/subphase-1.2/output/scripts/batch2_screened.csv` line 36 (P53_HUMAN, disorder_fraction=0.5827, foldindex_global=-0.0024, frac_windows_disordered=0.6006)
- Per-protein generation status: `/nfs/roberts/scratch/pi_mg269/rag88/gamma/bioemu-ensembles/batch2/<UNIPROT>/generation_status.json` (50 files complete as of 2026-05-07T23:42Z)
- Cross-agent context: `shared/notes/1.1-bioemu-passrates.md` (batch 1 calibration + YAP1 drop), `shared/notes/1.2-bioemu-batch2-passrates.md` (batch 2 plan, CD19 exclusion, topup policy, 3-tier walltime split)
- Today's two ISSUES JSONs: `REV_HV1H2/generation_status.json` (4453 frames, 80.5%), `AACC1_PSEAI/generation_status.json` (2409 frames, 85.2%)
- REV_HV1H2 inspection: 1,050-frame reconstruction from 150 NPZ files; per-criterion masks applied via `_filter_unphysical_traj_masks`; clustering analysis on residue positions
- Queue snapshot (2026-05-07): `squeue -u rag88` — 10730244 SHORT mostly running, 10730245 MED + 10730246 LONG fully PENDING
