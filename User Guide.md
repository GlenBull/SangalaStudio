# Sangala Studio — User Guide (Chapters 1–3)

**Sangala Studio** is the *Digital Fabrication Tool* you use to design a shape on
screen and then make it on the Silhouette **die cutter** — print it, cut its
outline, and crease its fold lines. This guide covers the 2D features you need for
Chapters 1–3: importing and tracing a photo, drawing and combining shapes, and
doing a print‑and‑cut. (3D features are introduced later and are not covered here.)

---

## 1. The big picture

Everything you make follows the same path:

**Design on the mat → choose which lines cut and which fold → (optionally) print →
Make it!**

The die cutter cannot tell a fold from a cut by itself, so *you* tell Sangala which
is which. That is the single most important idea in this guide — see Section 3.

---

## 2. The screen

- **Top toolbar** — file and machine actions: Connect, Open, Save SVG, Marks,
  Print, Test, Setup. The green **Make it!** button (right panel) sends your design
  to the die cutter.
- **Tools palette** (left edge) — the drawing and editing tools: Select, Pen,
  Nodes, Shapes, Combine, Align.
- **The mat** (center) — your working page. The label at the top tells you the mat
  size (about 8 × 12 inches).
- **Fabricate panel** (right) — the **Make it!** button, status messages, and — when
  a shape is selected — the **Selected object** panel for changing or measuring it.

**Connect first.** Click **Connect** to link to the die cutter over USB. Until it
connects, the status reads "Not connected" and **Make it!** stays disabled. You can
design at any time; you only need to connect to make something.

---

## 3. Cut lines vs. fold lines (read this)

Every line in your design is one of three kinds. You set the kind by selecting the
shape and clicking a button in the **Selected object** panel:

- **✂️ Cut** — the blade cuts all the way through. Drawn as a solid red line.
- **⁝ Score / Fold** — a crease the paper folds along. The die cutter perforates it
  lightly (a dashed line at reduced force) so it folds cleanly without cutting off.
  Drawn as a dashed red line.
- **🖨️ Print only** — printed but never cut or creased (for artwork, windows, labels).

If a line that should fold is left as a **Cut**, the die cutter will slice right
through it and your model will fall apart. When in doubt, select the line and check
which button is highlighted.

---

## 4. The Tools palette

Click a tool to turn it on; click it again (or click **Select**) to turn it off.
Some tools open a small pop‑out menu of choices.

### Select
The arrow. Click a shape to pick it, drag it to move, drag a corner handle to
resize. This is the "normal" mode you return to between other tools.

### Pen
Draw a free‑form outline point by point. Click on the mat to drop each corner; a red
preview line follows your cursor. To finish, click the first point again, press
**Enter**, or double‑click — the outline closes into an editable cut shape. Press
**Esc** to cancel. Use the Pen for custom silhouettes, frames, and profiles that
aren't a plain rectangle or circle. (After you finish, you can fine‑tune it with the
Nodes tool.)

### Nodes
Edit the individual points of a shape. With a shape selected, drag a point to move
it, click on a line segment to add a point, or select a point and press **Delete** to
remove it. Great for reshaping a traced silhouette or pulling up a mountain peak.

### Shapes
Opens a menu to draw a **Rectangle** or a **Circle**. Pick one, then drag on the mat —
rectangle corner‑to‑corner, circle center‑outward. After drawing, adjust the exact
size in the **Selected object** panel.

### Combine
Opens a menu to merge two shapes. Click one shape, then **Shift + click** a second
(it turns orange), then choose:

- **Union** — join both into one outline.
- **Difference** — cut the second (orange) shape out of the first.
- **Intersect** — keep only the part where the two overlap.

**Combine with a photo:** click a shape, **Shift + click** the imported photo, then
**Intersect** to crop the photo to that shape — everything outside the shape is
removed. This is how you make a round (or any‑shaped) photo cut‑out for a collage
(see Section 6).

### Align
Opens a menu to line up two or more objects. Select them (drag a box around them, or
click one and **Shift + click** another), then choose:

- **↕ Vertical** — line them up on a vertical axis (same left‑right center).
- **↔ Horizontal** — line them up on a horizontal axis (same up‑down center).
- **✛ Center (both)** — center them on each other.

The largest object stays put and the others move to it — so **Center** drops a small
circle exactly into the middle of a larger square (or onto the center of a photo).

---

## 5. Working with a selected shape

Select any shape to open the **Selected object** panel on the right:

- **✂️ Cut / ⁝ Score‑Fold / 🖨️ Print only** — set what the line does (Section 3). The
  highlighted button is the current setting.
- **Dimensions** — the size and position are shown in a small box and are editable:
  click a number and type, or use the up/down spinner, to set an exact value.
- **〰️ Simplify nodes** — for hand‑drawn or traced shapes with many points, this
  reduces the point count while keeping the same outline (each press simplifies a
  little more). A tidier shape cuts more smoothly.
- **🗑 Delete** — remove the shape (or press the **Delete** key).

**Selecting several at once:** drag a box across empty mat to rubber‑band multiple
shapes. You can then move them together, delete them, or change them all to
Cut/Score/Print at once.

