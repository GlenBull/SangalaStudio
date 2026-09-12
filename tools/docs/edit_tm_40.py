# -*- coding: utf-8 -*-
"""Tech Manual Ver 3.9 -> Ver 4.0: two British spellings corrected to American.

The paragraphs added at 3.9 used "centres" and "centring". The house rule is American spelling
everywhere - documents, code comments and interface text alike - so they become "centers" and
"centering". Nothing else changes. Versions roll at .9, so 3.9 goes to 4.0.

    python "tools/docs/edit_tm_40.py"
"""
import os
import re
import shutil
import zipfile

B = r"D:\Code Projects\Silhouette Tools\Documents"
SRC = os.path.join(B, "Tech Manual (Ver 3.9).docx")
DST = os.path.join(B, "Tech Manual (Ver 4.0).docx")

zin = zipfile.ZipFile(SRC)
doc = zin.read("word/document.xml").decode("utf-8")

before = doc
doc = doc.replace("fitView() centres on it", "fitView() centers on it")
doc = doc.replace("the centring term in draw()", "the centering term in draw()")
assert doc != before, "neither spelling was found"

text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", doc))
for bad in ("centres", "centring", "colour", "behaviour", "recognise"):
    assert bad not in text, "British spelling still present: %r" % bad
assert "fitView() centers on it" in text and "the centering term in draw()" in text

names = zin.namelist()
with zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for x in ["[Content_Types].xml"] + [y for y in names if y != "[Content_Types].xml"]:
        zout.writestr(zin.getinfo(x),
                      doc.encode("utf-8") if x == "word/document.xml" else zin.read(x))
zin.close()
print("wrote", DST, os.path.getsize(DST), "bytes")

shutil.move(SRC, os.path.join(B, ".Archive", "Tech Manual (Ver 3.9).docx"))
print("archived Tech Manual (Ver 3.9).docx")
