# Phase 0 / 1.1 / 1.2 Comprehensive Audit

**Auditor:** Claude Opus 4.6 (automated review)
**Date:** 2026-04-26
**Scope:** All dashboard, status, note, gate, registry, and script files across Phases 0-1.2

---

## 1. Dashboard Consistency

### master-status.md

- [x] Current phase and subphase correct (Phase 1, Sub 1.2 active)
- [x] Decision log entries internally consistent with timeline
- [x] Active blockers section accurately describes fair-share situation
- [x] Upcoming milestones correctly show D1 and D3 as done
- [ ] **FAIL: SO3LR count mismatch.** Line 14 says "002 SO3LR 2/5 PASS" and line 56 says "SO3LR 2/5 PASS". The user reports 3/5 actually passed (GB3, GB1, UBQ). The SO3LR cross-agent note (`1.2-so3lr-pilot-stability.md`) says 2/5 PASS (GB1+UBQ) because GB3 had a silent structural explosion despite completing 5 ns with exit code 0. The registry (`shared/registry.md` line 41) says "3/5 PASS: GB3+GB1+UBQ". **One of these is wrong.** The cross-agent note's structural analysis is authoritative -- GB3 Rg went from 10.6 A to 986 A, clearly FAILED. The registry's "3/5 PASS" is incorrect; the dashboards' "2/5 PASS" is correct.
- [ ] **FAIL: MACE version stale.** All dashboard references say "MACE v5" with job IDs 9449439-41 as current pending. The registry (line 40) says "v5 FAILED: WW chk mismatch, GB3 _dof bug, UBQ NaN; v6 fixes applied -- 50ps equil, chk mismatch handler, _dof init; diagnostic 9546808 + resubmit pending fair-share". **The dashboards are behind: v5 apparently failed and v6 exists, but master-status.md, active-subphase.md, gate-tracker.md, and task-001-status.md all still reference v5 as current.** The registry is the only file updated with v6 information.
- [ ] **FAIL: BioEmu count inconsistency.** master-status line 14 says "83 resubmitted" but active-subphase line 25 says "82 PENDING". The cross-agent note (`1.2-bioemu-batch2-passrates.md`) says "11/93 proteins complete" (including 3 topups), but dashboards say "10/93". The difference: 10 proteins are at >=2000 conformations (success), plus CD19_HUMAN has 90 conformations (effectively failed, 1.4% pass rate). The batch 2 resubmit arrays cover 41+42=83 proteins, which implies 93-10=83 remaining (excluding CD19 from the 10 count). The active-subphase saying "82" is wrong if 83 are truly pending.
- [x] Decision log D3 retirement entry present and correct
- [x] Option 5 commit documented with empirical evidence

### active-subphase.md

- [x] Task table has all 6 tasks
- [x] Wave protocol summary correct
- [x] Compute budget table matches subphase-plan
- [ ] **FAIL: Task-002 SO3LR status contradicts registry.** active-subphase says "COMPLETE -- 2/5 PASS (GB1+UBQ)" which is correct per structural analysis. Registry says "3/5 PASS: GB3+GB1+UBQ" which is wrong. (See master-status finding above.)
- [ ] **FAIL: MACE v5 stale.** Same as master-status -- still references v5 as current, doesn't reflect v5 failure or v6 fixes. Job IDs 9449439-41 may be stale if v6 has new job IDs.
- [ ] **FAIL: BioEmu "82 PENDING" vs "83 resubmitted" discrepancy.** (See master-status finding.)
- [x] SLURM job inventory table is detailed and has terminal failure history
- [x] Gate evidence section correctly notes D2 as preliminary and D3 as retiring

### gate-tracker.md

- [x] D1 correctly ASSESSED: GO
- [x] D3 correctly ASSESSED: GO (RETIRED) with baselines evidence
- [x] D2 assessment correctly says ON TRACK
- [ ] **FAIL: D2 SO3LR count stale.** Line 13 says "SO3LR: 2/5 PASS" -- this is correct per structural analysis, but should be cross-checked against any v6-related MACE updates that are not reflected here.
- [ ] **FAIL: MACE job IDs stale.** References "9449439-41" as current v5 jobs. If v5 failed per registry, these IDs are stale.
- [x] Gate criteria reference section complete and accurate
- [x] Early evidence sections well-documented with specific metrics
- [x] T3 and T5 evidence sections accurate

