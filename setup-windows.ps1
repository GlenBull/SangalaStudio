<#
.SYNOPSIS
  One-shot, re-runnable setup of the Windows toolchain that lets Claude Code read,
  edit, and render the "Design through Making" Word chapters at full fidelity
  (text + images), with no Cowork round-trips.

  Prefers user-scope winget and portable / no-admin installs. Safe to re-run.
  Ends with a docx image round-trip verification against a committed test fixture
  (never touches the real chapter files).

.PARAMETER VerifyOnly
  Skip installation and just run the verification round-trip.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\setup-windows.ps1
  powershell -ExecutionPolicy Bypass -File .\setup-windows.ps1 -VerifyOnly

.NOTES
  What it installs:
    - Python 3.12 (winget, user scope) + pip: defusedxml, lxml (the docx skill's
      unpack/pack XML engine) and pymupdf (PDF -> image rasterizer, no Poppler needed)
    - pandoc (winget, user scope) - Word text extraction
    - Node (portable zip) + the `docx` npm package - create brand-new .docx
    - Poppler (portable zip) - pdftoppm, so the Read tool's own PDF view also works
    - LibreOffice (best effort; optional) - only needed for legacy .doc or machines
      without MS Word. Skipped with a warning if it needs admin.
  Also sets PYTHONUTF8=1 (user env) so the skill scripts don't hit Windows cp1252
  codec crashes on UTF-8 XML.

  Rendering uses MS Word if present (ExportAsFixedFormat -> PDF), else LibreOffice.
#>
param([switch]$VerifyOnly)

$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}

$Tools       = Join-Path $env:LOCALAPPDATA 'SangalaTools'   # portable tools live here (not in the repo)
$NodeVersion = 'v22.11.0'     # bump as needed: https://nodejs.org/dist/
$PopplerRel  = 'v24.08.0-0'   # bump as needed: https://github.com/oschwartz10612/poppler-windows/releases

function Info($m){ Write-Host "==> $m" -ForegroundColor Cyan }
function Ok($m){   Write-Host "  OK  $m" -ForegroundColor Green }
function Warn($m){ Write-Host "  !!  $m" -ForegroundColor Yellow }
function Have($c){ [bool](Get-Command $c -ErrorAction SilentlyContinue) }
function RefreshPath {
  $env:PATH = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' +
              [Environment]::GetEnvironmentVariable('Path','User')
}
function Add-UserPath($dir){
  if (-not (Test-Path $dir)) { return }
  $u = [Environment]::GetEnvironmentVariable('Path','User'); if (-not $u) { $u = '' }
  if (($u -split ';') -notcontains $dir) {
    [Environment]::SetEnvironmentVariable('Path', ($u.TrimEnd(';') + ';' + $dir), 'User')
    Ok "added to user PATH: $dir"
  }
  if (($env:PATH -split ';') -notcontains $dir) { $env:PATH = $env:PATH + ';' + $dir }
}
function Winget-Install($id, [switch]$User){
  $a = @('install','-e','--id',$id,'--accept-source-agreements','--accept-package-agreements','--disable-interactivity')
  if ($User) { $a += @('--scope','user') }
  & winget @a
}
function Get-Zip($url, $zipPath){
  Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing
}

function Install-PythonPandoc {
  RefreshPath
  if (Have python) { Ok 'python present' }
  else { Info 'installing Python 3.12 (user scope)'; Winget-Install 'Python.Python.3.12' -User; RefreshPath }
  if (-not (Have python)) { throw 'Python install failed - install Python 3.12 manually and re-run.' }

  if (Have pandoc) { Ok 'pandoc present' }
  else { Info 'installing pandoc (user scope)'; Winget-Install 'JohnMacFarlane.Pandoc' -User; RefreshPath }
  if (-not (Have pandoc)) { Warn 'pandoc not found after install - text extraction may not work.' }
}

