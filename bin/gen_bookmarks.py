#!/usr/bin/env python3
"""Generate Seattle SDR bookmarks HTML page."""
import json

bk_file = "/home/dragon/openwebrx-config/bookmarks.d/seattle.json"
settings_file = "/home/dragon/openwebrx-data/settings.json"

with open(bk_file) as f:
    bookmarks = json.load(f)
with open(settings_file) as f:
    settings = json.load(f)

profiles = []
for sdr_id, sdr in settings["sdrs"].items():
    for pid, p in sdr["profiles"].items():
        center = p["center_freq"]
        rate = p["samp_rate"]
        profiles.append({"sdr_id": sdr_id, "pid": pid, "pname": p["name"],
            "center": center, "low": center - rate // 2, "high": center + rate // 2,
            "combo": sdr_id + "|" + pid})

radio_info = {
    "rtlsdr-e4000": ("E4", "#ff9800", "E4000"),
    "rtlsdr-r820t-1": ("R8", "#2196f3", "R820T"),
    "sdrplay-rsp1b": ("HF", "#9c27b0", "RSP1B"),
}

def find_profile(freq):
    matches = [(abs(freq - p["center"]), p) for p in profiles if p["low"] <= freq <= p["high"]]
    return sorted(matches, key=lambda x: x[0])[0][1] if matches else None

def categorize(name, freq, mod):
    if freq >= 88000000 and freq <= 108000000: return "FM Broadcast"
    if freq >= 530000 and freq <= 1700000 and mod == "am": return "AM Broadcast"
    if 108000000 <= freq <= 137000000 and mod in ("am","acars"): return "Aviation"
    if 156000000 <= freq <= 163000000: return "Marine / AIS / NOAA WX"
    if 144000000 <= freq <= 148000000: return "Amateur 2m"
    if 420000000 <= freq <= 450000000: return "Amateur 70cm / Digital Voice"
    if 150000000 <= freq <= 156000000: return "Public Safety / Fire / EMS"
    if 453000000 <= freq <= 464000000: return "City / Transit / Hospital / FRS"
    if 849000000 <= freq <= 870000000: return "KCERS P25 800 MHz"
    if 925000000 <= freq <= 935000000: return "FLEX Pagers"
    if 160000000 <= freq <= 162000000: return "Railroad"
    if 137000000 <= freq <= 138000000: return "NOAA Satellites"
    if freq < 30000000: return "HF / Shortwave / CB"
    if "SSTV" in name: return "SSTV"
    if "FT8" in name or "WSPR" in name or "Packet" in name: return "Digital Modes"
    if any(x in name for x in ["ISM","LoRa","Garage","Key Fob","TPMS"]): return "ISM / IoT"
    if any(x in name for x in ["Iridium","GPS","ADS-B","UAT","TACAN"]): return "Satellite / ADS-B"
    if any(x in name for x in ["LTE","GSM","FirstNet","Cellular"]): return "Cellular / LTE"
    if "WMTS" in name: return "Medical Telemetry"
    if 170000000 <= freq <= 172000000: return "TV News Crews"
    if any(x in name for x in ["Military","JBLM","MARS","CAP"]): return "Military"
    if "Fax" in name: return "Weather Fax"
    if "WWV" in name: return "Time Signals"
    return "Other"

categories = {}
for b in bookmarks:
    freq, name, mod = b["frequency"], b["name"].lstrip("* "), b["modulation"]
    active, profile = b["name"].startswith("* "), find_profile(freq)
    cat = categorize(name, freq, mod)
    if cat not in categories: categories[cat] = []
    categories[cat].append((b["name"], freq, mod, active, profile))

base = "http://172.31.255.48:8073"
L = []
a = L.append

