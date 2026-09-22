# -*- coding: utf-8 -*-
"""User Guide Ver 9.3 -> Ver 9.4: the traced photograph stays and prints; there is no Position.

Studio 2026-09-22.211-.214 changed what a reader of Sections 4, 12 and 13 would see. Confirm now turns
the red outline into a cut line ON the photograph and leaves the photograph in place, and it prints.
With Marks on, the mat shades the margin the marks occupy. The Position setting is gone, so a design
cuts where it sits. Section 12 also still sent the reader into Setup for the Material, which has sat
below Make It! since July.

Run-level edits only; no paragraph is added or removed.

    python "tools/docs/edit_ug_94.py"
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from runedit import DocEdit, ptext

B = r"D:\Code Projects\Silhouette Tools\Documents"
d = DocEdit(os.path.join(B, "User Guide (Ver 9.3).docx"))

# Section 4 - Confirm
p = d.para("Sangala Studio removes the background outside of the red cut line")
d.set_run(p, 2, ". Sangala Studio turns the red line into a cut line that sits on the subject. The "
                "photograph stays beneath it: the photograph is what prints, and the cut line is where "
                "the blade will go. A photograph that is no longer wanted can be selected and deleted.")

# Section 4 - Marks on
p = d.para("Three marks appear on the page; the die cutter reads them")
d.set_run(p, 2, " on. Three marks appear on the page, and the margin they occupy is shaded, with a dashed "
                "line inside it. Keep the picture inside the dashed line so that nothing prints over a "
                "mark; the die cutter reads the marks to line the blade up with the printed picture.")

# Section 12 - Material is below Make It!, and there is no Position
p = d.para("if the design should sit at a particular spot on the mat")
d.replace_run(p, 0, [("Choose the ", None)])
d.replace_run(p, 1, [("Material", "i")])
d.set_run(p, 2, " from the list below the ")
d.replace_run(p, 3, [("Make It!", "i")])
d.set_run(p, 4, " button (Paper, Sticker Paper, Cardstock, Heavy Cardstock, Vinyl, Custom, or Pen (draw)). "
                "This is used to adjust Force, Speed, Blade, and the ")
d.set_run(p, 5, "number of Passes; thicker material needs more force and more passes. ")
d.set_run(p, 6, "Custom")
d.set_run(p, 7, " opens ")
d.set_run(p, 8, "Settings")
d.set_run(p, 9, " (the gear icon) so that they can be set by hand. A design is cut exactly where it sits "
                "on the page, so there is no position to set. ")

# Section 13 - what each save keeps
p = d.para("the picture is no longer just a reference")
d.set_run(p, 0, "Once the background has been removed and the outline confirmed, the photograph stays under "
                "its new cut line and prints with it. Save project keeps it; Save as SVG carries the cut "
                "outline alone. A photograph cropped to a shape becomes part of the print-and-cut design, "
                "and either save keeps it.")

text = " ".join(ptext(x) for x in d.root.iter(d.root.tag.replace("document", "p")))
for gone in ("Set the Position", "removes the background outside", "Either save keeps it, and it reappears"):
    assert gone not in text, gone
d.save(os.path.join(B, "User Guide (Ver 9.4).docx"), os.path.join(B, ".Archive"))
