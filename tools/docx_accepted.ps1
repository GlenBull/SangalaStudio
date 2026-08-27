# Measure the proposal with every tracked change ACCEPTED, on a throwaway copy.
# try/finally so Word can never be left running.
$ErrorActionPreference = "Continue"
$dir  = "C:\Users\glenb\AppData\Local\Temp\claude\D--Code-Projects-Silhouette-Tools\4e8d3fb8-b024-4ca7-95b5-722897c4085c\scratchpad"
$src  = Join-Path $dir "CAD Design via LEGO Bricks (Ver 1.1).docx"
$copy = Join-Path $dir "_probe.docx"
Copy-Item $src $copy -Force
$word = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $a = $word.Documents.Open($copy)
    $a.Revisions.AcceptAll()
    $a.Repaginate()
    Write-Output ("ACCEPTED -> pages {0}   words {1}" -f $a.ComputeStatistics(2), $a.ComputeStatistics(0))
    $PAGE = 3; $VPOS = 6
    $ps = $a.PageSetup
    Write-Output ("text area: {0} to {1} pt" -f $ps.TopMargin, ($ps.PageHeight - $ps.BottomMargin))
    $i = 0
    foreach ($p in $a.Paragraphs) {
        $i++
        $r = $p.Range; $t = $r.Text.Trim()
        $endR = $a.Range($r.End - 1, $r.End)
        $label = if ($t.Length -eq 0) { "[image/blank]" } else { $t.Substring(0, [Math]::Min(44, $t.Length)) }
        Write-Output ("  p{0,-3} pg{1}  top {2,6:N1}  bot {3,6:N1}  {4}" -f $i, $r.Information($PAGE), $r.Information($VPOS), $endR.Information($VPOS), $label)
    }
    $a.Close($false)
} catch {
    Write-Output ("ERROR: " + $_.Exception.Message.Trim())
} finally {
    if ($word) { try { $word.Quit() } catch {}
                 try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null } catch {} }
    Remove-Item $copy -Force -ErrorAction SilentlyContinue
}