---

## 6. Chapter 1 — turn a photo into a cut‑out

Sangala can lift a subject out of a photograph and make a printed cut‑out of it — no
other software needed.

1. **Open** the photo (**Open** accepts .png and .jpg). It appears on the mat as a
   faint reference layer. It will not cut, print, or save on its own — it is only
   there to work from.
2. Click **Remove BG**. Sangala finds the subject and draws a red boundary around it,
   right on top of the photo.
3. Tune the boundary with the two sliders that appear in the Fabricate panel:
   - **Silhouette threshold** — tighter or looser edge.
   - **Ignore specks** — drops tiny stray bits so only the main subject is outlined.
4. When the boundary looks right, click **Confirm**. Sangala removes the background
   (leaving the subject on white) and builds a **print‑and‑cut**: it will print the
   subject and cut around the outline. Registration marks turn on automatically.
5. **Print** the page, load it on the mat, and press **Make it!** (see Section 8).
   The die cutter reads the marks and cuts exactly around your printed subject.

**Crop a photo to a shape instead.** If you want a photo inside a circle (or any
outline) for a collage: **Open** the photo, draw a shape over the part you want with
**Shapes** or **Pen**, then use **Combine → Intersect** (Section 4). Everything
outside the shape is removed and you get a print‑and‑cut of the cropped photo. Use
**Align → Center** first if you want the shape centered on the photo.

---

## 7. Zoom & pan (looking closely)

To check fine detail:

- **Zoom** — mouse wheel, or the **+ / −** buttons at the bottom of the mat.
- **Fit** — the **Fit** button returns to the whole page.
- **Pan** (when zoomed in) — hold the **Space** bar and drag, or drag with the middle
  mouse button.

Zoom is only for looking; it does not change the size of your design. To resize the
design, use the shape's dimensions (Section 5) or **Scale %** in Setup.

---

## 8. Printing, registration marks, and Make it!

**Marks** (the ⌖ button) is a toggle that decides how **Make it!** behaves:

- **Marks OFF** — **Make it!** does a plain cut: the die cutter cuts (and creases)
  your lines directly. Use this when there is nothing printed to line up with.
- **Marks ON** — this is **print‑and‑cut**. **Print** lays down your artwork *plus*
  three registration marks. Load the printed page on the mat, then **Make it!** — the
  die cutter finds the marks and cuts precisely on top of the print. This is what the
  photo cut‑out and collage workflows use, and Marks turns on for you when you Confirm
  a background removal or a crop.

So the print‑and‑cut sequence is: **Marks on → Print → load the printed sheet →
Make it!**

---

## 9. Setup (materials and settings)

Click **Setup** to set how the die cutter behaves. Close it and press **Make it!**
when you're ready.

- **Material** — pick Paper, Cardstock, Heavy cardstock, Vinyl, or Pen (draw). This
  sets sensible Force / Speed / Blade / Passes for you; adjust below if needed.
- **Force / Speed / Blade / Passes** — pressure, how fast it moves, blade depth, and
  how many times it traces each cut. Thick material needs more force and more passes,
  not just a deeper blade.
- **Scale %** — enlarge or shrink the whole design (100% = as drawn).
- **Units** — inches or millimeters for the readouts.
- **Position (From left / From top)** — where the design sits on the mat.

**Tip:** for heavy cardstock, more passes beats brute force — try the Heavy cardstock
preset and add a pass before turning the force up.

---

## 10. Saving

**Save SVG** writes your design to a file you can reopen later or share. The imported
reference photo is not part of the saved design — only the shapes you made are saved.

---

## 11. Quick reference

| I want to… | Do this |
|---|---|
| Move / resize a shape | **Select**, drag the body or a corner handle |
| Draw a box or circle | **Shapes → Rectangle / Circle**, drag on the mat |
| Draw a free‑form outline | **Pen**, click each point, Enter to finish |
| Reshape an outline | **Nodes**, drag / add / delete points |
| Make a line fold instead of cut | Select it, click **⁝ Score / Fold** |
| Merge / subtract / overlap two shapes | **Combine → Union / Difference / Intersect** |
| Center one shape in another | Select both, **Align → Center** |
| Cut a subject out of a photo | **Open** photo → **Remove BG** → **Confirm** |
| Crop a photo to a circle/shape | Draw the shape, **Combine → Intersect** |
| Print and cut on the print | **Marks on → Print → Make it!** |
| Look at fine detail | Mouse wheel to zoom, **Fit** to reset |

---

## 12. Which tools for which chapter

- **Chapter 1 (silhouettes / collage):** Open a photo, **Remove BG**, tune the
  boundary, **Confirm**, print‑and‑cut. Crop photos to shapes with **Combine →
  Intersect**. Reshape traced outlines with **Nodes**.
- **Chapter 2 (profiles / mountains):** Draw a base with **Shapes** or **Pen**, then
  use **Nodes** to add and pull points into the profile you want.
- **Chapter 3 (frames / shadowbox):** Build openings with **Combine** (Difference and
  Intersect), **Align → Center** a window in a frame, and set the fold lines to
  **Score / Fold** so the die cutter creases them instead of cutting through.
