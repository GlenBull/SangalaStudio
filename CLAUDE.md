# Sangala Studio — project guide for Claude Code

No-admin control of a **Silhouette Portrait 3/4** die cutter from a browser page
plus a tiny local **bridge**. Prints Silhouette-standard registration marks, scans
them, and does a registered print-and-cut (cut outlines + creased/folded score
lines) for paper-craft designs exported to SVG from Silhouette Studio. Built for
schools: **no admin rights, no driver install, no Bluetooth, no extra hardware —
USB only, user-mode.** This constraint is absolute.

## Interaction / process (please follow)
- Be concise and direct. Cut any word that isn't needed. Minimal formatting; prose over bullet lists unless a list is clearly warranted.
- Do NOT use popup question dialogs. Ask inline in plain chat, one question at a time.
- **NEVER write "honest", "honestly", "genuinely", or "straightforward"** — not in chat, not in code comments,
  not in commit messages. This is not a style preference to weigh: "honest" implies I was lying up to that
  point, which is insulting, and Glen has had to tell me more than once. Say the thing plainly instead; if a
  sentence seems to need "honestly", the sentence is the problem. Check before sending.
- **American spelling everywhere** — UI text, code comments, commit messages, docs, and chat. Not just the
  docs: color (not colour), center, gray, behavior, neighbor, canceled. This is a US project for a US course;
  I have drifted into British spelling repeatedly and had to sweep it back out, including shipping "Paper
  color" in a panel while its own tooltips said "colour".
- **One change at a time, then let the user test on the physical machine, then commit.** Do not batch many untested changes — that already cost a multi-hour unrecoverable break once. Commit (or tag) after each verified-good state so any regression is a `git diff` away, not a guess.
- Terminology: the machine is a **die cutter** / **Digital Fabrication tool**. Always write the full term **"die cutter"** — never abbreviate or truncate to "cutter" (or use "cutting"). In schools the bare word "cutter" can evoke self-harm (a teen who slashes their arms); the full "die cutter" keeps the meaning unambiguous. Applies to UI text, code comments, and chat. Prefer **"Make It"** over "Cut It". Product = **Sangala Studio**. Two DIFFERENT cases, on purpose (set by Glen 2026-07-23): in the
  **app UI** the subtitle is **"Digital Fabrication Tool"** — Title Case, capital "T" — matching
  Sangala Mosaic's **"Mosaic Design Tool"**. But in **documentation** (this file, the README, the
  User Guide, chat) write it **lowercase: "Digital Fabrication tool"**. Capital "Tool" in the
  running apps, lowercase "tool" in the docs — do not unify them. Same distinction in
  `Documents/README.md`. Show the mat/page in inches as whole numbers. The drag-snapping function is **"Snap to Fit"** — never bare "Snap", which collides with the **Snap!** programming language (which has its own button in the app); in UI status text and the docs, set *Snap to Fit* in italics to mark it as a function.

## Document formatting standards (User Guide & Tech Manual .docx)
- **Never regenerate a doc to revise it — edit the user's actual file IN PLACE** (surgical
  text edits only; run no document-wide formatting commands). Regenerating wipes his manual
  formatting and has caused repeated rework. New version = copy to the next version number, edit,
  then MOVE the prior version into the `Documents/.Archive` subfolder (the docs live in `Documents/`, which shows only the current version of each).
- Body = **Times New Roman 11 pt**, black, never below 11 pt; code identifiers in Consolas.
- Numbered lists for step sequences; **3 pt space after each list item**. A label leading a list
  item is **italic** (not bold). Labels: Title-Case every word EXCEPT words in parentheses (lowercase).
- **PARAGRAPH SPACING — a heading or lead-in sits TIGHT to the list it introduces.** Word's defaults
  are wrong here and I have had to be corrected: **Heading 3 = 0 pt before, 3 pt after**; a body
  paragraph **immediately before a list = 0 pt before, 3 pt after** (not the usual 5/5). An ordinary
  body paragraph keeps 5 pt. Set these explicitly — never inherit them from the style.
- **FIGURE CAPTIONS — apply ALL FOUR, and VERIFY each before delivering.** Sit the caption
  directly beneath its figure ("Figure N. <sentence>", numbered sequentially through the document;
  renumber the later figures when inserting one):
  1. **3 pt space between the figure and its caption** (space-before on the caption paragraph).
  2. **Centered** beneath the figure.
  3. **Italic** — the whole caption.
  4. **If it wraps to two lines, BALANCE them** (roughly equal length) with a manual line break
     (Shift+Enter) at a word boundary near the middle. A long first line over a stub is wrong.
