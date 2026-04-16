#!/bin/bash
# SDR Station Benchmark Script
# Runs specific tests based on todo item ID
# Usage: sdr-benchmark.sh <todo_id> [label]
# Results saved to /home/dragon/benchmarks/

TODO_ID=${1:-"all"}
LABEL=${2:-$(date -u +%Y%m%d_%H%M)}
BENCHDIR="/home/dragon/benchmarks"
RESULTFILE="${BENCHDIR}/${TODO_ID}_${LABEL}.json"

mkdir -p "$BENCHDIR"

run_power_scan() {
    local device=$1 freq_range=$2 step=$3 duration=$4 outfile=$5
    timeout $duration rtl_power -d $device -f $freq_range -g 30 -i 5 -e $((duration-5)) "$outfile" 2>/dev/null
}

analyze_scan() {
    local csvfile=$1
    python3 -c "
import csv, json, sys
scans = {}
with open('$csvfile') as f:
    for row in csv.reader(f):
        if len(row) < 7: continue
        try:
            fl = int(float(row[2]))
            fs = float(row[4])
            for i, p in enumerate([float(x) for x in row[6:]]):
                freq = fl + int(i * fs)
                if freq not in scans or p > scans[freq]: scans[freq] = p
        except: pass
if not scans:
    print(json.dumps({'error': 'no data'}))
    sys.exit(1)
powers = sorted(scans.values())
noise = powers[len(powers)//2]
peak = powers[-1]
above_noise = sum(1 for p in powers if p > noise + 10)
print(json.dumps({
    'bins': len(scans),
    'noise_floor_db': round(noise, 1),
    'peak_db': round(peak, 1),
    'snr_db': round(peak - noise, 1),
    'active_signals': above_noise,
    'freq_low': min(scans.keys()),
    'freq_high': max(scans.keys())
}))
"
}

case "$TODO_ID" in
    rg6_tram|discone_outdoor|lna_adsb)
        # Test VHF/UHF signal quality on E4000 and R820T
        echo "Testing VHF/UHF signal quality..."
        TMPCSV="/tmp/bench_vhf.csv"

        # ADS-B signal strength
        echo "  ADS-B 1090 MHz..."
        run_power_scan 1 "1085M:1095M:25k" 25k 15 "$TMPCSV"
        ADSB=$(analyze_scan "$TMPCSV")
        rm -f "$TMPCSV"

        # P25 800 MHz
        echo "  P25 800 MHz..."
        run_power_scan 1 "849M:870M:12.5k" 12.5k 15 "$TMPCSV"
        P25=$(analyze_scan "$TMPCSV")
        rm -f "$TMPCSV"

        # Aviation
        echo "  Aviation 118-137 MHz..."
        run_power_scan 0 "118M:137M:25k" 25k 15 "$TMPCSV"
        AIR=$(analyze_scan "$TMPCSV")
        rm -f "$TMPCSV"

        # FM broadcast
        echo "  FM broadcast..."
        run_power_scan 0 "88M:108M:25k" 25k 15 "$TMPCSV"
        FM=$(analyze_scan "$TMPCSV")
        rm -f "$TMPCSV"

        # Marine VHF
        echo "  Marine VHF..."
        run_power_scan 1 "155M:163M:12.5k" 12.5k 15 "$TMPCSV"
        MARINE=$(analyze_scan "$TMPCSV")
        rm -f "$TMPCSV"

        # 70cm amateur
        echo "  70cm amateur..."
        run_power_scan 1 "440M:450M:12.5k" 12.5k 15 "$TMPCSV"
        SEVENTY=$(analyze_scan "$TMPCSV")
        rm -f "$TMPCSV"

        python3 -c "
import json
result = {
    'todo_id': '$TODO_ID',
    'label': '$LABEL',
    'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
    'tests': {
        'adsb_1090': $ADSB,
        'p25_800': $P25,
        'aviation': $AIR,
        'fm_broadcast': $FM,
        'marine_vhf': $MARINE,
        'amateur_70cm': $SEVENTY
    }
}
with open('$RESULTFILE', 'w') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
"
        ;;

    kiwisdr|splitter|mla30_outdoor)
        # Test HF signal quality via RSP1B
        echo "Testing HF signal quality (requires OpenWebRX stop)..."
        docker stop openwebrx > /dev/null 2>&1
        sleep 3
        killall sdrplay_apiService 2>/dev/null
        sleep 2
        /opt/sdrplay_api/sdrplay_apiService &
        APIPID=$!
        sleep 5

        python3 -c "
import numpy as np, SoapySDR, json

results = {}
freqs = {
    'wwv_5mhz': 5000000,
    'wwv_10mhz': 10000000,
    'wwv_15mhz': 15000000,
    'nmc_8682': 8680100,
    'nmc_4346': 4344100,
    'kodiak_8457': 8455100,
    'ft8_40m': 7074000,
    'am_komo_1000': 1000000,
}

