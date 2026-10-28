#!/usr/bin/env python3
"""Build lcc.bin, the Chess Guide data file, from a PGN file.

Usage: export_lcc.py GAMES.pgn OUT_FILE

Each game becomes one guide entry. Headers used: White, Black, Event, Date (year), Opening, Result,
and optionally Part / PartTitle. A comment before the first move is the note for the start position;
a comment after a move is the note for that move. Every position is precomputed, so stepping a move on
the device is a lookup, not a chess computation.

Format (little-endian): see docs/data-format.md.
"""

import struct
import sys
from pathlib import Path

import chess
import chess.pgn
from PIL import Image, ImageFilter

SQUARE = 60
PIECES = "PNBRQKpnbrqk"
CODE = {p: i + 1 for i, p in enumerate("PNBRQK")} | {p: i + 9 for i, p in enumerate("pnbrqk")}
SHEET = Path(__file__).resolve().parent.parent / "assets" / "pieces-60.png"


def s(text):
    raw = (text or "").encode("utf-8")[:255]
    return struct.pack("<B", len(raw)) + raw


def bits(img):
    """1-bit bitmap of a mode-L image: 1 where pixel < 128, rows padded to whole bytes."""
    w, h = img.size
    px = img.load()
    out = bytearray()
    for y in range(h):
        row = 0
        for x in range(w):
            row = (row << 1) | (1 if px[x, y] < 128 else 0)
            if x % 8 == 7:
                out.append(row)
                row = 0
        if w % 8:
            out.append(row << (8 - w % 8))
    return bytes(out)


def sprites():
    """12 pieces (PNBRQKpnbrqk) from the sprite sheet, each as an ink bitmap plus a halo mask."""
    sheet = Image.open(SHEET).convert("RGBA")
    out = struct.pack("<H", SQUARE)
    for i, _ in enumerate(PIECES):
        sp = sheet.crop((i * SQUARE, 0, (i + 1) * SQUARE, SQUARE))
        alpha = sp.getchannel("A").point(lambda a: 255 if a >= 128 else 0)
        lum = sp.convert("L")
        # ink: black where the piece is dark; halo: the dilated piece shape, cleared before inking
        ink = Image.new("L", sp.size, 255)
        ink.paste(lum.point(lambda v: 0 if v < 128 else 255), (0, 0), alpha)
        piece = Image.new("L", sp.size, 255)
        piece.paste(0, (0, 0), alpha)
        halo = piece.filter(ImageFilter.MinFilter(5))
        out += bits(ink) + bits(halo)
    return out


def board_bytes(b):
    cells = []
    for rank in range(7, -1, -1):
        for file in range(8):
            p = b.piece_at(chess.square(file, rank))
            cells.append(CODE[p.symbol()] if p else 0)
    return bytes((cells[i] << 4) | cells[i + 1] for i in range(0, 64, 2))


def sq_index(sq):
    return (7 - chess.square_rank(sq)) * 8 + chess.square_file(sq)


def game_bytes(n, game):
    h = game.headers
    year = int(h.get("Date", "0")[:4]) if h.get("Date", "?")[:4].isdigit() else 0
    out = struct.pack("<BBH", n, int(h.get("Part", "1")), year)
    out += s(f"game-{n:02d}") + s(h.get("White")) + s(h.get("Black")) + s(h.get("Event"))
    out += s(h.get("Opening")) + s(h.get("PartTitle")) + s(h.get("Result"))
    nodes = list(game.mainline())
    out += struct.pack("<H", len(nodes))
    b = game.board()
    for ply in range(len(nodes) + 1):
        if ply:
            mv = nodes[ply - 1].move
            san = b.san(mv)
            b.push(mv)
            frm, to = sq_index(mv.from_square), sq_index(mv.to_square)
            note = nodes[ply - 1].comment
        else:
            san, frm, to = "", 255, 255
            note = game.comment
        raw = note.strip().encode("utf-8")
        out += board_bytes(b) + struct.pack("<BB", frm, to) + s(san) + struct.pack("<H", len(raw)) + raw
    return out


def read_games(path):
    games = []
    with open(path, encoding="utf-8") as f:
        while (g := chess.pgn.read_game(f)) is not None:
            games.append(g)
    return games


def main():
    src, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    games = [game_bytes(i + 1, g) for i, g in enumerate(read_games(src))]
    spr = sprites()
    head_len = 4 + 2 + 2 + 4 + 4 * len(games)
    offsets, pos = [], head_len + len(spr)
    for gb in games:
        offsets.append(pos)
        pos += len(gb)
    data = b"LCC1" + struct.pack("<HHI", 1, len(games), head_len) + struct.pack(f"<{len(games)}I", *offsets) + spr + b"".join(games)
    out_path.write_bytes(data)
    print(f"wrote {out_path} {len(data):,} bytes, {len(games)} games")


if __name__ == "__main__":
    main()
