"""The grey crowned crane, as a brick figure.

A reconstruction from a photograph of the figure built in the pilot course, not a record of it.
Copy this file to add another animal -- it is all data; the drawing is engine.py's job.

Coordinates are (x, y, z) in studs, z up. The bird faces +x. Heights use BH (one brick, 1.2) and
PH (one plate, 0.4) so every dimension stays a real, buildable stack.
"""
from engine import brick, slope, decal, BH, PH

# The height of each layer, named so a change ripples through instead of being retyped.
Z_LEG   = 0.0
Z_PLATE = BH*3                 # the legs are three bricks tall
Z_C1    = Z_PLATE + PH         # first body course, on the bridging plate
Z_WING  = Z_C1 + BH            # wings slot in BETWEEN the courses...
Z_C2    = Z_WING + PH          # ...so this course pins them and they read as flanks, not a roof
Z_C3    = Z_C2 + BH            # the neck's seat
Z_NECK  = Z_C3 + BH
Z_HEAD  = Z_NECK + BH*5        # five bricks of neck
Z_CROWN = Z_HEAD + BH*2
Z_PRONG = Z_CROWN + PH

TITLE = "How to Build the LEGO Crane"
SUBTITLE = "Eleven steps, from the baseplate upward"
NOTE = ("<b>These steps are a reconstruction, not a record.</b> They were worked out from a photograph "
        "of the finished bird, so the piece sizes are one plausible way to reach that shape rather than "
        "the exact pieces that were used. Substitute freely for whatever is in the bin &mdash; choosing "
        "the substitute is the design work, not a compromise.")
CLOSING = ("When it is standing",
           "Set the finished bird beside the mosaic it came from and compare them: the neck too short, "
           "the body too narrow, the crown too tight. Every difference you can name is the next "
           "revision. Because the bricks come apart as easily as they go together, changing your mind "
           "costs nothing &mdash; which is exactly what makes a prototype worth building.")

# Each entry: (label, (kind, width, depth, height, color)) -- kind is "brick", "slope" or "tile".
INVENTORY = [
    ("1 green baseplate, 12 × 6", ("brick", 4, 2, PH*0.7, "green")),
    ("6 black 1 × 1 bricks",       ("brick", 1, 1, BH, "black")),
    ("5 light gray 1 × 1 bricks",  ("brick", 1, 1, BH, "gray")),
    ("1 white 2 × 6 plate",        ("brick", 2, 3, PH, "white")),
    ("1 white 2 × 6 brick",        ("brick", 2, 3, BH, "white")),
    ("1 white 2 × 4 brick",        ("brick", 2, 2, BH, "white")),
    ("1 white 2 × 2 brick",        ("brick", 2, 2, BH, "white")),
    ("2 white 2 × 1 slopes",       ("slope", 1, 2, BH, "white")),
    ("2 light gray 2 × 4 plates",  ("brick", 4, 2, PH, "light gray")),
    ("2 black 2 × 2 bricks",       ("brick", 2, 2, BH, "black")),
    ("1 white 1 × 1 round tile",   ("tile", 1, 1, PH, "white")),
    ("1 red 2 × 1 slope",          ("slope", 1, 2, BH, "red")),
    ("1 yellow 2 × 2 plate",       ("brick", 2, 2, PH, "yellow")),
    ("5 yellow upright pieces",         ("tile", 1, 1, 1.0, "yellow")),
]

