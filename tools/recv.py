"""Receive a canvas image from a page and write it to disk, so a render can be LOOKED at.

The browser pane will not composite frames, so screenshots of it fail. The way that works: draw the
canvas onto a smaller one in the page, toDataURL it, POST the base64 here, then open the file with
the Read tool. Verifying 3D by measuring geometry does not work - numbers cannot see shape.

    python tools/recv.py 3        # wait for 3 images, then exit

In the page:
    await fetch("http://localhost:8899/name.png", {method:"POST", mode:"no-cors",
      headers:{"Content-Type":"text/plain"}, body: canvas.toDataURL("image/png")});

Writes to assets/_tmp-<name>.<ext>. Delete the staged files afterward.
"""

import base64, sys, os
from http.server import BaseHTTPRequestHandler, HTTPServer

OUTDIR = r"D:\Code Projects\Silhouette Tools\assets"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 1
count = {"n": 0}

class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
    def do_OPTIONS(self):
        self.send_response(200); self._cors(); self.end_headers()
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n).decode("utf-8", "replace")
        name = self.path.strip("/") or ("shot%d" % count["n"])
        if "," in raw:
            raw = raw.split(",", 1)[1]
        ext = "png" if "png" in (self.path + raw[:20]).lower() else "jpg"
        path = os.path.join(OUTDIR, "_tmp-%s.%s" % (name, ext))
        try:
            open(path, "wb").write(base64.b64decode(raw))
            print("WROTE", path, os.path.getsize(path), "bytes", flush=True)
        except Exception as e:
            print("FAIL", e, flush=True)
        self.send_response(200); self._cors()
        self.send_header("Content-Type", "text/plain"); self.end_headers()
        self.wfile.write(b"ok")
        count["n"] += 1
        if count["n"] >= N:
            print("DONE", flush=True)
            import threading; threading.Thread(target=self.server.shutdown).start()
    def log_message(self, *a):
        pass

srv = HTTPServer(("127.0.0.1", 8899), H)
print("listening on 8899 for", N, "image(s)", flush=True)
srv.serve_forever()
print("exited", flush=True)
