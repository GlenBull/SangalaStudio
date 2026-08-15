"""Dump a .docx's paragraphs with an index, so a rule pass can enumerate sites before judging them."""
import re
import sys
import zipfile

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
from xml.etree import ElementTree as ET


def paras(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    body = root.find(W + "body")
    out = []
    for i, p in enumerate(body.iter(W + "p")):
        style = ""
        pPr = p.find(W + "pPr")
        if pPr is not None:
            ps = pPr.find(W + "pStyle")
            if ps is not None:
                style = ps.get(W + "val")
        # Text of the paragraph as a reader sees it: skip deleted runs, keep inserted ones.
        parts = []
        for r in p.iter(W + "r"):
            for t in r.findall(W + "t"):
                parts.append(t.text or "")
        text = "".join(parts)
        out.append((i, style, text))
    return out


if __name__ == "__main__":
    path = sys.argv[1]
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 9
    for i, style, text in paras(path):
        if not (lo <= i <= hi):
            continue
        if not text.strip():
            continue
        print("[%03d] %-12s %s" % (i, style[:12], text))
