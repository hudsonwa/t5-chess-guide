# 002 Full-quality clean refresh fires during interaction
Round 1, rank 1 by worst case. Status: fixed in round 1.
Measured: wait_after max 1321 ms, display p90 611 ms. The refresh-cycle policy promotes every Nth fast update to epd_fast / epd_quality (modes 3 and 1 seen in 6 of 40 frames).
Fix: in the chess guide, always use the fastest waveform on the move path; run one quality clean-up when the reader has been idle for a few seconds instead.
Test: no mode 1/3 frames in perf_run; idle clean-up visible in the log.

State: closed
