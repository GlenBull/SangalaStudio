"""The hanging indent needs a tab to be a hanging indent. Ver 3.1 -> Ver 3.2.

Ver 3.1 set left=1584 hanging=1584, which indents every WRAPPED line to 1.1 inch but leaves the FIRST
line starting wherever the marker happens to end - about 0.55 inch for "0:00 - " and about an inch for
"2:30 - Gerald. ". So the body text formed no column at all: its first line sat left of its own
continuation. Rendering the page is what showed it; the XML looked correct.

The fix is a tab after the marker. The hanging indent creates a stop at 1.1 inch, the tab jumps to it,
and every line of the spoken text - first and wrapped alike - begins in the same column.

Only a tab run is inserted, and only on paragraphs beginning with a time mark. No text changes.
"""
import os
import re
import shutil
import sys
import zipfile

DRAFTS = (r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts")
SRC = os.path.join(DRAFTS, "Networked Weather Station (Ver 3.1).docx")
OUT = os.path.join(DRAFTS, "Networked Weather Station (Ver 3.2).docx")

MARK = re.compile(r"^\d:\d\d \u2014 ")
TAB = "<w:r><w:tab/></w:r>"


def main():
    if os.path.exists(OUT):
        sys.exit("refusing to overwrite " + OUT)
    z = zipfile.ZipFile(SRC)
    names = z.namelist()
    blobs = dict((n, z.read(n)) for n in names)
    z.close()

    xml = blobs["word/document.xml"].decode("utf-8")
    paras = re.findall(r"<w:p[ >].*?</w:p>|<w:p/>", xml, re.S)

    done = 0
    for p in paras:
        text = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, re.S))
        if not MARK.match(text):
            continue
        if "<w:tab/>" in p:
            sys.exit("already tabbed: " + text[:40])
        end = p.find("</w:r>")                       # end of the marker run
        if end < 0:
            sys.exit("no run found in: " + text[:40])
        cut = end + len("</w:r>")
        new = p[:cut] + TAB + p[cut:]
        if xml.count(p) != 1:
            sys.exit("paragraph is not unique: " + text[:40])
        xml = xml.replace(p, new, 1)
        done += 1

    print("tabbed %d paragraphs" % done)
    if done != 14:
        print("NOTE: expected 14")
    blobs["word/document.xml"] = xml.encode("utf-8")

    shutil.copy2(SRC, OUT)
    out = zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED)
    out.writestr("[Content_Types].xml", blobs["[Content_Types].xml"])
    for n in names:
        if n != "[Content_Types].xml":
            out.writestr(n, blobs[n])
    out.close()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
