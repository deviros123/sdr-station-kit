#!/bin/bash
# KiwiSDR Integration Setup
# Run after connecting KiwiSDR to the network
# Installs kiwiclient, configures capture schedule, tests connection

set -e

KIWI_HOST=${1:-"localhost"}
KIWI_PORT=${2:-8073}

echo "============================================"
echo "  KiwiSDR Integration Setup"
echo "============================================"
echo "KiwiSDR: http://${KIWI_HOST}:${KIWI_PORT}"
echo ""

# 1. Install kiwiclient
echo "[1/4] Installing kiwiclient..."
pip3 install kiwiclient --break-system-packages 2>/dev/null || \
    pip3 install kiwiclient 2>/dev/null || \
    { echo "Trying from git..."; pip3 install git+https://github.com/jks-prv/kiwiclient.git --break-system-packages 2>/dev/null; }

which kiwirecorder && echo "  kiwirecorder installed" || echo "  WARNING: kiwirecorder not found in PATH"

# 2. Test connection
echo "[2/4] Testing KiwiSDR connection..."
timeout 10 kiwirecorder \
    --host "$KIWI_HOST" --port "$KIWI_PORT" \
    --frequency 10000 --modulation am \
    --tlimit 5 \
    --filename "kiwi_test" \
    --dir /tmp/ 2>&1 | tail -3

if [ -f /tmp/kiwi_test*.wav ]; then
    echo "  Connection OK!"
    rm -f /tmp/kiwi_test*.wav
else
    echo "  WARNING: Could not connect to KiwiSDR at ${KIWI_HOST}:${KIWI_PORT}"
    echo "  Make sure the KiwiSDR is powered on and accessible."
fi

# 3. Deploy scripts
echo "[3/4] Deploying capture scripts..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp "$SCRIPT_DIR/kiwi-fax-capture.sh" /home/dragon/ 2>/dev/null || true
cp "$SCRIPT_DIR/kiwi-navtex-monitor.sh" /home/dragon/ 2>/dev/null || true
chmod +x /home/dragon/kiwi-fax-capture.sh /home/dragon/kiwi-navtex-monitor.sh 2>/dev/null || true

# Set KiwiSDR host/port in environment
echo "export KIWI_HOST=${KIWI_HOST}" >> /home/dragon/.bashrc
echo "export KIWI_PORT=${KIWI_PORT}" >> /home/dragon/.bashrc

# 4. Switch crontab from RSP1B captures to KiwiSDR captures
echo "[4/4] Updating capture schedule to use KiwiSDR..."

# Build new crontab replacing wxfax-capture with kiwi-fax-capture
# and weather-monitor navtex with kiwi-navtex-monitor
crontab -l 2>/dev/null | \
    sed 's|/home/dragon/wxfax-capture.sh \([0-9]*\) |/home/dragon/kiwi-fax-capture.sh \1 |g' | \
    sed "s|wxfax-capture.sh \([0-9]*\)000 |kiwi-fax-capture.sh \1 |g" | \
    sed 's|/home/dragon/weather-monitor.sh navtex.*|/home/dragon/kiwi-navtex-monitor.sh 600|g' | \
    crontab -

echo ""
echo "============================================"
echo "  KiwiSDR Integration Complete!"
echo "============================================"
echo ""
echo "KiwiSDR Web UI:    http://${KIWI_HOST}:${KIWI_PORT}"
echo "Weather Fax:       Now captured via KiwiSDR (zero OpenWebRX downtime)"
echo "NAVTEX:            Now monitored via KiwiSDR"
echo ""
echo "NOTE: The KiwiSDR uses port 8073 by default, same as OpenWebRX+."
echo "If both run on the same Pi, change the KiwiSDR to port 8074:"
echo "  Set port in KiwiSDR admin page -> Network tab"
echo "  Then re-run: sudo ./kiwi-setup.sh localhost 8074"
