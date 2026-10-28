# Round 4: open, wake and sync

Ranked list (cold open measured at ~2.25 s from command to settled ink):
1. Entry refresh epd_text 1320 ms (#017)
2. Reading the whole data file first, 811 ms (#016)
3. Wake from sleep returned to Home: a tap plus a full open lost (#019)
4. Position sync with the hub (#018, the feature this round also delivers)

| | Before | After |
|---|---|---|
| Open guide, command to settled ink | ~2250 ms | **~900 ms** (load 229, draw 72, refresh 610) |
| Wake from sleep | Home screen | **Guide, at the saved position** |
| Sync device <-> hub | none | **5/5 end-to-end checks** (USB bridge for the device's network leg) |

Move path unchanged: Next/Prev 276 ms, note page 253, choose game 406, games list 333, flip 326, real swipe 338 (actions.py, 3 runs each).

> Measurement caveats (from the final audit): "finger-down" excludes the touch controller's own report time; "battery" is BATTERYSIM on USB power; "settled ink" is the driver's waveform-complete signal, not observed ink; device-side sync was tested over the USB bridge, not Wi-Fi. See final-audit-response.md.
