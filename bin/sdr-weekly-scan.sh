#!/bin/bash
# SDR Weekly Frequency Scanner - All 3 radios
# Crontab: 0 3 * * 0 /home/dragon/sdr-weekly-scan.sh

LOG="/home/dragon/sdr-scan.log"
SCANDIR="/tmp/sdr-scans"

echo "$(date) - Starting weekly SDR scan" | tee $LOG
mkdir -p $SCANDIR
rm -f $SCANDIR/*.csv

# Stop OpenWebRX to free all dongles
echo "Stopping OpenWebRX..." | tee -a $LOG
docker stop openwebrx >> $LOG 2>&1
sleep 5

# Start SDRplay API service on host for RSP1B scanning
echo "Starting SDRplay API on host..." | tee -a $LOG
/usr/local/bin/sdrplay_apiService &
SDRPLAY_PID=$!
sleep 3

scan_rtl() {
    local dev=$1 name=$2 frange=$3 step=$4 gain=$5 outfile=$6
    echo "  [$name] $frange step=$step..." | tee -a $LOG
    timeout 45 rtl_power -d $dev -f $frange -g $gain -i 5 -e 10 $SCANDIR/$outfile >> $LOG 2>&1
}

scan_rsp() {
    local name=$1 frange=$2 rate=$3 time=$4 outfile=$5
    echo "  [RSP1B] $name $frange..." | tee -a $LOG
    timeout 60 soapy_power -d driver=sdrplay -f $frange -r $rate -T $time -F rtl_power > $SCANDIR/$outfile 2>> $LOG
}

# === E4000 (device 0): 52-1087 MHz ===
echo "$(date) - Scanning E4000..." | tee -a $LOG
scan_rtl 0 "E4000" "52M:88M:25k"    25k 30 e4_vhf_low.csv
scan_rtl 0 "E4000" "85M:110M:25k"   25k 30 e4_fm.csv
scan_rtl 0 "E4000" "108M:138M:25k"  25k 30 e4_air.csv
scan_rtl 0 "E4000" "138M:174M:25k"  25k 30 e4_vhf_high.csv
scan_rtl 0 "E4000" "220M:320M:25k"  25k 20 e4_ptc_ism.csv
scan_rtl 0 "E4000" "425M:440M:25k"  25k 30 e4_ism433.csv

# === R820T (device 1): 24-1766 MHz ===
echo "$(date) - Scanning R820T..." | tee -a $LOG
scan_rtl 1 "R820T" "118M:138M:25k"     25k 30 r1_air.csv
scan_rtl 1 "R820T" "144M:174M:12.5k"   12.5k 30 r1_vhf.csv
scan_rtl 1 "R820T" "440M:470M:12.5k"   12.5k 30 r1_uhf.csv
scan_rtl 1 "R820T" "450M:465M:12.5k"   12.5k 30 r1_city.csv
scan_rtl 1 "R820T" "606M:616M:25k"     25k 30 r1_wmts.csv
scan_rtl 1 "R820T" "725M:770M:25k"     25k 30 r1_lte.csv
scan_rtl 1 "R820T" "849M:870M:12.5k"   12.5k 30 r1_p25.csv
scan_rtl 1 "R820T" "869M:895M:25k"     25k 30 r1_cell850.csv
scan_rtl 1 "R820T" "900M:920M:25k"     25k 30 r1_ism900.csv
scan_rtl 1 "R820T" "925M:935M:12.5k"   12.5k 30 r1_pager.csv
scan_rtl 1 "R820T" "973M:983M:25k"     25k 30 r1_uat.csv
scan_rtl 1 "R820T" "1025M:1035M:25k"   25k 30 r1_tacan.csv
scan_rtl 1 "R820T" "1085M:1095M:25k"   25k 30 r1_adsb.csv

# === RSP1B: Full HF spectrum + extended ===
echo "$(date) - Scanning RSP1B HF..." | tee -a $LOG
scan_rsp "VLF/LF"       "10k:100k:100"     250e3  10 rsp_vlf.csv
scan_rsp "LF/MW"        "100k:2M:500"      2e6    10 rsp_lf.csv
scan_rsp "HF 2-6 MHz"   "2M:6M:500"        2e6    10 rsp_hf_2_6.csv
scan_rsp "HF 6-10 MHz"  "6M:10M:500"       2e6    10 rsp_hf_6_10.csv
scan_rsp "HF 10-14 MHz" "10M:14M:500"      2e6    10 rsp_hf_10_14.csv
scan_rsp "HF 14-18 MHz" "14M:18M:500"      2e6    10 rsp_hf_14_18.csv
scan_rsp "HF 18-22 MHz" "18M:22M:500"      2e6    10 rsp_hf_18_22.csv
scan_rsp "HF 22-30 MHz" "22M:30M:500"      2e6    10 rsp_hf_22_30.csv
scan_rsp "CB 26-28 MHz" "26.5M:28M:200"    2e6    10 rsp_cb.csv
scan_rsp "GPS L1"        "1574M:1577M:1k"  2e6    5  rsp_gps.csv
scan_rsp "Iridium"       "1620M:1628M:1k"  2e6    5  rsp_iridium.csv

echo "$(date) - All scans complete" | tee -a $LOG

# Stop SDRplay API service
kill $SDRPLAY_PID 2>/dev/null
wait $SDRPLAY_PID 2>/dev/null

# Restart OpenWebRX
echo "Starting OpenWebRX..." | tee -a $LOG
docker start openwebrx >> $LOG 2>&1
sleep 20

for i in $(seq 1 30); do
    if curl -s -m 2 http://localhost:8073/ > /dev/null 2>&1; then
        echo "OpenWebRX is back up" | tee -a $LOG
        break
    fi
    sleep 2
done

# Analyze and update bookmarks
echo "$(date) - Analyzing scan data..." | tee -a $LOG
python3 /home/dragon/sdr-analyze-scan.py >> $LOG 2>&1

# Regenerate bookmarks page
echo "$(date) - Regenerating bookmarks page..." | tee -a $LOG
python3 /tmp/gen_bookmarks4.py >> $LOG 2>&1
python3 /tmp/fix_notif.py >> $LOG 2>&1
python3 /tmp/fix_layout.py >> $LOG 2>&1

# Inject into container
docker cp /home/dragon/openwebrx-config/seattle-bookmarks.html openwebrx:/usr/lib/python3/dist-packages/htdocs/seattle-bookmarks.html >> $LOG 2>&1

# Verify capture schedule has no conflicts
echo "$(date) - Checking capture schedule for conflicts..." | tee -a $LOG
python3 /home/dragon/check-schedule.py >> $LOG 2>&1

echo "$(date) - Weekly scan complete!" | tee -a $LOG
