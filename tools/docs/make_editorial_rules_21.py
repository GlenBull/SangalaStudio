# -*- coding: utf-8 -*-
"""Editorial Rules Ver 2.0 -> Ver 2.1, edited IN PLACE so Glen's formatting survives.

The Chapter 2 review found 63 violations. Two findings drove this revision:

  * The only two rules carrying an explicit "It does not reach..." clause - 1 and 2 - produced
    5 and 1 violations. The two with no boundary at all - 11 and 17 - produced 10 and 15, two
    fifths of the total. So every rule is given its edge, and where a rule has no exception it
    says so, which is itself a boundary.
  * Fourteen violations were changes made against rules that do not exist. The document never
    said the list was closed, so it now does.

Three rules are added, all of them faults the chapter actually exhibited. The question of whether
the book addresses the reader as "you" is NOT added as a rule - it is raised for decision, which is
what the closure statement requires of anything outside the list.

    python "tools/docs/make_editorial_rules_21.py"
"""
import os, re, sys, zipfile

SRC = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\Chapters\Notes\Editorial Rules (Ver 2.0).docx"
OUT = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\Chapters\Notes\Editorial Rules (Ver 2.1).docx"

# ---------------------------------------------------------------- the paragraph templates
HEAD = ('<w:p><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="240" w:after="60"/>'
        '<w:ind w:left="293"/></w:pPr><w:r><w:rPr><w:b/><w:color w:val="000000"/></w:rPr>'
        '<w:t xml:space="preserve">{}</w:t></w:r></w:p>')
GROUP = ('<w:p><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="280" w:after="80"/>'
         '</w:pPr><w:r><w:rPr><w:b/><w:color w:val="000000"/></w:rPr>'
         '<w:t xml:space="preserve">{}</w:t></w:r></w:p>')
LINE = ('<w:p><w:pPr><w:spacing w:after="60"/><w:ind w:left="293"/></w:pPr>'
        '<w:r><w:rPr><w:i/><w:color w:val="000000"/></w:rPr><w:t xml:space="preserve">{} </w:t></w:r>'
        '<w:r><w:rPr><w:color w:val="000000"/></w:rPr><w:t xml:space="preserve">{}</w:t></w:r></w:p>')
PLAIN = ('<w:p><w:pPr><w:spacing w:after="60"/></w:pPr>'
         '<w:r><w:rPr><w:color w:val="000000"/></w:rPr><w:t xml:space="preserve">{}</w:t></w:r></w:p>')


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rule(num, title, r, t, e):
    return (HEAD.format(esc("%d. %s" % (num, title))) + LINE.format("Rule.", esc(r))
            + LINE.format("Test.", esc(t)) + LINE.format("Example.", esc(e)))


# ------------------------------------------------- the edge each existing rule was missing
# anchored on a fragment of the rule's own wording, which is unique in the document
EDGES = [
 ("Do not write \"not X but Y\" unless a reader would plausibly have believed X",
  " It does not reach a plain negation that states a fact about the thing itself, such as the "
  "animal is not drawn on the wall; it stands out of it. That is a description, not a frame."),
 ("The conclusion must not restate the premise.",
  " It does not reach a definition, whose work is to restate a term in other words, nor a sentence "
  "that gives the reason a thing is so."),
 ("No absolutes or superlatives unless they survive attack",
  " It does not reach an absolute that holds by construction - a dimension fixed by the "
  "material, or a limit imposed by the software - which is exact rather than overstated."),
 ("Check checkable claims before asserting them.",
  " It does not reach a claim the reader can confirm from the figure or screen beside it."),
 ("Every number must be consistent with the dimensions and units",
  " It does not reach a number the text has already marked as an approximation."),
 ("Use the unit the document established for each axis",
  " It does not reach a passage that converts deliberately in order to teach the relation between "
  "two units."),
 ("Do not use a number that hedges when an exact number is provided.",
  " It does not reach a quantity that genuinely varies with the design, such as how many layers a "
  "collage should have."),
 ("Define a specialist term at first use.",
  " It does not reach a term defined in an earlier chapter of the same book. For this book the "
  "specialist terms include mat, canvas, path, node, vector, silhouette, registration mark, layer "
  "and stud."),
 ("Match the reader. For a novice audience, avoid critical, trade, and academic vocabulary",
  " It does not reach a technical term the book exists to teach, which is Rule 10\'s business, "
  "nor admiring or evaluative prose, which is Rule 19\'s."),
 ("Three-item lists only where all three items carry distinct content.",
  " It does not reach three items the reader must separately do, have, or choose between."),
 ("Objects do not want, ask, refuse, or survive.",
  " It does not reach an established technical usage with no literal equivalent, such as a path "
  "closing or a blade following an outline."),
 ("Do not use fixed expressions whose meaning cannot be worked out from the words.",
  " It does not reach a term of art the text has defined."),
 ("Do not enumerate the same sequence twice in different words.",
  " It does not reach a list of materials followed by the steps that use them, which are two "
  "different lists."),
 ("One claim per sentence.",
  " It does not reach a sentence whose clauses are one sequence of actions performed in order."),
 ("Name the agent when a particular party acts.",
  " In this book the agent is almost always one of three: the reader, Sangala Studio, or the die "
  "cutter. Name whichever it is. It does not reach a passive that describes a state rather than an "
  "act, where no party is doing anything."),
 ("A heading names what the section contains.",
  " It does not reach a heading that names a process or an object in ordinary words, however "
  "vivid those words are on their own."),
]

