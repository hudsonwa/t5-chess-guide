#!/usr/bin/env python3
"""Check that partial updates leave exactly what a full redraw shows.

Usage: consistency.py N_STEPS
Steps Next N times (partial updates), screenshots, re-opens the guide (full redraw of the same position),
screenshots again, and compares the two images pixel for pixel.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import devpath  # noqa: E402,F401  (puts the firmware scripts on the path)
from devlink import DevLink  # noqa: E402
from usb_screen import screenshot  # noqa: E402

n = int(sys.argv[1]) if len(sys.argv) > 1 else 15
out = devpath.SHOTS
os.makedirs(out, exist_ok=True)
with DevLink() as d:
    d.call("CHESS", "CHESS_OK")
    d.wait_for("PERF] frame", timeout=30)
    for _ in range(n):
        d.send("TAP 337 916")
        d.wait_for("PERF] frame", timeout=15)
    a = screenshot(d.ser, f"{out}/partial.png")
    d.call("HOME", "HOME_OK")
    d.wait_for("PERF]", "Entering activity: Home", timeout=15)
    d.call("CHESS", "CHESS_OK")
    d.wait_for("PERF] frame", timeout=30)
    b = screenshot(d.ser, f"{out}/full.png")
diff = sum(1 for x, y in zip(a, b) if x != y)
print("partial vs full redraw:", "IDENTICAL" if diff == 0 else f"{diff} pixels differ")
sys.exit(1 if diff else 0)
