# -*- coding: utf-8 -*-
"""Tech Manual Ver 4.0 -> Ver 4.1: the reference photo prints; Position is gone; the registration zone.

Studio 2026-09-22.211-.214. The manual said refImg "never cuts, prints, or saves" and that placement was
built from Scale % AND Position. Confirm now leaves the photo in place and printSheet draws it; the
Position offset is removed (it drew shapes 12.7 mm from their stored coordinates while the photo and the
print did not move); the print and the registered cut add no offset of their own; and the mat shades the
mark margin while Marks are on.

Run-level edits only; no paragraph is added or removed.

    python "tools/docs/edit_tm_41.py"
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from runedit import DocEdit, ptext, text_runs

B = r"D:\Code Projects\Silhouette Tools\Documents"
d = DocEdit(os.path.join(B, "Tech Manual (Ver 4.0).docx"))

# the reference photo
p = d.para("drawn beneath the vectors as tracing scaffolding")
d.replace_run(p, len(text_runs(p)) - 1, [
    (" — drawn beneath the vectors. It never cuts, because the blade is sent objects and the photo is "
     "not one. It does print: ", None), ("printSheet", "code"),
    (" draws it at its own position under the design, so a traced subject prints as a picture and is cut "
     "round its outline. Confirm (", None), ("integrateTrace", "code"),
    (") converts the trace into cut objects at the photo's exact position and leaves the photo in place. "
     "A .model project file stores the photo; Export SVG does not.", None)])

# coordinate systems - no Position
p = d.para("built from the Scale % and Position settings")
d.sub_in_run(p, 7, ") built from the Scale % and Position settings, so aligning objects in design-mm is "
                   "equivalent to aligning them on the page. ",
             ") built from the Scale % setting alone, so aligning objects in design-mm is equivalent to "
             "aligning them on the page. There is no Position offset. The setting was removed in "
             "2026-09-22.214: it drew every shape 12.7 mm from its stored coordinates while the reference "
             "photo and the printed sheet did not move, so a traced outline landed beside its subject and "
             "the mat disagreed with the print. A shape now sits, prints and cuts at one set of "
             "coordinates. ")

# the project file
p = d.para("passes, scale, position, the registration-marks toggle")
d.sub_in_run(p, 8, "passes, scale, position, the registration-marks toggle",
             "passes, scale, the registration-marks toggle")

p = d.para("re-ranges the position fields and")
d.set_run(p, 1, " restores the page size and the units. A file saved while the Position setting existed "
                "carries ")
d.replace_run(p, 2, [("offx", "code")])
d.set_run(p, 3, " and ")
d.replace_run(p, 4, [("offy", "code")])
d.set_run(p, 5, "; its shapes are moved by that offset once on open, so they reopen where the mat showed "
                "them. A new file writes both as zero, which Sangala Blocks reads as no shift. A file "
                "written before the page-size key existed carries no page size; the current workspace is "
                "then left alone rather than forced to Letter, since an older file cannot say which "
                "workspace it was authored on.")

# registration - the zone, and no offset
p = d.para("The setup sequence is ")
d.sub_in_run(p, len(text_runs(p)) - 1, "), which reverse-engineered Silhouette Studio.",
             "), which reverse-engineered Silhouette Studio. The page sends page coordinates: the bridge "
             "subtracts the 15.9 mm mark origin from every point itself, so neither the print nor the "
             "registered cut adds an offset of its own. While Marks are on, the mat shades the margin the "
             "marks occupy and draws a dashed line inside it; nothing moves a design out of that margin, "
             "so the user can see it and keep clear of it.")

# the Snap! import note
p = d.para("That pinned Scale to 1 and Position to zero")
d.sub_in_run(p, 3, "That pinned Scale to 1 and Position to zero,", "That pinned Scale to 1,")

text = " ".join(ptext(x) for x in d.root.iter(d.root.tag.replace("document", "p")))
for gone in ("never cuts, prints, or saves", "Scale % and Position settings", "scale, position,",
             "re-ranges the position fields", "and Position to zero"):
    assert gone not in text, gone
d.save(os.path.join(B, "Tech Manual (Ver 4.1).docx"), os.path.join(B, ".Archive"))
