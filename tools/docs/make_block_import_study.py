"""Builds 'Importing a Sangala Blocks Figure into Sangala Studio' for the _Drafts folder.

Ver 1.0-1.4 were a FEASIBILITY STUDY: a thirteen-agent reading of both applications on 2026-08-20
(run wf_d37e2843-288) - five readers over the two codebases, three competing designs for the
handoff, four adversarial checks, and a synthesis.

Ver 1.5 is a RECORD OF WHAT WAS BUILT, on the same day. Three of the study's conclusions did not
survive contact with the work, and they are kept in the document rather than quietly deleted:

  * The study proposed rebuilding each slope as a rectangle carrying a per-edge roof angle, and
    costed the approximation that forces (a 0.6 mm lip where the real part stands vertical for 1.6,
    so a 33-degree slope arriving at 29.4). None of it was needed. The figure imports with its
    PROFILE in the plan, and in that orientation a slope's ramp lies IN THE PAGE - so the part
    simply is its own measured outline, exactly, and no angle is parsed from any part's name.
  * The study reported that 43712's shape could not be carried and that the wings would arrive as
    rectangular slabs. On the profile plane the tracer returns twelve points INCLUDING the curve.
  * The study recommended that the importer arrive at roughly five consolidated masses. Glen
    rejected it: "a student will never print the blocks ... not just a block diagram for what might
    become a crane with a lot of work." Boxes grouped into masses are still boxes; what makes the
    import worth having is that each part arrives as its real shape.

The placement counts in Ver 1.0 were also wrong - 15573 was counted twice - and now sum to 34.

    set PYTHONUTF8=1
    python "D:\\Code Projects\\Silhouette Tools\\tools\\docs\\make_block_import_study.py"
"""
import sys

sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
from makedocx import Doc                                            # noqa: E402

DRAFTS = r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts"

d = Doc()
d.title("Importing a Sangala Blocks Figure into Sangala Studio")

# ---------------------------------------------------------------- the question
d.heading("What Was Asked, and What Was Built")
d.body(
    "Sangala Blocks designs a figure from real LEGO bricks and fabricates nothing; Sangala Studio "
    "designs for fabrication and drives the die cutter and the 3D printer. The proposal examined "
    "here was that a figure designed in Blocks be imported into Studio and adapted there for 3D "
    "printing \u2014 as a printed object rather than as something assembled from bricks. It was "
    "studied, then built, on 20 August 2026."
)
d.body(
    "The proposal does not disturb the division between the three applications. Blocks still drives "
    "no machine and gains no export to one; the file it already writes is opened by the application "
    "that owns the machines. It also closes a loop that was already half built, since Blocks opens "
    "a Studio model file and takes the outline of a figure from it as a frame."
)
d.body(
    "One asymmetry governs everything that follows. Studio's bricks are printable geometry that it "
    "generates. Blocks' bricks are real parts that it specifies and does not generate. Studio "
    "makes; Blocks orders. An import is therefore a translation between two different kinds of "
    "thing, not a transfer of one kind."
)

# ---------------------------------------------------------------- what shipped
d.heading("What the Importer Does")
d.body(
    "Studio's Open accepts a .block file. The change is confined to SangalaStudio.html: no edit to "
    "SangalaServer.cs, no rebuilt executable, and no LDraw parts library shipped beside Studio. "
    "Open reads a local file through the browser's own file interface, so nothing about a new file "
    "type reaches the local bridge at all. This was the cost assumed to make the whole proposal "
    "expensive, and it is not incurred.",
    before_list=True,
)
d.item(
    "The Plan Carries the Profile. ",
    "The figure arrives as it is drawn in Blocks \u2014 in profile \u2014 with its depth on the "
    "extrude axis, where it becomes Depth and Base on each piece. This matters more than it "
    "sounds: a Studio-designed figure is built the same way, so the two routes to one figure now "
    "arrive in the same orientation and can be compared directly. An earlier arrangement put the "
    "figure's height on the extrude axis, which made the workspace a view from above \u2014 a "
    "standing bird seen from overhead is a scatter of overlapping rectangles.",
)
d.item(
    "Each Part Carries Its Measured Profile. ",
    "Not a box, and not an angle read from a part's name. In the profile orientation a slope's ramp "
    "lies in the page, so the part simply is its outline. The outlines are traced once from the "
    "LDraw library that Blocks bundles and pasted into the page as about six kilobytes of numbers; "
    "Studio carries no parts library and traces nothing while it runs. A part the table does not "
    "know arrives as its box rather than as an error, so an unfamiliar design still opens whole.",
)
d.item(
    "Each Named Element Becomes a Plane. ",
    "The decomposition the builder made while building \u2014 Crown, Head, Neck, Back, Body, the "
    "two Wings, Legs \u2014 arrives as Studio's own list of named things: a row per element "
    "carrying its name, a disclosure triangle, show and hide, mirror, and Depth and Base for the "
    "whole element at once. This is the one thing Blocks knows that Studio would otherwise have to "
    "ask a student to invent.",
)
d.item(
    "The Pieces Are Printable Geometry, Never Cut Paths. ",
    "A flag marks a piece as having come from Blocks, and three one-line widenings act on it: the "
    "pieces appear in the Parts list, they are never sent to the die cutter, and they are not drawn "
    "as cut lines. Without it the imported figure was drawn in red, as though it were about to be "
    "cut out of cardstock.",
)

