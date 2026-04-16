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
<svg viewBox="0 0 960 780" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:960px;margin:0 auto;display:block">
<rect width="960" height="780" fill="#0d1117"/>
<text x="480" y="25" fill="#58a6ff" font-size="15" text-anchor="middle" font-weight="bold">SDR Station Architecture</text>

<!-- ===== ROW 1: ANTENNAS ===== -->
<text x="420" y="55" fill="#f0883e" font-size="11" text-anchor="middle" font-weight="bold">ANTENNAS (Attic)</text>

<rect x="55" y="70" width="130" height="50" rx="8" fill="#1a3a1a" stroke="#3fb950" stroke-width="2"/>
<text x="120" y="90" fill="#3fb950" font-size="10" text-anchor="middle" font-weight="bold">MLA-30+</text>
<text x="120" y="103" fill="#8b949e" font-size="8" text-anchor="middle">Active Loop 0.5-30 MHz</text>

<rect x="350" y="70" width="130" height="50" rx="8" fill="#1a2a3a" stroke="#ff9800" stroke-width="2"/>
<text x="415" y="90" fill="#ff9800" font-size="10" text-anchor="middle" font-weight="bold">Tram 1410 Discone</text>
<text x="415" y="103" fill="#8b949e" font-size="8" text-anchor="middle">25-1300 MHz</text>

<rect x="635" y="70" width="130" height="50" rx="8" fill="#2a1a3a" stroke="#2196f3" stroke-width="2"/>
<text x="700" y="90" fill="#2196f3" font-size="10" text-anchor="middle" font-weight="bold">Rooftop Antenna</text>
<text x="700" y="103" fill="#8b949e" font-size="8" text-anchor="middle">AM/FM/VHF/UHF</text>

<!-- Splitter -->
<rect x="85" y="148" width="70" height="26" rx="5" fill="#21262d" stroke="#484f58" stroke-width="1"/>
<text x="120" y="165" fill="#c9d1d9" font-size="8" text-anchor="middle">BNC Splitter</text>
<line x1="120" y1="120" x2="120" y2="148" stroke="#3fb950" stroke-width="2"/>

<!-- ===== ROW 2: SDR RECEIVERS (spaced apart) ===== -->
<text x="420" y="208" fill="#f0883e" font-size="11" text-anchor="middle" font-weight="bold">SDR RECEIVERS</text>

<!-- KiwiSDR at x=55 -->
<rect x="15" y="220" width="145" height="65" rx="8" fill="#2d1a0e" stroke="#f0883e" stroke-width="2"/>
<text x="87" y="240" fill="#f0883e" font-size="10" text-anchor="middle" font-weight="bold">KiwiSDR 2</text>
<text x="87" y="253" fill="#c9d1d9" font-size="8" text-anchor="middle">10 kHz - 30 MHz</text>
<text x="87" y="265" fill="#8b949e" font-size="8" text-anchor="middle">32 MHz BW | 14-bit</text>
<text x="87" y="277" fill="#3fb950" font-size="7" text-anchor="middle">Fax / NAVTEX / GPS</text>

<!-- RSP1B at x=230 (gap from KiwiSDR) -->
<rect x="195" y="220" width="145" height="65" rx="8" fill="#1a0e2d" stroke="#9c27b0" stroke-width="2"/>
<text x="267" y="240" fill="#9c27b0" font-size="10" text-anchor="middle" font-weight="bold">SDRplay RSP1B</text>
<text x="267" y="253" fill="#c9d1d9" font-size="8" text-anchor="middle">1 kHz - 2 GHz</text>
<text x="267" y="265" fill="#8b949e" font-size="8" text-anchor="middle">10 MHz BW | 14-bit</text>
<text x="267" y="277" fill="#3fb950" font-size="7" text-anchor="middle">HF Browsing</text>

<!-- E4000 at x=415 (clear gap from RSP1B) -->
<rect x="380" y="220" width="145" height="65" rx="8" fill="#1a2a0e" stroke="#ff9800" stroke-width="2"/>
<text x="452" y="240" fill="#ff9800" font-size="10" text-anchor="middle" font-weight="bold">E4000 RTL-SDR</text>
<text x="452" y="253" fill="#c9d1d9" font-size="8" text-anchor="middle">52 - 2174 MHz</text>
<text x="452" y="265" fill="#8b949e" font-size="8" text-anchor="middle">SMArt XTR v5</text>
<text x="452" y="277" fill="#3fb950" font-size="7" text-anchor="middle">VHF/UHF/FM/Aviation</text>

