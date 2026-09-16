"""Hanging indents on the timed script. Ver 3.0 -> Ver 3.1.

Glen: "You need hanging indents for the points beside each time marker."

Without one, a line that wraps returns to the left margin and runs under the time, so the marks stop
being a column and the page stops being scannable. With one, every mark sits alone in the left column
and all of the spoken text lines up in a second.

The hang is 1584 twips (1.1 inch), set from the LONGEST marker rather than the shortest: "2:30 -
Gerald. " and "6:30 - nobody. " are about an inch at Times New Roman 11 pt, and a hang narrower than
the widest marker pushes that marker's first line out of the column it is meant to define.

Edited in place on the saved file - only the paragraph indentation changes, and only on the paragraphs
that begin with a time mark. No text is touched.
"""
import os
import re
import shutil
import sys
import zipfile

DRAFTS = (r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts")
SRC = os.path.join(DRAFTS, "Networked Weather Station (Ver 3.0).docx")
OUT = os.path.join(DRAFTS, "Networked Weather Station (Ver 3.1).docx")

IND = '<w:ind w:left="1584" w:hanging="1584"/>'
MARK = re.compile(r"^\d:\d\d \u2014 ")


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
        if "<w:ind " in p:
            sys.exit("paragraph already carries an indent: " + text[:40])
        m = re.search(r"<w:pPr>(.*?)</w:pPr>", p, re.S)
        if not m:
            sys.exit("no pPr on: " + text[:40])
        # w:ind follows w:spacing in CT_PPr's fixed order, so append it inside pPr
        new = p.replace(m.group(0), "<w:pPr>" + m.group(1) + IND + "</w:pPr>", 1)
        if xml.count(p) != 1:
            sys.exit("paragraph is not unique: " + text[:40])
        xml = xml.replace(p, new, 1)
        done += 1
        print("%-22s %s" % (text[:20], "indented"))

    if done != 14:
        print("NOTE: indented %d paragraphs, expected 14" % done)
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