# ------------------------------------------------- what crosses, by part number
d.heading("What Crosses, and What Does Not")
d.body(
    "Measured against the completed crane, a figure of thirty-four placements drawn from seventeen "
    "distinct parts.",
    before_list=True,
)
d.item(
    "Carried Exactly (twenty-eight placements). ",
    "Every brick and plate, every slope, every inverted slope, both round plates and both wedges. "
    "A 45-degree slope ramps over half its length and a 33-degree slope over two of its three "
    "studs, each stopping at the real 1.6 mm lip, because that is what the parts measure. The "
    "inverted slopes rest on one stud and span two, which is the crown geometry settled from a "
    "photograph of the model, and the two crest pieces oppose each other. The wedge that forms each "
    "wing keeps its curve, twelve points of it. The round plates are true circles.",
)
d.item(
    "Carried without Its Connectors (three placements). ",
    "Part 2434 keeps its body and loses the sixteen side studs the wings hang from; part 15573 "
    "loses its centered stud, though its geometric purpose \u2014 putting the neck on the midline "
    "by a half step \u2014 survives intact. Studio places studs on one face of a piece, the one it "
    "extrudes towards, so a second studded face cannot be expressed.",
)
d.item(
    "Carried in Outline Only (one placement). ",
    "The cone keeps its tapering profile and loses its axle hole and collar, neither of which a "
    "printed mass needs.",
)
d.item(
    "Not Carried. ",
    "Studs, on any piece; the hollow underside and anti-stud tubes of a real brick, which a printed "
    "mass should not have; and the curved upper surface of the wedge, which lies across the "
    "extrusion rather than in the page. The wing prints as a plate of the correct shape rather than "
    "a sculpted one.",
)

# ---------------------------------------------------------------- the mapping
d.heading("The Coordinate Mapping")
d.body(
    "The conversion follows the function Blocks uses to build its own three-dimensional view, not "
    "the one it uses to write an LDraw file. The two disagree: the writer measures a part by its "
    "nominal width where the builder measures it across its placed orientation, which is a whole "
    "stud out on a tipped plate, and the two use datums a millimeter apart.",
    before_list=True,
)
d.listing(
    "quarter = (rot | 0) & 1                       a quarter turn swaps across and deep\n"
    "across  = quarter ? d : w        deep2 = quarter ? w : d\n"
    "faced   = (turn === \"face\" || turn === \"back\")      away = (turn === \"back\")\n"
    "depth   = base + half            over  = (shape === \"invslope\") ? 1 : 0\n"
    "\n"
    "x0  = (col - oL) * 8             x1   = (col + across + oR) * 8\n"
    "py0 = row * 3.2                  py1  = py0 + (faced ? deep2 * 8 : h * 3.2)\n"
    "thk = faced ? h * 3.2 : deep2 * 8\n"
    "front = away ? depth * 8 : depth * 8 + thk        rear = front - thk"
)
d.body(
    "A row runs down the page in Blocks and down the page in Studio, so it needs no flip. Depth is "
    "signed about a midline in Blocks, so the hindmost face of the whole figure is put at zero and "
    "every Base measured from it; the offset is common to the figure, so nothing moves relative to "
    "anything else and the back of the bird sits on the plate."
)
d.body(
    "Two facts about the outline table cost a round each and are recorded so they are not "
    "rediscovered. Which plane a part shows depends on how the PART is modeled rather than how it "
    "is placed \u2014 a Slope Brick 45 2 x 1 measures 8 mm across and 16 deep, so its ramp lies in "
    "the z-y plane. Four planes are therefore measured for every part, and the importer chooses by "
    "matching the box it has already computed against the part's measured millimeters, which "
    "settles the part's own orientation and any quarter turn in one test. And a plane that carries "
    "a part's height must not be flipped: LDraw's Y axis and Studio's page both run downward, and "
    "flipping stood every slope on its head."
)

# ---------------------------------------------------------------- scale
d.heading("Size and Scale")
d.body(
    "The complete design spans 128 x 64 x 126.4 mm. Without the 8 x 16 ground plate the figure is "
    "104 x 38.4 x 123.2 mm, or roughly 4.1 x 1.5 x 4.9 inches, which fits the printer bed with room "
    "to spare. The thinnest members are 3.2 mm plates and the legs are 8 mm columns some 30 mm "
    "tall, so nothing is too fine to print."
)
d.body(
    "The import is therefore one to one, and carries no scale control. Studio has no uniform "
    "three-dimensional scale in any case: the scale percentage is read by the placement arithmetic "
    "alone and never by the mesh builder or the exporter. A factor could be applied only inside the "
    "importer's own arithmetic, and any factor other than one would forfeit the parametric joint "
    "bricks, which are fixed to the 8 mm pitch and to a clutch tolerance validated in plastic."
)

