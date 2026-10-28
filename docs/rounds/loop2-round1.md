# Loop 2, round 1: opening the guide

Measured from the finger landing on Home's "Chess Guide" row (simulated 80 ms finger) to settled ink.

| Cost | Before | After |
|---|---|---|
| Entry waveform (#023) | 437 ms epd_fast | ~330 ms move waveform, full screen |
| Frame draw (#024) | 69 ms | 3 ms copy |
| App-state SD write (#025) | 30 ms | after first frame |
| Position + note layout (#026) | 15 ms | 1 ms |
| Home acts on release (#027) | finger hold + grace | touch-down |
| **Tap to settled ink** | **~750 ms** | **372 ms** (ink starts at ~44 ms) |

What is left is the panel: ~330 ms to drive a full-screen change with the move waveform.
