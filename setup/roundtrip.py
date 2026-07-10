#!/usr/bin/env python3
"""Replace the first embedded image in a .docx with a marker PNG, repack, and
assert the image round-trips byte-for-byte. Used by setup-windows.ps1 verification.

Usage: python roundtrip.py <in.docx> <marker.png> <out.docx>
"""
import sys
import zipfile


def main():
    src, marker, out = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(marker, "rb") as fh:
        mb = fh.read()

    zin = zipfile.ZipFile(src)
    img = next((n for n in zin.namelist() if n.startswith("word/media/")), None)
    if not img:
        print("  !!  fixture has no embedded image", file=sys.stderr)
        sys.exit(1)

    # rewrite the archive, swapping just the one image part
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            data = zin.read(it.filename)
            zout.writestr(it, mb if it.filename == img else data)
    zin.close()

    z = zipfile.ZipFile(out)
    ok = z.read(img) == mb
    z.close()
    if not ok:
        print("  !!  image did not round-trip byte-for-byte", file=sys.stderr)
        sys.exit(1)
    print("  OK  replaced %s and verified byte-for-byte round-trip" % img)


if __name__ == "__main__":
    main()
