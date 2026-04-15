#!/usr/bin/env python3
"""Generate comprehensive weather dashboard HTML page."""
import os
import glob
import json
from datetime import datetime

WXDIR = "/home/dragon/weatherfax"
NAVTEX_LOG = "/home/dragon/weather-text/navtex.log"
SITORB_LOG = "/home/dragon/weather-text/sitorb.log"
DSC_LOG = "/home/dragon/weather-text/dsc.log"
EAS_LOG = "/home/dragon/weather-text/eas.log"

HTMLFILE = os.path.join(WXDIR, "index.html")

def read_log(path, max_entries=50):
    """Read log entries, newest first."""
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            lines = f.readlines()
        # Each entry separated by blank line or ---
        entries = []
        current = []
        for line in lines:
            line = line.rstrip()
            if line == "---" or line == "":
                if current:
                    entries.append("\n".join(current))
                    current = []
            else:
                current.append(line)
        if current:
            entries.append("\n".join(current))
        return entries[-max_entries:][::-1]  # newest first
    except:
        return []

latest_fax = sorted(glob.glob(os.path.join(WXDIR, "latest", "*.png")))
archive_fax = sorted(glob.glob(os.path.join(WXDIR, "images", "*.png")), reverse=True)[:200]
navtex = read_log(NAVTEX_LOG)
sitorb = read_log(SITORB_LOG)
dsc = read_log(DSC_LOG)
eas = read_log(EAS_LOG)

html = """<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Seattle SDR Weather Center</title>
<meta http-equiv="refresh" content="300">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:sans-serif;background:#0d1117;color:#c9d1d9;padding:20px}
h1{color:#58a6ff;text-align:center;margin-bottom:5px}
.subtitle{text-align:center;color:#484f58;margin-bottom:15px;font-size:0.85em}
h2{color:#f0883e;border-bottom:1px solid #21262d;padding-bottom:5px;margin:20px 0 10px 0}
.tabs{display:flex;gap:0;border-bottom:2px solid #21262d;margin-bottom:15px}
.tab{padding:8px 16px;cursor:pointer;color:#484f58;border-bottom:2px solid transparent;margin-bottom:-2px;font-size:0.9em}
.tab:hover{color:#c9d1d9}
.tab.active{color:#58a6ff;border-bottom-color:#58a6ff}
.panel{display:none}
.panel.active{display:block}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:12px;margin:10px 0}
.card{background:#161b22;border:1px solid #21262d;border-radius:8px;overflow:hidden}
.card img{width:100%;display:block;cursor:pointer}
.card img:hover{opacity:0.85}
.card .info{padding:6px 10px;font-size:0.8em}
.card .name{color:#58a6ff;font-weight:bold}
.card .time{color:#484f58;font-size:0.75em}
.text-log{background:#161b22;border:1px solid #21262d;border-radius:8px;max-height:600px;overflow-y:auto;padding:10px;margin:10px 0}
.text-entry{border-bottom:1px solid #21262d;padding:8px 0;font-family:monospace;font-size:0.78em;white-space:pre-wrap;word-wrap:break-word;color:#8b949e}
.text-entry:last-child{border-bottom:none}
.text-entry .timestamp{color:#58a6ff;font-weight:bold}
.text-entry .alert{color:#f85149}
.text-entry .warning{color:#ffa657}
.empty{text-align:center;color:#484f58;padding:30px;font-style:italic}
.stats{display:flex;gap:15px;justify-content:center;flex-wrap:wrap;margin:10px 0}
.stat{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:10px 20px;text-align:center}
.stat .num{color:#58a6ff;font-size:1.5em;font-weight:bold}
.stat .label{color:#484f58;font-size:0.75em}
.filter-bar{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}
.filter-bar select,.filter-bar input{background:#0d1117;border:1px solid #30363d;color:#c9d1d9;padding:5px 8px;border-radius:4px;font-size:0.85em}
a.back{color:#58a6ff;text-decoration:none;font-size:0.85em}
a.back:hover{text-decoration:underline}
.cd,.cd-multi{font-family:monospace;font-size:1em;color:#c9d1d9}
.cd-soon{color:#3fb950;font-weight:bold;font-size:1.05em}
.cd-active{color:#f0883e;font-weight:bold;font-size:1.05em;animation:pulse 1s infinite}
.cd-later{color:#c9d1d9}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
.next-up{background:#0d2818;border:1px solid #1a4d2e;border-radius:8px;padding:12px;margin:10px 0;text-align:center}
.next-up .label{color:#484f58;font-size:0.8em}
.next-up .value{color:#3fb950;font-size:1.3em;font-weight:bold;font-family:monospace}
.next-up .chart{color:#58a6ff;font-size:0.9em}
</style></head><body>
<a class="back" href="/static/seattle-bookmarks.html">&larr; Back to SDR Receiver</a>
<h1>Seattle SDR Weather Center</h1>
<div class="subtitle">Automated weather data from HF radiofax and digital text broadcasts</div>
"""

