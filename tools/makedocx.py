"""Build a Word .docx on THIS machine, where the usual toolchains do not exist.

There is no Node (so no docx-js), no python-docx, no `zip` command and no LibreOffice.
What there is: Python 3.12 and its `zipfile`. This module wraps the hand-built OOXML
package so a new document is a dozen lines, not a rediscovery.

    from makedocx import Doc
    d = Doc()                       # page numbers ON; pass Doc(page_numbers=False) for a one-pager
    d.title("A Title")
    d.heading("A section")
    d.body("An ordinary paragraph.")
    d.item("A Label. ", "A list-like paragraph led by an italic label.")
    d.step("The first numbered step.")
    print(d.save(r"C:\\...\\_Drafts", "TurtleStitch Projects for Sangala Studio"))

House formatting is applied by construction: Letter page with 1 in margins, Times New
Roman 11 pt black body, headings carrying keepNext AND keepLines so they cannot orphan,
5 pt after a body paragraph and 3 pt after a list item, and NO autospacing anywhere.

A PAGE NUMBER sits at the bottom center, because any document longer than one page must
carry one (Glen, 2026-08-05). It is ON by default, since nearly every document runs past
a page and the failure mode is forgetting it. A document that really is one page should
be built with Doc(page_numbers=False); docxcheck reports the page count, so build first
and turn it off only if the count comes back 1.

Heading text is written in Mixed Case - capitalize each word except the minor ones (a, an,
the, and, or, to, in, of, for, with). That is the caller's job; this module cannot know
which words are proper nouns.

`save()` computes the next unused version number in the folder AT WRITE TIME and opens
the file with mode "x", so it cannot overwrite anything - not one of Glen's documents,
and not a version number he has already claimed. It raises rather than clobber.
"""
import os, re, zipfile, xml.dom.minidom

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
OFF = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT = "application/vnd.openxmlformats-officedocument."


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _run(text, italic=False, bold=False, sz=22):
    rpr = '<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>'
    if bold:
        rpr += "<w:b/>"
    if italic:
        rpr += "<w:i/>"
    rpr += '<w:color w:val="000000"/><w:sz w:val="%d"/><w:szCs w:val="%d"/></w:rPr>' % (sz, sz)
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, esc(text))


def _runs(parts, sz=22):
    """parts is a string, or a list of (text, italic, bold) tuples."""
    if isinstance(parts, str):
        parts = [(parts, False, False)]
    return "".join(_run(t, italic=i, bold=b, sz=sz) for (t, i, b) in parts)


