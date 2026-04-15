# sdr-station-kit

A complete, automated SDR monitoring station built on OpenWebRX+ with multi-radio support, 460+ frequency bookmarks, automated weather fax capture, and a custom web interface.

## Features

- **OpenWebRX+** web-based SDR receiver with softMBE digital voice decoding (DMR, D-STAR, YSF, NXDN, P25)
- **Multi-radio support** -- RTL-SDR (R820T, E4000) and SDRplay RSP1B
- **460+ bookmarks** organized by category with active signal detection
- **Custom bookmarks web interface** with:
  - Split-pane layout (bookmarks + embedded receiver)
  - One-click tuning with automatic profile switching
  - Radio indicator badges (which SDR handles each frequency)
  - Modulation mode color-coded badges
  - Filter by radio, modulation type, or active status
  - Live frequency tracking from the receiver
  - Collapsible sidebar with category mini-nav
  - Search with clear button
- **Automated weather fax capture** from NMC Point Reyes and NOJ Kodiak
- **Weather dashboard** with:
  - Fax chart gallery with archive and filtering
  - NAVTEX marine text weather
  - EAS emergency alert monitoring
  - SITOR-B maritime safety
  - DSC digital selective calling
  - Live countdown timers to next captures
  - Tabbed interface with schedule view
- **Weekly frequency scanning** across all bands with active signal detection
- **Conflict-free scheduling** -- automated checks prevent RSP1B task overlaps

## Hardware

Tested with:
- Raspberry Pi 5 (8GB) running DragonOS (Debian 13 trixie)
- 2x Nooelec RTL-SDR (NESDR SMArt v5 R820T + SMArt XTR v5 E4000)
- SDRplay RSP1B
- Powered USB hub recommended for multiple dongles

## Quick Start

```bash
git clone https://github.com/deviros123/sdr-station-kit.git
cd sdr-station-kit
sudo ./install.sh
```

> **New to SDR?** See the [Complete Setup Guide](docs/SETUP.md) for step-by-step instructions covering hardware purchase, OS installation, antenna selection, and configuration.

After installation:
- **Receiver**: `http://<pi-ip>:8073`
- **Bookmarks**: `http://<pi-ip>:8073/static/seattle-bookmarks.html`
- **Weather Center**: `http://<pi-ip>:8073/static/weatherfax/index.html`

## Frequency Coverage

### Seattle/Pacific Northwest Bookmarks (464 frequencies)

| Category | Count | Bands |
|----------|-------|-------|
| FM Broadcast | 29 | 88-108 MHz |
| AM Broadcast | 22 | 530-1700 kHz |
| Aviation | 40+ | 108-137 MHz |
| Marine / AIS / NOAA WX | 20+ | 156-163 MHz |
| Railroad | 10+ | 160-162 MHz |
| Public Safety / Fire / EMS | 30+ | 150-156 MHz |
| KCERS P25 800 MHz | 20+ | 851-859 MHz |
| City / Transit / Hospital | 30+ | 453-464 MHz |
| Amateur 2m | 15+ | 144-148 MHz |
| Amateur 70cm / Digital Voice | 20+ | 440-450 MHz |
| HF / Shortwave / CB | 40+ | 1 kHz - 30 MHz |
| And 10+ more categories | | |

### Customizing for Your Location

The Seattle bookmarks are in `config/bookmarks/seattle.json`. To adapt for another city:

1. Edit the JSON file with your local frequencies
2. Update `config/openwebrx/settings.json` with your GPS coordinates and SDR profiles
3. Run `python3 bin/gen_bookmarks.py` to regenerate the web interface
4. Modify `config/crontab` weather fax times if outside Pacific time zone

## Architecture

```
OpenWebRX+ (Docker) ──── RTL-SDR E4000 (VHF/UHF 52-2174 MHz)
     │                ├── RTL-SDR R820T (VHF/UHF 24-1766 MHz)
     │                └── SDRplay RSP1B (HF-UHF 1kHz-2GHz)
     │
     ├── :8073/                    Web receiver
     ├── :8073/static/seattle-bookmarks.html  Custom bookmarks UI
     ├── :8073/static/weatherfax/  Weather dashboard
     └── :8073/map                 Map view (AIS, APRS, ADS-B)

Cron Jobs ─── wxfax-capture.sh     Weather fax (21x/day)
          ├── weather-monitor.sh   NAVTEX + EAS text
          ├── sdr-weekly-scan.sh   Full band scan (weekly)
          └── weather-dashboard.py Dashboard refresh (every 15 min)
```

## File Structure

```
sdr-station-kit/
├── install.sh                 # One-command installer
├── bin/
│   ├── gen_bookmarks.py       # Bookmarks web page generator
│   ├── sdr-weekly-scan.sh     # Full-band frequency scanner
│   ├── sdr-analyze-scan.py    # Scan data analyzer
│   ├── check-schedule.py      # Crontab conflict checker
│   ├── wxfax-capture.sh       # Weather fax capture orchestrator
│   ├── wxfax-record.py        # SoapySDR audio recorder
│   ├── wxfax-decode.py        # Radiofax image decoder
│   ├── weather-dashboard.py   # Weather center page generator
│   ├── weather-monitor.sh     # NAVTEX/EAS text capture
│   └── openwebrx-inject.sh    # Bookmarks page persistence
├── config/
│   ├── bookmarks/
│   │   └── seattle.json       # 464 Seattle-area frequency bookmarks
│   ├── openwebrx/
│   │   ├── settings.json      # SDR device and profile configuration
│   │   └── openwebrx.conf     # OpenWebRX+ base config
│   ├── systemd/               # Service unit files
│   ├── blacklist-rtlsdr.conf  # DVB driver blacklist
│   └── crontab                # Automated capture schedule
└── docs/
```

## Supported Decoders

OpenWebRX+ with softMBE provides these decoders out of the box:

| Mode | Decoder | Use |
|------|---------|-----|
| NFM, AM, WFM, USB, LSB, CW | Analog audio | Standard radio |
| DMR | softMBE | Digital voice repeaters |
| D-STAR | softMBE | Digital voice |
| YSF (System Fusion) | softMBE | Digital voice |
| NXDN | softMBE | Digital voice |
| P25 | softMBE | Public safety trunked |
| POCSAG/FLEX | multimon-ng | Pager decoding |
| ACARS | acarsdec | Aircraft text messages |
| ADS-B | dump1090 | Aircraft tracking |
| AIS | Built-in | Ship tracking |
| APRS/Packet | Built-in | Ham position reports |
| FT8, WSPR, JS8 | Built-in | HF digital modes |
| SSTV | Built-in | Slow-scan TV images |
| FAX | Built-in | Weather fax charts |
| NAVTEX | Built-in | Marine text weather |
| EAS | Built-in | Emergency alerts |
| ISM | Built-in | IoT sensor data |
| Radiosonde | Built-in | Weather balloon telemetry |
| DRM | dream | Digital shortwave broadcast |
| HFDL | dumphfdl | HF data link |

## License

MIT
