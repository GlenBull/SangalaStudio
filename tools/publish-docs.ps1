# Keep the repository's documents and the shared Dropbox folder in step, in EITHER direction.
#
# Dropbox here is a business-licensed team account. AI Sandbox sits at the TOP level of it,
# deliberately, because that placement is what makes access control straightforward:
#   %USERPROFILE%\UVa Lab School Dropbox\AI Sandbox\...     (top level - this folder)
#   %USERPROFILE%\UVa Lab School Dropbox\Glen Bull\...      (Glen's own folder in the account)
#
# WHY TWO-WAY. An earlier version only pushed repo -> Dropbox. If a document was edited in the
# Dropbox copy - which happens, because that is where it is convenient to open it - a push would
# have silently overwritten the newer work, and the only remedy was to redo the edit by hand on
# the other side. This version records the hash of each file at the last successful sync, so it
# can tell WHICH side changed and move the file the right way. If both sides changed, it refuses
# to guess: it reports the conflict and changes nothing.
param([switch]$Apply)

$ErrorActionPreference = 'Stop'
$repo   = Split-Path -Parent $PSScriptRoot
$docs   = Join-Path $repo 'Documents'
$target = Join-Path $env:USERPROFILE 'UVa Lab School Dropbox\AI Sandbox\Design through Making\Sangala Studio Files'
$statef = Join-Path $PSScriptRoot '.publish-state.json'

# ---- what the testers get. Add a line here to sync something else. --------------------------
$managed = @(
    @{ Stem = 'User Guide';  From = $docs }      # newest "User Guide (Ver N.N).docx"
    @{ Stem = 'Tech Manual'; From = $docs }
    @{ Name = 'Update SangalaStudio.cmd';    From = $repo }
    @{ Name = 'Create Desktop Shortcut.cmd'; From = $repo }
)

function Get-Ver([string]$name) {
    if ($name -match '\(Ver\s+([0-9]+)\.([0-9]+)\)') { return [int]$matches[1] * 1000 + [int]$matches[2] }
    return 0
}
function Hash-Of($p) {
    if (-not (Test-Path $p)) { return $null }
    return (Get-FileHash $p -Algorithm SHA256).Hash
}
function Newest-Versioned($dir, $stem) {
    $f = Get-ChildItem -Path $dir -Filter "$stem (Ver *).docx" -File -ErrorAction SilentlyContinue |
         Sort-Object { Get-Ver $_.Name } -Descending
    if ($f) { return $f[0] } else { return $null }
}

$state = @{}
if (Test-Path $statef) {
    (Get-Content $statef -Raw | ConvertFrom-Json).PSObject.Properties |
        ForEach-Object { $state[$_.Name] = $_.Value }
}

Write-Host ""
Write-Host "  Repository : $repo"
Write-Host "  Dropbox    : $target"
if (-not $Apply) { Write-Host "  MODE       : preview only - nothing will be changed" }
Write-Host ""

if (-not (Test-Path $target)) {
    Write-Host "  The shared folder was not found."
    Write-Host "  Expected: $target"
    Write-Host "  Check that the AI Sandbox folder is synced to this PC."
    exit 1
}
$archive = Join-Path $target 'Archive'
$pushed = 0; $pulled = 0; $archived = 0; $same = 0; $conflicts = 0
$conflictNames = @()
$newstate = @{}

