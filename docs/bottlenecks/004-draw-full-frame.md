# 004 Drawing the whole frame per move with per-pixel calls
Round 1, rank 3 by time. Status: fixed in round 1.
Measured: draw median 60 ms, max 95 ms. clearScreen + every square hatched pixel by pixel through drawPixel (~120k calls) + pieces + note text.
Fix: write hatch rows and sprites straight into the frame buffer by byte; skip redrawing unchanged squares.
Test: draw median.

State: closed