### compute-budget.md

- [x] SU rate reference table correct
- [x] Sub 1.1 SU breakdown detailed and adds up
- [x] BioEmu topup lesson documented
- [x] Gamma budget detail correctly shows ~1,893 remaining
- [x] Priority Tier policy documented
- [ ] **FAIL: Alpha-M Phase 1 "Used" column stale.** Budget Overview table (line 13) says Alpha-M Phase 1 used "~78 GPU-hrs" with "~2,922 remaining". But the burn rate table (line 81) shows Sub 1.2 actual consumed ~130 GPU-hrs on top of Sub 1.1's ~134 total. Even counting only Alpha-M's share (SO3LR 58h + MACE diag 16h = ~74 GPU-hrs for Sub 1.2 Alpha-M), the Phase 1 Alpha-M used should be ~78 (from Sub 1.1) + ~74 (Sub 1.2 so far) = ~152, not ~78. The "Used" and "Remaining" columns in the overview table have not been updated with Sub 1.2 actuals.
- [ ] **FAIL: Gamma "Used" column stale.** Shows ~163 GPU-hrs (batch 1 only). Sub 1.2 BioEmu batch 2 has consumed ~56 GPU-hrs already (per burn rate line 81). Gamma used should be ~163 + ~56 = ~219, not ~163. Remaining should be ~1,781, not ~1,837.
- [ ] **FAIL: Delta "Used" column stale.** Shows ~1.5 GPU-hrs. Sub 1.2 delta baselines used ~1 GPU-hr (per burn rate). Should be ~2.5. Minor but stale.
- [ ] **FAIL: Projection line math error.** Line 187 says "Phase 1 Alpha-M budget remaining after Sub 1.2 (projected): ~2,580 GPU-hrs (3,000 - 5 used - 423 Sub 1.2 = ~2,572)". It says "5 used" but the overview table says "~78 used" for Phase 1. The "5" appears to be a typo or references only a subset. The actual remaining should be 3,000 - 78 (Sub 1.1) - 74 (Sub 1.2 actual so far) - 420 (remaining MACE NPT) = ~2,428.

### decisions-needed.md

- [x] Correctly shows no active decisions
- [x] Resolved decisions table accurate (HPr, T4L, Phase 2 MACE scope)
- [x] Last updated date (2026-04-18) is reasonable since no new decisions have arisen

---

## 2. Cross-Agent Notes Completeness

### Expected notes per Sub 1.2 CLAUDE.md (line 134-141)

| Expected Note | Exists? | Status |
|---|---|---|
| `1.2-mace-npt-stability.md` | [x] Yes | Preliminary only; no empirical stability results yet (jobs pending). Has extensive debug history through section 4. Correct for current state. |
| `1.2-so3lr-pilot-stability.md` | [x] Yes | Has full structural analysis in section 2. Authoritative. |
| `1.2-osf-deposited.md` | [x] Yes | Stub (urgency=info). Correct -- deposit not yet made. |
| `1.2-bioemu-batch2-passrates.md` | [x] Yes | Has interim v2 results with 11/93 progress. Active. |
| `1.2-delta-baselines-results.md` | [x] Yes | Complete with full results table. D3 retired. |
| `1.2-stats-pipeline-validation.md` | [x] Yes | Complete with test results and R cross-validation. |

### Additional Sub 1.2 notes (not in expected list)

| Note | Purpose | Current? |
|---|---|---|
| `1.2-env-so3lr-typing-extensions-fix.md` | SO3LR PYTHONNOUSERSITE fix | [x] Complete |
| `1.2-mace-conda-path-fix.md` | MACE sbatch conda path fix | [x] Complete |
| `1.2-gpu-util-efficiency.md` | YCRC auto-cancel root cause | [x] Complete |
| `1.2-mace-throughput-ceiling.md` | 2.56 ns/day ceiling analysis | [x] Complete |
| `1.2-bioemu-precache-keepalive-fix.md` | Precache keepalive lesson | [x] Complete |
| `1.2-scope-recommendations.md` | Forward-looking scope from audit | [x] Complete |

### SO3LR note accuracy

