# lcc.bin

The device never parses chess: every position is precomputed, so a move is a lookup and a redraw. All integers are
little-endian; `str` is a u8 byte length followed by UTF-8.

```
header   "LCC1"  u16 version (1)  u16 nGames  u32 spritesOffset  u32[nGames] gameOffsets
sprites  u16 size (60), then 12 pieces in order PNBRQKpnbrqk, each [ink bitmap][halo mask]:
         1 bit per pixel, rows padded to whole bytes. The halo is the dilated piece shape, cleared to white
         on dark (hatched) squares so pieces stay legible on a 1-bit panel.
game     u8 number  u8 part  u16 year
         str id  str white  str black  str event  str opening  str partTitle  str result
         u16 nPlies, then nPlies + 1 positions (position 0 is the start):
           32 B board   4 bits per square, a8..h1 row-major, high nibble first;
                        0 empty, 1-6 white PNBRQK, 9-14 black pnbrqk
           u8 from, u8 to   last move's squares (0 = a8 ... 63 = h1; 255 = none)
           str san
           u16 noteLen + note bytes (UTF-8, paragraphs separated by a blank line)
```

The device reads the header, sprites and the first 512 bytes of each game (names for the games list) on open, the
current game next, and the rest in the background while idle. `tools/check_lcc.py` is an independent parser that
replays every game with python-chess and checks each stored board, move squares and SAN.
