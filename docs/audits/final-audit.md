# Final adversarial audit: T5S3-Reader t5-main (11a1133..HEAD), sync service, web sync client

Read-only review, 2026-10-28. Nothing was built, run or flashed. "Verified" means the failure follows from the code as read. "Suspected" means it depends on runtime timing or on library internals I did not confirm.

## High

**H1. The 60 ms new-touch rule can split one held touch or swipe into a phantom tap plus a swipe, on every screen.** Verified logic; how often it happens is suspected.
`lib/hal/HalGPIO.cpp` readTouchState: `if (touchActive && millis() - lastTouchSeenTime > TOUCH_NEW_TOUCH_GAP_MS) finishTouch();`. Touch is only polled once per main-loop pass (`gpio.update()` in `src/main.cpp` loop). So any loop pass longer than about 60 ms while the finger is down makes the gap look like a lift. If the finger had not yet moved 25 px, `finishTouch()` emits a **tap at the start point**, then a new touch begins mid-swipe.
Ways to get a pass that long:
- The idle path uses `delay(idleLoopDelayMs())`, which is 50 ms for non-chess screens, at the reduced CPU clock, plus the loop's own work.
- Slow activity `loop()` bodies. The firmware already logs "New max loop duration > 50".
- In chess, `prepareFrame()`/`prepareGameList()` run inside `loop()` under `RenderLock` and can prepare several frames in one pass. Board drawing alone takes 33-71 ms (round5).

Effects:
- Reader: a slow swipe becomes a centre tap (opens the menu) plus a shortened swipe.
- Global menu: the top-band drag can lose its start point.
- GT911 not-ready reads (`BoardT5S3.cpp:586`) also count as absence.

The test harness never exercises this path, because simulated touches report a point on every poll (see M6).

**H2. A ChessSync Wi-Fi session can outlive the activity and turn off Wi-Fi under the next screen.** Verified.
- `ChessGuideActivity::onExit` calls `CHESS_SYNC.stop()` and then `savePosition()`. `savePosition()` calls `push()`, so leaving the guide after any move starts a Wi-Fi connect (up to 15 s), a PUT, and then `WiFi.disconnect(true); WiFi.mode(WIFI_OFF)` (`ChessSync.cpp` run()).
- If the user goes straight to File Transfer, Calibre connect or OTA, the background task can connect while that screen is setting up its own Wi-Fi, and later switch the radio off underneath it.
- The task is never deleted and has no handshake with other Wi-Fi users.

**H3. Wi-Fi stays connected for the whole time the guide is open.** Verified.
- `start()` connects on enter. Every save, which is debounced per move, pushes.
- The radio is only switched off in the `doStop` branch, so on battery the radio idles for the entire session.
- The device never pulls again after `onEnter`, so keeping the connection buys nothing for following the web.

**H4. Interactive mode writes the next frame into the panel buffer while the previous waveform may still be reading it.** Suspected; it depends on M5GFX Panel_EPD internals.
- `displayBuffer()` calls `writeBwBoxToPanel()` (into `_buf`) before `pushPanelCanvas()` runs its `waitDisplay()` ("wait_before").
- Interactive fast pushes deliberately do not wait afterwards. If Panel_EPD's update task reads `_buf` over the course of the update, fast taps can change pixels mid-waveform, which would leave ghost or half-driven squares.
- This only affects chess, because only chess sets interactive mode. [decision 11](../decisions.md) says panel-side faults are invisible to screenshots, so this was never checked visually.

## Medium

**M1. An empty or failed game can crash the guide.** Verified.
- `openGame()` returns early if `ensureGameLoaded(0)` fails (SD card removed before the background preload finished, or a corrupt record), leaving `games[g].plies` empty.
- `render()`→`drawGame()` then indexes `game.plies[at.ply]`.
- `stepPly()` computes `last = -1`, so `next = 0`, and `layoutNote()` indexes `plies[0]`.
- Result: out-of-bounds access on an empty vector.

**M2. Corrupt `/lcc.bin` header fields are not bounds-checked.** Verified.
- `spriteOffset = le32(gData+8)` is never checked against `gDataLen`, and neither is `+2+12*rows*spriteRowBytes`. `gData[spriteOffset]` and later sprite blits read out of bounds.
- A non-monotonic offset table makes `gameEnd()-gameOffset()` underflow (size_t), so `readRange` is called with a huge length. The file size bounds the actual read, so there is no write overflow, but load still fails or behaves oddly.
- Header strings past the first 512 bytes are parsed from uninitialised PSRAM.

**M3. The `gData` cache goes stale when `/lcc.bin` is replaced.** Verified.
- `gData`, `gDataLen`, `gHeadLoaded` and `gGamesLoaded` are file-scope and live for the whole device lifetime.
- A new file uploaded via File Transfer is read using the old header and offsets, with old games marked as already loaded. The result is mixed or garbled games until reboot.
- There is no memory corruption, because lengths derive from the old `gDataLen`.

