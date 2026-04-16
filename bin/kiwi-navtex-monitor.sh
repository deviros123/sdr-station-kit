#!/bin/bash
# KiwiSDR NAVTEX Monitor
# Connects to KiwiSDR, decodes NAVTEX text on 518 kHz
# Usage: kiwi-navtex-monitor.sh <duration_sec>

DURATION=${1:-600}
KIWI_HOST=${KIWI_HOST:-"localhost"}
KIWI_PORT=${KIWI_PORT:-8073}
TEXTDIR="/home/dragon/weather-text"
LOGFILE="${TEXTDIR}/navtex.log"
TMPFILE="${TEXTDIR}/tmp_navtex_kiwi.txt"

mkdir -p "$TEXTDIR"

echo "---" >> $LOGFILE
echo "$(date -u +%Y-%m-%d\ %H:%M:%S\ UTC) - KiwiSDR NAVTEX monitoring 518 kHz" >> $LOGFILE

# Use kiwirecorder to capture NAVTEX
# NAVTEX is SITOR-B on 518 kHz
kiwirecorder \
    --host "$KIWI_HOST" --port "$KIWI_PORT" \
    --frequency 518 --modulation usb \
    --tlimit "$DURATION" \
    --filename "navtex_capture" \
    --dir "$TEXTDIR" \
    >> $LOGFILE 2>&1

# If a WAV was produced, decode with multimon-ng
WAVFILE=$(ls -t "${TEXTDIR}/navtex_capture"*.wav 2>/dev/null | head -1)
if [ -n "$WAVFILE" ] && [ -f "$WAVFILE" ]; then
    multimon-ng -t wav -a SITOR-B "$WAVFILE" 2>/dev/null | grep -v "^$" >> $LOGFILE
    rm -f "$WAVFILE"
fi

# Trim log
if [ -f "$LOGFILE" ]; then
    tail -5000 "$LOGFILE" > "${LOGFILE}.tmp"
    mv "${LOGFILE}.tmp" "$LOGFILE"
fi

# Regenerate dashboard
python3 /home/dragon/weather-dashboard.py 2>/dev/null
