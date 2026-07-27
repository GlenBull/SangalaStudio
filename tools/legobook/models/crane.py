"""The grey crowned crane, as a brick figure.

Rebuilt 2026-07-27 from Glen's part-by-part reading of a photograph of the figure built in the pilot
course. Sixteen corrections to the first attempt, which had been guessed from the same photograph at
a glance: the crown was a tuft rather than a fan, the head two bricks rather than a brick and a
plate, the body a box with a post on it rather than a clothed core, and the baseplate was shrunk to
flatter the proportions.

Two rules this file follows, both learned the hard way:

  ONE Piece PER REAL LEGO PIECE. Never merge a stack into a single box. The first version drew the
  neck as one tall box while its parts list claimed five bricks, and nothing could catch the
  disagreement because a stack and a column render identically unless the seams are drawn.

  ANYTHING SYMMETRIC IS WRITTEN ONCE. The wings are a function of their y, called twice. Two
  hand-typed coordinate sets can drift apart by a typo and still look nearly right.

Coordinates are (x, y, z) in studs, z up. The bird faces +x. Heights use BH (a brick) and PH (a
plate), so every dimension is a real stack.
"""
from engine import brick, slope, decal, cone, ridge, wedge, blade, BH, PH

# ---- the layers, named so a change ripples instead of being retyped ----
Z_LEG_A = 0.0                   # the short piece each leg stands on
Z_LEG_B = Z_LEG_A + PH          # the long column
Z_LEG_C = Z_LEG_B + BH*2        # the short piece that meets the body
Z_CORE1 = Z_LEG_C + PH          # rectangular core, first course
Z_CORE2 = Z_CORE1 + BH          # second course -- the wings flank THIS one and hide it
Z_TOP   = Z_CORE2 + BH          # the course the shaped top rests on
Z_SHAPE = Z_TOP + BH            # shaped pieces resting on that course
Z_NECK  = Z_SHAPE + BH          # the neck's cantilevered seat
Z_COL   = Z_NECK + BH           # the long column
Z_HEAD  = Z_COL + BH*4
Z_CAP   = Z_HEAD + BH           # the plate over head and beak
Z_CROWN = Z_CAP + PH

TITLE = "How to Build the LEGO Crane"
SUBTITLE = "Twelve steps, from the baseplate upward"
NOTE = ("<b>These steps are a reconstruction, not a record.</b> They were read off photographs of the "
        "finished bird, so the piece sizes are one plausible way to reach that shape rather than the "
        "exact pieces that were used. Two places are reasoned rather than seen, and say so where they "
        "come up: the rectangular bricks inside the body, which the wings hide, and the legs, which "
        "are hard to photograph in black. Substitute freely for whatever is in the bin &mdash; "
        "choosing the substitute is the design work, not a compromise.")
CLOSING = ("When it is standing",
           "Set the finished bird beside the mosaic it came from and compare them: the neck too "
           "short, the body too narrow, the crown too tight. Every difference you can name is the "
           "next revision. Because the bricks come apart as easily as they go together, changing "
           "your mind costs nothing &mdash; which is exactly what makes a prototype worth building.")


def leg(x):
    """One leg: a short piece to stand on, a long one to span, a short one to meet the body.
    The long piece does the reaching and the short ones do the joining -- the same habit the neck
    follows, and the joints are where the strength is."""
    return [brick(x, 3, Z_LEG_A, 1, 1, PH, "black"),
            brick(x, 3, Z_LEG_B, 1, 1, BH*2, "black"),
            brick(x, 3, Z_LEG_C, 1, 1, PH, "black")]


def wing(y0):
    """One wing, occupying y0..y0+2. Called twice; the far wing is this one mirrored, and every
    piece here is symmetric across the bird's centreline, so mirroring is only a change of y."""
    return [wedge(4, y0, Z_CORE2, 4, 2, BH, "white", dirn="-x", low=0.0, inset=0.62),
            blade(8, y0, Z_CORE2, 1, 2, BH, "light gray"),
            blade(9, y0, Z_CORE2, 2, 2, BH, "white")]


