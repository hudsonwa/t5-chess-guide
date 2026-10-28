# 021 Wake: M5GFX's start-up clear holds the first guide frame until ~2.86 s after power-on
Round 5, rank 1 on the wake path. Status: open, needs a supervised session (panel side, [decision 11](../decisions.md)).
Measured: the guide's first frame is ready at ~2.1 s but waits 557-716 ms for the library's start-up clear (LGFX init clears the screen, apparently with the default quality waveform, ~1.2 s). Settled ink ~3.2 s after power-on.
Options to test with eyes on the panel: setEpdMode(epd_fastest) before gfx->init(), or init without the clear when resuming (the e-ink still shows the pre-sleep image). Estimated saving ~0.9 s per wake.

State: open
