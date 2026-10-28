# Loop 2: toward the panel's limit (rounds 1-5)

Finger down (simulated 80 ms finger) to settled ink, median.

| Action | Loop 1 end | Loop 2 end | Panel floor (waveform) |
|---|---|---|---|
| Open guide from Home | ~750 ms | **371 ms** | ~338 ms full-screen |
| Next / Prev | 276 ms | **269 ms** | ~240 ms |
| Note page | 252 ms | **251 ms** | ~240 ms |
| Flip | 326 ms | **287 ms** | ~240 ms |
| Choose game | 406 ms | **327 ms** | ~300 ms full-screen |
| Games list | 333 ms | **332 ms** | ~300 ms full-screen |

A move now starts inking ~13 ms after the input reaches the guide (touch poll ~11 ms before that).
Moves already use M5GFX's fastest waveform; what is left is the panel (#034).

Rounds: 1 open path (#023-027), 2 board blit + font prewarm (#029-030), 3 precomputed dirty boxes (#031),
4 pre-drawn list picks (#032), 5 first-frame diff (#033). Audit: no critical; 4 medium fixed
(font-cache lock, tile cache reset + PSRAM, frames forgotten on orientation change, stale hint on early return);
known limits: a same-size lcc.bin swap and external edits to the position file while the guide is closed.

Regression: all pass (speed, every action, partial == full redraw, 15/15 presses at 150 and 400 ms,
sync 5/5, resume and other screens). Sync first failed because the device clock held Perth time as UTC
(set by me in loop 1); reset to true UTC, the on-screen clock still shows Perth time.
