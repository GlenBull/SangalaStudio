# -*- coding: utf-8 -*-
"""What Undo currently covers in Sangala Studio, as a .docx in the Drafts folder.

Glen asked for this on 2026-09-12, after Elaine Wolfe's "is there an Undo/Redo feature?" Everything
in it was read out of SangalaStudio.html at 2026-09-12.210 - serializeState(), commit(),
scheduleCommit(), restoreState(), openProject() - rather than from the interface, because the
interface says nothing about Undo at all.

    python "tools/docs/make_undo_coverage.py"

DO NOT RUN THIS AGAINST _Drafts AGAIN. It built Ver 1.0 and 1.1; Glen then revised the document
and saved it as "Sangala Studio Undo (Ver 1.2.docx" - his title, his headings, his wording. That
version is HIS, and regenerating would drop a rival file beside it rather than overwrite it,
because save() takes the next FREE number - and archiving a version frees its number again,
which is how a second Ver 1.0 appeared on 2026-09-12. Revise his file in place instead.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from makedocx import Doc

DRAFTS = (r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts")
EM = "\u2014"

d = Doc()
d.title("What Undo Covers in Sangala Studio")

d.body("Sangala Studio undoes with Ctrl-Z and redoes with Ctrl-Shift-Z or Ctrl-Y. No button, menu or "
       "label anywhere in the interface names either one, so the feature is reached only by someone "
       "who already knows it is there.")

d.heading("How It Decides What to Remember")
d.body("The application takes a snapshot of the design once editing settles, and that snapshot "
       "records one thing: the list of objects. For each object it keeps the drawing element, every "
       "attribute that element carries, the classification of the line, the outline, any interior "
       "loops, any baked three-dimensional mesh, and the grouping. Nothing else is recorded. A "
       "snapshot identical to the one before it is discarded, and sixty are held at a time.")
d.body("One rule follows from that, and it settles every case. A change that lands in an object or "
       "in one of its attributes can be undone. A change that lives anywhere else " + EM + " a "
       "setting, a mode, a view " + EM + " is invisible to Undo, and pressing Ctrl-Z after making one "
       "will step past it to the last change that did touch the design.")

d.heading("Actions Undo Covers")
d.body("The following can be undone and redone.", before_list=True)
for s in [
    "Drawing and editing shapes: Pen paths, rectangles, circles and lines, node edits, and moving, "
    "resizing or rotating a shape.",
    "Deleting a shape, and duplicating one by copy and paste.",
    "Combining shapes by union, difference or intersection, including the mesh that is baked.",
    "Aligning and mirroring.",
    "Grouping and ungrouping, including nested groups.",
    "Changing layer order: to front, to back, raise and lower.",
    "Reclassifying a line as a cut line, a score line or printed artwork.",
    "Paper color.",
    "Labels: the text, where it sits, and its size.",
    "Marking a shape as a hole.",
    "Three-dimensional shape settings: depth, base, the angle of each sloped side, cone taper and "
    "invert.",
    "Bars, and the holes they bore through a part.",
    "Plane settings: the name, depth and base of a plane, its mirror state, its stud override, and "
    "hiding a plane or a part.",
    "The choice of brick part, and its fit.",
    "Anything that arrives as objects: the shapes of an imported design, a drawing brought in from "
    "Snap!, and the outlines a traced photograph produces.",
]:
    d.step(s)

d.heading("Actions Undo Does Not Cover")
d.new_list()   # the second list restarts at 1; without this it continues from the first
d.body("The following are not recorded, and Ctrl-Z will not reverse them.", before_list=True)
for s in [
    "Force, speed, blade depth, the number of passes and the scale percentage.",
    "The choice of material.",
    "The unit of measurement.",
    "Page size, and turning the mat between portrait and landscape.",
    "The position offsets.",
    "The registration marks toggle.",
    "Switching between two-dimensional and three-dimensional mode.",
    "Zoom and pan.",
    "A reference photograph, the background removed from it, and the tuning of its trace. Adding "
    "one, clearing it or tracing it again cannot be undone, although the outlines a trace produces "
    "can be.",
]:
    d.step(s)

d.heading("Two Behaviors Worth Knowing")
d.item("While the Pen Is Drawing. ",
       "Ctrl-Z takes back the last point placed rather than reverting the design. It undoes the "
       "design only when no path is in progress. This is deliberate.")
d.item("After Opening an SVG. ",
       "The history is not cleared, so pressing Ctrl-Z enough times steps back into the design that "
       "was open before. Opening a project file does clear it. The two behave differently, and the "
       "difference appears to be unintended.")

print(d.save(DRAFTS, "What Undo Covers in Sangala Studio"))