for name, freq in freqs.items():
    try:
        args = SoapySDR.KwargsFromString('driver=sdrplay')
        sdr = SoapySDR.Device(args)
        sdr.setSampleRate(SoapySDR.SOAPY_SDR_RX, 0, 250000)
        sdr.setFrequency(SoapySDR.SOAPY_SDR_RX, 0, freq)
        sdr.setGainMode(SoapySDR.SOAPY_SDR_RX, 0, False)
        sdr.setGain(SoapySDR.SOAPY_SDR_RX, 0, 40)
        rxStream = sdr.setupStream(SoapySDR.SOAPY_SDR_RX, SoapySDR.SOAPY_SDR_CF32)
        sdr.activateStream(rxStream)
        buf = np.zeros(8192, dtype=np.complex64)
        iq = []
        for i in range(150):
            sr = sdr.readStream(rxStream, [buf], 8192)
            if sr.ret > 0: iq.append(buf[:sr.ret].copy())
        sdr.deactivateStream(rxStream)
        sdr.closeStream(rxStream)
        del sdr
        iq = np.concatenate(iq)
        power = float(10 * np.log10(np.mean(np.abs(iq)**2) + 1e-20))
        fft = np.fft.fftshift(np.abs(np.fft.fft(iq[:65536])))
        snr = float(20 * np.log10(np.max(fft) / (np.median(fft) + 1e-20)))
        results[name] = {'power_db': round(power, 1), 'snr_db': round(snr, 1)}
        print('  %s: power=%.1f dB, SNR=%.1f dB' % (name, power, snr))
    except Exception as e:
        results[name] = {'error': str(e)}
        print('  %s: ERROR %s' % (name, e))

result = {
    'todo_id': '$TODO_ID',
    'label': '$LABEL',
    'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
    'tests': results
}
with open('$RESULTFILE', 'w') as f:
    json.dump(result, f, indent=2)
" 2>&1

        kill $APIPID 2>/dev/null
        wait $APIPID 2>/dev/null
        killall -9 sdrplay_apiService 2>/dev/null
        docker start openwebrx > /dev/null 2>&1
        ;;

    ppm_cal)
        # Measure frequency offset against NOAA WX
        echo "Testing frequency accuracy on NOAA WX 162.55 MHz..."
        TMPCSV="/tmp/bench_ppm.csv"
        run_power_scan 1 "162.54M:162.56M:100" 100 15 "$TMPCSV"

        python3 -c "
import csv, json
scans = {}
with open('$TMPCSV') as f:
    for row in csv.reader(f):
        if len(row) < 7: continue
        try:
            fl = int(float(row[2]))
            fs = float(row[4])
            for i, p in enumerate([float(x) for x in row[6:]]):
                scans[fl + int(i * fs)] = p
        except: pass
if scans:
    peak_freq = max(scans, key=scans.get)
    expected = 162550000
    offset_hz = peak_freq - expected
    offset_ppm = offset_hz / (expected / 1e6)
    result = {
        'todo_id': 'ppm_cal', 'label': '$LABEL',
        'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
        'tests': {
            'noaa_wx_peak_hz': peak_freq,
            'expected_hz': expected,
            'offset_hz': offset_hz,
            'offset_ppm': round(offset_ppm, 1),
            'peak_power_db': round(scans[peak_freq], 1)
        }
    }
else:
    result = {'todo_id': 'ppm_cal', 'label': '$LABEL', 'tests': {'error': 'no data'}}
with open('$RESULTFILE', 'w') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
"
        rm -f "$TMPCSV"
        ;;

    change_passwords|https|adsb_feed|aprs_igate|ais_feed)
        # Software/security items - just record status
        python3 -c "
import json
result = {
    'todo_id': '$TODO_ID',
    'label': '$LABEL',
    'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
    'tests': {'status': 'manual_check', 'note': 'This item requires manual verification'}
}
with open('$RESULTFILE', 'w') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
"
        ;;

    replace_dongle)
        # Count USB devices
        RTL_COUNT=$(lsusb | grep -c "0bda:2838")
        python3 -c "
import json
result = {
    'todo_id': 'replace_dongle',
    'label': '$LABEL',
    'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
    'tests': {'rtlsdr_count': $RTL_COUNT, 'expected': 3}
}
with open('$RESULTFILE', 'w') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
"
        ;;

    all)
        echo "Running all benchmarks..."
        $0 rg6_tram "baseline_${LABEL}"
        $0 kiwisdr "baseline_${LABEL}"
        $0 ppm_cal "baseline_${LABEL}"
        $0 replace_dongle "baseline_${LABEL}"
        echo "All benchmarks complete. Results in $BENCHDIR/"
        ls -la "$BENCHDIR/"*_baseline_*.json 2>/dev/null
        ;;

    *)
        echo "Unknown todo: $TODO_ID"
        echo "Usage: $0 <todo_id|all> [label]"
        echo "Valid IDs: rg6_tram, kiwisdr, splitter, ppm_cal, discone_outdoor, replace_dongle, change_passwords, adsb_feed, aprs_igate, ais_feed, https, mla30_outdoor, lna_adsb, all"
        exit 1
        ;;
esac

echo "Result saved to: $RESULTFILE"
