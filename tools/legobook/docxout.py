"""Write a Book out as a Word document, one step at a time, with the drawings embedded as images.

Follows the project's document conventions: Times New Roman 11 pt body, Arial 10 pt tables with a
merged bold title row, italic centered headings over a double rule, and 3 pt before / 2 pt after in
every cell. Headings carry keepNext + keepLines so a step title can never strand at the foot of a page.
"""
import os, re, struct, zipfile

EMU = 914400

def _plain(s):
    """The model writes its prose once, with light HTML for the booklet. Word takes it flat."""
    s = re.sub(r"<[^>]+>", "", s or "")
    for a, b in (("&mdash;", "—"), ("&nbsp;", " "), ("&times;", "×"),
                 ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()
NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"')

def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _png_size(path):
    with open(path, "rb") as f:
        return struct.unpack(">II", f.read(26)[16:24])

def _runs(text, *, font="Times New Roman", sz=22, bold=False, italic=False):
    rpr = ('<w:rPr><w:rFonts w:ascii="%s" w:hAnsi="%s"/>%s%s<w:sz w:val="%d"/><w:szCs w:val="%d"/></w:rPr>'
           % (font, font, "<w:b/>" if bold else "", "<w:i/>" if italic else "", sz, sz))
    out = []
    for i, seg in enumerate(text.split("\n")):
        out.append('<w:r>%s%s<w:t xml:space="preserve">%s</w:t></w:r>'
                   % (rpr, "<w:br/>" if i else "", _esc(seg)))
    return "".join(out)

def _para(text, *, font="Times New Roman", sz=22, bold=False, italic=False,
          before=100, after=100, align=None, keep_next=False):
    jc = '<w:jc w:val="%s"/>' % align if align else ""
    kn = "<w:keepNext/><w:keepLines/>" if keep_next else ""
    return ("<w:p><w:pPr>%s<w:spacing w:before=\"%d\" w:after=\"%d\"/>%s</w:pPr>%s</w:p>"
            % (kn, before, after, jc,
               _runs(text, font=font, sz=sz, bold=bold, italic=italic) if text else ""))

def _picture(rid, pid, w_in, px, py, *, before=60, after=60):
    cx = int(w_in * EMU); cy = int(cx * py / px)
    return ('<w:p><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="%d" w:after="%d"/>'
            '<w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
            '<wp:inline distT="0" distB="0" distL="0" distR="0">'
            '<wp:extent cx="%d" cy="%d"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
            '<wp:docPr id="%d" name="Step %d"/>'
            '<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic><pic:nvPicPr><pic:cNvPr id="%d" name="step%d.png"/><pic:cNvPicPr/></pic:nvPicPr>'
            '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
            '</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'
            % (before, after, cx, cy, pid, pid, pid, pid, rid, cx, cy))

def _cell(text, width, *, bold=False, italic=False, align=None, span=None, dbl=False):
    grid = '<w:gridSpan w:val="%d"/>' % span if span else ""
    b = ('<w:tcBorders><w:bottom w:val="double" w:sz="4" w:space="0" w:color="000000"/></w:tcBorders>'
         if dbl else "")
    jc = '<w:jc w:val="%s"/>' % align if align else ""
    p = ("<w:p><w:pPr><w:spacing w:before=\"60\" w:after=\"40\"/>%s</w:pPr>%s</w:p>"
         % (jc, _runs(text, font="Arial", sz=20, bold=bold, italic=italic)))
    return ('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s%s<w:vAlign w:val="top"/></w:tcPr>%s</w:tc>'
            % (width, grid, b, p))

def _table(title, heads, rows, widths):
    total = sum(widths)
    borders = ("<w:tblBorders>" + "".join(
        '<w:%s w:val="single" w:sz="4" w:space="0" w:color="000000"/>' % s
        for s in ("top", "left", "bottom", "right", "insideH", "insideV")) + "</w:tblBorders>")
    mar = ('<w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="108" w:type="dxa"/>'
           '<w:bottom w:w="0" w:type="dxa"/><w:right w:w="108" w:type="dxa"/></w:tblCellMar>')
    tr = ['<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>%s</w:tr>'
          % _cell(title, total, bold=True, span=len(widths))]
    tr.append('<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>%s</w:tr>'
              % "".join(_cell(h, w, italic=True, align="center", dbl=True) for h, w in zip(heads, widths)))
    for row in rows:
        tr.append("<w:tr><w:trPr><w:cantSplit/></w:trPr>%s</w:tr>"
                  % "".join(_cell(v, w, bold=(i == 0)) for i, (v, w) in enumerate(zip(row, widths))))
    return ('<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/>%s%s</w:tblPr>'
            '<w:tblGrid>%s</w:tblGrid>%s</w:tbl>'
            % (total, borders, mar, "".join('<w:gridCol w:w="%d"/>' % w for w in widths), "".join(tr)))

_STYLES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
           '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           '<w:docDefaults><w:rPrDefault><w:rPr>'
           '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>'
           '<w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr></w:rPrDefault>'
           '<w:pPrDefault><w:pPr><w:spacing w:before="100" w:after="100"/></w:pPr></w:pPrDefault>'
           '</w:docDefaults><w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
           '<w:name w:val="Normal"/><w:qFormat/></w:style></w:styles>')

_CT = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
       '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
       '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
       '<Default Extension="xml" ContentType="application/xml"/>'
       '<Default Extension="png" ContentType="image/png"/>'
       '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
       '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
       "</Types>")

_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
         '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
         '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
         "</Relationships>")

def write(book, images, out_path, *, table=None, image_width_in=2.15):
    """book: a Book. images: one PNG path per step. table: (title, heads, rows, widths) or None."""
    body = [_para(book.title, sz=34, bold=True, before=0, after=60, align="center", keep_next=True),
            _para(book.subtitle, sz=22, italic=True, before=0, after=200, align="center", keep_next=True)]
    if book.note:
        body.append(_para(_plain(book.note), italic=True, before=0, after=160))
    if table:
        body.append(_table(*table))
        body.append(_para("", before=0, after=0))

    rels = []
    for i, s in enumerate(book.steps):
        rid = "rIdImg%d" % (i+1)
        px, py = _png_size(images[i])
        rels.append((rid, "media/step%02d.png" % (i+1), images[i]))
        body.append(_para("Step %d.  %s" % (i+1, s["title"]), sz=26, bold=True,
                          before=120, after=50, keep_next=True))
        body.append(_picture(rid, 100+i, image_width_in, px, py))
        body.append(_para(_plain(s["text"]), before=40, after=60))
        body.append(_para("Add these pieces:  " + ";  ".join(lab for lab, _ in s["parts"]),
                          sz=20, italic=True, before=0, after=80))
    if book.closing:
        body.append(_para(book.closing[0], sz=26, bold=True, before=200, after=60, keep_next=True))
        body.append(_para(_plain(book.closing[1]), before=0, after=100))

    sect = ('<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
            '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
            'w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>')
    document = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<w:document %s><w:body>%s%s</w:body></w:document>' % (NS, "".join(body), sect))

    drels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
             '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
             '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>']
    for rid, target, _ in rels:
        drels.append('<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="%s"/>'
                     % (rid, target))
    drels.append("</Relationships>")

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", _CT)
        z.writestr("_rels/.rels", _RELS)
        z.writestr("word/_rels/document.xml.rels", "".join(drels))
        z.writestr("word/styles.xml", _STYLES)
        z.writestr("word/document.xml", document)
        for _, target, src in rels:
            z.write(src, "word/" + target)
    return out_path
