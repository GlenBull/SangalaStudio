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
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
DML = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"

EMU_PER_IN = 914400
TEXT_WIDTH_IN = 6.5          # Letter less the 1 in margins this module sets


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


def _pixel_size(path):
    """Width and height of a PNG or JPEG, read from the file's own header.

    Deliberately dependency-free: this module's whole reason to exist is that the usual
    toolchains are absent here, so it must not acquire a Pillow dependency to place a figure.
    """
    with open(path, "rb") as f:
        head = f.read(32)
        if head[:8] == b"\x89PNG\r\n\x1a\n":                    # IHDR is always the first chunk
            return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
        if head[:2] == b"\xff\xd8":                             # JPEG: walk to the first SOF marker
            f.seek(2)
            while True:
                b = f.read(1)
                if not b:
                    break
                if b != b"\xff":
                    continue
                marker = f.read(1)
                while marker == b"\xff":
                    marker = f.read(1)
                if marker[0] in range(0xC0, 0xCF) and marker[0] not in (0xC4, 0xC8, 0xCC):
                    f.read(3)
                    h = int.from_bytes(f.read(2), "big")
                    w = int.from_bytes(f.read(2), "big")
                    return w, h
                size = int.from_bytes(f.read(2), "big")
                f.seek(size - 2, 1)
    raise ValueError("cannot read image dimensions: %s" % path)


