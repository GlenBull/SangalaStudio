"""Build the Sangala Studio package for a Chromebook: sangala-studio_<version>_all.deb

    python tools/chromebook/build_deb.py [output_folder]

The Chromebook counterpart of the Mac .pkg and the Windows setup program. On a Chromebook with Linux
turned on, double-clicking the file in the Files app installs it: tested 2026-09-25 with a probe
package, which showed that the Files app's installer fetches the packages named in Depends (and
theirs), runs the install script as root, and puts a system-wide launcher entry in the ChromeOS
launcher. So this package does everything setup.sh does with sudo, and the only steps left by hand
are the two ChromeOS settings no package can reach: turning on Linux, and sharing the die cutter.

What goes where, and why:

  /usr/share/sangala-studio/   a read-only TEMPLATE of the program. The launcher copies it into the
                               user's own "Sangala Studio" folder, where update.sh can rewrite it -
                               the split the Mac application uses (tools/mac/app-launcher.sh).
  /usr/bin/sangala-studio      the launcher (tools/chromebook/sangala-studio).
  /usr/lib/udev/rules.d/       the rule that lets a normal user open the die cutter. setup.sh puts
                               the same rule in /etc/udev/rules.d; udev lets the /etc copy win when
                               both exist, so a Chromebook set up the old way is unaffected, and a
                               file under /usr/lib is not a conffile, so dpkg never stops to ask.
  /usr/share/applications/     the launcher entry, and /usr/share/icons/... its icon.

Needs dpkg-deb, which every Debian and Ubuntu system has, GitHub's Ubuntu machines included. Every
text file is written with LF line endings, whatever the checkout has.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# (path in the package, source in the repository, mode)
FILES = [
    ("usr/bin/sangala-studio", "tools/chromebook/sangala-studio", 0o755),
    ("usr/share/sangala-studio/sangala_bridge.py", "tools/sangala_bridge.py", 0o644),
    ("usr/share/sangala-studio/update.sh", "tools/chromebook/update.sh", 0o755),
    ("usr/share/sangala-studio/SangalaStudio.html", "SangalaStudio.html", 0o644),
    ("usr/share/sangala-studio/Sangala for Snap.xml", "Sangala for Snap.xml", 0o644),
    ("usr/share/sangala-studio/Calibration Card.svg", "samples/Calibration Card.svg", 0o644),
    ("usr/lib/udev/rules.d/99-silhouette.rules", "tools/chromebook/99-silhouette.rules", 0o644),
    ("usr/share/icons/hicolor/128x128/apps/sangala-studio.png",
     "tools/chromebook/sangala-studio.png", 0o644),
]
# The page's assets travel whole, as the Mac and Windows packages carry them.
ASSETS = "assets"
BINARY = (".png", ".wasm", ".onnx")

DESKTOP = """[Desktop Entry]
Type=Application
Version=1.0
Name=Sangala Studio
GenericName=Digital Fabrication Tool
Comment=Design and cut with a Silhouette die cutter
Exec=/usr/bin/sangala-studio
Icon=sangala-studio
Terminal=false
Categories=Education;Graphics;2DGraphics;
Keywords=Sangala;Silhouette;die cutter;cut;fabrication;
StartupNotify=false
"""

# python3-usb is how the bridge reaches USB (setup.sh installs the same); xdg-utils is how the
# launcher hands the page to Chrome, which setup.sh also installs because the icon depends on it.
CONTROL = """Package: sangala-studio
Version: {version}
Architecture: all
Maintainer: Make to Learn <https://github.com/maketolearn/SangalaStudio>
Depends: python3, python3-usb, xdg-utils
Section: education
Priority: optional
Homepage: https://github.com/maketolearn/SangalaStudio
Description: Sangala Studio - Digital Fabrication Tool
 Design paper models in the browser and make them on a Silhouette die cutter
 over USB. Start it from the ChromeOS launcher; it keeps itself up to date.
"""

# Apply the rule now, so a die cutter already plugged in can be opened without replugging it.
# udevadm's own manual: --reload re-reads the rules, and trigger replays events for existing devices.
POSTINST = """#!/bin/sh
set -e
if [ "$1" = "configure" ]; then
  udevadm control --reload >/dev/null 2>&1 || true
  udevadm trigger --subsystem-match=usb --attr-match=idVendor=0b4d >/dev/null 2>&1 || true
fi
exit 0
"""

POSTRM = """#!/bin/sh
set -e
if [ "$1" = "remove" ] || [ "$1" = "purge" ]; then
  udevadm control --reload >/dev/null 2>&1 || true
fi
exit 0
"""


def read(rel):
    path = os.path.join(REPO, *rel.split("/"))
    if not os.path.isfile(path):
        sys.exit("missing: %s" % rel)
    with open(path, "rb") as f:
        data = f.read()
    return data if rel.endswith(BINARY) else data.replace(b"\r\n", b"\n")


def version():
    """The page's release number, in the form Debian accepts: 2026-09-24.215 -> 2026.09.24.215.
    A hyphen would be read as the start of a Debian revision."""
    head = read("SangalaStudio.html")[:4000].decode("utf-8", "replace")
    m = re.search(r"SANGALA_VERSION:\s*(\d{4})-(\d{2})-(\d{2})\.(\d+)", head)
    if not m:
        sys.exit("no SANGALA_VERSION release number on the page")
    return "%s.%s.%s.%s" % m.groups()


def put(root, rel, data, mode):
    path = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    os.chmod(path, mode)


def main(argv):
    out_dir = os.path.abspath(argv[1] if len(argv) > 1 else os.path.join(REPO, "tools", "chromebook"))
    ver = version()
    root = tempfile.mkdtemp(prefix="sangala-deb-")
    try:
        for dest, src, mode in FILES:
            put(root, dest, read(src), mode)
        for dirpath, dirnames, filenames in os.walk(os.path.join(REPO, ASSETS)):
            for fn in filenames:
                rel = os.path.relpath(os.path.join(dirpath, fn), REPO).replace(os.sep, "/")
                put(root, "usr/share/sangala-studio/" + rel, read(rel), 0o644)
        put(root, "usr/share/applications/sangala-studio.desktop", DESKTOP.encode(), 0o644)
        put(root, "DEBIAN/control", CONTROL.format(version=ver).encode(), 0o644)
        put(root, "DEBIAN/postinst", POSTINST.encode(), 0o755)
        put(root, "DEBIAN/postrm", POSTRM.encode(), 0o755)
        for dirpath, dirnames, filenames in os.walk(root):
            os.chmod(dirpath, 0o755)
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, "sangala-studio_%s_all.deb" % ver)
        subprocess.run(["dpkg-deb", "--root-owner-group", "--build", root, out], check=True)
        print("wrote %s (%.1f MB)" % (out, os.path.getsize(out) / 1e6))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
