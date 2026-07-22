@echo off
setlocal
rem Copy the current User Guide, Tech Manual and the two tester scripts into the shared
rem Dropbox folder, so Moses and the other testers get them without downloading the whole
rem repository. Superseded versions move to that folder's Archive; nothing is deleted.
rem
rem Run with no arguments to publish. Run "Publish to Dropbox.cmd /preview" to see what it
rem would do without changing anything.

title Publish Sangala documents to Dropbox

if /i "%~1"=="/preview" (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\publish-docs.ps1"
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\publish-docs.ps1" -Apply
)

echo.
pause
endlocal
