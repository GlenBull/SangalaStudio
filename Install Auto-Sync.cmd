@echo off
setlocal
rem Make the Dropbox sync happen by itself, so nobody has to remember to run it.
rem
rem Registers a scheduled task that runs at sign-in and every 15 minutes, hidden. It syncs the
rem User Guide, the Tech Manual and the two tester scripts between this project folder and the
rem shared Dropbox folder, in whichever direction was edited. If BOTH sides changed it touches
rem nothing and writes "SYNC CONFLICT.txt" here so you can see it.
rem
rem   Install Auto-Sync.cmd           turn it on
rem   Install Auto-Sync.cmd /remove   turn it off again

title Sangala auto-sync

if /i "%~1"=="/remove" (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\install-sync-task.ps1" -Remove
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\install-sync-task.ps1"
)

echo.
pause
endlocal
