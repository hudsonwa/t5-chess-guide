# Final adversarial audit: findings and responses

The audit was done by an independent reviewer that read the code, without hardware. Its full report is at `research/final-audit.md`.

| # | Finding | Response | Verified on device |
|---|---|---|---|
| H1 | One touch split into a tap plus a swipe on every screen, when a loop pass takes more than 60 ms | Fixed. A new touch also needs 3 or more consecutive polls with no finger, so one slow loop pass cannot split a touch. | Input reliability 15/15 at 150 ms and 400 ms spacing; home menu and reader turns pass |
| H2 | Sync task switches Wi-Fi off under the next screen | Fixed. No network work starts after the guide exits. Wi-Fi is switched off only if the sync client switched it on, after each exchange. | Logic only (no Wi-Fi network saved on the device) |
| H3 | Wi-Fi stays connected for the whole chess session | Fixed. Connect for each exchange, disconnect afterwards. | Logic only |
| H4 | Next frame written into the panel buffer while the driver may still read it | Fixed. Interactive frames wait for the panel before writing (only rapid taps pay for it). | Tap-to-ink unchanged at 276 ms |
| M5 | Crash on an empty or corrupt game | Fixed. An unreadable game falls back to game 1, then to the "data missing" screen. | Truncated `lcc.bin`: "data missing" screen, no crash |
| M6 | Corrupt header read past the buffer | Fixed. Game offsets must be in order and inside the file; the sprite block must fit before game 1. | Same truncated-file test |
| M7 | Stale cache when `lcc.bin` is replaced | Fixed. The cache is dropped when the file size changes. Residual risk: a replacement of exactly the same size. | Not tested |
| M8 | The guide replaces the e-book's resume target | Fixed. Leaving normally hands it back to the book; going to sleep keeps the guide. | Book, then guide, then Home, then book, then sleep: wakes in the reader. Sleep in guide: wakes in guide. |
| M9 | Offline pushes dropped; server reply ignored | Fixed. A push stays queued until the service confirms it. On open the device sends its own position; the service's reply (the newest) is followed when newer. | Bridge end-to-end 5/5 |
| M10 | The reports' numbers do not measure what they claim | Corrected in the reports (see the caveats below). | n/a |
| M11 | Partial refresh shrinks the periodic anti-ghosting pass on every screen | Fixed. A refresh promoted to a cleaner waveform drives the whole screen; only fastest-waveform updates are partial. | Reader turns pass; ghosting not checked by eye |
| M12 | Sync depends on the device clock | Mitigated. NTP sync runs when the sync client connects Wi-Fi; the clock was also set over USB. | n/a |
| L13 | Concurrent waitIdle calls | Accepted. Both calls only poll a flag; deleting a task blocked in vTaskDelay is safe. | n/a |
| L14 | About 0.6 MB of PSRAM held | Accepted. 8 MB available. | n/a |
| L15 | The 8-bit canvas goes stale in interactive mode | Accepted. Screenshots now read the panel buffer; non-interactive screens re-render the canvas inside the boxes they push. Home and Settings checked by screenshot. | Yes |
| L16 | A fast refresh with no changes does nothing | Accepted. Clean-ups use other modes. | n/a |
| L17 | Test commands ship in the firmware | Accepted for this personal build. They need physical USB access. | n/a |
| L18 | Web client can re-push the same position once | Accepted. Harmless, not a loop. | n/a |
| L19 | Service has no authentication and is LAN-reachable; decisions contradicted each other | Decisions 3 and 7 corrected; decision 12 added. | n/a |
| L20 | Interactive mode changes refresh selection, unlogged | Decision 13 added. | n/a |

## Caveats on the numbers (M10)

- **"From finger-down"** means from the moment a simulated finger enters the firmware's touch logic. The GT911 controller's own scan and report time is not included. A real tap adds that, typically one controller report interval.
- **"Battery"** figures were taken on USB power with `BATTERYSIM 1`. That reproduces the firmware's idle power saving (lower CPU clock and the idle poll), but it is not a measurement on battery.
- **"Settled ink"** means the M5GFX driver reports its waveform finished (`waitDisplay`). Nobody watched the physical ink.
- **Sync, device side.** The Wi-Fi and HTTP transport is untested, because no Wi-Fi network is saved on the device. The bridge tests exercise everything else.
- **Ghosting** after many fastest-waveform updates has not been checked by eye.
