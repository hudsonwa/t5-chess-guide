# 003 Converting the whole frame to the 8-bit canvas
Round 1, rank 4 by time. Status: fixed in round 1.
Measured: convert = 53 ms every frame. renderBwToPanelCanvas walks all 518,400 pixels one bit at a time.
Fix: convert only the dirty box (from 001), and expand 8 pixels per byte with a lookup table.
Test: convert median.

State: closed
