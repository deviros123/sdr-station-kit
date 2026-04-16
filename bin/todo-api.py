#!/usr/bin/env python3
"""Simple todo API - reads/writes /home/dragon/station-todos.json
Served via a tiny HTTP handler that the station page calls."""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

TODO_FILE = "/home/dragon/station-todos.json"

DEFAULT_TODOS = [
    {"id":"rg6_tram", "text":"Replace Tram 1410 discone RG-174 cable with RG-6", "category":"Antenna", "priority":"High", "impact":"~5-10 dB gain at UHF. RG-174 loses ~10 dB/10ft at 400 MHz vs ~2 dB for RG-6. Will significantly improve P25, ADS-B, pager, and 70cm reception.", "done":False, "baseline":"", "result":""},
    {"id":"kiwisdr", "text":"Install KiwiSDR 2 for automated HF captures", "category":"Hardware", "priority":"High", "impact":"Zero OpenWebRX+ downtime during weather fax/NAVTEX captures. Clean decoded fax charts. 4 simultaneous HF users.", "done":False, "baseline":"", "result":""},
    {"id":"splitter", "text":"Install BNC splitter for MLA-30+ to KiwiSDR + RSP1B", "category":"Hardware", "priority":"High", "impact":"Required for KiwiSDR integration. ~3.5 dB loss per port with passive splitter, acceptable given 35+ dB SNR on HF.", "done":False, "baseline":"", "result":""},
    {"id":"ppm_cal", "text":"Calibrate RTL-SDR PPM offset against NOAA WX or WWV", "category":"Calibration", "priority":"Medium", "impact":"Improves frequency accuracy. Stations will tune to exact center. Set loPpmCorrection in OpenWebRX+ settings.", "done":False, "baseline":"", "result":""},
    {"id":"discone_outdoor", "text":"Move Tram 1410 discone from attic to roof mount", "category":"Antenna", "priority":"Medium", "impact":"ADS-B range jumps from ~50 miles to 150+ miles. Marine VHF, aviation, and distant public safety signals improve dramatically.", "done":False, "baseline":"", "result":""},
    {"id":"replace_dongle", "text":"Replace flaky R820T dongle (SN: 81796306)", "category":"Hardware", "priority":"Medium", "impact":"Restores third RTL-SDR for dedicated UHF monitoring or ADS-B tracking.", "done":False, "baseline":"", "result":""},
    {"id":"change_passwords", "text":"Change default passwords (dragon/dragon)", "category":"Security", "priority":"High", "impact":"Basic security. Change system password, OpenWebRX+ admin password, and any other defaults.", "done":False, "baseline":"", "result":""},
    {"id":"adsb_feed", "text":"Set up ADS-B feed to FlightAware/FlightRadar24", "category":"Software", "priority":"Low", "impact":"Free premium account ($90/yr value) in exchange for feeding ADS-B data.", "done":False, "baseline":"", "result":""},
    {"id":"aprs_igate", "text":"Configure APRS iGate for packet gateway", "category":"Software", "priority":"Low", "impact":"Contributes APRS position reports to the internet.", "done":False, "baseline":"", "result":""},
    {"id":"ais_feed", "text":"Feed AIS data to MarineTraffic", "category":"Software", "priority":"Low", "impact":"Free premium MarineTraffic account for feeding ship positions.", "done":False, "baseline":"", "result":""},
    {"id":"https", "text":"Enable HTTPS on OpenWebRX+", "category":"Security", "priority":"Low", "impact":"Encrypted web access. Required if exposing to internet.", "done":False, "baseline":"", "result":""},
    {"id":"mla30_outdoor", "text":"Move MLA-30+ from attic to outdoor mount", "category":"Antenna", "priority":"Low", "impact":"Minor improvement for HF. Active loop works well indoors.", "done":False, "baseline":"", "result":""},
    {"id":"lna_adsb", "text":"Add filtered LNA for ADS-B (1090 MHz)", "category":"Hardware", "priority":"Low", "impact":"Dramatically improves ADS-B range. ~$25 for RTL-SDR Blog LNA.", "done":False, "baseline":"", "result":""},
]

def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE) as f:
            return json.load(f)
    else:
        save_todos(DEFAULT_TODOS)
        return DEFAULT_TODOS

def save_todos(todos):
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)

BENCH_DIR = "/home/dragon/benchmarks"

def get_benchmarks(todo_id):
    """Get all benchmark results for a todo item, sorted newest first."""
    results = []
    if os.path.isdir(BENCH_DIR):
        for f in sorted(os.listdir(BENCH_DIR), reverse=True):
            if f.startswith(todo_id + "_") and f.endswith(".json"):
                try:
                    with open(os.path.join(BENCH_DIR, f)) as fh:
                        results.append(json.load(fh))
                except:
                    pass
    return results

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/todos":
            data = json.dumps(load_todos())
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data.encode())
        elif self.path.startswith("/benchmarks/"):
            todo_id = self.path.split("/")[-1]
            data = json.dumps(get_benchmarks(todo_id))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data.encode())
        elif self.path == "/benchmark/run":
            # This would be dangerous to run via GET but convenient for testing
            self.send_response(405)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/todos":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode()
            todos = json.loads(body)
            save_todos(todos)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        elif self.path == "/benchmark/run":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode())
            todo_id = body.get("id", "")
            label = body.get("label", "manual")
            # Run benchmark in background
            os.system("/home/dragon/sdr-benchmark.sh %s %s &" % (todo_id, label))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "running", "id": todo_id}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress logs

if __name__ == "__main__":
    port = 8075
    server = HTTPServer(("0.0.0.0", port), Handler)
    print("Todo API running on port %d" % port)
    server.serve_forever()
