# 009 First tap after a pause slow on battery (50 ms idle poll + low CPU clock)
Round 2, rank 3 (68 ms input). Status: fixed in round 2.
Hidden by USB: serial counts as activity. BATTERYSIM 1 makes the harness behave as on battery.
Fix: activities set their idle loop delay; the guide polls every 10 ms. 331 -> 293 ms from finger-down after a 5 s pause.

State: closed
