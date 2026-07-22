# Publish the current documents and the beta-tester scripts to the shared Dropbox folder, so
# Moses and the other testers can pick up a new User Guide without downloading the whole
# repository as a zip.
#
# Dropbox here is a business-licensed team account. AI Sandbox sits at the TOP level of it,
# deliberately, because that is what makes access easy to control:
#   %USERPROFILE%\UVa Lab School Dropbox\AI Sandbox\...     (top level - this folder)
#   %USERPROFILE%\UVa Lab School Dropbox\Glen Bull\...      (Glen's own folder in the account)
#
# Rules this follows:
#   - Only the files named below are touched. Anything else in the folder is left alone.
#   - Documents are versioned in the filename, and the folder shows ONE current version of
#     each. When a newer version is published, the superseded one MOVES to Archive - the same
#     convention the repository's own Documents folder uses. Nothing is ever deleted.
#   - A file that is already identical is skipped, so running this twice does nothing.
param([switch]$Apply)

$ErrorActionPreference = 'Stop'
$repo   = Split-Path -Parent $PSScriptRoot
$docs   = Join-Path $repo 'Documents'
$target = Join-Path $env:USERPROFILE 'UVa Lab School Dropbox\AI Sandbox\Design through Making\Sangala Studio Files'

# ---- what the testers get. Add a line here to publish something else. ----------------------
$publish = @(
    @{ Stem = 'User Guide';  From = $docs }      # newest "User Guide (Ver N.N).docx"
    @{ Stem = 'Tech Manual'; From = $docs }
    @{ Name = 'Update SangalaStudio.cmd';    From = $repo }
    @{ Name = 'Create Desktop Shortcut.cmd'; From = $repo }
)

function Get-Ver([string]$name) {
    if ($name -match '\(Ver\s+([0-9]+)\.([0-9]+)\)') {
        return [double]("{0}.{1}" -f $matches[1], $matches[2].PadRight(3,'0'))
    }
    return 0.0
}

function Same-File($a, $b) {
    if (-not (Test-Path $b)) { return $false }
    if ((Get-Item $a).Length -ne (Get-Item $b).Length) { return $false }
    return (Get-FileHash $a -Algorithm SHA256).Hash -eq (Get-FileHash $b -Algorithm SHA256).Hash
}

Write-Host ""
Write-Host "  Source : $repo"
Write-Host "  Target : $target"
if (-not $Apply) { Write-Host "  MODE   : preview only - nothing will be changed (run with -Apply to publish)" }
Write-Host ""

if (-not (Test-Path $target)) {
    Write-Host "  The shared folder was not found."
    Write-Host "  Expected: $target"
    Write-Host "  Check that the AI Sandbox team folder is synced to this PC."
    exit 1
}
$archive = Join-Path $target 'Archive'

$copied = 0; $archived = 0; $skipped = 0
foreach ($item in $publish) {

    # ---- pick the file to publish ----------------------------------------------------------
    if ($item.Stem) {
        $found = Get-ChildItem -Path $item.From -Filter "$($item.Stem) (Ver *).docx" -File |
                 Sort-Object { Get-Ver $_.Name } -Descending
        if (-not $found) { Write-Host "  MISSING   $($item.Stem) (Ver *).docx  - not in Documents"; continue }
        if ($found.Count -gt 1) {
            Write-Host "  NOTE      several versions of '$($item.Stem)' in Documents; publishing $($found[0].Name)"
        }
        $src = $found[0]
    } else {
        $p = Join-Path $item.From $item.Name
        if (-not (Test-Path $p)) { Write-Host "  MISSING   $($item.Name)"; continue }
        $src = Get-Item $p
    }
    $dest = Join-Path $target $src.Name

    # ---- retire any older version of the same document, so one current copy is visible -----
    if ($item.Stem) {
        Get-ChildItem -Path $target -Filter "$($item.Stem) (Ver *).docx" -File |
          Where-Object { $_.Name -ne $src.Name } | ForEach-Object {
            Write-Host "  ARCHIVE   $($_.Name)  ->  Archive\"
            if ($Apply) {
                if (-not (Test-Path $archive)) { New-Item -ItemType Directory $archive | Out-Null }
                $to = Join-Path $archive $_.Name
                if (Test-Path $to) { Remove-Item $to -Force }   # same version already archived
                Move-Item $_.FullName $to -Force
            }
            $archived++
        }
    }

    # ---- copy if it differs ----------------------------------------------------------------
    if (Same-File $src.FullName $dest) {
        Write-Host "  current   $($src.Name)"
        $skipped++
    } else {
        $verb = if (Test-Path $dest) { "UPDATE " } else { "NEW    " }
        Write-Host "  $verb   $($src.Name)"
        if ($Apply) { Copy-Item $src.FullName $dest -Force }
        $copied++
    }
}

Write-Host ""
if ($Apply) {
    Write-Host "  Published $copied file(s), archived $archived, $skipped already current."
    Write-Host "  Dropbox will sync them out; testers see the new file in the shared folder."
} else {
    Write-Host "  Would publish $copied file(s) and archive $archived. $skipped already current."
    Write-Host "  Run 'Publish to Dropbox.cmd' to do it."
}
Write-Host ""
