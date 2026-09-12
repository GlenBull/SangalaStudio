# -*- coding: utf-8 -*-
"""Tech Manual Ver 3.8 -> Ver 3.9: compound paths, and the workspace that follows the design.

Two paragraphs added to Section 6, "The browser UI", for the three changes shipped in Studio
2026-09-12.210:

  * "Compound paths." after the Line classification list, because that is where a path becomes
    objects, and this is the step that used to invent geometry.
  * "The workspace and the view." after "The workspace.", because it qualifies exactly what that
    paragraph describes.

Both are built to match the paragraph beside them rather than composed: pStyle NormalWeb, spacing
100 before and after with autospacing explicitly OFF, a Strong lead-in run, then the body. Nothing
else in the document is touched.

    python "tools/docs/edit_tm_39.py"
"""
import os
import re
import shutil
import zipfile

B = r"D:\Code Projects\Silhouette Tools\Documents"
SRC = os.path.join(B, "Tech Manual (Ver 3.8).docx")
DST = os.path.join(B, "Tech Manual (Ver 3.9).docx")

PPR = ('<w:pPr><w:pStyle w:val="NormalWeb" /><w:spacing w:before="100" w:beforeAutospacing="0" '
       'w:after="100" w:afterAutospacing="0" /><w:rPr><w:szCs w:val="22" /></w:rPr></w:pPr>')
LEAD = ('<w:r><w:rPr><w:rStyle w:val="Strong" /><w:szCs w:val="22" /></w:rPr>'
        '<w:t xml:space="preserve">%s</w:t></w:r>')
BODY = '<w:r><w:rPr><w:szCs w:val="22" /></w:rPr><w:t xml:space="preserve">%s</w:t></w:r>'

def para(lead, body):
    return "<w:p>" + PPR + (LEAD % lead) + (BODY % body) + "</w:p>"

COMPOUND = para(
    "Compound paths.",
    " Silhouette writes a shape and its interior detail as one &lt;path&gt; holding several "
    "subpaths, and each subpath is a ring of its own. sampleRings() walks the element by arc "
    "length, so two consecutive samples can never be further apart than one step except across a "
    "subpath break, where getPointAtLength jumps to the next subpath's start. That makes the break "
    "exact to detect and needs no parsing of the d attribute. nestRings() then sorts the rings by "
    "even-odd containment, the same rule the SVG fill uses, into an outer ring carrying the rings "
    "it encloses as holes - which is what cutPolys() already cuts and what draw() already shows. "
    "Disjoint rings in one path become separate objects. Until 2026-09-12.210 the element was "
    "walked into a single polyline, which joined every subpath end to start and drew a straight "
    "line across each gap: lines present in no file, which the classifier then cut.")

WORKSPACE = para(
    "The workspace and the view.",
    " The workspace is the page, or the design, whichever is larger. contentBox() unions the page "
    "with every object in the file; fitZoom() measures that box, clampPan() bounds the view by it, "
    "and fitView() centres on it. This matters because a Silhouette file may park pieces well "
    "outside the page and a print file keeps those coordinates, normalize() being run only on "
    "designs that are not print files. Two further details of the view are easy to get wrong. "
    "fitZoom() measures the canvas through its bounding rectangle rather than cv.width and "
    "cv.height, which hold the element's declared attributes until the first draw() has run. And "
    "setZoom() solves for the design point under the cursor and puts it back there at the new "
    "scale, because the centring term in draw() is (cv.width - vw * k) / 2 and therefore moves "
    "with the zoom; anchoring on the pan alone left the fixed point out near a corner.")

zin = zipfile.ZipFile(SRC)
doc = zin.read("word/document.xml").decode("utf-8")

def after(probe, block):
    """Insert block immediately after the paragraph whose text contains probe."""
    global doc
    hits = [m for m in re.finditer(r"<w:p\b[^>]*>.*?</w:p>", doc, re.S)
            if probe in "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", m.group(0)))]
    assert len(hits) == 1, "%r identifies %d paragraphs, not 1" % (probe[:40], len(hits))
    m = hits[0]
    doc = doc[:m.end()] + block + doc[m.end():]

after("a fold must be explicitly dashed", COMPOUND)
after("a design meant for brick or for extrusion belongs on the baseplate", WORKSPACE)

text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", doc))
assert "Compound paths." in text and "The workspace and the view." in text
assert "w:beforeAutospacing=\"1\"" not in COMPOUND + WORKSPACE

names = zin.namelist()
with zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for x in ["[Content_Types].xml"] + [y for y in names if y != "[Content_Types].xml"]:
        zout.writestr(zin.getinfo(x),
                      doc.encode("utf-8") if x == "word/document.xml" else zin.read(x))
zin.close()
print("wrote", DST, os.path.getsize(DST), "bytes")

arch = os.path.join(B, ".Archive")
shutil.move(SRC, os.path.join(arch, "Tech Manual (Ver 3.8).docx"))
print("archived Tech Manual (Ver 3.8).docx")
