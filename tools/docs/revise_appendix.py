"""Two corrections to Glen's Ver 1.1 of the Installation appendix, edited IN PLACE into Ver 1.2.

His file, not mine: it is copied and edited, never regenerated from the script that produced 1.0 -
that script does not know about his revisions and would silently drop them.

"Document Object Identifier" sits inside one run and is a plain string replacement. "they and are
not" does not: Word split it across runs while he was typing, so it is repaired run-aware, the same
way trackedit locates text that straddles a run boundary.
"""
import os
import re
import zipfile

D = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts"
SRC = os.path.join(D, "Appendix - Installation (Ver 1.1).docx")
OUT = os.path.join(D, "Appendix - Installation (Ver 1.2).docx")
assert not os.path.exists(OUT), "1.2 already exists"

RUN = re.compile(r"<w:r(?:\s[^>]*)?>(?:(?!</w:r>).)*?</w:r>", re.S)
TXT = re.compile(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", re.S)

with zipfile.ZipFile(SRC) as z:
    xml = z.read("word/document.xml").decode("utf-8")

# 1. the DOI expansion - one run, one replacement
before = xml.count("Document Object Identifier")
xml = xml.replace("Document Object Identifier", "Digital Object Identifier", 1)
print("DOI expansion corrected:", before == 1)

# 2. "they and are not" -> "they are not", across runs: rebuild the runs it spans
target, replacement = "they and are not", "they are not"
runs = list(RUN.finditer(xml))
pos, spans = 0, []
text = ""
for r in runs:
    text += "".join(TXT.findall(r.group(0)))
start = text.index(target)
end = start + len(target)
pos = 0
out, done = [], False
for r in runs:
    rt = "".join(TXT.findall(r.group(0)))
    a, b = pos, pos + len(rt)
    pos = b
    lo, hi = max(a, start), min(b, end)
    if lo >= hi:
        continue
    inside = rt[lo - a:hi - a]
    keep = rt[:lo - a] + (replacement if not done else "") + rt[hi - a:]
    done = True
    new_run = re.sub(r"(<w:t(?:\s[^>]*)?>).*?(</w:t>)",
                     lambda m: m.group(1) + keep + m.group(2), r.group(0), count=1, flags=re.S)
    # a run left with nothing to say is dropped rather than left as an empty <w:t>
    if keep == "":
        new_run = ""
    spans.append((r.start(), r.end(), new_run))
    print("   run touched: %r -> %r" % (inside, keep))

new_xml, last = "", 0
for a, b, rep in spans:
    new_xml += xml[last:a] + rep
    last = b
new_xml += xml[last:]

with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
    names = zin.namelist()
    for n in [x for x in names if x == "[Content_Types].xml"] + [x for x in names if x != "[Content_Types].xml"]:
        data = new_xml.encode("utf-8") if n == "word/document.xml" else zin.read(n)
        zout.writestr(zin.getinfo(n), data)
print("wrote", OUT)
