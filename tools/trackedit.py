"""Run-aware Word tracked-change edits on a .docx.

A deletion must become <w:del> wrapping runs whose <w:t> has been changed to <w:delText>, and an
insertion must become <w:ins> wrapping ordinary runs. The target text almost never lines up with run
boundaries - Word splits runs at spell-check marks, formatting and revision ids - so each touched run
is split into before / inside / after and only the inside part is marked.

Every edit is located by a UNIQUE substring of the paragraph's concatenated text. If it is absent, or
occurs more than once, the edit raises rather than guessing.
"""

import re

RUN = re.compile(r"<w:r(?:\s[^>]*)?>(?:(?!</w:r>).)*?</w:r>", re.S)
TXT = re.compile(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", re.S)
PARA = re.compile(r"<w:p(?:\s[^>]*)?>.*?</w:p>", re.S)
AUTHOR = "Editorial Rules pass"
DATE = "2026-08-08T00:00:00Z"


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def para_text(p):
    return "".join(TXT.findall(p))


class Editor:
    def __init__(self, doc):
        self.doc = doc
        self.rid = 1000
        self.log = []

    def _next(self):
        self.rid += 1
        return self.rid

    def find_para(self, needle):
        hits = [m for m in PARA.finditer(self.doc) if needle in para_text(m.group(0))]
        if len(hits) != 1:
            raise ValueError("paragraph locator %r matched %d paragraphs" % (needle[:60], len(hits)))
        return hits[0]

    def delete(self, locator, target, note=""):
        """Mark `target` deleted inside the single paragraph containing `locator`."""
        m = self.find_para(locator)
        para = m.group(0)
        text = para_text(para)
        if text.count(target) != 1:
            raise ValueError("target %r occurs %d times in its paragraph"
                             % (target[:60], text.count(target)))
        start = text.index(target)
        end = start + len(target)

        out, pos = [], 0
        runs = list(RUN.finditer(para))
        pieces = {}
        for r in runs:
            rt = "".join(TXT.findall(r.group(0)))
            a, b = pos, pos + len(rt)
            pos = b
            lo, hi = max(a, start), min(b, end)
            if lo >= hi:                                  # this run is untouched
                continue
            rpr = re.search(r"<w:rPr>.*?</w:rPr>", r.group(0), re.S)
            rpr = rpr.group(0) if rpr else ""
            before, inside, after = rt[:lo - a], rt[lo - a:hi - a], rt[hi - a:]
            new = ""
            if before:
                new += '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, esc(before))
            new += ('<w:del w:id="%d" w:author="%s" w:date="%s">'
                    '<w:r>%s<w:delText xml:space="preserve">%s</w:delText></w:r></w:del>'
                    % (self._next(), AUTHOR, DATE, rpr, esc(inside)))
            if after:
                new += '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, esc(after))
            pieces[r.group(0)] = (r.start(), r.end(), new)

        if not pieces:
            raise ValueError("no run overlapped the target %r" % target[:60])
        # Rebuild the paragraph, replacing touched runs by offset so untouched content survives.
        spans = sorted(pieces.values())
        new_para, last = "", 0
        for s, e, rep in spans:
            new_para += para[last:s] + rep
            last = e
        new_para += para[last:]

        if self.doc.count(para) != 1:
            raise ValueError("paragraph is not unique in the document")
        self.doc = self.doc.replace(para, new_para, 1)
        self.log.append(("delete", target, note))
        return self

    def replace(self, locator, target, replacement, note=""):
        """Mark `target` deleted and `replacement` inserted in its place, as one adjacent pair.

        Word shows this as a substitution rather than as an unrelated deletion and insertion some
        distance apart, and Reject restores exactly the original wording.
        """
        m = self.find_para(locator)
        para = m.group(0)
        text = para_text(para)
        if text.count(target) != 1:
            raise ValueError("target %r occurs %d times" % (target[:60], text.count(target)))
        start, end = text.index(target), text.index(target) + len(target)
        pos, spans = 0, []
        for r in RUN.finditer(para):
            rt = "".join(TXT.findall(r.group(0)))
            a, b = pos, pos + len(rt)
            pos = b
            lo, hi = max(a, start), min(b, end)
            if lo >= hi:
                continue
            rpr = re.search(r"<w:rPr>.*?</w:rPr>", r.group(0), re.S)
            rpr = rpr.group(0) if rpr else ""
            before, inside, after = rt[:lo - a], rt[lo - a:hi - a], rt[hi - a:]
            new = ""
            if before:
                new += '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, esc(before))
            new += ('<w:del w:id="%d" w:author="%s" w:date="%s">'
                    '<w:r>%s<w:delText xml:space="preserve">%s</w:delText></w:r></w:del>'
                    % (self._next(), AUTHOR, DATE, rpr, esc(inside)))
            if hi == end:                       # the insertion goes once, at the end of the target
                new += ('<w:ins w:id="%d" w:author="%s" w:date="%s">'
                        '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:ins>'
                        % (self._next(), AUTHOR, DATE, rpr, esc(replacement)))
            if after:
                new += '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, esc(after))
            spans.append((r.start(), r.end(), new))
        if not spans:
            raise ValueError("no run overlapped %r" % target[:60])
        new_para, last = "", 0
        for a, b, rep in sorted(spans):
            new_para += para[last:a] + rep
            last = b
        new_para += para[last:]
        if self.doc.count(para) != 1:
            raise ValueError("paragraph is not unique")
        self.doc = self.doc.replace(para, new_para, 1)
        self.log.append(("replace", "%s -> %s" % (target, replacement), note))
        return self

    def insert(self, locator, after_text, addition, note=""):
        """Insert `addition` immediately after `after_text` in the paragraph holding `locator`."""
        m = self.find_para(locator)
        para = m.group(0)
        text = para_text(para)
        if text.count(after_text) != 1:
            raise ValueError("anchor %r occurs %d times" % (after_text[:50], text.count(after_text)))
        cut = text.index(after_text) + len(after_text)
        pos = 0
        for r in RUN.finditer(para):
            rt = "".join(TXT.findall(r.group(0)))
            a, b = pos, pos + len(rt)
            pos = b
            if not (a < cut <= b):
                continue
            rpr = re.search(r"<w:rPr>.*?</w:rPr>", r.group(0), re.S)
            rpr = rpr.group(0) if rpr else ""
            head, tail = rt[:cut - a], rt[cut - a:]
            new = ""
            if head:
                new += '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, esc(head))
            new += ('<w:ins w:id="%d" w:author="%s" w:date="%s">'
                    '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:ins>'
                    % (self._next(), AUTHOR, DATE, rpr, esc(addition)))
            if tail:
                new += '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, esc(tail))
            new_para = para[:r.start()] + new + para[r.end():]
            self.doc = self.doc.replace(para, new_para, 1)
            self.log.append(("insert", addition, note))
            return self
        raise ValueError("could not place the insertion")
