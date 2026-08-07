"""Build "Sangala Studio for Chromebook.zip" from the repository.

    python tools/chromebook/build_zip.py [output_folder]

The zip used to be assembled by hand, which is how its copies of setup.sh, the udev rule and the
Read Me drifted out of the repository - two of those three existed ONLY inside the zip. Everything
it contains now has a tracked source, so rebuilding is repeatable and a change can be reviewed as a
diff rather than by unzipping.

Two things this handles that a plain zip command would not:

  * LINE ENDINGS. The target is Linux. Every text member is written with LF, whatever the working
    copy has, because a setup.sh with CRLF fails on the Chromebook with an unreadable error about
    '\\r'. Binary members (the wasm, the ONNX model, the icon) are copied byte for byte.

  * THE BRIDGE IS ON ANOTHER BRANCH. sangala_bridge.py lives on mac-bridge, which Glen has kept
    unmerged. It is read with `git show mac-bridge:tools/sangala_bridge.py` rather than from the
    working tree, so the zip cannot pick up whatever branch happens to be checked out. When
    mac-bridge is merged, drop BRIDGE_REF and read it from the tree like everything else.
"""

import os
import subprocess
import sys
import zipfile

BRIDGE_REF = "mac-bridge:tools/sangala_bridge.py"
ZIP_NAME = "Sangala Studio for Chromebook.zip"

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CB = os.path.join(REPO, "tools", "chromebook")

# (path in the zip, source on disk relative to the repo). Order is the order a person unzipping sees.
TEXT = [
    ("Read Me First.txt", "tools/chromebook/Read Me First.txt"),
    ("setup.sh", "tools/setup_chromebook.sh"),
    ("99-silhouette.rules", "tools/chromebook/99-silhouette.rules"),
    ("SangalaStudio.html", "SangalaStudio.html"),
    ("Sangala for Snap.xml", "Sangala for Snap.xml"),
    ("Calibration Card.svg", "samples/Calibration Card.svg"),
    ("assets/imagetracer_v1.2.6.js", "assets/imagetracer_v1.2.6.js"),
    ("assets/NOTICE.md", "assets/NOTICE.md"),
    ("assets/ort-wasm-simd-threaded.mjs", "assets/ort-wasm-simd-threaded.mjs"),
    ("assets/ort.wasm.min.js", "assets/ort.wasm.min.js"),
    ("assets/trace-engine.js", "assets/trace-engine.js"),
    ("assets/licenses/imagetracer-Unlicense.txt", "assets/licenses/imagetracer-Unlicense.txt"),
    ("assets/licenses/onnxruntime-web-MIT.txt", "assets/licenses/onnxruntime-web-MIT.txt"),
    ("assets/licenses/u2netp-Apache-2.0.txt", "assets/licenses/u2netp-Apache-2.0.txt"),
]
BINARY = [
    ("sangala-studio.png", "tools/chromebook/sangala-studio.png"),
    ("assets/ort-wasm-simd-threaded.wasm", "assets/ort-wasm-simd-threaded.wasm"),
    ("assets/u2netp.onnx", "assets/u2netp.onnx"),
]


def lf(raw):
    """Normalise to LF without touching anything else."""
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def read(rel):
    path = os.path.join(REPO, rel)
    if not os.path.isfile(path):
        sys.exit("missing: %s" % rel)
    with open(path, "rb") as f:
        return f.read()


def bridge_bytes():
    try:
        out = subprocess.run(["git", "-C", REPO, "show", BRIDGE_REF],
                             capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        sys.exit("could not read %s from git (%s)" % (BRIDGE_REF, e))
    if b"class Cutter" not in out:
        sys.exit("%s does not look like the bridge" % BRIDGE_REF)
    return lf(out)


def main(argv):
    out_dir = argv[1] if len(argv) > 1 else CB
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, ZIP_NAME)

    members = []
    for name, rel in TEXT:
        members.append((name, lf(read(rel))))
    members.append(("sangala_bridge.py", bridge_bytes()))
    for name, rel in BINARY:
        members.append((name, read(rel)))

    # Order the members the way the old zip listed them: the three files a person needs first, the
    # bridge, then the page and its assets.
    order = ["Read Me First.txt", "setup.sh", "99-silhouette.rules", "sangala-studio.png",
             "sangala_bridge.py", "SangalaStudio.html", "Sangala for Snap.xml",
             "Calibration Card.svg"]
    members.sort(key=lambda m: (order.index(m[0]) if m[0] in order else len(order), m[0]))

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in members:
            # A fixed timestamp keeps the zip byte-identical when nothing inside it changed, so a
            # rebuild that ships nothing new is visible as such.
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if name.endswith(".sh") else 0o644) << 16
            z.writestr(info, data)

    total = sum(len(d) for _, d in members)
    print("wrote %s" % out_path)
    print("  %d files, %s uncompressed, %s packed"
          % (len(members), fmt(total), fmt(os.path.getsize(out_path))))
    for name, data in members:
        crlf = b"\r\n" in data and not name.endswith((".png", ".wasm", ".onnx"))
        print("   %9d  %s%s" % (len(data), name, "   <-- CRLF!" if crlf else ""))
    return 0


def fmt(n):
    return "%.1f MB" % (n / 1048576.0) if n > 1048576 else "%.0f KB" % (n / 1024.0)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
