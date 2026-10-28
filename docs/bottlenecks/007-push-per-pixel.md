# 007 Push goes through M5GFX's generic per-pixel copy
Round 2, rank 2 (48 ms). Status: fixed in round 2.
Fix: FastPanelEPD subclass exposes the protected 4-bit buffer; 1-bit boxes written with a 256-entry table; one display() for the union. Push 48 -> 1 ms, tap-to-first-change 87 -> 36 ms.

State: closed
