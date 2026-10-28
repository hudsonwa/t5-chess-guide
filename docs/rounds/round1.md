# Round 1

Baseline (round 0, 40 taps, Next x20 + Prev x20, `tools/perf_run.py`):

| Stage | Median | p90 | Max |
|---|---|---|---|
| input (tap to render start) | 21 | 29 | 71 |
| draw | 60 | 76 | 95 |
| convert | 53 | 53 | 53 |
| push | 123 | 123 | 123 |
| wait_after (ink) | 253 | 436 | 1321 |
| **tap_to_ink** | **518** | **688** | **1611** |

Ranked issues: 002 (worst case), 005 (median, physical), 001, 004, 003, 006.

## Fixes (each measured with `perf_run.py`, 40 taps, and checked with `consistency.py`: partial updates pixel-identical to a full redraw)

| Issue | Change | tap_to_ink median |
|---|---|---|
| 001/003 | Diff 1-bit frame, convert with a lookup table, push one clip rect per changed column band | 518 → 372 |
| 002 | Interactive mode: fastest waveform only; one clean-up refresh after 4 s idle | 372 → 366 (worst case 1611 → 437) |
| 004 | Pre-draw neighbouring moves into spare frames; a step is a copy | 366 → 305 (reading pace) |
| 005 | Return after the push; wait for the ink in the loop; pre-draw after the ink settles (during it costs ~35 ms) | 298 reading / 305 rapid |
| 006 | Input latency fell 21 → 11 ms as a side effect of 004/005 | n/a |

## Result

| | Round 0 | Round 1 (reading) | Round 1 (rapid) |
|---|---|---|---|
| tap_to_ink median | 518 | **298** | **305** |
| p90 | 688 | 315 | 310 |
| max | 1611 | 316 | 315 |
| tap to first panel change | ~300 | **87** | 90 |

Remaining per tap (reading): input 11, draw 5, convert 16, push 48, waveform ~211.

Measurement note: the driver's displayBusy() clears before the waveform ends, so a first attempt reported 88 ms. That number was wrong; ink completion is now measured with waitDisplay().