# HTML head + CSS
a('<!DOCTYPE html><html><head><meta charset="utf-8">')
a('<meta name="viewport" content="width=device-width,initial-scale=1">')
a('<title>Seattle SDR Receiver</title>')
a('<style>')
css = """*{box-sizing:border-box;margin:0;padding:0}
body{font-family:sans-serif;background:#0d1117;color:#c9d1d9;display:flex;height:100vh;overflow:hidden}
#sidebar{width:440px;min-width:360px;display:flex;flex-direction:column;border-right:2px solid #21262d;flex-shrink:0;overflow:hidden}
#sidebar-header{padding:10px 12px;flex-shrink:0;background:#161b22;border-bottom:1px solid #21262d}
#sidebar-content{overflow-y:auto;flex:1;padding:0}
#receiver{flex:1;border:none}
h1{color:#58a6ff;text-align:center;font-size:1.15em;margin:4px 0}
h2{color:#f0883e;padding:8px 12px;margin:0;cursor:pointer;user-select:none;font-size:0.88em;background:#161b22;border-bottom:1px solid #21262d;position:sticky;top:0;z-index:1}
h2:hover{background:#1c2129}
.cnt{color:#484f58;font-size:0.8em;font-weight:normal}
.elist{border-bottom:1px solid #21262d}
.entry{display:grid;grid-template-columns:26px 1fr 82px 42px;align-items:center;padding:3px 8px;cursor:pointer;font-size:0.78em;border-bottom:1px solid #0d1117;gap:4px}
.entry:hover{background:#2d1f0e;border-left:3px solid #f0883e}
.entry.tuned{background:#122d0f;border-left:3px solid #3fb950}
.active{color:#3fb950} .inactive{color:#484f58}
.rb{font-size:0.6em;font-weight:bold;padding:1px 3px;border-radius:3px;text-align:center;color:#fff;line-height:1.4}
.freq{color:#58a6ff;font-family:monospace;font-size:0.9em;text-align:right}
.mod{font-size:0.6em;font-weight:bold;text-align:center;padding:2px 5px;border-radius:3px;text-transform:uppercase;color:#c9d1d9}
.m-nfm{background:#2a6e35} .m-am{background:#7a4a1e} .m-wfm{background:#5b3d8a}
.m-p25{background:#8b2820} .m-dmr{background:#6b4a8a} .m-dstar{background:#2a6e3a}
.m-ysf{background:#7a5020} .m-nxdn{background:#7a3530} .m-acars{background:#2a6e35}
.m-adsb{background:#7a3530} .m-uat{background:#7a4540} .m-ft8{background:#3a5a8a}
.m-wspr{background:#4a6a8a} .m-sstv{background:#6b4a8a} .m-page{background:#8a7a20}
.m-ais{background:#2a6e35} .m-ism{background:#2a6e3a} .m-packet{background:#3a5a8a}
.m-sonde-rs41{background:#7a5020} .m-drm{background:#6b4a8a} .m-usb{background:#3a5a8a}
.m-lsb{background:#3a5a8a} .m-fax{background:#4a6a8a} .m-cw{background:#484f58}
.m-default{background:#484f58}
.star{color:#e3b341;margin-right:2px}
.name{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.search-wrap{position:relative;margin:6px 0}
.search{width:100%;padding:7px 30px 7px 10px;font-size:13px;background:#0d1117;border:1px solid #30363d;color:#c9d1d9;border-radius:6px}
.search:focus{border-color:#58a6ff;outline:none}
.search-x{position:absolute;right:8px;top:50%;transform:translateY(-50%);cursor:pointer;color:#484f58;font-size:16px;display:none}
.search-x:hover{color:#c9d1d9}
.legend{display:flex;gap:8px;justify-content:center;margin:6px 0;flex-wrap:wrap}
.legend-item{font-size:0.65em;display:flex;align-items:center;gap:3px}
.filter-btn{cursor:pointer;padding:2px 6px;border-radius:4px;border:1px solid transparent;user-select:none}
.filter-btn:hover{border-color:#484f58}
.filter-btn.on{border-color:#58a6ff;background:#0d2240}
#notif-bar{flex-shrink:0;background:#161b22;border-top:1px solid #21262d;padding:8px 12px;font-size:0.82em;color:#484f58;min-height:38px;display:flex;align-items:center;justify-content:center}
#notif-bar.active{background:#0d2818;color:#3fb950;font-weight:bold}
#collapse-btn{position:absolute;top:8px;right:8px;cursor:pointer;color:#484f58;font-size:18px;z-index:10;width:24px;height:24px;display:flex;align-items:center;justify-content:center;border-radius:4px}
#collapse-btn:hover{color:#c9d1d9;background:#21262d}
#sidebar.collapsed{width:42px;min-width:42px}
#sidebar.collapsed #sidebar-header>*:not(#collapse-btn){display:none}
#sidebar.collapsed #sidebar-content{display:none}
#sidebar.collapsed #notif-bar{display:none}
#sidebar.collapsed #mini-nav{display:flex}
#mini-nav{display:none;flex-direction:column;gap:2px;padding:4px;overflow-y:auto;flex:1}
.mini-cat{font-size:0.5em;color:#f0883e;padding:2px 4px;cursor:pointer;border-radius:2px;text-align:center;white-space:nowrap;overflow:hidden}
.mini-cat:hover{background:#1c2129}
.mod-filters{display:flex;flex-wrap:wrap;gap:3px;justify-content:center;margin:4px 0}
.mod-filter{font-size:0.6em;font-weight:bold;padding:2px 5px;border-radius:3px;cursor:pointer;text-transform:uppercase;border:1px solid transparent;user-select:none;color:#c9d1d9}
.mod-filter:hover{border-color:#484f58}
.mod-filter.on{border-color:#58a6ff;box-shadow:0 0 4px rgba(88,166,255,0.4)}"""
a(css)
a('</style></head><body>')

