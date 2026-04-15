# Complete Setup Guide: SDR Station Kit

This guide walks you through building a complete SDR monitoring station from scratch, from buying the hardware to receiving your first signals.

## Table of Contents

1. [Hardware Shopping List](#1-hardware-shopping-list)
2. [Operating System Setup](#2-operating-system-setup)
3. [Hardware Assembly](#3-hardware-assembly)
4. [Software Installation](#4-software-installation)
5. [Verifying Your SDR Devices](#5-verifying-your-sdr-devices)
6. [Configuring OpenWebRX+](#6-configuring-openwebrx)
7. [Customizing for Your Location](#7-customizing-for-your-location)
8. [Setting Up Automated Captures](#8-setting-up-automated-captures)
9. [Accessing Your Station](#9-accessing-your-station)
10. [Troubleshooting](#10-troubleshooting)
11. [Adding New Frequencies](#11-adding-new-frequencies)
12. [Antenna Recommendations](#12-antenna-recommendations)

---

## 1. Hardware Shopping List

### Required

| Item | Purpose | Approx. Cost |
|------|---------|-------------|
| **Raspberry Pi 5 (8GB)** | Station computer | $80 |
| **microSD card (64GB+)** | Boot drive | $12 |
| **USB-C power supply (27W)** | Pi power | $12 |
| **RTL-SDR dongle** (at least 1) | VHF/UHF receiver (24-1766 MHz) | $30 |
| **Antenna** | Signal reception | $20-50 |

Recommended: **Nooelec NESDR SMArt v5** (R820T2 tuner) for best VHF/UHF sensitivity.

### Recommended Upgrades

| Item | Purpose | Approx. Cost |
|------|---------|-------------|
| **Second RTL-SDR** (E4000 tuner) | Extended range (52-2174 MHz) | $35 |
| **SDRplay RSP1B** | HF/Shortwave (1 kHz - 2 GHz, 10 MHz BW) | $120 |
| **Powered USB hub** | Stable power for multiple dongles | $25 |
| **Ethernet cable** | More reliable than WiFi | $5 |
| **Case with fan** | Keeps Pi cool | $15 |

### Antenna Options

| Antenna | Coverage | Best For |
|---------|----------|----------|
| **Telescopic whip** (included with most RTL-SDRs) | VHF/UHF | Getting started |
| **Discone antenna** (Diamond D130J or similar) | 25-1300 MHz | Wide coverage, outdoor |
| **RTL-SDR Blog dipole kit** | VHF/UHF | Indoor, adjustable |
| **Random wire (10-20m)** | HF | Shortwave with RSP1B |
| **MLA-30+ magnetic loop** | HF | Indoor shortwave |

---

## 2. Operating System Setup

### Option A: DragonOS (Recommended)

DragonOS comes pre-loaded with SDR tools. Download from:
- https://sourceforge.net/projects/dragonos-pi64/

Flash to microSD with:
```bash
# On your computer
sudo dd if=DragonOS-Pi64-*.img of=/dev/sdX bs=4M status=progress
```

Or use **Raspberry Pi Imager** and select the DragonOS image.

Default credentials: `dragon` / `dragon`

### Option B: Raspberry Pi OS (64-bit)

If using stock Raspberry Pi OS:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install RTL-SDR tools
sudo apt install -y rtl-sdr librtlsdr-dev

# Install SoapySDR (for SDRplay)
sudo apt install -y soapysdr-tools python3-soapysdr
```

### First Boot

1. Insert microSD, connect Ethernet, power on
2. Find your Pi's IP: check your router or run `hostname -I` on the Pi
3. SSH in: `ssh dragon@<pi-ip>` (password: `dragon`)
4. Change the default password: `passwd`

---

## 3. Hardware Assembly

### Connecting SDR Dongles

1. **With 1 dongle**: Plug directly into Pi USB port
2. **With 2-3 dongles**: Use a **powered USB hub** -- multiple RTL-SDRs draw ~300mA each, which can exceed the Pi's USB power budget
3. **SDRplay RSP1B**: Connect via USB, works alongside RTL-SDRs

### Identifying Your Dongles

```bash
# List USB devices
lsusb | grep -i "rtl\|sdr"

# Test RTL-SDR detection
rtl_test -d 0 -t    # Test device 0
rtl_test -d 1 -t    # Test device 1 (if you have two)
```

Each dongle has a serial number. Note these -- you'll need them for configuration.

### Blacklist DVB Drivers

RTL-SDR dongles ship as DVB-T TV receivers. The kernel's DVB driver grabs them before SDR software can. Fix this:

```bash
sudo cp config/blacklist-rtlsdr.conf /etc/modprobe.d/
sudo reboot
```

After reboot, verify no DVB modules loaded:
```bash
lsmod | grep dvb    # Should return nothing
```

---

## 4. Software Installation

### Quick Install

```bash
git clone https://github.com/deviros123/sdr-station-kit.git
cd sdr-station-kit
sudo ./install.sh
```

This installs Docker, pulls OpenWebRX+, configures everything, and starts the receiver.

### Manual Install

If you prefer to understand each step:

#### Install Docker
```bash
sudo apt install -y docker.io
sudo usermod -aG docker $USER
sudo systemctl enable docker
```

#### Pull OpenWebRX+ (with digital voice decoding)
```bash
sudo docker pull slechev/openwebrxplus-softmbe:latest
```

#### Create directories
```bash
mkdir -p ~/openwebrx-config/bookmarks.d
mkdir -p ~/openwebrx-data
mkdir -p ~/weatherfax/{wav,images,latest}
mkdir -p ~/weather-text
```

#### Start the container
```bash
sudo docker run -d \
    --name openwebrx \
    --restart unless-stopped \
    -p 8073:8073 \
    --device /dev/bus/usb \
    -v ~/openwebrx-config:/etc/openwebrx \
    -v ~/openwebrx-data:/var/lib/openwebrx \
    -v ~/weatherfax:/usr/lib/python3/dist-packages/htdocs/weatherfax \
    slechev/openwebrxplus-softmbe:latest
```

#### Create admin user
```bash
# Wait 15 seconds for container to start, then:
echo -e "yourpassword\nyourpassword" | sudo docker exec -i openwebrx openwebrx admin adduser admin
```

---

## 5. Verifying Your SDR Devices

### Check detection inside the container
```bash
sudo docker exec openwebrx rtl_test -d 0 -t   # RTL-SDR device 0
sudo docker exec openwebrx rtl_test -d 1 -t   # RTL-SDR device 1
```

You should see output like:
```
Found 2 device(s):
  0:  Nooelec, NESDR SMArt v5, SN: 86215444
  1:  Nooelec, SMArt XTR v5, SN: 00000001
```

### Check SDRplay RSP1B
```bash
sudo docker exec openwebrx SoapySDRUtil --find="driver=sdrplay"
```

If the RSP1B isn't found, restart the container:
```bash
sudo docker stop openwebrx && sudo docker start openwebrx
```

### Common Issues

| Problem | Solution |
|---------|----------|
| `usb_open error -4` | Another process has the device. Stop OpenWebRX first. |
| Only 1 of 2 dongles found | USB power issue. Use a powered hub. |
| Garbled device names | Container has stale USB handles. Stop/start container. |
| `dvb_usb_rtl28xxu` loaded | DVB blacklist not applied. Reboot after installing blacklist. |

---

## 6. Configuring OpenWebRX+

### SDR Device Settings

Edit `config/openwebrx/settings.json` to match your hardware. Key fields:

```json
{
    "sdrs": {
        "my-rtlsdr": {
            "name": "My RTL-SDR",
            "type": "rtl_sdr",
            "device": "0",
            "profiles": {
                "fm": {
                    "name": "FM Broadcast",
                    "center_freq": 98000000,
                    "samp_rate": 2400000,
                    "start_freq": 98100000,
                    "start_mod": "wfm"
                }
            }
        }
    }
}
```

- `type`: `rtl_sdr` for RTL-SDR, `sdrplay` for RSP1B
- `device`: Device index (0, 1, 2...)
- `samp_rate`: Bandwidth. RTL-SDR max 2400000, RSP1B up to 10000000
- `start_mod`: Default demodulator (`am`, `nfm`, `wfm`, `usb`, `lsb`, `dmr`, `p25`, etc.)

### Receiver Location

Set your coordinates in `settings.json`:
```json
{
    "receiver_name": "My SDR Station",
    "receiver_location": "My City, State",
    "receiver_gps": {"lat": 47.6062, "lon": -122.3321},
    "receiver_asl": 50
}
```

### Important Settings

```json
{
    "version": 8,
    "max_clients": 20,
    "max_clients_per_ip": 10,
    "bot_ban_enabled": false,
    "map_type": "osm"
}
```

---

## 7. Customizing for Your Location

### Creating Your Bookmark File

The included `seattle.json` is an example. Create your own:

```json
[
    {
        "name": "Local FM Station",
        "frequency": 98100000,
        "modulation": "wfm"
    },
    {
        "name": "Police Dispatch",
        "frequency": 460125000,
        "modulation": "nfm"
    }
]
```

Save as `config/bookmarks/your-city.json` and copy to:
```bash
sudo cp config/bookmarks/your-city.json ~/openwebrx-config/bookmarks.d/
sudo docker restart openwebrx
```

### Modulation Reference

| Use Case | Modulation | Value |
|----------|-----------|-------|
| FM broadcast | Wideband FM | `wfm` |
| AM broadcast | AM | `am` |
| Police/Fire/Business | Narrowband FM | `nfm` |
| Aviation | AM | `am` |
| SSB (amateur) | Upper/Lower sideband | `usb` / `lsb` |
| Digital voice | DMR, D-STAR, YSF, P25 | `dmr`, `dstar`, `ysf`, `p25` |
| Pagers | POCSAG/FLEX | `page` |
| Aircraft tracking | ADS-B | `adsb` |
| Ship tracking | AIS | `ais` |
| APRS | Packet | `packet` |
| FT8 | FT8 | `ft8` |
| Weather fax | Fax | `fax` |
| ACARS | ACARS | `acars` |
| Weather balloon | Radiosonde | `sonde-rs41` |

### Generating the Bookmarks Web Page

After editing bookmarks or profiles:
```bash
python3 bin/gen_bookmarks.py
sudo docker cp ~/openwebrx-config/seattle-bookmarks.html openwebrx:/usr/lib/python3/dist-packages/htdocs/seattle-bookmarks.html
```

### Finding Frequencies for Your Area

- **RadioReference.com** -- Most comprehensive US scanner frequency database
- **RepeaterBook.com** -- Amateur radio repeaters
- **LiveATC.net** -- Aviation frequencies by airport
- **FCC ULS** (wireless.fcc.gov) -- Licensed frequency assignments
- **RTL-SDR.com** -- General SDR frequency guides

---

## 8. Setting Up Automated Captures

### Weather Fax Schedule

Edit `config/crontab` to match your region's radiofax stations:

**US West Coast**: NMC Point Reyes (4346/8682 kHz) and NOJ Kodiak (4296/8457 kHz)
**US East Coast**: NMF Boston (4233/6338/9108/12748 kHz)
**US Gulf**: NMG New Orleans (4316/8502/12788 kHz)
**Hawaii**: KVM70 Honolulu (9980/11088/16133 kHz)

Full schedules: https://ocean.weather.gov/shtml/pacsch.php

### NAVTEX Stations

| Station | Location | Frequency |
|---------|----------|-----------|
| W | Astoria, OR | 518 kHz |
| Q | Cambria, CA | 518 kHz |
| C | San Francisco, CA | 518 kHz |
| N | Boston, MA | 518 kHz |
| F | New Orleans, LA | 518 kHz |

### Installing the Schedule

```bash
sudo crontab config/crontab
```

### Checking for Conflicts

```bash
python3 bin/check-schedule.py
```

This verifies no two RSP1B tasks overlap. Each capture temporarily stops OpenWebRX+ (~12 minutes), so tasks must be spaced apart.

---

## 9. Accessing Your Station

| Page | URL | Purpose |
|------|-----|---------|
| Receiver | `http://<pi-ip>:8073` | Main SDR receiver with waterfall |
| Bookmarks | `http://<pi-ip>:8073/static/seattle-bookmarks.html` | Custom bookmark interface |
| Weather Center | `http://<pi-ip>:8073/static/weatherfax/index.html` | Weather fax, NAVTEX, EAS |
| Map | `http://<pi-ip>:8073/map` | AIS ships, APRS, ADS-B aircraft |
| Admin | `http://<pi-ip>:8073/settings` | Configuration (login required) |

### Remote Access

To access from outside your network:
1. Set up port forwarding on your router (port 8073 -> Pi IP)
2. Or use a reverse tunnel (e.g., Cloudflare Tunnel, Tailscale)

---

## 10. Troubleshooting

### OpenWebRX+ won't start
```bash
sudo docker logs openwebrx    # Check logs
sudo docker restart openwebrx  # Restart
```

### "No SDR Devices available"
```bash
# Check if dongles are on the bus
lsusb | grep -i rtl

# Restart container to re-detect
sudo docker stop openwebrx && sleep 5 && sudo docker start openwebrx
```

### Dongle keeps disconnecting
- Use a **powered USB hub**
- Check `dmesg | grep -i usb` for error messages
- Some USB ports on the Pi are more stable than others
- If one specific dongle is flaky, try a different USB port or replace it

### "Client address banned"
Set in `settings.json`:
```json
{
    "max_clients_per_ip": 10,
    "bot_ban_enabled": false
}
```
Restart the container to clear existing bans.

### Weather fax captures are blank
- Check the log: `cat ~/weatherfax/capture.log`
- Verify the SDRplay API service can start: `/usr/local/bin/sdrplay_apiService`
- HF reception depends heavily on antenna and time of day
- 8682 kHz works best daytime, 4346 kHz at night

### No audio from the receiver
- Click "Start OpenWebRX+" button in the browser
- Check that your browser allows audio autoplay for the site
- Try a different browser

---

## 11. Adding New Frequencies

### Add to bookmarks JSON
```bash
# Edit the bookmarks file
nano ~/openwebrx-config/bookmarks.d/seattle.json
```

Add entries in this format:
```json
{
    "name": "Station Name",
    "frequency": 162550000,
    "modulation": "nfm"
}
```

Frequency is in Hz (162.55 MHz = 162550000).

### Add a matching profile (if needed)

If the frequency isn't within any existing profile's bandwidth, add one in `settings.json`:

```json
"new_profile": {
    "name": "My New Band (160-163 MHz)",
    "center_freq": 161500000,
    "samp_rate": 2400000,
    "start_freq": 162550000,
    "start_mod": "nfm"
}
```

The profile must cover the bookmark frequency: `center_freq - samp_rate/2` to `center_freq + samp_rate/2`.

### Regenerate and deploy
```bash
python3 ~/gen_bookmarks.py
sudo docker cp ~/openwebrx-config/seattle-bookmarks.html openwebrx:/usr/lib/python3/dist-packages/htdocs/seattle-bookmarks.html
sudo docker restart openwebrx
```

### Run a scan to check for activity
```bash
sudo ~/sdr-weekly-scan.sh
```

---

## 12. Antenna Recommendations

### Basic Setup (RTL-SDR only)
The telescopic whip antenna that comes with most RTL-SDR dongles works for strong local signals (FM broadcast, NOAA weather, local repeaters). For better results:

### Wideband VHF/UHF
**Discone antenna** mounted outdoors as high as possible. Covers 25-1300 MHz with no tuning needed. Best all-around choice for a monitoring station.

### HF/Shortwave (RSP1B)
- **Random wire**: 10-20 meters of wire strung as high as possible, connected to the RSP1B's SMA input via a balun (9:1 or 49:1). Cheapest and most effective HF antenna.
- **End-fed half-wave**: Better performance than random wire, requires a matching transformer.
- **MLA-30+ magnetic loop**: Indoor option, works surprisingly well for shortwave broadcast.

### ADS-B (1090 MHz)
A dedicated **1090 MHz ground plane antenna** dramatically improves aircraft reception range (from ~50 miles to 200+ miles). Can be built from a PCB connector and 4 pieces of wire.

### Tips
- **Height matters more than antenna type** -- get it outside and as high as possible
- **Coax cable**: Use RG-6 or LMR-240 for runs over 10 feet. Cheap RG-174 loses significant signal.
- **Lightning protection**: If mounting an outdoor antenna, install a lightning arrestor at the building entry point.
- **Multiple antennas**: You can connect different antennas to different SDRs (e.g., discone on RTL-SDR for VHF/UHF, wire on RSP1B for HF).
