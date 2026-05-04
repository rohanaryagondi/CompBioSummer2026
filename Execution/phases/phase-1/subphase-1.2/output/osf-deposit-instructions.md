# OSF Deposit Instructions (for the human user)

**Audience:** The human operator (amita4171@gmail.com).
**Purpose:** Step-by-step instructions for depositing `osf-prereg-final.md` publicly on OSF and returning the resulting DOI to the head-1.2 HeadAI so it can be recorded in `dashboards/master-status.md`.
**Hard deadline for deposit:** **2026-05-15 23:59 UTC** (per IP §7.2 and `shared/notes/1.2-scope-recommendations.md` item 1). A 1-day grace to 2026-05-16 is tolerated; >2 days slip requires PlannerAI replan.

This document assumes the osf-prereg SubAgent has produced `osf-prereg-final.md` (ready for deposit) by the internal target date 2026-05-13. If that date slips, notify head-1.2 immediately; do not wait past 2026-05-14.

---

## Prerequisites (complete these on or before 2026-05-13)

1. OSF account at https://osf.io (free, no institutional affiliation required). If you do not yet have one, register with your email (amita4171@gmail.com) and verify. Takes ~2 minutes.

2. A co-author list finalized. OSF requires at least one "Contributor" (can be just you) and allows adding co-authors at or after deposit time. You can deposit with only yourself as the contributor and add co-authors later as the manuscript is drafted — OSF pre-registrations do not lock the contributor list.

3. The file `osf-prereg-final.md` from `phases/phase-1/subphase-1.2/output/` ready to paste. If the SubAgent has not yet produced the `final` version, use `osf-prereg-v1.md` as interim; that is acceptable per the failure protocol in `tasks/task-003-osf-prereg.md` §Failure Protocol item 1.

4. Confirm your local clone of the repository is on the commit that matches the GitHub commit hash recorded in §12.3 of `osf-prereg-final.md`. If the SHA is not yet recorded, coordinate with head-1.2 to pin the SHA at time of deposit (the SubAgent will compute it).

---

## Deposit procedure

### Step 1 — Log in to OSF

1. Navigate to https://osf.io/dashboard
2. Sign in with your OSF account credentials.

### Step 2 — Create a new OSF Project

1. On the dashboard, click the green **"+ Create new project"** button (top right, or in the "Your Projects" section if you have existing projects).
2. Project name suggestion: **"CompBioSummer2026: MLFF Force Field + Dynamics-to-Fitness + Perturbation Benchmark Pre-Registration"** (feel free to shorten if OSF imposes a length limit — something like "CompBioSummer2026 Benchmark Pre-Registration" works).
3. Category: **Project**
4. Storage location: **United States** (default is fine).
5. Description (one-liner): *"Pre-registered analysis plan for three computational benchmark projects (Alpha-M, Gamma, Delta) and one conditional combined paper (Alpha-M + Gamma) on the Yale McCleary HPC cluster, covering protein roster, generators, observables, statistical tests, decision rules T1-T6/S1-S5, kill criteria AK/GK/CK/DK, and recalculated power analysis."*
6. Click **"Create project"**.

### Step 3 — Add the pre-registration document to the project's files

1. In the new project, navigate to the **"Files"** tab.
2. Click **"Upload"** and select `osf-prereg-final.md` (or `osf-prereg-v1.md` if final is not ready).
3. Also upload:
   - `phases/phase-0/subphase-0.1/proteins/manifest.json` (Appendix C data source)
   - The Python power-analysis script from Appendix B (copy the code block from `osf-prereg-final.md` §Appendix B into a standalone `appendix_b_power_analysis.py` file if needed — the SubAgent will have prepared this)
   - `shared/notes/1.1-methods-section-drafts.md` (D.1-D.4 caveat source)
4. Wait for uploads to complete.

### Step 4 — Create the Pre-Registration (the formal timestamp)

