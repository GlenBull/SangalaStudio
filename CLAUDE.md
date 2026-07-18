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
- Terminology: the machine is a **die cutter** / **Digital Fabrication Tool**. Always write the full term **"die cutter"** — never abbreviate or truncate to "cutter" (or use "cutting"). In schools the bare word "cutter" can evoke self-harm (a teen who slashes their arms); the full "die cutter" keeps the meaning unambiguous. Applies to UI text, code comments, and chat. Prefer **"Make It"** over "Cut It". Product = **Sangala Studio**; subtitle **Digital Fabrication Tool** (mixed case). Show the mat/page in inches as whole numbers. The drag-snapping function is **"Snap to Fit"** — never bare "Snap", which collides with the **Snap!** programming language (which has its own button in the app); in UI status text and the docs, set *Snap to Fit* in italics to mark it as a function.

## Document formatting standards (User Guide & Tech Manual .docx)
- **Never regenerate a doc to revise it — edit the user's actual file IN PLACE** (surgical
  text edits only; run no document-wide formatting commands). Regenerating wipes his manual
  formatting and has caused repeated rework. New version = copy to the next version number, edit,
  then MOVE the prior version into the `.Archive` subfolder (main folder shows only the current).
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
  **(B) Visual formatting — clone the EXACT values from Table 8 of the Tech Manual, do NOT
  reconstruct from memory:**
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
  scratch folder, and pushing commits to this GitHub repo. No need to ask.
- **Always ask first:** anything outside the repo (other drives, the user's
  Dropbox), system/account settings, network to anywhere other than this GitHub
  repo, and any history-losing git — force-push, hard reset that drops commits,
  branch deletion.
- **Commit and push after each verified-good change** — one change, verify it's
  good (see line-14 physical-test rule for machine-facing changes), then commit
  and push so any regression is a `git diff` away, not a guess.

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
- **Beta testers update via `Update SangalaStudio.cmd`**, which checks a
  `SANGALA_VERSION` marker (an HTML comment on line 2 of SangalaStudio.html) against
  GitHub before downloading, and skips the download/backup entirely when they
  match. **Any commit that changes SangalaStudio.html must bump that version
  string**, or the checker calls a real change "already up to date."
- **Loopback is addressed as `localhost`, never `127.0.0.1`, anywhere the PAGE can reach.** Glen's preview
  pane blocks raw-IP navigation and shows a "Link to 127.0.0.1 was blocked" banner. The real culprit was
  SangalaStudio.html's own `file://` hop (it fetches the bridge and `location.replace`s to it): the harness
  previews the file after every edit, the hop fires whenever the bridge is running, and the preview blocks
  it — a banner per edit. Both spellings reach the same IPv4 listener (verified), so prefer `localhost` in
  the page and in browser-tool navigation alike. `SangalaServer.cs` opening 127.0.0.1 in a REAL browser is
  fine and is not the trigger — and changing it would force testers to rebuild.

## Hardware / protocol facts
- Portrait 3: USB VID 0x0B4D, PID 0x113A, width 203 mm, mat TG "3". Portrait 4:
  PID 0x113F, width 216 mm, TG "11". usbprint.sys interface GUID
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
- Print files (silhouette-style SVGs) keep ABSOLUTE page coordinates. Registered cut
  coords = page coords − 15.9 mm (the mark origin). Print hides the red machine lines
  (like Studio's weight-0) and overlays the standard marks, so the inkjet prints
  artwork only. Preview shows the 8.5×11 Letter page (not the 12" mat) for print files.
- End of job returns media to the front (\0,0 M0,0 FN0). FO fed the wrong way; do not
  reintroduce it without checking direction.

## UI
Toolbar: Connect · Open SVG · **Marks** (toggle, default OFF) · Print · **Test**
(menu: Test square / Scan test / Manual align) · Settings (gear). Green **Make it!** branches
on the Marks toggle: ON → register + cut (/printcut); OFF → plain cut (/cut).
**Material** (Paper/Cardstock/Heavy cardstock/Vinyl/Pen) sits BELOW the Make it! button in the
Fabricate panel — the most-used control, out of Setup — and **defaults to Cardstock** (the material used
most). Picking a material drives Force/Speed/Blade/Passes via `applyMat()`. Settings panel (the gear) holds
the rest under a **Silhouette Settings** header: Force, Speed, Blade, Passes, Scale %, Units, Position. Heavy cardstock preset = force 33, speed 3,
blade 7, 2 passes.

## Current state (as of handoff)
- Full no-admin print-and-cut VALIDATED end-to-end on the Calibration Card:
  print artwork + marks → scan/register → cut outline → crease fold. Known-good.
- JBK colonial house (John Blair Kitchen): **blocked on Gina redrawing the design so
  every fold line is explicitly dashed** in the exported SVG (some folds currently
  export as solid red and get cut, splitting the model). Classifier + positioning
  are correct; the file just needs unambiguous fold lines.
- Open threads: adapt designs wider than the 8" (203 mm) Portrait width by re-nesting
  (no scaling); prepare a CAD Library entry (open SVG + metadata + instructions);
  a "Open from Library" linkage that fetches a design SVG by URL.

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
   **`PYTHONIOENCODING=utf-8` first** or it crashes printing `→` to the cp1252 console.
6. **CHECK PAGINATION before delivering — MANDATORY. This is how the defects get caught; skipping it is how
   they shipped.** Orphaned headings live in the PAGINATION, not the XML, so `validate.py` passes while the
   page looks wrong. No LibreOffice/poppler here and the Read tool can't rasterize a PDF either — instead drive
   **Word via COM**, which reports where each heading falls. Run the ready-made check:
   `powershell -NoProfile -File tools\docxcheck.ps1 "User Guide (Ver 4.1).docx"`
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