# Sidebar header
a('<div id="sidebar"><div id="sidebar-header" style="position:relative">')
a('<span id="collapse-btn" onclick="toggleSidebar()">&#9664;</span>')
a('<h1>Seattle SDR Receiver</h1>')
a('<div style="text-align:center;margin:2px 0"><a href="/static/weatherfax/index.html" target="_blank" style="color:#58a6ff;font-size:0.75em;text-decoration:none;background:#161b22;border:1px solid #21262d;padding:3px 10px;border-radius:4px">&#9748; Weather Fax Gallery</a></div>')
a('<div class="legend">')
for sid, (icon, color, label) in radio_info.items():
    a('<div class="legend-item filter-btn" data-filter="radio-%s" onclick="toggleFilter(this,\'radio-%s\')"><span class="rb" style="background:%s">%s</span> %s</div>' % (sid, sid, color, icon, label))
a('<div class="legend-item filter-btn" data-filter="active" onclick="toggleFilter(this,\'active\')"><span class="star">&#9733;</span> Active</div>')
a('</div>')
# Modulation filter buttons
a('<div class="mod-filters">')
mod_colors = {
    "nfm": "#2a6e35", "am": "#7a4a1e", "wfm": "#5b3d8a", "p25": "#8b2820",
    "dmr": "#6b4a8a", "dstar": "#2a6e3a", "ysf": "#7a5020", "nxdn": "#7a3530",
    "acars": "#2a6e35", "adsb": "#7a3530", "uat": "#7a4540", "ft8": "#3a5a8a",
    "wspr": "#4a6a8a", "sstv": "#6b4a8a", "page": "#8a7a20", "ais": "#2a6e35",
    "ism": "#2a6e3a", "packet": "#3a5a8a", "sonde-rs41": "#7a5020",
    "drm": "#6b4a8a", "lsb": "#3a5a8a", "usb": "#3a5a8a",
}
# Order by count, skip very rare ones
mod_order = ["nfm","am","wfm","p25","sstv","page","dmr","acars","sonde-rs41","packet","dstar","ism","ais","ft8","ysf","adsb","uat","drm","usb","lsb","wspr","nxdn"]
for m in mod_order:
    bg = mod_colors.get(m, "#484f58")
    a('<span class="mod-filter" style="background:%s" data-filter="mod-%s" onclick="toggleFilter(this,\'mod-%s\')">%s</span>' % (bg, m, m, m.upper()))
a('</div>')
a('<div class="search-wrap">')
a('<input type="text" class="search" id="searchbox" placeholder="Search %d bookmarks..." oninput="filt(this.value)">' % len(bookmarks))
a('<span class="search-x" id="search-x" onclick="clearSearch()">&#10005;</span>')
a('</div></div>')

# Scrollable content
a('<div id="sidebar-content">')

cat_order = ["FM Broadcast","AM Broadcast","Aviation","Marine / AIS / NOAA WX","Railroad",
    "NOAA Satellites","Public Safety / Fire / EMS","KCERS P25 800 MHz",
    "City / Transit / Hospital / FRS","Amateur 2m","Amateur 70cm / Digital Voice",
    "Digital Modes","FLEX Pagers","TV News Crews","Military","Satellite / ADS-B",
    "ISM / IoT","Medical Telemetry","Cellular / LTE","SSTV",
    "HF / Shortwave / CB","Weather Fax","Time Signals","Other"]

