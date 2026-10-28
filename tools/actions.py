#!/usr/bin/env python3
"""Time every guide action from finger-down to settled ink (simulated 80 ms finger), N times each.

Usage: actions.py OUT_JSON [N]
"""

import json
import os
import re
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import devpath  # noqa: E402,F401  (puts the firmware scripts on the path)
from devlink import DevLink  # noqa: E402

FRAME = re.compile(r"PERF\] frame .*?display=(\d+)ms .*?at=(\d+)")
PUSH = re.compile(r"PERF\] push mode=(\d+) .*?wait_after=(\d+)ms")
INK = re.compile(r"PERF\] ink done at=(\d+)")


def act(d, command):
    """Send a TOUCH/SWIPE/... command; return ms from its injection to settled ink."""
    d.send(command)
    t0 = frame_at = None
    blocking = False
    for line in d.lines(20):
        for marker in ("TOUCH_OK", "SWIPE_OK", "DRAG_OK", "CHESS_OK"):
            if marker in line and t0 is None:
                rest = line.split(marker)[1].split()
                t0 = int(rest[0]) if rest else None
        if (m := PUSH.search(line)):
            blocking = int(m.group(2)) > 0
        if (m := FRAME.search(line)) and t0 is not None:
            frame_at = int(m.group(2))
            if blocking:
                return frame_at - t0
        if (m := INK.search(line)) and frame_at is not None:
            return int(m.group(1)) - t0
    raise TimeoutError(f"no frame for {command}")


def main():
    out, n = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 5
    res = {}
    with DevLink() as d:
        d.call("CHESS", "CHESS_OK")
        d.wait_for("PERF] frame", timeout=30)
        time.sleep(2)

        def run(name, setup, command, settle=1.0):
            vals = []
            for _ in range(n):
                for s in setup:
                    d.send(s)  # setup steps may legitimately draw nothing
                    time.sleep(settle + 0.5)
                vals.append(act(d, command))
                time.sleep(settle)
            res[name] = {"median": statistics.median(vals), "max": max(vals), "samples": vals}
            print(f"{name:22s} median {statistics.median(vals):6.0f} ms   max {max(vals):6d} ms")

        # open game 1 at move 0 to start from a known state
        act(d, "TOUCH 67 916 80"); time.sleep(1.5); act(d, "TOUCH 100 80 80"); time.sleep(1.5)
        run("next (button)", [], "TOUCH 337 916 80")
        run("prev (button)", [], "TOUCH 202 916 80")
        run("next (swipe, injected)", [], "SWIPE 450 400 150 400")
        run("next (real drag 200ms)", [], "DRAG 450 400 150 400 200")
        run("flip", [], "TOUCH 472 916 80")
        run("note page", [], "TOUCH 450 740 80")
        run("choose game", ["TOUCH 67 916 80"], "TOUCH 100 80 80", settle=1.5)
        run("open games list", ["TOUCH 100 80 80"], "TOUCH 67 916 80", settle=1.5)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
