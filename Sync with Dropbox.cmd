@echo off
setlocal
rem Keep the repository's documents and the shared Dropbox folder in step, in either direction.
rem Moses and the other testers read the User Guide, the Tech Manual and the two tester scripts
rem out of that folder, so they never need to download the whole repository.
rem
rem It records what each file looked like at the last sync, so it knows which side you edited
rem and moves the file that way. If BOTH sides changed it stops and tells you, rather than
rem guessing and losing an edit. Superseded versions move to that folder's Archive.
rem
rem   Sync with Dropbox.cmd            do it
rem   Sync with Dropbox.cmd /preview   show what it would do, change nothing

title Sync Sangala documents with Dropbox

if /i "%~1"=="/preview" (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\publish-docs.ps1"
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\publish-docs.ps1" -Apply
)

echo.
pause
endlocal
