#!/bin/bash
# Tahoe-100M download progress monitor
# Usage: bash ~/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/output/tahoe-progress.sh

TARGET="/nfs/roberts/scratch/pi_mg269/rag88/tahoe-100m"
PROGRESS_FILE="${TARGET}/.download_progress"
PID_FILE="${TARGET}/.download_pid"
EXPECTED_GB=429  # approximate total dataset size in GB

echo "=== Tahoe-100M Download Progress ==="
echo ""

# Check if process is still running
if [ -f "${PID_FILE}" ]; then
    PID=$(cat "${PID_FILE}")
    if ps -p "${PID}" > /dev/null 2>&1; then
        ELAPSED=$(ps -o etime= -p "${PID}" | xargs)
        echo "Status:   RUNNING (PID ${PID}, elapsed: ${ELAPSED})"
    else
        echo "Status:   STOPPED (PID ${PID} no longer running)"
    fi
else
    echo "Status:   NOT RUNNING (no PID file)"
fi
echo ""

# Current size
if [ -d "${TARGET}" ]; then
    BYTES=$(du -sb "${TARGET}" 2>/dev/null | cut -f1)
    GB=$(echo "scale=2; ${BYTES}/1073741824" | bc 2>/dev/null || echo "?")
    PCT=$(echo "scale=1; ${GB}*100/${EXPECTED_GB}" | bc 2>/dev/null || echo "?")

    PARQUET_FILES=$(find "${TARGET}" -type f -name '*.parquet' 2>/dev/null | wc -l)
    TOTAL_FILES=$(find "${TARGET}" -type f 2>/dev/null | wc -l)

    echo "Downloaded: ${GB} GB / ~${EXPECTED_GB} GB (${PCT}%)"
    echo "Files:      ${TOTAL_FILES} total (${PARQUET_FILES} parquet)"
else
    echo "Downloaded: 0 GB (directory not found)"
fi
echo ""

# Download speed from progress log (last 5 entries)
if [ -f "${PROGRESS_FILE}" ]; then
    LINES=$(wc -l < "${PROGRESS_FILE}")
    echo "Recent progress (sampled every 60s):"

    if [ "${LINES}" -ge 2 ]; then
        # Calculate speed from last two entries
        PREV=$(tail -2 "${PROGRESS_FILE}" | head -1)
        CURR=$(tail -1 "${PROGRESS_FILE}")

        PREV_BYTES=$(echo "${PREV}" | grep -oP 'bytes=\K[0-9]+')
        CURR_BYTES=$(echo "${CURR}" | grep -oP 'bytes=\K[0-9]+')
        PREV_TIME=$(echo "${PREV}" | cut -d' ' -f1)
        CURR_TIME=$(echo "${CURR}" | cut -d' ' -f1)

        if [ -n "${PREV_BYTES}" ] && [ -n "${CURR_BYTES}" ]; then
            DIFF_BYTES=$((CURR_BYTES - PREV_BYTES))
            DIFF_MB=$(echo "scale=1; ${DIFF_BYTES}/1048576" | bc 2>/dev/null || echo "?")
            SPEED_MBS=$(echo "scale=1; ${DIFF_BYTES}/1048576/60" | bc 2>/dev/null || echo "?")
            echo "  Latest interval: +${DIFF_MB} MB in 60s (${SPEED_MBS} MB/s)"

            # ETA
            REMAINING_BYTES=$((EXPECTED_GB * 1073741824 - CURR_BYTES))
            if [ "${DIFF_BYTES}" -gt 0 ] 2>/dev/null; then
                ETA_MIN=$(echo "scale=0; ${REMAINING_BYTES}/${DIFF_BYTES}" | bc 2>/dev/null || echo "?")
                ETA_HR=$(echo "scale=1; ${ETA_MIN}/60" | bc 2>/dev/null || echo "?")
                echo "  Est. remaining:  ~${ETA_HR} hours"
            fi
        fi
    fi

    echo ""
    echo "Last 5 samples:"
    tail -5 "${PROGRESS_FILE}" | while read -r line; do
        TS=$(echo "$line" | cut -d' ' -f1)
        BYTES_VAL=$(echo "$line" | grep -oP 'bytes=\K[0-9]+')
        FILES_VAL=$(echo "$line" | grep -oP 'parquet_files=\K[0-9]+')
        GB_VAL=$(echo "scale=2; ${BYTES_VAL}/1073741824" | bc 2>/dev/null || echo "?")
        echo "  ${TS}  ${GB_VAL} GB  (${FILES_VAL} parquet files)"
    done
else
    echo "No progress samples yet (monitor writes every 60s)"
fi

echo ""

# Check for completion marker
if [ -f "${TARGET}/.download_complete" ]; then
    echo "*** DOWNLOAD COMPLETE ***"
    cat "${TARGET}/.download_complete" | python3 -m json.tool 2>/dev/null || cat "${TARGET}/.download_complete"
fi

# Per-subset breakdown
echo ""
echo "Per-subset breakdown:"
for subset in gene_metadata drug_metadata cell_line_metadata sample_metadata obs_metadata expression_data pseudobulk_differential_expression; do
    SDIR="${TARGET}/${subset}"
    if [ -d "${SDIR}" ]; then
        SIZE=$(du -sh "${SDIR}" 2>/dev/null | cut -f1)
        FCOUNT=$(find "${SDIR}" -type f 2>/dev/null | wc -l)
        echo "  ${subset}: ${SIZE} (${FCOUNT} files)"
    else
        echo "  ${subset}: (not started)"
    fi
done
