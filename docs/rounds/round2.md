# Round 2

Ranked list at the start of round 2 (after round 1: 298 ms reading pace, injected taps):
1. Hidden: real taps wait 300 ms after the finger lifts (release grace), and quick re-taps were merged or lost (#008)
2. Push through the generic per-pixel path, 48 ms (#007)
3. Idle poll on battery, 68 ms input after a pause (#009, hidden by USB)
4. Idle clean-up refresh colliding with taps, up to ~1.5 s (#010)
5. Draw 5 ms, convert 13 ms (#011)
Not addressed: waveform ~242 ms (panel side, see [decision 11](../decisions.md)).

## Measurement changes

- `TOUCH x y ms` simulates a finger through the real touch path; tap_to_ink is now timed from finger-down.
- `BATTERYSIM 1` stops USB counting as activity so idle power saving is measured.
- `input_reliability.py` checks no press is lost or doubled.
- Screenshots read the panel driver's own buffer.

## Result (from finger-down, simulated 80 ms press)

| | Round 0 (estimated for a real press) | Round 1 | Round 2 |
|---|---|---|---|
| tap to first panel change | ~680 | ~470 | **30** |
| tap to settled ink, awake | ~900 (518 + 380) | ~680 (298 + 380) | **272** (p90 275) |
| tap to settled ink, battery, after 5 s pause | n/a | n/a | **293** |
| presses lost or doubled | quick re-taps merged | quick re-taps merged | **0 of 45** |

Round 0 and 1 columns add the 380 ms (80 ms press + 300 ms grace) that the injected-tap harness skipped.

> Measurement caveats (from the final audit): "finger-down" excludes the touch controller's own report time; "battery" is BATTERYSIM on USB power; "settled ink" is the driver's waveform-complete signal, not observed ink; device-side sync was tested over the USB bridge, not Wi-Fi. See final-audit-response.md.
