# docxcheck.ps1 - pre-delivery pagination check for the User Guide / Tech Manual.
# These defects (orphaned headings, autospacing gaps) live in the PAGINATION, not the XML, so validate.py
# passes while the page looks wrong. There is no LibreOffice/poppler on this machine, so we drive Word via COM
# (read-only, so it works even while the doc is open) and ask Word itself where each heading falls.
# Usage:  powershell -NoProfile -File tools\docxcheck.ps1 "Documents\User Guide (Ver 4.3).docx"
param([Parameter(Mandatory=$true)][string]$Path)
$wdActiveEndPageNumber = 3
$wdVerticalPositionRelativeToPage = 6
$full = (Resolve-Path $Path).Path
$w = New-Object -ComObject Word.Application; $w.Visible = $false
$doc = $w.Documents.Open($full, $false, $true)   # ConfirmConversions=false, ReadOnly=true
$orphans = @(); $noKeep = @(); $auto = 0
$deepest = @{}                                   # page -> lowest content top seen (points), for underfilled-page detection
foreach ($p in $doc.Paragraphs) {
  try { if ($p.SpaceBeforeAuto -or $p.SpaceAfterAuto) { $auto++ } } catch {}
  $pg = $p.Range.Information($wdActiveEndPageNumber)
  if ($p.Range.Text.Trim().Length -gt 0) {
    $vp = $p.Range.Information($wdVerticalPositionRelativeToPage)
    if (-not $deepest.ContainsKey($pg) -or $vp -gt $deepest[$pg]) { $deepest[$pg] = $vp }
  }
  $st = $p.Style.NameLocal
  if ($st -like 'Heading*') {
    $txt = $p.Range.Text.Trim()
    if (-not $p.KeepWithNext) { $noKeep += $txt }
    $nx = $p.Next()
    if ($nx -ne $null) {
      $np = $nx.Range.Information($wdActiveEndPageNumber)
      if ($pg -ne $np) { $orphans += ("p$pg -> p$np  $txt") }   # heading and its first line split across a page break
    }
  }
}
$pages = $doc.ComputeStatistics(2)               # wdStatisticPages = 2
$usableBottom = $doc.PageSetup.PageHeight - $doc.PageSetup.BottomMargin
$underfilled = @()
for ($pg = 1; $pg -lt $pages; $pg++) {           # every page BUT the last
  if ($deepest.ContainsKey($pg)) {
    $slack = $usableBottom - $deepest[$pg]
    if ($slack -gt 216) { $underfilled += ("page $pg : ~$([math]::Round($slack/72,1)) in blank at the bottom - a few lines overflowed onto it; tighten page $($pg-1) to pull them back") }
  }
}
$doc.Close($false); $w.Quit()
Write-Output ("autospacing paragraphs (never ADD more): " + $auto)
Write-Output ("headings lacking keepNext (fix - they can orphan): " + $noKeep.Count)
$noKeep | ForEach-Object { Write-Output ("  - " + $_) }
Write-Output ("ORPHANED headings right now: " + $orphans.Count)
$orphans | ForEach-Object { Write-Output ("  ! " + $_) }
Write-Output ("UNDERFILLED pages (content spills, leaving a near-empty page) - review each: " + $underfilled.Count)
$underfilled | ForEach-Object { Write-Output ("  ? " + $_) }
if ($orphans.Count -eq 0 -and $noKeep.Count -eq 0 -and $underfilled.Count -eq 0) { Write-Output "PAGINATION CLEAN" }
