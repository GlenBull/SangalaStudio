"""
Parity reference: run rembg's u2netp on an image and save the raw grayscale MASK
(original size), so the in-browser port can be compared against it.

This is DEV-TIME ONLY (rembg is never shipped). It uses the committed offline model
at assets/u2netp.onnx via U2NET_HOME, so it needs no network.

Usage: python reference.py <input_image> <output_mask.png>
"""
import os, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.environ.setdefault("U2NET_HOME", os.path.join(REPO, "assets"))  # our committed u2netp.onnx
os.environ.setdefault("MODEL_CHECKSUM_DISABLED", "1")               # use the local file as-is, no re-download

from rembg import new_session
from PIL import Image


def main():
    if len(sys.argv) < 3:
        print("Usage: python reference.py <input_image> <output_mask.png>")
        sys.exit(1)
    src, out = sys.argv[1], sys.argv[2]
    session = new_session("u2netp")
    img = Image.open(src)
    mask = session.predict(img)[0]        # grayscale 'L' mask at original size (rembg's own pre/post)
    mask.save(out)
    print(f"wrote {out}  size={mask.size}  mode={mask.mode}")


if __name__ == "__main__":
    main()