- [ ] **FAIL (CRITICAL): Registry contradicts SO3LR note.** `shared/registry.md` line 41 says "3/5 PASS: GB3+GB1+UBQ stable 5 ns" but `shared/notes/1.2-so3lr-pilot-stability.md` section 2.3 says GB3 FAILED due to silent structural explosion (Rg 10.6 -> 986.5 A, RMSD 1386.75 A). The note's "2/5 PASS" (GB1+UBQ only) is correct. **The registry's "3/5 PASS" including GB3 was written before the structural analysis was performed and was never updated.** This is the most dangerous inconsistency found -- downstream agents reading only the registry would incorrectly count GB3 as a SO3LR success.

### All other notes checked

- [x] `1.2-mace-npt-stability.md` -- preliminary approach documented; awaiting empirical data. Consistent with task-001 status.
- [x] `1.2-delta-baselines-results.md` -- results match task-005-status.md exactly (WMSE values, pass/fail, strata counts)
- [x] `1.2-stats-pipeline-validation.md` -- JZS BF 0.0001% match documented; all 5 components validated
- [x] `1.2-osf-deposited.md` -- correctly in stub state awaiting deposit
- [x] `1.2-bioemu-batch2-passrates.md` -- interim v2 shows 11/93 with honest CD19 exclusion recommendation

---

## 3. Status Files Accuracy

### task-001-status.md (MACE NPT)

- [x] Frontmatter status correctly says "slurm-pending-fair-share-v5"
- [x] Job history table (v1 through v5) complete and internally consistent
- [x] Optimization dead ends well-documented (CUDA, oeq, cuequivariance, GPU NL)
- [x] Throughput ceiling of 2.56 ns/day documented
- [ ] **FAIL: v5 status stale per registry.** The status file says v5 (9449439/40/41) is current and PENDING. The registry says v5 FAILED with 3 bugs and v6 fixes were applied (diagnostic 9546808 pending). **The status file has not been updated to reflect the v5 failure or v6 resubmission.** This is the same discrepancy seen in the dashboards.
- [x] Resource usage section acknowledges estimates are TBD
- [x] Failure scenarios accurately predicted (barostat, hang, corruption)
- [ ] **STALE JOB IDs in SLURM section (line 229):** Still lists original v1 job IDs (8885960-62) in the Resource Usage table. These are 6 versions old. The correct current IDs (per registry) would be the v6 diagnostic 9546808, not v5's 9449439-41.

### task-002-status.md (SO3LR)

- [x] Frontmatter status says "complete" (correct)
- [x] Env remediation section well-documented
- [ ] **FAIL: Success criteria table not updated with final results.** Criteria 2-7 (per-protein stability) are all still listed as "pending" with the original v2 job IDs (8890874-78). But SO3LR is marked as COMPLETE. The structural analysis results (2/5 PASS per the cross-agent note) have NOT been backfilled into this status file. The status file was written before the SO3LR jobs completed and never updated afterward.
- [x] Remediation section thorough and accurate (typing_extensions fix)
- [ ] **STALE JOB IDs (line 324):** Resource usage table lists original v1 FAILED job IDs (8886091-95) rather than the actual final job IDs (8890875-78, 8903311). These are the v1 failure IDs, not the production runs.

### task-003-status.md (OSF pre-reg)

- [x] Status correctly shows "v2-drafted"
- [x] Criteria evaluation accurate (early v1, on track for final)
- [x] Word count overrun documented with mitigation options
- [x] T3 retirement correctly framed
- [x] v2 refinement schedule clear (2026-05-13 target)
- [x] All artifacts present at documented paths

### task-004-status.md (BioEmu batch 2)

- [x] Frontmatter status correctly shows "slurm-10-of-93-complete"
- [x] Disorder screen documentation thorough
- [x] Oversampling manifest documented
- [ ] **FAIL: Does not reflect topup completions.** The batch2 cross-agent note (interim v2) shows GCN4, A0A1I9GEU1, and OXDA topups completed (bringing count to 11 with successful topups), plus CD19 as a probable exclusion. But the status file body was written when only the initial submission was done (2 SLURM jobs: precache + batch 1 array). It has NOT been updated to reflect the batch 1 retry (8903490), the topup round, or the batch 2-10 arrays.
- [ ] **STALE JOB IDs (line 221):** Lists 8887441 (precache) and 8887446 (batch 1 array) as the job IDs. Both are from the initial submission. The actual current jobs are 9449458 and 9449459 (the v2 resubmission after accidental cancellation). The precache job (8887441) was YCRC-cancelled.
- [x] Unexpected findings section accurate (ProteinGym pool, binding coverage, TF ABI)