STEPS = [
 dict(title="Start with the baseplate",
      text="One green baseplate, 16 &times; 8. Set it down with the long side facing you &mdash; the "
           "crane will face to the right, and will very nearly fill it.",
      parts=[("1 green baseplate, 16 × 8", ("brick", 4, 2, PH*0.7, "green"))],
      pieces=[brick(0, 0, -0.30, 16, 8, 0.30, "green")]),

 dict(title="Stand up the two legs",
      text="Three pieces each: a short one on the baseplate, a long one for the span, a short one on "
           "top. The long piece reaches and the short ones join, which is where the strength is. "
           "<i>Least certain step in the sheet &mdash; black photographs badly, and this is read from "
           "a dark picture.</i>",
      parts=[("2 black 1 × 1 plates (feet)", ("brick", 1, 1, PH, "black")),
             ("2 black 1 × 1 columns", ("brick", 1, 1, BH*2, "black")),
             ("2 black 1 × 1 plates (tops)", ("brick", 1, 1, PH, "black"))],
      pieces=leg(6) + leg(8)),

 dict(title="Lay the body's rectangular core",
      text="Two plain courses of rectangular brick. Almost none of this will show once the wings go "
           "on &mdash; it is the thing everything else mounts to. <i>Inferred: the wings hide these "
           "bricks in every photograph, but a strip of the body's top edge is visible above the "
           "wing, so their size is read from the outline rather than guessed.</i>",
      parts=[("1 white 2 × 9 brick", ("brick", 2, 3, BH, "white")),
             ("1 white 2 × 7 brick", ("brick", 2, 3, BH, "white"))],
      pieces=[brick(2, 3, Z_CORE1, 9, 2, BH, "white"),
              brick(4, 3, Z_CORE2, 7, 2, BH, "white")]),

 dict(title="Mount the wings on the core",
      text="Three pieces a side, flanking the core at the same height so they hide it. The back is a "
           "wedge &mdash; tilted on top and drawn in at the sides at once &mdash; and the two pieces "
           "in front of it thin toward the leading edge because their tops and undersides both slope "
           "away. Three pieces carry nearly all of the bird's curve.",
      parts=[("2 white wedges", ("brick", 3, 2, BH, "white")),
             ("2 light gray 1 × 2 blades", ("brick", 1, 2, BH, "light gray")),
             ("2 white 2 × 2 blades", ("brick", 2, 2, BH, "white"))],
      pieces=wing(5) + wing(1)),

 dict(title="Taper the tail",
      text="Two slopes stacked at the very back, so the tail draws down across two courses and comes "
           "to a fine point rather than a chopped corner. The lower one is black &mdash; expedience, "
           "not design: it is what the bin had.",
      parts=[("1 black 2 × 1 slope", ("slope", 1, 2, BH, "black")),
             ("1 light gray 2 × 1 slope", ("slope", 1, 2, BH, "light gray"))],
      pieces=[slope(2, 3, Z_CORE2, 2, 2, BH, "-x", "black"),
              slope(2, 3, Z_TOP, 2, 2, BH, "-x", "light gray")]),

 dict(title="Close the top of the body",
      text="A white brick behind and a gray one in front of it. Neither is shaped: they are the "
           "course the shaped pieces sit on. Block the mass out square first, then clothe it &mdash; "
           "that way the bird is a bird at every stage.",
      parts=[("1 white 2 × 2 brick", ("brick", 2, 2, BH, "white")),
             ("1 light gray 2 × 3 brick", ("brick", 3, 2, BH, "light gray"))],
      pieces=[brick(4, 3, Z_TOP, 2, 2, BH, "white"),
              brick(6, 3, Z_TOP, 3, 2, BH, "light gray")]),

 dict(title="Cap the back with a ridged plate",
      text="A thin gray plate sloped on top on <i>both</i> sides, like the roof of a house &mdash; "
           "but asymmetrical, the left face longer than the right. One odd piece does more for the "
           "back than three ordinary ones would.",
      parts=[("1 light gray ridged plate", ("brick", 2, 2, PH, "light gray"))],
      pieces=[ridge(4, 3, Z_SHAPE, 2, 2, PH*1.6, "light gray", peak=0.66)]),

 dict(title="Raise the shoulder toward the neck",
      text="Two slopes resting on the gray brick, stepping the body's line up to meet the neck. One "
           "gray, one white &mdash; again what the bin allowed, and it does the bird no harm.",
      parts=[("1 light gray 2 × 2 slope", ("slope", 2, 2, BH, "light gray")),
             ("1 white 2 × 2 slope", ("slope", 2, 2, BH, "white"))],
      pieces=[slope(6, 3, Z_SHAPE, 2, 2, BH, "-x", "light gray"),
              slope(8, 3, Z_SHAPE, 2, 2, BH, "-x", "white")]),

 dict(title="Cantilever a seat, then raise the neck",
      text="A brick reaching forward past the breast makes a landing for the neck, so the throat "
           "stands <i>in front of</i> the chest the way a crane's does. Then one long column, not a "
           "stack: the same long-piece-spans, short-piece-joins habit as the legs.",
      parts=[("1 light gray 1 × 2 brick (seat)", ("brick", 2, 1, BH, "light gray")),
             ("1 light gray 1 × 1 × 4 column", ("brick", 1, 1, BH*4, "gray"))],
      pieces=[brick(10, 3, Z_NECK, 2, 1, BH, "light gray"),
              brick(11, 3, Z_COL, 1, 1, BH*4, "gray")]),

 dict(title="Set the head on the column",
      text="One brick &mdash; not two. A white round tile on its side is the eye, and it does more "
           "for the bird than any other single piece.",
      parts=[("1 black 2 × 2 brick", ("brick", 2, 2, BH, "black")),
             ("1 white 1 × 1 round tile", ("tile", 1, 1, PH, "white"))],
      pieces=[brick(11, 3, Z_HEAD, 2, 2, BH, "black"),
              decal(11, 5, Z_HEAD, 1.35, 0.62, 0.28, "white")]),

 dict(title="Add the beak, then pin it with a plate",
      text="The beak is a slope that stops short of a point, leaving a small upright wall at its "
           "tip. A thin plate then runs across the head and forward <i>onto</i> the beak, capping "
           "the head and trapping the beak at once &mdash; which is what holds a wedge that size on. "
           "A beak that did come to a point would have served just as well; none was in the bin. "
           "Printing one is a different matter.",
      parts=[("1 red 2 × 2 slope", ("slope", 2, 2, BH, "red")),
             ("1 black 2 × 3 plate", ("brick", 3, 2, PH, "black"))],
      pieces=[slope(13, 3, Z_HEAD, 2, 2, BH, "+x", "red", low=BH*0.35),
              brick(11, 3, Z_CAP, 3, 2, PH, "black")]),

 dict(title="Finish with the golden crown",
      text="Three pieces, and they splay <i>sideways</i> rather than standing up in a tuft: an "
           "inverted slope flaring each way &mdash; top full and flat, underside swept away &mdash; "
           "with a cone between them. A wide golden fan is what names the bird from across a room.",
      parts=[("2 yellow inverted slopes", ("slope", 1, 2, PH*1.5, "yellow")),
             ("1 yellow cone", ("brick", 1, 1, BH, "yellow"))],
      pieces=[slope(10.1, 3.2, Z_CROWN, 1.4, 1.6, PH*1.6, "-x", "yellow", inv=True),
              cone(11.5, 3.4, Z_CROWN, 1.0, 1.2, BH*0.8, "yellow"),
              slope(12.5, 3.2, Z_CROWN, 1.4, 1.6, PH*1.6, "+x", "yellow", inv=True)]),
]

