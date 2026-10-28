# Design decisions

Numbered as in the original log, so references elsewhere in these docs (for example "DECISIONS 11") still resolve.
Entries about private infrastructure are summarised.

| # | Decision | Why |
|---|---|---|
| 1 | Lean C++ inside the existing T5S3-Reader firmware | Reuses its display and touch drivers. The language does not change tap-to-ink time; the pipeline does. |
| 3 | Reading position lives in a small sync service on the home server | Both the web guide and the device can reach it. It stores only a reading position. |
| 4 | Sync record mirrors the web guide's local save: game, ply, mode, flipped, plus updated_at and device | One meaning on both sides; last write wins by updated_at. |
| 7 | Service reachable on the VPN (tailnet) and the home LAN | The device joins home Wi-Fi, not the VPN. |
| 8 | The data file stores every position precomputed (32 B per ply, 4 bits per square), plus SAN, note and last-move squares | No chess engine on the device: a move is a lookup. |
| 9 | Piece sprites (60 px, 1-bit ink + halo mask) ship inside the data file | Art can change without a firmware rebuild. |
| 10 | v1 scope: board, paged notes, Prev/Next and swipe, games list, flip, sync | Keeps the speed work on the path used most. |
| 11 | No waveform or panel bus-clock changes without checking the panel by eye | Screenshots read the driver's buffer, not the ink, so a waveform or timing fault would be invisible to the test harness. Panel-side ideas are logged as issues instead. |
| 12 | Sync service has no authentication | It stores only a reading position on a private network. Revisit before any wider exposure. |
| 13 | While interacting, fast refreshes are never promoted to cleaner waveforms; one clean-up refresh after 15 frames and 20 s idle | Keeps clean-up waveforms off the tap path. Chooses among the driver's existing waveforms, so it stays inside decision 11. |
| 14 | The start-up clear on wake (#021) is left unchanged | A power-on waveform change can't be verified without seeing the panel. |
