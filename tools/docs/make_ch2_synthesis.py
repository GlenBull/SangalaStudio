# -*- coding: utf-8 -*-
"""Build the Chapter 2 revision synthesis for the Design through Making Notes folder.

Chapter 2 was edited against the Editorial Rules and issued as Ver 3.0. Jo Watts reviewed that
version, found 63 violations, and corrected them by hand as Ver 3.1. This states what the revision
did, grouped by pattern rather than listed one change at a time.

    python "tools/docs/make_ch2_synthesis.py"
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from makedocx import Doc

NOTES = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\Chapters\Notes"
LQ, RQ, DASH, APOS = "\u201c", "\u201d", "\u2014", "\u2019"

d = Doc()
d.title("What the Chapter 2 Revision Changed")

d.body("Chapter 2 was edited against the Editorial Rules and issued as Version 3.0. A review of that "
       "version identified 63 violations of the rules, which were corrected by hand in Version 3.1. "
       "This note compares the two and states what the revision did, grouped by the pattern each "
       "change belongs to rather than listed one change at a time.")
d.body("The revision touched 20 passages, covering roughly 35 of the chapter" + APOS + "s 85 "
       "paragraphs, and removed 336 words. The chapter is a tenth shorter than it was.")

d.heading("A Single Habit in Several Forms")
d.body("The violations are not scattered slips. Most are one habit appearing in different guises: "
       "prose that admires the subject rather than describing it. Version 3.0 called a cut silhouette "
       + LQ + "a satisfying object by itself," + RQ + " said that " + LQ + "flat shapes, stacked with "
       "care, become a world," + RQ + " described design decisions as " + LQ + "genuinely interesting,"
       + RQ + " and named the move from screen to paper " + LQ + "one of the most satisfying moments "
       "in the making process." + RQ + " The revision removed each of these outright rather than "
       "softening them. What remains states what the reader does and what the material does.")
d.body("A quotation had also been introduced with no attribution " + DASH + " " + LQ + "Every material "
       "has its own character, and the designer who works with materials learns from them" + RQ
       + " " + DASH + " and the revision deleted it.")

d.heading("Announcements Replaced by the Thing Itself")
d.body("Rule 1 accounts for five of the violations, and the repairs share a shape: the sentence that "
       "announces a move is replaced by the move.", before_list=True)
d.item("Version 3.0. ", "The next step, from the isolated silhouette to the complete scene, is a paper "
       "collage " + DASH + " a form with deep roots in fine art, folk craft, and graphic design "
       "traditions.")
d.item("Version 3.1. ", "Extending the paper silhouette to a full collage creates a completed "
       "composition. As an art form, collage has deep roots in fine art, folk craft, and graphic "
       "design traditions.")
d.body("The same correction runs through the chapter. " + LQ + "In this chapter, the central element "
       "is the Crowned Crane silhouette created in Chapter 1" + RQ + " becomes " + LQ + "The work in "
       "this chapter begins with the Crowned Crane silhouette created in Chapter 1," + RQ + " and "
       + LQ + "With the crane and grass in place, the composition is a figure without a setting" + RQ
       + " is cut entirely in favor of " + LQ + "Adding background elements creates a more complete "
       "scene." + RQ)

d.heading("The Passive Repairs Are the Clearest Lesson")
d.body("Rule 17 accounts for fifteen violations, the largest single group. The repairs are worth study "
       "because they produce better sentences rather than merely compliant ones: naming the agent also "
       "addresses the reader.", before_list=True)
d.item("Version 3.0. ", "A photo opened only as a reference for tracing is not saved. Once the "
       "background of a shape has been removed to create a silhouette outline, the picture becomes "
       "part of the print-and-cut design.")
d.item("Version 3.1. ", "Sangala Studio does not save a photo you opened only to trace over. If you "
       "remove a photo" + APOS + "s background to leave an outline, the photo becomes part of the "
       "design.")

d.heading("False Contrast, Circular Claims, and Series")
d.body("Where a claim was built on a contrast that does not hold, the revision kept the idea and "
       "discarded the frame. " + LQ + "These are the questions that distinguish a designer from a "
       "technician: not just how to do something, but why to do it in a particular way" + RQ
       + " became " + LQ + "A designer asks why to do something one way rather than another; a "
       "technician asks only how." + RQ)
d.body("Circular statements were rewritten to state the requirement once. " + LQ + "The key principle "
       "is contrast: each layer of the collage must be distinguishable from the layers behind it" + RQ
       + " loses its opening clause, and " + LQ + "The silhouette depends on contrast to be seen" + RQ
       + " becomes " + LQ + "The silhouette" + APOS + "s visibility requires contrast." + RQ)
d.body("Illustrative series were cut wherever the list carried no information the reader needed. The "
       "colors of the collage " + DASH + " " + LQ + "a deep green for the grass, brown for the tree "
       "trunk, gold for the crane, blue and orange for the sky layers" + RQ + " " + DASH + " and the "
       "moods of the sky " + DASH + " " + LQ + "a deep indigo for pre-dawn, a warm orange-red for "
       "sunrise, a clear blue for midday" + RQ + " " + DASH + " are both gone.")

d.heading("Corrections of Fact")
d.body("Four changes are not matters of style, and they matter more than the rest.", before_list=True)
d.item("The controls were misnamed. ", "Version 3.0 described the row across the top as menus. They "
       "are buttons, and the revision counts them: " + LQ + "The menu bar at the top of the window "
       "contains six buttons." + RQ + " The 2D and 3D control was likewise described as a menu.")
d.item("The section heading was wrong. ", LQ + "The Mat" + RQ + " became " + LQ + "The Workspace,"
       + RQ + " which is what the section describes.")
d.item("The canvas lost its purpose. ", "The revision restores what the surrounding canvas is for: "
       "components can be parked there while the main composition is assembled on the mat.")
d.item("A capability was left implicit. ", "The account of printing before cutting now says plainly "
       "what it achieves: a brown tree with green leaves can be printed on a single sheet of "
       "cardstock and cut as one piece.")

d.heading("Rules That Do Not Exist")
d.body("Fourteen of the 63 fall under three headings that are not rules in Editorial Rules Version 2.0 "
       + DASH + " nominalization, paired coordination, and trailing participial clauses. These were "
       "preferences applied to the chapter as though they carried the authority of the rule set. "
       "Eight, four, and two changes respectively were made on that basis, and the review had to undo "
       "them. An edit made in the name of a rule that does not exist costs more than a missed "
       "violation, because nothing in the agreed standard authorizes it and the author has no way to "
       "anticipate it.")

d.heading("Carried Forward to the Next Revision")
d.body("Three points remain for the next pass.", before_list=True)
d.item("east Africa. ", "The acacia is described in Version 3.1 as a familiar shape on the West "
       "African landscape. The book is set at Mt. Elgon, and the term is written lowercase: east "
       "Africa.")
d.item("A missing word. ", LQ + "Begin connecting the Silhouette die cutter to your computer with the "
       "USB cable clicking Connect in Sangala Studio." + RQ)
d.item("Two mechanical slips. ", "A button " + LQ + "switch" + RQ + " rather than switches between 2D "
       "and 3D mode, and the sentence ending " + LQ + "objects that can be handled and manipulated"
       + RQ + " closes without a period.")

print(d.save(NOTES, "Chapter 2 Revision Synthesis"))
