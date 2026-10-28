# 005 Ink settling time (waveform)
Round 1, rank 1 by median. Status: open, investigate after 001-004.
Measured: wait_after median 253 ms in epd_fastest (mode 4).
Ideas: fewer frames for pure black/white content, bus clock 16 to 20 MHz, overlap the next draw with the waveform instead of blocking.

Round 1 outcome: the 213 ms waveform itself is unchanged (no panel-side changes without a way to see the ink, see [decision 11](../decisions.md)). What changed: frames no longer block on it; pre-drawing was moved after the ink settles because drawing during the waveform stretched it by ~35 ms (PSRAM contention, measured).

State: open (this is the panel floor; see 034)
