#!/usr/bin/env python3
"""Resume-after-sleep, resume-target hand-back, home menu, settings, and the e-book reader."""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import devpath  # noqa: E402,F401  (puts the firmware scripts on the path)
from devlink import DevLink  # noqa: E402
from usb_screen import screenshot  # noqa: E402

ok = []


def check(name, cond, detail=""):
    ok.append(cond)
    print(f"{'PASS' if cond else 'FAIL'}  {name} {detail}")


def entered(d, timeout=20):
    line = d.wait_for("Entering activity: ", timeout=timeout)
    return line.split("Entering activity: ")[1].strip()


# 1. sleeping in the guide wakes into the guide
with DevLink() as d:
    d.call("CHESS", "CHESS_OK"); d.wait_for("PERF] frame", timeout=30)
    d.call("SLEEPPREP", "SLEEPPREP_OK")
with DevLink(boot_wait=0) as d:
    check("sleep in guide -> wakes in guide", entered(d) == "ChessGuide")

# 2. open a book, visit the guide, leave to Home, sleep from the reader: the book resumes, not the guide
with DevLink() as d:
    d.call("OPEN /Logical-Chess-T5.epub", "OPEN_OK"); time.sleep(10)
    d.call("CHESS", "CHESS_OK"); d.wait_for("PERF] frame", timeout=30)
    d.call("HOME", "HOME_OK"); time.sleep(2)
    d.call("OPEN /Logical-Chess-T5.epub", "OPEN_OK"); time.sleep(10)
    d.call("SLEEPPREP", "SLEEPPREP_OK")
with DevLink(boot_wait=0) as d:
    act = entered(d)
    check("guide hands the resume target back to the book", act in ("Reader", "EpubReader"), f"({act})")

# 3. home menu entries through the real touch path
with DevLink() as d:
    for target, y in (("Settings", 634), ("ChessGuide", 490), ("RecentBooks", 418), ("FileBrowser", 346)):
        d.call("HOME", "HOME_OK"); time.sleep(2)
        d.send(f"TOUCH 150 {y} 90")
        try:
            act = entered(d, 6)
        except TimeoutError:
            act = "nothing"
        check(f"home -> {target}", act.startswith(target[:6]), f"({act})")
        time.sleep(1)

# 4. e-book reader: a page reached by page turns is drawn identically when reached by page turns again
#    (same fast waveform both times; reopening uses a different waveform, so it is not compared)
with DevLink() as d:
    d.call("OPEN /Logical-Chess-T5.epub", "OPEN_OK"); time.sleep(12)
    for _ in range(5):
        d.send("TOUCH 500 480 80"); time.sleep(3.5)
    a = screenshot(d.ser, os.path.join(devpath.SHOTS, "reader-turned.png"))
    d.call("HOME", "HOME_OK"); time.sleep(3)
    d.call("OPEN /Logical-Chess-T5.epub", "OPEN_OK"); time.sleep(10)
    d.send("TOUCH 40 480 80"); time.sleep(3.5)   # back one page
    d.send("TOUCH 500 480 80"); time.sleep(3.5)  # forward again
    b = screenshot(d.ser, os.path.join(devpath.SHOTS, "reader-returned.png"))
    diff = sum(1 for x, y in zip(a, b) if x != y)
    check("reader page via turns == same page via turns again", diff == 0, f"({diff} pixels differ)")
    d.call("HOME", "HOME_OK")

print("screens check:", "ALL PASS" if all(ok) else "FAILURES")
sys.exit(0 if all(ok) else 1)
