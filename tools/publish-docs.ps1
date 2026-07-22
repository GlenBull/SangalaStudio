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
param(
    [switch]$Apply,
    # Called from the post-commit hook. Documents move only when their VERSION NUMBER changes,
    # which is the rule Glen asked for: a revision gets a new version number by convention, so
    # the version is the signal that there is something new for the testers. Same-version edits
    # are left for the manual two-way sync, which can tell which side changed. Runs quiet: it
    # prints only when it does something, because it speaks after every commit.
    [switch]$OnCommit
)
if ($OnCommit) { $Apply = $true }

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
# A .docx is a ZIP, and Word rewrites bookkeeping on every save - revision ids, timestamps,
# the rsid table in settings.xml, docProps. Two files that read identically therefore hash
# differently if they were saved at different moments. Hashing the whole file asks "are these
# the same FILE", when what matters is "are these the same DOCUMENT". So: fingerprint only the
# parts that carry content, with Word's revision noise stripped out.
Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue

function Get-ContentHash($p) {
    if (-not (Test-Path $p)) { return $null }
    if ([IO.Path]::GetExtension($p) -ne '.docx') { return (Get-FileHash $p -Algorithm SHA256).Hash }
    $sha = [Security.Cryptography.SHA256]::Create()
    $sb  = New-Object Text.StringBuilder
    $zip = $null
    try {
        $zip = [IO.Compression.ZipFile]::OpenRead($p)
        $parts = $zip.Entries | Where-Object {
            $_.FullName -eq 'word/document.xml' -or
            $_.FullName -like 'word/header*.xml' -or
            $_.FullName -like 'word/footer*.xml' -or
            $_.FullName -like 'word/media/*'     -or
            @('word/footnotes.xml','word/endnotes.xml','word/styles.xml','word/numbering.xml') -contains $_.FullName
        } | Sort-Object FullName
        foreach ($e in $parts) {
            $ms = New-Object IO.MemoryStream
            $st = $e.Open(); $st.CopyTo($ms); $st.Close()
            $bytes = $ms.ToArray(); $ms.Dispose()
            if ($e.FullName -like '*.xml') {
                $txt = [Text.Encoding]::UTF8.GetString($bytes)
                $txt = [Regex]::Replace($txt, '\s+w:rsid[A-Za-z]*="[^"]*"', '')
                $txt = [Regex]::Replace($txt, '\s+w14:(paraId|textId)="[^"]*"', '')
                $bytes = [Text.Encoding]::UTF8.GetBytes($txt)
            }
            [void]$sb.Append($e.FullName).Append('=')
            [void]$sb.Append([BitConverter]::ToString($sha.ComputeHash($bytes)))
        }
    } catch {
        # unreadable as a zip for any reason: fall back to the plain file hash
        if ($zip) { $zip.Dispose(); $zip = $null }
        return (Get-FileHash $p -Algorithm SHA256).Hash
    } finally { if ($zip) { $zip.Dispose() } }
    return [BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($sb.ToString()))).Replace('-','')
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

if (-not $OnCommit) {
    Write-Host ""
    Write-Host "  Repository : $repo"
    Write-Host "  Dropbox    : $target"
    if (-not $Apply) { Write-Host "  MODE       : preview only - nothing will be changed" }
    Write-Host ""
}

if (-not (Test-Path $target)) {
    # After a commit this must never look like a failure: Dropbox may simply not be mounted.
    if ($OnCommit) { exit 0 }
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
    $isVersioned = [bool]$item.Stem

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
                $newstate[$srcFile.Name] = Get-ContentHash $srcFile.FullName
            } else {
                Write-Host "  PULL       $($dstFile.Name)   (newer version than the repository)"
                if ($Apply) { Copy-Item $dstFile.FullName (Join-Path $item.From $dstFile.Name) -Force }
                $pulled++
                $newstate[$dstFile.Name] = Get-ContentHash $dstFile.FullName
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
    $hs = Get-ContentHash $src
    $hd = Get-ContentHash $dst
    $last = $state[$name]

    if ($hd -eq $null) {
        Write-Host "  PUSH       $name   (not in Dropbox yet)"
        if ($Apply) { Copy-Item $src $dst -Force }
        $pushed++; $newstate[$name] = $hs
    }
    elseif ($hs -eq $hd) {
        if (-not $OnCommit) { Write-Host "  in step    $name" }
        $same++; $newstate[$name] = $hs
    }
    elseif ($OnCommit -and $isVersioned) {
        # Same version on both sides but the contents differ. The version number is the signal
        # this hook acts on, so it leaves this alone; 'Sync with Dropbox.cmd' handles it, and it
        # can tell which side was edited.
        $newstate[$name] = $last
    }
    elseif ($last -eq $null) {
        # never synced by this tool, so there is no record of who changed: fall back to time
        $sNewer = (Get-Item $src).LastWriteTime -gt (Get-Item $dst).LastWriteTime
        if ($sNewer) {
            if (-not $OnCommit) { Write-Host "  PUSH       $name   (differs; repository copy is newer - first sync, judged by time)" }
            if ($Apply) { Copy-Item $src $dst -Force }
            $pushed++; $newstate[$name] = $hs
        } else {
            if (-not $OnCommit) { Write-Host "  PULL       $name   (differs; Dropbox copy is newer - first sync, judged by time)" }
            if ($Apply) { Copy-Item $dst $src -Force }
            $pulled++; $newstate[$name] = $hd
        }
    }
    elseif ($hs -eq $last) {
        if (-not $OnCommit) { Write-Host "  PULL       $name   (edited in Dropbox)" }
        if ($Apply) { Copy-Item $dst $src -Force }
        $pulled++; $newstate[$name] = $hd
    }
    elseif ($hd -eq $last) {
        if (-not $OnCommit) { Write-Host "  PUSH       $name   (edited in the repository)" }
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
