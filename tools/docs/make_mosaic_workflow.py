"""Build "Mosaic to Brick Figure Workflow" - the explanation of the student chain
from a 2D LEGO mosaic to a 3D brick figure.

Ver 1.0 (2026-08-21) described the chain as it stood that night and proposed a two-field
Frame scale control. Glen's low-cost test the same evening refuted the premise behind the
proposal - no scale factor makes a frame FIT a build, because a build departs from its
mosaic mass by mass - and the next morning's work replaced it: Blocks now opens a .mosaic
directly, reads a tile as one stud by two plates in the side view, sheds a photograph's
backdrop, and fits the frame by Studio-style resize handles judged against the Transparent
overlay. Ver 1.1 records the chain as it now runs. Facts verified against the shipped
application (Blocks 2026-08-22.178).
"""
import sys
sys.path.insert(0, r"D:\Code Projects\Silhouette Tools\tools")
from makedocx import Doc

d = Doc()
d.title("From a 2D Mosaic to a 3D Brick Figure")

d.heading("Purpose")
d.body("Students design a flat LEGO mosaic and then extrapolate it into a standing brick "
       "figure. The mosaic supplies the silhouette and the color masses; everything the flat "
       "picture cannot say \u2014 depth, layering, and which real parts realize each mass \u2014 "
       "is the student's design work in the third dimension. The imported outline serves as a "
       "guide to build against, not a template to trace, so a ballpark fit is the intent of the "
       "workflow rather than a compromise of it. One principle, settled by test, governs the "
       "fitting: scaling buys proportion, never feature fit. A global factor can size a figure, "
       "but where each mass lands is adjusted by hand, mass by mass. Each student carries their "
       "own animal through the same chain.")

d.heading("The Two Applications in the Chain")
d.body("The chain runs directly from Sangala Mosaic to Sangala Blocks.", before_list=True)
d.item("Sangala Mosaic. ",
       "The figure is designed as flat tiles on the 8 mm grid, and the tiles are grouped into "
       "named masses \u2014 Crown, Head, Wing \u2014 with Select Area or the Wand, then Group. "
       "The design saves as a .mosaic file.")
d.item("Sangala Blocks. ",
       "The Open button reads the .mosaic directly and the mosaic arrives as the frame: each "
       "named mass one element under its name, tiles in no mass kept in their own colors, one "
       "element per patch. Bricks are placed over it \u2014 Snap to Studs lands every part on "
       "the lattice \u2014 and the Parts list becomes the bill of materials for the physical "
       "build.")
d.body("Sangala Studio is no longer a required stop on this route. It remains the door to a "
       "different one: the same .mosaic opened in Studio becomes named masses that can be given "
       "depths and printed as a relief on a 3D printer, and a finished .block opened there "
       "becomes geometry for printing. Studio fabricates; for a figure built of real bricks, "
       "the mosaic goes straight to Blocks.")

d.heading("What the Import Does on the Way In")
d.body("Three rules govern the arrival, and each exists for a measured reason.", before_list=True)
d.item("The Backdrop Stays Behind. ",
       "A mosaic built from a photograph tiles its background like everything else \u2014 a sky "
       "arrives as hundreds of tiles. When every cell of the mosaic's rectangle carries a tile, "
       "which is the signature of a photograph's build, the import removes the field of tiles "
       "reachable from the corners in the corner's own color \u2014 the same rule as Mosaic's "
       "Remove Background button \u2014 and the status line reports how many tiles were left "
       "behind. A sparse mosaic, already cleaned by hand, is not touched.")
d.item("A Tile's Height Follows the View. ",
       "A tile is 8 mm square, but a standing figure is built in plates of 3.2 mm, and 8 mm is "
       "two and a half plates \u2014 so a square tile can never rest both its top and its base "
       "on plate lines, and a brick placed against it must overlap or gap by half a plate. Seen "
       "from the side, a tile therefore imports as one stud wide by two plates tall, and every "
       "edge of the frame lands on a line a brick can land on. This is also what restores the "
       "figure's proportions: carried across square, a figure stands a quarter too tall.")
d.item("The Page Follows the Mosaic. ",
       "The page switches to the 32 x 32 baseplate, the surface a mosaic is built on, and the "
       "mosaic lands at its own plate coordinates \u2014 where a design sits on its plate is "
       "part of the design.")

d.heading("The Workflow, Step by Step")
d.step("In Sangala Mosaic, design the figure and group its tiles into named masses. Save the "
       ".mosaic file. (Remove Background before building from a photograph, or leave it \u2014 "
       "the import will shed a photo-built backdrop itself.)")
d.step("In Sangala Blocks, open the .mosaic. It arrives as the frame, on the baseplate, in its "
       "own colors, with the named masses named.")
d.step("Size the whole frame if it is too large or small for the parts on hand: Frame scale in "
       "Settings is one percentage for the whole figure.")
d.step("Fit the frame mass by mass. Click an element to select it \u2014 or sweep several \u2014 "
       "and drag its handles: a corner keeps proportions, a mid-edge stretches one direction "
       "only. Press Transparent in the menu bar to see placed bricks and frame together, and "
       "recolor an element from the palette when contrast is wanted. Snap to Studs lands a "
       "dragged element on the lattice.")
d.step("Build over the frame: choose a part, place it, and let Snap to Studs settle it. The "
       "frame guides the silhouette; depth from front to back is the student's own extension "
       "of the design.")
d.step("Read the Parts list for the finished figure and save it \u2014 as a list to read, an "
       "order to place, or a kit another builder can open and build from.")

d.heading("What the Test Settled")
d.body("An evening was spent testing whether a scale factor could make the proportion-true "
       "crane frame fit the crane actually built of bricks. It cannot, and the reason is now "
       "measured rather than suspected: the build departs from the mosaic mass by mass, in "
       "both directions \u2014 the built crown is half the frame's height, the built neck a "
       "quarter taller \u2014 because real parts come in their own sizes. No global factor, "
       "one-axis or two, lands every feature at once. The consequence is the division of labor "
       "above: the import supplies correct proportions, Frame scale supplies overall size, and "
       "the per-mass fitting is handle work, judged by eye against the Transparent overlay. An "
       "earlier version of this document proposed a two-field width-and-height scale control; "
       "the test made it moot, and it was not built.")

d.heading("The Crane as the Worked Example")
d.body("The crested crane has traveled the whole chain. Crane 5.mosaic, built from a "
       "photograph, opens in Sangala Blocks shedding its 515-tile sky and keeping its grass; "
       "the figure arrives in sixteen colored elements. The crane built of real bricks stands "
       "13 studs wide and 38 plates tall on its baseplate \u2014 34 parts in 17 kinds \u2014 "
       "and its files, Crane 5.mosaic, Crane.block and Crane.kit in the applications' Projects "
       "folders, are the reference set for demonstrating each leg of the workflow.")

print(d.save(r"C:\Users\glenb\UVa Lab School Dropbox\AI Sandbox\Design through Making\_Drafts",
             "Mosaic to Brick Figure Workflow"))
