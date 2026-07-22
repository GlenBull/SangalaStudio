# Register (or remove) a Windows scheduled task that keeps the documents and the shared
# Dropbox folder in step without anyone remembering to run anything.
#
# It runs as the signed-in user, not as SYSTEM, because the Dropbox folder only exists inside
# the user's session. No administrator rights are needed for that.
#
# Cadence: at sign-in, then every 15 minutes. The sync itself is cheap when nothing has
# changed - it hashes four files and stops - so a short interval costs nothing.
param([switch]$Remove)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$name = 'Sangala - sync documents with Dropbox'
$ps1  = Join-Path $PSScriptRoot 'publish-docs.ps1'

if ($Remove) {
    if (Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $name -Confirm:$false
        Write-Host ""
        Write-Host "  Removed the scheduled task. Syncing is manual again:"
        Write-Host "  run 'Sync with Dropbox.cmd' when you want it."
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "  There was no scheduled task to remove."
        Write-Host ""
    }
    return
}

if (-not (Test-Path $ps1)) { Write-Host "  Cannot find $ps1"; exit 1 }

$action = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument ('-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}" -Apply' -f $ps1) `
    -WorkingDirectory $repo

# at sign-in, and every 15 minutes after that for as long as the session lasts
$atLogon = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$repeat  = New-ScheduledTaskTrigger -Once -At (Get-Date).Date.AddMinutes(1) `
             -RepetitionInterval (New-TimeSpan -Minutes 15)

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
    -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

if (Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $name -Confirm:$false
}
Register-ScheduledTask -TaskName $name -Action $action -Trigger @($atLogon, $repeat) `
    -Settings $settings -Principal $principal `
    -Description 'Keeps the Sangala User Guide, Tech Manual and tester scripts in step between the repository and the shared Dropbox folder. Two-way: it moves whichever side changed, and stops if both changed.' | Out-Null

Write-Host ""
Write-Host "  Installed: '$name'"
Write-Host "  Runs at sign-in, then every 15 minutes, hidden."
Write-Host ""
Write-Host "  Record of each run : tools\sync-log.txt"
Write-Host "  If both sides were edited, it changes nothing and writes 'SYNC CONFLICT.txt'"
Write-Host "  into the project folder so you can see it."
Write-Host ""
Write-Host "  To stop it later:  Install Auto-Sync.cmd /remove"
Write-Host ""
