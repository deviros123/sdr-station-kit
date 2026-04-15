#!/usr/bin/env python3
"""Analyze RTL-SDR and SoapySDR power scan data and update bookmarks."""

import csv
import json
import os
import glob
from datetime import datetime

SCANDIR = "/tmp/sdr-scans"
BOOKMARKS = "/home/dragon/openwebrx-config/bookmarks.d/seattle.json"

def load_scan_data():
    """Load all CSV scan files (rtl_power and soapy_power format)."""
    scans = {}
    for csvfile in glob.glob(os.path.join(SCANDIR, "*.csv")):
        try:
            with open(csvfile) as f:
                for row in csv.reader(f):
                    if len(row) < 7:
                        continue
                    try:
                        # Both rtl_power and soapy_power use same CSV format:
                        # date, time, freq_low, freq_high, freq_step, num_samples, db, db, db...
                        freq_low = int(float(row[2]))
                        freq_step = float(row[4])
                        powers = [float(x) for x in row[6:]]
                        for i, pwr in enumerate(powers):
                            freq = freq_low + int(i * freq_step)
                            if freq not in scans or pwr > scans[freq]:
                                scans[freq] = pwr
                    except (ValueError, IndexError):
                        pass
        except Exception as e:
            print("Error reading {}: {}".format(csvfile, e))
    return scans

def calculate_threshold(scans, band_ranges=None):
    """Calculate activity threshold. Use per-band noise floor for better accuracy."""
    if not scans:
        return -20

    # Global threshold as fallback
    all_powers = sorted(scans.values())
    global_median = all_powers[len(all_powers) // 2]
    return global_median + 10

def find_signal_power(freq, scans, tolerance=None):
    """Find the strongest signal power near a given frequency."""
    # Use wider tolerance for HF (signals are broader) and narrow for VHF/UHF
    if tolerance is None:
        if freq < 30000000:  # HF
            tolerance = 5000  # 5 kHz
        elif freq < 300000000:  # VHF
            tolerance = 25000  # 25 kHz
        else:  # UHF+
            tolerance = 15000  # 15 kHz

    best = -999
    for sf in scans:
        if abs(sf - freq) < tolerance:
            if scans[sf] > best:
                best = scans[sf]
    return best if best > -999 else None

def main():
    timestamp = datetime.now().isoformat()
    print("{} - Loading scan data...".format(timestamp))
    scans = load_scan_data()
    if not scans:
        print("ERROR: No scan data found in {}".format(SCANDIR))
        return

    # Separate HF and VHF/UHF scans for different thresholds
    hf_scans = {f: p for f, p in scans.items() if f < 30000000}
    vhf_scans = {f: p for f, p in scans.items() if f >= 30000000}

    if hf_scans:
        hf_powers = sorted(hf_scans.values())
        hf_threshold = hf_powers[len(hf_powers) // 2] + 10
        print("HF scan: {} bins, threshold {:.1f} dB".format(len(hf_scans), hf_threshold))
    else:
        hf_threshold = -20
        print("HF scan: no data")

    if vhf_scans:
        vhf_powers = sorted(vhf_scans.values())
        vhf_threshold = vhf_powers[len(vhf_powers) // 2] + 10
        print("VHF/UHF scan: {} bins, threshold {:.1f} dB".format(len(vhf_scans), vhf_threshold))
    else:
        vhf_threshold = -20
        print("VHF/UHF scan: no data")

    print("Total: {} frequency bins".format(len(scans)))

    # Load bookmarks
    with open(BOOKMARKS) as f:
        bookmarks = json.load(f)
    print("Loaded {} bookmarks".format(len(bookmarks)))

    # Analyze each bookmark
    active = 0
    inactive = 0
    no_data = 0
    newly_active = []
    newly_inactive = []

    for b in bookmarks:
        name = b["name"]
        was_active = name.startswith("* ")
        clean_name = name.lstrip("* ")
        freq = b["frequency"]

        # Choose threshold based on frequency
        threshold = hf_threshold if freq < 30000000 else vhf_threshold

        power = find_signal_power(freq, scans)
        if power is None:
            b["name"] = clean_name
            no_data += 1
        elif power >= threshold:
            b["name"] = "* " + clean_name
            active += 1
            if not was_active:
                newly_active.append((clean_name, freq, power))
        else:
            b["name"] = clean_name
            inactive += 1
            if was_active:
                newly_inactive.append((clean_name, freq, power))

    # Save updated bookmarks
    with open(BOOKMARKS, "w") as f:
        json.dump(bookmarks, f, indent=4)

    # Report
    print("\n=== Scan Results ===")
    print("  Active:   {}".format(active))
    print("  Inactive: {}".format(inactive))
    print("  No data:  {}".format(no_data))

    if newly_active:
        print("\n  NEW active since last scan:")
        for name, freq, pwr in sorted(newly_active, key=lambda x: -x[2])[:30]:
            print("    + {} ({:.4f} MHz, {:.1f} dB)".format(name, freq/1e6, pwr))
        if len(newly_active) > 30:
            print("    ... and {} more".format(len(newly_active) - 30))

    if newly_inactive:
        print("\n  Went INACTIVE since last scan:")
        for name, freq, pwr in sorted(newly_inactive, key=lambda x: x[2])[:30]:
            print("    - {} ({:.4f} MHz, {:.1f} dB)".format(name, freq/1e6, pwr))
        if len(newly_inactive) > 30:
            print("    ... and {} more".format(len(newly_inactive) - 30))

    # Save scan report
    report = {
        "scan_date": timestamp,
        "total_bins": len(scans),
        "hf_bins": len(hf_scans),
        "vhf_uhf_bins": len(vhf_scans),
        "hf_threshold_db": round(hf_threshold, 1),
        "vhf_threshold_db": round(vhf_threshold, 1),
        "active": active,
        "inactive": inactive,
        "no_data": no_data,
        "newly_active": len(newly_active),
        "newly_inactive": len(newly_inactive)
    }
    with open("/home/dragon/sdr-scan-report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\nReport saved to /home/dragon/sdr-scan-report.json")

if __name__ == "__main__":
    main()
