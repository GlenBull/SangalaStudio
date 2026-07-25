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
      # Compare the heading's page with the page its text BEGINS on. Information() reports the page a
      # range ENDS on, so asking the whole next paragraph flags any paragraph that merely spills over
      # the break - which is a false alarm, and cost three bogus reports on Ver 5.8. Collapse to the start.
      $ns = $nx.Range.Duplicate; $ns.End = $ns.Start
      $np = $ns.Information($wdActiveEndPageNumber)
      if ($pg -ne $np) { $orphans += ("p$pg -> p$np  $txt") }   # heading stranded: its text starts on the next page
    }
  }
}
# Floating figures in text boxes. Glen anchors a figure + its caption in a text box and wraps text
# around it, to keep the pair together and use the space beside a list. That is deliberate, not a
# defect - but the box floats, so a revision that adds or removes narrative can leave it stranded
# beside the wrong text. This cannot be judged mechanically, so report it for eyes every run.
$floats = @()
foreach ($s in $doc.Shapes) {
  try {
    $cap = ''
    if ($s.TextFrame.HasText) { $cap = ($s.TextFrame.TextRange.Text -replace '\s+', ' ').Trim() }
    $a = $s.Anchor
    $apg = $a.Information($wdActiveEndPageNumber)
    $atx = ($a.Paragraphs(1).Range.Text -replace '\s+', ' ').Trim()
    if ($atx.Length -gt 58) { $atx = $atx.Substring(0, 58) + '...' }
    if ($cap.Length -gt 58) { $cap = $cap.Substring(0, 58) + '...' }
    $floats += ("p$apg  box: $cap`n        anchored to: $atx")
  } catch {}
}

$pages = $doc.ComputeStatistics(2)               # wdStatisticPages = 2
$usableBottom = $doc.PageSetup.PageHeight - $doc.PageSetup.BottomMargin
# A cover page is mostly white by design, so skip it. Detected by the first section carrying a
# title page, which is how the cover suppresses its own page number.
$firstContentPage = 1
if ($doc.Sections(1).PageSetup.DifferentFirstPageHeaderFooter) { $firstContentPage = 2 }
$underfilled = @()
for ($pg = $firstContentPage; $pg -lt $pages; $pg++) {   # every page BUT the cover and the last
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
Write-Output ("FLOATING figures in text boxes - CHECK each still sits beside its narrative: " + $floats.Count)
$floats | ForEach-Object { Write-Output ("  ~ " + $_) }
if ($orphans.Count -eq 0 -and $noKeep.Count -eq 0 -and $underfilled.Count -eq 0) { Write-Output "PAGINATION CLEAN" }
if ($floats.Count -gt 0) { Write-Output "(the floating figures above still need a human eye - CLEAN does not cover them)" }
