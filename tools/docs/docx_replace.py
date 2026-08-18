# -*- coding: utf-8 -*-
"""Replace phrases inside a .docx, one PARAGRAPH at a time and each paragraph rewritten ONCE.

Every edit is first assigned to the paragraph that contains it. A paragraph carrying more than one
edit takes them all in a single rewrite - rebuilding it twice from the same offsets is what ran past
its end into the table that followed.

Where a paragraph's runs share one format, it is rebuilt as a single run. Where they differ, only
the <w:t> holding the phrase is touched, and if a phrase straddles runs there the script stops
rather than decide which formatting wins.
"""
import re, sys
from collections import OrderedDict

PATH = "unpacked/word/document.xml"
RUN = r"<w:r(?:\s[^>]*)?>.*?</w:r>"
TXT = r"<w:t(?:\s[^>]*)?>(.*?)</w:t>"
DASH, APOS = "—", "’"

EDITS = [
    ("This chapter takes that composition into actual three-dimensional space. A shadowbox is a "
     "framed construction in which cut paper panels are held at measurably different depths",
     "A shadowbox is a framed construction in which cut paper panels are placed at different depths"),
    ("They introduce a new option in the Combine tool, the Union option, to merge the silhouette of "
     "the crane with the frame of the shadowbox. ",
     ""),
    ("With the frame template saved, the next step is to merge each layer" + APOS + "s silhouette "
     "into the circular window of its frame.",
     "Each layer" + APOS + "s silhouette is merged into the circular window of its frame."),
    ("These discoveries " + DASH + " and the adjustments they call for " + DASH + " are not problems "
     "with the process. They are the process.",
     "These discoveries are the process."),
    ("The scene acquires a quality that no screen representation can fully anticipate.",
     "The panels cast shadows on one another, an effect that is not modeled in the CAD program."),
    ("A designer who iterates between the digital and the physical, adjusting and recutting, learns "
     "more than one who accepts the first result.",
     "Designers refine a design through iteration moving between digital models and physical "
     "prototypes."),
]

s = open(PATH, encoding="utf-8").read()
paras = [(m.start(), m.end(), m.group(0))
         for m in re.finditer(r"<w:p(?:\s[^>]*)?>.*?</w:p>", s, re.S)]

# assign each edit to its paragraph
byPara = OrderedDict()
for old, new in EDITS:
    hits = [p for p in paras if old in "".join(re.findall(TXT, p[2], re.S))]
    if len(hits) != 1:
        sys.exit("expected one paragraph, found %d: %s" % (len(hits), old[:50]))
    byPara.setdefault(hits[0][:2], []).append((old, new, hits[0][2]))

out = []
for (a, b), items in byPara.items():
    xml = items[0][2]
    runs = re.findall(RUN, xml, re.S)
    props = set(re.search(r"<w:rPr>.*?</w:rPr>", r, re.S).group(0) if "<w:rPr>" in r else ""
                for r in runs)
    if len(props) == 1:
        text = "".join(re.findall(TXT, xml, re.S))
        for old, new, _ in items:
            text = text.replace(old, new)
        rpr = props.pop()
        ppr = re.search(r"<w:pPr>.*?</w:pPr>", xml, re.S)
        head = re.match(r"<w:p(?:\s[^>]*)?>", xml).group(0)
        out.append((a, b, head + (ppr.group(0) if ppr else "")
                    + "<w:r>" + rpr + '<w:t xml:space="preserve">' + text + "</w:t></w:r></w:p>"))
        print("rebuilt one paragraph carrying %d edit(s)" % len(items))
    else:
        for old, new, _ in items:
            spans = [m for m in re.finditer(TXT, xml, re.S) if old in m.group(1)]
            if len(spans) != 1:
                sys.exit("phrase straddles runs in a mixed-format paragraph: " + old[:50])
            m = spans[0]
            out.append((a + m.start(1), a + m.end(1), m.group(1).replace(old, new)))
            print("edited one run in a mixed-format paragraph")

spans = sorted(out, key=lambda e: e[0])
for i in range(1, len(spans)):
    if spans[i][0] < spans[i - 1][1]:
        sys.exit("two edits overlap; stopping")
for a, b, rep in sorted(out, key=lambda e: -e[0]):
    s = s[:a] + rep + s[b:]

open(PATH, "w", encoding="utf-8", newline="").write(s)
import xml.etree.ElementTree as ET
ET.fromstring(s)          # refuse to leave malformed XML behind
print("written, and it parses")
