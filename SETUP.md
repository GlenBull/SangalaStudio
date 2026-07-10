# Setup — new Windows machine

This gets a fresh Windows PC ready to use **Claude Code** on this repo, including
reading and editing the "Design through Making" Word chapters at full fidelity
(text + images) with no Cowork round-trips.

## Steps

1. **Install Claude Code.**
   Follow the current instructions at <https://claude.com/claude-code>. Verify with:
   ```
   claude --version
   ```

2. **Clone this repo.**
   ```
   git clone https://github.com/GlenBull/SangalaStudio.git
   cd SangalaStudio
   ```

3. **Run the toolchain setup script.**
   ```
   powershell -ExecutionPolicy Bypass -File .\setup-windows.ps1
   ```
   It installs (user-scope / no-admin where possible): Python + pandoc, the Python
   packages the docx skill needs (`defusedxml`, `lxml`, `pymupdf`), portable Node +
   the `docx` npm package, and portable Poppler. It sets `PYTHONUTF8=1`. LibreOffice
   is attempted but **optional** — it only matters for legacy `.doc` files or a
   machine without MS Word, and it's skipped with a warning if it would need admin.
   The script ends by running a **docx image round-trip verification** and prints
   `VERIFICATION PASSED` when the chain works.

   - Re-runnable and idempotent — safe to run again anytime.
   - Re-run just the check with: `powershell -ExecutionPolicy Bypass -File .\setup-windows.ps1 -VerifyOnly`
   - **Open a new terminal afterward** so the PATH changes take effect.

4. **Make the Word chapters available offline.**
   The chapters live in Dropbox under `AI Sandbox\Design through Making\`. In the
   Dropbox app (or File Explorer), right-click that folder → **"Make available
   offline"** (a.k.a. Available offline) so the `.docx` are real local files, not
   online-only placeholders. Note the local path — on the reference machine it is:
   ```
   C:\Users\<you>\UVa Lab School Dropbox\AI Sandbox
   ```
   (The Dropbox root folder name may differ on your machine.)

5. **Point Claude Code at that folder (once).**
   Add the AI Sandbox path to `permissions.additionalDirectories` in
   `.claude/settings.local.json` (this file is git-ignored — machine-specific paths
   live here, never in the committed `settings.json`). Example:
   ```json
   {
     "permissions": {
       "additionalDirectories": [
         "C:/Users/<you>/UVa Lab School Dropbox/AI Sandbox"
       ]
     }
   }
   ```
   Now Claude can read and write the chapters directly, without per-file prompts.

## How the toolchain is used

- **Read a chapter:** `pandoc` extracts text; the docx skill's `unpack.py` extracts
  the raw XML + `word/media/` images (which Claude reads directly).
- **Edit a chapter:** unpack → edit the XML / swap an image → `pack.py` repacks and
  validates. **Always on a copy in a temp folder — never the live chapter file**
  until the result is approved.
- **Render to check layout:** MS Word (`ExportAsFixedFormat` → PDF) if present, else
  LibreOffice; then **PyMuPDF** rasterizes the PDF to page images. No admin needed.
- **Create a new document:** the Node `docx` package.

## What lives where (config)

- **`.claude/settings.json`** (committed) — portable permission rules that are the
  same on any machine (git commands, running the setup script, the toolchain CLIs).
- **`.claude/settings.local.json`** (git-ignored) — machine-specific absolute paths,
  including the AI Sandbox `additionalDirectories` entry.

## Notes / gotchas

- **`PYTHONUTF8=1` is required.** Without it, the skill's Python scripts crash on
  Windows' legacy cp1252 codec when reading UTF-8 XML. The setup script sets it as a
  user env var; open a new terminal after setup.
- **Poppler / LibreOffice are optional.** PyMuPDF handles PDF rasterizing and MS Word
  handles rendering, so the core read/edit/render path needs neither. Poppler just
  also lets the Read tool's own PDF view work; LibreOffice is for legacy `.doc` and
  no-Word machines.
- **Portable tools** (Node, Poppler) install under `%LOCALAPPDATA%\SangalaTools` and
  are added to your user PATH — nothing goes into the repo.
