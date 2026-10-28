# Latency: from 820 ms to the panel's limit

The goal was a chess-book viewer that feels instant on e-ink. E-ink has a hard physical floor: the particles take a
fixed number of drive frames to move. On this panel the fastest waveform M5GFX offers (`epd_fastest`) settles a move
in about 240 ms. Everything above that number is software, and this is how it was removed.

## Method

Every round followed the same loop:

1. **Measure** each stage on the device with timestamps the firmware logs over USB (`PERF` lines): input → draw →
   convert → push → ink settled.
2. **Rank** the stages by milliseconds and file each as an issue ([docs/bottlenecks](bottlenecks/)).
3. **Fix** in rank order, re-measuring after each fix, and **check correctness**: a frame built from partial updates
   must be pixel-identical to a full redraw of the same position (`tools/consistency.py`), and no press may be lost or
   doubled (`tools/input_reliability.py`).
4. **Audit**: an independent adversarial review of the diff; findings fixed or answered in writing
   ([docs/audits](audits/)).

Two measurement decisions mattered as much as any optimisation:

- **"Done" means the waveform finished**, reported by the driver, not "the draw call returned". Early on, a busy flag
  that cleared early produced an 88 ms reading that was simply wrong.
- **Input is a simulated finger** fed through the real touch state machine (`TOUCH x y ms`), not an injected tap event.
  Injected taps had hidden a 300 ms release grace that every real press paid.

## Where the time went

Baseline, Next move, real press: **~820 ms** (518 ms measured from an injected tap, plus the hidden release grace).

| Stage | Before | After | How |
|---|---|---|---|
| Touch: wait for finger lift + 300 ms grace | ~380 ms | 0 | Act on touch-down; swipes fire mid-gesture (#008, #012) |
| Draw the frame | 60 ms | 0 on the tap | Pre-draw neighbouring frames while the reader reads (#004) |
| Copy + diff the 259 KB frame | 8 ms | 0 on the tap | Diff pre-drawn frames while idle; copy only changed boxes (#031) |
| Convert 1-bit → 4-bit, whole frame | 53 ms | ~5 ms | Convert only dirty boxes, through a 256-entry lookup table (#003) |
| Push through the 8-bit canvas | 123 ms | ~1 ms | Write boxes straight into the EPD driver's 4-bit buffer (#007) |
| Quality refresh mid-interaction | up to 1.3 s | 0 | Fastest waveform only while interacting; one clean-up when idle (#002, #010) |
| Wait for the ink before polling again | ~240 ms | 0 | Return while the waveform runs; a watcher task reports settle (#005) |
| **Ink (the panel)** | ~240 ms | ~240 ms | Physics |

Opening the guide went from ~2,250 ms to 371 ms the same way: read only the current game from the card (#016), use the
move waveform on entry with a deferred clean-up (#017, #023), keep drawn frames in PSRAM across visits so reopening is
a copy (#024), and move the settings write after the first frame (#025).

## The pieces worth reading in the code

- **Precomputed dirty boxes** (`HalDisplay::diffAgainstShown`, `hintDirtyBoxes`). The display keeps a copy of the frame
  on screen and a generation counter that changes whenever the screen does. A pre-drawn frame stores the rectangles
  where it differs from the screen *and the generation it was diffed against*. On the tap, if the generation still
  matches, the guide copies just those rectangles and passes them to the driver; otherwise it falls back to a full
  diff. Correctness rests on one invariant (the frame buffer equals the shown frame between renders), which the audit
  traced through every path.
- **Board blit** (`ChessGuideActivity::blitBoard`). In portrait the panel is rotated 90°, so drawing pixel by pixel
  scatters writes across PSRAM rows. Instead, each of the 26 square kinds (13 piece codes × light/dark) is rendered once
  into the panel's native layout, where a square column is one 60-bit row at a nibble-aligned offset. A board is
  64 × 60 read-modify-writes of 8 bytes. Verified pixel-identical against the old path, normal and flipped.
- **Touch** (`HalGPIO`). Touch-down and flick events, sequence numbers so one physical touch can't fire twice
  across a screen change, and a new-touch rule (a 60 ms gap with at least 3 empty polls) that separates quick
  re-taps the controller would otherwise merge.

## Dead ends (measured and reverted)

- **32-bit aligned stores in the convert.** Replacing 4-byte `memcpy` with word stores looked like an obvious win;
  it changed nothing. The convert is bound by PSRAM write bandwidth (~250 KB in 9 ms), not instructions.
- **Pre-drawing during the waveform.** Drawing the next frame while the panel was still inking slowed the ink by
  ~35 ms (the panel driver and the CPU compete for PSRAM). Pre-drawing now waits for the ink to settle.
- **Faster waveforms or bus clock.** Off the table without judging ghosting and contrast on the real panel by eye;
  documented as the remaining lever (#034).

## What's left

| | Time | Owner |
|---|---|---|
| Touch controller report + poll | ~11 ms | GT911 report rate |
| Copy boxes + convert + push | ~13 ms | PSRAM bandwidth |
| Ink | ~240 ms (move), ~300–340 ms (full screen) | The panel |
