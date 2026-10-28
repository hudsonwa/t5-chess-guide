# 031 Every move copied the whole 259 KB frame and diffed it again (8 ms)
Loop 2 round 3, rank 1. Status: fixed.
Fix: prepared frames are diffed against the screen while idle; showing one copies only the changed boxes and hands them to the display (checked by a screen generation counter). Move: input to first ink ~13 ms.

State: closed