- **TABLES — two kinds of rule; apply ALL and VERIFY each before delivering.**
  **(A) Structure/content conventions I must APPLY (these are NOT in the XML — cannot be cloned;
  I generate them):** every table has a **numbered title with a descriptive caption**
  ("Table N. <caption>"); tables are **numbered sequentially through the document**; the
  **column-heading row sits in the row directly below the title**. (Draft the number + caption for
  Glen's approval — I can't clone these.)
  **(B) Visual formatting — clone the EXACT values from an existing Tech Manual table, do NOT
  reconstruct from memory.** (This used to say "Table 8"; the manual has only Tables 1–5, and all
  five carry the identical format — Arial 10 pt, cell paragraph spacing before=60/after=40 twips,
  table centered, merged bold title row, italic centered heading row, double rule under the headings.
  **Table 4** is the exemplar to copy from; verified 2026-07-25.)
  1. Table **centered on the page**.
  2. **Arial 10 pt** throughout.
  3. **Cell paragraph spacing: 3 pt before, 2 pt after** on every cell — this is PARAGRAPH spacing
     (space-before/space-after), **NOT** cell top/bottom margins. (The rule most often missed.)
  4. Left/right cell margins present; label column slightly left-indented.
  5. Title row = one cell **merged across all columns**, Arial 10 pt **Bold**.
  6. Column-heading row: Arial 10 pt **Italic**, **centered**.
  7. Body cells: Arial 10 pt regular, left-aligned.
  8. Borders: single-line grid; the column-heading→body divider is a **double** line.
- **PAGINATION — headings must never orphan, and autospacing must never be added. These two defects came
  from MY edits (I add content, the page breaks shift, headings strand and gaps balloon), and Glen has been
  fixing them by hand. Stop them at the source:**
  - **Every heading paragraph carries `<w:keepNext/>` AND `<w:keepLines/>`** in its `pPr`, so it stays glued to
    the text beneath it and can never sit alone at the bottom of a page. The guide's headings currently have
    NEITHER (verified: zero `keepNext` in the file) — that is why adding a paragraph orphaned a heading two
    sections away. Whenever I touch a doc, ensure every heading has both.
  - **Never add autospacing.** Do NOT write `w:beforeAutospacing="1"` / `w:afterAutospacing="1"` on any
    paragraph I insert, and do NOT copy them off a neighboring run. Word renders autospacing as large
    browser-style gaps — that is the extra space between a bullet and the next heading. Use the EXPLICIT point
    values from the spacing rules above. (The file carries ~110 legacy autospacing paragraphs from its HTML
    origin; leave those alone — mass-converting them is a forbidden document-wide change — but never add more.)
  - **A few lines must not spill onto a near-empty page.** When my added content pushes a couple of lines onto
    a fresh page that then holds nothing else, that reads as broken. Glen's fix, and mine: reclaim room on the
    PRIOR page (tighten the spacing there — usually the autospacing gaps are the culprit) so the stray lines
    pull back up. `docxcheck.ps1` flags these as UNDERFILLED pages; treat each as a judgment call, not an
    auto-fix — sometimes the short page is a legitimate section end.
- Delivery: give the plain Windows file path in text (no preview cards / no `computer://` links).

## Approval & git safety
- **Auto-approve (standing consent):** work confined to this repo, the temp
  scratch folder, pushing commits to this GitHub repo, and **the Dropbox
  `AI Sandbox\Design through Making\Sangala Tools` tree** (see the publishing rule
  below). No need to ask.
- **Always ask first:** the rest of the user's Dropbox and any other drive,
  system/account settings, network to anywhere other than this GitHub
  repo, and any history-losing git — force-push, hard reset that drops commits,
  branch deletion.
- **PUBLISH DOC UPDATES TO DROPBOX — standing practice (set by Glen 2026-07-25).**
  `Sangala Tools` is how **Moses** gets the current **User Guide** and **Tech
  Manual**, so a new version of either is not finished until it is there. When a
  new version is delivered: copy it into the right subfolder (the guide and manual
  both live in `Sangala Tools\Sangala Studio Files`), then move the version it
  supersedes into that folder's own `Archive` subfolder — so the folder shows only
  the current version, mirroring how `Documents/` and `Documents/.Archive` work in
  the repo. Do this without being asked; it is part of shipping the doc. (The app
  itself needs no copying — `Update SangalaStudio.cmd` pulls the page and exe from
  GitHub.)
- **Commit and push after each verified-good change** — one change, verify it's
  good (see line-14 physical-test rule for machine-facing changes), then commit
  and push so any regression is a `git diff` away, not a guess.
- **Collaboration is shared-repo, not forks (since 2026-07-24).** Jo Watts is a
  write collaborator on `GlenBull/SangalaStudio`; he and Glen work on branches in
  the one repo and integrate via ordinary Pull Requests — no more cross-fork
  merges. The one-time "Github Merge" runbook (the careful bring-in of Jo's 3D
  fork into `main`) was a migration artifact, not the routine process; day-to-day
  is branch → PR.

