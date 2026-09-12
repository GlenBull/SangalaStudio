# -*- coding: utf-8 -*-
"""User Guide Ver 9.2 -> Ver 9.3: Section 11 describes what Fit now does.

Studio 2026-09-12.210 changed two things a reader of Section 11 would notice. Fit used to frame the
PAGE; it now frames the whole workspace, which is the page or the design, whichever is larger - so a
design with pieces parked off the page is framed entire. And the wheel anchors on the pointer while
the plus and minus buttons anchor on the middle, which was not true before and is now exact.

Two run-level edits inside the existing numbered list. No paragraph is added, no heading moves, and
the legacy autospacing on the Fit item is left alone.

    python "tools/docs/edit_ug_93.py"
"""
import os
import re
import shutil
import zipfile

B = r"D:\Code Projects\Silhouette Tools\Documents"
SRC = os.path.join(B, "User Guide (Ver 9.2).docx")
DST = os.path.join(B, "User Guide (Ver 9.3).docx")

EDITS = [
    (" with the mouse wheel, or the plus and minus buttons at the bottom of the ",
     " with the mouse wheel, which magnifies about the pointer, or with the plus and minus buttons "
     "at the bottom of the "),
    ("returns to the whole page. ",
     "frames the whole design, including any pieces that sit outside the page. "),
]

zin = zipfile.ZipFile(SRC)
doc = zin.read("word/document.xml").decode("utf-8")

for old, new in EDITS:
    hits = [m for m in re.finditer(r"(<w:t[^>]*>)([^<]*)(</w:t>)", doc) if m.group(2) == old]
    assert len(hits) == 1, "%r matches %d runs, not 1" % (old[:40], len(hits))
    m = hits[0]
    doc = doc[:m.start(2)] + new + doc[m.end(2):]

# the "which magnify about the middle" tail replaces the bare full stop that closed that item
tail = [m for m in re.finditer(r"(<w:t[^>]*>)([^<]*)(</w:t>)", doc)
        if m.group(2) == ". " and "Fabricate Panel" in doc[max(0, m.start()-400):m.start()]]
assert tail, "could not find the full stop closing the zoom item"
m = tail[0]
doc = doc[:m.start(2)] + ", which magnify about the middle. " + doc[m.end(2):]

text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", doc))
assert "magnifies about the pointer" in text and "magnify about the middle" in text
assert "frames the whole design" in text and "returns to the whole page" not in text

names = zin.namelist()
with zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for x in ["[Content_Types].xml"] + [y for y in names if y != "[Content_Types].xml"]:
        zout.writestr(zin.getinfo(x),
                      doc.encode("utf-8") if x == "word/document.xml" else zin.read(x))
zin.close()
print("wrote", DST, os.path.getsize(DST), "bytes")

arch = os.path.join(B, ".Archive")
os.makedirs(arch, exist_ok=True)
shutil.move(SRC, os.path.join(arch, "User Guide (Ver 9.2).docx"))
print("archived User Guide (Ver 9.2).docx")
