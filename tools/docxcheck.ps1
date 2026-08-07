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
try { $doc = $w.Documents.Open($full, $false, $true) } catch { $doc = $null }   # ConfirmConversions=false, ReadOnly=true
# A document Word cannot open has no paragraphs, so every count below is zero and the script printed
# PAGINATION CLEAN over a file that would not open at all. Stop here instead.
if ($doc -eq $null) { $w.Quit(); Write-Output "CANNOT OPEN - Word refused the file; the XML is malformed. No check was run."; exit 1 }
$orphans = @(); $noKeep = @(); $auto = 0
$blankRuns = @(); $blankRun = 0; $blankPage = 0
$deepest = @{}                                   # page -> lowest content top seen (points), for underfilled-page detection
$forced = @{}                                    # page -> $true when a deliberate break STARTS that page
foreach ($p in $doc.Paragraphs) {
  try { if ($p.SpaceBeforeAuto -or $p.SpaceAfterAuto) { $auto++ } } catch {}
  $pg = $p.Range.Information($wdActiveEndPageNumber)
  if ($p.Range.Text.Trim().Length -gt 0) {
    # Measure the BOTTOM of the paragraph's LAST line, not the top of its first.
    # Information(wdVerticalPositionRelativeToPage) on a whole paragraph returns the top of its
    # bounding rectangle, so a page ending in a long paragraph used to report everything below that
    # paragraph's first line as blank - Chapter 5 page 8 read as 3.6 in empty when it holds ~1.9.
    # A collapsed range just before the paragraph mark sits on the LAST line; add one line's height.
    $rEnd = $p.Range.Duplicate
    $rEnd.SetRange($p.Range.End - 1, $p.Range.End - 1)
    $pgEnd = $rEnd.Information($wdActiveEndPageNumber)
    $top   = $rEnd.Information($wdVerticalPositionRelativeToPage)
    $h = 14                                        # a plain line, when nothing better is known
    try { $fs = $p.Range.Font.Size; if ($fs -gt 1 -and $fs -lt 200) { $h = $fs * 1.25 } } catch {}
    try { if ($p.Range.InlineShapes.Count -gt 0) {  # an image paragraph is as tall as its picture
            $ih = $p.Range.InlineShapes.Item(1).Height; if ($ih -gt $h) { $h = $ih } } } catch {}
    $bottom = $top + $h
    if (-not $deepest.ContainsKey($pgEnd) -or $bottom -gt $deepest[$pgEnd]) { $deepest[$pgEnd] = $bottom }
    # A paragraph whose text WRAPS across a page fills every page it crosses, so those pages are not
    # short. But a paragraph carrying a manual break (Chr 12) also spans two pages without filling the
    # first - that is exactly how the User Guide opens each appendix - so exclude it, or the deliberate
    # short page before an appendix is silently marked full and stops being reported at all.
    if (-not $p.Range.Text.Contains([char]12)) {
      $rStart = $p.Range.Duplicate; $rStart.Collapse(1)
      $pgStart = $rStart.Information($wdActiveEndPageNumber)
      if ($pgEnd -gt $pgStart) {
        for ($sp = $pgStart; $sp -lt $pgEnd; $sp++) { $deepest[$sp] = [double]::MaxValue }
      }
    }
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

$hasCover = $doc.Sections(1).PageSetup.DifferentFirstPageHeaderFooter
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
# PAGE NUMBERS. Any document longer than one page carries one, bottom center (Glen, 2026-08-05).
# A one-page document is exempt, so the count decides. Look for a PAGE field rather than text: a
# literal "2" typed into a footer looks right on page 2 and wrong everywhere else.
$wdHeaderFooterPrimary = 1
$wdFieldPage = 33
$pageNumState = "n/a (one page)"
$pageNumBad = $false
if ($pages -gt 1) {
  $hasField = $false; $centered = $false
  foreach ($sec in $doc.Sections) {
    try {
      $f = $sec.Footers.Item($wdHeaderFooterPrimary)
      foreach ($fld in $f.Range.Fields) {
        if ($fld.Type -eq $wdFieldPage) {
          $hasField = $true
          try { if ($fld.Code.Paragraphs(1).Alignment -eq 1) { $centered = $true } } catch {}
        }
      }
    } catch {}
  }
  if (-not $hasField) { $pageNumState = "MISSING - $pages pages and no PAGE field in the footer"; $pageNumBad = $true }
  elseif (-not $centered) { $pageNumState = "present but NOT centered - move it to the bottom center"; $pageNumBad = $true }
  else { $pageNumState = "present, bottom center" }
}
# PAGE FILL. The UNDERFILLED gate above only speaks when a page is more than 3 in short, and it skips
# the last page - so it passed a concept draft whose page 2 was 1.5 in short and visibly half empty,
# and Glen found it rather than the script. This reports the same measurement UNCONDITIONALLY, for
# every page including the last, so a gap that is real but under the gate is still visible. It does
# NOT withhold CLEAN: a short page is often a section ending, and only a person can tell.
$fill = @()
$fullPages = 0
for ($pg = $firstContentPage; $pg -le $pages; $pg++) {
  if (-not $deepest.ContainsKey($pg)) { continue }
  if ($deepest[$pg] -eq [double]::MaxValue) { $fullPages++; continue }
  $slack = $usableBottom - $deepest[$pg]
  if ($slack -gt 72) {
    $note = ""
    if ($pg -eq $pages) { $note = "  (last page - normal)" }
    elseif ($forced.ContainsKey($pg + 1)) { $note = "  (deliberate break follows)" }
    $fill += ("page {0}: {1} in blank{2}" -f $pg, [math]::Round($slack/72,1), $note)
  } else { $fullPages++ }
}

$doc.Close($false); $w.Quit()
Write-Output ("pages: " + $pages)
Write-Output ("PAGE FILL - pages more than 1 in short (informational, does NOT withhold CLEAN): " + $fill.Count + " of " + $pages)
$fill | ForEach-Object { Write-Output ("  . " + $_) }
Write-Output ("page numbers: " + $pageNumState)
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
if ($orphans.Count -eq 0 -and $noKeep.Count -eq 0 -and $underfilled.Count -eq 0 -and $blanks.Count -eq 0 -and (-not $pageNumBad)) { Write-Output "PAGINATION CLEAN" }
if ($floats.Count -gt 0) { Write-Output "(the floating figures above still need a human eye - CLEAN does not cover them)" }