1. In the project, click the **"Registrations"** tab (may be labeled "Pre-registrations" depending on OSF's current UI).
2. Click **"+ New registration"** (green button, top right).
3. Select the registration template: **"OSF Standard Pre-Registration"** (this is the template with a narrative-style free-text field suitable for our markdown document; alternatives like "OSF Pre-Registration (Open-Ended)" also work).
4. On the registration form:
   - Title: inherits from the project; confirm.
   - **Study Information** section: paste §1 (Project Overview) from `osf-prereg-final.md`.
   - **Design Plan** section: paste §3-§5 (Protein Roster, Generator Roster, Observables).
   - **Sampling Plan** section: paste §10 (Power Analysis).
   - **Variables** section: paste §5 (Observables) — OK to reference this from Design Plan.
   - **Analysis Plan** section: paste §6-§8 (Statistical Tests, Decision Rules, Trajectory Truncation Protocol).
   - **Hypotheses** section: paste §2 (Hypotheses).
   - **Other** / **"Anything else?"** section: paste §9 (Kill Criteria), §11 (Pre-Registered Caveats), §12 (Compute and Software), §13 (Amendments Process).
   - Attachments: ensure `osf-prereg-final.md`, the Python script, the manifest JSON, and the methods-section drafts markdown are attached to the registration (OSF will have a step for this).

   **Alternative (simpler) — paste the entire markdown into a single free-text field.** If the OSF Standard template's section-by-section structure is inconvenient, OSF also offers an "OSF Pre-Registration (Open-Ended)" template with a single large free-text narrative field. Paste the full contents of `osf-prereg-final.md` into that field. Both templates produce a valid pre-registration with a DOI.

5. Review the preview. Pay particular attention to:
   - The verbatim D.1-D.4 caveat paragraphs (§11) render correctly (long paragraphs — make sure nothing is truncated).
   - The Appendix A Bayesian model code block renders as a fixed-width block, not collapsed.
   - All section headers (## 1 through ## 14) are visible.
   - The citation numbers in §14 are all present (expect 37 numbered citations).

6. **Before confirming:** note the target deposit date (2026-05-15). Once you click "Register", the timestamp is immutable.

7. Click **"Register"**, then **"Submit for registration"**. OSF then assigns a DOI (typically within 1-2 minutes — sometimes up to 24 hours if OSF is under load).

### Step 5 — Retrieve the DOI

1. After confirmation, return to the project page.
2. Under "Registrations", the new registration shows a DOI of the form `https://doi.org/10.17605/OSF.IO/XXXXX` (or similar).
3. **Copy the DOI URL in full** (starts with `https://doi.org/10.17605/` or `https://osf.io/...`).

### Step 6 — Return the DOI to head-1.2

Reply to head-1.2 (or paste into the HeadAI chat) with:

```
OSF deposit complete.
DOI: <paste URL here>
Deposit timestamp: <paste exact timestamp from OSF — format 2026-05-15T14:23:00Z>
```

The osf-prereg SubAgent will then:
1. Compute the SHA256 of the deposited markdown file locally.
2. Write `phases/phase-1/subphase-1.2/output/osf-deposited.md` with DOI + timestamp + SHA256.
3. Upgrade `shared/notes/1.2-osf-deposited.md` to urgency=critical with the DOI URL in the Finding section.
4. Request head-1.2 update `dashboards/master-status.md` decision-log with the DOI.

---

## Troubleshooting

### OSF site is down

1. Wait up to 48 hours (OSF outages rarely exceed this). Monitor https://osf.io for banner messages.
2. If OSF is unavailable for > 48 hours and the 2026-05-15 deadline is imminent: fall back to **Zenodo** (https://zenodo.org). Zenodo also issues DOIs and accepts markdown files. Use the "Pre-registration" or "Other" resource type. Document the fallback in the cross-agent note.
3. Deposit MUST happen by 2026-05-16 (1-day grace). Any later requires PlannerAI replan.

### DOI not issued within 24 hours

Contact OSF support via the "Support" link at the bottom of osf.io — they are responsive within 1 business day. Alternatively, the registration is typically visible at https://osf.io/registrations/ even before DOI assignment; copy the project URL temporarily and replace with the DOI once issued.

### File upload fails for a large attachment

The Python power-analysis script (Appendix B) and the manifest JSON are small (< 100 kB each). If `osf-prereg-final.md` itself is large, OSF's upload limit is 5 GB per file — this is not a concern. If upload persistently fails: paste the full contents into the registration narrative text field instead of attaching the file.

### You realize after submission that there is a typo or a missing section

This is a tracked amendment (see §13 of the pre-registration itself). After the deposit DOI is issued:
1. Create a new Pre-Registration on the same OSF project with the amended content.
2. In the amendment's narrative, explicitly state: *"Amendment to [original DOI]: [description of change, e.g., 'populate power-analysis table with task-006 validated numbers']."*
3. The amendment receives its own DOI, and both DOIs are cited in the manuscript.

**The original deposit is immutable.** Do not attempt to delete or modify it post-deposit.

### You want to add a co-author after deposit

OSF allows adding Contributors post-registration. Navigate to the project → Contributors → + Add. New contributors have read/write access but the registration timestamp is immutable.

---

## Post-deposit checklist (for the SubAgent, not the user)

- [ ] `output/osf-deposited.md` created with DOI + timestamp + SHA256
- [ ] `shared/notes/1.2-osf-deposited.md` upgraded from stub (urgency=info) to critical with DOI
- [ ] Request to head-1.2 to update `dashboards/master-status.md`
- [ ] Status report `status/task-003-status.md` updated to status=`complete`

---

## Notes

- **You do not need to notify any external party** (NatMeth, NCS, or a funding agency) of the OSF deposit. The OSF DOI is a public timestamp; it is cited in the manuscript and supplementary materials, not announced in advance.
- The OSF deposit covers BOTH the combined-paper and separation scenarios. Whichever decision is made at 2026-08-31 (D6), the manuscript cites the same OSF DOI.
- OSF deposits are NOT retracted after this policy. If a major issue is discovered post-deposit, amend; do not retract. Retraction (if ever performed) would be disclosed in the manuscript's Methods section and would trigger a PlannerAI replan.

---

*Document prepared by osf-prereg SubAgent, 2026-04-19. Contact head-1.2 with any questions before depositing.*
