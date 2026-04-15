#!/bin/bash
# Weather Text Monitor - captures NAVTEX and logs text broadcasts
# Run periodically from crontab to capture text weather data
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

# For NAVTEX (518 kHz) - use RSP1B since RTL-SDRs can't tune that low
if [ "$FREQ" -lt 30000000 ]; then
    # Need to stop OpenWebRX and use RSP1B
    docker stop openwebrx > /dev/null 2>&1
    sleep 3
    /usr/local/bin/sdrplay_apiService &
    APIPID=$!
    sleep 3

    # Record with SoapySDR
    python3 /home/dragon/wxfax-record.py $FREQ $DURATION "$TMPWAV" 2>> $LOGFILE

    kill $APIPID 2>/dev/null
    wait $APIPID 2>/dev/null
    docker start openwebrx > /dev/null 2>&1
else
    # Use RTL-SDR (through OpenWebRX container)
    # For EAS on NOAA WX Radio, we can use rtl_fm
    DEVICE=1  # R820T
    timeout $DURATION rtl_fm -d $DEVICE -f $FREQ -M nfm -s 22050 -l 0 - 2>/dev/null | \
        sox -t raw -r 22050 -e signed -b 16 -c 1 - "$TMPWAV" 2>/dev/null
fi

# Decode based on type
if [ -f "$TMPWAV" ]; then
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
fi

# Trim log to last 500 entries
if [ -f "$LOGFILE" ]; then
    tail -5000 "$LOGFILE" > "${LOGFILE}.tmp"
    mv "${LOGFILE}.tmp" "$LOGFILE"
fi

# Regenerate dashboard
python3 /home/dragon/weather-dashboard.py 2>/dev/null
