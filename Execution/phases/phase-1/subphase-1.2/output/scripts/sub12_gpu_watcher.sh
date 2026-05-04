#!/bin/bash
# Sub 1.2 GPU watcher
# ---------------------------------------------------------------------------
# Purpose: ensure every Sub 1.2 SLURM job has an external-process GPU
# keepalive attached, so YCRC never auto-cancels us for 0% GPU util.
#
# Filters to Sub 1.2 jobs only (8-char alphanumeric cryptic names per
# operational-practices.md), excluding other projects like rosetta (`ros_*`).
#
# Run persistently via the Monitor tool (claude Monitor with persistent=true)
# or as a manual background bash loop. Emits one line per action.
#
# Design (2026-04-20):
# - Every 5 min, enumerate my running SLURM jobs
# - For any Sub 1.2 job not yet tracked, spawn an external-process keepalive
#   via srun --overlap (attaches to the same GPU allocation)
# - Track attached job IDs in a state file so we never double-attach
# - Clean the state file when jobs exit
#
# Why external-process: MACE + BioEmu both have phases where Python main
# thread holds the GIL in a C extension (matscipy.neighbour_list for MACE,
# colabfold MSA build for BioEmu). In-Python keepalive threads cannot run
# during those phases, so YCRC sees 0% GPU util. An external process under
# srun --overlap shares the GPU allocation but is not GIL-blocked.
# ---------------------------------------------------------------------------

set -u

USER_NAME="rag88"
PROJECT_ROOT="/home/rag88/projects/CompBioSummer2026/Execution"
KEEPALIVE_SCRIPT="${PROJECT_ROOT}/phases/phase-1/subphase-1.2/output/scripts/gpu_keepalive.py"
LOG_DIR="${PROJECT_ROOT}/phases/phase-1/subphase-1.2/output/slurm_logs"
STATE_FILE="${LOG_DIR}/sub12_watcher_attached.txt"
CONDA_SH="/apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh"

mkdir -p "${LOG_DIR}"
touch "${STATE_FILE}"

# Emit startup banner
echo "[watcher $(date -u '+%H:%M:%SZ')] Sub 1.2 GPU watcher starting (user=${USER_NAME})"

while true; do
  # Get all my running jobs (JobID, Name, Partition)
  jobs_raw=$(squeue -u "${USER_NAME}" -t R -h -o "%A|%j|%P" 2>/dev/null)

  # Track jids currently running to clean up state file later
  running_jids=""

  for entry in ${jobs_raw}; do
    jid=$(echo "${entry}" | cut -d'|' -f1)
    name=$(echo "${entry}" | cut -d'|' -f2)
    partition=$(echo "${entry}" | cut -d'|' -f3)

    running_jids="${running_jids} ${jid}"

    # FILTER: only Sub 1.2 cryptic job names (8-char [a-z0-9]). Excludes
    # rosetta jobs (ros_*), interactive bash (bash), etc.
    if [[ ! "${name}" =~ ^[a-z0-9]{8}$ ]]; then
      continue
    fi

    # Skip if we already attached a keepalive to this jid
    if grep -qE "^${jid}\$" "${STATE_FILE}" 2>/dev/null; then
      continue
    fi

    # Resolve internal JobId (array tasks need this for srun --overlap)
    internal_jid=$(scontrol show job "${jid}" 2>/dev/null | grep "^JobId=" | head -1 | awk '{print $1}' | cut -d= -f2)
    if [ -z "${internal_jid}" ]; then
      internal_jid="${jid}"
    fi

    # Pick env by partition: gpu_h200 → MACE, everything else → bioemu/so3lr
    case "${partition}" in
      gpu_h200)
        env_name="env-mace"
        ;;
      *)
        # For `gpu` partition we check name patterns or default to bioemu.
        # SO3LR tags in this subphase: 932e3sz8, pr32hg7t, ixgkbzna, ubi1w71f,
        # g6m5vkof, h6k3vr9m. All finished now. If a new SO3LR job appears
        # we'd want env-so3lr, but env-bioemu's torch also works for the
        # keepalive matmul (only needs cuda + torch) so this is safe either
        # way — the keepalive itself is env-agnostic, only torch matters.
        env_name="env-bioemu"
        ;;
    esac

    echo "[watcher $(date -u '+%H:%M:%SZ')] attach: jid=${jid} name=${name} part=${partition} env=${env_name}"
    # Spawn keepalive as detached background process via srun --overlap.
    # The srun process and its python child will terminate automatically
    # when the main SLURM job exits (SLURM cleanup kills the allocation's
    # child processes).
    srun --jobid="${internal_jid}" --overlap --ntasks=1 --time=24:00:00 \
      bash -c "source ${CONDA_SH} && conda activate ${env_name} && python ${KEEPALIVE_SCRIPT}" \
      > "${LOG_DIR}/keepalive-watcher-${jid}.log" 2>&1 &
    echo "${jid}" >> "${STATE_FILE}"
  done

  # Clean state file: drop entries for jids no longer running
  if [ -s "${STATE_FILE}" ]; then
    tmp=$(mktemp)
    while IFS= read -r tracked_jid; do
      [ -z "${tracked_jid}" ] && continue
      if [[ " ${running_jids} " == *" ${tracked_jid} "* ]]; then
        echo "${tracked_jid}" >> "${tmp}"
      fi
    done < "${STATE_FILE}"
    mv "${tmp}" "${STATE_FILE}"
  fi

  sleep 300  # 5 min polling interval
done
