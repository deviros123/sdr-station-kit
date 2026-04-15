#!/bin/bash
# Weather Text Monitor - captures NAVTEX and logs text broadcasts
# Usage: weather-monitor.sh <type> <freq_hz> <duration_sec>

TYPE=${1:-navtex}
FREQ=${2:-518000}
DURATION=${3:-300}
TEXTDIR="/home/dragon/weather-text"
LOGFILE="${TEXTDIR}/${TYPE}.log"
TMPWAV="${TEXTDIR}/tmp_${TYPE}.wav"

mkdir -p "$TEXTDIR"

echo "---" >> $LOGFILE
echo "$(date -u +%Y-%m-%d\ %H:%M:%S\ UTC) - Monitoring ${TYPE} on ${FREQ} Hz" >> $LOGFILE

if [ "$FREQ" -lt 30000000 ]; then
    # HF frequency - need RSP1B via host SoapySDR
    # Must stop OpenWebRX container (it holds sdrplay_apiService)
    docker stop openwebrx >> $LOGFILE 2>&1
    sleep 5

    # Kill any lingering sdrplay API service
    pkill -f sdrplay_apiService 2>/dev/null
    sleep 2

    # Start fresh API service on host
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

    # Record audio
    python3 /home/dragon/wxfax-record.py $FREQ $DURATION "$TMPWAV" 2>> $LOGFILE

    # Clean up
    kill $APIPID 2>/dev/null
    wait $APIPID 2>/dev/null
    sleep 2
    docker start openwebrx >> $LOGFILE 2>&1
else
    # VHF/UHF - use RTL-SDR directly (no need to stop OpenWebRX)
    # OpenWebRX may have the device, so use rtl_fm with a free device
    DEVICE=1
    timeout $DURATION rtl_fm -d $DEVICE -f $FREQ -M nfm -s 22050 -l 0 - 2>/dev/null | \
        sox -t raw -r 22050 -e signed -b 16 -c 1 - "$TMPWAV" 2>/dev/null
fi

# Decode based on type
if [ -f "$TMPWAV" ] && [ -s "$TMPWAV" ]; then
    case $TYPE in
        navtex)
            multimon-ng -t wav -a SITOR-B "$TMPWAV" 2>/dev/null | \
                grep -v "^$" >> $LOGFILE
            ;;
        eas)
            multimon-ng -t wav -a EAS "$TMPWAV" 2>/dev/null | \
                grep -v "^$" >> $LOGFILE
            ;;
    esac
    rm -f "$TMPWAV"
else
    echo "$(date -u) - No audio captured" >> $LOGFILE
fi

# Trim log
if [ -f "$LOGFILE" ]; then
    tail -5000 "$LOGFILE" > "${LOGFILE}.tmp"
    mv "${LOGFILE}.tmp" "$LOGFILE"
fi

# Regenerate dashboard
python3 /home/dragon/weather-dashboard.py 2>/dev/null