# ------------------------------------------------------------------ what the chapter exposed
NEW = [
 (19, "Appraisal",
  "Do not tell the reader that something is satisfying, striking, elegant, interesting, or "
  "beautiful. Describe what it is and what it does, and leave the judgment to the reader. This "
  "rule has no exception: the appraisal is never the content.",
  "Ask whether the sentence would still stand if the reader disagreed with it. If the sentence is "
  "the writer\'s opinion of the work, cut it. If it states what the work does, keep it.",
  "A single silhouette, precisely cut, is a satisfying object by itself was cut. So were flat "
  "shapes, stacked with care, become a world and one of the most satisfying moments in the making "
  "process. Most of the 63 violations found in Chapter 2 were this fault under other headings."),
 (20, "Interface names",
  "A control is called what the application calls it. Buttons are buttons, menus are menus, and a "
  "section heading names the part of the screen it describes. It does not reach a general "
  "description of a region of the screen, which may be worded freely as long as no control is "
  "misnamed.",
  "Open the application and read the control. Compare it with the word on the page.",
  "The row across the top of Sangala Studio was described as menus; the six items are buttons. A "
  "section headed The Mat described the workspace, of which the mat is one part."),
 (21, "Unattributed quotation",
  "Do not place words in quotation marks unless they were said or written by someone who can be "
  "named. This rule has no exception: an unsourced quotation is an invention whatever its merit.",
  "For every quotation, name the source. If none can be named, it is not a quotation.",
  "Every material has its own character, and the designer who works with materials learns from "
  "them appeared in quotation marks with no source, and was removed."),
]

# ------------------------------------------------------------------------------- do the work
s = open("unpacked/word/document.xml", encoding="utf-8").read()

for anchor, edge in EDGES:
    a = esc(anchor)
    if s.count(a) != 1:
        sys.exit("anchor not unique: " + anchor[:50])
    m = re.search(re.escape(a) + r"(.*?)</w:t>", s, re.S)
    s = s[:m.end(1)] + esc(edge) + s[m.end(1):]

# the closure statement, straight after the standing-rules line
lead = esc("These are standing rules for drafts and revisions.")
i = s.find(lead)
if i < 0:
    sys.exit("lead sentence not found")
j = s.find("</w:p>", i) + len("</w:p>")
s = s[:j] + PLAIN.format(esc(
    "The list is exhaustive. Anything not stated here is not a rule, and no change may be made to a "
    "draft on the authority of one. Where something outside the list seems worth changing, raise it "
    "as a proposal and leave the text alone until it is agreed.")) + PLAIN.format(esc(
    "Rule numbers are permanent. A new rule takes the next unused number and keeps it, so that a "
    "count of violations made against one version can still be read against the next.")) + s[j:]

# the new rules, and the question that is not one, at the end of the body
tail = "</w:body>"
k = s.rfind("<w:sectPr")
if k < 0:
    k = s.rfind(tail)
block = GROUP.format(esc("E. Voice and accuracy"))
for num, title, r, t, e in NEW:
    block += rule(num, title, r, t, e)
block += GROUP.format(esc("Not yet rules"))
block += PLAIN.format(esc(
    "Whether the book addresses the reader as you is unsettled, and it governs more sentences than "
    "any rule here. The Chapter 2 revision uses the second person - a photo you opened only to "
    "trace over - while the version before it avoided the reader entirely. Until it is decided, "
    "neither form is a violation. It is recorded here rather than written into Rule 17 because the "
    "closure statement above forbids acting on a rule that has not been agreed."))
s = s[:k] + block + s[k:]

open("unpacked/word/document.xml", "w", encoding="utf-8", newline="").write(s)

src = zipfile.ZipFile("work.docx")
out = zipfile.ZipFile("built.docx", "w", zipfile.ZIP_DEFLATED)
names = src.namelist()
first = "[Content_Types].xml"
for n in [first] + [x for x in names if x != first]:
    p = os.path.join("unpacked", n.replace("/", os.sep))
    out.writestr(src.getinfo(n), open(p, "rb").read() if os.path.exists(p) else src.read(n))
out.close(); src.close()
print("built.docx written")