# Stats
html += '<div class="stats">'
html += '<div class="stat"><div class="num">%d</div><div class="label">Fax Charts</div></div>' % (len(latest_fax) + len(archive_fax))
html += '<div class="stat"><div class="num">%d</div><div class="label">NAVTEX Messages</div></div>' % len(navtex)
html += '<div class="stat"><div class="num">%d</div><div class="label">SITOR-B Messages</div></div>' % len(sitorb)
html += '<div class="stat"><div class="num">%d</div><div class="label">DSC Alerts</div></div>' % len(dsc)
html += '<div class="stat"><div class="num">%d</div><div class="label">EAS Alerts</div></div>' % len(eas)
html += '</div>'

# Tabs
html += '<div class="tabs">'
html += '<div class="tab active" onclick="showTab(\'fax\',this)">Weather Fax</div>'
html += '<div class="tab" onclick="showTab(\'navtex\',this)">NAVTEX</div>'
html += '<div class="tab" onclick="showTab(\'sitorb\',this)">SITOR-B</div>'
html += '<div class="tab" onclick="showTab(\'dsc\',this)">DSC</div>'
html += '<div class="tab" onclick="showTab(\'eas\',this)">EAS Alerts</div>'
html += '<div class="tab" onclick="showTab(\'schedule\',this)">Schedule</div>'
html += '</div>'

# Fax panel
html += '<div class="panel active" id="panel-fax">'
html += '<h2>Latest Charts</h2>'
if latest_fax:
    html += '<div class="grid">'
    for f in latest_fax:
        bn = os.path.basename(f)
        name = bn.replace(".png", "").replace("_", " ")
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M UTC")
        except:
            mtime = ""
        html += '<div class="card"><a href="/static/weatherfax/latest/%s" target="_blank"><img src="/static/weatherfax/latest/%s" loading="lazy"></a>' % (bn, bn)
        html += '<div class="info"><div class="name">%s</div><div class="time">%s</div></div></div>' % (name, mtime)
    html += '</div>'
else:
    html += '<div class="empty">No charts captured yet. First captures will appear at the next scheduled transmission.</div>'

html += '<h2>Archive</h2>'
if archive_fax:
    html += '<div class="filter-bar"><select onchange="filterFax(this.value)"><option value="all">All Charts</option>'
    chart_types = set()
    for f in archive_fax:
        parts = os.path.basename(f).replace(".png", "").split("_", 2)
        if len(parts) > 2:
            chart_types.add(parts[2])
    for ct in sorted(chart_types):
        html += '<option value="%s">%s</option>' % (ct, ct.replace("_", " ").title())
    html += '</select></div>'
    html += '<div class="grid" id="fax-archive">'
    for f in archive_fax:
        bn = os.path.basename(f)
        name = bn.replace(".png", "").replace("_", " ")
        parts = bn.replace(".png", "").split("_", 2)
        ctype = parts[2] if len(parts) > 2 else ""
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M")
        except:
            mtime = ""
        html += '<div class="card fax-card" data-type="%s"><a href="/static/weatherfax/images/%s" target="_blank"><img src="/static/weatherfax/images/%s" loading="lazy"></a>' % (ctype, bn, bn)
        html += '<div class="info"><div class="name">%s</div><div class="time">%s</div></div></div>' % (name, mtime)
    html += '</div>'
