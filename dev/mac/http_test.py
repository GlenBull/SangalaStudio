"""Exercise the bridge's HTTP surface. No machine: every route that needs one must refuse politely.

Runs on a spare port so the real SangalaStudio.exe bridge in the tray is left alone.
"""
import os, sys, json, threading, urllib.request, urllib.error
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                os.pardir, os.pardir, "tools"))
import sangala_bridge as B
from http.server import ThreadingHTTPServer

fails = []


def check(name, got, want):
    if got != want:
        fails.append(name)
        print("FAIL %s\n  got  %r\n  want %r" % (name, got, want))
    else:
        print("ok   %s" % name)


B.ROOT = B.find_root()
check("found the repo root", B.ROOT is not None, True)

srv = ThreadingHTTPServer(("127.0.0.1", 0), B.Handler)
srv.daemon_threads = True
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = "http://127.0.0.1:%d" % PORT


def get(path, data=None, method=None):
    req = urllib.request.Request(URL + path, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


# ---- the page
st, body, hdr = get("/")
check("GET / status", st, 200)
check("GET / is the page", body.rstrip().endswith(b"</html>"), True)
check("GET / content type", hdr["Content-Type"], "text/html; charset=utf-8")
check("GET / no-store", hdr["Cache-Control"], "no-store")
check("GET /index.html", get("/index.html")[0], 200)

# ---- assets
st, body, hdr = get("/assets/trace-engine.js")
check("asset served", st, 200)
check("asset mime", hdr["Content-Type"], "text/javascript; charset=utf-8")
st, body, hdr = get("/assets/u2netp.onnx")
check("onnx served", st, 200)
check("onnx has NO charset", hdr["Content-Type"], "application/octet-stream")
check("onnx size", len(body), 4574861)
check("asset traversal refused", get("/assets/../SangalaServer.cs")[0], 400)
check("missing asset 404", get("/assets/nope.js")[0], 404)

# ---- status is answerable with no machine, and must never block
st, body, _ = get("/status")
check("status", (st, json.loads(body)), (200, {"status": "idle"}))

# ---- machine routes refuse politely rather than crashing
st, body, _ = get("/cut", data=b"33,8,3,0\n1,2 3,4")
j = json.loads(body)
check("cut without a machine", (st, j["ok"], j["error"]),
      (200, False, "Not connected to the Die Cutter."))
for r in ("/scan", "/printcut", "/manualstart", "/jog", "/manualread", "/manualcut", "/unload", "/raw"):
    j = json.loads(get(r, data=b"")[1])
    check("%s refuses" % r, (j["ok"], j["error"]), (False, "Not connected to the Die Cutter."))

# /connect reports why it cannot reach a machine -- the message a Mac user will actually see
j = json.loads(get("/connect")[1])
check("connect fails cleanly", j["ok"], False)
print("     connect says: %s" % j["error"])

# a malformed body must come back as an error, not a stack trace
S = B.S
S.cutter = object()                                   # pretend we are connected
j = json.loads(get("/cut", data=b"nonsense\n1,2 3,4")[1])
check("bad header reported", (j["ok"], j["error"]), (False, "Bad settings header: 'nonsense'"))
j = json.loads(get("/cut", data=b"33,8,3,0\n1,2 zz")[1])
check("bad point reported", (j["ok"], "Bad point at line 1" in j["error"]), (False, True))
j = json.loads(get("/cut", data=b"33,8,3,0")[1])
check("no design reported", (j["ok"], j["error"]), (False, "No design received."))
j = json.loads(get("/cut", data=b"33,8,3,0\n\n")[1])
check("empty design reported", (j["ok"], j["error"]), (False, "No cut paths in the design."))
S.cutter = None

# ---- Snap! bridge: post a drawing, collect it once, and it is gone
check("snap spike starts empty", get("/snap/svg")[1], b"")
check("snap post", get("/snap/svg", data=b"<svg/>")[1], b"ok")
st, body, hdr = get("/snap/svg")
check("snap collect", body, b"<svg/>")
check("snap CORS", hdr["Access-Control-Allow-Origin"], "*")
check("snap private network", hdr["Access-Control-Allow-Private-Network"], "true")
check("snap spike cleared", get("/snap/svg")[1], b"")
st, body, hdr = get("/", method="OPTIONS")
check("preflight", (st, hdr["Access-Control-Allow-Methods"]), (200, "GET, POST, OPTIONS"))
check("snap library", get("/snap/library.xml")[1].lstrip().startswith(b"<blocks"), True)

# ---- unknown route
check("unknown route 404", get("/nope")[0], 404)

srv.shutdown()
print()
print("FAILURES: %d" % len(fails))
sys.exit(1 if fails else 0)
