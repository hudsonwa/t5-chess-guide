# Round 3: every other action

Round 2 brought Next/Prev to the waveform floor, so round 3 timed every action (`tools/actions.py`, simulated finger from finger-down to settled ink) and ranked them.

| Action | Before | After |
|---|---|---|
| Next / Prev (button) | 270 | 275 |
| Swipe (real 200 ms drag) | ~775 (200 drag + 300 grace + 275) | **338** |
| Note page | 672 | **250** |
| Choose game | 778 | **403** |
| Games list | 357 | **332** |
| Flip | 352 | **323** |

Checks after the round: consistency (partial == full redraw) IDENTICAL; input reliability 15/15 at 150 ms and 400 ms spacing.

> Measurement caveats (from the final audit): "finger-down" excludes the touch controller's own report time; "battery" is BATTERYSIM on USB power; "settled ink" is the driver's waveform-complete signal, not observed ink; device-side sync was tested over the USB bridge, not Wi-Fi. See final-audit-response.md.