else:
    html += '<div class="empty">No archived charts yet.</div>'
html += '</div>'

# NAVTEX panel
html += '<div class="panel" id="panel-navtex">'
html += '<h2>NAVTEX Messages (518 kHz)</h2>'
html += '<p style="color:#484f58;font-size:0.8em;margin-bottom:10px">Station W (Astoria, OR) - Marine weather forecasts, storm warnings, navigation hazards</p>'
if navtex:
    html += '<div class="text-log">'
    for entry in navtex:
        entry_html = entry.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if "WARNING" in entry.upper() or "STORM" in entry.upper():
            entry_html = '<span class="warning">%s</span>' % entry_html
        elif "MAYDAY" in entry.upper() or "URGENT" in entry.upper():
            entry_html = '<span class="alert">%s</span>' % entry_html
        html += '<div class="text-entry">%s</div>' % entry_html
    html += '</div>'
else:
    html += '<div class="empty">No NAVTEX messages captured yet. Monitoring 518 kHz continuously.</div>'
html += '</div>'

# SITOR-B panel
html += '<div class="panel" id="panel-sitorb">'
html += '<h2>SITOR-B Maritime Safety (HF)</h2>'
if sitorb:
    html += '<div class="text-log">'
    for entry in sitorb:
        html += '<div class="text-entry">%s</div>' % entry.replace("&", "&amp;").replace("<", "&lt;")
    html += '</div>'
else:
    html += '<div class="empty">No SITOR-B messages captured yet.</div>'
html += '</div>'

# DSC panel
html += '<div class="panel" id="panel-dsc">'
html += '<h2>Digital Selective Calling (2187.5 kHz)</h2>'
if dsc:
    html += '<div class="text-log">'
    for entry in dsc:
        entry_html = entry.replace("&", "&amp;").replace("<", "&lt;")
        if "DISTRESS" in entry.upper():
            entry_html = '<span class="alert">%s</span>' % entry_html
        html += '<div class="text-entry">%s</div>' % entry_html
    html += '</div>'
else:
    html += '<div class="empty">No DSC calls captured yet.</div>'
html += '</div>'

# EAS panel
html += '<div class="panel" id="panel-eas">'
html += '<h2>Emergency Alert System</h2>'
if eas:
    html += '<div class="text-log">'
    for entry in eas:
        html += '<div class="text-entry alert">%s</div>' % entry.replace("&", "&amp;").replace("<", "&lt;")
    html += '</div>'
else:
    html += '<div class="empty">No EAS alerts captured. This is good news.</div>'
html += '</div>'

# Schedule panel
html += '<div class="panel" id="panel-schedule">'
html += '<h2>Capture Schedule</h2>'
html += '<div class="next-up"><div class="label">NEXT CAPTURE</div><div class="value" id="next-countdown">--:--:--</div><div class="chart" id="next-chart">Loading...</div></div>'
html += '<p style="color:#484f58;font-size:0.8em;margin-bottom:15px">All times shown in UTC. Seattle local time is UTC-7 (PDT) / UTC-8 (PST). Countdowns update live.</p>'

html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:15px">'

