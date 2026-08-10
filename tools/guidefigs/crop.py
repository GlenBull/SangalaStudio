"""Crop and compose the screenshots with PyMuPDF (no Pillow on this machine).

A PNG opens as a one-page document, so get_pixmap(clip=...) crops it and a fresh page with several
images placed on it composes them. Coordinates are in the SHOT's own pixels.
"""
import os
import fitz

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")


def size(name):
    d = fitz.open(os.path.join(D, name + ".png"))
    r = d[0].rect
    return int(r.width), int(r.height)


def crop(src, dst, x0, y0, x1, y1, scale=1.0):
    d = fitz.open(os.path.join(D, src + ".png"))
    pm = d[0].get_pixmap(clip=fitz.Rect(x0, y0, x1, y1), matrix=fitz.Matrix(scale, scale))
    pm.save(os.path.join(D, dst + ".png"))
    return pm.width, pm.height


def crop_px(src, dst, x0, y0, x1, y1):
    """Crop in the source PNG's OWN pixels, and write out at that same resolution.

    PyMuPDF measures an image in points using whatever dpi the file declares - a 96 dpi screenshot
    and a 200 dpi page render therefore need different factors, which is a trap worth removing:
    the ratio is derived here instead of being passed in.
    """
    path = os.path.join(D, src + ".png")
    d = fitz.open(path)
    with open(path, "rb") as f:
        head = f.read(32)
    w = int.from_bytes(head[16:20], "big")          # PNG IHDR width, the file's true pixels
    k = d[0].rect.width / w                          # points per pixel
    pm = d[0].get_pixmap(clip=fitz.Rect(x0 * k, y0 * k, x1 * k, y1 * k),
                         matrix=fitz.Matrix(1 / k, 1 / k))
    pm.save(os.path.join(D, dst + ".png"))
    return pm.width, pm.height


def content_box(name, margin=18, white=246):
    """Pixel bounding box of everything that is not the white workspace, plus a margin."""
    d = fitz.open(os.path.join(D, name + ".png"))
    pm = d[0].get_pixmap(matrix=fitz.Matrix(4.0 / 3.0, 4.0 / 3.0))
    w, h, n, s = pm.width, pm.height, pm.n, pm.samples
    x0, y0, x1, y1 = w, h, 0, 0
    for y in range(h):
        base = y * pm.stride
        for x in range(w):
            i = base + x * n
            if s[i] < white or s[i + 1] < white or s[i + 2] < white:
                if x < x0: x0 = x
                if x > x1: x1 = x
                if y < y0: y0 = y
                if y > y1: y1 = y
    if x1 < x0:
        return 0, 0, w, h
    return (max(0, x0 - margin), max(0, y0 - margin),
            min(w, x1 + margin + 1), min(h, y1 + margin + 1))


def row(srcs, dst, gap=24, bg=(1, 1, 1)):
    """Place several images side by side, tops aligned, on one white canvas."""
    imgs = [fitz.open(os.path.join(D, s + ".png")) for s in srcs]
    ws = [int(i[0].rect.width) for i in imgs]
    hs = [int(i[0].rect.height) for i in imgs]
    W, H = sum(ws) + gap * (len(imgs) - 1), max(hs)
    out = fitz.open()
    page = out.new_page(width=W, height=H)
    page.draw_rect(fitz.Rect(0, 0, W, H), color=bg, fill=bg)
    x = 0
    for s, w, h in zip(srcs, ws, hs):
        page.insert_image(fitz.Rect(x, 0, x + w, h), filename=os.path.join(D, s + ".png"))
        x += w + gap
    # the page was laid out in POINTS, so render at 4/3 to come back out at the images' own pixels
    pm = page.get_pixmap(matrix=fitz.Matrix(4.0 / 3.0, 4.0 / 3.0))
    pm.save(os.path.join(D, dst + ".png"))
    return pm.width, pm.height


if __name__ == "__main__":
    for n in ("screen", "palette", "medium_tiles", "medium_dots", "medium_beads"):
        print("%-16s %s" % (n, size(n)))
