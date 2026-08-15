"""Depth-aware paragraph finder for trackedit: a Word text box nests its own <w:p>."""
import os
import re
import sys
import zipfile

sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
import trackedit

# Two of the paragraphs to correct hold a floating figure in a Word text box, and a text box carries
# its own <w:p> inside the paragraph that anchors it. trackedit's PARA regex is non-greedy, so it
# closes the outer paragraph on the BOX's </w:p> and the real text after the box falls outside every
# match - the locator then finds nothing. This finder counts depth instead, so a paragraph is the
# whole paragraph however many boxes are nested in it.
PTAG = re.compile(r"<w:p(?:\s[^>]*)?>|</w:p>")


class Shim(object):
    def __init__(self, text):
        self.text = text

    def group(self, _n):
        return self.text


OPEN = re.compile(r"<w:p(?:\s[^>]*)?>")


def _self_closing(tag):
    """Word writes an empty paragraph as <w:p .../>, which opens and closes in one tag. Counting it
    as an opener runs the depth away and swallows every paragraph after it."""
    return tag.endswith("/>")


class BoxEditor(trackedit.Editor):
    def _spans(self):
        out, i = [], 0
        while True:
            m = OPEN.search(self.doc, i)
            if not m:
                return out
            if _self_closing(m.group(0)):
                i = m.end()
                continue
            depth, end = 0, None
            for t in PTAG.finditer(self.doc, m.start()):
                if _self_closing(t.group(0)):
                    continue
                depth += -1 if t.group(0).startswith("</") else 1
                if depth == 0:
                    end = t.end()
                    break
            if end is None:
                return out
            out.append((m.start(), end))
            i = end

    def find_para(self, needle):
        hits = [self.doc[a:b] for a, b in self._spans()
                if needle in trackedit.para_text(self.doc[a:b])]
        if len(hits) != 1:
            raise ValueError("paragraph locator %r matched %d paragraphs" % (needle[:60], len(hits)))
        return Shim(hits[0])

