# Sangala Studio — no-admin Digital Fabrication tool

Browser-based design and control for Silhouette **Portrait 3/4** and **Cameo**
die cutters over USB, with **no admin rights, no driver install, no Bluetooth,
no extra hardware — USB only, user-mode.** Built for schools, where that
constraint is absolute.

Sangala Studio is now two things in one page: a **design tool** and a **die
cutter driver**. You can draw and arrange 2D shapes, build 3D solids from them
(bars, sloped roofs, cones, boolean combines, holes), trace a reference photo,
then export the result as an SVG for the die cutter, an STL for a 3D printer, or
run a registered print-and-cut on the machine directly. It also emits a block
library for **Snap!** / TurtleStitch.

## What it does

- **Print-and-cut, registered.** Prints Silhouette-standard registration marks,
  scans them with the machine's optical eye, and cuts outlines plus creased
  fold/score lines aligned to your inkjet print — all in user mode over USB.
- **2D design.** Draw and move shapes (the whole interior of a closed shape is a
  grab handle), group and combine them, and snap pieces together with *Snap to
  Fit*.
- **3D design.** Extrude shapes into solids; turn a line into a round or
  rectangular **bar**; ramp any side of a top into a sloped **roof** or a circle
  into a **cone**; mark a shape as a **Hole**; and **Combine** solids and holes
  with true 3D booleans (union / intersect, with holes carving). Grouping a hole
  with solids previews the cut live without baking. 3D parts export to STL.
- **Reference-photo tracing.** Drop in a photo, remove its background (an offline
  ONNX u2netp model — no upload, no internet), and trace it to editable vectors
  (imagetracer). Everything bundled in `assets/` and runs in the browser.
- **Materials.** Pick Paper / Cardstock / Heavy cardstock / Vinyl / Pen / Custom
  to drive force, speed, blade depth, and pass count; Cardstock is the default.

## Files

- **DieCutter.cs** — USB + GPGL engine. Opens the die cutter via the
  `usbprint.sys` device interface (SetupDi\* + CreateFile, user-mode, no admin),
  converts SVG paths to GPGL, runs the registration scan, and cuts/scores.
- **SangalaServer.cs** — the local **bridge**: a loopback `TcpListener` (no admin,
  no firewall prompt) that serves the page and holds the USB connection. Runs in
  the tray. Endpoints: `/connect` `/status` `/cut` `/scan` `/printcut`
  `/manualstart` `/jog` `/manualread` `/manualcut` `/unload` `/raw`.
- **SangalaStudio.html** — the whole browser UI in one file (HTML + CSS + JS):
  design canvas, 2D/3D modes, classification, preview, and the toolbar.
- **assets/** — the offline photo tools: ONNX Runtime Web + the u2netp model for
  background removal, and imagetracer for vectorizing. Third-party licenses are
  in `assets/licenses/`.
- **Sangala for Snap.xml** — the block library Sangala loads into Snap! /
  TurtleStitch.
- **Sangala.ico** — the program icon (used by the Desktop shortcut).
- **Build SangalaStudio.cmd** — compiles the two `.cs` files with the in-box .NET
  Framework compiler (`csc.exe`) into `SangalaStudio.exe`. No install, no
  internet, no admin.
- **Update SangalaStudio.cmd** — one-double-click updater (see below).
- **Create Desktop Shortcut.cmd** — puts a "Sangala Studio" icon on the Desktop.

`SangalaStudio.exe` is **not** committed to the repo — it is built locally by
`Build SangalaStudio.cmd`, and is git-ignored.

## Build & run

1. Run `Build SangalaStudio.cmd` (uses the .NET compiler already in Windows) to
   produce `SangalaStudio.exe`.
2. Keep `SangalaStudio.exe` next to `SangalaStudio.html`; double-click the exe.
3. Your browser opens the design page; the bridge drives the machine over USB.

The page is served fresh from disk each request, so UI-only edits need just a
browser refresh; engine or bridge (`.cs`) changes need a rebuild and relaunch.

## Updating

**`Update SangalaStudio.cmd`** brings a beta tester up to date in one
double-click, with no git and no compiler know-how. It downloads the latest
**source** — `SangalaStudio.html`, `DieCutter.cs`, `SangalaServer.cs`,
`Build SangalaStudio.cmd`, `Sangala for Snap.xml`, `Sangala.ico` — then rebuilds
`SangalaStudio.exe` **locally** with the in-box .NET compiler.

Why build locally instead of downloading a ready-made exe: a program you compile
yourself carries no "downloaded from the internet" mark, so Windows does not warn
about it. The updater gates on the `SANGALA_VERSION` marker in the HTML,
downloads every file to a `.new` temp copy and sanity-checks each before swapping
anything in, backs up the files it replaces to `.bak`, closes the running engine,
rebuilds, and refreshes the Desktop shortcut — all-or-nothing, so a failed
download or build leaves your working copy untouched.

## Conventions

- **Registration marks:** Silhouette-standard — a solid square plus two
  L-brackets, 15.9 mm inset, on an 8.5 × 11 (Letter) page.
- **Cut vs. fold is read from the SVG line style** (Silhouette's own cut/score
  metadata does not survive SVG export, so only the visible style is left to go
  on): **red solid, unfilled = CUT**; **red dashed = SCORE / FOLD**; red filled
  and everything else = print (ignored). **Every fold line must be explicitly
  dashed in the exported SVG** — a solid red fold is indistinguishable from a cut
  and will be cut through. Score lines are cut as a light perforation at reduced
  force.
- **Optical eye offset:** the eye sits ~30 mm right of the blade on a Portrait, so
  the auto-scan search start is shifted left to compensate (`ScanRegMarks`
  `eyeRightMm`). The offset is per-machine — 30 mm on the Portraits, 0 on the
  Cameos.

## Machine support

Detection is by USB vendor ID (`0x0B4D`); a product-ID branch then sets the bed
width, mat type, and eye offset. The Portrait 3 (203 mm), Portrait 4 (216 mm),
and the Cameo family (Cameo 2 at 304 mm through the Cameo 5 Plus) are recognized;
an unknown product ID falls back to Portrait 3 settings. Full no-admin
print-and-cut is validated end-to-end on the Portrait and on the **Cameo 2**
(reads the marks and the registered cut lands accurately). WebUSB / WinUSB are
blocked or need admin, so the proven path is the `usbprint.sys` user-mode device
interface.

## File formats

- **Save** writes a `.model` file (JSON) that reopens **exactly** as saved —
  geometry, 3D meshes, mode, settings, position, and any reference photo and its
  background mask.
- **Export SVG** writes an interchange SVG for the die cutter or other CAD tools
  (re-sampled geometry; lossy for reload — use `.model` to round-trip).
- **Export STL** writes a 3D-print mesh of the current 3D part.
