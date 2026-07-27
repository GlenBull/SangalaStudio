# legobook — LEGO-kit instruction booklets

Generates step-by-step build instructions in the style of a LEGO kit: numbered steps, an isometric
drawing of the assembly at each one, new pieces in full color against the earlier ones in pale, and a
parts callout beside every step.

Every illustration is rendered from **one 3D model of the finished figure**, drawn cumulatively. That
is the point of the tool: the pictures cannot drift out of step with each other or with the parts
list, because they are all the same model at different depths.

Built for Chapter 5 of *Design through Making*, where a student's mosaic becomes a figure in bricks.

```
python build.py --list                 the models available
python build.py crane                  writes the HTML booklet beside this script
python build.py crane --docx           also a Word document (needs Microsoft Edge)
python build.py crane --out "..\..\Documents"
```

The HTML is self-contained — one file, no assets, prints from any browser. The Word path needs Edge
only to turn the drawings into images; nothing else is installed. Generated output is gitignored;
rename it with a version number (`How to Build the LEGO Crane (Ver 1.0).docx`) when you publish it
into `Documents\`.

## Adding an animal

Copy `models/crane.py`, rename it, and change the data. Nothing in `engine.py` needs to be touched.
A model file provides:

| Name | What it is |
|---|---|
| `TITLE`, `SUBTITLE` | shown at the top |
| `NOTE` | the caveat box (optional) |
| `INVENTORY` | the "pieces you will need" list |
| `STEPS` | the steps: `title`, `text`, `parts`, `pieces` |
| `CLOSING` | `(heading, text)` after the last step (optional) |
| `TABLE` | the parts table in the Word version (optional) |

Coordinates are `(x, y, z)` in studs, `z` up, the figure facing `+x`. Use `BH` (a brick, 1.2) and
`PH` (a plate, 0.4) for heights so every dimension stays a real stack — three plates make a brick
exactly, as in real LEGO. Note that a brick is **not** a cube: the stud pitch is 8 mm but a brick
stands 9.6 mm, so one brick of height is a little more than one stud of width.

Three pieces are available:

```python
brick(x, y, z, w, d, h, color)               # a box with studs; studs=False for a smooth top
slope(x, y, z, w, d, h, "+x", color)         # ramps down toward +x / -x / +y / -y
decal(x, y, z, along, up, r, color)          # a round tile on a vertical face (an eye, a spot)
```

Colors are LEGO names from `engine.COLORS` (`"dark gray"`, `"red"`, …) or any `#rrggbb`.

Order the steps from the baseplate upward, the way the figure is actually built. Put a piece in the
step where a builder would reach for it — the drawing follows automatically.

## Checking the engine

`models/_shapecheck.py` is not a figure — it draws every primitive once (all four slope directions,
a decal, a smooth-topped tile, a tall stack behind a nearer block) so a change to `engine.py` can be
eyeballed in a single picture. It is underscore-prefixed, so it stays out of `--list`:

```
python -c "import sys;sys.path[:0]=['.','models'];import engine,importlib as i;m=i.import_module('_shapecheck');engine.Book(m.TITLE,m.SUBTITLE,m.NOTE,m.INVENTORY,m.STEPS).rasterize('_images_check')"
```

## Two things learned the hard way

**Draw order is decided pairwise, not by a sort key.** `draw_order` compares each pair of pieces that
overlap on screen and asks whether one is wholly on the viewer's side of the other, then
topologically sorts the result. A single number cannot do this: an early version keyed on each
piece's center, which put the wide baseplate *after* one of the legs and painted the leg out of the
picture entirely. If a figure ever draws in the wrong order, that function is where to look.

**Where a piece goes in the sequence changes what it reads as.** The crane's wings were first placed
on top of the last body course and looked like a roof slab laid over the bird's back. Moving them one
step earlier — so the next course pins their inner studs — made them read as wings at the flanks. Same
pieces, same position; only the order changed.

## Limits worth knowing

- The camera is fixed at one isometric angle. There is no way to show the back of a figure, or to spin
  it. A part hidden behind another in this view is hidden in every step.
- The piece vocabulary is boxes, slopes, and round decals. No cylinders, wedge plates, arches, or
  pieces rotated off the grid. Each would be a self-contained addition to `engine.py`.
- A model is written by hand. Deriving one from a Sangala relief would give the parts, their
  footprints, and their depths — enough for a booklet with one step per *part*. Which actual bricks
  fill each part is the student's design work, and Chapter 5 is deliberate about leaving it to them.