# Point Reyes schedule
html += '<div class="card" style="padding:12px">'
html += '<div class="name" style="font-size:1em;margin-bottom:8px">NMC Point Reyes, CA</div>'
html += '<div style="color:#484f58;font-size:0.75em;margin-bottom:8px">Frequencies: 4346 kHz (night) / 8682 kHz (day)</div>'
html += '<table style="width:100%;font-size:0.78em;border-collapse:collapse">'
html += '<tr style="color:#58a6ff;border-bottom:1px solid #21262d"><th style="text-align:left;padding:3px">UTC</th><th style="text-align:left;padding:3px">Local</th><th style="text-align:left;padding:3px">Chart</th><th style="text-align:left;padding:3px">Freq</th><th style="text-align:left;padding:3px">Countdown</th></tr>'

ptreyes_sched = [
    ("01:43", "18:43", "Satellite NE Pacific", "4346"),
    ("02:30", "19:30", "500mb Analysis 00Z", "4346"),
    ("03:00", "20:00", "Sea State Analysis 00Z", "4346"),
    ("03:31", "20:31", "Surface Analysis 00Z", "8682"),
    ("08:20", "01:20", "24hr Wind & Wave", "8682"),
    ("09:00", "02:00", "48hr Surface Forecast", "8682"),
    ("09:31", "02:31", "Surface Analysis 06Z", "8682"),
    ("14:20", "07:20", "Satellite NE Pacific 12Z", "8682"),
    ("14:45", "07:45", "500mb Analysis 12Z", "8682"),
    ("15:05", "08:05", "Surface Analysis 12Z", "8682"),
    ("18:22", "11:22", "24hr Wind & Wave 12Z", "8682"),
    ("18:45", "11:45", "SST Analysis", "8682"),
    ("20:40", "13:40", "48hr Surface 12Z", "8682"),
    ("21:24", "14:24", "Surface Analysis 18Z", "8682"),
]
for utc, local, chart, freq in ptreyes_sched:
    h, m = utc.split(":")
    html += '<tr style="border-bottom:1px solid #0d1117"><td style="padding:3px;color:#3fb950">%s</td><td style="padding:3px;color:#484f58">%s</td><td style="padding:3px">%s</td><td style="padding:3px;color:#f0883e">%s</td><td style="padding:3px" class="cd" data-h="%s" data-m="%s"></td></tr>' % (utc, local, chart, freq, h, m)
html += '</table></div>'

# Kodiak schedule
html += '<div class="card" style="padding:12px">'
html += '<div class="name" style="font-size:1em;margin-bottom:8px">NOJ Kodiak, AK</div>'
html += '<div style="color:#484f58;font-size:0.75em;margin-bottom:8px">Frequencies: 4296 kHz (night) / 8457 kHz (day)</div>'
html += '<table style="width:100%;font-size:0.78em;border-collapse:collapse">'
html += '<tr style="color:#58a6ff;border-bottom:1px solid #21262d"><th style="text-align:left;padding:3px">UTC</th><th style="text-align:left;padding:3px">Local</th><th style="text-align:left;padding:3px">Chart</th><th style="text-align:left;padding:3px">Freq</th><th style="text-align:left;padding:3px">Countdown</th></tr>'

kodiak_sched = [
    ("02:00", "19:00", "Surface Analysis 00Z", "4296"),
    ("05:00", "22:00", "Sea Ice Analysis", "8457"),
    ("05:20", "22:20", "24hr Surface Forecast", "8457"),
    ("08:00", "01:00", "48hr Surface Forecast", "8457"),
    ("14:00", "07:00", "Surface Analysis 12Z", "8457"),
    ("17:30", "10:30", "Satellite Imagery", "8457"),
    ("20:00", "13:00", "Wind & Wave Forecast", "8457"),
]
for utc, local, chart, freq in kodiak_sched:
    h, m = utc.split(":")
    html += '<tr style="border-bottom:1px solid #0d1117"><td style="padding:3px;color:#3fb950">%s</td><td style="padding:3px;color:#484f58">%s</td><td style="padding:3px">%s</td><td style="padding:3px;color:#f0883e">%s</td><td style="padding:3px" class="cd" data-h="%s" data-m="%s"></td></tr>' % (utc, local, chart, freq, h, m)
