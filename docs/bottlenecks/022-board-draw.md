# 022 Board drawn pixel by pixel on frames that were not pre-drawn
Round 5, rank 3 (board 33 ms awake, 71 ms at boot). Status: open, low impact.
Only frames that were not pre-drawn pay it (open, choose game, flip, first frame after wake). Fix idea: sprites pre-rotated to the panel orientation and blitted by byte.

State: closed (fixed by 029)
