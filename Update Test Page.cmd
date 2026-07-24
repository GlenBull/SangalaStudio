@echo off
REM ==========================================================================
REM  Update Sangala Studio's PAGE from the test branch (claude/repo-review-det4qo).
REM  Double-click this to pull the latest SangalaStudio.html without downloading
REM  a whole ZIP. No admin, no install, no git.
REM
REM  This grabs ONLY the page (the HTML), which is where all the current test
REM  changes live. It does NOT touch SangalaStudio.exe (the engine) - the engine
REM  has not changed on this branch. If that ever changes you'll be told to grab
REM  a fresh copy.
REM
REM  This file points at a TEST branch and is not for everyday use - the normal
REM  "Update SangalaStudio.cmd" (which tracks the released version) is the one to
REM  keep once testing is done.
REM ==========================================================================
setlocal
cd /d "%~dp0"

set "URL=https://raw.githubusercontent.com/watts-j/SangalaStudio/claude/repo-review-det4qo/SangalaStudio.html"
set "TMP=SangalaStudio.html.new"

echo Fetching the latest test page...
echo.
if exist "%TMP%" del "%TMP%" >nul 2>&1

REM curl is built into Windows 10/11; PowerShell is the fallback.
curl.exe -fL -o "%TMP%" "%URL%" 2>nul
if not exist "%TMP%" powershell -NoProfile -Command "try{ Invoke-WebRequest -UseBasicParsing '%URL%' -OutFile '%TMP%' }catch{ exit 1 }"
if not exist "%TMP%" goto :failed

REM A good page ends with the closing </html> tag; a truncated download will not.
find "</html>" "%TMP%" >nul 2>&1
if errorlevel 1 goto :badfile

move /y "%TMP%" "SangalaStudio.html" >nul
echo Updated the page. Refresh your browser (or restart SangalaStudio.exe) to see it.
echo.
pause
exit /b 0

:badfile
del "%TMP%" >nul 2>&1
echo The download looked incomplete - nothing was changed. Try again in a moment.
echo.
pause
exit /b 1

:failed
echo Could not download. Check your internet connection, then try again.
echo (If this repo is private, the plain download will not work - use a fresh ZIP.)
echo.
pause
exit /b 1
