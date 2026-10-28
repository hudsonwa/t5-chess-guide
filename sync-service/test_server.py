"""Run: python3 sync-service/test_server.py  (starts the server on a free port with a temp data file)."""
import json, os, socket, subprocess, sys, tempfile, time, urllib.request

def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

def req(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

port = free_port(); tmp = tempfile.mkdtemp()
env = dict(os.environ, PORT=str(port), LCC_SYNC_DATA=os.path.join(tmp, "state.json"))
proc = subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "server.py")], env=env)
base = f"http://127.0.0.1:{port}"
try:
    for _ in range(50):
        try:
            if req("GET", base + "/health")[0] == 200: break
        except OSError: time.sleep(0.1)
    assert json.loads(req("GET", base + "/state")[1]) == {}
    a = {"game": "game-03", "ply": 12, "mode": "book", "flipped": False, "updated_at": 1000, "device": "web"}
    assert json.loads(req("PUT", base + "/state", a)[1]) == a
    old = dict(a, ply=2, updated_at=999, device="t5")
    assert json.loads(req("PUT", base + "/state", old)[1]) == a, "older write must lose"
    new = dict(a, ply=14, updated_at=1001, device="t5")
    assert json.loads(req("PUT", base + "/state", new)[1]) == new
    assert json.loads(req("GET", base + "/state")[1]) == new
    assert req("PUT", base + "/state", {"ply": 1})[0] == 400
    assert req("PUT", base + "/state", dict(a, ply=True, updated_at=2000))[0] == 400
    assert req("PUT", base + "/state", dict(a, extra="x" * 4000))[0] == 413
    assert json.loads(req("PUT", base + "/state", dict(a, junk=1, updated_at=3000))[1]).get("junk") is None
    print("sync-service tests: all passed")
finally:
    proc.terminate()
