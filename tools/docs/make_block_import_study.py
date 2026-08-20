"""Builds 'Importing a Sangala Blocks Figure into Sangala Studio' for the _Drafts folder.

The study behind it was a thirteen-agent reading of both applications on 2026-08-20 (run
wf_d37e2843-288): five readers over the two codebases, three competing designs for the handoff,
four adversarial checks against the load-bearing claims, and a synthesis. This script is the
document; the findings are recorded here so the file can be rebuilt rather than retyped.

CORRECTED 2026-08-20 by direct measurement. The study reported that 43712's shape could not be
carried and that the wings would arrive as rectangular slabs. Tracing the part with Blocks'
tools/plan_outline.py at five grid and tolerance settings converges every time on the same SIX
points - the plan outline is a hexagon, not a curve, straight to within about a quarter of a
millimeter over a 48 mm part. What curves on 43712 is its upper surface. The two were conflated.
The placement counts were wrong as well: 15573 was counted both as carried exactly and as carried
without its connectors, so "twelve" was eleven. Counts now sum to the crane's 34.

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
d.heading("The Question")
d.body(
    "Sangala Blocks designs a figure from real LEGO bricks and fabricates nothing; Sangala Studio "
    "designs for fabrication and drives the die cutter and the 3D printer. The proposal examined "
    "here is that a figure designed in Blocks be imported into Studio and adapted there for 3D "
    "printing \u2014 as a printed object rather than as something assembled from bricks."
)
d.body(
    "The proposal does not disturb the division between the three applications. Blocks still drives "
    "no machine and gains no export to one; the file it already writes is opened by the application "
    "that owns the machines. It also closes a loop that is already half built, since Blocks opens a "
    "Studio model file today and takes the outline of a figure from it as a frame."
)
d.body(
    "One asymmetry governs everything that follows. Studio's bricks are printable geometry that it "
    "generates, from seven parametric shapes with a print-validated clutch. Blocks' bricks are real "
    "parts that it specifies and does not generate. Studio makes; Blocks orders. An import is "
    "therefore a translation between two different kinds of thing, not a transfer of one kind."
)

# ---------------------------------------------------------------- the finding
d.heading("The Finding")
d.body(
    "The import is possible, and as a page-only addition to SangalaStudio.html. It requires no edit "
    "to SangalaServer.cs, no rebuilt executable, and no LDraw parts library shipped beside Studio. "
    "Studio's Open reads a local file through the browser's own file interface, so nothing about a "
    "new file type reaches the local bridge at all. This was the cost that had been assumed to make "
    "the whole proposal expensive, and it is not incurred."
)
d.body(
    "The import that works, however, is not the one the proposal implies. Landing thirty-four "
    "separate LEGO parts in Studio and leaving the student to consolidate them fails against three "
    "mechanisms in Studio as it stands: a baked Combine result cannot be mirrored, because the "
    "mirror rewrites the outline and the element geometry and never touches the stored mesh; a "
    "parametric brick can never be a Combine operand; and a baked part keeps only the largest ring "
    "of the union as its plan footprint. The consolidation the method calls for is therefore not "
    "available to a student working on thirty-four imported pieces."
)
d.body(
    "The recommendation is that the importer arrive at the printable masses itself: a Blocks file "
    "opens as roughly five named, grouped, printable masses, with real parametric bricks at the "
    "vertical joints and round pegs at the wing roots. The masses are left as fused groups rather "
    "than baked, so the student re-cuts them with Ungroup and Group, which is where the judgment "
    "the course teaches actually lives."
)

# ------------------------------------------------- what crosses, by part number
d.heading("What Crosses, and What Does Not")
d.body(
    "The findings below were established against the completed crane, a figure of thirty-four "
    "placements drawn from seventeen distinct parts.",
    before_list=True,
)
d.item(
    "Carried Exactly (eleven placements). ",
    "Parts 3001, 3004, 3020, 3021, 3623, 14716, 2453b and 92438. A LEGO brick's body is a "
    "box, and Studio's box generator reproduces it to the millimeter. Nothing is lost but the studs "
    "and the anti-stud tubes, neither of which a printed mass needs. The two tipped wing plates, "
    "the same part turned to the face and to the back, arrive as the correct mirrored pair.",
)
d.item(
    "Carried with Their Real Angle (fifteen placements, forty-four percent of the figure). ",
    "Parts 4286, 3039, 3040 and 3665. These must be built as plain rectangles carrying a per-edge "
    "slope, never as the parametric brick: the brick's own slope is quantized to whole rows, can "
    "face in one direction only, and is excluded from rotation, so the two opposed crest pieces "
    "would come out identical. The roof engine accepts any angle on any edge. One approximation "
    "remains: the fixed vertical lip is 0.6 mm where a real three-plate slope stands vertical for "
    "1.6, so a slope's toe sits about 1 mm low and the 33-degree part arrives at 29.4 degrees. The "
    "top edge, which is what the piece above rests on, is exact.",
)
d.item(
    "Carried in Part (three placements). ",
    "Part 4589 arrives as a truncated cone, losing its axle hole and collar. The two round eyes are "
    "tipped, so their axis is horizontal; imported as bars they are geometrically exact, minus the "
    "stud.",
)
d.item(
    "Carried as Its Measured Outline (two placements). ",
    "Part 43712, the wedge that forms both wings. Its plan outline is a hexagon and not a curve: a "
    "rectangle at the root, then two straight edges tapering to a tip half the width. Traced from "
    "the part's own geometry at five separate grid and tolerance settings, the measurement "
    "converges every time on the same six points, straight to within about a quarter of a "
    "millimeter over a 48 mm part, which is below print resolution. Studio extrudes an arbitrary "
    "polygon, so the wing is not approximated at all — it is the part's real planform. What "
    "curves on 43712 is its upper surface, descending across the span, and that is what does not "
    "cross: the wing prints as a flat plate of the correct shape rather than a sculpted one. Two "
    "per-edge slopes on the tapering sides would recover most of it if it were ever wanted.",
)
d.item(
    "Carried without Its Connectors (three placements). ",
    "Part 2434 keeps its body and loses the sixteen side studs the wings hang from, because Studio "
    "has no stud or socket on a vertical face. That absence is the reason the wing joint has to "
    "become a peg. Part 15573 loses its centered stud, the stud grid having no center position on a "
    "16 mm footprint, but its geometric purpose \u2014 putting the neck on the midline by a half "
    "step \u2014 survives intact.",
)
d.body(
    "Three further things cross without difficulty: a named group arrives as a real Studio group "
    "and keeps its name; every LDraw color code maps to Studio's own fill attribute with no change "
    "to Studio; and the 8 mm lattice transfers by identity, since the stud and plate constants in "
    "the two applications are the same numbers."
)

# ---------------------------------------------------------------- the mapping
d.heading("The Coordinate Mapping")
d.body(
    "The conversion must follow the function Blocks uses to build its own three-dimensional view, "
    "not the one it uses to write an LDraw file. The two disagree: the LDraw writer measures a part "
    "by its nominal width where the viewer measures it across its placed orientation, which is a "
    "whole stud out on the tipped wing plates, and the two use datums 1 mm apart. For a standing "
    "figure, with H the model height in millimeters:",
    before_list=True,
)
d.listing(
    "r      = (rot | 0) & 3;   quarter = r & 1\n"
    "across = quarter ? d : w;   deep2 = quarter ? w : d\n"
    "faced  = (turn === \"face\" || turn === \"back\");   away = (turn === \"back\")\n"
    "half   = (half === true) ? 0.5 : (+half || 0);   depth = base + half\n"
    "over   = (shape === \"invslope\") ? 1 : 0;   oL = flip ? 0 : over;   oR = flip ? over : 0\n"
    "\n"
    "x0  = (col - oL) * 8;            x1 = (col + across + oR) * 8\n"
    "z1  = H - row * 3.2;             z0 = faced ? z1 - deep2 * 8 : H - (row + h) * 3.2\n"
    "thk = faced ? h * 3.2 : deep2 * 8\n"
    "yM  = -depth * 8;   y1 = away ? yM + thk : yM;   y0 = y1 - thk"
)
d.body(
    "Relief mode swaps the units the two screen axes carry, and forces a part upright. Into Studio "
    "the placement becomes a footprint at x0 and y0, offset in y by a whole multiple of 8 mm so the "
    "lattice survives, with the elevation and thickness taken from z0 and z1. The transform is the "
    "identity plus a translation, so the printed solid is congruent with the design rather than "
    "mirrored."
)
d.body(
    "The mapping sidesteps one hazard worth recording. Blocks determines a part's yaw from the "
    "measured bounding box of its LDraw geometry, and for four of the crane's placements the answer "
    "with the parts library loaded differs by ninety degrees from the answer without it. A massing "
    "import is immune, because a box was already sized across its placed orientation. Only a slope's "
    "edge and a wedge's taper need a direction, and those are given by the part's shape, rotation "
    "and flip rather than by the measurement."
)

# ---------------------------------------------------------------- scale
d.heading("Size and Scale")
d.body(
    "The complete design spans 128 x 64 x 126.4 mm. Without the 8 x 16 ground plate the figure "
    "itself is 104 x 38.4 x 123.2 mm, or roughly 4.1 x 1.5 x 4.9 inches. It fits the printer bed "
    "Studio draws in its preview with room to spare. The thinnest members are 3.2 mm plates and the "
    "legs are 8 mm columns some 30 mm tall, so nothing is too fine to print."
)
d.body(
    "One-to-one is therefore both printable and the right default, which is fortunate, because "
    "Studio has no uniform three-dimensional scale: the scale percentage is read by the placement "
    "arithmetic alone and never by the mesh builder or the exporter, and the box resize handles the "
    "two horizontal axes only. A scale factor could be applied only inside the importer's own "
    "arithmetic, and any factor other than one forfeits the parametric joint bricks, which are fixed "
    "to the 8 mm pitch and to the clutch tolerance validated in plastic. The import is therefore one "
    "to one, and carries no scale control."
)

# ---------------------------------------------------------------- build order
d.heading("What Must Be Built, in Order")
d.body("All of it sits in SangalaStudio.html.", before_list=True)
d.step(
    "The mapping alone. Add the new extension to the file dialog's accept list, add one dispatch "
    "line beside the existing branch for a Mosaic file, and add an import function beside the "
    "Mosaic importer that emits every placement as a plain rectangle. About eighty lines. The first "
    "testable milestone is to open the crane file and see the bird standing in three dimensions, "
    "with the crown spanning five studs over the three it rests on. That milestone proves the whole "
    "coordinate mapping, which is the part that can be silently wrong: a sign error in the depth "
    "axis exchanges left for right on a bird with a near and a far wing, and it will ship unless "
    "someone looks."
)
d.step(
    "The shape ladder. Per-edge slopes at their real angles, inverted slopes, cones, circles, and "
    "bars for tipped round parts. About forty lines. The check is that the two crest pieces oppose "
    "each other.",
    before=60,
)
d.step(
    "The outline table. A part whose plan is neither a rectangle nor a slope carries a measured "
    "outline, keyed by part number, as a short list of points normalized to the part's own box. The "
    "outlines are measured once by the tracing script that already exists in Blocks and pasted into "
    "the page as data, so Studio gains no dependency on an LDraw library and nothing is traced at "
    "run time. The wedge is six points; a few dozen parts would be a few hundred numbers. Nothing "
    "is drawn by hand, so both wings are identical, and identical for every student.",
    before=60,
)
d.step(
    "Provenance. A flag marking a piece as having come from Blocks, and three one-line widenings so "
    "that such a piece appears in the Parts panel, never reaches the die cutter, and keeps its flag "
    "through node editing. This step is committed and tested by itself, because two of those "
    "expressions run on every redraw and every panel refresh.",
    before=60,
)
d.step(
    "Joints, which must exist before any consolidation. At each vertical joint the lower mass's top "
    "course is shortened by one brick height over the joint cells and a real parametric brick is "
    "substituted at the validated clutch tolerance, with a matching socket pad above it. At each "
    "wing root, a round peg on the wing and a slightly larger bore grouped with the body, which "
    "Studio's group preview carves live and carries into the exported mesh without baking.",
    before=60,
)
d.step(
    "Consolidation. Parked placements are dropped; a group is treated as an atom; any placement "
    "whose depth interval misses the midline course is bucketed as a limb; the remainder is cut at "
    "any plate plane no placement straddles and whose face contact is two studs or less; and what "
    "is left is partitioned into connected components at a 4 mm tolerance. On the crane this "
    "separates all thirty-four placements into ground, two legs, body with tail and neck, near "
    "wing, far wing, and head with crown. Each mass is grown by a tenth of a millimeter so the "
    "slicer welds it, and is left as a fused group rather than baked \u2014 baking costs the "
    "mirror, the depth and base fields and the plan footprint, and buys nothing the slicer does not "
    "do at slice time.",
    before=60,
)
d.step(
    "The report. One status line naming the pieces produced and naming whatever did not cross "
    "intact — an upper surface flattened, a connector dropped, a placement resting on nothing. "
    "It reports rather than repairs: a part that touches nothing is a fact about the design, and "
    "closing such a gap silently would hide the next one.",
    before=60,
)

# ---------------------------------------------------------------- the cost
d.heading("The Cost to a Finished Application")
d.body(
    "Studio is finished, and its User Guide, its Technical Manual and a chapter of the book all "
    "describe it as it stands. Adding to it is cheap and changing it is not, so the distinction "
    "matters."
)
d.body(
    "Purely added: the accept string, the dispatch line, the import function and a small color "
    "table. Nothing existing changes behavior. Studio's saved state copies an element's attributes "
    "wholesale, so saving, undo, drag-and-drop and the document name all inherit the new type with "
    "no code written on the save side, and the exporter, the mesh builder, the boolean, the brick, "
    "the stud and socket generators, the bar and the roof engine are all used exactly as they "
    "stand. Changed: three one-line widenings, each adding an alternative without altering an "
    "existing case. Not touched at all: the local bridge, whose route table contains no file route "
    "of any kind."
)
d.body(
    "The executable is neither rebuilt nor recommitted, but it must remain committed and reachable, "
    "because the updater downloads it on any version change and stops the running engine before "
    "swapping. A page-only release therefore still requires a tester to close Studio."
)
d.body(
    "The documentation is where the real cost sits. The User Guide needs a short section on opening "
    "a Blocks file, with figures, and a note that the Parts panel now lists pieces originating in a "
    "sibling application. The Technical Manual needs the coordinate arithmetic and the "
    "consolidation rules, since those are what a collaborator would have to reproduce. The book "
    "chapter is the expensive one, and its cost is pedagogical rather than technical: the chapter "
    "teaches block approximation as a judgment the student makes, and an importer that proposes the "
    "five masses moves that judgment to the machine. Either the chapter changes, or the importer "
    "lands the pieces uncut and the student does the cutting."
)

# ---------------------------------------------------------------- open questions
d.heading("The Question That Remains Open")
d.body(
    "One decision belongs to the author rather than to the code, and it changes what is built: "
    "should the importer propose the five masses, or land thirty-four pieces and leave the student "
    "to cut them, given that the chapter currently teaches that cut as the exercise?"
)

# ---------------------------------------------------------------- method
d.heading("How This Was Determined")
d.body(
    "The findings were established by reading both applications rather than by recollection: five "
    "parallel readings of Studio's object model, its file-opening path, the Blocks data model, the "
    "geometry Blocks holds and Studio's printing machinery; three competing designs for the "
    "handoff; and four adversarial checks, each written to refute rather than to confirm a claim "
    "the designs depended on. The check on the wing wedge refuted the claim that Studio's existing "
    "primitives could approximate every part, and that refutation is recorded above rather than "
    "set aside. Every coordinate stated here was reproduced by hand from the saved crane file."
)

print(d.save(DRAFTS, "Importing a Blocks Figure into Studio"))