TABLE = ("Table 1. Every piece used, gathered by the part it builds.",
         ["Part", "Color", "Pieces"],
         [("Baseplate", "Green", "1 baseplate, 16 × 8"),
          ("Legs", "Black", "2 plates 1 × 1; 2 columns 1 × 1 × 2;\n2 plates 1 × 1"),
          ("Body core", "White", "1 brick 2 × 9; 1 brick 2 × 7"),
          ("Wings", "White, Light Gray", "2 wedges; 2 blades 1 × 2;\n2 blades 2 × 2"),
          ("Tail", "Black, Light Gray", "2 slopes, 2 × 1"),
          ("Body top", "White, Light Gray", "1 brick 2 × 2; 1 brick 2 × 3;\n"
                                            "1 ridged plate; 2 slopes 2 × 2"),
          ("Neck", "Light Gray", "1 brick 1 × 2 (seat);\n1 column 1 × 1 × 4"),
          ("Head", "Black", "1 brick 2 × 2; 1 plate 2 × 3"),
          ("Eye", "White", "1 round tile, 1 × 1"),
          ("Beak", "Red", "1 slope, 2 × 2"),
          ("Crown", "Yellow", "2 inverted slopes; 1 cone")],
         [1500, 2100, 5760])

INVENTORY = [(lab, spec) for s in STEPS for lab, spec in s["parts"]]