<!-- R820T at x=600 (clear gap from E4000) -->
<rect x="565" y="220" width="145" height="65" rx="8" fill="#0e1a2d" stroke="#2196f3" stroke-width="2"/>
<text x="637" y="240" fill="#2196f3" font-size="10" text-anchor="middle" font-weight="bold">R820T RTL-SDR</text>
<text x="637" y="253" fill="#c9d1d9" font-size="8" text-anchor="middle">24 - 1766 MHz</text>
<text x="637" y="265" fill="#8b949e" font-size="8" text-anchor="middle">NESDR SMArt v5</text>
<text x="637" y="277" fill="#3fb950" font-size="7" text-anchor="middle">Marine/P25/ADS-B</text>

<!-- ===== ANTENNA TO SDR CONNECTIONS ===== -->
<!-- Splitter left to KiwiSDR -->
<line x1="100" y1="174" x2="87" y2="220" stroke="#3fb950" stroke-width="2"/>
<text x="68" y="200" fill="#3fb950" font-size="7">RG-174</text>
<!-- Splitter right to RSP1B -->
<line x1="140" y1="174" x2="267" y2="220" stroke="#3fb950" stroke-width="2"/>
<text x="180" y="192" fill="#3fb950" font-size="7">RG-174</text>
<!-- MLA-30+ to splitter label -->
<text x="130" y="138" fill="#3fb950" font-size="7">RG-174</text>
<!-- Tram down to E4000 -->
<line x1="415" y1="120" x2="452" y2="220" stroke="#ff9800" stroke-width="2"/>
<text x="425" y="175" fill="#ff9800" font-size="7">RG-174</text>
<!-- Rooftop down to R820T -->
<line x1="700" y1="120" x2="637" y2="220" stroke="#2196f3" stroke-width="2"/>
<text x="670" y="175" fill="#2196f3" font-size="7">RG-6</text>

<!-- ===== ROW 3: USB HUB (below SDRs) ===== -->
<rect x="230" y="330" width="400" height="45" rx="8" fill="#21262d" stroke="#484f58" stroke-width="2"/>
<text x="430" y="350" fill="#c9d1d9" font-size="10" text-anchor="middle" font-weight="bold">7-Port Powered USB Hub</text>
<text x="430" y="365" fill="#8b949e" font-size="8" text-anchor="middle">USB 3.0 | External Power Supply</text>

<!-- USB lines from SDRs down to hub -->
<line x1="267" y1="285" x2="310" y2="330" stroke="#484f58" stroke-width="1.5" stroke-dasharray="3,2"/>
<line x1="452" y1="285" x2="430" y2="330" stroke="#484f58" stroke-width="1.5" stroke-dasharray="3,2"/>
<line x1="637" y1="285" x2="550" y2="330" stroke="#484f58" stroke-width="1.5" stroke-dasharray="3,2"/>
<text x="280" y="312" fill="#484f58" font-size="7">USB</text>
<text x="445" y="312" fill="#484f58" font-size="7">USB</text>
<text x="600" y="312" fill="#484f58" font-size="7">USB</text>

<!-- ===== ROW 4: RASPBERRY PI ===== -->
<rect x="320" y="420" width="220" height="70" rx="10" fill="#0d2818" stroke="#3fb950" stroke-width="2"/>
<text x="430" y="445" fill="#3fb950" font-size="13" text-anchor="middle" font-weight="bold">Raspberry Pi 5</text>
<text x="430" y="460" fill="#c9d1d9" font-size="8" text-anchor="middle">8 GB RAM | DragonOS aarch64</text>
<text x="430" y="473" fill="#8b949e" font-size="8" text-anchor="middle">OpenWebRX+ (Docker) | Automation | Watchdog</text>
<text x="430" y="485" fill="#484f58" font-size="7" text-anchor="middle">172.31.255.48</text>

<!-- USB hub down to Pi -->
<line x1="430" y1="375" x2="430" y2="420" stroke="#3fb950" stroke-width="2"/>
<text x="445" y="400" fill="#3fb950" font-size="7">USB 3.0</text>

<!-- ===== ROW 5: SWITCH ===== -->
<rect x="320" y="535" width="220" height="50" rx="8" fill="#1a1a2d" stroke="#58a6ff" stroke-width="2"/>
<text x="430" y="555" fill="#58a6ff" font-size="10" text-anchor="middle" font-weight="bold">UniFi 8-Port PoE Switch</text>
<text x="430" y="570" fill="#8b949e" font-size="8" text-anchor="middle">Gigabit Ethernet | PoE</text>

<!-- Pi down to switch -->
<line x1="430" y1="490" x2="430" y2="535" stroke="#58a6ff" stroke-width="2"/>
<text x="445" y="515" fill="#58a6ff" font-size="7">Gigabit ETH</text>