html += '</table></div>'

html += '</div>'  # close grid

# Text monitoring schedule
html += '<h2 style="margin-top:20px">Text Monitoring Schedule</h2>'
html += '<div class="card" style="padding:12px;margin-top:10px">'
html += '<table style="width:100%;font-size:0.78em;border-collapse:collapse">'
html += '<tr style="color:#58a6ff;border-bottom:1px solid #21262d"><th style="text-align:left;padding:3px">Source</th><th style="text-align:left;padding:3px">Frequency</th><th style="text-align:left;padding:3px">Interval</th><th style="text-align:left;padding:3px">Content</th><th style="text-align:left;padding:3px">Next Capture</th></tr>'

# NAVTEX runs at :10 past every 4th hour (0,4,8,12,16,20)
# EAS runs at :05 and :35 past every hour
# Build actual schedule times for countdown
# NAVTEX: 00:10, 04:10, 08:10, 12:10, 16:10, 20:10
navtex_times = [(0,0),(4,10),(8,40),(12,10),(16,10),(20,20)]
# EAS: every 30 min at :05 and :35
eas_times = [(h,m) for h in range(24) for m in (5,35)]

text_sched = [
    ("NAVTEX", "518 kHz", "Every 4 hours", "Marine weather forecasts, storm warnings, nav hazards", navtex_times),
    ("EAS Alerts", "162.55 MHz", "Every 30 min", "FEMA/NWS emergency alerts, tornado/tsunami warnings", eas_times),
    ("SITOR-B", "HF (various)", "With NAVTEX", "Extended range maritime safety information", navtex_times),
    ("DSC", "2187.5 kHz", "With NAVTEX", "Digital distress and safety calls", navtex_times),
]
for src, freq, interval, content, times in text_sched:
    # Encode all schedule times as data attributes for JS countdown
    times_str = ",".join(["%d:%d" % (h,m) for h,m in times])
    html += '<tr style="border-bottom:1px solid #0d1117">'
    tab_id = {"NAVTEX":"navtex","EAS Alerts":"eas","SITOR-B":"sitorb","DSC":"dsc"}.get(src, "")
    html += '<td style="padding:3px"><a href="#" onclick="showTab(\'%s\',document.querySelector(\'[onclick*=%s]\')); return false;" style="color:#58a6ff;font-weight:bold;text-decoration:none">%s</a></td>' % (tab_id, tab_id, src)
    html += '<td style="padding:3px;color:#f0883e">%s</td>' % freq
    html += '<td style="padding:3px;color:#3fb950">%s</td>' % interval
    html += '<td style="padding:3px;color:#8b949e">%s</td>' % content
    html += '<td style="padding:3px" class="cd-multi" data-times="%s"></td>' % times_str
    html += '</tr>'
html += '</table></div>'

# Weekly scan
html += '<h2 style="margin-top:20px">System Maintenance</h2>'
html += '<div class="card" style="padding:12px;margin-top:10px">'
html += '<table style="width:100%;font-size:0.78em;border-collapse:collapse">'
html += '<tr style="border-bottom:1px solid #0d1117"><td style="padding:3px;color:#58a6ff;font-weight:bold">Weekly RF Scan</td><td style="padding:3px;color:#3fb950">Sunday 03:00 UTC</td><td style="padding:3px;color:#8b949e">Scans all bands, updates active bookmark markers</td></tr>'
html += '<tr style="border-bottom:1px solid #0d1117"><td style="padding:3px;color:#58a6ff;font-weight:bold">Dashboard Refresh</td><td style="padding:3px;color:#3fb950">Every 15 minutes</td><td style="padding:3px;color:#8b949e">Regenerates this page with latest data</td></tr>'
html += '<tr style="border-bottom:1px solid #0d1117"><td style="padding:3px;color:#58a6ff;font-weight:bold">Archive Cleanup</td><td style="padding:3px;color:#3fb950">With each capture</td><td style="padding:3px;color:#8b949e">Removes fax images older than 7 days</td></tr>'
html += '</table></div>'

