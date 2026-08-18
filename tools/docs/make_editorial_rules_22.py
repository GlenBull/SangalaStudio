# -*- coding: utf-8 -*-
"""Editorial Rules Ver 2.1 -> Ver 2.2, edited IN PLACE. Adds Rule 22, Numerals.

Glen settled the convention while Chapter 3 was being finished: numbers ten and under are spelled,
Arabic numerals above ten. It goes into Group B, Numbers, where its subject belongs. The number 22
is the next unused one and it keeps it, as the document's own numbering statement requires - a rule
in Group B numbered above the rules in Group E is expected, not an error.

The boundary is the one the chapter taught: "Frame 1 - Sky" is a file name the reader types, not a
count, and spelling it would break the instruction.

Run from a directory holding a freshly unpacked copy in `unpacked/` and `work.docx` beside it.
"""
import os, re, sys, zipfile
import xml.etree.ElementTree as ET

HEAD = ('<w:p><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="240" w:after="60"/>'
        '<w:ind w:left="293"/></w:pPr><w:r><w:rPr><w:b/><w:color w:val="000000"/></w:rPr>'
        '<w:t xml:space="preserve">{}</w:t></w:r></w:p>')
LINE = ('<w:p><w:pPr><w:spacing w:after="60"/><w:ind w:left="293"/></w:pPr>'
        '<w:r><w:rPr><w:i/><w:color w:val="000000"/></w:rPr><w:t xml:space="preserve">{} </w:t></w:r>'
        '<w:r><w:rPr><w:color w:val="000000"/></w:rPr><w:t xml:space="preserve">{}</w:t></w:r></w:p>')


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


RULE = (
    HEAD.format(esc("22. Numerals"))
    + LINE.format("Rule.", esc(
        "Spell a number ten and under; use Arabic numerals above ten. It does not reach a LABEL - a "
        "figure number, a chapter number, a file name, a course number, a version - which names "
        "something rather than counting it."))
    + LINE.format("Test.", esc(
        "Ask whether the number counts or measures. If it does, the rule applies. If it names "
        "something the reader will look for or type, leave it exactly as it appears."))
    + LINE.format("Example.", esc(
        "Then set its width and height to 4 inches became four inches, matching a four-inch square "
        "in the same paragraph. Frame 1 - Sky and Frame 2 - Crane were left alone, being file names "
        "the reader types."))
)

s = open("unpacked/word/document.xml", encoding="utf-8").read()

anchor = esc("C. Words")
i = s.find(anchor)
if i < 0:
    sys.exit("could not find the C. Words heading")
start = s.rfind("<w:p", 0, i)          # insert before that heading's paragraph
if "22. Numerals" in s:
    sys.exit("Rule 22 is already in this document")
s = s[:start] + RULE + s[start:]

open("unpacked/word/document.xml", "w", encoding="utf-8", newline="").write(s)
ET.fromstring(s)

src = zipfile.ZipFile("work.docx")
out = zipfile.ZipFile("built.docx", "w", zipfile.ZIP_DEFLATED)
names = src.namelist()
first = "[Content_Types].xml"
for n in [first] + [x for x in names if x != first]:
    p = os.path.join("unpacked", n.replace("/", os.sep))
    out.writestr(src.getinfo(n), open(p, "rb").read() if os.path.exists(p) else src.read(n))
out.close(); src.close()
print("Rule 22 added at the end of Group B; built.docx written")
