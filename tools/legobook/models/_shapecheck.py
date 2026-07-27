"""Not a figure - a bench test that draws every piece the engine can make, so a change to
engine.py can be eyeballed in one picture. Underscore-prefixed, so it stays out of --list."""
from engine import brick, slope, decal, cone, ridge, wedge, BH, PH

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
 dict(title="Inverted slopes", text="Top full and flat, the underside falling away - all four ways.",
      parts=[("4 inverted slopes", ("slope", 1, 2, BH, "tan"))],
      pieces=[slope(7, 1, BH*2, 2, 2, BH, "+x", "tan", inv=True),
              slope(10, 1, BH*2, 2, 2, BH, "-x", "brown", inv=True),
              slope(7, 4, BH*2, 2, 2, BH, "+y", "pink", inv=True),
              slope(10, 4, BH*2, 2, 2, BH, "-y", "dark blue", inv=True)]),
 dict(title="Truncated slopes", text="Ramps stopping short, leaving an upright wall - the beak shape.",
      parts=[("truncated", ("slope", 1, 2, BH, "red"))],
      pieces=[slope(1, 6, 0, 2, 2, BH*1.5, "+x", "red", low=BH*0.55),
              slope(4, 6, 0, 2, 2, BH*1.5, "-x", "orange", low=BH*0.55),
              slope(12, 4, 0, 2, 2, BH*1.5, "+y", "blue", low=BH*0.55)]),
 dict(title="Wedges", text="Tilted top and tapering sides at once - the wing shape.",
      parts=[("wedges", ("brick", 2, 2, BH, "white"))],
      pieces=[wedge(1, 12, 0, 4, 3, BH*1.6, "white", low=BH*0.5),
              wedge(7, 12, 0, 4, 3, BH*1.6, "tan", dirn="-x", low=BH*0.5),
              wedge(12, 12, 0, 3, 3, BH*1.6, "blue", low=0.0, inset=0.9)]),
 dict(title="Ridges", text="Sloped both sides: symmetric, asymmetric, and with eaves left standing.",
      parts=[("ridges", ("brick", 2, 2, BH, "gray"))],
      pieces=[ridge(1, 9, 0, 3, 2, BH*1.4, "light gray"),
              ridge(5, 9, 0, 3, 2, BH*1.4, "tan", peak=0.72),
              ridge(9, 9, 0, 3, 2, BH*1.4, "blue", peak=0.35, eaves=BH*0.4),
              ridge(13, 6, 0, 2, 3, BH*1.4, "lime", peak=0.65, axis="y")]),
 dict(title="Round pieces", text="A cone, a steeper cone, a round brick, and a cone with a stud.",
      parts=[("cones", ("brick", 1, 1, BH, "yellow"))],
      pieces=[cone(1, 6, 0, 1, 1, BH, "yellow"),
              cone(3, 6, 0, 1, 1, BH*1.4, "red", top=0.18),
              cone(5, 6, 0, 1, 1, BH, "blue", top=1.0),
              cone(12, 1, 0, 1, 1, BH, "lime", studs=True)]),
 dict(title="Decals and a stack", text="A round tile on each visible face, and a tall stack.",
      parts=[("decals", ("tile", 1, 1, PH, "white"))],
      pieces=[brick(4, 4, 0, 2, 2, BH*2, "dark gray"),
              decal(4, 6, 0, 1.0, 1.2, 0.32, "white"),
              brick(1, 1, PH, 1, 1, BH*4, "black")]),
]