<!-- KiwiSDR Ethernet to switch -->
<line x1="87" y1="285" x2="87" y2="555" stroke="#f0883e" stroke-width="1.5" stroke-dasharray="4,2"/>
<line x1="87" y1="555" x2="320" y2="555" stroke="#f0883e" stroke-width="1.5" stroke-dasharray="4,2"/>
<text x="200" y="550" fill="#f0883e" font-size="7">Ethernet</text>

<!-- Home Network -->
<rect x="320" y="625" width="220" height="45" rx="8" fill="#21262d" stroke="#484f58" stroke-width="1"/>
<text x="430" y="645" fill="#c9d1d9" font-size="10" text-anchor="middle" font-weight="bold">Home Network / Internet</text>
<text x="430" y="660" fill="#8b949e" font-size="8" text-anchor="middle">Router | LAN | Web Access</text>
<line x1="430" y1="585" x2="430" y2="625" stroke="#484f58" stroke-width="1.5"/>

<!-- Web Services -->
<rect x="750" y="420" width="180" height="115" rx="8" fill="#161b22" stroke="#21262d" stroke-width="1"/>
<text x="840" y="442" fill="#58a6ff" font-size="10" text-anchor="middle" font-weight="bold">Web Services</text>
<text x="840" y="460" fill="#3fb950" font-size="8" text-anchor="middle">:8073 OpenWebRX+</text>
<text x="840" y="474" fill="#3fb950" font-size="8" text-anchor="middle">:8073/static/* Bookmarks</text>
<text x="840" y="488" fill="#3fb950" font-size="8" text-anchor="middle">:8073/static/weatherfax/*</text>
<text x="840" y="502" fill="#3fb950" font-size="8" text-anchor="middle">:8073/.../station.html</text>
<text x="840" y="520" fill="#f0883e" font-size="8" text-anchor="middle">:8074 KiwiSDR Web UI</text>
<line x1="540" y1="455" x2="750" y2="470" stroke="#21262d" stroke-width="1" stroke-dasharray="3,2"/>

<!-- Legend -->
<rect x="20" y="700" width="920" height="55" rx="5" fill="#161b22" stroke="#21262d" stroke-width="1"/>
<text x="40" y="718" fill="#c9d1d9" font-size="9" font-weight="bold">Legend:</text>
<line x1="40" y1="732" x2="65" y2="732" stroke="#3fb950" stroke-width="2"/>
<text x="70" y="736" fill="#8b949e" font-size="8">MLA-30+ RG-174</text>
<line x1="195" y1="732" x2="220" y2="732" stroke="#ff9800" stroke-width="2"/>
<text x="225" y="736" fill="#8b949e" font-size="8">Tram RG-174</text>
<line x1="330" y1="732" x2="355" y2="732" stroke="#2196f3" stroke-width="2"/>
<text x="360" y="736" fill="#8b949e" font-size="8">Rooftop RG-6</text>
<line x1="460" y1="732" x2="485" y2="732" stroke="#484f58" stroke-width="1.5" stroke-dasharray="3,2"/>
<text x="490" y="736" fill="#8b949e" font-size="8">USB</text>
<line x1="530" y1="732" x2="555" y2="732" stroke="#f0883e" stroke-width="1.5" stroke-dasharray="4,2"/>
<text x="560" y="736" fill="#8b949e" font-size="8">Ethernet</text>
<line x1="630" y1="732" x2="655" y2="732" stroke="#58a6ff" stroke-width="2"/>
<text x="660" y="736" fill="#8b949e" font-size="8">Gigabit ETH</text>
<text x="40" y="748" fill="#484f58" font-size="7">Seattle, WA | All antennas attic-mounted | 4 SDR receivers | 3 antennas | 481 bookmarks</text>

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

<!-- STATION TODO / IMPROVEMENTS -->
<h2 id="todo">Station Improvements</h2>
<p>Track planned upgrades and their impact on performance. Check items off as completed.</p>

<div id="todo-list" style="margin:15px 0">
</div>

<script>
var todos = [];
var TODO_API = 'http://' + window.location.hostname + ':8075';

function loadTodos() {
    fetch(TODO_API + '/todos')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            todos = data;
            renderTodos();
        })
        .catch(function(e) {
            document.getElementById('todo-list').innerHTML = '<div style="color:#f85149;padding:20px;text-align:center">Todo API not responding on port 8075. Start it with: sudo systemctl start sdr-todo</div>';
        });
}

function saveTodos() {
    fetch(TODO_API + '/todos', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(todos)
    }).catch(function(e) { console.log('Save failed:', e); });
}

function renderTodos() {
    var container = document.getElementById('todo-list');
    var cats = {};
    todos.forEach(function(t) {
        if (!cats[t.category]) cats[t.category] = [];
        cats[t.category].push(t);
    });

    var html = '';
    var done_count = todos.filter(function(t){return t.done}).length;
    var total = todos.length;
    var pct = Math.round(100 * done_count / total);

    // Progress bar
    html += '<div style="background:#21262d;border-radius:8px;height:24px;margin:10px 0;overflow:hidden;position:relative">';
    html += '<div style="background:#3fb950;height:100%;width:' + pct + '%;transition:width 0.3s"></div>';
    html += '<div style="position:absolute;top:0;left:0;right:0;text-align:center;line-height:24px;font-size:0.8em;color:#c9d1d9">' + done_count + ' / ' + total + ' complete (' + pct + '%)</div>';
    html += '</div>';

    var catOrder = ['Hardware','Antenna','Calibration','Security','Software'];
    var catColors = {Hardware:'#f0883e',Antenna:'#3fb950',Calibration:'#58a6ff',Security:'#f85149',Software:'#a371f7'};

    catOrder.forEach(function(cat) {
        if (!cats[cat]) return;
        html += '<h3 style="color:' + (catColors[cat]||'#c9d1d9') + ';margin:15px 0 8px 0;font-size:0.95em">' + cat + '</h3>';

        cats[cat].forEach(function(t, i) {
            var opacity = t.done ? '0.6' : '1';
            var strike = t.done ? 'text-decoration:line-through' : '';
            var priColor = t.priority === 'High' ? '#f85149' : (t.priority === 'Medium' ? '#ffa657' : '#484f58');

            html += '<div style="background:#161b22;border:1px solid #21262d;border-radius:8px;padding:12px;margin:6px 0;opacity:' + opacity + '">';
            html += '<div style="display:flex;align-items:center;gap:8px">';
            html += '<input type="checkbox" ' + (t.done ? 'checked' : '') + ' onchange="toggleTodo(\'' + t.id + '\')" style="width:18px;height:18px;cursor:pointer">';
            html += '<span style="flex:1;' + strike + ';font-size:0.9em">' + t.text + '</span>';
            html += '<span style="color:' + priColor + ';font-size:0.7em;border:1px solid ' + priColor + ';padding:1px 6px;border-radius:3px">' + t.priority + '</span>';
            html += '</div>';
            html += '<div style="color:#8b949e;font-size:0.78em;margin:5px 0 0 26px">' + t.impact + '</div>';

            // Baseline & result fields
            html += '<div style="margin:8px 0 0 26px;display:flex;gap:8px;flex-wrap:wrap">';
            html += '<div style="flex:1;min-width:200px"><label style="color:#484f58;font-size:0.7em;display:block">Before (baseline measurement)</label>';
            html += '<input type="text" value="' + (t.baseline||'').replace(/"/g,'&quot;') + '" onchange="setBaseline(\'' + t.id + '\',this.value)" placeholder="e.g., ADS-B range 47 miles, SNR 35 dB" style="width:100%;background:#0d1117;border:1px solid #30363d;color:#c9d1d9;padding:4px 6px;border-radius:4px;font-size:0.8em"></div>';
            html += '<div style="flex:1;min-width:200px"><label style="color:#484f58;font-size:0.7em;display:block">After (result)</label>';
            html += '<input type="text" value="' + (t.result||'').replace(/"/g,'&quot;') + '" onchange="setResult(\'' + t.id + '\',this.value)" placeholder="e.g., ADS-B range 156 miles, SNR 42 dB" style="width:100%;background:#0d1117;border:1px solid #30363d;color:#c9d1d9;padding:4px 6px;border-radius:4px;font-size:0.8em"></div>';
            html += '</div>';

            html += '</div>';
        });
    });

    container.innerHTML = html;
}

function toggleTodo(id) {
    todos.forEach(function(t) { if (t.id === id) t.done = !t.done; });
    saveTodos();
    renderTodos();
}

function setBaseline(id, val) {
    todos.forEach(function(t) { if (t.id === id) t.baseline = val; });
    saveTodos();
}

function setResult(id, val) {
    todos.forEach(function(t) { if (t.id === id) t.result = val; });
    saveTodos();
}

loadTodos();
</script>

<div style="text-align:center;margin-top:30px;color:#484f58;font-size:0.8em">
<p>Seattle SDR Station | 481 bookmarks | 4 radios | 3 antennas</p>
<p><a href="https://github.com/deviros123/sdr-station-kit" style="color:#58a6ff">github.com/deviros123/sdr-station-kit</a></p>
</div>

</body></html>"""

with open("/home/dragon/weatherfax/station.html", "w") as f:
    f.write(html)
print("Station documentation page generated")