function Install-PyDeps {
  Info 'installing Python packages: defusedxml, lxml, pymupdf'
  & python -m pip install --quiet --upgrade pip
  & python -m pip install --quiet defusedxml lxml pymupdf
  if ($LASTEXITCODE -ne 0) { throw 'pip install failed.' }
  Ok 'python packages installed'
  [Environment]::SetEnvironmentVariable('PYTHONUTF8','1','User'); $env:PYTHONUTF8 = '1'
  Ok 'PYTHONUTF8=1 set (user env) - avoids Windows cp1252 codec crashes in the skill'
}

function Install-Node {
  if (Have node) { Ok 'node present' }
  else {
    Info "installing portable Node $NodeVersion (no admin)"
    $nz  = "node-$NodeVersion-win-x64"
    $url = "https://nodejs.org/dist/$NodeVersion/$nz.zip"
    $zip = Join-Path $env:TEMP "$nz.zip"
    try {
      Get-Zip $url $zip
      New-Item -ItemType Directory -Force $Tools | Out-Null
      Expand-Archive -Path $zip -DestinationPath $Tools -Force   # -> $Tools\node-<ver>-win-x64
      Add-UserPath (Join-Path $Tools $nz)
      RefreshPath
    } catch { Warn "Node download failed ($url): $($_.Exception.Message). Install Node LTS manually." }
  }
  if (Have npm) {
    Info 'installing the docx npm package (global)'
    & npm install -g docx --silent
    if ($LASTEXITCODE -eq 0) { Ok 'docx npm package installed' } else { Warn 'npm install docx failed.' }
  } else { Warn 'npm not found - skipping docx package. Later run:  npm install -g docx' }
}

function Install-Poppler {
  if (Have pdftoppm) { Ok 'poppler (pdftoppm) present'; return }
  Info "installing portable Poppler $PopplerRel (no admin)"
  $asset = "Release-$($PopplerRel.TrimStart('v')).zip"
  $url   = "https://github.com/oschwartz10612/poppler-windows/releases/download/$PopplerRel/$asset"
  $zip   = Join-Path $env:TEMP $asset
  $dest  = Join-Path $Tools 'poppler'
  try {
    Get-Zip $url $zip
    New-Item -ItemType Directory -Force $dest | Out-Null
    Expand-Archive -Path $zip -DestinationPath $dest -Force
    $bin = Get-ChildItem $dest -Recurse -Filter 'pdftoppm.exe' | Select-Object -First 1
    if ($bin) { Add-UserPath $bin.Directory.FullName; RefreshPath; Ok 'poppler installed' }
    else { Warn 'pdftoppm.exe not found in the Poppler zip.' }
  } catch { Warn "Poppler download failed ($url): $($_.Exception.Message). Optional - PyMuPDF already rasterizes PDFs." }
}

function Install-LibreOffice {
  if (Have soffice) { Ok 'LibreOffice present'; return }
  Info 'installing LibreOffice (optional; may require admin)'
  try { Winget-Install 'TheDocumentFoundation.LibreOffice'; RefreshPath } catch {}
  if (Have soffice) { Ok 'LibreOffice installed' }
  else { Warn 'LibreOffice not installed (no user-scope installer; needs admin). Optional: only for legacy .doc conversion or machines without MS Word. Install portable LibreOffice by hand if you need it.' }
}

