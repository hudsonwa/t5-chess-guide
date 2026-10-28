# Testing on the device

All numbers in this repository come from the real hardware, driven over USB serial. The firmware accepts
`CMD:<VERB> ...` lines and answers `<VERB>_OK`; `scripts/devlink.py` in the firmware branch wraps that.

| Command | Purpose |
|---|---|
| `TOUCH x y ms`, `DRAG x0 y0 x1 y1 ms`, `SWIPE ...` | Simulated finger through the real touch state machine |
| `SCREENGRAY` | Screenshot read from the panel driver's own 4-bit buffer (what the panel is being driven to show) |
| `PUT path size` / `GET` / `LS` / `RM` | File transfer with per-chunk offset + CRC32, resend on silence, read-back CRC |
| `CHESS`, `HOME`, `OPEN path` | Jump between screens |
| `SETTIME epoch` | Set the clock (true UTC epoch seconds) |
| `SYNCBRIDGE 1` | Route the sync client's traffic over USB, so the network leg can be tested without Wi-Fi |
| `BATTERYSIM 1` | Stop USB counting as user activity, so idle power-saving paths are exercised |

## The harness

`tools/regression.sh` runs everything below and writes `reports/regression-<date>.txt`. Set `T5_FIRMWARE` to the
firmware checkout (default `../T5S3-Reader`).

| Script | Checks |
|---|---|
| `perf_run.py` | Per-stage latency of N moves (input, draw, convert, push, ink) |
| `actions.py` | Finger-down → ink settled for every action |
| `consistency.py` | Partial updates produce a frame pixel-identical to a full redraw |
| `input_reliability.py` | N presses at a given spacing land exactly N moves |
| `sync_e2e.py` | Device ↔ sync service ↔ web guide, both directions (needs `LCC_SYNC_URL`, `LCC_WEB_URL`) |
| `screens_check.py` | Sleep/wake resumes the guide; other screens and the e-book reader are unaffected |

## Caveats

- "Finger-down" excludes the touch controller's own scan and report time (~10 ms).
- "Settled" is the driver's waveform-complete signal; the eye may judge the last frames differently.
- Screenshots show what the panel is driven to, not a photo of the ink, so ghosting has to be judged by eye.
