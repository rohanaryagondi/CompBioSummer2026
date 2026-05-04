# Priority SU Tracker

Tracks Service Unit consumption on the `prio_mg269` priority account for CompBioSummer2026 project jobs on Yale McCleary HPC.

## Budget

- **Current budget:** 50 SU (set in `prio_su_budget.json`)
- **Warning threshold:** 80% (40 SU)
- **Hard limit:** 100% (50 SU) -- `prio_submit.sh` refuses to submit when over budget

To change the budget, edit `prio_su_budget.json`:
```json
{ "budget_su": 50.0, "warning_threshold": 0.80 }
```

## The q6 naming convention

All CompBioSummer2026 priority-queue jobs use names starting with `q6` followed by 6 random alphanumeric characters (e.g., `q6f8m3v2`). This lets the tracker distinguish our project jobs from other `prio_mg269` jobs on the same account.

Pre-q6 jobs (like the initial `d6v6fxwq` diagnostic) are tracked via the manual registry.

## Checking budget

```bash
./prio_su_tracker.sh
```

Exit codes:
- `0` -- WITHIN_BUDGET (used < 80%)
- `1` -- WARNING (used >= 80%)
- `2` -- OVER_BUDGET (used >= 100%)

Results are also written to `prio_su_status.json` for programmatic access.

## Submitting priority jobs

Always use the wrapper instead of raw `sbatch`:

```bash
./prio_submit.sh [sbatch args...] script.sbatch
```

The wrapper:
1. Checks budget before submitting (blocks if over budget)
2. Auto-generates a `q6XXXXXX` job name (unless you provide `--job-name=q6...`)
3. Forces `--account=prio_mg269 --qos=prio_mg269 --partition=priority_gpu`
4. Registers the job in `prio_su_registry.json`
5. Shows updated budget after submission

Example:
```bash
./prio_submit.sh --time=00:30:00 --gres=gpu:rtx_5000_ada:1 --mem=16G --cpus-per-task=2 my_diagnostic.sbatch
```

To add a purpose note (tracked in registry):
```bash
./prio_submit.sh --purpose="MACE NPT WW diagnostic v7" --time=00:30:00 my_script.sbatch
```

## Manually adding a job to the registry

If a job was submitted outside `prio_submit.sh` (e.g., pre-q6 jobs), add it to `prio_su_registry.json`:

```bash
jq '.jobs += [{"job_id": "1234567", "job_name": "d6v6fxwq", "submit_time": "2026-04-27T16:00:00Z", "purpose": "description", "status": "FAILED", "actual_su": 11.2, "notes": "Pre-q6 naming."}]' prio_su_registry.json > tmp.json && mv tmp.json prio_su_registry.json
```

The tracker checks both sacct (for q6* jobs) and the registry (for manually listed job IDs). If sacct has data for a registry job, sacct's calculated SU is used. If the job has aged out of sacct, the registry's `actual_su` is used as fallback.

## Files

| File | Purpose |
|------|---------|
| `prio_su_tracker.sh` | Budget checker -- queries sacct + registry, prints summary |
| `prio_submit.sh` | Safe sbatch wrapper with budget check + auto-naming + registry |
| `prio_su_budget.json` | Budget configuration (SU limit + warning threshold) |
| `prio_su_registry.json` | Job registry (all priority jobs, including pre-q6) |
| `prio_su_status.json` | Latest tracker output in JSON (written by tracker) |
