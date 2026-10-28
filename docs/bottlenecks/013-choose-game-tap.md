# 013 Choosing a game waits for the tap (release grace) and redraws everything
Round 3, rank 2 (778 ms). Status: fixed in round 3 (403 ms).
Fix: list rows act on touch-down. The rest is a full-screen change (whole frame differs), which costs the full waveform area.

State: closed
