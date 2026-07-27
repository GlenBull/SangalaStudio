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
$blankRuns = @(); $blankRun = 0; $blankPage = 0
$deepest = @{}                                   # page -> lowest content top seen (points), for underfilled-page detection
$forced = @{}                                    # page -> $true when a deliberate break STARTS that page
foreach ($p in $doc.Paragraphs) {
  try { if ($p.SpaceBeforeAuto -or $p.SpaceAfterAuto) { $auto++ } } catch {}
  $pg = $p.Range.Information($wdActiveEndPageNumber)
  if ($p.Range.Text.Trim().Length -gt 0) {
    $vp = $p.Range.Information($wdVerticalPositionRelativeToPage)
    if (-not $deepest.ContainsKey($pg) -or $vp -gt $deepest[$pg]) { $deepest[$pg] = $vp }
  }
  # Runs of consecutive EMPTY paragraphs are invisible vertical padding. They caused a 92 pt hole above
  # section 5 of the Tech Manual that no other check could see: the underfilled test measures the BOTTOM of
  # a page and the gap was interior, while each individual step was a normal ~30 pt. The tell is the blanks.
  $isBlank = ($p.Range.Text.Trim().Length -eq 0) -and (-not $p.Range.Information(12)) -and ($p.Range.InlineShapes.Count -eq 0)
  if ($isBlank) {
    if ($blankRun -eq 0) { $blankPage = $pg }
    $blankRun++
  } else {
    if ($blankRun -ge 2) {
      $bt = ($p.Range.Text -replace '\s+', ' ').Trim()
      if ($bt.Length -gt 44) { $bt = $bt.Substring(0, 44) + '...' }
      $blankRuns += ,@($blankPage, "page $blankPage : $blankRun blank paragraphs before '$bt'")
    }
    $blankRun = 0
  }

  # A page that ends short because the AUTHOR ended it there is not a defect. Two ways to say so in Word:
  # PageBreakBefore on the paragraph, or a manual break (Chr 12) inside it - the User Guide's Appendix A
  # heading uses the second, carrying <w:br w:type="page"/> as its first run so the appendix opens on a
  # fresh page. Without this, page 21 of Ver 8.2 reported ~6.6 in blank and withheld PAGINATION CLEAN
  # forever, for a break Glen put there on purpose. Record which page each deliberate break STARTS.
  #   PageBreakBefore -> the paragraph itself begins the new page, so ask where it STARTS.
  #   manual break    -> the break sits mid-paragraph and the text after it begins the new page, so the
  #                      page the paragraph ENDS on is the new one.
  try {
    if ($p.PageBreakBefore) {
      $fs = $p.Range.Duplicate; $fs.End = $fs.Start
      $forced[$fs.Information($wdActiveEndPageNumber)] = $true
    } elseif ($p.Range.Text.Contains([char]12)) {
      $forced[$pg] = $true
    }
  } catch {}

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

# Cover version vs filename. The cover carries a "Version X.Y" line that nothing updates on its own,
# so it silently drifts every time a new version is saved - it had gone five revisions stale before
# anyone noticed. Compare it with the (Ver X.Y) in the filename.
$hasCover = $doc.Sections(1).PageSetup.DifferentFirstPageHeaderFooter
$verMismatch = ''
$fileVer = ''
if ((Split-Path $full -Leaf) -match '\(Ver\s*([0-9.]+)\)') { $fileVer = $matches[1] }
if ($fileVer -ne '' -and $hasCover) {          # a document with no cover page has nothing to check
  $coverVer = ''
  foreach ($p in $doc.Paragraphs) {
    if ($p.Range.Information($wdActiveEndPageNumber) -gt 2) { break }
    if ($p.Range.Text -match 'Version\s+([0-9.]+)') { $coverVer = $matches[1]; break }
  }
  if ($coverVer -eq '') { $verMismatch = "no 'Version X.Y' line found on the cover (filename says $fileVer)" }
  elseif ($coverVer -ne $fileVer) { $verMismatch = "cover says Version $coverVer but the filename says $fileVer" }
}

$pages = $doc.ComputeStatistics(2)               # wdStatisticPages = 2
$usableBottom = $doc.PageSetup.PageHeight - $doc.PageSetup.BottomMargin
# A cover page is mostly white by design, so skip it. Detected by the first section carrying a
# title page, which is how the cover suppresses its own page number.
$firstContentPage = 1
if ($hasCover) { $firstContentPage = 2 }
$underfilled = @(); $byDesign = @()
for ($pg = $firstContentPage; $pg -lt $pages; $pg++) {   # every page BUT the cover and the last
  if ($deepest.ContainsKey($pg)) {
    $slack = $usableBottom - $deepest[$pg]
    if ($slack -gt 216) {
      $inches = [math]::Round($slack/72,1)
      if ($forced.ContainsKey($pg + 1)) {
        # The next page is started by a deliberate break, so nothing "overflowed" - the section ends here.
        # Reported for the record, but it does NOT withhold CLEAN: no edit to page $pg-1 could reclaim it.
        $byDesign += ("page $pg : ~$inches in blank, but page $($pg+1) is started by a deliberate page break - section ends here, nothing to fix")
      } else {
        $underfilled += ("page $pg : ~$inches in blank at the bottom - a few lines overflowed onto it; tighten page $($pg-1) to pull them back")
      }
    }
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
if ($byDesign.Count -gt 0) {
  Write-Output ("short pages BY DESIGN (deliberate page break follows - not counted against CLEAN): " + $byDesign.Count)
  $byDesign | ForEach-Object { Write-Output ("  = " + $_) }
}
# a cover page is padded with blanks on purpose, so ignore runs there
$blanks = @($blankRuns | Where-Object { $_[0] -ge $firstContentPage } | ForEach-Object { $_[1] })
Write-Output ("RUNS of blank paragraphs (invisible vertical gaps): " + $blanks.Count)
$blanks | ForEach-Object { Write-Output ("  _ " + $_) }
Write-Output ("FLOATING figures in text boxes - CHECK each still sits beside its narrative: " + $floats.Count)
$floats | ForEach-Object { Write-Output ("  ~ " + $_) }
if ($verMismatch -ne '') { Write-Output ("COVER VERSION: " + $verMismatch) }
if ($orphans.Count -eq 0 -and $noKeep.Count -eq 0 -and $underfilled.Count -eq 0 -and $verMismatch -eq '' -and $blanks.Count -eq 0) { Write-Output "PAGINATION CLEAN" }
if ($floats.Count -gt 0) { Write-Output "(the floating figures above still need a human eye - CLEAN does not cover them)" }
