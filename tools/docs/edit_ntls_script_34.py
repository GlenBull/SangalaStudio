"""Follows Glen's own example on the 0:00 line. Ver 3.3 -> Ver 3.4.

Glen: "the dash is completely unnecessary. use my example and format the others to follow."

VER 3.3 IS HIS. He reformatted the first line and left the other thirteen for me to match. His example,
read from the file rather than guessed:

    <w:ind w:left="630" w:hanging="630"/>     0.44 inch, not the 1.1 inch I had set
    italic run, text "0:00  "                 the em dash gone, two spaces in its place
    <w:r><w:tab/></w:r>                       the tab stays

So each remaining marker loses " - " and each paragraph takes his indent.

THE THREE LABELLED LINES NEED ONE MORE STEP. "2:30 - Gerald. " is about an inch wide, and left in the
marker it would overrun a 0.44 inch column and push its own first line out - the fault he objected to
in the first place. So the marker becomes the bare time, and "Gerald. ", "Roger. ", "nobody. " move to
the head of the body as their own italic runs. The left column is then the time and nothing else, on
every line, which is what his example sets.
"""
import os
import re
import shutil
import sys
import zipfile

DRAFTS = (r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts")
SRC = os.path.join(DRAFTS, "Networked Weather Station (Ver 3.3).docx")
OUT = os.path.join(DRAFTS, "Networked Weather Station (Ver 3.4).docx")

HIS_IND = '<w:ind w:left="630" w:hanging="630"/>'
OLD_IND = '<w:ind w:left="1584" w:hanging="1584"/>'
ITALIC = '<w:r><w:rPr><w:i/><w:color w:val="000000"/></w:rPr><w:t xml:space="preserve">%s</w:t></w:r>'
TABRUN = "<w:r><w:tab/></w:r>"
MARK = re.compile(r"^\d:\d\d")


def main():
    if os.path.exists(OUT):
        sys.exit("refusing to overwrite " + OUT)
    z = zipfile.ZipFile(SRC)
    names = z.namelist()
    blobs = dict((n, z.read(n)) for n in names)
    z.close()
    xml = blobs["word/document.xml"].decode("utf-8")

    changed = 0
    for p in re.findall(r"<w:p[ >].*?</w:p>|<w:p/>", xml, re.S):
        text = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, re.S))
        if not MARK.match(text) or OLD_IND not in p:
            continue
        new = p.replace(OLD_IND, HIS_IND, 1)

        m = re.search(r'<w:t xml:space="preserve">(\d:\d\d) \u2014 ([^<]*)</w:t>', new)
        if not m:
            sys.exit("unexpected marker in: " + text[:40])
        time, label = m.group(1), m.group(2).strip()
        new = new.replace(m.group(0), '<w:t xml:space="preserve">%s  </w:t>' % time, 1)

        if label:                                  # Gerald. / Roger. / nobody.
            at = new.find(TABRUN) + len(TABRUN)
            new = new[:at] + (ITALIC % (label + " ")) + new[at:]

        if xml.count(p) != 1:
            sys.exit("paragraph is not unique: " + text[:40])
        xml = xml.replace(p, new, 1)
        changed += 1
        print("%-7s %s" % (time, ("label moved: " + label) if label else "dash removed"))

    print("changed %d paragraphs" % changed)
    if changed != 13:
        print("NOTE: expected 13 (his 0:00 line is already done)")
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
