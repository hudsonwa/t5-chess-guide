# Position sync service

One JSON record (`game`, `ply`, `flipped`, `updated_at` in ms, `device`), last write wins by `updated_at`.
`GET /state`, `PUT /state`, `GET /health`. Standard library only.

```bash
PORT=8120 LCC_SYNC_DATA=state.json python server.py
python test_server.py
```

It has no authentication: run it on a private network (LAN or a VPN such as Tailscale), not the internet.
