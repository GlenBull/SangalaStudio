"""
Parity regression test: prove the in-browser u2netp port (trace-engine.js) matches
rembg's u2netp. Runs the SAME image through both and compares the masks by IoU.

DEV-TIME ONLY (needs rembg + a Chromium/Edge). Uses the committed offline model
assets/u2netp.onnx for both sides. Run after any change to trace-engine.js's
preprocessing/postprocessing.

Usage: python parity_check.py [image]   (defaults to the Ch 1 Giraffe collage)
Exit code 0 = PASS (IoU >= 0.95), 1 = FAIL.
"""
import os, sys, subprocess, base64, io, re
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
os.environ.setdefault("U2NET_HOME", os.path.join(REPO, "assets"))
os.environ.setdefault("MODEL_CHECKSUM_DISABLED", "1")

PASS_IOU = 0.95


def find_edge():
    for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
        if os.path.exists(p):
            return p
    raise SystemExit("msedge.exe not found")


def python_mask(src):
    from rembg import new_session
    sess = new_session("u2netp")
    return sess.predict(Image.open(src))[0].convert("L")


def browser_mask(src):
    import shutil, time
    Image.open(src).convert("RGB").save(os.path.join(HERE, "_input.png"))
    prof = os.path.join(HERE, "_edgeprof"); shutil.rmtree(prof, ignore_errors=True)
    log = os.path.join(HERE, "_edgelog.txt")
    url = "file:///" + os.path.join(HERE, "browser.html").replace("\\", "/")
    # Run headed-less Edge that stays open; the page console.logs the mask in chunks.
    # We capture stderr and poll for the END marker, then terminate (deterministic).
    with open(log, "wb") as errf:
        proc = subprocess.Popen([find_edge(), "--headless=old", "--disable-gpu", "--no-sandbox",
                                 "--allow-file-access-from-files", "--user-data-dir=" + prof,
                                 "--enable-logging=stderr", "--v=1", url],
                                stdout=subprocess.DEVNULL, stderr=errf)
        try:
            deadline = time.time() + 120
            while time.time() < deadline:
                time.sleep(1)
                d = open(log, encoding="utf-8", errors="ignore").read()
                if "SANGALA_MASK_END" in d or "SANGALA_STATUS ERR" in d:
                    break
        finally:
            proc.terminate()
            try: proc.wait(timeout=10)
            except Exception: proc.kill()
    d = open(log, encoding="utf-8", errors="ignore").read()
    status = re.search(r"SANGALA_STATUS (.+)", d)
    status = status.group(1).strip()[:90] if status else "(no status)"
    begin = re.search(r"SANGALA_MASK_BEGIN \S+ len=(\d+)", d)
    chunks = re.findall(r"SANGALA_MASK ([A-Za-z0-9+/=]+)", d)
    if not chunks:
        raise SystemExit("browser produced no mask. status = " + status + " | tail: " + d[-300:])
    b64 = "".join(chunks)
    if begin and int(begin.group(1)) != len(b64):
        raise SystemExit("mask truncated: expected %s chars, got %d (console truncation?)" % (begin.group(1), len(b64)))
    return Image.open(io.BytesIO(base64.b64decode(b64))).convert("L"), status


def _iou(a, b, thr=128):
    A, B = np.array(a) >= thr, np.array(b) >= thr
    inter, union = np.logical_and(A, B).sum(), np.logical_or(A, B).sum()
    return (inter / union) if union else 1.0


def compare(a, b, thr=128):
    if a.size != b.size:
        b = b.resize(a.size)
    iou = _iou(a, b, thr)
    mad = np.abs(np.array(a, np.int32) - np.array(b, np.int32)).mean()
    agree = (np.array(a) >= thr) == (np.array(b) >= thr)
    # diagnostic: IoU at the model-native 320x320 (isolates the output up-resize)
    iou320 = _iou(a.resize((320, 320), Image.Resampling.LANCZOS), b.resize((320, 320), Image.Resampling.LANCZOS), thr)
    return iou, agree.mean(), mad, iou320


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.expanduser("~"), "UVa Lab School Dropbox", "AI Sandbox",
        "Design through Making", "Images", "Ch 1 Images", "Giraffe.jpeg")
    print("image  :", src)
    pm = python_mask(src); pm.save(os.path.join(HERE, "_mask_py.png"))
    bm, status = browser_mask(src); bm.save(os.path.join(HERE, "_mask_browser.png"))
    print("browser:", status)
    iou, agree, mad, iou320 = compare(pm, bm)
    print("IoU(full) = %.4f   IoU(@320) = %.4f   pixel-agree = %.4f   mean|diff| = %.2f/255" % (iou, iou320, agree, mad))
    ok = iou >= PASS_IOU
    print("PARITY:", "PASS" if ok else "FAIL", "(threshold IoU >= %.2f)" % PASS_IOU)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
