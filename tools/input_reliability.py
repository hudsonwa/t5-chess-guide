#!/usr/bin/env python3
"""Check that no press is lost or doubled, including presses made while the ink is still settling.

Usage: input_reliability.py N_PRESSES DELAY_AFTER_FRAME_S
Opens game 1 at move 0, presses Next N times with a simulated 80 ms finger, each press DELAY seconds
after the previous frame was pushed, then checks the guide reached move N.
"""

import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import devpath  # noqa: E402,F401  (puts the firmware scripts on the path)
from devlink import DevLink  # noqa: E402

n, delay = int(sys.argv[1]), float(sys.argv[2])
PLY = re.compile(r"PERF\] frame .* ply=(\d+)")
with DevLink() as d:
    d.call("CHESS", "CHESS_OK")
    d.wait_for("PERF] frame", timeout=30)
    for xy in ((67, 916), (100, 80)):
        d.send(f"TAP {xy[0]} {xy[1]}")
        d.wait_for("PERF] frame", timeout=15)
    time.sleep(1.5)
    ply = 0
    for _ in range(n):
        d.send("TOUCH 337 916 80")
        line = d.wait_for("PERF] frame", timeout=10)
        ply = int(PLY.search("PERF] " + line.split("PERF] ", 1)[-1]).group(1))
        time.sleep(delay)
    # any late frame from a doubled press would show up here
    for line in d.lines(2):
        if (m := PLY.search(line)):
            ply = int(m.group(1))
print(f"{n} presses, {delay * 1000:.0f} ms after each frame -> move {ply}:", "PASS" if ply == n else "FAIL")
sys.exit(0 if ply == n else 1)
