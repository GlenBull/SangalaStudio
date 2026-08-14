"""Build "Sangala Studio for Mac.zip" from the repository.

    python tools/mac/build_zip.py [output_folder]

The companion of tools/chromebook/build_zip.py, and it exists for the same reason: the zip that
went to Moses in August was assembled by hand, and its Read Me First.txt existed ONLY inside the
zip - there was no tracked copy to review or revise. Everything here has a source in the
repository, so rebuilding is repeatable and a change to the kit is a diff.

Two things this handles that a plain zip command would not:

  * THE EXECUTABLE BIT. Finder runs a .command file on a double-click only if it is marked
    executable, and that mark has to survive the round trip through the zip. Both launchers are
    written with mode 755; everything else is 644.

  * LINE ENDINGS, and THE BRANCH. The target is macOS, so every text member is written with LF -
    a .command with CRLF fails with an unreadable complaint about '\\r'. The engine and the two
    launchers live on the mac-bridge branch, which Glen has kept unmerged, so they are read with
    `git show mac-bridge:...` rather than from the working tree: the kit cannot then depend on
    which branch happens to be checked out. When mac-bridge is merged, drop GIT_MEMBERS and read
    them from the tree like everything else.

The default output folder is the Mac folder in Dropbox, because that is where Moses fetches it.
"""

import os
import subprocess
import sys
import zipfile

ZIP_NAME = "Sangala Studio for Mac.zip"
BRANCH = "mac-bridge"

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DROPBOX = os.path.join(os.path.expanduser("~"), "UVa Lab School Dropbox", "AI Sandbox",
                       "Design through Making", "Sangala Tools", "Other Platforms", "Mac")

# (path in the zip, path on the mac-bridge branch). These are the Mac-only files.
GIT_MEMBERS = [
    ("Sangala Studio.command", "Sangala Studio.command"),
    ("Update Sangala Studio.command", "Update Sangala Studio.command"),
    ("sangala_bridge.py", "tools/sangala_bridge.py"),
]
# (path in the zip, source on disk relative to the repo). Order is the order a person unzipping
# sees. The engine sits BESIDE the page here, not in tools/ - the launchers accept either, and a
# flat folder is kinder to someone who has just unzipped it.
TEXT = [
    ("Read Me First.txt", "tools/mac/Read Me First.txt"),
    ("mac_usb_probe.py", "tools/mac_usb_probe.py"),
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
    ("assets/ort-wasm-simd-threaded.wasm", "assets/ort-wasm-simd-threaded.wasm"),
    ("assets/u2netp.onnx", "assets/u2netp.onnx"),
]

# What each member must contain to count as itself. A download that quietly returned an error page,
# or a path that has moved, is caught here rather than on Moses's Mac.
SIGNATURE = {
    "Sangala Studio.command": b"exec \"$PY\"",
    "Update Sangala Studio.command": b"raw.githubusercontent.com",
    "sangala_bridge.py": b"class Cutter",
    "SangalaStudio.html": b"</html>",
    "Sangala for Snap.xml": b"<blocks",
}


def lf(raw):
    """Normalize to LF without touching anything else."""
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def read(rel):
    path = os.path.join(REPO, rel)
    if not os.path.isfile(path):
        sys.exit("missing: %s" % rel)
    with open(path, "rb") as f:
        return f.read()


def from_git(rel):
    ref = "%s:%s" % (BRANCH, rel)
    try:
        out = subprocess.run(["git", "-C", REPO, "show", ref],
                             capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        sys.exit("could not read %s from git (%s)" % (ref, e))
    return lf(out)


def main(argv):
    out_dir = argv[1] if len(argv) > 1 else DROPBOX
    if not os.path.isdir(out_dir):
        sys.exit("no such folder: %s" % out_dir)
    out_path = os.path.join(out_dir, ZIP_NAME)

    members = []
    for name, rel in GIT_MEMBERS:
        members.append((name, from_git(rel)))
    for name, rel in TEXT:
        members.append((name, lf(read(rel))))
    for name, rel in BINARY:
        members.append((name, read(rel)))

    for name, data in members:
        sig = SIGNATURE.get(name)
        if sig is not None and sig not in data:
            sys.exit("%s does not look like itself (no %r)" % (name, sig))

    # The order a person unzipping sees: what to read, what to double-click, then the program.
    order = ["Read Me First.txt", "Sangala Studio.command", "Update Sangala Studio.command",
             "sangala_bridge.py", "mac_usb_probe.py", "SangalaStudio.html",
             "Sangala for Snap.xml", "Calibration Card.svg"]
    members.sort(key=lambda m: (order.index(m[0]) if m[0] in order else len(order), m[0]))

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in members:
            # A fixed timestamp keeps the zip byte-identical when nothing inside it changed, so a
            # rebuild that ships nothing new is visible as such.
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            # 755 on the launchers or Finder will not run them on a double-click...
            mode = 0o755 if name.endswith(".command") else 0o644
            # ...and the mode alone is not enough. A zip records WHICH KIND OF SYSTEM wrote it, and an
            # extractor honours the Unix mode only when that says Unix. Python stamps the host from the
            # machine it runs on, so a zip built here declared itself DOS/FAT and every Unix mode in it
            # was ignored: Moses's Mac unpacked the launchers without the executable bit and macOS
            # refused them with "you do not have appropriate access privileges" before Gatekeeper was
            # ever reached - and Finder's Get Info has no execute checkbox to repair it with.
            # create_system 3 is Unix. S_IFREG marks a regular file, which some extractors require
            # before they will read the mode at all. Verify with `unzip -Z`: the host column must read
            # "unix" and the launchers "-rwxr-xr-x". "fat" means this is broken again.
            info.create_system = 3
            info.external_attr = (0o100000 | mode) << 16
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