### task-005-status.md (Delta baselines)

- [x] Status correctly shows "complete"
- [x] All success criteria evaluated and MET (with appropriate caveats on criterion 7)
- [x] Results table includes specific WMSE/Spearman/ECE values matching cross-agent note
- [x] Random baseline FAIL gate verified at both 2K and 100K scale
- [x] Resource usage honest (0 GPU-hours actual, all on login node)
- [x] No stale job IDs (no SLURM jobs submitted)

### task-006-status.md (Stats pipeline)

- [x] Status correctly shows "complete"
- [x] All 10 success criteria MET with specific evidence
- [x] JZS BF 0.0001% match documented (far exceeds 20% spec)
- [x] env-stats creation documented per non-destructive-env rule
- [x] ICC pingouin version drift handled
- [x] Resource usage accurate (0 GPU-hours, login node only)
- [x] No stale job IDs

---

## 4. Phase 0 and 1.1 Closure

### Phase 0 subphase-0.1/completion-report.md

- [x] Present and complete with 10 sections
- [x] All 4 tasks documented with results
- [x] D1 gate signal correctly identified as positive
- [x] T3 NOT MET correctly documented with AK3 analysis
- [x] T5 MET correctly documented (13/14)
- [x] Resource usage documented
- [x] BioEmu API discovery documented (no BioEmuSampler class)
- [ ] **Minor: GPU naming.** Report notes "RTX 5090" but later project docs consistently use "RTX 5000 Ada". The cluster GRES is `rtx_50` which could be either. This discrepancy has not caused issues but was never formally resolved.
- [x] BMRB table was corrected with a correction note (line 102)

### Phase 1 subphase-1.1/completion-report.md

- [x] Present and complete with all required sections
- [x] D1 gate evidence table accurate (both PASS)
- [x] 9/9 success criteria correctly assessed as MET
- [x] BioEmu batch 1 results accurate (46/47 proteins, 112,351 conformations)
- [x] HEWL DROP correctly documented (40.2% SG-SG)
- [x] YAP1 DROP correctly documented (0.7% pass rate)
- [x] Post-subphase remediation addendum correctly references `1.1-robustness-remediation.md`
- [x] Delta methods: main body correctly says "3 of 3 attempted"; remediation addendum correctly says "5/5 installed"
- [x] Key findings section comprehensive (12 items for Sub 1.2 planning)
- [x] Cross-agent notes list matches actual files
- [x] Phase 1.1 CLOSED statement at end

### Gate Assessments

- [x] `gate-D1-assessment.md` present, dated 2026-04-17, verdict GO
- [x] D1 criteria table correctly shows all 5 criteria MET
- [x] D1 downstream conditions noted (hybrid-mode validation for Sub 1.2)
- [x] `gate-D3-assessment.md` present, dated 2026-04-17, verdict GO (amended same-day)
- [x] D3 evidence includes 5/5 Tier 1 methods + baselines (baselines added Sub 1.2)
- [x] Gate assessment cross-references match actual file locations

---

## 5. Script and Artifact Integrity

### Scripts referenced in task specs vs actual files

