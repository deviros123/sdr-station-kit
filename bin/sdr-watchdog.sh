#!/bin/bash
# SDR Station Watchdog
# Checks health of all services and sends alerts
# Run every 5 minutes from crontab
# Logs to /home/dragon/watchdog.log

LOG="/home/dragon/watchdog.log"
ALERT_FILE="/home/dragon/.watchdog_alert"
STATUS_FILE="/home/dragon/station-status.json"
MAX_LOG_SIZE=500000  # 500KB

# Rotate log if too big
if [ -f "$LOG" ] && [ $(stat -c%s "$LOG" 2>/dev/null || echo 0) -gt $MAX_LOG_SIZE ]; then
    tail -200 "$LOG" > "${LOG}.tmp"
    mv "${LOG}.tmp" "$LOG"
fi

NOW=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
ISSUES=()

# Check OpenWebRX container
OWRX_STATUS=$(docker inspect openwebrx --format '{{.State.Status}}' 2>/dev/null || echo "missing")
OWRX_HEALTH=$(docker inspect openwebrx --format '{{.State.Health.Status}}' 2>/dev/null || echo "unknown")
if [ "$OWRX_STATUS" != "running" ]; then
    # Could be down for a scheduled capture -- check if a capture is running
    if pgrep -f "wxfax-capture\|weather-monitor\|sdr-weekly-scan" > /dev/null 2>&1; then
        OWRX_STATUS="capture-in-progress"
    else
        ISSUES+=("OpenWebRX container is $OWRX_STATUS")
        # Try to restart it
        docker start openwebrx >> $LOG 2>&1
        echo "$NOW - RESTART: OpenWebRX container was $OWRX_STATUS, restarted" >> $LOG
    fi
fi

# Check web interface responds
if [ "$OWRX_STATUS" = "running" ]; then
    HTTP_CODE=$(curl -s -m 10 -o /dev/null -w "%{http_code}" http://localhost:8073/ 2>/dev/null)
    if [ "$HTTP_CODE" != "200" ]; then
        ISSUES+=("OpenWebRX web interface returned HTTP $HTTP_CODE")
    fi
fi

# Check RTL-SDR dongles on USB
RTL_COUNT=$(lsusb | grep -c "0bda:2838" 2>/dev/null || echo 0)
if [ "$RTL_COUNT" -lt 2 ]; then
    ISSUES+=("Only $RTL_COUNT RTL-SDR dongles on USB (expected 2)")
fi

# Check RSP1B on USB
RSP_COUNT=$(lsusb | grep -c "1df7:3050" 2>/dev/null || echo 0)
if [ "$RSP_COUNT" -lt 1 ]; then
    ISSUES+=("RSP1B not found on USB")
fi

# Check disk space
DISK_USAGE=$(df / --output=pcent | tail -1 | tr -d ' %')
if [ "$DISK_USAGE" -gt 90 ]; then
    ISSUES+=("Disk usage at ${DISK_USAGE}%")
    # Emergency cleanup
    find /home/dragon/weatherfax/wav -name "*.wav" -mtime +3 -delete 2>/dev/null
    find /home/dragon/weatherfax/images -name "*.png" -mtime +14 -delete 2>/dev/null
    echo "$NOW - CLEANUP: Disk at ${DISK_USAGE}%, cleaned old files" >> $LOG
elif [ "$DISK_USAGE" -gt 80 ]; then
    ISSUES+=("Disk usage at ${DISK_USAGE}% (warning)")
fi

# Check memory
MEM_AVAIL=$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo)
if [ "$MEM_AVAIL" -lt 500 ]; then
    ISSUES+=("Low memory: ${MEM_AVAIL}MB available")
fi

# Check CPU temperature
if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
    CPU_TEMP=$(($(cat /sys/class/thermal/thermal_zone0/temp) / 1000))
    if [ "$CPU_TEMP" -gt 80 ]; then
        ISSUES+=("CPU temperature: ${CPU_TEMP}C (throttling likely)")
    fi
else
    CPU_TEMP="N/A"
fi

# Check last capture success
LAST_CAPTURE_LOG="/home/dragon/weatherfax/capture.log"
if [ -f "$LAST_CAPTURE_LOG" ]; then
    LAST_FAIL=$(grep -c "FAILED" "$LAST_CAPTURE_LOG" 2>/dev/null || echo 0)
    LAST_SUCCESS=$(grep -c "Complete:" "$LAST_CAPTURE_LOG" 2>/dev/null || echo 0)
    if [ "$LAST_FAIL" -gt 0 ] && [ "$LAST_SUCCESS" -eq 0 ]; then
        ISSUES+=("All recent weather fax captures have failed")
    fi
fi

# Check bookmarks page exists in container
if [ "$OWRX_STATUS" = "running" ]; then
    BK_EXISTS=$(docker exec openwebrx ls /usr/lib/python3/dist-packages/htdocs/seattle-bookmarks.html 2>/dev/null && echo "yes" || echo "no")
    if [ "$BK_EXISTS" = "no" ]; then
        # Re-inject it
        docker cp /home/dragon/openwebrx-config/seattle-bookmarks.html openwebrx:/usr/lib/python3/dist-packages/htdocs/seattle-bookmarks.html 2>/dev/null
        echo "$NOW - FIX: Re-injected bookmarks page" >> $LOG
    fi
fi

# Write status JSON
cat > "$STATUS_FILE" << STATUSEOF
{
    "timestamp": "$NOW",
    "openwebrx": "$OWRX_STATUS",
    "openwebrx_health": "$OWRX_HEALTH",
    "rtlsdr_count": $RTL_COUNT,
    "rsp1b_present": $([ "$RSP_COUNT" -gt 0 ] && echo true || echo false),
    "disk_percent": $DISK_USAGE,
    "memory_avail_mb": $MEM_AVAIL,
    "cpu_temp_c": "$CPU_TEMP",
    "issues": $( [ ${#ISSUES[@]} -eq 0 ] && echo '[]' || printf '["%s"]' "$(IFS='","'; echo "${ISSUES[*]}")" ),
    "issue_count": ${#ISSUES[@]}
}
STATUSEOF

# Log issues
if [ ${#ISSUES[@]} -gt 0 ]; then
    echo "$NOW - ISSUES (${#ISSUES[@]}):" >> $LOG
    for issue in "${ISSUES[@]}"; do
        echo "  - $issue" >> $LOG
    done
else
    # Only log OK every hour to reduce noise
    MINUTE=$(date +%M)
    if [ "$MINUTE" -lt 5 ]; then
        echo "$NOW - OK: All systems healthy (disk:${DISK_USAGE}% mem:${MEM_AVAIL}MB cpu:${CPU_TEMP}C rtl:${RTL_COUNT} rsp:${RSP_COUNT})" >> $LOG
    fi
fi
