# -*- coding: utf-8 -*-
"""Group A proposals for Chapter 3, in the same shape as the Chapter 2 notes: original on the left,
proposed revision on the right.

Group A of Editorial Rules Ver 2.1 is rules 1 to 6 - announcements, restatement, false contrast,
circular claims, overstatement, unverified assertions. Nothing here is applied; Rule 1 requires a
revision to be proposed rather than a sentence deleted, so every row carries one.

    python "tools/docs/make_ch3_groupA.py"
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from makedocx import Doc

NOTES = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\Chapters\Notes"

PROPOSALS = [
 ("1 / \u00b65",
  "This chapter takes that composition into actual three-dimensional space. A shadowbox is a framed "
  "construction in which cut paper panels are held at measurably different depths.",
  "A shadowbox is a framed construction in which cut paper panels are held at measurably different "
  "depths."),
 ("1 / \u00b613",
  "They introduce a new option in the Combine tool, the Union option, to merge the silhouette of the "
  "crane with the frame of the shadowbox.",
  "Cut, and name the Union option where it is first used, in the paragraph that merges the "
  "silhouette with the frame."),
 ("1 / \u00b631",
  "With the frame template saved, the next step is to merge each layer's silhouette into the "
  "circular window of its frame.",
  "Each layer's silhouette is merged into the circular window of its frame."),
 ("2 / \u00b612",
  "The frames connect to each other through folding tabs: narrow strips on either side that fold at "
  "a crease and glue to the face of the adjacent frame, establishing the spacing between layers.",
  "The frames connect to each other through folding tabs, which establish the spacing between "
  "layers. (The strip and the crease are described at \u00b622, where the reader makes one.)"),
 ("3 / \u00b643",
  "These discoveries - and the adjustments they call for - are not problems with the process. They "
  "are the process.",
  "These discoveries are the process."),
 ("5 / \u00b642",
  "The scene acquires a quality that no screen representation can fully anticipate.",
  "The panels cast shadows on one another, which the screen did not show."),
 ("5 / \u00b643",
  "A designer who iterates between the digital and the physical, adjusting and recutting, learns "
  "more than one who accepts the first result.",
  "Iterating between the digital and the physical, adjusting and recutting, is how the design is "
  "refined."),
 ("6 / \u00b660",
  "a comparison that points to the long history of papercraft as a medium for storytelling",
  "Either cite the history, or attribute the comparison: the designers describe the result as "
  "reminiscent of the layered illustrations in children's books."),
]

EXEMPT = [
 ("4 / \u00b69",
  "A shadowbox is a display case with enough depth between its front glass and back panel to hold "
  "objects or create a layered scene.",
  "Rule 4 does not reach a definition, whose work is to restate a term in other words."),
 ("5 / \u00b629",
  "Overwriting the template means rebuilding it from scratch.",
  "Rule 5 does not reach an absolute that holds by construction."),
 ("3 / \u00b631",
  "The silhouette is not simply placed inside the circle - it is integrated with it.",
  "Rule 3 reaches a contrast only where no reader would have believed the first term. A reader "
  "would plausibly expect the silhouette to be placed inside the circle."),
 ("3 / \u00b670",
  "not just arranged to imply distance, as the collages of Chapter 2 were, but were spaced apart",
  "The text established the first term in Chapter 2, so the contrast is real."),
]

d = Doc()
d.title("Chapter 3, Group A: Proposed Revisions")

d.body("Group A of Editorial Rules Version 2.1 covers Rules 1 through 6: announcements, restatement "
       "in new shapes, false contrast, circular claims, overstatement, and unverified assertions. "
       "Chapter 3 was read at Version 2.7, and eight passages fall under those rules. Nothing has "
       "been applied. Rule 1 requires that a revision be proposed in place of the sentence rather "
       "than the sentence deleted, so every row carries one.")

d.table("Table 1. Passages Falling Under Group A, with Proposed Revisions",
        ["Rule", "Original", "Proposed revision"],
        [[a, b, c] for a, b, c in PROPOSALS],
        weights=[1, 3, 3], center_cols=(0,))

d.heading("Passages Considered and Not Flagged")
d.body("Four passages would have been flagged under Version 2.0 and are exempt under the boundary "
       "clauses added in Version 2.1. They are listed so that the boundaries can be checked against "
       "the judgment they produced.")

d.table("Table 2. Passages the Boundary Clauses Exempt",
        ["Rule", "Passage", "Why it is exempt"],
        [[a, b, c] for a, b, c in EXEMPT],
        weights=[1, 3, 3], center_cols=(0,))

d.heading("Points That Are Not Rule Matters")
d.body("Five mechanical errors were noticed while reading. None falls under any rule, and none has "
       "been changed.", before_list=True)
d.step("Paragraph 17: differnce for difference.")
d.step("Paragraph 33: silhouettewithin, a missing space in the caption to Figure 3.7.")
d.step("Paragraph 39: Studio,with, a missing space in the caption to Figure 3.9.")
d.step("Paragraph 66: a closing quotation mark with no opening one.")
d.step("Paragraph 70: a tense break, are held apart by measurable distances ... but were spaced "
       "apart.")

print(d.save(NOTES, "Chapter 3 Group A Proposals"))