for cat in cat_order:
    if cat not in categories: continue
    entries = sorted(categories[cat], key=lambda x: x[1])
    act = sum(1 for e in entries if e[3])
    actstr = " / %d active" % act if act else ""
    a('<h2 onclick="tog(this)">%s <span class="cnt">%d%s</span></h2>' % (cat, len(entries), actstr))
    a('<div class="elist">')
    for name, freq, mod, active, profile in entries:
        disp = name.lstrip("* ").replace("'", "&#39;").replace('"', "&quot;")
        fmhz = freq / 1e6
        cls = "active" if active else "inactive"
        star = '<span class="star">&#9733;</span>' if active else ""
        combo = profile["combo"] if profile else ""
        sdr_id = profile["sdr_id"] if profile else ""
        icon, color, _ = radio_info.get(sdr_id, ("??", "#484f58", ""))
        if fmhz >= 1000: fs = "%.3f" % fmhz
        elif fmhz >= 1: fs = "%.4f" % fmhz
        else: fs = "%.1fk" % (freq / 1000)
        a('<div class="entry %s radio-%s mod-%s" id="bk%d" onclick="tune(%d,\'%s\',\'%s\',this)">' % (cls, sdr_id if sdr_id else "none", mod, freq, freq, mod, combo))
        a('<span class="rb" style="background:%s">%s</span>' % (color, icon))
        a('<span class="name">%s%s</span>' % (star, disp))
        a('<span class="freq">%s</span>' % fs)
        a('<span class="mod m-%s">%s</span>' % (mod, mod.upper()))
        a('</div>')
    a('</div>')

a('</div>')
# Mini nav for collapsed state
a('<div id="mini-nav">')
cat_abbrevs = {"FM Broadcast":"FM","AM Broadcast":"AM","Aviation":"AIR","Marine / AIS / NOAA WX":"MAR",
    "Railroad":"RR","NOAA Satellites":"SAT","Public Safety / Fire / EMS":"911",
    "KCERS P25 800 MHz":"P25","City / Transit / Hospital / FRS":"CTY",
    "Amateur 2m":"2m","Amateur 70cm / Digital Voice":"70c","Digital Modes":"DIG",
    "FLEX Pagers":"PGR","TV News Crews":"TV","Military":"MIL",
    "Satellite / ADS-B":"ADS","ISM / IoT":"IoT","Medical Telemetry":"MED",
    "Cellular / LTE":"LTE","SSTV":"STV","HF / Shortwave / CB":"HF",
    "Weather Fax":"FAX","Time Signals":"WWV","Other":"OTH"}
for cat in cat_order:
    if cat not in categories: continue
    ab = cat_abbrevs.get(cat, cat[:3])
    a('<div class="mini-cat" onclick="expandTo(\'%s\')" title="%s">%s</div>' % (cat, cat, ab))
a('</div>')
a('<div id="notif-bar">Click a station to tune</div>')
a('</div>')

# Receiver iframe
a('<iframe id="receiver" src="%s"></iframe>' % base)