function Verify {
  Info 'VERIFICATION: docx image round-trip'
  RefreshPath; $env:PYTHONUTF8 = '1'
  $fixture = Join-Path $PSScriptRoot 'setup\roundtrip-fixture.docx'
  if (-not (Test-Path $fixture)) { throw "test fixture missing: $fixture" }

  foreach ($c in 'python','pandoc','node','pdftoppm') {
    if (Have $c) { Ok "$c on PATH" } else { Warn "$c NOT on PATH" }
  }
  & python -c "import fitz, lxml, defusedxml; print('  OK  python deps import: pymupdf/lxml/defusedxml')"
  if ($LASTEXITCODE -ne 0) { throw 'python deps missing (pymupdf/lxml/defusedxml).' }

  $vtmp = Join-Path $env:TEMP ('sangala-verify-' + [Guid]::NewGuid().ToString('N').Substring(0,8))
  New-Item -ItemType Directory -Force $vtmp | Out-Null
  $src     = Join-Path $vtmp 'in.docx';  Copy-Item $fixture $src -Force
  $outdocx = Join-Path $vtmp 'out.docx'
  $marker  = Join-Path $vtmp 'marker.png'
  $pdf     = Join-Path $vtmp 'out.pdf'
  $page    = Join-Path $vtmp 'page1.png'

  # marker image (obviously different from the fixture image)
  Add-Type -AssemblyName System.Drawing
  $bmp = New-Object System.Drawing.Bitmap 460,220
  $g = [System.Drawing.Graphics]::FromImage($bmp); $g.Clear([System.Drawing.Color]::FromArgb(210,45,45))
  $g.SmoothingMode = 'AntiAlias'; $g.TextRenderingHint = 'AntiAlias'
  $f = New-Object System.Drawing.Font('Arial',30,[System.Drawing.FontStyle]::Bold)
  $g.DrawString("ROUND-TRIP OK",$f,[System.Drawing.Brushes]::White,24,90); $g.Dispose()
  $bmp.Save($marker,[System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()

  # replace the fixture's embedded image, repack, assert byte-for-byte round-trip
  & python (Join-Path $PSScriptRoot 'setup\roundtrip.py') $src $marker $outdocx
  if ($LASTEXITCODE -ne 0) { throw 'image round-trip through docx repack failed.' }

  # render out.docx -> PDF via MS Word, else LibreOffice
  $rendered = $false
  try {
    $w = New-Object -ComObject Word.Application
    try {
      $w.Visible = $false; $w.DisplayAlerts = 0
      $d = $w.Documents.Open([string]$outdocx, $false, $true)   # ReadOnly
      $d.ExportAsFixedFormat([string]$pdf, 17)                  # 17 = wdExportFormatPDF
      $d.Close($false); $rendered = $true
    } finally { $w.Quit(); [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null }
    Ok 'rendered via MS Word'
  } catch { Warn "Word render unavailable: $($_.Exception.Message)" }
  if (-not $rendered -and (Have soffice)) {
    & soffice --headless --convert-to pdf --outdir $vtmp $outdocx | Out-Null
    if (Test-Path $pdf) { $rendered = $true; Ok 'rendered via LibreOffice' }
  }
  if (-not $rendered) { throw 'no renderer available (need MS Word or LibreOffice).' }

  # rasterize page 1 and sanity-check it is not blank
  & python (Join-Path $PSScriptRoot 'setup\rasterize.py') $pdf $page
  if ($LASTEXITCODE -ne 0) { throw 'PDF rasterize failed.' }
  $sz = (Get-Item $page).Length
  if ($sz -lt 3000) { throw "rendered page too small ($sz bytes) - render likely blank." }
  Ok "rendered page raster OK ($sz bytes) -> $page"

  Write-Host ''
  Write-Host 'VERIFICATION PASSED - read / edit / render toolchain works end to end.' -ForegroundColor Green
}

# ---- main ----
if ($VerifyOnly) { Verify; return }

Info 'Sangala Windows toolchain setup (user-scope / no-admin preferred)'
if (-not (Have winget)) { throw "winget not found. Install 'App Installer' from the Microsoft Store, then re-run." }
New-Item -ItemType Directory -Force $Tools | Out-Null
Install-PythonPandoc
Install-PyDeps
Install-Node
Install-Poppler
Install-LibreOffice
Verify
Write-Host ''
Write-Host 'Setup complete. Open a NEW terminal so PATH changes take effect.' -ForegroundColor Green
