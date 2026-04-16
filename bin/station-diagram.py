#!/usr/bin/env python3
"""Generate station documentation page with SVG diagram."""

html = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SDR Station Documentation</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:sans-serif;background:#0d1117;color:#c9d1d9;padding:20px}
h1{color:#58a6ff;text-align:center;margin-bottom:5px}
h2{color:#f0883e;border-bottom:1px solid #21262d;padding-bottom:8px;margin:25px 0 15px 0}
h3{color:#58a6ff;margin:15px 0 8px 0}
.subtitle{text-align:center;color:#484f58;margin-bottom:20px;font-size:0.85em}
.nav{display:flex;gap:10px;justify-content:center;margin:15px 0;flex-wrap:wrap}
.nav a{color:#58a6ff;text-decoration:none;background:#161b22;border:1px solid #21262d;padding:5px 12px;border-radius:4px;font-size:0.85em}
.nav a:hover{background:#1c2129}
.diagram-container{background:#161b22;border:1px solid #21262d;border-radius:12px;padding:20px;margin:20px 0;overflow-x:auto}
table{width:100%;border-collapse:collapse;margin:10px 0}
th{background:#161b22;color:#58a6ff;text-align:left;padding:8px 10px;border-bottom:2px solid #21262d}
td{padding:8px 10px;border-bottom:1px solid #21262d;font-size:0.85em}
tr:hover{background:#1c2129}
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:15px;margin:15px 0}
.card{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:15px}
.card .title{color:#58a6ff;font-weight:bold;font-size:1.05em;margin-bottom:5px}
.card .type{color:#f0883e;font-size:0.75em;text-transform:uppercase;margin-bottom:8px}
.card .spec{color:#8b949e;font-size:0.8em;line-height:1.6}
.card .spec b{color:#c9d1d9}
.freq-bar{height:20px;border-radius:3px;margin:3px 0;position:relative;font-size:0.65em;line-height:20px;padding:0 5px;color:#fff;white-space:nowrap;overflow:hidden}
.legend-row{display:flex;gap:15px;flex-wrap:wrap;margin:10px 0}
.legend-item{display:flex;align-items:center;gap:5px;font-size:0.8em}
.legend-dot{width:12px;height:12px;border-radius:3px}
a.back{color:#58a6ff;text-decoration:none;font-size:0.85em}
p{color:#8b949e;font-size:0.85em;line-height:1.6;margin:8px 0}
.highlight{color:#c9d1d9}
</style>
</head><body>
<a class="back" href="/static/seattle-bookmarks.html">&larr; SDR Receiver</a> &nbsp;
<a class="back" href="/static/weatherfax/index.html">&larr; Weather Center</a>
<h1>SDR Station Documentation</h1>
<div class="subtitle">Complete hardware and software architecture</div>

<div class="nav">
<a href="#hardware">Hardware</a>
<a href="#diagram">System Diagram</a>
<a href="#radios">Radio Coverage</a>
<a href="#antennas">Antennas</a>
<a href="#network">Network</a>
<a href="#software">Software</a>
<a href="#frequencies">Frequency Map</a>
</div>

<!-- HARDWARE INVENTORY -->
<h2 id="hardware">Hardware Inventory</h2>
<div class="card-grid">

<div class="card">
<div class="title">Raspberry Pi 5</div>
<div class="type">Station Computer</div>
<div class="spec">
<b>CPU:</b> BCM2712 Quad-core ARM Cortex-A76 @ 2.4 GHz<br>
<b>RAM:</b> 8 GB LPDDR4X<br>
<b>OS:</b> DragonOS (Debian 13 trixie) aarch64<br>
<b>Storage:</b> microSD<br>
<b>Network:</b> Gigabit Ethernet to UniFi switch<br>
<b>USB:</b> 7-port powered hub attached<br>
<b>Role:</b> Runs OpenWebRX+ (Docker), all automation scripts
</div>
</div>

<div class="card">
<div class="title">SDRplay RSP1B</div>
<div class="type">HF/VHF/UHF Software Defined Radio</div>
<div class="spec">
<b>Range:</b> 1 kHz - 2 GHz<br>
<b>Bandwidth:</b> Up to 10 MHz<br>
<b>ADC:</b> 14-bit<br>
<b>Antenna:</b> MLA-30+ Active Loop (shared)<br>
<b>Connection:</b> USB via powered hub<br>
<b>Role:</b> HF browsing via OpenWebRX+, manual tuning
</div>
</div>

<div class="card">
<div class="title">KiwiSDR 2</div>
<div class="type">Dedicated HF Network SDR</div>
<div class="spec">
<b>Range:</b> 10 kHz - 30 MHz<br>
<b>Bandwidth:</b> 32 MHz (entire HF at once)<br>
<b>ADC:</b> 14-bit<br>
<b>Users:</b> 4 simultaneous<br>
<b>Antenna:</b> MLA-30+ Active Loop (shared via splitter)<br>
<b>Connection:</b> Ethernet to UniFi switch<br>
<b>Built-in:</b> GPS, web server, fax decoder, NAVTEX<br>
<b>Role:</b> Automated weather fax capture, NAVTEX, always-on HF
</div>
</div>

<div class="card">
<div class="title">Nooelec SMArt XTR v5</div>
<div class="type">RTL-SDR with E4000 Tuner</div>
<div class="spec">
<b>Range:</b> 52 MHz - 2174 MHz (gap 1088-1224)<br>
<b>Bandwidth:</b> 2.4 MHz<br>
<b>ADC:</b> 8-bit<br>
<b>Tuner:</b> Elonics E4000 (extended range)<br>
<b>Antenna:</b> Tram 1410 Discone<br>
<b>Connection:</b> USB via powered hub<br>
<b>Role:</b> VHF/UHF monitoring, FM, aviation, ISM, GPS, Iridium
</div>
</div>

<div class="card">
<div class="title">Nooelec NESDR SMArt v5</div>
<div class="type">RTL-SDR with R820T Tuner</div>
<div class="spec">
<b>Range:</b> 24 MHz - 1766 MHz<br>
<b>Bandwidth:</b> 2.4 MHz<br>
<b>ADC:</b> 8-bit<br>
<b>Tuner:</b> Rafael Micro R820T (best sensitivity)<br>
<b>Antenna:</b> Rooftop AM/FM/VHF/UHF<br>
<b>Connection:</b> USB via powered hub<br>
<b>Role:</b> Marine, public safety, P25, ADS-B, pagers, amateur
</div>
</div>

<div class="card">
<div class="title">7-Port Powered USB Hub</div>
<div class="type">USB Infrastructure</div>
<div class="spec">
<b>Ports:</b> 7x USB 3.0<br>
<b>Power:</b> External power supply<br>
<b>Connected to:</b> Raspberry Pi 5 USB port<br>
<b>Devices:</b> RSP1B, E4000 RTL-SDR, R820T RTL-SDR<br>
<b>Role:</b> Stable power delivery to all SDR dongles
</div>
</div>

<div class="card">
<div class="title">UniFi 8-Port PoE Switch</div>
<div class="type">Network Infrastructure</div>
<div class="spec">
<b>Ports:</b> 8x Gigabit Ethernet with PoE<br>
<b>Connected:</b> Raspberry Pi, KiwiSDR 2, home network<br>
<b>Role:</b> Network backbone for all SDR devices and web access
</div>
</div>

</div>

<!-- SYSTEM DIAGRAM -->
<h2 id="diagram">System Diagram</h2>
<div class="diagram-container">
<svg viewBox="0 0 1000 700" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:1000px;margin:0 auto;display:block">
<!-- Background -->
<rect width="1000" height="700" fill="#0d1117"/>

<!-- Title -->
<text x="500" y="30" fill="#58a6ff" font-size="16" text-anchor="middle" font-weight="bold">SDR Station Architecture</text>

<!-- ANTENNAS (top) -->
<text x="160" y="60" fill="#f0883e" font-size="11" text-anchor="middle" font-weight="bold">ANTENNAS (Attic)</text>

<!-- MLA-30+ -->
<rect x="30" y="75" width="120" height="55" rx="8" fill="#1a3a1a" stroke="#3fb950" stroke-width="2"/>
<text x="90" y="95" fill="#3fb950" font-size="10" text-anchor="middle" font-weight="bold">MLA-30+</text>
<text x="90" y="108" fill="#8b949e" font-size="8" text-anchor="middle">Active Loop</text>
<text x="90" y="120" fill="#8b949e" font-size="8" text-anchor="middle">0.5-30 MHz</text>

<!-- Tram 1410 -->
<rect x="170" y="75" width="120" height="55" rx="8" fill="#1a2a3a" stroke="#58a6ff" stroke-width="2"/>
<text x="230" y="95" fill="#58a6ff" font-size="10" text-anchor="middle" font-weight="bold">Tram 1410</text>
<text x="230" y="108" fill="#8b949e" font-size="8" text-anchor="middle">Discone</text>
<text x="230" y="120" fill="#8b949e" font-size="8" text-anchor="middle">25-1300 MHz</text>

<!-- Rooftop -->
<rect x="310" y="75" width="120" height="55" rx="8" fill="#2a1a3a" stroke="#a371f7" stroke-width="2"/>
<text x="370" y="95" fill="#a371f7" font-size="10" text-anchor="middle" font-weight="bold">Rooftop Antenna</text>
<text x="370" y="108" fill="#8b949e" font-size="8" text-anchor="middle">AM/FM/VHF/UHF</text>
<text x="370" y="120" fill="#8b949e" font-size="8" text-anchor="middle">Broadband</text>

<!-- Splitter -->
<rect x="55" y="155" width="70" height="30" rx="5" fill="#21262d" stroke="#484f58" stroke-width="1"/>
<text x="90" y="174" fill="#c9d1d9" font-size="8" text-anchor="middle">BNC Splitter</text>

<!-- Antenna cables -->
<line x1="90" y1="130" x2="90" y2="155" stroke="#3fb950" stroke-width="2"/>
<line x1="230" y1="130" x2="230" y2="250" stroke="#58a6ff" stroke-width="2"/>
<line x1="370" y1="130" x2="370" y2="350" stroke="#a371f7" stroke-width="2"/>

<!-- Splitter outputs -->
<line x1="70" y1="185" x2="70" y2="250" stroke="#3fb950" stroke-width="1.5" stroke-dasharray="4,2"/>
<line x1="110" y1="185" x2="110" y2="250" stroke="#3fb950" stroke-width="1.5" stroke-dasharray="4,2"/>

<!-- SDR DEVICES (middle) -->
<text x="250" y="240" fill="#f0883e" font-size="11" text-anchor="middle" font-weight="bold">SDR RECEIVERS</text>

<!-- KiwiSDR 2 -->
<rect x="20" y="255" width="140" height="70" rx="8" fill="#2d1a0e" stroke="#f0883e" stroke-width="2"/>
<text x="90" y="275" fill="#f0883e" font-size="11" text-anchor="middle" font-weight="bold">KiwiSDR 2</text>
<text x="90" y="290" fill="#c9d1d9" font-size="8" text-anchor="middle">10 kHz - 30 MHz</text>
<text x="90" y="302" fill="#8b949e" font-size="8" text-anchor="middle">32 MHz bandwidth</text>
<text x="90" y="314" fill="#3fb950" font-size="7" text-anchor="middle">Fax / NAVTEX / GPS</text>

<!-- RSP1B -->
<rect x="180" y="255" width="140" height="70" rx="8" fill="#1a0e2d" stroke="#9c27b0" stroke-width="2"/>
<text x="250" y="275" fill="#9c27b0" font-size="11" text-anchor="middle" font-weight="bold">SDRplay RSP1B</text>
<text x="250" y="290" fill="#c9d1d9" font-size="8" text-anchor="middle">1 kHz - 2 GHz</text>
<text x="250" y="302" fill="#8b949e" font-size="8" text-anchor="middle">10 MHz bandwidth, 14-bit</text>
<text x="250" y="314" fill="#3fb950" font-size="7" text-anchor="middle">HF Browsing</text>

<!-- E4000 -->
<rect x="180" y="345" width="140" height="70" rx="8" fill="#1a2a0e" stroke="#ff9800" stroke-width="2"/>
<text x="250" y="365" fill="#ff9800" font-size="11" text-anchor="middle" font-weight="bold">E4000 RTL-SDR</text>
<text x="250" y="380" fill="#c9d1d9" font-size="8" text-anchor="middle">52 MHz - 2174 MHz</text>
<text x="250" y="392" fill="#8b949e" font-size="8" text-anchor="middle">SMArt XTR v5</text>
<text x="250" y="404" fill="#3fb950" font-size="7" text-anchor="middle">VHF/UHF/FM/Aviation</text>

<!-- R820T -->
<rect x="340" y="345" width="140" height="70" rx="8" fill="#0e1a2d" stroke="#2196f3" stroke-width="2"/>
<text x="410" y="365" fill="#2196f3" font-size="11" text-anchor="middle" font-weight="bold">R820T RTL-SDR</text>
<text x="410" y="380" fill="#c9d1d9" font-size="8" text-anchor="middle">24 MHz - 1766 MHz</text>
<text x="410" y="392" fill="#8b949e" font-size="8" text-anchor="middle">NESDR SMArt v5</text>
<text x="410" y="404" fill="#3fb950" font-size="7" text-anchor="middle">Marine/P25/ADS-B</text>

<!-- Antenna to E4000 -->
<line x1="230" y1="250" x2="250" y2="345" stroke="#58a6ff" stroke-width="1.5"/>
<!-- Antenna to R820T -->
<line x1="370" y1="250" x2="410" y2="345" stroke="#a371f7" stroke-width="1.5"/>

<!-- INFRASTRUCTURE (bottom) -->
<text x="700" y="240" fill="#f0883e" font-size="11" text-anchor="middle" font-weight="bold">INFRASTRUCTURE</text>

<!-- 7-Port USB Hub -->
<rect x="540" y="345" width="160" height="60" rx="8" fill="#21262d" stroke="#484f58" stroke-width="2"/>
<text x="620" y="368" fill="#c9d1d9" font-size="10" text-anchor="middle" font-weight="bold">7-Port Powered USB Hub</text>
<text x="620" y="383" fill="#8b949e" font-size="8" text-anchor="middle">USB 3.0 | External Power</text>
<text x="620" y="395" fill="#484f58" font-size="7" text-anchor="middle">RSP1B + E4000 + R820T</text>

<!-- USB cables from hub to SDRs -->
<line x1="540" y1="375" x2="320" y2="310" stroke="#484f58" stroke-width="1" stroke-dasharray="3,2"/>
<text x="435" y="335" fill="#484f58" font-size="7" transform="rotate(-15, 435, 335)">USB</text>
<line x1="540" y1="380" x2="320" y2="380" stroke="#484f58" stroke-width="1" stroke-dasharray="3,2"/>
<text x="435" y="375" fill="#484f58" font-size="7">USB</text>
<line x1="540" y1="385" x2="480" y2="385" stroke="#484f58" stroke-width="1" stroke-dasharray="3,2"/>
<text x="505" y="395" fill="#484f58" font-size="7">USB</text>

<!-- Raspberry Pi 5 -->
<rect x="540" y="450" width="200" height="80" rx="10" fill="#0d2818" stroke="#3fb950" stroke-width="2"/>
<text x="640" y="475" fill="#3fb950" font-size="13" text-anchor="middle" font-weight="bold">Raspberry Pi 5</text>
<text x="640" y="492" fill="#c9d1d9" font-size="9" text-anchor="middle">8 GB RAM | DragonOS</text>
<text x="640" y="505" fill="#8b949e" font-size="8" text-anchor="middle">OpenWebRX+ (Docker)</text>
<text x="640" y="518" fill="#8b949e" font-size="8" text-anchor="middle">Automation Scripts | Watchdog</text>

<!-- USB from Pi to Hub -->
<line x1="620" y1="450" x2="620" y2="405" stroke="#3fb950" stroke-width="2"/>
<text x="630" y="430" fill="#3fb950" font-size="7">USB 3.0</text>

<!-- UniFi Switch -->
<rect x="540" y="570" width="200" height="60" rx="8" fill="#1a1a2d" stroke="#58a6ff" stroke-width="2"/>
<text x="640" y="593" fill="#58a6ff" font-size="11" text-anchor="middle" font-weight="bold">UniFi 8-Port PoE Switch</text>
<text x="640" y="608" fill="#8b949e" font-size="8" text-anchor="middle">Gigabit Ethernet | PoE</text>
<text x="640" y="620" fill="#484f58" font-size="7" text-anchor="middle">Pi + KiwiSDR + Home Network</text>

<!-- Ethernet from Pi to Switch -->
<line x1="640" y1="530" x2="640" y2="570" stroke="#58a6ff" stroke-width="2"/>
<text x="655" y="555" fill="#58a6ff" font-size="7">Gigabit ETH</text>

<!-- Ethernet from KiwiSDR to Switch -->
<line x1="90" y1="325" x2="90" y2="600" stroke="#f0883e" stroke-width="1.5" stroke-dasharray="4,2"/>
<line x1="90" y1="600" x2="540" y2="600" stroke="#f0883e" stroke-width="1.5" stroke-dasharray="4,2"/>
<text x="300" y="595" fill="#f0883e" font-size="7">Ethernet to Switch</text>

<!-- Network / Internet -->
<rect x="820" y="570" width="160" height="60" rx="8" fill="#21262d" stroke="#484f58" stroke-width="1"/>
<text x="900" y="593" fill="#c9d1d9" font-size="10" text-anchor="middle" font-weight="bold">Home Network</text>
<text x="900" y="608" fill="#8b949e" font-size="8" text-anchor="middle">Router / Internet</text>
<text x="900" y="620" fill="#484f58" font-size="7" text-anchor="middle">Web access on LAN</text>
<line x1="740" y1="600" x2="820" y2="600" stroke="#484f58" stroke-width="1.5"/>

<!-- WEB SERVICES -->
<rect x="800" y="440" width="180" height="100" rx="8" fill="#161b22" stroke="#21262d" stroke-width="1"/>
<text x="890" y="462" fill="#58a6ff" font-size="10" text-anchor="middle" font-weight="bold">Web Services</text>
<text x="890" y="480" fill="#3fb950" font-size="8" text-anchor="middle">:8073 OpenWebRX+</text>
<text x="890" y="494" fill="#3fb950" font-size="8" text-anchor="middle">:8073/static/* Bookmarks</text>
<text x="890" y="508" fill="#3fb950" font-size="8" text-anchor="middle">:8073/static/weatherfax/*</text>
<text x="890" y="522" fill="#f0883e" font-size="8" text-anchor="middle">:8074 KiwiSDR Web UI</text>

<line x1="800" y1="490" x2="740" y2="490" stroke="#21262d" stroke-width="1" stroke-dasharray="3,2"/>

<!-- Legend -->
<text x="30" y="660" fill="#484f58" font-size="8">Solid lines = coax/antenna cables | Dashed lines = USB/Ethernet data | Colors match antenna assignment</text>
<text x="30" y="675" fill="#484f58" font-size="8">Green = MLA-30+ HF path | Blue = Tram Discone VHF/UHF | Purple = Rooftop antenna | Orange = KiwiSDR Ethernet</text>

</svg>
</div>

<!-- RADIO COVERAGE -->
<h2 id="radios">Radio Coverage Detail</h2>
<table>
<tr><th>Radio</th><th>Antenna</th><th>Frequency Range</th><th>Bandwidth</th><th>Primary Role</th></tr>
<tr><td style="color:#f0883e;font-weight:bold">KiwiSDR 2</td><td>MLA-30+ (shared)</td><td>10 kHz - 30 MHz</td><td>32 MHz (all HF)</td><td>Automated fax/NAVTEX capture, 4-user web UI</td></tr>
<tr><td style="color:#9c27b0;font-weight:bold">SDRplay RSP1B</td><td>MLA-30+ (shared)</td><td>1 kHz - 2 GHz</td><td>Up to 10 MHz</td><td>HF browsing, manual tuning, VHF/UHF backup</td></tr>
<tr><td style="color:#ff9800;font-weight:bold">E4000 RTL-SDR</td><td>Tram 1410 Discone</td><td>52 - 2174 MHz</td><td>2.4 MHz</td><td>FM, aviation, VHF, ISM, GPS, Iridium</td></tr>
<tr><td style="color:#2196f3;font-weight:bold">R820T RTL-SDR</td><td>Rooftop Antenna</td><td>24 - 1766 MHz</td><td>2.4 MHz</td><td>Marine, P25, ADS-B, pagers, amateur, transit</td></tr>
</table>

<!-- FREQUENCY MAP -->
<h2 id="frequencies">Frequency Coverage Map</h2>
<p>Visual representation of which radio covers which frequencies. Overlapping coverage provides redundancy.</p>

<div style="background:#161b22;border:1px solid #21262d;border-radius:8px;padding:15px;margin:15px 0">
<div style="font-size:0.75em;color:#484f58;margin-bottom:10px">0 ←──────── Frequency ──────────→ 2 GHz</div>

<div style="margin:5px 0"><span style="color:#f0883e;font-size:0.8em;display:inline-block;width:100px">KiwiSDR 2</span>
<div class="freq-bar" style="background:linear-gradient(90deg,#f0883e,#f0883e);width:1.5%;margin-left:0;display:inline-block">0-30 MHz</div></div>

<div style="margin:5px 0"><span style="color:#9c27b0;font-size:0.8em;display:inline-block;width:100px">RSP1B</span>
<div class="freq-bar" style="background:linear-gradient(90deg,#9c27b0,#7b1fa2);width:100%;display:inline-block">1 kHz ───────────────────────────────── 2 GHz</div></div>

<div style="margin:5px 0"><span style="color:#ff9800;font-size:0.8em;display:inline-block;width:100px">E4000</span>
<div class="freq-bar" style="background:#ff9800;width:97%;margin-left:2.6%;display:inline-block">52 MHz ─────────────────────────── 2174 MHz</div></div>

<div style="margin:5px 0"><span style="color:#2196f3;font-size:0.8em;display:inline-block;width:100px">R820T</span>
<div class="freq-bar" style="background:#2196f3;width:87%;margin-left:1.2%;display:inline-block">24 MHz ────────────────────── 1766 MHz</div></div>
</div>

<!-- ANTENNAS -->
<h2 id="antennas">Antenna Details</h2>
<div class="card-grid">
<div class="card">
<div class="title">MLA-30+ Active Magnetic Loop</div>
<div class="type">HF Reception | Attic Mounted</div>
<div class="spec">
<b>Range:</b> 0.5 - 30 MHz<br>
<b>Type:</b> Active (requires DC power via inserter)<br>
<b>Feeds:</b> RSP1B + KiwiSDR 2 (via BNC splitter)<br>
<b>Best for:</b> Shortwave broadcast, weather fax, amateur HF, NAVTEX, AM broadcast<br>
<b>Location:</b> Attic
</div>
</div>

<div class="card">
<div class="title">Tram 1410 Super Discone</div>
<div class="type">VHF/UHF Wideband | Attic Mounted</div>
<div class="spec">
<b>Range:</b> 25 - 1300 MHz<br>
<b>Type:</b> Passive wideband<br>
<b>Feeds:</b> E4000 RTL-SDR<br>
<b>Best for:</b> Aviation, FM broadcast, marine VHF, ISM bands, satellites<br>
<b>Location:</b> Attic
</div>
</div>

<div class="card">
<div class="title">Rooftop AM/FM/VHF/UHF</div>
<div class="type">Broadband | Attic Mounted</div>
<div class="spec">
<b>Range:</b> VHF/UHF broadband<br>
<b>Type:</b> Passive<br>
<b>Feeds:</b> R820T RTL-SDR<br>
<b>Best for:</b> Public safety, P25 800 MHz, ADS-B, pagers, transit<br>
<b>Location:</b> Attic
</div>
</div>
</div>

<!-- NETWORK -->
<h2 id="network">Network Topology</h2>
<table>
<tr><th>Device</th><th>Connection</th><th>IP</th><th>Port(s)</th></tr>
<tr><td>Raspberry Pi 5</td><td>Gigabit Ethernet → UniFi Switch</td><td>172.31.255.48</td><td>8073 (OpenWebRX+)</td></tr>
<tr><td>KiwiSDR 2</td><td>Ethernet → UniFi Switch</td><td>TBD (DHCP)</td><td>8074 (KiwiSDR UI)</td></tr>
<tr><td>RSP1B</td><td>USB → Powered Hub → Pi</td><td>—</td><td>Via OpenWebRX+</td></tr>
<tr><td>E4000 RTL-SDR</td><td>USB → Powered Hub → Pi</td><td>—</td><td>Via OpenWebRX+</td></tr>
<tr><td>R820T RTL-SDR</td><td>USB → Powered Hub → Pi</td><td>—</td><td>Via OpenWebRX+</td></tr>
<tr><td>UniFi Switch</td><td>Uplink → Home Router</td><td>—</td><td>LAN backbone</td></tr>
</table>

<!-- SOFTWARE -->
<h2 id="software">Software Stack</h2>
<table>
<tr><th>Component</th><th>Version</th><th>Role</th></tr>
<tr><td>OpenWebRX+ (Docker)</td><td>v1.2.111 softmbe</td><td>Web SDR receiver with digital voice decoding</td></tr>
<tr><td>Docker</td><td>docker.io</td><td>Container runtime for OpenWebRX+</td></tr>
<tr><td>SoapySDR</td><td>0.8.0</td><td>Hardware abstraction for RSP1B</td></tr>
<tr><td>SDRplay API</td><td>3.15</td><td>RSP1B driver</td></tr>
<tr><td>rtl-sdr</td><td>librtlsdr</td><td>RTL-SDR dongle driver</td></tr>
<tr><td>multimon-ng</td><td>—</td><td>POCSAG/FLEX pager, EAS, SITOR-B decoder</td></tr>
<tr><td>dump1090</td><td>8.2</td><td>ADS-B aircraft decoder</td></tr>
<tr><td>kiwiclient</td><td>—</td><td>KiwiSDR remote recording/fax capture</td></tr>
<tr><td>sox</td><td>14.4.2</td><td>Audio processing</td></tr>
<tr><td>scipy/numpy</td><td>—</td><td>Signal processing for captures</td></tr>
</table>

<h3>Automation</h3>
<table>
<tr><th>Task</th><th>Frequency</th><th>Method</th></tr>
<tr><td>Weather Fax Capture</td><td>21x/day (Pt Reyes + Kodiak)</td><td>KiwiSDR via kiwiclient</td></tr>
<tr><td>JMH Tokyo Fax</td><td>4x/day</td><td>KiwiSDR via kiwiclient</td></tr>
<tr><td>NAVTEX Monitoring</td><td>6x/day (every 4 hours)</td><td>KiwiSDR via kiwiclient</td></tr>
<tr><td>EAS Alert Monitoring</td><td>48x/day (every 30 min)</td><td>RTL-SDR + multimon-ng</td></tr>
<tr><td>Dashboard Refresh</td><td>Every 15 minutes</td><td>Python script</td></tr>
<tr><td>Station Watchdog</td><td>Every 5 minutes</td><td>Bash health check</td></tr>
<tr><td>Full Band Scan</td><td>Weekly (Saturday 23:00 UTC)</td><td>rtl_power + soapy_power</td></tr>
<tr><td>Schedule Conflict Check</td><td>Weekly</td><td>Python crontab analyzer</td></tr>
</table>

<div style="text-align:center;margin-top:30px;color:#484f58;font-size:0.8em">
<p>Seattle SDR Station | 481 bookmarks | 4 radios | 3 antennas</p>
<p><a href="https://github.com/deviros123/sdr-station-kit" style="color:#58a6ff">github.com/deviros123/sdr-station-kit</a></p>
</div>

</body></html>"""

with open("/home/dragon/weatherfax/station.html", "w") as f:
    f.write(html)
print("Station documentation page generated")
