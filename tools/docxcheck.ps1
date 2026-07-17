# docxcheck.ps1 - pre-delivery pagination check for the User Guide / Tech Manual.
# These defects (orphaned headings, autospacing gaps) live in the PAGINATION, not the XML, so validate.py
# passes while the page looks wrong. There is no LibreOffice/poppler on this machine, so we drive Word via COM
# (read-only, so it works even while the doc is open) and ask Word itself where each heading falls.
# Usage:  powershell -NoProfile -File tools\docxcheck.ps1 "User Guide (Ver 4.1).docx"
param([Parameter(Mandatory=$true)][string]$Path)
$wdActiveEndPageNumber = 3
$full = (Resolve-Path $Path).Path
$w = New-Object -ComObject Word.Application; $w.Visible = $false
$doc = $w.Documents.Open($full, $false, $true)   # ConfirmConversions=false, ReadOnly=true
$orphans = @(); $noKeep = @(); $auto = 0
foreach ($p in $doc.Paragraphs) {
  try { if ($p.SpaceBeforeAuto -or $p.SpaceAfterAuto) { $auto++ } } catch {}
  $st = $p.Style.NameLocal
  if ($st -like 'Heading*') {
    $txt = $p.Range.Text.Trim()
    if (-not $p.KeepWithNext) { $noKeep += $txt }
    $hp = $p.Range.Information($wdActiveEndPageNumber)
    $nx = $p.Next()
    if ($nx -ne $null) {
      $np = $nx.Range.Information($wdActiveEndPageNumber)
      if ($hp -ne $np) { $orphans += ("p$hp -> p$np  $txt") }   # heading and its first line split across a page break
    }
  }
}
$doc.Close($false); $w.Quit()
Write-Output ("autospacing paragraphs (never ADD more): " + $auto)
Write-Output ("headings lacking keepNext (fix - they can orphan): " + $noKeep.Count)
$noKeep | ForEach-Object { Write-Output ("  - " + $_) }
Write-Output ("ORPHANED headings right now: " + $orphans.Count)
$orphans | ForEach-Object { Write-Output ("  ! " + $_) }
if ($orphans.Count -eq 0 -and $noKeep.Count -eq 0) { Write-Output "PAGINATION CLEAN" }