class Doc:
    def __init__(self, page_numbers=True):
        self.paras = []
        self.numbered = False
        self.page_numbers = page_numbers
        self.images = []                 # (zip name, bytes, extension)
        self.numid = 1                   # the list step() is currently adding to; see new_list()

    def _p(self, parts, before=0, after=100, keep=False, jc=None, sz=22, num=False, ind=0,
           brk=False):
        ppr = "<w:pPr>"
        if keep:
            ppr += "<w:keepNext/><w:keepLines/>"
        if brk:
            # pageBreakBefore, not a <w:br> in a paragraph of its own: docxcheck recognises this as
            # a deliberate break and stops counting the short page before it against PAGINATION
            # CLEAN. The schema wants it here, after keepLines and before numPr.
            ppr += "<w:pageBreakBefore/>"
        if num:
            ppr += ('<w:numPr><w:ilvl w:val="0"/><w:numId w:val="%d"/></w:numPr>' % self.numid)
            ppr += '<w:ind w:left="720" w:hanging="360"/>'
        elif ind:
            # Aligns a continuation paragraph under the TEXT of a numbered step, whose text sits at
            # 720. Without this, a sub-paragraph falls back to the margin and the step's own indent
            # makes the two look unrelated - the list stops reading as blocks.
            ppr += '<w:ind w:left="%d"/>' % ind
        ppr += '<w:spacing w:before="%d" w:after="%d"/>' % (before, after)
        if jc:
            ppr += '<w:jc w:val="%s"/>' % jc
        ppr += "</w:pPr>"
        self.paras.append("<w:p>%s%s</w:p>" % (ppr, _runs(parts, sz=sz)))

    # --- the four shapes a Sangala document actually uses -------------------
    def title(self, text):
        self._p([(text, False, True)], after=240, jc="center", sz=28)

    def heading(self, text, page_break_before=False):
        """Headings carry keepNext + keepLines, and sit tight to what follows (0 before / 3 pt after).

        page_break_before=True starts the section on a fresh page - use it for an appendix, in
        preference to page_break(), which docxcheck cannot tell from an accidental short page.
        """
        self._p([(text, False, True)], before=240, after=60, keep=True, brk=page_break_before)

    def body(self, parts, before_list=False):
        """An ordinary body paragraph keeps 5 pt after; one introducing a list takes 3 pt."""
        self._p(parts, after=60 if before_list else 100)

    def item(self, label, text, ind=0, after=60):
        """A list-like paragraph led by an ITALIC label, 3 pt after.

        Pass ind=720 to tuck it under a numbered step so the two read as one block.
        """
        self._p([(label, True, False), (text, False, False)], after=after, ind=ind)

    def step(self, parts, before=0):
        """A numbered step, 3 pt after. `before` separates one step's block from the previous."""
        self.numbered = True
        self._p(parts, before=before, after=60, num=True)

    def new_list(self):
        """Begin a fresh numbered list: the next step() starts again at 1.

        Call this between two separate step sequences. Without it every step() in the document
        shares one counter, so a second sequence of seven continues at 8 - which reads as a fault
        under a heading that announces a new procedure. This was found in a real document only by
        rendering the page, because the XML looks correct either way.

        A NEW numId ALONE DOES NOT RESTART A LIST: it inherits the abstract definition's counter,
        so each one is emitted with an explicit lvlOverride/startOverride (see save()). Verify with
        Word COM Range.ListFormat.ListString, never by reading the XML.
        """
        self.numid += 1

    def table(self, title, headers, rows, weights=None, center_cols=()):
        """A table in the house format, CLONED from the Tech Manual's Table 4 rather than described.

        Every value below was read out of `Tech Manual (Ver 3.6).docx` — table centered on the page,
        Arial 10 pt throughout, 3 pt before and 2 pt after on EVERY cell paragraph (60/40 twips; this
        is paragraph spacing, not cell margins, which are zero), a title row merged across all
        columns in bold, an italic centered heading row, a double rule dividing the headings from the
        body, single rules elsewhere, and the label column indented 171 twips.

        title    "Table 1. What the Table Shows" — number it yourself, sequentially through the doc
        headers  one string per column
        rows     list of lists of strings, one per column
        weights  relative column widths; defaults to equal. Scaled to the same 8272 twips Table 4 uses
        center_cols  indices of body columns to centre rather than left-align (a short column like
                 "Method" reads better centred; the default is left, per the house rule)
        """
        n = len(headers)
        weights = list(weights or [1] * n)
        total = 8272
        w = [int(total * x / float(sum(weights))) for x in weights]
        w[-1] += total - sum(w)                      # rounding lands on the last column

        SGL = '<w:%s w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        DBL = '<w:%s w:val="double" w:sz="4" w:space="0" w:color="000000"/>'
        ZMAR = ('<w:tcMar><w:top w:w="0" w:type="dxa"/><w:left w:w="0" w:type="dxa"/>'
                '<w:bottom w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tcMar>')

        def cell(text, width, top, bottom, bold=False, italic=False, jc=None, ind=0):
            rpr = ('<w:rPr><w:rFonts w:ascii="Arial" w:eastAsia="Times New Roman" w:hAnsi="Arial"'
                   ' w:cs="Arial"/>' + ("<w:b/><w:bCs/>" if bold else "<w:bCs/>")
                   + ("<w:i/>" if italic else "")
                   + '<w:sz w:val="20"/><w:szCs w:val="22"/></w:rPr>')
            ppr = "<w:pPr>"
            if ind:
                ppr += '<w:ind w:left="%d"/>' % ind
            ppr += '<w:spacing w:before="60" w:after="40"/>'
            if jc:
                ppr += '<w:jc w:val="%s"/>' % jc
            ppr += rpr + "</w:pPr>"
            borders = ("<w:tcBorders>" + (top % "top") + (SGL % "left")
                       + (bottom % "bottom") + (SGL % "right") + "</w:tcBorders>")
            return ('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s%s</w:tcPr>'
                    '<w:p>%s<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:p></w:tc>'
                    % (width, borders, ZMAR, ppr, rpr, esc(text)))

        out = ['<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:jc w:val="center"/>'
               '<w:tblBorders><w:top w:val="outset" w:sz="6" w:space="0" w:color="auto"/>'
               '<w:left w:val="outset" w:sz="6" w:space="0" w:color="auto"/>'
               '<w:bottom w:val="outset" w:sz="6" w:space="0" w:color="auto"/>'
               '<w:right w:val="outset" w:sz="6" w:space="0" w:color="auto"/></w:tblBorders>'
               '<w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:bottom w:w="40" w:type="dxa"/>'
               '</w:tblCellMar><w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0"'
               ' w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr>'
               '<w:tblGrid>' + "".join('<w:gridCol w:w="%d"/>' % x for x in w) + "</w:tblGrid>"]

        # title row: one cell spanning the table, bold
        hdr_tr = '<w:trPr><w:tblHeader/><w:jc w:val="center"/></w:trPr>'
        out.append("<w:tr>" + hdr_tr
                   + ('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/><w:gridSpan w:val="%d"/>'
                      % (total, n))
                   + "<w:tcBorders>" + (SGL % "top") + (SGL % "left") + (SGL % "bottom")
                   + (SGL % "right") + "</w:tcBorders>" + ZMAR + "</w:tcPr>"
                   + ('<w:p><w:pPr><w:spacing w:before="60" w:after="40"/></w:pPr>'
                      '<w:r><w:rPr><w:rFonts w:ascii="Arial" w:eastAsia="Times New Roman"'
                      ' w:hAnsi="Arial" w:cs="Arial"/><w:b/><w:bCs/><w:sz w:val="20"/>'
                      '<w:szCs w:val="22"/></w:rPr><w:t xml:space="preserve">%s</w:t></w:r></w:p>'
                      % esc(title))
                   + "</w:tc></w:tr>")

        # heading row: italic, centred, double rule beneath
        out.append("<w:tr>" + hdr_tr + "".join(
            cell(h, w[i], SGL, DBL, italic=True, jc="center") for i, h in enumerate(headers)) + "</w:tr>")

        # body rows: the first takes the double rule on top, to meet the heading row's
        for r, row in enumerate(rows):
            top = DBL if r == 0 else SGL
            out.append('<w:tr><w:trPr><w:jc w:val="center"/></w:trPr>' + "".join(
                cell(str(c), w[i], top, SGL,
                     jc=("center" if i in center_cols else None),
                     ind=(171 if i == 0 else 0))
                for i, c in enumerate(row)) + "</w:tr>")

        out.append("</w:tbl>")
        self.paras.append("".join(out))
        # Word needs a paragraph after a table: without one, two tables in a row merge into one and
        # a table cannot be the last block before sectPr.
        self._p("", after=100)

    def caption(self, text):
        """A figure caption carrying the document's Caption STYLE, not hand-applied formatting.

        The style is what makes a caption italic, centered and 3 pt below its figure. A caption typed
        as an ordinary paragraph inherits the BODY font and renders upright black Times beside the
        others - which looks right as you type it and wrong on the page. Write the text Mixed Case
        with no closing period: "Figure 4. The Finished Collage with All Layers in Their Final
        Positions".

        This module cannot place images, so when a figure is pasted in afterward, set the image's own
        paragraph to the Figure style: it carries keepNext, so the figure can never separate from its
        caption, and its `next` is Caption, so pressing Enter after it lands in the right style.
        """
        # The run carries NO rPr on purpose. Every other paragraph shape here writes explicit Times
        # New Roman onto each run, and direct formatting beats a style - so a caption built that way
        # would reference the Caption style and still render as upright black Times beside the ones
        # that inherit it. An empty run lets the style govern, which is the whole point.
        self.paras.append('<w:p><w:pPr><w:pStyle w:val="Caption"/></w:pPr>'
                          '<w:r><w:t xml:space="preserve">%s</w:t></w:r></w:p>' % esc(text))

    def image(self, path, width_in=None):
        """Place a figure, centered, in the Figure style - so it cannot part from its caption.

        Call caption() immediately afterward. The image is scaled to `width_in` (default: the
        full 6.5 in text column, or its natural size at 96 dpi if that is narrower), aspect
        ratio preserved. The Figure style carries keepNext and names Caption as what follows,
        which is what keeps a figure and its caption on the same page.
        """
        px_w, px_h = _pixel_size(path)
        want = width_in if width_in else min(TEXT_WIDTH_IN, px_w / 96.0)
        cx = int(want * EMU_PER_IN)
        cy = int(cx * px_h / px_w)
        ext = os.path.splitext(path)[1].lower().lstrip(".")
        ext = "jpeg" if ext == "jpg" else ext
        n = len(self.images) + 1
        name = "media/image%d.%s" % (n, ext)
        with open(path, "rb") as f:
            self.images.append((name, f.read(), ext))
        rid = "rIdImg%d" % n
        self.paras.append(
            '<w:p><w:pPr><w:pStyle w:val="Figure"/></w:pPr><w:r><w:drawing>'
            '<wp:inline distT="0" distB="0" distL="0" distR="0">'
            '<wp:extent cx="%d" cy="%d"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
            '<wp:docPr id="%d" name="Figure %d"/>'
            '<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            '<a:graphic><a:graphicData uri="%s">'
            '<pic:pic><pic:nvPicPr><pic:cNvPr id="%d" name="image%d.%s"/><pic:cNvPicPr/></pic:nvPicPr>'
            '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
            "</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>"
            % (cx, cy, n, n, PIC, n, n, ext, rid, cx, cy)
        )

    def code(self, text):
        """A command line, set in Consolas and indented. Sits tight to the step that introduces it
        (keepNext), so an instruction is never separated from the command it names."""
        ppr = ('<w:pPr><w:keepNext/><w:keepLines/><w:ind w:left="720"/>'
               '<w:spacing w:before="60" w:after="120"/></w:pPr>')
        rpr = ('<w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>'
               '<w:color w:val="000000"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr>')
        self.paras.append('<w:p>%s<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:p>'
                          % (ppr, rpr, esc(text)))

    def listing(self, text):
        """A multi-line code listing: Consolas 9 pt, indented, lines tight together.

        Deliberately NOT code(): that glues its line to the paragraph below with keepNext, which is
        right for one command under the step that names it and wrong for a block - sixty lines
        cannot be kept with the next paragraph, and 6 pt between every line makes a script unreadable.
        """
        rpr = ('<w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>'
               '<w:color w:val="000000"/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>')
        ppr = '<w:pPr><w:ind w:left="360"/><w:spacing w:before="0" w:after="0"/></w:pPr>'
        for line in text.splitlines():
            self.paras.append('<w:p>%s<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:p>'
                              % (ppr, rpr, esc(line)))

    def page_break(self):
        self.paras.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    # --- packaging ---------------------------------------------------------
    def _parts(self):
        # A footerReference must come FIRST inside sectPr - CT_SectPr fixes that order, and Word
        # rejects the package if the page size precedes it.
        ftr_ref = '<w:footerReference w:type="default" r:id="rId9"/>' if self.page_numbers else ""
        document = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:document xmlns:w="%s" xmlns:r="%s" xmlns:wp="%s" xmlns:a="%s" xmlns:pic="%s">'
            "<w:body>%s"
            '<w:sectPr>%s<w:pgSz w:w="12240" w:h="15840"/>'
            '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"'
            ' w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>'
            "</w:body></w:document>" % (W, OFF, WP, DML, PIC, "".join(self.paras), ftr_ref)
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
            '<w:name w:val="Normal"/><w:qFormat/></w:style>'
            # Caption and Figure, cloned from the User Guide's own definitions so a document built
            # here matches the ones Glen has been writing by hand. Caption = Arial 10 pt italic gray,
            # centered, 3 pt above. Figure carries keepNext so an image cannot part from its caption,
            # and names Caption as what follows it.
            '<w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="caption"/>'
            '<w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>'
            '<w:pPr><w:keepLines/><w:spacing w:before="60" w:after="200"/>'
            '<w:jc w:val="center"/></w:pPr>'
            '<w:rPr><w:rFonts w:ascii="Arial" w:eastAsia="Arial" w:hAnsi="Arial" w:cs="Arial"/>'
            '<w:i/><w:iCs/><w:color w:val="444444"/><w:sz w:val="20"/><w:szCs w:val="20"/>'
            '</w:rPr></w:style>'
            '<w:style w:type="paragraph" w:customStyle="1" w:styleId="Figure">'
            '<w:name w:val="Figure"/><w:basedOn w:val="Normal"/><w:next w:val="Caption"/>'
            '<w:pPr><w:keepNext/><w:spacing w:before="320" w:after="0"/>'
            '<w:jc w:val="center"/></w:pPr></w:style>'
            "</w:styles>" % W
        )
        numbering = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:numbering xmlns:w="%s">'
            '<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="singleLevel"/>'
            '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/>'
            '<w:lvlText w:val="%%1."/><w:lvlJc w:val="left"/>'
            '<w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl></w:abstractNum>'
            "%s</w:numbering>" % (
                W,
                # One <w:num> per list new_list() handed out, each restarting the shared abstract
                # definition's counter at 1. The override is what actually restarts it.
                "".join('<w:num w:numId="%d"><w:abstractNumId w:val="0"/>'
                        '<w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride>'
                        "</w:num>" % n for n in range(1, self.numid + 1)))
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
        defaults = ""
        for ext in sorted({e for _, _, e in self.images}):
            defaults += '<Default Extension="%s" ContentType="image/%s"/>' % (ext, ext)
        for i, (name, _, _) in enumerate(self.images, 1):
            doc_rel += ('<Relationship Id="rIdImg%d" Type="%s/image" Target="%s"/>'
                        % (i, OFF, name))
        content_types = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>%s%s</Types>'
            % (defaults, overrides)
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
        for name, blob, _ in self.images:        # binary parts, validated by being readable
            parts["word/" + name] = blob
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
