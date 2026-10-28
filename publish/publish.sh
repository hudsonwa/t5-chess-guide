#!/usr/bin/env bash
# One-time publish to GitHub. Review everything first; nothing here runs automatically.
#   GH_USER=hudsonwa bash publish/publish.sh
# Needs: gh (logged in), run from this repo's root, the firmware branch at ../T5S3-Reader (branch chess-guide).
set -euo pipefail
GH_USER=${GH_USER:?set GH_USER}
ROOT=$(cd "$(dirname "$0")/.." && pwd)

# 1. Firmware: a real GitHub fork of upstream, with the chess-guide branch pushed to it.
gh repo fork ShallowGreen123/T5S3-Reader --clone=false
git -C "$ROOT/../T5S3-Reader" remote add origin "https://github.com/$GH_USER/T5S3-Reader.git" 2>/dev/null || true
git -C "$ROOT/../T5S3-Reader" push -u origin chess-guide

# 2. This repo.
gh repo create "$GH_USER/t5-chess-guide" --public --source "$ROOT" --push \
  --description "Native chess-book viewer for the LilyGo T5 e-paper, tuned to the panel's physical latency limit"
gh repo edit "$GH_USER/t5-chess-guide" --add-topic esp32 --add-topic e-ink --add-topic e-paper \
  --add-topic chess --add-topic embedded --add-topic latency --add-topic platformio

# 3. One GitHub issue per bottleneck, closed when the write-up says it was fixed.
gh label create bottleneck -R "$GH_USER/t5-chess-guide" --color D93F0B --description "Measured latency bottleneck" 2>/dev/null || true
for f in "$ROOT"/docs/bottlenecks/*.md; do
  title=$(head -1 "$f" | sed 's/^# *//')
  url=$(gh issue create -R "$GH_USER/t5-chess-guide" --title "$title" --body-file "$f" --label bottleneck 2>/dev/null \
        || gh issue create -R "$GH_USER/t5-chess-guide" --title "$title" --body-file "$f")
  if grep -q '^State: closed' "$f"; then
    gh issue close "$url" --reason completed
  fi
  sleep 1  # stay well under the API rate limit
done
