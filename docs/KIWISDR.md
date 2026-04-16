# KiwiSDR Integration Guide

## Overview

Adding a KiwiSDR 2 to your station eliminates all OpenWebRX+ downtime during automated captures. The KiwiSDR handles all HF weather fax and NAVTEX decoding independently.

## Hardware Setup

### What You Need
- KiwiSDR 2 (~$300, includes BeagleBone)
- Ethernet cable (KiwiSDR requires wired network)
- 5V 2A power supply (included with KiwiSDR)
- Antenna splitter (to share MLA-30+ with RSP1B)

### Antenna Sharing

```
MLA-30+ Active Loop (0.5-30 MHz)
    │
    ├── [Splitter] ──→ RSP1B (OpenWebRX+ HF browsing)
    │              └──→ KiwiSDR 2 (automated captures + web UI)
    │
    Options:
    ├── BNC T-adapter ($5) -- works fine, ~6 dB loss
    ├── Mini-Circuits ZFSC-2-2 ($30) -- proper 3.5 dB split  
    └── Stridsberg MCA204M ($150) -- active, 0 dB loss, 4 ports
```

### Network Setup

1. Connect KiwiSDR to your router via Ethernet
2. Find its IP: check router DHCP leases or use `nmap -sn 192.168.x.0/24`
3. KiwiSDR admin page: `http://<kiwi-ip>:8073/admin`
4. **Important**: Change KiwiSDR port to **8074** if running on same network as OpenWebRX+ (both default to 8073)

### Initial KiwiSDR Configuration

1. Open `http://<kiwi-ip>:8073/admin`
2. Set your location (GPS coordinates)
3. Set a station name
4. Under Network tab: set port to **8074** (avoid conflict with OpenWebRX+)
5. Under Config tab: set antenna to "Active Loop MLA-30+"

## Software Setup

On the Raspberry Pi (where OpenWebRX+ runs):

```bash
cd sdr-station-kit
sudo ./bin/kiwi-setup.sh <kiwi-ip> 8074
```

This will:
- Install `kiwiclient` Python package
- Test the KiwiSDR connection
- Deploy capture scripts
- Switch the crontab from RSP1B captures to KiwiSDR captures

### Manual Setup

```bash
# Install kiwiclient
pip3 install kiwiclient --break-system-packages

# Test connection
kiwirecorder --host <kiwi-ip> --port 8074 \
    --frequency 10000 --modulation am --tlimit 5 \
    --filename test --dir /tmp/

# Switch to KiwiSDR crontab
sudo crontab config/crontab.kiwisdr
```

## What Changes

| Before (RSP1B) | After (KiwiSDR) |
|---|---|
| OpenWebRX stops for each capture | OpenWebRX stays running 24/7 |
| Python homebrew fax decoder | KiwiSDR's proven built-in decoder |
| Manual start/stop tone detection | Automatic start/stop detection |
| 1 capture at a time | Up to 4 simultaneous captures |
| ~5 hours daily downtime | Zero downtime |
| Noisy/static images | Clean decoded charts |

## Capture Schedule

The KiwiSDR crontab (`config/crontab.kiwisdr`) includes:
- **14 Point Reyes** charts per day
- **7 Kodiak** charts per day
- **4 JMH Tokyo** charts per day (bonus Pacific coverage)
- **6 NAVTEX** monitoring sessions per day
- **EAS** monitoring still uses RTL-SDR (VHF, not HF)

Total: **31 weather fax captures + 6 NAVTEX** with zero downtime.

## Accessing the KiwiSDR

- **KiwiSDR Web UI**: `http://<kiwi-ip>:8074` -- full 0-30 MHz waterfall, 4 users
- **OpenWebRX+**: `http://<pi-ip>:8073` -- RTL-SDR + RSP1B, stays online 24/7
- **Bookmarks**: `http://<pi-ip>:8073/static/seattle-bookmarks.html`
- **Weather Center**: `http://<pi-ip>:8073/static/weatherfax/index.html`

## Troubleshooting

### KiwiSDR not found
```bash
# Check if it's on the network
ping <kiwi-ip>

# Check if the web port is open
curl -s http://<kiwi-ip>:8074/status

# Check if kiwirecorder can connect
kiwirecorder --host <kiwi-ip> --port 8074 --frequency 10000 --modulation am --tlimit 5 --dir /tmp/
```

### Fax images are blank
- Verify antenna is connected and MLA-30+ is powered
- Check if the KiwiSDR sees signal: open its web UI and tune to 8682 kHz USB
- Try a known active frequency: JMH Tokyo 7793.5 kHz USB (almost always transmitting)

### Port conflict with OpenWebRX+
Both default to port 8073. Change KiwiSDR to 8074 in its admin page, or change OpenWebRX+ Docker to `-p 8075:8073`.
