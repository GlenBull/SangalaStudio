# Sangala Studio — no-admin die cutter control

Browser-based control for a Silhouette Portrait 3/4 die cutter over USB, with
**no admin rights, no driver install, no Bluetooth**. Prints registration marks,
scans them, and performs a registered print-and-cut (cut outlines + creased
folds) for paper-craft designs exported as SVG from Silhouette Studio.

## Source files
- **DieCutter.cs** — USB + GPGL engine. Opens the cutter via the usbprint.sys
  device interface (user-mode, no admin), converts SVG paths to GPGL, runs the
  registration scan, and cuts/scores.
- **SangalaServer.cs** — tiny local helper (loopback TcpListener, no admin/firewall)
  that serves the page and holds the USB connection. Endpoints: /connect /cut
  /scan /printcut /manualstart /jog /manualread /manualcut.
- **SangalaStudio.html** — browser UI: open SVG, classify cut/score, preview,
  Marks toggle, Print, Test menu, Make it.
- **Build SangalaStudio.cmd** — compiles the two .cs files with the in-box .NET
  compiler into SangalaStudio.exe (no install, no admin).
- **Calibration Card.svg** — simple test file (one cut rectangle + one fold line).

## Build & run
1. Run `Build SangalaStudio.cmd` (uses the .NET compiler already in Windows).
2. Keep `SangalaStudio.exe` next to `SangalaStudio.html`; double-click the exe.
3. Your browser opens the page; it drives the machine over USB.

## Conventions
- Silhouette-standard registration marks: 5 mm solid square + two L-brackets,
  15.9 mm inset, on an 8.5 x 11 (Letter) page.
- Cut vs fold is read from the SVG line style: **red solid unfilled = CUT**,
  **red dashed = SCORE/FOLD**, red filled + everything else = print (ignored).
  Every fold line must be explicitly dashed in the exported SVG.
- The optical eye sits ~30 mm right of the blade; the auto-scan search is shifted
  left to compensate (see ScanRegMarks eyeRightMm).
