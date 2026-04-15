#!/bin/bash
# Weather Fax Automatic Capture Script
# Usage: wxfax-capture.sh <freq_hz> <chart_name> <duration_sec>

FREQ=${1:-8682000}
CHART_NAME=${2:-"unknown_chart"}
DURATION=${3:-600}
OUTDIR="/home/dragon/weatherfax"
DATE=$(date -u +%Y%m%d)
TIME=$(date -u +%H%M)
BASENAME="${DATE}_${TIME}_${CHART_NAME}"
WAVFILE="${OUTDIR}/wav/${BASENAME}.wav"
IMGFILE="${OUTDIR}/images/${BASENAME}.png"
LOGFILE="${OUTDIR}/capture.log"

mkdir -p "${OUTDIR}/wav" "${OUTDIR}/images" "${OUTDIR}/latest"

echo "$(date -u) - Capturing ${CHART_NAME} on ${FREQ} Hz for ${DURATION}s" >> $LOGFILE

# Stop OpenWebRX to free the RSP1B
docker stop openwebrx >> $LOGFILE 2>&1
sleep 5

# Kill any lingering sdrplay API service
pkill -f sdrplay_apiService 2>/dev/null
sleep 2

# Start fresh SDRplay API on host
/opt/sdrplay_api/sdrplay_apiService &
APIPID=$!
sleep 5

# Verify device is found
if ! SoapySDRUtil --find="driver=sdrplay" 2>/dev/null | grep -q "sdrplay"; then
    echo "$(date -u) - ERROR: RSP1B not found, aborting" >> $LOGFILE
    kill $APIPID 2>/dev/null
    docker start openwebrx >> $LOGFILE 2>&1
    exit 1
fi

# Capture and demodulate using Python + SoapySDR
python3 /home/dragon/wxfax-record.py $FREQ $DURATION "$WAVFILE" >> $LOGFILE 2>&1
RESULT=$?

# Stop SDRplay API
kill $APIPID 2>/dev/null
wait $APIPID 2>/dev/null
sleep 2

# Restart OpenWebRX
docker start openwebrx >> $LOGFILE 2>&1

if [ $RESULT -ne 0 ] || [ ! -f "$WAVFILE" ]; then
    echo "$(date -u) - FAILED: No audio captured for ${CHART_NAME}" >> $LOGFILE
    exit 1
fi

echo "$(date -u) - Audio captured: $WAVFILE ($(du -h "$WAVFILE" | cut -f1))" >> $LOGFILE

# Decode fax image
python3 /home/dragon/wxfax-decode.py "$WAVFILE" "$IMGFILE" >> $LOGFILE 2>&1

if [ -f "$IMGFILE" ]; then
    cp "$IMGFILE" "${OUTDIR}/latest/${CHART_NAME}.png"
    echo "$(date -u) - Image decoded: $IMGFILE" >> $LOGFILE
else
    echo "$(date -u) - Decode failed, keeping WAV" >> $LOGFILE
fi

# Regenerate gallery
python3 /home/dragon/weather-dashboard.py >> $LOGFILE 2>&1

# Clean up old files (keep 7 days)
find "${OUTDIR}/wav" -name "*.wav" -mtime +7 -delete 2>/dev/null
find "${OUTDIR}/images" -name "*.png" -mtime +7 -delete 2>/dev/null

echo "$(date -u) - Complete: ${CHART_NAME}" >> $LOGFILE
