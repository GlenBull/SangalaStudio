@echo off
REM ==========================================================================
REM  Update SangalaStudio.html to the latest version from GitHub.
REM  Double-click this file. No admin, no install, no git needed - it just
REM  downloads the current page and drops it in beside itself.
REM
REM  This updates the APP PAGE only (button behaviour, tools, fixes). That is
REM  almost every update. If a rare change to the machine engine ships, you
REM  would rebuild with "Build SangalaStudio.cmd" instead - but for normal
REM  updates, this one file is all you need.
REM ==========================================================================
setlocal
cd /d "%~dp0"

set "URL=https://raw.githubusercontent.com/GlenBull/SangalaStudio/main/SangalaStudio.html"
set "TARGET=SangalaStudio.html"
set "TMP=SangalaStudio.html.new"

echo Updating Sangala Studio...
echo.

if exist "%TMP%" del "%TMP%" >nul 2>&1

REM curl is built into Windows 10/11; fall back to PowerShell if it is missing.
where curl >nul 2>&1
if %errorlevel%==0 (
  curl -L -f -s -o "%TMP%" "%URL%"
) else (
  powershell -NoProfile -Command "try { Invoke-WebRequest -Uri '%URL%' -OutFile '%TMP%' -UseBasicParsing } catch { exit 1 }"
)

if not exist "%TMP%" goto :failed

REM A good copy ends with the closing </html> tag; a truncated download will not.
find "</html>" "%TMP%" >nul 2>&1
if errorlevel 1 goto :badfile

REM Compare version markers so a re-run with nothing new doesn't touch anything.
set "REMOTEVER="
set "LOCALVER="
for /f "delims=" %%V in ('findstr /c:"SANGALA_VERSION" "%TMP%"') do if not defined REMOTEVER set "REMOTEVER=%%V"
if exist "%TARGET%" for /f "delims=" %%V in ('findstr /c:"SANGALA_VERSION" "%TARGET%"') do if not defined LOCALVER set "LOCALVER=%%V"

if defined LOCALVER if "%LOCALVER%"=="%REMOTEVER%" (
  del "%TMP%" >nul 2>&1
  echo Already up to date - nothing downloaded.
  echo.
  pause
  exit /b 0
)

REM Keep the working copy as a backup, then swap in the new page.
if exist "%TARGET%" copy /y "%TARGET%" "%TARGET%.bak" >nul
move /y "%TMP%" "%TARGET%" >nul

echo Done - Sangala Studio is up to date.
echo.
echo   Now REFRESH the Sangala Studio page in your browser ^(press F5^),
echo   or close and reopen SangalaStudio.exe.
echo.
echo   ^(Your previous version was saved as %TARGET%.bak, just in case.^)
echo.
pause
exit /b 0

:badfile
del "%TMP%" >nul 2>&1
:failed
echo.
echo Update FAILED - could not download a complete copy.
echo Your current Sangala Studio was NOT changed, so it still works.
echo Check the internet connection and run this again.
echo.
pause
exit /b 1
