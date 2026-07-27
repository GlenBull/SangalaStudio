"""Not a figure - a bench test that draws every piece the engine can make, so a change to
engine.py can be eyeballed in one picture. Underscore-prefixed, so it stays out of --list."""
from engine import brick, slope, decal, BH, PH

TITLE = "Shape check"
SUBTITLE = "every primitive, once"
NOTE = ""
INVENTORY = [("test", ("brick", 2, 2, BH, "red"))]

STEPS = [
 dict(title="Ground and boxes", text="A plate, a brick, a smooth-topped tile.",
      parts=[("assorted", ("brick", 2, 2, BH, "light gray"))],
      pieces=[brick(0, 0, -0.3, 14, 8, 0.3, "green"),
              brick(1, 1, 0, 2, 2, PH, "white"),
              brick(1, 4, 0, 2, 2, BH, "blue"),
              brick(4, 1, 0, 2, 2, BH, "red", studs=False)]),
 dict(title="All four slope directions", text="Falling toward +x, -x, +y and -y in turn.",
      parts=[("4 slopes", ("slope", 1, 2, BH, "yellow"))],
      pieces=[slope(7, 1, 0, 2, 2, BH, "+x", "yellow"),
              slope(10, 1, 0, 2, 2, BH, "-x", "orange"),
              slope(7, 4, 0, 2, 2, BH, "+y", "lime"),
              slope(10, 4, 0, 2, 2, BH, "-y", "purple")]),
 dict(title="Decals and a stack", text="A round tile on each visible face, and a tall stack.",
      parts=[("decals", ("tile", 1, 1, PH, "white"))],
      pieces=[brick(4, 4, 0, 2, 2, BH*2, "dark gray"),
              decal(4, 6, 0, 1.0, 1.2, 0.32, "white"),
              brick(1, 1, PH, 1, 1, BH*4, "black")]),
]
