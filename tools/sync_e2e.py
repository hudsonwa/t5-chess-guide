#!/usr/bin/env python3
"""End-to-end sync test: T5 (over the USB bridge) <-> sync service <-> web guide.

The device's Wi-Fi transport is replaced by this script relaying SYNC_PULL / SYNC_PUSH lines to the
real service; everything else (device logic, service, web app) is the production path.
"""

import json
import os
import re
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
import devpath  # noqa: E402,F401  (puts the firmware scripts on the path)
from devlink import DevLink  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

SYNC = os.environ["LCC_SYNC_URL"]  # e.g. http://<server>:8120/state
HUB = os.environ["LCC_WEB_URL"]  # a web guide that runs the same sync client
PLY = re.compile(r"PERF\] frame .* ply=(\d+)")
results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name} {detail}")


def put(rec):
    r = urllib.request.Request(SYNC, json.dumps(rec).encode(), {"Content-Type": "application/json"}, method="PUT")
    return json.loads(urllib.request.urlopen(r, timeout=5).read())


def get():
    return json.loads(urllib.request.urlopen(SYNC, timeout=5).read())


def relay(d, timeout):
    """Serve the device's sync traffic for `timeout` seconds; return the last frame's ply."""
    ply = None
    for line in d.lines(timeout):
        if "SYNC_PULL" in line:
            d.send("SYNCREMOTE " + json.dumps(get(), separators=(",", ":")))
        elif "SYNC_PUSH " in line:
            put(json.loads(line.split("SYNC_PUSH ", 1)[1]))
        if (m := PLY.search(line)):
            ply = int(m.group(1))
    return ply


with DevLink() as d:
    d.call("SYNCBRIDGE 1", "SYNCBRIDGE_OK")
    put({"game": "game-07", "ply": 11, "mode": "book", "flipped": False, "updated_at": int(time.time() * 1000), "device": "web"})
    d.call("HOME", "HOME_OK")
    time.sleep(2)
    d.send("CHESS")
    ply = relay(d, 8)
    check("device follows the web position on open", ply == 11, f"(device at ply {ply})")

    d.send("TOUCH 337 916 80")
    relay(d, 4)  # the device saves 2 s after a change and pushes
    s = get()
    check("device move reaches the service", (s["game"], s["ply"], s["device"]) == ("game-07", 12, "t5"), str(s))

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(HUB)
        pg.wait_for_timeout(2500)
        st = pg.evaluate("JSON.parse(localStorage.getItem('lcc:v1'))")
        check("web guide opens at the device position", (st["game"], st["ply"]) == ("game-07", 12), f"({st['game']} {st['ply']})")
        pg.click("#btn-fwd")
        pg.wait_for_timeout(2500)
        b.close()
    s = get()
    check("web move reaches the service", (s["ply"], s["device"]) == (13, "web"), str(s))

    d.call("HOME", "HOME_OK")
    time.sleep(2)
    d.send("CHESS")
    ply = relay(d, 8)
    check("device follows the web move on reopen", ply == 13, f"(device at ply {ply})")
    d.call("SYNCBRIDGE 0", "SYNCBRIDGE_OK")

print("sync end-to-end:", "ALL PASS" if all(results) else "FAILURES")
sys.exit(0 if all(results) else 1)
