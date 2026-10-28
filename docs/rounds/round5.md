# Round 5: full frames and wake

Ranked list:
1. Full frames through the 8-bit canvas: convert 52 + push 122 ms on open and clean-up (#020): fixed.
2. Wake: first frame held ~0.6-0.7 s by M5GFX's start-up clear (#021): open, needs eyes on the panel.
3. Pre-drawing ran before the first frame after wake (+170 ms before the clear was found to dominate): fixed.
4. Pixel-by-pixel board drawing on non-pre-drawn frames, 33-71 ms (#022): open, low impact.

| | Before | After |
|---|---|---|
| Cold open, command to settled ink | ~900 ms | **~750 ms** |
| Wake into the guide, power-on to settled ink | n/a (woke to Home) | **~3.2 s** (bounded by the start-up clear, #021) |
