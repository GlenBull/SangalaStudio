"""Screenshot Sangala Studio headlessly, the same way as Sangala Mosaic.

One difference matters: the page probes the bridge on load and, if it answers, replaces itself with
the served copy - which would throw away the setup script. The temporary copy therefore points that
one probe at a port nothing listens on. Nothing else is altered, so what is captured is the real
page in a real browser.
"""
import json, os, subprocess, sys, tempfile

APP = r"D:\Code Projects\Silhouette Tools\SangalaStudio.html"
PROJ = r"D:\Code Projects\Silhouette Tools\Projects"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
EDGE = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]

SETUP = """
<script>
(async () => {
  const wait = ms => new Promise(r => setTimeout(r, ms));
  await wait(300);
  %s
  document.title = "SHOT-READY";
})();
</script>
"""

OPEN_FILE = """
  const f = new File([%s], "%s", {type: "%s"});
  const dt = new DataTransfer(); dt.items.add(f);
  const inp = document.getElementById("file");
  inp.files = dt.files;
  inp.dispatchEvent(new Event("change", {bubbles: true}));
  await wait(1500);
"""


def edge():
    for p in EDGE:
        if os.path.exists(p):
            return p
    raise SystemExit("Microsoft Edge not found")


def page_source(extra):
    html = open(APP, encoding="utf-8").read()
    hop = 'fetch("http://localhost:8787/"'
    assert hop in html, "the bridge probe moved - check before disabling it"
    html = html.replace(hop, 'fetch("http://localhost:9/"', 1)   # nothing listens on port 9
    return html + SETUP % extra


def shoot(name, extra="", size=(1500, 950), settle=3500):
    os.makedirs(OUT, exist_ok=True)
    png = os.path.join(OUT, name + ".png")
    if os.path.exists(png):
        os.remove(png)
    with tempfile.TemporaryDirectory() as tmp:
        page = os.path.join(tmp, "shot.html")
        open(page, "w", encoding="utf-8").write(page_source(extra))
        subprocess.run([edge(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=2", "--virtual-time-budget=%d" % settle,
                        "--screenshot=" + png, "--window-size=%d,%d" % size,
                        "file:///" + page.replace("\\", "/")],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    print("%-18s %s" % (name, "%d bytes" % os.path.getsize(png) if os.path.exists(png) else "NOT WRITTEN"))
    return png


def open_project(fname, mime="application/json"):
    text = open(os.path.join(PROJ, fname), encoding="utf-8").read()
    return OPEN_FILE % (json.dumps(text), fname, mime)


if __name__ == "__main__":
    shoot("studio_plain")