## Files
- **DieCutter.cs** — USB + GPGL engine. Opens the cutter via the `usbprint.sys`
  device interface (SetupDi* + CreateFile, user-mode, no admin). Classes: Native
  (USB discovery), Cutter (Open/Setup/Cut/ScanRegMarks/ManualRegMarks/MoveToMm/
  SetForce/SetBladeDepth/Unload), Svg, MainForm (standalone desktop app entry).
- **SangalaServer.cs** — the local **bridge** (call it the bridge, never "helper"). Loopback `TcpListener` (no admin/firewall),
  serves SangalaStudio.html, holds the USB connection. Routes: /connect /status
  /cut /scan /printcut /manualstart /jog /manualread /manualcut. Runs in the tray.
- **SangalaStudio.html** — the browser UI (single file: HTML+CSS+JS).
- **Build SangalaStudio.cmd** — compiles DieCutter.cs + SangalaServer.cs with the
  in-box .NET Framework csc.exe (`/main:DieCutterApp.Server /target:winexe`) into
  SangalaStudio.exe. No install, no internet, no admin.
- **Calibration Card.svg** — minimal test file: one cut rectangle + one fold line.

## Build & run
1. `Build SangalaStudio.cmd` → SangalaStudio.exe.
2. Keep SangalaStudio.exe next to SangalaStudio.html; double-click the exe.
3. It opens the page in the browser and drives the machine over USB.
The HTML is served fresh from disk each request, so UI-only changes need just a
browser refresh; engine/server (.cs) changes need a rebuild + relaunch.
- **Beta testers update via `Update SangalaStudio.cmd`**, which now fetches BOTH the
  page AND the engine (`SangalaStudio.exe`) in one double-click — so engine (.cs)
  changes reach non-technical users without anyone rebuilding. The exe is therefore
  COMMITTED to the repo (un-ignored in .gitignore) and served from its raw URL; a
  normal `git push` ships it. The updater gates on the `SANGALA_VERSION` marker (HTML
  comment on line 2), downloads to temp, verifies BOTH (page ends in `</html>`, exe
  > 20 KB), then `taskkill`s the running exe and swaps both — both-or-nothing, so a
  half-download changes nothing. `SANGALA_VERSION` is the **release** number: bump it
  on ANY shipped change, **page or engine** (an engine-only fix still bumps the line,
  else the checker calls it "already up to date"). **After an engine (.cs) change:
  rebuild the exe (`Build SangalaStudio.cmd`) AND commit the exe**, or testers get the
  new page over a stale engine. The updater .cmd itself is stable infrastructure —
  distribute a new copy of it by USB the once (it can't update itself while running).
- **Loopback is addressed as `localhost`, never `127.0.0.1`, anywhere the PAGE can reach.** Glen's preview
  pane blocks raw-IP navigation and shows a "Link to 127.0.0.1 was blocked" banner. The real culprit was
  SangalaStudio.html's own `file://` hop (it fetches the bridge and `location.replace`s to it): the harness
  previews the file after every edit, the hop fires whenever the bridge is running, and the preview blocks
  it — a banner per edit. Both spellings reach the same IPv4 listener (verified), so prefer `localhost` in
  the page and in browser-tool navigation alike. `SangalaServer.cs` opening 127.0.0.1 in a REAL browser is
  fine and is not the trigger — and changing it would force testers to rebuild.

## Hardware / protocol facts
- Portrait 3: USB VID 0x0B4D, PID 0x113A, width 203 mm, mat TG "3". Portrait 4:
  PID 0x113F, width 216 mm, TG "11". **Cameo 2: PID 0x112B, width 304 mm (12 in), mat TG "3", EyeRightMm 0.
  FULL print-and-cut VALIDATED on the Cameo 2 (2026-07-18, Gina): reads the marks AND the registered cut
  lands accurately — so EyeRightMm 0 and mat TG "3" are both correct for it. The fix was the per-machine eye
  shift (`EyeRightMm`): Portrait 30, **Cameo 2 = 0** — the Portrait's 30 mm was aiming the scan past the marks
  (the reference driver applies no eye shift and works on Cameos). On failed registration the machine re-inits
  (`Reset()` = ESC EOT; no dedicated clear command exists — power-cycle is the sure clear of a stuck Cameo 2
  job); that reset path is in place but not yet exercised (Gina's scans succeeded).** Detection is by VID alone (`Native.Find("vid_0b4d")`), then a PID branch picks width/TG/eye; an
  unknown PID falls back to Portrait 3. usbprint.sys interface GUID
  {28d78fad-5a12-11d1-ae5b-0000f803a8c2}. WebUSB/WinUSB are dead ends (blocked or
  need admin); usbprint.sys user-mode is the proven path.
- GPGL: ASCII commands terminated by ETX (0x03). 1 mm = 20 Silhouette Units
  (SU = round(mm*20)). Coordinates are **y-first**: `M y,x` = move (pen up),
  `D y,x` = draw (pen down). ESC EOT = init; ESC ENQ = status (0 ready/1 moving/2 unloaded).
- Registration (Cameo/Portrait "type 2"): TB50,0 TB99 TB52,2 TB51,400 (20 mm mark
  length) TB53,10 (0.5 mm thickness) TB55,1, then
  `TB123,<Ydist>,<Xdist>,<searchTop>,<searchLeft>`. Reply trimmed == "0" means
  marks found. Distances are between mark reference points; for Letter with 15.9 mm
  inset that's Ydist≈247.6, Xdist≈184.1. Manual variant is `TB23,<Ydist>,<Xdist>`.
  This mirrors fablabnbg/inkscape-silhouette (Graphtec.py), which sniffed Studio.
- **Optical eye offset (~30 mm right of the blade).** The firmware aims the blade,
  not the eye, and reports zero sensor offset (TB71 = 0,0). So the auto-scan search
  start is shifted LEFT by `eyeRightMm` (default 30, in ScanRegMarks) — allowed to
  go negative into the left margin — otherwise the eye never reaches the top-left
  square. Manual align solves the same reach problem by letting the jog go negative.
  If registration lands slightly off, this 30 is the number to tune.
- AutoBlade depth is set with FY1 (reset) + TF<depth>. NOTE: FY1 must NOT run right
  before a registration scan (it disturbs the scan). Blade depth is currently set in
  Setup via TF only; `SetBladeDepth()` (FY1+TF) exists if depth needs re-tapping
  before a cut. Heavy cardstock needs multiple passes, not just force.

## Design classification (critical)
Silhouette's cut/fold/score designation is METADATA that does NOT survive SVG
export — only the visual line style survives. Sangala classifies from the SVG:
- **red (#ff0000) solid, unfilled → CUT**
- **red dashed (stroke-dasharray) → SCORE / FOLD**
- red filled (e.g. window panes) + everything else → print (ignored)
Therefore **every fold line must be explicitly DASHED in the exported SVG.** A fold
left as plain solid red is indistinguishable from a cut and WILL be cut through.
Dashed folds already work and hold — do NOT "fix" them with shallow blade depth.
- Score lines are cut as a **perforation** (dashes ~4 mm on, ~1.2 mm gap) at reduced force.
- Polylines are simplified (Douglas-Peucker ~0.08 mm) so straight runs are single
  smooth strokes — otherwise the blade shudders over hundreds of tiny segments.

## Coordinate / print notes
- SVG read: getCTM() returns pixel space → convert px→mm with 25.4/96. For paths in
  <defs> (null CTM, e.g. Studio's <use>-instanced geometry) use raw user units × the
  svg's mm-per-unit scale. Drop any non-finite point's whole path.
- **On load, a rect/circle/ellipse's own geometry attributes (x/y/w/h, cx/cy/r) are re-mapped through the
  same getCTM into design-mm, because the 3D build (`bodyTris`) reads them straight off the element — a
  polygon uses `o.poly`, but a rect/circle uses its attributes.** Without this a REOPENED shape extruded at
  its raw file coordinates: Save SVG crops the viewBox to the design's bbox, which re-bases `o.poly` but not
  the attributes, so a reopened rect/circle sat OFFSET in X,Y (by the old bbox-min) in 3D while the 2D sketch
  looked right (Z was fine — only x/y drift). A drawn shape sets `el` and `poly` together so it was never
  affected; the mismatch only showed when a new shape was drawn over an opened design. `normalize()` shifts
  the element geometry in lockstep with `o.poly`. A rotated rect (skew in the CTM) is left as-is. Verified
  against real Chromium getCTM (`ctm_math.js`): viewBox "50 30 100 80" maps a rect at (60,45) → (10,15).
- Print files (silhouette-style SVGs) keep ABSOLUTE page coordinates. Registered cut
  coords = page coords − 15.9 mm (the mark origin). Print hides the red machine lines
  (like Studio's weight-0) and overlays the standard marks, so the inkjet prints
  artwork only. Preview shows the 8.5×11 Letter page (not the 12" mat) for print files.
- End of job returns media to the front (\0,0 M0,0 FN0). FO fed the wrong way; do not
  reintroduce it without checking direction.

## UI
Toolbar: Connect · **Save** (💾) · Open · **Export SVG** (📄) · **Export STL** (🔷, 3D only) · **Marks** (toggle, default OFF) · Print · **Test**
(menu: Test square / Scan test / Manual align) · Settings (gear). Green **Make it!** branches
on the Marks toggle: ON → register + cut (/printcut); OFF → plain cut (/cut).
- **Three file actions, distinct on purpose (2026-07-24):** **Save** writes a `.project` file (JSON) that
  reopens EXACTLY as saved; **Export SVG** (was "Save SVG") writes an interchange SVG for TinkerCAD / the die
  cutter; **Export STL** writes a 3D-print mesh. `.project` = `collectProject()` — the verbatim `serializeState()`
  object snapshot (the SAME one Undo restores, so NO re-sampling) PLUS the globals SVG drops: `mode3D`, `units`,
  the Silhouette settings (force/speed/blade/passes/scale), `material`, position (offx/offy), the Marks toggle,
  and `view`. `openProject()` runs `restoreState()` then re-applies those globals (`setUnits` FIRST — it rewrites
  the position fields — then restore their saved values; `setMode3D` LAST to re-lay the toolbar), and is routed
  through the **Open** button by the `.project` extension (accept list + `openFile`). An **in-progress trace IS
  stored** (`refImage`, format version 2): the source photo (data URL), placement, the Remove-BG **mask** (also a
  data URL — so reopening recomputes the fast `SangalaBg.trace` from it and NEVER re-runs the ONNX model), and the
  threshold/pathomit tuning. `restoreRefImage()` decodes it async (photo, then mask, then re-trace) and re-opens
  the tune panel. A big photo makes a big project file — that is the accepted cost. Icons: Save 💾, Export SVG 📄,
  Export STL 🔷 (avoid 📦 — the Mode(3D)
  button uses it). Why: Export SVG re-samples geometry (getCTM + Douglas-Peucker ~0.08 mm), re-derives kind from
  stroke, and doesn't carry mode/settings/photo — it is lossy for reload; the project file is the exact one.
  Validated: build+combine+group in 3D → project JSON (4.5 KB) → flip mode & Force, reopen → objects, mesh
  volumes, gpaths, all attrs, mode, and settings restored identically (`project_test.js`, real `openProject`);
  and a reference photo + Remove-BG mask + trace + threshold/pathomit round-trips exactly (`refimg_test.js`).
**Material** (Paper/Cardstock/Heavy cardstock/Vinyl/Pen/**Custom**) sits BELOW the Make it! button in the
Fabricate panel — the most-used control, out of Setup — and **defaults to Cardstock** (the material used
most). Picking a material drives Force/Speed/Blade/Passes via `applyMat()`; **Custom** seeds the fields with Cardstock's values as a starting point and opens the Settings panel (`openSettings()`) to adjust (it is not a MATS preset, so the cut runs in blade mode from the field values). Settings panel (the gear) holds
the rest under a **Silhouette Settings** header: Force, Speed, Blade, Passes, Scale %, Units, Position. Heavy cardstock preset = force 33, speed 3,
blade 7, 2 passes.
- **Grabbing a shape to move it: the whole INTERIOR is a grip, not just the thin outline.** In the select-tool
  mousedown handler, an unselected body press picks the TOPMOST closed shape whose interior (`ptInPoly`) — or
  outline (within 8 px) — is under the pointer, selects it, and starts the move in one gesture; you can grab a
  DIFFERENT shape directly (it switches selection). It sets `suppressClick` so a press that doesn't drag still
  holds the shape. Guarded by `!e.shiftKey` so Shift+click still builds a group / picks the Combine operand via
  the click handler. (Before: an unfilled shape was grabbable only by its ~8 px outline — "hard to click in the
  right place." The click handler's own interior selection still requires a fill, deliberately, for 2D
  click-through; this is only the drag-to-move grab.) Grouped shapes are still grabbed by the group block above.

## Current state (as of handoff)
- Full no-admin print-and-cut VALIDATED end-to-end on the Calibration Card:
  print artwork + marks → scan/register → cut outline → crease fold. Known-good.
  Also VALIDATED on the Cameo 2 (2026-07-18, Gina) — third machine, registration + accurate cut.
- JBK colonial house (John Blair Kitchen): **blocked on Gina redrawing the design so
  every fold line is explicitly dashed** in the exported SVG (some folds currently
  export as solid red and get cut, splitting the model). Classifier + positioning
  are correct; the file just needs unambiguous fold lines.
- Open threads: adapt designs wider than the 8" (203 mm) Portrait width by re-nesting
  (no scaling); prepare a CAD Library entry (open SVG + metadata + instructions);
  a "Open from Library" linkage that fetches a design SVG by URL.

## 3D bars and line-driven holes (feature branch `claude/repo-review-det4qo`)
A straight line can be turned into a solid 3D **bar** (round or rectangular cross-section,
placed by the line's XY + angle, height set by Base). Combining a bar with a part via
**Difference / Union / Intersect** runs a true **3D boolean** (`mesh3D` — an inlined BSP CSG,
plus `bool3D` / `operandMesh` / `makeMeshObj`), because a horizontal rod through a solid — or a
hole through a curved or sloped part — has no flat 2D stand-in. Difference bores a hole, Union
adds a peg, Intersect keeps the overlap. Validated by an independent point-membership +
watertightness oracle (dev harness in the scratchpad). Bars and combined parts are **3D-only**:
excluded from the die cutter, drawn on the plan as a teal line (bar) or gray outline (part).
- **Two mechanisms, cleanly split by role (settled 2026-07-23, Glen's design):**
  - **Group / Ungroup (details-panel buttons) = BUNDLE, in BOTH modes.** A group binds members so they move
    and select together; the objects stay separate and Ungroup-able (it is NOT a bake). Grouping **nests** (`gpath =
    [outermost..innermost]`, `o.group` = `gpath[0]`), so **Ungroup peels one level** (stepwise). **You build a
    nested group by Shift+clicking (TinkerCAD-style): select a group, Shift+click a new shape to ADD it, then
    Group.** The click handler's Shift branch grows `selMulti` (adding the clicked object's WHOLE outermost
    group) so a group + a new shape becomes one Group-able selection; two loose single shapes still set
    `selId2` (the Combine 2nd operand, also Group-able as a pair), and any 3rd pick or a group operand promotes
    to `selMulti`. (Before this, Shift+click only set `selId2` and only when a single shape was selected, so a
    group could never gain a member — the bug Glen hit.) Persists via
    Save SVG (`data-gpath`, space-joined; legacy `data-group` = one level), Undo/Redo, copy. (The earlier
    live union+carve group build — `evalGroupTree`/`evalNonBrick`/`geomStamp`/`_groupCache` — was REMOVED;
    Glen's rule: "a Group that is really a Union" is wrong. Bricks still weld via `FUSE_GROW`/`offsetRing`
    through `bodyTris(o,fuse)`.)
  - **Combine (`bool3D`) = MERGE/CARVE, baked.** This is where geometry actually combines. **Union honors the
    Solid/Hole flag** (TinkerCAD-style): a Hole operand subtracts, a solid unions — so Union alone does both
    (solids merge, holes carve), validated by the oracle (`union_hole_test.js`, mism=0). **N-ary in 3D
    (`bool3Dn`, 2026-07-24): Combine takes AS MANY shapes as are selected** — union merges every solid then
    carves every hole; intersect keeps the region common to all. `applyBool` routes `selMulti` (2+) through
    `bool3Dn` in `mode3D`; `bool3D(op,o1,o2)` is now a 2-operand shim over it, and `updateCombine` enables the
    buttons for a 2+ multi-selection. Removes only the shapes it actually combined (a selected flat/no-Depth
    shape is left alone), bakes ONE part with a footprint FOLDED to match the op. Validated: 3 chained solids +
    1 hole → one part, vol 10000−360=9640; 3-box intersect → 1000 (`nary_test.js`/`nary_test2.js`, real
    `applyBool`). **Menu is mode-specific:** 2D = Union / Difference / Intersect (two shapes); **3D = Union /
    Intersect only** (`pDiff` hidden when `mode3D` — Difference is unneeded because Hole + Union carves).
    Combine bakes one mesh, keeps Depth/Base,
    and is destructive (undo/redo to reposition). A bar bores a hole by being marked Hole and Combined. The BSP
    CSG (`mesh3D`) leaves T-junctions on subtract/intersect (a face split against one solid's plane but not the
    neighbor's shared edge → edges shared by ≠2 faces → slicers flag "non-manifold"), so `bool3D` runs the
    result through **`cleanMesh`** (weld coincident verts + split each straddled edge at the vertices on it,
    winding preserved) → manifold STL, volume unchanged. Validated `cleanmesh.js` (nm→0, vol diff ~1e-14).
    **Where the clean runs (settled 2026-07-24, iterated-Combine freeze fix):** `bool3D` bakes **weld-only**
    (`cleanMesh(...,1e-4,true)` — weld coincident verts + drop degenerate slivers, but SKIP the T-junction
    pass); the **full manifold clean runs once per piece at STL export** (`exportSTL` maps each `part` through
    `cleanMesh`). Reason: the T-junction pass ADDS triangles (it splits straddled edges), and running it after
    every Combine compounds across an iterated design — each new hole re-splits an ever-larger mesh, so the
    COST was O(mesh) per hole and the page froze on the 4th-ish round hole cut into a many-combine solid (not
    the CSG — the clean). Weld-only intermediates stay geometrically exact (volume tracks perfectly) and keep
    their T-junctions until export, where slicers need manifold. Validated: 16 iterated holes each <300 ms,
    NaN=0 throughout (`app_sim.js`); known-good CSG suite still nm→0 with identical volumes (`suite_new.js`).
    A baked part therefore persists a weld-only (non-manifold-until-export) mesh in `data-mesh-tris`; the STL
    is cleaned at export, and cleaning is per-piece (never across pieces, which would weld separate parts).
    **CSG robustness (same fix):** `mesh3D` now DROPS degenerate (cross-length <1e-9) and non-finite triangles
    from CSG input AND output, and `split` clamps a near-zero denominator (`|den|>1e-12 ? … : 0.5`) — an
    iterated boolean was accumulating sliver triangles whose garbage plane-normals divided to NaN and made the
    BSP recurse forever, which is why each successive hole "reported several NaN errors before resolving." With
    the drop+clamp a sliver can no longer poison the next Combine. **Perf:** the T-junction test is
    spatial-hashed (splits reuse existing welded verts, so the hash is valid throughout) — a naive all-verts
    scan froze the page on a cone CSG (thousands of tris); hashed it's ~8× faster (a cone+cone union
    1113→82 ms). A >50k-tri backstop welds only rather than hang. **Known remaining limit:** the BSP still
    re-fragments flat faces each subtract (a slab top chopped by a cutter's infinite side-planes), so a VERY
    heavy iterated design (many high-facet holes) can still bloat past ~50k tris and then export non-manifold
    via the backstop — a coplanar-face merge is the follow-up cure if a real design hits it.
  - **The *Hole* flag** (Stage 1: checkbox in shape details for `mode3D && is3DSolid`; draws blue-dotted
    `#1a5fb4`, `data-role="hole"`). A **loose (ungrouped) hole still makes no material** — it shows nothing in
    3D. But a hole **grouped** with solids now carves them in the LIVE preview (see next bullet), and Combine
    still bakes.
  - **Group-preview boolean (settled 2026-07-24, Glen's staging-ground request).** `buildTris` buckets the
    non-brick bodies by their OUTERMOST group. A bundle with **no** hole stays a plain bundle (each solid its
    own piece — non-touching shapes just coexist). A bundle that **holds a hole** previews the boolean: each
    solid is carved (`mesh3D("subtract", …)`, weld-only) by every hole that reaches it — a hole that misses a
    solid leaves it whole, a hole that covers one empties it. So a grouped solid+hole **renders AND exports**
    as a solid-with-a-hole WITHOUT baking (WYSIWYG: `buildTris` is the single source for both the 3D preview
    and the STL). The objects stay separate and Ungroup-able; Combine is still what bakes a single committed
    mesh. **No forced union of solids** (overlapping solids stay separate parts — a slicer unions them) and
    **no Intersect** — a bundle has no operator for "keep only the overlap"; that stays Combine-only. Cached
    per bundle by a geometry stamp (`grpStamp` → `_grpPrev`) so orbiting never recomputes and only an edited
    bundle rebuilds; camera moves call `renderPreview` (projection) not `buildTris`, so this never reintroduces
    the old rotate-freeze. Validated: grouped solid+hole vol 12000→11000 (1000 carved), a disjoint solid in the
    same group stays whole, a loose hole still emits nothing (`grouppreview_test.js`, real `buildTris`).
  - **Plan-view (2D) footprint of a baked part is operation-matched** so it reads true with 3D View off
    (`bool3D` computes it via `boolShapes` to mirror the op): a shape carve = solid **minus** cutter — the
    outline **notches** where the cutter bit an edge and shows a **dashed interior hole** where it was inside,
    existing holes carried; union/intersect show the merged/overlap outline. The part draws gray, its openings
    dashed-gray (distinct from a not-yet-combined hole's blue dots). Stored in `o.holes` (`data-holes`),
    persisted, and moved/rotated/resized with the part; `bodyTris` ignores them (the mesh already has them).
    A **bar** bore is the exception: it keeps the solid outline + a dashed swept-rectangle marker (an internal
    bore does not breach the top face, so it must not notch the outline). Validated: `footprint_test2.js`.
- **Sloped tops = per-edge "roof" (`roofTris`, Stage A + B DONE, validated 2026-07-23).** Any side of a CONVEX
  extruded top can ramp inward independently, set by ANGLE (deg from vertical, 0 = flat), uniform or asymmetric.
  Every ramp keeps a short vertical **lip** (`ROOF_LIP` = 0.6 mm) so it never tapers to an unprintable feather
  edge. **Invert** (`data-slope-inv`, an *Invert* checkbox shown once there is a slope/cone) mirrors the roof in
  Z — the top stays full and flat, the UNDERSIDE falls away — the shape that fills the underside of an overhang,
  like a slope brick's invert (reflect + swap winding, so normals stay outward). An inward-sloped solid on a
  convex base is itself convex, so the mesh is the **3D convex hull** (`rfHull`,
  incremental) of the base ring (z0), the lip ring (zL) and the top vertices (z1); the top vertices come from
  clipping the base inward by each edge's offset (`rfClip`/`rfTopVerts`), capped only so the feasible top is at
  least a point. That single construction covers a **truncated** top, a **ridge** (top = segment, a gable), and
  an **apex** (top = point, a pyramid/hip) — Stage B — all watertight and winding-agnostic. Replaces the old
  one-axis `slopedBoxTris` wedge (removed; `yzPrism` stays for bricks, which keep their own slope path).
  **Data:** `data-slopes` = per-edge angles aligned to the footprint's own edge order; legacy single
  `data-slope-run`/`data-slope-dir` is read as a fallback and migrated on first edit. Persists via Save/Undo/copy.
  **Gate:** axis-aligned rects (canonical Front -Y / Right +X / Back +Y / Left -X) OR any `rfConvex` polygon OR a
  **circle → cone** (`data-cone` = one rim taper angle; `rfConeBase` gives a moderate-facet ring, roofed with a
  uniform run — moderate = truncated cone, steep = full cone/apex); concave falls back to no slope (Stage C);
  skipped with sockets/holes (a non-level top). **UI:** rects show named sides, other convex shapes show numbered
  Side 1..N (focusing/hovering a field green-highlights that edge on the plan, `slopeHi`), a circle shows one
  Cone taper field. Validated against the point-membership + watertightness oracle across square/triangle/
  pentagon, uniform/asymmetric, truncated + ridge + apex, and clockwise inputs (scratchpad `roof.js`/`roofB.js`);
  the ported app code reproduces the oracle volumes exactly (`app_roofB.js` check). **Next:** Stage C (concave
  via straight skeleton), and possibly a circle → cone.
- A 3D-Combine result is a **baked mesh**. It PERSISTS: `syncMeshToEl`/`parseMeshRel` store the
  triangles in `data-mesh-tris` (relative to the footprint bbox-min, so a Save-SVG crop cancels), so
  save/reopen and Undo/Redo (`serializeState` carries `o.mesh`) keep the part. It can be MOVED, ROTATED,
  and RESIZED — the drag handlers carry the mesh through the same transform as the footprint (rotate spins
  the mesh about the vertical axis; box-resize scales its x/y, `rotMeshTris` + the boxresize scale). **Full
  z control in the details panel** (`mode3D` only): a baked part shows **Depth** (`data-dim="meshdepth"` —
  scales every triangle's z about the base so the lowest point stays put and thickness grows upward, like a
  shape's Depth extruding up from z0) and **Base** (`data-dim="meshbase"` — rigidly shifts all z so the lowest
  point sits at the given height). Both leave footprint x/y untouched, update the preview live, persist via
  `data-mesh-tris`, and carry through Undo/Redo. A z-scale about the base is a positive affine, so the mesh
  stays watertight. (Footprint x/y still resize only via box-resize; the z fields cover thickness + elevation.)

## Editing a .docx on THIS machine (read before touching a doc — I have hit this 6+ times)
The standard skill recipe's rezip step **does not work here: there is no `zip` command.**
`unzip` exists; `zip` does not. Do not run `zip -Xr` and rediscover this again.
1. `unzip -q "Doc.docx" -d unpacked/`
2. **Skip `merge_runs.py`** — it corrupts validation on this machine (a merged-but-unedited
   control failed identically). Targets have matched in raw XML anyway.
3. Edit `unpacked/word/document.xml` surgically with a small Python script (read/write UTF-8).
4. **Rezip with Python's `zipfile`** (`[Content_Types].xml` first, then walk the tree) — this is
   the established method here and has been used for every past doc edit.
5. Validate with `scripts/office/validate.py out.docx --original <orig>`, and set
   **`PYTHONIOENCODING=utf-8` first** or it crashes printing `→` to the cp1252 console. Set
   **`PYTHONUTF8=1`** as well: without it the validator READS the docx with the Windows locale codec and
   reports a bogus `'charmap' codec can't decode byte 0x9d` as a NEW validation error, when the file is
   perfectly good UTF-8. Confirm any such "error" against the bytes before believing it.
6. **CHECK PAGINATION before delivering — MANDATORY. This is how the defects get caught; skipping it is how
   they shipped.** Orphaned headings live in the PAGINATION, not the XML, so `validate.py` passes while the
   page looks wrong. No LibreOffice/poppler here and the Read tool can't rasterize a PDF either — instead drive
   **Word via COM**, which reports where each heading falls. Run the ready-made check:
   `powershell -NoProfile -File tools\docxcheck.ps1 "Documents\User Guide (Ver 4.3).docx"`
   It opens the doc read-only (works even while Glen has it open) and prints: headings lacking `keepNext`, any
   heading currently split from its text across a page break, and the autospacing count. **Deliver only when it
   prints `PAGINATION CLEAN`** (zero orphans, zero headings missing keepNext). If you need a human-eyeball copy,
   Word COM `ExportAsFixedFormat` to a PDF for Glen — but the script is the gate.
Useful facts already established: the docs use em dash U+2014 with spaces, straight apostrophes,
keystrokes as italic runs written `Ctrl-Z` (hyphen), body paragraphs are `<w:pStyle w:val="NormalWeb"/>`,
and §6-style labels are sentence case (matching the file, e.g. *Break at a node*).

## Gotcha
The project now lives in a plain (non-Dropbox) git checkout, so edit files
directly with the Write/Edit tools — no need to route saves through bash/python.
**Python IS installed** (3.12, `C:\Users\glenb\AppData\Local\Programs\Python\Python312`) — an
earlier version of this file claimed otherwise, which was wrong and steered me away from the
zipfile path above. (It formerly lived in a Dropbox-synced folder
that corrupted large saves with NUL bytes/truncation and dehydrated files to
cloud-only placeholders; that no longer applies.) A quick integrity glance after
big edits is still cheap: brace balance for .cs, file ends with </html>.
