# Sangala Studio — project guide for Claude Code

No-admin control of a **Silhouette Portrait 3/4** die cutter from a browser page
plus a tiny local helper. Prints Silhouette-standard registration marks, scans
them, and does a registered print-and-cut (cut outlines + creased/folded score
lines) for paper-craft designs exported to SVG from Silhouette Studio. Built for
schools: **no admin rights, no driver install, no Bluetooth, no extra hardware —
USB only, user-mode.** This constraint is absolute.

## Interaction / process (please follow)
- Be concise and direct. Cut any word that isn't needed. Minimal formatting; prose over bullet lists unless a list is clearly warranted.
- Do NOT use popup question dialogs. Ask inline in plain chat, one question at a time.
- Avoid the words "honest", "honestly", "genuinely", "straightforward".
- **One change at a time, then let the user test on the physical machine, then commit.** Do not batch many untested changes — that already cost a multi-hour unrecoverable break once. Commit (or tag) after each verified-good state so any regression is a `git diff` away, not a guess.
- Terminology: the machine is a **die cutter** / **Digital Fabrication Tool**. Always write the full term **"die cutter"** — never abbreviate or truncate to "cutter" (or use "cutting"). In schools the bare word "cutter" can evoke self-harm (a teen who slashes their arms); the full "die cutter" keeps the meaning unambiguous. Applies to UI text, code comments, and chat. Prefer **"Make It"** over "Cut It". Product = **Sangala Studio**; subtitle **Digital Fabrication Tool** (mixed case). Show the mat/page in inches as whole numbers.

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
- **SangalaServer.cs** — local helper. Loopback `TcpListener` (no admin/firewall),
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
(menu: Test square / Scan test / Manual align) · Setup. Green **Make it!** branches
on the Marks toggle: ON → register + cut (/printcut); OFF → plain cut (/cut).
Setup panel: Material (Paper/Cardstock/Heavy cardstock/Vinyl/Pen), Force, Speed,
Blade, Passes, Scale %, Units, Position. Heavy cardstock preset = force 33, speed 3,
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

## Gotcha
The project now lives in a plain (non-Dropbox) git checkout, so edit files
directly with the Write/Edit tools — no need to route saves through bash/python,
and Python is not installed here. (It formerly lived in a Dropbox-synced folder
that corrupted large saves with NUL bytes/truncation and dehydrated files to
cloud-only placeholders; that no longer applies.) A quick integrity glance after
big edits is still cheap: brace balance for .cs, file ends with </html>.