foreach ($item in $managed) {

    # ---- locate the file on each side ------------------------------------------------------
    if ($item.Stem) {
        $srcFile = Newest-Versioned $item.From $item.Stem
        $dstFile = Newest-Versioned $target    $item.Stem
        if (-not $srcFile -and -not $dstFile) { Write-Host "  MISSING    $($item.Stem) - on neither side"; continue }
        # a higher version number on either side wins outright
        $sv = if ($srcFile) { Get-Ver $srcFile.Name } else { -1 }
        $dv = if ($dstFile) { Get-Ver $dstFile.Name } else { -1 }
        if ($sv -ne $dv) {
            if ($sv -gt $dv) {
                Write-Host "  PUSH       $($srcFile.Name)   (newer version than Dropbox)"
                if ($Apply) {
                    if ($dstFile) {
                        if (-not (Test-Path $archive)) { New-Item -ItemType Directory $archive | Out-Null }
                        $to = Join-Path $archive $dstFile.Name
                        if (Test-Path $to) { Remove-Item $to -Force }
                        Move-Item $dstFile.FullName $to -Force
                        Write-Host "  ARCHIVE    $($dstFile.Name)  ->  Archive\"
                    }
                    Copy-Item $srcFile.FullName (Join-Path $target $srcFile.Name) -Force
                }
                if ($dstFile) { $archived++ }
                $pushed++
                $newstate[$srcFile.Name] = Hash-Of $srcFile.FullName
            } else {
                Write-Host "  PULL       $($dstFile.Name)   (newer version than the repository)"
                if ($Apply) { Copy-Item $dstFile.FullName (Join-Path $item.From $dstFile.Name) -Force }
                $pulled++
                $newstate[$dstFile.Name] = Hash-Of $dstFile.FullName
            }
            continue
        }
        $name = $srcFile.Name
        $src  = $srcFile.FullName
        $dst  = Join-Path $target $name
    } else {
        $name = $item.Name
        $src  = Join-Path $item.From $name
        $dst  = Join-Path $target $name
        if (-not (Test-Path $src)) { Write-Host "  MISSING    $name"; continue }
    }

    # ---- same version on both sides: decide by what changed since the last sync -------------
    $hs = Hash-Of $src
    $hd = Hash-Of $dst
    $last = $state[$name]

    if ($hd -eq $null) {
        Write-Host "  PUSH       $name   (not in Dropbox yet)"
        if ($Apply) { Copy-Item $src $dst -Force }
        $pushed++; $newstate[$name] = $hs
    }
    elseif ($hs -eq $hd) {
        Write-Host "  in step    $name"
        $same++; $newstate[$name] = $hs
    }
    elseif ($last -eq $null) {
        # never synced by this tool, so there is no record of who changed: fall back to time
        $sNewer = (Get-Item $src).LastWriteTime -gt (Get-Item $dst).LastWriteTime
        if ($sNewer) {
            Write-Host "  PUSH       $name   (differs; repository copy is newer - first sync, judged by time)"
            if ($Apply) { Copy-Item $src $dst -Force }
            $pushed++; $newstate[$name] = $hs
        } else {
            Write-Host "  PULL       $name   (differs; Dropbox copy is newer - first sync, judged by time)"
            if ($Apply) { Copy-Item $dst $src -Force }
            $pulled++; $newstate[$name] = $hd
        }
    }
    elseif ($hs -eq $last) {
        Write-Host "  PULL       $name   (edited in Dropbox)"
        if ($Apply) { Copy-Item $dst $src -Force }
        $pulled++; $newstate[$name] = $hd
    }
    elseif ($hd -eq $last) {
        Write-Host "  PUSH       $name   (edited in the repository)"
        if ($Apply) { Copy-Item $src $dst -Force }
        $pushed++; $newstate[$name] = $hs
    }
    else {
        Write-Host ""
        Write-Host "  CONFLICT   $name"
        Write-Host "             both copies changed since the last sync. Nothing was touched."
        Write-Host "             repository : $((Get-Item $src).LastWriteTime)  $((Get-Item $src).Length) bytes"
        Write-Host "             Dropbox    : $((Get-Item $dst).LastWriteTime)  $((Get-Item $dst).Length) bytes"
        Write-Host "             Merge them by hand, then run this again."
        Write-Host ""
        $conflicts++
        $conflictNames += $name
        $newstate[$name] = $last          # keep the old record so it stays flagged
    }
}

if ($Apply) { $newstate | ConvertTo-Json | Set-Content $statef -Encoding utf8 }

Write-Host ""
if ($Apply) {
    Write-Host "  Pushed $pushed, pulled $pulled, archived $archived, $same already in step, $conflicts conflict(s)."
} else {
    Write-Host "  Would push $pushed, pull $pulled, archive $archived. $same in step, $conflicts conflict(s)."
    Write-Host "  Run 'Sync with Dropbox.cmd' to do it."
}
if ($conflicts -gt 0) { Write-Host "  Resolve the conflict(s) above before relying on this." }
Write-Host ""

# ---- leave a record, because this also runs unattended from Task Scheduler -----------------
if ($Apply) {
    $stamp  = Get-Date -Format 'yyyy-MM-dd HH:mm'
    $logf   = Join-Path $PSScriptRoot 'sync-log.txt'
    $marker = Join-Path $repo 'SYNC CONFLICT.txt'
    Add-Content -Path $logf -Encoding utf8 -Value ("{0}  pushed {1}, pulled {2}, archived {3}, in step {4}, conflicts {5}" -f $stamp, $pushed, $pulled, $archived, $same, $conflicts)
    $lines = @(Get-Content $logf)
    if ($lines.Count -gt 500) { $lines[-500..-1] | Set-Content $logf -Encoding utf8 }

    # A conflict during an unattended run would otherwise be invisible. Drop a file where it
    # will be noticed, and clear it as soon as the conflict is resolved.
    if ($conflicts -gt 0) {
        $msg  = "Sangala document sync stopped on a conflict at $stamp.`r`n`r`n"
        $msg += "These files were edited BOTH in the repository and in the Dropbox folder since`r`n"
        $msg += "the last sync, so nothing was copied - copying either way would lose an edit:`r`n`r`n"
        foreach ($n in $conflictNames) { $msg += "    $n`r`n" }
        $msg += "`r`nOpen both copies, merge them by hand, then run 'Sync with Dropbox.cmd'.`r`n"
        $msg += "This file disappears once the conflict is cleared.`r`n"
        Set-Content -Path $marker -Value $msg -Encoding utf8
    } elseif (Test-Path $marker) {
        Remove-Item $marker -Force
    }
}
