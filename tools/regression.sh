#!/usr/bin/env bash
# Full on-device regression: speed, consistency, input reliability, sync, resume, other screens.
# Needs the T5 on USB. Results go to reports/regression-<date>.txt
set -u
cd "$(dirname "$0")/.."
PY=${PY:-python3}
T=tools
mkdir -p reports
OUT=reports/regression-$(date +%Y%m%d-%H%M).txt
run() { echo "== $1" | tee -a "$OUT"; shift; "$@" 2>&1 | tail -12 | tee -a "$OUT"; echo "exit $?" >> "$OUT"; }
: > "$OUT"
run "move speed, simulated finger, reading pace" $PY $T/perf_run.py reports/touch.json 20 1 touch
run "every action" $PY $T/actions.py reports/actions.json 3
run "partial updates == full redraw" $PY $T/consistency.py 15
run "presses 150 ms apart" $PY $T/input_reliability.py 15 0.15
run "presses 400 ms apart" $PY $T/input_reliability.py 15 0.4
if [ -n "${LCC_SYNC_URL:-}" ] && [ -n "${LCC_WEB_URL:-}" ]; then
  run "sync end to end (USB bridge for the device's network leg)" $PY $T/sync_e2e.py
else
  echo "== sync end to end: skipped (set LCC_SYNC_URL and LCC_WEB_URL)" | tee -a "$OUT"
fi
run "resume and other screens" $PY $T/screens_check.py
echo "written $OUT"
