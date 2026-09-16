"""Puts a photograph behind the title slide. Ver 2.1 -> Ver 2.2.

Glen: "we need an image for the title slide."

VER 2.1 IS GLEN'S, not mine - he retitled slide 1 to "NTLS Networked Weather Station". So this EDITS
his file rather than regenerating from my Ver 2.0, which would have thrown that away. The only slide
touched is the first; his wording is kept exactly and only moved, resized and recoloured so it reads
over the photograph.

The photograph is photo_07 from the album: a deep valley between two ridges, the far slope farmed to
the top and dotted with homesteads. It shows in one frame what the network has to cover, and it reads
from the back of a room. It is not used anywhere else in the deck.
"""
import copy
import os
import sys

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

DRAFTS = (r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts")
SRC = os.path.join(DRAFTS, "Networked Weather Station (Ver 2.1).pptx")
OUT = os.path.join(DRAFTS, "Networked Weather Station (Ver 2.2).pptx")
PHOTO = os.path.join(DRAFTS, "Working", "NTLS Photos", "photo_07.jpg")

PAPER = RGBColor(0xFF, 0xFF, 0xFF)


def to_back(shape, index=0):
    """Move a shape to the given position in the tree; 0 puts it behind everything."""
    tree = shape._element.getparent()
    tree.remove(shape._element)
    tree.insert(index + 2, shape._element)        # +2: nvGrpSpPr and grpSpPr come first


def main():
    if os.path.exists(OUT):
        sys.exit("refusing to overwrite " + OUT)
    if not os.path.exists(PHOTO):
        sys.exit("missing " + PHOTO)

    prs = Presentation(SRC)
    W, H = prs.slide_width, prs.slide_height
    slide = prs.slides[0]

    # --- the photograph, filling the slide, cropped rather than distorted ---
    from PIL import Image
    iw, ih = Image.open(PHOTO).size
    sw, sh = W / 914400.0, H / 914400.0
    scale = max(sw / iw, sh / ih)
    w, h = iw * scale, ih * scale
    pic = slide.shapes.add_picture(PHOTO, Inches((sw - w) / 2), Inches((sh - h) / 2),
                                   Inches(w), Inches(h))
    to_back(pic, 0)

    # --- a band across the foot so white type reads over the hillside ---
    band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, H - Inches(2.3), W, Inches(2.3))
    band.fill.solid()
    band.fill.fore_color.rgb = RGBColor(0, 0, 0)
    band.line.fill.background()
    band.shadow.inherit = False
    to_back(band, 1)

    # --- HIS title text, kept word for word; only placed and coloured ---
    title = mark = None
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        t = sh.text_frame.text.strip()
        if t == "0:00":
            mark = sh
        elif t:
            title = sh
    if title is None:
        sys.exit("could not find the title text box on slide 1")
    print("title kept as:", repr(title.text_frame.text))

    title.left, title.top = Inches(0.7), H - Inches(2.0)
    title.width, title.height = W - Inches(1.4), Inches(1.1)
    for p in title.text_frame.paragraphs:
        for r in p.runs:
            r.font.size = Pt(46)
            r.font.bold = True
            r.font.color.rgb = PAPER

    sub = slide.shapes.add_textbox(Inches(0.75), H - Inches(1.0), W - Inches(1.4), Inches(0.6))
    sr = sub.text_frame.paragraphs[0].add_run()
    sr.text = "Mount Elgon, eastern Uganda"
    sr.font.size = Pt(22)
    sr.font.color.rgb = PAPER
    sr.font.name = "Segoe UI"

    if mark is not None:
        for p in mark.text_frame.paragraphs:
            for r in p.runs:
                r.font.color.rgb = PAPER

    prs.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