# JavaScript
a('<script>')
a('var iframe=document.getElementById("receiver");')
a('var curTuned=null;')
a('function tune(freq,mod,pc,el){')
a('var st=document.getElementById("notif-bar");')
a('if(curTuned)curTuned.classList.remove("tuned");if(el){el.classList.add("tuned");curTuned=el;el.scrollIntoView({block:"nearest"});}')
a('st.className="active";st.textContent="Tuning "+(freq/1e6).toFixed(4)+" MHz ["+mod.toUpperCase()+"]...";')
a('try{var iw=iframe.contentWindow;')
# Switch profile if needed
a('if(pc){var s=iw.document.getElementById("openwebrx-sdr-profiles-listbox");')
a('if(s&&s.value!==pc){s.value=pc;if(iw.sdr_profile_changed)iw.sdr_profile_changed();')
# Poll until the bandwidth covers our freq (max 5 seconds)
a('var attempts=0;var poller=setInterval(function(){attempts++;')
a('try{var bw=iw.bandwidth||2400000;var cf=iw.center_freq||0;')
a('if(cf>0&&Math.abs(freq-cf)<=bw/2){clearInterval(poller);setHash(iw,freq,mod,st);}')
a('else if(attempts>25){clearInterval(poller);setHash(iw,freq,mod,st);}')
a('}catch(x){if(attempts>25){clearInterval(poller);setHash(iw,freq,mod,st);}}')
a('},200);return;}')
# Already on correct profile, just set hash
a('else{setHash(iw,freq,mod,st);return;}}')
# No profile combo, just set hash
a('setHash(iw,freq,mod,st);')
a('}catch(e){iframe.src="%s/#freq="+freq+",mod="+mod;}' % base)
a('}')
a('function setHash(iw,freq,mod,st){')
a('iw.location.hash="";')
a('setTimeout(function(){iw.location.hash="freq="+freq+",mod="+mod;')
a('st.textContent=(freq/1e6).toFixed(4)+" MHz - "+mod.toUpperCase();')
a('setTimeout(function(){st.className="";st.textContent="Click a station to tune";},4000);')
a('},200);')
a('}')
a('function tog(e){var d=e.nextElementSibling;d.style.display=d.style.display==="none"?"":"none";}')
a('function filt(q){document.getElementById("search-x").style.display=q?"block":"none";applyFilters();}')
a('function clearSearch(){var b=document.getElementById("searchbox");b.value="";b.focus();filt("");}')
a('function toggleSidebar(){')
a('var sb=document.getElementById("sidebar");var btn=document.getElementById("collapse-btn");')
a('if(sb.classList.contains("collapsed")){sb.classList.remove("collapsed");btn.innerHTML="&#9664;";}')
a('else{sb.classList.add("collapsed");btn.innerHTML="&#9654;";}')
a('}')
a('function expandTo(cat){')
a('var sb=document.getElementById("sidebar");sb.classList.remove("collapsed");')
a('document.getElementById("collapse-btn").innerHTML="&#9664;";')
a('var h2s=document.querySelectorAll("h2");')
a('for(var i=0;i<h2s.length;i++){if(h2s[i].textContent.indexOf(cat)>=0){h2s[i].scrollIntoView({behavior:"smooth"});break;}}')
a('}')
a('var activeFilters={};')
a('function toggleFilter(btn,f){')
a('if(activeFilters[f]){delete activeFilters[f];btn.classList.remove("on");}')
a('else{activeFilters[f]=true;btn.classList.add("on");}')
a('applyFilters();')
a('}')
a('function applyFilters(){')
a('var hasRadio=false,hasActive=false,hasMod=false,radios=[],mods=[];')
a('for(var f in activeFilters){if(f==="active")hasActive=true;else if(f.indexOf("radio-")===0){hasRadio=true;radios.push(f);}else if(f.indexOf("mod-")===0){hasMod=true;mods.push(f);}}')
a('var q=(document.getElementById("searchbox").value||"").toLowerCase();')
a('document.querySelectorAll(".entry").forEach(function(d){')
a('var show=true;')
a('if(q&&d.textContent.toLowerCase().indexOf(q)<0)show=false;')
a('if(show&&hasRadio){var match=false;for(var i=0;i<radios.length;i++){if(d.classList.contains(radios[i])){match=true;break;}}if(!match)show=false;}')
a('if(show&&hasMod){var match=false;for(var i=0;i<mods.length;i++){if(d.classList.contains(mods[i])){match=true;break;}}if(!match)show=false;}')
a('if(show&&hasActive&&!d.classList.contains("active"))show=false;')
a('d.style.display=show?"grid":"none";')
a('});')
a('}')
# Frequency monitor - watches the receiver's hash and highlights matching bookmarks
a('function matchFreq(freq){')
a('if(!freq)return;')
a('var best=null,bestDist=50000;')  # 50 kHz tolerance
a('document.querySelectorAll(".entry").forEach(function(el){')
a('var id=el.id;if(!id||!id.startsWith("bk"))return;')
a('var f=parseInt(id.substring(2));')
a('var dist=Math.abs(f-freq);')
a('if(dist<bestDist){bestDist=dist;best=el;}')
a('});')
a('if(best&&best!==curTuned){')
a('if(curTuned)curTuned.classList.remove("tuned");')
a('best.classList.add("tuned");curTuned=best;')
a('best.scrollIntoView({block:"nearest",behavior:"smooth"});')
a('var st=document.getElementById("notif-bar");')
a('st.className="active";st.textContent=(freq/1e6).toFixed(4)+" MHz - "+best.querySelector(".name").textContent.replace(/^\\u2733\\s*/,"");')
a('setTimeout(function(){st.className="";st.textContent="Click a station to tune";},4000);')
a('}')
a('}')
# Poll the iframe hash every 2 seconds to detect changes from inside the receiver
a('setInterval(function(){')
a('try{')
a('var h=iframe.contentWindow.location.hash;')
a('if(!h)return;')
a('var m=h.match(/freq=(\\d+)/);')
a('if(m){matchFreq(parseInt(m[1]));}')
a('}catch(e){}')
a('},2000);')
a('</script></body></html>')

with open("/home/dragon/openwebrx-config/seattle-bookmarks.html", "w") as f:
    f.write("\n".join(L))
print("Generated bookmarks page: %d bookmarks, radio icons, search X" % len(bookmarks))
