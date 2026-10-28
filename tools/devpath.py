"""Where the firmware checkout (for scripts/devlink.py) and screenshots live; override with environment variables."""

import os
import sys

FIRMWARE = os.environ.get("T5_FIRMWARE", os.path.join(os.path.dirname(__file__), "..", "..", "T5S3-Reader"))
SHOTS = os.environ.get("T5_SHOTS", os.path.join(os.path.dirname(__file__), "..", "shots"))
os.makedirs(SHOTS, exist_ok=True)
sys.path.insert(0, os.path.join(FIRMWARE, "scripts"))
