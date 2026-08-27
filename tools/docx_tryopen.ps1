# Try to open each .docx named on the command line; always quit Word, even on failure.
$ErrorActionPreference = "Continue"
$word = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    foreach ($f in $args) {
        if (-not (Test-Path $f)) { Write-Output ("MISSING  " + $f); continue }
        try {
            $d = $word.Documents.Open($f, $false, $true)
            $rev = $d.Revisions.Count
            Write-Output ("OK       {0}  pages {1}  words {2}  revisions {3}" -f (Split-Path $f -Leaf), $d.ComputeStatistics(2), $d.ComputeStatistics(0), $rev)
            $d.Close($false)
        } catch {
            Write-Output ("CORRUPT  {0}  -- {1}" -f (Split-Path $f -Leaf), $_.Exception.Message.Trim())
        }
    }
} finally {
    if ($word) {
        try { $word.Quit() } catch {}
        try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null } catch {}
    }
}
