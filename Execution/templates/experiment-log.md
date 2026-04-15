---
experiment_id: "<subphase>-<short-name>"
task_id: "task-<NNN>"
agent: "<agent-name>"
date: <ISO date>
slurm_job_ids: [<job IDs>]
status: running | complete | failed | cancelled
---

# Experiment Log: <Title>

## Setup

| Item | Value |
|------|-------|
| Conda environment | <env name> |
| Node type | <GPU node / CPU node> |
| GPU type | <H200 / RTX 5000 Ada / B200 / None> |
| GPU count | <N> |
| SLURM partition | <partition name> |
| Wall time requested | <HH:MM:SS> |
| Software versions | <key packages with exact versions> |

### Software Version Details

```
<Output of relevant version commands, e.g.:
python --version
pip show torch mace-torch openmm
conda list | grep -E "torch|cuda|openmm">
```

---

## Parameters

<All simulation, training, or analysis parameters. Enough to reproduce exactly.>

| Parameter | Value | Justification |
|-----------|-------|---------------|
| <param> | <value> | <why this value> |

---

## Commands

<Exact command-line invocations used. Include SLURM submission commands.>

```bash
# Environment activation
conda activate <env>

# Main command
<exact command>

# SLURM submission (if applicable)
sbatch <script.sh>
```

---

## Results

<Output metrics, measurements, or observations.>

| Metric | Value | Expected | Status |
|--------|-------|----------|--------|
| <metric> | <value> | <expected range> | pass/fail |

### Output Files

| File | Path | Size | MD5 |
|------|------|------|-----|
| <name> | <path> | <size> | <checksum> |

---

## Reproducibility

| Item | Value |
|------|-------|
| Random seed(s) | <seed values> |
| SLURM job ID(s) | <job IDs> |
| Node name(s) | <node names> |
| GPU index(es) | <GPU indices> |
| Start time | <ISO timestamp> |
| End time | <ISO timestamp> |
| Wall time used | <HH:MM:SS> |
| GPU-hours consumed | <hours> |

---

## Notes

<Any observations, warnings, or anomalies during the experiment.>
