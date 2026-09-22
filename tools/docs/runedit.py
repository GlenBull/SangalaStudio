# -*- coding: utf-8 -*-
"""Run-level edits to a .docx paragraph, shared by the edit_ug_* / edit_tm_* scripts.

A paragraph is found by a piece of its text that must occur in exactly one paragraph. Its runs are then
addressed by index (the order a dump of the paragraph shows them), and a run is replaced by one or more
new runs that copy its formatting - adding Consolas for a code identifier, or italic for a UI label. No
paragraph is added or removed and nothing outside the named runs is touched.
"""
import copy
import os
import shutil
import zipfile

from lxml import etree

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def ptext(p):
    return "".join(t.text or "" for t in p.iter(W + "t"))


def text_runs(p):
    return [r for r in p.iter(W + "r") if "".join(t.text or "" for t in r.iter(W + "t"))]


class DocEdit:
    def __init__(self, src):
        self.src = src
        self.z = zipfile.ZipFile(src)
        self.root = etree.fromstring(self.z.read("word/document.xml"))

    def para(self, key):
        hits = [p for p in self.root.iter(W + "p") if key in ptext(p)
                and not any(a.tag.endswith("}Fallback") for a in p.iterancestors())]
        assert len(hits) == 1, "%r is in %d paragraphs, not 1" % (key[:50], len(hits))
        return hits[0]

    def replace_run(self, p, idx, segments):
        """segments: list of (text, kind) with kind None, 'code' or 'i'. An empty list deletes the run."""
        runs = text_runs(p)
        old = runs[idx]
        parent = old.getparent()
        pos = parent.index(old)
        for text, kind in segments:
            r = copy.deepcopy(old)
            for t in r.findall(W + "t"):
                r.remove(t)
            rpr = r.find(W + "rPr")
            if kind:
                if rpr is None:
                    rpr = etree.SubElement(r, W + "rPr")
                    r.remove(rpr)
                    r.insert(0, rpr)
                if kind == "code":
                    f = rpr.find(W + "rFonts")
                    if f is None:
                        f = etree.Element(W + "rFonts")
                        rpr.insert(0, f)
                    for a in ("ascii", "hAnsi", "cs"):
                        f.set(W + a, "Consolas")
                elif kind == "i":
                    for tag in ("i", "iCs"):
                        if rpr.find(W + tag) is None:
                            rpr.append(etree.Element(W + tag))
            t = etree.SubElement(r, W + "t")
            t.text = text
            t.set(XML_SPACE, "preserve")
            pos += 1
            parent.insert(pos, r)
        parent.remove(old)

    def set_run(self, p, idx, text):
        runs = text_runs(p)
        ts = runs[idx].findall(W + "t")
        ts[0].text = text
        ts[0].set(XML_SPACE, "preserve")
        for t in ts[1:]:
            runs[idx].remove(t)

    def sub_in_run(self, p, idx, old, new):
        run = text_runs(p)[idx]
        full = "".join(t.text or "" for t in run.iter(W + "t"))
        assert full.count(old) == 1, "%r occurs %d times in run %d" % (old[:40], full.count(old), idx)
        self.set_run(p, idx, full.replace(old, new))

    def save(self, dst, archive_dir):
        doc = etree.tostring(self.root, xml_declaration=True, encoding="UTF-8", standalone=True)
        names = self.z.namelist()
        with zipfile.ZipFile(dst, "x", zipfile.ZIP_DEFLATED) as out:
            for n in ["[Content_Types].xml"] + [y for y in names if y != "[Content_Types].xml"]:
                out.writestr(self.z.getinfo(n), doc if n == "word/document.xml" else self.z.read(n))
        self.z.close()
        os.makedirs(archive_dir, exist_ok=True)
        shutil.move(self.src, os.path.join(archive_dir, os.path.basename(self.src)))
        print("wrote", dst, os.path.getsize(dst), "bytes; archived", os.path.basename(self.src))
