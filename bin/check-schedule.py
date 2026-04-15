#!/usr/bin/env python3
"""Check crontab for RSP1B task conflicts."""
import subprocess
import re

result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
lines = result.stdout.strip().split("\n")

tasks = []
for line in lines:
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    # Parse crontab: min hour * * * command
    parts = line.split()
    if len(parts) < 6:
        continue

    minute_field = parts[0]
    hour_field = parts[1]
    command = " ".join(parts[5:])

    # Skip non-RSP1B tasks
    if "weather-dashboard" in command:
        continue
    if "eas 162550000" in command:
        continue  # EAS uses RTL-SDR

    # Handle */15 style
    if "/" in minute_field or "/" in hour_field:
        continue
    # Handle 5,35 style
    if "," in minute_field:
        continue

    try:
        m = int(minute_field)
        h = int(hour_field)
    except ValueError:
        continue

    # Determine duration from command
    if "wxfax-capture" in command:
        # Extract duration from args
        match = re.search(r'(\d+)$', command)
        dur = int(match.group(1)) if match else 600
    elif "weather-monitor" in command:
        match = re.search(r'(\d+)$', command)
        dur = int(match.group(1)) if match else 600
    elif "sdr-weekly-scan" in command:
        dur = 1800  # ~30 min
    else:
        dur = 600

    name = command.split("/")[-1].split(".sh")[0]
    if "wxfax-capture" in command:
        parts2 = command.split()
        name = parts2[-2] if len(parts2) >= 3 else name
    elif "weather-monitor" in command:
        parts2 = command.split()
        name = parts2[-3] if len(parts2) >= 4 else name

    start_min = h * 60 + m
    tasks.append((start_min, dur, name))

tasks.sort()
OVERHEAD = 2

conflicts = 0
print("Schedule check: %d RSP1B tasks" % len(tasks))
for i in range(len(tasks) - 1):
    s1, d1, n1 = tasks[i]
    e1 = s1 + d1 // 60 + OVERHEAD
    s2, _, n2 = tasks[i + 1]
    gap = s2 - e1
    if gap < 0:
        print("  CONFLICT: %s (%02d:%02d-%02d:%02d) overlaps %s (%02d:%02d) by %d min" % (
            n1, s1//60, s1%60, e1//60%24, e1%60, n2, s2//60, s2%60, -gap))
        conflicts += 1

if conflicts:
    print("WARNING: %d schedule conflicts detected!" % conflicts)
else:
    print("OK: No conflicts found")
