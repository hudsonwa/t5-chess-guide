# 029 The board was drawn pixel by pixel through the rotation helper (33 ms)
Loop 2 round 2, rank 1 (supersedes 022). Status: fixed.
Fix: 26 square tiles (13 piece kinds x light/dark) pre-rendered in the panel's own bit layout; a square is 60 eight-byte row writes. Board 33 -> 6 ms; screenshots pixel-identical normal and flipped.

State: closed
