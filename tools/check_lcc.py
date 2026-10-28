#!/usr/bin/env python3
"""Parse lcc.bin independently of the exporter and check every position against a chess replay.

Usage: check_lcc.py LCC_BIN GAMES.pgn
"""

import struct
import sys
from pathlib import Path

import chess
import chess.pgn

PIECES = "PNBRQKpnbrqk"
SYM = {i + 1: p for i, p in enumerate("PNBRQK")} | {i + 9: p for i, p in enumerate("pnbrqk")}


def rd_str(buf, pos):
    n = buf[pos]
    return buf[pos + 1 : pos + 1 + n].decode("utf-8"), pos + 1 + n


def main():
    buf = Path(sys.argv[1]).read_bytes()
    with open(sys.argv[2], encoding="utf-8") as f:
        source = []
        while (g := chess.pgn.read_game(f)) is not None:
            source.append(g)
    assert len(source) == struct.unpack_from("<H", buf, 6)[0], "game count"
    assert buf[:4] == b"LCC1", "bad magic"
    version, n_games, spr_off = struct.unpack_from("<HHI", buf, 4)
    offsets = struct.unpack_from(f"<{n_games}I", buf, 12)
    size = struct.unpack_from("<H", buf, spr_off)[0]
    bm = (size + 7) // 8 * size
    assert spr_off + 2 + 24 * bm == offsets[0], "sprite block size mismatch"
    total_plies = 0
    for gi, off in enumerate(offsets):
        n, part, year = struct.unpack_from("<BBH", buf, off)
        pos = off + 4
        fields = []
        for _ in range(7):
            v, pos = rd_str(buf, pos)
            fields.append(v)
        gid = fields[0]
        nplies = struct.unpack_from("<H", buf, pos)[0]
        pos += 2
        b = source[gi].board()
        moves = list(source[gi].mainline_moves())
        assert nplies == len(moves), f"{gid}: ply count"
        for ply in range(nplies + 1):
            if ply:
                san_expected = b.san(moves[ply - 1])
                b.push(moves[ply - 1])
            cells = []
            for byte in buf[pos : pos + 32]:
                cells += [byte >> 4, byte & 15]
            pos += 32
            for i, c in enumerate(cells):
                p = b.piece_at(chess.square(i % 8, 7 - i // 8))
                assert (SYM.get(c) if c else None) == (p.symbol() if p else None), f"{gid} ply {ply} square {i}"
            frm, to = buf[pos], buf[pos + 1]
            pos += 2
            san, pos = rd_str(buf, pos)
            if ply:
                assert san == san_expected, f"{gid} ply {ply} san"
                mv = moves[ply - 1]
                assert frm == (7 - chess.square_rank(mv.from_square)) * 8 + chess.square_file(mv.from_square)
            note_len = struct.unpack_from("<H", buf, pos)[0]
            buf[pos + 2 : pos + 2 + note_len].decode("utf-8")
            pos += 2 + note_len
        total_plies += nplies
        if gi + 1 < n_games:
            assert pos == offsets[gi + 1], f"{gid}: record length"
    assert pos == len(buf), "trailing bytes"
    print(f"lcc.bin OK: v{version}, {n_games} games, {total_plies} plies, all positions and SAN match")


if __name__ == "__main__":
    main()
