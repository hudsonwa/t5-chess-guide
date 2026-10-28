# 008 Taps reported 300 ms after the finger lifts; quick re-taps merged or missed
Round 2, rank 1 (>= 380 ms of real latency the injected-tap harness could not see). Status: fixed in round 2.
Found by simulating a finger through the real touch path (TOUCH x y ms).
Fixes: act on touch-down for the guide's buttons; a finger absent >= 60 ms then back is a new touch; consumed touches tracked by id; ink wait moved to a watcher task so the loop keeps polling touch during the settle.
Tests: input_reliability.py, 15 presses at 150/300/600 ms spacing, all exact.

State: closed