STEPS = [
 dict(title="Start with the baseplate",
      text="Everything stands on one green baseplate. Set it down with the long side facing you "
           "&mdash; the crane will face to the right.",
      parts=[("1 green baseplate, 12 × 6", ("brick", 4, 2, PH*0.7, "green"))],
      pieces=[brick(0, 0, -0.30, 12, 6, 0.30, "green")]),

 dict(title="Stand up the two legs",
      text="Stack three 1 &times; 1 bricks for each leg, two studs apart. Thin legs are the most "
           "fragile part of the whole bird &mdash; press every brick fully home.",
      parts=[("6 black 1 × 1 bricks", ("brick", 1, 1, BH, "black"))],
      pieces=[brick(4, 2, Z_LEG, 1, 1, BH*3, "black"),
              brick(6, 2, Z_LEG, 1, 1, BH*3, "black")]),

 dict(title="Bridge the legs with a plate",
      text="One long plate ties the legs together and becomes the underside of the body. This is the "
           "piece that stops the legs wobbling.",
      parts=[("1 white 2 × 6 plate", ("brick", 2, 3, PH, "white"))],
      pieces=[brick(2, 2, Z_PLATE, 6, 2, PH, "white")]),

 dict(title="Build the body's first course",
      text="One long brick on top of the plate. The body needs real bulk &mdash; a bird built only "
           "of plates reads as a paper cutout standing on edge.",
      parts=[("1 white 2 × 6 brick", ("brick", 2, 3, BH, "white"))],
      pieces=[brick(2, 2, Z_C1, 6, 2, BH, "white")]),

 dict(title="Slot the wings in at the sides",
      text="A plate each side, overlapping the body by one row of studs. They go on now, mid-body, so "
           "the next course pins them down &mdash; that is what makes them read as wings at the bird's "
           "flanks rather than a slab laid over its back.",
      parts=[("2 light gray 2 × 4 plates", ("brick", 4, 2, PH, "light gray"))],
      pieces=[brick(3, 1, Z_WING, 4, 2, PH, "light gray"),
              brick(3, 3, Z_WING, 4, 2, PH, "light gray")]),

 dict(title="Second course, and taper the tail",
      text="The next course pins the wings and steps in at the back, where a slope finishes the tail. "
           "This is where the block starts to read as a bird rather than a box.",
      parts=[("1 white 2 × 4 brick", ("brick", 2, 2, BH, "white")),
             ("1 white 2 × 1 slope", ("slope", 1, 2, BH, "white"))],
      pieces=[brick(4, 2, Z_C2, 4, 2, BH, "white"),
              slope(3, 2, Z_C2, 1, 2, BH, "-x", "white")]),

 dict(title="Close the back and seat the neck",
      text="A 2 &times; 2 brick at the front gives the neck something solid to stand on; one more "
           "slope rounds off the back.",
      parts=[("1 white 2 × 2 brick", ("brick", 2, 2, BH, "white")),
             ("1 white 2 × 1 slope", ("slope", 1, 2, BH, "white"))],
      pieces=[brick(6, 2, Z_C3, 2, 2, BH, "white"),
              slope(5, 2, Z_C3, 1, 2, BH, "-x", "white")]),

 dict(title="Raise the neck",
      text="Five 1 &times; 1 bricks stacked straight up. The neck is the crane's signature &mdash; "
           "and at one brick wide it is also the piece most likely to snap. Pick the finished bird up "
           "by its baseplate, never by the neck.",
      parts=[("5 light gray 1 × 1 bricks", ("brick", 1, 1, BH, "gray"))],
      pieces=[brick(7, 2, Z_NECK, 1, 1, BH*5, "gray")]),

 dict(title="Set the head on top",
      text="Two 2 &times; 2 bricks make the head, overhanging the neck toward the front. A white round "
           "tile on the side is the eye &mdash; one small piece that does more for the bird than any "
           "other.",
      parts=[("2 black 2 × 2 bricks", ("brick", 2, 2, BH, "black")),
             ("1 white 1 × 1 round tile", ("tile", 1, 1, PH, "white"))],
      pieces=[brick(7, 2, Z_HEAD, 2, 2, BH*2, "black"),
              decal(7, 4, Z_HEAD, 1.35, 1.45, 0.30, "white")]),

 dict(title="Point the beak forward",
      text="One red slope at the front of the head is the beak. The mosaic could only spell this out "
           "as a few red tiles; in brick it becomes a single wedge &mdash; a shape the 8 mm grid could "
           "never hold.",
      parts=[("1 red 2 × 1 slope", ("slope", 1, 2, BH, "red"))],
      pieces=[slope(9, 2, Z_HEAD + BH*0.5, 1, 2, BH, "+x", "red")]),

 dict(title="Finish with the golden crown",
      text="A yellow plate across the head carries the crown. Stand short pieces upright in a fan, "
           "tallest in the middle &mdash; this is the detail that names the bird, so spread them wide.",
      parts=[("1 yellow 2 × 2 plate", ("brick", 2, 2, PH, "yellow")),
             ("5 yellow upright pieces", ("tile", 1, 1, 1.0, "yellow"))],
      pieces=[brick(7, 2, Z_CROWN, 2, 2, PH, "yellow")]
             + [brick(7.12 + i*0.40, 2.55 + 0.12*abs(i-2), Z_PRONG, 0.36, 0.36,
                      [0.75, 1.05, 1.25, 1.05, 0.75][i], "yellow", studs=False)
                for i in range(5)]),
]

# The parts table printed above the steps in the Word version.
TABLE = ("Table 1. Every piece used, gathered by the part it builds.",
         ["Part", "Color", "Pieces"],
         [("Baseplate", "Green", "1 baseplate, 12 × 6"),
          ("Legs", "Black", "6 bricks, 1 × 1"),
          ("Body", "White", "1 plate 2 × 6; 1 brick 2 × 6; 1 brick 2 × 4;\n"
                            "1 brick 2 × 2; 2 slopes 2 × 1"),
          ("Wings", "Light Gray", "2 plates, 2 × 4"),
          ("Neck", "Light Gray", "5 bricks, 1 × 1"),
          ("Head", "Black", "2 bricks, 2 × 2"),
          ("Eye", "White", "1 round tile, 1 × 1"),
          ("Beak", "Red", "1 slope, 2 × 1"),
          ("Crown", "Yellow", "1 plate 2 × 2; 5 upright pieces")],
         [1500, 1700, 6160])