# ---------------------------------------------------------- preparing a figure
d.heading("Preparing a Figure in Blocks")
d.body(
    "What the import produces depends on how the design was named, and a few decisions belong to "
    "the designer rather than to the importer.",
    before_list=True,
)
d.item(
    "Naming Is the Boundary. ",
    "A named element becomes a plane, so the same act that decides the masses decides what can be "
    "moved, hidden and extruded as a unit. A part that should stand on its own \u2014 a beak in a "
    "different color from the head \u2014 is named as its own element.",
)
d.item(
    "A Printed Piece Has One Color. ",
    "Where an element uses more than one, the predominant color prevails, measured BY VOLUME rather "
    "than by counting bricks: on the crane, counting ties on both of the two mixed elements and "
    "settles neither. Six of the nine elements are a single color already.",
)
d.item(
    "Some Detail Belongs After Printing. ",
    "The eyes of the crane were added to the printed figure rather than printed into it, and the "
    "wings were real LEGO parts snapped onto a printed body. An element can therefore be left out "
    "of the print deliberately; the printed piece needs studs on the face where such a part "
    "attaches.",
)

# ---------------------------------------------------------------- what remains
d.heading("What Remains")
d.body("In the order it would be built.", before_list=True)
d.step(
    "Studs. Studio places them on the face it extrudes towards, which in this orientation faces the "
    "viewer \u2014 correct for the side-stud brick that a wing snaps onto, and wrong for an upright "
    "brick whose studs point up the figure. The placements record where a part's side studs sit, so "
    "the data to place them correctly is already in the file."
)
d.step(
    "Fusing an element into one printable piece. A plane can be given a Depth and a Base together, "
    "but its pieces remain separate solids; an element that exports as a single piece is what makes "
    "the figure printable in the handful of parts the method calls for.",
    before=60,
)
d.step(
    "Joints. At each vertical joint, a real parametric brick at the validated clutch tolerance with "
    "a matching socket above it; at each wing root, a peg and a slightly larger bore.",
    before=60,
)
d.step(
    "Relief designs. A relief stacks towards the viewer in plates rather than back to front in "
    "studs, so its two screen axes carry different units. The importer refuses one with a message "
    "rather than guessing: untested arithmetic in a finished application is how a design arrives "
    "wrong way out with nothing on screen to show that it did.",
    before=60,
)

# ---------------------------------------------------------------- the cost
d.heading("What It Cost the Finished Application")
d.body(
    "Studio was finished, and its User Guide, its Technical Manual and a chapter of the book all "
    "describe it as it stands, so the distinction between adding and changing matters."
)
d.body(
    "Purely added: the accept string, one dispatch line, the import function, the outline table and "
    "a small color table. Studio's saved state copies an element's attributes wholesale, so saving, "
    "undo, drag-and-drop and the document name all inherit the new type with no code written on the "
    "save side. Changed: three one-line widenings, each adding an alternative without altering an "
    "existing case. Not touched: the local bridge, whose route table contains no file route of any "
    "kind. The executable is neither rebuilt nor recommitted, though it must remain reachable, "
    "because the updater downloads it on any version change and stops the running engine before "
    "swapping \u2014 so a page-only release still requires a tester to close Studio."
)
d.body(
    "The documentation is the remaining cost. The User Guide needs a section on opening a Blocks "
    "figure and the Technical Manual the arithmetic above, since that is what a collaborator would "
    "have to reproduce."
)

# ---------------------------------------------------------------- method
d.heading("How This Was Determined")
d.body(
    "The study that preceded the work read both applications rather than recalling them: five "
    "parallel readings of Studio's object model, its file-opening path, the Blocks data model, the "
    "geometry Blocks holds and Studio's printing machinery; three competing designs for the "
    "handoff; and four adversarial checks, each written to refute rather than to confirm a claim "
    "the designs depended on."
)
d.body(
    "The built importer was then verified against Blocks' own accessors rather than against the "
    "same arithmetic written twice: the same design loaded into both applications, each placement's "
    "box read through the functions Blocks uses to draw it, and eleven placements compared on six "
    "numbers each. All matched. Two apparent mismatches were faults in the test rather than in the "
    "importer, and are recorded as such."
)
d.body(
    "Three of the study's own conclusions did not survive the work and are corrected above rather "
    "than removed: that a slope would have to be rebuilt as a rectangle carrying a roof angle and "
    "would arrive about four degrees shallow; that the wedge's curve could not be carried at all; "
    "and that the importer should deliver about five consolidated masses. The first two were "
    "answered by measuring the parts on the plane the import actually uses. The third was answered "
    "by the author: a student will never print the blocks, and masses assembled from boxes are "
    "still boxes."
)

print(d.save(DRAFTS, "Importing a Blocks Figure into Studio"))
