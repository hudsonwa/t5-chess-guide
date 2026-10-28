# 012 Swipes act only after the finger lifts plus 300 ms grace
Round 3, rank 1 (~775 ms for a 200 ms drag). Status: fixed in round 3.
Fix: flick event once horizontal travel >= 80 px and |dx| > 2|dy|, while the finger is down. 338 ms from finger-down.

State: closed