**M4. Opening the guide hijacks the e-book resume target.** Verified.
- `onEnter` sets `APP_STATE.openEpubPath = "chess://guide"` and saves.
- After visiting the guide once, the user's book is no longer what resumes on boot.
- `SleepActivity` cover lookup sees a non-book path and falls back.
- `isReaderActivity()` returning true for chess also feeds `lastSleepFromReader`.

**M5. Offline pushes are dropped.** Verified.
- `run()` swaps `pendingPush` into `body` before `ensureWifi()`. If Wi-Fi fails, `body` is discarded, with no retry and no re-queue.
- The device's change never reaches the service until the next move.
- The PUT reply, which is the server's winning record, is ignored, so a rejected push is never reconciled.

**M6. Measurement honesty.** Verified.
- **Touch latency:** `TOUCH`/`simulateDrag` bypass `touch.readPoint()` entirely. There is no GT911 I2C read, no not-ready gaps, and no controller report latency. So "from finger-down" excludes the controller, and the 60 ms split (H1) can never trigger in tests.
- **"Battery" numbers (r2-009, round2 table):** taken over USB with `BATTERYSIM 1`. This only stops serial counting as activity. Power source, CPU and USB-CDC servicing all differ from a real battery run.
- **"Settled ink":** this is `waitDisplay()` returning, meaning the driver finished, not that the ink was optically settled. In interactive mode the ink watcher's `waitDisplay` can also return between back-to-back updates.
- **Round4 "Sync 5/5 end-to-end":** run in bridge mode (`SYNC_PUSH`/`SYNC_PULL` over USB). `ChessSync::run()`'s Wi-Fi/HTTPClient path was not exercised by those checks.

**M7. Partial refresh shrinks the periodic anti-ghosting pass on all screens.** Suspected.
- With `partial`, a quality or middle escalation (`refreshCycleCount` thresholds) is applied only to the clipped dirty boxes, not the whole panel. Ghosting outside the changed areas is no longer cleaned on other screens.
- In non-interactive mode each box is a separate clipped `pushSprite`. The "driver merges them" comment is unverified, and the boxes may become N separate panel updates.

**M8. Device timestamps depend on a valid RTC.** Suspected.
- `nowMs()` is `gettimeofday`. If the clock is unset or wrong (no NTP since the RTC was lost), device `updated_at` values are tiny.
- The server's `>=` rejects every device push, and the device then adopts any remote position.
- There is no skew protection on either side. Last-write-wins across two clocks is fragile.

## Low

- **L1.** The ink watcher and the render task both call `display.waitIdle()`. `onExit` does `vTaskDelete(inkWatcher)` while it may be blocked inside `waitDisplay()`. This is benign only if M5GFX holds no lock there. Suspected.
- **L2.** Static `saved` buffers in `prepareFrame` and `prepareGameList` (2 × ~65 KB PSRAM) plus `gData` (~0.5 MB) are never freed. This is deliberate but permanent. Verified.
- **L3.** `getPanelGrayBuffer()` and the 8-bit canvas go stale after interactive or direct writes. Screenshots taken from the canvas show old content. `readPanelRow` is correct. Verified.
- **L4.** `displayBuffer` returns early when there are zero dirty boxes. A FAST refresh requested to clean ghosting with identical content is now a no-op. Verified.
- **L5.** While a simulated touch is active, real GT911 input is ignored and `point` is uninitialised (unused). This is test-only, but the serial commands ship in the firmware. Verified.
- **L6.** Web `onSyncVisibility` builds `syncKey` with `remote.mode || 'book'`. If the local mode or explore state differs, the next `save()` re-pushes the same timestamp, which the server accepts because of `>=`. This is a harmless echo, not a loop. Web first save stamps `Date.now()` into localStorage when there was no prior `updated_at`, so a later older device move loses on reload. Verified.
- **L7.** The sync service has no authentication, binds `0.0.0.0`, and sends `CORS *`. Any page in a LAN browser can rewrite the position. [decision 3](../decisions.md) says "tailnet-only" and #7 says LAN-bound; the docs contradict each other. `ply` has no upper bound, but the device clamps it. Verified.
- **L8.** [decision 11](../decisions.md) says "no waveform changes". Interactive mode does change waveform selection, by suppressing the quality and middle escalation (`!interactiveMode`) and skipping the post-push wait. This is policy, not timing, but it is not logged as a decision. Verified.

## Checked and found OK

- Grayscale reader pages: `displayGrayBuffer` sets `shownValid=false`, so the next BW frame is full.
- `flipOutput` change forces a full refresh, and the dirty-box flip math is consistent between canvas and panel paths.
- `findDirtyBoxes` box overflow merge is correct.
- Consumed-touch sequence logic handles touch-down, flick and injected ids.
- Remote `ply` and unknown `game` are clamped or ignored.
- Echo suppression on the device works (`pushOnSave=false`).
- The 64-game mask is guarded by `n <= 64`.
