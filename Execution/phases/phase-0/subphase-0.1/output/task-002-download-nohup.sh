#!/bin/bash
# Tahoe-100M download — runs on login node via nohup
# Usage: nohup bash task-002-download-nohup.sh &

set -euo pipefail

TARGET_DIR="/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m"
LOG_DIR="/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/output"
PROGRESS_FILE="${TARGET_DIR}/.download_progress"

echo "========================================" | tee -a "${LOG_DIR}/task-002-download-nohup.log"
echo "Tahoe-100M Download (login node)" | tee -a "${LOG_DIR}/task-002-download-nohup.log"
echo "  PID:   $$" | tee -a "${LOG_DIR}/task-002-download-nohup.log"
echo "  Node:  $(hostname)" | tee -a "${LOG_DIR}/task-002-download-nohup.log"
echo "  Start: $(date -u '+%Y-%m-%dT%H:%M:%SZ')" | tee -a "${LOG_DIR}/task-002-download-nohup.log"
echo "========================================" | tee -a "${LOG_DIR}/task-002-download-nohup.log"

# Write PID for monitoring
echo $$ > "${TARGET_DIR}/.download_pid"

# Activate environment
source /apps/software/system/software/miniconda/24.11.3/etc/profile.d/conda.sh
conda activate env-tahoe-download

# Enable hf_transfer for faster downloads
export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_HOME="${TARGET_DIR}/.hf_cache"
mkdir -p "${HF_HOME}"

# Start a background progress monitor that writes stats every 60 seconds
(
  while true; do
    sleep 60
    if [ -d "${TARGET_DIR}" ]; then
      BYTES=$(du -sb "${TARGET_DIR}" 2>/dev/null | cut -f1 || echo 0)
      FILES=$(find "${TARGET_DIR}" -type f -name '*.parquet' 2>/dev/null | wc -l || echo 0)
      TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
      echo "${TIMESTAMP} bytes=${BYTES} parquet_files=${FILES}" >> "${PROGRESS_FILE}"
    fi
  done
) &
MONITOR_PID=$!

# Run the download
python "${LOG_DIR}/task-002-download-script.py" 2>&1 | tee -a "${LOG_DIR}/task-002-download-nohup.log"
EXIT_CODE=${PIPESTATUS[0]}

# Kill the monitor
kill ${MONITOR_PID} 2>/dev/null || true

echo "" | tee -a "${LOG_DIR}/task-002-download-nohup.log"
echo "========================================" | tee -a "${LOG_DIR}/task-002-download-nohup.log"
echo "Download finished (exit code: ${EXIT_CODE})" | tee -a "${LOG_DIR}/task-002-download-nohup.log"
echo "  End: $(date -u '+%Y-%m-%dT%H:%M:%SZ')" | tee -a "${LOG_DIR}/task-002-download-nohup.log"
du -sh "${TARGET_DIR}" 2>/dev/null | tee -a "${LOG_DIR}/task-002-download-nohup.log"
echo "========================================" | tee -a "${LOG_DIR}/task-002-download-nohup.log"

# Clean up PID file
rm -f "${TARGET_DIR}/.download_pid"

exit ${EXIT_CODE}