class Doc:
    def __init__(self, page_numbers=True):
        self.paras = []
        self.numbered = False
        self.page_numbers = page_numbers

    def _p(self, parts, before=0, after=100, keep=False, jc=None, sz=22, num=False):
        ppr = "<w:pPr>"
        if keep:
            ppr += "<w:keepNext/><w:keepLines/>"
        if num:
            ppr += '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'
            ppr += '<w:ind w:left="720" w:hanging="360"/>'
        ppr += '<w:spacing w:before="%d" w:after="%d"/>' % (before, after)
        if jc:
            ppr += '<w:jc w:val="%s"/>' % jc
        ppr += "</w:pPr>"
        self.paras.append("<w:p>%s%s</w:p>" % (ppr, _runs(parts, sz=sz)))

    # --- the four shapes a Sangala document actually uses -------------------
    def title(self, text):
        self._p([(text, False, True)], after=240, jc="center", sz=28)

    def heading(self, text):
        """Headings carry keepNext + keepLines, and sit tight to what follows (0 before / 3 pt after)."""
        self._p([(text, False, True)], before=240, after=60, keep=True)

    def body(self, parts, before_list=False):
        """An ordinary body paragraph keeps 5 pt after; one introducing a list takes 3 pt."""
        self._p(parts, after=60 if before_list else 100)

    def item(self, label, text):
        """A list-like paragraph led by an ITALIC label, 3 pt after."""
        self._p([(label, True, False), (text, False, False)], after=60)

    def step(self, parts):
        """A numbered step, 3 pt after."""
        self.numbered = True
        self._p(parts, after=60, num=True)

    def page_break(self):
        self.paras.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    # --- packaging ---------------------------------------------------------
    def _parts(self):
        # A footerReference must come FIRST inside sectPr - CT_SectPr fixes that order, and Word
        # rejects the package if the page size precedes it.
        ftr_ref = '<w:footerReference w:type="default" r:id="rId9"/>' if self.page_numbers else ""
        document = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:document xmlns:w="%s" xmlns:r="%s"><w:body>%s'
            '<w:sectPr>%s<w:pgSz w:w="12240" w:h="15840"/>'
            '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"'
            ' w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>'
            "</w:body></w:document>" % (W, OFF, "".join(self.paras), ftr_ref)
        )
        # The page number is a PAGE field, not literal text, so it counts itself on every page.
        # The <w:t>1</w:t> between separate and end is the cached result Word shows before it
        # repaginates; Word replaces it on open.
        footer = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:ftr xmlns:w="%s"><w:p><w:pPr><w:jc w:val="center"/>'
            '<w:spacing w:before="0" w:after="0"/></w:pPr>'
            '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            '%s'
            '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>'
            % (W, _run("1"))
        )
        styles = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:styles xmlns:w="%s"><w:docDefaults><w:rPrDefault><w:rPr>'
            '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"'
            ' w:eastAsia="Times New Roman" w:cs="Times New Roman"/>'
            '<w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr></w:rPrDefault>'
            '<w:pPrDefault><w:pPr><w:spacing w:before="0" w:after="100"/></w:pPr></w:pPrDefault>'
            "</w:docDefaults>"
            '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
            '<w:name w:val="Normal"/><w:qFormat/></w:style></w:styles>' % W
        )
        numbering = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:numbering xmlns:w="%s">'
            '<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="singleLevel"/>'
            '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/>'
            '<w:lvlText w:val="%%1."/><w:lvlJc w:val="left"/>'
            '<w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl></w:abstractNum>'
            '<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num></w:numbering>' % W
        )
        overrides = (
            '<Override PartName="/word/document.xml" ContentType="%swordprocessingml.document.main+xml"/>'
            '<Override PartName="/word/styles.xml" ContentType="%swordprocessingml.styles+xml"/>'
            % (CT, CT)
        )
        doc_rel = (
            '<Relationship Id="rId1" Type="%s/styles" Target="styles.xml"/>' % OFF
        )
        if self.numbered:
            overrides += ('<Override PartName="/word/numbering.xml" '
                          'ContentType="%swordprocessingml.numbering+xml"/>' % CT)
            doc_rel += '<Relationship Id="rId2" Type="%s/numbering" Target="numbering.xml"/>' % OFF
        if self.page_numbers:
            overrides += ('<Override PartName="/word/footer1.xml" '
                          'ContentType="%swordprocessingml.footer+xml"/>' % CT)
            doc_rel += '<Relationship Id="rId9" Type="%s/footer" Target="footer1.xml"/>' % OFF
        content_types = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>%s</Types>' % overrides
        )
        rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="%s"><Relationship Id="rId1" Type="%s/officeDocument"'
            ' Target="word/document.xml"/></Relationships>' % (PKG, OFF)
        )
        doc_rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="%s">%s</Relationships>' % (PKG, doc_rel)
        )
        parts = {
            "[Content_Types].xml": content_types,
            "_rels/.rels": rels,
            "word/document.xml": document,
            "word/styles.xml": styles,
            "word/_rels/document.xml.rels": doc_rels,
        }
        if self.numbered:
            parts["word/numbering.xml"] = numbering
        if self.page_numbers:
            parts["word/footer1.xml"] = footer
        return parts

    def save(self, folder, stem=None, version=None):
        """Write to <folder>/<stem> (Ver N.M).docx, taking the next unused number.

        Pass a full path as `folder` and leave `stem` None to write that exact file.
        Either way the write uses mode "x" and RAISES if the target exists - it never
        overwrites, so a version number someone else has claimed stays theirs.
        """
        parts = self._parts()
        for name, text in parts.items():         # never ship a package Word cannot open
            xml.dom.minidom.parseString(text)
        if stem is None:
            out = folder
        else:
            out = os.path.join(folder, "%s (Ver %s).docx" % (stem, version or next_version(folder, stem)))
        with zipfile.ZipFile(out, "x", zipfile.ZIP_DEFLATED) as z:
            for name, text in parts.items():
                z.writestr(name, text)
        return out


def next_version(folder, stem):
    """Highest (Ver N.M) present for this stem, plus 0.1 - read at write time, never reserved ahead."""
    hi = (0, 0)
    pat = re.compile(re.escape(stem) + r" \(Ver (\d+)\.(\d+)\)\.docx$", re.I)
    for f in (os.listdir(folder) if os.path.isdir(folder) else []):
        m = pat.match(f)
        if m:
            hi = max(hi, (int(m.group(1)), int(m.group(2))))
    return "1.0" if hi == (0, 0) else "%d.%d" % (hi[0], hi[1] + 1)