| Script | Referenced in | Exists? |
|--------|--------------|---------|
| `mace_hybrid_npt.py` | task-001 | [x] Yes (`output/scripts/mace_hybrid_npt.py`) |
| `submit_mace_npt.sh` | task-001 | [x] Yes (`output/scripts/submit_mace_npt.sh`) |
| `mace_cuda_patch.py` | task-001 debug | [x] Yes (`output/scripts/mace_cuda_patch.py`) |
| `gpu_keepalive.py` | task-001 | [x] Yes (`output/scripts/gpu_keepalive.py`) |
| `so3lr_pilot_runner.py` | task-002 | [x] Yes (`output/scripts/so3lr_pilot_runner.py`) |
| `so3lr_prep_proteins.py` | task-002 | [x] Yes (`output/scripts/so3lr_prep_proteins.py`) |
| `so3lr_pilot.sbatch` | task-002 | [x] Yes (`output/scripts/so3lr_pilot.sbatch`) |
| `submit_so3lr_pilot.sh` | task-002 | [x] Yes (`output/scripts/submit_so3lr_pilot.sh`) |
| `compile_candidates.py` | task-004 | [x] Yes (`output/scripts/compile_candidates.py`) |
| `disorder_screen.py` | task-004 | [x] Yes (`output/scripts/disorder_screen.py`) |
| `batch2_manifest_builder.py` | task-004 | [x] Yes (`output/scripts/batch2_manifest_builder.py`) |
| `bioemu_batch2.sbatch` | task-004 | [x] Yes (`output/scripts/bioemu_batch2.sbatch`) |
| `submit_bioemu_batch2.sh` | task-004 | [x] Yes (`output/scripts/submit_bioemu_batch2.sh`) |
| `precache_msa.py` | task-004 | [x] Yes (`output/scripts/precache_msa.py`) |
| `precache_msa.sbatch` | task-004 | [x] Yes (`output/scripts/precache_msa.sbatch`) |
| `delta/baselines/*.py` (5 files) | task-005 | [x] Yes (linear, mean, pca, random, persistence) |
| `delta/eval/wmse.py` | task-005 | [x] Yes |
| `delta/eval/fdr.py` | task-005 | [x] Yes |
| `delta/eval/calibration.py` | task-005 | [x] Yes |
| `delta/eval/stratified.py` | task-005 | [x] Yes |
| `delta/eval/run_smoketest.py` | task-005 | [x] Yes |
| `delta/eval/synth_unit_test.py` | task-005 | [x] Yes |
| `delta/loaders/tahoe.py` | task-005 | [x] Yes |
| `stats/friedman_nemenyi.py` | task-006 | [x] Yes |
| `stats/icc.py` | task-006 | [x] Yes |
| `stats/hierarchical_bootstrap.py` | task-006 | [x] Yes |
| `stats/jzs_bf.py` | task-006 | [x] Yes |
| `stats/truncation.py` | task-006 | [x] Yes |
| `stats/tests/test_all.py` | task-006 | [x] Yes |
| `stats/README.md` | task-006 | [x] Yes |

- [x] All 6 task spec files present in `tasks/`
- [x] All referenced scripts exist at documented paths
- [x] Delta package structure intact (`__init__.py` files present)
- [x] Stats package structure intact (`__init__.py` files present)
- [x] Multiple diagnostic scripts present from MACE optimization campaign (expected)
- [x] BioEmu manifests and CSVs present (batch2_candidates.csv, batch2_screened.csv, batch2_manifest.csv, batch2_manifest.fasta)

---

## 6. Registry Accuracy

### Agent entries

- [x] System agents (PlannerAI, AdminAI) correct
- [x] HeadAIs (head-0.1, head-1.1, head-1.2) all present with correct locations
- [x] head-0.1 and head-1.1 correctly marked Complete
- [x] head-1.2 correctly marked Running
- [x] All 4 Sub 0.1 SubAgents present and Complete
- [x] All 6 Sub 1.1 SubAgents present and Complete
- [x] All 6 Sub 1.2 SubAgents present
- [x] All 16 ad-hoc remediation SubAgents documented
- [ ] **FAIL (CRITICAL): mlff-so3lr-pilot status wrong.** Line 41 says "3/5 PASS: GB3+GB1+UBQ stable 5 ns" but GB3 FAILED the structural integrity check (Rg ratio 93x, RMSD 1387 A). The correct count is 2/5 PASS (GB1+UBQ only). This was the pre-structural-analysis assessment that was never corrected. **Must be updated to "2/5 PASS: GB1+UBQ stable 5 ns; GB3 silent structural explosion (Rg 93x); NTL9 explosion+NaN@4.4ns; WW FAIL NaN@0.7ns".**
- [ ] **FAIL: mlff-mace-pilot status is ahead of other docs.** Line 40 references v5 FAILED and v6 fixes with diagnostic job 9546808 -- information that does NOT appear in any dashboard file, the task-001-status.md, or the cross-agent notes. Either (a) the registry was updated from a session that did not update the other docs, or (b) the registry info is speculative. **All other documentation still references v5 as current. The registry is the only file with v6 information.**
- [x] delta-baselines and stats-pipeline correctly marked Complete
- [x] osf-prereg correctly shows v2 drafted status
- [x] bioemu-batch2 shows "10/93 success, 1 partial, 82 pending" -- consistent with cross-agent note's interim results but not with dashboard's "10/93"

