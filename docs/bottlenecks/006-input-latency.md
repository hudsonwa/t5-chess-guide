# 006 Tap to handler latency
Round 1, rank 5 by time. Status: fixed in round 1.
Measured: input median 21 ms, max 71 ms (touch poll + loop delay + render task wake-up).
Fix: act on the tap as soon as it is decoded; check the loop delay while the guide is open.

State: closed
