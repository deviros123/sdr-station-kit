#!/bin/bash
# KiwiSDR Weather Fax Capture
# Connects to local KiwiSDR, decodes fax, saves PNG
# Usage: kiwi-fax-capture.sh <freq_khz> <chart_name> <duration_sec>
# No OpenWebRX downtime! KiwiSDR runs independently.

FREQ=${1:-8682}
CHART_NAME=${2:-"unknown_chart"}
DURATION=${3:-720}
KIWI_HOST=${KIWI_HOST:-"localhost"}
KIWI_PORT=${KIWI_PORT:-8073}
OUTDIR="/home/dragon/weatherfax"
DATE=$(date -u +%Y%m%d)
TIME=$(date -u +%H%M)
BASENAME="${DATE}_${TIME}_${CHART_NAME}"
LOGFILE="${OUTDIR}/capture.log"

mkdir -p "${OUTDIR}/images" "${OUTDIR}/latest"

echo "$(date -u) - KiwiSDR capture: ${CHART_NAME} on ${FREQ} kHz for ${DURATION}s" >> $LOGFILE

# Capture fax using kiwirecorder
kiwirecorder \
    --host "$KIWI_HOST" --port "$KIWI_PORT" \
    --frequency "$FREQ" --modulation usb \
    --extension fax \
    --tlimit "$DURATION" \
    --filename "${BASENAME}" \
    --dir "${OUTDIR}/images" \
    >> $LOGFILE 2>&1

RESULT=$?

# Find the output file (kiwirecorder may append timestamp)
OUTFILE=$(ls -t "${OUTDIR}/images/${BASENAME}"*.png 2>/dev/null | head -1)

if [ $RESULT -eq 0 ] && [ -n "$OUTFILE" ] && [ -f "$OUTFILE" ]; then
    # Copy to latest
    cp "$OUTFILE" "${OUTDIR}/latest/${CHART_NAME}.png"
    echo "$(date -u) - SUCCESS: ${CHART_NAME} -> $(basename $OUTFILE)" >> $LOGFILE
else
    echo "$(date -u) - FAILED: ${CHART_NAME} (exit=$RESULT)" >> $LOGFILE
fi

# Regenerate dashboard
python3 /home/dragon/weather-dashboard.py 2>/dev/null

# Clean up old files (keep 7 days)
find "${OUTDIR}/images" -name "*.png" -mtime +7 -delete 2>/dev/null

echo "$(date -u) - Complete: ${CHART_NAME}" >> $LOGFILE