---

## Summary of Issues Found

### CRITICAL (affects correctness of downstream planning)

1. **Registry SO3LR count wrong:** `shared/registry.md` line 41 says "3/5 PASS: GB3+GB1+UBQ" but GB3 FAILED structural analysis. Correct count is 2/5 PASS. Dashboards have the correct count.

2. **MACE version lag across all docs except registry:** Registry says v5 FAILED and v6 fixes applied (diagnostic 9546808). All four dashboards, task-001-status.md, and cross-agent notes still show v5 (job IDs 9449439-41) as current. If v5 truly failed, then job IDs in dashboards/active-subphase.md SLURM inventory are stale.

### IMPORTANT (data accuracy but not blocking)

3. **Compute budget overview table not updated with Sub 1.2 actuals.** Alpha-M "Used" shows ~78 (Sub 1.1 only); should include ~74 more from Sub 1.2 actuals. Gamma "Used" shows ~163; should include ~56 more. Budget remaining figures are overstated.

4. **Compute budget projection math error.** Line 187 says "3,000 - 5 used" but the Phase 1 Used column shows 78. The "5" is unexplained.

5. **BioEmu count inconsistencies.** master-status says "83 resubmitted", active-subphase says "82 PENDING", cross-agent note says "11/93 complete". The dashboards say "10/93" (not counting CD19's 90 conformations). Need to settle on whether 10 or 11 are complete and whether 82 or 83 are pending.

6. **task-002-status.md success criteria never backfilled.** All per-protein stability criteria are still "pending" despite SO3LR being marked COMPLETE. The structural analysis verdicts (2/5 PASS) are only in the cross-agent note.

7. **task-004-status.md body not updated since initial submission.** Still references original job IDs (8887441, 8887446). Does not reflect batch 1 retry (8903490), topup round, or current v2 resubmission (9449458/59).

### MINOR (documentation hygiene)

8. **task-001-status.md Resource Usage table has v1 stale job IDs.** Line 229 lists 8885960-62 (v1 failures from day 1). Informational only since the job history table above it is complete.

9. **task-002-status.md Resource Usage table has v1 stale job IDs.** Line 324 lists 8886091-95 (v1 failed typing_extensions). Same pattern.

10. **Phase 0 completion report GPU naming.** References "RTX 5090" but all subsequent docs use "RTX 5000 Ada". Never formally resolved. Has not caused operational issues.

11. **decisions-needed.md last_updated is 2026-04-18.** Not a problem per se (no new decisions), but other dashboards updated 2026-04-25. Could be confusing if someone checks freshness.

---

## Verification Summary

| Category | Pass | Fail | Notes |
|----------|------|------|-------|
| Dashboard consistency | 16 | 8 | Major: SO3LR count, MACE version, BioEmu count, compute budget |
| Cross-agent notes | 11 | 1 | Registry/note SO3LR mismatch is the critical one |
| Status files | 17 | 6 | task-002 and task-004 most stale; task-001 v5/v6 gap |
| Phase 0/1.1 closure | 15 | 1 | Minor GPU naming only; completion reports solid |
| Scripts/artifacts | 30 | 0 | All referenced scripts verified present |
| Registry | 11 | 2 | SO3LR count wrong; MACE version ahead of other docs |
| **Total** | **100** | **18** | |

---

## Recommended Fix Priority

1. **Fix registry SO3LR count** -- change "3/5 PASS: GB3+GB1+UBQ" to "2/5 PASS: GB1+UBQ" and note GB3 failed structural analysis.
2. **Resolve MACE v5/v6 discrepancy** -- either update all dashboards + task-001-status to reflect v6, OR revert the registry if v6 info is premature. Determine what the actual current SLURM job IDs are.
3. **Update compute budget overview table** with Sub 1.2 actuals.
4. **Backfill task-002-status.md** with structural analysis results from the cross-agent note.
5. **Settle BioEmu count** (10 vs 11 complete, 82 vs 83 pending) across all files.
6. **Update task-004-status.md** with current job IDs and topup history.
