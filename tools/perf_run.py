#!/usr/bin/env python3
"""Measure tap-to-ink on the T5 Chess Guide over USB.

Usage: perf_run.py OUT_JSON [N_STEPS] [GAP_SECONDS]

GAP_SECONDS is the pause between taps: 0 = rapid tapping, 1 or more = reading pace.
MODE: "tap" (injected tap event, default) or "touch" (simulated 80 ms finger press through the real touch
path; times run from finger-down).
Add "battery" as a 5th argument to measure with idle power saving active (use a gap over 3 s).

Opens the guide, then taps Next N times (and Prev N times), one tap per finished frame. For each tap it
records the device's PERF line (draw ms, display ms) and the full latency from the moment the firmware
injected the tap (TAP_OK <millis>) to the end of the panel update (PERF ... at=<millis>).
"""

import json
import re
import statistics
import sys
import time

sys.path.insert(0, __import__("os").path.dirname(__file__))
import devpath  # noqa: E402,F401  (puts the firmware scripts on the path)
from devlink import DevLink  # noqa: E402

NEXT, PREV = (337, 916), (202, 916)
PERF = re.compile(r"PERF\] frame draw=(\d+)ms display=(\d+)ms input_to_ink=(\d+)ms at=(\d+) start=(\d+)(?: prepared=(\d))?")
PUSH = re.compile(r"PERF\] push mode=(\d+) wait_before=(\d+)ms push=(\d+)ms wait_after=(\d+)ms")
CONV = re.compile(r"PERF\] convert=(\d+)ms")
INK = re.compile(r"PERF\] ink done at=(\d+)")


MODE = "tap"  # "tap": injected tap event; "touch": simulated finger (80 ms) through the real touch path


def tap(d, xy):
    if MODE == "touch":
        d.send(f"TOUCH {xy[0]} {xy[1]} 80")
    else:
        d.send(f"TAP {xy[0]} {xy[1]}")
    # the TAP_OK reply carries the injection time; it may arrive just after CMD_RX
    tap_at, extra = None, {}
    for line in d.lines(15):
        for marker in ("TAP_OK", "TOUCH_OK"):
            if marker in line:
                tap_at = int(line.split(marker)[1].split()[0])
        if (m := CONV.search(line)):
            extra["convert"] = int(m.group(1))
        if (m := PUSH.search(line)):
            extra.update(mode=int(m.group(1)), wait_before=int(m.group(2)), push=int(m.group(3)), wait_after=int(m.group(4)))
        m = PERF.search(line)
        if m and tap_at is not None:
            draw, disp, _, at, start = map(int, m.groups()[:5])
            prepared = m.group(6) == "1"
            frame = {"input": start - tap_at, "draw": draw, "display": disp, "tap_to_push": at - tap_at,
                     "prepared": prepared, **extra}
            if extra.get("wait_after", 1) > 0:
                # firmware still blocks until the ink settles: the frame end is the ink end
                return dict(frame, tap_to_ink=at - tap_at)
            for line2 in d.lines(5):
                if (k := INK.search(line2)):
                    return dict(frame, tap_to_ink=int(k.group(1)) - tap_at)
            raise TimeoutError("no ink-done after frame")
    raise TimeoutError("no frame after tap")


def main():
    out, n = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 20
    gap = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    global MODE
    MODE = sys.argv[4] if len(sys.argv) > 4 else "tap"
    battery = len(sys.argv) > 5 and sys.argv[5] == "battery"
    with DevLink() as d:
        d.call("CHESS", "CHESS_OK")
        d.wait_for("PERF] frame", timeout=30)
        # start from a known place: Games list, then game 1 (opens at move 0)
        for xy in ((67, 916), (100, 80)):
            d.send(f"TAP {xy[0]} {xy[1]}")
            d.wait_for("PERF] frame", timeout=15)
        time.sleep(1)
        if battery:
            # USB stops counting as activity, so idle power saving kicks in as it would on battery
            d.call("BATTERYSIM 1", "BATTERYSIM_OK")
        samples = []
        for xy, name in ((NEXT, "next"), (PREV, "prev")):
            for _ in range(n):
                time.sleep(gap)
                samples.append(dict(tap(d, xy), dir=name))
        if battery:
            d.call("BATTERYSIM 0", "BATTERYSIM_OK")
    summary = {}
    for key in ("input", "draw", "convert", "wait_before", "push", "wait_after", "display", "tap_to_push", "tap_to_ink"):
        vals = [s[key] for s in samples if key in s]
        summary[key] = {"median": statistics.median(vals), "p90": sorted(vals)[int(0.9 * len(vals)) - 1], "max": max(vals)}
    json.dump({"samples": samples, "summary": summary}, open(out, "w"), indent=1)
    modes = __import__("collections").Counter(s.get("mode") for s in samples)
    print("epd modes used:", dict(modes), "| prepared frames:", sum(1 for s in samples if s.get("prepared")), "of", len(samples))
    for k, v in summary.items():
        print(f"{k:11s} median {v['median']:6.0f} ms   p90 {v['p90']:5d} ms   max {v['max']:5d} ms")


if __name__ == "__main__":
    main()
