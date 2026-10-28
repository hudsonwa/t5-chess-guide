#!/usr/bin/env python3
"""Reading-position sync for the Logical Chess guide (hub web app + T5 e-ink device).

GET  /state  -> the stored position as JSON ({} if none yet)
PUT  /state  -> store a position if it is at least as new as the stored one (last write wins)
GET  /health -> "ok"

A position is a small JSON object: {game, ply, mode, flipped, updated_at, device}.
updated_at is milliseconds since the epoch, set by the writer.
"""

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DATA = os.environ.get("LCC_SYNC_DATA", "/data/state.json")
MAX_BODY = 2048
FIELDS = {"game": str, "ply": int, "mode": str, "flipped": bool, "updated_at": int, "device": str}
lock = threading.Lock()


def load():
    try:
        with open(DATA) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save(state):
    tmp = DATA + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, DATA)


def clean(body):
    """Keep only known fields of the right type; None if the record is unusable."""
    if not isinstance(body, dict):
        return None
    out = {k: body[k] for k, t in FIELDS.items() if isinstance(body.get(k), t) and not (t is int and isinstance(body[k], bool))}
    if "game" not in out or "ply" not in out or "updated_at" not in out:
        return None
    if len(out["game"]) > 32 or out["ply"] < 0 or len(out.get("mode", "")) > 16 or len(out.get("device", "")) > 32:
        return None
    return out


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, payload):
        data = json.dumps(payload).encode() if not isinstance(payload, bytes) else payload
        self.send_response(code)
        self.send_header("Content-Type", "application/json" if not isinstance(payload, bytes) else "text/plain")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.reply(204, b"")

    def do_GET(self):
        if self.path == "/health":
            self.reply(200, b"ok")
        elif self.path == "/state":
            with lock:
                self.reply(200, load())
        else:
            self.reply(404, {"error": "not found"})

    def do_PUT(self):
        if self.path != "/state":
            self.reply(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            self.reply(413, {"error": "bad length"})
            return
        try:
            incoming = clean(json.loads(self.rfile.read(length)))
        except ValueError:
            incoming = None
        if incoming is None:
            self.reply(400, {"error": "bad position"})
            return
        with lock:
            current = load()
            if incoming["updated_at"] >= current.get("updated_at", 0):
                save(incoming)
                current = incoming
        self.reply(200, current)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8120"))), Handler).serve_forever()
