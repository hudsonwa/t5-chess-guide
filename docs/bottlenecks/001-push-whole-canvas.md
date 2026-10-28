# 001 Push only the changed area to the panel driver
Round 1, rank 2 by time. Status: fixed in round 1.
Measured (round 0): push = 123 ms every frame (median = p90). The whole 960x540 8-bit canvas is pushed even when 2 squares and the note changed.
Fix: diff the 1-bit frame buffer against the previous frame, push only the dirty bounding box (clip rect).
Test: perf_run.py push median; screenshot check that the board and note are correct.

State: closed