html += '</div>'  # close schedule panel

# JavaScript
html += """
<script>
function updateCountdowns(){
var now=new Date();
var utcH=now.getUTCHours(),utcM=now.getUTCMinutes(),utcS=now.getUTCSeconds();
var nowMin=utcH*60+utcM;
var nextSec=999999,nextChart='';
document.querySelectorAll('.cd').forEach(function(el){
var h=parseInt(el.dataset.h),m=parseInt(el.dataset.m);
var targetMin=h*60+m;
var diffMin=targetMin-nowMin;
if(diffMin<0)diffMin+=1440;
var diffSec=diffMin*60-utcS;
if(diffSec<0)diffSec+=86400;
var hh=Math.floor(diffSec/3600);
var mm=Math.floor((diffSec%3600)/60);
var ss=diffSec%60;
var txt=String(hh).padStart(2,'0')+':'+String(mm).padStart(2,'0')+':'+String(ss).padStart(2,'0');
el.textContent=txt;
el.className='cd';
if(diffSec<600){el.classList.add('cd-active');txt='NOW';}
else if(diffSec<3600){el.classList.add('cd-soon');}
else{el.classList.add('cd-later');}
if(diffSec<nextSec){
nextSec=diffSec;
var row=el.parentElement;
var cells=row.querySelectorAll('td');
nextChart=cells[2]?cells[2].textContent:'';
}
});
var nh=Math.floor(nextSec/3600);
var nm=Math.floor((nextSec%3600)/60);
var ns=nextSec%60;
var nxt=document.getElementById('next-countdown');
var nch=document.getElementById('next-chart');
if(nxt){
if(nextSec<600){nxt.textContent='CAPTURING NOW';nxt.style.color='#f0883e';}
else{nxt.textContent=String(nh).padStart(2,'0')+':'+String(nm).padStart(2,'0')+':'+String(ns).padStart(2,'0');nxt.style.color='#3fb950';}
}
if(nch)nch.textContent=nextChart;
// Update multi-schedule countdowns (NAVTEX, EAS, etc)
document.querySelectorAll('.cd-multi').forEach(function(el){
var times=el.dataset.times.split(',');
var bestSec=999999;
for(var i=0;i<times.length;i++){
var parts=times[i].split(':');
var th=parseInt(parts[0]),tm=parseInt(parts[1]);
var targetMin=th*60+tm;
var diffMin=targetMin-nowMin;
if(diffMin<0)diffMin+=1440;
var diffSec=diffMin*60-utcS;
if(diffSec<0)diffSec+=86400;
if(diffSec<bestSec)bestSec=diffSec;
}
var bh=Math.floor(bestSec/3600);
var bm=Math.floor((bestSec%3600)/60);
var bs=bestSec%60;
el.textContent=String(bh).padStart(2,'0')+':'+String(bm).padStart(2,'0')+':'+String(bs).padStart(2,'0');
el.className='cd-multi';
if(bestSec<600)el.classList.add('cd-active');
else if(bestSec<3600)el.classList.add('cd-soon');
else el.classList.add('cd-later');
});
}
updateCountdowns();
setInterval(updateCountdowns,1000);

function showTab(id,el){
document.querySelectorAll('.panel').forEach(function(p){p.classList.remove('active');});
document.querySelectorAll('.tab').forEach(function(t){t.classList.remove('active');});
document.getElementById('panel-'+id).classList.add('active');
el.classList.add('active');
}
function filterFax(type){
document.querySelectorAll('.fax-card').forEach(function(c){
c.style.display=(type==='all'||c.dataset.type===type)?'':'none';
});
}
</script>
</body></html>"""

with open(HTMLFILE, "w") as f:
    f.write(html)
print("Weather dashboard generated")
